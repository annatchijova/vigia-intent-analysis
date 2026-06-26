<!--
VIGIA Academic Documentation
Module: 91f2a764
Batch ID: vigia-doc-0129-91f2a764
Generated: 2026-05-20T14:56:47.872334+00:00
-->

## ENGLISH

### What Is This Module?

`vigia/sift/_math_utils.py` is the deterministic arithmetic core of the VIGÍA digital-forensic signal-sifting system. It processes evidence traces (forensic artifacts) using exact rational-number arithmetic (the `Fraction` type) rather than approximated representations. Every internal operation—scoring, conflict resolution, entropy calculation, and square-root iteration—remains in the rational number domain until the final export step. Scientists can treat it as a reproducible scoring laboratory: the same input always yields the same score, with no hardware-dependent drift.

The module implements six interrelated capabilities: (1) safe conversion of boundary float inputs to exact fractions; (2) correlated evidence fusion via the Noisy-OR model; (3) source-reliability weighting; (4) redundancy group construction and scoring; (5) conflict detection with dominance-preserving penalty; and (6) Newton-Raphson square-root iteration over rational operands. All constants (`LN2`, `RESISTANCE_FACTOR`, `EPS`) are stored as exact `Fraction` objects. The only point at which a numeric value crosses the rational boundary is the final `SignalOutput` constructor, which accepts a bounded float for compatibility with downstream interfaces.

### Key Concepts

| Concept | Forensic Role | Deterministic Mechanism |
|---|---|---|
| **Exact Rational Arithmetic** | Core computation engine | All scores stored as integer numerator/denominator pairs (`Fraction`). No rounding occurs during fusion, penalty, or entropy steps. |
| **Resistance Factor (R)** | Anti-silencing safeguard | A rational multiplier that protects non-dominant signals from being extinguished by the dominant one. |
| **Conflict Penalty** | Contradiction management | Penalizes subordinate (non-dominant) artifacts only; the dominant signal's rank is preserved as an invariant. |
| **Newton Sqrt for Fractions** | Exact iterative root | Integer-step Newton-Raphson refinement converges to a rational bound within `EPS`; no intermediate approximation. |
| **Shannon Entropy** | Uncertainty measure | Computed directly from an integer-frequency list via exact rational logarithms; no serialization or float accumulation. |
| **TOCTOU Hardening** | Timestamp integrity | `_parse_iso_timestamp` raises an explicit exception on failure; a silent zero return is forbidden, eliminating time-of-check/time-of-use race conditions. |
| **Safe Float Clamp** | Input sanitization | `clamp_float_to_fraction` forces the input into a bounded integer interval before rational conversion, preventing `OverflowError`. |
| **Dominance Stability Test** | Post-condition check | After any penalty, an explicit invariant verifies that the dominant artifact remains dominant. |

### Functions

| Function | Purpose | Deterministic Guarantee |
|---|---|---|
| `clamp_float_to_fraction` | Boundary-limited float-to-Fraction conversion | Clamps to `[min_val, max_val]` using integer bounds; overflow impossible. |
| `noisy_or_correlated` | Correlated evidence fusion | Combines artifact likelihoods via Noisy-OR model using rational probability bounds. |
| `apply_artifact_reliability` | Reliability weighting | Multiplies raw signal by a source-reliability coefficient expressed as an exact fraction. |
| `build_redundancy_groups` | Evidence clustering | Groups artifacts by deterministic correlation keys; output depends only on input content, not iteration order. |
| `apply_frs` | Redundancy scoring | Computes the Forensic Redundancy Score as a rational aggregate of group members. |
| `classify_group` | Group typing | Assigns a deterministic label (e.g., consistent, contradictory) based on rational thresholds. |
| `apply_conflict_penalty` | Anti-silencing correction | Computes `WEIGHTED_SCORE = z × Γ × R`, where `R` is the Resistance Factor. Penalty applied to non-dominant artifacts only; dominant signal never penalized. |
| `partition_contradictory_group` | Dominance-based splitting | Separates a contradictory group into dominant and non-dominant subsets using exact score comparisons. |
| `process_all_groups` | Full analysis pipeline | Enforces processing precedence `CONFLICT > FRS`. Runs dominance-stability validation after penalty application. |

### Constants

| Constant | Meaning | Value Type |
|---|---|---|
| `LN2` | Natural logarithm of 2 | Exact `Fraction`; used in Shannon entropy. |
| `RESISTANCE_FACTOR` | Resistance multiplier `R` | Exact `Fraction`; prevents signal silencing. |
| `EPS` | Convergence tolerance | Exact `Fraction`; termination bound for Newton iteration. |
| `MAX_ITER` | Iteration ceiling | Integer; safety limit for Newton-Raphson loops. |

