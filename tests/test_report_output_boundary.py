"""vigia.report.writer must never write into VIGIA_EVIDENCE_DIR.

Same three checks as tests/test_b182_report_pdf_output_boundary.py for the
PDF exporter: refused inside the evidence directory, refused through a
symlinked parent, written atomically outside. Plus: write_all() produces the
four sibling files with the documented names and leaves the bundle bytes
untouched.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from tests.test_report_adapter import make_mcp_doc_kiwi
from vigia.report.writer import sibling_path, write_all, write_report
from vigia.security.output_boundary import SecurityError


def _write_bundle(path: Path) -> bytes:
    raw = json.dumps(make_mcp_doc_kiwi(), indent=2, sort_keys=True, ensure_ascii=True).encode()
    path.write_bytes(raw)
    return raw


def test_sibling_path_layout():
    assert sibling_path("/x/CASE-1_bundle.json", "junior", "es") == "/x/CASE-1_bundle_report_junior_es.md"
    assert sibling_path("CASE-1_bundle.json", "expert", "en") == "./CASE-1_bundle_report_expert_en.md"
    assert sibling_path("/x/CASE-1.bin", "junior", "en", output_dir="/out") == "/out/CASE-1.bin_report_junior_en.md"
    with pytest.raises(ValueError):
        sibling_path("a.json", "manager", "en")
    with pytest.raises(ValueError):
        sibling_path("a.json", "junior", "fr")


def test_refuses_report_inside_evidence(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    evidence = tmp_path / "evidence"
    evidence.mkdir()
    monkeypatch.setenv("VIGIA_EVIDENCE_DIR", str(evidence))

    with pytest.raises(SecurityError, match="evidence"):
        write_report("# x\n", str(evidence / "report.md"))

    assert list(evidence.iterdir()) == []


def test_refuses_report_through_symlinked_parent(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    evidence = tmp_path / "evidence"
    redirect = tmp_path / "redirect"
    evidence.mkdir()
    redirect.symlink_to(evidence, target_is_directory=True)
    monkeypatch.setenv("VIGIA_EVIDENCE_DIR", str(evidence))

    with pytest.raises(SecurityError, match="symlink|evidence"):
        write_report("# x\n", str(redirect / "report.md"))

    assert list(evidence.iterdir()) == []


def test_write_all_refuses_when_bundle_lives_in_evidence(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    """A bundle read from the evidence directory must not get siblings there."""
    evidence = tmp_path / "evidence"
    evidence.mkdir()
    bundle = evidence / "CASE_bundle.json"
    raw = _write_bundle(bundle)
    monkeypatch.setenv("VIGIA_EVIDENCE_DIR", str(evidence))

    with pytest.raises(SecurityError, match="evidence"):
        write_all(str(bundle))

    assert sorted(p.name for p in evidence.iterdir()) == ["CASE_bundle.json"]
    assert bundle.read_bytes() == raw

    # Redirected outside, the same bundle renders fine.
    out = tmp_path / "reports"
    written = write_all(str(bundle), output_dir=str(out))
    assert len(written) == 4
    assert sorted(p.name for p in evidence.iterdir()) == ["CASE_bundle.json"]


def test_write_all_writes_four_siblings_and_leaves_bundle_untouched(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
):
    evidence = tmp_path / "evidence"
    evidence.mkdir()
    monkeypatch.setenv("VIGIA_EVIDENCE_DIR", str(evidence))
    work = tmp_path / "work"
    work.mkdir()
    bundle = work / "VIGIA-KIWI-006_bundle.json"
    raw = _write_bundle(bundle)
    before = hashlib.sha256(raw).hexdigest()

    written = write_all(str(bundle))

    assert [Path(p).name for p in written] == [
        "VIGIA-KIWI-006_bundle_report_junior_en.md",
        "VIGIA-KIWI-006_bundle_report_junior_es.md",
        "VIGIA-KIWI-006_bundle_report_expert_en.md",
        "VIGIA-KIWI-006_bundle_report_expert_es.md",
    ]
    for p in written:
        text = Path(p).read_text(encoding="utf-8")
        assert text.startswith("# ")
        assert before in text, "report must bind itself to the bundle's SHA-256"
        assert "SUSPICION" in text
    assert hashlib.sha256(bundle.read_bytes()).hexdigest() == before
    assert list(evidence.iterdir()) == []


def test_write_all_rejects_unreadable_bundle(tmp_path: Path):
    bad = tmp_path / "bad.json"
    bad.write_text("not json")
    with pytest.raises(ValueError):
        write_all(str(bad))
    assert sorted(p.name for p in tmp_path.iterdir()) == ["bad.json"], "nothing written on failure"
