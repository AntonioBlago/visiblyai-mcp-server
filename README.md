# VisiblyAI MCP Server

SEO tools for Claude Code. Free local tools + paid API-powered analysis.

**Production routing:** MCP clients connect to `https://mcp.visibly-ai.com/mcp`. The installed package sends API-backed tool calls to `https://app.visibly-ai.com/api/v1/mcp`. The marketing domain `visibly-ai.com` is not an API host.

**Free tools** (no API key needed): keyword classifier, SEO checklists, best practices, URL analysis, Google guidelines, workflow skills.

**Paid tools** (require API key + credits): traffic analysis, keyword research, backlinks, competitors, OnPage SEO audit, PageSpeed/Core Web Vitals, SERP analysis, sitemap audit, structured data validation, hreflang checks, link checking, SEO agents, SEO workflows, advanced keyword classification.

## Quick Start

### Option 1: Remote server (zero install, recommended)

No Python or pip needed. Just add a URL to your Claude Code config:

```bash
# With API key (all 83 tools):
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

### Content workflow (API key with scoped rights) — 35 tools

Read the editor context, research keywords, create and analyze a query, write and optimize drafts, approve articles, configure CMS connections, publish, and review optimizer suggestions. The Visibly server operator must enable the relevant write stage. Grant only the required rights in Visibly Settings → API key & MCP; existing keys do not receive new rights automatically.

| Tool | Description |
|------|-------------|
| `get_content_query` / `list_content_queries` / `get_content_briefing` / `get_content_status` | Read query, draft, briefing, analysis and generation state; draft bodies are paginated |
| `create_content_query` | Analyze a keyword and create a content query (paid; `content:write` + `spending:execute`) |
| `save_content_query_draft` | Save HTML/Markdown with revision protection and sanitization (`content:write`) |
| `generate_article_from_query` | Queue AI generation from a ready query (paid; `content:write` + `spending:execute`) |
| `optimize_content_draft` | Return a measured editor optimization proposal; does not save (paid; `spending:execute`) |
| `submit_article_draft` | Hand your own text over as an article draft (query, draft and article in one transaction; HTML is sanitized) |
| `update_article` | Edit a draft or rejected article with `expected_revision` (409 on conflict) |
| `edit_content_article` | Full editor save for editable lifecycle states; snapshots the old version and checks `expected_revision` |
| `regenerate_content_article` | Requeue an eligible article for paid generation (`content:write` + `spending:execute`) |
| `change_article_status` | Approve, reject, archive or queue; approval requires `content:approve` and sends the normal approval webhook. Queueing additionally requires `spending:execute`, plan access, member budget and owner credits |
| `list_cms_connections` / `create_cms_connection` / `test_cms_connection` / `delete_cms_connection` | Manage and test project CMS connections (`cms:manage`) |
| `create_contentpilot_key` / `get_contentpilot_key_status` / `revoke_contentpilot_key` | Manage the project-scoped Pull API key; plaintext only on creation (`cms:manage`) |
| `publish_article` / `update_cms_article` | Publish an approved article or update its existing CMS entry (`content:publish`) |
| `pull_live_article` / `set_article_live_url` | Read the live page into a proposal or connect/disconnect its public URL |
| `list_article_backups` / `get_article_backup` / `restore_article_backup` | Read and restore editor/CMS versions; restore requires the current article revision |
| `get_optimizer_settings` / `update_optimizer_settings` | Read and change optimizer and autolink settings (`content:write`) |
| `run_content_optimizer` | Start a paid optimizer run (`content:write` + `spending:execute`) |
| `list_optimizer_suggestions` / `approve_optimizer_suggestion` / `reject_optimizer_suggestion` / `undo_optimizer_suggestion` | Review and apply measured suggestions; applying/undoing requires `content:approve`. Snippet/link changes also require `content:publish` for automatic CMS writeback; topic suggestions do not |
| `get_mcp_operation` | Status and result of one of your write operations |
| `remember` | Store a fact in your own visibly brain (key right `memory:write`; account or project scope; read back by `recall` and the chat) |
| `import_meeting_preview` | Turn a meeting transcript into a reviewable proposal: brain facts with categories and entities, brand rules, personas, profile fields (15 credits, nothing written) |
| `import_meeting_apply` | Write the reviewed selection: facts into your brain (`memory:write`), rules, personas and profile into the project (`content:write`); 0 credits, idempotent |

Webhook secrets and `cp_` keys created through MCP are returned **once**. Store them in the hosting provider's secret manager; never paste them into source code or logs. The Visibly MCP creates and tests the CMS connection but does not write Vercel, Railway, Hetzner, or other host environment variables. Use that provider's authorized MCP or secret manager for deployment configuration.

The paid optimizer run and article generation require the `spending:execute` key scope; the caller must still pass the project budget, tier and credit checks. The server reports their actual errors rather than silently degrading into free actions.

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
