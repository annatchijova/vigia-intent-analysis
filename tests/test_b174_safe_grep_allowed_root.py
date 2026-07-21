"""B-174 — ``safe_grep`` must use component-aware allowed-root confinement.

String-prefix checks confuse a sibling such as ``evidence-escape`` with a
child of ``evidence``.  That is an authority-boundary bug when an MCP caller
supplies the search folder: the sandbox must reject the sibling before it
executes ``find`` or reads a byte from it.
"""
from __future__ import annotations

import asyncio
from pathlib import Path

from vigia.security.sandbox import safe_grep


def test_b174_rejects_sibling_with_allowed_root_text_prefix(tmp_path: Path) -> None:
    evidence = tmp_path / "evidence"
    sibling = tmp_path / "evidence-escape"
    evidence.mkdir()
    sibling.mkdir()
    (sibling / "private.txt").write_text("classified-only-outside-evidence\n")

    result = asyncio.run(
        safe_grep(
            "classified-only-outside-evidence",
            str(sibling),
            allowed_dirs=[str(evidence)],
        )
    )

    assert result["matches"] == []
    assert result["error"] is not None
    assert "outside allowed evidence directories" in result["error"]


def test_b174_allows_real_descendant_of_allowed_root(tmp_path: Path) -> None:
    evidence = tmp_path / "evidence"
    child = evidence / "nested"
    child.mkdir(parents=True)
    (child / "artifact.txt").write_text("needle-inside-evidence\n")

    result = asyncio.run(
        safe_grep(
            "needle-inside-evidence",
            str(child),
            allowed_dirs=[str(evidence)],
        )
    )

    assert result["error"] is None
    assert any("needle-inside-evidence" in match for match in result["matches"])
