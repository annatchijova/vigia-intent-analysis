RFC-002 — Trust Model
# RFC-002: VIGÍA Trust Model Specification

**Status:** Draft  
**Authors:** The VIGÍA AI Collective  
**Last Updated:** 2026  

---

## 1. Abstract

This document defines the trust model used in VIGÍA to evaluate the reliability of forensic evidence.

Trust is treated as a first-class signal that propagates through the pipeline and modulates all downstream scoring.

---

## 2. Core Principle

Trust is not binary.


trust ∈ [0.0, 1.0]


Where:

- 1.0 = fully verifiable, high-integrity evidence  
- 0.0 = completely untrustworthy  

---

## 3. Trust Sources

### 3.1 Provenance Trust

Derived from chain of custody validation.

Factors:
- lineage continuity
- hash integrity
- parent existence
- temporal consistency

---

### 3.2 Temporal Trust

Derived from physical causality validation.

Penalized by:
- effect-before-cause
- impossible speed
- clock inconsistencies

---

## 4. Trust Fusion

### 4.1 Formula


effective_trust = base_trust * exp(-2 * temporal_penalty)


---

### 4.2 Properties

- Monotonic decreasing with anomalies
- Exponential penalty for compounded violations
- Bounded in [0,1]

---

## 5. Trust Propagation

Trust flows forward only.


Artifact → Trust → Score → Verdict


No feedback loops are allowed.

---

## 6. Trust Collapse

If:


effective_trust < 0.3


Then:

- evidence weight is heavily reduced
- correlation penalties are relaxed
- artifact is considered unreliable

---

## 7. Interaction with Correlation

Correlation is weighted by trust:


effective_corr = base_corr * sqrt(T_A * T_B)


Implication:
Low-trust evidence cannot suppress independent signals.

---

## 8. Missing Provenance

If provenance is unavailable:


base_trust = 0.6


Rationale:
Unverifiable ≠ malicious, but cannot be fully trusted.

---

## 9. Design Goals

- Deterministic
- Explainable
- Resistant to planted evidence

---

## 10. Security Implications

- Trust acts as a defense against evidence fabrication
- Prevents amplification of low-quality signals
- Limits attacker ability to bias composite score

---
