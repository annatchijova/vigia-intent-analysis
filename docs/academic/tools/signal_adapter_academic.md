<!--
VIGIA Academic Documentation
Module: 6725056c
Batch ID: vigia-doc-0171-6725056c
Generated: 2026-05-20T14:56:47.881613+00:00
-->

# Module Documentation: `vigia/tools/signal_adapter.py`

## ENGLISH

### What Is This Module?
This module is a **protocol translator**—a deterministic rosetta stone—between two incompatible forensic subsystems. The legacy **ForensicEngine** generates heterogeneous diagnostic records (dictionaries with tool-specific keys such as `sda_nr`, `cli`, `acp`, `roi`). The modern **LikelihoodEngine** requires a single, uniform signal format called `SignalOutput`.

Rather than altering the proven, court-tested ForensicEngine, this adapter extracts the scientifically relevant measurements—**signals**—from each legacy record and re-packages them into standardized, immutable containers. It validates the structure of every incoming record before processing, ensuring that no malformed data propagate downstream. Every transformation is deterministic: scores are treated as exact rational numbers derived from integer arithmetic against a versioned, immutable **BaselineProfile**.

### Key Concepts

| Concept | Plain-Language Definition | Role in the System |
|---|---|---|
| **Legacy Forensic Verdict** | A raw diagnostic record produced by the existing analysis engine. It contains tool-specific sections (SDA, CLI, ACP, ROI) with heterogeneous metrics. | Source data; the input to the adapter. |
| **SignalOutput** | A standardized, tamper-evident envelope that carries one extracted measurement, its baseline provenance, and normalization metadata. | Universal currency consumed by the LikelihoodEngine. |
| **BaselineProfile** | A versioned, immutable reference distribution derived from the AUTHENTIC bootstrap corpus. It stores deterministic rational benchmarks (mean and dispersion) for each tool. | Provides Daubert-grade traceability; prevents silent statistical drift. |
| **Adapter Pattern** | A bridge between two incompatible interfaces that leaves both endpoints untouched. | Allows legacy and modern engines to coexist without forking the codebase. |
| **Schema Validation** | A deterministic structural audit that verifies the presence of all mandatory keys (`_REQUIRED_TOP_KEYS`, `_REQUIRED_CAPAS_KEYS`) before extraction. | Raises `ForensicVerdictSchemaError` if the record is incomplete, halting the pipeline to prevent invalid inference. |
| **Z-Score (Deterministic)** | An exact rational index of deviation: the integer-scaled distance between an observation and the baseline mean, divided by the baseline dispersion (e.g., MAD). Expressed as a reproducible ratio, not an approximate decimal. | Enables cross-tool comparison on a common, integer-derived scale. |
| **Pre-normalized Flag** | A boolean indicator stored in `SignalOutput`. `True` means the metric is already a z-score against its institutional baseline; `False` means it is a raw composite or proportion requiring further scaling. | Tells the LikelihoodEngine which signals need additional deterministic normalization. |
| **Immutable Artifact** | An object whose state is fixed at construction. Its SHA-256 fingerprint is computed once from an integer bitstring representation and cached forever. | Provides tamper-evident audit trails and reproducible hashing. |

### Glossary

- **ForensicEngine**: The existing adversarial-NLP subsystem that generates heterogeneous verdict dictionaries.
- **LikelihoodEngine**: The downstream probabilistic subsystem that consumes only uniform `SignalOutput` objects.
- **Signal**: A forensic index extracted from a verdict—for example, a cognitive stress index or an attack confidence proportion.
- **Bootstrap Baseline (AUTHENTIC)**: A reference corpus of verified genuine documents used to calibrate all deviation metrics deterministically.
- **Daubert Traceability**: The legal-scientific standard requiring that every computational step, baseline version, and transformation be documented, versioned, and reproducible.
- **ForensicVerdictSchemaError**: A deterministic exception raised when an input record lacks the required structural keys, preventing garbage-in-garbage-out processing.
- **Mean / MAD**: The baseline center (mean) and mean absolute dispersion (MAD), stored as rational numbers derived from integer population counts.
- **SHA-256**: A deterministic cryptographic digest algorithm that produces a fixed-length integer hash from any input bitstring, used here to fingerprint baseline profiles.

