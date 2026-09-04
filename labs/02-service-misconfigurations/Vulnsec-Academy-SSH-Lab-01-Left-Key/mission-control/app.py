#!/usr/bin/env python3
"""Atlas Mission Control for SSH Lab 01 — Left Key."""

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
TARGET_IP = "10.23.54.60"
FLAG = "SSH{left_key_quay}"

QUESTIONS = [
    {
        "id": "target",
        "eyebrow": "01 / Confirm target",
        "prompt": "What is the IPv4 address of the operator node?",
        "helper": "Printed on the briefing card. SSH here as s.crane.",
        "placeholder": "Target IPv4",
        "success": "Target locked. Password SSH in as s.crane, then look for someone else’s key.",
        "error": "That is not the assigned host. Recheck Network Coordinates.",
        "hints": [
            "Open the Briefing tab and read TARGET HOST.",
            "SSH user is s.crane. Password is on the briefing card.",
            f"The host is {TARGET_IP}.",
        ],
    },
    {
        "id": "keypath",
        "eyebrow": "02 / Find the key",
        "prompt": "What is the full path of the leaked private key?",
        "helper": "It is an id_rsa that s.crane can read. Include /home/…",
        "placeholder": "/home/user/.ssh/id_rsa",
        "success": "World-readable private key. Copy it to Kali before you use it.",
        "error": "Look in other home directories. The misconfig is a 644 id_rsa.",
        "hints": [
            "ls -la /home  then  ls -la /home/*/ .ssh",
            "find /home -name id_rsa -ls",
            "The path is /home/n.quay/.ssh/id_rsa.",
        ],
    },
    {
        "id": "owner",
        "eyebrow": "03 / Key owner",
        "prompt": "Which user does that private key belong to?",
        "helper": "Username only. You will SSH as this account with -i.",
        "placeholder": "username",
        "success": "n.quay. chmod 600 the copy on Kali, then ssh -i.",
        "error": "The home directory that holds the key is the owner. Not s.crane.",
        "hints": [
            "The path is /home/n.quay/.ssh/id_rsa.",
            "Password auth is locked for that account. The key is the door.",
            "The user is n.quay.",
        ],
    },
    {
        "id": "flag",
        "eyebrow": "04 / Flag",
        "prompt": "Submit the flag from n.quay’s home directory.",
        "helper": "Flags are case-sensitive.",
        "placeholder": "SSH{...}",
        "success": "Flag accepted. Left Key complete — walkthrough access granted.",
        "error": "SSH as n.quay with the key and cat ~/user.txt (or ~/flag.txt).",
        "hints": [
            "scp s.crane@10.23.54.60:/home/n.quay/.ssh/id_rsa .",
            "chmod 600 id_rsa && ssh -i id_rsa n.quay@10.23.54.60",
            f"The flag is {FLAG}.",
        ],
    },
]


def preview_state() -> dict[str, Any]:
    return {"session_id": "preview-left-key", "target_ip": TARGET_IP, "port": 22}


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
    if question_id == "keypath":
        compact = value.replace(" ", "").rstrip("/")
        return compact in {
            "/home/n.quay/.ssh/id_rsa",
            "home/n.quay/.ssh/id_rsa",
            "/home/n.quay/.ssh/id_rsa.pem",
        }
    if question_id == "owner":
        compact = value.replace(" ", "")
        return compact in {"n.quay", "nquay", "quay"}
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
