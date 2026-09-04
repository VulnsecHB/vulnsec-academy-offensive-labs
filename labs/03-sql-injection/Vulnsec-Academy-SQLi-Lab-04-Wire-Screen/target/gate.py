#!/usr/bin/env python3
"""Northline Yard Access — contractor pass lookup (WAF + intentional SQLi)."""

from __future__ import annotations

import html
import os
import re
import secrets
import sqlite3
import urllib.parse
from http import HTTPStatus
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


APP_ROOT = Path(__file__).resolve().parent
FLAG = "SQLI{wire_screen_northline_bypass}"
SESSIONS: dict[str, dict] = {}
BASE_PATH = os.environ.get("BASE_PATH", "").rstrip("/")

# Perimeter screen: spaced keywords and classic tautologies.
# Comment-wrapped tokens (UNION/**/SELECT) are allowed on purpose.
SCREEN_RULES = (
    re.compile(r"\bunion\b\s", re.I),
    re.compile(r"\s\bunion\b", re.I),
    re.compile(r"\bselect\b\s", re.I),
    re.compile(r"\s\bselect\b", re.I),
    re.compile(r"'\s*(and|or)\s+", re.I),
    re.compile(r"\s+(and|or)\s+\d", re.I),
    re.compile(r"\bor\b\s+1\s*=\s*1", re.I),
    re.compile(r"\band\b\s+\d+\s*=\s*\d+", re.I),
)


def connect() -> sqlite3.Connection:
    db = sqlite3.connect("/tmp/northline-yard.db")
    db.row_factory = sqlite3.Row
    return db


def seed() -> None:
    db = connect()
    db.executescript(
        """
        DROP TABLE IF EXISTS passes;
        DROP TABLE IF EXISTS contractors;
        DROP TABLE IF EXISTS users;

        CREATE TABLE contractors (
            id INTEGER PRIMARY KEY,
            code TEXT,
            name TEXT,
            yard TEXT
        );
        CREATE TABLE passes (
            id INTEGER PRIMARY KEY,
            pass_id TEXT,
            holder TEXT,
            company TEXT,
            valid_until TEXT,
            zone TEXT
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

        INSERT INTO contractors (id, code, name, yard) VALUES
            (1, 'HBR-09', 'Harbour Bearings Ltd', 'Yard A'),
            (2, 'TYN-14', 'Tyne Hose & Valve', 'Yard C'),
            (3, 'FOR-03', 'Forth Night Stores', 'Bay 2');

        INSERT INTO passes (id, pass_id, holder, company, valid_until, zone) VALUES
            (1, 'YA-10442', 'P. Hendry', 'Harbour Bearings Ltd', '2026-09-12', 'A-west'),
            (2, 'YA-22018', 'L. Adeyemi', 'Tyne Hose & Valve', '2026-08-30', 'C-rail'),
            (3, 'YA-33107', 'S. Curran', 'Forth Night Stores', '2026-10-02', 'Bay-2');

        INSERT INTO users (id, username, password, display_name, role, title, desk_ext) VALUES
            (1, 'k.briggs', 'GateHouse#12', 'Kai Briggs', 'clerk', 'Gate Clerk', '2204'),
            (2, 's.okoye', 'NightWatch!9', 'Sade Okoye', 'clerk', 'Night Gate', '2208'),
            (3, 't.marsh', 'Bypass-4408', 'Tamsin Marsh', 'marshal', 'Yard Marshal', '2200');
        """
    )
    db.commit()
    db.close()


def screen_blocked(value: str) -> bool:
    decoded = urllib.parse.unquote_plus(value)
    return any(rule.search(decoded) for rule in SCREEN_RULES)


def render(name: str, **values: str) -> bytes:
    text = (APP_ROOT / "templates" / name).read_text(encoding="utf-8")
    for key, value in values.items():
        text = text.replace("{{" + key + "}}", value)
    return text.encode("utf-8")


def parse_form(body: bytes) -> dict[str, str]:
    parsed = urllib.parse.parse_qs(body.decode("utf-8", errors="replace"), keep_blank_values=True)
    return {key: (values[0] if values else "") for key, values in parsed.items()}


def lookup_pass(pass_id: str) -> tuple[list | None, str]:
    # INTENTIONAL VULNERABILITY — training lab only.
    query = (
        "SELECT id, pass_id, holder, company, valid_until, zone FROM passes "
        f"WHERE pass_id = '{pass_id}'"
    )
    db = connect()
    try:
        rows = db.execute(query).fetchall()
    except sqlite3.Error:
        db.close()
        return None, "error"
    db.close()
    return list(rows), "ok"


def safe_login(username: str, password: str) -> dict | None:
    db = connect()
    row = db.execute(
        "SELECT id, username, display_name, role, title, desk_ext FROM users "
        "WHERE username = ? AND password = ? LIMIT 1",
        (username, password),
    ).fetchone()
    db.close()
    return dict(row) if row else None


