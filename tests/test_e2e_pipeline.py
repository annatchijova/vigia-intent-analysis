"""
vigia/tests/test_e2e_pipeline.py

Test end-to-end del pipeline completo VIGÍA.
Simula un caso real con múltiples artefactos y valida todo el flujo.

Escenario: Operación "Tres Espejos"
- Memoria: proceso inyectado PID=1234
- Registry: persistencia via Run key
- EventLog: log borrado después del ataque
- Network: beaconing a IP C2
"""

from __future__ import annotations
from fractions import Fraction
import sys
sys.path.insert(0, '/mnt/agents/output')

from _math_utils import (
    apply_artifact_reliability,
    build_redundancy_groups,
    classify_group,
    apply_conflict_penalty,
    process_all_groups,
    noisy_or_correlated,
)

class MockSignalOutput:
    """Mock de SignalOutput para testing."""
    def __init__(self, tool_name, z_score, confidence, metadata):
        self.tool_name = tool_name
        self.z_score = z_score
        self.confidence = confidence
        self.metadata = metadata
        self.value = z_score / 5.0

    def __repr__(self):
        return f"MockSignalOutput({self.tool_name}, z={self.z_score})"


def test_e2e_tres_espejos():
    """
    Caso real: Operación Tres Espejos

    Timeline:
    T+0s:  Memory - proceso inyectado PID=1234 (z=3.5)
    T+2s:  Registry - Run key creada (z=2.8)
    T+5s:  EventLog - log borrado ID 1102 (z=3.8)
    T+10s: Network - beaconing a 192.168.1.100 (z=2.5)

    Esperado:
    - Grupos: 2 grupos (PID=1234: Memory+Registry+EventLog, IP=192.168.1.100: Network sola)
    - Clasificación: REDUNDANT (todos convergen, min=1.96 > 0.5)
    - FRS: dominante conservado, no-dominantes penalizados
    - Gamma: aplicado a todas
    """
    print("=" * 60)
    print("TEST E2E: Operación Tres Espejos")
    print("=" * 60)

    # Señales crudas del caso
    signals = [
        MockSignalOutput("MEMORY_FORENSICS", 3.5, 0.95, {
            "pid": 1234, "timestamp": 0, "artifact_type": "memory",
            "finding_types": ["malfind_pe_injection"]
        }),
        MockSignalOutput("REGISTRY_RTR", 2.8, 0.70, {
            "pid": 1234, "timestamp": 2, "artifact_type": "registry",
            "finding_types": ["run_key"]
        }),
        MockSignalOutput("EVENT_LOG", 3.8, 0.60, {
            "pid": 1234, "timestamp": 5, "artifact_type": "event_log",
            "finding_types": ["LOG_WIPE_AFTER_ATTACK"]
        }),
        MockSignalOutput("NETWORK_FORENSICS", 2.5, 0.75, {
            "dst_ip": "192.168.1.100", "timestamp": 10, "artifact_type": "network",
            "finding_types": ["BEACONING"]
        }),
    ]

    print("\n--- Paso 1: Señales crudas ---")
    for sig in signals:
        print(f"  {sig.tool_name}: z={sig.z_score}, Γ={sig.metadata['artifact_type']}")

    # Paso 1: Gamma
    print("\n--- Paso 2: Aplicar Gamma ---")
    gamma_signals = []
    for sig in signals:
        z_frac = Fraction(int(round(sig.z_score * 100)), 100)
        z_adj = apply_artifact_reliability(z_frac, sig.metadata["artifact_type"])
        sig.z_score = float(z_adj)
        sig.metadata["gamma_applied"] = True
        gamma_signals.append(sig)
        print(f"  {sig.tool_name}: {sig.z_score} (Γ={sig.metadata['artifact_type']})")

    # Paso 2: Redundancy groups
    print("\n--- Paso 3: Redundancy Groups ---")
    def entity_key_fn(sig):
        pid = sig.metadata.get("pid", 0)
        if pid:
            return (f"pid:{pid}", sig.metadata.get("timestamp", 0))
        ip = sig.metadata.get("dst_ip", "")
        if ip:
            return (f"ip:{ip}", sig.metadata.get("timestamp", 0))
        return (sig.tool_name, sig.metadata.get("timestamp", 0))

    groups = build_redundancy_groups(gamma_signals, entity_key_fn, delta_t=60)
    print(f"  Grupos: {len(groups)}")
    for i, g in enumerate(groups):
        tools = [gamma_signals[idx].tool_name for idx in g]
        print(f"    Grupo {i}: {g} → {tools}")

    # Validar grupos
    assert len(groups) == 2, f"Esperado 2 grupos, got {len(groups)}"

    # Paso 3: Clasificación
    print("\n--- Paso 4: Clasificación ---")
    for i, group in enumerate(groups):
        cls = classify_group(gamma_signals, group)
        tools = [gamma_signals[idx].tool_name for idx in group]
        print(f"  Grupo {i} ({tools}): {cls}")

    # Paso 4: Pipeline completo
    print("\n--- Paso 5: Pipeline process_all_groups ---")
    final_signals = process_all_groups(gamma_signals, groups)

    print("\n--- Resultados finales ---")
    for sig in final_signals:
        print(f"  {sig.tool_name}:")
        print(f"    z_score: {sig.z_score}")
        if sig.metadata.get("frs_applied"):
            print(f"    FRS: factor={sig.metadata.get('frs_factor')}")
        if sig.metadata.get("conflict"):
            print(f"    CONFLICT: z_before={sig.metadata.get('z_before_conflict')}")
            print(f"             z_after={sig.metadata.get('z_after_conflict')}")
            print(f"             penalty={sig.metadata.get('conflict_penalty')}")

    # Validaciones finales
    print("\n--- Validaciones ---")

    # 1. Dominante (MEMORY, z=3.325) NO debería tener FRS (se conserva)
    mem_sig = next(s for s in final_signals if s.tool_name == "MEMORY_FORENSICS")
    assert mem_sig.metadata.get("frs_applied") != True, "Memory dominante NO debería tener FRS"
    assert mem_sig.z_score == 3.325, f"Memory dominante debería conservar z: {mem_sig.z_score}"
    print("✅ Memory: Dominante conservado (sin FRS)")

    # 2. No-dominantes (Registry, EventLog) DEBEN tener FRS
    reg_sig = next(s for s in final_signals if s.tool_name == "REGISTRY_RTR")
    ev_sig = next(s for s in final_signals if s.tool_name == "EVENT_LOG")
    assert reg_sig.metadata.get("frs_applied") == True, "Registry debería tener FRS"
    assert ev_sig.metadata.get("frs_applied") == True, "EventLog debería tener FRS"
    print("✅ Registry & EventLog: FRS aplicado (no-dominantes)")

    # 3. Network NO debería tener FRS (grupo solitario)
    net_sig = next(s for s in final_signals if s.tool_name == "NETWORK_FORENSICS")
    assert net_sig.metadata.get("frs_applied") != True, "Network no debería tener FRS (grupo solitario)"
    print("✅ Network: Sin FRS (grupo solitario)")

    # 4. Todos deberían tener gamma_applied
    for sig in final_signals:
        assert sig.metadata.get("gamma_applied") == True, f"{sig.tool_name} debería tener gamma"
    print("✅ Todos: Gamma aplicado")

    # 5. Registry z debería bajar por FRS (1.96 * 1/3 ≈ 0.65)
    assert reg_sig.z_score < 1.0, f"Registry z debería bajar por FRS: {reg_sig.z_score}"
    print(f"✅ Registry z ajustado: {reg_sig.z_score} < 1.0")

    # 6. EventLog z debería bajar por FRS (2.28 * 1/3 ≈ 0.76)
    assert ev_sig.z_score < 1.0, f"EventLog z debería bajar por FRS: {ev_sig.z_score}"
    print(f"✅ EventLog z ajustado: {ev_sig.z_score} < 1.0")

    print("\n" + "=" * 60)
    print("✅ TEST E2E PASADO: Operación Tres Espejos")
    print("=" * 60)


