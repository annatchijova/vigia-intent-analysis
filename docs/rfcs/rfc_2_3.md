

# RFC-002 — VIGÍA Trust Model

**Status:** Draft
**Author(s):** The VIGÍA AI Collective
**Created:** 2026-04-16
**Target Version:** v1.0
**Related:** RFC-001 (Pipeline), CAIE, TCV, EPC, CDE

---

## 1. Abstract

This document defines the **Trust Model** of VIGÍA. It formalizes how trust is computed, propagated, degraded, and fused across forensic artifacts. The model integrates:

* Provenance Chain (EPC)
* Temporal Causality Validation (TCV)
* Correlation Decay (CDE)

The output is a **composite trust score** used for forensic decision-making under Daubert.

---

## 2. Motivation

Raw evidence scores are insufficient in adversarial environments. Trust must:

* Reflect **chain of custody integrity**
* Penalize **temporal impossibilities**
* Avoid **correlated overcounting**

This RFC defines a deterministic, explainable trust computation model.

---

## 3. Definitions

| Term                  | Definition                              |
| --------------------- | --------------------------------------- |
| Raw Score             | Initial evidence score (pre-adjustment) |
| Adjusted Score        | Score after spoofability weighting      |
| Provenance Trust (Tₚ) | Trust derived from EPC                  |
| Temporal Trust (Tₜ)   | Trust derived from TCV                  |
| Effective Trust (Tₑ)  | Final trust after fusion                |
| Correlation Penalty   | Reduction due to evidence redundancy    |

---

## 4. Trust Components

### 4.1 Provenance Trust (Tₚ)

Derived from ProvenanceChain:

```
Tₚ = average(composite_trust over chain)
```

Where:

```
composite_trust = inherited_trust × local_trust
```

#### Properties:

* Broken chain → Tₚ ≈ 0.1
* Full integrity → Tₚ ≈ 1.0

---

### 4.2 Temporal Trust (Tₜ)

Derived from TCV violations:

```
Tₜ = exp(- Σ(weightᵢ × severityᵢ))
```

#### Violation Weights:

| Type                   | Weight |
| ---------------------- | ------ |
| EFFECT_BEFORE_CAUSE    | 1.0    |
| TOO_FAST               | 0.7    |
| CLOCK_SKEW             | 0.5    |
| IDENTICAL_TIMESTAMP    | 0.4    |
| STATISTICAL_UNIFORMITY | 0.3    |

#### Interpretation:

* Exponential decay ensures **non-linear degradation**
* Multiple violations compound sharply

---

### 4.3 Correlation Adjustment

Handled by CDE:

```
Score_effective = Score_adjusted × (1 - correlation_penalty)
```

Where correlation penalty is:

* Reduced by **trust-weighted geometric mean**
* Increased if **trust < 0.3**

---

## 5. Trust Fusion

### 5.1 Core Formula

```
Tₑ = Tₚ × Tₜ
```

### 5.2 Properties

* If either component collapses → trust collapses
* Resistant to partial manipulation
* Deterministic and explainable

---

## 6. Integration with Scoring

Final artifact contribution:

```
Final Score = Raw × (1 - spoofability) × weight × Tₑ
```

Then passed into Correlation Decay Engine.

---

## 7. Edge Cases

### 7.1 No Provenance

```
Tₚ = 0.5
```

### 7.2 No Temporal Data

```
Tₜ = 1.0
```

### 7.3 Broken Chain + Temporal Violations

```
Tₑ → near 0
```

---

## 8. Security Properties

| Property           | Mechanism              |
| ------------------ | ---------------------- |
| Tamper resistance  | Provenance validation  |
| Anti-forgery       | Temporal causality     |
| Anti-amplification | Correlation decay      |
| Explainability     | Deterministic formulas |

---

## 9. Daubert Alignment

