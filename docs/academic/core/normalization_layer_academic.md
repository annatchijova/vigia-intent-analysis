<!--
VIGIA Academic Documentation
Module: 6d01ab83
Batch ID: vigia-doc-0066-6d01ab83
Generated: 2026-05-20T14:56:47.858673+00:00
-->

ENGLISH:
- Title: Normalization Layer — VIGÍA Core
- What Is This Module? Explain it as a central translator/standardization lab. All forensic tools send signals in different "languages" (probabilistic formats). This layer converts them into a single, deterministic scale so scientists can compare them without knowing Python. Use Decimal (exact arithmetic) instead of float (approximate).
- Key Concepts Table:
  - NormalizedSignal | The standardized output container | Exact Decimal values in [0,1], Z-score, confidence, baseline version
  - NormalizationLayer | The gateway | Mandatory passage; no module can skip it
  - ToolName | Controlled vocabulary | Prevents arbitrary strings from contaminating the forensic chain of custody
  - Baseline (AUTHENTIC) | Reference ground truth | Computed with raw MAD (no 1.4826 Gaussian correction), deterministic integer arithmetic for robustness
  - Decimal vs Float | Exact vs approximate | Deterministic integer-based representation eliminates rounding non-determinism
  - Z-score | Distance from authentic baseline | Measured in units of raw MAD; positive = suspicious deviation
  - Constants (GCI, DGPI, etc.) | Signal source tags | Label provenance: semiotic, geopolitical, CAIE, etc.
- Functions Table:
  - normalize() | Translates one raw signal into the common space
  - batch_normalize() | Translates many signals at once
  - get_baseline_spec() | Exports baseline parameters for external audit (P2-A)
- Glossary:
  - Chain of custody | chronological documentation of evidence handling
  - Deterministic integer arithmetic | calculations using exact integer scalings (Decimal, Fraction) rather than binary floating-point approximations
  - Raw MAD | Median Absolute Deviation without the 1.4826 asymptotic correction factor used for Gaussian distributions
  - Semiotic (Peirce/Eco) | relating to the study of signs and meaning; in VIGÍA, it denotes evidence interpreted as a sign-system rather than raw data
  - Spoofability | the measurable susceptibility of a forensic metric to adversarial manipulation or false injection
  - Z-score | a standardized measure of how far an observed value deviates from a central baseline
- Scientific Note: Peirce (the logician), Eco (Umberto Eco, semiotician), and Grice (philosopher of language) developed vocabularies for how signs carry meaning and how humans infer intent from signals. VIGÍA borrows these terms precisely as engineering labels for sensor states. A "semiotic" signal is no more mystical than a voltage reading from a spectrophotometer; it is simply a structured observation that must be decoded against a known protocol. The NormalizationLayer treats these philosophical descriptors as deterministic sensor categories, ensuring that a sign from a geopolitical module and a sign from a CAIE module are both converted into the same exact numerical dialect before analysis.

ESPAÑOL:
- Similar structure.
- "¿Qué es este módulo?"
- Conceptos clave
- Glosario
- Nota científica: Peirce/Eco/Grice no son misticismo.
- Use same license line.
- Terms: NormalizedSignal -> SeñalNormalizada, NormalizationLayer -> CapaDeNormalización, ToolName -> NombreDeHerramienta.
- Raw MAD -> MAD crudo.
- Deterministic integer arithmetic -> aritmética entera determinista.

РУССКИЙ:
- "Что представляет собой этот модуль?"
- Ключевые понятия
- Глоссарий
- Научное примечание: терминология Пирса/Эко/Грайса — это не мистика.
- Names: НормализованныйСигнал (NormalizedSignal), СлойНормализации (NormalizationLayer), ИмяИнструмента (ToolName).
- Decimal: Decimal.
- Raw MAD: MAD без поправочного коэффициента 1,4826.
- Deterministic integer arithmetic: детерминированная целочисленная арифметика.

