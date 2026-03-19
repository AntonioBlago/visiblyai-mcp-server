"""Unit tests for the VisiblyAI API client."""

import json
import pytest
from unittest.mock import patch, MagicMock

from visiblyai_mcp.api_client import VisiblyAIClient, APIError


class TestRequireKey:
    def test_raises_without_key(self):
        client = VisiblyAIClient(api_key=None)
        with pytest.raises(APIError, match="No API key set"):
            client._require_key()

    def test_passes_with_key(self):
        client = VisiblyAIClient(api_key="lc_test123")
        client._require_key()  # Should not raise


class TestHandleResponse:
    def _mock_response(self, status_code, json_data=None):
        resp = MagicMock()
        resp.status_code = status_code
        resp.json.return_value = json_data or {}
        return resp

    def test_200_success(self):
        client = VisiblyAIClient(api_key="lc_test")
        resp = self._mock_response(200, {"success": True, "data": {"key": "value"}})
        result = client._handle_response(resp)
        assert result["data"]["key"] == "value"

    def test_401_raises(self):
        client = VisiblyAIClient(api_key="lc_test")
        resp = self._mock_response(401)
        with pytest.raises(APIError) as exc_info:
            client._handle_response(resp)
        assert exc_info.value.status_code == 401

    def test_402_raises_with_credits_hint(self):
        client = VisiblyAIClient(api_key="lc_test")
        resp = self._mock_response(402)
        with pytest.raises(APIError) as exc_info:
            client._handle_response(resp)
        assert exc_info.value.status_code == 402
        assert exc_info.value.credits_hint is True

    def test_429_raises(self):
        client = VisiblyAIClient(api_key="lc_test")
        resp = self._mock_response(429)
        with pytest.raises(APIError, match="Rate limit"):
            client._handle_response(resp)

    def test_500_raises(self):
        client = VisiblyAIClient(api_key="lc_test")
        resp = self._mock_response(500)
        with pytest.raises(APIError, match="Server error"):
            client._handle_response(resp)

    def test_success_false_raises(self):
        client = VisiblyAIClient(api_key="lc_test")
        resp = self._mock_response(200, {"success": False, "error": "Bad request"})
        with pytest.raises(APIError, match="Bad request"):
            client._handle_response(resp)


class TestClientLifecycle:
    def test_ensure_client_creates_once(self):
        client = VisiblyAIClient(api_key="lc_test")
        with patch("visiblyai_mcp.api_client.httpx.Client") as MockClient:
            mock_instance = MagicMock()
            mock_instance.is_closed = False
            MockClient.return_value = mock_instance

            c1 = client._ensure_client()
            c2 = client._ensure_client()
            assert c1 is c2
            MockClient.assert_called_once()

    def test_ensure_client_recreates_if_closed(self):
        client = VisiblyAIClient(api_key="lc_test")
        with patch("visiblyai_mcp.api_client.httpx.Client") as MockClient:
            mock1 = MagicMock()
            mock1.is_closed = False
            mock2 = MagicMock()
            mock2.is_closed = False
            MockClient.side_effect = [mock1, mock2]

            c1 = client._ensure_client()
            mock1.is_closed = True  # Simulate closed
            c2 = client._ensure_client()
            assert c1 is not c2
            assert MockClient.call_count == 2

    def test_close_closes_client(self):
        client = VisiblyAIClient(api_key="lc_test")
        mock_http = MagicMock()
        mock_http.is_closed = False
        client._client = mock_http
        client.close()
        mock_http.close.assert_called_once()

    def test_close_noop_without_client(self):
        client = VisiblyAIClient(api_key="lc_test")
        client.close()  # Should not raise


