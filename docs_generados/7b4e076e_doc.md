<!--
VIGIA Academic Documentation
Module: 7b4e076e
Batch ID: vigia-doc-0100-7b4e076e
Generated: 2026-05-20T14:56:47.866285+00:00
-->

The user wants technical documentation for a Python module `vigia/inference/check_determinism.py`. The target audience is scientists/researchers who do NOT know Python. It must be in Markdown with 4 language sections: ENGLISH, ESPAÑOL, РУССКИЙ, 中文.

Key requirements:
1. 4 language sections.
2. Each section must include:
   - "What Is This Module?" (plain language explanation)
   - Key concepts with tables
   - A glossary of technical terms
   - A 【科学说明】/【Scientific Note】 box explaining that Peirce/Eco/Grice terminology is NOT mysticism — use the sensor analogy
3. Chinese translations must use: 艾柯 (not Eco), 格赖斯 (not Grice), 取证工件 (not 制品), 逻辑断裂 (not 裂缝)
4. 
5. Do NOT use floating-point math explanations — emphasize deterministic integer arithmetic where applicable
6. Be thorough but concise.
7. Module details:
   - Path: vigia/inference/check_determinism.py
   - Docstring: check_determinism.py — VIGIA Determinism Verification Script
   - Runs same analysis N times on same evidence file, compares SHA-256 hashes of generated reports. If hashes diverge, alerts about non-determinism.
   - Critical for forensic admissibility.
   - Usage: python3 check_determinism.py [evidence_file] [--runs N] [--tool TOOL]
   - Exit codes: 0 — All runs pro... (truncated, likely 0 = success/pass, non-zero = fail)
   - Functions: main()
   - Constants & Config: VOLATILE_KEYS, STABLE_TOOLS, BRIDGE_TOOLS, _BRIDGE_CANDIDATES

Since the user is a scientist audience who doesn't know Python, I need to explain the module's purpose in scientific/forensic terms, not code terms.

Structure for each language:
- Header with module path and docstring summary.
- "What Is This Module?" section.
- Key Concepts with tables (e.g., Determinism, SHA-256, Volatile Keys, Stable/Bridge Tools, Evidence File, Forensic Admissibility).
- Glossary.
- Scientific Note box about Peirce/Eco/Grice terminology not being mysticism, using sensor analogy. (Peirce = semiotics, Eco = semiotics, Grice = cooperative principle/implicature). The module name is VIGIA, which sounds like it might relate to semiotics (Umberto Eco, Charles Sanders Peirce, H.P. Grice). The scientific note must clarify that terms borrowed from semiotics/philosophy of language are formal abstractions, like calling a sensor a "witness" — it's an analogy, not mysticism. Use sensor analogy.
- License line at the end.

I need to be careful with the Chinese terms:
- 艾柯 (Umberto Eco)
- 格赖斯 (H.P. Grice)
- 取证工件 (forensic artifact)
- 逻辑断裂 (logical fracture/discontinuity) instead of 裂缝.

Also, NO floating-point math explanations. Emphasize deterministic integer arithmetic where applicable. The module uses SHA-256, which operates on integer arithmetic (bitwise operations on fixed-width binary data). I should describe SHA-256 in terms of deterministic integer arithmetic, not floating point.

Let's draft the ENGLISH version first.

**ENGLISH:**

*Module Path:* `vigia/inference/check_determinism.py`

*What Is This Module?*
This script is a forensic quality-control instrument. Its sole purpose is to verify whether an analytical tool produces *exactly* the same output every time it examines the same digital evidence. In scientific terms, it tests for **determinism**: the property that a fixed input, processed by a fixed method, must yield a fixed output. The script runs the analysis repeatedly, then mathematically fingerprints each result using SHA-256 (a deterministic integer-based hashing algorithm). If any fingerprint differs, the tool is flagged as non-deterministic, making its results unreliable for court admissibility.

*Key Concepts Table:*

