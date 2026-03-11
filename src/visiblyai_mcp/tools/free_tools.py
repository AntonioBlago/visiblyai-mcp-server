"""
Free MCP tools - run locally, no API key or credits required.
"""

import json
import logging
from urllib.parse import urlparse

from ..classifier import KeywordClassifier, ClassificationResult
from ..knowledge.checklists import get_checklist, list_checklists, CHECKLIST_TYPES
from ..knowledge.seo_guidance import get_guidance, list_topics, search_guidance
from ..knowledge.skills import get_skill as _get_skill, list_skills as _list_skills
from ..config import get_api_key, SIGNUP_URL

logger = logging.getLogger(__name__)


def classify_keywords(
    keywords: list[str],
    brand_name: str = "",
    brand_variations: list[str] | None = None,
    product_keywords: list[str] | None = None,
    competitors: list[dict] | None = None,
) -> str:
    """Classify keywords by search intent, funnel stage, brand type, and topic.

    Supports German and English keywords. Returns structured classification
    including intent (transactional/commercial/informational/navigational/local),
    funnel stage (TOFU/MOFU/BOFU), conversion score (0-100), and topic.

    Args:
        keywords: List of keywords to classify
        brand_name: Optional brand name for brand vs generic classification
        brand_variations: Optional additional brand name spellings
        product_keywords: Optional product-related keywords
        competitors: Optional list of competitor configs [{"name": "...", "variations": [...]}]

    Returns:
        JSON formatted classification results
    """
    if not keywords:
        return json.dumps({"error": "No keywords provided"}, indent=2)

    brand_config = None
    if brand_name:
        brand_config = {
            "brand_name": brand_name,
            "brand_variations": brand_variations or [],
            "product_keywords": product_keywords or [],
            "competitors": competitors or [],
        }

    classifier = KeywordClassifier(brand_config=brand_config)
    results = classifier.classify_batch(keywords)

    output = []
    for r in results:
        output.append({
            "keyword": r.keyword,
            "intent": r.intent.type.value,
            "intent_confidence": round(r.intent.confidence, 2),
            "conversion_potential": r.intent.conversion_potential.value,
            "funnel_stage": r.funnel.stage.value,
            "funnel_description": r.funnel.description,
            "brand_type": r.brand.type.value,
            "matched_brand": r.brand.matched_brand,
            "primary_topic": r.topic.primary_topic,
            "conversion_score": r.conversion_score,
            "overall_confidence": round(r.overall_confidence, 2),
            "modifiers": r.modifiers.detected_modifiers,
        })

    return json.dumps({
        "total": len(output),
        "results": output,
    }, indent=2, ensure_ascii=False)


def seo_checklist(
    checklist_type: str = "general",
    language: str = "en",
) -> str:
    """Get an SEO checklist. Available types: general, blog, ecommerce, discover, backlink, all.

    Returns a comprehensive, actionable checklist in markdown format.

    Args:
        checklist_type: Type of checklist (general, blog, ecommerce, discover, backlink, or all)
        language: Language (en or de)

    Returns:
        Markdown formatted checklist
    """
    return get_checklist(checklist_type, language)


def seo_guidance(
    topic: str,
) -> str:
    """Get SEO best practices and guidance on a specific topic.

    Available topics: title_tags, meta_descriptions, heading_structure,
    internal_linking, core_web_vitals, eeat, keyword_research, schema_markup,
    image_optimization, local_seo.

    Use topic='list' to see all available topics.

    Args:
        topic: SEO topic to get guidance on, or 'list' for all topics

    Returns:
        Markdown formatted SEO guidance
    """
    if topic.lower() in ("list", "help", "all"):
        topics = list_topics()
        lines = ["# Available SEO Guidance Topics\n"]
        for t in topics:
            lines.append(f"- **{t['topic']}**: {t['title']}")
        return "\n".join(lines)

    return get_guidance(topic)


def get_skill(name: str) -> str:
    """Get an SEO workflow skill with step-by-step methodology.

    Skills provide structured workflows for common SEO tasks including
    methodology, CTR models, quality gates, and action items.

    Use name='list' to see all available skills.

    Args:
        name: Skill name (e.g. 'seo-audit') or 'list' for all

    Returns:
        Markdown formatted skill content
    """
    if name.lower() in ("list", "help", "all"):
        skills = _list_skills()
        lines = ["# Available SEO Workflow Skills\n"]
        for s in skills:
            lines.append(f"- **{s['skill_name']}**: {s.get('description', '')}")
        if not skills:
            lines.append("No skills available. Skills are synced via `visiblyai-mcp-server sync-skills`.")
        return "\n".join(lines)

    return _get_skill(name)


