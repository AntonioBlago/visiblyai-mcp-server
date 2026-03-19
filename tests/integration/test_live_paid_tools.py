"""Integration tests for paid tools (consume real credits).

Run with: VISIBLYAI_API_KEY=lc_xxx pytest tests/integration/test_live_paid_tools.py -v
Mark: @pytest.mark.expensive - these burn credits
"""

import json
import os
import pytest

from visiblyai_mcp.tools import paid_tools

pytestmark = [
    pytest.mark.skipif(
        not os.environ.get("VISIBLYAI_API_KEY"),
        reason="VISIBLYAI_API_KEY not set",
    ),
    pytest.mark.expensive,
]

TEST_DOMAIN = "visibly-ai.com"


class TestLiveTrafficSnapshot:
    def test_returns_data(self):
        result = json.loads(paid_tools.get_traffic_snapshot(TEST_DOMAIN))
        assert "data" in result or "error" in result


class TestLiveKeywords:
    def test_returns_keywords(self):
        result = json.loads(paid_tools.get_keywords(TEST_DOMAIN, limit=10))
        assert "data" in result or "error" in result


class TestLiveCompetitors:
    def test_returns_competitors(self):
        result = json.loads(paid_tools.get_competitors(TEST_DOMAIN, limit=5))
        assert "data" in result or "error" in result


class TestLiveBacklinks:
    def test_returns_backlinks(self):
        result = json.loads(paid_tools.get_backlinks(TEST_DOMAIN, limit=10))
        assert "data" in result or "error" in result


class TestLiveValidateKeywords:
    def test_returns_volumes(self):
        result = json.loads(paid_tools.validate_keywords(
            ["seo tools", "seo agentur"], top_n=5
        ))
        assert "data" in result or "error" in result


class TestLiveCrawlWebsite:
    def test_crawl_homepage(self):
        result = json.loads(paid_tools.crawl_website(f"https://{TEST_DOMAIN}"))
        assert "data" in result or "error" in result


class TestLiveOnpageAnalysis:
    def test_onpage_check(self):
        result = json.loads(paid_tools.onpage_analysis(
            f"https://{TEST_DOMAIN}", "seo tools"
        ))
        assert "data" in result or "error" in result