| Concept | Plain-Language Definition | Role in This Module |
|---|---|---|
| Determinism | The guarantee that identical inputs always produce identical outputs, with no hidden randomness or time-dependent variation. | Core property being verified. |
| SHA-256 | A cryptographic hash function that computes a fixed-length, deterministic integer fingerprint from a data file. | Used to compare reports; any change in output changes the fingerprint. |
| Evidence File | The digital object under investigation (e.g., a disk image, log, or network capture). | The fixed input for the repeated experiment. |
| Volatile Keys | Metadata fields that change between runs (e.g., timestamps, temporary file paths) and must be excluded from comparison. | Stripped before hashing so that only meaningful content is compared. |
| Stable Tools | Analytical methods that are expected to be deterministic and produce identical results on every run. | The tools being tested by this script. |
| Bridge Tools | Intermediate processing components that translate data between formats or systems. | Must also be deterministic, or they introduce logical fractures in the chain of custody. |
| Forensic Admissibility | The legal and scientific standard requiring that analytical methods are repeatable and verifiable by third parties. | The ultimate goal of the verification. |

*Glossary:*
- **Determinism**: In computing, a system where the output is entirely dictated by the input and the algorithm, with no stochastic (random) elements.
- **Hash / Fingerprint**: A compact, deterministic integer representation of a larger data object. Even a single-bit change in the input produces a completely different hash.
- **Non-determinism**: Any behavior causing the same input to yield different outputs across runs, often due to hidden state, race conditions, or floating-point approximations (the latter being irrelevant here as the system uses integer arithmetic).
- **Chain of Custody**: The documented, unbroken trail of evidence handling. Non-determinism creates a logical break in this chain.
- **Integer Arithmetic**: Mathematical operations on whole numbers with exact precision, as opposed to floating-point approximations. SHA-256 relies exclusively on bitwise integer operations.

*【Scientific Note】*
VIGIA borrows terminology from semiotics—Charles Sanders Peirce, Umberto Eco, and H.P. Grice—to describe information structures. These terms are **formal abstractions**, not mysticism. Think of them like the word "witness" in sensor design: a physical sensor does not have consciousness, yet we call it a "witness" to an event because it records data. Similarly, Peirce's *sign*, Eco's *code*, and Grice's *maxims* are analytical lenses used to classify how digital evidence carries meaning. They provide a rigorous logical framework; they do not invoke supernatural agency. When this module checks for determinism, it is ensuring that the "sensor" (the analytical tool) records the same "testimony" (the report) every time, under identical conditions.

*License:* 

---

**ESPAÑOL:**

*Ruta del módulo:* `vigia/inference/check_determinism.py`

*¿Qué es este módulo?*
Este script es un instrumento de control de calidad forense. Su único propósito es verificar si una herramienta analítica produce *exactamente* el mismo resultado cada vez que examina la misma evidencia digital. En términos científicos, prueba el **determinismo**: la propiedad por la cual una entrada fija, procesada por un método fijo, debe producir una salida fija. El script ejecuta el análisis repetidamente y luego calcula una huella digital matemática de cada resultado mediante SHA-256 (un algoritmo de hash determinista basado en aritmética entera). Si alguna huella difiere, la herramienta se marca como no determinista, haciendo que sus resultados sean poco fiables para la admisibilidad judicial.

*Conceptos clave:*

| Concepto | Definición en lenguaje sencillo | Rol en este módulo |
|---|---|---|
| Determinismo | La garantía de que entradas idénticas siempre producen salidas idénticas, sin aleatoriedad oculta ni variación temporal. | Propiedad fundamental que se verifica. |
| SHA-256 | Una función hash criptográfica que calcula una huella digital entera, de longitud fija y determinista, a partir de un archivo de datos. | Se usa para comparar informes; cualquier cambio en la salida altera la huella. |
| Archivo de evidencia | El objeto digital bajo investigación (p. ej., imagen de disco, registro o captura de red). | La entrada fija para el experimento repetido. |
| Claves volátiles | Campos de metadatos que cambian entre ejecuciones (p. ej., marcas de tiempo, rutas temporales) y deben excluirse de la comparación. | Se eliminan antes del hash para comparar solo el contenido significativo. |
| Herramientas estables | Métodos analíticos que se espera sean deterministas y produzcan resultados idénticos en cada ejecución. | Las herramientas que este script prueba. |
| Herramientas puente | Componentes de procesamiento intermedio que traducen datos entre formatos o sistemas. | También deben ser deterministas; de lo contrario, introducen fracturas lógicas en la cadena de custodia. |
| Admisibilidad forense | El estándar legal y científico que exige que los métodos analíticos sean repetibles y verificables por terceros. | El objetivo último de la verificación. |

