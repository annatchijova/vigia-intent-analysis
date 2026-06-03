<!--
VIGIA Academic Documentation
Module: d4e678b5
Batch ID: vigia-doc-0022-d4e678b5
Generated: 2026-05-20T14:56:47.849380+00:00
-->

---

# ENGLISH

## What Is This Module?

`scripts/run_demo.py` is the master entry point for the VIGÍA forensic demonstration. Think of it as the **“start button”** for an automated laboratory workflow. It reads a digital case file written in JSON format, transforms raw forensic artefacts into structured signals, evaluates evidence strength through deterministic statistical engines, checks logical consistency via a multi-agent review board, and finally seals the results with a cryptographic integrity chain. No manual Python coding is required from the analyst; the script orchestrates the entire analytical sequence.

The module exposes two control points:

| Function | Role |
|---|---|
| `run_case()` | Executes the full analytical pipeline for a single forensic case file. |
| `main()` | Activates the script when started; locates the case file and triggers `run_case()`. |

## Key Concepts

**Table 1. Workflow Stages**

| Stage | Plain-Language Description | Deterministic Integer Component |
|---|---|---|
| Case Loading | Reads the JSON case file (e.g., `case_001_temporal.json`). | File paths handled as exact byte strings. |
| CaseAdapter | Converts raw forensic artefacts into `SignalOutput` objects. | Integer-indexed artefact arrays. |
| LikelihoodEngine | Scores how strongly each signal supports a hypothesis. | Uses kernel density counts; final scores mapped to rational thresholds via integer arithmetic. |
| GraphStabilityEngine | Validates that the evidence network is robust. | Bootstrap B=500: exactly 500 resampling iterations, counted as integers. |
| RiskBoundedDecisionLayer | Applies decision rules with strict error limits. | Risk budgets expressed as integer counts of allowable misclassifications. |
| AbductionTrace | Records the inference path (Firstness / Secondness / Thirdness). | Trace indices stored as fixed-width integers. |
| ForensicBundle | Collects all outputs into one evidentiary package. | Bundle manifest uses integer sequence numbers. |
| BundleBuilder.seal() | Creates a SHA-256 Merkle chain to prevent tampering. | SHA-256 operates on 512-bit integer blocks; hash chain links are deterministic integers. |
| C3 Multi-Agent Validation | `NarrativeAuditor` checks for logical breaks or prompt injections before closure. | Validation flags are discrete integer states (pass / fail / uncertain). |

**Table 2. Configuration Constants**

| Constant | Purpose |
|---|---|
| `_SCRIPT_DIR` | Absolute path to the script location, ensuring files are found reliably. |
| `_CASE_SEARCH_DIRS` | Ordered list of directories to search for case files. |
| `_VERIFIER_CANDIDATES` | Pool of auditing agents available for the C3 validation step. |
| `_DEFAULT_CASES` | Fallback case filenames if the user supplies none. |
| `_BANNER` | Text header displayed when the demo starts. |

## Glossary

| Term | Definition |
|---|---|
| **Forensic artefact** | Any digital remnant left by user activity (log entry, file timestamp, registry key). |
| **SignalOutput** | A standardized numerical representation of an artefact’s features, ready for statistical analysis. |
| **KDE** | Kernel Density Estimation; here used as a counting-based smoothing method to compare observed frequencies against expected baselines. |
| **Bootstrap B=500** | A robustness check repeating the graph analysis exactly 500 times on resampled subsets. |
| **Merkle chain** | A hierarchical cryptographic checksum where each layer depends on the previous, producing a single top-level integrity value. |
| **Prompt injection** | An adversarial attempt to hide malicious activity inside a narrative or query. |
| **AbductionTrace** | The logical footprint of an inference: Firstness (raw sensation), Secondness (observed reaction), Thirdness (interpreted law or rule). |
| **NarrativeAuditor** | An automated reviewer that verifies story coherence before the case is sealed. |

## 【Scientific Note】

> The terminology of Peirce, Eco, and Grice (Firstness / Secondness / Thirdness, narrative frameworks, implicatures) is sometimes mistaken for metaphysical speculation. In this module, these terms function exactly like a sensor array
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
