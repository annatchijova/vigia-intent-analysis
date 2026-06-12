# VIGÍA — Known Limitations

**Version:** EBS v1 + P2 calibration | **Updated:** 2026-05-27
**Applies to:** `github.com/annatchijova/vigia-intent-analysis`

> VIGÍA does not claim to be infallible — it claims to be **auditable**.
> These limitations are documented deliberately as part of the Daubert
> standard of falsifiability. A system that cannot name its failure modes
> cannot be trusted in court.

---

## How to Read This Document

Each limitation entry describes:

- **What** VIGÍA gets wrong or cannot do
- **Why** — the technical root cause
- **Forensic implication** — what this means for real casework
- **Workaround** if one exists, or explicit statement that none does

Limitations marked **[RESOLVED]** were present in earlier versions and
have been fixed. They are kept here for auditability and to explain the
reasoning behind design decisions in the commit history.

Limitations marked **[DESIGN DECISION]** are intentional behaviors that
could theoretically be changed but were chosen deliberately with
documented rationale.

---

## Part I — Scoring and Verdict Limitations

### L-001 — Perfect Attack Without Anomalies

**Affects:** `BREAK_006` | **Status:** Real limitation

**Description:** When an attacker executes an operation without technical
errors — valid credentials, consistent timestamps, no detectable tooling —
VIGÍA tends to emit SUSPICION rather than MALICE.

**Root cause:** The scoring engine depends on structural anomalies and
CAIE fractures. Without inconsistencies, the composite score does not
cross the MALICE threshold.

**Forensic implication:** VIGÍA is more effective detecting attacks with
operational errors than high-tier APTs with perfect OPSEC. This is not
unique to VIGÍA — it reflects the fundamental epistemological limit of
artifact-based analysis: an actor who leaves no trace cannot be detected
from the trace.

**Workaround:** Combine with baseline behavioral analysis
(`baselines_institucionales.yaml`) to detect statistical deviations from
institutional norms.

---

### L-002 — Critical Signal Drowned in Noise

**Affects:** `BREAK_004` | **Status:** Real limitation

**Description:** When there are many irrelevant artifacts and few critical
ones, the average score drops and VIGÍA emits SUSPICION rather than MALICE.

**Root cause:** The evidence aggregator does not implement dynamic
weighting by artifact relevance. All artifacts carry similar initial
weight before trust adjustment via CAIE profiles.

**Forensic implication:** In high-noise cases, pre-filter artifacts by
relevance before ingesting into the pipeline. Submit only artifacts
that are forensically relevant to the hypothesis under investigation.

---

### L-003 — Log Absence as Evidence

**Affects:** `BREAK_007` | **Status:** Real limitation

**Description:** The absence of records where they should exist — e.g.,
an SSH session present in netflow but with no entry in auth.log — does
not generate enough signal to reach MALICE.

**Root cause:** The current model treats absent evidence as neutral noise,
not as a positive signal of tampering.

**Forensic implication:** Detection of "significant silence" requires
comparison against institutional baselines. Without a configured baseline,
VIGÍA cannot evaluate absences. This is a known open problem in DFIR:
distinguishing "log was never written" from "log was deleted" from "log
collection failed" requires out-of-band context.

---

### L-004 — Prompt Poison / Misleading Narrative

**Affects:** `BREAK_009` | **Status:** Real limitation

**Description:** When a text artifact contains assertions such as "case
already confirmed benign by the team," VIGÍA does not fully neutralize
misleading narrative framing embedded in free-text artifacts.

**Root cause:** `LLMShield` filters direct prompt injections into the
reasoning engine but does not neutralize misleading narratives embedded
in artifacts submitted as evidence. The system partially mitigates this
via reduced trust for free-text artifact types.

**Forensic implication:** All free-text artifacts must be treated with
reduced trust. Do not rely on unverifiable assertions embedded within
evidence items — this is standard forensic procedure regardless of
tooling.

**Reference:** Austin (1962) — false performative speech acts. A text
that says "this is benign" does not make the evidence benign.

---

### L-005 — Verdict Threshold vs. Ambiguous Evidence

**Affects:** `BREAK_002`, `BREAK_005` | **Status:** Debatable

**Description:** Cases involving suspicious but authorized activity
(documented pentest) or simultaneous unrelated events produce SUSPICION
or UNKNOWN rather than more precise verdicts.

