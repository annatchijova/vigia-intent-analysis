<!--
VIGIA Academic Documentation
Module: ae52197a
Batch ID: vigia-doc-0044-ae52197a
Generated: 2026-05-20T14:56:47.853917+00:00
-->

## ENGLISH

### What Is This Module?

The `compare_baseline.py` support module executes a deterministic forensic benchmark between the VIGÍA analytical engine and a naive averaging heuristic. Designed for controlled hackathon demonstrations, it evaluates discrete case files—either the full cohort or a single specified instance—and emits a structured output key contrasting VIGÍA's inferential logic with baseline mean-value assumptions. No stochastic sampling is employed; all findings are fully reproducible.

The module does not perform probabilistic inference. Instead, it applies a rule-based comparative procedure: VIGÍA's output is compared against a fixed mean-value reference using exact integer operations. Every comparison is bitwise deterministic — the same case file always produces the same result on any hardware.

### Key Concepts

| Concept | Definition | Technical Role |
|---|---|---|
| **Baseline Heuristic** | A naive reference method that uses mean-value assumptions without contextual analysis. | The comparison target against which VIGÍA's inferential advantage is measured. |
| **Deterministic Benchmark** | An evaluation protocol that produces identical results across repeated executions without random sampling. | The methodological contract. All comparisons use exact integer arithmetic. |
| **Case File** | A discrete forensic instance containing event data submitted for evaluation. | The input unit; each case is processed independently in strict sequence. |
| **Cohort** | The complete set of case instances processed in a single benchmark run. | The batch scope; enables comparative analysis across the full evidence population. |
| **Inferential Logic** | The reasoning process used by the VIGÍA engine to derive forensic conclusions. | The subject of evaluation; contrasted against the mean-value baseline at each step. |
| **Output Key** | A structured annotation mapping each result to its analytical source (VIGÍA or baseline). | The output format; enables downstream audit and reproducibility verification. |

> **【Scientific Note】**
> Peirce's Thirdness, Eco's encyclopedic calibration, and Grice's cooperative maxims are not mysticism — they are formal sensors that this module measures against a baseline. Just as a spectrometer's accuracy is validated by comparing its readings to a known reference standard, this benchmark validates VIGÍA's inferential engine by contrasting it against a mean-value heuristic. The baseline has no Peircean Secondness (no structural comparison against context) and no Gricean relevance filter. The measured gap between the two is the operational signature of VIGÍA's deterministic intentionality framework. All scoring uses exact integer arithmetic; deterministic integer operations ensure courtroom reproducibility.

### Glossary

1. **Baseline** — A reference heuristic using mean-value assumptions for deterministic comparison against VIGÍA outputs.
2. **Case File** — A discrete forensic instance containing event data for analysis.
3. **Cohort** — The complete set of case instances processed in a single benchmark run.
4. **Deterministic Benchmark** — An evaluation producing identical outputs from identical inputs without random sampling.
5. **Heuristic** — A simplified rule-based approximation method used as the comparison reference.
6. **Inferential Logic** — The reasoning process by which the VIGÍA engine derives forensic conclusions from evidence.
7. **Output Key** — A structured annotation linking each benchmark result to its analytical source.
8. **Reproducibility** — The property ensuring repeated executions yield bitwise-identical findings.
9. **Structured Output** — Machine-readable comparative results formatted for direct audit.
10. **VIGÍA Engine** — The core analytical module under evaluation in this benchmark.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## ESPAÑOL

### ¿Qué es este módulo?

El módulo de soporte `compare_baseline.py` ejecuta un benchmark forense determinístico entre el motor analítico VIGÍA y una heurística ingenua de promedios. Diseñado para demostraciones controladas en hackathones, evalúa archivos de caso discretos—toda la cohorte o una instancia específica—y genera una clave de salida estructurada que contrasta la lógica inferencial de VIGÍA con las suposiciones de valor medio del método base. No se emplea muestreo estocástico; todos los hallazgos son totalmente reproducibles.

El módulo no realiza inferencia probabilística. En cambio, aplica un procedimiento comparativo basado en reglas: la salida de VIGÍA se compara contra una referencia de valor medio fijo mediante operaciones enteras exactas. Cada comparación es deterministamente idéntica a nivel de bits — el mismo archivo de caso siempre produce el mismo resultado en cualquier hardware.

### Conceptos clave

| Concepto | Definición | Rol técnico |
|---|---|---|
| **Heurística de referencia** | Método de referencia ingenuo que usa supuestos de valor medio sin análisis contextual. | El objetivo de comparación contra el cual se mide la ventaja inferencial de VIGÍA. |
| **Benchmark determinístico** | Protocolo de evaluación que produce resultados idénticos en ejecuciones repetidas sin muestreo aleatorio. | El contrato metodológico. Todas las comparaciones usan aritmética entera exacta. |
| **Archivo de caso** | Instancia forense discreta con datos de eventos para evaluación. | La unidad de entrada; cada caso se procesa independientemente en secuencia estricta. |
| **Cohorte** | Conjunto completo de instancias de caso procesadas en una sola ejecución del benchmark. | El ámbito del lote; permite análisis comparativo en toda la población de evidencias. |
| **Lógica inferencial** | El proceso de razonamiento usado por el motor VIGÍA para derivar conclusiones forenses. | El sujeto de evaluación; contrastado con la referencia de valor medio en cada paso. |
| **Clave de salida** | Anotación estructurada que mapea cada resultado a su fuente analítica (VIGÍA o referencia). | El formato de salida; permite auditoría y verificación de reproducibilidad. |

