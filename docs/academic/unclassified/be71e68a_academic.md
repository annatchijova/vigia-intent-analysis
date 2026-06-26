<!--
VIGIA Academic Documentation
Module: be71e68a
Batch ID: vigia-doc-0105-be71e68a
Generated: 2026-05-20T14:56:47.867430+00:00
-->

---

## ENGLISH

### What Is This Module?

The **Cross-Case Pattern Library (CCPL)** is a deterministic forensic knowledge base. It operates as an exact-matching engine that compares active investigative signals—discrete textual indicators such as log entries, registry keys, or file signatures—against a curated collection of documented attack patterns. These patterns are derived from MITRE ATT&CK® Enterprise v14, public Cyber Threat Intelligence (CTI), and landmark incidents (e.g., SolarWinds).

The module does not employ probabilistic classifiers, neural networks, or approximations. Instead, it uses pure set algebra: a pattern matches **if and only if** its defined set of required signals is a subset of the active signal set. Every pattern and every match is **immutable**; once recorded, it cannot be altered in memory, ensuring chain-of-custody integrity throughout the investigation session. All scoring uses exact integer counts — the number of matched patterns, the number of triggered signals — with no floating-point weighting.

### Key Concepts

| Concept | Description | Scientific Role |
|---|---|---|
| **Attack Pattern** | A named, documented set of signals that collectively indicate a specific adversarial technique. | The unit of comparison; matched against the active signal set. |
| **Signal Set** | The collection of active investigative indicators currently under evaluation. | The input to the pattern-matching engine. |
| **Subset Matching** | A pattern fires if and only if all its required signals are present in the active signal set. | Exact Boolean logic; eliminates false positives from partial matches. |
| **Immutable Record** | A pattern record that cannot be changed after creation. | Preserves chain-of-custody integrity for every matched finding. |
| **MITRE ATT&CK® v14** | The standardized taxonomy of adversarial tactics and techniques. | Source of pattern definitions; provides court-defensible TTP labels. |
| **Exact Integer Scoring** | Match counts expressed as exact integers, not weighted probabilities. | Guarantees reproducible, auditable scoring across all platforms. |

### Core Operations

| Operation | Purpose |
|---|---|
| `match()` | Compares the active signal set against all known patterns; returns all matching patterns as an immutable list. |
| `add_pattern()` | Registers a new attack pattern into the library. Pattern is immediately frozen. |
| `query_by_technique()` | Retrieves all patterns associated with a specific MITRE ATT&CK® technique ID. |

### Glossary
1. **Attack Pattern** — A named set of signals constituting a documented adversarial technique.
2. **Chain-of-Custody** — The unbroken documentary record of evidence handling.
3. **CTI (Cyber Threat Intelligence)** — Publicly or commercially sourced information about known threat actors and their methods.
4. **Deterministic Matching** — A matching algorithm producing identical results for identical inputs, based on exact set algebra.
5. **Exact Integer Scoring** — Expressing match counts as whole numbers with no probabilistic weighting.
6. **Immutable Record** — A data structure that cannot be modified after creation.
7. **MITRE ATT&CK®** — A globally recognized knowledge base of adversary tactics and techniques.
8. **Signal** — A discrete, textual investigative indicator (e.g., a specific registry key path).
9. **Signal Set** — The collection of all active signals currently under investigation.
10. **Subset Matching** — The exact-match rule: a pattern fires only if all its required signals are present.

> **【Scientific Note】**
> Peirce/Eco/Grice terminology is NOT mysticism. In VIGÍA, a CCPL attack pattern is a Peircean *legisign*: a law-like rule that governs how a class of tokens (individual signal occurrences) produces meaning. Eco's notion of an interpretive code is operationalized as the pattern library itself — the shared codebook against which individual signs are decoded. Grice's maxim of relation ensures that only signals relevant to the active hypothesis are included in the signal set, preventing spurious matches.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## ESPAÑOL

### ¿Qué es este módulo?

La **Biblioteca de Patrones entre Casos (CCPL)** es una base de conocimiento forense determinista. Opera como un motor de coincidencia exacta que compara señales de investigación activas—indicadores textuales discretos como entradas de registro, claves de registro o firmas de archivos—contra una colección curada de patrones de ataque documentados. Estos patrones se derivan de MITRE ATT&CK® Enterprise v14, Inteligencia de Amenazas Cibernéticas (CTI) pública e incidentes emblemáticos (p. ej., SolarWinds).

El módulo no emplea clasificadores probabilísticos, redes neuronales ni aproximaciones. En cambio, utiliza álgebra de conjuntos pura: un patrón coincide **si y solo si** su conjunto definido de señales requeridas es un subconjunto del conjunto de señales activas. Cada patrón y cada coincidencia es **inmutable**. Toda la puntuación usa conteos enteros exactos — sin ponderación.

### Conceptos clave

