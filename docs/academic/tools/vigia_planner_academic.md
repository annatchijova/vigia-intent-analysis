<!--
VIGIA Academic Documentation
Module: 2a5dbf34
Batch ID: vigia-doc-0177-2a5dbf34
Generated: 2026-05-20T14:56:47.882803+00:00
-->

# Module Documentation: `vigia/tools/vigia_planner.py`

---

## ENGLISH

### What Is This Module?
The VIGÍA Planner (`vigia/tools/vigia_planner.py`) is the reasoning core of an autonomous digital forensics platform. Its purpose is to replace manual decision-making during an investigation with a transparent, repeatable decision engine.

Imagine a laboratory robot that examines physical evidence, decides which analytical instrument to use next (microscope, spectrometer, DNA sequencer), records the result, and then decides again—repeating this cycle until the sample is fully characterized. The VIGÍA Planner performs the equivalent task for digital evidence: it inspects files, logs, and network traces (forensic artifacts), selects the next forensic tool based on what it has learned so far, and stops when the case reaches a defined closure state.

The module offers two modes of operation:
1. **Autonomous Loop** (`autonomous_investigation`): A self-directed cycle that runs without human intervention.
2. **Advisory Mode** (`dry_run_plan`): A simulation that prints the planned decision chain for human auditors without touching any evidence.

### Key Concepts

| Concept | Plain-Language Definition | Role in the Module |
|---------|---------------------------|-------------------|
| **PeircePlanner** | An abductive decision tree that generates the best available hypothesis from observations, then selects the next action to test that hypothesis. | The central reasoning engine. |
| **PlannerConfig** | A structured container for all operational limits and thresholds. No "magic numbers" are buried in the code; every limit is exposed and adjustable. | Guarantees reproducibility across laboratories. |
| **Severity-Ordered Rules** | Decision rules ranked by integer severity (1 = most critical). The planner scans the list and executes the **first** matching rule. | Ensures deterministic, predictable priority. |
| **Deterministic Integer Arithmetic** | All priority rankings, step counters, and match indices use exact integer operations. No rounding, no truncation uncertainty. | Eliminates non-reproducible behavior between runs. |
| **Autonomous Investigation Loop** | A four-stage cycle: (1) observe evidence state, (2) plan next step via the decision tree, (3) execute tool, (4) record result. Repeats until `max_steps` or an entropy threshold is reached. | The main operational workflow. |
| **Tool Registry** | A catalog of available forensic instruments (document analyzers, vision tools, network fetchers) that the planner can invoke. | Supplies the actions the planner can choose. |
| **STIX 2.1 Export** | A standardized JSON bundle format for sharing threat-intelligence and forensic results between organizations. | Output format for interoperability. |
| **Redirect Blockade (_NoRedirect)** | A security filter that forbids all HTTP redirects, preventing the engine from being tricked into attacking cloud metadata services or entering infinite loops. | Protects against SSRF and DoS. |
| **Dry Run** | A trace of the planned tool sequence without executing any binary or touching live evidence. | Used for peer review and audit trails. |

### Glossary of Technical Terms

| Term | Definition |
|------|------------|
| **Abduction** | Inference to the best explanation: given an observation, form the hypothesis that most plausibly accounts for it. |
| **Decision Tree** | A branching model of decisions and their possible consequences, used here to map evidence patterns to tool selections. |
| **Entropy Threshold** | A configured limit on informational disorder; when the case state exceeds this limit, the loop terminates to prevent runaway processing. |
| **Forensic Artifact** | Any digital object—file, log entry, memory fragment, or packet capture—that serves as evidence in an investigation. |
| **MCP (Model Context Protocol)** | A protocol that allows an AI assistant to discover and invoke external tools in a standardized way. |
| **SSRF (Server-Side Request Forgery)** | An attack in which a server is coerced into making unauthorized requests to internal or external resources. |
| **STIX (Structured Threat Information Expression)** | A standardized language for cyber threat intelligence, maintained by OASIS. |

