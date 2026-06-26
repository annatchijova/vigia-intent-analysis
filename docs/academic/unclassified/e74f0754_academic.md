<!-- VIGÍA Academic Documentation | Module: convert_synthetic_cases.py | Hash: e74f0754 | Format: Standardized v1 -->

## ENGLISH

### What Is This Module?

`convert_synthetic_cases.py` (VIGÍA hash `e74f0754`) is a deterministic schema migration engine that converts synthetic forensic datasets from the deprecated VIGIA-SYN v1 format into the canonical Evidentiary Batch Standard (EBS) v1 format. These synthetic cases were generated during the April production cycle as controlled evidentiary proxies for algorithmic validation, adversarial robustness testing, and calibration of the Analytical Correlation (AC) pipeline. Because the legacy VIGIA-SYN v1 schema uses obsolete field ontologies, non-canonical temporal encodings, and forensic-score normalization routines that diverge semantically from EBS v1 expectations, direct ingestion of legacy artifacts into current workflows is architecturally precluded.

The module applies a total mapping function Φ = Φ_prov ∘ Φ_score ∘ Φ_struct where: Φ_struct provides injective structural canonicalization (no field is lost or aliased); Φ_score is a deterministic affine vector transformation v_new = A·v_old + b with rational matrix A ∈ ℚ^{m×n} and bias b ∈ ℚ^m, implemented using Python's `fractions.Fraction` to avoid IEEE 754 rounding variance; and Φ_prov appends an immutable audit digest SHA-256(s ∥ module_hash ∥ timestamp_canonical ∥ schema_version). Deterministic UUID v5 identifiers are generated for canonical case IDs. No pseudo-random number generators, OS entropy sources, or timing-based jitter are used anywhere in the algorithm.

The module treats synthetic cases as forensic evidence without qualification, applying the same integrity-preservation rigor expected for naturalistic digital exhibits.

### Key Concepts

| Concept | Definition |
|---------|-----------|
| Total mapping Φ | Φ = Φ_prov ∘ Φ_score ∘ Φ_struct; deterministic, lossless, bitwise-reproducible migration from VIGIA-SYN v1 to EBS v1 |
| Φ_struct (structural canonicalization) | Injective mapping of legacy fields onto EBS v1 relational model; no field lost, aliased, or ambiguously merged |
| Φ_score (score recalibration) | Affine transformation v_new = A·v_old + b with A ∈ ℚ^{m×n}, b ∈ ℚ^m; implemented via fractions.Fraction |
| Rational arithmetic (ℚ) | All intermediate computations in the rational number field; IEEE 754 variance confined to final serialization step only |
| Φ_prov (provenance augmentation) | Appends audit digest = SHA-256(s ∥ module_hash ∥ timestamp_canonical ∥ schema_version) |
| UUID version 5 | Deterministic UUID derived from SHA-1(case_id ∥ VIGÍA_namespace); identical inputs always yield identical IDs |
| VIGIA-SYN v1 record s | Input tuple ⟨case_id, t_gen, h_src, v_legacy, m_bundle, c_legacy⟩ |
| EBS v1 entity e | Output tuple ⟨ebs_case_uuid, t_canon, d_prov, v_new, m_norm, h_integ, τ_audit⟩ |
| decimal.ROUND_HALF_EVEN | Rounding mode used at final serialization; arithmetic nondeterminism confined to this single controlled step |

> **【Scientific Note】**
> Phrases like "rational matrix" and "affine transformation" can sound abstract, but the operation is equivalent to a unit conversion with a calibration offset — the same calculation a laboratory instrument performs when converting raw sensor readings to calibrated measurements in standard units. A rational matrix A ∈ ℚ^{m×n} is simply a conversion table whose entries are exact fractions (e.g., 3/4, 7/100) rather than floating-point approximations. Using Python's `fractions.Fraction` instead of IEEE 754 floats ensures that the conversion table does not introduce measurement rounding error that varies by CPU architecture. Peirce's semiotics, Eco's overinterpretation theory, and Grice's cooperative principle describe *why* forensic signals need to be preserved faithfully across schema migrations — this module is the engineering implementation of that requirement: exact arithmetic, no stochastic steps, immutable provenance.

### Glossary

