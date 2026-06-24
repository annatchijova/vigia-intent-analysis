# VIGÍA FORENSIC INTENT ANALYSIS REPORT — Amicus Curiae

## Case: VIGIA-KIWI-002

```
Case ID      : VIGIA-KIWI-002-ZAPALLO-POV
Case Name    : VIGIA-KIWI-002 Apophenia Stress Test — Denunciante POV
Investigator : VIGÍA Autonomous Agent (Claude Code + MCP / Anthropic)
Origin       : MPF7779408 | framing: perspective_actor_a
Evidence     : scripts/VIGIA_KIWI_002_ZAPALLO_POV.json
Mode         : Claude Code + MCP [LLM: FALLBACK]
SHA-256      : 739f538ad85c01c74768d200cbfe9c103702ab4c3eb99bb297d4a5e25eb56c51
File size    : 9923 bytes
Timestamp    : 2026-06-24T16:44:00.082992Z
SANS Phase   : Phase 4 — Validation / Lessons Learned
```

---

## FORENSIC BUNDLE — FOUR INTEGRITY HASHES

Sealed: `2026-06-24T16:45:28.315732Z`

| Hash Type | Value |
|---|---|
| `bundle_hash` | `139851cb94faa4fa81bce4eee4de682df23702aa91c713ec435e5f99c72ba3ff` |
| `decision_hash` | `9fd38d3342875ab95a4a42ec69f00463c6c69459f35d6f237bba5f1671bfb18d` |
| `engine_attestation_hash` | `cf550ce92190c7caf6d15b40faaa4ad78e5c78fecc7245ff736d9ae2394f6865` |
| `graph_hash` | `94147b51c639cd0c5f361fc885bdd59a257ffaf3f770203ff7b7a3a787b57f53` |

**Bundle verification: PASSED — bundle íntegro**

---

## PIPELINE SCORING RESULTS

| Metric | Value |
|---|---|
| Pipeline decision | REJECT (REJECT_POSTERIOR) |
| Posterior P(intent\|evidence) | 0.023874 (2.4%) |
| Log-LR | −3.711 |
| Risk score | 0.976126 |
| PSI (drift, recalculated) | 31.8132 — extremely high distributional shift |
| CAIE composite score | 0.0419 |
| CAIE fractures (automated) | 0 |
| CAIE structural verdict | NOISE |
| Consistency score (sealed) | 1.0 (DARVO patch not yet applied at seal time — see F-004) |
| Consistency score (current code) | 0.70 (DARVO penalty 3/10 fires) |
| Inference mode | CALIBRATED |
| Signals | 8 artifacts at uniform z_score=2.0, confidence=0.3 |

---

## EXECUTIVE SUMMARY

KIWI-002 is an adversarial input constructed entirely from unverified actor_A testimony. All 8 artifacts carry prior_trust=0.3 and uniform raw_score=0.8. The pipeline correctly issues REJECT at posterior=0.024, matching the expected verdict of SUSPICION. Two primary questions were investigated:

1. **Prior trust propagation:** NO — partial gap confirmed. The confidence field (mapped from prior_trust) is stored in the audit trail but is not read by LikelihoodEngine.infer(). Only z_score enters the log-LR computation. Counterfactual runs with confidence=0.3 vs confidence=0.8 produce identical results. However, the verdict is stable: all three trust-propagation variants converge on REJECT.

2. **Apophenia detection:** NOT automated — manually confirmed via Peircean analysis. The detect_eco_overinterpretation tool returned NORMAL_DISTRIBUTION (it checks for keyword-based staging, not statistical uniformity). Apophenia is detectable through PSI=31.8132 (flagging implausible clustering of 8 uniform z=2.0 signals), claim taxonomy analysis, and Eco's Significant Silence.

**Verdict: SUSPICION** — consistent with expected_verdict in case definition.

---

## QUESTION 1: DOES PRIOR_TRUST=0.3 PROPAGATE CORRECTLY?

**Answer: Partially — the verdict is correct, but the mathematical certainty is underweighted.**

The pipeline mapping is prior_trust → confidence (SignalOutput field). LikelihoodEngine reads only z_score:

