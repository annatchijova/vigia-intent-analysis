<!--
VIGIA Academic Documentation
Module: f14e91cc
Batch ID: vigia-doc-0036-f14e91cc
Generated: 2026-05-20T14:56:47.852299+00:00
-->

The user wants academic technical documentation for a Python module `vigia/core/abductive_intent_engine.py` (docstring says `vigia/engine/abductive_intent_engine.py — HITO 2.1`).

Key requirements:
1. Target audience: scientists/researchers who do NOT know Python.
2. Format: Markdown with 4 language sections: ENGLISH, ESPAÑOL, РУССКИЙ, 中文.
3. Each section must include:
   - "What Is This Module?" (plain language explanation)
   - Key concepts with tables
   - A glossary of technical terms
   - A 【科学说明】/【Scientific Note】 box explaining that Peirce/Eco/Grice terminology is NOT mysticism — use the sensor analogy
4. Chinese translations must use: 艾柯 (not Eco), 格赖斯 (not Grice), 取证工件 (not 制品), 逻辑断裂 (not 裂缝).
5. 
6. Do NOT use floating-point math explanations — emphasize deterministic integer arithmetic where applicable.

Module content summary from docstring/classes/functions:
- Module path: vigia/core/abductive_intent_engine.py
- Module docstring: vigia/engine/abductive_intent_engine.py — HITO 2.1
- MOTOR DE INFERENCIA ABDUCTIVA CON OCKHAM'S RAZOR
- Fundamento: Peirce (abduction), Ockham (fewer unobserved assumptions = more probable)
- Principio VIGÍA: Primeridad (datos) → Segundidad (correlaciones) → Terceridad (ley/hábito)
- Question: "¿Qué hábito del atacante explica MEJOR esta cadena de artefactos?" → hypothesis with LOWEST Ockham cost (fewer assumptions) → Deterministic: same input → same winning hypothesis
- GARANTÍA DAUBERT:
  - Ockham cost = integer count (no float)
  - Coverage = integer percentage (no float)
  - Rationale is auditably readable
  - Template tables are explicit (no hidden conditional logic)
- Architecture:
  - Artifact (Primeridad) - raw observed data. In Peirce: sign in crudest form. In IR: an observable.
  - AbductiveHypothesis (Terceridad) - explanatory hypothesis. Answers: "What attacker habit/law explains this chain of artifacts?" Ockham...
  - AbductiveResult - Output: winning hypothesis + runners-up (ordered by Ockham). Winner is hypothesis with: 1. Lower cost...
  - AbductiveIntentEngine - Inference engine with operationalized Ockham's Razor.
    - Principle: Given N candidate hypotheses for a fas... (cut off)
- Functions:
  - to_dict() (listed 3 times, maybe for each class?)
  - to_json()
  - infer_habit(): Abduce attacker intent from artifact chain.
    - Algorithm: 1. Load templates (candidate hypotheses) ...
- Constants & Config: none.

I need to generate thorough but concise documentation. Since the audience doesn't know Python, I should explain the module as a scientific instrument/methodology, not as code. Use the sensor analogy for the scientific note.

Structure for each language section:
- Header with language name.
- "What Is This Module?" section.
- Key Concepts with tables.
- Glossary of Technical Terms.
- 【Scientific Note】/【科学说明】 box about Peirce/Eco/Grice terminology not being mysticism, using sensor analogy.
- License line at the very end of the document? The requirement says "License line: ..." It doesn't specify if it's per section or once. Probably once at the end of the document is fine, but to be safe and clear, I'll put it at the very end. Or maybe in each section? The requirement says "6. License line: ..." It's a line. I'll put it at the end of the document, but maybe repeated in each section? Let's put it once at the end of the doc, but since it's a 4-language doc, maybe place it once globally. Actually, to ensure compliance, I can include it at the bottom of every language section or as a global footer. I'll include it as a global footer after all sections. Or maybe each section should have it? The prompt says "Each section must include: ..." and then separately "License line". I'll include the license line once at the bottom of the whole markdown document. Wait, the prompt lists requirements 1-6. Requirement 5 is just a line to include. I will put it at the very end of the document. To be safe, I'll make it a final footer.

Let's draft content.

