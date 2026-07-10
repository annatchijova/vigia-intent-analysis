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

VEREDICTO DEL GATE (regla pre-registrada de Anna: aplicar solo si fixed>=1
AND broken==0 sobre los 199): medido autoritativo fixed=30, broken=3 →
**NO APLICADO** (fail-closed; el fix fue implementado, medido y REVERTIDO).
Los 3 broken (expected=INTENT, motor=SUSPICION) hoy pasan GRACIAS al colapso.
Baseline honesto post-B10: 140/199; con el fix sería 167/199 (neto +27).
Ver BUGS_PENDIENTES B-097 [NO APLICADO] para los números completos.

Los tests del colapso quedan como SENTINELAS xfail(strict=True) — mismo
patrón que BUG-NLP-002: el defecto sigue visible; si un fix futuro los hace
pasar, el xfail truena (XPASS) y obliga a retirar el marker junto con el
cierre del tracker y un nuevo gate.

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
    @pytest.mark.xfail(
        strict=True,
        reason="B-097 [NO APLICADO — gate negativo fixed=30/broken=3]: el "
        "colapso SUSPICION→INTENT del path motor sigue presente por decisión "
        "del gate pre-registrado. Si esto pasa (XPASS), se aplicó un fix: "
        "retirar el marker, cerrar B-097 y re-correr el gate de 199.",
    )
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

    @pytest.mark.xfail(
        strict=True,
        reason="B-097 [NO APLICADO]: SUSPICION_DETECTED todavía se sella "
        "INTENT (colapso). Sentinela — ver el marker de la clase E2E.",
    )
    def test_suspicion_detected_seals_suspicion(self):
        assert self._classify("SUSPICION_DETECTED") == "SUSPICION"

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
