"""
vigia/tests/test_conflict_dominance_stability.py

TANDA 6.1 — Hardening mínimo post-auditoría Kimi
Fecha: 2026-05-07

Test de "Conflict Dominance Stability":
Invariante: si source A tiene z_A > z_B Y gamma_A > gamma_B,
entonces z_final_A >= z_final_B después de apply_conflict_penalty.

Si falla, hay un bug conceptual en el ConflictResolver.
"""
from __future__ import annotations

from fractions import Fraction
from typing import Dict, Any


class MockSignal:
    """Mock mínimo de SignalOutput para tests standalone."""
    def __init__(self, tool_name: str, z_score: float, artifact_type: str):
        self.tool_name = tool_name
        self.z_score = z_score
        self.confidence = 0.9
        self.metadata: Dict[str, Any] = {"artifact_type": artifact_type}
        self.value = z_score / 5.0

    def __repr__(self) -> str:
        return f"MockSignal({self.tool_name}, z={self.z_score})"


# Importar la función a testear
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "sift"))
from _math_utils import apply_conflict_penalty


def _run_conflict(
    z_a: float, art_a: str,
    z_b: float, art_b: str,
) -> tuple[float, float]:
    """
    Aplica apply_conflict_penalty a dos señales y retorna (z_final_A, z_final_B).
    A siempre es el índice 0, B el índice 1.
    """
    signals = [
        MockSignal("SOURCE_A", z_a, art_a),
        MockSignal("SOURCE_B", z_b, art_b),
    ]
    adjusted = apply_conflict_penalty(signals, [0, 1], score_attr="z_score",
                                      use_gamma=True, use_resistance=True)
    return adjusted[0].z_score, adjusted[1].z_score


class TestConflictDominanceStability:
    """
    Invariante central:
    Si z_A > z_B y gamma_A > gamma_B,
    entonces z_final_A >= z_final_B después del penalty.
    """

    def _assert_dominance(
        self,
        z_a: float, art_a: str,
        z_b: float, art_b: str,
        label: str,
    ) -> None:
        """
        Aplica conflict penalty y verifica dominancia.
        Falla con mensaje explícito si se invierte.
        """
        z_fa, z_fb = _run_conflict(z_a, art_a, z_b, art_b)
        assert z_fa >= z_fb, (
            f"Inversión semántica detectada: source con mayor z y mayor gamma "
            f"terminó con score inferior. "
            f"Caso: {label}. "
            f"Entrada: z_A={z_a} ({art_a}), z_B={z_b} ({art_b}). "
            f"Salida: z_final_A={z_fa}, z_final_B={z_fb}."
        )

    # ------------------------------------------------------------------
    # Casos requeridos por Kimi T6.1
    # ------------------------------------------------------------------

    def test_caso_1_memoria_vs_log(self):
        """
        # T6.1 START
        Caso 1: z=3.5 gamma=0.95 (memory) vs z=2.4 gamma=0.60 (event_log)
        Esperado: memory sigue dominando post-penalty.
        """
        self._assert_dominance(
            z_a=3.5, art_a="memory",
            z_b=2.4, art_b="event_log",
            label="Caso 1: memory(3.5,γ=0.95) vs event_log(2.4,γ=0.60)",
        )
        # T6.1 END

    def test_caso_2_memoria_vs_registry(self):
        """
        # T6.1 START
        Caso 2: z=2.5 gamma=0.95 (memory) vs z=2.4 gamma=0.70 (registry)
        Esperado: memory sigue dominando (margen pequeño pero debe mantenerse).
        """
        self._assert_dominance(
            z_a=2.5, art_a="memory",
            z_b=2.4, art_b="registry",
            label="Caso 2: memory(2.5,γ=0.95) vs registry(2.4,γ=0.70)",
        )
        # T6.1 END

    def test_caso_3_margen_minimo(self):
        """
        # T6.1 START
        Caso 3: z=1.0 gamma=0.95 (memory) vs z=0.9 gamma=0.60 (event_log)
        Esperado: memory sigue dominando con margen mínimo.
        """
        self._assert_dominance(
            z_a=1.0, art_a="memory",
            z_b=0.9, art_b="event_log",
            label="Caso 3: memory(1.0,γ=0.95) vs event_log(0.9,γ=0.60)",
        )
        # T6.1 END

    # ------------------------------------------------------------------
    # Casos adicionales: variaciones de fuentes
    # ------------------------------------------------------------------

    def test_mft_vs_network(self):
        """memory(γ=0.95) no existe aquí — mft(γ=0.80) vs network(γ=0.75)."""
        self._assert_dominance(
            z_a=3.2, art_a="mft",
            z_b=2.8, art_b="network",
            label="mft(3.2,γ=0.80) vs network(2.8,γ=0.75)",
        )

    def test_registry_vs_event_log(self):
        """registry(γ=0.70) vs event_log(γ=0.60)."""
        self._assert_dominance(
            z_a=2.8, art_a="registry",
            z_b=2.0, art_b="event_log",
            label="registry(2.8,γ=0.70) vs event_log(2.0,γ=0.60)",
        )

    def test_igual_z_diferente_gamma(self):
        """
        Caso edge: z iguales pero gamma distintos.
        El de mayor gamma (memory) debe quedar >= al otro.
        """
        z_fa, z_fb = _run_conflict(2.5, "memory", 2.5, "event_log")
        assert z_fa >= z_fb, (
            f"Con z iguales, memory(γ=0.95) debería quedar >= event_log(γ=0.60). "
            f"Salida: z_final_A={z_fa}, z_final_B={z_fb}."
        )

    def test_weighted_max_zero_no_crash(self):
        """
        Caso edge: z=0 en ambas fuentes.
        No debe crashear. penalty=0, z_final=0.
        """
        z_fa, z_fb = _run_conflict(0.0, "memory", 0.0, "event_log")
        assert z_fa >= 0.0
        assert z_fb >= 0.0

    def test_penalty_clamped_to_one(self):
        """
        Verificar que penalty nunca supera 1.0.
        Caso extremo: z_B muy bajo vs z_A muy alto.
        """
        z_fa, z_fb = _run_conflict(3.5, "memory", 0.01, "event_log")
        # z_final debe ser >= 0
        assert z_fa >= 0.0, f"z_final_A negativo: {z_fa}"
        assert z_fb >= 0.0, f"z_final_B negativo: {z_fb}"
        # Dominancia preservada
        assert z_fa >= z_fb, (
            f"Dominancia perdida en caso extremo: z_fa={z_fa}, z_fb={z_fb}"
        )


if __name__ == "__main__":
    import unittest

    suite = unittest.TestLoader().loadTestsFromTestCase(TestConflictDominanceStability)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    if result.wasSuccessful():
        print("\n✅ TODOS LOS TESTS DE DOMINANCE STABILITY PASARON")
    else:
        print(f"\n❌ {len(result.failures) + len(result.errors)} tests fallaron")
