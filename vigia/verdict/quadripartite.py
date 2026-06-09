# vigia/verdict/quadripartite.py
"""
Quadripartite Verdict System
=====================================
Replaces the binary MALICE/BENIGN/ABSTAIN system with
an 8-state system that captures confidence and causation.

Why it matters:
- A system that rarely says "I don't know" is overconfident
- A MALICE at 51% confidence is NOT the same as one at 95%
- For Daubert, the distinction is critical
- For the SANS analyst, the action to take depends on the level

The 8 states:
  MALICE_HIGH      → Presentable in court, immediate action
  MALICE_MEDIUM    → Requires corroboration before action
  BENIGN_HIGH      → Close the case
  BENIGN_MEDIUM    → Monitor, do not close
  ABSTAIN_CONTRADICTION → PeircePlanner oscillated — contradictory evidence
  ABSTAIN_INSUFFICIENT  → Insufficient signals — more evidence required
  ABSTAIN_DEGRADED      → System in degraded mode — unreliable
  ESCALATE         → Specialist said MALICE when majority said BENIGN
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import Enum
from fractions import Fraction
from typing import Optional


# ---------------------------------------------------------------------------
# The 8 verdict states
# ---------------------------------------------------------------------------

class VerdictState(Enum):
    """
    Quadripartite system expanded to 8 states.

    Naming:
    - _HIGH:   Confidence > 80%  — direct action
    - _MEDIUM: Confidence 60-80% — requires corroboration
    - ABSTAIN_*: Specific abstention reason
    - ESCALATE: Requires immediate human review
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
    """Action the SANS analyst must take."""
    IMMEDIATE_CONTAINMENT    = "IMMEDIATE_CONTAINMENT"
    CORROBORATE_THEN_ACT     = "CORROBORATE_THEN_ACT"
    CLOSE_CASE               = "CLOSE_CASE"
    MONITOR_30_DAYS          = "MONITOR_30_DAYS"
    GATHER_MORE_EVIDENCE     = "GATHER_MORE_EVIDENCE"
    HUMAN_REVIEW_REQUIRED    = "HUMAN_REVIEW_REQUIRED"
    RERUN_FULL_CAPABILITIES  = "RERUN_FULL_CAPABILITIES"


# ---------------------------------------------------------------------------
# Configuration for each state
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class VerdictStateConfig:
    """Configuration and semantics for each verdict state."""
    state:            VerdictState
    display_label:    str
    action:           ActionRequired
    color_code:       str      # For the visual report
    daubert_note:     str      # Admissibility-specific note
    confidence_range: str      # Expected confidence range


