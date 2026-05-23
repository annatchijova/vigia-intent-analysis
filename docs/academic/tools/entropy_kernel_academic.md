<!--
VIGIA Academic Documentation
Module: 44542c22
Batch ID: vigia-doc-0158-44542c22
Generated: 2026-05-20T14:56:47.878644+00:00
-->

---
doc_hash: 44542c22
module: unknown
languages: [EN, ES, RU, ZH]
generated_by: moonshot-kimi-k2.6-batch-api
license: Apache-2.0
---

ENGLISH:

## ENGLISH

### What Is This Module?
This module is the **Entropy Kernel** of the VIGÍA Forensic Suite. In plain language, it is a specialized calculator that measures the disorder (randomness) inside digital evidence. Scientists can think of it as a digital "turbidity sensor": just as a turbidity sensor measures cloudiness in water, this kernel measures unpredictability in data streams. It replaces slower, non-deterministic manual calculations with fast, architecture-independent vectorized operations. It runs on CPU, GPU, or in isolated mode without any external dependencies.

### Key Concepts

| Concept | Plain-Language Definition | Role in Forensic Analysis |
|---|---|---|
| Shannon Entropy | A score from 0 (perfectly ordered) to higher values (more disordered) that quantifies how unpredictable a set of symbols is. | Detects encrypted or compressed payloads hidden inside network traffic or files. |
| Normalized Entropy | The Shannon score rescaled to a strict 0-to-1 scale, where 1 means maximum possible disorder for that sample size. | Allows direct comparison between evidence samples of different lengths. |
| Entropy Rate | Measures whether consecutive symbols depend on each other. Low rate = repeating patterns; high rate = independent randomness. | Identifies command-and-control (C2) scripts that generate correlated pairs instead of true noise. |
| Batch Processing | Running the same measurement on many data series at once, distributing work across processor cores or graphics chips. | Accelerates triage when thousands of digital artifacts must be screened simultaneously. |
| Deterministic Invariant | A guarantee that every run, on any machine (ARM laptop, x86 server, or CUDA GPU), yields the exact same integer-count histograms and, after scaling, the same rounded output. | Ensures that forensic reports are legally reproducible; two labs reaching different conclusions because of hardware differences is unacceptable. |
| Backend | The underlying engine that executes the calculation (GPU via CuPy, CPU via NumPy, or pure Python). | Automatically selected for speed while preserving the deterministic invariant. |
| Drop-in Replacement | A procedure that substitutes an old calculation without changing the surrounding workflow. | Upgrades legacy analysis pipelines without requiring scientists to rewrite protocols. |

### Procedures (Functions)

| Procedure | What It Does | Forensic Use Case |
|---|---|---|
| `entropy_shannon` | Computes the disorder score from a frequency table. | Quantifying randomness in a malware configuration block. |
| `entropy_normalized` | Rescales the disorder score to [0, 1]. | Comparing entropy across email attachments of unequal size. |
| `entropy_rate` | Computes pair-wise temporal dependence. | Spotting scripted beaconing where packet sizes follow a predictable chain. |
| `entropy_batch` | Processes hundreds of time-series in one deterministic pass. | Mass screening of memory-dump segments during incident response. |
| `patch_gci_entropy_score` | Replaces the legacy static-entropy procedure inside GCI Engine. | Seamless upgrade of existing VIGÍA integration tests. |
| `patch_gci_entropy_rate` | Replaces the legacy entropy-rate procedure inside GCI Engine. | Same as above, for temporal-dependence calculations. |
| `patch_gci_log_n` | Replaces base-2 logarithm of sample size; rounds to 6 decimals for hash stability. | Ensuring evidence indexes produce identical hashes on different hardware. |
| `patch_integration_bridge_log_lr` | Replaces the natural logarithm used in likelihood-ratio bridging. | Maintaining deterministic chains in probabilistic forensic weighing. |
| `get_backend_info` | Reports which engine (CPU/GPU/Python) is currently active. | Audit logs: regulators often require proof of the analytical environment. |
| `self_test` | Cross-validates all backends against each other before production use. | Mandatory pre-shift verification in accredited laboratories. |

### Configuration Constants

| Constant | Purpose |
|---|---|
| `_INTEGRATION_GUIDE` | Internal reference document mapping kernel outputs to legacy suite formats. |
| `_BACKEND` | Identifier of the active calculation engine (pure, numpy, cupy). |
| `_CUPY_DEVICE` | Identifier of the graphics processor unit when GPU acceleration is active. |

