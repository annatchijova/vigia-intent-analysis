## ENGLISH

The module `vigia/governance/risk_bounded_layer_v2.py` implements the `RiskBoundedDecisionLayer` (version 3.0-P0-001, with patches C4, C5, P1-A, P2, and P0-001 applied). It constitutes the terminal governance stratum of the VIGÍA forensic pipeline, bearing the institutional responsibility of converting continuous probabilistic evidence assessments into discrete, legally admissible verdicts. Whereas upstream inference layers compute raw likelihoods over evidentiary signifiers, this layer enforces a rigid risk envelope that precludes automated decisions in epistemically hazardous zones. Its architecture is deliberately segregated from both evidence ingestion and posterior computation, establishing a clean separation of concerns between scientific inference and governance action. Every emitted verdict is accompanied by an immutable `DecisionTrace` record, ensuring that the entire logical provenance—from raw evidence to categorical decision—is available for adversarial audit, peer review, and judicial scrutiny.

**Mathematical Foundations**

The layer operates on the Bayesian posterior \( P(A \mid E) \), where \( A \) denotes the hypothesis that a given evidentiary artifact is authentic and \( E \) represents the complete forensic evidence corpus synthesized by upstream semantic coherence modules. This posterior quantifies the degree of justified belief in authenticity conditioned on the observed evidence. The module defines the fabrication risk \( r \) as the exact complementary probability:

\[
r = 1 - P(A \mid E)
\]

with the codomain \( r \in [0, 1] \). This invariant establishes a monotonically decreasing map between epistemic certainty and institutional risk: as the belief in authenticity approaches unity, the fabrication risk asymptotically vanishes, and conversely, a posterior approaching zero implies near-certain fabrication risk.

Decision boundaries are governed by the parameter triple \( (\lambda, \gamma, \omega) \in \mathbb{R}^3 \), which are global system properties read exclusively from the `SelfAdaptiveRiskPolicy` module per patch C4. These parameters delimit three mutually exclusive decision regions:

- **Authenticity region:** \( \Omega_{\text{authentic}} = \{ P \mid P \ge \lambda \} \)
- **Inconclusive region:** \( \Omega_{\text{inconclusive}} = \{ P \mid \gamma < P < \lambda \} \)
- **Fabrication region:** \( \Omega_{\text{fabricated}} = \{ P \mid P \le \gamma \} \)

The width of the inconclusive zone is constrained by the ambiguity tolerance bandwidth \( \omega \), such that \( \lambda - \gamma \ge \omega \). This three-way partition implements a risk-bounded refusal mechanism: the system is forbidden from issuing definitive positive or negative verdicts whenever the posterior falls within the hazardous mid-zone, preventing false certainty under ambiguous evidentiary conditions. The expected utility of each region is implicitly calibrated by the adaptive policy, although the local layer strictly consumes the boundaries without embedding utility functions itself.

All arithmetic is executed using Python’s `decimal.Decimal` class within a fixed-precision, thread-local decimal context. This design eliminates the representation error, rounding indeterminacy, and cross-platform variance inherent to IEEE-754 binary floating-point arithmetic, which is essential when a verdict may hinge on a posterior value infinitesimally close to a decision threshold.

**Algorithm Description**

The principal entry point, `decide(posterior)`, executes a strictly sequential, branch-predictable algorithm engineered for auditability and deterministic reproducibility:

1. **Validation Guard (P0-001):** The input `posterior` is subjected to a domain validation enforcing \( 0 \le \text{posterior} \le 1 \). Any deviation triggers a deterministic exception prior to any state-dependent computation, preventing the semantic inversion wherein an unnormalized or inverted probability could corrupt the risk calculus. This guard codifies the explicit semantic equation \( \text{posterior} = P(\text{authenticity} \mid \text{evidence}) \).

2. **Policy Retrieval (C4 FIX):** The layer performs a read-only query to `SelfAdaptiveRiskPolicy` to obtain the current global parameter set \( (\lambda, \gamma, \omega) \). This query bypasses all local templates, configuration files, or default dictionaries, ensuring that the risk envelope reflects the single institutional source of truth. No runtime overrides are permitted.

3. **Risk Computation:** The fabrication risk is computed as \( r = 1 - \text{posterior} \) using exact decimal subtraction within the fixed-precision context. The operation is guaranteed to be reproducible bit-for-bit across homogeneous software revisions, irrespective of host CPU architecture or operating system.

