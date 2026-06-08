<!--
VIGIA Academic Documentation
Module: 8cf3f33e
Batch ID: vigia-doc-0119-8cf3f33e
Generated: 2026-05-20T14:56:47.870276+00:00
-->

---

## ENGLISH

### What Is This Module?
This module is a **deterministic comparator** for two separate executions (*runs*) of the VIGÍA forensic pipeline against the **same dataset**. It answers one question: *What exactly changed between Run A and Run B?* To do this, it parses the structured output of each run, computes exact differences using **integer arithmetic and irreducible rational fractions**, labels each change as an **IMPROVEMENT**, **REGRESSION**, or **VERDICT_SHIFT**, and flags candidate explanatory components via **heuristic (non-causal) driver detection**. It does **not** compute confusion-matrix statistics such as TP/FP/TN/FN; those are handled by `evaluate_detector.py`.

---

### Key Concepts

| Term | Meaning | Role in the Module |
|------|---------|-------------------|
| **Deterministic Comparator** | A system that yields identical outputs from identical inputs with no stochastic steps | Guarantees bitwise reproducibility of conclusions |
| **Irreducible Rational Fraction** | A ratio of two integers reduced to lowest terms (e.g., `3/7`, never `0.428…`) | Produces court-admissible exact deltas under the Daubert standard |
| **Heuristic Driver Detection** | Non-causal identification of components that *likely* accompany a change | Surfaces suspects, not proven causes |
| **Verdict Shift** | Any change in the final classification or outcome label between two runs | Critical label for downstream review |
| **Deterministic Forensic Hash** | An integer fingerprint of a digital artifact, free of floating-point representation | Ensures integrity checks remain inside integer space |
| **Integer Decision Logic** | All branching, thresholds, and labels rely on integer or fraction arithmetic | Eliminates rounding-induced non-determinism |
| **Logical Fracture** | A non-causal break in expected logical continuity between two runs | Detected by the heuristic engine to flag anomalous transitions |

---

### Classes

| Class | Purpose |
|-------|---------|
| `PipelineResult` | Immutable container for one pipeline run’s outputs; parses the run manifest into structured, typed fields |
| `IntentDelta` | Encodes the exact difference between two matched intent objects across runs, expressed as integer deltas |
| `ComparisonResult` | Aggregates all deltas, assigns outcome labels (`IMPROVEMENT` / `REGRESSION` / `VERDICT_SHIFT`), and stores heuristic driver candidates |

---

### Functions

| Function | Purpose |
|----------|---------|
| `hash_forensic()` | Computes a deterministic integer hash of a forensic artifact; used for integrity verification |
| `load_run()` | Reads a run directory and assembles a `PipelineResult` using only structured text and integer parsing |
| `compare_artifact()` | Performs pairwise comparison of two artifacts, returning an irreducible rational delta where applicable |
| `print_table()` | Renders a comparison matrix to the terminal for human inspection |
| `print_diff()` | Emits a line-oriented diff of textual forensic outputs |
| `compute_meta_metrics()` | Calculates summary statistics over the comparison using integer rational arithmetic |
| `export_csv()` | Writes comparison results to a comma-separated file for external audit |
| `main()` | Entry point; orchestrates loading, comparison, labeling, and output generation |

---

### Constants & Configuration

| Constant | Meaning |
|----------|---------|
| `REQUIRED_KEYS` | Mandatory manifest fields that must be present for a run to qualify for comparison |
| `COMPONENT_KEYS` | Subsystem identifiers whose values are exposed to heuristic driver detection |
| `MI_KEYS` | Mutual-information / message-intent keys tracked for semantic comparison |
| `LEVEL_ORDER` | Hierarchical precedence used when resolving conflicting labels during aggregation |

---

### Glossary

- **Deterministic** — Producing the same result every time from the same initial conditions; devoid of randomness.
- **Irreducible Fraction** — A rational number *a/b* where the numerator and denominator share no common divisor other than 1.
- **Heuristic** — A practical rule or pattern for discovery, not proof of causation.
- **Daubert Standard** — Legal criterion for admissible scientific evidence requiring known reliability and error rates.
- **Forensic Artifact** — Any digital object offered as evidence (file, log, memory dump).
- **Regression** — A change that degrades performance or accuracy relative to a baseline.
- **Non-causal** — Describing correlation or co-occurrence without established cause-and-effect.
- **Verdict Shift** — Any alteration in the final outcome label between two runs.
- **Logical Fracture** — A non-causal discontinuity in the expected logical chain between two pipeline executions.

---

> 【Scientific Note】
> This module borrows terminology from semiotics (Peirce), interpretive theory (Umberto Eco), and pragmatics (Grice). These names are **not mysticism**. Treat them as **sensor ontologies**: Peirce’s categories classify *how* a detection signal relates to an object (icon, index, symbol); Eco’s framework specifies *how* meaning is negotiated between the detection system and its context; Grice’s maxims define *expected cooperativity* in message exchange between pipeline stages. Just as a physicist does not treat a voltmeter as magic, a forensic scientist should not treat semiotic vocabulary as occult—it is a structured language for describing information flow inside deterministic measurement systems.

---

## ESPAÑOL

### ¿Qué es este módulo?
Este módulo es un **comparador determinista** entre dos ejecuciones (*runs*) del pipeline forense VIGÍA sobre el **mismo conjunto de datos**. Responde a una pregunta: *¿Qué cambió exactamente entre la Ejecución A y la Ejecución B?* Para ello, analiza la salida estructurada de cada ejecución, calcula diferencias exactas mediante **aritmética entera y fracciones racionales irreducibles**, etiqueta cada cambio como **MEJORA**, **REGRESIÓN** o **CAMBIO_DE_VEREDICTO**, y señala componentes candidatos explicativos mediante la **detección heurística de drivers (no causal)**. **No** calcula estadísticas de matriz de confusión (TP/FP/TN/FN); eso corresponde a `evaluate_detector.py`.

---

### Conceptos clave

| Término | Significado | Rol en el módulo |
|---------|-------------|------------------|
| **Comparador determinista** | Sistema que produce la misma salida ante las mismas entradas, sin pasos estocásticos | Garantiza reproducibilidad bit a bit |
| **Fracción racional irreducible** | Cociente de dos enteros reducido a mínima expresión (p. ej., `3/7`, nunca `0,428…`) | Asegura deltas exactos, admisibles bajo el estándar Daubert |
| **Detección heurística de drivers** | Identificación no causal de componentes que *probablemente* acompañan un cambio | Señala sospechosos, no causas probadas |
| **Cambio de veredicto** | Cualquier variación en la clasificación o decisión final entre dos ejecuciones | Etiqueta crítica para revisión posterior |
| **Hash forense determinista** | Huella dactilar entera de un artefacto digital, libre de representación en punto flotante | Garantiza que la integridad se verifica en espacio entero |
| **Lógica de decisión entera** | Todas las ram
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
