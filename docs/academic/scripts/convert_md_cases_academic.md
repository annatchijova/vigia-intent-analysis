<!--
VIGIA Academic Documentation
Module: a05271e7
Batch ID: vigia-doc-0011-a05271e7
Generated: 2026-05-20T14:56:47.847170+00:00
-->

---
doc_hash: a05271e7
module: scripts/convert_md_cases.py
languages: [EN, ES, RU, ZH]
generated_by: moonshot-kimi-k2.6-batch-api
license: Apache-2.0
---

ENGLISH:
- Title: Module Documentation: `scripts/convert_md_cases.py`
- What Is This Module?: A deterministic text-processing pipeline that transforms human-readable forensic case narratives (written in Markdown) into a structured, machine-readable JSON canon (the VIGÍA format). Think of it as a digital lathe that cuts unstructured evidence notes into standardized, countable, and indexable blocks—without using any probabilistic or floating-point operations. Every operation is exact integer-based string matching and deterministic record assembly.
- Key Concepts table: Maybe 2 tables? One for the pipeline stages, one for the semiotic layers?
  - Pipeline stages: Input (Markdown), Parsing (Regex patterns), Extraction (Fields), Transformation (Peirce/Eco/Grice layers), Output (JSON)
  - Regex constants explained as "deterministic finite automata patterns" - but audience doesn't know Python, so explain as "exact text boundary markers"
  - Functions as stages:
    - parse_md_file: ingestion
    - parse_case_body: dissection
    - signals_to_artifacts: evidence structuring
    - build_peirce: semiotic triad construction
    - infer_mitre: tactic mapping (deterministic lookup)
    - devil_advocate_template: null hypothesis generation
    - consolidate: aggregation
    - detect_type: classification
- Glossary: Canonical JSON, VIGÍA format, Regex (exact pattern matching), Peirce chain, MITRE ATT&CK, Devil's Advocate, Deterministic integer arithmetic, Artifact, Semiotic layer
- Scientific Note: Explain Peirce (sign-object-interpretant), Eco (codes/culture), Grice (maxims of communication) via sensor analogy. "These are not mystical concepts but formal semiotic sensors..."

ESPAÑOL:
- What: Same but in Spanish. "Torno digital", etc.
- Key concepts: Pipeline de conversión forense.
- Glossary: JSON canónico, Formato VIGÍA, Expresiones regulares (patrones exactos), Cadena Peirce, MITRE ATT&CK, Abogado del diablo, Aritmética determinista de enteros, Artefacto, Capa semiótica.
- Nota científica: same sensor analogy.

РУССКИЙ:
- What: Конвейер детерминированной обработки текста...
- Key concepts: Таблицы этапов.
- Glossary: Канонический JSON, Формат VIGÍA, Регулярные выражения (точное сопоставление), Цепочка Пирса, MITRE ATT&CK, Адвокат дьявола, Детерминированная целочисленная арифметика, Артефакт, Семиотический слой.
- Scientific Note: Пирс/Эко/Грайс через аналогию с датчиками.

中文:
- Must use: 艾柯 (Eco), 格赖斯 (Grice), 取证工件 (artifacts), 逻辑断裂 (logical fracture/gap)
- What: 确定性文本处理管道... 数字车床比喻.
- Key concepts: 输入、解析、提取、转换、输出.
- Glossary: 规范JSON, VIGÍA格式, 正则表达式（精确文本边界定位器）, 皮尔斯链条, MITRE ATT&CK, 魔鬼代言人, 确定性整数运算, 取证工件, 符号学层.
- Scientific Note: 【科学说明】 box. 传感器类比. 艾柯 and 格赖斯.

Need to ensure no floating-point math explanations. Emphasize deterministic integer arithmetic. The module uses regex and integer counters, so I can mention that string positions are tracked via integer indices and counts are exact integers.

Let me organize the output. I'll put all four languages in one markdown document, clearly separated.

Actually, looking at the prompt: "Format: Markdown with 4 language sections". So one document with four major sections.

Let me structure:

# Module Documentation: `scripts/convert_md_cases.py`

## ENGLISH

### What Is This Module?
...

