<!--
VIGIA Academic Documentation
Module: 9e2e4cde
Batch ID: vigia-doc-0081-9e2e4cde
Generated: 2026-05-20T14:56:47.861995+00:00
-->

---
doc_hash: 9e2e4cde
module: vigia/core/vigia_core_forensic_technical_detector.py
languages: [EN, ES, RU]
generated_by: moonshot-kimi-k2.6-batch-api
license: Apache-2.0
---

### ENGLISH

#### What Is This Module?
Plain language: This file is a deterministic forensic sensor. It reads the text content of digital forensic artifacts (logs, memory dumps, network traces) and identifies explicit technical indicators known as TTPs (Tactics, Techniques, and Procedures). Unlike machine-learning black boxes, it uses exact pattern rules (regular expressions) and integer-ratio arithmetic to guarantee that the same artifact always produces the same result. It works alongside the SemioticDetectorV2, which handles meaning and context, while this module handles hard technical evidence.

#### Key Concepts (table)
We need tables.

Concepts:
- Deterministic TTP Detection
- Integer-Ratio Arithmetic (Fraction)
- Forensic Artifact
- Explicit Regex Traceability
- Synergy Scoring
- Display Float (z_score)


Also perhaps a table for Constants:
Constant | Internal Type | Purpose

Constants: BASE_Z, MAX_Z, SYNERGY_STEP, MAX_SYNERGY, TYPE_TOOL.

Another table for Class/Function.

Class/Function table:
Name | Role | Input / Output

ForensicTechnicalDetector | Core deterministic sensor | forensic artifact text
analyze() | Main measurement method | returns scoring dictionary

#### Glossary
- TTP (Tactics, Techniques, and Procedures): The observable, technical methods used in an intrusion or cyber operation.
- Regex (Regular Expression): A formal language pattern used to match exact strings; here it acts as a deterministic filter.
- Fraction: Python's rational-number type representing values as integer numerator/denominator pairs, ensuring no rounding errors.
- Forensic Artifact: Any digital object collected as evidence (e.g., log file, packet capture, disk sector).
- Deterministic Invariant: A guarantee that identical inputs, processed by identical logic, yield identical outputs.
- z_score: A standardized score indicating how many standard-deviation units an observation lies from a reference; here derived from integer ratios and rendered as decimal solely for display.
- Synergy: The incremental gain added when multiple corroborating indicators appear together.

#### 【Scientific Note】 box
Title: 【Scientific Note】Peirce, Eco, and Grice Are Not Mysticism — They Are Sensor Ontologies

Content: In the companion module SemioticDetectorV2, terms drawn from Charles Sanders Peirce (sign, interpretant), Umberto Eco (code, encyclopedia), and H. P. Grice (implicature, cooperative principle) describe layers of context detection. These are not metaphysical concepts. Think of them as different spectrums of a multi-band sensor: Peirce defines how a raw voltage becomes a symbol, Eco calibrates the cultural filter, and Grice tunes the noise-reduction protocol for intentional signals. The ForensicTechnicalDetector is the base platinum resistance thermometer: it measures physical facts (regex matches) without interpretation. Together, the two modules form a fused instrument array — one channel for physical quantity, one channel for semantic context.

#### Invariants
Mention I2, I7, I9.

I2: Same input → same output always.
I7: All logic uses Fraction — no internal floats.
I9: Every detection traceable to explicit regex.

No floating-point math explanations. Emphasize integer arithmetic.

### ESPAÑOL

Mirror content.

- "What Is This Module?" -> "¿Qué es este módulo?"
- Deterministic sensor analogy.
- Use terms: Detector Técnico Forense, Artefacto forense, Fracción (aritmética de enteros), Expresión regular (regex), TTPs, Invariante.

Chinese specific terms:
- 取证工件 (forensic artifact)



### РУССКИЙ

Mirror.

- Terms: детерминированный, дробь (Fraction), целочисленная арифметика, следовой артефакт (or forensический артефакт), регулярное выражение.
- Scientific Note -> 【Научное Примечание】.

### Overall Formatting


Under each, subheaders: `## What Is This Module?`, `## Key Concepts`, `## Glossary`, `## 【Scientific Note】/【...】`.


First, let's think about the constants and how to describe them without floating point.

