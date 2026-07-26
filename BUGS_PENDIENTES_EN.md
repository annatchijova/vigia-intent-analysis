# BUGS_PENDIENTES_EN.md — VIGÍA Bug Registry (Pending)

Registry of bugs that are **genuinely still pending**: open, documented
without a fix applied, or awaiting an architecture decision. Format: one
block per bug, keeping the same number it always had — never renumbered.

Bugs that are already resolved, closed, applied, or discarded live in
[`BUGS_HISTORICO_EN.md`](./BUGS_HISTORICO_EN.md) — split out on 2026-07-25
so this file stays navigable. Useful if you're red-teaming VIGÍA: it holds
everything that's already been found and fixed. Numbering is shared
between both files: a given B-XXX never appears in both at once.

---

## B-010 — TODO: Migrate forensic_technical_detector.py to SemioticDetectorV2

| Field | Value |
|-------|-------|
| **Status** | OPEN |
| **Severity** | P3 — technical debt, not a functional bug |
| **File** | `vigia/core/forensic_technical_detector.py` |
| **Original lines** | 194 |
| **Detected** | Post-hackathon session 2026-06-25 |

### Description

```python
# TODO: migrar a SemioticDetectorV2 en v3.0
```

The forensic technical detector still uses the v1 architecture. `SemioticDetectorV2`
exists but is not wired here. This is not a functional bug — the detector operates
correctly with the current architecture. It is migration debt for v3.0.

### Fix when applicable

Evaluate whether SemioticDetectorV2 covers all forensic_technical_detector use cases.
Migration must be audited by the team before applying.

---

## B-111 — Mode 3 (Ollama/hermes3:8b): unreliable behavior on dense testimonial evidence — N=2, STOCHASTIC

| Field | Value |
|-------|-------|
| **Status** | OBSERVED — insufficient evidence to escalate to KNOWN_LIMITATIONS |
| **Severity** | P3 (experimental — Mode 3 already classified as non-primary) |
| **Detected in** | Blind comparative experiment 2026-07-13, KIWI-006 and KIWI-007 |
| **N observations** | 2 KIWI-006 runs (1 hallucination, 1 clean) + 1 KIWI-007 run (truncated JSON) |

### Observations

**Run 1 — KIWI-006, first execution:** `hermes3:8b` hallucinated
`"carnegie_pattern": "JAILBREAK_ATTEMPT"` and
`"security_alert": "EVIDENCE_DELIMITER_MISMATCH"` — fields that do not exist in the
VIGÍA schema. The model interpreted the content of the testimony (surveillance,
blocked contacts, witness coordination) as evidence of an attack on
itself. The correct Peircean analysis was also present in the same
response, embedded alongside the hallucinated fields. Valid JSON.

**Run 2 — KIWI-007, first execution:** `hermes3:8b` returned invalid JSON
(object truncated midway through the A02 field, after completing A01). The tool
detected the failure and returned `"error": "LLM did not return valid JSON."` with the
fragment in `"raw_response"`. Required manual synthesis for A02 and A03.

**Run 3 — KIWI-006, re-execution with IDENTICAL prompt (2026-07-13, same session):**
Clean result. No hallucination. Complete valid JSON. Correct Peircean chain.
Verdict NOISE 0.25, reasonable and consistent with CAIE.

### State of the evidence

N=2 runs of KIWI-006 (1 hallucination / 1 clean with the same prompt). The
behavior is **stochastic, not deterministic** — the same input does not reproduce
the same error. N=1 for KIWI-007 (truncated), no re-run yet.

Does not escalate to KNOWN_LIMITATIONS because:
- N insufficient to establish an error frequency
- The KIWI-006 re-run was clean → not a consistent pattern
- Mode 3 is already classified as experimental/complementary in the README and CLAUDE.md

### What to watch in future runs

- Does the jailbreak hallucination reappear in KIWI-006 with a third run?
- Does KIWI-007 truncate consistently, or was it a one-off event?
- Do other dense testimonial cases (KIWI-007 analogues) show the same pattern?
- If the hallucination rate is confirmed in >20% of runs on testimonial cases:
  escalate to KNOWN_LIMITATIONS with a recommendation of `gemma3:27b` for Mode 3
  in production on dense narrative.

### Note on non-reproducibility

The non-reproducibility of the error is itself a relevant data point: a
consistent error is caught in testing; a stochastic one can reach production with
no prior signal. If further samples confirm that the rate is not negligible,
that opacity argument would be the basis for the formal limitation, not the
current two isolated events.

---

## B-112 — CAIE catalogue gap candidate: SELF_INCRIMINATION_LOG — self-incriminating evidence epistemically distinct from a third-party-spoofable log

| Field | Value |
|-------|-------|
| Detected | 2026-07-13 |
| Source case | KIWI-001-A02 and KIWI-003-A03/A04 (case file MPF7779408) |
| Status | CANDIDATE — N=1 real judicial case |

### Description

When the actor himself voluntarily submits credentials or logs that incriminate him in judicial documentation, the artifact is epistemically irrefutable even though CAIE assigns it `spoofability=0.85` (log_entry). The spoofability metric models an external attacker who fabricates evidence; it does not apply when the evidence comes from the accuser himself.

In KIWI-001 (A02) and KIWI-003 (A03/A04), the complainant (actor_a) submitted his own stalking-server credentials and admitted having hacked an ex-partner. CAIE computes adjusted=0.0071 and 0.0081 respectively due to spoofability=0.85 — values that underestimate the real epistemic weight. If a `SELF_INCRIMINATION_LOG` fracture existed, the composite would exceed the SUSPICION threshold in both cases without any need for manual escalation.

