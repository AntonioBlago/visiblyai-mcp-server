"""
VisiblyAI MCP Server - SEO tools for Claude Code.

Free tools run locally (keyword classification, checklists, SEO guidance).
Paid tools proxy to the VisiblyAI platform API with credit billing.

Usage:
    pip install visiblyai-mcp-server
    claude mcp add --transport stdio \\
        --env VISIBLYAI_API_KEY=lc_your_key \\
        visiblyai -- visiblyai-mcp-server
"""

from mcp.server.fastmcp import FastMCP

from .tools import content_write_tools, free_tools, paid_tools, project_tools

mcp = FastMCP(
    "VisiblyAI SEO Tools",
    instructions=(
        "Professional SEO tools powered by VisiblyAI. "
        "Free: keyword classifier, SEO checklists, best practices. "
        "Paid: traffic analysis, keyword research, backlinks, competitor analysis, "
        "OnPage SEO audit, link checking, SEO agents, SEO workflows "
        "(requires API key + credits). "
        "Google: Search Console queries, Analytics reports, project management "
        "(requires API key, 0 credits). "
        "Project data & content (read-only, 0 credits): GSC clusters, GA4 insights, "
        "revenue, scorecard, EEAT, pages, internal links, articles, content queries, "
        "briefings, text scoring, memory recall. Nothing is written back."
    ),
)

# ---------------------------------------------------------------------------
# Free Tools (local, no API key needed)
# ---------------------------------------------------------------------------

@mcp.tool()
def classify_keywords_simple(
    keywords: list[str],
    brand_name: str = "",
    brand_variations: list[str] | None = None,
    product_keywords: list[str] | None = None,
    competitors: list[dict] | None = None,
) -> str:
    """Classify keywords using local regex patterns (fast, free, offline).

    Returns intent (transactional/commercial/informational/navigational/local),
    funnel stage (TOFU/MOFU/BOFU), brand type, conversion score (0-100), topic.
    Supports German and English.

    For DataForSEO-enhanced intent detection use classify_keywords_advanced (paid).

    Free tool - no API key or credits required.
    """
    return free_tools.classify_keywords(
        keywords, brand_name, brand_variations, product_keywords, competitors
    )


@mcp.tool()
def seo_checklist(
    checklist_type: str = "general",
    language: str = "en",
) -> str:
    """Get an SEO checklist. Types: general, blog, ecommerce, discover, backlink, all.

    Returns actionable checklists with specific items to verify.
    Available in English (en) and German (de).

    Free tool - no API key or credits required.
    """
    return free_tools.seo_checklist(checklist_type, language)


@mcp.tool()
def seo_guidance(topic: str) -> str:
    """Get SEO best practices on a topic. Use topic='list' to see all topics.

    Topics: title_tags, meta_descriptions, heading_structure, internal_linking,
    core_web_vitals, eeat, keyword_research, schema_markup, image_optimization, local_seo.

    Free tool - no API key or credits required.
    """
    return free_tools.seo_guidance(topic)


@mcp.tool()
def get_google_guidelines(category: str = "list") -> str:
    """Get official Google Search developer guidelines (scraped weekly from developers.google.com).

    Use category='list' to see all available categories. Available categories:
    fundamentals, content, crawling, sitemaps, structured_data, performance,
    ranking, updates, monitoring, snippets, guidelines.

    Free tool - no API key or credits required.
    """
    return free_tools.get_google_guidelines(category)


@mcp.tool()
def analyze_url_structure(url: str) -> str:
    """Analyze a URL for SEO-friendliness. Checks length, structure, and common issues.

    Free tool - no API key or credits required.
    """
    return free_tools.analyze_url_structure(url)


@mcp.tool()
def get_account_info() -> str:
    """Check VisiblyAI account status, credit balance, and subscription tier.

    Shows available free tools if no API key is set.
    """
    return free_tools.get_account_info()


