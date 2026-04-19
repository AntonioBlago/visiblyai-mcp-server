# Changelog

All notable changes to `visiblyai-mcp-server` are documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), versioning follows [SemVer](https://semver.org/).

## [0.6.0] — 2026-04-19

### Added
- **New MCP tool `query_fanout`** — runs Query Fan-Out AI Coverage Analysis for a URL + seed keyword. Gemini Grounding generates fan-out sub-queries, the page content is crawled and topic-extracted, and semantic matching scores coverage. Returns `coverage_score`, `fanout_queries[]`, `gaps[]`, `covered_count`, `total_count`. Registered in `server.py`, handler in `paid_tools.py`, HTTP client method in `api_client.py`.
- **3 new platform skills** shipped in the fallback bundle and queryable via `get_skill`:
  - `@onpage-local-check` (seo-technical, 0 cr.) — offline HTML pre-publish gate with 8-block checklist + project-CI validation
  - `@content-write` (seo-content, 45 cr.) — single-article draft synchronous generator (blog / pillar / product-page) using user's project frame + templates + query-fanout for sub-topic coverage
  - `@project-health-check` (seo-analysis, 35 cr.) — 6-dimension scorecard (traffic, GSC/GA4, CWV, sitemap, schema, content coverage) with rate-limit fallback

### Changed
- Server version bumped to `0.6.0` (minor: new tool + new skills).
- Platform `SERVER_VERSION` in `mcp_protocol_routes.py` synced to `0.6.0` (was `0.5.2`).
- Fallback skill blob rebuilt (22 skills, 66.4 KB compressed — was 19 skills).
- `test_server_registration.py` expected tool count updated 32 → 33.

### Notes
- No breaking changes. Existing tools retain identical signatures.
- Skills registry grew 19 → 22 and is now synced to both `mcp_skills` DB table and Pinecone vector index.
- Platform-side migration `add_ci_rules_eeat_projects_20260419.sql` introduces a new optional `ci_rules JSON` column on `eeat_projects`, consumed by `@onpage-local-check` and `@content-write` via `prompt_loader.resolve_ci_rules`.

---

## [0.5.3] — 2026-04-xx

Previous patch release. See git log for details.

## [0.5.2] — 2026-04-14

Prior baseline release.
