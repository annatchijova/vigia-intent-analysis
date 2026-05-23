<!--
VIGIA Academic Documentation
Module: 7b5f476a
Batch ID: vigia-doc-0034-7b5f476a
Generated: 2026-05-20T14:56:47.851872+00:00
-->

---
doc_hash: 7b5f476a
module: unknown
languages: [EN]
generated_by: moonshot-kimi-k2.6-batch-api
license: Apache-2.0
---

---

# ENGLISH

## What Is This Module?
The **Collapse Decision Layer (CDL)**, version 2 aggressive, is the terminal quality-control gate in the Vigia digital-forensics pipeline. Its sole purpose is to prevent composite evidence from being accepted when the underlying data sources have lost **sensor independence**—the guarantee that each source observes an event through an isolated channel. If two or more forensic artifacts share a hidden dependency (for example, one log file was generated from another), they can no longer corroborate each other. The CDL detects this condition and returns an **INCONCLUSIVE** verdict. The entire logic runs on **deterministic integer arithmetic**: every state, every comparison, and every decision uses exact whole-number flags, eliminating rounding errors and ensuring bit-level reproducibility across laboratories.

## Key Concepts

| Component | Plain-Language Description | Scientific Role |
|---|---|---|
| **CollapseVerdict** | The final classification label assigned to an evidence
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