**Root cause:** VIGÍA has no access to external organizational context
(tickets, authorizations, policies) during automated analysis.

**Forensic implication:** For cases with authorization context, the analyst
must manually review SUSPICION/UNKNOWN verdicts and incorporate that
context into the final report. Automated tools cannot substitute for
analyst judgment when organizational context is the deciding factor.

---

### L-006 — Single Temporal Inconsistency Triggers MALICE

**Affects:** `BREAK_001` | **Status:** Design decision

**Description:** A single artifact with a timezone inconsistency among
three otherwise aligned artifacts produces MALICE, when greater
uncertainty might be expected.

**Root cause:** The `EFFECT_BEFORE_CAUSE` hard gate and temporal
inconsistency penalty are aggressive by design — they prioritize false
positives over false negatives in a forensic context.

**Design rationale:** In forensics, it is preferable to flag a case that
turns out to be benign than to miss one that turns out to be malicious.
This asymmetric cost structure is intentional and consistent with the
conservative posture recommended by NIST SP 800-86.

---

### L-007 — Semantic Intent Requires LLM Backend

**Affects:** VIGIA-REAL corpus in fallback mode | **Status:** Real limitation

**Description:** In fallback mode (no LLM backend configured), VIGÍA
cannot interpret semantic content embedded in artifacts. Attacker aliases
("Mr. Evil"), IRC channel names ("#Elite.Hackers.UnderNet"), or specific
tool names ("NetStumbler", "Ethereal") carry strong contextual intent
signals that the deterministic scorer cannot evaluate — it only processes
evidence types and numerical scores derived from structural anomalies.

**Root cause:** The AbductiveIntentEngine requires an active LLM backend
(Ollama or Anthropic) to analyze free-text content and generate semantic
fractures that feed back into the scoring pipeline. Without it,
`reason_with_llm` produces post-bundle narrative only and does not
influence scoring.

**Forensic implication:** Fallback mode is deliberately conservative.
Cases with strong semantic intent signals but weak structural anomalies
will score as SUSPICION rather than MALICE. This is epistemologically
correct: without semantic analysis, the system cannot infer intent from
names and narrative context alone.

**Configuration:** Set `VIGIA_LLM_BACKEND=ollama` with a local model
(tested: `hermes3:8b`, `deepseek-r1:8b`) or `VIGIA_LLM_BACKEND=anthropic`
with a valid API key.

---

### L-008 — Homogeneous Evidence Cannot Reach MALICE

**Affects:** VIGIA-REAL-007 | **Status:** Design decision

**Description:** Cases where all artifacts belong to fewer than 3 distinct
evidence types AND have fewer than 4 total artifacts cannot reach MALICE
regardless of individual raw scores. VIGÍA requires heterogeneous
corroboration for the strongest verdict.

**Affected cases (as of 2026-05-27):**

| Case | Artifacts | Types | Score | Verdict |
|------|-----------|-------|-------|---------|
| VIGIA-REAL-002 (Nitroba) | 5 | 2 (`log_entry` + `file_timestamp`) | 0.244 | SUSPICION |
| VIGIA-REAL-007 | 3 | 2 (`log_entry` + `file_timestamp`) | 0.200 | SUSPICION |
| VIGIA-REAL-010 | 4 | 2 (`log_entry` + `file_timestamp`) | 0.238 | SUSPICION |

**Root cause:** The heterogeneous corroboration gate (commit `ae30787`)
requires `n_artifacts >= 4 OR n_unique_types >= 3` to reach MALICE.

**Daubert rationale:** A single class of evidence — however strong
individually — is insufficient to infer malicious intent. Convergence of
independent, heterogeneous evidence types is the epistemological minimum
for the strongest verdict. A case with only logs and timestamps could
represent normal system activity with misconfigured clocks. This principle
is consistent with the convergent validity requirements of Daubert.

**Workaround:** Enrich the case with additional artifact types (registry
keys, memory artifacts, network captures) before submitting to VIGÍA.
If enrichment is not possible, SUSPICION is the correct conservative
verdict pending further investigation.

---

### L-009 — Spoofability Floor Under Forensic Chain of Custody

**Affects:** VIGIA-REAL corpus generally | **Status:** Design decision

**Description:** The `acquisition_assurance` system reduces effective
spoofability for artifacts with documented chain of custody (NIST/DFRWS
certified images). However, a minimum floor prevents spoofability from
reaching zero even for fully verified evidence.