### Generalization restriction

The three KIWI cases (001, 002, 003) belong to the same judicial case file (MPF7779408) viewed from different angles — **they are not 3 independent samples, they are 1 real case looked at 3 times**. The observation is N=1 of a real judicial case. A second independent case file with the same structure (an accuser who submits self-incriminating evidence) is needed before generalizing this pattern as a real catalogue gap and implementing the fracture.

### Escalation criterion

Observe the pattern in a second independent judicial case file (other than MPF7779408). Do not implement the fracture until then.

---

## B-113 — CAIE catalogue gap candidate: INSTITUTIONAL_REJECTION — independent institutional rejection as forensic corroboration

| Field | Value |
|-------|-------|
| Detected | 2026-07-13 |
| Source case | KIWI-003-A05 (case file MPF7779408) |
| Status | CANDIDATE — N=1 real judicial case |

### Description

In KIWI-003-A05, three court orders presented 6 formal irregularities and two police stations independently refused to execute the ordered search. The institutional rejection by two independent bodies constitutes forensic corroboration of the documentary irregularity — a source of evidence that CAIE does not capture because `document_geometry` only models the physical artifact, not the institutional reaction to it.

If an `INSTITUTIONAL_REJECTION` fracture existed, artifact A05 would go from adjusted=0.0327 to a significantly higher weight, given that the police rejection eliminates the "isolated administrative error" explanation as a benign hypothesis.

### Generalization restriction

Same restriction as B-112: the three KIWI cases are the same case file MPF7779408 — **N=1 real case**. It is not evidence of a systematic gap in the CAIE catalogue until it is observed in a second independent case file involving institutional rejection of documentation in a forensic context.

### Escalation criterion

Observe the pattern in a second independent judicial case file (other than MPF7779408). Do not implement the fracture until then.

---

## B-116 — `signal_quality_gate.py` designed and functional in isolation, NOT wired to scorer — dry-run shows 122/199 cases degraded

> **Update 2026-07-17 (condition 4 re-measured, Kimi-endorsed placeholder
> policy applied):** the four acquisition/conversion placeholders
> (`legacy_converter`, `manual_forensic_review`, `generate_forensic_hash`,
> `read_evidence`) no longer count as analysis tools — they are skipped in
> the `tool_name -> source_tool -> evidence_type` fallback, exactly like the
> literal "unknown". Single source of truth: `_NON_ANALYSIS_PLACEHOLDERS`
> in `vigia/core/signal_quality_gate.py` (not replicated in scripts).
> Re-measured dry-run (corpus grew 202 -> 205 evaluable): MODE B passed
> 77 -> 87; ABSTAIN_INSUFFICIENT_TOOLS 66 -> 40 (the -26 matches the
> census: 31/66 had >=2 distinct evidence_type; the uncovered cases now
> land honestly in the next checks — DEPENDENT_SIGNALS/LOW_Z_VARIANCE);
> degraded-with-expected-MALICE 46 -> 42. Gate remains UNWIRED (zero
> production callers): no verdict moved. Tests:
> `tests/test_b116_placeholder_tools.py` (9, red-first).

| Field | Value |
|-------|-------|
| **Status** | POSTPONED — blocked by interface mismatch and data quality |
| **Severity** | P2 (gate-level architectural gap — safety mechanism exists but does not fire) |
| **File** | `vigia/signal_quality_gate.py` AND `vigia/core/signal_quality_gate.py` (identical duplicates) |
| **Detected in** | Post-hackathon session 2026-07-14, dry-run script `scripts/dryrun_signal_quality_gate.py` |

### Description

`SignalQualityGate` implements five checks before a verdict can be emitted:
tool diversity (>= 2 tools), signal strength (z >= 2.0), tool independence
(<= 60% from same tool), z-score variance (range >= 0.5), and noise inflation
detection. The module is complete, tested in isolation, and conceptually aligned
with VIGIA's Daubert corroboration requirements (vigia_scorer.py lines 1194-1240).

However, it has **zero callers** in the codebase. Additionally, the module is
duplicated: `vigia/signal_quality_gate.py` and `vigia/core/signal_quality_gate.py`
are byte-identical copies.

### Dry-run results (2026-07-14)

Full corpus dry-run (`scripts/dryrun_signal_quality_gate.py`) against all 199 cases:

| Gate reason | Cases failed |
|-------------|-------------|
| `ABSTAIN_INSUFFICIENT_TOOLS` | 67 |
| `ABSTAIN_WEAK_SIGNALS` | 20 |
| `ABSTAIN_DEPENDENT_SIGNALS` | 18 |
| `ABSTAIN_LOW_Z_VARIANCE` | 17 |
| **Total degraded** | **122** |
| **Passed gate** | **76** |

Of the 122 degraded, **23 are currently MALICE** — including 11 from the
VIGIA-REAL-001 to REAL-010 series (the most validated corpus).

### Root cause (three independent blockers)

1. **Interface mismatch**: gate expects `tool_name` + `z_score` (statistical).
   Scorer produces `source_tool` + `raw_score` in [0.0, 1.0].
2. **Data quality**: 67/199 cases (33%) have only 1 unique `source_tool`, many
   with `source_tool=unknown`.
