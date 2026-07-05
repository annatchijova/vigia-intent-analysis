#!/usr/bin/env python3
"""
Fase 2 — Generador del dataset de calibración del ladder
(data/calibration_ladder_dataset_*.json).

Para cada caso del corpus (run_all_agent.find_cases): la etiqueta
(`expected_verdict`), el veredicto/score/confianza del MOTOR CIEGO
(`vigia_scorer._vigia_score` con la etiqueta removida) y los features que el
ladder usa para decidir: n_artifacts, artefactos/clases DEVICE (vía
`evidence_role`), trust efectivo medio, fracturas CAIE y distancia al umbral
más cercano.

El campo `agree` replica la doctrina del comparador batch (run_all_agent):
  - alias BENIGN→NOISE,
  - expected=UNKNOWN acepta cualquier veredicto,
  - sobre-severidad MALICE-donde-INTENT es acierto (decisión de Anna,
    2026-07-05 — docs/FASE2_DATASET_CALIBRACION.md §4 opción (a));
    la sub-severidad NO se acepta.

Determinista: mismo corpus + mismo código → mismo dataset (los umbrales se
leen de este archivo; si el ladder cambia, actualizar THRESHOLDS en lockstep
— hay un test de contrato que compara contra vigia_scorer).

Uso:
    python3 scripts/generate_ladder_dataset.py [salida.json]
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from run_all_agent import CASES_DIRS, find_cases  # noqa: E402
from vigia_scorer import _vigia_score  # noqa: E402
from vigia.tools.caie import evidence_role  # noqa: E402

# Umbrales del ladder (vigia_scorer.py) — B-076: SUSPICION 0.18→0.10.
THRESHOLDS = {"MALICE": 0.33, "SUSPICION": 0.10, "UNKNOWN": 0.08}

ALIAS = {"BENIGN": "NOISE"}


def nearest_threshold(score: float):
    name, value = min(THRESHOLDS.items(), key=lambda kv: abs(score - kv[1]))
    return name, round(score - value, 4)


def agree(expected: str, motor_verdict: str) -> bool:
    exp_n = ALIAS.get(expected, expected)
    got_n = ALIAS.get(motor_verdict, motor_verdict)
    if expected == "UNKNOWN":
        return True
    if exp_n == "INTENT" and got_n == "MALICE":
        return True  # sobre-severidad aceptada (doctrina 2026-07-05)
    return got_n == exp_n


def build_rows():
    rows = []
    for path in find_cases(CASES_DIRS):
        try:
            case = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        if not isinstance(case, dict):
            continue
        arts = case.get("artifacts")
        if not isinstance(arts, list) or not arts:
            continue
        expected = case.get("expected_verdict", "UNKNOWN")
        blind = {k: v for k, v in case.items() if k != "expected_verdict"}
        try:
            r = _vigia_score(blind)
        except Exception as e:
            rows.append({
                "case_id": path.stem,
                "expected": expected,
                "motor_verdict": f"ERROR:{type(e).__name__}",
            })
            continue
        device = [a for a in arts
                  if evidence_role(str(a.get("evidence_type", ""))) == "device"]
        thr_name, thr_dist = nearest_threshold(float(r["score"]))
        rows.append({
            "case_id": path.stem,
            "path": str(path.relative_to(REPO)),
            "expected": expected,
            "motor_verdict": r["verdict"],
            "agree": agree(expected, r["verdict"]),
            "score": float(r["score"]),
            "confidence": float(r["confidence"]),
            "reason": str(r.get("reason", ""))[:120],
            "n_artifacts": len(arts),
            "n_device": len(device),
            "n_device_types": len({a.get("evidence_type") for a in device}),
            "mean_effective_trust": float(r.get("mean_effective_trust", 0)),
            "caie_fractures": r.get("caie_fractures", 0),
            "nearest_threshold": thr_name,
            "dist_to_threshold": thr_dist,
        })
    return rows


def main() -> None:
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else (
        REPO / "data" / "calibration_ladder_dataset_20260705.json")
    rows = build_rows()
    disagreements = [r for r in rows if not r.get("agree")]
    out.write_text(json.dumps({
        "generated": "2026-07-05",
        "method": ("motor ciego (_vigia_score sin expected_verdict) sobre "
                   "find_cases(CASES_DIRS); agree = doctrina del comparador "
                   "batch (BENIGN→NOISE, UNKNOWN acepta todo, "
                   "MALICE-donde-INTENT acepta)"),
        "purpose": ("Fase 2 — dataset de calibración del ladder (regla "
                    "L-033); backlog B-075/B-076"),
        "n_cases": len(rows),
        "n_disagreements": len(disagreements),
        "cases": rows,
    }, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"dataset: {out} ({len(rows)} casos, {len(disagreements)} desacuerdos)")


if __name__ == "__main__":
    main()
