"""B-182 — standalone forensic PDF exports must not alter source evidence."""
from __future__ import annotations

import importlib
import sys
import types
from io import BytesIO
from pathlib import Path

import pytest

from vigia.security.output_boundary import SecurityError


class _FakeDocument:
    """Avoid testing ReportLab while exercising the export filesystem boundary."""

    def __init__(self, buffer: BytesIO, **_kwargs) -> None:
        self._buffer = buffer

    def build(self, _elements) -> None:
        self._buffer.write(b"%PDF-1.4 synthetic report")


def _report() -> dict:
    return {
        "case": {"document_id": "b182", "analysis_timestamp": "2026-07-21T00:00:00Z"},
        "forensic_result": {
            "likelihood_ratio": "1.0",
            "posterior_probability": "0.5",
            "enfsi_label": "INCONCLUSIVE",
            "narrative": "Synthetic boundary test.",
        },
        "model_performance": {
            "auc": "0.5",
            "brier_score": "0.25",
            "expected_calibration_error": "0.0",
        },
        "plots": {},
        "signals": [],
        "model_traceability": {"dataset_hash": "synthetic", "calibration_date": "n/a"},
    }


class _Element:
    def __init__(self, *_args, **_kwargs) -> None:
        pass

    def setStyle(self, *_args, **_kwargs) -> None:
        pass


def _load_exporter(monkeypatch: pytest.MonkeyPatch):
    """Load the exporter with a renderer stub when ReportLab is unavailable."""
    reportlab = types.ModuleType("reportlab")
    reportlab.__path__ = []  # type: ignore[attr-defined]
    platypus = types.ModuleType("reportlab.platypus")
    platypus.SimpleDocTemplate = _FakeDocument
    platypus.Paragraph = _Element
    platypus.Spacer = _Element
    platypus.Image = _Element
    platypus.PageBreak = _Element
    platypus.Table = _Element
    platypus.TableStyle = _Element
    lib = types.ModuleType("reportlab.lib")
    lib.__path__ = []  # type: ignore[attr-defined]
    styles = types.ModuleType("reportlab.lib.styles")
    styles.getSampleStyleSheet = lambda: {
        "Title": object(), "Normal": object(), "Heading2": object(),
        "Heading3": object(), "Code": object(),
    }
    colors = types.ModuleType("reportlab.lib.colors")
    colors.black = object()
    colors.grey = object()
    pagesizes = types.ModuleType("reportlab.lib.pagesizes")
    pagesizes.A4 = object()
    for name, module in {
        "reportlab": reportlab,
        "reportlab.platypus": platypus,
        "reportlab.lib": lib,
        "reportlab.lib.styles": styles,
        "reportlab.lib.colors": colors,
        "reportlab.lib.pagesizes": pagesizes,
    }.items():
        monkeypatch.setitem(sys.modules, name, module)
    monkeypatch.delitem(sys.modules, "vigia.pipeline.report_exporter_v2", raising=False)
    return importlib.import_module("vigia.pipeline.report_exporter_v2")


def test_b182_refuses_pdf_export_inside_evidence(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    exporter = _load_exporter(monkeypatch)
    evidence = tmp_path / "evidence"
    evidence.mkdir()
    monkeypatch.setenv("VIGIA_EVIDENCE_DIR", str(evidence))

    with pytest.raises(SecurityError, match="evidence"):
        exporter.export_pdf(_report(), str(evidence / "report.pdf"))

    assert list(evidence.iterdir()) == []


def test_b182_refuses_pdf_export_through_symlinked_parent(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    exporter = _load_exporter(monkeypatch)
    evidence = tmp_path / "evidence"
    redirect = tmp_path / "pdf-redirect"
    evidence.mkdir()
    redirect.symlink_to(evidence, target_is_directory=True)
    monkeypatch.setenv("VIGIA_EVIDENCE_DIR", str(evidence))

    with pytest.raises(SecurityError, match="symlink|evidence"):
        exporter.export_pdf(_report(), str(redirect / "report.pdf"))

    assert list(evidence.iterdir()) == []


def test_b182_writes_pdf_atomically_to_external_directory(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    exporter = _load_exporter(monkeypatch)
    evidence = tmp_path / "evidence"
    target = tmp_path / "reports" / "report.pdf"
    evidence.mkdir()
    target.parent.mkdir()
    monkeypatch.setenv("VIGIA_EVIDENCE_DIR", str(evidence))

    result = exporter.export_pdf(_report(), str(target))

    assert Path(result["output_path"]) == target
    assert target.read_bytes() == b"%PDF-1.4 synthetic report"
    assert list(evidence.iterdir()) == []
