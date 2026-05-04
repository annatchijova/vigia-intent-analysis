#!/usr/bin/env python3
"""
vigia/cli/evaluate_detector.py

Evaluación forense determinista del detector contra ground truth.
Responsabilidad:
  - Ejecutar el pipeline sobre un dataset de casos
  - Comparar alert_level contra expected_verdict
  - Calcular precision, recall, FPR (métricas reales, no meta-métricas)
  - Exportar: CSV humano + JSON de métricas + JSON completo de resultados

Restricciones:
  - Sin floats en lógica de decisión
  - Ground truth vocabulario: ADVERSARIAL / BENIGN
  - Determinismo total
"""

import argparse
import csv
import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
from typing import Dict, List, Any, Optional


# ── Canonicalización explícita (I2 + I7) ─────────────────────────────────
# Falla ruidosamente si hay un Fraction suelto — eso es un bug de arquitectura.

# P1-19: importar _canonicalize canónico
from vigia.core.canonicalize import _canonicalize  # noqa: F401

# ── Configuración ─────────────────────────────────────────────────────────
DETECTION_THRESHOLD = "MEDIUM"
LEVEL_ORDER = ["INFO", "LOW", "MEDIUM", "HIGH", "CRITICAL"]

# ── Data models ───────────────────────────────────────────────────────────

@dataclass
class GroundTruth:
    artifact_id: str
    text: str
    expected_verdict: str
    tags: List[str]

@dataclass
class EvaluationResult:
    artifact_id: str
    expected: str
    predicted_level: str
    predicted_verdict: str
    match: bool
    category: str  # TP | FP | TN | FN
    pipeline_output: Dict[str, Any]  # JSON completo para compare_runs

# ── Utilidades ────────────────────────────────────────────────────────────

def _level_to_int(level: str) -> int:
    return LEVEL_ORDER.index(level) if level in LEVEL_ORDER else -1

def _is_detected(alert_level: str) -> bool:
    return _level_to_int(alert_level) >= _level_to_int(DETECTION_THRESHOLD)

def _categorize(expected: str, predicted_level: str) -> str:
    detected = _is_detected(predicted_level)
    is_adversarial = expected.upper() == "ADVERSARIAL"
    if is_adversarial and detected:
        return "TP"
    if is_adversarial and not detected:
        return "FN"
    if not is_adversarial and detected:
        return "FP"
    return "TN"

# ── Adaptador de pipeline (REAL, no placeholder) ───────────────────────────

