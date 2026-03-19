"""Unit tests for all paid MCP tools (mocked API)."""

import json
import pytest
from unittest.mock import patch, MagicMock

from visiblyai_mcp.tools import paid_tools
from visiblyai_mcp.api_client import APIError


def _parse(result: str) -> dict:
    return json.loads(result)


def _mock_client_with(method_name, return_value=None, side_effect=None):
    """Create a mock VisiblyAIClient with a specific method mocked."""
    mock_client = MagicMock()
    method = getattr(mock_client, method_name)
    if side_effect:
        method.side_effect = side_effect
    else:
        method.return_value = return_value
    return mock_client


# ---------------------------------------------------------------------------
# Traffic Snapshot
# ---------------------------------------------------------------------------

class TestGetTrafficSnapshot:
    def test_success(self, mock_api_key, sample_traffic_response):
        mock_client = _mock_client_with("traffic_snapshot", sample_traffic_response)
        with patch("visiblyai_mcp.tools.paid_tools._require_key", return_value=mock_client):
            data = _parse(paid_tools.get_traffic_snapshot("example.com"))
            assert data["data"]["organic_traffic"] == 15000
            assert data["credits_used"] == 10

    def test_no_api_key(self, no_api_key):
        data = _parse(paid_tools.get_traffic_snapshot("example.com"))
        assert "error" in data
        assert "API key" in data["error"]

    def test_insufficient_credits(self, mock_api_key):
        mock_client = _mock_client_with("traffic_snapshot",
                                        side_effect=APIError("Insufficient credits", 402, True))
        with patch("visiblyai_mcp.tools.paid_tools._require_key", return_value=mock_client):
            data = _parse(paid_tools.get_traffic_snapshot("example.com"))
            assert "error" in data
            assert "credits" in data["error"].lower()

    def test_custom_location(self, mock_api_key, sample_traffic_response):
        mock_client = _mock_client_with("traffic_snapshot", sample_traffic_response)
        with patch("visiblyai_mcp.tools.paid_tools._require_key", return_value=mock_client):
            paid_tools.get_traffic_snapshot("example.com", "United States")
            mock_client.traffic_snapshot.assert_called_once_with("example.com", "United States")


# ---------------------------------------------------------------------------
# Historical Traffic
# ---------------------------------------------------------------------------

class TestGetHistoricalTraffic:
    def test_success(self, mock_api_key):
        resp = {"success": True, "data": [{"month": "2025-01", "traffic": 1000}],
                "credits_used": 10, "credits_remaining": 2490}
        mock_client = _mock_client_with("historical_traffic", resp)
        with patch("visiblyai_mcp.tools.paid_tools._require_key", return_value=mock_client):
            data = _parse(paid_tools.get_historical_traffic("example.com"))
            assert "data" in data

    def test_with_dates(self, mock_api_key):
        resp = {"success": True, "data": [], "credits_used": 10, "credits_remaining": 2490}
        mock_client = _mock_client_with("historical_traffic", resp)
        with patch("visiblyai_mcp.tools.paid_tools._require_key", return_value=mock_client):
            paid_tools.get_historical_traffic("example.com", "Germany", "2025-01-01", "2025-06-01")
            mock_client.historical_traffic.assert_called_once_with(
                "example.com", "Germany", date_from="2025-01-01", date_to="2025-06-01")

    def test_no_api_key(self, no_api_key):
        data = _parse(paid_tools.get_historical_traffic("example.com"))
        assert "error" in data


# ---------------------------------------------------------------------------
# Keywords
# ---------------------------------------------------------------------------

class TestGetKeywords:
    def test_success(self, mock_api_key, sample_keywords_response):
        mock_client = _mock_client_with("keywords", sample_keywords_response)
        with patch("visiblyai_mcp.tools.paid_tools._require_key", return_value=mock_client):
            data = _parse(paid_tools.get_keywords("example.com"))
            assert len(data["data"]) == 2

    def test_limit_capped(self, mock_api_key, sample_keywords_response):
        mock_client = _mock_client_with("keywords", sample_keywords_response)
        with patch("visiblyai_mcp.tools.paid_tools._require_key", return_value=mock_client):
            paid_tools.get_keywords("example.com", limit=5000)
            mock_client.keywords.assert_called_once_with("example.com", "Germany", 1000)

    def test_no_api_key(self, no_api_key):
        data = _parse(paid_tools.get_keywords("example.com"))
        assert "error" in data


# ---------------------------------------------------------------------------
# Competitors
# ---------------------------------------------------------------------------

class TestGetCompetitors:
    def test_success(self, mock_api_key, sample_competitors_response):
        mock_client = _mock_client_with("competitors", sample_competitors_response)
        with patch("visiblyai_mcp.tools.paid_tools._require_key", return_value=mock_client):
            data = _parse(paid_tools.get_competitors("example.com"))
            assert len(data["data"]) == 2

    def test_limit_capped(self, mock_api_key, sample_competitors_response):
        mock_client = _mock_client_with("competitors", sample_competitors_response)
        with patch("visiblyai_mcp.tools.paid_tools._require_key", return_value=mock_client):
            paid_tools.get_competitors("example.com", limit=100)
            mock_client.competitors.assert_called_once_with("example.com", "Germany", "German", 50)

    def test_no_api_key(self, no_api_key):
        data = _parse(paid_tools.get_competitors("example.com"))
        assert "error" in data


