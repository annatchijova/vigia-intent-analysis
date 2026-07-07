#!/usr/bin/env python3
"""
vigia/cli/compare_runs.py

Comparador determinista entre ejecuciones de VIGÍA.
Responsabilidad:
  - Comparar dos runs del pipeline sobre el mismo dataset
  - Calcular deltas racionales irreducibles
  - Detectar driver heurístico (non-causal)
  - Etiquetar cambios como IMPROVEMENT / REGRESSION / VERDICT_SHIFT

Restricciones:
  - Sin floats en lógica de decisión (solo en display)
  - Fracciones irreducibles (Daubert)
  - Driver detection explícitamente heurístico
  - NO calcula TP/FP/TN/FN (eso es evaluate_detector.py)
"""

import argparse
import csv
import hashlib
import json
import math
import sys
from dataclasses import dataclass, field
from fractions import Fraction
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional

# ── Schema constants ──────────────────────────────────────────────────────
REQUIRED_KEYS = {"artifact_id", "aggregator", "decision"}
COMPONENT_KEYS = {"base", "synergy", "sequence"}
MI_KEYS = {"num", "den"}
LEVEL_ORDER = ["INFO", "LOW", "MEDIUM", "HIGH", "CRITICAL"]

# ── I2 Compliant canonical hash ──────────────────────────────────────────

# P1-19: importar _canonicalize canónico
# R3-2: consumidor fuera del camino de bundle sellado — hashing local de comparación entre corridas (no bundle sellado).
# Se fija a v1 (comportamiento previo) para que el fix v2 (prefijo "s:"
# en strings) no altere su salida/hash. v2 es solo para el sellado.
from vigia.core.canonicalize import _canonicalize_v1 as _canonicalize  # noqa: F401

def hash_forensic(obj: Dict) -> str:
    raw = json.dumps(_canonicalize(obj), sort_keys=True, ensure_ascii=True).encode()
    return hashlib.sha256(raw).hexdigest()

# ── Data models ───────────────────────────────────────────────────────────

@dataclass
class PipelineResult:
    artifact_id: str
    mi: Tuple[int, int]
    base: Tuple[int, int]
    synergy: Tuple[int, int]
    sequence: Tuple[int, int]
    alert: str
    hash: str
    abduction: Optional[Dict] = None

@dataclass
class IntentDelta:
    hypothesis_a: str = "N/A"
    hypothesis_b: str = "N/A"
    ockham_delta: int = 0
    shifted: bool = False

@dataclass
class ComparisonResult:
    artifact_id: str
    delta: Tuple[int, int]  # irreducible
    alert_changed: bool
    driver: str
    driver_type: str
    label: str
    intent: IntentDelta = field(default_factory=IntentDelta)
    hash_a: str = ""
    hash_b: str = ""

# ── Validation ────────────────────────────────────────────────────────────

def _validate_entry(entry: Dict, path: Path):
    if not REQUIRED_KEYS.issubset(entry.keys()):
        raise ValueError(f"Schema mismatch en {path}: faltan claves {REQUIRED_KEYS - entry.keys()}")
    agg = entry["aggregator"]
    if "components" not in agg:
        raise ValueError(f"Schema mismatch en {path}: falta aggregator.components")
    if not COMPONENT_KEYS.issubset(agg["components"].keys()):
        raise ValueError(
            f"Schema mismatch en {path}: faltan componentes "
            f"{COMPONENT_KEYS - agg['components'].keys()}"
        )
    # Fail-fast: mi_final requerido (DEA v1 contract) — acepta mi como fallback con advertencia
    if "mi_final" not in agg and "mi" not in agg:
        raise ValueError(
            f"Schema mismatch en {path}: aggregator debe contener 'mi_final' (DEA v1). "
            f"Encontrado: {list(agg.keys())}"
        )
    if "mi_final" not in agg:
        print(f"[WARN] {path}: 'mi_final' ausente, usando 'mi' como fallback. "
              f"Actualizar pipeline a DEA v1.", file=sys.stderr)

# ── Loaders ───────────────────────────────────────────────────────────────

def _get_mi(agg: Dict) -> Tuple[int, int]:
    """Extrae mi como (num, den), soportando mi o mi_final."""
    if "mi" in agg:
        mi = agg["mi"]
    elif "mi_final" in agg:
        mi = agg["mi_final"]
    else:
        return 0, 1
    return mi.get("num", 0), mi.get("den", 1)

