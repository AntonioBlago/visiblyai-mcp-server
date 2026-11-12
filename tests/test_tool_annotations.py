"""Tool titles and MCP annotations from one table (karte-257 K9.1, K9.2, K9.4; chatgpt-plugin K12.1, K12.2)."""
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
HINTS = ("readOnlyHint", "destructiveHint", "openWorldHint")

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
                if kw.arg in HINTS:
                    hits.append(f"line {node.lineno}: {kw.arg}=")
                if kw.arg == "title" and isinstance(kw.value, ast.Constant):
                    hits.append(f"line {node.lineno}: title= literal")
        if isinstance(node, ast.Constant) and node.value in HINTS:
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

    # The 0.18.0 release stays documented; the current version is checked in K12.2.
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
        assert set(entry) == {"title", *HINTS, "justification"}

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
        assert set(definition["annotations"]) == set(HINTS)
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


# ---------------------------------------------------------------------------
# K12.1 (contract chatgpt-plugin v001): openWorldHint and justification
# ---------------------------------------------------------------------------

# Tools that query arbitrary public domains, URLs, live search results or public search data.
OPEN_WORLD_QUERIES = {
    "analyze_url_structure", "classify_keywords_advanced", "get_traffic_snapshot",
    "get_historical_traffic", "get_keywords", "get_competitors", "get_backlinks",
    "get_referring_domains", "validate_keywords", "crawl_website", "onpage_analysis", "check_serp",
    "query_fanout", "check_pagespeed", "audit_sitemap", "check_structured_data", "check_hreflang",
    "check_links", "seo_agent", "seo_workflow", "create_content_query",
}
# Rule (decision 2026-11-12): a justification that mentions sending outward means openWorldHint True.
SENDING_WORDS = re.compile(r"\b(sends|CMS|Buffer|webhook|publishes)\b")
# Named exceptions: they mention the CMS but send nothing to an external system.
SENDING_EXCEPTIONS = {
    "pull_live_article": "reads the live URL stored in the project, sends nothing",
    "create_cms_connection": "stores a new connection inside Visibly, sends nothing",
    "set_article_live_url": "stores the URL used later for writeback, sends nothing",
    "list_cms_connections": "lists stored connections, sends nothing",
    "get_article_workflow": "reads the stored transfer status, sends nothing",
    "delete_cms_connection": "removes the stored connection inside Visibly, sends nothing",
    "revoke_contentpilot_key": "revokes a key inside Visibly, sends nothing",
}
SENDING_TOOLS = {
    "publish_article", "update_cms_article", "change_article_status", "test_cms_connection",
    "approve_optimizer_suggestion", "undo_optimizer_suggestion", "create_social_post", "approve_social_post",
}
OPEN_WORLD = OPEN_WORLD_QUERIES | SENDING_TOOLS
TARGET_FIELDS = {"url", "domain", "target", "webhook_url"}
# Named exceptions (decision 2026-11-12), each only while project_id is required.
TARGET_FIELD_EXCEPTIONS = {
    "get_internal_links": "url is a lookup key inside the project's own stored crawl",
    "get_page_facts": "url is a lookup key inside the project's own stored crawl",
    "create_cms_connection": "webhook_url is stored for later deliveries; creating the connection sends nothing",
}
SENTENCE_PREFIXES = (
    ("readOnlyHint", "Read-only:", "Not read-only:"),
    ("destructiveHint", "Destructive:", "Not destructive:"),
    ("openWorldHint", "Open world:", "Closed world:"),
)


def _open_world_problems(table: dict) -> list[str]:
    return [f"{name}: openWorldHint={entry.get('openWorldHint')!r} is not a bool"
            for name, entry in table.items() if type(entry.get("openWorldHint")) is not bool]


def _target_field_problems(table: dict, schemas: dict) -> list[str]:
    """Tools with a url/domain/target input but openWorldHint False (project-scoped lookups excepted)."""
    problems = []
    for name, schema in sorted(schemas.items()):
        fields = TARGET_FIELDS & set(schema.get("properties", {}))
        if not fields or table[name]["openWorldHint"] is True:
            continue
        if name in TARGET_FIELD_EXCEPTIONS and "project_id" in schema.get("required", []):
            continue
        problems.append(f"{name}: input {sorted(fields)} with openWorldHint=False")
    return problems


def _justification_problems(table: dict) -> list[str]:
    problems, seen = [], {}
    for name, entry in table.items():
        text = entry.get("justification")
        if not isinstance(text, str) or not text.strip():
            problems.append(f"{name}: justification empty")
            continue
        if not 20 <= len(text) <= 300:
            problems.append(f"{name}: justification has {len(text)} characters (20..300)")
        if not text.isascii():
            problems.append(f"{name}: justification not ASCII")
        if text.casefold() in seen:
            problems.append(f"{name}: justification duplicates {seen[text.casefold()]}")
        seen.setdefault(text.casefold(), name)
        sentences = re.findall(r"[^.]+\.", text)
        if len(sentences) != 3 or "".join(sentences).strip() != text.strip():
            problems.append(f"{name}: justification needs exactly one sentence per hint")
            continue
        for sentence, (hint, yes, no) in zip(sentences, SENTENCE_PREFIXES):
            expected = yes if entry.get(hint) is True else no
            if not sentence.strip().startswith(expected):
                problems.append(f"{name}: sentence for {hint} must start with {expected!r}")
    return problems


