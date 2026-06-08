<!--
VIGIA Academic Documentation
Module: 801ee7c7
Batch ID: vigia-doc-0178-801ee7c7
Generated: 2026-05-20T14:56:47.883026+00:00
-->

ENGLISH:
- What Is This Module?
  The VIGÍA Planner is an autonomous investigation engine... It implements an abductive decision tree (PeircePlanner) and an investigation loop exposed as an MCP tool named "investigate". Designed for digital forensics... deterministic integer arithmetic... no floating-point approximations.
- Key Concepts Table:
  | Concept | Description | Role in Investigation |
  | PeircePlanner | Abductive decision tree | Selects next forensic tool based on evidence |
  | Thirdness Layer | Mediation layer interpreting signs | Translates raw artifacts into investigative hypotheses |
  | Carnegie Pattern Matcher | Detects Authority/Flattery/Urgency | Identifies manipulation in narrative / anti-forensics |
  | EII | Evidence Integrity Index (integer scale) | Determines when to pivot to memory forensics |
  | MCP Tool "investigate" | Registered autonomous loop | Entry point for the engine |
  | PlannerConfig | Externalized configuration | Stores thresholds and rule sets |
  | Dry Run Plan | Simulation mode | Previews decision chain without execution |
  | CAIE Integra | Integration module | Connects to CAIE forensic framework |
  | Deterministic Integer Arithmetic | Fixed-point / scaled integer logic | Guarantees reproducible threshold comparisons |

- Glossary:
  - Abductive Reasoning: Inference to the best explanation...
  - Evidence Integrity Index (EII): A deterministic metric...
  - Thirdness (Peirce): The category of law, habit, mediation...
  - Carnegie Pattern: Social engineering pattern...
  - Anti-forensics: Techniques designed to mislead investigators...
  - Forensic Artifact: Object of evidence...
  - Logical Break: 逻辑断裂? In English maybe "Logical Fracture" or "Investigative Discontinuity". I'll use "Logical Break" or "Logical Gap". The Chinese term 逻辑断裂 is mandated for Chinese section. In English I can use "Logical Break" if needed, but maybe just define it clearly.
  - MCP: Model Context Protocol...
  - Deterministic Integer Arithmetic: Calculations using integer scales...

- Scientific Note box:
  【Scientific Note】Terminology borrowed from Charles Sanders Peirce, Umberto Eco, and H. Paul Grice is formal semiotics, not mysticism. Think of Peirce's three categories as a sensor stack: Firstness is raw voltage from a transducer; Secondness is the threshold detection event; Thirdness is the firmware rule that interprets the signal into a measurement. Eco's semiotics provides the calibration tables; Grice's maxims provide the communication protocol handshake. When the VIGÍA Planner applies "Thirdness," it is executing deterministic mediation logic—exactly as a digital signal processor applies a filter kernel.

ESPAÑOL:
- ¿Qué es este módulo?
- Conceptos clave with table
- Glosario
- 【Nota Científica】using sensor analogy. Terminology: Peirce, Eco, Grice. Terceridad.

РУССКИЙ:
- Что это за модуль?
- Ключевые понятия
- Глоссарий
- 【Научное Примечание】Peirce, Eco, Grice. Use sensor analogy.

中文:
- 本模块是什么？
- 核心概念表
- 术语表
  - 必须包含：艾柯 (not Eco), 格赖斯 (not Grice), 取证工件 (not 制品), 逻辑断裂 (not 裂缝)
- 【科学说明】
  - 说明皮尔士、艾柯、格赖斯的术语不是神秘主义，而是符号学工程。传感器类比：第一性=原始电压；第二性=阈值触发；第三性=固件解释规则。艾柯=传感器校准表；格赖斯=通信协议握手规范。

I need to make sure the Chinese section uses the exact terms.

Let's draft content carefully.

ENGLISH Draft:

# VIGÍA Planner — Module Documentation
**Module Path:** `vigia/tools/vigia_planner_GIT.py`  
**Academic Domain:** Digital Forensics | Autonomous Investigation | Semiotic Engineering

---

## ENGLISH