4. **Boundary Evaluation:** The posterior is compared against the retrieved thresholds. If \( \text{posterior} \ge \lambda \), the categorical verdict is `AUTHENTIC`. If \( \text{posterior} \le \gamma \), the verdict is `FABRICATED`. Otherwise, the verdict is `INCONCLUSIVE`. The width constraint \( \lambda - \gamma \ge \omega \) is verified during policy retrieval rather than the hot path, minimizing decision latency.

5. **Trace Emission:** A `DecisionTrace` object is instantiated, capturing the input posterior, the computed risk \( r \), the active policy snapshot \( (\lambda, \gamma, \omega) \), a UTC timestamp in ISO 8601 format, and a unique trace identifier. This record is appended to the immutable audit log atomically with respect to the decision computation.

6. **Return:** The function returns the `DecisionTrace`, which encapsulates both the categorical verdict and the complete computational provenance required for downstream verification.

The auxiliary method `get_policy_spec()` returns an immutable, read-only mapping of the active policy parameters. It carries an explicit guard comment documenting the P0-001 semantics: that `posterior` represents \( P(\text{authenticity} \mid \text{evidence}) \), that \( r \) represents fabrication risk, and that lower authenticity probability implies higher risk. This annotation serves as a future-proofing mechanism against developer-induced parameter inversion during subsequent maintenance cycles.

**Input/Output Specifications**

- **Input to `decide()`:** A single positional argument `posterior` of type `decimal.Decimal`, quantifying \( P(\text{authenticity} \mid \text{evidence}) \). Precondition: the value must lie within the closed interval \([0, 1]\) and must be quantized to the precision defined by the active decimal context. The function is total over this domain and partial otherwise, raising a domain exception for invalid inputs.

- **Output from `decide()`:** An instance of `DecisionTrace` containing the following fields:
  - `verdict`: a categorical member of the enumerated set \(\{\text{AUTHENTIC}, \text{FABRICATED}, \text{INCONCLUSIVE}\}\);
  - `computed_risk`: a `decimal.Decimal` exactly equal to \( 1 - \text{posterior} \);
  - `policy_snapshot`: a frozen `RiskParameters` record (namedtuple or equivalent immutable structure) with fields \( \lambda \), \( \gamma \), and \( \omega \);
  - `trace_id`: a UUID version 4 string, uniquely identifying the decision event for cross-referencing with external custody logs;
  - `timestamp`: an ISO 8601 timestamp string in UTC, marking the instant of trace emission;
  - `module_version`: a constant string `"v3.0-P0-001"`, identifying the exact software revision responsible for the decision logic.

**Deterministic Guarantees**

The module provides the following deterministic guarantees, which are necessary conditions for forensic admissibility and scientific reproducibility:

- **Bitwise Reproducibility:** Owing to the exclusive use of `decimal.Decimal` with a fixed precision context, an explicit rounding mode (typically `ROUND_HALF_EVEN`), and the avoidance of all binary floating-point operations, the computation of \( r \) and the subsequent threshold comparisons yield identical results across all compliant execution environments. There exists no dependency on hardware-specific floating-point units or compiler optimizations that could introduce cross-platform variance.

- **Domain Totality:** The P0-001 validation guard renders `decide()` a total function over the domain \([0, 1]\). Invalid inputs are rejected through deterministic exception pathways before any computation occurs, ensuring that no undefined or platform-dependent behavior can influence the risk calculus.

- **Policy Provenance Integrity (C4):** Because \( \lambda \), \( \gamma \), and \( \omega \) are read exclusively from `SelfAdaptiveRiskPolicy`, each `DecisionTrace` contains an unambiguous provenance link to the institutional risk configuration. The absence of local templates or hard-coded defaults eliminates silent parameter drift and configuration shadowing.

- **Semantic Non-Inversion (P0-001):** The explicit documentation and guard comments in `get_policy_spec()` codify the semantic mapping between posterior probability, fabrication risk, and verdict polarity. This structural safeguard prevents regression bugs or developer misinterpretation from inverting the authenticity–fabrication semantic axis.

- **Audit Atomicity:** Every invocation of `decide()` generates exactly one `DecisionTrace`. The emission is atomic with respect to the decision computation; under no circumstance is a verdict returned to the caller without a corresponding immutable trace record being committed to the audit substrate.

**Related VIGÍA Modules and Standards Compliance**