中文:
- 标题：归一化层 — VIGÍA 核心
- "本模块是什么？"
- 关键概念表
- 术语表
- 【科学说明】box
- Must use: 艾柯 (Eco), 格赖斯 (Grice), 取证工件 (artifact, though the user said 取证工件 instead of 制品), 逻辑断裂 (logical break/fracture instead of 裂缝).
- Note: The user said "取证工件" (not 制品) — I should use 取证工件 where appropriate or at least ensure I don't use 制品 for artifact/tool. Actually the user specifically listed these as Chinese translations that must be used. So I need to incorporate them naturally.
- Terms:
  - NormalizedSignal: 归一化信号
  - NormalizationLayer: 归一化层
  - ToolName: 工具名称枚举
  - Decimal: 十进制精确数 (Decimal)
  - Float: 浮点数 (but avoid explaining it; emphasize integer/Decimal)
  - Raw MAD: 原始中位数绝对偏差（不乘1.4826修正因子）
  - Z-score: Z分数 / 标准分数
  - Baseline: 基线
  - Deterministic integer arithmetic: 确定性整数运算
  - Chain of custody: 监管链
- Scientific Note: 皮尔士、艾柯与格赖斯的术语并非神秘主义。用传感器类比。

General technical details to convey:
- The module acts as a mandatory gateway (pasarela).
- It unifies different probabilistic "dialects" from upstream modules into one exact representation.
- Uses Python's `Decimal` and `Fraction` (exact rational numbers) rather than binary floating-point (`float`) to ensure reproducibility.
- Z-score is computed against an AUTHENTIC baseline using raw MAD (no 1.4826 factor). This is important because 1.4826 is a correction factor to make MAD a consistent estimator for the standard deviation under a normal distribution. Omitting it means the MAD stays as a pure median-of-deviations metric, which is robust and deterministic.
- ToolName enum prevents arbitrary strings, ensuring chain of custody integrity.
- Constants label the provenance of each signal.
- get_baseline_spec() is for external audit (P2-A).
- batch_normalize() handles multiple signals deterministically.

I must NOT explain floating-point math. So instead of saying "float is bad because of IEEE 754 rounding", I should say "Decimal uses deterministic integer arithmetic at a fixed scale, eliminating representation uncertainty."

The scientific note about Peirce/Eco/Grice: The module docstring mentions "Semiótico". This refers to Charles Sanders Peirce (logic, semiotics), Umberto Eco (semiotics), and H.P. Grice (pragmatics, implicature). The note should say: these are analytical frameworks for how signs convey meaning. In VIGÍA, a "semiotic signal" is treated like a sensor output that encodes information via a known protocol. Just as a mass spectrometer outputs voltage that represents molecular weight, a semiotic module outputs a Fraction that represents an interpretive state. The normalization layer converts these heterogeneous sensor outputs into a common exact scale. It is engineering, not mysticism.

Now, writing the actual markdown. I'll make it thorough but concise. Each language section will be clearly marked.

## ENGLISH

### Module Overview
**Path:** `vigia/core/normalization_layer.py`  
**Version:** NormalizationLayer v2.0

#### What Is This Module?
Imagine a forensic laboratory where different instruments—a chromatograph, a geopolitical risk sensor, a logical-continuity probe, and a Bayesian likelihood engine—each produce readings in their own native scales and formats. Before any scientist can compare these readings, they must be translated into a single, exact, reproducible unit system.

The Normalization Layer is that central metrology laboratory. It is a **mandatory gateway**: no downstream analytical module may bypass it. It ingests raw signals from all upstream VIGÍA modules—whether they originate as exact rational numbers (Fraction/int), geopolitical sigmoid outputs, or posterior probabilities—and converts them into a unified deterministic representation based on **exact Decimal integer-scaled arithmetic**. This ensures that every signal is comparable, auditable, and free from the rounding non-determinism associated with approximate number systems.

#### Key Concepts

