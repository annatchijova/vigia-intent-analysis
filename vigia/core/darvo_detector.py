"""
vigia/core/darvo_detector.py
DARVO Detector — asimetría de contacto actor_a vs actor_b
Alimenta consistency_score en RiskBoundedDecisionLayer

B-140 (L-029 / FW-009 Fase 1): también anota el path motor
(vigia_scorer._vigia_score) vía detect_darvo_pattern() — detección
estructurada con trazabilidad Daubert, SIN efecto en veredicto. El efecto
sobre veredicto y el veredicto relacional false_flag siguen siendo
decisiones de doctrina (KNOWN_LIMITATIONS L-029).
"""
from __future__ import annotations
from fractions import Fraction
from typing import Any, Dict, List

SURVEILLANCE_KEYWORDS = ('honeypot', 'accesos', 'server', 'log', 'stalkeo', 'php error', 'trampolin')
ZERO_CONTACT_KEYWORDS = ('cero contacto', 'zero contact', 'no contact', 'bloqueado')
_SURVEILLANCE_TYPES = ('file_metadata', 'log_entry')


def _field(artifact: Any, name: str, default: Any = None) -> Any:
    """Lee un campo de un artefacto dado como objeto O como dict (B-140).

    El path Modo 1 (EBS JSON) pasa artefactos como dicts planos; el pipeline
    pasa objetos SignalOutput. Solo getattr dejaba al detector
    estructuralmente ciego frente a dicts.
    """
    if isinstance(artifact, dict):
        return artifact.get(name, default)
    return getattr(artifact, name, default)


def detect_darvo_pattern(artifacts: List[Any]) -> Dict[str, Any]:
    """Detección estructurada de la asimetría DARVO (FW-009 Fase 1).

    Devuelve conteos, la penalidad en Fraction y los ids de los artefactos
    que dispararon (trazabilidad Daubert). Aritmética Fraction pura,
    determinista; total frente a campos malformados (str() coercion,
    metadata no-dict tratada como vacía).
    """
    surveillance_count = 0
    zero_contact_count = 0
    matched: List[str] = []

    for idx, a in enumerate(artifacts):
        desc = str(_field(a, 'description', '') or '').lower()
        meta = _field(a, 'metadata', None)
        if not isinstance(meta, dict):
            meta = {}
        etype = _field(a, 'evidence_type', None) or meta.get('evidence_type', '')

        hit = False
        if etype in _SURVEILLANCE_TYPES and any(k in desc for k in SURVEILLANCE_KEYWORDS):
            surveillance_count += 1
            hit = True
        if any(k in desc for k in ZERO_CONTACT_KEYWORDS):
            zero_contact_count += 1
            hit = True
        if hit:
            matched.append(str(_field(a, 'artifact_id', None) or f'#{idx}'))

    if surveillance_count == 0:
        penalty = Fraction(0)
    elif zero_contact_count > 0:
        penalty = min(Fraction(8, 10), Fraction(surveillance_count * 3, 10))
    else:
        penalty = min(Fraction(8, 10), Fraction(surveillance_count, 10))

    return {
        # pattern_present exige la asimetría COMPLETA: infraestructura de
        # vigilancia Y reclamo de cero contacto. Keywords de vigilancia
        # solos ('log', 'server'...) disparan en 47/201 casos del corpus
        # (incluidos benignos) — anotarlos como "DARVO" sería narrativa
        # engañosa. Medido 2026-07-17: con ambos lados, exactamente los 5
        # casos correctos (familia KIWI + MAGNET-2021-IOS-ELI).
        "pattern_present": surveillance_count > 0 and zero_contact_count > 0,
        # penalty conserva la fórmula original (surveillance-only pena 1/10
        # por artefacto): es el contrato del pipeline (consistency_score) y
        # no se toca aquí.
        "penalty": penalty,
        "surveillance_count": surveillance_count,
        "zero_contact_count": zero_contact_count,
        "matched_artifacts": matched,
    }


def compute_darvo_penalty(artifacts: List[Any]) -> Fraction:
    return detect_darvo_pattern(artifacts)["penalty"]


def adjust_consistency_score(base: float, artifacts: List[Any]) -> float:
    penalty = compute_darvo_penalty(artifacts)
    return float(max(Fraction(0), Fraction(base) - penalty))
