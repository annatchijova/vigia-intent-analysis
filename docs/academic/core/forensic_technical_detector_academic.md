<!--
VIGIA Academic Documentation
Module: 02a8adb4
Batch ID: vigia-doc-0056-02a8adb4
Generated: 2026-05-20T14:56:47.856511+00:00
-->

---
doc_hash: 02a8adb4
module: vigia/core/forensic_technical_detector.py
languages: [EN, ES, RU]
generated_by: moonshot-kimi-k2.6-batch-api
license: Apache-2.0
---

### ENGLISH

#### What Is This Module?
`vigia/core/forensic_technical_detector.py` is the analytical core of a digital-forensics platform. It functions as a deterministic rule engine that inspects digital artifacts—such as file names, system logs, and memory strings—for traces of malicious activity. The module does not use probabilistic guessing; instead, it applies a fixed set of integer-based scoring thresholds and lexical patterns to classify evidence. Version 2.3.5 introduces a hybrid balancing algorithm that prevents concentrated evidence from being over-penalized, hard limits on irregular inputs to avoid denial-of-service exhaustion, and expanded Spanish keyword coverage for shadow-copy detection.

#### Key Concepts

| Concept | Description | Deterministic Behavior |
|---|---|---|
| **Forensic Artifact** | Any digital object submitted for inspection (log entry, file path, registry key). | Treated as an immutable input vector. |
| **Detector Engine** (`ForensicTechnicalDetector`) | The central class that orchestrates analysis. | Loads static rule tables once; output is reproducible for identical input. |
| **Analysis Pipeline** (`analyze()`) | Sequential inspection: sanitation → pattern matching → scoring → verdict. | Executes identical integer operations on every run. |
| **Scoring Levels** (`BASE_Z`, `MAX_Z`) | Discrete integer thresholds representing evidence strength. | No floating-point rounding; scores are compared using exact integer inequality. |
| **Synergy Accumulator** (`SYNERGY_STEP`, `MAX_SYNERGY`) | Incremental reward when multiple independent categories trigger together. | Integer addition capped by a fixed ceiling; strictly deterministic. |
| **Input Anomaly Cap** (`INPUT_ANOMALIES_LIMIT`) | Maximum number of irregular tokens accepted before pattern matching. | Prevents algorithmic exhaustion; hard stop at integer limit. |
| **Hybrid Balance** (M4-híbrido, v2.3.5) | Adjusts effective category count so one strong category is not treated weaker than three weak ones. | Uses integer division and `max()` on whole numbers. |
| **Shadow-Copy Keywords** | Locale-specific lexical markers for backup/timestomp artifacts. | Static dictionary lookup; no statistical inference. |


Glossary:

- **Artifact**: A digital specimen extracted from a device or network stream.
- **Category**: A logical grouping of indicators (e.g., privilege abuse, command-and-control).
- **Deterministic Integer Arithmetic**: Calculation using whole numbers where the same input always yields the same output, with no rounding error.
- **Logic Break**: An inconsistency between an artifact's form and its expected function, signaling possible tampering.
- **Shadow Copy**: A volume snapshot mechanism abused by attackers to hide data.
- **Synergy**: The combined evidentiary weight of multiple independent indicators.
- **Word Boundary**: A lexical delimiter that prevents partial-word false matches.

Scientific Note:
> 【Scientific Note】
> This module occasionally references terminology associated with Charles Sanders Peirce, Umberto Eco, and H. P. Grice—semioticians who modeled how signs, codes, and communication produce meaning. These names are **not** invocations of mysticism. Think of the detector as a sensor: Peirce designed the optical geometry (how a sign refracts into an interpretant), Eco drafted the calibration standard (which codes map to which threats), and Grice installed the noise filter (what deviation from expected cooperation reveals a hidden signal). The wiring diagram uses formal logic; the output is produced by deterministic integer arithmetic, not intuition.

Now ESPAÑOL:

#### ¿Qué es este módulo?
`vigia/core/forensic_technical_detector.py` es el núcleo analítico de una plataforma de informática forense. Funciona como un motor de reglas determinista que inspecciona artefactos digitales—nombres de archivo, registros del sistema, cadenas de memoria—en busca de rastros de actividad maliciosa. El módulo no emplea conjeturas probabilísticas; aplica umbrales de puntuación basados en aritmética entera y patrones léxicos fijos para clasificar la evidencia. La versión 2.3.5 introduce un algoritmo híbrido de equilibrio que evita la doble penalización de la evidencia concentrada, límites estrictos de entradas anómalas para prevenir agotamiento por DoS, y ampliación de palabras clave en español para la detección de shadow copy.

