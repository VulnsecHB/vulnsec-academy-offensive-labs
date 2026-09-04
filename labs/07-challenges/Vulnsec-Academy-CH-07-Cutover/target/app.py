#!/usr/bin/env python3
from __future__ import annotations
import os
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

APP_ROOT = Path(__file__).resolve().parent
BASE_PATH = os.environ.get("BASE_PATH", "").rstrip("/")
OPS = APP_ROOT / "ops"

def html(name: str) -> bytes:
    return (APP_ROOT / "templates" / name).read_text(encoding="utf-8").replace("{{base}}", BASE_PATH).encode()

class H(BaseHTTPRequestHandler):
    server_version = "CutoverMag/1.0"
    def log_message(self, m, *a): print(f"{self.address_string()} - {m % a}", flush=True)
    def route(self):
        p = self.path.split("?", 1)[0]
        if p != "/" and p.endswith("/"): p = p[:-1]
        if BASE_PATH and (p == BASE_PATH or p.startswith(BASE_PATH + "/")):
            p = p[len(BASE_PATH):] or "/"
        return p
    def send_html(self, b, s=HTTPStatus.OK):
        self.send_response(s); self.send_header("Content-Type","text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)
    def send_bytes(self, b, t, extra=None):
        self.send_response(200); self.send_header("Content-Type", t)
        self.send_header("Content-Length", str(len(b)))
        if extra:
            for k,v in extra: self.send_header(k,v)
        self.end_headers(); self.wfile.write(b)
    def do_GET(self):
        p = self.route()
        if p == "/healthz": return self.send_bytes(b'{"status":"ok"}', "application/json")
        if p == "/static/site.css": return self.send_bytes((APP_ROOT/"static"/"site.css").read_bytes(), "text/css; charset=utf-8")
        if p == "/robots.txt":
            return self.send_bytes(b"User-agent: *\nDisallow: /intranet-2019/\nDisallow: /staff-old/\nDisallow: /backup/\n", "text/plain")
        if p in {"/intranet-2019", "/staff-old", "/backup"}:
            return self.send_html(b"<h1>gone</h1><p>decoy</p>")
        if p == "/intranet":
            q = parse_qs(urlparse(self.path).query).get("q", [""])[0]
            # parameterized dead end
            return self.send_html(f"<h1>intranet</h1><p>bound lookup for {q or 'nothing'} — 0 rows.</p>".encode())
        if p == "/ops":
            listing = "<ul>" + "".join(f"<li><a href='{BASE_PATH}/ops/{n}'>{n}</a></li>" for n in sorted(os.listdir(OPS))) + "</ul>"
            return self.send_html(f"<!doctype html><meta charset=utf-8><link rel=stylesheet href='{BASE_PATH}/static/site.css'><body><main><h1>ops</h1>{listing}</main>".encode())
        if p.startswith("/ops/"):
            name = p.split("/")[-1]
            fp = OPS / name
            if fp.is_file() and fp.resolve().parent == OPS.resolve():
                ctype = "application/octet-stream" if name == "id_rsa" else "text/plain"
                extra = [("Content-Disposition", f"attachment; filename={name}")] if name == "id_rsa" else None
                return self.send_bytes(fp.read_bytes(), ctype, extra)
        if p == "/": return self.send_html(html("home.html"))
        if p == "/essay": return self.send_html(html("essay.html"))
        self.send_html(b"<h1>Not found</h1>", HTTPStatus.NOT_FOUND)

if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", int(os.environ.get("PORT", "80"))), H).serve_forever()
