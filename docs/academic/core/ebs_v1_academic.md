<!--
VIGIA Academic Documentation
Module: bb8bfa2d
Batch ID: vigia-doc-0048-bb8bfa2d
Generated: 2026-05-20T14:56:47.854843+00:00
-->

# Module Documentation: `vigia/core/ebs_v1.py`

## ENGLISH

**What Is This Module?**

This document describes the **Evidence Bundle Specification v1.0 (EBS v1)**—the lowest layer of a digital-forensics architecture. It is a pure data schema: a set of formal rules that define how an investigative instrument records its findings before any interpretation, narrative generation, or cryptographic sealing occurs.

Think of it as the **standardized label on a specimen vial**. The label does not analyze the specimen, tell a story about it, or lock the freezer. It simply guarantees that every laboratory instrument describes the specimen using the same fields, units, and relationships. In this architecture, cryptographic sealing and linguistic narrative are handled by separate, external modules, ensuring that a compromised tool cannot legitimize its own false output.

**Key Concepts — Core Data Containers**

| Concept | Role in the Schema | Deterministic Properties |
|---|---|---|
| **ForensicBundle** | The master container. An immutable envelope that aggregates all instrument outputs, graphs, decisions, and policy rules. | Never self-hashes. Integrity is added later by an external builder. |
| **SignalOutput** | A single, canonical reading from one forensic tool. | z_score computed as an exact rational deviation: integer-scaled difference from baseline mean divided by integer Median Absolute Deviation (MAD). No floating-point approximation. |
| **EvidenceEdge** | A directed dependency between two signals. | Stability π_ij is recorded as an exact count of appearances across 500 bootstrap resamples (integer count / 500). |
| **EvidenceGraph** | The full map of how signals depend on one another. | Produced by an external stability engine. Its identifier (graph_hash) is assigned externally; the graph itself contains no self-referential validation logic. |
| **DecisionTrace** | The mathematical result of a risk-bounded evaluation. | 100% numeric fields. Contains an explicit ABSTAIN exit state when uncertainty exceeds policy thresholds. No references to AI models or natural-language inference. |
| **PolicyRule / PolicySpec** | Declarative constraints that define acceptable risk boundaries. | Pure logical structure. Used by the decision layer to compute deterministic thresholds. |
| **ActionRecord** | A log of an executed intervention. | Designed under the **I4** principle: zero implicit effects. Every consequence must be explicitly declared in the record. |

**Key Concepts — Mathematical and Policy Primitives**

| Primitive | Description |
|---|---|
| z_score | Deterministic standardized deviation using median absolute deviation (MAD) via integer-safe rational arithmetic. |
| π_ij | Bootstrap frequency of an edge over 500 resamples, expressed as exact rational count/500. |
| ENFSI label | Verbal translation of a likelihood ratio using fixed categorical scale. |
| ABSTAIN | Formal exit state when uncertainty exceeds risk bounds. |

**Supporting Functions**

| Function | Purpose | Deterministic Guarantee |
|---|---|---|
| **make_default_policy()** | Generates a baseline policy template. | Identical input always yields identical rule structure. |
| **enfsi_label()** | Translates a Likelihood Ratio into a verbal category. | Maps exact ratio intervals to fixed ENFSI scale labels. No probabilistic rounding. |
| **to_dict()** | Serializes the bundle contents into a standardized dictionary. | Excludes integrity fields; those are appended only by the external BundleBuilder. |
| **is_forensically_stable()** | Checks whether a component meets minimum bootstrap stability. | Boolean verdict based on integer threshold comparison. |
| **global_stability()** | Computes overall system stability. | Penalized by **graph fracture** (disconnected components). Uses integer-weighted scoring. |
| **connected_components()** | Identifies isolated subgraphs within the evidence map. | Deterministic graph traversal; output depends solely on edge presence, not on stochastic sampling. |
| **get_rule()** | Retrieves a specific policy constraint by identifier. | Exact lookup; no heuristic search. |

**Integrity and Externalization Rules**

- No self-hashing: Bundle never seals itself.
- No LLM references: No model names, no prompt fragments.
- No business logic: Pure structure.
- External attestation: bundle_builder.py handles graph_hash and integrity.

**Glossary**

