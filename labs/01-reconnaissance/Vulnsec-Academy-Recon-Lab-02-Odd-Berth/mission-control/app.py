#!/usr/bin/env python3
"""Atlas Mission Control for Recon Lab 02 — Odd Berth."""

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
TARGET_IP = "10.23.54.19"
PROOF = "BC-1908"

QUESTIONS = [
    {
        "id": "target",
        "eyebrow": "01 / Confirm target",
        "prompt": "What is the IPv4 address of the assigned berth host?",
        "helper": "Printed on the briefing card. Do not scan other hosts.",
        "placeholder": "Target IPv4",
        "success": "Target locked. Scan it — and do not stop at port 80.",
        "error": "That is not the assigned host. Recheck Network Coordinates.",
        "hints": [
            "Open the Briefing tab and read TARGET HOST.",
            "One static address, no range.",
            f"The host is {TARGET_IP}.",
        ],
    },
    {
        "id": "eighty",
        "eyebrow": "02 / Check the obvious port",
        "prompt": "Is TCP port 80 open on the target?",
        "helper": "Answer yes or no from the nmap STATE column.",
        "placeholder": "yes / no",
        "success": "Port 80 is closed. The web service lives somewhere else.",
        "error": "Re-read the STATE column for port 80. Closed is not open.",
        "hints": [
            f"nmap -sV -p80 {TARGET_IP}",
            "If nmap prints closed or shows no open row for 80, the answer is no.",
            "No. TCP 80 is not open.",
        ],
    },
    {
        "id": "count",
        "eyebrow": "03 / Widen the scan",
        "prompt": "How many TCP ports are open on the target?",
        "helper": "Default nmap ports can miss uncommon web ports. Use -p- on this host.",
        "placeholder": "number",
        "success": "Two services, neither of them on 80. Name the HTTP port next.",
        "error": "Recount open rows. If you only scanned 80, widen the list.",
        "hints": [
            f"nmap -sV -p- {TARGET_IP}",
            "-p- means every TCP port, not the default top 1000.",
            "There are 2 open TCP ports.",
        ],
    },
    {
        "id": "httpport",
        "eyebrow": "04 / Find the web port",
        "prompt": "On which TCP port is the HTTP service listening?",
        "helper": "The port number from the nmap row whose service is http.",
        "placeholder": "port number",
        "success": "HTTP is on 8088. Browse that port and read the berth identifier.",
        "error": "That is not the HTTP port. Look at the service column, not SSH.",
        "hints": [
            "SSH is 22. The other open port is the web service.",
            "nmap prints 8088/tcp open http.",
            "The HTTP port is 8088.",
        ],
    },
    {
        "id": "proof",
        "eyebrow": "05 / Read the board",
        "prompt": "What is the berth identifier printed on the public board?",
        "helper": "Open http://TARGET:8088 — not port 80.",
        "placeholder": "BC-....",
        "success": "Identifier accepted. Odd Berth complete — walkthrough access granted.",
        "error": "That is not the berth identifier. Browse port 8088 and copy it exactly.",
        "hints": [
            f"curl -s http://{TARGET_IP}:8088/",
            "The header line reads Berth identifier BC-1908.",
            "The identifier is BC-1908.",
        ],
    },
]


def preview_state() -> dict[str, Any]:
    return {"session_id": "preview-odd-berth", "target_ip": TARGET_IP, "port": 8088}


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
        "eighty": {
            "no",
            "n",
            "closed",
            "not open",
            "false",
            "80 closed",
            "port 80 closed",
            "nope",
        },
        "count": {"2", "two", "02"},
        "httpport": {"8088", "tcp 8088", "8088/tcp", "port 8088"},
        "proof": {normalized(PROOF), "bc1908", "bc 1908"},
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
