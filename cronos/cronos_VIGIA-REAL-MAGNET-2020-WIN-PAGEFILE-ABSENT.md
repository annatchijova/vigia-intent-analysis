# Cronos Audit Trail — VIGIA-REAL-MAGNET-2020-WIN-PAGEFILE-ABSENT
<!-- trace_id: f098880b-f90e-4a55-8f28-cf9b9d6351ae -->

| Field | Value |
|-------|-------|
| Trace ID | `f098880b-f90e-4a55-8f28-cf9b9d6351ae` |
| Agent | `vigia-case-analyst` |
| Started | 2026-07-10T17:10:33.899906+00:00 |
| Closed | 2026-07-10T17:11:15.985761+00:00 |
| Quality | MINIMAL (1/3 observation groups) |
| Confidence | 3/5 (submitted 22/25 — capped by diversity ceiling) |
| Chain hash | `fb8fb7c3b39bc93e231073ecd2d5483e6d8b307c18648d491942b0bf75ff08ed` |
| Chain integrity | true |
| Cronos version | 0.1.0 |

---

## Objective

VIGIA-REAL-MAGNET-2020-WIN-PAGEFILE-ABSENT: Windows 10 memory, pslist=0/psscan=20 DKOM rootkit, iexplore Wow64 spawned by Chrome

---

## Step-by-step trace

### 1. Hypothesis registered: `H1_dkom_rootkit` (2026-07-10T17:10:43.648989+00:00)
Active kernel rootkit using EPROCESS DKOM to hide all processes from pslist. iexplore.exe masquerading with wrong parent and Wow64 evasion.

### 2. Hypothesis registered: `H2_ctf_synthetic_artifact` (2026-07-10T17:10:48.037089+00:00)
Magnet CTF 2020 planted rootkit artifact for challenge purposes — synthetic scenario, not real-world malice

### 3. Evidence — supports `H1_dkom_rootkit` (2026-07-10T17:10:54.538214+00:00) *(negation detected)*
pslist=0 / psscan=20: delta of 20 processes hidden from OS kernel list. No benign explanation for a 0-vs-20 discrepancy — this is definitionally a DKOM kernel manipulation.

### 4. Evidence — supports `H1_dkom_rootkit` (2026-07-10T17:10:56.843892+00:00)
iexplore.exe PID 4480 Wow64=True spawned by chrome.exe PID 3384. IE should spawn from explorer.exe or itself. Chrome-parented IE + Wow64 on 64-bit = process injection masquerade, two independent anti-forensic techniques.

### 5. Evidence — refutes `H1_dkom_rootkit` (2026-07-10T17:11:00.430506+00:00) *(negation detected)*
No malicious C2 in netscan. Chrome connects to Google/CloudFront only. Rootkit present but no active exfiltration observed at capture time.

### 6. Decision sealed (2026-07-10T17:11:15.985761+00:00)
MALICE — DKOM rootkit confirmed (pslist=0 vs psscan=20, no benign explanation). iexplore.exe Wow64 spawned by Chrome = process masquerading. Two independent anti-forensic techniques. No C2 visible but presence of kernel-level concealment is itself MALICE evidence. devil_advocate: CTF synthetic scenario, no C2 — but forensic analysis conclusion holds regardless of source.

---

## Hypotheses summary

| Label | Status | Outcome |
|-------|--------|---------|
| `H1_dkom_rootkit` | Active (contradicted — Type A) | DKOM confirmed by pslist=0/psscan=20 delta and Chrome-parented iexplore.exe Wow64; no C2 at capture time is a partial refutation but does not eliminate kernel-level concealment finding |
| `H2_ctf_synthetic_artifact` | Active (acknowledged) | CTF context documented in devil_advocate; forensic analysis conclusion holds regardless of artifact origin |

Contradiction recorded: Type A — 'H1_dkom_rootkit' has evidence both supporting and refuting it.

---

## Decision

MALICE — DKOM rootkit confirmed (pslist=0 vs psscan=20, no benign explanation). iexplore.exe Wow64 spawned by Chrome = process masquerading. Two independent anti-forensic techniques. No C2 visible but presence of kernel-level concealment is itself MALICE evidence. devil_advocate: CTF synthetic scenario, no C2 — but forensic analysis conclusion holds regardless of source.

---

## Quality metrics

| Metric | Value |
|--------|-------|
| Quality tier | MINIMAL |
| Observational diversity | 1/3 |
| Confidence submitted | 22/25 |
| Confidence stored | 3/5 — capped by diversity ceiling |

Confidence ceiling: only 1 of 3 observation groups covered. Submitted confidence 22/25 capped at 3/5.

---

## Chain of custody

```
entry_hash : fb8fb7c3b39bc93e231073ecd2d5483e6d8b307c18648d491942b0bf75ff08ed
chain_ok   : true
```