*Glosario:*
- **Determinismo**: En informática, un sistema donde la salida está dictada enteramente por la entrada y el algoritmo, sin elementos estocásticos (aleatorios).
- **Hash / Huella digital**: Una representación entera, compacta y determinista de un objeto de datos más grande. Incluso un cambio de un solo bit en la entrada produce un hash completamente diferente.
- **No determinismo**: Cualquier comportamiento que hace que la misma entrada produzca diferentes salidas entre ejecuciones, a menudo debido a estado oculto, condiciones de carrera o aproximaciones de punto flotante (estas últimas no son relevantes aquí, ya que el sistema usa aritmética entera).
- **Cadena de custodia**: El rastro documentado e ininterrumpido del manejo de evidencia. El no determinismo crea una ruptura lógica en esta cadena.
- **Aritmética entera**: Operaciones matemáticas sobre números enteros con precisión exacta, en contraste con las aproximaciones de punto flotante. SHA-256 se basa exclusivamente en operaciones bit a bit con enteros.

*【Nota Científica】*
VIGIA toma prestada terminología de la semiótica—Charles Sanders Peirce, Umberto Eco y H.P. Grice—para describir estructuras de información. Estos términos son **abstracciones formales**, no misticismo. Piense en ellos como la palabra "testigo" en el diseño de sensores: un sensor físico no tiene conciencia, sin embargo lo llamamos "testigo" de un evento porque registra datos. Del mismo modo, el *signo* de Peirce, el *código* de Eco y los *máximas* de Grice son lentes analíticos usados para clasificar cómo la evidencia digital porta significado. Proporcionan un marco lógico riguroso; no invocan agencia sobrenatural. Cuando este módulo verifica el determinismo, está asegurando que el "sensor" (la herramienta analítica) registre el mismo "testimonio" (el informe) cada vez, bajo condiciones idénticas.

*Licencia:* 

---

**РУССКИЙ:**

*Путь к модулю:* `vigia/inference/check_determinism.py`

*Что это за модуль?*
Этот скрипт — инструмент судебного контроля качества. Его единственная цель — проверить, производит ли аналитический инструмент *точно* тот же результат при каждом исследовании одних и тех же цифровых доказательств. Научными терминами, он проверяет **детерминизм**: свойство, при котором фиксированный вход, обработанный фиксированным методом, даёт фиксированный выход. Скрипт многократно запускает анализ, затем математически «снимает отпечатки» каждого результата с помощью SHA-256 (детерминированного хеш-алгоритма на основе целочисленной арифметики). Если какой-либо отпечаток отличается, инструмент помечается как недетерминированный, а его результаты признаются ненадёжными для судебного допуска.

*Ключевые понятия:*

| Понятие | Определение простым языком | Роль в модуле |
|---|---|---|
| Детерминизм | Гарантия, что идентичные входные данные всегда дают идентичный результат, без скрытой случайности или временных вариаций. | Основное проверяемое свойство. |
| SHA-256 | Криптографическая хеш-функция, вычисляющая фиксированную детерминированную целочисленную метку (отпечаток) файла данных. | Используется для сравнения отчётов; любое изменение выходных данных меняет метку. |
| Файл доказательств | Цифровой объект под investigation (например, образ диска, журнал или сетевой дамп). | Фиксированный вход для повторяющегося эксперимента. |
| Летучие ключи | Поля метаданных, меняющиеся между запусками (например, временные метки, пути к временным файлам), которые необходимо исключить из сравнения. | Удаляются перед хешированием, чтобы сравнивать только значимое содержимое. |
| Стабильные инструменты | Аналитические методы, которые по определению должны быть детерминированными и давать одинаковые результаты при каждом запуске. | Инструменты, проверяемые данным скриптом. |
| Мостовые инструменты | Промежуточные компоненты обработки, переводящие данные между форматами или системами. | Также должны быть детерминированными; иначе они вносят логические разрывы в цепочку сохранности. |
| Судебная допустимость | Правовой и научный стандарт, требующий, чтобы аналитические методы были воспроизводимы и верифицируемы третьими сторонами. | Конечная цель проверки. |

