# Tool Inventory

## Free Tools (6) — No API key, 0 credits

| Tool | Parameters | Credits |
|------|-----------|---------|
| `classify_keywords` | `keywords`, `brand_name?`, `brand_variations?`, `product_keywords?`, `competitors?`, `language?`, `location?` | 0 |
| `seo_checklist` | `checklist_type?`, `language?` | 0 |
| `seo_guidance` | `topic` | 0 |
| `analyze_url_structure` | `url` | 0 |
| `get_account_info` | — | 0 |
| `list_locations` | — | 0 |

## Paid Tools (12) — API key + credits

| Tool | Parameters | Credits | API Endpoint |
|------|-----------|---------|-------------|
| `get_traffic_snapshot` | `domain`, `location?` | ~10 | `/tools/traffic-snapshot` |
| `get_historical_traffic` | `domain`, `location?`, `date_from?`, `date_to?` | ~10 | `/tools/historical-traffic` |
| `get_keywords` | `domain`, `location?`, `limit?` (max 1000) | ~15 | `/tools/keywords` |
| `get_competitors` | `domain`, `location?`, `language?`, `limit?` (max 50) | ~20 | `/tools/competitors` |
| `get_backlinks` | `domain`, `location?`, `limit?` (max 1000) | ~15 | `/tools/backlinks` |
| `get_referring_domains` | `domain`, `location?`, `limit?` (max 500) | ~10 | `/tools/referring-domains` |
| `validate_keywords` | `keywords`, `location?`, `language?`, `top_n?` (max 200) | ~5-20 | `/tools/validate-keywords` |
| `crawl_website` | `url`, `keyword?`, `max_pages?` (max 10) | 15-60 | `/tools/crawl` |
| `onpage_analysis` | `url`, `keyword` | 15 | `/tools/onpage-analysis` |
| `check_links` | `url` | 20 | `/tools/check-links` |
| `seo_agent` | `task`, `agent?`, `domain?`, `url?`, `keyword?`, `content?`, `params?` | varies | `/tools/seo-agent` |
| `seo_workflow` | `workflow`, `domain`, `project_id`, `params?` | 150-200 | `/tools/seo-workflow` |

## Google/Project Tools (5) — API key, 0 credits

| Tool | Parameters | API Endpoint |
|------|-----------|-------------|
| `list_projects` | — | `/tools/list-projects` |
| `get_project` | `project_id` | `/tools/get-project` |
| `get_google_connections` | — | `/tools/google-connections` |
| `query_search_console` | `gsc_property?`, `dimension?`, `days?`, `limit?`, `country?`, `device?` | `/tools/query-search-console` |
| `query_analytics` | `ga4_property?`, `report_type?`, `days?`, `limit?` | `/tools/query-analytics` |

**Total: 23 tools**
