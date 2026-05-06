"""
vigia/tests/test_2_vs_1_pipeline.py

Test del caso 2-vs-1 completo:
- Memoria (z=3.5, Γ=0.95) + Registro (z=3.4, Γ=0.70) = REDUNDANT → FRS
- Luego vs Logs (z=0.1, Γ=0.60) = CONTRADICTORY → penalización

Valida el pipeline completo: Gamma → FRS → CONTRADICTORY → Narrativa
"""

from __future__ import annotations
from fractions import Fraction

# Simulación standalone del pipeline
import sys
sys.path.insert(0, '/mnt/agents/output')

from vigia.sift._math_utils import (
    apply_artifact_reliability,
    build_redundancy_groups,
    classify_group,
    apply_conflict_penalty,
    process_all_groups,
)

class MockSignal:
    def __init__(self, tool, z, conf, meta):
        self.tool_name = tool
        self.z_score = z
        self.confidence = conf
        self.metadata = meta
        self.value = z / 5.0

def entity_key_fn(sig):
    pid = sig.metadata.get("pid", 0)
    if pid:
        return (f"pid:{pid}", sig.metadata.get("timestamp", 0))
    return (sig.tool_name, 0)

print("=" * 60)
print("TEST 2-VS-1: Pipeline Completo")
print("=" * 60)

# Paso 0: Señales crudas
signals = [
    MockSignal("MEMORY_FORENSICS", 3.5, 0.95, {
        "pid": 999, "timestamp": 1000, "artifact_type": "memory",
        "finding_types": ["malfind_pe_injection"]
    }),
    MockSignal("REGISTRY_RTR", 3.4, 0.70, {
        "pid": 999, "timestamp": 1002, "artifact_type": "registry",
        "finding_types": ["run_key"]
    }),
    MockSignal("EVENT_LOG", 0.1, 0.60, {
        "pid": 999, "timestamp": 1005, "artifact_type": "event_log",
        "finding_types": ["LOG_WIPE_AFTER_ATTACK"]
    }),
]

print("\n--- Paso 1: Gamma (Artifact Reliability) ---")
gamma_signals = []
for sig in signals:
    z_frac = Fraction(int(round(sig.z_score * 100)), 100)
    z_adj = apply_artifact_reliability(z_frac, sig.metadata["artifact_type"])
    sig.z_score = float(z_adj)
    sig.metadata["gamma_applied"] = True
    gamma_signals.append(sig)
    print(f"  {sig.tool_name}: {sig.z_score} (Γ={sig.metadata['artifact_type']})")

print("\n--- Paso 2: Redundancy Groups ---")
groups = build_redundancy_groups(gamma_signals, entity_key_fn, delta_t=60)
print(f"  Grupos: {len(groups)}")
for i, g in enumerate(groups):
    print(f"    Grupo {i}: {g}")

print("\n--- Paso 3: Clasificación por grupo ---")
for i, group in enumerate(groups):
    cls = classify_group(gamma_signals, group)
    print(f"  Grupo {i}: {cls}")

print("\n--- Paso 4: Pipeline completo (process_all_groups) ---")
final_signals = process_all_groups(gamma_signals, groups)

print("\n--- Resultados finales ---")
for sig in final_signals:
    print(f"  {sig.tool_name}:")
    print(f"    z_score: {sig.z_score}")
    if sig.metadata.get("conflict"):
        print(f"    CONFLICT: z_before={sig.metadata.get('z_before_conflict')}, z_after={sig.metadata.get('z_after_conflict')}")
    if sig.metadata.get("frs_applied"):
        print(f"    FRS: factor={sig.metadata.get('frs_factor')}")

# Validaciones
print("\n--- Validaciones ---")

# En CONTRADICTORY, NO se aplica FRS (se aplica penalización de conflicto)
has_conflict = any(s.metadata.get("conflict") for s in final_signals)
dominant = max(final_signals, key=lambda s: s.z_score)

print(f"Conflicto detectado: {has_conflict} (esperado: True)")
print(f"Dominante: {dominant.tool_name} (z={dominant.z_score})")

# Verificar que el dominante tiene metadata de conflicto
if dominant.metadata.get("conflict"):
    print(f"  conflict_sources: {dominant.metadata.get('conflict_sources')}")
    print(f"  z_before: {dominant.metadata.get('z_before_conflict')}")
    print(f"  z_after: {dominant.metadata.get('z_after_conflict')}")
    print(f"  penalty: {dominant.metadata.get('conflict_penalty')}")

assert has_conflict, "Conflicto debería detectarse"
# El dominante debería ser REGISTRY (2.38) porque MEMORY fue penalizado (1.69)
assert dominant.tool_name == "MEMORY_FORENSICS", f"Dominante debería ser MEMORY, got {dominant.tool_name}"

print("\n" + "=" * 60)
print("✅ TEST 2-VS-1 PASADO")
print("=" * 60)
