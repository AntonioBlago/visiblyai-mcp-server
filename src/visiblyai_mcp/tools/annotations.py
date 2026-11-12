"""Single source of tool titles and MCP annotations (karte-257 K9.1, chatgpt-plugin K12.1).

Every tool registered by the package takes its ``title``, ``readOnlyHint``,
``destructiveHint`` and ``openWorldHint`` from ``TOOL_ANNOTATIONS``; nothing else
may hard-code them. The remote server reads the same values through
``tool_definitions()`` or this table.

Classification (E14, O3):
- readOnlyHint=True only for tools that create, change, publish or send nothing,
  write nothing locally and spend no credits.
- destructiveHint=True for every tool that deletes, overwrites (even with a
  backup), publishes, sends outward or revokes access.
- Tools that only create something without outside effect, and credit-spending
  reads, have both hints False.
In doubt readOnlyHint=False: a wrong True lets clients run the tool unasked.

openWorldHint (K12.1):
- True for tools that query arbitrary public domains, URLs, search results or
  web data (any domain or URL as input, live SERPs, public search market data).
- True as well for tools that send content outward to the user's configured
  CMS or social account (publish, CMS writeback, webhook, Buffer queue).
- False for tools limited to the connected account and its own projects, or to
  static content of the package or service.

``justification`` holds one English sentence per hint (read-only, destructive,
open-world) for the review portal (T4). It is not sent to MCP clients.
"""
from __future__ import annotations

from typing import Any, Callable, TypedDict

from mcp.types import ToolAnnotations


class ToolEntry(TypedDict):
    title: str
    readOnlyHint: bool
    destructiveHint: bool
    openWorldHint: bool
    justification: str


# (openWorldHint, sentence for the justification)
World = tuple[bool, str]

_OWN: World = (False, "Closed world: limited to the connected account and its own projects.")
_STATIC: World = (False, "Closed world: it returns only static content provided by the service.")
_LOCAL: World = (False, "Closed world: it runs locally on the given input only.")
_CATALOG: World = (False, "Closed world: it searches only the service's own indexed catalog.")
# Tools that send content outward count as open world (OpenAI review guidelines, boss decision 12.11.2026).
_SENDS_CMS: World = (True, "Open world: it sends content to the user's configured CMS, an external system.")
_SENDS_SOCIAL: World = (True, "Open world: it sends content to the user's configured social account, an external system.")
_OWN_LIVE_URL: World = (False, "Closed world: it only reads the live URL the project set for this article.")


def _open(what: str) -> World:
    return (True, f"Open world: it queries {what}.")


_OPEN_DOMAIN = _open("data about any public domain")
_OPEN_URL = _open("any public URL")
_OPEN_SERP = _open("live public search results for any keyword")
_OPEN_KEYWORDS = _open("public search market data for any keyword")
_OPEN_URL_INPUT: World = (True, "Open world: it accepts any public URL as input.")
_OPEN_TARGET = _open("any public domain or URL")

_NOT_DESTRUCTIVE = "Not destructive: it deletes or overwrites nothing."


def _entry(title: str, read_only: bool, destructive: bool, world: World, sentences: list[str]) -> ToolEntry:
    open_world, world_sentence = world
    return {
        "title": title,
        "readOnlyHint": read_only,
        "destructiveHint": destructive,
        "openWorldHint": open_world,
        "justification": " ".join([*sentences, world_sentence]),
    }


def _read(title: str, does: str, world: World = _OWN) -> ToolEntry:
    """Pure read without credits and without any write effect."""
    return _entry(title, True, False, world,
                  [f"Read-only: it {does}, spends no credits and writes nothing.", _NOT_DESTRUCTIVE])


def _paid(title: str, does: str, world: World = _OWN) -> ToolEntry:
    """Read that spends credits (O3, T3): not read-only, not destructive."""
    return _entry(title, False, False, world,
                  [f"Not read-only: it {does} and charges credits to the connected account.", _NOT_DESTRUCTIVE])


def _additive(title: str, does: str, world: World = _OWN) -> ToolEntry:
    """Creates something or spends credits, changes nothing that exists."""
    return _entry(title, False, False, world, [f"Not read-only: it {does}.", _NOT_DESTRUCTIVE])


