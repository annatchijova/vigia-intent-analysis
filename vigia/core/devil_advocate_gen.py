"""
vigia/core/devil_advocate_gen.py

R7 — Deterministic composition of devil_advocate (Eco's Razor / abductive
falsification). Approved by Collective vote, 2026-06-19. No LLM on this path.

Single source of truth: signals already computed by CasePatternLibrary
(missing_signals_by_pattern, match_score_by_pattern). Every pattern present
in missing_signals_by_pattern has already cleared its own pattern-specific
similarity_threshold inside CasePatternLibrary.match() — there is no second,
undisclosed global confidence threshold here. Re-filtering with an arbitrary
constant on top of an already-validated match would reintroduce exactly the
kind of unprincipled numeric criterion this design is meant to avoid.

Aggregates the top-k matching patterns (not only the single best match) to
preserve counterfactual diversity, per Collective review.

Known structural limitation: the standalone scorer path (vigia_scorer.py /
build_bundle()) never has pattern-matching data available — CasePatternLibrary
only runs inside sift_orchestrator.py, a separate code path. Confirmed by
direct audit of both vigia_scorer.py copies (root and vigia/core/), 2026-06-19.
On that path, pattern_signal_metadata is always None and the composer falls
back to an explicit scope-limitation narrative rather than a generic template.
"""
from __future__ import annotations

from fractions import Fraction
from typing import Any, Dict, List, Optional

K_DEFAULT = 3  # top-k patterns to aggregate, ranked by their own match_score


def compose_devil_advocate_struct(
    pattern_signal_metadata: Optional[Dict[str, Any]],
    raw_verdict: str,
    mapped_verdict: str,
    score: float,
    confidence: float,
    k: int = K_DEFAULT,
    scope_note: str = "standalone scorer mode",
) -> Dict[str, Any]:
    """
    Builds the structured devil_advocate object from missing_signals already
    computed by CasePatternLibrary.match().

    pattern_signal_metadata: the .metadata of the "patterns" SignalOutput, or
    None when CasePatternLibrary is not part of the current code path (e.g.
    the standalone scorer — see KNOWN_LIMITATIONS.md) or did not run.
    """
    missing_by_pattern: Dict[str, List[str]] = {}
    scores_by_pattern: Dict[str, str] = {}
    if pattern_signal_metadata:
        missing_by_pattern = pattern_signal_metadata.get("missing_signals_by_pattern", {}) or {}
        scores_by_pattern = pattern_signal_metadata.get("match_score_by_pattern", {}) or {}

    candidates = []
    for pattern_name, missing in missing_by_pattern.items():
        score_str = scores_by_pattern.get(pattern_name, "0")
        try:
            pat_score = Fraction(score_str)
        except (ValueError, ZeroDivisionError):
            pat_score = Fraction(0)
        candidates.append((pattern_name, pat_score, missing))

    # No separate threshold here by design — every candidate already cleared
    # its own pattern.similarity_threshold to be present in missing_by_pattern.
    candidates.sort(key=lambda c: c[1], reverse=True)
    top_k = candidates[:k]

    pattern_evidence_gaps = []
    total_gap_mass = Fraction(0)
    for pattern_name, pat_score, missing in top_k:
        gap_strength = Fraction(len(missing)) * pat_score
        total_gap_mass += gap_strength
        pattern_evidence_gaps.append({
            "pattern": pattern_name,
            "confidence": str(pat_score),
            "missing_signals": missing,
            "gap_strength": str(gap_strength),
        })

    dominant_alt = top_k[0][0] if top_k else None

    if pattern_evidence_gaps:
        devil_advocate_source = "deterministic_missing_signals"
    elif pattern_signal_metadata is None:
        devil_advocate_source = "deterministic_no_pattern_data_available"
    else:
        devil_advocate_source = "deterministic_no_pattern_matched"

    struct: Dict[str, Any] = {
        "version": "r7-da-v1",
        "decision_context": {
            "raw_verdict": raw_verdict,
            "mapped_verdict": mapped_verdict,
            "score": score,
            "confidence": confidence,
        },
        "pattern_evidence_gaps": pattern_evidence_gaps,
        "aggregation": {
            "method": "top_k_already_validated_matches_v2",
            "k": k,
            "total_gap_mass": str(total_gap_mass),
        },
        "counterfactual_summary": {
            "primary_alternative_hypothesis": dominant_alt,
        },
        "meta": {
            "generated_from": "case_pattern_library",
            "deterministic": True,
        },
        "devil_advocate_source": devil_advocate_source,
    }

    if pattern_evidence_gaps:
        narrative = (
            f"Eco's Razor (Abductive Falsification) applied to verdict {mapped_verdict}. "
            f"Hypothesis tested: evidence aligns with pattern '{dominant_alt}'. "
            f"Falsification attempt: corroborating signals expected for the top-"
            f"{len(top_k)} matching pattern(s) but absent from the evidence graph: "
            + "; ".join(f"{g['pattern']}: {g['missing_signals']}" for g in pattern_evidence_gaps)
            + ". Result: absence of these signals does not, by itself, falsify the "
            "malicious-intent hypothesis; verdict retained subject to the configured "
            "confidence threshold."
        )
    elif pattern_signal_metadata is None:
        narrative = (
            f"Eco's Razor (Abductive Falsification) applied to verdict {mapped_verdict}. "
            "Pattern-matching data was not available on this code path — "
            f"CasePatternLibrary is not invoked here by design ({scope_note}; "
            "see KNOWN_LIMITATIONS.md). No structured counter-hypothesis could be "
            "derived deterministically. This is a documented scope limitation of the "
            "current code path, not an absence of falsification attempt."
        )
    else:
        narrative = (
            f"Eco's Razor (Abductive Falsification) applied to verdict {mapped_verdict}. "
            "CasePatternLibrary was invoked but no known attack pattern matched this "
            "evidence set above its own similarity threshold. No structured "
            "counter-hypothesis could be derived from current pattern library coverage "
            "at this confidence level. This is a known limitation of pattern library "
            "coverage, not an absence of falsification attempt."
        )
    struct["narrative"] = narrative
    return struct
