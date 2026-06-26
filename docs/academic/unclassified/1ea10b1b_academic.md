<!--
VIGIA Academic Documentation
Module: 1ea10b1b
Batch ID: vigia-doc-0046-1ea10b1b
Generated: 2026-05-20T14:56:47.854418+00:00
-->

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

## 中文

### 这是什么模块？

本文档描述 **VIGÍA** 分析流水线的最终决策门控单元。可将其理解为一个**经过校准的裁判**：它从上游取证阶段接收一个经过聚合的单一数值评分（操纵指数，MI），并将其转换为离散的风险标签。该模块不产生新的证据，仅对已完成测量的结果进行解释。

本模块具有**确定性**：给定相同的输入，始终产生相同的输出。它完全基于**精确整数运算**（分数运算），避免了十进制近似固有的舍入误差。系统中没有任何隐藏的加权项、启发式调整或随机因素——只有经过版本控制且可审计的阈值。

本模块在法庭上的可采纳性，正是建立在其绝对可重现性之上。每一次对相同取证工件的分析，都会经由相同的确定性整数分数比较路径，产生相同的风险标签。这一属性满足道伯特标准（Daubert）对科学证据可测试性、可重现性和已知误差率的要求。

### 关键概念

| 概念 | 定义 | 技术作用 |
|---|---|---|
| **RiskBoundedDecisionLayer** | 最终分类阶段 | 具有四个警报级别（LOW → MEDIUM → HIGH → CRITICAL）的确定性状态机 |
| **MI / 操纵指数** | 主要输入信号 | 表示在取证工件中检测到的语义失真的聚合标量 |
| **FSV / 法证语义向量** | 结构化输入容器 | 承载来自先前流水线阶段的操纵指数与关键标志的数据包 |
| **决策接口**（`decide` / `decide_verdict`） | 外部访问点 | 接收聚合 FSV 并输出风险标签的确定性程序 |
| **阈值**（LOW、MEDIUM、HIGH） | 决策边界 | 精确的分数截止值，已进行版本控制并可接受审计 |
| **ECO_SEMIOTIC_COLLISION** | 覆盖标志 | 无论 MI 评分如何，自动强制将警报级别提升至最高（CRITICAL）的条件 |
| **精确整数运算** | 内部计算方式 | 使用整数分子/分母进行运算，确保比较结果完全可重现；法证可重现性的数学基础 |

> **【科学说明】**
> 皮尔斯（Peirce）、艾柯（Eco）和格赖斯（Grice）的术语并非神秘主义，而是形式化的分析机制。如同光谱仪将光子相互作用转换为离散整数计数，本模块将证据信号转换为确定性整数分数。精确整数运算确保法庭可重现性，不依赖浮点近似。取证工件链的逻辑断裂以整数标志事件的形式被检测，而非直觉判断。本模块中的"艾柯符号学碰撞"（ECO_SEMIOTIC_COLLISION）如同物理传感器的触发器：当取证工件的符号代码结构以艾柯代码一致性理论所预测的方式发生自我矛盾时，传感器即触发。这是一条工程规则，而非文学判断。

### 词汇表

1. **操纵指数（MI）** — 对检测到的语义或结构操纵的定量度量；本模块的主要输入信号。
2. **法证语义向量（FSV）** — 来自先前流水线阶段的结构化输出，包含最终操纵指数及任何关键模式标志。
3. **确定性裁决** — 完全可从输入数据预测和重现的分类结果，不含任何随机性。
4. **ECO_SEMIOTIC_COLLISION** — 表示取证工件符号学结构存在根本矛盾的模式；在本系统中作为强制升级至 CRITICAL 的硬性覆盖标志。
5. **取证工件** — 任何受分析的数字对象（如文档、图像或日志文件）。
6. **阈值** — 将一个风险级别与另一个风险级别分隔开的预定义边界值；以精确分数表示。
7. **风险标签** — 由本模块输出的离散分类（LOW、MEDIUM、HIGH、CRITICAL）。
8. **SHA-256 哈希链** — 将每次分析事件以密码学方式绑定到先前事件的不可篡改日志机制。
9. **道伯特标准** — 美国联邦证据规则第 702 条，要求科学证据具备可测试性、已知误差率及同行评审性。
10. **精确分数运算** — 使用整数分子与整数分母进行的数学运算，确保法庭可重现性而不依赖近似值。

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