| Term | Definition |
|------|-----------|
| convert_synthetic_cases.py | Module performing deterministic, lossless migration of VIGIA-SYN v1 synthetic forensic datasets to EBS v1 format |
| VIGIA-SYN v1 | Deprecated synthetic forensic dataset schema from the April production cycle |
| EBS v1 (Evidentiary Batch Standard) | Canonical format required by the AC analytical pipeline and downstream VIGÍA components |
| affine transformation | Linear map v_new = A·v_old + b; here A and b are rational-valued for exact arithmetic |
| fractions.Fraction | Python stdlib type providing exact rational arithmetic; used during all intermediate score computations |
| UUID v5 | Deterministic UUID derived from SHA-1 of a namespace + name; identical inputs produce identical UUIDs |
| temporal canonicalization | Phase II: legacy timestamps parsed to monotonic UNIX epoch nanoseconds and re-serialized as RFC 3339 with explicit UTC offset |
| provenance augmentation | Phase V: SHA-256 audit digest binding the output to its input source hash and module identity |
| AC analytical pipeline | Downstream consumer requiring EBS v1 canonical inputs for correlation analysis and evidential weighting |

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## ESPAÑOL

### ¿Qué es este módulo?

`convert_synthetic_cases.py` (hash VIGÍA `e74f0754`) es un motor determinista de migración de esquemas que convierte conjuntos de datos forenses sintéticos del formato deprecado VIGIA-SYN v1 al formato canónico Evidentiary Batch Standard (EBS) v1. Estos casos sintéticos fueron generados durante el ciclo productivo de abril como proxies probatorios controlados para validación algorítmica, pruebas de robustez adversarial y calibración del pipeline de Correlación Analítica (AC). Dado que el esquema legacy VIGIA-SYN v1 emplea ontologías de campo obsoletas, codificaciones temporales no canónicas y rutinas de normalización de puntuaciones forenses que divergen semánticamente de las expectativas de EBS v1, la ingesta directa de artefactos legacy en los flujos de trabajo actuales está arquitectónicamente vedada.

El módulo aplica una función de mapeo total Φ = Φ_prov ∘ Φ_score ∘ Φ_struct donde: Φ_struct provee canonicalización estructural inyectiva (ningún campo se pierde ni se alíasa); Φ_score es una transformación afín vectorial determinista v_new = A·v_old + b con matriz racional A ∈ ℚ^{m×n} y sesgo b ∈ ℚ^m, implementada con `fractions.Fraction` de Python para evitar la varianza de redondeo IEEE 754; y Φ_prov adjunta un resumen de auditoría inmutable SHA-256(s ∥ module_hash ∥ timestamp_canonical ∥ schema_version). Los identificadores UUID v5 deterministas se generan para los identificadores canónicos de caso. No se usan generadores de números pseudoaleatorios, fuentes de entropía del sistema operativo ni fluctuaciones basadas en temporización en ninguna parte del algoritmo.

El módulo trata los casos sintéticos como evidencia forense sin calificación, aplicando el mismo rigor de preservación de integridad que se esperaría para exhibiciones digitales naturalistas.

### Conceptos clave

| Concepto | Definición |
|---------|-----------|
| Mapeo total Φ | Φ = Φ_prov ∘ Φ_score ∘ Φ_struct; migración determinista, sin pérdidas y bit a bit reproducible de VIGIA-SYN v1 a EBS v1 |
| Φ_struct (canonicalización estructural) | Mapeo inyectivo de campos legacy al modelo relacional EBS v1; ningún campo se pierde, alíasa o fusiona ambiguamente |
| Φ_score (recalibración de puntuaciones) | Transformación afín v_new = A·v_old + b con A ∈ ℚ^{m×n}, b ∈ ℚ^m; implementada vía fractions.Fraction |
| Aritmética racional (ℚ) | Todos los cálculos intermedios en el cuerpo numérico racional; varianza IEEE 754 confinada solo al paso final de serialización |
| Φ_prov (aumento de procedencia) | Adjunta resumen de auditoría = SHA-256(s ∥ module_hash ∥ timestamp_canonical ∥ schema_version) |
| UUID versión 5 | UUID determinista derivado de SHA-1(case_id ∥ VIGÍA_namespace); entradas idénticas siempre producen IDs idénticos |
| Registro VIGIA-SYN v1 s | Tupla de entrada ⟨case_id, t_gen, h_src, v_legacy, m_bundle, c_legacy⟩ |
| Entidad EBS v1 e | Tupla de salida ⟨ebs_case_uuid, t_canon, d_prov, v_new, m_norm, h_integ, τ_audit⟩ |
| decimal.ROUND_HALF_EVEN | Modo de redondeo usado en la serialización final; el no-determinismo aritmético está confinado a este único paso controlado |

