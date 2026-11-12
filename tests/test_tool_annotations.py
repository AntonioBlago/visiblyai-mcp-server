"""Tool titles and MCP annotations from one table (contract karte-257, K9.1, K9.2, K9.4)."""
from __future__ import annotations

import ast
import asyncio
import re
from pathlib import Path

import pytest
from mcp.server.fastmcp import FastMCP

import visiblyai_mcp
from visiblyai_mcp.api_client import CONTENT_WORKFLOW_PATHS
from visiblyai_mcp.server import mcp
from visiblyai_mcp.tools import content_workflow_tools
from visiblyai_mcp.tools.annotations import (
    _ENTRIES,
    TOOL_ANNOTATIONS,
    _build_table,
    annotated_tool,
    tool_options,
)

PACKAGE_DIR = Path(visiblyai_mcp.__file__).parent
REPO_ROOT = Path(__file__).resolve().parent.parent
SERVER_PY = PACKAGE_DIR / "server.py"
WORKFLOW_PY = PACKAGE_DIR / "tools" / "content_workflow_tools.py"

EXPECTED_TOOL_COUNT = 91

# First word of every title; also the words that do not count as "non-verb" in group checks.
VERBS = {
    "Analyze", "Apply", "Approve", "Audit", "Change", "Check", "Classify", "Crawl", "Create",
    "Delete", "Edit", "Fetch", "Generate", "Get", "List", "Optimize", "Preview", "Publish",
    "Query", "Read", "Recall", "Regenerate", "Reject", "Restore", "Revoke", "Rotate", "Run",
    "Save", "Score", "Search", "Set", "Store", "Submit", "Test", "Undo", "Update", "Validate",
}
MINOR_WORDS = {"a", "an", "and", "for", "from", "in", "of", "on", "or", "the", "to", "with"}
PRODUCT_NAMES = ("visibly", "contentpilot")
DESTRUCTIVE_TITLE_VERBS = {"Delete", "Revoke", "Publish", "Send", "Approve", "Restore", "Overwrite"}

DESTRUCTIVE_MINIMUM = {
    "delete_social_post", "delete_cms_connection", "publish_article", "change_article_status",
    "update_cms_article", "approve_optimizer_suggestion", "undo_optimizer_suggestion",
    "restore_article_backup", "revoke_contentpilot_key", "approve_social_post", "update_article",
    "edit_content_article", "regenerate_content_article", "set_article_live_url",
    "update_optimizer_settings",
    # E15
    "create_contentpilot_key", "test_cms_connection",
}
NOT_READONLY_MINIMUM = {
    "submit_article_draft", "save_content_query_draft", "create_content_query",
    "create_cms_connection", "create_contentpilot_key", "create_social_post", "remember",
    "import_meeting_apply", "generate_article_from_query", "run_content_optimizer",
    "reject_optimizer_suggestion",
}
# O3: reads that spend credits are not read-only.
CREDIT_READS = {
    "classify_keywords_advanced", "get_traffic_snapshot", "get_historical_traffic", "get_keywords",
    "get_competitors", "get_backlinks", "get_referring_domains", "validate_keywords",
    "crawl_website", "onpage_analysis", "check_serp", "query_fanout", "check_pagespeed",
    "audit_sitemap", "check_structured_data", "check_hreflang", "check_links", "seo_agent",
    "seo_workflow", "query_knowledge_base", "import_meeting_preview", "optimize_content_draft",
}
# Write routes of the app, listed explicitly (not by pattern). cms-pull is a read.
WRITE_ROUTES = {
    "/tools/content/create-query",
    "/tools/content/save-query-draft",
    "/tools/content/generate-article",
    "/tools/content/optimize-draft",
    "/tools/content/change-status",
    "/tools/content/edit-article",
    "/tools/content/regenerate-article",
    "/tools/content/cms/create",
    "/tools/content/cms/test",
    "/tools/content/cms/delete",
    "/tools/content/contentpilot-key/create",
    "/tools/content/contentpilot-key/revoke",
    "/tools/content/publish",
    "/tools/content/cms-update",
    "/tools/content/set-live-url",
    "/tools/content/restore-backup",
    "/tools/content/optimizer/settings/update",
    "/tools/content/optimizer/run",
    "/tools/content/optimizer/approve",
    "/tools/content/optimizer/reject",
    "/tools/content/optimizer/undo",
}


