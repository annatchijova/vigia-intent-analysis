<!--
VIGIA Academic Documentation
Module: e3ae3cf0
Batch ID: vigia-doc-0180-e3ae3cf0
Generated: 2026-05-20T14:56:47.883464+00:00
-->

# Technical Documentation: `vigia/tools/visible_variables.py`

---

## ENGLISH

### What Is This Module?
This module, `vigia/tools/visible_variables.py`, constitutes the deterministic analysis kernel of the VIGIA digital forensics platform. Its purpose is to convert uninterpreted system observations—such as process creation events, network socket states, and filesystem timestamps—into structured, court-admissible evidence objects. The engine accepts only integer arithmetic and lookup-table mappings. It contains no floating-point instructions, no probabilistic thresholds, and no hidden conditional branches. This design satisfies judicial reliability criteria (Daubert standard) by ensuring that every output is reproducible, auditable, and falsifiable.

### Key Concepts and Components

**Table 1: Core Components and Capabilities**

| Component / Capability | Scientific Role | Deterministic Guarantee |
|---|---|---|
| IRPhase | Symbolic taxonomy for NIST SP 800-61 incident response stages | Discrete, immutable constants |
| VariableCategory | Ontological classification of observable properties (temporal, process, network) | Exhaustive enumeration |
| Artifact | Unit of raw forensic observation (Peircean Firstness) | Immutable acquisition record |
| FocusAnalysis | Structured container for analyzed visible variables | `consistency_score`: integer [0, 100] |
| VisibleVariablesEngine | Central processor executing rule satisfaction via lookup tables | Zero floating-point operations |
| AbductiveIntentEngineInterface | Typed boundary for downstream intent-inference engine (Milestone 2.1) | Lossless deterministic channel |
| `analyze_bundle_focus` | Convenience operation for end-to-end bundle analysis | Reproducible pipeline |
| `to_dict` / `to_json` | Serialization for evidence interchange | SHA256-stable output |
| `detect_phase` | Phase classification using exclusive mapping tables | Returns `(IRPhase, integer_score)` |
| `analyze_focus` | Comprehensive focal analysis over a visible variable set | Integer rule-satisfaction counting |
| `infer_habit` | Placeholder for abductive hypothesis generation (Milestone 2.1) | Future deterministic extension |

**Table 2: Daubert Compliance Framework**

| Principle | Module Implementation | Integer Arithmetic Basis |
|---|---|---|
| Determinism | Identical input always yields identical output | `(satisfied_rules × 100) // total_rules` |
| Auditability | Every decision traceable to a public lookup table | No opaque weights or embeddings |
| Reproducibility | SHA256 hash of output invariant across platforms | Absence of float-induced platform variance |
| Falsifiability | Explicit, enumerable rules; no concealed heuristics | Integer score disprovable by single counter-example |

**Table 3: Incident Response Phase Constants (NIST 800-61 Mapping)**

| Constant | Forensic Semantics |
|---|---|
| RECONNAISSANCE | Adversary surveying activity preceding compromise |
| INITIAL_ACCESS | Vector of first unauthorized system entry |
| EXECUTION | Activation of adversary-controlled code |
| PERSISTENCE | Mechanisms maintaining access across sessions |
| PRIVILEGE_ESCALATION | Acquisition of higher-level credentials |
| DEFENSE_EVASION | Anti-forensic or counter-detection behavior |
| CREDENTIAL_ACCESS | Theft or compromise of authentication material |
| DISCOVERY | Internal asset and network enumeration |
| LATERAL_MOVEMENT | Propagation between hosts or segments |
| COLLECTION | Aggregation of data prior to exfiltration |

**Table 4: Integer Scoring Methodology**

| Metric | Exact Formula | Domain |
|---|---|---|
| `consistency_score` | `(satisfied_rules × 100) // total_rules` | Integer interval [0, 100] |
| Phase detection tuple | `(detected_IRPhase, consistency_score)` | Discrete symbol × Integer |

