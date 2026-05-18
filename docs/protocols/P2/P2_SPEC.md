# VIGÍA Protocol P2 — Advanced Forensic Semantics Specification

> **Protocol:** P2
> **Version:** 2.8-Draft
> **Date:** 2026-05-16
> **Status:** Draft / Pre-freeze
> **Target freeze:** 2026-06-15 (advisory, conditional on freeze_criteria)
> **Depends on:** P1 (frozen, immutable)
> **Schema:** `canonical_vectors_p2.json` v2.8
> **Maintainers:** VIGÍA AI Collective (Anna Tchijova, Kimi, Claude, Gemini, DeepSeek, ChatGPT, Qwen, Grok)

---

## 0. Philosophy of P2

P1 answered: *"Does the entropy kernel produce the same results everywhere?"*

P2 answers: *"Is the system mathematically consistent, adversarially robust, and epistemologically honest?"*

P2 is a **categorical jump**:

| Layer | P1 | P2 |
|------|-----|-----|
| Semantics | Isolated symbols | Context, memory, sequence |
| Invariance | None | Monotonic (PE), temporal (Markov) |
| Adversarial | Basic (NaN, Inf) | Denormals, stress, fuzzing, tie-breaking |
| Decision | Out of scope | Formalized abstention |
| Traceability | Absent | Chain-of-custody |
| Canonicalization | `round(x, 6)` | `Decimal.quantize()` HALF_EVEN |

---

## 1. Protocol Scope

P2 covers ONLY:

| Component | Covered? | P1 Status |
|-----------|----------|-----------|
| entropy_kernel | ✅ Inherited | Frozen |
| pair_encoding | ✅ Inherited | Frozen |
| backend_determinism | ✅ Inherited | Frozen |
| **markov_order_k** | ✅ **NEW** | Draft |
| **lempel_ziv_complexity** | ✅ **NEW** | Draft |
| **permutation_entropy** | ✅ **NEW** | Draft |
| **abstention_policy** | ✅ **NEW** | Draft |
| **adversarial_robustness** | ✅ **NEW** | Draft |
| **chain_of_custody** | ✅ **NEW** | Draft |
| **symbolization_policy** | ✅ **NEW** | Draft |
| **compliance_levels** | ✅ **NEW** | Draft |
| **discretization_policy** | ✅ **NEW (v2.5)** | Draft |
| **terminology_warnings** | ✅ **NEW (v2.5)** | Draft |
| **known_adversarial_gaps** | ✅ **NEW (v2.5)** | Draft |
| hypothesis engine | ❌ | Future (P3) |
| graph scoring | ❌ | Future |
| classifier_policy | ❌ | Future |

**A build that passes P2 is NOT "VIGÍA official".** It is "VIGÍA-compatible P2 for advanced forensic semantics."

---

## 2. Non-Goals (legal protection)

P2 explicitly does NOT pursue:

- Semantic interpretation of evidence
- Authorship attribution
- Truth inference
- Intent inference
- Psychological profiling
- Legal admissibility certification
- Absolute ground-truth correctness
- Behavioral classification of humans vs bots
- Ontological claims about "humanity" or "authenticity"

**P2 is a reproducibility contract for entropy mathematics.** Reproducibility is not truth. Determinism is not authority. Mathematical consistency does not imply semantic correctness. Any inference beyond distributional properties requires independent forensic validation.

---

## 3. Terminology Warnings (interpretive overreach hardening — NEW in v2.5)

P2 metrics (entropy, Markov, Lempel-Ziv, permutation entropy) are **distributional descriptors**. They are NOT detectors of: AI-generated content, human authorship, deception, manipulation, intent, or authenticity. Names of mathematical quantities must not be reified into ontological categories.

**Prohibited interpretive phrasings:**

- "AI detector"
- "bot detector"
- "human-vs-machine classifier"
- "authenticity score"
- "deception score"
- "intent score"
- "humanity index"

**Permitted interpretive phrasings:**

- "distributional variability measure"
- "compressibility estimate"
- "ordinal complexity estimate"
- "conditional entropy estimate"

**Rationale:** Distributional properties of a signal do not encode the ontological status of its producer. A high-entropy sequence is not "more human" and a low-entropy sequence is not "more synthetic". Any such mapping requires a calibrated, dataset-specific, externally validated decision layer that is OUTSIDE P2 scope.

