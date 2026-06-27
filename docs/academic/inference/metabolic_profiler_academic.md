<!--
VIGIA Academic Documentation
Module: 8bc0d526
Batch ID: vigia-doc-0102-8bc0d526
Generated: 2026-05-20T14:56:47.866726+00:00
-->

# Module Documentation: `vigia/inference/metabolic_profiler.py`

---

## ENGLISH

### What Is This Module?

`vigia/inference/metabolic_profiler.py` is a deterministic forensic analyzer that treats a computing system as a living organism whose "metabolism" is the stream of discrete events it generates over time. Like a clinical electrocardiograph (ECG) records the electrical rhythm of a heart, this module records the temporal rhythm of software behavior: event frequency, quiescent (rest) intervals, and the predictability—or entropy—of state transitions. It constructs a baseline *metabolic profile*, compares live observations against that baseline, and flags deviations termed *logical fractures*. Every numeric quantity inside the analysis pipeline is handled as an exact rational number (a ratio of two integers) or its string representation, guaranteeing that the chain of evidence is bitwise reproducible and free of rounding artifacts.

### Key Concepts

| Concept | Plain-Language Definition | Scientific Role |
|---|---|---|
| Event Stream | A time-ordered sequence of discrete system occurrences (e.g., file access, network packet) | Input specimen |
| Timestamp | An integer mark recording the absolute or relative moment of an event | Temporal coordinate |
| Activity / Rest Pattern | Rhythmic alternation between windows containing events and windows devoid of events | Behavioral phenotype |
| Behavioral Entropy | Exact measure of disorder or unpredictability in the sequence of states | Anomaly indicator |
| Metabolic Profile | Baseline model of the system's normal rhythm, built from historical event statistics | Reference calibration |
| MetabolicProfiler | The core analytical engine that ingests streams and computes profiles | Central instrument |
| MetabolicAnalysisResult | The complete laboratory report containing profiles, entropy values, and flagged fractures | Output container |
| Fraction (Rational) | Exact ratio of two integers; arithmetic is performed without decimal rounding | Deterministic number type |
| SignalOutput | The final export wrapper; the sole boundary where exact rationals are cast to floating-point to satisfy an external API contract | External interface |
| Artifact Reliability | Rational confidence score assigned to the generated forensic artifact | Quality-assurance metric |
| Logical Fracture | A break in the expected chain of signs (Peirce), codes (Eco), or cooperative rules (Grice) | Deviation flag |

### Analytical Constructs

| Construct | Scientific Analogy | Function |
|---|---|---|
| `MetabolicProfiler` | Core spectrometer / ECG machine | Orchestrates analysis |
| `MetabolicProfile` | Baseline calibration curve | Stores normal rhythm reference |
| `MetabolicAnalysisResult` | Lab report with attachments | Holds all findings and exact metrics |
| `analyze()` | Assay protocol | Processes event stream to build profile |
| `to_signal()` | Signal converter / DAC | Prepares exact data for external API |
| `TOOL_NAME` | Instrument serial label | Identifies profiler in audit logs |
| `ARTIFACT_RELIABILITY` | Measurement uncertainty (rational) | Quantifies confidence in the forensic artifact |

### Glossary

- **Event**: A discrete, observable state change in the target system.
- **Activity Window**: A contiguous time interval containing one or more events.
- **Rest Window**: A contiguous time interval containing zero events.
- **Fraction Arithmetic**: Operations on pairs of integers (numerator, denominator). Ensures identities such as 1/3 + 1/3 = 2/3 exactly, with no approximation.
- **Deterministic Pipeline**: An analytical workflow in which identical inputs always produce identical internal evidence, because no stochastic rounding or floating-point noise is introduced.
- **Semiotic Sensor**: A conceptual instrument (after Peirce, Eco, Grice) that transduces raw event data into classified signs and detects violations.

### Deterministic Arithmetic Guarantee

All internal evidence dictionaries store numeric values as `Fraction` or `str`. Every intermediate calculation—frequency, entropy, and reliability—uses integer rational arithmetic. Conversion to floating-point occurs only inside the `SignalOutput` constructor, and solely because the external API mandates that representation. Until that final boundary, the pipeline is entirely deterministic.

### 【Scientific Note】

The terminology borrowed from C. S. Peirce, Umberto Eco, and H. P. Grice is not mysticism, literary criticism, or philosophical ornament. Inside this module, these names denote rigorous analytical instruments—conceptual sensors. Peirce's semiosis is the transducer that turns raw system events into interpretable signs; Eco's codes are the calibration tables against which those sign classes are matched; Grice's maxims are the threshold filters that flag violations of expected cooperative behavior. A detected "logical fracture" is nothing more than a sensor reading that falls outside the calibrated tolerance band. Treat these constructs as laboratory hardware, not as metaphysics.

