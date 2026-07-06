# AUDITORIA — Motor sin label (blind scoring)

Red-team run of the corpus with `expected_verdict` removed at scoring time, plus a
case-schema validation pass. Every number below was produced by running the code on
this repository state; nothing is estimated. This document reports measurements only —
no architectural proposals.

- **Scope:** Mode 1 deterministic path. Two engines compared:
  - **Agent** — `vigia_agent.py` -> `sift_orchestrator.py` (shim) -> `_analyze_ebs_json`
    (`source = ebs_v1_json_adapter` for all JSON cases).
  - **Motor** — standalone `vigia_scorer.py` (`_vigia_score`), pipeline
    TrustFusion -> CorrelationDecay -> CAIE -> Decision -> Quadripartite.
- **Blind run:** `expected_verdict` stripped from a copy of each case before scoring.
  Repo cases were not modified.
- **Ground truth:** each case's original `expected_verdict`.
- **Verdict normalization for FP/FN:** MALICE and INTENT/SUSPICION -> "malicious";
  NOISE/BENIGN -> "benign"; UNKNOWN/ABSTAIN -> "abstain".
- **Corpus:** `run_all_agent.find_cases(CASES_DIRS)` = 199 cases (198 with an
  `artifacts` list; 1 is a pipeline-error case).

---

## 1. Case-schema validator

`python3 validate_case.py <case>` over the full corpus (run serially):

| Result | Count |
|---|---|
| PASS | **54 / 199** |
| FAIL | **145 / 199** |

Most frequent errors (serial run):

| Count | Error class |
|---|---|
| 1082 | `'<field>' ausente en metadata — acquisition_assurance=0` (missing `acquisition_tool` / `acquisition_hash` / `acquisition_timestamp`) |
| 246 | artifact required field missing (`artifact_id`, `evidence_type`, `source_tool`, `raw_score`, ...) |
| 243 | case-root required field missing (`schema_version`, ...) |
| 41 | `raw_score=-1 fuera de rango [0.0, 1.0]` |

`OWL-NEXUS5-CASE` alone reports 181 errors (its artifacts are not in EBS shape:
missing `artifact_id` / `evidence_type` / `raw_score`).

---

## 2. Blind run — agent vs motor over the corpus

`expected_verdict` stripped from every case before scoring.

| Engine | Verdict distribution (blind) |
|---|---|
| **Agent** (`ebs_v1_json_adapter`, 198/198) | **NOISE 189, ABSTAIN 9** — zero malicious detections |
| **Motor** (`_vigia_score`) | **MALICE 108, INTENT 35, NOISE 41, ABSTAIN 14** |

- With `expected_verdict` present, the agent reproduces the label
  (measured separately: agent verdict == label in 194/196 label-bearing cases).
- With `expected_verdict` removed, the agent's `_analyze_ebs_json` falls back to
  `avg > Fraction(2,1)` (`sift_orchestrator.py:620`), which never triggers for scores
  in `[0,1]` (corpus max `avg` = 0.87), so every case collapses to NOISE/ABSTAIN.
- The motor produces a distributed verdict without the label.

### Motor blind — accuracy vs ground truth

| | Count |
|---|---|
| Correct (malicious/benign) | 165 |
| False positive (gt benign, motor malicious) | **3** |
| False negative (gt malicious, motor benign/abstain) | **17** |
| Other (abstain ground truth, etc.) | 13 |

Of the 17 FN: ~11 are UNKNOWN/ABSTAIN (the motor abstains rather than clearing) and
~6 are NOISE (the motor clears a malicious case).

---

## 3. Refuted hypothesis — validator failure does NOT cause the FP/FN

**Hypothesis (abduction):** the FP/FN come from cases failing the validator (missing
acquisition metadata -> degraded trust -> mis-scoring).

**Deduction:** adding the missing acquisition metadata so the case passes the validator
should move the motor verdict toward ground truth.

**Induction (measured):** acquisition metadata added to blind copies; motor re-scored.

| Case | motor before | motor after fix | validator after fix |
|---|---|---|---|
| FP-CULTURAL-CLEAN-001 | MALICE | **MALICE** (unchanged) | PASS* |
| VIGIA-FN-002 | NOISE | **NOISE** (unchanged) | PASS* |
| VIGIA_KIWI_006 | NOISE | **NOISE** (unchanged) | PASS (already) |
| VIGIA-2026-DEMO-009 | UNKNOWN | **UNKNOWN** (unchanged) | PASS* |

