## ENGLISH

### What Is This Module?

The module `vigia/tools/build_calibration_dataset.py` constitutes a foundational data-engineering component of the VIGÍA forensic analysis architecture, purpose-built to assemble, validate, and serialize the labeled evidentiary corpus required for the calibration of downstream classification pipelines. Within the epistemological framework of digital forensics, a discriminative classifier yields raw scores that do not, by themselves, constitute statistically valid posterior probabilities. To satisfy the evidentiary reliability criteria articulated in the Daubert standard—particularly the requirement that scientific testimony pertain to a technique with a known and reproducible error rate—these scores must be transformed via a dedicated calibration stage. This module executes the antecedent data-construction pipeline, producing the calibration dataset $\mathcal{D}_{\text{cal}}$ that enables `fit_calibration.py` to learn a mapping from uncalibrated outputs to well-calibrated probability estimates. Its design is strictly confined to deterministic symbolic and discrete operations; it performs no floating-point optimization, no stochastic gradient descent, and no numerical convergence routines.

Mathematically, the module operates over a finite evidence space $\mathcal{E}$ populated by digital artifacts drawn from two distinct provenance classes: $\mathcal{C}_{\text{BEN}}$ (authentic, benign evidentiary units, label $y = 0$) and $\mathcal{C}_{\text{REAL}}$ (fabricated or manipulated units, label $y = 1$). The ground-truth labeling function $\lambda: \mathcal{C} \to \{0, 1\}$ is deterministic and total. For each evidentiary unit $c$, a SHA-256 digest $h(c)$ is computed, inducing a strict total order $\preceq_h$ via lexicographic comparison of hexadecimal digest strings. This hash-based ordering is essential because filesystem enumeration order is operating-system-dependent and therefore non-deterministic. Per-class proportions are stored and validated as exact rational pairs $(N_y, N)$, computed by pure integer counting; no floating-point rounding is permitted in the stratification logic.

### Key Concepts

| Concept | Definition | Technical Role |
|---|---|---|
| **Ground-truth label** | Integer $y \in \{0, 1\}$ assigned deterministically by $\lambda$ | Binary encoding isomorphic to the Bernoulli outcome space used by calibration algorithms |
| **SHA-256 hash-based ordering** | Strict total order $\preceq_h$ on $\mathcal{C}$ via lexicographic hex comparison | Eliminates OS-dependent filesystem enumeration non-determinism |
| **Exact rational stratification** | Per-class proportions stored as integer pairs $(N_y, N)$ | Prevents representational drift that could perturb class balance |
| **Cryptographic manifest** | Pre-computed SHA-256 digests from `vigia/pipeline/validate_chain.py` | Anchors chain of custody from upstream collection through dataset construction |
| **Calibration dataset $\mathcal{D}_{\text{cal}}$** | Ordered $n$-tuple $(h(c_i), \lambda(c_i), m(c_i))$ | Input to `fit_calibration.py` for learning score-to-probability mapping |
| **Idempotent serialization** | Re-running the pipeline on the same inputs produces bit-identical output | Satisfies Daubert reproducibility and GB/T 29360-2012 integrity requirements |
| **Per-class minimum $N_{\min}^{(y)}$** | Integer floor on examples per class | Prevents degenerate calibration datasets with insufficient coverage |

### Algorithm Description

The algorithm proceeds through six deterministic phases:

1. **Corpus Ingestion and Manifest Validation.** Reads `corpus_ben/` and `corpus_real/` directory trees and reconciles every file against upstream cryptographic manifests $M_{\text{BEN}}$ and $M_{\text{REAL}}$. Any digest mismatch, missing file, or manifest violation triggers a logged rejection with a hexadecimal failure code; silent record dropping is architecturally impossible.

2. **Cryptographic Fingerprinting.** Computes SHA-256 digest $h(c)$ for each evidentiary unit $c$. This digest serves as the collision-resistant addressing key and the primary sort key for the total order $\preceq_h$.

3. **Deterministic Labeling.** Applies $\lambda(c) = 0$ to all units in `corpus_ben/` and $\lambda(c) = 1$ to all units in `corpus_real/`. The labeling function is a pure mapping with no external state dependency.

