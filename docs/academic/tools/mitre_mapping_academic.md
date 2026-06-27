<!--
VIGIA Academic Documentation
Module: 55f58261
Batch ID: vigia-doc-0166-55f58261
Generated: 2026-05-20T14:56:47.880366+00:00
-->

## ENGLISH

### What Is This Module?
The file `vigia/tools/mitre_mapping.py` functions as the **central knowledge hub** of the VIGÍA digital-forensics ecosystem. Its purpose is to translate raw digital evidence into structured, actionable intelligence using the MITRE ATT&CK framework.

Imagine a physical crime laboratory. Investigators collect tangible clues—fingerprints, fibers, or tool marks. This module performs the digital equivalent: it matches **forensic artifacts** (logs, registry keys, memory segments, network packets) against a standardized catalog of adversary behaviors known as **TTPs** (Tactics, Techniques, and Procedures). Once a match is established, the module packages the resulting intelligence into **STIX 2.1** domain objects, enabling seamless exchange with external DFIR platforms such as OpenCTI or SIFT.

Additionally, the module supplies deterministic lookup tables and pre-computed mappings to two internal subsystems:
- **CAIE** (Context-Aware Intelligence Engine), which consumes rich TTP context.
- **PeircePlanner**, which consumes simplified TTP-to-signal mappings to drive semiotic analysis.

### Key Concepts

**Core Entities**

| Concept | Plain-Language Definition | Forensic Role |
|---|---|---|
| **TTP** | A standardized description of an adversary behavior maintained by MITRE. | Answers *what* the attacker did. |
| **Evidence Type** | A categorical label for a class of digital artifact (e.g., Windows Event Log, DNS query). | Answers *what clue* was discovered. |
| **Attack Tactic** | A strategic phase of an intrusion (e.g., Initial Access, Persistence). | Groups related techniques into columns of the ATT&CK matrix. |
| **Confidence Score** | A deterministic integer product of three discrete reliability factors: base severity, evidence reliability, and method reliability. | Quantifies the certainty that a given TTP is truly present. |
| **Spoofability** | The degree to which an evidence type can be deliberately falsified by an adversary. | Assesses risk of false-positive attribution. |
| **STIX 2.1 SDO** | A Structured Threat Information Expression Domain Object. | The standardized envelope used to share threat intelligence. |
| **STIX Bundle** | A deterministic, sorted collection of SDOs packaged for transport. | Ensures interoperability between distinct tools. |
| **CAIE** | Context-Aware Intelligence Engine (VIGÍA analysis subsystem). | Consumes TTP metadata to build investigative context. |
| **PeircePlanner** | VIGÍA planning module that operates on semiotic signals. | Consumes reduced TTP→signal maps to reason about attacker intent. |

**ATT&CK Tactic Constants**

The module exposes the following deterministic tactic labels, corresponding to the standard MITRE ATT&CK matrix columns:

| Constant Label | ATT&CK Tactic Name |
|---|---|
| `RECONNAISSANCE` | Reconnaissance |
| `RESOURCE_DEVELOPMENT` | Resource Development |
| `INITIAL_ACCESS` | Initial Access |
| `EXECUTION` | Execution |
| `PERSISTENCE` | Persistence |
| `PRIVILEGE_ESCALATION` | Privilege Escalation |
| `DEFENSE_EVASION` | Defense Evasion |
| `CREDENTIAL_ACCESS` | Credential Access |
| `DISCOVERY` | Discovery |
| `LATERAL_MOVEMENT` | Lateral Movement |

**Functional Capabilities**