*Глоссарий:*
- **Детерминизм**: В вычислительной технике — система, в которой выход полностью определяется входом и алгоритмом, без стохастических (случайных) элементов.
- **Хеш / Отпечаток**: Компактная детерминированная целочисленная репрезентация большего объекта данных. Даже изменение одного бита во входных данных даёт совершенно другой хеш.
- **Недетерминизм**: Любое поведение, приводящее к тому, что одинаковый вход даёт разные выходы в разных запусках, часто из-за скрытого состояния, состояний гонки или операций с плавающей точкой (последние здесь неактуальны, так как система использует целочисленную арифметику).
- **Цепочка сохранности**: Документированный непрерывный след обращения с доказательствами. Недетерминизм создаёт логический разрыв в этой цепи.
- **Целочисленная арифметика**: Математические операции над целыми числами с точной точностью, в отличие от приближений с плавающей точкой. SHA-256 полностью основан на побитовых целочисленных операциях.

*【Научное Примечание】*
VIGIA заимствует терминологию из семиотики — Чарльза Сандерса Пирса, Умберто Эко и Г. П. Грайса — для описания информационных структур. Эти термины являются **формальными абстракциями**, а не мистицизмом. Вспомните аналогию со словом «свидетель» в проектировании датчиков: физический датчик не обладает сознанием, тем не менее мы называем его «свидетелем» события, потому что он регистрирует данные. Аналогично, *знак* Пирса, *код* Эко и *максимы* Грайса — это аналитические линзы, используемые для классификации того, как цифровые доказательства несут смысл. Они обеспечивают строгую логическую рамку; они не апеллируют к сверхъестественному. Когда этот модуль проверяет детерминизм, он гарантирует, что «датчик» (аналитический инструмент) фиксирует одно и то же «показание» (отчёт) каждый раз при идентичных условиях.

*Лицензия:* 

---

**中文:**

*模块路径:* `vigia/inference/check_determinism.py`

*What Is This Module?* -> should be "这是什么模块？" or similar. The user said "Each section must include: 'What Is This Module?' (plain language explanation)". I can keep the heading in English or translate it? The user said "Each section must include: 'What Is This Module?'". This could mean the section heading should be that exact string, but since the whole document is in 4 languages, it makes sense to translate the heading while keeping the content structure. However, to be safe and clear, I'll translate the heading to the respective language.

Chinese heading: 这是什么模块？ (What is this module?)

*这是什么模块？*
本脚本是一种取证质量控制仪器。其唯一目的是验证：当同一分析工具每次检查相同的数字证据时，是否产生*完全*相同的结果。用科学术语来说，它检验的是**确定性**：固定输入经由固定方法处理，必须产生固定输出的特性。该脚本重复运行分析，随后使用 SHA-256（一种基于确定性整数运算的哈希算法）为每次结果计算数学指纹。若任何指纹出现差异，则该工具被标记为非确定性，其结果在司法可采性方面将不可靠。

*Key concepts with tables:*

| 概念 | 通俗定义 | 在本模块中的作用 |
|---|---|---|
| 确定性 | 保证相同输入始终产生相同输出，不存在隐藏随机性或时间相关变异。 | 被验证的核心属性。 |
| SHA-256 | 一种密码学哈希函数，从数据文件计算出固定长度、确定性的整数指纹。 | 用于比较报告；输出有任何变化，指纹即改变。 |
| 证据文件 | 受调查的数字对象（例如磁盘镜像、日志或网络捕获）。 | 重复实验的固定输入。 |
| 易变键 (Volatile Keys) | 在多次运行之间会发生变化的元数据字段（如时间戳、临时文件路径），必须在比较前排除。 | 在哈希计算前被剥离，确保仅比较有意义的实质内容。 |
| 稳定工具 (Stable Tools) | 预期具有确定性、每次运行都产生相同结果的分析方法。 | 本脚本所测试的工具。 |
| 桥接工具 (Bridge Tools) | 在不同格式或系统之间转换数据的中间处理组件。 | 也必须具有确定性，否则将在保管链条中引入逻辑断裂。 |
| 取证可采性 | 要求分析方法可被第三方重复与验证的法律及科学标准。 | 验证的最终目标。 |

Wait, the user specified Chinese translations must use:
- 艾柯 (not Eco)
- 格赖斯 (not Grice)
- 取证工件 (not 制品)
- 逻辑断裂 (not 裂缝)

So I should use 逻辑断裂 in the table for bridge tools. And maybe introduce 取证工件 somewhere appropriate. Perhaps in the glossary or main text. Let's make sure to use it. For example, "取证工件" can be used to describe the generated reports or evidence files. "生成的取证工件（报告）" or similar.

Let's refine the Chinese table and text.