4. **Stratification and Cardinality Enforcement.** Computes $N_y = |\{c : \lambda(c) = y\}|$ for each $y \in \{0,1\}$ using integer counting. Validates per-class minima $N_{\min}^{(y)}$ and, when configured, exact proportion targets $\rho_y = N_y / N$ stored as rational pairs.

5. **Deterministic Ordering and Metadata Assembly.** Sorts all accepted units under $\preceq_h$. For each $c_i$ in the sorted sequence, assembles metadata $m(c_i)$ containing provenance identifiers, file-format assertions, temporal stamps, and deferred feature-extraction references.

6. **Schema-Locked Serialization.** Serializes $\mathcal{D}_{\text{cal}}$ to JSON Lines or Apache Parquet with strict atomic typing (ISO 8601:2019 timestamps, UTF-8 strings, integer labels). Emits the dual-digest attestation $\langle h(c_{\text{first}}), h(c_{\text{last}}) \rangle$ and the rule manifest version to the audit subsystem.

### Glossary

1. **Calibration Dataset** — A labeled corpus used to learn a monotone mapping from raw classifier scores to well-calibrated probability estimates.
2. **Ground-Truth Label** — An integer in $\{0, 1\}$ assigned deterministically to each evidentiary unit based on its provenance class.
3. **SHA-256 Digest** — A 256-bit cryptographic fingerprint of a file's contents, used as a collision-resistant key and sort criterion.
4. **Stratification** — The process of enforcing per-class cardinality constraints on a dataset, computed here by exact integer counting.
5. **Idempotence** — A property of the pipeline: re-running it on the same inputs under the same configuration yields bit-identical output.
6. **Cryptographic Manifest** — A pre-computed registry of SHA-256 digests linking each evidentiary unit to its upstream chain of custody.
7. **Exact Rational Proportion** — A class balance expressed as an integer pair $(N_y, N)$, avoiding floating-point rounding in stratification logic.
8. **Lexicographic Hash Order** — The total order $\preceq_h$ obtained by comparing hexadecimal SHA-256 digest strings character-by-character.
9. **Daubert Standard** — U.S. Federal Rules of Evidence criterion requiring scientific techniques to have testability, peer review, known error rate, and general acceptance.
10. **Chain of Custody** — The unbroken, timestamped record of all actions taken on evidence from collection through dataset construction.

> **【Scientific Note】**
> Peirce's Firstness in this module is each raw evidentiary unit $c$ before any classification—the pure digital phenomenon. Secondness is the labeling function $\lambda(c)$: the binary, dyadic reaction that assigns the unit to one of two provenance classes based on immutable origin metadata. Thirdness is the total order $\preceq_h$ and the stratification rule: the repeatable law that determines which units enter the calibration dataset and in what sequence, producing the same ordered set on the same corpus in every execution. Eco's encyclopedia principle ensures that labels $y = 0$ (AUTHENTIC) and $y = 1$ (FABRICATED) have single, unambiguous definitions across all VIGÍA modules, preventing semantic drift in downstream calibration. Grice's maxim of Quantity guarantees that $\mathcal{D}_{\text{cal}}$ contains exactly the evidence it claims to contain: the dual-digest attestation and the cardinality record are not summaries but exact cryptographic witnesses.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## ESPAÑOL

### ¿Qué es este módulo?

El módulo `vigia/tools/build_calibration_dataset.py` constituye un componente fundamental de ingeniería de datos de la arquitectura forense VIGÍA, diseñado específicamente para ensamblar, validar y serializar el corpus probatorio etiquetado requerido para la calibración de los flujos de clasificación downstream. Para satisfacer los criterios de confiabilidad evidenciaría del estándar Daubert, los puntajes crudos de un clasificador discriminativo deben transformarse mediante una etapa de calibración dedicada. Este módulo ejecuta el flujo de construcción de datos previo, produciendo el conjunto de datos de calibración $\mathcal{D}_{\text{cal}}$ que permite a `fit_calibration.py` aprender un mapeo de salidas sin calibrar a estimaciones de probabilidad bien calibradas. Su diseño está estrictamente confinado a operaciones simbólicas y discretas deterministas; no realiza optimización de punto flotante, descenso de gradiente estocástico ni rutinas de convergencia numérica.

