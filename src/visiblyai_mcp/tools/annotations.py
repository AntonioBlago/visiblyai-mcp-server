"""Single source of tool titles and MCP annotations (contract karte-257, K9.1).

Every tool registered by the package takes its ``title``, ``readOnlyHint`` and
``destructiveHint`` from ``TOOL_ANNOTATIONS``; nothing else may hard-code them.
The remote server reads the same values through ``tool_definitions()``.

Classification (E14, O3):
- readOnlyHint=True only for tools that create, change, publish or send nothing,
  write nothing locally and spend no credits.
- destructiveHint=True for every tool that deletes, overwrites (even with a
  backup), publishes, sends outward or revokes access.
- Tools that only create something without outside effect, and credit-spending
  reads, have both hints False.
In doubt readOnlyHint=False: a wrong True lets clients run the tool unasked.
"""
from __future__ import annotations

from typing import Any, Callable, TypedDict

from mcp.types import ToolAnnotations


class ToolEntry(TypedDict):
    title: str
    readOnlyHint: bool
    destructiveHint: bool


def _read(title: str) -> ToolEntry:
    """Pure read without credits and without any write effect."""
    return {"title": title, "readOnlyHint": True, "destructiveHint": False}


def _additive(title: str) -> ToolEntry:
    """Creates something or spends credits, changes nothing that exists."""
    return {"title": title, "readOnlyHint": False, "destructiveHint": False}


def _destructive(title: str) -> ToolEntry:
    """Deletes, overwrites, publishes, sends outward or revokes access."""
    return {"title": title, "readOnlyHint": False, "destructiveHint": True}