def _list_tools():
    return asyncio.run(mcp.list_tools())


# ---------------------------------------------------------------------------
# Check functions (used on the real code and on deliberately broken samples)
# ---------------------------------------------------------------------------

def _hardcoded_hits(source: str) -> list[str]:
    """Annotation values written outside annotations.py, found via AST."""
    hits = []
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Call):
            func = node.func
            fname = func.id if isinstance(func, ast.Name) else getattr(func, "attr", "")
            if fname == "ToolAnnotations":
                hits.append(f"line {node.lineno}: ToolAnnotations(")
            if (isinstance(func, ast.Attribute) and func.attr == "tool"
                    and isinstance(func.value, ast.Name) and func.value.id == "mcp"):
                hits.append(f"line {node.lineno}: mcp.tool( bypasses the table")
            for kw in node.keywords:
                if kw.arg in ("readOnlyHint", "destructiveHint"):
                    hits.append(f"line {node.lineno}: {kw.arg}=")
                if kw.arg == "title" and isinstance(kw.value, ast.Constant):
                    hits.append(f"line {node.lineno}: title= literal")
        if isinstance(node, ast.Constant) and node.value in ("readOnlyHint", "destructiveHint"):
            hits.append(f"line {node.lineno}: {node.value!r} key")
    return hits


def _hint_problems(table: dict) -> list[str]:
    problems = []
    for name, entry in table.items():
        for hint in ("readOnlyHint", "destructiveHint"):
            if type(entry.get(hint)) is not bool:
                problems.append(f"{name}: {hint}={entry.get(hint)!r} is not a bool")
        if entry.get("readOnlyHint") is True and entry.get("destructiveHint") is True:
            problems.append(f"{name}: readOnlyHint and destructiveHint both true")
    return problems


def _title_problems(title: str) -> list[str]:
    problems = []
    if not isinstance(title, str) or not 1 <= len(title) <= 64:
        return [f"{title!r}: length must be 1..64"]
    if not title.isascii():
        problems.append(f"{title!r}: not ASCII")
    if "–" in title or "—" in title:
        problems.append(f"{title!r}: dash")
    if "_" in title:
        problems.append(f"{title!r}: underscore")
    if title[-1] in ".,;:!?-":
        problems.append(f"{title!r}: trailing punctuation")
    words = title.split(" ")
    if words[0] not in VERBS:
        problems.append(f"{title!r}: does not start with a verb")
    for index, word in enumerate(words):
        if not word:
            problems.append(f"{title!r}: double space")
        elif index and word in MINOR_WORDS:
            continue
        elif not (word[0].isupper() or word[0].isdigit()):
            problems.append(f"{title!r}: {word!r} not in Title Case")
    return problems


def _duplicate_titles(titles: list[str]) -> list[str]:
    seen, dupes = set(), []
    for title in titles:
        key = title.casefold()
        if key in seen:
            dupes.append(title)
        seen.add(key)
    return dupes


def _non_verb_words(title: str) -> frozenset[str]:
    return frozenset(w.casefold() for w in title.split() if w not in VERBS and w.casefold() not in MINOR_WORDS)


def _annotation_gaps(tools) -> list[str]:
    """Names of listed tools without title, readOnlyHint or destructiveHint (None counts as missing)."""
    gaps = []
    for tool in tools:
        ann = tool.annotations
        if (not tool.title or ann is None or ann.readOnlyHint is None or ann.destructiveHint is None):
            gaps.append(tool.name)
    return sorted(gaps)


