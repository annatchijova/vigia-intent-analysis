# VIGÍA — Protocol P2 v2.8: Implementation Checklist
# ══════════════════════════════════════════════════════════════════════════
# Generated 2026-05-16 for Anna Tchijova
# SANS FIND EVIL Hackathon 2026 — VIGÍA AI Collective
#   (Anna Tchijova, Kimi, Claude, Gemini, DeepSeek, ChatGPT, Qwen, Grok)
#
# P2 v2.8: 9 audit rounds (Kimi + ChatGPT + Grok + Claude + DeepSeek round 2)
#
#   REFINEMENT (DeepSeek round-2 #5): PRNG binding tiered by compliance level
#     - strict:      bit-identity with NumPy required
#     - reference:   statistical equivalence with documented seeding
#     - accelerated: any seeded deterministic PRNG
#
#   EMPIRICAL VERIFICATION (DeepSeek round-2 #3): pe_large_tie_break_complex
#     - raw PE = 0.48070929113822736
#     - quantized = 0.480709 (exact match with vector)
#     - patterns: (0,1,2)×200, (1,2,0)×49, (2,0,1)×49 over 298 windows
#     - vector confirmed mathematically sound
#
#   CLARIFICATIONS (DeepSeek round-2 #2, #4, #6):
#     - near_equal hex representations expanded (with empirical verification —
#       DeepSeek's proposed 0x1.0000000000006p+0 was incorrect; actual is
#       0x1.0000000000009p+0)
#     - special_float_handling.native_value_rejection_clause adds largest-
#       denormal example (2.2250738585072009e-308 = hex 0x0.fffffffffffffp-1022)
#     - CHECKLIST step 3 clarifies _p2 suffix is staging-only convention
#
#   NO-OP (DeepSeek round-2 #1): vector_count = 22 reverified
#
#   --- v2.7 inheritance (prior round, kept for traceability) ---
#   BUG FIX (DeepSeek #1): pe_tie_break_stability seq → [1,1,1,2,2,2]
#   NORMATIVE FIX (DeepSeek #3): PRNG binding pinned to NumPy PCG64
#   CLARIFICATIONS (DeepSeek #2, #6): abstention open interval, native denormal
#   SELF-CONTAINMENT (DeepSeek #4): Shannon/entropy_rate definitions inlined
#   REJECTED (DeepSeek #5): generator-based lz_periodic_low (feature creep)
# ══════════════════════════════════════════════════════════════════════════

## Repo structure

```
docs/
├── official_builds.md          # P1 + P2 governance (v2.4)
└── protocols/
    ├── P1/
    │   ├── SPEC.md              # FROZEN
    │   ├── canonical_vectors.json
    │   └── canonical_vectors.sha256
    └── P2/
        ├── SPEC.md              # v2.8 DRAFT
        ├── canonical_vectors_p2.json
        └── canonical_vectors_p2.sha256
```

## P2 v2.8 copy checklist

### Step 1: Create structure
- [ ] `mkdir -p docs/protocols/P2`

### Step 2: Copy P2 files
- [ ] Copy `SPEC.md` → `docs/protocols/P2/SPEC.md`
- [ ] Copy `canonical_vectors_p2.json` → `docs/protocols/P2/`
- [ ] Copy `canonical_vectors_p2.sha256` → `docs/protocols/P2/`

### Step 3: Update governance doc
- [ ] Copy `official_builds.md` (or `official_builds_p2.md` if downloaded with the P2-stage suffix) → `docs/official_builds.md`
- [ ] **Note:** The repository canonical filename is `docs/official_builds.md` (single global governance doc covering P1+P2+future). When this doc is staged alongside P2 deliverables, the output filename may carry a `_p2` suffix purely for grouping; rename to `official_builds.md` when placing into the repo.

### Step 4: Technical verification
- [ ] JSON valid: `python3 -c "import json; json.load(open('docs/protocols/P2/canonical_vectors_p2.json'))"`
- [ ] SHA-256: `sha256sum docs/protocols/P2/canonical_vectors_p2.json` vs `.sha256`
- [ ] **Runtime hash validator**: `python3 -c "import hashlib; h=hashlib.sha256(open('docs/protocols/P2/canonical_vectors_p2.json','rb').read()).hexdigest(); print(h)"` vs `.sha256` contents
- [ ] Expected SHA-256: `f7276a524a46149a2811d52f9e5072d2a281df227f9d46d084a651d6420cf4ce`
- [ ] P1 still passes

