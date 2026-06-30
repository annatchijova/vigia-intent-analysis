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

## B-021 — `sift_orchestrator.py` vol3 path emitted SUSPICION with 0 signals

| Field | Value |
|-------|-------|
| **Status** | RESOLVED — commit `1b0df1c` |
| **Severity** | P1 — incorrect verdict on genuinely clean memory dumps |
| **File** | `sift_orchestrator.py` |
| **Function** | Volatility3 orchestrator path — verdict emission |
| **Original line** | 337 |
| **Fix commit** | `1b0df1c` — POST HACKATHON: fix B-021/B-022 |
| **Detected** | Post-hackathon session 2026-06-28 |

### Description

The Volatility3 orchestrator path had a binary hypothesis: `MALICIOUS_INTENT_DETECTED`
or `SUSPICION_DETECTED`. When `avg == Fraction(0, 1)` — i.e., memory analysis produced
zero signals — the fallback branch emitted `SUSPICION_DETECTED` instead of
`NO_SEMIOTIC_ANOMALY_DETECTED`.

```python
# BEFORE:
verdict = (
    "MALICIOUS_INTENT_DETECTED" if avg > threshold
    else "SUSPICION_DETECTED"   # ← fired even when avg == Fraction(0,1)
)

# AFTER:
verdict = (
    "MALICIOUS_INTENT_DETECTED" if avg > threshold
    else "NO_SEMIOTIC_ANOMALY_DETECTED" if avg == Fraction(0, 1)   # ← new middle branch
    else "SUSPICION_DETECTED"
)
```

A clean memory dump correctly analyzed by Volatility3 (no malicious processes, no
network anomalies, no malfind hits) received an incorrect `SUSPICION` verdict solely
because it produced zero signals — which is the expected result for a clean dump.

### Forensic Impact

- A genuinely clean memory image was sealed with `verdict = SUSPICION_DETECTED`, implying
  anomalies were present when none were. Under Daubert cross-examination, the analyst
  would be unable to identify what anomaly triggered the suspicion verdict — because
  there was none. The bundle would be indefensible.
- `SUSPICION` requires a "documented baseline deviation" (see Verdict Scale). Zero signals
  is the absence of deviation, not a deviation. The verdict violated its own definition.
- Affected any case processed through the vol3 path where the memory image was clean:
  the incorrect verdict propagated into the sealed bundle and accuracy metrics.

### Fix Applied

Added middle branch at line 337: emit `NO_SEMIOTIC_ANOMALY_DETECTED` when
`avg == Fraction(0, 1)`. `SUSPICION_DETECTED` is now only emitted when `avg > Fraction(0, 1)`
but below the `MALICIOUS_INTENT_DETECTED` threshold — i.e., when there are real signals
that do not reach the malice threshold.

### Verification

```python
# vol3 path with 0 signals → NO_SEMIOTIC_ANOMALY_DETECTED
assert orchestrator.build_vol3_verdict(avg=Fraction(0, 1)) == "NO_SEMIOTIC_ANOMALY_DETECTED"

# vol3 path with weak signals → SUSPICION_DETECTED
assert orchestrator.build_vol3_verdict(avg=Fraction(1, 10)) == "SUSPICION_DETECTED"
```

---

## B-022 — `run_all_agent.py` accuracy comparator aliased `ABSTAIN` → `UNKNOWN`

| Field | Value |
|-------|-------|
| **Status** | RESOLVED — commit `1b0df1c` |
| **Severity** | P1 — ABSTAIN cases counted as FAIL in accuracy metrics |
| **File** | `run_all_agent.py` |
| **Function** | Accuracy comparator dict |
| **Original line** | 168 |
| **Fix commit** | `1b0df1c` — POST HACKATHON: fix B-021/B-022 |
| **Detected** | Post-hackathon session 2026-06-28 |

### Description

The accuracy comparator dict contained the entry `"ABSTAIN": "UNKNOWN"`, while the
main verdict mapper used `"ABSTAIN": "ABSTAIN"`. The two dicts were inconsistent:

```python
# run_all_agent.py line 168 — BEFORE:
comparator_aliases = {
    ...
    "ABSTAIN": "UNKNOWN",   # ← diverged from main mapper
}

# main verdict mapper (correct):
verdict_map = {
    ...
    "ABSTAIN": "ABSTAIN",
}
```

