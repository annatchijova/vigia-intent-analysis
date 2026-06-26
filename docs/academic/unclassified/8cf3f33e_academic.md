<!--
VIGIA Academic Documentation
Module: 8cf3f33e
Batch ID: vigia-doc-0119-8cf3f33e
Generated: 2026-05-20T14:56:47.870276+00:00
-->

---

## ENGLISH

### What Is This Module?
This module is a **deterministic comparator** for two separate executions (*runs*) of the VIGÍA forensic pipeline against the **same dataset**. It answers one question: *What exactly changed between Run A and Run B?* To do this, it parses the structured output of each run, computes exact differences using **integer arithmetic and irreducible rational fractions**, labels each change as an **IMPROVEMENT**, **REGRESSION**, or **VERDICT_SHIFT**, and flags candidate explanatory components via **heuristic (non-causal) driver detection**. It does **not** compute confusion-matrix statistics such as TP/FP/TN/FN; those are handled by `evaluate_detector.py`.

---

### Key Concepts

| Term | Meaning | Role in the Module |
|------|---------|-------------------|
| **Deterministic Comparator** | A system that yields identical outputs from identical inputs with no stochastic steps | Guarantees bitwise reproducibility of conclusions |
| **Irreducible Rational Fraction** | A ratio of two integers reduced to lowest terms (e.g., `3/7`, never `0.428…`) | Produces court-admissible exact deltas under the Daubert standard |
| **Heuristic Driver Detection** | Non-causal identification of components that *likely* accompany a change | Surfaces suspects, not proven causes |
| **Verdict Shift** | Any change in the final classification or outcome label between two runs | Critical label for downstream review |
| **Deterministic Forensic Hash** | An integer fingerprint of a digital artifact, free of floating-point representation | Ensures integrity checks remain inside integer space |
| **Integer Decision Logic** | All branching, thresholds, and labels rely on integer or fraction arithmetic | Eliminates rounding-induced non-determinism |
| **Logical Fracture** | A non-causal break in expected logical continuity between two runs | Detected by the heuristic engine to flag anomalous transitions |

---

### Classes

| Class | Purpose |
|-------|---------|
| `PipelineResult` | Immutable container for one pipeline run's outputs; parses the run manifest into structured, typed fields |
| `IntentDelta` | Encodes the exact difference between two matched intent objects across runs, expressed as integer deltas |
| `ComparisonResult` | Aggregates all deltas, assigns outcome labels (`IMPROVEMENT` / `REGRESSION` / `VERDICT_SHIFT`), and stores heuristic driver candidates |

---

### Functions

| Function | Purpose |
|----------|---------|
| `hash_forensic()` | Computes a deterministic integer hash of a forensic artifact; used for integrity verification |
| `load_run()` | Reads a run directory and assembles a `PipelineResult` using only structured text and integer parsing |
| `compare_artifact()` | Performs pairwise comparison of two artifacts, returning an irreducible rational delta where applicable |
| `print_table()` | Renders a comparison matrix to the terminal for human inspection |
| `print_diff()` | Emits a line-oriented diff of textual forensic outputs |
| `compute_meta_metrics()` | Calculates summary statistics over the comparison using integer rational arithmetic |
| `export_csv()` | Writes comparison results to a comma-separated file for external audit |
| `main()` | Entry point; orchestrates loading, comparison, labeling, and output generation |

---

### Constants & Configuration

| Constant | Meaning |
|----------|---------|
| `REQUIRED_KEYS` | Mandatory manifest fields that must be present for a run to qualify for comparison |
| `COMPONENT_KEYS` | Subsystem identifiers whose values are exposed to heuristic driver detection |
| `MI_KEYS` | Mutual-information / message-intent keys tracked for semantic comparison |
| `LEVEL_ORDER` | Hierarchical precedence used when resolving conflicting labels during aggregation |

---

### Glossary

- **Deterministic** — Producing the same result every time from the same initial conditions; devoid of randomness.
- **Irreducible Fraction** — A rational number *a/b* where the numerator and denominator share no common divisor other than 1.
- **Heuristic** — A practical rule or pattern for discovery, not proof of causation.
- **Daubert Standard** — Legal criterion for admissible scientific evidence requiring known reliability and error rates.
- **Forensic Artifact** — Any digital object offered as evidence (file, log, memory dump).
- **Regression** — A change that degrades performance or accuracy relative to a baseline.
- **Non-causal** — Describing correlation or co-occurrence without established cause-and-effect.
- **Verdict Shift** — Any alteration in the final outcome label between two runs.
- **Logical Fracture** — A non-causal discontinuity in the expected logical chain between two pipeline executions.

---

