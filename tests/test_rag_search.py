"""Tests for RAG search through the shared visibly-app API client."""

import importlib
from types import SimpleNamespace
from unittest.mock import MagicMock

from visiblyai_mcp.knowledge import rag_search


def _client(result=None, error=None):
    method = MagicMock(return_value=result or {"data": []})
    if error is not None:
        method.side_effect = error
    return SimpleNamespace(rag_search=method)


class TestSearchRagSuccess:
    def test_uses_shared_client_with_all_parameters(self):
        client = _client(
            {
                "data": [{"title": "T"}],
                "credits_used": 2,
                "credits_remaining": 8,
            }
        )

        result = rag_search.search_rag(
            client,
            "eeat",
            top_k=7,
            category="quality",
            document_type="guideline",
            include_external=False,
        )

        client.rag_search.assert_called_once_with(
            query="eeat",
            top_k=7,
            category="quality",
            document_type="guideline",
            include_external=False,
        )
        assert result == {
            "results": [{"title": "T"}],
            "credits_used": 2,
            "credits_remaining": 8,
        }

    def test_credits_used_defaults_to_two(self):
        result = rag_search.search_rag(_client({"data": []}), "q")
        assert result["credits_used"] == 2


class TestApiUrlOverride:
    def test_default_targets_visibly_app(self, monkeypatch):
        monkeypatch.delenv("VISIBLYAI_API_URL", raising=False)
        import visiblyai_mcp.config as config

        importlib.reload(config)
        assert config.BASE_URL == "https://visibly-ai.com/api/v1/mcp"

    def test_override_repoints_all_api_tools(self, monkeypatch):
        monkeypatch.setenv(
            "VISIBLYAI_API_URL", "https://staging.example/api/v1/mcp/"
        )
        import visiblyai_mcp.config as config

        try:
            importlib.reload(config)
            assert config.BASE_URL == "https://staging.example/api/v1/mcp"
        finally:
            monkeypatch.delenv("VISIBLYAI_API_URL", raising=False)
            importlib.reload(config)


class TestSearchRagErrors:
    def test_client_error_returns_error_dict(self):
        result = rag_search.search_rag(_client(error=RuntimeError("boom")), "q")
        assert result["results"] == []
        assert result["error"] == "boom"
