<!--
VIGIA Academic Documentation
Module: 2dbec0bc
Batch ID: vigia-doc-0059-2dbec0bc
Generated: 2026-05-20T14:56:47.857146+00:00
-->

# Module Documentation: `vigia/core/integrity_constraints.py`

---

## ENGLISH

### What Is This Module?
`integrity_constraints.py` is the circuit breaker for forensic reasoning inside VIGÍA. When the system detects a temporal collapse—such as a `TEMPORAL_PARADOX` or a `TEMPORAL_CAUSALITY_VIOLATION`—this module ensures that every downstream hypothesis which relied on the shattered assumption is immediately invalidated. It is analogous to a building inspector who, upon discovering a fatal crack in a foundation, evacuates every apartment above it.

The module implements an ATMS-inspired (Assumption-based Truth Maintenance System) dependency tracker using deterministic integer arithmetic. Every assumption, hypothesis, and constraint is identified by exact integer keys. State transitions (valid → invalid) are performed via integer operations, ensuring bitwise-repeatable results across all hardware platforms. There are no approximate calculations.

### Key Concepts

**Table 1. Core Concepts**
| Concept | Plain-Language Definition | Deterministic Integer Role |
|---|---|---|
| `IntegrityConstraint` | A formal rule that states which assumptions an abductive hypothesis needs in order to remain valid. | Each constraint receives an integer `constraint_id`; status is stored as an integer enumeration (e.g., 0 = active, 1 = violated). |
| `AssumptionTracker` | The engine that maps parent assumptions to child hypotheses in a directed dependency graph. | Graph edges and node states are indexed by integers, guaranteeing bitwise-identical evaluation on every run. |
| CAIE Fracture | A logical rupture reported by the CAIE submodule, such as `TEMPORAL_PARADOX` or `TEMPORAL_CAUSALITY_VIOLATION`. | Translated into an integer invalidation code; propagation uses integer set operations, never approximate comparisons. |
| Downstream Invalidation | The cascade that occurs when a collapsed assumption recursively disqualifies every hypothesis built upon it. | Implemented as deterministic integer state transitions (valid → invalid) without probabilistic thresholds. |
| `ForensicBundle` | A standardized export container used to archive or transmit the tracker's full state. | Contains only JSON-safe integers and strings; callable objects are excluded from serialization. |

**Table 2. Main Components**
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

### Glossary

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

### 【Scientific Note】

> **【Scientific Note】**
> The terminology of Peirce (abduction), Eco (interpretative frameworks), and Grice (pragmatic maxims) is sometimes mistaken for philosophical mysticism. In VIGÍA, these concepts function as formalized sensors. Just as a digital thermometer converts thermal energy into an integer reading (e.g., 298 K), the system converts semiotic and inferential relations into deterministic integer states. They are instruments for measuring coherence, not esoteric doctrines.

---

## ESPAÑOL

### ¿Qué es este módulo?
`integrity_constraints.py` es el disyuntor del razonamiento forense dentro de VIGÍA. Cuando el sistema detecta un colapso temporal —como un `TEMPORAL_PARADOX` o una `TEMPORAL_CAUSALITY_VIOLATION`— este módulo garantiza que toda hipótesis descendiente que dependía del supuesto quebrado sea invalidada de inmediato. Es análogo a un inspector de edificios que, al descubrir una falla fatal en los cimientos, evacúa todos los pisos superiores.

El módulo implementa un rastreador de dependencias inspirado en ATMS (Sistema de Mantenimiento de Verdad basado en Supuestos) mediante aritmética entera determinista. Cada supuesto, hipótesis y restricción se identifica con claves enteras exactas. Las transiciones de estado (válido → inválido) se ejecutan mediante operaciones enteras, lo que garantiza resultados idénticos bit a bit en cualquier plataforma de hardware. No existen cálculos aproximados.

### Conceptos Clave

**Tabla 1. Conceptos Principales**
| Concepto | Definición en Lenguaje Sencillo | Rol Entero Determinista |
|---|---|---|
| `IntegrityConstraint` | Regla formal que establece qué supuestos necesita una hipótesis abductiva para seguir siendo válida. | Cada restricción recibe un `constraint_id` entero; el estado se almacena como enumeración entera (p. ej., 0 = activo, 1 = violado). |
| `AssumptionTracker` | Motor que mapea supuestos padre a hipótesis hijo en un grafo de dependencias dirigido. | Aristas y estados de nodo indexados por enteros, garantizando evaluación bit a bit idéntica en cada ejecución. |
| Fractura CAIE | Ruptura lógica reportada por el submódulo CAIE, como `TEMPORAL_PARADOX` o `TEMPORAL_CAUSALITY_VIOLATION`. | Traducida a un código entero de invalidación; la propagación usa operaciones de conjuntos enteros. |
| Invalidación Descendente | La cascada que se produce cuando un supuesto colapsado descalifica recursivamente cada hipótesis construida sobre él. | Implementada como transiciones de estado enteras deterministas (válido → inválido) sin umbrales probabilísticos. |
| `ForensicBundle` | Contenedor de exportación estándar para archivar o transmitir el estado completo del rastreador. | Contiene solo enteros y cadenas seguros para JSON; los objetos invocables se excluyen de la serialización. |