> 【Scientific Note】
> This module borrows terminology from semiotics (Peirce), interpretive theory (Umberto Eco), and pragmatics (Grice). These names are **not mysticism**. Treat them as **sensor ontologies**: Peirce's categories classify *how* a detection signal relates to an object (icon, index, symbol); Eco's framework specifies *how* meaning is negotiated between the detection system and its context; Grice's maxims define *expected cooperativity* in message exchange between pipeline stages. Just as a physicist does not treat a voltmeter as magic, a forensic scientist should not treat semiotic vocabulary as occult—it is a structured language for describing information flow inside deterministic measurement systems.

---

## ESPAÑOL

### ¿Qué es este módulo?
Este módulo es un **comparador determinista** entre dos ejecuciones (*runs*) del pipeline forense VIGÍA sobre el **mismo conjunto de datos**. Responde a una pregunta: *¿Qué cambió exactamente entre la Ejecución A y la Ejecución B?* Para ello, analiza la salida estructurada de cada ejecución, calcula diferencias exactas mediante **aritmética entera y fracciones racionales irreducibles**, etiqueta cada cambio como **MEJORA**, **REGRESIÓN** o **CAMBIO_DE_VEREDICTO**, y señala componentes candidatos explicativos mediante la **detección heurística de drivers (no causal)**. **No** calcula estadísticas de matriz de confusión (TP/FP/TN/FN); eso corresponde a `evaluate_detector.py`.

---

### Conceptos clave

| Término | Significado | Rol en el módulo |
|---------|-------------|------------------|
| **Comparador determinista** | Sistema que produce la misma salida ante las mismas entradas, sin pasos estocásticos | Garantiza reproducibilidad bit a bit |
| **Fracción racional irreducible** | Cociente de dos enteros reducido a mínima expresión (p. ej., `3/7`, nunca `0,428…`) | Asegura deltas exactos, admisibles bajo el estándar Daubert |
| **Detección heurística de drivers** | Identificación no causal de componentes que *probablemente* acompañan un cambio | Señala sospechosos, no causas probadas |
| **Cambio de veredicto** | Cualquier variación en la clasificación o decisión final entre dos ejecuciones | Etiqueta crítica para revisión posterior |
| **Hash forense determinista** | Huella dactilar entera de un artefacto digital, libre de representación en punto flotante | Garantiza que la integridad se verifica en espacio entero |
| **Lógica de decisión entera** | Todas las ram
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## РУССКИЙ

### Что это за модуль?
Данный модуль — **детерминированный компаратор** двух отдельных запусков (*runs*) форензического конвейера VIGÍA на **одном и том же наборе данных**. Он отвечает на один вопрос: *что именно изменилось между запуском A и запуском B?* Для этого модуль разбирает структурированный вывод каждого запуска, вычисляет точные различия с помощью **целочисленной арифметики и несократимых рациональных дробей**, маркирует каждое изменение как **УЛУЧШЕНИЕ**, **РЕГРЕССИЮ** или **СДВИГ_ВЕРДИКТА**, и отмечает кандидатов-объяснителей через **эвристическое (непричинное) обнаружение драйверов**.

Модуль **не** вычисляет статистику матрицы путаницы (TP/FP/TN/FN) — это функция `evaluate_detector.py`. Все пороги, ветвления и метки опираются исключительно на целочисленную арифметику или дробную логику, что исключает недетерминизм, вызванный округлением. Детерминированный целочисленный хэш форензического артефакта гарантирует, что проверки целостности остаются в целочисленном пространстве.

Понятие «несократимая рациональная дробь» ключевое: вместо `0.428…` модуль всегда выдаёт `3/7` — точный результат, допустимый в суде согласно стандарту Добера и воспроизводимый без аппаратно-зависимых режимов округления.

### Ключевые концепции
| Термин | Значение | Роль в модуле |
|---|---|---|
| Детерминированный компаратор | Система, дающая идентичные выходные данные из идентичных входных данных без стохастических шагов | Гарантирует побитовую воспроизводимость заключений |
| Несократимая рациональная дробь | Отношение двух целых чисел, приведённое к наименьшим членам (например, `3/7`, никогда `0,428…`) | Обеспечивает точные делты, допустимые в суде по стандарту Добера |
| Эвристическое обнаружение драйверов | Непричинная идентификация компонентов, вероятно сопровождающих изменение | Выявляет подозреваемых, а не доказанные причины |
| Сдвиг вердикта | Любое изменение финальной метки классификации между двумя запусками | Критическая метка для последующей проверки |
| Детерминированный форензический хэш | Целочисленный отпечаток цифрового артефакта без представления с плавающей запятой | Гарантирует, что проверки целостности остаются в целочисленном пространстве |
| Целочисленная логика решений | Все ветвления, пороги и метки опираются на целочисленную или дробную арифметику | Исключает недетерминизм, вызванный округлением |
| Логический разрыв | Непричинный разрыв в ожидаемой логической цепи между двумя запусками конвейера | Обнаруживается эвристическим движком для маркировки аномальных переходов |

