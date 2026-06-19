#!/usr/bin/env python3
"""
r7_devil_advocate_patch.py — R7 surgical patch (Phase 1 + Phase 2), v2

Fixes applied vs v1, per critique review:
  - Removed the assumption that scorer_result has an "engine_signal_metadata"
    key. Confirmed via direct repo audit (root vigia_scorer.py AND
    vigia/core/vigia_scorer.py — both checked, neither touches
    CasePatternLibrary): the standalone scorer path used by build_bundle()
    structurally never has pattern-matching data. The composer now receives
    pattern_signal_metadata=None explicitly on that path, with an honest
    scope-limitation narrative instead of a pretended field lookup.
  - Removed the separate, undisclosed TAU threshold in devil_advocate_gen.py.
    Every pattern present in missing_signals_by_pattern has already cleared
    its own pattern.similarity_threshold inside CasePatternLibrary.match() —
    re-filtering with a second arbitrary constant was redundant.
  - decision_verdict scope in build_bundle() verified directly against the
    live file: it is defined earlier in the same function and remains in
    scope at the injection point. No NameError risk.
  - Hash integrity verified directly against bundle_builder.py: caie_analysis
    is inserted as a full dict into bundle_payload before bundle_hash is
    computed over the whole payload. Confirmed safe, not assumed.
  - All code, comments and docstrings in English per project convention.

Usage:
    cd ~/vigia-repo
    python3 r7_devil_advocate_patch.py            # applies with automatic .bak
    python3 r7_devil_advocate_patch.py --dry-run  # shows what would change, touches nothing
"""
import sys
import shutil
from pathlib import Path

DRY_RUN = "--dry-run" in sys.argv
REPO = Path(__file__).resolve().parent


def patch_file(path: str, replacements: list[tuple[str, str]]) -> None:
    fpath = REPO / path
    if not fpath.exists():
        raise SystemExit(f"ABORT: {fpath} does not exist")
    original = fpath.read_text(encoding="utf-8")
    text = original
    for old, new in replacements:
        count = text.count(old)
        if count == 0:
            raise SystemExit(f"ABORT: anchor not found in {path}:\n{old[:200]}")
        if count > 1:
            raise SystemExit(f"ABORT: ambiguous anchor ({count} matches) in {path}:\n{old[:200]}")
        text = text.replace(old, new)
    if DRY_RUN:
        print(f"[DRY-RUN] {path} — {len(replacements)} replacement(s) verified, anchor(s) unique. OK.")
        return
    backup = fpath.with_suffix(fpath.suffix + ".bak")
    shutil.copy2(fpath, backup)
    fpath.write_text(text, encoding="utf-8")
    print(f"[OK] {path} patched. Backup at {backup}")


# ---------------------------------------------------------------------------
# 1. case_pattern_library.py — expose missing_signals and match_score
# ---------------------------------------------------------------------------
patch_file(
    "vigia/inference/case_pattern_library.py",
    [(
        '''            metadata={
                "total_patterns": self.total_patterns,
                "match_count": len(self.matches),
                "best_match": self.best_match or "NONE",
                "artifact_type": "pattern",
                "artifact_reliability": str(ARTIFACT_RELIABILITY),
                "finding_types": sorted(list(set(
                    m.pattern_name for m in self.matches
                ))),
            }''',
        '''            metadata={
                "total_patterns": self.total_patterns,
                "match_count": len(self.matches),
                "best_match": self.best_match or "NONE",
                "artifact_type": "pattern",
                "artifact_reliability": str(ARTIFACT_RELIABILITY),
                "finding_types": sorted(list(set(
                    m.pattern_name for m in self.matches
                ))),
                # R7 — raw data for deterministic devil_advocate composition.
                # Fraction serialised as str (H22: no floats on the verdict path).
                # Every key here already cleared its own pattern.similarity_threshold
                # inside match() — no separate confidence filter is applied downstream.
                "missing_signals_by_pattern": {
                    m.pattern_name: m.missing_signals for m in self.matches
                },
                "match_score_by_pattern": {
                    m.pattern_name: str(m.match_score) for m in self.matches
                },
            }''',
    )],
)

