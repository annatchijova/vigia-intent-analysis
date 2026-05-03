#!/usr/bin/env python3
"""Convierte casos ChatGPT al formato VIGÍA CaseAdapter."""
import json, sys

with open(sys.argv[1]) as f:
    cases = json.load(f)

for case in cases:
    new_artifacts = []
    for i, art in enumerate(case["artifacts"]):
        art_type = art.get("type", "log")
        # Mapear tipo a evidence_type
        evidence_map = {
            "auth.log": "log_entry",
            "netflow": "network_artifact", 
            "audit": "log_entry",
            "filesystem": "file_timestamp",
            "bash_history": "log_entry",
            "ticket": "file_metadata",
            "script": "file_hash",
            "network": "network_artifact",
            "binary": "file_hash",
            "log": "log_entry",
            "system": "log_entry",
            "traffic": "network_artifact",
            "text": "log_entry",
            "context": "file_metadata"
        }
        evidence_type = evidence_map.get(art_type, "log_entry")
        
        # Derivar score del contenido (heuristico simple)
        content = art.get("content", "").lower()
        if any(w in content for w in ["exfil", "mimikatz", "dump", "nmap"]):
            score = 0.85
        elif any(w in content for w in ["suspicious", "ssh", "russian"]):
            score = 0.60
        elif "NO ENTRY" in content:
            score = 0.10
        else:
            score = 0.30
            
        new_artifacts.append({
            "artifact_id": art.get("id", f"ART-{i+1:03d}"),
            "evidence_type": evidence_type,
            "raw_score": score,
            "description": art.get("content", ""),
            "source_tool": "chatgpt_test",
            "metadata": art
        })
    
    case["artifacts"] = new_artifacts
    # Mantener expected para validación
    
    out = f"/tmp/vigia_break_{case['case_id']}.json"
    with open(out, "w") as f:
        json.dump(case, f, indent=2)
    print(f"OK → {out}")
