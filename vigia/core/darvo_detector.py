"""
vigia/core/darvo_detector.py
DARVO Detector — asimetría de contacto actor_a vs actor_b
Alimenta consistency_score en RiskBoundedDecisionLayer
"""
from __future__ import annotations
from fractions import Fraction
from typing import List, Any

SURVEILLANCE_KEYWORDS = ('honeypot', 'accesos', 'server', 'log', 'stalkeo', 'php error', 'trampolin')
ZERO_CONTACT_KEYWORDS = ('cero contacto', 'zero contact', 'no contact', 'bloqueado')


def compute_darvo_penalty(artifacts: List[Any]) -> Fraction:
    surveillance_count = 0
    zero_contact_count = 0

    for a in artifacts:
        desc = getattr(a, 'description', '').lower()
        etype = getattr(a, 'evidence_type', '')

        if etype in ('file_metadata', 'log_entry') and any(k in desc for k in SURVEILLANCE_KEYWORDS):
            surveillance_count += 1
        if any(k in desc for k in ZERO_CONTACT_KEYWORDS):
            zero_contact_count += 1

    if surveillance_count == 0:
        return Fraction(0)

    if zero_contact_count > 0:
        penalty = Fraction(surveillance_count * 3, 10)
    else:
        penalty = Fraction(surveillance_count, 10)

    return min(Fraction(8, 10), penalty)


def adjust_consistency_score(base: float, artifacts: List[Any]) -> float:
    penalty = compute_darvo_penalty(artifacts)
    return float(max(Fraction(0), Fraction(base) - penalty))
