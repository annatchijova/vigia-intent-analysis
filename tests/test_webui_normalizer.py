"""Tests for vigia.ui.normalizer — schema detection, verdict verbatim rules,
Fraction handling, MCP field-name tolerance."""

import json

import pytest

from vigia.ui import normalizer
from vigia.ui.normalizer import (
    SCHEMA_AGENT_AUDIT,
    SCHEMA_EBS_V1,
    SCHEMA_MCP,
    SCHEMA_UNKNOWN,
    decode_fractions,
    detect_schema,
    fraction_display,
    normalize,
)


# ---------------------------------------------------------------------------
# Fixtures: one minimal document per family, mirroring real corpus shapes.
# ---------------------------------------------------------------------------

def make_ebs_doc():
    return {
        "bundle_version": "1.0",
        "bundle_id": "EBS-TEST-001",
        "timestamp": "2026-06-10T19:28:16.852773+00:00",
        "evidence_graph": {"nodes": [], "edges": []},
        "decision_trace": {"decision": "ABSTAIN", "risk": 0.4,
                           "abstain_reason": "STANDALONE_SCORER_UNCALIBRATED_EBS_RISK"},
        "caie_analysis": {"case_id": "CASE-EBS", "verdict": "MALICE",
                          "confidence": 0.93, "reason": "temporal fracture"},
        "integrity": {"bundle_hash": "ab" * 32, "sealed_at": "2026-06-10T19:28:17+00:00"},
        "policy_spec": {}, "system_state": {}, "config_attestation": {},
    }


def make_agent_doc():
    frac = {"__fraction__": True, "num": 53, "den": 100}
    return {
        "case_id": "CASE-AGENT",
        "agent_verdict": "SUSPICION",
        "analysis_timestamp": "2026-07-23T16:51:24+00:00",
        "evidence_sha256": "cd" * 32,
        "audit_trail": {
            "total_entries": 2,
            "entries": [
                {"seq": 1, "timestamp": "t1", "action": "SESSION_START",
                 "tool": "vigia_agent", "note": "start"},
                {"seq": 2, "timestamp": "t2", "action": "AGENT_EXIT",
                 "tool": "vigia_agent", "note": "end"},
            ],
        },
        "pipeline_results": {
            "abduction": {"best_hypothesis": "SUSPICION_DETECTED",
                          "best_posterior": "53/100", "confidence": frac},
            "signals": [
                {"artifact_id": "ART-001", "evidence_type": "network",
                 "source": "log", "description": "egress observed",
                 "confidence": {"__fraction__": True, "num": 17, "den": 25},
                 "z_score": {"__fraction__": True, "num": 68, "den": 125}},
            ],
        },
        "sans_compliance": {"audit_trail": True},
    }


def make_mcp_doc_nested():
    """ROCBA style: finding_id, nested peirce_chain, mitre_ttps."""
    return {
        "case_id": "CASE-MCP",
        "overall_verdict": "MALICE",
        "overall_confidence": "HIGH",
        "investigation_timestamp": "2026-05-01T00:00:00Z",
        "findings": [
            {"finding_id": "F-001", "title": "masquerading", "verdict": "MALICE",
             "confidence": "HIGH", "status": "CONFIRMED",
             "peirce_chain": {"firstness": "a", "secondness": "b", "thirdness": "c"},
             "carnegie_pattern": "authority transfer",
             "mitre_ttps": ["T1036.005"], "devil_advocate": "could be legit",
             "artifacts": ["ART-001"], "tools_used": ["infer_intent"]},
        ],
        "tool_execution_log": [
            {"seq": 1, "event_id": "e1", "timestamp": "t", "mode": "claude_code",
             "tool": "generate_forensic_hash", "target": "x",
             "result_summary": "ok", "input_hash": "ff" * 32,
             "chain_version": "2", "prev_hash": "0" * 64, "entry_hash": "aa" * 32},
        ],
        "integrity": {"bundle_hash": "ee" * 32},
    }


def make_mcp_doc_flat():
    """OWL style: id, flattened firstness/secondness/thirdness, mitre, artifact."""
    return {
        "case_id": "CASE-OWL",
        "overall_verdict": "INTENT",
        "analysis_timestamp": "2026-04-01T00:00:00Z",
        "refutation_gate_log": [],
        "findings": [
            {"id": "F-001", "title": "flat finding", "verdict": "INTENT",
             "confidence": "MEDIUM", "status": "INFERRED",
             "firstness": "a", "secondness": "b", "thirdness": "c",
             "carnegie": "none", "mitre": ["T1070.006"], "artifact": "ART-9"},
        ],
        "tool_execution_log": [],
    }


# ---------------------------------------------------------------------------
# detect_schema
# ---------------------------------------------------------------------------

