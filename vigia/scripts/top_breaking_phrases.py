#!/usr/bin/env python3
"""
vigia/cli/top_breaking_phrases.py

Clasificador de daños estructurales — Top 5 frases conflictivas.

Toma el reporte de negation_stress_test.py y prioriza regresiones según:
    impact_score = |delta_decimal| * WEIGHT_DELTA
                 + (1 if verdict_shift else 0) * WEIGHT_VERDICT_SHIFT

Fallback de texto: si text no está en Run B, lo busca en el dataset original.

Uso:
    python3 -m vigia.cli.top_breaking_phrases \\
        --stress-report outputs/negation_report.json \\
        --run-b outputs/run_b.json \\
        --dataset data/test_cases.json \\
        --output outputs/top_breaking.json \\
        [--top-n 5]

Autor: Colectivo VIGÍA
Versión: 2.3
"""

import argparse
import json
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# ── Serialización defensiva ───────────────────────────────────────────────

def _json_default(obj: Any) -> Any:
    if isinstance(obj, Fraction):
        return {"num": obj.numerator, "den": obj.denominator}
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


# ── Pesos de scoring de impacto ───────────────────────────────────────────

WEIGHT_DELTA = Fraction(7, 10)          # 70% del score = magnitud del delta MI
WEIGHT_VERDICT_SHIFT = Fraction(3, 10)  # 30% del score = penalidad por cambio de veredicto


# ── Utilidades ────────────────────────────────────────────────────────────

def _impact_score(delta_num: int, delta_den: int, verdict_shift: bool) -> Fraction:
    """
    Calcula impact score en Fraction (sin floats).

    score = |delta| * WEIGHT_DELTA + verdict_shift * WEIGHT_VERDICT_SHIFT
    """
    delta = Fraction(abs(delta_num), delta_den or 1)
    shift_penalty = WEIGHT_VERDICT_SHIFT if verdict_shift else Fraction(0)
    return delta * WEIGHT_DELTA + shift_penalty


def _load_texts_from_run(run_b: List[Dict]) -> Dict[str, str]:
    """Extrae {artifact_id: text} del run_b."""
    return {r["artifact_id"]: r.get("text", "") for r in run_b}


def _load_texts_from_dataset(dataset: List[Dict]) -> Dict[str, str]:
    """Extrae {artifact_id: text} del dataset original."""
    return {d["artifact_id"]: d.get("text", "") for d in dataset}


# ── Core ──────────────────────────────────────────────────────────────────

def compute_top_breaking(
    stress_report: Dict[str, Any],
    run_b: List[Dict],
    dataset: Optional[List[Dict]] = None,
    top_n: int = 5,
) -> List[Dict]:
    """
    Prioriza regresiones del stress test por impact score.

    Retorna lista ordenada de hasta top_n frases con mayor daño estructural.
    Solo incluye casos con regression=True.
    """
    results = stress_report.get("results", [])
    regressions = [r for r in results if r.get("regression", False)]

    if not regressions:
        return []

    # Textos disponibles: Run B primero, fallback a dataset
    texts_b = _load_texts_from_run(run_b)
    texts_ds = _load_texts_from_dataset(dataset) if dataset else {}

    scored: List[Tuple[Fraction, Dict]] = []

    for r in regressions:
        aid = r["artifact_id"]
        delta_num = r.get("delta", {}).get("num", 0)
        delta_den = r.get("delta", {}).get("den", 1) or 1
        verdict_shift = r.get("verdict_shift", False)

        score = _impact_score(delta_num, delta_den, verdict_shift)

        # Texto: Run B → dataset → vacío con advertencia
        text = texts_b.get(aid, "")
        if not text:
            text = texts_ds.get(aid, "")
        if not text:
            print(f"[WARN] {aid}: texto no encontrado en run_b ni en dataset.", file=sys.stderr)

        scored.append((score, {
            "artifact_id": aid,
            "expected": r.get("expected", "UNKNOWN"),
            "negation_type": r.get("negation_type", "OTHER"),
            "text_snippet": text[:200] + ("..." if len(text) > 200 else ""),
            "mi_a": r.get("mi_a", {"num": 0, "den": 1}),
            "mi_b": r.get("mi_b", {"num": 0, "den": 1}),
            "delta": r.get("delta", {"num": 0, "den": 1}),
            "delta_decimal": f"{float(Fraction(delta_num, delta_den)):.4f}",
            "alert_a": r.get("alert_a", "LOW"),
            "alert_b": r.get("alert_b", "LOW"),
            "verdict_shift": verdict_shift,
            "negation_count": r.get("negation_count", 0),
            "impact_score": {
                "num": score.numerator,
                "den": score.denominator,
                "decimal": f"{float(score):.4f}",
            },
        }))

    # Ordenar por score descendente, desempate por artifact_id (determinismo)
    scored.sort(key=lambda x: (-x[0], x[1]["artifact_id"]))

    return [item for _, item in scored[:top_n]]


# ── CLI ────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="VIGÍA Top Breaking Phrases — Clasificador de daños estructurales"
    )
    parser.add_argument(
        "--stress-report", required=True,
        help="JSON de negation_stress_test (reporte completo)"
    )
    parser.add_argument(
        "--run-b", required=True,
        help="JSON del pipeline Run B (negation ON, para fallback de textos)"
    )
    parser.add_argument(
        "--dataset", type=Path,
        help="Dataset original (fallback de textos si no están en run_b)"
    )
    parser.add_argument(
        "--output", required=True,
        help="JSON con el ranking Top N de frases conflictivas"
    )
    parser.add_argument(
        "--top-n", type=int, default=5,
        help="Cuántas frases incluir en el ranking (default: 5)"
    )
    args = parser.parse_args()

    stress_report = json.loads(Path(args.stress_report).read_text(encoding="utf-8"))
    run_b = json.loads(Path(args.run_b).read_text(encoding="utf-8"))
    dataset = json.loads(args.dataset.read_text(encoding="utf-8")) if args.dataset else None

    top = compute_top_breaking(stress_report, run_b, dataset, args.top_n)

    payload = {
        "top_n": args.top_n,
        "total_regressions_found": len(stress_report.get("results", [])),
        "top_breaking_phrases": top,
    }

    Path(args.output).write_text(
        json.dumps(payload, indent=2, sort_keys=True,
                   ensure_ascii=True, default=_json_default),
        encoding="utf-8",
    )

    print(f"\n=== VIGÍA TOP BREAKING PHRASES (Top {args.top_n}) ===")
    if not top:
        print("No se encontraron regresiones. Negation Handler sin daño estructural detectable.")
    else:
        for i, item in enumerate(top, 1):
            score_str = item["impact_score"]["decimal"]
            print(
                f"  #{i} [{item['artifact_id']}] score={score_str} "
                f"delta={item['delta_decimal']} "
                f"shift={item['verdict_shift']} "
                f"type={item['negation_type']}"
            )
            if item["text_snippet"]:
                print(f"     → \"{item['text_snippet'][:80]}...\"")

    print(f"\n[OK] Reporte → {args.output}")


if __name__ == "__main__":
    main()
