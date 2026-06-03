<!--
VIGIA Academic Documentation
Module: 0b473fc1
Batch ID: vigia-doc-0061-0b473fc1
Generated: 2026-05-20T14:56:47.857613+00:00
-->

ENGLISH:
- Title: VIGÍA Likelihood Engine — Core Bayesian Inference Module
- What Is This Module?: It's the deterministic brain of VIGÍA. Takes signals from forensic tools, measures how much they deviate from known authentic patterns, and outputs a calibrated probability that a piece of content was fabricated. Think of it as a digital caliper: it measures distance from "normal" using exact arithmetic, applies correction for redundant measurements, and writes an unalterable measurement log.
- Key Concepts Table:
  | Term | What It Means | Role in the Module |
  | Likelihood Ratio (LR) | A score telling you how much more likely the evidence is under a "fabricated" vs "authentic" hypothesis. | Core output before probability conversion. |
  | z-clipping | A deterministic guardrail that caps extreme deviations at ±3 standard units to prevent outlier dominance. | Ensures no single wild measurement can hijack the final score. |
  | log-LR | The logarithm of the Likelihood Ratio. Converts multiplicative effects into additive, exact steps. | Allows sequential, traceable combination of evidence. |
  | Correlation Penalty | A discount applied when two tools measure the same underlying artifact, so they do not double-count. | Prevents overconfidence from redundant signals. |
  | MAD (Median Absolute Deviation) | A robust integer-friendly spread measure: median of absolute distances from the median. | Baseline spread calculated from authentic samples. |
  | ForensicRecord | An immutable audit object containing every input, parameter, and intermediate result. | Guarantees reproducibility and chain-of-custody. |
  | SHA-256 | A deterministic 256-bit integer fingerprint of the record. | Integrity check; any tampering changes the fingerprint. |
  | ENFSI Statement | A standardized forensic conclusion format. | Final verbal expression of the probability. |

- Glossary:
  - **Deterministic**: The system contains no randomness. Identical inputs always produce identical outputs, like a mechanical balance.
  - **Bayesian Inference**: A logical framework for updating the probability of a hypothesis as new evidence arrives. It is counting and re-weighting, not guesswork.
  - **Bootstrap Dataset**: A collection of historical cases used to measure the engine's error rate empirically.
  - **Daubert Auditability**: The property of being testable, with a known error rate, admissible under scientific evidence standards.
  - **Shadow Mode**: Running the engine in parallel with human experts to validate performance without affecting active cases.
  - **Pearson Correlation Matrix**: A table quantifying linear co-movement between pairs of historical signal values.
  - **Chain of Custody**: The documented, unbroken trail of evidence handling.

- Scientific Note:
  【Scientific Note】
  VIGÍA occasionally borrows terms from the semiotics of Peirce, Eco, and Grice to describe *how forensic tools interpret signs*. This is not mysticism. Think of a sensor array: Peirce’s “icon” is a photocell that responds to shape; Eco’s “code” is the calibration table that maps voltage to temperature; Grice’s “maxim” is the fault flag raised when a thermocouple violates expected transmission protocol. The terminology simply provides a compact taxonomy for *sensor-like interpretive behavior*. The LikelihoodEngine itself deals only with deterministic arithmetic on those sensor readings.

ESPAÑOL:
- Motor de Inferencia Bayesiana VIGÍA
- What: El cerebro determinista de VIGÍA. Recibe señales de herramientas forenses, mide su desviación respecto a patrones auténticos conocidos y entrega una probabilidad calibrada de fabricación. Es como un calibre digital: mide distancia al "normal" con aritmética exacta, corrige mediciones redundantes y deja un registro inalterable.
- Key Concepts Table:
  | Término | Qué significa | Rol en el módulo |
  | Razón de Verosimilitud (LR) | Puntuación que indica cuánto más probable es la evidencia bajo hipótesis de fabricación vs. autenticidad. | Salida central antes de conversión a probabilidad. |
  | z-clipping | Guardarrail determinista que limita desviaciones extremas a ±3 unidades estándar. | Evita que un valor atípico domine el puntaje final. |
  | log-LR | Logaritmo de la LR. Convierte efectos multiplicativos en aditivos, exactos. | Permite combinar evidencia secuencial y rastreable. |
  | Penalización por correlación | Descuento aplicado cuando dos herramientas miden el mismo artefacto subyacente. | Evita sobreconfianza por señales redundantes. |
  | MAD | Mediana de las desviaciones absolutas respecto a la mediana. Medida robusta. | Dispersión de referencia calculada solo con muestras auténticas. |
  | ForensicRecord | Objeto de auditoría inmutable con cada entrada, parámetro y resultado intermedio. | Garantiza reproducibilidad y cadena de custodia. |
  | SHA-256 | Huella digital entera determinista de 256 bits del registro. | Verificación de integridad. |
  | Declaración ENFSI | Formato estandarizado de conclusión forense. | Expresión verbal final de la probabilidad. |

