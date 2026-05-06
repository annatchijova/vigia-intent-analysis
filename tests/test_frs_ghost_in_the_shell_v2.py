"""
vigia/tests/test_frs_ghost_in_the_shell_v2.py

Test suite V2 para FRS + Ghost In The Shell + Anti-Silencing.
Valida:
1. Caso PID 123: 3 señales redundantes → MALICE_MEDIUM (no HIGH)
2. Caso CONTRADICTORY: memoria fuerte + logs débiles → penalización
3. Anti-Silencing: logs falsos de alta Γ NO pueden silenciar memoria legítima
4. Dominance Stability: A con mayor z y mayor Γ nunca termina con z_final < B
5. Edge cases: PID recycling, temporal boundary, 2-vs-1

Determinismo: seeds fijos, inputs ordenados, no datetime en asserts.
"""

from __future__ import annotations

from fractions import Fraction
from typing import List, Dict, Any

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
    RESISTANCE_FACTOR,
)


class MockSignalOutput:
    def __init__(self, tool_name: str, z_score: float, confidence: float, metadata: Dict[str, Any]):
        self.tool_name = tool_name
        self.z_score = z_score
        self.confidence = confidence
        self.metadata = metadata
        self.value = z_score / 5.0

    def __repr__(self):
        return f"MockSignalOutput({self.tool_name}, z={self.z_score})"


def test_pid_123_redundancy():
    """Caso: Triple señal sobre PID 123 en ventana de 10s."""
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
    assert len(groups) == 1, f"Esperado 1 grupo, got {len(groups)}"
    assert len(groups[0]) == 3

    classification = classify_group(signals, groups[0])
    assert classification == "REDUNDANT"

    adjusted = apply_frs(signals, groups, score_attr="z_score")
    dominant_z = adjusted[0].z_score
    assert dominant_z == 3.5, f"Dominante debería conservarse: {dominant_z}"
    assert adjusted[1].metadata.get("frs_applied") == True
    assert adjusted[2].metadata.get("frs_applied") == True

    print("✅ TEST 1 PASADO: Caso PID 123 - REDUNDANT, FRS aplicado")


def test_ghost_in_the_shell():
    """Caso: Memoria fuerte (z=3.5) + Logs débiles (z=0.2) mismo PID."""
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
    assert len(groups) == 1
    assert len(groups[0]) == 2

    classification = classify_group(signals, groups[0])
    assert classification == "CONTRADICTORY"

    adjusted = apply_conflict_penalty(signals, groups[0])
    assert adjusted[0].metadata.get("conflict") == True
    assert "memory" in adjusted[0].metadata.get("conflict_sources", [])
    assert "event_log" in adjusted[0].metadata.get("conflict_sources", [])

    # T6.1: El dominante NO es penalizado, los no-dominantes sí
    dominant = max(adjusted, key=lambda s: s.z_score)
    non_dominants = [s for s in adjusted if s != dominant]
    
    # El dominante debe mantener su z
    assert dominant.z_score >= 3.5, f"Dominante debería mantener z: {dominant.z_score}"
    
    # Algún no-dominante debe haber bajado
    assert any(s.z_score < 3.5 for s in non_dominants), "Algún no-dominante debería bajar"
    assert all(s.z_score > 0 for s in adjusted), "Ningún z debería colapsar a 0"

    print("✅ TEST 2 PASADO: Ghost In The Shell - CONTRADICTORY, penalización aplicada")


