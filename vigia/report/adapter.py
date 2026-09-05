"""Read-only view over a sealed bundle, for the audience renderers.

Everything here is *extraction*: values are copied out of the parsed document
and the normalizer's output, never derived. The one transformation permitted is
``render_scalar``, which turns a sealed value into the exact text that
represents it (a serialized Fraction becomes ``"N/D"``, a sealed float becomes
its own JSON literal). No rounding, no float(), no arithmetic.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from typing import Any, Optional

from vigia.ui.normalizer import (
    SCHEMA_AGENT_AUDIT,
    SCHEMA_EBS_V1,
    SCHEMA_MCP,
    SCHEMA_UNKNOWN,
    fraction_display,
    is_serialized_fraction,
    normalize,
)

# MITRE ATT&CK technique id, with optional sub-technique suffix. Findings in
# Mode 2 bundles embed ids inside free text ("T1585.001 (Establish Accounts)").
_TTP_RE = re.compile(r"\bT\d{4}(?:\.\d{3})?\b")

# Audit-trail actions that record a gate, downgrade or self-correction.
_GATE_ACTION_RE = re.compile(
    r"(?i)gate|downgrade|contradiction|self.?correct|refut|override|cap"
)

# Maximum log entries listed verbatim in the expert view. The cap is stated in
# the output whenever it truncates, so a reader knows to open the bundle.
TOOL_LOG_LISTING_CAP = 25


@dataclass(frozen=True)
class BundleView:
    """Immutable handle on one sealed bundle.

    ``raw`` is the parsed document. It is shared, not copied: renderers must
    treat it as read-only. ``test_report_adapter.py`` hashes it before and
    after a render to prove nothing mutates it.
    """

    schema: str
    case_id: Optional[str]
    source_sha256: str
    source_name: str
    normalized: dict
    raw: dict
    gaps: tuple[str, ...]


def load_view(bundle_bytes: bytes, source_name: str = "") -> BundleView:
    """Parse bundle bytes into a :class:`BundleView`.

    Raises ``ValueError`` on invalid JSON or a non-object document: an
    unreadable bundle is a hard failure, not something to paper over.
    """
    try:
        doc = json.loads(bundle_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"bundle is not valid UTF-8 JSON: {exc}") from exc
    if not isinstance(doc, dict):
        raise ValueError("bundle document is not a JSON object")

    normalized = normalize(doc, rel_path=source_name)
    gaps = list(normalized.get("warnings") or [])
    if normalized["schema"] == SCHEMA_UNKNOWN:
        # normalize() already warned; keep the tuple stable and unique.
        pass
    return BundleView(
        schema=normalized["schema"],
        case_id=normalized.get("case_id"),
        source_sha256=hashlib.sha256(bundle_bytes).hexdigest(),
        source_name=source_name.rsplit("/", 1)[-1] if source_name else "",
        normalized=normalized,
        raw=doc,
        gaps=tuple(dict.fromkeys(gaps)),
    )


# ---------------------------------------------------------------------------
# Scalars
# ---------------------------------------------------------------------------

def render_scalar(value: Any) -> Optional[str]:
    """Exact textual form of a sealed scalar; ``None`` when the value is absent.

    * serialized Fraction ``{"__fraction__": true, ...}`` -> ``"N/D"``
    * normalizer-decoded Fraction ``{"is_fraction": true, "display": ...}`` -> display
    * bool -> ``"true"`` / ``"false"`` (JSON spelling, matches the bundle)
    * int -> ``str(int)``
    * float -> ``json.dumps(float)`` — the same literal the bundle carries.
      Never ``round()``, never a format spec: reformatting a sealed number is
      restating it.
    * str -> unchanged
    * list / dict -> canonical JSON (sorted keys, no ASCII escaping)
    """
    if value is None:
        return None
    if is_serialized_fraction(value):
        return fraction_display(value)
    if isinstance(value, dict) and value.get("is_fraction") is True:
        return str(value.get("display"))
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        return json.dumps(value)
    if isinstance(value, str):
        return value
    return json.dumps(value, sort_keys=True, ensure_ascii=False)


def _get(doc: Any, *path: str) -> Any:
    cur = doc
    for key in path:
        if not isinstance(cur, dict) or key not in cur:
            return None
        cur = cur[key]
    return cur


# ---------------------------------------------------------------------------
# Extractors
# ---------------------------------------------------------------------------

def custody_fields(view: BundleView) -> list[tuple[str, Optional[str]]]:
    """Chain-of-custody anchors for this family, in a fixed order.

    Each item is ``(bundle_field_name, rendered_value_or_None)``. ``None``
    means the field is absent in this bundle; renderers show that as an
    explicit gap with the L-030/L-031 pointer (hashes are not comparable
    across families).
    """
    raw = view.raw
    if view.schema == SCHEMA_EBS_V1:
        integrity = _get(raw, "integrity") or {}
        names = (
            "bundle_hash", "analysis_fingerprint", "graph_hash", "decision_hash",
            "policy_hash", "engine_attestation_hash", "ecl_hash", "sealed_at",
        )
        return [(f"integrity.{n}", render_scalar(integrity.get(n)) or None) for n in names]
    if view.schema == SCHEMA_AGENT_AUDIT:
        return [
            ("evidence_sha256", render_scalar(raw.get("evidence_sha256"))),
            ("runtime_fingerprint", render_scalar(raw.get("runtime_fingerprint"))),
            ("analysis_timestamp", render_scalar(raw.get("analysis_timestamp"))),
            ("audit_trail.total_entries",
             render_scalar(_get(raw, "audit_trail", "total_entries"))),
        ]
    if view.schema == SCHEMA_MCP:
        integrity = _get(raw, "integrity") or {}
        return [
            ("bundle_sha256", render_scalar(raw.get("bundle_sha256"))),
            ("integrity.bundle_hash", render_scalar(integrity.get("bundle_hash"))),
            ("primary_evidence_sha256",
             render_scalar(raw.get("primary_evidence_sha256"))),
            ("evidence_hash", render_scalar(raw.get("evidence_hash"))),
            ("chain_tip_sha256", render_scalar(raw.get("chain_tip_sha256"))),
            ("timestamp_sealed", render_scalar(
                raw.get("timestamp_sealed", raw.get("sealed_at")))),
        ]
    return []


def verdict_entries(view: BundleView) -> list[dict]:
    """Every verdict-bearing field the normalizer found, verbatim."""
    return list(view.normalized.get("verdicts") or [])


def finding_entries(view: BundleView) -> list[dict]:
    return list(view.normalized.get("findings") or [])


def devil_advocate_entries(view: BundleView) -> list[tuple[str, Any]]:
    """``(json_pointer, value)`` for every devil_advocate the bundle carries."""
    raw = view.raw
    out: list[tuple[str, Any]] = []
    if view.schema == SCHEMA_EBS_V1:
        val = _get(raw, "caie_analysis", "devil_advocate")
        if val is not None:
            out.append(("/caie_analysis/devil_advocate", val))
    elif view.schema == SCHEMA_AGENT_AUDIT:
        val = _get(raw, "pipeline_results", "abduction", "devil_advocate")
        if val is not None:
            out.append(("/pipeline_results/abduction/devil_advocate", val))
    elif view.schema == SCHEMA_MCP:
        for i, f in enumerate(raw.get("findings") or []):
            if isinstance(f, dict) and f.get("devil_advocate") is not None:
                out.append((f"/findings/{i}/devil_advocate", f["devil_advocate"]))
    return out


def refutation_gate_entries(view: BundleView) -> list[dict]:
    """Records of a gate, downgrade or self-correction, as the bundle stores them.

    * MCP: ``refutation_gate_log`` (a list, or a single object in KIWI bundles).
    * agent audit: ``audit_trail.entries`` whose ``action`` names a gate.
    * EBS v1: the decision-trace / CAIE fields that record gate outcomes.
    Each item carries a ``_pointer`` key so the reader can find it in the JSON.
    """
    raw = view.raw
    out: list[dict] = []
    if view.schema == SCHEMA_MCP:
        rgl = raw.get("refutation_gate_log")
        items = rgl if isinstance(rgl, list) else ([rgl] if isinstance(rgl, dict) else [])
        for i, item in enumerate(items):
            if isinstance(item, dict):
                entry = dict(item)
                entry["_pointer"] = (f"/refutation_gate_log/{i}"
                                     if isinstance(rgl, list) else "/refutation_gate_log")
                out.append(entry)
    elif view.schema == SCHEMA_AGENT_AUDIT:
        entries = _get(raw, "audit_trail", "entries") or []
        for i, e in enumerate(entries):
            if isinstance(e, dict) and _GATE_ACTION_RE.search(str(e.get("action", ""))):
                out.append({
                    "_pointer": f"/audit_trail/entries/{i}",
                    "seq": e.get("seq"),
                    "action": e.get("action"),
                    "note": e.get("note"),
                    "iteration": e.get("iteration"),
                })
    elif view.schema == SCHEMA_EBS_V1:
        dt = _get(raw, "decision_trace") or {}
        caie = _get(raw, "caie_analysis") or {}
        for name, src, ptr in (
            ("reason_code", dt, "/decision_trace/reason_code"),
            ("abstain_reason", dt, "/decision_trace/abstain_reason"),
            ("hard_temporal_gate", caie, "/caie_analysis/hard_temporal_gate"),
            ("r3_calibration_note", caie, "/caie_analysis/r3_calibration_note"),
            ("caie_fractures_source", caie, "/caie_analysis/caie_fractures_source"),
        ):
            if isinstance(src, dict) and name in src and src[name] not in (None, ""):
                out.append({"_pointer": ptr, "field": name, "value": src[name]})
    return out


def exact_scores(view: BundleView) -> list[tuple[str, str]]:
    """``(json_pointer, exact_text)`` for every sealed numeric the expert view lists."""
    raw = view.raw
    out: list[tuple[str, str]] = []
    if view.schema == SCHEMA_EBS_V1:
        dt = _get(raw, "decision_trace") or {}
        for k in sorted(dt):
            v = dt[k]
            if isinstance(v, (int, float, dict)) and not isinstance(v, bool) and v is not None:
                if isinstance(v, dict) and not is_serialized_fraction(v):
                    continue
                out.append((f"/decision_trace/{k}", render_scalar(v) or ""))
        caie = _get(raw, "caie_analysis") or {}
        for k in ("composite_score", "confidence", "caie_fractures"):
            if k in caie and caie[k] is not None and not isinstance(caie[k], (str, bool)):
                out.append((f"/caie_analysis/{k}", render_scalar(caie[k]) or ""))
    elif view.schema == SCHEMA_AGENT_AUDIT:
        ab = _get(raw, "pipeline_results", "abduction") or {}
        for k in ("best_posterior", "confidence"):
            if k in ab and ab[k] is not None:
                out.append((f"/pipeline_results/abduction/{k}", render_scalar(ab[k]) or ""))
        for i, sig in enumerate(_get(raw, "pipeline_results", "signals") or []):
            if not isinstance(sig, dict):
                continue
            for k in ("confidence", "z_score"):
                if k in sig and sig[k] is not None:
                    out.append((f"/pipeline_results/signals/{i}/{k}",
                                render_scalar(sig[k]) or ""))
    elif view.schema == SCHEMA_MCP:
        for i, f in enumerate(raw.get("findings") or []):
            if isinstance(f, dict) and f.get("confidence") is not None:
                out.append((f"/findings/{i}/confidence", render_scalar(f["confidence"]) or ""))
        for e in refutation_gate_entries(view):
            if e.get("candidate_confidence") is not None:
                out.append((f"{e['_pointer']}/candidate_confidence",
                            render_scalar(e["candidate_confidence"]) or ""))
    return out


def _histogram(values: list[str]) -> list[tuple[str, int]]:
    counts: dict[str, int] = {}
    for v in values:
        counts[v] = counts.get(v, 0) + 1
    return sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))


def tool_log_summary(view: BundleView) -> dict:
    """Counts and sorted histograms over the execution record of this family.

    Keys: ``kind`` (``tool_execution_log`` | ``audit_trail`` | ``system_state``
    | ``none``), ``entry_count``, ``histogram`` (list of ``(label, count)``),
    ``listing`` (first ``TOOL_LOG_LISTING_CAP`` entries, compact dicts),
    ``truncated`` (bool), plus family-specific fields.
    """
    raw = view.raw
    if view.schema == SCHEMA_MCP:
        log = raw.get("tool_execution_log") or []
        entries = [e for e in log if isinstance(e, dict)]
        listing = [{
            "seq": e.get("seq"), "tool": e.get("tool"), "target": e.get("target"),
            "result_summary": e.get("result_summary"),
        } for e in entries[:TOOL_LOG_LISTING_CAP]]
        return {
            "kind": "tool_execution_log",
            "entry_count": len(entries),
            "chain_version": (entries[0].get("chain_version", "1") if entries else None),
            "chain_tip_present": raw.get("chain_tip_sha256") is not None,
            "chain_tip_hmac_present": raw.get("chain_tip_hmac") is not None,
            "histogram": _histogram([str(e.get("tool")) for e in entries]),
            "listing": listing,
            "truncated": len(entries) > TOOL_LOG_LISTING_CAP,
        }
    if view.schema == SCHEMA_AGENT_AUDIT:
        audit = raw.get("audit_trail") or {}
        entries = [e for e in (audit.get("entries") or []) if isinstance(e, dict)]
        listing = [{
            "seq": e.get("seq"), "action": e.get("action"), "iteration": e.get("iteration"),
            "note": e.get("note"),
        } for e in entries[:TOOL_LOG_LISTING_CAP]]
        return {
            "kind": "audit_trail",
            "entry_count": audit.get("total_entries", len(entries)),
            "start_time": audit.get("start_time"),
            "end_time": audit.get("end_time"),
            "entries_with_sha256": sum(1 for e in entries if e.get("entry_sha256")),
            "histogram": _histogram([str(e.get("action")) for e in entries]),
            "listing": listing,
            "truncated": len(entries) > TOOL_LOG_LISTING_CAP,
        }
    if view.schema == SCHEMA_EBS_V1:
        state = raw.get("system_state") or {}
        return {
            "kind": "system_state",
            "entry_count": 0,
            "fields": [(k, render_scalar(state[k]) or "") for k in sorted(state)],
            "histogram": [],
            "listing": [],
            "truncated": False,
        }
    return {"kind": "none", "entry_count": 0, "histogram": [], "listing": [],
            "truncated": False}


def mitre_ids(view: BundleView) -> list[tuple[str, str]]:
    """Sorted unique ``(technique_id, where_found)`` pairs.

    ``where_found`` names the bundle region so the reader knows whether the id
    was a declared TTP field or merely mentioned in free text:
    ``findings.mitre_ttps``, ``mitre_ttps_aggregate``, ``caie_analysis``,
    ``signals.description``.
    """
    raw = view.raw
    found: dict[str, str] = {}

    def _scan(text: Any, where: str) -> None:
        for m in _TTP_RE.findall(json.dumps(text, ensure_ascii=False)
                                 if not isinstance(text, str) else text):
            found.setdefault(m, where)

    if view.schema == SCHEMA_MCP:
        for f in raw.get("findings") or []:
            if isinstance(f, dict):
                _scan(f.get("mitre_ttps", f.get("mitre")) or [], "findings.mitre_ttps")
        _scan(raw.get("mitre_ttps_aggregate") or [], "mitre_ttps_aggregate")
    elif view.schema == SCHEMA_EBS_V1:
        caie = raw.get("caie_analysis") or {}
        for k in ("mitre_ttps", "mitre", "ttps"):
            if k in caie:
                _scan(caie[k], f"caie_analysis.{k}")
    elif view.schema == SCHEMA_AGENT_AUDIT:
        for sig in _get(raw, "pipeline_results", "signals") or []:
            if isinstance(sig, dict):
                _scan(str(sig.get("description", "")), "signals.description")
    return sorted(found.items())


def known_limitations(view: BundleView) -> list[str]:
    """The bundle's own ``known_limitations`` list, as strings, verbatim."""
    kl = view.raw.get("known_limitations")
    if isinstance(kl, list):
        return [render_scalar(x) or "" for x in kl]
    if isinstance(kl, (str, dict)):
        return [render_scalar(kl) or ""]
    return []