- Glossary:
  - **Determinista**: El sistema carece de aleatoriedad. Mismas entradas = mismas salidas, como una balanza mecánica.
  - **Inferencia Bayesiana**: Marco lógico para actualizar la probabilidad de una hipótesis ante nueva evidencia. Es conteo y reponderación, no conjetura.
  - **Dataset Bootstrap**: Colección de casos históricos para medir empíricamente la tasa de error del motor.
  - **Auditabilidad Daubert**: Propiedad de ser testable, con tasa de error conocida, admisible bajo estándares de evidencia científica.
  - **Shadow Mode**: Ejecución paralela con expertos humanos para validar rendimiento sin afectar casos activos.
  - **Matriz de Correlación de Pearson**: Tabla que cuantifica comovimiento lineal entre pares de valores históricos de señales.
  - **Cadena de Custodia**: Documentación ininterrumpida del manejo de evidencia.

- Scientific Note:
  【Nota Científica】
  VIGÍA ocasionalmente usa términos de la semiótica de Peirce, Eco y Grice para describir *cómo las herramientas forenses interpretan signos*. Esto no es misticismo. Piense en un arreglo de sensores: el "icono" de Peirce es una fotocélula que responde a la forma; el "código" de Eco es la tabla de calibración que mapea voltaje a temperatura; la "máxima" de Grice es la bandera de fallo que se levanta cuando un termopar viola el protocolo de transmisión esperado. La terminología simplemente ofrece una taxonomía compacta para el *comportamiento interpretativo tipo sensor*. El LikelihoodEngine solo realiza aritmética determinista sobre esas lecturas.

РУССКИЙ:
- Байесовский движок VIGÍA
- What: Это детерминированный «мозг» VIGÍA. Принимает сигналы от судебных инструментов, измеряет их отклонение от известных аутентичных образцов и выдаёт калиброванную вероятность фабрикации. Как цифровой штангенциркуль: измеряет расстояние до «нормы» точной арифметикой, корректирует избыточные измерения и оставляет неизменяемый журнал.
- Key Concepts Table:
  | Термин | Значение | Роль в модуле |
  | Отношение правдоподобия (LR) | Оценка, показывающая, насколько вероятнее доказательство при гипотезе «подделка» vs. «подлинность». | Основной вывод перед конвертацией в вероятность. |
  | z-обрезка (z-clipping) | Детерминированный ограничитель, фиксирующий предельные отклонения на уровне ±3 стандартных единиц. | Не даёт единичному выбросу захватить итоговую оценку. |
  | log-LR | Логарифм LR. Превращает мультипликативные эффекты в аддитивные, точные шаги. | Позволяет последовательно и прослеживаемо комбинировать доказательства. |
  | Штраф за корреляцию | Дисконт, применяемый когда два инструмента измеряют один и тот же артефакт. | Предотвращает избыточную уверенность от дублирующих сигналов. |
  | MAD (медианное абсолютное отклонение) | Медиана модулей отклонений от медианы. Робастная мера разброса. | Базовый разброс, рассчитанный только на аутентичных образцах. |
  | ForensicRecord | Неизменяемый аудиторский объект со всеми входами, параметрами и промежуточными результатами. | Гарантирует воспроизводимость и цепочку хранения. |
  | SHA-256 | Детерминистический 256-битный целочисленный отпечаток записи. | Проверка целостности; любое вмешательство меняет отпечаток. |
  | Заключение ENFSI | Стандартизированный формат судебного заключения. | Итоговая вербальная форма вероятности. |

