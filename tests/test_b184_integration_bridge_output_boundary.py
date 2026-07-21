"""B-184 — integration bridge outputs must remain outside source evidence."""
from __future__ import annotations

import json
import sys
import types
from pathlib import Path

import pytest

from vigia.pipeline import vigia_integration_bridge as bridge
from vigia.security.output_boundary import SecurityError


def _case(case_id: str = "b184") -> dict:
    return {
        "case_id": case_id,
        "artifacts": [
            {
                "artifact_id": "synthetic-artifact",
                "evidence_type": "log_entry",
                "raw_score": 0.5,
                "source_tool": "synthetic",
            }
        ],
    }


def _pipeline_result() -> dict:
    return {
        "decision": "ABSTAIN",
        "posterior": 0.5,
        "risk": 0.1,
        "bundle_hash": "synthetic",
        "bundle_json": json.dumps({}),
        "narrative": None,
        "verify": {"passed": True, "message": "synthetic"},
        "mode": "SYNTHETIC",
    }


def _stub_pipeline(monkeypatch: pytest.MonkeyPatch, calls: list) -> None:
    def fake_run_vigia(**kwargs):
        calls.append(kwargs)
        return _pipeline_result()

    monkeypatch.setattr(bridge, "_PIPELINE_AVAILABLE", True)
    monkeypatch.setattr(bridge, "run_vigia", fake_run_vigia)


def test_b184_refuses_bridge_output_directory_inside_evidence(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    evidence = tmp_path / "evidence"
    output = evidence / "bridge-output"
    evidence.mkdir()
    monkeypatch.setenv("VIGIA_EVIDENCE_DIR", str(evidence))
    calls: list = []
    _stub_pipeline(monkeypatch, calls)
    engine = bridge.VigiaIntegrationEngine(output_dir=str(output))

    with pytest.raises(SecurityError, match="evidence"):
        engine.run_case(_case(), save_bundle=True, save_report=False)

    assert not output.exists()
    assert calls == []


def test_b184_refuses_bridge_output_directory_through_symlink(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    evidence = tmp_path / "evidence"
    redirect = tmp_path / "bridge-redirect"
    evidence.mkdir()
    redirect.symlink_to(evidence, target_is_directory=True)
    monkeypatch.setenv("VIGIA_EVIDENCE_DIR", str(evidence))
    calls: list = []
    _stub_pipeline(monkeypatch, calls)
    engine = bridge.VigiaIntegrationEngine(output_dir=str(redirect))

    with pytest.raises(SecurityError, match="symlink|evidence"):
        engine.run_case(_case(), save_bundle=True, save_report=False)

    assert list(evidence.iterdir()) == []
    assert calls == []


def test_b184_rejects_case_id_that_can_escape_report_output(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    evidence = tmp_path / "evidence"
    output = tmp_path / "results"
    evidence.mkdir()
    output.mkdir()
    # Precondition for the old traversal: atomic_write_text() would create
    # report_escape/../../evidence/pwn.json through this existing component.
    (output / "report_escape").mkdir()
    monkeypatch.setenv("VIGIA_EVIDENCE_DIR", str(evidence))
    calls: list = []
    _stub_pipeline(monkeypatch, calls)
    monkeypatch.setitem(
        sys.modules,
        "report_builder",
        types.SimpleNamespace(build_report=lambda **_kwargs: {"synthetic": True}),
    )
    engine = bridge.VigiaIntegrationEngine(output_dir=str(output))

    with pytest.raises(ValueError, match="case_id"):
        engine.run_case(
            _case("escape/../../evidence/pwn"),
            save_bundle=False,
            save_report=True,
        )

    assert list(evidence.iterdir()) == []
    assert calls == []


def test_b184_keeps_a_valid_bundle_output_external(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    evidence = tmp_path / "evidence"
    output = tmp_path / "results"
    evidence.mkdir()
    monkeypatch.setenv("VIGIA_EVIDENCE_DIR", str(evidence))
    calls: list = []
    _stub_pipeline(monkeypatch, calls)
    engine = bridge.VigiaIntegrationEngine(output_dir=str(output))

    result = engine.run_case(_case(), save_bundle=True, save_report=False)

    bundle = output / "bundle_b184.json"
    assert bundle.is_file()
    assert result["bundle_path"] == bundle.name
    assert len(calls) == 1
    assert list(evidence.iterdir()) == []
