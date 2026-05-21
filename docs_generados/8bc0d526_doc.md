<!--
VIGIA Academic Documentation
Module: 8bc0d526
Batch ID: vigia-doc-0102-8bc0d526
Generated: 2026-05-20T14:56:47.866726+00:00
-->

The user wants academic technical documentation for a Python module `vigia/inference/metabolic_profiler.py` (though docstring says `vigia/engine/metabolic_profiler.py`). Target audience: scientists who don't know Python. Format: Markdown with 4 language sections: ENGLISH, ESPAÑOL, РУССКИЙ, 中文.

Requirements:
1. Target audience: scientists/researchers who do NOT know Python.
2. Format: Markdown with 4 language sections.
3. Each section must include:
   - "What Is This Module?" (plain language explanation)
   - Key concepts with tables
   - A glossary of technical terms
   - A 【科学说明】/【Scientific Note】 box explaining that Peirce/Eco/Grice terminology is NOT mysticism — use the sensor analogy.
4. Chinese translations must use: 艾柯 (not Eco), 格赖斯 (not Grice), 取证工件 (not 制品), 逻辑断裂 (not 裂缝).
5. 
6. Do NOT use floating-point math explanations — emphasize deterministic integer arithmetic where applicable.

Module details:
- Path: vigia/inference/metabolic_profiler.py
- Docstring: vigia/engine/metabolic_profiler.py
- Description: "Perfil metabólico del sistema: analiza el 'ritmo' de actividad del sistema para detectar desviaciones comportamentales."
- FIX P0: All numeric values in evidence dict use Fraction/str. NEVER float.
- FIX P0: All internal calculations use Fraction. Conversion to float only in SignalOutput constructor (inevitable by API).
- CLASSES:
  - MetabolicProfile
  - MetabolicAnalysisResult
  - MetabolicProfiler: Analyzes system metabolism: event frequency, activity/rest patterns, and behavior entropy.