@mcp.tool()
def list_locations() -> str:
    """List available countries/locations for SEO data queries.

    Free tool - no API key or credits required.
    """
    return free_tools.list_locations()


@mcp.tool()
def get_skill(name: str) -> str:
    """Get an SEO workflow skill with step-by-step methodology and CTR models.

    Skills: seo-audit, keyword-research, competitor-analysis,
    traffic-analysis, gsc-report, site-health-check.
    Use name='list' to see all available skills.

    Free tool - no API key or credits required.
    """
    return free_tools.get_skill(name)


# ---------------------------------------------------------------------------
# Paid Tools (require VISIBLYAI_API_KEY + credits)
# ---------------------------------------------------------------------------

@mcp.tool()
def classify_keywords_advanced(
    keywords: list[str],
    brand_name: str = "",
    brand_variations: list[str] | None = None,
    product_keywords: list[str] | None = None,
    competitors: list[dict] | None = None,
    language: str = "German",
    location: str = "Germany",
) -> str:
    """Classify keywords using DataForSEO Search Intent API + regex classifier (paid).

    Combines DataForSEO search intent (main_intent, secondary_intents) with
    local regex classification (brand type, funnel stage, topic, conversion score).
    More accurate than classify_keywords_simple for intent detection.
    Credits: dynamic (based on keyword count).

    Requires VISIBLYAI_API_KEY. Use get_account_info to check your balance.
    """
    return paid_tools.classify_keywords_advanced(
        keywords, brand_name, brand_variations, product_keywords, competitors, language, location
    )


@mcp.tool()
def get_traffic_snapshot(domain: str, location: str = "Germany") -> str:
    """Get current organic and paid traffic for a domain. Credits: varies.

    Requires VISIBLYAI_API_KEY. Use get_account_info to check your balance.
    """
    return paid_tools.get_traffic_snapshot(domain, location)


@mcp.tool()
def get_historical_traffic(
    domain: str, location: str = "Germany",
    date_from: str = "", date_to: str = "",
) -> str:
    """Get historical traffic trends (up to 5 years). Credits: varies.

    Requires VISIBLYAI_API_KEY. Use get_account_info to check your balance.
    """
    return paid_tools.get_historical_traffic(domain, location, date_from, date_to)


@mcp.tool()
def get_keywords(domain: str, location: str = "Germany", limit: int = 100) -> str:
    """Get top ranking keywords for a domain with volume, position, URL. Credits: varies.

    Requires VISIBLYAI_API_KEY. Use get_account_info to check your balance.
    """
    return paid_tools.get_keywords(domain, location, limit)


@mcp.tool()
def get_competitors(
    domain: str, location: str = "Germany",
    language: str = "German", limit: int = 10,
) -> str:
    """Get competitor domains based on keyword overlap. Credits: varies.

    Requires VISIBLYAI_API_KEY. Use get_account_info to check your balance.
    """
    return paid_tools.get_competitors(domain, location, language, limit)


@mcp.tool()
def get_backlinks(domain: str, location: str = "Germany", limit: int = 100) -> str:
    """Get backlink profile: Domain Rating, total backlinks, referring domains. Credits: varies.

    Requires VISIBLYAI_API_KEY. Use get_account_info to check your balance.
    """
    return paid_tools.get_backlinks(domain, location, limit)


@mcp.tool()
def get_referring_domains(domain: str, location: str = "Germany", limit: int = 50) -> str:
    """Get referring domains with authority scores. Credits: varies.

    Requires VISIBLYAI_API_KEY. Use get_account_info to check your balance.
    """
    return paid_tools.get_referring_domains(domain, location, limit)


@mcp.tool()
def validate_keywords(
    keywords: list[str], location: str = "Germany",
    language: str = "German", top_n: int = 50,
) -> str:
    """Validate keywords: get search volume, competition, CPC. Credits: varies.

    Requires VISIBLYAI_API_KEY. Use get_account_info to check your balance.
    """
    return paid_tools.validate_keywords(keywords, location, language, top_n)


