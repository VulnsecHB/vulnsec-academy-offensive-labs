#!/usr/bin/env python3
"""Atlas Mission Control for Class 00 — Operator Foundations."""

from __future__ import annotations

import json
import os
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any


APP_ROOT = Path(__file__).resolve().parent
STATE_PATH = Path(os.environ.get("STATE_PATH", "/run/mission-control/lab-state.json"))
PREVIEW = os.environ.get("PREVIEW", "") == "1"


def load_state() -> dict[str, Any]:
    if PREVIEW:
        return {"session_id": "preview-class-00", "mode": "class"}
    try:
        data = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"session_id": "class-00", "mode": "class"}
    data.setdefault("mode", "class")
    data.setdefault("session_id", "class-00")
    return data


class MissionControlHandler(BaseHTTPRequestHandler):
    server_version = "AtlasMissionControl/1.0"

    def end_headers(self) -> None:
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "SAMEORIGIN")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self'; img-src 'self' data:; style-src 'self'; "
            "script-src 'self'; connect-src 'self'; base-uri 'none'; frame-ancestors 'self'",
        )
        super().end_headers()

    def log_message(self, message: str, *args: Any) -> None:
        print(f"{self.address_string()} - {message % args}", flush=True)

    def send_bytes(self, payload: bytes, content_type: str, status: HTTPStatus = HTTPStatus.OK) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store" if "json" in content_type else "no-cache")
        self.end_headers()
        self.wfile.write(payload)

    def send_json(self, value: dict[str, Any], status: HTTPStatus = HTTPStatus.OK) -> None:
        self.send_bytes(
            json.dumps(value, separators=(",", ":")).encode("utf-8"),
            "application/json; charset=utf-8",
            status,
        )

    def do_GET(self) -> None:  # noqa: N802
        path = self.path.split("?", 1)[0]
        files = {
            "/": ("index.html", "text/html; charset=utf-8"),
            "/index.html": ("index.html", "text/html; charset=utf-8"),
            "/static/styles.css": ("static/styles.css", "text/css; charset=utf-8"),
            "/static/class.css": ("static/class.css", "text/css; charset=utf-8"),
            "/static/class.js": ("static/class.js", "text/javascript; charset=utf-8"),
        }
        if path in files:
            name, ctype = files[path]
            self.send_bytes((APP_ROOT / name).read_bytes(), ctype)
            return
        if path == "/healthz":
            self.send_json({"status": "ok"})
            return
        if path == "/api/state":
            state = load_state()
            self.send_json(
                {
                    "session_id": state["session_id"],
                    "mode": "class",
                    "preview": PREVIEW,
                    "title": "Operator Foundations",
                }
            )
            return
        self.send_json({"error": "Not found"}, HTTPStatus.NOT_FOUND)


def main() -> None:
    port = int(os.environ.get("PORT", "8888"))
    server = ThreadingHTTPServer(("0.0.0.0", port), MissionControlHandler)
    print(f"Atlas Class 00 listening on port {port}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