### 【Scientific Note】
The terminology of **Peirce**, **Eco**, and **Grice** is not mysticism. Think of the planner as a laboratory sensor array. Charles Sanders Peirce's "abduction" is merely the firmware routine that generates a working hypothesis when a sensor registers an anomalous reading. Umberto Eco's semiotics supplies the classification matrix for signal types—analogous to a flow cytometer distinguishing cell populations. Paul Grice's conversational maxims operate as noise-suppression filters, discarding irrelevant data exactly as a lock-in amplifier rejects out-of-phase noise. These names label deterministic signal-processing stages, not metaphysical doctrines. The engine proceeds by exact integer comparisons against externalized thresholds; there is no ambiguity, only measurable state transitions.

---

## ESPAÑOL

### ¿Qué es este módulo?
El Planificador VIGÍA (`vigia/tools/vigia_planner.py`) es el núcleo de razonamiento de una plataforma forense digital autónoma. Su propósito es sustituir la toma de decisiones manual durante una investigación por un motor de decisiones transparente y reproducible.

Imagínese un robot de laboratorio que examina evidencia física, decide qué instrumento analítico usar a continuación (microscopio, espectrómetro, secuenciador de ADN), registra el resultado y vuelve a decidir—repitiendo este ciclo hasta caracterizar completamente la muestra. El Planificador VIGÍA realiza la tarea equivalente para evidencia digital: inspecciona archivos, registros y trazas de red (artefactos forenses), selecciona la siguiente herramienta forense según lo aprendido hasta el momento y se detiene cuando el caso alcanza un estado de cierre definido.

El módulo ofrece dos modos de operación:
1. **Bucle autónomo** (`autonomous_investigation`): Ciclo autodirigido que opera sin intervención humana.
2. **Modo asesor** (`dry_run_plan`): Simulación que imprime la cadena de decisiones planificada para auditores humanos sin tocar la evidencia.

### Conceptos clave

| Concepto | Definición en lenguaje sencillo | Rol en el módulo |
|----------|--------------------------------|------------------|
| **PeircePlanner** | Árbol de decisión abductivo que genera la mejor hipótesis disponible a partir de observaciones y selecciona la siguiente acción para probarla. | Motor de razonamiento central. |
| **PlannerConfig** | Contenedor estructurado de todos los límites y umbrales operativos. No hay "números mágicos" ocultos en el código; cada límite está expuesto y ajustable. | Garantiza reproducibilidad entre laboratorios. |
| **Reglas ordenadas por severidad** | Reglas de decisión clasificadas por severidad entera (1 = más crítica). El planificador recorre la lista y ejecuta la **primera** regla coincidente. | Asegura prioridad determinista y predecible. |
| **Aritmética entera determinista** | Todos los rangos de prioridad, contadores de pasos e índices de coincidencia usan operaciones enteras exactas. Sin redondeo ni incertidumbre de truncamiento. | Elimina comportamientos no reproducibles entre ejecuciones. |
| **Bucle de investigación autónoma** | Ciclo de cuatro etapas: (1) observar estado de la evidencia, (2) planificar siguiente paso mediante el árbol de decisión, (3) ejecutar herramienta, (4) registrar resultado. Se repite hasta `max_steps` o un umbral de entropía. | Flujo de trabajo operativo principal. |
| **Registro de herramientas** | Catálogo de instrumentos forenses disponibles (analizadores de documentos, herramientas de visión, recuperadores de red) que el planificador puede invocar. | Suministra las acciones entre las que el planificador puede elegir. |
| **Exportación STIX 2.1** | Formato estandarizado de paquete JSON para compartir inteligencia sobre amenazas y resultados forenses entre organizaciones. | Formato de salida para interoperabilidad. |
| **Bloqueo de redirecciones (_NoRedirect)** | Filtro de seguridad que prohíbe toda redirección HTTP, impidiendo que el motor sea engañado para atacar servicios de metadatos en la nube o entrar en bucles infinitos. | Protege contra SSRF y DoS. |
| **Ejecución en seco (Dry Run)** | Trazado de la secuencia de herramientas planificada sin ejecutar ningún binario ni tocar evidencia activa. | Usado para revisión por pares y auditorías. |

