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

- **Integridad de la procedencia de la política (C4):** Dado que \( \lambda \), \( \gamma \) y \( \omega \) se leen exclusivamente desde `SelfAdaptiveRiskPolicy`, cada `DecisionTrace` que vos obtenés contiene un enlace de procedencia inequívoco hacia la configuración de riesgo institucional. La ausencia de plantillas locales o valores por defecto cod