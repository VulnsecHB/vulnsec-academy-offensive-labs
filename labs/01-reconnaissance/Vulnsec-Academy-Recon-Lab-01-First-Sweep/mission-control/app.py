#!/usr/bin/env python3
"""Atlas Mission Control for Recon Lab 01 — First Sweep."""

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
TARGET_IP = "10.23.54.12"
PROOF = "LS-0412"

QUESTIONS = [
    {
        "id": "target",
        "eyebrow": "01 / Confirm target",
        "prompt": "What is the IPv4 address of the assigned lodge host?",
        "helper": "The address is printed on the briefing card. Do not scan other hosts.",
        "placeholder": "Target IPv4",
        "success": "Target locked. Scan it with nmap before you browse.",
        "error": "That is not the assigned host. Recheck Network Coordinates.",
        "hints": [
            "Open the Briefing tab and read TARGET HOST.",
            "The address is a single static IPv4 — there is no range to sweep.",
            f"The host is {TARGET_IP}.",
        ],
    },
    {
        "id": "count",
        "eyebrow": "02 / Count the ports",
        "prompt": "How many TCP ports are open on the target?",
        "helper": "Run a version scan and count the open rows. Default nmap ports are enough.",
        "placeholder": "number",
        "success": "Two services. Identify what they are before you open a client.",
        "error": "Recount the open ports in the nmap output. Closed and filtered do not count.",
        "hints": [
            f"nmap -sV {TARGET_IP}",
            "Look at lines that say open, not closed.",
            "There are 2 open TCP ports.",
        ],
    },
    {
        "id": "ssh",
        "eyebrow": "03 / Name port 22",
        "prompt": "What service is listening on TCP 22?",
        "helper": "Use the service column from nmap -sV, not a guess.",
        "placeholder": "service name",
        "success": "SSH is live. You do not need to log in for this lab.",
        "error": "That is not the service on 22. Read the nmap service column.",
        "hints": [
            "The left column is the port. The service column is the name nmap assigned.",
            "Port 22 is almost always remote login on Unix.",
            "The service is ssh (OpenSSH).",
        ],
    },
    {
        "id": "http",
        "eyebrow": "04 / Name port 80",
        "prompt": "What service is listening on TCP 80?",
        "helper": "Again: the nmap service column after -sV.",
        "placeholder": "service name",
        "success": "HTTP is live. Browse it next and read the notice board.",
        "error": "That is not the service on 80. Re-read the scan.",
        "hints": [
            f"curl -I http://{TARGET_IP}/ if you want a second opinion.",
            "Port 80 is the default web port.",
            "The service is http.",
        ],
    },
    {
        "id": "proof",
        "eyebrow": "05 / Read the lodge",
        "prompt": "What is the lodge identifier printed on the public notice board?",
        "helper": "Open the web page on port 80. The identifier is on the header.",
        "placeholder": "LS-....",
        "success": "Identifier accepted. First sweep complete — walkthrough access granted.",
        "error": "That is not the lodge identifier. Browse the HTTP service and copy it exactly.",
        "hints": [
            f"Open http://{TARGET_IP}/ in a browser, or curl it.",
            "The header line reads Lodge identifier LS-0412.",
            "The identifier is LS-0412.",
        ],
    },
]


def preview_state() -> dict[str, Any]:
    return {"session_id": "preview-first-sweep", "target_ip": TARGET_IP, "port": 80}


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
    accepted: dict[str, set[str]] = {
        "target": {normalized(str(state["target_ip"]))},
        "count": {"2", "two", "02"},
        "ssh": {"ssh", "openssh", "open ssh", "open-ssh", "22/tcp ssh", "ssh openssh"},
        "http": {"http", "www", "web", "http-server", "http server"},
        "proof": {normalized(PROOF), "ls0412", "nl-ls-0412", "nlls0412"},
    }
    return value in accepted.get(question_id, set())


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
