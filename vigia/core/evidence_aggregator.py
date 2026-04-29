#!/usr/bin/env python3
"""
vigia/core/evidence_aggregator.py

Evidence Aggregator — VIGÍA
Combina señales semióticas usando composición probabilística acotada.
Determinista, auditable, sin floating point en decisiones.

Fórmula: MI_final = 1 - (1 - MI_base) * (1 - synergy*ALPHA) * (1 - sequence*ALPHA)
Propiedad: cada componente aporta evidencia independiente, no amplifica la base.

Autor: Colectivo VIGÍA (ChatGPT fórmula, Kimi implementación, DeepSeek validación)
Versión: 1.0
"""

import json
from fractions import Fraction
from typing import Dict, Any, List, Optional
from dataclasses import dataclass


# ── Constantes ────────────────────────────────────────────────────────────

ALPHA = Fraction(1, 2)  # Factor de dependencia: synergy/sequence pesan 50% por dependencia con matches
ONE = Fraction(1, 1)
ZERO = Fraction(0, 1)
MAX_CAP = Fraction(1, 1)


# ── Dataclass de salida ────────────────────────────────────────────────────

@dataclass
class AggregatedFSV:
    manipulation_index: Fraction
    base_mi: Fraction
    synergy_factor: Fraction
    sequence_factor: Fraction
    total_patterns: int
    dominant_category: Optional[str]
    peirce_layers_present: List[str]
    critical_patterns: List[str]