def test_detect_ebs_v1():
    assert detect_schema(make_ebs_doc()) == SCHEMA_EBS_V1


def test_detect_agent_audit():
    assert detect_schema(make_agent_doc()) == SCHEMA_AGENT_AUDIT


def test_detect_mcp_both_variants():
    assert detect_schema(make_mcp_doc_nested()) == SCHEMA_MCP
    assert detect_schema(make_mcp_doc_flat()) == SCHEMA_MCP


def test_detect_requires_two_markers():
    # one stray marker key must not classify
    assert detect_schema({"bundle_version": "1.0"}) == SCHEMA_UNKNOWN
    assert detect_schema({"findings": []}) == SCHEMA_UNKNOWN
    assert detect_schema({"agent_verdict": "NOISE"}) == SCHEMA_UNKNOWN


def test_detect_non_dict():
    assert detect_schema([1, 2]) == SCHEMA_UNKNOWN
    assert detect_schema("x") == SCHEMA_UNKNOWN


# ---------------------------------------------------------------------------
# Fractions — exactness is a Daubert property; floats are forbidden
# ---------------------------------------------------------------------------

def test_fraction_display_exact():
    assert fraction_display({"__fraction__": True, "num": 53, "den": 100}) == "53/100"
    assert fraction_display({"num": 1, "den": 2}) is None  # missing marker
    assert fraction_display(0.53) is None


def test_decode_fractions_never_produces_float():
    doc = make_agent_doc()
    decoded = decode_fractions(doc)

    def walk(obj):
        if isinstance(obj, float):
            # floats that existed before decoding are fine; but fraction
            # decoding must not create any — assert none appear under
            # decoded fraction nodes
            pytest.fail(f"unexpected float in decoded fractions: {obj}")
        if isinstance(obj, dict):
            if obj.get("is_fraction"):
                assert isinstance(obj["num"], int)
                assert isinstance(obj["den"], int)
                assert obj["display"] == f"{obj['num']}/{obj['den']}"
                return  # nothing else to check inside
            for v in obj.values():
                walk(v)
        elif isinstance(obj, list):
            for v in obj:
                walk(v)

    walk(decoded["pipeline_results"])


def test_decode_fractions_preserves_non_fraction_dicts():
    obj = {"a": {"num": 1, "den": 2}, "b": [1, "x"]}
    assert decode_fractions(obj) == obj


# ---------------------------------------------------------------------------
# normalize — verdicts verbatim, disagreement surfaced, never invented
# ---------------------------------------------------------------------------

def test_normalize_ebs_emits_both_verdicts_and_disagreement():
    norm = normalize(make_ebs_doc(), "results/x.json")
    assert norm["schema"] == SCHEMA_EBS_V1
    verdicts = {v["source"]: v["verdict"] for v in norm["verdicts"]}
    assert verdicts["decision_trace.decision (sealed EBS decision)"] == "ABSTAIN"
    assert verdicts["caie_analysis.verdict (CAIE forensic verdict)"] == "MALICE"
    assert norm["verdict_disagreement"] is True
    assert norm["integrity"]["bundle_hash"] == "ab" * 32


def test_normalize_ebs_agreeing_verdicts_no_flag():
    doc = make_ebs_doc()
    doc["caie_analysis"]["verdict"] = "ABSTAIN"
    norm = normalize(doc)
    assert norm["verdict_disagreement"] is False


def test_normalize_agent_fractions_render_as_ratio():
    norm = normalize(make_agent_doc(), "results/a.json")
    assert norm["schema"] == SCHEMA_AGENT_AUDIT
    assert norm["verdicts"][0]["verdict"] == "SUSPICION"
    # abduction verdict carries the fraction confidence as "53/100"
    ab = [v for v in norm["verdicts"] if "abduction" in v["source"]][0]
    assert ab["confidence"] == "53/100"
    sig = norm["findings"][0]
    assert sig["confidence"] == "17/25"
    assert sig["z_score"] == "68/125"
    assert sig["kind"] == "pipeline_signal"
    assert norm["audit_trail"]["present"] is True
    assert norm["audit_trail"]["entry_count"] == 2


def test_normalize_mcp_nested_variant():
    norm = normalize(make_mcp_doc_nested())
    assert norm["schema"] == SCHEMA_MCP
    f = norm["findings"][0]
    assert f["id"] == "F-001"
    assert f["peirce"] == {"firstness": "a", "secondness": "b", "thirdness": "c"}
    assert f["mitre_ttps"] == ["T1036.005"]
    assert f["carnegie"] == "authority transfer"
    assert norm["tool_log"]["present"] is True
    assert norm["tool_log"]["chain_version"] == "2"