| Concepto | Descripción | Rol científico |
|---|---|---|
| **Patrón de Ataque** | Conjunto nombrado y documentado de señales que indican colectivamente una técnica adversarial específica. | Unidad de comparación; comparada con el conjunto de señales activas. |
| **Conjunto de Señales** | Colección de indicadores de investigación activos actualmente bajo evaluación. | Entrada al motor de coincidencia de patrones. |
| **Coincidencia de Subconjunto** | Un patrón se activa si y solo si todas sus señales requeridas están presentes en el conjunto de señales activas. | Lógica booleana exacta; elimina falsos positivos de coincidencias parciales. |
| **Registro Inmutable** | Registro de patrón que no puede cambiarse tras su creación. | Preserva la integridad de la cadena de custodia para cada hallazgo coincidente. |
| **MITRE ATT&CK® v14** | Taxonomía estandarizada de tácticas y técnicas adversariales. | Fuente de definiciones de patrones; proporciona etiquetas TTP defendibles en tribunales. |
| **Puntuación Entera Exacta** | Conteos de coincidencias expresados como enteros exactos, no probabilidades ponderadas. | Garantiza puntuación reproducible y auditable en todas las plataformas. |

### Glosario
1. **Patrón de Ataque** — Conjunto nombrado de señales que constituyen una técnica adversarial documentada.
2. **Cadena de Custodia** — Registro documental ininterrumpido del manejo de la evidencia.
3. **CTI (Inteligencia de Amenazas Cibernéticas)** — Información sobre actores de amenaza conocidos y sus métodos, de fuentes públicas o comerciales.
4. **Coincidencia Determinista** — Algoritmo de coincidencia que produce resultados idénticos para entradas idénticas, basado en álgebra de conjuntos exacta.
5. **Puntuación Entera Exacta** — Expresar conteos de coincidencias como números enteros sin ponderación probabilística.
6. **Registro Inmutable** — Estructura de datos que no puede modificarse tras su creación.
7. **MITRE ATT&CK®** — Base de conocimiento reconocida globalmente de tácticas y técnicas adversariales.
8. **Señal** — Indicador de investigación textual y discreto (p. ej., una ruta de clave de registro específica).
9. **Conjunto de Señales** — Colección de todas las señales activas actualmente bajo investigación.
10. **Coincidencia de Subconjunto** — Regla de coincidencia exacta: un patrón se activa solo si todas sus señales requeridas están presentes.

> **【Nota Científica】**
> La terminología de Peirce/Eco/Grice no es misticismo. En VIGÍA, un patrón de ataque CCPL es un *legisigno* peirceano: una regla normativa que gobierna cómo una clase de tokens produce significado. La noción de Eco de código interpretativo se operacionaliza como la biblioteca de patrones misma. La máxima de relación de Grice garantiza que solo las señales relevantes para la hipótesis activa se incluyan en el conjunto de señales, previniendo coincidencias espurias.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## РУССКИЙ

### Что это за модуль?

**Библиотека межслучайных паттернов (CCPL)** — детерминированная криминалистическая база знаний. Она функционирует как движок точного сопоставления, сравнивающий активные следственные сигналы — дискретные текстовые индикаторы, такие как записи журналов, ключи реестра или сигнатуры файлов — с отобранной коллекцией задокументированных паттернов атак. Эти паттерны получены из MITRE ATT&CK® Enterprise v14, публичной Киберугрозовой разведки (CTI) и резонансных инцидентов (например, SolarWinds).

Модуль не использует вероятностные классификаторы, нейронные сети или приближения. Вместо этого применяется чистая алгебра множеств: паттерн совпадает **тогда и только тогда**, когда его определённое множество требуемых сигналов является подмножеством активного набора сигналов. Каждый паттерн и каждое совпадение **неизменяемы**. Вся оценка использует точные целочисленные счётчики.

### Ключевые концепции

| Концепция | Описание | Научная роль |
|---|---|---|
| **Паттерн атаки** | Именованный задокументированный набор сигналов, совокупно указывающих на конкретную состязательную технику. | Единица сравнения; сопоставляется с активным набором сигналов. |
| **Набор сигналов** | Коллекция активных следственных индикаторов, находящихся под оценкой в данный момент. | Входные данные для движка сопоставления паттернов. |
| **Подмножественное сопоставление** | Паттерн срабатывает тогда и только тогда, когда все его требуемые сигналы присутствуют в активном наборе сигналов. | Точная булева логика; исключает ложноположительные результаты от частичных совпадений. |
| **Неизменяемая запись** | Запись паттерна, которая не может быть изменена после создания. | Сохраняет целостность цепочки хранения для каждого найденного совпадения. |
| **MITRE ATT&CK® v14** | Стандартизированная таксономия состязательных тактик и техник. | Источник определений паттернов; обеспечивает судебно-защищаемые метки TTP. |
| **Точная целочисленная оценка** | Счётчики совпадений, выраженные точными целыми числами, а не взвешенными вероятностями. | Гарантирует воспроизводимую, аудируемую оценку на всех платформах. |

