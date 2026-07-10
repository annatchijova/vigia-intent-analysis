# Cronos Audit Trail — VIGIA-LINUX-006
<!-- trace_id: 5ecb100c-ab75-498f-bc70-b1cbb02c24f9 -->

| Field | Value |
|-------|-------|
| Trace ID | `5ecb100c-ab75-498f-bc70-b1cbb02c24f9` |
| Agent | `vigia-claude-sonnet-4-6` |
| Started | 2026-07-10T17:58:38.826951+00:00 |
| Closed | 2026-07-10T18:07:15.127516+00:00 |
| Quality | MINIMAL (1/3 observation groups) |
| Confidence | 3/5 (submitted 9/10 — capped by diversity ceiling) |
| Chain hash | `20c6f38c4aa36062b4d620f0ed5dc46a100b41bbb16899314230b481d41b11d2` |
| Chain integrity | true |
| Cronos version | 0.1.0 |

---

## Objective

VIGIA-LINUX-006: Classify cryptominer deployment — /var/tmp/systemd-logind masquerade, Monero pool 62.60.246[.]210:443, 14-day crontab persistence. Verdict: MALICE.

---

## Step-by-step trace

### 1. Hypothesis registered: `H1_cryptominer_masquerade` (2026-07-10T18:01:04.199048+00:00)
Cryptominer deployed as /var/tmp/systemd-logind (masquerading as systemd service). Connects to Monero pool at 62.60.246[.]210:443 (TLS over HTTPS port). 14-day persistence via crontab @reboot. Active anti-forensics: process name chosen to blend with legitimate systemd-logind in process listings.

### 2. Hypothesis registered: `H2_legitimate_system_process` (2026-07-10T18:02:56.006092+00:00)
/var/tmp/systemd-logind is a legitimate system process variant or custom deployment script. The Monero pool connection is a false positive (CDN/legitimate service using same IP). crontab @reboot entry is for a legitimate service autostart.

### 3. Evidence — supports `H1_cryptominer_masquerade` (2026-07-10T18:04:51.452841+00:00) *(negation detected)*
/var/tmp/systemd-logind: binary resides in /var/tmp (not /lib/systemd/ or /usr/lib/systemd/). Legitimate systemd-logind is at /lib/systemd/systemd-logind — path mismatch is the masquerade indicator. Active connection to 62.60.246[.]210:443 confirmed as Monero mining pool. crontab @reboot entry for 14-day persistence. PARENT_ANOMALY: process spawned outside normal systemd service tree.

### 4. Decision sealed (2026-07-10T18:07:15.127516+00:00)
MALICE 90/100 — Cryptominer masquerading as systemd-logind at /var/tmp (wrong path). Active Monero pool connection 62.60.246[.]210:443. 14-day @reboot crontab persistence. PARENT_ANOMALY confirmed. H2 refuted: /var/tmp is not a valid systemd binary path; Monero pool connection is not legitimate system traffic. T1036 + T1496.

---

## Hypotheses summary

| Label | Status | Outcome |
|-------|--------|---------|
| `H1_cryptominer_masquerade` | Active (confirmed) | Path mismatch (/var/tmp vs /lib/systemd/), confirmed Monero pool, @reboot persistence, PARENT_ANOMALY |
| `H2_legitimate_system_process` | Discarded (refuted) | /var/tmp is not a valid systemd binary path; Monero pool confirmed by network telemetry |

---

## Decision

MALICE 90/100 — Cryptominer masquerading as systemd-logind at /var/tmp (wrong path). Active Monero pool connection 62.60.246[.]210:443. 14-day @reboot crontab persistence. PARENT_ANOMALY confirmed. H2 refuted: /var/tmp is not a valid systemd binary path; Monero pool connection is not legitimate system traffic. T1036 + T1496.

---

## Quality metrics

| Metric | Value |
|--------|-------|
| Quality tier | MINIMAL |
| Observational diversity | 1/3 |
| Confidence submitted | 9/10 |
| Confidence stored | 3/5 — capped by diversity ceiling |

Confidence ceiling: only 1 of 3 observation groups covered. Submitted confidence 9/10 capped at 3/5.

---

## Chain of custody

```
entry_hash : 20c6f38c4aa36062b4d620f0ed5dc46a100b41bbb16899314230b481d41b11d2
chain_ok   : true
```
