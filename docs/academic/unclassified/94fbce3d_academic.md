<!--
VIGIA Academic Documentation
Module: 94fbce3d
Batch ID: vigia-doc-0073-94fbce3d
Generated: 2026-05-20T14:56:47.860260+00:00
-->

---

## ENGLISH

### What Is This Module?

This module is a deterministic forensic analysis engine that detects meaningful patterns inside digital artifacts—such as log entries, file fragments, or memory strings—using concepts from formal semiotics. It treats an artifact as a structured signal and interrogates it through exact matching, approximate (fuzzy) matching, combinatorial reinforcement (synergy), and time-ordered logic (sequences). All scores are computed as integer ratios (numerator ÷ denominator), guaranteeing that every execution on the same input produces bit-identical results. It does not use machine learning, statistical inference, or floating-point mathematics.

### Key Concepts

#### Core Components
| Component | Role | Deterministic Guarantee |
|---|---|---|
| **PatternMatch** | Records a single pattern hit, including its position, investigative phase, and score | Score stored as an integer pair (numerator, denominator) |
| **SynergyEvent** | Logs when two or more patterns reinforce each other | Triggered solely by predefined integer logic in `SYNERGY_RULES` |
| **SequenceEvent** | Captures ordered chains of patterns across time | Evaluated through integer timestamp windows |
| **SessionPatternMemory** | Retains recent pattern history within a bounded temporal span | State changes are rule-governed, never probabilistic |
| **SemioticDetectorV2** | Master engine that orchestrates regex, fuzzy, synergy, sequence, and Forensic Signal Vector (FSV) assembly | All internal scoring uses rational integer arithmetic; zero floating-point logic |

#### Analysis Pipeline
| Stage | Mechanism | Arithmetic Type |
|---|---|---|
| Regex matching | Exact alignment of patterns against artifact strings | Integer index positions |
| Fuzzy matching | N-gram tokenization + bounded Levenshtein distance | Integer distance ≤ `MAX_LEVENSHTEIN` |
| Synergy analysis | Intersection check against `SYNERGY_RULES` | Integer counters |
| Sequence check | Ordered pattern validation inside `WINDOW_SIZE` | Integer temporal logic |
| FSV assembly | Composition of all preceding stage outputs into a unified vector | Integer component vectors |

#### Rational Configuration Constants
| Constant | Purpose | Integer Form |
|---|---|---|
| `NGRAM_SIZE` | Token length for fuzzy alignment | Integer count |
| `SIMILARITY_THRESHOLD_NUM` / `_DEN` | Minimum required similarity score | Rational fraction (numerator ÷ denominator) |
| `MAX_LEVENSHTEIN` | Maximum allowable edit distance | Integer bound |
| `WINDOW_SIZE` | Co-occurrence observation frame | Integer count |
| `TEMPORAL_SPAN` | Session memory limit | Integer time units (seconds/ticks) |
| `SYNERGY_RULES` | Combinatorial reinforcement definitions | Immutable integer rule set |
| `PATTERN_TO_PHASE` | Maps raw patterns to investigative phases | Deterministic dictionary mapping |
| `SEQUENCE_RULES` | Valid pattern orderings | Ordered integer rule set |

### Glossary

| Term | Definition |
|---|---|
| **Semiotics** | The formal study of signs, symbols, and their interpretation. Here it supplies the logical taxonomy for pattern classification. |
| **Forensic Signal Vector (FSV)** | A deterministic, integer-based composite descriptor that summarizes all detected signs within a single artifact. |
| **Rational arithmetic** | Calculation strictly with ratios of integers (numerator/denominator), eliminating the reproducibility hazards of floating-point representations. |
| **N-gram** | A contiguous sequence of *n* items extracted from a text string; used here for fuzzy matching. |
| **Levenshtein distance** | The minimum number of single-character insertions, deletions, or substitutions required to transform one string into another. |
| **Synergy** | A deterministic reinforcement effect—additive or multiplicative—when correlated patterns co-occur within the same window. |
| **Temporal memory** | A bounded buffer that retains recent pattern occurrences so that sequence rules can be evaluated. |
| **Artifact** | Any digital object under examination (e.g., a log line, a memory fragment, a file segment). |

### 【Scientific Note】

> This module employs terminology derived from **Charles Sanders Peirce**, **Umberto Eco**, and **H. P. Grice**. These names refer to formal logical frameworks for sign classification and communicative coherence, not to metaphysical doctrines. Think of the detector as a sensor array: Peirce’s triad provides the *wavelength channels*, Eco’s codes provide the *spectral calibration curves*, and Grice’s maxims provide the *noise-rejection thresholds*. The module does not “interpret meaning” in a human sense; it applies deterministic integer filters to forensic artifacts, producing reproducible vectors. The semiotic vocabulary is merely the taxonomy printed on the instrument panel.

---

## ESPAÑOL

### ¿Qué es este módulo?

Este módulo es un motor de análisis forense determinista que detecta patrones significativos dentro de artefactos digitales—como entradas de registro, fragmentos de archivos o cadenas en memoria—utilizando conceptos de la semiótica formal. Trata un artefacto como una señal estructurada y lo interroga mediante coincidencia exacta, coincidencia aproximada (*fuzzy*), refuerzo combinatorio (sinergia) y lógica temporal (secuencias). Todas las puntuaciones se computan como razones de enteros (numerador ÷ denominador), garantizando que cada ejecución sobre la misma entrada produzca resultados idénticos a nivel de bits. No utiliza aprendizaje automático, inferencia estadística ni matemática de punto flotante.

### Conceptos clave

#### Componentes principales
| Componente | Función | Garantía determinista |
|---|---|---|
| **PatternMatch** | Registra un único acierto de patrón, incluyendo posición, fase investigativa y puntuación | La puntuación se almacena como par de enteros (numerador, denominador) |
| **SynergyEvent** | Registra cuando dos o más patrones se refuerzan mutuamente | Se activa únicamente por la lógica entera predefinida en `SYNERGY_RULES` |
| **SequenceEvent** | Captura cadenas ordenadas de patrones a través del tiempo | Se evalúa mediante ventanas de marcas temporales enteras |
| **SessionPatternMemory** | Conserva el historial reciente de patrones dentro de un lapso temporal acotado | Los cambios de estado obedecen a reglas, nunca a probabilidades |
| **SemioticDetectorV2** | Motor principal que orquesta regex, *fuzzy*, sinergia, secuencia y ensamblaje del Vector de Señal Forense (FSV) | Toda puntuación interna usa aritmética racional entera; cero lógica de punto flotante |

#### Tubería de análisis
| Etapa | Mecanismo | Tipo de aritmética |
|---|---|---|
| Coincidencia regex | Alineación exacta de patrones contra cadenas del artefacto | Posiciones de índice enteras |
| Coincidencia *fuzzy* | Tokenización por n-gramas + distancia de Levenshtein acotada | Distancia entera ≤ `MAX_LEVENSHTEIN` |
| Análisis de sinergia | Verificación de intersección contra `SYNERGY_RULES` | Contadores enteros |
| Verificación de secuencias | Validación ordenada de patrones dentro de `WINDOW_SIZE` | Lógica temporal entera |
| Ensamblaje de FSV | Composición de las salidas de todas las etapas previas en un vector unificado | Vectores de componentes enteras |

#### Constantes de configuración racional
| Constante | Propósito | Forma entera |
|---|---|---|
| `NGRAM_SIZE` | Longitud de token para alineamiento *fuzzy* | Cuenta entera |
| `SIMIL
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
