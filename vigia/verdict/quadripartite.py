# vigia/verdict/quadripartite.py
"""
Sistema de Veredicto Cuatripartito
=====================================
Reemplaza el sistema binario MALICE/BENIGN/ABSTAIN con
un sistema de 8 estados que captura confianza y causa.

Por qué importa:
- Un sistema que raramente dice "no sé" está sobreconfiado
- Un MALICE con 51% de confianza NO es lo mismo que uno con 95%
- Para Daubert, la distinción es crítica
- Para el analista SANS, la acción a tomar depende del nivel

Los 8 estados:
  MALICE_HIGH      → Presentable en tribunal, acción inmediata
  MALICE_MEDIUM    → Requiere corroboración antes de acción
  BENIGN_HIGH      → Cerrar el caso
  BENIGN_MEDIUM    → Monitorear, no cerrar
  ABSTAIN_CONTRADICTION → PeircePlanner osciló — evidencia contradictoria
  ABSTAIN_INSUFFICIENT  → Señales insuficientes — más evidencia requerida
  ABSTAIN_DEGRADED      → Sistema en modo degradado — no confiable
  ESCALATE         → Especialista dijo MALICE cuando mayoría dijo BENIGN
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import Enum
from fractions import Fraction
from typing import Optional


# ---------------------------------------------------------------------------
# Los 8 estados del veredicto
# ---------------------------------------------------------------------------

class VerdictState(Enum):
    """
    Sistema cuatripartito expandido a 8 estados.

    Nomenclatura:
    - _HIGH:   Confianza > 80%  — acción directa
    - _MEDIUM: Confianza 60-80% — requiere corroboración
    - ABSTAIN_*: Razón específica de abstención
    - ESCALATE: Requiere revisión humana inmediata
    """
    MALICE_HIGH              = "MALICE_HIGH"
    MALICE_MEDIUM            = "MALICE_MEDIUM"
    BENIGN_HIGH              = "BENIGN_HIGH"
    BENIGN_MEDIUM            = "BENIGN_MEDIUM"
    ABSTAIN_CONTRADICTION    = "ABSTAIN_CONTRADICTION"
    ABSTAIN_INSUFFICIENT     = "ABSTAIN_INSUFFICIENT"
    ABSTAIN_DEGRADED         = "ABSTAIN_DEGRADED"
    ESCALATE                 = "ESCALATE"


class ActionRequired(Enum):
    """Acción que el analista SANS debe tomar."""
    IMMEDIATE_CONTAINMENT    = "IMMEDIATE_CONTAINMENT"
    CORROBORATE_THEN_ACT     = "CORROBORATE_THEN_ACT"
    CLOSE_CASE               = "CLOSE_CASE"
    MONITOR_30_DAYS          = "MONITOR_30_DAYS"
    GATHER_MORE_EVIDENCE     = "GATHER_MORE_EVIDENCE"
    HUMAN_REVIEW_REQUIRED    = "HUMAN_REVIEW_REQUIRED"
    RERUN_FULL_CAPABILITIES  = "RERUN_FULL_CAPABILITIES"


# ---------------------------------------------------------------------------
# Configuración de cada estado
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class VerdictStateConfig:
    """Configuración y semántica de cada estado del veredicto."""
    state:            VerdictState
    display_label:    str
    action:           ActionRequired
    color_code:       str      # Para el reporte visual
    daubert_note:     str      # Nota específica para admisibilidad
    confidence_range: str      # Rango de confianza esperado


VERDICT_STATE_CONFIGS: dict[VerdictState, VerdictStateConfig] = {
    VerdictState.MALICE_HIGH: VerdictStateConfig(
        state=VerdictState.MALICE_HIGH,
        display_label="🔴 MALICE — ALTA CONFIANZA",
        action=ActionRequired.IMMEDIATE_CONTAINMENT,
        color_code="#FF0000",
        daubert_note=(
            "Veredicto con confianza >80%. Trazabilidad completa disponible. "
            "Hipótesis alternativas evaluadas y descartadas con razón documentada."
        ),
        confidence_range=">80%",
    ),
    VerdictState.MALICE_MEDIUM: VerdictStateConfig(
        state=VerdictState.MALICE_MEDIUM,
        display_label="🟠 MALICE — CONFIANZA MEDIA",
        action=ActionRequired.CORROBORATE_THEN_ACT,
        color_code="#FF8C00",
        daubert_note=(
            "Veredicto con confianza 60-80%. Señales pivot identificadas. "
            "Requiere evidencia adicional antes de uso en tribunal."
        ),
        confidence_range="60-80%",
    ),
    VerdictState.BENIGN_HIGH: VerdictStateConfig(
        state=VerdictState.BENIGN_HIGH,
        display_label="🟢 BENIGN — ALTA CONFIANZA",
        action=ActionRequired.CLOSE_CASE,
        color_code="#008000",
        daubert_note=(
            "Evidencia de malicia descartada con >80% de confianza. "
            "Penalización adversarial aplicada — hipótesis benigna no es "
            "artificialmente simple."
        ),
        confidence_range=">80%",
    ),
    VerdictState.BENIGN_MEDIUM: VerdictStateConfig(
        state=VerdictState.BENIGN_MEDIUM,
        display_label="🟡 BENIGN — CONFIANZA MEDIA",
        action=ActionRequired.MONITOR_30_DAYS,
        color_code="#FFD700",
        daubert_note=(
            "Hipótesis benigna lidera pero con margen reducido. "
            "Roadmap de investigación disponible para señales pivot."
        ),
        confidence_range="60-80%",
    ),
    VerdictState.ABSTAIN_CONTRADICTION: VerdictStateConfig(
        state=VerdictState.ABSTAIN_CONTRADICTION,
        display_label="⚫ ABSTAIN — EVIDENCIA CONTRADICTORIA",
        action=ActionRequired.GATHER_MORE_EVIDENCE,
        color_code="#808080",
        daubert_note=(
            "El ciclo abductivo detectó oscilación A→B→A entre hipótesis. "
            "La evidencia disponible es insuficiente para resolver la contradicción. "
            "Estado epistemológicamente honesto — no es fallo del sistema."
        ),
        confidence_range="N/A",
    ),
    VerdictState.ABSTAIN_INSUFFICIENT: VerdictStateConfig(
        state=VerdictState.ABSTAIN_INSUFFICIENT,
        display_label="⚫ ABSTAIN — EVIDENCIA INSUFICIENTE",
        action=ActionRequired.GATHER_MORE_EVIDENCE,
        color_code="#A9A9A9",
        daubert_note=(
            "Señales activas insuficientes para discriminar entre hipótesis. "
            "Señales pivot identificadas — recolectar y reingresar al sistema."
        ),
        confidence_range="<60%",
    ),
    VerdictState.ABSTAIN_DEGRADED: VerdictStateConfig(
        state=VerdictState.ABSTAIN_DEGRADED,
        display_label="🟤 ABSTAIN — SISTEMA DEGRADADO",
        action=ActionRequired.RERUN_FULL_CAPABILITIES,
        color_code="#8B4513",
        daubert_note=(
            "Módulos críticos estaban desactivados durante el análisis. "
            "Veredicto no confiable. Reejecutar con sistema en FULL_INTEGRITY."
        ),
        confidence_range="N/A",
    ),
    VerdictState.ESCALATE: VerdictStateConfig(
        state=VerdictState.ESCALATE,
        display_label="🚨 ESCALATE — REVISIÓN HUMANA REQUERIDA",
        action=ActionRequired.HUMAN_REVIEW_REQUIRED,
        color_code="#800080",
        daubert_note=(
            "Módulo especialista disintió de la mayoría con alta confianza. "
            "El disenso es de módulo 'hard-to-evade' — difícil de evadir "
            "por un adversario. Requiere revisión de analista senior."
        ),
        confidence_range="Variable",
    ),
}


# ---------------------------------------------------------------------------
# Modelos del veredicto
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class QuadripartiteVerdict:
    """
    Veredicto cuatripartito completo.
    Inmutable — el veredicto es un hecho forense.
    """
    state:               VerdictState
    config:              VerdictStateConfig
    raw_verdict:         str          # "MALICE" o "BENIGN" pre-clasificación
    confidence:          Fraction     # Confianza del veredicto
    stability:           Fraction     # Estabilidad del veredicto (del HLT)
    adversarial_penalty: bool         # Si se aplicó penalización Ockham
    dissent_present:     bool         # Si hubo disenso de especialista
    dissent_module:      Optional[str]
    integrity_level:     str          # "FULL_INTEGRITY", "DEGRADED", etc.
    abstain_reason:      Optional[str]
    pivot_signals:       tuple[str, ...]
    investigation_roadmap: tuple[str, ...]
    audit_hash:          str


# ---------------------------------------------------------------------------
# Clasificador principal
# ---------------------------------------------------------------------------

class QuadripartiteClassifier:
    """
    Clasifica el output del pipeline en uno de los 8 estados.

    Recibe:
    - raw_verdict: "MALICE" | "BENIGN" | "ABSTAIN"
    - confidence: Fraction del motor de decisión
    - stability: Fraction del HLT
    - integrity_level: str del ConfigAuditMonitor
    - dissent_info: dict del DisssentReport
    - abstain_reason: str si raw_verdict == "ABSTAIN"

    Emite:
    - QuadripartiteVerdict con estado, acción y metadata completa
    """

    # Umbrales de confianza como Fraction
    HIGH_CONFIDENCE_THRESHOLD:   Fraction = Fraction(4, 5)    # 80%
    MEDIUM_CONFIDENCE_THRESHOLD: Fraction = Fraction(3, 5)    # 60%

    def classify(
        self,
        raw_verdict:     str,
        confidence:      Fraction,
        stability:       Fraction,
        integrity_level: str,
        dissent_info:    Optional[dict] = None,
        abstain_reason:  Optional[str] = None,
        pivot_signals:   list[str] = None,
        investigation_roadmap: list[str] = None,
        adversarial_penalty: bool = False,
    ) -> QuadripartiteVerdict:
        """
        Clasifica el veredicto en uno de los 8 estados.

        La clasificación es determinista — mismo input, mismo output.
        El orden de los checks importa:
        1. Integridad del sistema primero (DEGRADED)
        2. Disenso de especialista (ESCALATE)
        3. ABSTAIN con razón
        4. MALICE/BENIGN por nivel de confianza
        """
        pivot_signals          = tuple(pivot_signals or [])
        investigation_roadmap  = tuple(investigation_roadmap or [])
        dissent_info           = dissent_info or {}

        # ------------------------------------------------------------------
        # Check 1: Sistema degradado → siempre ABSTAIN_DEGRADED
        # ------------------------------------------------------------------
        if integrity_level in ("INTEGRITY_COMPROMISED", "DEGRADED_MODE"):
            state = VerdictState.ABSTAIN_DEGRADED
            return self._build_verdict(
                state=state,
                raw_verdict=raw_verdict,
                confidence=confidence,
                stability=stability,
                adversarial_penalty=adversarial_penalty,
                dissent_info=dissent_info,
                integrity_level=integrity_level,
                abstain_reason=(
                    f"Sistema en {integrity_level}. "
                    f"Veredicto no confiable sin capacidades completas."
                ),
                pivot_signals=pivot_signals,
                roadmap=investigation_roadmap,
            )

        # ------------------------------------------------------------------
        # Check 2: Disenso de especialista → ESCALATE
        # ------------------------------------------------------------------
        if dissent_info.get("escalation_required", False):
            state = VerdictState.ESCALATE
            return self._build_verdict(
                state=state,
                raw_verdict=raw_verdict,
                confidence=confidence,
                stability=stability,
                adversarial_penalty=adversarial_penalty,
                dissent_info=dissent_info,
                integrity_level=integrity_level,
                abstain_reason=None,
                pivot_signals=pivot_signals,
                roadmap=investigation_roadmap,
            )

        # ------------------------------------------------------------------
        # Check 3: ABSTAIN con razón específica
        # ------------------------------------------------------------------
        if raw_verdict == "ABSTAIN":
            if abstain_reason and "OSCIL" in abstain_reason.upper():
                state = VerdictState.ABSTAIN_CONTRADICTION
            elif confidence < self.MEDIUM_CONFIDENCE_THRESHOLD:
                state = VerdictState.ABSTAIN_INSUFFICIENT
            else:
                state = VerdictState.ABSTAIN_INSUFFICIENT

            return self._build_verdict(
                state=state,
                raw_verdict=raw_verdict,
                confidence=confidence,
                stability=stability,
                adversarial_penalty=adversarial_penalty,
                dissent_info=dissent_info,
                integrity_level=integrity_level,
                abstain_reason=abstain_reason,
                pivot_signals=pivot_signals,
                roadmap=investigation_roadmap,
            )

        # ------------------------------------------------------------------
        # Check 4: Confianza muy baja → ABSTAIN_INSUFFICIENT
        # ------------------------------------------------------------------
        if confidence < self.MEDIUM_CONFIDENCE_THRESHOLD:
            return self._build_verdict(
                state=VerdictState.ABSTAIN_INSUFFICIENT,
                raw_verdict=raw_verdict,
                confidence=confidence,
                stability=stability,
                adversarial_penalty=adversarial_penalty,
                dissent_info=dissent_info,
                integrity_level=integrity_level,
                abstain_reason=(
                    f"Confianza {int(confidence * 100)}% menor al umbral "
                    f"mínimo de {int(self.MEDIUM_CONFIDENCE_THRESHOLD * 100)}%."
                ),
                pivot_signals=pivot_signals,
                roadmap=investigation_roadmap,
            )

        # ------------------------------------------------------------------
        # Check 5: MALICE por nivel de confianza
        # ------------------------------------------------------------------
        if raw_verdict == "MALICE":
            # Penalizar si la estabilidad es baja — el margen es pequeño
            effective_confidence = self._adjust_for_stability(
                confidence, stability
            )

            if effective_confidence >= self.HIGH_CONFIDENCE_THRESHOLD:
                state = VerdictState.MALICE_HIGH
            else:
                state = VerdictState.MALICE_MEDIUM

            return self._build_verdict(
                state=state,
                raw_verdict=raw_verdict,
                confidence=effective_confidence,
                stability=stability,
                adversarial_penalty=adversarial_penalty,
                dissent_info=dissent_info,
                integrity_level=integrity_level,
                abstain_reason=None,
                pivot_signals=pivot_signals,
                roadmap=investigation_roadmap,
            )

        # ------------------------------------------------------------------
        # Check 6: BENIGN por nivel de confianza
        # ------------------------------------------------------------------
        if raw_verdict == "BENIGN":
            effective_confidence = self._adjust_for_stability(
                confidence, stability
            )

            # BENIGN con penalización adversarial activa es más confiable —
            # el sistema verificó que la simplicidad no es artificial
            if adversarial_penalty:
                effective_confidence = min(
                    Fraction(1),
                    effective_confidence + Fraction(1, 20)  # +5% bonus
                )

            if effective_confidence >= self.HIGH_CONFIDENCE_THRESHOLD:
                state = VerdictState.BENIGN_HIGH
            else:
                state = VerdictState.BENIGN_MEDIUM

            return self._build_verdict(
                state=state,
                raw_verdict=raw_verdict,
                confidence=effective_confidence,
                stability=stability,
                adversarial_penalty=adversarial_penalty,
                dissent_info=dissent_info,
                integrity_level=integrity_level,
                abstain_reason=None,
                pivot_signals=pivot_signals,
                roadmap=investigation_roadmap,
            )

        # Fallback — nunca debería llegar aquí
        return self._build_verdict(
            state=VerdictState.ABSTAIN_INSUFFICIENT,
            raw_verdict=raw_verdict,
            confidence=confidence,
            stability=stability,
            adversarial_penalty=adversarial_penalty,
            dissent_info=dissent_info,
            integrity_level=integrity_level,
            abstain_reason=f"Veredicto raw no reconocido: '{raw_verdict}'",
            pivot_signals=pivot_signals,
            roadmap=investigation_roadmap,
        )

    def _adjust_for_stability(
        self, confidence: Fraction, stability: Fraction
    ) -> Fraction:
        """
        Ajusta la confianza por la estabilidad del veredicto.

        Un veredicto ganado por margen pequeño tiene confianza efectiva
        menor que uno ganado por margen amplio.

        effective = confidence × (0.5 + stability × 0.5)
        Todo en Fraction.
        """
        stability_factor = Fraction(1, 2) + stability * Fraction(1, 2)
        return confidence * stability_factor

    def _build_verdict(
        self,
        state:           VerdictState,
        raw_verdict:     str,
        confidence:      Fraction,
        stability:       Fraction,
        adversarial_penalty: bool,
        dissent_info:    dict,
        integrity_level: str,
        abstain_reason:  Optional[str],
        pivot_signals:   tuple[str, ...],
        roadmap:         tuple[str, ...],
    ) -> QuadripartiteVerdict:
        config = VERDICT_STATE_CONFIGS[state]

        dissent_present = bool(dissent_info.get("escalation_required", False))
        dissent_module  = dissent_info.get("dissenting_module")

        audit_data = {
            "state":          state.value,
            "raw_verdict":    raw_verdict,
            "confidence":     str(confidence),
            "stability":      str(stability),
            "integrity":      integrity_level,
            "adversarial":    adversarial_penalty,
            "dissent":        dissent_present,
        }
        audit_hash = hashlib.sha256(
            json.dumps(audit_data, sort_keys=True).encode()
        ).hexdigest()

        return QuadripartiteVerdict(
            state=state,
            config=config,
            raw_verdict=raw_verdict,
            confidence=confidence,
            stability=stability,
            adversarial_penalty=adversarial_penalty,
            dissent_present=dissent_present,
            dissent_module=dissent_module,
            integrity_level=integrity_level,
            abstain_reason=abstain_reason,
            pivot_signals=pivot_signals,
            investigation_roadmap=roadmap,
            audit_hash=audit_hash,
        )

    def render_for_report(self, verdict: QuadripartiteVerdict) -> dict:
        """
        Renderiza el veredicto para el reporte forense.
        Formato estructurado — consumible por OpenWebUI y exporters.
        """
        conf_pct      = int(verdict.confidence * 100)
        stability_pct = int(verdict.stability * 100)

        return {
            "verdict_state":    verdict.state.value,
            "display_label":    verdict.config.display_label,
            "action_required":  verdict.config.action.value,
            "confidence_pct":   conf_pct,
            "stability_pct":    stability_pct,
            "daubert_note":     verdict.config.daubert_note,
            "adversarial_penalty_applied": verdict.adversarial_penalty,
            "dissent_present":  verdict.dissent_present,
            "dissent_module":   verdict.dissent_module,
            "integrity_level":  verdict.integrity_level,
            "abstain_reason":   verdict.abstain_reason,
            "pivot_signals":    list(verdict.pivot_signals)[:5],
            "investigation_roadmap": list(verdict.investigation_roadmap)[:10],
            "audit_hash":       verdict.audit_hash,
            "analyst_summary": self._build_analyst_summary(verdict),
        }

    def _build_analyst_summary(self, verdict: QuadripartiteVerdict) -> str:
        """Resumen ejecutivo en lenguaje natural para el analista SANS."""
        conf_pct = int(verdict.confidence * 100)

        summaries = {
            VerdictState.MALICE_HIGH: (
                f"VIGÍA determina con {conf_pct}% de confianza que esta "
                f"evidencia indica actividad maliciosa. "
                f"{'Penalización adversarial aplicada — la hipótesis benigna fue evaluada y descartada.' if verdict.adversarial_penalty else ''} "
                f"Acción recomendada: contención inmediata."
            ),
            VerdictState.MALICE_MEDIUM: (
                f"Indicadores de malicia con {conf_pct}% de confianza. "
                f"Margen sobre hipótesis alternativa es reducido. "
                f"Buscar señales pivot antes de acción: "
                f"{', '.join(verdict.pivot_signals[:2]) if verdict.pivot_signals else 'ver roadmap'}."
            ),
            VerdictState.BENIGN_HIGH: (
                f"Actividad benigna con {conf_pct}% de confianza. "
                f"{'Penalización adversarial evaluada — la explicación benigna no es artificialmente simple.' if verdict.adversarial_penalty else ''} "
                f"Caso puede cerrarse."
            ),
            VerdictState.BENIGN_MEDIUM: (
                f"Actividad probablemente benigna ({conf_pct}%) pero con "
                f"hipótesis alternativas dentro del margen. "
                f"Monitorear 30 días. Señales pivot: "
                f"{', '.join(verdict.pivot_signals[:2]) if verdict.pivot_signals else 'ver roadmap'}."
            ),
            VerdictState.ABSTAIN_CONTRADICTION: (
                "El sistema detectó evidencia contradictoria — hipótesis A y B "
                "son igualmente válidas con la evidencia disponible. "
                "Recolectar evidencia adicional. Este es el comportamiento correcto "
                "ante ambigüedad forense real."
            ),
            VerdictState.ABSTAIN_INSUFFICIENT: (
                f"Señales insuficientes para veredicto confiable (confianza: {conf_pct}%). "
                f"Ver roadmap de investigación para señales específicas a buscar."
            ),
            VerdictState.ABSTAIN_DEGRADED: (
                f"⚠️ ANÁLISIS NO CONFIABLE: Sistema operó en {verdict.integrity_level}. "
                f"Reejecutar con todos los módulos activos."
            ),
            VerdictState.ESCALATE: (
                f"⚠️ ESCALACIÓN REQUERIDA: El módulo especialista "
                f"'{verdict.dissent_module}' disiente de la mayoría. "
                f"Este módulo es difícil de evadir por adversarios. "
                f"Revisión de analista senior requerida."
            ),
        }

        return summaries.get(verdict.state, "Veredicto generado. Ver detalles.")