def _sending_problems(table: dict) -> list[str]:
    """Justification mentions sends/CMS/Buffer/webhook/publishes but openWorldHint is False (named exceptions)."""
    problems = []
    for name, entry in sorted(table.items()):
        match = SENDING_WORDS.search(entry.get("justification") or "")
        if match and entry.get("openWorldHint") is not True and name not in SENDING_EXCEPTIONS:
            problems.append(f"{name}: justification mentions {match.group(0)!r} but openWorldHint=False")
    return problems


def _schemas() -> dict:
    return {tool.name: tool.inputSchema or {} for tool in _list_tools()}


def test_k12_1_open_world_explicit():
    """K12.1: Every TOOL_ANNOTATIONS entry carries openWorldHint as a bool; True exactly for open-world tools."""
    assert _open_world_problems(TOOL_ANNOTATIONS) == []
    actual = {name for name, entry in TOOL_ANNOTATIONS.items() if entry["openWorldHint"]}
    print(f"{len(actual)} Werkzeuge mit openWorldHint=true von {len(TOOL_ANNOTATIONS)}")
    assert actual == OPEN_WORLD, (sorted(actual - OPEN_WORLD), sorted(OPEN_WORLD - actual))
    for tool in _list_tools():
        assert tool.annotations.openWorldHint is TOOL_ANNOTATIONS[tool.name]["openWorldHint"], tool.name

    # Rule: sending outward means open world; the sending tools are exactly those found by the rule.
    assert _sending_problems(TOOL_ANNOTATIONS) == []
    by_rule = {name for name, entry in TOOL_ANNOTATIONS.items()
               if SENDING_WORDS.search(entry["justification"]) and name not in SENDING_EXCEPTIONS}
    assert by_rule == SENDING_TOOLS and len(SENDING_TOOLS) == 8, sorted(by_rule ^ SENDING_TOOLS)
    assert set(SENDING_EXCEPTIONS) <= set(TOOL_ANNOTATIONS)
    assert not any(TOOL_ANNOTATIONS[name]["openWorldHint"] for name in SENDING_EXCEPTIONS)
    for name in ("approve_optimizer_suggestion", "undo_optimizer_suggestion", "publish_article"):
        table = _copy_table()
        table[name]["openWorldHint"] = False
        assert _sending_problems(table)[0].startswith(name), name

    # Negative cases: missing key, None, int, string.
    for bad_value in ("missing", None, 1, "true"):
        table = _copy_table()
        if bad_value == "missing":
            del table["check_serp"]["openWorldHint"]
        else:
            table["check_serp"]["openWorldHint"] = bad_value
        shown = table["check_serp"].get("openWorldHint")
        assert _open_world_problems(table) == [f"check_serp: openWorldHint={shown!r} is not a bool"], bad_value


def test_k12_1_url_domain_open_world():
    """K12.1: A tool with input url, domain, target or webhook_url has openWorldHint True (named exceptions)."""
    schemas = _schemas()
    assert _target_field_problems(TOOL_ANNOTATIONS, schemas) == []
    with_target = sorted(name for name, schema in schemas.items()
                         if TARGET_FIELDS & set(schema.get("properties", {})))
    print(f"{len(with_target)} Werkzeuge mit url/domain/target: {with_target}")
    assert set(TARGET_FIELD_EXCEPTIONS) == {"get_internal_links", "get_page_facts", "create_cms_connection"}
    assert set(TARGET_FIELD_EXCEPTIONS) <= set(with_target)
    assert not any(TOOL_ANNOTATIONS[name]["openWorldHint"] for name in TARGET_FIELD_EXCEPTIONS)
    assert "webhook_url" in schemas["create_cms_connection"]["properties"]

    # Negative: an open-world tool switched to False, and a new tool with a `target` field.
    table = _copy_table()
    table["check_links"]["openWorldHint"] = False
    assert _target_field_problems(table, schemas) == ["check_links: input ['url'] with openWorldHint=False"]
    table = _copy_table()
    table["k12_probe"] = dict(TOOL_ANNOTATIONS["get_project"])
    probe_schemas = {**schemas, "k12_probe": {"properties": {"target": {"type": "string"}}}}
    assert _target_field_problems(table, probe_schemas) == ["k12_probe: input ['target'] with openWorldHint=False"]
    # The project-scoped exception holds only while project_id is required.
    loose = {**schemas, "get_page_facts": {"properties": {"url": {"type": "string"}}, "required": []}}
    assert _target_field_problems(TOOL_ANNOTATIONS, loose) == [
        "get_page_facts: input ['url'] with openWorldHint=False"]


