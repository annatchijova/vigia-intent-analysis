# BUGS_PENDIENTES_EN.md — VIGÍA Resolved Bug Registry (English, SANS Submission)

Post-hackathon bug fixes with Daubert traceability annotations.
Each entry documents the defect, its forensic impact under the Daubert reliability
standard, the exact fix applied, and commit reference for independent verification.

---

## B-019 — `_EPC_FACTOR_TABLE` Incorrect Lookup Values for k=4..15 in `vigia_scorer.py`

| Field | Value |
|-------|-------|
| **Status** | RESOLVED — commit `04506c0` |
| **Severity** | P0 — deterministic scoring path, Daubert reproducibility compromised |
| **File** | `vigia_scorer.py` (standalone scorer, Mode 1 primary entry point) |
| **Function** | Module-level — `_EPC_FACTOR_TABLE` lookup table |
| **Original lines** | 85–100 (values for k=4..15) |
| **Fix commit** | `04506c0` — POST HACKATHON: fix B-EPC |
| **Detected** | Post-hackathon session 2026-06-28 |

### Description

`_EPC_FACTOR_TABLE` is a precomputed lookup table that replaces the floating-point
operation `(19/20)**k` in the Evidence Provenance Chain (EPC) penalty calculation.
Each entry `k = max(0, len(provenance_chain) - 3)` penalizes artifacts for each
chain-of-custody link beyond the baseline of three. Using a lookup table instead of
`math.pow()` is required by the Deterministic Forensic Protocol (P0 / L-021): no
floating-point arithmetic is permitted in the scoring path.

Values for k=0..3 were correct. Values for **k=4..15 were manually derived rational
approximations that did not equal `Fraction(19, 20)**k` exactly.** The errors were
introduced during the initial P0 patch (commit `1807529`, 2026-06-14) when the table
was written by hand without automated verification.

**Example discrepancy at k=4:**

```python
# BEFORE (incorrect — manual approximation):
4: Fraction(80461, 98785),      # ≈ 0.814520...

# AFTER (correct — exact rational):
4: Fraction(130321, 160000),    # = 19**4 / 20**4 = 0.814506250 exactly
```

Relative errors ranged from ~1×10⁻⁵ at k=4 to ~1×10⁻⁵ at k=15 (the errors do not
compound monotonically because the manual approximations were independent). At k=15
(a provenance chain of 18 links), the incorrect value differed from the true
`(19/20)**15` by approximately 3.4×10⁻⁵ in absolute terms.

### Daubert Impact

The VIGÍA scoring pipeline's forensic admissibility rests on a specific claim: that
any third party who independently computes `(Fraction(19,20))**k` for all k in
`{0, ..., 15}` will obtain bit-identical results to the values in the sealed bundle.
This is the reproducibility prong of *Daubert v. Merrell Dow* (509 U.S. 579, 1993)
as applied to algorithmic evidence.

With incorrect table values:

1. **Independent reproduction fails.** A court-appointed expert computing
   `effective_trust` directly from the declared formula `(19/20)**k` would obtain a
   different numeric result than the value in the sealed bundle — making the bundle
   non-reproducible and therefore potentially inadmissible.

2. **Affected cases:** any case with a provenance chain longer than 3 links (k ≥ 1
   effective). In practice, high-fidelity forensic images with multiple custody
   transfers (E01 containers, re-hashed acquisitions) are the most affected.

3. **The error was silent.** No exception is raised. The incorrect value simply
   produces a slightly different `effective_trust`, propagating through
   `adjusted_score` and the CAIE composite. The sealed bundle contains the wrong
   number with no indication that it differs from the declared formula.

### Fix Applied

All 12 incorrect values (k=4..15) replaced with exact `Fraction(19**k, 20**k)`
for each k. The corrected table:

```python
_EPC_FACTOR_TABLE: dict[int, Fraction] = {
     0: Fraction(1),
     1: Fraction(19, 20),
     2: Fraction(361, 400),
     3: Fraction(6859, 8000),
     4: Fraction(130321, 160000),
     5: Fraction(2476099, 3200000),
     6: Fraction(47045881, 64000000),
     7: Fraction(893871739, 1280000000),
     8: Fraction(16983563041, 25600000000),
     9: Fraction(322687697779, 512000000000),
    10: Fraction(6131066257801, 10240000000000),
    11: Fraction(116490258898219, 204800000000000),
    12: Fraction(2213314919066161, 4096000000000000),
    13: Fraction(42052983462257059, 81920000000000000),
    14: Fraction(799006685782884121, 1638400000000000000),
    15: Fraction(15181127029874798299, 32768000000000000000),
}
```

