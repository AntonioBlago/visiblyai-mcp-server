"""Integration tests for free tools (no credits consumed)."""

import json
import os
import pytest

from visiblyai_mcp.tools.free_tools import (
    classify_keywords, seo_checklist, seo_guidance,
    analyze_url_structure, get_account_info, list_locations,
)

pytestmark = pytest.mark.skipif(
    not os.environ.get("VISIBLYAI_API_KEY"),
    reason="VISIBLYAI_API_KEY not set",
)


class TestLiveClassifyKeywords:
    def test_german_keywords(self):
        result = json.loads(classify_keywords(["seo agentur berlin", "schuhe kaufen online"]))
        assert result["total"] == 2
        for r in result["results"]:
            assert "intent" in r
            assert "funnel_stage" in r
            assert "conversion_score" in r

    def test_english_keywords(self):
        result = json.loads(classify_keywords(["buy running shoes", "what is seo"]))
        assert result["total"] == 2


class TestLiveSeoChecklist:
    @pytest.mark.parametrize("ctype", ["general", "blog", "ecommerce", "discover", "backlink"])
    def test_checklist_types(self, ctype):
        result = seo_checklist(ctype, "en")
        assert len(result) > 100
        assert "- [" in result  # Contains checkbox items

    def test_german_checklist(self):
        result = seo_checklist("general", "de")
        assert len(result) > 100


class TestLiveSeoGuidance:
    @pytest.mark.parametrize("topic", [
        "title_tags", "meta_descriptions", "heading_structure",
        "internal_linking", "core_web_vitals", "eeat",
    ])
    def test_guidance_topics(self, topic):
        result = seo_guidance(topic)
        assert len(result) > 50

    def test_list_topics(self):
        result = seo_guidance("list")
        assert "title_tags" in result


class TestLiveAnalyzeUrl:
    def test_good_url(self):
        result = json.loads(analyze_url_structure("https://example.com/seo-guide"))
        assert "score" in result
        assert result["score"] >= 0

    def test_bad_url(self):
        result = json.loads(analyze_url_structure(
            "http://example.com/THIS_IS_A_VERY_LONG_URL/" + "segment/" * 10
        ))
        assert len(result["issues"]) > 0


class TestLiveAccountInfo:
    def test_returns_account_data(self):
        result = json.loads(get_account_info())
        assert "authenticated" in result


class TestLiveListLocations:
    def test_returns_locations(self):
        result = json.loads(list_locations())
        assert result["total"] >= 10
        names = [loc["location_name"] for loc in result["locations"]]
        assert "Germany" in names
