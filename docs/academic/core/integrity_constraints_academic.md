<!--
VIGIA Academic Documentation
Module: 2dbec0bc
Batch ID: vigia-doc-0059-2dbec0bc
Generated: 2026-05-20T14:56:47.857146+00:00
-->

---
doc_hash: 2dbec0bc
module: vigia/core/integrity_constraints.py
languages: [EN, ES, RU, ZH]
generated_by: moonshot-kimi-k2.6-batch-api
license: Apache-2.0
---

ENGLISH:
- Title: vigia/core/integrity_constraints.py — Assumption & Integrity Tracker
- What Is This Module?: It's the "circuit breaker" for forensic reasoning. When VIGÍA finds a temporal paradox, this module tells all downstream hypotheses that their foundation is gone. It's like a building inspector who not only flags a cracked foundation but evacuates all apartments above it. Uses deterministic integer arithmetic to ensure every status is exact (no rounding errors).
- Scientific Note: Peirce's abduction, Eco's interpretative loops, Grice's maxims are not mysticism. Think of them as formal sensors. A thermal sensor converts heat into an integer digital signal. Similarly, these philosophical tools are converted by VIGÍA into deterministic integer flags (e.g., 0 = valid, 1 = collapsed). They are measurement instruments for meaning, not spiritual concepts.
- Key Concepts Table:
  - IntegrityConstraint | A formal rule binding an abductive hypothesis to its required assumptions. Represented internally with deterministic integer IDs.
  - AssumptionTracker | The dependency engine. Maintains directed links between assumptions (parents) and hypotheses (children) using integer graph indices.
  - CAIE Fracture | A logic break detected by the CAIE module (TEMPORAL_PARADOX, etc.). Propagated as deterministic integer state changes, never as floating-point approximations.
  - Downstream Invalidation | The cascade effect: when assumption A collapses, every hypothesis using A is marked INVALID via integer arithmetic state transitions.
  - ForensicBundle | Standardized container for exporting tracker state as JSON-serializable integers and strings.
- Classes/Functions Table:
  - IntegrityConstraint | IntegrityConstraint | Immutable rule object. Fields: constraint_id (int), required_assumptions (tuple), status (int enum).
  - AssumptionTracker | AssumptionTracker | Dependency graph manager. Methods: register(), evaluate_all(), invalidate_assumption(), to_bundle().
  - apply_caie_fractures() | function | Receives a list of CAIE fractures; converts each into an invalidation event using deterministic integer matching.
  - build_default() | function | Factory returning a tracker pre-loaded with SYSTEM_ASSUMPTIONS as integer-keyed constraints.
  - with_status() | method | Returns new instance (no mutation) with updated integer status code and evidence reference.
  - to_dict() | method | Exports constraint state as JSON-safe integers; excludes non-serializable callable fields.
- Glossary:
  - Abductive Hypothesis | A best-explanation inference (Peirce), formalized here as a node with integer state.
  - Assumption Collapse | The event where a prerequisite belief is falsified, triggering integer state = 0 (false).
  - ATMS | Assumption-based Truth Maintenance System. A deterministic bookkeeping algorithm using integer pointers.
  - Deterministic Integer Arithmetic | Calculations using whole numbers (no decimals) guaranteeing identical results across all hardware.
  - Downstream | Hypotheses that logically depend on a prior assumption.
  - JSON-serializable | Data format representable as text without code execution.
- License.

ESPAÑOL:
- Título: vigia/core/integrity_constraints.py — Rastreador de Supuestos e Integridad
- What Is This Module? -> "¿Qué es este módulo?": Es el "disyuntor" del razonamiento forense. Cuando VIGÍA detecta una paradoja temporal, este módulo notifica a todas las hipótesis dependientes que su fundamento desapareció. Es como un inspector de edificios que no solo señala una grieta en la cimentación, sino que evacúa todos los pisos superiores. Utiliza aritmética entera determinista para garantizar estados exactos (sin errores de redondeo).
- Nota científica: La abducción de Peirce, los lazos interpretativos de Eco y las máximas de Grice no son misticismo. Piense en ellos como sensores formales. Un sensor térmico convierte el calor en una señal digital entera. De igual modo, VIGÍA convierte estas herramientas filosóficas en banderas enteras deterministas (p. ej., 0 = válido, 1 = colapsado). Son instrumentos de medición del significado, no conceptos espirituales.
- Conceptos clave (tablas similares).
- Glosario.
- Licencia.

