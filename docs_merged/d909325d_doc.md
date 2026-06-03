<!--
VIGIA Academic Documentation
Module: d909325d
Batch ID: vigia-doc-0130-d909325d
Generated: 2026-05-20T14:56:47.872545+00:00
-->

ENGLISH:
# ENGLISH

## What Is This Module?
This module is a digital-forensic interpreter for two Windows system journals: **Amcache.hve** and **ShimCache** (also known as AppCompatCache). In non-specialist terms, it functions like a laboratory instrument that reads two different event logs left behind by the Windows operating system whenever a program is launched—or even when the OS merely considers launching one.

- **Amcache** acts as a complete execution ledger: every program that actually ran, including malicious software, leaves a trace here.
- **ShimCache** acts as an intent ledger: it lists programs that Windows prepared to run, regardless of whether the launch succeeded or failed.

The module transforms raw binary registry entries into structured, human-readable forensic findings without using inexact floating-point arithmetic. Every numerical value is stored as an exact integer or rational fraction (text-serialized when needed), ensuring that evidence metrics remain deterministic and reproducible across repeated analyses.

## Key Concepts

| Concept | Description | Role in Analysis |
|---------|-------------|------------------|
| **Amcache.hve** | A Windows registry hive that logs metadata for all executed applications (path, SHA1, install date, last run timestamp). | Primary evidence source for confirmed execution events. |
| **ShimCache / AppCompatCache** | A compatibility cache stored in the SYSTEM registry hive; records programs Windows mapped for execution, including failed attempts. | Secondary evidence source for intent and anti-forensics detection. |
| **Deterministic Integer Arithmetic** | A calculation policy that forbids floating-point numbers. All metrics use exact integers or `Fraction` objects, eliminating rounding errors. | Guarantees that numerical evidence is bitwise reproducible. |
| **Signal** (via `to_signal()`) | A normalized, interpretable unit of evidence derived from a raw registry entry. Analogous to a processed sensor reading. | Bridges raw data and analytical conclusions. |
| **Artifact Reliability** | A constant-defined trust score assigned to the source artifact class, expressed as an exact rational. | Weighs the confidence level of extracted records. |
| **Blacklisted Programs** | A curated registry of known-malicious program signatures. | Enables automated flagging of high-risk executions. |

## Glossary

| Term | Definition |
|------|------------|
| **Registry Hive** | A top-level logical group within the Windows Registry, analogous to a distinct file cabinet containing system configuration records. |
| **SHA1** | A cryptographic hash function producing a 160-bit digest; used here as a deterministic file fingerprint. |
| **Forensic Artifact** | Any digital object with potential evidentiary value—here, specific registry structures left by OS activity. |
| **Deterministic System** | A process where identical inputs always yield identical outputs, with no randomness or rounding uncertainty. |
| **Fraction (Rational Number)** | A ratio of two integers (e.g., 3/4) stored exactly, avoiding the approximation inherent to decimal floating-point representation. |
| **Signal** | In this context, a structured data object that encodes a semiotic interpretation of a raw registry entry. |
| **Amcache Record** | A single row-like data unit extracted from Amcache.hve representing one program execution instance. |
| **ShimCache Record** | A single data unit from ShimCache representing one program compatibility check or attempted execution. |

## 【Scientific Note】
The analytical vocabulary in this module draws from the semiotic frameworks of **Charles Sanders Peirce**, **Umberto Eco**, and **H. Paul Grice**. This is not mysticism or literary criticism. It is a formal notation system—functionally equivalent to the calibration algebra used in physical sensor design.

Think of a raw registry entry as the electrical output of an uncalibrated photodetector. Peirce's triadic model (sign, object, interpretant) provides the wiring diagram that tells us *what* is being measured, *how* it refers to the real-world program, and *what* the investigator should conclude. Eco's codes govern how the binary pattern is decoded into a culturally/technically meaningful message (the file path, the hash, the timestamp). Grice's cooperative maxims function as noise-reduction filters: they detect **logical fractures**—statements that violate expected patterns of rational system behavior, such as a malware entry pretending to be a legitimate system process.