3. **Duplicate module**: two identical copies exist.

### Decision

Postponed. Blocked until `fit_calibration.py` produces real z-scores. The
scorer's corroboration gate (lines 1194-1240) partially covers the same
Daubert requirement but lacks noise inflation detection and z-score variance
checks unique to `SignalQualityGate`.

---

## B-122 — Audit trail gap: 20 of 23 MCP tools lack TOOL_INVOKED logging

| Field | Value |
|-------|-------|
| **Status** | PARTIALLY RESOLVED — 3 priority tools covered, 20 pending |
| **Severity** | P2 (Daubert chain-of-custody gap) |
| **File** | `vigia/vigia_sift_bridge.py` |
| **Detected in** | Module archaeology audit 2026-07-14 |

### Description

Of 23 MCP tools, only 3 have `audit_logger.log_info(event_type="TOOL_INVOKED")`
before path sanitization: `generate_forensic_hash`, `read_evidence`, `list_files`.
These 3 are the evidence-touching tools (chain-of-custody anchor). The remaining
20 Phase 2-4 analysis tools are not instrumented. A calling agent can reconstruct
a v2 HMAC `tool_execution_log` after a session, but that is not equivalent to
tool-side instrumentation or contemporaneous capture.

**OWL v2 confirmation (2026-07-21):** external bundle
`results/OWL-NEXUS5-CASE_bundle_claude_v2.json` preserves 37 entries and the
stdlib verifier confirms its hash chain. Its own report documents that entries
were written by the agent in batches after MCP calls and that HMAC cannot be
keyedly verified without the access-restricted key. The chain therefore proves
subsequent relative integrity, not wall-clock timing, call order, or literal
MCP response text. This is not a verifier defect; it is concrete evidence that
B-122 remains partially open.

Deferred: broader rollout needs to address `audit_logger` synchronous fsync
performance before adding to all 20 tools.

---

## B-123 — Causal Closure Score gate designed and tested, NOT wired — dry-run inviable (0/258 cases have data)

| Field | Value |
|-------|-------|
| **Status** | POSTPONED — blocked by full chain of orphaned producer modules |
| **Severity** | P2 (Daubert gate — prevents MALICE without causal coherence) |
| **Files** | `vigia/core/causal_closure.py`, `vigia/patterns/adversarial_silence.py`, `vigia/temporal/coherence_validator.py`, `vigia/core/explainable_governance.py` |
| **Test** | `tests/test_audit_gates.py` (passes in isolation) |
| **Detected in** | Module archaeology audit 2026-07-14 |

### Description

CCS gate caps verdict at ABSTAIN when causal coherence < 50%:

```
CCS = 0.3*temporal_coherence + 0.2*semantic_resonance
    + 0.3*abductive_parsimony + 0.2*adversarial_silence
```

**Why not wired:** none of the 4 input dimensions exist in any of the 258
corpus cases. Without data, CCS = 0.50 (all defaults) for every case and
the gate passes unconditionally. Wiring would be cosmetic.

**Blocking chain:** 4 producer modules all orphaned or incomplete:
`coherence_validator.py`, `cross_artifact_resonance.py` (live but missing
field), `hypothesis_lineage.py` (93KB orphaned), `adversarial_silence.py`.

### Comparison with B-116

| | B-116 signal_quality_gate | B-123 causal_closure |
|---|---|---|
| Data in corpus | raw_score/source_tool exist | 0/4 dimensions exist |
| Dry-run | 122/199 degraded | 0/258 (trivial) |
| Blocker | 1 module | 4 orphaned modules |
| Effort to unblock | Medium | High |

### Decision

4 files preserved as pending-to-wire capability (real forensic logic,
tested, doctrinally correct). NOT candidates for deletion. Blocked until
>= 2 producer modules are wired and corpus includes real CCS values.

---

## B-124 — Verdict/governance cluster: 6 modules designed, NOT wired — same pattern as B-123

| Field | Value |
|-------|-------|
| **Status** | POSTPONED — same blocking pattern as B-123 |
| **Severity** | P2 (governance gates not firing) |
| **Detected in** | Module archaeology audit 2026-07-14 |

### The 6 files

1. **`ockham_adversarial.py`** (224 lines) — penalizes "too simple" benign
   hypotheses in presence of malice signals. Concept exists inline in
   `abductive_intent_engine.py` but as separate implementation.
2. **`dissent_report.py`** (305 lines) — minority signal escalation.
   Needs ALL governance module results (circular dep).
3. **`config_sentinel.py`** — config tampering detection for critical modules.
4. **`narrative_auditor.py`** (283 lines) — C3 narrative injection validator.
   `run_demo.py` loads from DIFFERENT paths that don't resolve to this file.
5. **`peirceplanner_bounded.py`** (375 lines) — Miller's Law bound +
   oscillation detection for abduction.
6. **`advanced_signal_router.py`** — signal routing, conceptually superseded
   by scorer's inline evidence_type lookup.

All 6: zero production callers, all depend on orphaned producer chain
(vigia/abduction/, vigia/temporal/, vigia/patterns/). Dry-run inviable.
Preserved as pending-to-wire capability, NOT deletion candidates.

### Update 2026-07-25 — confirmed by execution: the `adversarial_penalty` gap
is not just "not wired," it changes the emitted state

