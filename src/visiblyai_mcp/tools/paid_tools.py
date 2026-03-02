"""
Paid MCP tools - proxy to the VisiblyAI platform API. Require API key and credits.
"""

import json
import logging

from ..api_client import VisiblyAIClient, APIError
from ..config import get_api_key, SIGNUP_URL, CREDITS_URL

logger = logging.getLogger(__name__)


def _require_key() -> VisiblyAIClient:
    """Get API client or return helpful error."""
    api_key = get_api_key()
    if not api_key:
        raise APIError(
            f"API key required for paid tools. "
            f"Set VISIBLYAI_API_KEY env var. Sign up at {SIGNUP_URL}",
            status_code=401,
        )
    return VisiblyAIClient(api_key)


def _format_result(result: dict) -> str:
    """Format API result as JSON string."""
    output = {
        "data": result.get("data"),
        "credits_used": result.get("credits_used", 0),
        "credits_remaining": result.get("credits_remaining"),
    }
    return json.dumps(output, indent=2, ensure_ascii=False, default=str)


def _handle_error(e: Exception) -> str:
    """Format error as JSON string."""
    if isinstance(e, APIError):
        error_data = {"error": str(e)}
        if e.credits_hint:
            error_data["credits_url"] = CREDITS_URL
        if e.status_code == 401:
            error_data["signup_url"] = SIGNUP_URL
        return json.dumps(error_data, indent=2)
    return json.dumps({"error": str(e)}, indent=2)


def get_traffic_snapshot(
    domain: str,
    location: str = "Germany",
) -> str:
    """Get current organic and paid traffic data for a domain.

    Returns estimated monthly traffic, top keywords, and traffic distribution.
    Credits: varies based on data volume.

    Args:
        domain: Domain to analyze (e.g., 'example.com')
        location: Country for data (default: Germany). Use list_locations for options.

    Returns:
        JSON with traffic data, credits used, and remaining balance
    """
    try:
        client = _require_key()
        result = client.traffic_snapshot(domain, location)
        return _format_result(result)
    except Exception as e:
        return _handle_error(e)


def get_historical_traffic(
    domain: str,
    location: str = "Germany",
    date_from: str = "",
    date_to: str = "",
) -> str:
    """Get historical traffic trends for a domain (up to 5 years).

    Shows organic and paid traffic changes over time.
    Credits: varies based on data volume.

    Args:
        domain: Domain to analyze (e.g., 'example.com')
        location: Country for data (default: Germany)
        date_from: Start date (YYYY-MM-DD), optional
        date_to: End date (YYYY-MM-DD), optional

    Returns:
        JSON with historical traffic data
    """
    try:
        client = _require_key()
        result = client.historical_traffic(
            domain, location,
            date_from=date_from or None,
            date_to=date_to or None,
        )
        return _format_result(result)
    except Exception as e:
        return _handle_error(e)


def get_keywords(
    domain: str,
    location: str = "Germany",
    limit: int = 100,
) -> str:
    """Get top ranking keywords for a domain.

    Returns keywords with search volume, position, URL, and traffic share.
    Credits: varies based on data volume.

    Args:
        domain: Domain to analyze (e.g., 'example.com')
        location: Country for data (default: Germany)
        limit: Max keywords to return (default: 100, max: 1000)

    Returns:
        JSON with keyword rankings data
    """
    try:
        client = _require_key()
        result = client.keywords(domain, location, min(limit, 1000))
        return _format_result(result)
    except Exception as e:
        return _handle_error(e)


def get_competitors(
    domain: str,
    location: str = "Germany",
    language: str = "German",
    limit: int = 10,
) -> str:
    """Get competitor domains based on keyword overlap.

    Returns domains competing for the same keywords.
    Credits: varies based on data volume.

    Args:
        domain: Domain to analyze (e.g., 'example.com')
        location: Country for data (default: Germany)
        language: Language for analysis (default: German)
        limit: Max competitors to return (default: 10, max: 50)

    Returns:
        JSON with competitor data
    """
    try:
        client = _require_key()
        result = client.competitors(domain, location, language, min(limit, 50))
        return _format_result(result)
    except Exception as e:
        return _handle_error(e)


