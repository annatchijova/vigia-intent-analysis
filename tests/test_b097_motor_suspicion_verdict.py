"""
B-097 — el path motor colapsa SUSPICION→INTENT en el sellado.

Causa raíz (investigada 2026-07-10, 33/33 casos): el motor (_vigia_score)
calcula SUSPICION, B-075 lo mapea a la hipótesis SUSPICION_DETECTED, y
classify_agent_verdict la sube a INTENT ("SUSPICION" in hyp → INTENT) porque
históricamente SUSPICION no era un veredicto sellado. Desde el enforcement
§9.4-LIM, SUSPICION SÍ es un veredicto sellado real (EXIT_INTENT, piso de
alerta) — el colapso ya no tiene razón de ser.

Fix candidato (mínimo, label-blind): en classify_agent_verdict, hipótesis con
SUSPICION (sin INTENT/MALICIOUS) sella "SUSPICION" directamente.

HISTORIA DEL GATE: la regla pre-registrada original (fixed>=1 AND broken==0)
midió fixed=30/broken=3 → NO APLICADO fail-closed. Al día siguiente
(2026-07-10) Anna FIRMÓ la aplicación con validación por triple fuente
independiente sobre los 33 casos: (1) etiqueta ground-truth = SUSPICION en
los 30 recuperados; (2) banda interna del motor (0.10<score<=0.33 = banda
SUSPICION de B-076) — el motor calculaba bien, solo el sellado colapsaba;
(3) batch ciego Claude Code + Cronos (46 casos) confirmó SUSPICION. Los 3
expuestos (expected=INTENT, motor=SUSPICION — pasaban por accidente del
colapso) quedan como fallos honestos pendientes de revisión de datos
(conversión sub-tipificada, ver docs/B097_ROOT_CAUSE_ANALYSIS.md).

Estos tests son ahora la GUARDA DE REGRESIÓN del fix aplicado (eran
sentinelas xfail(strict=True) mientras estuvo NO APLICADO).

Los tests E2E usan casos REALES del corpus identificados en la investigación.
"""

from __future__ import annotations

from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent

# Casos reales medidos: motor=SUSPICION, expected=SUSPICION, sellado hoy=INTENT
REAL_CASES = [
    "data/cases/consolidated_canonical/VIGIA-CAN-014.json",
    "data/cases/VIGIA-BREAK-013.json",
    "data/cases/case_002_log_fabrication.json",
]


def _seal(case_rel: str) -> tuple:
    import sift_orchestrator as shim
    from vigia_agent import classify_agent_verdict, _signal_stats
    case = REPO / case_rel
    assert case.exists(), f"caso del corpus movido: {case_rel}"
    r = shim.SIFTOrchestrator(case_id=case.stem).analyze(log_path=str(case))
    ab = r.get("abduction", {})
    n_p, n_u = _signal_stats(r)
    return ab.get("best_hypothesis"), classify_agent_verdict(ab, n_p, n_u)


class TestMotorSuspicionSealsSuspicion:
    @pytest.mark.parametrize("case_rel", REAL_CASES)
    def test_motor_suspicion_case_seals_suspicion(self, case_rel):
        hyp, verdict = _seal(case_rel)
        # precondición de la investigación: el motor dijo SUSPICION
        assert hyp == "SUSPICION_DETECTED", (
            f"precondición rota: {case_rel} ya no produce SUSPICION_DETECTED "
            f"(hyp={hyp}) — re-investigar antes de tocar el test")
        assert verdict == "SUSPICION", (
            f"colapso B-097: motor dijo SUSPICION pero se selló {verdict}")


class TestUnitNoCollapse:
    def _classify(self, hyp):
        from vigia_agent import classify_agent_verdict
        return classify_agent_verdict(
            {"best_hypothesis": hyp, "is_conclusive": True}, 3, 0)

    def test_suspicion_detected_seals_suspicion(self):
        assert self._classify("SUSPICION_DETECTED") == "SUSPICION"

    def test_suspicion_has_own_exit_code_5(self):
        """El exit code de SUSPICION es PROPIO (5) — hasta B-097 compartía el
        3 con INTENT, confuso para consumidores del exit. INTENT conserva el
        3 (contrato histórico: todo exit 3 sellado hasta hoy era familia
        INTENT)."""
        from vigia_agent import _VERDICT_EXIT, EXIT_SUSPICION, EXIT_INTENT
        assert EXIT_SUSPICION == 5
        assert _VERDICT_EXIT["SUSPICION"] == EXIT_SUSPICION
        assert _VERDICT_EXIT["INTENT"] == EXIT_INTENT == 3
        # y ningún otro veredicto comparte el 5
        assert [k for k, v in _VERDICT_EXIT.items() if v == 5] == ["SUSPICION"]

    def test_intent_detected_still_intent(self):
        assert self._classify("INTENT_DETECTED") == "INTENT"

    def test_malicious_still_malice(self):
        assert self._classify("MALICIOUS_INTENT_DETECTED") == "MALICE"

    def test_ceiling_on_suspicion_is_noop(self):
        from vigia_agent import classify_agent_verdict
        v = classify_agent_verdict(
            {"best_hypothesis": "SUSPICION_DETECTED", "is_conclusive": True,
             "verdict_ceiling": "SUSPICION"}, 3, 0)
        assert v == "SUSPICION"