| Term | Plain-Language Definition | Scientific Role |
|---|---|---|
| **NormalizedSignal** | The standardized forensic container | Holds an exact `Decimal` value in [0, 1], a `z_score` relative to the AUTHENTIC baseline, a confidence metric, and a baseline version for calibration traceability. |
| **NormalizationLayer** | The unified gateway | Acts as the sole mandatory checkpoint. All signals must pass through it before reaching analytical dashboards or reporting engines. |
| **ToolName** | Strict enumeration of valid forensic tools | Prevents arbitrary text strings from entering the evidence pipeline, preserving **chain of custody** integrity. |
| **Decimal Integer-Scaled Arithmetic** | Exact computation using base-10 integer scaling | Replaces approximate representations with deterministic, reproducible precision suitable for legal and scientific review. |
| **Raw MAD Baseline** | Median Absolute Deviation without Gaussian correction | The AUTHENTIC baseline uses raw MAD (no 1.4826 factor). This keeps the metric robust and independent of normality assumptions. |
| **Z-score** | Standardized deviation from the authentic baseline | Expressed in raw MAD units. Indicates how atypical a signal is compared to known-authentic reference data. |
| **Signal Provenance Constants** (GCI, DGPI, CAIE, SDA, CLI, ROI, ACP, GEOPOLITICAL, ENTANGLEMENT, UNKNOWN) | Category labels for signal origin | Tag each normalized output with its source module, ensuring full traceability across the probabilistic space. |

#### Functions

| Function | Purpose |
|---|---|
| `normalize()` | Converts a single raw upstream signal into the common NormalizedSignal format using exact Decimal mapping. |
| `batch_normalize()` | Converts a collection of raw signals deterministically, preserving order and provenance. |
| `get_baseline_spec()` | Exports the current AUTHENTIC baseline parameters (P2-A) for independent external audit and replication. |

#### Glossary

- **Chain of custody**: The chronological, documented trail that records the seizure, control, transfer, analysis, and disposition of forensic evidence. Any break in this chain may compromise admissibility.
- **Deterministic integer arithmetic**: Mathematical operations performed on exact integer-scaled values (e.g., `Decimal` or `Fraction`) that yield the same result on every execution, with no rounding variance.
- **Raw MAD (Median Absolute Deviation)**: A robust measure of statistical dispersion calculated as the median of absolute deviations from the median. *Crucially*, the VIGÍA baseline omits the conventional 1.4826 scaling factor, keeping the metric non-parametric and deterministic.
- **Semiotic (Peirce / Eco)**: Pertaining to the theory of signs and interpretation. Within VIGÍA, this denotes evidence processed as structured sign-systems rather than uninterpreted raw data.
- **Spoofability**: A quantifiable vulnerability metric indicating how easily a forensic indicator can be manipulated, forged, or injected with adversarial noise.
- **Z-score**: A standardized score describing an observation's distance from a central reference value, here measured against the AUTHENTIC baseline using raw MAD units.

> 【Scientific Note】
> **Why the terminology of Peirce, Eco, and Grice is engineering, not mysticism.**
> 
> The upstream "Semiotic" module borrows concepts from Charles Sanders Peirce (logic of signs), Umberto Eco (codes of interpretation), and H. P. Grice (pragmatic implicature). In VIGÍA, these names function as **sensor-taxonomy labels**, not philosophical incantations. A "semiotic signal" is analogous to the voltage output from a spectrophotometer: it is a structured reading that must be decoded through a known analytical protocol. Peirce’s categories describe *states of information entropy*; Eco’s codes describe *encoding schemas*; Grice’s maxims describe *expected coherence constraints*. The NormalizationLayer treats these heterogeneous sensor outputs—semiotic, geopolitical, or CAIE—exactly as a data-acquisition system treats thermocouple versus photodiode outputs: it converts them into one exact, deterministic scale (Decimal) before any scientific comparison occurs. There is no hermeneutic mystery here—only reproducible metrology.

---