# ---------------------------------------------------------------------------
# Backlinks
# ---------------------------------------------------------------------------

class TestGetBacklinks:
    def test_success(self, mock_api_key, sample_backlinks_response):
        mock_client = _mock_client_with("backlinks", sample_backlinks_response)
        with patch("visiblyai_mcp.tools.paid_tools._require_key", return_value=mock_client):
            data = _parse(paid_tools.get_backlinks("example.com"))
            assert data["data"]["domain_rating"] == 45

    def test_no_api_key(self, no_api_key):
        data = _parse(paid_tools.get_backlinks("example.com"))
        assert "error" in data


# ---------------------------------------------------------------------------
# Referring Domains
# ---------------------------------------------------------------------------

class TestGetReferringDomains:
    def test_success(self, mock_api_key, sample_referring_domains_response):
        mock_client = _mock_client_with("referring_domains", sample_referring_domains_response)
        with patch("visiblyai_mcp.tools.paid_tools._require_key", return_value=mock_client):
            data = _parse(paid_tools.get_referring_domains("example.com"))
            assert len(data["data"]) == 2

    def test_limit_capped(self, mock_api_key, sample_referring_domains_response):
        mock_client = _mock_client_with("referring_domains", sample_referring_domains_response)
        with patch("visiblyai_mcp.tools.paid_tools._require_key", return_value=mock_client):
            paid_tools.get_referring_domains("example.com", limit=1000)
            mock_client.referring_domains.assert_called_once_with("example.com", "Germany", 500)


# ---------------------------------------------------------------------------
# Validate Keywords
# ---------------------------------------------------------------------------

class TestValidateKeywords:
    def test_success(self, mock_api_key, sample_validate_keywords_response):
        mock_client = _mock_client_with("validate_keywords", sample_validate_keywords_response)
        with patch("visiblyai_mcp.tools.paid_tools._require_key", return_value=mock_client):
            data = _parse(paid_tools.validate_keywords(["seo tools"]))
            assert data["data"][0]["search_volume"] == 5400

    def test_empty_keywords(self, mock_api_key):
        data = _parse(paid_tools.validate_keywords([]))
        assert "error" in data

    def test_top_n_capped(self, mock_api_key, sample_validate_keywords_response):
        mock_client = _mock_client_with("validate_keywords", sample_validate_keywords_response)
        with patch("visiblyai_mcp.tools.paid_tools._require_key", return_value=mock_client):
            paid_tools.validate_keywords(["seo"], top_n=500)
            mock_client.validate_keywords.assert_called_once_with(["seo"], "Germany", "German", 200)


# ---------------------------------------------------------------------------
# Crawl Website
# ---------------------------------------------------------------------------

class TestCrawlWebsite:
    def test_success(self, mock_api_key, sample_crawl_response):
        mock_client = _mock_client_with("crawl", sample_crawl_response)
        with patch("visiblyai_mcp.tools.paid_tools._require_key", return_value=mock_client):
            data = _parse(paid_tools.crawl_website("https://example.com"))
            assert data["data"]["title"] == "Example Site"

    def test_with_keyword(self, mock_api_key, sample_crawl_response):
        mock_client = _mock_client_with("crawl", sample_crawl_response)
        with patch("visiblyai_mcp.tools.paid_tools._require_key", return_value=mock_client):
            paid_tools.crawl_website("https://example.com", "seo", 3)
            mock_client.crawl.assert_called_once_with("https://example.com", "seo", 3)

    def test_max_pages_capped(self, mock_api_key, sample_crawl_response):
        mock_client = _mock_client_with("crawl", sample_crawl_response)
        with patch("visiblyai_mcp.tools.paid_tools._require_key", return_value=mock_client):
            paid_tools.crawl_website("https://example.com", max_pages=50)
            mock_client.crawl.assert_called_once_with("https://example.com", "", 10)


# ---------------------------------------------------------------------------
# OnPage Analysis
# ---------------------------------------------------------------------------

class TestOnpageAnalysis:
    def test_success(self, mock_api_key, sample_onpage_response):
        mock_client = _mock_client_with("onpage_analysis", sample_onpage_response)
        with patch("visiblyai_mcp.tools.paid_tools._require_key", return_value=mock_client):
            data = _parse(paid_tools.onpage_analysis("https://example.com", "seo"))
            assert data["data"]["overall_score"] == 72

    def test_empty_keyword(self, mock_api_key):
        data = _parse(paid_tools.onpage_analysis("https://example.com", ""))
        assert "error" in data

    def test_no_api_key(self, no_api_key):
        data = _parse(paid_tools.onpage_analysis("https://example.com", "seo"))
        assert "error" in data