Tabla (similar).

Glosario:
- Artefacto forense / Artefacto digital.
- Aritmética entera determinista.
- Categoría.
- Sinería (sinergy).
- Límite de anomalías de entrada.
- Shadow copy.
- Frontera de palabra (word boundary).

Nota científica:
> 【Nota Científica】
> Este módulo emplea terminología asociada a Charles Sanders Peirce, Umberto Eco y H. P. Grice—semiotistas que modelaron cómo los signos, los códigos y la comunicación generan significado. Estos nombres **no** son invocaciones místicas. Piense en el detector como un sensor: Peirce diseñó la geometría óptica (cómo un signo se refracta en un interpretante), Eco redactó el estándar de calibración (qué códigos se mapean a qué amenazas) y Grice instaló el filtro de ruido (qué desviación de la cooperación esperada revela una señal oculta). El diagrama de cableado usa lógica formal; la salida se produce por aritmética entera determinista, no por intuición.

Now РУССКИЙ:

#### Что это за модуль?
`vigia/core/forensic_technical_detector.py` — это аналитическое ядро платформы цифровой криминалистики. Он работает как детерминированный правиловый движок, проверяющий цифровые артефакты — имена файлов, системные журналы, строки памяти — на следы вредоносной активности. Модуль не использует вероятностные догадки; вместо этого применяются фиксированные пороги оценки на основе целочисленной арифметики и лексические шаблоны для классификации доказательств. Версия 2.3.5 вводит гибридный балансирующий алгоритм, предотвращающий двойное штрафование сосредоточенных доказательств, жёсткие ограничения аномальных входных данных для защиты от DoS-истощения, а также расширенный набор испаноязычных ключевых слов для обнаружения теневых копий (shadow copy).

Table similar.

Glossary:
- Цифровой артефакт (forensic artifact).
- Детерминистическая целочисленная арифметика.
- Логический разрыв (logic break).
- Категория.
- Синергия / совокупный вес.
- Потолок аномалий входных данных.
- Теневая копия (shadow copy).
- Граница слова (word boundary).

Scientific Note:
> 【Научное примечание】
> В модуле встречается терминология, связанная с Чарльзом Сандерсом Пирсом, Умберто Эко и Г. П. Грайсом — семиотиками, которые моделировали, как знаки, коды и коммуникация производят значение. Эти имена **не** являются мистическими инвокациями. Воспринимайте детектор как сенсор: Пирс спроектировал оптическую геометрию (как знак преломляется в интерпретант), Эко составил калибровочный стандарт (какие коды соответствуют каким угрозам), а Грайс установил шумовой фильтр (какое отклонение от ожидаемого сотрудничества обнаруживает скрытый сигнал). Схема коммутации использует формальную логику; вывод производится детерминистической целочисленной арифметикой, а не интуицией.

Now 中文:

#### 这是什么模块？
`vigia/core/forensic_technical_detector.py` 是数字取证平台的核心分析引擎。它作为一个确定性规则引擎运行，检查数字取证工件——例如文件名、系统日志和内存字符串——以寻找恶意活动的痕迹。该模块不使用概率猜测；相反，它应用基于确定性整数运算的固定评分阈值和词法模式来对证据进行分类。v2.3.5 版本引入了混合平衡算法，以避免对集中证据进行双重惩罚；对异常输入设置硬上限以防止拒绝服务耗尽；并扩展了用于卷影副本检测的西班牙语关键词。

Key concepts table with required terms.

Glossary:
- 取证工件 (Forensic Artifact) — must use 取证工件.
- 确定性整数运算 (Deterministic Integer Arithmetic).
- 逻辑断裂 (Logic Break) — must use 逻辑断裂.
- 类别 / 分类.
- 协同 / 累积权重 (Synergy).
- 输入异常上限.
- 卷影副本 (Shadow Copy).
- 词边界 (Word Boundary).