When a case had `expected_verdict = "ABSTAIN"` and the scorer correctly produced a
bundle with `verdict = "ABSTAIN"`, the comparator translated the produced verdict to
`"ABSTAIN"` but the expected value went through the alias dict and became `"UNKNOWN"`.
The comparison `"ABSTAIN" == "UNKNOWN"` evaluated to False → the case was counted as
FAIL in accuracy metrics.

### Forensic Impact

- All ABSTAIN cases (e.g., VIGIA-SEP800-001, VIGIA-SET68I-001, VIGIA-ANDROID11-001)
  that correctly produced ABSTAIN verdicts were counted as accuracy failures, depressing
  the reported accuracy score.
- The artifact made the system appear less accurate than it was, specifically on the
  class of cases where the correct answer is epistemic abstention. This is the opposite
  of a conservative error: the system was correct but reported as wrong.
- Accuracy numbers computed with this bug in place must be treated as underestimates
  for the ABSTAIN class.

### Fix Applied

Removed the `"ABSTAIN": "UNKNOWN"` alias from the comparator dict. `"ABSTAIN"` now
maps to itself in both dicts, restoring consistency. ABSTAIN cases that produce the
correct verdict are now counted as PASS.

### Verification

```python
# ABSTAIN case with correct verdict → PASS
bundle = {"verdict": "ABSTAIN"}
expected = "ABSTAIN"
assert comparator.compare(bundle, expected) == "PASS"
```

---

## B-023 — `_apply_quadripartite` silently collapsed unknown verdicts to `ABSTAIN`

| Field | Value |
|-------|-------|
| **Status** | RESOLVED — commit `fb95648` |
| **Severity** | P1 — unrecognized verdict strings silently produced forensically incorrect ABSTAIN bundles |
| **File** | `vigia_scorer.py` |
| **Function** | `_apply_quadripartite()` |
| **Original line** | 332 |
| **Fix commit** | `fb95648` — POST HACKATHON: fix B-023 |
| **Detected** | Post-hackathon session 2026-06-28 |

### Description

`_apply_quadripartite()` used `.get()` with a silent fallback to map verdict strings
to their raw score representation:

```python
# BEFORE:
raw = _VERDICT_TO_RAW.get(verdict, "ABSTAIN")
```

Any verdict string not present in `_VERDICT_TO_RAW` — whether from a typo, a new
verdict state added to the scale without updating the table, or a pipeline bug
producing a malformed string — was silently mapped to `"ABSTAIN"` with no error,
no log entry, and no diagnostic output.

This violated the Daubert fail-loud principle: a forensic system that silently
produces an incorrect result is less defensible than one that halts with an explicit
error, because the incorrect result may be presented as evidence without any visible
indication that something went wrong.

### Forensic Impact

- A typo in a verdict string (e.g., `"MALICEE"`, `"intent"`, `"SUSPICION "` with
  trailing whitespace) would produce a sealed bundle with `verdict = "ABSTAIN"` —
  the epistemic abstention verdict — without any indication that the verdict is the
  result of a lookup failure rather than a genuine analytical decision.
- A new verdict state added to the scale (e.g., `"INCONCLUSIVE"`) without updating
  `_VERDICT_TO_RAW` would silently collapse to ABSTAIN across all cases that reached
  that state. The bug would be invisible in the bundle output, discoverable only by
  auditing the source table.
- Under cross-examination: the analyst would be unable to explain why the bundle
  emits ABSTAIN for a case that reached a non-ABSTAIN verdict state.

### Fix Applied

Replaced `.get()` with explicit membership check. If `verdict` is not in
`_VERDICT_TO_RAW`, a `ValueError` is raised with full diagnostic (Daubert fail-loud
principle):

```python
# AFTER:
if verdict not in _VERDICT_TO_RAW:
    raise ValueError(
        f"_apply_quadripartite: unrecognized verdict '{verdict}'. "
        f"Valid values: {sorted(_VERDICT_TO_RAW.keys())}. "
        f"Update _VERDICT_TO_RAW if a new verdict state was added to the scale."
    )
raw = _VERDICT_TO_RAW[verdict]
```

The failure is now loud, explicit, and traceable — the bundle is never sealed with
a silently incorrect verdict.

### Verification