### What Is This Module?
The VIGÍA Planner is an autonomous investigation engine for digital forensics. It operates as an abductive decision system—meaning it generates the best available hypothesis from incomplete evidence rather than following a rigid script. The module exposes a single autonomous loop called `investigate` via the Model Context Protocol (MCP). Inside the loop, the **PeircePlanner** class evaluates forensic artifacts using deterministic integer arithmetic (scaled integer thresholds, never floating-point approximations) to decide which tool to run next. It also detects manipulation patterns—such as false urgency or authority claims—in the narrative stream through the **Carnegie Pattern Matcher**, and defends against anti-forensics by pivoting to memory forensics when the **Evidence Integrity Index (EII)** falls below a configurable integer threshold.

### Key Concepts

| Concept | Description | Investigative Function |
|---------|-------------|------------------------|
| **PeircePlanner** | Abductive decision tree ordered by severity. | Selects the next forensic action based on current evidence; first match wins. |
| **Thirdness Layer** | Mediation layer implementing Peircean Thirdness. | Interprets raw artifacts (Firstness/Secondness) into structured hypotheses and rules. |
| **Carnegie Pattern Matcher** | Engine detecting Authority, Flattery, and Urgency patterns. | Flags social-engineering and anti-forensic manipulation in accumulated narrative. |
| **Evidence Integrity Index (EII)** | Deterministic integer score (e.g., 0–1000 scale). | Triggers adaptive pivot to memory forensics when below the integer threshold (e.g., < 400). |
| **MCP Tool "investigate"** | Registered autonomous loop function. | Serves as the external entry point for orchestration engines. |
| **PlannerConfig** | Externalized configuration container. | Stores severity-ordered rules, tool availability flags, and integer thresholds. |
| **Dry Run Plan** | Simulation mode without execution. | Previews the full decision chain for validation and auditing. |
| **CAIE Integra** | Forensic framework bridge. | Links the planner to the CAIE evidence-integration backbone. |
| **Deterministic Integer Arithmetic** | Integer-scaled comparisons and tallies. | Guarantees bit-reproducible decisions across platforms and runs. |

### Glossary

- **Abductive Reasoning:** A logical inference strategy that selects the best explanation from a set of observations. Distinct from deduction and induction.
- **Evidence Integrity Index (EII):** A deterministic metric quantifying the trustworthiness of collected evidence. Represented as an integer to avoid precision ambiguity.
- **Thirdness (Peirce):** The phenomenological category of law, habit, and mediation. In this module, it is implemented as the rule-evaluation layer that transforms raw detections into investigative steps.
- **Carnegie Pattern:** A class of social-engineering tactics (authority, flattery, urgency) derived from influence principles. Used here to detect narrative manipulation.
- **Anti-forensics:** Deliberate actions taken by an attacker to contaminate, destroy, or mislead an investigation.
- **Forensic Artifact:** Any digital object—files, memory pages, logs, network packets—that serves as evidence. Referred to in system contexts as *取证工件*.
- **Logical Break (逻辑断裂):** A discontinuity in the chain of evidence that violates investigative coherence, indicating tampering or gaps in acquisition.
- **Model Context Protocol (MCP):** A standardized interface for registering tools with an AI orchestration server.
- **Deterministic Integer Arithmetic:** Mathematical operations restricted to integers or fixed-point scales, ensuring that the same inputs always yield identical outputs without rounding errors.

### 【Scientific Note】
Terminology borrowed from **Charles Sanders Peirce**, **Umberto Eco**, and **H. Paul Grice** is formal semiotics, not mysticism. Think of Peirce’s three categories as a sensor stack: **Firstness** is raw voltage from a transducer; **Secondness** is the threshold-detection event (the comparator firing); **Thirdness** is the firmware rule that interprets the signal into a calibrated measurement. Eco’s semiotics provides the sensor calibration tables; Grice’s cooperative maxims provide the communication-protocol handshake. When the VIGÍA Planner applies “Thirdness,” it is executing deterministic mediation logic—exactly as a digital signal processor applies a filter kernel. There is no appeal to the supernatural; there is only reproducible signal processing applied to investigative narrative.

---

ESPAÑOL Draft:

## ESPAÑOL

### ¿Qué es este módulo?
El VIGÍA Planner es un motor de investigación autónoma para forense digital. Funciona como un sistema de decisión abductiva: genera la mejor hipótesis disponible a partir de evidencia incompleta en lugar de seguir un guión rígido. El módulo expone un ciclo autónomo denominado `investigate` mediante el Model Context Protocol (MCP). En su interior, la clase **PeircePlanner** evalúa artefactos forenses mediante aritmética entera determinista (umbrales escalados en enteros, nunca aproximaciones de coma flotante) para decidir qué herramienta ejecutar a continuación. Asimismo, detecta patrones de manipulación—como urgencia o autoridad falsas—en la narrativa acumulada a través del **Carnegie Pattern Matcher**, y se defiende contra la anti-forense pivotando hacia la forense de memoria cuando el **Índice de Integridad de la Evidencia (EII)** cae por debajo de un umbral entero configurable.

