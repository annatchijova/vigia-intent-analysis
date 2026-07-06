---
name: peirce-abduction
description: >
  Run a full Peircean abductive forensic investigation using the VIGÍA playbook.
  Use when starting a new investigation on an artifact, case file, or evidence
  directory. Invokes Phases 1–5: evidence preservation → signal acquisition →
  intentionality analysis → self-correction (Eco's Razor) → structured report.
triggers:
  - /peirce
  - /abduction
  - /investigar
---

Conduct a complete Peircean abductive forensic investigation on the provided
evidence. Follow this protocol exactly, in order. Do not skip phases.

---

## Phase 1 — Evidence Preservation

1. Verify `VIGIA_EVIDENCE_DIR` is set and the path exists.
2. Call `generate_forensic_hash` on every artifact **before reading**. Record
   hash, file size, and timestamp. This is the chain-of-custody anchor.
3. If evidence is a disk image, call `mount_sift_evidence`.
4. Call `list_files` on the evidence directory to survey scope.
5. Log every tool call: tool name, arguments, result summary.

---

## Phase 2 — Signal Acquisition

1. `calculate_shannon_entropy` on all binary artifacts and anomalous text.
   Baseline: plaintext 4.0–5.0 bits/byte; packed payload > 7.5 bits/byte.
2. `detect_habit_incongruence` on process lists and execution artifacts.
3. `audit_network` — active ports and connections.
4. `search_pattern` — C2 strings, staging artifacts, anti-forensic signatures.
5. `audit_image_metadata` on image artifacts.
6. Flag every anomaly: inode/path · tool that found it · confidence HIGH/MEDIUM/LOW.

---

## Phase 3 — Intentionality Analysis (Peirce Core)

Apply triadic reasoning **before** calling tools on any MEDIUM or higher anomaly:

- **Firstness** — What is the raw phenomenon? Describe precisely, no interpretation.
- **Secondness** — Is it structurally consistent with its context? What is the
  baseline? How does this deviate?
- **Thirdness** — What repeatable pattern of deliberate behavior does it reveal?
  What legitimate expectation is being weaponized (Carnegie taxonomy)?

Then:

1. `infer_intent` — primary Peirce inference engine.
2. `audit_grice_maxims` — for text/communication artifacts.
3. `detect_human_jitter` / `calculate_human_entropy` — for timing data.
4. `analyze_stylometry` — if multiple sources show identical anomalies.
5. `detect_eco_overinterpretation` — if evidence is implausibly well-aligned
   (too-perfect evidence is itself a fabrication signal).

---

## Phase 4 — Mandatory Refutation (Eco's Razor — Daubert)

**Required before any INTENT or MALICE verdict. Cannot be skipped.**

1. `validate_and_correct_analysis` — review own reasoning for Peircean fallacies.
2. Formulate the **strongest possible benign/incompetence hypothesis**.
3. Test it against the full evidence set:
   - If it explains ALL anomalies → downgrade to SUSPICION.
   - If it fails → maintain or upgrade to INTENT/MALICE.
4. If novel patterns remain and LLM is available → `reason_with_llm`.
5. `devil_advocate` field **must be populated**. Empty = verdict invalid under Daubert.

---

## Phase 5 — Report

Produce the structured VIGÍA report:

```
VIGIA FORENSIC INTENT ANALYSIS REPORT
======================================
Case ID      :
Investigator : VIGÍA Autonomous Agent (Claude Code / Anthropic)
Evidence     :
Mode         : Claude Code | Ollama | FALLBACK
SHA-256      :
Timestamp    : [ISO 8601 UTC]
SANS Phase   :

EXECUTIVE SUMMARY
-----------------
[2–3 sentences: what was analyzed, what was found, overall verdict]

FINDINGS
--------
Finding ID   : F-NNN
Verdict      : NOISE | SUSPICION | INTENT | MALICE | ABSTAIN
Confidence   : HIGH | MEDIUM | LOW
Status       : CONFIRMED | INFERRED | REFUTED
Firstness    :
Secondness   :
Thirdness    :
Carnegie     :
MITRE TTPs   :
Devil Advocate:
Corroboration:

KNOWN LIMITATIONS
-----------------
```

**Verdict scale:**

| Verdict | Requirement |
|---------|-------------|
| `MALICE` | Active concealment + two independent sources + `devil_advocate` populated |
| `INTENT` | Deliberate decisions evidenced + two independent sources + Refutation Protocol |
| `SUSPICION` | Structural anomaly, no confirmed deliberate concealment |
| `NOISE` | Fully explained by misconfiguration or normal behavior |
| `ABSTAIN` | Insufficient evidence — document the gap explicitly |
