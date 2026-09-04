#!/usr/bin/env python3
from __future__ import annotations
import os, sqlite3
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

APP_ROOT = Path(__file__).resolve().parent
BASE_PATH = os.environ.get("BASE_PATH", "").rstrip("/")
DB = Path("/tmp/tide.db")

def init():
    con = sqlite3.connect(DB)
    con.execute("CREATE TABLE IF NOT EXISTS reports (id INTEGER, title TEXT, body TEXT)")
    con.execute("DELETE FROM reports")
    con.executemany("INSERT INTO reports VALUES (?,?,?)", [
        (1, "shift", "Calm water."),
        (2, "pump", "Replaced gasket."),
        (3, "flag", "CH{inner_tide_inner}"),
    ])
    con.commit(); con.close()

def page():
    return (APP_ROOT/"templates"/"home.html").read_text(encoding="utf-8").replace("{{base}}", BASE_PATH)

class H(BaseHTTPRequestHandler):
    server_version = "TideDesk/1.0"
    def log_message(self, m, *a): print(f"{self.address_string()} - {m % a}", flush=True)
    def route(self):
        p=self.path.split("?",1)[0]
        if p!="/" and p.endswith("/"): p=p[:-1]
        if BASE_PATH and (p==BASE_PATH or p.startswith(BASE_PATH+"/")): p=p[len(BASE_PATH):] or "/"
        return p
    def send_html(self, s, st=HTTPStatus.OK):
        b=s.encode(); self.send_response(st); self.send_header("Content-Type","text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)
    def send_bytes(self, b, t):
        self.send_response(200); self.send_header("Content-Type", t)
        self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)
    def do_GET(self):
        p=self.route()
        if p=="/healthz": return self.send_bytes(b'{"status":"ok"}',"application/json")
        if p=="/static/site.css": return self.send_bytes((APP_ROOT/"static"/"site.css").read_bytes(),"text/css; charset=utf-8")
        if p=="/":
            return self.send_html(page().replace("{{result}}","Pick a report id."))
        if p=="/report":
            rid = parse_qs(urlparse(self.path).query).get("id",["1"])[0]
            con=sqlite3.connect(DB)
            try:
                rows=con.execute(f"SELECT id, title, body FROM reports WHERE id={rid}").fetchall()
                result = "".join(f"<article><h2>{t}</h2><p>{b}</p></article>" for i,t,b in rows) or "<p>none</p>"
            except sqlite3.Error as e:
                result = f"<pre>{e}</pre>"
            con.close()
            return self.send_html(page().replace("{{result}}", result))
        self.send_html("<h1>404</h1>", HTTPStatus.NOT_FOUND)

if __name__=="__main__":
    init()
    ThreadingHTTPServer(("0.0.0.0", int(os.environ.get("PORT","80"))), H).serve_forever()