- Glossary:
  - **Детерминированный**: В системе отсутствует случайность. Одинаковые входы всегда дают одинаковые выходы, как механические весы.
  - **Байесовская инференция**: Логическая рамка для обновления вероятности гипотезы по мере поступления новых доказательств. Это подсчёт и перевзвешивание, а не догадка.
  - **Бутстреп-набор данных**: Совокупность исторических дел для эмпирического измерения частоты ошибок движка.
  - **Аудируемость по Daubert**: Свойство быть тестируемым, с известной частотой ошибок, допустимым по стандартам научных доказательств.
  - **Режим тени (Shadow Mode)**: Параллельный запуск движка с человеком-экспертом для валидации без влияния на текущие дела.
  - **Матрица корреляции Пирсона**: Таблица количественной оценки линейного согласованного движения пар исторических значений сигналов.
  - **Цепочка хранения**: Документированная непрерывная история обращения с доказательствами.

- Scientific Note:
  【Научное примечание】
  VIGÍA изредка заимствует термины из семиотики Пирса, Эко и Грайса для описания *того, как судебные инструменты интерпретируют знаки*. Это не мистицизм. Вспомните массив датчиков: «икона» Пирса — это фотоэлемент, реагирующий на форму; «код» Эко — таблица калибровки, сопоставляющая напряжение с температурой; «максима» Грайса — флаг отказа, поднимаемый, когда термопара нарушает ожидаемый протокол передачи. Терминология лишь даёт компактную таксономию для *интерпретативного поведения, аналогичного датчику*. Сам LikelihoodEngine занимается только детерминированной арифметикой этих показаний.

中文:
- VIGÍA 似然比引擎 — 核心贝叶斯推断模块
- What Is This Module?: 它是 VIGÍA 的确定性“大脑”。接收来自取证工具的 取证工件 信号，测量其与已知真实样本模式的偏离程度，并输出内容被伪造的校准概率。如同数字卡尺：以确定性整数运算测量与“正常”的距离，修正冗余测量，并留下不可篡改的记录。
- Key Concepts Table:
  | 术语 | 含义 | 模块中的作用 |
  | 似然比 (LR) | 衡量证据在“伪造”假设下相对于“真实”假设可能性的得分。 | 概率转换前的核心输出。 |
  | z-截断 (z-clipping) | 确定性护栏，将极端偏离限制在 ±3 个标准单位内。 | 防止单一异常值主导最终得分。 |
  | 对数似然比 (log-LR) | 似然比的对数。将乘法效应转化为加法步骤。 | 支持证据的顺序、可追溯组合。 |
  | 相关性惩罚 | 当两个工具测量同一底层 取证工件 时应用的折扣。 | 防止冗余信号导致过度自信。 |
  | MAD（中位数绝对偏差） | 各数据点与中位数之差的绝对值的中位数。稳健离散度量。 | 仅使用真实样本计算的基线离散度。 |
  | 取证记录 (ForensicRecord) | 包含所有输入、参数和中间结果的不可变审计对象。 | 保证可重现性与保管链。 |
  | SHA-256 | 记录序列化的确定性 256 位整数指纹。 | 完整性校验；任何篡改都会改变指纹。 |
  | ENFSI 陈述 | 标准化的法庭科学结论格式。 | 概率的最终 verbal 表达。 |

Chinese Glossary:
  - **确定性 (Deterministic)**: 系统不含随机性。相同输入永远产生相同输出，如同机械天平。
  - **贝叶斯推断 (Bayesian Inference)**: 随着新证据到来更新假设概率的逻辑框架。它是计数与重新加权，而非猜测。
  - **Bootstrap 数据集**: 用于经验性测量引擎错误率的历史案例集合。
  - **Daubert 可审计性**: 具备可测试性、已知错误率，符合科学证据标准。
  - **影子模式 (Shadow Mode)**: 引擎与人类专家并行运行以验证性能，不影响在办案件。
  - **皮尔逊相关矩阵**: 量化历史信号值对之间线性共变程度的表格。
  - **保管链 (Chain of Custody)**: 对证据处理过程的文件化、不间断追溯。
  - **取证工件**: 被检测的数字对象或痕迹单元，是信号测量的载体。
  - **逻辑断裂**: 信号之间出现的非物理性、非统计性不一致，提示潜在伪造。