The `to_signal()` method is therefore the analog-to-digital converter of this forensic sensor. It produces an exact, deterministic integer-valued reading from an analog-like raw binary stimulus.

---

ESPAÑOL:
# ESPAÑOL

## ¿Qué es este módulo?
Este módulo es un intérprete forense digital para dos diarios del sistema Windows: **Amcache.hve** y **ShimCache** (también conocido como AppCompatCache). En términos no especializados, funciona como un instrumento de laboratorio que lee dos registros de eventos distintos que el sistema operativo Windows deja cada vez que se lanza un programa—incluso cuando el sistema operativo únicamente *considera* lanzarlo.

- **Amcache** actúa como un libro mayor de ejecución completo: todo programa que efectivamente se ejecutó, incluido software malicioso, deja un rastro aquí.
- **ShimCache** actúa como un libro mayor de intenciones: enumera programas que Windows preparó para ejecutar, independientemente de si el lanzamiento tuvo éxito o fracasó.

El módulo transforma entradas binarias brutas del registro en hallazgos forenses estructurados y legibles sin utilizar aritmética de punto flotante inexacta. Cada valor numérico se almacena como un entero exacto o una fracción racional (serializada como texto cuando es necesario), garantizando que las métricas de evidencia sean deterministas y reproducibles en análisis repetidos.

## Conceptos clave

| Concepto | Descripción | Rol en el análisis |
|----------|-------------|--------------------|
| **Amcache.hve** | Una colmena (hive) del registro de Windows que registra metadatos de todas las aplicaciones ejecutadas (ruta, SHA1, fecha de instalación, marca temporal de última ejecución). | Fuente primaria de evidencia para eventos de ejecución confirmada. |
| **ShimCache / AppCompatCache** | Caché de compatibilidad almacenada en la colmena SYSTEM del registro; registra programas que Windows mapeó para ejecución, incluyendo intentos fallidos. | Fuente secundaria de evidencia para intención y detección de antiforense. |
| **Aritmética entera determinista** | Política de cálculo que prohíbe números de punto flotante. Todas las métricas usan enteros exactos u objetos `Fraction`, eliminando errores de redondeo. | Garantiza que la evidencia numérica sea reproducible bit a bit. |
| **Señal** (vía `to_signal()`) | Unidad de evidencia normalizada e interpretable derivada de una entrada bruta del registro. Análoga a una lectura de sensor procesada. | Puente entre datos brutos y conclusiones analíticas. |
| **Confiabilidad del artefacto** | Puntuación de confianza asignada a la clase de artefacto fuente, definida por constante y expresada como una fracción racional exacta. | Pondera el nivel de confianza de los registros extraídos. |
| **Programas en lista negra** | Registro curado de firmas de programas conocidos como maliciosos. | Permite el marcado automatizado de ejecuciones de alto riesgo. |

## Glosario

| Término | Definición |
|---------|------------|
| **Colmena del Registro (Registry Hive)** | Grupo lógico de nivel superior dentro del Registro de Windows, análogo a un archivador distinto que contiene registros de configuración del sistema. |
| **SHA1** | Función hash criptográfica que produce un resumen de 160 bits; usada aquí como huella digital determinista de un archivo. |
| **Artefacto forense** | Cualquier objeto digital con valor potencial probatorio—aquí, estructuras específicas del registro dejadas por la actividad del sistema operativo. |
| **Sistema determinista** | Proceso en el que entradas idénticas siempre producen salidas idénticas, sin aleatoriedad ni incertidumbre de redondeo. |
| **Fracción (número racional)** | Razón de dos enteros (p. ej., 3/4) almacenada exactamente, evitando la aproximación inherente a la representación decimal de punto flotante. |
| **Señal** | En este contexto, objeto de datos estructurado que codifica una interpretación semiótica de una entrada bruta del registro. |
| **Registro Amcache** | Unidad de datos tipo fila extraída de Amcache.hve que representa una instancia de ejecución de un programa. |
| **Registro ShimCache** | Unidad de datos de ShimCache que representa una verificación de compatibilidad o ejecución intentada de un programa. |