**Technical detail:** With `k=4/5` and FORENSIC assurance (3/4 gates
passed), `log_entry` effective spoofability = `max(1/4, 0.85 × 0.40)` =
0.34 (down from intrinsic 0.85). The floor of 1/4 does not activate in
this case (0.34 > 0.25), but the intrinsic penalty remains.

**Design rationale:** Even within a certified forensic image, log entries
can be tampered before acquisition. The floor encodes the irreducible
epistemic uncertainty about pre-acquisition integrity — a forensic image
proves the data was not modified *after* acquisition, not before.
Consistent with NIST SP 800-86 §4.3.

---

## Part II — CAIE Adversarial Limitations

### L-010 — Sensor Independence Not Verified

**Affects:** CAIE v2.0 adversarial suite (3/25 cases) | **Status:** Real limitation — roadmap v3.0

**Description:** CAIE assumes that different `source_tool` values indicate
independent evidence sources. It does not detect when multiple
`source_tool` values actually represent the same underlying sensor or
acquisition pipeline.

**Affected adversarial cases:**
- `ASSUMPTION_BREAK_timestamp_comparability_AND_sensor_independence`
- `ASSUMPTION_BREAK_sensor_independence_AND_memory_ground_truth`
- `ASSUMPTION_BREAK_sensor_independence_AND_log_completeness`

**Root cause:** No native detection for sensor independence violations.
The system cannot distinguish between truly independent sources and
multiple outputs from a single compromised sensor.

**Attack scenario:** An attacker who compromises a single EDR sensor can
fabricate evidence appearing to come from multiple independent sources.
CAIE v2.0 may produce overconfident verdicts (SUSPICION instead of
INCONCLUSIVE) in this scenario.

**Mitigation (v2.0):** When multiple evidence sources may originate from
the same compromised sensor, manual review is required. Document this
explicitly in the forensic report.

**Roadmap (v3.0):**
- `EvidenceDependencyGraph` with `sensor_fingerprint` tracking
- `AcquisitionContext.provenance_trust` field
- Collapse Decision Layer rules for sensor independence
- INCONCLUSIVE verdict for confirmed dependency detection

---

## Part III — Infrastructure Limitations

### L-011 — Kernel-Level or Root Compromise

**Affects:** All analysis on live systems | **Status:** Permanent design boundary

**Description:** If an attacker has achieved kernel-level access or root
privileges on the host being analyzed — or on the host running VIGÍA
itself — the integrity of all evidence must be considered suspect. VIGÍA
operates entirely in userspace and has no mechanism to detect or
compensate for a compromised kernel, hypervisor, or firmware layer.

**Attack vectors:**

- **Rootkit / LKM injection:** A kernel module can intercept syscalls and
  return falsified data to any userspace process. File hashes, timestamps,
  process lists, and network state can all be spoofed transparently.
- **Direct kernel memory manipulation:** An attacker with root access can
  alter in-memory data structures without leaving traces in
  userspace-visible logs.
- **eBPF weaponization:** Malicious eBPF programs can intercept and modify
  data at the kernel-userspace boundary before VIGÍA reads it.
- **Hypervisor or firmware compromise:** At levels below the OS kernel,
  all host evidence is untrustworthy regardless of VIGÍA's controls.
- **VIGÍA host compromise:** If the machine *running* VIGÍA is under
  adversarial control, the entire pipeline — including chain-of-custody
  sealing, HMAC generation, and audit logs — is compromised. A sealed
  `ForensicBundle` produced under these conditions is cryptographically
  valid but evidentially worthless.

**Forensic implication:** VIGÍA's Daubert guarantees apply strictly to
the software layer. Any analysis on a live system where root compromise
cannot be excluded should be treated as **preliminary**.

**Detection boundary:** VIGÍA may detect artifacts *consistent with* a
rootkit (USN Journal gaps, MFT anomalies, CAIE process/network
incongruences) but cannot confirm kernel integrity from userspace.

