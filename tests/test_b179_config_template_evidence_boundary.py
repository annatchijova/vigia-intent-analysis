"""B-179 — configuration templates must not be emitted into evidence."""
from __future__ import annotations

from pathlib import Path

import pytest

from vigia.tools.adversarial_nlp import ConfigLoader
from vigia.tools.forensic_db import SecurityError


def test_b179_refuses_config_template_inside_evidence_before_creating_parent(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    evidence = tmp_path / "evidence"
    evidence.mkdir()
    monkeypatch.setenv("VIGIA_EVIDENCE_DIR", str(evidence))

    with pytest.raises(SecurityError, match="evidence"):
        ConfigLoader().save_default_config(str(evidence / "templates" / "defaults.json"))

    assert list(evidence.iterdir()) == []


def test_b179_writes_config_template_to_external_directory(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    evidence = tmp_path / "evidence"
    target = tmp_path / "config" / "defaults.json"
    evidence.mkdir()
    monkeypatch.setenv("VIGIA_EVIDENCE_DIR", str(evidence))

    ConfigLoader().save_default_config(str(target))

    assert target.is_file()
    assert list(evidence.iterdir()) == []


def test_b179_refuses_symlinked_config_parent_that_resolves_into_evidence(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    evidence = tmp_path / "evidence"
    redirect = tmp_path / "config-redirect"
    evidence.mkdir()
    redirect.symlink_to(evidence, target_is_directory=True)
    monkeypatch.setenv("VIGIA_EVIDENCE_DIR", str(evidence))

    with pytest.raises(SecurityError, match="symlink|evidence"):
        ConfigLoader().save_default_config(str(redirect / "defaults.json"))

    assert list(evidence.iterdir()) == []
