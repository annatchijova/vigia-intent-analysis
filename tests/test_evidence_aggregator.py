#!/usr/bin/env python3
"""
tests/test_evidence_aggregator.py

Tests de invariantes matemáticos para el Evidence Aggregator (DEA v1).

Invariantes verificadas:
  - Identidad: si S=0 y Q=0, MI_final == B (base)
  - Monotonicidad: añadir synergy o sequence solo puede subir el MI
  - Cota superior: MI_final <= 9/10 (clamp)
  - Cota inferior: MI_final >= 0
  - Caso cero: B=0, S=0, Q=0 → MI_final = 0
  - Critical override: ECO_SEMIOTIC_COLLISION fuerza CRITICAL sin importar MI

Autor: Colectivo VIGÍA (diseño ChatGPT/DeepSeek, implementación Claude)
Versión: 2.3
"""

import sys
import unittest
from fractions import Fraction
from pathlib import Path

# Asegurar que el root del proyecto esté en el path
sys.path.insert(0, str(Path(__file__).parent.parent))

from vigia.core.evidence_aggregator import EvidenceAggregator, aggregate_evidence


def _make_detector_output(
    mi_num: int, mi_den: int,
    synergy_rules: list = None,
    sequence_rules: list = None,
    critical_patterns: list = None,
) -> dict:
    """Helper para construir detector output con el schema correcto."""
    return {
        "fsv": {
            "manipulation_index": {"num": mi_num, "den": mi_den},
            "total_patterns": 1,
            "dominant_category": "TEST",
            "peirce_layers_present": ["FIRSTNESS"],
            "critical_patterns": critical_patterns or [],
        },
        "synergy": {
            "triggered_rules": synergy_rules or [],
        },
        "sequences": {
            "triggered_rules": sequence_rules or [],
        },
        "critical_patterns": critical_patterns or [],
    }


