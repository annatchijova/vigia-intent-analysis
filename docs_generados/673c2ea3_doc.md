<!--
VIGIA Academic Documentation
Module: 673c2ea3
Batch ID: vigia-doc-0069-673c2ea3
Generated: 2026-05-20T14:56:47.859298+00:00
-->

The user wants technical documentation for a Python module `vigia/core/peirceplanner_bounded.py` written in 4 languages: English, Spanish, Russian, Chinese.

Key requirements:
1. Target audience: scientists/researchers who do NOT know Python.
2. Format: Markdown with 4 language sections.
3. Each section must include:
   - "What Is This Module?" (plain language explanation)
   - Key concepts with tables
   - Glossary of technical terms
   - A 【科学说明】/【Scientific Note】 box explaining that Peirce/Eco/Grice terminology is NOT mysticism — use the sensor analogy
4. Chinese translations must use specific terms:
   - 艾柯 (not Eco)
   - 格赖斯 (not Grice)
   - 取证工件 (not 制品)
   - 逻辑断裂 (not 裂缝)
5. 
6. Do NOT use floating-point math explanations — emphasize deterministic integer arithmetic where applicable.

From the module docstring provided:
- It's a PeircePlanner with Miller limit (N=7) and oscillation detection for VIGÍA.
- Principle: Abductive reasoning without limit can oscillate infinitely between contradictory hypotheses or overfit to noise. Miller limit (7±2, George Miller 1956) formalizes the human cognitive limit that a forensic expert applies instinctively.
- Stop conditions (in order):
  1. Complete signal coverage
  2. Ockham convergence (stable cost between iterations)
  3. Oscillation detected A→B→A (ABSTAIN — contradictory evidence)
  4. Hard Miller limit: 7 iterations
- Kimi fix applied:
  - display uses int(confidence * 100) — never round()
  - PlannerResult.display_confidence_pct() for reports
- Invariants: All... (cut off)
- Classes:
  - PlannerTerminationReason
  - HypothesisStatus
  - EvidenceSignal
  - Hypothesis
  - PlannerIteration
  - PlannerResult
  - OscillationDetector: Detects A→B→A pattern in winning hypothesis sequence. Deterministic sliding window.
- Functions:
  - run_bounded_planner(): Abduction engine with Miller limit and oscillation detection.
  - hypothesis_generator: function that generates new hypo... (cut off)
  - digest(): Deterministic hash of hypothesis for cycle detection.
  - display_confidence_pct(): Kimi fix: truncated int(), never round().
  - to_report():
  - record():
  - detect():
  - score():
- Constants & Config:
  - SIGNAL_COVERAGE
  - OCKHAM_CONVERGENCE
  - OSCILLATION_DETECTED
  - MILLER_LIMIT_REACHED
  - HYPOTHESIS_EXHAUSTED
  - ACTIVE
  - CONFIRMED
  - DISCARDED
  - SUSPENDED

I need to construct a comprehensive academic document. Since the audience doesn't know Python, I should describe the module as a scientific instrument or methodology, not as code.

Structure for each language section:
1. Header with language name.
2. "What Is This Module?" section.
3. Key Concepts (with tables).
4. Scientific Note box.
5. Glossary.
6. License line at the very end (once, or per section? The user says each section must include... but the license line is a separate requirement. I'll put the license line at the end of each section or a final global license. The prompt says "License line: ...". I'll include it in each section footer to be safe, or maybe once at the end. Let's put it at the end of the document, but since it's 4 language sections, I'll put it at the end of each language block or a single concluding line. I'll add it as a footer in each language section for completeness, or perhaps just once. The prompt says "Each section must include..." but lists specific bullets. The license line is listed separately (point 5). I'll include the license line at the bottom of the entire markdown document, perhaps repeated in each language or just once in English. To be safe and compliant, I'll include it at the end of every language section.)

Wait, the user says: "3. Each section must include: ... 5. License line: ..." This could mean the license line is a global requirement. I'll put it at the end of the document, maybe once. But to ensure compliance with "Each section must include", I'll include the license line at the bottom of each section. Actually, re-reading: "5. License line: ''" This is a separate requirement. I will place it prominently once at the end of the document, but since the sections are distinct, I'll append it to each section to be absolutely sure. Or maybe one final line. Let's do one final line after all sections, but also maybe include a note in each section's footer. I'll include it in each section's footer to satisfy "each section must include" if interpreted broadly.

