# VIGÍA — Known Limitations

**Version:** EBS v1 + P2 calibration | **Updated:** 2026-07-08
**Applies to:** `github.com/annatchijova/vigia-intent-analysis`
**Corpus baseline:** 167/199 label-blind deterministic detection (see `README.md`
for the segmentation and doctrine notes behind this figure).

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

**Silent-fallback sub-case (confirmed 2026-07-13):** When
`VIGIA_LLM_BACKEND=anthropic` is configured but `ANTHROPIC_API_KEY` is not
set, `LLMBackend._try_anthropic()` raises `TypeError` (SDK auth validation)
which is caught internally and the call silently falls through to Ollama at
`http://127.0.0.1:11434`. If Ollama is running, `reason_with_llm` appears
to work but is actually answered by the local Ollama model, not by Claude.
If Ollama is also down, the empty-response error is returned.
Since 2026-07-13 the output field `llm_backend` reflects the actual
responding backend (`"ollama"` not `"anthropic"`) and a `backend_warn`
field is included when degradation occurred (`vigia/config.py:LLMBackend`).

**Important architectural constraint — see L-055:** Setting
`VIGIA_LLM_BACKEND=anthropic` without `ANTHROPIC_API_KEY` cannot be fixed
by any code change in VIGÍA. The Claude Code Max plan session is not
exposed to Python subprocesses. An independent `ANTHROPIC_API_KEY` is
required for the Anthropic path.

**Forensic implication:** Fallback mode is deliberately conservative.
Cases with strong semantic intent signals but weak structural anomalies
will score as SUSPICION rather than MALICE. This is epistemologically
correct: without semantic analysis, the system cannot infer intent from
names and narrative context alone.

**Configuration:** Set `VIGIA_LLM_BACKEND=ollama` with a local model
(tested: `hermes3:8b`, `deepseek-r1:8b`) or `VIGIA_LLM_BACKEND=anthropic`
with a valid `ANTHROPIC_API_KEY`.

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

### L-016 — Trust-Weighted Consensus: No Shared-Provenance Deduplication

**Status:** Real limitation (architectural, code-verified 2026-07-11)

> **Methodological note (correction 2026-07-11):** this entry previously
> listed a specific `case_id` under "Affects" as if it were evidence of the
> limitation. A test case (N=1) proves that THAT case fails — not the
> frequency or severity of the general class — exactly the kind of
> overgeneralization that VIGÍA's Daubert doctrine exists to prevent.
> Rewritten to assert only the architectural fact verified in code; the
> empirical behavior of the individual case lives in "Accuracy by Mode"
> below, marked N=1, not generalizable.

**Description:** The composite (`vigia_scorer._vigia_score`, Noisy-OR style
aggregation weighted by `raw_score × (1−spoofability) × weight × trust`)
treats each artifact as an independent source. No mechanism detects N
artifacts sharing the same underlying provenance (e.g., the same compromised
credential or log-forwarding pipeline) and collapses them into one effective
source before scoring. R4-3's tail decay (`vigia_scorer.py:771+`) dedupes by
**collection domain** (D1–D5 band) — a different axis; it does not close
this specific gap (shared-credential/session identity).

**Root cause (verified against code, 2026-07-11):** no source-deduplication-
by-shared-provenance function exists in `vigia_scorer.py` or
`vigia/tools/caie.py`.

**Forensic implication (deductive from the verified mechanism, not an
empirical rate claim):** if N sources share one compromised credential, the
composite counts them as N independent corroborating sources rather than 1 —
*fruit of the poisoned tree* applied to log sources.

**Workaround:** LLM mode can reason about a shared compromise vector
contextually (see Accuracy by Mode for the single illustrative case) — this
is not a substitute for a scorer-level fix.

**Roadmap:** source-deduplication-by-shared-provenance layer keyed on
`provenance_chain` overlap or shared credential/session id.

---

### L-017 — MALICE Corroboration Gate Has No Single-Artifact-Confidence Exception

**Status:** Real limitation (architectural, code-verified 2026-07-11)

> **Methodological note (correction 2026-07-11):** same as L-016 — the
> specific numerical examples (raw/trust of individual artifacts) were
> moved to "Accuracy by Mode", marked N=2, not generalizable.

**Description:** The MALICE corroboration gate (`vigia_scorer.py`, R4-3 v2,
~line 1141) requires one of three branches to open: cross-domain evidence
with mass (`n_domains≥2` AND `n_artifacts≥4` OR `n_types≥3`), hard-mass
(`≥3` hard types OR `≥4` hard artifacts, spoofability≤0.30), or per-artifact
cost (`≥4` D5-hard/media artifacts). **None of the three branches has an
exception for a single artifact whose individual `raw_score × prior_trust`
is very high** — a lone, highly confident artifact cannot reach MALICE
regardless of its evidentiary weight.

**Root cause:** the gate was designed to block single-artifact MALICE; it
does not distinguish "single weak artifact" from "single forensically
decisive artifact."

**Forensic implication (deductive):** evidence classes typically
concentrated in one or two artifacts (e.g., memory-forensics process
hollowing, biometric contradiction) are structurally disadvantaged relative
to multi-artifact/multi-type cases, independent of per-artifact confidence.

**Workaround:** LLM mode can apply Peircean reasoning that recognizes an
individually decisive artifact — no equivalent scorer-level exception exists.

**Roadmap:** evaluate a `max(raw_score × prior_trust) > threshold` exception
branch — requires calibration against a labeled corpus (pattern variants,
not the 2 illustrative cases in Accuracy by Mode) before adoption.

---

### L-018 — No Cross-Artifact Contextual Reinterpretation in the Composite

**Status:** Real limitation (architectural, code-verified 2026-07-11)

> **Methodological note (correction 2026-07-11):** same as L-016/L-017 —
> the case-specific examples were moved to "Accuracy by Mode", marked N=2,
> not generalizable. Additionally, it was verified (not assumed) that the
> ATMS mechanism mentioned in the `vigia_scorer.py` docstring does not
> close this gap: see "Root cause" below.

**Description:** the composite scores each artifact independently via
`raw_score × (1−spoofability) × weight × trust`; there is no mechanism for
one artifact's content to reinterpret or invalidate another's contribution.
The closest existing feature, the ATMS-inspired `AssumptionTracker`
(`vigia/core/integrity_constraints.py`), invalidates **structural**
assumptions (e.g., triggered by `TEMPORAL_CAUSALITY_VIOLATION`) — verified
(2026-07-11, grep) that `AssumptionTracker`/`invalidate_assumption` is never
called from `vigia_scorer.py`: it is not wired into the composite, so it
does not let a low-`raw_score`-but-high-significance contextual artifact
(e.g., an HR record, an authorization ticket) transform the interpretation
of a co-occurring technical artifact.

**Root cause:** no contextual-invalidation layer connects non-technical
context artifacts to the malice contribution of co-occurring technical
artifacts in the scoring formula.

**Forensic implication (deductive):** cases whose only distinguishing signal
is a non-technical fact (confirmed absence via HR record, absence of a
change ticket) cannot be up-weighted by the composite regardless of that
fact's forensic decisiveness.

**Workaround:** LLM mode can apply abductive reasoning to perform this
contextual transformation manually — no scorer-level mechanism exists.

