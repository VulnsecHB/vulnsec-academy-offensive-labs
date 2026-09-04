#!/usr/bin/env python3
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HOME = b"""<!doctype html><html><head><meta charset=utf-8><title>spare hold</title>
<style>body{font-family:Georgia;padding:72px;background:#0d1114;color:#d7e0d7}</style></head>
<body><h1>Spare hold</h1><p>Bonus only. Atlas does not accept this flag.</p>
<p><a href="/bonus.txt">bonus.txt</a></p></body></html>"""
FLAG = b"CH{cutover_bonus_hold}\n"

class H(BaseHTTPRequestHandler):
    def log_message(self, m, *a): print(f"{self.address_string()} - {m % a}", flush=True)
    def do_GET(self):
        if self.path.startswith("/healthz"):
            b=b'{"status":"ok"}'
        elif self.path.startswith("/bonus"):
            b=FLAG
        else:
            b=HOME
        self.send_response(200)
        self.send_header("Content-Type", "text/plain" if b==FLAG or b.startswith(b"{") else "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)

if __name__=="__main__":
    ThreadingHTTPServer(("0.0.0.0", 80), H).serve_forever()
