#!/usr/bin/env python3
"""Northline Materials — spare-parts catalog (intentionally vulnerable search)."""

from __future__ import annotations

import html
import os
import secrets
import sqlite3
import urllib.parse
from http import HTTPStatus
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


APP_ROOT = Path(__file__).resolve().parent
FLAG = "SQLI{false_record_northline_spares}"
SESSIONS: dict[str, dict] = {}
BASE_PATH = os.environ.get("BASE_PATH", "").rstrip("/")


def connect() -> sqlite3.Connection:
    db = sqlite3.connect("/tmp/northline-materials.db")
    db.row_factory = sqlite3.Row
    return db


def seed() -> None:
    db = connect()
    db.executescript(
        """
        DROP TABLE IF EXISTS products;
        DROP TABLE IF EXISTS warehouses;
        DROP TABLE IF EXISTS users;

        CREATE TABLE warehouses (
            id INTEGER PRIMARY KEY,
            code TEXT,
            name TEXT,
            city TEXT
        );
        CREATE TABLE products (
            id INTEGER PRIMARY KEY,
            sku TEXT,
            name TEXT,
            warehouse TEXT,
            qty INTEGER,
            unit_cost REAL,
            lead_days INTEGER
        );
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            password TEXT,
            display_name TEXT,
            role TEXT,
            title TEXT,
            desk_ext TEXT
        );

        INSERT INTO warehouses (id, code, name, city) VALUES
            (1, 'YRD-A', 'Yard A — Couplers', 'Grangemouth'),
            (2, 'YRD-C', 'Yard C — Hydraulics', 'Immingham'),
            (3, 'BAY-2', 'Bay 2 — Night stores', 'Harwich');

        INSERT INTO products (id, sku, name, warehouse, qty, unit_cost, lead_days) VALUES
            (1, 'NL-4401', 'Spherical roller 22220 bearing', 'YRD-A', 14, 186.40, 6),
            (2, 'NL-2188', 'Hardened coupler knuckle pin', 'YRD-A', 41, 27.15, 3),
            (3, 'NL-9012', 'Hydraulic 3000 psi hose', 'YRD-C', 22, 64.90, 8),
            (4, 'NL-1170', 'Composite brake-block pack', 'YRD-A', 96, 18.75, 2),
            (5, 'NL-5520', 'Amber LED marker lamp', 'BAY-2', 7, 41.00, 12),
            (6, 'NL-3304', 'Type C air-dryer cartridge', 'YRD-C', 19, 73.20, 5),
            (7, 'NL-7741', 'Draft-gear follower plate', 'YRD-A', 5, 240.00, 21),
            (8, 'NL-6088', '24V cab-heater element', 'BAY-2', 11, 55.60, 9);

        INSERT INTO users (id, username, password, display_name, role, title, desk_ext) VALUES
            (1, 'j.okonkwo', 'SpareKey#4', 'Jordan Okonkwo', 'clerk', 'Stores Clerk', '4412'),
            (2, 'd.voss', 'NightBay!22', 'Dana Voss', 'clerk', 'Night Stores', '4418'),
            (3, 'm.hale', 'Dockside-7719', 'Mara Hale', 'storekeeper', 'Materials Controller', '4400');
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


def product_cards(rows: list) -> str:
    if not rows:
        return '<p class="empty">No matching stock lines. Try a SKU or a shorter name.</p>'
    cards = []
    for row in rows:
        sku = html.escape(str(row["sku"] if "sku" in row.keys() else row[1]))
        name = html.escape(str(row["name"] if "name" in row.keys() else row[2]))
        warehouse = html.escape(str(row["warehouse"] if "warehouse" in row.keys() else row[3]))
        qty = html.escape(str(row["qty"] if "qty" in row.keys() else row[4]))
        cost = row["unit_cost"] if "unit_cost" in row.keys() else row[5]
        try:
            cost_s = f"£{float(cost):.2f}"
        except (TypeError, ValueError):
            cost_s = html.escape(str(cost))
        cards.append(
            "<article class='sku-card'>"
            f"<span class='sku'>{sku}</span>"
            f"<h3>{name}</h3>"
            f"<dl><div><dt>Warehouse</dt><dd>{warehouse}</dd></div>"
            f"<div><dt>On hand</dt><dd>{qty}</dd></div>"
            f"<div><dt>Unit</dt><dd>{cost_s}</dd></div></dl>"
            "</article>"
        )
    return "<div class='sku-grid'>" + "".join(cards) + "</div>"


def search_products(q: str) -> tuple[list | None, str]:
    # INTENTIONAL VULNERABILITY — training lab only.
    # q is concatenated so sqlmap can close the quote and continue the WHERE clause.
    query = (
        "SELECT id, sku, name, warehouse, qty, unit_cost FROM products "
        f"WHERE name LIKE '%{q}' OR name LIKE '{q}%' OR sku = '{q}'"
    )
    db = connect()
    try:
        rows = db.execute(query).fetchall()
    except sqlite3.Error as exc:
        db.close()
        return None, f"SQLite error: {exc}"
    db.close()
    return list(rows), ""


def safe_login(username: str, password: str) -> dict | None:
    db = connect()
    row = db.execute(
        "SELECT id, username, display_name, role, title, desk_ext FROM users "
        "WHERE username = ? AND password = ? LIMIT 1",
        (username, password),
    ).fetchone()
    db.close()
    return dict(row) if row else None


class CatalogHandler(BaseHTTPRequestHandler):
    server_version = "NorthlineMaterials/3.1"

    def log_message(self, message: str, *args) -> None:
        print(f"{self.address_string()} - {message % args}", flush=True)

    def route(self) -> str:
        path = self.path.split("?", 1)[0]
        if BASE_PATH and (path == BASE_PATH or path.startswith(BASE_PATH + "/")):
            path = path[len(BASE_PATH) :] or "/"
        return path

    def loc(self, path: str) -> str:
        return f"{BASE_PATH}{path}"

    def send_html(self, payload: bytes, status: HTTPStatus = HTTPStatus.OK, headers: list[tuple[str, str]] | None = None) -> None:
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        if headers:
            for key, value in headers:
                self.send_header(key, value)
        self.end_headers()
        self.wfile.write(payload)

    def send_file(self, path: Path, content_type: str) -> None:
        data = path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def current_user(self) -> dict | None:
        cookie = SimpleCookie(self.headers.get("Cookie", ""))
        if "nl_mat" not in cookie:
            return None
        return SESSIONS.get(cookie["nl_mat"].value)

    def page_shell(self, template: str, **values: str) -> bytes:
        user = self.current_user()
        if user:
            account = (
                f"<a class='who' href='{self.loc('/desk')}'>{html.escape(user['display_name'])}</a>"
                f"<a href='{self.loc('/logout')}'>Sign out</a>"
            )
        else:
            account = f"<a href='{self.loc('/account')}'>Staff sign-in</a>"
        return render(
            template,
            base=BASE_PATH,
            account=account,
            **values,
        )

    def do_GET(self) -> None:  # noqa: N802
        path = self.route()
        query = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)

        if path == "/healthz":
            body = b'{"status":"ok"}'
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if path == "/static/catalog.css":
            self.send_file(APP_ROOT / "static" / "catalog.css", "text/css; charset=utf-8")
            return
        if path == "/logout":
            cookie = SimpleCookie(self.headers.get("Cookie", ""))
            if "nl_mat" in cookie:
                SESSIONS.pop(cookie["nl_mat"].value, None)
            self.send_html(
                b"",
                HTTPStatus.FOUND,
                [("Location", self.loc("/")), ("Set-Cookie", "nl_mat=; Max-Age=0; Path=/")],
            )
            return
        if path in {"/", "/catalog"}:
            db = connect()
            rows = db.execute(
                "SELECT id, sku, name, warehouse, qty, unit_cost FROM products ORDER BY sku"
            ).fetchall()
            db.close()
            self.send_html(
                self.page_shell(
                    "catalog.html",
                    heading="Current stock",
                    lede="Live quantities from Yards A, C and Night Bay 2. Search by SKU or description.",
                    q="",
                    notice="",
                    results=product_cards(list(rows)),
                )
            )
            return
        if path == "/search":
            q = query.get("q", [""])[0]
            rows, err = search_products(q)
            if err:
                notice = (
                    "<p class='banner bad'>Materials search failed to evaluate your filter. "
                    f"Stores IT logged: <code>{html.escape(err)}</code></p>"
                )
                results = ""
            else:
                notice = f"<p class='banner'>Showing matches for <b>{html.escape(q) or 'all stock'}</b>.</p>"
                results = product_cards(rows or [])
            self.send_html(
                self.page_shell(
                    "catalog.html",
                    heading="Search results",
                    lede="Results are drawn live from the materials database. Narrow the term if the list is long.",
                    q=html.escape(q),
                    notice=notice,
                    results=results,
                )
            )
            return
        if path == "/account":
            notice = ""
            if query.get("notice") == ["denied"]:
                notice = "<p class='banner warn'>That desk cannot open sealed requisitions.</p>"
            elif query.get("notice") == ["expired"]:
                notice = "<p class='banner warn'>Sign in again to continue.</p>"
            self.send_html(self.page_shell("account.html", notice=notice, error=""))
            return
        if path == "/desk":
            user = self.current_user()
            if user is None:
                self.send_html(b"", HTTPStatus.FOUND, [("Location", self.loc("/account?notice=expired"))])
                return
            if user["role"] == "storekeeper":
                locker = (
                    "<section class='requisition'>"
                    "<p class='kicker'>Sealed requisition · SOC-only</p>"
                    "<h2>Priority hold — coupler stock</h2>"
                    "<p>Do not circulate this hold number outside Materials Control.</p>"
                    f"<p class='flag'>{html.escape(FLAG)}</p>"
                    "</section>"
                )
            else:
                locker = (
                    "<section class='panel'>"
                    "<h2>Open tickets</h2>"
                    "<p>No sealed requisitions are assigned to a clerk desk. Ask the materials controller.</p>"
                    "</section>"
                )
            self.send_html(
                self.page_shell(
                    "desk.html",
                    display=html.escape(user["display_name"]),
                    title=html.escape(user["title"]),
                    role=html.escape(user["role"].title()),
                    ext=html.escape(user["desk_ext"]),
                    locker=locker,
                )
            )
            return
        self.send_html(b"<h1>Not found</h1>", HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:  # noqa: N802
        if self.route() != "/account":
            self.send_html(b"<h1>Not found</h1>", HTTPStatus.NOT_FOUND)
            return
        length = int(self.headers.get("Content-Length", "0") or 0)
        form = parse_form(self.rfile.read(max(0, min(length, 8192))))
        user = safe_login(form.get("username", ""), form.get("password", ""))
        if user is None:
            self.send_html(
                self.page_shell(
                    "account.html",
                    notice="",
                    error="<p class='banner bad'>Those materials-desk credentials were not recognised.</p>",
                )
            )
            return
        token = secrets.token_hex(16)
        SESSIONS[token] = user
        self.send_html(
            b"",
            HTTPStatus.FOUND,
            [("Location", self.loc("/desk")), ("Set-Cookie", f"nl_mat={token}; Path=/; HttpOnly")],
        )


def main() -> None:
    seed()
    port = int(os.environ.get("PORT", "80"))
    server = ThreadingHTTPServer(("0.0.0.0", port), CatalogHandler)
    print(f"Northline Materials listening on port {port}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
