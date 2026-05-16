#!/usr/bin/env python3
"""
Test de integración CAIE + ForensicAdapter
"""

import json
import sys
from pathlib import Path

# Asegurar que vigia está en path
sys.path.insert(0, str(Path(__file__).parent))

from vigia.sift.sift_orchestrator import SIFTOrchestrator

# Cargar caso
case_path = sys.argv[1] if len(sys.argv) > 1 else "cases/case_003_false_flag.json"
with open(case_path) as f:
    case_data = json.load(f)

print(f"=== CASO: {case_path} ===")
print(f"Descripción: {case_data.get('description', 'N/A')}")
print()

# Crear orchestrator y correr
orch = SIFTOrchestrator(case_id=case_data.get("case_id", "TEST-001"))

# Extraer parámetros del caso (ajustar según estructura real)
params = case_data.get("inputs", case_data)

print("Ejecutando run_full_analysis()...")
result = orch.run_full_analysis(**params)

print()
print("=== RESULTADO CAIE ===")
caie = result.get("caie", {})
print(f"Status: {caie.get('status', 'N/A')}")
print(f"Verdict: {caie.get('verdict', 'N/A')}")
print(f"Composite Score: {caie.get('composite_score', 'N/A')}")
print(f"Fractures detectados: {caie.get('fractures_detected', 'N/A')}")
print(f"Golden Rules: {caie.get('golden_rules_triggered', 'N/A')}")

if caie.get("fractures"):
    print()
    print("Fracturas:")
    for f in caie["fractures"][:3]:
        print(f"  - {f.get('type')}: {f.get('artifact_a', '')[:50]} vs {f.get('artifact_b', '')[:50]}")

print()
print("=== METADATA PIPELINE ===")
meta = result.get("pipeline_meta", {})
print(f"Total señales: {meta.get('n_total_signals', 'N/A')}")
print(f"CAIE ejecutado: {meta.get('caie_executed', 'N/A')}")
print(f"CAIE verdict: {meta.get('caie_verdict', 'N/A')}")

print()
print("=== ABDUCTIVE V2 ===")
v2 = result.get("abduction_v2", {})
print(f"Status: {v2.get('status', 'N/A')}")
print(f"Artefactos: {v2.get('n_artifacts', 'N/A')}")
print(f"Layers: {v2.get('layers', 'N/A')}")

print()
print("✓ Test completado")