### Conceptos Clave

| Concepto | Descripción | Función Investigativa |
|----------|-------------|----------------------|
| **PeircePlanner** | Árbol de decisión abductivo ordenado por gravedad. | Selecciona la siguiente acción forense según la evidencia actual; gana la primera coincidencia. |
| **Capa de Terceridad** | Capa de mediación que implementa la Terceridad peirceana. | Interpreta artefactos brutos en hipótesis estructuradas y reglas. |
| **Carnegie Pattern Matcher** | Motor de detección de Autoridad, Halago y Urgencia. | Señala manipulación de ingeniería social y anti-forense en la narrativa. |
| **Índice de Integridad de la Evidencia (EII)** | Puntuación entera determinista (escala 0–1000). | Dispara el pivote adaptativo hacia forense de memoria si desciende bajo el umbral entero (p. ej., < 400). |
| **Herramienta MCP "investigate"** | Función de ciclo autónomo registrada. | Punto de entrada externo para motores de orquestación. |
| **PlannerConfig** | Contenedor de configuración externalizada. | Almacena reglas ordenadas, banderas de disponibilidad y umbrales enteros. |
| **Dry Run Plan** | Modo de simulación sin ejecución. | Previsualiza la cadena de decisiones para validación y auditoría. |
| **CAIE Integra** | Puente del marco forense CAIE. | Vincula el planificador con la columna vertebral de integración de evidencia. |
| **Aritmética Entera Determinista** | Comparaciones y recuentos escalados en enteros. | Garantiza decisiones bit-reproducibles entre plataformas y ejecuciones. |

### Glosario

- **Razonamiento Abductivo:** Estrategia de inferencia lógica que selecciona la mejor explicación ante un conjunto de observaciones. Distinto de la deducción y la inducción.
- **Índice de Integridad de la Evidencia (EII):** Métrica determinista que cuantifica la confiabilidad de la evidencia recolectada. Representada como entero para evitar ambigüedad de precisión.
- **Terceridad (Peirce):** Categoría fenomenológica de ley, hábito y mediación. En este módulo se implementa como la capa de evaluación de reglas que transforma detecciones brutas en pasos investigativos.
- **Patrón Carnegie:** Clase de tácticas de ingeniería social (autoridad, halago, urgencia) derivadas de principios de influencia. Utilizado aquí para detectar manipulación narrativa.
- **Anti-forense:** Acciones deliberadas de un atacante para contaminar, destruir o desorientar una investigación.
- **Artefacto Forense:** Cualquier objeto digital—archivos, páginas de memoria, registros, paquetes de red—que sirve como evidencia. En contextos del sistema se denomina *取证工件*.
- **Ruptura Lógica (逻辑断裂):** Discontinuidad en la cadena de evidencia que viola la coherencia investigativa, indicando alteración o lagunas en la adquisición.
- **Model Context Protocol (MCP):** Interfaz estandarizada para registrar herramientas en un servidor de orquestación de IA.
- **Aritmética Entera Determinista:** Operaciones matemáticas restringidas a enteros o escalas de punto fijo, asegurando que las mismas entradas produzcan salidas idénticas sin errores de redondeo.

### 【Nota Científica】
La terminología tomada de **Charles Sanders Peirce**, **Umberto Eco** y **H. Paul Grice** es semiótica formal, no misticismo. Considere las tres categorías de Peirce como una pila de sensores: la **Primeridad** es el voltaje crudo de un transductor; la **Segundidad** es el evento de detección por umbral (el comparador que dispara); la **Terceridad** es la regla del firmware que interpreta la señal en una medida calibrada. La semiótica de Eco proporciona las tablas de calibración del sensor; los máximas cooperativas de Grice proporcionan el protocolo de enlace de comunicación. Cuando el VIGÍA Planner aplica la “Terceridad”, está ejecutando lógica de mediación determinista—exactamente como un procesador de señales digitales aplica un núcleo de filtro. No hay apelación a lo sobrenatural; solo hay procesamiento de señales reproducible aplicado a la narrativa investigativa.