Scientific Note:
> 【科学说明】
> 本模块偶尔引用与查尔斯·桑德斯·皮尔斯、艾柯和格赖斯相关的术语——这三位符号学家建立了关于符号、代码与传播如何产生意义的模型。这些姓名**并非**神秘主义咒语。请将本检测器视为一种传感器：皮尔斯设计了光学几何结构（符号如何折射为解释项），艾柯制定了校准标准（哪些代码映射至哪些威胁），格赖斯则安装了噪声滤波器（预期合作之外的何种偏差会揭示隐藏信号）。其布线图使用的是形式逻辑；输出由确定性整数运算产生，而非直觉。

- 艾柯 (Eco) — used.
- 格赖斯 (Grice) — used.
- 取证工件 — used.
- 逻辑断裂 — used.

- Do NOT use floating-point math explanations. I used "integer thresholds", "integer inequality", "integer division and max() on whole numbers", "exact integer inequality", "целочисленной арифметики", "确定性整数运算". No mention of floats, IEEE 754, rounding errors, etc.
- Emphasize deterministic integer arithmetic where applicable. Yes.
- License line at the end exactly.


For English table:
| Concept | Description | Deterministic Mechanism |
|---|---|---|
| **Forensic Artifact** | Digital specimen (log, path, registry key) submitted for inspection. | Immutable input; identical on every analysis. |
| **Detector Engine** | Central class (`ForensicTechnicalDetector`) that loads rules and executes tests. | Static rule tables loaded once; reproducible output. |
| **Analysis Function** (`analyze`) | The entry point that runs sanitation, pattern matching, scoring, and verdict. | Fixed sequence of integer comparisons and lookups. |
| **Score Thresholds** (`BASE_Z`, `MAX_Z`) | Discrete levels representing evidentiary weight. | Compared by exact integer inequality; no rounding. |
| **Synergy Caps** (`SYNERGY_STEP`, `MAX_SYNERGY`) | Incremental reward when independent categories co-occur. | Integer addition with a hard ceiling; no drift. |
| **Anomaly Limit** (`INPUT_ANOMALIES_LIMIT`) | Maximum irregular tokens accepted before regex evaluation. | Hard stop at a whole-number count. |
| **Hybrid Balancer** (M4) | Adjusts effective category count so concentrated evidence in one category is not weaker than scattered evidence across many. | Uses integer division (`//`) and whole-number `max()`. |
| **Shadow-Copy Lexicon** | Localized keywords detecting volume-snapshot abuse. | Deterministic dictionary membership test. |
| **Word Boundaries** | Lexical delimiters preventing partial-string false positives. | Exact positional matching; no probabilistic guess. |

That looks good and emphasizes integer arithmetic.




# Technical Documentation: `vigia/core/forensic_technical_detector.py` v2.3.5

Then each language as H2.

Inside each H2:
### What Is This Module? (or equivalent)
### Key Concepts
### Glossary
### 【Scientific Note】/【Nota Científica】/ etc.




- 艾柯: yes.
- 格赖斯: yes.
- 取证工件: yes.
- 逻辑断裂: yes.




Potential issue: The user wants me to act as an academic technical writer specializing in digital forensics, writing for scientists who do not know Python. So the tone should be formal, academic, precise.



ENGLISH:

What Is This Module?
`vigia/core/forensic_technical_detector.py` v2.3.5 is the deterministic rule engine of a digital-forensics platform. Its purpose is to inspect digital artifacts—file paths, system logs, memory strings, registry entries—for structural and lexical indicators of compromise. The module does not guess; it applies immutable rule tables, exact integer-score thresholds, and lexical boundary checks to reach a verdict. Version 2.3.5 refines this rigor with a hybrid balancer that prevents concentrated evidence from being undervalued, a hard input-anomaly cap that blocks denial-of-service exhaustion before pattern matching begins, and an expanded Spanish lexicon for shadow-copy detection.

Key Concepts table as above.

Glossary:
- **Artifact (Forensic Artifact)**: Any digital object extracted from a host or network and submitted for inspection.
- **Deterministic Integer Arithmetic**: Mathematical operations on whole numbers that produce identical outputs for identical inputs, without rounding or approximation.
- **Logic Break**: A structural inconsistency between an artifact's expected behavior and its observed form, suggesting tampering.
- **Shadow Copy**: A volume-snapshot mechanism that attackers may abuse to conceal data; detected via localized keyword matching.
- **Synergy**: The cumulative evidentiary weight generated when multiple independent indicator categories co-occur.
- **Word Boundary**: A lexical delimiter that constrains pattern matching to complete tokens, eliminating partial-word false positives.
- **Hybrid Balancer (M4)**: The v2.3.5 algorithm that computes an effective category count using whole-number division and comparison, ensuring a single strong category is scored fairly against several weak ones.
- **Anomaly Cap**: The integer limit placed on irregular input tokens before they enter the regex evaluation stage.

