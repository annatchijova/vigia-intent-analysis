"""vigia.report.adapter — extraction only, never derivation.

Proves, on the three bundle families:
  * ``load_view`` classifies each family and never mutates the parsed document
    (digest of the raw dict identical before and after every extractor runs,
    mirroring tests/test_reasoning_trace_bundle_gate.py);
  * ``render_scalar`` renders a serialized Fraction as ``N/D`` and a sealed
    float as its own JSON literal, and never rounds;
  * the KIWI-series MCP shape (``final_verdict``, ``refutation_gate_log`` as a
    single object, ``bundle_sha256``) is read, not warned away.
"""
from __future__ import annotations

import hashlib
import json

import pytest

from tests.test_webui_normalizer import (
    make_agent_doc,
    make_ebs_doc,
    make_mcp_doc_flat,
    make_mcp_doc_nested,
)
from vigia.report import adapter
from vigia.report.adapter import BundleView, load_view, render_scalar


def _bytes(doc: dict) -> bytes:
    return json.dumps(doc, indent=2, sort_keys=True, ensure_ascii=True).encode("utf-8")


def _digest(doc: dict) -> str:
    return hashlib.sha256(
        json.dumps(doc, indent=2, sort_keys=True, ensure_ascii=True, default=str).encode()
    ).hexdigest()


def make_mcp_doc_kiwi():
    """KIWI-006 style: final_verdict, refutation_gate_log as one object,
    top-level bundle_sha256 / primary_evidence_sha256 / timestamp_sealed."""
    return {
        "bundle_id": "VIGIA-KIWI-006-BUNDLE",
        "case_id": "VIGIA-KIWI-006",
        "mode": "Claude Code + MCP",
        "timestamp_sealed": "2026-06-20T10:00:00Z",
        "primary_evidence_sha256": "11" * 32,
        "sans_phase": "Phase 5 — Lessons Learned",
        "final_verdict": "SUSPICION",
        "executive_summary": "Resumen ejecutivo del investigador.",
        "findings": [
            {"finding_id": "F-001", "title": "Linguistic contagion", "verdict": "SUSPICION",
             "confidence": "MEDIUM", "status": "INFERRED",
             "firstness": "a", "secondness": "b", "thirdness": "c",
             "mitre_ttps": ["T1585.001 (Establish Accounts)"],
             "devil_advocate": "witnesses may share vocabulary naturally",
             "artifacts": ["A01"], "tools_used": ["analyze_stylometry"]},
        ],
        "refutation_gate_log": {
            "finding_id": "CANDIDATE-INTENT-001", "candidate_verdict": "INTENT",
            "candidate_confidence": 85, "gate_applied": "Daubert Corroboration Gate",
            "gate_result": "CANDIDATE REJECTED pre-emission. Emitted as SUSPICION.",
        },
        "tool_execution_log": [
            {"seq": 1, "tool": "reason_with_llm", "target": "probe",
             "result_summary": "ok", "chain_version": "2"},
            {"seq": 2, "tool": "analyze_stylometry", "target": "A01",
             "result_summary": "70%", "chain_version": "2"},
        ],
        "known_limitations": ["L-020 no granular audit_trail"],
        "bundle_sha256": "22" * 32,
    }


ALL_DOCS = {
    "ebs": make_ebs_doc, "agent": make_agent_doc, "mcp_nested": make_mcp_doc_nested,
    "mcp_flat": make_mcp_doc_flat, "mcp_kiwi": make_mcp_doc_kiwi,
}


def _run_every_extractor(view: BundleView) -> None:
    adapter.custody_fields(view)
    adapter.verdict_entries(view)
    adapter.finding_entries(view)
    adapter.devil_advocate_entries(view)
    adapter.refutation_gate_entries(view)
    adapter.exact_scores(view)
    adapter.tool_log_summary(view)
    adapter.mitre_ids(view)
    adapter.known_limitations(view)
    adapter.sans_phase_text(view)
    adapter.executive_summary(view)
    adapter.narrative_text(view)


# ---------------------------------------------------------------------------
# load_view
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("name", sorted(ALL_DOCS))
def test_load_view_never_mutates_the_document(name):
    doc = ALL_DOCS[name]()
    raw = _bytes(doc)
    view = load_view(raw, source_name=f"dir/{name}_bundle.json")
    before = _digest(view.raw)
    _run_every_extractor(view)
    assert _digest(view.raw) == before, f"an extractor mutated the parsed bundle ({name})"
    assert view.source_sha256 == hashlib.sha256(raw).hexdigest()
    assert view.source_name == f"{name}_bundle.json", "only the basename may appear"


