<!--
VIGIA Academic Documentation
Module: 83a57d82
Batch ID: vigia-doc-0035-83a57d82
Generated: 2026-05-20T14:56:47.852099+00:00
-->

# Module Documentation: `vigia/config.py`

## ENGLISH

### What Is This Module?

This module is the **central control registry** for the VIGÍA digital-forensics system. It reads external operating-system parameters—called *environment variables*—and converts them into validated, deterministic runtime settings. Think of it as a laboratory protocol translator: before any analytical instrument (for example, the large-language-model backend) begins processing evidence, this module ensures that every threshold, mode switch, and path is set to an exact, approved value using discrete integer logic and exact string matching. No approximations are introduced.

### Key Concepts

| Concept | Plain-Language Definition | Scientific Relevance |
|---------|--------------------------|---------------------|
| **CONFIG Singleton** | A single, shared instance of the `VigiaConfig` class that persists for the entire program duration. | Guarantees that all subsystems read the same setting simultaneously, eliminating race conditions or contradictory parameters. |
| **Environment Variable Override** | Supplying an external shell variable (e.g., `VIGIA_LLM_BACKEND=anthropic`) to replace the built-in default. | Allows forensic workstations to alter behavior without modifying the source code, preserving chain-of-custody integrity. |
| **Validation Layer** | Pydantic V2 when installed; otherwise, Python `dataclasses` with manual type and range checks. | Rejects malformed inputs before they reach analysis logic. Operates on deterministic integer arithmetic and exact categorical membership; floating-point thresholds are deliberately avoided. |
| **Fallback Strategy** | Graceful degradation to dataclass-based validation when Pydantic is unavailable. | Essential for SIFT and other minimal environments where extra Python packages are prohibited. |
| **Capability Probe (`_PYDANTIC_AVAILABLE`)** | An internal boolean flag that detects whether the Pydantic V2 library is present. | Directs the module to use strict schema validation or to switch to manual dataclass checks without crashing. |

### Glossary of Technical Terms

| Term | Definition |
|------|------------|
| **Singleton** | A design pattern restricting a class to exactly one instance. Analogous to having one master logbook per laboratory. |
| **Environment Variable** | A text-based parameter stored outside the program, typically in the operating-system profile or shell session. |
| **Pydantic** | A third-party validation library that enforces data types using declarative schemas. |
| **Dataclass** | A native Python construct for bundling related data fields with minimal boilerplate code. |
| **SIFT** | *SANS Investigative Forensic Toolkit*—an Ubuntu-based distribution pre-loaded with forensic tools but minimal Python extras. |
| **Deterministic Integer Arithmetic** | Mathematical operations performed exclusively on whole numbers with exact results, avoiding the rounding errors inherent in floating-point representation. |

### 【Scientific Note】 Semiotics, Sensors, and Configuration Integrity

VIGÍA occasionally employs terminology inspired by Charles Sanders **Peirce**, Umberto **Eco**, and H. P. **Grice**. This is not mysticism; it is rigorous information theory cast in semiotic terms. Consider the **sensor analogy**:

1. A physical stimulus (e.g., temperature) strikes a sensor. In Peircean terms, this creates a **sign** (representamen).
2. The analog-to-digital converter translates that stimulus into a **deterministic integer**—an exact count with no floating-point drift.
3. The system interprets that integer via a calibration table. This is **Eco's encyclopedic model**: the integer acquires meaning only within a structured, agreed-upon frame of reference.
4. Finally, the sensor transmits the reading to the logging system following **Grice's cooperative maxims**: it states exactly what is needed, truthfully, relevantly, and without obscurity.

In `vigia/config.py`, an environment variable is the raw stimulus. The module acts as the converter and calibration protocol: it transforms text into validated, discrete settings (integers or categorical strings) and communicates them unambiguously to the rest of the forensic pipeline. The use of semiotic vocabulary underscores that **meaning is constructed through deterministic, verifiable rules**—not through metaphysical speculation.

---

## ESPAÑOL

### ¿Qué es este módulo?

Este módulo es el **registro de control central** del sistema de informática forense VIGÍA. Lee parámetros externos del sistema operativo—llamados *variables de entorno*—y los convierte en configuraciones de ejecución validadas y deterministas. Piense en él como un traductor de protocolos de laboratorio: antes de que ningún instrumento analítico (por ejemplo, el backend de modelo de lenguaje grande) comience a procesar evidencia, este módulo garantiza que cada umbral, interruptor de modo y ruta esté configurado con un valor exacto y aprobado, utilizando lógica discreta de enteros y coincidencia exacta de cadenas. No se introducen aproximaciones.

