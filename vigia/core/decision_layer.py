#!/usr/bin/env python3
"""
vigia/core/decision_layer.py

Risk Bounded Decision Layer — VIGÍA
Capa de decisión final. NO crea evidencia, solo interpreta el MI agregado.

Principios:
- Umbrales configurables, versionados, auditables
- Sin lógica adicional (no bonuses, no heurísticas)
- CRITICAL automático para ECO_SEMIOTIC_COLLISION
- Todo en fracciones exactas

Autor: Colectivo VIGÍA (DeepSeek arquitectura, Kimi implementación)
Versión: 1.0
"""

from fractions import Fraction
from typing import Dict, Any, List, Optional


# ── Constantes ────────────────────────────────────────────────────────────

# Thresholds calibrados con dataset real (Colectivo VIGÍA, 2026-04)
# LOW < 15/100 <= MEDIUM < 30/100 <= HIGH < CRITICAL (override)
DEFAULT_LOW = Fraction(15, 100)      # < 0.15 → LOW
DEFAULT_MEDIUM = Fraction(30, 100)   # [0.15, 0.30) → MEDIUM
DEFAULT_HIGH = Fraction(60, 100)     # [0.30, 0.60) → HIGH; >= 0.60 → CRITICAL
# Nota: spec propone 1/10, 4/10, 7/10 — pendiente recalibración con corpus real


class RiskBoundedDecisionLayer:
    """
    Capa de decisión final con 4 niveles de alerta.
    NO crea evidencia — solo interpreta el MI agregado.

    Niveles: LOW → MEDIUM → HIGH → CRITICAL
    Override: ECO_SEMIOTIC_COLLISION fuerza CRITICAL independiente del MI.
    """

    def __init__(
        self,
        low_num: int = 15, low_den: int = 100,
        medium_num: int = 30, medium_den: int = 100,
        high_num: int = 60, high_den: int = 100,
    ):
        self.low = Fraction(low_num, low_den)
        self.medium = Fraction(medium_num, medium_den)
        self.high = Fraction(high_num, high_den)

    def decide(self, aggregated_fsv: Dict[str, Any]) -> Dict[str, Any]:
        """
        Toma el FSV agregado y emite veredicto determinista.

        Acepta tanto 'mi_final' (contrato DEA v1) como 'manipulation_index' (alias).
        """
        # Extraer MI — prioridad: mi_final > manipulation_index
        mi_raw = aggregated_fsv.get("mi_final") or aggregated_fsv.get("manipulation_index", {})
        mi = Fraction(
            mi_raw.get("num", 0),
            mi_raw.get("den", 1) or 1
        )

        # Override crítico ECO_SEMIOTIC_COLLISION
        critical_patterns = aggregated_fsv.get("metadata", {}).get("critical_patterns", [])
        has_collision = "ECO_SEMIOTIC_COLLISION" in critical_patterns

        score_str = f"{mi.numerator}/{mi.denominator}"
        score_dec = f"{float(mi):.4f}"

        if has_collision or mi >= self.high:
            level = "CRITICAL"
            verdict = "ADVERSARIAL_SEMIOTIC_PATTERN_DETECTED"
            confidence = "HIGH"
        elif mi >= self.medium:
            level = "HIGH"
            verdict = "ADVERSARIAL_SEMIOTIC_PATTERN_DETECTED"
            confidence = "MEDIUM"
        elif mi >= self.low:
            level = "MEDIUM"
            verdict = "ADVERSARIAL_SEMIOTIC_PATTERN_DETECTED"
            confidence = "LOW"
        else:
            level = "LOW"
            verdict = "NO_SEMIOTIC_ANOMALY_DETECTED"
            confidence = "LOW"

        return {
            "verdict": verdict,
            "alert_level": level,
            "confidence": confidence,
            "score": score_str,
            "_score_decimal": score_dec,  # display only — no usar en lógica (I7)
            "mi_final": {"num": mi.numerator, "den": mi.denominator},
            "reason": self._generate_reason(mi, level, aggregated_fsv),
        }

    def _generate_reason(self, mi: Fraction, level: str, fsv: Dict) -> str:
        meta = fsv.get("metadata", {})
        patterns = meta.get("total_patterns", 0)
        synergies = meta.get("synergy_rules_triggered", 0)
        sequences = meta.get("sequence_rules_triggered", 0)
        dominant = meta.get("dominant_category", "N/A")
        mi_str = f"{float(mi):.3f}"

        # F3 fix: recompute the SAME has_collision check decide() used to
        # pick CRITICAL, so the narrative names the actual trigger instead
        # of always blaming MI. Before this fix, an ECO_SEMIOTIC_COLLISION
        # override at MI=0.000 produced "MI crítico (0.000). ... Escalamiento
        # inmediato requerido." -- CRITICAL with a reason that names the one
        # value (MI) that was nowhere near critical, and never mentions the
        # collision that actually forced the override. Recomputed here
        # (rather than threaded as a new parameter) because _generate_reason
        # already receives the same fsv decide() derived has_collision from.
        has_collision = "ECO_SEMIOTIC_COLLISION" in meta.get("critical_patterns", [])

        if level == "CRITICAL" and has_collision:
            return (
                f"ECO_SEMIOTIC_COLLISION detectado — override crítico independiente de MI "
                f"(MI={mi_str}). {patterns} patrones, {synergies} sinergias, "
                f"{sequences} secuencias. Categoría dominante: {dominant}. "
                f"Escalamiento inmediato requerido."
            )
        if level == "CRITICAL":
            return (
                f"MI crítico ({mi_str}). {patterns} patrones, {synergies} sinergias, "
                f"{sequences} secuencias. Categoría dominante: {dominant}. "
                f"Escalamiento inmediato requerido."
            )
        elif level == "HIGH":
            return (
                f"MI elevado ({mi_str}). {patterns} patrones, {synergies} sinergias, "
                f"{sequences} secuencias. Análisis humano complementario recomendado."
            )
        elif level == "MEDIUM":
            return (
                f"MI moderado ({mi_str}). {patterns} patrones detectados con correlación parcial. "
                f"Requiere verificación contextual."
            )
        else:
            return (
                f"MI bajo ({mi_str}). {patterns} patrones sin correlación adversarial significativa."
            )


# ── API de conveniencia ───────────────────────────────────────────────────

def decide_verdict(aggregated_fsv: Dict[str, Any]) -> Dict[str, Any]:
    """API de alto nivel para decisión."""
    layer = RiskBoundedDecisionLayer()
    return layer.decide(aggregated_fsv)


def decide(detector_output: Dict[str, Any], aggregated_fsv: Dict[str, Any]) -> Dict[str, Any]:
    """
    Adaptador canónico para run_pipeline.py.
    Recibe detector_output (para critical_patterns) y aggregated_fsv.
    Inyecta critical_patterns del detector en metadata si no están en el aggregator.
    """
    # Garantizar que critical_patterns llegue al decision layer
    if "metadata" not in aggregated_fsv:
        aggregated_fsv["metadata"] = {}
    if not aggregated_fsv["metadata"].get("critical_patterns"):
        aggregated_fsv["metadata"]["critical_patterns"] = detector_output.get("critical_patterns", [])

    layer = RiskBoundedDecisionLayer()
    return layer.decide(aggregated_fsv)
