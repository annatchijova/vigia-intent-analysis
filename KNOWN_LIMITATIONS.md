# VIGÍA — Known Limitations

**Version:** EBS v1 + P2 calibration | **Updated:** 2026-06-29
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

Limitations marked **[RESOLVED]** were present in earlier versions and have been
fixed. They are kept here for auditability and to explain the reasoning behind
design decisions in the commit history.

Limitations marked **[DESIGN DECISION]** are intentional behaviors that could
theoretically be changed but were chosen deliberately with documented rationale.

Limitations marked **[FIX DESIGNED]** have a documented fix but the fix has not
yet been deployed to the main codebase. Application is deferred post-hackathon.

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

**Affects:** VIGIA-REAL-002, VIGIA-REAL-007, VIGIA-REAL-010 | **Status:** Design decision

**Description:** Cases where all artifacts belong to fewer than 3 distinct
evidence types AND have fewer than 4 total artifacts cannot reach MALICE
regardless of individual raw scores. VIGÍA requires heterogeneous
corroboration for the strongest verdict.

**Affected cases (as of 2026-06-13):**

| Case | Artifacts | Types | Score | Verdict |
|------|-----------|-------|-------|---------|
| VIGIA-REAL-002 | 5 | 2 (`log_entry` + `file_timestamp`) | 0.244 | SUSPICION |
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

### L-012 — NOISE vs ABSTAIN Semantic Boundary

**Affects:** VIGIA-BEN-014 (Authorized Journalist / Tor) | **Status:** Design decision

**Definition enforced:**

- `NOISE`: null or near-null signal — absence of forensic relevance. Score < 0.05.
- `ABSTAIN`: epistemic indeterminacy under non-trivial competing hypotheses.
  Requires structural conflict, causal ambiguity, or insufficient discriminative
  evidence when signal IS present.

**Implication:** A case with score ~0.018 and no CAIE fractures is NOISE, not ABSTAIN.
ABSTAIN is not a catch-all for low scores — it is reserved for cases where evidence
exists but cannot discriminate between hypotheses.

**Forensic justification:** Inflating ABSTAIN with null-signal cases degrades
ABSTAIN-OH as a metric and weakens the epistemic gate's interpretability.

---

### L-015 — Directional Signal Aggregation Blindness

**Affects:** `VIGIA-BREAK-011` | **Status:** Real limitation

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

### L-016 — Trust-Weighted Consensus Failure

**Affects:** `VIGIA-BREAK-012` | **Status:** Real limitation

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
applied to log sources. Evidence derived from a single compromised channel is one
piece of evidence regardless of how many records it generates.

**LLM mode note (2026-06-14 empirical):** LLM mode also failed BREAK-012
(escalated to MALICE instead of BENIGN), confirming this limitation persists
in both modes.

---

### L-017 — Corroboration Gate Over-Restriction

**Affects:** `VIGIA-FN-001`, `VIGIA-FN-003`, `VIGIA-BREAK-015` | **Status:** Real limitation

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

### L-018 — Non-Technical Context Opacity

**Affects:** `VIGIA-FN-001`, `VIGIA-FN-002` | **Status:** Real limitation

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

---

### L-021 — Float Intermediates in Core Scoring Path

**Affects:** `vigia_scorer.py`, `vigia/tools/caie.py`, `caie_legacy_root.py` | **Status:** [RESOLVED]

**Description:** `_dround()` returned `float` and `_dsum()` returned `float`,
allowing IEEE 754 platform-dependent rounding in intermediate scoring values
(`effective_trust`, `adjusted_score`, `composite`, `final_score`).

**Resolution (2026-06-25, L-021 Phase 1 + Phase 2):**
- `_dround()` returns `decimal.Decimal` — internal algebra is Decimal throughout.
- `_dsum()` returns `decimal.Decimal` — handles Decimal, Fraction, int, float inputs.
- `evaluate()` output boundary uses `str()` serialization: `composite_score`,
  `probabilistic_score`, `fracture_bonus_applied`, `severity`, `spoofability_delta`,
  `ttp_confidences`, `raw_score`, `adjusted` — all `str`, never `float`.
- No `float()` at any output boundary.
- Tests updated for str comparisons. 188 passed, 0 failed, 6 xfailed.
- Commits: `1a16ee9` (Phase 1), `6bba3d7` (Phase 2).

**Prior mitigation (2026-06-14):** `math.log()`, `math.exp()`, and `0.95**k`
replaced with precomputed Fraction lookup tables in `vigia_scorer.py`.
Verdict thresholds converted to Fraction constants.

---

## Part II — CAIE Adversarial Limitations

### L-010 — Sensor Independence Not Verified

**Affects:** CAIE v2.0 adversarial suite (3/25 cases) | **Status:** Real limitation — roadmap v3.0

**Description:** CAIE assumes that different `source_tool` values indicate
independent evidence sources. It does not detect when multiple `source_tool`
values actually represent the same underlying sensor or acquisition pipeline.

**Affected adversarial cases:**
- `ASSUMPTION_BREAK_timestamp_comparability_AND_sensor_independence`
- `ASSUMPTION_BREAK_sensor_independence_AND_memory_ground_truth`
- `ASSUMPTION_BREAK_sensor_independence_AND_log_completeness`

**Root cause:** No native detection for sensor independence violations.
The system cannot distinguish between truly independent sources and multiple
outputs from a single compromised sensor.

**Attack scenario:** An attacker who compromises a single EDR sensor can fabricate
evidence appearing to come from multiple independent sources. CAIE v2.0 may produce
overconfident verdicts (SUSPICION instead of INCONCLUSIVE) in this scenario.

**Mitigation (v2.0):** When multiple evidence sources may originate from the same
compromised sensor, manual review is required. Document this explicitly in the
forensic report.

**Roadmap (v3.0):**
- `EvidenceDependencyGraph` with `sensor_fingerprint` tracking
- `AcquisitionContext.provenance_trust` field
- Collapse Decision Layer rules for sensor independence
- INCONCLUSIVE verdict for confirmed dependency detection

---

### L-014 — Soft Evidence Convergence Without Cross-Type Fractures

**Affects:** `BREAK_003`, `BREAK_008`, `BREAK_010` | **Status:** Real limitation

**Description:** Cases where adversarial patterns are encoded exclusively in
soft evidence types (log_entry/network_flow, spoofability 0.75-0.85) without
the multi-type artifact combinations required by CAIE fracture rules.

CAIE fracture detection requires specific type co-occurrence:
- LOG_VS_MEMORY: `log_entry` + `memory_process` artifacts required
- CULTURAL_VS_TECHNICAL: `cultural_marker` + technical artifacts required

Converted break cases with homogeneous soft evidence produce 0 CAIE fractures.
Without fracture bonuses, Noisy-OR composite stays at 0.09-0.12 (UNKNOWN range).

**Root cause:** Absence of adversarial intent prior layer. VIGÍA P2 evaluates
"how strong is the evidence" but not "how compatible is the pattern with
adversarial behavior." This is a design gap for a future Intent Amplifier Layer.

**CAIE Gap:** BREAK_003 should trigger CULTURAL_VS_TECHNICAL fracture (cultural
markers + C2 coherence), BREAK_010 should trigger OVERPERFECT_CONSISTENCY
fracture. Neither pattern is implemented in the current CAIE rule set.

**Roadmap:** Intent Amplifier Layer as explicit module over CAIE score.

---

## Part III — Infrastructure Limitations

### L-011 — Kernel-Level or Root Compromise

**Affects:** All analysis on live systems | **Status:** Permanent design boundary

**Description:** If an attacker has achieved kernel-level access or root
privileges on the host being analyzed — or on the host running VIGÍA
itself — the integrity of all evidence must be considered suspect. VIGÍA
operates entirely in userspace and has no mechanism to detect or compensate
for a compromised kernel, hypervisor, or firmware layer.

**Attack vectors:**

- **Rootkit / LKM injection:** A kernel module can intercept syscalls and
  return falsified data to any userspace process. File hashes, timestamps,
  process lists, and network state can all be spoofed transparently.
- **Direct kernel memory manipulation:** An attacker with root access can
  alter in-memory data structures without leaving traces in userspace-visible
  logs.
- **eBPF weaponization:** Malicious eBPF programs can intercept and modify
  data at the kernel-userspace boundary before VIGÍA reads it.
- **Hypervisor or firmware compromise:** At levels below the OS kernel, all
  host evidence is untrustworthy regardless of VIGÍA's controls.
