#!/usr/bin/env python3
"""Atlas Mission Control for Recon Lab 03 — Unlisted Door."""

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
TARGET_IP = "10.23.54.31"
PROOF = "UD-3104"

QUESTIONS = [
    {
        "id": "target",
        "eyebrow": "01 / Confirm target",
        "prompt": "What is the IPv4 address of the stores desk?",
        "helper": "Printed on the briefing card.",
        "placeholder": "Target IPv4",
        "success": "Target locked. Browse the public pages, then fuzz what they do not link.",
        "error": "That is not the assigned host. Recheck Network Coordinates.",
        "hints": [
            "Open the Briefing tab and read TARGET HOST.",
            "One static address.",
            f"The host is {TARGET_IP}.",
        ],
    },
    {
        "id": "tool",
        "eyebrow": "02 / Pick the fuzzer",
        "prompt": "Which directory fuzzer is this lab built around?",
        "helper": "Name the tool, not the wordlist. ffuf is accepted as an equivalent.",
        "placeholder": "tool name",
        "success": "Point it at the web root with a common directory wordlist.",
        "error": "nmap already did its job. This lab is a directory fuzzer.",
        "hints": [
            "Kali ships gobuster and ffuf.",
            "The briefing names gobuster as the intended tool.",
            "The answer is gobuster (ffuf is also accepted).",
        ],
    },
    {
        "id": "path",
        "eyebrow": "03 / Name the unlisted door",
        "prompt": "What hidden directory returns HTTP 200 and is not linked from the public site?",
        "helper": "A common.txt-style wordlist is enough. Ignore robots.txt decoys that 404.",
        "placeholder": "/directory",
        "success": "That board is not on the nav. Open it and read the handover.",
        "error": "That path is not the 200 you want. Fuzz the root and skip the 404s.",
        "hints": [
            f'gobuster dir -u http://{TARGET_IP} -w /usr/share/wordlists/dirb/common.txt',
            "robots.txt lists /backup/ and /intranet-old/ — those 404.",
            "The hidden directory is /internal/.",
        ],
    },
    {
        "id": "decoy",
        "eyebrow": "04 / Ignore robots",
        "prompt": "Name one path listed in robots.txt that is not actually on the server.",
        "helper": "Disallow is not a map of live folders.",
        "placeholder": "/path",
        "success": "Decoy noted. robots.txt is a hint file, not an inventory.",
        "error": "Open /robots.txt and try those paths. The live hidden dir is not listed there.",
        "hints": [
            f"curl -s http://{TARGET_IP}/robots.txt",
            "Both listed paths return 404.",
            "Acceptable answers: /backup/ or /intranet-old/.",
        ],
    },
    {
        "id": "proof",
        "eyebrow": "05 / Read the handover",
        "prompt": "What handover identifier is printed on the internal board?",
        "helper": "Open the hidden directory in a browser or curl.",
        "placeholder": "UD-....",
        "success": "Identifier accepted. Unlisted Door complete — walkthrough access granted.",
        "error": "That is not the identifier. Open /internal/ and copy it exactly.",
        "hints": [
            f"curl -s http://{TARGET_IP}/internal/",
            "The line reads Handover identifier UD-3104.",
            "The identifier is UD-3104.",
        ],
    },
]


def preview_state() -> dict[str, Any]:
    return {"session_id": "preview-unlisted-door", "target_ip": TARGET_IP, "port": 80}


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
    accepted: dict[str, set[str]] = {
        "target": {normalized(str(state["target_ip"]))},
        "tool": {
            "gobuster",
            "ffuf",
            "feroxbuster",
            "dirb",
            "dirbuster",
            "wfuzz",
        },
        "path": {"internal", "internal/", "/internal", "/internal/"},
        "decoy": {
            "backup",
            "backup/",
            "/backup",
            "/backup/",
            "intranet-old",
            "intranet-old/",
            "/intranet-old",
            "/intranet-old/",
        },
        "proof": {normalized(PROOF), "ud3104"},
    }
    if question_id in {"path", "decoy"}:
        return value in {normalized(item) for item in accepted[question_id]}
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
