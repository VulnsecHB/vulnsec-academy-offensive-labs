#!/usr/bin/env python3
"""Atlas Mission Control for SQLi Lab 03 — Quiet Ledger."""

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
FLAG = "SQLI{quiet_ledger_northline_clearance}"
TARGET_IP = "10.23.54.104"

QUESTIONS = [
    {
        "id": "target",
        "eyebrow": "01 / Confirm target",
        "prompt": "What is the IPv4 address of the finance ledger?",
        "helper": "The address is assigned and printed on the briefing card.",
        "placeholder": "Target IPv4",
        "success": "Target locked. Open the public invoice lookup next.",
        "error": "That is not the assigned host. Recheck the briefing card.",
        "hints": [
            "Open the Briefing tab and read Network Coordinates.",
            "The target address is listed as TARGET HOST.",
            f"The ledger is {TARGET_IP}.",
        ],
    },
    {
        "id": "parameter",
        "eyebrow": "02 / Isolate the parameter",
        "prompt": "Which query parameter is concatenated into the invoice lookup?",
        "helper": "Name the GET field on the public check form.",
        "placeholder": "parameter name",
        "success": "Parameter confirmed. The page will not print rows — automate the inference.",
        "error": "That is not the injectable parameter. Inspect the lookup form and the URL.",
        "hints": [
            "Submit a known reference such as INV-44190 and watch the address bar.",
            "The form uses method GET and a single text field.",
            "The parameter is ref.",
        ],
    },
    {
        "id": "table",
        "eyebrow": "03 / Enumerate with sqlmap",
        "prompt": "Which table holds directory credentials?",
        "helper": "Point sqlmap at a known-good reference and list tables.",
        "placeholder": "table name",
        "success": "Table identified. Dump it and recover the controller account.",
        "error": "That is not the credential table. Re-run sqlmap --tables.",
        "hints": [
            f'sqlmap -u "http://{TARGET_IP}/lookup?ref=INV-44190" --batch --tables',
            "The lookup is boolean-blind. sqlmap will infer tables from true/false pages.",
            "The table is users.",
        ],
    },
    {
        "id": "account",
        "eyebrow": "04 / Recover the controller",
        "prompt": "What is the finance controller's directory username?",
        "helper": "Dump the users table and read the controller row.",
        "placeholder": "username",
        "success": "Account recovered. Sign in on the finance desk and open the clearance note.",
        "error": "That is not the controller. Dump users again and check the role column.",
        "hints": [
            f'sqlmap -u "http://{TARGET_IP}/lookup?ref=INV-44190" --batch -T users --dump',
            "Clerks cannot open clearance notes.",
            "The controller username is e.vale.",
        ],
    },
    {
        "id": "flag",
        "eyebrow": "05 / Capture proof",
        "prompt": "Submit the flag from the clearance note.",
        "helper": "Flags are case-sensitive and include the braces.",
        "placeholder": "SQLI{...}",
        "success": "Proof accepted. Mission complete — walkthrough access granted.",
        "error": "Flag rejected. Sign in as the controller and copy the clearance number exactly.",
        "hints": [
            "Account login is parameterized. Use the dumped password, do not inject there.",
            "Username e.vale  /  password Clearance-3301",
            "The flag is SQLI{quiet_ledger_northline_clearance}",
        ],
    },
]


def preview_state() -> dict[str, Any]:
    return {
        "session_id": "preview-quiet-ledger",
        "target_ip": TARGET_IP,
        "port": 80,
    }


def load_lab_state() -> dict[str, Any]:
    if PREVIEW:
        return preview_state()
    try:
        data = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError("Lab state is unavailable") from exc
    required = {"session_id", "target_ip", "port"}
    if not required.issubset(data):
        raise RuntimeError("Lab state is incomplete")
    return data


def normalized(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip()).lower()


def answer_is_correct(question_id: str, answer: str, state: dict[str, Any]) -> bool:
    value = normalized(answer)
    accepted: dict[str, set[str]] = {
        "target": {normalized(str(state["target_ip"]))},
        "parameter": {"ref", "reference", "invoice", "invoice reference"},
        "table": {"users", "user"},
        "account": {"e.vale", "evale", "ellis vale", "vale"},
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
