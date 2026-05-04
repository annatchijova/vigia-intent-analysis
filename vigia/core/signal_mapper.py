# vigia/pipeline/signal_mapper.py
"""
Signal Mapper
==============
El eslabón que falta entre los módulos nuevos y el pipeline existente.

Los módulos nuevos (TCV, ASD, HLT, CCPL) producen sus propios
objetos de resultado. El pipeline existente consume SignalOutput.

Este módulo hace la traducción de forma determinista y trazable.

Arquitectura:
  TCV Result  ──┐
  ASD Result  ──┤
  CCPL Result ──┼──► SignalMapper ──► list[SignalOutput] ──► Pipeline existente
  HLT Report  ──┘
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from fractions import Fraction
from typing import Any, Optional

# Import del SignalOutput canónico — path único post-limpieza
from vigia.models.signal_output import SignalOutput


# ---------------------------------------------------------------------------
# Constantes de nombres de señales
# Los nombres aquí deben coincidir 1:1 con los usados en CasePatternLibrary
# Cualquier cambio aquí requiere actualizar la KB de patrones
# ---------------------------------------------------------------------------

class SignalNames:
    """
    Nombres canónicos de señales producidas por módulos nuevos.
    Usar estas constantes — nunca strings literales.
    """
    # TCV signals
    TCV_CAUSALITY_VIOLATION       = "tcv_causality_violation"
    TCV_ENTITY_PREDATES_EXISTENCE = "tcv_entity_predates_existence"
    TCV_TIMEZONE_INCONSISTENCY    = "tcv_timezone_inconsistency"
    TCV_CLOCK_SKEW_SYSTEMATIC     = "tcv_clock_skew_systematic"
    TCV_DURATION_IMPOSSIBLE       = "tcv_duration_impossible"
    TCV_FABRICATION_SIGNAL        = "tcv_fabrication_signal"

    # ASD signals
    ASD_SILENCE_HIGH              = "asd_silence_score_high"
    ASD_SELECTIVE_ERASURE         = "asd_selective_erasure"
    ASD_EXPERT_ERASURE            = "asd_expert_erasure"
    ASD_PREFETCH_ABSENT           = "prefetch_absent"
    ASD_AMCACHE_ABSENT            = "amcache_absent"
    ASD_EVENT_7045_ABSENT         = "event_7045_absent"
    ASD_FABRICATION_HIGH          = "asd_fabrication_high"

    # CCPL signals (los matches más importantes como señales)
    CCPL_SUPPLY_CHAIN_MATCH       = "ccpl_supply_chain_match"
    CCPL_TIMESTOMPING_MATCH       = "ccpl_timestomping_match"
    CCPL_LOG_CLEARING_MATCH       = "ccpl_log_clearing_match"
    CCPL_LSASS_DUMP_MATCH         = "ccpl_lsass_dump_match"
    CCPL_LATERAL_MOVEMENT_MATCH   = "ccpl_lateral_movement_match"
    CCPL_MULTI_TACTIC_DETECTED    = "ccpl_multi_tactic_detected"

    # HLT signals
    HLT_LOW_STABILITY             = "hlt_low_verdict_stability"
    HLT_NEAR_MISS_MALICE          = "hlt_near_miss_malice"
    HLT_ADVERSARIAL_SIMPLICITY    = "ockham_adversarial_flag"

    # Ockham Adversarial
    OCKHAM_ADVERSARIAL_FLAG       = "ockham_adversarial_flag"
    OCKHAM_PENALTY_APPLIED        = "ockham_penalty_applied"


# Mapeo: technique_id → signal_name para CCPL
TECHNIQUE_TO_SIGNAL: dict[str, str] = {
    "T1195.002": SignalNames.CCPL_SUPPLY_CHAIN_MATCH,
    "T1070.006": SignalNames.CCPL_TIMESTOMPING_MATCH,
    "T1070.001": SignalNames.CCPL_LOG_CLEARING_MATCH,
    "T1003.001": SignalNames.CCPL_LSASS_DUMP_MATCH,
    "T1550.002": SignalNames.CCPL_LATERAL_MOVEMENT_MATCH,
}


# ---------------------------------------------------------------------------
# Modelos
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class MappingResult:
    """
    Resultado de la traducción de un módulo a SignalOutputs.
    Incluye audit trail propio.
    """
    source_module:  str
    signals:        tuple[SignalOutput, ...]
    signal_count:   int
    mapping_hash:   str


# ---------------------------------------------------------------------------
# Mapper principal
# ---------------------------------------------------------------------------

class SignalMapper:
    """
    Traduce resultados de módulos nuevos a SignalOutput del pipeline.

    Principio de diseño:
    - Cada módulo nuevo produce N señales específicas
    - Las señales tienen nombres canónicos (ver SignalNames)
    - Los valores son siempre Fraction entre 0 y 1
    - La confianza refleja cuánto confiamos en esa señal específica
    - El metadata incluye el audit_hash del módulo origen

    Uso:
        mapper = SignalMapper()
        signals = mapper.from_tcv(tcv_result)
        signals += mapper.from_asd(asd_result)
        signals += mapper.from_ccpl(ccpl_result)
        signals += mapper.from_hlt(lineage_report)
        # Ahora pasar signals al pipeline existente
    """

    def from_tcv(self, tcv_result) -> MappingResult:
        """
        Traduce TCVResult a SignalOutputs.

        Cada tipo de anomalía produce una señal distinta.
        La severidad de la anomalía determina el valor de la señal.
        """
        from vigia.temporal.coherence_validator import AnomalyType, AnomalySeverity

        signals = []

        # Señal agregada de fabricación temporal
        if tcv_result.fabrication_signal > Fraction(0):
            signals.append(SignalOutput(
                tool_name=SignalNames.TCV_FABRICATION_SIGNAL,
                value=tcv_result.fabrication_signal,
                z_score=Fraction(0),
                confidence=tcv_result.coherence_score,
                metadata={
                    "anomaly_count":    len(tcv_result.anomalies),
                    "coherence_pct":    int(tcv_result.coherence_score * 100),
                    "fabrication_pct":  int(tcv_result.fabrication_signal * 100),
                    "audit_hash":       tcv_result.audit_hash,
                    "summary":          tcv_result.summary,
                },
            ))

        # Señales por tipo de anomalía
        severity_to_value = {
            AnomalySeverity.CRITICAL: Fraction(1, 1),
            AnomalySeverity.HIGH:     Fraction(3, 4),
            AnomalySeverity.MEDIUM:   Fraction(1, 2),
            AnomalySeverity.LOW:      Fraction(1, 4),
        }

        anomaly_type_to_signal = {
            AnomalyType.CAUSALITY_VIOLATION:       SignalNames.TCV_CAUSALITY_VIOLATION,
            AnomalyType.ENTITY_PREDATES_EXISTENCE: SignalNames.TCV_ENTITY_PREDATES_EXISTENCE,
            AnomalyType.TIMEZONE_INCONSISTENCY:    SignalNames.TCV_TIMEZONE_INCONSISTENCY,
            AnomalyType.CLOCK_SKEW_SYSTEMATIC:     SignalNames.TCV_CLOCK_SKEW_SYSTEMATIC,
            AnomalyType.DURATION_IMPOSSIBLE:       SignalNames.TCV_DURATION_IMPOSSIBLE,
        }

        # Agrupar anomalías por tipo y tomar la más severa
        by_type: dict[AnomalyType, list] = {}
        for anomaly in tcv_result.anomalies:
            by_type.setdefault(anomaly.anomaly_type, []).append(anomaly)

        for anomaly_type, anomaly_list in by_type.items():
            signal_name = anomaly_type_to_signal.get(anomaly_type)
            if not signal_name:
                continue

            # Anomalía más severa del tipo
            worst = max(anomaly_list, key=lambda a: a.severity.value)
            value = severity_to_value.get(worst.severity, Fraction(1, 2))

            signals.append(SignalOutput(
                tool_name=signal_name,
                value=value,
                z_score=Fraction(0),
                confidence=worst.forensic_weight,
                metadata={
                    "count":             len(anomaly_list),
                    "worst_severity":    worst.severity.name,
                    "worst_delta_s":     worst.delta_seconds,
                    "hard_to_fake":      worst.hard_to_fake,
                    "description":       worst.description[:200],
                    "investigation":     worst.investigation_hint[:200],
                    "audit_hash":        tcv_result.audit_hash,
                },
            ))

        mapping_hash = self._compute_mapping_hash("TCV", signals)
        return MappingResult(
            source_module="TemporalCoherenceValidator",
            signals=tuple(signals),
            signal_count=len(signals),
            mapping_hash=mapping_hash,
        )

    def from_asd(self, asd_result) -> MappingResult:
        """
        Traduce SilenceAnalysisResult a SignalOutputs.

        El silencio adversarial produce señales de ausencia —
        señales cuyo valor alto indica que algo que DEBERÍA
        estar presente NO está.
        """
        signals = []

        # Señal de silencio general
        if asd_result.silence_score > Fraction(1, 4):
            signals.append(SignalOutput(
                tool_name=SignalNames.ASD_SILENCE_HIGH,
                value=asd_result.silence_score,
                z_score=Fraction(0),
                confidence=asd_result.selectivity_score,
                metadata={
                    "silence_pct":      int(asd_result.silence_score * 100),
                    "selectivity_pct":  int(asd_result.selectivity_score * 100),
                    "fabrication_pct":  int(asd_result.fabrication_likelihood * 100),
                    "audit_hash":       asd_result.audit_hash,
                },
            ))

        # Señal de borrado selectivo (más diagnóstica)
        if asd_result.selectivity_score > Fraction(1, 3):
            signals.append(SignalOutput(
                tool_name=SignalNames.ASD_SELECTIVE_ERASURE,
                value=asd_result.selectivity_score,
                z_score=Fraction(0),
                confidence=Fraction(9, 10),  # Alta confianza — selectividad es difícil de explicar benignamente
                metadata={
                    "selectivity_pct":    int(asd_result.selectivity_score * 100),
                    "sophistication_pct": int(asd_result.erasure_sophistication * 100),
                    "interpretation": (
                        "Artefactos fáciles de borrar presentes + "
                        "artefactos difíciles de borrar ausentes = "
                        "borrado quirúrgico por actor con conocimiento forense"
                    ),
                    "audit_hash": asd_result.audit_hash,
                },
            ))

        # Señal de sofisticación de borrado
        if asd_result.erasure_sophistication > Fraction(1, 2):
            signals.append(SignalOutput(
                tool_name=SignalNames.ASD_EXPERT_ERASURE,
                value=asd_result.erasure_sophistication,
                z_score=Fraction(0),
                confidence=Fraction(85, 100),
                metadata={
                    "sophistication_pct": int(asd_result.erasure_sophistication * 100),
                    "top_hints": asd_result.top_investigation_hints[:3],
                    "audit_hash": asd_result.audit_hash,
                },
            ))

        # Señales específicas por artefacto ausente confirmado
        absent_artifact_signals = {
            "prefetch_entry":   SignalNames.ASD_PREFETCH_ABSENT,
            "amcache_entry":    SignalNames.ASD_AMCACHE_ABSENT,
            "event_7045":       SignalNames.ASD_EVENT_7045_ABSENT,
        }

        for record in asd_result.silence_records:
            if not record.absence_confirmed:
                continue
            art_type = record.expected_artifact.artifact_type
            signal_name = absent_artifact_signals.get(art_type)
            if signal_name:
                signals.append(SignalOutput(
                    tool_name=signal_name,
                    value=record.expected_artifact.forensic_value,
                    z_score=Fraction(0),
                    confidence=record.expected_artifact.forensic_value,
                    metadata={
                        "erasure_difficulty": (
                            record.expected_artifact.erasure_difficulty.name
                        ),
                        "forensic_value_pct": int(
                            record.expected_artifact.forensic_value * 100
                        ),
                        "detection_command":  (
                            record.expected_artifact.detection_command
                        ),
                        "alternative_explanation": record.alternative_explanation,
                        "audit_hash": asd_result.audit_hash,
                    },
                ))

        # Señal integrada de fabricación
        if asd_result.fabrication_likelihood > Fraction(1, 2):
            signals.append(SignalOutput(
                tool_name=SignalNames.ASD_FABRICATION_HIGH,
                value=asd_result.fabrication_likelihood,
                z_score=Fraction(0),
                confidence=asd_result.selectivity_score,
                metadata={
                    "fabrication_pct": int(asd_result.fabrication_likelihood * 100),
                    "audit_hash": asd_result.audit_hash,
                },
            ))

        mapping_hash = self._compute_mapping_hash("ASD", signals)
        return MappingResult(
            source_module="AdversarialSilenceDetector",
            signals=tuple(signals),
            signal_count=len(signals),
            mapping_hash=mapping_hash,
        )

    def from_ccpl(self, ccpl_result) -> MappingResult:
        """
        Traduce CCPLResult a SignalOutputs.

        Cada match de patrón ATT&CK produce una señal.
        Un match de alta confianza es una señal fuerte.
        """
        signals = []

        # Señal por cada match de técnica conocida
        for match in ccpl_result.matches:
            technique_id = match.pattern.technique_id
            signal_name = TECHNIQUE_TO_SIGNAL.get(technique_id)

            if signal_name:
                signals.append(SignalOutput(
                    tool_name=signal_name,
                    value=match.confidence_score,
                    z_score=Fraction(0),
                    confidence=match.coverage,
                    metadata={
                        "technique_id":     technique_id,
                        "technique_name":   match.pattern.technique_name,
                        "tactic":           match.pattern.tactic.name,
                        "coverage_pct":     int(match.coverage * 100),
                        "confidence_level": match.confidence_level.name,
                        "source":           match.pattern.source_document,
                        "source_url":       match.pattern.source_url,
                        "matched_signals":  sorted(match.matched_required),
                        "missing_signals":  sorted(match.missing_required),
                        "investigation_gaps": match.investigation_gaps[:3],
                        "audit_hash":       ccpl_result.audit_hash,
                    },
                ))

        # Señal de múltiples tácticas detectadas (kill chain avanzado)
        n_tactics = len({m.pattern.tactic for m in ccpl_result.matches})
        if n_tactics >= 3:
            signals.append(SignalOutput(
                tool_name=SignalNames.CCPL_MULTI_TACTIC_DETECTED,
                value=min(
                    Fraction(1),
                    Fraction(n_tactics, 5)   # 5 tácticas = score 1.0
                ),
                z_score=Fraction(0),
                confidence=ccpl_result.aggregate_confidence,
                metadata={
                    "tactic_count":  n_tactics,
                    "tactics":       ccpl_result.kill_chain_position,
                    "kill_chain":    " → ".join(ccpl_result.kill_chain_position),
                    "interpretation": (
                        f"Kill chain de {n_tactics} tácticas detectadas. "
                        f"Incidente multi-fase con alta probabilidad de actor APT."
                    ),
                    "audit_hash": ccpl_result.audit_hash,
                },
            ))

        mapping_hash = self._compute_mapping_hash("CCPL", signals)
        return MappingResult(
            source_module="CasePatternLibrary",
            signals=tuple(signals),
            signal_count=len(signals),
            mapping_hash=mapping_hash,
        )

    def from_hlt(self, lineage_report) -> MappingResult:
        """
        Traduce LineageReport a SignalOutputs.

        El linaje produce señales sobre la calidad del veredicto,
        no sobre el incidente en sí.
        """
        signals = []

        # Señal de baja estabilidad del veredicto
        stability = lineage_report.verdict_stability
        if stability < Fraction(6, 10):
            signals.append(SignalOutput(
                tool_name=SignalNames.HLT_LOW_STABILITY,
                value=Fraction(1) - stability,  # Invertir: alto = inestable
                z_score=Fraction(0),
                confidence=Fraction(9, 10),
                metadata={
                    "stability_pct": int(stability * 100),
                    "interpretation": (
                        f"Veredicto ganado con {int(stability * 100)}% de estabilidad. "
                        f"Hipótesis alternativas muy cercanas al ganador."
                    ),
                    "audit_hash": lineage_report.audit_hash,
                },
            ))

        # Señal de near miss malicioso
        malice_near_misses = [
            n for n in lineage_report.near_misses
            if n.verdict == "MALICE"
        ]
        if malice_near_misses and lineage_report.winner.verdict == "BENIGN":
            signals.append(SignalOutput(
                tool_name=SignalNames.HLT_NEAR_MISS_MALICE,
                value=Fraction(1) - stability,
                z_score=Fraction(0),
                confidence=Fraction(8, 10),
                metadata={
                    "near_miss_count": len(malice_near_misses),
                    "near_miss_names": [n.hypothesis_name for n in malice_near_misses],
                    "interpretation": (
                        f"Veredicto BENIGN pero {len(malice_near_misses)} hipótesis "
                        f"MALICE dentro del 20% del ganador. "
                        f"Señales pivot pueden invertir el veredicto."
                    ),
                    "pivot_signals": [
                        p.signal_name for p in lineage_report.pivot_signals[:3]
                    ],
                    "audit_hash": lineage_report.audit_hash,
                },
            ))

        mapping_hash = self._compute_mapping_hash("HLT", signals)
        return MappingResult(
            source_module="HypothesisLineageTracker",
            signals=tuple(signals),
            signal_count=len(signals),
            mapping_hash=mapping_hash,
        )

    def from_ockham(self, penalty_result) -> MappingResult:
        """
        Traduce OckhamPenaltyResult a SignalOutputs.
        """
        signals = []

        if penalty_result.adversarial_flag:
            signals.append(SignalOutput(
                tool_name=SignalNames.OCKHAM_ADVERSARIAL_FLAG,
                value=min(
                    Fraction(1),
                    penalty_result.penalty / Fraction(3, 1)
                ),
                z_score=Fraction(0),
                confidence=Fraction(85, 100),
                metadata={
                    "raw_cost":       str(penalty_result.raw_cost),
                    "penalty":        str(penalty_result.penalty),
                    "adjusted_cost":  str(penalty_result.adjusted_cost),
                    "trigger_reason": penalty_result.trigger_reason[:300],
                },
            ))

            signals.append(SignalOutput(
                tool_name=SignalNames.OCKHAM_PENALTY_APPLIED,
                value=Fraction(1),   # Binario: se aplicó o no
                z_score=Fraction(0),
                confidence=Fraction(1),
                metadata={
                    "penalty_magnitude": str(penalty_result.penalty),
                    "reason":            penalty_result.trigger_reason[:200],
                },
            ))

        mapping_hash = self._compute_mapping_hash("OCKHAM", signals)
        return MappingResult(
            source_module="OckhamAdversarial",
            signals=tuple(signals),
            signal_count=len(signals),
            mapping_hash=mapping_hash,
        )

    def merge_all(self, *mapping_results: MappingResult) -> list[SignalOutput]:
        """
        Combina múltiples MappingResults en una lista plana de SignalOutputs.
        Lista lista para pasar al pipeline existente.

        Detecta duplicados por tool_name y toma el de mayor confianza.
        """
        seen: dict[str, SignalOutput] = {}

        for mapping in mapping_results:
            for signal in mapping.signals:
                existing = seen.get(signal.tool_name)
                if existing is None:
                    seen[signal.tool_name] = signal
                else:
                    # Tomar el de mayor confianza
                    if signal.confidence > existing.confidence:
                        seen[signal.tool_name] = signal

        return list(seen.values())

    def compute_composite_hash(
        self, *mapping_results: MappingResult
    ) -> str:
        """
        Hash compuesto de todos los mappings.
        Para incluir en el ForensicBundle.
        """
        combined = "|".join(
            sorted(m.mapping_hash for m in mapping_results)
        )
        return hashlib.sha256(combined.encode()).hexdigest()

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _compute_mapping_hash(
        self, module: str, signals: list[SignalOutput]
    ) -> str:
        data = {
            "module":  module,
            "signals": [
                {
                    "tool":       s.tool_name,
                    "value":      str(s.value),
                    "confidence": str(s.confidence),
                }
                for s in signals
            ],
        }
        return hashlib.sha256(
            json.dumps(data, sort_keys=True).encode()
        ).hexdigest()
