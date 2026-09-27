"""Verify the live MCP registry exposes every supported tool."""

from visiblyai_mcp.server import mcp
from visiblyai_mcp.tools import content_workflow_tools


EXPECTED_TOOLS = {
    # Free (8)
    "classify_keywords_simple",
    "seo_checklist",
    "seo_guidance",
    "get_google_guidelines",
    "analyze_url_structure",
    "get_account_info",
    "list_locations",
    "get_skill",
    # Paid (20)
    "classify_keywords_advanced",
    "get_traffic_snapshot",
    "get_historical_traffic",
    "get_keywords",
    "get_competitors",
    "get_backlinks",
    "get_referring_domains",
    "validate_keywords",
    "crawl_website",
    "onpage_analysis",
    "query_fanout",
    "check_links",
    "check_serp",
    "check_pagespeed",
    "audit_sitemap",
    "check_structured_data",
    "check_hreflang",
    "seo_agent",
    "seo_workflow",
    "query_knowledge_base",
    # Google/Project (5)
    "list_projects",
    "get_project",
    "get_google_connections",
    "query_search_console",
    "query_analytics",
    # Project data & content, read-only (15)
    "get_gsc_clusters",
    "get_cluster_keywords",
    "get_analytics_insights",
    "get_revenue_insights",
    "get_scorecard",
    "get_eeat_summary",
    "list_pages",
    "get_internal_links",
    "recall",
    "list_articles",
    "get_article",
    "list_content_queries",
    "get_content_briefing",
    "get_content_status",
    "score_text",
    "submit_article_draft",
    "update_article",
    "get_mcp_operation",
    "remember",
    "import_meeting_preview",
    "import_meeting_apply",
    # Full content workflow (29)
    "get_content_query",
    "create_content_query",
    "save_content_query_draft",
    "generate_article_from_query",
    "optimize_content_draft",
    "change_article_status",
    "edit_content_article",
    "regenerate_content_article",
    "list_cms_connections",
    "create_cms_connection",
    "test_cms_connection",
    "delete_cms_connection",
    "create_contentpilot_key",
    "get_contentpilot_key_status",
    "revoke_contentpilot_key",
    "publish_article",
    "update_cms_article",
    "pull_live_article",
    "set_article_live_url",
    "list_article_backups",
    "get_article_backup",
    "restore_article_backup",
    "get_optimizer_settings",
    "update_optimizer_settings",
    "run_content_optimizer",
    "list_optimizer_suggestions",
    "approve_optimizer_suggestion",
    "reject_optimizer_suggestion",
    "undo_optimizer_suggestion",
}


def _get_registered_tools() -> set[str]:
    """Read the registry after both decorator and dynamic tool registration."""
    return set(mcp._tool_manager._tools)


class TestServerRegistration:
    def test_all_tools_registered(self):
        registered = _get_registered_tools()
        missing = EXPECTED_TOOLS - registered
        extra = registered - EXPECTED_TOOLS
        assert not missing, f"Missing tools: {missing}"
        assert not extra, f"Unexpected tools: {extra}"

    def test_tool_count(self):
        registered = _get_registered_tools()
        assert len(registered) == 83, f"Expected 83 tools, found {len(registered)}: {registered}"

    def test_all_tools_have_docstrings(self):
        for name, tool in mcp._tool_manager._tools.items():
            assert tool.description, f"Tool '{name}' is missing a docstring"

    def test_no_duplicate_tool_names(self):
        names = [tool.__name__ for tool in content_workflow_tools.TOOLS]
        assert len(names) == len(set(names)), f"Duplicate content workflow tools: {names}"