Scientific Note Chinese:
  【科学说明】
  VIGÍA 偶尔借用皮尔斯、艾柯与格赖斯的符号学术语来描述*取证工具如何解读符号*。这并非神秘主义。请设想一组传感器阵列：皮尔斯的“像似符”是一块对形状产生响应的光电元件；艾柯的“代码”是将电压映射为温度的校准表；格赖斯的“准则”是当热电偶违反预期传输协议时升起的故障标志。这些术语仅为*类传感器解释行为*提供了一套紧凑的分类法。LikelihoodEngine 本身仅对这些传感器读数执行确定性运算。

Need to ensure "deterministic integer arithmetic" emphasis. In the English and other sections, when describing the engine, mention it operates on exact arithmetic principles. For example, mention that all counting, indexing, hashing (SHA-256) are integer operations. The z-clipping and log-LR might be conceptualized as deterministic rational mappings. I will say something like: "Although statistical transformations appear continuous, the implementation treats them as deterministic functions over fixed-precision integer registers, ensuring bitwise reproducibility." Or more simply, avoid calling them floats.

Actually, the user says "Do NOT use floating-point math explanations — emphasize deterministic integer arithmetic where applicable". So for SHA-256, record_hash, counting, indexing, the bootstrap error rate (integer counts of errors), I will explicitly mention integer arithmetic. For the statistical formulas, I'll describe them conceptually without using terms like "floating point". I'll say "deterministic arithmetic operations".

Also, the module path and docstring should be referenced.

Let's organize the Markdown.

I'll create a main title, then 4 sections.

For each section:
## ENGLISH / ESPAÑOL / РУССКИЙ / 中文

### What Is This Module?
...

### Key Concepts
| ... | ... | ... |

### Component Overview (optional but helpful)
Maybe brief descriptions of classes/functions in a table. The user asked for documentation of the module. I'll include a table for Classes and Functions.

### Glossary
...

### 【Scientific Note】/【Nota Científica】/【Научное примечание】/【科学说明】
...

Then at the very end of each section, the license line.

Let's refine the content to be thorough but concise.

ENGLISH details:

**What Is This Module?**
`vigia/core/likelihood_ratio.py` houses the **LikelihoodEngine**, the deterministic Bayesian inference core of the VIGÍA forensic platform. It consumes arrays of `SignalOutput` objects produced by upstream detection tools, compares them against baselines built exclusively from authenticated samples, and yields a calibrated probability of fabrication. Every transformation—standard-deviation clipping, correlation penalization, and logarithmic combination—is executed as a deterministic arithmetic procedure with no randomness, no language-model calls, and no network access. The module also produces a `ForensicRecord`, an immutable audit artifact that can be exported to JSON and integrity-locked via SHA-256 for courtroom chain-of-custody requirements.

**Key Concepts**
| Concept | Plain-Language Definition | Function in This Module |
|---|---|---|
| SignalOutput | A structured measurement packet generated by a forensic tool (e.g., anomaly score, metadata flag). | The raw input fed into the engine. |
| z-clipping | A boundary rule that forces extreme values to stay within ±3 standard units of the baseline. | Prevents a single outlier from exploding the Likelihood Ratio. |
| log-LR | The additive form of the Likelihood Ratio, turning stacked evidence into a sum rather than a product. | Enables step-by-step, auditable evidence combination. |
| Correlation Penalty | A downward adjustment applied when two signals are derived from the same underlying source. | Removes double-counting; keeps confidence honest. |
| MAD Baseline | Median Absolute Deviation computed solely on the AUTHENTIC class to set the “normal” scale. | Robust, integer-rank-friendly spread measure. |
| ForensicRecord | A complete, timestamped ledger of the inference run. | Reproducibility and legal perusal. |
| SHA-256 Hash | A deterministic 256-bit integer digest of the serialized record. | Tamper detection; chain-of-custody seal. |
| ENFSI Statement | A standardized verbal qualification of the probability (e.g., “strong support for fabrication”). | Human-readable court-ready conclusion. |