- **SelfAdaptiveRiskPolicy:** The sole authoritative source for the global parameter triple \( (\lambda, \gamma, \omega) \). This module implements adaptive recalibration of risk boundaries based on institutional feedback, error-rate tracking, and evolving evidentiary baselines. The read-only interface guarantees that `RiskBoundedDecisionLayer` cannot mutate policy state.

- **Semantic Coherence Engine:** The upstream module responsible for computing \( P(\text{authenticity} \mid \text{evidence}) \) from raw evidentiary signifiers, logical continuity checks, and inter-source corroboration. Its output constitutes the `posterior` input to the governance layer.

- **Evidence Ingestion Layer:** Provides canonicalized, hashed, and chain-of-custody tagged evidentiary units to the coherence engine, ensuring that the posterior received by the decision layer originates from a tamper-evident pipeline.

- **Standards Compliance:** The deterministic, reproducible, and peer-reviewable logic of the module satisfies the *Daubert* standard for scientific evidence admissibility in United States federal proceedings, particularly with respect to known error rates, testable hypotheses, and general acceptance. The module’s granular traceability, chain-of-custody preservation, and access-control semantics align with **GB/T** national standards for electronic data forensics (e.g., GB/T 29360-2012 regarding digital evidence collection and preservation). Furthermore, the comprehensive audit immutability and non-repudiation properties satisfy the **MLPS 2.0** (Multi-Level Protection Scheme 2.0) mandates for audit granularity, hierarchical protection, and accountability in classified information systems.

## ESPAÑOL

El módulo `vigia/governance/risk_bounded_layer_v2.py` implementa la `RiskBoundedDecisionLayer` (versión 3.0-P0-001, con los parches C4, C5, P1-A, P2 y P0-001 aplicados). Al integrar este componente en la canalización forense VIGÍA, observás que constituye el estrato terminal de gobernanza, encargado de convertir evaluaciones probabilísticas continuas de la evidencia en veredictos discretos admisibles jurídicamente. Mientras que las capas de inferencia ascendentes computan verosimilitudes brutas sobre signos evidenciales, esta capa impone un sobre de riesgo rígido que te impide emitir decisiones automáticas en zonas epistémicamente peligrosas. Su arquitectura se encuentra deliberadamente segregada tanto de la ingestión de evidencia como del cálculo de la probabilidad a posteriori, estableciendo una separación clara de responsabilidades entre la inferencia científica y la acción de gobernanza. Cada veredicto emitido se acompaña de un registro inmutable de `DecisionTrace`, de modo que vos contás con la procedencia lógica completa —desde la evidencia bruta hasta la decisión categórica— para auditorías adversariales, revisión por pares y escrutinio judicial.

**Fundamentos matemáticos**

La capa opera sobre la probabilidad a posteriori bayesiana \( P(A \mid E) \), donde \( A \) denota la hipótesis de que un artefacto evidencial dado es auténtico y \( E \) representa el corpus forense completo sintetizado por los módulos de coherencia semántica ascendentes. Esta posterior cuantifica el grado de creencia justificada en la autenticidad condicionada a la evidencia observada. Si analizás la función de riesgo, notarás que el módulo define el riesgo de fabricación \( r \) como la probabilidad complementaria exacta:

\[
r = 1 - P(A \mid E)
\]

con el codominio \( r \in [0, 1] \). Este invariante establece una aplicación monótonamente decreciente entre la certeza epistémica y el riesgo institucional: a medida que la creencia en la autenticidad se aproxima a la unidad, el riesgo de fabricación se anula asintóticamente, y viceversa, una posterior que tiende a cero implica un riesgo de fabricación casi cierto.

Los límites de decisión que vos utilizás se rigen por la tripleta de parámetros \( (\lambda, \gamma, \omega) \in \mathbb{R}^3 \), que son propiedades globales del sistema leídas exclusivamente desde el módulo `SelfAdaptiveRiskPolicy` conforme al parche C4. Estos parámetros delimitan tres regiones de decisión mutuamente excluyentes:

- **Región de autenticidad:** \( \Omega_{\text{auténtico}} = \{ P \mid P \ge \lambda \} \)
- **Región inconclusa:** \( \Omega_{\text{inconcluso}} = \{ P \mid \gamma < P < \lambda \} \)
- **Región de fabricación:** \( \Omega_{\text{fabricado}} = \{ P \mid P \le \gamma \} \)