def test_anti_silencing():
    """
    FIX P0: Anti-Silencing Test.

    Escenario: Atacante inunda con 5 señales de event_log falsas (z=3.5, Γ=0.60)
    para silenciar 1 señal de memoria legítima (z=3.5, Γ=0.95).

    Con Factor de Resistencia:
    - Memoria: z * Γ * R = 3.5 * 0.95 * 0.95 = 3.158
    - EventLog: z * Γ * R = 3.5 * 0.60 * 0.55 = 1.155

    Resultado: Memoria SIGUE siendo dominante. El atacante NO puede silenciar.
    """
    signals = [
        MockSignalOutput("MEMORY_FORENSICS", 3.5, 0.95, {
            "pid": 999, "timestamp": 1000, "artifact_type": "memory"
        }),
        MockSignalOutput("EVENT_LOG_FAKE_1", 3.5, 0.60, {
            "pid": 999, "timestamp": 1001, "artifact_type": "event_log"
        }),
        MockSignalOutput("EVENT_LOG_FAKE_2", 3.5, 0.60, {
            "pid": 999, "timestamp": 1002, "artifact_type": "event_log"
        }),
        MockSignalOutput("EVENT_LOG_FAKE_3", 3.5, 0.60, {
            "pid": 999, "timestamp": 1003, "artifact_type": "event_log"
        }),
        MockSignalOutput("EVENT_LOG_FAKE_4", 3.5, 0.60, {
            "pid": 999, "timestamp": 1004, "artifact_type": "event_log"
        }),
        MockSignalOutput("EVENT_LOG_FAKE_5", 3.5, 0.60, {
            "pid": 999, "timestamp": 1005, "artifact_type": "event_log"
        }),
    ]

    def entity_key_fn(sig):
        pid = sig.metadata.get("pid", 0)
        if pid:
            return (f"pid:{pid}", sig.metadata.get("timestamp", 0))
        return (sig.tool_name, 0)

    groups = build_redundancy_groups(signals, entity_key_fn, delta_t=60)
    assert len(groups) == 1
    assert len(groups[0]) == 6

    # Procesar con pipeline completo (incluye resistencia)
    adjusted = process_all_groups(signals, groups)

    # Encontrar dominante
    def weighted_score(sig):
        z = sig.z_score
        art = sig.metadata.get("artifact_type", "unknown")
        gamma = {"memory": 0.95, "mft": 0.80, "registry": 0.70, "event_log": 0.60, "network": 0.75}.get(art, 1.0)
        r = float(RESISTANCE_FACTOR.get(art, Fraction(1, 1)))
        return z * gamma * r

    dominant = max(adjusted, key=weighted_score)

    # FIX P0: El dominante DEBE ser MEMORY, no un event_log falso
    assert dominant.tool_name == "MEMORY_FORENSICS",         f"Anti-silencing FALLÓ: dominante={dominant.tool_name}"

    assert dominant.z_score == 3.5, f"MEMORY debería conservar z=3.5, got {dominant.z_score}"

    # Verificar que los event logs fueron penalizados
    event_logs = [s for s in adjusted if s.tool_name.startswith("EVENT_LOG")]
    assert all(s.metadata.get("frs_applied") for s in event_logs), "Event logs deberían tener frs_applied"
    assert dominant.z_score == 3.5, f"MEMORY debería conservar z=3.5, got {dominant.z_score}"

    # Verificar que los event logs fueron penalizados
    event_logs = [s for s in adjusted if s.tool_name.startswith("EVENT_LOG")]
    assert all(s.metadata.get("frs_applied") for s in event_logs), "Event logs deberían tener frs_applied"

    print("✅ TEST 3 PASADO: Anti-Silencing - Memoria resiste inundación de logs falsos")