Actually, to be precise, I'll make the license line appear once at the end of the document, but ensure it's visible. The prompt structure is:
1. Target audience...
2. Format...
3. Each section must include: (bulleted list)
4. Chinese translations...
5. License line...
6. Do NOT use...

So points 1-6 are all requirements. Point 3 is about section content. Point 5 is a global requirement. I will place the license line once at the very end.

Let's plan the content.

**ENGLISH Section:**
- What Is This Module?
  This module implements a bounded abductive inference engine for the VIGÍA forensic analysis framework. In plain language, it mimics how a human expert forms educated guesses (hypotheses) to explain collected evidence signals, but prevents the reasoning process from running forever or chasing contradictory ideas in circles. It enforces a strict cognitive boundary known as the Miller limit (7 iterations), derived from George Miller’s 1956 work on human short-term memory capacity. The system stops when it fully explains the evidence, when the explanations stabilize, when it detects logical oscillation, or when it hits the hard iteration ceiling. All internal calculations use deterministic integer arithmetic to guarantee reproducible results.

- Key Concepts with tables:
  Table 1: Stop Conditions (Termination Reasons)
  | Condition | Scientific Meaning | Integer Rule |
  |---|---|---|
  | SIGNAL_COVERAGE | All evidence signals are explained by the current hypothesis set. | Binary check: 0 or 1 (covered / not covered). |
  | OCKHAM_CONVERGENCE | Cost function stable across iterations. No new complexity added. | Delta between iteration *n* and *n-1* is exactly 0. |
  | OSCILLATION_DETECTED | System flips between hypothesis A and hypothesis B. Contradictory evidence. | Sliding window of length 3 detects A→B→A pattern via integer hashes. |
  | MILLER_LIMIT_REACHED | Cognitive safety limit triggered after 7 iterations. | Iteration counter == 7. Hard stop. |
  | HYPOTHESIS_EXHAUSTED | No further candidate explanations remain in the search space. | Empty generator queue. |

  Table 2: Hypothesis Lifecycle States
  | State | Meaning |
  |---|---|
  | ACTIVE | Currently under evaluation. |
  | CONFIRMED | Accepted as explanatory of the evidence. |
  | DISCARDED | Rejected due to cost or inconsistency. |
  | SUSPENDED | Temporarily set aside (e.g., pending new evidence). |

  Table 3: Core Artifacts (Classes / Functions described as conceptual objects)
  | Artifact | Role |
  |---|---|
  | EvidenceSignal | A single observation or measurement from the forensic source. |
  | Hypothesis | A candidate explanation linking one or more signals. |
  | PlannerIteration | One complete cycle of generate → score → evaluate. |
  | OscillationDetector | Deterministic sensor that watches the last 3 winning hypotheses to detect A→B→A. |
  | run_bounded_planner() | The main engine. Orchestrates inference until a stop condition is met. |

  Table 4: Deterministic Integer Arithmetic Guarantees
  | Operation | Guarantee |
  |---|---|
  | digest() | Produces a deterministic integer hash of a hypothesis. Enables exact cycle detection without probability. |
  | display_confidence_pct() | Converts confidence to a percentage via truncation (`int(confidence * 100)`), never rounding. Eliminates non-deterministic floating-point presentation. |

- Scientific Note:
  【Scientific Note】
  The terminology of Peirce, Eco, and Grice is not mysticism. Think of this module as a sensor array, not a séance. Charles Sanders Peirce’s "abduction" is simply the logical operation of inferring the best available explanation from incomplete data—identical in principle to how a geophysicist infers subsurface structure from seismic sensor readings. Umberto Eco’s semiotics and H. Paul Grice’s conversational maxims provide the *calibration rules* for that sensor: they define what counts as noise, what counts as a valid signal, and when two readings contradict each other. The OscillationDetector is therefore not detecting "ghosts"; it is registering sensor saturation when two mutually exclusive calibration states (hypotheses A and B) alternate, indicating the input evidence contains contradictory information. The Miller limit is the buffer size of the instrument’s working memory. All outputs are deterministic integer values, ensuring that every experiment is reproducible.

