"""Complete Visibly content lifecycle tools for Claude/MCP."""
from __future__ import annotations

import uuid
from typing import Any, Literal

from ..api_client import APIError, VisiblyAIClient
from ..config import SIGNUP_URL, get_api_key
from .paid_tools import _format_result, _handle_error


def _call(tool: str, payload: dict[str, Any]) -> str:
    api_key = get_api_key()
    if not api_key:
        return _handle_error(APIError(
            f"API key required. Set VISIBLYAI_API_KEY env var. Sign up at {SIGNUP_URL}", status_code=401,
        ))
    try:
        return _format_result(VisiblyAIClient(api_key).content_workflow(tool, payload))
    except Exception as exc:  # noqa: BLE001 - MCP returns structured errors to Claude
        return _handle_error(exc)


def list_articles(project_id: int, status: str = "all", limit: int = 25, offset: int = 0) -> str:
    """List project articles and metadata; no text is returned unless get_article is used."""
    return _call("list_articles", {"project_id": project_id, "status": status, "limit": limit, "offset": offset})


def get_content_query(query_id: int, project_id: int | None = None, include_draft: bool = False,
                      draft_offset: int = 0, draft_limit: int = 12000) -> str:
    """Read query context and optionally a bounded, paginated saved draft."""
    return _call("get_content_query", {"query_id": query_id, "project_id": project_id,
                                        "include_draft": include_draft, "draft_offset": draft_offset,
                                        "draft_limit": draft_limit})


def create_content_query(project_id: int, keyword: str, country: str = "de", language: str = "de",
                         persona_id: int | None = None) -> str:
    """Run paid SERP/content analysis and create a query. Requires content:write and spending:execute."""
    return _call("create_content_query", {"project_id": project_id, "keyword": keyword, "country": country,
                                           "language": language, "persona_id": persona_id})


def save_content_query_draft(query_id: int, expected_revision: int, content: str, title: str | None = None,
                             format: Literal["html", "markdown"] = "html", project_id: int | None = None) -> str:
    """Save an editor draft with revision CAS. The content is sanitized and nothing is published."""
    return _call("save_content_query_draft", {"query_id": query_id, "project_id": project_id,
                                              "expected_revision": expected_revision, "title": title,
                                              "content": content, "format": format})


def generate_article_from_query(query_id: int, project_id: int | None = None, improve: bool = False) -> str:
    """Queue AI article generation from a ready query; requires spending:execute."""
    return _call("generate_article_from_query", {"query_id": query_id, "project_id": project_id, "improve": improve})


def optimize_content_draft(query_id: int, kind: Literal["terms", "header_terms", "entities", "fanout", "structure",
                           "readability", "style"], draft_content: str, project_id: int | None = None) -> str:
    """Return a measured, paid optimization proposal. Does not save; requires spending:execute."""
    return _call("optimize_content_draft", {"query_id": query_id, "project_id": project_id,
                                             "kind": kind, "draft_content": draft_content})


def change_article_status(article_id: int, new_status: Literal["approved", "rejected", "archived", "queued"],
                          project_id: int | None = None) -> str:
    """Review or approve an article. Approval requires content:approve and triggers the normal CMS webhook."""
    return _call("change_article_status", {"article_id": article_id, "project_id": project_id,
                                            "new_status": new_status})


def edit_content_article(article_id: int, expected_revision: int, title: str | None = None,
                         content: str | None = None, format: Literal["html", "markdown"] | None = None,
                         meta_description: str | None = None, keywords: list[str] | None = None,
                         search_intent: str | None = None, recommended_page_type: str | None = None,
                         project_id: int | None = None, idempotency_key: str | None = None) -> str:
    """Full editor update for editable statuses. Creates a backup and checks the revision."""
    payload: dict[str, Any] = {"article_id": article_id, "expected_revision": expected_revision,
                               "idempotency_key": idempotency_key or uuid.uuid4().hex}
    for key, value in (("title", title), ("content", content), ("format", format),
                       ("meta_description", meta_description), ("keywords", keywords),
                       ("search_intent", search_intent), ("recommended_page_type", recommended_page_type),
                       ("project_id", project_id)):
        if value is not None:
            payload[key] = value
    return _call("edit_content_article", payload)


def regenerate_content_article(article_id: int, project_id: int | None = None) -> str:
    """Queue paid regeneration for an eligible article; requires spending:execute."""
    return _call("regenerate_content_article", {"article_id": article_id, "project_id": project_id})


def list_cms_connections(project_id: int) -> str:
    """List project CMS connections without returning credentials or webhook secrets; requires cms:manage."""
    return _call("list_cms_connections", {"project_id": project_id})


def create_cms_connection(project_id: int, cms_type: Literal["webhook", "wordpress", "shopify", "flask_blog"],
                           label: str = "", config: dict[str, str] | None = None,
                           webhook_url: str | None = None,
                           webhook_events: list[Literal["article.approved", "article.updated", "article.published"]] | None = None) -> str:
    """Create a CMS connection (cms:manage). A generated webhook secret is returned once and must be placed in the host secret store."""
    payload: dict[str, Any] = {"project_id": project_id, "cms_type": cms_type, "label": label,
                               "config": config or {}, "webhook_events": webhook_events or ["article.approved", "article.updated"]}
    if webhook_url:
        payload["webhook_url"] = webhook_url
    return _call("create_cms_connection", payload)


def test_cms_connection(project_id: int, connection_id: int) -> str:
    """Test CMS credentials and signed webhook delivery. Requires cms:manage."""
    return _call("test_cms_connection", {"project_id": project_id, "connection_id": connection_id})


