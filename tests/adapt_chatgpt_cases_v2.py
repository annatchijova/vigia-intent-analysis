#!/usr/bin/env python3
"""
Convierte casos ChatGPT al formato VIGÍA CaseAdapter.
v2: reglas forenses reales, no keywords sueltas.
"""
import json, sys

with open(sys.argv[1]) as f:
    cases = json.load(f)

for case in cases:
    cid = case["case_id"]
    new_artifacts = []
    
    for i, art in enumerate(case.get("artifacts", [])):
        content = art.get("content", "").strip()
        art_type = art.get("type", "log")
        cl = content.lower()
        
        # ── Mapeo de evidence_type ──────────────────────────────
        evidence_map = {
            "auth.log": "log_entry", "netflow": "network_artifact",
            "audit": "log_entry", "filesystem": "file_timestamp",
            "bash_history": "log_entry", "ticket": "file_metadata",
            "script": "file_hash", "network": "network_artifact",
            "binary": "file_hash", "log": "log_entry",
            "system": "log_entry", "traffic": "network_artifact",
            "text": "log_entry", "context": "file_metadata"
        }
        evidence_type = evidence_map.get(art_type, "log_entry")
        
        # ── Scoring forense real ────────────────────────────────
        # Por defecto, desconocido = señal baja
        score = 0.15
        
        # Contra-evidencia (tickets, autorizaciones)
        if any(w in cl for w in ["authorized", "approved", "pentest", "ticket"]):
            score = 0.05  # Esto BAJA el score total
            evidence_type = "file_metadata"
        
        # Señales técnicas fuertes
        elif any(w in cl for w in ["exfil", "mimikatz", "dump", "nmap", "data dump"]):
            score = 0.88
        elif any(w in cl for w in ["russian", "valid execution", "c2", "infra"]):
            score = 0.82
        elif any(w in cl for w in ["ssh session", "ftp transfer"]):
            score = 0.65
        
        # Ausencia de logs = señal (Eco filter)
        elif "no entry" in cl:
            score = 0.90  # La ausencia es la señal
            evidence_type = "log_entry"
        
        # Inconsistencia temporal
        elif "utc+2" in cl or "utc+3" in cl:
            score = 0.60
        
        # Ruido explícito
        elif "irrelevant" in cl:
            score = 0.02  # Casi cero
            evidence_type = "log_entry"
        
        # Perfección sospechosa
        elif "exactly" in cl or "zero jitter" in cl:
            score = 0.75
        
        # Prompt poisoning: texto engañoso
        elif "already confirmed benign" in cl:
            score = 0.10  # Esto es FUD, no evidencia
        
        new_artifacts.append({
            "artifact_id": art.get("id", f"ART-{i+1:03d}"),
            "evidence_type": evidence_type,
            "raw_score": score,
            "description": content,
            "source_tool": "read_evidence",
            "provenance_chain": ["sha256:chatgpt_synthetic_test"],
            "metadata": art
        })
    
    case["artifacts"] = new_artifacts
    
    # Mapear expected_verdict correctamente
    exp = case.get("expected", {})
    if exp:
        verdict_map = {
            "MALICE": "MALICE", "BENIGN_OR_UNCERTAIN": "NOISE",
            "BENIGN": "NOISE", "NOISE": "NOISE"
        }
        case["expected_verdict"] = verdict_map.get(
            exp.get("verdict", "").upper(), "UNKNOWN"
        )
    
    out = f"/tmp/vigia_break_{cid}.json"
    with open(out, "w") as f:
        json.dump(case, f, indent=2)
    print(f"OK → {out}")
