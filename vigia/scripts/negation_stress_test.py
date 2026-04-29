#!/usr/bin/env python3
"""
vigia/cli/negation_stress_test.py

Prueba de estrés del Negation Handler.
Compara Run A (negation OFF) vs Run B (negation ON) y reporta:
  - Delta MI por artefacto (fracción irreducible)
  - Conteo de matches con negation_detected=True
  - Agrupación por negation_type (SIMPLE, CONTRASTIVE, OTHER)
  - Regressions vs Improvements con referencia al ground truth

Restricciones:
  - Sin floats en lógica de decisión
  - Fracciones irreducibles (math.gcd)
  - Vocabulario ground truth: ADVERSARIAL / BENIGN

Uso:
    python3 -m vigia.cli.negation_stress_test \\
        --run-a outputs/run_a.json \\
        --run-b outputs/run_b.json \\
        --ground-truth data/ground_truth.json \\
        --output outputs/negation_report.json \\
        [--export-csv outputs/negation_report.csv]

Autor: Colectivo VIGÍA
Versión: 2.3
"""

import argparse
import csv
import json
import math
import sys
from dataclasses import dataclass, field, asdict
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# ── Serialización defensiva ───────────────────────────────────────────────

def _json_default(obj: Any) -> Any:
    if isinstance(obj, Fraction):
        return {"num": obj.numerator, "den": obj.denominator}
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


# ── Data models ───────────────────────────────────────────────────────────

@dataclass
class NegationResult:
    artifact_id: str
    expected: str                   # ADVERSARIAL / BENIGN
    negation_type: str              # SIMPLE / CONTRASTIVE / OTHER
    mi_a: Tuple[int, int]          # (num, den) Run A
    mi_b: Tuple[int, int]          # (num, den) Run B
    delta: Tuple[int, int]         # irreducible, signed
    alert_a: str
    alert_b: str
    verdict_shift: bool
    negation_count: int             # matches con negation_detected=True en Run B
    regression: bool                # delta va en dirección equivocada
    improvement: bool


@dataclass
class NegationSummary:
    total: int = 0
    improvements: int = 0
    regressions: int = 0
    verdict_shifts: int = 0
    total_negation_detections: int = 0
    by_type: Dict[str, Dict[str, int]] = field(default_factory=dict)


# ── Utilidades racionales ─────────────────────────────────────────────────

def _frac_from_agg(agg: Dict) -> Fraction:
    """Extrae mi como Fraction. Prioriza mi_final (DEA v1), fallback a mi."""
    mi = agg.get("mi_final") or agg.get("mi") or agg.get("manipulation_index") or {}
    den = mi.get("den", 1) or 1
    return Fraction(mi.get("num", 0), den)


def _irreducible(delta: Fraction) -> Tuple[int, int]:
    """Devuelve (num, den) irreducible preservando signo en numerador."""
    if delta.denominator == 0:
        return (0, 1)
    return (delta.numerator, delta.denominator)


def _classify_negation_type(text: str) -> str:
    """
    Clasifica el tipo de negación dominante en el texto.
    CONTRASTIVE: contiene conector adversativo ("but", "pero", "sin embargo")
    SIMPLE: contiene negación directa ("no", "not", "nunca")
    OTHER: sin negación clara

    Usa tokenización por palabras para evitar falsos positivos de substring
    (ej: "butaca" no debe disparar "but", "conocimiento" no debe disparar "no").
    Para conectores de múltiples palabras ("sin embargo", "a pesar") se busca
    la frase completa con word boundaries.
    """
    import re
    t = text.lower()
    tokens = set(re.findall(r"[a-záéíóúüñ']+", t))

    # Conectores de una sola palabra — verificar contra el set de tokens
    contrastive_single = {"but", "pero", "however", "aunque"}
    # Conectores multi-palabra — buscar como frase con re.search
    contrastive_multi = [r"\bsin\s+embargo\b", r"\ba\s+pesar\b", r"\bno\s+obstante\b"]

    for c in contrastive_single:
        if c in tokens:
            return "CONTRASTIVE"
    for pattern in contrastive_multi:
        if re.search(pattern, t):
            return "CONTRASTIVE"

    # Negación simple — ya usaba word boundaries
    simple_neg = {"no", "not", "nunca", "jamás", "never", "don't", "doesn't"}
    for n in simple_neg:
        if f" {n} " in f" {t} " or t.startswith(n + " "):
            return "SIMPLE"

    return "OTHER"


