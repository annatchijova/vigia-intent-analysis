<!--
VIGIA Academic Documentation
Module: 6ae41267
Batch ID: vigia-doc-0145-6ae41267
Generated: 2026-05-20T14:56:47.875708+00:00
-->

ENGLISH:
Title: Module Documentation: `vigia/signal_quality_gate.py`

What Is This Module?
Plain language for non-Python scientists. It's a quality control filter. Before the VIGÍA system declares a digital artifact (取证工件) as suspicious/ACCEPT (guilty), this gate checks if the forensic signals are strong enough. It prevents weak, noisy, or redundant clues from causing false positives. It enforces deterministic integer arithmetic rules to ensure reproducibility.

Key Concepts:
Table 1: The Five Quality Checks
| Check | Rule | Scientific Rationale |
|---|---|---|
| Tool Diversity | ≥ 2 distinct tools | Avoid single-source bias |
| Strong Signal | At least one signal with strength index ≥ 2 (deterministic integer threshold) | One strong ingredient outweighs many weak ones |
| Independence | Not all signals from same tool | Correlated sensors produce echo, not evidence |
| Variability | Z-scores not identical | Identical values suggest duplication or synthetic noise |
| Noise Inflation | Reject many weak + few strong mixes | Prevents accumulation of meaningless readings |

Table 2: Core Components
| Component | Role |
|---|---|
| `SignalQualityGate` | The taster/catador. Evaluates the batch of signals. |
| `QualityGateResult` | Verdict container: PASS, FAIL, or specific rejection reason. |
| `evaluate()` | Main deterministic function applying all checks in integer arithmetic. |
| `detect_noise_inflation()` | Identifies and corrects over-confidence from redundant weak signals. |

Constants table:
| Constant | Purpose |
|---|---|
| `MIN_TOOLS_REQUIRED` | Minimum integer count of distinct forensic tools (≥2). |
| `MIN_STRONG_SIGNALS` | Minimum integer count of strong signals required. |
| `Z_STRONG` | Rational threshold (2/1) for a signal to be considered strong. |
| `MIN_Z_VARIANCE` | Minimum integer-scaled dispersion allowed among signal scores. |
| `MAX_SAME_TOOL_RATIO` | Maximum integer ratio of signals allowed from a single source. |

Glossary:
- **Digital Forensic Artifact (取证工件)**: A discrete object extracted from a digital environment (e.g., a log entry, memory fragment) that may serve as evidence.
- **Signal**: A measurable indicator produced by a forensic tool suggesting an anomaly.
- **Z-score / Strength Index**: A standardized deterministic metric. Here treated as an integer-scaled or rational value for reproducible threshold comparison; never a floating-point approximation.
- **Firstness (Peirce)**: The mode of being of a raw, uninterpreted quality—like an uncalibrated sensor voltage. In this module, a weak signal in isolation.
- **Thirdness (Peirce)**: The mode of law, habit, or mediated interpretation—like a validated pattern recognized after repeated calibrated readings. Here, a stable, actionable forensic hypothesis.
- **Noise Inflation**: The erroneous increase in confidence caused by counting many correlated weak detections as independent evidence.
- **Deterministic Integer Arithmetic**: A calculation method using whole numbers and exact rational bounds, ensuring every execution on identical input yields the exact same verdict.

Scientific Note:
> 【Scientific Note】
> The terminology of Peirce, Eco, and Grice is not mysticism. These are formal models of signification and communication. Think of a sensor network: **Firstness** is the raw voltage from a thermocouple before calibration; **Thirdness** is the confirmed temperature trend after cross-referencing multiple calibrated sensors. **艾柯 (Eco)**’s semiotics provides the codebook mapping voltages to states; **格赖斯 (Grice)**’s maxims ensure sensors do not "lie" by violating quantity or quality. The culinary metaphor in this module ("many mediocre ingredients do not make an excellent dish") is an intuitive parallel: a single high-fidelity sensor reading is more epistemically valuable than a thousand noisy, uncalibrated blips.

