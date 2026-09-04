#!/usr/bin/env python3
"""Northline public site + hidden field telemetry API (intentional SQLi)."""

from __future__ import annotations

import html
import json
import os
import sqlite3
import urllib.parse
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


APP_ROOT = Path(__file__).resolve().parent
BASE_PATH = os.environ.get("BASE_PATH", "").rstrip("/")


def connect() -> sqlite3.Connection:
    db = sqlite3.connect("/tmp/night-wharf.db")
    db.row_factory = sqlite3.Row
    return db


def seed() -> None:
    db = connect()
    db.executescript(
        """
        DROP TABLE IF EXISTS units;
        DROP TABLE IF EXISTS contractors;
        DROP TABLE IF EXISTS operators;

        CREATE TABLE contractors (
            id INTEGER PRIMARY KEY,
            code TEXT,
            name TEXT
        );
        CREATE TABLE units (
            id INTEGER PRIMARY KEY,
            unit_id TEXT,
            berth TEXT,
            status TEXT,
            note TEXT
        );
        CREATE TABLE operators (
            id INTEGER PRIMARY KEY,
            username TEXT,
            password TEXT,
            display_name TEXT,
            role TEXT,
            access TEXT
        );

        INSERT INTO contractors (id, code, name) VALUES
            (1, 'HBR-09', 'Harbour Bearings Ltd'),
            (2, 'TYN-14', 'Tyne Hose & Valve'),
            (3, 'FOR-03', 'Forth Night Stores');

        INSERT INTO units (id, unit_id, berth, status, note) VALUES
            (1, 'NL-2188', 'Yard A', 'standby', 'Coupler pin watch'),
            (2, 'NL-7719', 'Yard C', 'in-service', 'Returned after hose delay'),
            (3, 'NL-4401', 'Bay 2', 'held', 'Night stores only');

        INSERT INTO operators (id, username, password, display_name, role, access) VALUES
            (1, 'm.hale', 'StoreKey-old', 'Mara Hale', 'stores', 'none'),
            (2, 'svc.telemetry', 'LocalOnly!1', 'Telemetry svc', 'service', 'none'),
            (3, 'j.reeves', 'Dockline-1904', 'Jonah Reeves', 'field', 'ssh');
        """
    )
    db.commit()
    db.close()


def render(name: str, **values: str) -> bytes:
    text = (APP_ROOT / "templates" / name).read_text(encoding="utf-8")
    for key, value in values.items():
        text = text.replace("{{" + key + "}}", value)
    return text.encode("utf-8")


def parse_form(body: bytes) -> dict[str, str]:
    parsed = urllib.parse.parse_qs(body.decode("utf-8", errors="replace"), keep_blank_values=True)
    return {key: (values[0] if values else "") for key, values in parsed.items()}


def lookup_unit(unit_id: str) -> tuple[list[dict] | None, str]:
    # INTENTIONAL VULNERABILITY — training lab only.
    query = (
        "SELECT id, unit_id, berth, status, note FROM units "
        f"WHERE unit_id = '{unit_id}'"
    )
    db = connect()
    try:
        rows = [dict(row) for row in db.execute(query).fetchall()]
    except sqlite3.Error:
        db.close()
        return None, "error"
    db.close()
    return rows, "ok"


def nav(active: str) -> str:
    items = [
        ("/", "home", "Home"),
        ("/operations", "operations", "Operations"),
        ("/news", "news", "News"),
        ("/careers", "careers", "Careers"),
        ("/contact", "contact", "Contact"),
    ]
    bits = []
    for href, key, label in items:
        cls = "on" if key == active else ""
        bits.append(f'<a class="{cls}" href="{BASE_PATH}{href}">{label}</a>')
    return "".join(bits)


def site_page(template: str, active: str, title: str, **values: str) -> bytes:
    return render(
        "layout.html",
        title=title,
        nav=nav(active),
        base=BASE_PATH,
        body=render(template, base=BASE_PATH, **values).decode("utf-8"),
    )


