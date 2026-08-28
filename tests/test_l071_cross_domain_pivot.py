"""
L-071 — minimal-cost cross-domain pivot in the B-068 gate (R4-3 v2).

Origen: auditoría externa DeepSeek (2 hallazgos), verificada contra el
código vivo. El hallazgo tal como fue enunciado ("el Noisy-OR hace que el
dominio duro se active por cantidad de ruido blando") es FALSO —
`r43_domain_scores` se calcula por dominio sobre los índices propios de ese
dominio, y el ruido blando no entra en el score del dominio duro. Lo que SÍ
se reproduce es un mecanismo distinto: la rama cross-domain del gate B-068
cuenta la PRESENCIA de un dominio, no su masa probatoria, de modo que un
único artefacto de valor evidencial casi nulo compra el segundo dominio y
voltea SUSPICION -> MALICE.

Estos tests son de CARACTERIZACIÓN: fijan el comportamiento medido para que
un cambio de calibración futuro sea deliberado y visible, no accidental.
No afirman que el comportamiento sea correcto — L-071 lo documenta como
limitación abierta (cuestión de doctrina de calibración, igual que L-049).
"""

import pytest

from vigia_scorer import _vigia_score, _M2_MIN_SIGNAL_ADJ


def _art(i, etype, raw, prior=0.9):
    """Artefacto con metadatos de adquisición completos — aísla el efecto
    medido de la degradación de trust por NIST SP 800-86."""
    return {
        "artifact_id": f"A{i}", "evidence_type": etype, "raw_score": raw,
        "prior_trust": prior, "source_tool": f"t{i}", "description": f"a{i}",
        "timestamp": f"2026-01-01T10:00:{i % 60:02d}Z",
        "provenance_chain": ["acq"],
        "metadata": {
            "acquisition_tool": "dd", "acquisition_hash": "h" * 64,
            "acquisition_timestamp": "2026-01-01T00:00:00Z",
            "examiner_id": "E1", "write_blocker_used": True,
        },
    }


def _single_domain_base():
    """16 artefactos, TODOS en filesystem_metadata (D3) — un solo dominio de
    recolección. Supera el umbral MALICE (0.33) pero el gate debe negar
    MALICE: volumen dentro de un único dominio blando no corrobora."""
    return (
        [_art(i, "sms", 0.9) for i in range(4)]
        + [_art(10 + i, "chat_message", 0.9) for i in range(4)]
        + [_art(20 + i, "web_search", 0.9) for i in range(4)]
        + [_art(30 + i, "call_log", 0.9) for i in range(4)]
    )


def _score(arts, case_id="L071"):
    return _vigia_score({"case_id": case_id, "artifacts": arts})


class TestSingleDomainVolumeDoesNotCorroborate:
    """B-091/B-092 sigue vigente: el volumen mono-dominio no abre MALICE."""

    def test_single_soft_domain_above_threshold_is_capped_to_suspicion(self):
        r = _score(_single_domain_base())
        assert r["score"] > 0.33, "el caso base debe superar el umbral MALICE"
        assert r["verdict"] == "SUSPICION", r["reason"]
        assert "no corroboration branch opens" in r["reason"]


class TestL071CrossDomainPivot:
    """El defecto: UN artefacto de valor casi nulo en un segundo dominio
    abre la rama cross-domain y voltea el veredicto."""

    @pytest.mark.parametrize("etype", ["network_flow", "log_entry"])
    @pytest.mark.parametrize("raw", [0.01, 0.001])
    def test_near_zero_artifact_in_second_domain_flips_to_malice(self, etype, raw):
        base = _single_domain_base()
        assert _score(base)["verdict"] == "SUSPICION"

        r = _score(base + [_art(900, etype, raw)])
        assert r["verdict"] == "MALICE", (
            f"L-071: pivote {etype} raw={raw} debía abrir cross-domain. "
            f"Si esto falla, el gate fue recalibrado — revisar L-071."
        )
        assert "cross-domain" in r["reason"]

    def test_pivot_moves_verdict_far_more_than_it_moves_score(self):
        """Firmeza del hallazgo: el salto de veredicto NO está sostenido por
        masa probatoria. El pivote aporta un delta de score marginal."""
        base_r = _score(_single_domain_base())
        piv_r = _score(_single_domain_base() + [_art(900, "network_flow", 0.001)])

        delta = piv_r["score"] - base_r["score"]
        assert delta < 0.05, f"delta de score inesperadamente grande: {delta}"
        assert base_r["verdict"] == "SUSPICION" and piv_r["verdict"] == "MALICE"


class TestM2SignalFloorIsExactlyZero:
    """El piso que gobierna la corroboración del gate es 0.0 (comparación
    estricta >), NO el _SOURCE_MATERIALITY_FLOOR=0.05 de caie.py — ese vive
    en otro módulo y gobierna independent_sources/confidence_penalty de CAIE,
    no el gate B-068. Fijar esto evita que la confusión se repita."""

    def test_m2_floor_constant_is_zero(self):
        assert _M2_MIN_SIGNAL_ADJ == 0.0

    def test_exact_zero_raw_score_does_not_corroborate(self):
        """raw_score=0 => adjusted=0 => NO abre el gate (piso estricto >)."""
        r = _score(_single_domain_base() + [_art(900, "network_flow", 0.0)])
        assert r["verdict"] == "SUSPICION", r["reason"]
        assert "no corroboration branch opens" in r["reason"]

    def test_caie_floor_is_a_different_module_and_does_not_gate_the_scorer(self):
        from vigia.tools.caie import _SOURCE_MATERIALITY_FLOOR
        assert float(_SOURCE_MATERIALITY_FLOOR) == 0.05
        assert float(_SOURCE_MATERIALITY_FLOOR) > _M2_MIN_SIGNAL_ADJ
