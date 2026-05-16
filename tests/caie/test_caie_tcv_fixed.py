#!/usr/bin/env python3
"""
Test CAIE TCV con case_001_temporal_pipeline.json (el que creamos con timestamps en metadata)
"""

import json
import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from vigia.tools.caie import cross_artifact_analysis

async def main():
    case_path = "cases/case_001_temporal_pipeline.json"
    with open(case_path) as f:
        case_data = json.load(f)

    print("=== CAIE TCV TEST ===")
    print(f"Caso: {case_data['case_id']}")
    print()

    # Pasar artifacts DIRECTAMENTE a CAIE (formato que espera)
    caie_input = []
    for art in case_data["artifacts"]:
        caie_input.append({
            "source_tool": art["source_tool"],
            "evidence_type": art["evidence_type"],
            "raw_score": art["raw_score"],
            "description": art.get("description", ""),
            "metadata": art.get("metadata", {}),
            "base_trust": art.get("prior_trust", 1.0),
        })
        print(f"  {art['artifact_id']}: {art['evidence_type']}")
        print(f"    meta: { {k:v for k,v in art['metadata'].items() if 'time' in k or 'pid' in k} }")

    print(f"\nCAIE input: {len(caie_input)} artifacts")
    result = await cross_artifact_analysis(caie_input)

    print(f"\n=== RESULTADO ===")
    print(f"Status: {result.get('status')}")
    print(f"Verdict: {result.get('verdict')}")
    print(f"Composite: {result.get('composite_score')}")
    print(f"Fractures: {result.get('fractures_detected')}")
    print(f"Golden Rules: {result.get('golden_rules_triggered')}")

    if result.get("fractures"):
        print("\n🔥 FRACTURAS:")
        for f in result["fractures"]:
            print(f"  [{f['type']}] sev={f['severity']}")
            print(f"    A: {f['artifact_a'][:70]}")
            print(f"    B: {f['artifact_b'][:70]}")

    print(f"\nPeirce Thirdness: {result.get('peirce_chain', {}).get('thirdness', 'N/A')[:100]}")

if __name__ == "__main__":
    asyncio.run(main())
