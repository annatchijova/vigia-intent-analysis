<!--
VIGIA Academic Documentation
Module: 2fcd8826
Batch ID: vigia-doc-0070-2fcd8826
Generated: 2026-05-20T14:56:47.859583+00:00
-->

# Module Documentation: `vigia/core/pipeline.py`

## ENGLISH

### What Is This Module?
In software engineering, a module is a discrete file containing a set of related analytical procedures—analogous to a single protocol booklet in a laboratory. The file `vigia/core/pipeline.py` defines the end-to-end deterministic processing pipeline for VIGÍA forensic analysis. It coordinates three sequentially dependent stages—detection, aggregation, and decision—ensuring that each output is the strict, reproducible consequence of its input. No stochastic or approximate intermediate values are permitted.

Inputs: (1) `text` — the character string to be examined; (2) `artifact_id` — a unique label for the specimen, equivalent to a laboratory sample ID.

### Key Concepts

| Stage | Component | Function | Arithmetic Nature |
|---|---|---|---|
| Detection | SemioticDetectorV2 | Identifies patterns, synergies, sequences; computes FSV | Deterministic integer maps |
| Aggregation | EvidenceAggregator | Combines evidence streams using weight alpha | Exact rational (integer ratio) |
| Decision | RiskBoundedDecisionLayer | Applies threshold to yield verdict | Integer threshold comparison |

### Glossary

| Term | Definition |
|---|---|
| Artifact | A textual object under examination, treated as physical evidence. |
| Semiotic Detection | Decomposition of text into sign-systems per Peirce and Eco. |
| Synergy | Co-occurrence of signs producing a combined effect exceeding individual contributions. |
| Sequence | Ordered sign arrangement analyzed for temporal or spatial anomalies. |
| FSV (Forensic Sign Vector) | Deterministic integer vector summarizing detected indicators. |
| Alpha (α) | Configurable integer parameter governing relative evidence weight. |
| Threshold | Immutable integer cutoff triggering a classification. |
| Pipeline | Linear sequence of stages where output feeds deterministically into the next. |

### 【Scientific Note】

> **Terminology borrowed from Peirce, Eco (艾柯), and Grice (格赖斯) is not mysticism—it is sensor calibration vocabulary.**
>
> The pipeline integrates frameworks from three formal traditions. Peircean semiotics provides the hypothesis-formation protocol (abduction). Eco's semiotic theory supplies the codebook that maps raw pattern matches to meaningful forensic categories. Grice's cooperative maxims define logical constraints on valid evidence sequences—violations are anomaly signals, not rhetorical features. The deterministic core operates exclusively on integer ratios and fixed thresholds. No stochastic approximations enter the decision path. These philosophical frameworks serve as structured taxonomies for deterministic boundary conditions, analogous to wavelength specifications in a spectrometer. The pipeline is an instrument, not an interpreter. Each stage maps inputs to outputs through exact, reproducible rules. The labels "Firstness," "Secondness," and "Thirdness" designate discrete integer processing states, not metaphysical propositions. Any finding produced by the pipeline can be independently verified by replaying the same inputs against the same deterministic configuration.

---

## ESPAÑOL

### ¿Qué es este módulo?
En ingeniería de software, un módulo es un archivo discreto que contiene un conjunto de procedimientos analíticos relacionados, análogo a un manual de protocolo en un laboratorio. El archivo `vigia/core/pipeline.py` define la canalización determinista de extremo a extremo para el análisis forense de VIGÍA. Coordina tres etapas secuencialmente dependientes—detección, agregación y decisión—asegurando que cada salida sea la consecuencia estricta y reproducible de su entrada. No se permiten valores intermedios estocásticos o aproximados.

Entradas: (1) `text` — la cadena de caracteres a examinar; (2) `artifact_id` — una etiqueta única para el espécimen, equivalente a un ID de muestra de laboratorio.

### Conceptos Clave

