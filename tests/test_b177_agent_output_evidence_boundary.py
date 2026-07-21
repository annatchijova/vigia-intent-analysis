"""B-177 — autonomous-agent result artifacts must stay outside evidence."""
from __future__ import annotations

from pathlib import Path

import pytest

from vigia_agent import _validate_agent_output_path


def test_b177_rejects_default_bundle_path_when_cwd_is_evidence(tmp_path: Path) -> None:
    evidence = tmp_path / "evidence"
    evidence.mkdir()

    with pytest.raises(ValueError, match="evidence"):
        _validate_agent_output_path(
            "CASE-177_bundle.json",
            working_directory=evidence,
            evidence_directory=evidence,
        )


def test_b177_rejects_explicit_output_nested_in_evidence(tmp_path: Path) -> None:
    work = tmp_path / "work"
    evidence = work / "evidence"
    evidence.mkdir(parents=True)

    with pytest.raises(ValueError, match="evidence"):
        _validate_agent_output_path(
            str(evidence / "result.json"),
            working_directory=work,
            evidence_directory=evidence,
        )


def test_b177_allows_sibling_results_directory(tmp_path: Path) -> None:
    work = tmp_path / "work"
    evidence = work / "evidence"
    results = work / "results"
    evidence.mkdir(parents=True)
    results.mkdir()

    assert _validate_agent_output_path(
        "results/CASE-177_bundle.json",
        working_directory=work,
        evidence_directory=evidence,
    ) == str(results / "CASE-177_bundle.json")
