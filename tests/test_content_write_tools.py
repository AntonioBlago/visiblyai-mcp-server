"""Write tools (2A): argument mapping, generated idempotency key, validation, error reporting."""
import json
from unittest.mock import MagicMock, patch

from visiblyai_mcp.api_client import APIError
from visiblyai_mcp.tools import content_write_tools as w

OK = {"success": True, "data": {"operation_id": 1, "status": "succeeded"}, "credits_used": 0, "credits_remaining": None}


def _run(fn, method, *args, **kwargs):
    client = MagicMock()
    getattr(client, method).return_value = OK
    with patch("visiblyai_mcp.tools.content_write_tools._require_key", return_value=client):
        out = json.loads(fn(*args, **kwargs))
    return out, getattr(client, method).call_args


def test_submit_maps_payload_and_generates_key():
    out, call = _run(w.submit_article_draft, "submit_article_draft", 5, "T", "# x", "kw", format="markdown",
                     persona_id=3)
    payload = call.args[0]
    assert payload["project_id"] == 5 and payload["format"] == "markdown" and payload["persona_id"] == 3
    assert "query_id" not in payload and len(payload["idempotency_key"]) == 32
    assert out["idempotency_key"] == payload["idempotency_key"] and out["data"]["status"] == "succeeded"


def test_submit_keeps_given_key_and_validates():
    _, call = _run(w.submit_article_draft, "submit_article_draft", 5, "T", "x", "kw", idempotency_key="abc",
                   query_id=9, expected_query_revision=2)
    assert call.args[0]["idempotency_key"] == "abc" and call.args[0]["query_id"] == 9
    assert "error" in json.loads(w.submit_article_draft(5, "", "x", "kw"))
    assert "error" in json.loads(w.submit_article_draft(5, "T", "x", "kw", format="docx"))


def test_update_requires_field_and_format_with_content():
    assert "error" in json.loads(w.update_article(7, 1))
    assert "error" in json.loads(w.update_article(7, 1, content="x"))
    _, call = _run(w.update_article, "update_article", 7, 1, content="x", format="html", keywords=["a"])
    assert call.args[0]["expected_revision"] == 1 and call.args[0]["keywords"] == ["a"]
    assert "title" not in call.args[0]


def test_operation_and_api_error():
    _, call = _run(w.get_mcp_operation, "mcp_operation", 11)
    assert call.args == (11,)
    client = MagicMock()
    client.mcp_operation.side_effect = APIError("stage_disabled", status_code=403)
    with patch("visiblyai_mcp.tools.content_write_tools._require_key", return_value=client):
        assert json.loads(w.get_mcp_operation(11))["error"] == "stage_disabled"


def test_remember_validates_and_maps_payload():
    assert "error" in json.loads(w.remember(""))
    assert "error" in json.loads(w.remember("x", scope="global"))
    assert "error" in json.loads(w.remember("x", scope="project"))
    out, call = _run(w.remember, "remember", "JACKS: Kernkundin 45+", scope="project", project_id=12)
    payload = call.args[0]
    assert payload == {"content": "JACKS: Kernkundin 45+", "scope": "project", "project_id": 12,
                       "idempotency_key": payload["idempotency_key"]}
    assert len(payload["idempotency_key"]) == 32 and out["idempotency_key"] == payload["idempotency_key"]
    _, call = _run(w.remember, "remember", "kontoweit", scope="account", idempotency_key="abc")
    assert call.args[0] == {"content": "kontoweit", "scope": "account", "idempotency_key": "abc"}

def test_import_meeting_preview_validates_and_maps_payload():
    assert "error" in json.loads(w.import_meeting_preview(0, "x" * 300))
    assert "error" in json.loads(w.import_meeting_preview(5, "zu kurz"))
    assert "error" in json.loads(w.import_meeting_preview(5, "x" * 60_001))
    _, call = _run(w.import_meeting_preview, "import_meeting_preview", 5, "  " + "x" * 300 + "  ", source="Call 11.9.")
    assert call.args[0] == {"project_id": 5, "text": "x" * 300, "source": "Call 11.9."}
    _, call = _run(w.import_meeting_preview, "import_meeting_preview", 5, "y" * 200)
    assert "source" not in call.args[0]

def test_import_meeting_apply_validates_and_generates_key():
    assert "error" in json.loads(w.import_meeting_apply(5, "Call"))
    assert "error" in json.loads(w.import_meeting_apply(5, "", facts=[{"content": "x"}]))
    assert "error" in json.loads(w.import_meeting_apply(5, "Call", rules=[{"rule_type": "excluded_term", "term": "x"}]))
    assert "error" in json.loads(w.import_meeting_apply(5, "Call", facts=[{"content": " "}]))
    fact = {"content": "Produziert in Berlin.", "category": "marke", "entities": [{"name": "Berlin", "type": "ort"}]}
    out, call = _run(w.import_meeting_apply, "import_meeting_apply", 5, "Call", facts=[fact],
                     rules=[{"rule_type": "tone", "note": "Per Du."}], brand_profile={"usps": ["A"]})
    payload = call.args[0]
    assert payload["facts"] == [fact] and payload["personas"] == [] and payload["brand_profile"] == {"usps": ["A"]}
    assert len(payload["idempotency_key"]) == 32 and out["idempotency_key"] == payload["idempotency_key"]
    _, call = _run(w.import_meeting_apply, "import_meeting_apply", 5, "Call", facts=[fact], idempotency_key="k1")
    assert call.args[0]["idempotency_key"] == "k1"
