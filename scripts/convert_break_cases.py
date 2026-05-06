#!/usr/bin/env python3
"""
scripts/convert_break_cases.py
==============================
Convierte casos VIGIA_BREAK (formato legacy) al formato canónico EBS v1.

Los casos break evalúan capacidades específicas del motor forense.
Este convertidor asigna scores y estructura forense apropiados.
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone

# Mapeo: tipo legacy → evidence_type canónico
TYPE_MAP = {
    "auth.log": "log_entry",
    "netflow": "network_artifact",
    "audit": "log_entry",
    "filesystem": "file_timestamp",
    "bash_history": "log_entry",
    "ticket": "log_entry",
    "script": "log_entry",
    "network": "network_artifact",
    "binary": "memory_process",
    "log": "log_entry",
    "system": "log_entry",
    "auth": "log_entry",
    "text": "log_entry",
    "traffic": "network_artifact",
    "context": "log_entry",
}

# Scores base por tipo de caso break
def assign_scores(case_id: str, artifacts: list) -> list:
    """Asigna raw_score y prior_trust basado en el caso."""
    scores = {
        "VIGIA_BREAK_001_SILENT_INCONSISTENCY": [0.8, 0.8, 0.8, 0.7],
        "VIGIA_BREAK_002_VALID_BENIGN": [0.6, 0.9],
        "VIGIA_BREAK_003_CULTURAL_TRUE_POSITIVE": [0.7, 0.8, 0.85],
        "VIGIA_BREAK_004_SIGNAL_DROWNING": [0.3, 0.3, 0.9, 0.85],
        "VIGIA_BREAK_005_FALSE_CORRELATION": [0.7, 0.6, 0.7],
        "VIGIA_BREAK_006_PERFECT_ATTACK": [0.85, 0.8, 0.8],
        "VIGIA_BREAK_007_MISSING_LOGS": [0.8, 0.2],
        "VIGIA_BREAK_008_AMBIGUOUS": [0.5, 0.5],
        "VIGIA_BREAK_009_PROMPT_POISON": [0.4, 0.8],
        "VIGIA_BREAK_010_OVERPERFECT": [0.7, 0.7],
    }
    base_scores = scores.get(case_id, [0.5] * len(artifacts))
    return base_scores

def build_temporal_violations(case_id: str, artifacts: list) -> list:
    """Construye violaciones temporales para casos relevantes."""
    violations = []
    
    if case_id == "VIGIA_BREAK_001_SILENT_INCONSISTENCY":
        # Timezone inconsistente: log4 tiene UTC+2 vs UTC+3
        violations.append({
            "type": "CLOCK_SKEW",
            "severity": 0.8,
            "cause": {
                "artifact_id": artifacts[0].get("id", "unknown"),
                "timestamp": "2026-04-10T10:00:00+03:00",
                "description": "SSH login at UTC+3"
            },
            "effect": {
                "artifact_id": artifacts[3].get("id", "unknown"),
                "timestamp": "2026-04-10T10:00:00+02:00",
                "description": "File access at UTC+2 — timezone mismatch"
            },
            "delta_seconds": 0,
            "interpretation": "Same nominal time but different timezones — temporal inconsistency detected"
        })
    
    elif case_id == "VIGIA_BREAK_007_MISSING_LOGS":
        # Missing logs where they should exist
        violations.append({
            "type": "STATISTICAL_UNIFORMITY",
            "severity": 0.9,
            "cause": {
                "artifact_id": artifacts[0].get("id", "unknown"),
                "timestamp": "2026-04-10T10:00:00Z",
                "description": "SSH session present in netflow"
            },
            "effect": {
                "artifact_id": artifacts[1].get("id", "unknown"),
                "timestamp": "2026-04-10T10:00:00Z",
                "description": "NO ENTRY in auth.log — missing evidence"
            },
            "delta_seconds": 0,
            "interpretation": "Network session exists but authentication log is absent — evidence destruction or log tampering"
        })
    
    elif case_id == "VIGIA_BREAK_010_OVERPERFECT":
        # Over-perfect logs
        violations.append({
            "type": "STATISTICAL_UNIFORMITY",
            "severity": 0.7,
            "cause": {
                "artifact_id": artifacts[0].get("id", "unknown"),
                "timestamp": "2026-04-10T10:00:00Z",
                "description": "Events every exactly 10.000 seconds"
            },
            "effect": {
                "artifact_id": artifacts[1].get("id", "unknown"),
                "timestamp": "2026-04-10T10:00:00Z",
                "description": "Zero jitter in traffic"
            },
            "delta_seconds": 0,
            "interpretation": "Statistically impossible uniformity — artificial pattern generation detected"
        })
    
    return violations

def build_peirce_chain(case_id: str, description: str, artifacts: list) -> dict:
    """Construye cadena Peirce para casos relevantes."""
    chains = {
        "VIGIA_BREAK_001_SILENT_INCONSISTENCY": {
            "firstness": "Four artifacts show same nominal time but one has different timezone",
            "secondness": "UTC+2 vs UTC+3 creates temporal inconsistency even at same clock time",
            "thirdness": "Deliberate timezone manipulation to obscure event sequence"
        },
        "VIGIA_BREAK_002_VALID_BENIGN": {
            "firstness": "Suspicious commands detected in bash history",
            "secondness": "Authorized pentest ticket present with matching timeframe",
            "thirdness": "Activity is authorized security testing, not malicious intrusion"
        },
        "VIGIA_BREAK_003_CULTURAL_TRUE_POSITIVE": {
            "firstness": "Russian language markers and infrastructure connections observed",
            "secondness": "Technical execution traces confirm valid malicious payload",
            "thirdness": "Cultural markers corroborate technical evidence — true positive, not bias"
        },
        "VIGIA_BREAK_004_SIGNAL_DROWNING": {
            "firstness": "Multiple irrelevant log entries obscure critical artifacts",
            "secondness": "Critical netflow and audit entries show exfiltration patterns",
            "thirdness": "Signal-to-noise analysis must prioritize high-value artifacts"
        },
        "VIGIA_BREAK_005_FALSE_CORRELATION": {
            "firstness": "Three events occur simultaneously",
            "secondness": "No causal chain links ftp transfer to package update to ssh login",
            "thirdness": "Temporal coincidence does not imply causation — avoid false correlation"
        },
        "VIGIA_BREAK_006_PERFECT_ATTACK": {
            "firstness": "Clean exfiltration, valid credentials, consistent timestamps",
            "secondness": "No technical inconsistencies detected in any artifact",
            "thirdness": "Absence of errors is suspicious — advanced persistent threat with OPSEC discipline"
        },
        "VIGIA_BREAK_007_MISSING_LOGS": {
            "firstness": "Network session established",
            "secondness": "Authentication log shows NO ENTRY where record should exist",
            "thirdness": "Log deletion or suppression — evidence tampering detected"
        },
        "VIGIA_BREAK_008_AMBIGUOUS": {
            "firstness": "Suspicious activity observed but with plausible benign explanation",
            "secondness": "Context supports both malicious and benign interpretations equally",
            "thirdness": "Insufficient evidence for definitive classification — maintain uncertainty"
        },
        "VIGIA_BREAK_009_PROMPT_POISON": {
            "firstness": "Text claims incident is benign",
            "secondness": "Network data shows exfiltration independently of text narrative",
            "thirdness": "Unverified textual claims must not override technical evidence"
        },
        "VIGIA_BREAK_010_OVERPERFECT": {
            "firstness": "System events occur at exactly 10-second intervals",
            "secondness": "Zero jitter in network traffic is statistically impossible naturally",
            "thirdness": "Artificial pattern generation — synthetic logs injected"
        },
    }
    return chains.get(case_id, {
        "firstness": description,
        "secondness": "Technical analysis of artifacts",
        "thirdness": "Forensic inference"
    })

def convert_case(case: dict) -> dict:
    """Convierte un caso break al formato canónico EBS v1."""
    case_id = case["case_id"]
    description = case.get("description", "")
    artifacts_raw = case.get("artifacts", [])
    
    # Asignar scores
    scores = assign_scores(case_id, artifacts_raw)
    
    # Convertir artefactos
    canonical_artifacts = []
    for i, art in enumerate(artifacts_raw):
        art_id = art.get("id", f"art_{i}")
        art_type = art.get("type", "unknown")
        content = art.get("content", "")
        
        canonical_artifacts.append({
            "artifact_id": art_id,
            "evidence_type": TYPE_MAP.get(art_type, "default"),
            "source_tool": "break_test_generator",
            "timestamp": f"2026-04-10T10:00:{i:02d}Z",
            "raw_score": scores[i] if i < len(scores) else 0.5,
            "prior_trust": 0.7,
            "provenance_chain": [f"sha256:break_{case_id}_{art_id}"],
            "description": content,
            "metadata": {
                "original_type": art_type,
                "break_case": case_id,
                "content": content
            }
        })
    
    # Construir expected
    expected = case.get("expected", {})
    verdict_map = {
        "VIGIA_BREAK_001_SILENT_INCONSISTENCY": "SUSPICION",
        "VIGIA_BREAK_002_VALID_BENIGN": "BENIGN",
        "VIGIA_BREAK_003_CULTURAL_TRUE_POSITIVE": "MALICE",
        "VIGIA_BREAK_004_SIGNAL_DROWNING": "MALICE",
        "VIGIA_BREAK_005_FALSE_CORRELATION": "NOISE",
        "VIGIA_BREAK_006_PERFECT_ATTACK": "MALICE",
        "VIGIA_BREAK_007_MISSING_LOGS": "MALICE",
        "VIGIA_BREAK_008_AMBIGUOUS": "SUSPICION",
        "VIGIA_BREAK_009_PROMPT_POISON": "MALICE",
        "VIGIA_BREAK_010_OVERPERFECT": "SUSPICION",
    }
    
    return {
        "case_id": case_id,
        "name": description,
        "description": description,
        "artifacts": canonical_artifacts,
        "temporal_violations": build_temporal_violations(case_id, artifacts_raw),
        "expected_verdict": verdict_map.get(case_id, "SUSPICION"),
        "expected_confidence": 0.85,
        "expected_mitre_ttps": ["T1070.006"],
        "peirce_chain": build_peirce_chain(case_id, description, artifacts_raw),
        "demo_command": f"python tests/run_vigia_case.py cases/{case_id.lower()}.json",
        "demo_quote": description
    }

def main():
    input_file = Path("data/cases/VIGIA_BREAK_001-010.json")
    output_dir = Path("cases")
    
    if not input_file.exists():
        print(f"ERROR: {input_file} no encontrado")
        sys.exit(1)
    
    with open(input_file) as f:
        cases = json.load(f)
    
    converted = []
    for case in cases:
        canonical = convert_case(case)
        converted.append(canonical)
        
        # Guardar individual
        out_file = output_dir / f"{canonical['case_id'].lower()}.json"
        with open(out_file, "w") as f:
            json.dump(canonical, f, indent=2, ensure_ascii=False)
        print(f"✅ Convertido: {canonical['case_id']} → {out_file}")
    
    # Guardar array completo
    array_file = output_dir / "vigia_break_canonical_001-010.json"
    with open(array_file, "w") as f:
        json.dump(converted, f, indent=2, ensure_ascii=False)
    print(f"✅ Array completo: {array_file}")
    print(f"✅ Total: {len(converted)} casos convertidos")

if __name__ == "__main__":
    main()
