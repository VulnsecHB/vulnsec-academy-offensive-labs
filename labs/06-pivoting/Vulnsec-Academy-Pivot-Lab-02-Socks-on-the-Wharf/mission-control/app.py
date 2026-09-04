#!/usr/bin/env python3
"""Atlas Mission Control for Pivot Lab 02 — Socks on the Wharf."""

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
TARGET_IP = "10.23.54.247"
FLAG = "PIV{socks_on_the_wharf}"

QUESTIONS = [
    {"id":"target","eyebrow":"01 / Confirm foothold","prompt":"What is the IPv4 address of the edge SSH host?","helper":"Briefing card.","placeholder":"Target IPv4","success":"Edge locked. This lab is SOCKS, not a single -L.","error":"Recheck Network Coordinates.","hints":["Open Briefing.","10.23.54.247"]},
    {"id":"inner","eyebrow":"02 / Scan through the hop","prompt":"What IPv4 should you scan on the inner net?","helper":"~/note.txt on the foothold.","placeholder":"10.24.10.x","success":"Do not -L every port. Use a dynamic SOCKS.","error":"SSH as n.wharf and read note.txt.","hints":["ssh n.wharf@10.23.54.247","10.24.10.21"]},
    {"id":"socks","eyebrow":"03 / Dynamic forward","prompt":"Which ssh flag opens a SOCKS proxy?","helper":"One letter, with the dash.","placeholder":"-?","success":"ssh -D 9050 n.wharf@10.23.54.247 then point proxychains at 127.0.0.1:9050","error":"-L is one port. You want dynamic.","hints":["man ssh | grep dynamic","The flag is -D."]},
    {"id":"ports","eyebrow":"04 / Inner ports","prompt":"Which two TCP ports are open on 10.24.10.21? (low then high)","helper":"proxychains nmap -sT -Pn 10.24.10.21","placeholder":"80 8088","success":"80 is the decoy. The flag is on 8088.","error":"TCP connect scan through SOCKS. SYN scan will not proxy.","hints":["proxychains nmap -sT -Pn -p 1-10000 10.24.10.21","80 and 8088","80 8088"]},
    {"id":"flag","eyebrow":"05 / Hidden berth","prompt":"Submit the flag from the service that is not on port 80.","helper":"Case-sensitive.","placeholder":"PIV{...}","success":"Flag accepted. Socks on the Wharf complete.","error":"proxychains curl http://10.24.10.21:8088/","hints":["proxychains curl -s http://10.24.10.21:8088/","PIV{socks_on_the_wharf}"]}
]


def preview_state() -> dict[str, Any]:
    return {"session_id": "preview-socks", "target_ip": TARGET_IP, "port": 22}


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
    if question_id == "inner":
        return value.replace(" ", "") == "10.24.10.21"
    if question_id == "socks":
        compact = value.replace(" ", "")
        return compact in {"-d", "d", "socks", "socks5", "-dsocks"}
    if question_id == "ports":
        nums = re.findall(r"\d+", value)
        return nums == ["80", "8088"] or set(nums) == {"80", "8088"}
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
