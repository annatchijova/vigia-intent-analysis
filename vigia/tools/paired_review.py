"""
vigia/tools/paired_review.py
F2 (L-029 / FW-009) — deterministic cross-bundle paired review.

Formalizes the manual workaround L-029 documented ("submit KIWI-002 and
KIWI-003 as a paired bundle review"). This module computes DETERMINISTIC
sub-metrics only; the Thirdness (role-inversion) reasoning belongs to the
calling analyst/LLM in Mode 2, OUTSIDE the decision loop (CLAUDE.md
invariant 3). The output carries ZERO verdict authority and says so in
its own caveats — every join key is examiner-authored input (L-004).

Kimi's audit trap (docs/VEREDICTO_KIMI_L029_20260717.md §6): case_origin
lives at artifacts[].metadata.case_origin — top-level case_origin is None
in every KIWI file. Reading it from top-level silently groups the whole
corpus under None.

Label-blind by construction: expected_verdict is never read
(the B-075 leak class).
"""
from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, List, Optional

from vigia.core.darvo_detector import detect_darvo_pattern

PAIRED_REVIEW_CAVEATS = (
    "This record carries NO verdict authority: every join key "
    "(case_origin, framing, descriptions) is examiner-authored input "
    "(L-004 narrative class).",
    "Completeness only when honest: an aggressor filing through their own "
    "examiner omits or alters case_origin — absence of linkage proves "
    "nothing.",
    "A hostile filer can forge case_origin/framing to force a smear "
    "pairing — the pairing yields only this annotated record, which "
    "names itself examiner testimony.",
    "Role attribution remains examiner testimony; the Thirdness reasoning "
    "belongs to the analyst, outside the decision loop.",
)


def artifact_case_origin(case: Dict[str, Any]) -> Optional[str]:
    """Join key read from artifact metadata (never top-level — Kimi §6).

    Returns the single consistent case_origin, or None when absent or
    ambiguous (mixed origins are an integrity smell, not a join key).
    """
    origins = set()
    for a in case.get("artifacts", []):
        if not isinstance(a, dict):
            continue
        meta = a.get("metadata")
        if isinstance(meta, dict) and meta.get("case_origin"):
            origins.add(str(meta["case_origin"]))
    return sorted(origins)[0] if len(origins) == 1 else None


def _prior_trust_mean(case: Dict[str, Any]) -> Fraction:
    values = []
    for a in case.get("artifacts", []):
        if isinstance(a, dict) and a.get("prior_trust") is not None:
            try:
                values.append(Fraction(str(a["prior_trust"])))
            except (ValueError, ZeroDivisionError):
                continue
    if not values:
        return Fraction(1, 2)
    return sum(values, Fraction(0)) / len(values)


def compare_paired_bundles_data(
    case_a: Dict[str, Any], case_b: Dict[str, Any]
) -> Dict[str, Any]:
    """Deterministic paired sub-metrics over two already-loaded cases."""
    origin_a = artifact_case_origin(case_a)
    origin_b = artifact_case_origin(case_b)
    framing_a = case_a.get("framing")
    framing_b = case_b.get("framing")
    mean_a = _prior_trust_mean(case_a)
    mean_b = _prior_trust_mean(case_b)

    union = list(case_a.get("artifacts", [])) + list(case_b.get("artifacts", []))
    darvo = detect_darvo_pattern(union)

    chains_a = {
        tuple(a.get("provenance_chain") or [])
        for a in case_a.get("artifacts", []) if isinstance(a, dict)
    }
    chains_b = {
        tuple(a.get("provenance_chain") or [])
        for a in case_b.get("artifacts", []) if isinstance(a, dict)
    }
    overlap = sorted(" > ".join(c) for c in (chains_a & chains_b))

    return {
        "schema": "paired_review_v1",
        "case_origin": {
            "a": origin_a, "b": origin_b,
            "match": origin_a is not None and origin_a == origin_b,
        },
        "framing": {
            "a": framing_a, "b": framing_b,
            "complementary": {framing_a, framing_b} == {
                "perspective_actor_a", "perspective_actor_b"},
        },
        "prior_trust": {
            "mean_a": str(mean_a),
            "mean_b": str(mean_b),
            "delta": str(abs(mean_a - mean_b)),
        },
        "darvo_union": {
            "pattern_present": darvo["pattern_present"],
            "penalty": str(darvo["penalty"]),
            "surveillance_count": darvo["surveillance_count"],
            "zero_contact_count": darvo["zero_contact_count"],
        },
        "provenance": {
            "chain_overlap": overlap,
            "disjoint_chains": not overlap,
        },
        "caveats": list(PAIRED_REVIEW_CAVEATS),
        "verdict_authority": "none",
    }


def compare_paired_bundles(path_a: str, path_b: str) -> Dict[str, Any]:
    """MCP-facing entry: load two case/bundle JSONs and compare.

    Deterministic sub-metrics only; the calling analyst/LLM performs the
    Thirdness reasoning over the returned record (Mode 2), outside the
    decision loop.
    """
    try:
        case_a = json.loads(Path(path_a).read_text(encoding="utf-8"))
        case_b = json.loads(Path(path_b).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        return {"schema": "paired_review_v1", "error": f"{type(e).__name__}: {e}",
                "verdict_authority": "none"}
    if not isinstance(case_a, dict) or not isinstance(case_b, dict):
        return {"schema": "paired_review_v1",
                "error": "both inputs must be JSON objects with artifacts[]",
                "verdict_authority": "none"}
    result = compare_paired_bundles_data(case_a, case_b)
    result["sources"] = {"a": str(path_a), "b": str(path_b)}
    return result
