#!/usr/bin/env python3
"""Salt Gate — public shop (safe) + staff vhost (SQLi)."""
from __future__ import annotations

import os
import sqlite3
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

APP_ROOT = Path(__file__).resolve().parent
BASE_PATH = os.environ.get("BASE_PATH", "").rstrip("/")
DB = Path("/tmp/salt.db")
STAFF_HOSTS = {"staff.saltgate.internal", "staff", "staff.saltgate"}


def init_db() -> None:
    con = sqlite3.connect(DB)
    con.execute("CREATE TABLE IF NOT EXISTS products (id INTEGER, name TEXT, price TEXT)")
    con.execute("DELETE FROM products")
    con.executemany("INSERT INTO products VALUES (?,?,?)", [
        (1, "flake salt", "4.20"),
        (2, "brine cask", "18.00"),
        (3, "keeper's grind", "9.50"),
    ])
    con.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER, username TEXT, role TEXT, password_hash TEXT, note TEXT)")
    con.execute("DELETE FROM users")
    con.executemany("INSERT INTO users VALUES (?,?,?,?,?)", [
        (1, "a.salt", "shop", "$6$YOKufkVCNqguyhBq$yekeHrRO4kTd7Z23zHZ3Liih4hMFpaTADhAusX44jzpW2/kARGEyP58FQGBUuatshzQ0CTiz2Z7gppQSoi.0n.", "never rotated"),
        (2, "n.briggs", "ops", "$6$r2AvF1YdV6CR.GLG$TCr2FBSAFyp9s3ZSYA.tEa4qnxh7pVLGCBroLs6UEKrxRnJASuPhRUyZAEiurQNWbEZq3BCo6wOo947Sf0kLB0", "ssh on this host"),
        (3, "k.winter", "audit", "$6$aqMmXYShW6Zb1oPX$2.nKjuE1CYKDnQ5RBpRSjpP/aS4Jea9hZzBx5yKVXSMyfN8Qc/dRJSsJ4trHkZiU4C7jN4E1YAXJQxQ5.6gQF.", "policy: 9+ mixed"),
    ])
    con.commit()
    con.close()


def html(name: str) -> str:
    return (APP_ROOT / "templates" / name).read_text(encoding="utf-8").replace("{{base}}", BASE_PATH)


class Handler(BaseHTTPRequestHandler):
    server_version = "SaltGate/1.0"

    def log_message(self, m, *a):
        print(f"{self.address_string()} - {m % a}", flush=True)

    def host(self) -> str:
        return (self.headers.get("Host") or "").split(":")[0].lower()

    def is_staff(self) -> bool:
        path = self.route()
        return self.host() in STAFF_HOSTS or path.startswith("/internal")

    def route(self) -> str:
        path = self.path.split("?", 1)[0]
        if path != "/" and path.endswith("/"):
            path = path[:-1]
        if BASE_PATH and (path == BASE_PATH or path.startswith(BASE_PATH + "/")):
            path = path[len(BASE_PATH):] or "/"
        if path.startswith("/internal"):
            path = path[len("/internal"):] or "/"
        return path

    def send_html(self, payload: str, status=HTTPStatus.OK):
        data = payload.encode()
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def send_bytes(self, payload: bytes, ctype: str):
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        path = self.route()
        if path == "/healthz":
            return self.send_bytes(b'{"status":"ok"}', "application/json")
        if path == "/static/site.css":
            name = "staff.css" if self.is_staff() else "site.css"
            return self.send_bytes((APP_ROOT / "static" / name).read_bytes(), "text/css; charset=utf-8")
        if path == "/robots.txt":
            return self.send_bytes(b"User-agent: *\nDisallow: /backup\nDisallow: /shop-old\n", "text/plain")
        if self.is_staff():
            return self.staff(path)
        return self.public(path)

    def public(self, path: str) -> None:
        if path == "/":
            return self.send_html(html("home.html"))
        if path == "/search":
            q = parse_qs(urlparse(self.path).query).get("q", [""])[0]
            con = sqlite3.connect(DB)
            rows = con.execute("SELECT name, price FROM products WHERE name LIKE ?", (f"%{q}%",)).fetchall()
            con.close()
            items = "".join(f"<li>{n} — {p}</li>" for n, p in rows) or "<li>no matches</li>"
            page = html("search.html").replace("{{q}}", q.replace("<", "")).replace("{{items}}", items)
            return self.send_html(page)
        self.send_html("<h1>Not found</h1>", HTTPStatus.NOT_FOUND)

    def staff(self, path: str) -> None:
        if path in {"/", "/search"}:
            q = parse_qs(urlparse(self.path).query).get("q", [""])[0]
            rows_html = ""
            error = ""
            if q:
                con = sqlite3.connect(DB)
                try:
                    rows = con.execute(f"SELECT username, role, note FROM users WHERE username LIKE '%{q}%'").fetchall()
                    rows_html = "".join(f"<tr><td>{a}</td><td>{b}</td><td>{c}</td></tr>" for a, b, c in rows)
                except sqlite3.Error as exc:
                    error = str(exc)
                con.close()
            page = html("staff.html").replace("{{q}}", q.replace("<", "")).replace("{{rows}}", rows_html).replace("{{error}}", error)
            return self.send_html(page)
        self.send_html("<h1>staff 404</h1>", HTTPStatus.NOT_FOUND)


if __name__ == "__main__":
    init_db()
    ThreadingHTTPServer(("0.0.0.0", int(os.environ.get("PORT", "80"))), Handler).serve_forever()
