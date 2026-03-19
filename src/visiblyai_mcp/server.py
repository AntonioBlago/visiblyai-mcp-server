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

from .tools import free_tools, paid_tools

mcp = FastMCP(
    "VisiblyAI SEO Tools",
    instructions=(
        "Professional SEO tools powered by VisiblyAI. "
        "Free: keyword classifier, SEO checklists, best practices. "
        "Paid: traffic analysis, keyword research, backlinks, competitor analysis, "
        "OnPage SEO audit, link checking, SEO agents, SEO workflows "
        "(requires API key + credits). "
        "Google: Search Console queries, Analytics reports, project management "
        "(requires API key, 0 credits)."
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
) -> str:
    """Run a specialized SEO agent. Agents: crawling, seo_analyst, strategist,
    copywriter, chief_editor, consultant. Auto-detects from task if omitted. Credits: varies.

    Requires VISIBLYAI_API_KEY. Use get_account_info to check your balance.
    """
    return paid_tools.seo_agent(task, agent, domain, url, keyword, content, params)


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
