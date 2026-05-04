"""
vigia/core/causal_closure.py
=============================
Causal Closure Score para VIGÍA.

Principio (ChatGPT + Claude, Mayo 2026):
Un caso forense no es solo señales — es una historia causal coherente.
El CCS mide cuán bien los artefactos disponibles cierran causalmente
la hipótesis ganadora bajo condiciones adversariales.

Cuatro dimensiones:
  1. temporal_coherence    (TCV)  — ¿los timestamps son físicamente posibles?
  2. semantic_resonance    (CAR)  — ¿los artefactos se refieren al mismo evento?
  3. abductive_parsimony   (HLT)  — ¿la hipótesis es la más simple que explica todo?
  4. adversarial_silence   (ASD)  — ¿la ausencia de artefactos es estructural?

Uso como GATE (no solo multiplicador):
  Si CCS < GATE_THRESHOLD → veredicto máximo alcanzable = ABSTAIN
  Esto es defendible ante Daubert: alta señal + baja coherencia causal
  = perfil exacto de evidencia fabricada.

Invariantes:
  - Todo scoring usa Fraction — sin floats en lógica
  - CausalClosureResult es frozen dataclass
  - audit_hash determinista
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from fractions import Fraction
from typing import Optional


# Umbral mínimo para alcanzar MALICE_HIGH
GATE_THRESHOLD: Fraction = Fraction(5, 10)  # 50%

# Pesos de cada dimensión — suma debe ser 1
_WEIGHTS: dict[str, Fraction] = {
    "temporal_coherence":  Fraction(3, 10),
    "semantic_resonance":  Fraction(2, 10),
    "abductive_parsimony": Fraction(3, 10),
    "adversarial_silence": Fraction(2, 10),
}


@dataclass(frozen=True)
class CausalClosureResult:
    """Resultado del score de cierre causal. Inmutable."""
    temporal_coherence:    Fraction
    semantic_resonance:    Fraction
    abductive_parsimony:   Fraction
    adversarial_silence:   Fraction
    causal_closure_score:  Fraction
    gate_passed:           bool
    verdict_cap:           str        # "MALICE_HIGH" | "ABSTAIN"
    audit_hash:            str
    explanation:           str

    def display_pct(self) -> int:
        """Porcentaje entero — int() truncado, nunca round()."""
        return int(self.causal_closure_score * 100)


def compute_causal_closure(
    temporal_coherence:  Optional[Fraction] = None,
    semantic_resonance:  Optional[Fraction] = None,
    abductive_parsimony: Optional[Fraction] = None,
    adversarial_silence: Optional[Fraction] = None,
    gate_threshold:      Fraction = GATE_THRESHOLD,
) -> CausalClosureResult:
    """
    Calcula el Causal Closure Score desde las cuatro dimensiones.

    Cualquier dimensión no disponible se sustituye por Fraction(1,2)
    (máxima incertidumbre — ni confirma ni descarta).

    Args:
        temporal_coherence:  coherence_score del TCV (0=incoherente, 1=coherente)
        semantic_resonance:  coherence_score del CrossArtifactResonance
        abductive_parsimony: verdict_stability del HypothesisLineageTracker
        adversarial_silence: 1 - fabrication_likelihood del AdversarialSilenceDetector
        gate_threshold:      umbral mínimo para MALICE_HIGH

    Returns:
        CausalClosureResult con score y gate decision
    """
    # Sustituir None por incertidumbre máxima
    tc = temporal_coherence  if temporal_coherence  is not None else Fraction(1, 2)
    sr = semantic_resonance  if semantic_resonance  is not None else Fraction(1, 2)
    ap = abductive_parsimony if abductive_parsimony is not None else Fraction(1, 2)
    # adversarial_silence: si ASD dice fabrication_likelihood=0.8,
    # la coherencia desde ASD es 1 - 0.8 = 0.2
    as_score = adversarial_silence if adversarial_silence is not None else Fraction(1, 2)

    # Clampar cada dimensión a [0, 1]
    def _clamp(v: Fraction) -> Fraction:
        return max(Fraction(0), min(Fraction(1), v))

    tc = _clamp(tc)
    sr = _clamp(sr)
    ap = _clamp(ap)
    as_score = _clamp(as_score)

    # Score ponderado
    ccs = (
        tc       * _WEIGHTS["temporal_coherence"]
        + sr     * _WEIGHTS["semantic_resonance"]
        + ap     * _WEIGHTS["abductive_parsimony"]
        + as_score * _WEIGHTS["adversarial_silence"]
    )

    gate_passed = ccs >= gate_threshold
    verdict_cap = "MALICE_HIGH" if gate_passed else "ABSTAIN"

    explanation = _build_explanation(tc, sr, ap, as_score, ccs, gate_passed, gate_threshold)
    audit_hash  = _compute_hash(tc, sr, ap, as_score, ccs)

    return CausalClosureResult(
        temporal_coherence=tc,
        semantic_resonance=sr,
        abductive_parsimony=ap,
        adversarial_silence=as_score,
        causal_closure_score=ccs,
        gate_passed=gate_passed,
        verdict_cap=verdict_cap,
        audit_hash=audit_hash,
        explanation=explanation,
    )


def apply_ccs_to_confidence(
    raw_confidence:   Fraction,
    ccs_result:       CausalClosureResult,
    gate_threshold:   Fraction = GATE_THRESHOLD,
) -> tuple[Fraction, str]:
    """
    Aplica el CCS como multiplicador y gate al confidence raw.

    Si gate no pasa → confidence efectiva = 0, veredicto = ABSTAIN.
    Si gate pasa → confidence efectiva = raw × CCS (penaliza incoherencia).

    Returns:
        (effective_confidence, effective_verdict_cap)
    """
    if not ccs_result.gate_passed:
        return Fraction(0), "ABSTAIN"

    effective = raw_confidence * ccs_result.causal_closure_score
    return _clamp_fraction(effective), "UNRESTRICTED"


def _clamp_fraction(v: Fraction) -> Fraction:
    return max(Fraction(0), min(Fraction(1), v))


def _build_explanation(
    tc: Fraction, sr: Fraction, ap: Fraction, as_score: Fraction,
    ccs: Fraction, gate_passed: bool, threshold: Fraction,
) -> str:
    parts = [
        f"CausalClosureScore={int(ccs * 100)}%",
        f"  temporal_coherence={int(tc * 100)}% (w={_WEIGHTS['temporal_coherence']})",
        f"  semantic_resonance={int(sr * 100)}% (w={_WEIGHTS['semantic_resonance']})",
        f"  abductive_parsimony={int(ap * 100)}% (w={_WEIGHTS['abductive_parsimony']})",
        f"  adversarial_silence={int(as_score * 100)}% (w={_WEIGHTS['adversarial_silence']})",
    ]
    if gate_passed:
        parts.append(f"GATE PASSED (>= {int(threshold * 100)}%) — MALICE_HIGH reachable")
    else:
        parts.append(
            f"GATE FAILED (< {int(threshold * 100)}%) — "
            f"verdict capped at ABSTAIN. "
            f"High signal + low causal coherence = fabrication profile."
        )
    return "\n".join(parts)


def _compute_hash(
    tc: Fraction, sr: Fraction, ap: Fraction,
    as_score: Fraction, ccs: Fraction,
) -> str:
    content = json.dumps({
        "tc":  str(tc),
        "sr":  str(sr),
        "ap":  str(ap),
        "as":  str(as_score),
        "ccs": str(ccs),
    }, sort_keys=True)
    return hashlib.sha256(content.encode()).hexdigest()
