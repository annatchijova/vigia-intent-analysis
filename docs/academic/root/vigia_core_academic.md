## ENGLISH

**Module:** `vigia/vigia_core.py` — Forensic Semiotic Inference Core

**1. Module Purpose**
The `vigia/vigia_core.py` module constitutes the central evidentiary-reasoning engine of the VIGÍA forensic platform. Encapsulated within the `VigiaCore` class, the module orchestrates a deterministic, six-stage semiotic verification cycle grounded in the phenomenology of Charles Sanders Peirce, the sign theory of Umberto Eco, and the cooperative-pragmatic maxims of H. Paul Grice. Its principal function is to ingest normalized digital evidence artifacts, subject them to exhaustive integer-based confidence aggregation, and emit a formal admissibility verdict. Unlike conventional probabilistic inference frameworks that rely upon floating-point stochasticity and Bayesian posteriors, VIGÍA enforces a fully deterministic evaluation pipeline in which every state transition, penalty assignment, and threshold comparison operates exclusively over the integer domain \( \mathbb{Z} \). This architectural commitment to exact arithmetic eliminates representation error, platform-dependent rounding, and non-reproducible entropy, thereby satisfying the falsifiability and known-error-rate prerequisites of the *Daubert* standard for scientific evidence in United States federal procedure. Furthermore, the module’s tamper-evident audit architecture conforms to the evidentiary-integrity requirements of GB/T 29360-2012 (Electronic Data Forensics General Principles), while its role-based access granularity satisfies the controlled-access stipulations of MLPS 2.0 Level 3 (Multi-Level Protection Scheme). Within the broader VIGÍA ecosystem, `vigia_core.py` serves as the adjudicative kernel that mediates between ingestion pipelines, cryptographic integrity services, and reporting interfaces.

**2. Mathematical Foundations**
The module formalizes evidence processing as a deterministic finite-state transducer \( \mathcal{M} = (\mathcal{S}, \mathcal{E}, \delta, s_0, \mathcal{F}) \), where:
- The state space is \( \mathcal{S} = \{ F, S, T, G, D, V \} \), denoting respectively Firstness, Secondness, Thirdness, Geopolitical validation, Devil's Advocate refutation, and Verdict.
- The evidence space \( \mathcal{E} = \{ e_1, e_2, \dots, e_n \} \) comprises normalized digital artifacts supplied by the related `vigia_preprocess` module.
- The initial state is \( s_0 = F \).
- The set of accepting states is \( \mathcal{F} = \{ V \} \).
- The transition function \( \delta: \mathcal{S} \times \mathcal{E} \to \mathcal{S} \) is a total function deterministically computed by the `analyze_case()` method; no stochastic transitions are permitted.

Confidence aggregation is defined as a weighted integer sum with bounded saturation:
\[
C_{\text{final}} = \operatorname{clamp}_{[0,100]}\left( \sum_{i=1}^{k} w_i \cdot c_i \right), \quad w_i, c_i \in \mathbb{Z}.
\]
The clamping operator \( \operatorname{clamp}_{[L,U]}(x) = \min(U, \max(L, x)) \) ensures closure within the admissible integer interval \( [0, 100] \cap \mathbb{Z} \), forming a commutative monoid under saturated addition. The constant `MIN_CONFIDENCE` is formally an integer threshold \( \tau \in \mathbb{Z} \), operationally set to \( \tau = 75 \). The verdict function \( V: \mathbb{Z} \to \{ \text{ADMISSIBLE}, \text{INADMISSIBLE} \} \) is defined by:
\[
V(C_{\text{final}}) = \begin{cases} \text{ADMISSIBLE}, & \text{if } C_{\text{final}} \geq \tau, \\ \text{INADMISSIBLE}, & \text{if } C_{\text{final}} < \tau. \end{cases}
\]
All arithmetic operations—addition, scalar multiplication, and comparison—are performed in two's-complement integer representation, guaranteeing bitwise reproducibility across heterogeneous hardware architectures and compiler optimizations.

**3. Algorithm Description**
The `analyze_case()` function executes the following deterministic sequence, each stage producing exactly one transition record:

1. **Ingestion and Cryptographic Verification.** The input `case_bundle` is validated against SHA-256 cryptographic hashes maintained by `vigia_hash`. Any digest mismatch triggers an immediate abort, returning a `HASH_FAILURE` terminal state. This step ensures that only integrity-verified artifacts enter the semiotic cycle.
2. **Firstness (State \( F \)).** Raw artifact features are extracted as an integer vector \( \mathbf{a} \in \mathbb{Z}^m \). No floating-point normalization is permitted; all scaling is effected through fixed-point integer multiplication by pre-calibrated rational denominators stored as integer pairs \( (p, q) \) with \( q \neq 0 \). This stage corresponds to the pure phenomenological reception of the sign-vehicle.
3. **Secondness (State \( S \)).** Each extracted feature is differentially compared against a calibrated ground-truth baseline vector \( \mathbf{b} \in \mathbb{Z}^m \) residing in the forensic knowledge base. A binary-relation matrix \( \mathbf{R} \in \{0,1\}^{m \times m} \) is populated, where \( R_{ij} = 1 \) if and only if \( |a_i - b_j| \leq \epsilon_{ij} \) for an integer tolerance \( \epsilon_{ij} \in \mathbb{Z}_{\geq 0} \), and \( 0 \) otherwise. A logical rupture is declared if any mandatory feature yields a zero row in \( \mathbf{R} \).
4. **Thirdness (State \( T \)).** Synthetic mediation combines the differential signals into an intermediate confidence score \( C_T \). This stage applies a rule-based integer matrix operation or a weighted sum of violation counts, yielding \( C_T \in [0, 100] \cap \mathbb{Z} \). The operation is referentially transparent: identical inputs always produce identical \( C_T \).
5. **Geopolitical (State \( G \)).** Contextual metadata—including timezone offsets, language locale codes, and jurisdictional tagging—are validated against the `jurisdiction_profile`. Integer rule-matching predicates \( G_j: \mathcal{M} \to \{0, 1\} \) determine compliance with regional evidentiary standards. Each non-compliance event applies an integer penalty \( p_{G,j} \in \mathbb{Z} \) subtracted from the running score.
6. **Devil's Advocate (State \( D \)).** An adversarial stress-test applies Gricean maxim evaluation (Quantity, Quality, Relation, Manner) to the artifact's semantic payload. Each detected maxim violation decrements the score by an integer penalty \( p_k \in \mathbb{Z} \), formalized as:
   \[
   C_D = C_T - \sum_{k=1}^{4} p_k \cdot \mathbb{I}(\text{violation}_k),
   \]
   where \( \mathbb{I} \) is the indicator function returning \( 1 \) if the violation is present and \( 0 \) otherwise.
7. **Verdict (State \( V \)).** The final score is computed as \( C_V = \operatorname{clamp}_{[0,100]}(C_D) \). The function evaluates \( C_V \geq \text{MIN\_CONFIDENCE} \). If true, the verdict is `ADMISSIBLE`; otherwise `INADMISSIBLE`. The terminal state and all intermediate scores are sealed into the output record.
8. **Audit Logging.** Every state transition \( (s_i, s_{i+1}, C_i, h_i) \), together with its integer Unix timestamp and SHA-256 digest \( h_i \), is appended to the tamper-evident log managed by `vigia_chain_of_custody`.

**4. Input / Output Specifications**
- **Inputs:**
  - `case_bundle`: `dict` containing artifact payloads (byte sequences or integer feature vectors), acquisition timestamps expressed as Unix epoch integers, examiner credentials as integer-coded identifiers, and provenance metadata.
  - `jurisdiction_profile`: `dict` encoding regional evidentiary rules as integer-coded flag sets and mandatory field masks.
  - `audit_context`: `object` referencing the active chain-of-custody session identifier and the previous log hash for linked-list integrity.
- **Outputs:**
  - `verdict_record`: `dict` with strictly defined keys:
    - `final_state`: terminal state identifier from \( \mathcal{S} \).
    - `integer_score`: \( C_V \in [0, 100] \cap \mathbb{Z} \).
    - `admissibility`: categorical string, either `ADMISSIBLE` or `INADMISSIBLE`.
    - `transition_log`: ordered list of tuples \( (\text{state}, \text{integer\_score}, \text{hash\_digest}) \) documenting the Peircean cycle traversal.
    - `hash_digest`: SHA-256 fingerprint of the canonicalized `verdict_record`.