## 【Nota Científica】
El vocabulario analítico de este módulo proviene de los marcos semióticos de **Charles Sanders Peirce**, **Umberto Eco** y **H. Paul Grice**. Esto no es misticismo ni crítica literaria. Es un sistema de notación formal—funcionalmente equivalente al álgebra de calibración utilizada en el diseño de sensores físicos.

Piense en una entrada bruta del registro como la salida eléctrica de un fotodetector no calibrado. El modelo triádico de Peirce (signo, objeto, interpretante) proporciona el diagrama de cableado que nos dice *qué* se mide, *cómo* se refiere al programa real y *qué* debe concluir el investigador. Los códigos de Eco gobiernan cómo el patrón binario se decodifica en un mensaje técnicamente significativo (la ruta del archivo, el hash, la marca temporal). Los máximas cooperativas de Grice funcionan como filtros de reducción de ruido: detectan **fracturas lógicas**—afirmaciones que violan los patrones esperados de comportamiento racional del sistema, como una entrada de malware fingiendo ser un proceso legítimo.

El método `to_signal()` es, por tanto, el convertidor analógico-digital de este sensor forense. Produce una lectura exacta, de valor entero determinista, a partir de un estímulo binario bruto de tipo analógico.

---

РУССКИЙ:
# РУССКИЙ

## Что представляет собой этот модуль?
Этот модуль — цифровой судебный интерпретатор для двух системных журналов Windows: **Amcache.hve** и **ShimCache** (также известного как AppCompatCache). Простым языком, он работает как лабораторный прибор, считывающий два различных журнала событий, которые операционная система Windows оставляет при каждом запуске программы — даже когда ОС лишь *рассматривает* возможность запуска.

- **Amcache** действует как полный реестр исполнений: каждая действительно запущенная программа, включая вредоносное ПО, оставляет здесь след.
- **ShimCache** действует как реестр намерений: в нём перечислены программы, которые Windows подготовила к запуску, независимо от того, завершился ли запуск успешно или неудачно.

Модуль преобразует необработанные двоичные записи реестра в структурированные, читаемые судебные результаты без использования неточной арифметики с плавающей запятой. Каждое числовое значение хранится в виде точного целого числа или рациональной дроби (при необходимости сериализуется как текст), гарантируя, что метрики доказательств остаются детерминированными и воспроизводимыми при повторных анализах.

## Ключевые понятия

| Понятие | Описание | Роль в анализе |
|---------|----------|----------------|
| **Amcache.hve** | Улей реестра Windows, регистрирующий метаданные всех выполненных приложений (путь, SHA1, дата установки, временная метка последнего запуска). | Первичный источник доказательств подтверждённых событий исполнения. |
| **ShimCache / AppCompatCache** | Кэш совместимости, хранящийся в улье SYSTEM реестра; регистрирует программы, которые Windows отобразила для исполнения, включая неудавшиеся попытки. | Вторичный источник доказательств намерений и обнаружения антифorenзики. |
| **Детерминированная целочисленная арифметика** | Политика вычислений, запрещающая числа с плавающей запятой. Все метрики используют точные целые числа или объекты `Fraction`, устраняя ошибки округления. | Гарантирует побитовую воспроизводимость числовых доказательств. |
| **Сигнал** (через `to_signal()`) | Нормализованная, интерпретируемая единица доказательства, полученная из необработанной записи реестра. Аналогична обработанному показанию датчика. | Мост между сырыми данными и аналитическими выводами. |
| **Надёжность артефакта** | Балл доверия, присваиваемый классу исходного артефакта, определяемый константой и выраженный в виде точной рациональной дроби. | Оценивает уровень доверия к извлечённым записям. |
| **Программы из чёрного списка** | Курируемый реестр сигнатур известных вредоносных программ. | Обеспечивает автоматическую маркировку высокорискованных исполнений. |

