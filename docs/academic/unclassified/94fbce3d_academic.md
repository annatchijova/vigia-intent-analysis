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

> This module employs terminology derived from **Charles Sanders Peirce**, **Umberto Eco**, and **H. P. Grice**. These names refer to formal logical frameworks for sign classification and communicative coherence, not to metaphysical doctrines. Think of the detector as a sensor array: Peirce's triad provides the *wavelength channels*, Eco's codes provide the *spectral calibration curves*, and Grice's maxims provide the *noise-rejection thresholds*. The module does not "interpret meaning" in a human sense; it applies deterministic integer filters to forensic artifacts, producing reproducible vectors. The semiotic vocabulary is merely the taxonomy printed on the instrument panel.

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

---

## РУССКИЙ

### Что это за модуль?

Данный модуль — детерминированный движок форензического анализа, обнаруживающий значимые паттерны в цифровых артефактах — таких как записи журналов, фрагменты файлов или строки в памяти — с использованием концепций формальной семиотики. Он рассматривает артефакт как структурированный сигнал и исследует его через точное сопоставление, приближённое (нечёткое) сопоставление, комбинаторное усиление (синергию) и темпоральную логику (последовательности).

Все оценки вычисляются как целочисленные отношения (числитель ÷ знаменатель), что гарантирует: каждое выполнение на одних и тех же входных данных порождает побитово идентичные результаты. Модуль не использует машинное обучение, статистический вывод или математику с плавающей запятой. Конфигурационные константы `SIMILARITY_THRESHOLD_NUM` / `_DEN` выражают пороги как несократимые целочисленные дроби — никогда как приближения с плавающей запятой — сохраняя гарантии воспроизводимости в соответствии со стандартом Добера.

Пять этапов конвейера анализа — сопоставление регулярных выражений, нечёткое сопоставление, анализ синергии, проверка последовательностей и сборка FSV — образуют полностью детерминированную цепочку обработки, где каждый этап оперирует исключительно целочисленными счётчиками и индексами.

### Ключевые концепции

#### Основные компоненты
| Компонент | Роль | Детерминированная гарантия |
|---|---|---|
| PatternMatch | Записывает одно попадание паттерна, включая позицию, следственную фазу и оценку | Оценка хранится как целочисленная пара (числитель, знаменатель) |
| SynergyEvent | Фиксирует взаимное усиление двух или более паттернов | Инициируется только предопределённой целочисленной логикой в `SYNERGY_RULES` |
| SequenceEvent | Захватывает упорядоченные цепочки паттернов во времени | Оценивается через целочисленные временны́е окна |
| SessionPatternMemory | Сохраняет историю недавних паттернов в ограниченном временном диапазоне | Изменения состояния управляются правилами, никогда вероятностями |
| SemioticDetectorV2 | Главный движок, оркестрирующий regex, нечёткий поиск, синергию, последовательности и сборку FSV | Вся внутренняя оценка использует рациональную целочисленную арифметику |

#### Конвейер анализа
| Этап | Механизм | Тип арифметики |
|---|---|---|
| Сопоставление regex | Точное выравнивание паттернов со строками артефакта | Целочисленные позиции индексов |
| Нечёткое сопоставление | Токенизация n-граммами + ограниченное расстояние Левенштейна | Целочисленное расстояние ≤ `MAX_LEVENSHTEIN` |
| Анализ синергии | Проверка пересечения с `SYNERGY_RULES` | Целочисленные счётчики |
| Проверка последовательностей | Упорядоченная валидация паттернов внутри `WINDOW_SIZE` | Целочисленная темпоральная логика |
| Сборка FSV | Компоновка выходов всех предыдущих этапов в единый вектор | Целочисленные векторы компонент |

> **【Научное примечание】**
> Терминология Пирса, Эко и Грайса — это не мистика, а формальная аналитическая механика. Как спектрометр преобразует фотонные взаимодействия в дискретные целочисленные отсчёты, этот модуль преобразует сигналы улик в детерминированные целочисленные оценки. Целочисленная арифметика гарантирует воспроизводимость в суде без округлений и аппроксимаций. Любое нарушение логики в цепочке артефактов фиксируется как целочисленный флаг, а не интуитивное суждение.

