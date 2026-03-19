"""Shared test fixtures for visiblyai-mcp-server."""

import json
import pytest
from unittest.mock import patch, MagicMock


# ---------------------------------------------------------------------------
# Sample API responses matching real backend shapes
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_traffic_response():
    return {
        "success": True,
        "data": {
            "domain": "example.com",
            "organic_traffic": 15000,
            "paid_traffic": 2000,
            "organic_keywords": 850,
            "organic_cost": 12500.0,
        },
        "credits_used": 10,
        "credits_remaining": 2490,
    }


@pytest.fixture
def sample_keywords_response():
    return {
        "success": True,
        "data": [
            {"keyword": "seo tools", "position": 3, "search_volume": 5400,
             "url": "https://example.com/tools", "traffic_share": 12.5},
            {"keyword": "seo audit", "position": 7, "search_volume": 3200,
             "url": "https://example.com/audit", "traffic_share": 5.2},
        ],
        "credits_used": 15,
        "credits_remaining": 2475,
    }


@pytest.fixture
def sample_competitors_response():
    return {
        "success": True,
        "data": [
            {"domain": "competitor1.com", "common_keywords": 120, "organic_traffic": 25000},
            {"domain": "competitor2.com", "common_keywords": 85, "organic_traffic": 18000},
        ],
        "credits_used": 20,
        "credits_remaining": 2455,
    }


@pytest.fixture
def sample_backlinks_response():
    return {
        "success": True,
        "data": {
            "domain_rating": 45,
            "total_backlinks": 1250,
            "referring_domains": 180,
            "dofollow_links": 950,
            "nofollow_links": 300,
        },
        "credits_used": 15,
        "credits_remaining": 2440,
    }


@pytest.fixture
def sample_referring_domains_response():
    return {
        "success": True,
        "data": [
            {"domain": "referrer1.com", "authority": 65, "backlinks": 15},
            {"domain": "referrer2.com", "authority": 42, "backlinks": 8},
        ],
        "credits_used": 10,
        "credits_remaining": 2430,
    }


@pytest.fixture
def sample_validate_keywords_response():
    return {
        "success": True,
        "data": [
            {"keyword": "seo tools", "search_volume": 5400, "competition": 0.65,
             "cpc": 3.20, "keyword_difficulty": 58},
        ],
        "credits_used": 5,
        "credits_remaining": 2425,
    }


@pytest.fixture
def sample_crawl_response():
    return {
        "success": True,
        "data": {
            "url": "https://example.com",
            "title": "Example Site",
            "meta_description": "An example website",
            "h1": ["Welcome"],
            "h2": ["About", "Services"],
            "word_count": 1500,
            "internal_links": 25,
            "external_links": 8,
            "images": 12,
        },
        "credits_used": 15,
        "credits_remaining": 2410,
    }


@pytest.fixture
def sample_onpage_response():
    return {
        "success": True,
        "data": {
            "overall_score": 72,
            "keyword_score": 65,
            "content_score": 78,
            "technical_score": 73,
            "checks_passed": 16,
            "checks_failed": 5,
            "checks_warning": 3,
            "total_checks": 24,
            "recommendations": [{"type": "warning", "message": "Add keyword to H1"}],
        },
        "credits_used": 15,
        "credits_remaining": 2395,
    }


@pytest.fixture
def sample_check_links_response():
    return {
        "success": True,
        "data": {
            "total_links": 45,
            "broken_links": 2,
            "redirects": 5,
            "ok_links": 38,
            "links": [
                {"url": "https://example.com/page1", "status": 200, "type": "ok"},
                {"url": "https://example.com/missing", "status": 404, "type": "broken"},
            ],
        },
        "credits_used": 20,
        "credits_remaining": 2375,
    }


@pytest.fixture
def sample_seo_agent_response():
    return {
        "success": True,
        "data": {
            "agent": "seo_analyst",
            "task": "Analyze SEO for example.com",
            "result": "Domain has 850 organic keywords...",
            "recommendations": ["Improve title tags", "Add internal links"],
        },
        "credits_used": 25,
        "credits_remaining": 2350,
    }


@pytest.fixture
def sample_seo_workflow_response():
    return {
        "success": True,
        "data": {
            "workflow": "seo_performance_audit",
            "status": "completed",
            "steps_completed": 5,
            "report_url": "https://antonioblago.com/reports/123",
            "summary": "SEO Performance Audit completed for example.com",
        },
        "credits_used": 150,
        "credits_remaining": 2200,
    }


@pytest.fixture
def sample_projects_response():
    return {
        "success": True,
        "data": [
            {"id": 1, "name": "Example Project", "domain": "example.com", "score": 85},
            {"id": 2, "name": "Test Project", "domain": "test.com", "score": 72},
        ],
        "credits_used": 0,
        "credits_remaining": 2200,
    }


@pytest.fixture
def sample_project_response():
    return {
        "success": True,
        "data": {
            "id": 1, "name": "Example Project", "domain": "example.com",
            "competitors": ["competitor1.com"],
            "gsc_connected": True, "ga4_connected": False,
        },
        "credits_used": 0,
        "credits_remaining": 2200,
    }


@pytest.fixture
def sample_google_connections_response():
    return {
        "success": True,
        "data": {
            "gsc_properties": ["sc-domain:example.com"],
            "ga4_properties": ["properties/123456"],
            "pairings": [{"gsc": "sc-domain:example.com", "ga4": "properties/123456"}],
        },
        "credits_used": 0,
        "credits_remaining": 2200,
    }


@pytest.fixture
def sample_gsc_response():
    return {
        "success": True,
        "data": [
            {"query": "seo tools", "clicks": 150, "impressions": 5000,
             "ctr": 0.03, "position": 8.5},
        ],
        "credits_used": 0,
        "credits_remaining": 2200,
    }


@pytest.fixture
def sample_ga4_response():
    return {
        "success": True,
        "data": {
            "total_sessions": 12500,
            "total_users": 8900,
            "total_pageviews": 35000,
        },
        "credits_used": 0,
        "credits_remaining": 2200,
    }


@pytest.fixture
def mock_api_key():
    """Mock the API key to be present."""
    with patch("visiblyai_mcp.config.get_api_key", return_value="lc_test_key_123"):
        yield "lc_test_key_123"


@pytest.fixture
def no_api_key():
    """Mock the API key to be absent."""
    with patch("visiblyai_mcp.config.get_api_key", return_value=None):
        yield
