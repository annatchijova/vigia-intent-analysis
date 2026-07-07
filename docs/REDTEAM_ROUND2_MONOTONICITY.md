# Security Audit — VIGÍA Forensic Intent Scorer

## Red Team Round 2 — Monotonicity Invariants

**Date:** 2026-07-07  **Method:** Abductive Engineering (A–D–I) + Red-Team Auditing (epistemic ladder)
**Scope:** `vigia_scorer._vigia_score` — the deterministic scoring core. Property-based, black-box. **Read-only audit — no product code was modified.**
**Base:** `claude/monotonicity-invariants-redteam-sc0x9r` @ `e78d94b`
**Runtime:** CPython 3.11.15
**Reproducible evidence:** `scripts/redteam_round2_monotonicity.py`
(`PYTHONPATH=$(pwd) python3 scripts/redteam_round2_monotonicity.py`)

---

## Threat model

This is **not** a code-injection or crypto-seal audit. The "attacker" here is
**whoever assembles the artifact set** fed to the scorer — a careless examiner,
an automated ingestion pipeline, or an adversary who can add (not forge) evidence.

- Attacker **CAN**: add artifacts to the case, choose their `evidence_type`,
  `raw_score`, `prior_trust`, and `semantic_role=incriminatory` (the default).
- Attacker **CANNOT**: modify `vigia_scorer.py`, break the seal, forge HMAC,
  or alter an already-sealed bundle. Every input used below is a *legitimate*,
  schema-valid artifact — nothing is malformed.
- Trust boundary crossed: the **composition** of per-artifact scoring into a
  case-level verdict. Each module is individually correct; the aggregate
  violates two properties the system's own philosophy promises.

Both findings are **Round 2 (invariant) fractures**, not local defects.

---

## Epistemic legend

CODE FACT · PLAUSIBLE HYPOTHESIS · **CONFIRMED BY INDUCTION** · FALSIFIED

---

## Executive summary

| ID | Severity | Level | Module | Finding |
|----|----------|-------|--------|---------|
| M2-1 | High | **CONFIRMED BY INDUCTION** | `vigia_scorer.py` L714–738 (correlation decay) | **Positive monotonicity is false.** Adding an incriminating same-class artifact can *lower* `final_score` by up to 0.09 (29/30 matrix cells). |
| M2-2 | High | **CONFIRMED BY INDUCTION** | `vigia_scorer.py` L924–936 (B-068 gate) | **No-dilution is false.** A forensically empty document (`raw_score=0`) of a new class flips SUSPICION → MALICE by crossing the `n_unique_types ≥ 3` gate. |
| M2-3 | Medium | **CONFIRMED BY INDUCTION** | `vigia_scorer.py` L719–737 (`diversity_bonus`/support) | **No-dilution is false at band edges too.** A `raw_score=0` new-type document flips NOISE → UNKNOWN purely via `diversity_bonus`, no gate involved. |

Both invariants the round was chartered to test are **CONFIRMED violated**. A
matched control (adding a *new-type* incriminating artifact) **HOLDS** with 0/30
violations, which isolates the mechanism rather than blaming aggregation in
general.

---

## Invariant 1 — Positive Monotonicity

> Adding an incriminating artifact must never lower `final_score`.
> Matrix swept: `z_score` (0–5, mapped `raw = z/5`) × `prior_trust` (0.0–1.0).

**Surprise / expectation violated.** The scoring philosophy (and CLAUDE.md
Invariant 6, "fabrication artifacts *raise* the score") implies more
incriminating evidence is monotone-nondecreasing in intent score. It is not.

### Rival hypotheses

