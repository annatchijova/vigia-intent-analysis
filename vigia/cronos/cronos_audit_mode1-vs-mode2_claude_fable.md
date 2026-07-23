# Cronos Audit Trail — Mode-1 vs Mode-2 cross-check (VIGIA, Claude Fable)
<!-- trace_id: f0aa8447-6688-44fa-b9f0-ed054d169a5f -->

| Field | Value |
|-------|-------|
| Trace ID | `f0aa8447-6688-44fa-b9f0-ed054d169a5f` |
| Agent | `vigia-claude-fable` |
| Started | 2026-07-23T03:29:04 UTC |
| Closed | 2026-07-23T03:30 UTC (approx) |
| Quality | MINIMAL (observational diversity 1/3) |
| Confidence | 3/5 stored (submitted 22/25 — capped by diversity ceiling) |
| Chain hash | `8c938a1d30dfeab910c065c71284854836a5ca197b48c43f842ccdc3ffd13640` |
| Chain integrity | OK (chain_ok=true at close) |
| Cronos version | chain v2 (SHA-256 tamper-evident) |

---

## Objective

Run the deterministic Mode-1 agent (vigia_agent.py, no LLM) against the session's
cases and compare to the Mode-2 analyst verdicts, over curated JSON and over raw
evidence, to document VIGÍA's architectural boundaries.

---

## Step-by-step trace

### 1. Trace opened — cronos_open_trace (2026-07-23T03:29:04 UTC)

### 2. Evidence — Mode-1 verdicts by input

Mode-1 over curated JSON: FLARE-On MALICE (intent 0.8106, cross-domain 3 domains);
OWL-COMPLETE and OWL-NEXUS5 ABSTAIN (normalization integrity loss — metadata coerced
at intake); JESS SUSPICION (0.1395 floored). Over RAW FLARE-On binaries: ABSTAIN
(composite 0.0022, CDL coverage 16.7%, 1 primary signal of 5). Same case, three
verdicts by input: JSON-MALICE / raw-ABSTAIN / Mode2-INTENT.

### 3. Evidence — lessons

(1) verdict quality tracks ingested-evidence coverage; (2) VigiaPipeline.run_full
bypasses the honest-degradation gate that vigia_agent.py applies (the whole OWL
REJECT-vs-ABSTAIN difference); (3) the deterministic core cannot apply world-context
(CTF => no real malice). Both readings preserved; no divergence is a real evidence
disagreement.

### 4. Trace closed — cronos_close_trace (2026-07-23T03:30 UTC)

Confidence submitted 22/25, stored 3/5 (diversity ceiling 1/3). Quality MINIMAL,
chain_ok=true.

---

## Hypotheses summary

| Label | Status | Outcome |
|-------|--------|---------|
| (methodology cross-check, no rival hypotheses) | — | Divergences all map to documented Mode-1 boundaries. |

---

## Decision

**Mode-1 does NOT reproduce the Mode-2 labels, but every divergence lands on a
documented architectural boundary, not a real evidence disagreement.** FLARE-On
agent=MALICE(JSON)/ABSTAIN(raw) vs analyst INTENT; OWL agent=ABSTAIN (integrity
gate) vs analyst INTENT (run_full bypasses the gate); JESS agent=SUSPICION vs
analyst ABSTAIN (adjacent). Documented in
vigia/results/MODE1-vs-MODE2_crosscheck_claude_fable.md; agent bundles in
vigia/results/mode1_crosscheck/.

---

## Quality metrics

| Metric | Value |
|--------|-------|
| Quality tier | MINIMAL |
| Observational diversity | 1/3 groups |
| Confidence submitted | 22/25 (88%) |
| Confidence stored | 3/5 (60%) — capped by diversity ceiling |

**Confidence warnings:** Confidence 22/25 capped at 3/5 (diversity ceiling: 1/3
observation groups).

**Contradictions flagged by Cronos:** none.

---

## Chain of custody

```
entry_hash : 8c938a1d30dfeab910c065c71284854836a5ca197b48c43f842ccdc3ffd13640
chain_ok   : true
```
