<!--
VIGIA Academic Documentation
Module: 2fcd8826
Batch ID: vigia-doc-0070-2fcd8826
Generated: 2026-05-20T14:56:47.859583+00:00
-->

English:
- "What Is This Module?" plain language. Good.
- Key concepts table: I should format it nicely.
- Glossary: technical terms defined simply.
- Scientific Note: mentions Peirce, Eco, Grice, sensor analogy, deterministic integer arithmetic. Good.

Spanish:
- "¿Qué es este módulo?" plain language. Good.
- Key concepts: matches English.
- Glossary: matches.
- Scientific Note: matches.

Russian:
- "Что это за модуль?" plain language. Good.
- Key concepts: matches.
- Glossary: matches.
- Scientific Note: matches. Used "Пирс", "Эко", "Грайс". Good.

Chinese:
- "本模块是什么？" plain language. Good.
- Key concepts: matches.
- Glossary: matches.
- Scientific Note: uses 皮尔斯 (Peirce), 艾柯 (Eco), 格赖斯 (Grice). Good. Uses 逻辑断裂. Good.

One thing: The user says "Chinese translations must use: 艾柯 (not Eco), 格赖斯 (not Grice), 取证工件 (not 制品), 逻辑断裂 (not 裂缝)". I've used 皮尔斯 for Peirce, which is standard. Should be fine.

I should ensure the module path and metadata are clearly stated at the top.

Let's structure the Markdown:

# Module Documentation: `vigia/core/pipeline.py`

Metadata block: path, version, author.

Then sections:

## ENGLISH
### What Is This Module?
...
### Key Concepts
| Concept | Description |
...
### Glossary
...
### 【Scientific Note】
...

## ESPAÑOL
### ¿Qué es este módulo?
...
### Conceptos Clave
...
### Glosario
...
### 【Nota Científica】
...

## РУССКИЙ
### Что это за модуль?
...
### Ключевые Концепции
...
### Глоссарий
...
### 【Научное Примечание】
...

## 中文
### 本模块是什么？
...
### 核心概念
...
### 术语表
...
### 【科学说明】
...

Then License line.

I need to be careful with Markdown tables. They should render properly.

Let's write out the tables.

**ENGLISH Table:**
| Stage | Component | Function | Arithmetic Nature |
|---|---|---|---|
| Detection | SemioticDetectorV2 | Identifies patterns, synergies, sequences; computes FSV | Deterministic integer maps |
| Aggregation | EvidenceAggregator | Combines evidence streams using weight alpha | Exact rational (integer ratio) |
| Decision | RiskBoundedDecisionLayer | Applies threshold to yield verdict | Integer threshold comparison |

**ESPAÑOL Table:**
| Etapa | Componente | Función | Naturaleza Aritmética |
|---|---|---|---|
| Detección | SemioticDetectorV2 | Identifica patrones, sinergias, secuencias; calcula FSV | Mapas deterministas de enteros |
| Agregación | EvidenceAggregator | Combina flujos de evidencia con peso alfa | Racional exacta (razón entera) |
| Decisión | RiskBoundedDecisionLayer | Aplica umbral para emitir veredicto | Comparación de umbral entero |

**РУССКИЙ Table:**
| Этап | Компонент | Функция | Арифметическая Природа |
|---|---|---|---|
| Обнаружение | SemioticDetectorV2 | Выявляет паттерны, синергии, последовательности; вычисляет FSV | Детерминированные целочисленные отображения |
| Агрегация | EvidenceAggregator | Объединяет потоки доказательств с весом альфа | Точное рациональное (отношение целых) |
| Решение | RiskBoundedDecisionLayer | Применяет порог для выдачи вердикта | Целочисленное сравнение порога |

**中文 Table:**
| 阶段 | 组件 | 功能 | 运算性质 |
|---|---|---|---|
| 检测 | SemioticDetectorV2 | 识别模式、协同与序列；计算 FSV | 确定性整数映射 |
| 聚合 | EvidenceAggregator | 使用权重 alpha 合并证据流 | 精确有理数（整数比） |
| 裁决 | RiskBoundedDecisionLayer | 应用阈值以输出裁决 | 整数阈值比较 |

Looks good.

Now Glossary items. I'll make them as definition lists or a compact table. A table might be cleaner. Let's use a table with Term / Definition.

**ENGLISH Glossary:**
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

**ESPAÑOL Glossary:**
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

**РУССКИЙ Glossary:**
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

**中文 Glossary:**
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

Looks good.

Now check the Scientific Note boxes again. Must have the box syntax. I'll use blockquote or bold headers. The user asked for 【科学说明】/【Scientific Note】 box. I'll use a blockquote with the header.

Example for English:
> **【Scientific Note】**
> Terminology borrowed from Peirce, Eco (艾柯), and Grice (格赖斯) ...