РУСССКИЙ:
- Title: vigia/core/integrity_constraints.py — Трекер допущений и целостности
- What Is This Module? -> "Что это за модуль?": Это «автоматический выключатель» судебного рассуждения. Когда VIGÍA обнаруживает временной парадокс, этот модуль оповещает все зависимые гипотезы об утрате их основания. Это как инспектор зданий, который не только выявляет трещину в фундаменте, но и эвакуирует все квартиры выше. Использует детерминированную целочисленную арифметику для обеспечения точности состояний (без ошибок округления).
- Scientific Note: Абдукция Пирса, интерпретативные петли Эко и максимы Грайса — это не мистицизм. Воспринимайте их как формальные датчики. Термодатчик преобразует тепло в цифровое целочисленное значение. Аналогично VIGÍA превращает эти философские инструменты в детерминированные целочисленные флаги (например, 0 = действительно, 1 = коллапс). Это измерительные приборы смысла, а не духовные концепции.
- Key concepts & glossary.
- License.

中文:
- Title: vigia/core/integrity_constraints.py — 假设与完整性追踪器
- What Is This Module? -> "此模块是什么？": 它是法医推理的“断路器”。当 VIGÍA 发现时间悖论时，该模块会通知所有下游假设其基础已不复存在。它就像建筑检查员，不仅标记地基中的 逻辑断裂，还会疏散其上方的所有楼层。该模块使用确定性整数运算，确保每个状态完全精确（无舍入误差）。
- Scientific Note: 【科学说明】皮尔士（Peirce）的溯因、艾柯（Eco）的诠释循环、格赖斯（Grice）的准则并非神秘主义。请将它们视为形式化传感器。温度传感器将热量转换为数字整数信号；同理，VIGÍA 将这些哲学工具转换为确定性整数标志（例如，0 = 有效，1 = 坍塌）。它们是意义的测量仪器，而非玄学概念。
- Key concepts:
  - 完整性约束 (IntegrityConstraint) | 将溯因假设与其所需前提绑定的形式规则。内部以确定性整数 ID 表示。
  - 假设追踪器 (AssumptionTracker) | 依赖关系引擎。使用整数图索引维护假设（父节点）与假设（子节点）之间的有向链接。
  - CAIE 逻辑断裂 (CAIE Fracture) | 由 CAIE 模块检测到的逻辑断裂（如 TEMPORAL_PARADOX）。以确定性整数状态变更传播，绝不使用浮点近似。
  - 下游失效 (Downstream Invalidation) | 级联效应：当假设 A 坍塌时，所有使用 A 的假设均通过整数运算状态转换标记为 INVALID。
  - 取证工件 (ForensicBundle) | 用于将追踪器状态导出为 JSON 可序列化整数与字符串的标准化容器。
- Glossary:
  - 溯因假设 (Abductive Hypothesis) | 最佳解释推断（皮尔士），在此形式化为具有整数状态的节点。
  - 假设坍塌 (Assumption Collapse) | 某个先决信念被证伪的事件，触发整数状态 = 0（假）。
  - ATMS | 基于假设的真值维护系统（Assumption-based Truth Maintenance System），一种使用整数指针的确定性簿记算法。
  - 确定性整数运算 (Deterministic Integer Arithmetic) | 使用完整数字（无小数）的计算，确保在所有硬件上结果完全一致。
  - 下游 (Downstream) | 在逻辑上依赖于先前假设的假设。
  - JSON 可序列化 (JSON-serializable) | 可表示为文本且无需执行代码的数据格式。
- License.






Make sure the Chinese uses the specified terms:
- 艾柯 (Eco)
- 格赖斯 (Grice)
- 取证工件 (not 制品)





ENGLISH Table 1: Core Concepts
| Concept | Plain-Language Definition | Deterministic Integer Role |
|---|---|---|
| IntegrityConstraint | A formal rule that states which assumptions an abductive hypothesis needs in order to remain valid. | Each constraint receives an integer `constraint_id`; status is stored as an integer enumeration (e.g., 0 = active, 1 = violated). |
| AssumptionTracker | The engine that maps parent assumptions to child hypotheses in a directed dependency graph. | Graph edges and node states are indexed by integers, guaranteeing bitwise-identical evaluation on every run. |
| CAIE Fracture | A logical rupture reported by the CAIE submodule, such as `TEMPORAL_PARADOX` or `TEMPORAL_CAUSALITY_VIOLATION`. | Translated into an integer invalidation code; propagation uses integer set operations, never floating-point comparisons. |
| Downstream Invalidation | The cascade that occurs when a collapsed assumption recursively disqualifies every hypothesis built upon it. | Implemented as deterministic integer state transitions (valid → invalid) without probabilistic thresholds. |
| ForensicBundle | A standardized export container used to archive or transmit the tracker’s full state. | Contains only JSON-safe integers and strings; callable objects are excluded from serialization. |

