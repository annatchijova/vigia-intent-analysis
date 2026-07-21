"""B-193 — legacy case-adapter exports are derived artifacts, not evidence."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from vigia.security.output_boundary import SecurityError
from vigia.tools.vigia_case_adapter import save_signals


def test_b193_refuses_case_adapter_export_inside_evidence(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    evidence = tmp_path / "evidence"
    evidence.mkdir()
    monkeypatch.setenv("VIGIA_EVIDENCE_DIR", str(evidence))

    with pytest.raises(SecurityError, match="evidence"):
        save_signals([], str(evidence / "derived.json"))

    assert list(evidence.iterdir()) == []


def test_b193_refuses_case_adapter_export_through_symlink(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    evidence = tmp_path / "evidence"
    redirect = tmp_path / "redirect"
    evidence.mkdir()
    redirect.symlink_to(evidence, target_is_directory=True)
    monkeypatch.setenv("VIGIA_EVIDENCE_DIR", str(evidence))

    with pytest.raises(SecurityError, match="symlink|evidence"):
        save_signals([], str(redirect / "derived.json"))

    assert list(evidence.iterdir()) == []


def test_b193_allows_private_case_adapter_export(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    evidence = tmp_path / "evidence"
    target = tmp_path / "private-work" / "derived.json"
    evidence.mkdir()
    monkeypatch.setenv("VIGIA_EVIDENCE_DIR", str(evidence))

    written = save_signals([{"artifact_id": "B193-001"}], str(target))

    assert Path(written) == target
    assert json.loads(target.read_text(encoding="utf-8")) == [{"artifact_id": "B193-001"}]
    assert list(evidence.iterdir()) == []
