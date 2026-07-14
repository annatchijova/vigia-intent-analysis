"""
Fase 1 (PLAN_ABDUCTIVO_PENDIENTES_20260705 §3) — B-075: resolve() en el
adaptador EBS. Tests rojos escritos ANTES del fix (ENGINEERING_DISCIPLINE
§5.2 "provalo"): son la definición ejecutable de "resuelto" para P2-C.

La sorpresa (AUDITORIA_MOTOR_SIN_LABEL): sin `expected_verdict`, el agente
colapsa a NOISE 189/ABSTAIN 9 (cero detecciones) mientras el motor
determinista (`vigia_scorer._vigia_score`) produce la distribución real
(MALICE 108 / SUSPICION 35 / UNKNOWN 14 / NOISE 41). El único camino del
adaptador a un veredicto malicioso era la etiqueta (label leak,
`sift_orchestrator.py:620`), con el umbral `avg > 2` inalcanzable para
inputs normalizados [0,1].

Hipótesis rivales (bucle A–D–I):
- H2 (error de unidades): un umbral re-escalado sobre avg reproduciría la
  distribución del motor. REFUTADA por medición 2026-07-05: el mejor juego
  de umbrales posible sobre avg alcanza 58.6% de acuerdo 4-clases (74.7%
  binario) contra el motor ciego — las clases se solapan (MALICE avg
  min=0.000, NOISE avg max=0.788). El escalar no porta la información del
  ladder (TrustFusion → CAIE → gates Daubert).
- H3 (falta la función de selección — Aliseda): la selección formal entre
  hipótesis ya generadas EXISTE en el repo — es el ladder de decisión de
  `_vigia_score` (umbrales 0.33/0.18/0.08, hard gate temporal, gate de
  corroboración B-068). El adaptador nunca la llamaba; la etiqueta tapaba
  el hueco. CORROBORADA: resolve() = invocar esa selección canónica.

Modo de despliegue: VIGIA_EBS_RESOLVE=motor|legacy. Default **motor** desde
la decisión de doctrina (opción (a), flip 2026-07-05 — Anna): el corpus pasa
a medir detección real. Legacy queda solo como modo explícito de
reproducción/evaluación de bundles históricos; cualquier valor desconocido
cae a motor (el modo honesto), nunca a legacy.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import sift_orchestrator as so

REPO = Path(__file__).resolve().parent.parent
FIXTURES = REPO / "data" / "cases" / "red-team"

RT_NOLABEL = FIXTURES / "RT-NOLABEL-001.json"          # motor ciego: MALICE 0.5553
RT_CONSTELLATION = FIXTURES / "RT-FN-CONSTELLATION-001.json"  # GT MALICE, motor: NOISE
RT_CULTURAL = FIXTURES / "RT-FP-CULTURAL-001.json"     # GT NOISE, motor: MALICE


def _adapter(monkeypatch, mode: str | None, json_path: Path) -> dict:
    if mode is None:
        monkeypatch.delenv("VIGIA_EBS_RESOLVE", raising=False)
    else:
        monkeypatch.setenv("VIGIA_EBS_RESOLVE", mode)
    orch = so.SIFTOrchestrator(case_id=json_path.stem)
    return orch._analyze_ebs_json(str(json_path))


def _flip_label(tmp_path: Path, src: Path, label: str | None) -> Path:
    case = json.loads(src.read_text(encoding="utf-8"))
    if label is None:
        case.pop("expected_verdict", None)
    else:
        case["expected_verdict"] = label
    out = tmp_path / f"{src.stem}__{label or 'nolabel'}.json"
    out.write_text(json.dumps(case), encoding="utf-8")
    return out


class TestBlindGate:
    """El agente sin etiqueta NO puede colapsar a NOISE sobre evidencia
    que el motor canónico clasifica MALICE."""

    def test_nolabel_case_is_not_dismissed_as_noise(self, monkeypatch):
        # M2 update (2026-07-12): the fixture is a label-stripped copy of
        # case_090 (subgroup C), whose historical MALICE 0.5553 rode the
        # FALSE_FLAG_PATTERN fossil; the canonical motor now says SUSPICION
        # pending the raw re-scoring session. The invariant under test is
        # label-blindness + no benign collapse, so the expectation follows
        # the canonical motor dynamically instead of freezing one era's
        # verdict (it tracks the re-score automatically).
        from vigia_scorer import _vigia_score

        blind = json.loads(RT_NOLABEL.read_text(encoding="utf-8"))
        blind.pop("expected_verdict", None)
        motor_verdict = _vigia_score(blind)["verdict"]
        assert motor_verdict not in ("NOISE", "ERROR"), (
            f"fixture degenerated: canonical motor says {motor_verdict}"
        )
        res = _adapter(monkeypatch, "motor", RT_NOLABEL)
        hyp = res["abduction"]["best_hypothesis"]
        assert hyp == so._MOTOR_HYPOTHESIS_MAP[motor_verdict], (
            f"RT-NOLABEL-001 (motor ciego: {motor_verdict}) produjo '{hyp}' — "
            "el adaptador sigue ciego sin etiqueta (P2-C)."
        )
        assert hyp != "NO_SEMIOTIC_ANOMALY_DETECTED"

    def test_motor_mode_matches_canonical_scorer_on_all_fixtures(self, monkeypatch):
        """resolve() ES la selección del motor: hipótesis == map(veredicto motor).

        B-127: resolve() now injects Grice results for testimony-only cases
        before calling _vigia_score. The canonical scorer is called with
        the SAME enriched dict that resolve() builds, so the comparison
        remains valid. We replicate the Grice injection here to keep the
        test aligned with the real code path.
        """
        from vigia_scorer import _vigia_score

        _B127_TESTIMONY_TYPES = {"cultural_marker", "log_entry", "document_geometry", "testimony"}

        for fixture in sorted(FIXTURES.glob("RT-*.json")):
            case = json.loads(fixture.read_text(encoding="utf-8"))
            blind = {k: v for k, v in case.items() if k != "expected_verdict"}

            # B-127: replicate the Grice injection that resolve() now does,
            # so _vigia_score sees the same dict as the orchestrator path.
            _arts = blind.get("artifacts", [])
            if (
                _arts
                and all(str(a.get("evidence_type", "")).lower() in _B127_TESTIMONY_TYPES
                        for a in _arts)
                and not any(str(a.get("semantic_role", "")).lower() == "exculpatory"
                            for a in _arts)
            ):
                try:
                    _msgs = [a.get("description", "") for a in _arts if a.get("description")]
                    if _msgs:
                        import asyncio
                        from vigia.vigia_sift_bridge import audit_grice_maxims
                        _gr = asyncio.run(audit_grice_maxims(_msgs))
                        blind["grice_verdict"] = _gr.get("verdict", "")
                        blind["grice_deception_probability"] = _gr.get("probability_deception", 0)
                except Exception:
                    pass

            motor_verdict = _vigia_score(blind)["verdict"]
            res = _adapter(monkeypatch, "motor", fixture)
            expected_hyp = so._MOTOR_HYPOTHESIS_MAP[motor_verdict]
            assert res["abduction"]["best_hypothesis"] == expected_hyp, fixture.name

    def test_resolve_metadata_sealed_for_traceability(self, monkeypatch):
        """Daubert: el bundle debe declarar QUÉ función de selección decidió."""
        from vigia_scorer import _vigia_score

        blind = json.loads(RT_NOLABEL.read_text(encoding="utf-8"))
        blind.pop("expected_verdict", None)
        motor_verdict = _vigia_score(blind)["verdict"]
        res = _adapter(monkeypatch, "motor", RT_NOLABEL)
        meta = res["pipeline_meta"]
        assert meta["ebs_adapter_mode"] == "motor"
        # M2 update (2026-07-12): compare against the live canonical motor
        # instead of the fossil-era hardcoded MALICE (see BlindGate note).
        assert meta["resolve"]["motor_verdict"] == motor_verdict
        assert "motor_score" in meta["resolve"]


class TestLabelFlipInvariance:
    """3b de la auditoría, ahora como contrato: en modo motor, la etiqueta
    no puede mover ni la hipótesis ni la sección abduction completa."""

    @pytest.mark.parametrize("fixture", [RT_CONSTELLATION, RT_CULTURAL])
    def test_flip_does_not_change_abduction(self, monkeypatch, tmp_path, fixture):
        variants = {}
        for label in ("MALICE", "NOISE", None):
            path = _flip_label(tmp_path, fixture, label)
            res = _adapter(monkeypatch, "motor", path)
            res["pipeline_meta"].pop("expected_verdict", None)  # passthrough declarado
            variants[label] = res
        base = variants["MALICE"]
        for label, res in variants.items():
            assert res["abduction"] == base["abduction"], (
                f"label={label}: la sección abduction cambió con la etiqueta — "
                "el leak sigue vivo en modo motor."
            )
            assert res["signals"] == base["signals"], f"label={label}: señales cambiaron"

    def test_legacy_mode_still_leaks_pinned(self, monkeypatch, tmp_path):
        """Pin del comportamiento legacy (documentado, NO deseado): la misma
        evidencia cambia de hipótesis con la etiqueta. Legacy quedó como modo
        explícito de reproducción de bundles históricos tras el flip (a) —
        este pin documenta POR QUÉ nunca puede volver a ser default."""
        flipped = _flip_label(tmp_path, RT_CONSTELLATION, "NOISE")
        original = _flip_label(tmp_path, RT_CONSTELLATION, "MALICE")
        res_m = _adapter(monkeypatch, "legacy", original)
        res_n = _adapter(monkeypatch, "legacy", flipped)
        assert res_m["abduction"]["best_hypothesis"] == "MALICIOUS_INTENT_DETECTED"
        assert res_n["abduction"]["best_hypothesis"] == "NO_SEMIOTIC_ANOMALY_DETECTED"


class TestDefaultModeIsMotor:
    """Doctrina (a) — flip 2026-07-05: el default es el modo honesto."""

    def test_default_mode_is_motor(self, monkeypatch):
        res = _adapter(monkeypatch, None, RT_CONSTELLATION)
        assert res["pipeline_meta"]["ebs_adapter_mode"] == "motor"
        # RT-FN-CONSTELLATION trae expected=MALICE pero el motor ciego dice
        # NOISE (0.0179): el default HONESTO emite el FN real, no el eco.
        assert res["abduction"]["best_hypothesis"] == "NO_SEMIOTIC_ANOMALY_DETECTED"

    def test_unknown_mode_value_falls_back_to_motor(self, monkeypatch):
        # Fail-honest: un valor desconocido nunca puede reactivar el leak.
        res = _adapter(monkeypatch, "banana", RT_CONSTELLATION)
        assert res["pipeline_meta"]["ebs_adapter_mode"] == "motor"


class TestMotorModeHonesty:
    """En modo motor los FN/FP conocidos del motor se emiten TAL CUAL
    (honestidad sobre completitud, Regla 5) — no se maquillan con la etiqueta."""

    def test_constellation_fn_is_emitted_not_masked(self, monkeypatch):
        # GT=MALICE pero el motor ciego dice NOISE (0.0179): en modo motor el
        # adaptador debe decir NOISE — es el FN real de L-014/FN-002, visible,
        # no un MALICE copiado de la etiqueta.
        res = _adapter(monkeypatch, "motor", RT_CONSTELLATION)
        assert res["abduction"]["best_hypothesis"] == "NO_SEMIOTIC_ANOMALY_DETECTED"

    def test_conclusive_never_true_for_abstain_family(self, monkeypatch, tmp_path):
        # Guard B-027 preservado en el camino nuevo.
        case = json.loads(RT_NOLABEL.read_text(encoding="utf-8"))
        case["artifacts"] = []  # sin artefactos → motor ERROR → PIPELINE_ERROR
        path = tmp_path / "empty.json"
        path.write_text(json.dumps(case), encoding="utf-8")
        res = _adapter(monkeypatch, "motor", path)
        assert "ABSTAIN" in res["abduction"]["best_hypothesis"] or \
            "ERROR" in res["abduction"]["best_hypothesis"]
        assert res["abduction"]["is_conclusive"] is False
