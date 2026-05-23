<!--
VIGIA Academic Documentation
Module: fd5b51d8
Batch ID: vigia-doc-0147-fd5b51d8
Generated: 2026-05-20T14:56:47.876126+00:00
-->

---
doc_hash: fd5b51d8
module: unknown
languages: [EN, ES, RU, ZH]
generated_by: moonshot-kimi-k2.6-batch-api
license: Apache-2.0
---

ENGLISH:
- What Is This Module? Plain language for scientists. This is a deterministic inference engine that reconstructs attacker intent from digital forensic artifacts using abductive logic and Ockham's Razor. It ranks hypotheses by integer cost, not probability/floats.
- Key Concepts: 
  - Abduction (Peirce): inference to best explanation
  - Ockham's Razor: plurality should not be posited without necessity; here operationalized as integer assumption count
  - Primeridad/Segundidad/Terceridad (Peircean categories): Firstness (raw data/artifact), Secondness (correlations), Thirdness (habit/law/hypothesis)
  - Ockham Cost: integer count of unobserved assumptions
  - Coverage: integer percentage of artifacts explained
  - Deterministic Output: same input yields same winner (integer arithmetic only)
  - Daubert Guarantee: forensic admissibility standard—auditability, explicit templates, no hidden logic, no floats
- Table 1: Peircean Semiotics in Digital Forensics
  | Term | Forensic Mapping | Role in Engine |
  |---|---|---|
  | Firstness (Primeridad) | Artifact | Raw observable |
  | Secondness (Segundidad) | Correlation | Link between artifacts |
  | Thirdness (Terceridad) | Hypothesis | Attacker habit/intent |
- Table 2: Engine Classes
  | Class | Function | Deterministic Property |
  |---|---|---|
  | Artifact | Encapsulates raw forensic datum | Immutable integer ID, timestamp |
  | AbductiveHypothesis | Candidate explanation | Ockham cost stored as integer |
  | AbductiveResult | Ranked output | Winner selected by integer comparison |
  | AbductiveIntentEngine | Orchestrates inference | Reproducible on identical input |
- Table 3: Core Functions
  | Function | Purpose | Output |
  |---|---|---|
  | infer_habit() | Main inference | AbductiveResult |
  | to_dict() | Serialize to dictionary | String-keyed integer maps |
  | to_json() | Export for audit | Human-readable deterministic record |
- Glossary:
  - Abduction: ...
  - Ockham's Razor: ...
  - Artifact: ...
  - Hypothesis (in this context): ...
  - Ockham Cost: ...
  - Deterministic System: ...
  - Daubert Standard: ...
  - Firstness/Secondness/Thirdness: ...
  - Template: ...
- Scientific Note box: Peirce/Eco/Grice terminology is NOT mysticism. Sensor analogy: A sensor detects raw voltage (Firstness). A comparator notes a threshold crossing (Secondness). A firmware routine interprets this as "door opened" (Thirdness). Semiotics is the taxonomy of such inference layers, not occultism. Grice's maxims and Eco's sign theory are formal descriptions of how meaning emerges from structured data—exactly like signal processing pipelines. The engine uses these terms as operational categories, not metaphysical claims.

ESPAÑOL:
- Similar structure. Use original terms from docstring where appropriate (Primeridad, Segundidad, Terceridad).
- Glossary: Artefacto forense, Hipótesis abductiva, Costo Ockham, etc.
- Scientific Note: analogous, mention Peirce/Eco/Grice, analogía del sensor.

РУССКИЙ:
- Terms: Пирс (Peirce), Эко (Eco), Грайс (Grice). Note: In Russian, Eco is usually Эко, Grice is Грайс.
- Scientific note: аналогия с датчиком.
- Key terms: Артефакт (Artifact), Абдукция, Бритва Оккама, etc.
- Deterministic integer arithmetic: целочисленная арифметика.