**Mitigations (outside VIGÍA's scope):**
1. Acquire a forensic image with a hardware write blocker. Run VIGÍA
   against the image, not the live system.
2. Verify the integrity of the VIGÍA host before sealing any bundle.
3. For high-stakes cases, supplement with out-of-band kernel integrity
   checks (Secure Boot attestation, TPM PCR validation).
4. Document explicitly whether analysis was on a live system or a
   verified forensic image.

**Epistemological note:** No closed system can distinguish between
"no evidence" and "perfectly hidden attack" without an external trust
anchor (TPM, hypervisor attestation, hardware root of trust). This is a
fundamental limit, not a bug.

**References:** NIST SP 800-86 §4.1; RFC 3227 §2.3; MITRE ATT&CK T1014
(Rootkit), T1601 (Modify System Image).

---

## Part IV — Resolved Limitations

### [RESOLVED] Normalization Schema Mismatch

**Was:** The `vigia_scorer.py` had `_normalize_case()` defined but never
called, causing cases with legacy schema (`type`/`content`/`peirce_layer`)
to produce `adjusted_score=0.0` for all artifacts.

**Fixed in:** commit `4230281` — added `case = _normalize_case(case)` call
at the start of `_vigia_score()`.

---

### [RESOLVED] Acquisition Assurance Gate G1 Accepting Legacy Hashes

**Was:** The `_compute_acquisition_assurance()` gate G1 accepted
`sha256:legacy_ART-001` as a valid hash because it only checked for the
`legacy_unknown_provenance` suffix, not for the `legacy_` prefix in
general.

**Fixed in:** commit `4230281` — G1 now requires exactly 64 lowercase hex
characters after `sha256:`.

---

### [RESOLVED] Converter Injecting Uniform `prior_trust=0.7`

**Was:** `scripts/convert_legacy_cases.py` hardcoded `prior_trust: 0.7`
for all artifacts regardless of `peirce_layer`, overriding the
normalizador's correct per-layer values (FIRSTNESS=0.70,
SECONDNESS=0.85, THIRDNESS=0.90).

**Fixed in:** commit `ae30787`.

---

### [RESOLVED] Ambiguous Encryption Case False Positive (VIGIA-REAL-005)

**Was:** VIGIA-REAL-005 (Ali Hadi Encrypt Them All) scored as MALICE
when expected SUSPICION, because `memory_process` with `raw_score=0.95`
and `spoofability=0.15` produced a high adjusted score without
corroborating heterogeneous evidence.

**Fixed in:** commit `ae30787` — heterogeneous corroboration gate
(`n_artifacts >= 4 OR n_unique_types >= 3`) now required for MALICE.

---

## Summary Table

| ID | Description | Affects | Status |
|----|-------------|---------|--------|
| L-001 | Perfect attack without anomalies | BREAK_006 | Real limitation |
| L-002 | Critical signal drowned in noise | BREAK_004 | Real limitation |
| L-003 | Log absence not scored as evidence | BREAK_007 | Real limitation |
| L-004 | Prompt poison / misleading narrative | BREAK_009 | Real limitation |
| L-005 | Ambiguous authorized activity | BREAK_002/005 | Debatable |
| L-006 | Single temporal inconsistency → MALICE | BREAK_001 | Design decision |
| L-007 | Semantic intent requires LLM backend | REAL corpus (fallback) | Real limitation |
| L-008 | Homogeneous evidence cannot reach MALICE | REAL-007 only | Design decision |
| L-009 | Spoofability floor under chain of custody | REAL corpus | Design decision |
| L-010 | Sensor independence not verified | CAIE adversarial 3/25 | Roadmap v3.0 |
| L-011 | Kernel/root compromise (live analysis) | All live analysis | Permanent boundary |
| L-019 | FALSE_FLAG_PATTERN fires on clean foreign-language machines | FP-CULTURAL-CLEAN | Real limitation (deferred) |
| — | Normalization schema mismatch | vigia_scorer.py | **RESOLVED** |
| — | Gate G1 accepting legacy hashes | caie.py | **RESOLVED** |
| — | Uniform prior_trust=0.7 in converter | convert_legacy_cases.py | **RESOLVED** |
| — | Ali Hadi encryption FP | VIGIA-REAL-005 | **RESOLVED** |

---

*VIGÍA — SANS FIND EVIL Hackathon 2026*
*Author: Anna Tchijova | AI Collective: Claude, Kimi, Gemini, DeepSeek, Qwen, Grok, ChatGPT*
*License: Apache 2.0 | Repository: github.com/annatchijova/vigia-intent-analysis*

---

## L-012 — NOISE vs ABSTAIN Semantic Boundary

**Affects:** VIGIA-BEN-014 (Authorized Journalist / Tor) | **Status:** Design decision

**Definition enforced:**