def analyze_url_structure(url: str) -> str:
    """Analyze a URL for SEO-friendliness.

    Checks URL length, structure, keyword presence, and common issues.

    Args:
        url: The URL to analyze

    Returns:
        JSON formatted analysis results
    """
    try:
        parsed = urlparse(url)
    except Exception:
        return json.dumps({"error": "Invalid URL format"})

    path = parsed.path.rstrip("/")
    issues = []
    positives = []

    # Length check
    if len(url) > 100:
        issues.append("URL is too long (>100 chars). Keep under 70 chars for best results.")
    elif len(url) <= 70:
        positives.append("URL length is optimal (under 70 characters)")

    # HTTPS check
    if parsed.scheme == "https":
        positives.append("Uses HTTPS")
    elif parsed.scheme == "http":
        issues.append("Not using HTTPS. Migrate to HTTPS for security and SEO.")

    # Path analysis
    if path:
        segments = [s for s in path.split("/") if s]

        # Depth check
        if len(segments) > 4:
            issues.append(f"URL is {len(segments)} levels deep. Keep under 3-4 levels.")
        elif len(segments) <= 3:
            positives.append(f"Good URL depth ({len(segments)} levels)")

        # Underscores
        if "_" in path:
            issues.append("Uses underscores. Use hyphens (-) instead for word separation.")
        elif "-" in path:
            positives.append("Uses hyphens for word separation")

        # Uppercase
        if path != path.lower():
            issues.append("Contains uppercase characters. URLs should be lowercase.")
        else:
            positives.append("All lowercase")

        # Parameters in path
        if "?" in url and "utm_" not in url:
            issues.append("Contains query parameters. Use clean, static URLs when possible.")

        # File extensions
        if any(path.endswith(ext) for ext in [".html", ".php", ".asp", ".jsp"]):
            issues.append("Contains file extension. Modern SEO prefers extensionless URLs.")

        # Numbers/IDs
        import re
        if re.search(r'/\d{4,}/', path) or re.search(r'/id/\d+', path):
            issues.append("Contains numeric IDs. Use descriptive slugs instead.")

        # Stop words
        stop_words = ["the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
                       "der", "die", "das", "und", "oder", "in", "auf", "an", "zu", "fuer"]
        path_words = path.lower().replace("-", " ").replace("/", " ").split()
        found_stops = [w for w in path_words if w in stop_words]
        if found_stops:
            issues.append(f"Contains stop words: {', '.join(found_stops)}. Remove for cleaner URLs.")

    else:
        positives.append("Root URL (homepage)")

    # Domain analysis
    if parsed.netloc:
        if "www." in parsed.netloc:
            positives.append("Uses www subdomain (ensure redirect from non-www)")
        if len(parsed.netloc) > 30:
            issues.append("Domain name is quite long. Shorter domains are easier to remember.")

    score = max(0, min(100, 100 - (len(issues) * 15) + (len(positives) * 5)))

    return json.dumps({
        "url": url,
        "score": score,
        "issues": issues,
        "positives": positives,
        "recommendation": "Good URL structure" if score >= 70 else "URL needs improvement",
    }, indent=2, ensure_ascii=False)


def get_account_info() -> str:
    """Check your VisiblyAI account status, credit balance, and subscription tier.

    Requires VISIBLYAI_API_KEY environment variable.

    Returns:
        JSON formatted account information
    """
    api_key = get_api_key()
    if not api_key:
        return json.dumps({
            "authenticated": False,
            "message": f"No API key set. Set VISIBLYAI_API_KEY environment variable.",
            "signup_url": SIGNUP_URL,
            "free_tools": [
                "classify_keywords", "seo_checklist", "seo_guidance",
                "get_skill", "analyze_url_structure", "list_locations",
            ],
        }, indent=2)

    try:
        from ..api_client import VisiblyAIClient
        client = VisiblyAIClient(api_key)
        result = client.verify()
        data = result.get("data", {})
        return json.dumps({
            "authenticated": True,
            "email": data.get("email"),
            "tier": data.get("tier"),
            "credits_balance": data.get("credits_balance"),
        }, indent=2)
    except Exception as e:
        return json.dumps({
            "authenticated": False,
            "error": str(e),
        }, indent=2)


def list_locations() -> str:
    """List available countries/locations for SEO data queries.

    Returns supported locations with their codes for use in paid tools.

    Returns:
        JSON formatted list of available locations
    """
    # Static data to avoid API call
    locations = [
        {"location_name": "Germany", "country_iso_code": "DE", "language_name": "German"},
        {"location_name": "United States", "country_iso_code": "US", "language_name": "English"},
        {"location_name": "United Kingdom", "country_iso_code": "GB", "language_name": "English"},
        {"location_name": "Austria", "country_iso_code": "AT", "language_name": "German"},
        {"location_name": "Switzerland", "country_iso_code": "CH", "language_name": "German"},
        {"location_name": "France", "country_iso_code": "FR", "language_name": "French"},
        {"location_name": "Spain", "country_iso_code": "ES", "language_name": "Spanish"},
        {"location_name": "Italy", "country_iso_code": "IT", "language_name": "Italian"},
        {"location_name": "Netherlands", "country_iso_code": "NL", "language_name": "Dutch"},
        {"location_name": "Canada", "country_iso_code": "CA", "language_name": "English"},
        {"location_name": "Australia", "country_iso_code": "AU", "language_name": "English"},
        {"location_name": "Brazil", "country_iso_code": "BR", "language_name": "Portuguese"},
        {"location_name": "Japan", "country_iso_code": "JP", "language_name": "Japanese"},
        {"location_name": "India", "country_iso_code": "IN", "language_name": "English"},
        {"location_name": "Poland", "country_iso_code": "PL", "language_name": "Polish"},
        {"location_name": "Sweden", "country_iso_code": "SE", "language_name": "Swedish"},
        {"location_name": "Belgium", "country_iso_code": "BE", "language_name": "Dutch"},
        {"location_name": "Czech Republic", "country_iso_code": "CZ", "language_name": "Czech"},
        {"location_name": "Denmark", "country_iso_code": "DK", "language_name": "Danish"},
        {"location_name": "Norway", "country_iso_code": "NO", "language_name": "Norwegian"},
    ]

    return json.dumps({
        "total": len(locations),
        "locations": locations,
        "note": "Use 'location_name' value in paid tool calls (e.g., location='Germany')",
    }, indent=2)