### Glossary of Technical Terms

- **Artifact**: A raw, uninterpreted system observation (e.g., a registry modification, a TCP SYN packet, or a file MAC-time). In semiotics, this corresponds to Peircean *Firstness*: the pure quality of immediate presence, prior to reaction or law.
- **Consistency Score**: An exact integer in the closed interval [0, 100] quantifying the proportion of applicable logical rules that are satisfied. It is computed by integer multiplication and floor division, entirely avoiding fractional representations.
- **Deterministic Lookup Table**: A total function implemented as a fixed mapping from keys to values. Each lookup is reproducible and inspectable; there are no confidence intervals, probability densities, or statistical thresholds.
- **IRPhase**: An object representing a stage in the incident response lifecycle, aligned with NIST SP 800-61r2 guidelines.
- **Visible Variable**: A directly measurable system attribute whose value can be enumerated without interpretive inference (e.g., process ID, source IP address, inode number).
- **Abductive Intent Engine**: A planned analytical subsystem (Milestone 2.1) that will generate inferential hypotheses regarding adversary intent from the deterministic outputs of this module.

### 【Scientific Note】
This module employs terminology rooted in the semiotics of Charles Sanders Peirce (Firstness, Secondness, Thirdness), the cultural coding theory of Umberto Eco, and the cooperative logic of H. P. Grice. These are not mystical or humanistic conceits. Consider a laboratory spectrometer: Peircean *Firstness* is the raw detector voltage before any processing; Eco's codes are the calibration matrices that map voltage to spectral lines; Grice's maxims are the laboratory protocols that prevent selective reporting of data. Here, an **Artifact** is the "raw voltage," the engine's lookup tables constitute the "calibration standard," and the integer `consistency_score` is the "certified measurement." The semiotic vocabulary provides a formal epistemology for deterministic classification, not a metaphysical belief system.

---

## ESPAÑOL

### ¿Qué Es Este Módulo?
Este módulo, `vigia/tools/visible_variables.py`, constituye el núcleo de análisis determinista de la plataforma forense digital VIGIA. Su propósito es convertir observaciones del sistema no interpretadas—tales como eventos de creación de procesos, estados de sockets de red y marcas temporales del sistema de archivos—en objetos de evidencia estructurados y admisibles en tribunales. El motor acepta únicamente aritmética de enteros y mapeos por tablas de búsqueda. No contiene instrucciones de punto flotante, umbrales probabilísticos ni ramas condicionales ocultas. Este diseño satisface los criterios de confiabilidad judicial (estándar Daubert) al garantizar que cada salida sea reproducible, auditable y falsable.

### Conceptos Clave y Componentes

**Tabla 1: Componentes y Capacidades Principales**

| Componente / Capacidad | Rol Científico | Garantía Determinista |
|---|---|---|
| IRPhase | Taxonomía simbólica para las etapas de respuesta a incidentes NIST SP 800-61 | Constantes discretas e inmutables |
| VariableCategory | Clasificación ontológica de propiedades observables (temporal, proceso, red) | Enumeración exhaustiva |
| Artifact (Artefacto) | Unidad de observación forense bruta (Primeridad peirceana) | Registro de adquisición inmutable |
| FocusAnalysis | Contenedor estructurado para variables visibles analizadas | `consistency_score`: entero [0, 100] |
| VisibleVariablesEngine | Procesador central que ejecuta satisfacción de reglas vía tablas | Cero operaciones de punto flotante |
| AbductiveIntentEngineInterface | Frontera tipada para el motor de inferencia de intención (Hito 2.1) | Canal determinista sin pérdida |
| `analyze_bundle_focus` | Operación de conveniencia para análisis completo de un bundle | Pipeline reproducible |
| `to_dict` / `to_json` | Serialización para intercambio de evidencias | Salida estable ante SHA256 |
| `detect_phase` | Clasificación de fase usando tablas de mapeo exclusivas | Retorna `(IRPhase, entero_score)` |
| `analyze_focus` | Análisis focal comprehensivo sobre un conjunto de variables | Conteo entero de reglas satisfechas |
| `infer_habit` | Marcador de posición para generación de hipótesis abductivas (Hito 2.1) | Extensión determinista futura |