**Revocation clause (NEW in v2.6):** Any build whose documentation, UI labels, CLI output, API field names, or marketing material uses any phrase from the prohibited list AUTOMATICALLY FORFEITS the right to claim "VIGÍA-compatible P2", regardless of vector passage. This is non-negotiable and applies retroactively to any prior claim. Validators MAY scan implementation strings as a best-effort check, but the revocation clause is normative regardless of automated enforcement.

---

## 3a. Interpretation Safeguards (counterexamples — NEW in v2.6)

Even with terminology warnings, the ecosystem will attempt to reinterpret entropy metrics as ontological signals (high entropy → human, low entropy → AI). This is inevitable and cannot be fully prevented at the protocol level. P2 v2.6 formalizes the counterexamples implementations SHOULD include in user-facing documentation to make the failure modes legible alongside the metrics.

| ID | Naive claim | Counterexamples |
|----|-------------|-----------------|
| **REINT-01** | "High Shannon entropy indicates human authorship" | Form-filling, structured templates, repetitive professional writing; stylistically constrained genres (legal, medical, technical reports); speech-to-text under quiet conditions with predictable phrasing |
| **REINT-02** | "Low Shannon entropy indicates synthetic/AI authorship" | High-temperature LLM sampling; adversarially-trained generators optimized for distributional naturalness; models with entropy regularization toward natural-text targets |
| **REINT-03** | "Low Lempel-Ziv complexity indicates non-natural origin" | DNA sequences in repetitive regions; network telemetry under steady-state load; sensor data in quiescent physical systems |
| **REINT-04** | "High permutation entropy indicates randomness" | Logistic map at chaotic parameter regimes; deterministic PRNG output; Lorenz attractor trajectories at small embedding dimensions |

**Documentation requirement:** Implementations claiming VIGÍA-compatible P2 SHOULD include at least one counterexample from each REINT-NN category in user-facing material that displays P2 metric values. Recommended, not strictly normative, but strongly encouraged.

**Rationale:** P2's mathematical core cannot prevent semantic misuse downstream. The most honest available defense is to make the failure modes legible alongside the metrics themselves. Counterexamples reduce — but do not eliminate — the risk of ecosystem reinterpretation.

---

## 4. Discretization Policy (upstream gap acknowledgment — NEW in v2.5)

P2 operates on discrete symbols under exact float64 equality. Continuous signals (audio, sensor data, network telemetry, DSP output) **MUST be discretized before P2 metrics are applied**. P2 does NOT define the discretization step.

**In scope:**

- Mathematics of discrete symbol sequences once discretization is fixed
- Reproducibility of metric output given identical discrete input
- Rejection of NaN, Inf, denormals at metric ingress

**Out of scope:**

- Choice of bin width, codebook, or quantizer for continuous data
- ADC quantization, jitter compensation, DSP normalization
- Codec artifacts, GPU kernel rounding, parser float drift
- Symbolic explosion induced by floating-point noise in upstream pipelines

**Upstream risk acknowledgment:** Real-world signals are subject to noise, jitter, codec artifacts, and parser drift that can artificially inflate the symbol space under exact-equality symbolization. P2 is mathematically consistent but is NOT, by itself, forensically robust against this upstream risk.

**Chain-of-custody requirement:** Any P2 application to non-natively-discrete data MUST record the discretization function, its parameters, and its provenance in `chain_of_custody.processing_manifest`. Failure to do so invalidates forensic reproducibility claims even if P2 vectors pass.

**Future work:** A formal upstream discretization standard is a candidate for P3. P2 deliberately delegates this to the implementer to keep the mathematical core freezable.

---

## 5. Dependency on P1

```
P2 (advanced semantics)
└── P1 (base determinism)
    └── IEEE 754 float64
```

P2 validators MUST:

1. Validate all P1 vectors first.
2. Only if P1 passes, validate P2 vectors.
3. Report: `"P1: PASS, P2: PASS/FAIL"` — never `"P2: PASS"` alone.

---

## 6. Reference Runtime

| Property | Value |
|----------|-------|
| Language | Python |
| Exact tested versions | 3.11, 3.12 |
| Quantization | `Decimal(value).quantize(Decimal('1.000000'), rounding=ROUND_HALF_EVEN)` |
| Rounding reference | IEEE-754 round-half-to-even via Python decimal module |
| Markov implementation | Histogram-based, single-pass, pure MLE |
| LZ implementation | LZ76 factorization, full history |
| PE implementation | Sliding window, stable sort for ties |
| **PRNG binding** | **`numpy.random.Generator(numpy.random.PCG64(seed))` — NumPy ≥ 1.17** |

### 6a. PRNG Binding (NEW in v2.7 — DeepSeek #3, refined in v2.8 — DeepSeek #5)

