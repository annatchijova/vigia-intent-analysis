<!--
VIGIA Academic Documentation
Module: 91f2a764
Batch ID: vigia-doc-0129-91f2a764
Generated: 2026-05-20T14:56:47.872334+00:00
-->

### ENGLISH

#### What Is This Module?
A deterministic arithmetic engine... scientists don't need Python.

#### Key Concepts Table
| Term | Role | Deterministic Mechanism |
|---|---|---|
| Fraction Arithmetic | Core engine | Integer numerator/denominator operations only |
| Resistance Factor (R) | Anti-silencing | Weighted multiplier protecting non-dominant but valid signals |
| Conflict Penalty | Contradiction handling | Penalizes subordinate signals; dominant signal invariant preserved |
| Newton Sqrt (Fraction) | Exact irrational approx | Iterative integer refinement to bounded exactitude |
| Shannon Entropy | Uncertainty quant | Direct computation over value lists, no intermediate serialization |
| TOCTOU Hardening | Timestamp integrity | Explicit error on parse failure; zero is never silently returned |
| Safe Float Clamp | Boundary enforcement | Input floats clamped to [min, max] before Fraction conversion, preventing overflow |

#### Functions Table
| Function | Purpose | Deterministic Guarantee |
|---|---|---|
| `clamp_float_to_fraction` | Safe type conversion | Overflow prevented; bounds enforced with integer clamp |
| `noisy_or_correlated` | Correlated evidence fusion | Noisy-OR via rational probability bounds |
| `apply_artifact_reliability` | Source trust weighting | Reliability coefficient applied as exact rational multiplier |
| `build_redundancy_groups` | Evidence clustering | Grouping by exact match criteria, no probabilistic hash |
| `apply_frs` | Redundancy scoring | Forensic Redundancy Score as rational aggregate |
| `classify_group` | Group typing | Deterministic threshold classification |
| `apply_conflict_penalty` | Anti-silencing correction | Weighted score = z × Γ × R; dominant signal never penalized |
| `partition_contradictory_group` | Split by dominance | Explicit dominant/non-dominant separation |
| `process_all_groups` | Full pipeline | Precedence: CONFLICT > FRS; invariant validated post-penalty |

#### Constants Table
| Constant | Meaning | Type |
|---|---|---|
| `LN2` | ln(2) for entropy | Fraction |
| `RESISTANCE_FACTOR` | R in penalty formula | Fraction |
| `EPS` | Convergence threshold for sqrt | Fraction |
| `MAX_ITER` | Iteration safety bound | Integer |

#### Glossary
...terms like Artifact, Dominant Signal, Signal Silencing, TOCTOU, Invariant, Resistance Factor, Interpretant (Peirce), Code (Eco), Maxim (Grice).

#### Scientific Note
> **【Scientific Note】** The module employs terminology derived from Charles Sanders Peirce (sign-object-interpretant), Umberto Eco (coding/overcoding), and H. Paul Grice (conversational maxims). In this forensic context, these terms are **operational analogues to sensor calibration parameters**, not metaphysical concepts. A Peircean "interpretant" corresponds to the measurable effect a trace has on the scoring function; an Eco-style "code" is the formal likelihood mapping between a source state and its evidentiary output; a Gricean "maxim" is a binding constraint on how signals may be combined without logical fracture. Think of them as formal rules for fusing readings from a heterogeneous sensor array.

#### License

---

Then replicate for other languages.

For ESPAÑOL:
- Módulo: motor aritmético determinista...
- Peirce, Eco, Grice analogía sensorial.
- Términos: Factor de Resistencia, Penalización por Conflicto, Artefacto de prueba / Artefacto forense (or "artefacto de evidencia"). The user wrote "apply_artifact_reliability" and "apply_conflict_penalty". I should use "artefacto forense" or "artefacto de evidencia". Let's use "artefacto forense".
- Signal silencing = silenciamiento de señal.
- TOCTOU = condición de carrera tiempo-comprobación/tiempo-uso.
- Scientific note: 【Nota Científica】 or 【科学说明】? The user said for Chinese use 【科学说明】. For other languages, I should use an equivalent boxed note. The user specifically said "A 【科学说明】/【Scientific Note】 box". So for ENGLISH use 【Scientific Note】, ESPAÑOL maybe 【Nota Científica】, РУССКИЙ 【Научное примечание】, 中文 【科学说明】. That seems consistent.

