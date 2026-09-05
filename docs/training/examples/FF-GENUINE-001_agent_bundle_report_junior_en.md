# VIGÍA verdict, explained for a SOC analyst

| Field | Value |
| --- | --- |
| Case | `FF-GENUINE-001` |
| Bundle family | `agent_audit` |
| Source bundle | `FF-GENUINE-001_agent_bundle.json` |
| Source SHA-256 | `e4496808337b21c05185ac7e0cce1b89cf384a354bdf435f5c6a1d240e8e74dd` |
| Audience | junior SOC analyst |
| Report layout version | `1.0` |

> This document carries NO verdict authority. It presents a sealed result verbatim; it computed nothing, reconciled nothing and can be regenerated from the bundle bytes at any time. If this text and the bundle ever disagree, the bundle is right and this file is stale.

> Values quoted from the bundle appear exactly as sealed, including their original language, spelling and numeric form. That is the evidence, not a rendering defect.

Agent audit bundle: output of `python3 vigia_agent.py` (Mode 1). Carries `agent_verdict`, `audit_trail`, `pipeline_results` and a deterministic `narrative`. Numbers are exact Fractions.

## 1. The verdict

This is the sealed result, copied character by character from the bundle. Each line names the field it came from.

- `agent_verdict`: **MALICE**
- `pipeline_results.abduction.best_hypothesis`: **MALICIOUS_INTENT_DETECTED** (confidence: `19/20`)

`best_hypothesis` is the label of the winning abductive hypothesis, not a verdict. The verdict is `agent_verdict`.

## 2. What this verdict means

VIGÍA uses a five-rung scale. The rung says how much deliberate behavior the evidence supports; it does not say who did it or whether a law was broken.

| Verdict | Meaning | Evidence bar |
| --- | --- | --- |
| `NOISE` | Everything observed is explained by misconfiguration, software error or normal operations. | Single source is enough. |
| `SUSPICION` | A structural anomaly exists, but there is no evidence of deliberate concealment or coordination. | Single source plus a documented deviation from baseline. |
| `INTENT` | Deliberate decisions were made to produce this outcome. | Two independent sources and a passed refutation protocol. |
| `MALICE` **(This bundle)** | Active concealment of intent: the actor is hiding that they are hiding (log deletion, timestamp tampering, masquerading, false flags). | Two independent sources, refutation protocol, and a populated `devil_advocate`. |
| `ABSTAIN` | Not enough evidence to classify. The gap is documented as a limitation. | Explicit statement of what is missing. |

Mode 1 (`vigia_agent.py`) has no INTENT rung: borderline cases that would qualify as INTENT are capped at SUSPICION by the scoring pipeline (CLAUDE.md, Verdict Scale). An agent bundle reading SUSPICION can therefore be stronger than it looks; read the narrative.

## 3. What to do next

Generic SOC steps for this rung. They are not case-specific advice and they do not come from the bundle; adapt them to your runbook.

- Escalate now. Concealment means the actor expects to be looked for.
- Preserve everything, including logs the actor may have tried to delete.
- Containment decisions belong to incident response and management, not to this report.

## 4. What NOT to conclude

- MALICE describes a concealment pattern in the analyzed artifacts. It is not a legal finding, not an identification of a person, and not a statement about damage.
- No presentation, this one included, can add evidence that the bundle does not contain.

## 5. Findings, in plain language

Agent bundles do not carry per-finding verdicts. They record signals (one per analyzed artifact) and one abductive hypothesis. The sealed narrative below is the pipeline's own account.

| Artifact | Evidence type | Source tool | Confidence | z-score |
| --- | --- | --- | --- | --- |
| tech_real_001 | memory_process | list_processes | 19/20 | 209/250 |
| tech_real_002 | lsass_session | list_processes | 19/20 | 399/500 |
| cultural_planted_001 | cultural_marker | infer_intent | 3/10 | 27/100 |

Confidence and z-score are exact fractions, shown as numerator/denominator. They are not percentages.

Signals carry no verdict of their own; only the case does.

**Sealed narrative (verbatim)**

```text
=== VIGÍA FORENSIC AGENT — CASE FF-GENUINE-001 ===
Evidence: /home/labestiadevigia/vigia-repo/data/cases/FF-GENUINE-001.json
Evidence SHA-256: 3900f5762b64d74ac1a090a10f3ae0e50b9b071cfc50d122dbda6d3953a076d2
Analysis iterations: 1
Self-corrections applied: 0

--- MAIN HYPOTHESIS ---
Hypothesis: MALICIOUS_INTENT_DETECTED
Posterior confidence: 19/20
Conclusive: YES

--- PEIRCEAN NARRATIVE ---
[FIRSTNESS] 3 señal(es): 3 primaria(s) de ['infer_intent', 'list_processes'], 0 derivada(s)/no-analizada(s). Top z: Process hollowing in svchost.exe confirm=0.84, LSASS credential dumping detected (T1003=0.80, Suspiciously pristine Russian-language s=0.27.
[SECONDNESS] Ninguna señal primaria supera z>2 — sin desviación estructural contra baseline en esta iteración. CAIE (viva): 1 fractura(s) cross-artefacto contribuyeron al veredicto (boost +0.3825).
[THIRDNESS] Hipótesis: MALICIOUS_INTENT_DETECTED. Conclusiva: sí.

Razonamiento del motor abductivo:
A real compromise: process hollowing and LSASS credential dumping confirmed in memory (hard-to-fake structural evidence). On top of the real attack, the operator planted suspiciously pristine Russian-language strings whose profile contradicts the actual TTPs and OPSEC. This is what a real false flag looks like: the malicious event is PRESENT, and the attribution is engineered to misdirect. MALICE is correct here — and it belongs to the framer, not to any Russian-speaker.

--- TOP SIGNALS (top 5 by z-score) ---
  [Process hollowing in svchost.exe confirmed (T1055.012). Reflective DLL] z=0.836 conf=0.95 — 
  [LSASS credential dumping detected (T1003.001). Active compromise, not ] z=0.798 conf=0.95 — 
  [Suspiciously pristine Russian-language strings injected into the dropp] z=0.270 conf=0.30 — 

--- CAIE (Cross-Artifact Incongruence Engine — motor) ---
  Fractures: 1 | Malice boost aplicado: +0.3825
  Fracture: FALSE_FLAG_ATTRIBUTION_MISMATCH severity=0.85 [T1036.005] — Real malicious event confirmed (high technical score) with cultural attribution markers that contradict the observed TTP
  1 fractura(s) CAIE viva(s) contribuyeron al veredicto (boost +0.3825 aplicado al composite del scorer). Fuente: vigia_scorer._vigia_score (B-094).

--- FINAL ALERT LEVEL ---
HIGH — MALICE verdict from Bayesian posterior aggregation. Individual z-scores below threshold (distributed evidence pattern: no single dominant signal, but aggregate posterior is decisive). Alert floored (B-028/B-065).
Reconciliation: verdict MALICE rests on hypothesis-level aggregation, not on any single high-magnitude signal. Per-signal magnitude level was: LOW (per-signal magnitude) — no individual primary signal exceeds z>2 in this iteration.

Critical signals (z>3, primary): 0
High signals (2<z<=3, primary): 0
Primary signals: 3 | Derived: 0 | Total: 3
```

