#!/usr/bin/env python3
from __future__ import annotations

import os
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

APP_ROOT = Path(__file__).resolve().parent
BASE_PATH = os.environ.get("BASE_PATH", "").rstrip("/")


def render(name: str) -> bytes:
    return (APP_ROOT / "templates" / name).read_text(encoding="utf-8").replace("{{base}}", BASE_PATH).encode()


class Handler(BaseHTTPRequestHandler):
    server_version = "YardStatus/1.0"

    def log_message(self, message: str, *args) -> None:
        print(f"{self.address_string()} - {message % args}", flush=True)

    def route(self) -> str:
        path = self.path.split("?", 1)[0]
        if path != "/" and path.endswith("/"):
            path = path[:-1]
        if BASE_PATH and (path == BASE_PATH or path.startswith(BASE_PATH + "/")):
            path = path[len(BASE_PATH):] or "/"
        return path

    def send_html(self, payload: bytes, status: HTTPStatus = HTTPStatus.OK) -> None:
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def send_bytes(self, payload: bytes, content_type: str) -> None:
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self) -> None:
        path = self.route()
        if path == "/healthz":
            self.send_bytes(b'{"status":"ok"}', "application/json")
            return
        if path == "/static/site.css":
            self.send_bytes((APP_ROOT / "static" / "site.css").read_bytes(), "text/css; charset=utf-8")
            return
        if path == "/":
            self.send_html(render("home.html"))
            return
        if path == "/status":
            self.send_html(render("status.html"))
            return
        self.send_html(b"<h1>Not found</h1>", HTTPStatus.NOT_FOUND)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "80"))
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()