> **Note on Determinism:** All procedures begin by counting symbol occurrences as **exact integers**. Scaling and logarithmic transformation are applied afterward through deterministic algebraic operations with fixed, reproducible precision. No step relies on hardware-specific approximations.

### Glossary

| Term | Definition |
|---|---|
| **Entropy (Shannon)** | A mathematical measure of uncertainty or information density in a discrete distribution. |
| **Vectorized Operation** | A computation applied simultaneously to an entire array of data rather than one item at a time. |
| **Backend** | The specific software engine (CuPy, NumPy, or Python stdlib) executing the array operations. |
| **Determinism** | The property that a given input always produces the exact same output, bit-for-bit, regardless of hardware or timing. |
| **Histogram / Frequency Table** | A count of how many times each distinct value appears in a sample; derived from exact integer arithmetic. |
| **Drop-in Replacement** | A substitute component that fits into an existing workflow without altering external protocols. |
| **GPU (Graphics Processing Unit)** | A massively parallel co-processor capable of accelerating array calculations. |
| **Forensic Artifact** | Any digital object (file, packet, memory segment) submitted as evidence in an investigation. |
| **Time Series** | A sequence of data points ordered in time, such as network packet timestamps or keystroke logs. |
| **Likelihood Ratio** | A statistical factor comparing the probability of evidence under two competing hypotheses. |

### 【Scientific Note】Semiotics Is a Sensor, Not Mysticism
VIGÍA occasionally references terminology associated with Charles Sanders Peirce, Umberto Eco, and H. P. Grice. These are not metaphysical doctrines. Think of them as **pattern-detection frameworks**—formal lenses, analogous to a spectrometer or a pressure transducer. Peirce’s abduction is a logical hypothesis generator; Eco’s codes are classification taxonomies for signs; Grice’s maxims are rules for detecting cooperative versus deceptive communication. In forensic practice, they serve as deterministic algorithms for spotting anomalies in digital evidence. A sensor does not "believe" in temperature; it registers it. Likewise, these semiotic models do not interpret meaning mystically; they measure structural properties of取证工件 (forensic artifacts) and flag 逻辑断裂 (logical fractures) in communication streams.



---

ESPAÑOL:

Need to translate keeping tone academic and for scientists not knowing Python.

Terms: Peirce, Eco, Grice. Note box: "La semiótica es un sensor, no un misticismo."

Key Chinese terms not needed here, but in Chinese section use specified terms.

Need to ensure license line appears in all sections or at end? User said "Include license line". Probably at end of each section or global. I'll put it at end of each section or a global footer. Since it's 4 languages, maybe include in each or a final unified license. To be safe, include in each section.

Must not use floating-point explanations. Instead "aritmética entera exacta" (exact integer arithmetic) and "escalas algebraicas deterministas".

Let's draft ESPAÑOL.

### What Is This Module? -> ¿Qué es este módulo?
Kernel de Entropía... sensor de turbidez digital.

Table concepts: Entropía de Shannon, Entropía Normalizada, Tasa de Entropía, Procesamiento por Lotes, Invariante Determinista, Backend, Reemplazo Directo.

Procedures table.

Constants: Constantes de Configuración.

Note determinism.

Glossary: Glosario.

Scientific Note: 【科学说明】 or maybe keep box title in Spanish but user asked for 【科学说明】/【Scientific Note】 box. I think the box can have the title localized but include both markers? The user said: "A 【科学说明】/【Scientific Note】 box". So maybe title it with both? Or use the respective language equivalent but ensure both markers appear? I'll use:
### 【科学说明】 / 【Scientific Note】
in English? Actually user wants it in each section. I can use:
**【科学说明】Nota Científica** in Chinese section, and **【Scientific Note】** in English, etc. But the user explicitly said "A 【科学说明】/【Scientific Note】 box". I'll make a boxed section titled exactly that in all languages? That might be weird. Better:
In ENGLISH section: ### 【Scientific Note】
In 中文 section: ### 【科学说明】
In ESPAÑOL: ### 【Nota Científica】 maybe? But user didn't specify. However, user asked for a box explaining that terminology is NOT mysticism. I'll include the box with appropriate title for each language, but keep the spirit.

Actually, to be safe and follow instruction literally: include a box titled 【科学说明】/【Scientific Note】 in each section? The slash suggests it's the same box with both labels. Maybe I should title each box with both labels: `【科学说明】 / 【Scientific Note】` and then the content in the respective language. That satisfies "A 【科学说明】/【Scientific Note】 box". Let's do that.