### Conceptos clave

| Concepto | Definición en lenguaje sencillo | Relevancia científica |
|----------|-------------------------------|----------------------|
| **Singleton CONFIG** | Una única instancia compartida de la clase `VigiaConfig` que persiste durante toda la ejecución del programa. | Garantiza que todos los subsistemas lean el mismo ajuste simultáneamente, eliminando condiciones de competencia o parámetros contradictorios. |
| **Anulación por variable de entorno** | Proporcionar una variable externa del shell (p. ej., `VIGIA_LLM_BACKEND=anthropic`) para reemplazar el valor predeterminado. | Permite que estaciones forenses modifiquen el comportamiento sin alterar el código fuente, preservando la integridad de la cadena de custodia. |
| **Capa de validación** | Pydantic V2 cuando está instalado; de lo contrario, `dataclasses` de Python con comprobaciones manuales de tipo y rango. | Rechaza entradas malformadas antes de que lleguen a la lógica de análisis. Opera exclusivamente con aritmética entera determinista y membresía categórica exacta; se evitan umbrales de coma flotante. |
| **Estrategia de respaldo** | Degradación controlada a validación basada en *dataclasses* cuando Pydantic no está disponible. | Esencial para entornos SIFT y otros minimalistas donde se prohíben paquetes Python adicionales. |
| **Sonda de capacidad (`_PYDANTIC_AVAILABLE`)** | Un indicador booleano interno que detecta si la biblioteca Pydantic V2 está presente. | Dirige el módulo a usar validación estricta de esquema o a cambiar a comprobaciones manuales de *dataclasses* sin bloquearse. |

### Glosario de términos técnicos

| Término | Definición |
|---------|------------|
| **Singleton** | Patrón de diseño que restringe una clase a exactamente una instancia. Análogo a tener un único libro de registro maestro por laboratorio. |
| **Variable de entorno** | Parámetro de texto almacenado fuera del programa, típicamente en el perfil del sistema operativo o sesión del shell. |
| **Pydantic** | Biblioteca de terceros que impone tipos de datos mediante esquemas declarativos. |
| **Dataclass** | Estructura nativa de Python para agrupar campos de datos relacionados con código repetitivo mínimo. |
| **SIFT** | *SANS Investigative Forensic Toolkit*—distribución basada en Ubuntu con herramientas forenses preinstaladas pero con extras de Python mínimos. |
| **Aritmética entera determinista** | Operaciones matemáticas realizadas exclusivamente con números enteros y resultados exactos, evitando los errores de redondeo propios de la representación en coma flotante. |

### 【Nota Científica】 Semiótica, sensores e integridad de la configuración

VIGÍA emplea ocasionalmente terminología inspirada en Charles Sanders **Peirce**, Umberto **Eco** y H. P. **Grice**. Esto no es misticismo; es teoría de la información rigurosa expresada en términos semióticos. Considere la **analogía del sensor**:

1. Un estímulo físico (p. ej., temperatura) incide sobre un sensor. En términos peirceanos, esto crea un **signo** (representamen).
2. El convertidor analógico-digital traduce ese estímulo en un **entero determinista**—un recuento exacto sin deriva de coma flotante.
3. El sistema interpreta ese entero mediante una tabla de calibración. Este es el **modelo enciclopédico de Eco**: el entero adquiere sentido solo dentro de un marco de referencia estructurado y convenido.
4. Finalmente, el sensor transmite la lectura al sistema de registro siguiendo las **máximas cooperativas de Grice**: indica exactamente lo necesario, veraz, relevante y sin oscuridad.

En `vigia/config.py`, una variable de entorno es el estímulo bruto. El módulo actúa como el convertidor y el protocolo de calibración: transforma texto en ajustes discretos validados (enteros o cadenas categóricas) y los comunica sin ambigüedad al resto de la tubería forense. El uso de vocabulario semiótico subraya que **el significado se construye mediante reglas deterministas y verificables**—no mediante especulación metafísica.

---

## РУССКИЙ

### Что это за модуль?