BASE_Z: integer base offset for the score.
MAX_Z: integer cap for the score.
SYNERGY_STEP: integer increment added when multiple indicators co-occur.
MAX_SYNERGY: integer ceiling for synergy bonuses.
TYPE_TOOL: categorical tag for tool-type indicators.

All stored as integers or strings, manipulated via Fraction for ratios.

Function analyze(): accepts forensic artifact text, applies regex rules, counts matches, computes integer-based score using Fraction, returns dict with `z_score` (converted to float only for display) and other fields like `co_occurrence_map`, `trace_log`, `deterministic_hash`.




Now, the note about no floating-point math: "Emphasize deterministic integer arithmetic where applicable." So when explaining scoring, say: "The scoring engine uses Python's `Fraction` class, which stores each value as a pair of integers (numerator, denominator). All additions, multiplications, and comparisons occur in integer arithmetic. The resulting rational number is only converted to a decimal string at the final output boundary."


---

**ENGLISH**

*Module Path:* `vigia/core/vigia_core_forensic_technical_detector.py`

## What Is This Module?

This module is a deterministic forensic instrument. It ingests the raw text of digital forensic artifacts—such as system logs, memory extracts, or network packet transcripts—and identifies explicit technical indicators called TTPs (Tactics, Techniques, and Procedures). It contains no machine-learning models, no statistical black boxes, and no external dependencies. Instead, it relies on exact pattern rules (regular expressions) and integer-ratio arithmetic to guarantee that an identical artifact always yields an identical report. It operates as the physical-measurement channel of a two-channel system: the companion `SemioticDetectorV2` handles semantic context, while this module records hard technical facts.

## Key Concepts

| Concept | Description | Scientific Relevance |
|---|---|---|
| Deterministic TTP Detection | Matching text against a catalog of explicit technical indicators (e.g., command-line signatures, registry keys, API call sequences). | Eliminates observer variability; identical evidence produces identical conclusions. |
| Integer-Ratio Arithmetic (`Fraction`) | All internal scores are maintained as exact fractions (pairs of integers: numerator/denominator). | Guarantees reproducibility and avoids rounding artifacts inherent in floating-point representations. |
| Forensic Artifact | Any digital object collected as evidence: log files, disk sectors, packet captures, or memory pages. | The input specimen under measurement. |
| Explicit Regex Traceability | Every positive match can be traced back to a specific, human-readable regular-expression rule. | Full auditability; no opaque weights or hidden layers. |
| Synergy Scoring (`SYNERGY_STEP`, `MAX_SYNERGY`) | When multiple corroborating indicators appear together, the score increments by discrete integer steps up to a ceiling. | Reflects combined evidentiary weight without continuous (float) approximations. |
| Display `z_score` | The final integer-ratio result is converted to a decimal number **only** for screen or file output. | Human-readable display; the underlying value remains an exact rational. |

**Constants & Configuration**

| Constant | Internal Representation | Purpose |
|---|---|---|
| `BASE_Z` | Integer | The initial baseline score offset. |
| `MAX_Z` | Integer | The absolute upper bound of the technical score. |
| `SYNERGY_STEP` | Integer | The discrete integer increment awarded for each additional corroborating indicator. |
| `MAX_SYNERGY` | Integer | The maximum total bonus that synergy can contribute. |
| `TYPE_TOOL` | String (categorical tag) | Label identifying the indicator class “tool usage.” |

**Core Components**

| Name | Role | Input → Output |
|---|---|---|
| `ForensicTechnicalDetector` | Deterministic sensor class | Initializes with rule catalog and invariants. |
| `analyze()` | Measurement method | Accepts forensic artifact text → returns result dictionary (integer-ratio internals + display `z_score`). |

## Glossary

- **Artifact (Forensic):** A digital object preserved as evidence during an investigation.
- **Deterministic Invariant:** A logical guarantee that the same input, processed by the same algorithm, always produces the same output.
- **Fraction:** A rational-number representation using two integers (numerator and denominator), ensuring exact arithmetic.
- **Regex (Regular Expression):** A formal pattern-matching language; here it acts as a deterministic sieve for textual evidence.
- **Synergy:** The incremental evidentiary gain produced when multiple independent indicators co-occur in the same artifact.
- **TTP (Tactics, Techniques, and Procedures):** The observable technical behaviors and tool signatures that constitute a cyber operation.
- **z_score:** A standardized metric derived from integer-ratio arithmetic and rendered as a decimal solely for display.

