<!--
VIGIA Academic Documentation
Module: 9e2e4cde
Batch ID: vigia-doc-0081-9e2e4cde
Generated: 2026-05-20T14:56:47.861995+00:00
-->

## ENGLISH

### What Is This Module?

This module is a deterministic forensic instrument. It ingests the raw text of digital forensic artifacts — such as system logs, memory extracts, or network packet transcripts — and identifies explicit technical indicators called TTPs (Tactics, Techniques, and Procedures). It contains no machine-learning models, no statistical black boxes, and no external dependencies. Instead, it relies on exact pattern rules (regular expressions) and integer-ratio arithmetic to guarantee that an identical artifact always yields an identical report. It operates as the physical-measurement channel of a two-channel system: the companion `SemioticDetectorV2` handles semantic context, while this module records hard technical facts.

### Key Concepts

| Concept | Description | Scientific Relevance |
|---|---|---|
| Deterministic TTP Detection | Matching text against a catalog of explicit technical indicators (command-line signatures, registry keys, API call sequences). | Eliminates observer variability; identical evidence produces identical conclusions. |
| Integer-Ratio Arithmetic (`Fraction`) | All internal scores are maintained as exact fractions (pairs of integers: numerator/denominator). | Guarantees reproducibility and avoids rounding artifacts inherent in floating-point representations. |
| Forensic Artifact | Any digital object collected as evidence: log files, disk sectors, packet captures, or memory pages. | The input specimen under measurement. |
| Explicit Regex Traceability | Every positive match can be traced back to a specific, human-readable regular-expression rule. | Full auditability; no opaque weights or hidden layers. |
| Synergy Scoring (`SYNERGY_STEP`, `MAX_SYNERGY`) | When multiple corroborating indicators appear together, the score increments by discrete integer steps up to a ceiling. | Reflects combined evidentiary weight without continuous approximations. |
| Display `z_score` | The final integer-ratio result is converted to a decimal number **only** for screen or file output. | Human-readable display; the underlying value remains an exact rational. |
| `BASE_Z` / `MAX_Z` | Integer baseline offset and absolute upper bound of the technical score. | Deterministic score boundaries enforced at the integer level. |
| `ForensicTechnicalDetector` | Core deterministic sensor class. | Initializes with rule catalog and invariants; exposes `analyze()`. |
| `analyze()` | Main measurement method. | Accepts artifact text → returns result dictionary with integer-ratio internals and display `z_score`. |

> **【Scientific Note】**
> Terminology from **Charles Sanders Peirce** (sign, interpretant), **Umberto Eco** (code, encyclopedia), and **H. P. Grice** (implicature, cooperative principle) is used in the companion `SemioticDetectorV2` to model layers of contextual inference. These terms are not metaphysical. Think of them as spectral bands on a multi-sensor instrument: Peirce defines how raw voltage becomes a legible symbol; Eco calibrates the cultural filter; Grice adjusts noise reduction for intentional signals. `ForensicTechnicalDetector` is the base platinum resistance thermometer — it measures physical facts (regex matches) without interpretation. Together, the two modules form a fused instrument array: one channel for physical presence, one for semantic context. Deterministic integer arithmetic ensures every measurement is courtroom-reproducible.

### Glossary

1. **Forensic Artifact** — Any digital object preserved as evidence during an investigation.
2. **TTP (Tactics, Techniques, and Procedures)** — The observable technical behaviors and tool signatures constituting a cyber operation.
3. **Regex (Regular Expression)** — A formal pattern-matching language acting as a deterministic sieve for textual evidence.
4. **Fraction** — A rational-number representation using two integers (numerator/denominator), ensuring exact arithmetic.
5. **Deterministic Invariant** — A logical guarantee that the same input, processed by the same algorithm, always produces the same output.
6. **Synergy** — The incremental evidentiary gain produced when multiple independent indicators co-occur in the same artifact.
7. **z_score** — A standardized metric derived from integer-ratio arithmetic, rendered as decimal solely for display.
8. **BASE_Z** — The integer baseline score offset from which all TTP scoring begins.
9. **SYNERGY_STEP** — The discrete integer increment awarded for each additional corroborating indicator.
10. **TYPE_TOOL** — Categorical string label identifying the indicator class "tool usage."

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## ESPAÑOL

### ¿Qué es este módulo?

