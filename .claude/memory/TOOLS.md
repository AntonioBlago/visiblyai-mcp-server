# Tool Inventory

## Free Tools (8) — No credits

| Tool | Parameters | Credits |
|------|-----------|---------|
| `classify_keywords_simple` | `keywords`, `brand_name?`, `brand_variations?`, `product_keywords?`, `competitors?` | 0 |
| `seo_checklist` | `checklist_type?`, `language?` | 0 |
| `seo_guidance` | `topic` | 0 |
| `get_google_guidelines` | `category?` | 0 |
| `analyze_url_structure` | `url` | 0 |
| `get_account_info` | — | 0 |
| `list_locations` | — | 0 |
| `get_skill` | `name?` | 0 |

## Paid Tools (20) — API key + credits

| Tool | Parameters | Credits | API Endpoint |
|------|-----------|---------|-------------|
| `get_traffic_snapshot` | `domain`, `location?` | ~10 | `/tools/traffic-snapshot` |
| `get_historical_traffic` | `domain`, `location?`, `date_from?`, `date_to?` | ~10 | `/tools/historical-traffic` |
| `get_keywords` | `domain`, `location?`, `limit?` (max 1000) | ~15 | `/tools/keywords` |
| `get_competitors` | `domain`, `location?`, `language?`, `limit?` (max 50) | ~20 | `/tools/competitors` |
| `get_backlinks` | `domain`, `location?`, `limit?` (max 1000) | ~15 | `/tools/backlinks` |
| `get_referring_domains` | `domain`, `location?`, `limit?` (max 500) | ~10 | `/tools/referring-domains` |
| `validate_keywords` | `keywords`, `location?`, `language?`, `top_n?` (max 200) | ~5-20 | `/tools/validate-keywords` |
| `classify_keywords_advanced` | `keywords`, `language?`, `location?` | varies | `/tools/classify-keywords` |
| `crawl_website` | `url`, `keyword?`, `max_pages?` (max 10) | 15-60 | `/tools/crawl` |
| `onpage_analysis` | `url`, `keyword` | 15 | `/tools/onpage-analysis` |
| `query_fanout` | `url`, `keyword`, `data_source?`, `gsc_property?`, `language?` | 10-60 | `/tools/query-fanout` |
| `check_links` | `url` | 20 | `/tools/check-links` |
| `check_serp` | `keyword`, `location?`, `language?`, `depth?` | 15 | `/tools/check-serp` |
| `check_pagespeed` | `url`, `strategy?` | 5 | `/tools/check-pagespeed` |
| `audit_sitemap` | `domain` | 20 | `/tools/audit-sitemap` |
| `check_structured_data` | `url` | 5 | `/tools/check-structured-data` |
| `check_hreflang` | `url` | 10 | `/tools/check-hreflang` |
| `seo_agent` | `task`, `agent?`, `domain?`, `url?`, `keyword?`, `content?`, `params?` | varies | `/tools/seo-agent` |
| `seo_workflow` | `workflow`, `domain`, `project_id`, `params?` | 150-200 | `/tools/seo-workflow` |
| `query_knowledge_base` | `query`, `top_k?`, `category?`, `document_type?`, `include_external?` | 2 | `/tools/rag-search` |

## Google/Project Tools (5) — API key, 0 credits

| Tool | Parameters | API Endpoint |
|------|-----------|-------------|
| `list_projects` | — | `/tools/list-projects` |
| `get_project` | `project_id` | `/tools/get-project` |
| `get_google_connections` | — | `/tools/google-connections` |
| `query_search_console` | `gsc_property?`, `dimension?`, `days?`, `limit?`, `country?`, `device?` | `/tools/query-search-console` |
| `query_analytics` | `ga4_property?`, `report_type?`, `days?`, `limit?` | `/tools/query-analytics` |

**Total: 33 tools**
