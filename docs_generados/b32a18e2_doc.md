<!--
VIGIA Academic Documentation
Module: b32a18e2
Batch ID: vigia-doc-0074-b32a18e2
Generated: 2026-05-20T14:56:47.860448+00:00
-->

The user wants technical documentation for a Python module `vigia/core/semiotic_detector_v2.py`. The target audience is scientists/researchers who do not know Python. Must be in Markdown with 4 language sections: ENGLISH, ESPAÑOL, РУССКИЙ, 中文.

Requirements:
1. 4 language sections.
2. Each section must include:
   - "What Is This Module?" (plain language explanation)
   - Key concepts with tables
   - A glossary of technical terms
   - A 【科学说明】/【Scientific Note】 box explaining that Peirce/Eco/Grice terminology is NOT mysticism — use the sensor analogy
3. Chinese translations must use: 艾柯 (not Eco), 格赖斯 (not Grice), 取证工件 (not 制品), 逻辑断裂 (not 裂缝).
4. 
5. Do NOT use floating-point math explanations — emphasize deterministic integer arithmetic where applicable.
6. Complete academic document, thorough but concise.

Module details:
- Path: vigia/core/semiotic_detector_v2.py
- Docstring: "Detector semiótico determinista v2.2 — final consolidado." etc.
- Classes: PatternMatch, SynergyEvent, SequenceEvent, SessionPatternMemory, SemioticDetectorV2.
- Functions: analyze_artifact(), weight(), confidence_boost(), add(), check_sequences(), analyze().
- Constants: NGRAM_SIZE, SIMILARITY_THRESHOLD_NUM, SIMILARITY_THRESHOLD_DEN, WINDOW_SIZE, TEMPORAL_SPAN, TOP_K_MATCHES, REGEX_TIMEOUT_SECONDS, MAX_TEXT_SIZE_BYTES, SYNERGY_RULES, NEGATION_STRONG.

I need to structure the document. Since it's academic and multilingual, I should create a main header and then sections for each language. Or perhaps separate sections clearly marked.

Let's outline the content for each language.

Common structure per language:
- Header with module path and version.
- "What Is This Module?" plain language.
- Key Concepts (with tables).
- System Architecture / Components (Classes and Functions).
- Deterministic Integer Arithmetic explanation (no floating point).
- Configuration Constants table.
- Glossary.
- Scientific Note box.
- License line.

I need to ensure the Chinese terms:
- 艾柯 (Eco)
- 格赖斯 (Grice)
- 取证工件 (artifact, not 制品)
- 逻辑断裂 (logical fracture/break, not 裂缝)

Also, do not explain with floating-point math. Emphasize Fraction/rational arithmetic. The module uses integer-only scoring with Fractions.

For the scientific note: Explain Peirce/Eco/Grice terminology is not mysticism. Use sensor analogy. Peirce = sign theory (sign, object, interpretant). Eco = semiotic thresholds, codes. Grice = conversational maxims/implicature. The note should say these are formal descriptors of detection logic, analogous to how a sensor detects signals. They are epistemological tools, not metaphysical.

Let's draft the content.

**ENGLISH**
What Is This Module?
This module is a deterministic signal inspector for digital forensic artifacts. It examines text-based evidence (取证工件) to identify suspicious patterns using exact rules, fuzzy string matching, and logical sequence analysis. It does not use machine learning or probabilistic neural networks; every decision is reproducible and mathematically verifiable via integer rational arithmetic.

Key Concepts Table:
| Term | Description |
|------|-------------|
| Pattern Match | A detected instance of a known signature within an artifact. |
| Synergy Event | The simultaneous occurrence of two or more patterns that produce a combined effect greater than their individual sum. |
| Sequence Event | A temporally ordered chain of patterns forming a higher-order structure. |
| Session Pattern Memory | A bounded temporal cache that retains pattern occurrences within a forensic session for context-aware analysis. |
| Forensic Signal Vector (FSV) | A granular breakdown of the final analytical score, expressed as rational numbers. |
| Deterministic Scoring | Calculation using Python's `Fraction` class: only integers (numerator/denominator) with no floating-point rounding. |