Several vectors specify `"type": "prng", "algorithm": "PCG64", "seed": N`. The bare name "PCG64" is ambiguous: O'Neill's reference, NumPy's binding, and Boost's implementation produce different output streams from the same seed. P2 pins the **NumPy binding** as the bit-identity reference, with compliance-level-tiered requirements.

**Reference call:**

```python
import numpy as np
rng = np.random.Generator(np.random.PCG64(seed))
samples = rng.integers(low, high, size=n, endpoint=False)
```

**Compliance-level requirements (refined in v2.8):**

| Compliance level | PRNG requirement |
|------------------|-------------------|
| **Strict** | Non-NumPy implementations MUST produce bit-identical output streams to the NumPy reference. Acknowledged as highly demanding (NumPy-specific 64-bit packing, endianness, and rejection-sampling logic must be matched exactly). Implementations that cannot meet bit-identity are disqualified from strict compliance. |
| **Reference** | Bit-identity relaxed to **statistical equivalence** with documented seeding. Any PCG64 family implementation passing standard randomness tests under the same seed semantics is acceptable. Any divergence from the NumPy reference stream MUST be documented in the compliance manifest. |
| **Accelerated** | Any deterministic seeded PRNG acceptable, with documentation. Not eligible for "VIGÍA-compatible P2" claim regardless. |

**Rationale for tiered requirements:** Bit-identity across language ecosystems is generally not achievable for PCG64 even when implementations are mathematically correct. Forensic audit (strict) needs the strongest guarantee. Production DFIR (reference) tolerates documented divergence as long as it is statistically equivalent. Demanding bit-identity across the board would needlessly exclude correct implementations.

---

## 7. Self-Contained Definitions Inlined from P1 (NEW in v2.7 — DeepSeek #4)

For reviewer convenience, P2 v2.7 inlines the three entropy definitions that P2 references but inherits from P1. P1 remains authoritative; these are mirror definitions for self-containment.

### 7a. Shannon Entropy

- **Formula:** `H = -Σ p_i · log₂(p_i)`
- **Alphabet construction:** Set of distinct symbols extracted via `exact_equality` symbolization (no binning, no hashing).
- **Log base:** 2
- **Empty input:** `H(∅) = 0`
- **Single distinct symbol:** `H = 0`
- **Function name in vectors:** `entropy_shannon`

### 7b. Entropy Normalized

- **Formula:** `H_norm = H / log₂(|alphabet|)` when `|alphabet| > 1`; `0` otherwise.
- **Range:** `[0.0, 1.0]`
- **Function name in vectors:** `entropy_normalized`

### 7c. Entropy Rate

- **Description:** Shannon entropy over the distribution of adjacent non-overlapping pairs, tokenized into uint64 via `pair_encoding`.
- **Formula:** `H_rate = -Σ_t P(t) · log₂(P(t))` over distinct pair tokens.
- **Normalized:** `H_rate / log₂(|distinct pair tokens|)` when defined.
- **Function name in vectors:** `entropy_rate`

---

## 8. Canonicalization

### 7.1 Decimal Quantization

P2 v2.4+ replaces `round(x, 6)` with **explicit decimal quantization**:

```python
from decimal import Decimal, ROUND_HALF_EVEN

def canonical_quantize(value):
    d = Decimal(str(value))
    return float(d.quantize(Decimal('1.000000'), rounding=ROUND_HALF_EVEN))
```

**Why:** CPython's `round()` delegates to the C library. Behavior may differ across platforms. `Decimal.quantize()` with explicit context eliminates platform divergence.

**Comparison rule:** `canonical_quantize(actual) == canonical_quantize(expected)`

---

## 8. Serialization Layers

P2 defines **three separate layers**:

### 8.1 Transport Layer

- Format: JSON per RFC 8259
- Encoding: UTF-8
- No semantic extensions

### 8.2 Serialization Layer

- Canonicalization: `custom_vigia_p2`
- Rules: insertion order, specific separators, no ASCII escape
- Float serialization: shortest round-trip decimal (semantic primary, CPython reference informative)

### 8.3 Semantic Layer

- Protocol-aware interpretation of special values
- Tokens: `{"type": "special_float", "value": "NaN|Inf|denormal"}`
- Parser MUST interpret per `input_encoding`, not as literal dicts

---

## 9. Symbolization Policy

### 9.1 Exact Equality

Two values `a, b` are the same symbol **iff** `a == b` under IEEE-754 float64 equality.

### 9.2 Signed Zero

`+0.0` and `-0.0` **MUST** map to the same symbol (IEEE-754 equality returns `True`).