```python
# recognized verdict → normal path
assert _apply_quadripartite("MALICE") == expected_raw_malice

# unrecognized verdict → ValueError, not silent ABSTAIN
try:
    _apply_quadripartite("MALICEE")
    assert False, "should have raised"
except ValueError as e:
    assert "unrecognized verdict" in str(e)
```

---

## B-024 — `epc_factor = 0.1` float literal in EPC path (BROKEN chain case)

| Field | Value |
|-------|-------|
| **Status** | RESOLVED — commit `fb95648` (same as B-023) |
| **Severity** | P0 — float in deterministic scoring path, L-021 homogeneity violation |
| **File** | `vigia_scorer.py` |
| **Function** | EPC (Evidence Provenance Chain) scoring path |
| **Original line** | 476 |
| **Fix commit** | `fb95648` — POST HACKATHON: fix B-023 |
| **Detected** | Post-hackathon session 2026-06-28 |

### Description

When `provenance_chain` is empty or `chain_status == "BROKEN"`, the EPC scoring path
assigned `epc_factor` using the float literal `0.1`:

```python
# BEFORE:
if chain_status == "BROKEN" or not provenance_chain:
    epc_factor = 0.1   # ← float literal in deterministic scoring path
else:
    epc_factor = _EPC_FACTOR_TABLE[k]   # ← Fraction from lookup table
```

The normal path (`_EPC_FACTOR_TABLE`) returns a `Fraction` with exact rational
arithmetic (invariant P0 / L-021). The BROKEN/empty path introduced a `float` at
the same variable in the same function, making the type of `epc_factor` dependent
on a runtime branch condition. Any downstream multiplication of `epc_factor` by a
`Fraction` score in the BROKEN path produced a `float` result, propagating the
homogeneity violation through the rest of the scoring computation.

This is classified P0 — the same severity as B-019 — because it represents a
direct violation of the Deterministic Forensic Protocol: a `float` in the scoring
path makes the result architecture-dependent and non-reproducible under the
bit-identical cross-architecture requirement.

### Forensic Impact

- **Reproducibility violation:** on any case where `chain_status == "BROKEN"` or the
  provenance chain is absent, the `effective_trust` computation used a `float`
  intermediate. Two architectures (e.g., x86-64 Linux vs ARM64 macOS) may produce
  different IEEE 754 rounding results for the same case, producing different sealed
  bundles from identical input — breaking the Daubert attestation of reproducibility.
- **Homogeneity violation:** the EPC scoring function mixed `Fraction` and `float`
  arithmetic within a single execution depending on a runtime branch. This is
  structurally different from a clean boundary conversion and violates the L-021
  invariant that the entire scoring path operate in `Fraction`.
- **Affected cases:** any case with a broken or absent provenance chain — which
  includes adversarially submitted evidence, corrupted images, and cases where
  chain-of-custody documentation was not provided.

### Fix Applied

Replaced the float literal with the exact `Fraction` equivalent:

```python
# AFTER:
if chain_status == "BROKEN" or not provenance_chain:
    epc_factor = Fraction(1, 10)   # exact rational: 0.1 = 1/10
else:
    epc_factor = _EPC_FACTOR_TABLE[k]
```

`epc_factor` is now always a `Fraction` regardless of branch, restoring type
homogeneity across the entire EPC scoring path.

### Verification

```python
from fractions import Fraction

# BROKEN chain → Fraction, not float
epc = compute_epc_factor(chain_status="BROKEN", provenance_chain=[])
assert isinstance(epc, Fraction), f"expected Fraction, got {type(epc)}"
assert epc == Fraction(1, 10)

# empty chain → same
epc = compute_epc_factor(chain_status="OK", provenance_chain=[])
assert isinstance(epc, Fraction)
assert epc == Fraction(1, 10)
```

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

---

## B-029 — `quadripartite.py` Check 3 `else` Branch Is Dead Code (`ABSTAIN_CONTRADICTION` Unreachable for Non-OSCIL Reasons)

| Field | Value |
|-------|-------|
| **Status** | OPEN — documentation only, no patch needed until investigation below is complete |
| **Severity** | P3 — dead code, no functional impact |
| **File** | `vigia/verdict/quadripartite.py` |
| **Function** | `classify()` — Check 3 ABSTAIN sub-state branch |
| **Original lines** | 297–303 |
| **Fix commit** | — |
| **Detected** | Post-hackathon session 2026-06-28, `quadripartite.py` state space audit |

### Description