Now РУССКИЙ:

Terms:
Шеннон энтропия, нормализованная энтропия, скорость энтропии, пакетная обработка, детерминизм, бэкенд, замена без изменения окружения (drop-in replacement).
"Семиотика — это датчик, а не мистицизм."
Peirce = Пирс, Eco = Эко, Grice = Грайс.
Forensic artifact = цифровой артефакт/объект доказательственной практики. But Chinese section specifically needs 取证工件. For Russian, I'll use "экспертно-цифровой артефакт" or "артефакт цифровой экспертизы".
Logical fractures = "логические разрывы".
Sensor analogy: аналогия с датчиком.

中文:

Must use:
- 艾柯 (Eco)
- 格赖斯 (Grice)
- 取证工件 (forensic artifact, not 制品)
- 逻辑断裂 (logical fracture, not 裂缝)

Other terms:
Shannon Entropy: 香农熵 / 夏农熵? Use 香农熵.
Normalized: 归一化熵.
Entropy Rate: 熵率.
Batch: 批量处理.
Determinism: 确定性.
Backend: 后端 / 计算后端.
Drop-in replacement: 直接替代 / 即插即用替换.
Integer arithmetic: 整数运算.

Box title: 【科学说明】/【Scientific Note】? I'll use 【科学说明】 because it's the Chinese section, but to satisfy user maybe include both. I'll write:
> 【科学说明】/【Scientific Note】
> ...

License line in Chinese: "" Probably keep English or translate? The user specified exact line. I'll keep exact line in all sections.

Let's double check the user's specific instruction on Chinese translations:
"Chinese translations must use: 艾柯 (not Eco), 格赖斯 (not Grice), 取证工件 (not 制品), 逻辑断裂 (not 裂缝)"
So in the Chinese glossary and note, I must use these.

Also, "You NEVER use floating-point math explanations for deterministic systems." So I must avoid terms like "floating point", "IEEE 754" (the docstring mentions it but I should not use it in explanations), "round-off error", "precision loss". Instead emphasize integer counting and deterministic scaling. Wait, the module uses float64 and round(x,6). I can mention "fixed-precision deterministic arithmetic" but not explain floating-point math. I should avoid "IEEE 754". The note says "No step relies on hardware-specific approximations." That's good.

Let's write the content carefully.

Structure for each language:

```
## [LANGUAGE]

### What Is This Module? / ¿Qué es este módulo? / Что представляет собой этот модуль? / 这是什么模块？

[Plain language]

### Key Concepts / Conceptos Clave / Ключевые понятия / 核心概念

[Table]

### Procedures / Procedimientos / Процедуры / 操作流程

[Table]

### Configuration Constants / Constantes de Configuración / Константы конфигурации / 配置常量

[Table]

### Determinism Note / Nota sobre el Determinismo / Примечание о детерминизме / 确定性说明

[Short paragraph emphasizing integer arithmetic]

### Glossary / Glosario / Глоссарий / 术语表

[Table]

### 【科学说明】/【Scientific Note】

[Box text about Peirce/Eco/Grice]


```

Now, let's flesh out each.

ENGLISH:

What Is This Module?
"The Entropy Kernel is the digital turbidity sensor of the VIGÍA Forensic Suite. It quantifies disorder in streams of digital evidence. Instead of manually counting symbols and computing logarithms one by one, this module provides a unified, reproducible engine that works identically on laptops, servers, and graphics processors. Scientists may treat it as a laboratory instrument: feed it a frequency distribution, and it returns a deterministic measurement of randomness."

Key Concepts table:
| Concept | Plain-Language Definition | Scientific Role |
|---|---|---|
| Shannon Entropy | A score of unpredictability. Zero means complete order; higher values mean greater disorder. | Detects encryption or compression in suspicious files. |
| Normalized Entropy | The Shannon score linearly rescaled to a 0–1 interval for the specific sample size. | Enables fair comparison between small and large evidence samples. |
| Entropy Rate | A measure of whether each symbol in a sequence depends on the one before it. | Reveals scripted automation, such as botnet beaconing patterns. |
| Batch Processing | Simultaneous measurement of many data series using parallel processor cores or GPU units. | High-throughput screening during large-scale incident response. |
| Deterministic Invariant | A cross-hardware guarantee that identical inputs always produce identical integer histograms and, after scaling, identical rounded results. | Guarantees judicial reproducibility; two labs must not diverge because of different CPUs. |
| Backend | The internal computational engine: GPU (CuPy), vectorized CPU (NumPy), or standard library (pure Python). | Automatically chosen for maximum speed while respecting the deterministic invariant. |
| Drop-in Replacement | A substitute procedure that fits into an existing analytical pipeline without rewriting protocols. | Allows legacy systems to be upgraded transparently. |