- Glossary:
  - **Abductive reasoning / Abduction**: Inference to the best explanation. Unlike deduction (certain) or induction (probabilistic generalization), abduction generates plausible causes for observed effects.
  - **Miller limit (N=7)**: The cognitive boundary proposed by George Miller in 1956, stating that humans can hold approximately 7±2 items in working memory. Here, it caps the number of inference iterations.
  - **Ockham convergence**: A stop condition based on Ockham’s Razor: if the explanatory cost does not decrease between two successive iterations, the simplest sufficient explanation has been found.
  - **Oscillation (A→B→A)**: A logical trap where the system alternates between two contradictory hypotheses, indicating that the evidence set is ambiguous or mutually contradictory.
  - **Deterministic integer arithmetic**: Mathematical operations using whole numbers with exact results, ensuring no rounding errors or platform-dependent floating-point variance.
  - **Forensic artifact (取证工件)**: Any object or data structure carrying probative value in a digital investigation.
  - **Sliding window**: A fixed-size buffer that examines the most recent *N* elements of a sequence. Here, a window of 3 hypotheses.

**ESPAÑOL Section:**
- ¿Qué es este módulo?
  Motor de inferencia abductiva acotada para el marco forense VIGÍA. Simula cómo un perito humano genera conjeturas para explicar señales de evidencia, pero impide que el razonamiento se extienda infinitamente o que persiga ideas contradictorias en círculos. Impone un límite cognitivo estricto: el límite de Miller (7 iteraciones), basado en la capacidad de memoria a corto plazo humana (George Miller, 1956). El sistema se detiene cuando explica toda la evidencia, cuando las explicaciones se estabilizan, cuando detecta oscilación lógica o al alcanzar el techo duro de iteraciones. Todos los cálculos internos usan aritmética entera determinista.

- Tablas:
  Tabla 1: Condiciones de Parada
  | Condición | Significado Científico | Regla Entera |
  |---|---|---|
  | SIGNAL_COVERAGE | Todas las señales de evidencia están explicadas. | Verificación binaria: 0 o 1. |
  | OCKHAM_CONVERGENCE | Función de costo estable entre iteraciones. | Delta entre iteración *n* y *n-1* es exactamente 0. |
  | OSCILLATION_DETECTED | El sistema alterna entre hipótesis A y B. | Ventana deslizante de longitud 3 detecta patrón A→B→A mediante hashes enteros. |
  | MILLER_LIMIT_REACHED | Límite de seguridad cognitiva tras 7 iteraciones. | Contador de iteración == 7. Parada dura. |
  | HYPOTHESIS_EXHAUSTED | No quedan explicaciones candidatas. | Cola del generador vacía. |

  Tabla 2: Estados del Ciclo de Vida de la Hipótesis
  | Estado | Significado |
  |---|---|
  | ACTIVE | En evaluación actualmente. |
  | CONFIRMED | Aceptada como explicatoria de la evidencia. |
  | DISCARDED | Rechazada por costo o inconsistencia. |
  | SUSPENDED | Apartada temporalmente. |

  Tabla 3: Artefactos Principales
  | Artefacto | Rol |
  |---|---|
  | EvidenceSignal | Una observación o medición de la fuente forense. |
  | Hypothesis | Explicación candidata que vincula señales. |
  | PlannerIteration | Un ciclo completo de generar → puntuar → evaluar. |
  | OscillationDetector | Sensor determinista que vigila las últimas 3 hipótesis ganadoras para detectar A→B→A. |
  | run_bounded_planner() | Motor principal. Orquesta la inferencia hasta cumplir una condición de parada. |

  Tabla 4: Garantías de Aritmética Entera Determinista
  | Operación | Garantía |
  |---|---|
  | digest() | Produce un hash entero determinista de una hipótesis. Habilita detección exacta de ciclos sin probabilidad. |
  | display_confidence_pct() | Convierte confianza a porcentaje mediante truncamiento (`int(confianza * 100)`), nunca redondeo. Elimina presentación de punto flotante no determinista. |

- Nota Científica:
  【Nota Científica】
  La terminología de Peirce, Eco y Grice no es misticismo. Piense en este módulo como un conjunto de sensores, no una sesión espiritista. La "abducción" de Charles Sanders Peirce es simplemente la operación lógica de inferir la mejor explicación disponible a partir de datos incompletos—idéntica en principio a cómo un geofísico infiere la estructura del subsuelo a partir de lecturas sísmicas. La semiótica de Umberto Eco y los máximas conversacionales de H. Paul Grice proporcionan las *reglas de calibración* de ese sensor: definen qué cuenta como ruido, qué cuenta como señal válida y cuándo dos lecturas se contradicen. El OscillationDetector, por tanto, no detecta "fantasmas"; registra la saturación del sensor cuando dos estados de calibración mutuamente excluyentes (hipótesis A y B) alternan, indicando que la evidencia de entrada contiene información contradictoria. El límite de Miller es el tamaño del búfer de la memoria de trabajo del instrumento. Todas las salidas son valores enteros deterministas, garantizando que todo experimento sea reproducible.