def get_backlinks(
    domain: str,
    location: str = "Germany",
    limit: int = 100,
) -> str:
    """Get backlink profile for a domain.

    Returns Domain Rating (0-100), total backlinks, referring domains,
    dofollow/nofollow ratio, and individual backlinks.
    Credits: varies based on data volume.

    Args:
        domain: Domain to analyze (e.g., 'example.com')
        location: Country for data (default: Germany)
        limit: Max backlinks to return (default: 100, max: 1000)

    Returns:
        JSON with backlink data
    """
    try:
        client = _require_key()
        result = client.backlinks(domain, location, min(limit, 1000))
        return _format_result(result)
    except Exception as e:
        return _handle_error(e)


def get_referring_domains(
    domain: str,
    location: str = "Germany",
    limit: int = 50,
) -> str:
    """Get referring domains linking to a domain.

    Returns domains with their authority scores and link counts.
    Credits: varies based on data volume.

    Args:
        domain: Domain to analyze (e.g., 'example.com')
        location: Country for data (default: Germany)
        limit: Max domains to return (default: 50, max: 500)

    Returns:
        JSON with referring domain data
    """
    try:
        client = _require_key()
        result = client.referring_domains(domain, location, min(limit, 500))
        return _format_result(result)
    except Exception as e:
        return _handle_error(e)


def validate_keywords(
    keywords: list[str],
    location: str = "Germany",
    language: str = "German",
    top_n: int = 50,
) -> str:
    """Validate keywords and get search volume data.

    Returns search volume, competition level, CPC, and opportunity score.
    Credits: varies based on number of keywords.

    Args:
        keywords: List of keywords to validate
        location: Country for data (default: Germany)
        language: Language for data (default: German)
        top_n: Number of top results (default: 50, max: 200)

    Returns:
        JSON with keyword validation data
    """
    if not keywords:
        return json.dumps({"error": "No keywords provided"})

    try:
        client = _require_key()
        result = client.validate_keywords(keywords, location, language, min(top_n, 200))
        return _format_result(result)
    except Exception as e:
        return _handle_error(e)


def crawl_website(
    url: str,
    keyword: str = "",
    max_pages: int = 1,
) -> str:
    """Crawl a website and get page data with optional OnPage SEO analysis.

    Fetches page content and extracts title, meta description, headings,
    word count, links, and images. If keyword is provided, runs a 24-point
    OnPage SEO analysis.
    Credits: 15-60 depending on pages crawled.

    Args:
        url: URL to crawl (e.g., 'https://example.com/page')
        keyword: Optional keyword for OnPage SEO analysis
        max_pages: Number of pages to crawl (default: 1, max: 10)

    Returns:
        JSON with crawl data and optional SEO analysis
    """
    try:
        client = _require_key()
        result = client.crawl(url, keyword, min(max_pages, 10))
        return _format_result(result)
    except Exception as e:
        return _handle_error(e)


def onpage_analysis(
    url: str,
    keyword: str,
) -> str:
    """Run a 24-point OnPage SEO analysis on a URL.

    Analyzes keyword optimization (6 checks), content optimization (9 checks),
    and technical optimization (9 checks). Returns scores, passed/failed checks,
    and actionable recommendations.
    Credits: 15.

    Args:
        url: URL to analyze (e.g., 'https://example.com/page')
        keyword: Target keyword to check optimization for

    Returns:
        JSON with analysis scores, check results, and recommendations
    """
    if not keyword:
        return json.dumps({"error": "keyword is required for OnPage analysis"})

    try:
        client = _require_key()
        result = client.onpage_analysis(url, keyword)
        return _format_result(result)
    except Exception as e:
        return _handle_error(e)


def check_links(
    url: str,
) -> str:
    """Check all links on a page for broken/redirect status.

    Crawls the page and checks each link's HTTP status.
    Credits: 20.

    Args:
        url: URL to check links on (e.g., 'https://example.com/page')

    Returns:
        JSON with link check results
    """
    try:
        client = _require_key()
        result = client.check_links(url)
        return _format_result(result)
    except Exception as e:
        return _handle_error(e)
