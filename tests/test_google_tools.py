"""Unit tests for Google & Project MCP tools (mocked API)."""

import json
import pytest
from unittest.mock import patch, MagicMock

from visiblyai_mcp.tools import paid_tools
from visiblyai_mcp.api_client import APIError


def _parse(result: str) -> dict:
    return json.loads(result)


def _mock_client_with(method_name, return_value=None, side_effect=None):
    mock_client = MagicMock()
    method = getattr(mock_client, method_name)
    if side_effect:
        method.side_effect = side_effect
    else:
        method.return_value = return_value
    return mock_client


class TestListProjects:
    def test_success(self, mock_api_key, sample_projects_response):
        mock_client = _mock_client_with("list_projects", sample_projects_response)
        with patch("visiblyai_mcp.tools.paid_tools._require_key", return_value=mock_client):
            data = _parse(paid_tools.list_projects())
            assert len(data["data"]) == 2
            assert data["credits_used"] == 0

    def test_no_api_key(self, no_api_key):
        data = _parse(paid_tools.list_projects())
        assert "error" in data


class TestGetProject:
    def test_success(self, mock_api_key, sample_project_response):
        mock_client = _mock_client_with("get_project", sample_project_response)
        with patch("visiblyai_mcp.tools.paid_tools._require_key", return_value=mock_client):
            data = _parse(paid_tools.get_project(1))
            assert data["data"]["domain"] == "example.com"
            assert data["data"]["gsc_connected"] is True

    def test_missing_project_id(self, mock_api_key):
        data = _parse(paid_tools.get_project(0))
        assert "error" in data

    def test_no_api_key(self, no_api_key):
        data = _parse(paid_tools.get_project(1))
        assert "error" in data


class TestGetGoogleConnections:
    def test_success(self, mock_api_key, sample_google_connections_response):
        mock_client = _mock_client_with("get_google_connections", sample_google_connections_response)
        with patch("visiblyai_mcp.tools.paid_tools._require_key", return_value=mock_client):
            data = _parse(paid_tools.get_google_connections())
            assert "sc-domain:example.com" in data["data"]["gsc_properties"]

    def test_no_api_key(self, no_api_key):
        data = _parse(paid_tools.get_google_connections())
        assert "error" in data


class TestQuerySearchConsole:
    def test_success(self, mock_api_key, sample_gsc_response):
        mock_client = _mock_client_with("query_search_console", sample_gsc_response)
        with patch("visiblyai_mcp.tools.paid_tools._require_key", return_value=mock_client):
            data = _parse(paid_tools.query_search_console())
            assert data["data"][0]["query"] == "seo tools"
            assert data["credits_used"] == 0

    def test_custom_params(self, mock_api_key, sample_gsc_response):
        mock_client = _mock_client_with("query_search_console", sample_gsc_response)
        with patch("visiblyai_mcp.tools.paid_tools._require_key", return_value=mock_client):
            paid_tools.query_search_console(
                gsc_property="sc-domain:example.com",
                dimension="page", days=90, limit=50,
                country="DEU", device="mobile",
            )
            mock_client.query_search_console.assert_called_once_with(
                gsc_property="sc-domain:example.com",
                dimension="page", days=90, limit=50,
                country="DEU", device="mobile",
            )

    def test_days_clamped_max(self, mock_api_key, sample_gsc_response):
        mock_client = _mock_client_with("query_search_console", sample_gsc_response)
        with patch("visiblyai_mcp.tools.paid_tools._require_key", return_value=mock_client):
            paid_tools.query_search_console(days=999)
            _, kwargs = mock_client.query_search_console.call_args
            assert kwargs["days"] == 365

    def test_days_clamped_min(self, mock_api_key, sample_gsc_response):
        mock_client = _mock_client_with("query_search_console", sample_gsc_response)
        with patch("visiblyai_mcp.tools.paid_tools._require_key", return_value=mock_client):
            paid_tools.query_search_console(days=-5)
            _, kwargs = mock_client.query_search_console.call_args
            assert kwargs["days"] == 1

    def test_limit_clamped_max(self, mock_api_key, sample_gsc_response):
        mock_client = _mock_client_with("query_search_console", sample_gsc_response)
        with patch("visiblyai_mcp.tools.paid_tools._require_key", return_value=mock_client):
            paid_tools.query_search_console(limit=5000)
            _, kwargs = mock_client.query_search_console.call_args
            assert kwargs["limit"] == 1000

    def test_no_api_key(self, no_api_key):
        data = _parse(paid_tools.query_search_console())
        assert "error" in data


class TestQueryAnalytics:
    def test_success(self, mock_api_key, sample_ga4_response):
        mock_client = _mock_client_with("query_analytics", sample_ga4_response)
        with patch("visiblyai_mcp.tools.paid_tools._require_key", return_value=mock_client):
            data = _parse(paid_tools.query_analytics())
            assert data["data"]["total_sessions"] == 12500

    def test_custom_params(self, mock_api_key, sample_ga4_response):
        mock_client = _mock_client_with("query_analytics", sample_ga4_response)
        with patch("visiblyai_mcp.tools.paid_tools._require_key", return_value=mock_client):
            paid_tools.query_analytics(
                ga4_property="properties/123",
                report_type="top_pages", days=60, limit=50,
            )
            mock_client.query_analytics.assert_called_once_with(
                ga4_property="properties/123",
                report_type="top_pages", days=60, limit=50,
            )

    def test_days_clamped(self, mock_api_key, sample_ga4_response):
        mock_client = _mock_client_with("query_analytics", sample_ga4_response)
        with patch("visiblyai_mcp.tools.paid_tools._require_key", return_value=mock_client):
            paid_tools.query_analytics(days=999)
            _, kwargs = mock_client.query_analytics.call_args
            assert kwargs["days"] == 365

    def test_limit_clamped(self, mock_api_key, sample_ga4_response):
        mock_client = _mock_client_with("query_analytics", sample_ga4_response)
        with patch("visiblyai_mcp.tools.paid_tools._require_key", return_value=mock_client):
            paid_tools.query_analytics(limit=1000)
            _, kwargs = mock_client.query_analytics.call_args
            assert kwargs["limit"] == 500

    def test_no_api_key(self, no_api_key):
        data = _parse(paid_tools.query_analytics())
        assert "error" in data
