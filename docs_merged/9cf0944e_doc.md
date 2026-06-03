<!--
VIGIA Academic Documentation
Module: 9cf0944e
Batch ID: vigia-doc-0031-9cf0944e
Generated: 2026-05-20T14:56:47.851259+00:00
-->

ENGLISH:
- What Is This Module?: It's an abductive inference engine that analyzes digital forensic artifacts (raw data points) to determine attacker intent. It uses Peircean semiotics and Ockham's Razor. It ranks hypotheses by "cost" (integer count of unobserved assumptions) and picks the deterministic winner. Same input always yields same output. Designed for Daubert-standard forensic admissibility (auditability, explicit logic, no hidden conditionals).
- Key Concepts Table:
  - Artifact / Primeridad: Raw observed data (e.g., log entry, file hash). Deterministic integer features.
  - AbductiveHypothesis / Terceridad: Candidate explanation (attacker habit/law). Contains template and assumptions.
  - Ockham Cost: Integer count of unobserved assumptions required. Lower is better. No floats.
  - Coverage: Integer percentage (0-100) of artifacts explained by hypothesis. No floats.
  - AbductiveResult: Winning hypothesis + ranked runners-up. Fully auditable rationale.
  - AbductiveIntentEngine: The deterministic engine that loads templates and applies integer arithmetic to select the best hypothesis.
  - Deterministic Inference: Same chain of artifacts always produces same ranking because arithmetic uses integer operations on explicit tables.
- Functions/Methods Table:
  - infer(artifact_chain): Loads candidate templates, computes integer Ockham cost and integer coverage for each, ranks them, returns AbductiveResult.
  - to_dict(): Serializes object into an audit-friendly dictionary with integer fields only.
  - to_json(): Exports audit trail to JSON format for review.
- Glossary:
  - Abduction (Peirce): Inference to the best explanation; inferring a cause from its effects.
  - Ockham's Razor: Principle that the explanation requiring fewest new assumptions is preferable.
  - Primeridad (Firstness): The mode of being of a pure quality or raw feeling; here, uninterpreted raw data.
  - Segundidad (Secondness): The mode of being of reaction or relation; here, correlations between artifacts.
  - Terceridad (Thirdness): The mode of being of law or habit; here, the inferred attacker intent/habit.
  - Artifact: A forensic artifact; an observable trace in a digital system.
  - Deterministic system: A system where identical inputs always produce identical outputs, with no randomness or floating-point uncertainty.
  - Daubert Standard: Legal criteria for admissibility of expert evidence, requiring testability and known error rates.
- Scientific Note: Peirce/Eco/Grice terminology is not mysticism. Think of a sensor array: Primeridad is the raw voltage reading (uninterpreted). Segundidad is the correlation between sensor A and sensor B firing together. Terceridad is the firmware rule that says "when A and B fire in this pattern, the event is X." The engine applies this sensor-like logic to forensic data. No divination—just deterministic signal interpretation.

ESPAÑOL:
- ¿Qué es este módulo?: Motor de inferencia abductiva que analiza artefactos forenses digitales (datos brutos) para determinar la intención del atacante. Usa la semiótica peirceana y la Navaja de Ockham. Clasifica hipótesis por "costo" (conteo entero de supuestos no observados) y elige al ganador determinista. Mismo entrada → misma salida. Diseñado para admisibilidad forense bajo estándar Daubert (auditabilidad, lógica explícita, sin condicionales ocultos).
- Conceptos clave (tablas similar).
- Glosario: Abducción (Peirce), Navaja de Ockham, Primeridad, Segundidad, Terceridad, Artefacto forense, Sistema determinista, Estándar Daubert.
- Nota científica: La terminología de Peirce/Eco/Grice no es misticismo. Análogo a sensores: Primeridad = voltaje crudo; Segundidad = correlación entre sensores; Terceridad = regla del firmware que interpreta el patrón. Se aplica lógica determinista de interpretación de señales.