### 9.3 No Canonicalization Before Symbolization

Values are symbolized **BEFORE** quantization. `1.0000000001` and `1.0` are **DIFFERENT** symbols.

### 9.4 No Hash-Based Symbolization

No hashing, no bucketing, no binning for discrete entropy functions.

### 9.5 Continuous Data

User must discretize externally (see §4 — Discretization Policy). P2 does not provide automatic binning.

---

## 10. Pair Encoding

| Property | Value |
|----------|-------|
| Domain | `uint32 × uint32` |
| Input range | `[0, 4294967295]` |
| Negative policy | `reject` — `raise ValueError` |
| Overflow policy | `reject` — `raise OverflowError` |
| Packing formula | `token = (uint64(a) << 32) \| uint64(b)` |
| Endianness | Semantic big-endian (`a`: bits [63:32], `b`: bits [31:0]) |
| Output type | `uint64` |
| Collision-free proof | Bijective mapping. No collisions possible. |

---

## 11. Backend Equivalence

| Property | Value |
|----------|-------|
| Comparison | `canonical_quantize(actual) == canonical_quantize(expected)` |
| Reduction order | `implementation_defined` |
| Accumulator dtype | `float64 mandatory` |
| Maximum nondeterminism | `0` post-quantization |
| Note | Parallel reductions may accumulate differently. Must match after canonical quantization. |

**No float32, no tensor cores, no mixed precision.**

---

## 12. Compliance Levels

### 12.1 Strict

**For:** Forensic audit, legal proceedings, academic reproducibility.

- Python pure only
- Sequential reduction
- `Decimal.quantize()` HALF_EVEN
- All 22 P2 vectors + all P1 vectors
- **Claim:** "VIGÍA-compatible P2 (strict)"

### 12.2 Reference

**For:** Production DFIR, research, cross-platform.

- NumPy/CuPy permitted
- Parallel reduction allowed
- `float64` accumulator mandatory
- `Decimal.quantize()` HALF_EVEN
- All 22 P2 vectors + all P1 vectors
- **Claim:** "VIGÍA-compatible P2"

### 12.3 Accelerated

**For:** Real-time streaming, high-volume, embedded.

- Any backend permitted
- `float32` / `float16` permitted with documented precision loss
- Must pass P1 vectors
- Must pass documented P2 subset
- **CANNOT claim "VIGÍA-compatible P2"**
- **MUST use:** "VIGÍA-accelerated", "P2-subset", or "P2-inspired"
- **Any claim of P2 compatibility without full passage is MISLEADING and PROHIBITED.**

---

## 13. Mathematical Definitions

### 13.1 Markov Order-k Entropy

**Formula:**

```
H_k = -Σ_{w ∈ contexts} P(w) · Σ_{s ∈ symbols} P(s|w) · log₂(P(s|w))
```

**Smoothing:** `none` (pure MLE). No Laplace, no Kneser-Ney, no add-epsilon.

**Precondition:** `len(sequence) > k`
**Violation:** `raise ValueError`

---

### 13.2 Lempel-Ziv Complexity (LZ76)

**Pseudocode (exact):**

```
INPUT:  sequence S[0..n-1]
OUTPUT: integer c

1. IF n == 0: RETURN 0
2. c ← 1; u ← 1; v ← 1; vmax ← 1; i ← 0
3. WHILE u + v <= n:
4.     IF S[i+v-1] == S[u+v-1]: v ← v+1
5.     ELSE:
6.         vmax ← max(v,vmax); i ← i+1
7.         IF i == u: c ← c+1; u ← u+vmax; v ← 1; i ← 0; vmax ← 1
8.         ELSE: v ← 1
9. IF v != 1: c ← c+1
10. RETURN c
```

**Complexity:** Implementation-dependent. Naive: O(n²) worst-case. Optimized suffix-tree: O(n).

**Normalization:** `LZC_norm = c(n) / (n / log₂(n))`

**Worked examples** (cross-referenced in `lempel_ziv_definition.reference_factorization_semantics.reference_examples`):

| Input | Factors | Count |
|-------|---------|-------|
| `[1,2,1,2,1,2]` | `[1], [2], [1,2,1,2]` | 3 |
| `[1,2,3,1,2,3,1,2,3]` | `[1], [2], [3], [1,2,3,1,2,3]` | 4 |

Implementations MUST reproduce these factorizations exactly.

**Reference:** Lempel & Ziv (1976), *IEEE Trans. IT* 22(1):75-81.

---

### 13.3 Permutation Entropy

**Formula:**