def test_load_view_schema_per_family():
    assert load_view(_bytes(make_ebs_doc())).schema == "ebs_v1"
    assert load_view(_bytes(make_agent_doc())).schema == "agent_audit"
    assert load_view(_bytes(make_mcp_doc_nested())).schema == "mcp_investigation"
    assert load_view(_bytes(make_mcp_doc_kiwi())).schema == "mcp_investigation"
    assert load_view(b'{"hello": 1}').schema == "unknown"


def test_load_view_rejects_non_json_and_non_object():
    with pytest.raises(ValueError):
        load_view(b"not json")
    with pytest.raises(ValueError):
        load_view(b"[1, 2, 3]")
    with pytest.raises(ValueError):
        load_view(b"\xff\xfe")


# ---------------------------------------------------------------------------
# render_scalar
# ---------------------------------------------------------------------------

def test_render_scalar_fraction_exact_never_float():
    assert render_scalar({"__fraction__": True, "num": 19, "den": 20}) == "19/20"
    assert render_scalar({"is_fraction": True, "display": "1/3", "num": 1, "den": 3}) == "1/3"
    out = render_scalar({"__fraction__": True, "num": 1, "den": 3})
    assert "0.3" not in out and "." not in out


def test_render_scalar_float_is_the_sealed_literal():
    # 0.3346 is a sealed float in results/srl2018/*; json.dumps round-trips it exactly.
    assert render_scalar(0.3346) == "0.3346"
    assert render_scalar(0.67) == "0.67"
    assert render_scalar(1.0) == "1.0"
    # Never rounded: a 6-decimal literal stays 6 decimals.
    assert render_scalar(0.123456) == "0.123456"


def test_render_scalar_other_types():
    assert render_scalar(None) is None
    assert render_scalar(True) == "true"
    assert render_scalar(False) == "false"
    assert render_scalar(7) == "7"
    assert render_scalar("MALICE") == "MALICE"
    assert render_scalar({"b": 1, "a": [1, 2]}) == '{"a": [1, 2], "b": 1}'
    assert render_scalar(["ñ"]) == '["ñ"]'  # no ASCII escaping of sealed text


# ---------------------------------------------------------------------------
# Extractors, per family
# ---------------------------------------------------------------------------

def test_custody_fields_ebs_present_and_absent():
    view = load_view(_bytes(make_ebs_doc()))
    fields = dict(adapter.custody_fields(view))
    assert fields["integrity.bundle_hash"] == "ab" * 32
    assert fields["integrity.sealed_at"] == "2026-06-10T19:28:17+00:00"
    assert fields["integrity.analysis_fingerprint"] is None  # absent -> gap, not invented
    assert list(fields)[0] == "integrity.bundle_hash"       # fixed order


def test_custody_fields_agent():
    view = load_view(_bytes(make_agent_doc()))
    fields = dict(adapter.custody_fields(view))
    assert fields["evidence_sha256"] == "cd" * 32
    assert fields["audit_trail.total_entries"] == "2"
    assert fields["runtime_fingerprint"] is None


def test_custody_fields_mcp_kiwi_names():
    view = load_view(_bytes(make_mcp_doc_kiwi()))
    fields = dict(adapter.custody_fields(view))
    assert fields["bundle_sha256"] == "22" * 32
    assert fields["primary_evidence_sha256"] == "11" * 32
    assert fields["timestamp_sealed"] == "2026-06-20T10:00:00Z"
    assert fields["chain_tip_sha256"] is None


def test_verdict_entries_mcp_final_verdict_is_read_verbatim():
    view = load_view(_bytes(make_mcp_doc_kiwi()))
    entries = adapter.verdict_entries(view)
    assert [(e["source"], e["verdict"]) for e in entries] == [("final_verdict", "SUSPICION")]
    assert not any("overall_verdict" in g for g in view.gaps)


def test_verdict_entries_agent_keeps_both_fields():
    view = load_view(_bytes(make_agent_doc()))
    entries = adapter.verdict_entries(view)
    assert entries[0]["verdict"] == "SUSPICION"
    assert entries[1]["verdict"] == "SUSPICION_DETECTED"
    assert entries[1]["confidence"] == "53/100"