For РУССКИЙ:
- Модуль: детерминированный вычислительный движок...
- Термины: дробная арифметика (Fraction), фактор сопротивления (R), штраф за конфликт, группы избыточности, артефакт (forensic artifact = цифровой артефакт / артефакт доказательства). Let's use "артефакт" in context.
- Scientific note: 【Научное примечание】

For 中文:
- 模块：确定性整数运算引擎...
- Terms: 取证工件 (forensic artifact), 逻辑断裂 (logical fracture), 艾柯 (Eco), 格赖斯 (Grice), 皮尔士 (Peirce).
- 信号压制 (signal silencing), 冲突惩罚, 主导信号 (dominant signal), 不变量验证.
- Scientific note: 【科学说明】
- Explain Peirce/Eco/Grice as sensor calibration.

Important: The user said "You NEVER use floating-point math explanations for deterministic systems." So when describing algorithms like Newton-Raphson sqrt or entropy, I must describe them as integer/rational iterative methods or exact rational aggregations, not as "approximations because floats are bad." The reason for Fraction is determinism and reproducibility.

I also need to mention that floats are only used at the final output boundary (SignalOutput constructor), as per FIX 2.

Let's draft the content carefully.

**ENGLISH Draft:**

What Is This Module?
`vigia/sift/_math_utils.py` is the deterministic arithmetic core of a digital-forensic signal-sifting system. It processes evidence traces ("forensic artifacts") using exact rational-number arithmetic (the `Fraction` type) rather than floating-point approximations. Every internal operation—scoring, conflict resolution, entropy calculation, and square-root iteration—remains in the integer domain until the final export step. Scientists can treat it as a reproducible scoring laboratory: the same input always yields the same score, with no hardware-dependent rounding drift.

Key Concepts Table:
| Concept | Forensic Role | Deterministic Mechanism |
|---|---|---|
| Exact Rational Arithmetic | Core computation engine | All scores stored as integer numerator/denominator pairs (`Fraction`). No rounding occurs during fusion, penalty, or entropy steps. |
| Resistance Factor (R) | Anti-silencing safeguard | A rational multiplier that protects non-dominant signals from being extinguished by the dominant one. |
| Conflict Penalty | Contradiction management | Penalizes subordinate (non-dominant) artifacts only; the dominant signal’s rank is preserved as an invariant. |
| Mid Attenuation (Pure Fraction) | Score re-weighting | Applied entirely within rational arithmetic; no intermediate float conversion. |
| Newton Sqrt for Fractions | Exact iterative root | Integer-only Newton-Raphson refinement converges to a rational bound within `EPS`; no float intermediate. |
| Shannon Entropy | Uncertainty measure | Computed directly from an integer-frequency list via exact rational logarithms; no string serialization or float accumulation. |
| TOCTOU Hardening | Timestamp integrity | `_parse_iso_timestamp` raises an explicit exception on failure; a silent zero fallback is forbidden, eliminating time-of-check/time-of-use race conditions in evidence ordering. |
| Safe Float Clamp | Input sanitization | `clamp_float_to_fraction` forces the input into a bounded integer interval before rational conversion, preventing `OverflowError`. |
| Dominance Stability Test | Post-condition check | After any penalty, an explicit invariant verifies that the dominant artifact remains dominant. |

Functions Table:
| Function | Purpose | Deterministic Guarantee |
|---|---|---|
| `clamp_float_to_fraction` | Boundary-limited float-to-Fraction conversion | Clamps to `[min_val, max_val]` using integer bounds; overflow impossible. |
| `noisy_or_correlated` | Correlated evidence fusion | Combines artifact likelihoods via the Noisy-OR model using rational probability bounds. |
| `apply_artifact_reliability` | Reliability weighting | Multiplies raw signal by a source-reliability coefficient expressed as an exact fraction. |
| `build_redundancy_groups` | Evidence clustering | Groups artifacts by deterministic correlation keys; output depends only on input content, not on iteration order. |
| `apply_frs` | Redundancy scoring | Computes the Forensic Redundancy Score as a rational aggregate of group members. |
| `classify_group` | Group typing | Assigns a deterministic label (e.g., consistent, contradictory) based on rational thresholds. |
| `apply_conflict_penalty` | Anti-silencing correction | Computes `WEIGHTED_SCORE = z × Γ × R`, where `R` is the Resistance Factor. Penalty is applied to non-dominant artifacts only; the dominant signal is never penalized. |
| `partition_contradictory_group` | Dominance-based splitting | Separates a contradictory group into a dominant subset and a non-dominant subset using exact score comparisons. |
| `process_all_groups` | Full analysis pipeline | Enforces processing precedence `CONFLICT > FRS`. Runs dominance-stability validation after penalty application. |

