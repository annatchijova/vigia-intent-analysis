<!--
VIGIA Academic Documentation
Module: 1566c038
Batch ID: vigia-doc-0071-1566c038
Generated: 2026-05-20T14:56:47.859800+00:00
-->

## ENGLISH

### What Is This Module?
This module is the strategic scheduler of the VIGIA digital forensic suite. Think of a busy laboratory that must run a battery of expensive tests on a single piece of evidence. Some tests—such as Error Level Analysis (ELA) or CLIP neural inference—consume hours of CPU time and electrical energy. This module decides **which test to run first** and **when to stop early** because the accumulated evidence has already crossed the confidence threshold.

It treats every forensic instrument as an **investigative sensor** with two known properties: (1) its resource cost (normalized CPU time or energy units), and (2) its expected informational value (historical average contribution to the Likelihood Ratio). By ranking instruments according to the exact rational ratio of value-to-cost, the module guarantees an efficient, auditable, and reproducible examination plan.

### Key Concepts
| Concept | Plain-Language Definition | System Role |
|---------|---------------------------|-------------|
| **ToolSpec** | A formal declaration of a forensic instrument (name, cost, expected value). | Serves as the immutable blueprint for every tool admitted into the plan. |
| **Priority (P)** | The deterministic ratio of expected log LR contribution to relative cost, expressed as an exact rational number. | Determines the execution order; higher-value-per-cost tools run first. |
| **log LR** | The base-10 logarithm of the Likelihood Ratio; a measure of evidential weight. | Quantifies how strongly a tool discriminates between the prosecution and defense hypotheses. |
| **AbortDecision** | A deterministic rule that halts further signal processing. | Prevents redundant expenditure of resources once the posterior threshold is breached. |
| **ResourceOptimizer** | The central engine that sorts tools, monitors cumulative evidence, and issues abort commands. | Maintains the execution plan and enforces cost-benefit discipline. |
| **ExecutionLog** | An immutable, append-only record of every action taken. | Provides the audit trail required for courtroom reconstruction; stored inside the **ForensicBundle**. |
| **Exponential Moving Average (EMA)** | A recurrence relation that updates a tool's expected value using recent observations weighted by an exact integer fraction. | Adapts historical estimates without drift, preserving determinism. |
| **ForensicBundle** | A sealed container of forensic artifacts. | Bundles the ExecutionLog with evidence for chain-of-custody verification. |

> **【Scientific Note】**
> Terms such as **abduction** (Peirce), **sign system** (Eco), and **cooperative principle** (Grice) are sometimes mistaken for metaphysical speculation. In this forensic context, they function exactly like physical sensors. Peirce's abduction is a hypothesis-generation detector; Eco's semiotics is a pattern-recognition filter; Grice's maxims are noise-reduction protocols. Just as a spectrometer detects wavelengths without "believing" in light, these epistemological frameworks detect logical structure without invoking mysticism. The module employs them as formal calibration tools for the inference engine, identifying logical fractures and ensuring that evidentiary signals are interpreted through rigorous, material operators rather than intuitive guesswork.

### Glossary
1. **Likelihood Ratio (LR)** — The ratio of two conditional probabilities: probability of the observed data under the prosecution hypothesis divided by its probability under the defense hypothesis.
2. **Posterior Accumulation** — The cumulative evidential weight obtained by summing log LR contributions across multiple tools.
3. **Confidence Threshold** — A predetermined, case-specific limit on the accumulated posterior; crossing it deterministically aborts further processing.
4. **Relative Cost** — Normalized resource expenditure (time, energy, or CPU cycles) expressed as an exact integer or rational scalar.
5. **Deterministic Integer Arithmetic** — Mathematical operations performed on exact integers and rational fractions, ensuring bitwise-reproducible results on every hardware platform.
6. **Chain of Custody** — The legal principle requiring documented, unbroken control over evidence; the ExecutionLog supports this directly.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## ESPAÑOL

