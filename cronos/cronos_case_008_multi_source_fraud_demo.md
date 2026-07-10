# Cronos Audit Trail — case_008_multi_source_fraud_demo
<!-- trace_id: d37ff284-2343-43c1-bcdf-285b93d68f02 -->

| Field | Value |
|-------|-------|
| Trace ID | `d37ff284-2343-43c1-bcdf-285b93d68f02` |
| Agent | `vigia-claude-sonnet-4-6` |
| Started | 2026-07-10T17:58:44.972247+00:00 |
| Closed | 2026-07-10T18:07:29.774950+00:00 |
| Quality | MINIMAL (1/3 observation groups) |
| Confidence | 3/5 (submitted 7/10 — capped by diversity ceiling) |
| Chain hash | `60e9801d3263d100db60a3ec42bbec30f2f01d1b349c748692836f8044466c63` |
| Chain integrity | true |
| Cronos version | 0.1.0 |

---

## Objective

case_008_multi_source_fraud_demo: Classify DEMO-008 repackaged document fraud — acquisition gate (prior_trust 0.45) explicitly bounds at SUSPICION despite strong forgery evidence. Verdict: SUSPICION.

---

## Step-by-step trace

### 1. Hypothesis registered: `H1_document_forgery_exfil` (2026-07-10T18:01:16.476912+00:00)
DEMO-008 repackaged case: systematic multi-artifact document forgery (internal template on external audit, PNG digital signature, Photoshop-edited financials) covering accounting irregularities. Strong forgery evidence at behavioral level but acquisition chain (prior_trust 0.45) bounds verdict at SUSPICION under Daubert.

### 2. Hypothesis registered: `H2_legitimate_audit_with_weak_chain` (2026-07-10T18:03:09.517426+00:00)
Legitimate audit conducted by Dra. Goldstein; metadata anomalies explained by software/template differences. Prior_trust 0.45 means the acquisition chain itself is insufficient to confirm forgery under Daubert — chain-of-custody gaps prevent confirming H1 even if behavioral evidence is strong.

### 3. Evidence — supports `H2_legitimate_audit_with_weak_chain` (2026-07-10T18:05:08.280678+00:00)
Acquisition chain prior_trust 0.45 on primary documents. Placeholder provenance hashes prevent confirming chain-of-custody under Daubert. Behavioral pattern matches H1 (systematic forgery: internal template, internal email server, 13-day domain, PNG signature, ELA edits) but forensic record quality caps verdict at SUSPICION regardless of behavioral strength.

### 4. Decision sealed (2026-07-10T18:07:29.774950+00:00)
SUSPICION 70/100 — DEMO-008 repackaged: systematic document forgery pattern (internal template, internal mail server, 13-day domain, PNG signature, ELA edits). Acquisition chain prior_trust 0.45 prevents Daubert-compliant MALICE. Behavioral evidence is MALICE-level; evidentiary quality caps at SUSPICION.

---

## Hypotheses summary

| Label | Status | Outcome |
|-------|--------|---------|
| `H1_document_forgery_exfil` | Active (behaviorally confirmed) | Forgery pattern confirmed at behavioral level; acquisition chain (prior_trust 0.45) prevents Daubert MALICE |
| `H2_legitimate_audit_with_weak_chain` | Active (evidentiary gap) | Cannot be fully excluded due to acquisition chain weakness; placeholder hashes fail cross-examination |

---

## Decision

SUSPICION 70/100 — DEMO-008 repackaged: systematic document forgery pattern (internal template, internal mail server, 13-day domain, PNG signature, ELA edits). Acquisition chain prior_trust 0.45 prevents Daubert-compliant MALICE. Behavioral evidence is MALICE-level; evidentiary quality caps at SUSPICION.

---

## Quality metrics

| Metric | Value |
|--------|-------|
| Quality tier | MINIMAL |
| Observational diversity | 1/3 |
| Confidence submitted | 7/10 |
| Confidence stored | 3/5 — capped by diversity ceiling |

Confidence ceiling: only 1 of 3 observation groups covered. Submitted confidence 7/10 capped at 3/5.

---

## Chain of custody

```
entry_hash : 60e9801d3263d100db60a3ec42bbec30f2f01d1b349c748692836f8044466c63
chain_ok   : true
```
