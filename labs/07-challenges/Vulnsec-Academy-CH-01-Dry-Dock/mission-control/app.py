#!/usr/bin/env python3
"""Atlas Mission Control for Dry Dock (flag drop only)."""
from __future__ import annotations

import json
import os
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

APP_ROOT = Path(__file__).resolve().parent
STATE_PATH = Path(os.environ.get("STATE_PATH", "/run/mission-control/lab-state.json"))
MAX_BODY_BYTES = 8_192
PREVIEW = os.environ.get("PREVIEW", "") == "1"
TARGET_IP = "10.23.54.130"
LAB_ID = "ch-01-dry-dock"
FLAGS = {
    "user": "CH{dry_dock_user}",
    "root": "CH{dry_dock_root}",
}

FLAG_META = [
    {
        "id": "user",
        "eyebrow": "01 / User",
        "prompt": "Submit the user flag.",
        "helper": "Usually user.txt after a foothold shell.",
        "placeholder": "CH{...}",
        "success": "User flag accepted.",
        "error": "That is not the user flag.",
    },
    {
        "id": "root",
        "eyebrow": "02 / Root",
        "prompt": "Submit the root flag.",
        "helper": "Usually root.txt after privilege escalation (or the inner prize on pivot challenges).",
        "placeholder": "CH{...}",
        "success": "Root flag accepted. Walkthrough access granted.",
        "error": "That is not the root flag.",
    },
]


def preview_state() -> dict[str, Any]:
    return {"session_id": "preview-ch-01-dry-dock", "target_ip": TARGET_IP, "port": 80}


def load_lab_state() -> dict[str, Any]:
    if PREVIEW:
        return preview_state()
    try:
        data = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError("Lab state is unavailable") from exc
    if not {"session_id", "target_ip", "port"}.issubset(data):
        raise RuntimeError("Lab state is incomplete")
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
        self.send_bytes(json.dumps(value, separators=(",", ":")).encode("utf-8"), "application/json; charset=utf-8", status)

    def do_GET(self) -> None:
        if self.path in {"/", "/index.html"}:
            self.send_bytes((APP_ROOT / "index.html").read_bytes(), "text/html; charset=utf-8")
            return
        if self.path == "/static/styles.css":
            self.send_bytes((APP_ROOT / "static/styles.css").read_bytes(), "text/css; charset=utf-8")
            return
        if self.path == "/static/app.js":
            self.send_bytes((APP_ROOT / "static/app.js").read_bytes(), "text/javascript; charset=utf-8")
            return
        if self.path == "/healthz":
            try:
                load_lab_state()
            except RuntimeError:
                self.send_json({"status": "starting"}, HTTPStatus.SERVICE_UNAVAILABLE)
                return
            self.send_json({"status": "ok"})
            return
        if self.path == "/api/state":
            try:
                state = load_lab_state()
            except RuntimeError as exc:
                self.send_json({"error": str(exc)}, HTTPStatus.SERVICE_UNAVAILABLE)
                return
            self.send_json({
                "session_id": state["session_id"],
                "target_ip": state["target_ip"],
                "port": state["port"],
                "preview": PREVIEW,
                "lab_id": LAB_ID,
                "questions": FLAG_META,
            })
            return
        self.send_json({"error": "Not found"}, HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
        if self.path != "/api/check":
            self.send_json({"error": "Not found"}, HTTPStatus.NOT_FOUND)
            return
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            content_length = 0
        if content_length < 1 or content_length > MAX_BODY_BYTES:
            self.send_json({"error": "Invalid request size"}, HTTPStatus.BAD_REQUEST)
            return
        try:
            body = json.loads(self.rfile.read(content_length))
            flag_id = str(body["question_id"])
            answer = str(body["answer"]).strip()
            load_lab_state()
        except (json.JSONDecodeError, KeyError, RuntimeError, UnicodeDecodeError):
            self.send_json({"error": "Invalid request"}, HTTPStatus.BAD_REQUEST)
            return
        expected = FLAGS.get(flag_id)
        if expected is None:
            self.send_json({"error": "Unknown flag"}, HTTPStatus.BAD_REQUEST)
            return
        meta = next(item for item in FLAG_META if item["id"] == flag_id)
        self.send_json({"correct": answer == expected, "message": meta["success"] if answer == expected else meta["error"]})


def main() -> None:
    port = int(os.environ.get("PORT", "8888"))
    server = ThreadingHTTPServer(("0.0.0.0", port), MissionControlHandler)
    print(f"Atlas Mission Control listening on port {port}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