## Глоссарий

| Термин | Определение |
|--------|-------------|
| **Улей реестра (Registry Hive)** | Логическая группа верхнего уровня внутри реестра Windows, аналогичная отдельному картотечному шкафу, содержащему записи конфигурации системы. |
| **SHA1** | Криптографическая хеш-функция, производящая 160-битный дайджест; используется здесь как детерминистический отпечаток файла. |
| **Судебный артефакт** | Любой цифровой объект с потенциальной доказательственной ценностью — здесь конкретные структуры реестра, оставленные активностью ОС. |
| **Детерминированная система** | Процесс, при котором идентичные входные данные всегда дают идентичные выходные, без случайности или неопределённости округления. |
| **Дробь (рациональное число)** | Отношение двух целых чисел (например, 3/4), хранимое точно, избегая присущей десятичному представлению с плавающей запятой аппроксимации. |
| **Сигнал** | В данном контексте — структурированный объект данных, кодирующий семиотическую интерпретацию необработанной записи реестра. |
| **Запись Amcache** | Единичная строчная единица данных, извлечённая из Amcache.hve, представляющая один экземпляр исполнения программы. |
| **Запись ShimCache** | Единичная единица данных из ShimCache, представляющая проверку совместимости или попытку исполнения программы. |

## 【Научное Примечание】
Аналитическая терминология этого модуля восходит к семиотическим рамкам **Чарльза Сандерса Пирса**, **Умберто Эко** и **Х. Пола Грайса**. Это не мистицизм и не литературная критика. Это формальная система обозначений — функционально эквивалентная калибровочной алгебре, применяемой при проектировании физических датчиков.

Представьте необработанную запись реестра как электрический выход некалиброванного фотодетектора. Триадическая модель Пирса (знак, объект, интерпретант) предоставляет монтажную схему, сообщающую, *что* измеряется, *как* это относится к реальной программе и *какой* вывод должен сделать исследователь. Коды Эко регулируют, как двоичный шаблон декодируется в технически значимое сообщение (путь к файлу, хеш, временная метка). Кооперативные максимы Грайса служат фильтрами подавления шума: они обнаруживают **логические разрывы** — утверждения, нарушающие ожидаемые паттерны рационального поведения системы, например, запись вредоносного ПО, выдающая себя за легитимный системный процесс.

Таким образом, метод `to_signal()` является аналого-цифровым преобразователем этого судебного датчика. Он производит точное, детерминированное целочисленное показание из аналогоподобного сырого двоичного стимула.

---

中文:
# 中文

## 这是什么模块？
本模块是针对两个 Windows 系统日志的取证解析器：**Amcache.hve** 与 **ShimCache**（亦称 AppCompatCache）。用通俗的语言来说，它如同一台实验室仪器，读取 Windows 操作系统在每次程序启动时——甚至在操作系统仅*考虑*启动程序时——留下的两份不同的事件记录。

- **Amcache** 相当于完整的执行总账：所有实际运行过的程序（包括恶意软件）都会在此留下痕迹。
- **ShimCache** 相当于意图总账：它列出了 Windows 准备运行的程序，无论该启动最终成功还是失败。

本模块将原始的二进制注册表项转换为结构化、可读的取证结果，并且不使用不精确的浮点运算。每个数值均以精确整数或有理分数形式存储（必要时以文本序列化），从而确保证据指标在重复分析中保持确定性与可复现性。

## 核心概念