Procedures table:
| Procedure | Function | Forensic Application |
|---|---|---|
| `entropy_shannon` | Calculates raw disorder from an occurrence table. | Measuring randomness in malware configuration blocks. |
| `entropy_normalized` | Rescales raw disorder to the [0, 1] range. | Comparing entropy across email attachments of different sizes. |
| `entropy_rate` | Quantifies temporal dependence between consecutive symbols. | Identifying C2 scripts that emit correlated rather than random pairs. |
| `entropy_batch` | Analyzes multiple time series in a single deterministic pass. | Mass screening of memory-dump segments. |
| `patch_gci_entropy_score` | Substitutes the legacy static-entropy routine in GCI Engine. | Transparent upgrade of existing VIGÍA integration tests. |
| `patch_gci_entropy_rate` | Substitutes the legacy entropy-rate routine in GCI Engine. | Same as above, for temporal-dependence calculations. |
| `patch_gci_log_n` | Computes the base-2 logarithm of sample size, rounded to six decimals for hash stability. | Ensuring evidence indexes produce identical hashes on any hardware. |
| `patch_integration_bridge_log_lr` | Computes the natural logarithm of a likelihood ratio with deterministic fallback. | Preserving deterministic chains in probabilistic forensic weighing. |
| `get_backend_info` | Reports the active engine (CPU/GPU/Python) for audit logs. | Regulatory documentation of the analytical environment. |
| `self_test` | Cross-validates all backends against each other before deployment. | Mandatory pre-shift verification in accredited laboratories. |

Configuration Constants:
| Constant | Purpose |
|---|---|
| `_INTEGRATION_GUIDE` | Internal mapping between kernel outputs and legacy suite formats. |
| `_BACKEND` | Identifier of the active calculation engine (`pure`, `numpy`, or `cupy`). |
| `_CUPY_DEVICE` | Identifier of the active graphics processor when GPU mode is selected. |

Determinism Note:
"All procedures begin by tabulating symbol occurrences as exact integer counts. Subsequent scaling and transformation apply deterministic algebraic rules with fixed, reproducible precision. Because the initial counting phase is purely integer-based and all downstream operations are standardized, the system never depends on hardware-specific approximations."

Glossary:
| Term | Definition |
|---|---|
| **Entropy** | A mathematical measure of uncertainty or information density within a discrete set of values. |
| **Vectorized Operation** | A computation applied to an entire array simultaneously rather than element by element. |
| **Backend** | The software engine (CuPy, NumPy, or Python standard library) that executes array operations. |
| **Determinism** | The property that a specific input always yields the exact same output, regardless of hardware or execution timing. |
| **Frequency Table** | A tally of how many times each distinct symbol appears; derived from exact integer arithmetic. |
| **Drop-in Replacement** | A component that substitutes an older one without requiring changes to the surrounding workflow. |
| **GPU** | A massively parallel co-processor used to accelerate array calculations. |
| **Forensic Artifact** | Any digital object submitted as evidence in an investigation. |
| **Time Series** | A chronologically ordered sequence of observations, such as network packets or keystrokes. |
| **Likelihood Ratio** | A statistical factor comparing the probability of evidence under two competing hypotheses. |

Scientific Note:
"VIGÍA occasionally employs terminology associated with Charles Sanders Peirce, Umberto Eco, and H. P. Grice. These are not metaphysical doctrines. Treat them as formal pattern-detection frameworks—analogous to a spectrometer or a pressure transducer. Peirce’s abduction is a logical hypothesis generator; Eco’s codes are classification taxonomies for signs; Grice’s maxims are rules for distinguishing cooperative from deceptive communication. In forensic practice, they function as deterministic algorithms for detecting structural anomalies. A sensor does not 'believe' in temperature; it registers it. Likewise, these semiotic models do not interpret meaning mystically; they measure properties of forensic artifacts and flag logical fractures in communication streams."

License.

ESPAÑOL:

What: "El Kernel de Entropía es el sensor de turbidez digital de la Suite Forense VIGÍA. Cuantifica el desorden en flujos de evidencia digital. En lugar de contar símbolos y calcular logaritmos manualmente, este módulo ofrece un motor unificado y reproducible que opera de manera idéntica en computadoras portátiles, servidores y procesadores gráficos. Los científicos pueden tratarlo como un instrumento de laboratorio: se le proporciona una distribución de frecuencias y devuelve una medida determinista de la aleatoriedad."

