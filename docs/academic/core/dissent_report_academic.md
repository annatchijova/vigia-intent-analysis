<!--
VIGIA Academic Documentation
Module: 5fbbcb8f
Batch ID: vigia-doc-0047-5fbbcb8f
Generated: 2026-05-20T14:56:47.854612+00:00
-->

# Module Documentation: `vigia/core/dissent_report.py`

## ENGLISH

**What Is This Module?**

This module is a deterministic aggregator for multi-sensor forensic detection. In the VIGÍA system, multiple detection modules (specialized software sensors) analyze the same digital object and render independent classifications. This module collects those classifications, calculates exact consensus and dissent metrics using integer-ratio arithmetic, and produces a structured report. Its core scientific purpose is to prevent "majority suppression" — a tactic used by advanced persistent threats (APTs) to evade detection by forcing a false consensus of BENIGN. When one behavioral module reports MALICIOUS against nine others reporting BENIGN, this module escalates the minority opinion as a dissent signal requiring analyst review. All calculations are reproducible: identical inputs always produce identical reports, with no hardware-dependent variation.

**Key Concepts**

| Concept | Description |
|---|---|
| ModuleVerdict | The atomic classification produced by one detection engine (MALICIOUS, SUSPICIOUS, BENIGN, ABSTAIN). |
| ModuleOpinion | A verdict bound to its confidence score, expressed as exact rational numbers (Fraction), never approximate decimals. |
| DissentSignal | A minority opinion that survives noise filtering. It is preserved explicitly to prevent evasion via majority agreement. |
| DissentReport | The deterministic output document aggregating all opinions, the majority view, and all dissent signals. |
| Deterministic Scoring | All mathematics performed with Python's fractions.Fraction, ensuring identical inputs always yield identical reports across hardware and time. |
| Integer Display | Human-readable percentages are generated via integer truncation (int()), never rounding, eliminating reproducibility variance. |
| Noise Threshold | A minimum confidence level, defined as a Fraction, below which an opinion is treated as instrument noise rather than evidence. |
| Critical Dissent Threshold | A Fraction-based boundary that determines when a minority opinion is strong enough to be declared a dissent signal. |

**Functions and Output Methods**

| Function / Method | Purpose |
|---|---|
| generate_dissent_report() | Orchestrates the creation of the report. Accepts thresholds as Fraction objects to maintain exact arithmetic. |
| display_confidence_pct() | Converts an exact confidence fraction to an integer percentage by truncation. |
| display_majority_pct() | Truncated integer percentage of the majority bloc. |
| display_consensus_pct() | Truncated integer percentage representing overall consensus. |

**Constants**

| Constant | Scientific Meaning |
|---|---|
| MALICIOUS | Confirmed threat indicator. The object exhibits known or strongly inferred hostile behavior. |
| SUSPICIOUS | Anomalous characteristics detected, but insufficient evidence for a confirmed malicious verdict. |
| BENIGN | No threat indicators detected. Object appears safe under current analytical rules. |
| ABSTAIN | The module declined to render a verdict, typically due to insufficient data or out-of-scope analysis. |

**Glossary**

- **Advanced Persistent Threat (APT)**: A prolonged and targeted cyberattack in which an intruder establishes a long-term presence in a network to exfiltrate data or disrupt operations.
- **Determinism**: The property of a computational system whereby the same input always yields the same output, with no temporal or hardware-dependent variation.
- **Fraction (fractions.Fraction)**: A numeric type representing rational numbers exactly as pairs of integers (numerator, denominator). All arithmetic is integer-based.
- **Integer Truncation**: The discarding of a fractional remainder without rounding (e.g., 99.9 % becomes 99 %). This operation is deterministic.
- **Consensus Evasion**: An adversarial technique designed to force a majority of detection modules to agree on a false BENIGN classification, thereby suppressing true minority alarms.
- **Sensor Analogy**: The conceptual model treating each software detection module as an independent physical instrument measuring the same target with different physical principles.

**Scientific Note**

> 【Scientific Note】
> The terminology of Charles Sanders Peirce (abductive inference), Umberto Eco (semiotic threshold), and H. Paul Grice (cooperative principle / conversational implicature) is occasionally dismissed as metaphysical. Within this module, these frameworks are operationalized as rigorous engineering constraints. Use the sensor analogy: Peircean abduction is the generation of a best-fit hypothesis when a single instrument produces an anomalous reading; Eco's semiotic threshold is the noise floor below which a signal is classified as instrument error rather than a phenomenon; Gricean maxims function as inter-instrument communication protocols, ensuring each sensor conveys the maximally relevant information without redundancy. A dissenting module is not being uncooperative — it is a spectrometer reporting a spectral peak that optical cameras cannot resolve. In forensic science, suppressing such a signal in the name of consensus is a methodological failure, not a statistical correction.

