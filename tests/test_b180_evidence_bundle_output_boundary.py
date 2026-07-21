"""B-180 — evidence-package outputs must remain outside source evidence."""
from __future__ import annotations

from pathlib import Path

import pytest

from vigia.pipeline.evidence_bundle import build_evidence_bundle
from vigia.tools.forensic_db import SecurityError


def test_b180_refuses_bundle_output_directory_inside_source_evidence(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    evidence = tmp_path / "evidence"
    source_pdf = tmp_path / "external-report.pdf"
    evidence.mkdir()
    source_pdf.write_bytes(b"synthetic external report")
    monkeypatch.setenv("VIGIA_EVIDENCE_DIR", str(evidence))

    with pytest.raises(SecurityError, match="evidence"):
        build_evidence_bundle(
            pdf_path=str(source_pdf),
            ledger_dict={"events": []},
            output_dir=str(evidence),
            case_id="b180",
            metadata={"case": "b180"},
            zip_output=False,
        )

    assert list(evidence.iterdir()) == []


def test_b180_builds_bundle_in_external_output_directory(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    evidence = tmp_path / "evidence"
    output = tmp_path / "outputs"
    source_pdf = tmp_path / "external-report.pdf"
    evidence.mkdir()
    source_pdf.write_bytes(b"synthetic external report")
    monkeypatch.setenv("VIGIA_EVIDENCE_DIR", str(evidence))

    result = build_evidence_bundle(
        pdf_path=str(source_pdf),
        ledger_dict={"events": []},
        output_dir=str(output),
        case_id="b180",
        metadata={"case": "b180"},
        zip_output=False,
    )

    assert Path(result["bundle_dir"]).is_dir()
    assert (Path(result["bundle_dir"]) / "manifest.json").is_file()
    assert list(evidence.iterdir()) == []


def test_b180_refuses_case_id_path_traversal_into_evidence(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    evidence = tmp_path / "evidence"
    output = tmp_path / "outputs"
    source_pdf = tmp_path / "external-report.pdf"
    evidence.mkdir()
    source_pdf.write_bytes(b"synthetic external report")
    monkeypatch.setenv("VIGIA_EVIDENCE_DIR", str(evidence))

    with pytest.raises(SecurityError, match="Case ID"):
        build_evidence_bundle(
            pdf_path=str(source_pdf),
            ledger_dict={"events": []},
            output_dir=str(output),
            case_id="../evidence/b180",
            metadata={"case": "b180"},
            zip_output=False,
        )

    assert list(evidence.iterdir()) == []


def test_b180_refuses_symlinked_output_directory_into_evidence(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    evidence = tmp_path / "evidence"
    redirect = tmp_path / "output-redirect"
    source_pdf = tmp_path / "external-report.pdf"
    evidence.mkdir()
    redirect.symlink_to(evidence, target_is_directory=True)
    source_pdf.write_bytes(b"synthetic external report")
    monkeypatch.setenv("VIGIA_EVIDENCE_DIR", str(evidence))

    with pytest.raises(SecurityError, match="symlink|evidence"):
        build_evidence_bundle(
            pdf_path=str(source_pdf),
            ledger_dict={"events": []},
            output_dir=str(redirect),
            case_id="b180",
            metadata={"case": "b180"},
            zip_output=False,
        )

    assert list(evidence.iterdir()) == []