In the main text, maybe: "该脚本重复运行分析，随后使用 SHA-256 为每次生成的取证工件（报告）计算数学指纹..."

And for bridge tools: "否则将在保管链中引入逻辑断裂。"

Glossary should include these terms.

*术语表 (Glossary):*
- **确定性**: 在计算领域中，指系统的输出完全由输入和算法决定，不含任何随机（随机性）因素。
- **哈希 / 指纹**: 对较大数据对象的紧凑、确定性整数表征。即使输入仅改变一个二进制位，哈希结果也会完全不同。
- **非确定性**: 导致相同输入在不同运行中产生不同输出的任何行为，通常由隐藏状态、竞争条件或浮点运算近似引起（后者在此不适用，因为本系统采用整数运算）。
- **保管链**: 对证据处理过程的、有文件记录的、不间断的追踪。非确定性会在该链条中造成逻辑断裂。
- **整数运算**: 对整数进行的数学操作，具有精确精度，与浮点近似相对。SHA-256 完全依赖于按位整数运算。
- **取证工件**: 在数字取证过程中生成或采集的任何对象（如报告、镜像、日志），可作为证据或分析产物。
- **逻辑断裂**: 指论证、数据流或保管链中的不连续或断裂，使得结论无法被严格复现或追踪。

*【科学说明】*
VIGIA 借用符号学领域的术语——查尔斯·桑德斯·皮尔士（Charles Sanders Peirce）、**艾柯**（Umberto Eco）与**格赖斯**（H.P. Grice）——来描述信息结构。这些术语是**形式化抽象**，而非神秘主义。不妨借用传感器类比来理解：物理传感器并不具备意识，但我们在工程中会称其为事件的“见证者”，因为它记录了数据。同理，皮尔士的“符号”、艾柯的“代码”以及格赖斯的“准则”都是分析透镜，用于分类数字证据如何承载意义。它们提供的是严密的逻辑框架，并不诉诸超自然力量。当本模块检验确定性时，它实际上是在确保“传感器”（分析工具）在相同条件下每次都能记录下相同的“证词”（报告）。

*许可协议:* 

---

Now let's review all constraints:
1. Target audience: scientists who do not know Python. Yes, no Python code, plain language, scientific/forensic framing.
2. Format: Markdown with 4 language sections. Yes.
3. Each section includes:
   - "What Is This Module?" -> I'll use translated headings but maintain the section.
   - Key concepts with tables. Yes.
   - Glossary. Yes.
   - Scientific Note box with Peirce/Eco/Grice not mysticism, sensor analogy. Yes.
4. Chinese translations: 艾柯, 格赖斯, 取证工件, 逻辑断裂. Yes, included.
5. License line included. Yes.
6. No floating-point math explanations; emphasize deterministic integer arithmetic. Yes, explicitly mentioned SHA-256 uses integer arithmetic, not floating point.
7. Thorough but concise. Will try to keep it tight.

One thing: The user provided module details like FUNCTIONS: main(), CONSTANTS: VOLATILE_KEYS, STABLE_TOOLS, BRIDGE_TOOLS, _BRIDGE_CANDIDATES. I should make sure these are explained in the key concepts or glossary. I did for most except _BRIDGE_CANDIDATES. I should add it.

_BRIDGE_CANDIDATES: Potential bridge tools being evaluated for inclusion in the deterministic pipeline.

Let's add to tables/glossary in each language.

ENGLISH:
Add to table or glossary: `_BRIDGE_CANDIDATES` -> Maybe in glossary since it's an internal constant.
**Bridge Candidates**: Provisional intermediate tools under evaluation for stability before being granted full status in the deterministic pipeline.

ESPAÑOL:
**Candidatos a puente**: Herramientas intermedias provisionales en evaluación de estabilidad antes de obtener el estado completo en la tubería determinista.

РУССКИЙ:
**Кандидаты в мостовые инструменты**: Промежуточные инструменты на стадии оценки стабильности перед включением в детерминированный конвейер.

中文:
**桥接候选工具 (_BRIDGE_CANDIDATES)**: 在获得确定性流程正式地位之前，正在接受稳定性评估的临时中间组件。

Also, the docstring says "Exit codes: 0 — All runs pro". I should mention exit codes briefly. I can add a row in the table or mention in the text.

Let's add to "What Is This Module?" or a separate small table. Since the user lists it, I should cover it.

