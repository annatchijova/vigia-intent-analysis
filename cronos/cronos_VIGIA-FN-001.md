# Cronos Audit Trail — VIGIA-FN-001
<!-- trace_id: 3b9a893f-b148-4446-8336-ea79a5e2c0b2 -->

| Field | Value |
|-------|-------|
| Trace ID | `3b9a893f-b148-4446-8336-ea79a5e2c0b2` |
| Agent | `vigia-claude-sonnet-4-6` |
| Started | 2026-07-10T17:59:07.179866+00:00 |
| Closed | 2026-07-10T18:08:09.186552+00:00 |
| Quality | MINIMAL (1/3 observation groups) |
| Confidence | 3/5 (submitted 4/5 — capped by diversity ceiling) |
| Chain hash | `560506b9263b0db65ed41e96c4008f8e91ca06bbe96dfccaf9575ea84b693545` |
| Chain integrity | true |
| Cronos version | 0.1.0 |

---

## Objective

VIGIA-FN-001: Classify insider exfiltration — marketing_user logged in on vacation day, 500MB rclone to personal Google Drive. TEMPORAL_IDENTITY_VIOLATION. Verdict: MALICE.

---

## Step-by-step trace

### 1. Hypothesis registered: `H1_insider_vacation_exfil` (2026-07-10T18:01:57.134072+00:00)
marketing_user logged in on declared vacation day, accessed corporate documents, transferred 500MB via rclone to personal Google Drive account. TEMPORAL_IDENTITY_VIOLATION: HR records confirm user on vacation, physical building access logs show no badge entry. Credential use during documented absence is the identity-context fracture.

### 2. Hypothesis registered: `H2_authorized_remote_work` (2026-07-10T18:03:46.745026+00:00)
marketing_user worked remotely on declared vacation day for urgent business need. rclone to personal Google Drive is authorized cloud sync. HR vacation records may be incorrect or the user took time off but continued working voluntarily. Building badge absence is expected for remote work.

### 3. Evidence — refutes `H2_authorized_remote_work` (2026-07-10T18:05:45.530332+00:00) *(negation detected)*
HR records confirm marketing_user on declared vacation. Physical building access logs: no badge entry on the day of the login. Corporate phone: off. Login from IP not in registered home or corporate range. rclone destination: personal Google Drive (not corporate storage). TEMPORAL_IDENTITY_VIOLATION: all three identity context checks (HR, building, phone) independently confirm the declared person was not present at work. H2 (authorized remote work) refuted by three independent absence confirmations.

### 4. Decision sealed (2026-07-10T18:08:09.186552+00:00)
MALICE 80/100 — marketing_user exfiltrated 500MB via rclone to personal Google Drive on declared vacation day. H2 refuted by three independent absence confirmations: HR records, building badge log, corporate phone off. TEMPORAL_IDENTITY_VIOLATION: identity context and physical presence irreconcilable with authorized work activity. T1567 + T1078.

---

## Hypotheses summary

| Label | Status | Outcome |
|-------|--------|---------|
| `H1_insider_vacation_exfil` | Active (confirmed) | Three independent absence confirmations establish TEMPORAL_IDENTITY_VIOLATION; personal Drive destination |
| `H2_authorized_remote_work` | Discarded (refuted) | HR records + building badge + corporate phone all confirm declared vacation; IP not in registered range |

---

## Decision

MALICE 80/100 — marketing_user exfiltrated 500MB via rclone to personal Google Drive on declared vacation day. H2 refuted by three independent absence confirmations: HR records, building badge log, corporate phone off. TEMPORAL_IDENTITY_VIOLATION: identity context and physical presence irreconcilable with authorized work activity. T1567 + T1078.

---

## Quality metrics

| Metric | Value |
|--------|-------|
| Quality tier | MINIMAL |
| Observational diversity | 1/3 |
| Confidence submitted | 4/5 |
| Confidence stored | 3/5 — capped by diversity ceiling |

Confidence ceiling: only 1 of 3 observation groups covered. Submitted confidence 4/5 capped at 3/5.

---

## Chain of custody

```
entry_hash : 560506b9263b0db65ed41e96c4008f8e91ca06bbe96dfccaf9575ea84b693545
chain_ok   : true
```
