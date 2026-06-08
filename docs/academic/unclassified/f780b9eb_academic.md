<!--
VIGIA Academic Documentation
Module: f780b9eb
Batch ID: vigia-doc-0160-f780b9eb
Generated: 2026-05-20T14:56:47.879095+00:00
-->

---

# ENGLISH

## What Is This Module?

This module is the **secure evidence locker** for the VIGÍA system.  
Imagine a high-security laboratory notebook that automatically records every observation, every suspect communication profile, and every chain-of-custody event in a tamper-resistant SQLite database. Scientists do not need to know Python; they only need to understand that this component guarantees that data retrieved today will be **bit-for-bit identical** to data stored yesterday.

The manager enforces strict admission rules: if a measurement fails integrity checks—for example, a coherence score crosses a safety threshold—the entry is **rejected**. All arithmetic inside the decision boundary is **deterministic integer arithmetic**; the system uses exact integer comparisons (e.g., scaled integer thresholds) rather than approximate real-number operations. There are no probabilistic roundings.

Design motto: **SANS FIND EVIL**.

### Key Concepts

| Concept | Plain-Language Definition | Scientific Relevance |
|---|---|---|
| **Singleton Pattern** | Only one database manager exists per running process. | Prevents conflicting writes and guarantees a single source of forensic truth. |
| **WAL Mode** | Write-Ahead Logging: changes are appended to a separate journal before touching the main file. | Ensures atomic transactions; if power is lost, recovery is deterministic. |
| **ACP Profile** | Adversarial Communication Profile: a structured record of linguistic behavior. | Stores Peircean sign-classification vectors and Gricean maxim-violation counts as integer tuples. |
| **MCP (Coherence Metric)** | An integer-scaled consistency score. | Updates are rejected via exact integer arithmetic when the scaled threshold is breached (e.g., `10 × MCP_int > 25`), signaling probable spoofing. |
| **Sliding Window** | SQLite triggers retain only the 20 most recent documents per emitter. | Bounds storage deterministically; old records are purged by integer count, not heuristic. |
| **Anti-Traversal / Anti-Symlink** | Path sanitization blocks `..` sequences and symbolic link tricks. | Prevents redirection of the database file to an attacker-controlled path. |
| **Daubert Audit Trail** | Immutable log satisfying legal admissibility standards for expert testimony. | Every write carries an integer timestamp and attribution, producing court-ready provenance. |
| **File Permissions (0o640)** | Owner and group may read/write; all others are denied. | Enforces least-privilege at the operating-system level using exact octal integer masks. |
| **500 MB
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