def test_k12_1_justification_present():
    """K12.1: Every entry has a unique English justification of 20..300 characters, one sentence per hint."""
    assert _justification_problems(TOOL_ANNOTATIONS) == []

    def broken(**changes):
        table = _copy_table()
        table["get_keywords"].update(changes)
        return _justification_problems(table)

    own = TOOL_ANNOTATIONS["get_keywords"]["justification"]
    assert broken(justification="") == ["get_keywords: justification empty"]
    assert broken(justification=None) == ["get_keywords: justification empty"]
    assert any("duplicates" in p for p in broken(justification=TOOL_ANNOTATIONS["get_backlinks"]["justification"]))
    assert any("(20..300)" in p for p in broken(justification="Read-only: x."))
    assert any("(20..300)" in p for p in broken(justification="Not read-only: " + "x" * 290 + ". A. B."))
    assert any("one sentence per hint" in p for p in broken(justification="Not read-only: it reads keywords."))
    assert any("must start with 'Open world:'" in p
               for p in broken(justification=own.replace("Open world:", "Closed world:")))


# ---------------------------------------------------------------------------
# K12.2: three hints in the output, single source
# ---------------------------------------------------------------------------

def _three_hint_gaps(tools) -> list[str]:
    gaps = []
    for tool in tools:
        ann = tool.annotations
        missing = [hint for hint in HINTS if ann is None or type(getattr(ann, hint, None)) is not bool]
        if missing:
            gaps.append(f"{tool.name}: {missing}")
    return gaps


async def _tools_list_over_protocol():
    """tools/list through a real in-process MCP client session (JSON-RPC, no network)."""
    from mcp.shared.memory import create_connected_server_and_client_session

    async with create_connected_server_and_client_session(mcp._mcp_server) as session:
        result = await session.list_tools()
        return result.tools


def _literal_hits(root: Path, literal: str, allowed: set) -> list[str]:
    hits = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or "__pycache__" in path.parts or path.resolve() in allowed:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        hits += [f"{path.relative_to(root)}:{n}" for n, line in enumerate(text.splitlines(), 1) if literal in line]
    return hits


def test_k12_2_three_hints_in_list():
    """K12.2: tools/list (in-process) and tool_definitions() carry all three hints; version 0.19.0 with CHANGELOG."""
    tools = asyncio.run(_tools_list_over_protocol())
    assert len(tools) == EXPECTED_TOOL_COUNT
    assert _three_hint_gaps(tools) == []
    for tool in tools:
        entry = TOOL_ANNOTATIONS[tool.name]
        assert {hint: getattr(tool.annotations, hint) for hint in HINTS} == {hint: entry[hint] for hint in HINTS}
    print(f"{len(tools)} Werkzeuge ueber tools/list, alle mit drei Hinweisen")

    for definition in content_workflow_tools.tool_definitions():
        entry = TOOL_ANNOTATIONS[definition["name"]]
        assert definition["annotations"] == {hint: entry[hint] for hint in HINTS}, definition["name"]

    # Negative: a tool registered with only two hints is reported.
    from mcp.types import ToolAnnotations

    probe = "k12_2_probe_tool"

    def k12_2_probe_tool() -> str:
        """Probe tool registered by the test only."""
        return ""

    try:
        mcp.add_tool(k12_2_probe_tool, name=probe,
                     annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False))
        gaps = _three_hint_gaps(asyncio.run(_tools_list_over_protocol()))
        assert gaps == [f"{probe}: ['openWorldHint']"]
    finally:
        mcp._tool_manager._tools.pop(probe, None)
    assert len(_list_tools()) == EXPECTED_TOOL_COUNT

    assert visiblyai_mcp.__version__ == "0.19.0"
    changelog = (REPO_ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    section = re.search(r"^## \[0\.19\.0\].*?(?=^## \[)", changelog, re.S | re.M)
    assert section, "CHANGELOG.md has no 0.19.0 section"
    assert "openWorldHint" in section.group(0)
    assert "nicht auf PyPI veröffentlicht" in section.group(0)


def test_k12_2_single_source(tmp_path):
    """K12.2: The literal openWorldHint appears in src/ only in annotations.py (like grep -rn)."""
    src = REPO_ROOT / "src"
    allowed = {(PACKAGE_DIR / "tools" / "annotations.py").resolve()}
    assert _literal_hits(src, "openWorldHint", allowed) == []
    assert _literal_hits(src, "openWorldHint", set()), "annotations.py must define the hint"
    for path in (SERVER_PY, WORKFLOW_PY):
        assert _hardcoded_hits(path.read_text(encoding="utf-8")) == [], path.name
    assert _hardcoded_hits("f(openWorldHint=True)") and _hardcoded_hits("x = {'openWorldHint': False}")

    # Negative: a stray literal in another source file is found.
    (tmp_path / "pkg").mkdir()
    (tmp_path / "pkg" / "server.py").write_text("ann = {'openWorldHint': True}\n", encoding="utf-8")
    assert _literal_hits(tmp_path, "openWorldHint", set()) == [str(Path("pkg") / "server.py") + ":1"]