La anchura de la zona inconclusa se ve restringida por la banda de tolerancia a la ambigüedad \( \omega \), de modo que \( \lambda - \gamma \ge \omega \). Esta partición tripartita implementa un mecanismo de rechazo acotado por riesgo: el sistema se abstiene de emitir veredictos definitivos positivos o negativos siempre que la posterior caiga dentro de la zona media peligrosa, previniendo así la falsa certeza bajo condiciones evidenciales ambiguas. La utilidad esperada de cada región se calibra implícitamente mediante la política adaptativa, aunque la capa local consume estrictamente los límites sin incorporar funciones de utilidad propias.

Toda la aritmética se ejecuta mediante la clase `decimal.Decimal` de Python dentro de un contexto decimal de precisión fija y local al hilo. Este diseño elimina el error de representación, la indeterminación del redondeo y la varianza entre plataformas propia de la aritmética de punto flotante binaria IEEE-754, lo cual resulta esencial cuando un veredicto puede depender de un valor de posterior infinitesimalmente cercano a un umbral de decisión.

**Descripción del algoritmo**

El punto de entrada principal, `decide(posterior)`, ejecuta un algoritmo estrictamente secuencial y de ramas predecibles, diseñado para que vos podás auditarlo paso a paso:

1. **Guarda de validación (P0-001):** Al invocar la función, el parámetro `posterior` se somete a una validación de dominio que impone \( 0 \le \text{posterior} \le 1 \). Si ingresás un valor fuera de este rango, el sistema dispara una excepción determinística antes de que ocurra cualquier cómputo dependiente del estado, evitando la inversión semántica mediante la cual una probabilidad no normalizada o invertida podría corromper el cálculo del riesgo. Esta guarda codifica la ecuación semántica explícita \( \text{posterior} = P(\text{autenticidad} \mid \text{evidencia}) \).

2. **Recuperación de la política (C4 FIX):** La capa realiza una consulta de solo lectura a `SelfAdaptiveRiskPolicy` para obtener el conjunto de parámetros globales \( (\lambda, \gamma, \omega) \). Esta consulta omite toda plantilla local, archivo de configuración o diccionario de valores por defecto, de modo que asegurás que el sobre de riesgo refleje la única fuente institucional de verdad. No se permiten anulaciones en tiempo de ejecución.

3. **Cómputo del riesgo:** Vos podés verificar que el riesgo de fabricación se calcula como \( r = 1 - \text{posterior} \) mediante una sustracción decimal exacta dentro del contexto de precisión fija. La operación se garantiza reproducible bit a bit entre revisiones de software homogéneas, independientemente de la arquitectura de la CPU o el sistema operativo del huésped.

4. **Evaluación de límites:** El sistema compara la posterior contra los umbrales recuperados. Si \( \text{posterior} \ge \lambda \), el veredicto categórico es `AUTÉNTICO`. Si \( \text{posterior} \le \gamma \), el veredicto es `FABRICADO`. En caso contrario, el veredicto es `INCONCLUSO`. La restricción de anchura \( \lambda - \gamma \ge \omega \) se verifica durante la recuperación de la política y no en la ruta activa, minimizando la latencia de decisión.

5. **Emisión de la traza:** Se instancia un objeto `DecisionTrace` que captura la posterior de entrada, el riesgo computado \( r \), la instantánea de la política activa \( (\lambda, \gamma, \omega) \), una marca temporal UTC en formato ISO 8601 y un identificador único de traza. Este registro se anexa al log de auditoría inmutable de forma atómica respecto al cómputo de la decisión, de modo que vos disponés de un registro completo e inalterable.

6. **Retorno:** La función te devuelve el `DecisionTrace`, que encapsula tanto el veredicto categórico como la procedencia computacional completa requerida para la verificación descendente.

El método auxiliar `get_policy_spec()` devuelve un mapeo inmutable de solo lectura de los parámetros de la política activa. Dicho mapeo contiene un comentario de guarda explícito que documenta las semánticas P0-001: que `posterior` representa \( P(\text{autenticidad} \mid \text{evidencia}) \), que \( r \) representa el riesgo de fabricación, y que una menor probabilidad de autenticidad implica un mayor riesgo. Esta anotación funciona como mecanismo de protección frente a futuros ciclos de mantenimiento en los que vos u otro desarrollador podrían inducir una inversión de parámetros.

**Especificaciones de entrada y salida**

