# Cronos Audit Trail — VIGIA-CAN-032
<!-- trace_id: 66bf3de8-ed6f-4ba6-865b-3b221dad45ea -->

| Field | Value |
|-------|-------|
| Trace ID | `66bf3de8-ed6f-4ba6-865b-3b221dad45ea` |
| Agent | `vigia-case-analyst` |
| Started | 2026-07-10T17:52:42.954316+00:00 |
| Closed | 2026-07-10T17:57:30.798385+00:00 |
| Quality | MINIMAL (1/3 observation groups) |
| Confidence | 3/5 (submitted 17/25 — capped by diversity ceiling) |
| Chain hash | `2fd1d4a66ca84ad0ca4846b374d2d2edafe1af676c01927aa48fbaf8a1c5b82f` |
| Chain integrity | true |
| Cronos version | 0.1.0 |

---

## Objective

VIGIA-CAN-032: Distractor white noise flood + DB exfiltration — COGNITIVE_DOS pattern

---

## Step-by-step trace

### 1. Hypothesis registered: `H1_cognitive_dos_cover` (2026-07-10T17:52:59.160219+00:00)
2048 identical low-entropy packets are a deliberate distractor flood to mask simultaneous DB exfiltration from analyst attention.

### 2. Hypothesis registered: `H2_coincidence_legitimate_backup` (2026-07-10T17:56:12.555560+00:00)
finance_user's 7z compression of Customer_DB.mdf is a legitimate scheduled weekly/monthly backup job. The brute-force from 847 RU/CN IPs is unrelated automated internet scanning, not a coordinated distraction. The 847MB HTTPS is authorized cloud backup traffic. Timing correlation is coincidence. Prior_trust 0.25 on network artifact makes H2 viable.

### 3. Evidence — supports `H1_noise_distraction_exfil` (2026-07-10T17:56:45.718132+00:00)
7z.exe PID 3184 (prior_trust 0.95) began compressing Customer_DB.mdf at 15:05Z — exactly 5 minutes after 5,000 Event 4625 brute-force flood started at 15:00Z generating 47 SIEM High Priority alerts. 50MB chunk strategy is consistent with staged exfiltration. Timing correlation supports RED_HERRING CAIE fracture (severity 0.95).

### 4. Evidence — supports `H2_coincidence_legitimate_backup` (2026-07-10T17:57:09.723468+00:00) *(negation detected)*
Network exfiltration artifact (847MB HTTPS to 198.51.100.77) carries prior_trust 0.25 — insufficient for MALICE. Backup legitimacy of finance_user 7z operation not investigated. H2 (scheduled backup coincidence) cannot be excluded without change management records. Brute-force prior_trust 0.35 also weak.

### 5. Decision sealed (2026-07-10T17:57:30.798385+00:00)
SUSPICION 68/100 — RED_HERRING CAIE fracture: 5k brute-force flood (15:00Z) followed by 7z compression of Customer_DB (15:05Z) and 847MB HTTPS exfiltration during SOC alert window. H2 not excluded (backup legitimacy uninvestigated). Network artifact prior_trust 0.25 insufficient for MALICE.

---

## Hypotheses summary

| Label | Status | Outcome |
|-------|--------|---------|
| `H1_cognitive_dos_cover` | Active (supported) | RED_HERRING CAIE fracture: timing correlation between flood and DB compression supports deliberate distraction |
| `H2_coincidence_legitimate_backup` | Active (not refuted) | Acquisition chain weakness (prior_trust 0.25) and uninvestigated backup legitimacy prevent exclusion |

---

## Decision

SUSPICION 68/100 — RED_HERRING CAIE fracture: 5k brute-force flood (15:00Z) followed by 7z compression of Customer_DB (15:05Z) and 847MB HTTPS exfiltration during SOC alert window. H2 not excluded (backup legitimacy uninvestigated). Network artifact prior_trust 0.25 insufficient for MALICE.

---

## Quality metrics

| Metric | Value |
|--------|-------|
| Quality tier | MINIMAL |
| Observational diversity | 1/3 |
| Confidence submitted | 17/25 |
| Confidence stored | 3/5 — capped by diversity ceiling |

Confidence ceiling: only 1 of 3 observation groups covered. Submitted confidence 17/25 capped at 3/5.

---

## Chain of custody

```
entry_hash : 2fd1d4a66ca84ad0ca4846b374d2d2edafe1af676c01927aa48fbaf8a1c5b82f
chain_ok   : true
```
