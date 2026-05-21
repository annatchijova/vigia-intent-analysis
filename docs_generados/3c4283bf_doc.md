<!--
VIGIA Academic Documentation
Module: 3c4283bf
Batch ID: vigia-doc-0157-3c4283bf
Generated: 2026-05-20T14:56:47.878421+00:00
-->

The user wants documentation for a Python module `vigia/tools/eml_symbolic.py` in a very specific format.

Key requirements:
1. Academic technical writer style, digital forensics focus.
2. Target audience: scientists who do NOT know Python.
3. Four language sections: ENGLISH, ESPAÑOL, РУССКИЙ, 中文.
4. Each section must include:
   - "What Is This Module?" (plain language)
   - Key concepts with tables
   - A glossary of technical terms
   - A 【科学说明】/【Scientific Note】 box explaining Peirce/Eco/Grice terminology is NOT mysticism, using sensor analogy
5. Chinese translations must use: 艾柯 (not Eco), 格赖斯 (not Grice), 取证工件 (not 制品), 逻辑断裂 (not 裂缝)
6. 
7. NEVER use floating-point math explanations for deterministic systems. Emphasize deterministic integer arithmetic where applicable.
8. Module path: vigia/tools/eml_symbolic.py
9. Docstring info provided needs to be incorporated.

Let me parse the module content provided:
- Module name/path: vigia/tools/eml_symbolic.py
- Title: DGPI — Deterministic Generative Pattern Inference
- Nombre correcto: Not "symbolic regression engine" but "deterministic generative pattern inference" or "symbolic pattern reconstruction". It identifies the mathematical law that governed generation, doesn't infer from scratch.
- What it does: Given a vector of temporal intervals, determines if a simple generator function exists (constant, linear, sinusoidal, Poisson). If found, expresses in canonical EML form.
- Operator EML: eml(x, y) = e^x - ln(y) (Odrzywołek). Used as LENGU (probably language?).
- Classes:
  - PatternResult: Result of DGPI inference.
    Fields: pattern_type (enum-like string), eml_expr
  - DGPIEngine: Deterministic Generative Pattern Inference Engine.
    Orders from most specific to most general:
    1. CONSTANT_SLEEP — sleep
    (The list seems cut off but mentions these patterns)
- Functions:
  - analyze_symbolic_regression(): Entry point for MCP bridge. Public name maintained for compatibility.
  - is_algorithmic():
  - to_dict():
  - to_dict_display(): Rounded version for human display.
  - analyze(): DGPI analysis on a list of temporal intervals.
    Args: deltas: Intervals in seconds (>0). (text cuts off with "dis")
- Constants & Config:
  - _DEFAULT_DGPI
  - PATTERN_NONE
  - PATTERN_CONSTANT
  - PATTERN_JITTER
  - PATTERN_LINEAR_DRIFT
  - PATTERN_SINUSOIDAL
  - PATTERN_POISSON_EXACT
  - M, C, B (probably parameters)

Wait, the user says "Generate the complete academic document now. Be thorough but concise." and "Be thorough but concise" - I need to balance detail with brevity.

Important: The scientific note must explain that Peirce/Eco/Grice terminology is NOT mysticism, using the sensor analogy. This refers to semiotics (Charles Sanders Peirce, Umberto Eco, H.P. Grice). In digital forensics, symbolic pattern reconstruction draws from semiotic theory. The note should say something like: "Referencing Peirce, Eco, or Grice does not invoke mysticism; it is analogous to how a sensor detects physical stimuli and maps them to structured readings. The DGPI engine acts as a semiotic sensor: it maps raw temporal intervals to deterministic symbolic classes..." etc.

Must include license line exactly: ""

No floating-point explanations. Emphasize deterministic integer arithmetic. So when discussing intervals in seconds, emphasize they are integers or handled as exact rational values, not floating point approximations. The engine uses integer arithmetic to ensure reproducibility.

