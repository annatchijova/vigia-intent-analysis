"""B-186 — the persistent chain ledger must never use source evidence."""
from __future__ import annotations

from pathlib import Path

import pytest

from vigia.forensics.vigia_chain_of_custody import ChainOfCustody


def test_b186_refuses_explicit_ledger_inside_evidence(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    evidence = tmp_path / "evidence"
    evidence.mkdir()
    monkeypatch.setenv("VIGIA_EVIDENCE_DIR", str(evidence))

    with pytest.raises(ValueError, match="evidence"):
        ChainOfCustody(str(evidence / "vigia_chain.db"))

    assert list(evidence.iterdir()) == []


def test_b186_refuses_ledger_through_symlinked_parent(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    evidence = tmp_path / "evidence"
    redirect = tmp_path / "ledger-redirect"
    evidence.mkdir()
    redirect.symlink_to(evidence, target_is_directory=True)
    monkeypatch.setenv("VIGIA_EVIDENCE_DIR", str(evidence))

    with pytest.raises(ValueError, match="symlink|evidence"):
        ChainOfCustody(str(redirect / "vigia_chain.db"))

    assert list(evidence.iterdir()) == []


def test_b186_default_ledger_uses_work_dir_even_from_evidence_cwd(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    evidence = tmp_path / "evidence"
    work = tmp_path / "work"
    evidence.mkdir()
    monkeypatch.chdir(evidence)
    monkeypatch.setenv("VIGIA_EVIDENCE_DIR", str(evidence))
    monkeypatch.setenv("VIGIA_WORK_DIR", str(work))
    monkeypatch.delenv("VIGIA_CHAIN_DB_PATH", raising=False)

    chain = ChainOfCustody()
    try:
        assert Path(chain.db_path) == work / "vigia_chain.db"
        assert Path(chain.db_path).is_file()
        assert list(evidence.iterdir()) == []
    finally:
        chain.close()


def test_b186_allows_explicit_external_ledger(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    evidence = tmp_path / "evidence"
    target = tmp_path / "work" / "vigia_chain.db"
    evidence.mkdir()
    monkeypatch.setenv("VIGIA_EVIDENCE_DIR", str(evidence))

    chain = ChainOfCustody(str(target))
    try:
        assert Path(chain.db_path) == target
        assert target.is_file()
        assert list(evidence.iterdir()) == []
    finally:
        chain.close()