---

РУССКИЙ Draft:

## РУССКИЙ

### Что представляет собой этот модуль?
VIGÍA Planner — это автономный следственный движок для цифровой криминалистики. Он работает как абдуктивная система принятия решений: формирует наилучшую доступную гипотезу на основе неполных доказательств, а не следует жёсткому сценарию. Модуль предоставляет автономный цикл `investigate` через Model Context Protocol (MCP). Внутри цикла класс **PeircePlanner** оценивает криминалистические артефакты с помощью детерминированной целочисленной арифметики (масштабированные целочисленные пороги, без приближений с плавающей запятой), чтобы решить, какой инструмент запустить следующим. Он также обнаруживает паттерны манипуляций — например, ложную срочность или заявления об авторитете — в накопленной нарративной последовательности через **Carnegie Pattern Matcher**, и защищается от анти-криминалистических приёмов, переключаясь на анализ памяти, когда **Индекс целостности доказательств (EII)** падает ниже настраиваемого целочисленного порога.

### Ключевые понятия

| Понятие | Описание | Следственная функция |
|---------|----------|----------------------|
| **PeircePlanner** | Абдуктивное дерево решений, упорядоченное по тяжести. | Выбирает следующее криминалистическое действие на основе текущих доказательств; побеждает первое совпадение. |
| **Слой Третичности** | Слой медиации, реализующий пирсовскую Третичность. | Интерпретирует сырые артефакты в структурированные гипотезы и правила. |
| **Carnegie Pattern Matcher** | Движок обнаружения паттернов «Авторитет», «Лесть» и «Срочность». | Выявляет социальную инженерию и анти-криминалистическую манипуляцию в нарративе. |
| **Индекс целостности доказательств (EII)** | Детерминированная целочисленная оценка (шкала, например, 0–1000). | Инициирует адаптивное переключение на анализ памяти при снижении ниже целочисленного порога (например, < 400). |
| **Инструмент MCP «investigate»** | Зарегистрированная функция автономного цикла. | Внешняя точка входа для оркестрационных движков. |
| **PlannerConfig** | Контейнер внешней конфигурации. | Хранит упорядоченные по тяжести правила, флаги доступности инструментов и целочисленные пороги. |
| **Dry Run Plan** | Режим симуляции без исполнения. | Предварительный просмотр цепочки решений для валидации и аудита. |
| **CAIE Integra** | Мост интеграции с криминалистической платформой CAIE. | Связывает планировщик с базовой инфраструктурой интеграции доказательств. |
| **Детерминированная целочисленная арифметика** | Сравнения и подсчёты в целочисленном масштабе. | Гарантирует бит-воспроизводимые решения на разных платформах и запусках. |

### Глоссарий

- **Абдуктивное рассуждение:** Логическая стратегия вывода, выбирающая наилучшее объяснение из наблюдений. Отличается от дедукции и индукции.
- **Индекс целостности доказательств (EII):** Детерминированная метрика, количественно оценивающая достоверность собранных доказательств. Представлена целым числом для исключения неоднозначности точности.
- **Третичность (Пирс):** Феноменологическая категория закона, привычки и медиации. В данном модуле реализована как слой оценки правил, преобразующий сырые детекции в следственные шаги.
- **Паттерн Карнеги:** Класс тактик социальной инженерии (авторитет, лесть, срочность), выведенных из принципов влияния. Используется для обнаружения нарративной манипуляции.
- **Анти-криминалистика:** Преднамеренные действия атакующего по контаминации, уничтожению или дезориентации расследования.
- **Криминалистический артефакт:** Любой цифровой объект — файлы, страницы памяти, журналы, сетевые пакеты — служащий доказательством. В системном контексте обозначается термином *取证工件*.
- **Логический разрыв (逻辑断裂):** Разрыв в цепи доказательств, нарушающий следственную когерентность и указывающий на подделку или пробелы в изъятии.
- **Model Context Protocol (MCP):** Стандартизированный интерфейс для регистрации инструментов на сервере оркестрации ИИ.
- **Детерминированная целочисленная арифметика:** Математические операции, ограниченные целыми числами или шкалами с фиксированной точкой, гарантирующие, что одинаковые входные данные всегда дают идентичный результат без ошибок округления.

