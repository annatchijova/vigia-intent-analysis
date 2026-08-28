# DeepSeek audit — 2026-08-09

**Branch:** `claude/toctou-matriz-confianza-xbr9pi`
**Scope:** five findings raised by an external model (DeepSeek) against
`vigia_sift_bridge.py::_quarantine_malformed_evidence` and
`vigia_scorer.py::_vigia_score`, delivered across two review rounds. This is an
audit-verification record, not a claim that every finding below is a newly
discovered defect — three of the five were refuted or already documented, and
the scorer itself was left unmodified throughout, per its own delicacy.

## Method

Applied `audit-before-patch`: every finding was checked against the live file
before any code changed, not against the auditor's line numbers (which had
drifted from the file on disk in all five cases — see each finding's "Anchor
drift" note). Where a mechanism was claimed, it was reproduced empirically
against `vigia_scorer._vigia_score` and the `data/cases/` corpus rather than
reasoned about in the abstract. `abductive-engineering` governed the framing:
each finding's *stated mechanism* was treated as one hypothesis among several,
tested for whether it actually entails the claimed observation before being
accepted.

No scorer code was changed as a result of this audit. Two of the five findings
describe genuine scorer behavior; both are calibration-doctrine questions in
the shape already established by L-049/B-091/B-092 (Round 4 saturation) and
L-054 (exculpatory context), and both are recorded as open limitations rather
than patched unilaterally.

## Summary table

| # | Claim | Verdict | Disposition |
|---|-------|---------|-------------|
| 1 | TOCTOU symlink race in `_quarantine_malformed_evidence` (mkstemp name vs. FD open) | **Refuted as stated** | No-op guard not added |
| 1b | (found during verification, not claimed by the audit) `os.chmod(final_path, ...)` follows symlinks by name post-rename | **Confirmed — real, low-severity residual** | **Fixed**: sealed via `os.fchmod` on the open descriptor |
| 2 | Noisy-OR lets soft-domain flood "activate" a near-zero hard domain | **Refuted as stated** | — |
| 2b | (confirmed by measurement) B-068 cross-domain gate counts domain *presence*, not domain *mass* | **Confirmed — real** | Documented as **L-071**, not patched (corpus-gated) |
| 3 | `caie.py::_SOURCE_MATERIALITY_FLOOR=0.05` should have excluded a `raw=0.01` pivot artifact | **Refuted** | Wrong module — that floor has no authority over the scorer's B-068 gate |
| 4 | `provenance_chain` trust uses `len()` only, hashes never verified | **Already documented** | **L-065** (2026-07-18); this audit answers the layering question it left open — see below |
| 5 | `Fraction` → `float` rounding at the MALICE threshold demotes a case that should be MALICE (false negative) | **Refuted — direction inverted** | Documented as **L-073**: the measured bias is a false *positive*, and is unreached by the corpus |
| 6 | Exculpatory/Eco filter can be defeated by writing a honeypot-flavored description to "fool" it | **Refuted — mechanism backwards** | Documented as **L-072**: bait text makes Eco *retain* the artifact; suppression needs bland text, and most corpus cases already have it |

---

## Finding 1 — TOCTOU in `_quarantine_malformed_evidence` [REFUTED, real residual FIXED]

**Anchor drift:** claimed line ~520; live function starts at
`vigia_sift_bridge.py:1019`.

**Claim:** an attacker can replace the mkstemp-named temp file with a symlink
to `/dev/null` "in the microsecond between `mkstemp()` giving the name and the
code opening the FD to write."

**Why this is false:** `tempfile.mkstemp()` does not return a name to open
later — it returns `(fd, path)` from **one syscall**, with `O_CREAT|O_EXCL`.
The code already writes through that `fd` via `os.fdopen(fd_dst, "wb", ...)`.
There is no window between "get the name" and "open the FD" because the FD
comes from the same call that produces the name. The recommended defense
(`os.fstat(fd)` to confirm a regular file) is a provable no-op:

```python
fd, path = tempfile.mkstemp(dir=d)
stat.S_ISREG(os.fstat(fd).st_mode)   # always True — O_EXCL forbids anything else
```

It was **not added** — a guard against an impossible condition is noise in an
audit trail whose value depends on every check meaning something.