| Exit Code | Meaning |
|---|---|
| 0 | All runs produced identical hashes; the tool is deterministic. |
| Non-zero | Hash mismatch detected; non-determinism found. |

I'll add this to the key concepts table in each language.

Now, compiling the final output.

I need to ensure the markdown is clean. Use headers.

Structure:
# Module Documentation: `vigia/inference/check_determinism.py`

## ENGLISH

### What Is This Module?
...

### Key Concepts

| ... |
| ... |

### Glossary
...

### 【Scientific Note】
...



---

## ESPAÑOL

### ¿Qué es este módulo?
...

### Conceptos clave
...

### Glosario
...

### 【Nota Científica】
...



---

## РУССКИЙ

### Что это за модуль?
...

### Ключевые понятия
...

### Глоссарий
...

### 【Научное Примечание】
...



---

## 中文

### 这是什么模块？
...

### 核心概念

| ... |
| ... |

### 术语表
...

### 【科学说明】
...



---

Let me double check the Chinese terms again.
- 艾柯: used in scientific note. Yes.
- 格赖斯: used in scientific note. Yes.
- 取证工件: used in glossary and text. Yes.
- 逻辑断裂: used in table and glossary. Yes.

Also, the user says "Do NOT use floating-point math explanations — emphasize deterministic integer arithmetic where applicable". I have explicitly stated in EN: "non-determinism... floating-point approximations (the latter being irrelevant here as the system uses integer arithmetic)." And in the SHA-256 description: "deterministic integer-based hashing algorithm". This is good.

One final check on the scientific note sensor analogy. I used the word "witness" for sensor. That's a good analogy. I explicitly said they are formal abstractions, not mysticism. Good.

I should ensure I don't use any Python code examples, since the audience doesn't know Python. The user said "Generate documentation for the following Python module... for scientists who do NOT know Python". I will not include code blocks or Python syntax beyond the module path.

Let me refine the ENGLISH scientific note to make sure it's punchy and clear.

"VIGIA borrows terminology from semiotics—Charles Sanders Peirce, Umberto Eco, and H.P. Grice—to describe information structures. These terms are formal abstractions, not mysticism. Consider the sensor analogy: in engineering, we call a physical sensor a 'witness' to an event even though it lacks consciousness; it simply records data. Likewise, Peirce's sign, Eco's code, and Grice's maxims are analytical lenses for classifying how digital evidence carries meaning. They provide a rigorous logical framework; they do not invoke supernatural agency. When this module checks for determinism, it is ensuring that the 'sensor' (the analytical tool) records the same 'testimony' (the report) every time under identical conditions."

That's good.

For the exit code table in EN:
| Exit Code | Meaning |
|---|---|
| 0 | All runs produced identical SHA-256 hashes; the pipeline is deterministic. |
| Non-zero | A hash mismatch occurred, signaling non-determinism in the tool or pipeline. |

I'll integrate this into the Key Concepts table or as a separate small table. I'll make it part of the Key Concepts table to keep it concise.

Actually, a separate table might be better for readability. I'll do two tables: one for general concepts, one for script outputs. Or one big table. A big table might be too wide. Let's do two.

**Table 1: Forensic Concepts**
...
**Table 2: Script Outputs & Constants**
| Label | Meaning |
|---|---|
| Exit code 0 | Success: all runs yielded identical hashes. |
| Exit code non-zero | Failure: non-determinism detected. |
| VOLATILE_KEYS | Metadata fields excluded from comparison. |
| STABLE_TOOLS | Methods expected to be deterministic. |
| BRIDGE_TOOLS | Approved intermediate data translators. |
| _BRIDGE_CANDIDATES | Provisional tools awaiting stability verification. |

This covers all constants. I will do this for each language.

Let's write it out carefully.

**ENGLISH:**

#### Key Concepts

**Operational Outputs and Configuration**

| Label | Plain-Language Definition | Scientific Role |
|---|---|---|
| Exit code 0 | The script finishes and reports that all repeated analyses produced identical fingerprints. | Signals that the tool is deterministic and forensically admissible. |
| Non-zero exit | The script finishes and reports that at least one fingerprint differed across runs. | Signals non-determinism; the pipeline requires inspection before legal use. |
| VOLATILE_KEYS | Metadata fields that legitimately change between runs, such as timestamps or temporary paths. | Stripped from reports before hashing so they do not trigger false mismatches. |
| STABLE_TOOLS | Analytical methods engineered to produce bit-for-bit identical results on every execution. | The baseline tools whose determinism is being verified. |
| BRIDGE_TOOLS | Intermediate components that convert data between formats without altering meaning. | Must be deterministic; otherwise they introduce logical discontinuities in evidence handling. |
| _BRIDGE_CANDIDATES | New or modified intermediate tools currently under evaluation for stability. | Audited before promotion to full BRIDGE_TOOLS status to prevent non-determinism. |