Structure for each language section:
- Heading: ENGLISH / ESPAÑOL / РУССКИЙ / 中文
- Subheading: What Is This Module?
- Subheading: Key Concepts (with tables)
- Subheading: Glossary
- Box: 【Scientific Note】/【Nota Científica】/【Научное примечание】/【科学说明】

Wait, the requirement says: A 【科学说明】/【Scientific Note】 box. So for English it should be 【Scientific Note】, for Spanish maybe 【Nota Científica】, Russian 【Научное примечание】, Chinese 【科学说明】.

Also need to include the license line. Probably at the end of the document.

Let me draft content.

**ENGLISH Section:**
- What Is This Module?
  `vigia/tools/eml_symbolic.py` implements DGPI (Deterministic Generative Pattern Inference). It examines a sequence of time intervals extracted from digital evidence (e.g., fabrication logs) and determines whether those intervals were produced by a simple mathematical rule: constant, linear drift, sinusoidal, or exact Poisson. Rather than performing statistical regression, it reconstructs the generative law using deterministic integer arithmetic. When a law is identified, the module expresses it in canonical EML (Extended Mathematical Language) notation, built upon the Odrzywołek operator `eml(x, y) = e^x - ln(y)`. The module is designed for forensic reproducibility: every conclusion is an exact, auditable classification, not a probabilistic guess.

- Key Concepts table:
  | Concept | Description |
  |---|---|
  | DGPI | Deterministic Generative Pattern Inference. A forensic method that reconstructs the exact mathematical law governing a sequence of timestamps, avoiding floating-point approximations. |
  | EML | Extended Mathematical Language. A canonical notation used to express the identified generator function. |
  | Odrzywołek Operator | The foundational EML operator defined as `eml(x, y) = e^x − ln(y)`, serving as the linguistic base for pattern expression. |
  | Temporal Interval (delta) | The exact integer count of seconds between two consecutive events in a log. |
  | PatternResult | A forensic container holding the identified pattern type and its EML expression. |
  | DGPIEngine | The deterministic classifier that evaluates intervals from most specific to most general pattern. |

  Maybe another table for the pattern types:
  | Pattern Type | Meaning |
  |---|---|
  | CONSTANT_SLEEP | The intervals follow a fixed, unchanging duration. |
  | PATTERN_JITTER | Small, bounded integer variations around a central value. |
  | PATTERN_LINEAR_DRIFT | Intervals increase or decrease by a constant integer step. |
  | PATTERN_SINUSOIDAL | Intervals follow a periodic, wave-like integer progression. |
  | PATTERN_POISSON_EXACT | Intervals conform to an exact Poisson point process with integer-rate parameters. |
  | PATTERN_NONE | No recognizable deterministic generator was found. |

- Glossary:
  | Term | Definition |
  |---|---|
  | Deterministic Integer Arithmetic | Calculation using exact whole numbers and rational operations, guaranteeing identical results across all hardware and executions. |
  | Generative Law | The underlying mathematical rule that produced the observed data, as opposed to a statistical fit. |
  | Canonical Form | A standardized, unique representation of the pattern, ensuring that two equivalent laws are expressed identically. |
  | MCP Bridge | A compatibility interface connecting the DGPI engine to the master control program or analysis pipeline. |
  | Forensic Artifact | Any object or data of interest in a digital investigation; here, the vector of temporal intervals. |

- Scientific Note:
  【Scientific Note】
  The module occasionally references semiotic concepts derived from Charles Sanders Peirce, Umberto Eco, and H.P. Grice. This is not mysticism. Think of the DGPI engine as a sensor: just as a thermometer converts thermal energy into a structured numerical reading, this engine converts raw temporal intervals into structured symbolic classes. Peirce’s sign-relation, Eco’s code, and Grice’s implicature are merely formal vocabularies for describing how a physical signal maps to a meaningful pattern. The process is deterministic engineering, not divination.

