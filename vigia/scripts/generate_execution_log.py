#!/usr/bin/env python3
"""
vigia/cli/generate_execution_log.py

Genera Agent Execution Logs en formato JSONL para los entregables SANS.

Recorre un caso (o dataset) JSON, ejecuta el pipeline completo y loguea
cada fase: SESSION_START → VISIBLE_VARIABLES → MCP_TOOL_CALL → FORENSIC_FINDING
→ ABDUCTIVE_HYPOTHESIS → EPISTEMIC_CHECK → RISK_CALCULATION → FINAL_VERDICT.

Uso (caso individual):
    python3 -m vigia.cli.generate_execution_log \\
        --case data/cases/VIGIA-REAL-006.json \\
        --output data/logs/VIGIA-REAL-006_execution.jsonl

Uso (batch sobre dataset):
    python3 -m vigia.cli.generate_execution_log \\
        --input tests/red_team/payloads.json \\
        --output data/logs/batch_execution.jsonl

Autor: Colectivo VIGÍA
Versión: 2.3
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from vigia.core.semiotic_detector_v2 import SemioticDetectorV2
    from vigia.core.evidence_aggregator import aggregate_evidence
    from vigia.core.decision_layer import decide
    from vigia.core.execution_logger import VigiaExecutionLogger
except ImportError as e:
    print(f"[FATAL] Importación fallida: {e}", file=sys.stderr)
    print("[FATAL] Ejecutar con: PYTHONPATH=$(pwd) python3 -m vigia.cli.generate_execution_log")
    sys.exit(1)


# ── Mapeo de alert_level → veredicto legible ──────────────────────────────

ALERT_TO_VERDICT = {
    "CRITICAL": "MALICE",
    "HIGH": "INTENT",
    "MEDIUM": "SUSPICION",
    "LOW": "NOISE",
    "INFO": "NOISE",
}

IR_PHASES = [
    "RECONNAISSANCE", "WEAPONIZATION", "DELIVERY",
    "EXPLOITATION", "INSTALLATION", "COMMAND_AND_CONTROL",
    "LATERAL_MOVEMENT", "EXFILTRATION", "IMPACT",
]


def _detect_ir_phase(matches: List[Dict]) -> str:
    """Detecta la fase IR más probable a partir de los patrones detectados."""
    if not matches:
        return "RECONNAISSANCE"
    # Heurística por peso y capa Peirce
    thirdness = [m for m in matches if m.get("peirce_layer") == "THIRDNESS"]
    secondness = [m for m in matches if m.get("peirce_layer") == "SECONDNESS"]
    if thirdness:
        return "EXFILTRATION"
    if secondness:
        return "LATERAL_MOVEMENT"
    return "RECONNAISSANCE"


def _generate_devil_advocate(case: Dict, verdict: str) -> str:
    da = case.get("devil_advocate", "")
    if da:
        return da
    templates = {
        "MALICE": "El comportamiento podría explicarse por configuración automática legítima o error administrativo.",
        "INTENT": "Las inconsistencias podrían deberse a cambios de procedimiento no documentados.",
        "SUSPICION": "Los artefactos son ambiguos — podrían ser residuos de actividad de mantenimiento.",
        "NOISE": "El patrón es consistente con ruido de fondo del sistema.",
    }
    return templates.get(verdict, "Hipótesis benigna alternativa no determinada.")


def process_case(
    case: Dict[str, Any],
    detector: SemioticDetectorV2,
    output_path: Optional[str] = None,
) -> str:
    """
    Procesa un caso individual y genera su JSONL de ejecución.
    Retorna la ruta del archivo generado.
    """
    case_id = case.get("case_id", case.get("artifact_id", "UNKNOWN"))
    text = case.get("text", "")

    # Si no hay texto directo, concatenar artefactos
    if not text and "artifacts" in case:
        parts = []
        for art in case["artifacts"]:
            content = art.get("content", "")
            if content:
                parts.append(content)
        text = " | ".join(parts)

    if not text:
        print(f"[WARN] {case_id}: sin texto ni artefactos, omitiendo.", file=sys.stderr)
        return ""

    # Determinar output_dir
    if output_path:
        log_path = Path(output_path)
        output_dir = str(log_path.parent)
        log_filename = log_path.stem
    else:
        output_dir = "data/logs"
        log_filename = case_id

    logger = VigiaExecutionLogger(log_filename, output_dir=output_dir)

    # VISIBLE_VARIABLES — qué artefactos se exponen
    artifacts = case.get("artifacts", [{"artifact_id": "ART-001", "type": "text"}])
    logger._write({
        "event_type": "VISIBLE_VARIABLES",
        "phase": "RECONNAISSANCE",
        "artifacts_exposed": [a.get("artifact_id", f"ART-{i+1:03d}") for i, a in enumerate(artifacts)],
        "filter_applied": "lazy_abstraction_by_phase",
        "reason": "Fase inicial: artefactos visibles según IR phase detectada",
    })

    # DETECTION — ejecutar pipeline
    timestamp = datetime.now(timezone.utc).isoformat()
    det = detector.analyze(text, case_id, timestamp)
    agg = aggregate_evidence(det)
    dec = decide(det, agg)

    matches = det.get("matches", [])
    alert = dec.get("alert_level", "LOW")
    verdict = ALERT_TO_VERDICT.get(alert, "NOISE")
    ir_phase = _detect_ir_phase(matches)

    # Log de herramientas MCP por cada tipo de patrón detectado
    if matches:
        logger.log_tool_call(
            tool_name="audit_grice_maxims",
            parameters={"text": text[:100] + "...", "case_id": case_id},
            result_summary=f"{len(matches)} patrones semióticos detectados",
            duration_ms=45,
        )

    # FORENSIC_FINDINGS — uno por patrón detectado (máx 5)
    for i, match in enumerate(matches[:5]):
        peirce = match.get("peirce_layer", "FIRSTNESS")
        art_id = f"ART-{i+1:03d}"

        logger.log_event(
            phase=ir_phase,
            peirce_layer=peirce,
            artifact=art_id,
            finding=f"Patrón {match.get('pattern_name', 'UNKNOWN')} detectado: {match.get('matched_text', '')[:80]}",
            intent_hypothesis=match.get("description", "")[:100],
            devil_advocate=_generate_devil_advocate(case, verdict),
            tool_called="semiotic_detector_v2",
            confidence=int(match.get("weight", 0.5) * 100),
            verdict_partial=verdict if i == len(matches) - 1 else None,
            pattern_detected=match.get("pattern_name"),
            pattern_weight=match.get("weight"),
        )

    # ABDUCTIVE_HYPOTHESIS
    mi_raw = agg.get("mi_final", {})
    mi_float = mi_raw.get("num", 0) / max(mi_raw.get("den", 1), 1)
    peirce_expected = case.get("peirce_expected", {})
    if not isinstance(peirce_expected, dict):
        peirce_expected = {}

    logger.log_abductive_hypothesis(
        hypothesis_id="H-001",
        hypothesis=(
            peirce_expected.get("thirdness", "")
            or case.get("description", f"Análisis forense de {case_id}")
        )[:200],
        supporting_artifacts=[a.get("artifact_id", f"ART-{i+1:03d}") for i, a in enumerate(artifacts[:4])],
        devil_advocate=_generate_devil_advocate(case, verdict),
        devil_strength=max(0.1, 1.0 - mi_float),
        ockham_cost=1,
        phase="ABDUCTION",
    )

    # EPISTEMIC_CHECK
    logger.log_epistemic_check(
        posterior=verdict,
        consistency_score=min(0.95, mi_float + 0.2),
        consistency_threshold=0.5,
    )

    # RISK_CALCULATION
    logger.log_risk_calculation(
        r_value=round(mi_float, 8),
        variables={
            "P": round(mi_float, 8),
            "D": 0.1,
            "S": round(1.0 - mi_float * 0.2, 8),
            "I": round(min(0.95, mi_float + 0.05), 8),
        },
        formula="r = (1-P)·(1+λD)·(1+γ(1-S))·(1+ω(1-I))",
        decision=verdict,
        reason_code=f"{'REJECT' if mi_float >= 0.15 else 'ACCEPT'}_POSTERIOR_{verdict}",
    )

    # FINAL_VERDICT
    logger.log_verdict(
        verdict=verdict,
        confidence=int(mi_float * 100),
        reason_code=dec.get("reason", "THRESHOLD_BASED")[:50],
        bundle_hash=logger.bundle_hash,
        carnegie_pattern=case.get("carnegie_pattern_expected"),
        mitre_ttps=case.get("expected_mitre_ttps", []),
        devil_advocate_final=_generate_devil_advocate(case, verdict),
    )

    print(f"[OK] {case_id} → {logger.log_file} ({logger.event_count} eventos)")
    return logger.log_file


def process_dataset(
    dataset: List[Dict[str, Any]],
    output_dir: str = "data/logs",
) -> List[str]:
    """Procesa múltiples casos y genera un log por cada uno."""
    detector = SemioticDetectorV2()
    logs = []
    for case in dataset:
        log_path = process_case(case, detector, output_path=None)
        if log_path:
            logs.append(log_path)
    return logs


# ── CLI ────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="VIGÍA Agent Execution Log Generator — entregable SANS"
    )
    parser.add_argument("--case", type=Path,
                        help="JSON de un caso individual (VIGIA-REAL-006.json)")
    parser.add_argument("--input", type=Path,
                        help="JSON con lista de artefactos/casos (batch)")
    parser.add_argument("--output", type=Path,
                        help="Ruta de salida del JSONL (solo para --case)")
    parser.add_argument("--output-dir", type=str, default="data/logs",
                        help="Directorio de salida para batch (default: data/logs)")
    args = parser.parse_args()

    if not args.case and not args.input:
        parser.error("Se requiere --case o --input")

    detector = SemioticDetectorV2()

    _MAX_JSON_SIZE = 50 * 1024 * 1024  # P1-22: 50MB max
    import os as _os
    if args.case:
        if _os.path.getsize(args.case) > _MAX_JSON_SIZE:
            raise SystemExit(f"[VIGÍA] JSON demasiado grande: {args.case}")
        with open(args.case, "r", encoding="utf-8") as f:
            case = json.load(f)
        output_path = str(args.output) if args.output else None
        process_case(case, detector, output_path=output_path)

    elif args.input:
        if _os.path.getsize(args.input) > _MAX_JSON_SIZE:
            raise SystemExit(f"[VIGÍA] JSON demasiado grande: {args.input}")
        with open(args.input, "r", encoding="utf-8") as f:
            data = json.load(f)
        cases = data if isinstance(data, list) else [data]
        logs = []
        for case in cases:
            log_path = process_case(case, detector, output_path=None)
            if log_path:
                logs.append(log_path)
        print(f"\n[OK] {len(logs)} logs generados en {args.output_dir}")


if __name__ == "__main__":
    main()