---

## ESPAÑOL

**¿Qué es este módulo?**

Este módulo es un agregador determinista para la detección forense multi-sensor. En el sistema VIGÍA, múltiples módulos de detección (sensores software especializados) analizan el mismo objeto digital y emiten clasificaciones independientes. Este módulo recoge esas clasificaciones, calcula métricas exactas de consenso y disenso mediante aritmética de razones enteras, y produce un informe estructurado. Su propósito científico central es prevenir la "supresión mayoritaria" — una táctica empleada por amenazas persistentes avanzadas (APT) para evadir la detección forzando un falso consenso de BENIGNO. Cuando un módulo conductual reporta MALICIOSO frente a nueve que reportan BENIGNO, este módulo escala la opinión minoritaria como una señal de disenso que requiere revisión del analista. Todos los cálculos son reproducibles: entradas idénticas siempre producen informes idénticos, sin variación dependiente del hardware.

**Conceptos clave**

| Concepto | Descripción |
|---|---|
| ModuleVerdict | La etiqueta atómica asignada por un único motor de detección. Uno de cuatro estados posibles: MALICIOUS, SUSPICIOUS, BENIGN o ABSTAIN. |
| ModuleOpinion | Un veredicto vinculado a una puntuación de confianza exacta, almacenada como número racional (par de enteros numerador/denominador) en lugar de aproximación decimal. |
| DissentSignal | Una opinión minoritaria que supera el umbral de ruido y no debe ser silenciada. Representa una desviación estadísticamente significativa respecto a la mayoría. |
| DissentReport | El documento de salida determinista que registra cada módulo votante, cada abstención, el bloque mayoritario y todas las señales de disenso. |
| Puntuación Determinista | El uso de fractions.Fraction de Python para toda la aritmética. Cada valor de confianza es una razón exacta de dos enteros, garantizando la reproducibilidad entre plataformas. |
| Visualización Entera | Conversión de la confianza fraccionaria exacta a porcentajes legibles mediante truncamiento entero (int()), nunca redondeo. |
| Umbral de Ruido | Nivel mínimo de confianza, definido como Fraction, por debajo del cual una opinión se trata como ruido instrumental. |
| Umbral Crítico de Disenso | Límite basado en Fraction que determina cuándo una opinión minoritaria es lo suficientemente fuerte para declararse señal de disenso. |

**Funciones y métodos de salida**

| Función / Método | Propósito |
|---|---|
| generate_dissent_report() | Orquesta la generación del informe. Acepta umbrales como objetos Fraction para preservar la aritmética exacta en cada etapa de agregación. |
| display_confidence_pct() | Convierte una Fraction de confianza exacta a un porcentaje entero truncando la parte fraccionaria. |
| display_majority_pct() | Devuelve el porcentaje entero truncado que representa la proporción del bloque mayoritario. |
| display_consensus_pct() | Devuelve el porcentaje entero truncado que representa el nivel general de acuerdo. |

**Constantes**

| Constante | Significado Científico |
|---|---|
| MALICIOUS | Indicador de amenaza confirmada. El objeto exhibe comportamiento hostil conocido o fuertemente inferido. |
| SUSPICIOUS | Características anómalas detectadas, pero evidencia insuficiente para un veredicto malicioso confirmado. |
| BENIGN | No se detectan indicadores de amenaza. El objeto parece seguro bajo las reglas analíticas actuales. |
| ABSTAIN | El módulo declinó emitir un veredicto, típicamente por datos insuficientes o análisis fuera de alcance. |

**Glosario**

- **Amenaza Persistentemente Avanzada (APT)**: Un ciberataque prolongado y dirigido en el que un intruso establece una presencia a largo plazo en una red para exfiltrar datos o perturbar operaciones.
- **Determinismo**: Propiedad de un sistema computacional por la cual la misma entrada siempre produce la misma salida.
- **Fracción (fractions.Fraction)**: Un tipo numérico de Python que representa números racionales exactamente como pares de enteros (numerador, denominador).
- **Truncamiento Entero**: El descarte del resto fraccionario sin redondeo (p. ej., 99.9 % se convierte en 99 %).
- **Evasión por Consenso**: Una técnica adversarial diseñada para forzar a una mayoría de módulos de detección a acordar una falsa clasificación BENIGN.
- **Analogía del Sensor**: El modelo conceptual que trata cada módulo de detección software como un instrumento físico independiente.

**Nota Científica**

