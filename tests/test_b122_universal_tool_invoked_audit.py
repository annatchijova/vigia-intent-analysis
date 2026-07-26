"""
B-122: originally documented as "20 of 23 MCP tools lack TOOL_INVOKED
logging" -- only generate_forensic_hash, read_evidence, and list_files had
their own audit_logger.log_info(event_type="TOOL_INVOKED", ...) call, with
the remaining 20 deferred to a dedicated session because instrumenting all
of them individually would add ~20 more synchronous fsync() calls per
investigation (see security.py's ConfigAuditMonitor -- each log_info() does
open+flock+write+flush+fsync+close).

Re-investigated (2026-07-26) while fixing an unrelated "21 tools" count
discrepancy across the docs: the codebase now has exactly ONE registration
path for MCP tools, _register_mcp_tool() (vigia_sift_bridge.py), which wraps
every tool -- decorator style (@_register_mcp_tool) and call style
(_register_mcp_tool(func) for the optional/gated tools) alike -- with
_audit_mcp_entry(), which itself calls
audit_logger.log_info(event_type="TOOL_INVOKED", ...) BEFORE the wrapped
function runs. Confirmed by:

- `grep -c "mcp.tool()"` on vigia_sift_bridge.py: exactly 1 occurrence,
  inside _register_mcp_tool -- there is no other way to register a tool in
  this file.
- AST walk: every one of the 22 base tools (decorator style) and the 5
  always-loaded optional tools (call style) resolves to _register_mcp_tool.
- Direct execution: calling deactivate_honey_token and
  get_phonetic_dict_stats (both on B-122's original "NOT covered" list)
  produces a TOOL_INVOKED audit_logger event, with no per-tool code changes
  needed -- the coverage was already universal by construction.

This resolves B-122's underlying concern via a stronger mechanism than the
one the bug proposed (uniform coverage at the registration boundary, not
20 individual instrumentation sites) -- and sidesteps the fsync-cost
objection differently: the cost was already being paid for every tool call
by the time this was checked, so there's no new perf regression to weigh --
this test only locks in that the existing behavior doesn't regress.

Also corrects a stale detail in B-122's original "NOT covered (20)" list:
check_syscall_latency was listed as an uninstrumented MCP tool, but it is
not decorated with @_register_mcp_tool and has zero callers anywhere in the
file -- it was never an MCP tool at all (likely dead code), so it was never
part of either count.
"""

from __future__ import annotations

import asyncio
from unittest.mock import patch

import pytest

import vigia.vigia_sift_bridge as bridge


def _tool_invoked_events(captured: list) -> list:
    return [c for c in captured if c[1].get("event_type") == "TOOL_INVOKED"]


class TestRegistrationIsTheSoleMcpToolPath:
    def test_mcp_tool_decorator_called_exactly_once_in_the_module(self):
        """If a second mcp.tool() call site is ever added outside
        _register_mcp_tool, it would bypass the audit wrapper -- this guard
        makes that change visible instead of silent."""
        import inspect

        src = inspect.getsource(bridge)
        assert src.count("mcp.tool()") == 1, (
            "mcp.tool() is called more than once -- a new tool-registration "
            "path may bypass _audit_mcp_entry's TOOL_INVOKED logging. "
            "Re-verify universal audit coverage before trusting this test."
        )

    def test_register_mcp_tool_wraps_with_audit_entry(self):
        import inspect

        src = inspect.getsource(bridge._register_mcp_tool)
        assert "_audit_mcp_entry" in src


class TestPreviouslyUninstrumentedToolsNowEmitToolInvoked:
    """These specific tools were named in B-122's original "NOT covered"
    list. Each must now emit TOOL_INVOKED without any per-tool code change."""

    def _call_and_capture(self, coro) -> list:
        captured = []
        orig = bridge.audit_logger.log_info

        def spy(*args, **kwargs):
            captured.append((args, kwargs))
            return orig(*args, **kwargs)

        with patch.object(bridge.audit_logger, "log_info", side_effect=spy):
            try:
                asyncio.run(coro)
            except Exception:
                pass  # only auditing matters here, not the tool's own result
        return captured

    def test_deactivate_honey_token_emits_tool_invoked(self):
        captured = self._call_and_capture(
            bridge.deactivate_honey_token(file_path="/nonexistent/x.txt")
        )
        events = _tool_invoked_events(captured)
        assert len(events) == 1
        assert events[0][1]["tool"] == "deactivate_honey_token"

    def test_get_phonetic_dict_stats_emits_tool_invoked(self):
        captured = self._call_and_capture(bridge.get_phonetic_dict_stats())
        events = _tool_invoked_events(captured)
        assert len(events) == 1
        assert events[0][1]["tool"] == "get_phonetic_dict_stats"


class TestCheckSyscallLatencyWasNeverAnMcpTool:
    def test_check_syscall_latency_has_no_register_decorator(self):
        import inspect

        src = inspect.getsource(bridge)
        lines = src.splitlines()
        idx = next(
            i for i, line in enumerate(lines)
            if line.strip().startswith("async def check_syscall_latency")
        )
        preceding = "\n".join(lines[max(0, idx - 3):idx])
        assert "_register_mcp_tool" not in preceding

    def test_check_syscall_latency_has_no_callers(self):
        import subprocess

        repo_root = __file__.rsplit("/tests/", 1)[0]
        result = subprocess.run(
            ["grep", "-rn", r"check_syscall_latency(", "--include=*.py", "."],
            cwd=repo_root, capture_output=True, text=True,
        )
        callers = [
            line for line in result.stdout.splitlines()
            if "def check_syscall_latency" not in line and "/tests/" not in line
        ]
        assert callers == [], (
            f"check_syscall_latency now has callers: {callers} -- it may no "
            f"longer be dead code, revisit whether it should be registered "
            f"as an MCP tool."
        )