Этот модуль — **центральный реестр управления** цифровой криминалистической системы VIGÍA. Он считывает внешние параметры операционной системы — *переменные среды* — и преобразует их в проверенные, детерминированные настройки времени выполнения. Воспринимайте его как транслятор лабораторного протокола: прежде чем какой-либо аналитический прибор (например, серверная часть большой языковой модели) начнёт обрабатывать доказательства, этот модуль гарантирует, что каждый порог, переключатель режима и путь установлены в точное, утверждённое значение с помощью дискретной целочисленной логики и точного сопоставления строк. Никакие приближения не вводятся.

### Ключевые понятия

| Понятие | Определение простым языком | Научное значение |
|---------|---------------------------|------------------|
| **Одиночка CONFIG** | Единственный общий экземпляр класса `VigiaConfig`, существующий на протяжении всей работы программы. | Гарантирует, что все подсистемы одновременно считывают одинаковую настройку, устраняя состояния гонки или противоречивые параметры. |
| **Переопределение переменной среды** | Задание внешней переменной оболочки (например, `VIGIA_LLM_BACKEND=anthropic`) для замены встроенного значения по умолчанию. | Позволяет криминалистическим станциям изменять поведение без модификации исходного кода, сохраняя целостность цепочки сохранения. |
| **Слой валидации** | Pydantic V2 при наличии; иначе классы данных Python с ручными проверками типа и диапазона. | Отклоняет некорректные входные данные до их попадания в аналитическую логику. Работает исключительно с детерминированной целочисленной арифметикой и точным категориальным членством; пороги с плавающей точкой намеренно исключены. |
| **Резервная стратегия** | Плавная деградация к проверке на основе классов данных при отсутствии Pydantic. | Критически важно для сред SIFT и других минималистичных сред, где дополнительные пакеты Python запрещены или недоступны. |
| **Зонд возможностей (`_PYDANTIC_AVAILABLE`)** | Внутренний булев флаг, проверяющий наличие библиотеки Pydantic V2. | Направляет модуль на использование строгой проверки схемы или переключает на ручные проверки классов данных без аварийного завершения. |

### Глоссарий технических терминов

| Термин | Определение |
|--------|-------------|
| **Одиночка (Singleton)** | Шаблон проектирования, ограничивающий класс ровно одним экземпляром. Аналогия: одна главная лабораторная книга учёта. |
| **Переменная среды** | Текстовый параметр, хранящийся вне программы, обычно в профиле ОС или сеансе оболочки. |
| **Pydantic** | Сторонняя библиотека проверки данных, строго задающая типы с помощью декларативных схем. |
| **Класс данных (Dataclass)** | Встроенная конструкция Python для группировки связанных полей данных с минимальным шаблонным кодом. |
| **SIFT** | *SANS Investigative Forensic Toolkit* — дистрибутив на базе Ubuntu с предустановленными криминалистическими инструментами и минимальным набором Python-пакетов. |
| **Детерминированная целочисленная арифметика** | Математические операции, выполняемые исключительно над целыми числами с точными результатами, избегая ошибок округления, присущих представлению чисел с плавающей запятой. |

### 【Научное Примечание】 Семиотика, датчики и целостность конфигурации

VIGÍA иногда использует терминологию, вдохновлённую Чарльзом Сандерсом **Пирсом**, Умберто **Эко** и Г. П. **Грайсом**. Это не мистицизм; это строгая теория информации в семиотических терминах. Рассмотрим **аналогию с датчиком**:

1. Физический стимул (например, температура) воздействует на датчик. В терминах Пирса это создаёт **знак** (репрезентамен).
2. Аналого-цифровой преобразователь переводит этот стимул в **детерминированное целое число** — точный счёт без плавающей погрешности.
3. Система интерпретирует это целое число через таблицу калибровки. Это **энциклопедическая модель Эко**: целое число приобретает смысл только в рамках структурированной, согласованной системы отсчёта.
4. Наконец, датчик передаёт показание системе регистрации, следуя **кооперативным максимам Грайса**: сообщает именно то, что нужно, правдиво, по существу и без двусмысленности.

В `vigia/config.py` переменная среды — это исходный стимул. Модуль действует как преобразователь и протокол калибровки: он преобразует текст в проверенные дискретные настройки (целые числа или категориальные строки) и однозначно передаёт их остальной части криминалистического конвейера. Использование семиотической лексики подчёркивает, что **смысл конструируется через детерминированные, верифицируемые правила**, а не через метафизические домыслы.

