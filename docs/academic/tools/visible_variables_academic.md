<!--
VIGIA Academic Documentation
Module: e3ae3cf0
Batch ID: vigia-doc-0180-e3ae3cf0
Generated: 2026-05-20T14:56:47.883464+00:00
-->

ENGLISH:
- Artifact: Observable forensic artifact (Peircean Firstness)
- VisibleVariablesEngine: Deterministic engine
- AbductiveIntentEngineInterface: Interface for inference engine
- detect_phase: returns (IRPhase, consistency_score_int)

ESPAÑOL:
- Artefacto: Artefacto forense observable (Primeridad de Peirce)
- Motor de Variables Visibles
- Interfaz para Motor de Inferencia Abdutiva
- detect_phase: retorna (IRPhase, consistency_score_entero)

РУССКИЙ:
- Артефакт: Наблюдаемый судебный артефакт (перводность Пирса)
- Движок видимых переменных
- Интерфейс абдуктивного движка намерений
- детектировать_фазу: возвращает (IRPhase, целое_согласованность)

中文:
- 取证工件: 可观测取证工件 (皮尔斯的"第一性")
- 可见变量引擎
- 溯因意图引擎接口
- 检测阶段: 返回 (IRPhase, 一致性评分整数)

Now let's draft the tables and content carefully.

**ENGLISH Section:**

What Is This Module?
This module, located at `vigia/tools/visible_variables.py`, is the deterministic kernel of the VIGIA forensic platform. It transforms raw system observations—such as process creation, network connections, and file timestamps—into structured, auditable evidence bundles. It operates exclusively through integer arithmetic and predefined lookup tables, eliminating the variability associated with floating-point approximations. Designed for judicial admissibility under Daubert standards, it provides a reproducible pipeline from observable artifact to incident response phase classification.

Key Concepts:
Table 1: Core Components
| Component | Scientific Role | Deterministic Guarantee |
|---|---|---|
| Artifact | Raw observable datum (Peircean Firstness) | Direct sensor-like acquisition |
| IRPhase | Incident Response phase per NIST 800-61 | Mapped via exclusive lookup tables |
| FocusAnalysis | Aggregation of visible variables | consistency_score is integer [0,100] |
| VisibleVariablesEngine | Central processor | Zero hidden conditionals; table-driven only |
| AbductiveIntentEngineInterface | Future inference receptor (Milestone 2.1) | Strictly typed boundary |

Table 2: Daubert Compliance Guarantees
| Principle | Implementation | Integer Arithmetic Role |
|---|---|---|
| Determinism | 100% reproducible output for identical input | (rules_sat × 100) // total_rules |
| Auditability | Every decision is a table lookup | No opaque neural weights |
| Reproducibility | SHA256 hash stable across executions | No float-induced variance |
| Falsifiability | Explicit rules, no hidden heuristics | Integer score can be disproven by counter-example |

Table 3: Incident Response Phase Constants (NIST 800-61 Aligned)
| Constant | Forensic Meaning |
|---|---|
| RECONNAISSANCE | Pre-compromise surveying activity |
| INITIAL_ACCESS | First unauthorized entry vector |
| EXECUTION | Adversary code execution |
| PERSISTENCE | Maintaining foothold across reboots |
| PRIVILEGE_ESCALATION | Elevated credentials obtained |
| DEFENSE_EVASION | Counter-forensic or anti-detection |
| CREDENTIAL_ACCESS | Credential theft or compromise |
| DISCOVERY | Internal network enumeration |
| LATERAL_MOVEMENT | Host-to-host propagation |
| COLLECTION | Data aggregation for exfiltration |

Table 4: Integer Scoring Methodology
| Metric | Formula | Data Type |
|---|---|---|
| consistency_score | (satisfied_rules × 100) // total_rules | Integer [0, 100] |
| Phase Detection | Lookup table → (IRPhase, consistency_score) | Tuple of discrete symbols and integers |