ESPAÑOL:
What Is This Module?
Módulo de control de calidad. Evita que VIGÍA emita un veredicto de ACEPTAR (culpable) cuando las señales forenses carecen de calidad suficiente. Actúa como un catador que prueba cada ingrediente antes de servir el plato.

Key Concepts: (in Spanish)
Tabla 1: Las Cinco Pruebas de Calidad
| Prueba | Regla | Fundamento Científico |
|---|---|---|
| Diversidad de herramientas | ≥ 2 herramientas distintas | Evita el sesgo de fuente única |
| Señal fuerte | Al menos una señal con índice de fuerza ≥ 2 (umbral entero determinista) | Un ingrediente fuerte supera a muchos débiles |
| Independencia | No todas las señales de la misma herramienta | Sensores correlacionados generan eco, no evidencia |
| Variabilidad | Los z-scores no son idénticos | Valores idénticos sugieren duplicación o ruido sintético |
| Inflación por ruido | Rechaza la mezcla "muchas débiles + pocas fuertes" | Evita la acumulación de lecturas sin sentido |

Tabla 2: Componentes Principales
| Componente | Rol |
|---|---|
| `SignalQualityGate` | El catador. Evalúa el lote de señales. |
| `QualityGateResult` | Contenedor del veredicto: PASS, FAIL o razón de rechazo. |
| `evaluate()` | Función determinista principal que aplica todas las pruebas con aritmética entera. |
| `detect_noise_inflation()` | Identifica y corrige la sobreconfianza por señales débiles redundantes. |

Constantes:
| Constante | Propósito |
|---|---|
| `MIN_TOOLS_REQUIRED` | Conteo entero mínimo de herramientas forenses distintas (≥2). |
| `MIN_STRONG_SIGNALS` | Conteo entero mínimo de señales fuertes requeridas. |
| `Z_STRONG` | Umbral racional (2/1) para considerar una señal fuerte. |
| `MIN_Z_VARIANCE` | Dispersión mínima escalada en enteros permitida entre puntuaciones. |
| `MAX_SAME_TOOL_RATIO` | Razón entera máxima de señales permitidas de una sola fuente. |

Glosario:
- **Artefacto forense digital (取证工件)**: Objeto discreto extraído de un entorno digital que puede servir como evidencia.
- **Señal**: Indicador mensurable producido por una herramienta forense que sugiere una anomalía.
- **Índice Z / Índice de fuerza**: Métrica determinista estandarizada. Aquí tratada como valor entero o racional para comparaciones reproducibles; nunca como aproximación de punto flotante.
- **Firstness (Peirce)**: Modo del ser de una cualidad cruda e interpretada—como el voltaje bruto de un sensor sin calibrar. En este módulo, una señal débil aislada.
- **Thirdness (Peirce)**: Modo de la ley, hábito o interpretación mediada—como un patrón validado tras lecturas calibradas repetidas. Aquí, una hipótesis forense estable y accionable.
- **Inflación por ruido**: Incremento erróneo de confianza causado por contar muchas detecciones débiles correlacionadas como evidencia independiente.
- **Aritmética entera determinista**: Método de cálculo con números enteros y límites racionales exactos, garantizando que cada ejecución con idénticas entradas produzca el mismo veredicto.

Nota Científica:
> 【Scientific Note】
> La terminología de Peirce, Eco y Grice no es misticismo. Son modelos formales de significación y comunicación. Piense en una red de sensores: la **Firstness** es el voltaje crudo de un termopar antes de la calibración; la **Thirdness** es la tendencia de temperatura confirmada tras contrastar múltiples sensores calibrados. La semiótica de **艾柯 (Eco)** proporciona el código que mapea voltajes a estados; los máximos de **格赖斯 (Grice)** aseguran que los sensores no "mientan" violando cantidad o calidad. La metáfora culinaria de este módulo ("muchos ingredientes mediocres no hacen un plato excelente") es un paralelo intuitivo: una sola lectura de sensor de alta fidelidad es epistemológicamente más valiosa que mil señales ruidosas y no calibradas.

