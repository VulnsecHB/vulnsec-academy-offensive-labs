#!/usr/bin/env python3
from __future__ import annotations
import os
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

APP = Path(__file__).resolve().parent
BASE = os.environ.get("BASE_PATH", "").rstrip("/")
FLAG = "PIV{second_hold}"
EXTRA_PORT = 0

def render(name, **kw):
    text = (APP / "templates" / name).read_text(encoding="utf-8")
    for k, v in kw.items():
        text = text.replace("{{" + k + "}}", v)
    return text.encode()

class H(BaseHTTPRequestHandler):
    server_version = "NorthlineInner/1.0"
    def log_message(self, m, *a):
        print(f"{self.address_string()} - {m % a}", flush=True)
    def route(self):
        p = self.path.split("?",1)[0]
        if p != "/" and p.endswith("/"):
            p = p[:-1]
        if BASE and (p == BASE or p.startswith(BASE+"/")):
            p = p[len(BASE):] or "/"
        return p
    def send_html(self, b, st=HTTPStatus.OK):
        self.send_response(st)
        self.send_header("Content-Type","text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(b)))
        self.send_header("Cache-Control","no-store")
        self.end_headers()
        self.wfile.write(b)
    def send_bytes(self, b, ct, st=HTTPStatus.OK):
        self.send_response(st)
        self.send_header("Content-Type", ct)
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)
    def do_GET(self):
        p = self.route()
        if p == "/healthz":
            return self.send_bytes(b'{"status":"ok"}', "application/json")
        if p == "/static/inner.css":
            return self.send_bytes((APP/"static"/"inner.css").read_bytes(), "text/css; charset=utf-8")
        port = self.server.server_address[1]
        if port == EXTRA_PORT:
            return self.send_html(render("flag.html", flag=FLAG, base=BASE))
        if p == "/":
            return self.send_html(render("home.html", flag=FLAG, base=BASE))
        self.send_html(b"<h1>Not found</h1>", HTTPStatus.NOT_FOUND)

def main():
    port = int(os.environ.get("PORT", "80"))
    if EXTRA_PORT:
        import threading
        t = ThreadingHTTPServer(("0.0.0.0", EXTRA_PORT), H)
        threading.Thread(target=t.serve_forever, daemon=True).start()
    s = ThreadingHTTPServer(("0.0.0.0", port), H)
    print(f"inner on {port} extra={EXTRA_PORT}", flush=True)
    s.serve_forever()
if __name__ == "__main__":
    main()