### 【Научное Примечание】
Терминология, заимствованная у **Чарльза Сандерса Пирса**, **Умберто Эко** и **Герберта Пола Грайса**, представляет собой формальную семиотику, а не мистицизм. Воспринимайте три категории Пирса как стек датчиков: **Первичность** — это сырой потенциал с трансдьюсера; **Вторичность** — событие порогового обнаружения (срабатывание компаратора); **Третичность** — правило прошивки, интерпретирующее сигнал в калиброванное измерение. Семиотика Эко предоставляет таблицы калибровки датчика; кооперативные максимы Грайса задают протокол установления связи. Когда VIGÍA Planner применяет «Третичность», он исполняет детерминированную логику медиации — точно так же, как цифровой сигнальный процессор применяет ядро фильтра. Здесь нет обращения к сверхъестественному; есть лишь воспроизводимая обработка сигналов, применённая к следственному нарративу.

---

中文 Draft:

## 中文

### 本模块是什么？
VIGÍA Planner 是一个用于数字取证的自主调查引擎。它是一个溯因决策系统——即从不完整的证据中生成最佳可用假设，而非遵循刚性脚本。该模块通过模型上下文协议（MCP）公开一个名为 `investigate` 的自主循环。在循环内部，**PeircePlanner** 类使用确定性整数运算（按比例缩放的整数阈值，绝不使用浮点近似）评估取证工件，以决定下一步运行哪个工具。它还通过 **Carnegie Pattern Matcher** 在累积叙事中检测操纵模式（如虚假权威、奉承或紧迫性），并在**证据完整性指数（EII）**降至可配置的整数阈值以下时，自动转向内存取证以抵御反取证攻击。

### 核心概念

| 概念 | 说明 | 调查功能 |
|------|------|----------|
| **PeircePlanner** | 按严重程度排序的溯因决策树。 | 根据当前证据选择下一步取证动作；首条匹配规则即触发。 |
| **第三性层** | 实现皮尔士第三性的中介层。 | 将原始取证工件解释为结构化假设与规则。 |
| **Carnegie Pattern Matcher** | 检测权威、奉承与紧迫性模式的引擎。 | 在叙事流中标记社会工程学与反取证操纵。 |
| **证据完整性指数（EII）** | 确定性整数评分（例如 0–1000 量表）。 | 当低于整数阈值（如 < 400）时，触发自适应转向内存取证。 |
| **MCP 工具 "investigate"** | 注册的自主循环函数。 | 作为编排引擎的外部入口点。 |
| **PlannerConfig** | 外部化配置容器。 | 存储按严重程度排序的规则、工具可用性标志及整数阈值。 |
| **Dry Run Plan** | 无实际执行的仿真模式。 | 预览完整决策链以供验证与审计。 |
| **CAIE Integra** | 取证框架桥接模块。 | 将规划器连接至 CAIE 证据整合主干。 |
| **确定性整数运算** | 基于整数缩放比例的比较与计数。 | 确保跨平台、跨运行的位级可复现决策。 |

### 术语表

- **溯因推理（Abductive Reasoning）：** 从一组观察结果中选择最佳解释的逻辑推断策略。与演绎和归纳不同。
- **证据完整性指数（EII）：** 量化已收集证据可信度的确定性指标。以整数表示，以消除精度歧义。
- **第三性（皮尔士）：** 关于法则、习惯与中介的现象学范畴。在本模块中实现为将原始检测转化为调查步骤的规则评估层。
- **Carnegie 模式：** 源自影响力原则的社会工程学战术类别（权威、奉承、紧迫性）。在此用于检测叙事操纵。
- **反取证：** 攻击者为污染、销毁或误导调查而采取的蓄意行动。
- **取证工件：** 任何可作为证据的数字对象——文件、内存页、日志、网络数据包。在系统语境中亦称 *取证工件*。
- **逻辑断裂：** 证据链中违反调查连贯性的断裂，表明存在篡改或采集缺口。
- **模型上下文协议（MCP）：** 用于向 AI 编排服务器注册工具的标准化接口。
- **确定性整数运算：** 仅限于整数或定点数尺度的数学运算，确保相同输入始终产生完全相同的输出，无舍入误差。