РУССКИЙ:
What Is This Module? -> Что это за модуль?
Это модуль контроля качества. Предотвращает выдачу системой VIGÍA вердикта ACCEPT (виновен) в случаях, когда цифровые сигналы недостаточно качественны. Действует как дегустатор, пробуя каждый ингредиент перед подачей блюда.

Key Concepts:
Таблица 1: Пять проверок качества
| Проверка | Правило | Научное обоснование |
|---|---|---|
| Разнообразие инструментов | ≥ 2 различных инструмента | Исключение систематической погрешности одного источника |
| Сильный сигнал | Хотя бы один сигнал с индексом силы ≥ 2 (детерминированный целочисленный порог) | Один сильный ингредиент важнее множества слабых |
| Независимость | Не все сигналы от одного инструмента | Коррелированные датчики дают эхо, а не доказательство |
| Изменчивость | Z-оценки не идентичны | Идентичные значения указывают на дублирование или синтетический шум |
| Инфляция шума | Отклонение комбинации «много слабых + мало сильных» | Предотвращение накопления бессмысленных показаний |

Таблица 2: Основные компоненты
| Компонент | Роль |
|---|---|
| `SignalQualityGate` | Дегустатор. Оценивает партию сигналов. |
| `QualityGateResult` | Контейнер вердикта: PASS, FAIL или конкретная причина отказа. |
| `evaluate()` | Главная детерминированная функция, применяющая все проверки с помощью целочисленной арифметики. |
| `detect_noise_inflation()` | Выявляет и корректирует избыточную уверенность, вызванную избыточными слабыми сигналами. |

Константы:
| Константа | Назначение |
|---|---|
| `MIN_TOOLS_REQUIRED` | Минимальное целое число различных криминалистических инструментов (≥2). |
| `MIN_STRONG_SIGNALS` | Минимальное целое число требуемых сильных сигналов. |
| `Z_STRONG` | Рациональный порог (2/1) для классификации сигнала как сильного. |
| `MIN_Z_VARIANCE` | Минимальная допустимая целочисленная дисперсия между оценками сигналов. |
| `MAX_SAME_TOOL_RATIO` | Максимальное целочисленное соотношение сигналов, допустимое от одного источника. |

Глоссарий:
- **Цифровой криминалистический артефакт (取证工件)**: Дискретный объект, извлечённый из цифровой среды и пригодный в качестве доказательства.
- **Сигнал**: Измеримый индикатор, выдаваемый криминалистическим инструментом и указывающий на аномалию.
- **Z-оценка / индекс силы**: Стандартизированная детерминированная метрика. Здесь используется как целочисленная или рациональная величина для воспроизводимого сравнения с порогом; никак не приближённое значение с плавающей запятой.
- **Firstness (Пирс)**: Мода бытия сырой, неинтерпретированной качественности — как некалиброванное напряжение датчика. В данном модуле — изолированный слабый сигнал.
- **Thirdness (Пирс)**: Мода закона, привычки или опосредованной интерпретации — как подтверждённая тенденция после многократных калиброванных измерений. Здесь — устойчивая криминалистическая гипотеза, пригодная для действий.
- **Инфляция шума**: Ошибочное повышение уверенности, вызванное подсчётом множества коррелированных слабых обнаружений как независимых доказательств.
- **Детерминированная целочисленная арифметика**: Метод вычисления с использованием целых чисел и точных рациональных границ, гарантирующий, что при идентичных входных данных каждый запуск даст один и тот же вердикт.

Научная заметка:
> 【Scientific Note】
> Терминология Пирса, Эко и Грайса — это не мистицизм. Это формальные модели знаковости и коммуникации. Представьте сеть датчиков: **Firstness** — это сырое напряжение термопары до калибровки; **Thirdness** — подтверждённая тенденция температуры после сверки нескольких откалиброванных датчиков. Семиотика **艾柯 (Eco)** задаёт кодовую таблицу, сопоставляющую напряжения состояниям; максимы **格赖斯 (Grice)** гарантируют, что датчики не «лгут», нарушая количество или качество информации. Кулинарная метафора данного модуля («множество посредственных ингредиентов не делают блюдо отличным») — это интуитивная аналогия: одно показание высокоточного датчика эпистемологически ценнее тысячи шумных, некалиброванных всплесков.