**Tabla 2: Marco de Cumplimiento Daubert**

| Principio | Implementación del Módulo | Base Aritmética Entera |
|---|---|---|
| Determinismo | Entrada idéntica siempre produce salida idéntica | `(reglas_satisfechas × 100) // total_reglas` |
| Auditabilidad | Cada decisión es trazable a una tabla de búsqueda pública | Sin pesos ni embeddings opacos |
| Reproducibilidad | Hash SHA256 de la salida invariante entre plataformas | Ausencia de varianza por punto flotante |
| Falsabilidad | Reglas explícitas y enumerables; sin heurísticas ocultas | Puntuación entero refutable por contraejemplo |

**Tabla 3: Constantes de Fase de Respuesta a Incidentes (Mapeo NIST 800-61)**

| Constante | Semántica Forense |
|---|---|
| RECONNAISSANCE | Actividad de reconocimiento previa al compromiso |
| INITIAL_ACCESS | Vector de primera entrada no autorizada |
| EXECUTION | Activación de código controlado por el adversario |
| PERSISTENCE | Mecanismos que mantienen el acceso entre sesiones |
| PRIVILEGE_ESCALATION | Adquisición de credenciales de nivel superior |
| DEFENSE_EVASION | Comportamiento anti-forense o contra-detección |
| CREDENTIAL_ACCESS | Robo o compromiso de material de autenticación |
| DISCOVERY | Enumeración interna de activos y red |
| LATERAL_MOVEMENT | Propagación entre hosts o segmentos |
| COLLECTION | Agregación de datos previa a la exfiltración |

**Tabla 4: Metodología de Puntuación Entera**

| Métrica | Fórmula Exacta | Dominio |
|---|---|---|
| `consistency_score` | `(reglas_satisfechas × 100) // total_reglas` | Entero [0, 100] |
| Tupla de detección de fase | `(IRPhase_detectada, consistency_score)` | Símbolo discreto × Entero |

### Glosario de Términos Técnicos

- **Artefacto forense**: Dato bruto del sistema sin interpretar. En términos semióticos, la Primeridad de Peirce: presencia pura sin reacción ni ley.
- **Puntuación de consistencia**: Entero 0-100 que representa la proporción de reglas lógicas satisfechas. No se utiliza aproximación decimal.
- **Tabla de mapeo determinista**: Mapeo fijo donde cada clave de entrada corresponde a exactamente un valor de salida. Sin distribuciones estadísticas ni umbrales probabilísticos.
- **IRPhase**: Objeto que representa una etapa del ciclo de vida de respuesta a incidentes, alineado con NIST SP 800-61r2.
- **Variable visible**: Atributo directamente medible y enumerable sin inferencia (PID, IP origen, hash).
- **Motor de Inferencia Abductiva**: Subsistema analítico planificado (Hito 2.1) que generará hipótesis sobre la intención del adversario a partir de las salidas deterministas de este módulo.

### 【Nota Científica】
La terminología proviene de Charles Sanders Peirce (Primeridad/Segundidad/Terceridad), Umberto Eco (códigos) y H. P. Grice (máximas cooperativas). No es misticismo. Analógicamente: la Primeridad peirceana es el voltaje crudo de un termopar antes de la calibración; los códigos de Eco son las tablas de calibración; las máximas de Grice son los protocolos de comunicación que previenen la notificación selectiva de datos. En este motor forense, un **Artefacto** es el "voltaje crudo", las tablas son la "matriz de calibración" y la puntuación de consistencia entera es la "medición certificada". El vocabulario semiótico proporciona una epistemología formal para la clasificación determinista, no un sistema de creencias metafísico.