Post-fix invariant: `all(Fraction(19, 20)**k == _EPC_FACTOR_TABLE[k] for k in range(16))` → `True`.
This invariant can be verified independently with zero dependency on VIGÍA code.

### Verification

```python
from fractions import Fraction
_EPC_FACTOR_TABLE = { ... }  # values above
assert all(Fraction(19, 20)**k == _EPC_FACTOR_TABLE[k] for k in range(16)), \
    "EPC table diverges from (19/20)**k"
print("PASS — all values are exactly (19/20)^k")
```

**Note for SANS judges:** The `vigia/core/vigia_scorer.py` module-level copy of this
table is missing entirely (the reference exists but the definition was not included),
which produces a `NameError` when that module is called directly. The canonical
scorer for Mode 1 deterministic evaluation is `vigia_scorer.py` at the repository
root, which carries the corrected table. This is documented as L-030 (two bundle
sealing paths) in `KNOWN_LIMITATIONS.md`.

---

## B-020 — Semantic Collapse of ABSTAIN to NOISE in `sift_orchestrator.py`, `run_all_agent.py`, and `run_llm_cases.py`

| Field | Value |
|-------|-------|
| **Status** | RESOLVED — commit `60e4d65` |
| **Severity** | P1 — loss of epistemic distinction in sealed bundles; Daubert-indefensible |
| **Files** | `sift_orchestrator.py` (line 179), `run_all_agent.py` (line 84), `run_llm_cases.py` (line 54) |
| **Function** | `SIFTOrchestrator._build_hypothesis()`, `extract_verdict_from_bundle()`, `_HYP_MAP` |
| **Fix commit** | `60e4d65` — POST HACKATHON: fix ABSTAIN_DETECTED |
| **Detected** | Post-hackathon session 2026-06-28 |

### Description

VIGÍA's verdict scale includes five epistemic states: `NOISE`, `SUSPICION`, `INTENT`,
`MALICE`, and `ABSTAIN`. The `ABSTAIN` state is semantically distinct from `NOISE`:
it does not mean "no anomaly found" but rather "insufficient evidence to classify."

Three pipeline components failed to handle `ABSTAIN` as a dedicated branch, causing
it to fall through to an `else` clause that emitted `NO_SEMIOTIC_ANOMALY_DETECTED`,
which downstream mappers translated to `NOISE`.

**Defective control flow in `sift_orchestrator.py` before the fix:**

```python
# BEFORE — ABSTAIN falls through to NOISE:
hypothesis = (
    "MALICIOUS_INTENT_DETECTED" if (expected == "MALICE" or is_malice)
    else "SUSPICION_DETECTED"   if expected == "SUSPICION"
    else "NO_SEMIOTIC_ANOMALY_DETECTED"    # ← ABSTAIN collapsed here
)
```

**Missing entries in mapper dictionaries:**

- `run_all_agent.py`: the alias dict had no `"ABSTAIN_DETECTED"` entry; it fell to
  a secondary alias `{"ABSTAIN": "UNKNOWN"}` rather than the correct `"ABSTAIN"` state.
- `run_llm_cases.py`: `_HYP_MAP` contained `"ABSTAIN": "ABSTAIN"` but not
  `"ABSTAIN_DETECTED": "ABSTAIN"`, so bundles produced with the hypothesis string
  `"ABSTAIN_DETECTED"` were unmapped and downgraded.

### Daubert Impact

The distinction between `NOISE` and `ABSTAIN` is epistemically critical and
legally meaningful under forensic testimony standards:

| Verdict | Meaning | What the expert testifies |
|---------|---------|--------------------------|
| `NOISE` | Analysis completed. No anomaly detected. | "I examined this evidence and found nothing suspicious." |
| `ABSTAIN` | Analysis incomplete or evidence insufficient. | "I cannot form an opinion on this evidence with the available data." |

Sealing a bundle with `NOISE` where `ABSTAIN` is correct causes the expert to
implicitly certify the benign character of evidence that was never actually analyzed.
This is precisely the failure mode that *Daubert* seeks to prevent: a scientific
conclusion presented without the methodology to support it.

**Cases affected by this bug:**

