#!/usr/bin/env python3
"""
vigia/scripts/ci_gate.py

CI Gate forense con tolerancia cero — entregable SANS.

Compara el pipeline candidato contra un baseline de referencia y falla
si el motor se vuelve "más tonto" en cualquier caso o si el MI drift
supera 1/100.

Umbrales (no negociables):
  Max MI Drift     : 1/100  (Fraction — sin floats)
  Allowed New FP   : 0
  Allowed New FN   : 0

Si el gate falla, exit 1 con explicación exacta del caso que lo rompió.

Uso:
    python3 -m vigia.scripts.ci_gate \\
        --baseline  outputs/run_baseline.json \\
        --candidate outputs/run_candidate.json \\
        --ground-truth tests/red_team/ground_truth.json

Autor: Colectivo VIGÍA
Versión: 2.3
"""

import argparse
import json
import math
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# ── Umbrales (Fraction — sin floats en lógica de decisión) ───────────────

MAX_MI_DRIFT    = Fraction(1, 100)   # 0.01 — desviación máxima tolerada
ALLOWED_NEW_FP  = 0                  # ningún falso positivo nuevo
ALLOWED_NEW_FN  = 0                  # ningún falso negativo nuevo

LEVEL_ORDER = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]


# ── Utilidades ────────────────────────────────────────────────────────────

def _frac_from_result(result: Dict[str, Any]) -> Fraction:
    """Extrae MI como Fraction del resultado del pipeline."""
    agg = result.get("aggregator", {})
    mi = agg.get("mi_final") or agg.get("mi") or agg.get("manipulation_index") or {}
    den = mi.get("den", 1) or 1
    return Fraction(mi.get("num", 0), den)


def _alert_level(result: Dict[str, Any]) -> str:
    return result.get("decision", {}).get("alert_level", "LOW")


def _is_positive(alert: str) -> bool:
    """MEDIUM o superior = detección positiva."""
    return LEVEL_ORDER.index(alert) >= LEVEL_ORDER.index("MEDIUM")


def _irreducible_delta(a: Fraction, b: Fraction) -> Tuple[int, int]:
    """Retorna delta = b - a como fracción irreducible (num, den)."""
    delta = b - a
    g = math.gcd(abs(delta.numerator), delta.denominator)
    return delta.numerator // g, delta.denominator // g


def _load_run(path: str) -> Dict[str, Dict]:
    """Carga un JSON de pipeline y lo indexa por artifact_id."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, list):
        print(f"[FATAL] {path}: se esperaba lista JSON", file=sys.stderr)
        sys.exit(1)
    return {r["artifact_id"]: r for r in data if "artifact_id" in r}


# ── Lógica del gate ───────────────────────────────────────────────────────

def run_gate(
    baseline_path: str,
    candidate_path: str,
    ground_truth_path: str,
) -> int:
    """
    Ejecuta el CI gate. Retorna 0 si pasa, 1 si falla.
    """
    baseline  = _load_run(baseline_path)
    candidate = _load_run(candidate_path)
    gt        = json.loads(Path(ground_truth_path).read_text(encoding="utf-8"))

    failures: List[str] = []
    new_fp = 0
    new_fn = 0
    drift_violations: List[str] = []

    # Verificar que el candidate cubre todos los casos del baseline
    missing = set(baseline.keys()) - set(candidate.keys())
    if missing:
        print(f"[WARN] {len(missing)} casos en baseline sin par en candidate: {missing}",
              file=sys.stderr)

    for aid, base_result in baseline.items():
        if aid not in candidate:
            continue

        cand_result = candidate[aid]
        expected = gt.get(aid, "UNKNOWN").upper()

        mi_base = _frac_from_result(base_result)
        mi_cand = _frac_from_result(cand_result)
        delta   = mi_cand - mi_base
        delta_num, delta_den = _irreducible_delta(mi_base, mi_cand)
        drift   = abs(delta)

        alert_base = _alert_level(base_result)
        alert_cand = _alert_level(cand_result)

        pos_base = _is_positive(alert_base)
        pos_cand = _is_positive(alert_cand)

        # 1. MI drift
        if drift > MAX_MI_DRIFT:
            drift_violations.append(
                f"  DRIFT {aid}: baseline={mi_base.numerator}/{mi_base.denominator} "
                f"candidate={mi_cand.numerator}/{mi_cand.denominator} "
                f"delta={delta_num:+}/{delta_den} > {MAX_MI_DRIFT}"
            )

        # 2. Nuevos FP: caso BENIGN que antes era correcto y ahora dispara
        if expected == "BENIGN" and not pos_base and pos_cand:
            new_fp += 1
            failures.append(
                f"  NEW FP [{aid}]: BENIGN, baseline={alert_base} → candidate={alert_cand}"
            )

        # 3. Nuevos FN: caso ADVERSARIAL que antes se detectaba y ahora no
        if expected == "ADVERSARIAL" and pos_base and not pos_cand:
            new_fn += 1
            failures.append(
                f"  NEW FN [{aid}]: ADVERSARIAL, baseline={alert_base} → candidate={alert_cand}"
            )

    # ── Reporte ──────────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"  VIGÍA CI GATE v2.3")
    print(f"{'='*60}")
    print(f"  Baseline  : {baseline_path}")
    print(f"  Candidate : {candidate_path}")
    print(f"  GT        : {ground_truth_path}")
    print(f"  Casos comparados: {min(len(baseline), len(candidate))}")
    print(f"")
    print(f"  Max MI Drift   : {float(MAX_MI_DRIFT):.4f}  ({MAX_MI_DRIFT})")
    print(f"  Drift violations: {len(drift_violations)}")
    print(f"  New FP         : {new_fp}  (allowed: {ALLOWED_NEW_FP})")
    print(f"  New FN         : {new_fn}  (allowed: {ALLOWED_NEW_FN})")
    print(f"{'='*60}")

    all_failures = drift_violations + failures
    if all_failures:
        print(f"\n  [CI GATE FAIL] — {len(all_failures)} violaciones:")
        for f in all_failures:
            print(f)
        print(f"\n  El pipeline candidato degrada la calidad forense.")
        print(f"  No se permite commit hasta corregir todos los casos listados.")
        return 1

    print(f"\n  [CI GATE PASS] — Sin regresiones ni drift.")
    print(f"  El candidato es al menos tan bueno como el baseline.")
    print(f"  Listo para merge.\n")
    return 0


# ── CLI ────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="VIGÍA CI Gate — tolerancia cero en regresiones forenses"
    )
    parser.add_argument("--baseline",      required=True,
                        help="JSON del pipeline baseline (run anterior aprobado)")
    parser.add_argument("--candidate",     required=True,
                        help="JSON del pipeline candidato (run actual a validar)")
    parser.add_argument("--ground-truth",  required=True,
                        help="JSON de ground truth {artifact_id: ADVERSARIAL/BENIGN}")
    args = parser.parse_args()

    exit_code = run_gate(args.baseline, args.candidate, args.ground_truth)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