Continuation of the "Round 2" audit (see B-217/B-221): while investigating
why `vigia_scorer.py:1931` (`_apply_quadripartite`) passes `dissent_info={}`
(F1, B-217), I noticed the same call also hardcodes `pivot_signals=[]`,
`investigation_roadmap=[]`, and `adversarial_penalty=False` — all three are
literals inside `_apply_quadripartite` (line ~503), not derived from any
computation in `vigia_scorer.py`. `pivot_signals`/`investigation_roadmap` are
pure display data (they feed the analyst report via
`QuadripartiteClassifier._build_verdict` → `render_for_report`) — their
absence degrades the report to "see roadmap" but changes no verdict.

`adversarial_penalty`, by contrast, **does gate a live branch** (Check 6,
`quadripartite.py` line ~375): with `adversarial_penalty=True`, a BENIGN
verdict gets a +5% effective-confidence bonus (the bonus exists precisely
because the system evaluated and discarded the too-simple hypothesis, per
`ockham_adversarial.py`'s principle). Confirmed by direct execution against
`QuadripartiteClassifier.classify()`:

```
BENIGN, confidence=78%, stability=100%
  adversarial_penalty=False (today's real state) -> BENIGN_MEDIUM, confidence=78%
  adversarial_penalty=True  (if ockham were wired)-> BENIGN_HIGH,  confidence=83%
```

The +5% crosses the HIGH/MEDIUM threshold (80%) in this example — not a
cosmetic adjustment, it changes the emitted `VerdictState`. Since
`ockham_adversarial.py` has zero callers anywhere in the repository
(confirmed by exhaustive grep, including tests — there isn't even a unit
test for this module), the `adversarial_penalty=True` branch of
`_build_verdict`/Check 6 is reachable in the code but **unreachable in
practice**: nothing in the live pipeline can produce that `True` today. Same
pattern as F1 (B-217): a correctly implemented decision branch with its own
branch logic, but with the one input that would activate it hardcoded to a
fixed value at the sole production call site.

Not opened as a new bug — same root cause already documented in this B-124
entry (orphaned producer chain in `vigia/abduction/`), just now with the
concrete consequence verified by execution instead of deduced. Left as
additional evidence to prioritize roadmap step 3 ("Wire governance modules
in order: ockham -> dissent -> config_sentinel") if that path is pursued.

### Update 2026-07-25 (bis) — `config_sentinel.py`: if wired today as-is, it
would lie about the two critical modules already known to be broken

Continuing the B-124 cluster excavation, I read `ConfigAuditMonitor` in
full. Its stated purpose is exactly this: detect "critical modules disabled
at startup" and seal an `analyst_warning` into the bundle if `CAIE`,
`TrustFusion`, `OckhamAdversarial`, or `SignalRouter` (its own
`CRITICAL_MODULES`) are inactive. But its `_MODULE_ENV_MAP` maps each module
to an environment variable the monitor itself reads — and of the 9 mapped
variables, **7 are read nowhere else in the repository** (confirmed by
exhaustive grep, excluding tests and `config_sentinel.py` itself):
`VIGIA_OCKHAM_ADVERSARIAL`, `VIGIA_SIGNALROUTER_ENABLED`,
`VIGIA_PDF_ENABLED`, `VIGIA_NETWORK_ENABLED`, `VIGIA_REGISTRY_ENABLED`,
`VIGIA_EMAIL_ENABLED`, `VIGIA_TEMPORAL_ENABLED`. Only
`VIGIA_CAIE_ENABLED` and `VIGIA_TRUST_FUSION_ENABLED` gate anything real.

`_getenv_bool` is designed to return `True` (active) when the variable is
unset — `NOT_SET` reads as "active by default," which makes sense IF the
variable actually controlled the module. But since `VIGIA_OCKHAM_ADVERSARIAL`
and `VIGIA_SIGNALROUTER_ENABLED` control nothing (this same B-124 entry
already established `ockham_adversarial.py` has zero callers and
`advanced_signal_router.py` is "conceptually superseded"), the monitor would
report "active" for exactly the two critical modules that are completely
disconnected from the live pipeline.

Executed directly against `ConfigAuditMonitor` with a clean environment (none
of the 9 variables set — the normal case, since none of them are
documented):

```
integrity_level: FULL_INTEGRITY
analyst_warning: None

OckhamAdversarial    active=True  env_var=VIGIA_OCKHAM_ADVERSARIAL  env_value=NOT_SET
SignalRouter         active=True  env_var=VIGIA_SIGNALROUTER_ENABLED  env_value=NOT_SET
```

A "configuration guardian" that reports `FULL_INTEGRITY` and "active" for
the two modules its own sibling entry (this B-124) documents as completely
orphaned isn't just "not wired" — if wired in without first fixing
`_MODULE_ENV_MAP`, it would give false reassurance exactly where the system
is most broken. Same epistemological pattern as "attacks against the
auditor" (see B-219): a mechanism that, far from failing loudly, would
produce a sealed report saying "all good" about an absent module.

Not opened as a new bug — still part of B-124's root cause (orphaned
dependency chain), but the correct fix for `config_sentinel.py` is no longer
just "wire it in": `_MODULE_ENV_MAP` needs to reflect how each module is
actually activated (for `OckhamAdversarial` and `SignalRouter`, today that
would be "never, because they have no caller," not an environment variable
nobody reads) before the monitor can be trusted. Verified with a permanent
test: `tests/test_config_sentinel_orphaned_module_env_map.py`.

---

## B-129 — PeircePlanner bounded: Phase 1 observation adapter [PHASE 2 PENDING]

| Field | Value |
|-------|-------|
| **Status** | PHASE 1 COMPLETE — Phase 2 (calibration) and Phase 3 (integration) pending |
| **Severity** | P3 — observation-only module, does not affect verdicts |
| **Files** | `vigia/core/planner_adapter.py` (new), `vigia/core/peirceplanner_bounded.py` |
| **Detected** | Investigation 2026-07-14 |

### Description

Adapter translating VIGIA case artifacts into EvidenceSignal and Hypothesis
objects for `run_bounded_planner()`. Output is observation-only — it does
NOT feed the scorer or the verdict path.

Observation baseline over 198/199 cases: 22% agreement with the scorer
(severely miscalibrated), 90 under-alerts (planner NOISE where the scorer
says SUSPICION+). Root cause: confidence-as-weight measures certainty, not
anomaly severity. Phase 2 (not before 2026-08-14) must recalibrate the
weight (z_score or raw_score x (1 - spoofability)) and reach >70% agreement
before Phase 3 integration is even considered; oscillation detection
(ABSTAIN on contradictory evidence) is the primary value-add.

---

## B-149 — T-5: a high-severity C2 IoC can collapse to NOISE when the exculpatory memory artifact was never network-analyzed (surfaced by B-148) [OPEN — synthetic-only]

| Field | Value |
|-------|-------|
| **Status** | OPEN — synthetic-only (0/201 corpus cases). Documented as a limitation, not silently patched. Deliberately NOT bundled into B-148. |
| **Severity** | P2 (latent) — a real, corroborated C2 IoC should never read as NOISE ("nothing to see here"). Currently reproducible only synthetically. |
| **File** | `vigia_scorer.py` (spoofability-weighted Noisy-OR / verdict cascade); probe: `vigia/tests/adversarial/test_spoofability_correlation_attack.py::test_red_team_anchor_bypass` (now `xfail(strict=True)`) |

**Why B-148 surfaced it.** The LOG_VS_MEMORY fabrication rule was doing double
duty: besides detecting fabrication, its firing on network-absent memory was
INCIDENTALLY the mechanism that stopped a high-spoofability C2 log from collapsing
to NOISE. B-148 correctly stops the absence-firing (it was a false positive), which
removes that incidental protection. Measured post-B-148: a C2 IoC
(`raw_score=0.95`, `log_entry`) + a network-UNANALYZED exculpatory memory artifact
with no explicit `verdict` → **verdict = NOISE** (`test_red_team_anchor_bypass`),
whereas with an explicit-verdict exculpatory artifact it holds at SUSPICION
(`test_metadata_convention...`, now a genuine-contradiction pass).

**Honest scope.** The B-148 corpus gate shows **0/201 real cases** exhibit this —
the anti-collapse protection rested on a false positive, but no real case relied
on it either. So T-5 is a latent behavior, not a live corpus regression.

**Proper fix (deferred, needs a decision).** A high-severity, independently
corroborated IoC must resist NOISE collapse **on its own merits** — not via a
fracture coupled to absent memory. This is a scorer-level change (e.g. an IoC
floor that spoofability weighting cannot push below SUSPICION), NOT a re-coupling
to the absence bug B-148 fixed. Tracked separately so the correct fix is designed
deliberately. When it lands, the `xfail(strict=True)` on `test_red_team_anchor_bypass`
flips to XPASS and the marker is removed.

---

## B-151 — Scorer downgrades: (a) silent single-artifact score clamp [RESOLVED, dead code]; (b) mandated contradiction_detector chain entry not wired in Mode-1 [OPEN — architecture decision]

| Field | Value |
|-------|-------|
| **Status** | (a) RESOLVED (2026-07-19) — clamp made auditable; also found unreachable. (b) OPEN — architecture decision, deliberately NOT bundled with (a). |
| **Severity** | (a) P3 (disclosure of a dead-code clamp). (b) P2 (doctrine-vs-implementation gap). |
| **File** | (a) `vigia_scorer.py` clamp ~1216 + marker ~1620; (b) `vigia_scorer.py` (no `ToolExecutionLogChain` in the decision path). |

**(a) Silent single-artifact score clamp — RESOLVED, with an honest twist.**
`if n_artifacts < 2 and final_score > 0.65: final_score = 0.65` silently rewrote
the sealed score (a probative-strength reduction with no reason/marker, unlike
every other downgrade in the cascade). Fix: capture the pre-cap score and surface
a `single_artifact_score_cap` marker + reason note into `base_result`, mirroring
the `normalization_failures` / `temporal_pairs_skipped` disclosure pattern.
Verdict-neutral (the cap already applied; disclosure is additive).

**Twist found while verifying: the clamp is currently UNREACHABLE dead code.** A
single signal artifact is suppressed to a max score of ~0.038 (`cryptographic_hash`,
raw 0.99, all boosters) — far below the 0.65 cap — so the "silent downgrade" this
item named is not a live risk; the clamp is defensive and the marker is
forward-looking disclosure. Pinned by `tests/test_b151a_single_artifact_cap.py`:
if a single artifact ever scores >= 0.65 the test fails, flagging that the marker
path has gone live. `_dround` returns float, so `final_score` here is float by the
scorer's deterministic-rounding design (not a pure-Fraction path) — the `= 0.65`
assignment is type-consistent, no new float injection.

**(b) contradiction_detector chain entry not wired in Mode-1 — OPEN.** CLAUDE.md's
"Self-Correction Event Schema" mandates that every gate-driven downgrade append a
`contradiction_detector` entry via `ToolExecutionLogChain`. Verified: `vigia_scorer.py`,
`bundle_builder.py`, `pipeline.py`, `sift_orchestrator.py` contain **zero**
references to `ToolExecutionLogChain` / `contradiction_detector` — the appender is
instantiated only in tests and a red-team script. So the deterministic Mode-1 path
does not emit the mandated tamper-evident self-correction events (the cascade DOES
set human-readable `reason` strings for 7/8 downgrades — the gap is the *chained*
event, not the reason). This is an architecture decision — wire it into Mode-1, or
amend the doctrine to state the chained self-correction event is a Mode-2 (Claude
Code) construct by design. Deliberately NOT fixed as a one-liner. Not yet decided.

---

## B-162 — The legacy adapter silently erased an unmodeled structured-evidence schema [PARTIALLY REMEDIATED — Codex 2026-07-21]

| Field | Value |
|-------|-------|
| **Severity** | P2 evidence-integrity / honest-degradation failure. |
| **Files** | `vigia/pipeline/vigia_integration_bridge.py:_normalize_artifact_legacy`, `vigia_scorer.py` normalization gate. |
| **Detected by** | Codex audit of `OWL-NEXUS5-CASE`, 2026-07-21. |

The legacy adapter expected `artifact_id`, `forensic_anomalies`, and
`analyst_flags`. The OWL scenario uses `id`, nested structured `content`, and
mobile/social types such as `web_search` and `instant_message`. Before any
mapping, all 20 artifacts silently became `artifact_id="?"`,
`evidence_type="unknown"`, and zero-score signals. The run then sealed
`NOISE`, without a `normalization_failures` marker or an `ABSTAIN` disposition.

Repository-wide measurement found 24 legacy artifacts with unmapped types;
20 belong to OWL. Mapping those type names alone is not a verdict repair:
the adapter has no deterministic extractor for the nested message, URL, and
account semantics, so each artifact still receives the minimum raw score and
OWL remains `NOISE` (measured score `0.0627`). Treating scenario prose such as
`metadata.significance` as an anomaly or score would instead make an authored
case narrative authoritative, reopening the label-leak / examiner-assertion
class.

**Applied repair:** the normalizer preserves `id` as `artifact_id`, recognizes
the mobile/social taxonomy only as a collection class, and attaches
`structured_content_without_semantic_extractor` when structured content lacks a
deterministic extractor. The existing gate converts the would-be `NOISE` to
`ABSTAIN`. Neither `metadata.significance`, narrative text, nor
`expected_verdict` becomes a score input.

**Verification:** red-first tests establish that the ID and
`instant_message` class are preserved, that the minimal case ends in `ABSTAIN`
with the exact loss marker, and that changing its expected label between
`SUSPICION` and `MALICE` changes no normalized artifact.
`tests/test_b162_structured_legacy_degradation.py`,
`tests/test_label_leak_normalize_case_schema.py`,
`tests/test_b066_b067_mobile_whitelist.py`,
`tests/test_p1_metadata_normalization_integrity.py`, and
`tests/test_b6_artifact_type_map_consistency.py`: **58 passed**. A real
temporary-bundle run of `vigia_agent.py` on the OWL JSON changed `NOISE` to
**`ABSTAIN`** (`motor_score=0.0627`), with a valid checksum and reasoning trace,
without promoting prose into evidence.

**Open residual:** this repairs the false-clean outcome; it does not extract
forensic meaning from nested chat, URL, or account records. A source-specific
Android / Chrome / Musical.ly extractor must operate over hash-bound raw
artifacts before VIGÍA may derive a score or its own `SUSPICION`.

**Cross-mode confirmation, without verdict authority (2026-07-21):** the
work products preserved in
`results/OWL-NEXUS5-CASE_{report,bundle}_claude*` and
`results/OWL-NEXUS5-CASE_{report,bundle}_chatgpt.*` verify their checksums and
agree that legacy `NOISE` does not adequately describe the recovered evidence.
Claude v1 traversed the extraction through 29 MCP calls and ChatGPT performed a
read-only manual image review. Claude v2 corrected the scope: a delivery SMS
was outside the original query and the Windows/Pidgin companion is
**UNRESOLVED**, not ruled out. It retains `SUSPICION`, not `INTENT`/`MALICE`,
because the cross-device link was not materialized. They are neither a motor
regression oracle nor a score input: they differ, for example, on which message
text is recoverable and what can be inferred about the second device. That
disagreement is preserved and reinforces that VIGÍA must keep emitting
`ABSTAIN` until a deterministic, source-specific, hash-bound extractor
materializes the facts it proposes to score.

---

## B-214 — `VigiaPipeline.run_full` bypasses the normalization-integrity gate that `vigia_agent.py` applies: two entry points, two verdicts [DOCUMENTED — Claude 2026-07-23]

| Field | Value |
|-------|-------|
| **Severity** | P2 (architectural footgun, not an incorrectness): the same case yields different verdicts by entry point. `run_full` scores raw; `vigia_agent.py` applies the honest-degradation gate. A caller using `run_full` gets an ungated score and may seal it as if it were the authoritative verdict. |
| **Files** | `vigia/pipeline/pipeline.py` (`VigiaPipeline.run_full`), `vigia_agent.py` (full Mode-1 agent). |
| **Mode** | Any code that calls `run_full` directly to seal (e.g. `scripts/run_vigia_full.py` and this session's `_claude_fable` bundles) instead of going through the agent. |
| **Detected by** | Mode-1 vs Mode-2 cross-check (session 2026-07-23, `vigia/results/MODE1-vs-MODE2_crosscheck_claude_fable.md`). |

**Reproduced observation:** on `data/cases/OWL-NEXUS5-CASE.json` and
`VIGIA-OWL-2019-COMPLETE.json`, `VigiaPipeline.run_full` returns
`decision=REJECT, posterior=1.0`; `vigia_agent.py` on the same JSON returns
**ABSTAIN** with reason `NORMALIZATION INTEGRITY LOSS` — it detects that an
artifact's metadata (the `significance` field carrying `..` on the coordination
SMS) was coerced at intake, which can silently drop a scoring-relevant assertion.
`run_full` does not run that check.

**Note (Thirdness):** neither side is "wrong" — there are two paths with different
guarantees and nothing flags it at the call site. The integrity gate (P1 metadata
normalization) is correct; the problem is that `run_full` is a low-level API that
bypasses it. Related to the B-160/B-206 semantic-extractor gap that leaves
OWL-NEXUS5 in honest ABSTAIN.

**Proposed fix (NOT applied):** either (a) `run_full` runs the same gate and
degrades to ABSTAIN on metadata coercion, or (b) `run_full` is renamed/documented
explicitly as "raw ungated score" and authoritative sealing always routes through
the agent. Needs an architecture decision + corpus dry-run before touching, since
it changes the sealed verdict of any case with `normalization_failures`.

## B-215 — `evidence_graph` not populated in `run_full` bundles: `graph_hash` identical across all cases (integrity anchor is meaningless) [DOCUMENTED — Claude 2026-07-23]

| Field | Value |
|-------|-------|
| **Severity** | P2 (Daubert integrity): `graph_hash` should bind the bundle to the case-specific evidence graph; if constant, it anchors nothing. `decision_hash` IS case-specific and stable, so verdict reproducibility is not compromised — but a verifier relying on `graph_hash` as proof of graph integrity is trusting an empty value. |
| **Files** | `vigia/core/bundle_builder.py` (`graph_hash = _sha256_dict(evidence_graph.to_dict())`), `vigia/pipeline/pipeline.py` (`ForensicBundle` construction in `run_full`). |
| **Mode** | Bundles sealed via `run_full`. |
| **Detected by** | Empirical check of 4 `_claude_fable` bundles (session 2026-07-23). |

**Reproduced observation:** OWL-NEXUS5 (22 artifacts), MAGNET-2022-iOS-JESS (6),
OWL-COMPLETE (30) and FLAREON-2017 (14) — totally different content and size —
produce the **same** `graph_hash` `94147b51c639cd0c...`. The `decision_hash`, by
contrast, differs across all four.

**Root cause (Secondness):** `graph_hash` = SHA-256 of `evidence_graph.to_dict()`
minus `graph_hash`/`generated_at`. Its being constant implies the
`ForensicBundle.evidence_graph` built by `run_full` is empty or a constant default
— it is not populated with nodes/edges derived from the case signals. The evidence
graph (a causal-chain artifact relevant to Daubert) is absent from the bundle.

**Proposed fix (NOT applied):** populate `evidence_graph` in `run_full` with signal
nodes and their relations before computing `graph_hash`; add a test asserting
distinct `graph_hash` for two cases with distinct artifacts (red-first against the
current state). Requires reviewing downstream consumers of `evidence_graph` so
`verify_ebs_v1.py` does not break.

**Related findings (NOT bugs, recorded to avoid re-discovery):** (1) `bundle_hash`
embeds `bundle_id` (random UUID) + timestamp and varies per seal — this is
**intentional** and documented at `bundle_builder.py:171`; the determinism anchor
is `decision_hash`, not `bundle_hash`. (2) `ecl_hash` is never populated in
`run_full` bundles, so `verify_ebs_v1.py` reports `R5_ECL_BINDING` WARN and caps at
Level 2 — Level 3 requires wiring the Evidence Chain Ledger (`VIGIA_CHAIN_DB_PATH`),
pending integration; not a failure, a Level-3 feature not connected to this entry
point.

## B-220 — The `bayesian_update` cache is keyed only by `artifact_id`: it ignores `custom_window`, even though the parameter is part of the public signature [DOCUMENTED — Claude 2026-07-25]

| Field | Value |
|-------|-------|
| **Severity** | P3, latent (no caller uses the affected parameter today). Origin: "Round 2" audit, finding F4. |
| **File** | `vigia/core/trust_fusion.py` (`TrustFusionEngine.bayesian_update`, line ~260). |
| **Function** | `bayesian_update(self, artifact_id, custom_window=None)`. |
| **Original lines** | `if artifact_id in self._bayesian_cache: return self._bayesian_cache[artifact_id]` — the cache key is `artifact_id` alone; `custom_window` plays no part. |
| **Fix commit** | None — documented, not applied. |
| **Detected in** | "Round 2" audit, executed against the live file. |

### Description

`bayesian_update(artifact_id, custom_window=None)` accepts `custom_window`
as a documented parameter and correctly uses it to compute the temporal
neighborhood (`get_neighborhood(artifact_id, custom_window)`) — but
**before** reaching that computation, it checks `self._bayesian_cache` keyed
only by `artifact_id`. Executed: `bayesian_update('a3')` and
`bayesian_update('a3', custom_window=timedelta(seconds=30))` return the
**same object** — the second call never recomputes with the different
window, it simply returns whatever was cached from the first call
(whichever that was).

Confirmed by exhaustive grep: no caller of `bayesian_update` anywhere in the
repository (neither internal nor MCP-exposed) passes `custom_window` today —
every production call site (`vigia/core/trust_fusion.py`, lines 319, 345,
395, 541) uses the `None` default. The bug is purely latent: no real
execution path reaches it in the code's current state.

### Impact

If some future caller (internal or via MCP) starts using `custom_window` —
the parameter is documented and exposed, so this is a foreseeable use, not
an exotic one — it would get results from the wrong temporal window
depending solely on call order: the first call "wins" and stays cached for
any subsequent `custom_window` on the same `artifact_id`. This is a classic
incomplete-cache-key bug, matching the pattern of other cache-key bugs
already documented in this repository (search "cache key" in
`BUGS_PENDIENTES_EN.md`).

### Proposed fix (NOT applied)

Include `custom_window` in the cache key (e.g.
`cache_key = (artifact_id, custom_window)`, with `custom_window=None` a
valid tuple member), or — simpler, given nobody uses it today — explicitly
exclude from caching any call with a non-default `custom_window`,
documenting that only the default window gets cached. Either option needs a
regression test that doesn't exist today (no test of `bayesian_update`
exercises a non-`None` `custom_window`).