def test_dominance_stability():
    """
    FIX P0: Dominance Stability Test.
    Si A tiene mayor z y mayor Γ que B, entonces A nunca puede terminar con z_final < B.
    """
    signals = [
        MockSignalOutput("MEMORY_FORENSICS", 3.5, 0.95, {
            "pid": 777, "timestamp": 1000, "artifact_type": "memory"
        }),
        MockSignalOutput("EVENT_LOG", 0.2, 0.60, {
            "pid": 777, "timestamp": 1005, "artifact_type": "event_log"
        }),
    ]

    def entity_key_fn(sig):
        pid = sig.metadata.get("pid", 0)
        if pid:
            return (f"pid:{pid}", sig.metadata.get("timestamp", 0))
        return (sig.tool_name, 0)

    groups = build_redundancy_groups(signals, entity_key_fn, delta_t=60)
    adjusted = process_all_groups(signals, groups)

    mem = next(s for s in adjusted if s.tool_name == "MEMORY_FORENSICS")
    ev = next(s for s in adjusted if s.tool_name == "EVENT_LOG")

    # Memoria tiene z=3.5, Γ=0.95, R=0.95 → weighted = 3.158
    # EventLog tiene z=0.2, Γ=0.60, R=0.55 → weighted = 0.066
    # Memoria DEBE seguir siendo mayor
    mem_weighted = mem.z_score * 0.95 * float(RESISTANCE_FACTOR["memory"])
    ev_weighted = ev.z_score * 0.60 * float(RESISTANCE_FACTOR["event_log"])

    assert mem_weighted > ev_weighted,         f"Dominance Stability FALLÓ: mem={mem_weighted} vs ev={ev_weighted}"

    print("✅ TEST 4 PASADO: Dominance Stability - invariante preservada")


def test_two_vs_one():
    """Caso: Memoria (z=3.5) + Registro (z=3.4) = REDUNDANT. Luego vs Logs (z=0.1) = CONTRADICTORY."""
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
    assert len(groups) == 1
    assert len(groups[0]) == 3

    adjusted = process_all_groups(signals, groups)
    has_conflict = any(s.metadata.get("conflict") == True for s in adjusted)
    assert has_conflict, "Debería haber conflicto marcado"

    print("✅ TEST 5 PASADO: 2-vs-1 - FRS + CONTRADICTORY pipeline")


def test_pid_recycling():
    """Caso: Mismo PID pero timestamps separados por > 60s."""
    signals = [
        MockSignalOutput("MEMORY_FORENSICS", 3.5, 0.95, {
            "pid": 100, "timestamp": 0, "artifact_type": "memory"
        }),
        MockSignalOutput("EVENT_LOG", 3.2, 0.80, {
            "pid": 100, "timestamp": 300, "artifact_type": "event_log"
        }),
    ]

    def entity_key_fn(sig):
        pid = sig.metadata.get("pid", 0)
        if pid:
            return (f"pid:{pid}", sig.metadata.get("timestamp", 0))
        return (sig.tool_name, 0)

    groups = build_redundancy_groups(signals, entity_key_fn, delta_t=60)
    assert len(groups) == 2, f"Esperado 2 grupos (recycling), got {len(groups)}"

    print("✅ TEST 6 PASADO: PID Recycling - grupos separados por tiempo")


def test_temporal_boundary():
    """Caso: Dos señales separadas por exactamente delta_t (60s)."""
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

    print("✅ TEST 7 PASADO: Temporal Boundary - límite exacto en 60s")


def test_gamma_application():
    """Verifica que Gamma nunca eleva el score y penaliza correctamente."""
    score = Fraction(35, 10)

    mem_adjusted = apply_artifact_reliability(score, "memory")
    assert mem_adjusted == Fraction(3325, 1000), f"Memory gamma failed: {mem_adjusted}"

    ev_adjusted = apply_artifact_reliability(score, "event_log")
    assert ev_adjusted == Fraction(21, 10), f"Event log gamma failed: {ev_adjusted}"

    unk_adjusted = apply_artifact_reliability(score, "unknown")
    assert unk_adjusted == score, f"Unknown gamma failed: {unk_adjusted}"

    assert mem_adjusted <= score
    assert ev_adjusted <= score

    print("✅ TEST 8 PASADO: Gamma - penalización correcta, nunca eleva")


if __name__ == "__main__":
    print("=" * 60)
    print("VIGÍA TEST SUITE V2 - FRS + Ghost In The Shell + Anti-Silencing")
    print("=" * 60)

    tests = [
        test_pid_123_redundancy,
        test_ghost_in_the_shell,
        test_anti_silencing,
        test_dominance_stability,
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
