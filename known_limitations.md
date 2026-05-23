# VIGÍA — Known Limitations

## Version: EBS v1 | Updated: 2026-05-23

These limitations are deliberately documented as part of the Daubert standard
of falsifiability. VIGÍA does not claim to be infallible — it claims to be
auditable.

---

## L-001 — Perfect Attack With No Anomalies (BREAK_006)

**Description:** When an attacker executes an operation without technical
errors (valid credentials, consistent timestamps, no detectable tools),
VIGÍA tends to emit SUSPICION instead of MALICE.

**Cause:** The scoring engine depends on structural anomalies and CAIE
fractures. Without inconsistencies, the score does not exceed the MALICE
threshold.

**Forensic implication:** VIGÍA is more effective detecting attacks with
operational errors than high-level APTs with perfect OPSEC.

**Workaround:** Combine with baseline behavioral analysis
(baselines_institucionales.yaml) to detect statistical deviations.

---

## L-002 — Critical Signal Drowned in Noise (BREAK_004)

**Description:** When there are many irrelevant artifacts and few critical
ones, the average score drops and VIGÍA emits SUSPICION instead of MALICE.

**Cause:** The evidence aggregator does not yet implement dynamic weighting
by artifact type. All artifacts carry similar initial weight before trust
adjustment.

**Forensic implication:** In high-noise cases, it is recommended to
pre-filter artifacts by relevance before entering the pipeline.

---

## L-003 — Absence of Logs as Evidence (BREAK_007)

**Description:** The absence of records where they should exist (e.g.,
SSH session present in netflow but no entry in auth.log) does not generate
sufficient signal to reach MALICE.

**Cause:** The current model treats absent evidence as neutral noise,
not as a positive signal of manipulation.

**Forensic implication:** Detection of "significant silence" requires
comparison against institutional baselines. Without a configured baseline,
VIGÍA cannot evaluate absences.

---

## L-004 — Prompt Poison / Deceptive Narrative (BREAK_009)

**Description:** When a text artifact contains statements such as "case
already confirmed benign by the team", VIGÍA does not distinguish between
unverified narrative text and structured technical evidence.

**Cause:** LLMShield filters direct injections into the reasoning engine,
but does not neutralize deceptive narratives embedded in free-text artifacts.

**Forensic implication:** All free-text artifacts must be manually assigned
reduced trust. Do not rely on unverifiable claims embedded in evidence.

**Reference:** Austin (1962) — false performative speech acts. A text that
says "this is benign" does not make the evidence benign.

---

## L-005 — Verdict Threshold vs. Ambiguous Evidence (BREAK_002, BREAK_005)

**Description:** Cases with suspicious but authorized activity (documented
pentest) or simultaneous unrelated events produce SUSPICION or UNKNOWN
instead of more precise verdicts.

**Cause:** VIGÍA has no access to external organizational context (tickets,
authorizations, policies) during automated analysis.

**Forensic implication:** For cases with authorization context, the analyst
must manually review the SUSPICION/UNKNOWN verdict and incorporate context
into the final report.

---

## L-006 — Single Temporal Inconsistency (BREAK_001)

**Description:** A single artifact with an inconsistent timezone among three
aligned artifacts produces MALICE, when greater uncertainty might be expected.

**Cause:** The EFFECT_BEFORE_CAUSE hard gate and the temporal inconsistency
penalty are aggressive by design — they prioritize false positives over false
negatives in a forensic context.

**Design decision:** In forensics, it is preferable to investigate a case
that turned out to be benign than to ignore one that turned out to be
malicious. This behavior is intentional.

---

## L-007 — Corpus Bias Toward MALICE (Daubert Concern)

**Description:** The canonical case corpus (`vigia_cases_canonical_v2.json`,
`vigia_cases_consolidated.json`) contains 51/52 and 40/41 cases with
`expected_verdict: MALICE` respectively. Only 1 case per file has a different
verdict (SUSPICION). There are no NOISE or BENIGN cases in the main canonical
corpus.

**Cause:** The corpus was built from real and synthetic cases representing
confirmed attack scenarios. Benign cases exist in `data/cases/benign/`
(15 files, VIGIA-BEN-001..015) and break cases in `data/cases/converted/`,
but neither is integrated into the canonical v2 corpus.

**Forensic implication (Daubert):** An external evaluator could object that
accuracy metrics are inflated if the evaluation corpus does not include
representative false positives. The reported error rate has not been validated
against real-world distributions of benign cases in production.

**Status:** Accepted as technical debt. Benign/break cases exist in the repo
but require formal integration into the canonical corpus.

**Workaround:** For complete evaluation, run `evaluate_detector.py` explicitly
including `data/cases/benign/` and `data/cases/converted/VIGIA_BREAK_*`.

---

## L-008 — Academic Documents With Non-Human-Readable Hash Names

**Description:** Directories `docs_clean/`, `docs_generados/`, and
`docs_merged/` contain ~180 files named `02a8adb4_doc.md`,
`0b4cea01_doc.md`, etc. These are batch-generated academic documents
whose correspondence to the module they document is not evident from the
filename.

**The `docs/academic/` directory contains the same documents with readable
names** (`caie_academic.md`, `pipeline_academic.md`, etc.) and should be
considered the canonical source for human navigation.

**Cause:** The three directories (`docs_clean/`, `docs_generados/`,
`docs_merged/`) are intermediate artifacts from the batch documentation
generation process. They are redundant with respect to `docs/academic/`.

**Risk:** Confusion for external reviewers (including hackathon judges)
who navigate the repo and encounter hundreds of files with meaningless names.

**Pending action (pre-deadline):** Remove or move to `.archive/` the
directories `docs_clean/`, `docs_generados/`, and `docs_merged/` before
submission. Verify that `docs/academic/` is complete and no documented
module is missing.

**Status:** PENDING — does not block functionality, blocks repo readability.

---

## Summary

| ID | Case | VIGÍA Output | Expected | Type |
|----|------|-------------|----------|------|
| L-001 | BREAK_006 | SUSPICION | MALICE | Real limitation |
| L-002 | BREAK_004 | SUSPICION | MALICE | Real limitation |
| L-003 | BREAK_007 | SUSPICION | MALICE | Real limitation |
| L-004 | BREAK_009 | UNKNOWN | MALICE | Real limitation |
| L-005 | BREAK_002/005 | UNKNOWN/SUSPICION | NOISE/UNKNOWN | Debatable |
| L-006 | BREAK_001 | MALICE | UNKNOWN | Design decision |
| L-007 | corpus bias | — | — | Technical debt / Daubert |
| L-008 | hash doc names | — | — | Presentation debt |
