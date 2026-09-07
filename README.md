# VisiblyAI MCP Server

SEO tools for Claude Code. Free local tools + paid API-powered analysis.

**Production routing:** MCP clients connect to `https://mcp.visibly-ai.com/mcp`. The installed package sends API-backed tool calls to `https://app.visibly-ai.com/api/v1/mcp`. The marketing domain `visibly-ai.com` is not an API host.

**Free tools** (no API key needed): keyword classifier, SEO checklists, best practices, URL analysis, Google guidelines, workflow skills.

**Paid tools** (require API key + credits): traffic analysis, keyword research, backlinks, competitors, OnPage SEO audit, PageSpeed/Core Web Vitals, SERP analysis, sitemap audit, structured data validation, hreflang checks, link checking, SEO agents, SEO workflows, advanced keyword classification.

## Quick Start

### Option 1: Remote server (zero install, recommended)

No Python or pip needed. Just add a URL to your Claude Code config:

```bash
# With API key (all 48 tools):
claude mcp add --transport http \
  --header "Authorization: Bearer lc_your_key" \
  visiblyai https://mcp.visibly-ai.com/mcp

# Without API key (8 free tools only):
claude mcp add --transport http visiblyai https://mcp.visibly-ai.com/mcp
```

### Option 2: uvx (local, no install needed)

```bash
claude mcp add --transport stdio \
  --env VISIBLYAI_API_KEY=lc_your_key \
  visiblyai -- uvx visiblyai-mcp-server
```

### Option 3: pip install (local)

```bash
pip install visiblyai-mcp-server
claude mcp add --transport stdio \
  --env VISIBLYAI_API_KEY=lc_your_key \
  visiblyai -- visiblyai-mcp-server
```

Then restart Claude Code.