ESPAÑOL:

### ES PAÑOL (or just ### ESPAÑOL)

#### ¿Qué es este módulo?
Imaginemos un laboratorio forense donde distintos instrumentos—un cromatógrafo, un sensor de riesgo geopolítico, una sonda de continuidad lógica y un motor de probabilidad bayesiana—generan lecturas en sus propias escalas y formatos nativos. Antes de que un científico pueda compararlas, deben traducirse a un sistema de unidades único, exacto y reproducible.

La Capa de Normalización es ese laboratorio central de metrología. Es una **pasarela obligatoria**: ningún módulo analítico posterior puede eludirla. Ingiere señales crudas de todos los módulos VIGÍA aguas arriba—ya sean números racionales exactos (Fraction/int), salidas sigmoides geopolíticas o probabilidades a posteriori—y las convierte en una representación unificada y determinista basada en **aritmética entera escalada en Decimal exacto**. Así, cada señal es comparable, auditable y libre del no-determinismo del redondeo propio de los sistemas numéricos aproximados.

#### Conceptos clave

| Término | Definición en lenguaje sencillo | Función científica |
|---|---|---|
| **SeñalNormalizada** | El contenedor forense estandarizado | Almacena un valor `Decimal` exacto en [0, 1], un `z_score` respecto a la línea base AUTHENTIC, una métrica de confianza y una versión de calibración para trazabilidad. |
| **CapaDeNormalización** | La pasarela unificada | Actúa como el único punto de control obligatorio. Toda señal debe atravesarla antes de llegar a paneles analíticos o motores de informes. |
| **NombreDeHerramienta** | Enumeración estricta de herramientas forenses válidas | Evita que cadenas de texto arbitrarias entren en la tubería de evidencia, preservando la integridad de la **cadena de custodia**. |
| **Aritmética entera escalada en Decimal** | Cómputo exacto mediante escalamiento entero en base 10 | Reemplaza las representaciones aproximadas por precisión determinista y reproducible, apta para revisión legal y científica. |
| **Línea base AUTHENTIC con MAD crudo** | Desviación absoluta mediana sin corrección gaussiana | La línea base emplea MAD crudo (sin factor 1.4826). Mantiene la métrica robusta e independiente de supuestos de normalidad. |
| **Z-score** | Desviación estandarizada respecto a la línea base auténtica | Expresado en unidades de MAD crudo. Indica cuán atípica es una señal comparada con datos de referencia conocidos como auténticos. |
| **Constantes de procedencia** (GCI, DGPI, CAIE, SDA, CLI, ROI, ACP, GEOPOLITICAL, ENTANGLEMENT, UNKNOWN) | Etiquetas categóricas del origen de la señal | Etiquetan cada salida normalizada con su módulo fuente, asegurando trazabilidad total en el espacio probabilístico. |

#### Funciones

| Función | Propósito |
|---|---|
| `normalize()` | Convierte una señal cruda individual al formato común NormalizedSignal usando mapeo Decimal exacto. |
| `batch_normalize()` | Convierte una colección de señales crudas de forma determinista, preservando orden y procedencia. |
| `get_baseline_spec()` | Exporta los parámetros actuales de la línea base AUTHENTIC (P2-A) para auditoría externa independiente y replicación. |

#### Glosario