Glossary:
- **Artifact**: A raw, uninterpreted system datum (e.g., a timestamp, registry key, or network packet). In semiotic terms, this is Peircean Firstness: pure quality of presence without reaction or law.
- **Consistency Score**: An integer from 0 to 100 representing the ratio of satisfied logical rules to total applicable rules, scaled by exact integer multiplication and floor division. No decimal approximation is used.
- **Deterministic Lookup Table**: A fixed mapping where every input key corresponds to exactly one output value. There are no statistical distributions, confidence intervals, or probabilistic thresholds.
- **IRPhase**: An incident response phase object compatible with NIST SP 800-61 guidelines.
- **Visible Variable**: A system attribute that is directly measurable and enumerable without inference (e.g., PID, source IP, file hash).
- **Abductive Intent Engine**: A future analytical module (Milestone 2.1) that will generate hypotheses about adversary intent from the structured output of this module.

【Scientific Note】
The module employs terminology derived from Charles Sanders Peirce (Firstness/Secondness/Thirdness), Umberto Eco (code/cultural framework), and H. P. Grice (cooperative maxims). This is not mysticism or literary criticism. It is best understood through a sensor analogy: Peircean Firstness is the raw voltage from a thermocouple before any calibration; Eco's codes are the calibration tables that translate voltage into temperature; Grice's maxims are the communication protocols ensuring that sensor data is reported without omission or distortion. In this forensic engine, an **Artifact** is the "raw voltage," the lookup tables are the "calibration matrix," and the integer consistency score is the "certified measurement." The semiotic framework provides the epistemological grammar for deterministic classification, not a metaphysical doctrine.

**ESPAÑOL Section:**

What Is This Module? → ¿Qué Es Este Módulo?
Este módulo... núcleo determinista... transforma observaciones brutas del sistema en paquetes de evidencia estructurados y auditables. Opera exclusivamente mediante aritmética de enteros y tablas de búsqueda predefinidas...

Tablas:
Componentes Principales
| Componente | Rol Científico | Garantía Determinista |
|---|---|---|
| Artifact (Artefacto) | Dato observable bruto (Primeridad peirceana) | Adquisición tipo sensor directo |
| IRPhase | Fase de Respuesta a Incidentes NIST 800-61 | Mapeo exclusivo por tablas |
| FocusAnalysis | Agregación de variables visibles | consistency_score: entero [0,100] |
| VisibleVariablesEngine | Procesador central | Cero condicionales ocultos; solo tablas |
| AbductiveIntentEngineInterface | Receptor de inferencia futura (Hito 2.1) | Frontera estrictamente tipada |

Garantías Daubert (same structure)
Fases (same)
Metodología de Puntuación Entera
| Métrica | Fórmula | Tipo de Dato |
|---|---|---|
| consistency_score | (reglas_satisfechas × 100) // total_reglas | Entero [0, 100] |

Glosario:
- **Artefacto forense**: Dato bruto del sistema sin interpretar. En términos semióticos, la Primeridad de Peirce: presencia pura sin reacción ni ley.
- **Puntuación de consistencia**: Entero 0-100 que representa la proporción de reglas lógicas satisfechas. No se utiliza aproximación decimal.
- **Tabla de mapeo determinista**: Mapeo fijo donde cada clave de entrada corresponde a exactamente un valor de salida. Sin distribuciones estadísticas ni umbrales probabilísticos.
- **Variable visible**: Atributo directamente medible y enumerable sin inferencia (PID, IP origen, hash).

Nota Científica:
La terminología proviene de Charles Sanders Peirce (Primeridad/Segundidad/Terceridad), Umberto Eco (códigos) y H. P. Grice (máximas cooperativas). No es misticismo. Analógicamente: la Primeridad peirceana es el voltaje crudo de un termopar antes de la calibración; los códigos de Eco son las tablas de calibración; las máximas de Grice son los protocolos de comunicación. En este motor forense, un **Artefacto** es el "voltaje crudo", las tablas son la "matriz de calibración" y la puntuación de consistencia es la "medición certificada".

License line.

**РУССКИЙ Section:**