### Step 5: Git
- [ ] `git add docs/protocols/P2/ docs/official_builds.md`
- [ ] `git status`
- [ ] Commit: `git commit -m "docs: P2 v2.8 — 9th audit pass (Kimi+ChatGPT+Grok+Claude+DeepSeek round 2, 2026-05-16); PRNG binding tiered by compliance level; pe_large_tie_break_complex empirically verified (0.480709); near_equal hex notes expanded; largest-denormal example added"`

### Step 6: P2 semantic validation (22 vectors)

#### Markov (4 vectors)
- [ ] `markov_k0_shannon` (k=0 = Shannon, 1.584963)
- [ ] `markov_k1_deterministic` (k=1 deterministic = 0.0)
- [ ] `markov_k1_random` (k=1 random in [1.9, 2.0])
- [ ] `markov_invalid_k` (precondition violation → ValueError)

#### Lempel-Ziv (4 vectors)
- [ ] `lz_periodic_low` (periodic n=900 → [0.0, 0.15])
- [ ] `lz_random_high` (random → [0.85, 1.0])
- [ ] `lz_raw_factorization_verification` (raw factors for `[1,2,1,2,1,2]` → 3 factors)
- [ ] `lz_raw_factorization_periodic` (raw factors for period-3 → 4 factors)
- [ ] Algorithm = exact LZ76 (O(n²) worst-case naive)

#### Permutation Entropy (5 vectors)
- [ ] `pe_periodic_sin` (sinusoid in [0.30, 0.60])
- [ ] `pe_monotonic_zero` (monotonic = 0.0)
- [ ] `pe_random_high` (random >= 0.95)
- [ ] **`pe_tie_break_stability`** ([1,1,1,2,2,2] → PE = 0.0) ← v2.7 BUG FIX
- [ ] `pe_large_tie_break_complex` (n=300 → PE = 0.480709)
- [ ] Precondition `n >= d*tau` → ValueError if not

#### Abstention (3 vectors)
- [ ] `abstention_boundary_middle` (0.47 → ABSTAIN, in open interval (0.15, 0.85))
- [ ] `abstention_boundary_low` (0.0 → LOW_VARIABILITY)
- [ ] `abstention_boundary_high` (1.0 → HIGH_VARIABILITY)

#### Adversarial (5 vectors)
- [ ] `reject_denormal` → ValueError (also any native 5e-324, -5e-324)
- [ ] `reject_nan_inf_combined` → ValueError
- [ ] `large_scale_stability` (in [19.0, 20.0])
- [ ] `pair_fuzz_max_uint32` (token = `18446744073709551615` = 2⁶⁴-1)
- [ ] `near_equal_symbol_stability` (H = log2(3))

#### Entropy Rate (1 vector)
- [ ] `entropy_rate_pairs_intermediate` (normalized = 1.0)

### Step 7: Compliance level validation
- [ ] **Strict**: Python pure, sequential, all 22 vectors, NumPy PCG64 for PRNG vectors
- [ ] **Reference**: NumPy/CuPy, parallel OK, float64, all 22 vectors
- [ ] **Accelerated**: document deviations, NO "P2-compatible" claim

### Step 8: Runtime hash validation
- [ ] Validator computes SHA-256 of JSON at runtime
- [ ] Compares against `.sha256`
- [ ] Rejects on mismatch
- [ ] Validator asserts `validation_rules.vector_count == 22`

### Step 9: v2.8-specific governance checks
- [ ] `normative_banner` is present near the top of the JSON
- [ ] `reference_runtime.prng_binding` references `numpy.random.Generator(numpy.random.PCG64(seed))` — implementations MUST match this stream bit-identically
- [ ] `shannon_entropy_definition`, `entropy_normalized_definition`, `entropy_rate_definition` blocks present and marked `p2_inlined_for_review: true`
- [ ] `abstention_policy_definition.abstention_zone.range_notation` explicitly states open-interval semantics
- [ ] `special_float_handling.native_value_rejection_clause` documents that `5e-324`, `-5e-324`, and any native float64 with `0 < abs(x) < 2^-1022` MUST raise `ValueError`
- [ ] `terminology_warnings.prohibited_interpretive_phrasings` enforced in implementation docs, UI labels, CLI output, and API field names
- [ ] **Revocation clause acknowledged**: any prohibited phrasing automatically forfeits the P2-compatible claim, retroactive to prior claims
- [ ] `interpretation_safeguards`: at least one counterexample from each REINT-01..REINT-04 displayed in user-facing material that exposes P2 metric values
- [ ] `discretization_policy` documented in reference implementation when continuous data is processed
- [ ] `abstention_policy_definition.calibration_status` (= `heuristic_pending_empirical_validation`) displayed in any UI/CLI exposing thresholds
- [ ] `known_adversarial_gaps` GAP-01..GAP-10 linked from README; issues reference gaps by ID
- [ ] `governance.future_work_p3` (P3-01..P3-05) acknowledged in roadmap docs
- [ ] `target_freeze_date` (2026-06-15) visible in repo top-level README

