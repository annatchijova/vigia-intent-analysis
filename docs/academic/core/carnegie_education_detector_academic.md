<!--
VIGIA Academic Documentation
Module: 9ae17aea
Batch ID: vigia-doc-0041-9ae17aea
Generated: 2026-05-20T14:56:47.853267+00:00
-->

## ENGLISH

### What Is This Module?
The module located at `vigia/core/carnegie_education_detector.py` is a **forensic instrument**, not a chat filter. It is **not** a chat-prompt filter and it does **not** replace LLMShield. It examines **textual forensic artifacts** (digital evidence such as logs, prompts, transcripts, or documents) to expose a specific deception pattern known as the **Carnegie education frame**. In this pattern, harmful or illicit content is camouflaged by wrapping it in apparently instructional language—tutorials, training scenarios, learning exercises, or pedagogical role-play. The module treats every artifact as a **semiotic object** (a structured system of signs) and searches for structural forgeries: measurable mismatches between the surface “educational” code and the underlying intent. All scoring, counting, and threshold decisions rely exclusively on **deterministic integer arithmetic**; no floating-point approximations are used, guaranteeing that identical artifacts always produce identical results on any hardware.

### Key Concepts

| Term | Definition | Role in the Module |
|------|------------|-------------------|
| **Carnegie Education Frame** | A rhetorical disguise that presents harmful content as instructional material (e.g., *“Imagine you are teaching a course on…”*). | The primary target pattern. The detector searches for lexical and structural markers of this frame inside evidence. |
| **Semiotic Forgery** | The deliberate manipulation of signs and cultural codes to make an object appear to mean something it does not. | The conceptual model. The module detects forgeries by analyzing how signs are assembled within the artifact. |
| **Forensic Text Artifact** | Any piece of digital text collected as evidence during an investigation. | The input object. The analysis operation (`analyze()`) accepts these artifacts. |
| **Signal** | A discrete record of one detected anomaly, storing integer coordinates and integer severity levels. | The output unit. The component `CarnegieEducationSignal` stores each detected frame instance. |
| **Detector** | The analytical engine that processes artifacts and emits Signals. | The core instrument. The component `CarnegieEducationDetector` performs the full analysis pipeline. |
| **Deterministic Integer Arithmetic** | Exact whole-number calculations (addition, counting, integer scoring) without
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
