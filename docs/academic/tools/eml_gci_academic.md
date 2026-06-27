<!--
VIGIA Academic Documentation
Module: e21ddd66
Batch ID: vigia-doc-0156-e21ddd66
Generated: 2026-05-20T14:56:47.878155+00:00
-->

---

## ENGLISH

### What Is This Module?

The file `vigia/tools/eml_gci.py` contains the **GCI Engine** (Generative Content Indicator). It is a forensic analysis module that examines sequences of time gaps—called *deltas*—between digital events (e.g., when a log entry was written, a document created, or an email edited). Its purpose is to reveal whether these intervals exhibit the mechanical regularity typical of automated generation, as opposed to the irregular rhythm of human activity. Crucially, the engine never discards information by returning a simple True/False flag. Instead, it returns a full numerical distribution (a z-score relative to an AUTHENTIC human baseline), allowing downstream systems to make informed, evidence-based decisions.

### Key Concepts

**Table 1: Core Procedures**
| Procedure | Scientific Role |
|---|---|
| `analyze_gci()` | Main entry point for the system bridge. Accepts either raw timestamps or pre-computed integer deltas. |
| `analyze_timestamps()` | Wrapper that converts epoch-second timestamps into integer deltas and delegates to the core analyzer. |
| `analyze_deltas()` | Core computation. Receives a list of whole-second intervals and deterministically computes the median absolute deviation (MAD) and the associated z-score against the baseline. |
| `build_baseline()` | Constructs the AUTHENTIC profile from collections of verified, human-generated delta sets. |
| `is_algorithmic()` | Derived advisory indicator only. It is a secondary interpretation of the z-score; the primary output remains the distribution itself. |
| `to_dict()` | Serializes the exact numeric results into a standardized dictionary structure. |
| `to_dict_display()` | Produces a rounded, human-readable view while preserving the exact underlying integers. |

**Table 2: Classes and Configuration**
| Name | Description |
|---|---|
| `GCIEngine` | Orchestrator that loads the baseline and executes deterministic comparisons on integer interval sets. |
| `GCIResult` | Enriched result container that always includes the full distribution, never a stripped boolean. |
| `_DEFAULT_ENGINE` | Singleton instance using the factory default baseline. |
| `MAX_INPUT_SIZE` | Upper limit on input cardinality to guarantee deterministic execution time and memory bounds. |

### Glossary

- **Delta**: The integer count of seconds between two consecutive events. The engine operates exclusively on these whole-number inputs.
- **Epoch second**: An integer timestamp counting seconds from the universal reference date 1970-01-01 UTC.
- **MAD (Median Absolute Deviation)**: A robust statistic measuring spread via the median of absolute deviations from the median. It naturally suppresses the influence of outliers without discarding data.
- **z-score (in this module)**: A deterministic index expressing how far an observed set of intervals deviates from the AUTHENTIC baseline, measured in MAD units. The computation uses exact integer inputs and deterministic scaling.
- **AUTHENTIC Baseline**: A pre-calibrated reference model derived from empirically verified human-generated timestamps.
- **Trust Decay**: A fixed penalty coefficient (0.4) applied to a trust score when the z-score exceeds the threshold of 2, signaling strong algorithmic regularity.
- **Heavy-tailed distribution**: A probability distribution where extreme values occur more frequently than in a normal distribution, necessitating robust statistics like MAD.
- **Outlier**: An extreme observation that lies far from the central tendency of the dataset.
- **Deterministic integer arithmetic**: Exact calculations performed on integer inputs (seconds, counts, ranks) that yield reproducible results without reliance on floating-point approximations in the primary pipeline.

### 【Scientific Note】
Semiotic terminology invoked elsewhere in the VIGIA framework—deriving from Peirce, Eco, and Grice—is an analytical instrumentation suite, not mysticism. Treat these terms as sensors: a spectrometer does not "believe" in light; it registers specific wavelengths. Likewise, these conceptual sensors register classes of logical relations within evidence. The GCI Engine itself is built upon deterministic integer arithmetic: exact counts of epoch seconds and exact median deviations. This design guarantees that every measurement is reproducible and free from the uncertainty introduced by floating-point representations.

---

## ESPAÑOL

### ¿Qué es este módulo?