> 【Nota Científica】
> La terminología de Charles Sanders Peirce (inferencia abdutiva), Umberto Eco (umbral semiótico) y H. Paul Grice (principio cooperativo / implicatura conversacional) ocasionalmente se descarta como metafísica. Dentro de este módulo, estos marcos se operacionalizan como restricciones de ingeniería rigurosas. Use la analogía del sensor: la abducción peirceana es la generación de una hipótesis de mejor ajuste cuando un instrumento produce una lectura anómala; el umbral semiótico de Eco es el piso de ruido bajo el cual una señal se clasifica como error instrumental en lugar de un fenómeno; las máximas griceanas funcionan como protocolos de comunicación entre instrumentos, asegurando que cada sensor transmita la información máximamente relevante sin redundancia. Un módulo disidente no está siendo poco cooperativo: es un espectrómetro que reporta un pico espectral que las cámaras ópticas no pueden resolver. En ciencias forenses, suprimir tal señal en nombre del consenso es un fallo metodológico, no una corrección estadística.

---

## РУССКИЙ

**Что представляет собой этот модуль?**

Этот модуль является детерминированным агрегатором для многосенсорной криминалистической детекции. В системе VIGÍA множество модулей детекции (специализированных программных датчиков) анализируют один и тот же цифровой объект и выдают независимые классификации. Данный модуль собирает эти классификации, вычисляет точные метрики консенсуса и диссенсуса с помощью арифметики целочисленных отношений и формирует структурированный отчёт. Его основная научная цель — предотвратить «подавление большинством» — тактику, используемую продвинутыми постоянными угрозами (APT) для уклонения от обнаружения путём принуждения к ложному консенсусу BENIGN. Когда один поведенческий модуль сообщает MALICIOUS против девяти, сообщающих BENIGN, этот модуль эскалирует мнение меньшинства как сигнал диссенсуса. Все вычисления воспроизводимы.

**Ключевые концепции**

| Концепция | Описание |
|---|---|
| ModuleVerdict | Атомарная метка, присвоенная одним движком детекции. Одно из четырёх возможных состояний: MALICIOUS, SUSPICIOUS, BENIGN или ABSTAIN. |
| ModuleOpinion | Вердикт, связанный с точным значением достоверности, хранимым как рациональное число (пара целых чисел числитель/знаменатель). |
| DissentSignal | Мнение меньшинства, превышающее порог шума и не подлежащее заглушению. |
| DissentReport | Детерминированный выходной документ, фиксирующий каждый голосующий модуль, каждую абстенцию, большинственный блок и все сигналы диссенсуса. |
| Детерминированное оценивание | Использование fractions.Fraction из Python для всех вычислений. |
| Целочисленное отображение | Преобразование точной дробной достоверности в проценты путём усечения до целого (int()), а не округления. |
| Порог шума | Минимальный уровень достоверности, заданный как Fraction, ниже которого мнение рассматривается как шум прибора. |
| Критический порог диссенсуса | Граница на основе Fraction, определяющая, когда мнение меньшинства достаточно сильно. |

**Функции и методы вывода**

| Функция / Метод | Назначение |
|---|---|
| generate_dissent_report() | Организует генерацию отчёта. Принимает пороги в виде объектов Fraction, чтобы сохранить точную арифметику. |
| display_confidence_pct() | Преобразует точную дробь достоверности в целое процентное значение путём усечения. |
| display_majority_pct() | Возвращает усечённое целое процентное значение, представляющее долю большинственного голосующего блока. |
| display_consensus_pct() | Возвращает усечённое целое процентное значение общего уровня согласия. |

**Константы**

| Константа | Научное значение |
|---|---|
| MALICIOUS | Подтверждённый индикатор угрозы. |
| SUSPICIOUS | Обнаружены аномальные характеристики, но доказательств недостаточно. |
| BENIGN | Индикаторы угрозы не обнаружены. |
| ABSTAIN | Модуль отказался вынести вердикт из-за недостаточности данных. |

**Глоссарий**

- **Продвинутая постоянная угроза (APT)**: Длительная и целенаправленная кибератака.
- **Детерминизм**: Свойство системы, при котором одинаковые входные данные всегда дают одинаковый результат.
- **Дробь (fractions.Fraction)**: Тип данных Python, представляющий рациональные числа точно как пары целых чисел.
- **Усечение до целого**: Отбрасывание дробного остатка без округления.
- **Уклонение через консенсус**: Тактика принуждения большинства модулей к ложной классификации BENIGN.
- **Аналогия с датчиком**: Концептуальная модель, рассматривающая каждый программный модуль как независимый физический прибор.

**Научное примечание**

> 【Научное примечание】
> Терминология Пирса (абдукция), Эко (семиотический порог) и Грайса (кооперативный принцип / импликатура) иногда отвергается как метафизическая. В этом модуле эти концепции операционализированы как инженерные ограничения. Представьте лабораторную систему приборов: пирсовская абдукция — это генерация гипотез на основе аномальных показаний датчиков; семиотический порог Эко — это уровень шума, ниже которого сигнал считается приборной погрешностью; грайсовы максимы — это коммуникационные протоколы, гарантирующие, что каждый датчик сообщает максимально релевантную информацию без избыточности. Диссидентский модуль не «сложный» — это спектрометр, регистрирующий пик, который другие камеры не видят. Заглушать его — методологическая ошибка, а не статистическая коррекция.

