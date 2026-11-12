# CLAUDE.md — VisiblyAI MCP Server


## Connector-Sync (Pflicht, seit 09.11.2026)

Diese Repos bilden zusammen eine Schnittstelle und werden immer gemeinsam nachgezogen:

- `visibly-app`: Pull-API (`backend/app/routers/content/pull_api_routes.py`), Webhook-Payload, Confirm-Endpunkt.
- `visibly-ai-cms-connector`: öffentliches SDK (`ai_content_autopilot`). Die Feldtabelle im README ist der Vertrag.
- `visiblyai`: Blog-Connector der Marketingseite. Nutzt das SDK; eigene Logik nur für Datei, Rückprüfung und GitHub-Commit.
- `visiblyai-mcp-server`: Artikel-, Draft- und Live-URL-Werkzeuge mit derselben Feldsemantik.
- `anycms`: Beispiele (WordPress, Astro, Next.js, Flask) auf der aktuellen SDK-Version.

Ändert sich in einem Repo ein Feld, ein Statuscode, die Webhook-Signatur oder ein Endpunkt, im selben Zug die anderen
prüfen und nachziehen, je Repo mit Test und CHANGELOG-Eintrag. Anlass: Am 09.11.2026 scheiterte der erste Blogartikel
an `missing_language`, weil Pull-API, SDK-Doku und Marketing-Connector auseinandergelaufen waren.

## Plugin-/MCP-Übergabe

Start with [AGENTS.md](AGENTS.md) and the cross-repository
[handoff](docs/PLUGIN_MCP_HANDOFF.md) for plugin, skill, release or transport work.
[PLUGINS.md](PLUGINS.md) is the user installation guide. Record verified changes,
versions and publication status in the handoff so the next agent can continue.

## Project Overview

Python MCP (Model Context Protocol) server providing 91 tools as of release 0.16.1 (2026-11-03) for Claude Code, Codex and other MCP clients. Published on PyPI as `visiblyai-mcp-server`. Plugin bundles have a separate version: 1.0.2.

- **Free tools (8)**: Run locally or use free API metadata (classifier, checklists, guidance, URL analysis)
- **Paid tools (20)**: Use the Visibly AI API (traffic, keywords, backlinks, competitors, crawling, audits, RAG, SEO agents, workflows)
- **Google tools (5)**: Use user's OAuth tokens, 0 credits (GSC, GA4, projects)
- **Project data tools (15)** and **content workflow tools (36)**: read/write, scoring and CMS operations; costs and permissions are defined per tool by the backend.

**Backend API**: `https://app.visibly-ai.com/api/v1/mcp`
**Remote MCP**: `https://mcp.visibly-ai.com/mcp`

The backend URL is the internal REST target used by API-backed package tools. MCP clients configure the remote MCP URL. The marketing domain `visibly-ai.com` is not an API host.

---

## Key Files

| File | Purpose |
|------|---------|
| `src/visiblyai_mcp/server.py` | FastMCP registration, including dynamically registered workflow tools; count the runtime registry |
| `src/visiblyai_mcp/api_client.py` | `VisiblyAIClient` HTTP client for backend |
| `src/visiblyai_mcp/tools/paid_tools.py` | Paid tool implementations |
| `src/visiblyai_mcp/tools/free_tools.py` | Free tool implementations (local) |
| `src/visiblyai_mcp/classifier.py` | Keyword classifier engine |
| `src/visiblyai_mcp/config.py` | API URLs, key management |
| `src/visiblyai_mcp/tools/content_workflow_tools.py` | Shared workflow definitions used by package and remote transport |
| `skills/content-nss-optimize/SKILL.md` | Canonical article optimization skill; synchronize bundle copies via build script |
| `scripts/build_plugins.py` | Validate marketplaces/manifests and build reproducible plugin ZIPs |

---

## Code Patterns

### Adding a New Tool
Follow the `new-tool` workflow in `.claude/workflows/new-tool.md`:
1. `api_client.py` → add method: `self._post("/tools/endpoint", payload)`
2. `paid_tools.py` → add function: `_require_key()` / `_format_result()` / `_handle_error()`
3. `server.py` → add `@mcp.tool()` function with docstring
4. Tests → add to `test_paid_tools.py` + update `test_server_registration.py`

### Error Handling
```python
try:
    client = _require_key()
    result = client.method(args)
    return _format_result(result)
except Exception as e:
    return _handle_error(e)
```

### Parameter Capping
Always cap limits: `min(limit, MAX)` before passing to API.

---

## Test Commands

```bash
# Unit tests (fast, no API key)
pytest tests/ --ignore=tests/integration --ignore=tests/e2e -v

# Free integration tests (safe, no credits)
VISIBLYAI_API_KEY=lc_xxx pytest tests/integration/test_live_free_tools.py -v

# Full integration (burns credits)
VISIBLYAI_API_KEY=lc_xxx pytest tests/integration/ -v

# Specific test file
pytest tests/test_server_registration.py -v
```

---

## Skills (Slash Commands)

| Skill | Purpose | Credits |
|-------|---------|---------|
| `/seo-audit` | Full SEO audit (traffic + keywords + on-page + links + backlinks) | ~80 |
| `/competitor-analysis` | Compare domain vs top competitors | ~100 |
| `/keyword-research` | Keyword research with classification | ~30 |
| `/site-health-check` | Quick technical health check | ~50 |
| `/gsc-report` | GSC performance report with quick wins | 0 |
| `/traffic-analysis` | Traffic trends and projections | ~30 |

---

## Workflows

| Workflow | Purpose |
|----------|---------|
| `new-tool` | Add a new MCP tool to the package |
| `publish` | Test, build, publish to PyPI |
| `bug-fix` | Diagnose and fix tool issues |
| `feedback-loop` | Test-driven improvement cycle |

---

## Backend Sync

The backend is in `c:\Users\anton\PycharmProjects\visibly-app\`:
- `backend/app/routers/mcp/` contains the API-key-authenticated REST routes.
- `shared/services/` contains billing-free operations and native orchestration.
- `shared/tools/definitions.py` contains the chat tool contracts.
- The FastAPI routes and this package's tool definitions must stay in sync.

---

## Memory Files

| File | Content |
|------|---------|
| `.claude/memory/TOOLS.md` | Complete tool inventory with params and endpoints |
| `.claude/memory/ARCHITECTURE.md` | Code structure and patterns |
| `.claude/memory/TEST_RESULTS.md` | Test outcome tracking (feedback layer) |
