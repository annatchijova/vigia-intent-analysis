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
| L-071 | Cross-domain gate counts domain presence, not mass (1 near-zero artifact pivots SUSPICION→MALICE) | vigia_scorer.py B-068 gate | [OPEN] — calibration doctrine; refinement of the B-092 residual |
| L-072 | `semantic_role` declared label neutralizes MALICE (37/52 corpus cases, label alone) | vigia_scorer.py D1 block | [OPEN] — doctrine; extends L-054, sibling of L-065/L-070 |
| L-073 | Threshold compares `_dround` float vs `Fraction`; exact grid point grants higher rung | vigia_scorer.py verdict ladder | [OPEN] — latent, zero corpus incidence |
| L-074 | Audience reports render sealed fields verbatim and cannot fill gaps a family does not record | vigia/report/ (presentation layer) | DOCUMENTED — by design, not a defect |
| L-067 | §9.4-LIM: SUSPICION doctrinal ceiling for D3-only macOS/mobile (sealed 2026-07-10; renumbered from second L-051 on 2026-07-23) | sift_orchestrator.py verdict_ceiling | Sealed doctrine |
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

> **Addendum 2026-08-27 (measurement supersedes the mapping-table plan
> above):** the phase-distribution measurement prescribed by the B-129
> addendum was executed (`scripts/dryrun_b129_phase_distribution.py`):
> with the corpus's real inputs, `detect_phase()` yields UNKNOWN for
> 206/209 cases, because no `mitre_ttps` input field exists in any corpus
> case and the violation vocabulary was largely absent from the phase
> tables. Building the `tool_name -> artifact_type` mapping first would
> therefore solve the wrong problem — phase-scoped hypothesis matching is
> unreachable before a TTP producer exists. What was applied instead
> (B-129 registry, updates ter and 2026-08-27 second batch):
> `resolve_ttp_phase()` (exact -> extracted id -> subtechnique parent),
> `EFFECT_BEFORE_CAUSE` and four single-tactic techniques added to the
> tables. The example mappings suggested above (e.g. `audit_network ->
> lateral_movement_auth`) should be treated as illustrative only — the
> reverted commit `86f6777` failed precisely by mapping tool names to
> artifact names by convenience. See `BUGS_PENDIENTES.md` B-129 for the
> current unblocking order.

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
**Status:** IN_PROGRESS — FW-009 Fase 1 landed 2026-07-17 (B-140: motor-path annotation, see progress block below); verdict effect and `false_flag` vocabulary remain open doctrine decisions
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

**Progress 2026-07-17 (B-140 — FW-009 Fase 1, annotation only):** the
detector (`vigia/core/darvo_detector.py`) now reads dict artifacts — the
Mode 1 (EBS JSON) format — in addition to the pipeline's SignalOutput
objects; it was structurally blind to dicts (getattr-only access), so it
had never fired outside `VigiaPipeline`. `_vigia_score` annotates the
sealed output with a `darvo_pattern` block (counts, Fraction penalty as
string, matched artifact ids), and the orchestrator/agent surface it in
the sealed narrative through the same channel B-094 opened for live CAIE
fractures. The annotation modifies NEITHER verdict NOR score (equality pin
in `tests/test_b140_darvo_motor_annotation.py`; comparative corpus gate).
On KIWI-001 the motor path now reports the canonical asymmetry: 2
surveillance-infrastructure artifacts (A02 PHP-error/trampolin logs, A04
honeypot access log) + zero-contact claim, penalty 3/5 — recorded, not
applied.

**F0 update (2026-07-17, signed batch — dossier
`docs/PROPUESTA_L029_DARVO_20260717.md` + independent audit
`docs/VEREDICTO_KIMI_L029_20260717.md`):** the multi-agent investigation
plus adversarial audit confirmed the three open items' direction (no verdict
effect from description keywords; no `false_flag` verdict rung; pairing as
architecture without verdict authority) and corrected the B-140 record:
MAGNET-2021-IOS-ELI was a substring false positive (de-annotated by
word-boundary matching, B-142), the honest annotation census is 4 cases =
ONE expediente + 2 copies (real N=1), the dead pipeline penalty channel was
retired with a schema tripwire, and B-141 (run_vigia signal drop) was fixed
in both deployments. The verdict-effect reopening conditions are
pre-registered in the dossier §4.

**F1+F2 (2026-07-17, same session — B-143/B-144):** the sealed annotation
now carries a machine-readable L-004 caveat, a MANDATORY deterministic
devil_advocate, and per-keyword matched_spans (FIRMA: spans yes), with no
nominal attribution ever entering the sealed block. Pairing exists as
architecture with zero verdict authority: `compare_paired_bundles` (MCP,
deterministic sub-metrics; Thirdness belongs to the calling analyst) and
signed cross-bundle linkage records in the batch runner (copy-dedup,
collision caveats — RT-FN-COLLUSION-001 as permanent fixture, label-blind,
HMAC-sealed, timestamp-free). Still open: item 3's full paired scoring
(N=1 self-referential blocker) and everything gated on F3 data
acquisition.

**Still open (doctrine / architecture, NOT engineering):**
1. Verdict effect of the DARVO pattern in the motor path (would move
   verdicts → requires calibration decision + comparative gate sign-off).
2. `false_flag` as a relational verdict type in the scorer vocabulary
   (sealed-verdict schema change — maintainer signature required).
3. Cross-bundle paired review (KIWI-002 + KIWI-003 role inversion) — the
   Mode 1 pipeline has no paired-bundle concept; architecture work.

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
   score, CAIE fractures, peirce_chain, quadripartite_state. The direct scorer's
   forensic verdict is preserved in `caie_analysis`; its composite intent score is
   **not** treated as a calibrated EBS fabrication-risk posterior. Consequently
   the EBS `decision_trace` explicitly records `ABSTAIN` with
   `STANDALONE_SCORER_UNCALIBRATED_EBS_RISK`, while still sealing the complete
   direct analysis. This prevents a chatbot or API caller from reading a valid
   cryptographic seal as proof of a second, uncalibrated EBS decision.

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

**Affects:** `requirements-ci.txt`, and every test module that imports
`vigia.vigia_sift_bridge` at module scope (11 as of 2026-08-12) |
**Status:** documented CI limitation (Fase 0, finding S-1 of
`docs/PLAN_ABDUCTIVO_PENDIENTES_20260705.md`); scope and consequence
corrected 2026-08-12 — see "Correction" below

**Description:** the `mcp` package (required by the two e2e/adversarial test
modules that exercise the MCP bridge) cannot be installed in environments
where `PyJWT` was provisioned by the system package manager (e.g. Debian):
`pip` fails with `Cannot uninstall PyJWT — RECORD file not found`. Reproduced
2026-07-05 in a clean CI-like container. `mcp` therefore stays OUT of
`requirements-ci.txt` deliberately; it remains in `requirements.txt` and
`pyproject.toml` for full installs.

**Consequence:** in a minimal CI environment (requirements-ci only), the test
modules that import the bridge do not collect. This is an infrastructure gap,
not a forensic one — no verdict-path code depends on `mcp`.

**Correction 2026-08-12 — the scope and the consequence above were both
understated.** Two facts, measured on the live tree before anything was
changed:

1. *Scope.* The "Affects" list named two modules. Eleven import the bridge at
   module scope. Six already carried the `pytest.importorskip("mcp")` guard —
   `tests/test_mount_magic_bytes.py`, `tests/test_mcp_confused_deputy.py`,
   `tests/test_mcp_transport_auth_theater.py`,
   `tests/test_kassandra_salt_enforcement.py`,
   `tests/test_grupob_b9_honey_token_lifecycle.py`, and
   `vigia/tests/adversarial/test_human_jitter_deterministic_bypass.py`. That
   last one is named in the original "Affects" list as broken; it had been
   guarded at some point without this entry being updated.

   Five did not: `tests/e2e/test_integration_end_to_end.py` (the other module
   the original list named) and the four added after this entry was written —
   `tests/test_b122_universal_tool_invoked_audit.py`,
   `tests/test_b164_mcp_mount_root.py`,
   `tests/test_b169_mcp_invocation_audit.py`, and
   `tests/test_b173_bridge_work_root.py`. The convention existed; it was
   simply not carried forward.

2. *Consequence.* "Those modules do not collect" implies the rest of the suite
   runs. It does not. A collection error is not a skip: pytest aborts the
   session (`Interrupted: N errors during collection`) and executes **zero
   tests**. Measured in a container built from `requirements-ci.txt` alone,
   the authoritative full-suite command in `CLAUDE.md` collected 2352 tests,
   reported 4 errors, and ran none of them. Anyone verifying this repository
   from the documented minimal environment — including a third party
   reproducing the forensic claims — saw a red suite with no signal in it.