def test_normalize_mcp_flat_variant_tolerated():
    norm = normalize(make_mcp_doc_flat())
    f = norm["findings"][0]
    assert f["id"] == "F-001"
    assert f["peirce"] == {"firstness": "a", "secondness": "b", "thirdness": "c"}
    assert f["mitre_ttps"] == ["T1070.006"]
    assert f["carnegie"] == "none"
    assert f["artifacts"] == ["ART-9"]


def test_normalize_missing_fields_warn_not_invent():
    doc = make_mcp_doc_nested()
    del doc["findings"][0]["peirce_chain"]
    del doc["overall_verdict"]
    doc["refutation_gate_log"] = []  # keep it detectable as MCP
    norm = normalize(doc)
    assert norm["schema"] == SCHEMA_MCP
    assert norm["findings"][0]["peirce"] is None
    assert norm["verdicts"] == []
    assert any("overall_verdict" in w for w in norm["warnings"])
    assert any("Peirce" in w for w in norm["warnings"])


def test_normalize_unknown_is_honest():
    norm = normalize({"hello": "world"}, "results/weird.json")
    assert norm["schema"] == SCHEMA_UNKNOWN
    assert norm["verdicts"] == []
    assert norm["findings"] == []
    assert any("unrecognized" in w.lower() for w in norm["warnings"])


def test_legacy_agent_bundle_without_agent_verdict():
    """Pre-B-097 agent bundles lack agent_verdict but share the family shape."""
    doc = make_agent_doc()
    del doc["agent_verdict"]
    assert detect_schema(doc) == SCHEMA_AGENT_AUDIT
    norm = normalize(doc)
    assert all(v["source"] != "agent_verdict (sealed agent bundle)"
               for v in norm["verdicts"])
    assert any("agent_verdict" in w for w in norm["warnings"])


def test_disagreement_only_within_canonical_scale():
    """Abduction hypotheses (SUSPICION_DETECTED etc.) are another vocabulary,
    not verdicts — they must never trigger the disagreement flag."""
    norm = normalize(make_agent_doc())  # SUSPICION + SUSPICION_DETECTED
    assert norm["verdict_disagreement"] is False


def test_normalize_never_computes_a_verdict():
    """No normalized output may contain a verdict value absent from the raw doc."""
    for doc in (make_ebs_doc(), make_agent_doc(),
                make_mcp_doc_nested(), make_mcp_doc_flat()):
        raw = json.dumps(doc)
        norm = normalize(doc)
        for v in norm["verdicts"]:
            assert v["verdict"] in raw, (
                f"verdict {v['verdict']!r} not present verbatim in the raw bundle"
            )


# ---------------------------------------------------------------------------
# MCP field-name tolerance: KIWI-series bundles (final_verdict, bundle_sha256)
# ---------------------------------------------------------------------------

def make_mcp_doc_kiwi():
    """KIWI style: final_verdict instead of overall_verdict, top-level
    bundle_sha256 / primary_evidence_sha256 / timestamp_sealed / sans_phase."""
    return {
        "case_id": "CASE-KIWI",
        "final_verdict": "SUSPICION",
        "timestamp_sealed": "2026-06-20T10:00:00Z",
        "primary_evidence_sha256": "11" * 32,
        "bundle_sha256": "22" * 32,
        "sans_phase": "Phase 5 — Lessons Learned",
        "executive_summary": "resumen",
        "findings": [
            {"finding_id": "F-001", "title": "t", "verdict": "SUSPICION",
             "confidence": "MEDIUM", "status": "INFERRED",
             "firstness": "a", "secondness": "b", "thirdness": "c"},
        ],
        "tool_execution_log": [],
    }


def test_detect_mcp_final_verdict_variant():
    assert detect_schema(make_mcp_doc_kiwi()) == SCHEMA_MCP
    # still two markers: a lone final_verdict must not classify
    assert detect_schema({"final_verdict": "NOISE"}) == SCHEMA_UNKNOWN


def test_normalize_mcp_final_verdict_read_verbatim_with_custody_anchors():
    norm = normalize(make_mcp_doc_kiwi())
    assert norm["schema"] == SCHEMA_MCP
    assert [(v["source"], v["verdict"], v["raw_pointer"]) for v in norm["verdicts"]] == [
        ("final_verdict", "SUSPICION", "/final_verdict"),
    ]
    assert norm["sealed_at"] == "2026-06-20T10:00:00Z"
    assert norm["integrity"]["bundle_sha256"] == "22" * 32
    assert norm["integrity"]["primary_evidence_sha256"] == "11" * 32
    assert norm["extra"]["sans_phase"] == "Phase 5 — Lessons Learned"
    assert norm["extra"]["executive_summary"] == "resumen"
    assert not any("overall_verdict" in w for w in norm["warnings"])
    assert not any("timestamp" in w for w in norm["warnings"])
