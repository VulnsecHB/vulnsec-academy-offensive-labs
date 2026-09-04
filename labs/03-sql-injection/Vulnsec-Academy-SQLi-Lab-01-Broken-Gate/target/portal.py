#!/usr/bin/env python3
"""Northline Operations — Staff Access portal (intentionally vulnerable login)."""

from __future__ import annotations

import html
import os
import secrets
import sqlite3
import urllib.parse
from http import HTTPStatus
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


APP_ROOT = Path(__file__).resolve().parent
FLAG = "SQLI{broken_gate_northline_admin}"
SESSIONS: dict[str, dict] = {}
BASE_PATH = os.environ.get("BASE_PATH", "").rstrip("/")


def connect() -> sqlite3.Connection:
    db = sqlite3.connect("/tmp/northline.db")
    db.row_factory = sqlite3.Row
    return db


def seed() -> None:
    db = connect()
    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            password TEXT,
            display_name TEXT,
            role TEXT,
            title TEXT
        );
        DELETE FROM users;
        INSERT INTO users (id, username, password, display_name, role, title) VALUES
            (1, 'admin', 'N0rthl1ne-Adm!n', 'A. Reeves', 'admin', 'Access Administrator'),
            (2, 'm.chen', 'WinterRail!19', 'Mei Chen', 'staff', 'Yard Controller'),
            (3, 'j.okonkwo', 'YardShift#4', 'Jordan Okonkwo', 'staff', 'Shift Lead');
        """
    )
    db.commit()
    db.close()


def render(name: str, **values: str) -> bytes:
    text = (APP_ROOT / "templates" / name).read_text(encoding="utf-8")
    for key, value in values.items():
        text = text.replace("{{" + key + "}}", value)
    return text.encode("utf-8")


def parse_form(body: bytes) -> dict[str, str]:
    parsed = urllib.parse.parse_qs(body.decode("utf-8", errors="replace"), keep_blank_values=True)
    return {key: (values[0] if values else "") for key, values in parsed.items()}


def try_login(username: str, password: str) -> tuple[dict | None, str]:
    # INTENTIONAL VULNERABILITY — training lab only.
    query = (
        "SELECT id, username, display_name, role, title FROM users "
        f"WHERE username = '{username}' AND password = '{password}' LIMIT 1"
    )
    db = connect()
    try:
        row = db.execute(query).fetchone()
    except sqlite3.Error:
        db.close()
        return None, "error"
    db.close()
    if row is None:
        return None, "invalid"
    return dict(row), "ok"


class PortalHandler(BaseHTTPRequestHandler):
    server_version = "NorthlineAccess/2.4"

    def log_message(self, message: str, *args) -> None:
        print(f"{self.address_string()} - {message % args}", flush=True)

    def route(self) -> str:
        path = self.path.split("?", 1)[0]
        if BASE_PATH and (path == BASE_PATH or path.startswith(BASE_PATH + "/")):
            path = path[len(BASE_PATH):] or "/"
        return path

    def loc(self, path: str) -> str:
        return f"{BASE_PATH}{path}"

    def send_html(self, payload: bytes, status: HTTPStatus = HTTPStatus.OK, headers: list[tuple[str, str]] | None = None) -> None:
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        if headers:
            for key, value in headers:
                self.send_header(key, value)
        self.end_headers()
        self.wfile.write(payload)

    def send_file(self, path: Path, content_type: str) -> None:
        data = path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def current_user(self) -> dict | None:
        cookie = SimpleCookie(self.headers.get("Cookie", ""))
        if "nl_session" not in cookie:
            return None
        return SESSIONS.get(cookie["nl_session"].value)

    def do_GET(self) -> None:  # noqa: N802
        path = self.route()
        if path == "/healthz":
            body = b'{"status":"ok"}'
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if path == "/static/portal.css":
            self.send_file(APP_ROOT / "static" / "portal.css", "text/css; charset=utf-8")
            return
        if path in {"/", "/login"}:
            notice = ""
            query = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            if query.get("notice") == ["expired"]:
                notice = '<p class="banner warn">Your session ended. Sign in again.</p>'
            elif query.get("notice") == ["denied"]:
                notice = '<p class="banner warn">That account cannot open the incident locker.</p>'
            self.send_html(render("login.html", notice=notice, error="", base=BASE_PATH))
            return
        if path == "/logout":
            cookie = SimpleCookie(self.headers.get("Cookie", ""))
            if "nl_session" in cookie:
                SESSIONS.pop(cookie["nl_session"].value, None)
            self.send_html(
                b"",
                HTTPStatus.FOUND,
                [("Location", self.loc("/login?notice=expired")), ("Set-Cookie", "nl_session=; Max-Age=0; Path=/")],
            )
            return
        if path == "/dashboard":
            user = self.current_user()
            if user is None:
                self.send_html(b"", HTTPStatus.FOUND, [("Location", self.loc("/login?notice=expired"))])
                return
            if user["role"] == "admin":
                locker = (
                    '<section class="locker">'
                    "<h2>Sealed incident note</h2>"
                    "<p>Access Control review — do not circulate outside SOC.</p>"
                    f'<p class="flag">{html.escape(FLAG)}</p>'
                    "</section>"
                )
            else:
                locker = (
                    '<section class="panel">'
                    "<h2>Shift board</h2>"
                    "<p>No incidents assigned to your yard this window. Contact Access Control if you need the sealed locker.</p>"
                    "</section>"
                )
            self.send_html(
                render(
                    "dashboard.html",
                    display=html.escape(user["display_name"]),
                    title=html.escape(user["title"]),
                    role=html.escape(user["role"].replace("_", " ").title()),
                    locker=locker,
                    base=BASE_PATH,
                )
            )
            return
        self.send_html(b"<h1>Not found</h1>", HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:  # noqa: N802
        if self.route() != "/login":
            self.send_html(b"<h1>Not found</h1>", HTTPStatus.NOT_FOUND)
            return
        length = int(self.headers.get("Content-Length", "0") or 0)
        form = parse_form(self.rfile.read(max(0, min(length, 8192))))
        username = form.get("username", "")
        password = form.get("password", "")
        user, status = try_login(username, password)
        if status == "error":
            self.send_html(
                render(
                    "login.html",
                    notice="",
                    error='<p class="banner bad">Sign-in service encountered an unexpected error. Try again.</p>',
                    base=BASE_PATH,
                )
            )
            return
        if user is None:
            self.send_html(
                render(
                    "login.html",
                    notice="",
                    error='<p class="banner bad">Those credentials were not recognised.</p>',
                    base=BASE_PATH,
                )
            )
            return
        token = secrets.token_hex(16)
        SESSIONS[token] = user
        self.send_html(
            b"",
            HTTPStatus.FOUND,
            [("Location", self.loc("/dashboard")), ("Set-Cookie", f"nl_session={token}; Path=/; HttpOnly")],
        )


def main() -> None:
    seed()
    port = int(os.environ.get("PORT", "80"))
    server = ThreadingHTTPServer(("0.0.0.0", port), PortalHandler)
    print(f"Northline Staff Access listening on port {port}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