| 概念 | 说明 | 分析中的作用 |
|------|------|------------|
| **Amcache.hve** | Windows 注册表配置单元，记录所有已执行应用程序的元数据（路径、SHA1、安装日期、上次运行时间戳）。 | 确认执行事件的主要证据来源。 |
| **ShimCache / AppCompatCache** | 存储在 SYSTEM 注册表配置单元中的兼容性缓存；记录 Windows 映射为待执行的程序，包括失败的尝试。 | 意图识别与反取证检测的次要证据来源。 |
| **确定性整数运算** | 禁止浮点数的计算策略。所有指标使用精确整数或 `Fraction` 对象，消除舍入误差。 | 保证数值证据的逐位可复现性。 |
| **信号**（通过 `to_signal()`） | 从原始注册表项中提取的规范化、可解释的证据单元。类似于经处理的传感器读数。 | 连接原始数据与分析结论的桥梁。 |
| **取证工件可信度** | 赋予该取证工件类别的常量信任评分，以精确有理分数表示。 | 衡量提取记录的置信水平。 |
| **黑名单程序** | 已知恶意程序签名的精选列表。 | 实现高风险执行的自动标记。 |

## 术语表

| 术语 | 定义 |
|------|------|
| **注册表配置单元 (Registry Hive)** | Windows 注册表中的顶层逻辑组，类似于存放系统配置记录的独立文件柜。 |
| **SHA1** | 一种产生 160 位摘要的加密散列函数；此处用作文件的确定性指纹。 |
| **取证工件** | 任何具有潜在证据价值的数字对象——此处指操作系统活动留下的特定注册表结构。 |
| **确定性系统** | 相同输入始终产生相同输出的过程，不存在随机性或舍入不确定性。 |
| **分数（有理数）** | 两个整数的比值（例如 3/4），被精确存储，避免浮点十进制表示固有的近似误差。 |
| **信号** | 在本语境中，指对原始注册表项进行符号学解释后编码而成的结构化数据对象。 |
| **Amcache 记录** | 从 Amcache.hve 中提取的单条类行数据单元，代表一次程序执行实例。 |
| **ShimCache 记录** | 来自 ShimCache 的单条数据单元，代表一次程序兼容性检查或尝试执行。 |

## 【科学说明】
本模块的分析术语借鉴了 **查尔斯·桑德斯·皮尔士**、**艾柯** 与 **格赖斯** 的符号学框架。这不是神秘主义，也不是文学批评，而是一种形式化符号系统——在功能上等同于物理传感器设计中所使用的校准代数。

请将原始注册表项想象为一台未校准光电探测器的电信号输出。皮尔士的三元模型（符号、客体、解释项）提供了接线图，告诉我们*测量的是什么*、*它如何指涉真实世界的程序*，以及*调查人员应当得出什么结论*。艾柯的编码规则支配着二进制模式如何被解码为具有技术意义的信息（文件路径、散列值、时间戳）。格赖斯的合作原则则充当降噪滤波器：它们检测**逻辑断裂**——即违背系统理性行为预期模式的陈述，例如恶意软件条目伪装成合法系统进程。

因此，`to_signal()` 方法就是该取证传感器的模数转换器。它从类似模拟信号的原始二进制刺激中产生精确的、确定性的整数值读数。

---

License line must appear. Probably at the very end or per section? User says "License line: ''" I can put it at the bottom of the document, maybe once, but to be safe and thorough, perhaps include it at the end of each section or once globally. The user didn't specify once or per section, but since it's a document, once at the bottom is fine. However, to be thorough, I could place it at the end of each language section or as a final footer. I'll put it as a final footer in all four languages or a single line. Since the languages are separate, maybe include it under each. But that might be repetitive. A single centered footer at the end. But requirement says "Each section must include..." but the license line is a separate requirement. I'll add it at the very bottom once, or under each section. Let's add it at the very end, perhaps in a neutral block. Actually, to be safe and ensure compliance, I'll include it at the bottom of each language section. Wait, requirement 5 says "License line: ..." not necessarily per section. But requirement 3 says each section must include specific items. License is not in that list. So one global footer is fine. I'll make a final block.

