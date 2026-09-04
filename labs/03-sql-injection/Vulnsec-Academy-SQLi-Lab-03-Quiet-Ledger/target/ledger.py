#!/usr/bin/env python3
"""Northline Finance — supplier ledger (intentionally boolean-blind lookup)."""

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
FLAG = "SQLI{quiet_ledger_northline_clearance}"
SESSIONS: dict[str, dict] = {}
BASE_PATH = os.environ.get("BASE_PATH", "").rstrip("/")


def connect() -> sqlite3.Connection:
    db = sqlite3.connect("/tmp/northline-finance.db")
    db.row_factory = sqlite3.Row
    return db


def seed() -> None:
    db = connect()
    db.executescript(
        """
        DROP TABLE IF EXISTS invoices;
        DROP TABLE IF EXISTS suppliers;
        DROP TABLE IF EXISTS users;

        CREATE TABLE suppliers (
            id INTEGER PRIMARY KEY,
            code TEXT,
            name TEXT,
            town TEXT
        );
        CREATE TABLE invoices (
            id INTEGER PRIMARY KEY,
            ref TEXT,
            supplier TEXT,
            amount REAL,
            status TEXT
        );
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            password TEXT,
            display_name TEXT,
            role TEXT,
            title TEXT,
            desk_ext TEXT
        );

        INSERT INTO suppliers (id, code, name, town) VALUES
            (1, 'HBR-09', 'Harbour Bearings Ltd', 'Grangemouth'),
            (2, 'TYN-14', 'Tyne Hose & Valve', 'Immingham'),
            (3, 'FOR-03', 'Forth Night Stores', 'Harwich');

        INSERT INTO invoices (id, ref, supplier, amount, status) VALUES
            (1, 'INV-44190', 'HBR-09', 18640.00, 'held'),
            (2, 'INV-33012', 'TYN-14', 4275.50, 'posted'),
            (3, 'INV-77801', 'FOR-03', 910.00, 'posted'),
            (4, 'INV-12004', 'HBR-09', 2400.00, 'held');

        INSERT INTO users (id, username, password, display_name, role, title, desk_ext) VALUES
            (1, 'a.quist', 'Ledger#1904', 'Asha Quist', 'clerk', 'Invoice Clerk', '3302'),
            (2, 'r.nolan', 'BatchNight!7', 'Rory Nolan', 'clerk', 'Night Batch', '3308'),
            (3, 'e.vale', 'Clearance-3301', 'Ellis Vale', 'controller', 'Finance Controller', '3300');
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


def invoice_exists(ref: str) -> bool:
    # INTENTIONAL VULNERABILITY — training lab only.
    # Boolean-blind: callers only learn True/False. Errors look like "not found".
    query = f"SELECT id FROM invoices WHERE ref = '{ref}' LIMIT 1"
    db = connect()
    try:
        row = db.execute(query).fetchone()
    except sqlite3.Error:
        db.close()
        return False
    db.close()
    return row is not None


def safe_login(username: str, password: str) -> dict | None:
    db = connect()
    row = db.execute(
        "SELECT id, username, display_name, role, title, desk_ext FROM users "
        "WHERE username = ? AND password = ? LIMIT 1",
        (username, password),
    ).fetchone()
    db.close()
    return dict(row) if row else None


class LedgerHandler(BaseHTTPRequestHandler):
    server_version = "NorthlineFinance/1.6"

    def log_message(self, message: str, *args) -> None:
        print(f"{self.address_string()} - {message % args}", flush=True)

    def route(self) -> str:
        path = self.path.split("?", 1)[0]
        if BASE_PATH and (path == BASE_PATH or path.startswith(BASE_PATH + "/")):
            path = path[len(BASE_PATH) :] or "/"
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
        if "nl_fin" not in cookie:
            return None
        return SESSIONS.get(cookie["nl_fin"].value)

    def page_shell(self, template: str, **values: str) -> bytes:
        user = self.current_user()
        if user:
            account = (
                f"<a class='who' href='{self.loc('/desk')}'>{html.escape(user['display_name'])}</a>"
                f"<a href='{self.loc('/logout')}'>Sign out</a>"
            )
        else:
            account = f"<a href='{self.loc('/account')}'>Staff desk</a>"
        return render(template, base=BASE_PATH, account=account, **values)

    def do_GET(self) -> None:  # noqa: N802
        path = self.route()
        query = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)

        if path == "/healthz":
            body = b'{"status":"ok"}'
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if path == "/static/ledger.css":
            self.send_file(APP_ROOT / "static" / "ledger.css", "text/css; charset=utf-8")
            return
        if path == "/logout":
            cookie = SimpleCookie(self.headers.get("Cookie", ""))
            if "nl_fin" in cookie:
                SESSIONS.pop(cookie["nl_fin"].value, None)
            self.send_html(
                b"",
                HTTPStatus.FOUND,
                [("Location", self.loc("/")), ("Set-Cookie", "nl_fin=; Max-Age=0; Path=/")],
            )
            return
        if path in {"/", "/lookup"}:
            ref = query.get("ref", [""])[0]
            result = ""
            if "ref" in query:
                if invoice_exists(ref):
                    result = (
                        "<section class='verdict hit' id='verdict'>"
                        "<p class='kicker'>Public lookup</p>"
                        "<h2>Invoice on file</h2>"
                        "<p>That reference exists in the supplier ledger. Amount, supplier and hold status are withheld from this page.</p>"
                        "</section>"
                    )
                else:
                    result = (
                        "<section class='verdict miss' id='verdict'>"
                        "<p class='kicker'>Public lookup</p>"
                        "<h2>No matching invoice</h2>"
                        "<p>Nothing in the current year matches that reference. Check the prefix and try again.</p>"
                        "</section>"
                    )
            self.send_html(
                self.page_shell(
                    "lookup.html",
                    ref=html.escape(ref),
                    result=result,
                )
            )
            return
        if path == "/account":
            notice = ""
            if query.get("notice") == ["denied"]:
                notice = "<p class='banner warn'>That desk cannot open clearance notes.</p>"
            elif query.get("notice") == ["expired"]:
                notice = "<p class='banner warn'>Sign in again to continue.</p>"
            self.send_html(self.page_shell("account.html", notice=notice, error=""))
            return
        if path == "/desk":
            user = self.current_user()
            if user is None:
                self.send_html(b"", HTTPStatus.FOUND, [("Location", self.loc("/account?notice=expired"))])
                return
            if user["role"] == "controller":
                locker = (
                    "<section class='clearance'>"
                    "<p class='kicker'>Clearance note · SOC-only</p>"
                    "<h2>Held invoices — Harbour Bearings</h2>"
                    "<p>Do not circulate this clearance number outside Finance Control.</p>"
                    f"<p class='flag'>{html.escape(FLAG)}</p>"
                    "</section>"
                )
            else:
                locker = (
                    "<section class='panel'>"
                    "<h2>Open batch</h2>"
                    "<p>No clearance notes are assigned to a clerk desk. Ask the finance controller.</p>"
                    "</section>"
                )
            self.send_html(
                self.page_shell(
                    "desk.html",
                    display=html.escape(user["display_name"]),
                    title=html.escape(user["title"]),
                    role=html.escape(user["role"].title()),
                    ext=html.escape(user["desk_ext"]),
                    locker=locker,
                )
            )
            return
        self.send_html(b"<h1>Not found</h1>", HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:  # noqa: N802
        if self.route() != "/account":
            self.send_html(b"<h1>Not found</h1>", HTTPStatus.NOT_FOUND)
            return
        length = int(self.headers.get("Content-Length", "0") or 0)
        form = parse_form(self.rfile.read(max(0, min(length, 8192))))
        user = safe_login(form.get("username", ""), form.get("password", ""))
        if user is None:
            self.send_html(
                self.page_shell(
                    "account.html",
                    notice="",
                    error="<p class='banner bad'>Those finance-desk credentials were not recognised.</p>",
                )
            )
            return
        token = secrets.token_hex(16)
        SESSIONS[token] = user
        self.send_html(
            b"",
            HTTPStatus.FOUND,
            [("Location", self.loc("/desk")), ("Set-Cookie", f"nl_fin={token}; Path=/; HttpOnly")],
        )


def main() -> None:
    seed()
    port = int(os.environ.get("PORT", "80"))
    server = ThreadingHTTPServer(("0.0.0.0", port), LedgerHandler)
    print(f"Northline Finance listening on port {port}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
