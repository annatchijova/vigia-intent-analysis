"""B-183 — sealed bundles must not be published into source evidence."""
from __future__ import annotations

from pathlib import Path

import pytest

from vigia.core.bundle_builder import BundleBuilder
from vigia.security.output_boundary import SecurityError


def _sealed_fixture() -> dict:
    """A minimal serializable bundle is enough to exercise publication."""
    return {"case_id": "b183", "integrity": {"bundle_hash": "synthetic"}}


def test_b183_refuses_bundle_output_inside_evidence(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    evidence = tmp_path / "evidence"
    evidence.mkdir()
    monkeypatch.setenv("VIGIA_EVIDENCE_DIR", str(evidence))

    with pytest.raises(SecurityError, match="evidence"):
        BundleBuilder.save(_sealed_fixture(), str(evidence / "bundle.json"))

    assert list(evidence.iterdir()) == []


def test_b183_refuses_bundle_output_through_symlinked_parent(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    evidence = tmp_path / "evidence"
    redirect = tmp_path / "bundle-redirect"
    evidence.mkdir()
    redirect.symlink_to(evidence, target_is_directory=True)
    monkeypatch.setenv("VIGIA_EVIDENCE_DIR", str(evidence))

    with pytest.raises(SecurityError, match="symlink|evidence"):
        BundleBuilder.save(_sealed_fixture(), str(redirect / "bundle.json"))

    assert list(evidence.iterdir()) == []


def test_b183_writes_bundle_atomically_to_external_directory(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    evidence = tmp_path / "evidence"
    target = tmp_path / "results" / "bundle.json"
    evidence.mkdir()
    target.parent.mkdir()
    monkeypatch.setenv("VIGIA_EVIDENCE_DIR", str(evidence))

    returned_hash = BundleBuilder.save(_sealed_fixture(), str(target))

    assert target.is_file()
    assert returned_hash
    assert list(evidence.iterdir()) == []
