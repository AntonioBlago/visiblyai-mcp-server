"""Karte 606: Hält das Paket Tokens oder Prüfergebnisse, greift ein Widerruf sofort?

Reine Prüfung, kein Produktivcode. Die App wird per ``httpx.MockTransport``
nachgebildet (erst 200, dann 401). Platzhalter-Schlüssel entstehen zur Laufzeit;
im Quelltext steht kein tokenartiger Wert.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path

import httpx
import pytest

from visiblyai_mcp import api_client
from visiblyai_mcp.tools import (
    content_workflow_tools,
    content_write_tools,
    free_tools,
    paid_tools,
    project_tools,
)

SRC_DIR = Path(__file__).resolve().parent.parent / "src" / "visiblyai_mcp"


def _placeholder(prefix: str, char: str, length: int) -> str:
    """Baut einen Platzhalter-Schlüssel zur Laufzeit (kein Literal mit Präfix im Quelltext)."""
    return prefix + "_" + char * length


# ---------------------------------------------------------------------------
# Nachgebildete App
# ---------------------------------------------------------------------------

_OK_BODY = {
    "success": True,
    "data": {"marker": "app-data", "email": "user@example.com", "tier": "pro", "credits_balance": 10},
    "credits_used": 0,
    "credits_remaining": 10,
}
_REVOKED_BODY = {"detail": "Invalid or revoked token"}


class FakeApp:
    """Antwortet der Reihe nach mit den vorgegebenen Statuscodes und merkt Requests und Clients."""

    def __init__(self, statuses: list[int]):
        self.statuses = list(statuses)
        self.requests: list[httpx.Request] = []
        self.clients: list[httpx.Client] = []

    def handler(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        index = len(self.requests) - 1
        status = self.statuses[index] if index < len(self.statuses) else 401
        body = _OK_BODY if status == 200 else _REVOKED_BODY
        return httpx.Response(status, json=body)

    def auth_headers(self) -> list[str | None]:
        return [r.headers.get("Authorization") for r in self.requests]


@pytest.fixture
def fake_app(monkeypatch):
    """Ersetzt ``httpx.Client`` im api_client durch eine Fabrik mit MockTransport."""
    real_client = httpx.Client

    def install(statuses: list[int]) -> FakeApp:
        app = FakeApp(statuses)

        def factory(*args, **kwargs):
            kwargs.pop("transport", None)
            client = real_client(*args, transport=httpx.MockTransport(app.handler), **kwargs)
            app.clients.append(client)
            return client

        monkeypatch.setattr("visiblyai_mcp.api_client.httpx.Client", factory)
        return app

    yield install


# Einstiegspfade: (Name, Aufruf, Erfolgsprüfung, Ablehnungsprüfung)
def _data_ok(out: dict) -> bool:
    return out.get("data", {}).get("marker") == "app-data"


def _rejected_401(out: dict) -> bool:
    return out.get("status_code") == 401 and "data" not in out


def _authenticated(out: dict) -> bool:
    return out.get("authenticated") is True and out.get("email") == "user@example.com"


def _not_authenticated(out: dict) -> bool:
    return out.get("authenticated") is False


ENTRY_PATHS = {
    "paid_tools.get_traffic_snapshot": (
        lambda: paid_tools.get_traffic_snapshot("example.com"), _data_ok, _rejected_401),
    "project_tools.get_site_health": (
        lambda: project_tools.get_site_health(1), _data_ok, _rejected_401),
    "content_write_tools.get_mcp_operation": (
        lambda: content_write_tools.get_mcp_operation(1), _data_ok, _rejected_401),
    "content_workflow_tools.list_articles": (
        lambda: content_workflow_tools.list_articles(1), _data_ok, _rejected_401),
    "free_tools.get_account_info": (
        lambda: free_tools.get_account_info(), _authenticated, _not_authenticated),
}

VAT_PATHS = ["free_tools.get_account_info", "paid_tools.get_traffic_snapshot"]


def _revoke_then_call(fake_app, monkeypatch, path: str, key: str) -> FakeApp:
    call, ok, rejected = ENTRY_PATHS[path]
    monkeypatch.setenv("VISIBLYAI_API_KEY", key)
    app = fake_app([200, 401])

    first = json.loads(call())
    assert ok(first), f"1. Aufruf ohne Daten: {first}"

    # Widerruf in der App; der zweite Aufruf folgt direkt, ohne sleep.
    second = json.loads(call())
    assert rejected(second), f"2. Aufruf nach Widerruf nicht abgelehnt: {second}"
    assert "app-data" not in json.dumps(second), "2. Aufruf liefert Daten des ersten (Cache)"

    assert len(app.requests) == 2, f"erwartet genau 2 Requests, gesehen {len(app.requests)}"
    assert app.auth_headers() == [f"Bearer {key}"] * 2
    return app


# ---------------------------------------------------------------------------
# K1.2 Statischer Wächter
# ---------------------------------------------------------------------------

_FORBIDDEN_MODULES = {"shelve", "redis", "diskcache"}
_FORBIDDEN_FUNCTOOLS = {"lru_cache", "cache", "cached_property"}
_CLIENT_CONSTRUCTORS = {"VisiblyAIClient", "Client"}

# Erlaubnisliste = Befundzeilen in docs/reviews/2026-11-21-pruefung-widerruf/befund.md
ALLOWLIST = {
    ("classifier.py", "global", "_classifier_instance"),
    ("classifier.py", "class-cache-attr", "_compiled_cache"),
    ("cli.py", "file-write", "write_text"),
}


def _call_name(node: ast.Call) -> str | None:
    func = node.func
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        return func.attr
    return None


def _is_client_call(value: ast.AST | None) -> bool:
    if not isinstance(value, ast.Call):
        return False
    func = value.func
    if isinstance(func, ast.Name):
        return func.id in _CLIENT_CONSTRUCTORS
    if isinstance(func, ast.Attribute):
        if func.attr == "VisiblyAIClient":
            return True
        return func.attr == "Client" and isinstance(func.value, ast.Name) and func.value.id == "httpx"
    return False


def _write_mode(node: ast.Call) -> bool:
    mode = None
    if len(node.args) >= 2 and isinstance(node.args[1], ast.Constant):
        mode = node.args[1].value
    for kw in node.keywords:
        if kw.arg == "mode" and isinstance(kw.value, ast.Constant):
            mode = kw.value.value
    return isinstance(mode, str) and any(c in mode for c in "wax+")


def scan_source(source: str, filename: str) -> tuple[list[str], set[tuple[str, str, str]]]:
    """Liefert (Verstöße als 'datei:zeile: grund', getroffene Erlaubnislisten-Einträge)."""
    tree = ast.parse(source, filename=filename)
    violations: list[str] = []
    allowed_hits: set[tuple[str, str, str]] = set()

    def flag(node: ast.AST, kind: str, name: str, reason: str, allowable: bool = False) -> None:
        entry = (filename, kind, name)
        if allowable and entry in ALLOWLIST:
            allowed_hits.add(entry)
            return
        violations.append(f"{filename}:{node.lineno}: {reason}")

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".")[0]
                if root in _FORBIDDEN_MODULES:
                    flag(node, "import", root, f"import {alias.name}")
        elif isinstance(node, ast.ImportFrom):
            root = (node.module or "").split(".")[0]
            if root in _FORBIDDEN_MODULES:
                flag(node, "import", root, f"from {node.module} import ...")
            if root == "functools":
                for alias in node.names:
                    if alias.name in _FORBIDDEN_FUNCTOOLS:
                        flag(node, "functools", alias.name, f"from functools import {alias.name}")
        elif isinstance(node, ast.Attribute):
            base = node.value.id if isinstance(node.value, ast.Name) else None
            if base == "functools" and node.attr in _FORBIDDEN_FUNCTOOLS:
                flag(node, "functools", node.attr, f"functools.{node.attr}")
            elif node.attr == "cached_property":
                flag(node, "functools", node.attr, "cached_property")
            elif base == "pickle" and node.attr in {"dump", "dumps"}:
                flag(node, "pickle", node.attr, f"pickle.{node.attr}")
        elif isinstance(node, ast.Name) and node.id in {"lru_cache", "cached_property"}:
            flag(node, "functools", node.id, node.id)
        elif isinstance(node, ast.Global):
            for name in node.names:
                flag(node, "global", name, f"global {name}", allowable=True)
        elif isinstance(node, ast.ClassDef):
            for stmt in node.body:
                targets = []
                if isinstance(stmt, ast.Assign):
                    targets = [t for t in stmt.targets if isinstance(t, ast.Name)]
                elif isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
                    targets = [stmt.target]
                for target in targets:
                    if "cache" in target.id.lower():
                        flag(stmt, "class-cache-attr", target.id,
                             f"Klassenattribut {node.name}.{target.id}", allowable=True)
        elif isinstance(node, ast.Call):
            name = _call_name(node)
            if name in {"write_text", "write_bytes"}:
                flag(node, "file-write", name, f"Dateischreiben {name}", allowable=True)
            elif name == "open" and _write_mode(node):
                flag(node, "file-write", "open", "open(..., schreibend)", allowable=True)

    for stmt in tree.body:
        value = None
        if isinstance(stmt, (ast.Assign, ast.AnnAssign)):
            value = stmt.value
        if _is_client_call(value):
            violations.append(f"{filename}:{stmt.lineno}: Client-Instanz auf Modulebene")

    return violations, allowed_hits


def test_k1_2_no_hidden_cache():
    """K1.2: Kein verborgener Cache und kein prozessweiter Client im Paket; Erlaubnisliste = Befund."""
    files = sorted(SRC_DIR.rglob("*.py"))
    assert files, f"keine Quelltexte unter {SRC_DIR}"
    violations: list[str] = []
    hits: set[tuple[str, str, str]] = set()
    for path in files:
        found, allowed = scan_source(path.read_text(encoding="utf-8"), path.name)
        violations.extend(found)
        hits |= allowed
    assert violations == [], "\n".join(violations)
    assert hits == ALLOWLIST, f"Erlaubnisliste veraltet, nicht mehr gefunden: {ALLOWLIST - hits}"


def test_k1_2_detector_catches_probe():
    """K1.2: Dieselbe Prüffunktion meldet lru_cache auf get_api_key und einen Modul-Client mit Datei:Zeile."""
    probe_cache = (
        "import functools\n"
        "\n"
        "@functools.lru_cache(maxsize=None)\n"
        "def get_api_key():\n"
        "    return None\n"
    )
    probe_client = (
        "from visiblyai_mcp.api_client import VisiblyAIClient\n"
        "_CLIENT = VisiblyAIClient()\n"
    )
    found_cache, _ = scan_source(probe_cache, "probe_config.py")
    found_client, _ = scan_source(probe_client, "probe_client.py")
    assert any(v.startswith("probe_config.py:3:") and "lru_cache" in v for v in found_cache), found_cache
    assert any(v.startswith("probe_client.py:2:") and "Modulebene" in v for v in found_client), found_client


# ---------------------------------------------------------------------------
# K1.3 Widerruf lc_
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("path", list(ENTRY_PATHS))
def test_k1_3_lc_revoked_rejected_next_call(fake_app, monkeypatch, path):
    """K1.3: Ein in der App widerrufener lc_-Schlüssel wird beim direkt folgenden Aufruf abgelehnt."""
    _revoke_then_call(fake_app, monkeypatch, path, _placeholder("lc", "a", 24))


def test_k1_3_key_change_takes_effect(fake_app, monkeypatch):
    """K1.3: Ein Schlüsselwechsel in der Umgebung wirkt beim nächsten Aufruf (kein prozessweiter Client)."""
    old_key = _placeholder("lc", "a", 24)
    new_key = _placeholder("lc", "b", 24)
    app = fake_app([200, 200])

    monkeypatch.setenv("VISIBLYAI_API_KEY", old_key)
    paid_tools.get_traffic_snapshot("example.com")
    monkeypatch.setenv("VISIBLYAI_API_KEY", new_key)
    paid_tools.get_traffic_snapshot("example.com")

    assert app.auth_headers() == [f"Bearer {old_key}", f"Bearer {new_key}"]
    assert len(app.clients) == 2


# ---------------------------------------------------------------------------
# K1.4 Widerruf vat_ und maximale Verzögerung
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("path", VAT_PATHS)
def test_k1_4_vat_revoked_rejected_next_call(fake_app, monkeypatch, path):
    """K1.4: Ein widerrufenes vat_-Token wird ebenso beim nächsten Aufruf abgelehnt (keine Präfix-Sonderbehandlung)."""
    _revoke_then_call(fake_app, monkeypatch, path, _placeholder("vat", "c", 32))


def test_k1_4_max_delay_bound():
    """K1.4: Die Zahlen im Befund zur maximalen Verzögerung stimmen mit _TIMEOUT überein."""
    assert api_client._TIMEOUT.read == 60.0
    assert api_client._TIMEOUT.connect == 10.0


# ---------------------------------------------------------------------------
# K1.5 Lücken (Befund, Fix offen)
# ---------------------------------------------------------------------------

@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason="Befund 606-L1, Fix offen: httpx.Client mit Bearer-Header bleibt nach dem Aufruf offen bis GC",
)
def test_k1_5_client_closed_after_call(fake_app, monkeypatch):
    """K1.5: Der von get_traffic_snapshot erzeugte httpx.Client ist nach dem Aufruf geschlossen."""
    monkeypatch.setenv("VISIBLYAI_API_KEY", _placeholder("lc", "a", 24))
    app = fake_app([200])
    paid_tools.get_traffic_snapshot("example.com")
    assert len(app.clients) == 1
    assert app.clients[0].is_closed is True


# ---------------------------------------------------------------------------
# K1.7 Kein Schlüssel in der 401-Antwort
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("path", list(ENTRY_PATHS))
@pytest.mark.parametrize("prefix,char,length", [("lc", "a", 24), ("vat", "c", 32)])
def test_k1_7_401_output_has_no_key(fake_app, monkeypatch, path, prefix, char, length):
    """K1.7: Bei 401 enthält die JSON-Antwort des Werkzeugs den Schlüssel-String nicht."""
    key = _placeholder(prefix, char, length)
    monkeypatch.setenv("VISIBLYAI_API_KEY", key)
    fake_app([401])
    call, _, rejected = ENTRY_PATHS[path]
    raw = call()
    assert rejected(json.loads(raw)), raw
    assert key not in raw
    assert char * 8 not in raw