### Key Concepts
Table 1: Pipeline Stages
| Stage | Function Equivalent | Scientific Description |
|---|---|---|
| Ingestion | `parse_md_file()` | Reads Markdown source and segments it into discrete case records using exact integer-position boundary detection. |
| ... | ... | ... |

Table 2: Semiotic & Logical Layers
| Layer | Constant/Function | Role |
|---|---|---|
| Peirce Chain | `build_peirce()` / `PEIRCE_RE` | Models the sign-object-interpretant triad as a deterministic inference chain. |
| Eco Codes | (implied in interpretation) | Cultural and contextual framing extracted via exact pattern matching. |
| Grice Maxims | `GRICE_RE` | Communicative expectation rules; detects logical fractures in testimony. |
| Signals | `SIGNALS_RE` / `signals_to_artifacts()` | Converts raw observational text into structured 取证工件 (forensic artifacts). |

Wait, in English I should probably not use the Chinese term 取证工件. Use "forensic artifacts".

Table 3: Deterministic Configuration Constants
| Constant | Purpose |
|---|---|
| `CASE_RE` | Exact regular-expression delimiter for case headers (`#### Caso NNN...`) |
| `VERDICT_RE` | Boundary marker for verdict sections |
| ... |

### Glossary
...

### 【Scientific Note】
Box explaining Peirce/Eco/Grice are formal semiotic instruments, like sensors.
- Peirce = triadic sensor (sign/representamen → object → interpretant)
- Eco = cultural filter sensor (codebook lookup)
- Grice = coherence sensor (checks for logical fractures / 逻辑断裂 in narrative consistency)
They are deterministic classifiers, not mysticism. They operate via exact integer matching, not probability.

### License


Then repeat structure for other languages.

Let me think about the Chinese section carefully:
- Peirce = 皮尔斯 (standard translation)
- Eco = 艾柯 (required)
- Grice = 格赖斯 (required)
- Artifacts = 取证工件 (required)
- Logical fractures = 逻辑断裂 (required)

Chinese scientific note:
【科学说明】
皮尔斯、艾柯与格赖斯的术语并非神秘主义，而是一组形式化符号学传感器。皮尔斯三元体如同一个三态探针：符号（representamen）→ 对象（object）→ 解释项（interpretant）。艾柯的文化编码层如同一个确定性的码本滤波器。格赖斯的合作原则则是一个一致性传感器，用于检测叙事中的逻辑断裂。所有这些操作均通过确定性整数运算完成——字符串位置由整数索引标记，匹配结果只有“命中/未命中”两种离散状态，不存在概率或浮点近似。

Now, about "detect_type()" and "consolidate()" - I need to infer what they do based on names, since no docstring details were given. The prompt says:
- consolidate(): (no description)
- detect_type(): (no description)

I should describe them generically based on their names in the context: consolidate() likely aggregates multiple parsed cases into the final index and canonical files. detect_type() likely classifies the case or signals into a taxonomy. I'll describe them cautiously without making up too much, but enough to be useful.

For the deterministic integer arithmetic emphasis: I should note that regex engines operate on discrete finite automata, string indices are integers, counts are integers, and JSON serialization preserves exact discrete structures. No floating-point measurements or probabilistic inference.

Let me draft the content carefully.

ENGLISH SECTION:

**What Is This Module?**
This module is a deterministic text-refinery. It converts unstructured forensic case narratives—written by analysts in Markdown—into the VIGÍA canonical JSON format. Imagine a digital lathe operating on exact integer coordinates: it reads the Markdown source, locates every case heading (`#### Caso NNN: "Name" – Subtitle`) using discrete integer-position markers, slices the text into records, extracts semantic fields, and assembles structured evidence files. No probabilistic guessing, no floating-point approximations. Every cut is exact; every count is an integer.

**Key Concepts**