| Capability | Description |
|---|---|
| Retrieve TTP Metadata | Fetches canonical names, descriptions, and IDs for a given MITRE technique. |
| Map Evidence to TTPs | Returns the complete set of techniques historically associated with a specific evidence type. |
| Calculate TTP Confidence | Multiplies three integer-scaled factors (severity, evidence reliability, method reliability) using deterministic integer arithmetic; produces an exact, reproducible score. |
| Assess Spoofability | Computes a rational risk value for an evidence type; if no TTPs are linked, returns a deterministic moderate baseline (exactly one-half) without resorting to floating-point approximations. |
| Convert to STIX SDO | Transforms a VIGÍA forensic artifact into a validated STIX 2.1 Domain Object. |
| Create STIX Indicator | Builds a STIX Indicator object from artifact properties. |
| Assemble STIX Bundle | Aggregates multiple SDOs into a canonical bundle; serialization uses deterministic key ordering to guarantee bitwise reproducibility. |
| Validate STIX Bundle | Verifies the presence of mandatory fields; returns a Boolean validity flag together with a list of specific errors. |
| Export for CAIE | Emits TTP mappings in a format optimized for ingestion by the CAIE engine. |
| Export for Planner | Generates a minimal TTP→signal_type table for consumption by the PeircePlanner module. |

### Glossary

| Term | Definition |
|---|---|
| **Artifact** (取证工件) | Any digital object collected during an investigation: a log file, memory dump, disk image, or packet capture. |
| **Deterministic Integer Arithmetic** | Mathematical operations restricted to whole numbers on fixed scales, eliminating rounding errors and ensuring that every repeated computation yields the exact same result. |
| **Mapping** | A formal, many-to-many association between evidence types and adversary techniques. |
| **MITRE ATT&CK** | A globally accessible knowledge base of adversary tactics and techniques based on real-world observations. |
| **STIX** | Structured Threat Information Expression; a standardized language for cyber-threat intelligence. |
| **TTP** | Tactics, Techniques, and Procedures; the ontology of adversary actions. |
| **Semiotic Signal** | In PeircePlanner, a discrete token that represents a detected TTP, analogous to a digital sensor reading. |

### 【Scientific Note】
> **Semiotics in Forensic Engineering**
>
> The PeircePlanner module employs terminology drawn from Charles Sanders Peirce (sign classification), Umberto Eco (code theory), and H. P. Grice (cooperative principles). These terms are **formal analytical instruments**, not metaphysical or mystical concepts.
>
> To clarify with a physical analogy: Peirce's *sign* is comparable to a **sensor reading**—a discrete token triggered by a measurable physical state. Eco's *code* corresponds to a **calibration table** that translates raw sensor voltages into meaningful engineering units. Grice's *maxims* operate as **noise-filtering heuristics** that discard improbable sensor measurements according to rational consistency rules. Within PeircePlanner, TTP mappings function as deterministic signals routed through a semiotic circuit; the entire process belongs to information theory and forensic engineering, not to mysticism.

---

## ESPAÑOL

### ¿Qué es este módulo?
El archivo `vigia/tools/mitre_mapping.py` actúa como el **centro de conocimiento** del ecosistema forense digital VIGÍA. Su propósito es traducir evidencia digital bruta en inteligencia estructurada y accionable mediante el marco MITRE ATT&CK.

Imagine un laboratorio de criminalística física. Los investigadores recogen pistas tangibles—huellas dactilares, fibras o marcas de herramientas. Este módulo realiza el equivalente digital: empareja **artefactos forenses** (registros, claves de registro, segmentos de memoria, paquetes de red) con un catálogo estandarizado de comportamientos del adversario conocidos como **TTP** (Tácticas, Técnicas y Procedimientos). Una vez establecida la correspondencia, el módulo empaqueta la inteligencia resultante en objetos de dominio **STIX 2.1**, permitiendo el intercambio fluido con plataformas DFIR externas como OpenCTI o SIFT.

Además, el módulo suministra tablas de consulta determinísticas y mapeos precalculados a dos subsistemas internos:
- **CAIE** (Context-Aware Intelligence Engine), que consume contexto TTP enriquecido.
- **PeircePlanner**, que consume mapeos simplificados TTP→señal para impulsar el análisis semiótico.

