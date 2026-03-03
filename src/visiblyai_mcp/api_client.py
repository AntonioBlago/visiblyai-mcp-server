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

    def __init__(self, message: str, status_code: int = 0, credits_hint: bool = False):
        self.status_code = status_code
        self.credits_hint = credits_hint
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

    def check_links(self, url: str) -> dict:
        return self._post("/tools/check-links", {"url": url})

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
            raise APIError("Rate limit exceeded. Please wait and try again.", status_code=429)
        if resp.status_code >= 500:
            raise APIError(f"Server error ({resp.status_code})", status_code=resp.status_code)

        data = resp.json()
        if not data.get("success", True):
            raise APIError(data.get("error", "Unknown error"), status_code=resp.status_code)
        return data