### ¿Qué es este módulo?
Este módulo es el planificador estratégico de la suite forense digital VIGIA. Imaginen un laboratorio ocupado que debe ejecutar una batería de pruebas costosas sobre una única pieza de evidencia. Algunas pruebas—como el Análisis de Nivel de Error (ELA) o la inferencia neuronal CLIP—consumen horas de tiempo de CPU y energía eléctrica. Este módulo decide **qué prueba ejecutar primero** y **cuándo detenerse anticipadamente** porque la evidencia acumulada ya ha cruzado el umbral de confianza.

Trata cada instrumento forense como un **sensor investigativo** con dos propiedades conocidas: (1) su costo en recursos (tiempo de CPU o unidades de energía normalizadas) y (2) su valor informativo esperado (contribución histórica promedio al Cociente de Verosimilitud). Al ordenar los instrumentos según la razón racional exacta valor/costo, el módulo garantiza un plan de examen eficiente, auditable y reproducible.

### Conceptos Clave
| Concepto | Definición en lenguaje sencillo | Rol en el sistema |
|----------|--------------------------------|-------------------|
| **ToolSpec** | Declaración formal de un instrumento forense (nombre, costo, valor esperado). | Sirve como plano inmutable para cada herramienta admitida en el plan. |
| **Prioridad (P)** | Razón determinista entre la contribución esperada de log LR y el costo relativo, expresada como número racional exacto. | Determina el orden de ejecución; las herramientas de mayor valor por costo se ejecutan primero. |
| **log LR** | Logaritmo base 10 del Cociente de Verosimilitud; medida del peso probatorio. | Cuantifica cuán fuertemente una herramienta discrimina entre las hipótesis de fiscalía y defensa. |
| **AbortDecision** | Regla determinista que detiene el procesamiento adicional de señales. | Previene el gasto redundante de recursos una vez superado el umbral posterior. |
| **ResourceOptimizer** | Motor central que ordena herramientas, monitorea la evidencia acumulada y emite órdenes de aborto. | Mantiene el plan de ejecución y aplica disciplina de costo-beneficio. |
| **ExecutionLog** | Registro inmutable de solo-adición de cada acción realizada. | Provee la pista de auditoría necesaria para la reconstrucción judicial; almacenado dentro del **ForensicBundle**. |
| **Media Móvil Exponencial (EMA)** | Relación de recurrencia que actualiza el valor esperado de una herramienta usando observaciones recientes ponderadas por una fracción entera exacta. | Adapta estimaciones históricas preservando el determinismo. |
| **ForensicBundle** | Contenedor sellado de artefactos forenses. | Agrupa el ExecutionLog con la evidencia para la verificación de la cadena de custodia. |

> **【Nota Científica】**
> Términos como **abducción** (Peirce), **sistema de signos** (Eco) y **principio cooperativo** (Grice) a veces se confunden con especulación metafísica. En este contexto forense funcionan exactamente como sensores físicos. La abducción de Peirce es un detector de generación de hipótesis; la semiótica de Eco es un filtro de reconocimiento de patrones; los máximas de Grice son protocolos de reducción de ruido. Así como un espectrómetro detecta longitudes de onda sin "creer" en la luz, estos marcos epistemológicos detectan estructura lógica sin invocar misticismo.

### Glosario
1. **Cociente de Verosimilitud (LR)** — Razón entre la probabilidad de los datos bajo la hipótesis de la fiscalía y su probabilidad bajo la hipótesis de la defensa.
2. **Acumulación Posterior** — El peso probatorio acumulado obtenido sumando contribuciones de log LR de múltiples herramientas.
3. **Umbral de Confianza** — Límite predeterminado y específico del caso sobre la posterior acumulada; al cruzarlo el procesamiento se aborta de manera determinista.
4. **Costo Relativo** — Gasto de recursos normalizado expresado como escalar entero o racional exacto.
5. **Aritmética Entera Determinista** — Operaciones matemáticas sobre enteros exactos y fracciones racionales, garantizando resultados reproducibles en toda plataforma de hardware.
6. **Cadena de Custodia** — Principio legal que exige control documentado e ininterrumpido sobre la evidencia; el ExecutionLog lo apoya directamente.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## РУССКИЙ