- Glosario:
  - **Razonamiento abductivo / Abducción**: Inferencia a la mejor explicación. A diferencia de la deducción (cierta) o la inducción (generalización probabilística), la abducción genera causas plausibles para efectos observados.
  - **Límite de Miller (N=7)**: Frontera cognitiva propuesta por George Miller en 1956, que establece que los humanos pueden retener aproximadamente 7±2 elementos en la memoria de trabajo. Aquí, limita el número de iteraciones de inferencia.
  - **Convergencia Ockham**: Condición de parada basada en la Navaja de Ockham: si el costo explicativo no disminuye entre dos iteraciones sucesivas, se ha encontrado la explicación suficiente más simple.
  - **Oscilación (A→B→A)**: Trampa lógica donde el sistema alterna entre dos hipótesis contradictorias, señalando que el conjunto de evidencia es ambiguo o mutuamente contradictorio.
  - **Aritmética entera determinista**: Operaciones matemáticas con números enteros de resultado exacto, sin errores de redondeo ni varianza de punto flotante dependiente de la plataforma.
  - **Artefacto forense**: Cualquier objeto o estructura de datos con valor probatorio en una investigación digital.
  - **Ventana deslizante**: Búfer de tamaño fijo que examina los *N* elementos más recientes de una secuencia. Aquí, una ventana de 3 hipótesis.

**РУССКИЙ Section:**
- Что представляет собой этот модуль?
  Модуль реализует ограниченный абдуктивный механизм вывода для судебно-экспертной платформы VIGÍA. Проще говоря, он имитирует, как человек-эксперт выдвигает обоснованные предположения (гипотезы) для объяснения собранных сигналов доказательств, но не даёт процессу рассуждения продолжаться бесконечно или ходить по кругу в погоне за противоречивыми идеями. Устанавливается строгая когнитивная граница — предел Миллера (7 итераций), основанный на работе Джорджа Миллера 1956 года о ёмкости кратковременной памяти человека. Система останавливается, когда полностью объясняет доказательства, когда объяснения стабилизируются, при обнаружении логической осцилляции или при достижении жёсткого потолка итераций. Все внутренние вычисления используют детерминированную целочисленную арифметику.

- Таблицы:
  Таблица 1: Условия Останова
  | Условие | Научное Значение | Целочисленное Правило |
  |---|---|---|
  | SIGNAL_COVERAGE | Все сигналы доказательств объяснены текущим набором гипотез. | Бинарная проверка: 0 или 1. |
  | OCKHAM_CONVERGENCE | Функция стоимости стабильна между итерациями. | Разница между итерацией *n* и *n-1* точно равна 0. |
  | OSCILLATION_DETECTED | Система колеблется между гипотезами A и B. | Скользящее окно длины 3 обнаруживает паттерн A→B→A по целочисленным хешам. |
  | MILLER_LIMIT_REACHED | Когнитивный предел безопасности после 7 итераций. | Счётчик итераций == 7. Жёсткий останов. |
  | HYPOTHESIS_EXHAUSTED | В пространстве поиска не осталось кандидатов. | Очередь генератора пуста. |

  Таблица 2: Состояния Жизненного Цикла Гипотезы
  | Состояние | Значение |
  |---|---|
  | ACTIVE | В настоящее время оценивается. |
  | CONFIRMED | Принята как объясняющая доказательства. |
  | DISCARDED | Отвергнута из-за стоимости или несоответствия. |
  | SUSPENDED | Временно отложена. |

  Таблица 3: Основные Артефакты
  | Артефакт | Роль |
  |---|---|
  | EvidenceSignal | Отдельное наблюдение или измерение из судебного источника. |
  | Hypothesis | Кандидат на объяснение, связывающий один или несколько сигналов. |
  | PlannerIteration | Один полный цикл порождение → оценка → проверка. |
  | OscillationDetector | Детерминированный датчик, отслеживающий последние 3 победившие гипотезы для обнаружения A→B→A. |
  | run_bounded_planner() | Главный механизм. Оркестрирует вывод до выполнения условия останова. |

  Таблица 4: Гарантии Детерминированной Целочисленной Арифметики
  | Операция | Гарантия |
  |---|---|
  | digest() | Производит детерминированный целочисленный хеш гипотезы. Обеспечивает точное обнаружение циклов без вероятности. |
  | display_confidence_pct() | Преобразует достоверность в процент путём усечения (`int(confidence * 100)`), никогда округление. Устраняет недетерминированное представление с плавающей запятой. |