**5. Deterministic Guarantees**
- **Bit-exact Reproducibility:** For any two invocations with identical `case_bundle`, `jurisdiction_profile`, and `audit_context`, the module produces identical `integer_score`, `admissibility`, and `hash_digest`. Formally, the inference function \( f: \mathcal{X} \to \mathcal{Y} \) satisfies \( \forall x, y \in \mathcal{X},\, x = y \implies f(x) = f(y) \).
- **Integer Domain Closure:** All confidence values, penalties, weights, and tolerances are elements of \( \mathbb{Z} \). The saturated addition operator ensures closure under the algebraic structure \( (\mathbb{Z}_{[0,100]}, \oplus) \), where \( a \oplus b = \operatorname{clamp}_{[0,100]}(a + b) \).
- **Entropy Exclusion:** No pseudo-random number generators, hardware entropy sources, Monte Carlo sampling, or floating-point operations participate in the inference path. The algorithm is entirely deterministic and traceable.
- **Audit Completeness:** Every state transition is appended to the tamper-evident log as an immutable record containing the state identifier, the integer score, the Unix timestamp, and the SHA-256 digest of the preceding record. The audit log forms a cryptographic hash chain that cannot be modified without invalidating all subsequent entries.

### 【Scientific Note】
Peirce's Firstness, Secondness, and Thirdness map exactly onto the six-stage inference cycle: Firstness is the raw integer feature vector $\mathbf{a}$ extracted from the artifact—pure phenomenological reception with no interpretation. Secondness is the binary-relation matrix $\mathbf{R}$ produced in the Secondness stage: the measurable, dyadic reaction between the observed artifact and the calibrated baseline. Thirdness is the scoring rule applied in the Thirdness and subsequent stages: the repeatable law that converts a differential signal into an integer confidence score. Eco's encyclopedia principle ensures that every field name in the `case_bundle` has a single, unambiguous semantic definition across all VIGÍA modules, eliminating the overinterpretation that produces false positives. Grice's maxim of Quantity is operationalized in the Devil's Advocate stage: the artifact's semantic payload is evaluated for informational adequacy, and any detected insufficiency is penalized by an integer decrement. The `MIN_CONFIDENCE` threshold $\tau = 75$ is not a floating-point heuristic but a constitutively defined integer boundary: any score below it is inadmissible by definition, not by probabilistic judgment.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## ESPAÑOL

**Módulo:** `vigia/vigia_core.py` — Motor Central de Inferencia Semiótica Forense

### 1. Propósito del módulo
El módulo `vigia/vigia_core.py` constituye el motor central de razonamiento evidenciario de la plataforma forense VIGÍA. Encapsulado en la clase `VigiaCore`, orquesta un ciclo de verificación semiótica determinista de seis etapas fundamentado en la fenomenología de Charles Sanders Peirce, la teoría del signo de Umberto Eco y las máximas cooperativo-pragmáticas de H. Paul Grice. Su función principal es ingerir artefactos de evidencia digital normalizados, someterlos a una exhaustiva agregación de confianza basada en enteros y emitir un veredicto formal de admisibilidad. A diferencia de los marcos de inferencia probabilística convencionales que dependen de la estocasticidad de punto flotante y los posterioris bayesianos, VIGÍA impone un flujo de evaluación completamente determinista en el que cada transición de estado, asignación de penalidad y comparación de umbral opera exclusivamente en el dominio entero $\mathbb{Z}$. Este compromiso arquitectónico con la aritmética exacta elimina el error de representación, el redondeo dependiente de plataforma y la entropía no reproducible, satisfaciendo así los prerrequisitos de falsabilidad y tasa de error conocida del estándar *Daubert* para evidencia científica. Además, la arquitectura de auditoría a prueba de manipulaciones se ajusta a los requisitos de integridad probatoria de GB/T 29360-2012, mientras que la granularidad de acceso basada en roles satisface las estipulaciones de acceso controlado del MLPS 2.0 Nivel 3.

