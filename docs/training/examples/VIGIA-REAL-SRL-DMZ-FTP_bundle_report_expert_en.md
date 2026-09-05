# VIGÍA sealed verdict, expert review sheet

| Field | Value |
| --- | --- |
| Case | `VIGIA-REAL-SRL-DMZ-FTP` |
| Bundle family | `ebs_v1` |
| Source bundle | `VIGIA-REAL-SRL-DMZ-FTP_bundle.json` |
| Source SHA-256 | `d3083cb6b8a9bdebe286660845e858f096bfd27891a48bffb34505a6c9cb1a8a` |
| Audience | expert forensic examiner |
| Report layout version | `1.0` |

> This document carries NO verdict authority. It presents a sealed result verbatim; it computed nothing, reconciled nothing and can be regenerated from the bundle bytes at any time. If this text and the bundle ever disagree, the bundle is right and this file is stale.

> Values quoted from the bundle appear exactly as sealed, including their original language, spelling and numeric form. That is the evidence, not a rendering defect.

EBS v1: the sealed pipeline bundle (`evidence_graph`, `decision_trace`, `integrity`). Produced by `vigia/core/bundle_builder.py`.

## 1. Chain of custody

Every custody anchor this family defines, present or explicitly absent. Values are the sealed literals.

| Field | Sealed value |
| --- | --- |
| `integrity.bundle_hash` | `58e9c6248ceb6a4637e00b2abe39b1308daa74775b06ef36789036f6e159fc3a` |
| `integrity.analysis_fingerprint` | *not present in this bundle* |
| `integrity.graph_hash` | `beea81aad79408cec53c976857200936f6831741eeb345201c873118a0c1671f` |
| `integrity.decision_hash` | `f6ca86c484537e0ac280fea3abd689c305d62cab67665179c598e3570e799058` |
| `integrity.policy_hash` | `03d292f33eef1e4a2f355fe83299bdb8e72124c710f79ab4626d85a3998e9567` |
| `integrity.engine_attestation_hash` | `e50a38489c5672a9d158eb4b8e2f34a2bfd52c5eaaba541a96c1415f2e192e6b` |
| `integrity.ecl_hash` | *not present in this bundle* |
| `integrity.sealed_at` | `2026-06-10T19:28:16.860828+00:00` |

Hashes are only comparable within one bundle family. An EBS v1 `bundle_hash`, an agent bundle's sidecar digest and a Mode 2 `bundle_sha256` are computed over different payloads (KNOWN_LIMITATIONS L-030, L-031).

## 2. Verdict-bearing fields

| Field | Value | Confidence | JSON pointer |
| --- | --- | --- | --- |
| `decision_trace.decision` | **ABSTAIN** | *not present in this bundle* | `/decision_trace/decision` |
| `caie_analysis.verdict` | **MALICE** | `0.67` | `/caie_analysis/verdict` |

> `verdict_disagreement` is set: the fields above do not agree. The bundle sealed both; nothing here reconciles them (see docs/VIGIA_TECHNICAL_STATE_EN.md, section 12.3).

## 3. Peircean triad per finding (verbatim)

No Peircean triad is recorded in this bundle.

## 4. Exact sealed scores

Each value is the literal sealed in the bundle: serialized Fractions as `numerator/denominator`, floats as their JSON literal. Nothing is rounded or converted. A float in a sealed path is itself a finding (KNOWN_LIMITATIONS L-021, L-073).

| JSON pointer | Sealed literal |
| --- | --- |
| `/decision_trace/components_used` | `0` |
| `/decision_trace/consistency_score` | `1.0` |
| `/decision_trace/drift_score` | `0.0` |
| `/decision_trace/epsilon_used` | `0.05` |
| `/decision_trace/gamma_stability` | `2.0` |
| `/decision_trace/graph_stability` | `1.0` |
| `/decision_trace/lambda_drift` | `2.0` |
| `/decision_trace/log_lr` | `0.0` |
| `/decision_trace/lr` | `0.0` |
| `/decision_trace/omega_intention` | `1.0` |
| `/decision_trace/posterior` | `0.67` |
| `/decision_trace/risk` | `0.3346` |
| `/caie_analysis/composite_score` | `0.3346` |
| `/caie_analysis/confidence` | `0.67` |
| `/caie_analysis/caie_fractures` | `0` |

## 5. Daubert gates, refutation and devil's advocate

Records of a gate, downgrade or self-correction, as stored. These are the pre-emission corrections that make a verdict defensible.

### `/decision_trace/reason_code`

| Field | Sealed value |
| --- | --- |
| `field` | reason_code |
| `value` | VIGIA_SCORER:MALICE:R3_CALIBRATED |

### `/caie_analysis/hard_temporal_gate`

| Field | Sealed value |
| --- | --- |
| `field` | hard_temporal_gate |
| `value` | false |

### `/caie_analysis/r3_calibration_note`