**Real residual found while verifying:** `os.rename(purgatory_tmp, final_path)`
was followed by `os.chmod(final_path, 0o400)`. `chmod` by **path** resolves the
name and follows symlinks, while the `os.path.islink()` guard immediately
before it is a check-by-**name**. An attacker with write access to
`_PURGATORY_DIR` (mode `0o700`, so this requires the owning uid — severity is
low) could swap the temp file for a symlink *after* the `islink()` check and
have the subsequent `chmod` apply `0o400` to an arbitrary file of that uid.

**Fix (this commit):** the `0o400` seal now happens via `os.fchmod(dst.fileno(),
0o400)` on the descriptor that was actually written, before the file is
closed. The post-rename `os.chmod(final_path, ...)` was removed — re-adding it
would reopen exactly the window `fchmod` closes.

**Tests:** `tests/test_purgatory_fd_sealing.py` (15 tests) — proves the claimed
mechanism is a no-op (`TestMkstempClosesTheStatedWindow`), demonstrates the
`chmod`-follows-symlink hazard directly (`TestFchmodSealsTheInodeNotTheName`),
and pins the fix at the source level via AST parsing so it survives even in an
environment missing optional dependencies (`TestQuarantineSourceUsesFdSealing`).

---

## Finding 2 — Trust-matrix flooding / cross-domain pivot [REFUTED mechanism, CONFIRMED different one → L-071]

**Anchor drift:** claimed `caie.py` line ~538/~967 for `_MAX_ARTIFACTS` and the
materiality floor; live constants are at `caie.py:526` and `:570`.

**Claim:** 100 soft-domain artifacts (e.g. `log_entry`) plus one hard-domain
artifact at `raw_score=0.01` lets Noisy-OR "activate" the hard domain via
volume of soft noise, and `_SOURCE_MATERIALITY_FLOOR=0.05` should have
excluded that `0.01` artifact but might not be calibrated to.

**Why the stated mechanism is false:** `vigia_scorer.py`'s R4-3 per-domain
scores (`r43_domain_scores`, computed over `_by_domain`) are built **only**
from that domain's own artifact indices. A soft domain's mass never enters a
hard domain's score — verified directly:

```
100x log_entry raw=0.85 (soft flood only)           -> SUSPICION  0.1866
100x log_entry + 1x mft_entry raw=0.01              -> SUSPICION  0.1987
```

The score barely moves and the verdict does not flip via this path — B-091's
per-domain tail decay holds.

**Why `_SOURCE_MATERIALITY_FLOOR` doesn't apply here at all:** that constant
lives in `caie.py` and gates CAIE's own `independent_sources` /
`confidence_penalty`. It has **no authority over `vigia_scorer.py`'s B-068
corroboration gate**, which is a separate module with its own, much lower
floor: `_M2_MIN_SIGNAL_ADJ = 0.0` (strict `>`). Confusing the two floors is
the root of this finding's miscalibration claim — verified in
`tests/test_l071_cross_domain_pivot.py::TestM2SignalFloorIsExactlyZero`.

**What actually reproduces (a different bug, confirmed by measurement):** the
B-068 **cross-domain branch** opens on
`_n_domains >= 2 AND (_n_gate_arts >= 4 OR len(_gate_types) >= 3)`.
`_n_domains` counts domains **represented** by any artifact clearing the
`0.0` floor — i.e. counts *presence*, not *mass*. A single near-zero artifact
in a second domain is a full corroborating domain:

```
16x D3 filesystem_metadata (1 domain)         -> SUSPICION  0.5888
  + 1x network_flow raw=0.001                 -> MALICE     0.6145   (+0.0257)
  + 1x network_flow raw=0.0     (control)     -> SUSPICION  0.5888   (floor holds)
```

The verdict moves a full rung on a score delta of +0.026 — the promotion is
not carried by evidential mass.

**Why not patched:** measured, and both obvious fixes are refuted by the
corpus (not merely assumed to be risky):

1. A per-artifact floor above `0.0` is an **empty interval** — already proven
   in the `_M2_MIN_SIGNAL_ADJ` calibration note (`vigia_scorer.py` ~L147):
   canonical MALICE cases corroborate at adjusted `0.0017–0.002`, while
   excluding the known VIGIA-CAN-029 diluent needs `> 0.013`. The pivot at
   `raw=0.01` falls *inside* that gap.