| Etapa | Componente | Función | Naturaleza Aritmética |
|---|---|---|---|
| Detección | SemioticDetectorV2 | Identifica patrones, sinergias, secuencias; calcula FSV | Mapas deterministas de enteros |
| Agregación | EvidenceAggregator | Combina flujos de evidencia con peso alfa | Racional exacta (razón entera) |
| Decisión | RiskBoundedDecisionLayer | Aplica umbral para emitir veredicto | Comparación de umbral entero |

### Glosario

| Término | Definición |
|---|---|
| Artefacto | Objeto textual bajo examen, tratado como evidencia física. |
| Detección Semiótica | Descomposición del texto en sistemas de signos según Peirce y Eco. |
| Sinergia | Coocurrencia de signos que produce un efecto combinado mayor que la suma individual. |
| Secuencia | Disposición ordenada de signos analizada en busca de anomalías temporales o espaciales. |
| FSV | Vector determinista de enteros que resume los indicadores detectados. |
| Alfa (α) | Parámetro entero configurable que gobierna el peso relativo de la evidencia. |
| Umbral | Punto de corte entero inmutable que activa la clasificación. |
| Pipeline | Secuencia lineal de etapas donde la salida alimenta determinísticamente a la siguiente. |

### 【Nota Científica】

> **La terminología tomada de Peirce, Eco (艾柯) y Grice (格赖斯) no es misticismo—es vocabulario de calibración de sensores.**
>
> La canalización integra marcos de tres tradiciones formales. La semiótica peirceana provee el protocolo de formación de hipótesis (abducción). La teoría semiótica de Eco suministra el código que asigna coincidencias de patrones crudos a categorías forenses significativas. Las máximas cooperativas de Grice definen restricciones lógicas sobre secuencias de evidencia válidas: las violaciones son señales de anomalía, no rasgos retóricos. El núcleo determinista opera exclusivamente con razones enteras y umbrales fijos. Las etiquetas "Primeridad", "Segundidad" y "Terceridad" designan estados enteros discretos de procesamiento, no proposiciones metafísicas. Cualquier hallazgo producido por la canalización puede verificarse de forma independiente reproduciendo las mismas entradas contra la misma configuración determinista.

---

## РУССКИЙ

### Что это за модуль?
В программной инженерии модуль — это отдельный файл, содержащий набор связанных аналитических процедур, аналогичный одному буклету протокола в лаборатории. Файл `vigia/core/pipeline.py` определяет детерминированный сквозной конвейер обработки для судебного анализа VIGÍA. Он координирует три последовательно зависимые стадии—обнаружение, агрегацию и решение—обеспечивая, что каждый выход является строгим и воспроизводимым следствием своих входных данных. Стохастические или приближённые промежуточные значения не допускаются.

Входные данные: (1) `text` — строка символов, подлежащая экспертизе; (2) `artifact_id` — уникальная метка образца, эквивалентная лабораторному идентификатору пробы.

### Ключевые Концепции

| Этап | Компонент | Функция | Арифметическая Природа |
|---|---|---|---|
| Обнаружение | SemioticDetectorV2 | Выявляет паттерны, синергии, последовательности; вычисляет FSV | Детерминированные целочисленные отображения |
| Агрегация | EvidenceAggregator | Объединяет потоки доказательств с весом альфа | Точное рациональное (отношение целых) |
| Решение | RiskBoundedDecisionLayer | Применяет порог для выдачи вердикта | Целочисленное сравнение порога |

### Глоссарий

| Термин | Определение |
|---|---|
| Артефакт | Текстовый объект под экспертизой, рассматриваемый как физическое доказательство. |
| Семиотическое обнаружение | Разложение текста на системы знаков согласно Пирсу и Эко. |
| Синергия | Совместное появление знаков, дающее эффект больший суммы отдельных вкладов. |
| Последовательность | Упорядоченное расположение знаков, анализируемое на аномалии. |
| FSV | Детерминированный целочисленный вектор, обобщающий обнаруженные индикаторы. |
| Альфа (α) | Настраиваемый целочисленный параметр, определяющий относительный вес доказательств. |
| Порог | Неизменная целочисленная отсечка, инициирующая классификацию. |
| Конвейер (Pipeline) | Линейная последовательность стадий, где выход одной передаётся детерминированно на вход следующей. |