- **Cadena de custodia**: El rastro documentado y cronológico que registra el decomiso, control, transferencia, análisis y disposición de la evidencia forense. Cualquier ruptura puede comprometer su admisibilidad.
- **Aritmética entera determinista**: Operaciones matemáticas realizadas sobre valores enteros escalados exactos (p. ej., `Decimal` o `Fraction`) que producen el mismo resultado en cada ejecución, sin varianza por redondeo.
- **MAD crudo (Median Absolute Deviation)**: Medida robusta de dispersión estadística calculada como la mediana de las desviaciones absolutas respecto a la mediana. *Crucialmente*, la línea base VIGÍA omite el factor de escala convencional 1,4826, manteniendo la métrica no paramétrica y determinista.
- **Semiótico (Peirce / Eco)**: Relativo a la teoría de los signos y la interpretación. Dentro de VIGÍA, denota evidencia procesada como sistemas de signos estructurados en lugar de datos brutos sin interpretar.
- **Spoofability** (vulnerabilidad a falsificación): Métrica cuantificable de la susceptibilidad de un indicador forense a ser manipulado, falsificado o inyectado con ruido adversarial.
- **Z-score**: Puntuación estandarizada que describe la distancia de una observación respecto a un valor de referencia central; aquí se mide contra la línea base AUTHENTIC en unidades de MAD crudo.

> 【Nota Científica】
> **Por qué la terminología de Peirce, Eco y Grice es ingeniería, no misticismo.**
> 
> El módulo "Semiótico" aguas arriba toma prestados conceptos de Charles Sanders Peirce (lógica de los signos), Umberto Eco (códigos de interpretación) y H. P. Grice (implicatura pragmática). En VIGÍA, estos nombres operan como **etiquetas taxonómicas de sensores**, no como invocaciones filosóficas. Una "señal semiótica" es análoga a la tensión de salida de un espectrofotómetro: es una lectura estructurada que debe decodificarse mediante un protocolo analítico conocido. Las categorías de Peirce describen *estados de entropía informativa*; los códigos de Eco describen *esquemas de codificación*; los máximas de Grice describen *restricciones de coherencia esperadas*. La Capa de Normalización trata estas salidas heterogéneas—semióticas, geopolíticas o CAIE—exactamente como un sistema de adquisición de datos trata las salidas de un termopar versus un fotodiodo: las convierte a una escala exacta y determinista (Decimal) antes de cualquier comparación científica. Aquí no hay misterio hermenéutico, solo metrología reproducible.

---

РУССКИЙ:

### РУССКИЙ

#### Что представляет собой этот модуль?
Представьте себе судебно-экспертную лабораторию, в которой различные приборы—хроматограф, сенсор геополитического риска, зонд логической непрерывности и байесовский модуль оценки правдоподобия—выдают показания в собственных шкалах и форматах. Прежде чем учёный сможет их сравнить, их необходимо перевести в единую, точную и воспроизводимую систему единиц.

Слой нормализации—это центральная метрологическая лаборатория. Это **обязательный шлюз**: ни один нижестоящий аналитический модуль не может его обойти. Он принимает сырые сигналы от всех вышестоящих модулей VIGÍA—будь то точные рациональные числа (Fraction/int), выходы геополитических сигмоид или апостериорные вероятности—и преобразует их в унифицированное детерминированное представление на основе **точной десятичной целочисленной арифметики с фиксированным масштабом**. Это гарантирует, что каждый сигнал сопоставим, поддаётся аудиту и свободен от недетерминизма округления, присущего приближённым числовым системам.

#### Ключевые понятия

| Термин | Определение простым языком | Научная роль |
|---|---|---|
| **НормализованныйСигнал** | Стандартизированный судебный контейнер | Содержит точное значение `Decimal` в [0, 1], `z_score` относительно базовой линии AUTHENTIC, метрику достоверности и версию калибровки для прослеживаемости. |
| **СлойНормализации** | Унифицированный шлюз | Является единственным обязательным контрольным пунктом. Все сигналы должны пройти через него перед поступлением в аналитические панели или системы отчётности. |
| **ИмяИнструмента** | Строгое перечисление допустимых судебных инструментов | Предотвращает попадание произвольных текстовых строк в канал следственных действий, сохраняя целостность **цепочки хранения**. |
| **Детерминированная целочисленная арифметика Decimal** | Точные вычисления с использованием целочисленного масштабирования по основанию 10 | Заменяет приближённые представления воспроизводимой детерминированной точностью, пригодной для судебной и научной экспертизы. |
| **Базовая линия AUTHENTIC с сырым MAD** | Медианное абсолютное отклонение без гауссовской поправки | Базовая линия использует сырой MAD (без коэффициента 1,4826). Это сохраняет метрику робастной и независимой от предположений о нормальности. |
| **Z-score** | Стандартизированное отклонение от аутентичной базовой линии | Выражается в единицах сырого MAD. Показывает, насколько атипичен сигнал по сравнению с достоверными эталонными данными. |
| **Константы происхождения сигнала** (GCI, DGPI, CAIE, SDA, CLI, ROI, ACP, GEOPOLITICAL, ENTANGLEMENT, UNKNOWN) | Категориальные метки источника сигнала | Маркируют каждый нормализованный выход своим исходным модулем, обеспечивая полную прослеживаемость в вероятностном пространстве. |

