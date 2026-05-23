<!--
VIGIA Academic Documentation
Module: aa4e03f6
Batch ID: vigia-doc-0052-aa4e03f6
Generated: 2026-05-20T14:56:47.855668+00:00
-->

---
doc_hash: aa4e03f6
module: vigia/core/explainable_governance.py
languages: [EN]
generated_by: moonshot-kimi-k2.6-batch-api
license: Apache-2.0
---

---

## ENGLISH

### What Is This Module?
`vigia/core/explainable_governance.py` is a **deterministic forensic reasoning engine**. Its purpose is to convert raw digital findings—called forensic artifacts—into structured, human-readable governance reports. The module operates entirely through discrete logic. Every conclusion is produced via **deterministic integer arithmetic**: identical inputs always yield identical outputs, with no approximation, rounding, or fractional drift. It employs formal semiotic frameworks (Peirce, Eco, Grice) as classification layers. These are not philosophical opinions; they function like calibrated sensors that translate evidence traces into categorical integer states.

### Key Concepts

| Component | Scientific Role | Deterministic Behavior |
|-----------|----------------|------------------------|
| `ExplanationEngine` | Core processing unit that ingests normalized forensic artifacts and assigns categorical states. | Uses only integer-encoded rule sets; output is reproducible. |
| `generate_explanation()` | Procedure that maps a set of artifacts to a validated reason code. | Relies on integer ranking of evidence weight; no fractional weights. |
| `to_html()` | Rendering layer that converts discrete output structures into a visual markup format. | Transforms integer states into text without altering evidentiary content. |
| `dominance_key()` | Resolution function for competing hypotheses. | Applies ordinal integer comparison to establish priority. |
| `TEMPLATES` | Predefined structural schemata ensuring report consistency across analyses. | Static integer-indexed layouts. |
| `REASON_CODES` | Enumerated integer identifiers for every conclusion type. | Fixed integer map; one-to-one correspondence between state and label. |
| `CONTRADICTION_TYPES` | Discrete categories for logical conflicts detected between artifacts. | Encoded as integer enumerations; logical fractures are classified as distinct integer states. |

### Glossary

| Term | Definition |
|------|------------|
| **Forensic Artifact** | A discrete, measurable digital object extracted from a source system and normalized for analysis. |
| **Deterministic Integer Arithmetic** | A calculation paradigm using only whole numbers (integers) where identical inputs invariably produce identical outputs, eliminating stochastic drift. |
| **Semiotic Layer** | A formal analytical filter that treats data traces as signs with structured meaning, analogous to a physical
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
