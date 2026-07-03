"""
tests/test_b057_decimal_severity.py
====================================
Regresión B-057: las fracturas del CAIE VIVO llevan severity como
decimal.Decimal; el scorer las multiplicaba por floats crudos → TypeError →
_vigia_score crasheaba entero en cuanto CAIE emitía una fractura maliciosa.
El crash enmascaraba un veredicto MALICE correcto (VIGIA-BREAK-016).
"""
from __future__ import annotations

import decimal
import json
import logging
from pathlib import Path

import pytest

logging.disable(logging.CRITICAL)

REPO = Path(__file__).resolve().parent.parent


class TestB057DecimalSeverity:
    def test_break_016_scores_instead_of_crashing(self):
        # El caso real que reprodujo el bug: CAIE vivo emite fracturas
        # maliciosas con severity Decimal.
        from vigia_scorer import _vigia_score
        case = json.loads((REPO / "data/cases/VIGIA-BREAK-016.json").read_text())
        result = _vigia_score(case)  # pre-fix: TypeError Decimal*float
        assert result["verdict"] == "MALICE"
        assert result["verdict"] == case.get("expected_verdict"), (
            "el crash enmascaraba el veredicto MALICE esperado"
        )

    def test_decimal_severity_in_json_fractures_no_crash(self):
        # Unit: fractura precalculada con severity Decimal (frontera exacta).
        from vigia_scorer import _vigia_score
        case = {
            "case_id": "T-B057",
            "artifacts": [
                {"artifact_id": f"A{i}", "evidence_type": t, "raw_score": 0.8,
                 "prior_trust": 0.9, "provenance_chain": ["a", "b", "c", "d"]}
                for i, t in enumerate(
                    ["memory_process", "log_entry", "network_flow"])
            ],
            "provenance_analysis": {"chain_status": "INTACT"},
            "temporal_violations": [
                {"type": "STATISTICAL_UNIFORMITY",
                 "severity": decimal.Decimal("0.8"),
                 "cause": {"artifact_id": "A0"}, "effect": {"artifact_id": "A1"}},
            ],
            "caie_fractures": [
                {"fracture_type": "FALSE_FLAG_PATTERN",
                 "severity": decimal.Decimal("0.9")},
                {"fracture_type": "VERDICT_CONFLICT",
                 "severity": decimal.Decimal("0.6")},
            ],
        }
        result = _vigia_score(case)
        assert "verdict" in result

    @pytest.mark.parametrize("bad", [None, "alto", float("nan"), float("inf")])
    def test_garbage_severity_uses_default(self, bad):
        # El shield no solo cubre Decimal: cualquier basura cae al default.
        from vigia_scorer import _vigia_score
        case = {
            "case_id": "T-B057-G",
            "artifacts": [{"artifact_id": "A", "evidence_type": "log_entry",
                           "raw_score": 0.5, "prior_trust": 0.8,
                           "provenance_chain": ["a", "b", "c", "d"]}],
            "provenance_analysis": {"chain_status": "INTACT"},
            "temporal_violations": [],
            "caie_fractures": [
                {"fracture_type": "FALSE_FLAG_PATTERN", "severity": bad},
            ],
        }
        result = _vigia_score(case)
        assert "verdict" in result