def _assert_all_annotated(tools, expected_count: int) -> None:
    gaps = _annotation_gaps(tools)
    print(f"{len(gaps)} ohne Annotation, {len(tools)} Werkzeuge")
    assert not gaps, f"{len(gaps)} ohne Annotation: {gaps}"
    assert len(tools) == expected_count, f"{len(tools)} Werkzeuge, erwartet {expected_count}"


def _classification_problems(table: dict) -> list[str]:
    problems = []
    for name in sorted(DESTRUCTIVE_MINIMUM):
        entry = table[name]
        if entry["destructiveHint"] is not True or entry["readOnlyHint"] is not False:
            problems.append(f"{name}: destructiveHint={entry['destructiveHint']}, "
                            f"readOnlyHint={entry['readOnlyHint']} (expected destructive)")
    for name in sorted(NOT_READONLY_MINIMUM | CREDIT_READS):
        if table[name]["readOnlyHint"] is not False:
            problems.append(f"{name}: readOnlyHint={table[name]['readOnlyHint']} (expected False)")
    return problems


def _readonly_write_route_problems(table: dict, paths: dict) -> list[str]:
    return [f"{name}: readOnlyHint=True but {paths[name]} is a write route"
            for name in sorted(paths) if table[name]["readOnlyHint"] and paths[name] in WRITE_ROUTES]


def _title_verb_problems(table: dict) -> list[str]:
    problems = []
    for name, entry in table.items():
        if entry["title"].split(" ")[0] in DESTRUCTIVE_TITLE_VERBS:
            if entry["destructiveHint"] is not True or entry["readOnlyHint"] is not False:
                problems.append(f"{name}: title {entry['title']!r} with readOnlyHint={entry['readOnlyHint']}, "
                                f"destructiveHint={entry['destructiveHint']}")
    return problems


def _copy_table() -> dict:
    return {name: dict(entry) for name, entry in TOOL_ANNOTATIONS.items()}


# ---------------------------------------------------------------------------
# K9.1
# ---------------------------------------------------------------------------

