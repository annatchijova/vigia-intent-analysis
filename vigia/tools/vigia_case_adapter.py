#!/usr/bin/env python3
"""
vigia/tools/vigia_case_adapter.py

Adaptador de casos forenses VIGÍA → SignalOutput para el pipeline EBS v1.

Convierte artefactos con peirce_layer, forensic_anomalies y type
en señales con tool_name, value, z_score, confidence.

Lógica de conversión:
- THIRDNESS → z_score alto (3.0+) — evidencia de intención
- SECONDNESS → z_score medio (2.0-2.9) — evidencia de acción
- FIRSTNESS → z_score bajo (1.5-1.9) — evidencia contextual
- Más anomalías forenses → value más alto
- Type mapea a tool_name (registry→REG, network_flow→NET, etc.)
"""
import json
import sys
from pathlib import Path

PEIRCE_Z = {
    "THIRDNESS": 3.2,
    "SECONDNESS": 2.4,
    "FIRSTNESS": 1.7,
}

TYPE_TOOL = {
    "registry":       "REG",
    "network_flow":   "NET",
    "bash_history":   "CLI",
    "file_system":    "FS",
    "process":        "PROC",
    "memory":         "MEM",
    "log":            "LOG",
    "email":          "EML",
    "browser":        "BRW",
    "usb":            "USB",
    "prefetch":       "PFT",
    "lnk":            "LNK",
    "scheduled_task": "SCHED",
    "service":        "SVC",
    "user_account":   "USR",
    "crypto":         "CRY",
}

def artifact_to_signal(artifact: dict) -> dict:
    """Convierte un artefacto forense en SignalOutput."""
    layer = artifact.get("peirce_layer", "SECONDNESS").upper()
    art_type = artifact.get("type", "unknown")
    anomalies = artifact.get("forensic_anomalies", [])

    # z_score por capa Peirce
    z_score = PEIRCE_Z.get(layer, 2.0)

    # value = proporción de anomalías (mín 0.3, máx 0.95)
    n_anomalies = len(anomalies)
    value = min(0.95, max(0.3, 0.3 + n_anomalies * 0.2))

    # confidence basada en si tiene contenido forense
    content = artifact.get("content", "")
    confidence = 0.9 if len(content) > 50 else 0.7

    # tool_name desde type
    tool_name = TYPE_TOOL.get(art_type, art_type.upper()[:6])

    return {
        "tool_name":  tool_name,
        "value":      round(value, 3),
        "z_score":    z_score,
        "confidence": confidence,
        "metadata": {
            "artifact_id":  artifact.get("artifact_id"),
            "peirce_layer": layer,
            "type":         art_type,
            "anomalies":    anomalies[:2],  # primeras 2 para contexto
        }
    }

def convert_case(case_path: str) -> list:
    """Convierte un caso VIGÍA en lista de SignalOutput."""
    with open(case_path) as f:
        case = json.load(f)

    artifacts = case.get("artifacts", [])
    signals = [artifact_to_signal(a) for a in artifacts]

    # Metadata del caso para contexto
    print(f"Caso: {Path(case_path).stem}", file=sys.stderr)
    print(f"  Veredicto esperado: {case.get('expected_verdict', '?')}", file=sys.stderr)
    print(f"  Artefactos → señales: {len(signals)}", file=sys.stderr)

    return signals

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 vigia_case_adapter.py <caso.json> [output.json]")
        sys.exit(1)

    signals = convert_case(sys.argv[1])

    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    output = json.dumps(signals, indent=2, ensure_ascii=False)

    if output_path:
        with open(output_path, "w") as f:
            f.write(output)
        print(f"Señales guardadas en {output_path}", file=sys.stderr)
    else:
        print(output)