Constants Table:
| Constant | Meaning | Value Type |
|---|---|---|
| `LN2` | Natural logarithm of 2 | Exact `Fraction`; used in Shannon entropy. |
| `RESISTANCE_FACTOR` | Resistance multiplier `R` | Exact `Fraction`; prevents signal silencing. |
| `EPS` | Convergence tolerance | Exact `Fraction`; termination bound for Newton iteration. |
| `MAX_ITER` | Iteration ceiling | Integer; safety limit for Newton-Raphson loops. |

Glossary:
- **Artifact (Forensic)**: A discrete unit of digital evidence (e.g., a log entry, hash, timestamp) submitted for scoring.
- **Dominant Signal**: The artifact or group possessing the highest rational score within a given comparison set; treated as the reference state during conflict resolution.
- **Signal Silencing**: The unwanted suppression of a minority evidence trace when it contradicts a stronger trace. The Resistance Factor `R` corrects this.
- **Resistance Factor (R)**: A rational coefficient that scales non-dominant scores upward during conflict penalty, preserving their audible weight in the final fusion.
- **TOCTOU**: Time-of-check/time-of-use; a race condition where evidence state changes between validation and processing. Hardened here by explicit parse exceptions.
- **Invariant**: A logical condition that must hold true after an operation. Here: the dominant artifact before penalty must remain dominant after penalty.
- **Fraction (Rational)**: A number represented as a pair of integers (numerator, denominator), yielding exact results under addition, multiplication, and comparison.
- **Noisy-OR**: A probabilistic fusion model for correlated sources; implemented here with rational bounds to retain determinism.
- **Logical Fracture**: A state where combined evidence yields an internal contradiction; resolved by partitioning and penalizing the weaker side.

Scientific Note:
> 【Scientific Note】
> This module uses concepts from Charles Sanders Peirce (sign–object–interpretant), Umberto Eco (code and overcoding), and H. Paul Grice (conversational maxims). These are **operational analogues to sensor-calibration parameters**, not mystical or literary constructs.
> - A **Peircean interpretant** is the measurable change in the score function produced by a given trace.
> - An **Eco-style code** is the formal likelihood mapping between a system state and its evidentiary output.
> - A **Gricean maxim** is a hard constraint on signal combination; violating it produces a detectable **logical fracture** in the evidence stream, analogous to a sensor array returning incompatible readings from overlapping fields of view.
> Researchers should view these labels as formal names for fusion rules, comparable to calibration matrices in multi-sensor data assimilation.

---

**ESPAÑOL Draft:**

What Is This Module? -> ¿Qué es este módulo?
Es el núcleo aritmético determinista de un sistema forense digital de cribado de señales...

Key Concepts -> Conceptos clave
| Concepto | Rol forense | Mecanismo determinista |
|---|---|---|
| Aritmética racional exacta | Motor de cálculo | Todas las puntuaciones son pares de enteros (numerador/denominador). No hay redondeo. |
| Factor de Resistencia (R) | Protección anti-silenciamiento | Multiplicador racional que evita que señales no dominantes sean extinguidas. |
| Penalización por Conflicto | Gestión de contradicciones | Se aplica solo a artefactos subordinados; la señal dominante se preserva invariante. |
| Atenuación media | Reponderación | Se ejecuta en aritmética de fracciones puras, sin float intermedio. |
| Raíz cuadrada de Newton (Fracción) | Refinamiento exacto | Método iterativo de Newton-Raphson con enteros; convergencia racional dentro de EPS. |
| Entropía de Shannon | Medida de incertidumbre | Cálculo directo sobre lista de frecuencias enteras; sin serialización. |
| Endurecimiento TOCTOU | Integridad de marca temporal | El parser de ISO timestamp falla explícitamente; queda prohibido devolver 0 en silencio. |
| Clampeo seguro a fracción | Sanitización de entrada | `clamp_float_to_fraction` acota el valor a [min, max] antes de convertir a fracción, evitando OverflowError. |
| Prueba de estabilidad de dominancia | Verificación post-operación | Invariante explícito: el artefacto dominante antes de la penalización sigue siéndolo después. |

