# Abductive Audit Report — Unresolved-Bugs Session 2026-07-16

Submitted for multi-AI collective adversarial audit per
`docs/ENGINEERING_DISCIPLINE.md` §6. Findings in this report are claims,
not facts, until each auditor verifies them against the live tree (§4.1).
Every claim below carries a file:line anchor and a reproduction command.

| Field | Value |
|-------|-------|
| Branch | `claude/unresolved-bugs-1231gn` |
| Commits under audit | `85db3af` (B-131/B-133/B-134/B-135), `6b73b45` (B-114/B-136/B-116-partial) |
| Restore point | tag `pre-session-20260716-043649` |
| Method | Peircean triad + abduction/deduction/induction loop + mandatory refutation (Eco), per ENGINEERING_DISCIPLINE §1 |
| Suite | baseline 1376 passed → 1411 passed (+35 new tests), 0 regressions, 188 skipped / 33 xfailed / 1 xpassed unchanged |
| Corpus gate | `run_all_agent.py --rerun`, 201 cases live: 189/201 PASS before AND after each commit; **zero per-case verdict flips** (programmatic diff of `_batch_summary.json`) |
| Sealed bundles | `results/agent_batch/` restored via `git checkout --` after each comparative run — no regenerated bundle was committed |

Reproduction of the gate:

```bash
PYTHONPATH=$(pwd) python3 -m pytest tests/ vigia/tests/ -q --tb=short --ignore=tests/integration
PYTHONPATH=$(pwd) python3 run_all_agent.py --rerun
PYTHONPATH=$(pwd) python3 scripts/dryrun_signal_quality_gate.py   # B-116 measurement
```

---

## Finding 1 — B-131: acquisition metadata not propagated to post-Gamma signals [FIX APPLIED]

**Firstness.** Live reproduction (pre-fix): `run_full_analysis(event_stream=...)`
with `acquisition_overrides = {acquisition_tool, examiner_id, write_blocker_used}`
produced METABOLIC_PROFILER, BEHAVIORAL_FINGERPRINT, UNIFIED_TIMELINE and
ADV_ROBUST signals with none of those metadata fields, and CAIE fired
`ACQUISITION_METADATA_MISSING_CRITICAL`, degrading `base_trust` 0.55 → 0.10.

**Secondness.** The Gamma loop (step 4, `vigia/sift/sift_orchestrator.py`)
injects `_acq_meta` into every raw SIFT signal; signals created *after* the
loop are new `SignalOutput` objects that never pass through it. Baseline:
every signal reaching CAIE should carry examiner-declared custody fields.

**Thirdness (abduced law).** Any signal constructed after the Gamma
convergence point silently loses acquisition metadata. This law predicts the
step-7 timeline signal is also affected, although the original B-131 report
(RAW run 2026-07-14) only named steps 6 and 8.

**Deduction → induction.** Predicted UNIFIED_TIMELINE would also lack the
fields; confirmed live pre-fix. Fix covers steps 6, 7 and 8.

**Refutation attempted.** Benign hypothesis: "engines are derived signals;
maybe custody fields are intentionally omitted for them." Refuted: CAIE
applies the NIST SP 800-86 §4.3 degradation to them regardless, so the
omission has a real, unintended scoring effect; and `_mark_derived` already
labels them `derived` for the corroboration gates — custody metadata and
signal class are orthogonal concerns.

**Fix.** `SIFTOrchestrator._inject_acq_meta` (staticmethod,
`vigia/sift/sift_orchestrator.py:382`), applied at all six post-Gamma
creation sites. Merge precedence identical to the Gamma loop:
`{**acq_meta, **sig.metadata}` — the signal's own metadata wins. `None`
signal and empty `acq_meta` are no-ops.

**Verification.** `tests/test_b131_acq_meta_propagation.py` (6 tests, red
pre-fix). Post-fix live run: all four derived signals carry the three
declared fields; CAIE still (correctly) reports `acquisition_hash` /
`acquisition_timestamp` missing in a synthetic run with no ACQUIRE chain
records — honest degradation preserved.

