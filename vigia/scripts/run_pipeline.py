#!/usr/bin/env python3
"""
vigia/scripts/run_pipeline.py

Adaptador canónico VIGÍA — orquesta Detection → Aggregation → Decision.

Uso:
    python3 -m vigia.scripts.run_pipeline \\
        --input data/test_cases.json \\
        --output outputs/run_a.json \\
        [--negation-enabled]

Output por artefacto:
    {artifact_id, text, aggregator, decision, matches}

Invariantes:
    - sort_keys=True en todo dump JSON (I2: reproducibilidad bit a bit)
    - Sin floats en lógica de decisión (I7)
    - negation_enabled es feature flag A/B para comparación de versiones

Autor: Colectivo VIGÍA
Versión: 2.3
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, List


# ── Canonicalización explícita (I2 + I7) ─────────────────────────────────
# NO usar default= en json.dumps — si aparece un Fraction suelto es un bug
# de fuga de tipos que debe fallar ruidosamente, no silenciarse.

def _strict_json_hook(pairs: list) -> dict:
    """
    Rechaza payloads con claves duplicadas — protege contra Parser Differential Attack.
    Distintos parsers (Python vs SIEM/Go/Rust) pueden resolver claves dup diferente,
    rompiendo la cadena de custodia (Gemini V22).
    """
    d: dict = {}
    for key, value in pairs:
        if key in d:
            raise ValueError(
                f"Clave duplicada en payload forense: '{key}'. "
                f"Rechazado para preservar integridad de evidencia."
            )
        d[key] = value
    return d


def _validate_output_schema(result: Dict[str, Any]) -> None:
    """
    Valida el output de cada artefacto contra el schema canónico VIGÍA.
    Falla ruidosamente (ValueError) si la estructura no cumple el contrato.
    Garantiza admisibilidad Daubert: ningún resultado malformado sale del pipeline.
    """
    aid = result.get("artifact_id", "UNKNOWN")

    # artifact_id
    if not isinstance(result.get("artifact_id"), str) or not result["artifact_id"]:
        raise ValueError(f"[SCHEMA] {aid}: artifact_id ausente o vacío")

    # aggregator.mi_final
    agg = result.get("aggregator")
    if not isinstance(agg, dict):
        raise ValueError(f"[SCHEMA] {aid}: aggregator ausente")
    mi = agg.get("mi_final")
    if not isinstance(mi, dict) or "num" not in mi or "den" not in mi:
        raise ValueError(f"[SCHEMA] {aid}: aggregator.mi_final debe ser {{num, den}}")
    if not isinstance(mi["num"], int) or not isinstance(mi["den"], int):
        raise ValueError(f"[SCHEMA] {aid}: mi_final.num y mi_final.den deben ser int")
    if mi["den"] < 1:
        raise ValueError(f"[SCHEMA] {aid}: mi_final.den debe ser >= 1")

    # decision.alert_level y verdict
    dec = result.get("decision")
    if not isinstance(dec, dict):
        raise ValueError(f"[SCHEMA] {aid}: decision ausente")
    alert = dec.get("alert_level")
    if alert not in ("LOW", "MEDIUM", "HIGH", "CRITICAL"):
        raise ValueError(f"[SCHEMA] {aid}: alert_level inválido: {alert!r}")
    verdict = dec.get("verdict")
    if verdict not in ("ADVERSARIAL_SEMIOTIC_PATTERN_DETECTED", "NO_SEMIOTIC_ANOMALY_DETECTED"):
        raise ValueError(f"[SCHEMA] {aid}: verdict inválido: {verdict!r}")


# P1-19: importar _canonicalize canónico
from vigia.core.canonicalize import _canonicalize  # noqa: F401

try:
    from vigia.core.semiotic_detector_v2 import SemioticDetectorV2
    from vigia.core.evidence_aggregator import aggregate_evidence
    from vigia.core.decision_layer import decide
except ImportError as e:
    print(f"[FATAL] Importación fallida: {e}", file=sys.stderr)
    print("[FATAL] Ejecutar con: PYTHONPATH=$(pwd) python3 -m vigia.scripts.run_pipeline", file=sys.stderr)
    sys.exit(1)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _process_item(
    item: Dict[str, Any],
    detector: SemioticDetectorV2,
) -> Dict[str, Any]:
    """Procesa un artefacto individual. Fail-fast si faltan campos requeridos."""
    artifact_id = item.get("artifact_id")
    text = item.get("text")
    if not artifact_id or text is None:
        raise ValueError(f"Artefacto sin artifact_id o text: {list(item.keys())}")

    timestamp = item.get("timestamp", _now_iso())

    det = detector.analyze(text, artifact_id, timestamp)
    agg = aggregate_evidence(det)
    dec = decide(det, agg)

    result = {
        "artifact_id": artifact_id,
        "text": text,
        "aggregator": agg,
        "decision": dec,
        "matches": det.get("matches", []),
    }

    # Validar schema canónico antes de retornar — fail-fast Daubert (Punto 3)
    _validate_output_schema(result)
    return result


def run(input_path: str, output_path: str, negation_enabled: bool) -> None:
    """
    Itera sobre el dataset y exporta resultados.

    Args:
        input_path: JSON con lista de artefactos {artifact_id, text, ...}
        output_path: JSON de salida con resultados del pipeline
        negation_enabled: Feature flag A/B para el Negation Handler
    """
    data: List[Dict] = json.loads(
        Path(input_path).read_text(encoding="utf-8"),
        object_pairs_hook=_strict_json_hook
    )
    if not isinstance(data, list):
        print("[FATAL] El input debe ser una lista JSON de artefactos.", file=sys.stderr)
        sys.exit(1)

    detector = SemioticDetectorV2(negation_enabled=negation_enabled)

    results: List[Dict[str, Any]] = []
    errors = 0

    for item in data:
        try:
            # Resetear memoria de sesión entre artefactos independientes.
            # Sin esto, el artefacto N hereda patrones del N-1 y genera
            # sinergias falsas — contaminación cruzada de evidencia (Gemini P0).
            detector._memory = type(detector._memory)()
            result = _process_item(item, detector)
            results.append(result)
        except Exception as e:
            aid = item.get("artifact_id", "UNKNOWN")
            print(f"[ERROR] {aid}: {e}", file=sys.stderr)
            errors += 1

    Path(output_path).write_text(
        json.dumps(_canonicalize(results), indent=2, sort_keys=True, ensure_ascii=True),
        encoding="utf-8",
    )

    print(f"[OK] {len(results)} artefactos procesados → {output_path}")
    if errors:
        print(f"[WARN] {errors} artefactos fallaron — revisar stderr.")
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="VIGÍA Pipeline Runner — Detection → Aggregation → Decision"
    )
    parser.add_argument("--input", required=True, help="JSON de artefactos a procesar")
    parser.add_argument("--output", required=True, help="JSON de salida con resultados")
    parser.add_argument(
        "--negation-enabled",
        action="store_true",
        default=False,
        help="Activar Negation Handler (Run B). Omitir para Run A (baseline).",
    )
    args = parser.parse_args()

    run(args.input, args.output, args.negation_enabled)


if __name__ == "__main__":
    main()