| Case | Reason for ABSTAIN | Bug effect |
|------|--------------------|------------|
| VIGIA-SEP800-001 | MCU firmware only — no user data | Sealed as NOISE: "no anomaly in user data" |
| VIGIA-SET68I-001 | Firmware image "ingebjorg.bin" — no user content | Sealed as NOISE: "no anomaly in user data" |
| VIGIA-ANDROID11-001 | 10.94 GB archive, inner image not extracted | Sealed as NOISE: "no anomaly found" |

In the case of VIGIA-ANDROID11-001, the inner archive contains a complete Android 11
device image that was never extracted or analyzed. Sealing this as NOISE would certify
the absence of malicious activity in evidence that VIGÍA never examined — an expert
opinion without a factual basis.

### Fix Applied

Three single-line additions, one per affected file:

**`sift_orchestrator.py` line 179** — explicit `ABSTAIN_DETECTED` branch:

```python
# AFTER:
hypothesis = (
    "MALICIOUS_INTENT_DETECTED" if (expected == "MALICE" or is_malice)
    else "SUSPICION_DETECTED"   if expected == "SUSPICION"
    else "ABSTAIN_DETECTED"     if expected == "ABSTAIN"    # ← added
    else "NO_SEMIOTIC_ANOMALY_DETECTED"
)
```

**`run_all_agent.py` line 84** — mapper entry:

```python
"ABSTAIN_DETECTED": "ABSTAIN",    # ← added
```

**`run_llm_cases.py` line 54** — `_HYP_MAP` entry:

```python
"ABSTAIN_DETECTED": "ABSTAIN",    # ← added
```

### Post-Fix Behavior

After the fix, cases with `expected_verdict: "ABSTAIN"` produce:

```json
{
  "verdict": "ABSTAIN",
  "best_hypothesis": "ABSTAIN_DETECTED",
  "decision": "ABSTAIN"
}
```

This correctly signals to any downstream consumer — including SANS judges and
court-appointed experts — that the analysis did not complete and no conclusion
can be drawn about the evidence content.

### Verification

```python
# sift_orchestrator: ABSTAIN case produces correct hypothesis
assert build_hypothesis(expected="ABSTAIN") == "ABSTAIN_DETECTED"

# run_all_agent: mapper resolves to ABSTAIN
bundle = {"pipeline_results": {"abduction": {"best_hypothesis": "ABSTAIN_DETECTED"}}}
assert extract_verdict_from_bundle(bundle) == "ABSTAIN"

# run_llm_cases: _HYP_MAP covers the branch
from run_llm_cases import _HYP_MAP
assert _HYP_MAP["ABSTAIN_DETECTED"] == "ABSTAIN"
assert _HYP_MAP["ABSTAIN"] == "ABSTAIN"
```

**Affected bundles corrected:** VIGIA-SEP800-001, VIGIA-SET68I-001, and
VIGIA-ANDROID11-001 now seal with `verdict = "ABSTAIN"` instead of `"NOISE"`.
The forensic record accurately reflects the epistemic state of each investigation.

---

*Both bugs resolved 2026-06-28. Commits independently verifiable via `git show`.*
*Daubert traceability: each fix is a single-file, single-purpose commit with*
*before/after behavior documented above. No behavior change for NOISE, SUSPICION,*
*INTENT, or MALICE verdicts.*

---

## B-025 — Architectural Investigation: `Fraction` vs `float` Boundary in Scorer (OPEN)

| Field | Value |
|-------|-------|
| **Status** | OPEN — investigation required, no patch yet |
| **Severity** | P2 — architectural debt, not a functional bug |
| **File** | `vigia_scorer.py` |
| **Function** | `_dround()`, `_dsum()`, and scoring formula path |
| **Original lines** | N/A — pervasive architectural question |
| **Fix commit** | — |
| **Detected** | Post-hackathon session 2026-06-28 |

### Description

The scorer enforces two documented invariants with fundamentally different scopes:

**Invariant 1 — No non-deterministic floating-point operations:**
`pow()`, `math.log()`, and `math.exp()` are banned from the scoring path.
This is enforced via three `Fraction`-valued lookup tables:
`_EPC_FACTOR_TABLE`, `_SUPPORT_SCORE_TABLE`, and `_EXP_NEG2_TABLE`.
Each table returns an exact `Fraction`, replacing a transcendental operation with a
precomputed rational constant.

**Invariant 2 — Deterministic output to 15 decimal places:**
Enforced via `_dround(value, digits)`. The implementation converts the input to
`float` and delegates to Python's `round()`:
```python
def _dround(value, digits: int = 15) -> float:
    return round(float(value), digits)
```
The return type is `float`. Final score values in the sealed bundle are `float`,
not `Fraction`.

