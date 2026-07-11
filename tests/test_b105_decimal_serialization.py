"""Regression tests for B-105 — Decimal leak crashed case serialization.

Two CAIE Fracture constructors (LOG_VS_MEMORY at caie.py ~1374 and
NARRATIVE_POISONING_DETECTED at ~1932) passed `_dround(...)` — a Decimal —
as `severity`, violating the dataclass contract (`severity: float`). The
agent's canonical serializer correctly refuses unknown types, so the whole
case died with TypeError the moment such a fracture fired. The
NARRATIVE_POISONING trigger is additionally time-gated by evidence trust
decay, which made the crash a wall-clock time bomb: VIGIA-BREAK-016 sealed
MALICE for months and started returning NO_BUNDLE mid-day 2026-07-11 on
unchanged code.

Fixed behavior under test:
- the poisoning fracture path emits JSON-serializable severities;
- the serializer boundary encodes a stray Decimal exactly (as the bundle's
  __fraction__ convention) with a warning instead of destroying the case;
- the previously crashing corpus case seals end-to-end with its expected
  verdict.
"""

import json
import logging
import os
import subprocess
import sys
from decimal import Decimal
from fractions import Fraction

import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TestSerializerBoundary:
    def test_decimal_encoded_exactly_with_warning(self, caplog):
        from vigia_agent import _json_serial

        with caplog.at_level(logging.WARNING):
            encoded = _json_serial(Decimal("0.850000"))
        assert encoded == {"__fraction__": True,
                           "num": Fraction(Decimal("0.850000")).numerator,
                           "den": Fraction(Decimal("0.850000")).denominator}
        assert any("B-105" in r.getMessage() for r in caplog.records), (
            "a Decimal reaching the sealed payload is a type-contract "
            "violation and must be warned at the boundary"
        )

    def test_unknown_types_still_refused(self):
        from vigia_agent import _json_serial

        with pytest.raises(TypeError):
            _json_serial(object())


class TestNarrativePoisoningSeverityIsSerializable:
    def test_poisoning_fracture_fires_with_float_severity(self):
        # Deterministic trigger: a benignity-claiming narrative artifact plus
        # a high-score technical artifact contradicting it.
        import asyncio

        from vigia.tools.caie import cross_artifact_analysis

        artifacts = [
            {"artifact_id": "A-NAR", "evidence_type": "log_entry",
             "raw_score": 0.2, "source_tool": "helpdesk",
             "description": "ticket closed: confirmed benign, no threat",
             "prior_trust": 0.8, "provenance_chain": ["a"],
             "timestamp": "2026-01-01T10:00:00Z", "metadata": {}},
            {"artifact_id": "A-TEC", "evidence_type": "memory_process",
             "raw_score": 0.95, "source_tool": "volatility",
             "description": "beacon implant active in lsass memory",
             "prior_trust": 0.9, "provenance_chain": ["a"],
             "timestamp": "2026-01-01T10:05:00Z", "metadata": {}},
        ]
        result = asyncio.run(cross_artifact_analysis(artifacts))
        fractures = result.get("fractures", [])
        poisoning = [f for f in fractures
                     if f.get("type") == "NARRATIVE_POISONING_DETECTED"]
        assert poisoning, "trigger case must fire the poisoning fracture"
        # The whole result must be canonically serializable (the B-105 crash
        # path carried the raw Fracture dataclass with a Decimal severity;
        # the end-to-end test below pins that path — this pins the dict one).
        json.dumps(result, default=lambda o: (_ for _ in ()).throw(
            TypeError(f"non-serializable {type(o)!r} leaked: {o!r}")))


class TestBreak016EndToEnd:
    def test_previously_crashing_case_seals(self):
        case = os.path.join(REPO_ROOT, "data", "cases", "VIGIA-BREAK-016.json")
        if not os.path.isfile(case):
            pytest.skip("corpus case not present")
        # The agent's PathGuard rejects output paths outside its working
        # directory, so the bundle is written inside the repo and cleaned up.
        out = os.path.join(REPO_ROOT, "b016_regression_tmp_bundle.json")
        try:
            proc = subprocess.run(
                [sys.executable, os.path.join(REPO_ROOT, "vigia_agent.py"),
                 "--evidence", case, "--case-id", "VIGIA-BREAK-016",
                 "--output", out],
                capture_output=True, text=True, cwd=REPO_ROOT, timeout=120,
            )
            # Exit codes are verdicts (1 == MALICE, the expected label); a
            # crash exits 2 with no bundle.
            assert os.path.isfile(out), (
                f"agent produced no bundle (B-105 regression): "
                f"{proc.stderr[-500:]}"
            )
            with open(out, "r", encoding="utf-8") as f:
                bundle = json.load(f)
            assert bundle.get("agent_verdict") == "MALICE"
            assert proc.returncode == 1
        finally:
            for leftover in (out, out + ".sha256"):
                if os.path.exists(leftover):
                    os.unlink(leftover)


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