**Classes & Functions Overview**
| Name | Type | Purpose |
|---|---|---|
| `LikelihoodEngine` | Class | Deterministic Bayesian processor; stateless, no LLM. |
| `ForensicRecord` | Class | Immutable audit trail; exportable to JSON. |
| `infer()` | Method | Executes Bayesian inference over a list of `SignalOutput`. |
| `build_baseline_from_authentic()` | Function | Computes mean and MAD per tool using only authentic samples. |
| `compute_correlation_matrix_from_values()` | Function | Builds Pearson matrix from historical integer-indexed value tables. |
| `to_dict()` / `to_json()` | Methods | Serialize the record into dictionaries or JSON strings. |
| `record_hash()` | Method | Returns SHA-256 integer fingerprint of the record. |

**Glossary**
- **Deterministic system**: A process devoid of stochastic noise. Given identical inputs, the output is bitwise identical every time, analogous to a mechanical clockwork.
- **Bayesian updating**: A formal method for revising belief in a hypothesis by multiplying prior odds by the likelihood ratio of new evidence. It is rigorous counting, not subjective impression.
- **Bootstrap error rate**: The fraction of incorrect classifications observed when the engine is tested against resampled historical datasets; expressed as an exact integer ratio (e.g., 3 errors in 1,000 trials).
- **Daubert standard**: A legal threshold requiring forensic methods to be testable, peer-reviewed, and characterized by a known error rate.
- **Shadow mode**: A validation configuration in which the engine runs silently alongside live casework to accumulate performance metrics without affecting human decisions.
- **Pearson correlation**: A deterministic measure of linear association between two series of historical values, computed from integer sums of products and squares.
- **Chain of custody**: The documented, unbroken sequence of evidence possession and analysis.

**【Scientific Note】**
VIGÍA occasionally employs terminology drawn from the semiotics of Peirce, Eco, and Grice to describe how forensic tools interpret signs. This is not mysticism. Imagine a laboratory sensor array: Peirce’s “icon” behaves like a photocell that reacts to shape; Eco’s “code” behaves like a calibration table converting raw voltage into temperature; Grice’s “maxim” behaves like an integrity alarm triggered when a thermocouple violates expected transmission protocol. These terms provide a compact taxonomy for *sensor-like interpretive behavior*. The `LikelihoodEngine` itself performs only deterministic integer and combinatorial arithmetic on those sensor readings; it does not invoke any language model, nor does it traffic in vague hermeneutics.

ESPAÑOL details:
Similar structure. Ensure terms are correct.

**What Is This Module?**
`vigia/core/likelihood_ratio.py` alberga el **LikelihoodEngine**, el núcleo de inferencia bayesiana determinista de la plataforma forense VIGÍA. Consume arreglos de objetos `SignalOutput` generados por herramientas de detección, los compara contra líneas base construidas exclusivamente con muestras auténticas, y produce una probabilidad calibrada de fabricación. Cada transformación —z-clipping, penalización por correlación y combinación logarítmica— se ejecuta como un procedimiento aritmético determinista, sin aleatoriedad, sin modelos de lenguaje y sin acceso a red. El módulo también genera un `ForensicRecord`, artefacto de auditoría inmutable exportable a JSON y sellado con SHA-256 para requisitos de cadena de custodia.

**Key Concepts**
| Concepto | Definición en lenguaje llano | Función en este módulo |
|---|---|---|
| SignalOutput | Paquete de medición estructurado generado por una herramienta forense (p. ej., puntaje de anomalía). | La entrada cruda del motor. |
| z-clipping | Regla de límite que fuerza a los valores extremos a permanecer dentro de ±3 unidades estándar de la línea base. | Evita que un solo valor atípico explote la Razón de Verosimilitud. |
| log-LR | Forma aditiva de la LR, convirtiendo evidencia acumulada en una suma en vez de un producto. | Permite combinación secuencial y auditable de evidencia. |
| Penalización por correlación | Ajuste a la baja cuando dos señales provienen de la misma fuente subyacente. | Elimina doble conteo; mantiene la confianza realista. |
| Línea base MAD | Desviación Absoluta Mediana calculada SÓLO con la clase AUTHENTIC para fijar la escala “normal”. | Medida robusta de dispersión amigable con rangos enteros. |
| ForensicRecord | Registro completo y con marca temporal de la ejecución de inferencia. | Reproducibilidad y examen legal. |
| Hash SHA-256 | Resumen entero determinista de 256 bits del registro serializado. | Detección de manipulación; sello de cadena de custodia. |
| Declaración ENFSI | Cualificación verbal estandarizada de la probabilidad (p. ej., “fuerte apoyo a fabricación”). | Conclusión legible por humanos lista para tribunales. |