\* the only residual validator error after the metadata fix is the intentionally
removed `expected_verdict`.

**Result: hypothesis refuted.** The verdict does not move. Validator hygiene is a
separate corpus issue; it is not the cause of the FP/FN.

---

## 3b. Label-flip test — leakage isolated to the agent

Single case (`VIGIA-CAN-008`), flip **only** `expected_verdict` MALICE -> NOISE, change
nothing else, measure both engines. Motor seal = SHA-256 of the decision dict excluding
the passthrough `expected_verdict` field; agent seal = SHA-256 of bundle content
excluding volatile timestamps / audit trail.

| `expected_verdict` | Engine | verdict | score / posterior | seal |
|---|---|---|---|---|
| MALICE | Motor | MALICE | score 0.5553 | `260aef13...` |
| NOISE | Motor | MALICE | score 0.5553 | `260aef13...` |
| MALICE | Agent | MALICE | posterior 57/1000 | `ef326ea9...` |
| NOISE | Agent | NOISE | posterior 57/1000 | `d31bdf42...` |

- **Motor:** verdict, score, and seal are identical under both labels. No leakage.
- **Agent:** the same posterior `57/1000` is sealed as MALICE under one label and NOISE
  under the other; the seal changes. The label determines the agent's verdict and seal.

## 3c. `avg > 2` — concrete unreachable threshold (code audit)

The agent's decision in `_analyze_ebs_json` (`sift_orchestrator.py`):

```
effective  = raw_score * prior_trust        # per artifact (line ~604)
avg        = mean(effective)                # line ~616
is_malice  = avg > Fraction(2, 1) or expected == "MALICE"   # line 620
```

`validate_case.py` enforces `0.0 <= raw_score <= 1.0` and `0.0 <= prior_trust <= 1.0`
(lines 128, 132). Therefore for any schema-valid case:

- `effective = raw_score * prior_trust` in `[0, 1]`
- `avg = mean(effective)` in `[0, 1]`, theoretical max `1.0` (all artifacts raw=1, trust=1)

The threshold `avg > 2` is **unreachable** for normalized inputs — it requires twice the
domain maximum. The evidence branch to MALICE can never fire; the only surviving route to
`MALICIOUS_INTENT_DETECTED` in this adapter is `expected == "MALICE"`, i.e. the label.
Measured corpus max `avg` = 0.87. This is the concrete mechanism behind the label-flip
result in 3b.

---

## 4. Verified root causes (deduction confirmed by induction)

### 4.1 FP — `evidence_type=cultural_marker` with high `raw_score` (language-independent)

Clean host (memory / LSASS / MFT raw 0.04-0.08, trust 0.95) plus one `cultural_marker`
artifact (raw 0.85, trust 0.3). Ground truth NOISE.

| Run | Motor verdict | Score |
|---|---|---|
| Full case | MALICE | 0.4209 |
| `cultural_marker` artifact removed | NOISE | 0.0336 |

Dropping the single `cultural_marker` artifact flips the verdict to NOISE.

**This is NOT a language / script bias.** Varying only the filename script while holding
`raw_score=0.85`, `evidence_type=cultural_marker`, and the two clean forensic artifacts
constant yields an identical score for every script (measured):

| Script in `cultural_marker` description | Motor verdict | Score |
|---|---|---|
| Latin (control) `report_finance.docx` | SUSPICION | 0.3612 |
| Cyrillic `отчет_финансы.docx` | SUSPICION | 0.3612 |
| Arabic `تقرير_مالي.docx` | SUSPICION | 0.3612 |
| Chinese `财务报告.docx` | SUSPICION | 0.3612 |
| Japanese `財務報告.docx` | SUSPICION | 0.3612 |

The score is byte-identical across all five scripts — the scorer does not read the
Unicode content. What drives the elevation is the artifact's `evidence_type` and
`raw_score`, isolated by these controls (Cyrillic held fixed):

| Perturbation | Motor verdict | Score |
|---|---|---|
| `cultural_marker`, `raw_score=0.05` | NOISE | 0.0033 |
| `evidence_type=log_entry`, `raw_score=0.85` | NOISE | 0.0062 |
| Latin + `log_entry`, `raw_score=0.85` | NOISE | 0.0062 |

Same `raw_score=0.85` as a `log_entry` does not elevate; as a `cultural_marker` it does.
Grounded in code (`vigia/tools/caie.py`):