- `NOISE`: null or near-null signal — absence of forensic relevance. Score < 0.05.
- `ABSTAIN`: epistemic indeterminacy under non-trivial competing hypotheses.
  Requires structural conflict, causal ambiguity, or insufficient discriminative
  evidence when signal IS present.

**Implication:** A case with score ~0.018 and no CAIE fractures is NOISE, not ABSTAIN.
ABSTAIN is not a catch-all for low scores — it is reserved for cases where
evidence exists but cannot discriminate between hypotheses.

**Forensic justification:** Inflating ABSTAIN with null-signal cases degrades
ABSTAIN-OH as a metric and weakens the epistemic gate's interpretability.

---

## L-014 — Soft Evidence Convergence Without Cross-Type Fractures

**Affects:** `BREAK_003` (cultural true positive), `BREAK_008` (ambiguous), `BREAK_010` (overperfect)
**Status:** Real limitation

**Description:** Cases where adversarial patterns are encoded exclusively in
soft evidence types (log_entry/network_flow, spoofability 0.75-0.85) without
the multi-type artifact combinations required by CAIE fracture rules.

CAIE fracture detection requires specific type co-occurrence:
- LOG_VS_MEMORY: log_entry + memory_process artifacts required
- CULTURAL_VS_TECHNICAL: cultural_marker + technical artifacts required

Converted break cases with homogeneous soft evidence produce 0 CAIE fractures.
Without fracture bonuses, Noisy-OR composite stays at 0.09-0.12 (UNKNOWN range).

**Root cause:** Absence of adversarial intent prior layer. VIGÍA P2 evaluates
"how strong is the evidence" but not "how compatible is the pattern with
adversarial behavior." This is a design gap for a future Intent Amplifier Layer.

**CAIE Gap:** BREAK_003 should trigger CULTURAL_VS_TECHNICAL fracture (cultural
markers + C2 coherence), BREAK_010 should trigger OVERPERFECT_CONSISTENCY
fracture. Neither pattern is implemented in current CAIE rule set.

**Roadmap:** Intent Amplifier Layer as explicit module over CAIE score.

---

## Accuracy by Mode — Empirical Results (June 2026)

Two operational modes produce materially different accuracy profiles.
Both are documented here for Daubert transparency.

### LLM-assisted mode (Claude via MCP)

| Suite | Cases | Correct | Notes |
|-------|-------|---------|-------|
| Real corpus (VIGIA-REAL-001–010) | 10 | 10 | All verdicts match ground truth |
| Adversarial BREAK-001–010 | 10 | 10 | Epistemological manipulation suite |
| Epistemological boundary BREAK-011–016 | 6 | 6 | Aggregation, consensus, fabrication |
| False positive suite (FP-001–003) | 3 | 3 | Authorization context correctly read |
| False negative suite (FN-001–003) | 3 | 3 | Clean-surface attacks detected |
| Irreducible ambiguity (AMB-001–002) | 2 | 2 | ABSTAIN correctly emitted |
| **Total** | **34** | **34 (100%)** | |

### Fallback mode (scorer only, no LLM)

| Suite | Cases | Correct | Failure pattern |
|-------|-------|---------|-----------------|
| Canonical corpus | 62 | 62 | — |
| Real corpus (VIGIA-REAL-001–010) | 10 | 9 | REAL-007: SUSPICION instead of MALICE (L-008) |
| Adversarial BREAK-001–010 | 10 | 0 | Scorer emits UNKNOWN/ABSTAIN on all — conservative by design; LLM mode resolves correctly (L-007) |
| Epistemological boundary BREAK-011–016 | 6 | 2 | 4 structural failures (L-015, L-016, L-017) |
| False positive suite (FP-001–003) | 3 | 2 | FP-003: ABSTAIN instead of BENIGN |
| False negative suite (FN-001–003) | 3 | 0 | SUSPICION/NOISE instead of MALICE (L-018) |
| Irreducible ambiguity (AMB-001–002) | 2 | 0 | NOISE instead of ABSTAIN (L-012) |
| **Total** | **96** | **75 (78%)** | |

**Interpretation:** Fallback mode accuracy (78%) reflects the scorer's designed
scope — technically clear cases with structural anomalies. The 22% gap is not
random error: it is concentrated in four specific structural limitations (L-015
through L-018) documented below. In production, LLM-assisted mode is recommended
for all cases where those limitations apply.