```python
LikelihoodEngine.infer():
    z_clipped = [self._clip_z(s.z_score) for s in signals]   # ← only z_score
    log_lrs   = [calibrator.calibrated_log_lr(z) for z in z_clipped]
    # s.confidence is written to ForensicRecord.signals_in[] but never multiplied
```

Counterfactual analysis:

| Scenario | z_eff | posterior | log_LR | Risk | Decision |
|---|---|---|---|---|---|
| Actual (trust stored, not used) | 2.000 | 0.02387 | −3.711 | 0.976 | REJECT |
| Counterfactual (confidence=0.8, same z) | 2.000 | 0.02387 | −3.711 | 0.976 | REJECT |
| Correct — Method A: z_eff = z × trust | 0.600 | ~0.000 | −22.770 | 1.000 | REJECT |
| Correct — Method B: z_eff = z(raw×trust) | −1.733 | ~0.000 | −54.536 | 1.000 | REJECT |

Verdict stability: all paths → REJECT. The gap doesn't produce a wrong verdict here.

**Daubert implication:** The sealed bundle certifies posterior=0.024 whereas correct trust weighting would certify posterior≈0. A defense attorney could argue the pipeline overstates the claimant's evidence quality. The gap should be closed before court presentation.

**Recommended fix:** `log_lrs[i] *= s.confidence` in `LikelihoodEngine.infer()`. One line.

---

## QUESTION 2: IS APOPHENIA DETECTABLE?

**Answer: Not by any single automated tool — but the pattern is structurally identifiable through three converging signals.**

| Tool | Result | Apophenia captured? |
|---|---|---|
| detect_eco_overinterpretation | NORMAL_DISTRIBUTION | No — checks keyword staging, not uniform-score staging |
| audit_grice_maxims | SUSPICION, 30%, TACTICAL_EVASION/RELATION | Partially — detects evasion, not the full apophenia structure |
| infer_intent | NOISE — 0 escalation signals | No |

**Why detect_eco_overinterpretation fails here:** The Eco tool flags evidence that is too obviously planted (high ratio of explicit threat keywords). Apophenia produces the inverse signature: uniformly high confidence across thematically incoherent claims with no explicit threat vocabulary.

### Apophenia Indicators (manual)

**AP-1 — Statistical Uniformity Anomaly**
8 independent claims, 8 identical raw_score=0.8. PSI = 31.8132 (reference: KIWI-001 PSI=5.34, KIWI-002 is 6× higher). P(8 uncorrelated forensic signals at identical score by chance) ≈ 0. Uniform confidence not from evidence quality — from cognitive state of claimant who perceives all events as equally threatening.

**AP-2 — Claim Taxonomy Incoherence**
- A01: skill inference (habilidad ≠ conducta) → logically incoherent
- A03: cartas a Clarín → empirically REFUTED (no record)
- A05: debt as risk profile → zero legal correlation
- A06: Interpol coordination → structurally IMPOSSIBLE
- A07: threat from songs+photos, 0 contact → causally unconnected

Declarant assigns threat weight=0.8 to a REFUTED claim and an IMPOSSIBLE claim identically to plausible-but-unverifiable claims. Calibration has collapsed.

**AP-3 — Eco Significant Silence**
Across 8 claims: 0 verified positive artifacts attributable to imputada. A03 is the only verifiable claim → REFUTED. Apophenia's defining feature: the meaning network has no external anchors.

**AP-4 — Causal Chain Substitution**
Each claim bypasses the step "imputada directed this at me": A01: skill → assumed threat; A02: song → assumed declaration; A04: father owns weapon → assumed access. Systematic substitution of proximity for causation — hallmark of apophenic reasoning, not deception.

---

## PEIRCEAN ABDUCTIVE CHAIN

**FIRSTNESS:** 8 unverified claims at uniform raw_score=0.8. All from single unverified source (actor_A). One claim empirically refuted (A03), one structurally impossible (A06), five logically incoherent, one pre-causal. PSI=31.8132.

**SECONDNESS:** Normal testimony from a claimant with genuine threat experience shows variable confidence levels. Uniform 0.8 across 8 categorically distinct claims violates this baseline. A03 (verifiable, REFUTED) and A06 (Interpol, structurally impossible) carry the same weight as potentially-verifiable claims. Calibration collapse is the structural anomaly.