def _count_negation_detected(matches: List[Dict]) -> int:
    """Cuenta matches donde negation_detected=True."""
    return sum(1 for m in matches if m.get("negation_detected", False))


def _is_regression(expected: str, delta: Fraction) -> bool:
    """
    Un delta es regresión si va en la dirección equivocada respecto al ground truth.
    ADVERSARIAL + delta > 0 → MI sube con negation ON → el handler está ATENUANDO casos reales → REGRESSION
    ADVERSARIAL + delta < 0 → MI baja → IMPROVEMENT (el handler reduce falsa alarma, pero puede ser regresión de recall)
    BENIGN + delta < 0 → MI baja → IMPROVEMENT (handler funciona correctamente)
    BENIGN + delta > 0 → MI sube → REGRESSION (handler introduce falsa señal)

    Nota: para ADVERSARIAL, que el MI baje con negation ON puede ser REGRESSION de recall.
    Se reporta como regresión si ADVERSARIAL y delta < 0 (handler atenúa caso real).
    """
    if expected == "ADVERSARIAL":
        return delta < 0  # handler redujo MI en caso real → regresión de recall
    else:  # BENIGN
        return delta > 0  # handler aumentó MI en caso benigno → regresión de FPR


# ── Core ──────────────────────────────────────────────────────────────────

def run_stress_test(
    run_a: List[Dict],
    run_b: List[Dict],
    ground_truth: Dict[str, str],
    dataset: Optional[List[Dict]] = None,
) -> Tuple[List[NegationResult], NegationSummary]:
    """
    Compara Run A vs Run B y genera reporte de atenuación.

    Args:
        run_a: Output pipeline con negation OFF
        run_b: Output pipeline con negation ON
        ground_truth: {artifact_id: "ADVERSARIAL"/"BENIGN"}
        dataset: Dataset original (fallback para textos ausentes en run_b)
    """
    # Índice por artifact_id
    idx_a = {r["artifact_id"]: r for r in run_a}
    idx_b = {r["artifact_id"]: r for r in run_b}
    ds_idx = {d["artifact_id"]: d.get("text", "") for d in (dataset or [])}

    # Validar cobertura
    missing = set(idx_a.keys()) - set(idx_b.keys())
    if missing:
        print(f"[WARN] {len(missing)} artefactos en Run A sin par en Run B: {missing}", file=sys.stderr)

    results: List[NegationResult] = []
    summary = NegationSummary()

    for aid, r_a in idx_a.items():
        if aid not in idx_b:
            continue

        r_b = idx_b[aid]
        expected = ground_truth.get(aid, "UNKNOWN").upper()
        if expected not in ("ADVERSARIAL", "BENIGN"):
            print(f"[WARN] {aid}: expected_verdict desconocido '{expected}', omitiendo.", file=sys.stderr)
            continue

        mi_a = _frac_from_agg(r_a.get("aggregator", {}))
        mi_b = _frac_from_agg(r_b.get("aggregator", {}))
        delta = mi_b - mi_a  # fracción exacta, automáticamente reducida

        alert_a = r_a.get("decision", {}).get("alert_level", "LOW")
        alert_b = r_b.get("decision", {}).get("alert_level", "LOW")
        verdict_shift = alert_a != alert_b

        # Texto — fallback al dataset original si no está en run_b
        text = r_b.get("text", "") or ds_idx.get(aid, "")
        neg_type = _classify_negation_type(text)

        # Conteo de negation_detected en Run B
        neg_count = _count_negation_detected(r_b.get("matches", []))

        is_reg = _is_regression(expected, delta)
        is_imp = not is_reg and delta != Fraction(0)

        results.append(NegationResult(
            artifact_id=aid,
            expected=expected,
            negation_type=neg_type,
            mi_a=_irreducible(mi_a),
            mi_b=_irreducible(mi_b),
            delta=_irreducible(delta),
            alert_a=alert_a,
            alert_b=alert_b,
            verdict_shift=verdict_shift,
            negation_count=neg_count,
            regression=is_reg,
            improvement=is_imp,
        ))

        # Actualizar summary
        summary.total += 1
        if is_reg:
            summary.regressions += 1
        if is_imp:
            summary.improvements += 1
        if verdict_shift:
            summary.verdict_shifts += 1
        summary.total_negation_detections += neg_count

        # Agrupación por tipo
        if neg_type not in summary.by_type:
            summary.by_type[neg_type] = {
                "total": 0, "improvements": 0, "regressions": 0, "verdict_shifts": 0
            }
        summary.by_type[neg_type]["total"] += 1
        if is_imp:
            summary.by_type[neg_type]["improvements"] += 1
        if is_reg:
            summary.by_type[neg_type]["regressions"] += 1
        if verdict_shift:
            summary.by_type[neg_type]["verdict_shifts"] += 1

    return results, summary


