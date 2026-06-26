<!--
VIGIA Academic Documentation
Module: 8517382b
Batch ID: vigia-doc-0151-8517382b
Generated: 2026-05-20T14:56:47.876992+00:00
-->

---

## ENGLISH

### What Is This Module?
This module implements a **Gricean Maxim Violation Detector** for the VIGÍA forensic framework. It analyzes textual communication artifacts—statements, logs, chat transcripts, and narrative reports—and counts systematic violations of Grice's four cooperative maxims: Quantity, Quality, Relation, and Manner. Each violation is registered as an exact integer delta against fixed thresholds; no probabilistic scoring is used. When the cumulative violation count crosses an integer threshold, the module flags the communication artifact as exhibiting deliberate deceptive intent rather than cooperative communication.

The detector operates on the forensic principle that deliberate deception systematically violates at least one cooperative maxim. An analyst who provides too little information (Quantity), asserts unsupported claims (Quality), introduces irrelevant details (Relation), or communicates in deliberately obscure terms (Manner) is statistically distinguishable from a cooperative communicator. All detection thresholds are exact integers; all violation counts are exact integers. There are no probabilistic roundings.

### Key Concepts

| Concept | Definition | Technical Role |
|---|---|---|
| **Gricean Maxim** | One of four cooperative communication norms (Quantity, Quality, Relation, Manner) proposed by H. P. Grice. | The unit of analysis; each maxim is monitored by a dedicated detection rule. |
| **Violation Delta** | The exact integer increment added to a maxim's running count when a violation is detected. | Registered against a fixed integer threshold to trigger a deception flag. |
| **Fixed Threshold** | An exact integer value specifying the number of violations required to classify a communicative act as deceptive. | Prevents false positives from isolated, unintentional deviations. |
| **Cumulative Count** | The running exact integer total of violations across all four maxims. | The primary input to the admission/rejection gate. |
| **Deception Flag** | A binary (true/false) output set when the cumulative count exceeds the threshold. | The terminal signal emitted to the downstream forensic pipeline. |
| **Deterministic Integer Arithmetic** | All counting and threshold comparisons use exact integers. | Guarantees reproducibility: identical input text always produces the same violation counts. |

### Core Operations

| Operation | Purpose |
|---|---|
| `analyze_text()` | Runs all four maxim detectors on an input text; returns violation counts per maxim and cumulative total. |
| `check_quantity()` | Detects under-informativeness or over-elaboration beyond what the context requires. |
| `check_quality()` | Detects unsupported assertions or contradictions with known facts. |
| `check_relation()` | Detects irrelevant information inserted to distract or obscure. |
| `check_manner()` | Detects deliberate ambiguity, excessive verbosity, or unnecessarily obscure phrasing. |

### Glossary
1. **Cooperative Maxim** — One of Grice's four norms governing truthful, relevant, informative, and clear communication.
2. **Cumulative Violation Count** — The running exact integer total of detected maxim violations across all categories.
3. **Deception Flag** — A binary indicator set when violation counts exceed the integer threshold, signaling probable intentional deception.
4. **Deterministic Integer Arithmetic** — Computation using exact integer counts and fixed thresholds; no probabilistic scoring.
5. **Fixed Threshold** — An exact integer specifying the minimum violation count required to classify a communication as deceptive.
6. **Grice's Maxim of Manner** — The norm requiring communication to be orderly, unambiguous, and concise.
7. **Grice's Maxim of Quality** — The norm requiring truthfulness: assert only what you believe to be true and have evidence for.
8. **Grice's Maxim of Quantity** — The norm requiring informativeness: provide as much information as needed, but no more.
9. **Grice's Maxim of Relation** — The norm requiring relevance: contributions must be pertinent to the current exchange.
10. **Violation Delta** — The exact integer increment added to a maxim's count upon detection of a violation.

> **【Scientific Note】**
> Peirce/Eco/Grice terminology is NOT mysticism. Grice's cooperative maxims are empirically derived norms of communicative behavior. Their systematic violation is a measurable, reproducible signal: controlled studies show that deceptive communication statistically violates at least one maxim more frequently than cooperative communication. VIGÍA operationalizes this as an exact integer counting system, making the detection result fully auditable and reproducible.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## ESPAÑOL