---

## ESPAÑOL

### ¿Qué es este módulo?

`vigia/inference/metabolic_profiler.py` es un analizador forense determinista que trata a un sistema informático como un organismo vivo cuyo "metabolismo" es el flujo de eventos discretos que genera en el tiempo. Al igual que un electrocardiógrafo (ECG) clínico registra el ritmo eléctrico del corazón, este módulo registra el ritmo temporal del comportamiento del software: frecuencia de eventos, intervalos de reposo (inactividad) y la predecibilidad —o entropía— de las transiciones de estado. Construye un *perfil metabólico* de referencia, compara las observaciones en tiempo real contra esa línea base y marca las desviaciones denominadas *fracturas lógicas*. Cada cantidad numérica dentro de la tubería de análisis se maneja como un número racional exacto (una razón de dos enteros) o su representación textual, garantizando que la cadena de evidencia sea reproducible bit a bit y libre de artefactos de redondeo.

### Conceptos clave

| Concepto | Definición en lenguaje sencillo | Rol científico |
|---|---|---|
| Flujo de eventos | Secuencia ordenada cronológicamente de ocurrencias discretas del sistema | Muestra de entrada |
| Marca temporal (Timestamp) | Marca entera que registra el momento absoluto o relativo de un evento | Coordenada temporal |
| Patrón actividad/reposo | Alternancia rítmica entre ventanas con eventos y ventanas sin eventos | Fenotipo conductual |
| Entropía conductual | Medida exacta del desorden o la impredecibilidad en la secuencia de estados | Indicador de anomalía |
| Perfil metabólico | Modelo de referencia del ritmo normal del sistema | Línea base de calibración |
| MetabolicProfiler | Motor analítico central que ingiere flujos y calcula perfiles | Instrumento central |
| MetabolicAnalysisResult | Informe de laboratorio completo con perfiles, valores de entropía y fracturas marcadas | Contenedor de salida |
| Fracción (Racional) | Cociente exacto de dos enteros; aritmética sin redondeo decimal | Tipo numérico determinista |
| Salida de señal (SignalOutput) | Contenedor de exportación final; único punto donde los racionales exactos se convierten en punto flotante por compatibilidad de API | Interfaz externa |
| Confiabilidad del artefacto | Puntaje racional de confianza asignado al artefacto forense generado | Garantía de calidad |
| Fractura lógica | Ruptura en la cadena esperada de signos o reglas cooperativas | Indicador de anomalía |

### Constructos analíticos

| Constructo | Analogía científica | Función |
|---|---|---|
| `MetabolicProfiler` | Espectrómetro central / máquina de ECG | Orquesta el análisis |
| `MetabolicProfile` | Curva de calibración basal | Almacena la referencia del ritmo normal |
| `MetabolicAnalysisResult` | Informe de laboratorio con anexos | Contiene todos los hallazgos y métricas exactas |
| `analyze()` | Protocolo de ensayo | Procesa el flujo de eventos para construir el perfil |
| `to_signal()` | Convertidor de señal / DAC | Prepara datos exactos para la API externa |
| `TOOL_NAME` | Etiqueta de serie del instrumento | Identifica el perfilador en los registros de auditoría |
| `ARTIFACT_RELIABILITY` | Incertidumbre de medida (racional) | Cuantifica la confianza en el artefacto forense |

### Glosario

- **Evento**: Un cambio discreto y observable en el estado del sistema.
- **Ventana de actividad**: Intervalo de tiempo contiguo que contiene uno o más eventos.
- **Ventana de reposo**: Intervalo de tiempo contiguo sin eventos.
- **Aritmética de fracciones**: Cálculo mediante pares de enteros (numerador, denominador) de modo que 1/3 + 1/3 = 2/3 exactamente, nunca 0,333… + 0,333… ≈ 0,666….
- **Pipeline determinista**: Cadena de análisis en la que entradas idénticas siempre producen diccionarios de evidencia internos idénticos, porque no se introducen errores de redondeo.

### Garantía de aritmética determinista

Todos los diccionarios de evidencia internos almacenan valores numéricos como `Fraction` o `str`. Cada cálculo intermedio —frecuencia, entropía y confiabilidad— utiliza aritmética racional entera. La conversión a punto flotante ocurre únicamente dentro del constructor de `SignalOutput`, y exclusivamente porque la API externa lo exige. Hasta ese límite final, la tubería es completamente determinista.

### 【Nota Científica】