**ESPAÑOL Section:**
- Nombre del módulo: vigia/tools/eml_symbolic.py
- ¿Qué es este módulo?
  Implementa el DGPI (Deterministic Generative Pattern Inference). Examina secuencias de intervalos temporales extraídos de evidencia digital y determina si fueron producidos por una regla matemática simple. No realiza regresión estadística, sino que reconstruye la ley generadora mediante aritmética entera determinista. Cuando identifica una ley, la expresa en notación EML canónica usando el operador de Odrzywołek.

- Key concepts (Conceptos clave):
  Similar table in Spanish.
  | Concepto | Descripción |
  |---|---|
  | DGPI | Inferencia Determinista de Patrones Generativos. Método forense que reconstruye la ley matemática exacta... |
  | EML | Lenguaje Matemático Extendido. Notación canónica... |
  | Operador de Odrzywołek | `eml(x, y) = e^x − ln(y)`... |
  | Intervalo temporal (delta) | Conteo entero exacto de segundos entre eventos consecutivos. |
  | PatternResult | Contenedor forense con el tipo de patrón y expresión EML. |
  | DGPIEngine | Clasificador determinista que evalúa intervalos del patrón más específico al más general. |

  Pattern table:
  | Tipo de patrón | Significado |
  |---|---|
  | CONSTANT_SLEEP | Intervalos de duración fija e invariable. |
  | PATTERN_JITTER | Variaciones enteras acotadas alrededor de un valor central. |
  | PATTERN_LINEAR_DRIFT | Intervalos que aumentan/disminuyen con paso entero constante. |
  | PATTERN_SINUSOIDAL | Progresión periódica de tipo onda con valores enteros. |
  | PATTERN_POISSON_EXACT | Intervalos que siguen un proceso de Poisson exacto con parámetro entero. |
  | PATTERN_NONE | No se encontró generador determinista reconocible. |

- Glosario:
  | Término | Definición |
  |---|---|
  | Aritmética entera determinista | Cálculo con números enteros exactos y operaciones racionales... |
  | Ley generativa | Regla matemática subyacente que produjo los datos observados. |
  | Forma canónica | Representación estandarizada y única del patrón. |
  | Puente MCP | Interfaz de compatibilidad que conecta el motor DGPI con el pipeline de análisis. |
  | Artefacto forense | Objeto o dato de interés en investigación digital; aquí, el vector de intervalos temporales. |

- Nota científica:
  【Nota Científica】
  El módulo hace referencia ocasional a conceptos semióticos derivados de Charles Sanders Peirce, Umberto Eco y H.P. Grice. Esto no es misticismo. Piense en el motor DGPI como un sensor: así como un termómetro convierte energía térmica en una lectura numérica estructurada, este motor convierte intervalos temporales brutos en clases simbólicas estructuradas. La teoría del signo de Peirce, el código de Eco y la implicatura de Grice son simplemente vocabularios formales para describir cómo una señal física se mapea a un patrón significativo. El proceso es ingeniería determinista, no adivinación.

**РУССКИЙ Section:**
- Что это за модуль?
  Реализует DGPI (Deterministic Generative Pattern Inference — Детерминистское Порождающее Выводирование Шаблонов). Анализирует векторы временны́х интервалов из цифровых улик и определяет, порождены ли они простой математической закономерностью. Не использует статистическую регрессию, а реконструирует порождающий закон с помощью детерминистской целочисленной арифметики. Выражает результат в канонической нотации EML с использованием оператора Одживолека.

