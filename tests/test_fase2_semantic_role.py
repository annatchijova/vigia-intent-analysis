"""
FASE 2 (2026-07-06) — semantic_role: dirección de la inferencia del artefacto.

Diseño aprobado (docs/FASE2_EVIDENCIA_EXCULPATORIA.md + decisiones D1/D2):
  - semantic_role ∈ {incriminatory (default), exculpatory, contextual},
    EXAMINER-DECLARED únicamente.
  - exculpatory → semántica V1: fuera del composite Y del gate B-068,
    retenido en refutation_context (espejo de _narrative_artifacts B-070).
  - contextual → permanece en composite, NO corrobora el gate.
  - D1: cada exculpatorio pasa por el filtro Eco (vigia.core.eco_check,
    fuente única con el tool MCP) ANTES de apartarse — si su texto contiene
    vocabulario de cebo obvio, se RETIENE en el scoring (doc demasiado
    perfecta/mal etiquetada = señal) y el evento queda sellado.
  - Sin resta activa (V3) — medida y descartada en la investigación.
"""

import copy
import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from vigia_scorer import _vigia_score, _normalize_case  # noqa: E402


def _case(arts):
    return {"case_id": "TEST-SR", "artifacts": arts}


def _art(aid, raw, role=None, desc="registro de sistema", etype="log_entry"):
    a = {
        "artifact_id": aid, "evidence_type": etype, "raw_score": raw,
        "prior_trust": 0.85, "description": desc,
        "provenance_chain": [f"sha256:test_{aid}"],
    }
    if role is not None:
        a["semantic_role"] = role
    return a


def _score(case):
    return _vigia_score(_normalize_case(copy.deepcopy(case)))


BASE_INCRIMINATORY = [
    _art("A1", 0.8, desc="proceso anomalo en ruta de usuario"),
    _art("A2", 0.9, desc="conexion saliente no justificada", etype="file_timestamp"),
    _art("A3", 0.95, desc="registro alterado", etype="registry_key"),
]


class TestExculpatorySetAside:
    def test_exculpatory_lowers_score_vs_incriminatory(self):
        """El mismo artefacto declarado exculpatory deja de sumar al composite."""
        base = _score(_case(copy.deepcopy(BASE_INCRIMINATORY)))
        arts = copy.deepcopy(BASE_INCRIMINATORY)
        arts[2]["semantic_role"] = "exculpatory"
        arts[2]["description"] = "HR record: empleado verificado, contrato remoto"
        excul = _score(_case(arts))
        assert float(excul["score"]) < float(base["score"])
        assert excul["refutation_context"]["set_aside"][0]["artifact_id"] == "A3"

    def test_default_is_incriminatory_no_behavior_change(self):
        """Sin el campo, el scoring es bit-idéntico al pre-FASE-2."""
        r1 = _score(_case(copy.deepcopy(BASE_INCRIMINATORY)))
        arts = copy.deepcopy(BASE_INCRIMINATORY)
        for a in arts:
            a["semantic_role"] = "incriminatory"
        r2 = _score(_case(arts))
        assert r1["verdict"] == r2["verdict"]
        assert r1["score"] == r2["score"]

    def test_exculpatory_excluded_from_corroboration_gate(self):
        """V1: el exculpatorio no corrobora MALICE (no cuenta clases DEVICE).
        3 clases device con score alto cruzan el gate B-068; si una es
        exculpatoria, quedan 2 artefactos → el gate no puede dar MALICE."""
        arts = copy.deepcopy(BASE_INCRIMINATORY) + [
            _art("A4", 0.9, desc="entrada mft", etype="mft_entry"),
        ]
        base = _score(_case(copy.deepcopy(arts)))
        arts2 = copy.deepcopy(arts)
        for a in arts2[1:]:
            a["semantic_role"] = "exculpatory"
            a["description"] = "memo de autorizacion firmado por el directorio"
        excul = _score(_case(arts2))
        # con 3 de 4 apartados solo queda A1: jamás MALICE por el gate
        assert excul["verdict"] != "MALICE"
        assert len(excul["refutation_context"]["set_aside"]) == 3
        assert base["score"] >= excul["score"]

    def test_all_exculpatory_is_documented_refutation_noise(self):
        arts = copy.deepcopy(BASE_INCRIMINATORY)
        for a in arts:
            a["semantic_role"] = "exculpatory"
            a["description"] = "runbook auditado, cambio aprobado por el CAB"
        r = _score(_case(arts))
        assert r["verdict"] == "NOISE"
        assert "refutation" in r["reason"].lower() or "exculpatory" in r["reason"].lower()
        assert len(r["refutation_context"]["set_aside"]) == 3

    def test_invalid_role_value_treated_as_incriminatory_by_scorer(self):
        """El scorer degrada valores desconocidos a incriminatory (fail-safe);
        la validación fail-loud vive en validate_case_schema."""
        arts = copy.deepcopy(BASE_INCRIMINATORY)
        arts[0]["semantic_role"] = "exculpatoria"  # typo
        r = _score(_case(arts))
        base = _score(_case(copy.deepcopy(BASE_INCRIMINATORY)))
        assert r["score"] == base["score"]

    def test_label_blind(self):
        """El tratamiento no depende de expected_verdict (invariante B-075)."""
        arts = copy.deepcopy(BASE_INCRIMINATORY)
        arts[2]["semantic_role"] = "exculpatory"
        c1 = _case(copy.deepcopy(arts)); c1["expected_verdict"] = "MALICE"
        c2 = _case(copy.deepcopy(arts)); c2["expected_verdict"] = "NOISE"
        c1b = {k: v for k, v in c1.items() if k != "expected_verdict"}
        r1, r2, rb = _score(c1), _score(c2), _score(c1b)
        assert r1["verdict"] == r2["verdict"] == rb["verdict"]
        assert r1["score"] == r2["score"] == rb["score"]