class EvidenceAggregator:
    """
    Agrega señales del Detection Layer en un índice único.

    Principios:
    - Composición complement-product: cada señal reduce independientemente
      la probabilidad de "no-manipulación"
    - Sin bonificaciones aditivas (no crea evidencia)
    - Todo en fracciones exactas para trazabilidad Daubert
    """

    def __init__(self, alpha: Fraction = ALPHA):
        self.alpha = alpha
        self.one = ONE

    def aggregate(
        self,
        fsv: Dict[str, Any],
        synergy_result: Dict[str, Any],
        sequence_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Args:
            fsv: Forensic Signal Vector del Detection Layer
            synergy_result: Resultado del Synergy Engine
            sequence_result: Resultado del Sequence Detector

        Returns:
            FSV agregado con manipulation_index final
        """
        # 1. Extraer MI base
        mi_base = Fraction(
            fsv.get("manipulation_index", {}).get("num", 0),
            fsv.get("manipulation_index", {}).get("den", 1)
        )

        # 2. Calcular synergy_factor usando composición de impactos individuales
        synergy_factor = self._compute_synergy_factor(
            synergy_result.get("triggered_rules", [])
        )

        # 3. Calcular sequence_factor usando composición de impactos individuales
        sequence_factor = self._compute_sequence_factor(
            sequence_result.get("triggered_rules", [])
        )

        # 4. Composición complement-product con alpha de dependencia
        mi_final = self.one - (
            (self.one - mi_base) *
            (self.one - synergy_factor * self.alpha) *
            (self.one - sequence_factor * self.alpha)
        )

        # 5. Cap a [0, 9/10] — Daubert: no certeza absoluta mecánica
        MAX_MI = Fraction(9, 10)
        mi_final = max(ZERO, min(mi_final, MAX_MI))

        mi_num = mi_final.numerator
        mi_den = mi_final.denominator

        return {
            # Clave canónica para CLI (contrato DEA v1)
            "mi_final": {"num": mi_num, "den": mi_den},
            # Alias para compatibilidad con pipeline.py y compare_runs
            "manipulation_index": {
                "num": mi_num,
                "den": mi_den,
                "_decimal": f"{float(mi_final):.4f}"  # display only — no usar en lógica
            },
            "components": {
                "base_mi": f"{mi_base.numerator}/{mi_base.denominator}",
                "base": {"num": mi_base.numerator, "den": mi_base.denominator},
                "synergy_factor": f"{synergy_factor.numerator}/{synergy_factor.denominator}",
                "synergy": {"num": synergy_factor.numerator, "den": synergy_factor.denominator},
                "sequence_factor": f"{sequence_factor.numerator}/{sequence_factor.denominator}",
                "sequence": {"num": sequence_factor.numerator, "den": sequence_factor.denominator},
                "alpha": f"{self.alpha.numerator}/{self.alpha.denominator}",
                "aggregation_model": "complement_product_with_alpha_DEA_v1"
            },
            "metadata": {
                "total_patterns": fsv.get("total_patterns", 0),
                "dominant_category": fsv.get("dominant_category"),
                "peirce_layers": fsv.get("peirce_layers_present", []),
                "critical_patterns": fsv.get("critical_patterns", []),
                "synergy_rules_triggered": len(synergy_result.get("triggered_rules", [])),
                "sequence_rules_triggered": len(sequence_result.get("triggered_rules", []))
            }
        }

    def _compute_synergy_factor(self, triggered_rules: List[Dict]) -> Fraction:
        """
        Calcula synergy_factor usando composición de impactos.

        synergy_factor = 1 - Π(1 - impact_i)
        """
        if not triggered_rules:
            return ZERO

        complement_product = self.one
        for rule in triggered_rules:
            impact_num = rule.get("impact_num", rule.get("applied_bonus_num", 0))
            impact_den = rule.get("impact_den", rule.get("applied_bonus_den", 100))
            impact = self._clamp_fraction(Fraction(impact_num, impact_den))

            complement_product *= (self.one - impact)

        synergy_factor = self.one - complement_product
        return self._clamp_fraction(synergy_factor)

    def _compute_sequence_factor(self, triggered_sequences: List[Dict]) -> Fraction:
        """
        Calcula sequence_factor usando composición de impactos.

        sequence_factor = 1 - Π(1 - bonus_i)
        """
        if not triggered_sequences:
            return ZERO

        complement_product = self.one
        for seq in triggered_sequences:
            bonus_num = seq.get("bonus_num", seq.get("confidence_bonus_num", 0))
            bonus_den = seq.get("bonus_den", seq.get("confidence_bonus_den", 100))
            bonus = self._clamp_fraction(Fraction(bonus_num, bonus_den))

            complement_product *= (self.one - bonus)

        sequence_factor = self.one - complement_product
        return self._clamp_fraction(sequence_factor)

    @staticmethod
    def _clamp_fraction(frac: Fraction, min_val: Fraction = ZERO, max_val: Fraction = MAX_CAP) -> Fraction:
        """Garantiza que la fracción esté en [min_val, max_val]."""
        if frac < min_val:
            return min_val
        if frac > max_val:
            return max_val
        return frac


# ── API de conveniencia ───────────────────────────────────────────────────

def aggregate_fsv(
    fsv: Dict[str, Any],
    synergy: Dict[str, Any],
    sequences: Dict[str, Any]
) -> Dict[str, Any]:
    """API de alto nivel para agregación de FSV."""
    aggregator = EvidenceAggregator()
    return aggregator.aggregate(fsv, synergy, sequences)


def aggregate_evidence(detector_output: Dict[str, Any],
                        alpha: Optional[Fraction] = None) -> Dict[str, Any]:
    """
    Adaptador canónico para run_pipeline.py.

    alpha — factor de dependencia entre componentes. Default: Fraction(1,2).
    Calibrable por dataset: si synergy/sequence están muy correlacionados,
    bajar alpha (ej: Fraction(1,3)); si son independientes, subir (Fraction(2,3)).
    (DeepSeek — explotación del alpha fijo en código abierto).
    """
    agg_alpha = alpha if alpha is not None else ALPHA
    aggregator = EvidenceAggregator(alpha=agg_alpha)
    return aggregator.aggregate(
        detector_output.get("fsv", {}),
        detector_output.get("synergy", {}),
        detector_output.get("sequences", {}),
    )