**Fix applied:** all thirteen guards in the suite now read
`pytest.importorskip("mcp.server.fastmcp")` — the five modules that carried no
guard at all, and the eight that named the bare `mcp` distribution rather than
the subpackage `vigia_sift_bridge.py:49` actually imports. The distinction is
not cosmetic: `mcp` 2.0.0 removed `mcp.server.fastmcp`, so a guard on the bare
name passes while the bridge import still fails, reproducing the abort by a
second route. Suite in the minimal environment: 2127 passed, 209 skipped, 28
xfailed, 0 errors, 0 failed.

Retargeting the guard fixes the abort but would let a genuinely broken install
hide behind a wall of green skips, so the two states are deliberately
separated: absent `mcp` skips (this entry's documented state), while an `mcp`
that is installed but missing the subpackage fails loudly and specifically in
`tests/test_mcp_dependency_contract.py` without taking the session down.
Measured: minimal env 2127 passed / 0 failed; `mcp` 1.29.0 → 2237 passed / 0
failed (the 110-test delta is the MCP surface genuinely running, which is what
rules out over-skipping); `mcp` 2.0.0 → 2127 passed / 1 failed naming the
cause.

One of the repaired failures was a false pass rather than a plain error:
`test_b173_rejects_work_root_nested_in_evidence` asserts that importing the
bridge with `VIGIA_WORK_DIR` nested inside evidence exits non-zero. Without
`mcp`, the import exits non-zero because `mcp` is missing, so that assertion
passed for a reason unrelated to the rejection it exists to prove. It failed
only on the subsequent stderr check. A module-level skip removes the
ambiguity.

**Guard:** `tests/test_minimal_ci_collects_without_errors.py` runs the real
collection in a child interpreter with the allowlisted distributions forced
unimportable, and fails if the session reports any collection error. It is
environment-independent — it holds whether or not `mcp` is installed on the
machine running it — and it checks the outcome that matters (the suite
collects) rather than a syntactic proxy for it (a module contains an
`importorskip` line). It carries a control test that fails if the blocker ever
stops taking effect.

**Guard:** `tests/test_requirements_ci_contract.py` enforces that every other
third-party import reachable from `tests/` and `vigia/tests/` is covered by
`requirements-ci.txt`; `mcp` is the single allowlisted exception, pointing at
this entry. Adding a new dependency to tests without updating
`requirements-ci.txt` fails the contract test (this is the third occurrence
of the drift class: defusedxml/T-2 in B-017, then psutil and pytest-cov —
both reproduced 2026-07-05).

**Workaround for full local runs:** `pip install --ignore-installed PyJWT`
first (gives pip a RECORD to manage), then `pip install "mcp<2"`.

The version bound is not optional, and this line said plain `pip install mcp`
until 2026-08-12. `mcp` 2.0.0 removed the `mcp.server.fastmcp` subpackage that
`vigia/vigia_sift_bridge.py:49` imports, so the unbounded command installs a
version under which the bridge cannot import at all — following this
workaround verbatim produced a broken MCP surface, not a working one.
Installing the full `requirements.txt` was never affected: `fastmcp` pulls
`mcp<2` transitively. That transitive constraint is now also declared directly
in `requirements.txt` and `pyproject.toml`, and pinned by
`tests/test_mcp_dependency_contract.py` — no module in this repository imports
`fastmcp`, so relying on it to bound `mcp` was one vestigial-dependency
cleanup away from breaking Modes 2 and 5 silently.

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

## L-067 — §9.4-LIM: SUSPICION is the doctrinal ceiling for macOS/mobile D3-only cases (sealed decision, pure option (ii))

**Sealed 2026-07-10 (collective + Anna's signature; see `docs/B052_P2_DESIGN.md` §10).**

**Numbering note (2026-07-23, L-029/L-051 and B-093/B-106 precedent):** this
entry was originally recorded as **L-051**, colliding with "Formal
Specification of Arbitration Contract" (born 2026-06-25, holder of L-051
since its own renumbering on 2026-07-08 — chronologically earlier, keeps the
number). Renumbered to **L-067** (next free ID). Historic sealed bundles and
commit messages citing "L-051" for the D3-only SUSPICION ceiling point here;
`sift_orchestrator.py` narrative strings updated for future bundles.

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

### Contract clarification — 2026-07-21 (Codex)

Mode 2 is not a byte-for-byte replay of the Mode 1 agent bundle. Mode 1 seals
the output of its fixed JSON/scorer path. Mode 2 runs a tool-driven Peircean
investigation and records a separately scoped report. The two paths may reuse
deterministic components, but their evidence reach, aggregation, and report
schema differ. Mode 2 must never mutate or overwrite a Mode 1 seal; conversely,
a Mode 2 conclusion must not be described as if it were the already-sealed Mode
1 verdict. README and `CLAUDE.md` now state this explicitly.

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

## L-057 — MCP tools without a uniform `TOOL_INVOKED` entry audit log [RESOLVED — B-169, 2026-07-21]

**Scope:** Mode 2 (Claude Code + MCP), Mode 5 (OpenWebUI). Modes 1, 3, 4 unaffected.

**Status:** RESOLVED — B-169 replaced the partial B-122 instrumentation with
one mandatory registration boundary for every MCP tool exposed by the active
bridge. The historical condition below is retained so prior bundles and audit
claims are not rewritten.

### Historical condition (before B-169)

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

### Resolution (B-169)

`vigia/vigia_sift_bridge.py` now routes every local decorator and every
external `mcp.tool()` registration through `_register_mcp_tool()`. Its
`_audit_mcp_entry()` wrapper emits `TOOL_INVOKED` before rate limiting,
sanitization, sandboxing or tool execution, so blocked and failed attempts
are present too. Argument summaries preserve parameter names, scalar values,
collection cardinality, and a SHA-256 of at most a 4 KiB string/bytes prefix;
they never write raw evidence, prompts, paths or token values into the audit
trail merely to prove a call occurred.

This resolves entry-audit coverage for the bridge process. It does **not**
change the separate B-122/L-057 provenance limit for historical bundles, nor
does it prove wall-clock ordering, an external client's identity, or that a
post-hoc tool-log response came from the claimed live service.

### Known performance note

`_write_entry` in `SecurityAudit` calls `os.fsync()` synchronously.
Adding entry logs to high-rate tools increases blocking I/O in the asyncio
event loop. At current rate limits (max 30 calls/60s for most tools,
max 10 for entropy/network) the impact is negligible. If rate limits are
raised in the future, wrapping `_write_entry` in `loop.run_in_executor`
should be evaluated at that point.

---

## L-058 — Architectural Tension Between CAIE and Grice for Pure Testimony Evidence [DOCUMENTED]

**Discovered:** 2026-07-14 (B-126, Mode 2 blind re-run of KIWI-006/KIWI-007)
**Status:** DOCUMENTED — gate proposed as RECOMMENDATION, not implemented, pending refined dry-run.

### Description

When all artifacts in a case are pure testimony (evidence_type in
{cultural_marker, log_entry, document_geometry}) acquired via
`manual_forensic_review`, the deterministic CAIE pipeline applies
spoofability penalties of 0.85-0.90 that crush raw scores (0.6-0.8)
down to adjusted scores of 0.0009-0.0097, producing NOISE composites
regardless of the pragmatic content.

Meanwhile, `audit_grice_maxims` detects real RELATION and QUANTITY
maxim violations in the same testimony — violations that represent
genuine forensic signals at the pragmatic layer (tactical evasion,
inverse precision patterns).

The autonomous agent (Mode 1/4) resolves verdict primarily via the
CAIE motor. When CAIE says NOISE, the motor says NOISE — correctly,
per its design. Mode 2 (interactive) can weight Grice signals via
analyst judgment, reaching SUSPICION. Both verdicts are architecturally
correct within their respective modes.

### Affected cases

Two cases in the corpus have expected_verdict=SUSPICION but receive
NOISE from the autonomous agent due to this tension:

| Case | Expected | Agent | Motor Score | CAIE Composite | Grice |
|------|----------|-------|-------------|----------------|-------|
| KIWI-006 | SUSPICION | NOISE | 0.0294 | 0.0040 | SUSPICION (30%) |
| KIWI-007 | SUSPICION | NOISE | 0.0518 | 0.0104 | SUSPICION (30%) |

Mode 2 re-run (Claude Opus 4.6, 2026-07-14) produced SUSPICION for
both cases (55/100 and 65/100 confidence), matching expected labels.
CRONOS trace: `6b81f266-a8e7-4c59-a04e-fff20e9e9e2f`.

### Proposed gate (RECOMMENDATION — not implemented)

A naive Grice override gate (if Grice=SUSPICION and P(deception)>=0.25,
escalate motor to SUSPICION) was evaluated against the full corpus.
It would fix 2 cases but cause 3 regressions:

| Case | Expected | Current | With Naive Gate | Classification |
|------|----------|---------|-----------------|----------------|
| KIWI-006 | SUSPICION | NOISE | SUSPICION | True positive |
| KIWI-007 | SUSPICION | NOISE | SUSPICION | True positive |
| BEN-003 | NOISE | NOISE | SUSPICION | **False positive** |
| BEN-010 | NOISE | NOISE | SUSPICION | **False positive** |
| BREAK-002 | NOISE | NOISE | SUSPICION | **False positive** |

### Root cause of false positives

The Grice RELATION/TACTICAL_EVASION detector is a near-constant: it
fires identically (weight=30, P(deception)=0.30) on ALL testimony
fragments regardless of content — both genuinely evasive (KIWI) and
genuinely benign (BEN/BREAK). It has zero discriminating power at the
current threshold. CRONOS trace: `3b11e32e-9f39-439a-a819-6a20c8ca35c6`.

### Structural discriminators (for a refined gate)

Case-by-case audit (B-126) revealed that the 3 FP cases are
structurally distinguishable from the 2 TP cases:

| Discriminator | KIWI-006/007 (TP) | BEN-003/010, BREAK-002 (FP) |
|---------------|--------------------|-----------------------------|
| Exculpatory artifacts | None | Present (semantic_role=exculpatory) |
| prior_trust | 0.10-0.15 | 0.70-0.85 |
| write_blocker_used | false | true |
| Internal corroboration | None (contradictions instead) | Present (recovery, calendar, ticket) |
| source_tool | manual_forensic_review | legacy_converter |

A **refined gate** could use these discriminators:

```
IF evidence_types ALL IN {cultural_marker, log_entry, document_geometry, testimony}
AND grice_verdict == SUSPICION
AND NO artifact has semantic_role == "exculpatory"
AND max(prior_trust) < 0.30
AND NO internal corroboration detected
THEN motor_verdict = max(motor_verdict, SUSPICION)
```

### Status — B-126 implementation (2026-07-14)

**Grice v3.2 (vigia_sift_bridge.py):** IMPLEMENTED. The RELATION
detector was replaced with a phenomenon-based bilingual (EN+ES)
detector with four features: factual_impossibility, quantity_asymmetry,
evidence_withholding, fundamental_ignorance. Threshold=25 (Daubert:
single phenomenon insufficient). Tiered adj_density (>=10% -> 30).
Validated against 9 test cases (5 known + 4 adversarial) and 199-case
corpus (0 regressions). Iteration history: v2.1 (English-only, phrase
memorization) -> v3 (phenomenon patterns) -> v3.1 (negation fix) ->
v3.2 (bilingual, EN/ES bug fixed). Commit `2d599b65`.

**Scorer testimony gate (vigia_scorer.py):** IMPLEMENTED as defense
in depth. Fires only when: verdict=NOISE AND testimony-only AND no
exculpatory artifacts AND max(prior_trust)<0.30 AND Grice=SUSPICION.
Currently only active in Mode 2/3 (interactive) where Grice results
are available in the case data.

**Threshold=25 deliberate non-fires:** ADV-002 (quantity asymmetry
alone, score=20) and ADV-004 (evidence withholding alone, score=20)
deliberately stay below threshold. A single evasion phenomenon
without corroboration is INFERRED, not SUSPICION. This is consistent
with Daubert corroboration requirements. These 2 cases are documented
as permanent regression tests — do not lower threshold to capture
them without re-validating the full corpus.

### Pipeline integration — B-127 (2026-07-14) [RESOLVED]

`sift_orchestrator.py::_resolve_hypothesis()` now calls
`audit_grice_maxims()` conditionally before invoking `_vigia_score()`:

- Only for testimony-only cases (all evidence_types in
  {cultural_marker, log_entry, document_geometry, testimony})
- Only when no artifact has semantic_role=exculpatory
- Persists `grice_verdict` and `grice_deception_probability` in the
  blind dict so the scorer gate finds them

Fix for prior_trust boundary: `< 0.30` changed to `<= 0.30`
(KIWI-007 has prior_trust=0.30 on the panic button artifact).

Dry-run verification: +2 FIX (KIWI-006, KIWI-007), 0 regressions
attributable to B-127. 9 pre-existing MALICE->SUSPICION divergences
between cached bundles and re-scored cases confirmed unrelated
(identical results without B-127 changes). Commit `815352bf`.

Corpus accuracy: 185/199 -> **187/199** (pending batch cache refresh
with `run_all_agent.py --rerun --filter KIWI`).

---

## L-059 — SAFARI_SUSPICIOUS Detector Cannot Distinguish Attacker Research from Victim Remediation Searches [DOCUMENTED]

**Registered 2026-07-14. Status: DOCUMENTED — temporal context limitation.**
**Mode affected:** Mode 1 (ios_forensics.py). Mode 2 resolves via analyst temporal reasoning.
**Discovered:** VIGIA-MAGNET-2022-iOS-JESS investigation, 2026-07-14.

### Description

`ios_forensics.py::_analyze_safari` applies the `SAFARI_SUSPICIOUS` pattern set
against all Safari history entries without regard for temporal ordering relative
to other artifacts. The pattern `r"(?i)fix.*hacked.*computer"` and similar
remediation-language patterns fire identically on:

1. **Attacker pre-operational research** — searching for hacking tools, attack vectors,
   or target reconnaissance before an incident.
2. **Victim post-incident remediation** — searching for how to fix a device after
   discovering it was compromised.

### Real case demonstrating the gap

VIGIA-MAGNET-2022-iOS-JESS (iPhone 8, GrayKey, Magnet CTF 2022):

- 2022-02-09: Victim receives phishing SMS from `ow.ly` shortened URL.
- 2022-02-11: Safari history shows `r"(?i)fix.*hacked.*computer"` searches.

Temporal ordering is unambiguous: the phishing SMS precedes the searches by 48 hours.
The searches are victim-response (remediation research), not attacker pre-operational
research. `ios_forensics.py` correctly flags them (the z-score contribution is valid
as a structural signal), but the forensic interpretation in automated analysis
cannot distinguish the two scenarios.

The June 2026 Mode 2 run (Ollama backend) reached INTENT verdict by misidentifying
these searches as attacker research, without cross-referencing the SMS timestamp.
The July 2026 Mode 2 re-run (Claude Code, B-126/B-130 applied) correctly identified
the temporal ordering and reduced the verdict to SUSPICION.

### Root cause

`_analyze_safari` has access to individual Safari entry timestamps but does not
cross-reference them against SMS timestamps from `sms.db`. Each database is parsed
independently in ios_forensics.py. Cross-artifact temporal analysis — "is this search
temporally downstream of a phishing SMS targeting this device?" — requires joint
reasoning across multiple evidence sources that the single-module architecture
does not perform.

### Forensic implication

Any iOS device belonging to a victim of phishing, smishing, or malware infection
will likely produce SAFARI_SUSPICIOUS findings from post-incident remediation
searches. These are true positives from the detector's perspective (anomalous
searches are anomalous) but false positives from the verdict perspective (the
device user is a victim, not a perpetrator).