def pass_cards(rows: list) -> str:
    if not rows:
        return (
            "<section class='verdict miss'>"
            "<p class='kicker'>Pass check</p>"
            "<h2>No pass on file</h2>"
            "<p>That identifier is not on the current yard list.</p>"
            "</section>"
        )
    cards = []
    for row in rows:
        pid = html.escape(str(row["pass_id"] if "pass_id" in row.keys() else row[1]))
        holder = html.escape(str(row["holder"] if "holder" in row.keys() else row[2]))
        company = html.escape(str(row["company"] if "company" in row.keys() else row[3]))
        until = html.escape(str(row["valid_until"] if "valid_until" in row.keys() else row[4]))
        zone = html.escape(str(row["zone"] if "zone" in row.keys() else row[5]))
        cards.append(
            "<article class='pass-card'>"
            f"<span class='sku'>{pid}</span>"
            f"<h3>{holder}</h3>"
            f"<dl><div><dt>Company</dt><dd>{company}</dd></div>"
            f"<div><dt>Valid until</dt><dd>{until}</dd></div>"
            f"<div><dt>Zone</dt><dd>{zone}</dd></div></dl>"
            "</article>"
        )
    return "<div class='pass-grid'>" + "".join(cards) + "</div>"


class GateHandler(BaseHTTPRequestHandler):
    server_version = "NorthlineYard/4.2"

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
        if "nl_yard" not in cookie:
            return None
        return SESSIONS.get(cookie["nl_yard"].value)

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

    def blocked_page(self) -> None:
        body = self.page_shell(
            "blocked.html",
            reason="Spaced SQL keywords and classic tautologies are not permitted through the yard perimeter.",
        )
        self.send_html(body, HTTPStatus.FORBIDDEN)

    def do_GET(self) -> None:  # noqa: N802
        path = self.route()
        parsed = urllib.parse.urlparse(self.path)
        query = urllib.parse.parse_qs(parsed.query)

        if path == "/healthz":
            body = b'{"status":"ok"}'
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if path == "/static/gate.css":
            self.send_file(APP_ROOT / "static" / "gate.css", "text/css; charset=utf-8")
            return
        if path == "/logout":
            cookie = SimpleCookie(self.headers.get("Cookie", ""))
            if "nl_yard" in cookie:
                SESSIONS.pop(cookie["nl_yard"].value, None)
            self.send_html(
                b"",
                HTTPStatus.FOUND,
                [("Location", self.loc("/")), ("Set-Cookie", "nl_yard=; Max-Age=0; Path=/")],
            )
            return
        if path in {"/", "/check"}:
            raw_qs = parsed.query or ""
            pass_id = query.get("pass", [""])[0]
            if "pass" in query or raw_qs:
                if screen_blocked(raw_qs) or screen_blocked(pass_id):
                    self.blocked_page()
                    return
            result = ""
            if "pass" in query:
                rows, status = lookup_pass(pass_id)
                if status == "error":
                    result = (
                        "<section class='verdict miss'>"
                        "<p class='kicker'>Pass check</p>"
                        "<h2>Lookup failed</h2>"
                        "<p>The yard directory could not complete that check. Try a clean pass identifier.</p>"
                        "</section>"
                    )
                else:
                    result = pass_cards(rows or [])
            self.send_html(
                self.page_shell(
                    "check.html",
                    pass_id=html.escape(pass_id),
                    result=result,
                )
            )
            return
        if path == "/account":
            notice = ""
            if query.get("notice") == ["expired"]:
                notice = "<p class='banner warn'>Sign in again to continue.</p>"
            self.send_html(self.page_shell("account.html", notice=notice, error=""))
            return
        if path == "/desk":
            user = self.current_user()
            if user is None:
                self.send_html(b"", HTTPStatus.FOUND, [("Location", self.loc("/account?notice=expired"))])
                return
            if user["role"] == "marshal":
                locker = (
                    "<section class='clearance'>"
                    "<p class='kicker'>Sealed gate log · SOC-only</p>"
                    "<h2>Perimeter exception — Yard A west</h2>"
                    "<p>Do not circulate this exception number outside Yard Control.</p>"
                    f"<p class='flag'>{html.escape(FLAG)}</p>"
                    "</section>"
                )
            else:
                locker = (
                    "<section class='panel'>"
                    "<h2>Open gate list</h2>"
                    "<p>No sealed logs are assigned to a clerk desk. Ask the yard marshal.</p>"
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
                    error="<p class='banner bad'>Those yard-desk credentials were not recognised.</p>",
                )
            )
            return
        token = secrets.token_hex(16)
        SESSIONS[token] = user
        self.send_html(
            b"",
            HTTPStatus.FOUND,
            [("Location", self.loc("/desk")), ("Set-Cookie", f"nl_yard={token}; Path=/; HttpOnly")],
        )


def main() -> None:
    seed()
    port = int(os.environ.get("PORT", "80"))
    server = ThreadingHTTPServer(("0.0.0.0", port), GateHandler)
    print(f"Northline Yard Access listening on port {port}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