Este módulo es un instrumento forense determinista. Ingiere el texto crudo de artefactos forenses digitales — registros del sistema, extractos de memoria o transcripciones de paquetes de red — e identifica indicadores técnicos explícitos llamados TTP (Tácticas, Técnicas y Procedimientos). No contiene modelos de aprendizaje automático, cajas negras estadísticas ni dependencias externas. En su lugar, se basa en reglas de patrón exactas (expresiones regulares) y aritmética de razones enteras para garantizar que un artefacto idéntico siempre produzca un informe idéntico. Funciona como el canal de medición física de un sistema de dos canales: el compañero `SemioticDetectorV2` maneja el contexto semántico, mientras que este módulo registra hechos técnicos duros.

### Conceptos clave

| Concepto | Descripción | Relevancia científica |
|---|---|---|
| Detección determinista de TTP | Comparación de texto contra un catálogo de indicadores técnicos explícitos (firmas de línea de comandos, claves de registro, secuencias de llamadas a API). | Elimina la variabilidad del observador; la misma evidencia produce las mismas conclusiones. |
| Aritmética de razón entera (`Fraction`) | Todas las puntuaciones internas se mantienen como fracciones exactas (pares de enteros: numerador/denominador). | Garantiza la reproducibilidad y evita artefactos de redondeo. |
| Artefacto forense | Cualquier objeto digital recolectado como evidencia: archivos de registro, sectores de disco, capturas de paquetes o páginas de memoria. | La muestra de entrada bajo medición. |
| Trazabilidad por regex explícita | Cada coincidencia positiva puede rastrearse hasta una regla de expresión regular específica y legible. | Auditoría completa; sin pesos opacos ni capas ocultas. |
| Puntuación por sinergia (`SYNERGY_STEP`, `MAX_SYNERGY`) | Cuando aparecen juntos varios indicadores corroboradores, la puntuación se incrementa en pasos enteros discretos hasta un techo. | Refleja el peso evidencial combinado sin aproximaciones continuas. |
| `z_score` de visualización | El resultado final en razón entera se convierte a decimal **solo** para la salida en pantalla o archivo. | Visualización legible; el valor subyacente permanece como racional exacto. |
| `BASE_Z` / `MAX_Z` | Desplazamiento base entero y cota superior absoluta de la puntuación técnica. | Límites de puntuación deterministas aplicados a nivel entero. |
| `ForensicTechnicalDetector` | Clase sensor determinista central. | Se inicializa con catálogo de reglas e invariantes; expone `analyze()`. |
| `analyze()` | Método de medición principal. | Acepta texto de artefacto → devuelve diccionario de resultados con internos en razón entera y `z_score` de visualización. |

> **【Nota Científica】**
> La terminología de **Charles Sanders Peirce** (signo, interpretante), **Umberto Eco** (código, enciclopedia) y **H. P. Grice** (implicatura, principio cooperativo) se emplea en el módulo complementario `SemioticDetectorV2` para modelar capas de inferencia contextual. Estos términos no son metafísicos. Piense en ellos como bandas espectrales de un instrumento multisensor: Peirce define cómo un voltaje crudo se convierte en símbolo legible; Eco calibra el filtro cultural; Grice ajusta la reducción de ruido para señales intencionales. `ForensicTechnicalDetector` es el termómetro de resistencia de platino base: mide hechos físicos (coincidencias de regex) sin interpretación. La aritmética entera determinista garantiza que cada medición sea reproducible en sede judicial.

### Glosario

1. **Artefacto forense** — Objeto digital preservado como evidencia durante una investigación.
2. **TTP (Tácticas, Técnicas y Procedimientos)** — Comportamientos técnicos observables y firmas de herramientas que constituyen una operación cibernética.
3. **Expresión regular (Regex)** — Lenguaje formal de reconocimiento de patrones que actúa como tamiz determinista para evidencia textual.
4. **Fraction** — Representación de número racional mediante dos enteros (numerador/denominador), asegurando aritmética exacta.
5. **Invariante determinista** — Garantía lógica de que la misma entrada procesada por el mismo algoritmo siempre produce la misma salida.
6. **Sinergia** — Ganancia evidencial incremental cuando múltiples indicadores independientes coocurren en un mismo artefacto.
7. **z_score** — Métrica estandarizada derivada de aritmética de razón entera, representada como decimal únicamente para visualización.
8. **BASE_Z** — Desplazamiento base entero desde el que comienza toda puntuación de TTP.
9. **SYNERGY_STEP** — Incremento entero discreto otorgado por cada indicador corroborador adicional.
10. **TYPE_TOOL** — Etiqueta categórica de cadena que identifica la clase de indicador "uso de herramienta".

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## РУССКИЙ