def test_devil_advocate_entries_pointers():
    assert adapter.devil_advocate_entries(load_view(_bytes(make_mcp_doc_kiwi()))) == [
        ("/findings/0/devil_advocate", "witnesses may share vocabulary naturally"),
    ]
    assert adapter.devil_advocate_entries(load_view(_bytes(make_ebs_doc()))) == []


def test_refutation_gate_entries_kiwi_single_object():
    view = load_view(_bytes(make_mcp_doc_kiwi()))
    gates = adapter.refutation_gate_entries(view)
    assert len(gates) == 1
    assert gates[0]["_pointer"] == "/refutation_gate_log"
    assert gates[0]["candidate_verdict"] == "INTENT"


def test_refutation_gate_entries_agent_matches_gate_actions():
    doc = make_agent_doc()
    doc["audit_trail"]["entries"].append(
        {"seq": 3, "action": "CONTRADICTION_DETECTOR", "note": "BEFORE: MALICE | AFTER: SUSPICION"}
    )
    view = load_view(_bytes(doc))
    gates = adapter.refutation_gate_entries(view)
    assert [g["seq"] for g in gates] == [3]
    assert gates[0]["_pointer"] == "/audit_trail/entries/2"


def test_refutation_gate_entries_ebs_fields():
    view = load_view(_bytes(make_ebs_doc()))
    ptrs = {g["_pointer"]: g["value"] for g in adapter.refutation_gate_entries(view)}
    assert ptrs["/decision_trace/abstain_reason"] == "STANDALONE_SCORER_UNCALIBRATED_EBS_RISK"


def test_exact_scores_render_literals_only():
    ebs = dict(adapter.exact_scores(load_view(_bytes(make_ebs_doc()))))
    assert ebs["/decision_trace/risk"] == "0.4"
    assert ebs["/caie_analysis/confidence"] == "0.93"
    agent = dict(adapter.exact_scores(load_view(_bytes(make_agent_doc()))))
    assert agent["/pipeline_results/abduction/confidence"] == "53/100"
    assert agent["/pipeline_results/signals/0/z_score"] == "68/125"
    kiwi = dict(adapter.exact_scores(load_view(_bytes(make_mcp_doc_kiwi()))))
    assert kiwi["/refutation_gate_log/candidate_confidence"] == "85"


def test_tool_log_summary_mcp_histogram_sorted_and_capped():
    view = load_view(_bytes(make_mcp_doc_kiwi()))
    s = adapter.tool_log_summary(view)
    assert s["kind"] == "tool_execution_log"
    assert s["entry_count"] == 2
    assert s["chain_version"] == "2"
    assert s["chain_tip_present"] is False
    assert s["histogram"] == [("analyze_stylometry", 1), ("reason_with_llm", 1)]
    assert s["truncated"] is False


def test_tool_log_summary_agent_counts_sha256():
    doc = make_agent_doc()
    doc["audit_trail"]["entries"][0]["entry_sha256"] = "0" * 64
    s = adapter.tool_log_summary(load_view(_bytes(doc)))
    assert s["kind"] == "audit_trail"
    assert s["entries_with_sha256"] == 1
    assert s["histogram"] == [("AGENT_EXIT", 1), ("SESSION_START", 1)]


def test_mitre_ids_parsed_from_free_text_and_labeled():
    kiwi = adapter.mitre_ids(load_view(_bytes(make_mcp_doc_kiwi())))
    assert kiwi == [("T1585.001", "findings.mitre_ttps")]
    doc = make_agent_doc()
    doc["pipeline_results"]["signals"][0]["description"] = "Process hollowing (T1055.012)"
    agent = adapter.mitre_ids(load_view(_bytes(doc)))
    assert agent == [("T1055.012", "signals.description")]
    assert adapter.mitre_ids(load_view(_bytes(make_ebs_doc()))) == []


def test_known_limitations_and_summary_verbatim():
    view = load_view(_bytes(make_mcp_doc_kiwi()))
    assert adapter.known_limitations(view) == ["L-020 no granular audit_trail"]
    assert adapter.executive_summary(view) == "Resumen ejecutivo del investigador."
    assert adapter.sans_phase_text(view) == "Phase 5 — Lessons Learned"
    assert adapter.narrative_text(view) is None
