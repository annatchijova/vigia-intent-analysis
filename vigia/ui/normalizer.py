"""Bundle normalizer for the VIGÍA web UI.

The corpus under ``results/``, ``cases/`` and ``vigia/results/`` holds three
incompatible bundle families (documented in ``docs/EXECUTION_MODES.md``):

- ``ebs_v1``            — sealed EBS v1 pipeline bundle (``bundle_version``,
                          ``evidence_graph``, ``decision_trace``, ``integrity``).
- ``agent_audit``       — ``vigia_agent.py::_seal_bundle()`` output
                          (``agent_verdict``, ``audit_trail``, ``pipeline_results``;
                          numbers serialized as exact Fractions).
- ``mcp_investigation`` — Mode 2 Claude Code / MCP investigation bundle
                          (``findings[]``, ``tool_execution_log[]``); field names
                          vary within the family.

Invariants honored here:

- Verdicts are copied verbatim from the bundle — never computed, never
  reconciled. When a bundle carries more than one verdict-bearing field
  (e.g. EBS v1 sealed ``decision_trace.decision`` vs ``caie_analysis.verdict``,
  see docs/VIGIA_TECHNICAL_STATE_EN.md §12.3), ALL are emitted and a
  ``verdict_disagreement`` flag is set when they differ.
- Serialized Fractions ``{"__fraction__": true, "num": N, "den": D}`` are
  rendered as the exact string ``"N/D"``. They are never converted to float:
  exact arithmetic is a stated Daubert property of the deterministic core.
- Missing fields become ``None`` plus an entry in ``warnings[]`` — never
  an invented value. Unrecognized documents are labeled ``unknown`` and
  render raw only (honest degradation).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

SCHEMA_EBS_V1 = "ebs_v1"
SCHEMA_AGENT_AUDIT = "agent_audit"
SCHEMA_MCP = "mcp_investigation"
SCHEMA_UNKNOWN = "unknown"

_KNOWN_VERDICTS = ("NOISE", "SUSPICION", "INTENT", "MALICE", "ABSTAIN")


# ---------------------------------------------------------------------------
# Fractions
# ---------------------------------------------------------------------------

def is_serialized_fraction(obj: Any) -> bool:
    return (
        isinstance(obj, dict)
        and obj.get("__fraction__") is True
        and isinstance(obj.get("num"), int)
        and isinstance(obj.get("den"), int)
    )


def fraction_display(obj: Any) -> Optional[str]:
    """Exact ``"N/D"`` rendering of a serialized Fraction. No float ever."""
    if not is_serialized_fraction(obj):
        return None
    return f"{obj['num']}/{obj['den']}"


def decode_fractions(obj: Any) -> Any:
    """Recursively replace serialized Fractions with a display-safe dict.

    ``{"__fraction__":true,"num":N,"den":D}`` becomes
    ``{"is_fraction":true,"display":"N/D","num":N,"den":D}``.
    Integers stay exact; nothing is coerced to float.
    """
    if is_serialized_fraction(obj):
        return {
            "is_fraction": True,
            "display": fraction_display(obj),
            "num": obj["num"],
            "den": obj["den"],
        }
    if isinstance(obj, dict):
        return {k: decode_fractions(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [decode_fractions(v) for v in obj]
    return obj


def _scalar_display(value: Any) -> Any:
    """Render a scalar that may be a serialized Fraction as its display form."""
    if is_serialized_fraction(value):
        return fraction_display(value)
    return value


# ---------------------------------------------------------------------------
# Schema detection
# ---------------------------------------------------------------------------

def detect_schema(doc: Any) -> str:
    """Classify a parsed bundle document. Each detector requires at least two
    marker keys so a single stray field cannot misfile a bundle."""
    if not isinstance(doc, dict):
        return SCHEMA_UNKNOWN

    if "bundle_version" in doc and (
        "evidence_graph" in doc or "decision_trace" in doc
    ) and "integrity" in doc:
        return SCHEMA_EBS_V1

    # agent_verdict is absent in pre-B-097 legacy agent bundles; the
    # audit_trail + pipeline_results pair identifies the family regardless.
    if ("audit_trail" in doc and "pipeline_results" in doc) or (
        "agent_verdict" in doc
        and ("audit_trail" in doc or "pipeline_results" in doc)
    ):
        return SCHEMA_AGENT_AUDIT

    # Field names vary within the MCP family: the KIWI-series bundles sealed
    # the top-level verdict as ``final_verdict`` instead of ``overall_verdict``.
    if ("findings" in doc or "tool_execution_log" in doc) and (
        "overall_verdict" in doc
        or "final_verdict" in doc
        or "refutation_gate_log" in doc
        or "mitre_ttps_aggregate" in doc
    ):
        return SCHEMA_MCP

    return SCHEMA_UNKNOWN


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _first_key(doc: dict, keys: tuple, warnings: list, label: str) -> Any:
    """Return the first present key's value; warn (once) when all are absent."""
    for k in keys:
        if k in doc:
            return doc[k]
    warnings.append(f"missing field: {label} (looked for {', '.join(keys)})")
    return None


