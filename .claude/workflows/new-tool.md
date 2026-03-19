# Workflow: Add a New MCP Tool

## Trigger
`Run the new-tool workflow for [tool-name]`

## Steps

### 1. Planning
- Determine the backend API endpoint (check `mcp_api_routes.py` in the Bikefitting project)
- Define parameters, response shape, and credit cost
- Decide: free tool (local) or paid tool (API proxy)?

### 2. API Client Method
- File: `src/visiblyai_mcp/api_client.py`
- Add method to `VisiblyAIClient` following existing pattern
- Use `self._post("/tools/{endpoint}", payload)` for paid tools
- Only include non-empty optional params in payload

### 3. Tool Function
- File: `src/visiblyai_mcp/tools/paid_tools.py` (or `free_tools.py`)
- Follow the `_require_key()` / `_format_result()` / `_handle_error()` pattern
- Validate required params before API call
- Cap limits to safe maximums

### 4. Server Registration
- File: `src/visiblyai_mcp/server.py`
- Add `@mcp.tool()` decorated function that delegates to the tool module
- Include a clear docstring (used as tool description in MCP)
- Place in correct section (Free / Paid / Google)

### 5. Unit Tests
- Add tests in `tests/test_paid_tools.py` (or appropriate file)
- Test: success, no API key, 402 error, empty required params
- Mock API via `patch.object(VisiblyAIClient, "method_name")`

### 6. Integration Test
- Add live test in `tests/integration/test_live_paid_tools.py`
- Guard with `VISIBLYAI_API_KEY` check
- Mark with `@pytest.mark.expensive` if it burns credits

### 7. Registration Test
- Update `EXPECTED_TOOLS` set in `tests/test_server_registration.py`
- Update expected count assertion

### 8. Documentation
- Update `README.md` tools table
- Update `.claude/memory/TOOLS.md`

### 9. Version Bump
- Update version in `pyproject.toml`

## Quality Gate
```bash
pytest tests/ --ignore=tests/integration --ignore=tests/e2e -v
```
All tests must pass before committing.