ENGLISH:
- What Is This Module?
  This module is the abductive inference engine of the VIGÍA system. It functions like a digital forensic microscope that takes a chain of raw evidence artifacts (files, logs, timestamps) and reasons backward to propose the most probable attacker habit or intent. Instead of guessing, it compares competing explanatory hypotheses using a deterministic scoring rule based on Ockham's Razor: the explanation requiring the fewest unobserved assumptions wins. All calculations use integer arithmetic, ensuring that the same evidence always produces the same conclusion.

- Key Concepts Table:
  | Concept | Role in Forensic Analysis | Scientific Parallel |
  |---|---|---|
  | Artifact | A raw piece of digital evidence (e.g., a log entry, hash, file fragment). In Peircean terms, an instance of *Firstness*—pure data before interpretation. | A voltage reading from a sensor before calibration |
  | AbductiveHypothesis | A candidate explanation of *Thirdness*—a proposed law or habit that would generate the observed artifacts. | A theoretical model predicting how a physical process produces sensor readings |
  | Ockham Cost | An integer count of unobserved assumptions a hypothesis requires. Lower is better. | The number of free parameters added to a model beyond the measured data |
  | Coverage | An integer percentage (0–100) of observed artifacts explained by the hypothesis. | The ratio of data points accounted for by the model, expressed as a whole number |
  | AbductiveResult | The final output: one winning hypothesis plus ranked alternatives (runners-up), ordered strictly by Ockham cost then coverage. | A ranked list of candidate models from a fitting procedure |
  | infer_habit() | The core procedure: loads candidate templates, scores each against the evidence chain, and returns the deterministic best fit. | The automated measurement protocol that selects the best model |

- Glossary:
  | Term | Definition |
  |---|---|
  | Abduction | The logical operation of inferring the best explanation from observed effects (Peirce). |
  | Firstness (Primeridad) | The mode of being of a raw, uninterpreted datum. |
  | Secondness (Segundidad) | The mode of being of brute factual connection or correlation between data points. |
  | Thirdness (Terceridad) | The mode of being of law, habit, or general rule that explains patterns. |
  | Ockham's Razor | The principle that, among competing explanations, the one with the fewest unnecessary assumptions is preferable. |
  | Daubert Guarantee | A set of auditability requirements ensuring forensic methods are testable, explicit, and reproducible. |
  | Deterministic | A system where identical inputs always yield identical outputs; no randomness or floating-point approximation is used. |
  | Integer Arithmetic | Mathematical operations using whole numbers only, avoiding fractional or decimal representations. |

- Scientific Note:
  【Scientific Note】
  Terminology borrowed from Peirce, Eco, or Grice is **not** mysticism or literary criticism. In this engine, these terms function exactly like the components of a sensor array. **Firstness** is the raw voltage off the detector; **Secondness** is the correlation between two detectors firing; **Thirdness** is the calibrated physical law that predicts both. Treating abductive inference as a sensor pipeline makes the process auditable, deterministic, and entirely free of esoteric interpretation.

ESPAÑOL:
- ¿Qué es este módulo?
  Este módulo es el motor de inferencia abductiva del sistema VIGÍA. Funciona como un microscopio forense digital que recibe una cadena de artefactos de evidencia brutos (archivos, registros, marcas de tiempo) y razona hacia atrás para proponer el hábito o la intención del atacante más probable. En lugar de conjeturar, compara hipótesis explicativas competidoras mediante una regla de puntuación determinista basada en la Navaja de Ockham: gana la explicación que requiere menos supuestos no observados. Todos los cálculos usan aritmética entera, garantizando que la misma evidencia siempre produce la misma conclusión.

- Tabla de conceptos clave:
  | Concepto | Papel en el análisis forense | Paralelo científico |
  |---|---|---|
  | Artifact (Artefacto) | Pieza bruta de evidencia digital (p. ej., entrada de registro, hash, fragmento de archivo). En términos peirceanos, instancia de *Primeridad*: dato puro previo a la interpretación. | Lectura de voltaje de un sensor antes de la calibración |
  | AbductiveHypothesis | Explicación candidata de *Terceridad*: ley o hábito propuesto que generaría los artefactos observados. | Modelo teórico que predice cómo un proceso físico produce lecturas de sensor |
  | Costo Ockham | Conteo entero de supuestos no observados que requiere una hipótesis. Menor es mejor. | Número de parámetros libres añadidos a un modelo más allá de los datos medidos |
  | Cobertura | Porcentaje entero (0–100) de artefactos observados explicados por la hipótesis. | Proporción de puntos de datos explicados por el modelo, expresada como número entero |
  | AbductiveResult | Salida final: hipótesis ganadora más alternativas ordenadas, estrictamente por costo Ockham y luego cobertura. | Lista ordenada de modelos candidatos de un procedimiento de ajuste |
  | infer_habit() | Procedimiento central: carga plantillas candidatas, puntúa cada una contra la cadena de evidencia y devuelve el mejor ajuste determinista. | Protocolo de medición automatizado que selecciona el mejor modelo |