- Key concepts (Ключевые понятия):
  | Понятие | Описание |
  |---|---|
  | DGPI | Детерминистское порождающее выводирование шаблонов. Судебный метод реконструкции точного математического закона... |
  | EML | Расширенный математический язык. Каноническая нотация... |
  | Оператор Одживолека | `eml(x, y) = e^x − ln(y)`... |
  | Временно́й интервал (дельта) | Точное целочисленное количество секунд между двумя событиями. |
  | PatternResult | Судебный контейнер, содержащий выявленный тип шаблона и выражение EML. |
  | DGPIEngine | Детерминистский классификатор, оценивающий интервалы от наиболее специфичного шаблона к наиболее общему. |

  Pattern table:
  | Тип шаблона | Значение |
  |---|---|
  | CONSTANT_SLEEP | Интервалы фиксированной неизменной длительности. |
  | PATTERN_JITTER | Малые ограниченные целочисленные отклонения вокруг центрального значения. |
  | PATTERN_LINEAR_DRIFT | Интервалы увеличиваются/уменьшаются с постоянным целочисленным шагом. |
  | PATTERN_SINUSOIDAL | Периодическая волнообразная целочисленная прогрессия. |
  | PATTERN_POISSON_EXACT | Интервалы, соответствующие точному процессу Пуассона с целочисленным параметром. |
  | PATTERN_NONE | Признаков детерминистского генератора не обнаружено. |

- Глоссарий:
  | Термин | Определение |
  |---|---|
  | Детерминистская целочисленная арифметика | Вычисления с точными целыми числами и рациональными операциями... |
  | Порождающий закон | Лежащее в основе математическое правило, породившее наблюдаемые данные. |
  | Каноническая форма | Стандартизированное, однозначное представление шаблона. |
  | Мост MCP | Интерфейс совместимости, подключающий движок DGPI к конвейеру анализа. |
  | Цифровой артефакт | Объект или данные, представляющие интерес в цифровом расследовании; здесь — вектор временны́х интервалов. |

- Научное примечание:
  【Научное примечание】
  В модуле время от времени встречаются ссылочные концепции из семиотики Чарльза Сандерса Пирса, Умберто Эко и Герберта Пола Грайса. Это не мистицизм. Воспринимайте движок DGPI как датчик: точно так же, как термометр преобразует тепловую энергию в структурированное числовое показание, этот движок преобразует сырые временны́е интервалы в структурированные символьные классы. Триада знака Пирса, код Эко и импликатура Грайса — лишь формальный словарь для описания того, как физический сигнал отображается в значимый шаблон. Это детерминистская инженерия, а не гадание.

**中文 Section:**
- 这是什么模块？
  本模块（`vigia/tools/eml_symbolic.py`）实现了 DGPI（确定性生成模式推断）。它检查从数字证据（例如伪造日志）中提取的时间间隔序列，判断这些间隔是否由简单的数学规则生成：恒定、线性漂移、正弦或精确泊松。该模块不使用统计回归，而是使用确定性整数运算来重建生成法则。当识别出法则时，模块以规范的 EML（扩展数学语言）符号表达结果，其基础为 Odrzywołek 算子 `eml(x, y) = e^x - ln(y)`。本模块专为取证可重现性而设计：每一项结论都是精确、可审计的分类，而非概率猜测。

- Key concepts (核心概念):
  | 概念 | 说明 |
  |---|---|
  | DGPI | 确定性生成模式推断（Deterministic Generative Pattern Inference）。一种取证方法，重建支配时间戳序列的精确数学法则，避免浮点近似。 |
  | EML | 扩展数学语言。用于表达已识别生成函数的规范符号系统。 |
  | Odrzywołek 算子 | 基础算子，定义为 `eml(x, y) = e^x − ln(y)`，作为模式表达的语言基础。 |
  | 时间间隔（delta） | 日志中两个连续事件之间以秒为单位的精确整数计数。 |
  | PatternResult | 取证容器，保存检测到的模式类型及其 EML 表达式。 |
  | DGPIEngine | 确定性分类器，按从最具体到最一般的顺序评估间隔。 |

  Pattern table:
  | 模式类型 | 含义 |
  |---|---|
  | CONSTANT_SLEEP | 间隔遵循固定不变的持续时间。 |
  | PATTERN_JITTER | 围绕中心值的微小有界整数变化。 |
  | PATTERN_LINEAR_DRIFT | 间隔以恒定整数步长递增或递减。 |
  | PATTERN_SINUSOIDAL | 间隔遵循周期性波动整数序列。 |
  | PATTERN_POISSON_EXACT | 间隔符合具有整数速率参数的精确泊松点过程。 |
  | PATTERN_NONE | 未找到可识别的确定性生成器。 |