Functions -> Funciones
| Función | Propósito | Garantía determinista |
|---|---|---|
| `clamp_float_to_fraction` | Conversión float→Fraction segura | Acotación entera; imposibilidad de desbordamiento. |
| `noisy_or_correlated` | Fusión de evidencia correlacionada | Noisy-OR mediante cotas de probabilidad racionales. |
| `apply_artifact_reliability` | Ponderación por fiabilidad | Multiplicación por coeficiente racional exacto. |
| `build_redundancy_groups` | Agrupación de evidencias | Agrupación por clave de correlación determinista. |
| `apply_frs` | Puntuación de redundancia forense | Agregado racional exacto. |
| `classify_group` | Clasificación de grupos | Etiquetado por umbrales racionales. |
| `apply_conflict_penalty` | Corrección anti-silenciamiento | `WEIGHTED_SCORE = z × Γ × R`. Penaliza solo a no-dominantes. |
| `partition_contradictory_group` | Partición por dominancia | Separación exacta en subconjunto dominante y subordinado. |
| `process_all_groups` | Pipeline completo | Precedencia CONFLICTO > FRS; validación de invariante post-penalización. |

Constants -> Constantes
| Constante | Significado | Tipo |
|---|---|---|
| `LN2` | Logaritmo natural de 2 | `Fraction` exacta; usada en entropía. |
| `RESISTANCE_FACTOR` | Multiplicador de resistencia `R` | `Fraction` exacta. |
| `EPS` | Tolerancia de convergencia | `Fraction` exacta; límite de parada de Newton. |
| `MAX_ITER` | Tope de iteraciones | Entero; límite de seguridad. |

Glossary -> Glosario
- **Artefacto forense**: Unidad discreta de evidencia digital (registro, hash, marca temporal).
- **Señal dominante**: Artefacto o grupo con la puntuación racional más alta; referencia en resolución de conflictos.
- **Silenciamiento de señal**: Supresión indeseada de una traza minoritaria. El Factor R lo corrige.
- **Factor de Resistencia (R)**: Coeficiente racional que escala las puntuaciones no dominantes durante la penalización.
- **TOCTOU**: Condición de carrera entre comprobación y uso; mitigada mediante excepciones explícitas.
- **Invariante**: Condición lógica que debe cumplirse tras una operación. Aquí: la dominancia se mantiene.
- **Fracción (racional)**: Número como par de enteros (numerador, denominador); resultados exactos.
- **Noisy-OR**: Modelo de fusión probabilístico para fuentes correlacionadas; implementado con cotas racionales.
- **Fractura lógica**: Estado de contradicción interna en evidencias combinadas; resuelta particionando el lado más débil.

Scientific Note -> 【Nota Científica】
> 【Nota Científica】
> Este módulo utiliza conceptos de Charles Sanders Peirce (signo–objeto–interpretante), Umberto Eco (código y sobrecodificación) y H. Paul Grice (máximas conversacionales). Se trata de **analogías operacionales a parámetros de calibración de sensores**, no construcciones místicas o literarias.
> - Un **interpretante peirceano** es el cambio medible en la función de puntuación producido por una traza.
> - Un **código en sentido ecológico** (Eco) es el mapeo formal de verosimilitud entre un estado del sistema y su salida probatoria.
> - Una **máxima griceana** es una restricción dura sobre la combinación de señales; su violación produce una **fractura lógica** en el flujo de evidencias, análoga a una matriz de sensores que devuelve lecturas incompatibles en campos de vista solapados.
> El investigador debe entender estas etiquetas como nombres formales de reglas de fusión, comparables a matrices de calibración en la asimilación de datos multi-sensor.

License -> Licencia

---

**РУССКИЙ Draft:**

What Is This Module? -> Что представляет собой этот модуль?
Это детерминированное арифметическое ядро системы цифровой криминалистической сортировки сигналов...

Key Concepts -> Ключевые понятия
| Понятие | Криминалистическая роль | Детерминированный механизм |
|---|---|---|
| Точная рациональная арифметика | Вычислительное ядро | Все оценки — пары целых чисел (числитель/знаменатель). Округление отсутствует. |
| Фактор сопротивления (R) | Защита от подавления сигнала | Рациональный множитель, предотвращающий гашение недоминирующих сигналов. |
| Штраф за конфликт | Разрешение противоречий | Накладывается только на подчинённые артефакты; доминирующий сигнал сохраняется инвариантно. |
| Среднее ослабление | Перевзвешивание | Выполняется в чисто дробной арифметике без промежуточных float. |
| Квадратный корень Ньютона (дробный) | Точное итеративное приближение | Целочисленный метод Ньютона–Рафсона; сходимость в рациональной границе EPS. |
| Энтропия Шеннона | Мера неопределённости | Прямое вычисление по списку целочисленных частот; без сериализации. |
| Упрочнение TOCTOU | Целостность меток времени | Парсер ISO-метки явно выбрасывает исключение при ошибке; запрещено тихое возвращение 0. |
| Безопасное ограничение (clamp) | Очистка входных данных | `clamp_float_to_fraction` ограничивает значение [min, max] до рационального преобразования, предотвращая OverflowError. |
| Проверка стабильности доминирования | Постусловие | Явный инвариант: доминирующий артефакт после штрафа остаётся доминирующим. |

