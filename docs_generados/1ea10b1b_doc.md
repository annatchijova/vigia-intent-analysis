<!--
VIGIA Academic Documentation
Module: 1ea10b1b
Batch ID: vigia-doc-0046-1ea10b1b
Generated: 2026-05-20T14:56:47.854418+00:00
-->

# Module Documentation: `vigia/core/decision_layer.py`

---

## ENGLISH

### What Is This Module?

This document describes the final decision gate of the **VIGÍA** analytical pipeline. Think of it as a **calibrated referee** that receives a single, aggregated numerical score (the Manipulation Index, MI) from upstream forensic stages and translates it into a discrete risk label. It does not generate new evidence; it only interprets what has already been measured.

The module is **deterministic**: given the same inputs, it will always produce the same output. It operates exclusively with **exact integer ratios** (fractions), avoiding the rounding errors inherent in decimal approximations. There are no hidden bonuses, heuristic adjustments, or random elements—only versioned, auditable thresholds.

### Key Concepts

| Concept | Role in the System | Scientific Meaning |
|---|---|---|
| **RiskBoundedDecisionLayer** | The final classification stage | A deterministic state machine with four alert levels (LOW → MEDIUM → HIGH → CRITICAL) |
| **MI / Manipulation Index** | Primary input signal | An aggregated scalar representing semantic distortion detected across the forensic artifact |
| **FSV / Forensic Semantic Vector** | Structured input container | The bundle carrying the manipulation index and critical flags from previous pipeline stages |
| **Decision Interface** (`decide` / `decide_verdict`) | External access points | The deterministic procedures that ingest the aggregated FSV and emit the risk label |
| **Thresholds** (LOW, MEDIUM, HIGH) | Decision boundaries | Exact fractional cutoffs, versioned and auditable |
| **ECO_SEMIOTIC_COLLISION** | Override flag | A condition that automatically forces the highest alert level (CRITICAL), regardless of the MI score |
| **Exact Fractions** | Internal arithmetic | Integer numerator/denominator math ensuring perfectly reproducible comparisons |

### Glossary of Technical Terms

- **Aggregated FSV**: The consolidated output from previous pipeline stages, containing the final manipulation index and any critical pattern flags.
- **Deterministic Verdict**: A classification result that is fully predictable and reproducible from the input data, with no randomness.
- **ECO_SEMIOTIC_COLLISION**: A pattern indicating a fundamental contradiction in the semiotic structure of the artifact. In this system, it acts as a hard override to CRITICAL.
- **Forensic Artifact**: Any digital object under analysis (e.g., a document, image, or log file).
- **Manipulation Index (MI)**: A quantitative measure of detected semantic or structural manipulation.
- **Threshold**: A predefined boundary value that separates one risk level from another.
- **VIGÍA**: The name of the overall analytical framework.

> 【Scientific Note】
> The module references semioticians **Charles Sanders Peirce**, **Umberto Eco**, and philosopher **H. P. Grice**. These names denote formal models of sign-processes and communication protocols—not mysticism. Think of them as you would think of "Ohm" in electrical resistance or "Newton" in mechanics: they are labels for rigorously defined scientific constructs. In this pipeline, "Eco-semiotic collision" behaves like a physical sensor trip-wire: when the symbolic code structure of an artifact self-contradicts in a way predicted by Eco’s theory of code coherence, the sensor fires. It is an engineering rule, not a literary opinion.

---

## ESPAÑOL

### ¿Qué es este módulo?

Este documento describe la **puerta de decisión final** de la tubería analítica **VIGÍA**. Piense en ello como un **árbitro calibrado** que recibe una puntuación numérica agregada (el Índice de Manipulación, MI) de las etapas forenses previas y la traduce en una etiqueta de riesgo discreta. No genera nueva evidencia; solo interpreta lo que ya se ha medido.

El módulo es **determinista**: ante las mismas entradas, siempre producirá la misma salida. Opera exclusivamente con **fracciones exactas** (razones enteras), evitando los errores de redondeo propios de las aproximaciones decimales. No existen bonificaciones ocultas, ajustes heurísticos ni elementos aleatorios—solo umbrales versionados y auditables.

### Conceptos Clave