> **【Nota Científica】**
> Expresiones como "matriz racional" y "transformación afín" pueden sonar abstractas, pero la operación es equivalente a una conversión de unidades con un offset de calibración — el mismo cálculo que realiza un instrumento de laboratorio al convertir lecturas brutas del sensor en mediciones calibradas en unidades estándar. Una matriz racional A ∈ ℚ^{m×n} es simplemente una tabla de conversión cuyos valores son fracciones exactas (por ejemplo, 3/4, 7/100) en lugar de aproximaciones de punto flotante. El uso de `fractions.Fraction` de Python en lugar de flotantes IEEE 754 garantiza que la tabla de conversión no introduzca error de redondeo que varíe según la arquitectura de la CPU. La semiótica de Peirce, la teoría de la sobreinterpretación de Eco y el principio cooperativo de Grice describen *por qué* las señales forenses deben preservarse fielmente a través de las migraciones de esquemas — este módulo es la implementación de ingeniería de ese requisito: aritmética exacta, sin pasos estocásticos, procedencia inmutable.

### Glosario

| Término | Definición |
|--------|-----------|
| convert_synthetic_cases.py | Módulo que realiza migración determinista y sin pérdidas de conjuntos de datos forenses sintéticos VIGIA-SYN v1 al formato EBS v1 |
| VIGIA-SYN v1 | Esquema de conjunto de datos forenses sintéticos deprecado del ciclo productivo de abril |
| EBS v1 (Evidentiary Batch Standard) | Formato canónico requerido por el pipeline analítico AC y los componentes downstream de VIGÍA |
| transformación afín | Mapeo lineal v_new = A·v_old + b; aquí A y b son de valores racionales para aritmética exacta |
| fractions.Fraction | Tipo de la stdlib de Python que provee aritmética racional exacta; usado en todos los cálculos intermedios de puntuaciones |
| UUID v5 | UUID determinista derivado de SHA-1(namespace + nombre); entradas idénticas producen UUIDs idénticos |
| canonicalización temporal | Fase II: timestamps legacy analizados a nanosegundos UNIX monótonos y re-serializados como RFC 3339 con offset UTC explícito |
| aumento de procedencia | Fase V: resumen de auditoría SHA-256 que vincula la salida con el hash de fuente de entrada y la identidad del módulo |
| pipeline analítico AC | Consumidor downstream que requiere entradas canónicas EBS v1 para análisis de correlación y ponderación probatoria |

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## РУССКИЙ

### Что представляет собой этот модуль?

`convert_synthetic_cases.py` (хеш VIGÍA `e74f0754`) — детерминированный механизм миграции схем, выполняющий перевод синтетических форензических датасетов из устаревшего формата VIGIA-SYN v1 в канонический формат Evidentiary Batch Standard (EBS) v1. Указанные синтетические кейсы были сгенерированы в апрельском производственном цикле в качестве контролируемых доказательственных суррогатов для алгоритмической валидации, тестирования адверсариальной устойчивости и калибровки конвейера аналитической корреляции (AC). Поскольку устаревшая схема VIGIA-SYN v1 использует депрецированные онтологии полей, неканонические форматы временны́х меток и процедуры нормализации судебных оценок, семантически расходящиеся с требованиями EBS v1, прямая инжестия унаследованных артефактов в актуальные рабочие потоки архитектурно исключена.

Модуль применяет тотальную функцию отображения Φ = Φ_prov ∘ Φ_score ∘ Φ_struct, где: Φ_struct обеспечивает инъективную структурную каноникализацию (ни одно поле не теряется и не псевдонимизируется); Φ_score — детерминированное аффинное векторное преобразование v_new = A·v_old + b с рациональной матрицей A ∈ ℚ^{m×n} и смещением b ∈ ℚ^m, реализованное с использованием `fractions.Fraction` Python во избежание вариативности округления IEEE 754; Φ_prov присоединяет неизменяемый аудиторский дайджест SHA-256(s ∥ module_hash ∥ timestamp_canonical ∥ schema_version). Детерминированные UUID v5 генерируются для канонических идентификаторов дел. Нигде в алгоритме не используются генераторы псевдослучайных чисел, источники энтропии ОС или временнóе дрожание.

Модуль рассматривает синтетические кейсы как форензические доказательства без оговорок, применяя тот же уровень строгости в части сохранения целостности, который ожидается для натуралистических цифровых объектов.

### Ключевые понятия