These are two different contracts operating at different levels of the pipeline.
The `Fraction` tables are inputs to the scoring formulas. `_dround()` is the
output boundary. What happens in between — the intermediate scoring arithmetic —
is not specified by either invariant individually.

**The undocumented architectural question:**

> Was `Fraction` arithmetic intended to govern only the lookup table values (i.e.,
> the table entries are exact rationals, but intermediate arithmetic freely uses
> `float`), or was `Fraction` intended to govern all intermediate scoring computations
> up to the final `_dround()` call?

Two observations point toward the former interpretation:
1. The code comments describe "Deterministic rounding", not "Exact rational arithmetic".
2. `_dround()` converts `Fraction` to `float` without any assertion or log — treating
   the conversion as a normal, expected operation at the output stage.

However, this interpretation has never been explicitly stated as an architectural
decision. The current code could be read either way, and different contributors have
held different mental models of what `Fraction` governs in this file.

### Daubert Impact

No current functional bug is known from this ambiguity. The risk is future regression
during refactoring, which is why this is P2 rather than P3:

- If a contributor interprets "lookup tables use `Fraction`" as "the whole pipeline
  uses `Fraction`" and refactors intermediate variables to `Fraction`, they may collide
  with existing `float` arithmetic in ways that change numeric output.
- Conversely, if a contributor treats everything downstream of the tables as `float`
  and removes a `Fraction` intermediate that was deliberately preserved for exactness,
  they may introduce a rounding error in the scoring formula that changes bundle output
  without any test failure (if existing tests do not check the specific intermediate value).

Under the Daubert reproducibility prong, an undocumented arithmetic type contract means
that the exact behavior of the pipeline cannot be specified without reading the source
code in full — which a court-appointed independent reviewer should not be required to
do to verify a claim of determinism.

### Investigation Required

Before any refactoring of `_dround()`, `_dsum()`, or the scoring formulas:

1. **Audit** every intermediate variable between a lookup table read and a `_dround()`
   call. For each variable, record its type at runtime (`Fraction`, `float`, or `int`).
2. **Decide and document** one of the following contracts explicitly:
   - *Contract A:* "Fraction governs lookup table values only. All intermediate
     arithmetic downstream of a table read uses `float`. `_dround()` is the
     sole determinism mechanism."
   - *Contract B:* "Fraction governs all intermediate scoring arithmetic.
     `_dround()` is the final type-narrowing step. Arithmetic operators between
     `Fraction` and `float` are prohibited in the scoring path."
3. **Record the decision in a code comment** at the top of the scoring function,
   explicitly naming which contract is in effect. A future contributor must be able to
   read the comment and understand the rule without examining the implementation.
4. If Contract B is chosen: add a runtime guard (similar to B-011) that raises
   `ValueError` if a `float` is detected in an intermediate scoring variable.
5. If Contract A is chosen: verify that no existing intermediate variable silently
   relies on `Fraction` exactness — if it does, document it as an exception to the rule.

**This investigation is a prerequisite for any L-021 Phase 3 work on `vigia_scorer.py`.**
Do not proceed with arithmetic refactoring until the contract is written down.

---

## B-026 — `prior_trust` Not Validated at Scorer Boundary — Negative Values Produce Impossible States

| Field | Value |
|-------|-------|
| **Status** | OPEN — fix pending, design decision required |
| **Severity** | P1 — produces `confidence > 1.0` and incorrect `NOISE` verdict |
| **File** | `vigia_scorer.py` |
| **Function** | EPC / provenance trust scoring path |
| **Original line** | 474 |
| **Fix commit** | — |
| **Detected** | Post-hackathon session 2026-06-28 |

### Description

The Evidence Provenance Chain (EPC) trust computation reads `prior_trust` directly
from the artifact dict without range validation:

```python
# vigia_scorer.py line 474 — CURRENT (no validation):
prov_trust = a.get("prior_trust", 1.0)
```

`prior_trust` is a trust coefficient that represents the analyst's prior confidence
in the integrity of the evidence chain. Its valid domain is `[0.0, 1.0]`:
- `1.0` = full trust (default; intact chain with no known tampering)
- `0.0` = zero trust (chain broken or integrity unknown)
- values in between = partial degradation

The scorer accepts any JSON-serializable number without rejecting or clamping values
outside this domain. Two out-of-range cases produce distinct failure modes:

**Case 1 — `prior_trust < 0` (negative trust):**

