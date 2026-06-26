## ENGLISH

**Case Execution Controller (`scripts/run_case.py`)**

**1. Module Purpose and Architectural Role**

Within the VIGÍA forensic framework, `scripts/run_case.py` functions as the deterministic orchestration nucleus for single-case investigative pipelines. Its architectural mandate is to instantiate exactly one forensic case, enforce a totally ordered, sequential processing regime over the evidence object space, and emit a complete, tamper-evident execution metadata record. Unlike general-purpose workflow engines that may tolerate out-of-order execution, speculative parallelism, or dynamic task scheduling, this module is intentionally constrained to eliminate algorithmic uncertainty at the control-plane level. It occupies the stratum between the framework's case-management layer and its evidence-processing micro-modules, translating a declarative case manifest into an imperative, reproducible sequence of computational steps. By binding all case-specific state transitions to an integer-indexed evidence sequence, the module guarantees that independent executions commencing from identical initial conditions traverse bitwise-identical execution paths, thereby satisfying the reproducibility prerequisites stipulated under the Daubert standard for scientific evidence, the traceability mandates of GB/T 29360-2012, and the accountability controls of China's Multi-Level Protection Scheme (MLPS 2.0).

**2. Mathematical Foundations**

The formal semantics of the module can be expressed through a deterministic discrete-state finite automaton operating over an ordered evidence domain.

Let a forensic case $\mathcal{C}$ be defined as a strictly ordered 3-tuple:
$$\mathcal{C} = (\mathcal{P}, \mathcal{E}, \mathcal{M}_0)$$
where:
- $\mathcal{P} \in \mathbb{P}$ denotes the parameter configuration drawn from the VIGÍA policy space $\mathbb{P}$, encompassing a globally unique case identifier, examiner credentials, canonical workspace paths, and forensic policy flags.
- $\mathcal{E} = (e_1, e_2, \ldots, e_n)$ is an evidence sequence of length $n \in \mathbb{N}_0$, strictly indexed by the bijective integer map $idx: \{1, \ldots, n\} \to \mathcal{E}$. Each $e_i$ represents an immutable evidence object.
- $\mathcal{M}_0 = \emptyset$ is the initial metadata accumulator.

The controller implements a deterministic transition system $\mathcal{T} = (S, s_0, \delta)$, where:
- $S$ is the finite state space of the case execution environment.
- $s_0 = \text{INIT}(\mathcal{P})$ is the unique initial state derived exclusively from $\mathcal{P}$ via a pure function.
- $\delta: S \times \mathcal{E} \to S$ is the total state-transition function.

For a given case $\mathcal{C}$, the execution trace $\tau$ is the sequence of states:
$$\tau = (s_0, s_1, \ldots, s_n)$$
such that for each $i \in \{1, \ldots, n\}$:
$$s_i = \delta(s_{i-1}, e_i)$$

**Determinism Axiom.** The module enforces:
$$\forall \mathcal{P} \in \mathbb{P}, \forall \mathcal{E}, |\delta^*(s_0, \mathcal{E})| = 1$$
where $\delta^*$ denotes the reflexive-transitive closure of $\delta$. Consequently, the execution trace $\tau$ and the final metadata accumulator $\mathcal{M}_n$ are unique functions of $(\mathcal{P}, \mathcal{E})$.

Integer indexing is not merely an implementation convenience but a foundational requirement. By decoupling the iteration order from filesystem enumeration semantics or memory-address-dependent data structures (e.g., unhashed set iteration), the module eliminates a prevalent source of non-determinism in forensic pipelines. The evidence sequence $\mathcal{E}$ is materialized through a sorted manifest whose primary key is an unsigned integer, ensuring that the mapping $idx$ remains invariant across executions.

**3. Algorithm Description**

The algorithm proceeds through four strictly ordered phases.

*Phase I: Case Initialization.* The controller ingests the case manifest $\mathcal{M}_f$ (a UTF-8 JSON document conforming to the VIGÍA schema v2.1) and materializes the parameter structure $\mathcal{P}$. It computes a canonical workspace directory $W$ and sets the initial state $s_0$. A pre-execution exclusive lock is acquired on $W$ to preclude concurrent modification, thereby preserving sequential consistency. All dependent VIGÍA modules referenced in $\mathcal{P}$ (e.g., `modules/hash_validator.py`, `modules/chain_of_custody.py`) are probed for availability and version compatibility; any discrepancy triggers a fatal error with exit code 2.

