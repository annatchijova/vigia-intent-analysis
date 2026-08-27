"""
vigia/core/planner_adapter.py — B-129 Fase 1 (observation only)

Adapter that translates VIGIA case artifacts into EvidenceSignal and
Hypothesis objects for run_bounded_planner(). No integration with the
scorer or verdict path — output is logged alongside the real verdict
for comparison during the observation period.

The adapter generates three competing hypotheses:
- H_BENIGN: all anomalies explained by normal behavior (lowest Ockham cost)
- H_SUSPICION: structural anomalies indicate coordination (medium cost)
- H_MALICE: active concealment of intent (highest cost)

Each hypothesis "explains" signals whose weight exceeds a threshold
proportional to the hypothesis severity. This is a heuristic: the
bounded planner then selects the best by coverage/cost ratio and
detects oscillation if the evidence is genuinely contradictory.

L-027 note: we do NOT use AbductiveIntentEngine here because its
HYPOTHESIS_TEMPLATES require MITRE artifact names (timestamp_uniformity,
process_memory_contradiction) that real corpus cases do not have.
The translation layer SignalOutput -> required_artifacts was never
written. This adapter bypasses that gap entirely by working with
the case artifacts directly.
"""
from __future__ import annotations

from fractions import Fraction
from typing import Any, Dict, List, Optional

from vigia.core.peirceplanner_bounded import (
    EvidenceSignal,
    Hypothesis,
    HypothesisStatus,
    PlannerResult,
    run_bounded_planner,
)


def _to_fraction(raw: Any) -> Fraction:
    """Convert raw value to Fraction, handling tagged dicts and strings."""
    if isinstance(raw, Fraction):
        return raw
    if isinstance(raw, dict) and raw.get("__fraction__"):
        return Fraction(int(raw["num"]), int(raw["den"]))
    try:
        return Fraction(str(raw)).limit_denominator(1000)
    except (ValueError, ZeroDivisionError):
        return Fraction(1, 10)


def _clamp01(f: Fraction) -> Fraction:
    return max(Fraction(0), min(Fraction(1), f))


def _artifact_spoofability(a: Dict[str, Any]) -> Fraction:
    """Same CAIE instantiation as vigia_scorer.py Step 1, same 0.50 fallback."""
    try:
        from vigia.tools.caie import Artifact as _CaieArtifact
        filtered = {
            k: v for k, v in a.items()
            if k in {"source_tool", "evidence_type", "raw_score",
                     "description", "metadata", "provenance_chain",
                     "base_trust", "timestamp"}
        }
        filtered.setdefault(
            "description", str(a.get("content", ""))[:200] or "legacy_artifact"
        )
        spoof = _CaieArtifact(**filtered).effective_spoofability
        return _clamp01(Fraction(str(spoof)).limit_denominator(10000))
    except Exception:
        return Fraction(1, 2)


def case_to_signals(case: Dict[str, Any]) -> List[EvidenceSignal]:
    """
    Translate case artifacts or signals into EvidenceSignal objects.

    Weight semantics: anomaly severity in [0, 1] (the planner hypotheses
    read weight as "how anomalous", not "how certain").

    B-129 Fase 2 calibration (2026-08-27, 208-case dry-run against the
    live scorer — scripts/dryrun_b129_weight_calibration.py):
      confidence-as-weight (Fase 1)          22% agreement
      z_score                                45%
      raw_score * (1 - CAIE spoofability)    56%  <- best, used here
    Confidence measures certainty regardless of direction, so it was
    replaced by the calibrated anomaly measure:

    1. artifacts with raw_score -> raw * (1 - spoofability), spoofability
       from the same CAIE Artifact call the scorer uses (0.50 fallback);
    2. otherwise signal z_score (corpus z_scores already live in [0, 1]);
    3. nothing measurable -> empty list, which run_planner_observation
       reports as NO_SIGNALS/ABSTAIN. The previous fallback fabricated
       weight 5 (out of range) for artifacts missing raw_score.
    """
    artifacts = [a for a in case.get("artifacts", []) if isinstance(a, dict)]
    weighted = []
    for i, a in enumerate(artifacts):
        raw = a.get("raw_score")
        if isinstance(raw, bool) or not isinstance(raw, (int, float)):
            continue
        try:
            raw_frac = _clamp01(Fraction(str(raw)).limit_denominator(10000))
        except (ValueError, ZeroDivisionError):
            continue
        weighted.append(EvidenceSignal(
            signal_id=a.get("artifact_id", f"A-{i:03d}"),
            description=str(a.get("description", ""))[:200],
            weight=_clamp01(raw_frac * (Fraction(1) - _artifact_spoofability(a))),
        ))
    if weighted:
        return weighted

    return [
        EvidenceSignal(
            signal_id=s.get("artifact_id", f"S-{i:03d}"),
            description=str(s.get("description", ""))[:200],
            weight=_clamp01(_to_fraction(s.get("z_score", 0))),
        )
        for i, s in enumerate(case.get("signals", []))
        if isinstance(s, dict)
    ]


