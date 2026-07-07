# Security Audit — VIGÍA Forensic Intent Suite

## Red Team Round 3 — Emergent / Architectural Fractures

**Date:** 2026-07-07  **Method:** Abductive Engineering (A–D–I) + Red-Team Auditing (epistemic ladder)
**Scope:** composition of individually-correct modules — the scorer, the CAIE
temporal engine, the canonical hasher, the tool-log chain verifier, and the
corpus loader. **Read-only audit — no product code modified.**
**Base:** `claude/monotonicity-invariants-redteam-sc0x9r` @ `1d84c84`
**Restore tag:** `pre-session-round3-20260707-033355`
**Runtime:** CPython 3.11.15
**Reproducible evidence:** `scripts/redteam_round3_emergent.py`
(`PYTHONPATH=$(pwd) python3 scripts/redteam_round3_emergent.py [R3-1|R3-2|R3-3|R3-4]`)

Each module here is individually correct. The findings are in the seams: a
timestamp the parser reads faithfully but no one range-checks; a canonical form
that is internally consistent but collides across a type boundary; two case
files each valid on its own; a hash chain that proves exactly what it claims and
nothing more.

---

## Threat model

- Attacker **CAN**: assemble the artifact set / case JSON fed to the scorer
  (careless examiner, automated ingestion, or an adversary who can *add* — not
  forge — evidence); and, for R3-2/R3-4, hold write access to a bundle **before
  or after sealing** while **not** holding the HMAC key.
- Attacker **CANNOT**: modify `vigia_scorer.py`/CAIE/verifier code, forge the
  HMAC, or compromise the interpreter.
- Trust boundary crossed: the composition boundary between a module's local
  contract and a system-level invariant (temporal plausibility, hash
  injectivity, single-source-of-truth ground truth, causal auditability).

---

## Epistemic legend

CODE FACT · PLAUSIBLE HYPOTHESIS · **CONFIRMED BY INDUCTION** · FALSIFIED

## Executive summary

| ID | Severity | Level | Module seam | Finding |
|----|----------|-------|-------------|---------|
| R3-1 | **High** | **CONFIRMED BY INDUCTION** | CAIE TCV × no range gate | An epoch-edge timestamp (1970 on the earlier event, 2099 on the later) fabricates a severity-1.0 `TEMPORAL_CAUSALITY_VIOLATION`, flipping NOISE → SUSPICION. |
| R3-2 | Medium | **CONFIRMED BY INDUCTION** | `_canonicalize` injectivity | `True`/`"true"`, `1`/`"1:int"`, `None`/`"null"`, `0.1`/`"0.10000000"` all collide to one hash; `NFC`/`NFD` and `CRLF`/`LF` map one logical string to two hashes. |
| R3-3 | Medium | **CONFIRMED BY INDUCTION** | corpus loader dedup | 59 duplicated case stems across dirs; **3 carry divergent `expected_verdict`** (silently resolved by dir precedence), plus 1 malformed duplicated stem. |
| R3-4 | Low–Med | **CONFIRMED BY INDUCTION** | tool-log chain verifier | A v2 chain with timestamps running backwards, sitting at 1970, and duplicating a prior event verifies as CHAIN VERIFIED. Chain attests seq-order + integrity, not causality. |

---

## R3-1 — Temporal: an epoch-edge timestamp fabricates a malice fracture

**Bucket:** software vulnerability (emergent). **Severity: High** — a *benign*
data-quality artifact produces false MALICE signal.

### Surprise / expectation violated
A single artifact should not be able to manufacture a maximum-severity
"deliberate planting" fracture merely by carrying an out-of-range timestamp —
especially `1970-01-01T00:00:00Z`, which is the universal sentinel a forensic
tool emits when it *fails* to parse a date. "Missing timestamp" must not read as
"proof of retroactive planting."

### Peircean chain
- **Firstness (observe):** `CrossArtifactIncongruenceEngine._detect_temporal_causality`
  (`vigia/tools/caie.py:1361-1463`) pairs any artifact with `network_log_time`
  metadata against any `memory_process`, parses both with `_parse_ts_tcv`, and
  if `net_time < proc_time` emits `TEMPORAL_CAUSALITY_VIOLATION`, **severity
  fixed at 1.0**.
- **Secondness (contrast):** `_parse_ts_tcv` is robust about *format* (Z suffix,
  naive → UTC, unparseable → skip with audit) but performs **no absolute-range
  validation**: 1970, 2099, year-9999 all parse to valid `datetime`s. The rule
  compares two timestamps for *relative* order and never asks whether either is
  *physically plausible*. The scorer then treats `TEMPORAL_CAUSALITY_VIOLATION`
  as a `MALICIOUS_FRACTURE_TYPE` and adds `severity × 0.45 = 0.45` to the malice
  score (`vigia_scorer.py:766-811`).