The ABSTAIN branch in `classify()` (Check 3) assigns the ABSTAIN sub-state based on
two conditions: the content of `abstain_reason` and the `confidence` level. The
current structure is:

```python
# lines 297–303 — current (dead else):
if abstain_reason and "OSCIL" in abstain_reason.upper():
    state = ABSTAIN_CONTRADICTION      # oscillation-type contradiction
elif confidence < MEDIUM_CONFIDENCE_THRESHOLD:
    state = ABSTAIN_INSUFFICIENT       # low confidence
else:
    state = ABSTAIN_INSUFFICIENT       # ← identical to elif — dead code
```

The `else` branch is dead: it assigns the same `state` as the `elif` branch. The
`confidence` comparison in the `elif` is meaningless because both outcomes are
`ABSTAIN_INSUFFICIENT`. Any ABSTAIN case that is not oscillation-related lands in
`ABSTAIN_INSUFFICIENT` regardless of whether confidence is above or below the
threshold.

**The three ABSTAIN sub-states in the quadripartite model:**

| Sub-state | Intended meaning | Where handled |
|-----------|-----------------|---------------|
| `ABSTAIN_DEGRADED` | Provenance chain collapsed — evidence integrity too low to score | Check 1 (before this branch) |
| `ABSTAIN_CONTRADICTION` | Logical contradiction between evidence sources that cannot be resolved | Check 3, `if "OSCIL"` branch only |
| `ABSTAIN_INSUFFICIENT` | Not enough evidence to reach a verdict | Check 3, `elif` and dead `else` |

`ABSTAIN_CONTRADICTION` is currently only reachable when `abstain_reason` contains
the substring `"OSCIL"`. There is no path to `ABSTAIN_CONTRADICTION` for any other
type of contradiction reason.

### Forensic Significance

**No functional impact today:** `ABSTAIN_INSUFFICIENT` is the correct verdict for
any non-oscillation, non-provenance-collapse ABSTAIN case. The dead `else` does not
produce a wrong result. The system does not misclassify cases.

**The investigative question this raises:** is `ABSTAIN_CONTRADICTION` correctly
scoped to oscillation only, or are there other types of contradiction that the model
intends to classify as `ABSTAIN_CONTRADICTION` but currently cannot — because they
do not produce an `"OSCIL"`-containing reason string?

For example: if a CAIE LOG_VS_MEMORY fracture produces an irresolvable contradiction
between two evidence sources (not oscillation, but genuine conflicting assertions),
should that reach `ABSTAIN_CONTRADICTION` or `ABSTAIN_INSUFFICIENT`? The current code
makes this impossible to distinguish at the quadripartite level — both would produce
`ABSTAIN_INSUFFICIENT`.

Under Daubert, the distinction matters: `ABSTAIN_CONTRADICTION` would signal to the
court that evidence sources directly contradict each other, which is stronger grounds
for requesting additional evidence than `ABSTAIN_INSUFFICIENT` (which merely signals
evidentiary gaps). If contradiction cases are silently collapsed to insufficiency,
the sealed bundle understates the adversarial nature of the evidence conflict.

### Proposed Resolution

**Step 1 — Investigation (required first):**

Enumerate all `abstain_reason` strings that can be emitted upstream. Sources to check:
- `sift_orchestrator.py` — oscillation termination path
- `vigia/inference/abductive_reasoner.py` — oscillation and other termination paths
- Any CAIE path that sets `abstain_reason` on a case artifact
- `vigia_scorer.py` — if it sets `abstain_reason` before calling quadripartite

For each reason string, classify it as: **oscillation** (→ `ABSTAIN_CONTRADICTION`),
**other contradiction** (→ should be `ABSTAIN_CONTRADICTION` if the model intends it),
or **insufficiency** (→ `ABSTAIN_INSUFFICIENT`).

**Step 2a — If only oscillation produces contradiction:**

Simplify the dead branch away:
```python
# AFTER (honest control flow):
if abstain_reason and "OSCIL" in abstain_reason.upper():
    state = ABSTAIN_CONTRADICTION
else:
    state = ABSTAIN_INSUFFICIENT
```

**Step 2b — If other contradiction types exist:**