### 【Scientific Note】
References to **Peirce** (semiotic indices), **Eco** (coding and interpretative frames), and **Grice** (pragmatic implicature and cooperative maxims) appear throughout the broader VIGIA framework. These constructs are **not mysticism**. They operate exactly like physical sensors: a Peircean *index* transduces a stylistic anomaly into a deterministic deviation reading, just as a thermocouple transduces heat into voltage; an Eco coding frame categorizes textual features into discrete states, just as a spectrometer maps wavelengths to intensity bins; and Gricean thresholds generate deterministic cut-offs for cooperative discourse, just as a pressure sensor emits a calibrated digital signal when a threshold is crossed. This adapter performs an analogous transduction: it converts heterogeneous semiotic outputs into a uniform, deterministic measurement space without introducing logical fractures.

---

## ESPAÑOL

### ¿Qué es este módulo?
Este módulo es un **traductor de protocolos** —una piedra roseta determinística— entre dos subsistemas forenses incompatibles. El **ForensicEngine** heredado genera registros diagnósticos heterogéneos (diccionarios con claves propias de cada herramienta: `sda_nr`, `cli`, `acp`, `roi`). El **LikelihoodEngine** moderno requiere un formato de señal único y uniforme llamado `SignalOutput`.

En lugar de modificar el ForensicEngine probado y validado para tribunales, este adaptador extrae las mediciones científicamente relevantes —**señales**— de cada registro heredado y las reempaqueta en contenedores estandarizados e inmutables. Valida la estructura de cada registro entrante antes de procesarlo, garantizando que no se propaguen datos malformados río abajo. Cada transformación es determinística: las puntuaciones se tratan como números racionales exactos derivados de aritmética entera contra un **BaselineProfile** versionado e inmutable.

### Conceptos Clave

| Concepto | Definición en lenguaje sencillo | Rol en el sistema |
|---|---|---|
| **Veredicto Forense Heredado** | Registro diagnóstico crudo producido por el motor de análisis existente. Contiene secciones propias de cada herramienta (SDA, CLI, ACP, ROI) con métricas heterogéneas. | Datos fuente; entrada del adaptador. |
| **SignalOutput** | Sobre estandarizado e inmutable que transporta una medición extraída, su procedencia de línea base y sus metadatos de normalización. | Moneda universal consumida por el LikelihoodEngine. |
| **BaselineProfile** | Distribución de referencia versionada e inmutable derivada del corpus bootstrap AUTHENTIC. Almacena puntos de referencia racionales deterministas (media y dispersión) para cada herramienta. | Garantiza trazabilidad grado-Daubert; previene la deriva estadística silenciosa. |
| **Patrón Adaptador** | Puente entre dos interfaces incompatibles que no altera ninguno de los extremos. | Permite que los motores heredado y moderno coexistan sin bifurcar el código base. |
| **Validación de Esquema** | Auditoría estructural determinística que verifica la presencia de todas las claves obligatorias (`_REQUIRED_TOP_KEYS`, `_REQUIRED_CAPAS_KEYS`) antes de la extracción. | Lanza `ForensicVerdictSchemaError` si el registro está incompleto, deteniendo la tubería para evitar inferencias inválidas. |
| **Z-Score (Determinístico)** | Índice racional exacto de desviación: la distancia escalada en enteros entre una observación y la media de línea base, dividida por la dispersión de línea base (p. ej., MAD). Expresado como una proporción reproducible, no como un decimal aproximado. | Permite la comparación entre herramientas en una escala común derivada de enteros. |
| **Bandera Pre-normalizada** | Indicador booleano almacenado en `SignalOutput`. `True` significa que la métrica ya es un z-score contra su línea base institucional; `False` indica que es una métrica cruda o proporción que requiere escalamiento adicional. | Indica al LikelihoodEngine qué señales necesitan normalización determinística adicional. |
| **Artefacto Inmutable** | Objeto cuyo estado se fija en la construcción. Su huella SHA-256 se computa una sola vez a partir de una representación entera en bits y se almacena en caché para siempre. | Proporciona rutas de auditoría resistentes a la manipulación y hash reproducible. |

### Glosario