## 【Scientific Note】Peirce, Eco, and Grice Are Not Mysticism — They Are Sensor Ontologies

In the companion module `SemioticDetectorV2`, terminology drawn from **Charles Sanders Peirce** (sign, interpretant), **Umberto Eco** (code, encyclopedia), and **H. P. Grice** (implicature, cooperative principle) is used to model layers of contextual inference. These terms are **not metaphysical or mystical**. Think of them as spectral bands on a multi-sensor instrument: Peirce defines how raw voltage becomes a legible symbol; Eco calibrates the cultural and encyclopedic filter; Grice adjusts the noise-reduction protocol for intentional signals. `ForensicTechnicalDetector` is the base platinum resistance thermometer—it measures physical facts (regex matches) without interpretation. Together, the two modules form a fused instrument array: one channel quantifies physical presence, the other interprets semantic context.

---

**ESPAÑOL**

*Ruta del módulo:* `vigia/core/vigia_core_forensic_technical_detector.py`

## ¿Qué es este módulo?

Este módulo es un instrumento forense determinístico. Ingiere el texto crudo de artefactos forenses digitales —como registros del sistema, extractos de memoria o transcripciones de paquetes de red— e identifica indicadores técnicos explícitos llamados TTP (Tácticas, Técnicas y Procedimientos). No contiene modelos de aprendizaje automático, cajas negras estadísticas ni dependencias externas. En su lugar, se basa en reglas de patrón exactas (expresiones regulares) y aritmética de razones enteras para garantizar que un artefacto idéntico siempre produzca un informe idéntico. Funciona como el canal de medición física de un sistema de dos canales: el compañero `SemioticDetectorV2` maneja el contexto semántico, mientras que este módulo registra hechos técnicos duros.

## Conceptos Clave

| Concepto | Descripción | Relevancia Científica |
|---|---|---|
| Detección Determinística de TTP | Comparación de texto contra un catálogo de indicadores técnicos explícitos (p. ej., firmas de línea de comandos, claves de registro, secuencias de llamadas a API). | Elimina la variabilidad del observador; la misma evidencia produce las mismas conclusiones. |
| Aritmética de Razón Entera (`Fraction`) | Todas las puntuaciones internas se mantienen como fracciones exactas (pares de enteros: numerador/denominador). | Garantiza la reproducibilidad y evita artefactos de redondeo propios de la representación en coma flotante. |
| Artefacto Forense | Cualquier objeto digital recolectado como evidencia: archivos de registro, sectores de disco, capturas de paquetes o páginas de memoria. | La muestra de entrada bajo medición. |
| Trazabilidad por Regex Explícita | Cada coincidencia positiva puede rastrearse hasta una regla de expresión regular específica y legible por humanos. | Completa auditoría; sin pesos opacos ni capas ocultas. |
| Puntuación por Sinergia (`SYNERGY_STEP`, `MAX_SYNERGY`) | Cuando aparecen juntos varios indicadores corroboradores, la puntuación se incrementa en pasos enteros discretos hasta un techo. | Refleja el peso evidencial combinado sin aproximaciones continuas (flotantes). |
| `z_score` de Visualización | El resultado final en razón entera se convierte a número decimal **solo** para la salida en pantalla o archivo. | Visualización legible para humanos; el valor subyacente permanece como racional exacto. |

**Constantes y Configuración**

| Constante | Representación Interna | Propósito |
|---|---|---|
| `BASE_Z` | Entero | Desplazamiento base inicial de la puntuación. |
| `MAX_Z` | Entero | Cota superior absoluta de la puntuación técnica. |
| `SYNERGY_STEP` | Entero | Incremento entero discreto otorgado por cada indicador corroborador adicional. |
| `MAX_SYNERGY` | Entero | Bonificación máxima total que la sinergia puede aportar. |
| `TYPE_TOOL` | Cadena (etiqueta categórica) | Etiqueta que identifica la clase de indicador “uso de herramienta.” |

**Componentes Principales**