### Glossary

1. **Forensic Artifact** — A discrete unit of digital evidence (e.g., a log entry, hash, timestamp) submitted for scoring.
2. **Dominant Signal** — The artifact or group possessing the highest rational score within a given comparison set; treated as the reference state during conflict resolution.
3. **Signal Silencing** — The unwanted suppression of a minority evidence trace when it contradicts a stronger trace. The Resistance Factor `R` corrects this.
4. **Resistance Factor (R)** — A rational coefficient that scales non-dominant scores upward during conflict penalty, preserving their audible weight in the final fusion.
5. **TOCTOU** — Time-of-check/time-of-use; a race condition where evidence state changes between validation and processing. Hardened here by explicit parse exceptions.
6. **Invariant** — A logical condition that must hold true after an operation. Here: the dominant artifact before penalty must remain dominant after penalty.
7. **Fraction (Rational)** — A number represented as a pair of integers (numerator, denominator), yielding exact results under addition, multiplication, and comparison.
8. **Noisy-OR** — A probabilistic fusion model for correlated sources; implemented here with rational bounds to retain determinism.
9. **Logical Fracture** — A state where combined evidence yields an internal contradiction; resolved by partitioning and penalizing the weaker side.
10. **Forensic Redundancy Score (FRS)** — A rational aggregate score rewarding convergent evidence from independent sources, computed without intermediate approximation.

> **【Scientific Note】**
> This module uses concepts from Charles Sanders Peirce (sign–object–interpretant), Umberto Eco (code and overcoding), and H. Paul Grice (conversational maxims). These are **operational analogues to sensor-calibration parameters**, not mystical or literary constructs. A **Peircean interpretant** is the measurable change in the score function produced by a given trace. An **Eco-style code** is the formal likelihood mapping between a system state and its evidentiary output. A **Gricean maxim** is a hard constraint on signal combination; violating it produces a detectable **logical fracture** in the evidence stream, analogous to a sensor array returning incompatible readings from overlapping fields of view. Researchers should view these labels as formal names for fusion rules, comparable to calibration matrices in multi-sensor data assimilation.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## ESPAÑOL

### ¿Qué es este módulo?

`vigia/sift/_math_utils.py` es el núcleo aritmético determinista del sistema de cribado de señales forenses digitales de VIGÍA. Procesa trazas de evidencia (artefactos forenses) mediante aritmética de números racionales exacta (tipo `Fraction`) en lugar de representaciones aproximadas. Cada operación interna —puntuación, resolución de conflictos, cálculo de entropía e iteración de raíz cuadrada— permanece en el dominio de los racionales hasta el paso de exportación final. El investigador puede tratarlo como un laboratorio de puntuación reproducible: la misma entrada siempre produce la misma puntuación, sin variación dependiente del hardware.

El módulo implementa seis capacidades interrelacionadas: (1) conversión segura de flotantes límite a fracciones exactas; (2) fusión de evidencia correlacionada mediante el modelo Noisy-OR; (3) ponderación por fiabilidad de fuente; (4) construcción y puntuación de grupos de redundancia; (5) detección de conflictos con penalización que preserva la dominancia; y (6) iteración Newton-Raphson de raíz cuadrada sobre operandos racionales. Todas las constantes (`LN2`, `RESISTANCE_FACTOR`, `EPS`) se almacenan como objetos `Fraction` exactos.

### Conceptos clave

| Concepto | Rol forense | Mecanismo determinista |
|---|---|---|
| **Aritmética racional exacta** | Motor de cálculo | Todas las puntuaciones son pares de enteros (numerador/denominador). No hay redondeo durante la fusión, penalización o entropía. |
| **Factor de Resistencia (R)** | Protección anti-silenciamiento | Multiplicador racional que evita que señales no dominantes sean extinguidas. |
| **Penalización por Conflicto** | Gestión de contradicciones | Se aplica solo a artefactos subordinados; la señal dominante se preserva invariante. |
| **Raíz cuadrada de Newton (Fracción)** | Refinamiento exacto | Método de Newton-Raphson con pasos enteros; convergencia racional dentro de `EPS`. |
| **Entropía de Shannon** | Medida de incertidumbre | Cálculo directo sobre lista de frecuencias enteras; sin serialización. |
| **Endurecimiento TOCTOU** | Integridad de marca temporal | El parser falla explícitamente; devolver 0 en silencio está prohibido. |
| **Clampeo seguro** | Sanitización de entrada | `clamp_float_to_fraction` acota el valor a `[min, max]` antes de convertir a fracción. |
| **Prueba de estabilidad de dominancia** | Verificación post-operación | Invariante: el artefacto dominante antes de la penalización sigue siéndolo después. |