### Glosario de términos técnicos

| Término | Definición |
|---------|------------|
| **Abducción** | Inferencia a la mejor explicación: dada una observación, formar la hipótesis que la explica de manera más plausible. |
| **Árbol de decisión** | Modelo ramificado de decisiones y sus posibles consecuencias, usado aquí para mapear patrones de evidencia a selecciones de herramientas. |
| **Umbral de entropía** | Límite configurado sobre el desorden informacional; cuando el estado del caso lo supera, el bucle termina para evitar procesamiento descontrolado. |
| **Artefacto forense** | Cualquier objeto digital—archivo, entrada de registro, fragmento de memoria o captura de paquetes—que sirve como evidencia en una investigación. |
| **MCP (Model Context Protocol)** | Protocolo que permite a un asistente de IA descubrir e invocar herramientas externas de manera estandarizada. |
| **SSRF (Server-Side Request Forgery)** | Ataque en el que se fuerza a un servidor a realizar solicitudes no autorizadas a recursos internos o externos. |
| **STIX (Structured Threat Information Expression)** | Lenguaje estandarizado para inteligencia de amenazas cibernéticas, mantenido por OASIS. |

### 【Nota Científica】
La terminología de **Peirce**, **Eco** y **Grice** no es misticismo. Piense en el planificador como un conjunto de sensores de laboratorio. La "abducción" de Charles Sanders Peirce no es más que la rutina del firmware que genera una hipótesis operativa cuando un sensor registra una lectura anómala. La semiótica de Umberto Eco suministra la matriz de clasificación de tipos de señal—análoga a un citómetro de flujo que distingue poblaciones celulares. Los máximas conversacionales de Paul Grice funcionan como filtros de supresión de ruido, descartando datos irrelevantes exactamente como un amplificador lock-in rechaza el ruido fuera de fase. Estos nombres etiquetan etapas deterministas de procesamiento de señales, no doctrinas metafísicas. El motor avanza mediante comparaciones enteras exactas contra umbrales externalizados; no hay ambigüedad, solo transiciones de estado medibles.

---

## РУССКИЙ

### Что это за модуль?
Планировщик VIGÍA (`vigia/tools/vigia_planner.py`) — это ядро рассуждения автономной платформы цифровой криминалистики. Его назначение — заменить ручное принятие решений в ходе расследования прозрачным и воспроизводимым решательным аппаратом.

Представьте лабораторного робота, который исследует физические доказательства, решает, какой аналитический прибор задействовать следующим (микроскоп, спектрометр, секвенатор ДНК), фиксирует результат и снова принимает решение — повторяя цикл до полной характеризации образца. Планировщик VIGÍA выполняет эквивалентную задачу для цифровых доказательств: он инспектирует файлы, журналы и сетевые следы (артефакты криминалистического анализа), выбирает следующий инструмент на основе накопленных сведений и останавливается при достижении заданного конечного состояния.

Модуль предоставляет два режима работы:
1. **Автономный цикл** (`autonomous_investigation`): Самоуправляемый цикл без вмешательства человека.
2. **Консультативный режим** (`dry_run_plan`): Симуляция, выводящая цепочку планируемых решений для аудиторов без контакта с доказательствами.

### Ключевые концепции

