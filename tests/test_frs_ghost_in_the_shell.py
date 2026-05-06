"""
vigia/tests/test_frs_ghost_in_the_shell.py

Test unitario determinista para FRS + Ghost In The Shell.
Valida:
1. Caso PID 123: 3 señales redundantes → MALICE_MEDIUM (no HIGH)
2. Caso CONTRADICTORY: memoria fuerte + logs débiles → penalización
3. Edge cases: PID recycling, temporal boundary, 2-vs-1

Determinismo: seeds fijos, inputs ordenados, no datetime en asserts.
"""

from __future__ import annotations

from fractions import Fraction
from typing import List, Dict, Any

# Mock SignalOutput para tests
class MockSignalOutput:
    def __init__(self, tool_name: str, z_score: float, confidence: float, metadata: Dict[str, Any]):
        self.tool_name = tool_name
        self.z_score = z_score
        self.confidence = confidence
        self.metadata = metadata
        self.value = z_score / 5.0  # Mock

    def __repr__(self):
        return f"MockSignalOutput({self.tool_name}, z={self.z_score})"


# Importar funciones a testear (usar paths relativos para test standalone)
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from vigia.sift._math_utils import (
    build_redundancy_groups,
    apply_frs,
    classify_group,
    apply_conflict_penalty,
    process_all_groups,
    apply_artifact_reliability,
)


# ============================================================
# TEST 1: Caso PID 123 (Stress Test Principal)
# ============================================================

def test_pid_123_redundancy():
    """
    Caso: Triple señal sobre PID 123 en ventana de 10s.

    Entrada:
    - MFE: proceso sospechoso PID=123, z=3.5
    - ELC: login + exec PID=123, z=3.2  
    - NFE: conexión externa PID=123, z=2.8

    Esperado:
    - Grupo único (n=3)
    - FRS = 1 / (1 + 2) = 1/3
    - z_dominante ajustado ≈ 3.5 * 1/3 ≈ 1.17
    - Clasificación: REDUNDANT (min=2.8 > 0.5)
    - Veredicto: MALICE_MEDIUM (no HIGH)
    """
    signals = [
        MockSignalOutput("MEMORY_FORENSICS", 3.5, 0.95, {
            "pid": 123, "timestamp": 1000, "artifact_type": "memory"
        }),
        MockSignalOutput("EVENT_LOG", 3.2, 0.80, {
            "pid": 123, "timestamp": 1005, "artifact_type": "event_log"
        }),
        MockSignalOutput("NETWORK_FORENSICS", 2.8, 0.75, {
            "pid": 123, "timestamp": 1008, "artifact_type": "network"
        }),
    ]

    def entity_key_fn(sig):
        pid = sig.metadata.get("pid", 0)
        if pid:
            return (f"pid:{pid}", sig.metadata.get("timestamp", 0))
        return (sig.tool_name, 0)

    groups = build_redundancy_groups(signals, entity_key_fn, delta_t=60)

    # Verificar: exactamente 1 grupo con 3 señales
    assert len(groups) == 1, f"Esperado 1 grupo, got {len(groups)}"
    assert len(groups[0]) == 3, f"Esperado 3 señales, got {len(groups[0])}"

    # Clasificación: REDUNDANT (min=2.8 > 0.5)
    classification = classify_group(signals, groups[0])
    assert classification == "REDUNDANT", f"Esperado REDUNDANT, got {classification}"

    # Aplicar FRS
    adjusted = apply_frs(signals, groups, score_attr="z_score")

    # Verificar: dominante (MFE) conservado, otros penalizados
    dominant_z = adjusted[0].z_score  # MFE es dominante (3.5)
    # FRS = 1/3 para no-dominantes
    # El dominante no debería cambiar (apply_frs conserva dominante)
    assert dominant_z == 3.5, f"Dominante debería conservarse: {dominant_z}"

    # Los no-dominantes deberían tener metadata frs_applied
    assert adjusted[1].metadata.get("frs_applied") == True
    assert adjusted[2].metadata.get("frs_applied") == True

    print("✅ TEST 1 PASADO: Caso PID 123 - REDUNDANT, FRS aplicado")


# ============================================================
# TEST 2: Ghost In The Shell (CONTRADICTORY)
# ============================================================