def sans_phase_text(view: BundleView) -> Optional[str]:
    """Verbatim ``sans_phase`` (MCP) or ``None``."""
    v = view.raw.get("sans_phase")
    return render_scalar(v) if v is not None else None


def executive_summary(view: BundleView) -> Optional[str]:
    """Verbatim executive summary if the family stores one."""
    if view.schema == SCHEMA_MCP:
        v = view.raw.get("executive_summary")
        return render_scalar(v) if v is not None else None
    return None


def narrative_text(view: BundleView) -> Optional[str]:
    """Verbatim sealed narrative (agent family) or CAIE reason (EBS v1)."""
    if view.schema == SCHEMA_AGENT_AUDIT:
        v = view.raw.get("narrative")
        return v if isinstance(v, str) else None
    if view.schema == SCHEMA_EBS_V1:
        v = _get(view.raw, "caie_analysis", "reason")
        return v if isinstance(v, str) else None
    return None


__all__ = [
    "BundleView", "load_view", "render_scalar", "custody_fields", "verdict_entries",
    "finding_entries", "devil_advocate_entries", "refutation_gate_entries",
    "exact_scores", "tool_log_summary", "mitre_ids", "known_limitations",
    "sans_phase_text", "executive_summary", "narrative_text",
    "TOOL_LOG_LISTING_CAP",
]
