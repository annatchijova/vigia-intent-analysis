"""
B-216: tests/run_vigia_case.py crashed formatting a caie_fracture's None
severity with :.2f -- the OWL cases use a fracture schema (type/description)
that never populates severity, while most of the corpus uses the
fracture_type/severity schema. run_case() had no guard, so any OWL case
crashed the demo runner with TypeError before printing a verdict.

Confirmed empirically against the live corpus (2026-07-26) before fixing:
101 caie_fractures across data/cases/**/*.json and cases/**/*.json, 95 carry
a numeric severity, 6 (all in the two OWL cases) carry only type/description.

Fix: fracture_type falls back to the legacy `type` field, and severity
renders "N/A" (not a fabricated 0.00) when absent -- per this repo's own
honest-degradation doctrine (docs/ENGINEERING_DISCIPLINE.md 5.3: never emit
a result that looks correct when correctness cannot be guaranteed).
"""

from __future__ import annotations

import io
import sys
from contextlib import redirect_stdout
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "tests"))

from run_vigia_case import run_case  # noqa: E402


def _run_capturing_stdout(case_path: str) -> str:
    buf = io.StringIO()
    with redirect_stdout(buf):
        run_case(case_path)
    return buf.getvalue()


class TestSeverityNoneDoesNotCrash:
    def test_owl_nexus5_case_renders_without_crashing(self):
        out = _run_capturing_stdout(str(REPO / "data/cases/VIGIA-OWL-2019-COMPLETE.json"))
        assert "severity=N/A" in out
        assert "VERDICT" in out

    def test_owl_nexus5_short_case_renders_without_crashing(self):
        out = _run_capturing_stdout(str(REPO / "data/cases/OWL-NEXUS5-CASE.json"))
        assert "severity=N/A" in out


class TestSeverityWithValueStillRendersCorrectly:
    def test_case_with_real_severity_shows_the_numeric_value(self):
        out = _run_capturing_stdout(str(REPO / "cases/input/VIGIA-BREAK-012.json"))
        assert "severity=N/A" not in out
        assert "severity=0.90" in out or "severity=0." in out


class TestFractureTypeFallback:
    def test_legacy_type_field_used_when_fracture_type_absent(self):
        out = _run_capturing_stdout(str(REPO / "data/cases/VIGIA-OWL-2019-COMPLETE.json"))
        assert "[compartmentalization]" in out
        assert "[None]" not in out
