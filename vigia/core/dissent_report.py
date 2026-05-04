"""
vigia/core/dissent_report.py
=============================
Reporte de disenso entre módulos de detección forense para VIGÍA.

Principio: Un analista SANS ante un APT sofisticado no puede ignorar
la señal minoritaria de un módulo especialista. 9 módulos que dicen
BENIGN + 1 módulo behavioral que dice MALICE = escalación requerida.

El consenso artificialmente alto en BENIGN es él mismo una señal de evasión.

Fixes de Kimi aplicados:
- Display usa int(confidence * 100) — sin float, sin round()
- Separador estricto entre módulos que votan y módulos que abstienen
- noise_threshold y critical_dissent_threshold como Fraction

Invariantes:
- Todo scoring usa fractions.Fraction
- display_confidence() usa int() truncado, nunca round()
- DissentReport es generado deterministamente del mismo input
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from enum import Enum
from fractions import Fraction
from typing import Optional


class ModuleVerdict(Enum):
    MALICIOUS = "malicious"
    SUSPICIOUS = "suspicious"
    BENIGN    = "benign"
    ABSTAIN   = "abstain"


# Pesos de severidad — Fraction, sin floats
_SEVERITY_WEIGHT: dict[ModuleVerdict, Fraction] = {
    ModuleVerdict.MALICIOUS:  Fraction(10, 10),
    ModuleVerdict.SUSPICIOUS: Fraction(5,  10),
    ModuleVerdict.BENIGN:     Fraction(0,  10),
    ModuleVerdict.ABSTAIN:    Fraction(0,  10),
}

# Módulos clasificados por especialización forense
_MODULE_SPECIALIZATION: dict[str, str] = {
    "CAIE":              "Cross-artifact injection and evasion",
    "TrustFusion":       "Multi-signal trust correlation",
    "PeircePlanner":     "Abductive structural reasoning",
    "PDFDual":           "PDF parser exploit detection",
    "MemoryScanner":     "Volatile memory artifacts",
    "NetworkAnalyzer":   "C2 and exfiltration patterns",
    "RegistryAuditor":   "Windows registry persistence",
    "LogCorrelator":     "Temporal event correlation",
    "SyscallTracer":     "Behavioral system call analysis",
    "EntropyDetector":   "High-entropy / packer detection",
    "TemporalForensics": "Anachronism and timeline analysis",
    "OckhamAdversarial": "Adversarial simplicity detection",
}

# Módulos que son difíciles de evadir — su disenso es señal fuerte
_HARD_TO_EVADE: frozenset[str] = frozenset({
    "SyscallTracer",
    "MemoryScanner",
    "EntropyDetector",
    "TemporalForensics",
    "OckhamAdversarial",
})


@dataclass
class ModuleOpinion:
    module_name:   str
    verdict:       ModuleVerdict
    confidence:    Fraction      # 0..1 como Fraction
    reasoning:     str
    evidence_refs: list[str] = field(default_factory=list)
    mitre_ttps:    list[str] = field(default_factory=list)
    anomaly_type:  Optional[str] = None

    def display_confidence_pct(self) -> int:
        """Porcentaje entero — int() truncado, nunca round()."""
        return int(self.confidence * 100)


@dataclass
class DissentSignal:
    """Opinión minoritaria que no debe silenciarse."""
    dissenting_module:  str
    dissenting_verdict: ModuleVerdict
    majority_verdict:   ModuleVerdict
    dissent_weight:     Fraction
    specialization:     str
    reasoning:          str
    why_this_matters:   str
    evidence_refs:      list[str]
    is_hard_to_evade:   bool


@dataclass
class DissentReport:
    majority_verdict:    ModuleVerdict
    majority_confidence: Fraction
    total_modules:       int
    voting_modules:      int
    consensus_level:     Fraction
    dissent_signals:     list[DissentSignal]
    noise_filtered:      list[str]
    escalation_required: bool
    suspicious_consensus: bool
    forensic_summary:    str
    audit_hash:          str

    def display_majority_pct(self) -> int:
        """Kimi fix: int() truncado para reproducibilidad."""
        return int(self.majority_confidence * 100)

    def display_consensus_pct(self) -> int:
        return int(self.consensus_level * 100)


# ─── Funciones internas ───────────────────────────────────────────────────────

def _compute_majority(
    opinions: list[ModuleOpinion],
) -> tuple[ModuleVerdict, Fraction]:
    vote_counts: dict[ModuleVerdict, Fraction] = {v: Fraction(0) for v in ModuleVerdict}

    for op in opinions:
        if op.verdict == ModuleVerdict.ABSTAIN:
            continue
        weight = op.confidence * _SEVERITY_WEIGHT[op.verdict]
        vote_counts[op.verdict] += weight

    total = sum(vote_counts.values())
    if total == Fraction(0):
        return ModuleVerdict.ABSTAIN, Fraction(0)

    majority = max(vote_counts, key=lambda v: vote_counts[v])
    return majority, vote_counts[majority] / total


def _is_noise(
    opinion:         ModuleOpinion,
    noise_threshold: Fraction,
) -> bool:
    """
    Filtra disensos de bajo valor forense.
    Un disenso es ruido si:
    - Confianza < noise_threshold
    - Módulo sin especialización documentada
    - Sin evidencia ni tipo de anomalía
    """
    if opinion.confidence < noise_threshold:
        return True
    if opinion.module_name not in _MODULE_SPECIALIZATION:
        return True
    if not opinion.evidence_refs and not opinion.anomaly_type and not opinion.mitre_ttps:
        return True
    return False


def _why_this_matters(opinion: ModuleOpinion, majority: ModuleVerdict) -> str:
    spec = _MODULE_SPECIALIZATION.get(opinion.module_name, "generic analysis")
    hard = opinion.module_name in _HARD_TO_EVADE

    if majority == ModuleVerdict.BENIGN and opinion.verdict == ModuleVerdict.MALICIOUS:
        return (
            f"CRITICAL SIGNAL: {opinion.module_name} ({spec}) detected malice "
            f"while majority voted benign. "
            f"{'This module is hard to evade — ' if hard else ''}"
            f"Pattern consistent with threats designed to evade majority analysis. "
            f"Manual review required."
        )
    if majority == ModuleVerdict.BENIGN and opinion.verdict == ModuleVerdict.SUSPICIOUS:
        return (
            f"{opinion.module_name} ({spec}) detected anomaly without classifying as malicious. "
            f"In low-signal attacks (APT, living-off-the-land), "
            f"this is frequently the only visible signal in the initial phase."
        )
    if majority == ModuleVerdict.SUSPICIOUS and opinion.verdict == ModuleVerdict.MALICIOUS:
        return (
            f"{opinion.module_name} ({spec}) escalates verdict to malicious. "
            f"If this module specializes in the detected attack vector, "
            f"the majority verdict is conservative. Consider escalation."
        )
    return (
        f"{opinion.module_name} dissents. "
        f"Review reasoning: {opinion.reasoning[:200]}"
    )


def _is_suspicious_consensus(
    majority:          ModuleVerdict,
    consensus_level:   Fraction,
    dissent_signals:   list[DissentSignal],
) -> bool:
    """
    Detecta consenso artificialmente alto que podría indicar evasión.
    APT scenario: atacante evade 9/10 sensores pero 1 behavioral detecta.
    El consenso alto (90%) en BENIGN + disenso de hard-to-evade = sospechoso.
    """
    if majority != ModuleVerdict.BENIGN:
        return False
    if consensus_level <= Fraction(8, 10):
        return False
    return any(s.is_hard_to_evade for s in dissent_signals)


# ─── API pública ──────────────────────────────────────────────────────────────

def generate_dissent_report(
    opinions:                   list[ModuleOpinion],
    noise_threshold:            Fraction = Fraction(2, 10),
    critical_dissent_threshold: Fraction = Fraction(6, 10),
) -> DissentReport:
    """
    Genera reporte de disenso. Parámetros como Fraction para determinismo.

    noise_threshold:            confianza mínima para reportar disenso
    critical_dissent_threshold: confianza desde la que se requiere escalación
    """
    majority, majority_conf = _compute_majority(opinions)

    voting   = [o for o in opinions if o.verdict != ModuleVerdict.ABSTAIN]
    maj_count = sum(1 for o in voting if o.verdict == majority)
    consensus = Fraction(maj_count, len(voting)) if voting else Fraction(0)

    dissent_signals: list[DissentSignal] = []
    noise_filtered:  list[str] = []
    escalation = False

    for op in opinions:
        if op.verdict == majority or op.verdict == ModuleVerdict.ABSTAIN:
            continue

        if _is_noise(op, noise_threshold):
            noise_filtered.append(
                f"{op.module_name} (confidence={op.display_confidence_pct()}%, noise-filtered)"
            )
            continue

        weight = op.confidence * _SEVERITY_WEIGHT[op.verdict]

        # Escalación: especialista con alta confianza dice MALICIOUS cuando mayoría dice BENIGN
        if (
            op.verdict == ModuleVerdict.MALICIOUS
            and majority == ModuleVerdict.BENIGN
            and op.confidence >= critical_dissent_threshold
        ):
            escalation = True

        dissent_signals.append(DissentSignal(
            dissenting_module=op.module_name,
            dissenting_verdict=op.verdict,
            majority_verdict=majority,
            dissent_weight=weight,
            specialization=_MODULE_SPECIALIZATION.get(op.module_name, "unspecialized"),
            reasoning=op.reasoning,
            why_this_matters=_why_this_matters(op, majority),
            evidence_refs=op.evidence_refs,
            is_hard_to_evade=op.module_name in _HARD_TO_EVADE,
        ))

    # Ordenar por peso descendente
    dissent_signals.sort(key=lambda s: s.dissent_weight, reverse=True)

    suspicious = _is_suspicious_consensus(majority, consensus, dissent_signals)

    if suspicious:
        final_majority = ModuleVerdict.ABSTAIN
        summary = (
            f"SUSPICIOUS CONSENSUS: {majority.value} verdict with "
            f"{int(consensus * 100)}% agreement, but hard-to-evade modules dissented. "
            f"Pattern consistent with designed evasion. Manual review required."
        )
    elif escalation:
        final_majority = majority
        summary = (
            f"ESCALATION REQUIRED: majority={majority.value} but "
            f"{sum(1 for s in dissent_signals if s.dissenting_verdict == ModuleVerdict.MALICIOUS)} "
            f"specialist module(s) detected malice with high confidence."
        )
    elif dissent_signals:
        final_majority = majority
        summary = (
            f"Verdict={majority.value} (consensus={int(consensus * 100)}%). "
            f"{len(dissent_signals)} dissent signal(s) recorded for review."
        )
    else:
        final_majority = majority
        summary = (
            f"Verdict={majority.value} consensus={int(consensus * 100)}%. "
            f"No significant dissent."
        )

    # Audit hash
    content = (
        f"{final_majority.value}|{majority_conf}|"
        f"{[s.dissenting_module + s.dissenting_verdict.value for s in dissent_signals]}"
    )
    audit_hash = hashlib.sha256(content.encode()).hexdigest()

    return DissentReport(
        majority_verdict=final_majority,
        majority_confidence=majority_conf,
        total_modules=len(opinions),
        voting_modules=len(voting),
        consensus_level=consensus,
        dissent_signals=dissent_signals,
        noise_filtered=noise_filtered,
        escalation_required=escalation,
        suspicious_consensus=suspicious,
        forensic_summary=summary,
        audit_hash=audit_hash,
    )