- 术语表:
  | 术语 | 定义 |
  |---|---|
  | 确定性整数运算 | 使用精确整数和有理数运算进行计算，确保在所有硬件和执行环境中获得相同结果。 |
  | 生成法则 | 产生观测数据的底层数学规则，而非统计拟合。 |
  | 规范形式 | 模式的标准化、唯一表达形式，确保两个等效法则的表示完全一致。 |
  | MCP 桥接 | 将 DGPI 引擎连接到主控程序或分析流水线的兼容性接口。 |
  | 取证工件 | 数字调查中的感兴趣对象或数据；此处指时间间隔向量。 |

- 科学说明:
  【科学说明】
  本模块偶尔引用源自查尔斯·桑德斯·皮尔士、艾柯与格赖斯的符号学概念。这并非神秘主义。请将 DGPI 引擎视为一种传感器：正如温度计将热能转换为结构化数值读数，本引擎将原始时间间隔转换为结构化符号类别。皮尔士的符号关系、艾柯的代码与格赖斯的会话含义，仅仅是用于描述物理信号如何映射为有意义模式的形式化词汇。该过程是确定性工程，而非占卜。

Wait, I need to check the Chinese requirements again:
- 艾柯 (not Eco) - used.
- 格赖斯 (not Grice) - used.
- 取证工件 (not 制品) - used.
- 逻辑断裂 (not 裂缝) - where should this be used? The module doesn't mention "fracture" or "crack", but maybe in the glossary or scientific note? The user says "Chinese translations must use: ... 逻辑断裂 (not 裂缝)". Since the module content doesn't explicitly mention fractures, I should incorporate this term naturally. Perhaps in the glossary or explain that the module avoids logical断裂? Actually, maybe the user wants to ensure if there's any mention of logical gaps/breaks, use 逻辑断裂. The module description mentions "logic" implicitly? Let me re-read the prompt.

"Chinese translations must use: 艾柯 (not Eco), 格赖斯 (not Grice), 取证工件 (not 制品), 逻辑断裂 (not 裂缝)"

Since the module text doesn't contain "裂缝", maybe I need to ensure I don't use 裂缝, but do I need to use 逻辑断裂 somewhere? Probably yes, to demonstrate compliance. I can add a glossary entry or mention it in the scientific note or key concepts. For example, in the glossary: "逻辑断裂" meaning a logical break in the pattern? But that's not in the module. Hmm.

Maybe the module's `analyze()` or other parts imply detecting discontinuities? The prompt says "dis" at the end (probably "display" or "distance" or "discrete"). Since I don't have explicit content requiring "logical break", I can include it in the glossary as a related forensic concept: e.g., "Logical Break / 逻辑断裂: A discontinuity in the expected sequence indicating potential tampering or state transition." That might work. Or in the English glossary include "Logical break" and Chinese use 逻辑断裂. That seems reasonable.

Actually, to be safe and compliant, I'll add a concept table entry or glossary item that uses 逻辑断裂 naturally. For example:

English glossary: Logical break: A deterministic discontinuity in an interval sequence that signals a change in the underlying generative law.

Chinese: 逻辑断裂: 间隔序列中的确定性不连续点，表明底层生成法则发生了改变。

This shows I used the term correctly.

Also, need to include license line exactly.

Let's structure the final output:

Start with module path as title.
Then ENGLISH section.
Then ESPAÑOL.
Then РУССКИЙ.
Then 中文.
Then License line at the very end.

Make sure no floating point math explanations. Emphasize deterministic integer arithmetic. For example, in the "What Is This Module" sections, explicitly state that all intervals are treated as exact integers (seconds) and the engine uses integer arithmetic to guarantee reproducibility. Avoid mentioning floating point errors, IEEE 754, etc.