- **ForensicEngine**: Subsistema existente de NLP adversarial que genera diccionarios de veredictos heterogéneos.
- **LikelihoodEngine**: Subsistema probabilístico descendiente que consume únicamente objetos `SignalOutput` uniformes.
- **Señal**: Índice forense extraído de un veredicto —por ejemplo, un índice de estrés cognitivo o una proporción de confianza de ataque.
- **Línea base Bootstrap (AUTHENTIC)**: Corpus de referencia de documentos genuinos verificados utilizado para calibrar todas las métricas de desviación de manera determinística.
- **Trazabilidad Daubert**: Estándar científico-legal que exige que cada paso computacional, versión de línea base y transformación esté documentado, versionado y sea reproducible.
- **ForensicVerdictSchemaError**: Excepción determinística lanzada cuando un registro de entrada carece de las claves estructurales requeridas, evitando el procesamiento de datos inválidos.
- **Media / MAD**: Centro de la línea base (media) y dispersión absoluta media (MAD), almacenados como números racionales derivados de recuentos enteros de población.
- **SHA-256**: Algoritmo determinístico de digesto criptográfico que produce un hash entero de longitud fija a partir de cualquier cadena de bits, usado aquí para identificar perfiles de línea base.

### 【Nota Científica】
Las referencias a **Peirce** (índices semióticos), **Eco** (marcos de codificación e interpretación) y **Grice** (implicatura pragmática y máximas cooperativas) aparecen a lo largo del marco general VIGIA. Estos constructos **no son misticismo**. Operan exactamente como sensores físicos: un *índice* peirceano transduce una anomalía estilística en una lectura determinística de desviación, igual que un termopar transduce el calor en voltaje; un marco de codificación ecoliano categoriza rasgos textuales en estados discretos, igual que un espectrógrafo mapea longitudes de onda a intervalos de intensidad; y los umbrales griceanos generan cortes determinísticos para el discurso cooperativo, igual que un sensor de presión emite una señal digital calibrada al cruzar un umbral. Este adaptador realiza una transducción análoga: convierte salidas semióticas heterogéneas en un espacio de medición uniforme y determinista sin introducir fracturas lógicas.

---

## РУССКИЙ

### Что представляет собой этот модуль?
Этот модуль — **протокольный транслятор**, детерминистический «розеттский камень» между двумя несовместимыми судебно-экспертными подсистемами. Унаследованный **ForensicEngine** генерирует гетерогенные диагностические записи (словари с ключами, специфичными для каждого инструмента: `sda_nr`, `cli`, `acp`, `roi`). Современный **LikelihoodEngine** требует единого унифицированного формата сигналов под названием `SignalOutput`.

Вместо изменения проверенного и допущенного судом ForensicEngine данный адаптер извлекает научно значимые измерения — **сигналы** — из каждой унаследованной записи и переупаковывает их в стандартизированные неизменяемые контейнеры. Он проверяет структуру каждой входной записи перед обработкой, гарантируя отсутствие распространения искажённых данных вниз по потоку. Каждое преобразование детерминистично: оценки трактуются как точные рациональные числа, полученные в результате целочисленной арифметики относительно версионированного неизменяемого **BaselineProfile**.

### Ключевые концепции

