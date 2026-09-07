"""Project-data tools (read-only, 0 credits): argument mapping + error handling."""
import json
from unittest.mock import MagicMock, patch

from visiblyai_mcp.api_client import APIError
from visiblyai_mcp.tools import project_tools

OK = {"success": True, "data": {"items": []}, "credits_used": 0, "credits_remaining": None}


def _client(method: str, value=OK):
    client = MagicMock()
    getattr(client, method).return_value = value
    return client


def _run(fn, method, *args, **kwargs):
    client = _client(method)
    with patch("visiblyai_mcp.tools.project_tools._require_key", return_value=client):
        out = json.loads(fn(*args, **kwargs))
    return out, getattr(client, method).call_args


def test_gsc_clusters_maps_arguments():
    out, call = _run(project_tools.get_gsc_clusters, "gsc_clusters", 5, days=7, top_n=10, country="DEU")
    assert out["credits_used"] == 0 and out["data"] == {"items": []}
    assert call.args == (5,) and call.kwargs == {"days": 7, "top_n": 10, "country": "DEU"}


def test_cluster_keywords_requires_cluster_key():
    assert "error" in json.loads(project_tools.get_cluster_keywords(5, ""))
    _, call = _run(project_tools.get_cluster_keywords, "cluster_keywords", 5, "c1", limit=50, offset=10)
    assert call.args == (5, "c1") and call.kwargs["limit"] == 50 and call.kwargs["offset"] == 10


def test_get_article_defaults_to_no_content():
    _, call = _run(project_tools.get_article, "content_article", 9)
    assert call.kwargs["include_content"] is False and call.kwargs["content_offset"] == 0


def test_score_text_requires_content_and_valid_format():
    assert "error" in json.loads(project_tools.score_text(5, ""))
    assert "error" in json.loads(project_tools.score_text(5, "x", format="docx"))
    _, call = _run(project_tools.score_text, "score_text", 5, "# Hi", format="markdown", query_id=3)
    assert call.args == (5, "# Hi") and call.kwargs == {"format": "markdown", "query_id": 3, "persona_id": None}


def test_recall_without_query_lists():
    _, call = _run(project_tools.recall, "memory_recall")
    assert call.kwargs == {"query": "", "project_id": None, "limit": 10}


def test_api_error_is_reported_not_raised():
    client = MagicMock()
    client.scorecard.side_effect = APIError("Rate limited", status_code=429)
    with patch("visiblyai_mcp.tools.project_tools._require_key", return_value=client):
        out = json.loads(project_tools.get_scorecard(5))
    assert out["error"] == "Rate limited"


def test_403_detail_is_surfaced_in_wrapper_output():
    client = MagicMock()
    client.memory_recall.side_effect = APIError(
        "memory_disabled: Kundengraph ist fuer diesen Tarif nicht aktiv",
        status_code=403,
        detail={"error": "memory_disabled", "message": "Kundengraph ist fuer diesen Tarif nicht aktiv"},
    )
    with patch("visiblyai_mcp.tools.project_tools._require_key", return_value=client):
        out = json.loads(project_tools.recall())
    assert out["error"] == "memory_disabled: Kundengraph ist fuer diesen Tarif nicht aktiv"
    assert out["status_code"] == 403
    assert out["detail"] == {"error": "memory_disabled", "message": "Kundengraph ist fuer diesen Tarif nicht aktiv"}


def test_missing_key_hint():
    with patch("visiblyai_mcp.tools.project_tools.get_api_key", return_value=None):
        out = json.loads(project_tools.list_articles(5))
    assert "API key" in out["error"]