**Roadmap:** FW-007 — contextual invalidation layer wiring non-technical
context artifacts (HR, authorization/ITSM) into the composite as
multiplicative modifiers on co-occurring technical artifacts. Requires a
labeled corpus of pattern variants before calibration — not started.

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

### L-023 — Bundle Save TOCTOU Race (SEC-04) [RESOLVED 2026-07-03]

**Affects:** `bundle_builder.py` | **Status:** RESOLVED — Tanda A (TRIAGE 2026-07-03), tag `pre-tanda-a-20260703-134624`

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

**Fix applied (2026-07-03, Tanda A — A5):** exactly the scheduled design:
`BundleBuilder.save()` now writes via `tempfile.mkstemp()` in the target
directory → `fsync()` → `os.replace()` (atomic publish — no half-written
bundle is ever visible), the returned hash is computed FROM DISK after the
replace, and a memory-vs-disk hash divergence raises RuntimeError. Orphan
tempfiles are cleaned on failure and the previous bundle is left intact if
the write fails. Tests: `tests/test_tanda_a_triage.py::TestA5AtomicBundleSave`
(3, including simulated fsync failure).

---

### L-024 — Forensic Mount Point Allowlist Includes Generic `/mnt` [RESOLVED 2026-07-03]

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


**Fix applied (2026-07-03, Tanda B — prefixes approved by the operator):**
generic `/mnt` removed from the static allowlist. Only existing forensic
mount points enter, expanded at orchestrator construction from the approved
prefixes `/mnt/vigia_*`, `/mnt/ewf*` (ewfmount) and `/mnt/evidence`
(symlinks excluded). Any other mount requires `VIGIA_EVIDENCE_DIR` — the
documented contract — and its rejection is VISIBLE (PathGuard unanalyzed
signal, F7). Tests: `TestL024MntPrefixes` (3).

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