- **Entrada de `decide()`:** Vos debés proporcionar un único argumento posicional `posterior` de tipo `decimal.Decimal`, que cuantifica \( P(\text{autenticidad} \mid \text{evidencia}) \). Precondición: el valor debe encontrarse dentro del intervalo cerrado \([0, 1]\) y debe estar cuantizado a la precisión definida por el contexto decimal activo. La función es total sobre este dominio y parcial en caso contrario, levantando una excepción de dominio para entradas inválidas.

- **Salida de `decide()`:** La función te devuelve una instancia de `DecisionTrace` que contiene los siguientes campos:
  - `verdict`: miembro categórico del conjunto enumerado \(\{\text{AUTÉNTICO}, \text{FABRICADO}, \text{INCONCLUSO}\}\);
  - `computed_risk`: un `decimal.Decimal` exactamente igual a \( 1 - \text{posterior} \);
  - `policy_snapshot`: un registro `RiskParameters` inmutable (namedtuple o estructura equivalente) con campos \( \lambda \), \( \gamma \) y \( \omega \);
  - `trace_id`: una cadena UUID versión 4, que identifica de manera única el evento de decisión para su referencia cruzada con logs de custodia externos;
  - `timestamp`: una cadena de marca temporal ISO 8601 en UTC, que señala el instante de emisión de la traza;
  - `module_version`: una cadena constante `"v3.0-P0-001"`, que identifica la revisión de software exacta responsable de la lógica de decisión.

**Garantías determinísticas**

El módulo te provee las siguientes garantías determinísticas, las cuales constituyen condiciones necesarias para la admisibilidad forense y la reproducibilidad científica:

- **Reproducibilidad bit a bit:** Debido al uso exclusivo de `decimal.Decimal` con un contexto de precisión fija, un modo de redondeo explícito (típicamente `ROUND_HALF_EVEN`) y la ausencia de toda operación de punto flotante binaria, el cálculo de \( r \) y las comparaciones subsiguientes contra umbrales arrojan resultados idénticos en todos los entornos de ejecución compatibles. No existe dependencia de unidades de punto flotante específicas del hardware ni de optimizaciones del compilador que pudieran introducir varianza entre plataformas.

- **Totalidad de dominio:** La guarda de validación P0-001 convierte a `decide()` en una función total sobre el dominio \([0, 1]\). Si proporcionás una entrada inválida, el sistema la rechaza a través de rutas de excepción deterministas antes de que ocurra cualquier cómputo, asegurando que ningún comportamiento indefinido o dependiente de la plataforma pueda influir sobre el cálculo del riesgo.

- **Integridad de la procedencia de la política (C4):** Dado que \( \lambda \), \( \gamma \) y \( \omega \) se leen exclusivamente desde `SelfAdaptiveRiskPolicy`, cada `DecisionTrace` contiene un enlace de procedencia inequívoco hacia la configuración de riesgo institucional, eliminando la deriva silenciosa de parámetros.

- **No inversión semántica (P0-001):** Los comentarios de guarda documentan explícitamente que `posterior` representa \( P(\text{autenticidad} \mid \text{evidencia}) \) y que \( r \) representa el riesgo de fabricación, previniendo regresiones que inviertan el eje semántico autenticidad–fabricación.

> **【Nota Científica】**
> La capa de gobernanza operacionaliza los marcos de Peirce, Eco y Grice como mecanismos de control de riesgo institucional. La Primereidad peirceana es la probabilidad a posteriori bruta \( P(A \mid E) \) — el fenómeno tal como llega. La Segundidad es la comparación diferencial contra los umbrales \( \lambda \) y \( \gamma \): ¿dónde cae la probabilidad en relación con los límites de riesgo institucional? La Terceridad es el veredicto categórico — la ley repetible que transforma la incertidumbre continua en una decisión discreta y jurídicamente admisible. La enciclopedia de Eco es la política `SelfAdaptiveRiskPolicy`: el conocimiento institucional codificado sobre qué nivel de riesgo es tolerable. Las máximas de Grice imponen la zona inconclusa: cuando la evidencia no coopera con una respuesta clara, el sistema se abstiene de emitir un veredicto definitivo. Todas las operaciones usan aritmética decimal de precisión fija, garantizando reproducibilidad bajo el estándar Daubert.

### Glosario