- Научная заметка:
  【Научная заметка】
  Терминология Пирса, Эко и Грайса — это не мистицизм. Воспринимайте этот модуль как сенсорную решётку, а не спиритический сеанс. «Абдукция» Чарльза Сандерса Пирса — это просто логическая операция вывода наилучшего доступного объяснения из неполных данных, идентичная по принципу тому, как геофизик выводит структуру недр по сейсмическим показаниям датчиков. Семиотика Умберто Эко и разговорные максимы Г. Пола Грайса задают *правила калибровки* этого датчика: они определяют, что считается шумом, что — действительным сигналом, и когда два показания противоречат друг другу. Следовательно, OscillationDetector обнаруживает не «привидений», а регистрирует насыщение датчика, когда два взаимоисключающих состояния калибровки (гипотезы A и B) чередуются, указывая на то, что входные доказательства содержат противоречивую информацию. Предел Миллера — это размер буфера оперативной памяти прибора. Все выходные значения являются детерминированными целыми числами, что гарантирует воспроизводимость каждого эксперимента.

- Глоссарий:
  - **Абдуктивное рассуждение / Абдукция**: Вывод наилучшего объяснения. В отличие от дедукции (достоверный) или индукции (вероятностное обобщение), абдукция порождает правдоподобные причины наблюдаемых эффектов.
  - **Предел Миллера (N=7)**: Когнитивная граница, предложенная Джорджем Миллером в 1956 году: человек может удерживать примерно 7±2 элемента в рабочей памяти. Здесь она ограничивает число итераций вывода.
  - **Сходимость Оккама**: Условие останова, основанное на Бритве Оккама: если объяснительная стоимость не уменьшается между двумя последовательными итерациями, найдено простейшее достаточное объяснение.
  - **Осцилляция (A→B→A)**: Логическая ловушка, при которой система колеблется между двумя противоречивыми гипотезами, сигнализируя о неоднозначности или взаимном противоречии набора доказательств.
  - **Детерминированная целочисленная арифметика**: Математические операции с целыми числами, дающие точный результат без ошибок округления или платформенно-зависимой вариативности чисел с плавающей запятой.
  - **Судебный артефакт (取证工件)**: Любой объект или структура данных, несущая доказательственное значение в цифровом расследовании.
  - **Скользящее окно**: Буфер фиксированного размера, изучающий последние *N* элементов последовательности. Здесь — окно из 3 гипотез.

**中文 Section:**
- 这是什么模块？
  本模块为 VIGÍA 取证分析框架实现了一个有界的溯因推理引擎。通俗地说，它模拟人类专家如何根据已收集的证据信号提出有根据的猜测（假设），但防止推理过程无限运行或在相互矛盾的观点中循环打转。它强制执行一个严格的认知边界，即米勒极限（7 次迭代），该极限源自 George Miller 1956 年关于人类短时记忆容量的研究。当系统完全解释所有证据、解释趋于稳定、检测到逻辑振荡，或达到硬性的迭代上限时，系统将停止。所有内部计算均使用确定性整数运算，以保证结果可复现。

