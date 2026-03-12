"""
Google Search Developer Guidelines - fetched from VisiblyAI platform API.

Content is scraped weekly from developers.google.com by the platform's cron
worker and served here. Falls back to minimal hardcoded content if the API
is unreachable.
"""

import logging
from typing import List

import httpx

from ..config import BASE_URL

logger = logging.getLogger(__name__)

# Minimal hardcoded fallback — covers the most important categories so the
# tool remains useful even when the platform API is offline.
_FALLBACK_CATEGORIES = [
    {"category": "fundamentals", "page_count": 1, "last_changed": None},
    {"category": "content", "page_count": 1, "last_changed": None},
    {"category": "crawling", "page_count": 2, "last_changed": None},
    {"category": "sitemaps", "page_count": 1, "last_changed": None},
    {"category": "structured_data", "page_count": 1, "last_changed": None},
    {"category": "performance", "page_count": 1, "last_changed": None},
    {"category": "ranking", "page_count": 1, "last_changed": None},
    {"category": "updates", "page_count": 1, "last_changed": None},
    {"category": "monitoring", "page_count": 1, "last_changed": None},
    {"category": "snippets", "page_count": 1, "last_changed": None},
    {"category": "guidelines", "page_count": 1, "last_changed": None},
]

_FALLBACK_CONTENT = {
    "fundamentals": (
        "# Google SEO Starter Guide\n\n"
        "Source: https://developers.google.com/search/docs/fundamentals/seo-starter-guide\n\n"
        "Key principles:\n"
        "- Create unique, accurate page titles using the <title> element\n"
        "- Use the meta description tag to summarize page content\n"
        "- Use heading tags to emphasise important text\n"
        "- Add structured data markup to your pages\n"
        "- Organise your site hierarchy with a logical URL structure\n"
        "- Make your site crawlable: avoid hiding content in iframes, Flash, or JS\n"
        "- Optimise images with descriptive filenames and alt text\n"
        "- Create mobile-friendly pages (Google uses mobile-first indexing)\n"
        "- Ensure fast page load times\n"
        "- Build quality backlinks by creating helpful, shareable content\n\n"
        "Note: Fetch live content via the VisiblyAI platform for full details."
    ),
    "content": (
        "# Creating Helpful, Reliable, People-First Content\n\n"
        "Source: https://developers.google.com/search/docs/fundamentals/creating-helpful-content\n\n"
        "Google's helpful content guidance:\n"
        "- Write for people, not search engines\n"
        "- Demonstrate first-hand expertise and depth of knowledge\n"
        "- Provide a satisfying experience — users should feel they learned enough\n"
        "- Avoid content created primarily to rank (SEO-first content)\n"
        "- Follow E-E-A-T: Experience, Expertise, Authoritativeness, Trustworthiness\n"
        "- Avoid: auto-generated content, scraped content, thin affiliate pages\n\n"
        "Note: Fetch live content via the VisiblyAI platform for full details."
    ),
}


def get_guidelines(category: str = "list") -> dict:
    """Get Google Search developer guidelines for a category.

    Tries the platform API first; falls back to hardcoded minimal content.

    Args:
        category: Category slug or 'list' to get the category index.

    Returns:
        Dict with 'categories' (for list) or 'category'+'pages' (for specific).
    """
    try:
        resp = httpx.get(
            BASE_URL + "/tools/google-guidelines",
            params={"category": category},
            timeout=15.0,
        )
        if resp.status_code == 200:
            data = resp.json()
            if data.get("success"):
                return data.get("data", {})
    except Exception:
        pass

    # Fallback
    if category.lower() in ("list", "all", "help"):
        return {"categories": _FALLBACK_CATEGORIES}

    fallback_content = _FALLBACK_CONTENT.get(category)
    if fallback_content:
        return {
            "category": category,
            "pages": [
                {
                    "title": f"Google Search: {category.replace('_', ' ').title()}",
                    "source_url": f"https://developers.google.com/search/docs",
                    "content": fallback_content,
                    "last_changed": None,
                }
            ],
        }

    available = ", ".join(c["category"] for c in _FALLBACK_CATEGORIES)
    return {
        "category": category,
        "pages": [],
        "error": f"Category '{category}' not found in fallback. Available: {available}",
    }


def list_categories() -> List[dict]:
    """List all available guideline categories with page counts.

    Tries API first, falls back to hardcoded list.

    Returns:
        List of dicts: [{category, page_count, last_changed}, ...]
    """
    try:
        resp = httpx.get(
            BASE_URL + "/tools/google-guidelines",
            params={"category": "list"},
            timeout=15.0,
        )
        if resp.status_code == 200:
            data = resp.json()
            if data.get("success"):
                inner = data.get("data", {})
                return inner.get("categories", [])
    except Exception:
        pass

    return _FALLBACK_CATEGORIES