What Is This Module? → Что Это За Модуль?
Этот модуль... детерминистическое ядро... преобразует необработанные системные наблюдения в структурированные пакеты доказательств...

Таблицы:
Основные компоненты
| Компонент | Научная роль | Детерминистическая гарантия |
|---|---|---|
| Artifact (Артефакт) | Сырой наблюдаемый данный (перводность Пирса) | Прямое сенсорное считывание |
| IRPhase | Фаза реагирования на инцидент NIST 800-61 | Исключительно табличное отображение |
| FocusAnalysis | Агрегация видимых переменных | consistency_score: целое [0,100] |
| VisibleVariablesEngine | Центральный процессор | Только таблицы; нет скрытых условий |
| AbductiveIntentEngineInterface | Интерфейс для будущего движка абдукции | Строго типизированная граница |

Гарантии Доберта
Фазы реагирования
Методология целочисленного скоринга
| Метрика | Формула | Тип данных |
|---|---|---|
| consistency_score | (удовлетворённые_правила × 100) // всего_правил | Целое [0, 100] |

Глоссарий:
- **Судебный артефакт**: Необработанный системный данный. В семиотике Пирса — перводность: чистое качество присутствия без реакции или закона.
- **Балл согласованности**: Целое число 0–100, представляющее долю удовлетворённых логических правил. Без десятичных приближений.
- **Детерминистическая таблица отображения**: Фиксированное отображение, где каждому входу соответствует ровно один выход.
- **Видимая переменная**: Прямо измеримый атрибут (PID, IP-адрес источника, хеш файла).

Научное примечание:
Терминология основана на Чарльзе Сандерсе Пирсе (перводность/вторичность/третичность), Умберто Эко (коды) и Г. П. Грайсе (кооперативные максимы). Это не мистицизм. По аналогии с датчиком: перводность Пирса — это сырое напряжение термопары до калибровки; коды Эко — таблицы калибровки; максимы Грайса — протоколы передачи данных. В этом движке **артефакт** — «сырое напряжение», таблицы — «калибровочная матрица», а целочисленный балл — «сертифицированное измерение».

License line.

**中文 Section:**

What Is This Module? → 本模块是什么？
本模块位于 `vigia/tools/visible_variables.py`，是VIGIA取证平台的确定性核心。它将系统原始观测数据——如进程创建、网络连接和文件时间戳——转化为结构化、可审计的证据束。它仅通过整数运算和预定义查找表进行操作，消除了浮点近似带来的变异性。根据道伯特标准（Daubert）设计，以确保司法可采性，它提供了从可观测取证工件到事件响应阶段分类的可复现管道。

表格：
核心组件
| 组件 | 科学角色 | 确定性保证 |
|---|---|---|
| Artifact（取证工件） | 原始观测数据（皮尔斯的"第一性"） | 直接传感器式采集 |
| IRPhase | 符合NIST 800-61的事件响应阶段 | 仅通过查找表映射 |
| FocusAnalysis | 可见变量聚合 | consistency_score：整数 [0,100] |
| VisibleVariablesEngine | 中央处理器 | 零隐藏条件；纯表驱动 |
| AbductiveIntentEngineInterface | 未来推理引擎接口（里程碑2.1） | 严格类型边界 |

道伯特合规保证
事件响应阶段常量
整数评分方法论
| 指标 | 公式 | 数据类型 |
|---|---|---|
| 一致性评分 | (满足规则数 × 100) // 总规则数 | 整数 [0, 100] |

术语表：
- **取证工件**：未经解释的系统原始数据（如时间戳、注册表项或网络数据包）。在符号学术语中，这是皮尔斯的"第一性"：纯粹的在场质性，没有反应或法则。
- **一致性评分**：0到100之间的整数，表示满足的逻辑规则数与适用总规则数的比例，通过精确的整数乘法和向下取整除法缩放。不使用小数近似。
- **确定性查找表**：固定映射，每个输入键恰好对应一个输出值。没有统计分布、置信区间或概率阈值。
- **可见变量**：无需推理即可直接测量和枚举的系统属性（如PID、源IP、文件哈希）。
- **溯因意图引擎**：未来的分析模块（里程碑2.1），将从本模块的结构化输出生成关于对手意图的假设。