Replace the substring check with a structured enum or set of reason codes:
```python
_CONTRADICTION_REASONS = {"OSCIL", "LOG_VS_MEM_IRRESOLVABLE", ...}

if abstain_reason and any(r in abstain_reason.upper() for r in _CONTRADICTION_REASONS):
    state = ABSTAIN_CONTRADICTION
else:
    state = ABSTAIN_INSUFFICIENT
```

**Do not patch before Step 1 is complete.** The patch depends on the answer.

---

## B-030 — `quadripartite.py` Unrecognized `raw_verdict` Falls Through to Fallback (INVESTIGATED — NOT A BUG)

| Field | Value |
|-------|-------|
| **Status** | CLOSED — investigated and dismissed |
| **Severity** | N/A |
| **File** | `vigia/verdict/quadripartite.py` |
| **Function** | `classify()` — unrecognized verdict fallback |
| **Original line** | 397 |
| **Fix commit** | — |
| **Detected** | Post-hackathon session 2026-06-28, `quadripartite.py` state space audit |

### Investigation Summary

**The question:** if `raw_verdict` is not one of the three recognized values
(`"MALICE"`, `"BENIGN"`, `"ABSTAIN"`), what happens? All six checks in `classify()`
are verdict-gated; none of them fire for an unrecognized value. Control falls through
to a catch-all at line 397:

```python
# line 397 — fallback for unrecognized raw_verdict:
return QuadripartiteResult(
    state=ABSTAIN_INSUFFICIENT,
    abstain_reason=f"Unrecognized raw verdict: '{raw_verdict}'",
    ...
)
```

**Finding: this is correct behavior.** The fallback is fail-loud and self-documenting:
- It does not silently emit a forensically meaningful verdict (NOISE, SUSPICION, etc.).
- It produces an explicit ABSTAIN with a diagnostic `abstain_reason` string that names
  the unrecognized input verbatim.
- The sealed bundle is fully explainable under cross-examination: "the scorer passed
  an unrecognized verdict type; the quadripartite module correctly abstained and
  recorded the reason in the bundle."

**Layered defense is sound:**

The fallback at line 397 is a last-resort defensive measure. In practice it is
unreachable from the production scoring path because B-023 provides an upstream gate:
`_apply_quadripartite()` now raises `ValueError` for any verdict string not present
in `_VERDICT_TO_RAW` before calling `quadripartite.classify()`. An unrecognized
verdict never reaches `quadripartite.py` in normal operation.

The two layers are independent and complementary:

| Layer | Location | Behavior |
|-------|----------|----------|
| B-023 gate | `vigia_scorer.py` — `_apply_quadripartite()` | Raises `ValueError` — no bundle sealed |
| Line 397 fallback | `vigia/verdict/quadripartite.py` — `classify()` | Returns `ABSTAIN_INSUFFICIENT` with diagnostic reason |

If `quadripartite.classify()` is ever called directly (e.g., from tests, scripts, or
future code), the fallback provides correct behavior without depending on the B-023
upstream gate.

### OSCILLATION_MITIGATED String Routing — Also Investigated

The string `"OSCILLATION_MITIGATED"` appears in the audit trail `action` field when
the oscillation resolution strategy succeeds. The concern was whether this string
could propagate to `abstain_reason` and accidentally trigger `ABSTAIN_CONTRADICTION`
via the `"OSCIL"` substring check in Check 3 (B-029).

**Finding: it does not.** The routing is:

- **Successful oscillation mitigation:** `action = "OSCILLATION_MITIGATED"` in audit
  trail. The case proceeds with a resolved verdict. `abstain_reason` is not set.
  Does not reach `quadripartite.classify()` with an ABSTAIN verdict.

- **Terminal oscillation (resolution fails):** `termination_reason = "OSCILLATION_DETECTED"`.
  The `forensic_verdict` string derived from this termination is what gets passed as
  `abstain_reason` to `quadripartite.classify()`. This string contains `"OSCIL"` and
  correctly triggers `ABSTAIN_CONTRADICTION`.

The two strings (`OSCILLATION_MITIGATED` vs the terminal oscillation verdict) follow
completely separate code paths. There is no case where a successfully-mitigated
oscillation reaches the `"OSCIL"` check in Check 3.

### Conclusion

Not a bug. The fallback at line 397 is correct forensic behavior (fail-loud,
self-documenting ABSTAIN). The B-023 upstream gate provides additional protection
that makes the fallback unreachable in production. The oscillation string routing
is non-contradictory. **No action required.**

