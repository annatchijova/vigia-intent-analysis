# VIGÍA — Mode-1 (deterministic agent) vs Mode-2 (Claude Code analyst) cross-check

**Author:** VIGIA Autonomous Agent (Claude Code / Claude Fable)
**Date:** 2026-07-23
**Purpose:** Run the deterministic `vigia_agent.py` (Mode 1, no LLM) independently
against the cases resolved this session and record whether it reaches the same
verdict as the Mode-2 analyst — and, crucially, *why* it differs. Kept as a
methodology note for understanding VIGÍA's architectural boundaries.

---

## What was run, and on what input

- **Mode-2 (analyst, this session):** live tool analysis (hashing, entropy, string
  indicators, MCP tools) plus `VigiaPipeline.run_full` sealing on the case JSON —
  and, for ROCBA/OWL-HD1/FLARE-On, direct inspection of the **raw** evidence.
- **Mode-1 (`vigia_agent.py`):** the deterministic autonomous agent. It accepts
  either a **curated case JSON** (`data/cases/*.json`, a pre-distilled artifact list)
  or **raw evidence** (a directory/image it must extract itself).

**Answer to "did it run on JSON or raw?":** the first cross-check ran on the
**curated case JSON**. A second run put it on the **raw** FLARE-On binaries. The two
inputs produce *different* verdicts — that difference is the most important finding
here.

---

## Result table (Mode-1 over curated JSON)

| Case | Mode-2 analyst verdict | Mode-1 agent (JSON) | Agreement |
|------|------------------------|---------------------|-----------|
| FLARE-On 4 (2017) | INTENT (MALICE refuted by CTF context) | **MALICE** (intent score 0.8106, cross-domain: 3 domains / 14 artifacts) | signal agrees; label differs by context |
| OWL-COMPLETE | INTENT | **ABSTAIN** (posterior 17/100, normalization integrity loss) | no |
| OWL-NEXUS5 | SUSPICION | **ABSTAIN** (ABSTAIN_DETECTED, normalization integrity loss) | no |
| MAGNET-2022-iOS-JESS | ABSTAIN | **SUSPICION** (score 0.1395, alert floored) | adjacent |

## The JSON-vs-raw split (FLARE-On 4)

| Input to Mode-1 | Verdict | Why |
|-----------------|---------|-----|
| Curated JSON (14 hand-authored artifacts) | **MALICE** | intent score 0.8106, cross-domain corroboration across 3 domains |
| **Raw binaries** (`evidence/flare-on/flareon4/`) | **ABSTAIN / UNDETERMINED** | composite 0.0022, CDL coverage only 16.7%, 1 primary signal of 5, "sin base para inferencia abductiva" |
| Mode-2 analyst (live analysis on the same binaries) | **INTENT** | deliberate obfuscation/anti-analysis/webshell/C2 confirmed, then MALICE tempered by sanctioned-CTF context |

---

## Why they differ — each gap lands on a documented boundary

1. **FLARE-On: agent MALICE (JSON) vs analyst INTENT — the agent validates the raw
   signal, it does not contradict it.** The deterministic motor sees the offensive
   tradecraft and scores it MALICE (0.81), matching the CAIE structural MALICE
   (0.5277) the analyst reported. The only difference is the **context refutation**
   ("this is a sanctioned, published CTF — no victim, no deployment"), which a
   deterministic engine with no world-knowledge cannot apply. The analyst tempers
   MALICE → INTENT; the agent confirms the underlying signal is MALICE-strength.

2. **OWL: agent ABSTAIN vs analyst INTENT/SUSPICION — the agent is *more*
   conservative, and correctly so.** `vigia_agent.py` refuses to emit a verdict
   because of **"NORMALIZATION INTEGRITY LOSS"**: an artifact's metadata (the
   `significance` field carrying `..`, from the coordination-SMS artifact) was
   coerced during intake, which can silently drop a scoring-relevant assertion. The
   analyst's Mode-2 bundles used `VigiaPipeline.run_full` **directly**, which does
   **not** apply that honest-degradation gate — hence the analyst path returned
   REJECT/posterior 1.0 while the full agent abstains. This matches the pre-existing
   B-160/B-206 finding (the semantic-extractor gap leaves OWL-NEXUS5 in honest
   ABSTAIN). Honest degradation (§5.3) working as designed.

3. **JESS: agent SUSPICION vs analyst ABSTAIN — adjacent, no real conflict.** Both
   sit in the low-confidence band (agent score 0.1395, floored to a SUSPICION alert;
   analyst ABSTAIN). One step apart on the scale, same underlying uncertainty.

---

## Lessons (the gold)

1. **A verdict is only as good as the evidence the engine actually ingested.** On the
   **raw** FLARE-On binaries the agent covered just **16.7%** and abstained; on the
   **curated JSON** it reached MALICE. The JSON run is, in effect, scoring the
   *analyst's pre-digested findings*, not the raw bytes. Any Mode-1 verdict over a
   curated JSON must be read as "given these artifacts", not "from the raw evidence".
   (Same lesson as the earlier JESS note: iOS engine had never run on real SQLite,
   only curated JSON, until it was actually pointed at raw.)

2. **The LLM-out-of-the-loop architecture holds, and cuts both ways.** Where the
   analyst added *world-context* (CTF ⇒ no real malice), the deterministic core could
   not — and stayed at the raw signal. Where the analyst's convenience path
   (`run_full`) *skipped* an integrity gate, the full agent caught it and abstained.
   Neither side is uniformly "right"; the value is in preserving **both** and reading
   the delta.

3. **`run_full` ≠ the full Mode-1 agent.** The direct pipeline call bypasses the
   normalization-integrity / honest-degradation gates that `vigia_agent.py` applies.
   For OWL this is the whole difference between REJECT/posterior-1.0 and ABSTAIN. Seal
   with `run_full` for a raw decision score; run `vigia_agent.py` for the
   gate-protected, honestly-degrading verdict — and expect them to disagree exactly
   where an integrity gate fires.

4. **The Mode-2 verdicts this session stand, with a documented caveat.** The
   analyst verdicts (ROCBA MALICE, OWL INTENT, JESS ABSTAIN, FLARE-On INTENT) rest on
   analyst reasoning (context, cross-device corroboration) plus `run_full`. The
   Mode-1 agent, over the same JSON, is more conservative on OWL (ABSTAIN via the
   integrity gate) and stricter on FLARE-On (MALICE, no context). Both readings are
   preserved; neither silently overrides the other (Mode-1/Mode-2 scope rule).

---

## Reproduce

```bash
# Mode-1 over curated JSON (agreement / integrity-gate behaviour)
python3 vigia_agent.py --evidence data/cases/VIGIA-FLAREON-4.json      --case-id X --output out.json   # MALICE
python3 vigia_agent.py --evidence data/cases/VIGIA-OWL-2019-COMPLETE.json --case-id X --output out.json # ABSTAIN
python3 vigia_agent.py --evidence data/cases/OWL-NEXUS5-CASE.json      --case-id X --output out.json   # ABSTAIN
python3 vigia_agent.py --evidence data/cases/converted/VIGIA-MAGNET-2022-iOS-JESS.json --case-id X --output out.json # SUSPICION

# Mode-1 over RAW binaries (coverage-limited abstention)
python3 vigia_agent.py --evidence evidence/flare-on/flareon4 --case-id X --output out.json             # ABSTAIN (coverage 16.7%)
```
(Output path must stay inside the repo working directory — PathGuard blocks external paths.)
