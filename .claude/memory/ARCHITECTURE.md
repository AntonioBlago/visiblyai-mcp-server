# Architecture

## File Structure

```
src/visiblyai_mcp/
├── server.py           # FastMCP server — all 23 @mcp.tool() registrations
├── api_client.py       # VisiblyAIClient — HTTP client for backend API
├── config.py           # BASE_URL, get_api_key(), SIGNUP_URL, CREDITS_URL
├── classifier.py       # KeywordClassifier — local keyword classification
├── tools/
│   ├── free_tools.py   # Free tool implementations (local, no API)
│   └── paid_tools.py   # Paid tool implementations (proxy to API)
└── knowledge/
    ├── checklists.py   # SEO checklists (API-first, embedded fallback)
    └── seo_guidance.py # SEO guidance (API-first, embedded fallback)
```

## Patterns

### Adding a Paid Tool
1. `api_client.py`: Add method → `self._post("/tools/endpoint", payload)`
2. `paid_tools.py`: Add function → `_require_key()` / `_format_result()` / `_handle_error()`
3. `server.py`: Add `@mcp.tool()` function → delegate to `paid_tools.func()`

### Error Handling
- `APIError(message, status_code, credits_hint)` — raised by client
- `_handle_error(e)` — converts to JSON: `{"error": "...", "credits_url"?: "...", "signup_url"?: "..."}`
- Status codes: 401 (bad key), 402 (no credits), 429 (rate limit), 5xx (server)

### Knowledge Tools (Checklists/Guidance)
- Try API first (`httpx.get` to backend)
- On failure, fall back to embedded data in Python dicts
- No credits consumed

### API Base URL
- Config: `https://antonioblago.com/api/v1/mcp`
- Remote MCP: `https://mcp.visibly-ai.com/mcp`

## Test Structure

```
tests/
├── conftest.py                    # Shared fixtures, mock responses
├── test_classifier.py             # Keyword classifier (19 tests)
├── test_free_tools.py             # Free tools (18 tests)
├── test_paid_tools.py             # All paid tools (mocked API)
├── test_google_tools.py           # Google/project tools (mocked API)
├── test_api_client.py             # HTTP client behavior
├── test_server_registration.py    # Tool count & docstring validation
├── integration/                   # Live API tests (need VISIBLYAI_API_KEY)
│   ├── test_live_free_tools.py
│   └── test_live_paid_tools.py
└── e2e/                           # MCP protocol tests
```

### Running Tests
```bash
# Unit tests (fast, no API key)
pytest tests/ --ignore=tests/integration --ignore=tests/e2e -v

# Integration (needs API key, free tools only - safe)
VISIBLYAI_API_KEY=lc_xxx pytest tests/integration/test_live_free_tools.py -v

# Full integration (burns credits)
VISIBLYAI_API_KEY=lc_xxx pytest tests/integration/ -v -m expensive
```