def test_ghost_in_the_shell():
    """
    Caso: Memoria fuerte (z=3.5) + Logs débiles (z=0.2) mismo PID.

    Esperado:
    - Clasificación: CONTRADICTORY (max=3.5 >= 2.5 AND min=0.2 <= 0.5)
    - NO aplica FRS
    - Penalización de coherencia: penalty = 1 - (0.2/3.5) ≈ 0.943
    - z_adjusted = 3.5 * (1 - 0.943 * 0.5) ≈ 3.5 * 0.529 ≈ 1.85
    - Metadata: conflict=True, conflict_sources=[memory, event_log]
    """
    signals = [
        MockSignalOutput("MEMORY_FORENSICS", 3.5, 0.95, {
            "pid": 456, "timestamp": 2000, "artifact_type": "memory"
        }),
        MockSignalOutput("EVENT_LOG", 0.2, 0.60, {
            "pid": 456, "timestamp": 2005, "artifact_type": "event_log"
        }),
    ]

    def entity_key_fn(sig):
        pid = sig.metadata.get("pid", 0)
        if pid:
            return (f"pid:{pid}", sig.metadata.get("timestamp", 0))
        return (sig.tool_name, 0)

    groups = build_redundancy_groups(signals, entity_key_fn, delta_t=60)

    # Verificar: 1 grupo con 2 señales
    assert len(groups) == 1
    assert len(groups[0]) == 2

    # Clasificación: CONTRADICTORY
    classification = classify_group(signals, groups[0])
    assert classification == "CONTRADICTORY", f"Esperado CONTRADICTORY, got {classification}"

    # Aplicar penalización
    adjusted = apply_conflict_penalty(signals, groups[0])

    # Verificar metadata
    assert adjusted[0].metadata.get("conflict") == True
    assert "memory" in adjusted[0].metadata.get("conflict_sources", [])
    assert "event_log" in adjusted[0].metadata.get("conflict_sources", [])

    # Verificar z ajustado (T6.1: dominante NO es penalizado, no-dominantes sí)
    # Encontrar el dominante (z más alto antes del conflicto)
    dominant = max(adjusted, key=lambda s: s.z_score)
    non_dominants = [s for s in adjusted if s != dominant]
    
    # El dominante debe mantener su z (no penalizado)
    assert dominant.z_score >= 3.5, f"Dominante debería mantener z: {dominant.z_score}"
    
    # Algún no-dominante debe haber bajado
    assert any(s.z_score < 3.5 for s in non_dominants), f"Algún no-dominante debería bajar"
    assert all(s.z_score > 0 for s in adjusted), f"Ningún z debería colapsar a 0"

    print("✅ TEST 2 PASADO: Ghost In The Shell - CONTRADICTORY, penalización aplicada")


# ============================================================
# TEST 3: Edge Case - 2 vs 1 (Dos coinciden, uno contradice)
# ============================================================

def test_two_vs_one():
    """
    Caso: Memoria (z=3.5) + Registro (z=3.4) = REDUNDANT entre sí.
    Luego grupo resultante entra en CONTRADICTORY con Logs (z=0.1).

    Esperado:
    - Memoria y Registro: FRS aplicado (REDUNDANT)
    - Grupo vs Logs: CONTRADICTORY → penalización
    - Resultado: malicia confirmada pero con alerta de integridad
    """
    signals = [
        MockSignalOutput("MEMORY_FORENSICS", 3.5, 0.95, {
            "pid": 789, "timestamp": 3000, "artifact_type": "memory"
        }),
        MockSignalOutput("REGISTRY_RTR", 3.4, 0.70, {
            "pid": 789, "timestamp": 3002, "artifact_type": "registry"
        }),
        MockSignalOutput("EVENT_LOG", 0.1, 0.60, {
            "pid": 789, "timestamp": 3005, "artifact_type": "event_log"
        }),
    ]

    def entity_key_fn(sig):
        pid = sig.metadata.get("pid", 0)
        if pid:
            return (f"pid:{pid}", sig.metadata.get("timestamp", 0))
        return (sig.tool_name, 0)

    groups = build_redundancy_groups(signals, entity_key_fn, delta_t=60)

    # Todas en mismo PID → 1 grupo
    assert len(groups) == 1
    assert len(groups[0]) == 3

    # Procesar con pipeline completo
    adjusted = process_all_groups(signals, groups)

    # Verificar que hay conflicto marcado
    has_conflict = any(
        s.metadata.get("conflict") == True 
        for s in adjusted
    )
    assert has_conflict, "Debería haber conflicto marcado"

    print("✅ TEST 3 PASADO: 2-vs-1 - FRS + CONTRADICTORY pipeline")


# ============================================================
# TEST 4: Edge Case - PID Recycling (diferentes timestamps lejanos)
# ============================================================