### Conceptos Clave

**Entidades Principales**

| Concepto | Definición en lenguaje sencillo | Rol forense |
|---|---|---|
| **TTP** | Descripción estandarizada de un comportamiento del adversario, mantenida por MITRE. | Responde *qué* hizo el atacante. |
| **Evidence Type** | Etiqueta categórica para una clase de artefacto digital (p. ej., registro de eventos de Windows, consulta DNS). | Responde *qué pista* fue descubierta. |
| **Attack Tactic** | Fase estratégica de una intrusión (p. ej., Initial Access, Persistence). | Agrupa técnicas relacionadas en columnas de la matriz ATT&CK. |
| **Confidence Score** | Producto entero determinístico de tres factores discretos de fiabilidad: severidad base, fiabilidad de la evidencia y fiabilidad del método. | Cuantifica la certeza de que una TTP dada esté realmente presente. |
| **Spoofability** | Grado en que un tipo de evidencia puede ser falsificado deliberadamente por el adversario. | Evalúa el riesgo de atribución falsa positiva. |
| **STIX 2.1 SDO** | Structured Threat Information Expression Domain Object. | El sobre estandarizado para compartir inteligencia de amenazas. |
| **STIX Bundle** | Colección determinística y ordenada de SDOs empaquetados para transporte. | Garantiza la interoperabilidad entre herramientas distintas. |
| **CAIE** | Context-Aware Intelligence Engine (subsistema de análisis de VIGÍA). | Consume metadatos TTP para construir contexto investigativo. |
| **PeircePlanner** | Módulo de planificación de VIGÍA que opera sobre señales semióticas. | Consume mapas reducidos TTP→signal_type para razonar sobre la intención del atacante. |

**Constantes de Tácticas ATT&CK**

El módulo expone las siguientes etiquetas determinísticas de tácticas, correspondientes a las columnas estándar de la matriz MITRE ATT&CK:

| Etiqueta Constante | Nombre de Táctica ATT&CK |
|---|---|
| `RECONNAISSANCE` | Reconnaissance |
| `RESOURCE_DEVELOPMENT` | Resource Development |
| `INITIAL_ACCESS` | Initial Access |
| `EXECUTION` | Execution |
| `PERSISTENCE` | Persistence |
| `PRIVILEGE_ESCALATION` | Privilege Escalation |
| `DEFENSE_EVASION` | Defense Evasion |
| `CREDENTIAL_ACCESS` | Credential Access |
| `DISCOVERY` | Discovery |
| `LATERAL_MOVEMENT` | Lateral Movement |

**Capacidades Funcionales**

| Capacidad | Descripción |
|---|---|
| Recuperar metadatos de TTP | Obtiene nombres canónicos, descripciones e identificadores para una técnica MITRE dada. |
| Mapear evidencia a TTPs | Devuelve el conjunto completo de técnicas históricamente asociadas a un tipo de evidencia específico. |
| Calcular confianza de TTP | Multiplica tres factores de escala entera (severidad, fiabilidad de evidencia, fiabilidad de método) mediante aritmética entera determinística; produce una puntuación exacta y reproducible. |
| Evaluar spoofability | Calcula un valor de riesgo racional para un tipo de evidencia; si no hay TTPs vinculadas, devuelve una línea basal moderada determinística (exactamente la mitad) sin recurrir a aproximaciones de coma flotante. |
| Convertir a STIX SDO | Transforma un artefacto forense de VIGÍA en un Domain Object STIX 2.1 validado. |
| Crear indicador STIX | Construye un objeto STIX Indicator a partir de las propiedades del artefacto. |
| Ensamblar STIX Bundle | Agrega múltiples SDOs en un bundle canónico; la serialización usa ordenamiento determinístico de claves para garantizar reproducibilidad bit a bit. |
| Validar STIX Bundle | Verifica la presencia de campos obligatorios; retorna una bandera booleana de validez junto con una lista de errores específicos. |
| Exportar para CAIE | Emite mapeos de TTP en un formato optimizado para ingestión por el motor CAIE. |
| Exportar para Planner | Genera una tabla mínima TTP→signal_type para consumo del módulo PeircePlanner. |

