"""B-175 — graph exports must never write inside forensic evidence."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from vigia.abduction.vigia_artifact_graph import ArtifactGraphEngine, main


def _minimal_bundle() -> dict:
    return {
        "bundle_id": "b175-test",
        "abduction_trace": {},
        "evidence_graph": {},
    }


def test_b175_rejects_direct_graph_export_into_evidence(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    evidence = tmp_path / "evidence"
    evidence.mkdir()
    monkeypatch.setenv("VIGIA_EVIDENCE_DIR", str(evidence))

    with pytest.raises(ValueError, match="EVIDENCE_DIR"):
        ArtifactGraphEngine._validate_output_path(str(evidence / "graph.gexf"))


def test_b175_rejects_intermediate_symlink_in_output_path(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    evidence = tmp_path / "evidence"
    target = tmp_path / "redirect-target" / "nested"
    redirect = tmp_path / "redirect"
    evidence.mkdir()
    target.mkdir(parents=True)
    redirect.symlink_to(target.parent, target_is_directory=True)
    monkeypatch.setenv("VIGIA_EVIDENCE_DIR", str(evidence))

    with pytest.raises(ValueError, match="symlink"):
        ArtifactGraphEngine._validate_output_path(str(redirect / "nested" / "graph.gexf"))


def test_b175_json_cli_default_does_not_write_next_to_evidence_bundle(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    evidence = tmp_path / "evidence"
    evidence.mkdir()
    bundle_path = evidence / "case.json"
    bundle_path.write_text(json.dumps(_minimal_bundle()))
    monkeypatch.setenv("VIGIA_EVIDENCE_DIR", str(evidence))
    monkeypatch.setattr(sys, "argv", ["vigia_artifact_graph", "--bundle", str(bundle_path)])

    with pytest.raises(ValueError, match="EVIDENCE_DIR"):
        main()

    assert not (evidence / "case.graph.json").exists()


def test_b175_allows_output_in_real_child_of_permitted_root(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    reports = tmp_path / "reports"
    reports.mkdir()
    monkeypatch.delenv("VIGIA_EVIDENCE_DIR", raising=False)

    assert ArtifactGraphEngine._validate_output_path(str(reports / "graph.gexf")) == str(
        reports / "graph.gexf"
    )