#### Функции

| Функция | Назначение |
|---|---|
| `normalize()` | Преобразует один сырой вышестоящий сигнал в общий формат NormalizedSignal с использованием точного отображения Decimal. |
| `batch_normalize()` | Детерминированно преобразует набор сырых сигналов, сохраняя порядок и происхождение. |
| `get_baseline_spec()` | Экспортирует текущие параметры базовой линии AUTHENTIC (P2-A) для независимой внешней аудиторской проверки и репликации. |

#### Глоссарий

- **Цепочка хранения**: Хронологически задокументированный след, фиксирующий изъятие, контроль, передачу, анализ и распоряжение судебным доказательством. Любой разрыв в этой цепи может поставить под сомнение допустимость доказательств.
- **Детерминированная целочисленная арифметика**: Математические операции над точными целочисленными значениями с масштабом (например, `Decimal` или `Fraction`), дающие одинаковый результат при каждом выполнении без вариативности округления.
- **Сырой MAD (медианное абсолютное отклонение)**: Робастная мера статистического разброса, вычисляемая как медиана абсолютных отклонений от медианы. *Существенно*, что базовая линия VIGÍA опускает общепринятый масштабирующий коэффициент 1,4826, сохраняя метрику непараметрической и детерминированной.
- **Семиотический (Пирс / Эко)**: Относящийся к теории знаков и интерпретации. Внутри VIGÍA обозначает доказательства, обработанные как структурированные знаковые системы, а не как неинтерпретированные сырые данные.
- **Спуфабельность (spoofability)**: Количественно измеряемый показатель уязвимости судебного индикатора к манипулированию, подделке или внедрению состязательного шума.
- **Z-score**: Стандартизированная оценка, описывающая расстояние наблюдаемого значения от центрального эталона; здесь измеряется относительно базовой линии AUTHENTIC в единицах сырого MAD.

> 【Научное примечание】
> **Почему терминология Пирса, Эко и Грайса — это инженерия, а не мистика.**
> 
> Вышестоящий «семиотический» модуль заимствует концепции у Чарльза Сандерса Пирса (логика знаков), Умберто Эко (коды интерпретации) и Г. П. Грайса (прагматическая импликатура). В VIGÍA эти имена функционируют как **таксономические метки сенсоров**, а не как философские заклинания. «Семиотический сигнал» аналогичен выходному напряжению спектрофотометра: это структурированное показание, которое должно быть декодировано по известному аналитическому протоколу. Категории Пирса описывают *состояния информационной энтропии*; коды Эко описывают *схемы кодирования*; максимы Грайса описывают *ожидаемые ограничения когерентности*. Слой нормализации обращается с этими гетерогенными выходами—семиотическими, геополитическими или CAIE—точно так же, как система сбора данных обращается с выходами термопары и фотодиода: он преобразует их в одну точную, детерминированную шкалу (Decimal) до любого научного сравнения. Здесь нет герменевтической тайны—только воспроизводимая метрология.

---

中文:

### 中文

#### 本模块是什么？
设想一间数字取证实验室，其中不同的仪器——色谱仪、地缘政治风险传感器、逻辑连续性探针以及贝叶斯似然引擎——各自以原生尺度和格式输出读数。在科学家能够比较这些读数之前，必须先将它们翻译成一套单一、精确且可复现的计量单位。