Las referencias a Peirce, Eco y Grice no invocan misticismo ni crítica literaria. En este módulo, ellos nombran instrumentos analíticos rigurosos—sensores conceptuales. La semiosis de Peirce es el transductor que convierte eventos brutos del sistema en signos interpretables; los códigos de Eco son las tablas de calibración contra las cuales se clasifican los signos; los máximas de Grice son los filtros de umbral que señalan violaciones del comportamiento cooperativo esperado. Una "fractura lógica" detectada no es más que una lectura de sensor fuera de la banda de tolerancia calibrada. Trate estos constructos como hardware de laboratorio, no como filosofía.

---

## РУССКИЙ

### Что представляет собой этот модуль?

Данный модуль, `metabolic_profiler.py`, работает как цифровой судебный калориметр. Вместо измерения химической энергии он измеряет *ритм* вычислительной системы: частоту событий, длительность неактивности и предсказуемость поведенческих паттернов. Учёные могут воспринимать его как электрокардиограф (ЭКГ) для программной активности. Модуль принимает хронологически упорядоченную последовательность дискретных событий, строит эталонный метаболический профиль и маркирует отклонения — называемые *логическими разрывами* — с помощью точной дробной арифметики. В процессе анализа не вносится ошибок округления; каждое числовое значение во внутреннем словаре улик хранится в виде точной дроби или её строкового представления, что гарантирует полную воспроизводимость и юридическую состоятельность анализа.

### Ключевые понятия

| Понятие | Определение простым языком | Научная роль |
|---|---|---|
| Поток событий | Хронологически упорядоченный список дискретных системных событий | Входной образец |
| Метка времени (Timestamp) | Целочисленная метка, фиксирующая абсолютный или относительный момент события | Временная координата |
| Паттерн активности/покоя | Ритмичное чередование окон с событиями и без них | Поведенческий фенотип |
| Энтропия поведения | Точная мера непредсказуемости переходов состояний | Метрика беспорядка |
| Метаболический профиль | Базовая модель нормального ритма системы | Эталонная калибровка |
| MetabolicProfiler | Центральный аналитический движок, обрабатывающий потоки и вычисляющий профили | Центральный инструмент |
| MetabolicAnalysisResult | Полный лабораторный отчёт с профилями, значениями энтропии и помеченными разрывами | Контейнер вывода |
| Дробь (рациональное число) | Точное отношение двух целых чисел; арифметика без десятичного округления | Детерминированный числовой тип |
| Выходной сигнал (SignalOutput) | Контейнер финального экспорта; единственная точка, где точные дроби преобразуются в числа с плавающей точкой для совместимости с API | Внешний интерфейс |
| Надёжность артефакта | Рациональная оценка доверия, присвоенная созданному судебному артефакту | Обеспечение качества |
| Логический разрыв | Нарушение ожидаемой цепочки знаков или кооперативных правил | Флаг аномалии |

### Аналитические конструкты

| Конструкт | Научная аналогия | Функция |
|---|---|---|
| `MetabolicProfiler` | Центральный спектрометр / аппарат ЭКГ | Оркестрирует анализ |
| `MetabolicProfile` | Базовая калибровочная кривая | Хранит эталон нормального ритма |
| `MetabolicAnalysisResult` | Лабораторный отчёт с приложениями | Содержит все находки и точные метрики |
| `analyze()` | Протокол анализа | Обрабатывает поток событий для построения профиля |
| `to_signal()` | Преобразователь сигнала / ЦАП | Подготавливает точные данные для внешнего API |
| `TOOL_NAME` | Серийная метка прибора | Идентифицирует профилировщик в журналах аудита |
| `ARTIFACT_RELIABILITY` | Погрешность измерения (рациональная) | Количественно оценивает доверие к судебному артефакту |

### Глоссарий

- **Событие**: Дискретное наблюдаемое изменение состояния системы.
- **Окно активности**: Непрерывный временной интервал, содержащий одно или несколько событий.
- **Окно покоя**: Непрерывный временной интервал без событий.
- **Дробная арифметика**: Вычисления с использованием пар целых чисел (числитель, знаменатель), так что 1/3 + 1/3 = 2/3 точно, а не 0,333… + 0,333… ≈ 0,666….
- **Детерминированный конвейер**: Цепочка анализа, в которой идентичные входные данные всегда дают идентичные внутренние словари улик, поскольку ошибки округления отсутствуют.

### Гарантия детерминированной арифметики

Все внутренние словари доказательств хранят числовые значения как `Fraction` или `str`. Каждый промежуточный расчёт — частота, энтропия и надёжность — использует целочисленную рациональную арифметику. Преобразование в числа с плавающей точкой происходит только внутри конструктора `SignalOutput`, и исключительно потому, что внешний API это требует. До этой конечной границы конвейер является полностью детерминированным.

### 【Научное примечание】