### Глоссарий
1. **Паттерн атаки** — Именованный набор сигналов, составляющих задокументированную состязательную технику.
2. **Цепочка хранения** — Непрерывный документарный учёт обращения с доказательствами.
3. **CTI (Киберугрозовая разведка)** — Публично или коммерчески полученная информация об известных угрозах и их методах.
4. **Детерминированное сопоставление** — Алгоритм сопоставления, дающий идентичные результаты для идентичных входных данных на основе точной алгебры множеств.
5. **Точная целочисленная оценка** — Выражение счётчиков совпадений целыми числами без вероятностного взвешивания.
6. **Неизменяемая запись** — Структура данных, которая не может быть изменена после создания.
7. **MITRE ATT&CK®** — Глобально признанная база знаний состязательных тактик и техник.
8. **Сигнал** — Дискретный текстовый следственный индикатор (напр., конкретный путь ключа реестра).
9. **Набор сигналов** — Коллекция всех активных сигналов, находящихся под расследованием в данный момент.
10. **Подмножественное сопоставление** — Правило точного совпадения: паттерн срабатывает только при наличии всех требуемых сигналов.

> **【Научное примечание】**
> Терминология Пирса, Эко и Грайса — не мистика. В VIGÍA паттерн атаки CCPL является пирсовским *легизнаком*: нормативным правилом, управляющим тем, как класс токенов порождает значение. Понятие интерпретационного кода Эко операционализируется как сама библиотека паттернов — общий кодовый словарь, по которому декодируются отдельные знаки. Максима отношения Грайса обеспечивает включение в набор сигналов только релевантных для активной гипотезы индикаторов, предотвращая ложные совпадения.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## 中文

### 这是什么模块？

**跨案例模式库（CCPL）**是确定性取证知识库。它作为精确匹配引擎运行，将主动调查信号——离散的文本指标，如日志条目、注册表键或文件签名——与已记录的攻击模式精选集合进行比对。这些模式来源于 MITRE ATT&CK® Enterprise v14、公开的网络威胁情报（CTI）以及标志性事件（如 SolarWinds）。

该模块不使用概率分类器、神经网络或近似值。而是使用纯集合代数：当且仅当其定义的所需信号集是活跃信号集的子集时，模式才匹配。每个模式和每次匹配都是**不可变的**；一旦记录，内存中无法更改，确保整个调查会话中的监管链完整性。所有评分使用精确整数计数——匹配模式数量、触发信号数量——无需加权。

### 关键概念

| 概念 | 描述 | 科学作用 |
|---|---|---|
| **攻击模式** | 共同指示特定对抗性技术的命名记录信号集。 | 比较单元；与活跃信号集进行匹配。 |
| **信号集** | 当前正在评估的活跃调查指标集合。 | 模式匹配引擎的输入。 |
| **子集匹配** | 当且仅当所有必需信号均存在于活跃信号集中时，模式才触发。 | 精确布尔逻辑；消除部分匹配的假阳性。 |
| **不可变记录** | 创建后无法更改的模式记录。 | 为每个匹配发现保护监管链完整性。 |
| **MITRE ATT&CK® v14** | 对抗性战术和技术的标准化分类体系。 | 模式定义来源；提供法庭可辩护的 TTP 标签。 |
| **精确整数评分** | 以精确整数而非加权概率表示的匹配计数。 | 保证所有平台上可复现、可审计的评分。 |

### 词汇表
1. **攻击模式** — 构成已记录对抗性技术的命名信号集。
2. **监管链** — 证据处理的连续书面记录。
3. **CTI（网络威胁情报）** — 关于已知威胁行为者及其方法的公开或商业来源信息。
4. **确定性匹配** — 基于精确集合代数对相同输入产生相同结果的匹配算法。
5. **精确整数评分** — 以整数表示匹配计数，不使用概率加权。
6. **不可变记录** — 创建后无法修改的数据结构。
7. **MITRE ATT&CK®** — 全球公认的对抗性战术和技术知识库。
8. **信号** — 离散的文本调查指标（如特定注册表键路径）。
9. **信号集** — 当前正在调查的所有活跃信号的集合。
10. **子集匹配** — 精确匹配规则：仅当所有必需信号均存在时模式才触发。

> **【科学说明】**
> 皮尔斯、艾柯和格赖斯的术语并非神秘主义。在 VIGÍA 中，CCPL 攻击模式是皮尔斯意义上的*法则符号*：一种规范性规则，支配一类标记如何产生意义。艾柯的解释代码概念被操作化为模式库本身——据此解码个别符号的共享代码本。格赖斯的关联准则确保信号集中只包含与活跃假说相关的信号，防止虚假匹配。

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
