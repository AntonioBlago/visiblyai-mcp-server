"""
Project-data & content tools: read-only proxies to the VisiblyAI platform.
All tools cost 0 credits and never write back. Require an API key.
"""

import json

from ..api_client import APIError, VisiblyAIClient
from ..config import SIGNUP_URL, get_api_key
from .paid_tools import _format_result, _handle_error

__all__ = [
    "get_gsc_clusters", "get_cluster_keywords", "get_analytics_insights", "get_revenue_insights",
    "get_scorecard", "get_eeat_summary", "list_pages", "get_internal_links", "recall",
    "list_articles", "get_article", "list_content_queries", "get_content_briefing",
    "get_content_status", "score_text",
]


def _require_key() -> VisiblyAIClient:
    """Get API client or raise a helpful error."""
    api_key = get_api_key()
    if not api_key:
        raise APIError(f"API key required. Set VISIBLYAI_API_KEY env var. Sign up at {SIGNUP_URL}", status_code=401)
    return VisiblyAIClient(api_key)


def _call(method: str, *args, **kwargs) -> str:
    """Call a client method and format the result, converting any error to JSON."""
    try:
        client = _require_key()
        return _format_result(getattr(client, method)(*args, **kwargs))
    except Exception as e:  # noqa: BLE001 - every failure becomes a JSON error for the LLM
        return _handle_error(e)


def _bad(message: str) -> str:
    """Format a validation error as JSON, without touching the API client."""
    return json.dumps({"error": message})


def get_gsc_clusters(project_id: int, days: int = 28, top_n: int = 30, country: str | None = None) -> str:
    """List Search Console query clusters for a project, ranked by impressions."""
    if not project_id:
        return _bad("project_id is required")
    return _call("gsc_clusters", project_id, days=days, top_n=top_n, country=country)


def get_cluster_keywords(project_id: int, cluster_key: str, days: int = 28, country: str | None = None,
                         limit: int = 100, offset: int = 0) -> str:
    """List the individual keywords inside one GSC cluster (cluster_key from get_gsc_clusters)."""
    if not project_id or not (cluster_key or "").strip():
        return _bad("project_id and cluster_key are required (use cluster_key from get_gsc_clusters)")
    return _call("cluster_keywords", project_id, cluster_key, days=days, country=country, limit=limit, offset=offset)


def get_analytics_insights(project_id: int, days: int = 28) -> str:
    """Get GA4 flow, channel, and event insights for a project."""
    if not project_id:
        return _bad("project_id is required")
    return _call("analytics_insights", project_id, days=days)


def get_revenue_insights(project_id: int) -> str:
    """Get revenue Pareto and cluster-revenue insights for a project."""
    if not project_id:
        return _bad("project_id is required")
    return _call("revenue_insights", project_id)


def get_scorecard(project_id: int, days: int = 28) -> str:
    """Get the KPI scorecard (leading + lagging indicators) for a project."""
    if not project_id:
        return _bad("project_id is required")
    if days not in (28, 90):
        return _bad("days must be 28 or 90")
    return _call("scorecard", project_id, days=days)


def get_eeat_summary(project_id: int) -> str:
    """Get the latest EEAT analysis summary and open todos for a project."""
    if not project_id:
        return _bad("project_id is required")
    return _call("eeat_summary", project_id)


def list_pages(project_id: int, page_type: str | None = None, search: str = "", limit: int = 50, offset: int = 0) -> str:
    """List a project's crawled pages inventory, optionally filtered by type or search text."""
    if not project_id:
        return _bad("project_id is required")
    return _call("pages", project_id, page_type=page_type, search=search, limit=limit, offset=offset)


def get_internal_links(project_id: int, url: str | None = None, limit: int = 20, offset: int = 0) -> str:
    """List the internal link graph summary for a project, or inbound links to one URL."""
    if not project_id:
        return _bad("project_id is required")
    return _call("internal_links", project_id, url=url, limit=limit, offset=offset)


def recall(query: str = "", project_id: int | None = None, limit: int = 10) -> str:
    """Recall previously remembered customer-graph facts, optionally filtered by query and project."""
    return _call("memory_recall", query=query or "", project_id=project_id, limit=limit)


def list_articles(project_id: int, status: str = "all", limit: int = 25, offset: int = 0) -> str:
    """List content-autopilot articles for a project, optionally filtered by status."""
    if not project_id:
        return _bad("project_id is required")
    return _call("content_articles", project_id, status=status, limit=limit, offset=offset)


def get_article(article_id: int, include_content: bool = False, content_offset: int = 0,
                content_limit: int = 20000, project_id: int | None = None) -> str:
    """Get one content-autopilot article, with optional paginated content body."""
    if not article_id:
        return _bad("article_id is required")
    return _call("content_article", article_id, include_content=include_content, content_offset=content_offset,
                 content_limit=content_limit, project_id=project_id)


def list_content_queries(project_id: int, limit: int = 50, offset: int = 0) -> str:
    """List content-intelligence queries for a project."""
    if not project_id:
        return _bad("project_id is required")
    return _call("content_queries", project_id, limit=limit, offset=offset)


def get_content_briefing(query_id: int, project_id: int | None = None) -> str:
    """Get the deterministic content briefing (terms, entities, questions) for a content query."""
    if not query_id:
        return _bad("query_id is required")
    return _call("content_briefing", query_id, project_id=project_id)


def get_content_status(query_id: int, project_id: int | None = None) -> str:
    """Get the analysis status of one content-intelligence query."""
    if not query_id:
        return _bad("query_id is required")
    return _call("content_status", query_id, project_id=project_id)


def score_text(project_id: int, content: str, format: str = "markdown",
               query_id: int | None = None, persona_id: int | None = None) -> str:
    """Score a draft (HTML or markdown) against a content query's analysis and an optional persona."""
    if not project_id or not (content or "").strip():
        return _bad("project_id and content are required")
    if format not in ("html", "markdown"):
        return _bad("format must be 'html' or 'markdown'")
    return _call("score_text", project_id, content, format=format, query_id=query_id, persona_id=persona_id)
