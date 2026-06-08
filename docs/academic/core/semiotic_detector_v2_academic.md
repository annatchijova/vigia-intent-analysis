<!--
VIGIA Academic Documentation
Module: b32a18e2
Batch ID: vigia-doc-0074-b32a18e2
Generated: 2026-05-20T14:56:47.860448+00:00
-->

## ENGLISH
### What Is This Module?
...
### Key Concepts
...
### Architecture Overview
...
### Deterministic Integer Arithmetic
...
### Constants & Configuration
...
### Glossary
...
> 【Scientific Note】
> ...

## ESPAÑOL
### ¿Qué es este módulo?
...
(similar structure)

## РУССКИЙ
### Что представляет собой этот модуль?
...

## 中文
### 本模块是什么？
...

---

```

Also, the user said "do NOT use floating-point math explanations — emphasize deterministic integer arithmetic where applicable". So I should phrase everything positively around integer/rational.

Let's refine the text for each section to be thorough but concise.

**ENGLISH Section details:**

What Is This Module?
The `vigia/core/semiotic_detector_v2.py` module implements the Semiotic Detector v2.2, a deterministic forensic analysis engine for textual artifacts. It treats digital evidence as a signal stream that can be inspected through formal sign-relations. The detector executes a fixed pipeline: regular expression matching, fuzzy n-gram comparison, synergy detection, sequence validation, and Forensic Signal Vector (FSV) synthesis. It incorporates five critical hardening fixes from the VIGÍA Collective, including strict rational scoring, real TTL memory management, and structured collision logging.

Key Concepts table:
| Concept | Role in Analysis |
|---------|------------------|
| `PatternMatch` | Atomic detection unit storing pattern ID, position, and raw integer score. |
| `SynergyEvent` | Composite alert triggered when co-occurring patterns satisfy an interaction rule. |
| `SequenceEvent` | Higher-order alert requiring patterns to appear in a specific temporal order. |
| `SessionPatternMemory` | Context buffer with real TTL eviction and hard capacity caps; prevents unbounded growth. |
| `SemioticDetectorV2` | Controller class orchestrating the five-phase deterministic pipeline. |
| `analyze_artifact()` | Canonical public interface; accepts a forensic artifact and a `negation_enabled` flag. |

Architecture / Pipeline table:
| Phase | Method / Component | Description |
|-------|--------------------|-------------|
| 1. Regex Scan | Internal regex engine | Exact signature matching with integer timeout guards. |
| 2. Fuzzy Scan | Fuzzy config (5 patterns, 25 variants) | Approximate matching via n-grams and rational similarity thresholds (`NUM/DEN`). |
| 3. Synergy Analysis | `SynergyEvent` | Cross-reference matches against `SYNERGY_RULES` to detect combined threats. |
| 4. Sequence Check | `check_sequences()` | Validates ordered chains against `WINDOW_SIZE` and `TEMPORAL_SPAN`. |
| 5. FSV Synthesis | `analyze()` / `weight()` / `add()` | Aggregates integer sub-scores into a granular vector using `Fraction`. |

Deterministic Arithmetic:
All scoring operations inside `SemioticDetectorV2` use Python’s `fractions.Fraction`, representing every value as an exact ratio of two integers (numerator and denominator). There are no floating-point variables in the scoring path. This integer-only discipline guarantees that every forensic conclusion is bitwise identical across repeated executions and different hardware platforms.

Constants table:
| Constant | Function | Type |
|----------|----------|------|
| `NGRAM_SIZE` | Fuzzy token length | Positive integer |
| `SIMILARITY_THRESHOLD_NUM` | Threshold numerator | Integer |
| `SIMILARITY_THRESHOLD_DEN` | Threshold denominator | Non-zero integer |
| `WINDOW_SIZE` | Co-occurrence range | Positive integer |
| `TEMPORAL_SPAN` | Sequence validity limit | Positive integer |
| `TOP_K_MATCHES` | Match retention limit | Positive integer |
| `REGEX_TIMEOUT_SECONDS` | Execution safety bound | Positive integer |
| `MAX_TEXT_SIZE_BYTES` | Input size ceiling | Positive integer |
| `SYNERGY_RULES` | Interaction law table | Integer-structured mapping |
| `NEGATION_STRONG` | Negation polarity flag | Integer (0 or 1) |

Glossary:
- **Artifact**: A discrete object of digital evidence submitted for inspection (取证工件).
- **Deterministic Pipeline**: An analytical workflow where output is strictly entailed by input and configuration, excluding stochastic steps.
- **ECO_SEMIOTIC_COLLISION**: A structured field (`critical_patterns`) logging semiotic collisions per Eco (艾柯)—cases where pattern meanings structurally interfere.
- **Forensic Signal Vector (FSV)**: The final output structure decomposing the total score into rational components.
- **Fraction**: Python class for exact rational arithmetic; internally stores two integers.
- **Fuzzy Config**: The loaded `fuzzy_config.json` containing 5 base patterns and 25 variants.
- **Negation Handler**: A logical layer toggled by `negation_enabled` that inverts or suppresses scores when negation keywords are present.
- **TTL**: Time-to-live eviction policy coupled with a maximum count cap in `SessionPatternMemory`.

Scientific Note:
> 【Scientific Note】
> The references to Peirce, Eco (艾柯), and Grice (格赖斯) in this codebase are formal epistemological instruments, not mysticism. Think of them as the calibration vocabulary of a sensor: Peirce’s triad defines the states a sign-detector must distinguish (sign, object, interpretant); Eco’s semiotic threshold is realized as an exact rational cutoff (`SIMILARITY_THRESHOLD_NUM/DEN`); Grice’s conversational maxims become logical constraints on valid sequences. They provide a structured language for deterministic decision boundaries, analogous to wavelength specifications in a spectrometer.

**ESPAÑOL Section details:**
Mirror the English structure.

What Is This Module? -> ¿Qué es este módulo?
El módulo `vigia/core/semiotic_detector_v2.py` implementa el Detector Semiótico v2.2, un motor de análisis forense determinista para artefactos textuales. Trata la evidencia digital como una corriente de señales inspeccionable mediante relaciones de signos formales. El detector ejecuta un pipeline fijo: coincidencia regex, comparación fuzzy de n-gramas, detección de sinergia, validación de secuencias y síntesis del Vector de Señal Forense (FSV). Incorpora cinco correcciones críticas del Colectivo VIGÍA...

Key concepts table:
| Concepto | Rol en el Análisis |
|----------|-------------------|
| `PatternMatch` | Unidad atómica de detección que almacena ID de patrón, posición y puntaje entero crudo. |
| `SynergyEvent` | Alerta compuesta disparada cuando patrones coexistentes satisfacen una regla de interacción. |
| `SequenceEvent` | Alerta de orden superior que exige que los patrones aparezcan en un orden temporal específico. |
| `SessionPatternMemory` | Búfer de contexto con evacuación TTL real y límites duros de capacidad; evita crecimiento ilimitado. |
| `SemioticDetectorV2` | Clase controladora que orquesta el pipeline determinista de cinco fases. |
| `analyze_artifact()` | Interfaz pública canónica; acepta un artefacto forense y una bandera `negation_enabled`. |

Arquitectura / Pipeline:
| Fase | Método / Componente | Descripción |
|------|---------------------|-------------|
| 1. Escaneo Regex | Motor regex interno | Coincidencia exacta de firmas con guardas de tiempo de ejecución enteros. |
| 2. Escaneo Fuzzy | Config fuzzy (5 patrones, 25 variantes) | Coincidencia aproximada mediante n-gramas y umbrales de similitud racionales (`NUM/DEN`). |
| 3. Análisis de Sinergia | `SynergyEvent` | Referencia cruzada de coincidencias contra `SYNERGY_RULES` para detectar amenazas combinadas. |
| 4. Verificación de Secuencia | `check_sequences()` | Valida cadenas ordenadas contra `WINDOW_SIZE` y `TEMPORAL_SPAN`. |
| 5. Síntesis FSV | `analyze()` / `weight()` / `add()` | Agrega sub-puntajes enteros en un vector granular usando `Fraction`. |

Aritmética Determinista:
Todas las operaciones de puntuación dentro de `SemioticDetectorV2` utilizan `fractions.Fraction` de Python, representando cada valor como una razón exacta de dos enteros (numerador y denominador). No existen variables de punto flotante en la ruta de puntuación. Esta disciplina de solo-enteros garantiza que cada conclusión forense sea idéntica bit a bit entre ejecuciones repetidas y diferentes plataformas de hardware.

Tabla de Constantes:
| Constante | Función | Tipo |
|-----------|---------|------|
| `NGRAM_SIZE` | Longitud del token fuzzy | Entero positivo |
| `SIMILARITY_THRESHOLD_NUM` | Numerador del umbral | Entero |
| `SIMILARITY_THRESHOLD_DEN` | Denominador del umbral | Entero no cero |
| `WINDOW_SIZE` | Rango de co-ocurrencia | Entero positivo |
| `TEMPORAL_SPAN` | Límite de validez de secuencia | Entero positivo |
| `TOP_K_MATCHES` | Límite de retención de coincidencias | Entero positivo |
| `REGEX_TIMEOUT_SECONDS` | Cota de seguridad de ejecución | Entero positivo |
| `MAX_TEXT_SIZE_BYTES` | Tope de tamaño de entrada | Entero positivo |
| `SYNERGY_RULES` | Tabla de leyes de interacción | Mapeo estructurado con enteros |
| `NEGATION_STRONG` | Bandera de polaridad de negación | Entero (0 o 1) |

Glosario:
- **Artefacto**: Objeto discreto de evidencia digital sometido a inspección (取证工件).
- **Pipeline Determinista**: Flujo de trabajo analítico donde la salida está estrictamente implicada por la entrada y la configuración, excluyendo pasos estocásticos.
- **ECO_SEMIOTIC_COLLISION**: Campo estructurado (`critical_patterns`) que registra colisiones semióticas según Eco (艾柯)—casos donde los significados de los patrones interfieren estructuralmente.
- **Vector de Señal Forense (FSV)**: Estructura de salida final que descompone el puntaje total en componentes racionales.
- **Fraction**: Clase de Python para aritmética racional exacta; almacena internamente dos enteros.
- **Config Fuzzy**: El `fuzzy_config.json` cargado que contiene 5 patrones base y 25 variantes.
- **Manejador de Negación**: Capa lógica activada por `negation_enabled` que invierte o suprime puntajes cuando se detectan palabras clave de negación.
- **TTL**: Política de evacuación por tiempo de vida acoplada a un límite máximo de cantidad en `SessionPatternMemory`.

Nota Científica:
> 【Nota Científica】
> Las referencias a Peirce, Eco (艾柯) y Grice (格赖斯) en este código son instrumentos epistemológicos formales, no misticismo. Piense en ellos como el vocabulario de calibración de un sensor: la tríada de Peirce define los estados que un detector de signos debe distinguir (signo, objeto, interpretante); el umbral semiótico de Eco se realiza como un corte racional exacto (`SIMILARITY_THRESHOLD_NUM/_DEN`); las máximas conversacionales de Grice se convierten en restricciones lógicas sobre secuencias válidas. Proporcionan un lenguaje estructurado para límites de decisión deterministas, análogo a las especificaciones de longitud de onda en un espectrómetro.

**РУССКИЙ Section details:**
Mirror.

Что представляет собой этот модуль?
Модуль `vigia/core/semiotic_detector_v2.py` реализует Семиотический Детектор v2.2 — детерминистский судебно-экспертный аналитический движок для текстовых артефактов. Он рассматривает цифровые доказательства как поток сигналов, поддающийся инспекции через формальные отношения знаков. Детектор выполняет фиксированный конвейер: сопоставление регулярных выражений, нечёткое сравнение n-грамм, обнаружение синергии, проверку последовательностей и синтез Судебного Сигнального Вектора (FSV). Он включает пять критических исправлений коллектива VIGÍA...

Key concepts table:
| Концепция | Роль в Анализе |
|-----------|----------------|
| `PatternMatch` | Атомарная единица обнаружения, хранящая ID шаблона, позицию и сырые целочисленные баллы. |
| `SynergyEvent` | Составное оповещение, запускаемое при совместном появлении шаблонов, удовлетворяющих правилу взаимодействия. |
| `SequenceEvent` | Оповещение высшего порядка, требующее, чтобы шаблоны следовали в определённом временном порядке. |
| `SessionPatternMemory` | Контекстный буфер с реальным TTL-удалением и жёсткими
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