- Glosario:
  | Término | Definición |
  |---|---|
  | Abducción | Operación lógica de inferir la mejor explicación a partir de efectos observados (Peirce). |
  | Primeridad (Firstness) | Modo de ser de un dato bruto, no interpretado. |
  | Segundidad (Secondness) | Modo de ser de la conexión factual o correlación entre puntos de datos. |
  | Terceridad (Thirdness) | Modo de ser de la ley, el hábito o la regla general que explica patrones. |
  | Navaja de Ockham | Principio según el cual, entre explicaciones competidoras, se prefiere la que tiene menos supuestos innecesarios. |
  | Garantía Daubert | Requisitos de auditabilidad que aseguran que los métodos forenses sean comprobables, explícitos y reproducibles. |
  | Determinista | Sistema en el que entradas idénticas siempre producen salidas idénticas; no se usa aleatoriedad ni aproximación de coma flotante. |
  | Aritmética entera | Operaciones matemáticas usando solo números enteros, evitando representaciones fraccionarias o decimales. |

- Nota científica:
  【Scientific Note】
  La terminología tomada de Peirce, Eco o Grice **no** es misticismo ni crítica literaria. En este motor, estos términos funcionan exactamente como los componentes de un arreglo de sensores. La **Primeridad** es el voltaje crudo del detector; la **Segundidad** es la correlación entre dos sensores que se activan; la **Terceridad** es la ley física calibrada que predice ambos. Tratar la inferencia abductiva como una tubería de sensores hace el proceso auditable, determinista y completamente libre de interpretación esotérica.

РУССКИЙ:
- Что это за модуль?
  Этот модуль — абдуктивный инференс-движок системы VIGÍA. Он работает как цифровой судебный микроскоп: получает цепочку необработанных артефактов доказательств (файлы, журналы, временные метки) и рассуждает в обратном направлении, предлагая наиболее вероятную привычку или намерение злоумышленника. Вместо догадок он сравнивает конкурирующие объяснительные гипотезы с помощью детерминированного правила оценки, основанного на Бритве Оккама: побеждает объяснение, требующее наименьшего числа ненаблюдаемых допущений. Все вычисления выполняются целочисленной арифметикой, гарантируя, что одни и те же доказательства всегда дают один и тот же вывод.

- Таблица ключевых понятий:
  | Понятие | Роль в судебном анализе | Научный параллель |
  |---|---|---|
  | Artifact (Артефакт) | Необработанный фрагмент цифрового доказательства (например, запись журнала, хеш, фрагмент файла). В терминах Пирса — экземпляр *Первичности*: чистые данные до интерпретации. | Показание напряжения с датчика до калибровки |
  | AbductiveHypothesis | Кандидат-объяснение *Третичности*: предполагаемый закон или привычка, которые могли породить наблюдаемые артефакты. | Теоретическая модель, предсказывающая, как физический процесс генерирует показания датчика |
  | Стоимость по Оккаму | Целочисленный подсчёт ненаблюдаемых допущений, требуемых гипотезой. Чем меньше, тем лучше. | Количество свободных параметров модели, добавленных помимо измеренных данных |
  | Покрытие | Целочисленный процент (0–100) наблюдаемых артефактов, объясняемых гипотезой. | Доля учтённых точек данных, выраженная целым числом |
  | AbductiveResult | Итоговый результат: победившая гипотеза плюс упорядоченные альтернативы (по стоимости Оккама, затем покрытию). | Ранжированный список кандидат-моделей по результатам процедуры подгонки |
  | infer_habit() | Основная процедура: загружает шаблоны-кандидаты, оценивает каждый по цепочке доказательств и возвращает детерминированное наилучшее соответствие. | Автоматизированный протокол измерения, выбирающий лучшую модель |