中文:
What Is This Module? -> 本模块是什么？
本模块是一个质量控制闸门。它防止 VIGÍA 系统在信号质量不足时发出 ACCEPT（有罪）判决。如同一名品鉴师在上菜前先检验每一种原料，该模块在采纳取证结论前检验所有数字信号的质量。

Key Concepts:
表1：五项质量检验
| 检验项 | 规则 | 科学依据 |
|---|---|---|
| 工具多样性 | 至少使用 2 种不同工具 | 避免单一来源偏差 |
| 强信号 | 至少存在一条强度指数 ≥ 2 的信号（确定性整数阈值） | 一个优质原料远胜多个劣质原料 |
| 独立性 | 并非所有信号都来自同一工具 | 相关传感器产生的是回声，而非证据 |
| 可变性 | Z 分数互不相同 | 数值完全相同意味着复制或合成噪声 |
| 噪声膨胀检测 | 拒绝“多弱少强”的混合模式 | 防止无意义读数的累积 |

表2：核心组件
| 组件 | 作用 |
|---|---|
| `SignalQualityGate` | 信号品鉴师。对整批信号进行质量评估。 |
| `QualityGateResult` | 判决容器：通过、未通过或具体拒绝原因。 |
| `evaluate()` | 主确定性函数，使用整数运算依次执行全部检验。 |
| `detect_noise_inflation()` | 识别并校正由冗余弱信号导致的过度自信。 |

常量配置：
| 常量 | 用途 |
|---|---|
| `MIN_TOOLS_REQUIRED` | 不同取证工具的最小整数数量（≥2）。 |
| `MIN_STRONG_SIGNALS` | 所需强信号的最小整数计数。 |
| `Z_STRONG` | 判定强信号的有理数阈值（2/1）。 |
| `MIN_Z_VARIANCE` | 信号分数之间允许的最小整数级离散度。 |
| `MAX_SAME_TOOL_RATIO` | 单一来源信号允许的最大整数比例。 |

术语表：
- **取证工件（Digital Forensic Artifact）**：从数字环境中提取的、可作为证据的离散对象（如日志条目、内存片段）。
- **信号（Signal）**：取证工具生成的可度量异常指标。
- **Z 分数 / 强度指数（Z-score / Strength Index）**：标准化的确定性度量指标。本文档中将其视为整数或有理数进行比较，以实现可复现的阈值判定；绝非浮点近似值。
- **第一性（Firstness，皮尔斯）**：一种未经解释的原始质性的存在模式——如同未经校准的传感器电压。在本模块中，指孤立的弱信号。
- **第三性（Thirdness，皮尔斯）**：规律、习惯或中介性解释的存在模式——如同经过多次校准读数后确认的模式。在本模块中，指稳定且可操作的取证假设。
- **噪声膨胀（Noise Inflation）**：将大量相关弱检测误判为独立证据，从而导致置信度错误提升的现象。
- **确定性整数运算（Deterministic Integer Arithmetic）**：使用整数和精确有理数边界的计算方法，确保在相同输入下每次执行均产生完全相同的判决。

科学说明：
> 【科学说明】
> 皮尔斯、艾柯与格赖斯的术语并非神秘主义，而是关于符号过程与信息交流的形式模型。请设想一套传感器网络：**第一性**是热电偶在未经校准前输出的原始电压；**第三性**则是通过多台已校准传感器交叉验证后确认的温度趋势。艾柯的符号学提供了将电压映射为状态的编码手册；格赖斯的合作原则确保传感器不会通过违反“量”或“质”的准则来“撒谎”。本模块采用的烹饪隐喻（“许多平庸的原料做不出一道佳肴”）是一种直观的类比：一条高保真传感器的读数在认识论上胜过一千条 noisy、未经校准的杂波。

