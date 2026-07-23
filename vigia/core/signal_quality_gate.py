#!/usr/bin/env python3
"""
vigia/signal_quality_gate.py — Signal Quality Gate

Previene que VIGÍA emita un veredicto de ACCEPT (culpable)
cuando las señales no tienen calidad suficiente.

Principio Peirceano: Firstness no basta para Thirdness.
Acumular observaciones débiles no revela un hábito subyacente.

Principio Culinario: Muchos ingredientes mediocres no hacen
un plato excelente. Necesitás al menos UN ingrediente fuerte.

Checks:
  1. Diversidad de herramientas (mínimo 2)
  2. Al menos una señal fuerte (z >= 2.0)
  3. Independencia (no todas las señales de la misma tool)
  4. Variabilidad de z-scores (no todas idénticas)
  5. Detección de inflación por ruido (muchas débiles, pocas fuertes)
"""

from __future__ import annotations

from fractions import Fraction
from typing import List, Optional, Tuple

# B-116 (condition 4, Kimi-endorsed placeholder policy): source_tool values
# that name acquisition/conversion utilities, not analysis tools. The B-116
# census over the 66 ABSTAIN_INSUFFICIENT_TOOLS cases showed these four
# strings (plus None) dominate legacy artifacts: legacy_converter(88),
# manual_forensic_review(43), generate_forensic_hash(35), read_evidence(8).
# Counting them as distinct tools made the diversity check measure
# conversion pipelines instead of analytic independence. They are treated
# exactly like the literal "unknown": skipped in the tool_name ->
# source_tool -> evidence_type fallback chain. SINGLE SOURCE OF TRUTH —
# do not replicate this set in scripts (dryrun imports it from here).
_NON_ANALYSIS_PLACEHOLDERS: frozenset = frozenset({
    "legacy_converter",
    "manual_forensic_review",
    "generate_forensic_hash",
    "read_evidence",
})


class QualityGateResult:
    def __init__(self, passed: bool, reason_code: str, reason_detail: str, metrics: dict):
        self.passed = passed
        self.reason_code = reason_code
        self.reason_detail = reason_detail
        self.metrics = metrics