- **VIGÍA host compromise:** If the machine *running* VIGÍA is under adversarial
  control, the entire pipeline — including chain-of-custody sealing, HMAC
  generation, and audit logs — is compromised. A sealed `ForensicBundle`
  produced under these conditions is cryptographically valid but evidentially
  worthless.

**Forensic implication:** VIGÍA's Daubert guarantees apply strictly to the
software layer. Any analysis on a live system where root compromise cannot be
excluded should be treated as **preliminary**.

**Detection boundary:** VIGÍA may detect artifacts *consistent with* a rootkit
(USN Journal gaps, MFT anomalies, CAIE process/network incongruences) but cannot
confirm kernel integrity from userspace.

**Mitigations (outside VIGÍA's scope):**
1. Acquire a forensic image with a hardware write blocker. Run VIGÍA against the
   image, not the live system.
2. Verify the integrity of the VIGÍA host before sealing any bundle.
3. For high-stakes cases, supplement with out-of-band kernel integrity checks
   (Secure Boot attestation, TPM PCR validation).
4. Document explicitly whether analysis was on a live system or a verified
   forensic image.

**Epistemological note:** No closed system can distinguish between "no evidence"
and "perfectly hidden attack" without an external trust anchor (TPM, hypervisor
attestation, hardware root of trust). This is a fundamental limit, not a bug.

**References:** NIST SP 800-86 §4.1; RFC 3227 §2.3; MITRE ATT&CK T1014 (Rootkit),
T1601 (Modify System Image).

---

### L-020 — Claude Code Mode Bundle Does Not Include Granular audit_trail

**Affects:** ForensicBundles produced in Claude Code mode | **Status:** Known limitation

**Description:** The ForensicBundle produced by Claude Code (Mode 2) contains
integrity hashes and decision traces but no per-tool-call `audit_trail` array
with timestamps. Fallback mode bundles (Mode 1) include full timestamped
`audit_trail` entries.

**Mitigation:** For the primary demo case (VIGIA-REAL-SRL-DMZ-FTP), a fallback
execution log with 6 timestamped events is available at
`results/srl2018/VIGIA-REAL-SRL-DMZ-FTP_execution.jsonl`. The Amicus Curiae at
`results/srl2018/VIGIA-REAL-SRL-DMZ-FTP_amicus_curiae.md` provides the complete
tool call table for the Claude Code investigation.

**Post-hackathon fix:** Wire the HMAC audit logger into the MCP tool execution
pipeline for Mode 2.

---

### L-022 — devil_advocate Validation Partially Architectural

**Affects:** Claude Code mode bundles | **Status:** Partially architectural — post-audit improvement

**Detail:** `verify_ebs_v1.py` R6_DEVIL_ADVOCATE check validates that all
MALICE/INTENT findings have `devil_advocate` populated in EBS-format bundles
(fallback mode / Mode 1). For Claude Code mode bundles (free JSON format),
enforcement is via CLAUDE.md instructions only — no code path prevents an agent
from emitting MALICE with empty `devil_advocate` in that mode.

**Post-hackathon fix:** Add a bundle schema validator that runs before Claude Code
mode bundle serialization, enforcing the same R6 check programmatically.

---

### L-023 — Bundle Save TOCTOU Race (SEC-04)

**Affects:** `bundle_builder.py` | **Status:** P0 — fix scheduled post-hackathon

**Description:** The bundle hash is computed from in-memory content, not from
disk. Between `f.write()` and hash computation, the file can be swapped via
symlink attack or concurrent writer. No `fsync()`, `O_NOFOLLOW`, or atomic rename
is used.

**Impact:** Chain-of-custody break under Daubert. In a courtroom scenario,
opposing counsel could argue the bundle was tampered with after write.

**Mitigation:** Bundle is sealed with HMAC-SHA256 (H3) using `VIGIA_HMAC_KEY`.
Without the key, tampering is detectable post-write. However, the HMAC is
computed from the same in-memory content, so a TOCTOU at write time affects
both H2 and H3.

**Post-hackathon fix:** Atomic write via `tempfile.mkstemp()` → `fsync()` →
`os.replace()`. Hash computed from disk after fsync. See Claude Code audit report
2026-06-09.

---

### L-024 — Forensic Mount Point Allowlist Includes Generic `/mnt`

**Affects:** `sift_orchestrator.py` PathGuard configuration; any case requiring
mounted disk images via `ewfmount`/`ntfs-3g` (e.g. VANKO-FALLBACK-002) | **Status:** Design decision

**Description:** `SIFTOrchestrator.__init__` configures `PathGuard` with an
`allowed_base_paths` list that includes the generic Linux mount point `/mnt`
in its entirety, rather than a scoped subdirectory dedicated to VIGÍA forensic
mounts. Introduced in commit `e32a3c4` to support disk images too large to
copy into the evidence directory.

**Root cause:** Forensic images mounted via `ewfmount` or `ntfs-3g` may land
at arbitrary subpaths under `/mnt` depending on operator choice and SIFT
tooling conventions. There is no fixed, predictable subdirectory to scope the
allowlist to without constraining legitimate workflows.

**Forensic implication:** Any path under `/mnt` passes PathGuard's base-path
check, regardless of whether it corresponds to evidence relevant to the active
case. PathGuard's other controls remain in force — symlinks, device files,
pipes, and sockets are still rejected, and paths are resolved before
comparison — so this does not permit directory traversal or non-regular-file
access. It does mean PathGuard cannot distinguish "this case's mounted
evidence" from "any other regular file mounted anywhere on the system."

**Mitigation:** SHA-256 verification against the expected hash, already
enforced at the manifest layer, provides a secondary integrity check
independent of PathGuard's base-path scoping — a manifest referencing the
wrong mounted file will fail hash verification even though PathGuard accepts
the path.

**Roadmap:** Scope the allowlist to a dedicated, VIGÍA-managed mount namespace
(e.g. a configurable `VIGIA_MOUNT_ROOT`) once SIFT integration defines a
standard mount convention.

---

### L-025 — Devil's Advocate (Eco's Razor) Has No Autonomous Generator for Unlabeled Evidence

**Affects:** All MALICE/INTENT findings from live autonomous investigations | **Status:** Identified 2026-06-19 — active work, not a permanently accepted limitation

**Description:** The `devil_advocate` field in MALICE/INTENT findings is only populated when
a human curator writes it by hand in the case JSON before the corpus is built
(`vigia/scripts/generate_execution_log.py:75`, via `case.get("devil_advocate", "")`).
No component of the live autonomous pipeline — not `vigia_agent.py`, not `scripts/run_case.py`,
not any of the three copies of `abductive_intent_engine.py` (`vigia/`, `vigia/core/`,
`vigia/tools/`) — generates this field from evidence at investigation time.

**Root cause:** The intended generator (`LLMBackend._gorgias_counter_hypothesis()` in
`vigia/core/llm_backend.py:160`, identical in `vigia/llm_backend_v2.py`) exists only as a
named stub — `return ""`. The surrounding class scaffolding (`_build_firstness_prompt`,
`_build_thirdness_prompt`, `_symbolic_abduction`, etc.) is present but not wired into any
live execution path. Neither file is imported anywhere in production code.

**Forensic implication:** For a genuinely autonomous investigation over new, unlabeled
evidence, VIGÍA currently has no mechanism to perform the abductive falsification step that
Rule R7 requires. The field is absent unless a human provides it in advance — which negates
the purpose of an autonomous Devil's Advocate in live incident response.

**Secondary gap — verifier does not flag this as critical:** `forensics/verify_ebs_v1.py`
`_check_devil_advocate()` only validates that the string is non-empty (rejects `""`, `"N/A"`,
`"null"`, `"None"`). It does not detect generic or repeated boilerplate text, and
`R6_DEVIL_ADVOCATE` is not among the conditions for `conformity_level = 3`
(`verify_ebs_v1.py:440`). A bundle can reach maximum conformity with an empty
`devil_advocate` on a MALICE finding — the check issues only a WARNING.

**Candidate solution path (designed, not yet implemented):**
`vigia/memory/case_pattern_library.py` and `vigia/inference/case_pattern_library.py`
(duplicates — pending reconciliation) already define `exclusion_signals` per `CasePattern` —
the benign alternative criteria that would rule out the malicious reading of the same
evidence. `sift_orchestrator.py` already references this library, suggesting a live
connection point. The proposed approach is to compose `devil_advocate` deterministically from
`exclusion_signals` and `confidence_basis` of the matched pattern at verdict time — no LLM
in the path — rather than writing a new free-text generator. Prerequisite: confirm whether
`case_pattern_library` usage in `sift_orchestrator.py` feeds the final verdict composition or
is limited to an earlier triage stage.

**Discovered by:** Claude (AI Collective Integrator) + Anna Tchijova, during live repository
audit, 2026-06-19. Surfaced while investigating a proposed Formal Policy Engine specification.

---

## Part IV — Resolved Limitations

### [RESOLVED] Normalization Schema Mismatch

**Was:** `vigia_scorer.py` had `_normalize_case()` defined but never called,
causing cases with legacy schema (`type`/`content`/`peirce_layer`) to produce
`adjusted_score=0.0` for all artifacts.

**Fixed in:** commit `4230281` — added `case = _normalize_case(case)` call at
the start of `_vigia_score()`.

---

### [RESOLVED] Acquisition Assurance Gate G1 Accepting Legacy Hashes

**Was:** `_compute_acquisition_assurance()` gate G1 accepted
`sha256:legacy_ART-001` as a valid hash because it only checked for the
`legacy_unknown_provenance` suffix, not for the `legacy_` prefix in general.

**Fixed in:** commit `4230281` — G1 now requires exactly 64 lowercase hex
characters after `sha256:`.

---

### [RESOLVED] Converter Injecting Uniform prior_trust=0.7

**Was:** `scripts/convert_legacy_cases.py` hardcoded `prior_trust: 0.7` for all
artifacts regardless of `peirce_layer`, overriding the normalizador's correct
per-layer values (FIRSTNESS=0.70, SECONDNESS=0.85, THIRDNESS=0.90).

**Fixed in:** commit `ae30787`.

---

### [RESOLVED] L-019 — FALSE_FLAG_PATTERN on Clean Foreign-Language Machines

**Was:** `FALSE_FLAG_PATTERN` in CAIE Rule 1 fired when
`avg_cultural > 0.5 AND avg_technical < 0.2`, regardless of whether positive
manipulation evidence existed. A machine with native Cyrillic filenames, RU
keyboard layout, and UTC+3 timezone combined with a clean memory/LSASS profile
(low technical scores) satisfied the condition and received a MALICE verdict.

**Root cause:** The rule equated *absence of technical corroboration* with
*evidence of planted attribution*. These are not equivalent. A legitimate
Russian-language machine is not a false-flag operation.

**Forensic principle enforced:**
```
Cyrillic filenames ≠ Russian threat actor
UTC+3 timezone    ≠ Russian threat actor
RU keyboard       ≠ Russian threat actor
```
The MALICE verdict for a false-flag belongs to the person *planting* the
evidence, not to the person whose cultural markers are being imitated.

**Fixed in:** CAIE Rule 1 now requires both: (1) a confirmed malicious event
(`avg_technical > 0.5`) and (2) positive manipulation evidence (timestomp,
backdating, MFT inconsistency). Cultural markers alone are insufficient to
infer false-flag operation.

**Validation:** `FP-CULTURAL-CLEAN.json` (clean Russian-language machine) returns
NOISE/UNKNOWN as expected. `FF-GENUINE-001.json` (real attack + planted attribution)
correctly returns MALICE.

**Test coverage:** `tests/test_audit_false_flag.py` — 4 tests, all passing.

---

### [RESOLVED] Ambiguous Encryption Case False Positive (VIGIA-REAL-005)

**Was:** VIGIA-REAL-005 (Ali Hadi Encrypt Them All) scored as MALICE when
expected SUSPICION, because `memory_process` with `raw_score=0.95` and
`spoofability=0.15` produced a high adjusted score without corroborating
heterogeneous evidence.

**Fixed in:** commit `ae30787` — heterogeneous corroboration gate
(`n_artifacts >= 4 OR n_unique_types >= 3`) now required for MALICE.

---

## Accuracy by Mode — Empirical Results (June 2026)

Two operational modes produce materially different accuracy profiles.
Both are documented here for Daubert transparency.

### LLM-assisted mode (Claude via MCP)

| Suite | Cases | Correct | Notes |
|-------|-------|---------|-------|
| Real corpus (VIGIA-REAL-001–010) | 10 | 10 | All verdicts match ground truth |
| Adversarial BREAK-001–010 | 10 | 10 | Epistemological manipulation suite |
| Epistemological boundary BREAK-011–016 | 6 | 5 | BREAK-014: PASS (LLMShield security block on prompt-injection input — correct behavior, not a reasoning failure). BREAK-012: FAIL — LLM overdetects (MALICE vs expected BENIGN); fallback correctly returns NOISE; see L-016. BREAK-011/013/015/016: PASS |
| False positive suite (FP-001–003) | 3 | 3 | Authorization context correctly read |
| False negative suite (FN-001–003) | 3 | 3 | Clean-surface attacks detected |
| Irreducible ambiguity (AMB-001–002) | 2 | 0 | VIGIA-AMB-001/002: NOISE in both fallback and LLM mode (expected ABSTAIN). L-012 confirmed in LLM mode |
| **Total** | **34** | **31 (91%)** | |

### Fallback mode (scorer only, no LLM)

| Suite | Cases | Correct | Failure pattern |
|-------|-------|---------|-----------------|
| Canonical corpus | 62 | 62 | — |
| Real corpus (VIGIA-REAL-001–010) | 10 | 9 | REAL-007: SUSPICION instead of MALICE (L-008) |
| Adversarial BREAK-001–010 | 10 | 0 | UNKNOWN/ABSTAIN on all — conservative by design (L-007) |
| Epistemological boundary BREAK-011–016 | 6 | 2 | 4 structural failures (L-015, L-016, L-017) |
| False positive suite (FP-001–003) | 3 | 2 | FP-003: ABSTAIN instead of BENIGN |
| False negative suite (FN-001–003) | 3 | 0 | SUSPICION/NOISE instead of MALICE (L-018) |
| Irreducible ambiguity (AMB-001–002) | 2 | 0 | NOISE instead of ABSTAIN (L-012) |
| **Total** | **96** | **75 (78%)** | |

**Interpretation:** The 78% figure above describes the pure mathematical scorer
in isolation (no LLM, no autonomous agent loop). It is NOT the production accuracy
of VIGÍA. The autonomous agent (`vigia_agent.py`) achieves 134/136 (98.5%) across
the same combined corpus — see Agent mode below. Fallback mode accuracy (78%)
reflects the scorer's designed scope — technically clear cases with structural
anomalies. The 22% gap is concentrated in four specific structural limitations
(L-015 through L-018). In production, LLM-assisted mode is recommended for all
cases where those limitations apply.

**BREAK-001–010 note:** The 0/10 in fallback is not a crash — the scorer emits
UNKNOWN/ABSTAIN, which is Daubert-compliant (refusing to assert what cannot be
proven). The verdicts are conservative, not wrong in the harmful direction.

### Agent mode (vigia_agent.py, batch run)

| Suite | Cases | Correct | Notes |
|-------|-------|---------|-------|
| Domain A + B + C combined | 136 | 134 | 2 xfail, documented under L-012 |

Reproduce: `python3 run_all_agent.py --timeout 90`

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
| L-008 | Homogeneous evidence cannot reach MALICE | REAL-002/007/010 | Design decision |
| L-009 | Spoofability floor under chain of custody | REAL corpus | Design decision |
| L-010 | Sensor independence not verified | CAIE adversarial 3/25 | Roadmap v3.0 |
| L-011 | Kernel/root compromise (live analysis) | All live analysis | Permanent boundary |
| L-012 | NOISE vs ABSTAIN semantic boundary | VIGIA-BEN-014 | Design decision |
| L-013 | *(gap — entry retired)* | — | — |
| L-014 | Soft evidence convergence without cross-type fractures | BREAK_003/008/010 | Real limitation |
| L-015 | Directional signal aggregation blindness | BREAK_011 | Real limitation |
| L-016 | Trust-weighted consensus failure | BREAK_012 | Real limitation |
| L-017 | Corroboration gate over-restriction | FN-001/003, BREAK_015 | Real limitation |
| L-018 | Non-technical context opacity | FN-001/002 | Real limitation |
| L-019 | FALSE_FLAG_PATTERN on clean foreign-language machines | FP-CULTURAL-CLEAN | **RESOLVED** |
| L-020 | Claude Code bundle lacks granular audit_trail | Mode 2 bundles | Known limitation |
| L-021 | Float intermediates in scoring path | vigia_scorer.py, caie.py | **RESOLVED** |
| L-022 | devil_advocate validation partially architectural | Mode 2 bundles | Post-audit improvement |
| L-023 | Bundle save TOCTOU race (SEC-04) | bundle_builder.py | P0 — fix scheduled |
| L-024 | Forensic mount allowlist includes generic /mnt | sift_orchestrator.py | Design decision |
| L-025 | Devil's Advocate has no autonomous generator for unlabeled evidence | All live MALICE/INTENT findings | RESOLVED — see L-026 |
| L-026 | Devil's Advocate generator wired in; 1 pre-fix corpus bundle flagged | VIGIA-REAL-SRL-DMZ-FTP | **RESOLVED** / documented exception |
| L-027 | AbductiveIntentEngine call site in VigiaPipeline used wrong signature since birth | `vigia/pipeline/pipeline.py::run_full()` | **RESOLVED** 2026-06-22 — zero submission impact |
| L-028 | Golden Rule LOG_VS_MEMORY requires metadata["verdict"] convention | `vigia/tools/caie.py` | **RESOLVED** 2026-06-24 |
| L-029 | DARVO false flag victim signal dilution — agent fallback blind; scorer lacks false_flag verdict type | VIGIA-KIWI-001/002/003 | **IN_PROGRESS** — FW-009 DARVO detector |
| — | Normalization schema mismatch | vigia_scorer.py | **RESOLVED** |
| — | Gate G1 accepting legacy hashes | caie.py | **RESOLVED** |
| — | Uniform prior_trust=0.7 in converter | convert_legacy_cases.py | **RESOLVED** |
| — | Ali Hadi encryption FP (VIGIA-REAL-005) | VIGIA-REAL-005 | **RESOLVED** |
| L-033b | Fixed gamma for windows_event_log | Scoring pipeline | **RESOLVED** |
| L-034 | Multi-source corroboration sub-threshold aggregation | MAGNET-2022/2020-WINDOWS | Documented |
| L-035 | event_log mapped to log_entry in forensic_adapter | forensic_adapter.py | **RESOLVED** |
| L-036 | Pipeline RAW hypothesis override for UNDETERMINED | vigia_agent.py RAW path | **RESOLVED** |
| L-037 | ARTIFACT_RELIABILITY not propagated to CAIE | iOS/Android forensics | PENDING |
| L-038 | Dynamic gamma for windows_event_log | Scoring pipeline | IMPLEMENTED |

---

*VIGÍA — SANS FIND EVIL Hackathon 2026*
*Author: Anna Tchijova | AI Collective: Claude, Kimi, Gemini, DeepSeek, Qwen, Grok, ChatGPT*
*License: Apache 2.0 | Repository: github.com/annatchijova/vigia-intent-analysis*

---

### L-026 — Devil's Advocate Generator Wired In; 1 Pre-Fix Corpus Bundle Flagged by Stricter Verifier

**Status:** RESOLVED (generation gap) / DOCUMENTED (legacy bundle exception). Fixed 2026-06-19, POST HACKATHON.

**What was broken:**
`devil_advocate` in `caie_analysis` was only ever populated when a human curator
wrote it by hand into a case JSON during corpus construction. No autonomous
code path (`vigia_agent.py`, `vigia/pipeline/pipeline.py`,
`vigia/core/bundle_builder.py::build_bundle()`) generated it from evidence.
The intended generator, `LLMBackend._gorgias_counter_hypothesis()`, was an
unimplemented stub (`return ""`). The verifier (`forensics/verify_ebs_v1.py`)
only checked for an empty string and did not treat absence as a blocking
failure for `conformity_level == 3`.

**Fix applied (POST HACKATHON, 2026-06-19):**
- `vigia/core/devil_advocate_gen.py` (new): deterministic composer, no LLM in
  the path. Uses `missing_signals` from `CasePatternResult` when reachable;
  falls back to an explicit, honest statement otherwise — today, both sealing
  paths use the fallback, since `CasePatternLibrary` matching currently lives
  only in `sift_orchestrator.py` and is not yet wired into either path
  (tracked as follow-up below, not yet done).
- Both `bundle_builder.py::build_bundle()` and `pipeline.py` now call the
  composer when `caie_analysis["verdict"]` is `MALICE`/`INTENT` and no
  `devil_advocate` was already supplied.
- `forensics/verify_ebs_v1.py::_check_devil_advocate()` now returns CRITICAL
  for any MALICE/INTENT bundle missing `devil_advocate`, blocking
  `conformity_level == 3`. Verified by direct unit invocation against three
  constructed cases (missing / present / not-applicable).

**Corpus impact, measured, not assumed (2026-06-19):**
Full scan of every true EBS v1 bundle in the repository (`bundle_version` +
`decision_trace` present; legacy report-format files excluded) found
**1 bundle** sealed before this fix with a MALICE/INTENT verdict and no
`devil_advocate`:

- `results/srl2018/VIGIA-REAL-SRL-DMZ-FTP_bundle.json` (verdict: MALICE)

**If you re-run `verify_ebs_v1.py` against this specific file, it will
correctly report a CRITICAL R7 failure.** This is the verifier doing its job
on a bundle sealed under an earlier, less strict version of the same check —
not a regression. The file predates this fix and has not yet been
regenerated. Every other bundle in the repository, including the entire
submitted hackathon corpus, was unaffected.

**Follow-up (not yet done):**
1. Regenerate `VIGIA-REAL-SRL-DMZ-FTP_bundle.json` with the current pipeline.
2. Wire `sift_orchestrator.py`'s `CasePatternLibrary.missing_signals` into one
   or both sealing paths so the rich composition already written in
   `devil_advocate_gen.py` is actually reachable.

**Discovered by:** Claude (Collective Integrator) + Anna Tchijova, live repo
audit, 2026-06-19. Reviewed by the Collective (Grok, Gemini, Kimi, ChatGPT)
same date.

**Second update — same day, 2026-06-19, after implementing the fix:**

All three sealing paths now compose `devil_advocate` deterministically for
MALICE/INTENT verdicts, each with its own accurate `scope_note`:

- `vigia/pipeline/pipeline.py`
- `vigia/core/bundle_builder.py::build_bundle()`
- `vigia_agent.py::_seal_bundle()` (agent audit-trail format) — verified
  end-to-end against `VIGIA-REAL-VANKO`:
  `pipeline_results.abduction.devil_advocate` now contains a populated,
  scope-accurate structure (`devil_advocate_source:
  deterministic_no_pattern_data_available`).

`compose_devil_advocate_struct()` gained a `scope_note` parameter so each
call site states its own real architecture instead of sharing one generic
string that was only accurate for two of the three paths. Confirmed by
direct `diff`: `sift_orchestrator.py` as imported by `vigia_agent.py` is a
deliberate compatibility shim without `CasePatternLibrary` — see
`EXECUTION_MODES.md` for the full map.

Test bundles for all three stages of this fix (before / partial / after)
are preserved, not deleted, at `results/r7_test/` —
`VIGIA-REAL-VANKO-R7TEST` (before), `R7TEST2` (3 of 4 files patched),
`R7TEST3` (all 4 patched, working).

**Still open, not done today:**
1. `results/srl2018/VIGIA-REAL-SRL-DMZ-FTP_bundle.json` — the one
   pre-existing corpus bundle flagged earlier — has not yet been
   regenerated with the fixed pipeline.

**Numbering note:** the original Formal Policy Engine specification
(2026-04-30) calls this rule R7. The implemented check in
`forensics/verify_ebs_v1.py` is labeled `R6_DEVIL_ADVOCATE` (line 453). This
is a drift between the original spec's numbering and the as-built code,
confirmed 2026-06-19, not a different requirement — both refer to the same
Eco's Razor / devil's-advocate invariant. Left as-is rather than renumbering
working code; documenting the mismatch here instead.

**Third update — same day, 2026-06-19, regeneration attempt for
VIGIA-REAL-SRL-DMZ-FTP:**

Attempted to regenerate the one flagged corpus bundle
(`results/srl2018/VIGIA-REAL-SRL-DMZ-FTP_bundle.json`) with the R7 fix
applied. Stopped before touching the real file after a schema-test run
revealed the regeneration path was wrong.

Confirmed: `vigia_agent.py`'s CLI (`--evidence ... --case-id ... --output
...`) always produces the agent audit-trail schema (family 2 — see
`EXECUTION_MODES.md`), regardless of input evidence. Verified twice
independently — once against `VIGIA-REAL-VANKO`, once against
`VIGIA-REAL-SRL-DMZ-FTP` — both produced `audit_trail`/`pipeline_results`,
never `bundle_version`/`decision_trace`/`caie_analysis`.

The real bundle (EBS v1 schema, `verdict: MALICE`, `confidence: 0.67`,
sealed 2026-06-10T19:28:16Z, git commit `c21a819`) was almost certainly
produced by an interactive Claude Code + MCP investigation session, not by
running `vigia_agent.py` as a one-line CLI command. Three project documents
(`SUBMISSION_COMPLIANCE.md:389-396`, `PROMPTS_REALCASES_CLAUDE.md:9-16`,
`README.md:462-465`) each describe a different `--output` path, and none
matches where the file actually lives — discrepancies confirmed, not yet
resolved.

**Conclusion:** regenerating this bundle with `devil_advocate` requires
repeating the original interactive MCP investigation, not a terminal
command. Deferred to a dedicated session. The real bundle was not modified
— a schema-test run was sent to a disposable path
(`results/r7_test/srl_dmz_schema_test.json`) and inspected before any write
to the real file.

---

## L-027 — AbductiveIntentEngine Call Site Used Wrong Signature Since Birth

**Affects:** `vigia/pipeline/pipeline.py::run_full()` | **Status:** **[DESIGNED]** 2026-06-22, POST HACKATHON — import path resolved; semantic integration pending

**Description:** `VigiaPipeline.run_full()` called `AbductiveIntentEngine().infer(posterior=, signals=, evidence_graph=, vision_metadata=)` — a signature that exists in none of the three extant copies of the class. All copies define `infer_habit(artifacts, phase)` (or `infer(artifacts, phase)` in the root copy). The result was also treated as a `dict` via `.get()`, but all copies return `AbductiveResult` (dataclass). The call always raised `AttributeError: 'AbductiveIntentEngine' object has no attribute 'infer'`, caught by the surrounding `try/except`, falling back to `consistency_score=1.0`.

**Root cause:** The call site was written aspirationally before the engine API was finalized. The bug was present since the file was created (commit `84e8bfd`, 2026-05-06) and never triggered a test failure because `VigiaPipeline` was not used by any submission entry point.

**Submission impact:** **Zero.** Confirmed by tracing all three submission entry points in `SUBMISSION_COMPLIANCE.md` (`vigia_agent.py`, `scripts/run_case.py→vigia_sift_bridge.py::reason_with_llm`, `vigia/scripts/evaluate_detector.py`): none import `VigiaPipeline`. `generate_release_bundle.py` is a packaging script with no runtime imports. `generate_execution_log.py` uses `SemioticDetectorV2`/`aggregate_evidence`/`decide`, not `VigiaPipeline`.

**Secondary effect of the bug:** `consistency_score` was hardcoded to `1.0` on every call, which suppressed the Disonancia Semántica rule (`posterior > 0.7 and consistency_score < 0.5 → ABSTAIN`). Any case routed through `VigiaPipeline` (not the submission path) would never trigger ABSTAIN via this gate.

**Fix applied (POST HACKATHON, 2026-06-22):**

1. **Canonical engine created:** `vigia/inference/abductive_intent_engine.py` — merged from `vigia/core/` as base, which had: (a) `H_XF_001` fix for EXFILTRATION hypothesis ID collision, (b) DAUBERT comments on `cost`/`coverage_score` fields, (c) 3-tuple Ockham sort key `(cost, -coverage, len(required_artifacts))`. Only change from base: import fixed from bare `from visible_variables import` → `from vigia.tools.visible_variables import`.

2. **Import updated:** `pipeline.py:89` now imports from `vigia.inference.abductive_intent_engine` (matching the `vigia_namespace_shim.py:95` target that was already registered but pointing to a non-existent path).

3. **Call site reverted to documented stub:** `pipeline.py::run_full()` now explicitly sets `consistency_score=1.0` and `abductive_result=None` with a comment referencing L-027. No adapter is active. The previous adapter (commit `86f6777`, reverted) was found to produce output constant per phase (vocabulary mismatch: `SignalOutput.tool_name` vs `HYPOTHESIS_TEMPLATES.required_artifacts`), which would have forced ABSTAIN on every high-posterior case via `consistency_score=0.0 < 0.5` — worse than the original silent failure.

**Known limitation (not a bug, documented behavior):** Until a translation layer exists (`SignalOutput.tool_name` → template artifact name), the abductive engine cannot reason meaningfully from pipeline signals. The stub preserves the known pre-existing state (`consistency_score=1.0`, Disonancia Semántica inactive) rather than introducing a false sense of functionality.

**Future work:** Design and implement `SignalOutput` → `Artifact` translation layer with:
- Explicit mapping table: `tool_name` → `artifact_type` (e.g., `"audit_network"` → `"lateral_movement_auth"`, `"calculate_shannon_entropy"` → `"timestamp_uniformity"`)
- Real `category` from signal metadata (not hardcoded `_VarCat.PROCESS`)
- Real `observed_at` from signal timestamp
- `consistency_score` as `Fraction(coverage_score, 100)` (no floats; `cost` remains `int`)

**Triplication resolved:** `vigia/tools/abductive_intent_engine.py`, `vigia/core/abductive_intent_engine.py`, and `vigia/abductive_intent_engine.py` (root) remain in place as archived originals — not deleted, not imported by any active path after this fix. The `.bak` file at `vigia/core/abductive_intent_engine.py.bak` captures the pre-fix state.

**Discovered by:** Anna Tchijova + Claude + Kimi, live repo audit, 2026-06-22.

**Audited by:** Kimi (Moonshot AI), 2026-06-22. P0 found in adapter (output constant per phase, ABSTAIN over-trigger); P1 in documentation status (RESOLVED → DESIGNED); P2 in float reintroduction; P2 in hardcoded category; P3 in empty `observed_at`.

---

## L-019b — Agent Runtime Bundles vs. Canonical EBS v1 Schema

**Affects:** `forensics/verify_ebs_v1.py` on `vigia_agent.py` output  
**Status:** By design — not a bug

`vigia_agent.py` produces runtime agent bundles with SHA-256 chain of custody
(Evidence SHA-256 → Bundle SHA-256). These are NOT the same as canonical EBS v1
bundles (`AV-001_bundle.json`, `ADMIN-001_bundle.json`), which have the full
structured schema (`bundle_version`, `evidence_graph`, `decision_trace`, etc.).

`forensics/verify_ebs_v1.py` validates the canonical EBS v1 schema only.
For agent bundles, use the SHA-256 verification printed by the agent:
  `sha256sum -c results/real/${CASE}_bundle.json.sha256`

**Impact:** Zero — verdicts, z-scores, and chain of custody are unaffected.

## L-028 — Golden Rule LOG_VS_MEMORY Requires metadata["verdict"] Convention

**Affects:** `vigia/tools/caie.py::detect_fractures()` | **Status:** [RESOLVED] 2026-06-24, POST HACKATHON — commit 588956b

**Description:** The `LOG_VS_MEMORY` Golden Rule (structural fracture that forces `MALICE` regardless of probabilistic score) only fires when artifacts carry explicit `metadata["verdict"]` fields. When artifacts are built without this convention (direct `Artifact()` construction, upstream tools that don't emit `verdict` for negative findings), the rule does not engage and the case falls through to pure Noisy-OR probabilistic fusion. In this path, a high-spoofability log artifact (spoofability=0.85) can have its contribution depressed enough that the final verdict collapses to `NOISE`, even when containing a high-severity IoC (e.g., connection to a known C2 IP).

**Impact:** This is an exploitable gap (T-5, "inverse credibility anchor"). An attacker can use a structurally irrefutable artifact (memory process, low spoofability=0.15) as an "innocence anchor" to neutralize a trivially forgeable artifact (log entry, high spoofability=0.85) that carries the real evidence of compromise. The memory artifact does not need to be forged — its mere presence without explicit `verdict` disables the Golden Rule.

**Root cause:** The Golden Rule was designed with the assumption that all upstream tools emit `metadata["verdict"]` consistently. This assumption is not enforced by the `Artifact` dataclass nor by the ingestion pipeline. The rule's logic requires `tech_verdicts` to contain exactly `{"NOISE"}` — impossible when `verdict` is `None`.

**Known workarounds (none fully satisfactory):**
- Ensure all upstream tools emit `metadata["verdict"]` for every artifact (convention-dependent, not enforceable).
- Manually inject `verdict` fields during case construction (error-prone, not scalable).

**Planned fix:** Infer `verdict` from artifact structure when `metadata["verdict"]` is absent. Approaches under evaluation:
- Semantic keyword matching (same pattern as `NARRATIVE_POISONING_DETECTED`) — rejected due to fragility.
- Structural field analysis (presence/absence of `dst_ip`, `network_connections` in metadata) — under investigation, requires corpus analysis.
- `adjusted_score` thresholding with existing `composite` thresholds (0.5/0.2) — rejected as introducing arbitrary numeric thresholds.

**Resolution:** `_extract_assertions()` added as a pure semantic translation
layer between raw artifact metadata and Rule 2. LOG_VS_MEMORY now fires on
`log_claims_outbound_connection` (dst_ip/dest_ip present in log metadata) AND
`memory_shows_no_network_activity` (no dest_ip/source_ip/network_connections
in memory metadata). No metadata["verdict"] field required. PID overlap
between log and memory artifacts modulates severity (0.95 with overlap,
0.75 without) but does not gate fracture existence. Fix applied symmetrically
to both vigia/tools/caie.py and vigia/tools/caie_legacy_root.py.

**Test:** `test_red_team_anchor_bypass` in `vigia/tests/adversarial/test_spoofability_correlation_attack.py` confirms the gap. Status: `FAIL_T5_CONFIRMED`.

**Discovered by:** Anna Tchijova + Claude + Kimi, red team audit, 2026-06-22.

**Audited by:** Kimi (Moonshot AI), 2026-06-22.

---

## L-029 — DARVO_FALSE_FLAG_VICTIM_SIGNAL_DILUTION

**Affects:** Agent fallback (deterministic, no LLM) — full failure; Scorer mode — partial
**Status:** IN_PROGRESS — DARVO pattern detector implementation in pipeline (FW-009)
**Severity:** HIGH
**Discovered:** 2026-06-24 via VIGIA-KIWI trilogy stress test
**Test cases:** `VIGIA-KIWI-001`, `VIGIA-KIWI-002-ZAPALLO-POV`, `VIGIA-KIWI-003-AT-POV`

**Description:** In DARVO false flag cases where the real aggressor is the
complainant, agent fallback emits `NO_SEMIOTIC_ANOMALY`. Scorer mode partially
resolves: KIWI-003 (victim POV, `prior_trust=0.8`, verified evidence) reaches
MALICE at 87% confidence. However, `expected_verdict: false_flag` is not a
supported verdict type in scorer mode — the correct semantic classification
cannot be emitted even when the scoring threshold is crossed.

KIWI-002 (aggressor POV, `prior_trust=0.3`, unverified complainant testimony)
correctly reaches ABSTAIN at 40% confidence — low trust propagates correctly
through the Noisy-OR pipeline. This is the system working as designed.

**Architectural note — VERDICT vs QUADRIPARTITE STATE:**

VERDICT and QUADRIPARTITE STATE are distinct layers. KIWI-001 emits
`VERDICT=SUSPICION` (score 0.2696 crosses the SUSPICION threshold) while
`QUADRIPARTITE STATE=ABSTAIN` (confidence 54% insufficient for action). This
is correct behavior: signal exists but evidence is insufficient for a reliable
verdict. These two outputs are not contradictory — they operate at different
abstraction layers of the pipeline.

**Observed behavior by mode and case:**

| Case | Agent fallback | Scorer VERDICT | Scorer confidence | Quadripartite | Assessment |
|------|---------------|----------------|-------------------|---------------|------------|
| KIWI-001 (combined) | NO_SEMIOTIC_ANOMALY | SUSPICION | 54% | ABSTAIN | Signal present, insufficient for action |
| KIWI-002 (aggressor POV) | NO_SEMIOTIC_ANOMALY | SUSPICION | 40% | ABSTAIN (stability 30%) | Correct — low trust propagates |
| KIWI-003 (victim POV) | NO_SEMIOTIC_ANOMALY | MALICE | 87% | — | Correct direction; false_flag unsupported |

**Root cause (two distinct gaps):**

1. **Agent fallback — cross-artifact blindness:** The Noisy-OR composite formula
   treats each artifact as an independent event. The DARVO pattern is a
   relationship between bundles (role inversion across KIWI-002 and KIWI-003),
   not a property of any single artifact. Without cross-bundle Peircean Thirdness
   reasoning, the inversion is structurally invisible.

2. **Scorer mode — verdict vocabulary gap:** `vigia_scorer.py` verdict set is
   `{NOISE, UNKNOWN, SUSPICION, INTENT, MALICE, ABSTAIN}`. `false_flag` is a
   semantic classification that describes *who* is the aggressor relative to
   *who* filed the complaint — a relational verdict that requires role attribution
   context outside the artifact bundle schema. MALICE 87% on KIWI-003 is the
   correct directional output given the current vocabulary.

**Concrete failure (KIWI-001, agent fallback):**

| Artifact | Type | raw_score | prior_trust | Fallback contribution |
|----------|------|-----------|-------------|----------------------|
| KIWI-001-A01 | cultural_marker | 0.3 | 0.8 | Low — below SUSPICION threshold |
| KIWI-001-A03 | document_visual | 0.5 | 0.8 | Medium — insufficient for INTENT |
| KIWI-001-A04 | file_metadata | 0.6 | 0.8 | Medium — no cross-artifact anchor |
| KIWI-001-A02 | log_entry | 0.7 | 0.8 | Strong — single-type cap applies (L-008) |

The cross-artifact signal invisible to the scorer: the complainant who accuses
the victim of symbolic threats simultaneously operates a surveillance server
(`log_entry` 0.7). The inversion of roles is the signal. Four independent data
points in fallback; one DARVO pattern in LLM mode.

**Forensic implication:** DARVO false flag cases will systematically produce
`NO_SEMIOTIC_ANOMALY` in agent fallback. Even when scorer mode reaches MALICE
on the victim's bundle, the `false_flag` classification cannot be emitted —
the analyst receives an unsigned verdict without role attribution.

**LLM-assisted mode:** Resolves via Peircean Thirdness cross-artifact analysis
across the full trilogy. `infer_intent` applied to KIWI-002 + KIWI-003 as paired
bundles identifies: complainant maintains active surveillance infrastructure
(`prior_trust=0.3` claims vs `prior_trust=0.8` verified server logs) while
filing harassment allegations. Thirdness: DARVO, Carnegie authority inversion,
false-flag staging. Verdict emittable: MALICE with role-inversion notation.

**Workaround (fallback):** Submit KIWI-002 and KIWI-003 as a paired bundle review.
The `prior_trust` asymmetry (0.3 vs 0.8) with inverted role attribution is
visible to a human analyst comparing both bundles. Document in the forensic
report: DARVO detection requires LLM mode; fallback result is incomplete, not
wrong in the harmful direction.

**Roadmap:** Intent Amplifier Layer (FW-009) — DARVO pattern detector as
post-scorer module over paired bundles. Inputs: cross-bundle role attribution
fields, `prior_trust` asymmetry, temporal context (`contact_attempts_by_actor_b:
0` over 3 years), honeypot access logs. Output: `DARVO_PATTERN` fracture feeding
back into CAIE before final verdict emission. Secondary roadmap item: extend
verdict vocabulary to include `false_flag` as a relational verdict type.

**Discovered by:** Anna Tchijova, 2026-06-24, via VIGIA-KIWI trilogy stress test.

---


## L-029 — Formal Specification of Arbitration Contract Between Probabilistic Inference and Structural Contradiction Reasoning

**Status:** [OPEN] 2026-06-25, POST HACKATHON — design gap, not implementation bug

**Description:**

VIGÍA is a hybrid forensic reasoning engine, not a pure probabilistic classifier.
Two distinct epistemic questions coexist by design:

- The scoring layer answers: "How compatible is the evidence set with malicious intent?"
- CAIE answers: "Are there logical contradictions between artifacts?"

These are different questions. The current behavior (structural fractures take
precedence over probabilistic score) is correct. The gap is that this precedence
rule exists implicitly in code but not as a formal system contract.

**Current implicit rule:**
```
if structural_verdict == MALICE:
    final_verdict = MALICE  # regardless of probabilistic_verdict
```

**What is missing:**
A formal specification stating which fracture types carry structural authority,
under what conditions, and why. Without this, the precedence rule can be broken
by a future refactor without any test catching it (since the behavior is correct
by implementation, not by contract).

**Fractures with current structural authority (from code):**
- LOG_VS_MEMORY
- MEMORY_VS_DISK
- TIMELINE_PARADOX / EFFECT_BEFORE_CAUSE
- NARRATIVE_POISONING_DETECTED

**Proposed resolution:**
Document Axiom A1 formally:

> A structural fracture constitutes evidence of probatory set inconsistency
> and takes precedence over probabilistic estimation when the fracture passes
> CAIE validity criteria (_STRUCTURAL_MALICE_TYPES). This is not an override;
> it is the application of a different epistemic standard: logical impossibility
> supersedes statistical likelihood.

This makes the arbitration rule readable by a Daubert judge without requiring
them to read the source code.

**Not a bug.** Do not "fix" by introducing a weighted fusion function
(e.g. final_score = p + fracture_weight). Such functions require empirical
calibration and introduce thresholds that are scientifically indefensible
without a calibration corpus. The current design is more defensible precisely
because it separates the two reasoning modes rather than blending them.

**See also:** B-013 (low raw_score triggers structural fracture — related
design question)

---

## L-030 — Two Distinct Bundle Sealing Paths Produce Incomparable bundle_hash Values

**Status:** [DOCUMENTED] 2026-06-26, POST HACKATHON — architectural distinction, not a bug

**Description:**

VIGÍA has two legitimate bundle sealing paths that produce structurally different
bundles, both containing a `bundle_hash` field:

1. **Lightweight CLI bundle** (`vigia/core/bundle_builder.py::build_bundle()`):
   Seals scorer output for standalone use, junior analysts, and chatbot integration
   (OpenWebUI/Ollama). Input: dict from `_vigia_score()`. Contains: verdict,
   score, CAIE fractures, peirce_chain, quadripartite_state.

2. **Full forensic bundle** (`vigia/models/ebs.py::ForensicBundle.seal()`):
   Seals the complete pipeline output for SIFT integration. Input: ForensicBundle
   object with evidence_graph, decision_trace, policy_spec, system_state,
   abduction_trace. Covers significantly more content.

The two `bundle_hash` values are **not comparable** — they are computed over
different content and represent different forensic artifacts. This is intentional
and correct: the two paths serve different audiences and integration contexts.

**What is missing:**

A `bundle_schema_version` or `bundle_type` field (e.g. `"scorer_standalone"` vs
`"pipeline_full"`) that allows a recipient to identify which sealing contract
applies without reading the full bundle structure.

**Not a bug.** Do not unify the two paths — they serve different purposes.
The fix, when desired, is to add a `bundle_type` discriminator field to both
schemas so consumers can distinguish them unambiguously.

**See also:** #8 from the post-hackathon coverage report (CLI vs API hash
divergence, confirmed 2026-06-23).

---

## L-031 — EBS_V1_VERIFY_INCOMPATIBLE_WITH_FALLBACK_BUNDLES

**Status:** [DOCUMENTED] 2026-06-28, POST HACKATHON — architectural mismatch, not a bug

**Severity:** MEDIUM
**Mode affected:** Agent fallback (deterministic, no LLM)
**Discovered:** 2026-06-28 via Magnet CTF corpus verification

**Description:**

`forensics/verify_ebs_v1.py` requires the following fields to be present in a
bundle: `bundle_version`, `timestamp`, `evidence_graph`, `decision_trace`,
`policy_spec`, `actions`, `system_state`, `integrity`.

Agent fallback bundles generated by `vigia_agent.py` without an LLM backend do
not produce these fields — they produce a simplified bundle schema containing
`audit_trail`, `pipeline_results`, and `narrative` only.

**Result:** `verify_ebs_v1.py` returns **Level 0 Non-compliant** on all fallback
bundles, even when the forensic analysis is valid and the H4 EBS verify reports
PASS.

**Mitigation:** Use H4 EBS verify (bundle_sealer internal check) for fallback
bundles. Full EBS v1 verification requires LLM-assisted mode (Claude Code + MCP
or Ollama), which produces the complete `ForensicBundle` schema.

**Affected bundles:** All `results/real/*_bundle.json` generated without LLM
backend.

**Not a bug.** Do not add stub fields to fallback bundles to satisfy the
verifier — that would fabricate provenance data that was never collected.
The correct fix, when desired, is a `bundle_type` discriminator (see L-030)
that allows `verify_ebs_v1.py` to select the appropriate verification contract
before checking field presence.

**See also:** L-030 (two bundle sealing paths), L-019b (agent runtime bundles
vs. canonical EBS v1 schema).

---

## L-032 — False Negative: Agent Fallback on Raw Windows Disk Evidence (E01)

**Status:** [FIX DESIGNED] 2026-06-29, POST HACKATHON
**Severity:** P1
**Mode affected:** Autonomous agent fallback (`vigia_agent.py`) — raw Windows disk evidence
**Discovered:** 2026-06-29 | Case: `VIGIA-MAGNET-2022-WINDOWS`

**Description:**

The autonomous agent produces `UNDETERMINED` on raw Windows disk evidence when artifacts
are extracted manually and passed as a directory. Root cause:
`_build_orchestrator_kwargs()` maps `*.evtx` files to the `event_stream` parameter, but
`SIFTOrchestrator.analyze()` routes `event_stream` to `MetabolicProfiler`, not to
`EventLogCorrelator`. The correct parameter is `event_logs`.

As a result, `EventLogCorrelator` receives no input and produces `z=0`, while the
actual composite score from direct invocation is **19/20** (343 PASS_THE_HASH chains,
6 BRUTE_FORCE_SUCCESS, Event 25 ProcessTampering).

**Claude Code / MCP mode result on the same artifacts:** `MALICE` — correctly identified
via direct EVTX parsing. Two independent confirmed chains: account backdoor + RDP
pre-staging, `SubjectUserSid=S-1-5-18` throughout.

**Forensic implication:** Agent fallback is not reliable for raw Windows disk evidence.
Use Claude Code / MCP mode for E01 investigations until B-032 is resolved.

**Fix designed:** Change `event_stream` to `event_logs` in `_build_orchestrator_kwargs()`
for `.evtx` files. Tracked as **B-032**.

**Workaround:** Use Claude Code / MCP mode (Mode 2) for raw Windows disk evidence.
Domain C accuracy figures for raw E01 are not reliable until B-032 is deployed.

---

## L-033 — Gamma Calibration Suppresses High-Confidence Event Log Signals (FN Risk)

**Status:** [DESIGN DECISION — under review] 2026-06-29, POST HACKATHON
**Severity:** P2
**Mode affected:** All modes — `apply_artifact_reliability()` in scoring pipeline
**Discovered:** 2026-06-29 | Case: `VIGIA-MAGNET-2022-WINDOWS`

**Description:**

`apply_artifact_reliability()` applies a fixed `gamma=0.60` discount factor to all
`event_log` artifact class signals. A signal with `z=3.2` (e.g., 343 PASS_THE_HASH
chains, `composite_score=19/20`) is downscaled to `z=1.920`, falling below the MALICE
threshold.

**Root cause:** Event logs are classified as more falsifiable than memory forensics or
MFT artifacts — an attacker with SYSTEM-level access can clear or manipulate them.
The `gamma=0.60` discount reflects this epistemic downgrade. The discount is applied
uniformly regardless of the number of corroborating events or the composite score.

**Forensic implication:** High-confidence aggregate event log evidence — e.g., 343
independent PASS_THE_HASH chains with no contradicting signals — is suppressed to the
same degree as a single, weakly-corroborated log entry. This creates false negative
risk precisely in cases where the event log evidence is strongest.

**Why it is architecturally intentional:** The fixed gamma prevents the scoring engine
from over-trusting event logs in cases where log fabrication is the attack vector (see
L-001, `BREAK_006`). Removing the discount entirely would increase FP risk in
false-flag scenarios.

**Why it requires review:** The fixed gamma does not account for high-confidence
aggregate evidence. A calibrated gamma that scales with `n_corroborating_events` or
`composite_score` would preserve the FP protection while reducing FN risk for
well-evidenced chains. Adjusting the fixed value without calibration data risks
shifting the FP/FN tradeoff incorrectly.

**Fix path:** Requires calibration data across expanded real-world corpus before
adjusting `gamma`. Tracked for review post-corpus-expansion. Do not change `gamma`
without empirical validation on at least 20 real-case event log signals with known
ground truth.

**Workaround:** For investigations where event log evidence is high-confidence and
aggregate (composite_score ≥ 18/20, n_events ≥ 50), document the gamma suppression
explicitly in the report's Known Limitations section and note the pre-discount z-score
alongside the post-discount value.

---

## L-033b — Fixed gamma for windows_event_log [RESOLVED]

**Status:** RESOLVED — commit fix B-035
**Severity:** P1
**Mode affected:** All modes — scoring pipeline
**Discovered:** 2026-06-29

**Description:**

Event log gamma was 0.60 for all `event_log` types including Windows EVTX. This
treated Windows Event Logs (binary format with checksums, structurally harder to
tamper) identically to generic syslog entries (plaintext, trivially editable).

**Fix applied:**

Added `windows_event_log` type with `gamma=0.70` and a separate CAIE profile:
- `spoofability=0.55` (down from 0.85 for generic `log_entry`)
- `base_weight=0.25`

This reflects the structural integrity difference between binary EVTX (checksummed,
requires specialized tools to modify) and plaintext syslog (editable with any text
editor).

**See also:** L-033 (the broader gamma calibration design question remains open for
non-Windows event log types).

---

## L-034 — Multi-source corroboration does not compensate for sub-threshold individual signals

**Status:** Documented — fix requires aggregation layer redesign
**Severity:** P2
**Mode affected:** All modes — scoring pipeline
**Discovered:** 2026-06-29

**Description:**

Two signals at `z=1.96` and `z=2.24` do not combine to produce a MALICE verdict.
The scorer requires at least one signal above the threshold independently. There
is no aggregation mechanism that allows multiple sub-threshold signals to combine
into a supra-threshold composite.

**Cases affected:** `VIGIA-MAGNET-2022-WINDOWS`, `VIGIA-MAGNET-2020-WINDOWS`

**Forensic implication:** Cases where all individual signals are below the MALICE
threshold but multiple independent signals point to the same conclusion will cap
at SUSPICION or INTENT. This is conservative by design (prevents noise accumulation
from producing false MALICE) but creates false negative risk when multiple
well-evidenced chains each fall just below the threshold.

**Fix path:** Requires aggregation layer redesign — a mechanism to detect
directional coherence across sub-threshold signals without collapsing the
independence assumption that protects against noise accumulation.

---

## L-035 — event_log type mapped to log_entry profile in forensic_adapter [RESOLVED]

**Status:** RESOLVED — commit fix B-035
**Severity:** P1
**Mode affected:** All modes — forensic_adapter.py CAIE profile mapping
**Discovered:** 2026-06-29

**Description:**

`forensic_adapter.py` mapped `event_log` to `log_entry` (syslog generic profile,
`spoofability=0.85`). Windows EVTX is a binary format with internal checksums —
structurally much harder to tamper than plaintext syslog. The generic mapping
applied an inappropriate spoofability penalty that suppressed event log signal
contributions in the CAIE pipeline.

**Fix applied:**

Added `windows_event_log` to:
- `forensic_adapter.py` mapping (event_log → windows_event_log for Windows evidence)
- CAIE profiles (`spoofability=0.55`, `base_weight=0.25`)
- Gamma tables in `_math_utils.py` (`gamma=0.70`)

---

## L-036 — Pipeline RAW hypothesis override for UNDETERMINED results [RESOLVED]

**Status:** RESOLVED — commit fix L-036
**Severity:** P1
**Mode affected:** Agent fallback — `vigia_agent.py` RAW evidence path
**Discovered:** 2026-06-29

**Description:**

When `SIFTOrchestrator` returns `UNDETERMINED` but signals show `z>3`, the agent
now upgrades the hypothesis deterministically based on signal criticality:

| Condition | Hypothesis |
|-----------|------------|
| `n_critical >= 2` | `MALICIOUS_INTENT_DETECTED` |
| `n_critical >= 1` | `INTENT_DETECTED` |
| `n_high >= 2` | `SUSPICION_DETECTED` |

Exit code 3 was added for INTENT/SUSPICION (previously only `0`=clean, `1`=malice,
`2`=error).

**Root cause:** The original z-score threshold for hypothesis override was `z>5.0`,
which was impossible because `Z_CLIP_MAX=5.0` (signals are clipped to this maximum).
Fixed to `z>2.0`.

---

## L-037 — Acquisition metadata not propagated to CAIE [RESOLVED]

**Status:** RESOLVED (2026-06-30)
**Severity:** P1
**Mode affected:** Mode 1 (RAW) — all evidence types
**Discovered:** 2026-06-30

**Description:**

None of the 15 SIFT modules that produce `SignalOutput` included acquisition
metadata (`acquisition_tool`, `acquisition_hash`, `acquisition_timestamp`,
`examiner_id`, `write_blocker_used`) in their signal metadata. CAIE's NIST SP
800-86 §4.3 validator found all 5 fields absent and degraded `base_trust` to the
floor (0.10) on every artifact, collapsing composite scores.

**Fix applied:** Centralised injection at the gamma convergence point in
`sift_orchestrator.py`. `acquisition_hash` (sha256-prefixed) and
`acquisition_timestamp` (ISO-8601) are derived from `ChainOfCustody.records[0]`.
Three remaining fields (`acquisition_tool`, `write_blocker_used`, `examiner_id`)
must be declared explicitly via CLI flags — absent fields degrade trust honestly.

**Result:** CAIE composite score improved 226% (0.0027 → 0.0088) on MAGNET-2020-WINDOWS.
SIFT signals now pass 2/4 CAIE gates (VERIFIED tier) instead of 0/4 (NONE tier).

**Design constraint — single acquisition per case (L-037a):**

The current fix assumes a single acquisition per case (`self.chain` is singular —
one `ChainOfCustody` instance per `SIFTOrchestrator`). The first ACQUIRE record's
hash and timestamp are propagated to ALL signals uniformly.

If a future case mixes acquisitions from different tools (e.g., disk with FTK Imager +
memory with DumpIt + Android with Cellebrite), this model is no longer valid: each
artifact needs its own acquisition metadata, not case-level metadata. This would
require per-module acquisition metadata in each `SignalOutput`, not centralised
injection at the orchestrator.

For the current pipeline scope (single evidence source per case), the centralised
model is correct. If multi-source cases are needed, migration path:
1. Each SIFT module declares its own acquisition metadata in `SignalOutput.metadata`
2. The orchestrator's centralised injection becomes a fallback for modules that
   don't declare their own
3. The merge order (`{_acq_meta, **sig.metadata}`) already handles this: a module's
   own metadata takes precedence over the centralised fallback.

### L-037b — ARTIFACT_RELIABILITY not propagated to CAIE [PENDING]

`ios_forensics.py` and `android_forensics.py` define
`ARTIFACT_RELIABILITY=Fraction(70,100)`. The value is included in signal metadata
but `forensic_adapter.py` sets `base_trust=1.0` fixed, ignoring the reliability
discount from the signal metadata. Signals from mobile platforms are treated with
the same base trust as fully verified desktop forensic artifacts.

**Fix path:** `forensic_adapter` should read `artifact_reliability` from signal
metadata and apply it as a trust modifier.

---

## L-038 — Dynamic gamma for windows_event_log [IMPLEMENTED]

**Status:** IMPLEMENTED — Kimi design
**Severity:** P2
**Mode affected:** All modes — scoring pipeline
**Discovered:** 2026-06-29

**Description:**

Dynamic gamma formula for `windows_event_log`:

```
gamma = base + (1-base) * corroboration
```

where `corroboration = chain_factor * score_factor`.

Implemented as `apply_artifact_reliability_dynamic()` in
`vigia/sift/_math_utils.py`. Requires `composite_score` in event_log signal
metadata.

**Result:** EVENT_LOG z-score raised from `1.920` to `2.240–3.040` depending
on chain count, reflecting the corroborative strength of multiple independent
event chains.

---

## L-039 — PCAP parser requires tshark in PATH

**Status:** DOCUMENTED
**Severity:** P2
**Mode affected:** All modes — evidence ingestion
**Discovered:** 2026-06-30

**Description:**

The pcap parser (`vigia/sift/pcap_parser.py`) depends on `tshark` (Wireshark CLI)
being available in `PATH`. If tshark is not installed, pcap evidence will fail with
`FileNotFoundError` (fail-loud, not silent).

**Known constraints:**
- Requires `tshark` ≥ 3.0 (tested with 4.2.2).
- Install: `sudo apt install tshark` (Debian/Ubuntu) or `sudo dnf install wireshark-cli` (Fedora).
- Safety cap: maximum 50,000 packets per file. Larger files are truncated with a warning.
- Timestamps se truncan a segundo (epoch int) — sub-second jitter no es capturado por el parser, lo cual puede afectar la detección de beaconing con intervalos sub-segundo.
- No soporta pcap sobre stdin ni streams en vivo — solo archivos en disco.
- tshark subprocess tiene timeout de 120 segundos — pcaps extremadamente grandes pueden excederlo.

---