**Tabla 2. Componentes Principales**
| Componente | Tipo | Propósito |
|---|---|---|
| `IntegrityConstraint` | Clase | Objeto de datos inmutable que representa una regla de integridad. |
| `AssumptionTracker` | Clase | Grafo de dependencias mutable y orquestador de evaluación. |
| `apply_caie_fractures()` | Función | Ingiere una lista de fracturas CAIE y las convierte en eventos de invalidación del rastreador. |
| `build_default()` | Función | Factoría que devuelve un `AssumptionTracker` precargado con `SYSTEM_ASSUMPTIONS`. |
| `with_status()` | Método | Devuelve una nueva instancia de `IntegrityConstraint` con código de estado entero actualizado. |
| `to_dict()` | Método | Exporta el estado de la restricción como diccionario JSON-seguro de enteros y cadenas. |
| `register()` | Método | Añade una restricción al rastreador; el orden de registro define la precedencia de evaluación. |
| `evaluate_all()` | Método | Ejecuta cada restricción registrada contra la lista actual de artefactos usando aritmética entera determinista. |
| `invalidate_assumption()` | Método | Marca un supuesto como colapsado y registra todas las hipótesis descendientes afectadas. |
| `to_bundle()` | Método | Serializa el estado completo del rastreador en un diccionario compatible con JSON. |

### Glosario

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

### 【Nota Científica】

> **【Nota Científica】**
> La terminología de Peirce (abducción), Eco (marcos interpretativos) y Grice (máximas pragmáticas) a veces se confunde con misticismo filosófico. En VIGÍA, estos conceptos funcionan como sensores formalizados. Así como un termómetro digital convierte la energía térmica en una lectura entera (p. ej., 298 K), el sistema convierte las relaciones semióticas e inferenciales en estados enteros deterministas. Son instrumentos para medir la coherencia, no doctrinas esotéricas.

---

## РУССКИЙ

### Что это за модуль?
`integrity_constraints.py` — это «автоматический выключатель» судебного рассуждения внутри VIGÍA. Когда система обнаруживает временной коллапс — например, `TEMPORAL_PARADOX` или `TEMPORAL_CAUSALITY_VIOLATION` — модуль гарантирует немедленную инвалидацию каждой зависимой гипотезы, опиравшейся на разрушенное допущение. Это сродни работе инспектора зданий, который, обнаружив фатальную трещину в фундаменте, эвакуирует все квартиры выше.

Модуль реализует трекер зависимостей, основанный на идеях ATMS (система поддержания истинности на основе допущений), с применением детерминированной целочисленной арифметики. Каждое допущение, гипотеза и ограничение идентифицируются точными целочисленными ключами. Переходы состояний (действительно → недействительно) выполняются целочисленными операциями, обеспечивая побитово повторяемые результаты на любой аппаратной платформе. Приближённые вычисления отсутствуют.

### Ключевые Понятия

**Таблица 1. Основные Понятия**
| Понятие | Определение Простым Языком | Роль Детерминированных Целых Чисел |
|---|---|---|
| `IntegrityConstraint` | Формальное правило, указывающее, какие допущения нужны абдуктивной гипотезе для сохранения действительности. | Каждое ограничение получает целочисленный `constraint_id`; состояние хранится как целочисленное перечисление (например, 0 = активно, 1 = нарушено). |
| `AssumptionTracker` | Движок, отображающий родительские допущения на дочерние гипотезы в ориентированном графе зависимостей. | Рёбра и состояния узлов индексируются целыми числами, гарантируя побитово идентичные вычисления при каждом запуске. |
| Разрыв CAIE | Логический разрыв, сообщаемый подмодулем CAIE, такой как `TEMPORAL_PARADOX` или `TEMPORAL_CAUSALITY_VIOLATION`. | Преобразуется в целочисленный код инвалидации; распространение использует операции над целочисленными множествами. |
| Нижестоящая Инвалидация | Каскад, возникающий когда рухнувшее допущение рекурсивно дисквалифицирует каждую основанную на нём гипотезу. | Реализована как детерминированные целочисленные переходы состояний (действительно → недействительно) без вероятностных порогов. |
| `ForensicBundle` | Стандартизированный контейнер экспорта для архивирования или передачи полного состояния трекера. | Содержит только JSON-безопасные целые числа и строки; вызываемые объекты исключены из сериализации. |

