# Changelog

All notable changes to `visiblyai-mcp-server` are documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), versioning follows [SemVer](https://semver.org/).

## [0.10.0] - 2026-09-10

### Added
- `remember` (stage 2D of write-back, 0 credits, needs the key right `memory:write`): stores a fact in the key holder's own visibly brain, account-wide or for one project; `recall` and the SEO copilot chat read the same graph. Idempotent via `idempotency_key`, the server derives a stable memory id from the operation so retries never duplicate.

## [0.9.0] - 2026-09-08

### Added
- Three write tools (stage 2A of write-back, 0 credits, need the key right `content:write` granted in the visibly settings): `submit_article_draft` hands your own text over as an article draft (query, draft and article in one transaction, HTML sanitized), `update_article` edits a draft or rejected article guarded by `expected_revision`, `get_mcp_operation` reads the status of a write operation. Every call carries an `idempotency_key` (generated when omitted and echoed back) so retries replay instead of duplicating.

## [0.8.0] - 2026-09-08

### Added
- 15 read-only project-data and content tools (0 credits): Search Console clusters and keywords, GA4 insights, revenue, scorecard, EEAT, pages, internal links, `recall`, articles, content queries, briefing, status and `score_text`.

## [0.7.2] - 2026-09-06

### Fixed
- Register and credit-management links now point to the app (`https://app.visibly-ai.com/register`, `https://app.visibly-ai.com/settings`) instead of the marketing domain; the stale `antonioblago.com` support block in INSTALL.md is gone.
- Subscription tables in README and INSTALL show the current tiers (Standard €49 / 9,000 credits, Pro €149 / 30,000, Agency €499 / 90,000).

## [0.7.1] - 2026-08-01

### Fixed
- The default native API base URL now uses the production app host at `https://app.visibly-ai.com/api/v1/mcp`.

## [0.7.0] - 2026-08-01

### Changed
- All API-backed tools now use the native visibly-app FastAPI backend. The production host correction ships in 0.7.1.
- RAG search uses the shared `VisiblyAIClient` transport again; the temporary split `VISIBLYAI_RAG_URL` path is removed.
- Signup, credit-management, homepage, and documentation URLs now point to Visibly AI.
- The backend owner and release documentation now reflect the 33 registered tools.

### Added
- `VISIBLYAI_API_URL` can override the complete API base URL for local development or staging.

### Notes
- Tool names and function signatures are unchanged.
- The native backend preserves the legacy MCP response envelopes while using shared FastAPI authentication, credit billing, Google integrations, and SSRF protection.

## [0.6.1] — 2026-06-04

### Changed
- **RAG search backend repointed (surgical).** `query_knowledge_base` / `rag_search` now targets a dedicated `RAG_BASE_URL` instead of the shared `BASE_URL`. RAG has moved to the visibly-app (FastAPI on Railway); all other tools (`guidance`, `checklist`, `skills`, `google-guidelines`, traffic/keywords/…) still talk to antonioblago.com unchanged.
- `rag_search.py` now performs its own authenticated `httpx.post` against `RAG_BASE_URL/tools/rag-search` (Bearer API key) and parses the new envelope (`data` / `credits_used` / `credits_remaining`), rather than routing through `VisiblyAIClient` whose handler expects the legacy Flask response shape. The `client` argument is retained purely as the API-key source, so the `paid_tools` call site is unchanged.
- `__init__.py` version synced to `0.6.1` (was stuck at `0.5.2`, out of step with `pyproject.toml`).

### Added
- **`VISIBLYAI_RAG_URL` env var** — overrides the RAG backend URL. Defaults to `BASE_URL` (antonioblago.com), so behaviour is **unchanged** until the cutover is explicitly activated. Set to e.g. `https://<app>.up.railway.app/api/v1/mcp` to switch RAG to visibly-app.

### Notes
- No breaking changes. Tool signatures and the `paid_tools` call site are identical; the switch is purely transport-level and env-gated.
- Cutover gate: with `VISIBLYAI_RAG_URL` pointing at visibly-app, `query_knowledge_base` returns hits from visibly-app, 2 credits are deducted, and an `mcp_transactions` row is written (verified by `backend/scripts/check_rag_search_live.py --write` in visibly-app).

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