### 2. Fundamentos matemáticos
El módulo formaliza el procesamiento de evidencia como un transductor determinista de estado finito $\mathcal{M} = (\mathcal{S}, \mathcal{E}, \delta, s_0, \mathcal{F})$, donde el espacio de estados es $\mathcal{S} = \{ F, S, T, G, D, V \}$, denotando respectivamente Primereidad, Segundidad, Terceridad, Validación Geopolítica, Refutación del Abogado del Diablo y Veredicto. La función de transición $\delta: \mathcal{S} \times \mathcal{E} \to \mathcal{S}$ es calculada deterministamente por el método `analyze_case()`; no se permiten transiciones estocásticas.

La agregación de confianza se define como una suma entera ponderada con saturación acotada:
$$C_{\text{final}} = \operatorname{clamp}_{[0,100]}\left( \sum_{i=1}^{k} w_i \cdot c_i \right), \quad w_i, c_i \in \mathbb{Z}.$$
La función de veredicto $V: \mathbb{Z} \to \{ \text{ADMISIBLE}, \text{INADMISIBLE} \}$ está definida por $V(C_{\text{final}}) = \text{ADMISIBLE}$ si $C_{\text{final}} \geq \tau = 75$, e $\text{INADMISIBLE}$ en caso contrario. Todas las operaciones aritméticas se realizan en representación de complemento a dos, garantizando la reproducibilidad bit a bit entre arquitecturas de hardware heterogéneas.

### 3. Conceptos clave

| Concepto | Definición | Rol técnico |
|---|---|---|
| **Motor semiótico de seis etapas** | Transductor finito determinista $\mathcal{M}$ sobre artefactos de evidencia | Marco central de evaluación en `analyze_case()` |
| **Agregación de confianza entera** | Suma ponderada con saturación en $[0,100] \cap \mathbb{Z}$ | Garantiza aritmética exacta sin error de representación |
| **Primereidad** | Extracción de vector de características entero $\mathbf{a} \in \mathbb{Z}^m$ | Recepción fenomenológica pura del vehículo del signo |
| **Segundidad** | Matriz de relación binaria $\mathbf{R}$ contra línea base de verdad fundamental | Reacción diádica medible que identifica rupturas lógicas |
| **Terceridad** | Puntuación de confianza intermedia $C_T$ por operación de matriz entera ponderada | Mediación sintética reproducible; idénticas entradas → idéntico $C_T$ |
| **Umbral `MIN_CONFIDENCE`** | Entero $\tau = 75$ en $[0,100] \cap \mathbb{Z}$ | Límite constitutivo de admisibilidad, no heurístico |
| **Cadena de custodia mediante SHA-256** | Encadenamiento de hashes en el registro de auditoría de solo adición | Garantiza tamper-evidence para todos los registros de transición de estado |

### 4. Descripción del algoritmo
La función `analyze_case()` ejecuta la siguiente secuencia determinista de siete pasos: (1) Ingesta y verificación criptográfica contra SHA-256; (2) Primereidad: extracción de vector de características entero sin normalización de punto flotante; (3) Segundidad: comparación diferencial contra línea base calibrada, declarando ruptura lógica si alguna característica obligatoria produce una fila cero en $\mathbf{R}$; (4) Terceridad: mediación sintética con suma entera ponderada que produce $C_T \in [0,100] \cap \mathbb{Z}$; (5) Geopolítica: validación de metadatos contextuales con penalidades de incumplimiento $p_{G,j} \in \mathbb{Z}$; (6) Abogado del Diablo: evaluación de máximas griceanas con penalidades por violación $p_k \in \mathbb{Z}$; (7) Veredicto: $C_V = \operatorname{clamp}_{[0,100]}(C_D)$ comparado con $\tau$, y registro en el log de auditoría.

### 5. Garantías deterministas
- **Reproducibilidad bit a bit:** Dos invocaciones con entradas idénticas producen `integer_score`, `admissibility` y `hash_digest` idénticos.
- **Clausura del dominio entero:** Todos los valores de confianza, penalidades, pesos y tolerancias son elementos de $\mathbb{Z}$.
- **Exclusión de entropía:** Ningún generador de números pseudoaleatorios, fuente de entropía de hardware o operación de punto flotante participa en el camino de inferencia.

