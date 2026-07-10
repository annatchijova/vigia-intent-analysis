# Cronos Audit Trail — VIGIA-FN-002
<!-- trace_id: 5988aedf-eed8-467e-a1e8-bcfb7f01dfe4 -->

| Field | Value |
|-------|-------|
| Trace ID | `5988aedf-eed8-467e-a1e8-bcfb7f01dfe4` |
| Agent | `vigia-claude-sonnet-4-6` |
| Started | 2026-07-10T17:59:09.010575+00:00 |
| Closed | 2026-07-10T18:08:09.797470+00:00 |
| Quality | MINIMAL (1/3 observation groups) |
| Confidence | 3/5 (submitted 19/25 — capped by diversity ceiling) |
| Chain hash | `e401fca2cb9f3f91917e413bfe3a644fe5e30a5eb28deac853f59142476798fc` |
| Chain integrity | true |
| Cronos version | 0.1.0 |

---

## Objective

VIGIA-FN-002: Classify LOTL exfiltration — Veeam Agent backup with no change ticket, 100GB to unregistered IP. Living-off-the-land technique. Verdict: MALICE.

---

## Step-by-step trace

### 1. Hypothesis registered: `H1_lotl_veeam_exfil` (2026-07-10T18:01:58.678634+00:00)
Veeam Agent invoked for 100GB data transfer to unregistered IP with no ITSM change ticket. Living-off-the-land technique: legitimate backup tool weaponized for exfiltration. No change management record means no authorized maintenance window — LOTL signature is the absence of authorization documentation for a consequential data movement operation.

### 2. Hypothesis registered: `H2_emergency_backup_no_ticket` (2026-07-10T18:03:49.860296+00:00)
Veeam Agent used for emergency data backup or disaster recovery operation where ITSM ticket creation was bypassed due to urgency. The destination IP is a legitimate backup target that was not yet registered in CMDB. Ticket created retroactively or process was informally authorized.

### 3. Evidence — supports `H1_lotl_veeam_exfil` (2026-07-10T18:05:50.588024+00:00) *(negation detected)*
No ITSM change ticket for Veeam Agent 100GB transfer. Destination IP not in CMDB as registered backup target. Legitimate emergency operations in this environment require at minimum informal approval — even emergency tickets are created retroactively in this org's ITIL process. LOTL technique: Veeam Agent is authorized software repurposed for unauthorized data movement. H2 (emergency backup) weakened by absence of any authorization trail.

### 4. Decision sealed (2026-07-10T18:08:09.797470+00:00)
MALICE 76/100 — Veeam Agent LOTL: 100GB to unregistered IP, no ITSM change ticket. H2 (emergency backup) weakened by absence of any authorization trail. Living-off-the-land technique: legitimate backup tool weaponized for unauthorized data movement. T1048 + T1567.

---

## Hypotheses summary

| Label | Status | Outcome |
|-------|--------|---------|
| `H1_lotl_veeam_exfil` | Active (supported) | No change ticket, unregistered destination IP, no authorization trail; LOTL pattern confirmed |
| `H2_emergency_backup_no_ticket` | Active (weakened) | Emergency bypass possible but org requires retroactive tickets; absence of any authorization trail weakens H2 |

---

## Decision

MALICE 76/100 — Veeam Agent LOTL: 100GB to unregistered IP, no ITSM change ticket. H2 (emergency backup) weakened by absence of any authorization trail. Living-off-the-land technique: legitimate backup tool weaponized for unauthorized data movement. T1048 + T1567.

---

## Quality metrics

| Metric | Value |
|--------|-------|
| Quality tier | MINIMAL |
| Observational diversity | 1/3 |
| Confidence submitted | 19/25 |
| Confidence stored | 3/5 — capped by diversity ceiling |

Confidence ceiling: only 1 of 3 observation groups covered. Submitted confidence 19/25 capped at 3/5.

---

## Chain of custody

```
entry_hash : e401fca2cb9f3f91917e413bfe3a644fe5e30a5eb28deac853f59142476798fc
chain_ok   : true
```