### ¿Qué es este módulo?
Este módulo implementa un **Detector de Violaciones de Máximas de Grice** para el marco forense VIGÍA. Analiza artefactos de comunicación textual—declaraciones, registros, transcripciones de chat e informes narrativos—y cuenta violaciones sistemáticas de las cuatro máximas cooperativas de Grice: Cantidad, Calidad, Relación y Modo. Cada violación se registra como un delta entero exacto contra umbrales fijos; no se usa puntuación probabilística. Cuando el recuento acumulado de violaciones cruza un umbral entero, el módulo señala el artefacto de comunicación como que exhibe intención deceptiva deliberada en lugar de comunicación cooperativa.

El detector opera bajo el principio forense de que el engaño deliberado viola sistemáticamente al menos una máxima cooperativa. Un analista que proporciona muy poca información (Cantidad), afirma reclamaciones sin respaldo (Calidad), introduce detalles irrelevantes (Relación) o se comunica en términos deliberadamente oscuros (Modo) es estadísticamente distinguible de un comunicador cooperativo. Todos los umbrales de detección son enteros exactos; todos los recuentos de violaciones son enteros exactos. No hay redondeos probabilísticos.

### Conceptos clave

| Concepto | Definición | Rol técnico |
|---|---|---|
| **Máxima de Grice** | Una de cuatro normas de comunicación cooperativa propuestas por H. P. Grice: Cantidad, Calidad, Relación, Modo. | Unidad de análisis; cada máxima es monitoreada por una regla de detección dedicada. |
| **Delta de Violación** | El incremento entero exacto añadido al recuento de una máxima cuando se detecta una violación. | Registrado contra un umbral entero fijo para activar un indicador de engaño. |
| **Umbral Fijo** | Valor entero exacto que especifica el número de violaciones requeridas para clasificar un acto comunicativo como deceptivo. | Previene falsos positivos de desviaciones aisladas no intencionales. |
| **Recuento Acumulado** | Total entero exacto en ejecución de violaciones en las cuatro máximas. | La entrada principal a la puerta de admisión/rechazo. |
| **Indicador de Engaño** | Salida binaria (verdadero/falso) activada cuando el recuento acumulado supera el umbral. | La señal terminal emitida a la canalización forense de aguas abajo. |
| **Aritmética Entera Determinista** | Todos los conteos y comparaciones de umbral usan enteros exactos. | Garantiza reproducibilidad: el mismo texto de entrada siempre produce los mismos recuentos de violaciones. |

### Glosario
1. **Máxima Cooperativa** — Una de las cuatro normas de Grice que rigen la comunicación veraz, relevante, informativa y clara.
2. **Recuento Acumulado de Violaciones** — Total entero exacto en ejecución de violaciones de máximas detectadas en todas las categorías.
3. **Indicador de Engaño** — Indicador binario activado cuando los recuentos de violaciones superan el umbral entero, señalando probable engaño intencional.
4. **Aritmética Entera Determinista** — Cómputo usando recuentos enteros exactos y umbrales fijos; sin puntuación probabilística.
5. **Umbral Fijo** — Entero exacto que especifica el recuento mínimo de violaciones requerido para clasificar una comunicación como deceptiva.
6. **Máxima de Modo de Grice** — La norma que requiere comunicación ordenada, no ambigua y concisa.
7. **Máxima de Calidad de Grice** — La norma que requiere veracidad: afirmar solo lo que se cree verdadero y se tiene evidencia de ello.
8. **Máxima de Cantidad de Grice** — La norma que requiere ser informativo: proporcionar tanta información como sea necesaria, pero no más.
9. **Máxima de Relación de Grice** — La norma que requiere relevancia: las contribuciones deben ser pertinentes al intercambio actual.
10. **Delta de Violación** — El incremento entero exacto añadido al recuento de una máxima al detectar una violación.