**Classes & Functions Overview**
| Nombre | Tipo | Propósito |
|---|---|---|
| `LikelihoodEngine` | Clase | Procesador bayesiano determinista; sin estado, sin LLM. |
| `ForensicRecord` | Clase | Rastro de auditoría inmutable; exportable a JSON. |
| `infer()` | Método | Ejecuta inferencia bayesiana sobre una lista de `SignalOutput`. |
| `build_baseline_from_authentic()` | Función | Calcula media y MAD por herramienta usando solo muestras auténticas. |
| `compute_correlation_matrix_from_values()` | Función | Construye matriz de Pearson a partir de tablas históricas indexadas por enteros. |
| `to_dict()` / `to_json()` | Métodos | Serializan el registro a diccionarios o cadenas JSON. |
| `record_hash()` | Método | Devuelve huella digital entera SHA-256 del registro. |

**Glossary**
- **Sistema determinista**: Proceso carente de ruido estocástico. Ante entradas idénticas, la salida es idéntica bit a bit, como un mecanismo de relojería.
- **Actualización bayesiana**: Método formal para revisar la creencia en una hipótesis multiplicando las probabilidades previas por la razón de verosimilitud de la nueva evidencia. Es conteo riguroso, no impresión subjetiva.
- **Tasa de error bootstrap**: Fracción de clasificaciones erróneas observada al probar el motor contra conjuntos históricos remuestreados; expresada como razón entera exacta (p. ej., 3 errores en 1 000 pruebas).
- **Estándar Daubert**: Umbral legal que exige que los métodos forenses sean testeables, revisados por pares y con tasa de error conocida.
- **Shadow mode**: Configuración de validación en la que el motor opera en silencio junto a casos reales para acumular métricas de rendimiento sin afectar decisiones humanas.
- **Correlación de Pearson**: Medida determinista de asociación lineal entre dos series de valores históricos, calculada a partir de sumas enteras de productos y cuadrados.
- **Cadena de custodia**: Secuencia documentada e ininterrumpida de posesión y análisis de evidencia.

**【Nota Científica】**
VIGÍA emplea ocasionalmente terminología de la semiótica de Peirce, Eco y Grice para describir cómo las herramientas forenses interpretan signos. Esto no es misticismo. Imagine un arreglo de sensores de laboratorio: el “icono” de Peirce se comporta como una fotocélula que reacciona a la forma; el “código” de Eco se comporta como una tabla de calibración que convierte voltaje crudo en temperatura; la “máxima” de Grice se comporta como una alarma de integridad que se activa cuando un termopar viola el protocolo de transmisión esperado. Estos términos proporcionan una taxonomía compacta para el *comportamiento interpretativo tipo sensor*. El `LikelihoodEngine` solo realiza aritmética determinista entera y combinatoria sobre esas lecturas de sensores; no invoca ningún modelo de lenguaje ni incurre en hermenéutica vaga.

РУССКИЙ details:

**What Is This Module?**
`vigia/core/likelihood_ratio.py` содержит **LikelihoodEngine** — детерминированное ядро байесовской инференции судебной платформы VIGÍA. Он принимает массивы объектов `SignalOutput`, созданных инструментами обнаружения, сравнивает их с базовыми линиями, построенными исключительно на аутентичных образцах, и выдаёт калиброванную вероятность фабрикации. Каждое преобразование — z-обрезка, штраф за корреляцию и логарифмическое комбинирование — выполняется как детерминированная арифметическая процедура без случайности, без языковых моделей и без
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