### Glosario

| Término | Definición |
|---|---|
| **Artefacto** | Cualquier objeto digital recolectado durante una investigación: archivo de registro, volcado de memoria, imagen de disco o captura de paquetes. |
| **Aritmética Entera Determinística** | Operaciones matemáticas restringidas a números enteros en escalas fijas, eliminando errores de redondeo y asegurando que toda repetición del cálculo produzca exactamente el mismo resultado. |
| **Mapeo** | Asociación formal de muchos a muchos entre tipos de evidencia y técnicas del adversario. |
| **MITRE ATT&CK** | Base de conocimiento de acceso mundial sobre tácticas y técnicas del adversario, fundada en observaciones del mundo real. |
| **STIX** | Structured Threat Information Expression; lenguaje estandarizado para inteligencia de amenazas cibernéticas. |
| **TTP** | Tactics, Techniques, and Procedures; la ontología de las acciones del adversario. |
| **Señal Semiótica** | En PeircePlanner, un token discreto que representa una TTP detectada, análogo a una lectura de sensor digital. |

### 【Nota Científica】
> **Semiótica en Ingeniería Forense**
>
> El módulo PeircePlanner utiliza terminología derivada de Charles Sanders Peirce (clasificación de signos), Umberto Eco (teoría de códigos) y H. P. Grice (principios cooperativos). Estos términos son **instrumentos analíticos formales**, no conceptos metafísicos o místicos.
>
> Para clarificar con una analogía física: el *signo* de Peirce es comparable a una **lectura de sensor**—un token discreto activado por un estado físico medible. El *código* de Eco corresponde a una **tabla de calibración** que traduce voltajes crudos del sensor en unidades de ingeniería significativas. Los *máximas* de Grice operan como **heurísticas de filtrado de ruido** que descartan mediciones de sensor improbables según reglas de consistencia racional. Dentro de PeircePlanner, los mapeos de TTP funcionan como señales determinísticas enrutadas a través de un circuito semiótico; todo el proceso pertenece a la teoría de la información y a la ingeniería forense, no al misticismo.

---

## РУССКИЙ

### Что представляет собой этот модуль?
Файл `vigia/tools/mitre_mapping.py` функционирует как **центральное хранилище знаний** цифровой судебной экосистемы VIGÍA. Его назначение — преобразовывать необработанные цифровые доказательства в структурированную, действенную разведку с использованием фреймворка MITRE ATT&CK.

Представьте себе физическую криминалистическую лабораторию. Следователи собирают осязаемые улики — отпечатки пальцев, волокна или следы инструментов. Этот модуль выполняет цифровой аналог: он сопоставляет **судебные артефакты** (журналы, ключи реестра, сегменты памяти, сетевые пакеты) со стандартизированным каталогом поведений противника, известных как **TTP** (Tactics, Techniques, and Procedures — тактики, техники и процедуры). Установив соответствие, модуль упаковывает полученную разведку в объекты домена **STIX 2.1**, обеспечивая бесшовный обмен с внешними DFIR-платформами, такими как OpenCTI или SIFT.

Кроме того, модуль поставляет детерминированные справочные таблицы и предварительно вычисленные сопоставления двум внутренним подсистемам:
- **CAIE** (Context-Aware Intelligence Engine — контекстно-зависимый разведывательный движок), потребляющий обогащённый контекст TTP.
- **PeircePlanner**, потребляющий упрощённые сопоставления TTP→сигнал для проведения семиотического анализа.

### Ключевые концепции

**Основные сущности**