Need to ensure no floating-point math explanations. I used "floating-point" in the text to say we avoid it. That's fine. I emphasized deterministic integer arithmetic.

Need to ensure Chinese translations use:
- 艾柯 (done)
- 格赖斯 (done)
- 取证工件 (done)
- 逻辑断裂 (done)

Check Chinese: I used 逻辑断裂 in the scientific note. Good.

Check no mysticism: used sensor analogy. Good.

Tables: must be in markdown. Good.

Need to mention classes and functions. I described them in concepts and glossary. Maybe I should be explicit about the classes in the "What is this module?" or in the table. Let me check.

User wants documentation for the module. I have mentioned:
- AmcacheRecord -> Amcache 记录 / Registro Amcache / Запись Amcache / Amcache Record
- ShimcacheRecord -> ShimCache 记录 / Registro ShimCache / Запись ShimCache / ShimCache Record
- AmcacheAnalysisResult -> I didn't explicitly name it. Should I? The module includes classes. In the key concepts table, I can add rows for the classes.

Add rows:

| **AmcacheRecord** | A data class representing one extracted entry from the Amcache.hve artifact. | Encapsulates program path, SHA1, and execution timestamps as deterministic fields. |
| **ShimcacheRecord** | A data class representing one extracted entry from the ShimCache artifact. | Encapsulates compatibility metadata and execution intent flags. |
| **AmcacheAnalysisResult** | A container object aggregating all processed records and derived conclusions. | Presents the final, reproducible evidentiary report to the investigator. |
| **AmcacheShimcacheAnalyzer** | The primary engine class that orchestrates reading, parsing, and cross-referencing both artifacts. | Executes the deterministic analysis pipeline. |
| **to_signal()** | A normalization function that converts a raw binary registry entry into a structured semiotic signal. | Performs the initial analog-to-digital transformation of evidence. |
| **analyze()** | The main pipeline entry point that drives the entire Amcache/ShimCache interpretation workflow. | Returns an AmcacheAnalysisResult containing exact integer-based metrics. |

This will make it more complete.

Also mention constants:
- TOOL_NAME: String constant identifying the software component.
- ARTIFACT_RELIABILITY: Rational constant scoring the inherent trustworthiness of the artifact source.
- BLACKLISTED_PROGRAMS: Constant dataset of known-bad signatures.

I will integrate these into the table or glossary.

English Table update:
Add rows for the classes/functions/constants.

Concepts table might get long. That's okay. Let's make it comprehensive.

Revised English Key Concepts:

| Concept | Description | Role in Analysis |
|---------|-------------|------------------|
| **Amcache.hve** | ... | ... |
| **ShimCache / AppCompatCache** | ... | ... |
| **AmcacheRecord** | Data class holding one entry from Amcache: program path, SHA1 hash, install time, last run time. | Encapsulates a single confirmed execution event as a deterministic record. |
| **ShimcacheRecord** | Data class holding one entry from ShimCache: file path, execution flag, compatibility data. | Encapsulates a single intent or attempted execution event. |
| **AmcacheAnalysisResult** | Aggregate container for all parsed records, cross-references, and final metrics. | Delivers the complete, reproducible evidentiary report. |
| **AmcacheShimcacheAnalyzer** | Orchestrator class that reads both registry artifacts and runs the analysis pipeline. | Drives end-to-end processing without floating-point approximations. |
| **to_signal()** | Function translating a raw registry byte sequence into a normalized evidence unit. | Acts as the analog-to-digital converter for raw forensic input. |
| **analyze()** | Primary workflow function invoked to perform the full Amcache/ShimCache investigation. | Returns an `AmcacheAnalysisResult` with exact integer and fractional metrics. |
| **TOOL_NAME** | Constant string identifier for this forensic component. | Labels output provenance. |
| **ARTIFACT_RELIABILITY** | Constant rational score representing the base trustworthiness of these artifact types. | Used to weight evidence deterministically via integer fractions. |
| **BLACKLISTED_PROGRAMS** | Constant set of signatures identifying known malicious software. | Flags high-risk entries automatically during parsing. |
| **Deterministic Integer Arithmetic** | Policy forbidding floating-point numbers; all metrics use exact integers or `Fraction`. | Guarantees bitwise-reproducible evidence metrics. |

