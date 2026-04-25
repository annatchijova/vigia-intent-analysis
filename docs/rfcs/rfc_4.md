
---

# RFC-004 — VIGÍA Scoring & Decision Theory

**Status:** Draft
**Author(s):** The VIGÍA AI Collective
**Created:** 2026-04-16
**Target Version:** v1.0
**Related:** RFC-001 (Pipeline), RFC-002 (Trust), RFC-003 (Adversarial)

---

## 1. Abstract

This document defines the **mathematical decision layer** of VIGÍA.
It formalizes how:

* Evidence scores are aggregated
* Trust is applied
* Correlation is corrected
* A final **verdict** is produced

The system outputs one of four states:

```text
NOISE → INTENT → SUSPICION → MALICE
```

---

## 2. Scoring Pipeline (Formal)

### 2.1 Per-Artifact Score

Each artifact ( a_i ) produces:

[
S_i = R_i \cdot (1 - \sigma_i) \cdot w_i \cdot T_{e,i}
]

Where:

| Symbol       | Meaning         |
| ------------ | --------------- |
| ( R_i )      | Raw score       |
| ( \sigma_i ) | Spoofability    |
| ( w_i )      | Evidence weight |
| ( T_{e,i} )  | Effective trust |

---

### 2.2 Correlation-Adjusted Score

Let ( S_i' ) be the score after decay:

[
S_i' = S_i \cdot (1 - C_i)
]

Where ( C_i ) is computed by Correlation Decay Engine.

---

### 2.3 Composite Score

[
S_{total} = \sum_i S_i'
]

---

### 2.4 Diversity Bonus

[
S_{div} = S_{total} \cdot (1 + \beta \cdot D)
]

Where:

| Symbol          | Meaning                          |
| --------------- | -------------------------------- |
| ( D \in [0,1] ) | Diversity factor                 |
| ( \beta )       | Bonus coefficient (default: 0.2) |

---

### 2.5 Fracture Bonus

[
S_{final} = \min(0.99,; S_{div} + \sum_j (\gamma \cdot severity_j))
]

Where:

| Symbol     | Meaning                         |
| ---------- | ------------------------------- |
| ( \gamma ) | Fracture weight (default: 0.05) |

---

## 3. Confidence Model

Confidence is **not equal to score**.

[
Confidence = 1 - e^{-k \cdot S_{final} \cdot T_{avg}}
]

Where:

* ( k = 2.0 )
* ( T_{avg} = ) average trust across artifacts

### Properties:

* Saturates asymptotically
* Penalizes low-trust scenarios
* Prevents overconfidence

---

## 4. Verdict Function

### 4.1 Thresholds

| Range                       | Verdict   |
| --------------------------- | --------- |
| ( S_{final} < 0.2 )         | NOISE     |
| ( 0.2 \le S_{final} < 0.4 ) | INTENT    |
| ( 0.4 \le S_{final} < 0.7 ) | SUSPICION |
| ( S_{final} \ge 0.7 )       | MALICE    |

---

### 4.2 Override Rules (Critical)

#### Rule 1 — Temporal Impossibility Override

If ANY:

* EFFECT_BEFORE_CAUSE

Then:

```text
verdict = MALICE
confidence ≥ 0.9
```

---

#### Rule 2 — Broken Provenance Override

If:

* trust_score < 0.2

Then:

```text
verdict ≥ SUSPICION
```

---

#### Rule 3 — High Diversity Amplification

If:

* diversity > 0.8
* trust_avg > 0.8

Then:

```text
confidence += 0.1 (capped at 0.99)
```

---

#### Rule 4 — Correlation Collapse Protection

If:

* decay_ratio < 0.5

Then:

```text
reduce final score by 10%
```

(Prevents signal inflation attacks)

---

## 5. Peirce Mapping (Formal)

| Stage      | Meaning             | Implementation          |
| ---------- | ------------------- | ----------------------- |
| Firstness  | Raw signals         | ( R_i )                 |
| Secondness | Relations/conflicts | fractures + correlation |
| Thirdness  | Habit/inference     | verdict                 |

---

## 6. Decision Output Schema

```json
{
  "score": 0.78,
  "confidence": 0.91,
  "verdict": "MALICE",
  "components": {
    "raw_sum": 1.23,
    "adjusted_sum": 0.82,
    "diversity_bonus": 0.14,
    "fracture_bonus": 0.09
  },
  "trust": {
    "average": 0.86,
    "min": 0.42
  },
  "correlation": {
    "decay_ratio": 0.66
  },
  "overrides": [
    "TEMPORAL_IMPOSSIBILITY"
  ]
}
```

---

## 7. Failure Modes

### 7.1 High Score, Low Trust

* Many signals but weak provenance
  → Confidence collapses

---

### 7.2 Low Score, High Trust

* Clean but minimal evidence
  → INTENT at most

---

### 7.3 Correlated Flood

* Many similar artifacts
  → Neutralized by decay

---

## 8. Security Properties

| Property             | Mechanism           |
| -------------------- | ------------------- |
| Anti-spoofing        | spoofability factor |
| Anti-amplification   | correlation decay   |
| Anti-forgery         | trust fusion        |
| Anti-timeline attack | TCV override        |

---

## 9. Calibration Guidelines

Initial values:

```python
BETA = 0.2
GAMMA = 0.05
K_CONFIDENCE = 2.0
```

Recommended:

* Adjust via synthetic adversarial testing
* Keep thresholds fixed for legal defensibility

---

## 10. Determinism Guarantee

Given identical inputs:

```text
Output MUST be identical.
```

No randomness. No ML dependency.

---

## 11. Strategic Interpretation

The system does **not** answer:

> “What happened?”

It answers:

> “How inconsistent, manipulated, or improbable is the evidence?”

---