class TestEvidenceAggregatorInvariants(unittest.TestCase):
    """Invariantes matemáticas de la DEA v1."""

    def setUp(self):
        self.agg = EvidenceAggregator()

    def _mi(self, output: dict) -> Fraction:
        mi = output.get("mi_final", output.get("manipulation_index", {}))
        return Fraction(mi["num"], mi["den"])

    # ── Identidad ─────────────────────────────────────────────────────────

    def test_identity_no_synergy_no_sequence(self):
        """Sin synergy ni sequence, MI_final == MI_base."""
        det = _make_detector_output(1, 5)  # B = 1/5
        out = aggregate_evidence(det)
        mi = self._mi(out)
        self.assertEqual(mi, Fraction(1, 5),
                         f"Identidad fallida: esperado 1/5, got {mi}")

    def test_identity_zero_base(self):
        """B=0 sin señales → MI_final = 0."""
        det = _make_detector_output(0, 1)
        out = aggregate_evidence(det)
        mi = self._mi(out)
        self.assertEqual(mi, Fraction(0, 1),
                         f"Caso cero fallido: esperado 0, got {mi}")

    # ── Monotonicidad ─────────────────────────────────────────────────────

    def test_monotonicity_synergy_increases_mi(self):
        """Añadir synergy con impacto > 0 aumenta MI."""
        det_base = _make_detector_output(1, 5)
        det_syn = _make_detector_output(1, 5, synergy_rules=[
            {"impact_num": 10, "impact_den": 100}
        ])
        mi_base = self._mi(aggregate_evidence(det_base))
        mi_syn = self._mi(aggregate_evidence(det_syn))
        self.assertGreater(mi_syn, mi_base,
                           f"Monotonicidad synergy fallida: {mi_base} >= {mi_syn}")

    def test_monotonicity_sequence_increases_mi(self):
        """Añadir sequence con bonus > 0 aumenta MI."""
        det_base = _make_detector_output(1, 5)
        det_seq = _make_detector_output(1, 5, sequence_rules=[
            {"bonus_num": 10, "bonus_den": 100}
        ])
        mi_base = self._mi(aggregate_evidence(det_base))
        mi_seq = self._mi(aggregate_evidence(det_seq))
        self.assertGreater(mi_seq, mi_base,
                           f"Monotonicidad sequence fallida: {mi_base} >= {mi_seq}")

    def test_monotonicity_both_increases_more(self):
        """Synergy + sequence juntos aumentan más que cada uno solo."""
        det_syn = _make_detector_output(1, 5, synergy_rules=[
            {"impact_num": 10, "impact_den": 100}
        ])
        det_seq = _make_detector_output(1, 5, sequence_rules=[
            {"bonus_num": 10, "bonus_den": 100}
        ])
        det_both = _make_detector_output(1, 5,
            synergy_rules=[{"impact_num": 10, "impact_den": 100}],
            sequence_rules=[{"bonus_num": 10, "bonus_den": 100}],
        )
        mi_syn = self._mi(aggregate_evidence(det_syn))
        mi_seq = self._mi(aggregate_evidence(det_seq))
        mi_both = self._mi(aggregate_evidence(det_both))
        self.assertGreater(mi_both, mi_syn)
        self.assertGreater(mi_both, mi_seq)

    # ── Cotas ─────────────────────────────────────────────────────────────

    def test_upper_bound_clamp_nine_tenths(self):
        """MI_final no puede superar 9/10 (clamp Daubert)."""
        det = _make_detector_output(9, 10, synergy_rules=[
            {"impact_num": 90, "impact_den": 100},
            {"impact_num": 90, "impact_den": 100},
        ])
        out = aggregate_evidence(det)
        mi = self._mi(out)
        self.assertLessEqual(mi, Fraction(9, 10),
                             f"Clamp superior violado: {mi} > 9/10")

    def test_lower_bound_zero(self):
        """MI_final no puede ser negativo."""
        det = _make_detector_output(0, 1)
        out = aggregate_evidence(det)
        mi = self._mi(out)
        self.assertGreaterEqual(mi, Fraction(0, 1),
                                f"Cota inferior violada: {mi} < 0")

    # ── No double-counting ────────────────────────────────────────────────

    def test_complement_product_no_double_count(self):
        """
        Verificar que M < B + αS + αQ (no suma lineal inflada).
        La composición complement-product es siempre más conservadora
        que la suma simple para valores en (0,1).
        """
        B = Fraction(2, 5)   # 0.4
        S = Fraction(3, 10)  # 0.3
        Q = Fraction(2, 10)  # 0.2
        alpha = Fraction(1, 2)

        # Suma lineal (inflada)
        naive_sum = B + alpha * S + alpha * Q

        # Composición DEA v1
        one = Fraction(1)
        dea = one - (one - B) * (one - alpha * S) * (one - alpha * Q)

        self.assertLess(dea, naive_sum,
                        f"DEA debería ser más conservadora que suma lineal: {dea} >= {naive_sum}")

    # ── Schema de output ──────────────────────────────────────────────────

    def test_output_contains_mi_final(self):
        """Output debe contener 'mi_final' con num/den (contrato DEA v1)."""
        det = _make_detector_output(1, 4)
        out = aggregate_evidence(det)
        self.assertIn("mi_final", out, "Falta 'mi_final' en output")
        self.assertIn("num", out["mi_final"], "Falta 'num' en mi_final")
        self.assertIn("den", out["mi_final"], "Falta 'den' en mi_final")

    def test_output_components_present(self):
        """Output debe contener 'components' con base, synergy, sequence."""
        det = _make_detector_output(1, 4)
        out = aggregate_evidence(det)
        self.assertIn("components", out, "Falta 'components'")
        comp = out["components"]
        for key in ("base", "synergy", "sequence"):
            self.assertIn(key, comp, f"Falta components.{key}")

    def test_no_floats_in_mi_final(self):
        """mi_final debe contener solo enteros (invariante I7)."""
        det = _make_detector_output(3, 7)
        out = aggregate_evidence(det)
        num = out["mi_final"]["num"]
        den = out["mi_final"]["den"]
        self.assertIsInstance(num, int, f"mi_final.num no es int: {type(num)}")
        self.assertIsInstance(den, int, f"mi_final.den no es int: {type(den)}")

    def test_determinism_same_input_same_output(self):
        """Mismo input → mismo output (invariante I2)."""
        import json
        det = _make_detector_output(2, 7, synergy_rules=[
            {"impact_num": 5, "impact_den": 100}
        ])
        out1 = aggregate_evidence(det)
        out2 = aggregate_evidence(det)
        s1 = json.dumps(out1, sort_keys=True, ensure_ascii=True)
        s2 = json.dumps(out2, sort_keys=True, ensure_ascii=True)
        self.assertEqual(s1, s2, "Determinismo violado: outputs distintos para mismo input")