РУССКИЙ:
- Что это за модуль?: Дедуктивно-абдуктивный? No, abductive. Абдуктивный движок вывода, анализирующий цифровые криминалистические артефакты (сырые данные) для определения намерения атакующего. Использует семиотику Пирса и Бритву Оккама. Ранжирует гипотезы по «стоимости» (целочисленное количество ненаблюдаемых допущений) и выбирает детерминированного победителя. Одинаковый вход → одинаковый выход. Разработан для стандарта Доберта (Daubert) — допустимость экспертных доказательств, аудируемость, явная логика, без скрытых условий.
- Ключевые понятия.
- Глоссарий: Абдукция (Пирс), Бритва Оккама, Первичность (Первое), Вторичность (Второе), Третичность (Третье), Артефакт (криминалистический), Детерминированная система, Стандарт Доберта.
- Научное примечание: Терминология Пирса/Эко/Грайса — это не мистицизм. Аналогия с датчиком: Первичность — сырые показания напряжения; Вторичность — корреляция между срабатыванием датчиков А и Б; Третичность — прошивочное правило «когда А и Б срабатывают таким образом, событие есть X». Движок применяет эту датчикоподобную логику к криминалистическим данным. Никакого гадания — только детерминированная интерпретация сигналов.

中文:
- 这是什么模块？: 溯因推理引擎，用于分析数字取证工件（原始观测数据）以确定攻击者意图。使用皮尔斯符号学和奥卡姆剃刀。通过“奥卡姆成本”（未观测假设的整数计数）对假设进行排序，并选择确定性的最优解。相同输入总是产生相同输出。符合道伯特标准（Daubert）的取证可采性要求（可审计、逻辑显式、无隐藏条件）。
- 关键概念。
- 术语表: 溯因（皮尔斯）、奥卡姆剃刀、首位性（第一性）、次位性（第二性）、第三位性（第三性）、取证工件、确定性系统、道伯特标准。 Note: 艾柯 (Eco) and 格赖斯 (Grice) must appear somewhere. I should mention them in the scientific note or glossary. Since the scientific note mentions Peirce/Eco/Grice, I will include them there. Also ensure 取证工件 and 逻辑断裂 (though the prompt says 逻辑断裂 not 裂缝, I need to see if there's a place for it. Maybe in the context of "breaks in logic"? The prompt says "use: 取证工件 (not 制品), 逻辑断裂 (not 裂缝)". I should probably mention 逻辑断裂 in the glossary or note, e.g., explaining that the engine detects logical breaks? Or just use it in a sentence. Let me incorporate it naturally. For example: "The engine flags logical断裂 (logical breaks) between artifacts rather than statistical anomalies." Or in the glossary: 逻辑断裂 — logical discontinuity between forensic artifacts. I'll make sure to include it.
- 【科学说明】: 皮尔斯、艾柯与格赖斯的术语并非神秘主义。请使用传感器类比：首位性相当于传感器的原始电压读数（未经解释）；次位性相当于传感器A与传感器B同时触发的相关性；第三位性相当于固件规则——“当A与B以特定模式触发时，事件为X”。本引擎将此类传感器逻辑应用于取证工件，识别的是逻辑断裂与确定性模式，而非进行占卜。所有运算均为确定性整数运算，不存在浮点概率的“黑箱”。

Important: Do NOT use floating-point math explanations for deterministic systems. Emphasize deterministic integer arithmetic.

Also, the module path is vigia/abductive_intent_engine.py, docstring says vigia/engine/abductive_intent_engine.py — HITO 2.1. I should mention the path.

The prompt lists FUNCTIONS: to_dict() three times, to_json(), infer(). It probably means each class has to_dict(), and maybe the engine has infer(). I will structure the tables to reflect methods.

Let's draft the tables carefully.

ENGLISH Table 1: Core Concepts
| Term | Semiotic Role | Forensic Meaning | Arithmetic Nature |
|---|---|---|---|
| Artifact (Primeridad) | Firstness | Raw, uninterpreted digital trace (log line, hash, timestamp) | Integer features extracted deterministically |
| AbductiveHypothesis | Thirdness | Candidate attacker habit/law that explains an artifact chain | Ockham Cost = integer count of unobserved assumptions |
| Coverage | Secondness/Relation | Percentage of input artifacts explained by the hypothesis | Integer percentage (0–100), no fractional rounding |
| AbductiveResult | N/A | Winner + ranked runners-up with readable rationale | Deterministic ordering via integer comparison |
| AbductiveIntentEngine | N/A | Inference processor that loads explicit template tables | All comparisons use integer arithmetic |

ENGLISH Table 2: Public Interface (since audience doesn't know Python, explain what each "operation" does)
| Operation | Input | Output | Deterministic Guarantee |
|---|---|---|---|
| infer(artifact_chain) | Ordered list of Artifacts | AbductiveResult | Same chain always yields same result; costs are integers |
| to_dict() | Any engine object | Human-readable dictionary with integer fields | Audit-friendly; no hidden conditional logic |
| to_json() | Any engine object | Serialized JSON audit trail | Lossless integer representation |

ESPAÑOL Table 1:
| Término | Rol Semiótico | Significado Forense | Naturaleza Aritmética |
|---|---|---|---|
| Artefacto (Primeridad) | Primeridad | Dato digital bruto e ininterpretado (log, hash, timestamp) | Características enteras extraídas determinísticamente |
| AbductiveHypothesis | Terceridad | Hábito/ley candidata del atacante que explica la cadena | Costo Ockham = conteo entero de supuestos no observados |
| Cobertura | Segundidad/Relación | Porcentaje de artefactos de entrada explicados | Porcentaje entero (0–100), sin redondeo fraccional |
| AbductiveResult | N/A | Ganadora + finalistas ordenados con rationale legible | Orden determinista mediante comparación entera |
| AbductiveIntentEngine | N/A | Procesador de inferencia que carga tablas explícitas | Todas las comparaciones usan aritmética entera |

ESPAÑOL Table 2:
| Operación | Entrada | Salida | Garantía Determinista |
|---|---|---|---|
| infer(cadena_artefactos) | Lista ordenada de Artefactos | AbductiveResult | Misma cadena → mismo resultado; costos enteros |
| to_dict() | Cualquier objeto del motor | Diccionario legible con campos enteros | Auditable; sin lógica condicional oculta |
| to_json() | Cualquier objeto del motor | Pista de auditoría JSON serializada | Representación entera sin pérdida |

РУССКИЙ Table 1:
| Термин | Семиотическая роль | Криминалистическое значение | Арифметическая природа |
|---|---|---|---|
| Артефакт (Первичность) | Первичность | Сырые, неинтерпретированные цифровые следы (лог, хэш, метка времени) | Целочисленные признаки извлекаются детерминированно |
| AbductiveHypothesis | Третичность | Кандидат-привычка/закон атакующего, объясняющий цепочку | Стоимость Оккама = целое число ненаблюдаемых допущений |
| Покрытие | Вторичность/Отношение | Процент входных артефактов, объясняемых гипотезой | Целое процентное значение (0–100), без дробного округления |
| AbductiveResult | Н/Д | Победитель + упорядоченные претенденты с обоснованием | Детерминированное упорядочивание целочисленным сравнением |
| AbductiveIntentEngine | Н/Д | Процессор вывода, загружающий явные таблицы шаблонов | Все сравнения — целочисленная арифметика |

РУССКИЙ Table 2:
| Операция | Вход | Выход | Детерминированная гарантия |
|---|---|---|---|
| infer(цепочка_артефактов) | Упорядоченный список Артефактов | AbductiveResult | Одинаковая цепочка → одинаковый результат; стоимости — целые |
| to_dict() | Любой объект движка | Читаемый словарь с целочисленными полями | Пригоден для аудита; без скрытой условной логики |
| to_json() | Любой объект движка | Сериализованная JSON-след аудита | Целочисленное представление без потерь |

中文 Table 1:
| 术语 | 符号学角色 | 取证含义 | 运算性质 |
|---|---|---|---|
| 取证工件（首位性） | 第一性 | 原始、未经解释的数字痕迹（日志、哈希、时间戳） | 确定性提取整数特征 |
| 溯因假设（AbductiveHypothesis） | 第三性 | 解释工件链的攻击者习惯/规律候选 | 奥卡姆成本 = 未观测假设的整数计数 |
| 覆盖率 | 第二性/关联 | 假设所解释的输入工件占比 | 整数百分比（0–100），无分数舍入 |
| 溯因结果（AbductiveResult） | 不适用 | 获胜假设 + 按整数成本排序的候选及可读依据 | 通过整数比较进行确定性排序 |
| 溯因意图引擎（AbductiveIntentEngine） | 不适用 | 加载显式模板表的推理处理器 | 所有比较均使用整数运算 |

中文 Table 2:
| 操作 | 输入 | 输出 | 确定性保证 |
|---|---|---|---|
| infer(工件链) | 有序的取证工件列表 | 溯因结果 | 相同工件链始终产生相同结果；成本为整数 |
| to_dict() | 引擎任意对象 | 仅含整数字段的可读字典 | 可审计；无隐藏条件逻辑 |
| to_json() | 引擎任意对象 | 序列化JSON审计追踪 | 无损整数表示 |

Now Glossary for each.

ENGLISH Glossary:
- **Abduction (Peirce):** A logical inference that proposes a hypothesis to explain an observed phenomenon. Distinct from deduction and induction.
- **Ockham's Razor:** A problem-solving principle stating that the explanation with the fewest unobserved assumptions is the best one.
- **Firstness (Primeridad):** The category of raw, uninterpreted qualitative data; a digital artifact before semantic labeling.
- **Secondness (Segundidad):** The category of brute fact, reaction, or correlation between two observed items.
- **Thirdness (Terceridad):** The category of law, habit, or general rule inferred from data and correlations.
- **Forensic Artifact:** Any observable trace left in a digital system (e.g., log entry, registry key, file hash).
- **Deterministic System:** A system in which the same initial state and input always produce the identical output, with no stochastic or floating-point ambiguity.
- **Daubert Standard:** A legal benchmark for the admissibility of expert testimony, emphasizing testability, peer review, error rates, and general acceptance.
- **Ockham Cost:** An integer tally of unobserved assumptions required by a hypothesis. Lower cost = higher rank.
- **Logical Break:** A discontinuity in an artifact chain that a hypothesis must bridge with an explicit assumption.

ESPAÑOL Glossary:
- **Abducción (Peirce):** Inferencia lógica que propone una hipótesis para explicar un fenómeno observado. Distinta de la deducción y la inducción.
- **Navaja de Ockham:** Principio que establece que la explicación con menos supuestos no observados es la mejor.
- **Primeridad:** Categoría de los datos cualitativos brutos e ininterpretados; un artefacto digital antes del etiquetado semántico.
- **Segundidad:** Categoría del hecho bruto, reacción o correlación entre dos elementos observados.
- **Terceridad:** Categoría de la ley, hábito o regla general inferida a partir de datos y correlaciones.
- **Artefacto Forense:** Cualquier rastro observable dejado en un sistema digital (entrada de log, clave de registro, hash de archivo).
- **Sistema Determinista:** Sistema en el que el mismo estado inicial y entrada siempre producen la misma salida, sin ambigüedad estocástica o de punto flotante.
- **Estándar Daubert:** Referencia legal para la admisibilidad de testimonio pericial; enfatiza la comprobabilidad, revisión por pares, tasas de error y aceptación general.
- **Costo Ockham:** Conteo entero de supuestos no observados requeridos por una hipótesis. Menor costo = mayor ranking.
- **Ruptura Lógica:** Discontinuidad en una cadena de artefactos que una hipótesis debe salvar con un supuesto explícito.

РУССКИЙ Glossary:
- **Абдукция (Пирс):** Логический вывод, предлагающий гипотезу для объяснения наблюдаемого явления. Отличается от дедукции и индукции.
- **Бритва Оккама:** Принцип решения проблем, согласно которому объяснение с наименьшим числом ненаблюдаемых допущений является наилучшим.
- **Первичность (Первое):** Категория сырых, неинтерпретированных качественных данных; цифровой артефакт до семантической маркировки.
- **Вторичность (Второе):** Категория грубого факта, реакции или корреляции между двумя наблюдаемыми элементами.
- **Третичность (Третье):** Категория закона, привычки или общего правила, выводимого из данных и корреляций.
- **Криминалистический артефакт:** Любой наблюдаемый след в цифровой системе (запись журнала, ключ реестра, хеш файла).
- **Детерминированная система:** Система, в которой одно и то же начальное состояние и вход всегда дают идентичный выход, без стохастической или плавающей неоднозначности.
- **Стандарт Доберта (Daubert):** Правовой ориентир для допустимости экспертных показаний; акцент на тестируемости, рецензировании, частоте ошибок и общем признании.
- **Стоимость Оккама:** Целочисленный подсчёт ненаблюдаемых допущений, требуемых гипотезой. Меньшая стоимость = более высокий ранг.
- **Логический разрыв:** Разрыв в цепочке артефактов, который гипотеза должна преодолеть явным допущением.

中文 Glossary:
- **溯因（皮尔斯）**: 提出假设以解释观测现象的逻辑推理过程，区别于演绎与归纳。
- **奥卡姆剃刀**: 一种问题解决原则：所需未观测假设最少的解释即为最优解释。
- **首位性（第一性）**: 原始、未经解释之质性数据的范畴；尚未赋予语义标签的数字痕迹。
- **次位性（第二性）**: 事实、反应或两个观测项之间关联的范畴。
- **第三位性（第三性）**: 从数据与关联中推断出的规律、习惯或一般规则的范畴。
- **取证工件**: 数字系统中留下的任何可观测痕迹（日志条目、注册表键、文件哈希等）。
- **确定性系统**: 相同初态与输入始终产生相同输出的系统，不存在随机性或浮点歧义。
- **道伯特标准（Daubert）**: 专家证言可采性的法律基准，强调可检验性、同行评审、错误率及普遍接受度。
- **奥卡姆成本**: 假设所需未观测假设的整数计数。成本越低，排名越高。
- **逻辑断裂**: 工件链中的不连续性，假设必须通过显式假设予以弥合。

Scientific Note requirements: Explain Peirce/Eco/Grice terminology is NOT mysticism — use sensor analogy. Must be in a box.

ENGLISH Scientific Note:
> 【Scientific Note】
> The terminology of Peirce, Eco, and Grice is operational, not mystical. Think of a deterministic sensor array:
> - **Firstness (Primeridad)** is the raw voltage reading from a transducer—pure quality before interpretation.
> - **Secondness (Segundidad)** is the correlation pattern when Sensor A and Sensor B fire simultaneously—brute fact, not yet a rule.
> - **Thirdness (Terceridad)** is the firmware law that states: *“If Sensor A and Sensor B exceed integer threshold T in sequence S, then event E is present.”*
> The VIGÍA engine applies exactly this sensor-like logic to forensic artifacts. It does not divine intent; it counts integer assumptions and selects the hypothesis that bridges logical breaks with the fewest unobserved steps. Every operation is deterministic integer arithmetic—identical inputs always trigger identical outputs.

ESPAÑOL Scientific Note:
> 【Nota Científica】
> La terminología de Peirce, Eco y Grice es operacional, no mística. Piense en un conjunto determinista de sensores:
> - **Primeridad** es la lectura de voltaje cruda de un transductor—calidad pura previa a la interpretación.
> - **Segundidad** es el patrón de correlación cuando el Sensor A y el Sensor B se activan simultáneamente—hecho bruto, aún no una regla.
> - **Terceridad** es la ley del firmware que declara: *“Si el Sensor A y el Sensor B superan el umbral entero T en la secuencia S, entonces el evento E está presente.”*
> El motor VIGÍA aplica exactamente esta lógica sensorial a los artefactos forenses. No adivina la intención; cuenta supuestos enteros y selecciona la hipótesis que salva las rupturas lógicas con el menor número de pasos no observados. Cada operación es aritmética entera determinista—entradas idénticas siempre producen salidas idénticas.

РУССКИЙ Scientific Note:
> 【Научное примечание】
> Терминология Пирса, Эко и Грайса операционна, а не мистична. Представьте детерминированный массив датчиков:
> - **Первичность** — это сырое показание напряжения с преобразователя: чистое качество до интерпретации.
> - **Вторичность** — это корреляционный паттерн, когда датчик А и датчик В срабатывают одновременно: грубый факт, ещё не правило.
> - **Третичность** — это прошивочный закон, утверждающий: *«Если датчик А и датчик В превышают целочисленный порог T в последовательности S, то событие E присутствует.»*
> Движок VIGÍA применяет именно такую датчикоподобную логику к криминалистическим артефактам. Он не гадает о намерениях; он подсчитывает целочисленные допущения и выбирает гипотезу, которая перекрывает логические разрывы наименьшим числом ненаблюдаемых шагов. Каждая операция — детерминированная целочисленная арифметика: одинаковые входы всегда дают одинаковые выходы.

中文 Scientific Note:
> 【科学说明】
> 皮尔斯、艾柯与格赖斯的术语是操作性的，绝非神秘主义。请想象一套确定性传感器阵列：
> - **首位性（第一性）** 是传感器换能器的原始电压读数——尚未被解释的纯粹质性。
> - **次位性（第二性）** 是传感器A与传感器B同时触发时的相关性模式——属于粗粝事实，尚未上升为规则。
> - **第三位性（第三性）** 是固件定律，其表述为：“若传感器A与传感器B在序列S中以特定模式超过整数阈值T，则事件E成立。”
> VIGÍA 引擎正是将此类传感器逻辑应用于取证工件。它并非占卜意图，而是以整数运算计数未观测假设，并选择能以最少未观测步骤弥合**逻辑断裂**的假设。全部运算均为确定性整数算术——相同输入恒得相同输出。

Now I need to ensure the Chinese section uses 艾柯, 格赖斯, 取证工件, 逻辑断裂. I have used 艾柯, 格赖斯, 取证工件, 逻辑断裂 in the Chinese sections.

Also, do not use floating-point math explanations. I must make sure I don't mention floats at all except to say they are prohibited. I should emphasize integer arithmetic.

- "MOTOR DE INFERENCIA ABDUCTIVA CON OCKHAM'S RAZOR" -> I should include this as the module title.
- The docstring says HITO 2.1. I should mention this.
- The classes are Artifact, AbductiveHypothesis, AbductiveResult, AbductiveIntentEngine. I described them.
- Functions: infer, to_dict, to_json. I described them.
- "Determinista: mismo input → misma hipótesis ganadora" -> I covered this.
- "GARANTÍA DAUBERT" -> I covered this.
- "Costo Ockham = conteo entero (no float)" -> I covered this.
- "Cobertura = porcentaje entero (no float)" -> I covered this.
- "Tablas de templates son explícitas (no lógica condicional oculta)" -> I covered this.

I need to make sure the document is Markdown formatted cleanly.

Possible structure:

# Module Documentation: `vigia/abductive_intent_engine.py`

## ENGLISH
...
## ESPAÑOL
...
## РУССКИЙ
...
## 中文
...

Then License line.

ENGLISH: "What Is This Module?"
ESPAÑOL: "¿Qué es este módulo?" or "¿Qué Es Este Módulo?"
РУССКИЙ: "Что это за модуль?" or "Что Этот Модуль?"
中文: "这是什么模块？"

I'll make sure the tables are clear.

Let's refine the English "What Is This Module?" to be plain language.

**ENGLISH - What Is This Module?**
This module is a deterministic reasoning engine for digital forensics. It examines a chain of raw digital traces—called *artifacts*—and asks: *“What attacker habit best explains these observations?”* It proposes several candidate explanations (hypotheses), then ranks them using **Ockham’s Razor** by counting how many unobserved assumptions each hypothesis requires. The engine uses only integer arithmetic: assumption counts are whole numbers, coverage is an integer percentage, and the winner is always the same for the same input. This design meets forensic **Daubert** standards: every step is explicit, auditable, and free of hidden conditional logic or floating-point uncertainty.

**ESPAÑOL - ¿Qué es este módulo?**
Este módulo es un motor de razonamiento determinista para forense digital. Examina una cadena de rastros digitales brutos—llamados *artefactos*—y pregunta: *“¿Qué hábito del atacante explica mejor estas observaciones?”* Propone varias explicaciones candidatas (hipótesis) y las ordena aplicando la **Navaja de Ockham**, contando cuántos supuestos no observados requiere cada una. El motor utiliza solo aritmética entera: los conteos de supuestos son números enteros, la cobertura es un porcentaje entero y el ganador es siempre el mismo para la misma entrada. Este diseño cumple los estándares forenses **Daubert**: cada paso es explícito, auditable y libre de lógica condicional oculta o incertidumbre de punto flotante.

**РУССКИЙ - Что это за модуль?**
Этот модуль — детерминированный механизм рассуждения для цифровой криминалистики. Он изучает цепочку сырых цифровых следов — *артефактов* — и задаёт вопрос: *«Какая привычка атакующего наилучшим образом объясняет эти наблюдения?»* Он генерирует несколько кандидат-объяснений (гипотез), затем ранжирует их с помощью **Бритвы Оккама**, подсчитывая количество ненаблюдаемых допущений, необходимых каждой гипотезе. Движок использует исключительно целочисленную арифметику: подсчёты допущений — целые числа, покрытие — целое процентное значение, а победитель при одном и том же вход
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