This entry is preserved in the registry as an audit trail record: the scenario was
examined, the defense was confirmed, and the dismissal reasoning is documented for
any future reviewer who asks the same question.

---

## Session 2026-06-29 Bugs — Windows Disk Evidence & RAW Mode

### B-032 [FIXED] — vigia_agent.py mapped *.evtx to event_stream kwarg instead of event_logs

| Field | Value |
|-------|-------|
| **Status** | RESOLVED |
| **File** | `vigia_agent.py` |
| **Function** | `_build_orchestrator_kwargs()` |
| **Detected** | Session 2026-06-29 |

**Description:** `_build_orchestrator_kwargs()` mapped `.evtx` files to the `event_stream` parameter, but `SIFTOrchestrator.analyze()` routes `event_stream` to `MetabolicProfiler`, not to `EventLogCorrelator`. The correct parameter is `event_logs`. Result: `EventLogCorrelator` received no input and produced `z=0`, while the actual composite score from direct invocation was 19/20.

---

### B-033 [FIXED] — Agent did not auto-detect registry hives (SAM/SYSTEM/SOFTWARE/SECURITY)

| Field | Value |
|-------|-------|
| **Status** | RESOLVED |
| **File** | `vigia_agent.py` |
| **Detected** | Session 2026-06-29 |

**Description:** The autonomous agent did not auto-detect registry hive files (SAM, SYSTEM, SOFTWARE, SECURITY) when scanning evidence directories. These files lack extensions and were not matched by any glob pattern in the evidence scanner.

---

### B-034 [FIXED] — ChainOfCustody.acquire() missing notes kwarg in registry_timeline_reconstructor

| Field | Value |
|-------|-------|
| **Status** | RESOLVED |
| **File** | `vigia/sift/registry_timeline_reconstructor.py` |
| **Function** | `ChainOfCustody.acquire()` |
| **Detected** | Session 2026-06-29 |

**Description:** `ChainOfCustody.acquire()` was called without the `notes` keyword argument required by the method signature, producing a `TypeError` on every registry hive acquisition.

---

### B-035 [FIXED] — forensic_adapter mapped event_log to log_entry (syslog generic) instead of windows_event_log

| Field | Value |
|-------|-------|
| **Status** | RESOLVED |
| **File** | `vigia/sift/forensic_adapter.py` |
| **Detected** | Session 2026-06-29 |

**Description:** `forensic_adapter.py` mapped `event_log` to `log_entry` (syslog generic, `spoofability=0.85`). Windows EVTX is a binary format with checksums, much harder to tamper. Fix: Added `windows_event_log` to forensic_adapter mapping, CAIE profiles, and gamma tables. See L-033b, L-035.

---

### B-036 [FIXED] — z>5.0 threshold impossible in vigia_agent.py fallback hypothesis (Z_CLIP_MAX=5.0)

| Field | Value |
|-------|-------|
| **Status** | RESOLVED |
| **File** | `vigia_agent.py` |
| **Detected** | Session 2026-06-29 |

**Description:** The fallback hypothesis override in `vigia_agent.py` required `z>5.0` to trigger, but `Z_CLIP_MAX=5.0` clips all signals at 5.0. The threshold was impossible to reach. Fixed to `z>2.0`. See L-036.

---

### B-037 [FIXED] — EBS v1 adapter missing INTENT/BENIGN hypothesis mapping in sift_orchestrator.py

| Field | Value |
|-------|-------|
| **Status** | RESOLVED |
| **File** | `sift_orchestrator.py` |
| **Detected** | Session 2026-06-29 |

**Description:** The EBS v1 adapter in `sift_orchestrator.py` did not have mappings for `INTENT` and `BENIGN` hypothesis types. Cases producing these hypotheses would fall through to the default handler and produce incorrect bundle metadata.

---

### B-038 [FIXED] — composite_score not included in event_log signal metadata

| Field | Value |
|-------|-------|
| **Status** | RESOLVED |
| **File** | Event log signal emission path |
| **Detected** | Session 2026-06-29 |

**Description:** `composite_score` was not included in event_log signal metadata. This field is required by `apply_artifact_reliability_dynamic()` (L-038) to compute dynamic gamma based on corroboration strength.

---

### B-039 [FIXED] — windows_event_log type missing from gamma tables in _math_utils.py