Similarly for other languages.

ESPAÑOL:
- AmcacheRecord -> RegistroAmcache (but class name stays AmcacheRecord). I'll explain.
- ShimcacheRecord -> RegistroShimcache
- AmcacheAnalysisResult -> ResultadoAnálisisAmcache (or keep class name and explain).
- AmcacheShimcacheAnalyzer -> AnalizadorAmcacheShimcache
- to_signal() -> to_signal()
- analyze() -> analyze()
- TOOL_NAME -> NOMBRE_HERRAMIENTA? No, constant name stays. I'll describe.
- ARTIFACT_RELIABILITY -> CONFIABILIDAD_ARTEFACTO
- BLACKLISTED_PROGRAMS -> PROGRAMAS_LISTA_NEGRA

Russian:
- AmcacheRecord -> запись Amcache
- ShimcacheRecord -> запись ShimCache
- etc.

Chinese:
- AmcacheRecord -> Amcache 记录类
- ShimcacheRecord -> ShimCache 记录类
- AmcacheAnalysisResult -> Amcache 分析结果类
- AmcacheShimcacheAnalyzer -> Amcache-ShimCache 分析器类
- to_signal() -> to_signal() 函数
- analyze() -> analyze() 函数
- TOOL_NAME -> TOOL_NAME 常量
- ARTIFACT_RELIABILITY -> ARTIFACT_RELIABILITY 常量
- BLACKLISTED_PROGRAMS -> BLACKLISTED_PROGRAMS 常量

Now check requirement: "Do NOT use floating-point math explanations — emphasize deterministic integer arithmetic where applicable". I have done that.

Also: "FIX P0: Todo valor numérico en evidence dict usa Fraction/str. NUNCA float." I should mention evidence dict uses Fraction or str. I'll mention "Evidence dictionary stores all numeric values as exact `Fraction` objects or their string serialization; floating-point types are strictly prohibited."

Now let's compose the final output. It will be long but the user asked for thorough.

Make sure to use proper Markdown headers. The user wants 4 language sections. I'll separate with horizontal rules or clear headers.

Structure:

# Module Documentation: `vigia/sift/amcache_shimcache.py`

## ENGLISH
...
---
## ESPAÑOL
...
---
## РУССКИЙ
...
---
## 中文
...
---

Actually, the license line is required. I'll put it at the very bottom. And maybe in each section? I'll put it once at the bottom. It's safer to put it once but clearly.

Need to ensure the scientific note box is clearly marked with 【Scientific Note】/【科学说明】etc.

In English, the user said "A 【科学说明】/【Scientific Note】 box". So for English I should use 【Scientific Note】. For Spanish maybe 【Nota Científica】. For Russian 【Научное Примечание】. For Chinese 【科学说明】. This matches.

Let's double-check Chinese terms:
- 艾柯: used.
- 格赖斯: used.
- 取证工件: used in table and glossary? I used 取证工件? Let me check. In the draft I used "取证工件" in the table? I wrote "取证工件可信度" for Artifact Reliability. But for the glossary term "Forensic Artifact", I should use 取证工件. Yes, I used 取证工件. Good.
- 逻辑断裂: used. Good.

Let's refine the Chinese section to ensure natural academic tone.

Chinese:
- "注册表配置单元" for Registry Hive. Good.
- "Amcache.h
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
