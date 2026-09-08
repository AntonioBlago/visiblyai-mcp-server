"""
Write tools (stage 2A): hand a draft over to visibly and edit drafts.
0 credits. Need an API key with the right `content:write` and a content write role.
"""

import json
import uuid

from ..api_client import APIError, VisiblyAIClient
from ..config import SIGNUP_URL, get_api_key
from .paid_tools import _format_result, _handle_error

__all__ = ["submit_article_draft", "update_article", "get_mcp_operation"]
FORMATS = ("html", "markdown")


def _require_key() -> VisiblyAIClient:
    api_key = get_api_key()
    if not api_key:
        raise APIError(f"API key required. Set VISIBLYAI_API_KEY env var. Sign up at {SIGNUP_URL}", status_code=401)
    return VisiblyAIClient(api_key)


def _bad(message: str) -> str:
    return json.dumps({"error": message})


def _call(method: str, *args) -> str:
    try:
        return _format_result(getattr(_require_key(), method)(*args))
    except Exception as e:  # noqa: BLE001 - every failure becomes a JSON error for the LLM
        return _handle_error(e)


def _with_key(method: str, payload: dict) -> str:
    key = payload.get("idempotency_key") or uuid.uuid4().hex
    payload["idempotency_key"] = key
    out = _call(method, payload)
    try:
        data = json.loads(out)
    except ValueError:
        return out
    data["idempotency_key"] = key  # retry with the same key replays instead of duplicating
    return json.dumps(data, ensure_ascii=False)


def submit_article_draft(project_id: int, title: str, content: str, keyword: str, format: str = "markdown",
                         idempotency_key: str | None = None, language: str = "de", country: str = "de",
                         persona_id: int | None = None, query_id: int | None = None,
                         expected_query_revision: int | None = None, expected_article_revision: int | None = None) -> str:
    """Hand a text over as an article draft (status draft). Returns operation, article and query ids plus revisions."""
    if not project_id or not (title or "").strip() or not (content or "").strip() or not (keyword or "").strip():
        return _bad("project_id, title, content and keyword are required")
    if format not in FORMATS:
        return _bad("format must be html or markdown")
    payload = {"project_id": project_id, "title": title, "content": content, "keyword": keyword, "format": format,
               "language": language, "country": country, "idempotency_key": idempotency_key}
    for name, value in (("persona_id", persona_id), ("query_id", query_id),
                        ("expected_query_revision", expected_query_revision),
                        ("expected_article_revision", expected_article_revision)):
        if value is not None:
            payload[name] = value
    return _with_key("submit_article_draft", payload)


def update_article(article_id: int, expected_revision: int, idempotency_key: str | None = None,
                   title: str | None = None, content: str | None = None, format: str | None = None,
                   meta_description: str | None = None, keywords: list[str] | None = None,
                   project_id: int | None = None) -> str:
    """Edit a draft article; expected_revision must match the current revision (from get_article)."""
    if not article_id or not expected_revision:
        return _bad("article_id and expected_revision are required")
    fields = {"title": title, "content": content, "meta_description": meta_description, "keywords": keywords}
    if all(v is None for v in fields.values()):
        return _bad("give at least one of title, content, meta_description, keywords")
    if content is not None and format not in FORMATS:
        return _bad("format (html|markdown) is required when content is given")
    payload = {"article_id": article_id, "expected_revision": expected_revision, "idempotency_key": idempotency_key}
    payload.update({k: v for k, v in fields.items() if v is not None})
    if format is not None:
        payload["format"] = format
    if project_id:
        payload["project_id"] = project_id
    return _with_key("update_article", payload)


def get_mcp_operation(operation_id: int) -> str:
    """Status and result of one of your write operations (pending, succeeded, failed)."""
    if not operation_id:
        return _bad("operation_id is required")
    return _call("mcp_operation", operation_id)