1. **Probabilidad a posteriori bayesiana** — \( P(A \mid E) \): grado de creencia justificada en la autenticidad condicionada a la evidencia observada.
2. **Riesgo de fabricación** — \( r = 1 - P(A \mid E) \): complemento exacto de la probabilidad a posteriori; mide la plausibilidad de adulteración.
3. **Región inconclusa** — Zona de decisión donde la posterior cae entre \( \gamma \) y \( \lambda \); el sistema se abstiene de emitir un veredicto definitivo.
4. **DecisionTrace** — Registro inmutable que captura la posterior, el riesgo calculado, la instantánea de la política y la marca temporal de cada decisión.
5. **SelfAdaptiveRiskPolicy** — Fuente única y autorizada de los parámetros de riesgo globales \( (\lambda, \gamma, \omega) \).
6. **Banda de tolerancia \( \omega \)** — Anchura mínima obligatoria de la zona inconclusa; impide que los límites colapsen a un umbral único.
7. **Aritmética decimal de precisión fija** — Computaciones realizadas mediante `decimal.Decimal` con modo de redondeo explícito, eliminando la varianza de punto flotante.
8. **Parche P0-001** — Guarda de validación que documenta la semántica exacta de los parámetros e impide la inversión autenticidad–fabricación.
9. **Atomicidad de emisión** — Cada invocación de `decide()` genera exactamente un `DecisionTrace`; ningún veredicto se devuelve sin un registro de auditoría correspondiente.
10. **Estándar Daubert** — Criterio legal estadounidense que exige métodos científicos verificables con tasas de error conocidas; satisfecho por la aritmética exacta y la trazabilidad completa de la capa.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## РУССКИЙ

Модуль `vigia/governance/risk_bounded_layer_v2.py` реализует `RiskBoundedDecisionLayer` (версия 3.0-P0-001, с применёнными патчами C4, C5, P1-A, P2 и P0-001). Он составляет терминальный управленческий слой конвейера судебной экспертизы VIGÍA, несущий институциональную ответственность за преобразование непрерывных вероятностных оценок доказательств в дискретные, юридически допустимые вердикты. Архитектура намеренно разделена: EBS отделён как от приёма доказательств, так и от вычисления апостериорной вероятности, обеспечивая чистое разделение ответственности между научным инференсом и управленческим действием. Каждый выданный вердикт сопровождается неизменяемой записью `DecisionTrace`, гарантирующей полную логическую провенанс от исходного доказательства до категорического решения.

**Математические основания**

Слой оперирует байесовской апостериорной вероятностью \( P(A \mid E) \), где \( A \) обозначает гипотезу о подлинности артефакта, а \( E \) — полный корпус судебных доказательств. Риск фальсификации определяется как точная дополнительная вероятность:

\[
r = 1 - P(A \mid E)
\]

Границы решений задаются тройкой параметров \( (\lambda, \gamma, \omega) \), читаемых исключительно из `SelfAdaptiveRiskPolicy` согласно патчу C4. Эти параметры разграничивают три взаимоисключающие области решений:

- **Область подлинности:** \( \Omega_{\text{подлинный}} = \{ P \mid P \ge \lambda \} \)
- **Неопределённая область:** \( \Omega_{\text{неопределённый}} = \{ P \mid \gamma < P < \lambda \} \)
- **Область фальсификации:** \( \Omega_{\text{фальсифицированный}} = \{ P \mid P \le \gamma \} \)

Ширина неопределённой зоны ограничена допустимым диапазоном неоднозначности \( \omega \), так что \( \lambda - \gamma \ge \omega \). Вся арифметика выполняется посредством класса `decimal.Decimal` в фиксированном контексте точности, исключая ошибки представления и неопределённость округления, присущие двоичной арифметике IEEE-754 с плавающей запятой.

**Описание алгоритма**

Основная точка входа `decide(posterior)` выполняет строго последовательный алгоритм:

1. **Защитник валидации (P0-001):** Входной параметр `posterior` проходит доменную валидацию \( 0 \le \text{posterior} \le 1 \). Любое отклонение вызывает детерминированное исключение до начала любых вычислений.

2. **Получение политики (C4):** Слой выполняет запрос только для чтения к `SelfAdaptiveRiskPolicy` для получения текущего набора глобальных параметров \( (\lambda, \gamma, \omega) \).

3. **Вычисление риска:** Риск фальсификации вычисляется как \( r = 1 - \text{posterior} \) с использованием точного десятичного вычитания.

4. **Оценка границ:** При \( \text{posterior} \ge \lambda \) — вердикт `ПОДЛИННЫЙ`; при \( \text{posterior} \le \gamma \) — вердикт `ФАЛЬСИФИЦИРОВАННЫЙ`; иначе — `НЕОПРЕДЕЛЁННЫЙ`.