ENGLISH Table 2: Main Components
| Component | Type | Purpose |
|---|---|---|
| `IntegrityConstraint` | Class | Immutable data object representing one integrity rule. |
| `AssumptionTracker` | Class | Mutable dependency graph and evaluation orchestrator. |
| `apply_caie_fractures()` | Function | Ingests a list of CAIE fractures and converts them into tracker invalidation events. |
| `build_default()` | Function | Factory that returns an `AssumptionTracker` pre-loaded with `SYSTEM_ASSUMPTIONS`. |
| `with_status()` | Method | Returns a new `IntegrityConstraint` instance with an updated integer status code and evidence reference. |
| `to_dict()` | Method | Exports constraint state as a JSON-safe dictionary of integers and strings. |
| `register()` | Method | Adds a constraint to the tracker; registration order defines evaluation precedence. |
| `evaluate_all()` | Method | Runs every registered constraint against the current artifact list using deterministic integer arithmetic. |
| `invalidate_assumption()` | Method | Marks one assumption as collapsed and records all downstream hypotheses affected. |
| `to_bundle()` | Method | Serializes the entire tracker state into a JSON-compatible dictionary for embedding in a `ForensicBundle`. |

ESPAÑOL tables:
Conceptos principales.
Componentes principales.

РУССКИЙ tables:
Основные понятия.
Основные компоненты.

中文 tables:
核心概念.
主要组件.


Example:
> **【Scientific Note】**  
> Peirce's abduction, Eco's interpretative loops, and Grice's maxims are not mysticism. ...

In Chinese:
> **【科学说明】**  
> 皮尔士的溯因、艾柯的诠释循环、格赖斯的准则并非神秘主义。 ...









ENGLISH "What Is This Module?":
This module, `integrity_constraints.py`, is the circuit breaker for forensic reasoning inside VIGÍA. When the system detects a temporal collapse—such as a `TEMPORAL_PARADOX` or a `TEMPORAL_CAUSALITY_VIOLATION`—this module ensures that every downstream hypothesis which relied on the shattered assumption is immediately invalidated. It is analogous to a building inspector who, upon discovering a fatal crack in a foundation, evacuates every apartment above it.

The module implements an ATMS-inspired (Assumption-based Truth Maintenance System) dependency tracker using deterministic integer arithmetic. Every assumption, hypothesis, and constraint is identified by exact integer keys. State transitions (valid → invalid) are performed via integer operations, ensuring bitwise-repeatable results across all hardware platforms. There are no approximate calculations.

ESPAÑOL:
¿Qué es este módulo?
Este módulo, `integrity_constraints.py`, es el disyuntor del razonamiento forense dentro de VIGÍA. Cuando el sistema detecta un colapso temporal —como un `TEMPORAL_PARADOX` o una `TEMPORAL_CAUSALITY_VIOLATION`— este módulo garantiza que toda hipótesis descendiente que dependía del supuesto quebrado sea invalidada de inmediato. Es análogo a un inspector de edificios que, al descubrir una falla fatal en los cimientos, evacua todos los pisos superiores.

El módulo implementa un rastreador de dependencias inspirado en ATMS (Sistema de Mantenimiento de Verdad basado en Supuestos) mediante aritmética entera determinista. Cada supuesto, hipótesis y restricción se identifica con claves enteras exactas. Las transiciones de estado (válido → inválido) se ejecutan mediante operaciones enteras, lo que garantiza resultados idénticos bit a bit en cualquier plataforma de hardware. No existen cálculos aproximados.

РУССКИЙ:
Что это за модуль?
Этот модуль, `integrity_constraints.py`, — это «автоматический выключатель» судебного рассуждения внутри VIGÍA. Когда система обнаруживает временной коллапс — например, `TEMPORAL_PARADOX` или `TEMPORAL_CAUSALITY_VIOLATION` — модуль гарантирует немедленную инвалидацию каждой зависимой гипотезы, опиравшейся на разрушенное допущение. Это сродни работе инспектора зданий, который, обнаружив фатальную трещину в фундаменте, эвакуирует все квартиры выше.

Модуль реализует трекер зависимостей, основанный на идеях ATMS (система поддержания истинности на основе допущений), с применением детерминированной целочисленной арифметики. Каждое допущение, гипотеза и ограничение идентифицируются точными целочисленными ключами. Переходы состояний (действительно → недействительно) выполняются целочисленными операциями, обеспечивая побитово повторяемые результаты на любой аппаратной платформе. Приближённые вычисления отсутствуют.