### Funciones

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

### Constantes

| Constante | Significado | Tipo |
|---|---|---|
| `LN2` | Logaritmo natural de 2 | `Fraction` exacta; usada en entropía. |
| `RESISTANCE_FACTOR` | Multiplicador de resistencia `R` | `Fraction` exacta. |
| `EPS` | Tolerancia de convergencia | `Fraction` exacta; límite de parada de Newton. |
| `MAX_ITER` | Tope de iteraciones | Entero; límite de seguridad. |

### Glosario

1. **Artefacto forense** — Unidad discreta de evidencia digital (registro, hash, marca temporal).
2. **Señal dominante** — Artefacto o grupo con la puntuación racional más alta; referencia en resolución de conflictos.
3. **Silenciamiento de señal** — Supresión indeseada de una traza minoritaria. El Factor R lo corrige.
4. **Factor de Resistencia (R)** — Coeficiente racional que escala las puntuaciones no dominantes durante la penalización.
5. **TOCTOU** — Condición de carrera entre comprobación y uso; mitigada mediante excepciones explícitas.
6. **Invariante** — Condición lógica que debe cumplirse tras una operación. Aquí: la dominancia se mantiene.
7. **Fracción (racional)** — Número como par de enteros (numerador, denominador); resultados exactos.
8. **Noisy-OR** — Modelo de fusión para fuentes correlacionadas; implementado con cotas racionales.
9. **Fractura lógica** — Estado de contradicción interna en evidencias combinadas; resuelta particionando el lado más débil.
10. **Puntuación de Redundancia Forense (FRS)** — Agregado racional que recompensa evidencias convergentes de fuentes independientes.

> **【Nota Científica】**
> Este módulo utiliza conceptos de Charles Sanders Peirce (signo–objeto–interpretante), Umberto Eco (código y sobrecodificación) y H. Paul Grice (máximas conversacionales). Se trata de **analogías operacionales a parámetros de calibración de sensores**, no construcciones místicas o literarias. Un **interpretante peirceano** es el cambio medible en la función de puntuación producido por una traza. Un **código en sentido ecológico** es el mapeo formal de verosimilitud entre un estado del sistema y su salida probatoria. Una **máxima griceana** es una restricción dura sobre la combinación de señales; su violación produce una **fractura lógica** en el flujo de evidencias, análoga a una matriz de sensores que devuelve lecturas incompatibles en campos de vista solapados. El investigador debe entender estas etiquetas como nombres formales de reglas de fusión, comparables a matrices de calibración en la asimilación de datos multi-sensor.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## РУССКИЙ

### Что представляет собой этот модуль?

`vigia/sift/_math_utils.py` — детерминированное арифметическое ядро системы цифровой криминалистической сортировки сигналов VIGÍA. Модуль обрабатывает следовые записи доказательств (криминалистические артефакты) с использованием точной арифметики рациональных чисел (тип `Fraction`), а не приближённых представлений. Каждая внутренняя операция — оценка, разрешение конфликтов, вычисление энтропии и итерация квадратного корня — остаётся в рациональном домене до финального шага экспорта. Исследователи могут воспринимать его как воспроизводимую лабораторию оценки: одни и те же входные данные всегда дают один и тот же результат, без аппаратно-зависимого дрейфа.

Модуль реализует шесть взаимосвязанных возможностей: (1) безопасное преобразование граничных значений float в точные дроби; (2) слияние коррелированных доказательств по модели Noisy-OR; (3) взвешивание по надёжности источника; (4) построение групп избыточности и их оценка; (5) обнаружение конфликтов со штрафом, сохраняющим доминирование; (6) итерация Newton-Raphson для квадратного корня над рациональными операндами. Все константы хранятся как точные объекты `Fraction`.

### Ключевые понятия

