<!--
VIGIA Academic Documentation
Module: be71e68a
Batch ID: vigia-doc-0105-be71e68a
Generated: 2026-05-20T14:56:47.867430+00:00
-->

---

# ENGLISH

## What Is This Module?

The **Cross-Case Pattern Library (CCPL)** is a deterministic forensic knowledge base. It operates as an exact-matching engine that compares active investigative signals—discrete textual indicators such as log entries, registry keys, or file signatures—against a curated collection of documented attack patterns. These patterns are derived from MITRE ATT&CK® Enterprise v14, public Cyber Threat Intelligence (CTI), and landmark incidents (e.g., SolarWinds).

The module does not employ probabilistic classifiers, neural networks, or floating-point thresholds. Instead, it uses pure set algebra: a pattern matches **if and only if** its defined set of required signals is a subset of the active signal set. Every pattern and every match is **immutable**; once recorded, it
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