## 6. MITRE ATT&CK techniques mentioned

Technique ids found in the bundle, with MITRE's own name and description where VIGÍA's local dictionary has them. Descriptions are MITRE's English text and are not translated.

| Technique | Name | Found in |
| --- | --- | --- |
| `T1003.001` | [T1003.001](https://attack.mitre.org/techniques/T1003/001) (not in VIGÍA's local dictionary; URL derived from the id) | `signals.description` |
| `T1055.012` | [T1055.012](https://attack.mitre.org/techniques/T1055/012) (not in VIGÍA's local dictionary; URL derived from the id) | `signals.description` |

## 7. Where this sits in the SANS incident lifecycle

A sealed verdict is an output of the Identification phase. Containment, eradication and recovery are human decisions that this report does not make.

| Phase | What happens here |
| --- | --- |
| Preparation [1/6] | Build and maintain response capability: policy, tooling, training. |
| Identification [2/6] | Detect, alert and decide whether the event is an incident. Initial evidence collection and triage. VIGÍA's verdict lives here. |
| Containment [3/6] | Limit damage: isolate compromised systems while preserving evidence. |
| Eradication [4/6] | Remove the malicious artifact and its root cause. |
| Recovery [5/6] | Restore normal operation and monitor closely. |
| Lessons Learned [6/6] | Document the incident, improve detections and playbooks. |

`sans_compliance` in an agent bundle lists hackathon submission criteria (audit trail present, self-correction ran, and so on). It is not a PICERL phase.

```text
{"accuracy_validation": true, "analytical_reasoning": true, "architectural_guardrails": true, "audit_trail": true, "evidence_integrity": true, "self_correction": false}
```

## 8. Gaps and limitations

Anything the bundle does not say is listed here rather than filled in. Missing does not mean absent from reality; it means not recorded.

The bundle reader reported no gaps.

## 9. Glossary of sealed terms used above

Terms below are the literal tokens the bundle uses. They are explained, never translated.

- `Fraction`: Exact rational number (numerator/denominator). VIGÍA's scoring uses Fractions so two machines get identical results; they are never percentages.
- `MALICE`: Verdict rung 4 of 5. Active concealment of intent (anti-forensics). Requires two sources, the refutation protocol and a populated devil_advocate. (`devil_advocate`)
- `MITRE ATT&CK`: Public knowledge base of adversary techniques. Ids look like T1055 or T1070.006.
- `PICERL`: SANS incident-response lifecycle: Preparation, Identification, Containment, Eradication, Recovery, Lessons Learned.
- `agent_audit`: Bundle family: output of vigia_agent.py (Mode 1). Digest of the whole file lives in the .sha256 sidecar. (`agent_verdict`, `audit_trail`)
- `agent_verdict`: Agent bundle: the sealed four-value verdict (NOISE, SUSPICION, MALICE, ABSTAIN). Mode 1 has no INTENT rung.
- `best_hypothesis`: Agent bundle: label of the winning abductive hypothesis. A hypothesis label, not a verdict. (`agent_verdict`)
- `sans_compliance`: Agent bundle: checklist of hackathon submission criteria (audit trail, self-correction, ...). Not a PICERL phase. (`PICERL`)
- `z_score`: Agent signal: deviation of the signal from its baseline, as an exact Fraction. (`Fraction`)

## 10. How to verify this bundle yourself

Every check below is independent of this document. Run it on the bundle file, not on this report.

Agent bundle: `sha256sum -c FF-GENUINE-001_agent_bundle.json.sha256` checks the file against the digest written next to it when it was sealed. If a `_reasoning_trace.json` sibling exists, `vigia.core.reasoning_trace.verify_reasoning_trace` binds its verdict to `agent_verdict`.

Running a verifier on the wrong family reports non-compliance by design (docs/EXECUTION_MODES.md). Use the command that matches the family named in the header.

---

Generated by `vigia.report` 1.0 from the bundle whose SHA-256 is `e4496808337b21c05185ac7e0cce1b89cf384a354bdf435f5c6a1d240e8e74dd`. No timestamp is recorded on purpose: the same bundle bytes must always produce the same report bytes.