def _destructive(title: str, does: str, why: str, world: World = _OWN) -> ToolEntry:
    """Deletes, overwrites, publishes, sends outward or revokes access."""
    return _entry(title, False, True, world, [f"Not read-only: it {does}.", f"Destructive: {why}."])


_ENTRIES: tuple[tuple[str, ToolEntry], ...] = (
    # Free tools, local or free metadata
    ("classify_keywords_simple", _read("Classify Keywords Locally",
                                       "classifies the given keywords with local rules", _LOCAL)),
    ("seo_checklist", _read("Get SEO Checklist", "returns a built-in SEO checklist", _STATIC)),
    ("seo_guidance", _read("Get SEO Best Practices", "returns built-in SEO best practices", _STATIC)),
    ("get_google_guidelines", _read("Get Google Search Guidelines",
                                    "returns a stored copy of the Google Search guidelines", _STATIC)),
    ("analyze_url_structure", _read("Analyze URL Structure",
                                    "inspects the structure of the given URL string", _OPEN_URL_INPUT)),
    ("get_account_info", _read("Get Account Credits and Tier", "returns the account's credit balance and tier")),
    ("list_locations", _read("List Search Data Locations",
                             "returns the supported search data locations", _STATIC)),
    ("get_skill", _read("Get SEO Workflow Skill", "returns a stored SEO workflow skill", _STATIC)),
    # Paid reads: spend credits, therefore not read-only (O3)
    ("classify_keywords_advanced", _paid("Classify Keywords with Search Intent",
                                         "classifies keywords by search intent", _OPEN_KEYWORDS)),
    ("get_traffic_snapshot", _paid("Get Domain Traffic Snapshot",
                                   "reads traffic estimates of a domain", _OPEN_DOMAIN)),
    ("get_historical_traffic", _paid("Get Historical Domain Traffic",
                                     "reads historical traffic estimates of a domain", _OPEN_DOMAIN)),
    ("get_keywords", _paid("Get Domain Ranking Keywords", "reads the ranking keywords of a domain", _OPEN_DOMAIN)),
    ("get_competitors", _paid("Get Domain Competitors",
                              "reads competitor domains by keyword overlap", _OPEN_DOMAIN)),
    ("get_backlinks", _paid("Get Backlink Profile", "reads the backlink profile of a domain", _OPEN_DOMAIN)),
    ("get_referring_domains", _paid("Get Referring Domains",
                                    "reads the referring domains of a domain", _OPEN_DOMAIN)),
    ("validate_keywords", _paid("Validate Keyword Search Volume",
                                "reads search volume, competition and CPC of keywords", _OPEN_KEYWORDS)),
    ("crawl_website", _paid("Crawl Website Pages", "crawls the pages of a website", _OPEN_URL)),
    ("onpage_analysis", _paid("Run OnPage SEO Analysis", "analyzes the on-page SEO of a page", _OPEN_URL)),
    ("check_serp", _paid("Check Live Google SERP", "reads the live Google results of a keyword", _OPEN_SERP)),
    ("query_fanout", _paid("Analyze Query Fanout Coverage",
                           "measures the AI query coverage of a page", _OPEN_URL)),
    ("check_pagespeed", _paid("Check PageSpeed and Core Web Vitals",
                              "measures PageSpeed and Core Web Vitals of a page", _OPEN_URL)),
    ("audit_sitemap", _paid("Audit XML Sitemap", "audits the XML sitemap of a domain", _OPEN_DOMAIN)),
    ("check_structured_data", _paid("Check Structured Data",
                                    "validates the structured data on a page", _OPEN_URL)),
    ("check_hreflang", _paid("Check Hreflang Tags", "validates the hreflang tags of a page", _OPEN_URL)),
    ("check_links", _paid("Check Page Links", "checks the status of all links on a page", _OPEN_URL)),
    ("seo_agent", _paid("Run SEO Agent", "runs an SEO agent task", _OPEN_TARGET)),
    ("seo_workflow", _paid("Run SEO Workflow Report", "runs a multi-step SEO report", _OPEN_DOMAIN)),
    ("query_knowledge_base", _paid("Search SEO Knowledge Base",
                                   "searches the indexed SEO knowledge base", _CATALOG)),
    # Google and project tools, 0 credits
    ("list_projects", _read("List Projects", "lists the account's projects")),
    ("get_project", _read("Get Project Details", "reads the details of one project")),
    ("get_google_connections", _read("Get Google Connections", "lists the account's Google connections")),
    ("query_search_console", _read("Query Search Console", "reads the account's own Search Console data")),
    ("query_analytics", _read("Query Google Analytics", "reads the account's own Google Analytics data")),
    # Project data, 0 credits, read-only
    ("get_gsc_clusters", _read("Get Search Console Topic Clusters",
                               "reads the stored Search Console topic clusters of a project")),
    ("get_cluster_keywords", _read("Get Cluster Keywords", "reads the keywords of one stored topic cluster")),
    ("get_analytics_insights", _read("Get Analytics Insights", "reads the stored analytics insights of a project")),
    ("get_revenue_insights", _read("Get Organic Revenue Insights",
                                   "reads the organic revenue attribution of a project")),
    ("get_scorecard", _read("Get KPI Scorecard", "reads the KPI scorecard of a project")),
    ("get_eeat_summary", _read("Get EEAT Summary", "reads the stored EEAT summary of a project")),
    ("list_pages", _read("List Sitemap Pages", "lists the stored sitemap pages of a project")),
    # url is a lookup key inside the project's stored crawl, not a fetch target.
    ("get_internal_links", _read("Get Internal Link Graph", "reads the stored internal link graph of a project")),
    ("get_site_health", _read("Get Site Health Score", "reads the stored site health score of a project")),
    # url is a lookup key inside the project's stored crawl, not a fetch target.
    ("get_page_facts", _read("Get Crawl Facts for a Page", "reads the stored crawl facts of one project page")),
    ("list_site_findings", _read("List Site Crawl Findings", "lists the stored crawl findings of a project")),
    ("recall", _read("Recall Visibly Brain Facts", "reads facts the account stored earlier")),
    ("list_articles", _read("List Project Articles", "lists the article metadata of a project")),
    ("get_article", _read("Read Article Content", "reads one article of a project")),
    ("list_content_queries", _read("List Content Queries", "lists the content queries of a project")),
    ("get_content_briefing", _read("Get Content Briefing", "reads the briefing of a finished content query")),
    ("get_content_status", _read("Get Content Analysis Status", "reads the analysis status of a content query")),
    ("score_text", _read("Score Text Quality", "scores the given text against the project's rules")),
    ("get_mcp_operation", _read("Get Write Operation Status", "reads the status of one own write operation")),
    ("list_social_queue", _read("List Social Post Queue", "lists the project's own social posts")),
    # Write tools (content_write_tools)
    # With query_id the draft replaces the existing draft article of that query.
    ("submit_article_draft", _destructive("Submit Article Draft", "saves an article draft",
                                          "with query_id it replaces the existing draft article of that query")),
    ("update_article", _destructive("Update Draft Article", "edits a draft article",
                                    "it overwrites the text of the article")),
    ("remember", _additive("Store Fact in Visibly Brain", "stores a fact in the account memory")),
    ("import_meeting_preview", _paid("Preview Meeting Transcript Import",
                                     "turns a transcript into an import proposal")),
    # Upserts brand profile fields of the project, i.e. overwrites them.
    ("import_meeting_apply", _destructive("Apply Meeting Import Selection", "writes the reviewed import selection",
                                          "it overwrites brand profile fields of the project")),
    # approve=true queues the post for Buffer, i.e. sends it outward.
    ("create_social_post", _destructive("Create Social Post", "creates a social post",
                                        "with approve=true it queues the post for publishing via Buffer",
                                        _SENDS_SOCIAL)),
    ("approve_social_post", _destructive("Approve Social Post for Publishing", "approves a social post",
                                         "the approved post is handed to Buffer for publishing", _SENDS_SOCIAL)),
    ("delete_social_post", _destructive("Delete Social Post", "deletes a social post",
                                        "it removes the post and withdraws channels already scheduled")),
    # Content workflow (content_workflow_tools.TOOLS)
    ("get_content_query", _read("Get Content Query", "reads a content query and its saved draft")),
    ("create_content_query", _additive("Create Content Query",
                                       "runs a paid SERP analysis and creates a content query", _OPEN_SERP)),
    ("save_content_query_draft", _destructive("Save Editor Draft", "saves an editor draft",
                                              "it replaces the saved draft of the query")),
    # improve=true replaces the saved draft (a version snapshot is kept).
    ("generate_article_from_query", _destructive("Generate Article from Query", "queues paid article generation",
                                                 "with improve=true it replaces the saved draft, keeping a snapshot")),
    ("optimize_content_draft", _paid("Optimize Content Draft",
                                     "returns an optimization proposal without saving it")),
    ("change_article_status", _destructive("Change Article Status", "changes the review status of an article",
                                           "approval triggers the CMS webhook of the project", _SENDS_CMS)),
    ("edit_content_article", _destructive("Edit Article in Editor", "updates an article in the editor",
                                          "it overwrites the article text, keeping a backup")),
    ("regenerate_content_article", _destructive("Regenerate Article", "queues paid regeneration of an article",
                                                "it replaces the text of the article")),
    ("list_cms_connections", _read("List CMS Connections", "lists the project's CMS connections without secrets")),
    ("create_cms_connection", _additive("Create CMS Connection", "creates a CMS connection for the project")),
    # E15: sends a signed webhook to the CMS.
    ("test_cms_connection", _destructive("Test CMS Connection", "tests a CMS connection",
                                         "it sends a signed webhook to the CMS of the project", _SENDS_CMS)),
    ("delete_cms_connection", _destructive("Delete CMS Connection", "deletes a CMS connection",
                                           "the connection is removed for good")),
    # E15: rotating invalidates the previous key.
    ("create_contentpilot_key", _destructive("Create or Rotate Pull API Key", "creates or rotates the Pull API key",
                                             "rotating invalidates the previous key")),
    ("get_contentpilot_key_status", _read("Get Pull API Key Status", "reads the masked Pull API key status")),
    ("revoke_contentpilot_key", _destructive("Revoke Pull API Key", "revokes the Pull API key",
                                             "the CMS loses access with that key")),
    ("publish_article", _destructive("Publish Article to CMS", "publishes an approved article",
                                     "it puts the article live on the CMS of the project", _SENDS_CMS)),
    ("update_cms_article", _destructive("Update Live CMS Article", "updates the live CMS article",
                                        "it overwrites the content of the live page", _SENDS_CMS)),
    ("get_article_workflow", _read("Get Article Publishing Workflow",
                                   "reads editor links and the CMS transfer status of an article")),
    ("pull_live_article", _read("Fetch Live Article Content",
                                "fetches the live article for comparison without saving", _OWN_LIVE_URL)),
    ("set_article_live_url", _destructive("Set Article Live URL", "sets or clears the live URL of an article",
                                          "it replaces the stored URL used for CMS writeback")),
    ("list_article_backups", _read("List Article Backups", "lists the saved versions of an article")),
    ("get_article_backup", _read("Get Article Backup", "reads one saved version of an article")),
    ("restore_article_backup", _destructive("Restore Article Backup", "restores a saved article version",
                                            "it overwrites the current article text")),
    ("get_optimizer_settings", _read("Get Optimizer Settings", "reads the optimizer settings of a project")),
    ("update_optimizer_settings", _destructive("Update Optimizer Settings", "changes the optimizer settings",
                                               "it overwrites the current optimizer settings")),
    ("run_content_optimizer", _additive("Run Content Optimizer", "starts a paid content optimizer run")),
    ("list_optimizer_suggestions", _read("List Optimizer Suggestions",
                                         "lists the optimizer suggestions of a project")),
    ("approve_optimizer_suggestion", _destructive("Approve Optimizer Suggestion", "applies an optimizer suggestion",
                                                  "it changes article content and can write back to the CMS")),
    # Changes the state of an existing suggestion.
    ("reject_optimizer_suggestion", _destructive("Reject Optimizer Suggestion", "rejects an optimizer suggestion",
                                                 "it changes the state of the suggestion for good")),
    ("undo_optimizer_suggestion", _destructive("Undo Optimizer Suggestion", "undoes an applied suggestion",
                                               "it rewrites the article and its CMS page")),
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
                                       destructiveHint=entry["destructiveHint"],
                                       openWorldHint=entry["openWorldHint"]),
    }


def annotated_tool(mcp: Any) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator factory: register a function on ``mcp`` with its table entry."""

    def register(fn: Callable[..., Any]) -> Callable[..., Any]:
        return mcp.tool(**tool_options(fn.__name__))(fn)

    return register
