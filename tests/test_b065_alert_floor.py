"""
Tests B-065 — el piso del nivel de alerta se calcula sobre el veredicto final.

Bug: 44 bundles del corpus sellaban "Verdict: MALICE" junto a
"LOW — No significant anomalies detected in this iteration.". El floor B-028
usaba un proxy (is_conclusive + substring de la hipótesis) que estaba muerto
para evidencia distribuida no-concluyente — exactamente la población que lo
necesitaba. Reproducido en fresco con VIGIA-CAN-004 (4 señales z<0.5,
posterior 463/10000, is_conclusive=False, hipótesis MALICIOUS_INTENT_DETECTED).

Fix aprobado (A+B):
  A) el piso se calcula con classify_agent_verdict — el mismo camino único
     que sella agent_verdict y decide el exit code (lección B-058).
  B) LOW describe magnitud por señal y nunca afirma benignidad; cuando el
     veredicto y la magnitud divergen se emite una línea de reconciliación.
"""

from fractions import Fraction

from vigia_agent import VIGIAAgent, classify_agent_verdict


def _results(hypothesis, posterior, is_conclusive, n_signals=4, z=0.4):
    return {
        "signals": [
            {"tool": f"T{i}", "z_score": z, "confidence": 0.9,
             "value": 0.5, "metadata": {}}
            for i in range(n_signals)
        ],
        "abduction": {
            "best_hypothesis": hypothesis,
            "best_posterior": posterior,
            "is_conclusive": is_conclusive,
            "narrative": "x",
        },
        "results": {},
    }


def _narrative(results, case_id="T-B065"):
    return VIGIAAgent(case_id, ".")._generate_narrative(results, "c" * 64)


class TestB065MaliceFloor:
    def test_can004_shape_non_conclusive_malice_floors_to_medium(self):
        """La forma exacta del bug: MALICE distribuido, posterior < 1/8,
        is_conclusive=False → el proxy viejo dejaba LOW."""
        res = _results("MALICIOUS_INTENT_DETECTED", "463/10000", False)
        assert classify_agent_verdict(res["abduction"], 4) == "MALICE"
        nar = _narrative(res)
        assert "No significant anomalies" not in nar
        assert "MEDIUM — MALICE verdict" in nar
        assert "B-065" in nar

    def test_non_conclusive_malice_high_posterior_floors_to_high(self):
        res = _results("MALICIOUS_INTENT_DETECTED", "1/2", False)
        nar = _narrative(res)
        assert "HIGH — MALICE verdict" in nar

    def test_reconciliation_line_present_when_floored(self):
        res = _results("MALICIOUS_INTENT_DETECTED", "463/10000", False)
        nar = _narrative(res)
        assert "Reconciliation: verdict MALICE" in nar
        assert "Per-signal magnitude level was: LOW" in nar

    def test_high_z_malice_not_floored_no_reconciliation(self):
        # Con señales de alta magnitud el alert ya es alto por sí mismo:
        # no hay piso aplicado ni línea de reconciliación.
        res = _results("MALICIOUS_INTENT_DETECTED", "1/2", True, z=4.0)
        nar = _narrative(res)
        assert "CRITICAL —" in nar
        assert "Reconciliation:" not in nar


class TestB065LowWording:
    def test_low_never_claims_benignity(self):
        """Parte B: el texto LOW describe magnitud, no afirma 'sin anomalías'."""
        res = _results("NO_ANOMALY_DETECTED", "0/1", False)
        nar = _narrative(res)
        assert "No significant anomalies detected" not in nar
        assert "LOW (per-signal magnitude)" in nar

    def test_noise_verdict_keeps_low_without_reconciliation(self):
        res = _results("NO_ANOMALY_DETECTED", "0/1", False)
        assert classify_agent_verdict(res["abduction"], 4) == "NOISE"
        nar = _narrative(res)
        assert "Reconciliation:" not in nar


class TestB065IntentFloor:
    def test_intent_floors_regardless_of_conclusiveness(self):
        for conclusive in (True, False):
            res = _results("INTENT_DETECTED", "1/2", conclusive)
            nar = _narrative(res)
            assert "MEDIUM — INTENT verdict" in nar, f"is_conclusive={conclusive}"
            assert "No significant anomalies" not in nar

    def test_abstain_verdict_not_floored(self):
        # ABSTAIN no es MALICE/INTENT: la magnitud se reporta tal cual.
        res = _results("ABSTAIN_DETECTED", "0/1", False)
        assert classify_agent_verdict(res["abduction"], 4) == "ABSTAIN"
        nar = _narrative(res)
        assert "LOW (per-signal magnitude)" in nar
        assert "Reconciliation:" not in nar