| Nombre | Función | Entrada → Salida |
|---|---|---|
| `ForensicTechnicalDetector` | Clase sensor determinístico | Se inicializa con catálogo de reglas e invariantes. |
| `analyze()` | Método de medición | Acepta texto de artefacto forense → devuelve diccionario de resultados (internos en razón entera + `z_score` de visualización). |

## Glosario

- **Artefacto (Forense):** Objeto digital preservado como evidencia durante una investigación.
- **Expresión Regular (Regex):** Lenguaje formal de reconocimiento de patrones; aquí actúa como un tamiz determinístico para evidencia textual.
- **Fraction:** Representación de número racional mediante dos enteros (numerador y denominador), asegurando aritmética exacta.
- **Invariante Determinista:** Garantía lógica de que la misma entrada, procesada por el mismo algoritmo, siempre produce la misma salida.
- **Sinergia:** Ganancia evidencial incremental que se produce cuando múltiples indicadores independientes coocurren en un mismo artefacto.
- **TTP (Tácticas, Técnicas y Procedimientos):** Comportamientos técnicos observables y firmas de herramientas que constituyen una operación cibernética.
- **z_score:** Métrica estandarizada derivada de aritmética de razón entera y representada como decimal únicamente para visualización.

## 【Nota Científica】Peirce, Eco y Grice no son misticismo: son ontologías de sensor

En el módulo complementario `SemioticDetectorV2`, se emplea terminología derivada de **Charles Sanders Peirce** (signo, interpretante), **Umberto Eco** (código, enciclopedia) y **H. P. Grice** (implicatura, principio cooperativo) para modelar capas de inferencia contextual. Estos términos **no son metafísicos ni místicos**. Piense en ellos como bandas espectrales de un instrumento multisensor: Peirce define cómo un voltaje crudo se convierte en símbolo legible; Eco calibra el filtro cultural y enciclopédico; Grice ajusta el protocolo de reducción de ruido para señales intencionales. `ForensicTechnicalDetector` es el termómetro de resistencia de platino base: mide hechos físicos (coincidencias de regex) sin interpretación. Juntos, ambos módulos forman un arreglo fusionado de instrumentos: un canal cuantifica la presencia física; el otro interpreta el contexto semántico.

---

**РУССКИЙ**

*Путь к модулю:* `vigia/core/vigia_core_forensic_technical_detector.py`

## Что это за модуль?

Этот модуль — детерминированный криминалистический инструмент. Он принимает исходный текст цифровых следовых артефактов — таких как системные журналы, дампы памяти или транскрипты сетевых пакетов — и выявляет явные технические индикаторы, называемые TTP (тактики, техники и процедуры). В нём отсутствуют модели машинного обучения, статистические «чёрные ящики» и внешние зависимости. Вместо этого используются точные правила поиска (регулярные выражения) и арифметика целочисленных отношений (`Fraction`), гарантирующие, что одинаковый артефакт всегда даёт одинаковый отчёт. Модуль работает как физический измерительный канал двухканальной системы: сопутствующий `SemioticDetectorV2` обрабатывает семантический контекст, а данный модуль фиксирует жёсткие технические факты.

## Ключевые понятия

| Понятие | Описание | Научное значение |
|---|---|---|
| Детерминированное обнаружение TTP | Сопоставление текста с каталогом явных технических индикаторов (например, сигнатуры командной строки, ключи реестра, последовательности вызовов API). | Устраняет вариативность наблюдателя; одинаковые доказательства дают одинаковые выводы. |
| Арифметика целочисленных отношений (`Fraction`) | Все внутренние оценки хранятся в виде точных дробей (пар целых чисел: числитель/знаменатель). | Гарантирует воспроизводимость и исключает ошибки округления, присущие числам с плавающей запятой. |
| Следовой артефакт | Любой цифровой объект, собранный в качестве доказательства: файлы журналов, секторы диска, дампы трафика или страницы памяти. | Исследуемый входной образец. |
| Прослеживаемость явных регулярных выражений | Каждое положительное совпадение может быть отнесено к конкретному, читаемому человеком правилу регулярного выражения. | Полная аудиторская прозрачность; нет непрозрачных весов или скрытых слоёв. |
| Синергетическое начисление (`SYNERGY_STEP`, `MAX_SYNERGY`) | При совместном появлении нескольких подтверждающих индикаторов оценка увеличивается дискретными целочисленными шагами до потолка. | Отражает совокупный доказательственный вес без непрерывных (дробных) приближений. |
| Отображаемый `z_score` | Итоговое значение в виде целочисленного отношения преобразуется в десятичное число **только** для вывода на экран или в файл. | Читаемое человеком представление; базовое значение остаётся точной дробью. |

