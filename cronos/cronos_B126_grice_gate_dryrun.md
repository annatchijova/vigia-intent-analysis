# Cronos Audit Trail — B-126 Grice Override Gate Dry-Run and FP Audit
<!-- trace_id: 3b11e32e-9f39-439a-a819-6a20c8ca35c6 -->
<!-- date: 2026-07-14 -->
<!-- parent_trace: 6b81f266-a8e7-4c59-a04e-fff20e9e9e2f (KIWI-006/007 Mode 2 re-run) -->

| Field | Value |
|-------|-------|
| Trace ID | `3b11e32e-9f39-439a-a819-6a20c8ca35c6` |
| Agent | `vigia-mode2-claude-opus` |
| Started | 2026-07-14T15:56:00 UTC |
| Closed | 2026-07-14T15:57:02 UTC |
| Quality | MINIMAL |
| Confidence | 3/5 (submitted 39/50, capped by diversity ceiling) |
| Chain hash | `55ae6a05cc5fca30d1097f063947422e374d9420e1ac1176bead645a3629be7a` |
| Chain integrity | OK |

---

## Context

Following Mode 2 re-run of KIWI-006/007 (trace `6b81f266`), a Grice
override gate was proposed to fix the CAIE-vs-Grice architectural
tension for pure testimony evidence. Corpus scan identified 16
testimony-only cases, of which 5 have current motor verdict NOISE.
The proposed naive gate would affect all 5:

| Case | Expected | Current | With Gate | Impact |
|------|----------|---------|-----------|--------|
| KIWI-006 | SUSPICION | NOISE | SUSPICION | Fix |
| KIWI-007 | SUSPICION | NOISE | SUSPICION | Fix |
| BEN-003 | NOISE | NOISE | SUSPICION | **Regression** |
| BEN-010 | NOISE | NOISE | SUSPICION | **Regression** |
| BREAK-002 | NOISE | NOISE | SUSPICION | **Regression** |

---

## Per-Case Peircean Audit

### BEN-003 — The Real Disaster (Junior DB Delete)

**Evidence:** Junior dev DELETE without WHERE, public Slack panic,
immediate recovery_procedure, HR confirms 1st month + supervisor
permissions error.

**Refutation result:** Malicious hypothesis does NOT survive. Public
admission + panic + recovery is structurally incompatible with sabotage.

**Grice fires because:** RELATION detector sees short fragments as
evasion. Does not access semantic_role=exculpatory or prior_trust=0.70.

**Classification: (a) GENUINE FALSE POSITIVE. NOISE is correct.**

### BEN-010 — The Boss with a Real Deadline (CEO Urgent Email)

**Evidence:** CEO URGENT email. DKIM PASS, SPF PASS. Calendar event
created 6 weeks prior. Week-long email prep thread.

**Refutation result:** BEC hypothesis does NOT survive. Triple
corroboration (DKIM, calendar, thread) eliminates it.

**Grice fires because:** Same near-constant RELATION pattern.

**Classification: (a) GENUINE FALSE POSITIVE. NOISE is correct.**

### BREAK-002 — Valid Benign (Authorized Pentest)

**Evidence:** nmap/mimikatz/exfil in bash_history. Authorized pentest
ticket (semantic_role=exculpatory, prior_trust=0.85).

**Refutation result:** Fabrication hypothesis does NOT survive. No
fabrication signals detected.

**Classification: (a) GENUINE FALSE POSITIVE. NOISE is correct.**

---

## Root Cause Analysis

The Grice RELATION/TACTICAL_EVASION detector fires identically
(weight=30, P(deception)=0.30, verdict=SUSPICION) on ALL 5 tested
testimony cases. It is a near-constant with zero discriminating power.

### Why it cannot distinguish TP from FP

It operates on raw text fragments without access to:
- `semantic_role` field (exculpatory vs incriminatory)
- `prior_trust` values (0.10 vs 0.85)
- Internal corroboration signals
- `write_blocker_used` status
- Artifact-level contradiction detection

---

## Structural Discriminators for Refined Gate

| Feature | KIWI (TP) | BEN/BREAK (FP) |
|---------|-----------|-----------------|
| Exculpatory artifacts | None | Present |
| max(prior_trust) | 0.10-0.15 | 0.70-0.85 |
| write_blocker_used | false | true |
| Internal corroboration | None (contradictions) | Present |
| source_tool | manual_forensic_review | legacy_converter |

---

## Conclusion

The naive gate is not safe (net -1 accuracy). A refined gate using
the discriminators above is plausible but requires implementation in
`vigia_scorer.py` and a full 199-case corpus dry-run before wiring.
Documented as L-058 / B-126 in KNOWN_LIMITATIONS.md.