### Что это за модуль?

Этот модуль — детерминированный криминалистический инструмент. Он принимает исходный текст цифровых форензических артефактов — системных журналов, дампов памяти или транскриптов сетевых пакетов — и выявляет явные технические индикаторы, называемые TTP (тактики, техники и процедуры). В нём отсутствуют модели машинного обучения, статистические «чёрные ящики» и внешние зависимости. Вместо этого используются точные правила поиска по шаблону (регулярные выражения) и арифметика целочисленных отношений (`Fraction`), гарантирующие, что одинаковый артефакт всегда даёт одинаковый отчёт. Модуль работает как физический измерительный канал двухканальной системы: сопутствующий `SemioticDetectorV2` обрабатывает семантический контекст, а данный модуль фиксирует жёсткие технические факты.

### Ключевые концепции

| Концепция | Описание | Научное значение |
|---|---|---|
| Детерминированное обнаружение TTP | Сопоставление текста с каталогом явных технических индикаторов (сигнатуры командной строки, ключи реестра, последовательности вызовов API). | Устраняет вариативность наблюдателя; одинаковые доказательства дают одинаковые выводы. |
| Арифметика целочисленных отношений (`Fraction`) | Все внутренние оценки хранятся в виде точных дробей (пар целых чисел: числитель/знаменатель). | Гарантирует воспроизводимость и исключает ошибки округления. |
| Форензический артефакт | Любой цифровой объект, собранный в качестве доказательства: файлы журналов, секторы диска, дампы трафика или страницы памяти. | Исследуемый входной образец. |
| Прослеживаемость явных регулярных выражений | Каждое положительное совпадение может быть отнесено к конкретному читаемому правилу. | Полная аудиторская прозрачность; нет непрозрачных весов или скрытых слоёв. |
| Синергетическое начисление (`SYNERGY_STEP`, `MAX_SYNERGY`) | При совместном появлении нескольких подтверждающих индикаторов оценка увеличивается дискретными целочисленными шагами до потолка. | Отражает совокупный доказательственный вес без непрерывных приближений. |
| Отображаемый `z_score` | Итоговое значение в виде целочисленного отношения преобразуется в десятичное число **только** для вывода. | Читаемое человеком представление; базовое значение остаётся точной дробью. |
| `BASE_Z` / `MAX_Z` | Целочисленное базовое смещение и абсолютный верхний предел технической оценки. | Детерминированные границы оценки на целочисленном уровне. |
| `ForensicTechnicalDetector` | Класс детерминированного сенсора. | Инициализируется каталогом правил и инвариантами; предоставляет `analyze()`. |
| `analyze()` | Основной метод измерения. | Принимает текст артефакта → возвращает словарь результатов с целочисленными дробями и отображаемым `z_score`. |

> **【Научное примечание】**
> Терминология **Чарльза Сандерса Пирса** (знак, интерпретант), **Эко** (код, энциклопедия) и **Грайса** (импликатура, кооперативный принцип) применяется в сопутствующем модуле `SemioticDetectorV2` для моделирования уровней контекстуального вывода. Эти термины не являются метафизическими. Воспринимайте их как спектральные полосы мультисенсорного прибора: Пирс определяет, как сырой сигнал превращается в читаемый символ; Эко калибрует культурный фильтр; Грайс настраивает протокол подавления шума для целенаправленных сигналов. `ForensicTechnicalDetector` — это базовый платиновый резистивный термометр: он измеряет физические факты (совпадения регулярных выражений) без интерпретации. Детерминированная целочисленная арифметика гарантирует воспроизводимость в суде.

### Глоссарий

1. **Форензический артефакт** — Цифровой объект, сохранённый в качестве доказательства в ходе расследования.
2. **TTP (тактики, техники и процедуры)** — Наблюдаемые технические действия и сигнатуры инструментов, составляющие кибероперацию.
3. **Регулярное выражение (Regex)** — Формальный язык поиска по шаблону; здесь выступает в роли детерминированного сита для текстовых доказательств.
4. **Дробь (`Fraction`)** — Представление рационального числа парой целых чисел, обеспечивающее точную арифметику.
5. **Детерминированный инвариант** — Логическая гарантия того, что одинаковый вход, обработанный одинаковым алгоритмом, всегда даёт одинаковый выход.
6. **Синергия** — Инкрементальный доказательственный прирост при совместном появлении нескольких независимых индикаторов в одном артефакте.
7. **z_score** — Стандартизированная метрика, выведенная из арифметики целочисленных отношений и представленная в десятичном виде исключительно для отображения.
8. **BASE_Z** — Целочисленное базовое смещение, с которого начинается вся оценка TTP.
9. **SYNERGY_STEP** — Дискретное целочисленное приращение за каждый дополнительный подтверждающий индикатор.
10. **TYPE_TOOL** — Строковая категориальная метка, идентифицирующая класс индикаторов «использование инструмента».

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## 中文