- **Bootstrap Stability (π_ij)**: The proportion of 500 resampled graphs in which a specific evidence edge appears. Stored as an exact rational number (count ÷ 500).
- **Deterministic Integer Arithmetic**: Mathematical operations performed with integers or fixed-scale rationals, ensuring that the same input always produces the exact same output without rounding errors.
- **ENFSI Scale**: A standardized verbal scale used by European forensic institutes to express the weight of evidence. This module maps exact likelihood-ratio intervals to scale categories.
- **External Attestation**: Cryptographic sealing performed by an independent module (bundle_builder), rather than by the data producer. Prevents self-certification of corrupted data.
- **Graph Fracture**: The disconnection of an evidence graph into isolated components. Logically penalizes global stability because fractured graphs represent broken chains of inference.
- **I4 (No Implicit Effects)**: A design axiom requiring that every action record explicitly declare all its consequences; hidden side-effects are forbidden.
- **Layer 0**: The immutable foundation of the architecture. Contains only data contracts and no business logic, hashing, or narrative processing.
- **Likelihood Ratio (LR)**: A deterministic comparison of two competing hypotheses, expressed as an integer or rational value.
- **Risk-Bounded Decision**: A choice computed from explicit numerical thresholds. The system may return ABSTAIN when no option satisfies the safety bounds.

**Scientific Note**

【Scientific Note】Peirce, Eco, and Grice Are Not Mysticism; They Are Sensors

Certain terms inherited from semiotics and philosophy of language—abduction (Peirce), interpretive constraints (Eco), and cooperative maxims (Grice)—appear in forensic-trace documentation. They are **not** mystical or literary flourishes.

Think of them as **sensors for logical structure**. A thermocouple detects temperature without "understanding" heat; a mass spectrometer detects mass-to-charge ratio without "believing" in chemistry. Likewise:
- **Abduction** is a hypothesis-generation sensor. It detects the most economical explanatory pattern among competing traces.
- **Eco's constraints** act as a noise-filter sensor. They delimit which interpretations are admissible given the finite evidence set.
- **Gricean cooperation** functions as a protocol-synchronization sensor. It detects whether two communicating subsystems share the same background assumptions.

These constructs detect **semio-logical coherence**, not ghosts in the machine. Treating them as formal pattern-recognition instruments keeps the architecture rigorous and auditable.

---

## ESPAÑOL

**¿Qué es este módulo?**

Este documento describe la **Especificación de Paquete de Evidencia v1.0 (EBS v1)**—la capa más baja de una arquitectura de informática forense. Es un esquema de datos puros: un conjunto de reglas formales que definen cómo un instrumento de investigación registra sus hallazgos antes de cualquier interpretación, generación de narrativas o sellado criptográfico.

Piénsese en él como la **etiqueta estandarizada de un vial de muestra**. La etiqueta no analiza la muestra, no cuenta una historia sobre ella ni cierra la cerradura del congelador. Simplemente garantiza que todo instrumento de laboratorio describa la muestra usando los mismos campos, unidades y relaciones. En esta arquitectura, el sellado criptográfico y la narrativa lingüística son gestionados por módulos externos e independientes, asegurando que una herramienta comprometida no pueda legitimar su propia salida falsa.

**Conceptos Clave**

| Concepto | Rol en el esquema | Propiedades deterministas |
|---|---|---|
| **ForensicBundle** | Contenedor maestro. Sobre inmutable que agrega todas las salidas de instrumentos, grafos, decisiones y reglas de política. | Nunca se autohashea. La integridad se añade posteriormente por un constructor externo. |
| **SignalOutput** | Lectura canónica única de una herramienta forense. | z_score calculado como desviación racional exacta: diferencia escalada en enteros respecto a la media basal dividida por la Desviación Absoluta Mediana (MAD) entera. Sin aproximaciones de punto flotante. |
| **EvidenceEdge** | Dependencia dirigida entre dos señales. | La estabilidad π_ij se registra como un conteo exacto de apariciones en 500 remuestreos bootstrap (conteo entero / 500). |
| **EvidenceGraph** | Mapa completo de cómo las señales dependen unas de otras. | Producido por un motor de estabilidad externo. Su identificador (graph_hash) se asigna externamente. |
| **DecisionTrace** | Resultado matemático de una evaluación de riesgo acotado. | Campos 100% numéricos. Contiene un estado de salida explícito ABSTAIN cuando la incertidumbre excede los umbrales de política. |
| **PolicyRule / PolicySpec** | Restricciones declarativas que definen límites aceptables de riesgo. | Estructura lógica pura. |
| **ActionRecord** | Registro de una intervención ejecutada. | Diseñado bajo el principio **I4**: cero efectos implícitos. |

**Funciones de soporte**