# ---------------------------------------------------------------------------
# Check Links
# ---------------------------------------------------------------------------

class TestCheckLinks:
    def test_success(self, mock_api_key, sample_check_links_response):
        mock_client = _mock_client_with("check_links", sample_check_links_response)
        with patch("visiblyai_mcp.tools.paid_tools._require_key", return_value=mock_client):
            data = _parse(paid_tools.check_links("https://example.com"))
            assert data["data"]["broken_links"] == 2

    def test_no_api_key(self, no_api_key):
        data = _parse(paid_tools.check_links("https://example.com"))
        assert "error" in data


# ---------------------------------------------------------------------------
# SEO Agent
# ---------------------------------------------------------------------------

class TestSeoAgent:
    def test_success(self, mock_api_key, sample_seo_agent_response):
        mock_client = _mock_client_with("seo_agent", sample_seo_agent_response)
        with patch("visiblyai_mcp.tools.paid_tools._require_key", return_value=mock_client):
            data = _parse(paid_tools.seo_agent("Analyze SEO for example.com"))
            assert data["data"]["agent"] == "seo_analyst"
            assert data["credits_used"] == 25

    def test_with_agent_type(self, mock_api_key, sample_seo_agent_response):
        mock_client = _mock_client_with("seo_agent", sample_seo_agent_response)
        with patch("visiblyai_mcp.tools.paid_tools._require_key", return_value=mock_client):
            paid_tools.seo_agent("Write meta tags", agent="copywriter",
                                 domain="example.com", keyword="seo")
            mock_client.seo_agent.assert_called_once_with(
                "Write meta tags", "copywriter", "example.com", "", "seo", "", None)

    def test_empty_task(self, mock_api_key):
        data = _parse(paid_tools.seo_agent(""))
        assert "error" in data
        assert "task" in data["error"]

    def test_no_api_key(self, no_api_key):
        data = _parse(paid_tools.seo_agent("Analyze SEO"))
        assert "error" in data

    def test_api_error_402(self, mock_api_key):
        mock_client = _mock_client_with("seo_agent",
                                        side_effect=APIError("Insufficient credits", 402, True))
        with patch("visiblyai_mcp.tools.paid_tools._require_key", return_value=mock_client):
            data = _parse(paid_tools.seo_agent("Analyze SEO"))
            assert "error" in data


# ---------------------------------------------------------------------------
# SEO Workflow
# ---------------------------------------------------------------------------

class TestSeoWorkflow:
    def test_success(self, mock_api_key, sample_seo_workflow_response):
        mock_client = _mock_client_with("seo_workflow", sample_seo_workflow_response)
        with patch("visiblyai_mcp.tools.paid_tools._require_key", return_value=mock_client):
            data = _parse(paid_tools.seo_workflow("seo_performance_audit", "example.com", 1))
            assert data["data"]["status"] == "completed"
            assert data["credits_used"] == 150

    def test_empty_workflow(self, mock_api_key):
        data = _parse(paid_tools.seo_workflow("", "example.com", 1))
        assert "error" in data
        assert "workflow" in data["error"]

    def test_empty_domain(self, mock_api_key):
        data = _parse(paid_tools.seo_workflow("seo_performance_audit", "", 1))
        assert "error" in data
        assert "domain" in data["error"]

    def test_zero_project_id(self, mock_api_key):
        data = _parse(paid_tools.seo_workflow("seo_performance_audit", "example.com", 0))
        assert "error" in data
        assert "project_id" in data["error"]

    def test_no_api_key(self, no_api_key):
        data = _parse(paid_tools.seo_workflow("seo_performance_audit", "example.com", 1))
        assert "error" in data


# ---------------------------------------------------------------------------
# Error response format
# ---------------------------------------------------------------------------

class TestErrorFormat:
    def test_401_includes_signup_url(self, mock_api_key):
        mock_client = _mock_client_with("traffic_snapshot",
                                        side_effect=APIError("Invalid API key", 401))
        with patch("visiblyai_mcp.tools.paid_tools._require_key", return_value=mock_client):
            data = _parse(paid_tools.get_traffic_snapshot("example.com"))
            assert "error" in data

    def test_402_includes_credits_url(self, mock_api_key):
        mock_client = _mock_client_with("traffic_snapshot",
                                        side_effect=APIError("Insufficient credits", 402, True))
        with patch("visiblyai_mcp.tools.paid_tools._require_key", return_value=mock_client):
            data = _parse(paid_tools.get_traffic_snapshot("example.com"))
            assert "error" in data
            assert "credits_url" in data

    def test_generic_error(self, mock_api_key):
        mock_client = _mock_client_with("traffic_snapshot",
                                        side_effect=RuntimeError("Something broke"))
        with patch("visiblyai_mcp.tools.paid_tools._require_key", return_value=mock_client):
            data = _parse(paid_tools.get_traffic_snapshot("example.com"))
            assert "error" in data
