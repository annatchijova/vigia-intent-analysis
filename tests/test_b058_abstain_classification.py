"""
tests/test_b058_abstain_classification.py
==========================================
Regresión B-058 (auditoría de invariantes 2026-07-03):
`classify_agent_verdict` hacía match EXACTO contra ABSTAIN_HYPOTHESES, pero el
adaptador EBS emite "ABSTAIN_DETECTED" (cuando expected_verdict==ABSTAIN), que
no estaba en el frozenset → caía a NOISE (exit 0). Un caso que el sistema
etiqueta explícitamente ABSTAIN se sellaba como benigno (familia P0-A).

Peor: run_all_agent.py:86 mapea ABSTAIN_DETECTED→ABSTAIN en SU comparador
(leyendo best_hypothesis, no el agent_verdict sellado) → el batch daba PASS
sobre un bundle con agent_verdict=NOISE. Divergencia entre dos caminos de
mapeo de veredicto.

Invariante: toda hipótesis cuyo nombre contiene "ABSTAIN" clasifica ABSTAIN.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path

import pytest

logging.disable(logging.CRITICAL)
REPO = Path(__file__).resolve().parent.parent


class TestB058AbstainClassification:
    @pytest.mark.parametrize("hyp,n,conc", [
        ("ABSTAIN_DETECTED", 3, False),   # el caso exacto del bug
        ("ABSTAIN_DETECTED", 5, True),    # aún conclusivo con muchas señales
        ("ABSTAIN_V2", 5, True),
        ("SOMETHING_ABSTAIN_X", 4, True),
    ])
    def test_any_abstain_hypothesis_maps_to_abstain(self, hyp, n, conc):
        from vigia_agent import classify_agent_verdict
        v = classify_agent_verdict({"best_hypothesis": hyp, "is_conclusive": conc}, n)
        assert v == "ABSTAIN", f"{hyp!r} debe clasificar ABSTAIN, no {v}"

    def test_ebs_abstain_case_seals_abstain_not_noise(self, monkeypatch):
        # El caso real del corpus: VIGIA-AMB-001 (expected ABSTAIN, 3 señales)
        # sellaba agent_verdict=NOISE/exit 0.
        # B-075 (flip 2026-07-05): este test ejercita la cadena
        # adaptador-legacy → classify (la etiqueta ABSTAIN debe honrarse en
        # esa rama, no degradar a NOISE). Se fija a legacy explícito; en modo
        # motor la hipótesis sale de la evidencia (AMB-001 → NOISE del motor,
        # el desacuerdo con la etiqueta es backlog de Fase 2).
        monkeypatch.setenv("VIGIA_EBS_RESOLVE", "legacy")
        from sift_orchestrator import SIFTOrchestrator
        from vigia_agent import classify_agent_verdict, _signal_stats
        case = json.loads((REPO / "data/cases/VIGIA-AMB-001.json").read_text())
        import tempfile, os
        f = tempfile.mktemp(suffix=".json")
        json.dump(case, open(f, "w"))
        try:
            result = SIFTOrchestrator("T-B058")._analyze_ebs_json(f)
        finally:
            os.unlink(f)
        assert result["abduction"]["best_hypothesis"] == "ABSTAIN_DETECTED"
        v = classify_agent_verdict(result["abduction"], *_signal_stats(result))
        assert v == "ABSTAIN", "un caso etiquetado ABSTAIN no puede sellar NOISE"

    def test_no_regression_on_other_verdicts(self):
        from vigia_agent import classify_agent_verdict
        assert classify_agent_verdict(
            {"best_hypothesis": "MALICIOUS_INTENT_DETECTED"}, 5) == "MALICE"
        assert classify_agent_verdict(
            {"best_hypothesis": "INTENT_DETECTED"}, 5) == "INTENT"
        assert classify_agent_verdict(
            {"best_hypothesis": "NO_SEMIOTIC_ANOMALY_DETECTED",
             "is_conclusive": True}, 5) == "NOISE"
        assert classify_agent_verdict(
            {"best_hypothesis": "NO_ANOMALY_DETECTED",
             "is_conclusive": True}, 5) == "NOISE"
