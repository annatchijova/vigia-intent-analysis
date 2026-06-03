<!--
VIGIA Academic Documentation
Module: bb8bfa2d
Batch ID: vigia-doc-0048-bb8bfa2d
Generated: 2026-05-20T14:56:47.854843+00:00
-->

ENGLISH:
- Title: Evidence Bundle Specification v1.0 (EBS v1) — Core Data Schema
- What Is This Module?: A formal data contract that defines what forensic information looks like before any analysis, narrative, or cryptographic sealing is applied. Think of it as the "common language" that different instruments use to record their readings in a single, tamper-evident container. It is Layer 0: raw, immutable facts.
- Key Concepts tables:
  - Table 1: Core Data Containers
    - ForensicBundle: The master envelope. Holds all records but does not stamp or validate itself. External builder seals it.
    - SignalOutput: One instrument reading. Contains deterministic deviation score (integer-based rational calculation).
    - EvidenceGraph: Map of how signals relate. External engine assigns stability.
    - DecisionTrace: Mathematical risk evaluation. No AI interpretation.
    - ActionRecord: Log of what was done, with no hidden side effects.
  - Table 2: Mathematical & Policy Primitives
    - z_score: Deterministic standardized deviation using median absolute deviation (MAD) via integer-safe rational arithmetic.
    - pi_ij: Bootstrap frequency of an edge over 500 resamples, expressed as exact rational count/500.
    - ENFSI label: Verbal translation of a likelihood ratio using fixed categorical scale.
    - ABSTAIN: Formal exit state when uncertainty exceeds risk bounds.
  - Table 3: Integrity & Externalization Rules
    - No self-hashing: Bundle never seals itself.
    - No LLM references: No model names, no prompt fragments.
    - No business logic: Pure structure.
    - External attestation: bundle_builder.py handles graph_hash and integrity.
- Glossary:
  - Evidence Bundle Specification (EBS): The protocol for packaging forensic data.
  - Layer 0: The immutable basement of the architecture; data only.
  - Deterministic integer arithmetic: Calculations performed with exact integer or fixed-point operations, avoiding floating-point rounding errors.
  - Bootstrap stability (π_ij): The proportion of resampled graphs in which a specific dependency edge appears.
  - Graph fracture: Disconnection of the evidence graph, penalizing overall stability.
  - Risk-bounded decision: A mathematical choice made under explicit uncertainty thresholds.
  - I4 (No implicit effects): Principle that every action record must describe its consequences explicitly.
  - External attestation: Cryptographic sealing performed by an independent module, not the data producer.
- Scientific Note: Use sensor analogy. Peirce's abduction, Eco's semiotic limits, Grice's maxims — these are not mysticism. They are formal patterns. Just as a spectrometer detects wavelengths without "believing" in light, these models detect logical coherence without "understanding" narrative. Abduction is hypothesis generation; Eco's constraints are noise filters; Gricean cooperation is protocol synchronization. They are sensors for semio-logical structure.
- License.

ESPAÑOL:
- Similar structure.
- Terminology: Especificación de Paquete de Evidencia. Capa 0. Aritmética entera determinista. Atribución externa.
- Scientific Note: Peirce, Eco, Grice no son misticismo. Analogía del sensor.
- License.

РУССКИЙ:
- Title: Спецификация пакета доказательств v1.0
- Terms: Детерминированная целочисленная арифметика. Свидетельство внешнего модуля (аттестация). Разрыв графа (логический разрыв? but user says for Chinese "逻辑断裂", Russian can be "логический разрыв" or "фрагментация графа"). Устойчивость бутстрэп.
- Scientific Note: Пирс, Эко, Грайс — не мистицизм. Аналогия с датчиком.