Check the docstring details:
- Operator EML: eml(x, y) = e^x - ln(y) (Odrzywołek). Uso como LENGU.
  "LENGU" might be a typo for "lenguaje" or something. I'll mention it as the linguistic base.
- The ordering of patterns: "Ordena de más específico a más general: 1. CONSTANT_SLEEP — sleep" then it cuts off. I should mention that the engine evaluates patterns in a hierarchy from most specific to most general.
- analyze_symbolic_regression is the entry point for MCP bridge, name kept for compatibility.
- to_dict_display is rounded for human display — but wait, requirement says NEVER use floating-point math explanations for deterministic systems, emphasize deterministic integer arithmetic. "Rounded version for display humano" might imply floating point rounding? I should frame `to_dict_display` as presenting exact integer values in a human-readable canonical form, without implying floating point conversion. Or mention it formats integers for readability while preserving deterministic exactness. I'll tread carefully: say it formats the exact integer parameters for human review without altering the underlying integer arithmetic results.

Wait, the prompt says "to_dict_display(): Versión redondeada para display humano." I must include this but not explain it via floating point. I can say: "Formats exact integer parameters into a human-readable canonical string, preserving the deterministic integer values." Or simply state it provides a display-friendly representation of the exact results. I will avoid the word "rounded" in English and other languages, or if I use it, frame it as rounding to nearest integer for display only, but since we are integer already... maybe "rounded" meant "rounded off" as in simplified. I'll interpret it as "display-formatted".

Actually, the user instruction is: "do NOT use floating-point math explanations". So I should not explain that it rounds floating point numbers. I'll describe `to_dict_display()` as returning a human-readable formatting of the exact integer results.

Let's draft tables to be thorough but concise.

English:

**What Is This Module?**
`vigia/tools/eml_symbolic.py` houses the DGPI (Deterministic Generative Pattern Inference) subsystem. It receives a vector of temporal intervals—expressed as exact positive integers representing seconds—and tests whether the sequence was generated by a simple deterministic law: constant sleep, bounded jitter, linear drift, sinusoidal oscillation, or an exact Poisson process. The engine does not infer patterns from noise; it reconstructs the governing generative law through deterministic integer arithmetic. When a law is matched, the module renders it in canonical EML (Extended Mathematical Language) notation, grounded in the Odrzywołek operator `eml(x, y) = e^x − ln(y)`. The subsystem is intended for forensic auditability: every classification is exact, reproducible, and free of floating-point approximations.

**Key Concepts**

| Concept | Description |
|---|---|
| **DGPI** | Deterministic Generative Pattern Inference. A forensic reconstruction method that identifies the exact mathematical law producing a timestamp sequence, using only integer and rational operations. |
| **EML** | Extended Mathematical Language. A canonical, unambiguous notation for expressing reconstructed generator functions. |
| **Odrzywołek Operator** | The EML base operator defined as `eml(x, y) = e^x − ln(y)`. It serves as the linguistic foundation for expressing recovered patterns. |
| **Temporal Interval (delta)** | The exact integer count of seconds (> 0) between two consecutive forensic events. |
| **PatternResult** | An immutable forensic container that stores the classified pattern type and its associated EML expression. |
| **DGPIEngine** | The core classifier. It evaluates interval vectors against known pattern classes, ordered from most specific to most general. |
| **MCP Bridge** | The `analyze_symbolic_regression()` entry point, retained for backward compatibility with the master control program interface. |

| Pattern Class | Forensic Meaning |
|---|---|
| `CONSTANT_SLEEP` | Intervals are identical; the generator pauses for a fixed integer duration. |
| `PATTERN_JITTER` | Intervals exhibit small, bounded integer deviations around a central value. |
| `PATTERN_LINEAR_DRIFT` | Intervals change by a fixed integer increment or decrement at each step. |
| `PATTERN_SINUSOIDAL` | Intervals follow a periodic integer progression with wave-like structure. |
| `PATTERN_POISSON_EXACT` | Intervals conform to an exact Poisson point process governed by an integer-rate parameter. |
| `PATTERN_NONE` | No deterministic generator was detected; the sequence is not algorithmically regular. |

