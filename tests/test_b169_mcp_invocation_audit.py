"""Regression contract for MCP invocation records (L-057 / B-169)."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

pytest.importorskip("mcp.server.fastmcp")

import vigia.vigia_sift_bridge as bridge


@pytest.mark.asyncio
async def test_search_pattern_records_invocation_before_processing_sensitive_argument(monkeypatch):
    events = []

    def _record(**event):
        events.append(event)

    async def _empty_search(**_kwargs):
        return {"error": None, "matches": [], "truncated": False}

    monkeypatch.setattr(bridge.audit_logger, "log_info", _record)
    monkeypatch.setattr(bridge, "safe_grep", _empty_search)

    result = await bridge.search_pattern("needle-that-must-not-be-logged", ".")

    assert result == "Search completed with no findings."
    assert len(events) == 1
    assert events[0]["event_type"] == "TOOL_INVOKED"
    assert events[0]["tool"] == "search_pattern"
    assert "needle-that-must-not-be-logged" not in events[0]["message"]
    assert "sha256" in events[0]["message"]


@pytest.mark.asyncio
async def test_shared_boundary_preserves_synchronous_external_tool_results(monkeypatch):
    events = []

    def _record(**event):
        events.append(event)

    def external_fixture(document_id: int) -> dict:
        return {"document_id": document_id}

    monkeypatch.setattr(bridge.audit_logger, "log_info", _record)
    wrapped = bridge._audit_mcp_entry(external_fixture)

    assert await wrapped(7) == {"document_id": 7}
    assert events[0]["tool"] == "external_fixture"
    assert "document_id=7" in events[0]["message"]


def test_every_mcp_registration_flows_through_the_shared_invocation_audit_wrapper():
    source_path = Path(bridge.__file__)
    source = source_path.read_text(encoding="utf-8")
    tree = ast.parse(source)

    direct_decorators = [
        node.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and any(
            isinstance(decorator, ast.Call)
            and isinstance(decorator.func, ast.Attribute)
            and isinstance(decorator.func.value, ast.Name)
            and decorator.func.value.id == "mcp"
            and decorator.func.attr == "tool"
            for decorator in node.decorator_list
        )
    ]

    assert direct_decorators == []
    assert source.count("mcp.tool()") == 1