Need to ensure Chinese translations use specified terms: 艾柯 (not Eco), 格赖斯 (not Grice), 取证工件 (not 制品), 逻辑断裂 (not 裂缝). Wait, the user said "logic断裂" or "逻辑断裂"? They said: "Chinese translations must use: 艾柯 (not Eco), 格赖斯 (not Grice), 取证工件 (not 制品), 逻辑断裂 (not 裂缝)". I don't see "逻辑断裂" used in my draft. But if I encounter it, use 逻辑断裂. I haven't used it, but it's fine. I should make sure I don't use 制品.

Also, the user said "Principio: Muchas Firstnesses (señales débiles) no hac" at the end of the prompt (cut off). I should probably not worry about the cut-off.

Double-check: Do NOT use floating-point math explanations. I used "Z-score" but explained as integer-scaled or rational. Need to make sure I don't mention "floating point", "float", "IEEE 754", "decimal approximation", etc. The threshold z >= 2.0 should be described as a rational boundary 2/1 or integer threshold.

Also, need to be thorough but concise. The document will be long due to 4 languages, but each section should be concise.

Let's refine the English text to be more academic and suitable for scientists not knowing Python.

In "What Is This Module?", avoid Python jargon like "class", "function". Instead say "component", "procedure". But the requirement says each section must include key concepts with tables. The tables can mention the component names (which are Python names) but explain them plainly.

Scientific Note must be titled 【Scientific Note】 in EN/ES/RU? The prompt says: A 【科学说明】/【Scientific Note】 box. So English uses 【Scientific Note】, Spanish maybe 【Nota Científica】 or 【Scientific Note】? The prompt says "A 【科学说明】/【Scientific Note】 box". I think it's acceptable to localize the box title or keep it consistent. I'll use:
- EN: 【Scientific Note】
- ES: 【Nota Científica】 or 【Scientific Note】? I'll use 【Nota Científica】 to be natural, but maybe keep the bracket style.
- RU: 【Научное примечание】
- ZH: 【科学说明】

The prompt specifically says "A 【科学说明】/【Scientific Note】 box". To be safe, I'll use the exact bracket titles as specified for English and Chinese, and localize for Spanish/Russian but keep brackets.

Let's ensure the sensor analogy is clear.

Sensor analogy draft:
- Peirce's Firstness: raw sensor voltage before calibration (pure quality, no interpretation).
- Peirce's Thirdness: confirmed pattern after cross-referencing multiple calibrated sensors (law/habit).
- Eco: codebook mapping sensor voltages to semantic states.
- Grice: maxims ensuring sensors don't lie by violating quantity or quality (i.e., cooperative communication).
This is good.

Now, check the culinary principle. The module uses "culinary principle". In the scientific note, we mention it. That's fine.

Check terminology in Chinese:
- 艾柯: used.
- 格赖斯: used.
- 取证工件: used.
- 逻辑断裂: not used, but if I mention "gap", use 逻辑断裂. I don't think I need it.

Check license line: exact text at the end.

Check formatting: Markdown.

Let's refine the English section to be more polished.

ENGLISH:

## ENGLISH

### Module Overview
`vigia/signal_quality_gate.py`

#### What Is This Module?
This module is a deterministic quality-control gate for digital forensic analysis. Before the VIGÍA system renders a verdict of ACCEPT (indicating a suspect or guilty artifact), this gate verifies that the underlying forensic signals possess sufficient epistemic strength. It blocks verdicts that rely on weak, redundant, or noisy indicators. All threshold comparisons are performed via deterministic integer arithmetic or exact rational boundaries, ensuring fully reproducible results across executions.

#### Key Concepts