class TestContextualRole:
    def test_contextual_stays_in_composite_but_not_gate(self):
        """contextual suma al score pero no puede corroborar MALICE."""
        arts = [
            _art("A1", 0.9, desc="anomalia"),
            _art("A2", 0.9, desc="contexto osint", etype="file_timestamp",
                 role="contextual"),
            _art("A3", 0.9, desc="mas contexto", etype="registry_key",
                 role="contextual"),
            _art("A4", 0.9, desc="otro contexto", etype="mft_entry",
                 role="contextual"),
        ]
        r = _score(_case(arts))
        # 4 artefactos con score alto cruzarían el umbral; pero solo 1 clase
        # DEVICE no-contextual → el gate B-068 no puede emitir MALICE.
        assert r["verdict"] != "MALICE"


class TestD1EcoGate:
    def test_eco_retains_staged_exculpatory(self):
        """D1: una 'refutación' cuyo texto grita ataque NO se aparta."""
        arts = copy.deepcopy(BASE_INCRIMINATORY)
        arts[2]["semantic_role"] = "exculpatory"
        arts[2]["description"] = (
            "memo de autorizacion: acceso aprobado a mimikatz y backdoor "
            "para ejercicio, credenciales de c2 incluidas"
        )
        r = _score(_case(arts))
        base = _score(_case(copy.deepcopy(BASE_INCRIMINATORY)))
        ret = r["refutation_context"]["eco_retained"]
        assert len(ret) == 1 and ret[0]["artifact_id"] == "A3"
        assert set(ret[0]["eco_bait_terms"]) & {"mimikatz", "backdoor", "c2"}
        assert r["refutation_context"]["set_aside"] == []
        # el artefacto quedó en el scoring: score idéntico al base
        assert r["score"] == base["score"]

    def test_clean_authorization_memo_is_set_aside(self):
        arts = copy.deepcopy(BASE_INCRIMINATORY)
        arts[2]["semantic_role"] = "exculpatory"
        arts[2]["description"] = "IT ticket SUP-2024-1120 aprobado por el manager"
        r = _score(_case(arts))
        assert r["refutation_context"]["eco_retained"] == []
        assert len(r["refutation_context"]["set_aside"]) == 1

    def test_single_source_with_mcp_tool(self):
        """El scorer y el tool MCP comparten el criterio (vigia.core.eco_check)."""
        from vigia.core.eco_check import (
            OBVIOUS_BAIT_TERMS, text_obvious_bait_hits, eco_overinterpretation_check,
        )
        assert "mimikatz" in OBVIOUS_BAIT_TERMS and "c&c" in OBVIOUS_BAIT_TERMS
        assert "onion" in text_obvious_bait_hits("traffic to platform.onion node")
        # set-level: >50% con bait → staging (lógica histórica del tool)
        r = eco_overinterpretation_check(["mimikatz dump", "hacked!", "clean log"])
        assert r["verdict"] == "POSSIBLE_SCENE_STAGING"
        r2 = eco_overinterpretation_check(["clean", "normal", "mimikatz"])
        assert r2["verdict"] == "NORMAL_DISTRIBUTION"


class TestSchemaValidation:
    def test_invalid_semantic_role_fails_loud(self):
        from vigia.pipeline.vigia_integration_bridge import (
            CaseSchemaError, validate_case_schema,
        )
        case = _case([_art("A1", 0.8)])
        case["artifacts"][0]["semantic_role"] = "exculpatoria"  # typo
        with pytest.raises(CaseSchemaError, match="semantic_role"):
            validate_case_schema(case)

    def test_valid_roles_pass(self):
        from vigia.pipeline.vigia_integration_bridge import validate_case_schema
        for role in ("incriminatory", "exculpatory", "contextual"):
            case = _case([_art("A1", 0.8, role=role)])
            validate_case_schema(case)  # no raise


class TestCorpusLabeledCases:
    """Regresión sobre el corpus etiquetado (worklist §5 + D2)."""

    def _blind(self, rel):
        c = json.loads((REPO / rel).read_text(encoding="utf-8"))
        b = {k: v for k, v in c.items() if k != "expected_verdict"}
        return _vigia_score(_normalize_case(copy.deepcopy(b)))

    def test_ben_001_recovers_to_noise(self):
        r = self._blind("data/cases/converted/VIGIA-BEN-001.json")
        assert r["verdict"] == "NOISE"
        assert len(r["refutation_context"]["set_aside"]) == 2

    def test_ben_014_retained_by_d1(self):
        """El análisis de tráfico Tor (onion/c&c) NO se aparta — D1 en acción."""
        r = self._blind("data/cases/converted/VIGIA-BEN-014.json")
        ret = r["refutation_context"]["eco_retained"]
        assert len(ret) == 1 and ret[0]["artifact_id"] == "ART-003"
        assert r["verdict"] == "SUSPICION"  # costo honesto de D1, documentado

    def test_break_002_noise_with_revised_label(self):
        """D2: pentest autorizado con memo exculpatorio = NOISE."""
        c = json.loads((REPO / "data/cases/converted/VIGIA_BREAK_002_VALID_BENIGN.json")
                       .read_text(encoding="utf-8"))
        assert c["expected_verdict"] == "NOISE"
        assert "_label_revision" in c
        r = self._blind("data/cases/converted/VIGIA_BREAK_002_VALID_BENIGN.json")
        assert r["verdict"] == "NOISE"
