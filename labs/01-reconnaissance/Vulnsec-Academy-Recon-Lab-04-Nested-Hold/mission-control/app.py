#!/usr/bin/env python3
"""Atlas Mission Control for Recon Lab 04 — Nested Hold."""

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
TARGET_IP = "10.23.54.38"
PROOF = "NH-3802"

QUESTIONS = [
    {
        "id": "target",
        "eyebrow": "01 / Confirm target",
        "prompt": "What is the IPv4 address of the records office?",
        "helper": "Printed on the briefing card.",
        "placeholder": "Target IPv4",
        "success": "Target locked. The public catalogue will not list the hold.",
        "error": "That is not the assigned host. Recheck Network Coordinates.",
        "hints": [
            "Open the Briefing tab and read TARGET HOST.",
            "One static address.",
            f"The host is {TARGET_IP}.",
        ],
    },
    {
        "id": "folder",
        "eyebrow": "02 / First fuzz",
        "prompt": "What hidden directory on the web root is a closed hold (HTTP 200, not linked)?",
        "helper": "gobuster dir on the root with common.txt is enough for this step.",
        "placeholder": "/directory",
        "success": "That splash has no file listing. Fuzz inside it next.",
        "error": "Fuzz the root. The live folder is not in robots.txt.",
        "hints": [
            f'gobuster dir -u http://{TARGET_IP} -w /usr/share/wordlists/dirb/common.txt',
            "robots.txt lists /old/ and /records-old/ — those 404.",
            "The directory is /archive/.",
        ],
    },
    {
        "id": "ext",
        "eyebrow": "03 / Extensions",
        "prompt": "Which gobuster flag adds file extensions such as bak, old, and txt?",
        "helper": "A second fuzz of /archive without extensions will miss the backup file.",
        "placeholder": "flag",
        "success": "Use it on /archive with bak,old,txt.",
        "error": "Look up gobuster dir help. You need the extensions flag, not a new wordlist only.",
        "hints": [
            "gobuster dir --help | grep -i extension",
            "ffuf uses -e .bak,.old,.txt for the same job.",
            "The gobuster flag is -x.",
        ],
    },
    {
        "id": "file",
        "eyebrow": "04 / Name the backup",
        "prompt": "What is the filename of the backup sitting in the closed hold?",
        "helper": "Include the extension.",
        "placeholder": "name.ext",
        "success": "Fetch that file. The identifier is inside.",
        "error": "Fuzz /archive with -x bak,old,txt and a common wordlist.",
        "hints": [
            f'gobuster dir -u http://{TARGET_IP}/archive -w /usr/share/wordlists/dirb/common.txt -x bak,old,txt',
            "The stem is a word on common.txt. The extension is bak.",
            "The file is notes.bak.",
        ],
    },
    {
        "id": "proof",
        "eyebrow": "05 / Read the hold",
        "prompt": "What hold identifier is printed in the backup file?",
        "helper": "curl the file. Flags and identifiers are case-sensitive.",
        "placeholder": "NH-....",
        "success": "Identifier accepted. Nested Hold complete — walkthrough access granted.",
        "error": "Open /archive/notes.bak and copy the identifier exactly.",
        "hints": [
            f"curl -s http://{TARGET_IP}/archive/notes.bak",
            "The line reads Hold identifier: NH-3802.",
            "The identifier is NH-3802.",
        ],
    },
]


def preview_state() -> dict[str, Any]:
    return {"session_id": "preview-nested-hold", "target_ip": TARGET_IP, "port": 80}


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
    return re.sub(r"\s+", " ", value.strip()).lower().strip("/")


def answer_is_correct(question_id: str, answer: str, state: dict[str, Any]) -> bool:
    value = normalized(answer)
    if question_id == "target":
        return value == normalized(str(state["target_ip"]))
    if question_id == "folder":
        return value in {"archive", "archive/", "/archive", "/archive/"}
    if question_id == "ext":
        compact = value.replace(" ", "")
        return compact in {"-x", "x", "--extensions", "extensions", "-e", "e"}
    if question_id == "file":
        return value in {"notes.bak", "archive/notes.bak", "/archive/notes.bak"}
    if question_id == "proof":
        return value in {normalized(PROOF), "nh3802"}
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