| Función | Propósito | Garantía determinista |
|---|---|---|
| **make_default_policy()** | Genera una plantilla de política basal. | La misma entrada siempre produce la misma estructura de reglas. |
| **enfsi_label()** | Traduce una Razón de Verosimilitud a una categoría verbal. | Mapea intervalos exactos de razón a etiquetas fijas de la escala ENFSI. Sin redondeo probabilístico. |
| **to_dict()** | Serializa el contenido del paquete en un diccionario estandarizado. | Excluye campos de integridad. |
| **is_forensically_stable()** | Verifica si un componente cumple la estabilidad bootstrap mínima. | Veredicto booleano basado en comparación de umbrales enteros. |
| **global_stability()** | Calcula la estabilidad global del sistema. | Penalizada por **fractura del grafo**. Utiliza puntuación con pesos enteros. |
| **connected_components()** | Identifica subgrafos aislados dentro del mapa de evidencia. | Recorrido determinista del grafo. |
| **get_rule()** | Recupera una restricción de política específica por identificador. | Búsqueda exacta; sin heurística. |

**Glosario**

- **Estabilidad Bootstrap (π_ij)**: La proporción de grafos remuestreados (de 500) en la que aparece una arista de evidencia específica. Almacenada como número racional exacto (conteo ÷ 500).
- **Aritmética Entera Determinista**: Operaciones matemáticas realizadas con enteros o racionales de escala fija.
- **Escala ENFSI**: Escala verbal estandarizada utilizada por institutos forenses europeos para expresar el peso de la evidencia.
- **Atestación Externa**: El sellado criptográfico de un paquete realizado por un módulo independiente (bundle_builder). Previene la autoverificación de datos corruptos.
- **Fractura del Grafo**: La desconexión de un grafo de evidencia en componentes aisladas. Penaliza la estabilidad global.
- **I4 (Sin Efectos Implícitos)**: Axioma de diseño que exige que todo registro de acción declare explícitamente todas sus consecuencias.
- **Capa 0**: La fundación inmutable de la arquitectura. Contiene únicamente contratos de datos.
- **Razón de Verosimilitud (LR)**: Comparación determinista entre dos hipótesis competidoras.
- **Decisión de Riesgo Acotado**: Elección calculada a partir de umbrales numéricos explícitos. El sistema puede devolver ABSTAIN.

**Nota Científica**

【Nota Científica】Peirce, Eco y Grice no son misticismo; son sensores

Algunos términos heredados de la semiótica y la filosofía del lenguaje—abducción (Peirce), restricciones interpretativas (Eco) y máximas cooperativas (Grice)—aparecen en la documentación de rastros forenses. No son adornos místicos ni literarios.

Piénsese en ellos como **sensores de estructura lógica**. Un termopar detecta temperatura sin "entender" el calor; un espectrómetro de masas detecta la relación masa/carga sin "creer" en la química. Del mismo modo:
- La **abducción** es un sensor de generación de hipótesis. Detecta el patrón explicativo más económico entre rastros competidores.
- Las **restricciones de Eco** actúan como un sensor de filtrado de ruido. Delimitan qué interpretaciones son admisibles dado el conjunto finito de evidencia.
- La **cooperación griceana** funciona como un sensor de sincronización de protocolo. Detecta si dos subsistemas comunicantes comparten los mismos supuestos de fondo.

Estos constructos detectan **coherencia semio-lógica**, no fantasmas en la máquina. Tratarlos como instrumentos formales de reconocimiento de patrones mantiene la arquitectura rigurosa y auditable.

---

## РУССКИЙ

**Что представляет собой этот модуль?**

Настоящий документ описывает **Спецификацию пакета доказательств v1.0 (EBS v1)** — низший слой архитектуры цифровой криминалистики. Это чистая схема данных: формальный набор правил, определяющих, как следственный инструмент фиксирует свои находки до любой интерпретации, генерации повествования или криптографического запечатывания.

Воспринимайте её как **стандартизированную этикетку на пробирке с образцом**. Этикетка не анализирует образец, не рассказывает о нём историю и не запирает морозильную камеру. Она лишь гарантирует, что каждый лабораторный прибор описывает образец с использованием одних и тех же полей, единиц измерения и связей. В данной архитектуре криптографическое запечатывание и языковое повествование выполняются отдельными внешними модулями.

**Ключевые концепции**

| Концепция | Роль в схеме | Детерминированные свойства |
|---|---|---|
| **ForensicBundle** | Главный контейнер. Неизменяемый конверт, агрегирующий все выходные данные приборов, графы, решения и правила политик. | Никогда не хеширует себя сам. |
| **SignalOutput** | Одна каноническая запись от одного криминалистического инструмента. | z_score вычисляется как точное рациональное отклонение. Без приближений с плавающей точкой. |
| **EvidenceEdge** | Направленная зависимость между двумя сигналами. | Стабильность π_ij фиксируется как точное число появлений в 500 бутстрэп-выборках (целое счётное / 500). |
| **EvidenceGraph** | Полная карта зависимостей между сигналами. | Производится внешним движком стабильности. |
| **DecisionTrace** | Математический результат оценки с ограничением риска. | Поля на 100% числовые. Содержит явное состояние выхода ABSTAIN. |
| **PolicyRule / PolicySpec** | Декларативные ограничения, задающие допустимые границы риска. | Чистая логическая структура. |
| **ActionRecord** | Журнал выполненного вмешательства. | Спроектирован по принципу **I4**: нулевые неявные эффекты. |