| Концепция | Определение простым языком | Роль в системе |
|---|---|---|
| **Унаследованное судебное заключение (Forensic Verdict)** | Сырая диагностическая запись, производимая существующим аналитическим движком. Содержит разделы, специфичные для инструментов (SDA, CLI, ACP, ROI), с гетерогенными метриками. | Исходные данные; вход адаптера. |
| **SignalOutput** | Стандартизированный неизменяемый конверт, содержащий одно извлечённое измерение, сведения о базовой линии и метаданные нормализации. | Универсальная валюта, потребляемая LikelihoodEngine. |
| **BaselineProfile** | Версионированное неизменяемое опорное распределение, выведенное из корпуса AUTHENTIC bootstrap. Хранит детерминистические рациональные ориентиры (среднее и рассеяние) для каждого инструмента. | Гарантирует прослеживаемость стандарта Daubert; предотвращает скрытый статистический дрейф. |
| **Паттерн Адаптер** | Мост между двумя несовместимыми интерфейсами, не затрагивающий ни одну из сторон. | Позволяет унаследованному и современному движкам сосуществовать без разветвления кодовой базы. |
| **Валидация схемы** | Детерминистическая структурная проверка наличия всех обязательных ключей (`_REQUIRED_TOP_KEYS`, `_REQUIRED_CAPAS_KEYS`) перед извлечением. | Выбрасывает `ForensicVerdictSchemaError`, если запись неполна, останавливая конвейер для предотвращения недопустимых выводов. |
| **Z-балл (детерминистический)** | Точный рациональный индекс отклонения: целочисленно масштабированное расстояние между наблюдением и средним базовой линии, делённое на рассеяние базовой линии (например, MAD). Выражается как воспроизводимое отношение, а не приближённое десятичное число. | Обеспечивает межинструментальное сравнение в единой шкале, выведенной из целых чисел. |
| **Флаг предварительной нормализации** | Булев индикатор, хранимый в `SignalOutput`. `True` означает, что метрика уже является z-баллом относительно своей институциональной базовой линии; `False` означает сырые или составные единицы, требующие дальнейшего масштабирования. | Сообщает LikelihoodEngine, какие сигналы нуждаются в дополнительной детерминистической нормализации. |
| **Неизменяемый артефакт** | Объект, состояние которого фиксируется при создании. Его криптографический отпечаток SHA-256 вычисляется один раз на основе целочисленного битового представления и кэшируется навсегда. | Обеспечивает защищённые от подделки аудиторские следы и воспроизводимое хеширование. |

### Глоссарий

- **ForensicEngine**: Существующая подсистема состязательного NLP, генерирующая гетерогенные словари судебных заключений.
- **LikelihoodEngine**: Нисходящая вероятностная подсистема, потребляющая только унифицированные объекты `SignalOutput`.
- **Сигнал**: Судебно-экспертный индекс, извлечённый из заключения — например, индекс когнитивного стресса или доля уверенности в атаке.
- **Базовая линия Bootstrap (AUTHENTIC)**: Референсный корпус проверенных подлинных документов, используемый для детерминистической калибровки всех метрик отклонения.
- **Прослеживаемость Daubert**: Научно-правовой стандарт, требующий документирования, версионирования и воспроизводимости каждого вычислительного шага, версии базовой линии и преобразования.
- **ForensicVerdictSchemaError**: Детерминистическое исключение, возникающее при отсутствии в входной записи обязательных структурных ключей, предотвращающее обработку мусорных данных.
- **Среднее / MAD**: Центр базовой линии (среднее) и среднее абсолютное отклонение (MAD), хранимые как рациональные числа, выведенные из целочисленных совокупностей.
- **SHA-256**: Детерминистический криптографический алгоритм хеширования, вырабатывающий хеш фиксированной длины из любой битовой строки; здесь используется для идентификации профилей базовой линии.

### 【Научное примечание】
Ссылки на **Пирса** (семиотические индексы), **Эко** (кодировочные и интерпретационные рамки) и **Грайса** (прагматическая импликатура и кооперативные максимы) встречаются в обширной рамке VIGIA. Эти конструкты — **не мистицизм**. Они работают точно так же, как физические датчики: пирсовский *индекс* трансдуцирует стилистическую аномалию в детерминистическое отклонение, точно так же, как термопара трансдуцирует тепло в напряжение; эковская кодировочная рама категоризирует текстовые признаки в дискретные состояния, точно так же, как спектрограф отображает длины волн на интервалы интенсивности; а грайсовские пороги генерируют детерминистические отсечки для кооперативного дискурса, точно так же, как датчик давления выдаёт калиброванный цифровой сигнал при пересечении порога. Этот адаптер выполняет аналогичную трансдукцию: он преобразует гетерогенные семиотические выходы в единое детерминистическое пространство измерений, не внося логических разрывов.

---

## 中文

### 本模块是什么？
本模块是一个**协议转换器**——一种确定性的"罗塞塔石碑"，用于连接两个互不兼容的取证子系统。遗留的 **ForensicEngine** 会生成异构的诊断记录（即包含各工具专属键的字典，如 `sda_nr`、`cli`、`acp`、`roi`）。而现代的 **LikelihoodEngine** 仅接受一种名为 `SignalOutput` 的标准化统一信号格式。