- Глоссарий:
  | Термин | Определение |
  |---|---|
  | Абдукция | Логическая операция выведения наилучшего объяснения из наблюдаемых следствий (Пирс). |
  | Первичность (Firstness/Primeridad) | Модус бытия необработанного, неинтерпретированного датчика. |
  | Вторичность (Secondness/Segundidad) | Модус бытия фактической связи или корреляции между точками данных. |
  | Третичность (Thirdness/Terceridad) | Модус бытия закона, привычки или общего правила, объясняющего закономерности. |
  | Бритва Оккама | Принцип, согласно которому среди конкурирующих объяснений предпочтительнее то, что содержит меньше ненужных допущений. |
  | Гарантия Доберта | Набор требований к аудируемости, гарантирующих, что судебные методы проверяемы, явны и воспроизводимы. |
  | Детерминированный | Система, в которой идентичные входы всегда дают идентичные выходы; не используется случайность или плавающая точка. |
  | Целочисленная арифметика | Математические операции только с целыми числами, без дробных или десятичных представлений. |

- Научное примечание:
  【Scientific Note】
  Терминология, заимствованная у Пирса, Эко или Грайса, **не** является мистицизмом или литературной критикой. В этом движке эти термины работают точно так же, как компоненты сенсорной матрицы. **Первичность** — это необработанное напряжение с детектора; **Вторичность** — корреляция между срабатываниями двух детекторов; **Третичность** — откалиброванный физический закон, предсказывающий оба. Рассмотрение абдуктивного вывода как сенсорного конвейера делает процесс аудируемым, детерминированным и полностью свободным от эзотерической интерпретации.

中文:
- 这是什么模块？
  本模块是 VIGÍA 系统的溯因推理引擎。它如同一台数字取证显微镜，接收原始证据取证工件（日志条目、哈希值、文件碎片等）构成的链条，并反向推理，以提出最可能的攻击者习惯或意图。该引擎并非凭空猜测，而是依据奥卡姆剃刀原则，通过确定性评分规则对相互竞争的解释性假设进行比较：所需未观测假设最少的解释胜出。所有计算均采用整数运算，确保证据相同则结论必然相同。

- 关键概念表:
  | 概念 | 在取证分析中的角色 | 科学类比 |
  |---|---|---|
  | Artifact（取证工件） | 原始数字证据片段（如日志条目、哈希、文件碎片）。在皮尔斯术语中，属于*第一性*的实例：尚未被解释的纯数据。 | 校准前的传感器原始电压读数 |
  | AbductiveHypothesis（溯因假设） | 对*第三性*的候选解释：一个被提出的规律或习惯，能够产生已观测的取证工件。 | 预测物理过程如何产生传感器读数的理论模型 |
  | 奥卡姆成本（Ockham Cost） | 某一假设所需未观测假设的整数计数。越低越好。 | 模型中超出实测数据的自由参数个数 |
  | 覆盖率（Coverage） | 假设所能解释的已观测取证工件的整数百分比（0–100）。 | 模型所解释的数据点比例，以整数表示 |
  | AbductiveResult（溯因结果） | 最终输出：一个获胜假设，以及按奥卡姆成本和覆盖率严格排序的备选假设。 | 拟合程序得到的候选模型排序列表 |
  | infer_habit() | 核心流程：加载候选模板，依据证据链为每个模板评分，并返回确定性的最优匹配。 | 自动测量协议，用于选定最佳模型 |

- 术语表:
  | 术语 | 定义 |
  |---|---|
  | 溯因（Abduction） | 从观测结果推断最佳解释的逻辑操作（皮尔斯）。 |
  | 第一性（Primeridad/Firstness） | 原始、未被解释的数据之存在方式。 |
  | 第二性（Segundidad/Secondness） | 数据点之间的事实关联或相关性的存在方式。 |
  | 第三性（Terceridad/Thirdness） | 解释模式的规律、习惯或一般规则之存在方式。 |
  | 奥卡姆剃刀 | 在相互竞争的解释中，所需不必要假设最少的解释更可取。 |
  | 道伯特保证（Daubert Guarantee） | 一组可审计性要求，确保取证方法可检验、明确且可复现。 |
  | 确定性（Deterministic） | 相同输入始终产生相同输出的系统；不使用随机性或浮点近似。 |
  | 整数运算 | 仅使用整数的数学运算，避免分数或小数表示。 |