- **H1 (null):** monotonicity holds universally; aggregation is Noisy-OR, which is monotone.
- **H2 (correlation-decay):** `source_penalty = min(0.5, (count-1)·0.15)` (L726) is applied to **every** artifact sharing an `evidence_type`. Adding a same-type artifact raises the penalty on the *incumbents*; if the newcomer is weaker than they are, the penalty hike on strong evidence outweighs the newcomer's contribution → score drops.
- **H3 (CAIE credibility penalty):** the added artifact induces a `CREDIBILITY_REDUCING` CAIE fracture (`VERDICT_CONFLICT`, `ATTRIBUTION_INCONSISTENCY`) that subtracts `fracture_credibility_penalty` (L812–816).
- **H4 (boundary/cap artifact):** the drop is only rounding noise or the single-artifact 0.65 cap (L883), i.e. not a real monotonicity break.

### Discriminating experiment (economy of research: cheapest first)

Two matched matrix sweeps decide H1 vs H2 in one shot and simultaneously rule
out H4:

- **Control (new type):** baseline `1× file_hash raw=0.6`; add one incriminating
  `memory_process` across the matrix.
  **Prediction (H1):** 0 violations. — a new type triggers no `source_penalty`.
- **Treatment (same type):** baseline `3× cryptographic_hash raw=1.0 prior=1.0`
  (the highest-`adjusted_score` class: weight 0.45, spoofability 0.05); add one
  incriminating `cryptographic_hash` across the matrix.
  **Prediction (H2):** violations concentrated at low `z`/low `prior` (weak
  additions), vanishing only when the newcomer equals the incumbents.

### Induction — observed (before → after)

Control (new type): **0 / 30** cells decreased → monotonicity **HOLDS**.
This falsifies "aggregation is generally non-monotone" and pins the cause to
same-type decay.

Treatment (same type), sign of `after − before`:

```
        prior= 0.0 0.25  0.5 0.75  1.0
  z=0   DOWN  DOWN  DOWN  DOWN  DOWN
  z=1   DOWN  DOWN  DOWN  DOWN  DOWN
  z=2   DOWN  DOWN  DOWN  DOWN  DOWN
  z=3   DOWN  DOWN  DOWN  DOWN  DOWN
  z=4   DOWN  DOWN  DOWN  DOWN  DOWN
  z=5   DOWN  DOWN  DOWN  DOWN   up
```

**29 / 30** cells lower the score. Worst cell: `z=0, prior=0.0` →
`0.6234 → 0.5305` (Δ = **−0.0929**). Only `z=5, prior=1.0` (newcomer identical
to incumbents) does not drop.

Crisp counterexample:

```
BEFORE  3× cryptographic_hash raw=1.0 prior=1.0   score=0.6234  verdict=SUSPICION
ADD     1× cryptographic_hash raw=0.05 prior=0.85  (incriminating, weak)
AFTER                                              score=0.5350  verdict=MALICE
Δ score = −0.0884                                  → VIOLATION
```

**Verdict: H2 CONFIRMED BY INDUCTION. H1, H4 FALSIFIED.** (H3 untested here —
not needed; H2 alone breaks the invariant with no CAIE fracture in play.)

### Causal chain

```
add same-type incriminating artifact
    ↓ source_counts[type]: 3 → 4
source_penalty = min(0.5,(4-1)·0.15) = 0.45   (was 0.30)
    ↓ applied to ALL four artifacts of that type (L723-727)
each incumbent's adjusted_score × (1-0.45) instead of × (1-0.30)
    ↓ Noisy-OR product over smaller terms (L733-734)
composite drops   (0.6322 → 0.5350)
    ↓ final_score = raw_intent × (0.9 + 0.1·support)   (support bump 0.86→1.0 too small to compensate)
final_score drops   (0.6234 → 0.5350)
```

Note the second-order oddity: in the crisp case the score **falls** while the
verdict **rises** to MALICE — the same 4th artifact that guts the score also
trips the `n_artifacts ≥ 4` gate (see M2-2). Score and verdict move in opposite
directions from one identical action.

**Threat-model precondition:** attacker/examiner can append one legitimate,
schema-valid artifact of an already-present class. No forgery, no seal break.

---

## Invariant 2 — No Dilution

> Adding forensically irrelevant evidence (README.txt / photo / manual.pdf,
> `raw_score ≈ 0`) must never change the verdict.