**Sample-size caveat (added 2026-07-11, applies to FP-001–003, FN-001–003,
and the BREAK-012/015 rows within BREAK-011–016):** these row counts (N=3,
N=3, N=6) describe exactly those specific test artifacts — they are
reproducible single/few-case illustrations of the mechanisms in L-016/L-017/
L-018, NOT a statistically powered sample of the general pattern class
(e.g., "authorization-context cases" or "trust-weighted-consensus cases").
A quantitative failure-rate claim for any of those patterns (e.g., "VIGÍA
fails on X% of unauthorized-tool cases") would require generating additional
pattern variants first — same pattern, different parameters (timing,
volume, channel count, confidence levels). **This is tracked as pending
work below, not a conclusion already reached.**

**Pending work — pattern-variant corpus (not started):** generate variants
for L-016 (different channel counts / trust deltas), L-017 (different
artifact types / confidence levels), L-018 (different absence types —
HR/ITSM/other), then re-measure per-pattern accuracy before making any rate
claim in this document.

### Agent mode (vigia_agent.py, batch run)

| Suite | Cases | Correct | Notes |
|-------|-------|---------|-------|
| Domain A + B + C combined | 136 | 134 | 2 xfail, documented under L-012 |

Reproduce: `python3 run_all_agent.py --timeout 90`

---

## Summary Table

*L-016/L-017/L-018 (marked below): "Affects" previously pointed to a specific
`case_id` as if it were evidence of the limitation — corrected 2026-07-11
(see the methodological note in each entry). The single-case illustrative
example (N=1/2) lives in "Accuracy by Mode", not here.*

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
| L-016 | Trust-weighted consensus — no shared-provenance dedup | Composite scoring path* | Real limitation |
| L-017 | Corroboration gate — no single-artifact-confidence exception | Composite scoring path* | Real limitation |
| L-018 | No cross-artifact contextual reinterpretation | Composite scoring path* | Real limitation |
| L-019 | FALSE_FLAG_PATTERN on clean foreign-language machines | FP-CULTURAL-CLEAN | **RESOLVED** |
| L-020 | Claude Code bundle lacks granular audit_trail | Mode 2 bundles | Known limitation |
| L-021 | Float intermediates in scoring path | vigia_scorer.py, caie.py | **RESOLVED** |
| L-022 | devil_advocate validation partially architectural | Mode 2 bundles | Post-audit improvement |
| L-023 | Bundle save TOCTOU race (SEC-04) | bundle_builder.py | **RESOLVED** 2026-07-03 (atomic write); extended 2026-07-06/07 to vigia_agent.py primary path and models/ebs.py (B-080) |
| L-024 | Forensic mount allowlist includes generic /mnt | sift_orchestrator.py | **RESOLVED** 2026-07-03 (forensic prefixes) |
| L-025 | Devil's Advocate has no autonomous generator for unlabeled evidence | All live MALICE/INTENT findings | RESOLVED — see L-026 |
| L-026 | Devil's Advocate generator wired in; 1 pre-fix corpus bundle flagged | VIGIA-REAL-SRL-DMZ-FTP | **RESOLVED** / documented exception |
| L-027 | AbductiveIntentEngine call site in VigiaPipeline used wrong signature since birth | `vigia/pipeline/pipeline.py::run_full()` | **RESOLVED** 2026-06-22 — zero submission impact |
| L-028 | Golden Rule LOG_VS_MEMORY requires metadata["verdict"] convention | `vigia/tools/caie.py` | **RESOLVED** 2026-06-24 |
| L-029 | DARVO false flag victim signal dilution — agent fallback blind; scorer lacks false_flag verdict type (was briefly co-numbered with L-051; see L-051's numbering note) | VIGIA-KIWI-001/002/003 | **IN_PROGRESS** — FW-009 DARVO detector |
| — | Normalization schema mismatch | vigia_scorer.py | **RESOLVED** |
| — | Gate G1 accepting legacy hashes | caie.py | **RESOLVED** |
| — | Uniform prior_trust=0.7 in converter | convert_legacy_cases.py | **RESOLVED** |
| — | Ali Hadi encryption FP (VIGIA-REAL-005) | VIGIA-REAL-005 | **RESOLVED** |
| L-033b | Fixed gamma for windows_event_log | Scoring pipeline | **RESOLVED** |
| L-034 | Multi-source corroboration sub-threshold aggregation | MAGNET-2022/2020-WINDOWS | Documented |
| L-035 | event_log mapped to log_entry in forensic_adapter | forensic_adapter.py | **RESOLVED** |
| L-036 | Pipeline RAW hypothesis override for UNDETERMINED | vigia_agent.py RAW path | **RESOLVED** |
| L-037 | Acquisition metadata not propagated to CAIE | iOS/Android forensics | **RESOLVED** 2026-06-30 (see entry body; L-037b closed by Tanda B PR-B2) |
| L-038 | Dynamic gamma for windows_event_log | Scoring pipeline | IMPLEMENTED |
| L-039 | PCAP parser requires tshark in PATH | Evidence ingestion | Documented |
| L-041 | android SMS analysis limited to encrypted-app keywords | android_forensics.py | PENDING |
| L-044 | MetabolicProfiler/BehavioralFingerprint not run in Mode 1 | inference/*.py | Documented (design) |
| L-045 | `mcp` not installable in minimal CI (PyJWT conflict) | requirements-ci.txt | Documented (CI) |
| L-046 | Scorer non-monotonicity (M2-1/M2-2) | vigia_scorer.py | **RESOLVED** (B-081) |
| L-047 | Bundle canonicalization v1 type collisions (Canon v2) | core/canonicalize.py | **RESOLVED** (B-082/R3-2) |
| L-048 | Tool-log chain tail truncation (chain_tip_sha256) | core/tool_log_chain.py | **RESOLVED** (R3-5) |
| L-049 | Spoofable-type flood saturates to MALICE (R4-3) | vigia_scorer.py | Mitigated (B-091 tail decay + gate v2; mobile-band residual closed by B-092) |
| L-050 | Non-finite fail-closed on value/z_score/confidence × 4 impls | ebs_v1.py, signal_contract.py | **RESOLVED** (B-083/B-083b) |
| L-051 | Formal specification of arbitration contract (Axiom A1) — renumbered from shared L-029 | Scoring/CAIE precedence | [OPEN] — design gap, not a bug |
| L-032 | Agent fallback FN on raw Windows E01 | VIGIA-MAGNET-2022-WINDOWS | **RESOLVED** (B-032) |
| L-055 | Anthropic API and Claude Code Max plan are separate auth products — no bridge from subprocess | vigia/config.py:LLMBackend | DOCUMENTED — product boundary, no code fix possible |

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

**Secondary effect of the bug:** `consistency_score` was hardcoded to `1.0` on every call, which suppressed the Disonancia Semántica (semantic dissonance) rule — its name in code (`posterior > 0.7 and consistency_score < 0.5 → ABSTAIN`). Any case routed through `VigiaPipeline` (not the submission path) would never trigger ABSTAIN via this gate.

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


## L-051 — Formal Specification of Arbitration Contract Between Probabilistic Inference and Structural Contradiction Reasoning

**Status:** [OPEN] 2026-06-25, POST HACKATHON — design gap, not implementation bug

**Numbering note (2026-07-08):** this entry originally shared the ID L-029 with
the unrelated DARVO false-flag finding (`DARVO_FALSE_FLAG_VICTIM_SIGNAL_DILUTION`,
discovered 2026-06-24). The two are independent findings that happened to be
assigned the same number. Renumbered to **L-051** — the chronologically later of
the pair (2026-06-25 vs. 2026-06-24) — so each has a unique, citable ID. DARVO
keeps **L-029**. No cross-references to the old shared "L-029 — Formal
Specification..." title were found in `BUGS_PENDIENTES.md`/`BUGS_PENDIENTES_EN.md`
or elsewhere in the repository (confirmed by repo-wide search 2026-07-08); the
only other file referencing "L-029" is `WHAT_IS_NEXT.md:140`, which is about the
DARVO detector (FW-009) and correctly continues to point at L-029, unchanged.

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

## L-032 — False Negative: Agent Fallback on Raw Windows Disk Evidence (E01) [RESOLVED]

**Status:** [RESOLVED] — B-032 fixed. Originally [FIX DESIGNED] 2026-06-29, POST HACKATHON.
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

**Fix applied (B-032, RESOLVED):** `_build_orchestrator_kwargs()` now maps `.evtx`
files to `event_logs` (routed to `EventLogCorrelator`) instead of `event_stream`
(which `SIFTOrchestrator.analyze()` routes to `MetabolicProfiler`). `EventLogCorrelator`
now receives the parsed events and the composite score is no longer suppressed to `z=0`.
See B-032 in `BUGS_PENDIENTES(_EN).md`.

**Residual note:** `MetabolicProfiler` / `BehavioralFingerprint` still do not run in
agent Mode 1 because no `event_stream` is generated — this is the separate, documented
design limitation L-044, not a regression of this fix.

**Historical workaround (pre-fix):** Claude Code / MCP mode (Mode 2) was recommended for
raw Windows disk evidence. With B-032 deployed, agent fallback correctly parses EVTX.

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

### L-037b — ARTIFACT_RELIABILITY not propagated to CAIE [RESOLVED 2026-07-03]

`ios_forensics.py` and `android_forensics.py` define
`ARTIFACT_RELIABILITY=Fraction(70,100)`. The value is included in signal metadata
but `forensic_adapter.py` sets `base_trust=1.0` fixed, ignoring the reliability
discount from the signal metadata. Signals from mobile platforms are treated with
the same base trust as fully verified desktop forensic artifacts.

**Fix path:** `forensic_adapter` should read `artifact_reliability` from signal
metadata and apply it as a trust modifier.


**Fix applied (2026-07-03, Tanda B PR-B2):**
`ForensicAdapter.signal_to_caie_artifact` now propagates the reliability each
SIFT engine declares (`metadata["artifact_reliability"]`, Fraction-string) as
CAIE `base_trust`, clamped to [0,1]; absent/unparseable → 1.0 (previous
behavior). A forgeable event log no longer weighs the same as a memory dump
in CAIE. Verified: comparative scorer run over the 198 scored cases → 0
verdict flips, 0 score moves (this path feeds the orchestrator→CAIE flow,
not the scorer's JSON adapter). Tests: `TestL037bBaseTrustPropagation` (5,
ratio-based to isolate propagation from CAIE's own acquisition decays).
This removes one of the two preconditions of B-041b (CAIE→verdict feedback);
the remaining one is multi-layer artifacts (B-052-P2).

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
- Timestamps are truncated to whole seconds (epoch int) — sub-second jitter is not captured by the parser, which can affect detection of beaconing with sub-second intervals.
- No support for pcap over stdin or live streams — on-disk files only.
- The tshark subprocess has a 120-second timeout — extremely large pcaps can exceed it.

---

## L-041 — android_forensics.py: SMS content analysis limited to encrypted-app keyword matching [PENDING]

**Status:** PENDING — documented limitation
**Severity:** P1 — false negative risk on transaction/coordination content
**File:** `vigia/sift/android_forensics.py::_analyze_sms()`
**Discovered:** 2026-06-30, case VIGIA-OWL-2019-NEXUS5-QUICK

### Description

`_analyze_sms()` has exactly one detection rule: scanning outgoing SMS bodies
for mentions of encrypted-app names (Signal, Wickr, etc.) to flag
"SMS_ENCRYPTED_RECRUITMENT". It has no general-purpose content analysis for:
- Transaction/coordination language (price, time, location, delivery terms)
- Unknown/suspicious sender numbers
- Message frequency or burst patterns
- Cross-reference against contacts (sender not in contacts2.db)

### Real case demonstrating the gap

Owl 2019 Nexus5-Quick scenario (Digital Corpora, ground-truth documented):
SMS from `+13045184333`: "Sarah, the delivery is today 7 tonight the
confirmation will come later through pidgin." This is the exact coordination
message the scenario was designed to test ("One message sent via SMS should
confirm the time of the trade" — per scenario build guidelines). The message
contains no encrypted-app keywords, so it does not match any existing rule.
Result: 0 findings related to message content; only EMPTY_CONTACTS fired
(z=1.20, structural signal unrelated to the actual evidence).

### Why this matters

This is a coverage gap distinct from B-045 (wiring). B-045 fixed the pipeline
so AndroidForensicsAnalyzer actually runs — but once it runs, its SMS analysis
is narrow by design. The scenario's own ground truth (AXIOM commercial tool,
project logs) confirms this message exists and is the key evidence; VIGÍA's
deterministic pipeline cannot see it without a new detection rule.

### Fix path

Requires new finding types in `_analyze_sms()`:
- Generic transaction-language pattern (regex/keyword set: price/time/location
  terms — needs calibration to avoid false positives on legitimate planning SMS)
- Sender-not-in-contacts cross-reference (requires `_analyze_contacts()` to run
  first and pass known numbers to `_analyze_sms()`)
- This should NOT be a hardcoded "owl" keyword list — must generalize to any
  transaction-coordination pattern, or it only solves this one scenario.

Do not implement without calibration data across more cases — same caution
as L-033 gamma calibration. A naive price/time/location keyword set risks
false positives on ordinary scheduling SMS.


---

## L-044 — MetabolicProfiler and BehavioralFingerprint do not run in Mode 1 (agent) [DOCUMENTED]

**Affects:** `vigia/inference/metabolic_profiler.py`, `vigia/inference/behavioral_fingerprint.py` | **Status:** documented design limitation (Tanda B, option B)

**Description:** both engines require an `event_stream` (list of event dicts
with epoch `timestamp`), which the agent never generates (the shim re-maps
`event_stream` → `event_logs`). They are fully implemented but only reachable
in Mode 4 / direct API usage.

**Honesty marker:** since Tanda B, `pipeline_meta.engines_not_run_no_event_stream`
lists them explicitly in every V4 result without an event_stream — "did not
run by design" is distinguishable from "ran and found nothing"
(B-052-P1 pattern).

**Future work (PROPUESTA_TANDA_B.md item 7, option A):** feed them from the
`EventRecord`s already parsed by EventLogCorrelator (`timestamp` epoch int —
exactly the expected format). Deferred until a case demonstrates forensic
value over a single evtx.

## L-045 — `mcp` not installable in minimal CI environments (PyJWT conflict) [DOCUMENTED]

**Affects:** `requirements-ci.txt`, `tests/e2e/test_integration_end_to_end.py`,
`vigia/tests/adversarial/test_human_jitter_deterministic_bypass.py` |
**Status:** documented CI limitation (Fase 0, finding S-1 of
`docs/PLAN_ABDUCTIVO_PENDIENTES_20260705.md`)

**Description:** the `mcp` package (required by the two e2e/adversarial test
modules that exercise the MCP bridge) cannot be installed in environments
where `PyJWT` was provisioned by the system package manager (e.g. Debian):
`pip` fails with `Cannot uninstall PyJWT — RECORD file not found`. Reproduced
2026-07-05 in a clean CI-like container. `mcp` therefore stays OUT of
`requirements-ci.txt` deliberately; it remains in `requirements.txt` and
`pyproject.toml` for full installs.

**Consequence:** in a minimal CI environment (requirements-ci only), those two
test modules do not collect. This is an infrastructure gap, not a forensic
one — no verdict-path code depends on `mcp`.

**Guard:** `tests/test_requirements_ci_contract.py` enforces that every other
third-party import reachable from `tests/` and `vigia/tests/` is covered by
`requirements-ci.txt`; `mcp` is the single allowlisted exception, pointing at
this entry. Adding a new dependency to tests without updating
`requirements-ci.txt` fails the contract test (this is the third occurrence
of the drift class: defusedxml/T-2 in B-017, then psutil and pytest-cov —
both reproduced 2026-07-05).

**Workaround for full local runs:** `pip install --ignore-installed PyJWT`
first (gives pip a RECORD to manage), then `pip install mcp`.

---

## L-046 — Scorer Non-Monotonicity: Inculpatory Evidence Could Lower the Score [RESOLVED]

**Affects:** `vigia_scorer.py` | **Status:** [RESOLVED] 2026-07-07, POST HACKATHON —
commits `433d61a` (audit), `f85f171` (fixes), `1d84c84` (doctrine). Tracked as **B-081**.
**Severity:** P1
**Document:** `docs/REDTEAM_ROUND2_MONOTONICITY.md`

**Description:** Red-Team Round 2 confirmed two monotonicity violations in the
composite scorer:

- **M2-1 (monotonicity):** adding an additional inculpatory artifact could *lower*
  the composite score rather than raise or preserve it — a forensic scorer must never
  reward an examiner for withholding evidence.
- **M2-2 (no-dilution):** padding a case with weak same-type artifacts could dilute a
  strong signal below its correct verdict band.

**Root cause:** the redundancy penalty / best-prefix aggregation did not guarantee a
non-decreasing composite as strong evidence was added. The violation was latent — no
prior test asserted the invariant.

**Why this matters (Daubert):** non-monotonic scoring is not defensible in court. An
opposing expert could demonstrate that the same evidence set scores differently
depending on the order or count of corroborating artifacts. The invariant "more
inculpatory evidence never lowers the verdict" must hold by construction, not by luck.

**Fix applied:** the M2-1/M2-2 fixes were landed behind a comparative gate (corpus
165→163 on the fix alone: +1 correct fix, −3 label conflicts that had *encoded* the
dilution as ground truth). Round 2.1 was a doctrine decision — relabelling those 3
mislabelled cases — restoring the corpus to **166/199** (now 167/199 after later
label-hygiene work). The invariant is now pinned:
`tests/test_m2_monotonicity_invariants.py`.

**Forensic note:** three corpus cases had to be *relabelled*, not the code bent to
match them — their prior labels were the artifact of the very dilution bug being
fixed. This is documented as a doctrine decision, not a metric massage.

---

## L-047 — Bundle Canonicalization v1 Type Collisions (Canon v2) [RESOLVED]

**Affects:** `vigia/core/canonicalize.py`, seal/verify path | **Status:** [RESOLVED]
2026-07-07, POST HACKATHON — commit `b981803` (R3-2). Tracked as **B-082**.
**Severity:** P1 — seal integrity
**Document:** `docs/REDTEAM_ROUND3_EMERGENT.md`

**Description:** the v1 canonical form used to compute the bundle hash did not
disambiguate values that serialise to the same string across distinct types. A boolean
`True` and the string `"true"`, or an integer `1` and the string `"1"`, could canonicalise
to the same byte sequence. An attacker with write access to the pre-seal structure could
therefore swap a typed value for its string twin without changing the bundle hash — a
seal-integrity gap.

**Fix applied (canonicalization v2):** v2 encodes the *type tag* alongside the value
(`1` vs `"1:int"`, `True` vs `"true"`), closing the collision class. The change is
**backward-compatible**: v1 remains available and is used to verify historical bundles
sealed under the old canonical form, so no previously sealed bundle is invalidated. New
bundles seal under v2.

**Related Round 3 emergent findings (B-082, same batch):**

- **R3-1** — temporal range guard added in the Timestamp Comparability Validator
  (commit `22f6edc`); rejects out-of-range timestamps instead of silently comparing them.
- **R3-3** — label-consistency assertion added to the corpus runner (`22f6edc`); the
  full census (R3-3b/R3-3c) surfaced 62 duplicated case stems and one live
  `expected_verdict` divergence, and physically deduplicated 20 byte-identical copies.
  It also rescued `VIGIA_BREAK_005_FALSE_CORRELATION`, silently excluded since creation
  by a substring `SKIP_STEMS` match — the honest denominator was restored to 199.
- **R3-4** — causal-order validation added to the chain verifier as an axis independent
  of the cryptographic seal (commit `e0e7be0`).

**Forensic note:** a canonical form is only as trustworthy as its injectivity. Any two
distinct pre-seal structures must produce distinct canonical bytes, or the seal proves
less than it claims. v2 restores that property without breaking auditability of older
sealed evidence.

---

## L-048 — Tool-Log Chain Tail Truncation Invisible Without an External Anchor (chain_tip_sha256) [RESOLVED]

**Affects:** `vigia/core/tool_log_chain.py`, `verify_tool_log.py` |
**Status:** [RESOLVED] 2026-07-07, POST HACKATHON — commit `0d5abc2` (R3-5).
**Severity:** Low–Medium
**Document:** `docs/REDTEAM_ROUND3_EMERGENT.md`

**Description:** the v2 tool-execution-log hash chain makes every field of every entry
tamper-evident, and `prev_hash` linkage catches an entry deleted, inserted, or reordered
*in the middle* of the log. But deleting (or appending) entries strictly *after* the last
verified link leaves the remaining chain internally consistent — there is nothing past
the final entry to notice that later entries are gone. A truncating attacker could drop
the tail of the audit trail (e.g. the evidence of their own last actions) undetected.

**Fix applied:** the producer now writes `chain_tip_sha256` — the `entry_hash` of the last
entry — as a **bundle-level field, sibling to `tool_execution_log`**, outside the array a
truncating attacker would edit. The verifier recomputes the tip from the log it is handed
and compares; a mismatch means entries were removed or appended after the tip was recorded.
`verify_tool_log.py` threads the field through automatically when present (v2 only).

**Honest limit (documented, not overclaimed):** `chain_tip_sha256` alone is a plain
SHA-256, recomputable by any attacker with write access to the bundle — exactly like the
per-entry `entry_hash`. An attacker who truncates the tail *and* rewrites
`chain_tip_sha256` to match is invisible under hash-only verification. The keyed sibling
`chain_tip_hmac = HMAC(VIGIA_HMAC_KEY, chain_tip_sha256)` closes that residual the same way
`entry_hmac` does for the per-entry case: recomputable only by a holder of the key. Bundles
that omit `chain_tip_sha256` entirely (older bundles) remain verifiable — the verifier
reports the gap as a caveat, not a failure.

**Test:** `tests/test_r3_5_chain_tip_truncation.py`.

**Forensic note:** this is the single-bundle analogue of the checkpoint anchor
`ChainOfCustody` already provides for its sqlite ledger. An audit trail whose tail can be
silently amputated does not meet chain-of-custody completeness under Daubert.

---

## L-049 — Spoofable-Type Flood Saturates the Composite to MALICE [DOCUMENTED]

**Affects:** `vigia_scorer.py::_vigia_score` composite, B-068 corroboration gate |
**Status:** [DOCUMENTED] 2026-07-07, POST HACKATHON — recorded for a calibration-doctrine
decision, deliberately **not** silently patched. Tracked as **R4-3**.
**Severity:** Medium — invariant/semantic
**Document:** `docs/REDTEAM_ROUND4_BOUNDARIES.md`

**Description:** a flood of the *single most spoofable* evidence class saturates the
Noisy-OR composite to MALICE, even though every source is `log_entry` — the class an
administrator (or an attacker with shell access) can forge with `echo >> syslog`:

```
  4× log_entry (spoofability 0.85) → SUSPICION  score = 0.1672
 10× log_entry                     → MALICE     score = 0.3393
 50× log_entry                     → MALICE     score = 0.8741
100× log_entry                     → MALICE     score = 0.9842
```

This directly contradicts CAIE's own docstring claim that Noisy-OR grouping "prevents
flood attacks where one tool generates 100 alerts."

**Root cause:** the composite is `1 − ∏(1 − adj_i)` over *all* artifacts after a
redundancy (FRS) penalty **capped at 0.5**. Beyond ~4 same-type artifacts the penalty is
maxed, so each additional artifact still contributes Noisy-OR mass and the composite
saturates toward 0.99. The B-068 corroboration gate then opens on `n_artifacts ≥ 4` and
emits MALICE — cardinality of a *cheap* class manufactures a high-severity verdict. This
is the flood-attack analogue of the Round 2 No-Dilution finding (L-046 / M2-2).

**Forensic implication:** in fallback (deterministic) mode, an examiner or adversary who
can inject many low-cost, high-spoofability artifacts of one type can push a case to
MALICE without any low-spoofability corroboration. Treat MALICE verdicts resting on a
homogeneous flood of a single spoofable class as unproven pending heterogeneous
corroboration.

**Why not fixed here:** damping the flood changes scoring *semantics* and needs a
calibration decision — the same doctrine-call shape as the M2 relabels (L-046). Adjusting
it without a calibration corpus would trade one uncalibrated behavior for another.

**Recommendation (record only):** cap the composite contribution *per evidence class*
(domain-grouped FRS — group Noisy-OR within a class, then combine across classes, as CAIE
already does internally), and/or require the B-068 corroboration to rest on at least one
low-spoofability class before MALICE.

**Round 4 siblings (same audit, `docs/REDTEAM_ROUND4_BOUNDARIES.md`):** R4-1 (same-type
flood was O(n²) in the M2-1 best-prefix decay → **FIXED**, O(n), bit-identical over 20 000
random cases), R4-2 (no scorer-level artifact cap; per-artifact CAIE instantiation
dominates cost — documented recommendation), R4-4 (`None`/non-dict `case` crashed with
`AttributeError` → **FIXED** with a fail-loud `ERROR` guard).

**Update 2026-07-07 (B-091 / R4-3):** the recommendation above was implemented as the
per-collection-domain tail decay + the three-branch B-068 v2 gate (see B-091 in
BUGS_PENDIENTES). The flood curve for every type mapped in `_DOMAIN_MAP` is now flat
(`log_entry` ×10/50/100 → 0.1861/0.1866/0.1866) and a homogeneous soft-class flood can
no longer open any MALICE branch.

**Update 2026-07-09 (B-092) — mobile-band residual CLOSED:** the 8 mobile types of
`EVIDENCE_PROFILES` (`chat_message`, `sms`, `call_log`, `web_search`, `app_data`,
`social_media`, `location_data`, `contact_data`) had no `_DOMAIN_MAP` entry → band
UNKNOWN → exempt from the tail decay, leaving this exact flood vector open for the
mobile path (measured: 100× `web_search` raw 0.85 → 0.9900; 100× raw 0.05 pure noise
manufactured SUSPICION 0.3566). Fixed by mapping the local-record types to D3 and
`social_media` to D4; comparative gate over the 199-case corpus: 0 verdict flips,
0 score flips (mobile band absent from the JSON corpus). Residuals B-092 does NOT
close (measured, recorded in the B-092 entry): `location_data` (spoofability 0.30,
on the `<=0.30` boundary) still opens the hard-mass gate branch (4× raw 0.85 →
MALICE), and a D3+D4 mix (`web_search`+`social_media`) still opens the
cross-domain branch — both calibration-doctrine questions, not regressions. See
B-092 and `docs/MACOS_MODULES_DESIGN.md` §9.1-b.

---

## L-050 — Non-Finite (NaN / ±inf) Silently Admitted as Maximum-Severity Signal [RESOLVED]

**Affects:** `vigia/core/ebs_v1.py`, `vigia/core/signal_contract.py` (`SignalOutput`) |
**Status:** [RESOLVED] 2026-07-07, POST HACKATHON — commit `15e858d`. Tracked as
**B-083 / B-083b** (from the P0-001 `float()` census, `docs/AUDIT_P0001_FLOAT_CENSUS.md`).
**Severity:** P2 → security-relevant (silent maximum-severity injection)

**Description:** the `SignalOutput` clip/clamp logic silently converted non-finite inputs
into maximum-severity values on three fields, across four implementations:

- **`z_score`:** `min(z, Z_CLIP_MAX)` with a `NaN` argument returns the *clip ceiling*
  (`5.0`) under IEEE 754 `min` semantics — a corrupt z-score entered the pipeline as a
  maximum CRITICAL signal.
- **`value`:** same non-finite path.
- **`confidence`:** `max(0.0, min(1.0, nan))` collapsed to `1.0` — a corrupt confidence
  entered as silent *maximum* confidence; `±inf` clamped to `1.0`/`0.0`.

The **three fields × four implementations** are: `value`, `z_score`, and `confidence`,
each in (1) the `ebs_v1` Pydantic model, (2) the `ebs_v1` dataclass fallback, (3) the
`signal_contract` Pydantic model, and (4) the `signal_contract` dataclass fallback. The
Pydantic variants already rejected `NaN` via `Field(ge/le)` comparison semantics; the
**dataclass fallbacks** (used when Pydantic is unavailable) were the real gap.

**Fix applied (fail-closed):** non-finite `value` / `z_score` / `confidence` now raise
`ValueError` in all four variants — `math.isfinite` is checked explicitly so the contract
no longer depends on an incidental property of Pydantic's comparison operators. Clip and
clamp on *finite* values are unchanged. Tests were written red-first:
`tests/test_b083_signaloutput_fail_closed.py` (14, 8 red pre-fix; the dataclass fallbacks
verified by blocking Pydantic at import). Suite green, corpus 166/199, 0 verdict flips.

**Forensic note:** a scorer must never treat "I could not compute this value" as "this
value is maximally incriminating." Fail-closed (reject the corrupt signal loudly) is the
only defensible behavior — a silently-substituted `5.0` z-score is a fabricated CRITICAL
finding with no evidentiary basis.

---

## L-051 — §9.4-LIM: SUSPICION is the doctrinal ceiling for macOS/mobile D3-only cases (sealed decision, pure option (ii))

**Sealed 2026-07-10 (collective + Anna's signature; see `docs/B052_P2_DESIGN.md` §10).**

A case whose evidence comes exclusively from the D3 physical channel (the
device's own local filesystem — ALL macOS/mobile logical domains: browser,
antiforensic, persistence, quarantine, apps, fsevents, spotlight) cannot
escalate beyond SUSPICION by doctrine: the "multiple domains" share the
same fabrication channel, so their multiplicity does NOT constitute
independent corroboration. Whoever controls the disk controls all of those
sources at once.

- The logical-domain split (B-052-P2) was implemented, measured, and
  **rejected** — branch `claude/b052-p2-domain-signals-xk5ecq`, NOT merged,
  preserved as a record.
- The alternative metric `densidad_causal_D3` (D3 causal density) was
  discarded via a pre-registered experiment (Pearson r=0.9185 vs z,
  fail-closed gray zone).
- Mitigation implemented (narrative + `pipeline_meta` only): the class
  `suspicion_class = D3_RICH_NO_TRIANGULATION` distinguishes, within the
  bundle, the "strong evidence confined to D3, manual triangulation urgent"
  SUSPICION from the generic (weak evidence) SUSPICION. Exact rule and
  tests in `docs/B052_P2_DESIGN.md` §10.2.
- **Ceiling ENFORCED (signed and applied 2026-07-10):** when the
  D3-rich-without-triangulation condition is met, the shim declares
  `abduction.verdict_ceiling = "SUSPICION"` and `classify_agent_verdict`
  (the single sealing path) caps MALICE/INTENT → **SUSPICION** pre-emission
  (REFUTATION GATE pattern: the engine's raw hypothesis is preserved and
  the gate is logged in the narrative; the LLM cannot override it).
  SUSPICION enters the sealed verdict space sharing `EXIT_INTENT`
  (documented contract "3=intent/suspicion") and INTENT's alerting floor —
  the cap does not de-alert. Comparative enforcement gate: 0 flips across
  291 bundles, corpus 167/199 identical, byte-identical runner output.

**Closure criterion:** D2/D4-channel engines for mobile evidence (device
memory/network), or validation against a real labeled corpus of ≥50
macOS/mobile cases.

## L-052 — Living-off-the-Land Attacks Invisible to the Deterministic Motor [DOCUMENTED]

**Registered 2026-07-13. Status: DOCUMENTED — architectural limitation.**

The deterministic motor cannot detect attacks where the attacker uses
exclusively legitimate tools (PowerShell, Veeam, RDP) with stolen but
valid credentials, during normal business hours, with no anti-forensic
artifacts. Every individual signal is indistinguishable from authorized
activity.

Corpus evidence: VIGIA-FN-001 (score 0.020, NOISE) and VIGIA-FN-002
(score 0.018, NOISE) — both designed to exercise this gap.

**Why this is not a CAIE gap:** The anomaly is not a contradiction between
artifacts (what CAIE detects). It is the absence of anomaly in a context
where an anomaly should exist — detectable only with a per-user behavioral
baseline (User Behavior Analytics / UBA). UBA requires historical activity
profiles, which are outside the scope of a deterministic case-level scorer
that processes each case in isolation.

**Mitigation:** Mode 2 (Claude/MCP) can detect these patterns through
semantic analysis of the full evidence context. The limitation applies
only to Mode 1 (autonomous deterministic motor).

## L-053 — Weak Signal Convergence Below Individual Threshold [DOCUMENTED]

**Registered 2026-07-13. Status: DOCUMENTED — scorer architecture decision.**

When N signals individually below the SUSPICION threshold (0.10) all
point to the same target, the motor does not aggregate their collective
weight. Each signal is evaluated independently against the threshold;
convergence without individual significance produces NOISE.

Corpus evidence: VIGIA-BREAK-011 (20 weak signals, score 0.036, NOISE).

**Why this is not a CAIE gap:** Signal convergence is an accumulation
problem (how to sum N weak indicators), not a cross-artifact contradiction
(what CAIE fractures detect). The scorer's composite formula uses a
Noisy-OR model per artifact, not a collective convergence detector.

**Architectural note:** Adding a convergence detector would require a
fundamentally different accumulation model (e.g., Bayesian network over
indicator co-occurrence). The current N=1 corpus case does not justify
the complexity. If more cases emerge, this becomes a scorer enhancement
candidate, not a CAIE rule.

## L-054 — Exculpatory Context Not Modeled in Deterministic Scoring [DOCUMENTED]

**Registered 2026-07-13. Status: DOCUMENTED — doctrinal decision.**

The motor does not attenuate scores based on exculpatory metadata
(e.g., `authorized=true`, `benign_explanation` fields). Cases with
structurally suspicious artifacts that have documented legitimate
explanations (journalist using Tor with editorial authorization, Linux
kernel worker threads, NPS exercise data) receive SUSPICION rather than
NOISE.

Corpus evidence: VIGIA-BEN-012 (kworker, score 0.125), VIGIA-BEN-014
(Tor journalist, score 0.107), NPS-2009-DOMEXUSERS (exercise, score
0.146), VIGIA-FP-003 (shared password, score 0.176).

**Why this is a doctrinal decision, not a bug:** An exculpatory metadata
field (`authorized=true`) in a case file is an assertion by the case
author, not a forensic fact. An attacker who controls the evidence can
fabricate exculpatory context. The motor's conservative posture (alert
on structural anomaly regardless of claimed authorization) is the
Daubert-correct choice: over-alerting on benign cases is preferable to
under-alerting on malicious ones with planted exculpatory metadata.

**Mitigation:** Mode 2 (Claude/MCP) evaluates exculpatory context
semantically. The SUSPICION verdict in these cases is correct from the
motor's perspective — it flags the anomaly and leaves the authorization
judgment to the human investigator or Mode 2 analysis.

**Measured cost of the doctrinal choice — B-028/B-065 floor neutralizes
D1 Eco filter (measured 2026-07-13):**

The D1 Eco filter in `_vigia_score()` correctly sets aside artifacts
marked `"semantic_role": "exculpatory"` before computing the composite.
However, when a residual incriminatory signal of medium magnitude remains
after exclusion, the B-028/B-065 alert floor overrides the net score:
an intent-class hypothesis cannot present as LOW alert regardless of
per-signal magnitude.

Measured example — VIGIA-BEN-014 (journalist Tor case):

- ART-002 (authorization memo) and ART-003 (traffic analysis) are
  correctly excluded by D1 Eco filter (`semantic_role: "exculpatory"`).
- ART-001 (Tor connection, raw_score=0.7, z=0.49) remains as the sole
  scored artifact and produces hypothesis `SUSPICION_DETECTED`.
- B-028/B-065 floors the alert to MEDIUM.
- Mode 1 result: **SUSPICION, posterior 21/100**.
- MCP `evaluate()` result (no floor): **NOISE, composite 0.0070**.

The D1 Eco filter did its job — it correctly isolated the exculpatory
context and reduced the scoring set to one artifact. The floor then
overrode the resulting low-magnitude score back to SUSPICION. This is
not a bug in either layer: the floor is a deliberate Daubert-conservative
choice (preventing malicious actors from planting exculpatory metadata to
suppress alerts), and the D1 Eco filter is working as designed. The
interaction between them creates a measurable false-positive rate in
authorized-use cases with one structurally anomalous artifact remaining.

**NPS-2009-DOMEXUSERS** shows the same floor effect without the
exculpatory semantic_role mechanism (no exculpatory fields in the case):
Mode 1 returns SUSPICION at 29/100 while MCP returns NOISE at 0.0139.
The floor applies at hypothesis level regardless of semantic_role.

**This is not a bug to fix today.** The B-028/B-065 doctrine (over-alert
on intent-class findings) is a deliberate design decision requiring
explicit doctrinal review to change. This entry quantifies the known cost
of that decision: any exculpatory case with a single structurally anomalous
artifact of medium magnitude (z~0.4-0.9) will produce Mode 1 SUSPICION
regardless of how well the D1 Eco filter identifies and excludes the
exculpatory context. The floor is working correctly by its own definition;
the cost is now measured and documented.

---

## L-055 — Anthropic API and Claude Code Subscription Plans Are Separate Authentication Products [DOCUMENTED]

**Registered 2026-07-13. Status: DOCUMENTED — product boundary. No code
fix is possible from VIGÍA's side.**

**Affects:** `vigia/config.py:LLMBackend._try_anthropic()` — specifically
the Python `reason_with_llm` / `validate_and_correct_analysis` MCP tools,
in any environment where Claude Code is running but `ANTHROPIC_API_KEY`
is not set.

**Important scope clarification:** This limitation applies exclusively to
VIGÍA's Python tools calling `anthropic.Anthropic()` as a subprocess HTTP
client. It does NOT affect Claude Code's own operation as the conversational
LLM: in Mode 2, Claude Code itself reads evidence, calls MCP tools, writes
analysis, and produces investigation reports — all of that works correctly
regardless of this limitation. The gap is narrower than it appears: the
only missing piece is that `reason_with_llm` (a Python tool) cannot call
the Anthropic API independently. Ollama fills that role in this environment.

**Description:** When `reason_with_llm` or `validate_and_correct_analysis`
are called as MCP tools (from vigia_sift_bridge.py), they instantiate
`anthropic.Anthropic()` directly in Python and call `client.messages.create()`.
This requires a standalone `ANTHROPIC_API_KEY`. Without it, the SDK raises
`TypeError` ("Could not resolve authentication method") which causes the
tool to fall back to Ollama.

**Root cause — two separate products with separate auth:**

| System | Auth mechanism | Accessible from Python subprocess |
|--------|---------------|-----------------------------------|
| Claude Code (Pro / Max / API subscription via claude.ai or the CLI) | OAuth session token, stored internally by the CLI (`~/.claude/`) | NO — not exposed to subprocesses |
| Anthropic API (`api.anthropic.com`) | `ANTHROPIC_API_KEY` (static) or `ANTHROPIC_AUTH_TOKEN` (OAuth Bearer) | Yes, if explicitly set in the environment |

Claude Code injects `CLAUDECODE=1`, `CLAUDE_CODE_ENTRYPOINT=cli`, and
`CLAUDE_CODE_EXECPATH=...` into subprocess environments. None of these
variables carry API credentials. The Anthropic Python SDK (v0.109.2)
does not check `CLAUDECODE` at any point in its credential resolution chain
(`default_credentials()` in `anthropic/_client.py`).

This is by design: Claude Code's Pro/Max subscription billing applies to
conversations in the claude.ai UI or the Claude Code CLI. API calls from
Python (`client.messages.create()`) are a separate product with separate
per-token billing.

**Consequence:** Setting `VIGIA_LLM_BACKEND=anthropic` without
`ANTHROPIC_API_KEY` will always fall through to Ollama (if running) or
produce an empty-response error. Since 2026-07-13, the fallback is honest:
`backend_warn` in the tool output carries an explicit degradation notice,
and `llm_backend` reflects the actual responding backend.

**What is NOT possible from VIGÍA code:**
- Detecting or reusing the Claude Code session token from a Python subprocess.
- Using Pro/Max plan conversation quota for `client.messages.create()` calls.
- Any code change in VIGÍA that bridges the two auth systems.

**Mitigation:**
To activate the Anthropic Python path in VIGÍA, obtain a dedicated
`ANTHROPIC_API_KEY` from console.anthropic.com (separate billing) and set
it before launching the MCP server:

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
export VIGIA_LLM_BACKEND=anthropic
```

Alternatively, `VIGIA_LLM_BACKEND=ollama` with a local model
(`hermes3:8b`, `deepseek-r1:8b`) covers the same MCP tool functionality
with no API key required.

---

## L-056 — Mode 1 vs Mode 2 Alert Architecture Divergence (third divergence type, distinct from M3) [DOCUMENTED]

**Registered 2026-07-13. Status: DOCUMENTED — architectural gap, no fix
intended.**

**Affects:** Any case where Mode 1 (`vigia_agent.py`) and Mode 2 (Claude
Code + MCP `cross_artifact_analysis`) are compared on the same evidence.

### Background — three known divergence types between modes

| Type | Source | Mechanism | Status |
|------|--------|-----------|--------|
| M3 | `tests/test_m3_scorer_caie_parity.py` | Fracture-type weight maps in `vigia_scorer.py` drift from the live CAIE fracture catalogue in `vigia/tools/caie.py`. Missing fracture types are silently weighted at zero in the scorer. | Regression-tested — M3 test catches new drift. |
| semantic_role | `vigia_scorer.py:_vigia_score()` L-054 | `_vigia_score()` honors `semantic_role: "exculpatory"` via D1 Eco filter; MCP `evaluate()` ignores the field. | Documented as part of L-054. |
| **Alert floor (this entry)** | `vigia_scorer.py` B-028/B-065 | `_vigia_score()` applies a floor preventing intent-class hypotheses from presenting as LOW; MCP `evaluate()` is a pure Noisy-OR scoreboard with no floor. | Documented here — L-056. |

### Description of the alert floor divergence

`vigia/tools/caie.py::evaluate()` (called by MCP `cross_artifact_analysis`)
computes a Noisy-OR composite score and maps it to a verdict via a
numerical threshold: composite < 0.05 → NOISE. No floor is applied.

`vigia_scorer.py::_vigia_score()` (called by `vigia_agent.py` Mode 1)
computes z-scores per signal, aggregates to a hypothesis, then applies
the B-028/B-065 alert floor: a SUSPICION hypothesis cannot present as LOW
alert regardless of per-signal magnitude. This floor is downstream of all
scoring — it applies after the Noisy-OR composite, after D1 Eco filter
exclusions, and after z-score normalization.

**Measured divergence (2026-07-13):**

| Case | MCP composite | MCP verdict | Mode 1 posterior | Mode 1 verdict | Floor note |
|------|--------------|-------------|-----------------|----------------|-----------|
| VIGIA-BEN-014 | 0.0070 | NOISE | 21/100 | SUSPICION | B-028/B-065 floored — 1 residual artifact z=0.49 |
| NPS-2009-DOMEXUSERS | 0.0139 | NOISE | 29/100 | SUSPICION | B-028/B-065 floored — 9 artifacts, top z=0.18 |

In both cases the per-signal magnitudes are well below the z>2 threshold.
The Noisy-OR composite is sub-0.05 (NOISE). But the hypothesis-level
aggregation produces `SUSPICION_DETECTED`, and the floor prevents the
SUSPICION from collapsing to a LOW alert or NOISE verdict.

### Why this is not M3

M3 is specifically about fracture-type weight map drift: fracture types
present in `caie.py` but absent from the scorer's `MALICIOUS_FRACTURE_TYPES`
set receive zero weight in the scorer, causing systematic under-weighting
of specific fracture signals. Neither BEN-014 nor NPS-2009 has fractures
detected — M3 is not the active mechanism here.

### Why this gap exists and will not be closed

The two scorers serve different roles:
- `evaluate()` is designed for MCP tool use: a deterministic, stateless,
  composable function that returns a numeric score for pipeline integration.
  No floor — the number is the number.
- `_vigia_score()` is designed for Mode 1 sealed verdicts with full Daubert
  posture: a SUSPICION finding cannot be filed as LOW because an investigator
  reading a LOW alert will not escalate it. The floor encodes the doctrinal
  choice that it is better to over-report a structural anomaly than to allow
  it to disappear into a LOW-priority queue.

Aligning the two would require either adding a floor to `evaluate()` (which
would break MCP integrations that rely on the raw numeric value) or removing
the floor from `_vigia_score()` (which would require a doctrinal decision
equivalent to L-054 / B-028/B-065 review).

**Mitigation for analysts comparing Mode 1 and Mode 2 outputs:**
When Mode 1 returns SUSPICION with per-signal z-scores all below 2.0 and
Mode 2 returns NOISE, the likely cause is the B-028/B-065 floor — not an
error in either system. Mode 2's NOISE verdict reflects the raw Noisy-OR
composite; Mode 1's SUSPICION reflects the floor applied to a low-magnitude
hypothesis. Both are correct by their own contract. Human review is the
intended resolution layer.

---

## L-057 — 18 MCP tools without TOOL_INVOKED entry audit log [DOCUMENTED]

**Scope:** Mode 2 (Claude Code + MCP), Mode 5 (OpenWebUI). Modes 1, 3, 4 unaffected.

**Status:** DOCUMENTED — partial mitigation applied in B-122 (2026-07-14).

### What is missing

`vigia/vigia_sift_bridge.py` exposes 22 MCP tools. B-122 added
`audit_logger.log_info(event_type="TOOL_INVOKED")` at entry to the three
tools that access raw evidence files:

- `generate_forensic_hash`
- `read_evidence`
- `list_files`

The remaining 18 tools have no entry-level audit log call. An agent can
invoke any of them without leaving a trace in the forensic audit chain:

| Tool | Category |
|------|----------|
| `search_pattern` | subprocess execution |
| `list_processes` | system enumeration |
| `audit_network` | system enumeration |
| `mount_sift_evidence` | disk mounting |
| `calculate_shannon_entropy` | in-memory computation |
| `audit_image_metadata` | file read (EXIF) |
| `analyze_stylometry` | in-memory computation |
| `calculate_human_entropy` | in-memory computation |
| `infer_intent` | in-memory computation |
| `detect_habit_incongruence` | in-memory computation |
| `detect_human_jitter` | in-memory computation |
| `audit_grice_maxims` | in-memory computation |
| `detect_eco_overinterpretation` | in-memory computation |
| `deactivate_honey_token` | file write |
| `reason_with_llm` | LLM call |
| `validate_and_correct_analysis` | in-memory computation |
| `reload_phonetic_dict` | file read |
| `get_phonetic_dict_stats` | in-memory computation |

### Why this matters (Daubert posture)

The `audit_logger` chain provides chain-of-custody evidence of what tools
were invoked and with what arguments during an investigation. If a tool
is called without an entry log, the audit trail can only confirm what
the tool *returned* (through its own internal logging), not that it was
*invoked* with a given input. For `search_pattern` and `mount_sift_evidence`
in particular — which execute subprocesses — a missing invocation log
means the audit chain has a gap at the decision boundary between the
analyst instruction and the system action.

### Scope boundary

The three B-122 tools were prioritized because they touch raw evidence
bytes directly and are the most frequent entry points for any investigation.
The in-memory computation tools (entropy, stylometry, jitter) do not
access files independently — they process data already read by `read_evidence`
or supplied by the agent, so the chain-of-custody gap is lower severity.

`deactivate_honey_token` already has an audit log call at exit (not entry).
The gap is the invocation record before the operation, not the outcome record.

### Mitigation (follow-up to B-122)

Apply the same B-122 pattern to each remaining tool:

```python
audit_logger.log_info(
    event_type="TOOL_INVOKED",
    tool="<tool_name>",
    message=f"<primary_arg>={value!r}",  # or f"n_items={len(arg)}" for list args
)
```

Insert before the first `_sanitize_path_local()` call (file-touching tools)
or immediately after `try:` (computation tools with no path argument).

For `search_pattern` and `mount_sift_evidence` the log must precede the
`sandboxed_execute` call so that blocked or timed-out subprocess attempts
are also captured.

### Known performance note

`_write_entry` in `SecurityAudit` calls `os.fsync()` synchronously.
Adding entry logs to high-rate tools increases blocking I/O in the asyncio
event loop. At current rate limits (max 30 calls/60s for most tools,
max 10 for entropy/network) the impact is negligible. If rate limits are
raised in the future, wrapping `_write_entry` in `loop.run_in_executor`
should be evaluated at that point.

---
