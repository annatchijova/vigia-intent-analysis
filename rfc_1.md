# RFC-001: VIGÍA Forensic Evidence Integrity Pipeline

**Status:** Draft  
**Authors:** The VIGÍA AI Collective  
**Last Updated:** 2026  

---

## 1. Abstract

This document specifies the VIGÍA forensic analysis pipeline, a deterministic system for detecting deception in digital evidence through layered validation:

- Temporal causality enforcement
- Provenance chain verification
- Trust fusion
- Cross-artifact inconsistency detection
- Correlation-aware scoring

The system is designed to be explainable, reproducible, and defensible under Daubert standards.

---

## 2. Design Principles

### 2.1 Determinism
No probabilistic or ML-based inference is required for core logic.

### 2.2 Layer Separation
Each validation domain operates independently:

| Layer | Domain |
|------|--------|
| TCV | Physical causality |
| Provenance | Chain of custody |
| CAIE | Logical consistency |
| Decay | Statistical independence |

### 2.3 Trust Propagation
Trust is computed once and propagated forward. No circular dependencies.

---

## 3. Pipeline Overview

Raw Data
↓
Normalization (P0)
↓
Temporal Validation (P1)
↓
Provenance Analysis (P2)
↓
Trust Fusion
↓
Cross-Artifact Analysis (CAIE)
↓
Correlation Decay
↓
Verdict


---

## 4. Temporal Causality (TCV)

### 4.1 Objective
Detect violations of physical causality.

### 4.2 Violation Types

- EFFECT_BEFORE_CAUSE (critical)
- TOO_FAST
- CLOCK_SKEW
- STATISTICAL_UNIFORMITY

### 4.3 Rule

If EFFECT_BEFORE_CAUSE is detected:

verdict = MALICE


---

## 5. Provenance Chain

### 5.1 Objective
Ensure chain of custody integrity.

### 5.2 Validation Criteria

- Parent continuity
- Hash consistency
- Temporal ordering

### 5.3 Output

trust_score ∈ [0,1]


---

## 6. Trust Fusion

### 6.1 Formula


effective_trust = base_trust * exp(-2 * penalty)


### 6.2 Inputs

- Provenance trust
- Temporal violations

---

## 7. Cross-Artifact Analysis (CAIE)

### 7.1 Objective
Detect inconsistencies across independent evidence sources.

### 7.2 Examples

- Memory vs logs mismatch
- Network vs host inconsistency
- False flag patterns

---

## 8. Correlation Decay

### 8.1 Objective
Prevent over-counting correlated evidence.

### 8.2 Key Formula


effective_correlation = base_corr * sqrt(T_A * T_B)


### 8.3 Principle

Multiple signals from the same source ≠ independent evidence.

---

## 9. Decision Layer

### 9.1 Verdict Mapping

| Condition | Verdict |
|----------|--------|
| Physical violation | MALICE |
| Score > 0.8 | MALICE |
| Score > 0.5 | SUSPICION |
| Else | NOISE |

---

## 10. Orchestration (PeircePlanner)

### 10.1 Rules

- Trigger TCV when timestamps present
- Trigger Provenance on critical signals
- Trigger CAIE after sufficient artifacts

---

## 11. Explainability (Peirce Model)

| Stage | Meaning |
|------|--------|
| Firstness | Raw observations |
| Secondness | Relationships |
| Thirdness | Inferred behavior |

---

## 12. Security Considerations

- Assume adversarial manipulation
- Treat all timestamps as untrusted until validated
- Penalize unverifiable provenance

---

## 13. Future Work

- Calibration of spoofability values
- Adversarial simulation datasets
- Formal verification of causality rules

---


