"""
SECURITY.md <-> @rate_limit() drift contract.

SECURITY.md documents a table of MCP tool rate limits. It had drifted from
the actual @rate_limit(max_calls=N, ...) decorators in vigia_sift_bridge.py
in two ways simultaneously: `audit_network` was listed under the 5/min
"Sensitive" row but is actually decorated at 10/min, and
`deactivate_honey_token` (5/min in code) was missing from the table
entirely. Neither made the actual rate limiting wrong -- the code was
always the source of truth -- but the doc told an operator the wrong
number, the same claim/mechanism mismatch class of finding as the removed
HTTP/SSE auth-token theater.

This test closes the drift class the same way tests/test_requirements_ci_
contract.py does for requirements-ci.txt: parse both sources and assert
they agree, so a future rate-limit change that forgets to update SECURITY.md
fails CI instead of silently misleading whoever reads the doc.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
BRIDGE = REPO / "vigia" / "vigia_sift_bridge.py"
SECURITY_MD = REPO / "SECURITY.md"

_DECORATOR_RE = re.compile(
    r"@rate_limit\(\s*max_calls=(\d+)\s*,\s*window_seconds=(\d+)\s*,\s*"
    r"raise_on_limit=False\s*\)\s*\n\s*async def (\w+)\s*\("
)

_TABLE_ROW_RE = re.compile(r"^\|[^|]+\|(.+)\|\s*(\d+)/min\s*\|\s*$", re.MULTILINE)
_TOOL_NAME_RE = re.compile(r"`(\w+)`")


def _rate_limited_tools_in_code() -> dict[str, int]:
    src = BRIDGE.read_text(encoding="utf-8")
    return {
        name: int(max_calls)
        for max_calls, _window, name in _DECORATOR_RE.findall(src)
    }


def _rate_limited_tools_in_docs() -> dict[str, int]:
    doc = SECURITY_MD.read_text(encoding="utf-8")
    table_section = doc.split("### Rate Limiting", 1)[1].split("###", 1)[0]
    tools: dict[str, int] = {}
    for tools_cell, limit in _TABLE_ROW_RE.findall(table_section):
        for name in _TOOL_NAME_RE.findall(tools_cell):
            tools[name] = int(limit)
    return tools


class TestSecurityMdRateLimitContract:
    def test_every_documented_tool_limit_matches_code(self):
        code_limits = _rate_limited_tools_in_code()
        doc_limits = _rate_limited_tools_in_docs()

        assert doc_limits, "Failed to parse any rows out of SECURITY.md's rate-limit table"

        mismatches = {
            name: (doc_limit, code_limits.get(name))
            for name, doc_limit in doc_limits.items()
            if code_limits.get(name) != doc_limit
        }
        assert not mismatches, (
            "SECURITY.md rate-limit table disagrees with @rate_limit() in "
            f"vigia_sift_bridge.py (doc_limit, code_limit): {mismatches}"
        )

    def test_every_rate_limited_tool_is_documented(self):
        code_limits = _rate_limited_tools_in_code()
        doc_limits = _rate_limited_tools_in_docs()

        undocumented = sorted(set(code_limits) - set(doc_limits))
        assert not undocumented, (
            f"@rate_limit()-decorated tools missing from SECURITY.md's table: {undocumented}"
        )