Table 1: Pipeline Stages
| Stage | Equivalent Function | Scientific Description |
|---|---|---|
| Ingestion | `parse_md_file()` | Opens Markdown sources and splits the stream into raw case blocks using deterministic boundary detection. |
| Dissection | `parse_case_body()` | Extracts individual fields (title, verdict, interpretation) from a raw block via exact pattern matching. |
| Structuring | `signals_to_artifacts()` | Transforms free-text "signals" into discrete forensic artifacts with integer-indexed fields. |
| Semiotic Assembly | `build_peirce()` | Constructs the Peirce inference chain from extracted text segments. |
| TTP Mapping | `infer_mitre()` | Maps extracted content to MITRE ATT&CK tactics through deterministic lookup tables. |
| Null Hypothesis | `devil_advocate_template()` | Generates a benign alternative hypothesis to test against the primary interpretation. |
| Aggregation | `consolidate()` | Merges all processed cases into canonical output files and an index. |
| Classification | `detect_type()` | Assigns a deterministic typology label to the case or its components. |

Table 2: Semiotic Sensors & Pattern Anchors
| Symbolic Layer | Regex / Function | Scientific Role |
|---|---|---|
| Peirce Triad | `PEIRCE_RE` / `build_peirce()` | Triadic sensor: detects representamen → object → interpretant relationships. |
| Cultural Codes | (interpretation layer) | Eco-codebook filter: isolates context-dependent meaning frames. |
| Grice Maxims | `GRICE_RE` | Coherence sensor: flags violations of narrative consistency (logical fractures). |
| Carnegie Stages | `CARNEGIE_RE` | Evidence-maturity classifier (analogy to developmental stages). |
| Verdict Markers | `VERDICT_RE`, `VERDICT_IN_INTERP_RE` | Exact delimiters for conclusion sections. |
| Signal Boundaries | `SIGNALS_RE` | Delimiters that separate observational evidence from commentary. |

Table 3: Configuration & Integer-Arithmetic Guarantees
| Constant / Config | Purpose |
|---|---|
| `MD_SOURCES` | File-system path to input Markdown (discrete, countable set). |
| `OUTPUT_DIR` | Target directory for JSON artifacts (`data/cases/consolidated/`). |
| `CASE_RE` | Regular-expression finite automaton for header recognition; operates on integer state transitions. |
| `INTERPRETATION_RE` | Exact boundary marker for analyst interpretation sections. |

**Glossary**
- **Canonical JSON**: A standardized, deterministic text format for hierarchical data. Every field has an exact position and type.
- **VIGÍA Format**: The canonical forensic schema used by this project; enforces strict field naming and integer-indexed arrays.
- **Regular Expression (Regex)**: A deterministic finite-state machine that matches exact text patterns. Think of it as a stencil with integer-coordinate cut-outs.
- **Peirce Chain**: A formal semiotic inference structure (Sign → Object → Interpretant) used here as a deterministic logical sensor.
- **MITRE ATT&CK**: A globally recognized taxonomy of adversary tactics and techniques. Mapped via exact identifier lookup.
- **Devil's Advocate Template**: A structured null-hypothesis generator that proposes benign explanations to avoid confirmation bias.
- **Deterministic Integer Arithmetic**: All operations use whole-number counting, exact string indices, and discrete state logic. No floating-point noise is introduced.
- **Forensic Artifact**: A discrete, structured unit of evidence (from raw signal text).
- **Logical Fracture**: A break in narrative consistency detected by Gricean coherence rules.

**【Scientific Note】**
> The terminology of Peirce, Eco, and Grice is frequently mistaken for literary mysticism. In this module, these names denote formal semiotic **sensors**—deterministic instruments, not metaphysical entities.
>
> **Peirce** functions as a triadic sensor: it registers a *representamen* (the trace), an *object* (the real-world referent), and an *interpretant* (the analyst inference), producing an exact logical chain.
>
> **Eco** operates as a cultural codebook filter: it applies context-dependent classification rules via deterministic pattern matching, analogous to a calibrated spectrometer selecting specific wavelengths.
>
> **Grice** serves as a coherence sensor: it checks testimony against maxims of quantity, quality, relation, and manner, flagging **logical fractures** when a narrative violates communicative expectations.
>
> All three operate through exact integer matching and finite-state transitions. Their output is binary or categorical, never probabilistic.

**License**


---

ESPAÑOL SECTION:

**¿Qué es este módulo?**
Es una refinería de texto determinista. Convierte narrativas forenses escritas en Markdown al formato canónico JSON de VIGÍA. Imagínese un torno digital que opera con coordenadas enteras exactas: lee la fuente Markdown, localiza cada encabezado de caso (`#### Caso NNN: "Nombre" – Subtítulo`) mediante marcadores de posición de índices enteros, segmenta el texto en registros, extrae campos semánticos y ensambla archivos de evidencia estructurados. Sin conjeturas probabilísticas, sin aproximaciones en punto flotante. Corte exacto; conteo entero.

**Conceptos Clave**
Tables similar but translated.

| Etapa | Función Equivalente | Descripción Científica |
|---|---|---|
| Ingesta | `parse_md_file()` | Abre fuentes Markdown y divide la corriente en bloques de caso usando detección determinista de límites. |
| Disección | `parse_case_body()` | Extrae campos individuales (título, veredicto, interpretación) mediante coincidencia exacta de patrones. |
| Estructuración | `signals_to_artifacts()` | Transforma señales de texto libre en artefactos forenses discretos con campos indexados por enteros. |
| Ensamblaje Semiótico | `build_peirce()` | Construye la cadena de inferencia Peirce desde segmentos de texto extraídos. |
| Mapeo TTP | `infer_mitre()` | Mapea contenido extraído a tácticas MITRE ATT&CK mediante tablas de búsqueda deterministas. |
| Hipótesis Nula | `devil_advocate_template()` | Genera una hipótesis alternativa benigna para contraste. |
| Agregación | `consolidate()` | Fusiona todos los casos procesados en archivos canónicos y un índice maestro. |
| Clasificación | `detect_type()` | Asigna una etiqueta tipológica determinista al caso o sus componentes. |

Table: Sensores Semióticos
| Capa Simbólica | Regex / Función | Rol Científico |
|---|---|---|
| Triada Peirce | `PEIRCE_RE` / `build_peirce()` | Sensor triádico: detecta relaciones representamen → objeto → interpretante. |
| Códigos Culturales | (capa de interpretación) | Filtro tipo codebook de Eco: aísla marcos de significado contextuales. |
| Máximas Grice | `GRICE_RE` | Sensor de coherencia: señala violaciones de consistencia narrativa (fracturas lógicas). |
| Etapas Carnegie | `CARNEGIE_RE` | Clasificador de madurez de evidencia. |
| Marcadores de Veredicto | `VERDICT_RE`, `VERDICT_IN_INTERP_RE` | Delimitadores exactos de secciones de conclusión. |
| Fronteras de Señales | `SIGNALS_RE` | Delimitadores que separan evidencia observacional del comentario analítico. |

**Glosario**
- **JSON canónico**: Formato de texto determinista y estandarizado para datos jerárquicos.
- **Formato VIGÍA**: Esquema forense canónico del proyecto; exige nombres de campo estrictos y arreglos indexados por enteros.
- **Expresión regular (Regex)**: Máquina de estados finita determinista que reconoce patrones de texto exactos.
- **Cadena Peirce**: Estructura de inferencia semiótica formal (Signo → Objeto → Interpretante) usada aquí como sensor lógico determinista.
- **MITRE ATT&CK**: Taxonomía global de tácticas y técnicas adversarias.
- **Plantilla Abogado del Diablo**: Generador estructurado de hipótesis nulas benignas.
- **Aritmética determinista de enteros**: Todas las operaciones usan conteo de números enteros, índices exactos de cadenas y lógica de estados discretos.
- **Artefacto forense**: Unidad discreta y estructurada de evidencia.
- **Fractura lógica**: Ruptura en la consistencia narrativa detectada por reglas griceanas de coherencia.

**【Nota Científica】**
> La terminología de Peirce, Eco y Grice se confunde frecuentemente con misticismo literario. En este módulo, estos nombres designan **sensores** semióticos formales: instrumentos deterministas, no entidades metafísicas.
>
> **Peirce** funciona como un sensor triádico: registra un *representamen* (la traza), un *objeto* (el referente real) y un *interpretante* (la inferencia del analista), produciendo una cadena lógica exacta.
>
> **Eco** opera como un filtro de codebook cultural: aplica reglas de clasificación dependientes del contexto mediante coincidencia exacta de patrones, análogo a un espectrómetro calibrado que selecciona longitudes de onda específicas.
>
> **Grice** actúa como sensor de coherencia: verifica el testimonio contra máximas de cantidad, calidad, relación y modo, marcando **fracturas lógicas** cuando una narrativa viola expectativas comunicativas.
>
> Los tres operan mediante transiciones de estados finitos y coincidencia exacta de enteros. Su salida es binaria o categórica, nunca probabilística.