> **【Nota Científica】**
> La terminología de Peirce/Eco/Grice no es misticismo. Las máximas cooperativas de Grice son normas de comportamiento comunicativo derivadas empíricamente. Su violación sistemática es una señal medible y reproducible: estudios controlados muestran que la comunicación deceptiva viola estadísticamente al menos una máxima con más frecuencia que la comunicación cooperativa. VIGÍA operacionaliza esto como un sistema de conteo entero exacto, haciendo el resultado de detección completamente auditable y reproducible.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## РУССКИЙ

### Что это за модуль?
Данный модуль реализует **Детектор нарушений максим Грайса** для криминалистической платформы VIGÍA. Он анализирует артефакты текстовой коммуникации — заявления, журналы, транскрипты чатов и нарративные отчёты — и подсчитывает систематические нарушения четырёх кооперативных максим Грайса: Количества, Качества, Отношения и Способа. Каждое нарушение регистрируется как точный целочисленный дельта против фиксированных порогов; вероятностная оценка не используется. Когда совокупный счётчик нарушений превышает целочисленный порог, модуль помечает коммуникационный артефакт как демонстрирующий намеренный обман, а не кооперативную коммуникацию.

Детектор работает на криминалистическом принципе, что намеренный обман систематически нарушает по меньшей мере одну кооперативную максиму. Аналитик, предоставляющий слишком мало информации (Количество), заявляющий неподкреплённые утверждения (Качество), вводящий нерелевантные детали (Отношение) или общающийся намеренно туманно (Способ), статистически отличим от кооперативного коммуникатора. Все пороги обнаружения — точные целые числа; все счётчики нарушений — точные целые числа.

### Ключевые концепции

| Концепция | Определение | Техническая роль |
|---|---|---|
| **Максима Грайса** | Одна из четырёх норм кооперативной коммуникации Грайса: Количество, Качество, Отношение, Способ. | Единица анализа; каждая максима контролируется специализированным правилом обнаружения. |
| **Дельта нарушения** | Точный целочисленный прирост, добавляемый к счётчику максимы при обнаружении нарушения. | Регистрируется против фиксированного целочисленного порога для активации флага обмана. |
| **Фиксированный порог** | Точное целое число, задающее количество нарушений, необходимое для классификации коммуникативного акта как обманного. | Предотвращает ложноположительные результаты от изолированных непреднамеренных отклонений. |
| **Совокупный счётчик** | Текущий точный целочисленный итог нарушений по всем четырём максимам. | Основной вход для шлюза допуска/отклонения. |
| **Флаг обмана** | Двоичный (истина/ложь) вывод, активируемый, когда совокупный счётчик превышает порог. | Терминальный сигнал, эмитируемый в нижестоящий криминалистический конвейер. |
| **Детерминированная целочисленная арифметика** | Все подсчёты и сравнения порогов используют точные целые числа. | Гарантирует воспроизводимость: идентичный входной текст всегда даёт одинаковые счётчики нарушений. |

### Глоссарий
1. **Кооперативная максима** — Одна из четырёх норм Грайса, регулирующих правдивую, релевантную, информативную и ясную коммуникацию.
2. **Совокупный счётчик нарушений** — Текущий точный целочисленный итог обнаруженных нарушений максим по всем категориям.
3. **Флаг обмана** — Бинарный индикатор, активируемый когда счётчики нарушений превышают целочисленный порог, сигнализируя о вероятном намеренном обмане.
4. **Детерминированная целочисленная арифметика** — Вычисления с использованием точных целочисленных счётчиков и фиксированных порогов; без вероятностного оценивания.
5. **Фиксированный порог** — Точное целое число, задающее минимальный счётчик нарушений для классификации коммуникации как обманной.
6. **Максима способа Грайса** — Норма, требующая упорядоченной, однозначной и лаконичной коммуникации.
7. **Максима качества Грайса** — Норма, требующая правдивости: утверждать только то, во что верите и что можете подтвердить.
8. **Максима количества Грайса** — Норма, требующая информативности: давать столько информации, сколько необходимо, но не больше.
9. **Максима отношения Грайса** — Норма, требующая релевантности: вклад должен быть уместен в текущем обмене.
10. **Дельта нарушения** — Точный целочисленный прирост, добавляемый к счётчику максимы при обнаружении нарушения.

