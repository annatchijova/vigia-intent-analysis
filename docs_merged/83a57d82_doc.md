<!--
VIGIA Academic Documentation
Module: 83a57d82
Batch ID: vigia-doc-0035-83a57d82
Generated: 2026-05-20T14:56:47.852099+00:00
-->

ENGLISH:
- Title: Module Documentation: `vigia/config.py`
- What Is This Module?: A central registry that reads operating-system environment variables and converts them into validated, deterministic settings. Like a laboratory protocol that translates raw instrument readings into standardized units before any experiment begins.
- Key Concepts table:
  - CONFIG Singleton | Single shared instance of VigiaConfig | Prevents conflicting settings across the program
  - Environment Variable | External operating-system parameter (e.g., VIGIA_LLM_BACKEND) | Allows deployment-specific changes without editing code
  - Validation Layer | Pydantic V2 or dataclass+manual check | Ensures inputs are exact integers or allowed strings, rejecting ambiguous values
  - Fallback Strategy | Graceful degradation when Pydantic is absent | Supports SIFT workstations with minimal Python libraries
  - Deterministic Resolution | Settings resolved via exact string comparison and integer arithmetic | Guarantees reproducible behavior across executions
- Glossary:
  - Singleton: A design pattern ensuring only one instance exists.
  - Environment Variable: A key-value pair stored in the operating system shell.
  - Pydantic: A library for data validation using type hints.
  - Dataclass: A Python construct for structuring data without custom boilerplate.
  - SIFT: A forensic operating environment with restricted software packages.
  - Deterministic Integer Arithmetic: Exact numerical operations using whole numbers, avoiding IEEE-754 floating-point approximations.