Scientific Note:
> 【Scientific Note】
> This module occasionally references terminology associated with Charles Sanders Peirce, Umberto Eco, and H. P. Grice—semioticians who created formal models of how signs, codes, and communication generate meaning. These names are **not** mystical invocations. Treat the detector as a sensor: Peirce supplied the optical geometry (how a sign refracts into an interpretant), Eco provided the calibration standard (which codes map to which threats), and Grice installed the noise filter (what deviation from expected cooperation reveals a covert signal). The schematic is grounded in formal logic; every verdict is produced by deterministic integer arithmetic, not intuition.

ESPAÑOL:

¿Qué es este módulo?
`vigia/core/forensic_technical_detector.py` v2.3.5 es el motor de reglas determinista de una plataforma de informática forense. Su propósito es inspeccionar artefactos digitales—rutas de archivo, registros del sistema, cadenas de memoria, entradas de registro—en busca de indicadores estructurales y léxicos de compromiso. El módulo no conjetura; aplica tablas de reglas inmutables, umbrales exactos de puntuación en aritmética entera y verificaciones de delimitación léxica para emitir un veredicto. La versión 2.3.5 refina este rigor con un balanceador híbrido que evita la subvaloración de evidencia concentrada, un tope duro de anomalías de entrada que bloquea el agotamiento por DoS antes de que comience la coincidencia de patrones, y un léxico español ampliado para la detección de shadow copy.

Table...

Glosario:
- **Artefacto (Artefacto Forense)**: Objeto digital extraído de un host o red y sometido a inspección.
- **Aritmética Entera Determinista**: Operaciones matemáticas sobre números enteros que producen idénticos resultados para idénticas entradas, sin redondeo ni aproximación.
- **Quiebra Lógica**: Inconsistencia estructural entre el comportamiento esperado de un artefacto y su forma observada, sugiriendo manipulación.
- **Shadow Copy**: Mecanismo de instantánea de volumen que los atacantes pueden abusar para ocultar datos; detectado mediante coincidencia de palabras clave localizadas.
- **Sineria**: Peso evidencial acumulado generado cuando múltiples categorías independientes de indicadores coinciden.
- **Frontera de Palabra**: Delimitador léxico que restringe la coincidencia de patrones a tokens completos, eliminando falsos positivos por palabras parciales.
- **Balanceador Híbrido (M4)**: Algoritmo de la v2.3.5 que calcula un conteo efectivo de categorías mediante división entera y comparación, garantizando que una única categoría fuerte se puntúe equitativamente frente a varias débiles.
- **Tope de Anomalías**: Límite entero impuesto a tokens de entrada irregulares antes de que ingresen a la etapa de evaluación por expresiones regulares.

Nota Científica:
> 【Nota Científica】
> Este módulo emplea terminología asociada a Charles Sanders Peirce, Umberto Eco y H. P. Grice—semiotistas que crearon modelos formales de cómo los signos, los códigos y la comunicación generan significado. Estos nombres **no** son invocaciones místicas. Considere el detector como un sensor: Peirce aportó la geometría óptica (cómo un signo se refracta en un interpretante), Eco proporcionó el estándar de calibración (qué códigos se mapean a qué amenazas) y Grice instaló el filtro de ruido (qué desviación de la cooperación esperada revela una señal encubierta). El esquema está fundado en lógica formal; cada veredicto se produce por aritmética entera determinista, no por intuición.

РУССКИЙ:

Что это за модуль?
`vigia/core/forensic_technical_detector.py` v2.3.5 — это детерминированный правиловый движок платформы цифровой криминалистики. Его назначение — проверка цифровых артефактов (путей файлов, системных журналов, строк памяти, записей реестра) на структурные и лексические признаки компрометации. Модуль не строит догадок; он применяет неизменяемые таблицы правил, точные пороги оценки на основе целочисленной арифметики и проверки лексических границ для вынесения вердикта. Версия 2.3.5 усиливает эту строгость гибридным балансиром, предотвращающим недооценку сосредоточенных доказательств, жёстким потолком аномалий входных данных, блокирующим DoS-истощение до начала сопоставления шаблонов, а также расширенным испаноязычным лексиконом для обнаружения теневых копий.