### 【Научное Примечание】

> **Терминология, заимствованная у Пирса, Эко (艾柯) и Грайса (格赖斯), — не мистицизм, а словарь калибровки датчиков.**
>
> Конвейер интегрирует рамки трёх формальных традиций. Пирсовская семиотика предоставляет протокол формирования гипотез (абдукция). Семиотическая теория Эко поставляет кодовую книгу, отображающую сырые совпадения паттернов на значимые судебные категории. Кооперативные максимы Грайса определяют логические ограничения на допустимые последовательности доказательств: нарушения являются сигналами аномалии, а не риторическими особенностями. Детерминированное ядро работает исключительно с целочисленными отношениями и фиксированными порогами. Метки «Первичность», «Вторичность» и «Третичность» обозначают дискретные целочисленные состояния обработки, а не метафизические положения. Любой вывод, произведённый конвейером, может быть независимо проверен воспроизведением тех же входных данных при той же детерминированной конфигурации.

---

## 中文

### 本模块是什么？
在软件术语中，模块是一个包含一组相关分析规程的独立文件，类似于实验室中的一本单一协议手册。文件 `vigia/core/pipeline.py` 定义了 VIGÍA 法医分析的端到端确定性处理管线。它协调三个顺序依赖的阶段——检测、聚合与裁决——确保每个输出都是其输入的严格且可复现的结果。不允许任何随机或近似的中间值。

输入：(1) `text` — 待检验的字符串；(2) `artifact_id` — 样本的唯一标识符，相当于实验室样品编号。

### 核心概念

| 阶段 | 组件 | 功能 | 运算性质 |
|---|---|---|---|
| 检测 | SemioticDetectorV2 | 识别模式、协同与序列；计算 FSV | 确定性整数映射 |
| 聚合 | EvidenceAggregator | 使用权重 alpha 合并证据流 | 精确有理数（整数比） |
| 裁决 | RiskBoundedDecisionLayer | 应用阈值以输出裁决 | 整数阈值比较 |

### 术语表

| 术语 | 定义 |
|---|---|
| 取证工件 | 受检的文本对象，被视为物理证据。 |
| 符号学检测 | 依据皮尔斯与艾柯的理论将文本分解为符号系统的过程。 |
| 协同 | 符号共现产生的综合效应大于各自单独贡献之和。 |
| 序列 | 被用于检测时序或空间异常的符号有序排列。 |
| FSV（取证符号向量） | 概括已检测指标的确定性整数向量。 |
| Alpha（α） | 控制证据相对权重的可配置整数参数。 |
| 阈值 | 触发分类的不可变整数分界点。 |
| 管线（Pipeline） | 前一阶段输出确定性地馈入下一阶段的线性处理序列。 |

### 【科学说明】

> **借自皮尔斯、艾柯与格赖斯的术语并非神秘主义——而是传感器校准词汇。**
>
> 管线融合了三个形式传统的框架。皮尔斯符号学提供假设生成协议（溯因推理）。艾柯的符号学理论提供将原始模式匹配映射到有意义取证类别的代码本。格赖斯的合作准则定义了有效证据序列的逻辑约束——违例是异常信号，而非修辞特征。确定性核心仅基于整数比与固定阈值运行。"第一性"、"第二性"与"第三性"这些标签指定的是离散整数处理状态，而非形而上学命题。管线产生的任何发现都可以通过在相同确定性配置下重放相同输入来独立验证。逻辑断裂在管线中表现为序列约束或协同规则的违例，由整数状态检查精确标记。

---

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