**Константы и конфигурация**

| Константа | Внутреннее представление | Назначение |
|---|---|---|
| `BASE_Z` | Целое число | Начальное базовое смещение оценки. |
| `MAX_Z` | Целое число | Абсолютный верхний предел технической оценки. |
| `SYNERGY_STEP` | Целое число | Дискретное целочисленное приращение за каждый дополнительный подтверждающий индикатор. |
| `MAX_SYNERGY` | Целое число | Максимальный суммарный бонус, который может дать синергия. |
| `TYPE_TOOL` | Строка (категориальная метка) | Метка, идентифицирующая класс индикаторов «использование инструмента». |

**Основные компоненты**

| Имя | Роль | Вход → Выход |
|---|---|---|
| `ForensicTechnicalDetector` | Класс детерминированного сенсора | Инициализируется каталогом правил и инвариантами. |
| `analyze()` | Метод измерения | Принимает текст следового артефакта → возвращает словарь результатов (внутренние дроби + отображаемый `z_score`). |

## Глоссарий

- **Артефакт (следовой):** Цифровой объект, сохранённый в качестве доказательства в ходе расследования.
- **Детерминированный инвариант:** Логическая гарантия того, что одинаковый вход, обработанный одинаковым алгоритмом, всегда даёт одинаковый выход.
- **Дробь (`Fraction`):** Представление рационального числа парой целых чисел (числитель и знаменатель), обеспечивающее точную арифметику.
- **Регулярное выражение (Regex):** Формальный язык поиска по шаблону; здесь выступает в роли детерминированного сита для текстовых доказательств.
- **Синергия:** Инкрементальный доказательственный прирост, возникающий при совместном появлении нескольких независимых индикаторов в одном артефакте.
- **TTP (тактики, техники и процедуры):** Наблюдаемые технические действия и сигнатуры инструментов, составляющие кибероперацию.
- **z_score:** Стандартизированная метрика, выведенная из арифметики целочисленных отношений и представленная в десятичном виде исключительно для отображения.

## 【Научное Примечание】Пирс, Эко и Грайс — не мистика, а онтологии сенсоров

В сопутствующем модуле `SemioticDetectorV2` терминология, заимствованная у **Чарльза Сандерса Пирса** (знак, интерпретант), **Умберто Эко** (код, энциклопедия) и **Г. П. Грайса** (импликатура, кооперативный принцип), используется для моделирования уровней контекстуального вывода. Эти термины **не являются метафизическими или мистическими**. Воспринимайте их как спектральные полосы мультисенсорного прибора: Пирс определяет, как сырой сигнал превращается в читаемый символ; Эко калибрует культурный фильтр; Грайс настраивает протокол подавления шума для целенаправленных сигналов. `ForensicTechnicalDetector` — это базовый платиновый резистивный термометр: он измеряет физические факты (совпадения регулярных выражений) без интерпретации. Вместе оба модуля образуют совмещённый измерительный комплекс: один канал количественно фиксирует физическое присутствие, другой интерпретирует семантический контекст.

---

**中文**

*模块路径：* `vigia/core/vigia_core_forensic_technical_detector.py`

## 这是什么模块？

本模块是一台确定性取证传感器。它读取数字取证工件的原始文本——例如系统日志、内存提取片段或网络数据包转录——并识别被称为 TTP（战术、技术与程序）的显性技术指标。模块内不含机器学习模型、统计黑箱或外部依赖。相反，它依赖精确的模式规则（正则表达式）与整数比算术，确保相同的取证工件永远生成相同的报告。它在一个双通道系统中充当物理测量通道：配套的 `SemioticDetectorV2` 负责语义上下文，而本模块负责记录硬性技术事实。

## 核心概念