@mcp.tool()
def crawl_website(url: str, keyword: str = "", max_pages: int = 1) -> str:
    """Crawl a website + optional 24-point OnPage SEO analysis. Credits: 15-60.

    Requires VISIBLYAI_API_KEY. Use get_account_info to check your balance.
    """
    return paid_tools.crawl_website(url, keyword, max_pages)


@mcp.tool()
def onpage_analysis(url: str, keyword: str) -> str:
    """Run 24-point OnPage SEO analysis: keyword, content, technical checks. Credits: 15.

    Requires VISIBLYAI_API_KEY. Use get_account_info to check your balance.
    """
    return paid_tools.onpage_analysis(url, keyword)


@mcp.tool()
def check_serp(keyword: str, location: str = "Germany", language: str = "German", depth: int = 10) -> str:
    """Check live Google SERP for a keyword. See who ranks, what content types dominate, and SERP features present.

    Use for: competitive analysis, content gap detection, SERP intent analysis.
    Credits: 15.
    """
    return paid_tools.check_serp(keyword, location, language, depth)


@mcp.tool()
def query_fanout(
    url: str,
    keyword: str,
    data_source: str = "dataforseo",
    gsc_property: str | None = None,
    language: str = "en",
) -> str:
    """Run Query Fan-Out AI Coverage Analysis for a URL + seed keyword.

    Gemini Grounding generates fan-out sub-queries; page content is crawled and
    topic-extracted; semantic matching (embeddings) scores coverage and surfaces gaps.
    GSC or DataForSEO ranking keywords feed into the coverage calculation.

    Use for: content gap analysis, AI-search coverage, sub-topic coverage for a page.
    Credits: dynamic (~3-5 depending on data_source).
    """
    return paid_tools.query_fanout(url, keyword, data_source, gsc_property, language)


@mcp.tool()
def check_pagespeed(url: str, strategy: str = "mobile") -> str:
    """Check PageSpeed and Core Web Vitals for a URL. Returns performance, accessibility, SEO scores, LCP, CLS, TBT, and optimization opportunities. Credits: 5.

    Requires VISIBLYAI_API_KEY. Use get_account_info to check your balance.
    """
    return paid_tools.check_pagespeed(url, strategy)


@mcp.tool()
def audit_sitemap(domain: str) -> str:
    """Audit a site's XML sitemap: total URLs, duplicates, broken links, lastmod coverage. Credits: 20.

    Requires VISIBLYAI_API_KEY. Use get_account_info to check your balance.
    """
    return paid_tools.audit_sitemap(domain)


@mcp.tool()
def check_structured_data(url: str) -> str:
    """Validate JSON-LD and microdata on a URL: schema types, required fields, errors. Credits: 5.

    Requires VISIBLYAI_API_KEY. Use get_account_info to check your balance.
    """
    return paid_tools.check_structured_data(url)


@mcp.tool()
def check_hreflang(url: str) -> str:
    """Validate hreflang annotations: x-default, language codes, broken targets, bidirectional linking. Credits: 10.

    Requires VISIBLYAI_API_KEY. Use get_account_info to check your balance.
    """
    return paid_tools.check_hreflang(url)


@mcp.tool()
def check_links(url: str) -> str:
    """Check all links on a page for broken/redirect status. Credits: 20.

    Requires VISIBLYAI_API_KEY. Use get_account_info to check your balance.
    """
    return paid_tools.check_links(url)


@mcp.tool()
def seo_agent(
    task: str,
    agent: str = "",
    domain: str = "",
    url: str = "",
    keyword: str = "",
    content: str = "",
    params: dict | None = None,
    project_id: int = 0,
) -> str:
    """Run a specialized SEO agent. Agents: crawling, seo_analyst, strategist,
    copywriter, chief_editor, consultant. Auto-detects from task if omitted. Credits: varies.

    Pass project_id to enrich with project context (business type, target group, skill profile).

    Requires VISIBLYAI_API_KEY. Use get_account_info to check your balance.
    """
    return paid_tools.seo_agent(task, agent, domain, url, keyword, content, params, project_id)