def test_e2e_empty_case():
    """Caso vacío: sin señales."""
    signals = []
    groups = build_redundancy_groups(signals, lambda s: ("", 0), delta_t=60)
    assert len(groups) == 0
    final = process_all_groups(signals, groups)
    assert len(final) == 0
    print("✅ TEST E2E: Caso vacío pasado")


def test_e2e_single_signal():
    """Caso con una sola señal."""
    signals = [MockSignalOutput("MEMORY_FORENSICS", 3.5, 0.95, {
        "pid": 1, "timestamp": 0, "artifact_type": "memory"
    })]
    groups = build_redundancy_groups(signals, lambda s: (f"pid:{s.metadata.get('pid',0)}", 0), delta_t=60)
    assert len(groups) == 1
    assert len(groups[0]) == 1
    final = process_all_groups(signals, groups)
    assert len(final) == 1
    # Grupo de 1 elemento: no hay FRS ni conflicto
    assert final[0].metadata.get("frs_applied") != True
    assert final[0].metadata.get("conflict") != True
    print("✅ TEST E2E: Caso single signal pasado")


if __name__ == "__main__":
    test_e2e_tres_espejos()
    test_e2e_empty_case()
    test_e2e_single_signal()
    print("\n" + "=" * 60)
    print("✅ TODOS LOS TESTS E2E PASADOS (3/3)")
    print("=" * 60)