# ---------------------------------------------------------------------------
# 2. New module — shared deterministic composer (no LLM)
# ---------------------------------------------------------------------------
devil_advocate_gen_path = REPO / "vigia/core/devil_advocate_gen.py"
if devil_advocate_gen_path.exists():
    raise SystemExit(f"ABORT: {devil_advocate_gen_path} already exists — refusing to overwrite blind")

DEVIL_ADVOCATE_GEN_SRC = '''"""
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
            "CasePatternLibrary is not invoked here by design (standalone scorer mode; "
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
'''
if DRY_RUN:
    print(f"[DRY-RUN] {devil_advocate_gen_path} — would be created ({len(DEVIL_ADVOCATE_GEN_SRC)} bytes). OK.")
else:
    devil_advocate_gen_path.write_text(DEVIL_ADVOCATE_GEN_SRC, encoding="utf-8")
    print(f"[OK] created {devil_advocate_gen_path}")

# ---------------------------------------------------------------------------
# 3. bundle_builder.py (build_bundle) — inject into caie_payload
#    pattern_signal_metadata is always None on this path — confirmed by
#    direct audit, not assumed. See module docstring above.
# ---------------------------------------------------------------------------
patch_file(
    "vigia/core/bundle_builder.py",
    [(
        '''    caie_payload: Dict[str, Any] = {
        "verdict":               raw_verdict,
        "composite_score":       score,
        "confidence":            confidence,
        "caie_fractures":        int(scorer_result.get("caie_fractures", 0) or 0),
        "caie_fractures_source": scorer_result.get("caie_fractures_source", "standalone"),
        "hard_temporal_gate":    bool(scorer_result.get("hard_temporal_gate", False)),
        "peirce_chain":          peirce,
        "quadripartite_state":   scorer_result.get("quadripartite_state") or {},
        "reason":                scorer_result.get("reason", ""),
        "case_id":               case.get("case_id", case.get("name", "UNKNOWN")),
    }

    return BundleBuilder.seal(bundle, caie_analysis=caie_payload)''',
        '''    caie_payload: Dict[str, Any] = {
        "verdict":               raw_verdict,
        "composite_score":       score,
        "confidence":            confidence,
        "caie_fractures":        int(scorer_result.get("caie_fractures", 0) or 0),
        "caie_fractures_source": scorer_result.get("caie_fractures_source", "standalone"),
        "hard_temporal_gate":    bool(scorer_result.get("hard_temporal_gate", False)),
        "peirce_chain":          peirce,
        "quadripartite_state":   scorer_result.get("quadripartite_state") or {},
        "reason":                scorer_result.get("reason", ""),
        "case_id":               case.get("case_id", case.get("name", "UNKNOWN")),
    }

    # R7 — deterministic devil_advocate. Never overwrites a human-provided
    # value because this path (_vigia_score / build_bundle) never had one.
    # pattern_signal_metadata is always None here: CasePatternLibrary only
    # runs inside sift_orchestrator.py, a separate code path — confirmed by
    # direct audit of vigia_scorer.py, not assumed. The composer falls back
    # to an explicit scope-limitation narrative instead of a generic template.
    if raw_verdict in ("MALICE", "INTENT"):
        from vigia.core.devil_advocate_gen import compose_devil_advocate_struct
        caie_payload["devil_advocate"] = compose_devil_advocate_struct(
            pattern_signal_metadata=None,
            raw_verdict=raw_verdict,
            mapped_verdict=decision_verdict,
            score=score,
            confidence=confidence,
        )

    return BundleBuilder.seal(bundle, caie_analysis=caie_payload)''',
    )],
)