@mcp.tool()
def seo_workflow(
    workflow: str,
    domain: str,
    project_id: int,
    params: dict | None = None,
) -> str:
    """Run a multi-step SEO workflow with report generation.
    Workflows: seo_performance_audit (~150 credits), indexing_diagnosis (~200 credits),
    quick_win_analysis (~60 credits, DR-weighted keyword opportunities pos 10-100).
    Credits: 60-200 depending on workflow.

    Requires VISIBLYAI_API_KEY. Use get_account_info to check your balance.
    """
    return paid_tools.seo_workflow(workflow, domain, project_id, params)


# ---------------------------------------------------------------------------
# Google & Project Tools (require API key, 0 credits)
# ---------------------------------------------------------------------------

@mcp.tool()
def list_projects() -> str:
    """List your EEAT projects with scores, domains, and analysis status. Credits: 0.

    Requires VISIBLYAI_API_KEY.
    """
    return paid_tools.list_projects()


@mcp.tool()
def get_project(project_id: int) -> str:
    """Get project details including competitors and Google connections. Credits: 0.

    Requires VISIBLYAI_API_KEY.
    """
    return paid_tools.get_project(project_id)


@mcp.tool()
def get_google_connections() -> str:
    """Show connected Google Search Console and Analytics 4 properties. Credits: 0.

    Requires VISIBLYAI_API_KEY.
    """
    return paid_tools.get_google_connections()


@mcp.tool()
def query_search_console(
    gsc_property: str = "",
    dimension: str = "query",
    days: int = 28,
    limit: int = 100,
    country: str = "",
    device: str = "",
) -> str:
    """Query Google Search Console: clicks, impressions, CTR, position. Credits: 0.

    Dimensions: query, page, country, device, date. Auto-selects property if empty.
    Requires VISIBLYAI_API_KEY.
    """
    return paid_tools.query_search_console(
        gsc_property, dimension, days, limit, country, device
    )


@mcp.tool()
def query_analytics(
    ga4_property: str = "",
    report_type: str = "overview",
    days: int = 30,
    limit: int = 20,
) -> str:
    """Query Google Analytics 4: traffic, pages, sources, revenue. Credits: 0.

    Report types: overview, top_pages, traffic_sources, revenue.
    Auto-selects property if empty. Requires VISIBLYAI_API_KEY.
    """
    return paid_tools.query_analytics(ga4_property, report_type, days, limit)


@mcp.tool()
def query_knowledge_base(
    query: str,
    top_k: int = 5,
    category: str = "",
    document_type: str = "",
    include_external: bool = True,
) -> str:
    """Search the SEO knowledge base (blogs, docs, Google guidelines). Credits: 2.

    Semantic search over all indexed content ranked by relevance + recency.
    Sources: blog articles, SEO documentation, best practices, Google Search guidelines.
    Requires VISIBLYAI_API_KEY.
    """
    return paid_tools.query_knowledge_base(query, top_k, category, document_type, include_external)


# ---------------------------------------------------------------------------
# Project data & content (API key required, 0 credits, READ-ONLY)
# ---------------------------------------------------------------------------

@mcp.tool()
def get_gsc_clusters(project_id: int, days: int = 28, top_n: int = 30, country: str | None = None) -> str:
    """Topic clusters from Search Console with quick wins and alerts. Credits: 0, read-only.

    Returns the top_n clusters by impressions (each with a stable cluster_key for
    get_cluster_keywords), quick wins, alerts, totals and `computing`/`stale` flags.
    country: ISO alpha-3 (e.g. deu). Runs on the project owner's Google quota.
    """
    return project_tools.get_gsc_clusters(project_id, days, top_n, country)