中文:
- Must use: 艾柯 (Eco), 格赖斯 (Grice), 取证工件 (artifact), 逻辑断裂 (fracture).
- Title: 证据包规范 v1.0（EBS v1）核心数据模型
- What Is This Module? -> 本模块是什么？
- Key concepts tables.
- Glossary: 取证工件, 确定性整数运算, 引导重采样稳定性 (bootstrap), 逻辑断裂, 风险约束决策, 外部认证.
- Scientific Note: 【科学说明】解释皮尔士、艾柯、格赖斯的术语并非神秘主义。使用传感器类比。
-  (Keep as is or translate? User says include line. Usually keep English but can add translation. I'll keep the line exactly as requested.)

Important: The user says "You NEVER use floating-point math explanations for deterministic systems." So when describing z_score, say it's computed via deterministic integer arithmetic (e.g., using scaled integer MAD) or rational representation, never "float". And pi_ij = count/500 as exact rational.

Also, the user wants documentation for scientists who do not know Python. So avoid Python syntax, no "class", "def", etc. Use terms like "data container", "record type", "schema".

The module path is vigia/core/ebs_v1.py but docstring says vigia/models/ebs_v1.py. I should mention EBS v1 module.

Need to include all classes/functions mentioned in a cohesive way, but as concepts, not code.

# Evidence Bundle Specification v1.0 — Data Schema Documentation
`vigia/core/ebs_v1.py` | `vigia/models/ebs_v1.py`

Then sections for each language.

Let's draft the content fully.

ENGLISH draft:

---

## ENGLISH

### What Is This Module?
This document describes the **Evidence Bundle Specification v1.0 (EBS v1)**—the lowest layer of a digital-forensics architecture. It is a pure data schema: a set of formal rules that define how an investigative instrument records its findings before any interpretation, narrative generation, or cryptographic sealing occurs.

Think of it as the **standardized label on a specimen vial**. The label does not analyze the specimen, tell a story about it, or lock the freezer. It simply guarantees that every laboratory instrument describes the specimen using the same fields, units, and relationships. In this architecture, cryptographic sealing and linguistic narrative are handled by separate, external modules, ensuring that a compromised tool cannot legitimize its own false output.

### Key Concepts

| Concept | Role in the Schema | Deterministic Properties |
|---|---|---|
| **ForensicBundle** | The master container. An immutable envelope that aggregates all instrument outputs, graphs, decisions, and policy rules. | Never self-hashes. Integrity is added later by an external builder. |
| **SignalOutput** | A single, canonical reading from one forensic tool. | `z_score` computed as an exact rational deviation: integer-scaled difference from baseline mean divided by integer Median Absolute Deviation (MAD). No floating-point approximation. |
| **EvidenceEdge** | A directed dependency between two signals. | Stability `π_ij` is recorded as an exact count of appearances across 500 bootstrap resamples (integer count / 500). |
| **EvidenceGraph** | The full map of how signals depend on one another. | Produced by an external stability engine. Its identifier (`graph_hash`) is assigned externally; the graph itself contains no self-referential validation logic. |
| **DecisionTrace** | The mathematical result of a risk-bounded evaluation. | 100 % numeric fields. Contains an explicit `ABSTAIN` exit state when uncertainty exceeds policy thresholds. No references to AI models or natural-language inference. |
| **PolicyRule / PolicySpec** | Declarative constraints that define acceptable risk boundaries. | Pure logical structure. Used by the decision layer to compute deterministic thresholds. |
| **ActionRecord** | A log of an executed intervention. | Designed under the **I4** principle: zero implicit effects. Every consequence must be explicitly declared in the record. |

| Supporting Function | Purpose | Deterministic Guarantee |
|---|---|---|
| **make_default_policy()** | Generates a baseline policy template. | Identical input always yields identical rule structure. |
| **enfsi_label()** | Translates a Likelihood Ratio into a verbal category. | Maps exact ratio intervals to fixed ENFSI (European Network of Forensic Science Institutes) labels. No probabilistic rounding. |
| **to_dict()** | Serializes the bundle contents into a standardized dictionary. | Excludes integrity fields; those are appended only by the external `BundleBuilder`. |
| **is_forensically_stable()** | Checks whether a component meets minimum bootstrap stability. | Boolean verdict based on integer threshold comparison. |
| **global_stability()** | Computes overall system stability. | Penalized by **graph fracture** (disconnected components). Uses integer-weighted scoring. |
| **connected_components()** | Identifies isolated subgraphs within the evidence map. | Deterministic graph traversal; output depends solely on edge presence, not on stochastic sampling. |
| **get_rule()** | Retrieves a specific policy constraint by identifier. | Exact lookup; no heuristic search. |

### Glossary

- **Bootstrap Stability (`π_ij`)**: The proportion of 500 resampled graphs in which a specific evidence edge appears. Stored as an exact rational number (count ÷ 500).
- **Deterministic Integer Arithmetic**: Mathematical operations performed with integers or fixed-scale rationals, ensuring that the same input always produces the exact same output without rounding errors.
- **ENFSI Scale**: A standardized verbal scale used by European forensic institutes to express the weight of evidence. This module maps exact likelihood-ratio intervals to scale categories.
- **External Attestation**: The cryptographic sealing of a bundle performed by an independent module (`bundle_builder`), rather than by the data producer. Prevents self-certification of corrupted data.
- **Graph Fracture**: The disconnection of an evidence graph into isolated components. Logically penalizes global stability because fractured graphs represent broken chains of inference.
- **I4 (No Implicit Effects)**: A design axiom requiring that every action record explicitly declare all its consequences; hidden side-effects are forbidden.
- **Layer 0**: The immutable foundation of the architecture. Contains only data contracts and no business logic, hashing, or narrative processing.
- **Likelihood Ratio (LR)**: A deterministic comparison of two competing hypotheses, expressed as an integer or rational value.
- **Risk-Bounded Decision**: A choice computed from explicit numerical thresholds. The system may return `ABSTAIN` when no option satisfies the safety bounds.

### 【Scientific Note】Peirce, Eco, and Grice Are Not Mysticism; They Are Sensors
Certain terms inherited from semiotics and philosophy of language—abduction (Peirce), interpretive constraints (Eco), and cooperative maxims (Grice)—appear in forensic-trace documentation. They are **not** mystical or literary flourishes.

Think of them as **sensors for logical structure**. A thermocouple detects temperature without “understanding” heat; a mass spectrometer detects mass-to-charge ratio without “believing” in chemistry. Likewise:
- **Abduction** is a hypothesis-generation sensor. It detects the most economical explanatory pattern among competing traces.
- **Eco’s constraints** act as a noise-filter sensor. They delimit which interpretations are admissible given the finite evidence set.
- **Gricean cooperation** functions as a protocol-synchronization sensor. It detects whether two communicating subsystems share the same background assumptions.

These constructs detect **semio-logical coherence**, not ghosts in the machine. Treating them as formal pattern-recognition instruments keeps the architecture rigorous and auditable.

---

ESPAÑOL draft:

## ESPAÑOL

### ¿Qué es este módulo?
Este documento describe la **Especificación de Paquete de Evidencia v1.0 (EBS v1)**—la capa más baja de una arquitectura de informática forense. Es un esquema de datos puros: un conjunto de reglas formales que definen cómo un instrumento de investigación registra sus hallazgos antes de cualquier interpretación, generación de narrativas o sellado criptográfico.

Piénsese en él como la **etiqueta estandarizada de un vial de muestra**. La etiqueta no analiza la muestra, no cuenta una historia sobre ella ni cierra la cerradura del congelador. Simplemente garantiza que todo instrumento de laboratorio describa la muestra usando los mismos campos, unidades y relaciones. En esta arquitectura, el sellado criptográfico y la narrativa lingüística son gestionados por módulos externos e independientes, asegurando que una herramienta comprometida no pueda legitimar su propia salida falsa.

### Conceptos Clave

| Concepto | Rol en el esquema | Propiedades deterministas |
|---|---|---|
| **ForensicBundle** | Contenedor maestro. Sobre inmutable que agrega todas las salidas de instrumentos, grafos, decisiones y reglas de política. | Nunca se autohashea. La integridad se añade posteriormente por un constructor externo. |
| **SignalOutput** | Lectura canónica única de una herramienta forense. | `z_score` calculado como desviación racional exacta: diferencia escalada en enteros respecto a la media basal dividida por la Desviación Absoluta Mediana (MAD) entera. Sin aproximaciones de punto flotante. |
| **EvidenceEdge** | Dependencia dirigida entre dos señales. | La estabilidad `π_ij` se registra como un conteo exacto de apariciones en 500 remuestreos bootstrap (conteo entero / 500). |
| **EvidenceGraph** | Mapa completo de cómo las señales dependen unas de otras. | Producido por un motor de estabilidad externo. Su identificador (`graph_hash`) se asigna externamente; el grafo mismo no contiene lógica de autovalidación. |
| **DecisionTrace** | Resultado matemático de una evaluación de riesgo acotado. | Campos 100 % numéricos. Contiene un estado de salida explícito `ABSTAIN` cuando la incertidumbre excede los umbrales de política. Sin referencias a modelos de IA ni inferencia en lenguaje natural. |
| **PolicyRule / PolicySpec** | Restricciones declarativas que definen límites aceptables de riesgo. | Estructura lógica pura. Utilizada por la capa de decisión para calcular umbrales deterministas. |
| **ActionRecord** | Registro de una intervención ejecutada. | Diseñado bajo el principio **I4**: cero efectos implícitos. Cada consecuencia debe declararse explícitamente en el registro. |

| Función de soporte | Propósito | Garantía determinista |
|---|---|---|
| **make_default_policy()** | Genera una plantilla de política basal. | La misma entrada siempre produce la misma estructura de reglas. |
| **enfsi_label()** | Traduce una Razón de Verosimilitud a una categoría verbal. | Mapea intervalos exactos de razón a etiquetas fijas de la escala ENFSI. Sin redondeo probabilístico. |
| **to_dict()** | Serializa el contenido del paquete en un diccionario estandarizado. | Excluye campos de integridad; estos se agregan únicamente por el `BundleBuilder` externo. |
| **is_forensically_stable()** | Verifica si un componente cumple la estabilidad bootstrap mínima. | Veredicto booleano basado en comparación de umbrales enteros. |
| **global_stability()** | Calcula la estabilidad global del sistema. | Penalizada por **fractura del grafo** (componentes desconectadas). Utiliza puntuación con pesos enteros. |
| **connected_components()** | Identifica subgrafos aislados dentro del mapa de evidencia. | Recorrido determinista del grafo; la salida depende únicamente de la presencia de aristas, no del muestreo estocástico. |
| **get_rule()** | Recupera una restricción de política específica por identificador. | Búsqueda exacta; sin heurística. |

### Glosario

- **Estabilidad Bootstrap (`π_ij`)**: La proporción de grafos remuestreados (de 500) en la que aparece una arista de evidencia específica. Almacenada como número racional exacto (conteo ÷ 500).
- **Aritmética Entera Determinista**: Operaciones matemáticas realizadas con enteros o racionales de escala fija, garantizando que la misma entrada siempre produzca exactamente la misma salida sin errores de redondeo.
- **Escala ENFSI**: Escala verbal estandarizada utilizada por institutos forenses europeos para expresar el peso de la evidencia. Este módulo asigna categorías a intervalos exactos de razón de verosimilitud.
- **Atestación Externa**: El sellado criptográfico de un paquete realizado por un módulo independiente (`bundle_builder`), en lugar del productor de datos. Previene la autoverificación de datos corruptos.
- **Fractura del Grafo**: La desconexión de un grafo de evidencia en componentes aisladas. Penaliza lógicamente la estabilidad global porque los grafos fracturados representan cadenas de inferencia rotas.
- **I4 (Sin Efectos Implícitos)**: Axioma de diseño que exige que todo registro de acción declare explícitamente todas sus consecuencias; los efectos secundarios ocultos están prohibidos.
- **Capa 0**: La fundación inmutable de la arquitectura. Contiene únicamente contratos de datos y ninguna lógica de negocio, función hash ni procesamiento de narrativas.
- **Razón de Verosimilitud (LR)**: Comparación determinista entre dos hipótesis competidoras, expresada como valor entero o racional.
- **Decisión de Riesgo Acotado**: Elección calculada a partir de umbrales numéricos explícitos. El sistema puede devolver `ABSTAIN` cuando ninguna opción satisface los límites de seguridad.

### 【Nota Científica】Peirce, Eco y Grice no son misticismo; son sensores
Algunos términos heredados de la semiótica y la filosofía del lenguaje—abducción (Peirce), restricciones interpretativas (Eco) y máximas cooperativas (Grice)—aparecen en la documentación de rastros forenses. No son adornos místicos ni literarios.

Piénsese en ellos como **sensores de estructura lógica**. Un termopar detecta temperatura sin “entender” el calor; un espectrómetro de masas detecta la relación masa/carga sin “creer” en la química. Del mismo modo:
- La **abducción** es un sensor de generación de hipótesis. Detecta el patrón explicativo más económico entre rastros competidores.
- Las **restricciones de Eco** actúan como un sensor de filtrado de ruido. Delimitan qué interpretaciones son admisibles dado el conjunto finito de evidencia.
- La **cooperación griceana** funciona como un sensor de sincronización de protocolo. Detecta si dos subsistemas comunicantes comparten los mismos supuestos de fondo.

Estos constructos detectan **coherencia semio-lógica**, no fantasmas en la máquina. Tratarlos como instrumentos formales de reconocimiento de patrones mantiene la arquitectura rigurosa y auditable.

---

РУССКИЙ draft:

## РУССКИЙ

### Что представляет собой этот модуль?
Настоящий документ описывает **Спецификацию пакета доказательств v1.0 (EBS v1)** — низший слой архитектуры цифровой криминалистики. Это чистая схема данных: формальный набор правил, определяющих, как следственный инструмент фиксирует свои находки до любой интерпретации, генерации повествования или криптографического запечатывания.

Воспринимайте её как **стандартизированную этикетку на пробирке с образцом**. Этикетка не анализирует образец, не рассказывает о нём историю и не запирает морозильную камеру. Она лишь гарантирует, что каждый лабораторный прибор описывает образец с использованием одних и тех же полей, единиц измерения и связей. В данной архитектуре криптографическое запечатывание и языковое повествование выполняются отдельными внешними модулями, что гарантирует невозможность для скомпрометированного инструмента легитимизировать собственный ложный результат.

### Ключевые концепции

| Концепция | Роль в схеме | Детерминированные свойства |
|---|---|---|
| **ForensicBundle** | Главный контейнер. Неизменяемый конверт, агрегирующий все выходные данные приборов, графы, решения и правила политик. | Никогда не хеширует себя сам. Целостность добавляется позже внешним сборщиком. |
| **SignalOutput** | Одна каноническая запись от одного криминалистического инструмента. | `z_score` вычисляется как точное рациональное отклонение: масштабированная целочисленная разность от базового среднего, делённая на целочисленное медианное абсолютное отклонение (MAD). Без приближений с плавающей точкой. |
| **EvidenceEdge** | Направленная зависимость между двумя сигналами. | Стабильность `π_ij` фиксируется как точное число появлений в 500 бутстрэп-выборках (целое счётное / 500). |
| **EvidenceGraph** | Полная карта зависимостей между сигналами. | Производится внешним движком стабильности. Его идентификатор (`graph_hash`) назначается извне; сам граф не содержит логики самопроверки. |
| **DecisionTrace** | Математический результат оценки с ограничением риска. | Поля на 100 % числовые. Содержит явное состояние выхода `ABSTAIN`, когда неопределённость превышает пороги политики. Без ссылок на ИИ-модели или естественно-языковые выводы. |
| **PolicyRule / PolicySpec** | Декларативные ограничения, задающие допустимые границы риска. | Чистая логическая структура. Используется вычислительным слоем для расчёта детерминированных порогов. |
| **ActionRecord** | Журнал выполненного вмешательства. | Спроектирован по принципу **I4**: нулевые неявные эффекты. Каждое следствие должно быть явно задекларировано в записи. |

| Вспомогательная функция | Назначение | Детерминированная гарантия |
|---|---|---|
| **make_default_policy()** | Генерирует базовый шаблон политики. | При идентичном входе всегда выдаёт идентичную структуру правил. |
| **enfsi_label()** | Преобразует отношение правдоподобия в вербальную категорию. | Отображает точные интервалы отношений на фиксированные категории шкалы ENFSI. Без вероятностного округления. |
| **to_dict()** | Сериализует содержимое пакета в стандартизированный словарь. | Исключает поля целостности; они добавляются только внешним `BundleBuilder`. |
| **is_forensically_stable()** | Проверяет, соответствует ли компонент минимальной бутстрэп-устойчивости. | Булев вердикт на основе сравнения целочисленных порогов. |
| **global_stability()** | Вычисляет глобальную устойчивость системы. | Штрафуется за **разрыв графа** (несвязные компоненты). Использует целочисленное взвешенное скоринг. |
| **connected_components()** | Выявляет изолированные подграфы в карте доказательств. | Детерминированный обход графа; результат зависит только от наличия рёбер, а не от стохастической выборки. |
| **get_rule()** | Извлекает конкретное ограничение политики по идентификатору. | Точное извлечение; без эвристического поиска. |

### Глоссарий

- **Бутстрэп-устойчивость (`π_ij`)**: Доля графов из 500 повторных выборок, в которых присутствует конкретное ребро доказательства. Хранится как точное рациональное число (счётчик ÷ 500).
- **Детерминированная целочисленная арифметика**: Математические операции, выполняемые с целыми числами или рационалами фиксированного масштаба, гарантирующие, что одинаковый вход всегда даёт точно такой же выход без ошибок округления.
- **Шкала ENFSI**: Стандартизированная вербальная шкала, используемая европейскими криминалистическими институтами для выражения веса доказательства. Модуль отображает точные интервалы отношения правдоподобия на категории шкалы.
- **Внешняя аттестация**: Криптографическое запечатывание пакета, выполняемое независимым модулем (`bundle_builder`), а не производителем данных. Предотвращает самосертификацию искажённых данных.
- **Разрыв графа**: Распад графа доказательств на изолированные компоненты. Логически штрафует глобальную устойчивость, поскольку разорванные графы представляют собой разрушенные цепочки умозаключений.
- **I4 (отсутствие неявных эффектов)**: Принцип проектирования, требующий, чтобы каждая запись действия явно декларировала все свои последствия; скрытые побочные эффекты запрещены.
- **Слой 0**: Неизменяемый фундамент архитектуры. Содержит только контракты данных и не включает бизнес-логику, хеширование или обработку повествований.
- **Отношение правдоподобия (LR)**: Детерминистическое сравнение двух конкурирующих гипотез, выраженное целым числом или рационалом.
- **Решение с ограничением риска**: Выбор, вычисленный на основе явных числовых порогов. Система может вернуть `ABSTAIN`, когда ни один вариант не удовлетворяет допустимым границам безопасности.

### 【Научное примечание】Пирс, Эко и Грайс — не мистицизм; это датчики
Некоторые термины, унаследованные от семиотики и философии языка, — абдукция (Пирс), ограничения интерпретации (Эко) и кооперативные максимы (Грайс) — встречаются в документации судебных следов. Это не мистические или литературные украшения.

Воспринимайте их как **датчики логической структуры**. Термопара обнаруживает температуру, не «понимая» тепло; масс-спектрометр обнаруживает отношение массы к заряду, не «веря» в химию. Точно так же:
- **Абдукция** — это датчик генерации гипотез. Он обнаруживает наиболее экономичный объяснительный паттерн среди конкурирующих следов.
- **Ограничения Эко** действуют как датчик фильтрации шума. Они ограничивают допустимые интерпретации на основе конечного набора доказательств.
- **Грайсовская кооперация** функционирует как датчик синхронизации протокола. Он обнаруживает, разделяют ли два взаимодействующих подсистемы одни и те же фоновые предпосылки.

Эти конструкты обнаруживают **семио-логическую когерентность**, а не привидения в машине. Рассмотрение их как формальных инструментов распознавания паттернов сохраняет архитектуру строгой и поддающейся аудиту.

---

中文 draft:

## 中文

### 本模块是什么？
本文档描述 **证据包规范 v1.0（EBS v1）**——数字取证架构的最底层。它是一个纯粹的数据模式：一组形式化规则，用于规定调查工具在尚未进行任何解释、叙事生成或密码学封装之前，如何记录其发现。

请将其视为**标本瓶上的标准化标签**。标签本身并不分析标本、不讲述关于标本的故事，也不给冰箱上锁。它只是确保每台实验室仪器使用
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