**Вспомогательные функции**

| Вспомогательная функция | Назначение | Детерминированная гарантия |
|---|---|---|
| **make_default_policy()** | Генерирует базовый шаблон политики. | При идентичном входе всегда выдаёт идентичную структуру правил. |
| **enfsi_label()** | Преобразует отношение правдоподобия в вербальную категорию. | Отображает точные интервалы отношений на фиксированные категории шкалы ENFSI. |
| **to_dict()** | Сериализует содержимое пакета в стандартизированный словарь. | Исключает поля целостности. |
| **is_forensically_stable()** | Проверяет, соответствует ли компонент минимальной бутстрэп-устойчивости. | Булев вердикт на основе сравнения целочисленных порогов. |
| **global_stability()** | Вычисляет глобальную устойчивость системы. | Штрафуется за **разрыв графа**. |
| **connected_components()** | Выявляет изолированные подграфы в карте доказательств. | Детерминированный обход графа. |
| **get_rule()** | Извлекает конкретное ограничение политики по идентификатору. | Точное извлечение; без эвристического поиска. |

**Глоссарий**

- **Бутстрэп-устойчивость (π_ij)**: Доля графов из 500 повторных выборок, в которых присутствует конкретное ребро доказательства. Хранится как точное рациональное число (счётчик ÷ 500).
- **Детерминированная целочисленная арифметика**: Математические операции, выполняемые с целыми числами или рационалами фиксированного масштаба.
- **Шкала ENFSI**: Стандартизированная вербальная шкала, используемая европейскими криминалистическими институтами.
- **Внешняя аттестация**: Криптографическое запечатывание пакета, выполняемое независимым модулем. Предотвращает самосертификацию искажённых данных.
- **Разрыв графа**: Распад графа доказательств на изолированные компоненты. Штрафует глобальную устойчивость.
- **I4 (отсутствие неявных эффектов)**: Принцип проектирования, требующий явной декларации всех последствий.
- **Слой 0**: Неизменяемый фундамент архитектуры. Содержит только контракты данных.
- **Отношение правдоподобия (LR)**: Детерминистическое сравнение двух конкурирующих гипотез.
- **Решение с ограничением риска**: Выбор, вычисленный на основе явных числовых порогов. Система может вернуть ABSTAIN.

**Научное примечание**

【Научное примечание】Пирс, Эко и Грайс — не мистицизм; это датчики

Некоторые термины, унаследованные от семиотики и философии языка, — абдукция (Пирс), ограничения интерпретации (Эко) и кооперативные максимы (Грайс) — встречаются в документации судебных следов. Это не мистические или литературные украшения.

Воспринимайте их как **датчики логической структуры**. Термопара обнаруживает температуру, не «понимая» тепло; масс-спектрометр обнаруживает отношение массы к заряду, не «веря» в химию. Точно так же:
- **Абдукция** — это датчик генерации гипотез. Он обнаруживает наиболее экономичный объяснительный паттерн среди конкурирующих следов.
- **Ограничения Эко** действуют как датчик фильтрации шума. Они ограничивают допустимые интерпретации на основе конечного набора доказательств.
- **Грайсовская кооперация** функционирует как датчик синхронизации протокола. Он обнаруживает, разделяют ли два взаимодействующих подсистемы одни и те же фоновые предпосылки.

Эти конструкты обнаруживают **семио-логическую когерентность**, а не привидения в машине. Рассмотрение их как формальных инструментов распознавания паттернов сохраняет архитектуру строгой и поддающейся аудиту.

---

## 中文

**本模块是什么？**

本文档描述 **证据包规范 v1.0（EBS v1）**——数字取证架构的最底层。它是一个纯粹的数据模式：一组形式化规则，用于规定调查工具在尚未进行任何解释、叙事生成或密码学封装之前，如何记录其发现。

请将其视为**标本瓶上的标准化标签**。标签本身并不分析标本、不讲述关于标本的故事，也不给冰箱上锁。它只是确保每台实验室仪器使用相同的字段、单位和关系来描述标本。在此架构中，密码学封装和语言叙事由独立的外部模块处理，确保被攻陷的工具无法为自身的虚假输出背书。