**Licencia**


---

РУССКИЙ SECTION:

**Что представляет собой этот модуль?**
Это детерминированный текстовый рефайнери. Он преобразует неструктурированные судебно-экспертные описания дел, написанные в Markdown, в канонический формат JSON системы VIGÍA. Представьте цифровой токарный станок, работающий по точным целочисленным координатам: он читает исходный Markdown, находит каждый заголовок дела (`#### Caso NNN: "Nombre" – Subtítulo`) с помощью дискретных маркеров позиций индексов, разрезает текст на записи, извлекает семантические поля и собирает структурированные файлы доказательств. Никаких вероятностных догадок, никаких приближений с плавающей точкой. Каждый разрез точен; каждый счёт целочисленнен.

Wait, I need to make sure I don't use floating-point explanations. I should say "нет никакой арифметики с плавающей точкой" or just avoid mentioning it positively. The requirement is "do NOT use floating-point math explanations". So I can mention that we avoid it.

**Ключевые концепции**
Table 1:
| Этап | Эквивалентная функция | Научное описание |
|---|---|---|
| Загрузка | `parse_md_file()` | Открывает источники Markdown и разбивает поток на сырые блоки дел с помощью детерминированного обнаружения границ. |
| Диссекция | `parse_case_body()` | Извлекает отдельные поля (заголовок, вердикт, интерпретация) через точное сопоставление шаблонов. |
| Структурирование | `signals_to_artifacts()` | Преобразует свободные текстовые «сигналы» в дискретные артефакты цифровой криминалистики с целочисленной индексацией полей. |
| Семиотическая сборка | `build_peirce()` | Строит цепочку логических выводов Пирса из извлечённых текстовых сегментов. |
| Сопоставление TTP | `infer_mitre()` | Сопоставляет извлечённое содержимое с тактиками MITRE ATT&CK через детерминированные таблицы поиска. |
| Нулевая гипотеза | `devil_advocate_template()` | Генерирует структурированную доброкачественную альтернативную гипотезу. |
| Агрегация | `consolidate()` | Объединяет все обработанные дела в канонические выходные файлы и индекс. |
| Классификация | `detect_type()` | Назначает детерминированную типологическую метку делу или его компонентам. |

Table 2:
| Символический слой | Регулярное выражение / Функция | Научная роль |
|---|---|---|
| Триада Пирса | `PEIRCE_RE` / `build_peirce()` | Триадический датчик: обнаруживает отношения репрезентамен → объект → интерпретант. |
| Культурные коды | (слой интерпретации) | Культурный фильтр-кодебук Эко: выделяет контекстно-зависимые рамки значения. |
| Максимы Грайса | `GRICE_RE` | Датчик когерентности: отмечает нарушения повествовательной согласованности (логические разрывы). |
| Стадии Карнеги | `CARNEGIE_RE` | Классификатор зрелости доказательств. |
| Маркеры вердикта | `VERDICT_RE`, `VERDICT_IN_INTERP_RE` | Точные разделители разделов заключений. |
| Границы сигналов | `SIGNALS_RE` | Разделители, отделяющие наблюдательные доказательства от аналитического комментария. |

**Глоссарий**
- **Канонический JSON**: Стандартизированный детерминированный текстовый формат для иерархических данных.
- **Формат VIGÍA**: Каноническая судебно-экспертная схема проекта; требует строгих имён полей и массивов с целочисленной индексацией.
- **Регулярное выражение (Regex)**: Детерминированная машина конечных состояний, распознающая точные текстовые шаблоны.
- **Цепочка Пирса**: Формальная семиотическая структура логического вывода (Знак → Объект → Интерпретант), используемая здесь как детерминированный логический датчик.
- **MITRE ATT&CK**: Глобально признанная таксономия тактик и техник противника.
- **Шаблон «Адвокат дьявола»**: Структурированный генератор нулевых гипотез, предлагающий доброкачественные объяснения.
- **Детерминированная целочисленная арифметика**: Все операции используют счёт целыми числами, точные индексы строк и дискретную логику состояний. Никакого шума с плавающей точкой не вводится.
- **Артефакт цифровой криминалистики**: Дискретная структурированная единица доказательства.
- **Логический разрыв**: Нарушение повествовательной согласованности, обнаруживаемое правилами грайсовской когерентности.

