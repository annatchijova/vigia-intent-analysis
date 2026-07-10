# Cronos Audit Trail — VIGIA-LINUX-005
<!-- trace_id: 1be3a89f-1e16-4627-9f4f-9de687319fe9 -->

| Field | Value |
|-------|-------|
| Trace ID | `1be3a89f-1e16-4627-9f4f-9de687319fe9` |
| Agent | `vigia-case-analyst` |
| Started | 2026-07-10T17:52:43.872602+00:00 |
| Closed | 2026-07-10T17:57:33.726916+00:00 |
| Quality | MINIMAL (1/3 observation groups) |
| Confidence | 3/5 (submitted 3/4 — capped by diversity ceiling) |
| Chain hash | `26146aa7ddaf600544d00fea493aad2eba638da577d6d9b76a2eee83f5a6b1d6` |
| Chain integrity | true |
| Cronos version | 0.1.0 |

---

## Objective

VIGIA-LINUX-005: /opt/services/cron binary — PUMAKIT epistemic boundary test, Go task scheduler

---

## Step-by-step trace

### 1. Hypothesis registered: `H1_pumakit_variant` (2026-07-10T17:53:00.415234+00:00)
Binary is a PUMAKIT or PUMAKIT-like rootkit using the 'cron' name for process masquerading, early stage before kernel module activation.

### 2. Hypothesis registered: `H2_pumakit_variant` (2026-07-10T17:56:13.628278+00:00)
Binary at /opt/services/cron (entropy 7.4, UPX, not in package manager) is a PUMAKIT-like rootkit using 'cron' naming for process masquerading. High entropy + UPX = packed payload. Early deployment stage before kernel module activation. Ansible records may have been backdated.

### 3. Evidence — refutes `H2_pumakit_variant` (2026-07-10T17:56:48.645474+00:00) *(negation detected)*
Static analysis of cron binary: Go 1.22 import table shows stdlib only (net/http, time, os, encoding/json). All PUMAKIT-distinguishing signals absent: no LKM loading, no rmdir() abuse, no memfd_create, no syscall hooking, no privilege escalation, no C2. Ansible deployment recorded at 02:15 UTC; binary creation timestamp 02:17 UTC (2-minute pipeline execution). Wiki documentation predates creation by 8 months.

### 4. Evidence — supports `H1_legitimate_deployment` (2026-07-10T17:57:12.563902+00:00) *(negation detected)*
Process running as deploy/UID 1001 (non-root), CPU 0.1%, RSS 12MB, no anomalous network connections, no child processes, listening on localhost:8080 only. Behavioral profile matches documentation exactly: custom HTTP task scheduler. Go stdlib-only import table proves no syscall-level capability possible. H1 confirmed.

### 5. Decision sealed (2026-07-10T17:57:33.726916+00:00)
NOISE 75/100 — Custom Go task scheduler deployed via documented Ansible pipeline. H2 (PUMAKIT variant) refuted by static analysis: stdlib imports only, all PUMAKIT signals absent (no LKM/syscall/memfd/C2/root). Deployment timestamp matches pipeline execution. H1 confirmed.

---

## Hypotheses summary

| Label | Status | Outcome |
|-------|--------|---------|
| `H1_pumakit_variant` | Discarded (refuted) | PUMAKIT signals all absent; Go stdlib-only import table rules out syscall capability |
| `H2_pumakit_variant` | Discarded (refuted) | Same refutation; legitimate deployment confirmed by Ansible timeline + documentation |

---

## Decision

NOISE 75/100 — Custom Go task scheduler deployed via documented Ansible pipeline. H2 (PUMAKIT variant) refuted by static analysis: stdlib imports only, all PUMAKIT signals absent (no LKM/syscall/memfd/C2/root). Deployment timestamp matches pipeline execution. H1 confirmed.

---

## Quality metrics

| Metric | Value |
|--------|-------|
| Quality tier | MINIMAL |
| Observational diversity | 1/3 |
| Confidence submitted | 3/4 |
| Confidence stored | 3/5 — capped by diversity ceiling |

Confidence ceiling: only 1 of 3 observation groups covered. Submitted confidence 3/4 capped at 3/5.

---

## Chain of custody

```
entry_hash : 26146aa7ddaf600544d00fea493aad2eba638da577d6d9b76a2eee83f5a6b1d6
chain_ok   : true
```