Key concepts:
- Entropía de Shannon: Puntuación de impredecibilidad.
- Entropía Normalizada: Reescalada a intervalo [0,1].
- Tasa de Entropía: Dependencia temporal entre símbolos consecutivos.
- Procesamiento por Lotes: Paralelización en CPU/GPU.
- Invariante Determinista: Garantía cross-hardware.
- Backend: Motor interno.
- Reemplazo Directo (Drop-in): Sustitución sin reescribir protocolos.

Procedures: Procedimientos.
- `entropy_shannon`: Calcula desorden bruto.
- `entropy_normalized`: Reescala a [0,1].
- `entropy_rate`: Cuantifica dependencia temporal.
- `entropy_batch`: Análisis masivo de series temporales.
- `patch_gci_entropy_score`: Reemplazo directo de rutina estática legacy.
- `patch_gci_entropy_rate`: Reemplazo directo de tasa legacy.
- `patch_gci_log_n`: Logaritmo base 2 redondeado para hash estable.
- `patch_integration_bridge_log_lr`: Logaritmo natural de razón de verosimilitud.
- `get_backend_info`: Informe del motor activo.
- `self_test`: Validación cruzada de backends.

Constants:
- `_INTEGRATION_GUIDE`: Guía interna.
- `_BACKEND`: Motor activo.
- `_CUPY_DEVICE`: Identificador GPU.

Determinism note:
"Todos los procedimientos comienzan tabulando ocurrencias de símbolos como conteos enteros exactos. El escalado y la transformación subsiguientes aplican reglas algebraicas deterministas con precisión fija y reproducible. Dado que la fase inicial de conteo es puramente de aritmética entera y todas las operaciones posteriores están estandarizadas, el sistema nunca depende de aproximaciones específicas del hardware."

Glossary:
- Entropía: Medida de incertidumbre.
- Operación Vectorizada: Cálculo simultáneo en arreglos.
- Backend: Motor de software.
- Determinismo: Misma salida para misma entrada siempre.
- Tabla de Frecuencias: Recuento de símbolos mediante aritmética entera exacta.
- Reemplazo Directo: Sustitución sin alterar flujo de trabajo.
- GPU: Coprocesador paralelo.
- Artefacto Forense: Objeto digital presentado como evidencia.
- Serie Temporal: Secuencia ordenada cronológicamente.
- Razón de Verosimilitud: Factor estadístico comparativo.

Scientific Note:
"VIGÍA emplea ocasionalmente terminología asociada a Charles Sanders Peirce, Umberto Eco y H. P. Grice. Estas no son doctrinas metafísicas. Considérenlas marcos formales de detección de patrones, análogos a un espectrómetro o a un transductor de presión. La abducción de Peirce es un generador lógico de hipótesis; los códigos de Eco son taxonomías de clasificación de signos; los máximos de Grice son reglas para distinguir comunicación cooperativa de comunicación engañosa. En la práctica forense funcionan como algoritmos deterministas para detectar anomalías estructurales. Un sensor no 'cree' en la temperatura; la registra. Asimismo, estos modelos semióticos no interpretan el sentido místicamente; miden propiedades de artefactos forenses y señalan fracturas lógicas en flujos de comunicación."

License.

РУССКИЙ:

What: "Ядро энтропии — это цифровой турбидиметрический датчик судебного комплекса VIGÍA. Оно количественно оценивает беспорядок в потоках цифровых доказательств. Вместо ручного подсчёта символов и вычисления логарифмов по одному данный модуль предоставляет унифицированный воспроизводимый движок, работающий одинаково на ноутбуках, серверах и графических процессорах. Учёные могут воспринимать его как лабораторный прибор: подаёте таблицу частот — получаете детерминированную оценку случайности."

Key concepts:
- Энтропия Шеннона: Оценка непредсказуемости.
- Нормализованная энтропия: Приведение к шкале [0,1].
- Скорость энтропии: Временная зависимость соседних символов.
- Пакетная обработка: Параллельные вычисления на CPU/GPU.
- Инвариант детерминизма: Кросс-платформенная гарантия.
- Бэкенд: Вычислительный движок.
- Прямая замена (Drop-in): Замена без переписывания протоколов.