class SignalQualityGate:
    """
    Catador de señales. Prueba cada ingrediente antes de servir el plato.
    """

    MIN_TOOLS_REQUIRED = 2
    MIN_STRONG_SIGNALS = 1
    Z_STRONG = 2.0
    MIN_Z_VARIANCE = 0.5
    MAX_SAME_TOOL_RATIO = 0.6  # Máximo 60% de señales de la misma herramienta

    def evaluate(self, signals: List, evidence_graph=None) -> QualityGateResult:
        if not signals:
            return QualityGateResult(
                passed=False,
                reason_code="ABSTAIN_NO_SIGNALS",
                reason_detail="No signals available for forensic decision.",
                metrics={"signal_count": 0}
            )

        metrics = {"signal_count": len(signals)}

        # Check 1: Diversidad de herramientas
        tool_check = self._check_tool_diversity(signals)
        metrics.update(tool_check)
        if not tool_check["passed"]:
            return QualityGateResult(
                passed=False,
                reason_code="ABSTAIN_INSUFFICIENT_TOOLS",
                reason_detail=tool_check["detail"],
                metrics=metrics
            )

        # Check 2: Señales fuertes
        strength_check = self._check_signal_strength(signals)
        metrics.update(strength_check)
        if not strength_check["passed"]:
            return QualityGateResult(
                passed=False,
                reason_code="ABSTAIN_WEAK_SIGNALS",
                reason_detail=strength_check["detail"],
                metrics=metrics
            )

        # Check 3: Independencia
        independence_check = self._check_tool_independence(signals)
        metrics.update(independence_check)
        if not independence_check["passed"]:
            return QualityGateResult(
                passed=False,
                reason_code="ABSTAIN_DEPENDENT_SIGNALS",
                reason_detail=independence_check["detail"],
                metrics=metrics
            )

        # Check 4: Variabilidad de z-scores
        variance_check = self._check_z_variance(signals)
        metrics.update(variance_check)
        if not variance_check["passed"]:
            return QualityGateResult(
                passed=False,
                reason_code="ABSTAIN_LOW_Z_VARIANCE",
                reason_detail=variance_check["detail"],
                metrics=metrics
            )

        return QualityGateResult(
            passed=True,
            reason_code="QUALITY_OK",
            reason_detail=f"All checks passed: {len(signals)} signals from "
                         f"{metrics['unique_tools']} tools, "
                         f"max_z={metrics['max_z']:.2f}",
            metrics=metrics
        )

    def _get_tool_name(self, signal) -> str:
        # B-116 (unblocking condition 3): the scorer's artifacts carry
        # `source_tool` (often the literal string "unknown" in legacy cases)
        # and a reliably populated `evidence_type` — not `tool_name`. The
        # diversity/independence checks fall back along that chain so that
        # provenance-rich cases are not degraded just because the tool-name
        # field was never populated during conversion. "unknown" is treated
        # as absent: it must never count as a distinct tool — and so are the
        # acquisition/conversion placeholders (condition 4): a utility that
        # copied or hashed the artifact is not the analysis that produced
        # the signal.
        # B-116 MODE C (2026-07-22): `type` agregado como último eslabón.
        # La serie VIGIA-REAL-*/SRL-* (el corpus más validado) declara el
        # canal de adquisición en `type` (`registry`, `network_flow`,
        # `bash_history`, ...) — la conversión nunca lo mapeó a
        # evidence_type, y sin este eslabón 16 casos MALICE reales
        # aparecían como mono-herramienta (clase C1 de
        # docs/B116_CONDITION4_DESIGN.md). Mismo nivel epistémico que
        # evidence_type: declaración del examinador sobre el canal.
        for field in ("tool_name", "source_tool", "evidence_type", "type"):
            value = getattr(signal, field, None)
            if value is None and isinstance(signal, dict):
                value = signal.get(field)
            if value and value != "unknown" and value not in _NON_ANALYSIS_PLACEHOLDERS:
                return str(value)
        return "unknown"

    def _get_z_score(self, signal) -> float:
        # B-116/B-211: coerción explícita a float — el pipeline VIGÍA
        # transporta z_scores como Fraction, y abs(Fraction) devuelto tal
        # cual crashea los f"{...:.2f}" de este módulo en Python < 3.12
        # (Fraction.__format__ sin presentation types). El gate opera en
        # espacio float por diseño (umbrales 2.0/0.5) y NO está en el path
        # sellado, así que la coerción es contractual, no una violación
        # del invariante Fraction-only.
        if hasattr(signal, 'z_score'):
            return float(abs(signal.z_score or 0.0))
        elif isinstance(signal, dict):
            return float(abs(signal.get("z_score", 0.0) or 0.0))
        return 0.0

    def _check_tool_diversity(self, signals: List) -> dict:
        tools = set()
        for s in signals:
            tools.add(self._get_tool_name(s))
        unique_tools = len(tools)
        passed = unique_tools >= self.MIN_TOOLS_REQUIRED
        return {
            "unique_tools": unique_tools,
            "min_required": self.MIN_TOOLS_REQUIRED,
            "passed": passed,
            "detail": (
                f"Found {unique_tools} unique tool(s), "
                f"minimum required: {self.MIN_TOOLS_REQUIRED}."
                if not passed else
                f"Tool diversity OK: {unique_tools} tools."
            )
        }

    def _check_signal_strength(self, signals: List) -> dict:
        z_scores = [self._get_z_score(s) for s in signals]
        z_scores = [z for z in z_scores if z > 0]
        if not z_scores:
            return {
                "max_z": 0.0,
                "strong_signals": 0,
                "passed": False,
                "detail": "No valid z-scores found."
            }
        max_z = max(z_scores)
        strong_count = sum(1 for z in z_scores if z >= self.Z_STRONG)
        passed = strong_count >= self.MIN_STRONG_SIGNALS
        return {
            "max_z": round(max_z, 3),
            "strong_signals": strong_count,
            "weak_signals": len(z_scores) - strong_count,
            "passed": passed,
            "detail": (
                f"No signal exceeds z={self.Z_STRONG}. "
                f"Max z={max_z:.2f}. Need at least {self.MIN_STRONG_SIGNALS} strong signal(s)."
                if not passed else
                f"Signal strength OK: {strong_count} strong signal(s), max_z={max_z:.2f}."
            )
        }

    def _check_tool_independence(self, signals: List) -> dict:
        tool_counts = {}
        for s in signals:
            tool = self._get_tool_name(s)
            tool_counts[tool] = tool_counts.get(tool, 0) + 1
        n = len(signals)
        max_from_one_tool = max(tool_counts.values()) if tool_counts else 0
        ratio = max_from_one_tool / n if n > 0 else 1.0
        passed = ratio <= self.MAX_SAME_TOOL_RATIO
        return {
            "max_from_one_tool": max_from_one_tool,
            "ratio": round(ratio, 2),
            "max_allowed_ratio": self.MAX_SAME_TOOL_RATIO,
            "passed": passed,
            "detail": (
                f"{max_from_one_tool}/{n} signals from same tool (ratio={ratio:.2f}). "
                f"Maximum allowed: {self.MAX_SAME_TOOL_RATIO}."
                if not passed else
                f"Independence OK: max {max_from_one_tool}/{n} from one tool."
            )
        }

    def _check_z_variance(self, signals: List) -> dict:
        z_scores = [self._get_z_score(s) for s in signals]
        z_scores = [z for z in z_scores if z > 0]
        if len(z_scores) < 2:
            return {"z_range": 0.0, "passed": True, "detail": "Not enough signals for variance check."}
        min_z = min(z_scores)
        max_z = max(z_scores)
        z_range = max_z - min_z
        passed = z_range >= self.MIN_Z_VARIANCE
        return {
            "z_range": round(z_range, 3),
            "min_z": round(min_z, 3),
            "max_z": round(max_z, 3),
            "passed": passed,
            "detail": (
                f"Z-score range is {z_range:.3f}, below minimum {self.MIN_Z_VARIANCE}. "
                f"Too uniform to be independent evidence."
                if not passed else
                f"Z-score variance OK: range={z_range:.3f}."
            )
        }

    def detect_noise_inflation(self, signals: List, posterior: float) -> Tuple[float, dict]:
        """
        Detecta y corrige inflación de confianza sobre señales ruidosas.

        Principio: Muchas Firstnesses (señales débiles) no hacen una Thirdness (ley).
        Si hay muchas señales débiles y pocas fuertes, el posterior está inflado.
        """
        if not signals:
            return posterior, {"inflation_detected": False}

        strong = [s for s in signals if self._get_z_score(s) >= self.Z_STRONG]
        weak = [s for s in signals if 0 < self._get_z_score(s) < self.Z_STRONG]

        n_strong = len(strong)
        n_weak = len(weak)

        # Caso 1: Solo señales débiles, nada fuerte
        if n_strong == 0 and n_weak >= 3:
            penalty = min(n_weak * 0.10, 0.40)
            adjusted = posterior - (posterior - 0.5) * penalty
            return max(0.51, adjusted), {
                "inflation_detected": True,
                "inflation_type": "PURE_NOISE_ACCUMULATION",
                "strong_signals": 0,
                "weak_signals": n_weak,
                "original_posterior": round(posterior, 4),
                "adjusted_posterior": round(adjusted, 4),
                "penalty_applied": round(penalty, 4)
            }

        # Caso 2: Muchas débiles por cada fuerte
        if n_strong > 0 and n_weak > n_strong * 3:
            penalty = min((n_weak / n_strong) * 0.08, 0.35)
            adjusted = posterior - (posterior - 0.5) * penalty
            return max(0.51, adjusted), {
                "inflation_detected": True,
                "inflation_type": "WEAK_OVERWHELMING_STRONG",
                "strong_signals": n_strong,
                "weak_signals": n_weak,
                "ratio": round(n_weak / n_strong, 2),
                "original_posterior": round(posterior, 4),
                "adjusted_posterior": round(adjusted, 4),
                "penalty_applied": round(penalty, 4)
            }

        return posterior, {"inflation_detected": False}
