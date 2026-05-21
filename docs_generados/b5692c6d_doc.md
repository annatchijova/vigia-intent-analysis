<!--
VIGIA Academic Documentation
Module: b5692c6d
Batch ID: vigia-doc-0107-b5692c6d
Generated: 2026-05-20T14:56:47.867815+00:00
-->

# Module Documentation: `vigia/patterns/adversarial_silence.py`

---

## ENGLISH

### What Is This Module?
This module implements an **Adversarial Silence Detector** for the VIGÍA forensic framework. In digital investigations, every user action—a *primary action*—normally leaves behind secondary traces such as log entries, temporary files, or metadata structures. When these expected traces are systematically missing, the absence is not merely “nothing”; it is a deliberate pattern of deletion. This detector registers claimed or inferred actions, tracks whether their expected secondary artifacts are present or confirmed absent, and computes forensic scores using **exact integer arithmetic** (exact rational numbers). The central insight is that an attacker who knows which artifacts are difficult to erase—for example, Windows Prefetch files or `$MFT` records—and selectively removes them reveals advanced knowledge of forensic methodologies. The detector captures this sophistication indicator by analyzing the pattern of silence.

### Key Concepts

| Concept | Description | Scientific Relevance |
|---|---|---|
| **Primary Action** | An event asserted or inferred to have occurred (e.g., program execution, file deletion). | The hypothesized cause in a causal chain. |
| **Secondary Artifact** (`ExpectedArtifact`) | A trace or file that should remain if the primary action occurred (e.g., a Prefetch file). | The expected effect; its absence contradicts the hypothesis. |
| **Adversarial Silence** | The systematic absence of expected secondary artifacts. | Indicates deliberate anti-forensic activity rather than natural data decay. |
| **Deterministic Scoring** (`Fraction`) | Exact rational numbers computed from integer numerators and denominators. | Eliminates rounding errors; guarantees reproducible results across all platforms. |
| **Frozen Record** (`frozen dataclass`) | An immutable, hashable record. | Ensures audit integrity: once recorded, evidence cannot be altered in memory. |
| **Audit Hash** | A deterministic fingerprint of the analysis state. | Verifies that the investigative process itself has not been tampered with. |

| Operation | Plain-Language Description |
|---|---|
| **Register Primary Action** | Log a hypothesized main event into the detector. |
| **Register Present Artifact** | Confirm that a predicted secondary trace was found on the system. |
| **Register Confirmed Absent** | Record that a predicted trace is definitively missing. |
| **Analyze** | Compute exact forensic scores and detect patterns of adversarial silence. |

### Glossary

- **Adversarial Silence**: A forensic pattern in which an attacker selectively removes traces to thwart investigation.
- **Artifact (Forensic)**: Any digital object—file, log, metadata entry—that serves as evidence of an action.
- **Deterministic Integer Arithmetic**: Calculations performed with exact fractions (ratios of integers), avoiding all approximations.
- **Frozen Record**: An immutable data structure that cannot be modified after creation, preserving chain-of-custody in software.
- **Primary Action**: The main event under investigation from which secondary effects are predicted.
- **Secondary Artifact**: A byproduct trace expected to exist given a specific primary action.
- **Sensor Analogy**: The conceptual model treating expected artifacts as sensors; a missing signal is a null measurement, not an absence of data.

### 【Scientific Note】
This module employs concepts from semiotics (C. S. Peirce, Umberto Eco) and linguistic pragmatics (H. P. Grice). In semiotics, a sign need not be a visible object; the *absence* of an expected index is itself a sign. In pragmatics, Grice's cooperative maxims assume truthful and informative communication—systematic violation implies deliberate intent. None of this is mysticism. Think of the detector as a sensor array: each expected artifact is a sensor channel.
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
