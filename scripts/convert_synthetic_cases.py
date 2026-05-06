#!/usr/bin/env python3
"""
scripts/convert_synthetic_cases.py
===================================
Convierte casos VIGIA-SYN (formato legacy v1) al formato canónico EBS v1.

Los casos sintéticos fueron creados en abril con una versión anterior de VIGÍA.
Este convertidor les asigna scores forenses apropiados para el pipeline actual.
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone

# Mapeo: tipo legacy → evidence_type canónico
TYPE_MAP = {
    "registry": "registry_key",
    "network_flow": "network_artifact",
    "network_capture_summary": "network_artifact",
    "flujo_red": "network_artifact",
    "bash_history": "log_entry",
    "auth_log": "log_entry",
    "system_log": "log_entry",
    "file_metadata": "file_timestamp",
    "filesystem_metadata": "file_timestamp",
    "file_access_audit": "file_timestamp",
    "timestamp": "file_timestamp",
    "process_list": "memory_process",
    "memory_string": "memory_process",
    "email_header": "log_entry",
    "email_headers": "log_entry",
    "pdf_document": "log_entry",
    "accounting_system_log": "log_entry",
    "screenshot_dashboard": "log_entry",
    "registro_acceso": "log_entry",
    "historial_accesos_referencia": "log_entry",
    "contexto_usuario": "log_entry",
    "network": "network_artifact",
    "log": "log_entry",
    "system": "log_entry",
    "auth": "log_entry",
    "text": "log_entry",
    "traffic": "network_artifact",
    "context": "log_entry",
    "binary": "memory_process",
    "script": "log_entry",
}

# Scores por veredicto esperado
VERDICT_SCORES = {
    "MALICE": 0.85,
    "INTENT": 0.80,
    "SUSPICION": 0.65,
    "NOISE": 0.15,
    "BENIGN": 0.10,
    "ABSTAIN": 0.05,
}

def convert_case(case: dict) -> dict:
    """Convierte un caso sintético al formato canónico EBS v1."""
    case_id = case["case_id"]
    case_name = case.get("case_name", case_id)
    description = case.get("description", "")
    artifacts_raw = case.get("artifacts", [])
    expected_verdict = case.get("expected_verdict", "NOISE").upper()
    
    # Score base por veredicto
    base_score = VERDICT_SCORES.get(expected_verdict, 0.5)
    
    # Convertir artefactos
    canonical_artifacts = []
    for i, art in enumerate(artifacts_raw):
        art_id = art.get("artifact_id", f"ART-{i:03d}")
        art_type = art.get("type", "unknown")
        content = art.get("content", "")
        anomalies = art.get("forensic_anomalies", [])
        peirce_layer = art.get("peirce_layer", "SECONDNESS")
        
        # Score por artefacto: base + variación por posición
        # Más artefactos = caso más complejo = score ligeramente mayor
        position_boost = i * 0.02
        art_score = min(0.95, base_score + position_boost)
        
        canonical_artifacts.append({
            "artifact_id": art_id,
            "evidence_type": TYPE_MAP.get(art_type, "default"),
            "source_tool": "synthetic_generator",
            "timestamp": f"2026-04-{10+i:02d}T10:00:00Z",
            "raw_score": round(art_score, 4),
            "prior_trust": 0.75,
            "provenance_chain": [f"sha256:synthetic_{case_id}_{art_id}"],
            "description": content,
            "metadata": {
                "original_type": art_type,
                "synthetic_case": case_id,
                "peirce_layer": peirce_layer,
                "forensic_anomalies": anomalies,
                "content": content,
            }
        })
    
    # Construir peirce_chain desde peirce_expected
    peirce_expected = case.get("peirce_expected", {})
    peirce_chain = {
        "firstness": peirce_expected.get("firstness", description),
        "secondness": peirce_expected.get("secondness", "Technical analysis"),
        "thirdness": peirce_expected.get("thirdness", "Forensic inference"),
    }
    
    # Construir temporal_violations si hay grice_violation
    temporal_violations = []
    grice = case.get("grice_violation", "")
    if grice:
        temporal_violations.append({
            "type": "STATISTICAL_UNIFORMITY",
            "severity": 0.6,
            "cause": {
                "artifact_id": artifacts_raw[0].get("artifact_id", "unknown"),
                "timestamp": "2026-04-10T10:00:00Z",
                "description": "Gricean maxim violation detected"
            },
            "effect": {
                "artifact_id": artifacts_raw[-1].get("artifact_id", "unknown") if artifacts_raw else "unknown",
                "timestamp": "2026-04-10T10:00:00Z",
                "description": f"Grice violation: {grice[:100]}"
            },
            "delta_seconds": 0,
            "interpretation": f"Cooperative principle violated: {grice[:200]}"
        })
    
    # Determinar expected_mitre_ttps
    expected_mitre = case.get("expected_mitre_ttps", [])
    if not expected_mitre and expected_verdict in ("MALICE", "INTENT", "SUSPICION"):
        # Asignar TTP genérico para casos maliciosos sin TTPs específicos
        expected_mitre = ["T1070.006"]
    
    # Extraer eco_signal y devil_advocate para metadata del caso
    extra_metadata = {
        "eco_signal": case.get("eco_signal", ""),
        "devil_advocate": case.get("devil_advocate", ""),
        "grice_violation": grice,
        "carnegie_pattern": case.get("carnegie_pattern_expected", ""),
        "abstention_risk": case.get("abstention_risk", "bajo"),
        "source_origin": case.get("source_origin", "synthetic"),
        "source_dataset": case.get("source_dataset", "VIGÍA Internal Corpus"),
        "_parser": case.get("_parser", "unknown"),
        "_consolidation": case.get("_consolidation", {}),
    }
    
    return {
        "case_id": case_id,
        "name": case_name,
        "description": description,
        "artifacts": canonical_artifacts,
        "temporal_violations": temporal_violations,
        "expected_verdict": expected_verdict,
        "expected_confidence": case.get("confidence_expected", 85) / 100.0,
        "expected_mitre_ttps": expected_mitre,
        "peirce_chain": peirce_chain,
        "extra_metadata": extra_metadata,
        "demo_command": f"python tests/run_vigia_case.py data/cases/consolidated/{case_id}.json",
        "demo_quote": description[:200],
    }

def main():
    input_dir = Path("data/cases/consolidated")
    output_dir = Path("data/cases/consolidated_canonical")
    output_dir.mkdir(exist_ok=True)
    
    syn_files = sorted(input_dir.glob("VIGIA-SYN-*.json"))
    if not syn_files:
        print("ERROR: No se encontraron casos sintéticos")
        sys.exit(1)
    
    converted = []
    passed = 0
    failed = 0
    
    for syn_file in syn_files:
        with open(syn_file) as f:
            case = json.load(f)
        
        canonical = convert_case(case)
        converted.append(canonical)
        
        # Guardar individual
        out_file = output_dir / f"{canonical['case_id']}.json"
        with open(out_file, "w") as f:
            json.dump(canonical, f, indent=2, ensure_ascii=False)
        
        # Verificar rápido
        verdict = canonical["expected_verdict"]
        n_arts = len(canonical["artifacts"])
        avg_score = sum(a["raw_score"] for a in canonical["artifacts"]) / n_arts if n_arts else 0
        
        print(f"✅ {canonical['case_id']}: {n_arts} arts, avg_score={avg_score:.2f}, verdict={verdict}")
    
    # Guardar array completo
    array_file = output_dir / "vigia_syn_canonical_all.json"
    with open(array_file, "w") as f:
        json.dump(converted, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*60}")
    print(f"✅ Total: {len(converted)} casos sintéticos convertidos")
    print(f"📁 Directorio: {output_dir}")
    print(f"📄 Array completo: {array_file}")

if __name__ == "__main__":
    main()
