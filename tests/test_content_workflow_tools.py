"""Argument mapping for the full Visibly content workflow MCP tools."""
import json
from unittest.mock import MagicMock, patch

from visiblyai_mcp.tools import content_workflow_tools as tools
from visiblyai_mcp.api_client import APIError, VisiblyAIClient

OK = {"success": True, "data": {"result": {"status": "ok"}}, "credits_used": 0, "credits_remaining": None}


def _run(tool, name, *args, **kwargs):
    client = MagicMock()
    client.content_workflow.return_value = OK
    with patch("visiblyai_mcp.tools.content_workflow_tools.get_api_key", return_value="lc_test"), \
         patch("visiblyai_mcp.tools.content_workflow_tools.VisiblyAIClient", return_value=client):
        out = json.loads(tool(*args, **kwargs))
    return out, client.content_workflow.call_args


def test_create_query_and_generate_article_map_to_expected_workflow_paths():
    _, query_call = _run(tools.create_content_query, "create_content_query", 7, "bachata kurs", "de", "de", 4)
    assert query_call.args == ("create_content_query", {
        "project_id": 7, "keyword": "bachata kurs", "country": "de", "language": "de", "persona_id": 4,
    })
    _, generate_call = _run(tools.generate_article_from_query, "generate_article_from_query", 21, 7, True)
    assert generate_call.args == ("generate_article_from_query", {"query_id": 21, "project_id": 7, "improve": True})


def test_cms_connection_generation_does_not_require_caller_to_send_secret():
    _, call = _run(tools.create_cms_connection, "create_cms_connection", 7, "webhook",
                   label="Blog", webhook_url="https://site.example/webhook")
    assert call.args == ("create_cms_connection", {
        "project_id": 7, "cms_type": "webhook", "label": "Blog", "config": {},
        "webhook_events": ["article.approved", "article.updated"],
        "webhook_url": "https://site.example/webhook",
    })
    assert "webhook_secret" not in call.args[1]


def test_editor_save_publish_and_optimizer_actions_are_mapped():
    _, save_call = _run(tools.save_content_query_draft, "save_content_query_draft", 21, 3,
                        "<p>Draft</p>", "Title", "html", 7)
    assert save_call.args[0] == "save_content_query_draft"
    assert save_call.args[1]["expected_revision"] == 3
    _, publish_call = _run(tools.publish_article, "publish_article", 11, 7, 9, "publish")
    assert publish_call.args == ("publish_article", {
        "article_id": 11, "project_id": 7, "connection_id": 9, "publish_status": "publish",
    })
    _, optimize_call = _run(tools.optimize_content_draft, "optimize_content_draft", 21, "terms", "Draft", 7)
    assert optimize_call.args[0] == "optimize_content_draft"
    assert optimize_call.args[1]["kind"] == "terms"
    assert len({tool.__name__ for tool in tools.TOOLS}) == len(tools.TOOLS)


    def test_full_editor_and_version_operations_are_registered_and_revision_safe():
        _, edit_call = _run(tools.edit_content_article, "edit_content_article", 11, 7, title="New",
                search_intent="transactional", recommended_page_type="blog")
        payload = edit_call.args[1]
        assert edit_call.args[0] == "edit_content_article"
        assert payload["expected_revision"] == 7 and len(payload["idempotency_key"]) == 32
        _, restore_call = _run(tools.restore_article_backup, "restore_article_backup", 9, 3, 5)
        assert restore_call.args == ("restore_article_backup", {"backup_id": 9, "project_id": 3,
                                      "expected_revision": 5})
        names = {tool.__name__ for tool in tools.TOOLS}
        assert {"pull_live_article", "set_article_live_url", "list_article_backups",
            "get_article_backup", "restore_article_backup", "regenerate_content_article"} <= names


def test_client_uses_allowlisted_mcp_paths():
    client = VisiblyAIClient("lc_test")
    with patch.object(client, "_post", return_value=OK) as post:
        client.content_workflow("create_cms_connection", {"project_id": 7})
    post.assert_called_once_with("/tools/content/cms/create", {"project_id": 7})
    try:
        client.content_workflow("https://attacker.invalid", {})
    except APIError as exc:
        assert exc.status_code == 400
    else:
        raise AssertionError("unknown tool name must not become an arbitrary request path")


def test_server_registers_all_workflow_tools_without_name_collisions():
    from visiblyai_mcp.server import mcp

    registered = {tool.name for tool in mcp._tool_manager.list_tools()}
    assert {
        "create_content_query", "get_content_query", "save_content_query_draft",
        "generate_article_from_query", "edit_content_article", "regenerate_content_article",
        "pull_live_article", "list_article_backups", "restore_article_backup",
        "change_article_status", "create_cms_connection",
        "create_contentpilot_key", "publish_article", "run_content_optimizer",
        "approve_optimizer_suggestion", "optimize_content_draft",
    } <= registered