class PortalHandler(BaseHTTPRequestHandler):
    server_version = "NorthlinePublic/5.0"

    def log_message(self, message: str, *args) -> None:
        print(f"{self.address_string()} - {message % args}", flush=True)

    def route(self) -> str:
        path = self.path.split("?", 1)[0]
        if path != "/" and path.endswith("/"):
            path = path[:-1]
        if BASE_PATH and (path == BASE_PATH or path.startswith(BASE_PATH + "/")):
            path = path[len(BASE_PATH) :] or "/"
        return path

    def send_html(self, payload: bytes, status: HTTPStatus = HTTPStatus.OK) -> None:
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(payload)

    def send_bytes(self, payload: bytes, content_type: str, status: HTTPStatus = HTTPStatus.OK) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def send_file(self, path: Path, content_type: str) -> None:
        self.send_bytes(path.read_bytes(), content_type)

    def do_GET(self) -> None:  # noqa: N802
        path = self.route()
        query = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)

        if path == "/healthz":
            self.send_bytes(b'{"status":"ok"}', "application/json")
            return
        if path == "/static/site.css":
            self.send_file(APP_ROOT / "static" / "site.css", "text/css; charset=utf-8")
            return
        if path == "/robots.txt":
            body = (
                "User-agent: *\n"
                "Disallow: /intranet-2019/\n"
                "Disallow: /staff-old/\n"
                "Disallow: /backup/\n"
            ).encode()
            self.send_bytes(body, "text/plain; charset=utf-8")
            return
        if path == "/sitemap.xml":
            locs = ["/", "/operations", "/news", "/news/cutover", "/careers", "/contact"]
            xml = ['<?xml version="1.0" encoding="UTF-8"?>', "<urlset>"]
            for loc in locs:
                xml.append(f"  <url><loc>{BASE_PATH}{loc}</loc></url>")
            xml.append("</urlset>\n")
            self.send_bytes("\n".join(xml).encode(), "application/xml")
            return
        if path == "/":
            self.send_html(site_page("home.html", "home", "Northline Operations"))
            return
        if path == "/operations":
            self.send_html(site_page("operations.html", "operations", "Operations — Northline"))
            return
        if path == "/news":
            self.send_html(site_page("news.html", "news", "News — Northline"))
            return
        if path == "/news/cutover":
            self.send_html(site_page("news_cutover.html", "news", "Yard C cutover — Northline"))
            return
        if path == "/careers":
            self.send_html(site_page("careers.html", "careers", "Careers — Northline"))
            return
        if path == "/contact":
            self.send_html(site_page("contact.html", "contact", "Contact — Northline"))
            return
        if path == "/intranet":
            self.send_html(site_page("intranet.html", "home", "Staff intranet — Northline", notice="", error=""))
            return
        if path == "/intranet-2019":
            self.send_html(b"<h1>Archived</h1><p>The 2019 intranet was decommissioned.</p>", HTTPStatus.NOT_FOUND)
            return
        if path in {"/staff-old", "/backup"}:
            self.send_html(b"<h1>Forbidden</h1>", HTTPStatus.FORBIDDEN)
            return
        if path == "/remote":
            self.send_html(render("telemetry.html", base=BASE_PATH))
            return
        if path == "/remote/api":
            unit_id = query.get("id", [""])[0]
            if not unit_id:
                self.send_bytes(b'{"error":"missing id"}', "application/json")
                return
            rows, status = lookup_unit(unit_id)
            if status == "error":
                self.send_bytes(b'{"error":"lookup failed"}', "application/json")
                return
            self.send_bytes(
                json.dumps({"count": len(rows or []), "units": rows or []}, separators=(",", ":")).encode(),
                "application/json",
            )
            return
        self.send_html(b"<h1>Not found</h1>", HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:  # noqa: N802
        if self.route() != "/intranet":
            self.send_html(b"<h1>Not found</h1>", HTTPStatus.NOT_FOUND)
            return
        length = int(self.headers.get("Content-Length", "0") or 0)
        form = parse_form(self.rfile.read(max(0, min(length, 8192))))
        # Parameterized on purpose — dead end.
        db = connect()
        row = db.execute(
            "SELECT id FROM operators WHERE username = ? AND password = ? LIMIT 1",
            (form.get("username", ""), form.get("password", "")),
        ).fetchone()
        db.close()
        if row:
            error = "<p class='banner'>This intranet node is read-only. Use your field node, not this site.</p>"
        else:
            error = "<p class='banner bad'>Those directory credentials were not recognised.</p>"
        self.send_html(site_page("intranet.html", "home", "Staff intranet — Northline", notice="", error=error))


def main() -> None:
    seed()
    port = int(os.environ.get("PORT", "80"))
    server = ThreadingHTTPServer(("0.0.0.0", port), PortalHandler)
    print(f"Northline public site listening on port {port}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