Matemáticamente, el módulo opera sobre un espacio de evidencias finito $\mathcal{E}$ poblado por artefactos digitales de dos clases de procedencia distintas: $\mathcal{C}_{\text{BEN}}$ (unidades auténticas, etiqueta $y = 0$) y $\mathcal{C}_{\text{REAL}}$ (unidades fabricadas o manipuladas, etiqueta $y = 1$). Las proporciones por clase se almacenan y validan como pares racionales exactos $(N_y, N)$, computados por conteo entero puro; no se permite redondeo de punto flotante en la lógica de estratificación.

### Conceptos clave

| Concepto | Definición | Rol técnico |
|---|---|---|
| **Etiqueta de verdad fundamental** | Entero $y \in \{0, 1\}$ asignado deterministamente por $\lambda$ | Codificación binaria isomorfa al espacio de resultados de Bernoulli |
| **Ordenamiento por hash SHA-256** | Orden total estricto $\preceq_h$ sobre $\mathcal{C}$ por comparación hexadecimal | Elimina el no determinismo de enumeración del sistema de archivos |
| **Estratificación racional exacta** | Proporciones por clase almacenadas como pares enteros $(N_y, N)$ | Previene la deriva representacional que podría perturbar el balance de clases |
| **Manifiesto criptográfico** | Resúmenes SHA-256 precomputados de `vigia/pipeline/validate_chain.py` | Ancla la cadena de custodia desde la recolección hasta la construcción del conjunto |
| **Conjunto de calibración $\mathcal{D}_{\text{cal}}$** | $n$-tupla ordenada $(h(c_i), \lambda(c_i), m(c_i))$ | Entrada para `fit_calibration.py` |
| **Serialización idempotente** | Reejecutar el flujo en las mismas entradas produce salida bit a bit idéntica | Satisface la reproducibilidad Daubert y los requisitos de integridad GB/T 29360-2012 |
| **Mínimo por clase $N_{\min}^{(y)}$** | Piso entero de ejemplos por clase | Previene conjuntos de calibración degenerados |

### Descripción del algoritmo

El algoritmo procede en seis fases deterministas: (1) Ingesta del corpus y validación del manifiesto, conciliando cada archivo contra resúmenes SHA-256 precomputados; (2) Huella digital criptográfica, computando $h(c)$ para cada unidad; (3) Etiquetado determinista mediante $\lambda$; (4) Estratificación y control de cardinalidad mediante conteo entero exacto; (5) Ordenamiento determinista bajo $\preceq_h$ y ensamblaje de metadatos; (6) Serialización bloqueada por esquema con atestación de doble resumen.

### Glosario

1. **Conjunto de calibración** — Corpus etiquetado para aprender un mapeo monótono de puntajes crudos a estimaciones de probabilidad bien calibradas.
2. **Etiqueta de verdad fundamental** — Entero en $\{0, 1\}$ asignado deterministamente a cada unidad evidenciaría según su clase de procedencia.
3. **Resumen SHA-256** — Huella digital criptográfica de 256 bits, usada como clave sin colisiones y criterio de ordenamiento.
4. **Estratificación** — Proceso de imponer restricciones de cardinalidad por clase, computadas aquí por conteo entero exacto.
5. **Idempotencia** — Propiedad del flujo: reejecución sobre las mismas entradas produce salida bit a bit idéntica.
6. **Manifiesto criptográfico** — Registro precomputado de resúmenes SHA-256 que vincula cada unidad a su cadena de custodia upstream.
7. **Proporción racional exacta** — Balance de clases expresado como par entero $(N_y, N)$, evitando redondeo de punto flotante.
8. **Orden lexicográfico de hashes** — Orden total $\preceq_h$ obtenido comparando cadenas hexadecimales SHA-256 carácter a carácter.
9. **Estándar Daubert** — Criterio de las Reglas Federales de Evidencia de EE. UU. que exige comprobabilidad, revisión por pares, tasa de error conocida y aceptación general.
10. **Cadena de custodia** — Registro ininterrumpido y con marca temporal de todas las acciones tomadas sobre la evidencia desde la recolección hasta la construcción del conjunto de datos.