**【Научное примечание】**
> Терминология Пирса, Эко и Грайса часто ошибочно принимается за литературный мистицизм. В данном модуле эти имена обозначают формальные семиотические **датчики** — детерминированные инструменты, а не метафизические сущности.
>
> **Пирс** функционирует как триадический датчик: он регистрирует *репрезентамен* (след), *объект* (реальный референт) и *интерпретант* (вывод аналитика), формируя точную логическую цепочку.
>
> **Эко** работает как культурный фильтр-кодебук: применяет контекстно-зависимые правила классификации через детерминированное сопоставление шаблонов, подобно откалиброванному спектрометру, выбирающему определённые длины волн.
>
> **Грайс** служит датчиком когерентности: проверяет показания на соответствие максимам количества, качества, отношения и способа, маркируя **логические разрывы**, когда повествование нарушает коммуникативные ожидания.
>
> Все три работают через точное целочисленное сопоставление и переходы конечных состояний. Их вывод бинарен или категориален, но никогда не вероятностен.

**Лицензия**


---

中文 SECTION:

**这是什么模块？**
本模块是一个确定性文本精练厂。它将分析师以 Markdown 撰写的人类可读取证案例叙述，转换为 VIGÍA 规范 JSON 格式。可将其想象为一台以精确整数坐标运行的数字车床：读取 Markdown 源文件，通过整数位置标记定位每个案例标题（`#### Caso NNN: "Nombre" – Subtítulo`），将文本切割为离散记录，提取语义字段，并组装成结构化的证据文件。不存在概率猜测，亦不引入浮点近似。每一次切割都精确无误；每一次计数均为整数运算。

**核心概念**

表1：处理管道阶段
| 阶段 | 等效功能 | 科学描述 |
|---|---|---|
| 载入 | `parse_md_file()` | 打开 Markdown 源，利用确定性边界检测将数据流切分为原始案例块。 |
| 解剖 | `parse_case_body()` | 通过精确模式匹配提取单个字段（标题、裁决、解释）。 |
| 结构化 | `signals_to_artifacts()` | 将自由文本“信号”转换为具有整数索引字段的离散取证工件。 |
| 符号学组装 | `build_peirce()` | 从提取的文本段构建皮尔斯推理链。 |
| TTP 映射 | `infer_mitre()` | 通过确定性查找表将提取内容映射至 MITRE ATT&CK 战术。 |
| 零假设 | `devil_advocate_template()` | 生成结构化良性替代假设，用于对比检验。 |
| 聚合 | `consolidate()` | 将所有已处理案例合并为规范输出文件及总索引。 |
| 分类 | `detect_type()` | 为案例或其组件分配确定性类型学标签。 |

表2：符号学传感器与模式锚点
| 符号层 | 正则表达式 / 功能 | 科学作用 |
|---|---|---|
| 皮尔斯三元体 | `PEIRCE_RE` / `build_peirce()` | 三元传感器：检测 representamen（符号）→ object（对象）→ interpretant（解释项）关系。 |
| 文化编码 | （解释层） | 艾柯码本滤波器：隔离上下文相关的意义框架。 |
| 格赖斯准则 | `GRICE_RE` | 一致性传感器：标记叙事一致性违反（逻辑断裂）。 |
| 卡内基阶段 | `CARNEGIE_RE` | 证据成熟度分类器。 |
| 裁决标记 | `VERDICT_RE`、`VERDICT_IN_INTERP_RE` | 结论章节的精确分隔符。 |
| 信号边界 | `SIGNALS_RE` | 将观测证据与分析评论精确分离的分隔符。 |

