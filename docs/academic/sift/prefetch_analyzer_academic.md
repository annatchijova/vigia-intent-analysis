<!--
VIGIA Academic Documentation
Module: 6c431d0b
Batch ID: vigia-doc-0138-6c431d0b
Generated: 2026-05-20T14:56:47.874302+00:00
-->

---
doc_hash: 6c431d0b
module: vigia/sift/prefetch_analyzer.py
languages: [EN]
generated_by: moonshot-kimi-k2.6-batch-api
license: Apache-2.0
---

---

## ENGLISH

### What Is This Module?
`vigia/sift/prefetch_analyzer.py` is a deterministic digital-forensic engine that examines Windows Prefetch files (extension `.pf`). Every time a program launches, Windows creates or updates one of these files. The module reads them to reconstruct when a program ran, how many times it ran, and which auxiliary files were loaded. It also detects deliberate gaps—such as the selective deletion of individual prefetch files—which are strong indicators of anti-forensic tampering. All quantitative findings are stored as exact rational numbers (`Fraction` objects or their string forms), ensuring that repeated analyses produce identical integer results with no approximation errors.

### Key Concepts

| Concept | Description | Scientific Purpose |
|---|---|---|
| **Prefetch File (.pf)** | A Windows system trace that records program execution, launch timestamp, and dependencies. | Serves as a passive, OS-generated sensor of software activity. |
| **PrefetchRecord** | A structured data row representing a single parsed prefetch trace. | Standardizes raw file contents into a human-readable evidence unit. |
| **PrefetchAnalysisResult** | The final report object containing correlated findings, reliability metrics, and anomaly flags. | Provides a deterministic
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