Functions -> Функции
| Функция | Назначение | Детерминированная гарантия |
|---|---|---|
| `clamp_float_to_fraction` | Безопасное преобразование float→Fraction | Целочисленное ограничение; переполнение исключено. |
| `noisy_or_correlated` | Слияние коррелированных доказательств | Noisy-OR с рациональными вероятностными границами. |
| `apply_artifact_reliability` | Взвешивание по надёжности источника | Умножение на точный рациональный коэффициент. |
| `build_redundancy_groups` | Кластеризация артефактов | Группировка по детерминированным ключам корреляции. |
| `apply_frs` | Оценка криминалистической избыточности | Точный рациональный агрегат. |
| `classify_group` | Классификация групп | Метка по рациональным порогам. |
| `apply_conflict_penalty` | Коррекция подавления сигнала | `WEIGHTED_SCORE = z × Γ × R`. Штраф только недоминирующим. |
| `partition_contradictory_group` | Разделение по доминированию | Точное разделение на доминирующее и подчинённое подмножества. |
| `process_all_groups` | Полный конвейер | Приоритет CONFLICT > FRS; валидация инварианта после штрафа. |

Constants -> Константы
| Константа | Значение | Тип |
|---|---|---|
| `LN2` | Натуральный логарифм 2 | Точная `Fraction`; для энтропии. |
| `RESISTANCE_FACTOR` | Множитель сопротивления `R` | Точная `Fraction`. |
| `EPS` | Допуск сходимости | Точная `Fraction`; критерий остановки Ньютона. |
| `MAX_ITER` | Потолок итераций | Целое; предохранительный лимит. |

Glossary -> Глоссарий
- **Артефакт (криминалистический)**: Дискретная единица цифрового доказательства (запись, хэш, метка времени).
- **Доминирующий сигнал**: Артефакт или группа с наивысшей рациональной оценкой; эталон при разрешении конфликтов.
- **Подавление сигнала (silencing)**: Нежелательное гашение миноритарной следовой записи. Фактор R устраняет это.
- **Фактор сопротивления (R)**: Рациональный коэффициент, масштабирующий недоминирующие оценки при конфликтном штрафе.
- **TOCTOU**: Состояние гонки между проверкой и использованием; устранено явными исключениями.
- **Инвариант**: Логическое условие, обязательное после операции. Здесь: доминантность сохраняется.
- **Fraction (рациональное число)**: Число как пара целых (числитель, знаменатель); точные результаты.
- **Noisy-OR**: Вероятностная модель слияния коррелированных источников; реализована рациональными границами.
- **Логический разрыв (logical fracture)**: Состояние внутреннего противоречия комбинированных доказательств; разрешается разделением слабой стороны.

Scientific Note -> 【Научное примечание】
> 【Научное примечание】
> Модуль использует терминологию Чарльза Сандерса Пирса (знак–объект–интерпретант), Умберто Эко (код и overcoding) и Герберта Пола Грайса (конверсациональные максимы). Это **операциональные аналоги параметров калибровки сенсоров**, а не мистические или литературные конструкты.
> - **Пирсовский интерпретант** — измеримое изменение функции оценки, вызванное данной следовой записью.
> - **Код в смысле Эко** — формальное отображение правдоподобия между состоянием системы и её доказательственным выходом.
> - **Грайсовская максима** — жёсткое ограничение на комбинирование сигналов; её нарушение порождает обнаружимый **логический разрыв** в потоке доказательств, аналогичный ситуации, когда массив датчиков возвращает несовместимые показания в перекрывающихся полях зрения.
> Исследователи должны воспринимать эти термины как формальные названия правил слияния, сопоставимые с калибровочными матрицами в мультисенсорной ассимиляции данных.

License -> Лицензия

---

**中文 Draft:**

What Is This Module? -> 本模块是什么？
`vigia/sift/_math_utils.py` 是一个数字取证信号筛分系统的确定性算术核心...