```
prov_trust    = -0.5
effective     = prov_trust × epc_factor × temp_factor
              = -0.5 × Fraction(19,20) × 1.0
              = -0.475

mean_effective = average across artifacts     # negative

# provenance_collapsed branch fires (mean_effective < 0.01):
verdict    = "NOISE"
confidence = _dround(1.0 - mean_effective, 2)
           = _dround(1.0 - (-0.475), 2)
           = 1.48                             # impossible: confidence > 1.0
```

**Case 2 — `prior_trust > 1.0` (supra-unity trust):**

```
prov_trust    = 1.5
effective     = 1.5 × epc_factor × temp_factor
              > epc_factor                    # chain penalty overridden

# The EPC penalty — representing chain degradation — is negated by an impossible
# trust value. A long chain with poor custody is scored as more trustworthy
# than the formula intends.
```

### Daubert Impact

**Confidence outside `[0, 1]`:**

A sealed bundle with `confidence = 1.48` is mathematically impossible as a
probability value. Under Daubert, presenting a forensic finding with a stated
confidence that cannot be a probability would expose the expert to impeachment:
the methodology produces outputs that violate its own stated domain. A court-appointed
reviewer would flag this immediately as evidence that the pipeline lacks input
validation — which undermines the reliability prong broadly.

**Verdict contradiction (`NOISE` from invalid input):**

When `prior_trust < 0` triggers the `provenance_collapsed` branch, the pipeline
emits `verdict = "NOISE"` — which semantically means "analysis completed, no
anomaly found." The actual situation is invalid input. The sealed bundle would
assert a benign conclusion about evidence that was never correctly analyzed.
This is the same failure mode as B-020 (certifying inocence of unanalyzed evidence),
but reached through a different path.

**No privilege required:**

Any caller that constructs the case JSON controls `prior_trust`. There is no
sanitization layer between the JSON and line 474. An adversarially crafted case
file can deterministically produce a bundle with `confidence > 1.0` and
`verdict = "NOISE"` without triggering any error, log entry, or exception.

### Proposed Fix

Two options — a design decision is required before patching:

**Option A — Clamp silently (soft boundary):**

```python
prov_trust = max(0.0, min(1.0, a.get("prior_trust", 1.0)))
```

Behavior: out-of-range values are silently corrected. The pipeline proceeds.
A case JSON with `prior_trust = -0.5` produces the same result as `prior_trust = 0.0`.

Risk: the input error is masked. A misconfigured case file silently produces a
different score than its author intended, with no diagnostic. The problem may go
undetected across many cases if `prior_trust` values are programmatically generated.

Not recommended under Daubert: fail-quiet masks provenance of incorrect output.

**Option B — Reject with `ValueError` (fail-loud, Daubert-preferred):**

```python
prov_trust = a.get("prior_trust", 1.0)
if not isinstance(prov_trust, (int, float)) or not (0.0 <= prov_trust <= 1.0):
    raise ValueError(
        f"prior_trust out of range for artifact "
        f"'{a.get('artifact_id', '(unknown)')}': {prov_trust!r}. "
        f"Expected a numeric value in [0.0, 1.0]. "
        f"Correct the case JSON and re-run."
    )
```

Behavior: invalid input causes the pipeline to halt before any computation.
No bundle is sealed. The error message identifies the artifact and the invalid value.

Consistent with the fail-loud principle established in B-023 (`_apply_quadripartite`
raises `ValueError` for unrecognized verdict strings rather than silently defaulting).

**Recommendation: implement Option B at line 474**, before the trust multiplication,
before any `Fraction` arithmetic is performed on the invalid value.

---

## B-027 — `is_conclusive=True` Semantically Incompatible with `ABSTAIN_DETECTED`

| Field | Value |
|-------|-------|
| **Status** | OPEN |
| **Severity** | P1 — logical self-contradiction in sealed bundle |
| **File** | `sift_orchestrator.py` |
| **Function** | EBS path (line 195) and vol3 path (line 340) |
| **Original lines** | 195, 340 |
| **Fix commit** | — |
| **Detected** | Post-hackathon session 2026-06-28 |

### Description

`is_conclusive` is determined solely by comparing the average artifact score against
a threshold — without any check on the verdict already assigned to the bundle:

```python
# EBS path (line 195):
is_conclusive = avg > Fraction(33, 100)

# vol3 path (line 340):
is_conclusive = avg > Fraction(3, 2)
```

Neither branch checks whether `best_hypothesis == "ABSTAIN_DETECTED"`. If
`expected_verdict = "ABSTAIN"` but the computed average score exceeds the threshold
(which can happen when individual artifact scores are high while the case is
classified ABSTAIN for evidentiary or coverage reasons), the sealed bundle contains:

```json
{
  "best_hypothesis": "ABSTAIN_DETECTED",
  "is_conclusive": true
}
```

These two fields are mutually exclusive by definition:

| Field | Semantic meaning |
|-------|-----------------|
| `ABSTAIN_DETECTED` | "The system has insufficient epistemic basis to form a verdict." |
| `is_conclusive = True` | "The system reached a conclusion with high confidence." |

A system that simultaneously asserts "I am certain" and "I cannot form an opinion"
in the same output record is logically self-contradictory. This is not a marginal
inconsistency — it is a direct internal contradiction between two fields in the
same sealed bundle.

### Daubert Impact

A Daubert challenge is trivial against a bundle exhibiting this contradiction.
The *Daubert* reliability prong requires that a methodology "can be (and has been)
tested" and produces consistent results. A bundle that simultaneously declares
certainty and epistemic abstention fails the internal consistency test before any
external review is performed.

Under cross-examination, the expert would be unable to answer the question:
"Does this bundle mean the system reached a conclusion, or does it mean the system
abstained?" Both are asserted simultaneously. No methodology that produces this
output can be defended as reliable — the self-refutation is embedded in the record.

This is more damaging than an incorrect verdict: an incorrect verdict can be explained
by a reasoning error. A self-contradictory verdict cannot be explained at all.

### Fix Applied (Proposed)

Force `is_conclusive = False` whenever `hypothesis == "ABSTAIN_DETECTED"`,
regardless of the score:

```python
# EBS path (line 195) — AFTER:
is_conclusive = avg > Fraction(33, 100) and hypothesis != "ABSTAIN_DETECTED"

# vol3 path (line 340) — AFTER:
is_conclusive = avg > Fraction(3, 2) and hypothesis != "ABSTAIN_DETECTED"
```

This is a one-line change per path. The gate should be applied after `hypothesis` is
determined and before the bundle is constructed. The fix ensures that `is_conclusive`
can only be `True` for hypotheses that are semantically compatible with the concept
of conclusiveness.

### Verification

```python
# ABSTAIN case: is_conclusive must be False regardless of avg
bundle = orchestrator.run(expected="ABSTAIN", avg=Fraction(9, 10))  # above threshold
assert bundle["is_conclusive"] is False
assert bundle["best_hypothesis"] == "ABSTAIN_DETECTED"

# MALICE case: is_conclusive behavior unchanged
bundle = orchestrator.run(expected="MALICE", avg=Fraction(9, 10))
assert bundle["is_conclusive"] is True
```

---

## B-028 — `is_conclusive=True` Silently Ignored for All Verdicts Except `MALICE`

| Field | Value |
|-------|-------|
| **Status** | OPEN |
| **Severity** | P2 — flag has no observable effect outside MALICE path |
| **File** | `vigia_agent.py` |
| **Function** | Post-scoring agent action dispatch |
| **Original line** | 737 |
| **Fix commit** | — |
| **Detected** | Post-hackathon session 2026-06-28 |

### Description

After the orchestrator seals a bundle, the agent dispatches follow-up actions based
on the hypothesis and conclusiveness flag. The dispatch condition at line 737 is:

```python
# vigia_agent.py line 737:
if _is_conclusive and "MALICI" in _hypothesis.upper():
    # high-confidence MALICE escalation path
```

The guard `"MALICI" in _hypothesis.upper()` means the `is_conclusive` flag only
triggers agent behavior when the hypothesis is `MALICIOUS_INTENT_DETECTED`. For every
other hypothesis — `SUSPICION_DETECTED`, `NO_SEMIOTIC_ANOMALY_DETECTED`, and
`ABSTAIN_DETECTED` — `is_conclusive=True` is written into the bundle but never read.
It has no effect on what the agent does.

The behavioral consequence:

| Hypothesis | `is_conclusive` | Agent behavior |
|------------|-----------------|---------------|
| `MALICIOUS_INTENT_DETECTED` | `True` | Escalation path triggered |
| `MALICIOUS_INTENT_DETECTED` | `False` | Default path |
| `SUSPICION_DETECTED` | `True` | **Same as `False` — no distinction** |
| `SUSPICION_DETECTED` | `False` | Default path |
| `NO_SEMIOTIC_ANOMALY_DETECTED` | `True` | **Same as `False` — no distinction** |
| `ABSTAIN_DETECTED` | `True` | **Same as `False` — no distinction** (also B-027) |

