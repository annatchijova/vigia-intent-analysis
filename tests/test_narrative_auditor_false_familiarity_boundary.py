"""
tests/test_narrative_auditor_false_familiarity_boundary.py
==========================================================
Guarda de regresión para el patrón FALSE_FAMILIARITY de NarrativeAuditor.

Contexto (C3 dry-run):
    El patrón original matcheada la subcadena "know" en cualquier parte,
    produciendo 411 threats sobre 605 narrativas reales — casi todos falsos
    positivos dentro de "unknown", direcciones como whoknowsme@..., y prosa
    común. Este test fija el límite de palabra y el contexto de segunda
    persona para que "know" no dispare solo.

Verifica:
    - Frases de manipulación retórica ("as you know", "obviously"...) se detectan.
    - "unknown", "whoknowsme", "I don't know" y similares NO se detectan.
"""
from __future__ import annotations

import pytest

pytest.importorskip(
    "vigia.core.narrative_auditor",
    reason="vigia.core.narrative_auditor not importable (run with PYTHONPATH=$(pwd))",
)

from vigia.core.narrative_auditor import NarrativeAuditor


@pytest.fixture
def auditor() -> NarrativeAuditor:
    return NarrativeAuditor(strict_mode=True)


# ---------------------------------------------------------------------------
# Positivos: encuadres retóricos que presuponen terreno compartido
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("line", [
    "As you know, the suspect deleted the logs before extraction.",
    "You know the timeline puts the device at the scene.",
    "As you should know, this artifact is privileged.",
    "You should know the answer given the evidence.",
    "Obviously, the hash mismatch is the decisive signal.",
    "Naturally, the deleted file recovered from the image.",
    "Of course, the tool marks the entry as suspicious.",
])
def test_false_familiarity_detects_manipulation_cues(auditor, line):
    result = auditor.audit([line], investigation_id="TEST-POS")
    types = {t.pattern_type for t in result.threats_detected}
    assert "FALSE_FAMILIARITY" in types, (
        f"Expected FALSE_FAMILIARITY for manipulation cue: {line!r}"
    )


# ---------------------------------------------------------------------------
# Negativos: "know" como subcadena benigna NO debe disparar
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("line", [
    "The origin is unknown for this image.",
    "Contact whoknowsme@sbcglobal.net for the original drive.",
    "I don't know what I touched before the seizure.",
    "The witness acknowledged the chain-of-custody form.",
    "The 'know' token appears inside a quoted error message.",
    "Acknowledged — will review the acquisition report.",
])
def test_false_familiarity_ignores_substring_know(auditor, line):
    result = auditor.audit([line], investigation_id="TEST-NEG")
    types = {t.pattern_type for t in result.threats_detected}
    assert "FALSE_FAMILIARITY" not in types, (
        f"FALSE_FAMILIARITY must not fire on benign substring: {line!r}"
    )