**Surprise / expectation violated.** A zero-signal document is, by construction,
not evidence of intent. It must be inert. It is not: it corroborates.

### Rival hypotheses

- **H1 (null):** irrelevant artifacts (`raw_score ≈ 0`) are inert; verdict unchanged.
- **H2 (B-068 gate, `n_artifacts`/`n_unique_types`):** the MALICE corroboration
  gate (L924–936) counts DEVICE artifacts and unique types **with no reference
  to `raw_score`**. A zero-signal document of a *new* DEVICE class lifts
  `n_unique_types` 2 → 3 → gate opens → MALICE. (This is the "ojo especial" the
  brief flagged.)
- **H3 (`diversity_bonus`/support):** a new-type artifact adds
  `diversity_bonus += 0.05` (L719–720, 737) and raises `support_score`
  (L868–869), nudging `final_score` across a *band edge* (e.g. NOISE→UNKNOWN)
  with no gate involved.
- **H4 (downward dilution via `source_penalty`):** a *same-type* irrelevant
  artifact raises `source_penalty` and *lowers* the score, possibly
  down-grading a real MALICE (dilution in the opposite direction).

### Discriminating experiments

**Exp 2A (targets H2).** Baseline: `malware_infrastructure` + 2× `keylogger_capture`,
all `raw=0.95` → `score=0.342`, gated to **SUSPICION** (`n_arts=3<4`,
`n_types=2<3`). Add `manual.pdf` → `evidence_type="document"` (LEGACY profile,
DEVICE role), `raw_score=0.0`.
**Prediction (H2):** verdict flips SUSPICION → MALICE.

```
BEFORE  3 device artifacts / 2 types    score=0.3420  verdict=SUSPICION
ADD     manual.pdf (document, raw=0.0)   [IRRELEVANT]
AFTER                                    score=0.3633  verdict=MALICE
verdict changed = True                   → VIOLATION
```

**H2 CONFIRMED BY INDUCTION.** The empty document raised `n_unique_types`
2 → 3, opening the gate; `diversity_bonus` even nudged the score *up*
(0.342 → 0.3633), so it comfortably stayed in the MALICE band.

**Exp 2B (targets H4, and separates it from H2).** Baseline: `3× malware_infrastructure
raw=0.97` (1 type), `score=0.2656`, SUSPICION. Add a same-type `raw=0.0` artifact.

```
BEFORE  3× malware_infrastructure         score=0.2656  verdict=SUSPICION
ADD     1× same type, raw=0.0             [IRRELEVANT]
AFTER                                     score=0.2162  verdict=SUSPICION
verdict changed = False                   → HOLDS (verdict), but score fell 0.049
```

Same-type dilution **lowers** the score (H4 mechanism real) but here the
baseline was already below the 0.33 gate, so no verdict flip. H4 is a genuine
score-dilution channel; its verdict impact is regime-dependent.

**Exp 2C / band-edge probe (targets H3).** Two `log_entry raw=0.49` sit at
`score=0.0757` → **NOISE** (`≤ 0.08`). Add one `raw=0.0` `document` (new type).

```
BEFORE  2× log_entry raw=0.49             score=0.0757  verdict=NOISE
ADD     document, raw=0.0                 [IRRELEVANT]
AFTER                                     score=0.0810  verdict=UNKNOWN
verdict changed = True                    → VIOLATION
```

**H3 CONFIRMED BY INDUCTION.** `diversity_bonus` (0.00 → 0.05) plus the
`support_score` bump crossed the UNKNOWN edge (0.08) with zero new signal — a
dilution flip that does *not* need the B-068 gate at all.

**Verdict: H2 and H3 CONFIRMED BY INDUCTION; H4 is a real (regime-dependent)
downward channel; H1 FALSIFIED.**

### Causal chain (H2, the headline)