---

## РУССКИЙ

### Что Это За Модуль?
Этот модуль, `vigia/tools/visible_variables.py`, составляет детерминистическое аналитическое ядро цифровой криминалистической платформы VIGIA. Его назначение — преобразовывать необработанные системные наблюдения — такие как события создания процессов, состояния сетевых сокетов и временны́е метки файловой системы — в структурированные объекты доказательств, пригодных для судебного рассмотрения. Движок принимает только целочисленную арифметику и отображения через таблицы поиска. Он не содержит инструкций с плавающей точкой, вероятностных порогов или скрытых условных переходов. Этот дизайн удовлетворяет критериям судебной надёжности (стандарт Daubert), гарантируя, что каждый вывод является воспроизводимым, поддающимся аудиту и опровергаемым.

### Ключевые Концепции и Компоненты

**Таблица 1: Основные Компоненты и Возможности**

| Компонент / Возможность | Научная роль | Детерминистическая гарантия |
|---|---|---|
| IRPhase | Символическая таксономия стадий реагирования на инциденты NIST SP 800-61 | Дискретные, неизменяемые константы |
| VariableCategory | Онтологическая классификация наблюдаемых свойств (временны́е, процессные, сетевые) | Исчерпывающее перечисление |
| Artifact (Артефакт) | Единица необработанного криминалистического наблюдения (Перводность Пирса) | Неизменяемая запись сбора |
| FocusAnalysis | Структурированный контейнер для анализируемых видимых переменных | `consistency_score`: целое [0, 100] |
| VisibleVariablesEngine | Центральный процессор, выполняющий проверку правил через таблицы поиска | Нуль операций с плавающей точкой |
| AbductiveIntentEngineInterface | Типизированная граница для нижестоящего движка вывода о намерениях (Milestone 2.1) | Детерминированный канал без потерь |
| `analyze_bundle_focus` | Удобная операция для сквозного анализа пакета | Воспроизводимый конвейер |
| `to_dict` / `to_json` | Сериализация для обмена доказательствами | Стабильный SHA256 вывод |
| `detect_phase` | Классификация фазы с использованием эксклюзивных таблиц отображения | Возвращает `(IRPhase, целочисленный_score)` |
| `analyze_focus` | Комплексный фокусный анализ множества видимых переменных | Целочисленный подсчёт удовлетворённых правил |
| `infer_habit` | Заглушка для генерации абдуктивных гипотез (Milestone 2.1) | Будущее детерминированное расширение |

**Таблица 2: Структура Соответствия Daubert**

| Принцип | Реализация в модуле | Основа целочисленной арифметики |
|---|---|---|
| Детерминизм | Идентичный ввод всегда даёт идентичный вывод | `(удовлетв._правила × 100) // всего_правил` |
| Поддаваемость аудиту | Каждое решение прослеживается до публичной таблицы поиска | Нет непрозрачных весов или встраиваний |
| Воспроизводимость | Хэш SHA256 вывода инвариантен на разных платформах | Отсутствие вариаций из-за платформенных чисел с плавающей точкой |
| Опровергаемость | Явные, перечислимые правила; нет скрытых эвристик | Целочисленный балл опровергается одним контрпримером |

**Таблица 3: Константы Фаз Реагирования на Инциденты (Отображение NIST 800-61)**

| Константа | Криминалистическая семантика |
|---|---|
| RECONNAISSANCE | Деятельность противника по разведке до компрометации |
| INITIAL_ACCESS | Вектор первого несанкционированного входа в систему |
| EXECUTION | Активация кода, контролируемого противником |
| PERSISTENCE | Механизмы поддержания доступа между сеансами |
| PRIVILEGE_ESCALATION | Получение привилегий более высокого уровня |
| DEFENSE_EVASION | Антикриминалистическое или противообнаружительное поведение |
| CREDENTIAL_ACCESS | Кража или компрометация аутентификационного материала |
| DISCOVERY | Внутреннее перечисление активов и сети |
| LATERAL_MOVEMENT | Распространение между хостами или сегментами |
| COLLECTION | Агрегация данных перед экфильтрацией |