def _verdict_entry(source: str, verdict: Any, confidence: Any = None,
                   raw_pointer: str = "") -> dict:
    return {
        "source": source,
        "verdict": verdict,
        "confidence": _scalar_display(confidence),
        "raw_pointer": raw_pointer,
    }


def _disagreement(verdicts: list) -> bool:
    """True when two verdict entries on the canonical NOISE..MALICE/ABSTAIN
    scale differ. Entries in other vocabularies (e.g. abduction hypotheses
    like SUSPICION_DETECTED) are shown but never counted as disagreement —
    they are not verdicts."""
    seen = {
        v["verdict"] for v in verdicts
        if isinstance(v["verdict"], str) and v["verdict"] in _KNOWN_VERDICTS
    }
    return len(seen) > 1


# ---------------------------------------------------------------------------
# Per-schema normalizers
# ---------------------------------------------------------------------------

def _normalize_ebs_v1(doc: dict, warnings: list) -> dict:
    decision_trace = doc.get("decision_trace") or {}
    caie = doc.get("caie_analysis") or {}
    integrity = doc.get("integrity") or {}

    verdicts = []
    if "decision" in decision_trace:
        verdicts.append(_verdict_entry(
            "decision_trace.decision (sealed EBS decision)",
            decision_trace.get("decision"),
            raw_pointer="/decision_trace/decision",
        ))
    else:
        warnings.append("missing field: decision_trace.decision")
    if "verdict" in caie:
        verdicts.append(_verdict_entry(
            "caie_analysis.verdict (CAIE forensic verdict)",
            caie.get("verdict"),
            confidence=caie.get("confidence"),
            raw_pointer="/caie_analysis/verdict",
        ))

    return {
        "case_id": caie.get("case_id") or doc.get("bundle_id"),
        "sealed_at": integrity.get("sealed_at") or doc.get("timestamp"),
        "verdicts": verdicts,
        "findings": [],
        "tool_log": {"present": False, "entry_count": 0, "chain_version": None},
        "audit_trail": {"present": False, "entry_count": 0, "entries_preview": []},
        "integrity": {
            "bundle_hash": integrity.get("bundle_hash"),
        },
        "extra": decode_fractions({
            "decision_trace": decision_trace,
            "caie_reason": caie.get("reason"),
            "caie_composite_score": caie.get("composite_score"),
            "caie_peirce_chain": caie.get("peirce_chain"),
            "config_attestation": doc.get("config_attestation"),
        }),
    }


