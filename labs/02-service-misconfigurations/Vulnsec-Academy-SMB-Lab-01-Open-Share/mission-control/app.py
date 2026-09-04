#!/usr/bin/env python3
"""Atlas Mission Control for SMB Lab 01 — Open Share."""

from __future__ import annotations

import json
import os
import re
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any


APP_ROOT = Path(__file__).resolve().parent
STATE_PATH = Path(os.environ.get("STATE_PATH", "/run/mission-control/lab-state.json"))
MAX_BODY_BYTES = 8_192
PREVIEW = os.environ.get("PREVIEW", "") == "1"
TARGET_IP = "10.23.54.74"
FLAG = "SMB{open_share_yard}"

QUESTIONS = [
    {
        "id": "target",
        "eyebrow": "01 / Confirm target",
        "prompt": "What is the IPv4 address of the records host?",
        "helper": "Printed on the briefing card.",
        "placeholder": "Target IPv4",
        "success": "Target locked. Scan 139 and 445. The web notice is not the share.",
        "error": "That is not the assigned host. Recheck Network Coordinates.",
        "hints": [
            "Open the Briefing tab and read TARGET HOST.",
            "One static address.",
            f"The host is {TARGET_IP}.",
        ],
    },
    {
        "id": "share",
        "eyebrow": "02 / List shares",
        "prompt": "What is the name of the guest-accessible share?",
        "helper": "smbclient -N -L. Share name only — not IPC$.",
        "placeholder": "share",
        "success": "Share records is guest-ok. Connect and list files.",
        "error": "Anonymous listing. Ignore IPC$ and print$. The yard share has a real name.",
        "hints": [
            f"smbclient -N -L //{TARGET_IP}",
            "Look for Disk, not IPC.",
            "The share is records.",
        ],
    },
    {
        "id": "file",
        "eyebrow": "03 / File",
        "prompt": "What is the name of the file that holds the flag?",
        "helper": "Filename only, as listed inside the share.",
        "placeholder": "filename",
        "success": "get that file onto Kali and read it.",
        "error": "smbclient //IP/records -N then ls. Skip the readme.",
        "hints": [
            f"smbclient //{TARGET_IP}/records -N",
            "smb: \\> ls",
            "The file is yard-ledger.txt.",
        ],
    },
    {
        "id": "flag",
        "eyebrow": "04 / Flag",
        "prompt": "Submit the flag from the yard ledger.",
        "helper": "Flags are case-sensitive.",
        "placeholder": "SMB{...}",
        "success": "Flag accepted. Open Share complete — walkthrough access granted.",
        "error": "get yard-ledger.txt and read it on Kali.",
        "hints": [
            "smb: \\> get yard-ledger.txt",
            "cat yard-ledger.txt",
            f"The flag is {FLAG}.",
        ],
    },
]


def preview_state() -> dict[str, Any]:
    return {"session_id": "preview-open-share", "target_ip": TARGET_IP, "port": 445}


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


def normalized(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip()).lower()


def answer_is_correct(question_id: str, answer: str, state: dict[str, Any]) -> bool:
    value = normalized(answer)
    if question_id == "target":
        return value == normalized(str(state["target_ip"]))
    if question_id == "share":
        compact = value.replace(" ", "").strip("/\\")
        return compact in {"records", "records$", "//records"}
    if question_id == "file":
        compact = value.replace(" ", "").strip("/\\")
        return compact in {"yard-ledger.txt", "yard-ledger", "yardledger.txt"}
    if question_id == "flag":
        return answer.strip() == FLAG
    return False


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
            self.send_json(
                {
                    "session_id": state["session_id"],
                    "target_ip": state["target_ip"],
                    "port": state["port"],
                    "preview": PREVIEW,
                    "questions": QUESTIONS,
                }
            )
            return
        self.send_json({"error": "Not found"}, HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:  # noqa: N802
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
            question_id = str(body["question_id"])
            answer = str(body["answer"])
            state = load_lab_state()
        except (json.JSONDecodeError, KeyError, RuntimeError, UnicodeDecodeError):
            self.send_json({"error": "Invalid request"}, HTTPStatus.BAD_REQUEST)
            return
        question = next((item for item in QUESTIONS if item["id"] == question_id), None)
        if question is None:
            self.send_json({"error": "Unknown objective"}, HTTPStatus.BAD_REQUEST)
            return
        correct = answer_is_correct(question_id, answer, state)
        self.send_json({"correct": correct, "message": question["success"] if correct else question["error"]})


def main() -> None:
    port = int(os.environ.get("PORT", "8888"))
    server = ThreadingHTTPServer(("0.0.0.0", port), MissionControlHandler)
    print(f"Atlas Mission Control listening on port {port}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
