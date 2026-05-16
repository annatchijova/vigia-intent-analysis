#!/usr/bin/env python3
"""
Test CAIE PIPELINE REAL con case_001_temporal_pipeline.json
SignalOutput → ForensicAdapter → CAIE (con hashes y timestamps)
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
    case_path = "cases/case_001_temporal_pipeline.json"
    with open(case_path) as f:
        case_data = json.load(f)

    print("=" * 70)
    print("VIGÍA PIPELINE REAL — CAIE + FORENSIC ADAPTER")
    print("=" * 70)
    print(f"Caso: {case_data['case_id']}")
    print(f"Descripción: {case_data['description']}")
    print()

    # Convertir a SignalOutput (simulando salida de SIFT motores)
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
                **art.get("metadata", {}),  # Incluye process_creation_time, network_log_time, etc.
            }
        )
        signals.append(sig)
        print(f"📡 {art['artifact_id']}: {art['evidence_type']}")
        print(f"   z_score={sig.z_score:.2f} | value={sig.value}")
        print(f"   timestamp={art.get('timestamp', 'N/A')}")
        print(f"   meta: { {k:v for k,v in art['metadata'].items() if 'time' in k or 'pid' in k} }")

    # FORENSIC ADAPTER
    print()
    print("-" * 70)
    print("FORENSIC ADAPTER (SignalOutput → CAIE Artifact + ArtifactRecord)")
    print("-" * 70)
    
    adapter = ForensicAdapter()
    context = adapter.build_context(signals)

    for a in context.caie_artifacts:
        print(f"🔍 CAIE Artifact: {a.source_tool}")
        print(f"   evidence_type: {a.evidence_type}")
        print(f"   raw_score: {a.raw_score:.4f}")
        print(f"   provenance_hash: {a.provenance_chain[0][:16]}...")
        print(f"   timestamp: {a.timestamp}")

    for r in context.abductive_records:
        print(f"📋 ArtifactRecord: {r.artifact_id}")
        print(f"   layer: {r.layer.name}")
        print(f"   sha256: {r.sha256_hash[:16]}...")
        print(f"   timestamp: {r.acquisition_timestamp_utc}")

    # CAIE REAL
    print()
    print("-" * 70)
    print("CAIE — Cross-Artifact Incongruence Engine (v2.0 DETERMINISTIC)")
    print("-" * 70)

    caie_input = [
        {
            "source_tool": a.source_tool,
            "evidence_type": a.evidence_type,
            "raw_score": a.raw_score,
            "description": a.description,
            "metadata": a.metadata,
            "base_trust": getattr(a, 'base_trust', 1.0),
            "provenance_chain": a.provenance_chain,
        }
        for a in context.caie_artifacts
    ]

    result = await cross_artifact_analysis(caie_input)

    print(f"Status: {result.get('status')}")
    print(f"Verdict: {result.get('verdict')}")
    print(f"Composite Score: {result.get('composite_score')}")
    print(f"Fracturas detectadas: {result.get('fractures_detected')}")
    print(f"Golden Rules: {result.get('golden_rules_triggered')}")

    if result.get("fractures"):
        print()
        print("🔥 FRACTURAS DETECTADAS:")
        for f in result["fractures"]:
            print(f"\n  [{f['type']}] severity={f['severity']}")
            print(f"   A: {f['artifact_a'][:70]}")
            print(f"   B: {f['artifact_b'][:70]}")
            print(f"   → {f['interpretation'][:120]}...")

    print()
    print("-" * 70)
    print("PEIRCE CHAIN:")
    for k, v in result.get("peirce_chain", {}).items():
        print(f"  {k}: {str(v)[:80]}...")

    print()
    print("DAUBERT:")
    print(f"  {result.get('daubert_note', 'N/A')}")

    print()
    print("=" * 70)
    print("✓ PIPELINE REAL COMPLETADO")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(main())