| Понятие | Определение |
|---------|------------|
| Тотальное отображение Φ | Φ = Φ_prov ∘ Φ_score ∘ Φ_struct; детерминированная, безпотерьная, побитово воспроизводимая миграция из VIGIA-SYN v1 в EBS v1 |
| Φ_struct (структурная каноникализация) | Инъективное отображение унаследованных полей на реляционную модель EBS v1; ни одно поле не теряется, не псевдонимизируется |
| Φ_score (перекалибровка оценок) | Аффинное преобразование v_new = A·v_old + b с A ∈ ℚ^{m×n}, b ∈ ℚ^m; реализовано через fractions.Fraction |
| Рациональная арифметика (ℚ) | Все промежуточные вычисления в поле рациональных чисел; вариативность IEEE 754 ограничена только финальным шагом сериализации |
| Φ_prov (дополнение провенанса) | Присоединяет аудиторский дайджест = SHA-256(s ∥ module_hash ∥ timestamp_canonical ∥ schema_version) |
| UUID версии 5 | Детерминированный UUID, производный от SHA-1(case_id ∥ VIGÍA_namespace); идентичные входные данные всегда дают идентичные ID |
| Запись VIGIA-SYN v1 s | Входной кортеж ⟨case_id, t_gen, h_src, v_legacy, m_bundle, c_legacy⟩ |
| Сущность EBS v1 e | Выходной кортеж ⟨ebs_case_uuid, t_canon, d_prov, v_new, m_norm, h_integ, τ_audit⟩ |
| decimal.ROUND_HALF_EVEN | Режим округления при финальной сериализации; арифметический недетерминизм ограничен этим единственным контролируемым шагом |

> **【Научное примечание】**
> Такие выражения, как «рациональная матрица» и «аффинное преобразование», могут звучать абстрактно, но операция эквивалентна конверсии единиц с калибровочным смещением — тем же вычислением, которое выполняет лабораторный прибор при переводе сырых показаний датчика в откалиброванные измерения в стандартных единицах. Рациональная матрица A ∈ ℚ^{m×n} — это просто таблица преобразования, элементы которой представляют собой точные дроби (например, 3/4, 7/100), а не приближения с плавающей точкой. Использование `fractions.Fraction` Python вместо чисел IEEE 754 гарантирует, что таблица преобразования не вносит погрешности округления, варьирующейся в зависимости от архитектуры ЦПУ. Семиотика Пирса, теория сверхинтерпретации Эко и принцип кооперации Грайса описывают *то, почему* форензические сигналы должны достоверно сохраняться при миграции схем — данный модуль является инженерной реализацией этого требования: точная арифметика, отсутствие стохастических шагов, неизменяемый провенанс.

### Глоссарий

| Термин | Определение |
|--------|------------|
| convert_synthetic_cases.py | Модуль, выполняющий детерминированную, безпотерьную миграцию синтетических форензических датасетов VIGIA-SYN v1 в формат EBS v1 |
| VIGIA-SYN v1 | Устаревшая схема синтетических форензических датасетов апрельского производственного цикла |
| EBS v1 (Evidentiary Batch Standard) | Канонический формат, требуемый аналитическим конвейером AC и нижестоящими компонентами VIGÍA |
| аффинное преобразование | Линейное отображение v_new = A·v_old + b; здесь A и b имеют рациональные значения для точной арифметики |
| fractions.Fraction | Тип stdlib Python, обеспечивающий точную рациональную арифметику; используется при всех промежуточных вычислениях оценок |
| UUID v5 | Детерминированный UUID, производный от SHA-1(пространство_имён + имя); идентичные входные данные дают идентичные UUID |
| каноникализация временны́х меток | Фаза II: унаследованные метки разбираются в монотонные наносекунды эпохи UNIX и ресериализуются как RFC 3339 с явным UTC-смещением |
| дополнение провенанса | Фаза V: аудиторский дайджест SHA-256, связывающий выход с хешем входного источника и идентичностью модуля |
| аналитический конвейер AC | Нижестоящий потребитель, требующий канонических входных данных EBS v1 для корреляционного анализа и взвешивания доказательственной значимости |

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## 中文

### 本模块是什么？

`convert_synthetic_cases.py`（VIGÍA 哈希值 `e74f0754`）是一个确定性模式迁移引擎，将合成取证数据集从已弃用的 VIGIA-SYN v1 格式无损且按位可复现地迁移至规范性的证据批次标准（EBS）v1 格式。这些合成案例由 VIGÍA 框架的早期版本在四月份生产周期中生成，作为受控的证据代理（evidentiary proxy），用于算法验证、对抗鲁棒性测试以及分析相关性（AC）分析流程的校准。由于遗留架构 VIGIA-SYN v1 采用已弃用的字段本体、非规范的时间编码以及语义上与 EBS v1 预期不一致的取证评分归一化例程，此类遗留取证工件无法直接输入当代工作流。