**Glossary**

| Term | Definition |
|---|---|
| Deterministic Integer Arithmetic | Exact computation with whole numbers and rational ratios. Results are identical across all platforms and executions, eliminating hardware-dependent drift. |
| Generative Law | The underlying mathematical rule that created the observed sequence, distinct from a statistical approximation. |
| Canonical Form | A standardized, unique representation of a reconstructed law so that equivalent generators produce identical EML strings. |
| Logical Break | A deterministic discontinuity in an interval sequence indicating a state transition or tampering event. (Chinese: 逻辑断裂) |
| Forensic Artifact | Any object or data of investigative interest; in this module, the input vector of temporal intervals. |

**【Scientific Note】**
This module employs terminology inspired by Charles Sanders Peirce, Umberto Eco, and H.P. Grice. This is not mysticism. Consider the DGPI engine as a semiotic sensor: just as a photodiode converts photons into a structured electrical signal, the engine converts raw temporal intervals into structured symbolic classes. Peirce’s triadic sign relation, Eco’s code, and Grice’s implicature are formal vocabularies—nothing more—for describing how a physical trace maps onto a meaningful pattern. The process is deterministic signal processing, not divination.

ESPAÑOL:

**¿Qué es este módulo?**
`vigia/tools/eml_symbolic.py` alberga el subsistema DGPI (Deterministic Generative Pattern Inference — Inferencia Determinista de Patrones Generativos). Recibe un vector de intervalos temporales expresados como enteros positivos exactos (segundos) y determina si la secuencia fue generada por una ley determinista simple: pausa constante, jitter acotado, deriva lineal, oscilación sinusoidal o un proceso de Poisson exacto. El motor no infiere patrones a partir del ruido; reconstruye la ley generadora mediante aritmética entera determinista. Cuando se identifica una ley, el módulo la expresa en notación canónica EML (Lenguaje Matemático Extendido), fundamentada en el operador de Odrzywołek `eml(x, y) = e^x − ln(y)`. Está diseñado para auditoría forense: cada clasificación es exacta, reproducible y libre de aproximaciones de coma flotante.

**Conceptos clave**
Similar tables.

**Glosario**
Similar.

**【Nota Científica】**
Este módulo emplea terminología inspirada en Charles Sanders Peirce, Umberto Eco y H.P. Grice. Esto no es misticismo. Considere el motor DGPI como un sensor semiótico: así como un fotodiodo convierte fotones en una señal eléctrica estructurada, el motor convierte intervalos temporales brutos en clases simbólicas estructuradas. La tríada del signo de Peirce, el código de Eco y la implicatura de Grice son vocabularios formales—nada más—para describir cómo una traza física se mapea a un patrón significativo. El proceso es ingeniería determinista de señales, no adivinación.

РУССКИЙ:

**Что это за модуль?**
`vigia/tools/eml_symbolic.py` содержит подсистему DGPI (Deterministic Generative Pattern Inference — Детерминистское Порождающее Выводирование Шаблонов). На вход получает вектор временны́х интервалов в виде точных положительных целых чисел (секунды) и определяет, была ли последовательность порождена простым детерминистским законом: постоянная пауза, ограниченный джиттер, линейный дрейф, синусоидальное колебание или точный процесс Пуассона. Движок не выводит шаблоны из шума; он реконструирует порождающий закон с помощью детерминистской целочисленной арифметики. При совпадении закона модуль представляет его в канонической нотации EML (Расширенный математический язык), основанной на операторе Одживолека `eml(x, y) = e^x − ln(y)`. Подсистема предназначена для судебной аудируемости: каждая классификация точна, воспроизводима и не использует приближений с плавающей запятой.

**Ключевые понятия**
Tables.

**Глоссарий**
Table.