@mcp.tool()
def get_cluster_keywords(project_id: int, cluster_key: str, days: int = 28, country: str | None = None,
                         limit: int = 100, offset: int = 0) -> str:
    """Keywords of one cluster (clicks, impressions, CTR, position), paginated. Credits: 0, read-only.

    Use cluster_key from get_gsc_clusters. Response carries page.has_more/next_offset.
    """
    return project_tools.get_cluster_keywords(project_id, cluster_key, days, country, limit, offset)


@mcp.tool()
def get_analytics_insights(project_id: int, days: int = 28) -> str:
    """GA4 flow (channels → page types → outcomes), funnel, channels, AI-referrer signals. Credits: 0, read-only."""
    return project_tools.get_analytics_insights(project_id, days)


@mcp.tool()
def get_revenue_insights(project_id: int) -> str:
    """Organic revenue attribution: totals, top keywords/landing pages, Pareto, cluster revenue. Credits: 0, read-only.

    has_data=false means no revenue analysis exists yet (nothing is estimated).
    """
    return project_tools.get_revenue_insights(project_id)


@mcp.tool()
def get_scorecard(project_id: int, days: int = 28) -> str:
    """KPI scorecard (leading + lagging indicators) over 28 or 90 days. Credits: 0, read-only."""
    return project_tools.get_scorecard(project_id, days)


@mcp.tool()
def get_eeat_summary(project_id: int) -> str:
    """Latest E-E-A-T scores, trend, open todos and competitor comparison. Credits: 0, read-only."""
    return project_tools.get_eeat_summary(project_id)


@mcp.tool()
def list_pages(project_id: int, page_type: str | None = None, search: str = "", limit: int = 50, offset: int = 0) -> str:
    """Page inventory from the sitemap with GSC metrics and index state, paginated. Credits: 0, read-only."""
    return project_tools.list_pages(project_id, page_type, search, limit, offset)


@mcp.tool()
def get_internal_links(project_id: int, url: str | None = None, limit: int = 20, offset: int = 0) -> str:
    """Internal link graph. Without url: summary + orphan pages. With url: inbound links and anchors. Credits: 0, read-only."""
    return project_tools.get_internal_links(project_id, url, limit, offset)


@mcp.tool()
def recall(query: str = "", project_id: int | None = None, limit: int = 10) -> str:
    """Recall facts the account remembered in the visibly chat (account facts, plus project facts if project_id). Credits: 0, read-only.

    Empty query lists recent facts. Requires tier Pro and CUSTOMER_MEMORY_ENABLED on the platform.
    """
    return project_tools.recall(query, project_id, limit)


@mcp.tool()
def list_articles(project_id: int, status: str = "all", limit: int = 25, offset: int = 0) -> str:
    """Content articles of a project (metadata only), newest first, paginated. Credits: 0, read-only.

    status: all|draft|queued|generating|approved|rejected|published|failed|archived.
    """
    return project_tools.list_articles(project_id, status, limit, offset)


@mcp.tool()
def get_article(article_id: int, include_content: bool = False, content_offset: int = 0,
                content_limit: int = 20000, project_id: int | None = None) -> str:
    """One article. Text only with include_content=true, delivered in chunks of up to 20000 characters. Credits: 0, read-only.

    Use next_content_offset to continue; content_hash changes when the article was edited.
    """
    return project_tools.get_article(article_id, include_content, content_offset, content_limit, project_id)


@mcp.tool()
def list_content_queries(project_id: int, limit: int = 50, offset: int = 0) -> str:
    """Content queries (keyword analyses) with status and scores, paginated. Credits: 0, read-only."""
    return project_tools.list_content_queries(project_id, limit, offset)


