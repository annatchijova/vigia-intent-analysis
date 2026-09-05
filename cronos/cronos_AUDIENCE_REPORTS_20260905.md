# Cronos Audit Trail — AUDIENCE_REPORTS (junior SOC / expert presentations, EN + ES)
<!-- trace_id: not recorded — CRONOS MCP unavailable in this session -->

| Field | Value |
|-------|-------|
| Trace ID | not recorded — CRONOS MCP unavailable in this session |
| Agent | `claude-code-remote` (engineering session on branch `claude/modo-vogia-juniors-expertos-h0tjrl`) |
| Started | 2026-09-05 (session start; sub-second timestamps not recorded) |
| Closed | 2026-09-05 |
| Quality | STANDARD (3/3 observation groups: corpus renders, cross-process determinism, boundary refusals) |
| Confidence | 4/5 — every claim below is pinned by a test in `tests/test_report_*.py`, `tests/test_agent_audience_hook.py`, `tests/test_training_worked_examples_pinned.py` |
| Chain hash | not recorded — CRONOS MCP unavailable in this session |
| Chain integrity | not recorded |
| Cronos version | 0.1.0 (format) |

Fields marked "not recorded" are honest gaps, not placeholders: this session had no
CRONOS tool available to mint a trace id or a chain hash, and §5.3 forbids inventing
one. The git history of the five commits on this branch is the verifiable record.

---

## Objective

Add two audience-tailored presentations of an already-sealed VIGÍA verdict, for a
junior SOC analyst and for an expert forensic examiner, in English and Spanish, plus
training material, without touching the deterministic engine, the seal, or the Mode 2
investigation flow.

---

## Step-by-step trace

### 1. Hypothesis registered: `H1_presentation_outside_seal`
All three bundle families hash their entire payload (`bundle_builder.seal()` line 299;
`vigia_agent._seal_bundle` line 1545; Mode 2 `bundle_sha256`). A presentation can
therefore never live inside a bundle without changing its digest. Prediction: the
only architecture compatible with `tests/test_reasoning_trace_bundle_gate.py` is
sibling files, like `<stem>_reasoning_trace.json`.

### 2. Hypothesis registered: `H2_extend_evidence_narrative_gen`
Rival: extend `forensics/evidence_narrative_gen.py`, the only existing sectioned
renderer with a `lang` axis.

### 3. Evidence — refutes `H2`
Read against the live file: `BundleReader.posterior`/`risk` coerce with `float()` and
default missing values to `0.0` (violates §5.3); `_decision_icon` emits emoji;
`_now()` stamps generation time into §1 (breaks byte determinism); EBS v1 only.
Decision: build new under `vigia/report/` on top of `vigia/ui/normalizer.py`, which
already copies verdicts verbatim across the three families and renders Fractions as
`N/D`.

### 4. Evidence — normalizer gap found and fixed (supports the "verbatim" doctrine)
Seven real Mode 2 bundles under `results/` seal the top-level verdict as
`final_verdict`, not `overall_verdict`; `_normalize_mcp` warned "missing field" and
emitted no verdict for them. Fixed in the normalizer (also benefits the web UI),
pinned by two new cases in `tests/test_webui_normalizer.py`.

### 5. Evidence — import weight
`import vigia.sift.sans_phase` drags the whole SIFT engine package
(`vigia/sift/__init__.py` is eager) and `import vigia.tools.mitre_mapping` initializes
the security audit logger (mkdir + stderr banner). PICERL labels are reproduced
locally (lockstep test against `SANSPhase.label`); the MITRE dictionary is imported
lazily. `tests/test_report_not_in_verdict_path.py` asserts a fresh interpreter
importing `vigia.report` loads neither `vigia.sift` nor `vigia.security`.

### 6. Evidence — corpus render
346 bundles under `results/` (310 agent, 14 MCP, 4 EBS v1, 18 unrecognized) render in
all four variants without error; every sealed verdict token appears verbatim; no
decimal absent from the bundle or the static tables is introduced; no emoji; no
absolute path the bundle did not already contain; the parsed dict is never mutated.

### 7. Evidence — determinism
Two fresh interpreters with `PYTHONHASHSEED` 0 vs 1, different `LANG` and `TZ`,
render one bundle per family into byte-identical output (SHA-256 per variant).

### 8. Evidence — narrative auditor
Static strings and glossary, and fixture renders, pass `NarrativeAuditor` in strict
mode. One fixture initially failed on the word "naturally" (FALSE_FAMILIARITY); the
fixture text was changed, not the auditor.

### 9. Decision sealed
Five commits: adapter + strings + glossary (+ normalizer fix); renderers; writer +
CLI; agent hook; docs + training + L-074 + this trace. Agent hook is opt-in
(`--audience none` by default) so no existing output changes; kill switch
`VIGIA_AUDIENCE_REPORTS_ENABLED`, deliberately not registered in `config_sentinel`.

---

## Hypotheses summary

| Label | Status | Outcome |
|-------|--------|---------|
| `H1_presentation_outside_seal` | Confirmed | Sibling files; bundle bytes and `.sha256` sidecar byte-identical with and without the flag (end-to-end test) |
| `H2_extend_evidence_narrative_gen` | Refuted | float coercion, emoji, generation timestamp, EBS-only; new module instead |
| `H3_no_derived_labels` | Adopted as rule | No ENFSI bucket, no percentage, no rounding; `render_scalar` is the single transformation |

---

## Decision

Ship `vigia/report/` as a viewer with zero verdict authority. Two audiences, two
languages, three bundle families, one rule: sealed values verbatim, gaps explicit,
nothing inside the seal, no timestamp. Training guides and four renderer-generated,
test-pinned worked examples under `docs/training/`. KNOWN_LIMITATIONS L-074 records
what the layer inherits from each family and cannot fill.

---

## Quality metrics

| Metric | Value |
|--------|-------|
| Quality tier | STANDARD |
| Observational diversity | 3/3 (corpus renders, cross-process determinism, boundary refusals) |
| Tests added | 11 files, 460+ cases incl. 346 parametrized corpus renders |
| Verdict-path modules touched | 0 (`vigia/ui/normalizer.py` is a viewer; `vigia_agent.py` change is post-seal) |
| Confidence submitted | 4/5 |
| Confidence stored | 4/5 |

---

## Chain of custody

```
entry_hash : not recorded — CRONOS MCP unavailable in this session
chain_ok   : not recorded
git        : five commits on claude/modo-vogia-juniors-expertos-h0tjrl (see git log)
```