本模块应用全映射函数 Φ = Φ_prov ∘ Φ_score ∘ Φ_struct，其中：Φ_struct 提供单射结构规范化（无字段丢失或混淆）；Φ_score 是确定性仿射向量变换 v_new = A·v_old + b，其中有理矩阵 A ∈ ℚ^{m×n}、偏置 b ∈ ℚ^m，通过 Python 的 `fractions.Fraction` 实现以避免 IEEE 754 舍入差异；Φ_prov 附加不可变审计摘要 SHA-256(s ∥ module_hash ∥ timestamp_canonical ∥ schema_version)。规范案例 ID 使用确定性 UUID v5 生成。算法中不使用任何伪随机数生成器、操作系统熵源或基于时序的抖动。

本模块将合成案例视为取证证据本身，应用与自然数字检材同等严格的完整性保持要求。

### 关键概念

| 概念 | 定义 |
|------|------|
| 全映射 Φ | Φ = Φ_prov ∘ Φ_score ∘ Φ_struct；VIGIA-SYN v1 至 EBS v1 的确定性、无损、按位可复现迁移 |
| Φ_struct（结构规范化） | 将遗留字段以单射方式映射至 EBS v1 关系模型；无字段丢失、混淆或歧义合并 |
| Φ_score（评分重校准） | 仿射变换 v_new = A·v_old + b，A ∈ ℚ^{m×n}，b ∈ ℚ^m；通过 fractions.Fraction 实现 |
| 有理数算术（ℚ） | 所有中间运算在有理数域中进行；IEEE 754 差异仅限于最终序列化步骤 |
| Φ_prov（溯源增强） | 附加审计摘要 = SHA-256(s ∥ module_hash ∥ timestamp_canonical ∥ schema_version) |
| UUID 版本 5 | 由 SHA-1(case_id ∥ VIGÍA_命名空间) 确定性派生的 UUID；相同输入始终产生相同 ID |
| VIGIA-SYN v1 记录 s | 输入元组 ⟨case_id, t_gen, h_src, v_legacy, m_bundle, c_legacy⟩ |
| EBS v1 实体 e | 输出元组 ⟨ebs_case_uuid, t_canon, d_prov, v_new, m_norm, h_integ, τ_audit⟩ |
| decimal.ROUND_HALF_EVEN | 最终序列化时使用的舍入模式（银行家舍入）；算术非确定性仅限于此单一受控步骤 |

> **【科学说明】**
> "有理矩阵"和"仿射变换"等表述可能听起来抽象，但其操作等同于带校准偏移量的单位换算——与实验室仪器将传感器原始读数转换为标准单位校准测量值时所做的计算完全相同。有理矩阵 A ∈ ℚ^{m×n} 不过是一张换算表，其条目为精确分数（例如 3/4、7/100），而非浮点近似值。使用 Python 的 `fractions.Fraction` 而非 IEEE 754 浮点数，确保换算表不会引入因 CPU 架构而异的测量舍入误差。皮尔斯符号学、艾柯的过度诠释理论以及格赖斯的合作原则阐明了*为何*取证信号在模式迁移中必须被忠实保留——本模块是这一要求的工程实现：精确算术、无随机步骤、不可变溯源。

### 术语表

| 术语 | 定义 |
|------|------|
| convert_synthetic_cases.py | 将 VIGIA-SYN v1 合成取证数据集确定性、无损迁移至 EBS v1 格式的模块 |
| VIGIA-SYN v1 | 四月份生产周期中已弃用的合成取证数据集模式 |
| EBS v1（证据批次标准） | AC 分析管线及 VIGÍA 下游组件要求的规范格式 |
| 仿射变换 | 线性映射 v_new = A·v_old + b；此处 A 和 b 为有理值以保证精确算术 |
| fractions.Fraction | Python 标准库类型，提供精确有理数算术；用于所有中间评分计算 |
| UUID v5 | 由 SHA-1(命名空间 + 名称) 确定性派生的 UUID；相同输入产生相同 UUID |
| 时间规范化 | 阶段 II：遗留时间戳解析为单调递增 UNIX 纪元纳秒，重新序列化为带显式 UTC 偏移的 RFC 3339 格式 |
| 溯源增强 | 阶段 V：SHA-256 审计摘要，将输出与输入源哈希及模块身份绑定 |
| AC 分析管线 | 需要规范 EBS v1 输入进行相关性分析和证据权重计算的下游消费者 |

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
