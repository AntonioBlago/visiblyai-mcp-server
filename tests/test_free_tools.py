"""Tests for free MCP tools."""

import json
import pytest
from unittest.mock import patch, MagicMock
from visiblyai_mcp.tools.free_tools import (
    classify_keywords,
    seo_checklist,
    seo_guidance,
    analyze_url_structure,
    list_locations,
)


class TestClassifyKeywords:
    def test_basic_classification(self):
        result = json.loads(classify_keywords(["seo tool kaufen"]))
        assert result["total"] == 1
        assert result["results"][0]["intent"] == "transactional"

    def test_multiple_keywords(self):
        result = json.loads(classify_keywords(["seo kaufen", "was ist seo", "seo berlin"]))
        assert result["total"] == 3

    def test_with_brand_config(self):
        result = json.loads(classify_keywords(
            keywords=["visibly seo tool"],
            brand_name="visibly",
        ))
        assert result["results"][0]["brand_type"] == "brand"

    def test_empty_keywords(self):
        result = json.loads(classify_keywords([]))
        assert "error" in result

    def test_german_keywords(self):
        result = json.loads(classify_keywords(["beste seo agentur münchen"]))
        assert result["total"] == 1
        r = result["results"][0]
        assert r["intent"] in ["commercial", "local"]


class TestSeoChecklist:
    """Tests for seo_checklist - now fetches from API."""

    def _mock_response(self, content, status=200):
        mock_resp = MagicMock()
        mock_resp.status_code = status
        mock_resp.json.return_value = {"success": True, "data": content}
        return mock_resp

    @patch("visiblyai_mcp.knowledge.checklists.httpx")
    def test_general_checklist(self, mock_httpx):
        mock_httpx.get.return_value = self._mock_response("# General SEO Checklist\n- [ ] Check robots.txt")
        result = seo_checklist("general", "en")
        assert "General SEO Checklist" in result
        mock_httpx.get.assert_called_once()

    @patch("visiblyai_mcp.knowledge.checklists.httpx")
    def test_blog_checklist(self, mock_httpx):
        mock_httpx.get.return_value = self._mock_response("# Blog Article SEO Checklist")
        result = seo_checklist("blog", "en")
        assert "Blog" in result

    @patch("visiblyai_mcp.knowledge.checklists.httpx")
    def test_german_language(self, mock_httpx):
        mock_httpx.get.return_value = self._mock_response("# Allgemeine SEO Checkliste")
        result = seo_checklist("general", "de")
        assert "Allgemeine" in result

    @patch("visiblyai_mcp.knowledge.checklists.httpx")
    def test_api_failure_returns_message(self, mock_httpx):
        mock_resp = MagicMock()
        mock_resp.status_code = 500
        mock_httpx.get.return_value = mock_resp
        result = seo_checklist("general", "en")
        assert "Failed to fetch" in result

    @patch("visiblyai_mcp.knowledge.checklists.httpx")
    def test_network_error_returns_message(self, mock_httpx):
        mock_httpx.get.side_effect = Exception("Connection refused")
        result = seo_checklist("general", "en")
        assert "Could not fetch" in result


class TestSeoGuidance:
    """Tests for seo_guidance - now fetches from API."""

    def _mock_response(self, content, status=200):
        mock_resp = MagicMock()
        mock_resp.status_code = status
        mock_resp.json.return_value = {"success": True, "data": content}
        return mock_resp

    @patch("visiblyai_mcp.knowledge.seo_guidance.httpx")
    def test_title_tags(self, mock_httpx):
        mock_httpx.get.return_value = self._mock_response("# Title Tag Best Practices")
        result = seo_guidance("title_tags")
        assert "Title Tag" in result

    @patch("visiblyai_mcp.knowledge.seo_guidance.httpx")
    def test_list_topics(self, mock_httpx):
        mock_httpx.get.return_value = self._mock_response([
            {"topic": "title_tags", "title": "Title Tag Optimization"},
            {"topic": "eeat", "title": "E-E-A-T"},
        ])
        result = seo_guidance("list")
        assert "Available" in result
        assert "title_tags" in result

    @patch("visiblyai_mcp.knowledge.seo_guidance.httpx")
    def test_api_failure(self, mock_httpx):
        mock_resp = MagicMock()
        mock_resp.status_code = 500
        mock_httpx.get.return_value = mock_resp
        result = seo_guidance("eeat")
        assert "Failed to fetch" in result


class TestAnalyzeUrlStructure:
    def test_good_url(self):
        result = json.loads(analyze_url_structure("https://example.com/seo-guide"))
        assert result["score"] >= 70
        assert "Uses HTTPS" in result["positives"]

    def test_long_url(self):
        result = json.loads(analyze_url_structure(
            "https://example.com/" + "a" * 100
        ))
        assert any("too long" in i for i in result["issues"])

    def test_uppercase_url(self):
        result = json.loads(analyze_url_structure(
            "https://example.com/SEO-Guide"
        ))
        assert any("uppercase" in i.lower() for i in result["issues"])

    def test_underscore_url(self):
        result = json.loads(analyze_url_structure(
            "https://example.com/seo_guide"
        ))
        assert any("underscore" in i.lower() for i in result["issues"])

    def test_http_url(self):
        result = json.loads(analyze_url_structure("http://example.com/page"))
        assert any("HTTPS" in i for i in result["issues"])


class TestListLocations:
    def test_returns_locations(self):
        result = json.loads(list_locations())
        assert result["total"] >= 10
        names = [loc["location_name"] for loc in result["locations"]]
        assert "Germany" in names
        assert "United States" in names