**What the auditor should try to break.**
- Whether `_inject_acq_meta` can overwrite engine-authored metadata
  (it must not — signal's own keys take precedence).
- Whether any post-Gamma creation site was missed (grep
  `_mark_derived(` — every call must be wrapped).
- Whether corpus JSON cases could shift: chain-derived `_acq_meta` is
  non-empty whenever chain records exist. The corpus gate showed zero
  flips; verify the diff method (baseline `_batch_summary.json` vs post).

---

## Finding 2 — B-133: `knowledgeC.db` hijacked iOS extractions to the macOS engine [FIX APPLIED]

**Firstness.** `[SIFT_SHIM] iOS engine skipped ... macOS engine takes
precedence (B-048)` on the VIGIA-MAGNET-2022-iOS-JESS full extraction; zero
IOS_FORENSICS signals in the sealed bundle.

**Secondness.** `knowledgeC.db` (CoreDuet) ships on both macOS and iOS
(`/private/var/mobile/Library/CoreDuet/Knowledge/`). It was listed only in
`_MACOS_MARKER_FILES`, so `all_names & (_MACOS_MARKER_FILES -
_IOS_MARKER_FILES)` was non-empty for every full iOS extraction.

**Thirdness.** The B-048 guard's exclusivity assumption fails for any
cross-platform artifact present in exactly one of the two marker sets.

**Refutation attempted.** Benign hypothesis: "the guard is correct; JESS was
mis-extracted." Refuted: the artifact is documented as standard iOS content
since iOS 9+, and the workaround (moving the file out) immediately produced
a correct 22-finding iOS run — the routing, not the evidence, was at fault.

**Fix.** `knowledgeC.db` added to `_IOS_MARKER_FILES`
(`vigia/sift/ios_forensics.py:87`). The macOS-exclusive set retains TCC.db,
.fseventsd, .Spotlight-V100, system.log, QuarantineEventsV2, plists. The
shim same-directory precedence guard (`sift_orchestrator.py:766` root shim)
still resolves dual-match directories (iOS skipped, macOS runs).

**Verification.** `tests/test_b133_knowledgec_ios_marker.py` (6 tests,
including routing simulations through the real
`vigia_agent._build_orchestrator_kwargs`). Routing dry-run over every
marker-bearing directory in the repo: 2 directories, zero flips.

**Declared coverage limit (honest degradation, §5.3).** The corpus JSON
cases never exercise directory-marker routing (single files), and the repo
contains no full raw macOS/iOS extraction. The residual risk class — a
macOS directory whose ONLY macOS-exclusive marker is `knowledgeC.db` —
has no instance in the repo and would post-fix route to iOS. Recorded in
the registry as a coverage limitation of the gate, not as an observed
regression. **Auditor decision requested:** whether this residual risk
demands an additional guard (e.g. macOS wins when `Library/Preferences`
layout is present) or acceptance.

---

## Finding 3 — B-134: Wire undetectable in UUID containers [FIX APPLIED]

**Firstness.** JESS extraction contains `store.wiredatabase` (Wire message
DB, located and parsed by ios_forensics itself) yet `_detect_installed_apps`
reported no Wire.

**Secondness.** iOS stores third-party apps under
`Containers/Data/Application/<UUID>/`; no directory is ever named
`com.wire`, so the bundle-ID directory scan cannot match. Signal had the
identical problem and already has a filename special case
(`signal.sqlite`).

**Thirdness.** Bundle-ID directory scanning is structurally blind on iOS;
each messenger needs a filename-based witness file.

**Fix.** Filename detection of `store.wiredatabase`
(`vigia/sift/ios_forensics.py:659-663`), same pattern, weight
(`Fraction(60,100)`, consistent with the `com.wire` entry in
`ENCRYPTED_APPS`) and double-count guard as the Signal case. WeChat was
deliberately NOT touched: no version-portable witness filename exists;
keychain parsing remains a documented limitation.

**Verification.** `tests/test_b134_wire_filename_detection.py` (5 tests:
root, subdirectory, no double-count, Signal regression, empty dir).

**What the auditor should try to break.** False-positive surface of the
filename (`store.wiredatabase` is Wire-specific; challenge welcome), and
whether the one-level-deep glob misses realistic logical-extraction layouts.

---

## Finding 4 — B-135: audit log written into the evidence directory [FIX APPLIED]

**Firstness.** `security_audit.log` appeared inside the evidence tree after
every Mode 1 run with `VIGIA_EVIDENCE_DIR` set (twice observed, JESS
session 2026-07-14). Root: `_DEFAULT_LOG_DIR =
os.getenv("VIGIA_EVIDENCE_DIR", "/var/log/vigia")`.

**Secondness.** Invariant 1: evidence is read-only. Writing anything into
`VIGIA_EVIDENCE_DIR` violates the chain-of-custody posture the tool itself
enforces on others.

**Refutation attempted.** Benign hypothesis: "the default is intentional
and documented." Refuted empirically: `vigia/config.py:63-66` already
resolves `log_dir` from `VIGIA_LOG_DIR` with the same `/var/log/vigia`
default — security.py's use of `VIGIA_EVIDENCE_DIR` was an inconsistency,
not a decision.

**Fix.** `vigia/security/security.py:52`:
`os.getenv("VIGIA_LOG_DIR", "/var/log/vigia")` (design Option A).
`VIGIA_LOG_DIR` documented in INSTALL.md §7 and CLAUDE.md environment
section. The secure temp fallback path is unchanged.

**Verification.** `tests/test_b135_security_log_dir.py` (5 tests, including
an end-to-end check that the evidence directory stays byte-for-byte empty).
Design precaution confirmed: no test in the repo hardcodes the audit-log
path as evidence-dir-dependent (full suite green).

---

## Finding 5 — B-114: CAIE wrapper bypassed the Kimi P0 guardrails [FIX APPLIED]

**Firstness.** `add_from_tool_result()` appended `Artifact` objects directly
to `self._artifacts`, skipping the `_MAX_ARTIFACTS` anti-flooding limit and
the `evidence_type` whitelist that `add_artifact()` enforces.

**Secondness.** Every other producer passes through `add_artifact()`; the
wrapper was the single unguarded entry point. The scorer
(`vigia_scorer.py:652`) feeds CAIE via `add_artifact()` directly — the
verdict path was never exposed.

**Thirdness.** Any convenience wrapper that re-implements its target's
mutation instead of delegating will drift from the target's invariants.

**Fix.** The wrapper now returns `self.add_artifact(Artifact(...))`
(`vigia/tools/caie.py:1175`), propagating the bool verdict. Intended side
effect: wrapper artifacts now receive temporal/network indexing like every
other artifact (previously invisible to the TCV and NETWORK_VS_HOST rules).

**Verification.** `tests/test_b114_caie_guardrail_delegation.py` (6 tests).
Corpus gate: zero flips (consistent with the scorer not using the wrapper).

**What the auditor should try to break.** The signature change
(`-> None` to `-> bool`) — census found no caller consuming the return
value; verify. The indexing side effect — argue whether wrapper artifacts
participating in TCV is desired (position: yes, it restores uniformity).

---

## Finding 6 — B-136 (NEW): the "inject into CAIE" pattern outside the scorer is a structural no-op [DOCUMENTED — architectural decision requested]

This is the load-bearing discovery of the session; it came from executing
B-114's escalation criterion ("census the wrapper's callers").

**Firstness.** Four sites construct `caie = CrossArtifactIncongruenceEngine()`
as a local variable, add artifacts, and return without anything reading the
engine (`detect_fractures()` never called on it; object discarded):
`vigia/forensics/vision_audit.py:514`, `vigia/tools/adversarial_nlp.py:1595`,
`vigia/core/entanglement.py:597`,
`vigia/forensics/temporal_forensics_redteam.py:740`. Repo-wide census of
instantiations: the scorer (builds its own from case signals), caie.py
self-tests, and these four. No singleton, no shared engine, no `get_caie()`.

**Secondness.** An injection API only has effect if some consumer reads the
injected engine. The only consumer is the scorer's locally built engine.
Docstring claims ("Produces DOCUMENT_FORGERY fractures automatically") were
never true outside the discarded object. Three of the four sites
additionally pass kwargs that do not exist in the real signature
(`source_tool=`, `raw_score=`, `description=`, `metadata=` vs the actual
`(tool_name, result, evidence_type, provenance_chain)`) — every call raises
TypeError, silently swallowed and logged as `CAIE_INJECTION_FAILED`. Their
`evidence_type` values (`linguistic_forensics`, `batch_forensics`,
`temporal_fraud`) are also absent from `_VALID_EVIDENCE_TYPES`.

**Thirdness.** Injecting into an ephemeral engine is dead code that emits a
misleading audit trail: `vision_audit` logs `CAIE_ARTIFACT_INJECTED` and
`entanglement` would log `ENTANGLEMENT_CAIE_INJECTED` as successes with no
effect. For a Daubert-posture tool, false audit-trail assertions are an
integrity defect, not just technical debt.

**Refutation that KILLED a would-be fix (Eco's razor).** The obvious B-115
fix — correct the kwargs — was evaluated and rejected: today the broken
call fails honestly (`CAIE_INJECTION_FAILED` in the log). Fixing only the
kwargs would convert that honest failure into a false success (injection
into a discarded object, success-path logging). Strictly worse. No code was
changed at these sites.

**Dissolved decision.** B-115's "normalization decision" (`(mcp-1)/4` vs
`verdict.confidence`) is empty: `adversarial_nlp.py:1131` defines
`confidence = min(1.0, (mcp - 1.0) / 4.0)` — the two options are the same
value. When the architectural fix lands, `verdict.confidence` is the
correct `raw_score` with no further methodology call needed.

**Decision requested from the collective (three options, position stated):**
1. Route these tools' findings into the case's artifact/signal stream (the
   same path everything else takes) and delete the four local-engine blocks
   and their logs. *Recommended.*
2. Keep injection but introduce a shared engine consumed by the scorer —
   larger blast radius, duplicates the scorer's construction contract.
3. Delete the injection blocks without routing (pure dead-code removal) —
   honest but forfeits real fracture signal (stylometric, entanglement,
   temporal) that the design intended to feed CAIE.

Options 1 and 2 additionally require new `EVIDENCE_PROFILES` entries
(`linguistic_forensics`, `batch_forensics`, `temporal_fraud`) with
calibrated spoofability — same decision class as B-092 — and a full
comparative corpus gate, since new fractures move verdicts.

---

## Finding 7 — B-116 partial unblock (gate remains UNWIRED) [MEASUREMENT + POLICY DECISION REQUESTED]

Three of four blockers advanced; unblocking condition 4 (a dry-run showing
0 true-MALICE degradations) is still unmet, so `SignalQualityGate` still has
zero production callers, by design.

1. **Duplicate removed:** `vigia/signal_quality_gate.py` deleted
   (byte-identical to `vigia/core/signal_quality_gate.py`, same md5, zero
   imports of the root path).
2. **Fallback implemented** (condition 3, option B):
   `_get_tool_name()` resolves `tool_name → source_tool → evidence_type`,
   treating the literal `"unknown"` as absent
   (`vigia/core/signal_quality_gate.py:119`).
3. **Dry-run reconstructed and committed:** the 2026-07-14 script was never
   committed; `scripts/dryrun_signal_quality_gate.py` reproduces MODE A/B
   and is now versioned.

**Fresh measurement (202 evaluable cases):** MODE A: 0 pass / 202 degraded.
MODE B: 77 pass / 125 degraded; `ABSTAIN_INSUFFICIENT_TOOLS` = 66;
degraded-with-expected-MALICE = 46. (The 2026-07-14 numbers used a
different MALICE metric — emitted verdict vs `expected_verdict` — and 199
cases; not one-to-one comparable. Both statements are in the registry.)

**Census finding.** The 66 insufficient-tools cases are dominated by
conversion/acquisition placeholders in `source_tool`: `None` (91 artifacts),
`legacy_converter` (88), `manual_forensic_review` (43),
`generate_forensic_hash` (35), `read_evidence` (8). 31/66 cases have ≥2
distinct `evidence_type` values and would pass the diversity check if those
placeholders were treated as absent.

**Decision requested from the collective:** define the placeholder set
(candidates: `legacy_converter`, `manual_forensic_review`,
`generate_forensic_hash`, `read_evidence`) that must not count as an
analysis tool. This is data policy, not code — with the decision taken, the
existing fallback covers it with a one-line change, after which condition 4
can be re-measured.

---

## Explicit non-actions (with reasons)

| Item | Reason |
|------|--------|
| B-115 mechanical kwargs fix | REFUTED — would replace an honest failure log with a false success (see Finding 6). Subsumed into B-136. |
| B-010 (SemioticDetectorV2 migration) | The registry itself requires collective audit before migration; P3 debt, detector functionally correct. |
| B-123 / B-124 (CCS gate + governance cluster) | Blocked by the orphaned producer chain (`vigia/abduction/`, `vigia/temporal/`, `vigia/patterns/`); 0/258 cases carry the input dimensions — wiring today would be cosmetic. Unblocking starts with wiring `vigia/abduction/`, which is an architecture project, not a patch. |
| B-111 (Ollama Mode 3 behavior) | Requires an Ollama environment not present in this session. |
| B-112 / B-113 (CAIE catalogue candidates), REVIEW-001 (BREAK-012 label) | Maintainer calibration / labeling decisions. |
| Regenerated corpus bundles | Never committed; `results/agent_batch/` restored from git after each comparative run. |

---

## Standing invariants checked

- No float entered any sealed/decision path: fixes touch metadata merging,
  marker sets, a log path, guardrail delegation and an unwired gate; the
  only scoring-adjacent change (B-131) moves existing metadata values.
- No LLM influenced any sealed value; all changes are deterministic code.
- No rebase / squash / force-push; forward-only commits `85db3af`,
  `6b73b45`; restore tag in place.
- Every claim above was derived from live-tree reads and real command
  output; the two comparative gates were executed live (`--rerun`), not
  from cached bundles.