**Mode 1 behavior is correct by its own contract**: flagging anomalous searches is
appropriate. The limitation is that SUSPICION (the correct verdict for the combined
evidence) cannot be reliably distinguished from INTENT at the ios_forensics.py
layer without temporal cross-artifact reasoning.

### Mitigation

In Mode 2 analysis, always cross-reference SAFARI_SUSPICIOUS findings against SMS
timestamps before interpreting direction of causality. The temporal ordering
phishing SMS → remediation search is the canonical victim pattern.

For Mode 1, the SAFARI_SUSPICIOUS finding carries the right evidential weight; the
interpretation layer (Mode 2 analyst or Mode 2 LLM) must apply the temporal context.
Document the finding with its timestamp and the SMS that precedes it.

**Fix path (if desired):** Extend `_analyze_safari` to accept a list of known
phishing timestamps (from `_analyze_sms` output) and flag any SAFARI_SUSPICIOUS hit
within N hours after a phishing-candidate SMS as `VICTIM_RESPONSE` rather than
`SUSPICIOUS_SEARCH`. Requires calibration of N (48h is empirically correct for
this case; may not generalize). Deferred — requires cross-module data flow
change and calibration corpus.

---

## L-060 — `SecurityAudit` Wrote `security_audit.log` Into `VIGIA_EVIDENCE_DIR` [RESOLVED B-135]