- 科学说明:
  【科学说明】
  从皮尔斯、艾柯或格赖斯借用的术语**并非**神秘主义或文学批评。在本引擎中，这些术语的功能完全等同于传感器阵列的组成部分。**第一性**是检测器输出的原始电压；**第二性**是两个检测器触发之间的关联；**第三性**是预测前两者的经校准物理定律。将溯因推理视为传感器管道，使整个过程具备可审计性、确定性，并且完全不包含玄奥解释。

Now, need to make sure Chinese terms are correct:
- 艾柯 (Eco) ✓
- 格赖斯 (Grice) ✓
- 取证工件 (Artifact) ✓
- 逻辑断裂? The prompt says "逻辑断裂 (not 裂缝)". Wait, the module description doesn't mention "fracture" or "gap". It mentions artifact chain, hypotheses, etc. The requirement is just a constraint on translations if those terms appear. Since no fracture/gap is in the text, I don't need to use 逻辑断裂, but if I did, I must not use 裂缝. I'll just not mention it to avoid risk, or if I do mention logical gap, I must use 逻辑断裂. I'll avoid it.
- "取证工件" is used for Artifact.

Also, do not use floating-point math explanations. Emphasize deterministic integer arithmetic. I have done that.

 at the end.

Format: Markdown. Use headers.

Need to be thorough but concise. The user provided limited info (some classes cut off). I should synthesize based on the provided docstring fragments. I must not hallucinate beyond what's reasonable, but the user explicitly gave the module docstring and class descriptions, even if cut off. I should document exactly what is given: Artifact, AbductiveHypothesis, AbductiveResult, AbductiveIntentEngine, to_dict, to_json, infer_habit. And emphasize the deterministic integer arithmetic.

Let's refine the English text to be more academic and suitable for scientists who don't know Python. Avoid Python jargon like "class", "method", "function". Instead use "component", "procedure", "instrument".

Make sure the scientific note uses the sensor analogy explicitly.

Let's double-check the scientific note content:
- Peirce/Eco/Grice terminology is NOT mysticism.
- Use sensor analogy.
- Firstness = raw voltage off detector.
- Secondness = correlation between two detectors firing.
- Thirdness = calibrated physical law predicting both.

In Chinese, make sure:
- 艾柯 (Eco)
- 格赖斯 (Grice)

Let's structure each language section with clear markdown headings.

Possible structure:

# ENGLISH

## What Is This Module?

...

## Key Concepts

| ... |

## Glossary

| ... |

## Scientific Note

【Scientific Note】
...

Then repeat for other languages.

Finally, license line.

I should ensure I don't use the word "class" or "function" in a Python-specific way. I can say "data structure" or "procedural step".

Also, the prompt says "MODULE PATH: vigia/core/abductive_intent_engine.py" and docstring says "vigia/engine/abductive_intent_engine.py — HITO 2.1". I should probably mention the path as the module identifier.

Let's write it out fully.

ENGLISH details:
- "What Is This Module?"
  The module `vigia/core/abductive_intent_engine.py` (development milestone HITO 2.1) is the abductive inference engine of the VIGÍA forensic framework. It operates as a deterministic analytical instrument. Given a chain of raw digital artifacts—such as log entries, file hashes, or timestamps—the engine generates ranked explanatory hypotheses about the attacker's underlying habit or intent. It does not estimate probabilities using floating-point mathematics. Instead, it applies an operationalized Ockham's Razor: every candidate hypothesis receives an integer Ockham cost (a count of unobserved assumptions) and an integer coverage score (the percentage of artifacts explained). The hypothesis with the lowest cost wins; ties are broken by coverage. Because the arithmetic is strictly integer-based, identical evidence always yields the identical winning hypothesis, satisfying Daubert-standard auditability.

- Key concepts table should include the classes as rows:
  | Concept / Component | Role in Forensic Analysis | Scientific Parallel |
  |---|---|---|
  | Artifact | Raw forensic datum (log, hash, fragment). Represents *Firstness*: pure observable before interpretation. | Uncalibrated voltage reading from a physical sensor |
  | AbductiveHypothesis | Explanatory model representing *Thirdness*: a proposed attacker habit or law that generates the observed chain. | A theoretical law predicting how a process produces specific sensor outputs |
  | Ockham Cost | Integer count of assumptions required by the hypothesis but not observed in evidence. | Number of free parameters added to a model beyond measured data |
  | Coverage | Integer percentage (0–100) of input artifacts accounted for by the hypothesis. | Model-data agreement expressed as a whole-number fraction |
  | AbductiveResult | Ranked output set containing the winning hypothesis and runners-up, ordered first by Ockham cost, then by coverage. | Ranked candidate models from a fitting protocol |
  | AbductiveIntentEngine | The core analytical instrument that loads hypothesis templates and executes the deterministic comparison. | Automated spectrometer selecting the best-matching spectral model |
  | infer_habit() | The measurement protocol: ingests an artifact chain, scores all candidate hypotheses, and returns the deterministic best fit. | Standard operating procedure for model selection |
  | to_dict() / to_json() | Serialization procedures that export the engine's state or results into human-readable, audit-friendly record formats. | Data export functions generating lab notebooks or instrument logs |