> **【Nota Científica】**
> La Primereidad, Segundidad y Terceridad de Peirce se mapean exactamente sobre el ciclo de inferencia de seis etapas: Primereidad es el vector de características entero crudo $\mathbf{a}$; Segundidad es la matriz de relación binaria $\mathbf{R}$ producida en la comparación diferencial; Terceridad es la regla de puntuación aplicada en las etapas subsiguientes. El principio de enciclopedia de Eco garantiza que cada nombre de campo en el `case_bundle` tiene una única definición semántica inequívoca en todos los módulos de VIGÍA. La máxima de Cantidad de Grice se operacionaliza en la etapa del Abogado del Diablo: la carga semántica del artefacto se evalúa por adecuación informacional, y cualquier insuficiencia detectada se penaliza con un decremento entero. El umbral `MIN_CONFIDENCE` $\tau = 75$ no es una heurística de punto flotante sino un límite entero constitutivamente definido: cualquier puntuación por debajo de él es inadmisible por definición, no por juicio probabilístico.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## РУССКИЙ

**Модуль:** `vigia/vigia_core.py` — Центральное ядро криминалистического семиотического вывода

### 1. Назначение модуля
Модуль `vigia/vigia_core.py` составляет центральный движок доказательственного рассуждения криминалистической платформы VIGÍA. Инкапсулированный в классе `VigiaCore`, он оркестрирует детерминированный шестиэтапный семиотический верификационный цикл, основанный на феноменологии Чарльза Сандерса Пирса, теории знака Умберто Эко и кооперативно-прагматических максимах Г. П. Грайса. Его основная функция — принимать нормализованные артефакты цифровых доказательств, подвергать их исчерпывающей целочисленной агрегации достоверности и выносить формальный вердикт о допустимости. В отличие от традиционных вероятностных систем вывода, опирающихся на стохастику с плавающей точкой и байесовские апостериорные вероятности, VIGÍA реализует полностью детерминированный конвейер оценки, в котором каждый переход состояния, назначение штрафа и сравнение порога выполняются исключительно в целочисленном домене $\mathbb{Z}$. Архитектурная приверженность точной арифметике устраняет ошибку представления, платформозависимое округление и невоспроизводимую энтропию, удовлетворяя тем самым предпосылкам фальсифицируемости и известной частоты ошибок стандарта *Daubert*. Кроме того, архитектура аудита с защитой от подделок соответствует требованиям доказательственной целостности GB/T 29360-2012, а ролевая гранулярность доступа удовлетворяет требованиям контролируемого доступа MLPS 2.0 Уровень 3.

### 2. Математические основания
Модуль формализует обработку доказательств как детерминированный конечный преобразователь $\mathcal{M} = (\mathcal{S}, \mathcal{E}, \delta, s_0, \mathcal{F})$, где пространство состояний $\mathcal{S} = \{ F, S, T, G, D, V \}$ обозначает соответственно Первичность, Вторичность, Третичность, Геополитическую валидацию, Опровержение адвоката дьявола и Вердикт. Функция переходов $\delta: \mathcal{S} \times \mathcal{E} \to \mathcal{S}$ детерминированно вычисляется методом `analyze_case()`; стохастические переходы не допускаются.

Агрегация достоверности определяется как взвешенная целочисленная сумма с ограниченным насыщением:
$$C_{\text{final}} = \operatorname{clamp}_{[0,100]}\left( \sum_{i=1}^{k} w_i \cdot c_i \right), \quad w_i, c_i \in \mathbb{Z}.$$
Функция вердикта $V(C_{\text{final}}) = \text{ДОПУСТИМО}$ при $C_{\text{final}} \geq \tau = 75$, иначе $\text{НЕДОПУСТИМО}$. Все арифметические операции выполняются в представлении дополнения до двух, гарантируя побитовую воспроизводимость на разнородных аппаратных архитектурах.

### 3. Ключевые концепции

| Концепция | Определение | Техническая роль |
|---|---|---|
| **Шестиэтапный семиотический движок** | Детерминированный конечный преобразователь $\mathcal{M}$ над пространством доказательств | Центральный оценочный каркас в `analyze_case()` |
| **Целочисленная агрегация достоверности** | Взвешенная сумма с насыщением в $[0,100] \cap \mathbb{Z}$ | Гарантирует точную арифметику без ошибки представления |
| **Первичность** | Извлечение целочисленного вектора признаков $\mathbf{a} \in \mathbb{Z}^m$ | Чистое феноменологическое восприятие знако-носителя |
| **Вторичность** | Матрица бинарных отношений $\mathbf{R}$ против калиброванного базиса | Измеримая диадическая реакция, выявляющая логические разрывы |
| **Третичность** | Промежуточная оценка $C_T$ посредством взвешенной целочисленной матричной операции | Воспроизводимое синтетическое посредничество |
| **Порог `MIN_CONFIDENCE`** | Целое число $\tau = 75$ из $[0,100] \cap \mathbb{Z}$ | Конститутивная граница допустимости, не эвристика |
| **Цепочка хранения SHA-256** | Хеш-цепочка в журнале аудита только для дополнения | Гарантирует tamper-evidence для всех записей переходов состояний |