**Registered 2026-07-14. Resolved 2026-07-16 by B-135. Historical condition retained as an audit record.**
**Mode affected:** Mode 1 (`vigia_agent.py`) when `VIGIA_EVIDENCE_DIR` is set.
**Discovered:** VIGIA-MAGNET-2022-iOS-JESS Mode 1 runs, 2026-07-14.

### Description

`vigia/security/security.py` line 47:

```python
_DEFAULT_LOG_DIR: Final[str] = os.getenv("VIGIA_EVIDENCE_DIR", "/var/log/vigia")
```

When `VIGIA_EVIDENCE_DIR` is set (required for all investigations), `SecurityAudit`
defaults its log path to `Path(VIGIA_EVIDENCE_DIR) / "security_audit.log"`, writing
an audit log file directly into the evidence directory.

This violates the VIGÍA evidence read-only invariant: "Evidence is read-only.
Never write to `VIGIA_EVIDENCE_DIR`." (CLAUDE.md §5.1, VIGÍA CLAUDE.md Invariant 1).

### Forensic implication

The written `security_audit.log` modifies the evidence directory's mtime and
directory listing, potentially invalidating any directory-level hash taken before
the run. If the investigation uses forensic hash verification at the directory level
(e.g., for Daubert chain-of-custody purposes), the post-run hash will not match the
pre-run hash due to this added file.

Note: The file is an audit trail, not forged evidence. Its presence does not
affect the correctness of VIGÍA's analysis. The risk is Daubert credibility: a
defense expert could point to the modified evidence directory as a chain-of-custody
gap.

### Resolution and validation

B-135 changed the default to:

```python
_DEFAULT_LOG_DIR: Final[str] = os.getenv("VIGIA_LOG_DIR", "/var/log/vigia")
```

`VIGIA_EVIDENCE_DIR` now only identifies evidence. `VIGIA_LOG_DIR` controls the
audit destination; an explicit `SecurityAudit(log_path=...)` still has priority,
and the pre-existing secure temporary fallback is used when the configured log
directory cannot be written.

`tests/test_b135_security_log_dir.py` verifies all five relevant contracts:
the default ignores `VIGIA_EVIDENCE_DIR`, honours `VIGIA_LOG_DIR`, retains the
`/var/log/vigia` fallback, leaves an evidence directory byte-for-byte empty in
an end-to-end write, and preserves explicit log-path precedence.

---

## L-061 — CI import contract flags env-injected phantom modules from the in-repo `.venv` [DOCUMENTED]