```
add manual.pdf  (evidence_type="document", raw_score=0)
    ↓ evidence_role("document") = DEVICE   (default; L383-387 caie.py)
    ↓ semantic_role = incriminatory (default) → counts in the gate
_tech_arts unique types: {malware_infrastructure, keylogger_capture} → +document = 3
    ↓ gate test  (L934):  _n_types >= 3   TRUE
verdict = MALICE
    ↑ raw_score never consulted by the gate — an empty file corroborates
```

**Threat-model precondition:** attacker/examiner appends one legitimate,
schema-valid document of a class not already present (or a 4th DEVICE artifact
of any class to hit the `n_arts ≥ 4` arm). `raw_score` may be 0.

---

## Discarded / non-exploitable vectors

| Vector | Result | Why it failed |
|--------|--------|---------------|
| INV-1, add **new-type** incriminating artifact | HOLDS (0/30) | New `evidence_type` → no `source_penalty`; only `diversity_bonus`/Noisy-OR gains. Confirms the break is same-type-specific. |
| INV-2, **same-type** irrelevant artifact crossing `n_arts≥4` (Exp 2B) | No verdict flip | `source_penalty` from the same type sank the score below 0.33 before the gate could matter; here the two effects cancel. (The gate *does* open when the baseline clears 0.33 with margin — see M2-1 crisp case, which flips to MALICE.) |
| INV-1 monotonicity attributed to CAIE credibility penalty (H3) | Not needed | H2 alone breaks the invariant with no CAIE fracture present; CAIE-driven decreases remain a separate, plausible-but-unrun channel. |

---

## Interpretation (bucket: Part 2 of the red-team method)

Both findings are **software-invariant defects**, not threat-model assumptions
or hygiene:

- The inputs are legitimate, schema-valid artifacts an ordinary examiner could
  add. No precondition is "already game over."
- They contradict properties the system's own doctrine asserts (monotone
  accumulation of incriminating evidence; irrelevant evidence being inert).
- The B-068 gate was *designed* to make MALICE harder to reach (the NGDC-003
  fix); M2-2 shows the same gate makes MALICE reachable by **padding** with
  empty documents — the counting is by artifact/type cardinality, never by
  signal magnitude.

The deepest single sentence: **the scorer can reach a verdict its specification
says is impossible** — MALICE corroborated by a blank PDF, and *less* intent
scored from *more* incriminating evidence.

---

## Round 2.1 — Implementation of the fixes (2026-07-07, follow-up session)

M2-1 and M2-2 were implemented in `vigia_scorer.py` on this branch. Protocol:
restore tag `pre-session-20260707-025439`, red tests first
(`tests/test_m2_monotonicity_invariants.py`, 6 red / 1 control green at
`e78d94b`), then the fix, then green suite + corpus comparison.

**M2-2 (no-dilution):** a per-artifact *signal flag*
(`adjusted_score > _M2_MIN_SIGNAL_ADJ`, strict, floor 0.0) now gates every
cardinality channel: `n_artifacts`/`support_score`,
`unique_types`/`diversity_bonus`, the single-artifact 0.65 cap, and the B-068
corroboration gate. A `raw_score=0` document (adjusted = 0) is fully inert.
The floor is measured on **adjusted evidential value**, not raw score —
stricter than the suggested `raw_score > 0` (an artifact with signal but zero
effective trust does not corroborate either) and more Daubert-defensible.

**M2-1 (positive monotonicity):** redundancy decay is now evaluated on the
**best prefix per evidence type**: artifacts of a type are sorted by
`adjusted_score` (descending, stable ties), the legacy count penalty
`min(0.5, (k−1)·0.15)` is evaluated on every top-k prefix, and the prefix with
the highest Noisy-OR group contribution wins; artifacts outside it contribute
0. Adding an artifact only widens the candidate set, so the composite is
monotone non-decreasing by construction; wherever the full set was already
optimal (all regular corpus cases), the result is bit-for-bit identical to
legacy.

**Verification (CPython 3.11.15):**
- `tests/test_m2_monotonicity_invariants.py`: 7/7 green.
- `scripts/redteam_round2_monotonicity.py`: **HOLDS on all experiments**
  (was: 29/30 violations, 2 verdict flips).