| Criterion   | Satisfaction                 |
| ----------- | ---------------------------- |
| Testable    | Yes (deterministic formulas) |
| Peer review | Yes (transparent model)      |
| Error rate  | Measurable via thresholds    |
| Standards   | Explicit weighting system    |

---

## 10. Future Work

* Dynamic calibration of weights
* Integration with hardware attestation (TPM)
* Cross-case trust propagation

---

# RFC-003 — VIGÍA Adversarial Model

**Status:** Draft
**Author(s):** The VIGÍA AI Collective
**Created:** 2026-04-16
**Target Version:** v1.0
**Related:** RFC-001, RFC-002

---

## 1. Abstract

Defines the **threat model** VIGÍA is designed to withstand. Focuses on adversaries capable of:

* Evidence fabrication
* Timeline manipulation
* Chain-of-custody tampering
* Signal correlation abuse

---

## 2. Adversary Classes

### 2.1 A1 — Opportunistic Attacker

* Modifies logs
* Deletes artifacts
* Low sophistication

### 2.2 A2 — Advanced Operator

* Alters timestamps
* Injects fake artifacts
* Understands forensic tools

### 2.3 A3 — Forensic-Aware Adversary

* Simulates realistic timelines
* Maintains partial consistency
* Attempts anti-detection strategies

### 2.4 A4 — State-Level Actor

* Controls infrastructure
* Manipulates clock sources
* Injects hardware-level deception

---

## 3. Attack Surfaces

| Surface    | Attack                  |
| ---------- | ----------------------- |
| Logs       | Injection, deletion     |
| Filesystem | Timestamp forgery       |
| Memory     | Process injection       |
| Network    | False attribution       |
| Provenance | Chain breaks            |
| Time       | Clock skew / reordering |

---

## 4. Attack Strategies

### 4.1 Temporal Manipulation

* Backdating events
* Reordering cause/effect

**Mitigation:** TCV

---

### 4.2 Provenance Break

* Removing parent artifacts
* Forging lineage

**Mitigation:** EPC

---

### 4.3 Evidence Flooding

* Repeating same signal

**Mitigation:** CDE

---

### 4.4 False Diversity

* Generating fake “independent” sources

**Mitigation:** correlation matrix + trust weighting

---

### 4.5 Trust Poisoning

* Introducing low-trust artifacts to distort scoring

**Mitigation:** geometric trust weighting

---

## 5. Defensive Principles

### 5.1 Assume Malice

All inputs are adversarial until proven otherwise.

---

### 5.2 Causality is Law

Violations of time = strongest signal of fabrication.

---

### 5.3 Lineage Over Content

Origin matters more than appearance.

---

### 5.4 Independence Over Quantity

10 identical signals ≠ 10 independent truths.

---

## 6. Detection Guarantees

| Attack                 | Detection Confidence    |
| ---------------------- | ----------------------- |
| Timestamp forgery      | High                    |
| Chain tampering        | High                    |
| Signal duplication     | High                    |
| Sophisticated blending | Medium                  |
| Perfect simulation     | Low (theoretical limit) |

---

## 7. Failure Modes

### 7.1 Perfect Adversary

* Fully consistent timeline
* Valid provenance
* Independent signals

→ **Undetectable by definition**

---

### 7.2 Clock Drift False Positives

* Distributed systems
* Poor NTP sync

→ Mitigated by skew tolerance

---

### 7.3 Sparse Evidence

* Insufficient artifacts

→ Low confidence output

---

## 8. Operational Assumptions

* Partial observability
* Adversarial environment
* Imperfect clocks
* Mixed trust sources

---

## 9. Security Posture

VIGÍA is:

* **Detection-oriented**, not prevention
* **Explainable**, not probabilistic black-box
* **Deterministic**, not ML-dependent

---

## 10. Strategic Position

VIGÍA does not attempt to prove truth.
It identifies **inconsistency, manipulation, and improbability**.

---

## 11. Future Work

* Adversarial simulation framework
* Red-team datasets
* Formal verification of causality constraints

---



