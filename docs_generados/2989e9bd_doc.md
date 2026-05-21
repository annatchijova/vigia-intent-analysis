<!--
VIGIA Academic Documentation
Module: 2989e9bd
Batch ID: vigia-doc-0025-2989e9bd
Generated: 2026-05-20T14:56:47.850039+00:00
-->

# VIGÍA Forensic Suite — Consolidated Patch v1.0-Valkyrie  
**Module Path:** `scripts/vigia_patch_valkyrie.py`  
**Author:** Anna Tchijova  
**Date:** 2026-05-15  

---

# ENGLISH

## What Is This Module?
This file is a **forensic maintenance script** — a precise, automated repair tool for the VIGÍA digital forensics suite. Imagine a laboratory robotic arm that opens instrument cabinets, swaps mislabeled specimen tags, removes a compromised safety seal, and installs a corrected reference chart, all while logging every action with a tamper-evident checksum. This module performs exactly those operations on software files: it corrects four specific flaws discovered during a formal forensic audit, preserves backups, verifies file integrity via deterministic SHA-256 hashes, and can undo every change if an error occurs. No floating-point approximations are used; every decision is based on exact integer hash comparisons and deterministic string matching.

## Key Concepts

| Concept | Plain-Language Definition | Role in This Module |
|---|---|---|
| **Deterministic SHA-256 Verification** | A cryptographic fingerprint computed with exact integer arithmetic over every byte of a file. If a single bit changes, the fingerprint changes completely. | Before modifying anything, the script confirms that `ebs_v1.py` matches a pre-calculated, exact hash (`EBS_V1_EXPECTED_HASH`). |
| **Verifier Independence Invariant** | A scientific rule stating that the party who packages evidence must not be the same mechanism that later certifies its authenticity. | `patch_p0b()` removes the `ForensicBundle.seal()` method from all files except the original `ebs_v1.py`, preventing a conflict of interest in the evidence-handling chain. |
| **Tombstone (Daubert Marker)** | A permanent, read-only audit record left in place of removed code, noting why the removal occurred and under whose authority. | The `_SEAL_TOMBSTONE` constant injects a forensic marker so future reviewers can see that the seal was intentionally excised. |
| **Hypothesis ID Canonical Prefix** | A rigid naming convention for evidence labels (e.g., `H_XF_001`) that prevents two different artifacts from carrying the same identifier. | `patch_p0c()` renames a colliding label inside `abductive_intent_engine.py`, and `patch_p0d()` injects the master prefix table so the naming logic is consistent and deterministic. |
| **Rollback / Backup** | The automatic creation of a safety copy (`.valkyrie_bak`) before any change, with a one-click restore function. | `rollback_all_backups()` reverts every file to its pre-patch state using exact byte-for-byte restoration. |
| **PatchResult** | A structured record indicating whether a repair succeeded, failed, or was skipped. | Returned by every patch function so the `run()` coordinator can decide whether to continue or trigger automatic rollback. |
| **LIVE Mode** | The operational state in which changes are actually written to disk (as opposed to a simulation). | If any patch fails in LIVE mode, the script automatically invokes `rollback_all_backups()` to preserve evidence integrity. |

## Glossary

- **Forensic Artifact** — Any file, log, or data object that may be presented as evidence in an audit or legal proceeding.
- **Hash (SHA-256)** — A deterministic 256-bit integer digest that uniquely identifies a file’s exact content. Two files with the same hash are bit-for-bit identical.
- **Invariant** — A condition that must remain true at all times for the system to be scientifically valid.
- **Tombstone** — A non-executable audit marker left after code deletion to document the time, reason, and authority for the removal.
- **Canonical Prefix Table** — An authoritative lookup table that defines the only permitted letter codes for hypothesis identifiers, eliminating ambiguity.
- **Rollback** — The deterministic reversal of all modifications by restoring original files from their exact backups.

## 【Scientific Note】
> **Why the terminology of Peirce, Eco, and Grice is not mysticism.**  
> In the VIGÍA suite, these names refer to **semiotic sensors** — conceptual instruments that detect how meaning is formed, transmitted, and interpreted within digital evidence. Think of them not as philosophical ghosts, but as calibrated laboratory sensors:
> - A **Peirce sensor** detects the triadic relationship between a sign, the object it represents, and the interpreting mind (the interpretant).
> - An **Eco sensor** measures the boundaries of a "code" — the set of rules that makes a signal intelligible within a given culture or protocol.
> - A **Grice sensor** monitors cooperative communication expectations: it flags when a message violates the maxims of quantity, quality, relation, or manner.
>
> Just as a gas chromatograph does not "believe" in chemicals but measures them deterministically, these semiotic sensors do not invoke the occult; they apply deterministic, rule-based filters to logical fractures in evidence streams. Their outputs are integer-coded states, not vague intuitions.

---

# ESPAÑOL

## ¿Qué es este módulo?
Este archivo es un **script de mantenimiento forense** — una herramienta de reparación automatizada y precisa para la suite de forense digital VIGÍA. Imagínese un brazo robótico de laboratorio que abre gabinetes de instrumentos, corrige etiquetas de muestras mal escritas, retira un sello de seguridad comprometido e instala una tabla de referencia corregida, todo mientras
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