| Понятие | Криминалистическая роль | Детерминированный механизм |
|---|---|---|
| **Точная рациональная арифметика** | Вычислительное ядро | Все оценки — пары целых чисел (числитель/знаменатель). Округление отсутствует. |
| **Фактор сопротивления (R)** | Защита от подавления сигнала | Рациональный множитель, предотвращающий гашение недоминирующих сигналов. |
| **Штраф за конфликт** | Разрешение противоречий | Накладывается только на подчинённые артефакты; доминирующий сигнал сохраняется инвариантно. |
| **Квадратный корень Ньютона (дробный)** | Точное итеративное приближение | Целочисленный метод Ньютона–Рафсона; сходимость в рациональной границе `EPS`. |
| **Энтропия Шеннона** | Мера неопределённости | Прямое вычисление по списку целочисленных частот; без сериализации. |
| **Упрочнение TOCTOU** | Целостность меток времени | Парсер явно выбрасывает исключение при ошибке; запрещено тихое возвращение 0. |
| **Безопасное ограничение (clamp)** | Очистка входных данных | `clamp_float_to_fraction` ограничивает значение `[min, max]` до рационального преобразования. |
| **Проверка стабильности доминирования** | Постусловие | Явный инвариант: доминирующий артефакт после штрафа остаётся доминирующим. |

### Функции

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
| `process_all_groups` | Полный конвейер | Приоритет `CONFLICT > FRS`; валидация инварианта после штрафа. |

### Константы

| Константа | Значение | Тип |
|---|---|---|
| `LN2` | Натуральный логарифм 2 | Точная `Fraction`; для энтропии. |
| `RESISTANCE_FACTOR` | Множитель сопротивления `R` | Точная `Fraction`. |
| `EPS` | Допуск сходимости | Точная `Fraction`; критерий остановки Ньютона. |
| `MAX_ITER` | Потолок итераций | Целое; предохранительный лимит. |

### Глоссарий

1. **Криминалистический артефакт** — Дискретная единица цифрового доказательства (запись, хэш, метка времени).
2. **Доминирующий сигнал** — Артефакт или группа с наивысшей рациональной оценкой; эталон при разрешении конфликтов.
3. **Подавление сигнала** — Нежелательное гашение миноритарной следовой записи. Фактор R устраняет это.
4. **Фактор сопротивления (R)** — Рациональный коэффициент, масштабирующий недоминирующие оценки при конфликтном штрафе.
5. **TOCTOU** — Состояние гонки между проверкой и использованием; устранено явными исключениями.
6. **Инвариант** — Логическое условие, обязательное после операции. Здесь: доминантность сохраняется.
7. **Fraction (рациональное число)** — Число как пара целых (числитель, знаменатель); точные результаты.
8. **Noisy-OR** — Вероятностная модель слияния коррелированных источников; реализована рациональными границами.
9. **Логический разрыв** — Состояние внутреннего противоречия комбинированных доказательств; разрешается разделением слабой стороны.
10. **Оценка криминалистической избыточности (FRS)** — Рациональный агрегат, вознаграждающий конвергентные доказательства из независимых источников.

> **【Научное примечание】**
> Модуль использует терминологию Чарльза Сандерса Пирса (знак–объект–интерпретант), Умберто Эко (код и overcoding) и Г. П. Грайса (конверсациональные максимы). Это **операциональные аналоги параметров калибровки сенсоров**, а не мистические или литературные конструкты. **Пирсовский интерпретант** — измеримое изменение функции оценки, вызванное данной следовой записью. **Код в смысле Эко** — формальное отображение правдоподобия между состоянием системы и её доказательственным выходом. **Грайсовская максима** — жёсткое ограничение на комбинирование сигналов; её нарушение порождает обнаружимый **логический разрыв** в потоке доказательств, аналогичный ситуации, когда массив датчиков возвращает несовместимые показания в перекрывающихся полях зрения.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## 中文

### 本模块是什么？

`vigia/sift/_math_utils.py` 是 VIGÍA 数字取证信号筛分系统的确定性算术核心。它使用精确有理数算术（`Fraction` 类型）而非近似表示来处理证据痕迹（取证工件）。每个内部操作——评分、冲突解决、熵计算和平方根迭代——在最终导出步骤之前均保持在有理数域内。科学家可以将其视为可重现的评分实验室：相同输入始终产生相同分数，不存在硬件依赖的漂移。

模块实现六个相互关联的能力：(1) 将边界浮点输入安全转换为精确分数；(2) 通过 Noisy-OR 模型融合相关证据；(3) 来源可靠性加权；(4) 冗余组构建与评分；(5) 保留主导性的冲突检测与惩罚；(6) 有理操作数上的牛顿-拉夫逊平方根迭代。所有常量（`LN2`、`RESISTANCE_FACTOR`、`EPS`）均存储为精确 `Fraction` 对象。

### 核心概念