def _normalize_agent_audit(doc: dict, warnings: list) -> dict:
    audit = doc.get("audit_trail") or {}
    pipeline = doc.get("pipeline_results") or {}
    abduction = pipeline.get("abduction") or {}
    entries = audit.get("entries") or []

    verdicts = []
    if "agent_verdict" in doc:
        verdicts.append(_verdict_entry(
            "agent_verdict (sealed agent bundle)",
            doc.get("agent_verdict"),
            raw_pointer="/agent_verdict",
        ))
    else:
        warnings.append(
            "missing field: agent_verdict (pre-B-097 legacy agent bundle)"
        )
    if "best_hypothesis" in abduction:
        verdicts.append(_verdict_entry(
            "pipeline_results.abduction.best_hypothesis",
            abduction.get("best_hypothesis"),
            confidence=abduction.get("confidence"),
            raw_pointer="/pipeline_results/abduction/best_hypothesis",
        ))

    signals = pipeline.get("signals") or []
    findings = []
    for i, sig in enumerate(signals):
        if not isinstance(sig, dict):
            warnings.append(f"signal[{i}] is not an object; skipped")
            continue
        findings.append({
            "id": sig.get("artifact_id"),
            "title": sig.get("description"),
            "verdict": None,          # pipeline signals carry no per-signal verdict
            "confidence": _scalar_display(sig.get("confidence")),
            "status": None,
            "peirce": None,
            "mitre_ttps": [],
            "kind": "pipeline_signal",
            "evidence_type": sig.get("evidence_type"),
            "source": sig.get("source"),
            "z_score": _scalar_display(sig.get("z_score")),
            "raw_pointer": f"/pipeline_results/signals/{i}",
        })

    preview = []
    for e in entries[:20]:
        if isinstance(e, dict):
            preview.append({
                "seq": e.get("seq"),
                "timestamp": e.get("timestamp"),
                "action": e.get("action"),
                "tool": e.get("tool"),
                "note": e.get("note"),
            })

    return {
        "case_id": doc.get("case_id"),
        "sealed_at": doc.get("analysis_timestamp"),
        "verdicts": verdicts,
        "findings": findings,
        "tool_log": {"present": False, "entry_count": 0, "chain_version": None},
        "audit_trail": {
            "present": bool(entries),
            "entry_count": audit.get("total_entries", len(entries)),
            "entries_preview": preview,
        },
        "integrity": {
            "evidence_sha256": doc.get("evidence_sha256"),
            "runtime_fingerprint": doc.get("runtime_fingerprint"),
        },
        "extra": decode_fractions({
            "narrative": doc.get("narrative"),
            "abduction": abduction,
            "signal_stats": doc.get("signal_stats"),
            "sans_compliance": doc.get("sans_compliance"),
            "iterations_executed": doc.get("iterations_executed"),
            "self_corrections_applied": doc.get("self_corrections_applied"),
            "evidence_path": doc.get("evidence_path"),
        }),
    }


def _normalize_mcp_finding(f: dict, idx: int, warnings: list) -> dict:
    fid = f.get("finding_id", f.get("id"))
    if fid is None:
        warnings.append(f"finding[{idx}]: no finding_id/id")

    peirce = f.get("peirce_chain")
    if not isinstance(peirce, dict):
        flat = {k: f.get(k) for k in ("firstness", "secondness", "thirdness")}
        peirce = flat if any(v is not None for v in flat.values()) else None
    if peirce is None:
        warnings.append(f"finding[{idx}] ({fid}): no Peirce chain fields")

    artifacts = f.get("artifacts")
    if artifacts is None and f.get("artifact") is not None:
        artifacts = [f["artifact"]]

    return {
        "id": fid,
        "title": f.get("title"),
        "verdict": f.get("verdict"),
        "confidence": _scalar_display(f.get("confidence")),
        "status": f.get("status"),
        "peirce": peirce,
        "carnegie": f.get("carnegie_pattern", f.get("carnegie")),
        "mitre_ttps": f.get("mitre_ttps", f.get("mitre")) or [],
        "devil_advocate": f.get("devil_advocate"),
        "corroboration": f.get("corroboration"),
        "artifacts": artifacts or [],
        "tools_used": f.get("tools_used") or [],
        "kind": "finding",
        "raw_pointer": f"/findings/{idx}",
    }