Ссылки на Пирса, Эко и Грайса не являются мистицизмом или литературной критикой. В данном модуле они обозначают строгие аналитические инструменты — концептуальные датчики. Семиозис Пирса — это преобразователь, который переводит сырые события системы в интерпретируемые знаки; коды Эко — это таблицы калибровки, по которым классифицируются знаки; максимы Грайса — это пороговые фильтры, регистрирующие нарушения ожидаемого кооперативного поведения. Обнаруженный «логический разрыв» — не что иное, как показание датчика за пределами откалиброванной полосы допуска. Воспринимайте эти конструкты как лабораторное оборудование, а не философию.

---

## 中文

### 本模块是什么？

本模块 `metabolic_profiler.py` 的功能相当于一台数字取证量热器。它并非测量化学能，而是测量计算机系统的"节律"：事件发生的频率、系统静止的时长，以及其行为模式的可预测性。科研人员可将其视为软件活动的"心电图（ECG）"。该模块接收按时间排序的离散事件序列，构建正常代谢轮廓基线，并利用精确的有理数运算标记偏差——称为"逻辑断裂"。分析过程中不引入任何舍入误差；证据字典中的每一个数值均以精确分数或其字符串形式存储，从而确保分析结果完全可复现且具有法律上的可辩护性。

### 核心概念

| 概念 | 通俗定义 | 科学作用 |
|---|---|---|
| 事件流 | 按时间顺序排列的离散系统事件序列（如文件访问、网络数据包） | 输入样本 |
| 时间戳 | 表示事件发生时刻的整数标记 | 时间坐标 |
| 活动/休息模式 | 高事件窗口与无事件窗口之间的节律性交替 | 行为表型 |
| 行为熵 | 状态转移不可预测性的精确度量 | 无序性指标 |
| 代谢轮廓 | 系统正常节律的基线模型 | 参考基线 |
| MetabolicProfiler | 接收流并计算轮廓的核心分析引擎 | 核心仪器 |
| MetabolicAnalysisResult | 包含轮廓、熵值和标记断裂的完整实验报告 | 输出容器 |
| 分数（有理数） | 两个整数的精确比值；无十进制舍入 | 确定性数值类型 |
| 信号输出 (SignalOutput) | 最终导出容器；唯一一个将精确有理数转换为浮点数以兼容API的节点 | 外部接口 |
| 取证工件可靠性 | 赋予所生成取证工件的理性置信度评分 | 质量保障 |
| 逻辑断裂 | 预期符号链或合作规则出现断裂 | 异常标记 |

### 分析构造

| 构造 | 科学类比 | 功能 |
|---|---|---|
| `MetabolicProfiler` | 核心光谱仪 / 心电图机 | 统筹分析 |
| `MetabolicProfile` | 基线校准曲线 | 存储正常节律参考 |
| `MetabolicAnalysisResult` | 附带附件的实验报告 | 保存所有发现及精确指标 |
| `analyze()` | 检测规程 | 处理事件流以构建轮廓 |
| `to_signal()` | 信号转换器 / 数模转换器 | 为外部API准备精确数据 |
| `TOOL_NAME` | 仪器序列号标签 | 在审计日志中标识分析器 |
| `ARTIFACT_RELIABILITY` | 测量不确定度（有理数） | 量化对取证工件的置信度 |

### 术语表

- **事件**: 系统状态中可观察到的离散变化。
- **活动窗口**: 包含一个或多个事件的连续时间段。
- **休息窗口**: 不包含事件的连续时间段。
- **分数运算**: 使用成对整数（分子、分母）进行计算，使得 1/3 + 1/3 = 2/3 完全精确，而不会出现 0.333… + 0.333… ≈ 0.666… 的舍入误差。
- **确定性流水线**: 分析链条中，相同输入总是产生相同的内部证据字典，因为不存在舍入误差。

### 确定性运算保证

所有内部证据字典以 `Fraction` 或 `str` 形式存储数值。每个中间计算——频率、熵与可靠性——均使用整数有理运算。转换为浮点数仅发生在 `SignalOutput` 构造函数内部，且仅因外部 API 要求该表示形式。在最终边界之前，流水线完全确定性。

### 【科学说明】

本模块借用皮尔斯（C. S. Peirce）、艾柯（Umberto Eco）与格赖斯（H. P. Grice）的术语，并非神秘主义或文学装饰。在此模块中，这些名字代表严格的分析仪器——概念传感器。皮尔斯的符号过程（semiosis）是将原始系统事件转换为可解释符号的换能器；艾柯的符码是用于对符号进行分类的校准表；格赖斯的准则则是标记预期合作行为违背的阈值滤波器。所检测到的"逻辑断裂"只不过是超出校准容差带的传感器读数。请将这些构造视为实验室硬件，而非哲学思辨。

---

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