def load_run(path: Path) -> Dict[str, PipelineResult]:
    data = json.loads(path.read_text(encoding="utf-8"))
    results = {}
    for entry in data:
        _validate_entry(entry, path)
        aid = entry["artifact_id"]
        agg = entry["aggregator"]
        comp = agg["components"]
        mi_num, mi_den = _get_mi(agg)
        results[aid] = PipelineResult(
            artifact_id=aid,
            mi=(mi_num, mi_den),
            base=(comp["base"]["num"], comp["base"]["den"]),
            synergy=(comp["synergy"]["num"], comp["synergy"]["den"]),
            sequence=(comp["sequence"]["num"], comp["sequence"]["den"]),
            alert=entry["decision"]["alert_level"],
            hash=hash_forensic(entry),
            abduction=entry.get("abduction")
        )
    return results

# ── Math utilities ────────────────────────────────────────────────────────

def _reduce_fraction(num: int, den: int) -> Tuple[int, int]:
    if den == 0: return 0, 1
    g = math.gcd(abs(num), abs(den))
    return num // g, den // g

def _frac_to_float(frac: Tuple[int, int]) -> float:
    return frac[0] / frac[1] if frac[1] != 0 else 0.0

# ── Driver detection (heuristic_v1, non-causal) ───────────────────────────

def _detect_driver(a: PipelineResult, b: PipelineResult) -> Tuple[str, str]:
    deltas = {
        "base": abs(_frac_to_float(b.base) - _frac_to_float(a.base)),
        "synergy": abs(_frac_to_float(b.synergy) - _frac_to_float(a.synergy)),
        "sequence": abs(_frac_to_float(b.sequence) - _frac_to_float(a.sequence)),
    }
    dominant = max(deltas, key=lambda k: abs(deltas[k]))
    vals = sorted(deltas.values(), reverse=True)
    if vals[0] == 0: return "none", "heuristic_v1 (non-causal)"
    if len(vals) > 1 and abs(vals[0] - vals[1]) < 1e-12: return "mixed", "heuristic_v1 (non-causal)"
    return dominant, "heuristic_v1 (non-causal)"

# ── Labeling with ground truth ────────────────────────────────────────────

def _level_to_int(level: str) -> int:
    return LEVEL_ORDER.index(level) if level in LEVEL_ORDER else -1

def _label_change(delta_float: float, alert_changed: bool, expected: str) -> str:
    if alert_changed:
        return "VERDICT_SHIFT"
    is_adversarial = expected.upper() in ("ADVERSARIAL", "MALICE", "INTENT", "SUSPICION")
    if is_adversarial:
        return "IMPROVEMENT" if delta_float > 0 else "REGRESSION"
    return "IMPROVEMENT" if delta_float < 0 else "REGRESSION"

# ── Core comparison ───────────────────────────────────────────────────────

def compare_artifact(a: PipelineResult, b: PipelineResult, gt: str) -> ComparisonResult:
    mi_a = Fraction(a.mi[0], a.mi[1])
    mi_b = Fraction(b.mi[0], b.mi[1])
    delta = mi_b - mi_a
    d_num, d_den = _reduce_fraction(delta.numerator, delta.denominator)
    delta_f = float(delta)

    driver, dtype = _detect_driver(a, b)
    label = _label_change(delta_f, a.alert != b.alert, gt)

    hyp_a = a.abduction.get("winning_hypothesis", "N/A") if a.abduction else "N/A"
    hyp_b = b.abduction.get("winning_hypothesis", "N/A") if b.abduction else "N/A"
    cost_a = a.abduction.get("ockham_cost", 0) if a.abduction else 0
    cost_b = b.abduction.get("ockham_cost", 0) if b.abduction else 0
    intent = IntentDelta(hyp_a, hyp_b, cost_b - cost_a, hyp_a != hyp_b)

    return ComparisonResult(
        artifact_id=a.artifact_id,
        delta=(d_num, d_den),
        alert_changed=a.alert != b.alert,
        driver=driver,
        driver_type=dtype,
        label=label,
        intent=intent,
        hash_a=a.hash,
        hash_b=b.hash
    )

# ── Output formatters ─────────────────────────────────────────────────────

def _format_frac(num: int, den: int) -> str:
    return f"{num}/{den}"

def print_table(results: List[ComparisonResult]):
    header = f"{'ARTIFACT':<10} {'Δ MI':<12} {'LABEL':<15} {'DRIVER':<12} {'ALERT CHG':<10} {'INTENT SHIFT'}"
    print(header)
    print("-" * len(header))
    for r in results:
        sign = "+" if r.delta[0] > 0 else ""
        print(f"{r.artifact_id:<10} {sign}{_format_frac(*r.delta):<11} {r.label:<15} {r.driver:<12} {str(r.alert_changed):<10} {r.intent.shifted}")

