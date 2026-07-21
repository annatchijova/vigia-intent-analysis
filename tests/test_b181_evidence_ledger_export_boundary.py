"""B-181 — ledger exports must remain outside immutable source evidence."""
from __future__ import annotations

from pathlib import Path

import pytest

from vigia.pipeline.security_evidence_registry import EvidenceLedger
from vigia.security.output_boundary import SecurityError


def test_b181_refuses_ledger_export_inside_evidence(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    evidence = tmp_path / "evidence"
    evidence.mkdir()
    monkeypatch.setenv("VIGIA_EVIDENCE_DIR", str(evidence))

    with pytest.raises(SecurityError, match="evidence"):
        EvidenceLedger().export_json(str(evidence / "ledger.json"))

    assert list(evidence.iterdir()) == []


def test_b181_refuses_ledger_export_through_symlinked_parent(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    evidence = tmp_path / "evidence"
    redirect = tmp_path / "ledger-redirect"
    evidence.mkdir()
    redirect.symlink_to(evidence, target_is_directory=True)
    monkeypatch.setenv("VIGIA_EVIDENCE_DIR", str(evidence))

    with pytest.raises(SecurityError, match="symlink|evidence"):
        EvidenceLedger().export_json(str(redirect / "ledger.json"))

    assert list(evidence.iterdir()) == []


def test_b181_allows_external_ledger_export(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    evidence = tmp_path / "evidence"
    output = tmp_path / "outputs" / "ledger.json"
    evidence.mkdir()
    monkeypatch.setenv("VIGIA_EVIDENCE_DIR", str(evidence))

    EvidenceLedger().export_json(str(output))

    assert output.is_file()
    assert list(evidence.iterdir()) == []