**Table 1. The Five Epistemic Checks**
| Check | Deterministic Rule | Scientific Rationale |
|---|---|---|
| Tool Diversity | Count of distinct tools ≥ `MIN_TOOLS_REQUIRED` (integer ≥ 2) | Eliminates single-source bias; a lone instrument cannot confirm a pattern. |
| Strong Signal Existence | At least one signal exceeds the rational threshold `Z_STRONG` (2/1) | A single high-fidelity reading outweighs an ensemble of weak blips. |
| Source Independence | Ratio of signals from any single tool ≤ `MAX_SAME_TOOL_RATIO` | Correlated sensors produce echo, not independent evidence. |
| Score Variability | Dispersion among signal scores ≥ `MIN_Z_VARIANCE` (integer-scaled) | Identical scores suggest duplication or synthetic artifacts. |
| Noise-Inflation Guard | `detect_noise_inflation()` rejects many-weak/few-strong mixtures | Prevents the accumulation of meaningless readings into false confidence. |

**Table 2. Core Procedures and Data Structures**
| Name | Role |
|---|---|
| `SignalQualityGate` | The taster (*catador*). Orchestrates the evaluation of a signal batch. |
| `QualityGateResult` | Verdict container: PASS, FAIL, or a specific rejection reason. |
| `evaluate()` | The main deterministic procedure; applies all checks using integer arithmetic. |
| `detect_noise_inflation()` | Corrects over-confidence caused by redundant weak detections. |

**Table 3. Configuration Boundaries**
| Constant | Type | Purpose |
|---|---|---|
| `MIN_TOOLS_REQUIRED` | Integer | Minimum number of distinct forensic instruments required. |
| `MIN_STRONG_SIGNALS` | Integer | Minimum count of strong signals required for acceptance. |
| `Z_STRONG` | Rational | Exact strength boundary (2/1); signals must meet or exceed this index. |
| `MIN_Z_VARIANCE` | Integer-scaled | Minimum allowable diversity among signal indices. |
| `MAX_SAME_TOOL_RATIO` | Integer ratio | Ceiling for concentration of signals from one tool. |

#### Glossary
- **Digital Forensic Artifact (取证工件)**: A discrete object extracted from a digital environment (e.g., a log entry, a memory page fragment) that may serve as evidence.
- **Signal**: A measurable indicator generated by a forensic instrument, suggesting the presence of an anomaly.
- **Strength Index (Z-score)**: A standardized deterministic metric. In this system it is treated as an integer-comparable score against exact rational thresholds; it is never handled as an approximate floating-point value.
- **Firstness (Peirce)**: The mode of being of a raw, uninterpreted quality—analogous to an uncalibrated sensor voltage. Here, an isolated weak signal lacking context.
- **Thirdness (Peirce)**: The mode of law, habit, or mediated interpretation—analogous to a validated trend after repeated calibrated observations. Here, a stable, actionable forensic hypothesis.
- **Noise Inflation**: The erroneous increase in confidence that occurs when many correlated weak detections are treated as independent pieces of evidence.
- **Deterministic Integer Arithmetic**: A computational regime employing whole numbers and exact rational bounds, guaranteeing that identical inputs always yield the identical verdict.

#### 【Scientific Note】
> The terminology of Peirce, Eco, and Grice is not mysticism; it constitutes a formal taxonomy of signification and communication. Consider a distributed sensor network: **Firstness** is the raw millivolt reading from a thermocouple before calibration—pure quality without interpretation. **Thirdness** is the confirmed temperature trend that emerges only after cross-referencing multiple calibrated sensors, establishing a reliable habit or law. **艾柯 (Eco)** provides the codebook that maps raw voltages to semantic states (icon, index, symbol), while **格赖斯 (Grice)** supplies the cooperative maxims that prevent sensors from violating quantity or quality—essentially, from "lying." The culinary metaphor embedded in this module (“many mediocre ingredients do not produce an excellent dish”) is an intuitive epistemic parallel: one high-fidelity sensor reading is scientifically more valuable than a thousand uncalibrated, noisy blips.

ESPAÑOL:

## ESPAÑOL

### Visión general del módulo
`vigia/signal_quality_gate.py`