El archivo `vigia/tools/eml_gci.py` alberga el **Motor GCI** (Generative Content Indicator). Es un módulo de análisis forense que examina secuencias de intervalos temporales —llamados *deltas*— entre eventos digitales (por ejemplo, la escritura de una entrada de registro, la creación de un documento o la edición de un correo). Su finalidad es revelar si dichos intervalos exhiben la regularidad mecánica propia de la generación automatizada, en contraste con el ritmo irregular de la actividad humana. Es crucial que el motor nunca descarte información devolviendo un simple flag Verdadero/Falso. En su lugar, retorna una distribución numérica completa (un z-score respecto a una línea base AUTHENTIC humana), permitiendo que los sistemas posteriores tomen decisiones informadas basadas en evidencia.

### Conceptos clave

**Tabla 1: Procedimientos principales**
| Procedimiento | Rol científico |
|---|---|
| `analyze_gci()` | Punto de entrada principal para el puente del sistema. Acepta timestamps o deltas enteros precomputados. |
| `analyze_timestamps()` | Envoltorio que convierte timestamps en segundos-epoch a deltas enteros y delega al analizador central. |
| `analyze_deltas()` | Cálculo central. Recibe una lista de intervalos en segundos enteros y computa de forma determinista la desviación absoluta mediana (MAD) y el z-score asociado contra la línea base. |
| `build_baseline()` | Construye el perfil AUTHENTIC a partir de colecciones de conjuntos de deltas verificados de origen humano. |
| `is_algorithmic()` | Indicador derivado meramente informativo. Es una interpretación secundaria del z-score; la salida primaria sigue siendo la distribución. |
| `to_dict()` | Serializa los resultados numéricos exactos en un diccionario estandarizado. |
| `to_dict_display()` | Produce una vista redondeada legible para humanos preservando los enteros exactos subyacentes. |

**Tabla 2: Clases y configuración**
| Nombre | Descripción |
|---|---|
| `GCIEngine` | Orquestador que carga la línea base y ejecuta comparaciones deterministas sobre conjuntos de intervalos enteros. |
| `GCIResult` | Contenedor de resultado enriquecido que siempre incluye la distribución completa, nunca un booleano reducido. |
| `_DEFAULT_ENGINE` | Instancia singleton que utiliza la línea base por defecto de fábrica. |
| `MAX_INPUT_SIZE` | Límite superior de cardinalidad de entrada para garantizar tiempos de ejecución y límites de memoria deterministas. |

### Glosario

- **Delta**: Recuento entero de segundos entre dos eventos consecutivos. El motor opera exclusivamente sobre estas entradas de números enteros.
- **Segundo epoch**: Marca temporal de número entero que cuenta segundos desde la fecha de referencia universal 1970-01-01 UTC.
- **MAD (Median Absolute Deviation)**: Estadístico robusto que mide la dispersión mediante la mediana de las desviaciones absolutas respecto a la mediana. Suprime naturalmente la influencia de valores atípicos sin descartar datos.
- **z-score (en este módulo)**: Índice determinista que expresa cuánto se desvía un conjunto observado de intervalos de la línea base AUTHENTIC, medido en unidades MAD. El cálculo utiliza entradas enteras exactas y escalamiento determinista.
- **Línea base AUTHENTIC**: Modelo de referencia precalibrado derivado de marcas temporales de origen humano verificadas empíricamente.
- **Trust Decay (Decaimiento de confianza)**: Coeficiente de penalización fijo (0,4) aplicado a una puntuación de confianza cuando el z-score supera el umbral de 2, señalando una regularidad algorítmica fuerte.
- **Distribución de colas pesadas (heavy-tailed)**: Distribución de probabilidad donde los valores extremos ocurren con mayor frecuencia que en una distribución normal, lo que hace necesario el uso de estadísticos robustos como MAD.
- **Valor atípico (outlier)**: Observación extrema que se sitúa lejos de la tendencia central del conjunto de datos.
- **Aritmética entera determinista**: Cálculos exactos realizados sobre entradas enteras (segundos, conteos, rangos) que producen resultados reproducibles sin recurrir a aproximaciones de coma flotante en la canalización principal.

### 【Nota Científica】
La terminología semiótica invocada en el marco VIGIA —derivada de Peirce, Eco y Grice— constituye un arsenal de instrumentación analítica, no misticismo. Considere estos términos como sensores: un espectrómetro no «cree» en la luz, sino que registra longitudes de onda específicas. De igual modo, estos sensores conceptuales registran clases de relaciones lógicas dentro de la evidencia. El Motor GCI se construye sobre aritmética entera determinista: conteos exactos de segundos-epoch y desviaciones medianas exactas. Este diseño garantiza que cada medición sea reproducible y libre de la incertidumbre introducida por las representaciones de coma flotante.