### Глоссарий
1. **Семиотика** — Формальное изучение знаков, символов и их интерпретации; здесь предоставляет логическую таксономию для классификации паттернов.
2. **Форензический сигнальный вектор (FSV)** — Детерминированный целочисленный составной дескриптор, суммирующий все обнаруженные знаки в одном артефакте.
3. **Рациональная арифметика** — Вычисления строго с отношениями целых чисел (числитель/знаменатель), устраняющие риски воспроизводимости при представлении с плавающей запятой.
4. **N-грамма** — Непрерывная последовательность из *n* элементов, извлечённая из текстовой строки; используется для нечёткого сопоставления.
5. **Расстояние Левенштейна** — Минимальное количество вставок, удалений или замен одного символа, необходимых для преобразования одной строки в другую.
6. **Синергия** — Детерминированный эффект усиления — аддитивный или мультипликативный — при совместном появлении коррелированных паттернов.
7. **Темпоральная память** — Ограниченный буфер, сохраняющий недавние появления паттернов для оценки правил последовательностей.
8. **Форензический артефакт** — Любой цифровой объект под исследованием (строка журнала, фрагмент памяти, сегмент файла).
9. **Детерминированная целочисленная арифметика** — Точные вычисления без ошибок округления с плавающей запятой.
10. **Стандарт Добера** — Правовой критерий допустимости научных доказательств, требующий воспроизводимости.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## 中文

### 这是什么模块？

本模块是一个确定性取证分析引擎，使用形式符号学概念检测数字取证工件——如日志条目、文件片段或内存字符串——中的有意义模式。它将取证工件视为结构化信号，通过精确匹配、近似（模糊）匹配、组合强化（协同）和时序逻辑（序列）对其进行分析。

所有分数均以整数比（分子÷分母）计算，保证对相同输入的每次执行产生逐位相同的结果。本模块不使用机器学习、统计推断或浮点数学。配置常量`SIMILARITY_THRESHOLD_NUM`/`_DEN`以不可约整数分数表示阈值——永不使用近似值——保持符合道伯特标准的可重现性保证。

分析流程的五个阶段——正则表达式匹配、模糊匹配、协同分析、序列检查和FSV组装——构成完全确定性的处理链，每个阶段仅操作整数计数器和索引。

### 关键概念

#### 核心组件
| 组件 | 作用 | 确定性保证 |
|---|---|---|
| PatternMatch | 记录单个模式命中，包括位置、调查阶段和分数 | 分数以整数对（分子、分母）存储 |
| SynergyEvent | 记录两个或多个模式相互强化的情况 | 仅由`SYNERGY_RULES`中预定义的整数逻辑触发 |
| SequenceEvent | 捕获跨时间的有序模式链 | 通过整数时间戳窗口评估 |
| SessionPatternMemory | 在有界时间跨度内保留最近的模式历史 | 状态变化由规则控制，从不依赖概率 |
| SemioticDetectorV2 | 编排正则表达式、模糊、协同、序列和FSV组装的主引擎 | 所有内部评分使用有理整数运算 |

#### 分析流程
| 阶段 | 机制 | 运算类型 |
|---|---|---|
| 正则表达式匹配 | 模式与取证工件字符串的精确对齐 | 整数索引位置 |
| 模糊匹配 | N-gram分词 + 有界Levenshtein距离 | 整数距离 ≤ `MAX_LEVENSHTEIN` |
| 协同分析 | 与`SYNERGY_RULES`的交集检查 | 整数计数器 |
| 序列检查 | `WINDOW_SIZE`内的有序模式验证 | 整数时序逻辑 |
| FSV组装 | 将所有前序阶段输出合成为统一向量 | 整数分量向量 |

> **【科学说明】**
> 皮尔斯（Peirce）、艾柯（Eco）和格赖斯（Grice）的术语并非神秘主义，而是形式化的分析机制。如同光谱仪将光子相互作用转换为离散整数计数，本模块将证据信号转换为确定性整数分数。精确整数运算确保法庭可重现性。取证工件链的逻辑断裂以整数标志事件形式被检测。

### 词汇表
1. **符号学** — 对符号、象征及其解释的形式研究；此处提供模式分类的逻辑分类法。
2. **取证信号向量（FSV）** — 汇总单个取证工件中所有检测符号的确定性整数复合描述符。
3. **有理数运算** — 严格以整数比（分子/分母）计算，消除浮点表示的可重现性隐患。
4. **N-gram** — 从文本字符串中提取的*n*个连续项的序列；此处用于模糊匹配。
5. **Levenshtein距离** — 将一个字符串转换为另一个字符串所需的最少单字符插入、删除或替换次数。
6. **协同效应** — 相关模式在同一窗口内共现时的确定性强化效果——加法或乘法。
7. **时间记忆** — 保留最近模式出现以便评估序列规则的有界缓冲区。
8. **取证工件** — 任何受检数字对象（日志行、内存片段、文件段）。
9. **精确整数运算** — 对整数进行精确计算，排除浮点表示误差。
10. **道伯特标准** — 要求可重现性的科学证据可采性法律标准。

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