> **【Научное примечание】**
> Терминология Пирса, Эко и Грайса — это не мистика, а формальная аналитическая механика. Как спектрометр преобразует фотонные взаимодействия в дискретные целочисленные отсчёты, этот модуль преобразует сигналы улик в детерминированные целочисленные оценки. Целочисленная арифметика гарантирует воспроизводимость в суде без округлений и аппроксимаций. Любое нарушение логики в цепочке артефактов фиксируется как целочисленный флаг, а не интуитивное суждение.

### Глоссарий
1. **Детерминированный** — Дающий одинаковый результат каждый раз при одинаковых начальных условиях; лишённый случайности.
2. **Несократимая дробь** — Рациональное число *a/b*, числитель и знаменатель которого не имеют общего делителя, кроме 1.
3. **Эвристика** — Практическое правило или паттерн для открытия, а не доказательство причинно-следственной связи.
4. **Стандарт Добера** — Правовой критерий допустимости научных доказательств, требующий известной надёжности и уровней ошибок.
5. **Форензический артефакт** — Любой цифровой объект, предлагаемый в качестве доказательства (файл, журнал, дамп памяти).
6. **Регрессия** — Изменение, ухудшающее производительность или точность относительно базовой линии.
7. **Непричинный** — Описывающий корреляцию или совместное появление без установленной причинно-следственной связи.
8. **Сдвиг вердикта** — Любое изменение финальной метки результата между двумя запусками.
9. **Логический разрыв** — Непричинный разрыв в ожидаемой логической цепи между двумя выполнениями конвейера.
10. **Детерминированная целочисленная арифметика** — Точные вычисления над целыми числами, исключающие ошибки представления с плавающей запятой.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## 中文

### 这是什么模块？
本模块是对同一数据集进行VIGÍA取证流程两次独立执行（*运行*）的**确定性比较器**。它回答一个问题：*运行A和运行B之间究竟发生了什么变化？* 为此，它解析每次运行的结构化输出，使用**精确整数运算和不可约有理分数**计算精确差异，将每个变化标记为**改进**、**回归**或**裁决转变**，并通过**启发式（非因果）驱动因素检测**标记候选解释组件。

本模块**不**计算混淆矩阵统计（TP/FP/TN/FN）；那是`evaluate_detector.py`的功能。所有阈值、分支和标签完全依赖整数或分数运算，排除舍入引起的不确定性。不可约有理分数是关键概念：模块总是产生`3/7`而非`0.428…`——精确结果，符合道伯特标准的法庭可采性要求，且在重复执行时无需依赖硬件舍入模式。

### 关键概念
| 术语 | 含义 | 在模块中的作用 |
|---|---|---|
| 确定性比较器 | 从相同输入产生相同输出、无随机步骤的系统 | 保证结论的逐位可重现性 |
| 不可约有理分数 | 化简到最简形式的两整数之比（如`3/7`，永不用`0.428…`） | 在道伯特标准下产生法庭可采的精确差值 |
| 启发式驱动因素检测 | 对可能伴随变化的组件进行非因果识别 | 揭示嫌疑对象，而非证明的原因 |
| 裁决转变 | 两次运行间最终分类或结果标签的任何变化 | 下游审查的关键标签 |
| 确定性取证哈希 | 不含浮点表示的数字取证工件整数指纹 | 确保完整性检查保持在整数空间内 |
| 整数决策逻辑 | 所有分支、阈值和标签依赖整数或分数运算 | 消除舍入引起的不确定性 |
| 逻辑断裂 | 两次流程执行间预期逻辑连续性的非因果中断 | 由启发式引擎检测以标记异常转换 |

> **【科学说明】**
> 皮尔斯（Peirce）、艾柯（Eco）和格赖斯（Grice）的术语并非神秘主义，而是形式化的分析机制。如同光谱仪将光子相互作用转换为离散整数计数，本模块将证据信号转换为确定性整数分数。精确整数运算确保法庭可重现性。取证工件链的逻辑断裂以整数标志事件形式被检测。

### 词汇表
1. **确定性** — 每次从相同初始条件产生相同结果；不含随机性。
2. **不可约分数** — 分子与分母除1外没有公因子的有理数*a/b*。
3. **启发式** — 用于发现的实用规则或模式，而非因果证明。
4. **道伯特标准** — 要求已知可靠性和错误率的科学证据可采性法律标准。
5. **取证工件** — 作为证据提交的任何数字对象（文件、日志、内存转储）。
6. **回归** — 相对于基准线降低性能或准确性的变化。
7. **非因果** — 描述相关或共现而无确定因果关系。
8. **裁决转变** — 两次运行间最终结果标签的任何改变。
9. **逻辑断裂** — 两次流程执行间预期逻辑链的非因果不连续性。
10. **精确整数运算** — 对整数进行精确计算，排除浮点表示误差。

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