| Field | Sealed value |
| --- | --- |
| `field` | r3_calibration_note |
| `value` | EBS decision=ABSTAIN reflects R3 coherence (risk in ABSTAIN zone). Forensic verdict remains MALICE per VIGÍA scorer. Quadripartite state: CORROBORATE_THEN_ACT. |

### `/caie_analysis/caie_fractures_source`

| Field | Sealed value |
| --- | --- |
| `field` | caie_fractures_source |
| `value` | live_caie |

### `devil_advocate` entries

No `devil_advocate` field is present.

> GAP: a verdict of MALICE is sealed but no `devil_advocate` is present. The Refutation Protocol (CLAUDE.md, Step 3) requires one for INTENT and MALICE. This report does not alter the verdict; it records the gap (KNOWN_LIMITATIONS L-022).

## 6. Execution record

- Record type: `system_state`

**`system_state` fields**

| Field | Sealed value |
| --- | --- |
| `calibration_model_hash` | `""` |
| `drift_score` | `0.0` |
| `engine_version` | `vigia-ebs-v1.0` |
| `epsilon_accept` | `0.05` |
| `epsilon_reject` | `0.05` |
| `gamma_stability` | `2.0` |
| `graph_stability_global` | `0.84` |
| `lambda_drift` | `2.0` |
| `timestamp` | `2026-06-10T19:28:16.852755+00:00` |

## 7. How to verify this bundle yourself

Every check below is independent of this document. Run it on the bundle file, not on this report.

EBS v1 bundle: `python3 forensics/verify_ebs_v1.py VIGIA-REAL-SRL-DMZ-FTP_bundle.json` recomputes `bundle_hash` and `analysis_fingerprint` over the payload (everything except `integrity`). Exit 0 means every check passed; exit 1 lists the failing checks.

Running a verifier on the wrong family reports non-compliance by design (docs/EXECUTION_MODES.md). Use the command that matches the family named in the header.

## 8. Known limitations

Limitations declared by the bundle, gaps found by the reader, and the repository limitations that bound any presentation of this family.

The bundle reader reported no gaps.

- L-004: narrative and prompt content are examiner-authored input, not evidence.
- L-020: Mode 2 bundles carry no granular `audit_trail`.
- L-022: `devil_advocate` validation is partly architectural.
- L-030 / L-031: sealing paths differ; hashes are not comparable across families and `verify_ebs_v1.py` rejects non-EBS bundles by design.
- L-056: Mode 1 and Mode 2 alert architectures diverge.
- L-074: this presentation renders sealed fields verbatim and cannot fill gaps a family does not record.

## 9. Glossary of sealed terms used above

Terms below are the literal tokens the bundle uses. They are explained, never translated.

- `ABSTAIN`: Verdict rung 5 of 5. Insufficient evidence to classify; the gap is a documented limitation, not a benign finding.
- `Daubert`: US admissibility standard for expert evidence: testable method, known error rate, peer review, general acceptance. VIGÍA's gates exist to meet it.
- `Fraction`: Exact rational number (numerator/denominator). VIGÍA's scoring uses Fractions so two machines get identical results; they are never percentages.
- `MALICE`: Verdict rung 4 of 5. Active concealment of intent (anti-forensics). Requires two sources, the refutation protocol and a populated devil_advocate. (`devil_advocate`)
- `analysis_fingerprint`: SHA-256 over the EBS v1 payload minus timestamps and ids: two runs on the same evidence share it.
- `bundle_hash`: SHA-256 over the whole EBS v1 payload except the integrity block (Invariant I2). Any change to any field changes it.
- `composite_score`: CAIE: the composite intent score before the verdict ladder.
- `decision_hash`: SHA-256 of the whole EBS v1 decision_trace.
- `ebs_v1`: Bundle family: sealed pipeline bundle with evidence_graph, decision_trace and an integrity block. Verified by forensics/verify_ebs_v1.py. (`bundle_hash`, `analysis_fingerprint`)
- `ecl_hash`: Hash of the evidence collection log, when one was supplied.
- `engine_attestation_hash`: Hash attesting the engine build that produced the bundle. Empty when not supplied.
- `graph_hash`: SHA-256 of the EBS v1 evidence_graph (minus generated_at).
- `policy_hash`: SHA-256 of the EBS v1 policy_spec (minus created_at).
- `posterior`: EBS v1 decision_trace: posterior probability sealed by the pipeline.
- `risk`: EBS v1 decision_trace: bounded risk value sealed by the pipeline.
- `sealed_at`: Timestamp at which the EBS v1 integrity block was written.
- `system_state`: EBS v1: engine version, calibration model hash and stability parameters at sealing time.
- `verdict_disagreement`: Reader flag: the bundle carries two verdict-bearing fields with different values. Both are shown; neither is chosen.

---

Generated by `vigia.report` 1.0 from the bundle whose SHA-256 is `d3083cb6b8a9bdebe286660845e858f096bfd27891a48bffb34505a6c9cb1a8a`. No timestamp is recorded on purpose: the same bundle bytes must always produce the same report bytes.