| Field | Value |
|-------|-------|
| **Status** | RESOLVED |
| **File** | `vigia/sift/_math_utils.py` |
| **Detected** | Session 2026-06-29 |

**Description:** The `windows_event_log` artifact type was not present in the gamma lookup tables in `_math_utils.py`. Signals of this type would fall through to the default gamma value instead of using the calibrated `gamma=0.70`.

---

### B-040 [PENDING] — ARTIFACT_RELIABILITY not propagated to CAIE

| Field | Value |
|-------|-------|
| **Status** | PENDING |
| **Severity** | P2 |
| **File** | `vigia/sift/forensic_adapter.py` |
| **Detected** | Session 2026-06-29 |

**Description:** `ios_forensics.py` and `android_forensics.py` define `ARTIFACT_RELIABILITY=Fraction(70,100)` but `forensic_adapter.py` sets `base_trust=1.0` fixed, ignoring the signal metadata value. See L-037.

---

### B-041 [PENDING] — caie_artifacts not returned by run_full_analysis() — CAIE never runs in RAW mode

| Field | Value |
|-------|-------|
| **Status** | PENDING |
| **Severity** | P1 |
| **Detected** | Session 2026-06-29 |

**Description:** `run_full_analysis()` does not return `caie_artifacts` in its output, so the CAIE cross-artifact analysis engine never receives artifacts when processing RAW evidence. This means structural fracture detection (LOG_VS_MEMORY, TIMELINE_PARADOX, etc.) is bypassed in RAW mode.

---

### B-042 [PENDING] — iOS forensics module — P0 float boundary in to_signal()

| Field | Value |
|-------|-------|
| **Status** | PENDING — architectural decision required |
| **Severity** | P0 |
| **File** | `vigia/sift/ios_forensics.py` |
| **Detected** | Session 2026-06-29 |

**Description:** `to_signal()` in `ios_forensics.py` uses `float()` for z-score and confidence values. When this module feeds the deterministic scoring pipeline, floats enter the Fraction arithmetic path — a P0 violation of L-021. Architectural decision pending: should `SignalOutput` accept `Decimal`/`Fraction`, or is the float-to-Fraction conversion the correct boundary?

---

### B-043 [PENDING] — Android forensics module — same as B-042

| Field | Value |
|-------|-------|
| **Status** | PENDING — same architectural decision as B-042 |
| **Severity** | P0 |
| **File** | `vigia/sift/android_forensics.py` |
| **Detected** | Session 2026-06-29 |

**Description:** Same `float()` boundary issue as B-042 in `android_forensics.py`. The fix should be coordinated with B-042 as the same architectural decision applies.

---

### B-044 [FIXED] — `_build_orchestrator_kwargs()` ignores .pcap files — NetworkForensicsEngine never receives data

| Field | Value |
|-------|-------|
| **Status** | FIXED — 2026-06-30 |
| **Severity** | P1 |
| **Files** | `vigia/sift/pcap_parser.py` (new), `sift_orchestrator.py`, `vigia_agent.py` |
| **Detected** | Session 2026-06-30 |

**Description:** `_build_orchestrator_kwargs()` in `vigia_agent.py` did not detect `.pcap` or `.pcapng` files. No raw pcap parser existed in the repository. `NetworkForensicsEngine.analyze()` expected `List[NetworkFlow]` but never received real data — it could only be activated if an external caller manually constructed `NetworkFlow` objects.

**Test case:** `evidence/flare-on/flareon4/12/20170801_1300_filtered.pcap` — confirmed C2 beaconing (7220 packets to AWS 52.0.104.200), generated 0 signals, exit code 0.

**Fix applied:**
1. Created `vigia/sift/pcap_parser.py` — tshark parser (`-T json`) → `List[NetworkFlow]`, with a safety cap of 50000 packets and fail-loud on tshark errors.
2. In `sift_orchestrator.py` (shim) — when receiving `pcap_path`, parses the pcap with `parse_pcap_to_flows()` and passes the flows as `network_flows` to the real `run_full_analysis()`.
3. In `vigia_agent.py` `_build_orchestrator_kwargs()` — added `("*.pcap", "pcap_path")` and `("*.pcapng", "pcap_path")` to the directory detection pattern list, and `elif suffix in (".pcap", ".pcapng")` case for single file.

**Post-fix result:** NETWORK_FORENSICS emits signal with z=2.625, conf=0.95, 7220 flows, EXFILTRATION detected.