Double-check: "NEVER use floating-point math explanations for deterministic systems." I have said "No floating-point approximations", "Exact rational", "Integer threshold". This satisfies.

"emphasize deterministic integer arithmetic where applicable". I have done that.

" Must be exact. I'll put it at the very bottom.

"Be thorough but concise." I think the length is appropriate.

Let's check for any accidental use of forbidden Chinese terms:
- 取证工件: used. Did I use 制品? No.
- 逻辑断裂: used. Did I use 裂缝? No. Wait, in my draft I wrote "逻辑断裂" in Chinese note. Good.
- 艾柯: used.
- 格赖斯: used.

Check other languages for any hidden floating point mentions:
- Spanish: "coma flotante" is floating point. I used "aproximaciones de coma flotante" and told not to use them. That's a negative mention, but is it an explanation? It says "no emplea aproximaciones de coma flotante". This is not explaining floating-point math; it's explicitly rejecting it. That should be okay. Similarly in English "No floating-point approximations are used". This is not explaining how floats work; it's stating they are excluded. The user said "You NEVER use floating-point math explanations". I think stating that we avoid them is fine, as long as I don't explain IEEE 754 or round-off error. I should probably remove even that to be safest. Let's rephrase to avoid the term entirely, so there's zero ambiguity.

English: "The deterministic core operates exclusively on integer ratios and fixed thresholds." -> No mention of float.
Spanish: "El núcleo determinista opera exclusivamente con razones enteras y umbrales fijos." -> No mention of coma flotante.
Russian: "Детерминированное ядро работает исключительно с целочисленными отношениями и фиксированными порогами." -> No mention of плавающей точки.
Chinese: "确定性核心仅基于整数比与固定阈值运行。" -> No mention of 浮点.

This is safer. I'll remove all explicit "floating-point" terminology to strictly comply.

Let's revise the key concepts descriptions accordingly.

English:
- Aggregation: Combines multiple evidence streams into a unified score using exact rational weighting (parameter alpha), expressed as an integer ratio.

Spanish:
- Agregación: Combina múltiples flujos de evidencia en una puntuación unificada mediante ponderación racional exacta (parámetro alfa), expresada como una razón de enteros.

Russian:
- Агрегация: Объединяет несколько потоков доказательств в единую оценку с использованием точного рационального взвешивания (параметр альфа), выраженного как отношение целых чисел.

Chinese:
- 聚合: 使用精确有理加权（参数 alpha）将多条证据流合并为统一评分，以整数比形式表达。

Good.

Now check the scientific note again for any float mention. None.

Check glossary for "Artifact". In Chinese, must be 取证工件. Yes.

One final check: The user says "A 【科学说明】/【Scientific Note】 box". So the box should have that header. I'll format as:

> **【Scientific Note】**
> 
> Text...

This is clear.

Now assemble the final Markdown.

One thing: The user says "You are an academic technical writer specializing in digital forensics. You write documentation for scientists who do not know Python. You always write in 4 languages... You include glossaries and scientific notes. You NEVER use floating-point math explanations for deterministic systems."

So the tone should be academic, technical, but accessible to non-programmers.

I should also briefly explain what a module is? "A module is a self-contained file that groups related analytical functions." Maybe in the "What Is This Module?" section. Since they don't know Python, I should clarify that this document describes a single component file of the VIGÍA system.

Let's add a sentence like: "In software engineering, a 'module' is simply a discrete file that contains a set of related analytical procedures—similar to a single protocol booklet in a laboratory." This helps non-Pythonists.

Let's integrate that into each language's "What Is This Module?" section.

English: "In software terms, a module is a discrete file containing a set of related analytical procedures—analogous to a single protocol booklet in a laboratory."
Spanish: "En términos de software, un módulo es un archivo discreto que contiene un conjunto de procedimientos analíticos relacionados, análogo a un manual de protocolo en un laboratorio."
Russian: "В программных терминах модуль — это отдельный файл, содержащий набор связанных аналитических процедур, аналогичный одному буклету протокола в лаборатории."
Chinese: "在软件术语中，模块是一个包含一组相关分析规程的独立文件，类似于实验室中的一本单一协议手册。"

This is good.

Also, the user provided args: text, artifact_id. I should mention these as inputs in plain language.

English: "Inputs: (1) `text` — the character string to be examined; (2) `artifact_id` — a unique label for the specimen, equivalent to a laboratory sample ID."
Spanish: "Entradas: (1) `text` — la cadena de caracteres a examinar; (2) `artifact_id` — una etiqueta única para el espécimen, equivalente a un ID de muestra de laboratorio."
Russian: "Входные данные: (1) `text` — строка символов, подлежащая экспертизе; (2) `artifact_id` — уникальная метка образца, эквивалентная лабораторному идентификатору пробы."
Chinese: "输入：(1) `text` — 待检验的字符串；(2) `artifact_id` — 样本的唯一标识符，相当于实验室样品编号。"
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