```
PE = -Σ_{π} p(π) · log₂(p(π)) / log₂(d!)
```

**Precondition:** `len(sequence) >= d * tau`
**Violation:** `raise ValueError`

**Tie breaking:** Stable sort by time index.

**Reference:** Bandt & Pompe (2002), *Physica D* 172:127-134.

---

### 13.4 Abstention Policy

| Threshold | Value | Semantic |
|-----------|-------|----------|
| `ε_accept` | 0.85 | High distributional variability |
| `ε_reject` | 0.15 | Low distributional variability |

**Zones (open interval for ABSTAIN — clarified in v2.7 per DeepSeek #2):**

```
score <= 0.15        → LOW_VARIABILITY
score >= 0.85        → HIGH_VARIABILITY
0.15 < score < 0.85  → ABSTAIN    (open interval — endpoints excluded)
```

The abstention zone is an **open** interval `(0.15, 0.85)`: scores of exactly 0.15 or 0.85 are deliberately assigned to LOW/HIGH respectively, not ABSTAIN. This preserves mutual exclusivity of the three zones. The closed-form `gte/lte` in vector `abstention_boundary_middle.expected` is a **range assertion over the computed entropy value** for that specific input, not a redefinition of the zone.

**Calibration status (NEW in v2.5):** `heuristic_pending_empirical_validation`

The 0.15 / 0.85 thresholds are placeholders chosen for symmetry around the unit interval. They are **NOT empirically calibrated against forensic datasets**. Mathematical protocol freeze does NOT freeze these thresholds.

**Calibration freeze requirement:** Before P2 final freeze, thresholds MUST be validated against at least one published forensic corpus with documented sensitivity/specificity reporting. Until then, thresholds are advisory and any production deployment MUST document threshold provenance.

---

## 14. Known Adversarial Gaps (honest future-work — NEW in v2.5, IDs added in v2.6)

The following adversarial scenarios are **NOT** yet covered by canonical vectors. Each gap has a stable short ID (`GAP-NN`) for issue tracking. Documented as future-work to prevent overclaiming P2 robustness:

| ID | Name | Description |
|----|------|-------------|
| **GAP-01** | entropy_inflation_attack | Low-rate uniform noise pushes metrics toward high-variability zone without altering semantic content. |
| **GAP-02** | symbolic_explosion_attack | Sub-ULP float perturbations exploit exact-equality symbolization to artificially expand symbol space and inflate Shannon entropy. |
| **GAP-03** | calibration_drift | Threshold semantics may degrade as upstream data distributions shift. No drift-detection or recalibration cadence specified. |
| **GAP-04** | backend_divergence_under_stress | Parallel reductions under high core count may show post-quantization equivalence empirically but with margins that erode under adversarial input shapes. |
| **GAP-05** | heterogeneous_hardware_reproducibility | Cross-vendor GPU determinism (NVIDIA vs AMD vs Apple Silicon) not empirically validated for all P2 vectors at reference level. |
| **GAP-06** | false_structure_induction | Pathological inputs inducing coincidentally low LZ complexity or low PE without genuine structural regularity (e.g., aliasing artifacts). |
| **GAP-07** | dataset_leakage_in_calibration | Overlap between calibration corpus and deployment data biases sensitivity/specificity optimistically. |
| **GAP-08** | upstream_discretization_attack | Adversary controls the discretization step (out of P2 scope) to push downstream outputs into desired zones. P2 cannot defend without chain-of-custody attestation of the discretizer. |
| **GAP-09** | tie_break_exploitation | PE's stable-sort tie-break is deterministic but adversarially exploitable via inputs with many equal values forcing specific permutation distributions. |
| **GAP-10** | lz_period_aliasing | LZ76 normalization `c(n) / (n / log₂(n))` is asymptotic. For short sequences with periods near `sqrt(n)`, normalized scores may misrepresent true compressibility. |

**ID scheme:** Append-only. Once assigned, a `GAP-NN` ID is never reused or renumbered. Issues SHOULD reference gaps by ID.

**Future-work commitment:** Each gap is a candidate target for the P2-to-final-freeze validation campaign. P3 may introduce dedicated vectors for gaps that mature into stable test scenarios.

---

## 15. Hash Validation

Validators MUST compute SHA-256 of `canonical_vectors_p2.json` at runtime and compare against `canonical_vectors_p2.sha256`.

**Hash invalidation conditions:**

- Any whitespace modification
- Any key reordering
- Any float representation change
- Any comment/note modification
- Any `schema_version` change

---

## 16. What P2 Guarantees vs Does NOT Guarantee (unified table — NEW in v2.6)

This table is the single normative summary of P2's scope boundaries. It also appears in `docs/official_builds.md` for consistency.

| ✅ P2 Guarantees | ❌ P2 Does NOT Guarantee |
|------------------|--------------------------|
| Deterministic quantized equivalence across backends | Absolute accuracy — reproducibility ≠ truth |
| Contextual entropy (Markov memory) | Behavioral classification (humans vs bots, real vs synthetic) |
| Complexity semantics (LZ compressibility) | Authorship attribution or intent inference |
| Ordinal invariance (PE under monotonic transformations) | Legal admissibility certification |
| Adversarial rejection (denormals, NaN, Inf, overflow) | Complete adversarial robustness — see §14 GAP-01..GAP-10 |
| Abstention honesty (formalized as protocol property) | Calibrated decision thresholds — see §13.4 `calibration_status` |
| Symbolization honesty (exact float64 equality) | Upstream discretization correctness — delegated, see §4 |
| Pair encoding safety (collision-free bijective map) | Forensic conclusions about specific evidence |
| Cross-backend equivalence post-quantization | Score fusion, composition, uncertainty propagation — see §20 P3 future work |
| Compliance transparency (strict / reference / accelerated) | Ontological claims about "humanity" or "authenticity" |

---

## 17. Canonical Vectors

See: `canonical_vectors_p2.json` (accompanied by `canonical_vectors_p2.sha256`)

A build is **"VIGÍA-compatible P2"** iff:

1. Reproduces all **P1** canonical vectors.
2. Reproduces all **P2** canonical vectors after canonical quantization.
3. Respects abstention thresholds.
4. Validator asserts `validation_rules.vector_count == 22`.

### Vector Categories (22 total)

| Category | Count | Purpose |
|----------|-------|---------|
| Markov order-k | 4 | Memory + precondition |
| Lempel-Ziv | 4 | Complexity + raw factorization |
| Permutation entropy | 5 | Ordinal invariance + tie-breaking |
| Abstention | 3 | Threshold boundaries |
| Adversarial | 5 | Denormals, NaN+Inf, stability, fuzzing, symbol stability |
| Entropy rate | 1 | Pair entropy verification |

---

## 18. Compatibility Claims

| Claim | Valid? | Prerequisites |
|-------|--------|---------------|
| "Built on VIGÍA" | Yes | None |
| "Fork of VIGÍA" | Yes | None |
| "VIGÍA-compatible P1" | Yes | P1 vectors |
| **"VIGÍA-compatible P2"** | **Only if passes** | P1 + P2 + abstention + no prohibited interpretive phrasings |
| "VIGÍA-compatible P2 (strict)" | Yes | Strict compliance |
| "VIGÍA-accelerated" | Yes | Accelerated compliance |
| "Official VIGÍA runtime" | Requires signed manifest | P1 + P2 + governance |
| "Daubert-ready" | **Invalid** | Requires independent audit |
| "SANS-approved" | **Invalid** | SANS certifies people |
| Any phrase from §3 prohibited list | **Invalid + revokes prior claim** | See §3 revocation_clause |

---

## 19. Freeze Policy

P2 is **draft** until explicitly frozen.

**Target freeze date:** 2026-06-15 (advisory; aligned with SANS FIND EVIL Hackathon 2026 submission)

**Freeze criteria:**

1. All vectors verified across 3+ backends
2. No open mathematical ambiguities
3. Abstention thresholds validated on real datasets
4. Chain-of-custody tested in mock trial
5. Compliance levels tested
6. Discretization policy documented in at least one reference implementation
7. `known_adversarial_gaps` reviewed and either covered by vectors or formally deferred to P3

Once frozen: immutable like P1.

---

## 20. P3 Future Work (scope deliberately excluded from P2 — NEW in v2.6)

P2 is intentionally minimal. The following capabilities are explicitly **NOT** in P2 scope and are candidates for P3. Listed here so freeze decisions are made with explicit awareness of what P2 is NOT trying to be:

| ID | Name | Description |
|----|------|-------------|
| **P3-01** | formal_upstream_discretization_standard | Standardized discretization functions with reproducibility contracts. Today P2 delegates discretization to the implementer. The VIGÍA AI Collective endorses ChatGPT's diagnosis that discretization is plausibly the "real P3" rather than a side concern: two pipelines applying different discretizers to the same physical phenomenon produce "reproducible mathematical truths over different representations" — a known unresolved tension. |
| **P3-02** | score_fusion_and_weighting | P2 produces individual distributional measurements. It does NOT specify how to combine entropy + LZ + Markov + PE into a single decision or evidence object. Fusion strategies (weighted sums, Bayesian aggregation, Dempster-Shafer combination) are out of P2 scope. |
| **P3-03** | uncertainty_propagation | P2 reports point estimates. Confidence intervals, credible intervals, bootstrap variance estimates, and uncertainty propagation through fusion are P3 candidates. |
| **P3-04** | calibration_protocol | A formal protocol for empirical calibration of abstention thresholds against forensic corpora, including sensitivity/specificity reporting, calibration drift monitoring, and recalibration cadence. Currently flagged in §13.4 `calibration_status`. |
| **P3-05** | peircean_inference_closure | Today P2 measures. It does not yet reason. Closing the Peircean loop (abduction → deduction → induction over P2 measurements) is the candidate semantic layer above P2. |

**Rationale:** P2 is deliberately scoped as a mathematical reproducibility contract. Composition, fusion, uncertainty, and inference belong at a higher layer. Keeping P2 minimal is what makes it freezable; the cost — explicitly acknowledged — is that **P2 alone is not a forensic system, it is forensic infrastructure**.

---

## 21. Governance

| Role | Entity |
|------|--------|
| Maintainers | VIGÍA AI Collective (Anna Tchijova, Kimi, Claude, Gemini, DeepSeek, ChatGPT, Qwen, Grok) |
| Review | Multi-AI consensus + community audit |
| Updates | Schema version bump + new protocol identifier |
| Signatures | Forensically signed commits |

---

## 22. References

- P1: `docs/protocols/P1/SPEC.md`
- Lempel & Ziv (1976): *IEEE Trans. IT* 22(1):75-81
- Bandt & Pompe (2002): *Physica D* 172:127-134
- Cover & Thomas: *Elements of Information Theory*, Ch. 4

---

## 23. Changelog

- **v2.8 (this version)** — 9th audit pass (Kimi + ChatGPT + Grok + Claude + DeepSeek round 2)
  - **REFINEMENT (DeepSeek round-2 #5):** `prng_binding` now tiered by compliance level. **Strict** retains bit-identity requirement with NumPy reference stream (acknowledged as highly demanding due to NumPy-specific packing, endianness, and rejection-sampling logic). **Reference** relaxes to statistical equivalence with documented seeding. **Accelerated** permits any deterministic seeded PRNG. Rationale: bit-identity across language ecosystems is generally not achievable for PCG64 even for mathematically correct implementations; demanding it uniformly would exclude correct work.
  - **EMPIRICAL VERIFICATION (DeepSeek round-2 #3):** `pe_large_tie_break_complex` computed independently. Sequence `[1,1,2,2,3,3]×50` (n=300), d=3, tau=1 yields 3 distinct ordinal patterns under stable-sort: `(0,1,2)×200, (1,2,0)×49, (2,0,1)×49` over 298 windows. Raw PE = 0.48070929113822736; canonical (Decimal HALF_EVEN, 6 places) = 0.480709. Exact match with vector's `expected`. Vector confirmed mathematically sound.
  - **CLARIFICATION (DeepSeek round-2 #2):** `near_equal_symbol_stability` note expanded with empirically-verified hex representations: `1.0 → 0x1.0000000000000p+0`, `1.000000000000001 → 0x1.0000000000005p+0`, `1.000000000000002 → 0x1.0000000000009p+0`. (DeepSeek's round-2 message proposed `0x1.0000000000006p+0` for the third value, which is incorrect; the verified hex is used in the JSON.)
  - **CLARIFICATION (DeepSeek round-2 #6):** `special_float_handling.native_value_rejection_clause` adds the largest-denormal example `2.2250738585072009e-308` (hex `0x0.fffffffffffffp-1022`) and explicit note that the threshold `2^-1022 ≈ 2.2250738585072014e-308` is the smallest positive NORMAL float64.
  - **DOC FIX (DeepSeek round-2 #4):** CHECKLIST step 3 clarifies that repository canonical filename is `docs/official_builds.md` (single global governance doc), while output staging may use `_p2` suffix purely for grouping.
  - **NO-OP (DeepSeek round-2 #1):** `vector_count` = 22 reverified; no change.
- **v2.7** — 8th audit pass (Kimi + ChatGPT + Grok + Claude + DeepSeek round 1)
  - **BUG FIX (DeepSeek #1):** `pe_tie_break_stability` sequence corrected.
  - **NORMATIVE FIX (DeepSeek #3):** `reference_runtime.prng_binding` now pins `PCG64` to `numpy.random.Generator(numpy.random.PCG64(seed))`. Bare "PCG64" was previously ambiguous (NumPy / O'Neill / Boost variants differ). Non-NumPy implementations MUST match the NumPy reference stream bit-identically or be disqualified from strict/reference compliance.
  - **CLARIFICATION (DeepSeek #2):** `abstention_zone` open-interval semantics made explicit via new `range_notation` and `zone_assignment_rule` fields in JSON; SPEC §13.4 zones block clarified accordingly. Endpoints 0.15 and 0.85 are deliberately assigned to LOW/HIGH respectively, NOT ABSTAIN. The `gte/lte` in `abstention_boundary_middle.expected` is a per-vector range assertion over the computed entropy, not a redefinition of the zone.
  - **CLARIFICATION (DeepSeek #6):** `special_float_handling.native_value_rejection_clause` added. Native denormal floats (`5e-324`, `-5e-324`, any value with `0 < abs(x) < 2^-1022`) MUST raise `ValueError`, not only the synthetic protocol-layer denormal tokens.
  - **SELF-CONTAINMENT (DeepSeek #4):** New `shannon_entropy_definition`, `entropy_normalized_definition`, and `entropy_rate_definition` blocks inline the P1-inherited definitions for reviewer convenience. P1 remains authoritative; these are mirror definitions marked `p2_inlined_for_review: true`. SPEC §7 added.
  - **REJECTED (DeepSeek #5):** Generator-based representation for `lz_periodic_low` declined. Adding a `sequence_generator` input format is feature creep, not a fix; the explicit 900-element array remains canonical and is fully documented in the vector's `description` and `note`.
  - SPEC § renumbering: §6a (PRNG Binding) and §7 (Self-Contained Definitions) inserted; subsequent sections shifted by 2.
- **v2.6** — 7th audit pass (Kimi + ChatGPT + Grok + Claude)
  - **BUG FIX (Kimi):** `pair_fuzz_max_uint32` token corrected from `18446744065119617025` to `18446744073709551615` (= 2⁶⁴-1). The previous value was arithmetically inconsistent with `(2³²-1 << 32) | (2³²-1)`.
  - **Doc fix (Kimi):** `lz_periodic_low` description now states explicit length n=900 (= 300 repetitions of [1,2,3]).
  - Bug-NOT-confirmed (Kimi): `near_equal_symbol_stability` uses `1.000000000000001` which IS representable as distinct from `1.0` in float64 (hex 0x1.0000000000005p+0). Vector retained unchanged.
  - Added §3 revocation_clause (Grok): prohibited interpretive phrasings revoke P2-compatible claims.
  - Added §3a `interpretation_safeguards` with REINT-01..REINT-04 counterexamples (responds to ChatGPT's "entropy name is semantically dangerous" concern with the most honest defense available at protocol level: documented counterexamples).
  - Added §14 GAP-NN stable IDs (Grok) for issue tracking.
  - Added §16 unified Guarantees / Does NOT Guarantee table (Grok).
  - Added §20 P3 future work with P3-01..P3-05 (responds to ChatGPT's "missing composition theory" and "discretization is real P3" diagnoses; both explicitly endorsed by collective).
  - Added `normative_banner` at top of JSON.
  - Strengthened `discretization_policy.future_work` with explicit collective endorsement of ChatGPT's "discretization = real P3" position.
- **v2.5** — 6th audit pass (Kimi + ChatGPT + Grok + Claude)
  - terminology_warnings (interpretive overreach hardening)
  - discretization_policy (upstream gap acknowledgment)
  - calibration_status for abstention thresholds
  - known_adversarial_gaps (10 documented future-work items)
  - target_freeze_date 2026-06-15
  - validation_rules.vector_count: 22
  - pseudocode_worked_examples_ref in LZ definition
  - Full English translation pass
  - Grok added to AI Collective
- **v2.4** — Grok + ChatGPT 5th-round fixes (annotations vs non_normative, LZ O(n²) note, accelerated warning, new vectors, hash validator, non_goals)
- **v2.3** — 4th round (Decimal.quantize() HALF_EVEN, LZ raw factors, pair encoding, symbolization, compliance levels)
- **v2.2** — 3rd round (LZ complexity honesty, float_serialization split, PE tie-break, Markov invalid)
- **v2.1** — 2nd round (LZ pseudocode, PE precondition, Markov smoothing)
- **v2.0-draft** — initial P2 protocol

---

*"P1 makes measurements comparable. P2 makes measurements contextual. P2 measures; P3 will reason."*