---

## 中文

### 这是什么模块？

本模块是 VIGÍA 数字取证系统的**中央控制注册表**。它读取外部操作系统参数——称为*环境变量*——并将其转换为经过验证的确定性运行时设置。请将其视为实验室协议转换器：在任何分析仪器（例如大语言模型后端）开始处理证据之前，本模块确保每一个阈值、模式开关与路径都通过离散整数逻辑和精确字符串匹配被设置为精确的、经批准的值。不引入任何近似值。

### 核心概念

| 概念 | 通俗定义 | 科学意义 |
|------|---------|---------|
| **CONFIG 单例** | `VigiaConfig` 类的唯一共享实例，在整个程序运行期间持续存在。 | 确保所有子系统同时读取相同设置，消除竞态条件或矛盾参数。 |
| **环境变量覆盖** | 提供外部 shell 变量（如 `VIGIA_LLM_BACKEND=anthropic`）以替换内置默认值。 | 允许取证工作站在不修改源代码的情况下更改行为，保护保管链完整性。 |
| **验证层** | 已安装时使用 Pydantic V2；否则使用 Python `dataclasses` 进行手动类型与范围检查。 | 在输入到达分析逻辑之前拒绝格式错误的输入。仅对确定性整数运算和精确分类成员资格操作；有意避免浮点阈值。 |
| **降级策略** | 当 Pydantic 不可用时，优雅降级为基于 dataclass 的验证。 | 对于禁止额外 Python 包的 SIFT 及其他最小化环境至关重要。 |
| **能力探针（`_PYDANTIC_AVAILABLE`）** | 检测 Pydantic V2 库是否存在的内部布尔标志。 | 指示模块使用严格的模式验证，或在不崩溃的情况下切换至手动 dataclass 检查。 |

### 技术术语表

| 术语 | 定义 |
|------|------|
| **单例模式（Singleton）** | 将类限制为恰好一个实例的设计模式。类比：每个实验室只有一本主记录簿。 |
| **环境变量** | 存储于程序外部（通常在操作系统配置文件或 shell 会话中）的文本参数。 |
| **Pydantic** | 使用声明式模式强制执行数据类型的第三方验证库。 |
| **数据类（Dataclass）** | Python 的原生结构，用于以最少样板代码捆绑相关数据字段。 |
| **SIFT** | *SANS 调查取证工具包*——基于 Ubuntu 的发行版，预装取证工具，但 Python 扩展包极少。 |
| **确定性整数运算** | 仅对整数执行数学运算以获得精确结果，避免浮点表示固有的舍入误差。 |
| **取证工件** | 数字调查链中经过验证的配置参数或可观测的数字痕迹；若配置过程失败，可在证据链中造成逻辑断裂。 |
| **逻辑断裂** | 证据链或推理链中的不连续性；验证层的作用之一即是防止因配置错误引发此类断裂。 |

### 【科学说明】 符号学、传感器与配置完整性

VIGÍA 偶尔会使用源自查尔斯·桑德斯·**皮尔斯**、翁贝托·**艾柯**以及 H. P. **格赖斯**的术语。这不是神秘主义，而是以符号学语言表达的严格信息论。请考虑**传感器类比**：

1. 物理刺激（例如温度）作用于传感器。用皮尔斯的术语来说，这产生了一个**符号**（表征体，representamen）。
2. 模数转换器将该刺激转换为**确定性整数**——精确的计数，不存在浮点漂移。
3. 系统通过校准表解释该整数。这就是**艾柯的百科全书模型**：整数只有在结构化、约定俗成的参照框架内才能获得意义。
4. 最后，传感器将读数传输给记录系统，遵循**格赖斯的合作原则**：如实、相关、清晰、恰当地提供所需信息，毫不含糊。

在 `vigia/config.py` 中，环境变量就是原始刺激。该模块充当 ADC 和校准协议：它将文本转换为经过验证的离散设置（整数或分类字符串），并将其明确地传达给取证流水线的其余部分。如果此过程失败，就会在证据链中造成**逻辑断裂**。因此，经过验证的配置参数本身也是数字调查中的**取证工件**。使用符号学词汇是为了强调：**意义是通过确定性、可验证的规则构建的**——而非形而上学的臆测。

---

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