中文:
此模块是什么？
`integrity_constraints.py` 是 VIGÍA 内部法医推理的“断路器”。当系统检测到时间坍塌——例如 `TEMPORAL_PARADOX`（时间悖论）或 `TEMPORAL_CAUSALITY_VIOLATION`（时间因果性违例）——该模块确保所有依赖已崩塌假设的下游假设立即失效。它类似于建筑检查员：一旦发现地基存在致命的 逻辑断裂，便会疏散其上方的全部楼层。

该模块借鉴 ATMS（基于假设的真值维护系统）思想，利用确定性整数运算实现依赖追踪。每个假设、假设与约束均通过精确整数键标识。状态转换（有效 → 无效）由整数操作完成，确保在任何硬件平台上都能获得按位一致的结果。不存在任何近似计算。

Now the Scientific Note text.

ENGLISH:
> **【Scientific Note】**  
> The terminology of Peirce (abduction), Eco (interpretative frameworks), and Grice (pragmatic maxims) is sometimes mistaken for philosophical mysticism. In VIGÍA, these concepts function as formalized sensors. Just as a digital thermometer converts thermal energy into an integer reading (e.g., 298 K), the system converts semiotic and inferential relations into deterministic integer states. They are instruments for measuring coherence, not esoteric doctrines.

ESPAÑOL:
> **【Nota Científica】**  
> La terminología de Peirce (abducción), Eco (marcos interpretativos) y Grice (máximas pragmáticas) a veces se confunde con misticismo filosófico. En VIGÍA, estos conceptos funcionan como sensores formalizados. Así como un termómetro digital convierte la energía térmica en una lectura entera (p. ej., 298 K), el sistema convierte las relaciones semióticas e inferenciales en estados enteros deterministas. Son instrumentos para medir la coherencia, no doctrinas esotéricas.

РУССКИЙ:
> **【Научное Примечание】**  
> Терминология Пирса (абдукция), Эко (интерпретативные рамки) и Грайса (прагматические максимы) иногда ошибочно принимается за философский мистицизм. В VIGÍA эти понятия работают как формализованные датчики. Подобно тому как цифровой термометр преобразует тепловую энергию в целочисленное показание (например, 298 К), система превращает семиотические и инференциальные отношения в детерминированные целочисленные состояния. Это инструменты измерения когерентности, а не эзотерические доктрины.

中文:
> **【科学说明】**  
> 皮尔士（Peirce）的溯因、艾柯（Eco）的诠释框架、格赖斯（Grice）的语用准则有时被误认为哲学神秘主义。在 VIGÍA 中，这些概念充当形式化传感器。正如数字温度计将热能转换为整数读数（例如 298 K），系统也将符号学与推理关系转换为确定性整数状态。它们是测量一致性的仪器，而非秘传教义。


Revised Chinese note:
> **【科学说明】**  
> 皮尔士的溯因、艾柯的诠释框架与格赖斯的语用准则有时被误认为哲学神秘主义。在 VIGÍA 中，这些概念充当形式化传感器。正如数字温度计将热能转换为整数读数（例如 298 K），系统也将符号学与推理关系转换为确定性整数状态。它们是测量一致性的仪器，而非玄学教义。

Good.

Now Glossary.

ENGLISH Glossary:
| Term | Definition |
|---|---|
| **Abductive Hypothesis** | An inference to the best explanation (Peirce), represented in the tracker as a node with an exact integer state. |
| **Assumption Collapse** | The falsification of a prerequisite belief, triggering a deterministic integer state change to *invalid*. |
| **ATMS** | Assumption-based Truth Maintenance System. A deterministic bookkeeping algorithm that uses integer pointers to track logical dependencies. |
| **CAIE Fracture** | A logical break detected by the CAIE engine (e.g., temporal paradox). Recorded as an integer event code. |
| **Deterministic Integer Arithmetic** | Computation restricted to whole numbers, ensuring identical, repeatable results on every execution and every CPU. |
| **Downstream** | Hypotheses or constraints that logically depend on a parent assumption. |
| **Forensic Artifact** | A unit of digital evidence. The tracker evaluates constraints against lists of these artifacts using integer identifiers. |
| **Integrity Constraint** | A rule that binds a hypothesis to its required assumptions; violation invalidates the hypothesis. |
| **JSON-serializable** | A data representation composed only of strings, integers, and collections, safe for storage or transmission without code execution. |
| **SYSTEM_ASSUMPTIONS** | The built-in set of implicit assumptions formalized as first-class integrity constraints in the default tracker configuration. |