class TestClientMethods:
    """Verify each method calls the correct endpoint."""

    def _setup_client(self):
        client = VisiblyAIClient(api_key="lc_test")
        mock_http = MagicMock()
        mock_http.is_closed = False
        resp = MagicMock()
        resp.status_code = 200
        resp.json.return_value = {"success": True, "data": {}}
        mock_http.post.return_value = resp
        mock_http.get.return_value = resp
        client._client = mock_http
        return client, mock_http

    def test_traffic_snapshot_endpoint(self):
        client, mock = self._setup_client()
        client.traffic_snapshot("example.com")
        mock.post.assert_called_with("/tools/traffic-snapshot",
                                     json={"domain": "example.com", "location": "Germany"})

    def test_keywords_endpoint(self):
        client, mock = self._setup_client()
        client.keywords("example.com", "Germany", 100)
        mock.post.assert_called_with("/tools/keywords",
                                     json={"domain": "example.com", "location": "Germany", "limit": 100})

    def test_competitors_endpoint(self):
        client, mock = self._setup_client()
        client.competitors("example.com")
        mock.post.assert_called_with("/tools/competitors",
                                     json={"domain": "example.com", "location": "Germany",
                                           "language": "German", "limit": 10})

    def test_backlinks_endpoint(self):
        client, mock = self._setup_client()
        client.backlinks("example.com")
        mock.post.assert_called_with("/tools/backlinks",
                                     json={"domain": "example.com", "location": "Germany", "limit": 100})

    def test_crawl_endpoint(self):
        client, mock = self._setup_client()
        client.crawl("https://example.com", "seo", 3)
        mock.post.assert_called_with("/tools/crawl",
                                     json={"url": "https://example.com", "keyword": "seo", "max_pages": 3})

    def test_onpage_analysis_endpoint(self):
        client, mock = self._setup_client()
        client.onpage_analysis("https://example.com", "seo")
        mock.post.assert_called_with("/tools/onpage-analysis",
                                     json={"url": "https://example.com", "keyword": "seo"})

    def test_check_links_endpoint(self):
        client, mock = self._setup_client()
        client.check_links("https://example.com")
        mock.post.assert_called_with("/tools/check-links",
                                     json={"url": "https://example.com"})

    def test_seo_agent_endpoint(self):
        client, mock = self._setup_client()
        client.seo_agent("Analyze SEO", agent="seo_analyst", domain="example.com")
        mock.post.assert_called_with("/tools/seo-agent",
                                     json={"task": "Analyze SEO", "agent": "seo_analyst",
                                           "domain": "example.com"})

    def test_seo_agent_minimal(self):
        client, mock = self._setup_client()
        client.seo_agent("Analyze SEO")
        mock.post.assert_called_with("/tools/seo-agent",
                                     json={"task": "Analyze SEO"})

    def test_seo_workflow_endpoint(self):
        client, mock = self._setup_client()
        client.seo_workflow("seo_performance_audit", "example.com", 1)
        mock.post.assert_called_with("/tools/seo-workflow",
                                     json={"workflow": "seo_performance_audit",
                                           "domain": "example.com", "project_id": 1})

    def test_seo_workflow_with_params(self):
        client, mock = self._setup_client()
        client.seo_workflow("indexing_diagnosis", "example.com", 2,
                            params={"depth": "full"})
        mock.post.assert_called_with("/tools/seo-workflow",
                                     json={"workflow": "indexing_diagnosis",
                                           "domain": "example.com", "project_id": 2,
                                           "params": {"depth": "full"}})

    def test_list_projects_endpoint(self):
        client, mock = self._setup_client()
        client.list_projects()
        mock.post.assert_called_with("/tools/list-projects", json={})

    def test_query_search_console_endpoint(self):
        client, mock = self._setup_client()
        client.query_search_console(gsc_property="sc-domain:example.com",
                                    country="DEU", device="mobile")
        call_json = mock.post.call_args[1]["json"]
        assert call_json["gsc_property"] == "sc-domain:example.com"
        assert call_json["country"] == "DEU"
        assert call_json["device"] == "mobile"

    def test_classify_keywords_api_endpoint(self):
        client, mock = self._setup_client()
        client.classify_keywords_api(["seo tools"], "German", "Germany")
        mock.post.assert_called_with("/tools/classify-keywords",
                                     json={"keywords": ["seo tools"],
                                           "language": "German", "location": "Germany"})