| Концепция | Определение простым языком | Роль в модуле |
|-----------|----------------------------|---------------|
| **PeircePlanner** | Абдуктивное дерево решений, генерирующее наилучшую доступную гипотезу из наблюдений и выбирающее следующее действие для её проверки. | Центральное решающее ядро. |
| **PlannerConfig** | Структурированный контейнер всех операционных ограничений и порогов. В коде не скрыто «магических чисел»; каждый предел вынесен наружу и настраивается. | Гарантирует воспроизводимость между лабораториями. |
| **Правила, упорядоченные по строгости** | Решающие правила, ранжированные по целочисленной строгости (1 = наиболее критично). Планировщик просматривает список и выполняет **первое** подходящее правило. | Обеспечивает детерминированный и предсказуемый приоритет. |
| **Детерминированная целочисленная арифметика** | Все ранги приоритета, счётчики шагов и индексы совпадения используют точные целочисленные операции. Без округления и усечения. | Устраняет невоспроизводимое поведение между запусками. |
| **Цикл автономного расследования** | Четырёхэтапный цикл: (1) наблюдение состояния доказательств, (2) планирование следующего шага через дерево решений, (3) выполнение инструмента, (4) регистрация результата. Повторяется до `max_steps` или порога энтропии. | Основной операционный рабочий процесс. |
| **Реестр инструментов** | Каталог доступных криминалистических инструментов (анализаторы документов, средства визуализации, сетевые загрузчики), которые планировщик может вызывать. | Поставляет действия, доступные планировщику. |
| **Экспорт STIX 2.1** | Стандартизированный JSON-пакет для обмена данными о киберугрозах и результатами криминалистического анализа между организациями. | Выходной формат для интероперабельности. |
| **Блокировка перенаправлений (_NoRedirect)** | Защитный фильтр, запрещающий все HTTP-перенаправления, предотвращающий вынуждение движка к атакам на облачные метаданные или бесконечным циклам. | Защита от SSRF и DoS. |
| **Холостой прогон (Dry Run)** | Трассировка планируемой последовательности инструментов без запуска исполняемых файлов или контакта с живыми доказательствами. | Используется для экспертной проверки и аудиторских следов. |

### Глоссарий технических терминов

| Термин | Определение |
|--------|-------------|
| **Абдукция** | Вывод наилучшего объяснения: имея наблюдение, сформировать гипотезу, которая наиболее правдоподобно его объясняет. |
| **Дерево решений** | Разветвлённая модель решений и их возможных последствий, используемая здесь для сопоставления шаблонов доказательств с выбором инструментов. |
| **Порог энтропии** | Настроенный предел информационного беспорядка; при превышении дело прекращает обработку, чтобы предотвратить неконтролируемый расход ресурсов. |
| **Артефакт криминалистического анализа** | Любой цифровой объект — файл, запись журнала, фрагмент памяти или захват пакета — служащий доказательством в расследовании. |
| **MCP (Model Context Protocol)** | Протокол, позволяющий ИИ-ассистенту обнаруживать и вызывать внешние инструменты стандартизированным образом. |
| **SSRF (Server-Side Request Forgery)** | Атака, в ходе которой сервер вынуждают выполнять несанкционированные запросы к внутренним или внешним ресурсам. |
| **STIX (Structured Threat Information Expression)** | Стандартизированный язык киберразведки, поддерживаемый OASIS. |

### 【Научное примечание】
Терминология **Пирса**, **Эко** и **Грайса** — не мистицизм. Воспринимайте планировщик как лабораторную сенсорную матрицу. «Абдукция» Чарльза Сандерса Пирса — лишь встроенная программа, генерирующая рабочую гипотезу при регистрации аномального показания датчика. Семиотика Умберто Эко предоставляет классификационную матрицу типов сигналов — аналогично проточному цитометру, различающему клеточные популяции. Разговорные максимы Пола Грайса действуют как фильтры подавления шума, отбрасывая нерелевантные данные точно так же, как избирательный усилитель отсекает шум вне фазы. Эти имена обозначают детерминированные стадии обработки сигнала, а не метафизические доктрины. Движок оперирует точными целочисленными сравнениями с внешними порогами; здесь нет двусмысленности — только измеримые переходы состояний.

---

## 中文

### 本模块是什么？
VIGÍA 规划器（`vigia/tools/vigia_planner.py`）是自主数字取证平台的推理核心。其目的是以透明且可重复的决策引擎，替代调查过程中的人工决策。