ESPAÑOL Glossary:
| Término | Definición |
|---|---|
| **Hipótesis Abductiva** | Inferencia a la mejor explicación (Peirce), representada en el rastreador como un nodo con un estado entero exacto. |
| **Colapso de Supuesto** | Falsificación de una creencia prerequisito, que desencadena un cambio de estado entero determinista a *inválido*. |
| **ATMS** | Sistema de Mantenimiento de Verdad basado en Supuestos. Algoritmo determinista de contabilidad que usa punteros enteros para rastrear dependencias lógicas. |
| **Fractura CAIE** | Ruptura lógica detectada por el motor CAIE (p. ej., paradoja temporal). Registrada como un código de evento entero. |
| **Aritmética Entera Determinista** | Cálculo restringido a números enteros, que garantiza resultados idénticos y repetibles en cada ejecución y en cada CPU. |
| **Downstream / Descendiente** | Hipótesis o restricciones que dependen lógicamente de un supuesto padre. |
| **Artefacto Forense** | Unidad de evidencia digital. El rastreador evalúa restricciones sobre listas de estos artefactos usando identificadores enteros. |
| **Constraint de Integridad** | Regla que vincula una hipótesis con sus supuestos requeridos; su violación invalida la hipótesis. |
| **JSON-serializable** | Representación de datos compuesta solo de cadenas, enteros y colecciones, segura para almacenamiento o transmisión sin ejecución de código. |
| **SYSTEM_ASSUMPTIONS** | Conjunto integrado de supuestos implícitos formalizados como constraints de integridad de primera clase en la configuración por defecto del rastreador. |

РУССКИЙ Glossary:
| Термин | Определение |
|---|---|
| **Абдуктивная гипотеза** | Вывод к наилучшему объяснению (Пирс), представленный в трекере как узел с точным целочисленным состоянием. |
| **Коллапс допущения** | Опровержение предварительного убеждения, запускающее детерминированное целочисленное изменение состояния на *недействительно*. |
| **ATMS** | Система поддержания истинности на основе допущений. Детерминированный учётный алгоритм, использующий целочисленные указатели для отслеживания логических зависимостей. |
| **Разрыв CAIE** | Логический разрыв, обнаруженный движком CAIE (например, временной парадокс). Записывается как целочисленный код события. |
| **Детерминированная целочисленная арифметика** | Вычисления, ограниченные целыми числами, обеспечивающие идентичные, повторяемые результаты при каждом запуске на любом процессоре. |
| **Downstream / Нижестоящий** | Гипотезы или ограничения, логически зависящие от родительского допущения. |
| **Судебный артефакт** | Единица цифрового доказательства. Трекер оценивает ограничения по спискам этих артефактов с использованием целочисленных идентификаторов. |
| **Ограничение целостности** | Правило, связывающее гипотезу с необходимыми для неё допущениями; нарушение инвалидирует гипотезу. |
| **JSON-сериализуемый** | Представление данных, состоящее только из строк, целых чисел и коллекций, безопасное для хранения или передачи без исполнения кода. |
| **SYSTEM_ASSUMPTIONS** | Встроенный набор неявных допущений, формализованных как ограничения целостности первого класса в конфигурации трекера по умолчанию. |

中文 Glossary:
| 术语 | 定义 |
|---|---|
| **溯因假设** | 最佳解释推断（皮尔士），在追踪器中表示为具有精确整数状态的节点。 |
| **假设坍塌** | 先决信念被证伪的事件，触发确定性整数状态变更为*无效*。 |
| **ATMS** | 基于假设的真值维护系统（Assumption-based Truth Maintenance System）。使用整数指针追踪逻辑依赖关系的确定性簿记算法。 |
| **CAIE 逻辑断裂** | 由 CAIE 引擎检测到的逻辑断裂（如时间悖论）。以整数事件码记录。 |
| **确定性整数运算** | 仅限于整数的计算，确保在每次执行及每颗 CPU 上均产生相同、可重复的结果。 |
| **下游** | 在逻辑上依赖于父假设的假设或约束。 |
| **取证工件** | 数字证据的单位。追踪器使用整数标识符对取证工件列表进行约束评估。 |
| **完整性约束** | 将假设与其所需前提绑定的规则；一旦违例，该假设即告无效。 |
| **JSON 可序列化** | 仅由字符串、整数与集合构成的数据表示形式，可安全存储或传输，无需执行代码。 |
| **SYSTEM_ASSUMPTIONS** | 默认追踪器配置中，被形式化为第一类完整性约束的内置隐式假设集合。 |

"逻辑断裂 (not 裂缝)". I used 逻辑断裂. Good.








---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
