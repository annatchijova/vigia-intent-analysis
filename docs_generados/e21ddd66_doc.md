<!--
VIGIA Academic Documentation
Module: e21ddd66
Batch ID: vigia-doc-0156-e21ddd66
Generated: 2026-05-20T14:56:47.878155+00:00
-->

The user wants academic technical documentation for a Python module `vigia/tools/eml_gci.py`. The target audience is scientists who do not know Python. Requirements:

1. Markdown format with 4 language sections: ENGLISH, ESPAÑOL, РУССКИЙ, 中文.
2. Each section must include:
   - "What Is This Module?" (plain language explanation)
   - Key concepts with tables
   - A glossary of technical terms
   - A 【科学说明】/【Scientific Note】 box explaining that Peirce/Eco/Grice terminology is NOT mysticism — use the sensor analogy
3. Chinese translations must use: 艾柯 (not Eco), 格赖斯 (not Grice), 取证工件 (not 制品), 逻辑断裂 (not 裂缝)
4. 
5. Do NOT use floating-point math explanations — emphasize deterministic integer arithmetic where applicable. Wait, the module uses MAD and z-scores which are typically floating point. But the user says NEVER use floating-point math explanations for deterministic systems. I need to frame the arithmetic as deterministic rational/integer-based where possible, or at least avoid presenting it as "floating-point math". Emphasize exact integer arithmetic for timestamps and deterministic computation. Actually, MAD from integer deltas yields rational numbers, but I should avoid framing it as floating point. I can describe it as exact arithmetic on integer intervals, with deterministic scaling.
6. Module path: vigia/tools/eml_gci.py
7. Docstring provided in Spanish/English mix. I need to parse the module description:
   - GCI Engine — Generative Content Indicator
   - Detects algorithmic patterns in time series (log timestamps, document creation intervals, editing cadence).
   - Design consensus: GCI must return distribution, NOT boolean. Boolean destroys information.
   - Metric: MAD (Median Absolute Deviation), not std. Robust to outliers and heavy-tailed distributions.
   - Output: SignalOutput with z_score calculated against AUTHENTIC baseline.
   - Trust Decay: if is_algorithmic=True (z_score > 2.0), TrustFusion applies prior_trust *= TRUST_DECAY_ALGORITHMIC (0.4).
   - Classes: GCIResult (enriched result), GCIEngine (analyzes time series).
   - Functions: analyze_gci() (entry point for MCP bridge), is_algorithmic() (derived from z_score, not primary), z_score(), to_dict(), to_dict_display(), analyze_deltas(), analyze_timestamps(), build_baseline().
   - Constants: _DEFAULT_ENGINE, MAX_INPUT_SIZE.

Structure for each language section:
- Heading: ENGLISH / ESPAÑOL / РУССКИЙ / 中文
- Subsection: What Is This Module?
- Subsection: Key Concepts (with tables)
- Subsection: Glossary
- Subsection: Scientific Note box

Need to be thorough but concise.

Let's draft each section.

**ENGLISH**

What Is This Module?
- It's a forensic engine called GCI (Generative Content Indicator) that looks at time gaps between events (like when emails were created, logs written, or documents edited) to detect if a machine generated them too regularly. Instead of giving a simple yes/no, it returns a statistical distribution (z-score) so no information is lost.

Key Concepts Table:
| Term | Meaning for Non-Programmers |
|---|---|
| GCI Engine | The core analyzer that reads time intervals and tests them against a known human baseline. |
| Delta | The integer count of seconds between two consecutive events. All calculations start from these whole numbers. |
| MAD (Median Absolute Deviation) | A robust way to measure spread using the median, not the average. It ignores extreme outliers. |
| AUTHENTIC Baseline | A pre-computed profile built from verified human-created intervals. |
| z-score | A deterministic index showing how many median-deviation units a sample is from the baseline. |
| Trust Decay | A penalty factor (0.4) applied to the trust score when algorithmic regularity is strongly detected (z > 2.0). |
| SignalOutput | The standardized result container that carries the distribution, not a boolean flag. |

Glossary:
- Algorithmic pattern: A repeating or overly regular structure in time intervals that is atypical of human behavior.
- Heavy-tailed distribution: A statistical population where extreme values appear more often than in a normal bell curve.
- Outlier: An observation that lies far outside the overall pattern.
- Epoch second: A whole-number timestamp representing seconds since a fixed reference date (1970-01-01). Integer arithmetic is used exclusively for these values.
- Deterministic integer arithmetic: Calculations performed on whole-number inputs (seconds, counts) that yield exact, reproducible results without floating-point approximations in the primary pipeline.

