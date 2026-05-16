#!/usr/bin/env python3
"""
Test CAIE con caso break real — vigia_break_001_silent_inconsistency.json
"""

import json
import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from vigia.tools.caie import cross_artifact_analysis

async def main():
    case_path = "cases/vigia_break_001_silent_inconsistency.json"
    with open(case_path) as f:
        case_data = json.load(f)

    print(f"=== CASO: {case_data.get('case_id', 'N/A')} ===")
    print(f"Descripción: {case_data.get('description', 'N/A')[:100]}")
    print(f"Artefactos: {len(case_data.get('artifacts', []))}")
    print()

    # Ver estructura del primer artifact
    if case_data.get('artifacts'):
        first = case_data['artifacts'][0]
        print(f"Primer artifact keys: {sorted(first.keys())}")
        print(f"Metadata keys: {sorted(first.get('metadata', {}).keys())}")

    # Intentar pasar a CAIE como viene
    caie_input = []
    for art in case_data.get("artifacts", []):
        caie_input.append({
            "source_tool": art.get("source_tool", "unknown"),
            "evidence_type": art.get("evidence_type", "log_entry"),
            "raw_score": art.get("raw_score", 0.0),
            "description": art.get("description", ""),
            "metadata": art.get("metadata", {}),
            "base_trust": art.get("prior_trust", 1.0),
        })

    if not caie_input:
        print("⚠ No hay artifacts para CAIE")
        return

    print(f"\nCAIE input: {len(caie_input)} artifacts")
    result = await cross_artifact_analysis(caie_input)

    print(f"\n=== RESULTADO ===")
    print(f"Status: {result.get('status')}")
    print(f"Verdict: {result.get('verdict')}")
    print(f"Composite: {result.get('composite_score')}")
    print(f"Fracturas: {result.get('fractures_detected')}")

    if result.get("fractures"):
        for f in result["fractures"]:
            print(f"\n  🔥 {f['type']} (sev={f['severity']})")

if __name__ == "__main__":
    asyncio.run(main())