- Scientific Note: Peirce's semiotics, 艾柯's encyclopedia, Grice's maxims. Sensor analogy: A temperature sensor sends a voltage (signifier, Peirce's representamen). The ADC converts it to an integer (deterministic integer arithmetic). The system interprets this via a calibration table (艾柯's interpretant). Grice's cooperative principle ensures the config module communicates settings clearly and without ambiguity. This is engineering, not mysticism.
- License line

ESPAÑOL:
- Similar structure
- Key terms: Configuración Singleton, Variable de Entorno, Capa de Validación, Estrategia de Respaldo, Resolución Determinista
- Glossary: Singleton, Variable de Entorno, Pydantic, Clase de Datos, SIFT, Aritmética Entera Determinista
- Scientific Note: Same concepts, sensor analogy. "No es misticismo". Peirce (signo), Eco (interpretación enciclopédica), Grice (principio cooperativo).
- License line

РУССКИЙ:
- Title: Модуль `vigia/config.py`
- Similar structure
- Terms: Одиночка CONFIG, Переменная среды, Слой валидации, Резервная стратегия, Детерминированное разрешение
- Glossary: Одиночка (Singleton), Переменная окружения, Pydantic, Класс данных, SIFT, Детерминированная целочисленная арифметика
- Scientific Note: Пирс, Эко, Грайс. Аналогия с датчиком. Не мистицизм.
- License line

中文:
- Title: 模块文档：`vigia/config.py`
- Terms: CONFIG单例, 环境变量, 验证层, 降级策略, 确定性解析
- Important: 艾柯 (not Eco), 格赖斯 (not Grice), 取证工件 (not 制品), 逻辑断裂 (not 裂缝)
- Glossary: 单例模式 (Singleton), 环境变量, Pydantic, 数据类 (Dataclass), SIFT取证工作站, 确定性整数运算
- Scientific Note: 皮尔斯、艾柯、格赖斯. 传感器类比. 不是神秘主义.
  - Use 取证工件 if relevant... how? Maybe mention that misconfiguration creates a "逻辑断裂" in the forensic artifact chain? Actually the user said "Chinese translations must use: ... 取证工件 (not 制品), 逻辑断裂 (not 裂缝)". I need to incorporate these terms naturally. Perhaps in the scientific note or glossary.
  - 取证工件: Forensic artifact. Could say the configuration values are themselves 取证工件 in the digital forensics chain.
  - 逻辑断裂: Logical break/fracture. Could say validation prevents 逻辑断裂 in the chain of evidence.
- License line

Sensor analogy details:
- Physical phenomenon → Sensor (Peircean representamen/sign)
- ADC conversion → Deterministic integer value (exact, no floating point)
- Calibration protocol → Eco's encyclopedic interpretation (mapping integer to meaning)
- Communication protocol → Gricean maxims (quantity, quality, relation, manner) ensuring the config module states exactly what is needed, no more, no less, clearly.

This fits perfectly. The note must be boxed with 【科学说明】/【Scientific Note】.

Tables should be clean Markdown.

Actually, looking at the prompt again: "CLASSES: - LLMBackend... The backend is chosen from CONFIG.llm_backend... - VigiaConfig: All VIGÍA runtime settings..."

So LLMBackend is documented elsewhere but its selection is governed by CONFIG. I'll mention this relationship.

Structure:
- ENGLISH section
- ESPAÑOL section
- РУССКИЙ section
- 中文 section

Each starts with a header.

**ENGLISH**

## Module Documentation: `vigia/config.py`

### What Is This Module?
This module is the **central control registry** for the VIGÍA digital forensics system. It reads external operating-system parameters—called environment variables—and converts them into validated, deterministic runtime settings. Think of it as a laboratory protocol translator: before any analytical instrument (such as the LLM backend) begins processing evidence, this module ensures that every dial, threshold, and mode switch is set to an exact, approved value using discrete integer logic and exact string matching. No approximations are introduced.

### Key Concepts

| Concept | Plain-Language Definition | Scientific Relevance |
|---------|--------------------------|---------------------|
| **CONFIG Singleton** | A single, shared instance of the `VigiaConfig` class that lives for the entire program duration. | Guarantees that all subsystems read the same setting simultaneously, eliminating race conditions or contradictory parameters. |
| **Environment Variable** | An external key-value pair supplied by the operating system shell (e.g., `VIGIA_LLM_BACKEND=anthropic`). | Allows forensic workstations to alter behavior without modifying the source code, preserving chain-of-custody integrity. |
| **Validation Layer** | Pydantic V2 when installed; otherwise, Python `dataclasses` with manual type and range checks. | Rejects malformed inputs before they reach analysis logic. Operates exclusively on deterministic integer arithmetic and exact categorical membership; floating-point thresholds are avoided. |
| **Fallback Strategy** | Graceful degradation to dataclass-based validation when Pydantic is unavailable. | Essential for SIFT and other minimal environments where extra Python packages are prohibited or unavailable. |
| **Deterministic Resolution** | Settings are resolved via exact string comparison and integer arithmetic. | Ensures reproducible behavior: identical environment inputs always yield identical internal states, a prerequisite for admissible forensic pipelines. |

### Glossary of Technical Terms

| Term | Definition |
|------|------------|
| **Singleton** | A software engineering pattern restricting a class to exactly one instance. Analogous to having one master logbook per laboratory. |
| **Environment Variable** | A text-based parameter stored outside the program, typically in the operating system profile or shell session. |
| **Pydantic** | A third-party validation library that enforces data types using declarative schemas. |
| **Dataclass** | A native Python structure for bundling related data fields with minimal boilerplate code. |
| **SIFT** | *SANS Investigative Forensic Toolkit*—a Ubuntu-based distribution pre-loaded with forensic tools but minimal Python extras. |
| **Deterministic Integer Arithmetic** | Mathematical operations performed exclusively on whole numbers with exact results, avoiding the rounding errors inherent in IEEE-754 floating-point representation. |

### 【Scientific Note】Semiotics, Sensors, and Configuration Integrity
VIGÍA occasionally employs terminology inspired by Charles Sanders **Peirce**, Umberto **Eco**, and H. P. **Grice**. This is not mysticism; it is rigorous information theory cast in semiotic terms. Consider the **sensor analogy**:

1. A physical stimulus (e.g., temperature) strikes a sensor. In Peircean terms, this creates a **sign** (representamen).
2. The analog-to-digital converter (ADC) translates that stimulus into a **deterministic integer**—an exact count with no floating-point drift.
3. The system interprets that integer via a calibration table. This is **Eco's encyclopedic model**: the integer acquires meaning only within a structured, agreed-upon frame of reference.
4. Finally, the sensor transmits the reading to the logging system following **Grice's cooperative maxims**: it states exactly what is needed, truthfully, relevantly, and without obscurity.

In `vigia/config.py`, an environment variable is the raw stimulus. The module acts as the ADC and calibration protocol: it transforms text into validated, discrete settings (integers or categorical strings) and communicates them unambiguously to the rest of the forensic pipeline. The use of semiotic vocabulary underscores that **meaning is constructed through deterministic, verifiable rules**—not through metaphysical speculation.

---

Now ESPAÑOL. Need to translate accurately.

ESPAÑOL:

### ¿Qué es este módulo?
Registro de control central... lee parámetros externos (variables de entorno) y los convierte en configuraciones deterministas validadas. Protocolo traductor de laboratorio...

Key concepts:
- CONFIG Singleton → Singleton CONFIG / Instancia única compartida
- Variable de Entorno
- Capa de Validación
- Estrategia de Respaldo / Estrategia de degradación controlada
- Resolución Determinista

Glossary:
- Singleton
- Variable de Entorno
- Pydantic
- Dataclass → Clase de datos
- SIFT
- Aritmética Entera Determinista

Scientific Note:
- Peirce, Eco, Grice. Analogía del sensor. No es misticismo. Semiótica.
- Peirce: signo (representamen)
- Eco: modelo enciclopédico
- Grice: máximas cooperativas
- ADC: conversión a entero determinista

License: same.

РУССКИЙ:

### Что это за модуль?
Центральный реестр управления... читает переменные окружения... преобразует в проверенные детерминированные настройки.

Key concepts:
- Одиночка CONFIG / Singleton CONFIG
- Переменная среды
- Слой валидации
- Резервная стратегия / Стратегия отката
- Детерминированное разрешение

Glossary:
- Одиночка (Singleton)
- Переменная окружения / среды
- Pydantic
- Класс данных (Dataclass)
- SIFT
- Детерминированная целочисленная арифметика

Scientific Note:
- Пирс (Peirce), Эко (Eco), Грайс (Grice). Аналогия с датчиком. Не мистицизм.
- Пирс: знак (репрезентамен)
- Эко: энциклопедическая модель
- Грайс: кооперативный принцип и максимы
- АЦП (ADC): преобразование в детерминированное целое

License: same.

中文:

### 这是什么模块？
VIGÍA数字取证系统的中央控制注册表... 读取外部环境变量... 转换为经过验证的确定性运行时设置。

Key concepts:
- CONFIG单例 (Singleton)
- 环境变量
- 验证层
- 降级策略 / 回退策略
- 确定性解析

Must use:
- 艾柯 (Eco)
- 格赖斯 (Grice)
- 取证工件 (forensic artifact) — use in glossary or note
- 逻辑断裂 (logical fracture) — use perhaps in validation context: "防止逻辑断裂"

Glossary:
- 单例模式 (Singleton)
- 环境变量
- Pydantic
- 数据类 (Dataclass)
- SIFT取证工作站
- 确定性整数运算
- 取证工件 (Forensic artifact: digital evidence object in the investigation chain. I need to define it to use the required term.)
- 逻辑断裂 (Logical fracture: a break in the chain of reasoning or evidence custody)

Scientific Note:
- 皮尔斯 (Peirce), 艾柯 (Eco), 格赖斯 (Grice).
- 传感器类比。
- 不是神秘主义。
- 模数转换器 (ADC) 将物理刺激转换为确定性整数。
- 艾柯的百科全书式模型。
- 格赖斯的合作原则。
- Mention 取证工件: the validated config parameters themselves become 取证工件 in the pipeline, and misconfiguration would cause a 逻辑断裂.

【科学说明】
VIGÍA 偶尔会使用源自查尔斯·桑德斯·皮尔斯 (Charles Sanders Peirce)、翁贝托·艾柯 (Umberto Eco) 以及 H. P. 格赖斯 (H. P. Grice) 的术语。这不是神秘主义，而是披着符号学外衣的严格信息论。请考虑**传感器类比**：

1. 物理刺激（例如温度）作用于传感器。用皮尔斯的术语来说，这产生了一个**符号**（表征体，representamen）。
2. 模数转换器 (ADC) 将该刺激转换为**确定性整数**——精确的计数，不存在浮点漂移。
3. 系统通过校准表解释该整数。这就是**艾柯的百科全书模型**：整数只有在结构化、约定俗成的参照框架内才能获得意义。
4. 最后，传感器将读数传输给记录系统，遵循**格赖斯的合作原则**：它如实、相关、清晰、恰当地提供所需信息，毫不含糊。

在 `vigia/config.py` 中，环境变量就是原始刺激。该模块充当 ADC 和校准协议：它将文本转换为经过验证的离散设置（整数或分类字符串），并将其明确地传达给取证流水线的其余部分。如果此过程失败，就会在证据链中造成**逻辑断裂**。因此，经过验证的配置参数本身也是数字调查中的**取证工件**。使用符号学词汇是为了强调：**意义是通过确定性、可验证的规则构建的**——而非形而上学的臆测。

That uses all required terms.

Now let me ensure no floating-point explanations. I should avoid saying things like "converts string to float" or "decimal precision". Instead emphasize "exact string comparison", "integer arithmetic", "categorical matching".

Also, the user mentioned "LLMBackend" in the classes. In the English "What Is This Module", I mentioned it briefly as an analytical instrument. That's fine.

- All os.getenv() calls replaced with CONFIG singleton.
- Pydantic V2 used when available; falls back to dataclasses + manual validation.
- Works without pydantic (SIFT environments).
- Usage example: from vigia.config import CONFIG; if CONFIG.llm_backend == "anthropic": ...
- LLMBackend: thin async wrapper over Anthropic or Ollama APIs (backend chosen from CONFIG.llm_backend)
- VigiaConfig: runtime settings from env vars. Setting env var overrides default.

I should mention the override mechanism in the tables.

Also, need to make sure the constant `_PYDANTIC_AVAILABLE` is mentioned. It's an internal flag. In the glossary, maybe mention it as a capability probe.

- Environment Variable Override
- _PYDANTIC_AVAILABLE flag

For ENGLISH table:
| Concept | Plain-Language Definition | Scientific Relevance |
|---------|--------------------------|---------------------|
| **CONFIG Singleton** | ... | ... |
| **Environment Variable Override** | Setting an external shell variable (e.g., `VIGIA_LLM_BACKEND`) replaces the hard-coded default. | Provides reproducible, documented customization without altering signed source code. |
| **Validation Layer** | ... exact integer arithmetic ... | ... |
| **Fallback Strategy** | ... | ... |
| **Capability Probe (`_PYDANTIC_AVAILABLE`)** | An internal boolean flag testing whether the Pydantic V2 library is installed. | Directs the module to use strict schema validation or to switch to manual dataclass checks. |

Similarly for other languages.

Now, I need to ensure the tone is academic, technical, suitable for scientists who don't know Python. So avoid Python-specific jargon without explanation. Explain "dataclass" simply.

One concern: The user wants "thorough but concise". I'll aim for comprehensive but not overly verbose sections.

Also, the requirement: "You NEVER use floating-point math explanations for deterministic systems." I must check every sentence to ensure I don't accidentally mention floating point as a good thing. I should mention it only to say it's avoided.

Let's construct the final text.

ENGLISH Section:

# ENGLISH

## Module Documentation: `vigia/config.py`

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

### 【Scientific Note】Semiotics, Sensors, and Configuration Integrity
VIGÍA occasionally employs terminology inspired by Charles Sanders **Peirce**, Umberto **Eco**, and H. P. **Grice**. This is not mysticism; it is rigorous information theory cast in semiotic terms. Consider the **sensor analogy**:

1. A physical stimulus (e.g., temperature) strikes a sensor. In Peircean terms, this creates a **sign** (representamen).
2. The analog-to-digital converter translates that stimulus into a **deterministic integer**—an exact count with no floating-point drift.
3. The system interprets that integer via a calibration table. This is **Eco's encyclopedic model**: the integer acquires meaning only within a structured, agreed-upon frame of reference.
4. Finally, the sensor transmits the reading to the logging system following **Grice's cooperative maxims**: it states exactly what is needed, truthfully, relevantly, and without obscurity.

In `vigia/config.py`, an environment variable is the raw stimulus. The module acts as the converter and calibration protocol: it transforms text into validated, discrete settings (integers or categorical strings) and communicates them unambiguously to the rest of the forensic pipeline. The use of semiotic vocabulary underscores that **meaning is constructed through deterministic, verifiable rules**—not through metaphysical speculation.

---

ESPAÑOL Section:

# ESPAÑOL

## Documentación del módulo: `vigia/config.py`

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

### 【Nota Científica】Semiótica, sensores e integridad de la configuración
VIGÍA emplea ocasionalmente terminología inspirada en Charles Sanders **Peirce**, Umberto **Eco** y H. P. **Grice**. Esto no es misticismo; es teoría de la información rigurosa expresada en términos semióticos. Considere la **analogía del sensor**:

1. Un estímulo físico (p. ej., temperatura) incide sobre un sensor. En términos peirceanos, esto crea un **signo** (representamen).
2. El convertidor analógico-digital traduce ese estímulo en un **entero determinista**—un recuento exacto sin deriva de coma flotante.
3. El sistema interpreta ese entero mediante una tabla de calibración. Este es el **modelo enciclopédico de Eco**: el entero adquiere sentido solo dentro de un marco de referencia estructurado y convenido.
4. Finalmente, el sensor transmite la lectura al sistema de registro siguiendo las **máximas cooperativas de Grice**: indica exactamente lo necesario, veraz, relevante y sin oscuridad.

En `vigia/config.py`, una variable de entorno es el estímulo bruto. El módulo actúa como el convertidor y el protocolo de calibración: transforma texto en ajustes discretos validados (enteros o cadenas categóricas) y los comunica sin ambigüedad al resto de la tubería forense. El uso de vocabulario semiótico subraya que **el significado se construye mediante reglas deterministas y verificables**—no mediante especulación metafísica.

---

РУССКИЙ Section:

# РУССКИЙ

## Документация модуля: `vigia/config.py`

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
| **Класс данных (Dataclass)** | Встроенная конструкция Python для
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