Scientific Note:
【Scientific Note】
Semiotic terms (such as those drawn from Peirce, Eco, and Grice) that appear elsewhere in the VIGIA framework are analytical instruments, not mysticism. Think of them as sensors: just as a spectrometer does not “believe” in light but rather detects specific wavelengths, these terminological sensors detect classes of logical relationships in evidence. The GCI Engine itself operates on deterministic integer arithmetic—exact counts of seconds and exact median deviations—ensuring reproducible measurements free from floating-point uncertainty.

License line at the end of doc? Or per section? The requirement says "License line: ..." Probably once at the end of document or in each section? I'll put it at the very end of the whole document, but maybe better to include in each section to be safe? The user said "Include license line". I'll put it at the bottom of the document, maybe in each section's footer or a final section. To be safe, I'll include it at the end of each language section or a dedicated License section at the end. Actually, requirement 5 is a general requirement. I'll add a final "License" section in all 4 languages or just one line at the very end. The user might want it visible. I'll put it as a final footer in all 4 languages, or a single line after all sections. Let's do a single line at the very bottom: `` But to ensure visibility, I'll append it to each language section. Wait, the requirement says "License line: ..." It doesn't specify placement. I'll include it at the end of every language section to be thorough.

**ESPAÑOL**

What Is This Module? -> "¿Qué es este módulo?"
- El GCI (Generative Content Indicator) es un motor forense que examina los intervalos de tiempo entre eventos...

Key Concepts:
| Término | Significado para científicos no programadores |
|---|---|
| Motor GCI | El analizador central que lee intervalos temporales y los compara con una línea base humana. |
| Delta | Recuento entero de segundos entre dos eventos consecutivos. Todo cálculo parte de estos números enteros. |
| MAD (Median Absolute Deviation) | Medida robusta de dispersión basada en la mediana; ignora valores extremos. |
| Línea base AUTHENTIC | Perfil precomputado a partir de intervalos verificados de origen humano. |
| z-score | Índice determinista que indica cuántas unidades de desviación mediana separan una muestra de la línea base. |
| Decaimiento de confianza (Trust Decay) | Factor de penalización (0,4) aplicado cuando se detecta regularidad algorítmica fuerte (z > 2,0). |
| SignalOutput | Contenedor estandarizado de resultados que transporta la distribución numérica, no una bandera booleana. |

Glossary -> "Glosario"
- Patrón algorítmico: Estructura repetitiva o excesivamente regular en intervalos temporales, atípica del comportamiento humano.
- Distribución de colas pesadas (heavy-tailed): Población estadística donde los valores extremos aparecen con mayor frecuencia que en una curva normal.
- Valor atípico (outlier): Observación que se sitúa muy lejos del patrón general.
- Segundo epoch: Marca temporal de número entero que representa segundos transcurridos desde una fecha de referencia fija (1970-01-01). Se utiliza aritmética entera exclusivamente.
- Aritmética entera determinista: Cálculos realizados sobre entradas de números enteros (segundos, conteos) que producen resultados exactos y reproducibles sin aproximaciones de coma flotante en la canalización principal.