> **【Nota Científica】**
> La Primereidad de Peirce en este módulo es cada unidad evidenciaría cruda $c$ antes de cualquier clasificación — el fenómeno digital puro. La Segundidad es la función de etiquetado $\lambda(c)$: la reacción binaria, diádica, que asigna la unidad a una de dos clases de procedencia basándose en metadatos de origen inmutables. La Terceridad es el orden total $\preceq_h$ y la regla de estratificación: la ley repetible que determina qué unidades ingresan al conjunto de calibración y en qué secuencia, produciendo el mismo conjunto ordenado sobre el mismo corpus en cada ejecución. El principio de enciclopedia de Eco garantiza que las etiquetas $y = 0$ (AUTÉNTICO) e $y = 1$ (FABRICADO) tienen definiciones únicas e inequívocas en todos los módulos de VIGÍA. La máxima de Cantidad de Grice garantiza que $\mathcal{D}_{\text{cal}}$ contiene exactamente la evidencia que afirma contener: la atestación de doble resumen y el registro de cardinalidad son testigos criptográficos exactos, no resúmenes.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## РУССКИЙ

### Что представляет собой этот модуль?

Модуль `vigia/tools/build_calibration_dataset.py` составляет фундаментальный компонент инженерии данных архитектуры криминалистического анализа VIGÍA, специально созданный для сборки, валидации и сериализации размеченного доказательственного корпуса, необходимого для калибровки нисходящих классификационных конвейеров. Для удовлетворения требований доказательственной надёжности стандарта Daubert исходные оценки дискриминативного классификатора должны быть преобразованы посредством специального этапа калибровки. Данный модуль выполняет предшествующий конвейер построения данных, производя калибровочный набор данных $\mathcal{D}_{\text{cal}}$, который позволяет `fit_calibration.py` обучить отображение из нескалиброванных выходов в хорошо откалиброванные оценки вероятности. Его дизайн строго ограничен детерминированными символическими и дискретными операциями; он не выполняет оптимизации с плавающей точкой, стохастического спуска градиента и процедур численной сходимости.

Математически модуль работает над конечным пространством доказательств $\mathcal{E}$, населённым цифровыми артефактами из двух классов происхождения: $\mathcal{C}_{\text{BEN}}$ (подлинные единицы, метка $y = 0$) и $\mathcal{C}_{\text{REAL}}$ (изготовленные или манипулированные единицы, метка $y = 1$). Пропорции по классам хранятся и валидируются как точные рациональные пары $(N_y, N)$, вычисленные чистым целочисленным счётом; округление с плавающей точкой в логике стратификации не допускается.

### Ключевые концепции

| Концепция | Определение | Техническая роль |
|---|---|---|
| **Метка истины** | Целое число $y \in \{0, 1\}$, детерминированно назначаемое $\lambda$ | Бинарное кодирование, изоморфное пространству исходов Бернулли |
| **Упорядочение по хэшу SHA-256** | Строгий полный порядок $\preceq_h$ над $\mathcal{C}$ через лексикографическое сравнение hex | Устраняет недетерминизм перечисления файловой системы |
| **Точная рациональная стратификация** | Пропорции по классам как целочисленные пары $(N_y, N)$ | Предотвращает дрейф представления, способный нарушить баланс классов |
| **Криптографический манифест** | Предвычисленные SHA-256 дайджесты из `vigia/pipeline/validate_chain.py` | Якорит цепочку сохранения от upstream-сбора до построения набора данных |
| **Калибровочный набор $\mathcal{D}_{\text{cal}}$** | Упорядоченный $n$-кортеж $(h(c_i), \lambda(c_i), m(c_i))$ | Вход для `fit_calibration.py` |
| **Идемпотентная сериализация** | Повторный запуск на тех же входах даёт побитово идентичный выход | Удовлетворяет Daubert и GB/T 29360-2012 |
| **Минимум по классу $N_{\min}^{(y)}$** | Целочисленный нижний предел примеров на класс | Предотвращает вырожденные калибровочные наборы |

