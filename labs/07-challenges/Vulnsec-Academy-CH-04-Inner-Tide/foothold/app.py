#!/usr/bin/env python3
from __future__ import annotations
import os
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

APP_ROOT = Path(__file__).resolve().parent
BASE_PATH = os.environ.get("BASE_PATH", "").rstrip("/")

def render(name):
    return (APP_ROOT/"templates"/name).read_text(encoding="utf-8").replace("{{base}}", BASE_PATH).encode()

class H(BaseHTTPRequestHandler):
    server_version = "Edge151/1.0"
    def log_message(self, m, *a): print(f"{self.address_string()} - {m % a}", flush=True)
    def route(self):
        p = self.path.split("?",1)[0]
        if p!="/" and p.endswith("/"): p=p[:-1]
        if BASE_PATH and (p==BASE_PATH or p.startswith(BASE_PATH+"/")): p=p[len(BASE_PATH):] or "/"
        return p
    def send_html(self, b, s=HTTPStatus.OK):
        self.send_response(s); self.send_header("Content-Type","text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)
    def send_bytes(self, b, t):
        self.send_response(200); self.send_header("Content-Type", t)
        self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)
    def do_GET(self):
        p=self.route()
        if p=="/healthz": return self.send_bytes(b'{"status":"ok"}',"application/json")
        if p=="/static/site.css": return self.send_bytes((APP_ROOT/"static"/"site.css").read_bytes(),"text/css; charset=utf-8")
        if p in {"/","/contractors"}: return self.send_html(render("home.html" if p=="/" else "contractors.html"))
        self.send_html(b"<h1>Not found</h1>", HTTPStatus.NOT_FOUND)

if __name__=="__main__":
    ThreadingHTTPServer(("0.0.0.0", int(os.environ.get("PORT","80"))), H).serve_forever()