#### ¿Qué es este módulo?
Este módulo es una compuerta de control de calidad determinista para el análisis forense digital. Antes de que el sistema VIGÍA emita un veredicto de ACCEPT (culpable), esta compuerta verifica que las señales forenses subyacentes posean suficiente fuerza epistémica. Bloquea veredictos fundados en indicadores débiles, redundantes o ruidosos. Todas las comparaciones de umbral se realizan mediante aritmética entera determinista o límites racionales exactos, garantizando resultados plenamente reproducibles.

#### Conceptos clave

**Tabla 1. Las cinco comprobaciones epistémicas**
| Comprobación | Regla determinista | Fundamento científico |
|---|---|---|
| Diversidad de herramientas | Cantidad de herramientas distintas ≥ `MIN_TOOLS_REQUIRED` (entero ≥ 2) | Elimina el sesgo de fuente única; un solo instrumento no puede confirmar un patrón. |
| Existencia de señal fuerte | Al menos una señal supera el umbral racional `Z_STRONG` (2/1) | Una sola lectura de alta fidelidad pesa más que un conjunto de señales débiles. |
| Independencia de fuente | Proporción de señales de una misma herramienta ≤ `MAX_SAME_TOOL_RATIO` | Sensores correlacionados generan eco, no evidencia independiente. |
| Variabilidad de puntuaciones | Dispersión entre puntuaciones ≥ `MIN_Z_VARIANCE` (escalada en enteros) | Puntuaciones idénticas sugieren duplicación o artefactos sintéticos. |
| Protección contra inflación por ruido | `detect_noise_inflation()` rechaza mezclas "muchas débiles / pocas fuertes" | Evita que lecturas sin sentido se acumulen en confianza falsa. |

**Tabla 2. Procedimientos y estructuras principales**
| Nombre | Rol |
|---|---|
| `SignalQualityGate` | El catador. Orquesta la evaluación de un lote de señales. |
| `QualityGateResult` | Contenedor del veredicto: PASS, FAIL o razón específica de rechazo. |
| `evaluate()` | Procedimiento determinista principal; aplica todas las pruebas con aritmética entera. |
| `detect_noise_inflation()` | Corrige la sobreconfianza causada por detecciones débiles redundantes. |

**Tabla 3. Límites de configuración**
| Constante | Tipo | Propósito |
|---|---|---|
| `MIN_TOOLS_REQUIRED` | Entero | Número mínimo de instrumentos forenses distintos requeridos. |
| `MIN_STRONG_SIGNALS` | Entero | Cantidad mínima de señales fuertes exigidas para la aceptación. |
| `Z_STRONG` | Racional | Límite exacto de fuerza (2/1); las señales deben alcanzar o superar este índice. |
| `MIN_Z_VARIANCE` | Escalado en enteros | Diversidad mínima permisible entre los índices de las señales. |
| `MAX_SAME_TOOL_RATIO` | Razón entera | Tope de concentración de señales procedentes de una sola herramienta. |

#### Glosario
- **Artefacto forense digital (取证工件)**: Objeto discreto extraído de un entorno digital (p. ej., una entrada de registro, un fragmento de página de memoria) que puede servir como evidencia.
- **Señal**: Indicador mensurable generado por un instrumento forense que sugiere la presencia de una anomalía.
- **Índice de fuerza (z-score)**: Métrica determinista estandarizada. En este sistema se trata como una puntuación comparable con enteros respecto a umbrales racionales exactos; nunca se maneja como un valor de punto flotante aproximado.
- **Firstness (Peirce)**: Modo del ser de una cualidad cruda e interpretada—análogo al voltaje crudo de un sensor sin calibrar. Aquí, una señal débil aislada carente de contexto.
- **Thirdness (Peirce)**: Modo de la ley, el hábito o la interpretación mediada—análogo a una tendencia validada tras observaciones calibradas repetidas. Aquí, una hipótesis forense estable y accionable.
- **Inflación por ruido**: Incremento erróneo de la confianza que ocurre cuando muchas detecciones débiles correlacionadas se tratan como evidencia independ
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
