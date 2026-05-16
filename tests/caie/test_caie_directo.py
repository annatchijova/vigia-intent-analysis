#!/usr/bin/env python3
"""
Test directo de CAIE con caso real case_003_false_flag.json
Sin orchestrator — solo CAIE + ForensicAdapter
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
    # Cargar caso
    case_path = "cases/case_003_false_flag.json"
    with open(case_path) as f:
        case_data = json.load(f)

    print(f"=== CASO: {case_data['case_id']} ===")
    print(f"Descripción: {case_data['description']}")
    print(f"Artefactos en caso: {len(case_data['artifacts'])}")
    print()

    # Convertir artifacts del caso a SignalOutput (simulando salida de SIFT)
    signals = []
    for art in case_data["artifacts"]:
        sig = SignalOutput(
            tool_name=art["source_tool"],
            value=float(art["raw_score"]),
            z_score=art["raw_score"] * 4,
            confidence=art.get("prior_trust", 0.5),
            metadata={
                "artifact_type": art["evidence_type"],
                "description": art.get("description", ""),
                **art.get("metadata", {}),
            }
        )
        signals.append(sig)
        print(f"  Signal: {sig.tool_name} | type={art['evidence_type']} | z={sig.z_score:.2f} | value={sig.value}")

    print()
    print("=== FORENSIC ADAPTER ===")
    adapter = ForensicAdapter()
    context = adapter.build_context(signals)

    print(f"CAIE artifacts: {len(context.caie_artifacts)}")
    print(f"Abductive records: {len(context.abductive_records)}")
    print(f"Causal links: {len(context.causal_links)}")

    for a in context.caie_artifacts:
        print(f"  CAIE: {a.source_tool} | {a.evidence_type} | score={a.raw_score:.4f}")

    print()
    print("=== CAIE EJECUTANDO ===")
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

    print()
    print("=== RESULTADO CAIE ===")
    print(f"Status: {result.get('status')}")
    print(f"Verdict: {result.get('verdict')}")
    print(f"Composite Score: {result.get('composite_score')}")
    print(f"Fractures detectados: {result.get('fractures_detected')}")
    print(f"Golden Rules: {result.get('golden_rules_triggered')}")

    if result.get("fractures"):
        print()
        print("Fracturas detectadas:")
        for f in result["fractures"]:
            print(f"  🔥 {f['type']} (severity={f['severity']})")
            print(f"     A: {f['artifact_a'][:80]}")
            print(f"     B: {f['artifact_b'][:80]}")
            print(f"     → {f['interpretation'][:120]}...")

    print()
    print("=== PEIRCE CHAIN ===")
    peirce = result.get("peirce_chain", {})
    for k, v in peirce.items():
        print(f"  {k}: {str(v)[:100]}...")

    print()
    print("=== DAUBERT ===")
    print(result.get("daubert_note", "N/A"))

    print()
    print("✓ CAIE YA NO ES ADORNO")

if __name__ == "__main__":
    asyncio.run(main())
