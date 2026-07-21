"""B-176 — pericial PDF setup must not mutate evidence before refusal."""
from __future__ import annotations

import sys
import types
from types import SimpleNamespace
from pathlib import Path

from vigia.tools.adversarial_nlp import VigiaAdversarialNLP


def _exporter() -> VigiaAdversarialNLP:
    """The path guard does not need the heavyweight NLP engine to be built."""
    return object.__new__(VigiaAdversarialNLP)


def _verdict() -> SimpleNamespace:
    return SimpleNamespace(timestamp="2026-07-21T12:34:56Z", document_id="b176")


def _install_fake_pdf_renderer(monkeypatch, calls: list[tuple[str, str]]) -> None:
    fake_reporter = types.ModuleType("vigia.forensics.forensic_reporter")

    def generate_forensic_pdf(verdict, output_path, case_metadata):
        calls.append((output_path, case_metadata["case_number"]))
        Path(output_path).write_text("synthetic PDF renderer output")

    fake_reporter.generate_forensic_pdf = generate_forensic_pdf
    monkeypatch.setitem(sys.modules, "vigia.forensics.forensic_reporter", fake_reporter)


def test_b176_refusal_does_not_create_configured_pdf_dir_inside_evidence(
    monkeypatch, tmp_path: Path
) -> None:
    evidence = tmp_path / "evidence"
    evidence.mkdir()
    calls: list[tuple[str, str]] = []
    _install_fake_pdf_renderer(monkeypatch, calls)
    monkeypatch.setenv("VIGIA_PERICIAL_PDF_ENABLED", "true")
    monkeypatch.setenv("VIGIA_EVIDENCE_DIR", str(evidence))
    monkeypatch.setenv("VIGIA_PERICIAL_PDF_DIR", str(evidence / "generated-reports"))

    result = _exporter()._export_pdf(_verdict(), "statement.txt", None)

    assert result is None
    assert calls == []
    assert list(evidence.iterdir()) == []


def test_b176_creates_external_pdf_dir_only_after_boundary_check(
    monkeypatch, tmp_path: Path
) -> None:
    evidence = tmp_path / "evidence"
    reports = tmp_path / "reports"
    evidence.mkdir()
    calls: list[tuple[str, str]] = []
    _install_fake_pdf_renderer(monkeypatch, calls)
    monkeypatch.setenv("VIGIA_PERICIAL_PDF_ENABLED", "true")
    monkeypatch.setenv("VIGIA_EVIDENCE_DIR", str(evidence))
    monkeypatch.setenv("VIGIA_PERICIAL_PDF_DIR", str(reports))

    result = _exporter()._export_pdf(_verdict(), "statement.txt", "case-176")

    assert result is not None
    assert Path(result).is_file()
    assert calls == [(result, "case-176")]
    assert list(evidence.iterdir()) == []
