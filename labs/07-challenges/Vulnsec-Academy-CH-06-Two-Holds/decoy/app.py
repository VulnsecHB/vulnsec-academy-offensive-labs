#!/usr/bin/env python3
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PAGE = """<!doctype html><html><head><meta charset=utf-8><title>appliance</title>
<style>body{background:#1a120c;color:#c4b8a8;font-family:sans-serif;padding:80px}</style></head>
<body><h1>403 — out of scope appliance</h1><p>This inner host is a UPS controller. No flags, no SMB, no SSH.</p></body></html>""".encode("utf-8")

class H(BaseHTTPRequestHandler):
    def log_message(self, m, *a): print(f"{self.address_string()} - {m % a}", flush=True)
    def do_GET(self):
        if self.path.startswith("/healthz"):
            b=b'{"status":"ok"}'; self.send_response(200); self.send_header("Content-Type","application/json")
            self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b); return
        self.send_response(403); self.send_header("Content-Type","text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(PAGE))); self.end_headers(); self.wfile.write(PAGE)

if __name__=="__main__":
    ThreadingHTTPServer(("0.0.0.0", 80), H).serve_forever()