| Концепция | Определение простым языком | Судебная роль |
|---|---|---|
| **TTP** | Стандартизированное описание поведения противника, поддерживаемое MITRE. | Отвечает на вопрос, *что* сделал злоумышленник. |
| **Evidence Type** | Категориальный ярлык для класса цифровых артефактов (например, журнал событий Windows, DNS-запрос). | Отвечает на вопрос, *какая улика* была обнаружена. |
| **Attack Tactic** | Стратегическая фаза вторжения (например, Initial Access, Persistence). | Группирует связанные техники по столбцам матрицы ATT&CK. |
| **Confidence Score** | Детерминированное целочисленное произведение трёх дискретных факторов надёжности: базовой серьёзности, надёжности доказательств и надёжности метода. | Количественно определяет уверенность в наличии данной TTP. |
| **Spoofability** | Степень, в которой тип доказательств может быть намеренно фальсифицирован противником. | Оценивает риск ложноположительной атрибуции. |
| **STIX 2.1 SDO** | Structured Threat Information Expression Domain Object. | Стандартизированный конверт для обмена разведкой угроз. |
| **STIX Bundle** | Детерминированная, упорядоченная коллекция SDO, упакованных для транспортировки. | Обеспечивает совместимость между различными инструментами. |
| **CAIE** | Context-Aware Intelligence Engine (аналитическая подсистема VIGÍA). | Потребляет метаданные TTP для построения следственного контекста. |
| **PeircePlanner** | Модуль планирования VIGÍA, работающий на семиотических сигналах. | Потребляет сокращённые карты TTP→signal_type для рассуждения о намерениях злоумышленника. |

**Константы тактик ATT&CK**

Модуль предоставляет следующие детерминированные метки тактик, соответствующие стандартным столбцам матрицы MITRE ATT&CK:

| Метка константы | Название тактики ATT&CK |
|---|---|
| `RECONNAISSANCE` | Reconnaissance |
| `RESOURCE_DEVELOPMENT` | Resource Development |
| `INITIAL_ACCESS` | Initial Access |
| `EXECUTION` | Execution |
| `PERSISTENCE` | Persistence |
| `PRIVILEGE_ESCALATION` | Privilege Escalation |
| `DEFENSE_EVASION` | Defense Evasion |
| `CREDENTIAL_ACCESS` | Credential Access |
| `DISCOVERY` | Discovery |
| `LATERAL_MOVEMENT` | Lateral Movement |

**Функциональные возможности**

| Возможность | Описание |
|---|---|
| Получить метаданные TTP | Извлекает канонические имена, описания и идентификаторы для данной техники MITRE. |
| Сопоставить доказательства с TTP | Возвращает полный набор техник, исторически связанных с конкретным типом доказательств. |
| Вычислить уверенность TTP | Перемножает три целочисленно-масштабированных фактора (серьёзность, надёжность доказательств, надёжность метода) с использованием детерминированной целочисленной арифметики; даёт точный, воспроизводимый результат. |
| Оценить spoofability | Вычисляет рациональное значение риска для типа доказательств; если TTP не связаны, возвращает детерминированную умеренную базовую линию (ровно одну вторую) без приближений с плавающей запятой. |
| Преобразовать в STIX SDO | Преобразует судебный артефакт VIGÍA в проверенный объект домена STIX 2.1. |
| Создать индикатор STIX | Создаёт объект STIX Indicator из свойств артефакта. |
| Собрать STIX Bundle | Агрегирует несколько SDO в канонический пакет; сериализация использует детерминированный порядок ключей для обеспечения побитовой воспроизводимости. |
| Проверить STIX Bundle | Верифицирует наличие обязательных полей; возвращает логический флаг действительности вместе со списком конкретных ошибок. |
| Экспортировать для CAIE | Выдаёт сопоставления TTP в формате, оптимизированном для поглощения движком CAIE. |
| Экспортировать для Planner | Генерирует минимальную таблицу TTP→signal_type для потребления модулем PeircePlanner. |