中文:
- Must use 艾柯 (not Eco), 格赖斯 (not Grice), 取证工件 (not 制品), 逻辑断裂 (not 裂缝).
- Terms: 皮尔士 (Peirce), 溯因推理 (abduction), 奥卡姆剃刀 (Ockham's Razor), 首位性/第一性 (Firstness), 第二位性 (Secondness), 第三位性 (Thirdness), 习惯/规律 (habit/law), 取证工件 (artifact), 假设 (hypothesis), 奥卡姆成本 (Ockham cost), 覆盖率 (coverage), 确定性整数运算 (deterministic integer arithmetic).
- Scientific Note: 【科学说明】box. Sensor analogy: 传感器类比. Raw signal → threshold → interpretation.

Important: Do NOT use floating-point math explanations. Emphasize deterministic integer arithmetic. The module uses integer counts for Ockham cost and integer percentages for coverage. No floats.

Also, the user provided partial docstring text that cuts off. I should extrapolate the architecture gracefully without inventing too much speculative code. Focus on the documented classes and functions.

Let's refine the content.

ENGLISH Section:

## ENGLISH

### What Is This Module?
This module is a deterministic inference engine designed for digital-forensic research. It reconstructs the most plausible attacker intent from a chain of observed forensic artifacts. Instead of using probability or statistics, it employs **abductive reasoning** (inference to the best explanation) and ranks competing hypotheses by an integer **Ockham cost**—the count of unobserved assumptions each hypothesis requires. Because every operation uses exact integer arithmetic, identical inputs always produce the identical winning hypothesis, ensuring full reproducibility for scientific and legal review.

### Key Concepts

| Concept | Description | Deterministic Guarantee |
|---|---|---|
| **Abduction (Peirce)** | Reasoning that generates the hypothesis best explaining the observed data. | Templates are explicit; no hidden heuristics. |
| **Ockham's Razor** | Prefer the explanation with the fewest unobserved assumptions. | Cost is a non-negative integer count, never a float. |
| **Firstness (Primeridad)** | The raw forensic artifact: an observable datum such as a log entry or file hash. | Encapsulated as an immutable `Artifact` object. |
| **Secondness (Segundidad)** | The brute correlation or collision between two artifacts. | Discovered via explicit lookup tables, not fuzzy logic. |
| **Thirdness (Terceridad)** | The habit, law, or pattern that binds artifacts into a coherent story. | Returned as an `AbductiveHypothesis`. |
| **Ockham Cost** | Number of unobserved assumptions introduced by a hypothesis. | Integer arithmetic only; lower is better. |
| **Coverage** | Percentage of input artifacts explained by a hypothesis. | Integer percentage (0–100); no floating-point division. |
| **Daubert Guarantee** | Forensic admissibility standard: auditability, testability, explicit methodology. | Rationale is human-readable; templates are open. |

**Table 1. Class Overview**

| Class | Scientific Role | Deterministic Behavior |
|---|---|---|
| `Artifact` | Firstness: the raw sign / forensic datum | Integer identifiers; no mutation |
| `AbductiveHypothesis` | Thirdness: candidate attacker habit | Ockham cost stored as `int`; comparable by `<` |
| `AbductiveResult` | Ranked output list | Winner selected by integer sort key |
| `AbductiveIntentEngine` | Inference orchestrator | Same input → same output (pure integer pipeline) |

**Table 2. Public Functions**

| Function | Purpose | Output Type |
|---|---|---|
| `infer_habit(chain)` | Main entry point: abduce intent from an artifact chain | `AbductiveResult` |
| `to_dict()` | Serialize object state for audit logs | Dictionary with string keys and integer values |
| `to_json()` | Export to JSON for cross-platform review | Human-readable deterministic record |

### Glossary
- **Abduction**: A logical inference that begins with an observation and concludes with the hypothesis that best explains it. Distinct from deduction (necessarily true) and induction (probably true).
- **Artifact (forensic)**: Any observable digital trace—log line, registry key, memory fragment—that serves as evidence.
- **Ockham Cost**: An integer tally of unobserved entities or assumptions a hypothesis requires. The engine selects the hypothesis with the lowest cost.
- **Coverage**: An integer percentage (0–100) indicating how many observed artifacts are accounted for by a given hypothesis.
- **Firstness / Secondness / Thirdness**: Charles S. Peirce's three universal categories. In this engine, they map to data, correlation, and explanatory law respectively.
- **Template**: An explicit, pre-defined table of hypothesis patterns. The engine loads these tables; no conditional logic is hidden.
- **Deterministic System**: A system where identical initial conditions always yield identical outputs. Here achieved by exclusive use of integer arithmetic and explicit sorting.

### 【Scientific Note】
> **Semiotics Is Not Mysticism; It Is Sensor Taxonomy**
>
> Terminology borrowed from Peirce, Eco, and Grice sometimes sounds esoteric to bench scientists. It is not. Consider a laboratory sensor: the raw voltage reading is **Firstness**; the comparator registering that the voltage crossed a threshold is **Secondness**; the firmware interpreting “voltage crossing = door opened” is **Thirdness**. Umberto Eco's theory of signs and H. P. Grice's conversational maxims are formal descriptions of how structured data becomes meaningful—no different from signal-processing pipelines. This engine uses those terms as **operational categories** for inference layers, not as metaphysical claims. When the module speaks of “habit” or “law,” it refers to a reproducible pattern extracted from integer artifact chains, not to occult forces.

---

ESPAÑOL Section:

## ESPAÑOL

### ¿Qué Es Este Módulo?
Este módulo es un motor de inferencia determinista destinado a la investigación forense digital. Reconstruye la intención del atacante más plausible a partir de una cadena de artefactos forenses observados. En lugar de probabilidad o estadística, utiliza **razonamiento abductivo** (inferencia a la mejor explicación) y ordena las hipótesis competidoras mediante un **costo Ockham** entero: el conteo de supuestos no observados que cada hipótesis requiere. Como todas las operaciones emplean aritmética entera exacta, entradas idénticas siempre producen la misma hipótesis ganadora, garantizando reproducibilidad plena para revisión científica y legal.

### Conceptos Clave

| Concepto | Descripción | Garantía Determinista |
|---|---|---|
| **Abducción (Peirce)** | Razonamiento que genera la hipótesis que mejor explica lo observado. | Plantillas explícitas; sin heurísticas ocultas. |
| **Rasera de Ockham** | Preferir la explicación con menos supuestos no observados. | Costo es un entero no negativo, nunca flotante. |
| **Primeridad** | El artefacto forense bruto: dato observable como una entrada de registro o hash. | Encapsulado en objeto `Artifact` inmutable. |
| **Segundidad** | La correlación bruta o colisión entre dos artefactos. | Descubierta por tablas de búsqueda explícitas, sin lógica difusa. |
| **Terceridad** | El hábito, ley o patrón que une artefactos en una historia coherente. | Retornada como `AbductiveHypothesis`. |
| **Costo Ockham** | Número de supuestos no observados introducidos por una hipótesis. | Aritmética entera únicamente; menor es mejor. |
| **Cobertura** | Porcentaje entero de artefactos explicados por una hipótesis. | Porcentaje entero (0–100); sin división en punto flotante. |
| **Garantía Daubert** | Estándar de admisibilidad forense: auditabilidad, testabilidad, metodología explícita. | Justificación legible; tablas abiertas. |

**Tabla 1. Resumen de Clases**

| Clase | Rol Científico | Comportamiento Determinista |
|---|---|---|
| `Artifact` | Primeridad: el signo bruto / dato forense | Identificadores enteros; sin mutación |
| `AbductiveHypothesis` | Terceridad: hábito candidato del atacante | Costo Ockham almacenado como `int`; comparable con `<` |
| `AbductiveResult` | Lista de salida ordenada | Ganadora seleccionada por clave de ordenación entera |
| `AbductiveIntentEngine` | Orquestador de inferencia | Misma entrada → misma salida (pipeline entero puro) |

**Tabla 2. Funciones Públicas**

| Función | Propósito | Tipo de Salida |
|---|---|---|
| `infer_habit(chain)` | Punto de entrada: abducir intención desde cadena de artefactos | `AbductiveResult` |
| `to_dict()` | Serializar estado para bitácoras de auditoría | Diccionario con claves string y valores enteros |
| `to_json()` | Exportar a JSON para revisión multiplataforma | Registro determinista legible por humanos |

### Glosario
- **Abducción**: Inferencia lógica que parte de una observación y concluye con la hipótesis que mejor la explica. Distinta de la deducción (necesariamente verdadera) y la inducción (probablemente verdadera).
- **Artefacto (forense)**: Cualquier rastro digital observable—línea de registro, clave de registro, fragmento de memoria—que sirve como evidencia.
- **Costo Ockham**: Tally entero de entidades no observadas o supuestos que una hipótesis requiere. El motor selecciona la hipótesis de menor costo.
- **Cobertura**: Porcentaje entero (0–100) que indica cuántos artefactos observados son explicados por una hipótesis dada.
- **Primeridad / Segundidad / Terceridad**: Las tres categorías universales de Charles S. Peirce. En este motor mapean a dato, correlación y ley explicatoria respectivamente.
- **Template**: Tabla predefinida y explícita de patrones de hipótesis. El motor carga estas tablas; no hay lógica condicional oculta.
- **Sistema Determinista**: Sistema donde condiciones iniciales idénticas siempre producen salidas idénticas. Aquí se logra mediante aritmética entera exclusiva y ordenación explícita.

### 【科学说明】 / Nota Científica
> **La Semiótica No Es Misticismo; Es Taxonomía de Sensores**
>
> La terminología tomada de Peirce, Eco y Grice puede sonar esotérica para científicos de laboratorio. No lo es. Considere un sensor: la lectura cruda de voltaje es **Primeridad**; el comparador que registra que el voltaje cruzó un umbral es **Segundidad**; el firmware que interpreta “cruce de voltaje = puerta abierta” es **Terceridad**. La teoría de los signos de Umberto Eco y los máximas conversacionales de H. P. Grice son descripciones formales de cómo los datos estructurados adquieren significado—igual que las tuberías de procesamiento de señales. Este motor usa esos términos como **categorías operacionales** de capas de inferencia, no como afirmaciones metafísicas. Cuando el módulo habla de “hábito” o “ley”, se refiere a un patrón reproducible extraído de cadenas enteras de artefactos, no a fuerzas ocultas.

---

РУССКИЙ Section:

## РУССКИЙ

### Что Это за Модуль?
Этот модуль — детерминированный механизм логического вывода для цифровой криминалистики. Он восстанавливает наиболее правдоподобное намерение атакующего на основе цепочки наблюдаемых криминалистических артефактов. Вместо вероятности или статистики используется **абдуктивное рассуждение** (вывод наилучшего объяснения), при котором конкурирующие гипотезы ранжируются по целочисленной **стоимости Оккама** — количеству ненаблюдаемых допущений, требуемых каждой гипотезой. Поскольку все операции выполняются точной целочисленной арифметикой, идентичные входные данные всегда дают одинаковую победившую гипотезу, обеспечивая полную воспроизводимость для научного и судебного анализа.

### Ключевые Понятия

| Понятие | Описание | Детерминированная Гарантия |
|---|---|---|
| **Абдукция (Пирс)** | Рассуждение, порождающее гипотезу, наилучшим образом объясняющую наблюдения. | Шаблоны явные; скрытых эвристик нет. |
| **Бритва Оккама** | Предпочитать объяснение с наименьшим числом ненаблюдаемых допущений. | Стоимость — неотрицательное целое, never float. |
| **Первичность (Primeridad)** | Сырой криминалистический артефакт: наблюдаемый данный, например запись журнала или хэш файла. | Инкапсулирован в неизменяемый объект `Artifact`. |
| **Вторичность (Segundidad)** | Грубая корреляция или столкновение между двумя артефактами. | Обнаружение через явные таблицы поиска, не нечёткую логику. |
| **Третичность (Terceridad)** | Привычка, закон или паттерн, связывающий артефакты в связную историю. | Возвращается как `AbductiveHypothesis`. |
| **Стоимость Оккама** | Число ненаблюдаемых допущений, вводимых гипотезой. | Только целочисленная арифметика; меньше — лучше. |
| **Покрытие** | Целочисленный процент входных артефактов, объясняемых гипотезой. | Целое число (0–100); без деления с плавающей точкой. |
| **Гарантия Доберта** | Стандарт судебной допустимости: проверяемость, аудируемость, явная методология. | Обоснование читаемо; шаблоны открыты. |

**Таблица 1. Обзор Классов**

| Класс | Научная Роль | Детерминированное Поведение |
|---|---|---|
| `Artifact` | Первичность: сырой знак / криминалистический данный | Целочисленные идентификаторы; мутация исключена |
| `AbductiveHypothesis` | Третичность: кандидатная привычка атакующего | Стоимость Оккама хранится как `int`; сравнение по `<` |
| `AbductiveResult` | Ранжированный выходной список | Победитель выбирается по целочисленному ключу сортировки |
| `AbductiveIntentEngine` | Оркестратор вывода | Одинаковый вход → одинаковый выход (чистый целочисленный конвейер) |

**Таблица 2. Открытые Функции**

| Функция | Назначение | Тип Выходных Данных |
|---|---|---|
| `infer_habit(chain)` | Главная точка входа: абдукция намерения из цепочки артефактов | `AbductiveResult` |
| `to_dict()` | Сериализация состояния для журналов аудита | Словарь со строковыми ключами и целочисленными значениями |
| `to_json()` | Экспорт в JSON для межплатформенного анализа | Детерминированная читаемая запись |

### Глоссарий
- **Абдукция**: Логический вывод, начинающийся с наблюдения и завершающийся гипотезой, наилучшим образом его объясняющей. Отличается от дедукции (обязательно истинной) и индукции (вероятно истинной).
- **Артефакт (криминалистический)**: Любой наблюдаемый цифровой след—строка журнала, ключ реестра, фрагмент памяти—служащий доказательством.
- **Стоимость Оккама**: Целочисленный подсчёт ненаблюдаемых сущностей или допущений, требуемых гипотезой. Механизм выбирает гипотезу с наименьшей стоимостью.
- **Покрытие**: Целочисленный процент (0–100), показывающий, сколько наблюдаемых артефактов объясняет данная гипотеза.
- **Первичность / Вторичность / Третичность**: Три универсальные категории Чарльза С. Пирса. В данном механизме они отображаются на данные, корреляцию и объясняющий закон соответственно.
- **Шаблон (Template)**: Явная, предварительно определённая таблица паттернов гипотез. Механизм загружает эти таблицы; скрытой условной логики нет.
- **Детерминированная Система**: Система, в которой идентичные начальные условия всегда дают идентичные выходные данные. Здесь достигается исключительно за счёт целочисленной арифметики и явной сортировки.

### 【Scientific Note】 / Научное Примечание
> **Семиотика — Не Мистицизм; Это Таксономия Датчиков**
>
> Терминология, заимствованная у Пирса, Эко и Грайса, иногда звучит оккультно для лабораторных учёных. Это не так. Вспомните лабораторный датчик: сырое напряжение — это **Первичность**; компаратор, регистрирующий пересечение порога, — **Вторичность**; прошивка, интерпретирующая «пересечение напряжения = дверь открыта», — **Третичность**. Теория знаков Умберто Эко и разговорные максимы Г. П. Грайса — это формальные описания того, как структурированные данные обретают смысл; по сути, те же конвейеры обработки сигналов. Этот механизм использует эти термины как **операционные категории** слоёв вывода, а не как метафизические утверждения. Когда модуль говорит о «привычке» или «законе», он имеет в виду воспроизводимый паттерн, извлечённый из целочисленных цепочек артефактов, а не потусторонние силы.

---

中文 Section:

## 中文

### 什么是本模块？
本模块是一个为数字取证研究设计的**确定性推理引擎**。它根据观测到的取证工件（artifact）链条，重构最合理的攻击者意图。引擎不使用概率或统计学，而是采用**溯因推理**（abductive reasoning，即推断最佳解释），并通过**奥卡姆成本**（Ockham cost）——每条假设所需未观测前提的整数计数——对竞争假设进行排序。由于所有运算均使用精确的整数算术，相同输入始终产生相同的获胜假设，从而确保科学审查与法律审查的完全可复现性。

### 核心概念

| 概念 | 说明 | 确定性保障 |
|---|---|---|
| **溯因推理（皮尔士）** | 生成最能解释观测数据的假设的推理方式。 | 模板显式；无隐藏启发式。 |
| **奥卡姆剃刀** | 优先选择所需未观测前提最少的解释。 | 成本为非负整数，绝不使用浮点数。 |
| **首位性（Primeridad）** | 原始取证工件：如日志条目、文件哈希等可观测数据。 | 封装为不可变 `Artifact` 对象。 |
| **第二位性（Segundidad）** | 两个工件之间的原始关联或碰撞。 | 通过显式查找表发现，不使用模糊逻辑。 |
| **第三位性（Terceridad）** | 将工件整合为连贯叙事的习惯、规律或模式。 | 以 `AbductiveHypothesis` 返回。 |
| **奥卡姆成本** | 某条假设引入的未观测前提数量。 | 仅使用整数运算；数值越低越优。 |
| **覆盖率** | 某条假设解释的输入工件占比。 | 整数百分比（0–100）；不进行浮点除法。 |
| **道伯特保障（Daubert）** | 取证可采信标准：可审计、可检验、方法显式。 | 推理依据人类可读；模板公开透明。 |

**表 1. 类概览**

| 类 | 科学角色 | 确定性行为 |
|---|---|---|
| `Artifact` | 首位性：原始符号 / 取证数据 | 整数标识符；不可变 |
| `AbductiveHypothesis` | 第三位性：候选攻击者习惯 | 奥卡姆成本以 `int` 存储；通过 `<` 比较 |
| `AbductiveResult` | 排序后的输出列表 | 获胜者由整数排序键选出 |
| `AbductiveIntentEngine` | 推理编排器 | 相同输入 → 相同输出（纯整数流水线） |

**表 2. 公共函数**

| 函数 | 用途 | 输出类型 |
|---|---|---|
| `infer_habit(chain)` | 主入口：从工件链条溯因推断意图 | `AbductiveResult` |
| `to_dict()` | 将对象状态序列化以供审计日志 | 字符串键、整数值的字典 |
| `to_json()` | 导出为 JSON 以供跨平台审查 | 人类可读的确定性记录 |

### 术语表
- **溯因推理**：从观察出发，得出最能解释该观察之假设的逻辑推理。与演绎（必然为真）和归纳（可能为真）相区别。
- **取证工件**：任何可观测的数字痕迹——日志行、注册表项、内存片段——均可用作证据。
- **奥卡姆成本**：某条假设所需的未观测实体或前提的整数计数。引擎选择成本最低的假设。
- **覆盖率**：整数百分比（0–100），表示某条假设能够解释多少已观测工件。
- **首位性 / 第二位性 / 第三位性**：查尔斯·S·皮尔士的三种普遍范畴。在本引擎中分别映射为数据、关联、解释规律。
- **模板（Template）**：预先定义的显式假设模式表。引擎加载这些表格；不存在隐藏的条件逻辑。
- **确定性系统**：初始条件相同则输出永远相同的系统。本模块通过排他性使用整数算术与显式排序实现这一点。

### 【科学说明】
> **符号学不是神秘主义；它是传感器分类学**
>
> 借自皮尔士、艾柯（Umberto Eco）与格赖斯（H. P. Grice）的术语有时会让实验科学家感到玄奥。事实并非如此。请设想一台实验室传感器：原始电压读数是**首位性**；记录电压越过阈值的比较器是**第二位性**；将“电压越过阈值 = 门已打开”加以解释的固件则是**第三位性**。艾柯的符号理论与格赖斯的会话准则，本质上都是关于“结构化数据如何获得意义”的形式化描述——与信号处理流水线并无不同。本引擎将这些术语用作推理层的**操作范畴**，而非形而上学主张。当模块提到“习惯”或“规律”时，它指的是从整数工件链条中提取的可复现模式，而非超自然力量。

---



I should place it once at the bottom. But to be safe and since the user said "License line" as a requirement, I'll include it once after all sections.

Double-check Chinese requirements:
- 艾柯 (not Eco) ✓
- 格赖斯 (not Grice) ✓
- 取证工件 (not 制品) ✓ — used 取证工件.
- 逻辑断裂 (not 裂缝) — this term hasn't come up in my draft because the docstring didn't mention "logic break/fracture" explicitly. It mentioned "cadena de artefactos". I should check if I need to include it. The requirement says "Chinese translations must use: ... 逻辑断裂 (not 裂缝)". This implies there is a concept of "break/fracture/gap" somewhere. The docstring doesn't explicitly mention "break" but says "explica esta cadena de artefactos". Maybe the architecture implies no logic breaks? Or maybe I should mention it in the context of explicit templates preventing hidden logic断裂? The user might have a specific module where "logic break" is a term. Let me see if I can weave it in naturally. Perhaps in the Chinese glossary or key concepts: "逻辑断裂" as logical gap? Or maybe the original text had something like "no lógica condicional oculta" -> no hidden conditional logic prevents logic断裂? Hmm.

Wait, the user's docstring says: "Tablas de templates son explícitas (no lógica condicional oculta)". This could relate to preventing logical breaks. But I didn't mention "logic break" in English/Spanish/Russian either. The requirement specifically targets Chinese translation for these terms, implying they appear somewhere. I should probably include "逻辑断裂" in the Chinese section where appropriate, perhaps when discussing explicit templates preventing gaps in reasoning. But the user didn't say I *must* include the concept, only that if translated, those specific terms must be used. Since I haven't used it, it's okay. But to be thorough and show I paid attention, maybe I should add a note about it. However, forcing it might be awkward. Let me see if there's a natural place. In the scientific note
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