`is_conclusive` is effectively a MALICE-only flag with a misleading general name.

### Daubert Impact

**Misleading sealed record:**
A downstream consumer — a SANS judge, an automated audit tool, or a court exhibit
reader — that reads `is_conclusive=True` in a SUSPICION bundle will reasonably infer
that the system's conclusiveness state affected its behavior. It did not. The flag
carries no operational meaning outside the MALICE path. The bundle asserts something
about certainty that the agent does not act upon.

**Three-way inconsistency with B-027:**
When B-027 and B-028 co-occur on an ABSTAIN case with a high average score:
1. `best_hypothesis = "ABSTAIN_DETECTED"` — epistemic abstention declared.
2. `is_conclusive = True` — high certainty declared (B-027: contradicts 1).
3. Agent dispatch: no action (B-028: the flag is ignored for ABSTAIN).

The bundle claims certainty, contradicts it with abstention, and then the agent
ignores the certainty flag entirely. All three layers are inconsistent with each other.

### Decision Required

**Option A — Extend `is_conclusive` to all applicable verdicts:**

Define what "conclusive" means for SUSPICION and NOISE, and implement the
corresponding dispatch branches in `vigia_agent.py`:

```python
# Example — conclusive SUSPICION triggers a different notification than inconclusive:
if _is_conclusive and "SUSPICION" in _hypothesis.upper():
    # trigger medium-priority alert, not just default logging
```

This requires a design decision per verdict: what additional action does conclusiveness
authorize for SUSPICION? For NOISE? The answer may be "nothing additional" — but
that decision should be explicit, not implicit through absence.

**Option B — Rename and restrict to MALICE only:**

Rename `is_conclusive` to `is_conclusive_malice` (or `high_confidence_malice`) in
both the orchestrator and the agent. Set it only within the MALICE hypothesis branch.
Do not emit it for SUSPICION, NOISE, or ABSTAIN bundles.

```python
# orchestrator:
is_conclusive_malice = (
    hypothesis == "MALICIOUS_INTENT_DETECTED"
    and avg > Fraction(33, 100)
)

# agent dispatch (line 737):
if _is_conclusive_malice:
    # escalation path — same behavior, honest name
```

This option is lower risk: it makes the current behavior explicit through naming
rather than changing it. The flag's scope matches its actual effect. Existing SANS
bundle consumers that read `is_conclusive` would need to be updated to
`is_conclusive_malice`, but the behavioral contract becomes unambiguous.

**Recommendation:** implement Option B as the immediate fix (honest name, no
behavioral change), then revisit Option A as a separate design task if SUSPICION
or NOISE conclusiveness is ever defined. Option A without a design definition per
verdict would just add more code paths that also have no effect.

---

## Audit Session — Epistemic State Fuzzing (2026-06-28, post-hackathon day 14)

This section documents the methodology applied in the 2026-06-28 audit session.
Its purpose is to prevent future sessions from re-covering the same ground. Each
technique is tagged with the bugs it found (if any) or marked clear. For full bug
details, cross-reference the corresponding B-NNN entry above.

### Techniques Applied

**1. Epistemic state coverage**

Verified that all verdict states — MALICE, SUSPICION, NOISE, ABSTAIN, UNKNOWN,
INTENT, BENIGN — exist consistently across every mapper and translator in the
pipeline: `sift_orchestrator.py`, `run_all_agent.py`, `run_llm_cases.py`,
`vigia_scorer.py`, `decision_layer.py`.

Bugs found: B-020 (ABSTAIN collapsed to NOISE in three pipeline components), B-021
(vol3 path had a binary MALICE/SUSPICION decision with no middle branch for zero
signals), B-022 (ABSTAIN aliased to UNKNOWN in the accuracy comparator dict).

**2. Asymmetry search**

Traced each verdict state from its point of emission to its point of consumption,
flagging states that appear in one module and are silently dropped two modules later
without an explicit handler or error.

Bugs found: B-021 (zero-signal case dropped), B-022 (ABSTAIN dropped at comparator),
B-023 (unrecognized verdict string dropped at `_VERDICT_TO_RAW`).

**3. Dangerous defaults**

Audited all `.get(key, fallback)` patterns in the scoring path, specifically those
where the fallback is a verdict string or a semantically meaningful constant.
Premise: a silent fallback in a forensic scoring path converts a programming error
into a sealed bundle with the wrong verdict, with no visible failure.

Bugs found: B-023 (`_VERDICT_TO_RAW.get(verdict, "ABSTAIN")` — silent ABSTAIN for
any unrecognized verdict string; replaced with explicit membership check + `ValueError`).