> **【Nota Científica】**
> La Terceridad de Peirce, la calibración enciclopédica de Eco y las máximas cooperativas de Grice no son misticismo — son sensores formales que este módulo mide contra una referencia. Igual que la precisión de un espectrómetro se valida comparando sus lecturas con un estándar de referencia conocido, este benchmark valida el motor inferencial de VIGÍA contrastándolo con una heurística de valor medio. La referencia no tiene Segundidad peirceana ni filtro de relevancia griceano. La brecha medida entre ambos es la firma operacional del marco determinista de intencionalidad de VIGÍA. Todo el puntuaje usa aritmética entera exacta; las operaciones enteras deterministas garantizan reproducibilidad en sala de tribunal.

### Glosario

1. **Referencia (Baseline)** — Heurística de referencia que usa supuestos de valor medio para comparación determinista con las salidas de VIGÍA.
2. **Archivo de caso** — Instancia forense discreta que contiene datos de eventos para análisis.
3. **Cohorte** — Conjunto completo de instancias de caso procesadas en una sola ejecución del benchmark.
4. **Benchmark determinístico** — Evaluación que produce salidas idénticas de entradas idénticas sin muestreo aleatorio.
5. **Heurística** — Método de aproximación simplificado basado en reglas, usado como referencia de comparación.
6. **Lógica inferencial** — El proceso de razonamiento mediante el cual el motor VIGÍA deriva conclusiones forenses de la evidencia.
7. **Clave de salida** — Anotación estructurada que vincula cada resultado del benchmark a su fuente analítica.
8. **Reproducibilidad** — Propiedad que garantiza que ejecuciones repetidas produzcan hallazgos idénticos a nivel de bits.
9. **Salida estructurada** — Resultados comparativos legibles por máquina formateados para auditoría directa.
10. **Motor VIGÍA** — El módulo analítico central bajo evaluación en este benchmark.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## РУССКИЙ

### Что это за модуль?

Вспомогательный модуль `compare_baseline.py` выполняет детерминированное судебно-криминалистическое сравнение аналитического движка VIGÍA с наивной эвристикой усреднения. Предназначен для контролируемых демонстраций на хакатонах; обрабатывает дискретные кейс-файлы — всю когорту или отдельный экземпляр — и формирует структурированный ключ вывода, сопоставляющий инференциальную логику VIGÍA с предположениями базового метода о среднем значении. Стохастическая выборка не используется; все результаты полностью воспроизводимы.

Модуль не выполняет вероятностный инференс. Вместо этого он применяет основанную на правилах процедуру сравнения: вывод VIGÍA сопоставляется с фиксированной эталонной средней величиной с использованием точных целочисленных операций. Каждое сравнение побитово детерминировано — одинаковый кейс-файл всегда производит одинаковый результат на любом аппаратном обеспечении.

### Ключевые концепции

| Концепция | Определение | Техническая роль |
|---|---|---|
| **Базовая эвристика** | Наивный эталонный метод, использующий предположения о среднем значении без контекстного анализа. | Объект сравнения, по отношению к которому измеряется инференциальное преимущество VIGÍA. |
| **Детерминированный бенчмарк** | Протокол оценки, производящий идентичные результаты при повторных выполнениях без случайной выборки. | Методологический контракт. Все сравнения используют точную целочисленную арифметику. |
| **Кейс-файл** | Дискретный криминалистический экземпляр, содержащий данные о событиях для оценки. | Входная единица; каждый кейс обрабатывается независимо в строгой последовательности. |
| **Когорта** | Полный набор экземпляров кейсов, обрабатываемых в одном прогоне бенчмарка. | Объём пакета; обеспечивает сравнительный анализ по всей совокупности доказательств. |
| **Инференциальная логика** | Процесс рассуждения, используемый движком VIGÍA для получения криминалистических выводов. | Предмет оценки; сопоставляется с базовой эталонной средней на каждом шаге. |
| **Ключ вывода** | Структурированная аннотация, сопоставляющая каждый результат с его аналитическим источником. | Формат вывода; обеспечивает аудит и верификацию воспроизводимости. |