### Глоссарий

| Термин | Определение |
|---|---|
| **Артефакт** | Любой цифровой объект, собранный в ходе расследования: файл журнала, дамп памяти, образ диска или захват пакетов. |
| **Детерминированная целочисленная арифметика** | Математические операции, ограниченные целыми числами на фиксированных шкалах, устраняющие ошибки округления и гарантирующие, что каждое повторное вычисление даёт в точности одинаковый результат. |
| **Сопоставление (Mapping)** | Формальная ассоциация многие-ко-многим между типами доказательств и техниками противника. |
| **MITRE ATT&CK** | Глобально доступная база знаний о тактиках и техниках противника, основанная на реальных наблюдениях. |
| **STIX** | Structured Threat Information Expression; стандартизированный язык для разведки киберугроз. |
| **TTP** | Tactics, Techniques, and Procedures; онтология действий противника. |
| **Семиотический сигнал** | В PeircePlanner — дискретный токен, представляющий обнаруженную TTP, аналогичный показанию цифрового датчика. |

### 【Научное примечание】
> **Семиотика в судебной инженерии**
>
> Модуль PeircePlanner использует терминологию, заимствованную у Чарльза Сандерса Пирса (классификация знаков), Умберто Эко (теория кодов) и Г. П. Грайса (кооперативные принципы). Эти термины являются **формальными аналитическими инструментами**, а не метафизическими или мистическими концепциями.
>
> Для пояснения с физической аналогией: *знак* Пирса сопоставим с **показанием датчика** — дискретным токеном, активируемым измеримым физическим состоянием. *Код* Эко соответствует **таблице калибровки**, которая переводит сырые напряжения датчика в осмысленные инженерные единицы. *Максимы* Грайса работают как **эвристики фильтрации шума**, отбрасывающие маловероятные показания датчика согласно правилам рациональной согласованности. Внутри PeircePlanner сопоставления TTP функционируют как детерминированные сигналы, маршрутизируемые через семиотическую цепь; весь процесс принадлежит теории информации и судебной инженерии, а не мистицизму.

---

## 中文

### 什么是本模块？
`vigia/tools/mitre_mapping.py` 是 VIGÍA 取证系统的中央知识库。它利用 MITRE ATT&CK 框架将原始数字证据转化为结构化情报。可将其视为一个参考图书馆：将犯罪现场发现的线索（数字取证工件）与已知的对手行为（TTP）进行匹配，随后将该情报打包为符合行业标准的 STIX 2.1 对象，以便与 OpenCTI、SIFT 等其他 DFIR 平台共享。

它还为 CAIE 分析引擎和 PeircePlanner 提供确定性的、预先计算的映射，确保所有组件使用同一套语言。

### 核心概念

**主要实体**

| 概念 | 通俗定义 | 取证职能 |
|---|---|---|
| **TTP** | MITRE 维护的对手行为标准化描述。 | 回答攻击者*做了什么*。 |
| **Evidence Type** | 数字取证工件类别的分类标签（如 Windows 事件日志、DNS 查询）。 | 回答*发现了什么线索*。 |
| **Attack Tactic** | 入侵的战略阶段（如初始访问、持久化）。 | 将相关技术分组为 ATT&CK 矩阵的列。 |
| **Confidence Score** | 三个离散可靠性因子的确定性整数乘积：基础严重性、证据可靠性和方法可靠性。 | 量化给定 TTP 确实存在的确定性。 |
| **Spoofability** | 证据类型可被对手故意伪造的程度。 | 评估误报归因风险。 |
| **STIX 2.1 SDO** | 结构化威胁信息表达域对象。 | 共享威胁情报的标准化封装。 |
| **STIX Bundle** | 用于传输的确定性、有序 SDO 集合。 | 确保不同工具间的互操作性。 |
| **CAIE** | 上下文感知情报引擎（VIGÍA 分析子系统）。 | 消费 TTP 元数据构建调查上下文。 |
| **PeircePlanner** | 在符号信号上运行的 VIGÍA 规划模块。 | 消费简化的 TTP→信号映射以推理攻击者意图。 |