def build_hypotheses(signals: List[EvidenceSignal]) -> List[Hypothesis]:
    """
    Build three competing hypotheses from the available signals.

    Assignment logic:
    - H_BENIGN explains signals with weight <= 1/5 (low anomaly)
    - H_SUSPICION explains signals with weight <= 1/2 (moderate anomaly)
    - H_MALICE explains all signals (any anomaly level)

    Ockham costs reflect explanation complexity:
    - BENIGN: Fraction(1, 1) — simplest (things are normal)
    - SUSPICION: Fraction(2, 1) — moderate (coordination needed)
    - MALICE: Fraction(4, 1) — complex (deliberate concealment)
    """
    benign_explains = [s.signal_id for s in signals if s.weight <= Fraction(1, 5)]
    suspicion_explains = [s.signal_id for s in signals if s.weight <= Fraction(1, 2)]
    malice_explains = [s.signal_id for s in signals]

    return [
        Hypothesis(
            hypothesis_id="H_BENIGN",
            description="All anomalies explained by normal operational behavior, "
                        "misconfiguration, or human error. No deliberate intent.",
            ockham_cost=Fraction(1, 1),
            verdict="BENIGN",
            signals_explained=benign_explains,
        ),
        Hypothesis(
            hypothesis_id="H_SUSPICION",
            description="Structural anomalies indicate possible coordination, "
                        "information asymmetry, or strategic information management. "
                        "No evidence of active concealment.",
            ockham_cost=Fraction(2, 1),
            verdict="SUSPICION",
            signals_explained=suspicion_explains,
        ),
        Hypothesis(
            hypothesis_id="H_MALICE",
            description="Active concealment of intent detected. Evidence of "
                        "anti-forensic behavior, fabrication, or deliberate "
                        "manipulation of evidence chain.",
            ockham_cost=Fraction(4, 1),
            verdict="MALICE",
            signals_explained=malice_explains,
        ),
    ]


def run_planner_observation(case: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run the bounded planner on a case and return the observation report.

    This does NOT affect the verdict. It produces a report that is stored
    alongside the real scorer verdict for later comparison.

    Returns a dict with planner results, ready for JSON serialization.
    """
    case_id = case.get("case_id", "UNKNOWN")
    signals = case_to_signals(case)

    if not signals:
        return {
            "case_id": case_id,
            "planner_status": "NO_SIGNALS",
            "planner_verdict": "ABSTAIN",
            "reason": "No signals to analyze",
        }

    hypotheses = build_hypotheses(signals)
    result: PlannerResult = run_bounded_planner(
        initial_hypotheses=hypotheses,
        signals=signals,
    )

    return {
        "case_id": case_id,
        "planner_status": "OK",
        "planner_verdict": result.forensic_verdict[:300],
        "termination_reason": result.termination_reason.value,
        "iterations_used": result.iterations_used,
        "oscillation_detected": result.oscillation_detected,
        "oscillation_pattern": result.oscillation_pattern,
        "winning_hypothesis": (
            result.winning_hypothesis.hypothesis_id
            if result.winning_hypothesis else None
        ),
        "winning_verdict": (
            result.winning_hypothesis.verdict
            if result.winning_hypothesis else "ABSTAIN"
        ),
        "confidence_pct": result.display_confidence_pct(),
        "uncovered_signals": result.uncovered_signals,
        "audit_hash": result.audit_hash,
        "n_signals": len(signals),
        "n_hypotheses": len(hypotheses),
    }
