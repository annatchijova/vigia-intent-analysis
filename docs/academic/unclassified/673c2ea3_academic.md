<!--
VIGIA Academic Documentation
Module: 673c2ea3
Batch ID: vigia-doc-0069-673c2ea3
Generated: 2026-05-20T14:56:47.859298+00:00
-->

## ENGLISH

### What Is This Module?

This module implements a bounded abductive inference engine for the VIGÍA forensic analysis framework. It replicates, in algorithmic form, the cognitive workflow of a human forensic examiner who must explain a set of evidence signals by proposing and testing hypotheses. Unlike an unconstrained reasoning system, this engine incorporates a hard cognitive boundary—the Miller limit (N = 7 iterations)—to prevent infinite oscillation between contradictory explanations or overfitting to noise. The system halts when it achieves complete signal coverage, when explanatory cost stabilizes (Ockham convergence), when it detects an A→B→A oscillation pattern, or when it reaches the seventh iteration. Every internal operation relies on deterministic integer arithmetic.

---

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