**THIRDNESS:** The repeatable pattern is not deliberate deception (DARVO/false-flag) but apophenic signal generation: a cognitive state in which all perceived observations confirm a pre-existing threat narrative, producing uniform confidence regardless of evidential quality. This is distinct from the FC-1→FC-5 fracture pattern in KIWI-001 (where deliberate construction was indicated by server infrastructure and active surveillance). KIWI-002 does not evidence deliberate concealment — it evidences calibration failure in the declarant. Carnegie taxonomy: Pseudo-authority via volume — 8 claims presented with identical certainty creates cumulative rhetorical weight without evidential foundation.

---

## FINDINGS

### F-001 — Uniform Confidence Anomaly: apophenia structural signature

| | |
|---|---|
| Verdict | SUSPICION |
| Confidence | HIGH |
| Status | CONFIRMED |
| Artifact | All 8 (A01–A08) |
| Tools | run_vigia pipeline (PSI=31.8132), manual analysis |
| Firstness | 8 claims, 8 × raw_score=0.8, all from single unverified source |
| Secondness | Calibration collapse — REFUTED claim (A03) and IMPOSSIBLE claim (A06) carry identical confidence weight as unverifiable claims |
| Thirdness | Apophenic signal generation: threat narrative precedes and shapes evidence evaluation |
| Carnegie | Pseudo-authority via volume (cumulative unqualified assertions) |
| Devil Advocate | Uniform high fear response to perceived threat stimuli is consistent with trauma-related hypervigilance; does not require deliberate fabrication. |
| Corroboration | PSI=31.8132 (statistical), A03 refutation (empirical), A06 impossibility |
| Self-Correction | SUSPICION not INTENT. No evidence of deliberate construction by imputada. Daubert gate holds. |

### F-002 — Empirically refuted claim (A03): cartas documento a Clarín

| | |
|---|---|
| Verdict | NOISE (for imputada) / SUSPICION (for evidentiary quality of corpus) |
| Confidence | HIGH |
| Status | CONFIRMED (verifiable: True, verification_result: REFUTED) |
| Artifact | KIWI-002-A03 |
| Firstness | Claim: imputada sent 5 cartas documento to Clarín. Judicial file: no record. |
| Secondness | Only verifiable claim in corpus → REFUTED. Weight in declarant's narrative: identical to unverifiable claims (raw_score=0.8). |
| Thirdness | A single REFUTED claim in an 8-claim corpus from an unverified source with uniform confidence confirms that the trust prior (0.3) is correctly calibrated. |
| Devil Advocate | Claim may reflect genuine belief based on misremembered event or third-party misinformation. |
| Self-Correction | CONFIRMED via case definition verification_result field. |

### F-003 — Structurally impossible claim (A06): Interpol coordination

| | |
|---|---|
| Verdict | NOISE |
| Confidence | HIGH |
| Status | CONFIRMED |
| Artifact | KIWI-002-A06 |
| Firstness | Claim: imputada coordinates with Interpol against declarant. |
| Secondness | Interpol has no mandate for domestic partner disputes under any applicable treaty. The claim is structurally impossible independent of the imputada's conduct. |
| Thirdness | Structurally impossible claim + empirically refuted claim + logically incoherent claims = apophenic triad: threat network has expanded beyond factual constraints. |
| Devil Advocate | Declarant may have conflated Interpol with a domestic agency, or received disinformation from a third party. |
| Self-Correction | CONFIRMED. Structural impossibility established by treaty jurisdiction. |

### F-004 — DARVO: post-patch detection

| | |
|---|---|
| Verdict | SUSPICION |
| Confidence | MEDIUM |
| Status | INFERRED (bundle pre-patch; current code CONFIRMED) |
| Artifact | A06 (log_entry + surveillance keywords), A03+A07 (zero_contact keywords) |
| Tools | darvo_detector.py (post-linter-patch) |
| DARVO result | penalty=3/10, consistency_score=0.70 |
| Note | Sealed bundle (16:45:28Z) used pre-patch darvo_detector → consistency=1.0. Re-run with current code → consistency=0.70. Bundle hash would differ. Discrepancy documented for audit trail integrity. |
| Devil Advocate | DARVO keywords are in the examiner's descriptions of actor_A conduct (from KIWI-001), not in primary evidence produced by imputada. |
| Self-Correction | INFERRED. DARVO in this case belongs to actor_A's behavioral pattern established in KIWI-001. |