def _normalize_mcp(doc: dict, warnings: list) -> dict:
    raw_findings = doc.get("findings") or []
    findings = [
        _normalize_mcp_finding(f, i, warnings)
        for i, f in enumerate(raw_findings)
        if isinstance(f, dict)
    ]

    verdicts = []
    if "overall_verdict" in doc:
        verdicts.append(_verdict_entry(
            "overall_verdict",
            doc.get("overall_verdict"),
            confidence=doc.get("overall_confidence"),
            raw_pointer="/overall_verdict",
        ))
    elif "final_verdict" in doc:
        # KIWI-series field name for the same sealed value. Copied verbatim,
        # same as overall_verdict — the name differs, the rule does not.
        verdicts.append(_verdict_entry(
            "final_verdict",
            doc.get("final_verdict"),
            confidence=doc.get("overall_confidence"),
            raw_pointer="/final_verdict",
        ))
    else:
        warnings.append("missing field: overall_verdict (also looked for final_verdict)")

    tool_log = doc.get("tool_execution_log") or []
    chain_version = None
    if tool_log and isinstance(tool_log[0], dict):
        chain_version = tool_log[0].get("chain_version", "1")

    integrity = doc.get("integrity") or {}
    ts = _first_key(
        doc, ("analysis_timestamp", "investigation_timestamp", "report_generated",
              "timestamp_sealed", "sealed_at"),
        warnings, "timestamp",
    )

    return {
        "case_id": doc.get("case_id"),
        "sealed_at": ts,
        "verdicts": verdicts,
        "findings": findings,
        "tool_log": {
            "present": bool(tool_log),
            "entry_count": len(tool_log),
            "chain_version": chain_version,
            "chain_tip_sha256": doc.get("chain_tip_sha256"),
            "entries": decode_fractions(tool_log),
        },
        "audit_trail": {"present": False, "entry_count": 0, "entries_preview": []},
        "integrity": {
            "bundle_hash": integrity.get("bundle_hash"),
            "evidence_hash": doc.get("evidence_hash"),
            # KIWI-series names for the same two custody anchors. Absent keys
            # stay None — the viewer shows a gap, never a substitute.
            "bundle_sha256": doc.get("bundle_sha256"),
            "primary_evidence_sha256": doc.get("primary_evidence_sha256"),
        },
        "extra": decode_fractions({
            "verdict_rationale": doc.get("verdict_rationale"),
            "executive_summary": doc.get("executive_summary"),
            "sans_phase": doc.get("sans_phase"),
            "mitre_ttps_aggregate": doc.get("mitre_ttps_aggregate"),
            "refutation_gate_log": doc.get("refutation_gate_log"),
            "known_limitations": doc.get("known_limitations"),
            "self_corrections": doc.get(
                "self_corrections",
                doc.get("self_correction_events", doc.get("self_correction")),
            ),
            "mode": doc.get("mode", doc.get("investigation_mode")),
            "examiner": doc.get("examiner", doc.get("investigator")),
            "daubert_admissible": doc.get("daubert_admissible"),
        }),
    }


def _normalize_unknown(doc: dict, warnings: list) -> dict:
    warnings.append("unrecognized bundle schema — raw view only, nothing inferred")
    return {
        "case_id": doc.get("case_id") if isinstance(doc, dict) else None,
        "sealed_at": None,
        "verdicts": [],
        "findings": [],
        "tool_log": {"present": False, "entry_count": 0, "chain_version": None},
        "audit_trail": {"present": False, "entry_count": 0, "entries_preview": []},
        "integrity": {},
        "extra": {},
    }


_NORMALIZERS = {
    SCHEMA_EBS_V1: _normalize_ebs_v1,
    SCHEMA_AGENT_AUDIT: _normalize_agent_audit,
    SCHEMA_MCP: _normalize_mcp,
    SCHEMA_UNKNOWN: _normalize_unknown,
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def normalize(doc: Any, rel_path: str = "") -> dict:
    """Normalize a parsed bundle into the UI's display shape."""
    warnings: list = []
    schema = detect_schema(doc)
    if not isinstance(doc, dict):
        doc = {}
    body = _NORMALIZERS[schema](doc, warnings)
    body.update({
        "schema": schema,
        "rel_path": rel_path,
        "verdict_disagreement": _disagreement(body["verdicts"]),
        "warnings": warnings,
    })
    return body


def load_bundle(path: Path) -> Any:
    """Parse a bundle file. Raises on unreadable/invalid JSON — callers decide
    how to surface that (the index lists such files as unparseable)."""
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)
