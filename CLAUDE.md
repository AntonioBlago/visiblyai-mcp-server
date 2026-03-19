# CLAUDE.md — VisiblyAI MCP Server

## Project Overview

Python MCP (Model Context Protocol) server providing 23 SEO tools for Claude Code and other MCP clients. Published on PyPI as `visiblyai-mcp-server`.

- **Free tools (6)**: Run locally, no API key needed (classifier, checklists, guidance, URL analysis)
- **Paid tools (12)**: Proxy to VisiblyAI platform API (traffic, keywords, backlinks, competitors, crawling, on-page analysis, SEO agents, workflows)
- **Google tools (5)**: Use user's OAuth tokens, 0 credits (GSC, GA4, projects)

**Backend API**: `https://antonioblago.com/api/v1/mcp`
**Remote MCP**: `https://mcp.visibly-ai.com/mcp`

---

## Key Files

| File | Purpose |
|------|---------|
| `src/visiblyai_mcp/server.py` | FastMCP server — all 23 `@mcp.tool()` registrations |
| `src/visiblyai_mcp/api_client.py` | `VisiblyAIClient` HTTP client for backend |
| `src/visiblyai_mcp/tools/paid_tools.py` | Paid tool implementations |
| `src/visiblyai_mcp/tools/free_tools.py` | Free tool implementations (local) |
| `src/visiblyai_mcp/classifier.py` | Keyword classifier engine |
| `src/visiblyai_mcp/config.py` | API URLs, key management |

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

The backend is in `c:\Users\anton\PycharmProjects\Bikefitting_Project\scripts\`:
- `mcp_protocol_routes.py` — Remote MCP server (JSON-RPC)
- `mcp_api_routes.py` — REST API routes
- Both must stay in sync with this PyPI package's tool definitions

---

## Memory Files

| File | Content |
|------|---------|
| `.claude/memory/TOOLS.md` | Complete tool inventory with params and endpoints |
| `.claude/memory/ARCHITECTURE.md` | Code structure and patterns |
| `.claude/memory/TEST_RESULTS.md` | Test outcome tracking (feedback layer) |