## B-221 — "Round 2" audit (epistemological invariants): investigated and discarded vectors — recorded to avoid re-discovering them [DOCUMENTED — Claude 2026-07-25]

| Field | Value |
|-------|-------|
| **Severity** | N/A — not bugs. Documented as audit reference, not as a defect. |
| **Files** | `vigia/core/risk_bounded_layer.py` (`PolicyStabilityController`), `vigia/core/dissent_report.py` (`_compute_majority`, tie-break), `vigia/core/trust_fusion.py` (`NeighborhoodContext.mean_neighbor_trust`, `TrustFusionEngine.calculate_likelihood`, `add_artifact`). |
| **Method** | A-D-I (Abductive-Deductive-Inductive): every vector was executed against the live code before being accepted or discarded, not just deduced. |
| **Detected in** | "Round 2" audit, session 2026-07-25, independently re-verified in this session (no result from the pasted report was accepted without re-running it). |

### Description

Five vectors were investigated during the "Round 2" audit and did not turn
into bugs. They're documented here explicitly so a future audit doesn't
spend time re-discovering them:

**1. F5 — `PolicyStabilityController`: does the result diverge between the
numpy branch (`np.linalg.norm` + `np.array`) and the stdlib fallback
(`math.sqrt` + lists)?** FALSIFIED. Original hypothesis (deduced, not
executed): the verdict might silently depend on whether `numpy` is
installed. Re-executed in this session, forcing both branches over the same
`stabilize()` sequence: the three resulting parameters (`lambda, gamma,
epsilon`) are **bit-identical** across both paths (`0x1.b851eb851eb85p+1` in
both cases, verified via float `.hex()`). The two branches are
arithmetically equivalent for this operation; the BLAS divergence that
motivated the hypothesis is theoretical for this case, not demonstrated.
Retracted as a finding.