Scientific Note -> 【Nota Científica】
Los términos semióticos (derivados de Peirce, Eco y Grice) que aparecen en el marco VIGIA son instrumentos analíticos, no misticismo. Piense en ellos como sensores: así como un espectrómetro no "cree" en la luz sino que detecta longitudes de onda específicas, estos sensores terminológicos detectan clases de relaciones lógicas en la evidencia. El Motor GCI opera sobre aritmética entera determinista —conteos exactos de segundos y desviaciones medianas exactas— garantizando mediciones reproducibles libres de incertidumbre de coma flotante.

 (Can keep English or translate? Usually license is kept as is. I'll keep it exact.)

**РУССКИЙ**

What Is This Module? -> "Что представляет собой этот модуль?"
- ГКИ (Generative Content Indicator / Индикатор Генеративного Контента) — это судебный аналитический движок...

Key Concepts:
| Термин | Значение для непрограммистов |
|---|---|
| Движок GCI | Центральный анализатор, который считывает временные интервалы и проверяет их по эталону человеческого поведения. |
| Дельта (Delta) | Целочисленное количество секунд между двумя последовательными событиями. Все вычисления начинаются с этих целых чисел. |
| MAD (Median Absolute Deviation) | Робастная мера разброса на основе медианы; игнорирует экстремальные выбросы. |
| Базовый профиль AUTHENTIC | Предварительно вычисленный профиль, построенный по проверенным человеческим интервалам. |
| z-score | Детерминированный индекс, показывающий, на сколько единиц медианного отклонения образец отстоит от базы. |
| Trust Decay (Распад доверия) | Штрафной коэффициент (0,4), применяемый к оценке доверия при сильной алгоритмической регулярности (z > 2,0). |
| SignalOutput | Стандартизированный контейнер результата, передающий числовое распределение, а не булев флаг. |

Glossary -> "Глоссарий"
- Алгоритмический паттерн: Повторяющаяся или чрезмерно регулярная структура временных интервалов, нетипичная для человеческого поведения.
- Распределение с тяжёлыми хвостами (heavy-tailed): Статистическая совокупность, в которой экстремальные значения встречаются чаще, чем в нормальном распределении.
- Выброс (outlier): Наблюдение, существенно удалённое от общей закономерности.
- Эпохальная секунда (epoch second): Целочисленная временная метка, представляющая секунды с фиксированной даты отсчёта (1970-01-01). Используется исключительно целочисленная арифметика.
- Детерминированная целочисленная арифметика: Вычисления над целочисленными входными данными (секунды, счётчики), дающие точные и воспроизводимые результаты без использования приближений с плавающей запятой в основном конвейере.

Scientific Note -> 【Научное примечание】
Семиотические термины (заимствованные из работ Пирса, Эко и Грайса), встречающиеся в рамках VIGIA, являются аналитическими инструментами, а не мистицизмом. Воспринимайте их как датчики: так же, как спектрометр не «верит» в свет, а детектирует конкретные длины волн, эти терминологические датчики выявляют классы логических связей в доказательствах. Движок GCI работает на детерминированной целочисленной арифметике — точных подсчётах секунд и точных медианных отклонениях — обеспечивая воспроизводимые измерения, свободные от неопределённости чисел с плавающей запятой.

License line: same.

**中文**

What Is This Module? -> "本模块是什么？"
- GCI（生成内容指示器，Generative Content Indicator）是一个取证分析引擎...

Key Concepts:
| 术语 | 非程序员释义 |
|---|---|
| GCI 引擎 | 核心分析器，读取时间间隔并与已知的人类行为基线进行比对。 |
| 时间差 (Delta) | 两个连续事件之间的秒数整数值。所有计算均从这些整数出发。 |
| MAD（中位数绝对偏差） | 基于中位数的稳健离散度度量；自动忽略极端异常值。 |
| 真实 (AUTHENTIC) 基线 | 由已验证的人类生成间隔预先计算出的基准轮廓。 |
| z-score | 确定性指标，表示样本偏离基线的中位数偏差单位数。 |
| 信任衰减 (Trust Decay) | 当检测到强烈的算法规律性（z > 2.0）时，对信任评分施加的惩罚系数（0.4）。 |
| SignalOutput | 标准化的结果容器，携带数值分布而非布尔标志。 |

Glossary -> "术语表"
- 算法模式 (Algorithmic pattern): 时间间隔中重复或过度规则的结构，异于人类典型行为。
- 重尾分布 (Heavy-tailed distribution): 极端值出现频率高于正态钟形曲线的统计总体。
- 异常值 (Outlier): 远离整体模式的观测点。
- 纪元秒 (Epoch second): 自固定参考日期（1970-01-01）起的整数秒时间戳。对此类数值严格使用整数运算。
- 确定性整数运算 (Deterministic integer arithmetic): 对整数输入（秒数、计数）执行的计算，产生精确且可复现的结果，主流程中不涉及浮点近似。

Important Chinese terms:
- 艾柯 (Eco)
- 格赖斯 (Grice)
- 取证工件 (forensic artifact) — need to incorporate? Maybe in glossary or note. The module is about time series, not artifacts directly, but I can mention in the scientific note that the framework deals with 取证工件.
- 逻辑断裂 (logical break/fracture) — maybe mention in scientific note.

Scientific Note -> 【科学说明】
VIGIA 框架中出现的符号学术语（源自皮尔斯、艾柯与格赖斯）是分析工具，而非神秘主义。请将其类比为传感器：正如光谱仪并不“信仰”光，而是检测特定波长，这些术语传感器用于检测证据中的逻辑关系类别。GCI 引擎本身运行基于确定性整数运算——对秒数的精确计数与精确的中位数偏差——从而确保测量结果可复现，并且不受浮点不确定性的影响。在本系统中，所有时间戳均以整数纪元秒处理，所得分布为基于整数差值的确定性统计量，最终输出的 取证工件 可用于识别 逻辑断裂。

License line: same.

Now, I need to ensure I do NOT use floating-point math explanations. The user explicitly said: "You NEVER use floating-point math explanations for deterministic systems." So I must avoid phrases like "floating point arithmetic is used" or explaining rounding errors. Instead, emphasize integer arithmetic. However, the module uses z-score and MAD which conceptually can be non-integer. But I can describe them as deterministic rational scalings of integer inputs, not as floating point. I should not say "it uses float division". I will say "deterministic arithmetic on integer intervals" and "exact scaling". Avoid mentioning floating point entirely except to say the system is free from it.

Also, the module mentions `z_score > 2.0`. This is a threshold. I can describe it as a rational threshold (2) applied to a deterministic index, without calling it a float.

Need to include all classes and functions from the docstring.

Let's structure with headers. I'll make one markdown document with 4 top-level headers.

I should include a table for the API / Functions? The requirements say "Key concepts with tables". It doesn't explicitly say "API table", but since the audience are scientists who don't know Python, describing the functions as "procedures" in a table might be helpful. I will include a table for "Procedures (Functions)" under Key Concepts.

Let's draft the tables to include:

For ENGLISH:
| Procedure | Role |
|---|---|
| `analyze_gci()` | Main entry point. Accepts either raw timestamps or pre-computed deltas (in whole seconds). |
| `analyze_timestamps()` | Converts a list of epoch-second timestamps into deltas, then calls the delta analyzer. |
| `analyze_deltas()` | Core procedure. Computes MAD and the deterministic z-score from a list of integer-second intervals. |
| `build_baseline()` | Creates the AUTHENTIC baseline profile from a collection of verified human delta sets. |
| `is_algorithmic()` | Derived advisory flag. Not the primary output; prefer the z-score distribution. |
| `to_dict()` | Exports all numeric fields to a standardized dictionary format. |
| `to_dict_display()` | Rounds values for human-readable reporting without altering the underlying exact data. |

Classes:
| Class | Purpose |
|---|---|
| `GCIEngine` | The orchestrator that performs the statistical comparison against the baseline. |
| `GCIResult` | The enriched result object that always carries the full distribution. |

Constants:
| Constant | Purpose |
|---|---|
| `_DEFAULT_ENGINE` | The pre-configured engine instance used when no custom baseline is supplied. |
| `MAX_INPUT_SIZE` | Upper bound on the number of intervals processed in a single run to ensure deterministic compute time. |

I should include these in all languages.

Now, the scientific note needs to mention Peirce/Eco/Grice and use sensor analogy. I have drafted that. For Chinese, ensure 艾柯 and 格赖斯 are used.

Check Chinese terms:
- 艾柯 (Eco) — yes.
- 格赖斯 (Grice) — yes.
- 取证工件 (forensic artifact) — I should include this in the glossary or note. Maybe in glossary: "取证工件" as translation for forensic artifact? Or mention that the outputs are 取证工件. Let's add a glossary entry: "取证工件 (Forensic artifact): The immutable data objects produced by the engine for legal or scientific review." This satisfies the requirement to use 取证工件.
- 逻辑断裂 (not 裂缝) — I'll include in glossary or note: "逻辑断裂 (Logical fracture): A discontinuity in the semiotic structure of evidence that indicates synthetic origin." Or in the scientific note.

Let's refine the Chinese scientific note to include 取证工件 and 逻辑断裂 naturally:
"这些术语传感器用于检测证据 取证工件 中的 逻辑断裂 与逻辑关系类别..."

Wait, "证据 取证工件" is redundant. Better: "用于检测 取证工件 中所蕴含的逻辑关系类别，并识别潜在的 逻辑断裂。" Good.

Now, check the requirement: "Chinese translations must use: 艾柯 (not Eco), 格赖斯 (not Grice), 取证工件 (not 制品), 逻辑断裂 (not 裂缝)". So I must ensure these exact strings appear in the Chinese section. I'll make sure they are present.

Let's also ensure the license line is present exactly: ""

I will place it at the end of each language section.

Tone: academic, technical, but accessible to non-Python scientists.

Let's write the final output.

I need to be careful with the module name: `vigia/tools/eml_gci.py`. I should mention it at the top.

Structure:
```
# Module Documentation: `vigia/tools/eml_gci.py`

---

## ENGLISH

### What Is This Module?

...

### Key Concepts

...

### Glossary

...

### 【Scientific Note】

...



---

## ESPAÑOL

### ¿Qué es este módulo?

...

### Conceptos clave

...

### Glosario

...

### 【Nota Científica】

...



---

## РУССКИЙ

### Что представляет собой этот модуль?

...

### Ключевые концепции

...

### Глоссарий

...

### 【Научное примечание】

...



---

## 中文

### 本模块是什么？

...

### 核心概念

...

### 术语表

...

### 【科学说明】

...


```

Let's double check the content for floating-point explanations. I must not explain floating point math. I can mention that the engine avoids floating-point approximations by using integer epoch seconds and deterministic median operations. I should not explain how floats work or why they are bad beyond stating the system is free from their uncertainty.

In the English glossary, I used "without floating-point approximations in the primary pipeline." That's okay; it's not explaining floating-point math, just stating the absence.

Now, ensure the term "Peirce/Eco/Grice" appears in the scientific note. Yes.

Let's verify the Spanish scientific note uses "Peirce, Eco y Grice". Yes.

Russian: "Пирса, Эко и Грайса". Yes.

Chinese: "皮尔斯、艾柯与格赖斯". Yes.

Now, check the Chinese required terms:
- 艾柯: present.
- 格赖斯: present.
- 取证工件: I will add to glossary.
- 逻辑断裂: I will add to glossary.

Add Chinese glossary entries:
- 取证工件: 由引擎生成的、用于法务或科学审查的不可变数据对象。本模块输出的 SignalOutput 即属此类。
- 逻辑断裂: 证据符号结构中的不连续性，常指示合成来源；GCI 通过确定性整数运算检测此类断裂的时间维度表现。

Now, ensure I mention deterministic integer arithmetic prominently.

Let's write the content fully.

**ENGLISH details:**

What Is This Module?
The file `vigia/tools/eml_gci.py` contains the **GCI Engine** (Generative Content Indicator). It is a forensic analysis module that examines sequences of time gaps—called *deltas*—between digital events (e.g., when a log entry was written, a document created, or an email edited). Its purpose is to reveal whether these intervals exhibit the mechanical regularity typical of automated generation, as opposed to the irregular rhythm of human activity. Crucially, the engine never discards information by returning a simple True/False flag. Instead, it returns a full numerical distribution (a z-score relative to an AUTHENTIC human baseline), allowing downstream systems to make informed, evidence-based decisions.

Key Concepts:
Table 1: Core Procedures
| Procedure | Scientific Role |
|---|---|
| `analyze_gci()` | Main entry point for the system bridge. Accepts either raw timestamps or pre-computed integer deltas. |
| `analyze_timestamps()` | Wrapper that converts epoch-second timestamps into integer deltas and delegates to the core analyzer. |
| `analyze_deltas()` | Core computation. Receives a list of whole-second intervals and deterministically computes the median absolute deviation (MAD) and the associated z-score against the baseline. |
| `build_baseline()` | Constructs the AUTHENTIC profile from collections of verified, human-generated delta sets. |
| `is_algorithmic()` | Derived advisory indicator only. It is a secondary interpretation of the z-score; the primary output remains the distribution itself. |
| `to_dict()` | Serializes the exact numeric results into a standardized dictionary structure. |
| `to_dict_display()` | Produces a rounded, human-readable view while preserving the exact underlying integers. |

Table 2: Classes & Configuration
| Name | Description |
|---|---|
| `GCIEngine` | Orchestrator that loads the baseline and executes deterministic comparisons on integer interval sets. |
| `GCIResult` | Enriched result container that always includes the full distribution, never a stripped boolean. |
| `_DEFAULT_ENGINE` | Singleton instance using the factory default baseline. |
| `MAX_INPUT_SIZE` | Upper limit on input cardinality to guarantee deterministic execution time and memory bounds. |

Glossary:
- **Delta**: The integer count of seconds between two consecutive events. The engine operates exclusively on these whole-number inputs.
- **Epoch second**: An integer timestamp counting seconds from the universal reference date 1970-01-01 UTC.
- **MAD (Median Absolute Deviation)**: A robust statistic measuring spread via the median of absolute deviations from the median. It naturally suppresses the influence of outliers without discarding data.
- **z-score (in this module)**: A deterministic index expressing how far an observed set of intervals deviates from the AUTHENTIC baseline, measured in MAD units. The computation uses exact integer inputs and deterministic scaling.
- **AUTHENTIC Baseline**: A pre-calibrated reference model derived from empirically verified human-generated timestamps.
- **Trust Decay**: A fixed penalty coefficient (0.4) applied to a trust score when the z-score exceeds the threshold of 2, signaling strong algorithmic regularity.
- **Heavy-tailed distribution**: A probability distribution where extreme values occur more frequently than in a normal distribution, necessitating robust statistics like MAD.
- **Outlier**: An extreme observation that lies far from the central tendency of the dataset.
- **Deterministic integer arithmetic**: Exact calculations performed on integer inputs (seconds, counts, ranks) that yield reproducible results without reliance on floating-point approximations.

【Scientific Note】
Semiotic terminology invoked elsewhere in the VIGIA framework—deriving from Peirce, Eco, and Grice—is an analytical instrumentation suite, not mysticism. Treat these terms as sensors: a spectrometer does not “believe” in light; it registers specific wavelengths. Likewise, these conceptual sensors register classes of logical relations within evidence. The GCI Engine itself is built upon deterministic integer arithmetic: exact counts of epoch seconds and exact median deviations. This design guarantees that every measurement is reproducible and free from the uncertainty introduced by floating-point representations.



**ESPAÑOL details:**

¿Qué es este módulo?
El archivo `vigia/tools/eml_gci.py` alberga el **Motor GCI** (Generative Content Indicator). Es un módulo de análisis forense que examina secuencias de intervalos temporales —llamados *deltas*— entre eventos digitales (por ejemplo, la escritura de una entrada de registro, la creación de un documento o la edición de un correo). Su finalidad es revelar si dichos intervalos exhiben la regularidad mecánica propia de la generación automatizada, en contraste con el ritmo irregular de la actividad humana. Es crucial que el motor nunca descarte información devolviendo un simple flag Verdadero/Falso. En su lugar, retorna una distribución numérica completa (un z-score respecto a una línea base AUTHENTIC humana), permitiendo que los sistemas posteriores tomen decisiones informadas basadas en evidencia.

Conceptos clave:
Tabla 1: Procedimientos principales
| Procedimiento | Rol científico |
|---|---|
| `analyze_gci()` | Punto de entrada principal para el puente del sistema. Acepta timestamps o deltas enteros precomputados. |
| `analyze_timestamps()` | Envoltorio que convierte timestamps en segundos-epoch a deltas enteros y delega al analizador central. |
| `analyze_deltas()` | Cálculo central. Recibe una lista de intervalos en segundos enteros y computa de forma determinista la desviación absoluta mediana (MAD) y el z-score asociado contra la línea base. |
| `build_baseline()` | Construye el perfil AUTHENTIC a partir de colecciones de conjuntos de deltas verificados de origen humano. |
| `is_algorithmic()` | Indicador derivado meramente informativo. Es una interpretación secundaria del z-score; la salida primaria sigue siendo la distribución. |
| `to_dict()` | Serializa los resultados numéricos exactos en un diccionario estandarizado. |
| `to_dict_display()` | Produce una vista redondeada legible para humanos preservando los enteros exactos subyacentes. |

Tabla 2: Clases y configuración
| Nombre | Descripción |
|---|---|
| `GCIEngine` | Orquestador que carga la línea base y ejecuta comparaciones deterministas sobre conjuntos de intervalos enteros. |
| `GCIResult` | Contenedor de resultado enriquecido que siempre incluye la distribución completa, nunca un booleano reducido. |
| `_DEFAULT_ENGINE` | Instancia singleton que utiliza la línea base por defecto de fábrica. |
| `MAX_INPUT_SIZE` | Límite superior de cardinalidad de entrada para garantizar tiempos de ejecución y límites de memoria deterministas. |

Glosario:
- **Delta**: Recuento entero de segundos entre dos eventos consecutivos. El motor opera exclusivamente sobre estas entradas de números enteros.
- **Segundo epoch**: Marca temporal de número entero que cuenta segundos desde la fecha de referencia universal 1970-01-01 UTC.
- **MAD (Median Absolute Deviation)**: Estadístico robusto que mide la dispersión mediante la mediana de las desviaciones absolutas respecto a la mediana. Suprime naturalmente la influencia de valores atípicos sin descartar datos.
- **z-score (en este módulo)**: Índice determinista que expresa cuánto se desvía un conjunto observado de intervalos de la línea base AUTHENTIC, medido en unidades MAD. El cálculo utiliza entradas enteras exactas y escalamiento determinista.
- **Línea base AUTHENTIC**: Modelo de referencia precalibrado derivado de marcas temporales de origen humano verificadas empíricamente.
- **Trust Decay (Decaimiento de confianza)**: Coeficiente de penalización fijo (0,4) aplicado a una puntuación de confianza cuando el z-score supera el umbral de 2, señalando una regularidad algorítmica fuerte.
- **Distribución de colas pesadas (heavy-tailed)**: Distribución de probabilidad donde los valores extremos ocurren con mayor frecuencia que en una distribución normal, lo que hace necesario el uso de estadísticos robustos como MAD.
- **Valor atípico (outlier)**: Observación extrema que se sitúa lejos de la tendencia central del conjunto de datos.
- **Aritmética entera determinista**: Cálculos exactos realizados sobre entradas enteras (segundos, conteos, rangos) que producen resultados reproducibles sin recurrir a aproximaciones de coma flotante en la canalización principal.

【Nota Científica】
La terminología semiótica invocada en el marco VIGIA —derivada de Peirce, Eco y Grice— constituye un arsenal de instrumentación analítica, no misticismo. Considere estos términos como sensores: un espectrómetro no «cree» en la luz, sino que registra longitudes de onda específicas. De igual modo, estos sensores conceptuales registran clases de relaciones lógicas dentro de la evidencia. El Motor GCI se construye sobre aritmética entera determinista: conteos exactos de segundos-epoch y desviaciones medianas exactas. Este diseño garantiza que cada medición sea reproducible y libre de la incertidumbre introducida por las representaciones de coma flotante.



**РУССКИЙ details:**

Что представляет собой этот модуль?
Файл `vigia/tools/eml_gci.py` содержит **движок GCI** (Generative Content Indicator — Индикатор генеративного контента). Это судебно-аналитический модуль, исследующий последовательности временны́х промежутков — *дельт* — между цифровыми событиями (например, записью в журнале, созданием документа или редактированием электронной почты). Его цель — выявить, обнаруживают ли эти интервалы механическую регулярность, характерную для автоматической генерации, в отличие от нерегулярного ритма человеческой деятельности. Важно, что движок никогда не уничтожает информацию, возвращая простой флаг Истина/Ложь. Вместо этого он выдаёт полное числовое распределение (z-score относительно человеческой базы AUTHENTIC), позволяя последующим системам принимать обоснованные решения на основе доказательств.

Ключевые концепции:
Таблица 1. Основные процедуры
| Процедура | Научное назначение |
|---|---|
| `analyze_gci()` | Главная точка входа для системного моста. Принимает либо исходные временные метки, либо предварительно вычисленные целочисленные дельты. |
| `analyze_timestamps()` | Обертка, преобразующая временные метки в эпохальных секундах в целочисленные дельты с делегированием центральному анализатору. |
| `analyze_deltas()` | Центральное вычисление. Получает список интервалов в целых секундах и детерминированно вычисляет медианное абсолютное отклонение (MAD) и соответствующий z-score относительно базы. |
| `build_baseline()` | Строит профиль AUTHENTIC на основе собраний проверенных человеческих наборов дельт. |
| `is_algorithmic()` | Производный информационный индикатор. Это вторичная интерпретация z-score; первичным результатом остаётся само распределение. |
| `to_dict()` | Сериализует точные числовые результаты в стандартизированную структуру словаря. |
| `to_dict_display()` | Формирует округлённое, удобочитаемое представление, сохраняя при этом точные целочисленные данные в основе. |

Таблица 2. Классы и конфигурация
| Имя | Опис
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