VERDICT_STATE_CONFIGS: dict[VerdictState, VerdictStateConfig] = {
    VerdictState.MALICE_HIGH: VerdictStateConfig(
        state=VerdictState.MALICE_HIGH,
        display_label="🔴 MALICE — HIGH CONFIDENCE",
        action=ActionRequired.IMMEDIATE_CONTAINMENT,
        color_code="#FF0000",
        daubert_note=(
            "Verdict with >80% confidence. Full traceability available. "
            "Alternative hypotheses evaluated and discarded with documented reasoning."
        ),
        confidence_range=">80%",
    ),
    VerdictState.MALICE_MEDIUM: VerdictStateConfig(
        state=VerdictState.MALICE_MEDIUM,
        display_label="🟠 MALICE — MEDIUM CONFIDENCE",
        action=ActionRequired.CORROBORATE_THEN_ACT,
        color_code="#FF8C00",
        daubert_note=(
            "Verdict with 60-80% confidence. Pivot signals identified. "
            "Requires additional evidence before court submission."
        ),
        confidence_range="60-80%",
    ),
    VerdictState.BENIGN_HIGH: VerdictStateConfig(
        state=VerdictState.BENIGN_HIGH,
        display_label="🟢 BENIGN — HIGH CONFIDENCE",
        action=ActionRequired.CLOSE_CASE,
        color_code="#008000",
        daubert_note=(
            "Malice evidence discarded with >80% confidence. "
            "Adversarial penalty applied — benign hypothesis is not "
            "artificially simple."
        ),
        confidence_range=">80%",
    ),
    VerdictState.BENIGN_MEDIUM: VerdictStateConfig(
        state=VerdictState.BENIGN_MEDIUM,
        display_label="🟡 BENIGN — MEDIUM CONFIDENCE",
        action=ActionRequired.MONITOR_30_DAYS,
        color_code="#FFD700",
        daubert_note=(
            "Benign hypothesis leads but with reduced margin. "
            "Investigation roadmap available for pivot signals."
        ),
        confidence_range="60-80%",
    ),
    VerdictState.ABSTAIN_CONTRADICTION: VerdictStateConfig(
        state=VerdictState.ABSTAIN_CONTRADICTION,
        display_label="⚫ ABSTAIN — CONTRADICTORY EVIDENCE",
        action=ActionRequired.GATHER_MORE_EVIDENCE,
        color_code="#808080",
        daubert_note=(
            "The abductive cycle detected A→B→A oscillation between hypotheses. "
            "Available evidence is insufficient to resolve the contradiction. "
            "Epistemologically honest state — not a system failure."
        ),
        confidence_range="N/A",
    ),
    VerdictState.ABSTAIN_INSUFFICIENT: VerdictStateConfig(
        state=VerdictState.ABSTAIN_INSUFFICIENT,
        display_label="⚫ ABSTAIN — INSUFFICIENT EVIDENCE",
        action=ActionRequired.GATHER_MORE_EVIDENCE,
        color_code="#A9A9A9",
        daubert_note=(
            "Insufficient active signals to discriminate between hypotheses. "
            "Pivot signals identified — collect and re-enter into the system."
        ),
        confidence_range="<60%",
    ),
    VerdictState.ABSTAIN_DEGRADED: VerdictStateConfig(
        state=VerdictState.ABSTAIN_DEGRADED,
        display_label="🟤 ABSTAIN — DEGRADED SYSTEM",
        action=ActionRequired.RERUN_FULL_CAPABILITIES,
        color_code="#8B4513",
        daubert_note=(
            "Critical modules were disabled during analysis. "
            "Verdict is unreliable. Re-run with system in FULL_INTEGRITY mode."
        ),
        confidence_range="N/A",
    ),
    VerdictState.ESCALATE: VerdictStateConfig(
        state=VerdictState.ESCALATE,
        display_label="🚨 ESCALATE — HUMAN REVIEW REQUIRED",
        action=ActionRequired.HUMAN_REVIEW_REQUIRED,
        color_code="#800080",
        daubert_note=(
            "Specialist module dissented from the majority with high confidence. "
            "Dissent is from a 'hard-to-evade' module — difficult for an adversary "
            "to bypass. Requires senior analyst review."
        ),
        confidence_range="Variable",
    ),
}


# ---------------------------------------------------------------------------
# Verdict models
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class QuadripartiteVerdict:
    """
    Complete quadripartite verdict.
    Immutable — the verdict is a forensic fact.
    """
    state:               VerdictState
    config:              VerdictStateConfig
    raw_verdict:         str          # "MALICE" or "BENIGN" pre-classification
    confidence:          Fraction     # Verdict confidence
    stability:           Fraction     # Verdict stability (from HLT)
    adversarial_penalty: bool         # Whether Ockham penalty was applied
    dissent_present:     bool         # Whether specialist dissent occurred
    dissent_module:      Optional[str]
    integrity_level:     str          # "FULL_INTEGRITY", "DEGRADED", etc.
    abstain_reason:      Optional[str]
    pivot_signals:       tuple[str, ...]
    investigation_roadmap: tuple[str, ...]
    audit_hash:          str


# ---------------------------------------------------------------------------
# Main classifier
# ---------------------------------------------------------------------------