### Что это за модуль?
Этот модуль является стратегическим планировщиком цифрового судебного комплекса VIGIA. Представьте загруженную лабораторию, где необходимо провести серию дорогостоящих тестов над единственным объектом доказательства. Некоторые тесты—такие как анализ уровня ошибки (ELA) или нейронный вывод CLIP—требуют часов процессорного времени и электроэнергии. Этот модуль решает, **какой тест запустить первым**, и **когда досрочно остановиться**, потому что накопленные доказательства уже пересекли порог достоверности.

Каждый судебный инструмент рассматривается как **исследовательский датчик** с двумя известными свойствами: (1) стоимость ресурсов (нормализованное процессорное время или энергетические единицы) и (2) ожидаемая информационная ценность (средний исторический вклад в отношение правдоподобия). Упорядочивая инструменты по точному рациональному отношению ценность/стоимость, модуль гарантирует эффективный, поддающийся аудиту и воспроизводимый план экспертизы.

### Ключевые понятия
| Понятие | Определение простым языком | Роль в системе |
|---------|----------------------------|----------------|
| **ToolSpec** | Формальное объявление судебного инструмента (имя, стоимость, ожидаемая ценность). | Служит неизменным чертежом для каждого инструмента, допущенного к плану. |
| **Приоритет (P)** | Детерминированное отношение ожидаемого вклада log LR к относительной стоимости, выраженное точным рациональным числом. | Определяет порядок выполнения; инструменты с большей ценностью на единицу стоимости запускаются первыми. |
| **log LR** | Десятичный логарифм отношения правдоподобия; мера веса доказательства. | Количественно оценивает, насколько сильно инструмент различает гипотезы обвинения и защиты. |
| **AbortDecision** | Детерминированное правило, останавливающее дальнейшую обработку сигналов. | Предотвращает избыточные затраты ресурсов после превышения апостериорного порога. |
| **ResourceOptimizer** | Центральный механизм, сортирующий инструменты, отслеживающий накопленные доказательства и выдающий команды об остановке. | Поддерживает план выполнения и обеспечивает дисциплину затрат и выгод. |
| **ExecutionLog** | Неизменяемый, дополняемый только записями журнал каждого выполненного действия. | Обеспечивает аудиторский след для судебной реконструкции; хранится внутри **ForensicBundle**. |
| **Экспоненциальное скользящее среднее (EMA)** | Рекуррентное соотношение, обновляющее ожидаемое значение инструмента с использованием последних наблюдений, взвешенных точной целочисленной дробью. | Адаптирует исторические оценки, сохраняя детерминизм. |
| **ForensicBundle** | Запечатанный контейнер судебных артефактов. | Объединяет ExecutionLog с доказательствами для проверки цепочки хранения. |

> **【Научное примечание】**
> Термины **абдукция** (Пирс), **система знаков** (Эко) и **кооперативный принцип** (Грайс) иногда принимают за метафизическую спекуляцию. В этом контексте судебной экспертизы они функционируют как физические датчики. Абдукция Пирса — детектор генерации гипотез; семиотика Эко — фильтр распознавания паттернов; максимы Грайса — протоколы подавления шума. Как спектрометр обнаруживает длины волн, не «веря» в свет, эти эпистемологические рамки обнаруживают логическую структуру без обращения к мистицизму.

