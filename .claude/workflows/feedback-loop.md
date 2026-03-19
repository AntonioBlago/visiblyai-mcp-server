# Workflow: Feedback Loop

## Trigger
`Run the feedback-loop workflow`

## Purpose
Read test results, analyze failures, fix issues, re-test, and track improvement over time.

## Steps

### 1. Collect
- Read `.claude/memory/TEST_RESULTS.md` for the latest test outcomes
- Run the full unit test suite fresh:
```bash
pytest tests/ --ignore=tests/integration --ignore=tests/e2e -v --tb=short 2>&1
```

### 2. Analyze
- Parse test output for PASSED/FAILED/ERROR counts
- Group failures by category:
  - **API errors**: Wrong endpoint, missing method, response shape
  - **Parsing issues**: JSON decode errors, missing keys
  - **Logic bugs**: Wrong parameter capping, incorrect validation
  - **Import errors**: Missing dependencies, circular imports

### 3. Prioritize
- Rank issues by:
  1. Blocking (prevents tool from working at all)
  2. Data integrity (returns wrong data)
  3. Edge cases (fails on unusual inputs)

### 4. Fix (Top 3)
- For each issue, follow the bug-fix workflow steps
- Apply minimal targeted fixes
- Write regression test for each fix

### 5. Re-test
```bash
pytest tests/ --ignore=tests/integration --ignore=tests/e2e -v --tb=short 2>&1
```

### 6. Update Feedback Log
Update `.claude/memory/TEST_RESULTS.md` with:
- Date of run
- Pass/fail counts (before and after)
- Issues fixed this cycle
- Remaining issues
- Improvement delta

### 7. Report
Present to user:
- Tests passing: X/Y (was A/B)
- Issues fixed this cycle: [list]
- Remaining issues: [list]
- Overall trend: improving/stable/degrading

## Schedule
Run this workflow:
- After every new tool addition
- After every bug fix
- Before every publish
- Weekly as maintenance
