# Workflow: Publish to PyPI

## Trigger
`Run the publish workflow for [description]`

## Steps

### 1. Pre-flight Checks
```bash
git status
git diff --cached
```
- Verify no secrets in staged changes (.env, API keys, tokens)
- Verify version in `pyproject.toml` is bumped

### 2. Unit Tests
```bash
pytest tests/ --ignore=tests/integration --ignore=tests/e2e -v
```
**Gate: ALL tests must pass. Do not proceed if any fail.**

### 3. Build Package
```bash
python -m build --sdist --wheel
```
**Gate: Build must succeed without errors.**

### 4. Tool Count Validation
```bash
pytest tests/test_server_registration.py -v
```
**Gate: Tool count must match expected (23).**

### 5. Commit
- Stage specific files (not `git add .`)
- Write descriptive commit message
- Include `Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>` if AI-assisted

### 6. Tag
```bash
git tag v{version}  # Match pyproject.toml version
```

### 7. Push
```bash
git push origin master --tags
```

### 8. PyPI Upload
```bash
python -m twine upload dist/*
```
**Requires user confirmation before executing.**

### 9. Post-publish Verification
- Check PyPI page shows new version
- Test install: `pip install --upgrade visiblyai-mcp-server`
- Run quick smoke test: `python -c "from visiblyai_mcp.server import mcp; print('OK')"`

## Checklist
- [ ] Version bumped in `pyproject.toml`
- [ ] All unit tests pass
- [ ] Package builds cleanly
- [ ] Tool count matches expected
- [ ] Committed and tagged
- [ ] Pushed to remote
- [ ] Published to PyPI
- [ ] Verified installation