`tests/test_requirements_ci_contract.py::test_all_test_imports_resolve_with_requirements_ci`
walks the import closure of the test suites and, for any module whose spec
origin resolves *inside the repository root*, follows that module's own imports
too (it is trying to prove the project's own code closes over `requirements-ci.txt`).

A virtualenv commonly lives at `<repo>/.venv`, so its installed third-party
packages sit *under the repository root*. The scan therefore descends into
`.venv/**/site-packages` and parses the imports of installed dependencies. Two
imports found there do not resolve in an isolated CPython 3.12 virtualenv:

- **`annotationlib`** — a standard-library module introduced in **Python 3.14**
  (PEP 749). Forward-compatibility shims in installed packages reference it; it
  is absent from `sys.stdlib_module_names` on 3.12, so `find_spec` fails.
- **`apport_python_hook`** — an **Ubuntu system module** shipped in
  `/usr/lib/python3/dist-packages`. It resolves for the system interpreter but
  not inside an isolated venv.

Neither is a project dependency; both are environment noise reached only because
the scanner crosses into `site-packages`. They are declared in `KNOWN_CI_GAPS`
citing this limitation so the contract does not report environment noise as a
broken test import. The test passes as-is under the system interpreter (where
`apport_python_hook` is present).

Planned/alternative fix (deliberately not taken here to keep the change
surgical): exclude `site-packages` / `.venv` from the scanner's in-repo follow,
so installed dependencies are treated as third-party leaves rather than walked.
That is a broader change that also interacts with the third-party coverage
assertion and is tracked separately.

---

## L-062 — Scorer Hard Temporal Gate Trusted `temporal_violations` Without Validating It Against Artifact Timestamps [MITIGATED B-172; H-01 tolerance remains]

**Registered 2026-07-17. Claim-authority portion mitigated 2026-07-21 by B-172. The separate H-01 tolerance-window decision remains open.**
**Mode affected:** all modes that call `vigia_scorer._vigia_score` (the deterministic core).
**Discovered:** 2026-07-17, temporal-gate characterization (`tests/characterization/test_temporal_gate_curve.py`).
**Severity class:** integrity/contract gap (P2-class). NOT a runtime-exploitable vulnerability — it requires control of the case-construction input, not a network/attacker surface — but it is a Daubert integrity concern because it sits at the highest-authority verdict rung.

### Description

The scorer's hard temporal gate (`vigia_scorer.py` L1120-1122) fires an
**unconditional MALICE** verdict (confidence 0.95) as soon as the case's
`temporal_violations` list contains an entry with
`type == "EFFECT_BEFORE_CAUSE"` and `severity >= 0.9`:

```python
hard_temporal = any(
    v.get("type") == "EFFECT_BEFORE_CAUSE"
    and _sev_float(v.get("severity", 0), 0.0) >= 0.9
    for v in violations          # violations = case.get("temporal_violations", [])
)
```

It reads the asserted violation **verbatim**. It never parses the artifacts'
timestamps and never reads `delta_seconds`. The characterization test pins the
consequence: the gate fires MALICE for *every* delta, including `0` and `+2`
(the effect AFTER the cause — no violation at all), because the input asserts
the violation and the scorer trusts it.

Data-flow finding (verified 2026-07-17): **no production detector emits
`EFFECT_BEFORE_CAUSE`.** CAIE's live temporal rule emits
`TEMPORAL_CAUSALITY_VIOLATION` (path b), which *does* derive the sign from
real structured timestamps and *does* carry the R3-1 out-of-range guard.
`EFFECT_BEFORE_CAUSE` in `temporal_violations` is populated **only from the
case JSON** — i.e. examiner-authored / fixture data. There is no producer
test guaranteeing that population is correct, because there is no producer.

### Forensic implication

VIGÍA's highest-authority verdict rung (unconditional MALICE, "physical law
violation") can rest on an input field that is never cross-checked against the
evidence it claims to describe. A defense expert could show that the MALICE
verdict would fire identically for a non-violating timeline, because the gate
does not validate the asserted pair. Under Daubert this is a falsifiability
gap: the gate's conclusion is not independently reproducible from the artifact
timestamps.

### B-172 mitigation and remaining H-01 work

B-172 reconstructs every categorical `EFFECT_BEFORE_CAUSE` claim from the
referenced artifact IDs and their top-level ISO-8601 timestamps. The pair must
be unique, timezone-explicit, within CAIE's fixed plausibility window, and
actually satisfy `effect < cause`. A high-severity claim that fails any part of
that check is retained as `unverified_hard_temporal_violations`, contributes no
temporal trust penalty, and forces `ABSTAIN` rather than categorical `MALICE`.
The validated pair is exposed in the sealed score result.

This deliberately does **not** decide the tolerance policy: a verified negative
ordering still follows the former categorical gate, including a small skew. H-01
remains tracked in the strategy document for the cross-clock tolerance and CAIE
severity-scaling design.

`tests/test_b172_hard_temporal_pair_validation.py` covers a contradicted
assertion, a missing artifact, and a real inversion. The revised temporal-curve
characterization preserves H-01's no-tolerance negative-delta pin separately.

---

## L-063 — Fallback-Mode `caie_fractures` Carry Verdict Authority From Case JSON (Recognised Types) [RESOLVED B-170]

**Registered 2026-07-18. Resolved 2026-07-21 by B-170. Historical condition retained below as an audit record.**
**Mode affected:** `vigia_scorer._vigia_score` when `from vigia.tools.caie import ...` fails (standalone / CAIE-unavailable mode — a documented, supported mode, file header §"Deployment Modes").**
**Discovered:** 2026-07-18 pattern hunt (T-1), characterized in `tests/characterization/test_verdict_authority_inputs.py`.
**Severity class:** integrity/contract gap (P2-class, sibling of L-062) — requires control of the case-construction input, not a runtime attack surface.

### Description

Historically, when live CAIE was importable, the scorer **recomputed** fractures
from evidence and discarded any `caie_fractures` supplied in case JSON
(`caie_fractures_source == "live_caie"`). When the import failed, it fell back
to `case.get("caie_fractures", [])` and consumed them directly: a fabricated
fracture whose `fracture_type` was in `MALICIOUS_FRACTURE_TYPES` added
`sev*0.45` to the malice boost and could flip NOISE to SUSPICION.

The characterized bound (verified 2026-07-18) required a **recognised** type.
An unrecognised type was inert, but `caie_fractures_source == "json_fallback"`
only disclosed the degraded mode; it did not remove the declared fracture's
authority.

### Forensic implication

### Fix and current contract

B-170 separates disclosure from authority. In CAIE fallback mode every
JSON-declared fracture remains in `caie_fracture_details`, but contributes
neither a malice boost nor a credibility penalty. The sealed
`caie_fracture_authority` field reports that the material is
`unverified_json_no_verdict_authority`.

If the declaration contains a recognised CAIE fracture type, the final result
is `ABSTAIN`, with `unverified_json_caie_fractures` and the score-only
pre-gate verdict/reason retained in the sealed output. The operator must rerun
with live CAIE before VIGÍA can issue a substantive verdict. Live CAIE remains
unchanged: it recomputes its own fractures and may use them normally.

### Validation

`tests/characterization/test_verdict_authority_inputs.py::TestT1FallbackFractureAuthority`
proves the former NOISE -> SUSPICION escalation is gone: the same recognised
JSON declaration now yields zero boost and `ABSTAIN`; an unrecognised type is
still inert; a live CAIE run still discards case JSON and recomputes evidence.

---

## L-064 — `STATISTICAL_UNIFORMITY` Malice Boost Has No Runtime Producer (All Modes) [RESOLVED B-171]

**Registered 2026-07-18. Resolved 2026-07-21 by B-171. Historical condition retained below as an audit record.**
**Mode affected:** all modes calling `vigia_scorer._vigia_score` (NOT gated by CAIE availability — worse reach than L-063).**
**Discovered:** 2026-07-18 pattern hunt (T-2), characterized in `tests/characterization/test_verdict_authority_inputs.py`.
**Severity class:** integrity/contract gap (P2-class, sibling of L-062).

### Description

Historically, `case["temporal_violations"]` entries of
`type == "STATISTICAL_UNIFORMITY"` added `sev*0.35` to
`fracture_malice_boost` **unconditionally in every mode**. A fabricated entry
(severity 1.0) could flip NOISE to SUSPICION (measured: score 0.055 -> 0.375).

Data-flow finding (verified 2026-07-18): **no runtime module emits
`STATISTICAL_UNIFORMITY`.** A grep of `vigia/` finds it only as a weight-table
key (`vigia_scorer.py:328`, `trust_fusion.py`) and in corpus-conversion
scripts (`scripts/convert_break_cases.py`, `convert_synthetic_cases.py`) that
author it into case JSON. An in-code comment previously described it as coming
"from the temporal engine" — a producer that does not exist; the comment has
been corrected (honesty fix, behavior unchanged).

### Fix and current contract

B-171 removes every JSON-only score path: both the explicit malice boost and
the temporal-trust penalty. A declared violation remains counted in
`temporal_violations` and is retained as
`unverified_statistical_uniformity_violations`, but its score contribution is
zero. `statistical_uniformity_authority` explicitly reports
`unverified_json_no_verdict_authority`.

Because a declared regularity claim can be decision-relevant yet has no
producer under the scorer's contract, the final result is `ABSTAIN` and retains
the score-only pre-gate verdict/reason. This applies in live and fallback CAIE
modes: availability of CAIE does not validate a statistic CAIE never produced.
The separately callable MCP jitter detector is not treated as a producer; it
has a different input/output contract and is not wired into the sealed scorer.

**Known corpus effect:** `case_002_log_fabrication` retains its scenario label
`expected_verdict: SUSPICION`, but its current deterministic result is
`ABSTAIN` until the case carries raw interval evidence and a deterministic
scorer detector derives the statistical claim. The label documents the
scenario; it does not override the evidence contract.

### Validation

`tests/characterization/test_verdict_authority_inputs.py::TestT2StatisticalUniformity`
proves the former NOISE -> SUSPICION transition is gone in both live and
fallback CAIE modes. `tests/test_invariant4_fraction_accumulators.py` proves a
declared SU claim cannot add to a live CAIE fracture boost.

---

## L-065 — `provenance_chain` Trust Uses Length Only; Hashes Are Never Verified [DOCUMENTED]

**Registered 2026-07-18. Status: DOCUMENTED — doctrine decision pending (T cluster). L-number PROVISIONAL until merge.**
**Mode affected:** all modes (`vigia_scorer._vigia_score` epc_factor path; CAIE `add_artifact` len<2 decay).**
**Discovered:** 2026-07-18 pattern hunt (T-3), characterized in `tests/characterization/test_verdict_authority_inputs.py`.
**Severity class:** integrity/contract gap (P2-class, sibling of L-062).
**Layering question answered (2026-08-09, `docs/DEEPSEEK_AUDIT_20260809.md`):** no,
this is not verified in another layer. `ChainOfCustody`
(`vigia/core/chain_of_custody.py`) exists and is threaded through the SIFT
analyzers, but always as `Optional[...] = None`, and nothing connects an
instance of it to the scorer's `provenance_chain` field. The skeleton is real;
it is not wired to the trust computation.

### Description

The chain-of-custody trust factor (`epc_factor`, `vigia_scorer.py:721-728`)
consults **only `len(provenance_chain)`**; the hash strings are never
recomputed or matched against artifact content. Verified 2026-07-18: two
different sets of garbage hashes of the same length produce the identical
score, and chain length alone moves `mean_effective_trust` (e.g. 0.80 -> 0.37)
with zero real hashes. CAIE's own path likewise only checks `len < 2`
(`caie.py:790-795`). The bridge additionally fabricates a placeholder
provenance_chain when one is absent (`vigia_integration_bridge.py:447-448`).

### Forensic implication

An examiner can set custody trust by supplying an arbitrary-length list of
fabricated hash strings; the "chain of custody" the trust factor claims to
model is a length counter, not a verified cryptographic chain. Under Daubert
this is a falsifiability gap: the custody trust is not reproducible from the
artifact content the hashes claim to attest.

### Doctrine decision (pending, Anna)

Options: (a) verify at least the terminal hash against the artifact content
where the content is available; (b) rename the factor to state honestly that
it models declared-chain-length, not verified custody; (c) accept as
documented. Behavior is pinned unchanged until decided.

---

## L-066 — A high-severity C2 IoC can read as NOISE when the competing memory artifact was never network-analyzed (T-5 / B-149) [RESOLVED 2026-08-01 — B-149]

Surfaced by B-148 (CAIE absence≡negative fix). The LOG_VS_MEMORY fabrication
rule previously fired whenever a memory artifact lacked network fields, which
incidentally prevented a high-spoofability C2 `log_entry` from collapsing to
NOISE. B-148 correctly stops that firing (absence of network data is not a
contradiction — "not analyzed" != "analyzed, no activity"), which removes the
incidental protection.

**Reproducible (synthetic) scenario:** a `log_entry` with a confirmed C2 IoC
(`raw_score=0.95`, non-reserved `dst_ip`) competing with a low-spoofability
exculpatory `memory_process` artifact that was never network-analyzed (no
`dest_ip`/`source_ip`/`network_connections`) and carries no explicit
`metadata["verdict"]` → sealed verdict = NOISE. See
`vigia/tests/adversarial/test_spoofability_correlation_attack.py::test_red_team_anchor_bypass`
(`xfail(strict=True)`).

**Scope (honest):** the B-148 comparative corpus gate showed **0/201 real cases**
exhibit this — the anti-collapse behavior rested on a false positive, and no real
case relied on it. T-5 is a latent behavior, not a live corpus regression.

**Daubert posture:** a documented WARN beats a false PASS. The correct fix — a
high-severity, independently corroborated IoC must resist NOISE collapse on its
own merits (a scorer-level IoC floor), not via a fracture coupled to absent
memory — is tracked as B-149 and pinned until designed deliberately.

---


**RESOLVED 2026-08-01 (B-149).** The proposed remedy in this entry — an IoC
floor — was discarded after measurement. The defect was not that the IoC
lacked a floor but that monotonicity was inverted: a memory artifact that
never examined the network layer made the case read *more benign* than having
no memory artifact at all (NOISE vs INCONCLUSIVE), while one that did examine
it produced MALICE. The fix forbids concluding NOISE about a layer no artifact
analysed; it does not raise any score. An IoC floor would have forced
SUSPICION from a single highly-spoofable uncorroborated log — the opposite
error, and the one the Daubert corroboration gate exists to prevent.
Corpus impact: 0 of 282 cases.

## L-068 — The epistemic kernel is integrated but not wired into the verdict path [DOCUMENTED]

`vigia/core/ontology.py` (epistemic constitution) and
`vigia/core/reasoning/abduction.py` (abductive tribunal) are present, tested
(`tests/test_epistemic_kernel.py`), and **deliberately inert with respect to
scoring**. They generate hypotheses; they emit no verdict, score, or sealed
output. No module in the deterministic pipeline imports them, and
`test_kernel_is_not_imported_by_the_scoring_pipeline` fails if that changes.

**Forensic implication:** no sealed verdict, bundle hash, or corpus figure
reported elsewhere in this repository is affected by, or benefits from, this
layer. A reader must not treat the presence of an abductive tribunal in the
tree as evidence that VIGÍA's verdicts pass through it. They do not.

**Why it is not wired in:** connecting a hypothesis generator to the decision
path changes what the scoring pipeline is, and would require deliberate design
plus full corpus re-validation. That is a maintainer decision taken on purpose,
not a side effect of an integration commit.

**Open design questions inside the layer** — residual free-string typing in
`ClaimContext.prerequisites`, prose-primary `Hypothesis.statement` where a
causal structure belongs, and the absence of an `AssessmentMatrix` builder —
are recorded in `docs/EPISTEMIC_KERNEL.md` rather than answered by guesswork.
Each involves inventing taxonomy that belongs to the human maintainer.

**Attribution:** architecture by Kimi (Moonshot AI), design review by ChatGPT
(OpenAI), integration and defect repair by Claude (Anthropic). Eight defects
were repaired on integration (D-1..D-8), two of which prevented the modules from
importing or running at all; see `docs/EPISTEMIC_KERNEL.md`.

---

## L-070 — Case-JSON fields that are *outputs* can carry verdict authority (B-225) [MITIGATED FOR GRICE]

`_vigia_score` reads 10 fields from the case dict. Some are genuine inputs
(`artifacts`); others are **outputs of upstream analysers** that the pipeline
writes back into the same dict before scoring. Where the same key carries both
a live-computed result and an externally-declared one, the scorer cannot tell
them apart without a provenance marker.

Audited field by field (2026-08-01):

| Field | Authority guard |
|-------|-----------------|
| `caie_fractures` | `caie_fractures_source` — B-170 / L-063 |
| `temporal_violations` | pair reconstructed from artifacts — B-172 / L-062 |
| `expected_verdict` | blinded before scoring — B-075 |
| `grice_verdict`, `grice_deception_probability`, `pipeline_grice` | `grice_source` — **B-225, this entry** |
| `provenance_analysis` | consumed only in the conservative direction (broken chain → abstain) |
| `peirce_chain` | pass-through to the output; no authority |
| `grice_signals` | read and never consumed — dead assignment, removed by B-225 |

**Residual limitation.** The pattern is structural, not exhausted: any future
field that carries an analyser's output back into the case dict inherits the
same hazard, and nothing in the type system prevents it. The mitigation is a
convention (`<producer>_source` marker + the shared authority gate), not an
invariant the code enforces. A new decision-relevant field added without a
marker would silently regain authority.

The general remedy — a typed epistemic state that forces every stage to
declare what it measured, what was missing, and what gaps remain, with the
verdict derived from those rather than asserted alongside them — is a design
change, not a patch, and is not adopted here.

---

## L-069 — Mode-1's self-correction loop never actually iterates (B-224) [RESOLVED 2026-08-15]

> **Resolved 2026-08-15.** The loop is reachable: `VERDICT_FLIP`'s vocabulary
> was aligned and `CONTRADICTION_THRESHOLD` lowered 2 → 1. Measured corpus
> impact: zero — no case moved. **The diagnosis below is preserved as written
> but was wrong on one point**: rule 3 is not "the only reachable rule", it is
> unreachable by arithmetic. See "Correction and resolution" at the end of this
> entry before citing anything above it.

`vigia_agent.py`'s `ContradictionDetector.detect()` implements 4 rules. 3 of
them read fields no Mode-1 producer ever writes: `ENTROPY_VS_BEHAVIORAL` and
`VERDICT_FLIP` filter on a `signal["tool"]` key Mode-1 signals never carry
(they carry `evidence_type`/`source`), `SEMIOTIC_VS_TECHNICAL` reads
`module_results["technical_result"]`, which no producer in this repository
writes, and `VERDICT_FLIP` additionally checks for the literal string
`"BENIGN"` where Mode-1 emits `NO_*_ANOMALY_DETECTED`. Only
`CONFIDENCE_COLLAPSE` is reachable, and it contributes at most 1
contradiction. `CONTRADICTION_THRESHOLD = 2` gates `_apply_self_correction`
on `len(contradictions) >= 2`, so the maximum reachable count (1) never
meets it — the correction branch cannot fire for any possible input, not
merely none observed in the current corpus. Measured on the 21 cases under
`cases/input/`: `self_corrections_applied=0`, `iterations_executed=1`,
`sans_compliance.self_correction=False`, `contradictions_found=0` in every
case's `audit_trail`.

**Forensic implication:** no sealed verdict in this repository has ever
passed through a live self-correction iteration in Mode 1. The mechanism is
architecturally present (correct logic per rule, verified with control
tests that trigger each rule using the *wrong* field names to prove the
logic itself is not broken) but unreachable end-to-end, by construction.

**Distinct from the Daubert Corroboration Gate** (`vigia_scorer.py`,
imported by `vigia_api.py` / `sift_orchestrator.py` — the Mode 2/API path).
That gate is live, gates pre-emission, and is unrelated: `vigia_agent.py`
never imports `vigia_scorer.py` (verified, zero references). CLAUDE.md's
"VIGÍA's self-correction occurs pre-emission" passage describes that gate,
not this loop — the two must not be conflated when reading either document.

**Why not fixed:** every possible fix touches sealed verdicts. A live
correction rewrites `abduction["best_hypothesis"]`
(`OVERRIDE_ABDUCTIVE_CONCLUSION` / `ESCALATE_TO_CRITICAL`), so reviving any
one rule, or lowering `CONTRADICTION_THRESHOLD`, can change verdicts on real
corpus cases. Reviving a single rule alone would not even help: the reachable
maximum stays at 1, still below threshold 2, unless the threshold is also
revisited. A real fix requires deciding, together and with a corpus
dry-run: which rules to align to Mode-1's real field names/vocabulary,
whether `SEMIOTIC_VS_TECHNICAL` needs a producer or should be retired as a
dead concept, and whether `CONTRADICTION_THRESHOLD` should drop given how
many rules are actually live. None of that has been decided.

**Applied now (this entry, B-224):** honest-degradation documentation only,
zero verdict risk. `vigia_agent.py`'s module docstring, class docstring,
`ContradictionDetector`'s own docstring, and `--help` output all named the
mechanism as functioning ("automatic", "Max iterations: 3" implying
iteration happens); all four now state the true reachability status and
point here. `TEMPORAL_VS_CONTENT`, listed in the old docstring as a 5th
contradiction type, was never implemented at all — removed from the type
list, noted separately.

Permanent test: `tests/test_b224_contradiction_detector_dormancy.py` (10
tests, pinning the current broken state — they will FAIL the moment someone
wires a producer or aligns a rule's vocabulary, which is the point) and
`tests/test_b224_self_correction_docs_are_honest.py` (locks in the corrected
docstrings/`--help` text against silent drift back to the false claim).

### Correction and resolution (2026-08-15)

**The entry above named the wrong survivor.** It records
`CONFIDENCE_COLLAPSE` (rule 3) as "the only reachable rule", contributing at
most 1 contradiction. Rule 3 is in fact **unreachable through
`_detect_and_correct` on both of its MCA branches**, and unreachable by
arithmetic rather than by a missing producer:

`_detect_and_correct` derives `mca_score` as the mean of the very confidences
rule 3 then thresholds on. The rule requires `mca > 6/10` while more than
`7/10` of the terms are `< 3/10`. With `k/n > 7/10` the mean is bounded above
by `1 − 7/10·(k/n) < 51/100`, which can never exceed `6/10`. Confirmed three
ways: the algebraic bound, an exhaustive search over a 1/20 confidence lattice
up to 7 signals (1,184,039 combinations, no counterexample), and the z-score
fallback branch — which is taken only when no signal carries a `confidence`
key, in which case rule 3's own `.get("confidence", 1)` default makes the
low-confidence count 0. Rule 3 fires only against an aggregator that is *not*
the plain mean of these confidences; no caller supplies one.

So the reachable maximum was 1 before the fix and the surviving rule was
**rule 4, not rule 3** — which changes the fix. The entry's own reasoning
("reviving a single rule alone would not even help: the reachable maximum
stays at 1, still below threshold 2") turns out to apply to the vocabulary
alignment as well: fixing `VERDICT_FLIP` without touching the threshold would
have left the loop exactly as inert.

**Applied.** The three coupled decisions the entry left open, taken together:

1. **`VERDICT_FLIP` aligned.** New module constant `BENIGN_HYPOTHESES`
   (`BENIGN`, `NO_ANOMALY_DETECTED`, `NO_SEMIOTIC_ANOMALY_DETECTED`) replaces
   the bare `"BENIGN"` literal. `"BENIGN"` is retained because
   `vigia/verdict/quadripartite.py` and the integration bridges do emit it.
   Rule 4 is now live and is the only live rule.
2. **`CONTRADICTION_THRESHOLD` 2 → 1.** Required, per the arithmetic above.
   This does **not** weaken the two-independent-source bar the verdict scale
   applies to INTENT/MALICE: rule 4 already requires `len(critical_signals)
   >= 2` inside its own predicate, so the two-source requirement moved into
   the rule instead of being counted across rules.
3. **Rules 1 and 2 left dormant, deliberately, and now reported.** Neither
   was cosmetically re-keyed. Rule 1 was *not* re-pointed at `source`: that
   field holds collection tools (`sift_netflow`, `Plaso/WinEVT`, …), not the
   analytic module names the rule compares, so a rename would have made it
   look wired while still never matching — it needs a producer. Rule 2 has no
   producer for `technical_result` anywhere in the repository. Both, plus
   rule 3, are now emitted per run in the audit trail's `rules_not_evaluable`,
   so "no contradictions" is distinguishable from "could not check" (honest
   degradation).

**Corpus impact: ZERO.** All 21 cases under `cases/input/` re-run against the
patched agent: no verdict changed, no correction applied, every case still
converges in 1 iteration. No signal anywhere in the corpus exceeds `|z| > 3`,
which is why rule 4 stays quiet on real data — the loop is now reachable and
dormant, not reachable and active. `self_corrections_applied = 0` remains the
honest observed value; what changed is that it is no longer the *only
possible* value.

Reachability is proven end-to-end instead of asserted:
`test_self_correction_applies_end_to_end` drives a synthetic Mode-1-shaped
input through `_detect_and_correct` and asserts the verdict is actually
rewritten (`NO_SEMIOTIC_ANOMALY_DETECTED` →
`MALICIOUS_INTENT_SUSPECTED [OVERRIDE: …]`).

**This also closes B-151(b)**, whose remaining blocker was this one. The
chained `contradiction_detector` event CLAUDE.md mandates was already wired
in `vigia/core/reasoning_trace.py`; it had no input. New test
`tests/test_b151b_contradiction_chain_emitted.py` drives detector → correction
→ sealed trace and asserts the chained entry appears with its full schema and
bundle-level tail anchor.

Tests updated to pin the new state rather than the old:
`tests/test_b224_contradiction_detector_dormancy.py` (17 tests — including the
arithmetic proof for rule 3 and a `CONTRADICTION_THRESHOLD == 1` pin, so the
coupled decision cannot drift back silently) and
`tests/test_b224_self_correction_docs_are_honest.py` (13 tests — the risk
inverted from overclaiming to stale under-claiming, and both directions are
now guarded). Full suite after the change: 2138 passed, 0 failed.

---

## L-071 — Cross-domain corroboration counts domain PRESENCE, not domain MASS [OPEN]

**Affects:** `vigia_scorer.py::_vigia_score`, B-068 corroboration gate (R4-3 v2),
cross-domain branch |
**Status:** [OPEN] 2026-08-09, POST HACKATHON — calibration-doctrine question,
deliberately **not** silently patched (same posture as L-049). Refinement of the
B-092 residual ("a D3+D4 mix still opens the cross-domain branch").
**Severity:** Medium — invariant/semantic (verdict-path)
**Origin:** external audit (DeepSeek), verified against live code. The finding **as
stated** was refuted; a different mechanism was confirmed — see "Refuted as stated".
**Document:** `docs/DEEPSEEK_AUDIT_20260809.md` (Finding 2).

**Description:** the cross-domain branch opens on
`_n_domains >= 2 AND (_n_gate_arts >= 4 OR len(_gate_types) >= 3)`. `_n_domains`
is `len(set(_dom_arts))` — the count of *distinct collection domains represented*.
A domain is "represented" by any artifact whose `adjusted_score > _M2_MIN_SIGNAL_ADJ`,
and that constant is **exactly `0.0`** (strict `>`). Consequently a **single artifact
of arbitrarily small positive evidential value** constitutes a full corroborating
domain, and can flip a verdict that the gate had otherwise correctly capped.

**Measured (`tests/test_l071_cross_domain_pivot.py`):**

```
 16× D3 filesystem_metadata (1 domain)             → SUSPICION  0.5888
   + 1× network_flow raw=0.01                      → MALICE     0.6152
   + 1× network_flow raw=0.001                     → MALICE     0.6145
   + 1× log_entry    raw=0.001                     → MALICE     0.6145
   + 1× network_flow raw=0.0    (control)          → SUSPICION  0.5888
```

The pivot moves the **score** by +0.026 and the **verdict** by a full rung. The
verdict change is therefore not carried by evidential mass; it is carried by the
cardinality of a label. `raw_score=0.0` correctly does not corroborate — `0.0` is
the only excluded value.

**Refuted as stated (recorded for provenance):** the audit asserted that "Noisy-OR
lets the hard domain be *activated* by the quantity of soft noise". This is **false**
in this code: `r43_domain_scores` is computed per domain over that domain's own
indices only (`_by_domain`), so soft artifacts contribute zero mass to a hard
domain's score. The audit also assumed `caie.py::_SOURCE_MATERIALITY_FLOOR = 0.05`
would exclude a `raw_score=0.01` artifact. That floor is in a **different module**
and governs CAIE's own `independent_sources` / `confidence_penalty`; it has no
authority over the scorer's B-068 gate, whose floor is `_M2_MIN_SIGNAL_ADJ = 0.0`.

**Why the two obvious fixes are refuted by the corpus (measured, not assumed):**

1. *Raise the per-artifact floor above 0.* Already measured and rejected in the
   `_M2_MIN_SIGNAL_ADJ` calibration note (`vigia_scorer.py` ~L145, Round 2.1):
   canonical MALICE cases corroborate with artifacts at adjusted **0.0017–0.002**,
   while excluding the VIGIA-CAN-029 diluent needs **> 0.013** — an empty interval.
   The pivot at `raw=0.01` lands *inside* that empty interval, so no corpus-compatible
   per-artifact floor excludes it.
2. *Require ≥2 artifacts per counted domain.* Refuted by the corpus: a large share of
   canonical MALICE cases open this branch with reasons of the form
   `cross-domain (4 domains, 4 artifacts)` / `(3 domains, 4 artifacts)` — i.e. by
   pigeonhole, legitimate canonical cases rely on domains represented by **exactly one**
   artifact. A count floor would flip them.

**Forensic implication:** a party able to introduce one throwaway artifact of a
second collection domain — at a `raw_score` low enough to attract no scrutiny — can
convert a gate-capped SUSPICION into a sealed MALICE. Treat MALICE verdicts whose
`reason` cites the cross-domain branch as requiring the corroborating domain's own
mass to be inspected, not merely its presence.

**Recommendation (record only, not implemented):** the gate should consult
`r43_domain_scores`, which `_vigia_score` **already computes** (~L1149) and currently
uses only for traceability — requiring the corroborating domain's own Noisy-OR score
to clear a floor tests domain *mass* rather than domain *presence*, and is immune to
both refutations above (it is neither a per-artifact floor nor a per-domain count).
This mirrors the doctrine CAIE already adopted for the same bug class in its own
corroboration count (`_SOURCE_MATERIALITY_FLOOR`, "a group only counts toward
independent_sources if some member's raw_score reaches this floor"). Any such change
is a scoring-semantics change and requires the full 199-case comparative gate, per
the B-091/B-092 precedent.

**Tests:** `tests/test_l071_cross_domain_pivot.py` — characterization only. They pin
the measured behavior so a future recalibration is deliberate and visible; they do
**not** assert the behavior is correct.

---

## L-072 — `semantic_role` is a DECLARED input with verdict authority; a label alone neutralizes MALICE [OPEN]

**Affects:** `vigia_scorer.py::_vigia_score` (D1 exculpatory/Eco block) |
**Status:** [OPEN] 2026-08-09, POST HACKATHON — doctrine decision pending. Sibling
of L-065 (declared chain length) and L-070 (case-JSON fields carrying verdict
authority). **Extends L-054**, whose protective rationale does not cover this path.
**Severity:** Medium-High — verdict-path, false-negative direction
**Origin:** external audit (DeepSeek), verified against live code. The **attack
mechanism as stated was refuted**; a simpler and stronger one was confirmed.
**Document:** `docs/DEEPSEEK_AUDIT_20260809.md` (Finding 5).

**Description:** `_semantic_role(a)` reads `semantic_role` straight from the case
JSON (default `incriminatory`). Artifacts declared `exculpatory` are removed from
scoring unless the Eco filter fires on their *text* (`description` +
`metadata.content_preview`). Nothing verifies the declaration against the
artifact's own content, type, score, or provenance.

**Measured over the corpus (163 cases scored; 52 emit MALICE/INTENT):**

```
relabel ALL artifacts exculpatory (LABEL ONLY, original text untouched)
    -> 37 / 52 MALICE cases lose the MALICE verdict (13 of them to NOISE)
relabel ALL BUT ONE (strongest first, label only)
    -> 35 / 52 lose MALICE
relabel ALL + neutral description text
    -> 52 / 52 collapse to NOISE, score 0.0000
```

**Refuted as stated (recorded for provenance):** the audit proposed writing a
description resembling a honeypot / forensic investigation "to fool the Eco
filter". That is **backwards**: bait terms make the Eco filter FIRE, which
**retains** the artifact in scoring. Suppression requires the opposite — a bland
description — and in 37/52 cases the original text was already bland enough that
**no text crafting was needed at all**. The real exposure is larger than the one
reported, and the Eco filter's contribution is partial (it saved 15/52).

**Relation to L-054:** L-054 states the floor doctrine prevents "malicious actors
from planting exculpatory metadata to suppress alerts", and analyses the case where
a residual incriminatory artifact remains and the B-028/B-065 floor re-raises it.
That reasoning does not reach the path measured here: when every device artifact is
declared exculpatory, `_vigia_score` takes an **early return** emitting
`NOISE, score 0.0, confidence 0.9` *before* any floor applies. A floor can raise a
low alert; it cannot restore a MALICE verdict that was never computed.

**Mitigating fact (verified, must be stated):** the suppression is **auditable, not
silent** — every removed artifact is recorded in `refutation_context.set_aside`, and
the emitted `reason` names the exculpatory path explicitly. The threat model is a
corrupt or coerced case author (insider), not an anonymous remote attacker.

**Scope of the measurement (honest bound):** measured at `_vigia_score` level, not
through the full Mode 1 pipeline. Mode 1's hypothesis-level floors may re-raise some
downgraded cases to SUSPICION; they cannot restore MALICE.

**Recommendation (record only, not implemented):** treat `semantic_role` as a
*claim requiring corroboration* rather than an instruction — e.g. require the
declaration to be consistent with the artifact's evidence class and score before it
can remove evidence, and/or forbid the total-relabel early return from emitting
NOISE at confidence 0.9 (ABSTAIN is the honest verdict when the examiner has
declared the entire evidence set away). Any change here is scoring doctrine and
requires the full corpus gate.

**Tests:** `tests/test_l072_declared_inputs_and_threshold_edge.py` — characterization.

---

## L-073 — Verdict thresholds compare a `_dround` float against a `Fraction`; the exact grid point grants the higher rung [OPEN]

**Affects:** `vigia_scorer.py::_vigia_score` verdict ladder |
**Status:** [OPEN] 2026-08-09 — latent edge, **zero corpus incidence measured**.
**Severity:** Low — exactness/boundary, anti-conservative direction
**Origin:** external audit (DeepSeek). **Direction of the finding was inverted.**
**Document:** `docs/DEEPSEEK_AUDIT_20260809.md` (Finding 4).

**Description:** the ladder evaluates `final_score > Fraction(33, 100)` (likewise
`10/100`, `8/100`, and the `0.65` single-artifact cap). `final_score` is a float
from `_dround(..., 4)`, i.e. always a 4-decimal grid point — and `0.3300` is such a
point. Python compares `float` against `Fraction` **exactly**, so the outcome depends
on which side of the rational the nearest double falls.

Measured: for all four thresholds the nearest double sits **above** the exact
rational (`float(0.33) − 33/100 = 7/450359962737049600 > 0`). A score landing exactly
on the threshold therefore satisfies a **strictly-greater** test that exact decimal
arithmetic would fail — the case is promoted one rung.

**Refuted as stated:** the audit claimed a false **negative** (a MALICE case demoted
to SUSPICION by rounding down). The bias runs the other way. Its concrete example is
also self-defeating: with a strict `>`, `Fraction(33,100)` is not MALICE under exact
arithmetic either, so there is nothing to lose.

**Not a determinism violation:** `_dround` yields the same double on every platform;
Invariant 4 (`Fraction`/`Decimal` determinism) is intact. This is boundary exactness,
not cross-platform divergence.

**Reachability (measured):** across 163 corpus cases, **zero** land on or within two
grid steps of any threshold. The defect is latent, not active — a crafted case could
target it.

**Adjacent latent hazard (recorded, not active):** `_dround` returns `0.0` for any
argument that is not `int`/`float`, so a `Fraction` or `Decimal` reaching it would be
silently zeroed rather than raising. Probed over 80 corpus cases: only `float`
arguments occur (4449 calls), so the path is currently unreachable — but the guard
fails silent in a module that uses both `Fraction` and `Decimal`.

**Recommendation (record only):** keep the ladder in exact arithmetic end-to-end
(compare `Fraction` against `Fraction`), or state the threshold semantics as
"≥ next grid step" so the emitted rule matches the emitted verdict.

---

## L-074 — Audience reports render sealed fields verbatim and cannot fill gaps a family does not record [DOCUMENTED]

**Affects:** `vigia/report/` (junior / expert Markdown presentations, EN + ES), the
`vigia_agent.py --audience` hook, `docs/training/examples/` |
**Status:** DOCUMENTED 2026-09-05 — by design. This is a presentation layer with
zero verdict authority; the limitations below are what it inherits from the
bundle it reads, not defects it could fix without inventing content.
**Severity:** Informational — no verdict-path impact by construction
(`tests/test_report_not_in_verdict_path.py` enforces that no sealed module imports it).

**Description:** `python3 -m vigia.report <bundle>` (or `vigia_agent.py --audience`)
renders any of the three bundle families into a junior-SOC and an expert
presentation. Every value is copied verbatim through
`vigia.ui.normalizer` + `vigia.report.adapter`; nothing is computed, rounded,
reconciled or translated. Consequently:

- **Family gaps stay gaps.** Agent bundles carry no per-signal Peircean triad, no
  per-signal verdict and no declared TTP field; MCP bundles carry no granular
  `audit_trail` (L-020); EBS v1 bundles carry no findings list. The report prints
  "not present in this bundle" and never substitutes text from another source.
- **Hashes are not comparable across families** (L-030, L-031). The expert view
  prints each family's own custody anchors and says which ones the family does not
  define. It does not attempt to derive one from another.
- **Sealed floats are printed as sealed.** EBS v1 `decision_trace` holds floats
  (L-021, L-073). The report shows the JSON literal, never a rounded or converted
  value, so the reader sees the same anomaly the verifier sees.
- **A verdict-bearing disagreement is shown, not resolved.** When an EBS v1 bundle
  carries `decision_trace.decision` and `caie_analysis.verdict` with different
  values, both appear with a `verdict_disagreement` notice.
- **INTENT/MALICE without `devil_advocate`** is flagged as a GAP (L-022) and the
  verdict is left untouched. The report cannot supply the missing refutation.
- **MITRE coverage is the local dictionary** (`vigia/tools/mitre_mapping.py`,
  27 techniques, ATT&CK v14.1). Ids outside it get a URL derived from the id and are
  labeled as such; no name or description is invented.
- **Quoted prose keeps its sealed language.** Agent narratives are Spanish/English
  mixed; Mode 2 findings are in whatever language the investigator wrote. An
  English report may therefore quote Spanish text verbatim. That is the record.
- **"Next steps" are generic SOC guidance per rung**, stated as such. They are not
  derived from the bundle and carry no case-specific authority.
- **Worked examples are pinned** (`tests/test_training_worked_examples_pinned.py`).
  A wording change in the renderer requires regenerating and committing them; the
  diff is the review artifact.

**Not a determinism concern:** rendering is a pure function of the bundle bytes
(no clock, no randomness, no environment-dependent strings); byte identity across
fresh interpreters with different `PYTHONHASHSEED`, locale and timezone is tested.

**Kill switch:** `VIGIA_AUDIENCE_REPORTS_ENABLED=false` disables the agent hook. It
is deliberately **not** registered in `vigia/core/config_sentinel.py`: that map
feeds a sealed integrity report, and a presentation flag must not be able to move it.