class QuadripartiteClassifier:
    """
    Classifies pipeline output into one of the 8 states.

    Receives:
    - raw_verdict: "MALICE" | "BENIGN" | "ABSTAIN"
    - confidence: Fraction from the decision engine
    - stability: Fraction from the HLT
    - integrity_level: str from ConfigAuditMonitor
    - dissent_info: dict from DisssentReport
    - abstain_reason: str if raw_verdict == "ABSTAIN"

    Emits:
    - QuadripartiteVerdict with state, action, and complete metadata
    """

    # Confidence thresholds as Fraction
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
        Classifies the verdict into one of the 8 states.

        Classification is deterministic — same input, same output.
        The order of checks matters:
        1. System integrity first (DEGRADED)
        2. Specialist dissent (ESCALATE)
        3. ABSTAIN with reason
        4. MALICE/BENIGN by confidence level
        """
        pivot_signals          = tuple(pivot_signals or [])
        investigation_roadmap  = tuple(investigation_roadmap or [])
        dissent_info           = dissent_info or {}

        # ------------------------------------------------------------------
        # Check 1: Degraded system → always ABSTAIN_DEGRADED
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
                    f"System in {integrity_level}. "
                    f"Verdict unreliable without full capabilities."
                ),
                pivot_signals=pivot_signals,
                roadmap=investigation_roadmap,
            )

        # ------------------------------------------------------------------
        # Check 2: Specialist dissent → ESCALATE
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
        # Check 3: ABSTAIN with specific reason
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
        # Check 4: Very low confidence → ABSTAIN_INSUFFICIENT
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
                    f"Confidence {int(confidence * 100)}% below minimum "
                    f"threshold of {int(self.MEDIUM_CONFIDENCE_THRESHOLD * 100)}%."
                ),
                pivot_signals=pivot_signals,
                roadmap=investigation_roadmap,
            )

        # ------------------------------------------------------------------
        # Check 5: MALICE by confidence level
        # ------------------------------------------------------------------
        if raw_verdict == "MALICE":
            # Penalize if stability is low — margin is small
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
        # Check 6: BENIGN by confidence level
        # ------------------------------------------------------------------
        if raw_verdict == "BENIGN":
            effective_confidence = self._adjust_for_stability(
                confidence, stability
            )

            # BENIGN with active adversarial penalty is more reliable —
            # the system verified that simplicity is not artificial
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

        # Fallback — should never reach here
        return self._build_verdict(
            state=VerdictState.ABSTAIN_INSUFFICIENT,
            raw_verdict=raw_verdict,
            confidence=confidence,
            stability=stability,
            adversarial_penalty=adversarial_penalty,
            dissent_info=dissent_info,
            integrity_level=integrity_level,
            abstain_reason=f"Unrecognized raw verdict: '{raw_verdict}'",
            pivot_signals=pivot_signals,
            roadmap=investigation_roadmap,
        )

    def _adjust_for_stability(
        self, confidence: Fraction, stability: Fraction
    ) -> Fraction:
        """
        Adjusts confidence by verdict stability.

        A verdict won by a small margin has lower effective confidence
        than one won by a wide margin.

        effective = confidence × (0.5 + stability × 0.5)
        All in Fraction.
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
        Renders the verdict for the forensic report.
        Structured format — consumable by OpenWebUI and exporters.
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
        """Executive summary in natural language for the SANS analyst."""
        conf_pct = int(verdict.confidence * 100)

        summaries = {
            VerdictState.MALICE_HIGH: (
                f"VIGÍA determines with {conf_pct}% confidence that this "
                f"evidence indicates malicious activity. "
                f"{'Adversarial penalty applied — the benign hypothesis was evaluated and discarded.' if verdict.adversarial_penalty else ''} "
                f"Recommended action: immediate containment."
            ),
            VerdictState.MALICE_MEDIUM: (
                f"Malice indicators with {conf_pct}% confidence. "
                f"Margin over alternative hypothesis is narrow. "
                f"Seek pivot signals before action: "
                f"{', '.join(verdict.pivot_signals[:2]) if verdict.pivot_signals else 'see roadmap'}."
            ),
            VerdictState.BENIGN_HIGH: (
                f"Benign activity with {conf_pct}% confidence. "
                f"{'Adversarial penalty evaluated — the benign explanation is not artificially simple.' if verdict.adversarial_penalty else ''} "
                f"Case may be closed."
            ),
            VerdictState.BENIGN_MEDIUM: (
                f"Probably benign activity ({conf_pct}%) but with "
                f"alternative hypotheses within margin. "
                f"Monitor for 30 days. Pivot signals: "
                f"{', '.join(verdict.pivot_signals[:2]) if verdict.pivot_signals else 'see roadmap'}."
            ),
            VerdictState.ABSTAIN_CONTRADICTION: (
                "The system detected contradictory evidence — hypotheses A and B "
                "are equally valid with the available evidence. "
                "Collect additional evidence. This is the correct behavior "
                "in the face of genuine forensic ambiguity."
            ),
            VerdictState.ABSTAIN_INSUFFICIENT: (
                f"Insufficient signals for a reliable verdict (confidence: {conf_pct}%). "
                f"See investigation roadmap for specific signals to pursue."
            ),
            VerdictState.ABSTAIN_DEGRADED: (
                f"⚠️ UNRELIABLE ANALYSIS: System operated in {verdict.integrity_level}. "
                f"Re-run with all modules active."
            ),
            VerdictState.ESCALATE: (
                f"⚠️ ESCALATION REQUIRED: Specialist module "
                f"'{verdict.dissent_module}' dissents from the majority. "
                f"This module is difficult for adversaries to evade. "
                f"Senior analyst review required."
            ),
        }

        return summaries.get(verdict.state, "Verdict generated. See details.")