### Алгоритмическое описание

Алгоритм проходит шесть детерминированных фаз: (1) Поглощение корпуса и валидация манифеста, согласование каждого файла с предвычисленными SHA-256 дайджестами; (2) Криптографическое фингерпринтирование, вычисление $h(c)$ для каждой единицы; (3) Детерминированная разметка через $\lambda$; (4) Стратификация и контроль кардинальности через точный целочисленный счёт; (5) Детерминированное упорядочение под $\preceq_h$ и сборка метаданных; (6) Сериализация с фиксацией схемы с аттестацией двойного дайджеста.

### Глоссарий

1. **Калибровочный набор данных** — Размеченный корпус для обучения монотонного отображения исходных оценок в хорошо откалиброванные оценки вероятности.
2. **Метка истины** — Целое число из $\{0, 1\}$, детерминированно назначаемое каждой доказательственной единице по её классу происхождения.
3. **Дайджест SHA-256** — 256-битный криптографический отпечаток содержимого файла, используемый как устойчивый к коллизиям ключ и критерий сортировки.
4. **Стратификация** — Процесс обеспечения ограничений кардинальности по классам, вычисляемых здесь точным целочисленным счётом.
5. **Идемпотентность** — Свойство конвейера: повторный запуск на тех же входах под той же конфигурацией даёт побитово идентичный выход.
6. **Криптографический манифест** — Предвычисленный реестр SHA-256 дайджестов, связывающий каждую доказательственную единицу с upstream-цепочкой сохранения.
7. **Точная рациональная пропорция** — Баланс классов, выраженный как целочисленная пара $(N_y, N)$, исключающая округление с плавающей точкой.
8. **Лексикографический порядок хэшей** — Полный порядок $\preceq_h$, получаемый побуквенным сравнением шестнадцатеричных строк SHA-256.
9. **Стандарт Daubert** — Критерий Федеральных правил доказательств США, требующий проверяемости, экспертного рецензирования, известной частоты ошибок и общепризнанности.
10. **Цепочка сохранения** — Непрерывный, отмеченный временем журнал всех действий, предпринятых в отношении доказательств от сбора до построения набора данных.

> **【Научное примечание】**
> Первичность Пирса в данном модуле — каждая необработанная доказательственная единица $c$ до любой классификации: чистый цифровой феномен. Вторичность — функция разметки $\lambda(c)$: бинарная, диадическая реакция, назначающая единицу одному из двух классов происхождения на основе неизменяемых метаданных источника. Третичность — полный порядок $\preceq_h$ и правило стратификации: повторяемый закон, определяющий, какие единицы входят в калибровочный набор и в каком порядке, производя одинаковый упорядоченный набор на одном и том же корпусе при каждом исполнении. Принцип энциклопедии Эко гарантирует, что метки $y = 0$ (ПОДЛИННОЕ) и $y = 1$ (ИЗГОТОВЛЕННОЕ) имеют единственные, недвусмысленные определения во всех модулях VIGÍA. Максима Количества Грайса гарантирует, что $\mathcal{D}_{\text{cal}}$ содержит ровно те доказательства, которые заявляет содержать: аттестация двойного дайджеста и запись кардинальности — точные криптографические свидетели, а не резюме.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## 中文

### 本模块是什么？

`vigia/tools/build_calibration_dataset.py` 模块是 VIGÍA 取证分析架构的基础数据工程组件，专门用于组装、验证和序列化下游分类流水线校准所需的标注证据语料库。为满足道伯特标准中关于具有已知可重现误差率的科学证明要求，判别分类器的原始分数必须通过专用校准阶段进行转换。本模块执行前置数据构建流水线，产生校准数据集 $\mathcal{D}_{\text{cal}}$，使 `fit_calibration.py` 能够学习从未校准输出到经良好校准概率估计的映射。其设计严格限于确定性符号和离散操作；不执行浮点优化、随机梯度下降或数值收敛程序。