设想一台实验室机器人：它检查物理检材，决定下一步使用哪种分析仪器（显微镜、光谱仪、DNA 测序仪），记录结果，然后再次决策——循环往复，直到样品被完全表征。VIGÍA 规划器为数字证据执行等效任务：它检查文件、日志和网络痕迹（取证工件），根据迄今获得的信息选择下一步取证工具，并在案件达到既定闭合状态时停止。

本模块提供两种运行模式：
1. **自主调查循环**（`autonomous_investigation`）：无需人工干预的自导向循环。
2. **顾问模式**（`dry_run_plan`）：仅打印计划决策链供人类审计员审阅，不触碰任何证据。

### 核心概念

| 概念 | 通俗定义 | 在模块中的作用 |
|------|----------|----------------|
| **PeircePlanner（皮尔斯规划器）** | 溯因决策树：从观察中生成最佳可用假设，并选择下一步行动以验证该假设。 | 中央推理引擎。 |
| **PlannerConfig（规划器配置）** | 所有运行限制与阈值的结构化容器。代码中不埋藏任何"魔法数字"；每个限制均外露且可调。 | 保证跨实验室的可复现性。 |
| **按严重度排序的规则** | 按整数严重度排序的决策规则（1 = 最严重）。规划器自上而下扫描列表，执行**首个**匹配规则。 | 确保确定性的、可预测的优先级。 |
| **确定性整数运算** | 所有优先级、步数计数器与匹配索引均使用精确的整数运算。无舍入、无截断误差。 | 消除不同运行之间的不可复现行为。 |
| **自主调查循环** | 四阶段循环：(1) 观察证据状态，(2) 通过决策树规划下一步，(3) 执行工具，(4) 记录结果。重复直至达到 `max_steps` 或熵阈值。 | 主要操作流程。 |
| **工具注册表** | 可用取证工具的目录（文档分析器、视觉工具、网络获取工具等），供规划器调用。 | 提供规划器可选的动作集合。 |
| **STIX 2.1 导出** | 用于在组织间共享威胁情报与取证结果的标准化 JSON 包格式。 | 输出格式，保障互操作性。 |
| **重定向阻断（_NoRedirect）** | 禁止所有 HTTP 重定向的安全过滤器，防止引擎被诱骗攻击云元数据服务或陷入无限循环。 | 防御 SSRF 与 DoS。 |
| **空转模拟（Dry Run）** | 仅追踪计划工具序列，不执行任何二进制文件，也不接触实时证据。 | 用于同行评审与审计追踪。 |

### 技术术语表

| 术语 | 定义 |
|------|------|
| **溯因（Abduction）** | 最佳解释推理：给定观察，形成最能合理解释它的假设。 |
| **决策树** | 决策及其可能后果的分支模型，此处用于将证据模式映射到工具选择。 |
| **熵阈值** | 对信息无序程度的配置上限；当案件状态超出此限，循环终止以防止失控处理。 |
| **取证工件** | 任何在调查中作为证据的数字对象——文件、日志条目、内存片段或数据包捕获。 |
| **MCP（模型上下文协议）** | 允许 AI 助手以标准化方式发现与调用外部工具的协议。 |
| **SSRF（服务器端请求伪造）** | 一种攻击，迫使服务器向内部或外部资源发出未授权请求。 |
| **STIX（结构化威胁信息表达式）** | 由 OASIS 维护的网络威胁情报标准化语言。 |

### 【科学说明】
**皮尔斯**、**艾柯** 与 **格赖斯** 的术语并非神秘主义。请将本引擎视为实验室传感器阵列：查尔斯·桑德斯·皮尔斯的"溯因"不过是传感器在检测到异常读数时生成工作假设的固件例程；翁贝托·艾柯的符号学为信号类型提供分类矩阵——类比于流式细胞仪区分细胞群体；保罗·格赖斯的会话准则充当噪声抑制滤波器，滤除无关数据，其原理与锁相放大器剔除异相噪声完全一致。这些名称只是确定性信号处理阶段的工程标签，而非形而上学教条。引擎依据外部化阈值执行精确的整数比较——不存在模糊性，只有可测量的状态跃迁。

---

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