【科学说明】
本模块采用了源自查尔斯·桑德斯·皮尔斯（Charles Sanders Peirce，第一性/第二性/第三性）、翁贝托·艾柯（Umberto Eco，代码/文化框架）以及H. P. 格赖斯（H. P. Grice，合作原则）的术语。这并非神秘主义或文学批评。最佳理解方式是借助传感器类比：皮尔斯的"第一性"是热电偶在未经校准前的原始电压；艾柯的代码是将电压转换为温度的校准表；格赖斯的准则是确保传感器数据报告无遗漏、无失真的通信协议。在本取证引擎中，**取证工件**就是"原始电压"，查找表就是"校准矩阵"，而整数一致性评分就是"认证测量值"。符号学框架为确定性分类提供了认识论语法，而非形而上学教条。

Classes: IRPhase, VariableCategory, Artifact, FocusAnalysis, VisibleVariablesEngine, AbductiveIntentEngineInterface
Functions: analyze_bundle_focus, to_dict, to_json, detect_phase, analyze_focus, infer_habit
Constants: RECONNAISSANCE, INITIAL_ACCESS, EXECUTION, PERSISTENCE, PRIVILEGE_ESCALATION, DEFENSE_EVASION, CREDENTIAL_ACCESS, DISCOVERY, LATERAL_MOVEMENT, COLLECTION

I should include these in the tables or mention them in the key concepts. Since the audience doesn't know Python, I shouldn't list them as "functions" but rather as "operations" or "capabilities".

Revised Table 1 (EN): Core Components & Capabilities
| Symbolic Component | Scientific Function | Deterministic Property |
|---|---|---|
| IRPhase | Taxonomic container for NIST 800-61 incident lifecycle stages | Discrete symbolic constant |
| VariableCategory | Ontological class of observable system properties (temporal, process, network) | Exhaustive enumeration |
| Artifact | Raw forensic datum representing Peircean Firstness | Immutable observation unit |
| FocusAnalysis | Structured result container holding analyzed visible variables | Integer-only consistency_score [0,100] |
| VisibleVariablesEngine | Central deterministic processor executing table lookups | Zero floating-point operations |
| AbductiveIntentEngineInterface | Typed boundary for downstream intent inference (Milestone 2.1) | No information loss to non-deterministic channels |
| analyze_bundle_focus | Convenience operation for full-bundle processing | Reproducible end-to-end pipeline |
| to_dict / to_json | Serialization operations for evidence exchange | SHA256-stable output |
| detect_phase | Phase classification via exclusive mapping tables | Returns (IRPhase, integer consistency_score) |
| analyze_focus | Comprehensive focal analysis of visible variable set | Rule-satisfaction counting |
| infer_habit | Placeholder for abductive hypothesis generation (Milestone 2.1) | Future deterministic extension |

This is better. I can use a similar structure for all languages.

Also need to make sure I don't use floating-point math explanations. Emphasize integer arithmetic.

For the Chinese section, check required translations:
- 艾柯 (Eco) — used in scientific note
- 格赖斯 (Grice) — used in scientific note
- 取证工件 (Artifact) — used
- 逻辑断裂 — wait, where does this fit? The prompt mentions "逻辑断裂 (not 裂缝)". Looking at the module description, there might be a concept of "logic break/gap". But the provided module docstring doesn't explicitly mention a logic break. The user just said Chinese translations must use those terms. I should probably incorporate "逻辑断裂" somewhere if relevant, or maybe it's just a constraint if the term appears. Since the module deals with inference and abduction, maybe I can mention it in the glossary or note as "logic break/gap" if needed. Actually, the user listed it as a requirement for Chinese translations, likely because the module might deal with "breaks" in logic or "gaps". But I don't see "gap" or "break" in the docstring explicitly. However, abductive inference often deals with explanatory gaps. Let me include it in the glossary as a precautionary compliance: perhaps "逻辑断裂" as the translation for "logic gap/break" if describing what the engine detects. But since the module description doesn't explicitly use this term, I should be careful not to invent module functionality. I'll include it in the glossary as a term related to abductive reasoning: the gap that abduction seeks to bridge. Or better: in the description of `infer_habit`, it generates hypotheses to bridge explanatory gaps. I'll mention "逻辑断裂" there.

