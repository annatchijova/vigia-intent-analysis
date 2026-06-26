<!--
VIGIA Academic Documentation
Module: 68e0e743
Batch ID: vigia-doc-0004-68e0e743
Generated: 2026-05-20T14:56:47.845791+00:00
-->

---

## ENGLISH

### What Is This Module?
This module is an automated scientific-report generator for digital evidence. It ingests a sealed, tamper-evident container of forensic data (a **ForensicBundle** in JSON format) and writes a complete expert-witness statement named `evidence_narrative.md`. The statement is structured to satisfy the **Daubert** standard for admissible scientific evidence in court. It explains *what* was found, *how* integrity was preserved, *why* the method is reliable, and *which* conclusion follows from abductive reasoning. The report contains six deterministic sections: §1 Bundle Identification, §2 Chain of Custody, §3 Daubert Methodology, §4 Peirce Triad Analysis, §5 Winning Abductive Hypothesis, and §6 Triggered Rules.

### Key Concepts

**Table 1 — Forensic & Logical Frameworks**
| Term | Plain-Language Meaning | Role in the Module |
|---|---|---|
| **ForensicBundle** | A sealed, tamper-evident JSON container holding digital evidence and metadata. | Input source for the report. |
| **SHA-256** | A deterministic fingerprint algorithm producing an exact 256-bit integer hash. | Integrity verification via exact integer hash comparison. |
| **Daubert Standard** | A legal-scientific checklist (falsifiability, peer review, error rates, general standards). | §3 demonstrates that the methodology is defensible and reproducible. |
| **Peirce Triad** (Firstness / Secondness / Thirdness) | A logical framework for signs: (1) raw potential or signal, (2) actual event or interaction, (3) interpretive rule or habit. | §4 structures the narrative from raw data → observed event → interpreted meaning. |
| **Abductive Hypothesis** | Inference to the best explanation: given the evidence, what is the most plausible cause? | §5 selects the winning hypothesis using exact integer cost metrics (Ockham's razor). |
| **ENFSI Scale** | A standardized integer scale for expressing forensic conclusions. | Supplies deterministic, verbally anchored conclusion levels instead of inexact probability values. |
| **Ockham Cost** | A penalty score for unnecessary complexity; simpler explanations receive lower integer costs. | Used to rank competing hypotheses in a fully deterministic order. |

**Table 2 — Module Components**
| Component | Type | Plain-Language Description |
|---|---|---|
| `BundleReader` | Class | Opens the sealed JSON container and validates structure, checksums, and timestamps. |
| `NarrativeGenerator` | Class | Orchestrates the writing of all six report sections by applying deterministic rules to extracted data. |
| `main()` | Function | Entry point; executes the full pipeline from sealed bundle to finished narrative. |
| `bundle_id()` | Function | Returns the unique identifier of the evidence container. |
| `bundle_version()` | Function | Returns the container-format version to enforce backward compatibility. |
| `timestamp()` | Function | Returns the exact analysis time as a standardized integer epoch value. |
| `integrity()` | Function | Verifies overall bundle health using exact SHA-256 integer hash comparisons. |
| `bundle_hash()` | Function | Returns the primary SHA-256 integer fingerprint of the entire bundle. |
| `graph_hash()` | Function | Returns the SHA-256 integer fingerprint of the inference graph component. |

### Glossary
1. **Abductive Reasoning** — Inference to the best explanation; selecting the hypothesis that most economically accounts for all evidence.
2. **Chain of Custody** — The documented, unbroken record of who handled evidence, when, and how.
3. **Daubert Standard** — Legal criteria requiring scientific testimony to be based on falsifiable, peer-reviewed, and generally accepted methods.
4. **Deterministic Report** — A document whose content is fully determined by its input data, producing identical output for identical input.
5. **ENFSI Scale** — European Network of Forensic Science Institutes conclusion scale; uses integer-anchored verbal descriptors.
6. **ForensicBundle** — A sealed, integrity-verified container of digital evidence and analytical metadata.
7. **Ockham Cost** — An integer-valued parsimony penalty assigned to hypotheses; lower cost favors simpler explanations.
8. **Peirce Triad** — The three-layer sign analysis: Firstness (raw signal), Secondness (structural anomaly), Thirdness (inferred behavioral law).
9. **SHA-256** — Algorithm producing a deterministic 256-bit integer fingerprint of any byte sequence.
10. **Tamper-Evident** — A property of sealed containers where any unauthorized modification is detectable through hash verification.

> **【Scientific Note】**
> Peirce/Eco/Grice terminology is NOT mysticism. In VIGÍA, the Peirce Triad is a structured reasoning scaffold, not a philosophical exercise: Firstness is the raw sensor reading (the byte-level evidence), Secondness is the structural anomaly detected against a known baseline, and Thirdness is the repeatable behavioral pattern — the law of deliberate action — that the analyst presents to the court.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## ESPAÑOL

### ¿Qué es este módulo?
Este módulo es un generador automatizado de informes científicos para evidencia digital. Ingiere un contenedor sellado e inviolable de datos forenses (un **ForensicBundle** en formato JSON) y redacta una declaración completa de testigo experto denominada `evidence_narrative.md`. La declaración está estructurada para satisfacer el **estándar Daubert** de evidencia científica admisible en tribunales. Explica *qué* se encontró, *cómo* se preservó la integridad, *por qué* el método es fiable y *qué* conclusión se deriva del razonamiento abductivo. El informe contiene seis secciones deterministas: §1 Identificación del Paquete, §2 Cadena de Custodia, §3 Metodología Daubert, §4 Análisis de la Tríada Peirce, §5 Hipótesis Abductiva Ganadora y §6 Reglas Activadas.

### Conceptos clave

| Término | Significado | Rol en el módulo |
|---|---|---|
| **ForensicBundle** | Contenedor JSON sellado e inviolable que contiene evidencia digital y metadatos. | Fuente de entrada para el informe. |
| **SHA-256** | Algoritmo de huella digital determinista que produce un hash entero exacto de 256 bits. | Verificación de integridad mediante comparación exacta de hashes enteros. |
| **Estándar Daubert** | Lista de control legal-científica (falsabilidad, revisión por pares, tasas de error, normas generales). | §3 demuestra que la metodología es defendible y reproducible. |
| **Tríada Peirce** | Marco lógico de signos: (1) potencial/señal en bruto, (2) evento/interacción real, (3) regla/hábito interpretativo. | §4 estructura la narrativa desde datos en bruto → evento observado → significado interpretado. |
| **Hipótesis Abductiva** | Inferencia a la mejor explicación: dada la evidencia, ¿cuál es la causa más plausible? | §5 selecciona la hipótesis ganadora usando métricas de costo entero exactas. |
| **Escala ENFSI** | Escala entera estandarizada para expresar conclusiones forenses. | Proporciona niveles de conclusión deterministas con anclaje verbal. |
| **Costo Ockham** | Puntuación de penalización por complejidad innecesaria; explicaciones más simples reciben costos enteros menores. | Usado para ordenar hipótesis competidoras de forma totalmente determinista. |

### Glosario
1. **Razonamiento Abductivo** — Inferencia a la mejor explicación; seleccionar la hipótesis que da cuenta de toda la evidencia de forma más económica.
2. **Cadena de Custodia** — Registro documentado e ininterrumpido de quién manejó la evidencia, cuándo y cómo.
3. **Estándar Daubert** — Criterios legales que exigen que el testimonio científico se base en métodos falsificables, revisados por pares y generalmente aceptados.
4. **Informe Determinista** — Documento cuyo contenido está completamente determinado por sus datos de entrada.
5. **Escala ENFSI** — Escala de conclusión de la Red Europea de Institutos de Ciencias Forenses; utiliza descriptores verbales anclados en enteros.
6. **ForensicBundle** — Contenedor sellado y verificado de integridad que contiene evidencia digital y metadatos analíticos.
7. **Costo Ockham** — Penalización de parsimonia con valor entero asignada a hipótesis; menor costo favorece explicaciones más simples.
8. **Tríada Peirce** — Análisis de signo de tres capas: Primeridad (señal en bruto), Segundidad (anomalía estructural), Terceridad (ley conductual inferida).
9. **SHA-256** — Algoritmo que produce una huella digital entera determinista de 256 bits de cualquier secuencia de bytes.
10. **Inviolable** — Propiedad de contenedores sellados donde cualquier modificación no autorizada es detectable mediante verificación de hash.

> **【Nota Científica】**
> La terminología de Peirce/Eco/Grice no es misticismo. En VIGÍA, la Tríada Peirce es un andamiaje de razonamiento estructurado: la Primeridad es la lectura bruta del sensor, la Segundidad es la anomalía estructural detectada respecto a un referente conocido, y la Terceridad es el patrón conductual repetible — la ley de acción deliberada — que el analista presenta ante el tribunal.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## РУССКИЙ

### Что это за модуль?
Данный модуль представляет собой автоматизированный генератор научных отчётов по цифровым доказательствам. Он принимает запечатанный, защищённый от несанкционированного доступа контейнер криминалистических данных (**ForensicBundle** в формате JSON) и формирует полное заключение эксперта-свидетеля под названием `evidence_narrative.md`. Заключение структурировано в соответствии со **стандартом Добера** (Daubert) для допустимых научных доказательств в суде. В нём объясняется *что* было обнаружено, *как* была сохранена целостность, *почему* метод надёжен и *какой* вывод следует из абдуктивного рассуждения. Отчёт содержит шесть детерминированных разделов: §1 Идентификация пакета, §2 Цепочка хранения, §3 Методология Добера, §4 Анализ Триады Пирса, §5 Победившая абдуктивная гипотеза и §6 Активированные правила.

### Ключевые концепции

| Термин | Значение | Роль в модуле |
|---|---|---|
| **ForensicBundle** | Запечатанный, защищённый от вмешательства JSON-контейнер с цифровыми доказательствами и метаданными. | Источник входных данных для отчёта. |
| **SHA-256** | Детерминированный алгоритм отпечатка, производящий точный 256-битный целочисленный хеш. | Верификация целостности через точное сравнение целочисленных хешей. |
| **Стандарт Добера** | Юридически-научный контрольный список (фальсифицируемость, рецензирование, частоты ошибок, общие стандарты). | §3 демонстрирует защищаемость и воспроизводимость методологии. |
| **Триада Пирса** | Логическая рамка знаков: (1) сырой потенциал/сигнал, (2) реальное событие/взаимодействие, (3) интерпретационное правило/привычка. | §4 структурирует нарратив от сырых данных → наблюдаемое событие → интерпретированное значение. |
| **Абдуктивная гипотеза** | Умозаключение к наилучшему объяснению: учитывая доказательства, какова наиболее правдоподобная причина? | §5 выбирает победившую гипотезу с использованием точных целочисленных метрик стоимости. |
| **Шкала ENFSI** | Стандартизированная целочисленная шкала для выражения криминалистических выводов. | Обеспечивает детерминированные вербально-анкерные уровни вывода. |
| **Стоимость Оккама** | Штрафная оценка за излишнюю сложность; более простые объяснения получают меньшие целочисленные стоимости. | Используется для ранжирования конкурирующих гипотез в полностью детерминированном порядке. |

### Глоссарий
1. **Абдуктивное рассуждение** — Умозаключение к наилучшему объяснению; выбор гипотезы, наиболее экономично объясняющей все доказательства.
2. **Цепочка хранения** — Задокументированная, непрерывная запись о том, кто, когда и как обращался с доказательствами.
3. **Стандарт Добера** — Юридические критерии, требующие, чтобы научные показания основывались на фальсифицируемых, прошедших рецензирование и общепринятых методах.
4. **Детерминированный отчёт** — Документ, содержание которого полностью определяется входными данными.
5. **Шкала ENFSI** — Шкала выводов Европейской сети институтов судебных наук; использует вербальные дескрипторы с целочисленными якорями.
6. **ForensicBundle** — Запечатанный, верифицированный по целостности контейнер цифровых доказательств и аналитических метаданных.
7. **Стоимость Оккама** — Целочисленный штраф за сложность, присваиваемый гипотезам; меньшая стоимость предпочтительна.
8. **Триада Пирса** — Трёхуровневый анализ знака: Первичность (сырой сигнал), Вторичность (структурная аномалия), Третичность (выведенный поведенческий закон).
9. **SHA-256** — Алгоритм, производящий детерминированный 256-битный целочисленный отпечаток любой байтовой последовательности.
10. **Защита от вмешательства** — Свойство запечатанных контейнеров, при котором любое несанкционированное изменение обнаруживается через верификацию хеша.

> **【Научное примечание】**
> Терминология Пирса, Эко и Грайса — не мистика. В VIGÍA Триада Пирса является структурированным аналитическим каркасом: Первичность — это необработанное показание датчика, Вторичность — структурная аномалия, обнаруженная относительно известного базового уровня, а Третичность — повторяющийся поведенческий паттерн, закон намеренного действия, который аналитик представляет суду.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## 中文

### 这是什么模块？
本模块是数字证据的自动化科学报告生成器。它接收一个密封的、防篡改的取证数据容器（JSON 格式的 **ForensicBundle**），并生成名为 `evidence_narrative.md` 的完整专家证人陈述。该陈述结构满足法庭科学证据的**道伯特标准**（Daubert standard）。它解释*发现了什么*、*如何*保护完整性、*为什么*该方法可靠，以及*什么*结论来自溯因推理。报告包含六个确定性章节：§1 捆绑包识别、§2 监管链、§3 道伯特方法论、§4 皮尔斯三元组分析、§5 获胜溯因假说、§6 触发规则。

### 关键概念

| 术语 | 通俗含义 | 模块中的作用 |
|---|---|---|
| **ForensicBundle** | 包含数字证据和元数据的密封防篡改 JSON 容器。 | 报告的输入来源。 |
| **SHA-256** | 确定性指纹算法，产生精确的 256 位整数哈希。 | 通过精确整数哈希比较进行完整性验证。 |
| **道伯特标准** | 法律科学核对表（可证伪性、同行评审、错误率、通用标准）。 | §3 证明方法论具有可辩护性和可复现性。 |
| **皮尔斯三元组**（第一性/第二性/第三性） | 符号逻辑框架：(1) 原始潜力/信号，(2) 实际事件/交互，(3) 解释规则/习惯。 | §4 将叙述从原始数据→观察事件→解释意义结构化。 |
| **溯因假说** | 对最佳解释的推断：给定证据，最合理的原因是什么？ | §5 使用精确整数成本指标（奥卡姆剃刀）选择获胜假说。 |
| **ENFSI 量表** | 表达取证结论的标准化整数量表。 | 提供确定性的言语锚定结论级别，而非不精确的概率值。 |
| **奥卡姆成本** | 对不必要复杂性的惩罚分数；更简单的解释获得更低的整数成本。 | 用于以完全确定性的顺序排列竞争假说。 |

### 词汇表
1. **溯因推理** — 对最佳解释的推断；选择最经济地解释所有证据的假说。
2. **监管链** — 关于谁、何时、如何处理证据的书面、连续记录。
3. **道伯特标准** — 要求科学证词基于可证伪、经同行评审且普遍接受的方法的法律标准。
4. **确定性报告** — 内容完全由输入数据决定的文档，相同输入产生相同输出。
5. **ENFSI 量表** — 欧洲法证科学机构网络结论量表；使用整数锚定的言语描述符。
6. **ForensicBundle** — 包含数字证据和分析元数据的密封完整性验证容器。
7. **奥卡姆成本** — 分配给假说的整数简约惩罚；成本越低越优先。
8. **皮尔斯三元组** — 三层符号分析：第一性（原始信号）、第二性（结构异常）、第三性（推断的行为规律）。
9. **SHA-256** — 对任意字节序列产生确定性 256 位整数指纹的算法。
10. **防篡改** — 密封容器的特性，通过哈希验证可检测任何未经授权的修改。

> **【科学说明】**
> 皮尔斯、艾柯和格赖斯的术语并非神秘主义。在 VIGÍA 中，皮尔斯三元组是结构化推理框架：第一性是原始传感器读数，第二性是相对于已知基线检测到的结构异常，而第三性是分析员向法庭呈现的可重复行为模式——蓄意行动的规律。

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