**2. `_compute_majority`'s tie-break favors MALICIOUS on a tie.** NOT A BUG.
Breaking ties toward the more severe verdict on an exact vote tie is
deterministic and fail-safe — it's the correct policy for a forensic system:
under genuine uncertainty between two equally-voted verdicts, escalating is
more defensible than averaging down.

**3. `NeighborhoodContext.mean_neighbor_trust` returns `1.0` when there are
no neighbors — is that "absence of evidence treated as perfect trust"?**
FALSIFIED as a scoring risk. Verified against the live code:
`TrustFusionEngine.calculate_likelihood` short-circuits to `return 0.5` when
`neighborhood.neighbor_count == 0`, **before** ever reading
`mean_neighbor_trust` — the `1.0` value never participates in the
`likelihood`/`posterior` computation. The `1.0` does appear in the narrative
reason text (`BOOST: trust vecindad={neighborhood.mean_neighbor_trust:.3f}`)
in cases where neighbors DO exist, so there's no path where the "no
neighbors" default leaks into a score. Confirmed real risk: none.

**4. `add_artifact` silently deduplicates duplicate IDs.** Hygiene, not a
severity bug. `add_artifact` returns `False` with no exception and no
record when `artifact.artifact_id` already exists (`trust_fusion.py`, line
~207) — two artifacts sharing an ID collapse into one without appearing in
any `rejected_details` or equivalent structure. The behavior itself is
desirable (guards against double-counting), but it's invisible: nothing in
`TrustFusionEngine`'s output tells an expert witness that an artifact was
dropped as a duplicate. Minor, non-blocking ticket — not opened as its own
numbered bug since it affects no verdict; recorded here instead.

### Process note

This audit was done with explicit A-D-I discipline after an earlier pass
(B-217 through B-220 plus this block) had *deduced* some findings without
executing them. Re-verification with induction changed the outcome: F1 got
worse (the full chain was shown to be dead, not just that the module was
orphaned), F2 and F4 dropped in severity once their dormant preconditions
were discovered, and F5 was fully retracted once executed and found
bit-identical. The process is documented, not just the outcome, because the
process is repeatable: any future finding of this kind should go through the
same re-verification against live code before being accepted as confirmed.