Actually, the requirement says "Chinese translations must use: 艾柯 (not Eco), 格赖斯 (not Grice), 取证工件 (not 制品), 逻辑断裂 (not 裂缝)". This is a mandatory vocabulary constraint. I will ensure these exact strings appear in the Chinese section. I'll make sure "逻辑断裂" appears in the scientific note or glossary.

In the scientific note or glossary: "逻辑断裂" — the gap between raw data and inferred intent that the abductive engine will bridge. Or in the description of abductive inference.

Let's plan the Chinese text carefully:

翁贝托·艾柯 (Umberto Eco) — yes
H. P. 格赖斯 — yes
取证工件 — yes
逻辑断裂 — e.g., in the description of infer_habit: "填补原始取证工件与对手意图之间的逻辑断裂" (bridging the logic break between raw artifacts and adversary intent). This seems natural and compliant.

Now, double check: "You NEVER use floating-point math explanations for deterministic systems." So when explaining consistency_score, I must say it's integer arithmetic, and avoid mentioning floats as an alternative to avoid. Actually, the prompt says "do NOT use floating-point math explanations". So I should not explain how floats are bad using float math. I can mention that the system uses integer arithmetic exclusively.

Table 4 in each language should show the integer formula.

Let's assemble the final document. I'll write it as a single Markdown file with four top-level sections.

I'll ensure the license line appears at the end of the document. Actually, to be safest, I'll put it at the end of each language section since the user said "Each section must include..." and then listed the license separately. But the license is a global requirement. I'll put it once at the very bottom to avoid 4 repetitions cluttering the academic tone. Hmm, but compliance is key. I'll include it once after all four sections, clearly marked.

Document structure:
# Technical Documentation: `vigia/tools/visible_variables.py`

---

## ENGLISH

### What Is This Module?

### Key Concepts and Components
Table 1...
Table 2...
Table 3...
Table 4...

### Glossary of Technical Terms

### 【Scientific Note】

---

## ESPAÑOL

### ¿Qué Es Este Módulo?

### Conceptos Clave y Componentes
...

### Glosario de Términos Técnicos

### 【Nota Científica】

---

## РУССКИЙ

### Что Это За Модуль?

### Ключевые Концепции и Компоненты
...

### Глоссарий Технических Терминов

### 【Научное Примечание】

---

## 中文

### 本模块是什么？

### 核心概念与组件
...

### 术语表

### 【科学说明】

---

That looks good.

Now, content details for each.

**ENGLISH:**

What Is This Module?
This module, `vigia/tools/visible_variables.py`, constitutes the deterministic analysis kernel of the VIGIA digital forensics platform. Its purpose is to convert uninterpreted system observations—such as process creation events, network socket states, and filesystem timestamps—into structured, court-admissible evidence objects. The engine accepts only integer arithmetic and lookup-table mappings. It contains no floating-point instructions, no probabilistic thresholds, and no hidden conditional branches. This design satisfies judicial reliability criteria (Daubert standard) by ensuring that every output is reproducible, auditable, and falsifiable.

Table 1: Core Components and Capabilities
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

Table 2: Daubert Compliance Framework
| Principle | Module Implementation | Integer Arithmetic Basis |
|---|---|---|
| Determinism | Identical input always yields identical output | `(satisfied_rules × 100) // total_rules` |
| Auditability | Every decision traceable to a public lookup table | No opaque weights or embeddings |
| Reproducibility | SHA256 hash of output invariant across platforms | Absence of float-induced platform variance |
| Falsifiability | Explicit, enumerable rules; no concealed heuristics | Integer score disprovable by single counter-example |