def print_diff(r: ComparisonResult, a: PipelineResult, b: PipelineResult):
    print(f"\n[{r.artifact_id}]")
    sign = "+" if r.delta[0] > 0 else ""
    print(f"  MI: A={_format_frac(*a.mi)} → B={_format_frac(*b.mi)} | Δ={sign}{_format_frac(*r.delta)}")
    print(f"  COMPONENTS:")
    for comp in ("base", "synergy", "sequence"):
        av = _frac_to_float(getattr(a, comp))
        bv = _frac_to_float(getattr(b, comp))
        print(f"    {comp:<10}: {av:.4f} → {bv:.4f}")
    print(f"  DRIVER: {r.driver} ({r.driver_type})")
    if r.intent.shifted:
        print(f"  INTENT: {r.intent.hypothesis_a} → {r.intent.hypothesis_b} (Δcost={r.intent.ockham_delta})")
    if r.hash_a != r.hash_b:
        print(f"  ⚠️  DETERMINISM DRIFT: canonical hashes differ")

# ── Meta-metrics (versionado, NO forenses) ────────────────────────────────

def compute_meta_metrics(results: List[ComparisonResult]) -> Dict[str, Any]:
    total = len(results)
    improvements = sum(1 for r in results if r.label == "IMPROVEMENT")
    regressions = sum(1 for r in results if r.label == "REGRESSION")
    shifts = sum(1 for r in results if r.label == "VERDICT_SHIFT")
    neutral = total - improvements - regressions - shifts
    return {
        "total": total,
        "improvements": improvements,
        "regressions": regressions,
        "verdict_shifts": shifts,
        "neutral": neutral,
        "improvement_rate": f"{improvements/total:.2%}" if total else "N/A",
        "regression_rate": f"{regressions/total:.2%}" if total else "N/A",
        "shift_rate": f"{shifts/total:.2%}" if total else "N/A",
    }

# ── Export ──────────────────────────────────────────────────────────────

def export_csv(results: List[ComparisonResult], path: Path):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([
            "artifact_id", "delta_num", "delta_den", "label",
            "driver", "driver_type", "alert_changed",
            "intent_shifted", "ockham_delta", "hash_match"
        ])
        for r in results:
            w.writerow([
                r.artifact_id, r.delta[0], r.delta[1], r.label,
                r.driver, r.driver_type, r.alert_changed,
                r.intent.shifted, r.intent.ockham_delta, r.hash_a == r.hash_b
            ])

# ── CLI ─────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="VIGÍA Deterministic Run Comparator")
    parser.add_argument("--run-a", required=True, type=Path)
    parser.add_argument("--run-b", required=True, type=Path)
    parser.add_argument("--ground-truth", required=True, type=Path)
    parser.add_argument("--show-diff", action="store_true")
    parser.add_argument("--metrics", action="store_true")
    parser.add_argument("--export", type=Path, help="Export to CSV")
    parser.add_argument("--filter", type=str, help="Filter artifact IDs prefix")
    args = parser.parse_args()

    gt = json.loads(Path(args.ground_truth).read_text(encoding="utf-8"))
    run_a = load_run(args.run_a)
    run_b = load_run(args.run_b)

    # Validar que GT cubra ambos runs
    missing_in_a = set(gt.keys()) - set(run_a.keys())
    missing_in_b = set(gt.keys()) - set(run_b.keys())
    if missing_in_a:
        print(f"[WARN] {len(missing_in_a)} casos en GT no están en run_a: {missing_in_a}",
              file=sys.stderr)
    if missing_in_b:
        print(f"[WARN] {len(missing_in_b)} casos en GT no están en run_b: {missing_in_b}",
              file=sys.stderr)

    results = []
    for aid in run_a:
        if aid not in run_b: continue
        if args.filter and not aid.startswith(args.filter): continue
        expected = gt.get(aid, "UNKNOWN")
        results.append(compare_artifact(run_a[aid], run_b[aid], expected))

    print_table(results)

    if args.show_diff:
        for r in results:
            if r.label in ("REGRESSION", "VERDICT_SHIFT"):
                print_diff(r, run_a[r.artifact_id], run_b[r.artifact_id])

    if args.metrics:
        m = compute_meta_metrics(results)
        print(f"\nMETA-METRICS (versionado)")
        print(f"---------------------------")
        for k, v in m.items(): print(f"{k:<20}: {v}")

    if args.export:
        export_csv(results, args.export)
        print(f"\n[OK] Exported to {args.export}")

    drifts = [r for r in results if r.hash_a != r.hash_b]
    if drifts:
        print(f"\n⚠️  DETERMINISM DRIFT: {len(drifts)} artifacts differ in canonical hash.")
    else:
        print(f"\n✅ DETERMINISM: ALL HASHES MATCH.")

if __name__ == "__main__":
    main()