### 4. Алгоритмическое описание
Функция `analyze_case()` выполняет следующую детерминированную последовательность из семи шагов: (1) Поглощение и криптографическая верификация SHA-256; (2) Первичность: извлечение целочисленного вектора признаков без нормализации с плавающей точкой; (3) Вторичность: дифференциальное сравнение с калиброванным базисом, объявление логического разрыва при нулевой строке в $\mathbf{R}$; (4) Третичность: синтетическое посредничество через взвешенную сумму, дающую $C_T \in [0,100] \cap \mathbb{Z}$; (5) Геополитика: валидация контекстуальных метаданных со штрафами $p_{G,j} \in \mathbb{Z}$; (6) Адвокат дьявола: оценка грайсовских максим со штрафами $p_k \in \mathbb{Z}$; (7) Вердикт: $C_V = \operatorname{clamp}_{[0,100]}(C_D)$ сравнивается с $\tau$ и фиксируется в журнале аудита.

### 5. Детерминированные гарантии
- **Побитовая воспроизводимость:** Два вызова с идентичными входными данными дают идентичные `integer_score`, `admissibility` и `hash_digest`.
- **Замкнутость целочисленного домена:** Все значения достоверности, штрафы, веса и допуски являются элементами $\mathbb{Z}$.
- **Исключение энтропии:** Никакие генераторы псевдослучайных чисел, аппаратные источники энтропии или операции с плавающей точкой не участвуют в пути вывода.

> **【Научное примечание】**
> Первичность, Вторичность и Третичность Пирса точно отображаются на шестиэтапный цикл вывода. Первичность — это необработанный целочисленный вектор признаков $\mathbf{a}$: чистое феноменологическое восприятие без интерпретации. Вторичность — матрица бинарных отношений $\mathbf{R}$, созданная при дифференциальном сравнении. Третичность — правило оценки, применяемое в последующих этапах: повторяемый закон, преобразующий дифференциальный сигнал в целочисленную оценку достоверности. Принцип энциклопедии Эко гарантирует, что каждое имя поля в `case_bundle` имеет единственное недвусмысленное семантическое определение во всех модулях VIGÍA. Максима Количества Грайса операционализируется на этапе Адвоката дьявола: семантическая нагрузка артефакта оценивается на информационную достаточность, и любая выявленная недостаточность штрафуется целочисленным декрементом. Порог `MIN_CONFIDENCE` $\tau = 75$ — не эвристика с плавающей точкой, а конститутивная целочисленная граница: любая оценка ниже неё недопустима по определению.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## 中文

**模块：** `vigia/vigia_core.py` — 取证语义推断核心

### 1. 模块用途
`vigia/vigia_core.py` 模块构成 VIGÍA 取证平台的核心证据推理引擎。封装于 `VigiaCore` 类中，模块编排一个确定性的六阶段语义验证循环，以查尔斯·桑德斯·皮尔斯的现象学、艾柯的符号理论和格赖斯的合作-语用准则为理论基础。其主要功能是摄入规范化的数字证据取证工件，对其进行详尽的基于整数的置信度聚合，并发出正式的可采性裁决。与依赖浮点随机性和贝叶斯后验的传统概率推断框架不同，VIGÍA 强制执行完全确定性的评估流水线，其中每个状态转换、惩罚赋值和阈值比较均完全在整数域 $\mathbb{Z}$ 上执行。这种对精确算术的架构承诺消除了表示误差、平台依赖舍入和不可重现的熵，从而满足美国联邦诉讼道伯特标准对科学证据的可证伪性和已知误差率要求。