**Determinism and Measurement**

| Concept | Plain-Language Definition | Scientific Role |
|---|---|---|
| Determinism | The property that a fixed input and fixed procedure always yield the same output. | The fundamental requirement for reproducible forensic science. |
| SHA-256 | A cryptographic hash function relying exclusively on deterministic integer arithmetic to produce a fixed-length fingerprint. | Provides an exact, computationally cheap method to detect even single-bit changes in output. |
| Evidence File | The digital object under investigation (disk image, log, packet capture, etc.). | The constant experimental input. |
| Forensic Admissibility | The standard that analytical methods must be repeatable and verifiable by independent parties. | The legal-scientific objective of the verification. |

#### Glossary
- **Determinism**: A system state in which output is entirely predicted by input and algorithm, free of random variation.
- **SHA-256 Hash**: A deterministic integer fingerprint of a data object. Any alteration, however minor, produces a completely different hash value.
- **Non-determinism**: Behavior causing identical inputs to yield different outputs across runs, typically from hidden state, concurrency, or non-integer approximations (the latter excluded here by design).
- **Chain of Custody**: The documented, unbroken lineage of evidence handling. Non-determinism constitutes a logical breach in this chain.
- **Integer Arithmetic**: Exact mathematical operations on whole numbers, without the rounding errors inherent to floating-point representation. SHA-256 is built entirely upon bitwise integer operations.
- **Volatile Key**: A metadata attribute that changes between experimental trials and must be neutralized to avoid false conclusions.
- **Bridge Candidate**: A provisional processing component undergoing stability trials before full operational acceptance.

#### 【Scientific Note】
...

This looks solid. I'll adapt this structure to all languages.

**ESPAÑOL:**

#### Conceptos clave

**Salidas y configuración operativas**

| Etiqueta | Definición en lenguaje sencillo | Rol científico |
|---|---|---|
| Código de salida 0 | El script termina e informa que todos los análisis repetidos produjeron huellas digitales idénticas. | Señala que la herramienta es determinista y forensemente admisible. |
| Salida distinta de cero | El script termina e informa que al menos una huella difirió entre ejecuciones. | Señala no determinismo; la tubería requiere inspección antes de su uso legal. |
| VOLATILE_KEYS | Campos de metadatos que cambian legítimamente entre ejecuciones, como marcas de tiempo o rutas temporales. | Se eliminan de los informes antes del hash para evitar falsas discrepancias. |
| STABLE_TOOLS | Métodos analíticos diseñados para producir resultados idénticos bit a bit en cada ejecución. | Herramientas base cuyo determinismo se verifica. |
| BRIDGE_TOOLS | Componentes intermedios que convierten datos entre formatos sin alterar el significado. | Deben ser deterministas; de lo contrario, introducen discontinuidades lógicas en el manejo de evidencia. |
| _BRIDGE_CANDIDATES | Herramientas intermedias nuevas o modificadas actualmente en evaluación de estabilidad. | Auditadas antes de su promoción a estado BRIDGE_TOOLS para prevenir no determinismo. |

**Determinismo y medición**

| Concepto | Definición en lenguaje sencillo | Rol científico |
|---|---|---|
| Determinismo | La propiedad por la cual una entrada y un procedimiento fijos siempre producen la misma salida. | Requisito fundamental para la ciencia forense reproducible. |
| SHA-256 | Función hash criptográfica que se basa exclusivamente en aritmética entera determinista para producir una huella de longitud fija. | Método exacto y computacionalmente económico para detectar cambios de un solo bit en la salida. |
| Archivo de evidencia | Objeto digital bajo investigación (imagen de disco, registro, captura de paquetes, etc.). | Entrada experimental constante. |
| Admisibilidad forense | Estándar que exige que los métodos analíticos sean repetibles y verificables por partes independientes. | Objetivo científico-jurídico de la verificación. |

#### Glosario
- **Determ
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
