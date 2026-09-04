#!/usr/bin/env python3
"""Atlas Mission Control for SQLi Lab 01 — Broken Gate."""

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
FLAG = "SQLI{broken_gate_northline_admin}"

QUESTIONS = [
    {
        "id": "scope",
        "eyebrow": "01 / Define scope",
        "prompt": "What network are you authorized to scan?",
        "helper": "Enter the range exactly as CIDR notation.",
        "placeholder": "10.x.x.x/xx",
        "success": "Scope locked. Every probe must remain inside this boundary.",
        "error": "That range is outside the mission boundary. Recheck the briefing card.",
        "hints": [
            "The scope appears in the Network Coordinates card.",
            "Look for the value ending in /24.",
            "The authorized range is 10.23.54.0/24.",
        ],
    },
    {
        "id": "hosts",
        "eyebrow": "02 / Discover hosts",
        "prompt": "How many live hosts did Nmap return?",
        "helper": "Count the gateway and the unknown node.",
        "placeholder": "Number of live hosts",
        "success": "Correct. One address is infrastructure; the other is the staff portal.",
        "error": "Not quite. Run host discovery again and count each responsive address.",
        "hints": [
            "Use host discovery rather than a full port scan.",
            "Nmap's -sn option performs host discovery only.",
            "Run: nmap -sn 10.23.54.0/24",
        ],
    },
    {
        "id": "target",
        "eyebrow": "03 / Isolate the target",
        "prompt": "What IP address belongs to the unknown field node?",
        "helper": "Exclude the known gateway from your host-discovery results.",
        "placeholder": "Discovered target IPv4",
        "success": "Target acquired. You separated the portal from its gateway.",
        "error": "That is not the field node. Compare your scan with 10.23.54.1.",
        "hints": [
            "Remove the known gateway from the list of live hosts.",
            "The other responsive address is the target.",
            "The staff portal is the non-gateway host on 10.23.54.0/24.",
        ],
    },
    {
        "id": "service",
        "eyebrow": "04 / Fingerprint service",
        "prompt": "Which application protocol is listening on TCP 80?",
        "helper": "Answer with the protocol name, not the server product.",
        "placeholder": "Application protocol",
        "success": "Protocol confirmed. Open the staff portal in a browser next.",
        "error": "That does not match the service probe. Review the SERVICE column.",
        "hints": [
            "Use Nmap service/version detection against the discovered IP.",
            "Run: nmap -Pn -sV -p80 <TARGET_IP>",
            "The protocol is HTTP.",
        ],
    },
    {
        "id": "vector",
        "eyebrow": "05 / Identify the vector",
        "prompt": "Which login field is concatenated into the SQL query?",
        "helper": "Name the form field you can break with a single quote.",
        "placeholder": "form field name",
        "success": "Vector identified. Force the WHERE clause true and obtain an admin session.",
        "error": "That is not the unsafe parameter. Inspect the login form and try breaking one field at a time.",
        "hints": [
            "The staff portal posts two fields: username and password.",
            "Try submitting a single quote in each field and watch which one changes the response.",
            "The injectable field is username.",
        ],
    },
    {
        "id": "flag",
        "eyebrow": "06 / Capture proof",
        "prompt": "Submit the flag from the administrator dashboard.",
        "helper": "Flags are case-sensitive and include the braces.",
        "placeholder": "SQLI{...}",
        "success": "Proof accepted. Mission complete — walkthrough access granted.",
        "error": "Flag rejected. Sign in through the broken gate and copy the sealed incident note exactly.",
        "hints": [
            "A tautology in the username field comments out the password check.",
            "Try: username  ' OR 1=1--    password  anything",
            "The flag is SQLI{broken_gate_northline_admin}",
        ],
    },
]


def preview_state() -> dict[str, Any]:
    return {
        "session_id": "preview-broken-gate",
        "scope": "10.23.54.0/24",
        "gateway": "10.23.54.1",
        "target_ip": "10.23.54.47",
        "port": 80,
    }


def load_lab_state() -> dict[str, Any]:
    if PREVIEW:
        return preview_state()
    try:
        data = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError("Lab state is unavailable") from exc
    required = {"session_id", "scope", "gateway", "target_ip", "port"}
    if not required.issubset(data):
        raise RuntimeError("Lab state is incomplete")
    return data


def normalized(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip()).lower()


def answer_is_correct(question_id: str, answer: str, state: dict[str, Any]) -> bool:
    value = normalized(answer)
    accepted: dict[str, set[str]] = {
        "scope": {normalized(str(state["scope"]))},
        "hosts": {"2", "two"},
        "target": {normalized(str(state["target_ip"]))},
        "service": {"http", "http/1.1", "www", "web"},
        "vector": {"username", "user", "user name", "uname"},
    }
    if question_id == "flag":
        return answer.strip() == FLAG
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
                    "scope": state["scope"],
                    "gateway": state["gateway"],
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