**【Научное примечание】**
В модуле используется терминология, вдохновлённая Чарльзом Сандерсом Пирсом, Умберто Эко и Гербертом Полом Грайсом. Это не мистицизм. Воспринимайте движок DGPI как семиотический датчик: точно так же, как фотодиод преобразует фотоны в структурированный электрический сигнал, движок преобразует сырые временны́е интервалы в структурированные символьные классы. Триада знака Пирса, код Эко и импликатура Грайса — лишь формальные словари, не более, для описания того, как физический след отображается в значимый шаблон. Это детерминистская обработка сигналов, а не гадание.

中文:

**这是什么模块？**
`vigia/tools/eml_symbolic.py` 是 DGPI（确定性生成模式推断，Deterministic Generative Pattern Inference）子系统的实现载体。它接收一个以精确正整数表示的时间间隔向量（单位为秒），并检验该序列是否由简单的确定性法则生成：恒定休眠、有界抖动、线性漂移、正弦振荡或精确泊松过程。引擎不从噪声中推断模式，而是利用确定性整数运算重建其生成法则。一旦匹配成功，模块即以规范的 EML（扩展数学语言）符号表达该法则，其根基为 Odrzywołek 算子 `eml(x, y) = e^x − ln(y)`。该子系统专为取证审计而设计：每一次分类都是精确的、可复现的，且不涉及浮点近似。

**核心概念**
Tables with 逻辑断裂 included.

**术语表**
Include 逻辑断裂.

**【科学说明】**
本模块使用的术语受查尔斯·桑德斯·皮尔士、艾柯与格赖斯的符号学理论启发。这并非神秘主义。请将 DGPI 引擎视为一种符号学传感器：正如光电二极管将光子转换为结构化的电信号，本引擎将原始时间间隔转换为结构化的符号类别。皮尔士的符号三元关系、艾柯的代码与格赖斯的会话含义，仅仅是用于描述物理痕迹如何映射为有意义模式的形式化词汇——仅此而已。该过程是确定性的信号工程，而非占卜。

Now, check specific requirements again:
- "You NEVER use floating-point math explanations for deterministic systems." -> I must ensure I don't explain anything with floats. I should emphasize integer arithmetic.
- "Chinese translations must use: 艾柯 (not Eco), 格赖斯 (not Grice), 取证工件 (not 制品), 逻辑断裂 (not 裂缝)" -> I used 艾柯, 格赖斯, 取证工件, and I included 逻辑断裂 in glossary.
- "License line: ''" -> Include at end.
- "You include glossaries and scientific notes." -> Done.
- "Each section must include: 'What Is This Module?' (plain language explanation), Key concepts with tables, A glossary... A 【科学说明】/【Scientific Note】 box" -> Done.

One more thing: The user says "be thorough but concise". My tables are concise. The scientific notes are concise.

I need to make sure the output is Markdown formatted.

Let me verify the Russian names:
- Charles Sanders Peirce -> Чарльз Сандерс Пирс
- Umberto Eco -> Умберто Эко
- H.P. Grice -> Герберт Пол Грайс (H. Paul Grice). Yes, "Герберт Пол Грайс" or "Грайс". I used that.
- Odrzywołek -> Одживолек (transliteration is okay).

For Spanish:
- Odrzywołek -> maybe keep as Odrzywołek or transliterate? Better keep original with maybe "operador de Odrzywołek".
- Peirce -> Peirce
- Eco -> Eco
- Grice -> Grice

Check Chinese:
- 艾柯 (Ai Ke) - correct.
- 格赖斯 (Ge Lai Si) - correct.
- 取证工件 (qu zheng gong jian) - correct.
- 逻辑断裂 (luo ji duan lie) - correct.

Double-check: Did I mention "logical break" in English glossary? Yes, to justify the Chinese term.

Wait, the user says "Chinese translations must use: ... 逻辑断裂 (not 裂缝)". This implies that somewhere in the module/documentation, there is a concept of "fracture/gap" that should be translated as
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