# ── Export ─────────────────────────────────────────────────────────────────

def _results_to_dicts(results: List[NegationResult]) -> List[Dict]:
    out = []
    for r in results:
        out.append({
            "artifact_id": r.artifact_id,
            "expected": r.expected,
            "negation_type": r.negation_type,
            "mi_a": {"num": r.mi_a[0], "den": r.mi_a[1]},
            "mi_b": {"num": r.mi_b[0], "den": r.mi_b[1]},
            "delta": {"num": r.delta[0], "den": r.delta[1]},
            "delta_decimal": f"{float(Fraction(r.delta[0], r.delta[1])):.4f}",
            "alert_a": r.alert_a,
            "alert_b": r.alert_b,
            "verdict_shift": r.verdict_shift,
            "negation_count": r.negation_count,
            "regression": r.regression,
            "improvement": r.improvement,
        })
    return out


def export_json(results: List[NegationResult], summary: NegationSummary, path: Path) -> None:
    payload = {
        "summary": {
            "total": summary.total,
            "improvements": summary.improvements,
            "regressions": summary.regressions,
            "verdict_shifts": summary.verdict_shifts,
            "total_negation_detections": summary.total_negation_detections,
            "by_negation_type": summary.by_type,
        },
        "results": _results_to_dicts(results),
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True,
                                ensure_ascii=True, default=_json_default),
                    encoding="utf-8")


def export_csv(results: List[NegationResult], path: Path) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "artifact_id", "expected", "negation_type",
            "mi_a_num", "mi_a_den", "mi_b_num", "mi_b_den",
            "delta_num", "delta_den", "delta_decimal",
            "alert_a", "alert_b", "verdict_shift",
            "negation_count", "regression", "improvement"
        ])
        for r in results:
            delta_dec = float(Fraction(r.delta[0], r.delta[1]))
            writer.writerow([
                r.artifact_id, r.expected, r.negation_type,
                r.mi_a[0], r.mi_a[1], r.mi_b[0], r.mi_b[1],
                r.delta[0], r.delta[1], f"{delta_dec:.4f}",
                r.alert_a, r.alert_b, r.verdict_shift,
                r.negation_count, r.regression, r.improvement
            ])


# ── CLI ────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="VIGÍA Negation Stress Test — Run A (OFF) vs Run B (ON)"
    )
    parser.add_argument("--run-a", required=True, help="JSON pipeline con negation OFF")
    parser.add_argument("--run-b", required=True, help="JSON pipeline con negation ON")
    parser.add_argument("--ground-truth", required=True, help="JSON {artifact_id: ADVERSARIAL/BENIGN}")
    parser.add_argument("--output", required=True, help="JSON de reporte completo")
    parser.add_argument("--export-csv", type=Path, help="CSV de resultados por artefacto")
    parser.add_argument("--dataset", type=Path, help="Dataset original (fallback para textos)")
    args = parser.parse_args()

    run_a = json.loads(Path(args.run_a).read_text(encoding="utf-8"))
    run_b = json.loads(Path(args.run_b).read_text(encoding="utf-8"))
    gt = json.loads(Path(args.ground_truth).read_text(encoding="utf-8"))
    dataset = json.loads(args.dataset.read_text(encoding="utf-8")) if args.dataset else None

    results, summary = run_stress_test(run_a, run_b, gt, dataset)

    export_json(results, summary, Path(args.output))
    if args.export_csv:
        export_csv(results, args.export_csv)

    # Reporte a stdout
    print("\n=== VIGÍA NEGATION STRESS TEST ===")
    print(f"Total artefactos comparados : {summary.total}")
    print(f"Improvements                : {summary.improvements}")
    print(f"Regressions                 : {summary.regressions}")
    print(f"Verdict shifts              : {summary.verdict_shifts}")
    print(f"Negation detections (Run B) : {summary.total_negation_detections}")
    print("\nPor tipo de negación:")
    for ntype, stats in sorted(summary.by_type.items()):
        print(f"  {ntype:<14}: total={stats['total']} imp={stats['improvements']} reg={stats['regressions']}")
    print(f"\n[OK] Reporte → {args.output}")
    if args.export_csv:
        print(f"[OK] CSV    → {args.export_csv}")

    if summary.regressions > 2:
        print(f"\n[QUALITY GATE FAIL] Regressions={summary.regressions} > 2", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
