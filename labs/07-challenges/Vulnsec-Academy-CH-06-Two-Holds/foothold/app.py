#!/usr/bin/env python3
from __future__ import annotations
import os
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
APP_ROOT = Path(__file__).resolve().parent
BASE_PATH = os.environ.get("BASE_PATH","").rstrip("/")
HTML = """<!doctype html><html><head><meta charset=utf-8><title>Jump 172</title>
<style>body{margin:0;background:#101018;color:#ece8ff;font-family:Georgia,serif;padding:72px 8vw} a{color:#b9a6ff} pre{background:#0a0a12;padding:16px}</style></head>
<body><p>NORTHLINE · JUMP</p><h1>Contractor jump 172.</h1>
<p>SOCKS is allowed. The inner VLAN is 10.24.20.0/24 — scan it, do not guess one host.</p>
<pre>j.pike / tidewatch</pre>
<p>There is no prize on this jump besides the tunnel.</p></body></html>""".replace("{{base}}", BASE_PATH)

class H(BaseHTTPRequestHandler):
    def log_message(self, m, *a): print(f"{self.address_string()} - {m % a}", flush=True)
    def route(self):
        p=self.path.split("?",1)[0]
        if BASE_PATH and (p==BASE_PATH or p.startswith(BASE_PATH+"/")): p=p[len(BASE_PATH):] or "/"
        return p.rstrip("/") or "/"
    def send_html(self, s):
        b=s.encode(); self.send_response(200); self.send_header("Content-Type","text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)
    def do_GET(self):
        p=self.route()
        if p=="/healthz":
            b=b'{"status":"ok"}'; self.send_response(200); self.send_header("Content-Type","application/json")
            self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b); return
        self.send_html(HTML)

if __name__=="__main__":
    ThreadingHTTPServer(("0.0.0.0", int(os.environ.get("PORT","80"))), H).serve_forever()