**Таблица 4: Методология Целочисленного Скоринга**

| Метрика | Точная формула | Область |
|---|---|---|
| `consistency_score` | `(удовлетв._правила × 100) // всего_правил` | Целочисленный интервал [0, 100] |
| Кортеж обнаружения фазы | `(обнаруж._IRPhase, consistency_score)` | Дискретный символ × Целое |

### Глоссарий Технических Терминов

- **Судебный артефакт**: Необработанное системное наблюдение. В семиотике Пирса — Перводность: чистое качество присутствия без реакции или закона.
- **Балл согласованности**: Точное целое в интервале [0, 100], количественно выражающее долю применимых логических правил, которые удовлетворены. Вычисляется целочисленным умножением и делением с округлением вниз, полностью избегая дробных представлений.
- **Детерминистическая таблица поиска**: Тотальная функция, реализованная как фиксированное отображение ключей в значения. Каждый поиск воспроизводим и доступен для проверки; нет доверительных интервалов, плотностей вероятности или статистических порогов.
- **Видимая переменная**: Прямо измеримый атрибут системы, значение которого можно перечислить без интерпретативного вывода (например, PID, IP-адрес источника, номер inode).
- **Абдуктивный движок намерений**: Планируемая аналитическая подсистема (Milestone 2.1), которая будет генерировать выводные гипотезы об умысле противника из детерминистических выводов этого модуля.

### 【Научное Примечание】
Данный модуль использует терминологию, коренящуюся в семиотике Чарльза Сандерса Пирса (Перводность, Вторичность, Третичность), теории культурного кодирования Умберто Эко и кооперативной логике Г. П. Грайса. Это не мистические или гуманистические концепции. Рассмотрим лабораторный спектрометр: Перводность Пирса — это сырое напряжение детектора до какой-либо обработки; коды Эко — это калибровочные матрицы, отображающие напряжение в спектральные линии; максимы Грайса — это лабораторные протоколы, предотвращающие избирательное сообщение данных. Здесь **Артефакт** — это «сырое напряжение», таблицы поиска движка составляют «калибровочный стандарт», а целочисленный `consistency_score` — это «сертифицированное измерение». Семиотический словарь обеспечивает формальную эпистемологию для детерминистической классификации, а не метафизическую систему убеждений.

---

## 中文

### 本模块是什么？
本模块位于 `vigia/tools/visible_variables.py`，是VIGIA取证平台的确定性核心。它将系统原始观测数据——如进程创建、网络连接和文件时间戳——转化为结构化、可审计的证据束。它仅通过整数运算和预定义查找表进行操作，消除了浮点近似带来的变异性。根据道伯特标准（Daubert）设计，以确保司法可采性，它提供了从可观测取证工件到事件响应阶段分类的可复现管道。

### 核心概念与组件

**表1：核心组件与功能**

| 组件 / 功能 | 科学角色 | 确定性保证 |
|---|---|---|
| IRPhase | 符合NIST SP 800-61的事件响应阶段符号分类 | 离散不变常量 |
| VariableCategory | 可观测属性的本体论分类（时间性、进程性、网络性） | 穷举枚举 |
| Artifact（取证工件） | 原始取证观测单位（皮尔斯的"第一性"） | 不可变采集记录 |
| FocusAnalysis | 已分析可见变量的结构化容器 | `consistency_score`：整数 [0,100] |
| VisibleVariablesEngine | 通过查找表执行规则满足度的中央处理器 | 零浮点运算 |
| AbductiveIntentEngineInterface | 下游意图推理引擎的类型化边界（里程碑2.1） | 无损确定性通道 |
| `analyze_bundle_focus` | 端到端束分析的便捷操作 | 可复现管道 |
| `to_dict` / `to_json` | 证据交换序列化 | SHA256稳定输出 |
| `detect_phase` | 使用专用映射表进行阶段分类 | 返回 `(IRPhase, 整数评分)` |
| `analyze_focus` | 对可见变量集的全面焦点分析 | 整数规则满足度计数 |
| `infer_habit` | 溯因假设生成占位符（里程碑2.1） | 未来确定性扩展 |