| 概念 | 说明 | 科学意义 |
|---|---|---|
| 确定性 TTP 检测 | 将文本与显性技术指标目录进行匹配（例如命令行签名、注册表键、API 调用序列）。 | 消除观察者差异性；相同证据产生相同结论。 |
| 整数比算术（`Fraction`） | 所有内部分数均保存为精确分数（一对整数：分子/分母）。 | 保证可重复性，避免浮点表示固有的舍入误差。 |
| 取证工件 | 任何作为证据采集的数字对象：日志文件、磁盘扇区、数据包捕获或内存页。 | 待测量的输入样本。 |
| 显式正则追溯 | 每一次正向匹配均可回溯到具体、可人工阅读的正则表达式规则。 | 完全可审计；不存在不透明权重或隐藏层。 |
| 协同计分（`SYNERGY_STEP`、`MAX_SYNERGY`） | 当多个相互印证的指标同时出现时，分数按离散整数步长递增，直至上限。 | 在不使用连续（浮点）近似的前提下，反映综合证据权重。 |
| 展示用 `z_score` | 最终的整数比结果仅在输出到屏幕或文件时才转换为十进制数。 | 面向人类的可读展示；其底层值仍是精确有理数。 |

**常量与配置**

| 常量 | 内部表示 | 用途 |
|---|---|---|
| `BASE_Z` | 整数 | 分数的初始基准偏移量。 |
| `MAX_Z` | 整数 | 技术分数的绝对上限。 |
| `SYNERGY_STEP` | 整数 | 每增加一个印证指标所给予的离散整数增量。 |
| `MAX_SYNERGY` | 整数 | 协同效应所能提供的最大总加分。 |
| `TYPE_TOOL` | 字符串（类别标签） | 标识“工具使用”这一类别的标签。 |

**核心组件**

| 名称 | 角色 | 输入 → 输出 |
|---|---|---|
| `ForensicTechnicalDetector` | 确定性传感器类 | 以规则目录与不变量初始化。 |
| `analyze()` | 测量方法 | 接受取证工件文本 → 返回结果字典（整数比内部值 + 展示用 `z_score`）。 |

## 术语表

- **取证工件（Forensic Artifact）：** 调查过程中被保存为证据的数字对象。
- **确定性不变量（Deterministic Invariant）：** 逻辑保证：相同输入经相同算法处理，永远产生相同输出。
- **分数（Fraction）：** 以两个整数（分子与分母）表示有理数，确保算术完全精确。
- **正则表达式（Regex）：** 一种形式化的模式匹配语言；在此处充当文本证据的确定性筛子。
- **协同（Synergy）：** 多个独立指标在同一取证工件中共同出现时产生的增量证据增益。
- **TTP（战术、技术与程序）：** 构成网络行动的、可观察的技术行为与工具签名。
- **z_score：** 由整数比算术导出的标准化指标，仅在展示时转换为十进制小数。
- **逻辑断裂：** 当技术信号与语义上下文之间出现确定性断层时的状态；本模块通过硬指标匹配避免此类断裂。

## 【科学说明】皮尔士、艾柯与格赖斯不是神秘主义——它们是传感器本体论

在配套模块 `SemioticDetectorV2` 中，借用了 **C·S·皮尔士**（符号、阐释项）、**艾柯**（符码、百科全书）与 **格赖斯**（隐含意义、合作原则）的术语来建模不同层次的语境推断。这些术语**不是形而上学或神秘主义概念**。请将它们想象成多波段传感器上的光谱频段：皮尔士定义了原始电压如何成为可读符号；艾柯校准了文化与百科全书式滤镜；格赖斯调节了针对意图信号的降噪协议。`ForensicTechnicalDetector` 则是底层的铂电阻温度计：它测量物理事实（正则匹配），而不进行解释。两个模块共同构成了一套融合仪器阵列——一个通道量化物理存在，另一个通道解读语义上下文。

---



---


- 4 languages: yes.
- What Is This Module?: yes.
- Key concepts with tables: yes.
- Glossary: yes.
- License line included exactly.
- No floating-point math explanations. Emphasized deterministic integer arithmetic / Fraction. I used "integer-ratio arithmetic" / "razones enteras" / "целочисленных отношений" / "整数比算术". I explicitly said z_score is float display only and internal is integer fraction. This meets requirement.
- Module path: included at top of each section.
- Concise but thorough: looks good.

Double-check Chinese terms:
- 艾柯: used.
- 格赖斯: used.
- 取证工件: used
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