**归一化层（NormalizationLayer）** 就是这个中央计量实验室。它是一个**强制网关**：任何下游分析模块均不得绕过它。该层摄取来自所有上游 VIGÍA 模块的原始信号——无论其最初为精确有理数（Fraction/int 缩放）、地缘政治 sigmoid 输出，还是后验概率——并将其转换为基于**确定性整数运算的精确 Decimal 统一表示**。这确保了每个信号都具有可比性、可审计性，并且不受近似数系统舍入非确定性的影响。

#### 关键概念

| 术语 | 通俗定义 | 科学作用 |
|---|---|---|
| **归一化信号（NormalizedSignal）** | 标准化的取证输出容器 | 保存 [0,1] 范围内的精确 `Decimal` 数值、相对于 AUTHENTIC 基线的 `z_score`、置信度指标，以及用于校准可追溯性的基线版本号。 |
| **归一化层（NormalizationLayer）** | 统一的强制网关 | 作为唯一必经的检查点。所有信号在到达分析面板或报告引擎之前都必须通过此层。 |
| **工具名称枚举（ToolName）** | 有效取证工具的严格枚举 | 防止任意文本字符串进入证据流，保障**监管链（chain of custody）**的完整性。 |
| **Decimal 确定性整数运算** | 基于十进制整数缩放的精确计算 | 以确定性、可复现的精度取代近似表示，适用于法律与科学审查。 |
| **AUTHENTIC 基线与原始 MAD** | 不经高斯修正的中位数绝对偏差 | 基线采用原始 MAD（不乘 1.4826 因子），保持指标的稳健性，且不依赖于正态性假设。 |
| **Z 分数（Z-score）** | 相对于真实基线的标准化偏离 | 以原始 MAD 为单位。指示信号相对于已知真实参考数据的异常程度。 |
| **信号来源常量**（GCI、DGPI、CAIE、SDA、CLI、ROI、ACP、GEOPOLITICAL、ENTANGLEMENT、UNKNOWN） | 信号来源的类别标签 | 为每个归一化输出标记其来源模块，确保概率空间中的完全可追溯性。 |

#### 函数说明

| 函数 | 用途 |
|---|---|
| `normalize()` | 将单个上游原始信号通过精确的 Decimal 映射转换为通用的 NormalizedSignal 格式。 |
| `batch_normalize()` | 以确定性方式批量转换原始信号列表，保留顺序与来源信息。 |
| `get_baseline_spec()` | 导出当前 AUTHENTIC 基线参数（P2-A），供独立的外部审计与复现使用。 |

#### 术语表

- **监管链（Chain of custody）**：对取证证据的扣押、控制、转移、分析与处置进行按时间顺序记录的完整文书轨迹。任何断裂都可能损害证据的可采性。
- **确定性整数运算**：对精确整数缩放值（如 `Decimal` 或 `Fraction`）执行的数学运算，每次执行结果完全相同，不存在舍入差异。
- **原始 MAD（中位数绝对偏差）**：一种稳健的统计离散度度量，计算为各数据点到中位数的绝对偏差的中位数。*关键之处在于*，VIGÍA 的基线省略了常规的 1.4826 缩放因子，从而保持指标的非参数性与确定性。
- **符号学/语用学术语（Peirce / 艾柯 / 格赖斯）**：指关于符号与解释的理论。在 VIGÍA 中，它表示将证据作为结构化符号系统处理，而非未经解释的原始数据。
- **欺骗脆弱性（Spoofability）**：一种可量化的脆弱性指标，表明某一取证指标被操纵、伪造或注入对抗性噪声的难易程度。
- **Z 分数**：描述观测值与中心参考值之间距离的标准化得分；此处以原始 MAD 为单位，相对于 AUTHENTIC 基线进行度量。
- **
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