Table 3: Incident Response Phase Constants (NIST 800-61 Mapping)
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

Table 4: Integer Scoring Methodology
| Metric | Exact Formula | Domain |
|---|---|---|
| `consistency_score` | `(satisfied_rules × 100) // total_rules` | Integer interval [0, 100] |
| Phase detection tuple | `(detected_IRPhase, consistency_score)` | Discrete symbol × Integer |

Glossary:
- **Artifact**: A raw, uninterpreted system observation (e.g., a registry modification, a TCP SYN packet, or a file MAC-time). In semiotics, this corresponds to Peircean *Firstness*: the pure quality of immediate presence, prior to reaction or law.
- **Consistency Score**: An exact integer in the closed interval [0, 100] quantifying the proportion of applicable logical rules that are satisfied. It is computed by integer multiplication and floor division, entirely avoiding fractional representations.
- **Deterministic Lookup Table**: A total function implemented as a fixed mapping from keys to values. Each lookup is reproducible and inspectable; there are no confidence intervals, probability densities, or statistical thresholds.
- **IRPhase**: An object representing a stage in the incident response lifecycle, aligned with NIST SP 800-61r2 guidelines.
- **Visible Variable**: A directly measurable system attribute whose value can be enumerated without interpretive inference (e.g., process ID, source IP address, inode number).
- **Abductive Intent Engine**: A planned analytical subsystem (Milestone 2.1) that will generate inferential hypotheses regarding adversary intent from the deterministic outputs of this module.

【Scientific Note】
This module employs terminology rooted in the semiotics of Charles Sanders Peirce (Firstness, Secondness, Thirdness), the cultural coding theory of Umberto Eco, and the cooperative logic of H. P. Grice. These are not mystical or humanistic conceits. Consider a laboratory spectrometer: Peircean *Firstness* is the raw detector voltage before any processing; Eco’s codes are the calibration matrices that map voltage to spectral lines; Grice’s maxims are the laboratory protocols that prevent selective reporting of data. Here, an **Artifact** is the “raw voltage,” the engine’s lookup tables constitute the “calibration standard,” and the integer `consistency_score` is the “certified measurement.” The semiotic vocabulary provides a formal epistemology for deterministic classification, not a metaphysical belief system.

**ESPAÑOL:**

¿Qué Es Este Módulo?
Este módulo, `vigia/tools/visible_variables.py`, constituye el núcleo de análisis determinista de la plataforma forense digital VIGIA. Su propósito es convertir observaciones del sistema no interpretadas—tales como eventos de creación de procesos, estados de sockets de red y marcas temporales del sistema de archivos—en objetos de evidencia estructurados y admisibles en tribunales. El motor acepta únicamente aritmética de enteros y mapeos por tablas de búsqueda. No contiene instrucciones de punto flotante, umbrales probabilísticos ni ramas condicionales ocultas. Este diseño satisface los criterios de confiabilidad judicial (estándar Daubert) al garantizar que cada salida sea reproducible, auditabile y falsable.

Tabla 1: Componentes y Capacidades Principales
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

Tabla 2: Marco de Cumplimiento Daubert
| Principio | Implementación del Módulo | Base Aritmética Entera |
|---|---|---|
| Determinismo | Entrada idéntica siempre produce salida idéntica | `(reglas_satisfechas × 100) // total_reglas` |
| Auditabilidad | Cada decisión es trazable a una tabla de búsqueda pública | Sin pesos ni embeddings opacos |
| Reproducibilidad | Hash SHA256 de la salida invariante entre plataformas | Ausencia de varianza por punto flotante |
| Falsabilidad | Reglas explícitas y enumerables; sin heurísticas ocultas | Puntuación entero refutable por contraejemplo |

Tabla 3: Constantes de Fase de Respuesta a Incidentes (Mapeo NIST 800-61)
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

Tabla 4: Metodología de Puntuación Entera
| Métrica | Fórmula Exacta |
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