## P2 Changelog

- **v2.8 (this version)** — 9th audit pass (Kimi + ChatGPT + Grok + Claude + DeepSeek round 2)
  - **REFINEMENT (DeepSeek round-2 #5)**: `prng_binding` tiered by compliance level. Strict requires NumPy bit-identity; reference relaxes to statistical equivalence; accelerated accepts any seeded deterministic PRNG.
  - **EMPIRICAL VERIFICATION (DeepSeek round-2 #3)**: `pe_large_tie_break_complex` computed independently. Raw PE = 0.48070929113822736; canonical = 0.480709. Patterns (0,1,2)×200, (1,2,0)×49, (2,0,1)×49 over 298 windows. Vector mathematically sound.
  - **CLARIFICATION (DeepSeek round-2 #2)**: `near_equal_symbol_stability` note expanded with empirically-verified hex representations.
  - **CLARIFICATION (DeepSeek round-2 #6)**: `special_float_handling.native_value_rejection_clause` adds largest-denormal example 2.2250738585072009e-308.
  - **DOC FIX (DeepSeek round-2 #4)**: CHECKLIST step 3 clarifies `_p2` suffix is output-staging convention only.
  - **NO-OP (DeepSeek round-2 #1)**: vector_count = 22 reverified.

- **v2.7** — 8th audit pass (Kimi + ChatGPT + Grok + Claude + DeepSeek round 1)
  - **BUG FIX (DeepSeek #1)**: `pe_tie_break_stability` sequence corrected from `[1,1,2,2,1,2]` (PE ≈ 0.580279) to `[1,1,1,2,2,2]` (PE = 0.0). Old vector was mathematically inconsistent with its claimed expected value.
  - **NORMATIVE FIX (DeepSeek #3)**: `reference_runtime.prng_binding` pins PCG64 to `numpy.random.Generator(numpy.random.PCG64(seed))`. Bare "PCG64" was cross-impl ambiguous.
  - **CLARIFICATION (DeepSeek #2)**: Abstention zone open-interval `(0.15, 0.85)` semantics made explicit. Endpoints belong to LOW/HIGH, not ABSTAIN.
  - **CLARIFICATION (DeepSeek #6)**: Native denormal rejection clause added. `5e-324`, `-5e-324`, any native `0 < abs(x) < 2^-1022` MUST raise `ValueError`.
  - **SELF-CONTAINMENT (DeepSeek #4)**: `shannon_entropy_definition`, `entropy_normalized_definition`, `entropy_rate_definition` blocks inlined from P1 for reviewer convenience.
  - **REJECTED (DeepSeek #5)**: Generator-based `lz_periodic_low` representation declined. Feature creep, not fix.

- **v2.6** — 7th audit pass (Kimi + ChatGPT + Grok + Claude)
  - **BUG FIX (Kimi)**: `pair_fuzz_max_uint32` token corrected to `18446744073709551615` (= 2⁶⁴-1)
  - normative_banner at top of JSON (Grok)
  - revocation_clause in terminology_warnings (Grok)
  - interpretation_safeguards block with REINT-01..04 counterexamples (Claude → ChatGPT)
  - GAP-NN stable IDs in known_adversarial_gaps (Grok)
  - governance.future_work_p3 with P3-01..05 (Claude → ChatGPT)
  - unified Guarantees vs Does NOT Guarantee table in SPEC §16 and official_builds §6a (Grok)
  - Closing slogan changed from "P1 makes truth comparable" to "P1 makes measurements comparable" (ChatGPT)

- **v2.5** — 6th audit pass
  - terminology_warnings (interpretive overreach hardening)
  - discretization_policy (upstream gap acknowledgment)
  - calibration_status: heuristic_pending_empirical_validation
  - known_adversarial_gaps (10 documented future-work items)
  - target_freeze_date: 2026-06-15
  - validation_rules.vector_count: 22
  - Full English translation pass
  - Grok added to AI Collective

- **v2.4 FINAL** — Grok + ChatGPT 5th-round fixes
- **v2.3** — 4th round (Decimal.quantize() HALF_EVEN, LZ raw factors)
- **v2.2** — 3rd round (LZ honesty, float_serialization split, PE tie-break)
- **v2.1** — 2nd round (LZ pseudocode, PE precondition, Markov smoothing)
- **v2.0-draft** — initial P2 protocol

## Key implementation notes

### Canonicalization v2.4+
```python
from decimal import Decimal, ROUND_HALF_EVEN

def canonical_quantize(value):
    d = Decimal(str(value))
    return float(d.quantize(Decimal('1.000000'), rounding=ROUND_HALF_EVEN))
```

### Runtime Hash Validator
```python
import hashlib

with open('canonical_vectors_p2.json', 'rb') as f:
    computed_hash = hashlib.sha256(f.read()).hexdigest()

with open('canonical_vectors_p2.sha256') as f:
    expected_hash = f.read().split()[0]

assert computed_hash == expected_hash, "Hash mismatch — possible tampering"
```

### PRNG binding (v2.7 normative)
```python
import numpy as np
# For any vector specifying "type": "prng", "algorithm": "PCG64", "seed": N
rng = np.random.Generator(np.random.PCG64(seed))
samples = rng.integers(low, high, size=n, endpoint=False)
# Non-NumPy implementations MUST produce a bit-identical stream
# for the seeds and ranges in PRNG-typed vectors.
```

### pe_tie_break_stability v2.7 fix
```python
# Old (v2.6 and earlier — BUG):
#   sequence = [1,1,2,2,1,2], d=3, tau=1 → PE actually ≈ 0.580279
#   (4 windows produce 3 distinct ordinal patterns)
#
# New (v2.7):
seq = [1, 1, 1, 2, 2, 2]
d, tau = 3, 1
# 4 windows: (1,1,1), (1,1,2), (1,2,2), (2,2,2)
# All map to pattern (0,1,2) under stable sort → PE = 0.0
```

### Abstention zone (v2.7 clarification)
```python
# Open interval semantics:
def classify(score, eps_reject=0.15, eps_accept=0.85):
    if score <= eps_reject:
        return "LOW_VARIABILITY"      # 0.15 belongs HERE
    elif score >= eps_accept:
        return "HIGH_VARIABILITY"     # 0.85 belongs HERE
    else:
        return "ABSTAIN"              # strictly between, endpoints excluded
```

### Native denormal rejection (v2.7 clarification)
```python
import math

def reject_special_floats(value):
    if math.isnan(value):
        raise ValueError("NaN rejected")
    if math.isinf(value):
        raise ValueError("Inf rejected")
    if value != 0 and abs(value) < 2**-1022:
        raise ValueError("denormal/subnormal rejected")
    # Examples that MUST be rejected:
    # 5e-324, -5e-324, 2.2250738585072009e-308, ...
```

### Symbolization
```python
assert (+0.0 == -0.0)              # IEEE-754: same symbol
assert 1.0 != 1.0000000001         # Different symbols
assert 1.0 != 1.000000000000001    # hex 0x1.0000000000005p+0
```

### Accelerated Compliance
```python
# PROHIBITED:
# claim = "VIGÍA-compatible P2"  # ❌ without passing all 22 vectors

# PERMITTED:
# claim = "VIGÍA-accelerated"     # ✅ with deviation documentation
# claim = "P2-subset"             # ✅ specifying which vectors pass
# claim = "P2-inspired"           # ✅ no compatibility implication
```

### Terminology guardrails
```python
# PROHIBITED labels — auto-revoke P2-compatible claim:
prohibited = [
    "AI detector", "bot detector", "human-vs-machine classifier",
    "authenticity score", "deception score", "intent score",
    "humanity index"
]

# PERMITTED labels:
permitted = [
    "distributional variability measure",
    "compressibility estimate",
    "ordinal complexity estimate",
    "conditional entropy estimate"
]
```

### Non-Goals (legal protection)
P2 does NOT guarantee:
- Semantic interpretation of evidence
- Authorship attribution
- Truth inference
- Intent inference
- Psychological profiling
- Legal admissibility certification
- Absolute correctness
- Behavioral classification of humans vs bots
- Ontological claims about "humanity"

---

*"P1 makes measurements comparable. P2 makes measurements contextual. P2 measures; P3 will reason."*

— VIGÍA AI Collective, 2026-05-16 💜💛
