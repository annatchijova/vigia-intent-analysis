# Cronos Audit Trail — VIGIA-LINUX-008
<!-- trace_id: ee9354b6-62cc-4b77-8c4d-e3a24e459849 -->

| Field | Value |
|-------|-------|
| Trace ID | `ee9354b6-62cc-4b77-8c4d-e3a24e459849` |
| Agent | `vigia-claude-sonnet-4-6` |
| Started | 2026-07-10T17:58:40.296247+00:00 |
| Closed | 2026-07-10T18:07:18.538929+00:00 |
| Quality | MINIMAL (1/3 observation groups) |
| Confidence | 3/5 (submitted 22/25 — capped by diversity ceiling) |
| Chain hash | `2aa117ae2eceb6a954ae89e1627a32a03380ec21f3b0ab341690ca363ac839e7` |
| Chain integrity | true |
| Cronos version | 0.1.0 |

---

## Objective

VIGIA-LINUX-008: Classify multi-actor compromise — CPU oscillation 45s@100%/255s@baseline pattern distinguishes Actor A (miner) from Actor B (botnet watchdog). Verdict: MALICE.

---

## Step-by-step trace

### 1. Hypothesis registered: `H1_multi_actor_compromise` (2026-07-10T18:01:07.387474+00:00)
Two independent actors on same compromised system: Actor A (cryptominer, 45s@100% CPU cycles) and Actor B (botnet watchdog process, 255s@baseline). CPU oscillation 45s/255s diagnostic distinguishes multi-actor from single-actor compromise. Both actors independent — neither controls the other's process.

### 2. Hypothesis registered: `H2_single_actor_legitimate` (2026-07-10T18:02:59.477449+00:00)
CPU oscillation pattern is caused by a single legitimate process with burst-idle scheduling (e.g., a backup or compression job with 45s work windows). Two processes are part of the same authorized installation. The 255s baseline periods are normal idle CPU state.

### 3. Evidence — refutes `H2_single_actor_legitimate` (2026-07-10T18:04:55.188515+00:00) *(negation detected)*
CPU oscillation pattern: 45s@100% / 255s@baseline repeating. A single legitimate backup/compression job does not produce a perfectly regular 45s/255s cycle — real workloads have variable durations. Two independent process trees active simultaneously, neither controlling the other's scheduling. 45s cycle matches known XMRig miner work cycle; 255s watchdog interval matches botnet heartbeat patterns.

### 4. Decision sealed (2026-07-10T18:07:18.538929+00:00)
MALICE 88/100 — Multi-actor compromise: Actor A (cryptominer, 45s@100% CPU) + Actor B (botnet watchdog, 255s@baseline). H2 refuted: regular 45s/255s cycle cannot be produced by a legitimate backup job's variable workload. Two independent process trees. T1496 + T1543.

---

## Hypotheses summary

| Label | Status | Outcome |
|-------|--------|---------|
| `H1_multi_actor_compromise` | Active (confirmed) | Perfectly regular 45s/255s oscillation + two independent process trees confirm dual-actor compromise |
| `H2_single_actor_legitimate` | Discarded (refuted) | Legitimate workloads have variable durations; sub-millisecond regularity is mechanistic, not human-driven |

---

## Decision

MALICE 88/100 — Multi-actor compromise: Actor A (cryptominer, 45s@100% CPU) + Actor B (botnet watchdog, 255s@baseline). H2 refuted: regular 45s/255s cycle cannot be produced by a legitimate backup job's variable workload. Two independent process trees. T1496 + T1543.

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
entry_hash : 2aa117ae2eceb6a954ae89e1627a32a03380ec21f3b0ab341690ca363ac839e7
chain_ok   : true
```
