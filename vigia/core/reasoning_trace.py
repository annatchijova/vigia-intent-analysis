"""
vigia/core/reasoning_trace.py
=============================
A native, deterministic reasoning-trace layer for VIGÍA — "Cronos adapted to
VIGÍA". It records the Peircean forensic loop (hypotheses, evidence, refutations,
verdict) as a tamper-evident trace sealed BESIDE the ForensicBundle, never
inside the sealed verdict (LLM/trace stays out of the decision path).

PROCESS EVIDENCE, NEVER RESULT EVIDENCE — read this before wiring.
-----------------------------------------------------------------
This trace records HOW the investigation reasoned, not WHAT it concluded. The
authoritative result is, and remains, the sealed `bundle_hash` / verdict in the
ForensicBundle. The trace is attached OUTSIDE that hash (a narrative sibling
excluded from `bundle_hash`, like `integrity`), so editing the trace does NOT
invalidate the verdict — and, symmetrically, the trace can never *become* the
verdict. Its own integrity is self-contained: the embedded ToolExecutionLogChain
(entry_hash/entry_hmac + chain_tip anchor) seals the trace independently.

Because the two live side by side, there is exactly one rule: the verdict the
trace records in its DECISION step MUST equal the sealed bundle verdict. A
divergence between them is NOT an acceptable ambiguity to be interpreted away —
it is a BUG in the wiring (the trace was built from a different result than the
one sealed), and a verifier that sees `reasoning_trace.verdict != bundle verdict`
must FAIL, never silently prefer one. The trace explains the sealed result; it
must never contradict it. `sealed_verdict()` exposes the recorded verdict so the
wiring/verifier can assert this equality at the boundary.

Ported and adapted from the Cronos black-box recorder, with three VIGÍA-native
changes:

1. DETERMINISM. Cronos stamps wall-clock `datetime.now()` and `uuid4()` into
   each step; a VIGÍA trace that gets sealed must be reproducible bit-for-bit.
   Here trace_id is derived from case_id, step order is a logical counter, and
   the seal timestamp is injected (the case timestamp), so the same investigation
   yields the same sealed chain tip. Zero floats — confidence is `Fraction`.

2. HONEST-DEGRADATION DOCTRINE AT THE API (B-148/L-066). Evidence carries an
   ObservationState. NOT_ANALYZED / ANALYSIS_FAILED evidence can NEVER `supports`
   or `refutes` a hypothesis — "I did not look" is attenuating context, not a
   positive observation. Only ANALYZED evidence counts toward observational
   diversity (and thus toward the confidence ceiling). This is the exact
   distinction Forge's disposition.py and Cronos's detect_negation encode, now
   enforced structurally rather than by convention.

3. REUSE VIGÍA'S CHAIN (B-151b). Sealing uses the existing
   `ToolExecutionLogChain` (v2: entry_hash + entry_hmac + tail anchor), not a
   second SHA-256 chain. Refutations and gate-driven downgrades are emitted as
   `contradiction_detector` self-correction entries — the tamper-evident
   self-correction events CLAUDE.md mandates but the Mode-1 path did not chain.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from fractions import Fraction
from typing import Any, Dict, List, Optional

from vigia.core.tool_log_chain import ToolExecutionLogChain, verify_tool_execution_log

CRONOS_TRACE_VERSION = "1.0"


# ── Enums ──────────────────────────────────────────────────────────────────────

class TraceQuality(str, Enum):
    """Observational completeness — VIGÍA acquisition-assurance gating."""
    FULL = "FULL"        # all three observation groups present
    PARTIAL = "PARTIAL"  # two groups
    MINIMAL = "MINIMAL"  # one group
    EMPTY = "EMPTY"      # no real observations (only objective/decision)


class StepKind(str, Enum):
    OBJECTIVE = "objective"              # case + evidence scope
    TOOL = "tool"                        # a forensic tool was run
    HYPOTHESIS = "hypothesis"            # a verdict candidate (abduction)
    EVIDENCE = "evidence"                # an artifact observation
    DISCARD = "discard"                  # a hypothesis refuted (Refutation Protocol)
    SELF_CORRECTION = "self_correction"  # a gate downgraded a verdict (contradiction_detector)
    DECISION = "decision"                # the sealed verdict


class ObservationState(str, Enum):
    """B-148 four-state model, generalized: distinguishes a real observation
    from the absence of one. Only ANALYZED is a positive observation."""
    ANALYZED = "ANALYZED"                # the layer was examined; the fact is real
    NOT_ANALYZED = "NOT_ANALYZED"        # the layer was never examined — absence, not negative
    ANALYSIS_FAILED = "ANALYSIS_FAILED"  # examined but the input was malformed/degraded


_POSITIVE_OBSERVATION = frozenset({ObservationState.ANALYZED})


@dataclass
class TraceStep:
    kind: StepKind
    payload: Dict[str, Any]
    seq: int  # logical order — deterministic, no wall clock in the sealed content


# ── Epistemics (ported from Cronos quality.py — Fraction only) ─────────────────

# Confidence ceiling by observational diversity: even a perfect chain of custody
# cannot eliminate uncertainty; thin observation caps confidence.
_DIVERSITY_CEILING: Dict[int, Fraction] = {
    3: Fraction(1),        # fully diverse → no ceiling
    2: Fraction(17, 20),   # 0.85
    1: Fraction(3, 5),     # 0.60
    0: Fraction(1, 5),     # 0.20 — no real observations
}
_EVIDENCE_FLOOR = Fraction(1, 10)  # any supporting ANALYZED evidence → confidence cannot be 0

# Negation: absence-shaped facts must read as attenuating, never as confirmation.
_NEGATION_RE = re.compile(
    r"\b(no|not|never|none|nothing|without|absence|absent|lack|lacking|missing|"
    r"failed\s+to|unable\s+to|did\s+not|does\s+not|cannot|can't|isn't|aren't|"
    r"wasn't|weren't|hadn't|haven't|don't|doesn't|didn't|no\s+evidence\s+of)\b",
    re.IGNORECASE,
)


def detect_negation(text: str) -> bool:
    """True if the evidence text carries a negation within the first 200 chars."""
    return bool(_NEGATION_RE.search(text[:200]))


def _observation_groups(steps: List[TraceStep]) -> int:
    """Count the three forensic observation groups present:
      A — TOOL     (analysis actually run)
      B — EVIDENCE that is ANALYZED (a real positive observation, not absence)
      C — HYPOTHESIS or DISCARD (abduction + refutation)
    NOT_ANALYZED / ANALYSIS_FAILED evidence deliberately does NOT count toward B."""
    kinds = {s.kind for s in steps}
    groups = 0
    if StepKind.TOOL in kinds:
        groups += 1
    if any(
        s.kind == StepKind.EVIDENCE
        and s.payload.get("observation") == ObservationState.ANALYZED.value
        for s in steps
    ):
        groups += 1
    if kinds & {StepKind.HYPOTHESIS, StepKind.DISCARD}:
        groups += 1
    return groups


def diversity_score(steps: List[TraceStep]) -> Fraction:
    return Fraction(_observation_groups(steps), 3)


def compute_quality(steps: List[TraceStep]) -> TraceQuality:
    g = _observation_groups(steps)
    return {3: TraceQuality.FULL, 2: TraceQuality.PARTIAL,
            1: TraceQuality.MINIMAL, 0: TraceQuality.EMPTY}[g]


def apply_confidence_constraints(confidence: Fraction, steps: List[TraceStep]):
    """Apply the diversity ceiling and evidence floor. Returns (adjusted, warnings)."""
    warnings: List[str] = []
    g = _observation_groups(steps)
    ceiling = _DIVERSITY_CEILING[g]
    has_supporting = any(
        s.kind == StepKind.EVIDENCE
        and s.payload.get("observation") == ObservationState.ANALYZED.value
        and s.payload.get("supports")
        for s in steps
    )
    floor = _EVIDENCE_FLOOR if has_supporting else Fraction(0)
    adj = confidence
    if adj > ceiling:
        warnings.append(
            f"Confidence {confidence} capped at {ceiling} "
            f"(diversity ceiling: {g}/3 observation groups)"
        )
        adj = ceiling
    if adj < floor:
        warnings.append(
            f"Confidence {confidence} raised to floor {floor} "
            f"(supporting analyzed evidence present — cannot be zero)"
        )
        adj = floor
    return adj, warnings


def find_contradictions(steps: List[TraceStep]) -> List[str]:
    """Type A — a hypothesis has ANALYZED evidence both supporting and refuting it.
    Type B — a hypothesis has ANALYZED supporting evidence but was discarded."""
    supports, refutes, discarded = set(), set(), set()
    for s in steps:
        if s.kind == StepKind.EVIDENCE and s.payload.get("observation") == ObservationState.ANALYZED.value:
            if s.payload.get("supports"):
                supports.add(s.payload["supports"])
            if s.payload.get("refutes"):
                refutes.add(s.payload["refutes"])
        elif s.kind == StepKind.DISCARD:
            discarded.add(s.payload["label"])
    out = []
    for h in sorted(supports & refutes):
        out.append(f"Type A: '{h}' has analyzed evidence both supporting and refuting it")
    for h in sorted(supports & discarded):
        out.append(f"Type B: '{h}' has analyzed supporting evidence but was discarded")
    return out


# ── The trace ──────────────────────────────────────────────────────────────────

class ForensicReasoningTrace:
    """
    Deterministic reasoning trace for one VIGÍA investigation.

        t = ForensicReasoningTrace(case_id="CASE-001", objective="...")
        t.record_tool_call("infer_intent", "artifact-3", "intent=deliberate")
        t.add_hypothesis("malice", "deliberate anti-forensics")
        t.add_evidence("log deletion observed", ObservationState.ANALYZED, supports="malice")
        t.discard_hypothesis("benign_sysadmin", "no config change explains the deletion")
        sealed = t.seal(verdict="SUSPICION", confidence=Fraction(3, 5), sealed_at=case_ts)

    seal() returns a dict carrying the ordered steps, quality/diversity/
    contradictions, the constrained confidence, and a `tool_execution_log`
    (+ tail-anchor bundle fields) produced by ToolExecutionLogChain — ready to
    attach beside the sealed bundle. It never returns or alters the verdict.
    """

    def __init__(self, case_id: str, objective: str, mode: str = "python_fallback") -> None:
        if not case_id:
            raise ValueError("case_id is required (trace_id is derived from it, deterministically)")
        self.case_id = case_id
        self.trace_id = f"rt-{case_id}"
        self.mode = mode
        self._steps: List[TraceStep] = []
        self._sealed = False
        self._append(StepKind.OBJECTIVE, {"objective": objective, "case_id": case_id,
                                          "trace_version": CRONOS_TRACE_VERSION})

    # ── recording ──────────────────────────────────────────────────────────────

    def _append(self, kind: StepKind, payload: Dict[str, Any]) -> None:
        if self._sealed:
            raise RuntimeError("trace already sealed — no further steps may be recorded")
        self._steps.append(TraceStep(kind=kind, payload=payload, seq=len(self._steps)))

    def record_tool_call(self, tool: str, target: str, result_summary: str,
                         arguments: Optional[Dict[str, Any]] = None) -> None:
        self._append(StepKind.TOOL, {"tool": tool, "target": target,
                                     "result": result_summary, "arguments": arguments or {}})

    def add_hypothesis(self, label: str, description: str) -> None:
        self._append(StepKind.HYPOTHESIS, {"label": label, "description": description})

    def add_evidence(self, text: str, observation: ObservationState,
                     supports: str = "", refutes: str = "") -> None:
        """Record an observation. B-148 doctrine, enforced: only an ANALYZED
        observation may support or refute a hypothesis. A NOT_ANALYZED /
        ANALYSIS_FAILED fact is attenuating context — it cannot be a positive
        (or negative) confirmation, so supports/refutes are rejected for it."""
        if not isinstance(observation, ObservationState):
            raise TypeError("observation must be an ObservationState")
        if supports and refutes:
            raise ValueError("evidence cannot both support and refute — call add_evidence twice")
        if (supports or refutes) and observation not in _POSITIVE_OBSERVATION:
            raise ValueError(
                f"{observation.value} evidence cannot support/refute a hypothesis: "
                "absence of analysis is not a positive observation (B-148). Record it "
                "without supports/refutes, as attenuating context."
            )
        payload: Dict[str, Any] = {"text": text, "observation": observation.value}
        if supports:
            payload["supports"] = supports
        if refutes:
            payload["refutes"] = refutes
        if detect_negation(text):
            payload["negation_detected"] = True
        self._append(StepKind.EVIDENCE, payload)

    def discard_hypothesis(self, label: str, reason: str) -> None:
        """Refutation Protocol: a benign/rival hypothesis tested and rejected."""
        self._append(StepKind.DISCARD, {"label": label, "reason": reason})

    def record_self_correction(self, finding_id: str, verdict_before: str,
                               verdict_after: str, reason: str) -> None:
        """A gate downgraded a verdict pre-emission (B-151b): the tamper-evident
        self-correction event CLAUDE.md mandates. Chained on seal as a
        contradiction_detector entry."""
        self._append(StepKind.SELF_CORRECTION, {
            "finding_id": finding_id,
            "verdict_before": verdict_before,
            "verdict_after": verdict_after,
            "reason": reason,
        })

    # ── sealing ──────────────────────────────────────────────────────────────

    def _summarize(self, step: TraceStep) -> str:
        p = step.payload
        if step.kind == StepKind.SELF_CORRECTION:
            return (f"BEFORE: {p['verdict_before']} | AFTER: {p['verdict_after']} "
                    f"| REASON: {p['reason']}")
        if step.kind == StepKind.EVIDENCE:
            link = p.get("supports") or p.get("refutes") or "-"
            return f"[{p['observation']}] {p['text']} ({link})"
        if step.kind == StepKind.HYPOTHESIS:
            return f"{p['label']}: {p['description']}"
        if step.kind == StepKind.DISCARD:
            return f"{p['label']} discarded: {p['reason']}"
        if step.kind == StepKind.TOOL:
            return f"{p['tool']}({p['target']}) -> {p['result']}"
        if step.kind == StepKind.OBJECTIVE:
            return p.get("objective", "")
        return str(p)

    def seal(self, verdict: str, confidence: Fraction, *, sealed_at: str) -> Dict[str, Any]:
        """Seal the trace deterministically. `sealed_at` is the injected case
        timestamp (never wall-clock) so the same investigation seals identically.
        `confidence` must be a Fraction in [0,1]. Returns the sealed trace dict
        with a chained tool_execution_log + tail-anchor fields."""
        if self._sealed:
            raise RuntimeError("trace already sealed")
        if not isinstance(confidence, Fraction):
            raise TypeError("confidence must be a fractions.Fraction — no floats in the trace")
        if not (Fraction(0) <= confidence <= Fraction(1)):
            raise ValueError(f"confidence must be in [0,1] — got {confidence}")

        self._append(StepKind.DECISION, {"verdict": verdict,
                                         "confidence": f"{confidence.numerator}/{confidence.denominator}"})
        self._sealed = True

        quality = compute_quality(self._steps)
        groups = _observation_groups(self._steps)  # 0..3; shown as groups/3 (denominator is meaningful)
        contradictions = find_contradictions(self._steps)
        adj_confidence, warnings = apply_confidence_constraints(confidence, self._steps)

        # Chain every step with the existing v2 chain. Deterministic: event_id
        # and timestamp are injected from trace_id/seq/sealed_at (no uuid4/now()).
        chain = ToolExecutionLogChain(mode=self.mode)
        log: List[Dict[str, Any]] = []
        for step in self._steps:
            entry = chain.append(
                tool=(f"contradiction_detector" if step.kind == StepKind.SELF_CORRECTION
                      else f"reasoning:{step.kind.value}"),
                target=self.case_id,
                result_summary=self._summarize(step),
                arguments={"seq": step.seq, "payload": step.payload},
                event_id=f"{self.trace_id}:{step.seq}",
                timestamp=sealed_at,
            )
            log.append(entry)

        sealed = {
            "trace_id": self.trace_id,
            "case_id": self.case_id,
            "trace_version": CRONOS_TRACE_VERSION,
            "sealed_at": sealed_at,
            "verdict": verdict,
            "confidence_submitted": f"{confidence.numerator}/{confidence.denominator}",
            "confidence_stored": f"{adj_confidence.numerator}/{adj_confidence.denominator}",
            "confidence_warnings": warnings,
            "quality": quality.value,
            "diversity": f"{groups}/3",
            "contradictions": contradictions,
            "steps": [{"seq": s.seq, "kind": s.kind.value, "payload": s.payload}
                      for s in self._steps],
            "tool_execution_log": log,
        }
        sealed.update(chain.bundle_fields())  # chain_tip_sha256 (+ chain_tip_hmac)
        return sealed

    def sealed_verdict(self) -> Optional[str]:
        """The verdict recorded in the DECISION step (None until sealed).

        The wiring and any verifier MUST assert this equals the sealed bundle
        verdict. A divergence is a wiring bug — the trace was built from a
        different result than the one sealed — and must FAIL verification, never
        be silently reconciled (see the module docstring: process, not result)."""
        for s in reversed(self._steps):
            if s.kind == StepKind.DECISION:
                return s.payload.get("verdict")
        return None


@dataclass
class ReasoningTraceVerification:
    valid: bool
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {"valid": self.valid, "errors": list(self.errors)}


def sealed_trace_verdict(trace: Dict[str, Any]) -> Optional[str]:
    """Read the recorded verdict from a sealed trace dict (loaded from file)."""
    v = trace.get("verdict")
    if v is not None:
        return v
    for step in reversed(trace.get("steps", [])):
        if step.get("kind") == StepKind.DECISION.value:
            return step.get("payload", {}).get("verdict")
    return None


def verify_reasoning_trace(bundle: Dict[str, Any], trace: Dict[str, Any],
                           **hmac_kwargs) -> ReasoningTraceVerification:
    """Verify a reasoning trace against the bundle it explains.

    Two independent checks, both must pass:
      (i)  the trace's own tamper-evident chain is intact (ToolExecutionLogChain);
      (ii) the verdict the trace recorded EQUALS the bundle's sealed
           `agent_verdict`. This is the process-not-result invariant: the trace
           explains the sealed result and must never contradict it. A divergence
           is a WIRING BUG and MUST fail here — it is never silently reconciled.

    The trace lives OUTSIDE the bundle_digest (a sibling artifact with its own
    integrity), so this pairing check is the only thing binding the two: it must
    be strict.
    """
    errors: List[str] = []

    log = trace.get("tool_execution_log")
    if not isinstance(log, list) or not log:
        errors.append("trace has no tool_execution_log to verify")
    else:
        declared_tip = trace.get("chain_tip_sha256")
        if not isinstance(declared_tip, str) or not declared_tip:
            errors.append("trace has no declared chain_tip_sha256 to anchor its tail")
            declared_tip = None
        chain = verify_tool_execution_log(
            log,
            expected_tip=declared_tip,
            expected_tip_hmac=trace.get("chain_tip_hmac"),
            **hmac_kwargs,
        )
        if not chain.valid:
            errors.append(f"trace chain invalid: {chain.to_dict()}")

    trace_case = trace.get("case_id")
    bundle_case = bundle.get("case_id")
    if trace_case != bundle_case:
        errors.append(f"case_id mismatch: trace={trace_case!r} bundle={bundle_case!r}")

    trace_verdict = sealed_trace_verdict(trace)
    bundle_verdict = bundle.get("agent_verdict")
    if trace_verdict != bundle_verdict:
        errors.append(
            f"VERDICT DIVERGENCE (wiring bug): trace recorded {trace_verdict!r} "
            f"but the sealed bundle verdict is {bundle_verdict!r} — the trace was "
            f"built from a different result than the one sealed."
        )

    return ReasoningTraceVerification(valid=not errors, errors=errors)


def build_from_agent_bundle(bundle: Dict[str, Any]) -> Dict[str, Any]:
    """Derive a sealed reasoning trace from a sealed vigia_agent bundle.

    Built entirely from data the agent already sealed, so it explains — never
    re-decides — the result:
      - the abductive hypothesis (best_hypothesis);
      - the artifacts the agent could NOT analyze, as NOT_ANALYZED evidence
        (B-148 honest degradation — absence is not a positive observation);
      - the self-corrections it applied, as contradiction_detector entries
        (B-151b — chained, tamper-evident, in Mode-1).
    The DECISION verdict is the sealed `agent_verdict`, so the pairing check in
    verify_reasoning_trace() holds by construction. Deterministic given the
    bundle: sealed_at is the bundle's own analysis_timestamp, so the same sealed
    bundle always yields the same trace (and thus the same chain tip)."""
    case_id = str(bundle.get("case_id") or "UNKNOWN")
    verdict = str(bundle.get("agent_verdict") or "ABSTAIN")
    results = bundle.get("pipeline_results") if isinstance(bundle.get("pipeline_results"), dict) else {}
    abduction = results.get("abduction") if isinstance(results.get("abduction"), dict) else {}
    inner = results.get("results") if isinstance(results.get("results"), dict) else {}
    unanalyzed = inner.get("unanalyzed_artifacts") or []
    corrections = results.get("self_corrections") or []
    sealed_at = str(bundle.get("analysis_timestamp") or "1970-01-01T00:00:00+00:00")

    t = ForensicReasoningTrace(
        case_id=case_id,
        objective=f"Forensic intent analysis of {bundle.get('evidence_path', case_id)}",
        mode="python_fallback",
    )
    t.add_hypothesis("primary", str(abduction.get("best_hypothesis") or "UNDETERMINED"))
    for ua in list(unanalyzed)[:50]:
        if isinstance(ua, dict):
            label = ua.get("evidence_type") or ua.get("path") or ua.get("id") or "unknown"
        else:
            label = str(ua)
        t.add_evidence(f"artifact not analyzed: {label}", ObservationState.NOT_ANALYZED)
    for c in list(corrections)[:50]:
        if not isinstance(c, dict):
            continue
        ctype = str(c.get("contradiction_type") or "contradiction")[:64]
        action = str(c.get("recommended_action") or c.get("suggested_verdict_upgrade") or "corrected")
        t.record_self_correction(
            finding_id=ctype,
            verdict_before=str(abduction.get("best_hypothesis") or "?"),
            verdict_after=action,
            reason=ctype,
        )
    # Submitted confidence = 1; the diversity ceiling turns it into the honest
    # stored value (thin observation → capped confidence).
    return t.seal(verdict=verdict, confidence=Fraction(1, 1), sealed_at=sealed_at)
