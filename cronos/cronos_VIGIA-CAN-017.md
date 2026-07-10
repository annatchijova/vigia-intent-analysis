# Cronos Audit Trail — VIGIA-CAN-017
<!-- trace_id: 84704aa6-daf1-46d5-82e3-84aa15e38758 -->

| Field | Value |
|-------|-------|
| Trace ID | `84704aa6-daf1-46d5-82e3-84aa15e38758` |
| Agent | `vigia-case-analyst` |
| Started | 2026-07-10T17:52:42.126210+00:00 |
| Closed | 2026-07-10T17:57:27.369687+00:00 |
| Quality | MINIMAL (1/3 observation groups) |
| Confidence | 3/5 (submitted 18/25 — capped by diversity ceiling) |
| Chain hash | `679de113be85a6db5ad7464cfa70c0bf9e00a70bb753957ae4b1d0fda7052a69` |
| Chain integrity | true |
| Cronos version | 0.1.0 |

---

## Objective

VIGIA-CAN-017: Emotional trojan phishing PDF — Carnegie emotional manipulation, Grice violations

---

## Step-by-step trace

### 1. Hypothesis registered: `H1_emotional_phishing` (2026-07-10T17:52:57.556773+00:00)
PDF exploits emotional urgency (hospitalized child narrative) to bypass victim's critical reasoning and obtain credential or malware execution.

### 2. Hypothesis registered: `H2_legitimate_email_error` (2026-07-10T17:56:09.054349+00:00)
SPF/DKIM failure is a common mail server misconfiguration. donaciones.pdf is a benign condolence PDF. Juan Pérez may exist under a variant name in a different system. 12-host connection to family-support.org could be legitimate bereavement fund site. Prior_trust 0.30 on email artifact makes H2 technically survivable.

### 3. Evidence — refutes `H2_legitimate_email_error` (2026-07-10T17:56:42.655672+00:00) *(negation detected)*
Juan Pérez verified NOT FOUND in personnel database. Real HR department confirmed they did NOT send the condolence email. donaciones.pdf contains active JavaScript exploiting CVE-2023-21608 to exfiltrate session_id, auth_token, csrf cookies to family-support[.]org. 12 internal hosts connected to that domain within 30 minutes of PDF mass-open.

### 4. Evidence — supports `H1_spear_phishing_operation` (2026-07-10T17:57:07.035559+00:00)
Acquisition chain insufficient for MALICE under Daubert: prior_trust 0.30 for email artifact (a099_01), prior_trust 0.35 for personnel DB check (a099_04). Placeholder provenance hashes (sha256:a099mail01, sha256:a099pdf02) would not survive cross-examination. Behavioral pattern confirms H1 but evidentiary standard caps at SUSPICION.

### 5. Decision sealed (2026-07-10T17:57:27.369687+00:00)
SUSPICION 72/100 — Spear-phishing behavioral pattern confirmed (fake HR, non-existent Juan Pérez, CVE-2023-21608 PDF, 12-host C2 callback). H2 refuted at behavioral level. Acquisition chain (prior_trust 0.30-0.35, placeholder hashes) prevents Daubert-compliant MALICE. Evidentiary cap: SUSPICION.

---

## Hypotheses summary

| Label | Status | Outcome |
|-------|--------|---------|
| `H1_emotional_phishing` | Active (confirmed behaviorally) | CVE-2023-21608 PDF + fake HR + 12-host C2 callback confirm spear-phishing; acquisition chain prevents MALICE |
| `H2_legitimate_email_error` | Discarded (refuted behaviorally) | Juan Pérez not found; HR did not send email; CVE exploit in PDF; refuted at behavioral level |

---

## Decision

SUSPICION 72/100 — Spear-phishing behavioral pattern confirmed (fake HR, non-existent Juan Pérez, CVE-2023-21608 PDF, 12-host C2 callback). H2 refuted at behavioral level. Acquisition chain (prior_trust 0.30-0.35, placeholder hashes) prevents Daubert-compliant MALICE. Evidentiary cap: SUSPICION.

---

## Quality metrics

| Metric | Value |
|--------|-------|
| Quality tier | MINIMAL |
| Observational diversity | 1/3 |
| Confidence submitted | 18/25 |
| Confidence stored | 3/5 — capped by diversity ceiling |

Confidence ceiling: only 1 of 3 observation groups covered. Submitted confidence 18/25 capped at 3/5.

---

## Chain of custody

```
entry_hash : 679de113be85a6db5ad7464cfa70c0bf9e00a70bb753957ae4b1d0fda7052a69
chain_ok   : true
```
