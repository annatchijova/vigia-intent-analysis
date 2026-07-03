"""
Tests B-070 — rol epistémico device/contextual/narrative (Opción C).

Cierra el canal composite del FP NGDC-003 (AUDITORIA_ABDUCTIVA_NGDC003_FP):
la causa raíz (b) era que el modelo de datos no distinguía evidencia-de-
dispositivo de contexto-narrativo, así que la narrativa de escenario inflaba
el score de malicia (NGDC-003: +0.15, confianza 0.56→0.86). Opción C: un
registro único de roles (vigia.tools.caie.evidence_role) que scorer y gate
respetan.

Modelo de 3 roles:
  DEVICE     — composite ✓, gate ✓ (default, incl. desconocidos)
  CONTEXTUAL — composite ✓, gate ✗ (osint, acquisition_context, ...)
  NARRATIVE  — composite ✗, gate ✗ (behavioral_context/profile, outcome_signal)
"""

import json
import glob

import pytest

from vigia.tools.caie import (
    evidence_role,
    EVIDENCE_ROLE_DEVICE,
    EVIDENCE_ROLE_CONTEXTUAL,
    EVIDENCE_ROLE_NARRATIVE,
)
from vigia_scorer import _vigia_score


def _case(name):
    p = glob.glob(f"data/cases/**/{name}.json", recursive=True)[0]
    return json.load(open(p))


# ===========================================================================
# Registro de roles — fuente única
# ===========================================================================

class TestEvidenceRoleRegistry:
    def test_narrative_types(self):
        for t in ("behavioral_context", "behavioral_profile", "outcome_signal"):
            assert evidence_role(t) == EVIDENCE_ROLE_NARRATIVE

    def test_contextual_types(self):
        for t in ("osint", "acquisition_context", "device_acquisition_timeline"):
            assert evidence_role(t) == EVIDENCE_ROLE_CONTEXTUAL

    def test_device_is_default_for_known_and_unknown(self):
        # tipos de dispositivo conocidos
        for t in ("memory_process", "keylogger_capture", "email_content", "file_metadata"):
            assert evidence_role(t) == EVIDENCE_ROLE_DEVICE
        # un tipo desconocido NO deja de contar por no estar clasificado
        assert evidence_role("invented_type_xyz") == EVIDENCE_ROLE_DEVICE


# ===========================================================================
# Canal composite cerrado — NGDC-003
# ===========================================================================

class TestB070NarrativeComposite:
    def test_ngdc003_confidence_now_honest(self):
        """El canal composite: la narrativa ya no infla la confianza.
        Pre-B-070 la confianza era 0.86 (inflada por 2 artefactos narrativos);
        ahora ~0.56, acorde a la intención disputada (conf_expected del caso=67)."""
        r = _vigia_score(_case("VIGIA-NGDC-003"))
        assert r["verdict"] == "SUSPICION"
        assert float(r["confidence"]) < 0.70  # ya no 0.86
        # los 2 artefactos narrativos quedan retenidos para el reporte
        nc_types = {x["evidence_type"] for x in r.get("narrative_context", [])}
        assert nc_types == {"behavioral_context", "outcome_signal"}

    def test_narrative_does_not_move_verdict_but_is_retained(self):
        r = _vigia_score(_case("VIGIA-NGDC-002"))
        assert r["verdict"] == "MALICE"  # sigue MALICE por evidencia técnica
        assert any(x["evidence_type"] == "behavioral_profile"
                   for x in r.get("narrative_context", []))

    def test_contextual_stays_in_composite_no_regression(self):
        """LINUX-005 (PUMAKIT false-flag): su artefacto de contexto es OSINT
        (CONTEXTUAL, no NARRATIVE) → sigue en el composite → verdict sin
        cambio. Esta es la distinción que evita la regresión."""
        r = _vigia_score(_case("VIGIA-LINUX-005"))
        # OSINT no se aparta (no es narrativa) → no aparece en narrative_context
        assert r.get("narrative_context", []) == []
        assert r["verdict"] == _case("VIGIA-LINUX-005")["expected_verdict"]


# ===========================================================================
# Casos degenerados
# ===========================================================================

class TestB070Degenerate:
    def _artifact(self, i, etype, raw=0.9):
        return {"artifact_id": f"A{i}", "evidence_type": etype, "raw_score": raw,
                "source_tool": f"t{i}", "description": f"a{i}",
                "prior_trust": 0.85, "provenance_chain": ["a", "b", "c"],
                "timestamp": f"2026-01-0{i+1}T10:00:00Z", "metadata": {}}

    def test_all_narrative_case_abstains(self):
        """Un caso solo de narrativa de escenario no tiene evidencia de
        dispositivo → ABSTAIN, no NOISE ni MALICE."""
        arts = [self._artifact(0, "behavioral_context"),
                self._artifact(1, "outcome_signal"),
                self._artifact(2, "behavioral_profile")]
        r = _vigia_score({"case_id": "B070-ALLNARR", "artifacts": arts})
        assert r["verdict"] == "ABSTAIN"
        assert len(r["narrative_context"]) == 3

    def test_contextual_only_is_not_malice(self):
        """Solo evidencia CONTEXTUAL (sin DEVICE): entra al composite pero el
        gate (que exige DEVICE) no puede sellar MALICE."""
        arts = [self._artifact(0, "osint"),
                self._artifact(1, "acquisition_context")]
        r = _vigia_score({"case_id": "B070-CTXONLY", "artifacts": arts})
        assert r["verdict"] != "MALICE"


# ===========================================================================
# Corpus sin regresión
# ===========================================================================

class TestB070CorpusStable:
    def test_ngdc_family_verdicts(self):
        exp = {"001": "MALICE", "002": "MALICE", "003": "SUSPICION", "004": "MALICE"}
        for n, v in exp.items():
            r = _vigia_score(_case(f"VIGIA-NGDC-{n}"))
            assert r["verdict"] == v, f"NGDC-{n}: {r['verdict']} != {v}"
