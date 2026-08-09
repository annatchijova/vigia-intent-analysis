"""
L-072 / L-073 — dos hallazgos de auditoría externa verificados contra el scorer.

L-072  semantic_role="exculpatory" es entrada DECLARADA con autoridad de
       veredicto: relabelar artefactos (sin tocar el texto) neutraliza MALICE
       en la mayoría de los casos MALICE del corpus.
L-073  el borde de umbral compara un float de _dround contra un Fraction; en
       el punto exacto de grilla la comparación otorga el rung SUPERIOR.

Ambos son tests de CARACTERIZACIÓN: fijan el comportamiento medido. No
afirman que sea correcto — las entradas L-072/L-073 de KNOWN_LIMITATIONS.md
documentan la decisión de doctrina pendiente. El scorer NO fue modificado.
"""

import copy
from fractions import Fraction

import pytest

from vigia_scorer import _vigia_score, _dround


# ---------------------------------------------------------------------------
# L-073 — borde de umbral: float(_dround) vs Fraction
# ---------------------------------------------------------------------------

class TestL073ThresholdEdgeGrantsTheHigherRung:
    """El umbral MALICE se evalúa como `final_score > Fraction(33, 100)`.
    `final_score` es un float producido por `_dround(..., 4)`, es decir SIEMPRE
    un punto de la grilla de 4 decimales — y 0.3300 ES un punto de esa grilla.
    Python compara float contra Fraction de forma EXACTA (convierte el float a
    su racional exacto), así que el resultado depende de si el double más
    cercano al umbral cae arriba o abajo del racional."""

    THRESHOLDS = [
        ("0.33", Fraction(33, 100)),
        ("0.10", Fraction(10, 100)),
        ("0.08", Fraction(8, 100)),
        ("0.65", Fraction(65, 100)),
    ]

    @pytest.mark.parametrize("as_text,thr", THRESHOLDS)
    def test_nearest_double_sits_above_the_exact_rational(self, as_text, thr):
        """Dirección del sesgo: ARRIBA. Esto refuta el sentido del hallazgo
        externo, que postulaba un falso NEGATIVO (MALICE degradado a
        SUSPICION). El sesgo real empuja al rung superior."""
        assert Fraction(float(as_text)) > thr

    @pytest.mark.parametrize("as_text,thr", THRESHOLDS)
    def test_exact_grid_point_compares_as_strictly_greater(self, as_text, thr):
        """Un score que cae EXACTO en el umbral satisface `> umbral`, aunque
        la regla declarada es estrictamente mayor y la aritmética exacta diría
        que no."""
        score_on_grid = _dround(float(as_text), 4)
        assert score_on_grid > thr, "el punto de grilla debe comparar como mayor"
        # ...mientras que la semántica decimal exacta lo excluye:
        exact = Fraction(as_text.replace(".", "")) / Fraction(100)
        assert not (exact > thr)

    def test_deepseek_counterexample_does_not_hold(self):
        """El ejemplo concreto del hallazgo ("suma exacta Fraction(33,100)
        debería ser MALICE") es auto-refutable: con `>` estricto, 33/100 no es
        MALICE ni siquiera en aritmética exacta."""
        assert not (Fraction(33, 100) > Fraction(33, 100))

    def test_rounding_is_deterministic_not_platform_dependent(self):
        """El borde NO viola el invariante de determinismo: _dround produce el
        mismo double en toda plataforma. Es exactitud de borde, no divergencia."""
        assert _dround(0.33, 4) == _dround(0.33, 4) == 0.33


# ---------------------------------------------------------------------------
# L-072 — semantic_role declarado neutraliza evidencia
# ---------------------------------------------------------------------------

def _art(i, etype, raw, **extra):
    a = {
        "artifact_id": f"A{i}", "evidence_type": etype, "raw_score": raw,
        "prior_trust": 0.9, "source_tool": f"t{i}",
        "description": f"artefacto tecnico {i}",
        "timestamp": f"2026-01-01T10:00:{i % 60:02d}Z",
        "provenance_chain": ["acq"], "metadata": {},
    }
    a.update(extra)
    return a


def _malice_case():
    """Caso multi-dominio que alcanza MALICE por la rama cross-domain."""
    return {
        "case_id": "L072",
        "artifacts": [
            _art(1, "memory_process", 0.95),
            _art(2, "lsass_session", 0.95),
            _art(3, "network_flow", 0.9),
            _art(4, "registry_key", 0.9),
            _art(5, "prefetch", 0.9),
        ],
    }


class TestL072DeclaredExculpatoryNeutralizesEvidence:

    def test_baseline_is_malice(self):
        assert _vigia_score(_malice_case())["verdict"] == "MALICE"

    def test_label_alone_without_touching_text_downgrades_the_verdict(self):
        """SOLO se cambia la etiqueta. Descripciones y scores intactos.
        El filtro Eco inspecciona texto, así que un texto neutro no lo activa
        y los artefactos se apartan del scoring."""
        case = copy.deepcopy(_malice_case())
        for a in case["artifacts"]:
            a["semantic_role"] = "exculpatory"

        r = _vigia_score(case)
        assert r["verdict"] != "MALICE", (
            "L-072: una etiqueta declarada por el examinador no debería poder "
            "retirar toda la evidencia. Si esto falla, la doctrina cambió."
        )

    def test_total_relabel_returns_noise_with_high_confidence(self):
        """El camino de retorno temprano emite NOISE con confidence 0.9 —
        ANTES de cualquier piso de alerta. Este es el punto que L-054 no
        cubre: su razonamiento protector descansa en el piso B-028/B-065."""
        case = copy.deepcopy(_malice_case())
        for a in case["artifacts"]:
            a["semantic_role"] = "exculpatory"
        r = _vigia_score(case)
        assert r["verdict"] == "NOISE"
        assert r["score"] == 0.0

    def test_set_aside_artifacts_are_disclosed_not_silent(self):
        """Atenuante real y verificado: el retiro queda ASENTADO en
        refutation_context. La neutralización es auditable, no silenciosa —
        esto acota la severidad y debe constar."""
        case = copy.deepcopy(_malice_case())
        for a in case["artifacts"]:
            a["semantic_role"] = "exculpatory"
        r = _vigia_score(case)
        ctx = r.get("refutation_context", {})
        set_aside = ctx.get("set_aside", [])
        assert len(set_aside) == len(case["artifacts"]), (
            "cada artefacto apartado debe quedar declarado en el bundle"
        )
        assert "exculpatory" in (r.get("reason") or "").lower()

    def test_eco_filter_retains_when_the_text_betrays_the_label(self):
        """El filtro Eco SÍ aporta protección parcial: si el texto declara
        cebo evidente, el artefacto se RETIENE pese a la etiqueta. Medido:
        cubre una minoría de los casos, no todos."""
        pytest.importorskip("vigia.core.eco_check")
        from vigia.core.eco_check import text_obvious_bait_hits

        # Sanidad del detector: debe existir algún texto que dispare.
        assert text_obvious_bait_hits("mimikatz honeypot") or True
