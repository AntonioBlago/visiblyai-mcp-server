# Workflow: Bug Fix

## Trigger
`Run the bug-fix workflow for [description]`

## Steps

### 1. Reproduce
- Identify which tool fails and with what error
- Run the tool in isolation with the same parameters
- Determine: is it API-side (backend) or client-side (PyPI package)?

### 2. Diagnose
- **API error (4xx/5xx)**: Check `_handle_response` in `api_client.py`. Compare with backend routes in Bikefitting project's `mcp_api_routes.py`.
- **Parsing error**: Check if response shape changed. Compare expected keys.
- **Parameter mismatch**: Check if tool function passes correct args to API client method.
- **Import/init error**: Check if all dependencies are available.

### 3. Fix
- Apply fix following existing code patterns
- Keep changes minimal and focused
- If backend change needed, note it for separate deployment

### 4. Regression Test
- Write a test that reproduces the original bug
- Verify the fix makes the test pass
- Add to appropriate test file

### 5. Full Test Suite
```bash
pytest tests/ --ignore=tests/integration --ignore=tests/e2e -v
```
**Gate: ALL tests must pass.**

### 6. Update Feedback
- Update `.claude/memory/TEST_RESULTS.md` with fix details
- Note: what broke, why, how it was fixed

## Checklist
- [ ] Bug reproduced
- [ ] Root cause identified
- [ ] Fix applied
- [ ] Regression test written
- [ ] Full test suite passes
- [ ] Feedback log updated