本适配器不修改已经过验证、可用于法庭的 ForensicEngine，而是从每条遗留记录中提取具有科学意义的测量值——即**信号**——并将其重新封装到标准化且不可变的容器中。它在处理前会验证每条输入记录的结构，确保畸形数据不会向下游传播。所有变换都是确定性的：各项评分均被视作针对版本化且不可变的 **BaselineProfile** 进行整数运算后得到的精确有理数。

### 核心概念

| 概念 | 通俗定义 | 在系统中的作用 |
|---|---|---|
| **遗留取证裁决 (Legacy Forensic Verdict)** | 由现有分析引擎生成的原始诊断记录。包含各工具专属的分区（SDA、CLI、ACP、ROI），其度量指标呈异构形态。 | 源数据；适配器的输入。 |
| **SignalOutput** | 一种标准化、不可变的封装容器，承载一项提取后的测量值、其基线来源以及归一化元数据。 | LikelihoodEngine 所消费的通用"货币"。 |
| **BaselineProfile** | 从 AUTHENTIC 引导（bootstrap）语料库中导出的、带版本号且不可变的参考分布。为每种工具存储确定性的有理数基准（均值与离散度）。 | 提供达到道伯特（Daubert）标准的可追溯性；防止静默统计漂移。 |
| **适配器模式 (Adapter Pattern)** | 在不动任何一端的前提下，为两种不兼容接口搭建的桥梁。 | 使遗留引擎与现代引擎得以共存，而无需分叉代码库。 |
| **模式校验 (Schema Validation)** | 一种确定性结构审计，在提取前验证所有必填键（`_REQUIRED_TOP_KEYS`、`_REQUIRED_CAPAS_KEYS`）是否齐全。 | 若记录结构不完整，则抛出 `ForensicVerdictSchemaError`，终止流水线以防止无效推理。 |
| **确定性 Z 分数** | 精确的偏离度有理数指标：观测值与基线均值之间的整数级距离，除以基线离散度（如 MAD）。以可重现比值表示，而非近似小数。 | 在源自整数的公共尺度上实现跨工具比较。 |
| **预归一化标志** | 存储于 `SignalOutput` 中的布尔指标。`True` 表示该指标已是针对其机构基线的 Z 分数；`False` 表示原始复合值或比例，需进一步缩放。 | 告知 LikelihoodEngine 哪些信号需要额外的确定性归一化。 |
| **不可变取证工件** | 构建后状态固定的对象。其 SHA-256 指纹从整数位串表示中一次性计算得出并永久缓存。 | 提供防篡改的审计追踪和可重现的哈希值。 |

### 术语表

- **ForensicEngine**：现有的对抗性 NLP 子系统，生成异构的裁决字典。
- **LikelihoodEngine**：下游概率子系统，仅消费统一的 `SignalOutput` 对象。
- **信号**：从裁决中提取的取证指标——例如认知压力指数或攻击置信比例。
- **引导基线 (AUTHENTIC)**：经验证的真实文档参考语料库，用于确定性校准所有偏差指标。
- **道伯特可追溯性**：法律科学标准，要求每个计算步骤、基线版本和变换均经过记录、版本化并可重现。
- **ForensicVerdictSchemaError**：当输入记录缺少所需结构键时触发的确定性异常，防止无效数据处理。
- **均值 / MAD**：基线中心（均值）和平均绝对离散度（MAD），以源自整数总体计数的有理数存储。
- **SHA-256**：确定性密码哈希算法，从任意输入位串生成固定长度整数哈希，此处用于对基线档案进行指纹识别。

### 【科学说明】
**皮尔斯**（符号学指标）、**艾柯**（编码与解释框架）及**格赖斯**（语用含意与合作准则）的引用贯穿整个 VIGIA 框架。这些构念**并非神秘主义**。它们与物理传感器的工作方式完全相同：皮尔斯式*指标*将文体异常转换为确定性偏差读数，正如热电偶将热量转换为电压；艾柯编码框架将文本特征分类为离散状态，正如光谱仪将波长映射到强度区间；格赖斯阈值为合作话语生成确定性截止值，正如压力传感器在超过阈值时发出校准数字信号。本适配器执行类似的转换：它将异构的符号学输出转换为统一的确定性测量空间，而不引入逻辑断裂。

---

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