- Full suite: 776 passed (21 pre-existing, environment-dependent e2e failures
  present identically at the restore tag).
- Corpus `run_all_agent.py`: baseline **165/199** → **163/199**:
  `VIGIA-MAGNET-2022-WINDOWS` fixed (+1), and exactly 3 regressions —
  `VIGIA-FP-001`, `VIGIA-CAN-029`, `VIGIA-CAN-036`.

### The label conflict (measured impossibility, not an implementation gap)

The 3 regressed labels **encode the defect the invariants forbid**:

- `VIGIA-FP-001` (exp BENIGN) passes only because a `log_entry raw=0.05`
  *dilutes* the strong log's composite 0.083 → 0.0744, under the 0.08 NOISE
  edge. Undiluted, the case scores 0.0804 (UNKNOWN) under any monotone scheme.
- `VIGIA-CAN-029` / `VIGIA-CAN-036` (exp SUSPICION) pass only because a
  near-zero same-type artifact dilutes the composite below the 0.33 MALICE
  threshold; monotone scoring lifts them to 0.34–0.36 and the B-068 gate is
  satisfied by their own 4 signal artifacts.

Two impossibility results, both confirmed by induction on the full corpus:

1. **No signal floor exists** (raw or adjusted) that re-caps CAN-029/036 while
   preserving the canonical MALICE set: the corpus requires corroboration by
   artifacts with adjusted value as low as **0.0017** (25 MALICE cases regress
   at floor 0.015, incl. `VIGIA-CAN-003/006/007/010/011`, `VIGIA-REAL-SRL-*`),
   while excluding CAN-029's diluter requires a floor **> 0.013**. Empty
   interval. (Runs: floor 0.10 → 140/199; floor 0.015 → 142/199.)
2. **Any count-increasing redundancy decay is non-monotone somewhere**, and
   its monotone closure (best prefix) necessarily scores ≥ every sub-multiset
   — which crosses the labelled thresholds of exactly these 3 cases. A decay
   that never increases with count would forfeit the Noisy-OR flood
   protection (P1) entirely.

Therefore `{invariants hold} ∧ {199/199 label-compatible}` is unsatisfiable.
Resolution of the 3 labels is a doctrine decision (relabel vs. document as
known limitation vs. officially scope the invariant); recorded for that
decision, not silently resolved here.

**Doctrine decision (Anna, 2026-07-07): relabel the 3 cases.** If dilution is
a defect, labels that depend on it are too. Applied with a `_label_revision`
note in each JSON (including the shadowing duplicate
`data/cases/VIGIA-FP-001.json`, which the batch runner prefers over
`converted/`): `VIGIA-FP-001` BENIGN → UNKNOWN, `VIGIA-CAN-029` and
`VIGIA-CAN-036` SUSPICION → MALICE. Post-relabel corpus: **166/199 — zero
regressions vs. the 165/199 baseline, +1 (`VIGIA-MAGNET-2022-WINDOWS`)**.

## Recommendations (out of scope of this read-only audit — record only)

1. **B-068 gate should count signal, not cardinality.** Require corroborating
   DEVICE artifacts to clear a minimum `raw_score` (or `adjusted_score`) before
   they increment `n_arts`/`n_types`. A `raw_score=0` artifact must not
   corroborate.
2. **`source_penalty` must not lower the aggregate below its pre-addition value.**
   Options: apply redundancy decay only to the *marginal* (newest) same-type
   artifact rather than retroactively to incumbents; or clamp
   `composite_after ≥ composite_before` for incriminating additions (enforce
   the monotone explicitly).
3. **Property-based regression tests.** Adopt `scripts/redteam_round2_monotonicity.py`
   as a CI gate: for random incriminating additions, assert `score` is
   non-decreasing; for random `raw_score=0` additions, assert `verdict` is
   unchanged.
4. **Document the boundary honestly** in `KNOWN_LIMITATIONS.md` until fixed:
   verdict corroboration is currently cardinality-based and dilution-sensitive.