**BREAK-001–010 note:** The 0/10 in fallback is not a crash — the scorer emits
UNKNOWN/ABSTAIN, which is Daubert-compliant (refusing to assert what cannot be
proven). The verdicts are conservative, not wrong in the harmful direction.

---

## L-015 — Directional Signal Aggregation Blindness

**Affects:** VIGIA-BREAK-011 | **Status:** Real limitation

**Description:** Twenty weak artifacts (raw_score=0.15, prior_trust=0.20) all
pointing to the same target produce score=0.059 → NOISE. The scorer treats
N directional signals as N independent events, not as a convergent pattern.

**Root cause:** The Noisy-OR composite formula correctly models independence,
but fails when artifacts are intentionally distributed (same ASN, same interval,
same target). There is no accumulation mechanism for directional coherence.

**Forensic implication:** Coordinated low-volume reconnaissance from botnets
or distributed actors will systematically score as NOISE in fallback mode.

**Workaround:** LLM mode resolves this via pattern-level reasoning. Scorer fix
would require an ASN/subnet clustering layer before Noisy-OR computation.

**Roadmap:** FW-006 — Directional Signal Accumulator module.

---

## L-016 — Trust-Weighted Consensus Failure

**Affects:** VIGIA-BREAK-012 | **Status:** Real limitation

**Description:** Four compromised sources (prior_trust=0.30) with high raw_score
override one reliable source (prior_trust=0.95) with low raw_score.
The scorer returns SUSPICION; expected BENIGN.

**Root cause:** The Noisy-OR composite weights by adjusted_score
(raw × spoofability × weight × trust) but does not apply the Bayesian
principle that a shared compromise vector collapses N sources into 1.
Four servers sharing the same compromised SSH key are one source, not four.

**Forensic implication:** An attacker who compromises multiple log sources with
the same credential can fabricate a false consensus that overrides a single
clean witness in fallback mode.

**Workaround:** LLM mode correctly identifies the shared compromise vector.
Scorer fix requires a source deduplication layer keyed on shared provenance.

**Daubert note:** This is the forensic principle of *fruit of the poisoned tree*
applied to log sources. Evidence derived from a single compromised channel is
one piece of evidence regardless of how many records it generates.

---

## L-017 — Corroboration Gate Over-Restriction

**Affects:** VIGIA-FN-001, VIGIA-FN-003, VIGIA-BREAK-015 | **Status:** Real limitation

**Description:** The MALICE corroboration gate (`n_artifacts ≥ 4 OR n_types ≥ 3`)
blocks MALICE even when one or two artifacts are individually conclusive
(raw_score × prior_trust > 0.80).

Examples:
- FN-003: fn003_03 (wrong parent process, raw=0.88, trust=0.9) is forensically
  irrefutable for process hollowing. The gate blocks MALICE because n=3, types=2.
- BREAK-015: biometric contradiction (raw=0.95, trust=0.85) is independently
  sufficient. Gate blocks because VPN artifact has trust=0.20.

**Root cause:** The gate was designed to prevent single-artifact MALICE
(L-008 class failure). It over-corrects by ignoring artifact-level confidence.

**Forensic implication:** High-confidence memory forensics and biometric evidence
are structurally disadvantaged relative to lower-confidence multi-artifact cases.

**Workaround:** LLM mode applies Peirce Thirdness reasoning that recognizes
irrefutable individual artifacts. Scorer fix: gate exception for
`max(raw_score × prior_trust) > 0.80`.

---

## L-018 — Non-Technical Context Opacity

**Affects:** VIGIA-FN-001, VIGIA-FN-002 | **Status:** Real limitation

**Description:** The scorer cannot reason about the forensic significance of
absent authorization (no change ticket) or confirmed user absence (HR vacation
record) when those facts are encoded in low-raw_score artifacts.

- FN-001: HR vacation record (raw=0.08, trust=0.95) makes the authenticated
  session impossible — but the scorer has no mechanism to make the vacation
  record *invalidate* the login artifact.
- FN-002: Absence of a change ticket (raw=0.08, trust=0.30) is the decisive
  signal — the tool is legitimate but unauthorized. The scorer cannot express
  "absence of authorization" as a positive malice signal.

**Root cause:** The scoring formula computes `raw_score × (1-spoofability) ×
weight × trust`. A raw_score of 0.08 on a contextual artifact produces near-zero
contribution regardless of trust. There is no mechanism for one artifact to
*contextually transform the interpretation* of another.