class TestPipelineIntegration(unittest.TestCase):
    """Tests de integración detection → aggregation → decision."""

    def test_basic_flow(self):
        """Pipeline básico sin errores."""
        try:
            from vigia.core.decision_layer import decide
        except ImportError:
            self.skipTest("decision_layer no disponible")

        det = _make_detector_output(1, 5)
        from vigia.core.evidence_aggregator import aggregate_evidence
        agg = aggregate_evidence(det)
        decision = decide(det, agg)

        self.assertIn("alert_level", decision)
        self.assertIn("mi_final", decision)

    def test_critical_override_eco_semiotic_collision(self):
        """ECO_SEMIOTIC_COLLISION fuerza CRITICAL sin importar MI."""
        try:
            from vigia.core.decision_layer import decide
        except ImportError:
            self.skipTest("decision_layer no disponible")

        det = _make_detector_output(
            1, 100,  # MI muy bajo
            critical_patterns=["ECO_SEMIOTIC_COLLISION"]
        )
        from vigia.core.evidence_aggregator import aggregate_evidence
        agg = aggregate_evidence(det)
        decision = decide(det, agg)

        self.assertEqual(decision["alert_level"], "CRITICAL",
                         "ECO_SEMIOTIC_COLLISION debe forzar CRITICAL")

    def test_critical_override_reason_names_the_collision_not_just_mi(self):
        """F3 (Ronda 2 audit): _generate_reason() ignored has_collision and
        always attributed CRITICAL to MI's magnitude. At MI=1/100 (0.010,
        nowhere near the CRITICAL threshold) with ECO_SEMIOTIC_COLLISION
        forcing the override, the reason used to read "MI crítico (0.010).
        ... Escalamiento inmediato requerido." -- an auditor reading only the
        reason string, not the raw metadata, would conclude MI itself was
        the trigger. The reason must name the actual cause."""
        try:
            from vigia.core.decision_layer import decide
        except ImportError:
            self.skipTest("decision_layer no disponible")

        det = _make_detector_output(
            1, 100,  # MI muy bajo -- el trigger real es el collision, no MI
            critical_patterns=["ECO_SEMIOTIC_COLLISION"]
        )
        from vigia.core.evidence_aggregator import aggregate_evidence
        agg = aggregate_evidence(det)
        decision = decide(det, agg)

        self.assertEqual(decision["alert_level"], "CRITICAL")
        self.assertIn("ECO_SEMIOTIC_COLLISION", decision["reason"],
                       "El reason de un override por colisión debe nombrar la colisión, "
                       "no atribuir el CRITICAL solo a MI")

    def test_low_mi_gives_low_alert(self):
        """MI muy bajo sin críticos → LOW."""
        try:
            from vigia.core.decision_layer import decide
        except ImportError:
            self.skipTest("decision_layer no disponible")

        det = _make_detector_output(1, 1000)  # MI = 0.001
        from vigia.core.evidence_aggregator import aggregate_evidence
        agg = aggregate_evidence(det)
        decision = decide(det, agg)

        self.assertEqual(decision["alert_level"], "LOW")

    def test_high_mi_gives_high_or_critical(self):
        """MI alto → HIGH o CRITICAL."""
        try:
            from vigia.core.decision_layer import decide
        except ImportError:
            self.skipTest("decision_layer no disponible")

        det = _make_detector_output(80, 100)  # MI = 0.80
        from vigia.core.evidence_aggregator import aggregate_evidence
        agg = aggregate_evidence(det)
        decision = decide(det, agg)

        self.assertIn(decision["alert_level"], ("HIGH", "CRITICAL"),
                      f"MI alto debería dar HIGH o CRITICAL, got {decision['alert_level']}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