- FUNCTIONS:
  - to_signal()
  - analyze(): Analyzes an event stream and builds metabolic profile.
    Args: event_stream: List of events with 'timestamp' (i... [cut off]
- CONSTANTS & CONFIG:
  - TOOL_NAME
  - ARTIFACT_RELIABILITY

Need to generate thorough but concise academic documentation. Since the user didn't provide full source code, I need to infer the structure from the description and the constraints. I should write documentation that explains the module in scientific terms, avoiding Python jargon where possible, or explaining it simply.

Important: The scientific note must explain that Peirce/Eco/Grice terminology is NOT mysticism — use the sensor analogy. This is a very specific request. I need to frame semiotics (Peirce, Eco, Grice) as analytical constructs similar to how a sensor detects physical phenomena. Since the module is about "metabolic profiler" and "behavioral deviations", the connection to semiotics might be about interpreting signs/system events. I need to incorporate this note carefully.

Also, deterministic integer arithmetic: emphasize that all internal evidence uses Python's `Fraction` class (exact rational arithmetic) and string representations, avoiding IEEE 754 floating-point approximations. Only at the final API boundary (SignalOutput) is a conversion to float unavoidable.

Chinese terms:
- 艾柯 (Umberto Eco)
- 格赖斯 (H.P. Grice)
- 取证工件 (forensic artifact, not 制品)
- 逻辑断裂 (logical fracture/break, not 裂缝)

License line must be included exactly.

Structure for each language section:
- Heading in that language.
- "What Is This Module?" subsection.
- Key Concepts with tables.
- Glossary.
- Scientific Note box.
- Maybe a section on Deterministic Arithmetic.
- License line at the end of each section or globally? The requirement says "Each section must include...". It lists specific subsections. It doesn't explicitly say license must be in each section, but requirement 5 says "License line: ...". Usually one license line at the end of document is fine, but to be safe, I can put it at the very end of the document. However, to ensure compliance, perhaps include it in each section or at least once prominently. Let's put it at the bottom of each language section to be safe, or as a footer. Actually, requirement 5 is global. I'll include it at the end of each section to be thorough.

Let's draft content.

ENGLISH:
- What Is This Module? MetabolicProfiler is a deterministic forensic analyzer that treats the computer system as an organism. It measures the "pulse" of events—how often things happen, when the system sleeps, and how predictable its behavior is. It detects anomalies (deviations) without using floating-point approximations internally.
- Key Concepts Table:
  | Term | Meaning | Role |
  |---|---|---|
  | Event Stream | Chronological sequence of system occurrences | Input data |
  | Metabolic Profile | Baseline of normal activity rhythms | Reference model |
  | Entropy (Behavioral) | Measure of disorder or unpredictability in patterns | Anomaly indicator |
  | Fraction Arithmetic | Exact rational numbers (numerator/denominator) | Deterministic evidence |
  | SignalOutput | Final formatted result for external APIs | Export boundary |
  | Artifact Reliability | Confidence weight assigned to a forensic artifact | Quality metric |
  | Logical Fracture | Break in expected semiotic chain (Eco/Peirce/Grice) | Deviation flag |
- Glossary:
  - **Metabolism (Systemic)**: Not biological chemistry, but the sustained rate and pattern of digital events over time.
  - **Entropy**: In this context, the Shannon entropy of state transitions, computed exactly via integer logarithms or counts; high entropy means irregular behavior.
  - **Fraction**: A rational number type storing numerator and denominator separately, ensuring no rounding errors.
  - **Peirce/Eco/Grice Framework**: A semiotic layer mapping events to signs (Peirce), codes (Eco), and conversational maxims (Grice) to detect *logical fractures* when the system "breaks its own rules".
  - **Timestamp**: A discrete integer mark of absolute or relative time.
  - **Deterministic System**: One whose future state is entirely fixed by prior states, leaving no room for probabilistic drift in the arithmetic.
- Scientific Note:
  【Scientific Note】
  The terminology borrowed from C. S. Peirce, Umberto Eco, and H. P. Grice is not mysticism or literary ornament. In this module, these names denote rigorous analytical sensors—conceptual devices that detect *logical fractures* in the same way a physical sensor detects voltage or pressure. Peirce’s semiosis is the transducer that turns raw events into interpretable signs; Eco’s codes are the calibration tables that classify those signs; Grice’s maxims are the threshold filters that flag violations of expected cooperation. A "fracture" is simply a sensor reading outside the calibrated tolerance band. Treat these constructs as laboratory instruments, not philosophy.
- Deterministic Arithmetic Note: All evidence dictionaries store numeric values as `Fraction` or `str`. Internal calculations use rational arithmetic. The only conversion to floating-point occurs inside `SignalOutput.__init__`, mandated by the external API contract. This guarantees bitwise reproducibility of the analysis pipeline up to the final export step.

ESPAÑOL:
- ¿Qué es este módulo?
- Conceptos clave (tabla similar)
- Glosario
- Nota científica
- Aritmética determinista

РУССКИЙ:
- Что это за модуль?
- Ключевые понятия
- Глоссарий
- Научное примечание
- Детерминистская арифметика

中文:
- 什么是本模块？
- 关键概念
- 术语表
- 【科学说明】
- 确定性整数运算

Need to ensure Chinese terms:
- 艾柯 (Eco)
- 格赖斯 (Grice)
- 取证工件 (artifact)
- 逻辑断裂 (logical fracture)

Also, Peirce in Chinese is usually 皮尔斯 (C.S. Peirce). The user didn't specify a banned translation for Peirce, only that Eco and Grice must be specific. I should use 皮尔斯 for Peirce, or 皮尔士. Let's use 皮尔斯 as it's common.

Let's refine the content.

Since the module path is `vigia/inference/metabolic_profiler.py` but docstring says `vigia/engine/metabolic_profiler.py`, I should note this discrepancy or just use the path given. The user says "MODULE PATH: vigia/inference/metabolic_profiler.py" and "MODULE DOCSTRING: vigia/engine/metabolic_profiler.py". I can mention that the canonical path is `vigia/inference/metabolic_profiler.py`.

Let's think about the specific classes and functions to document.

Classes:
- `MetabolicProfile`: Represents the baseline or accumulated statistics of the system's metabolic behavior.
- `MetabolicAnalysisResult`: A container for the output of the analysis, holding profiles, entropy values, and detected deviations.
- `MetabolicProfiler`: The engine. It analyzes event frequency, activity/rest patterns, and behavior entropy.

Functions:
- `to_signal()`: Converts an internal metabolic profile or analysis result into a standardized signal representation. This is likely where the Fraction-to-boundary interaction happens.
- `analyze(event_stream)`: The primary method. Accepts a list of events (each with at least a 'timestamp' integer) and returns a `MetabolicAnalysisResult`.

Constants:
- `TOOL_NAME`: Identifier string for the profiler in forensic logs.
- `ARTIFACT_RELIABILITY`: A rational weight or score indicating the trustworthiness of the generated forensic artifact.

I should describe these in non-Python terms.

Let's draft the tables more carefully.

ENGLISH Key Concepts:
| Concept | Plain-Language Definition | Scientific Role |
|---|---|---|
| Metabolic Profiler | An analytical engine that monitors the "pulse" of digital events | Core analyzer |
| Event Stream | A time-ordered list of discrete system events | Input specimen |
| Timestamp | An integer mark indicating when an event occurred | Temporal coordinate |
| Activity/Rest Pattern | Rhythmic alternation between high-event and no-event windows | Behavioral phenotype |
| Behavioral Entropy | Exact measure of unpredictability in state transitions | Disorder metric |
| Metabolic Profile | Baseline model of normal system rhythm | Reference baseline |
| Fraction (Rational) | Exact ratio of two integers; no decimal rounding | Deterministic number type |
| SignalOutput | Final export container; sole point where exact rationals become floating-point for API compatibility | External interface |
| Artifact Reliability | Rational confidence score assigned to the output forensic artifact | Quality assurance |
| Logical Fracture | A break in the expected chain of signs or cooperative rules | Anomaly flag |

Glossary EN:
- **Event**: A discrete, observable change in system state (e.g., file access, network packet).
- **Activity Window**: A contiguous time span containing one or more events.
- **Rest Window**: A contiguous time span devoid of events.
- **Fraction Arithmetic**: Computation using pairs of integers (numerator, denominator) so that 1/3 + 1/3 = 2/3 exactly, never 0.333… + 0.333… ≈ 0.666….
- **Deterministic Pipeline**: An analysis chain where identical inputs always yield identical internal evidence dictionaries, because no rounding errors are introduced.

Scientific Note EN:
【Scientific Note】
References to Peirce, Eco, and Grice do not invoke mysticism or literary criticism. Within this module, they name rigorous analytical instruments—conceptual sensors. Peirce’s semiosis is the transducer that converts raw system events into interpretable signs; Eco’s codes are the calibration tables against which sign classes are matched; Grice’s maxims are threshold filters that flag violations of expected cooperative behavior. A detected “logical fracture” is nothing more than a sensor reading outside the calibrated tolerance band. Treat these constructs as laboratory hardware, not philosophy.

ESPAÑOL:
- Conceptos clave table:
| Concepto | Definición en lenguaje sencillo | Rol científico |
|---|---|---|
| Perfil metabólico | Modelo de referencia del ritmo normal del sistema | Línea base |
| Flujo de eventos | Lista ordenada cronológicamente de ocurrencias del sistema | Muestra de entrada |
| Patrón actividad/reposo | Alternancia rítmica entre ventanas con y sin eventos | Fenotipo conductual |
| Entropía conductual | Medida exacta de la impredecibilidad en las transiciones de estado | Métrica de desorden |
| Fracción (Racional) | Cociente exacto de dos enteros; sin redondeo decimal | Tipo numérico determinista |
| Salida de señal (SignalOutput) | Contenedor de exportación final; único punto donde los racionales exactos se convierten en punto flotante por compatibilidad de API | Interfaz externa |
| Confiabilidad del artefacto | Puntaje racional de confianza asignado al artefacto forense generado | Garantía de calidad |
| Fractura lógica | Ruptura en la cadena esperada de signos o reglas cooperativas | Indicador de anomalía |

Glosario ES:
- **Evento**: Un cambio discreto y observable en el estado del sistema.
- **Ventana de actividad**: Intervalo de tiempo contiguo que contiene uno o más eventos.
- **Ventana de reposo**: Intervalo de tiempo contiguo sin eventos.
- **Aritmética de fracciones**: Cálculo mediante pares de enteros (numerador, denominador) de modo que 1/3 + 1/3 = 2/3 exactamente, nunca 0,333… + 0,333… ≈ 0,666….
- **Pipeline determinista**: Cadena de análisis en la que entradas idénticas siempre producen diccionarios de evidencia internos idénticos, porque no se introducen errores de redondeo.

Nota Científica ES:
【Nota Científica】
Las referencias a Peirce, Eco y Grice no invocan misticismo ni crítica literaria. En este módulo, ellos nombran instrumentos analíticos rigurosos—sensores conceptuales. La semiosis de Peirce es el transductor que convierte eventos brutos del sistema en signos interpretables; los códigos de Eco son las tablas de calibración contra las cuales se clasifican los signos; los máximas de Grice son los filtros de umbral que señalan violaciones del comportamiento cooperativo esperado. Una “fractura lógica” detectada no es más que una lectura de sensor fuera de la banda de tolerancia calibrada. Trate estos constructos como hardware de laboratorio, no como filosofía.

РУССКИЙ:
- Ключевые понятия:
| Понятие | Определение простым языком | Научная роль |
|---|---|---|
| Метаболический профилировщик | Аналитический движок, отслеживающий «пульс» цифровых событий | Центральный анализатор |
| Поток событий | Хронологически упорядоченный список дискретных системных событий | Входной образец |
| Метаболический профиль | Базовая модель нормального ритма системы | Эталонная линия |
| Энтропия поведения | Точная мера непредсказуемости переходов состояний | Метрика беспорядка |
| Дробь (рациональное число) | Точное отношение двух целых чисел; без десятичного округления | Детерминированный числовой тип |
| Выходной сигнал (SignalOutput) | Контейнер финального экспорта; единственная точка, где точные дроби преобразуются в числа с плавающей точкой для совместимости с API | Внешний интерфейс |
| Надёжность артефакта | Рациональная оценка доверия, присвоенная созданному судебному артефакту | Обеспечение качества |
| Логический разрыв | Нарушение ожидаемой цепочки знаков или кооперативных правил | Флаг аномалии |

Глоссарий RU:
- **Событие**: Дискретное наблюдаемое изменение состояния системы.
- **Окно активности**: Непрерывный временной интервал, содержащий одно или несколько событий.
- **Окно покоя**: Непрерывный временной интервал без событий.
- **Дробная арифметика**: Вычисления с использованием пар целых чисел (числитель, знаменатель), так что 1/3 + 1/3 = 2/3 точно, а не 0,333… + 0,333… ≈ 0,666….
- **Детерминированный конвейер**: Цепочка анализа, в которой идентичные входные данные всегда дают идентичные внутренние словари улик, поскольку ошибки округления отсутствуют.

Научное примечание RU:
【Научное примечание】
Ссылки на Пирса, Эко и Грайса не являются мистицизмом или литературной критикой. В данном модуле они обозначают строгие аналитические инструменты — концептуальные датчики. Семиозис Пирса — это преобразователь, который переводит сырые события системы в интерпретируемые знаки; коды Эко — это таблицы калибровки, по которым классифицируются знаки; максимы Грайса — это пороговые фильтры, регистрирующие нарушения ожидаемого кооперативного поведения. Обнаруженный «логический разрыв» — не что иное, как показание датчика за пределами откалиброванной полосы допуска. Воспринимайте эти конструкты как лабораторное оборудование, а не философию.

中文:
- 关键概念:
| 概念 | 通俗定义 | 科学作用 |
|---|---|---|
| 代谢分析器 (Metabolic Profiler) | 监测数字事件“脉搏”的分析引擎 | 核心分析器 |
| 事件流 | 按时间顺序排列的离散系统事件列表 | 输入样本 |
| 时间戳 | 表示事件发生时刻的整数标记 | 时间坐标 |
| 活动/休息模式 | 高事件窗口与无事件窗口之间的节律性交替 | 行为表型 |
| 行为熵 | 状态转移不可预测性的精确度量 | 无序性指标 |
| 代谢轮廓 | 系统正常节律的基线模型 | 参考基线 |
| 分数（有理数） | 两个整数的精确比值；无十进制舍入 | 确定性数值类型 |
| 信号输出 (SignalOutput) | 最终导出容器；唯一一个将精确有理数转换为浮点数以兼容API的节点 | 外部接口 |
| 取证工件可靠性 | 赋予所生成取证工件的理性置信度评分 | 质量保障 |
| 逻辑断裂 | 预期符号链或合作规则出现断裂 | 异常标记 |

术语表 ZH:
- **事件**: 系统状态中可观察到的离散变化。
- **活动窗口**: 包含一个或多个事件的连续时间段。
- **休息窗口**: 不包含事件的连续时间段。
- **分数运算**: 使用成对整数（分子、分母）进行计算，使得 1/3 + 1/3 = 2/3 完全精确，而不会出现 0.333… + 0.333… ≈ 0.666… 的舍入误差。
- **确定性流水线**: 分析链条中，相同输入总是产生相同的内部证据字典，因为不存在舍入误差。

【科学说明】 ZH:
【科学说明】
本模块借用皮尔斯（C. S. Peirce）、艾柯（Umberto Eco）与格赖斯（H. P. Grice）的术语，并非神秘主义或文学装饰。在此模块中，这些名字代表严格的分析仪器——概念传感器。皮尔斯的符号过程（semiosis）是将原始系统事件转换为可解释符号的换能器；艾柯的符码是用于对符号进行分类的校准表；格赖斯的准则则是标记预期合作行为违背的阈值滤波器。所检测到的“逻辑断裂”只不过是超出校准容差带的传感器读数。请将这些构造视为实验室硬件，而非哲学思辨。

Additional sections:
Maybe a "Deterministic Arithmetic Guarantee" section in each language, emphasizing integer arithmetic and Fractions.

Let's refine the "What Is This Module?" for each language.

EN:
This module, `metabolic_profiler.py`, functions as a digital forensic calorimeter. Instead of measuring chemical energy, it measures the *rhythm* of a computing system: how frequently events occur, how long the system remains quiescent, and how predictable its behavioral patterns are. Scientists can think of it as an electrocardiograph (ECG) for software activity. It ingests a time-ordered sequence of discrete events, constructs a baseline metabolic profile, and flags deviations—called *logical fractures*—using exact rational arithmetic. No rounding errors are introduced during the analysis; every numeric value inside the evidence dictionary is stored as an exact fraction or its string representation, ensuring that the analysis is fully reproducible and legally defensible.

ES:
Este módulo, `metabolic_profiler.py`, actúa como un calorímetro forense digital. En lugar de medir energía química, mide el *ritmo* de un sistema informático: con qué frecuencia ocurren los eventos, cuánto tiempo permanece el sistema en reposo y qué tan predecibles son sus patrones conductuales. Los científicos pueden pensar en él como un electrocardiograma (ECG) para la actividad del software. Ingiere una secuencia ordenada en el tiempo de eventos discretos, construye un perfil metabólico de referencia y señala desviaciones —llamadas *fracturas lógicas*— mediante aritmética racional exacta. No se introducen errores de redondeo durante el análisis; cada valor numérico dentro del diccionario de evidencia se almacena como una fracción exacta o su representación textual, garantizando que el análisis sea totalmente reproducible y jurídicamente defendible.

RU:
Данный модуль, `metabolic_profiler.py`, работает как цифровой судебный калориметр. Вместо измерения химической энергии он измеряет *ритм* вычислительной системы: частоту событий, длительность неактивности и предсказуемость поведенческих паттернов. Учёные могут воспринимать его как электрокардиограф (ЭКГ) для программной активности. Модуль принимает хронологически упорядоченную последовательность дискретных событий, строит эталонный метаболический профиль и маркирует отклонения — называемые *логическими разрывами* — с помощью точной дробной арифметики. В процессе анализа не вносится ошибок округления; каждое числовое значение во внутреннем словаре улик хранится в виде точной дроби или её строкового представления, что гарантирует полную воспроизводимость и юридическую состоятельность анализа.

ZH:
本模块 `metabolic_profiler.py` 的功能相当于一台数字取证量热器。它并非测量化学能，而是测量计算机系统的“节律”：事件发生的频率、系统静止的时长，以及其行为模式的可预测性。科研人员可将其视为软件活动的“心电图（ECG）”。该模块接收按时间排序的离散事件序列，构建正常代谢轮廓基线，并利用精确的有理数运算标记偏差——称为“逻辑断裂”。分析过程中不引入任何舍入误差；证据字典中的每一个数值均以精确分数或其字符串形式存储，从而确保分析结果完全可复现且具有法律上的可辩护性。

Now, I need to make sure I address the classes and functions in a way scientists understand, perhaps as "Components".

Components Table maybe? The user wants "Key concepts with tables". I can include a table for components.

Let's add a Component/Construct table in each language.

EN:
| Construct | Scientific Analogy | Function |
|---|---|---|
| `MetabolicProfiler` | Core spectrometer / ECG machine | Orchestrates analysis |
| `MetabolicProfile` | Baseline calibration curve | Stores normal rhythm reference |
| `MetabolicAnalysisResult` | Lab report with attachments | Holds all findings and exact metrics |
| `analyze()` | Assay protocol | Processes event stream to build profile |
| `to_signal()` | Signal converter / DAC | Prepares exact data for external API |
| `TOOL_NAME` | Instrument serial label | Identifies profiler in audit logs |
| `ARTIFACT_RELIABILITY` | Measurement uncertainty (rational) | Quantifies confidence in the forensic artifact |

ES:
| Constructo | Analogía científica | Función |
|---|---|---|
| `MetabolicProfiler` | Espectrómetro central / máquina de ECG | Orquesta el análisis |
| `MetabolicProfile` | Curva de calibración basal | Almacena la referencia del ritmo normal |
| `MetabolicAnalysisResult` | Informe de laboratorio con anexos | Contiene todos los hallazgos y métricas exactas |
| `analyze()` | Protocolo de ensayo | Procesa el flujo de eventos para construir el perfil |
| `to_signal()` | Convertidor de señal / DAC | Prepara datos exactos para la API externa |
| `TOOL_NAME` | Etiqueta de serie del instrumento | Identifica el perfilador en los registros de auditoría |
| `ARTIFACT_RELIABILITY` | Incertidumbre de medida (racional) | Cuantifica la confianza en el artefacto forense |

RU:
| Конструкт | Научная аналогия | Функция |
|---|---|---|
| `MetabolicProfiler` | Центральный спектрометр / аппарат ЭКГ | Оркестрирует анализ |
| `MetabolicProfile` | Базовая калибровочная кривая | Хранит эталон нормального ритма |
| `MetabolicAnalysisResult` | Лабораторный отчёт с приложениями | Содержит все находки и точные метрики |
| `analyze()` | Протокол анализа | Обрабатывает поток событий для построения профиля |
| `to_signal()` | Преобразователь сигнала / ЦАП | Подготавливает точные данные для внешнего API |
| `TOOL_NAME` | Серийная метка прибора | Идентифицирует профилировщик в журналах аудита |
| `ARTIFACT_RELIABILITY` | Погрешность измерения (рациональная) | Количественно оценивает доверие к судебному артефакту |

ZH:
| 构造 | 科学类比 | 功能 |
|---|---|---|
| `MetabolicProfiler` | 核心光谱仪 / 心电图机 | 统筹分析 |
| `MetabolicProfile` | 基线校准曲线 | 存储正常节律参考 |
| `MetabolicAnalysisResult` | 附带附件的实验报告 | 保存所有发现及精确指标 |
| `analyze()` | 检测规程 | 处理事件流以构建轮廓 |
| `to_signal()` | 信号转换器 / 数模转换器 | 为外部API准备精确数据 |
| `TOOL_NAME` | 仪器序列号标签 | 在审计日志中标识分析器 |
| `ARTIFACT_RELIABILITY` | 测量不确定度（有理数） | 量化对取证工件的置信度 |

Now, the deterministic arithmetic emphasis.
I should have a specific callout or paragraph: "All internal calculations are performed using Python's `fractions.Fraction`, which represents each number as a pair of integers. This avoids the non-deterministic rounding inherent in IEEE 754 double-precision floating-point arithmetic. The `evidence` dictionary therefore contains only exact rational numbers or their canonical string representations. The only exception is the `SignalOutput` constructor, which converts to float as required by the external API boundary."

Let's integrate this into the text naturally.

Also, the user specified the module docstring is `vigia/engine/metabolic_profiler.py`. I should mention that the source header indicates this path, but the deployed path is `vigia/inference/metabolic_profiler.py`. Or simply note the module is located at `vigia/inference/metabolic_profiler.py`. I'll add a small note.

I need to make sure the document is "thorough but concise". So I shouldn't be overly verbose, but cover all required elements.

Let's assemble the final Markdown.

Structure:
- Maybe a top header.
- ENGLISH section
  - Heading
  - What Is This Module?
  - Key Concepts & Components (two tables or one combined? I'll do one comprehensive table and maybe a separate one for components. To be concise, one table with all key items.)
  - Glossary
  - Scientific Note
  - Deterministic Arithmetic Guarantee (short paragraph)
  - License line
- ESPAÑOL section (same structure)
- РУССКИЙ section
- 中文 section

Let's verify Chinese terminology again:
- 艾柯: Yes.
- 格赖斯: Yes.
- 取证工件: Yes, for artifact.
- 逻辑断裂: Yes, for logical fracture.
Also, Peirce is 皮尔斯.

Check scientific note content: Must explain that Peirce/Eco/Grice terminology is NOT mysticism — use the sensor analogy. My draft does exactly that.

Check no floating-point math explanations for deterministic systems: I must not say "floating-point is used for X because it's faster/approximate". I should say float is ONLY in SignalOutput constructor, unavoidable by API. And internal is Fraction/integer.

Check  Must be exact.

Let's finalize the text.

ENGLISH:

What Is This Module?
`vigia/inference/metabolic_profiler.py` is a deterministic forensic analyzer that treats a computing system as a living organism whose “metabolism” is the stream of discrete events it generates over time. Like a clinical electrocardiograph (ECG) records the electrical rhythm of a heart, this module records the temporal rhythm of software behavior: event frequency, quiescent (rest) intervals, and the predictability—or entropy—of state transitions. It constructs a baseline *metabolic profile*, compares live observations against that baseline, and flags deviations termed *logical fractures*. Every numeric quantity inside the analysis pipeline is handled as an exact rational number (a ratio of two integers) or its string representation, guaranteeing that the chain of evidence is bitwise reproducible and free of rounding artifacts.

Key Concepts
| Concept | Plain-Language Definition | Scientific Role |
|---|---|---|
| Event Stream | A time-ordered sequence of discrete system occurrences (e.g., file access, network packet) | Input specimen |
| Timestamp | An integer mark recording the absolute or relative moment of an event | Temporal coordinate |
| Activity / Rest Pattern | Rhythmic alternation between windows containing events and windows devoid of events | Behavioral phenotype |
| Behavioral Entropy | Exact measure of disorder or unpredictability in the sequence of states | Anomaly indicator |
| Metabolic Profile | Baseline model of the system’s normal rhythm, built from historical event statistics | Reference calibration |
| MetabolicProfiler | The core analytical engine that ingests streams and computes profiles | Central instrument |
| MetabolicAnalysisResult | The complete laboratory report containing profiles, entropy values, and flagged fractures | Output container |
| Fraction (Rational) | Exact ratio of two integers; arithmetic is performed without decimal rounding | Deterministic number type |
| SignalOutput | The final export wrapper; the sole boundary where exact rationals are cast to floating-point to satisfy an external API contract | External interface |
| Artifact Reliability | Rational confidence score assigned to the generated forensic artifact | Quality-assurance metric |
| Logical Fracture | A break in the expected chain of signs (Peirce), codes (Eco), or cooperative rules (Grice) | Deviation flag |

Glossary
- **Event**: A discrete, observable state change in the target system.
- **Activity Window**: A contiguous time interval containing one or more events.
- **Rest Window**: A contiguous time interval containing zero events.
- **Fraction Arithmetic**: Operations on pairs of integers (numerator, denominator). Ensures identities such as 1/3 + 1/3 = 2/3 exactly, with no approximation.
- **Deterministic Pipeline**: An analytical workflow in which identical inputs always produce identical internal evidence, because no stochastic rounding or floating-point noise is introduced.
- **Semiotic Sensor**: A conceptual instrument (after Peirce, Eco, Grice) that transduces raw event data into classified signs and detects violations.

Scientific Note
【Scientific Note】
The terminology borrowed from C. S. Peirce, Umberto Eco, and H. P. Grice is not mysticism, literary criticism, or philosophical ornament. Inside this module, these names denote rigorous analytical instruments—conceptual sensors. Peirce’s semiosis is the transducer that turns raw system events into interpretable signs; Eco’s codes are the calibration tables against which those sign classes are matched; Grice’s maxims are the threshold filters that flag violations of expected cooperative behavior. A detected “logical fracture” is nothing more than a sensor reading that falls outside the calibrated tolerance band. Treat these constructs as laboratory hardware, not as metaphysics.

Deterministic Arithmetic Guarantee
All internal evidence dictionaries store numeric values as `Fraction` or `str`. Every intermediate calculation—frequency, entropy, and reliability—uses integer rational arithmetic. Conversion to floating-point occurs only inside the `SignalOutput` constructor, and solely because the external API mandates that representation. Until that final boundary, the pipeline is entirely deterministic.



ESPAÑOL:

¿Qué es este módulo?
`vigia/inference/metabolic_profiler.py` es un analizador forense determinista que trata a un sistema informático como un organismo vivo cuyo “metabolismo” es el flujo de eventos discretos que genera en el tiempo. Al igual que un electrocardiógrafo (ECG) clínico registra el ritmo eléctrico del corazón, este módulo registra el ritmo temporal del comportamiento del software: frecuencia de eventos, intervalos de reposo (inactividad) y la predecibilidad —o entropía— de las transiciones de estado. Construye un *perfil metabólico* de referencia, compara las observaciones en tiempo real contra esa línea base y marca las desviaciones denominadas *fracturas lógicas*. Cada cantidad numérica dentro de la tubería de análisis se maneja como un número racional exacto (una razón de dos enteros) o su representación textual, garantizando que la cadena de evidencia sea reproducible bit a bit y libre de artefactos de redondeo.

Conceptos clave
| Concepto | Definición en lenguaje sencillo | Rol científico |
|---|---|---|
| Flujo de eventos | Secuencia ordenada cronológicamente de ocurrencias discretas del sistema (p. ej., acceso a archivo, paquete de red) | Muestra de entrada |
| Marca temporal (Timestamp) | Marca entera que registra el momento absoluto o relativo de un evento | Coordenada temporal |
| Patrón actividad/reposo | Alternancia rítmica entre ventanas con eventos y ventanas sin eventos | Fenotipo conductual |
| Entropía conductual | Medida exacta del desorden o la impredecibilidad en la secuencia de estados | Indicador de anomalía |
| Perfil metabó
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
