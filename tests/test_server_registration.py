"""Verify all expected MCP tools are registered in server.py."""

import ast
import pathlib
import pytest


EXPECTED_TOOLS = {
    # Free (8)
    "classify_keywords_simple",
    "seo_checklist",
    "seo_guidance",
    "get_google_guidelines",
    "analyze_url_structure",
    "get_account_info",
    "list_locations",
    "get_skill",
    # Paid (14)
    "classify_keywords_advanced",
    "get_traffic_snapshot",
    "get_historical_traffic",
    "get_keywords",
    "get_competitors",
    "get_backlinks",
    "get_referring_domains",
    "validate_keywords",
    "crawl_website",
    "onpage_analysis",
    "check_links",
    "seo_agent",
    "seo_workflow",
    "query_knowledge_base",
    # Google/Project (5)
    "list_projects",
    "get_project",
    "get_google_connections",
    "query_search_console",
    "query_analytics",
}


def _get_registered_tools() -> set[str]:
    """Parse server.py AST to find @mcp.tool() decorated functions."""
    server_py = pathlib.Path(__file__).parent.parent / "src" / "visiblyai_mcp" / "server.py"
    tree = ast.parse(server_py.read_text(encoding="utf-8"))

    tools = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            for dec in node.decorator_list:
                # Match @mcp.tool()
                if isinstance(dec, ast.Call) and isinstance(dec.func, ast.Attribute):
                    if dec.func.attr == "tool":
                        tools.add(node.name)
    return tools


class TestServerRegistration:
    def test_all_tools_registered(self):
        registered = _get_registered_tools()
        missing = EXPECTED_TOOLS - registered
        extra = registered - EXPECTED_TOOLS
        assert not missing, f"Missing tools: {missing}"
        assert not extra, f"Unexpected tools: {extra}"

    def test_tool_count(self):
        registered = _get_registered_tools()
        assert len(registered) == 27, f"Expected 27 tools, found {len(registered)}: {registered}"

    def test_all_tools_have_docstrings(self):
        server_py = pathlib.Path(__file__).parent.parent / "src" / "visiblyai_mcp" / "server.py"
        tree = ast.parse(server_py.read_text(encoding="utf-8"))

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                for dec in node.decorator_list:
                    if isinstance(dec, ast.Call) and isinstance(dec.func, ast.Attribute):
                        if dec.func.attr == "tool":
                            docstring = ast.get_docstring(node)
                            assert docstring, f"Tool '{node.name}' is missing a docstring"

    def test_no_duplicate_tool_names(self):
        server_py = pathlib.Path(__file__).parent.parent / "src" / "visiblyai_mcp" / "server.py"
        tree = ast.parse(server_py.read_text(encoding="utf-8"))

        names = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                for dec in node.decorator_list:
                    if isinstance(dec, ast.Call) and isinstance(dec.func, ast.Attribute):
                        if dec.func.attr == "tool":
                            names.append(node.name)

        assert len(names) == len(set(names)), f"Duplicate tool names: {[n for n in names if names.count(n) > 1]}"