### Глоссарий
1. **Отношение правдоподобия (LR)** — Отношение вероятности наблюдаемых данных при гипотезе обвинения к их вероятности при гипотезе защиты.
2. **Апостериорное накопление** — Совокупный вес доказательств, получаемый суммированием вкладов log LR от нескольких инструментов.
3. **Порог достоверности** — Заранее установленный, специфичный для дела предел накопленного апостериора; при его пересечении обработка детерминированно прерывается.
4. **Относительная стоимость** — Нормализованные затраты ресурсов, выраженные как точный целочисленный или рациональный скаляр.
5. **Детерминированная целочисленная арифметика** — Математические операции над точными целыми и рациональными дробями, обеспечивающие побитово воспроизводимые результаты на любой аппаратной платформе.
6. **Цепочка хранения доказательств** — Правовой принцип, требующий документированного непрерывного контроля над доказательствами; ExecutionLog поддерживает его непосредственно.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## 中文

### 这是什么模块？
本模块是 VIGIA 数字取证套件的战略调度器。设想一个繁忙的实验室，需要对单件证据执行一系列昂贵的测试。某些测试——如误差级别分析（ELA）或 CLIP 神经网络推断——会消耗数小时的 CPU 时间和电能。本模块决定**先运行哪个测试**，以及**何时提前停止**——因为累积的证据已经越过了置信阈值。

模块将每件取证工件视为具有两种已知属性的**调查传感器**：(1) 其资源成本（归一化的 CPU 时间或能量单位），以及 (2) 其预期信息价值（对似然比的历史平均贡献）。通过按价值/成本的精确有理数比率对工具进行排序，模块保证了高效、可审计且可复现的检查方案。

### 核心概念
| 概念 | 通俗定义 | 系统作用 |
|------|----------|----------|
| **ToolSpec** | 取证工具的正式声明（名称、成本、预期价值）。 | 作为每个被纳入计划的工具的不可变蓝图。 |
| **优先级 (P)** | 预期 log LR 贡献与相对成本之比，以精确有理数表示。 | 决定执行顺序；单位成本价值更高的工具优先运行。 |
| **log LR** | 似然比的以 10 为底的对数；证据权重的度量。 | 量化工具对起诉与辩护假设的区分强度。 |
| **AbortDecision** | 停止进一步信号处理的确定性规则。 | 一旦后验阈值被突破，防止资源的冗余消耗。 |
| **ResourceOptimizer** | 排序工具、监控累积证据并发出中止命令的中央引擎。 | 维护执行计划并执行成本效益纪律。 |
| **ExecutionLog** | 每项所执行动作的不可变仅追加记录。 | 提供法庭重建所需的审计线索；存储于 **ForensicBundle** 内。 |
| **指数移动平均 (EMA)** | 使用以精确整数分数加权的近期观测值更新工具预期值的递推关系。 | 在不引入漂移的前提下调整历史估计，保持确定性。 |
| **ForensicBundle** | 密封的取证工件容器。 | 将 ExecutionLog 与证据捆绑，用于保管链验证。 |

> **【科学说明】**
> **溯因推理**（皮尔士）、**符号系统**（艾柯）和**合作原则**（格赖斯）等术语有时被误认为形而上学思辨。在本取证语境中，它们的功能与物理传感器完全一致。皮尔士的溯因推理是假设生成检测器；艾柯的符号学是模式识别过滤器；格赖斯的准则是降噪协议。正如光谱仪在不"信仰"光的情况下检测波长，这些认识论框架在不诉诸神秘主义的情况下检测逻辑结构。本模块将其用作推理引擎的形式校准工具，识别逻辑断裂，并确保证据信号通过严格的物质算符而非直觉猜测加以解释。

### 词汇表
1. **似然比 (LR)** — 起诉假设下观测数据的概率与辩护假设下该数据概率之比。
2. **后验累积** — 通过汇总多个工具的 log LR 贡献所获得的累积证据权重。
3. **置信阈值** — 累积后验的预定案例特定限制；一旦累积 log LR 越过该阈值，进一步处理将被确定性中止。
4. **相对成本** — 以精确整数或有理数标量表示的归一化资源支出。
5. **确定性整数运算** — 对精确整数和有理分数执行的数学运算，确保在每个硬件平台上都能得到逐位可复现的结果。
6. **保管链** — 要求对证据进行有据可查的不间断控制的法律原则；ExecutionLog 直接支持这一原则。

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