**表2：道伯特合规框架**

| 原则 | 模块实现 | 整数运算基础 |
|---|---|---|
| 确定性 | 相同输入始终产生相同输出 | `(满足规则数 × 100) // 总规则数` |
| 可审计性 | 每个决策均可追溯至公开查找表 | 无不透明权重或嵌入 |
| 可复现性 | 跨平台输出SHA256哈希不变 | 无浮点平台差异 |
| 可证伪性 | 显式可枚举规则；无隐藏启发式 | 整数评分可被单个反例证伪 |

**表3：事件响应阶段常量（NIST 800-61映射）**

| 常量 | 取证语义 |
|---|---|
| RECONNAISSANCE | 入侵前的对手侦察活动 |
| INITIAL_ACCESS | 首次未授权系统进入的向量 |
| EXECUTION | 对手控制代码的激活 |
| PERSISTENCE | 维持跨会话访问的机制 |
| PRIVILEGE_ESCALATION | 获取更高级别凭证 |
| DEFENSE_EVASION | 反取证或对抗检测行为 |
| CREDENTIAL_ACCESS | 认证材料的盗窃或泄露 |
| DISCOVERY | 内部资产与网络枚举 |
| LATERAL_MOVEMENT | 主机间或网段间传播 |
| COLLECTION | 数据泄露前的聚合 |

**表4：整数评分方法论**

| 指标 | 精确公式 | 域 |
|---|---|---|
| `consistency_score` | `(满足规则数 × 100) // 总规则数` | 整数区间 [0, 100] |
| 阶段检测元组 | `(检测到的IRPhase, consistency_score)` | 离散符号 × 整数 |

### 术语表

- **取证工件**：未经解释的系统原始观测（如注册表修改、TCP SYN包或文件MAC时间）。在符号学中，对应皮尔斯的*第一性*：即时在场的纯质性，先于反应或法则。
- **一致性评分**：封闭区间 [0, 100] 中的精确整数，量化适用逻辑规则中被满足的比例。通过整数乘法和向下取整除法计算，完全避免小数表示。
- **确定性查找表**：实现为键值固定映射的全函数。每次查找均可复现且可检查；没有置信区间、概率密度或统计阈值。
- **可见变量**：无需推理即可直接测量和枚举的系统属性（如进程ID、源IP地址、inode号）。
- **溯因意图引擎**：计划中的分析子系统（里程碑2.1），将从本模块的确定性输出生成关于对手意图的推理假设，从而填补原始取证工件与对手意图之间的逻辑断裂。

### 【科学说明】
本模块采用了源自查尔斯·桑德斯·皮尔斯（Charles Sanders Peirce，第一性/第二性/第三性）、翁贝托·艾柯（Umberto Eco，代码/文化框架）以及H. P. 格赖斯（H. P. Grice，合作原则）的术语。这并非神秘主义或文学批评。最佳理解方式是借助传感器类比：皮尔斯的"第一性"是热电偶在未经校准前的原始电压；艾柯的代码是将电压转换为温度的校准表；格赖斯的准则是确保传感器数据报告无遗漏、无失真的通信协议。在本取证引擎中，**取证工件**就是"原始电压"，查找表就是"校准矩阵"，而整数一致性评分就是"认证测量值"。符号学框架为确定性分类提供了认识论语法，而非形而上学教条。

---

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
