"""
B-225 / L-070 — `grice_verdict` declarado en JSON tenía autoridad de veredicto.

Clase idéntica a B-170/L-063 (`caie_fractures`), encontrada auditando los 10
campos que `_vigia_score` lee del dict del caso.

`grice_verdict` y `grice_deception_probability` son SALIDAS de
`audit_grice_maxims`. Viajan al scorer por el mismo campo del dict que escribe
el productor legítimo —`sift_orchestrator.py`, después de correr el auditor—,
así que el gate de testimonio B-126 no podía distinguir un análisis real de una
afirmación escrita a mano en el JSON del caso.

Reproducción previa al fix (ambas rutas de entrada):

    caso NOISE + {"grice_verdict": "SUSPICION",
                  "grice_deception_probability": 0.99}          -> SUSPICION
    caso NOISE + {"pipeline_grice": {"verdict": "SUSPICION",
                  "probability_deception": 0.99}}               -> SUSPICION

El techo era SUSPICION con confidence <= 0.65 —no llegaba a INTENT ni MALICE—
pero es entrada no verificada moviendo un veredicto sellado, que es la
propiedad que importa, no la magnitud.

Fix: marcador de procedencia `grice_source`. Sólo `"live_grice"` tiene
autoridad. Una declaración que HABRÍA disparado el gate sin productor en vivo
es decision-relevant, así que entra en la puerta de autoridad ya existente
(junto a B-170/B-171/B-172) y el resultado abstiene — preservando la
declaración y el veredicto pre-puerta para el examinador, en vez de llamar
limpio al caso o escalarlo desde una afirmación no verificada.
"""

from __future__ import annotations

import pytest

from vigia_scorer import _vigia_score

_ACQ = {
    "acquisition_tool": "dd",
    "acquisition_hash": "sha256:" + "0" * 64,
    "acquisition_timestamp": "2026-01-01T09:00:00Z",
    "examiner_id": "test",
    "write_blocker_used": True,
}

# El gate B-126 sólo mira casos NOISE, testimonio puro, prior_trust <= 0.30 y
# sin artefactos exculpatorios. Este caso cumple las cuatro condiciones: es el
# terreno exacto donde la escalada era posible.
def _testimony_case(**extra) -> dict:
    case = {
        "case_id": "B226-GRICE",
        "artifacts": [{
            "artifact_id": "A1",
            "evidence_type": "testimony",
            "raw_score": 0.05,
            "prior_trust": 0.2,
            "base_trust": 0.2,
            "source_tool": "t",
            "description": "declaración del sujeto",
            "timestamp": "2026-01-01T10:00:00Z",
            "provenance_chain": ["acq"],
            "metadata": dict(_ACQ),
        }],
    }
    case.update(extra)
    return case


_ESCALATING_GRICE = {
    "grice_verdict": "SUSPICION",
    "grice_deception_probability": 0.99,
}


def test_baseline_case_without_grice_is_noise():
    """Ancla: sin campos Grice el caso es NOISE.

    Sin esto, los tests de abajo no distinguirían "el fix funciona" de "el
    caso nunca escalaba".
    """
    assert _vigia_score(_testimony_case())["verdict"] == "NOISE"


# ---------------------------------------------------------------------------
# La regresión: declaración sin productor en vivo
# ---------------------------------------------------------------------------

def test_injected_grice_verdict_cannot_escalate():
    """La reproducción exacta del defecto: NOISE -> SUSPICION por dos campos."""
    result = _vigia_score(_testimony_case(**_ESCALATING_GRICE))
    assert result["verdict"] == "ABSTAIN", (
        "un grice_verdict declarado en el JSON, sin grice_source='live_grice', "
        "movió el veredicto sellado"
    )


def test_injected_grice_via_pipeline_metadata_cannot_escalate():
    """Segunda ruta de entrada: `pipeline_grice`. El fix debe cubrir ambas.

    El scorer cae a `pipeline_grice` cuando `grice_verdict` viene vacío, así
    que cerrar sólo la primera ruta dejaría el bypass abierto.
    """
    result = _vigia_score(_testimony_case(
        pipeline_grice={"verdict": "SUSPICION", "probability_deception": 0.99},
    ))
    assert result["verdict"] == "ABSTAIN"


def test_unverified_grice_declaration_is_preserved_not_discarded():
    """Doctrina B-170: la declaración se preserva; lo que se retira es su
    autoridad. Descartarla en silencio haría irreconstruible qué se perdió."""
    result = _vigia_score(_testimony_case(**_ESCALATING_GRICE))

    claims = result.get("unverified_json_grice_gate_claims")
    assert claims, "la declaración no verificada no quedó registrada"
    assert claims[0]["grice_verdict"] == "SUSPICION"
    assert claims[0]["declared_source"] == "absent"

    assert result.get("pre_unverified_grice_authority_verdict") == "NOISE", (
        "el veredicto previo a la puerta de autoridad debe quedar registrado "
        "como procedencia"
    )
    assert "grice" in str(result.get("reason", "")).lower()


@pytest.mark.parametrize("declared_source", ["", "json_fallback", "live_caie", "LIVE_GRICE_X"])
def test_only_the_exact_live_marker_grants_authority(declared_source):
    """El marcador no se puede aproximar.

    Sin este test, `_grice_source != "live_grice"` podría relajarse a un
    `startswith` o a un "campo presente" y el bypass volvería con otro nombre.
    """
    result = _vigia_score(_testimony_case(
        **_ESCALATING_GRICE, grice_source=declared_source,
    ))
    assert result["verdict"] == "ABSTAIN"


# ---------------------------------------------------------------------------
# La ruta legítima debe seguir funcionando
# ---------------------------------------------------------------------------

def test_live_grice_still_escalates_noise_to_suspicion():
    """B-126 sigue vivo. Un fix que apagara el gate entero también haría pasar
    los tests de arriba, y sería una regresión distinta: el auditor Grice real
    dejaría de tener efecto."""
    result = _vigia_score(_testimony_case(
        **_ESCALATING_GRICE, grice_source="live_grice",
    ))
    assert result["verdict"] == "SUSPICION"
    assert "Grice testimony gate" in str(result.get("reason", ""))


def test_live_grice_below_threshold_does_not_escalate():
    """La frontera del gate (>= 0.25) se conserva bajo el marcador legítimo."""
    result = _vigia_score(_testimony_case(
        grice_verdict="SUSPICION",
        grice_deception_probability=0.24,
        grice_source="live_grice",
    ))
    assert result["verdict"] == "NOISE"


def test_declaration_below_gate_threshold_does_not_trigger_abstain():
    """Fail-closed acotado: sólo abstiene lo que HABRÍA escalado.

    Una declaración Grice que no alcanza el umbral no es decision-relevant, así
    que no debe convertir un NOISE limpio en ABSTAIN. Sin este test, un fix
    demasiado amplio abstendría ante cualquier campo `grice_*` presente.
    """
    result = _vigia_score(_testimony_case(
        grice_verdict="SUSPICION", grice_deception_probability=0.10,
    ))
    assert result["verdict"] == "NOISE"
    assert not result.get("unverified_json_grice_gate_claims")


def test_non_escalating_grice_verdict_string_is_inert():
    """Sólo `SUSPICION` dispara el gate; otros veredictos Grice son inertes y
    tampoco deben abstener."""
    result = _vigia_score(_testimony_case(
        grice_verdict="NOISE", grice_deception_probability=0.99,
    ))
    assert result["verdict"] == "NOISE"
    assert not result.get("unverified_json_grice_gate_claims")