def run_pipeline(text: str, artifact_id: str) -> Dict[str, Any]:
    """
    Ejecuta el pipeline completo de VIGÍA y normaliza el output al schema de compare_runs.

    Schema garantizado:
        aggregator.mi_final: {num, den}
        aggregator.components: {base, synergy, sequence} — cada uno {num, den}
        decision.alert_level: str
    """
    try:
        from vigia.core.semiotic_detector_v2 import SemioticDetectorV2
        from vigia.core.evidence_aggregator import aggregate_evidence
        from vigia.core.decision_layer import decide

        detector = SemioticDetectorV2()
        det = detector.analyze(text, artifact_id, "2026-01-01T00:00:00Z")
        agg = aggregate_evidence(det)
        dec = decide(det, agg)

        # mi_final — DEA v1 contract
        mi_final = agg.get("mi_final", agg.get("manipulation_index", {"num": 0, "den": 1}))

        # Normalizar components al schema {base, synergy, sequence} con {num, den}
        raw_comp = agg.get("components", {})

        def _to_nd(val: Any) -> Dict[str, int]:
            """Convierte fracción string 'N/D' o dict {num,den} a {num, den}."""
            if isinstance(val, dict) and "num" in val:
                return {"num": int(val["num"]), "den": int(val.get("den", 1) or 1)}
            if isinstance(val, str) and "/" in val:
                n, d = val.split("/", 1)
                return {"num": int(n), "den": int(d) or 1}
            return {"num": 0, "den": 1}

        components_normalized = {
            "base":     raw_comp.get("base") and _to_nd(raw_comp["base"]) or _to_nd(raw_comp.get("base_mi", "0/1")),
            "synergy":  raw_comp.get("synergy") and _to_nd(raw_comp["synergy"]) or _to_nd(raw_comp.get("synergy_factor", "0/1")),
            "sequence": raw_comp.get("sequence") and _to_nd(raw_comp["sequence"]) or _to_nd(raw_comp.get("sequence_factor", "0/1")),
        }

        return {
            "artifact_id": artifact_id,
            "aggregator": {
                "mi_final": {"num": mi_final.get("num", 0), "den": mi_final.get("den", 1) or 1},
                "mi": {"num": mi_final.get("num", 0), "den": mi_final.get("den", 1) or 1},
                "components": components_normalized,
                "metadata": agg.get("metadata", {}),
            },
            "decision": dec,
            "matches": det.get("matches", []),
            "text": text,
        }

    except ImportError as e:
        print(f"[FATAL] No se pudo importar el pipeline: {e}", file=sys.stderr)
        print("[FATAL] Asegurate de ejecutar con PYTHONPATH=$(pwd)", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"[FATAL] Error en pipeline para {artifact_id}: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)

# ── Core evaluation ───────────────────────────────────────────────────────

def evaluate(dataset_path: Path, output_csv: Optional[Path] = None,
             output_json: Optional[Path] = None,
             output_full: Optional[Path] = None) -> Dict[str, Any]:

    with open(dataset_path, "r", encoding="utf-8") as f:
        raw_cases = json.load(f)

    # Validación de dataset
    for case in raw_cases:
        if "expected_verdict" not in case:
            raise ValueError(f"Caso {case.get('artifact_id', 'UNKNOWN')} no tiene expected_verdict")
        verdict = case["expected_verdict"].upper()
        if verdict not in ("ADVERSARIAL", "BENIGN"):
            raise ValueError(f"Caso {case['artifact_id']} tiene expected_verdict inválido: {verdict}")

    cases = [GroundTruth(
        artifact_id=c["artifact_id"],
        text=c["text"],
        expected_verdict=c["expected_verdict"].upper(),
        tags=c.get("tags", [])
    ) for c in raw_cases]

    results: List[EvaluationResult] = []
    full_outputs: List[Dict] = []

    for case in cases:
        pipeline_out = run_pipeline(case.text, case.artifact_id)
        alert_level = pipeline_out["decision"]["alert_level"]
        predicted_verdict = "ADVERSARIAL" if _is_detected(alert_level) else "BENIGN"
        category = _categorize(case.expected_verdict, alert_level)

        results.append(EvaluationResult(
            artifact_id=case.artifact_id,
            expected=case.expected_verdict,
            predicted_level=alert_level,
            predicted_verdict=predicted_verdict,
            match=(case.expected_verdict == predicted_verdict),
            category=category,
            pipeline_output=pipeline_out
        ))

        full_outputs.append(pipeline_out)

    # Métricas
    tp = sum(1 for r in results if r.category == "TP")
    fp = sum(1 for r in results if r.category == "FP")
    tn = sum(1 for r in results if r.category == "TN")
    fn = sum(1 for r in results if r.category == "FN")

    # Métricas como fracciones irreducibles (I7: sin floats en output canónico)
    def _ratio(num: int, den: int) -> dict:
        """Fracción irreducible {num, den} + _decimal para display."""
        if den == 0:
            return {"num": 0, "den": 0, "_decimal": "N/A"}
        import math
        g = math.gcd(num, den)
        return {"num": num // g, "den": den // g, "_decimal": f"{num/den:.4f}"}

    metrics = {
        "total_cases": len(results),
        "tp": tp, "fp": fp, "tn": tn, "fn": fn,
        "precision":           _ratio(tp, tp + fp),
        "recall":              _ratio(tp, tp + fn),
        "false_positive_rate": _ratio(fp, fp + tn),
        "f1_score":            _ratio(2 * tp, 2 * tp + fp + fn),
        "accuracy":            _ratio(tp + tn, len(results)),
        "detection_threshold": DETECTION_THRESHOLD,
        "pipeline_version": "v2.3.0",
        "evaluated_at": datetime.now(timezone.utc).isoformat()
    }

    # Export CSV
    if output_csv:
        with open(output_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["artifact_id", "expected", "predicted_level", 
                           "predicted_verdict", "category", "match"])
            for r in results:
                writer.writerow([r.artifact_id, r.expected, r.predicted_level,
                               r.predicted_verdict, r.category, r.match])

    # Export JSON de métricas
    if output_json:
        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(_canonicalize(metrics), f, indent=2, sort_keys=True)

    # Export JSON completo de resultados (para compare_runs.py)
    if output_full:
        with open(output_full, "w", encoding="utf-8") as f:
            json.dump(_canonicalize(full_outputs), f, indent=2, sort_keys=True,
                      ensure_ascii=True)

    return {
        "metrics": metrics,
        "results": [
            {
                "artifact_id": r.artifact_id,
                "expected": r.expected,
                "predicted_level": r.predicted_level,
                "predicted_verdict": r.predicted_verdict,
                "category": r.category,
                "tags": next((c.tags for c in cases if c.artifact_id == r.artifact_id), [])
            }
            for r in results
        ]
    }

# ── CLI ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="VIGÍA Forensic Detector Evaluation")
    parser.add_argument("--dataset", required=True, type=Path, help="JSON con casos de test")
    parser.add_argument("--output", type=Path, help="CSV de resultados")
    parser.add_argument("--metrics-json", type=Path, help="JSON con métricas agregadas")
    parser.add_argument("--output-full", type=Path, help="JSON completo de resultados (para compare_runs)")
    args = parser.parse_args()

    report = evaluate(args.dataset, args.output, args.metrics_json, args.output_full)

    print("\n=== VIGÍA FORENSIC EVALUATION ===")
    print(f"Total cases: {report['metrics']['total_cases']}")
    print(f"TP: {report['metrics']['tp']} | FP: {report['metrics']['fp']}")
    print(f"TN: {report['metrics']['tn']} | FN: {report['metrics']['fn']}")

    def _fmt(m: dict) -> str:
        """Formatea fracción de métrica para display."""
        if isinstance(m, dict):
            return f"{m['_decimal']}  ({m['num']}/{m['den']})"
        return str(m)

    print(f"Precision: {_fmt(report['metrics']['precision'])}")
    print(f"Recall:    {_fmt(report['metrics']['recall'])}")
    print(f"FPR:       {_fmt(report['metrics']['false_positive_rate'])}")
    print(f"F1:        {_fmt(report['metrics']['f1_score'])}")
    print(f"Accuracy:  {_fmt(report['metrics']['accuracy'])}")

    if args.metrics_json:
        print(f"\n[OK] Metrics exported to {args.metrics_json}")
    if args.output:
        print(f"[OK] CSV exported to {args.output}")
    if args.output_full:
        print(f"[OK] Full results JSON exported to {args.output_full}")

if __name__ == "__main__":
    main()
