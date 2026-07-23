# Cronos Audit Trail — OWL-NEXUS5 case resolution and seal (VIGIA, Claude Fable)
<!-- trace_id: 4b0cace0-44d7-458c-8f8d-8cf3880c8450 -->

| Field | Value |
|-------|-------|
| Trace ID | `4b0cace0-44d7-458c-8f8d-8cf3880c8450` |
| Agent | `vigia-claude-fable` |
| Started | 2026-07-23T02:18:56 UTC |
| Closed | 2026-07-23T02:19 UTC (approx) |
| Quality | PARTIAL (observational diversity 2/3) |
| Confidence | 39/50 stored (submitted 39/50 — no capping) |
| Chain hash | `fe0254d79f49b6abcd0ba427173bd0fd93034dc190902e7f966e3aafab592d3a` |
| Chain integrity | OK (chain_ok=true at close) |
| Cronos version | chain v2 (SHA-256 tamper-evident) |

---

## Objective

Resolve and seal case VIGIA-OWL-2019-NEXUS5 (Project OWL illegal owl trade,
subject Sarah McAvoy, LGE Nexus 5 Android image) through the deterministic EBS
pipeline so the 30 GB raw can be freed; produce report, sealed bundle and amicus
in vigia/results with _claude_fable suffix.

---

## Step-by-step trace

### 1. Trace opened — cronos_open_trace (2026-07-23T02:18:56 UTC)

Trace opened for agent `vigia-claude-fable`, case VIGIA-OWL-2019-NEXUS5.

### 2-3. Hypotheses registered — cronos_add_hypothesis

`deliberate_owl_trade` (Sarah McAvoy deliberately participated in illegal owl
trade via Musical.ly with seller layster82, with concealment) and
`benign_pet_interest` (lawful curiosity, generic privacy hygiene).

### 4. Tool call — sha256 + VigiaPipeline.run_full (deterministic EBS seal)

Raw SHA-256 763e7acd...b6a5de. 22 artifacts -> 22 signals. EBS decision REJECT,
posterior 1.0, LR ~4.85e8 (ENFSI 'very strong'). CAIE structural NOISE (0.0586,
0 fractures). decision_hash 1fc52828... stable across 3 runs; verify_ebs_v1 PASS
Level 2 (10/11 checks). Only bundle_hash varies (random bundle_id + timestamp by
design; not a determinism defect).

### 5. Evidence — concealment fractures (supports deliberate_owl_trade)

Two CAIE fractures: (1) compartmentalization — owl trade only on Musical.ly
behind AppLock, Skype kept clean; (2) anti-forensic awareness — AppLock installed
to protect messaging apps, prior seller email thread deleted. Refutation: benign
pet-interest cannot explain compartmentalization + app shielding + correspondence
deletion. Completion NOT proven — no payment/delivery record on this device.

### 6. Discard — benign_pet_interest (refuted for intent, retained for completion)

Refuted for the intent question; retained only as the unrefuted explanation for
non-completion (no paid transaction proven on this single device).

### 7. Trace closed — cronos_close_trace (2026-07-23T02:19 UTC)

Decision SUSPICION recorded (doctrine cap over a 'very strong' EBS signal),
confidence 39/50, quality PARTIAL, diversity 2/3, no contradictions, chain_ok=true.

---

## Hypotheses summary

| Label | Status | Outcome |
|-------|--------|---------|
| `deliberate_owl_trade` | Active (accepted) | Supported by artifact constellation + two concealment fractures; intent confirmed on-device. |
| `benign_pet_interest` | Discarded (partial) | Refuted for intent (compartmentalization + email deletion); retained as explanation for non-completion. |

---

## Decision

**Case VIGIA-OWL-2019-NEXUS5: emitted verdict SUSPICION.** EBS pipeline rates
intentionality very strong (LR ~4.85e8, REJECT, posterior 1.0); doctrine
L-051/§9.4-LIM caps at SUSPICION (single device/channel, no independent
triangulation; purchase confirmation expected on the un-imaged HP companion).
CAIE structural NOISE (0.0586). Completed transaction NOT proven. Deterministic
seal reproducible (decision_hash `1fc5282832ebba458857717f938fa8b95de918edf45c3d0802dc71ce225264e3`,
verify_ebs_v1 PASS Level 2). Trio sealed in vigia/results with _claude_fable
suffix. Recommend imaging the HP companion to resolve completion.

---

## Quality metrics

| Metric | Value |
|--------|-------|
| Quality tier | PARTIAL |
| Observational diversity | 2/3 groups |
| Confidence submitted | 39/50 (78%) |
| Confidence stored | 39/50 (78%) — no ceiling applied |

**Confidence warnings:** none.

**Contradictions flagged by Cronos:** none (CAIE-vs-EBS divergence disclosed in the report/amicus, not a chain contradiction).

---

## Chain of custody

```
entry_hash : fe0254d79f49b6abcd0ba427173bd0fd93034dc190902e7f966e3aafab592d3a
chain_ok   : true
```