Wait, the user listed `to_dict()` three times and `to_json()` once. Maybe each class has its own `to_dict()`. I can generalize: "Serialization exports (to_dict, to_json)".

- Glossary should include terms like:
  - Abduction
  - Ockham's Razor
  - Firstness / Secondness / Thirdness
  - Artifact
  - Hypothesis
  - Deterministic Integer Arithmetic
  - Daubert Guarantee
  - Coverage
  - Ockham Cost

- Scientific Note:
  【Scientific Note】
  Terminology derived from Peirce, Eco, or Grice is **not** mysticism, semiotics worship, or literary criticism. Within this engine, these categories operate exactly like the signal chain of a scientific sensor. **Firstness** is the raw voltage arriving from the detector. **Secondness** is the brute correlation between two detector channels firing together. **Thirdness** is the calibrated physical law that predicts both voltages from first principles. Abductive inference is therefore treated as a sensor pipeline: it converts raw observables into law-governed conclusions without invoking esoteric interpretation, ensuring the process remains reproducible and deterministic.

ESPAÑOL details:
- Similar structure. Use "Artefacto" for Artifact. But in the module docstring it's "Artifact". The user didn't specify Spanish translation constraints except the ones already in Spanish. Use "Artefacto forense" or just "Artifact" since it's the class name? The prompt says "Artifact (Primeridad)" in the docstring. I think keeping "Artifact" as the class name in backticks and explaining it is fine. But the user says target audience doesn't know Python. So maybe avoid code backticks and use descriptive names. I'll use "Artefacto (Artifact)" or just "Artefacto". Let's use the class names as technical labels but explain them. Actually, since they don't know Python, using the English class names might confuse them. I will use descriptive names and note the module's internal designation in parentheses once.
  - Ej: "Artefacto forense (designación interna: Artifact)"
  - Or maybe just translate the concept and mention "en el módulo se denomina Artifact". Let's do that.

Actually, to keep it clean, I will use the English term in italics as the module-internal label, and explain it in the language.

Let's ensure "Ockham's Razor" is "Navaja de Ockham" in Spanish. "Costo Ockham" is used in the docstring.

