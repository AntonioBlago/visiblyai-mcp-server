"""get_skill reicht den optionalen Parameter lang an die API durch."""
from visiblyai_mcp.knowledge import skills


class _Resp:
    status_code = 200

    def json(self):
        return {"success": True, "data": "# Methodik"}


def _capture(monkeypatch):
    seen = {}

    def fake_get(url, params=None, timeout=None):
        seen["params"] = params
        return _Resp()

    monkeypatch.setattr(skills.httpx, "get", fake_get)
    return seen


def test_ohne_lang_wird_kein_lang_gesendet(monkeypatch):
    seen = _capture(monkeypatch)
    skills.get_skill("seo-audit")
    assert seen["params"] == {"name": "seo-audit"}


def test_mit_lang_wird_lang_gesendet(monkeypatch):
    seen = _capture(monkeypatch)
    skills.get_skill("seo-audit", lang="de")
    assert seen["params"] == {"name": "seo-audit", "lang": "de"}


def test_liste_mit_lang(monkeypatch):
    seen = _capture(monkeypatch)
    skills.list_skills(lang="en")
    assert seen["params"] == {"name": "list", "lang": "en"}


def test_server_tool_hat_lang_parameter():
    from visiblyai_mcp import server
    import inspect

    assert "lang" in inspect.signature(server.get_skill).parameters
