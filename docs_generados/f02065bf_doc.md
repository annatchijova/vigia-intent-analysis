<!--
VIGIA Academic Documentation
Module: f02065bf
Batch ID: vigia-doc-0173-f02065bf
Generated: 2026-05-20T14:56:47.882087+00:00
-->

# Module Documentation: `vigia/tools/temporal_drift.py`

---

## ENGLISH

### What Is This Module?
The **Temporal Drift Detector** (`vigia/tools/temporal_drift.py`) is a deterministic forensic engine that examines sequences of timestamps extracted from digital artifacts. Its purpose is to reveal evidence tampering by identifying logically impossible chronologies—for example, a file modified before it was created, or an email sent in the future. The module treats time as a discrete, ordered set of integer values. All comparisons use deterministic integer arithmetic on whole seconds, ensuring exact reproducibility without fractional approximation.

### Key Concepts

**Core Classes**

| Class | Role | Plain-Language Description |
|-------|------|----------------------------|
| `TemporalEvent` | Data container | Represents one timestamped occurrence (e.g., file creation). Stores time as integer seconds since epoch. |
| `TemporalAnalysis` | Result object | Holds the outcome of a sequence check: consistent, anomalous, or impossible. |
| `TemporalDriftDetector` | Engine | Orchestrates the comparison of events using deterministic integer thresholds. |
| `TimestampExtractor` | Utility | Retrieves raw timestamp integers from artifact headers (PDF, email, etc.). |

**Analysis Functions**

| Function | Input | Output | Purpose |
|----------|-------|--------|---------|
| `analyze()` | List of `TemporalEvent` | `TemporalAnalysis` | Sequentially validates integer timestamps against logical order. |
| `extract_from_pdf()` | PDF artifact bytes | Integer timestamp | Reads creation/modification dates from PDF metadata as whole seconds. |
| `extract_from_email()` | Email header string | Integer timestamp | Parses sent/received dates from headers into integer epoch time. |

**Deterministic Thresholds (Constants)**

| Constant | Type | Forensic Meaning |
|----------|------|------------------|
| `MAX_CREATION_TO_SEND` | Integer (seconds) | Maximum plausible delay between file creation and transmission. |
| `MAX_MODIFY_TO_SEND` | Integer (seconds) | Maximum plausible delay between last modification and sending. |
| `MAX_FUTURE_TOLERANCE` | Integer (seconds) | Small integer buffer allowed versus system clock to account for benign skew; values beyond this indicate tampering. |
| `MIN_TIMEZONE_GAP_HOURS` | Integer (hours) | Minimum offset difference deemed suspicious when artifacts cross time zones without logical justification. |

### Glossary

- **Epoch time**: A universal integer count of seconds elapsed since a fixed reference date (1970-01-01 00:00:00 UTC), used to avoid time zone and calendar parsing ambiguity.
- **Deterministic integer arithmetic**: Mathematical operations on whole numbers that always yield the exact same result, with no approximation. Critical for reproducible forensic conclusions.
- **Temporal inconsistency**: A logical contradiction in timestamps (e.g., modification preceding creation) that cannot occur under normal system behavior and therefore indicates artifact manipulation.
- **Artifact**: Any digital object carrying potential evidence (files, emails, log entries).
- **Timestamp extraction**: The process of reading a raw temporal value from an artifact's metadata without interpreting or altering it.

### 【Scientific Note】
This module’s architecture employs semiotic concepts—Peirce’s theory of signs, Eco’s cultural codes, and Grice’s conversational maxims. These terms are **not** mysticism or literary criticism. They function as a formal **sensor model**: just as a physical sensor converts a stimulus (light, pressure) into a structured electrical signal, this detector converts raw timestamp traces (Peircean signs) into interpretable states via deterministic rules (Eco’s codes) and logical expectations (Grice’s maxims). A temporal inconsistency is simply a signal that violates the expected code, triggering an alert. The terminology describes an information-processing layer, not an esoteric belief system.

---

## ESPAÑOL

### ¿Qué es este módulo?
El **Detector de Deriva Temporal** (`vigia/tools/temporal_drift.py`) es un motor forense determinista que examina secuencias de marcas temporales extraídas de artefactos digitales. Su objetivo es revelar la manipulación de evidencia identificando cronologías lógicamente imposibles—por ejemplo, un archivo modificado antes de ser creado, o un correo enviado en el futuro. El módulo trata el tiempo como un conjunto discreto y ordenado de valores enteros. Todas las comparaciones utilizan aritmética entera determinista sobre segundos completos, garantizando reproducibilidad exacta sin aproximación fraccionaria.

### Conceptos clave

**Clases principales**

| Clase | Rol | Descripción |
|-------|-----|-------------|
| `TemporalEvent` | Contenedor de datos | Representa una ocurrencia con marca temporal. Almacena el tiempo como enteros de segundos desde la época. |
| `TemporalAnalysis` | Objeto de resultado | Contiene el resultado de la verificación: consistente, anómalo o imposible. |
| `TemporalDriftDetector` | Motor | Orquesta la comparación de eventos usando umbrales enteros deterministas. |
| `TimestampExtractor` | Utilidad | Recupera valores enteros de marcas temporales de encabezados (PDF, correo, etc.). |

**Funciones de análisis**

| Función | Entrada | Salida | Propósito |
|---------|---------|--------|-----------|
| `analyze()` | Lista de `TemporalEvent` | `TemporalAnalysis` | Valida secuencialmente marcas temporales enteras contra el orden lógico. |
| `extract_from_pdf()` | Bytes del artefacto PDF | Marca temporal entera | Lee fechas de creación/modificación de metadatos PDF en segundos enteros. |
| `extract_from_email()` | Cadena de encabezado de correo | Marca temporal entera | Analiza fechas de envío/recepción de encabezados a tiempo época entero. |

**Umbrales deterministas (Constantes)**

| Constante | Tipo | Significado forense |
|-----------|------|---------------------|
| `MAX_CREATION_TO_SEND` | Entero (segundos) | Retraso máximo plausible entre creación y transmisión. |
| `MAX_MODIFY_TO_SEND` | Entero (segundos) | Retraso máximo plausible entre última modificación y envío. |
| `MAX_FUTURE_TOLERANCE` | Entero (segundos) | Pequeño margen ent
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