def delete_cms_connection(project_id: int, connection_id: int) -> str:
    """Delete a CMS connection. Requires cms:manage."""
    return _call("delete_cms_connection", {"project_id": project_id, "connection_id": connection_id})


def create_contentpilot_key(project_id: int) -> str:
    """Create/rotate a project-scoped Pull API key. Plaintext is returned once; requires cms:manage."""
    return _call("create_contentpilot_key", {"project_id": project_id})


def get_contentpilot_key_status(project_id: int) -> str:
    """Read masked project Pull API key status. Requires cms:manage."""
    return _call("get_contentpilot_key_status", {"project_id": project_id})


def revoke_contentpilot_key(project_id: int) -> str:
    """Revoke the project's Pull API key. Requires cms:manage."""
    return _call("revoke_contentpilot_key", {"project_id": project_id})


def publish_article(article_id: int, project_id: int, connection_id: int,
                    publish_status: Literal["draft", "publish"] = "draft") -> str:
    """Publish an approved article to a push CMS. Requires content:publish; webhook pull CMS runs on approval instead."""
    return _call("publish_article", {"article_id": article_id, "project_id": project_id,
                                     "connection_id": connection_id, "publish_status": publish_status})


def update_cms_article(article_id: int, project_id: int, connection_id: int) -> str:
    """Write a saved revision back to its existing CMS entry. Requires content:publish."""
    return _call("update_cms_article", {"article_id": article_id, "project_id": project_id,
                                        "connection_id": connection_id})


def pull_live_article(article_id: int, project_id: int) -> str:
    """Read the current live page as a proposal; nothing is saved."""
    return _call("pull_live_article", {"article_id": article_id, "project_id": project_id})


def set_article_live_url(article_id: int, project_id: int, published_url: str | None) -> str:
    """Connect or disconnect the public page URL for editor pull and CMS writeback."""
    return _call("set_article_live_url", {"article_id": article_id, "project_id": project_id,
                                          "published_url": published_url})


def list_article_backups(article_id: int, project_id: int) -> str:
    """List saved editor and CMS versions without their content."""
    return _call("list_article_backups", {"article_id": article_id, "project_id": project_id})


def get_article_backup(backup_id: int, project_id: int, content_offset: int = 0,
                       content_limit: int = 12000) -> str:
    """Read one saved version in bounded content chunks."""
    return _call("get_article_backup", {"backup_id": backup_id, "project_id": project_id,
                                         "content_offset": content_offset, "content_limit": content_limit})


def restore_article_backup(backup_id: int, project_id: int, expected_revision: int) -> str:
    """Restore a saved version only if the current article revision still matches."""
    return _call("restore_article_backup", {"backup_id": backup_id, "project_id": project_id,
                                             "expected_revision": expected_revision})


def get_optimizer_settings(project_id: int) -> str:
    """Read optimizer/autolink settings, limits, and latest run."""
    return _call("get_optimizer_settings", {"project_id": project_id})


def update_optimizer_settings(project_id: int, enabled: bool | None = None, autolink_enabled: bool | None = None,
                              autolink_max_per_article: int | None = None) -> str:
    """Change scheduled optimizer or approval-time autolink settings. Requires content:write."""
    payload: dict[str, Any] = {"project_id": project_id}
    for key, value in (("enabled", enabled), ("autolink_enabled", autolink_enabled),
                       ("autolink_max_per_article", autolink_max_per_article)):
        if value is not None:
            payload[key] = value
    return _call("update_optimizer_settings", payload)


def run_content_optimizer(project_id: int) -> str:
    """Start a paid content optimizer run. Requires content:write and spending:execute."""
    return _call("run_content_optimizer", {"project_id": project_id})


def list_optimizer_suggestions(project_id: int, status: Literal["open", "done"] = "open",
                               kind: Literal["snippet", "link", "topic"] | None = None,
                               limit: int = 50, offset: int = 0) -> str:
    """List optimizer suggestions for review."""
    return _call("list_optimizer_suggestions", {"project_id": project_id, "status": status, "kind": kind,
                                                 "limit": limit, "offset": offset})


def approve_optimizer_suggestion(suggestion_id: int) -> str:
    """Apply an optimizer suggestion; requires content:approve."""
    return _call("approve_optimizer_suggestion", {"suggestion_id": suggestion_id})


def reject_optimizer_suggestion(suggestion_id: int) -> str:
    """Reject an optimizer suggestion; requires content:write."""
    return _call("reject_optimizer_suggestion", {"suggestion_id": suggestion_id})


def undo_optimizer_suggestion(suggestion_id: int) -> str:
    """Undo an applied optimizer suggestion; requires content:approve."""
    return _call("undo_optimizer_suggestion", {"suggestion_id": suggestion_id})


TOOLS = (
    get_content_query, create_content_query, save_content_query_draft,
    generate_article_from_query, optimize_content_draft, change_article_status,
    edit_content_article, regenerate_content_article,
    list_cms_connections, create_cms_connection, test_cms_connection, delete_cms_connection,
    create_contentpilot_key, get_contentpilot_key_status, revoke_contentpilot_key,
    publish_article, update_cms_article, pull_live_article, set_article_live_url,
    list_article_backups, get_article_backup, restore_article_backup,
    get_optimizer_settings, update_optimizer_settings,
    run_content_optimizer, list_optimizer_suggestions, approve_optimizer_suggestion,
    reject_optimizer_suggestion, undo_optimizer_suggestion,
)
