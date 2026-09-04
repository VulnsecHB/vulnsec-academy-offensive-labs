#!/usr/bin/env python3
"""Atlas Mission Control for FTP Lab 01 — Open Hatch."""

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
TARGET_IP = "10.23.54.67"
FLAG = "FTP{open_hatch_anon}"

QUESTIONS = [
    {
        "id": "target",
        "eyebrow": "01 / Confirm target",
        "prompt": "What is the IPv4 address of the hatch host?",
        "helper": "Printed on the briefing card.",
        "placeholder": "Target IPv4",
        "success": "Target locked. Scan it. The notice on 80 is not the store.",
        "error": "That is not the assigned host. Recheck Network Coordinates.",
        "hints": [
            "Open the Briefing tab and read TARGET HOST.",
            "One static address.",
            f"The host is {TARGET_IP}.",
        ],
    },
    {
        "id": "port",
        "eyebrow": "02 / Service",
        "prompt": "Which TCP port is the file transfer service on?",
        "helper": "nmap the host. Number only.",
        "placeholder": "port",
        "success": "TCP 21 — FTP. Try anonymous before you hunt for a password.",
        "error": "Scan the host. HTTP 80 is a notice. The files are not there.",
        "hints": [
            f"nmap -sV {TARGET_IP}",
            "Look for ftp / vsftpd.",
            "The port is 21.",
        ],
    },
    {
        "id": "login",
        "eyebrow": "03 / Access",
        "prompt": "What username works with an empty password?",
        "helper": "Classic misconfig. One word.",
        "placeholder": "username",
        "success": "Anonymous FTP. ls, then get the interesting file.",
        "error": "ftp the host. When it asks for a name, the old default still works.",
        "hints": [
            f"ftp {TARGET_IP}",
            "Name: anonymous   Password: (empty, or any email)",
            "The username is anonymous.",
        ],
    },
    {
        "id": "file",
        "eyebrow": "04 / Manifest",
        "prompt": "What is the name of the file that holds the flag?",
        "helper": "Filename only, as listed by FTP ls.",
        "placeholder": "filename",
        "success": "get that file. The flag is inside.",
        "error": "ls after anonymous login. Skip README — look at the inbound sheet.",
        "hints": [
            "ftp> ls",
            "ftp> get inbound-manifest.txt",
            "The file is inbound-manifest.txt.",
        ],
    },
    {
        "id": "flag",
        "eyebrow": "05 / Flag",
        "prompt": "Submit the flag from the inbound manifest.",
        "helper": "Flags are case-sensitive.",
        "placeholder": "FTP{...}",
        "success": "Flag accepted. Open Hatch complete — walkthrough access granted.",
        "error": "get inbound-manifest.txt and read it on Kali.",
        "hints": [
            "ftp> get inbound-manifest.txt",
            "cat inbound-manifest.txt",
            f"The flag is {FLAG}.",
        ],
    },
]


def preview_state() -> dict[str, Any]:
    return {"session_id": "preview-open-hatch", "target_ip": TARGET_IP, "port": 21}


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
    if question_id == "port":
        compact = value.replace("tcp", "").replace("/", "").strip()
        return compact in {"21", "port21"}
    if question_id == "login":
        compact = value.replace(" ", "")
        return compact in {"anonymous", "ftp", "anon"}
    if question_id == "file":
        compact = value.replace(" ", "").strip("/")
        return compact in {"inbound-manifest.txt", "inbound-manifest", "inboundmanifest.txt"}
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