**Forensic implication:** LOLBAS (Living off the Land) attacks using legitimate
tools without authorization will systematically under-score in fallback mode.
Insider threat cases where the only signal is an HR record will return BENIGN.

**Workaround:** LLM mode applies the contextual transformation via abductive
reasoning. Scorer fix requires a contextual invalidation layer — an HR vacation
record at high trust should trigger an `identity_contradiction` flag that
multiplies the effective score of co-occurring login artifacts.

**Roadmap:** FW-007 — Contextual Invalidation Layer.


## L-XXX: Bundle Save TOCTOU Race (SEC-04)

**Status**: Documented, fix scheduled post-hackathon  
**Severity**: P0  
**File**: `vigia/core/bundle_builder.py`

The bundle hash is computed from in-memory content, not from disk. Between `f.write()` and hash computation, the file can be swapped via symlink attack or concurrent writer. No `fsync()`, `O_NOFOLLOW`, or atomic rename is used.

**Impact**: Chain-of-custody break under Daubert. In a courtroom scenario, opposing counsel could argue the bundle was tampered with after write.

**Mitigation**: Bundle is sealed with HMAC-SHA256 (H3) using `VIGIA_HMAC_KEY`. Without the key, tampering is detectable. However, the HMAC itself is computed from the same in-memory content, so a TOCTOU at write time affects both H2 and H3.

**Fix**: Atomic write with `tempfile.mkstemp()` → `fsync()` → `os.replace()`. Hash computed from disk after fsync. See Claude Code audit report 2026-06-09.

---

## L-019 — FALSE_FLAG_PATTERN fires on clean foreign-language machines

**Affects:** FP-CULTURAL-CLEAN.json | **Status:** Real limitation — fix deferred

**Description:** `FALSE_FLAG_PATTERN` in CAIE Rule 1 fires when
`avg_cultural > 0.5 AND avg_technical < 0.2`, regardless of whether
positive manipulation evidence exists. A machine with native Cyrillic
filenames, RU keyboard layout, and UTC+3 timezone, combined with a clean
memory/LSASS profile (low technical scores), satisfies the current condition
and receives MALICE verdict.

**Root cause:** The rule equates *absence of technical corroboration* with
*evidence of planted attribution*. These are not equivalent. The correct
condition requires: (1) confirmed malicious event (avg_technical > 0.5), plus
(2) positive manipulation evidence (timestomp, backdating, MFT inconsistency).

**Forensic implication:** Risk of false accusation based on language/origin.
A wrongful MALICE verdict against a legitimate foreign-language user.

**Sentinel case:** `FP-CULTURAL-CLEAN.json` — clean Russian-language machine.
Must always return NOISE/UNKNOWN. If it returns MALICE, this limitation is
actively causing false positives.

**Test coverage:** `tests/test_audit_false_flag.py` — 4 tests (xfail).
All 4 will transition to XPASS/PASSED when the fix is applied.

**Fix design (deferred post-hackathon):** Add `_has_manip` guard to Rule 1.
Requires adding explicit manipulation flags (`timestomp_detected`,
`backdating_detected`, `hollowed`, etc.) to 18+ canonical case JSON files
before the guard can be applied without regressions in the canonical corpus.
See `caie_false_flag_rule_fixed.py` for the corrected function.

**Roadmap:** Post-hackathon — update canonical corpus metadata, then apply
`_has_manip` guard with `_TECHNICAL_EVIDENCE_TYPES` and `_MANIPULATION_FLAGS`.
## L-020: Claude Code Mode Bundle Does Not Include Granular audit_trail

**Status:** Known limitation, documented.  
**Impact:** The ForensicBundle produced by Claude Code (Mode 3) contains integrity
hashes and decision traces but no per-tool-call audit_trail array with timestamps.
Fallback mode bundles (Mode 1) include full timestamped audit_trail entries.  
**Mitigation:** For the primary demo case (VIGIA-REAL-SRL-DMZ-FTP), a fallback
execution log with 6 timestamped events is available at:
`results/srl2018/VIGIA-REAL-SRL-DMZ-FTP_execution.jsonl`  
The amicus curiae at `results/srl2018/VIGIA-REAL-SRL-DMZ-FTP_amicus_curiae.md`
provides the complete tool call table for the Claude Code investigation.  
**Post-hackathon fix:** Wire the HMAC audit logger into the MCP tool execution
pipeline for Mode 3.