### 这是什么模块？

本模块是一台确定性取证传感器。它读取数字取证工件的原始文本——系统日志、内存提取片段或网络数据包转录——并识别被称为 TTP（战术、技术与程序）的显性技术指标。模块内不含机器学习模型、统计黑箱或外部依赖。相反，它依赖精确的模式规则（正则表达式）与整数比算术，确保相同的取证工件永远生成相同的报告。它在双通道系统中充当物理测量通道：配套的 `SemioticDetectorV2` 负责语义上下文，而本模块负责记录硬性技术事实。

### 关键概念

| 概念 | 说明 | 科学意义 |
|---|---|---|
| 确定性 TTP 检测 | 将文本与显性技术指标目录进行匹配（命令行签名、注册表键、API 调用序列）。 | 消除观察者差异性；相同证据产生相同结论。 |
| 整数比算术（`Fraction`） | 所有内部分数均保存为精确分数（一对整数：分子/分母）。 | 保证可重复性，避免舍入误差。 |
| 取证工件 | 任何作为证据采集的数字对象：日志文件、磁盘扇区、数据包捕获或内存页。 | 待测量的输入样本。 |
| 显式正则追溯 | 每一次正向匹配均可回溯到具体、可人工阅读的正则表达式规则。 | 完全可审计；不存在不透明权重或隐藏层。 |
| 协同计分（`SYNERGY_STEP`、`MAX_SYNERGY`） | 当多个相互印证的指标同时出现时，分数按离散整数步长递增，直至上限。 | 在不使用连续近似的前提下反映综合证据权重。 |
| 展示用 `z_score` | 最终的整数比结果仅在输出到屏幕或文件时才转换为十进制数。 | 面向人类的可读展示；底层值仍是精确有理数。 |
| `BASE_Z` / `MAX_Z` | 整数基准偏移量与技术分数的绝对上限。 | 在整数层面强制执行的确定性分数边界。 |
| `ForensicTechnicalDetector` | 核心确定性传感器类。 | 以规则目录与不变量初始化；提供 `analyze()` 方法。 |
| `analyze()` | 主测量方法。 | 接受取证工件文本 → 返回包含整数比内部值与展示用 `z_score` 的结果字典。 |

> **【科学说明】**
> **皮尔斯**（Peirce）的符号与阐释项、**艾柯**（Eco）的符码与百科全书、**格赖斯**（Grice）的隐含意义与合作原则，在配套模块 `SemioticDetectorV2` 中用于建模不同层次的语境推断。这些术语并非神秘主义，而是形式化的分析机制。请将它们想象成多波段传感器上的光谱频段：皮尔斯定义了原始信号如何成为可读符号；艾柯校准了文化过滤层；格赖斯调节了针对意图信号的降噪协议。`ForensicTechnicalDetector` 则是底层的铂电阻温度计——它测量物理事实（正则匹配），而不进行语义解释。精确整数运算确保法庭可重现性，取证工件链中的逻辑断裂以整数标志事件的形式被检测。

### 词汇表

1. **取证工件** — 调查过程中被保存为证据的数字对象。
2. **TTP（战术、技术与程序）** — 构成网络行动的、可观察的技术行为与工具签名。
3. **正则表达式（Regex）** — 一种形式化的模式匹配语言；在此处充当文本证据的确定性筛子。
4. **分数（Fraction）** — 以两个整数（分子与分母）表示有理数，确保算术完全精确。
5. **确定性不变量** — 逻辑保证：相同输入经相同算法处理，永远产生相同输出。
6. **协同（Synergy）** — 多个独立指标在同一取证工件中共同出现时产生的增量证据增益。
7. **z_score** — 由整数比算术导出的标准化指标，仅在展示时转换为十进制小数。
8. **BASE_Z** — 所有 TTP 计分的整数基准偏移起点。
9. **SYNERGY_STEP** — 每增加一个印证指标所给予的离散整数增量。
10. **逻辑断裂** — 当技术信号与语义上下文之间出现确定性断层时的状态；本模块通过硬性指标匹配避免此类断裂。

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