Key Concepts -> 核心概念
| 概念 | 取证作用 | 确定性机制 |
|---|---|---|
| 精确有理数运算 | 计算引擎 | 所有分数均以整数对（分子/分母）存储。融合、惩罚与熵计算过程中无任何舍入。 |
| 阻抗因子 (R) | 防信号压制 | 有理数乘数，防止非主导信号被主导信号湮灭。 |
| 冲突惩罚 | 矛盾管理 | 仅对从属取证工件施加惩罚；主导信号的排名保持不变量。 |
| 中段衰减 | 分数重加权 | 完全在纯分数算术内执行，无中间浮点转换。 |
| 牛顿开方（分数版） | 精确迭代求根 | 纯整数牛顿-拉夫逊迭代，在 `EPS` 有理数界限内收敛；无中间浮点。 |
| 香农熵 | 不确定度量化 | 直接基于整数值列表计算，采用精确有理对数；无序列化或浮点累加。 |
| TOCTOU 加固 | 时间戳完整性 | `_parse_iso_timestamp` 在解析失败时显式抛出异常；禁止静默返回 0。 |
| 安全浮点钳制 | 输入消毒 | `clamp_float_to_fraction` 在转换为分数前将输入钳制于 [min, max] 整数区间，防止 `OverflowError`。 |
| 主导稳定性测试 | 后置条件验证 | 显式不变量：惩罚操作后，主导取证工件仍保持主导地位。 |

Functions -> 函数
| 函数 | 用途 | 确定性保证 |
|---|---|---|
| `clamp_float_to_fraction` | 安全的浮点到分数转换 | 整数边界钳制；不可能发生溢出。 |
| `noisy_or_correlated` | 相关证据融合 | 通过有理概率界限实现 Noisy-OR 模型。 |
| `apply_artifact_reliability` | 来源可靠性加权 | 以精确有理系数乘以原始信号。 |
| `build_redundancy_groups` | 证据聚类 | 依据确定性相关键分组；输出仅取决于输入内容。 |
| `apply_frs` | 冗余度评分 | 以精确有理数聚合计算取证冗余分数 (FRS)。 |
| `classify_group` | 群组分类 | 基于有理阈值赋予确定性标签（如一致/矛盾）。 |
| `apply_conflict_penalty` | 反信号压制修正 | 计算 `WEIGHTED_SCORE = z × Γ × R`，其中 `R` 为阻抗因子。仅对非主导工件惩罚，永不惩罚主导信号。 |
| `partition_contradictory_group` | 按主导性拆分 | 利用精确分数比较，将矛盾群组分为主导子集与从属子集。 |
| `process_all_groups` | 完整分析流水线 | 强制优先级：`CONFLICT > FRS`；惩罚后执行主导稳定性验证。 |

Constants -> 常量
| 常量 | 含义 | 值类型 |
|---|---|---|
| `LN2` | 2 的自然对数 | 精确 `Fraction`；用于香农熵。 |
| `RESISTANCE_FACTOR` | 阻抗乘数 `R` | 精确 `Fraction`；防止信号压制。 |
| `EPS` | 收敛容差 | 精确 `Fraction`；牛顿迭代终止界。 |
| `MAX_ITER` | 迭代上限 | 整数；安全循环限制。 |

Glossary -> 术语表
- **取证工件**：数字证据的离散单元（如日志条目、哈希值、时间戳），作为评分输入。
- **主导信号**：在比较集合中拥有最高有理分数的取证工件或群组；在冲突解决中作为参考态。
- **信号压制**：少数证据痕迹被更强痕迹压制的不期望现象。阻抗因子 `R` 予以纠正。
- **阻抗因子 (R)**：冲突惩罚期间按比例放大非主导分数的有理系数，使其在最终融合中保持可闻权重。
- **TOCTOU**：检查时间与使用时间之间的竞争条件；本模块通过显式异常进行加固。
- **不变量**：操作后必须成立的逻辑条件。此处指：惩罚前的主导工件在惩罚后仍为主导。
- **分数（有理数）**：以整数对（分子、分母）表示的数，其加减乘除与比较结果完全精确。
- **Noisy-OR**：用于相关源的概率融合模型；此处采用有理界限实现以保持确定性。
- **逻辑断裂**：组合证据产生内部矛盾的状态；通过拆分并惩罚较弱一方予以解决。

Scientific Note -> 【科学说明】
> 【科学说明】
> 本模块借用了查尔斯·桑德斯·皮尔士（Charles Sanders Peirce，符号–对象–
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