### 2. 数学基础
模块将证据处理形式化为确定性有限状态转换器 $\mathcal{M} = (\mathcal{S}, \mathcal{E}, \delta, s_0, \mathcal{F})$，状态空间 $\mathcal{S} = \{ F, S, T, G, D, V \}$ 分别代表初性、二性、三性、地缘政治验证、魔鬼代言人反驳和裁决。置信度聚合定义为有界饱和加权整数和：
$$C_{\text{final}} = \operatorname{clamp}_{[0,100]}\left( \sum_{i=1}^{k} w_i \cdot c_i \right), \quad w_i, c_i \in \mathbb{Z}.$$
裁决函数：当 $C_{\text{final}} \geq \tau = 75$ 时输出"可采"，否则输出"不可采"。所有算术运算在二进制补码整数表示下执行，保证跨异构硬件架构的位相同可重现性。

### 3. 关键概念

| 概念 | 定义 | 技术作用 |
|---|---|---|
| **六阶段语义推断引擎** | 证据空间上的确定性有限转换器 $\mathcal{M}$ | `analyze_case()` 中的核心评估框架 |
| **整数置信度聚合** | 在 $[0,100] \cap \mathbb{Z}$ 上的饱和加权求和 | 保证精确算术，无表示误差 |
| **初性（Firstness）** | 提取整数特征向量 $\mathbf{a} \in \mathbb{Z}^m$ | 对符号载体的纯现象学接收 |
| **二性（Secondness）** | 对照校准基准真值的二元关系矩阵 $\mathbf{R}$ | 识别逻辑断裂的可测量二元反应 |
| **三性（Thirdness）** | 通过加权整数矩阵运算得出中间置信度分数 $C_T$ | 可重现的综合调解；相同输入 → 相同 $C_T$ |
| **`MIN_CONFIDENCE` 阈值** | $[0,100] \cap \mathbb{Z}$ 中的整数 $\tau = 75$ | 构成性可采性边界，而非启发式判断 |
| **SHA-256 监管链** | 仅追加审计日志中的哈希链 | 为所有状态转换记录提供防篡改保证 |

### 4. 算法描述
`analyze_case()` 函数执行以下七步确定性序列：(1) 对照 SHA-256 进行摄入和密码学验证；(2) 初性：无浮点规范化地提取整数特征向量；(3) 二性：对照校准基准进行差异比较，若任何必需特征在 $\mathbf{R}$ 中产生零行则声明逻辑断裂；(4) 三性：通过加权整数和综合调解，产生 $C_T \in [0,100] \cap \mathbb{Z}$；(5) 地缘政治：以整数惩罚 $p_{G,j} \in \mathbb{Z}$ 验证上下文元数据；(6) 魔鬼代言人：以整数惩罚 $p_k \in \mathbb{Z}$ 进行格赖斯准则评估；(7) 裁决：$C_V = \operatorname{clamp}_{[0,100]}(C_D)$ 与 $\tau$ 比较并封存至审计日志。

### 5. 确定性保证
- **位精确可重现性：** 相同输入的两次调用产生相同的 `integer_score`、`admissibility` 和 `hash_digest`。
- **整数域封闭性：** 所有置信度值、惩罚、权重和容差均为 $\mathbb{Z}$ 的元素。
- **熵排除：** 推断路径中不参与任何伪随机数生成器、硬件熵源或浮点运算。

> **【科学说明】**
> 皮尔斯的初性、二性和三性精确映射至六阶段推断循环：初性是原始整数特征向量 $\mathbf{a}$——纯粹的现象学接收，不含任何解释；二性是差异比较中产生的二元关系矩阵 $\mathbf{R}$——可测量的二元反应，识别观察取证工件与校准基准之间的逻辑断裂；三性是在三性及后续阶段应用的评分规则——将差异信号转换为整数置信度分数的可重复规律。艾柯的百科全书原则确保 `case_bundle` 中每个字段名在所有 VIGÍA 模块中具有单一明确的语义定义，消除产生误报的过度诠释。格赖斯的量的准则在魔鬼代言人阶段被操作化：对取证工件的语义有效载荷进行信息充分性评估，检测到任何不足均以整数递减予以惩罚。`MIN_CONFIDENCE` 阈值 $\tau = 75$ 不是浮点启发式，而是构成性整数边界：低于该值的任何分数在定义上不可采，而非基于概率判断。

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*