@mcp.tool()
def get_content_briefing(query_id: int, project_id: int | None = None) -> str:
    """Editorial briefing of a finished content analysis: terms, entities, questions, outline. Credits: 0, read-only.

    409 query_not_ready while the analysis is still pending.
    """
    return project_tools.get_content_briefing(query_id, project_id)


@mcp.tool()
def get_content_status(query_id: int, project_id: int | None = None) -> str:
    """Analysis status of a content query plus article generation state, no texts. Credits: 0, read-only."""
    return project_tools.get_content_status(query_id, project_id)


@mcp.tool()
def score_text(project_id: int, content: str, format: str = "markdown",
               query_id: int | None = None, persona_id: int | None = None) -> str:
    """Score a text against the project's brand rules and AI-slop patterns; with a ready query_id also the NSS. Credits: 0.

    Deterministic, nothing is stored. format: html|markdown (max 100000 chars).
    nss is null with a reason when no finished analysis is referenced.
    """
    return project_tools.score_text(project_id, content, format, query_id, persona_id)


@mcp.tool()
def submit_article_draft(project_id: int, title: str, content: str, keyword: str, format: str = "markdown",
                         idempotency_key: str | None = None, language: str = "de", country: str = "de",
                         persona_id: int | None = None, query_id: int | None = None,
                         expected_query_revision: int | None = None, expected_article_revision: int | None = None) -> str:
    """Hand your text over to visibly as an article draft (status draft, never queued). Credits: 0.

    Needs an API key with the right content:write. Pass a stable idempotency_key when retrying;
    the response echoes the key used. format: html|markdown. Without query_id a new content query
    is created; with query_id keyword/country/language/persona and expected_query_revision must match.
    """
    return content_write_tools.submit_article_draft(project_id, title, content, keyword, format, idempotency_key,
                                                    language, country, persona_id, query_id,
                                                    expected_query_revision, expected_article_revision)


@mcp.tool()
def update_article(article_id: int, expected_revision: int, idempotency_key: str | None = None,
                   title: str | None = None, content: str | None = None, format: str | None = None,
                   meta_description: str | None = None, keywords: list[str] | None = None,
                   project_id: int | None = None) -> str:
    """Edit a draft or rejected article. Credits: 0. Needs content:write.

    expected_revision comes from get_article; a mismatch returns revision_conflict with the current
    revision. With content, format (html|markdown) is required. Approved or published articles
    cannot be edited here; hand over a new draft instead.
    """
    return content_write_tools.update_article(article_id, expected_revision, idempotency_key, title, content, format,
                                              meta_description, keywords, project_id)


@mcp.tool()
def get_mcp_operation(operation_id: int) -> str:
    """Status and result of one of your write operations. Credits: 0, read-only."""
    return content_write_tools.get_mcp_operation(operation_id)


@mcp.tool()
def remember(content: str, scope: str = "project", project_id: int | None = None,
             idempotency_key: str | None = None) -> str:
    """Store a fact in YOUR visibly brain (the key holder's memory graph, read back by recall and the chat). Credits: 0.

    User data, not a permission: the fact only shapes your own chat context, never project
    content and never another member's graph. scope=project needs project_id; scope=account
    applies across all projects. Needs the key right memory:write. Pass a stable idempotency_key
    when retrying; the response echoes the key used.
    """
    return content_write_tools.remember(content, scope, project_id, idempotency_key)


def main():
    """Entry point for the MCP server and CLI commands.

    CLI usage:
        visiblyai-mcp-server                    Start MCP server (default)
        visiblyai-mcp-server sync-skills [path] Push skills to platform API
        visiblyai-mcp-server build-fallback [path] Build offline fallback blob
    """
    import sys
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        arg = sys.argv[2] if len(sys.argv) > 2 else None
        if cmd == "sync-skills":
            from .cli import sync_skills
            sync_skills(arg)
            return
        if cmd == "build-fallback":
            from .cli import build_fallback
            build_fallback(arg)
            return
    mcp.run()


if __name__ == "__main__":
    main()