2. A per-domain artifact-count floor (≥2 per domain) is refuted directly by
   the corpus: many canonical MALICE cases open this exact branch with
   reasons like `cross-domain (4 domains, 4 artifacts)` — one artifact per
   domain, by construction. A count floor would flip legitimate cases.

Recorded as **L-071** in `KNOWN_LIMITATIONS.md`, with the untried
recommendation (gate on `r43_domain_scores`, which the scorer already
computes for traceability, instead of on raw presence) left for a future
corpus-gated calibration decision.

**Tests:** `tests/test_l071_cross_domain_pivot.py` (9 tests) — characterization
only; they pin measured behavior, they do not assert it is correct.

---

## Finding 3 — `provenance_chain` custody trust is length-only [ALREADY DOCUMENTED — L-065, layering question answered]

**Anchor drift:** claimed `caie.py` context; the live consulted factor is
`vigia_scorer.py:921-928` (`epc_factor`), cited in L-065 at the now-stale
`721-728`.

This is not a new finding — `KNOWN_LIMITATIONS.md::L-065` (registered
2026-07-18) already states that `epc_factor` consults only `len(chain)` and
that hash content is never checked, with a corpus-measured reproduction and a
pending doctrine decision.

**What this audit round adds:** a direct answer to the layering question
L-065 leaves open — *"is this verified in another layer instead?"* No. A
`ChainOfCustody` class exists at `vigia/core/chain_of_custody.py` and is
threaded through the SIFT analyzers (`vigia/sift/disk_forensics.py`,
`macos_forensics.py`, `event_log_correlator.py`,
`registry_timeline_reconstructor.py`, `prefetch_analyzer.py`), but always as
`Optional[ChainOfCustody] = None`. Nothing connects an instance of it to the
scorer's `provenance_chain` field, which is read straight from the case JSON
as a plain list of strings. The skeleton the audit correctly identified is
real, but it is not wired to the trust computation it would need to verify.

L-065's doctrine options (verify the terminal hash / rename the factor
honestly / accept as documented) remain open; this round does not change that
decision, only confirms which of the audit's premises hold.

---

## Finding 4 — Threshold boundary: `Fraction` vs. `float(_dround(...))` [DIRECTION INVERTED → L-073]

**Anchor drift:** claimed lines 87/1006/1056/1059/1110; live sites are
`_dround` at `vigia_scorer.py:174`, the boost/penalty accumulation at
`~1302-1312`, and the MALICE threshold at `~1419`.

**Claim:** an exact `Fraction(33, 100)` sum, once passed through
`_dround`/`float`, can round *down* to `0.32999999999999996`, producing a
false **negative** (a case that should be MALICE demoted to SUSPICION).

**Why the direction is inverted:** Python compares `float` against `Fraction`
**exactly** — it does not approximate the `Fraction` side. Measured for all
four ladder thresholds, the nearest IEEE-754 double sits **above**, not below,
the exact rational:

```
float(0.33) - Fraction(33, 100) = 7/450359962737049600   (positive)
```

So a score landing exactly on a threshold's grid point compares as **strictly
greater** than that threshold even though exact decimal arithmetic would call
them equal — a promotion by one rung, i.e. a false **positive**, not the
claimed false negative. The audit's own numeric example is additionally
self-defeating under a strict `>`: `Fraction(33, 100) > Fraction(33, 100)` is
`False` regardless of which arithmetic is used, so there was never a case to
lose there.

**Not a determinism violation:** `_dround` produces the identical double on
every architecture for the precisions used here; Invariant 4 (`Fraction`/
`Decimal` exact accumulation) is intact. This is boundary exactness, not
cross-platform divergence.

**Reachability (measured, not assumed):** across all 163 scoreable corpus
cases (`data/cases/` + `data/cases/consolidated_canonical/`), **zero** land on
or within two 4-decimal grid steps of any of the four ladder thresholds. The
defect is latent.

**Adjacent hazard found while checking this (recorded, not patched):**
`_dround` returns `0.0` for any argument that is not `int`/`float` — a
`Fraction` or `Decimal` reaching it would be silently zeroed instead of
raising, in a module that uses both types elsewhere. Instrumented over 80
corpus cases: only `float` arguments reach it (4449 calls observed), so the
path is currently unreachable through the corpus, but the guard fails silent
rather than loud.