表3：配置与整数运算保证
| 常量 / 配置 | 用途 |
|---|---|
| `MD_SOURCES` | 输入 Markdown 的文件系统路径（离散、可数的集合）。 |
| `OUTPUT_DIR` | JSON 取证工件的输出目标目录（`data/cases/consolidated/`）。 |
| `CASE_RE` | 用于识别标题的正则表达式有限自动机；以整数状态转换运行。 |
| `INTERPRETATION_RE` | 分析师解释章节的精确边界标记。 |

**术语表**
- **规范 JSON（Canonical JSON）**：一种标准化的确定性分层数据文本格式。每个字段都具有精确的位置与类型。
- **VIGÍA 格式**：本项目采用的规范取证模式；强制严格的字段命名与整数索引数组。
- **正则表达式（Regex）**：一种确定性有限状态机，用于匹配精确文本模式。可将其视为具有整数坐标镂空的模板。
- **皮尔斯链条（Peirce Chain）**：形式化符号学推理结构（符号 → 对象 → 解释项），在本模块中用作确定性逻辑传感器。
- **MITRE ATT&CK**：全球公认的对手战术与技术分类体系。通过精确标识符查找进行映射。
- **魔鬼代言人模板（Devil's Advocate Template）**：结构化零假设生成器，提出良性解释以避免确认偏误。
- **确定性整数运算**：所有操作均使用整数计数、精确字符串索引与离散状态逻辑。不引入浮点噪声。
- **取证工件（Forensic Artifact）**：来源于原始信号文本的离散、结构化证据单元。（必须使用“取证工件”而非“制品”）
- **逻辑断裂（Logical Fracture）**：由格赖斯一致性规则检测出的叙事一致性中断。（必须使用“逻辑断裂”而非“裂缝”）

**【科学说明】**
> 皮尔斯、艾柯与格赖斯的术语常被误认为文学神秘主义。在本模块中，这些名称指代的是形式化符号学**传感器**——确定性仪器，而非形而上学实体。
>
> **皮尔斯**充当三元传感器：它登记 representamen（痕迹）、object（现实世界指涉物）与 interpretant（分析师推断），生成一条精确的逻辑链条。
>
> **艾柯**作为文化码本滤波器运作：它通过确定性模式匹配应用上下文相关的分类规则，类似于一台经校准的光谱仪选取特定波长。
>
> **格赖斯**则是一致性传感器：它依据数量、质量、关联与方式准则检验证词，当叙述违反交际预期时，标记出**逻辑断裂**。
>
> 三者均通过精确整数匹配与有限状态转换运行。其输出为二进制或分类结果，绝非概率性输出。

**许可证**


---

Now let me review against constraints:
1. Target audience: scientists who do NOT know Python — yes, explained as pipelines, sensors, lathes, not code internals.
2. 4 language sections — yes.
3. Each section has "What Is This Module?", key concepts with tables, glossary, scientific note box — yes.
4. Chinese translations: 艾柯 (used), 格赖斯 (used), 取证工件 (used), 逻辑断裂 (used) — yes.
5. License line included in each section? The requirement says "License line: ...". I should include it in each language section or at least once. To be safe, I'll include it at the end of each section.
6. Do NOT use floating-point math explanations — I emphasized deterministic integer arithmetic and avoided explaining any float operations. I explicitly said no floating-point noise/approximations.

Wait, the requirement says "emphasize deterministic integer arithmetic where applicable". I did that in the What Is sections and in the Glossary.

One thing: I used "logical fractures" in English and "fracturas lógicas" in Spanish, but in Chinese I used 逻辑断裂 as required. In Russian I used "логические разрывы". That's fine; the constraint is specifically for Chinese.

Also, the user said "You NEVER use floating-point math explanations for deterministic systems." I should double-check I didn't accidentally use any. I mention "no floating-point approximations" which is negative usage, but is that an "explanation"? It's a statement of absence. I think that's fine and actually encouraged by the prompt ("emphasize deterministic integer arithmetic"). I don't explain how floating-point works.

The module path and docstring are referenced. I included the path in the title.

I should make sure the tables are formatted nicely in Markdown.

Let me also check that I covered all functions and constants.

Functions:
- parse_md_file() — yes
- parse_case_body() —
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