*Phase II: Evidence Ingestion and Manifest Sequencing.* The evidence manifest $\mathcal{E}_f$ is parsed into the sequence $\mathcal{E}$. The parser enforces the integer bijection $idx$; any duplicate or missing index triggers a fatal initialization error. The sequence is loaded into memory as an immutable ordered tuple, not a dynamic array subject to pointer-reallocation variance.

*Phase III: Sequential Processing.* For each $i$ from $1$ to $n$ in strict ascending order:
1. The controller dispatches $e_i$ to `scripts/ingest_evidence.py`, which returns a validated in-memory representation $e'_i$.
2. The hash validation submodule (`modules/hash_validator.py`) computes the cryptographic digest $H(e'_i)$, typically SHA-256, and compares it against the manifest's ground truth.
3. A forensic transformation $\alpha_i$ is applied. This may include file carving, entropy analysis, or feature extraction, delegated to specialized worker modules. The controller itself remains agnostic to $\alpha_i$'s internal mechanics but mandates that all workers operate under the same deterministic contract.
4. The output $o_i$ and associated metadata $m_i$ (including sequence number $i$, digest $H(e'_i)$, and monotonic timestamp $t_i$) are appended to $\mathcal{M}_{i-1}$ to form $\mathcal{M}_i$.
5. State update: $s_i \leftarrow \delta(s_{i-1}, m_i)$.

Error handling within this phase is policy-driven. Under the default strict policy, any exception or hash mismatch aborts the trace, preserving the partial metadata log $\mathcal{M}_{i-1}$ for forensic inspection. Under the permissive policy, the error is logged and the controller proceeds to $i+1$.

*Phase IV: Finalization and Audit-Trail Emission.* Upon completion of the loop, the controller computes an aggregate integrity code:
$$H_{\text{agg}} = \mathcal{H}(m_1 \| m_2 \| \cdots \| m_n)$$
where $\|$ denotes unambiguous concatenation and $\mathcal{H}$ is the configured hash function. The aggregate metadata $\mathcal{M}_n$, execution trace digest, and termination status $\xi$ are written to the audit trail via `lib/audit_logger.py`. If `modules/crypto_signer.py` is available, the trail is cryptographically signed to provide non-repudiation. The workspace lock is released, and the process terminates with exit code $\xi \in \{0, 1, 2\}$.

**4. Input/Output Specifications**

*Inputs:*
- **Case Manifest** (`case_manifest.json`): A UTF-8 encoded JSON document containing $\mathcal{P}$. Mandatory fields include `case_id` (UUIDv4 string), `examiner_did` (decentralized identifier), `policy_profile` (string enum), and `workspace_root` (absolute path).
- **Evidence Manifest** (`evidence_manifest.json` or `evidence_manifest.csv`): A structured listing of evidence objects. Each record must contain an `evidence_id` (unsigned 64-bit integer), `source_path` (string), and `ground_truth_hash` (hexadecimal string).
- **Execution Context** (`context.json`, optional): Read-only environmental overrides, including `PYTHONHASHSEED` and `clock_source`.

*Outputs:*
- **Execution Log** (`execution.log`): JSON Lines format, one record per evidence object, containing $m_i$.
- **Metadata Database** (`metadata.db`): SQLite snapshot of $\mathcal{M}_n$, indexed by `evidence_id`.
- **Audit Trail** (`audit_trail.json`): Cryptographically signed (when `modules/crypto_signer.py` is available) attestation of $H_{\text{agg}}$ and $\xi$.
- **Exit Codes**: `0` indicates successful completion of all $n$ steps; `1` indicates a processing failure during Phase III; `2` indicates an initialization or schema validation failure in Phase I.

**5. Deterministic Guarantees and Forensic Rigor**

The module provides deterministic guarantees at multiple layers:

*Bitwise Reproducibility.* Given identical inputs $(\mathcal{P}, \mathcal{E}, \mathcal{M}_f, \mathcal{E}_f)$ and identical versions of all downstream worker modules, two executions on different host systems produce bit-identical output artifacts ($\mathcal{M}_n$, execution log, audit trail). This property is contingent upon:
- Exclusion of non-deterministic language primitives (e.g., unseeded random number generation, unordered set iteration).
- Canonical serialization order of JSON keys and CSV columns.
- Stable sorting of any intermediate aggregations.

*Temporal Determinism.* Internal control flow never depends on wall-clock time. Sequence ordering is governed by the integer index $i$, while metadata timestamps $t_i$ are either monotonic counters or deterministic mocked values in testing environments. Wall-clock timestamps are recorded solely as non-functional annotations.

*Environmental Isolation.* The module reads `PYTHONHASHSEED` from `context.json` and sets it explicitly before any data-structure initialization, eliminating hash-randomized iteration order (introduced by default in Python 3.3+). This environmental control ensures that the integer index $i$ is the sole determinant of processing order.

**6. Key Concepts**

| Concept | Definition | Technical Role |
|---|---|---|
| **Deterministic transition system** | $\mathcal{T} = (S, s_0, \delta)$ over ordered evidence | Eliminates algorithmic uncertainty at the control-plane level |
| **Integer evidence index** | Bijective map $idx: \{1,\ldots,n\} \to \mathcal{E}$ | Ensures processing order is invariant across filesystems and architectures |
| **Aggregate integrity code** | $H_{\text{agg}} = \mathcal{H}(m_1 \| m_2 \| \cdots \| m_n)$ | Non-repudiable attestation of the complete execution trace |
| **SHA-256 chain of custody** | Cryptographic digest chained across each evidence object | Satisfies Daubert traceability and GB/T 29360-2012 integrity requirements |
| **Monotonic timestamp** | Integer counter used for ordering, not logical control | Separates evidentiary sequencing from wall-clock dependency |
| **Policy profile** | `strict` or `permissive` execution mode | Governs error handling in Phase III without altering the deterministic execution path |

### 【Scientific Note】
Peirce's Firstness maps to Phase II: the evidence manifest is read as a raw, uninterpreted integer sequence—pure phenomenological reception with no judgment applied. Secondness is Phase III: each $e_i$ is differentially processed against the cryptographic ground truth in the manifest, producing a binary matching result (digest match / mismatch). Thirdness is the aggregate integrity code $H_{\text{agg}}$: the repeatable law that binds the entire execution trace into a single, auditable output regardless of which evidential items were processed. Eco's encyclopedia principle guarantees that `evidence_id` and `ground_truth_hash` have single, unambiguous definitions across all VIGÍA worker modules, preventing aliasing of distinct evidentiary objects. Grice's maxim of Manner is operationalized by the integer index $i$: the module reports the processing order in an unambiguous, strictly sequenced format, eliminating any interpretive ambiguity about which artifact was processed at which step.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## ESPAÑOL

**Controlador de Ejecución de Casos (`scripts/run_case.py`)**

### 1. Propósito del módulo y rol arquitectónico
Dentro del marco forense VIGÍA, `scripts/run_case.py` funciona como el núcleo de orquestación determinista para canalizaciones de investigación de un solo caso. Su mandato arquitectónico es instanciar exactamente un caso forense, imponer un régimen de procesamiento secuencial totalmente ordenado sobre el espacio de objetos de evidencia y emitir un registro de metadatos de ejecución completo y a prueba de manipulaciones. El módulo ocupa el estrato entre la capa de gestión de casos del marco y sus micromódulos de procesamiento de evidencia, traduciendo un manifiesto de caso declarativo en una secuencia de pasos computacionales imperativa y reproducible. Al vincular todas las transiciones de estado específicas del caso a una secuencia de evidencia indexada por enteros, el módulo garantiza que ejecuciones independientes desde condiciones iniciales idénticas recorran caminos de ejecución bit a bit idénticos, satisfaciendo así los prerrequisitos de reproducibilidad del estándar Daubert, los mandatos de trazabilidad de GB/T 29360-2012 y los controles de responsabilidad del Esquema de Protección Multinivel (MLPS 2.0) de China.

### 2. Fundamentos matemáticos
Un caso forense $\mathcal{C}$ se define formalmente como una 3-tupla estrictamente ordenada $\mathcal{C} = (\mathcal{P}, \mathcal{E}, \mathcal{M}_0)$, donde $\mathcal{P}$ es la configuración de parámetros, $\mathcal{E} = (e_1, e_2, \ldots, e_n)$ es la secuencia de evidencia indexada por enteros y $\mathcal{M}_0 = \emptyset$ es el acumulador de metadatos inicial. El controlador implementa un sistema de transición determinista $\mathcal{T} = (S, s_0, \delta)$ con función de transición total $\delta: S \times \mathcal{E} \to S$.

**Axioma de Determinismo:** $\forall \mathcal{P} \in \mathbb{P}, \forall \mathcal{E},\; |\delta^*(s_0, \mathcal{E})| = 1$.

El rastro de ejecución $\tau$ y el acumulador final de metadatos $\mathcal{M}_n$ son funciones únicas de $(\mathcal{P}, \mathcal{E})$.

### 3. Conceptos clave

| Concepto | Definición | Rol técnico |
|---|---|---|
| **Sistema de transición determinista** | $\mathcal{T} = (S, s_0, \delta)$ sobre evidencia ordenada | Elimina incertidumbre algorítmica en el nivel del plano de control |
| **Índice entero de evidencia** | Biyección $idx: \{1,\ldots,n\} \to \mathcal{E}$ | Garantiza invarianza del orden de procesamiento entre sistemas de archivos |
| **Código de integridad agregado** | $H_{\text{agg}} = \mathcal{H}(m_1 \| m_2 \| \cdots \| m_n)$ | Atestación no repudiable de la traza de ejecución completa |
| **Cadena de custodia SHA-256** | Resumen criptográfico encadenado por objeto de evidencia | Satisface Daubert y GB/T 29360-2012 |
| **Perfil de política** | Modo `estricto` o `permisivo` | Controla el manejo de errores sin alterar el camino de ejecución determinista |
| **Marca temporal monotónica** | Contador entero para ordenamiento, no para control lógico | Separa la secuenciación evidenciaría de la dependencia del reloj de pared |

### 4. Descripción del algoritmo
El algoritmo procede en cuatro fases estrictamente ordenadas:

*Fase I: Inicialización del caso.* El controlador ingiere el manifiesto de caso $\mathcal{M}_f$ y materializa $\mathcal{P}$. Calcula el directorio de espacio de trabajo canónico $W$, adquiere un bloqueo exclusivo previo a la ejecución y verifica la disponibilidad y compatibilidad de versiones de todos los módulos VIGÍA dependientes.

*Fase II: Ingesta de evidencia y secuenciación del manifiesto.* Se analiza el manifiesto de evidencia $\mathcal{E}_f$ en la secuencia $\mathcal{E}$. El índice de biyección entero $idx$ se hace cumplir; cualquier índice duplicado o faltante desencadena un error fatal de inicialización.

*Fase III: Procesamiento secuencial.* Para cada $i$ de $1$ a $n$ en orden ascendente estricto: (1) se despacha $e_i$ para validación; (2) se calcula el resumen criptográfico $H(e'_i)$ y se compara con la verdad fundamental; (3) se aplica una transformación forense $\alpha_i$; (4) la salida $o_i$ y los metadatos $m_i$ se añaden a $\mathcal{M}_{i-1}$; (5) actualización de estado.

*Fase IV: Finalización y emisión de la pista de auditoría.* Se computa $H_{\text{agg}}$, y los metadatos agregados, el resumen de la traza de ejecución y el estado de terminación $\xi$ se escriben a través de `lib/audit_logger.py`. Si está disponible `modules/crypto_signer.py`, la pista se firma criptográficamente.

> **【Nota Científica】**
> La Primereidad de Peirce se mapea a la Fase II: el manifiesto de evidencia se lee como una secuencia entera cruda y no interpretada. La Segundidad es la Fase III: cada $e_i$ se procesa diferencialmente contra la verdad fundamental criptográfica, produciendo un resultado binario de coincidencia de resumen. La Terceridad es el código de integridad agregado $H_{\text{agg}}$: la ley repetible que vincula toda la traza de ejecución en una salida única y auditable. El principio de enciclopedia de Eco garantiza que `evidence_id` y `ground_truth_hash` tienen definiciones únicas e inequívocas en todos los módulos trabajadores de VIGÍA. La máxima de Manera de Grice se operacionaliza mediante el índice entero $i$: el módulo reporta el orden de procesamiento en un formato inequívoco y estrictamente secuenciado, eliminando cualquier ambigüedad interpretativa sobre qué artefacto se procesó en qué paso.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## РУССКИЙ

**Контроллер исполнения дел (`scripts/run_case.py`)**

### 1. Назначение модуля и архитектурная роль
В рамках криминалистической платформы VIGÍA модуль `scripts/run_case.py` выполняет роль детерминированного ядра оркестрации для однодельных следственных конвейеров. Его архитектурный мандат состоит в том, чтобы инстанцировать ровно одно криминалистическое дело, обеспечить полностью упорядоченный, последовательный режим обработки над пространством объектов доказательств и произвести полную, tamper-evident запись метаданных исполнения. Модуль занимает страт между уровнем управления делами и микромодулями обработки доказательств, транслируя декларативный манифест дела в императивную, воспроизводимую последовательность вычислительных шагов. Привязывая все специфические для дела переходы состояния к индексированной целыми числами последовательности доказательств, модуль гарантирует, что независимые исполнения из идентичных начальных условий проходят побитово идентичные пути, удовлетворяя тем самым требованиям воспроизводимости стандарта Daubert, мандатам прослеживаемости GB/T 29360-2012 и средствам контроля подотчётности MLPS 2.0.

### 2. Математические основания
Криминалистическое дело $\mathcal{C}$ формально определяется как строго упорядоченная 3-кортеж $\mathcal{C} = (\mathcal{P}, \mathcal{E}, \mathcal{M}_0)$, где $\mathcal{P}$ — конфигурация параметров, $\mathcal{E} = (e_1, e_2, \ldots, e_n)$ — целочисленно-индексированная последовательность доказательств, $\mathcal{M}_0 = \emptyset$ — начальный накопитель метаданных. Контроллер реализует детерминированную систему переходов $\mathcal{T} = (S, s_0, \delta)$ с тотальной функцией перехода $\delta: S \times \mathcal{E} \to S$.

**Аксиома детерминизма:** $\forall \mathcal{P} \in \mathbb{P}, \forall \mathcal{E},\; |\delta^*(s_0, \mathcal{E})| = 1$. Трасса исполнения $\tau$ и итоговый накопитель метаданных $\mathcal{M}_n$ являются однозначными функциями $(\mathcal{P}, \mathcal{E})$.

### 3. Ключевые концепции

| Концепция | Определение | Техническая роль |
|---|---|---|
| **Детерминированная система переходов** | $\mathcal{T} = (S, s_0, \delta)$ над упорядоченными доказательствами | Устраняет алгоритмическую неопределённость на уровне плоскости управления |
| **Целочисленный индекс доказательств** | Биекция $idx: \{1,\ldots,n\} \to \mathcal{E}$ | Гарантирует инвариантность порядка обработки между файловыми системами |
| **Агрегатный код целостности** | $H_{\text{agg}} = \mathcal{H}(m_1 \| m_2 \| \cdots \| m_n)$ | Неотрекаемое подтверждение полной трассы исполнения |
| **Цепочка хранения SHA-256** | Криптографический дайджест, связанный по каждому объекту доказательств | Удовлетворяет требованиям Daubert и GB/T 29360-2012 |
| **Профиль политики** | Режим `строгий` или `разрешительный` | Управляет обработкой ошибок, не изменяя детерминированный путь исполнения |
| **Монотонная временна́я метка** | Целочисленный счётчик для упорядочивания, не для управления логикой | Отделяет доказательственную последовательность от зависимости от системных часов |

### 4. Алгоритмическое описание
Алгоритм проходит четыре строго упорядоченных фазы:

*Фаза I: Инициализация дела.* Контроллер поглощает манифест дела $\mathcal{M}_f$, материализует $\mathcal{P}$, вычисляет канонический рабочий каталог, захватывает эксклюзивную блокировку и проверяет доступность и совместимость версий всех зависимых модулей.

*Фаза II: Поглощение доказательств и секвенирование манифеста.* Манифест $\mathcal{E}_f$ разбирается в последовательность $\mathcal{E}$. Биекция целочисленных индексов принудительно соблюдается; дублирующийся или отсутствующий индекс вызывает фатальную ошибку.

*Фаза III: Последовательная обработка.* Для каждого $i$ от $1$ до $n$ в строго восходящем порядке: (1) $e_i$ передаётся на проверку; (2) вычисляется криптографический дайджест и сравнивается с эталоном; (3) применяется криминалистическая трансформация $\alpha_i$; (4) вывод $o_i$ и метаданные $m_i$ добавляются к $\mathcal{M}_{i-1}$.

*Фаза IV: Завершение и эмиссия журнала аудита.* Вычисляется $H_{\text{agg}}$; агрегатные метаданные и статус завершения записываются через `lib/audit_logger.py`. При наличии `modules/crypto_signer.py` журнал криптографически подписывается.

> **【Научное примечание】**
> Первичность Пирса соответствует Фазе II: манифест доказательств читается как необработанная, неинтерпретированная целочисленная последовательность. Вторичность — это Фаза III: каждое $e_i$ дифференциально обрабатывается против криптографической истины манифеста, производя бинарный результат совпадения дайджеста. Третичность — агрегатный код целостности $H_{\text{agg}}$: повторяемый закон, связывающий всю трассу исполнения в единственный, проверяемый выход. Принцип энциклопедии Эко гарантирует, что `evidence_id` и `ground_truth_hash` имеют единственные, недвусмысленные определения во всех рабочих модулях VIGÍA. Максима Манеры Грайса операционализируется целочисленным индексом $i$: модуль сообщает порядок обработки в недвусмысленном, строго упорядоченном формате, устраняя любую интерпретивную неоднозначность относительно того, какой артефакт был обработан на каком шаге.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## 中文

**案例执行控制器（`scripts/run_case.py`）**

### 1. 模块用途与架构角色
在 VIGÍA 取证框架中，`scripts/run_case.py` 充当单案例调查流水线的确定性编排核心。其架构使命是实例化恰好一个取证案例，对证据对象空间强制执行完全有序的顺序处理机制，并发出完整的防篡改执行元数据记录。模块占据框架案例管理层与证据处理微模块之间的层次，将声明式案例清单翻译为命令式、可重现的计算步骤序列。通过将所有案例特定状态转换绑定至整数索引证据序列，模块保证从相同初始条件开始的独立执行遍历位相同的执行路径，从而满足道伯特标准规定的可重现性前提、GB/T 29360-2012 的可追溯性要求以及中国多级保护方案（MLPS 2.0）的问责控制。

### 2. 关键概念

| 概念 | 定义 | 技术作用 |
|---|---|---|
| **确定性转换系统** | 有序证据上的 $\mathcal{T} = (S, s_0, \delta)$ | 在控制平面级别消除算法不确定性 |
| **整数证据索引** | 双射 $idx: \{1,\ldots,n\} \to \mathcal{E}$ | 保证处理顺序跨文件系统和架构的不变性 |
| **聚合完整性码** | $H_{\text{agg}} = \mathcal{H}(m_1 \| m_2 \| \cdots \| m_n)$ | 完整执行轨迹的不可抵赖证明 |
| **SHA-256 监管链** | 跨每个证据对象链接的密码摘要 | 满足道伯特标准和 GB/T 29360-2012 完整性要求 |
| **策略配置文件** | `strict` 或 `permissive` 执行模式 | 在不改变确定性执行路径的情况下管理错误处理 |
| **单调时间戳** | 用于排序而非逻辑控制的整数计数器 | 将证据排序与挂钟时间依赖分离 |

### 3. 算法描述
算法经四个严格有序阶段执行：

**第 I 阶段：案例初始化。** 控制器摄入案例清单 $\mathcal{M}_f$，实例化参数结构 $\mathcal{P}$，计算规范工作目录 $W$，在 $W$ 上获取排他预执行锁，并检验所有依赖 VIGÍA 模块的可用性和版本兼容性。

**第 II 阶段：证据摄入与清单排序。** 将证据清单 $\mathcal{E}_f$ 解析为序列 $\mathcal{E}$，强制执行整数双射 $idx$；任何重复或缺失的索引触发致命初始化错误。

**第 III 阶段：顺序处理。** 对每个 $i$ 从 $1$ 到 $n$ 严格升序执行：(1) 将 $e_i$ 分派至验证模块；(2) 计算密码摘要 $H(e'_i)$ 并对照清单基准真值比较；(3) 应用取证变换 $\alpha_i$；(4) 将输出 $o_i$ 和元数据 $m_i$ 追加至 $\mathcal{M}_{i-1}$；(5) 状态更新。

**第 IV 阶段：收尾与审计轨迹发送。** 计算 $H_{\text{agg}}$，将聚合元数据、执行轨迹摘要和终止状态 $\xi$ 写入 `lib/audit_logger.py`。若 `modules/crypto_signer.py` 可用，则对轨迹进行密码签名。

> **【科学说明】**
> 皮尔斯的初性映射至第 II 阶段：证据清单被读取为原始、未解释的整数序列——纯粹的现象学接收，不施加任何判断。二性是第 III 阶段：每个 $e_i$ 对照清单中的密码基准真值进行差异处理，产生二元摘要匹配结果。三性是聚合完整性码 $H_{\text{agg}}$：将整个执行轨迹绑定为单一可审计输出的可重复规律，无论处理了哪些证据项。艾柯的百科全书原则保证 `evidence_id` 和 `ground_truth_hash` 在所有 VIGÍA 工作模块中具有单一明确的定义，防止不同证据对象的别名混淆。格赖斯的方式准则通过整数索引 $i$ 被操作化：模块以明确、严格顺序的格式报告处理顺序，消除关于哪个步骤处理了哪个取证工件的任何解释歧义。

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*