---

## 中文

**本模块是什么？**

本模块是 VIGÍA 系统中的多传感器取证检测确定性聚合器。系统中多个检测模块（专门化的软件传感器）分析同一数字对象并给出独立分类。本模块收集这些分类，使用整数比运算计算精确的共识与异议指标，并生成结构化报告。其核心科学目的是防止"多数压制"——一种高级持续性威胁（APT）用于规避检测的策略，即通过强制达成虚假的"良性"共识来逃脱检测。当一个行为模块报告恶意而另外九个模块报告良性时，本模块将少数意见升级为需要分析师审查的异议信号。所有计算均可复现：相同输入始终产生相同报告，无任何硬件相关差异。

**核心概念**

| 概念 | 描述 |
|---|---|
| 模块裁决（ModuleVerdict） | 单个检测引擎产生的原子分类。四种可能状态之一：MALICIOUS、SUSPICIOUS、BENIGN 或 ABSTAIN。 |
| 模块意见（ModuleOpinion） | 与其置信度分数绑定的裁决，以精确有理数（分数）表示，而非近似小数。 |
| 异议信号（DissentSignal） | 通过噪声过滤的少数意见，需明确保存以防止因多数共识而被规避。 |
| 异议报告（DissentReport） | 聚合所有意见、多数观点及所有异议信号的确定性输出文档。 |
| 确定性评分 | 所有数学运算使用 fractions.Fraction，确保跨硬件和时间的相同输入始终产生相同报告。 |
| 整数显示 | 通过整数截断（int()）而非四舍五入将精确分数置信度转换为人类可读百分比。 |
| 噪声阈值 | 以 Fraction 定义的最低置信度水平，低于此水平的意见被视为仪器噪声。 |
| 关键异议阈值 | 基于 Fraction 的边界，确定少数意见何时足够强以被声明为异议信号。 |

**函数与输出方法**

| 函数/方法 | 用途 |
|---|---|
| generate_dissent_report() | 编排报告生成。接受 Fraction 对象作为阈值以保持精确运算。 |
| display_confidence_pct() | 通过截断将精确置信度 Fraction 转换为整数百分比。 |
| display_majority_pct() | 返回表示多数投票集团比例的截断整数百分比。 |
| display_consensus_pct() | 返回表示所有参与模块整体共识水平的截断整数百分比。 |

**常量**

| 常量 | 科学含义 |
|---|---|
| MALICIOUS（恶意） | 已确认的威胁指标。取证工件表现出已知或强烈推断的敌对行为。 |
| SUSPICIOUS（可疑） | 检测到异常特征，但证据不足以得出确认的恶意裁决。 |
| BENIGN（良性） | 未检测到威胁指标。取证工件在当前分析规则下看似安全。 |
| ABSTAIN（弃权） | 模块拒绝给出裁决，通常因数据不足或分析超出范围。 |

**术语表**

- **高级持续性威胁（APT）**：入侵者在网络中建立长期存在以窃取数据或破坏操作的长期定向网络攻击。
- **确定性**：计算系统的属性，同一输入始终产生同一输出，无时间或硬件相关差异。
- **分数（fractions.Fraction）**：以整数对（分子、分母）精确表示有理数的数值类型。所有运算均基于整数。
- **整数截断**：丢弃分数余数而不四舍五入（例如 99.9% 变为 99%）。该操作是确定性的。
- **共识规避**：设计用于迫使大多数检测模块同意虚假良性分类的对抗性技术，从而压制真正的少数警报。
- **传感器类比**：将每个软件检测模块视为用不同物理原理测量同一目标的独立物理仪器的概念模型。

**科学说明**

> 【科学说明】
> 皮尔斯（Peirce）的溯因推理、艾柯的符号学阈值，以及格赖斯的合作原则与含义理论，有时被误认为神秘主义或玄学话语。在本模块中，这些概念被严格操作化为工程约束。请使用传感器类比：将每个检测模块视为实验室中独立的物理仪器——皮尔斯式的溯因是从异常传感器读数中生成最佳假设；艾柯的符号学阈值即为噪声基底，低于该基底的信号被归类为仪器误差而非现象；格赖斯的量准则与关系准则则构成仪器间通信协议，确保每台传感器报告最大相关数据而不冗余。当单一模块发出异议信号时，它并非"不合作"，而是一台光谱仪探测到了其他成像设备无法感知的峰值。在取证科学中，以"多数共识"压制此类信号不是统计修正，而是方法论上的逻辑断裂。

---

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
