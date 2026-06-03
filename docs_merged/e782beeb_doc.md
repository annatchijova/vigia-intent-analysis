<!--
VIGIA Academic Documentation
Module: e782beeb
Batch ID: vigia-doc-0142-e782beeb
Generated: 2026-05-20T14:56:47.875056+00:00
-->

---

# ENGLISH

## What Is This Module?

The **SIFT Orchestrator V4** is the central coordination engine of the VIGÍA forensic collective. It functions as a deterministic pipeline manager that directs fourteen or more specialized analytical engines—collectively called SIFT engines—to examine digital evidence. The orchestrator does not perform analysis itself; rather, it enforces strict operational rules: every file path is validated before any disk access occurs (TOCTOU protection), and each engine operates inside an isolated failure domain so that a malfunction in one component cannot collapse the entire investigation. All state transitions rely on exact integer arithmetic and boolean validation flags; no floating-point approximations are used anywhere in the evidence-handling logic.

### Evidence Sources

| Source | Description |
|---|---|
| Prefetch Directory | A folder containing `.pf` files that log program execution times and paths. |
| USB Registry Hive | A binary registry database file recording USB device attachment and configuration history. |

### Key Concepts

| Concept | Description | Scientific Role |
|---|---|---|
| SIFT Engine | A specialized analytical module (e.g., Metabolic, Resonance,
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