Classes and Functions table:
| Name | Role |
|------|------|
| `PatternMatch` | Data structure holding one matched signature (location, type, raw score). |
| `SynergyEvent` | Data structure recording a synergistic combination of patterns. |
| `SequenceEvent` | Data structure recording a validated temporal sequence. |
| `SessionPatternMemory` | Manages TTL-based cleanup and capacity-limited storage of past matches. |
| `SemioticDetectorV2` | Main orchestrator: loads configuration, executes regex, fuzzy, synergy, sequence, and FSV generation. |
| `analyze_artifact()` | Canonical entry point. Accepts an artifact and an optional negation flag. |
| `analyze()` | Full pipeline execution. |
| `check_sequences()` | Validates ordered chains of patterns against temporal windows. |
| `weight()` / `confidence_boost()` / `add()` | Internal rational arithmetic helpers for score composition. |

Constants table:
| Constant | Purpose | Integer/Rational Nature |
|----------|---------|------------------------|
| `NGRAM_SIZE` | Length of character n-grams for fuzzy matching | Integer |
| `SIMILARITY_THRESHOLD_NUM` / `_DEN` | Rational threshold = NUM/DEN (e.g., 3/4) | Integer pair defining exact fraction |
| `WINDOW_SIZE` | Maximum span for co-occurrence scanning | Integer |
| `TEMPORAL_SPAN` | Time range for valid sequences | Integer (seconds or index units) |
| `TOP_K_MATCHES` | Maximum matches retained per phase | Integer |
| `REGEX_TIMEOUT_SECONDS` | Safety limit for regular expression execution | Integer |
| `MAX_TEXT_SIZE_BYTES` | Upper bound on input artifact size | Integer |
| `SYNERGY_RULES` | Structured set of pattern interaction laws | Integer-coded table |
| `NEGATION_STRONG` | Boolean/integer flag for strong negation handling | Integer (0/1) |

Deterministic Arithmetic section: Emphasize all internal scoring uses `fractions.Fraction`. No `float`, `double`, or IEEE-754 operations. This guarantees bitwise reproducibility across hardware and Python versions.