数学上，模块在由来自两个不同来源类别的数字取证工件填充的有限证据空间 $\mathcal{E}$ 上运作：$\mathcal{C}_{\text{BEN}}$（真实、良性证据单元，标签 $y = 0$）和 $\mathcal{C}_{\text{REAL}}$（伪造或被篡改的单元，标签 $y = 1$）。类别比例以精确有理数对 $(N_y, N)$ 存储和验证，通过纯整数计数计算；分层逻辑中不允许浮点舍入。

### 关键概念

| 概念 | 定义 | 技术作用 |
|---|---|---|
| **基准真值标签** | 由 $\lambda$ 确定性分配的整数 $y \in \{0, 1\}$ | 与校准算法使用的伯努利结果空间同构的二进制编码 |
| **基于 SHA-256 哈希的排序** | 通过十六进制词典比较在 $\mathcal{C}$ 上的严格全序 $\preceq_h$ | 消除依赖操作系统的文件系统枚举不确定性 |
| **精确有理分层** | 类别比例存储为整数对 $(N_y, N)$ | 防止可能扰乱类别平衡的表示漂移 |
| **密码清单** | 来自 `vigia/pipeline/validate_chain.py` 的预计算 SHA-256 摘要 | 将监管链从上游采集锚定至数据集构建 |
| **校准数据集 $\mathcal{D}_{\text{cal}}$** | 有序 $n$ 元组 $(h(c_i), \lambda(c_i), m(c_i))$ | `fit_calibration.py` 的输入 |
| **幂等序列化** | 在相同输入上重新运行流水线产生位相同输出 | 满足道伯特可重现性和 GB/T 29360-2012 完整性要求 |
| **每类最小值 $N_{\min}^{(y)}$** | 每类示例的整数下限 | 防止覆盖不足的退化校准数据集 |

### 算法描述

算法经六个确定性阶段执行：(1) 语料库摄入与清单验证，将每个文件对照预计算的 SHA-256 摘要进行核对；(2) 密码学指纹，为每个单元计算 $h(c)$；(3) 通过 $\lambda$ 确定性标注；(4) 通过精确整数计数进行分层和基数控制；(5) 在 $\preceq_h$ 下确定性排序并组装元数据；(6) 带双重摘要证明的模式锁定序列化。

### 术语表

1. **校准数据集** — 用于学习原始分数到经良好校准概率估计的单调映射的标注语料库。
2. **基准真值标签** — 确定性分配给每个证据单元的 $\{0, 1\}$ 中的整数，基于其来源类别。
3. **SHA-256 摘要** — 文件内容的 256 位密码指纹，用作无碰撞键和排序准则。
4. **分层** — 对数据集强制执行每类基数约束的过程，此处通过精确整数计数计算。
5. **幂等性** — 流水线属性：在相同配置下对相同输入重新运行产生位相同输出。
6. **密码清单** — SHA-256 摘要的预计算注册表，将每个证据单元与其上游监管链链接。
7. **精确有理比例** — 以整数对 $(N_y, N)$ 表示的类别平衡，避免分层逻辑中的浮点舍入。
8. **哈希词典序** — 通过逐字符比较十六进制 SHA-256 摘要字符串获得的全序 $\preceq_h$。
9. **道伯特标准** — 美国联邦证据规则标准，要求科学技术具有可测试性、同行评审、已知误差率和普遍接受性。
10. **监管链** — 从采集到数据集构建对证据采取的所有行动的不间断带时间戳记录。

> **【科学说明】**
> 皮尔斯的初性在本模块中是每个原始证据单元 $c$ 在任何分类之前的状态——纯粹的数字现象。二性是标注函数 $\lambda(c)$：将单元基于不可变来源元数据分配至两个来源类别之一的二元二极性反应。三性是全序 $\preceq_h$ 和分层规则：决定哪些单元进入校准数据集以及以何种顺序的可重复规律，在每次执行时对同一语料库产生相同的有序集合。艾柯的百科全书原则确保标签 $y = 0$（真实）和 $y = 1$（伪造）在所有 VIGÍA 模块中各有唯一明确的定义，防止下游校准中的语义漂移。格赖斯的量的准则保证 $\mathcal{D}_{\text{cal}}$ 恰好包含其声称包含的证据：双重摘要证明和基数记录是精确的密码学证人，而非摘要。

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