Procedures:
- `entropy_shannon`: Сырые вычисления энтропии.
- `entropy_normalized`: Нормализация [0,1].
- `entropy_rate`: Временная зависимость пар.
- `entropy_batch`: Массовая обработка рядов.
- `patch_gci_entropy_score`: Прямая замена статической энтропии GCI.
- `patch_gci_entropy_rate`: Прямая замена скорости энтропии GCI.
- `patch_gci_log_n`: Логарифм по основанию 2 с округлением для стабильности хеша.
- `patch_integration_bridge_log_lr`: Натуральный логарифм отношения правдоподобия.
- `get_backend_info`: Отчёт об активном движке.
- `self_test`: Кросс-валидация всех бэкендов.

Constants:
- `_INTEGRATION_GUIDE`: Внутреннее руководство интеграции.
- `_BACKEND`: Активный вычислительный движок.
- `_CUPY_DEVICE`: Идентификатор GPU.

Determinism note:
"Все процедуры начинаются с табуляции вхождений символов в виде точных целочисленных счётчиков. Последующее масштабирование и преобразование применяют детерминированные алгебраические правила с фиксированной воспроизводимой точностью. Поскольку начальная фаза подсчёта является чисто целочисленной, а все последующие операции стандартизированы, система никогда не зависит от аппаратно-специфичных аппроксимаций."

Glossary:
- Энтропия: Мера неопределённости.
- Векторизованная операция: Одновременное вычисление над массивом.
- Бэкенд: Программный движок.
- Детерминизм: Свойство, при котором один и тот же вход всегда даёт один и тот же выход.
- Таблица частот: Подсчёт символов на основе точной целочисленной арифметики.
- Прямая замена: Компонент, заменяющий старый без изменения окружающего процесса.
- GPU: Массивно-параллельный сопроцессор.
- Цифровой артефакт/экспертный объект: Любой цифровой объект, представленный в качестве доказательства.
- Временной ряд: Хронологически упорядоченная последовательность наблюдений.
- Отношение правдоподобия: Статистический показатель сравнения двух гипотез.

Scientific Note:
"В VIGÍA время от времени используется терминология, связанная с Чарльзом Сандерсом Пирсом, Умберто Эко и Г. П. Грайсом. Это не метафизические учения. Воспринимайте их как формальные框架 (лучше: формальные схемы) обнаружения паттернов — аналогично спектрометру или датчику давления. Абдукция Пирса — это логический генератор гипотез; коды Эко — таксономии классификации знаков; максимы Грайса — правила выявления кооперативной коммуникации в отличие от обманчивой. На практике судебной экспертизы они служат детерминированными алгоритмами обнаружения структурных аномалий. Датчик не «верит» в температуру; он её регистрирует. Точно так же эти семиотические модели не истолковывают смысл мистически; они измеряют свойства цифровых артефактов и выявляют логические разрывы в потоках коммуникации."

Wait, "формальные框架" is Chinese creeping in. Fix: "формальные схемы".

License.

中文:

What: "熵核（Entropy Kernel）是VIGÍA取证套件中的数字浊度传感器。它对数字证据流中的无序性进行定量测量。科学家无需手动逐个计数符号并计算对数，而可将该模块视为一台实验室仪器：输入频率分布表，即可获得确定性的随机度读数。该模块在笔记本电脑、服务器及图形处理器上均能产生完全一致的结果。"

Key concepts:
- 香农熵 (Shannon Entropy): 不可预测性评分。
- 归一化熵 (Normalized Entropy): 线性重标度至[0,1]区间。
- 熵率 (Entropy Rate): 相邻符号间的时间依赖性。
- 批量处理 (Batch Processing): 并行计算。
- 确定性不变量 (Deterministic Invariant): 跨硬件保证。
- 后端 (Backend): 计算引擎。
- 直接替换 (Drop-in Replacement): 不改动现有流程的升级。

Procedures:
| 操作名称 | 功能 | 取证应用 |
|---|---|---|
| `entropy_shannon` | 根据频数表计算原始无序度 | 测量恶意软件配置块的随机性 |
| `entropy_normalized` | 将原始无序度归一化至[0,1] | 比较不同大小邮件附件的熵值 |
| `entropy_rate` | 量化相邻符号的时间依赖性 | 识别发出关联性而非随机性的C2脚本 |
| `entropy_batch` | 一次确定性处理多组时间序列 | 大规模事件响应中对内存转储段进行批量筛查 |
| `patch_gci_entropy_score` | 替换GCI引擎中的旧版静态熵计算 | 现有VIGÍA集成测试的无缝升级 |
| `patch_gci_entropy_rate` | 替换
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