---

## РУССКИЙ

### Что представляет собой этот модуль?

Файл `vigia/tools/eml_gci.py` содержит **движок GCI** (Generative Content Indicator — Индикатор генеративного контента). Это судебно-аналитический модуль, исследующий последовательности временны́х промежутков — *дельт* — между цифровыми событиями (например, записью в журнале, созданием документа или редактированием электронной почты). Его цель — выявить, обнаруживают ли эти интервалы механическую регулярность, характерную для автоматической генерации, в отличие от нерегулярного ритма человеческой деятельности. Важно, что движок никогда не уничтожает информацию, возвращая простой флаг Истина/Ложь. Вместо этого он выдаёт полное числовое распределение (z-score относительно человеческой базы AUTHENTIC), позволяя последующим системам принимать обоснованные решения на основе доказательств.

### Ключевые концепции

**Таблица 1. Основные процедуры**
| Процедура | Научное назначение |
|---|---|
| `analyze_gci()` | Главная точка входа для системного моста. Принимает либо исходные временные метки, либо предварительно вычисленные целочисленные дельты. |
| `analyze_timestamps()` | Обертка, преобразующая временные метки в эпохальных секундах в целочисленные дельты с делегированием центральному анализатору. |
| `analyze_deltas()` | Центральное вычисление. Получает список интервалов в целых секундах и детерминированно вычисляет медианное абсолютное отклонение (MAD) и соответствующий z-score относительно базы. |
| `build_baseline()` | Строит профиль AUTHENTIC на основе собраний проверенных человеческих наборов дельт. |
| `is_algorithmic()` | Производный информационный индикатор. Это вторичная интерпретация z-score; первичным результатом остаётся само распределение. |
| `to_dict()` | Сериализует точные числовые результаты в стандартизированную структуру словаря. |
| `to_dict_display()` | Формирует округлённое, удобочитаемое представление, сохраняя при этом точные целочисленные данные в основе. |

**Таблица 2. Классы и конфигурация**
| Имя | Описание |
|---|---|
| `GCIEngine` | Оркестратор, загружающий базу и выполняющий детерминированные сравнения на наборах целочисленных интервалов. |
| `GCIResult` | Расширенный контейнер результатов, всегда включающий полное распределение, а не усечённое булево значение. |
| `_DEFAULT_ENGINE` | Одиночный экземпляр, использующий базу по умолчанию. |
| `MAX_INPUT_SIZE` | Верхний предел мощности входных данных для гарантии детерминированного времени выполнения и ограничений памяти. |

### Глоссарий

- **Дельта**: Целочисленное количество секунд между двумя последовательными событиями. Движок работает исключительно с такими целочисленными входными данными.
- **Эпохальная секунда**: Целочисленная временная метка, отсчитывающая секунды от универсальной опорной даты 1970-01-01 UTC.
- **MAD (Медианное абсолютное отклонение)**: Робастная статистика, измеряющая разброс через медиану абсолютных отклонений от медианы. Естественно подавляет влияние выбросов, не отбрасывая данные.
- **z-score (в данном модуле)**: Детерминированный индекс, выражающий, насколько наблюдаемый набор интервалов отклоняется от базы AUTHENTIC, измеренный в единицах MAD. Вычисление использует точные целочисленные входные данные и детерминированное масштабирование.
- **База AUTHENTIC**: Предварительно откалиброванная эталонная модель, полученная из эмпирически верифицированных временных меток человеческого происхождения.
- **Trust Decay (Затухание доверия)**: Фиксированный штрафной коэффициент (0,4), применяемый к баллу доверия, когда z-score превышает порог 2, сигнализируя о сильной алгоритмической регулярности.
- **Тяжелохвостое распределение**: Распределение вероятностей, в котором экстремальные значения встречаются чаще, чем в нормальном распределении, что требует применения робастных статистик, таких как MAD.
- **Выброс**: Экстремальное наблюдение, далеко отстоящее от центральной тенденции набора данных.
- **Детерминированная целочисленная арифметика**: Точные вычисления на целочисленных входных данных (секунды, счётчики, ранги), дающие воспроизводимые результаты без приближений с плавающей запятой в основном конвейере.

### 【Научное примечание】
Семиотическая терминология, используемая в рамках VIGIA — восходящая к Пирсу, Эко и Грайсу — представляет собой набор аналитических инструментальных средств, а не мистицизм. Воспринимайте эти термины как датчики: спектрометр не «верит» в свет; он регистрирует конкретные длины волн. Аналогично, эти концептуальные датчики регистрируют классы логических отношений внутри доказательств. Сам движок GCI построен на детерминированной целочисленной арифметике: точных подсчётах эпохальных секунд и точных медианных отклонениях. Такой дизайн гарантирует, что каждое измерение воспроизводимо и свободно от неопределённости, вносимой представлениями с плавающей запятой.

