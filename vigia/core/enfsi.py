"""
vigia/core/enfsi.py — Escala ENFSI canónica. Fuente única (B-059).

Antes de este módulo existían CUATRO escalas ENFSI divergentes:

    1. vigia/core/ebs_v1.py           — 8 buckets, inglés (SELLADA en el bundle)
    2. vigia/tools/signal_contract.py — 5 buckets, español
    3. forensics/evidence_narrative_gen.py — 7 buckets bilingüe (reporte judicial)
    4. vigia/pipeline/vigia_integration_bridge.py — 5 buckets inline (fallback)

Riesgo Daubert reproducido en AUDITORIA_INVARIANTES_ASIMETRIAS_20260703
(B-059): el mismo LR producía "limited" en el bundle sellado y "weak
support" en el reporte firmado que lee el tribunal.

DECISIÓN DE DOCTRINA (TANDA 1, 2026-07-06): la escala canónica es la que
`ebs_v1` sella en el ForensicBundle — es el registro criptográfico, sus
etiquetas están fijadas por tests de regresión (test_b051) y cambiarla
invalidaría la reproducibilidad de los bundles históricos. Las demás
implementaciones DELEGAN en esta. El texto narrativo bilingüe del reporte
judicial se deriva de la MISMA función de bucketing (enfsi_narrative), de
modo que bundle y reporte no pueden divergir por construcción.

Este módulo es stdlib-only y sin dependencias vigia.* — importable desde
los runners standalone de forensics/.

Escala canónica (ENFSI Guideline for Evaluative Reporting, buckets ebs_v1):

    LR == 0 (o NaN)      → "inconclusive"
    LR <  1              → "supports_H0"  (la evidencia favorece autenticidad)
    1     <= LR < 2      → "weak"
    2     <= LR < 10     → "limited"
    10    <= LR < 100    → "moderate"
    100   <= LR < 1000   → "moderately strong"
    1000  <= LR < 10000  → "strong"
    LR >= 10000 (o +inf) → "very strong"
"""
from __future__ import annotations

import math

__all__ = ["enfsi_label", "enfsi_narrative", "ENFSI_NARRATIVE"]


def enfsi_label(lr: float) -> str:
    """
    Convert a Likelihood Ratio to a verbal label per the ENFSI scale
    (European Network of Forensic Science Institutes).

    Semántica bit-idéntica a la histórica de ebs_v1 para todo LR finito
    (invariante B-059: ningún bundle sellado cambia de etiqueta). Único
    agregado: guard explícito para NaN — un NaN no es un LR y caía al
    bucket "very strong" por fallo silencioso de todas las comparaciones.
    """
    try:
        if math.isnan(lr):
            return "inconclusive"
    except TypeError:
        return "inconclusive"

    if lr == 0:
        return "inconclusive"
    elif lr < 1:
        return "supports_H0"  # Evidence favors authenticity
    elif lr < 2:
        return "weak"
    elif lr < 10:
        return "limited"
    elif lr < 100:
        return "moderate"
    elif lr < 1000:
        return "moderately strong"
    elif lr < 10000:
        return "strong"
    else:
        return "very strong"


# Render narrativo bilingüe POR BUCKET CANÓNICO — el reporte judicial usa
# estas frases, derivadas de la misma función de bucketing que el bundle.
# label canónico → (frase_es, frase_en)
ENFSI_NARRATIVE: dict = {
    "inconclusive":      ("No concluyente",
                          "inconclusive"),
    "supports_H0":       ("Proporciona soporte a la hipótesis de autenticidad (H0)",
                          "provides support for the authenticity hypothesis (H0)"),
    "weak":              ("Proporciona evidencia débil",
                          "provides weak support"),
    "limited":           ("Proporciona evidencia limitada",
                          "provides limited support"),
    "moderate":          ("Proporciona evidencia moderada",
                          "provides moderate support"),
    "moderately strong": ("Proporciona evidencia moderadamente fuerte",
                          "provides moderately strong support"),
    "strong":            ("Proporciona evidencia fuerte",
                          "provides strong support"),
    "very strong":       ("Proporciona evidencia muy fuerte",
                          "provides very strong support"),
}


def enfsi_narrative(lr: float, lang: str = "es") -> str:
    """
    Frase narrativa bilingüe para el reporte judicial, derivada del bucket
    canónico. Bundle y reporte no pueden divergir: comparten enfsi_label().
    """
    label = enfsi_label(lr)
    frase_es, frase_en = ENFSI_NARRATIVE[label]
    return frase_es if lang == "es" else frase_en
