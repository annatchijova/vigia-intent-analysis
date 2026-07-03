"""
Tests B-066 / B-067 — Fase 1 del whitelist mobile + fix del fallback invertido.

B-066 (AUDITORIA_MOBILE_WHITELIST §4 Fase 1): 8 tipos de evidencia mobile en
EVIDENCE_PROFILES + entradas en los 3 mapas del adapter + este test de
contrato, que convierte la convención productor/consumidor en contrato
(cierra la propuesta de B-060).

B-067 (AUDITORIA_MOBILE_WHITELIST §3.2): el fallback para tipo desconocido
era (0.50, 0.20) — puntuaba MÁS ALTO que log_entry (0.85, 0.15). Un caso
JSON adversarial podía inventar un tipo para esquivar el perfil de
spoofability de su tipo real (el bypass que caie.py add_artifact declara
prevenir). Ahora el desconocido se trata como la peor clase conocida
(0.90, 0.15) y la invariante se verifica contra TODA la tabla.
"""

import pytest

from vigia.tools.caie import EVIDENCE_PROFILES, Artifact
from vigia.core.forensic_adapter import (
    ForensicAdapter,
    _EVIDENCE_MAP,
    _LAYER_MAP,
    _ONTOLOGY_MAP,
)

MOBILE_TYPES = [
    "chat_message", "sms", "call_log", "web_search",
    "app_data", "social_media", "location_data", "contact_data",
]

# Etiquetas agregadas que emiten los motores mobile hoy (una señal por motor,
# hasta B-052-P2). Fuente: <engine>.to_signal() metadata["artifact_type"].
ENGINE_LABELS = [
    "android_forensic", "ios_forensic", "macos_forensic", "google_takeout",
]


# ===========================================================================
# B-066 — perfiles y contrato de mapas
# ===========================================================================

class TestB066MobileProfiles:
    @pytest.mark.parametrize("etype", MOBILE_TYPES)
    def test_mobile_type_has_profile(self, etype):
        assert etype in EVIDENCE_PROFILES

    def test_mobile_spoofability_ordering(self):
        """La calibración relativa del §2 de la auditoría: location_data es
        lo más duro de falsificar consistentemente; contact_data lo más
        trivial."""
        p = EVIDENCE_PROFILES
        assert p["location_data"].spoofability < p["chat_message"].spoofability
        assert p["chat_message"].spoofability < p["contact_data"].spoofability
        # Analogía declarada: "editable con root" ≈ registry_key (0.55)
        assert p["contact_data"].spoofability >= p["registry_key"].spoofability


class TestB066MapContract:
    """B-060: productor (motor) y consumidor (CAIE/adapter) coincidían solo
    por convención. Este test es el contrato: falla si un tipo emitido no
    resuelve en TODOS los mapas."""

    @pytest.mark.parametrize("etype", MOBILE_TYPES + ENGINE_LABELS)
    def test_type_resolves_in_all_adapter_maps(self, etype):
        assert etype in _LAYER_MAP, f"{etype} sin capa epistémica declarada"
        assert etype in _ONTOLOGY_MAP, f"{etype} sin nivel ontológico declarado"
        assert etype in _EVIDENCE_MAP, f"{etype} sin mapeo a tipo canónico"

    def test_every_evidence_map_value_is_whitelisted(self):
        """Ningún valor de _EVIDENCE_MAP puede apuntar fuera de
        EVIDENCE_PROFILES — si esto falla, un tipo 'mapeado' cae igual al
        fallback y el mapeo es mentira."""
        for k, v in _EVIDENCE_MAP.items():
            assert v in EVIDENCE_PROFILES, f"_EVIDENCE_MAP[{k!r}] = {v!r} no está en EVIDENCE_PROFILES"

    def test_adapter_end_to_end_mobile_signal(self):
        """Una señal mobile tipificada atraviesa el adapter y llega a CAIE
        con su tipo canónico (no al fallback)."""
        from vigia.core.ebs_v1 import SignalOutput

        sig = SignalOutput(
            tool_name="ANDROID_FORENSICS", value=0.7, z_score=2.5,
            confidence=0.9, metadata={"evidence_type": "sms"},
        )
        art = ForensicAdapter.signal_to_caie_artifact(sig)
        assert art.evidence_type == "sms"
        assert art.profile.description.startswith("mmssms.db")


# ===========================================================================
# B-067 — fallback invertido
# ===========================================================================

class TestB067FallbackInversion:
    def _fallback_profile(self):
        art = Artifact(
            source_tool="t", evidence_type="invented_type_xyz",
            raw_score=0.8, description="d",
        )
        return art.profile

    def test_unknown_type_not_better_than_any_known_type(self):
        """Invariante central: (1-spoof)×weight del tipo DESCONOCIDO debe ser
        ≤ el mínimo de toda la tabla. Si un perfil nuevo baja ese mínimo,
        este test obliga a bajar también el fallback."""
        fb = self._fallback_profile()
        fb_product = (1.0 - fb.spoofability) * fb.base_weight
        worst_known = min(
            (1.0 - p.spoofability) * p.base_weight
            for p in EVIDENCE_PROFILES.values()
        )
        assert fb_product <= worst_known + 1e-12, (
            f"fallback ({fb_product:.4f}) puntúa mejor que la peor clase "
            f"conocida ({worst_known:.4f}) — bypass B-067 reabierto"
        )

    def test_scorer_unknown_type_scores_at_most_log_entry(self):
        """Regresión del experimento §3.2 de la auditoría: mismo artefacto,
        tipo inventado vs log_entry — el inventado ya no puede ganar."""
        from vigia_scorer import _vigia_score

        def case(etype):
            return {"case_id": "B067", "artifacts": [{
                "source_tool": "tool", "evidence_type": etype,
                "raw_score": 0.85, "description": "x", "artifact_id": "A0",
                "provenance_chain": ["acquire", "hash", "extract"],
                "timestamp": "2026-01-01T10:00:00Z", "metadata": {},
            }]}

        unknown = _vigia_score(case("invented_type_xyz"))
        known = _vigia_score(case("log_entry"))
        u0 = (unknown.get("artifacts_trace") or unknown.get("effective_trusts"))[0]
        k0 = (known.get("artifacts_trace") or known.get("effective_trusts"))[0]
        assert u0["adjusted_score"] <= k0["adjusted_score"] + 1e-12

    def test_mobile_types_no_longer_hit_fallback(self):
        for etype in MOBILE_TYPES:
            art = Artifact(source_tool="t", evidence_type=etype,
                           raw_score=0.5, description="d")
            assert "Unknown evidence type" not in art.profile.description
