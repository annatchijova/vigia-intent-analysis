<!--
VIGIA Academic Documentation
Module: 350c8eab
Batch ID: vigia-doc-0131-350c8eab
Generated: 2026-05-20T14:56:47.872778+00:00
-->

# Module Documentation: `vigia/sift/browser_forensics.py`

---

## ENGLISH

### What Is This Module?
This module is a digital forensics instrument. It treats web browser artifacts—history logs, download records, cookies, and cache files—as empirical evidence in a scientific investigation. Its purpose is to reconstruct user actions, detect the download of attack tools, identify navigation to command-and-control (C2) domains, and correlate these findings with network activity logs. The module operates as a deterministic system: every quantitative value is stored as an exact rational number (`Fraction`) or as its string representation, never as an imprecise floating-point approximation. This guarantees that repeated analyses of identical data produce bit-for-bit identical results.

### Key Concepts

| Name | Type | Scientific Role |
|---|---|---|
| `BrowserDownloadRecord` | Data Template | A single file-download event: timestamp, origin URL, local path, cryptographic hash. Analogous to a specimen label in a physical laboratory. |
| `BrowserHistoryRecord` | Data Template | A single URL-visit event: timestamp, page title, navigation type. Analogous to a chronological entry in a field notebook. |
| `BrowserAnalysisResult` | Data Container | The final aggregated report. Holds correlated events, reliability metrics (as exact fractions), and interpretive conclusions. |
| `BrowserForensicsEngine` | Analytical Instrument | The main apparatus. Accepts a browser user profile (Chrome, Edge, or Firefox) and executes a systematic examination. |

| Name | Type | Scientific Role |
|---|---|---|
| `to_signal()` | Conversion Procedure | Normalizes a raw browser entry into a standardized evidence signal. Like converting an analog sensor voltage into a calibrated digital reading. |
| `analyze_profile()` | Pipeline Procedure | Runs the full analytical workflow on a browser profile directory. Outputs a `BrowserAnalysisResult`. |

| Name | Type | Scientific Role |
|---|---|---|
| `TOOL_NAME` | Identifier String | Name tag for the engine instance, ensuring traceability in multi-instrument workflows. |
| `ARTIFACT_RELIABILITY` | Reliability Matrix | Coded reference table indicating the level of trust assigned to each source category. |
| `MALICIOUS_DOMAINS` | Reference Set | Deterministic lookup table of known hostile hostnames. |
| `SUSPICIOUS_EXTENSIONS` | Reference Set | Deterministic lookup table of file extensions commonly associated with attack tools. |

### Deterministic Arithmetic
All numerical values placed into the evidence dictionary use exact rational arithmetic (`Fraction` objects or their string equivalents). Timestamps, ratios, and reliability scores are therefore represented as pairs of integers (numerator/denominator). This approach eliminates the irreproducibility inherent to floating-point approximations and is scientifically equivalent to retaining all measurements in exact rational form until final reporting.

### Glossary
- **Browser Profile:** A directory containing all user-specific data for a given
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