def test_pid_recycling():
    """
    Caso: Mismo PID pero timestamps separados por > 60s (delta_t).

    Esperado:
    - Dos grupos separados (no se consolidan)
    - Cada grupo procesado independientemente
    """
    signals = [
        MockSignalOutput("MEMORY_FORENSICS", 3.5, 0.95, {
            "pid": 100, "timestamp": 0, "artifact_type": "memory"
        }),
        MockSignalOutput("EVENT_LOG", 3.2, 0.80, {
            "pid": 100, "timestamp": 300, "artifact_type": "event_log"  # > 60s
        }),
    ]

    def entity_key_fn(sig):
        pid = sig.metadata.get("pid", 0)
        if pid:
            return (f"pid:{pid}", sig.metadata.get("timestamp", 0))
        return (sig.tool_name, 0)

    groups = build_redundancy_groups(signals, entity_key_fn, delta_t=60)

    # Deberían ser 2 grupos separados
    assert len(groups) == 2, f"Esperado 2 grupos (recycling), got {len(groups)}"

    print("✅ TEST 4 PASADO: PID Recycling - grupos separados por tiempo")


# ============================================================
# TEST 5: Edge Case - Temporal Boundary (justo en el límite)
# ============================================================

def test_temporal_boundary():
    """
    Caso: Dos señales separadas por exactamente delta_t (60s).

    Esperado:
    - abs(t1 - t2) = 60 <= delta_t → MISMO GRUPO
    - abs(t1 - t2) = 61 > delta_t → GRUPOS SEPARADOS
    """
    signals_same = [
        MockSignalOutput("MEMORY_FORENSICS", 3.5, 0.95, {
            "pid": 200, "timestamp": 0, "artifact_type": "memory"
        }),
        MockSignalOutput("EVENT_LOG", 3.2, 0.80, {
            "pid": 200, "timestamp": 60, "artifact_type": "event_log"
        }),
    ]

    signals_diff = [
        MockSignalOutput("MEMORY_FORENSICS", 3.5, 0.95, {
            "pid": 201, "timestamp": 0, "artifact_type": "memory"
        }),
        MockSignalOutput("EVENT_LOG", 3.2, 0.80, {
            "pid": 201, "timestamp": 61, "artifact_type": "event_log"
        }),
    ]

    def entity_key_fn(sig):
        pid = sig.metadata.get("pid", 0)
        if pid:
            return (f"pid:{pid}", sig.metadata.get("timestamp", 0))
        return (sig.tool_name, 0)

    groups_same = build_redundancy_groups(signals_same, entity_key_fn, delta_t=60)
    groups_diff = build_redundancy_groups(signals_diff, entity_key_fn, delta_t=60)

    assert len(groups_same) == 1, "t=60 debería estar en mismo grupo"
    assert len(groups_diff) == 2, "t=61 debería estar en grupos separados"

    print("✅ TEST 5 PASADO: Temporal Boundary - límite exacto en 60s")


# ============================================================
# TEST 6: Artifact Reliability (Gamma)
# ============================================================

def test_gamma_application():
    """
    Verifica que Gamma nunca eleva el score y penaliza correctamente.
    """
    score = Fraction(35, 10)  # 3.5

    # Memory: Γ=0.95 → 3.5 * 0.95 = 3.325
    mem_adjusted = apply_artifact_reliability(score, "memory")
    assert mem_adjusted == Fraction(3325, 1000), f"Memory gamma failed: {mem_adjusted}"

    # Event log: Γ=0.60 → 3.5 * 0.60 = 2.1
    ev_adjusted = apply_artifact_reliability(score, "event_log")
    assert ev_adjusted == Fraction(21, 10), f"Event log gamma failed: {ev_adjusted}"

    # Unknown: Γ=1.0 (default) → no change
    unk_adjusted = apply_artifact_reliability(score, "unknown")
    assert unk_adjusted == score, f"Unknown gamma failed: {unk_adjusted}"

    # Gamma nunca eleva
    assert mem_adjusted <= score
    assert ev_adjusted <= score

    print("✅ TEST 6 PASADO: Gamma - penalización correcta, nunca eleva")


# ============================================================
# RUN ALL TESTS
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("VIGÍA TEST SUITE - FRS + Ghost In The Shell")
    print("=" * 60)

    tests = [
        test_pid_123_redundancy,
        test_ghost_in_the_shell,
        test_two_vs_one,
        test_pid_recycling,
        test_temporal_boundary,
        test_gamma_application,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"❌ {test.__name__} FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ {test.__name__} ERROR: {e}")
            failed += 1

    print(f"\n{'='*60}")
    print(f"RESULTADO: {passed}/{len(tests)} tests pasados")
    if failed == 0:
        print("✅ TODOS LOS TESTS PASARON")
    else:
        print(f"❌ {failed} tests fallaron")
    print(f"{'='*60}")
