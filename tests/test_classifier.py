"""Tests for the standalone keyword classifier."""

import pytest
from visiblyai_mcp.classifier import (
    KeywordClassifier,
    ClassificationResult,
    IntentType,
    BrandType,
    FunnelStage,
    ConversionPotential,
    quick_classify,
    group_by_intent,
    group_by_funnel,
    filter_high_conversion,
    sort_by_conversion,
)


@pytest.fixture
def classifier():
    return KeywordClassifier()


@pytest.fixture
def brand_classifier():
    return KeywordClassifier(brand_config={
        "brand_name": "visiblyai",
        "brand_variations": ["visibly ai", "visibly-ai"],
        "product_keywords": ["seo tool", "mcp server"],
        "competitors": [{"name": "ahrefs"}, {"name": "semrush"}],
    })


class TestBasicClassification:
    def test_classify_returns_result(self, classifier):
        result = classifier.classify("seo tipps")
        assert isinstance(result, ClassificationResult)
        assert result.keyword == "seo tipps"

    def test_transactional_intent(self, classifier):
        result = classifier.classify("seo tool kaufen")
        assert result.intent.type == IntentType.TRANSACTIONAL
        assert result.funnel.stage == FunnelStage.BOFU

    def test_commercial_intent(self, classifier):
        result = classifier.classify("beste seo tools vergleich")
        assert result.intent.type == IntentType.COMMERCIAL

    def test_informational_intent(self, classifier):
        result = classifier.classify("was ist seo")
        assert result.intent.type == IntentType.INFORMATIONAL
        assert result.funnel.stage == FunnelStage.TOFU

    def test_local_intent(self, classifier):
        result = classifier.classify("seo agentur berlin")
        assert result.intent.type == IntentType.LOCAL

    def test_navigational_intent(self, classifier):
        result = classifier.classify("ahrefs login")
        assert result.intent.type == IntentType.NAVIGATIONAL

    def test_conversion_score_range(self, classifier):
        result = classifier.classify("seo tool kaufen")
        assert 0 <= result.conversion_score <= 100

    def test_invalid_keyword_raises(self, classifier):
        with pytest.raises(ValueError):
            classifier.classify("")

    def test_none_keyword_raises(self, classifier):
        with pytest.raises(ValueError):
            classifier.classify(None)

    def test_long_keyword_raises(self, classifier):
        with pytest.raises(ValueError):
            classifier.classify("x" * 501)


class TestBrandClassification:
    def test_brand_detected(self, brand_classifier):
        result = brand_classifier.classify("visiblyai seo")
        assert result.brand.type == BrandType.BRAND
        assert result.brand.matched_brand == "visiblyai"

    def test_brand_product_detected(self, brand_classifier):
        result = brand_classifier.classify("visiblyai mcp server")
        assert result.brand.type == BrandType.BRAND_PRODUCT
        assert result.brand.matched_product == "mcp server"

    def test_competitor_detected(self, brand_classifier):
        result = brand_classifier.classify("ahrefs backlink checker")
        assert result.brand.type == BrandType.COMPETITOR
        assert result.brand.matched_brand == "ahrefs"

    def test_generic_keyword(self, brand_classifier):
        result = brand_classifier.classify("how to improve rankings")
        assert result.brand.type == BrandType.GENERIC

    def test_no_brand_config(self, classifier):
        result = classifier.classify("seo tool")
        assert result.brand.type == BrandType.GENERIC


class TestModifiers:
    def test_year_detected(self, classifier):
        result = classifier.classify("seo trends 2026")
        assert result.modifiers.has_year is True

    def test_price_detected(self, classifier):
        result = classifier.classify("seo tool kostenlos")
        assert result.modifiers.has_price is True

    def test_question_detected(self, classifier):
        result = classifier.classify("was ist seo?")
        assert result.modifiers.has_question is True

    def test_comparison_detected(self, classifier):
        result = classifier.classify("ahrefs vs semrush")
        assert result.modifiers.has_comparison is True


class TestTopicClassification:
    def test_seo_topic(self, classifier):
        result = classifier.classify("keyword ranking verbessern")
        assert result.topic.primary_topic == "seo"

    def test_ecommerce_topic(self, classifier):
        result = classifier.classify("online shop erstellen")
        assert result.topic.primary_topic == "ecommerce"

    def test_health_topic(self, classifier):
        result = classifier.classify("fitness training ernährung")
        assert result.topic.primary_topic == "health"


class TestSerialization:
    def test_to_dict(self, classifier):
        result = classifier.classify("seo tipps")
        d = result.to_dict()
        assert "keyword" in d
        assert "intent" in d
        assert "brand" in d
        assert "funnel" in d
        assert "topic" in d

    def test_to_flat_dict(self, classifier):
        result = classifier.classify("seo tipps")
        d = result.to_flat_dict()
        assert "intent_type" in d
        assert "brand_type" in d
        assert "funnel_stage" in d
        assert "conversion_score" in d


class TestBatchAndHelpers:
    def test_classify_batch(self, classifier):
        results = classifier.classify_batch(["seo kaufen", "was ist seo", "seo berlin"])
        assert len(results) == 3

    def test_quick_classify(self):
        result = quick_classify("seo tool kaufen")
        assert isinstance(result, ClassificationResult)

    def test_group_by_intent(self, classifier):
        results = classifier.classify_batch(["seo kaufen", "was ist seo"])
        groups = group_by_intent(results)
        assert isinstance(groups, dict)

    def test_filter_high_conversion(self, classifier):
        results = classifier.classify_batch(["seo kaufen", "was ist seo"])
        high = filter_high_conversion(results, min_score=60)
        assert all(r.conversion_score >= 60 for r in high)

    def test_sort_by_conversion(self, classifier):
        results = classifier.classify_batch(["seo kaufen", "was ist seo", "seo tool preis"])
        sorted_results = sort_by_conversion(results)
        scores = [r.conversion_score for r in sorted_results]
        assert scores == sorted(scores, reverse=True)


class TestCaching:
    def test_cache_hit(self, classifier):
        r1 = classifier.classify("seo test")
        r2 = classifier.classify("seo test")
        assert r1.keyword == r2.keyword
        assert r1.conversion_score == r2.conversion_score

    def test_clear_cache(self, classifier):
        classifier.classify("cached keyword")
        classifier.clear_cache()
        # Should not raise
        result = classifier.classify("cached keyword")
        assert result is not None