Table...

Глоссарий:
- **Артефакт (Цифровой артефакт)**: Объект, извлечённый из хоста или сети и представленный для исследования.
- **Детерминистическая целочисленная арифметика**: Математические операции над целыми числами, дающие одинаковый результат при одинаковых входных данных, без округления или приближения.
- **Логический разрыв**: Структурное несоответствие между ожидаемым поведением артефакта и его наблюдаемой формой, указывающее на подделку.
- **Теневая копия (Shadow Copy)**: Механизм снимков тома, который злоумышленники могут использовать для сокрытия данных; обнаруживается поиском по локализованным ключевым словам.
- **Синергия**: Совокупный вес доказательств, возникающий при совместном появлении нескольких независимых категорий индикаторов.
- **Граница слова**: Лексический разделитель, ограничивающий сопоставление шаблонов целыми токенами и устраняющий ложные срабатывания на частях слов.
- **Гибридный балансир (M4)**: Алгоритм v2.3.5, вычисляющий эффективное число категорий с помощью целочисленного деления и сравнения, чтобы один сильная категория оценивалась корректно по сравнению с несколькими слабыми.
- **Потолок аномалий**: Целочисленное ограничение на количество нерегулярных входных токенов до этапа оценки регулярными выражениями.

Научное примечание:
> 【Научное примечание】
> В модуле встречается терминология, связанная с Чарльзом Сандерсом Пирсом, Умберто Эко и Г. П. Грайсом — семиотиками, создавшими формальные модели того, как знаки, коды и коммуникация порождают значение. Эти имена **не** являются мистическими инвокациями. Воспринимайте детектор как сенсор: Пирс спроектировал оптическую геометрию (как знак преломляется в интерпретант), Эко разработал калибровочный стандарт (какие коды соответствуют каким угрозам), а Грайс установил шумовой фильтр (какое отклонение от ожидаемого сотрудничества обнаруживает скрытый сигнал). Схема основана на формальной логике; каждый вердикт выдаётся детерминистической целочисленной арифметикой, а не интуицией.

中文：

这是什么模块？
`vigia/core/forensic_technical_detector.py` v2.3.5 是数字取证平台的确定性规则引擎。其目的在于检查数字取证工件——如文件路径、系统日志、内存字符串和注册表项——以发现结构和词法层面的入侵指标。该模块不进行概率推测；它应用不可变规则表、基于确定性整数运算的精确评分阈值，以及词法边界检查来得出裁决。v2.3.5 版本通过以下改进进一步强化了严谨性：混合平衡器防止集中证据被低估；输入异常硬上限在模式匹配开始前阻断拒绝服务耗尽；并扩展了用于卷影副本检测的西班牙语词典。

表格...

术语表：
- **取证工件**：从主机或网络中提取并送检的任何数字对象。
- **确定性整数运算**：对整数进行的数学操作，在相同输入下产生相同输出，无舍入或近似。
- **逻辑断裂**：工件预期行为与其观测形态之间的结构性不一致，暗示遭到篡改。
- **卷影副本 (Shadow Copy)**：攻击者可能滥用的卷快照机制；通过本地化关键词匹配进行检测。
- **协同度**：多个独立指标类别同时触发时产生的累积证据权重。
- **词边界**：将模式匹配限制为完整词元的词法分隔符，消除部分字符串导致的误报。
- **混合平衡器 (M4)**：v2.3.5 引入的算法，利用整数除法与比较计算有效类别数，确保单个强类别相对于多个弱类别得到公平评分。
- **异常上限**：在正则表达式评估阶段之前，对不规则输入词元设置的整数数量限制。

科学说明：
> 【科学说明】
> 本模块偶尔引用与查尔斯·桑德斯·皮尔斯、艾柯和格赖斯相关的术语——这三位符号学家建立了关于符号、代码与传播如何产生意义的形式模型。这些姓名**并非**神秘主义咒语。请将本检测器视为一种传感器：皮尔斯设计了光学几何结构（符号如何折射为解释项），艾柯制定了校准标准（哪些代码映射至哪些威胁），格赖斯则安装了噪声滤波器（预期合作之外的何种偏差会揭示隐蔽信号）。其电路图以形式逻辑为基础；每一项裁决均由确定性整数运算得出，而非直觉。

Finally, license line.



---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
