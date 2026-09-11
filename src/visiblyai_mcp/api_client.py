"""HTTP client for communicating with the VisiblyAI platform API."""

import httpx
import logging
from typing import Any

from .config import BASE_URL, get_api_key, SIGNUP_URL, CREDITS_URL

logger = logging.getLogger(__name__)

# Reusable timeout config
_TIMEOUT = httpx.Timeout(60.0, connect=10.0)


class APIError(Exception):
    """Raised when the platform API returns an error."""

    def __init__(self, message: str, status_code: int = 0, credits_hint: bool = False,
                 detail: dict | None = None):
        self.status_code = status_code
        self.credits_hint = credits_hint
        self.detail = detail
        super().__init__(message)


class VisiblyAIClient:
    """Synchronous HTTP client for the VisiblyAI MCP API."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or get_api_key()
        self._client: httpx.Client | None = None

    def _ensure_client(self) -> httpx.Client:
        if self._client is None or self._client.is_closed:
            headers = {}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            self._client = httpx.Client(
                base_url=BASE_URL,
                headers=headers,
                timeout=_TIMEOUT,
            )
        return self._client

    def close(self):
        if self._client and not self._client.is_closed:
            self._client.close()

    # ------------------------------------------------------------------
    # Auth / Account
    # ------------------------------------------------------------------

    def verify(self) -> dict:
        """Verify API key and return user info."""
        self._require_key()
        return self._post("/auth/verify")

    def get_credits(self) -> dict:
        """Get current credit balance."""
        self._require_key()
        return self._get("/account/credits")

    # ------------------------------------------------------------------
    # Paid tools
    # ------------------------------------------------------------------

    def traffic_snapshot(self, domain: str, location: str = "Germany") -> dict:
        return self._post("/tools/traffic-snapshot", {"domain": domain, "location": location})

    def historical_traffic(self, domain: str, location: str = "Germany",
                           date_from: str | None = None, date_to: str | None = None) -> dict:
        payload: dict[str, Any] = {"domain": domain, "location": location}
        if date_from:
            payload["date_from"] = date_from
        if date_to:
            payload["date_to"] = date_to
        return self._post("/tools/historical-traffic", payload)

    def keywords(self, domain: str, location: str = "Germany", limit: int = 1000) -> dict:
        return self._post("/tools/keywords", {"domain": domain, "location": location, "limit": limit})

    def competitors(self, domain: str, location: str = "Germany",
                    language: str = "German", limit: int = 10) -> dict:
        return self._post("/tools/competitors", {
            "domain": domain, "location": location, "language": language, "limit": limit
        })

    def backlinks(self, domain: str, location: str = "Germany", limit: int = 100) -> dict:
        return self._post("/tools/backlinks", {"domain": domain, "location": location, "limit": limit})

    def referring_domains(self, domain: str, location: str = "Germany", limit: int = 50) -> dict:
        return self._post("/tools/referring-domains", {"domain": domain, "location": location, "limit": limit})

    def validate_keywords(self, keywords: list[str], location: str = "Germany",
                          language: str = "German", top_n: int = 50) -> dict:
        return self._post("/tools/validate-keywords", {
            "keywords": keywords, "location": location, "language": language, "top_n": top_n
        })

    def crawl(self, url: str, keyword: str = "", max_pages: int = 1) -> dict:
        return self._post("/tools/crawl", {"url": url, "keyword": keyword, "max_pages": max_pages})

    def onpage_analysis(self, url: str, keyword: str) -> dict:
        return self._post("/tools/onpage-analysis", {"url": url, "keyword": keyword})

    def check_serp(self, keyword: str, location: str = "Germany", language: str = "German", depth: int = 10) -> dict:
        return self._post("/tools/check-serp", {
            "keyword": keyword, "location": location, "language": language, "depth": depth
        })

    def check_pagespeed(self, url: str, strategy: str = "mobile") -> dict:
        return self._post("/tools/check-pagespeed", {"url": url, "strategy": strategy})

    def audit_sitemap(self, domain: str) -> dict:
        return self._post("/tools/audit-sitemap", {"domain": domain})

    def check_structured_data(self, url: str) -> dict:
        return self._post("/tools/check-structured-data", {"url": url})

    def check_hreflang(self, url: str) -> dict:
        return self._post("/tools/check-hreflang", {"url": url})

    def query_fanout(
        self,
        url: str,
        keyword: str,
        data_source: str = "dataforseo",
        gsc_property: str | None = None,
        language: str = "en",
    ) -> dict:
        payload: dict = {
            "url": url,
            "keyword": keyword,
            "data_source": data_source,
            "language": language,
        }
        if gsc_property:
            payload["gsc_property"] = gsc_property
        return self._post("/tools/query-fanout", payload)

    def check_links(self, url: str) -> dict:
        return self._post("/tools/check-links", {"url": url})

    def seo_agent(self, task: str, agent: str = "", domain: str = "",
                  url: str = "", keyword: str = "", content: str = "",
                  params: dict | None = None, project_id: int = 0) -> dict:
        payload: dict[str, Any] = {"task": task}
        if agent:
            payload["agent"] = agent
        if domain:
            payload["domain"] = domain
        if url:
            payload["url"] = url
        if keyword:
            payload["keyword"] = keyword
        if content:
            payload["content"] = content
        if params:
            payload["params"] = params
        if project_id:
            payload["project_id"] = project_id
        return self._post("/tools/seo-agent", payload)

    def seo_workflow(self, workflow: str, domain: str, project_id: int,
                     params: dict | None = None) -> dict:
        payload: dict[str, Any] = {
            "workflow": workflow, "domain": domain, "project_id": project_id
        }
        if params:
            payload["params"] = params
        return self._post("/tools/seo-workflow", payload)

    def classify_keywords_api(self, keywords: list[str], language: str = "German",
                              location: str = "Germany") -> dict:
        return self._post("/tools/classify-keywords", {
            "keywords": keywords, "language": language, "location": location
        })

    def rag_search(
        self,
        query: str,
        top_k: int = 5,
        category: str | None = None,
        document_type: str | None = None,
        include_external: bool = True,
    ) -> dict:
        payload: dict[str, Any] = {
            "query": query,
            "top_k": top_k,
            "include_external": include_external,
        }
        if category:
            payload["category"] = category
        if document_type:
            payload["document_type"] = document_type
        return self._post("/tools/rag-search", payload)

    # ------------------------------------------------------------------
    # Google & Project tools (no credits)
    # ------------------------------------------------------------------

    def list_projects(self) -> dict:
        return self._post("/tools/list-projects")

    def get_project(self, project_id: int) -> dict:
        return self._post("/tools/get-project", {"project_id": project_id})

    def get_google_connections(self) -> dict:
        return self._post("/tools/google-connections")

    def query_search_console(self, gsc_property: str = "", dimension: str = "query",
                             days: int = 28, limit: int = 100,
                             country: str = "", device: str = "") -> dict:
        payload: dict[str, Any] = {"dimension": dimension, "days": days, "limit": limit}
        if gsc_property:
            payload["gsc_property"] = gsc_property
        if country:
            payload["country"] = country
        if device:
            payload["device"] = device
        return self._post("/tools/query-search-console", payload)

    def query_analytics(self, ga4_property: str = "", report_type: str = "overview",
                        days: int = 30, limit: int = 20) -> dict:
        payload: dict[str, Any] = {"report_type": report_type, "days": days, "limit": limit}
        if ga4_property:
            payload["ga4_property"] = ga4_property
        return self._post("/tools/query-analytics", payload)

    # ------------------------------------------------------------------
    # Project data & content (read-only, 0 credits)
    # ------------------------------------------------------------------

    def gsc_clusters(self, project_id: int, days: int = 28, top_n: int = 30, country: str | None = None) -> dict:
        payload: dict[str, Any] = {"project_id": project_id, "days": days, "top_n": top_n}
        if country:
            payload["country"] = country
        return self._post("/tools/gsc-clusters", payload)

    def cluster_keywords(self, project_id: int, cluster_key: str, days: int = 28, country: str | None = None,
                         limit: int = 100, offset: int = 0) -> dict:
        payload: dict[str, Any] = {"project_id": project_id, "cluster_key": cluster_key, "days": days,
                                   "limit": limit, "offset": offset}
        if country:
            payload["country"] = country
        return self._post("/tools/cluster-keywords", payload)

    def analytics_insights(self, project_id: int, days: int = 28) -> dict:
        return self._post("/tools/analytics-insights", {"project_id": project_id, "days": days})

    def revenue_insights(self, project_id: int) -> dict:
        return self._post("/tools/revenue-insights", {"project_id": project_id})

    def scorecard(self, project_id: int, days: int = 28) -> dict:
        return self._post("/tools/scorecard", {"project_id": project_id, "days": days})

    def eeat_summary(self, project_id: int) -> dict:
        return self._post("/tools/eeat-summary", {"project_id": project_id})

    def pages(self, project_id: int, page_type: str | None = None, search: str = "",
              limit: int = 50, offset: int = 0) -> dict:
        payload: dict[str, Any] = {"project_id": project_id, "search": search, "limit": limit, "offset": offset}
        if page_type:
            payload["page_type"] = page_type
        return self._post("/tools/pages", payload)

    def internal_links(self, project_id: int, url: str | None = None, limit: int = 20, offset: int = 0) -> dict:
        payload: dict[str, Any] = {"project_id": project_id, "limit": limit, "offset": offset}
        if url:
            payload["url"] = url
        return self._post("/tools/internal-links", payload)

    def memory_recall(self, query: str = "", project_id: int | None = None, limit: int = 10) -> dict:
        payload: dict[str, Any] = {"query": query, "limit": limit}
        if project_id:
            payload["project_id"] = project_id
        return self._post("/tools/memory/recall", payload)

    def content_articles(self, project_id: int, status: str = "all", limit: int = 25, offset: int = 0) -> dict:
        return self._post("/tools/content/articles",
                          {"project_id": project_id, "status": status, "limit": limit, "offset": offset})

    def content_article(self, article_id: int, include_content: bool = False, content_offset: int = 0,
                        content_limit: int = 20000, project_id: int | None = None) -> dict:
        payload: dict[str, Any] = {"article_id": article_id, "include_content": include_content,
                                   "content_offset": content_offset, "content_limit": content_limit}
        if project_id:
            payload["project_id"] = project_id
        return self._post("/tools/content/article", payload)

    def content_queries(self, project_id: int, limit: int = 50, offset: int = 0) -> dict:
        return self._post("/tools/content/queries", {"project_id": project_id, "limit": limit, "offset": offset})

    def content_briefing(self, query_id: int, project_id: int | None = None) -> dict:
        payload: dict[str, Any] = {"query_id": query_id}
        if project_id:
            payload["project_id"] = project_id
        return self._post("/tools/content/briefing", payload)

    def content_status(self, query_id: int, project_id: int | None = None) -> dict:
        payload: dict[str, Any] = {"query_id": query_id}
        if project_id:
            payload["project_id"] = project_id
        return self._post("/tools/content/status", payload)

    def score_text(self, project_id: int, content: str, format: str = "markdown",
                   query_id: int | None = None, persona_id: int | None = None) -> dict:
        payload: dict[str, Any] = {"project_id": project_id, "content": content, "format": format}
        if query_id:
            payload["query_id"] = query_id
        if persona_id:
            payload["persona_id"] = persona_id
        return self._post("/tools/content/score-text", payload)

    # ------------------------------------------------------------------
    # Write tools (stage 2A, 0 credits, need key right content:write)
    # ------------------------------------------------------------------

    def submit_article_draft(self, payload: dict) -> dict:
        return self._post("/tools/content/submit-draft", payload)

    def update_article(self, payload: dict) -> dict:
        return self._post("/tools/content/update-article", payload)

    def mcp_operation(self, operation_id: int) -> dict:
        return self._post("/tools/content/operation", {"operation_id": operation_id})

    def remember(self, payload: dict) -> dict:
        return self._post("/tools/memory/remember", payload)

    def import_meeting_preview(self, payload: dict) -> dict:
        return self._post("/tools/memory/meeting-import/preview", payload)

    def import_meeting_apply(self, payload: dict) -> dict:
        return self._post("/tools/memory/meeting-import/apply", payload)

    # ------------------------------------------------------------------
    # Free endpoints
    # ------------------------------------------------------------------

    def get_locations(self) -> dict:
        """Get available locations (no auth required)."""
        return self._get("/tools/locations")

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _require_key(self):
        if not self.api_key:
            raise APIError(
                f"No API key set. Set VISIBLYAI_API_KEY env var or sign up at {SIGNUP_URL}",
                status_code=401,
            )

    def _post(self, path: str, json_body: dict | None = None) -> dict:
        self._require_key()
        client = self._ensure_client()
        try:
            resp = client.post(path, json=json_body or {})
            return self._handle_response(resp)
        except httpx.HTTPError as e:
            raise APIError(f"HTTP error: {e}") from e

    def _get(self, path: str) -> dict:
        client = self._ensure_client()
        try:
            resp = client.get(path)
            return self._handle_response(resp)
        except httpx.HTTPError as e:
            raise APIError(f"HTTP error: {e}") from e

    def _handle_response(self, resp: httpx.Response) -> dict:
        if resp.status_code == 401:
            raise APIError(
                f"Invalid or missing API key. Get one at {SIGNUP_URL}",
                status_code=401,
            )
        if resp.status_code == 402:
            raise APIError(
                f"Insufficient credits. Top up at {CREDITS_URL}",
                status_code=402,
                credits_hint=True,
            )
        if resp.status_code == 429:
            message = "Rate limit exceeded. Please wait and try again."
            retry_after = resp.headers.get("Retry-After") if hasattr(resp, "headers") else None
            if retry_after:
                message = f"Rate limit exceeded. Retry after {retry_after}s. Please wait and try again."
            raise APIError(message, status_code=429)
        if resp.status_code >= 500:
            raise APIError(f"Server error ({resp.status_code})", status_code=resp.status_code)
        if resp.status_code >= 400:
            message, detail = self._parse_error_body(resp)
            raise APIError(message, status_code=resp.status_code, detail=detail)

        data = resp.json()
        if not data.get("success", True):
            raise APIError(data.get("error", "Unknown error"), status_code=resp.status_code)
        return data

    def _parse_error_body(self, resp: httpx.Response) -> tuple[str, dict | None]:
        """Turn a 4xx FastAPI error body into (message, detail-dict-or-None).

        Handles the three shapes the platform can send for `detail`:
        a dict (`{"error": ..., "message": ...}`), a plain string,
        or a pydantic validation-error list (`[{"msg": ..., ...}, ...]`).
        """
        try:
            body = resp.json()
        except Exception:
            body = None
        detail = body.get("detail") if isinstance(body, dict) else None

        if isinstance(detail, dict):
            message = f"{detail.get('error', 'error')}: {detail.get('message', '')}".strip(": ")
            return message, detail
        if isinstance(detail, str) and detail:
            return detail, None
        if isinstance(detail, list) and detail:
            messages = [str(item.get("msg", item)) if isinstance(item, dict) else str(item) for item in detail]
            return "; ".join(messages), None

        text = (getattr(resp, "text", "") or "")[:200]
        return text or f"HTTP error ({resp.status_code})", None