- 表格：
  表1：停止条件（终止原因）
  | 条件 | 科学含义 | 整数规则 |
  |---|---|---|
  | SIGNAL_COVERAGE | 所有证据信号均已被当前假设集合解释。 | 二元检查：0 或 1（已覆盖/未覆盖）。 |
  | OCKHAM_CONVERGENCE | 迭代之间的成本函数稳定，未增加新的复杂性。 | 第 *n* 次与第 *n-1* 次迭代的差值精确为 0。 |
  | OSCILLATION_DETECTED | 系统在假设 A 与假设 B 之间来回翻转。 | 长度为 3 的滑动窗口通过整数哈希检测 A→B→A 模式。 |
  | MILLER_LIMIT_REACHED | 经过 7 次迭代后触发认知安全极限。 | 迭代计数器 == 7。硬性停止。 |
  | HYPOTHESIS_EXHAUSTED | 搜索空间中不再有候选解释。 | 生成器队列空。 |

  表2：假设生命周期状态
  | 状态 | 含义 |
  |---|---|
  | ACTIVE | 当前正在评估中。 |
  | CONFIRMED | 已被接受为对证据的解释。 |
  | DISCARDED | 因成本或不一致而被拒绝。 |
  | SUSPENDED | 暂时搁置（例如等待新证据）。 |

  表3：核心取证工件
  | 取证工件 | 作用 |
  |---|---|
  | EvidenceSignal | 来自取证源的单一观测或测量。 |
  | Hypothesis | 将一条或多条信号关联起来的候选解释。 |
  | PlannerIteration | 一个完整的“生成 → 评分 → 评估”周期。 |
  | OscillationDetector | 确定性传感器，监视最近 3 个获胜假设以检测 A→B→A。 |
  | run_bounded_planner() | 主引擎。协调推理过程直至满足停止条件。 |

  表4：确定性整数运算保障
  | 运算 | 保障 |
  |---|---|
  | digest() | 生成假设的确定性整数哈希。实现精确的循环检测，不依赖概率。 |
  | display_confidence_pct() | 通过截断（`int(confidence * 100)`）将置信度转换为百分比，绝不使用四舍五入。消除非确定性的浮点数展示。 |

- 科学说明：
  【科学说明】
  皮尔斯（Peirce）、艾柯（Eco）与格赖斯（Grice）的术语并非神秘主义。请将此模块视为传感器阵列，而非降神会。查尔斯·桑德斯·皮尔斯的“溯因”（abduction）仅仅是从不完整数据中推断最佳可用解释的逻辑操作——其原理与地球物理学家根据地震传感器读数推断地下结构完全相同。艾柯的符号学与格赖斯的会话准则为该传感器提供了*校准规则*：它们定义了何为噪声、何为有效信号，以及何时两份读数相互矛盾。因此，OscillationDetector 并非在探测“幽灵”；它是在记录传感器饱和——当两种互斥的校准状态（假设 A 与假设 B）交替出现时，表明输入证据包含矛盾信息。米勒极限即该仪器工作记忆缓冲区的容量。所有输出均为确定性整数值，确保每次实验皆可复现。

- 术语表：
  - **溯因推理 / 溯因（Abduction）**：推断最佳解释的过程。与演绎（确定性）和归纳（概率性概括）不同，溯因为观察到的效应生成合理的成因。
  - **米勒极限（N=7）**：George Miller 于 1956 年提出的认知边界，指出人类工作记忆大约可容纳 7±2 个组块。此处用于限制推理迭代次数。
  - **奥卡姆收敛（Ockham convergence）**：基于奥卡姆剃刀的停止条件：若连续两次迭代的解释成本不再下降，则表明已找到最简充分解释。
  - **振荡（A→B→A）**：逻辑陷阱，系统在两种矛盾假设之间交替，表明证据集存在歧义或自相矛盾。
  - **确定性整数运算**：使用整数进行结果精确的数学运算，不存在舍入误差或平台依赖的浮点变异。
  - **取证工件**：在数字调查中具有证明价值的任何对象或数据结构。
  - **滑动窗口**：固定大小的缓冲区，检查序列中最近的 *N* 个元素。此处为长度为 3 的假设窗口。

I need to ensure I do not use floating-point math explanations. I must emphasize deterministic integer arithmetic. The prompt says "You NEVER use floating-point math explanations for deterministic systems." So when discussing confidence, I should mention it's handled as integer percentages via truncation, not rounded floats.