РУССКИЙ details:
- "Artifact" -> "Артефакт" (forensic artifact). "Artefacto" in Spanish.
- "Ockham Cost" -> "Стоимость по Оккаму" or "Оккамовы расходы". I'll use "Оккамова стоимость" or "Стоимость Оккама". "Стоимость по Оккаму" sounds okay. Let's use "Оккамова стоимость" (Ockham's cost). Or "цена Оккама". I'll use "Оккамова стоимость".
- "Coverage" -> "Покрытие".
- "Deterministic" -> "Детерминированный".

中文 details:
- "Artifact" -> "取证工件". Must use this.
- "AbductiveHypothesis" -> "溯因假设".
- "AbductiveResult" -> "溯因结果".
- "AbductiveIntentEngine" -> "溯因意图引擎".
- "infer_habit()" -> "推断习惯" or "infer_habit 流程". Since they don't know Python, describe it as "习惯推断流程（模块内部标识 infer_habit）".
- "to_dict() / to_json()" -> "字典导出 / JSON 导出" or "结构化导出".
- "Ockham Cost" -> "奥卡姆成本".
- "Coverage" -> "覆盖率".
- "Deterministic" -> "确定性".
- "Integer Arithmetic" -> "整数运算".
- "Daubert Guarantee" -> "道伯特保证".
- Scientific Note: 【科学说明】
  Terminology borrowed from Peirce, 艾柯, or 格赖斯 is NOT mysticism. Use sensor analogy.
  - 第一性 = 检测器输出的原始电压
  - 第二性 = 两个检测器触发之间的关联
  - 第三性 = 预测前两者的经校准物理定律

Double check: The user specifically wants "逻辑断裂 (not 裂缝)" if applicable. Since I don't have that concept in the text, I don't need to use it. But if I mention "gap" or "break" in logic, I must use 逻辑断裂. I'll avoid those words to be safe.

Also, the user says "You NEVER use floating-point math explanations for deterministic systems." So I must not explain anything using floating point. I should emphasize integer arithmetic.

Let's compose the final output.

Structure:

# Module Documentation: `vigia/core/abductive_intent_engine.py` — HITO 2.1

Maybe a brief intro? The user said "Generate the complete academic document". I'll just go into the 4 sections.

---

## ENGLISH

### What Is This Module?

...

### Key Concepts

| Component / Concept | Forensic Role | Scientific Analogy |
|---|---|---|
| ... | ... | ... |

### Glossary of Technical Terms

| Term | Definition |
|---|---|
| ... | ... |

### Scientific Note

【Scientific Note】
...

---

## ESPAÑOL

### ¿Qué es este módulo?

...

### Conceptos clave

...

### Glosario de términos técnicos

...

### Nota científica

【Scientific Note】
...

---

## РУССКИЙ

### Что представляет собой этот модуль?

...

### Ключевые понятия

...

### Глоссарий технических терминов

...

### Научное примечание

【Scientific Note】
...

---

## 中文

### 这是什么模块？

...

### 关键概念

...

### 技术术语表

...

### 科学说明

【科学说明】
...

---



---

Now, I need to make sure the content is thorough but concise. Let's flesh out each section carefully.

ENGLISH:

What Is This Module?
- Module identifier: `vigia/core/abductive_intent_engine.py` (milestone HITO 2.1).
- It is the abductive inference engine of the VIGÍA digital forensic system.
- Input: a chain of raw digital artifacts (evidence pieces).
- Process: loads candidate hypothesis templates, scores each using integer Ockham cost and integer coverage.
- Output: a deterministic ranking of hypotheses explaining the attacker's habit/intent.
- No floating-point arithmetic; all scores are integers. Same input → same output. Daubert compliant.

Key Concepts Table:
Let's make sure to include all items from the prompt.
1. Artifact (Firstness)
2. AbductiveHypothesis (Thirdness)
3. Ockham Cost
4. Coverage
5. AbductiveResult
6. AbductiveIntentEngine
7. infer_habit()
8. to_dict() / to_json()

Rows:
- **Artifact** | The fundamental unit of evidence: a raw, uninterpreted digital trace (log line, hash, timestamp). Corresponds to *Firstness*—pure data prior to meaning. | The uncalibrated voltage pulse produced by a physical transducer.
- **AbductiveHypothesis** | An explanatory construct of *Thirdness*: a candidate law or habit that, if true, would generate the observed artifact chain. | A theoretical model postulating a physical mechanism to account for sensor readings.
- **Ockham Cost** | An integer tally of unobserved assumptions demanded by a hypothesis. The engine minimizes this value. | The count of free parameters in a model that are not anchored by direct measurement.
- **Coverage** | An integer percentage (0–100) quantifying how many input artifacts are explained by a given hypothesis. | The whole-number percentage of data points successfully reproduced by the model.
- **AbductiveResult** | The final deliverable: the winning hypothesis together with ranked runners-up, ordered strictly by Ockham cost and then by coverage. | A ranked list of candidate models output by a fitting algorithm.
- **AbductiveIntentEngine** | The central analytical instrument that orchestrates template loading, integer scoring, and deterministic selection. | An automated spectrometer that selects the best-fitting spectral template from a library.
- **infer_habit()** | The core operational protocol: accepts an artifact chain, evaluates every candidate hypothesis, and returns the best-fit explanation. | The standard operating procedure governing automated model selection.
- **to_dict() / to_json()** | Serialization exports that render the engine’s internal state or final results into transparent, human-auditable formats. | Instrument logs exported to standardized lab notebook formats.

Glossary:
- **Abduction** — The logical inference of the best available explanation from a set of observed effects (C. S. Peirce).
- **Firstness** — The mode of being of a pure, unanalyzed quality or raw datum; immediacy without relation.
- **Secondness** — The mode of being of brute factual reaction or correlation between two distinct data points.
- **Thirdness** — The mode of being of law, habit, or general rule that governs and explains patterns across data.
-
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