> **【Научное примечание】**
> Терминология Пирса, Эко и Грайса — не мистика. Кооперативные максимы Грайса — эмпирически выведенные нормы коммуникативного поведения. Их систематическое нарушение является измеримым, воспроизводимым сигналом: контролируемые исследования показывают, что обманчивая коммуникация статистически нарушает по меньшей мере одну максиму чаще, чем кооперативная. VIGÍA операционализирует это как систему точного целочисленного подсчёта, делая результат обнаружения полностью аудируемым и воспроизводимым.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## 中文

### 这是什么模块？
本模块为 VIGÍA 取证框架实现**格赖斯准则违反检测器**。它分析文本通信工件——陈述、日志、聊天记录和叙事报告——并统计对格赖斯四项合作准则（数量、质量、关联、方式）的系统性违反。每次违反均作为精确整数变化量记录在固定阈值上；不使用概率评分。当累积违反计数超过整数阈值时，模块将该通信工件标记为表现出蓄意欺骗意图，而非合作性交流。

检测器基于取证原则运作：蓄意欺骗系统性地违反至少一项合作准则。提供信息过少（数量）、断言无证据支持的主张（质量）、引入无关细节（关联）或以故意晦涩的方式交流（方式）的分析员，在统计上可与合作性交流者区分。所有检测阈值均为精确整数；所有违反计数均为精确整数。不存在概率舍入。

### 关键概念

| 概念 | 定义 | 技术作用 |
|---|---|---|
| **格赖斯准则** | H·P·格赖斯提出的四项合作交流规范之一：数量、质量、关联、方式。 | 分析单元；每项准则由专用检测规则监控。 |
| **违反变化量** | 检测到违反时添加到准则运行计数的精确整数增量。 | 记录在固定整数阈值上以触发欺骗标志。 |
| **固定阈值** | 指定将交际行为分类为欺骗性所需违反次数的精确整数值。 | 防止来自孤立、无意偏差的假阳性。 |
| **累积计数** | 四项准则中违反的当前精确整数总计。 | 准入/拒绝门的主要输入。 |
| **欺骗标志** | 累积计数超过阈值时设置的二元（真/假）输出。 | 发送至下游取证流水线的终端信号。 |
| **确定性整数运算** | 所有计数和阈值比较使用精确整数。 | 保证可复现性：相同输入文本始终产生相同违反计数。 |

### 词汇表
1. **合作准则** — 格赖斯管理真实、相关、信息丰富和清晰交流的四项规范之一。
2. **累积违反计数** — 所有类别中检测到的准则违反的当前精确整数总计。
3. **欺骗标志** — 当违反计数超过整数阈值时设置的二元指示器，表明可能存在蓄意欺骗。
4. **确定性整数运算** — 使用精确整数计数和固定阈值进行计算；无概率评分。
5. **固定阈值** — 指定将通信分类为欺骗性所需最少违反计数的精确整数。
6. **格赖斯方式准则** — 要求交流有序、明确和简洁的规范。
7. **格赖斯质量准则** — 要求真实性的规范：只断言你相信为真且有证据的内容。
8. **格赖斯数量准则** — 要求信息性的规范：提供所需的信息量，但不要过多。
9. **格赖斯关联准则** — 要求相关性的规范：贡献必须与当前交流相关。
10. **违反变化量** — 检测到违反时添加到准则计数的精确整数增量。

> **【科学说明】**
> 皮尔斯、艾柯和格赖斯的术语并非神秘主义。格赖斯的合作准则是经验性推导出的交际行为规范。它们的系统性违反是一种可测量、可复现的信号：受控研究表明，欺骗性交流在统计上比合作性交流更频繁地违反至少一项准则。VIGÍA 将其操作化为精确整数计数系统，使检测结果完全可审计且可复现。

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