| 概念 | 取证作用 | 确定性机制 |
|---|---|---|
| **精确有理数运算** | 计算引擎 | 所有分数以整数对（分子/分母）存储，融合、惩罚与熵计算过程中无任何舍入。 |
| **阻抗因子 (R)** | 防信号压制 | 有理数乘数，防止非主导信号被主导信号湮灭。 |
| **冲突惩罚** | 矛盾管理 | 仅对从属取证工件施加惩罚；主导信号的排名保持不变量。 |
| **牛顿开方（分数版）** | 精确迭代求根 | 整数步进牛顿-拉夫逊迭代，在 `EPS` 有理数界限内收敛。 |
| **香农熵** | 不确定度量化 | 直接基于整数频率列表计算，采用精确有理对数；无序列化或浮点累加。 |
| **TOCTOU 加固** | 时间戳完整性 | `_parse_iso_timestamp` 在解析失败时显式抛出异常；禁止静默返回 0。 |
| **安全浮点钳制** | 输入消毒 | `clamp_float_to_fraction` 在转换为分数前将输入钳制于整数区间，防止 `OverflowError`。 |
| **主导稳定性测试** | 后置条件验证 | 显式不变量：惩罚操作后，主导取证工件仍保持主导地位。 |

### 函数

| 函数 | 用途 | 确定性保证 |
|---|---|---|
| `clamp_float_to_fraction` | 安全的浮点到分数转换 | 整数边界钳制；不可能发生溢出。 |
| `noisy_or_correlated` | 相关证据融合 | 通过有理概率界限实现 Noisy-OR 模型。 |
| `apply_artifact_reliability` | 来源可靠性加权 | 以精确有理系数乘以原始信号。 |
| `build_redundancy_groups` | 证据聚类 | 依据确定性相关键分组；输出仅取决于输入内容。 |
| `apply_frs` | 冗余度评分 | 以精确有理数聚合计算取证冗余分数 (FRS)。 |
| `classify_group` | 群组分类 | 基于有理阈值赋予确定性标签。 |
| `apply_conflict_penalty` | 反信号压制修正 | 计算 `WEIGHTED_SCORE = z × Γ × R`，仅对非主导工件惩罚。 |
| `partition_contradictory_group` | 按主导性拆分 | 利用精确分数比较，将矛盾群组分为主导子集与从属子集。 |
| `process_all_groups` | 完整分析流水线 | 强制优先级：`CONFLICT > FRS`；惩罚后执行主导稳定性验证。 |

### 常量

| 常量 | 含义 | 值类型 |
|---|---|---|
| `LN2` | 2 的自然对数 | 精确 `Fraction`；用于香农熵。 |
| `RESISTANCE_FACTOR` | 阻抗乘数 `R` | 精确 `Fraction`；防止信号压制。 |
| `EPS` | 收敛容差 | 精确 `Fraction`；牛顿迭代终止界。 |
| `MAX_ITER` | 迭代上限 | 整数；安全循环限制。 |

### 术语表

1. **取证工件** — 数字证据的离散单元（如日志条目、哈希值、时间戳），作为评分输入。
2. **主导信号** — 在比较集合中拥有最高有理分数的取证工件或群组；在冲突解决中作为参考态。
3. **信号压制** — 少数证据痕迹被更强痕迹压制的不期望现象。阻抗因子 `R` 予以纠正。
4. **阻抗因子 (R)** — 冲突惩罚期间按比例放大非主导分数的有理系数。
5. **TOCTOU** — 检查时间与使用时间之间的竞争条件；本模块通过显式异常进行加固。
6. **不变量** — 操作后必须成立的逻辑条件。此处指：惩罚前的主导工件在惩罚后仍为主导。
7. **分数（有理数）** — 以整数对（分子、分母）表示的数，其加减乘除与比较结果完全精确。
8. **Noisy-OR** — 用于相关源的概率融合模型；此处采用有理界限实现以保持确定性。
9. **逻辑断裂** — 组合证据产生内部矛盾的状态；通过拆分并惩罚较弱一方予以解决。
10. **取证冗余分数 (FRS)** — 奖励来自独立来源的收敛证据的有理聚合分数，无中间近似计算。

> **【科学说明】**
> 本模块借用了查尔斯·桑德斯·皮尔士（符号–对象–解释项）、艾柯（代码与超编码）和格赖斯（会话准则）的术语框架。这些是**传感器校准参数的操作类比**，而非神秘或文学构建物。**皮尔斯的解释项**是特定痕迹对评分函数产生的可测量变化。**艾柯意义上的代码**是系统状态与其证据输出之间的形式似然映射。**格赖斯的准则**是信号组合上的硬性约束；违反它会在证据流中产生可检测的**逻辑断裂**，类似于传感器阵列在重叠视野中返回不相容读数。研究人员应将这些标签视为融合规则的正式名称，与多传感器数据同化中的校准矩阵相当。

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
