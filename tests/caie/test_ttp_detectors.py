"""
Regression tests for the canonical TTP detectors (2026-07-12).

Ref: docs/CASE_RECOVERY_20260712.md. Three structured-metadata fracture
detectors for masquerade / defense-evasion / injection IoIs, plus the
scorer-side intake-abstain gate. Each keys only on structured metadata
(never free text, never annotation fields) and is FP-safe corpus-wide.
"""

import copy
import logging

logging.disable(logging.CRITICAL)

from vigia.tools.caie import CrossArtifactIncongruenceEngine, Artifact  # noqa: E402
from vigia_scorer import _vigia_score  # noqa: E402


def _types(*artifacts):
    e = CrossArtifactIncongruenceEngine()
    for a in artifacts:
        e.add_artifact(a)
    return {f.fracture_type for f in e.detect_fractures()}


def _art(evidence_type="memory_process", raw=0.6, metadata=None, aid="a"):
    return Artifact(
        source_tool="test", evidence_type=evidence_type, raw_score=raw,
        description="test artifact", metadata=metadata or {},
        provenance_chain=["sha256:x"],
    )


class TestProcessMasquerade:

    def test_fires_on_basename_match_path_differ(self):
        a = _art(metadata={"malicious_path": "/var/tmp/systemd-logind",
                           "legitimate_path": "/usr/lib/systemd/systemd-logind"})
        assert "PROCESS_MASQUERADE" in _types(a)

    def test_silent_when_paths_identical(self):
        a = _art(metadata={"malicious_path": "/usr/lib/systemd/systemd-logind",
                           "legitimate_path": "/usr/lib/systemd/systemd-logind"})
        assert "PROCESS_MASQUERADE" not in _types(a)

    def test_silent_when_basename_differs(self):
        # different program names in different dirs is not masquerade
        a = _art(metadata={"malicious_path": "/tmp/miner",
                           "legitimate_path": "/usr/bin/ls"})
        assert "PROCESS_MASQUERADE" not in _types(a)

    def test_silent_without_the_structured_fields(self):
        a = _art(metadata={"description": "svchost from a weird path"})
        assert "PROCESS_MASQUERADE" not in _types(a)


class TestDefenseEvasion:

    def test_fires_on_vsc_deletion(self):
        a = _art(metadata={"deleted_vsc": True})
        assert "DEFENSE_EVASION_ARTIFACT" in _types(a)

    def test_fires_on_firewall_off(self):
        a = _art(metadata={"firewall_state": "off"})
        assert "DEFENSE_EVASION_ARTIFACT" in _types(a)

    def test_silent_on_firewall_on(self):
        a = _art(metadata={"firewall_state": "on"})
        assert "DEFENSE_EVASION_ARTIFACT" not in _types(a)

    def test_silent_when_vsc_flag_false(self):
        a = _art(metadata={"deleted_vsc": False})
        assert "DEFENSE_EVASION_ARTIFACT" not in _types(a)


class TestProcessInjection:

    def test_fires_on_hollowing(self):
        a = _art(metadata={"injection_technique": "process_hollowing"})
        assert "PROCESS_INJECTION_ANTIFORENSIC" in _types(a)

    def test_fires_on_hidden_pid(self):
        a = _art(metadata={"pid_hidden": True})
        assert "PROCESS_INJECTION_ANTIFORENSIC" in _types(a)

    def test_silent_on_unknown_technique(self):
        a = _art(metadata={"injection_technique": "none"})
        assert "PROCESS_INJECTION_ANTIFORENSIC" not in _types(a)


class TestClaimVsRecordFabrication:

    def test_fires_on_claimed_refuted_pair(self):
        a = _art(evidence_type="log_entry", raw=0.06,
                 metadata={"claimed_manager_talk": True, "communication_found": False})
        assert "CLAIM_VS_RECORD_FABRICATION" in _types(a)

    def test_silent_when_claim_corroborated(self):
        a = _art(evidence_type="log_entry",
                 metadata={"claimed_manager_talk": True, "communication_found": True})
        assert "CLAIM_VS_RECORD_FABRICATION" not in _types(a)

    def test_silent_without_a_claim(self):
        a = _art(evidence_type="log_entry",
                 metadata={"communication_found": False})
        assert "CLAIM_VS_RECORD_FABRICATION" not in _types(a)


class TestDocumentForgeryMassExtension:

    def test_fires_on_date_regex_substitution(self):
        a = _art(evidence_type="log_entry", raw=0.09,
                 metadata={"modification_pattern": "date_regex_substitution"})
        assert "DOCUMENT_FORGERY" in _types(a)

    def test_silent_on_other_modification_patterns(self):
        a = _art(evidence_type="log_entry",
                 metadata={"modification_pattern": "manual_edit"})
        assert "DOCUMENT_FORGERY" not in _types(a)


class TestIntakeAbstainGate:

    _BASE = {
        "case_id": "INTAKE-TEST",
        "artifacts": [
            {"artifact_id": "h", "evidence_type": "file_hash", "source_tool": "hash",
             "raw_score": 0.05, "provenance_chain": ["sha256:z"],
             "description": "intake hash", "metadata": {}},
        ],
    }

    def _score(self, status=None, analysis_status=None, user_flag=None):
        case = copy.deepcopy(self._BASE)
        md = case["artifacts"][0]["metadata"]
        if status is not None:
            md["status"] = status
        if analysis_status is not None:
            md["analysis_status"] = analysis_status
        if user_flag is not None:
            md[user_flag] = False
        return _vigia_score(case)

    def test_baseline_intake_is_noise_without_marker(self):
        assert self._score()["verdict"] == "NOISE"

    def test_intake_only_status_yields_abstain(self):
        assert self._score(status="INTAKE_ONLY — extraction pending")["verdict"] == "ABSTAIN"

    def test_pending_analysis_status_yields_abstain(self):
        assert self._score(analysis_status="PENDING — requires extraction")["verdict"] == "ABSTAIN"

    def test_no_user_data_yields_abstain(self):
        assert self._score(user_flag="user_data_found")["verdict"] == "ABSTAIN"
        assert self._score(user_flag="user_content_found")["verdict"] == "ABSTAIN"
        assert self._score(user_flag="user_partition")["verdict"] == "ABSTAIN"

    def test_gate_never_softens_a_malice(self):
        # A case that scores MALICE must stay MALICE even if it carries an
        # intake marker (the gate only fires when the verdict is NOISE).
        case = copy.deepcopy(self._BASE)
        case["artifacts"] = [
            {"artifact_id": "m", "evidence_type": "memory_process", "source_tool": "vol",
             "raw_score": 0.9, "provenance_chain": ["sha256:a"],
             "description": "hollowed process",
             "metadata": {"injection_technique": "process_hollowing",
                          "user_data_found": False}},
            {"artifact_id": "n", "evidence_type": "network_flow", "source_tool": "net",
             "raw_score": 0.85, "provenance_chain": ["sha256:b"],
             "description": "c2", "metadata": {}},
            {"artifact_id": "l", "evidence_type": "log_entry", "source_tool": "log",
             "raw_score": 0.8, "provenance_chain": ["sha256:c"],
             "description": "persistence", "metadata": {}},
        ]
        assert _vigia_score(case)["verdict"] == "MALICE"