- `evidence_role("cultural_marker")` returns `DEVICE` (default; it is not in the
  NARRATIVE set `behavioral_context` / `behavioral_profile` / `outcome_signal`,
  `caie.py:372-387`), so it feeds the malice composite instead of being set aside as
  contextual.
- Its spoofability profile is `EvidenceProfile(0.90, 0.15, "Language, keyboard layout
  -- easy to fake")` (`caie.py:249`), commented in-code as the worst real class.

So the FP is a weighting of the `cultural_marker` evidence class as scored DEVICE
evidence, independent of the language of the content — not a Cyrillic/cultural bias.
(The 0.4209 in the first table vs 0.3612 here reflects the exact metadata fields present
in the original artifact; the language is irrelevant in both.)

### 4.2 FN — low-trust colluding sources (`VIGIA_KIWI_006` / `VIGIA_KIWI_007`)

Non-independent witnesses, `prior_trust` 0.1-0.15. Ground truth SUSPICION.
These cases **pass the validator**.

| Run | Motor verdict | Score |
|---|---|---|
| Full case (trust 0.1-0.15) | NOISE | 0.0294 |
| `prior_trust` raised to 0.85 | SUSPICION | 0.2101 |

Raising trust flips it toward detection. The low `prior_trust` collapses the composite;
the suspicion in the case is structural (linked witnesses), which the per-artifact score
does not model.

### 4.3 FN — constellation / living-off-the-land (`VIGIA-FN-002`)

Legit Veeam agent (raw 0.05), backup traffic to an external IP (raw 0.05), no change
ticket (raw 0.08). Ground truth MALICE.

| Run | Motor verdict | Score |
|---|---|---|
| Full case | NOISE | 0.0179 |

Every artifact is individually low-raw; the maliciousness is emergent across the set.
The per-artifact aggregation lands at 0.0179 -> NOISE.

### 4.4 FN — honest abstention (`VIGIA_BREAK_001..010`, `VIGIA-2026-DEMO-008/009`)

The motor returns UNKNOWN (low confidence, e.g. 0.26-0.30) instead of clearing.
Counted as FN against a malicious ground truth, but the emitted verdict is ABSTAIN,
not a benign clear.

---

## 5. Red-team fixtures

Four fixtures generated in `data/cases/red-team/`, derived from the verified cases
above (acquisition metadata + `schema_version` added so 1-3 pass the validator).
Numbers below are measured on the fixture files as written.

| Fixture | Derived from | GT | Validator | Motor blind | Agent (label present) | Agent (label removed) |
|---|---|---|---|---|---|---|
| `RT-FP-CULTURAL-001` | FP-CULTURAL-CLEAN-001 | NOISE | PASS | **MALICE** 0.4209 (conf 0.84) | NOISE | NOISE |
| `RT-FN-COLLUSION-001` | VIGIA_KIWI_006 | SUSPICION | PASS | **NOISE** 0.0294 (conf 0.97) | INTENT | NOISE |
| `RT-FN-CONSTELLATION-001` | VIGIA-FN-002 | MALICE | PASS | **NOISE** 0.0179 (conf 0.98) | MALICE | NOISE |
| `RT-NOLABEL-001` | VIGIA-CAN-008 | (removed) | FAIL (1 err: missing `expected_verdict`, by design) | **MALICE** 0.5553 (conf 0.95) | (no label in file) | NOISE |

Notes:
- Agent "label present" reproduces the label (NOISE->NOISE, SUSPICION->INTENT,
  MALICE->MALICE); agent "label removed" collapses to NOISE in all four.
- `RT-FP-CULTURAL-001`, `RT-FN-COLLUSION-001`, `RT-FN-CONSTELLATION-001` pass the
  validator, so their FP/FN are not a data-hygiene artifact.
- `RT-NOLABEL-001` fails the validator only on the intentionally removed
  `expected_verdict`; it is otherwise schema-valid.

Reproduce:
```
python3 validate_case.py data/cases/red-team/RT-FP-CULTURAL-001.json
python3 -c "import json; from vigia_scorer import _vigia_score; \
c=json.load(open('data/cases/red-team/RT-FP-CULTURAL-001.json')); c.pop('expected_verdict',None); \
print(_vigia_score(c)['verdict'])"
```

---

## Limitations of this audit

- Measured on the JSON-case path only (Domain B). Raw-evidence paths (E01 / evtx /
  memory) were not exercised here.
- No LLM was run (deterministic path only).
- No pipeline code was modified. Blind copies and fixtures were written to
  `data/cases/red-team/` and to the session scratchpad; repo corpus cases were left
  unchanged.
