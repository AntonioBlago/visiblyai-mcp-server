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


def classify_keywords_advanced(
    keywords: list[str],
    brand_name: str = "",
    brand_variations: list | None = None,
    product_keywords: list | None = None,
    competitors: list | None = None,
    language: str = "German",
    location: str = "Germany",
) -> str:
    """Classify keywords using DataForSEO Search Intent API + regex classifier.

    Combines DataForSEO main_intent and secondary_intents with local regex
    classification (brand type, funnel stage, topic, conversion score).
    Credits: dynamic based on keyword count.
    """
    if not keywords:
        return json.dumps({"error": "keywords is required"})
    try:
        client = _require_key()
        result = client.classify_keywords_api(keywords, language, location)
        return _format_result(result)
    except Exception as e:
        return _handle_error(e)


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


def seo_agent(
    task: str,
    agent: str = "",
    domain: str = "",
    url: str = "",
    keyword: str = "",
    content: str = "",
    params: dict | None = None,
) -> str:
    """Run a specialized SEO agent for analysis, strategy, or content tasks.

    Agents: crawling, seo_analyst, strategist, copywriter, chief_editor, consultant.
    Auto-detects the best agent from your task description if not specified.
    Credits: varies by agent and task complexity.

    Args:
        task: What you want done (e.g., 'Analyze SEO for example.com')
        agent: Agent type (auto-detected if omitted)
        domain: Target domain
        url: Target URL to crawl/analyze
        keyword: Target keyword
        content: Content to review or optimize
        params: Agent-specific parameters

    Returns:
        JSON with agent results, credits used, and remaining balance
    """
    if not task:
        return json.dumps({"error": "task is required"})

    try:
        client = _require_key()
        result = client.seo_agent(task, agent, domain, url, keyword, content, params)
        return _format_result(result)
    except Exception as e:
        return _handle_error(e)


def seo_workflow(
    workflow: str,
    domain: str,
    project_id: int,
    params: dict | None = None,
) -> str:
    """Run a multi-step SEO workflow with report generation.

    Workflows: seo_performance_audit (GSC analysis + PDF, ~150 credits),
    indexing_diagnosis (indexing issues, ~200 credits). Requires Pro+ tier.
    May take several minutes.
    Credits: 150-200 depending on workflow.

    Args:
        workflow: Workflow type (seo_performance_audit or indexing_diagnosis)
        domain: Target domain
        project_id: Project ID from your projects dashboard
        params: Workflow-specific parameters

    Returns:
        JSON with workflow results and generated reports
    """
    if not workflow:
        return json.dumps({"error": "workflow is required"})
    if not domain:
        return json.dumps({"error": "domain is required"})
    if not project_id:
        return json.dumps({"error": "project_id is required"})

    try:
        client = _require_key()
        result = client.seo_workflow(workflow, domain, int(project_id), params)
        return _format_result(result)
    except Exception as e:
        return _handle_error(e)


# ------------------------------------------------------------------
# Google & Project Tools (no credits - uses user's OAuth tokens)
# ------------------------------------------------------------------

def list_projects() -> str:
    """List your EEAT projects with scores and status.

    Returns all projects linked to your account with names, domains,
    latest scores, competitor counts, and analysis status.
    Credits: 0 (free).

    Returns:
        JSON with project list
    """
    try:
        client = _require_key()
        result = client.list_projects()
        return _format_result(result)
    except Exception as e:
        return _handle_error(e)


def get_project(project_id: int) -> str:
    """Get detailed project info including competitors and Google connections.

    Returns project settings, competitor domains, and connected GSC/GA4 properties.
    Credits: 0 (free).

    Args:
        project_id: The project ID to retrieve

    Returns:
        JSON with project details, competitors, and Google connection status
    """
    if not project_id:
        return json.dumps({"error": "project_id is required"})

    try:
        client = _require_key()
        result = client.get_project(int(project_id))
        return _format_result(result)
    except Exception as e:
        return _handle_error(e)


