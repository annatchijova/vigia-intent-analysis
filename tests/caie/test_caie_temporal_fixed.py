#!/usr/bin/env python3
"""
Test CAIE con case_001_temporal.json — FIX para TCV detection
"""

import json
import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from vigia.tools.caie import cross_artifact_analysis
from vigia.core.forensic_adapter import ForensicAdapter
from vigia.core.ebs_v1 import SignalOutput

async def main():
    case_path = "cases/case_001_temporal.json"
    with open(case_path) as f:
        case_data = json.load(f)

    print(f"=== CASO: {case_data['case_id']} ===")
    print(f"Descripción: {case_data['description']}")
    print()

    signals = []
    for art in case_data["artifacts"]:
        meta = {
            "artifact_type": art["evidence_type"],
            "description": art.get("description", ""),
        }
        
        # MAPEO ESPECIAL para TCV: pasar los timestamps que CAIE espera
        raw_meta = art.get("metadata", {})
        
        if "process_creation_time" in raw_meta:
            meta["process_creation_time"] = raw_meta["process_creation_time"]
        if "network_log_time" in raw_meta:
            meta["network_log_time"] = raw_meta["network_log_time"]
        if "file_write_time" in raw_meta:
            meta["timestamp"] = raw_meta["file_write_time"]
        if "firewall_claim" in raw_meta:
            meta["firewall_claim"] = raw_meta["firewall_claim"]
        if "host_reality" in raw_meta:
            meta["host_reality"] = raw_meta["host_reality"]
        if "open_sockets" in raw_meta:
            meta["open_sockets"] = raw_meta["open_sockets"]
        
        # Extra: pasar todo el metadata original también
        meta.update(raw_meta)

        sig = SignalOutput(
            tool_name=art["source_tool"],
            value=float(art["raw_score"]),
            z_score=art["raw_score"] * 4,
            confidence=art.get("prior_trust", 0.5),
            metadata=meta
        )
        signals.append(sig)
        print(f"  {art['artifact_id']}: {art['evidence_type']} | z={sig.z_score:.2f}")
        print(f"    meta keys: {sorted(meta.keys())}")

    adapter = ForensicAdapter()
    context = adapter.build_context(signals)

    print(f"\n=== ADAPTER ===")
    for a in context.caie_artifacts:
        print(f"  CAIE: {a.evidence_type} | score={a.raw_score:.4f}")
        print(f"    meta: { {k:v for k,v in a.metadata.items() if 'time' in k or 'creation' in k} }")

    caie_input = [
        {
            "source_tool": a.source_tool,
            "evidence_type": a.evidence_type,
            "raw_score": a.raw_score,
            "description": a.description,
            "metadata": a.metadata,
            "base_trust": getattr(a, 'base_trust', 1.0),
        }
        for a in context.caie_artifacts
    ]

    result = await cross_artifact_analysis(caie_input)

    print(f"\n=== RESULTADO ===")
    print(f"Verdict: {result.get('verdict')}")
    print(f"Composite: {result.get('composite_score')}")
    print(f"Fracturas: {result.get('fractures_detected')}")
    print(f"Golden Rules: {result.get('golden_rules_triggered')}")

    if result.get("fractures"):
        for f in result["fractures"]:
            print(f"\n  🔥 {f['type']} (sev={f['severity']})")
            print(f"     A: {f['artifact_a'][:80]}")
            print(f"     B: {f['artifact_b'][:80]}")
            print(f"     → {f['interpretation'][:150]}...")

    print(f"\nDaubert: {result.get('daubert_note')}")

if __name__ == "__main__":
    asyncio.run(main())