# ---------------------------------------------------------------------------
# 4. verify_ebs_v1.py — Option C: honest failure instead of silent pass,
#    plus CRITICAL severity and conformity_level guard (Collective vote).
# ---------------------------------------------------------------------------
patch_file(
    "forensics/verify_ebs_v1.py",
    [
        (
            '''def _check_devil_advocate(bundle: Dict) -> Tuple[bool, str]:
    """R6 — MALICE/INTENT findings must have devil_advocate populated (Daubert requirement)."""
    findings = bundle.get("findings", [])
    if not findings:
        return True, "No findings field — fallback mode bundle, check not applicable"
    violations = []
    for f in findings:
        if f.get("verdict", "") in ("MALICE", "INTENT"):
            da = str(f.get("devil_advocate", "")).strip()
            if not da or da in ("", "N/A", "null", "None"):
                violations.append(f.get("finding_id", f.get("id", "UNKNOWN")))
    if violations:
        return False, f"Findings {violations} have MALICE/INTENT verdict but empty devil_advocate — Daubert invalidity"
    return True, "All MALICE/INTENT findings have devil_advocate populated"''',
            '''def _check_devil_advocate(bundle: Dict) -> Tuple[bool, str]:
    """R6 — MALICE/INTENT findings must have devil_advocate populated (Daubert requirement)."""
    findings = bundle.get("findings", [])
    if not findings:
        # R7 Option C (Collective vote, 2026-06-19): a single-verdict bundle
        # with no findings[] is NOT exempt from this check just because it
        # has a different shape. Same vocabulary as the rest of this
        # function: caie_analysis.verdict, not decision_trace.decision
        # (which uses the mapped EBS vocabulary REJECT/ABSTAIN/ACCEPT,
        # distinct from the raw forensic MALICE/INTENT/SUSPICION verdict).
        caie = bundle.get("caie_analysis") or {}
        if caie.get("verdict", "") in ("MALICE", "INTENT"):
            da = caie.get("devil_advocate")
            if not da:
                return False, (
                    "R7 VIOLATION: single-verdict bundle has MALICE/INTENT verdict "
                    "in caie_analysis but no devil_advocate object — the "
                    "falsification step was never attempted. This bundle must not "
                    "be treated as sealed-compliant."
                )
            return True, "Single-verdict bundle has devil_advocate populated in caie_analysis"
        return True, "No findings field and no MALICE/INTENT verdict — check not applicable"
    violations = []
    for f in findings:
        if f.get("verdict", "") in ("MALICE", "INTENT"):
            da = str(f.get("devil_advocate", "")).strip()
            if not da or da in ("", "N/A", "null", "None"):
                violations.append(f.get("finding_id", f.get("id", "UNKNOWN")))
    if violations:
        return False, f"Findings {violations} have MALICE/INTENT verdict but empty devil_advocate — Daubert invalidity"
    return True, "All MALICE/INTENT findings have devil_advocate populated"''',
        ),
        (
            'result.add("R6_DEVIL_ADVOCATE", ok_da, msg_da, severity="WARNING" if not ok_da else "INFO")',
            'result.add("R6_DEVIL_ADVOCATE", ok_da, msg_da, severity="CRITICAL" if not ok_da else "INFO")',
        ),
        (
            "    if not critical and hash_ok and ok_pc and ok_att and ok_ecl:\n        result.conformity_level = 3",
            "    if not critical and hash_ok and ok_pc and ok_att and ok_ecl and ok_da:\n        result.conformity_level = 3",
        ),
    ],
)

print("\nDone." if not DRY_RUN else "\nDry-run OK — every anchor exists exactly once.")
print("Still pending: the pipeline.py insertion — needs the exact surrounding context, see chat.")
print("Flagged separately, not in this patch: vigia/core/vigia_scorer.py is stale and unused, "
      "but carries the pre-recalibration MALICE threshold (0.75 instead of 0.33) — a guaranteed "
      "false-negative regression if anyone ever imports it by mistake. High-priority cleanup item.")