5. **Эмиссия трассы:** Инициализируется объект `DecisionTrace`, атомарно фиксирующий входную апостериорную вероятность, вычисленный риск, снимок активной политики, временну́ю метку UTC и уникальный идентификатор трассы.

**Детерминированные гарантии**

- **Побитовая воспроизводимость:** Исключительное использование `decimal.Decimal` с фиксированной точностью гарантирует идентичные результаты на всех совместимых платформах.
- **Доменная полнота:** Защитник P0-001 делает `decide()` тотальной функцией на области \([0, 1]\).
- **Целостность провенанс политики:** Каждый `DecisionTrace` содержает однозначную ссылку на институциональную конфигурацию риска.
- **Атомарность аудита:** Каждый вызов `decide()` порождает ровно один `DecisionTrace`.

> **【Научное примечание】**
> Управленческий слой операционализирует концепции Пирса, Эко и Грайса как механизмы институционального контроля риска. Первичность Пирса — это необработанная апостериорная вероятность \( P(A \mid E) \): феномен как таковой. Вторичность — дифференциальное сравнение с порогами \( \lambda \) и \( \gamma \): где вероятность находится относительно институциональных границ риска? Третичность — категорический вердикт: повторяющийся закон, преобразующий непрерывную неопределённость в дискретное, юридически допустимое решение. Энциклопедия Эко — это политика `SelfAdaptiveRiskPolicy`: институционализированное знание о допустимом уровне риска. Максимы Грайса обеспечивают неопределённую зону: когда доказательства не дают чёткого ответа, система воздерживается от окончательного вердикта. Все операции используют десятичную арифметику фиксированной точности, гарантируя воспроизводимость согласно стандарту Daubert.

### Глоссарий

1. **Байесовская апостериорная вероятность** — \( P(A \mid E) \): степень обоснованного убеждения в подлинности при условии наблюдаемых доказательств.
2. **Риск фальсификации** — \( r = 1 - P(A \mid E) \): точное дополнение апостериорной вероятности; измеряет правдоподобие фальсификации.
3. **Неопределённая область** — Зона решений, где апостериорная вероятность попадает между \( \gamma \) и \( \lambda \); система воздерживается от окончательного вердикта.
4. **DecisionTrace** — Неизменяемая запись, фиксирующая апостериорную вероятность, вычисленный риск, снимок политики и временну́ю метку каждого решения.
5. **SelfAdaptiveRiskPolicy** — Единственный авторитетный источник глобальных параметров риска \( (\lambda, \gamma, \omega) \).
6. **Допустимый диапазон \( \omega \)** — Минимальная обязательная ширина неопределённой зоны; предотвращает коллапс границ к единственному порогу.
7. **Десятичная арифметика фиксированной точности** — Вычисления посредством `decimal.Decimal` с явным режимом округления, исключающим дисперсию с плавающей запятой.
8. **Патч P0-001** — Защитник валидации, документирующий точную семантику параметров и предотвращающий инверсию оси подлинность–фальсификация.
9. **Атомарность эмиссии** — Каждый вызов `decide()` порождает ровно один `DecisionTrace`; ни один вердикт не возвращается без соответствующей аудиторской записи.
10. **Стандарт Daubert** — Американский правовой критерий, требующий верифицируемых научных методов с известными частотами ошибок.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## 中文

模块 `vigia/governance/risk_bounded_layer_v2.py` 实现了 `RiskBoundedDecisionLayer`（版本 3.0-P0-001，应用了补丁 C4、C5、P1-A、P2 和 P0-001）。它构成 VIGÍA 取证流水线的终端治理层，承担将连续概率证据评估转换为离散的、法律上可采纳的裁决的机构责任。其架构故意与证据摄取和后验计算分离，在科学推断和治理行动之间建立清晰的职责分离。每个发出的裁决都附有不可变的 `DecisionTrace` 记录，确保从原始证据到分类决策的完整逻辑溯源可用于对抗审计、同行审查和司法审查。

**数学基础**

该层在贝叶斯后验概率 \( P(A \mid E) \) 上运作，其中 \( A \) 表示给定证据工件是真实的假设，\( E \) 代表上游语义连贯模块综合的完整取证证据集。模块将伪造风险 \( r \) 定义为精确的互补概率：

\[
r = 1 - P(A \mid E)
\]