> **No API key?** Free tools work without one. Get an API key at [app.visibly-ai.com/register](https://app.visibly-ai.com/register) to unlock paid tools.

## Tools

### Free (local, no credits) — 8 tools

| Tool | Description |
|------|-------------|
| `classify_keywords_simple` | Classify keywords by intent, funnel stage, brand type, topic (local regex, DE+EN) |
| `seo_checklist` | 5 checklists: general, blog, ecommerce, discover, backlink |
| `seo_guidance` | Best practices: title tags, EEAT, Core Web Vitals, schema, and more |
| `get_google_guidelines` | Official Google Search guidelines by category (scraped weekly) |
| `get_skill` | Fetch SEO workflow guides: audit, keyword research, competitor analysis |
| `analyze_url_structure` | Check URL SEO-friendliness |
| `get_account_info` | Check your credit balance and tier |
| `list_locations` | Available countries for paid tools |

### Paid (API-powered, uses credits) — 20 tools

| Tool | Credits | Description |
|------|---------|-------------|
| `classify_keywords_advanced` | varies | Keyword classification with DataForSEO Search Intent API + regex (more accurate intent) |
| `get_traffic_snapshot` | varies | Current organic/paid traffic for a domain |
| `get_historical_traffic` | varies | Traffic trends (up to 5 years) |
| `get_keywords` | varies | Top ranking keywords with volume and position |
| `get_competitors` | varies | Competitor domains by keyword overlap |
| `get_backlinks` | varies | Backlink profile with Domain Rating |
| `get_referring_domains` | varies | Referring domains with authority scores |
| `validate_keywords` | varies | Search volume, competition, CPC for keyword list |
| `crawl_website` | 15-60 | Live crawl + optional 24-point OnPage analysis |
| `onpage_analysis` | 15 | Full 24-point OnPage SEO audit |
| `check_serp` | 15 | Live Google SERP results for a keyword: top organic results with position, URL, domain |
| `check_pagespeed` | 5 | Google PageSpeed Insights + Core Web Vitals: LCP, CLS, TBT, performance score |
| `audit_sitemap` | 20 | XML sitemap audit: total URLs, duplicates, broken links, lastmod coverage |
| `check_structured_data` | 5 | JSON-LD and microdata validation: schema types, required fields, errors |
| `check_hreflang` | 10 | Hreflang validation: x-default, language codes, bidirectional linking |
| `check_links` | 20 | Broken link detection on a page |
| `seo_agent` | varies | Run specialized SEO agents: analyst, strategist, copywriter, consultant |
| `seo_workflow` | 150-200 | Multi-step SEO workflows: seo_performance_audit, indexing_diagnosis |
| `query_knowledge_base` | 2 | Semantic RAG search over SEO knowledge base, blog articles, Google guidelines |
| `query_fanout` | 10-60 | AI query fan-out and content coverage analysis |

### Google & Project (API key required, 0 credits) — 5 tools

These tools use your own Google OAuth tokens connected via the VisiblyAI platform.

| Tool | Description |
|------|-------------|
| `list_projects` | List your EEAT projects with scores and status |
| `get_project` | Get project details, competitors, and Google connections |
| `get_google_connections` | Show connected GSC/GA4 properties and pairings |
| `query_search_console` | Query GSC: clicks, impressions, CTR, position by query/page/country/device |
| `query_analytics` | Query GA4: traffic overview, top pages, traffic sources, revenue |

### Project data & content (API key required, 0 credits, read-only) — 15 tools

Nothing here writes back to visibly or spends credits. Team members read on the project owner's data; area roles apply (analytics / seo_tools / content).

| Tool | What it returns |
|---|---|
| `get_gsc_clusters` | Topic clusters (top_n), quick wins, alerts, `computing`/`stale` flags |
| `get_cluster_keywords` | Keywords of one cluster, paginated (`cluster_key` from the overview) |
| `get_analytics_insights` | GA4 flow, funnel, channels, AI-referrer signals |
| `get_revenue_insights` | Revenue totals, top keywords/pages, Pareto, cluster revenue |
| `get_scorecard` | KPI scorecard, 28 or 90 days |
| `get_eeat_summary` | E-E-A-T scores, trend, open todos, competitors |
| `list_pages` | Page inventory with GSC metrics and index state |
| `get_internal_links` | Link-graph summary + orphans, or inbound links of one URL |
| `recall` | Facts remembered in the visibly chat (tier Pro) |
| `list_articles` / `get_article` | Articles; text only on request, chunked |
| `list_content_queries` / `get_content_briefing` / `get_content_status` | Content analyses, briefing, status |
| `score_text` | Brand + AI-slop check, NSS with a finished analysis |

Limits: 60 requests/minute per key, responses up to 256 KiB (lists continue via `page.next_offset`), requests up to 512 KiB. Errors come as `{"error": "<code>", "message": ...}` (`not_found`, `role_no_access`, `rate_limited`, `result_too_large`, ...).

## Examples

In Claude Code, just ask naturally:

```
> Classify these keywords: "seo tool kaufen", "was ist seo", "seo agentur berlin"

> Give me the blog SEO checklist in German

> What are the best practices for title tags?

> What does Google say about EEAT?

> Get the top keywords for example.com

> Run an OnPage SEO analysis on https://example.com/page for the keyword "seo tool"

> Run a full SEO performance audit for example.com (project_id: 12)

> Search the knowledge base for structured data best practices
```

## Configuration

### Environment Variable

| Variable | Required | Description |
|----------|----------|-------------|
| `VISIBLYAI_API_KEY` | For API-backed tools | API key from [app.visibly-ai.com](https://app.visibly-ai.com/settings) |
| `VISIBLYAI_API_URL` | No | Override the API base URL for local development or staging |

### Getting an API Key

1. Sign up at [app.visibly-ai.com/register](https://app.visibly-ai.com/register)
2. Go to Settings > API Keys
3. Create a new key (starts with `lc_`)
4. Add it to your Claude Code MCP config

### Subscription Tiers

| Tier | Credits/month | Price |
|------|---------------|-------|
| Free | 0 | Free |
| Standard | 9,000 | €49/mo |
| Pro | 30,000 | €149/mo |
| Agency | 90,000 | €499/mo |

## Requirements

- Python 3.10+
- Claude Code CLI

## Development

Run the test suite with `PYTHONPATH=src`, not a plain `python -m pytest`:

```bash
PYTHONPATH=src python -m pytest tests -q --ignore=tests/integration
```

Without `PYTHONPATH=src`, `python -m pytest` can resolve `visiblyai_mcp` against an
installed package version instead of the local `src/` checkout, so tests run against
the wrong code. `--ignore=tests/integration` skips the tests that need a live API key.

## License

MIT