**关键概念**

| 概念 | 在模式中的角色 | 确定性属性 |
|---|---|---|
| **ForensicBundle** | 主容器。聚合所有仪器输出、图、决策和策略规则的不可变信封。 | 从不自我哈希。完整性由外部构建器后续添加。 |
| **SignalOutput** | 来自单个取证工具的单一规范读数。 | z_score 以精确有理差值计算：基于整数的与基线均值之差除以整数中位绝对偏差（MAD）。无浮点近似。 |
| **EvidenceEdge** | 两个信号之间的有向依赖关系。 | 稳定性 π_ij 记录为在 500 次引导重采样中出现的精确计数（整数计数 / 500）。 |
| **EvidenceGraph** | 信号相互依赖关系的完整图谱。 | 由外部稳定性引擎生成。其标识符（graph_hash）由外部分配；图本身不含自我引用验证逻辑。 |
| **DecisionTrace** | 风险约束评估的数学结果。 | 100% 数值字段。当不确定性超过策略阈值时，包含明确的 ABSTAIN 退出状态。不引用 AI 模型或自然语言推断。 |
| **PolicyRule / PolicySpec** | 定义可接受风险边界的声明性约束。 | 纯逻辑结构。 |
| **ActionRecord** | 已执行干预的日志。 | 按照 **I4** 原则设计：零隐式效应。每个后果必须在记录中明确声明。 |

**支持函数**

| 函数 | 用途 | 确定性保证 |
|---|---|---|
| **make_default_policy()** | 生成基线策略模板。 | 相同输入始终产生相同规则结构。 |
| **enfsi_label()** | 将似然比转换为口头类别。 | 将精确比率区间映射到固定的 ENFSI 量表标签。无概率舍入。 |
| **to_dict()** | 将包内容序列化为标准化字典。 | 排除完整性字段；这些字段仅由外部 BundleBuilder 追加。 |
| **is_forensically_stable()** | 检查组件是否满足最低引导稳定性。 | 基于整数阈值比较的布尔裁决。 |
| **global_stability()** | 计算整体系统稳定性。 | 因**逻辑断裂**（不连通组件）受到惩罚。使用整数加权评分。 |
| **connected_components()** | 识别证据图中的孤立子图。 | 确定性图遍历；输出仅取决于边的存在，而非随机采样。 |
| **get_rule()** | 按标识符检索特定策略约束。 | 精确查找；无启发式搜索。 |

**术语表**

- **引导稳定性（π_ij）**：在 500 次重采样图中特定证据边出现的比例。存储为精确有理数（计数 ÷ 500）。
- **确定性整数运算**：使用整数或固定比例有理数执行的数学运算，确保相同输入始终产生完全相同的输出，无舍入误差。
- **ENFSI 量表**：欧洲取证科学研究所用于表达证据权重的标准化口头量表。
- **外部认证**：由独立模块（bundle_builder）而非数据生产者执行的密码学封装。防止损坏数据的自我认证。
- **逻辑断裂**：证据图分裂为孤立组件的状态。从逻辑上惩罚全局稳定性，因为断裂的图代表推理链条中断。
- **I4（无隐式效应）**：要求每条行动记录明确声明其所有后果的设计公理；禁止隐藏副作用。
- **第 0 层**：架构的不可变基础。仅包含数据契约，不含业务逻辑、哈希或叙事处理。
- **似然比（LR）**：两种竞争假设的确定性比较，以整数或有理数表示。
- **风险约束决策**：从明确数值阈值计算的选择。当没有选项满足安全边界时，系统可返回 ABSTAIN。

**科学说明**

【科学说明】皮尔斯、艾柯与格赖斯并非神秘主义，而是传感器

某些从符号学和语言哲学继承的术语——溯因（皮尔斯）、解释性约束（艾柯）和合作准则（格赖斯）——出现在取证痕迹文档中。它们**并非**神秘主义或文学修辞。

请将它们视为**逻辑结构传感器**。热电偶在不"理解"热量的情况下检测温度；质谱仪在不"相信"化学的情况下检测质荷比。同样地：
- **溯因**是假设生成传感器。它在竞争性痕迹中检测最经济的解释模式。
- **艾柯的约束**充当噪声过滤传感器。它们在有限证据集下划定哪些解释是可接受的。
- **格赖斯合作**充当协议同步传感器。它检测两个通信子系统是否共享相同的背景假设。

这些构造检测**符号逻辑连贯性**，而非机器中的幽灵。将它们视为形式模式识别工具，使架构保持严谨且可审计。

---

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