Recorded as **L-073**. **Tests:**
`tests/test_l072_declared_inputs_and_threshold_edge.py::TestL073ThresholdEdgeGrantsTheHigherRung`
(5 tests).

---

## Finding 5 — Exculpatory/Eco "burden of proof" [MECHANISM BACKWARDS, EXPOSURE LARGER → L-072]

**Anchor drift:** claimed lines 272-291/284; live block is
`vigia_scorer.py:~742-777` (`_semantic_role`, `_artifact_text`, the D1
exculpatory loop).

**Claim:** an attacker can label an incriminating artifact
`semantic_role: "exculpatory"` and write a description that mimics a
"honeypot" or "forensic investigation" note to fool the Eco filter into
setting it aside.

**Why the mechanism is backwards:** `_eco_bait_hits` firing on bait terms
(`honeypot`, `mimikatz`, etc.) is what makes the artifact **stay** in scoring
(`_exculpatory_eco_retained`). Writing honeypot-flavored text is the one thing
guaranteed to *keep* the artifact scored. Suppression requires the opposite —
a bland, unremarkable description.

**Why the real exposure is larger than what was reported:** measured over the
52 corpus cases that score MALICE/INTENT, relabeling every artifact
`exculpatory` **without touching any text**:

```
label-only relabel of ALL artifacts        -> 37/52 lose the MALICE verdict (13 -> NOISE)
label-only relabel of ALL BUT ONE          -> 35/52 lose the MALICE verdict
label + neutral description text           -> 52/52 collapse to NOISE, score 0.0000
```

In the large majority of cases, no text crafting was needed at all — the
original artifact descriptions were already bland enough to never trip Eco.

**Relation to the existing L-054 doctrine:** `KNOWN_LIMITATIONS.md::L-054`
argues the exculpatory path is protected because the B-028/B-065 alert floor
re-raises a residual incriminatory signal after exculpatory artifacts are set
aside. That protection does not reach the path measured here: when **every**
device artifact is declared exculpatory, `_vigia_score` takes an early return
(`NOISE, score 0.0, confidence 0.9`) *before* any floor logic runs. A floor
can raise a low alert; it cannot resurrect a verdict that was never computed.

**Mitigating facts, stated for balance:** the suppression is **auditable, not
silent** — every set-aside artifact is recorded in
`refutation_context.set_aside` and the emitted `reason` names the exculpatory
path explicitly. The realistic threat model is a corrupt or coerced case
author (an insider with write access to the case JSON), not a remote,
unauthenticated attacker.

**Audit's proposed fix, considered and not adopted:** block set-aside when
`raw_score > 0.5` and `evidence_type` is not `log_entry`/`document_geometry`.
Rejected because it would also discard genuine high-confidence exculpatory
evidence (e.g. a well-corroborated authorization memo), trading one
uncalibrated failure mode for another — a doctrine tradeoff, not a
correction, and it belongs in the same corpus-gated decision as L-054.

Recorded as **L-072**. **Tests:**
`tests/test_l072_declared_inputs_and_threshold_edge.py::TestL072DeclaredExculpatoryNeutralizesEvidence`
(5 tests).

## Test evidence

| Command | Result |
|---|---:|
| `pytest tests/test_purgatory_fd_sealing.py tests/test_l071_cross_domain_pivot.py tests/test_l072_declared_inputs_and_threshold_edge.py -q` | 39 passed |
| `pytest tests/test_r4_boundaries.py tests/test_r4_3_domain_saturation.py tests/test_audit_gates.py tests/test_caie_source_materiality.py tests/caie/test_canonical_cases.py -q` | 73 passed, 25 xfailed |
| Full suite (`tests/ vigia/tests/`, `--continue-on-collection-errors`) before vs. after this audit | 21 pre-existing failures (missing optional deps: `psutil`, `fastapi`) both before and after — **zero new failures** |

## Next decision

L-071, L-072, and L-073 are recorded, not fixed — each requires the same
199-case comparative corpus gate that B-091/B-092 used before touching scorer
semantics (per `KNOWN_LIMITATIONS.md`'s own precedent: a calibration change
without that gate trades one uncalibrated behavior for another). L-065's
doctrine decision (verify the terminal hash / rename the factor / accept as
documented) is unchanged by this round. No scorer behavior differs from before
this audit; only `vigia_sift_bridge.py`'s purgatory sealing changed.