def test_k9_1_single_source():
    """K9.1: Titles and hints come only from annotations.py; registry equals table; version and CHANGELOG."""
    for path in (SERVER_PY, WORKFLOW_PY):
        assert _hardcoded_hits(path.read_text(encoding="utf-8")) == [], path.name

    # The checker catches hard-coded values (negative cases).
    for bad in ("ToolAnnotations(readOnlyHint=True)", "mcp.tool(title='Get Thing')(f)",
                "x = {'destructiveHint': False}", "f(readOnlyHint=False)", "mcp.tool()(f)"):
        assert _hardcoded_hits(bad), bad

    # 61 decorated tools in server.py, 30 from TOOLS, all through the table.
    tree = ast.parse(SERVER_PY.read_text(encoding="utf-8"))
    decorated = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)
                 and any(isinstance(d, ast.Name) and d.id == "_tool" for d in n.decorator_list)]
    assert len(decorated) == 61
    assert len(content_workflow_tools.TOOLS) == 30
    assert set(decorated) | {f.__name__ for f in content_workflow_tools.TOOLS} == set(TOOL_ANNOTATIONS)

    for tool in _list_tools():
        entry = TOOL_ANNOTATIONS[tool.name]
        assert tool.title == entry["title"], tool.name
        assert tool.annotations.readOnlyHint is entry["readOnlyHint"], tool.name
        assert tool.annotations.destructiveHint is entry["destructiveHint"], tool.name

    # A name without entry fails at registration time (i.e. at import of server.py).
    def k9_1_unlisted_tool() -> str:
        """Probe."""
        return ""

    with pytest.raises(KeyError, match="k9_1_unlisted_tool"):
        annotated_tool(FastMCP("k9-1-probe"))(k9_1_unlisted_tool)
    with pytest.raises(KeyError):
        tool_options("k9_1_unlisted_tool")

    assert visiblyai_mcp.__version__ == "0.18.0"
    changelog = (REPO_ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    section = re.search(r"^## \[0\.18\.0\].*?(?=^## \[)", changelog, re.S | re.M)
    assert section, "CHANGELOG.md has no 0.18.0 section"
    assert "nicht auf PyPI veröffentlicht" in section.group(0)
    pyproject = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert '"mcp[cli]>=1.10.0,<2.0.0"' in pyproject


def test_k9_1_no_dead_entries():
    """K9.1: Every table entry belongs to a registered tool and vice versa (no dead rows)."""
    registered = {tool.name for tool in _list_tools()}
    dead = set(TOOL_ANNOTATIONS) - registered
    missing = registered - set(TOOL_ANNOTATIONS)
    assert not dead, f"dead table entries: {sorted(dead)}"
    assert not missing, f"tools without entry: {sorted(missing)}"

    # Exactly one entry per name: the source rows hold no duplicates, and a duplicate fails.
    assert len(_ENTRIES) == len(TOOL_ANNOTATIONS)
    row = ("get_project", {"title": "Get Project Details", "readOnlyHint": True, "destructiveHint": False})
    with pytest.raises(ValueError, match="get_project"):
        _build_table((row, row))

    # Negative: an extra row is detected as dead.
    table = _copy_table()
    table["k9_1_ghost_tool"] = {"title": "Get Ghost", "readOnlyHint": True, "destructiveHint": False}
    assert set(table) - registered == {"k9_1_ghost_tool"}


def test_k9_1_hints_consistent():
    """K9.1: Both hints are explicit bools and never both true."""
    assert _hint_problems(TOOL_ANNOTATIONS) == []
    for entry in TOOL_ANNOTATIONS.values():
        assert set(entry) == {"title", "readOnlyHint", "destructiveHint"}

    both = {"x": {"title": "Get X", "readOnlyHint": True, "destructiveHint": True}}
    none = {"x": {"title": "Get X", "readOnlyHint": None, "destructiveHint": False}}
    missing = {"x": {"title": "Get X", "readOnlyHint": False}}
    for bad in (both, none, missing):
        assert _hint_problems(bad), bad


def test_k9_1_titles_readable():
    """K9.1: Titles are short English Title Case starting with a verb, unique, distinguishable."""
    titles = [entry["title"] for entry in TOOL_ANNOTATIONS.values()]
    problems = [p for title in titles for p in _title_problems(title)]
    assert problems == []
    assert _duplicate_titles(titles) == []

    with_product = [t for t in titles if any(p in t.casefold() for p in PRODUCT_NAMES)]
    assert len(with_product) <= 5, with_product

    groups = (
        {"update_article", "update_cms_article", "edit_content_article", "publish_article"},
        {"get_article", "list_articles"},
        {"delete_social_post", "approve_social_post"},
    )
    for group in groups:
        word_sets = {name: _non_verb_words(TOOL_ANNOTATIONS[name]["title"]) for name in group}
        names = sorted(group)
        for i, left in enumerate(names):
            for right in names[i + 1:]:
                assert word_sets[left] != word_sets[right], (left, right, word_sets[left])

    # Negative cases.
    for bad in ("Get " + "X" * 61, "Get Article – Draft", "Get_Article", "Keyword Classifier",
                "Get Article.", "get article", "Get draft Article", ""):
        assert _title_problems(bad), bad
    assert _duplicate_titles(["Update Article", "update article"]) == ["update article"]


def test_k9_1_definitions_match_list_tools():
    """K9.1: tool_definitions() carries title and annotations equal to list_tools()."""
    listed = {tool.name: tool for tool in _list_tools()}
    definitions = content_workflow_tools.tool_definitions()
    assert len(definitions) == 30
    for definition in definitions:
        tool = listed[definition["name"]]
        assert definition["title"] == tool.title
        assert definition["annotations"] == tool.annotations.model_dump(exclude_none=True)
        assert set(definition["annotations"]) == {"readOnlyHint", "destructiveHint"}
        assert definition["inputSchema"] == tool.inputSchema
        assert definition["description"] == tool.description


# ---------------------------------------------------------------------------
# K9.2
# ---------------------------------------------------------------------------

def test_k9_2_all_tools_annotated():
    """K9.2: list_tools() returns N tools, 0 without title or hints, N equals the table size."""
    tools = _list_tools()
    assert len(TOOL_ANNOTATIONS) == EXPECTED_TOOL_COUNT
    _assert_all_annotated(tools, len(TOOL_ANNOTATIONS))


def test_k9_2_new_tool_without_entry_fails():
    """K9.2: A tool registered without table entry turns the same check red and is removed again."""
    probe = "k9_2_probe_tool"

    def k9_2_probe_tool() -> str:
        """Probe tool registered by the test only."""
        return ""

    try:
        mcp.add_tool(k9_2_probe_tool, name=probe)
        tools = _list_tools()
        assert probe in {tool.name for tool in tools}
        with pytest.raises(AssertionError, match=probe):
            _assert_all_annotated(tools, len(TOOL_ANNOTATIONS))
    finally:
        mcp._tool_manager._tools.pop(probe, None)

    after = _list_tools()
    assert len(after) == len(TOOL_ANNOTATIONS)
    assert probe not in {tool.name for tool in after}


# ---------------------------------------------------------------------------
# K9.4
# ---------------------------------------------------------------------------

def test_k9_4_destructive_minimum():
    """K9.4: The listed tools are destructive and not read-only."""
    problems = [p for p in _classification_problems(TOOL_ANNOTATIONS) if "expected destructive" in p]
    assert problems == []

    table = _copy_table()
    table["publish_article"]["destructiveHint"] = False
    assert any(p.startswith("publish_article: destructiveHint=False") for p in _classification_problems(table))


def test_k9_4_not_readonly_minimum():
    """K9.4: Listed write tools and credit-spending reads (O3) are not read-only."""
    assert _classification_problems(TOOL_ANNOTATIONS) == []
    assert CREDIT_READS <= set(TOOL_ANNOTATIONS)

    for name in ("remember", "get_keywords"):
        table = _copy_table()
        table[name]["readOnlyHint"] = True
        table[name]["destructiveHint"] = False
        assert f"{name}: readOnlyHint=True (expected False)" in _classification_problems(table)


def test_k9_4_readonly_paths_are_reads():
    """K9.4: No read-only workflow tool points to a write route of the app."""
    assert WRITE_ROUTES <= set(CONTENT_WORKFLOW_PATHS.values()), WRITE_ROUTES - set(CONTENT_WORKFLOW_PATHS.values())
    assert CONTENT_WORKFLOW_PATHS["pull_live_article"] not in WRITE_ROUTES
    assert _readonly_write_route_problems(TOOL_ANNOTATIONS, CONTENT_WORKFLOW_PATHS) == []
    # Every write route belongs to a tool that is not read-only.
    for name, path in CONTENT_WORKFLOW_PATHS.items():
        if path in WRITE_ROUTES:
            assert TOOL_ANNOTATIONS[name]["readOnlyHint"] is False, name

    table = _copy_table()
    table["publish_article"].update(readOnlyHint=True, destructiveHint=False)
    assert _readonly_write_route_problems(table, CONTENT_WORKFLOW_PATHS) == [
        "publish_article: readOnlyHint=True but /tools/content/publish is a write route"]


def test_k9_4_title_verb_matches_hint():
    """K9.4: Titles starting with Delete, Revoke, Publish, Send, Approve, Restore or Overwrite are destructive."""
    assert _title_verb_problems(TOOL_ANNOTATIONS) == []

    bad = {"delete_social_post": {"title": "Delete Social Post", "readOnlyHint": True, "destructiveHint": False}}
    assert _title_verb_problems(bad)
