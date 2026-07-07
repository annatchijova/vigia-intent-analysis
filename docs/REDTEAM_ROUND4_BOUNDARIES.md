# Security Audit — VIGÍA Forensic Intent Scorer

## Red Team Round 4 — Boundary Conditions

**Date:** 2026-07-07  **Method:** Abductive Engineering (A–D–I) + Red-Team Auditing (epistemic ladder)
**Scope:** `vigia_scorer._vigia_score` at boundary inputs — 0 artifacts, empty/degenerate case, same-type floods, malformed artifacts.
**Base:** `claude/monotonicity-invariants-redteam-sc0x9r` @ `e0e7be0` (audit) → fixes on top.
**Restore tag:** `pre-session-r4-20260707-150231`
**Runtime:** CPython 3.11.15
**Reproducible evidence:** `scripts/redteam_round4_boundaries.py`

## Threat model

- Attacker **CAN**: assemble the case JSON — choose the number of artifacts, their `evidence_type`, `raw_score`, and pass degenerate/malformed values or a `None` case object.
- Attacker **CANNOT**: modify code, break the seal, forge HMAC.
- Trust boundary: the scorer's input surface. A forensic scorer must never crash on a degenerate input and must stay bounded/deterministic under volume (a crash or a multi-minute hang is a denial-of-analysis).

## Epistemic legend

CODE FACT · PLAUSIBLE HYPOTHESIS · **CONFIRMED BY INDUCTION** · FALSIFIED

## Executive summary

| ID | Severity | Level | Bucket | Finding | Status |
|----|----------|-------|--------|---------|--------|
| R4-1 | Medium | **CONFIRMED BY INDUCTION** | vuln (perf) | Same-type flood → **O(n²)** in the M2-1 best-prefix decay (2000 artifacts = 8.1 s). | **FIXED** (O(n), bit-identical) |
| R4-2 | Medium | **CONFIRMED BY INDUCTION** | vuln (perf/DoS) | No scorer-level artifact cap; CAIE `Artifact` is instantiated **twice per artifact** (~1.4 ms each) — the dominant cost, linear but unbounded. | Documented (recommendation) |
| R4-3 | Medium | **CONFIRMED BY INDUCTION** | invariant/semantic | A flood of the **most-spoofable** type (`log_entry`, spoofability 0.85) saturates the composite to MALICE (100× → 0.984). | Documented (needs calibration doctrine) |
| R4-4 | Low | **CONFIRMED BY INDUCTION** | hygiene | `None` / non-dict `case` crashes with `AttributeError` instead of a clean `ERROR`. | **FIXED** (guard) |

Two fixes landed (R4-1, R4-4); two findings are recorded for a follow-up decision (R4-2 needs a refactor/cap-policy call; R4-3 is a scoring-semantics change that needs a calibration doctrine, like the M2 relabels).

---

## R4-1 — Same-type flood is O(n²) in the best-prefix decay  · FIXED

**Surprise.** After the M2-1 monotonicity fix (Round 2), scoring 1000 same-type
artifacts took ~3 s and 2000 took ~8 s — super-linear for a deterministic scorer.

**Abduction (rivals).** (a) CAIE pairwise fracture detection is O(n²); (b) the
M2-1 **best-prefix** decay loop is O(n²) — it evaluates *every* prefix k=1..n per
type, each building a length-k list; (c) `_normalize_case`.

**Deduction → Induction (cProfile @ n=1000).** The best-prefix listcomp
(`vigia_scorer.py:792`) is called 1000× and drives **504 512** `_dround` calls
(0.85 s) — the classic Σk = n²/2 signature. Rival (a) CAIE `__post_init__` is
2.77 s but **linear** in calls (see R4-2). So the *super-linear* component is (b),
the code M2-1 introduced.

**Causal chain.**
```
1000 same-type artifacts, one evidence_type group of size n
   ↓ best-prefix loop: for k in 1..n  →  build list of size k, math.prod
Σ_{k=1..n} O(k) = O(n²)  →  ~500k _dround calls at n=1000
```

**Fix.** The candidate prefixes reduce to **{1, 2, 3, 4, n}** with *no change to
the result*: `penalty(k)=min(0.5,(k-1)·0.15)` is constant (0.5) for k≥5, so in that
regime the Noisy-OR factor is non-increasing in k (each extra artifact multiplies
by `(1−adj)≤1`) — the best prefix among k≥5 is always k=n. Only k∈{1,2,3,4} (where
penalty varies) and k=n can win; evaluated ascending with `≤` to preserve the
legacy tie-break (largest prefix wins). **O(n) per type.**

**Verification.** Bit-identical over **20 000** random cases (incl. degenerate:
equal values, zeros). M2-1 monotonicity tests still green. Timing: n=2000
**8.1 s → 6.1 s** (the residual is R4-2, CAIE); the quadratic component is gone
(per-doubling ratio 2.6× → ~1.9×). Corpus 166/199, byte-identical fail set.