def get_google_connections() -> str:
    """Show connected Google Search Console and Analytics 4 properties.

    Lists all GSC properties, GA4 properties, and GSC-GA4 pairings
    linked to your account.
    Credits: 0 (free).

    Returns:
        JSON with connected properties and pairings
    """
    try:
        client = _require_key()
        result = client.get_google_connections()
        return _format_result(result)
    except Exception as e:
        return _handle_error(e)


def query_search_console(
    gsc_property: str = "",
    dimension: str = "query",
    days: int = 28,
    limit: int = 100,
    country: str = "",
    device: str = "",
) -> str:
    """Query Google Search Console search analytics data.

    Fetches clicks, impressions, CTR, and position data from GSC.
    Auto-selects a property if not specified.
    Credits: 0 (free, uses your own OAuth token).

    Args:
        gsc_property: GSC property URL (auto-selected if empty)
        dimension: Data dimension: query, page, country, device, date (default: query)
        days: Number of days to query (1-365, default: 28)
        limit: Max rows to return (1-1000, default: 100)
        country: Filter by country code (e.g., 'DEU')
        device: Filter by device type (e.g., 'MOBILE')

    Returns:
        JSON with search analytics data
    """
    days = min(max(int(days), 1), 365)
    limit = min(max(int(limit), 1), 1000)

    try:
        client = _require_key()
        result = client.query_search_console(
            gsc_property=gsc_property,
            dimension=dimension,
            days=days,
            limit=limit,
            country=country,
            device=device,
        )
        return _format_result(result)
    except Exception as e:
        return _handle_error(e)


def query_analytics(
    ga4_property: str = "",
    report_type: str = "overview",
    days: int = 30,
    limit: int = 20,
) -> str:
    """Query Google Analytics 4 data.

    Fetches traffic, page views, revenue, or traffic source data from GA4.
    Auto-selects a property if not specified.
    Credits: 0 (free, uses your own OAuth token).

    Args:
        ga4_property: GA4 property ID (auto-selected if empty)
        report_type: Report type: overview, top_pages, traffic_sources, revenue (default: overview)
        days: Number of days to query (1-365, default: 30)
        limit: Max rows for top_pages (1-500, default: 20)

    Returns:
        JSON with analytics data
    """
    days = min(max(int(days), 1), 365)
    limit = min(max(int(limit), 1), 500)

    try:
        client = _require_key()
        result = client.query_analytics(
            ga4_property=ga4_property,
            report_type=report_type,
            days=days,
            limit=limit,
        )
        return _format_result(result)
    except Exception as e:
        return _handle_error(e)


def query_knowledge_base(
    query: str,
    top_k: int = 5,
    category: str = "",
    document_type: str = "",
    include_external: bool = True,
) -> str:
    """Search the SEO knowledge base with semantic search.

    Searches across all indexed content: blog articles, SEO documentation,
    best practices, checklists, and Google Search developer guidelines.
    Results are ranked by relevance + recency (newest content scores higher
    when similarity is tied).

    Credits: 2 per query.

    Args:
        query: Natural language question or topic (e.g. "how to fix crawl errors")
        top_k: Number of results to return (1-20, default: 5)
        category: Filter by category slug (e.g. "fundamentals", "crawling", "ranking")
        document_type: Filter by type (e.g. "best-practice", "checklist", "external-source", "blog")
        include_external: Include Google guidelines and external sources (default: true)

    Returns:
        JSON with ranked results: text excerpt, title, URL, source, date, similarity score
    """
    top_k = min(max(int(top_k), 1), 20)
    try:
        client = _require_key()
        from ..knowledge.rag_search import search_rag
        result = search_rag(
            client=client,
            query=query,
            top_k=top_k,
            category=category or None,
            document_type=document_type or None,
            include_external=include_external,
        )

        if result.get("error"):
            return json.dumps({"error": result["error"]}, ensure_ascii=False)

        results = result.get("results", [])
        output = {
            "query": query,
            "results_count": len(results),
            "results": results,
            "credits_used": result.get("credits_used", 2),
            "credits_remaining": result.get("credits_remaining"),
        }
        return json.dumps(output, ensure_ascii=False, indent=2)
    except Exception as e:
        return _handle_error(e)