**Таблица 2. Основные Компоненты**
| Компонент | Тип | Назначение |
|---|---|---|
| `IntegrityConstraint` | Класс | Неизменяемый объект данных, представляющий одно ограничение целостности. |
| `AssumptionTracker` | Класс | Изменяемый граф зависимостей и оркестратор оценки. |
| `apply_caie_fractures()` | Функция | Принимает список разрывов CAIE и преобразует их в события инвалидации трекера. |
| `build_default()` | Функция | Фабрика, возвращающая `AssumptionTracker`, предзагруженный `SYSTEM_ASSUMPTIONS`. |
| `with_status()` | Метод | Возвращает новый экземпляр `IntegrityConstraint` с обновлённым целочисленным кодом состояния. |
| `to_dict()` | Метод | Экспортирует состояние ограничения как JSON-безопасный словарь целых чисел и строк. |
| `register()` | Метод | Добавляет ограничение в трекер; порядок регистрации определяет приоритет оценки. |
| `evaluate_all()` | Метод | Запускает каждое зарегистрированное ограничение против текущего списка артефактов с использованием детерминированной целочисленной арифметики. |
| `invalidate_assumption()` | Метод | Помечает одно допущение как рухнувшее и записывает все затронутые нижестоящие гипотезы. |
| `to_bundle()` | Метод | Сериализует всё состояние трекера в JSON-совместимый словарь для встраивания в `ForensicBundle`. |

### Глоссарий

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

### 【Научное Примечание】

> **【Научное Примечание】**
> Терминология Пирса (абдукция), Эко (интерпретативные рамки) и Грайса (прагматические максимы) иногда ошибочно принимается за философский мистицизм. В VIGÍA эти понятия работают как формализованные датчики. Подобно тому как цифровой термометр преобразует тепловую энергию в целочисленное показание (например, 298 К), система превращает семиотические и инференциальные отношения в детерминированные целочисленные состояния. Это инструменты измерения когерентности, а не эзотерические доктрины.

---

## 中文

### 此模块是什么？
`integrity_constraints.py` 是 VIGÍA 内部法医推理的"断路器"。当系统检测到时间坍塌——例如 `TEMPORAL_PARADOX`（时间悖论）或 `TEMPORAL_CAUSALITY_VIOLATION`（时间因果性违例）——该模块确保所有依赖已崩塌假设的下游假设立即失效。它类似于建筑检查员：一旦发现地基存在致命的逻辑断裂，便会疏散其上方的全部楼层。

该模块借鉴 ATMS（基于假设的真值维护系统）思想，利用确定性整数运算实现依赖追踪。每个假设、约束均通过精确整数键标识。状态转换（有效 → 无效）由整数操作完成，确保在任何硬件平台上都能获得按位一致的结果。不存在任何近似计算。

### 核心概念

**表 1. 主要概念**
| 概念 | 通俗定义 | 确定性整数的作用 |
|---|---|---|
| `IntegrityConstraint` | 声明某溯因假设要保持有效所需前提的形式规则。 | 每个约束获得一个整数 `constraint_id`；状态存储为整数枚举（如 0 = 活动，1 = 违例）。 |
| `AssumptionTracker` | 在有向依赖图中将父假设映射到子假设的引擎。 | 图边和节点状态以整数索引，保证每次运行按位一致的求值。 |
| CAIE 逻辑断裂 | 由 CAIE 子模块检测到的逻辑断裂（如 `TEMPORAL_PARADOX`、`TEMPORAL_CAUSALITY_VIOLATION`）。 | 转换为整数失效码；传播使用整数集合操作，绝不使用近似比较。 |
| 下游失效 | 当某假设坍塌时，所有基于它的假设被递归取消资格的级联效应。 | 以确定性整数状态转换（有效 → 无效）实现，无概率阈值。 |
| `ForensicBundle` | 用于存档或传输追踪器完整状态的标准化导出容器。 | 仅包含 JSON 安全整数与字符串；可调用对象不纳入序列化。 |

**表 2. 主要组件**
| 组件 | 类型 | 目的 |
|---|---|---|
| `IntegrityConstraint` | 类 | 表示一条完整性规则的不可变数据对象。 |
| `AssumptionTracker` | 类 | 可变依赖图与求值协调器。 |
| `apply_caie_fractures()` | 函数 | 接收 CAIE 逻辑断裂列表并将其转换为追踪器失效事件。 |
| `build_default()` | 函数 | 返回预加载 `SYSTEM_ASSUMPTIONS` 的 `AssumptionTracker` 的工厂函数。 |
| `with_status()` | 方法 | 返回带有更新整数状态码的新 `IntegrityConstraint` 实例。 |
| `to_dict()` | 方法 | 将约束状态导出为整数与字符串的 JSON 安全字典。 |
| `register()` | 方法 | 向追踪器添加约束；注册顺序定义求值优先级。 |
| `evaluate_all()` | 方法 | 使用确定性整数运算对当前取证工件列表运行每条已注册约束。 |
| `invalidate_assumption()` | 方法 | 将某一假设标记为已坍塌，并记录所有受影响的下游假设。 |
| `to_bundle()` | 方法 | 将整个追踪器状态序列化为 JSON 兼容字典，嵌入 `ForensicBundle`。 |

### 术语表

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

### 【科学说明】

> **【科学说明】**
> 皮尔士的溯因、艾柯的诠释框架与格赖斯的语用准则有时被误认为哲学神秘主义。在 VIGÍA 中，这些概念充当形式化传感器。正如数字温度计将热能转换为整数读数（例如 298 K），系统也将符号学与推理关系转换为确定性整数状态。它们是测量一致性的仪器，而非玄学教义。

---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