- **Thirdness (law):** the composition assumes "timestamps are real measurements"
  (CAIE's contract) while the ingestion boundary guarantees no such thing. The
  weaponizable pattern: set the earlier event to the epoch sentinel — the exact
  value a broken parser upstream would already produce — and the strongest
  temporal signal in the system fires for free. Carnegie: none; this is a
  data-quality→verdict short circuit, not persuasion.

### Abduction (rival hypotheses)
- **H1 (null):** timestamps are range-validated somewhere before the TCV rule
  fires. — *Falsified:* no range check exists; `_parse_ts_tcv` returns any
  parseable datetime.
- **H2 (confirmed):** an epoch-edge value on the causally-earlier event
  fabricates the severity-1.0 fracture and moves the verdict.
- **H3:** only *examiner-supplied* `temporal_violations` reach the scorer, so
  this is pure attacker-controlled input. — *Partly:* the scorer also accepts
  input violations, but here the fracture is **recomputed live by CAIE**
  (`caie_fractures_source = live_caie`) from the artifact's own timestamp, so no
  pre-declared violation is needed.
- **H4:** the boost is capped/negligible. — *Falsified:* boost = 0.45, enough to
  cross NOISE → SUSPICION on otherwise near-zero evidence.

### Deduction → Induction (prediction stated before result)
Predict: two near-zero-signal artifacts (`network_flow` raw 0.2 +
`memory_process` raw 0.2) score NOISE with plausible timestamps; setting the
network `network_log_time` to `1970-01-01T00:00:00Z` fires exactly one fracture
and flips the verdict.

```
BASELINE  net@2026-10h proc@2026-09h : NOISE     score=0.0701  fractures=0 boost=0.00
1970      net@1970     proc@2026-09h : SUSPICION score=0.5058  fractures=1 boost=0.45
2099-proc net@2026     proc@2099     : SUSPICION score=0.5058  fractures=1 boost=0.45
2099-net  net@2099     proc@2026-09h : NOISE     score=0.0701  fractures=0 boost=0.00
```

Both sentinels that make the *earlier* event earlier-still (1970 on network) or
the *later* event later-still (2099 on process) fire; the control (2099 on the
network, which merely makes the ordering self-consistent) does not — confirming
the mechanism is the unbounded `net_time < proc_time` comparison, not the value
per se. **CONFIRMED under the threat model where the attacker (or a broken
upstream tool) sets one artifact's timestamp.**

### Causal chain
```
artifact.network_log_time = "1970-01-01T00:00:00Z"   (epoch sentinel / parser failure)
   ↓ _parse_ts_tcv → datetime(1970,…)   [format-valid, range-unchecked]
net_time(1970) < proc_time(2026)  → TRUE
   ↓ Fracture(TEMPORAL_CAUSALITY_VIOLATION, severity=1.0)
scorer: fracture_malice_boost += 1.0 × 0.45 = 0.45
   ↓ raw_intent_score += 0.45
verdict  NOISE → SUSPICION   (score 0.0701 → 0.5058)
```

---

## R3-2 — Canonicalization: distinct → one hash, and one → two hashes

**Bucket:** integrity gap in the tamper-evidence layer (leans hygiene, but it is
a real injectivity failure). **Severity: Medium.**

### Surprise / expectation violated
A canonical form for hashing must be **injective on meaning**: two objects with
the same hash must mean the same thing, and one object must always hash the same
way. `vigia/core/canonicalize.py` violates both directions.

### Peircean chain
- **Firstness:** `_canonicalize` maps `bool→"true"/"false"`, `int→"N:int"`,
  `float→"N.NNNNNNNN"`, and `str→` *itself, unchanged* (`canonicalize.py:59-79`).
- **Secondness:** because strings pass through untouched, the string literal
  `"true"` canonicalizes to `"true"` — identical to boolean `True`. Likewise
  `"1:int"` ≡ int `1`, `"null"` ≡ `None`, `"0.10000000"` ≡ float `0.1`. Two
  distinct inputs → one canonical form → one SHA-256. In the other direction,
  `str` passthrough means `NFC("café")` and `NFD("café")`, and `"a\r\nb"` vs
  `"a\nb"`, are different byte strings → different hashes for the same logical
  content. And a `Fraction` (used throughout the scorer's internal arithmetic)
  falls to the `str()` branch: `Fraction(1,2)→"1/2"`, which diverges from float
  `0.5→"0.50000000"`.
- **Thirdness:** the type tag (`":int"`, fixed-decimal float) was added to
  *prevent* int/float/str confusion, but it is applied only to the non-string
  side; the string side is never escaped, so the tag becomes forgeable by any
  attacker who supplies the tag text as a literal string. The invariant "the
  canonical hash identifies the value" holds only if strings are also escaped.

### Induction (all confirmed, `scripts/redteam_round3_emergent.py R3-2`)
```
TWO DISTINCT INPUTS -> ONE HASH:
  True vs "true"                 COLLISION
  False vs "false"               COLLISION
  None vs "null"                 COLLISION
  1 vs "1:int"                   COLLISION
  0.1 vs "0.10000000"            COLLISION
  {"verdict": True} vs {"verdict": "true"}   COLLISION   (nested, real payload shape)
  {"n": 1} vs {"n": "1:int"}     COLLISION
ONE LOGICAL INPUT -> TWO HASHES:
  NFC "café" vs NFD "café"       UNSTABLE
  CRLF vs LF                     UNSTABLE
  Fraction(1,2)="1/2" vs 0.5="0.50000000"   DIVERGENT
```

### Threat-model precondition & precise impact
`_canonicalize` backs `compute_entry_hash` (tool-log v2) and the EBS bundle
hash. **Consequence:** an attacker with write access to a sealed bundle can
retype a hashed field — swap `True` for the string `"true"`, or `1` for
`"1:int"` — and the `entry_hash` is **unchanged**, so the chain still links *and
the keyed HMAC still matches* (the HMAC is computed over `entry_hash`, which did
not move). This is a collision in the tamper-evidence layer itself, not merely a
cosmetic hash-hygiene note.

Precise language (Part 7): this is **"two distinct payloads share one sealed
hash,"** not "the seal is broken." Whether the retype changes a *verdict*
depends on a downstream consumer that reads the field back and distinguishes
`True` from `"true"` — that step is **PLAUSIBLE HYPOTHESIS, not confirmed**, and
is capped there deliberately. The collision and the instability themselves are
CONFIRMED. The NFC/NFD instability has an independent benign harm: two honest
acquisitions of the same Unicode evidence hash differently, which reads as
"content changed" and defeats cross-artifact/dedup matching.

---

## R3-3 — Duplicate case shadowing with divergent ground truth

**Bucket:** data-integrity / evaluation-process defect. **Severity: Medium**
(it silently corrupts the accuracy metric, not the runtime verdict).

### Surprise / expectation violated
A case ID should map to exactly one ground-truth label. The corpus stores the
same stem in multiple directories, and the runner (`run_all_agent.py`,
`find_cases`) dedups by stem taking the **first directory in `CASES_DIRS`
order** — so which label counts is decided by directory precedence, silently.

### Induction (`scripts/redteam_round3_emergent.py R3-3`)
```
total stems: 199   duplicated across dirs: 59
DIVERGENT-label duplicates: 3
  VIGIA-AMB-001   runner counts NOISE (data/cases/)   vs ABSTAIN (converted/)
  VIGIA-AMB-002   runner counts NOISE (data/cases/)   vs ABSTAIN (converted/)
  case_008_multi_source_fraud_demo
                  runner counts SUSPICION (data/cases/) vs MALICE (legacy/)
MALFORMED duplicated stem: 1
  VIGIA_BREAK_001-010  → JSON is a list, not a dict (extract_expected → "UNKNOWN")
```

### Thirdness / mechanism
This is the same class as the Round 2.1 `VIGIA-FP-001` shadow (the relabel had
to be applied to *both* copies). The evaluation harness has **no
single-source-of-truth guard**: 56 of the 59 duplicates happen to agree today,
masking the 3 that disagree. The metric "166/199" is computed against whichever
copy wins the directory race; the losing copies are dead ground truth that can
(and in Round 2.1 did) drift. `case_008` is the sharpest: the same fraud demo is
labelled SUSPICION in one tree and MALICE in another — a two-band disagreement
about the same evidence.

### Precise impact
No runtime verdict is wrong *because* of this; the harm is that the corpus
cannot be trusted as ground truth without deduplication, and a future edit to a
shadowed copy is a silent no-op (or a silent flip if it changes the winner).
Recommend a loader assertion: duplicated stems must have identical
`expected_verdict`, else fail loudly.

---

## R3-4 — Audit-chain accepts a causally impossible history

**Bucket:** threat-model boundary made explicit + hardening. **Severity:
Low–Medium.** Per the method (Part 5), stated honestly rather than sold as a
seal break.

### Surprise / expectation violated
A chain-of-custody log *feels* like it attests "these events happened, in this
order, at these times." The v2 chain attests **seq monotonicity + per-entry
content integrity + linkage** — and nothing about whether the recorded
*timestamps* are causally possible.

### Peircean chain
- **Firstness:** `verify_tool_execution_log` / `verify_chain`
  (`vigia/core/tool_log_chain.py`, `hash_chain.py`) recompute `entry_hash` over
  the full payload (timestamp included, so timestamps are tamper-evident *after*
  sealing), check `prev_hash` linkage, and enforce `seq = 1,2,3,…`.
- **Secondness:** neither the appender (`ToolExecutionLogChain.append`) nor the
  verifier compares consecutive timestamps or bounds them to a plausible range.
  `append` stamps `datetime.now(...)` by default but accepts any injected
  timestamp verbatim. So a log can carry `seq=2` earlier than `seq=1`, a `seq=3`
  at the 1970 epoch, and a `seq=4` duplicating `seq=1`'s exact content at a 2099
  timestamp — all sealed, all verifying.
- **Thirdness:** the honest boundary (Part 5 "audit-chain plausibility"): a hash
  chain proves **insertion order and integrity, not causality**. Presenting
  "CHAIN VERIFIED" to a judge as if it certified a plausible timeline overstates
  what the cryptography does.

### Induction (`scripts/redteam_round3_emergent.py R3-4`)
```
seq=1  2026-03-01T12:00:00Z  generate_forensic_hash
seq=2  2026-03-01T08:00:00Z  read_evidence          (4h BEFORE seq=1)
seq=3  1970-01-01T00:00:00Z  infer_intent           (epoch sentinel)
seq=4  2099-12-31T23:59:59Z  generate_forensic_hash (dup of seq=1 content)

timestamps monotonic increasing? False
verifier: valid=True  seq_discontinuities=0  broken_links=0   → CHAIN VERIFIED
```

### Precise impact
Not a break of the seal — the seal works perfectly. The gap is that verification
success is **necessary but not sufficient** for a plausible custody timeline.
Recommend an optional plausibility pass (monotone non-decreasing timestamps
within a sane absolute window, duplicate-content flagging) reported alongside —
never conflated with — the cryptographic result.

---

## Discarded / non-exploitable vectors

| Vector | Result | Why it failed |
|--------|--------|---------------|
| 2099 on the *network* (earlier) event | No fracture | Makes ordering self-consistent (`net > proc`); the `net_time < proc_time` test is false. Confirms the mechanism is relative order, not the raw value. |
| `dict` key-ordering affecting the hash | No effect | `_canonicalize` sorts dict items and `json.dumps(sort_keys=True)` re-sorts; ordering is already canonical. |
| Duplicate **seq** in the tool-log | Caught | The verifier enforces `seq = expected_seq` and records `seq_discontinuities`; only duplicate *content at distinct seq* slips through (R3-4). |
| float collision beyond 8 decimals changing a verdict | Not reachable | Scores round to 4 decimals before any threshold; sub-8-decimal collisions cannot move a band edge. Collision is real (R3-2) but verdict-inert. |

---

## Recommendations (out of scope of this read-only audit — record only)

1. **R3-1:** add an absolute-range plausibility gate in `_parse_ts_tcv` (reject
   or down-weight timestamps outside e.g. [2000, now+skew]); treat the 1970
   epoch as *missing*, not as evidence. A `TEMPORAL_CAUSALITY_VIOLATION` built
   on an out-of-range endpoint should not carry severity 1.0.
2. **R3-2:** make `_canonicalize` injective — escape strings (e.g. prefix
   `s:` / JSON-encode) so no string can spell another type's tag; NFC-normalize
   text and normalize newlines before hashing; give `Fraction` an explicit,
   value-stable encoding. Version-bump `CANONICALIZE_VERSION` and keep v1
   verification for historical bundles.
3. **R3-3:** deduplicate the corpus (one canonical location per stem) or add a
   loader assertion that duplicated stems share an identical `expected_verdict`;
   fix the malformed `VIGIA_BREAK_001-010.json` (list, not dict).
4. **R3-4:** add a non-cryptographic timeline-plausibility report (timestamp
   monotonicity + absolute-range + duplicate-content) surfaced separately from
   "CHAIN VERIFIED", so the audit trail never implies causality it did not check.