Also, I need to make sure the Chinese terms are correct:
- 艾柯 (Eco) ✓
- 格赖斯 (Grice) ✓
- 取证工件 (not 制品) ✓
- 逻辑断裂? Wait, the prompt says "逻辑断裂 (not 裂缝)". But where does "逻辑断裂" appear? Looking at the module description, it mentions "oscilación" and "ABSTAIN", but not "rupture" or "break". The user requirement says: "Chinese translations must use: ... 逻辑断裂 (not 裂缝)". This might be a preemptive instruction for if those terms appear. I should incorporate "逻辑断裂" somewhere appropriate, perhaps in the glossary or scientific note as a translation for "logical rupture/break" or in the context of contradictory evidence causing a break in logic. The module is about oscillation detection, which implies a logical break. I can mention it in the Chinese glossary for "Oscillation" or "Contradictory evidence". Let's add a note: "当证据自相矛盾时，系统内部会出现逻辑断裂，触发 ABSTAIN。" Or in the glossary entry for Oscillation, mention it leads to 逻辑断裂. I will include it naturally.

Let's refine the Chinese text to include 逻辑断裂.
In the Chinese Scientific Note: "...表明输入证据包含矛盾信息，导致**逻辑断裂**。" Or in the Oscillation definition: "...系统在两种矛盾假设之间交替，表明证据集存在歧义或**逻辑断裂**。" Let's put it in the Oscillation glossary entry.

Also, I need to check the Russian names: Peirce is Пирс, Eco is Эко, Grice is Грайс. That's fine.

The user wants the document to be thorough but concise. I should avoid Python code snippets since the audience doesn't know Python, but describe the module's scientific function. I can mention the names of classes/functions as conceptual artifacts.

I should make sure to include the license line. I'll put it at the very end of the document.

One final check: The module path is `vigia/core/peirceplanner_bounded.py`. I should probably mention this as the document title or identifier.

Let's assemble the final markdown. I'll use headers.

Structure:
# Module Documentation: `vigia/core/peirceplanner_bounded.py`
*(Maybe a subtitle)*

## ENGLISH
### What Is This Module?
...
### Key Concepts
Tables...
### 【Scientific Note】
...
### Glossary
...
---

## ESPAÑOL
### ¿Qué es este módulo?
...
### Conceptos Clave
...
### 【Nota Científica】
...
### Glosario
...

## РУССКИЙ
...
## 中文
...

Then license line.

Wait, the user said "Each section must include: ... A 【科学说明】/【Scientific Note】 box...". So each language section needs its own box with the appropriate title. I'll use 【Scientific Note】 for EN, 【Nota Científica】 for ES, 【Научная заметка】 for RU, and 【科学说明】 for ZH.

Also, the user said "You always write in 4 languages: ENGLISH, ESPAÑOL, РУССКИЙ, 中文." So the sections should be clearly demarcated.

I need to be careful with formatting. I'll use blockquotes or admonition-style boxes for the scientific note. Since it's markdown, I'll use `> **【Scientific Note】**` or just bold headers. The user asked for a box. I'll use a blockquote (`>`) to simulate a box, or just a bold header. A blockquote is cleaner in markdown.

Example:
> **【Scientific Note】**
> The terminology...

Let's ensure all tables are properly formatted.

One more thing: The prompt says "hypothesis_generator: función que genera nuevas hipó" and lists functions like digest(), display_confidence_pct(), etc. I should mention hypothesis_generator in the tables or text. It's the input function that feeds candidates.

Also, the constants like ACTIVE, CONFIRMED etc. are in the HypothesisStatus class. I should explain that.

In the EN section, I used "Forensic artifact (取证工件)" in the glossary. That's fine.

Double check: "You NEVER use floating-point math explanations for deterministic systems." So when I talk about display_confidence_pct, I say it uses integer truncation, not rounding. I should not say "confidence is a float between 0 and 1". Instead, I should say "confidence is represented internally as a ratio, but reported as a deterministic integer percentage via truncation." Or simply "avoids floating-point representation by truncating to an integer percentage." This is good.

Let's write it out. I'll be thorough but keep it concise. I'll avoid Python syntax like `def` or class definitions. I'll describe them as "components".

Let's finalize the content.

**ENGLISH:**
- What Is This Module?
  This module implements a bounded abductive inference engine for the VIGÍA forensic analysis framework. It replicates, in algorithmic form, the cognitive workflow of a human forensic examiner who must explain a set of evidence signals by proposing and testing hypotheses. Unlike an unconstrained reasoning system, this engine incorporates a hard cognitive boundary—the Miller limit (N = 7 iterations)—to prevent infinite oscillation between contradictory explanations or overfitting to noise. The system halts when it achieves complete signal coverage, when explanatory cost stabilizes (Ockham convergence), when it detects an A→B→A oscillation pattern, or when it reaches the seventh iteration. Every internal operation relies
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