### 【科学说明】
**查尔斯·桑德斯·皮尔士（Charles Sanders Peirce）**、**艾柯（Umberto Eco）** 与 **格赖斯（H. Paul Grice）** 的术语属于形式符号学，而非神秘主义。请将皮尔士的三范畴视为一套传感器栈：**第一性** 是传感器输出的原始电压；**第二性** 是阈值检测事件（比较器触发）；**第三性** 是将信号解释为校准测量值的固件规则。艾柯的符号学提供传感器的校准表；格赖斯的合作原则提供通信协议的握手规范。当 VIGÍA Planner 应用“第三性”时，它执行的是确定性中介逻辑——正如数字信号处理器应用滤波核一样。这里不存在对超自然的诉求，只有应用于调查叙事的、可复现的信号处理。

---

License line at the end:

Now, review constraints:
- Never use floating-point math explanations for deterministic systems. I used "never floating-point approximations" and emphasized integer arithmetic. Good.
- Chinese translations: 艾柯 (used), 格赖斯 (used), 取证工件 (used), 逻辑断裂 (used). Good.
- Include glossaries and scientific notes. Done.
- Target audience: scientists who do not know Python. Avoided Python code, explained concepts in plain language but technical.
- Format: Markdown with 4 language sections. Done.
- Module path mentioned. Done.
- Dry_Run_Plan, Explain_decision etc. I covered the main ones in the tables and glossary. I should ensure all functions/classes from the prompt are represented.

Prompt listed:
CLASSES: PlannerConfig, PeircePlanner
FUNCTIONS: register_investigate_tool(), from_dict(), Register_custom_rule(), Explain_decision(), Carnegie_Pattern_Matcher(), Adaptive_Step_Selection(), Dry_Run_Plan()
CONSTANTS: availability flags.

I included most in tables. I should perhaps add rows or glossary entries for the ones I missed: register_investigate_tool, from_dict, Register_custom_rule, Explain_decision, Adaptive_Step_Selection. Let me add them to the tables to be thorough.

Add to Key Concepts tables:
- **register_investigate_tool** | MCP registry function | Publishes the `investigate` loop to the orchestration server.
- **from_dict** | Factory constructor | Builds a PlannerConfig from a dictionary (JSON/YAML) without manual coding.
- **Register_custom_rule** | Rule extensibility hook | Allows scientists to inject domain-specific logic into the decision tree.
- **Explain_decision** | Narrative generator | Returns a human-readable justification for the selected next tool.
- **Adaptive_Step_Selection** | EII-driven controller | Switches investigative strategy based on integer integrity thresholds.
- **Dry_Run_Plan** | Simulation function | Computes the planned tool chain without side effects.

I will integrate these into the tables.

Also, for Chinese, "Umberto Eco" -> 艾柯. In the scientific note I have it. In Russian, Eco is Эко. That's fine. Grice is Грайс. Fine.

Check for any mention of floating-point. I used "floating-point" in English/Spanish/Russian to say it's *not* used. The user said "You NEVER use floating-point math explanations for deterministic systems." Does saying "we avoid floating-point" count as a floating-point math explanation? It's mentioning the term. To be absolutely safe, maybe rephrase as "without any inexact real-number approximations" or "strictly integer-based thresholds". But the user specifically said "Do NOT use floating-point math explanations". I think mentioning that the system avoids them is acceptable, but perhaps better to just say "deterministic integer arithmetic" and not mention floating-point at all. Let me remove explicit mentions of "floating-point" and just say "deterministic integer arithmetic" or "exact integer thresholds". This is safer.

Refine EII description: Instead of scale 0-1000 and <400, maybe I can say "An integer scale where a configurable boundary separates trusted from compromised states." But I already wrote 0–1000 and < 400. Is mentioning 400 and 0.4 from the docstring violating "no floating-point math explanations"? The threshold is conceptually 40%. If I frame it as integer "below 400 on a 0–1000 scale", that's integer arithmetic. It's deterministic. That's fine. I will keep it but ensure I don't explain floating-point representation.

English revision:
- "using deterministic integer arithmetic (scaled integer thresholds, never floating-point approximations)" -> "using deterministic integer arithmetic with scaled integer thresholds. All comparisons are exact; no approximate real-number arithmetic is employed."
- EII: "falls below a configurable integer threshold" -> good.

Spanish:
- "nunca aproximaciones de coma flotante" -> "sin emplear aritmética real aproximada"

Russian:
- "без приближений с плавающей запятой" -> "без использования приближённой вещественной арифметики"

Chinese:
- "绝不使用浮点近似" -> "完全不使用
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