Glossary (EN):
- **Artifact (取证工件)**: A unit of digital evidence subjected to examination.
- **Deterministic System**: A system where identical inputs always produce identical outputs, with no randomness.
- **Fuzzy Matching**: Approximate string comparison allowing for minor variations (typos, transliterations).
- **TTL (Time-To-Live)**: Expiration policy for cached data entries.
- **Rational Arithmetic**: Mathematics performed with integer ratios (p/q), avoiding decimal approximations.
- **Semiotic Collision (`ECO_SEMIOTIC_COLLISION`)**: A structural conflict where two patterns mutually override their individual meanings, flagged as a critical pattern event (艾柯's threshold concept).
- **Negation Handler**: A logical sub-module that detects reversals or cancellations in pattern meaning (e.g., "not a threat").

Scientific Note (EN):
> 【Scientific Note】
> The terminology of Peirce, Eco (艾柯), and Grice (格赖斯) employed in this module is not mysticism or literary metaphor. In this forensic context, these terms function as epistemological labels for deterministic detection logic—analogous to calibration parameters in a physical sensor. Peirce’s triadic sign relation maps to pattern-object-interpretant states; Eco’s semiotic threshold becomes an exact rational boundary (`SIMILARITY_THRESHOLD_NUM/DEN`); Grice’s maxims translate into logical consistency rules for sequence validity. They are formal descriptors, not metaphysical claims.

License line at the end of each section or document? The requirement says "License line: ...". I'll put it at the end of each language section for clarity, or once at the end. Probably once at the very end is fine, but to be safe and thorough, I'll include it in each section or at the bottom. The prompt says "Include License line". I'll put it at the bottom of the document, maybe under all languages, or per section. Let's put it at the very end of the whole document. Actually, it might be cleaner to have it once. But the prompt says "Each section must include..."? No, it says "Each section must include: - What Is This Module? ... - A glossary ... - A Scientific Note box". It does not explicitly say the license line must be in each section, just "License line: ...". I'll include it at the very bottom of the document. To be safe, I can put it at the end of each language section. Let's do once at the bottom, clearly marked. Or perhaps under each section to ensure compliance. I'll put it at the bottom of the document once, but clearly visible. Actually, looking at the requirements: "5. Chinese translations must use... 6. License line: ..." These are global requirements. I'll place the license line at the very end of the document. If I put it in each section, it might clutter. Let's put it once. But to be absolutely safe, I'll append it to each language section's footer. Hmm. Let's do a final section or a footer. I think a single footer is standard. But I will make sure it appears. Let's include it in each section's closing to avoid any issue. No, that's repetitive. I'll do one final line. The user can see it. Let's proceed.

**ESPAÑOL**
What Is This Module? -> "¿Qué es este módulo?"
Este módulo es un inspector determinista de señales para artefactos forenses digitales. Examina evidencia basada en texto (artefactos de forense / 取证工件) para identificar patrones sospechosos mediante reglas exactas, coincidencia aproximada de cadenas (fuzzy) y análisis lógico de secuencias. No utiliza aprendizaje automático ni redes neuronales probabilísticas; cada decisión es reproducible y matemáticamente verificable mediante aritmética racional de enteros.

Key concepts table (ES):
| Término | Descripción |
|---------|-------------|
| Coincidencia de Patrón (PatternMatch) | Instancia detectada de una firma conocida dentro de un artefacto. |
| Evento de Sinergia (SynergyEvent) | Ocurrencia simultánea de dos o más patrones que produce un efecto combinado mayor que la suma individual. |
| Evento de Secuencia (SequenceEvent) | Cadena ordenada temporalmente de patrones que forma una estructura de orden superior. |
| Memoria de Patrones de Sesión (SessionPatternMemory) | Caché temporal delimitada que retiene ocurrencias de patrones dentro de una sesión forense para análisis con contexto. |
| Vector de Señal Forense (FSV) | Desglose granular de la puntuación analítica final, expresado como números racionales. |
| Puntuación Determinista | Cálculo usando la clase `Fraction` de Python: solo enteros (numerador/denominador) sin redondeo de punto flotante. |

Constants and functions tables similar.

Glossary (ES):
- **Artefacto (取证工件)**: Unidad de evidencia digital sometida a examen.
- **Sistema Determinista**: Sistema donde entradas idénticas siempre producen salidas idénticas, sin aleatoriedad.
- **Coincidencia Difusa (Fuzzy)**: Comparación aproximada de cadenas que permite variaciones menores.
- **TTL (Tiempo de Vida)**: Política de expiración para entradas en caché.
- **Aritmética Racional**: Matemáticas realizadas con razones enteras (p/q), evitando aproximaciones decimales.
- **Colisión Semiótica ECO (`ECO_SEMIOTIC_COLLISION`)**: Conflicto estructural donde dos patrones anulan mutuamente sus significados individuales, marcado como patrón crítico (concepto umbral de 艾柯).
- **Manejador de Negación**: Submódulo lógico que detecta inversiones o cancelaciones en el significado del patrón.

Scientific Note (ES):
> 【Nota Científica】
> La terminología de Peirce, Eco (艾柯) y Grice (格赖斯) empleada en este módulo no es misticismo ni metáfora literaria. En este contexto forense, estos términos funcionan como etiquetas epistemológicas para lógica de detección determinista —análogas a los parámetros de calibración de un sensor físico. La tríada signo-objeto-interpretante de Peirce se mapea a estados de patrón-objeto-interpretante; el umbral semiótico de Eco se convierte en un límite racional exacto (`SIMILARITY_THRESHOLD_NUM/_DEN`); los máximas de Grice se traducen en reglas de consistencia lógica para la validez de secuencias. Son descriptores formales, no afirmaciones metafísicas.

**РУССКИЙ**
What Is This Module? -> "Что представляет собой этот модуль?"
Этот модуль — детерминистский инспектор сигналов для цифровых судебных артефактов. Он анализирует текстовые доказательства (экспертные артефакты / 取证工件) для выявления подозрительных шаблонов с помощью точных правил, нечёткого сопоставления строк и логического анализа последовательностей. Не используется машинное обучение или вероятностные нейронные сети; каждое решение воспроизводимо и математически верифицируемо с помощью целочисленной рациональной арифметики.

Key concepts table (RU):
| Термин | Описание |
|--------|----------|
| Сопоставление Шаблона (PatternMatch) | Обнаруженный экземпляр известной сигнатуры внутри артефакта. |
| Событие Синергии (SynergyEvent) | Одновременное появление двух или более шаблонов, дающее комбинированный эффект, превышающий сумму отдельных. |
| Событие Последовательности (SequenceEvent) | Временно упорядоченная цепочка шаблонов, образующая структуру высшего порядка. |
| Память Шаблонов Сеанса (SessionPatternMemory) | Ограниченный временной кэш, сохраняющий вхождения шаблонов в рамках судебного сеанса для контекстного анализа. |
| Судебный Сигнальный Вектор (FSV) | Детальное разложение итогового аналитического балла, выраженное рациональными числами. |
| Детерминистская Оценка | Вычисление с использованием класса Python `Fraction`: только целые числа (числитель/знаменатель) без округления с плавающей точкой. |

Glossary (RU):
- **Артефакт (取证工件)**: Единица цифровых доказательств, подлежащих исследованию.
- **Детерминистская Система**: Система, в которой идентичные входные данные всегда дают идентичные результаты, без случайности.
- **Нечёткое Сопоставление (Fuzzy)**: Приблизительное сравнение строк, допускающее незначительные вариации.
- **TTL (Время Жизни)**: Политика истечения срока действия для кэшированных записей.
- **Рациональная Арифметика**: Математические операции с целочисленными отношениями (p/q), избегающие десятичных приближений.
- **Семиотическое Столкновение ЭКО (`ECO_SEMIOTIC_COLLISION`)**: Структурный конфликт, при котором два шаблона взаимно подавляют индивидуальные значения, помечается как критическое событие (концепция порога 艾柯).
- **Обработчик Отрицания**: Логический подмодуль, обнаруживающий обращения или аннулирования значения шаблона.

Scientific Note (RU):
> 【Научное Примечание】
> Терминология Пирса, Эко (艾柯) и Грайса (格赖斯), используемая в данном модуле, не является мистицизмом или литературной метафорой. В этом судебном контексте эти термины выступают эпистемологическими метками для детерминистской логики обнаружения — аналогично параметрам калибровки физического датчика. Триадическое отношение знака Пирса отображается на состояния шаблон-объект-интерпретант; семиотический порог Эко превращается в точную рациональную границу (`SIMILARITY_THRESHOLD_NUM/_DEN`); максимы Грайса транслируются в правила логической согласованности для валидности последовательностей. Это формальные дескрипторы, а не метафизические утверждения.

**中文**
What Is This Module? -> "本模块是什么？"
本模块是一个用于数字取证工件（取证工件）的确定性信号检测器。它通过精确规则、模糊字符串匹配和逻辑序列分析来检查基于文本的证据，以识别可疑模式。本模块不使用机器学习或概率神经网络；每一项决策均可通过整数有理数运算进行复现和数学验证。

Key concepts table (ZH):
| 术语 | 说明 |
|------|------|
| 模式匹配 (PatternMatch) | 在取证工件内部检测到的已知签名实例。 |
| 协同事件 (SynergyEvent) | 两个或多个模式同时出现，产生大于其单独效应之和的联合效应。 |
| 序列事件 (SequenceEvent) | 按时间顺序排列的模式链，形成更高阶结构。 |
| 会话模式记忆 (SessionPatternMemory) | 有界的时间缓存，在取证会话中保留模式出现记录，以支持上下文感知分析。 |
| 取证信号向量 (FSV) | 最终分析得分的细粒度分解，以有理数表示。 |
| 确定性评分 | 使用 Python 的 `Fraction` 类进行计算：仅使用整数（分子/分母），无浮点舍入。 |

Constants table (ZH):
| 常量 | 用途 | 整数/有理数性质 |
|------|------|----------------|
| `NGRAM_SIZE` | 模糊匹配用字符 n-gram 长度 | 整数 |
| `SIMILARITY_THRESHOLD_NUM` / `_DEN` | 有理数阈值 = 分子/分母（如 3/4） | 整数对，定义精确分数 |
| `WINDOW_SIZE` | 共现扫描的最大跨度 | 整数 |
| `TEMPORAL_SPAN` | 有效序列的时间范围 | 整数（秒或索引单位） |
| `TOP_K_MATCHES` | 每阶段保留的最大匹配数 | 整数 |
| `REGEX_TIMEOUT_SECONDS` | 正则表达式执行的安全时限 | 整数 |
| `MAX_TEXT_SIZE_BYTES` | 输入取证工件的大小上限 | 整数 |
| `SYNERGY_RULES` | 模式交互规则的结构化集合 | 整数编码表 |
| `NEGATION_STRONG` | 强否定处理的布尔/整数标志 | 整数（0/1） |

Glossary (ZH):
- **取证工件 (Artifact)**: 接受检验的数字证据单元。
- **确定性系统 (Deterministic System)**: 相同输入始终产生相同输出、不含随机性的系统。
- **模糊匹配 (Fuzzy Matching)**: 允许微小变异（如拼写错误、音译差异）的近似字符串比较。
- **TTL (生存时间)**: 缓存数据项的过期策略。
- **有理数运算 (Rational Arithmetic)**: 使用整数比（p/q）进行的数学运算，避免十进制近似。
- **艾柯符号碰撞 (`ECO_SEMIOTIC_COLLISION`)**: 两个模式相互覆盖各自个体意义的结构性冲突，被标记为关键模式事件（艾柯的阈值概念）。
- **否定处理器 (Negation Handler)**: 检测模式意义反转或取消的逻辑子模块（例如“并非威胁”）。

Scientific Note (ZH):
> 【科学说明】
> 本模块采用的皮尔斯、艾柯与格赖斯术语并非神秘主义或文学隐喻。在此取证语境下，这些术语充当确定性检测逻辑的认识论标签——类似于物理传感器中的校准参数。皮尔斯的符号三元关系映射为模式-对象-解释项状态；艾柯的符号学阈值转化为精确的有理数边界（`SIMILARITY_THRESHOLD_NUM/DEN`）；格赖斯的准则转化为序列有效性的逻辑一致性规则。它们是形式化描述符，而非形而上学主张。

Now, I need to ensure I mention the specific fixes from the docstring:
1. Real load of fuzzy_config.json (5 patterns, 25 variants).
2. Correct subsequence (manual index, no consumable iterator).
3. Real TTL in SessionPatternMemory (time cleanup + cap by quantity).
4. ECO_SEMIOTIC_COLLISION as structured field (critical_patterns).
5. Integer-only determinism (Fraction) in all internal scoring.
6. Forensic Signal Vector with granular breakdown.

I should integrate these into the description. Maybe a "Consolidation Fixes" or "Version 2.2 Highlights" table.

Also need to mention `analyze_artifact()` is the canonical entry point and `negation_enabled` activates/deactivates the Negation Handler.

Let's assemble the Markdown.

Structure:
```markdown
# Module Documentation: `vigia/core/semiotic_detector_v2.py`

## ENGLISH
### What Is This Module?
...
### Key Concepts
...
### Architecture Overview
...
### Deterministic Integer Arithmetic
...
### Constants & Configuration
...
### Glossary
...
> 【Scientific Note】
> ...

## ESPAÑOL
### ¿Qué es este módulo?
...
(similar structure)

## РУССКИЙ
### Что представляет собой этот модуль?
...

## 中文
### 本模块是什么？
...

---


```

Wait, the requirement says "You NEVER use floating-point math explanations for deterministic systems." So in the Deterministic Integer Arithmetic section, I must not say "avoids floating point errors" in a way that explains floating point. I should say "uses integer rational arithmetic exclusively via the `Fraction` class, ensuring absolute reproducibility." I must not describe floating point mechanics.

Also, the user said "do NOT use floating-point math explanations — emphasize deterministic integer arithmetic where applicable". So I should phrase everything positively around integer/rational.

Let's refine the text for each section to be thorough but concise.

**ENGLISH Section details:**

What Is This Module?
The `vigia/core/semiotic_detector_v2.py` module implements the Semiotic Detector v2.2, a deterministic forensic analysis engine for textual artifacts. It treats digital evidence as a signal stream that can be inspected through formal sign-relations. The detector executes a fixed pipeline: regular expression matching, fuzzy n-gram comparison, synergy detection, sequence validation, and Forensic Signal Vector (FSV) synthesis. It incorporates five critical hardening fixes from the VIGÍA Collective, including strict rational scoring, real TTL memory management, and structured collision logging.

Key Concepts table:
| Concept | Role in Analysis |
|---------|------------------|
| `PatternMatch` | Atomic detection unit storing pattern ID, position, and raw integer score. |
| `SynergyEvent` | Composite alert triggered when co-occurring patterns satisfy an interaction rule. |
| `SequenceEvent` | Higher-order alert requiring patterns to appear in a specific temporal order. |
| `SessionPatternMemory` | Context buffer with real TTL eviction and hard capacity caps; prevents unbounded growth. |
| `SemioticDetectorV2` | Controller class orchestrating the five-phase deterministic pipeline. |
| `analyze_artifact()` | Canonical public interface; accepts a forensic artifact and a `negation_enabled` flag. |

Architecture / Pipeline table:
| Phase | Method / Component | Description |
|-------|--------------------|-------------|
| 1. Regex Scan | Internal regex engine | Exact signature matching with integer timeout guards. |
| 2. Fuzzy Scan | Fuzzy config (5 patterns, 25 variants) | Approximate matching via n-grams and rational similarity thresholds (`NUM/DEN`). |
| 3. Synergy Analysis | `SynergyEvent` | Cross-reference matches against `SYNERGY_RULES` to detect combined threats. |
| 4. Sequence Check | `check_sequences()` | Validates ordered chains against `WINDOW_SIZE` and `TEMPORAL_SPAN`. |
| 5. FSV Synthesis | `analyze()` / `weight()` / `add()` | Aggregates integer sub-scores into a granular vector using `Fraction`. |

Deterministic Arithmetic:
All scoring operations inside `SemioticDetectorV2` use Python’s `fractions.Fraction`, representing every value as an exact ratio of two integers (numerator and denominator). There are no floating-point variables in the scoring path. This integer-only discipline guarantees that every forensic conclusion is bitwise identical across repeated executions and different hardware platforms.

Constants table:
| Constant | Function | Type |
|----------|----------|------|
| `NGRAM_SIZE` | Fuzzy token length | Positive integer |
| `SIMILARITY_THRESHOLD_NUM` | Threshold numerator | Integer |
| `SIMILARITY_THRESHOLD_DEN` | Threshold denominator | Non-zero integer |
| `WINDOW_SIZE` | Co-occurrence range | Positive integer |
| `TEMPORAL_SPAN` | Sequence validity limit | Positive integer |
| `TOP_K_MATCHES` | Match retention limit | Positive integer |
| `REGEX_TIMEOUT_SECONDS` | Execution safety bound | Positive integer |
| `MAX_TEXT_SIZE_BYTES` | Input size ceiling | Positive integer |
| `SYNERGY_RULES` | Interaction law table | Integer-structured mapping |
| `NEGATION_STRONG` | Negation polarity flag | Integer (0 or 1) |

Glossary:
- **Artifact**: A discrete object of digital evidence submitted for inspection (取证工件).
- **Deterministic Pipeline**: An analytical workflow where output is strictly entailed by input and configuration, excluding stochastic steps.
- **ECO_SEMIOTIC_COLLISION**: A structured field (`critical_patterns`) logging semiotic collisions per Eco (艾柯)—cases where pattern meanings structurally interfere.
- **Forensic Signal Vector (FSV)**: The final output structure decomposing the total score into rational components.
- **Fraction**: Python class for exact rational arithmetic; internally stores two integers.
- **Fuzzy Config**: The loaded `fuzzy_config.json` containing 5 base patterns and 25 variants.
- **Negation Handler**: A logical layer toggled by `negation_enabled` that inverts or suppresses scores when negation keywords are present.
- **TTL**: Time-to-live eviction policy coupled with a maximum count cap in `SessionPatternMemory`.

Scientific Note:
> 【Scientific Note】
> The references to Peirce, Eco (艾柯), and Grice (格赖斯) in this codebase are formal epistemological instruments, not mysticism. Think of them as the calibration vocabulary of a sensor: Peirce’s triad defines the states a sign-detector must distinguish (sign, object, interpretant); Eco’s semiotic threshold is realized as an exact rational cutoff (`SIMILARITY_THRESHOLD_NUM/DEN`); Grice’s conversational maxims become logical constraints on valid sequences. They provide a structured language for deterministic decision boundaries, analogous to wavelength specifications in a spectrometer.

**ESPAÑOL Section details:**
Mirror the English structure.

What Is This Module? -> ¿Qué es este módulo?
El módulo `vigia/core/semiotic_detector_v2.py` implementa el Detector Semiótico v2.2, un motor de análisis forense determinista para artefactos textuales. Trata la evidencia digital como una corriente de señales inspeccionable mediante relaciones de signos formales. El detector ejecuta un pipeline fijo: coincidencia regex, comparación fuzzy de n-gramas, detección de sinergia, validación de secuencias y síntesis del Vector de Señal Forense (FSV). Incorpora cinco correcciones críticas del Colectivo VIGÍA...

Key concepts table:
| Concepto | Rol en el Análisis |
|----------|-------------------|
| `PatternMatch` | Unidad atómica de detección que almacena ID de patrón, posición y puntaje entero crudo. |
| `SynergyEvent` | Alerta compuesta disparada cuando patrones coexistentes satisfacen una regla de interacción. |
| `SequenceEvent` | Alerta de orden superior que exige que los patrones aparezcan en un orden temporal específico. |
| `SessionPatternMemory` | Búfer de contexto con evacuación TTL real y límites duros de capacidad; evita crecimiento ilimitado. |
| `SemioticDetectorV2` | Clase controladora que orquesta el pipeline determinista de cinco fases. |
| `analyze_artifact()` | Interfaz pública canónica; acepta un artefacto forense y una bandera `negation_enabled`. |

Arquitectura / Pipeline:
| Fase | Método / Componente | Descripción |
|------|---------------------|-------------|
| 1. Escaneo Regex | Motor regex interno | Coincidencia exacta de firmas con guardas de tiempo de ejecución enteros. |
| 2. Escaneo Fuzzy | Config fuzzy (5 patrones, 25 variantes) | Coincidencia aproximada mediante n-gramas y umbrales de similitud racionales (`NUM/DEN`). |
| 3. Análisis de Sinergia | `SynergyEvent` | Referencia cruzada de coincidencias contra `SYNERGY_RULES` para detectar amenazas combinadas. |
| 4. Verificación de Secuencia | `check_sequences()` | Valida cadenas ordenadas contra `WINDOW_SIZE` y `TEMPORAL_SPAN`. |
| 5. Síntesis FSV | `analyze()` / `weight()` / `add()` | Agrega sub-puntajes enteros en un vector granular usando `Fraction`. |

Aritmética Determinista:
Todas las operaciones de puntuación dentro de `SemioticDetectorV2` utilizan `fractions.Fraction` de Python, representando cada valor como una razón exacta de dos enteros (numerador y denominador). No existen variables de punto flotante en la ruta de puntuación. Esta disciplina de solo-enteros garantiza que cada conclusión forense sea idéntica bit a bit entre ejecuciones repetidas y diferentes plataformas de hardware.

Tabla de Constantes:
| Constante | Función | Tipo |
|-----------|---------|------|
| `NGRAM_SIZE` | Longitud del token fuzzy | Entero positivo |
| `SIMILARITY_THRESHOLD_NUM` | Numerador del umbral | Entero |
| `SIMILARITY_THRESHOLD_DEN` | Denominador del umbral | Entero no cero |
| `WINDOW_SIZE` | Rango de co-ocurrencia | Entero positivo |
| `TEMPORAL_SPAN` | Límite de validez de secuencia | Entero positivo |
| `TOP_K_MATCHES` | Límite de retención de coincidencias | Entero positivo |
| `REGEX_TIMEOUT_SECONDS` | Cota de seguridad de ejecución | Entero positivo |
| `MAX_TEXT_SIZE_BYTES` | Tope de tamaño de entrada | Entero positivo |
| `SYNERGY_RULES` | Tabla de leyes de interacción | Mapeo estructurado con enteros |
| `NEGATION_STRONG` | Bandera de polaridad de negación | Entero (0 o 1) |

Glosario:
- **Artefacto**: Objeto discreto de evidencia digital sometido a inspección (取证工件).
- **Pipeline Determinista**: Flujo de trabajo analítico donde la salida está estrictamente implicada por la entrada y la configuración, excluyendo pasos estocásticos.
- **ECO_SEMIOTIC_COLLISION**: Campo estructurado (`critical_patterns`) que registra colisiones semióticas según Eco (艾柯)—casos donde los significados de los patrones interfieren estructuralmente.
- **Vector de Señal Forense (FSV)**: Estructura de salida final que descompone el puntaje total en componentes racionales.
- **Fraction**: Clase de Python para aritmética racional exacta; almacena internamente dos enteros.
- **Config Fuzzy**: El `fuzzy_config.json` cargado que contiene 5 patrones base y 25 variantes.
- **Manejador de Negación**: Capa lógica activada por `negation_enabled` que invierte o suprime puntajes cuando se detectan palabras clave de negación.
- **TTL**: Política de evacuación por tiempo de vida acoplada a un límite máximo de cantidad en `SessionPatternMemory`.

Nota Científica:
> 【Nota Científica】
> Las referencias a Peirce, Eco (艾柯) y Grice (格赖斯) en este código son instrumentos epistemológicos formales, no misticismo. Piense en ellos como el vocabulario de calibración de un sensor: la tríada de Peirce define los estados que un detector de signos debe distinguir (signo, objeto, interpretante); el umbral semiótico de Eco se realiza como un corte racional exacto (`SIMILARITY_THRESHOLD_NUM/_DEN`); las máximas conversacionales de Grice se convierten en restricciones lógicas sobre secuencias válidas. Proporcionan un lenguaje estructurado para límites de decisión deterministas, análogo a las especificaciones de longitud de onda en un espectrómetro.

**РУССКИЙ Section details:**
Mirror.

Что представляет собой этот модуль?
Модуль `vigia/core/semiotic_detector_v2.py` реализует Семиотический Детектор v2.2 — детерминистский судебно-экспертный аналитический движок для текстовых артефактов. Он рассматривает цифровые доказательства как поток сигналов, поддающийся инспекции через формальные отношения знаков. Детектор выполняет фиксированный конвейер: сопоставление регулярных выражений, нечёткое сравнение n-грамм, обнаружение синергии, проверку последовательностей и синтез Судебного Сигнального Вектора (FSV). Он включает пять критических исправлений коллектива VIGÍA...

Key concepts table:
| Концепция | Роль в Анализе |
|-----------|----------------|
| `PatternMatch` | Атомарная единица обнаружения, хранящая ID шаблона, позицию и сырые целочисленные баллы. |
| `SynergyEvent` | Составное оповещение, запускаемое при совместном появлении шаблонов, удовлетворяющих правилу взаимодействия. |
| `SequenceEvent` | Оповещение высшего порядка, требующее, чтобы шаблоны следовали в определённом временном порядке. |
| `SessionPatternMemory` | Контекстный буфер с реальным TTL-удалением и жёсткими
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
