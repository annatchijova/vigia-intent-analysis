"""B-189 — the canonical pipeline must not write results into evidence."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from vigia.scripts.run_pipeline import run
from vigia.security.output_boundary import SecurityError


def _input_case(path: Path) -> None:
    path.write_text(
        json.dumps(
            [
                {
                    "artifact_id": "B189-001",
                    "text": "routine administrative note",
                    "timestamp": "2026-01-01T00:00:00Z",
                }
            ]
        ),
        encoding="utf-8",
    )


def test_b189_refuses_pipeline_output_inside_evidence(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    evidence = tmp_path / "evidence"
    source = tmp_path / "input.json"
    evidence.mkdir()
    _input_case(source)
    monkeypatch.setenv("VIGIA_EVIDENCE_DIR", str(evidence))

    with pytest.raises(SecurityError, match="evidence"):
        run(str(source), str(evidence / "pipeline-result.json"), False)

    assert list(evidence.iterdir()) == []


def test_b189_refuses_pipeline_output_through_symlinked_parent(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    evidence = tmp_path / "evidence"
    source = tmp_path / "input.json"
    redirect = tmp_path / "result-redirect"
    evidence.mkdir()
    redirect.symlink_to(evidence, target_is_directory=True)
    _input_case(source)
    monkeypatch.setenv("VIGIA_EVIDENCE_DIR", str(evidence))

    with pytest.raises(SecurityError, match="symlink|evidence"):
        run(str(source), str(redirect / "pipeline-result.json"), False)

    assert list(evidence.iterdir()) == []


def test_b189_allows_external_pipeline_output(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    evidence = tmp_path / "evidence"
    source = tmp_path / "input.json"
    target = tmp_path / "private-work" / "pipeline-result.json"
    evidence.mkdir()
    _input_case(source)
    monkeypatch.setenv("VIGIA_EVIDENCE_DIR", str(evidence))

    run(str(source), str(target), False)

    assert target.is_file()
    assert json.loads(target.read_text(encoding="utf-8"))[0]["artifact_id"] == "B189-001"
    assert list(evidence.iterdir()) == []
