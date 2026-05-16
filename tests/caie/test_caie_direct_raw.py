#!/usr/bin/env python3
"""
Test CAIE DIRECTO con case_001_temporal.json — sin adapter, sin SignalOutput
Como se hacía ANTES de la integración.
"""

import json
import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from vigia.tools.caie import cross_artifact_analysis

async def main():
    case_path = "cases/case_001_temporal.json"
    with open(case_path) as f:
        case_data = json.load(f)

    print(f"=== CASO: {case_data['case_id']} ===")
    print(f"Descripción: {case_data['description']}")
    print()

    # Pasar artifacts DIRECTAMENTE como espera CAIE (formato original del caso)
    caie_input = []
    for art in case_data["artifacts"]:
        caie_input.append({
            "source_tool": art["source_tool"],
            "evidence_type": art["evidence_type"],
            "raw_score": art["raw_score"],
            "description": art.get("description", ""),
            "metadata": art.get("metadata", {}),
            "base_trust": art.get("prior_trust", 1.0),
            "provenance_chain": art.get("provenance_chain", []),
        })
        print(f"  {art['artifact_id']}: {art['evidence_type']} | score={art['raw_score']} | meta={sorted(art.get('metadata',{}).keys())}")

    print(f"\n=== CAIE INPUT (formato original) ===")
    print(f"Artifacts: {len(caie_input)}")

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
            print(f"     → {f['interpretation'][:120]}...")

    print(f"\nDaubert: {result.get('daubert_note')}")

if __name__ == "__main__":
    asyncio.run(main())