### F-005 — Eco Overinterpretation tool gap: apophenia not detected

| | |
|---|---|
| Verdict | ABSTAIN (tool scope limitation) |
| Confidence | HIGH (for the gap characterization) |
| Status | CONFIRMED |
| Finding | Tool returned NORMAL_DISTRIBUTION despite 8 uniform-score claims from unverified source. Gap: tool checks for explicit threat keywords (obvious_ratio), not for statistical uniformity anomalies. |
| Recommendation | Add uniformity detector: flag when N≥3 signals from single unverified source cluster at raw_score > baseline ± 0.05. One additional check in detect_eco_overinterpretation. Does not require LLM. |

---

## REFUTATION GATE LOG

```
REFUTATION GATE — All findings
  Candidate verdict : INTENT
  Gate applied      : Daubert Corroboration + Benign Incompetence Hypothesis
  Benign hypothesis : Declarant experiencing trauma-related hypervigilance.
                      ALL 8 claims explained by apophenic cognition without any
                      deliberate fabrication by imputada.
  Gate result       : Benign hypothesis explains full evidence set without contradiction.
                      INTENT rejected. SUSPICION emitted.
                      No INTENT or MALICE finding for imputada — zero verified contact,
                      zero positive evidence of directed threat.
```

---

## VERDICT

| | |
|---|---|
| **Verdict** | **SUSPICION** |
| Confidence | 68% |
| Expected verdict | SUSPICION ✓ MATCH |
| Prior trust propagation | PARTIAL GAP — confidence field not read by LikelihoodEngine; verdict stable, posterior underweighted |
| Apophenia detected | YES — manually (PSI, claim taxonomy, causal gap pattern); NOT by automated tools |
| DARVO detected | YES — post-patch (penalty=0.30, consistency=0.70); sealed bundle pre-patch (1.0) |
| Pipeline decision | REJECT (posterior=0.024 < epsilon=0.05) |

---

## COMPARISON vs KIWI-001

| Metric | KIWI-001 | KIWI-002 |
|---|---|---|
| SHA-256 | 114a73c6... | 739f538a... |
| Artifacts | 4 (mixed scores 0.3–0.7) | 8 (uniform 0.8) |
| prior_trust | 0.8 | 0.3 |
| Posterior | 1×10⁻⁶ | 0.02387 |
| Log-LR | −14.335 | −3.711 |
| PSI | 5.3420 | 31.8132 |
| CAIE composite | 0.0137 | 0.0419 |
| Primary fracture type | FC-1..5 (false flag, deliberate construction) | Apophenia (calibration collapse) |
| DARVO | FC-5 candidate (manual) | Post-patch: 0.70 / Sealed: 1.0 |
| Verdict | SUSPICION ✓ | SUSPICION ✓ |

The two cases are analytically complementary: KIWI-001 shows deliberate false-flag construction (actor_A with infrastructure and tools); KIWI-002 shows apophenic input from the same actor (no infrastructure required — the meaning network is self-sustaining).

---

## KNOWN LIMITATIONS

1. **LLM FALLBACK:** reason_with_llm not available. All apophenia analysis is manual.
2. **Prior trust gap:** confidence → LikelihoodEngine propagation is zero. Correct fix: `log_lrs[i] *= s.confidence` in likelihood_ratio.py. Verdict unchanged here; posterior changes from 0.024 to ~0.000.
3. **Eco tool apophenia blind spot:** Uniform high-score unverified claims are not flagged. Dedicated uniformity check needed.
4. **DARVO bundle mismatch:** Sealed bundle hash 139851cb... corresponds to consistency_score=1.0. Current code produces 0.70. These are forensically distinct states — the sealed hash is the authoritative record of what was computed at seal time.
5. **Token usage:** FALLBACK — no LLM tokens consumed. Session: 2026-06-24T16:44:00Z.