---

## 中文

### 本模块是什么？

文件 `vigia/tools/eml_gci.py` 包含 **GCI 引擎**（Generative Content Indicator，生成内容指示器）。这是一个取证分析模块，用于检查数字事件之间时间间隔序列——称为 *delta*——（例如日志条目写入时间、文档创建时间或电子邮件编辑时间）。其目的是揭示这些间隔是否呈现出自动生成特有的机械规律性，而非人类活动的不规则节律。至关重要的是，引擎绝不通过返回简单的真/假标志来丢弃信息。相反，它返回完整的数值分布（相对于 AUTHENTIC 人类基线的 z 分数），使下游系统能够做出有据可查的循证决策。

### 核心概念

**表 1：核心过程**
| 过程 | 科学作用 |
|---|---|
| `analyze_gci()` | 系统桥接的主入口点。接受原始时间戳或预计算的整数 delta。 |
| `analyze_timestamps()` | 将 epoch 秒时间戳转换为整数 delta 并委托给核心分析器的包装器。 |
| `analyze_deltas()` | 核心计算。接收整秒间隔列表，确定性地计算中位绝对偏差（MAD）及对应基线 z 分数。 |
| `build_baseline()` | 从经验证的人类生成 delta 集合中构建 AUTHENTIC 剖面。 |
| `is_algorithmic()` | 仅为派生的参考指标。是对 z 分数的二级解释；首要输出仍是分布本身。 |
| `to_dict()` | 将精确数值结果序列化为标准化字典结构。 |
| `to_dict_display()` | 在保留精确底层整数的同时，生成经四舍五入的人类可读视图。 |

**表 2：类与配置**
| 名称 | 描述 |
|---|---|
| `GCIEngine` | 加载基线并对整数间隔集执行确定性比较的编排器。 |
| `GCIResult` | 始终包含完整分布（而非被截断的布尔值）的增强结果容器。 |
| `_DEFAULT_ENGINE` | 使用工厂默认基线的单例实例。 |
| `MAX_INPUT_SIZE` | 输入基数上限，以保证确定性执行时间与内存边界。 |

### 术语表

- **Delta（时间间隔）**：两个连续事件之间的整数秒计数。引擎完全在这些整数输入上运算。
- **Epoch 秒**：以整数时间戳计量，从通用参考日期 1970-01-01 UTC 起算的秒数。
- **MAD（中位绝对偏差）**：通过计算各观测值与中位数偏差的中位数来度量离散程度的鲁棒统计量。在不丢弃数据的前提下自然抑制异常值的影响。
- **z 分数（本模块语境）**：一个确定性指标，以 MAD 为单位表达观测间隔集相对于 AUTHENTIC 基线的偏离程度。计算使用精确整数输入与确定性缩放。
- **AUTHENTIC 基线**：由经实证验证的人类生成时间戳推导出的预校准参考模型。
- **Trust Decay（信任衰减）**：当 z 分数超过阈值 2 时，应用于信任分数的固定惩罚系数（0.4），表示强烈的算法规律性。
- **重尾分布**：极端值出现频率高于正态分布的概率分布，需要使用 MAD 等鲁棒统计量。
- **异常值**：数据集中远离中心趋势的极端观测值。
- **确定性整数运算**：对整数输入（秒、计数、秩）执行的精确计算，在主管线中不依赖浮点近似即可产生可复现结果。
- **取证工件**：由引擎生成的、用于法务或科学审查的不可变数据对象。本模块输出的 GCIResult 即属此类。
- **逻辑断裂**：证据符号结构中的不连续性，常指示合成来源；GCI 通过确定性整数运算检测此类断裂的时间维度表现。

### 【科学说明】
VIGIA 框架中援引的符号学术语——源自皮尔斯、艾柯与格赖斯——是一套分析仪器化工具集，而非神秘主义。请将这些术语视为传感器：光谱仪不"相信"光；它记录特定波长。同样，这些概念性传感器记录证据中各类逻辑关系。GCI 引擎本身建立在确定性整数运算之上：对 epoch 秒的精确计数与精确中位数偏差。这一设计保证每次测量均可复现，且不受浮点数表示引入的不确定性影响。

---

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