决策边界由参数三元组 \( (\lambda, \gamma, \omega) \) 控制，这些参数根据补丁 C4 专门从 `SelfAdaptiveRiskPolicy` 模块读取：

- **真实性区域：** \( \Omega_{\text{真实}} = \{ P \mid P \ge \lambda \} \)
- **不确定区域：** \( \Omega_{\text{不确定}} = \{ P \mid \gamma < P < \lambda \} \)
- **伪造区域：** \( \Omega_{\text{伪造}} = \{ P \mid P \le \gamma \} \)

不确定区域的宽度受模糊容忍带宽 \( \omega \) 约束，使得 \( \lambda - \gamma \ge \omega \)。所有运算均在固定精度的线程本地十进制上下文中使用 `decimal.Decimal` 类执行，消除 IEEE-754 二进制浮点运算固有的表示误差和舍入不确定性。

**算法描述**

主入口点 `decide(posterior)` 执行严格顺序算法：

1. **验证守卫（P0-001）：** 输入 `posterior` 进行域验证，强制 \( 0 \le \text{posterior} \le 1 \)。
2. **策略检索（C4）：** 层对 `SelfAdaptiveRiskPolicy` 执行只读查询，获取当前全局参数集 \( (\lambda, \gamma, \omega) \)。
3. **风险计算：** 使用精确十进制减法计算伪造风险 \( r = 1 - \text{posterior} \)。
4. **边界评估：** 若 \( \text{posterior} \ge \lambda \)，类别裁决为"真实"；若 \( \text{posterior} \le \gamma \)，裁决为"伪造"；否则为"不确定"。
5. **轨迹发出：** 实例化 `DecisionTrace` 对象，原子性地捕获输入后验、计算的风险、活动策略快照、UTC 时间戳和唯一轨迹标识符。

**确定性保证**

- **逐位可重现性：** 专门使用带固定精度上下文的 `decimal.Decimal` 确保所有兼容执行环境中的相同结果。
- **域完整性：** P0-001 验证守卫使 `decide()` 在域 \([0, 1]\) 上成为全函数。
- **策略溯源完整性：** 每个 `DecisionTrace` 包含到机构风险配置的明确溯源链接。
- **审计原子性：** 每次 `decide()` 调用恰好生成一个 `DecisionTrace`。

> **【科学说明】**
> 治理层将皮尔斯（Peirce）、艾柯（Eco）和格赖斯（Grice）的框架操作化为机构风险控制机制。皮尔斯的初性是原始后验概率 \( P(A \mid E) \)——现象本身。二性是与阈值 \( \lambda \) 和 \( \gamma \) 的差异比较：后验相对于机构风险边界处于何处？三性是类别裁决——将连续不确定性转化为离散、法律可采纳决策的可重复规律。艾柯的百科全书是 `SelfAdaptiveRiskPolicy`：关于可接受风险水平的机构化知识。格赖斯的准则强制执行不确定区域：当证据未能给出明确答案时，系统不发出明确裁决。所有运算使用固定精度十进制运算，确保道伯特标准下的法庭可重现性。

### 词汇表

1. **贝叶斯后验概率** — \( P(A \mid E) \)：在观察到的证据条件下对真实性的有理置信度。
2. **伪造风险** — \( r = 1 - P(A \mid E) \)：后验概率的精确互补；衡量伪造的可信度。
3. **不确定区域** — 后验落在 \( \gamma \) 和 \( \lambda \) 之间的决策区域；系统不发出明确裁决。
4. **DecisionTrace** — 捕获每次决策的输入后验、计算风险、策略快照和时间戳的不可变记录。
5. **SelfAdaptiveRiskPolicy** — 全局风险参数 \( (\lambda, \gamma, \omega) \) 的唯一权威来源。
6. **容忍带宽 \( \omega \)** — 不确定区域的最小强制宽度；防止边界坍缩到单一阈值。
7. **固定精度十进制运算** — 通过带显式舍入模式的 `decimal.Decimal` 进行的计算，消除浮点方差。
8. **补丁 P0-001** — 记录精确参数语义并防止真实性-伪造语义轴反转的验证守卫。
9. **发出原子性** — 每次 `decide()` 调用恰好生成一个 `DecisionTrace`；没有相应审计记录就不返回裁决。
10. **道伯特标准（Daubert Standard）** — 要求可验证的科学方法具有已知错误率的美国联邦法律标准。

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---