---

## R4-2 — No scorer-level artifact cap; per-artifact CAIE cost dominates  · documented

**CODE FACT + CONFIRMED.** CAIE enforces `_MAX_ARTIFACTS = 1000` in
`add_artifact` (`caie.py:1002`), but the **scorer** runs its own per-artifact
loops (effective-trust, spoofability, best-prefix) over *all* artifacts with **no
cap**. cProfile shows `CAIE Artifact.__post_init__` called **2000×** for 1000
artifacts (once for `detect_fractures`, once for `effective_spoofability`),
2.77 s total — the dominant cost, linear but unbounded: 10 000 artifacts ≈ 30 s.

**Bucket:** performance/DoS vuln, but bounded-linear, not a crash. **Threat-model
precondition:** attacker submits an oversized artifact set to a scoring endpoint.

**Recommendations (record only):**
- Enforce a scorer-level artifact cap (or explicit truncation with an audit note)
  mirroring CAIE's `_MAX_ARTIFACTS`, so the scorer never does unbounded work.
- Memoize `effective_spoofability` by `(evidence_type, acquisition-metadata
  signature)` — for a same-type flood it is identical across artifacts, so 1000
  instantiations collapse to 1.

---

## R4-3 — Spoofable-type flood saturates to MALICE  · documented

**Surprise / expectation violated.** CAIE's own docstring claims the Noisy-OR
grouping "prevents flood attacks where one tool generates 100 alerts." Yet a flood
of the **single most spoofable** evidence class reaches MALICE.

**Induction.**
```
  4x log_entry (spoofability 0.85) -> SUSPICION  score=0.1672
 10x log_entry                     -> MALICE     score=0.3393
 50x log_entry                     -> MALICE     score=0.8741
100x log_entry                     -> MALICE     score=0.9842
```

**Causal chain.** The scorer's composite is `1 − ∏(1 − adj_i)` over *all*
artifacts after a redundancy penalty capped at 0.5. Beyond ~4 same-type
artifacts the penalty is maxed, so each additional artifact still adds Noisy-OR
mass → the composite saturates toward 0.99. The B-068 gate then opens on
`n_artifacts ≥ 4`, and MALICE is emitted — even though every source is
`log_entry`, the class an admin can forge with `echo >> syslog`.

**Bucket:** invariant/semantic. This is the flood-attack analogue of the R2 No-
Dilution finding: cardinality of a *cheap* class manufactures a high-severity
verdict. **Not fixed here** because damping it changes scoring semantics and
needs a calibration decision (per-type flood damping, or gating corroboration on
low-spoofability classes) — the same doctrine-call shape as the M2 relabels.

**Recommendation (record only):** cap the composite contribution *per evidence
class* (group Noisy-OR then combine across classes, as CAIE already does
internally), and/or require the B-068 corroboration to rest on at least one
low-spoofability class before MALICE.

---

## R4-4 — `None` / non-dict case crashes  · FIXED

**CONFIRMED.** `_vigia_score(None)` → `AttributeError: 'NoneType' object has no
attribute 'get'` (via `case.get("artifacts")` after `_normalize_case`). Any
non-dict (`str`, `int`, `list`, …) crashes the same way.

**Fix.** A type guard at the top returns a clean `{"verdict": "ERROR", …}` for a
non-dict case (and again after `_normalize_case`, in case the bridge degrades the
type). Fail-loud, never an exception.

---

## Discarded (non-exploitable) vectors

| Vector | Result | Why it failed |
|--------|--------|---------------|
| 0 artifacts (`{"artifacts": []}`) | Clean `ERROR` | Guard at `vigia_scorer.py:441` returns ERROR, no crash. |
| Empty case `{}` / `{"artifacts": None}` | Clean `ERROR` | Same guard (falsy artifacts). |
| One empty artifact `[{}]` | `NOISE`, no crash | Finite-Math + type shields default every missing field. |
| `raw_score` = None / "high" / inf / NaN | `NOISE`, score 0 | Finite-Math shield coerces non-finite/non-numeric → 0.0. |
| `prior_trust = -5` | `ABSTAIN` | B-026 clamp → effective trust collapses → ABSTAIN (correct). |
| `evidence_type` = None / 123 | `NOISE`, no crash | Unknown type → worst-class fallback weight (B-067). |
| `provenance_chain` = "str" | `NOISE`, no crash | B-031 retypes non-list chain → []. |

The shields (P6 Finite-Math, B-026/B-031/B-067) absorb every malformed-artifact
vector tried — no crash, bounded score. That layer is doing its job.

---

## Recommendations summary (out of scope of the landed fixes — record only)

1. **R4-2:** scorer-level artifact cap + memoize `effective_spoofability` per class.
2. **R4-3:** per-class composite damping and/or low-spoofability corroboration gate
   before MALICE — needs a calibration doctrine decision.
