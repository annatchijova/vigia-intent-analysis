"""
Tests B-068 — el gate de corroboración de MALICE cuenta solo evidencia técnica.

FP real: VIGIA-NGDC-003 (National Gallery DC — intención genuinamente
disputada: monitoreo parental legal vs espionaje conyugal ilegal, artefactos
idénticos; expected SUSPICION) emitía MALICE porque el gate de corroboración
(n_artifacts >= 4 OR n_types >= 3) contaba 2 artefactos de documentación del
escenario (behavioral_context, outcome_signal) como si fueran fuentes
independientes. Daubert: "two independent sources" = clases de evidencia de
dispositivo; la narrativa del escenario describe motivo, no corrobora malicia.
"""

import json

from vigia_scorer import _vigia_score


def _case(n):
    return json.load(open(f"data/cases/VIGIA-NGDC-{n}.json"))


class TestB068NGDCRegression:
    def test_ngdc003_disputed_intent_is_suspicion(self):
        r = _vigia_score(_case("003"))
        assert r["verdict"] == "SUSPICION"
        assert "B-068" in r["reason"]

    def test_ngdc_001_002_004_remain_malice(self):
        for n in ("001", "002", "004"):
            r = _vigia_score(_case(n))
            assert r["verdict"] == "MALICE", f"NGDC-{n}: {r['verdict']}"


def _artifact(i, etype, raw=0.85):
    return {
        "artifact_id": f"A{i}", "evidence_type": etype, "raw_score": raw,
        "source_tool": f"tool_{i}", "description": f"artifact {i}",
        "prior_trust": 0.85, "timestamp": f"2026-01-0{i+1}T10:00:00Z",
        "provenance_chain": ["acquire", "hash", "extract"],
        "metadata": {},
    }


class TestB068SyntheticGate:
    def test_context_padding_cannot_corroborate_malice(self):
        """3 técnicos (2 clases) + 2 contextuales: el score cruza 0.33 pero
        la corroboración técnica es insuficiente → SUSPICION."""
        arts = [
            _artifact(0, "malware_infrastructure"),
            _artifact(1, "keylogger_capture"),
            _artifact(2, "keylogger_capture"),
            _artifact(3, "behavioral_context"),
            _artifact(4, "outcome_signal"),
        ]
        r = _vigia_score({"case_id": "B068-CTX", "artifacts": arts})
        assert r["verdict"] == "SUSPICION"
        assert "context/narrative" in r["reason"]

    def test_four_technical_artifacts_still_reach_malice(self):
        """Misma forma pero con 4 artefactos técnicos: el gate pasa por
        evidencia de dispositivo real → MALICE se mantiene alcanzable."""
        arts = [
            _artifact(0, "malware_infrastructure"),
            _artifact(1, "keylogger_capture"),
            _artifact(2, "keylogger_capture"),
            _artifact(3, "email_content"),
            _artifact(4, "behavioral_context"),
        ]
        r = _vigia_score({"case_id": "B068-TECH", "artifacts": arts})
        assert r["verdict"] == "MALICE"

    def test_three_technical_classes_also_pass(self):
        """La rama OR del gate: 3 clases técnicas distintas con 3 artefactos."""
        arts = [
            _artifact(0, "malware_infrastructure"),
            _artifact(1, "keylogger_capture"),
            _artifact(2, "email_content"),
            _artifact(3, "outcome_signal"),
        ]
        r = _vigia_score({"case_id": "B068-3CLS", "artifacts": arts})
        assert r["verdict"] == "MALICE"

    def test_pure_context_case_cannot_reach_malice(self):
        """Un caso armado SOLO con clases contextuales nunca sella MALICE,
        sin importar los raw_scores."""
        arts = [
            _artifact(i, t, raw=0.95) for i, t in enumerate(
                ("behavioral_context", "behavioral_profile", "outcome_signal",
                 "osint", "acquisition_context")
            )
        ]
        r = _vigia_score({"case_id": "B068-PURE", "artifacts": arts})
        assert r["verdict"] != "MALICE"