| Concepto | Rol en el Sistema | Significado Científico |
|---|---|---|
| **RiskBoundedDecisionLayer** | Etapa de clasificación final | Máquina de estados determinista con cuatro niveles de alerta (LOW → MEDIUM → HIGH → CRITICAL) |
| **MI / Índice de Manipulación** | Señal de entrada principal | Escalar agregado que representa la distorsión semántica detectada en el artefacto forense |
| **FSV / Vector Semántico Forense** | Contenedor de entrada estructurado | Paquete que transporta el índice de manipulación y las banderas críticas desde etapas previas |
| **Interfaz de Decisión** (`decide` / `decide_verdict`) | Puntos de acceso externos | Procedimientos deterministas que ingieren el FSV agregado y emiten la etiqueta de riesgo |
| **Umbrales** (LOW, MEDIUM, HIGH) | Límites de decisión | Cortes fraccionarios exactos, versionados y auditables |
| **ECO_SEMIOTIC_COLLISION** | Indicador de anulación | Condición que fuerza automáticamente el nivel más alto (CRITICAL), independientemente de la puntuación MI |
| **Fracciones Exactas** | Aritmética interna | Matemática de numerador/denominador entero que garantiza comparaciones perfectamente reproducibles |

### Glosario de Términos Técnicos

- **Artefacto Forense**: Cualquier objeto digital bajo análisis (p. ej., un documento, imagen o archivo de registro).
- **Determinista**: Un resultado que es completamente predecible y reproducible a partir de los datos de entrada, sin aleatoriedad.
- **ECO_SEMIOTIC_COLLISION**: Un patrón que indica una contradicción fundamental en la estructura semiótica del artefacto, nombrado en referencia a la teoría de los códigos de Umberto Eco. En este sistema, actúa como una anulación forzosa a CRITICAL.
- **FSV Agregado**: La salida consolidada de etapas previas de la tubería, que contiene el índice de manipulación final y cualquier bandera de patrón crítico.
- **Índice de Manipulación (MI)**: Medida cuantitativa de la manipulación semántica o estructural detectada.
- **Umbral**: Valor límite predefinido que separa un nivel de riesgo de otro.
- **VIGÍA**: Nombre del marco analítico integral.

> 【Nota Científica】
> Este módulo hace referencia a los semióticos **Charles Sanders Peirce** y **Umberto Eco**, así como al filósofo **H. P. Grice**. Estos nombres designan modelos formales de procesos de signos y protocolos de comunicación —no misticismo. Piense en ellos como piensa en «Ohm» en resistencia eléctrica o «Newton» en mecánica: son etiquetas para construcciones científicas rigurosamente definidas. En esta tubería, la «colisión eco-semiótica» se comporta como un cable de detección físico: cuando la estructura de código simbólica de un artefacto se autocontradice de una manera predicha por la teoría de la coherencia de códigos de Eco, el sensor se dispara. Es una regla de ingeniería, no una opinión literaria.

---

## РУССКИЙ

### Что это за модуль?

Настоящий документ описывает **финальное решающее звено** аналитического конвейера **VIGÍA**. Воспринимайте его как **калиброванного арбитра**, который получает от предыдущих судебно-экспертных этапов единое агрегированное числовое значение (Индекс Манипуляции, MI) и преобразует его в дискретную метку риска. Он не создаёт новых доказательств; он лишь интерпретирует уже измеренные данные.

Модуль **детерминирован**: при одинаковых входных данных он всегда выдаёт одинаковый результат. Вычисления выполняются исключительно с помощью **точных дробей** (отношений целых чисел), что исключает ошибки округления, присущие десятичным приближениям. Здесь нет скрытых надбавок, эвристических поправок или случайных элементов — только версионируемые и подлежащие аудиту пороги.

### Ключевые концепции

| Концепция | Роль в системе | Научное значение |
|---|---|---|
| **RiskBoundedDecisionLayer** | Финальная стадия классификации | Детерминированный конечный автомат с четырьмя уровнями тревоги (LOW → MEDIUM → HIGH → CRITICAL) |
| **MI / Индекс Манипуляции** | Основной входной сигнал | Агрегированный скаляр, представляющий обнаруженное семантическое искажение в цифровом артефакте |
| **FSV / Семантико-экспертный вектор** | Структурированный входной контейнер | Пакет, содержащий индекс манипуляции и критические флаги, поступающий с предыдущих стадий |
| **Интерфейс решения** (`decide` / `decide_verdict`) | Точки внешнего доступа | Детерминированные процедуры, принимающие агрегированный FSV и выдающие метку риска |
| **Пороги** (LOW, MEDIUM, HIGH
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