**ATT&CK 战术常量**

| 常量标签 | ATT&CK 战术名称 |
|---|---|
| `RECONNAISSANCE` | 侦察 |
| `RESOURCE_DEVELOPMENT` | 资源开发 |
| `INITIAL_ACCESS` | 初始访问 |
| `EXECUTION` | 执行 |
| `PERSISTENCE` | 持久化 |
| `PRIVILEGE_ESCALATION` | 权限提升 |
| `DEFENSE_EVASION` | 防御规避 |
| `CREDENTIAL_ACCESS` | 凭据访问 |
| `DISCOVERY` | 发现 |
| `LATERAL_MOVEMENT` | 横向移动 |

**功能能力**

| 能力 | 描述 |
|---|---|
| 检索 TTP 元数据 | 获取给定 MITRE 技术的规范名称、描述和 ID。 |
| 将证据映射到 TTP | 返回与特定证据类型历史关联的完整技术集合。 |
| 计算 TTP 置信度 | 使用确定性整数运算将三个整数缩放因子相乘；产生精确、可重现的评分。 |
| 评估可伪造性 | 计算证据类型的有理数风险值；若无关联 TTP，则返回确定性中等基线（恰好二分之一），不使用近似计算。 |
| 转换为 STIX SDO | 将 VIGÍA 取证工件转换为经验证的 STIX 2.1 域对象。 |
| 创建 STIX 指标 | 从取证工件属性构建 STIX Indicator 对象。 |
| 组装 STIX Bundle | 将多个 SDO 聚合为规范包；序列化使用确定性键排序以保证按位可重现性。 |
| 验证 STIX Bundle | 验证必填字段是否存在；返回布尔有效性标志及具体错误列表。 |
| 导出供 CAIE 使用 | 以优化格式输出 TTP 映射供 CAIE 引擎摄取。 |
| 导出供 Planner 使用 | 生成最小 TTP→signal_type 表供 PeircePlanner 模块使用。 |

### 术语表

| 术语 | 定义 |
|---|---|
| **取证工件** | 调查期间收集的任何数字对象：日志文件、内存转储、磁盘镜像或数据包捕获。 |
| **确定性整数运算** | 限于固定尺度整数的数学运算，消除舍入误差，确保每次重复计算产生完全相同的结果。 |
| **映射** | 证据类型与对手技术之间的正式多对多关联。 |
| **MITRE ATT&CK** | 基于真实世界观察的对手战术和技术的全球可访问知识库。 |
| **STIX** | 结构化威胁信息表达；网络威胁情报的标准化语言。 |
| **TTP** | 战术、技术和程序；对手行动的本体论。 |
| **符号信号** | 在 PeircePlanner 中，代表检测到的 TTP 的离散标记，类似于数字传感器读数。 |

### 【科学说明】
> **取证工程中的符号学**
>
> PeircePlanner 模块采用了源自查尔斯·桑德斯·皮尔士（符号分类）、翁贝托·艾柯（代码理论）和 H. P. 格赖斯（合作原则）的术语。这些术语是**形式化分析工具**，而非形而上学或神秘主义概念。
>
> 以物理类比加以说明：皮尔士的*符号*类似于**传感器读数**——由可测量物理状态触发的离散标记。艾柯的*代码*对应于**校准表**，将原始传感器电压转换为有意义的工程单位。格赖斯的*准则*充当**噪声过滤启发式**，根据理性一致性规则丢弃不合理的传感器测量值。在 PeircePlanner 中，TTP 映射作为路由通过符号回路的确定性信号发挥作用；整个过程属于信息论和取证工程领域，而非神秘主义。

---

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