_ENTRIES: tuple[tuple[str, ToolEntry], ...] = (
    # Free tools, local or free metadata
    ("classify_keywords_simple", _read("Classify Keywords Locally")),
    ("seo_checklist", _read("Get SEO Checklist")),
    ("seo_guidance", _read("Get SEO Best Practices")),
    ("get_google_guidelines", _read("Get Google Search Guidelines")),
    ("analyze_url_structure", _read("Analyze URL Structure")),
    ("get_account_info", _read("Get Account Credits and Tier")),
    ("list_locations", _read("List Search Data Locations")),
    ("get_skill", _read("Get SEO Workflow Skill")),
    # Paid reads: spend credits, therefore not read-only (O3)
    ("classify_keywords_advanced", _additive("Classify Keywords with Search Intent")),
    ("get_traffic_snapshot", _additive("Get Domain Traffic Snapshot")),
    ("get_historical_traffic", _additive("Get Historical Domain Traffic")),
    ("get_keywords", _additive("Get Domain Ranking Keywords")),
    ("get_competitors", _additive("Get Domain Competitors")),
    ("get_backlinks", _additive("Get Backlink Profile")),
    ("get_referring_domains", _additive("Get Referring Domains")),
    ("validate_keywords", _additive("Validate Keyword Search Volume")),
    ("crawl_website", _additive("Crawl Website Pages")),
    ("onpage_analysis", _additive("Run OnPage SEO Analysis")),
    ("check_serp", _additive("Check Live Google SERP")),
    ("query_fanout", _additive("Analyze Query Fanout Coverage")),
    ("check_pagespeed", _additive("Check PageSpeed and Core Web Vitals")),
    ("audit_sitemap", _additive("Audit XML Sitemap")),
    ("check_structured_data", _additive("Check Structured Data")),
    ("check_hreflang", _additive("Check Hreflang Tags")),
    ("check_links", _additive("Check Page Links")),
    ("seo_agent", _additive("Run SEO Agent")),
    ("seo_workflow", _additive("Run SEO Workflow Report")),
    ("query_knowledge_base", _additive("Search SEO Knowledge Base")),
    # Google and project tools, 0 credits
    ("list_projects", _read("List Projects")),
    ("get_project", _read("Get Project Details")),
    ("get_google_connections", _read("Get Google Connections")),
    ("query_search_console", _read("Query Search Console")),
    ("query_analytics", _read("Query Google Analytics")),
    # Project data, 0 credits, read-only
    ("get_gsc_clusters", _read("Get Search Console Topic Clusters")),
    ("get_cluster_keywords", _read("Get Cluster Keywords")),
    ("get_analytics_insights", _read("Get Analytics Insights")),
    ("get_revenue_insights", _read("Get Organic Revenue Insights")),
    ("get_scorecard", _read("Get KPI Scorecard")),
    ("get_eeat_summary", _read("Get EEAT Summary")),
    ("list_pages", _read("List Sitemap Pages")),
    ("get_internal_links", _read("Get Internal Link Graph")),
    ("get_site_health", _read("Get Site Health Score")),
    ("get_page_facts", _read("Get Crawl Facts for a Page")),
    ("list_site_findings", _read("List Site Crawl Findings")),
    ("recall", _read("Recall Visibly Brain Facts")),
    ("list_articles", _read("List Project Articles")),
    ("get_article", _read("Read Article Content")),
    ("list_content_queries", _read("List Content Queries")),
    ("get_content_briefing", _read("Get Content Briefing")),
    ("get_content_status", _read("Get Content Analysis Status")),
    ("score_text", _read("Score Text Quality")),
    ("get_mcp_operation", _read("Get Write Operation Status")),
    ("list_social_queue", _read("List Social Post Queue")),
    # Write tools (content_write_tools)
    # With query_id the draft replaces the existing draft article of that query.
    ("submit_article_draft", _destructive("Submit Article Draft")),
    ("update_article", _destructive("Update Draft Article")),
    ("remember", _additive("Store Fact in Visibly Brain")),
    ("import_meeting_preview", _additive("Preview Meeting Transcript Import")),
    # Upserts brand profile fields of the project, i.e. overwrites them.
    ("import_meeting_apply", _destructive("Apply Meeting Import Selection")),
    # approve=true queues the post for Buffer, i.e. sends it outward.
    ("create_social_post", _destructive("Create Social Post")),
    ("approve_social_post", _destructive("Approve Social Post for Publishing")),
    ("delete_social_post", _destructive("Delete Social Post")),
    # Content workflow (content_workflow_tools.TOOLS)
    ("get_content_query", _read("Get Content Query")),
    ("create_content_query", _additive("Create Content Query")),
    ("save_content_query_draft", _destructive("Save Editor Draft")),
    # improve=true replaces the saved draft (a version snapshot is kept).
    ("generate_article_from_query", _destructive("Generate Article from Query")),
    ("optimize_content_draft", _additive("Optimize Content Draft")),
    ("change_article_status", _destructive("Change Article Status")),
    ("edit_content_article", _destructive("Edit Article in Editor")),
    ("regenerate_content_article", _destructive("Regenerate Article")),
    ("list_cms_connections", _read("List CMS Connections")),
    ("create_cms_connection", _additive("Create CMS Connection")),
    # E15: sends a signed webhook to the CMS.
    ("test_cms_connection", _destructive("Test CMS Connection")),
    ("delete_cms_connection", _destructive("Delete CMS Connection")),
    # E15: rotating invalidates the previous key.
    ("create_contentpilot_key", _destructive("Create or Rotate Pull API Key")),
    ("get_contentpilot_key_status", _read("Get Pull API Key Status")),
    ("revoke_contentpilot_key", _destructive("Revoke Pull API Key")),
    ("publish_article", _destructive("Publish Article to CMS")),
    ("update_cms_article", _destructive("Update Live CMS Article")),
    ("get_article_workflow", _read("Get Article Publishing Workflow")),
    ("pull_live_article", _read("Fetch Live Article Content")),
    ("set_article_live_url", _destructive("Set Article Live URL")),
    ("list_article_backups", _read("List Article Backups")),
    ("get_article_backup", _read("Get Article Backup")),
    ("restore_article_backup", _destructive("Restore Article Backup")),
    ("get_optimizer_settings", _read("Get Optimizer Settings")),
    ("update_optimizer_settings", _destructive("Update Optimizer Settings")),
    ("run_content_optimizer", _additive("Run Content Optimizer")),
    ("list_optimizer_suggestions", _read("List Optimizer Suggestions")),
    ("approve_optimizer_suggestion", _destructive("Approve Optimizer Suggestion")),
    # Changes the state of an existing suggestion.
    ("reject_optimizer_suggestion", _destructive("Reject Optimizer Suggestion")),
    ("undo_optimizer_suggestion", _destructive("Undo Optimizer Suggestion")),
)


def _build_table(entries: tuple[tuple[str, ToolEntry], ...]) -> dict[str, ToolEntry]:
    """One entry per tool name; a duplicate name fails at import instead of silently winning."""
    table: dict[str, ToolEntry] = {}
    for name, entry in entries:
        if name in table:
            raise ValueError(f"tool {name!r} has more than one entry in TOOL_ANNOTATIONS")
        table[name] = entry
    return table


TOOL_ANNOTATIONS: dict[str, ToolEntry] = _build_table(_ENTRIES)


def tool_options(name: str) -> dict[str, Any]:
    """Keyword arguments for ``FastMCP.tool`` / ``Tool.from_function``.

    Raises ``KeyError`` for a name without entry, so an unannotated tool breaks
    the import instead of shipping without hints.
    """
    try:
        entry = TOOL_ANNOTATIONS[name]
    except KeyError:
        raise KeyError(f"tool {name!r} has no entry in visiblyai_mcp.tools.annotations.TOOL_ANNOTATIONS") from None
    return {
        "title": entry["title"],
        "annotations": ToolAnnotations(readOnlyHint=entry["readOnlyHint"],
                                       destructiveHint=entry["destructiveHint"]),
    }


def annotated_tool(mcp: Any) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator factory: register a function on ``mcp`` with its table entry."""

    def register(fn: Callable[..., Any]) -> Callable[..., Any]:
        return mcp.tool(**tool_options(fn.__name__))(fn)

    return register