> **【Научное примечание】**
> Третичность Пирса, энциклопедическая калибровка Эко и кооперативные максимы Грайса — не мистицизм, а формальные сенсоры, которые этот модуль измеряет относительно базовой линии. Так же, как точность спектрометра подтверждается сравнением его показаний с известным эталоном, данный бенчмарк подтверждает инференциальный движок VIGÍA, сопоставляя его с эвристикой среднего значения. Базовая линия лишена пирсовской Вторичности (нет структурного сравнения с контекстом) и грайсовского фильтра релевантности. Измеренный разрыв между ними является операциональной сигнатурой детерминированной системы интенциональности VIGÍA. Всё оценивание использует точную целочисленную арифметику; детерминированные целочисленные операции обеспечивают воспроизводимость в судебном разбирательстве.

### Глоссарий

1. **Базовая линия (Baseline)** — Эталонная эвристика, использующая предположения о среднем значении для детерминированного сравнения с выводами VIGÍA.
2. **Кейс-файл** — Дискретный криминалистический экземпляр, содержащий данные о событиях для анализа.
3. **Когорта** — Полный набор экземпляров кейсов, обрабатываемых в одном прогоне бенчмарка.
4. **Детерминированный бенчмарк** — Оценка, производящая идентичные результаты из идентичных входных данных без случайной выборки.
5. **Эвристика** — Упрощённый метод аппроксимации на основе правил, используемый как эталон сравнения.
6. **Инференциальная логика** — Процесс рассуждения, посредством которого движок VIGÍA извлекает криминалистические выводы из доказательств.
7. **Ключ вывода** — Структурированная аннотация, связывающая каждый результат бенчмарка с его аналитическим источником.
8. **Воспроизводимость** — Свойство, обеспечивающее побитово идентичные результаты при повторных выполнениях.
9. **Структурированный вывод** — Сравнительные результаты в машиночитаемом формате для прямого аудита.
10. **Движок VIGÍA** — Основной аналитический модуль, оцениваемый в данном бенчмарке.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## 中文

### 这是什么模块？

支持模块 `compare_baseline.py` 在 VIGÍA 分析引擎与朴素均值启发式之间执行确定性取证基准测试。专为受控的黑客马拉松演示设计，该模块处理离散案例文件——完整队列或单一指定实例——并生成结构化输出键，将 VIGÍA 的推理逻辑与基线均值假设进行对比。不采用随机抽样；所有发现完全可复现。

该模块不执行概率推理。相反，它应用基于规则的比较程序：使用精确整数运算将 VIGÍA 的输出与固定均值参考进行比较。每次比较在位级上都是确定性的——相同的案例文件在任何硬件上始终产生相同的结果。

### 关键概念

| 概念 | 定义 | 技术作用 |
|---|---|---|
| **基线启发式** | 使用均值假设而不进行上下文分析的朴素参考方法。 | 用于衡量 VIGÍA 推理优势的比较目标。 |
| **确定性基准** | 在重复执行中产生相同结果且不使用随机抽样的评估协议。 | 方法论契约。所有比较均使用精确整数运算。 |
| **案例文件** | 包含待评估事件数据的离散取证实例。 | 输入单元；每个案例按严格顺序独立处理。 |
| **队列（Cohort）** | 单次基准运行中处理的完整案例实例集合。 | 批处理范围；支持对整个证据集群的比较分析。 |
| **推理逻辑** | VIGÍA 引擎用于推导取证结论的推理过程。 | 评估主体；在每个步骤与均值基线形成对比。 |
| **输出键** | 将每个结果映射到其分析来源（VIGÍA 或基线）的结构化注释。 | 输出格式；支持后续审计和可重现性验证。 |

> **【科学说明】**
> 皮尔斯（Peirce）的三性、艾柯（Eco）的百科全书校准和格赖斯（Grice）的合作准则并非神秘主义——它们是本模块针对基线进行测量的形式传感器。正如光谱仪的精度通过将其读数与已知参考标准进行比较来验证，本基准通过将 VIGÍA 推理引擎与均值启发式进行对比来验证它。基线没有皮尔斯式的二性（没有与上下文的结构比较），也没有格赖斯式的相关性过滤器。两者之间的测量差距是 VIGÍA 确定性意图框架的操作特征签名。所有评分使用精确整数运算；确定性整数操作确保法庭可重现性。

### 词汇表

1. **基线（Baseline）** — 使用均值假设与 VIGÍA 输出进行确定性比较的参考启发式方法。
2. **案例文件** — 包含事件数据用于分析的离散取证实例。
3. **队列（Cohort）** — 单次基准运行中处理的完整案例实例集合。
4. **确定性基准** — 从相同输入产生相同输出且不使用随机抽样的评估。
5. **启发式（Heuristic）** — 用作比较参考的简化规则近似方法。
6. **推理逻辑** — VIGÍA 引擎从证据中推导取证结论的推理过程。
7. **输出键** — 将每个基准结果与其分析来源关联的结构化注释。
8. **可重现性** — 确保重复执行产生逐位相同发现的属性。
9. **结构化输出** — 格式化为直接审计用途的机器可读比较结果。
10. **VIGÍA 引擎** — 本基准中被评估的核心分析模块。

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---
