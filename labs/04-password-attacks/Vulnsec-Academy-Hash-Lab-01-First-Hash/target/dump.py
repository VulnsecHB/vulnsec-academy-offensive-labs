#!/usr/bin/env python3
"""Northline personnel archive — leaked MD5 dump (no live cracker)."""

from __future__ import annotations

import os
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs


APP_ROOT = Path(__file__).resolve().parent
BASE_PATH = os.environ.get("BASE_PATH", "").rstrip("/")
OPERATOR = ("a.holt", "letmein")
FLAG = "HASH{first_hash_gate}"


def render(name: str, **values: str) -> bytes:
    text = (APP_ROOT / "templates" / name).read_text(encoding="utf-8")
    for key, value in values.items():
        text = text.replace("{{" + key + "}}", value)
    return text.encode("utf-8")


def page(name: str, title: str, active: str, **extra: str) -> bytes:
    nav = "".join(
        f'<a class="{"on" if key == active else ""}" href="{BASE_PATH}{href}">{label}</a>'
        for href, key, label in (
            ("/", "home", "Home"),
            ("/archive", "archive", "Archive"),
            ("/staff", "staff", "Staff desk"),
        )
    )
    body = render(name, base=BASE_PATH, **extra).decode()
    return render("layout.html", title=title, nav=nav, base=BASE_PATH, body=body)


class DumpHandler(BaseHTTPRequestHandler):
    server_version = "NorthlineArchive/1.0"

    def log_message(self, message: str, *args) -> None:
        print(f"{self.address_string()} - {message % args}", flush=True)

    def route(self) -> str:
        path = self.path.split("?", 1)[0]
        if path != "/" and path.endswith("/"):
            path = path[:-1]
        if BASE_PATH and (path == BASE_PATH or path.startswith(BASE_PATH + "/")):
            path = path[len(BASE_PATH) :] or "/"
        return path

    def send_html(self, payload: bytes, status: HTTPStatus = HTTPStatus.OK) -> None:
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(payload)

    def send_bytes(self, payload: bytes, content_type: str, status: HTTPStatus = HTTPStatus.OK) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self) -> None:  # noqa: N802
        path = self.route()
        if path == "/healthz":
            self.send_bytes(b'{"status":"ok"}', "application/json")
            return
        if path == "/static/dump.css":
            self.send_bytes((APP_ROOT / "static" / "dump.css").read_bytes(), "text/css; charset=utf-8")
            return
        if path == "/":
            self.send_html(page("home.html", "Personnel archive — Northline", "home"))
            return
        if path == "/archive":
            self.send_html(page("archive.html", "Archive — Northline", "archive"))
            return
        if path == "/backup/roster.dump":
            data = (APP_ROOT / "files" / "roster.dump").read_bytes()
            self.send_bytes(data, "text/plain; charset=utf-8")
            return
        if path == "/staff":
            self.send_html(
                page("staff.html", "Staff desk — Northline", "staff", notice="", desk="")
            )
            return
        self.send_html(b"<h1>Not found</h1>", HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:  # noqa: N802
        if self.route() != "/staff":
            self.send_html(b"<h1>Not found</h1>", HTTPStatus.NOT_FOUND)
            return
        length = int(self.headers.get("Content-Length", "0") or 0)
        raw = self.rfile.read(min(length, 4096)).decode("utf-8", "replace")
        fields = parse_qs(raw, keep_blank_values=True)
        user = fields.get("username", [""])[0].strip()
        password = fields.get("password", [""])[0]
        if (user, password) == OPERATOR:
            desk = (
                f'<section class="desk"><p class="kicker">Cleared</p>'
                f"<h2>Operator desk</h2><p>Welcome, {user}.</p>"
                f'<p class="flag">{FLAG}</p></section>'
            )
            notice = ""
        else:
            desk = ""
            notice = '<p class="bad">Desk rejected those credentials.</p>'
        self.send_html(
            page("staff.html", "Staff desk — Northline", "staff", notice=notice, desk=desk)
        )


def main() -> None:
    port = int(os.environ.get("PORT", "80"))
    server = ThreadingHTTPServer(("0.0.0.0", port), DumpHandler)
    print(f"Personnel archive listening on port {port}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