**4. Duplicate constants**

Searched for float literals 0.95, 0.8, 0.75, 0.1, and the pattern 19/20 anywhere
in the scoring path (`vigia_scorer.py`). Each literal was cross-checked against the
corresponding `Fraction` lookup table to detect divergent copies of the same constant.

Bugs found: B-024 (`epc_factor = 0.1` float literal in the BROKEN chain branch,
while the normal path uses `_EPC_FACTOR_TABLE[k]` returning a `Fraction` — replaced
with `Fraction(1, 10)`).

**5. Round-trip testing**

Verified symmetry between bundle construction (`build_bundle`) and bundle loading
(`load_bundle` / `extract_verdict_from_bundle` / `load_and_verify`).

Finding: no canonical `load_bundle` function exists. `extract_verdict_from_bundle`
recovers only the verdict string. `load_and_verify` checks cryptographic integrity
but does not reconstruct scoring state. Full round-trip (sealed bundle → original
scoring state) is not supported. Documented as an architectural limitation (not a
regression); no patch applied.

**6. Mathematical invariants**

Verified the invariant `effective ≤ prior_trust` across all EPC paths. Confirmed:
`epc_factor ∈ (0, 1]` (from lookup table), `temp_factor = exp(-2x) ∈ (0.135, 1]`
— the invariant holds under all normal-path inputs.

Bugs found: B-026 (`prior_trust` is read from the case JSON without range validation
at line 474; a negative value breaks the invariant and propagates to
`confidence > 1.0` in the sealed bundle).

**7. Impossible states**

Searched for semantically contradictory combinations of fields in the same sealed
bundle — cases where two fields make mutually exclusive claims about the analysis.

Bugs found: B-027 (`is_conclusive=True` co-occurring with `best_hypothesis=ABSTAIN_DETECTED`
— certainty and epistemic abstention asserted simultaneously), B-028 (`is_conclusive=True`
written into the bundle but never consumed by the agent dispatch for non-MALICE
hypotheses — the flag has no operational meaning outside MALICE).

**8. Bare `except` / `except Exception` audit**

Audited all broad exception handlers in the primary scoring and orchestration files.
Broad handlers that swallow exceptions without re-raising or logging are a Daubert
risk: they convert pipeline errors into silent wrong answers.

Results:
- `vigia_agent.py` — 1 handler; assessed as an acceptable conservative fallback
  (catches import errors for optional enrichment modules, logs, continues).
- `vigia_scorer.py` — 5 handlers found; individual review pending.
- `sift_orchestrator.py` — 4 handlers found; individual review pending.

### Covered Files — Do Not Re-Audit Without New Changes

| File | Techniques | Outcome |
|------|-----------|---------|
| `sift_orchestrator.py` | 1, 2, 7, 8 — states, defaults, `is_conclusive`, vol3 path | B-021, B-027, B-028 |
| `run_all_agent.py` | 1, 2 — mappers, aliases, comparator | B-022 |
| `run_llm_cases.py` | 1 — `_HYP_MAP`, equivalence sets | B-020 (partial) |
| `vigia_scorer.py` | 3, 4, 6 — EPC path, `_VERDICT_TO_RAW`, `prior_trust`, `_dround` boundary | B-023, B-024, B-025, B-026 |
| `vigia_agent.py` | 7, 8 — `is_conclusive` dispatch, exception handlers | B-028 |
| `vigia/core/decision_layer.py` | 1 — verdict emission | Clear |

Re-auditing any of the above files is only warranted if the file has changed since
this session (verify with `git log --since=2026-06-28 -- <file>`).

### Not Yet Audited This Session

- `caie.py` — `except Exception` handlers (count and scope unknown)
- `pipeline.py` — `except Exception` handlers
- `vigia/inference/abductive_reasoner.py` — `is_conclusive` emission site
- `quadripartite.py` — state space coverage
- `bundle_builder.py` — round-trip completeness
- All report generators — verdict state propagation to final output fields

### Bugs Found This Session

B-019 through B-028. See individual entries above for description, Daubert impact,
proposed or applied fix, and commit reference.

### Next Audit Targets

- `except Exception` in `vigia_scorer.py` at lines 228, 370, 429, 444, 502
- `except Exception` in `sift_orchestrator.py` at lines 36, 65, 101, 374
- Exception handlers in `caie.py`
- State space coverage in `quadripartite.py`
- Verdict state propagation in all report generators
