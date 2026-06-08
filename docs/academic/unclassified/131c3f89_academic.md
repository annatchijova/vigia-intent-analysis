## ENGLISH

### 1. Module Purpose and Forensic Context
The VIGÍA Canonical Forensic Pipeline Adapter, cryptographically designated by hash `131c3f89`, constitutes the deterministic orchestration kernel of the VIGÍA digital-forensic architecture. Its principal mandate is to execute a formally specified three-stage analytical workflow—Detection ($\mathcal{D}$), Aggregation ($\mathcal{A}$), and Decision ($\Delta$)—over structured evidentiary records ingested exclusively via command-line invocation. Unlike conventional forensic platforms that employ stochastic scoring heuristics, Monte Carlo simulations, or non-deterministic machine-learning inference graphs, module `131c3f89` rigorously excludes all sources of entropy from its analytical path. The result is a purely functional pipeline that produces bitwise-consistent, per-artifact findings across repeated executions on identical inputs. This architectural posture directly satisfies the scientific reliability prongs of the *Daubert* standard (Federal Rules of Evidence 702), namely testability, peer review, and known or calculable error rates. Within the VIGÍA ecosystem, the module operates as the canonical mediation layer between upstream normalization subsystems—the **VIGÍA Ingestion Engine** and the **VIGÍA Evidence Normalizer**—and downstream consumers, including the **VIGÍA Report Generator**, the **VIGÍA Cryptographic Attestation Module**, and the **VIGÍA Audit Logger**. By binding the entire analytical logic to a static, version-pinned configuration document, the adapter ensures that every classification emitted can be independently reproduced, challenged, and verified by peer laboratories, a requirement increasingly critical under GB/T 29360-2012 (Electronic Data Forensic Inspection Technology) and MLPS 2.0 Level-3 audit mandates.

### 2. Mathematical Foundations
The adapter is formalized as a total deterministic function over discrete evidence and configuration spaces. Let $\mathcal{E}$ denote the space of structured evidentiary records, where each record $e \in \mathcal{E}$ is an ordered tuple $e = (a, m, b)$. Here, $a \in \mathcal{A}$ is the artifact identifier drawn from a globally unique namespace, $m \in \mathcal{M}$ is a finite-length provenance metadata block, and $b \in \{0,1\}^{256}$ is a cryptographic digest of the artifact’s byte sequence (SHA-256). Let $\mathcal{C}$ denote the configuration space, where every $c \in \mathcal{C}$ is statically validated against a formal schema to preclude undefined rule references or circular precedence relations. Let $\mathcal{F}$ denote the findings space. The forensic pipeline is defined as the function composition:

$$\Pi: \mathcal{E} \times \mathcal{C} \to \mathcal{F}, \quad \Pi(e, c) = (\Delta \circ \mathcal{A} \circ \mathcal{D})(e, c)$$

The three transformational stages are rigorously characterized as follows:

- **Detection.** $\mathcal{D}: \mathcal{E} \times \mathcal{C} \to 2^{\mathcal{P}}$ maps an evidentiary record and its active configuration to the power set of primitive indicators $\mathcal{P}$. Each primitive indicator $p \in \mathcal{P}$ is a decidable predicate $p(a, m, b)$ evaluating to $\{\text{TRUE}, \text{FALSE}\}$. The detection engine evaluates the rule set $R_c \subseteq \mathcal{C}$ in a deterministic lexicographic order keyed by rule identifier, ensuring that rule-to-indicator mappings are invariant across executions.

- **Aggregation.** $\mathcal{A}: 2^{\mathcal{P}} \times \mathcal{C} \to \mathcal{L}$ lifts the extracted indicator set into a bounded lattice $(\mathcal{L}, \preceq, \vee, \wedge)$. The join operator $\vee$ aggregates corroborating indicators monotonically, while the meet operator $\wedge$ resolves conflicts via a strict partial precedence relation $\prec_c \, \subseteq \mathcal{P} \times \mathcal{P}$ encoded within $c$. If $p_1 \prec_c p_2$, then $\phi(p_1) \wedge \phi(p_2) = \phi(p_2)$, where $\phi: \mathcal{P} \to \mathcal{L}$ is the canonical embedding of primitives into lattice atoms. The lattice is fully deterministic; no probabilistic, fuzzy, or Bayesian operators are admitted.

- **Decision.** $\Delta: \mathcal{L} \times \mathcal{C} \to \mathcal{F}$ performs a threshold-based classification on the aggregated lattice element, emitting a per-artifact finding $f \in \mathcal{F}$. The decision boundary $\theta_c = (\theta_{\text{low}}, \theta_{\text{high}}) \in \mathcal{L} \times \mathcal{L}$ is configuration-dependent but fixed for a given $c$. Consequently, $\forall e_1, e_2 \in \mathcal{E}, (e_1 = e_2) \implies \Pi(e_1, c) = \Pi(e_2, c)$, establishing the pipeline as a mathematical function in the strict sense.

An optional **Negation Handler** $\mathcal{N}$ extends the detection stage to $\mathcal{D}'$ by introducing complementary predicates $\neg p$ drawn from a negation-ready subset $\mathcal{P}_{\text{neg}}(c) \subseteq \mathcal{P}$. This extension operates on the principle of material absence: $\neg p$ is materialized only when the evidentiary record contains the artifact context in which $p$ would be expected, thereby preventing vacuous truth from contaminating the indicator set. Formally:

$$\mathcal{D}'(e, c) = \mathcal{D}(e, c) \cup \big\{ \neg p \mid p \in \mathcal{P}_{\text{neg}}(c) \;\wedge\; \text{Context}(e, p) = \text{TRUE} \big\}$$

### 3. Algorithmic Description
The execution flow is partitioned into three strictly sequential, stateless, and side-effect-free transformations.

*Stage I—Detection.* Upon CLI invocation, the module parses mandatory and optional arguments, loads the evidence manifest $E = \{e_1, \dots, e_n\} \subset \mathcal{E}$, and binds the configuration document $c \in \mathcal{C}$. The detection engine iterates over each record $e_i$ and evaluates the ordered rule set $R_c = \{r_1, \dots, r_k\}$. Each rule $r_j$ is a first-order logical expression over the schema of $\mathcal{E}$. The output is an indexed family of indicator sets $\{I_1, \dots, I_n\}$, where $I_i = \{ p \in \mathcal{P} \mid \exists r \in R_c, r(e_i) \models p \}$. If the negation handler is enabled via the `--negation-handler` flag, the engine additionally evaluates the dual rule set $R_c^{\neg}$ to populate negated indicators under the material-absence constraint. The time complexity of this stage is $O(|E| \cdot |R_c| \cdot L)$, where $L$ is the maximum predicate evaluation cost, and the space complexity is $O(|E| \cdot |\mathcal{P}|)$.

*Stage II—Aggregation.* For each indicator set $I_i$, the aggregation engine computes the lattice element $l_i = \bigvee_{p \in I_i} \phi(p)$. In the presence of conflicting indicators, the engine applies the precedence relation $\prec_c$ to compute pairwise meets before performing the global join. This schedule guarantees that the aggregation is both associative and deterministic, yielding a unique supremum $l_i \in \mathcal{L}$ for every $I_i$. The complexity is $O(|I_i| \cdot \log |\mathcal{L}|)$ per record due to precedence-resolved merge operations.

*Stage III—Decision.* The decision engine applies the deterministic threshold function:

$$\tau(l_i, c) = \begin{cases} \text{CONFIRMED} & \text{if } l_i \succeq \theta_{\text{high}} \\ \text{SUSPICIOUS} & \text{if } \theta_{\text{low}} \preceq l_i \prec \theta_{\text{high}} \\ \text{BENIGN} & \text{if } l_i \prec \theta_{\text{low}} \end{cases}$$

The resulting finding $f_i = (a_i, \tau_i, \mu_i)$ comprises the artifact identifier $a_i$, the classification tag $\tau_i$, and a deterministic metadata packet $\mu_i$. The metadata packet encodes the rule hit vector $\mathbf{h}_i \in \{0,1\}^{|R_c|}$, the lattice coordinate $\lambda(l_i) \in \mathbb{N}^d$ under a fixed enumeration of $\mathcal{L}$, and a cumulative execution digest $d_i \in \{0,1\}^{256}$.

### 4. Input/Output Specifications
*Inputs.* The module is invoked through a command-line interface accepting the following parameters:
- `--evidence-path` (mandatory): A file-system path or URI pointing to an evidentiary manifest conforming to the VIGÍA Normalized Evidence Schema (VNES). The manifest must be encoded in UTF-8 with normalized line endings (LF) to prevent platform-dependent parsing variance.
- `--config` (mandatory): A path to a JSON or YAML configuration document defining the rule set $R_c$, the lattice specification $(\mathcal{L}, \preceq)$, the embedding map $\phi$, the precedence relation $\prec_c$, and the threshold boundaries $\theta$.
- `--negation-handler` (optional): A Boolean flag that, when present, activates the extended detection space $\mathcal{D}'$.
- `--audit-anchor` (optional): A hexadecimal attestation string that links the current execution to an immutable entry in the **VIGÍA Audit Logger**.

*Outputs.* The module emits a single structured findings document, by default in canonical JSON with sorted keys and fixed-precision decimal encoding, eliminating serialization nondeterminism. The document schema comprises:
- `execution_digest`: The SHA-256 hash of the canonical tuple $(c, E, \text{module\_version})$.
- `findings_array`: An ordered sequence of per-artifact objects. Each object contains `artifact_id` (string), `classification` (enum: CONFIRMED, SUSPICIOUS, BENIGN), `lattice_coordinate` (array of integers), `indicator_hit_vector` (bit string), and `timestamp_utc` (string, sourced monotonically from the audit subsystem; while the absolute timestamp is environment-dependent, the analytical payload is strictly independent of wall-clock time).
- `determinism_proof`: A Merkle root computed over the individual SHA-256 hashes of each $f_i$, enabling bitwise consistency verification across executions and laboratories.

### 5. Deterministic Guarantees and Compliance
The adapter enforces deterministic execution through a confluence of language-level, algorithmic, and architectural constraints:
- **Pure Functional Semantics.** All core transformations $\mathcal{D}$, $\mathcal{A}$, and $\Delta$ are implemented as pure functions without reference to pseudorandom number generators, hardware floating-point units, or concurrency-dependent thread scheduling. Any arithmetic requiring fractional representation is performed using fixed-point rational libraries to avoid IEEE-754 cross-platform variance.
- **Bitwise Consistency.** For any fixed input tuple $(E, c)$ and module version $v$, the serialized output byte sequence is invariant across repeated executions on architecturally identical platforms. Formally, $\forall t_1, t_2, H(\Pi(E, c; t_1)) = H(\Pi(E, c; t_2))$, where $H$ denotes SHA-256. This property is verified continuously by the **VIGÍA Peer Review Gateway** during inter-laboratory validation.
- **Idempotence under Re-execution.** When an output findings document is re-ingested into the pipeline via the **VIGÍA Evidence Normalizer**, the adapter treats the document as a new artifact and produces a meta-finding that cryptographically attests to the prior execution hash without mutating the original analytical conclusions.
- **Standards Compliance.** The deterministic architecture directly supports *Daubert* admissibility by providing testable, peer-reviewable procedures with calculable error bounds (zero nondeterministic variance). It satisfies **GB/T 29360-2012** requirements for reproducible forensic extraction and aligns with **MLPS 2.0** Level-3 controls for audit traceability and deterministic security analytics.

### 6. Integration with Related VIGÍA Modules
Module `131c3f89` is architecturally embedded within a directed acyclic data flow. Upstream, the **VIGÍA Ingestion Engine** performs syntactic validation of the VNES manifest and binds cryptographic provenance anchors to each $e \in \mathcal{E}$. The **VIGÍA Evidence Normalizer** transcodes heterogeneous forensic disk images, memory dumps, and log streams into the canonical VNES representation, ensuring that the adapter receives a schema-rigid input. Downstream, the **VIGÍA Report Generator** consumes the `findings_array` to synthesize human-readable case narratives, while the **VIGÍA Cryptographic Attestation Module** appends the `determinism_proof` Merkle root to the chain-of-custody ledger. The **VIGÍA Audit Logger** intercepts every CLI invocation to append tamper-evident log entries containing the `execution_digest`. In regulated environments, the **VIGÍA Peer Review Gateway** re-executes the adapter against identical evidence manifests to confirm bitwise consistency, thereby closing the forensic validation loop.

### 7. Conclusion
The VIGÍA Canonical Forensic Pipeline Adapter (`131c3f89`) establishes a mathematically rigorous, deterministic foundation for digital-forensic analysis. By encoding the entire analytical logic within statically validated, configuration-driven pure functions and by excluding all nondeterministic scoring mechanisms, the module guarantees that every per-artifact finding is reproducible, defensible, and compliant with prevailing international and national forensic standards.

## ESPAÑOL

### 1. Propósito del módulo y contexto forense
El Adaptador Canónico de Canalización Forense VIGÍA, designado mediante el hash criptográfico `131c3f89`, constituye el núcleo de orquestación determinista dentro de la arquitectura de informática forense VIGÍA. Su función primordial consiste en ejecutar un flujo de trabajo analítico de tres etapas estrictamente formalizadas —Detección ($\mathcal{D}$), Agregación ($\mathcal{A}$) y Decisión ($\Delta$)— sobre registros de evidencia estructurados que deberás ingestar exclusivamente mediante invocación en línea de comandos. A diferencia de las plataformas forenses convencionales que se apoyan en heurísticas de puntuación estocásticas, simulaciones de Monte Carlo o grafos de inferencia de aprendizaje automático no deterministas, el módulo `131c3f89` excluye rigurosamente toda fuente de entropía de su trayectoria analítica. El resultado es una canalización puramente funcional que produce hallazgos consistentes bit a bit para cada artefacto, independientemente de cuántas veces repitas la ejecución con entradas idénticas. Esta postura arquitectónica satisface directamente los requisitos de confiabilidad científica del estándar *Daubert* (Federal Rules of Evidence 702), a saber: testabilidad, revisión por pares y tasas de error conocidas o calculables. Dentro del ecosistema VIGÍA, este módulo funciona como la capa canónica de mediación entre los subsistemas de normalización aguas arriba —el **Motor de Ingesta VIGÍA** y el **Normalizador de Evidencia VIGÍA**— y los consumidores aguas abajo, tales como el **Generador de Informes VIGÍA**, el **Módulo de Atestación Criptográfica VIGÍA** y el **Registrador de Auditoría VIGÍA**. Al vincular toda la lógica analítica a un documento de configuración estático y con versión fijada, el adaptador asegura que cada clasificación emitida pueda ser reproducida, impugnada y verificada de forma independiente por laboratorios pares, un requisito cada vez más crítico bajo la norma GB/T 29360-2012 y los mandatos de auditoría de Nivel 3 del MLPS 2.0.

### 2. Fundamentos matemáticos
El adaptador se formaliza como una función determinista total sobre espacios de evidencia y configuración discretos. Sea $\mathcal{E}$ el espacio de registros de evidencia estructurados, donde cada registro $e \in \mathcal{E}$ es una tupla ordenada $e = (a, m, b)$. Aquí, $a \in \mathcal{A}$ es el identificador de artefacto extraído de un espacio de nombres globalmente único, $m \in \mathcal{M}$ es un bloque de metadatos de procedencia de longitud finita, y $b \in \{0,1\}^{256}$ es un resumen criptográfico de la secuencia de bytes del artefacto (SHA-256). Sea $\mathcal{C}$ el espacio de configuración, en el que cada $c \in \mathcal{C}$ se valida estáticamente contra un esquema formal para impedir referencias de reglas indefinidas o relaciones de precedencia circulares. Sea $\mathcal{F}$ el espacio de hallazgos. La canalización forense se define como la composición funcional:

$$\Pi: \mathcal{E} \times \mathcal{C} \to \mathcal{F}, \quad \Pi(e, c) = (\Delta \circ \mathcal{A} \circ \mathcal{D})(e, c)$$

Las tres etapas transformacionales se caracterizan rigurosamente de la siguiente manera:

- **Detección.** $\mathcal{D}: \mathcal{E} \times \mathcal{C} \to 2^{\mathcal{P}}$ asigna un registro de evidencia y su configuración activa al conjunto potencia de indicadores primitivos $\mathcal{P}$. Cada indicador primitivo $p \in \mathcal{P}$ es un predicado decidible $p(a, m, b)$ que evalúa $\{\text{VERDADERO}, \text{FALSO}\}$. El motor de detección evalúa el conjunto de reglas $R_c \subseteq \mathcal{C}$ en un orden lexicográfico determinista claveado por el identificador de regla, asegurando que las asignaciones regla-indicador sean invariantes entre ejecuciones.

- **Agregación.** $\mathcal{A}: 2^{\mathcal{P}} \times \mathcal{C} \to \mathcal{L}$ eleva el conjunto de indicadores extraídos a una retícula acotada $(\mathcal{L}, \preceq, \vee, \wedge)$. El operador de unión $\vee$ agrega indicadores corroborantes de forma monótona, mientras que el operador de intersección $\wedge$ resuelve conflictos mediante una relación de precedencia estricta $\prec_c \, \subseteq \mathcal{P} \times \mathcal{P}$ codificada dentro de $c$. Si $p_1 \prec_c p_2$, entonces $\phi(p_1) \wedge \phi(p_2) = \phi(p_2)$, donde $\phi: \mathcal{P} \to \mathcal{L}$ es el encaje canónico de primitivos en átomos de retícula. La retícula es completamente determinista; no se admiten operadores probabilísticos, difusos ni bayesianos.

- **Decisión.** $\Delta: \mathcal{L} \times \mathcal{C} \to \mathcal{F}$ realiza una clasificación basada en umbrales sobre el elemento de retícula agregado, emitiendo un hallazgo por artefacto $f \in \mathcal{F}$. El límite de decisión $\theta_c = (\theta_{\text{alto}}, \theta_{\text{bajo}}) \in \mathcal{L} \times \mathcal{L}$ depende de la configuración, pero es fijo para una $c$ dada. En consecuencia, $\forall e_1, e_2 \in \mathcal{E}, (e_1 = e_2) \implies \Pi(e_1, c) = \Pi(e_2, c)$, estableciendo la canalización como una función matemática en sentido estricto.

Un **Gestor de Negación** $\mathcal{N}$ opcional extiende la etapa de detección a $\mathcal{D}'$ introduciendo predicados complementarios $\neg p$ extraídos de un subconjunto preparado para la negación $\mathcal{P}_{\text{neg}}(c) \subseteq \mathcal{P}$. Esta extensión opera sobre el principio de ausencia material: $\neg p$ se materializa únicamente cuando el registro de evidencia contiene el contexto del artefacto en el cual se esperaría $p$, impidiendo así que la verdad vacua contamine el conjunto de indicadores. Formalmente:

$$\mathcal{D}'(e, c) = \mathcal{D}(e, c) \cup \big\{ \neg p \mid p \in \mathcal{P}_{\text{neg}}(c) \;\wedge\; \text{Contexto}(e, p) = \text{VERDADERO} \big\}$$

### 3. Descripción algorítmica
El flujo de ejecución se divide en tres transformaciones secuenciales estrictas, sin estado y libres de efectos secundarios.

*Etapa I—Detección.* Al invocar el módulo desde la interfaz de línea de comandos, deberás especificar los argumentos mandatorios y opcionales, cargar el manifiesto de evidencia $E = \{e_1, \dots, e_n\} \subset \mathcal{E}$ y vincular el documento de configuración $c \in \mathcal{C}$. El motor de detección iterará sobre cada registro $e_i$ y evaluará el conjunto ordenado de reglas $R_c = \{r_1, \dots, r_k\}$. Cada regla $r_j$ es una expresión lógica de primer orden sobre el esquema de $\mathcal{E}$. La salida será una familia indexada de conjuntos de indicadores $\{I_1, \dots, I_n\}$, donde $I_i = \{ p \in \mathcal{P} \mid \exists r \in R_c, r(e_i) \models p \}$. Si habilitás el gestor de negación mediante la bandera `--negation-handler`, el motor evaluará adicionalmente el conjunto dual $R_c^{\neg}$ para poblar indicadores negados bajo la restricción de ausencia material. La complejidad temporal de esta etapa es $O(|E| \cdot |R_c| \cdot L)$, donde $L$ es el costo máximo de evaluación de predicados, y la complejidad espacial es $O(|E| \cdot |\mathcal{P}|)$.

*Etapa II—Agregación.* Para cada conjunto de indicadores $I_i$, el motor de agregación computa el elemento de retícula $l_i = \bigvee_{p \in I_i} \phi(p)$. Ante la presencia de indicadores conflictivos, el motor aplicará la relación de precedencia $\prec_c$ para calcular intersecciones por pares antes de realizar la unión global. Este cronograma garantiza que la agregación sea asociativa y determinista, produciendo un único supremo $l_i \in \mathcal{L}$ para cada $I_i$. La complejidad es $O(|I_i| \cdot \log |\mathcal{L}|)$ por registro debido a las operaciones de fusión resueltas por precedencia.

*Etapa III—Decisión.* El motor de decisión aplica la función de umbral determinista:

$$\tau(l_i, c) = \begin{cases} \text{CONFIRMADO} & \text{si } l_i \succeq \theta_{\text{alto}} \\ \text{SOSPECHOSO} & \text{si } \theta_{\text{bajo}} \preceq l_i \prec \theta_{\text{alto}} \\ \text{BENIGNO} & \text{si } l_i \prec \theta_{\text{bajo}} \end{cases}$$

El hallazgo resultante $f_i = (a_i, \tau_i, \mu_i)$ comprende el identificador del artefacto $a_i$, la etiqueta de clasificación $\tau_i$ y un paquete de metadatos determinista $\mu_i$. El paquete de metadatos codifica el vector de impacto de reglas $\mathbf{h}_i \in \{0,1\}^{|R_c|}$, la coordenada de retícula $\lambda(l_i) \in \mathbb{N}^d$ bajo una enumeración fija de $\mathcal{L}$, y un resumen de ejecución acumulativo $d_i \in \{0,1\}^{256}$.

### 4. Especificaciones de entrada y salida
*Entradas.* El módulo se invoca mediante una interfaz de línea de comandos que acepta los siguientes parámetros:
- `--evidence-path` (mandatorio): una ruta en el sistema de archivos o URI que apunte a un manifiesto de evidencia conforme al Esquema de Evidencia Normalizada VIGÍA (VNES). El manifiesto deberá estar codificado en UTF-8 con finales de línea normalizados (LF) para evitar varianza de análisis dependiente de la plataforma.
- `--config` (mandatorio): ruta a un documento de configuración JSON o YAML que define el conjunto de reglas $R_c$, la especificación de retícula $(\mathcal{L}, \preceq)$, el mapa de encaje $\phi$, la relación de precedencia $\prec_c$ y los límites de umbral $\theta$.
- `--negation-handler` (opcional): bandera booleana que, cuando está presente, activa el espacio de detección extendido $\mathcal{D}'$.
- `--audit-anchor` (opcional): cadena de atestación hexadecimal que vincula la ejecución actual con una entrada inmutable en el **Registrador de Auditoría VIGÍA**.

*Salidas.* El módulo emite un único documento de hallazgos estructurado, por defecto en JSON canónico con claves ordenadas y codificación decimal de precisión fija, eliminando así el no determinismo de serialización. El esquema del documento comprende:
- `execution_digest`: el hash SHA-256 de la tupla canónica $(c, E, \text{versión\_módulo})$.
- `findings_array`: una secuencia ordenada de objetos por artefacto. Cada objeto contiene `artifact_id` (cadena), `classification` (enumeración: CONFIRMADO, SOSPECHOSO, BENIGNO), `lattice_coordinate` (arreglo de enteros), `indicator_hit_vector` (cadena de bits) y `timestamp_utc` (cadena, obtenida monótonamente del subsistema de auditoría; si bien la marca temporal absoluta depende del entorno, la carga analítica es estrictamente independiente del tiempo de pared).
- `determinism_proof`: una raíz Merkle computada sobre los hashes SHA-256 individuales de cada $f_i$, permitiendo verificar la consistencia bit a bit entre ejecuciones y laboratorios.

### 5. Garantías deterministas y conformidad
El adaptador impone la ejecución determinista mediante una confluencia de restricciones a nivel de lenguaje, algoritmo y arquitectura:
- **Semántica funcional pura.** Todas las transformaciones centrales $\mathcal{D}$, $\mathcal{A}$ y $\Delta$ se implementan como funciones puras sin referencia a generadores de números pseudoaleatorios, unidades de punto flotante del hardware ni planificación de hilos dependiente del tiempo. Cualquier aritmética que requiera representación fraccionaria se realiza mediante bibliotecas racionales de punto fijo para evitar la varianza multiplataforma de IEEE-754.
- **Consistencia bit a bit.** Para una tupla de entrada fija $(E, c)$ y versión de módulo $v$, la secuencia de bytes de salida serializada es invariante ante ejecuciones repetidas en plataformas arquitectónicamente idénticas. Formalmente, $\forall t_1, t_2, H(\Pi(E, c; t_1)) = H(\Pi(E, c; t_2))$, donde $H$ denota SHA-256. Esta propiedad se verifica de forma continua por la **Puerta de Enlace de Revisión por Pares VIGÍA** durante la validación interlaboratorial.
- **Idempotencia ante re-ejecución.** Cuando un documento de hallazgos de salida se re-ingesta en la canalización mediante el **Normalizador de Evidencia VIGÍA**, el adaptador trata el documento como un nuevo artefacto y produce un meta-hallazgo que atestigua criptográficamente el hash de la ejecución previa sin mutar las conclusiones analíticas originales.
- **Conformidad normativa.** La arquitectura determinista respalda directamente la admisibilidad *Daubert* al proveer procedimientos testables y revisables por pares con cotas de error calculables (varianza no determinista nula). Asimismo, satisface los requisitos de la norma **GB/T 29360-2012** respecto de procedimientos de extracción forense reproducibles, y se alinea con los controles de Nivel 3 del **MLPS 2.0** para trazabilidad de auditorías y análisis de seguridad deterministas.

### 6. Integración con módulos VIGÍA relacionados
El módulo `131c3f89` se encuentra arquitectónicamente embebido dentro de un flujo de datos acíclico dirigido. Aguas arriba, el **Motor de Ingesta VIGÍA** realiza la validación sintáctica del manifiesto VNES y vincula anclas de procedencia criptográfica a cada $e \in \mathcal{E}$. El **Normalizador de Evidencia VIGÍA** transcodifica imágenes forenses heterogéneas, volcados de memoria y flujos de registros hacia la representación canónica VNES, asegurando que el adaptador reciba una entrada rígida de esquema. Aguas abajo, el **Generador de Informes VIGÍA** consume el `findings_array` para sintetizar narrativas de caso legibles por humanos, mientras que el **Módulo de Atestación Criptográfica VIGÍA** anexa la raíz Merkle del `determinism_proof` al libro mayor de cadena de custodia. El **Registrador de Auditoría VIGÍA** intercepta cada invocación CLI para adjuntar entradas de registro inviolables que contienen el `execution_digest`. En entornos regulados, la **Puerta de Enlace de Revisión por Pares VIGÍA** re-ejecuta el adaptador contra manifiestos de evidencia idénticos para confirmar la consistencia bit a bit, cerrando así el ciclo de validación forense.

### 7. Conclusión
El Adaptador Canónico de Canalización Forense VIGÍA (`131c3f89`) establece una base matemáticamente rigurosa y determinista para el análisis forense digital. Al codificar toda la lógica analítica dentro de funciones puras gobernadas por configuraciones validadas estáticamente y al excluir todo mecanismo de puntuación no determinista, el módulo asegura que cada hallazgo por artefacto sea reproducible, defendible y conforme a los estándares forenses nacionales e internacionales vigentes.

## РУССКИЙ

### 1. Назначение модуля и судебный контекст
Канонический адаптер судебного конвейера VIGÍA, обозначенный криптографическим хэшем `131c3f89`, представляет собой детерминированный оркестрационный слой архитектуры цифровой судебной экспертизы VIGÍA. Его основная функция заключается в строго регламентированном выполнении трёхэтапного аналитического процесса — Обнаружение ($\mathcal{D}$), Агрегация ($\mathcal{A}$) и Решение ($\Delta$) — над структурированными записями улик, потребляемыми исключительно через командный интерфейс. В отличие от традиционных судебных комплексов, полагающихся на стохастические эвристические оценки, моделирование методом Монте-Карло или недетерминированные графы логического вывода на базе машинного обучения, настоящий модуль строго исключает любые источники энтропии из аналитического пути. Результатом является чисто функциональный конвейер, формирующий побитово идентичные результаты для каждого артефакта при повторных запусках на идентичных входных данных. Такая архитектурная позиция непосредственно удовлетворяет критериям научной надёжности стандарта *Daubert* (Federal Rules of Evidence 702), а именно: тестируемости, рецензированию и известным или вычислимым коэффициентам ошибок. В экосистеме VIGÍA модуль функционирует как канонический посредник между восходящими подсистемами нормализации — **Модулем приёма данных VIGÍA** и **Судебным модулем нормализации VIGÍA** — и нисходящими потребителями: **Генератором отчётов VIGÍA**, **Криптографическим аттестационным модулем VIGÍA** и **Журналом аудита VIGÍA**. Связывая всю аналитическую логику со статическим конфигурационным документом фиксированной версии, адаптер гарантирует, что каждая выданная классификация может быть независимо воспроизведена, оспорена и верифицирована сторонними лабораториями, что является критически важным требованием в рамках GB/T 29360-2012 и требований аудита уровня 3 MLPS 2.0.

### 2. Математические основы
Модуль формализован в виде полной детерминированной функции над дискретными пространствами улик и конфигураций. Пусть $\mathcal{E}$ обозначает пространство структурированных записей улик, где каждая запись $e \in \mathcal{E}$ представляет собой упорядоченный кортеж $e = (a, m, b)$. Здесь $a \in \mathcal{A}$ — идентификатор артефакта из глобально уникального пространства имён, $m \in \mathcal{M}$ — блок метаданных происхождения конечной длины, а $b \in \{0,1\}^{256}$ — криптографический дайджест последовательности байтов артефакта (SHA-256). Пусть $\mathcal{C}$ — пространство конфигураций, где каждая $c \in \mathcal{C}$ статически валидируется по формальной схеме для предотвращения неопределённых ссылок на правила или циклических отношений предшествования. Пусть $\mathcal{F}$ — пространство результатов. Судебный конвейер определяется как композиция функций:

$$\Pi: \mathcal{E} \times \mathcal{C} \to \mathcal{F}, \quad \Pi(e, c) = (\Delta \circ \mathcal{A} \circ \mathcal{D})(e, c)$$

Три трансформационных этапа строго характеризуются следующим образом:

- **Обнаружение.** $\mathcal{D}: \mathcal{E} \times \mathcal{C} \to 2^{\mathcal{P}}$ отображает запись улик и связанную с ней конфигурацию на булеан множества примитивных индикаторов $\mathcal{P}$. Каждый примитивный индикатор $p \in \mathcal{P}$ является разрешимым предикатом $p(a, m, b)$, принимающим значение $\{\text{ИСТИНА}, \text{ЛОЖЬ}\}$. Движок обнаружения вычисляет набор правил $R_c \subseteq \mathcal{C}$ в детерминированном лексикографическом порядке по идентификатору правила, обеспечивая инвариантность отображений правило–индикатор между запусками.

- **Агрегация.** $\mathcal{A}: 2^{\mathcal{P}} \times \mathcal{C} \to \mathcal{L}$ поднимает извлечённое множество индикаторов в ограниченную решётку $(\mathcal{L}, \preceq, \vee, \wedge)$. Оператор объединения $\vee$ монотонно комбинирует подтверждающие индикаторы, тогда как оператор пересечения $\wedge$ разрешает конфликты посредством строгого частичного отношения предшествования $\prec_c \, \subseteq \mathcal{P} \times \mathcal{P}$, закодированного в $c$. Если $p_1 \prec_c p_2$, то $\phi(p_1) \wedge \phi(p_2) = \phi(p_2)$, где $\phi: \mathcal{P} \to \mathcal{L}$ — каноническое вложение примитивов в атомы решётки. Решётка является полностью детерминированной; вероятностные, нечёткие или байесовские операторы не допускаются.

- **Решение.** $\Delta: \mathcal{L} \times \mathcal{C} \to \mathcal{F}$ осуществляет пороговую классификацию элемента решётки, формируя результат по артефакту $f \in \mathcal{F}$. Пороговая граница $\theta_c = (\theta_{\text{высокий}}, \theta_{\text{низкий}}) \in \mathcal{L} \times \mathcal{L}$ зависит от конфигурации, но фиксирована для данной $c$. Следовательно, $\forall e_1, e_2 \in \mathcal{E}, (e_1 = e_2) \implies \Pi(e_1, c) = \Pi(e_2, c)$, что позволяет рассматривать конвейер как функцию в строгом математическом смысле.

Дополнительный **Обработчик отрицания** $\mathcal{N}$ расширяет стадию обнаружения до $\mathcal{D}'$ путём введения комплементарных предикатов $\neg p$ из подмножества, готового к отрицанию, $\mathcal{P}_{\text{neg}}(c) \subseteq \mathcal{P}$. Данное расширение действует по принципу материального отсутствия: $\neg p$ материализуется только тогда, когда запись улик содержит контекст артефакта, в котором ожидалось бы выполнение $p$, предотвращая тем самым загрязнение множества индикаторов истинностью в пустом смысле. Формально:

$$\mathcal{D}'(e, c) = \mathcal{D}(e, c) \cup \big\{ \neg p \mid p \in \mathcal{P}_{\text{neg}}(c) \;\wedge\; \text{Контекст}(e, p) = \text{ИСТИНА} \big\}$$

### 3. Алгоритмическое описание
Поток выполнения разбивается на три строго последовательных, не имеющих внутреннего состояния преобразования, свободных от побочных эффектов.

*Стадия I — Обнаружение.* При вызове через командный интерфейс модуль разбирает обязательные и опциональные аргументы, загружает манифест улик $E = \{e_1, \dots, e_n\} \subset \mathcal{E}$ и связывает документ конфигурации $c \in \mathcal{C}$. Движок обнаружения осуществляет итерацию по каждой записи $e_i$ и вычисляет упорядоченный набор правил $R_c = \{r_1, \dots, r_k\}$. Каждое правило $r_j$ представляет собой логическое выражение первого порядка над схемой $\mathcal{E}$. Выходными данными служит индексированное семейство множеств индикаторов $\{I_1, \dots, I_n\}$, где $I_i = \{ p \in \mathcal{P} \mid \exists r \in R_c, r(e_i) \models p \}$. При активизации обработчика отрицания посредством флага `--negation-handler` движок дополнительно вычисляет двойственный набор правил $R_c^{\neg}$ для заполнения отрицанных индикаторов с учётом ограничения материального отсутствия. Временная сложность данной стадии составляет $O(|E| \cdot |R_c| \cdot L)$, где $L$ — максимальная стоимость вычисления предиката, а пространственная сложность — $O(|E| \cdot |\mathcal{P}|)$.

*Стадия II — Агрегация.* Для каждого $I_i$ агрегирующий движок вычисляет элемент решётки $l_i = \bigvee_{p \in I_i} \phi(p)$. При наличии конфликтующих индикаторов движок применяет отношение предшествования $\prec_c$ для вычисления попарных пересечений перед выполнением глобального объединения. Такой порядок гарантирует, что агрегация является ассоциативной и детерминированной, порождая единственный супремум $l_i \in \mathcal{L}$ для каждого $I_i$. Сложность составляет $O(|I_i| \cdot \log |\mathcal{L}|)$ на запись ввиду операций слияния с разрешением предшествования.

*Стадия III — Решение.* Движок решения применяет детерминированную пороговую функцию:

$$\tau(l_i, c) = \begin{cases} \text{ПОДТВЕРЖДЁННЫЙ} & \text{если } l_i \succeq \theta_{\text{высокий}} \\ \text{ПОДОЗРИТЕЛЬНЫЙ} & \text{если } \theta_{\text{низкий}} \preceq l_i \prec \theta_{\text{высокий}} \\ \text{БЕЗОПАСНЫЙ} & \text{если } l_i \prec \theta_{\text{низкий}} \end{cases}$$

Результирующий объект $f_i = (a_i, \tau_i, \mu_i)$ включает идентификатор артефакта $a_i$, тег классификации $\tau_i$ и детерминированный пакет метаданных $\mu_i$. Пакет метаданных кодирует вектор срабатываний правил $\mathbf{h}_i \in \{0,1\}^{|R_c|}$, координату решётки $\lambda(l_i) \in \mathbb{N}^d$ при фиксированной нумерации $\mathcal{L}$ и кумулятивный дайджест выполнения $d_i \in \{0,1\}^{256}$.

### 4. Спецификации входных и выходных данных
*Входные данные.* Модуль вызывается через интерфейс командной строки (CLI) со следующими параметрами:
- `--evidence-path` (обязательный): путь в файловой системе или URI к манифесту улик, соответствующему Схеме нормализованных улик VIGÍA (VNES). Манифест должен быть закодирован в UTF-8 с нормализованными окончаниями строк (LF) для предотвращения платформенно-зависимой вариативности разбора.
- `--config` (обязательный): путь к файлу конфигурации JSON или YAML, определяющему наборы правил $R_c$, спецификацию решётки $(\mathcal{L}, \preceq)$, отображение вложения $\phi$, отношение предшествования $\prec_c$ и пороговые границы $\theta$.
- `--negation-handler` (опциональный): логический флаг, при наличии которого активируется расширенное пространство обнаружения $\mathcal{D}'$.
- `--audit-anchor` (опциональный): шестнадцатеричная строка аттестации, связывающая текущее выполнение с неизменяемой записью в **Журнале аудита VIGÍA**.

*Выходные данные.* Модуль формирует единственный структурированный документ результатов, по умолчанию в каноническом JSON с отсортированными ключами и фиксированной десятичной кодировкой, устраняющей недетерминизм сериализации. Схема документа включает:
- `execution_digest`: хэш SHA-256 канонического кортежа $(c, E, \text{версия\_модуля})$.
- `findings_array`: упорядоченная последовательность объектов по артефактам. Каждый объект содержит поля `artifact_id` (строка), `classification` (перечисление: ПОДТВЕРЖДЁННЫЙ, ПОДОЗРИТЕЛЬНЫЙ, БЕЗОПАСНЫЙ), `lattice_coordinate` (массив целых чисел), `indicator_hit_vector` (битовая строка) и `timestamp_utc` (строка, полученная монотонно из аудиторского подсистемы; хотя абсолютная временная метка зависит от среды, аналитическая нагрузка строго независима от астрономического времени).
- `determinism_proof`: корень Меркле, вычисленный над индивидуальными хэшами SHA-256 каждого $f_i$, обеспечивающий проверку побитовой согласованности между запусками и лабораториями.

### 5. Детерминированные гарантии и соответствие стандартам
Модуль обеспечивает детерминированное выполнение посредством совокупности ограничений на уровне языка, алгоритма и архитектуры:
- **Чистая функциональная семантика.** Все базовые преобразования $\mathcal{D}$, $\mathcal{A}$ и $\Delta$ реализованы как чистые функции без обращения к генераторам псевдослучайных чисел, блокам аппаратной арифметики с плавающей точкой или зависящему от времени планированию потоков. Любая арифметика, требующая дробного представления, выполняется с использованием рациональных библиотек с фиксированной точкой для исключения межплатформенной вариативности IEEE-754.
- **Побитовая идентичность.** Для фиксированного входного кортежа $(E, c)$ и версии модуля $v$ выходная сериализованная последовательность байтов инвариантна при повторных запусках на архитектурно идентичных платформах. Формально, $\forall t_1, t_2, H(\Pi(E, c; t_1)) = H(\Pi(E, c; t_2))$, где $H$ обозначает SHA-256. Данное свойство непрерывно верифицируется **Шлюзом рецензирования VIGÍA** в ходе межлабораторной валидации.
- **Идемпотентность при повторном выполнении.** При повторной инжестии выходного документа результатов в конвейер через **Судебный модуль нормализации VIGÍA** модуль обрабатывает документ как новый артефакт и порождает мета-результат, криптографически засвидетельствующий хэш предыдущего запуска без мутации исходных аналитических заключений.
- **Соответствие стандартам.** Детерминированная архитектура непосредственно поддерживает допустимость по *Daubert*, обеспечивая тестируемые, подлежащие рецензированию процедуры с вычислимыми границами ошибок (нулевая недетерминированная дисперсия). Она удовлетворяет требованиям **GB/T 29360-2012** в отношении воспроизводимых процедур судебного извлечения и согласована с требованиями уровня 3 **MLPS 2.0** к аудиторской прослеживаемости и детерминированному анализу безопасности.

### 6. Интеграция со смежными модулями VIGÍA
Модуль `131c3f89` архитектурно встроен в направленный ациклический поток данных. Восходящими поставщиками являются **Модуль приёма данных VIGÍA**, осуществляющий синтаксическую валидацию манифеста VNES и криптографическую привязку происхождения к каждой $e \in \mathcal{E}$, а также **Судебный модуль нормализации VIGÍA**, выполняющий транскодирование гетерогенных судебных образов дисков, дампов памяти и потоков журналов в каноническое представление VNES, гарантируя тем самым поступление на вход адаптера схемно-жёстких данных. Нисходящими потребителями выступают **Генератор отчётов VIGÍA**, потребляющий `findings_array` для синтеза читаемых человеком повествований по делам, и **Криптографический аттестационный модуль VIGÍA**, дополняющий реестр цепочки хранения доказательств корнем Меркле из `determinism_proof`. **Журнал аудита VIGÍA** перехватывает все вызовы CLI для добавления несанкционируемых записей, содержащих `execution_digest`. В регулируемых средах **Шлюз рецензирования VIGÍA** способен повторно выполнять модуль на идентичных манифестах улик для подтверждения побитовой согласованности, замыкая таким образом цикл судебной валидации.

### 7. Заключение
Канонический адаптер судебного конвейера VIGÍA (`131c3f89`) устанавливает математически строгий, детерминированный фундамент для цифровой судебной экспертизы. Исключая недетерминированные оценки и кодируя всю аналитическую логику внутри статически валидируемых, управляемых конфигурацией чистых функций, модуль гарантирует, что каждый результат по артефакту является воспроизводимым, защищаемым и соответствующим действующим международным и национальным судебным стандартам.

## 中文

### 1. 模块目的与取证背景
VIGÍA 规范取证流水线适配器，以密码学哈希 `131c3f89` 标识，是 VIGÍA 数字取证体系结构中的确定性编排内核。其核心职能是在通过命令行接口摄取的结构化证据记录上，执行严格形式化的三阶段分析工作流：检测（$\mathcal{D}$）、聚合（$\mathcal{A}$）与判定（$\Delta$）。与传统依赖随机评分启发式、蒙特卡罗模拟或非确定性机器学习推理图的取证平台不同，本模块严格排除分析路径中的所有熵源，从而构成一个纯函数式流水线，在相同输入的重复执行下，对每个工件输出逐位一致的结论。该架构立场直接满足 *Daubert* 标准（《联邦证据规则》702）的科学可靠性要件，即可检验性、同行审查及已知或可计算的错误率。在 VIGÍA 生态系统中，本模块作为规范中介层，向上游归一化子系统——**VIGÍA 摄取引擎**与 **VIGÍA 证据归一化器**——以及下游消费端——**VIGÍA 报告生成器**、**VIGÍA 密码学证明模块**与 **VIGÍA 审计日志器**——提供衔接。通过将全部分析逻辑绑定至静态且版本固化的配置文档，本适配器确保所发出的每项分类均可由同行实验室独立复现、质疑与验证；该能力在 GB/T 29360-2012《电子数据取证检验技术》及 MLPS 2.0 第三级审计要求下日益关键。

### 2. 数学基础
本模块被形式化为离散证据空间与配置空间上的全确定性函数。设 $\mathcal{E}$ 为结构化证据记录空间，其中每条记录 $e \in \mathcal{E}$ 为一个有序元组 $e = (a, m, b)$：$a \in \mathcal{A}$ 为取自全局唯一命名空间的工件标识符；$m \in \mathcal{M}$ 为有限长度来源元数据块；$b \in \{0,1\}^{256}$ 为工件字节序列的密码学摘要（SHA-256）。设 $\mathcal{C}$ 为配置空间，其中每个 $c \in \mathcal{C}$ 在执行前均经形式化模式静态验证，以杜绝未定义规则引用或循环优先关系。设 $\mathcal{F}$ 为结论空间。取证流水线定义为如下函数复合：

$$\Pi: \mathcal{E} \times \mathcal{C} \to \mathcal{F}, \quad \Pi(e, c) = (\Delta \circ \mathcal{A} \circ \mathcal{D})(e, c)$$

三个变换阶段严格刻画如下：

- **检测。** $\mathcal{D}: \mathcal{E} \times \mathcal{C} \to 2^{\mathcal{P}}$ 将证据记录及其激活配置映射至原始指标集合 $\mathcal{P}$ 的幂集。每个原始指标 $p \in \mathcal{P}$ 为可判定谓词 $p(a, m, b)$，取值为 $\{\text{真}, \text{假}\}$。检测引擎以规则标识符为键，按确定性字典序求值规则集 $R_c \subseteq \mathcal{C}$，确保规则到指标的映射在执行间保持不变。

- **聚合。** $\mathcal{A}: 2^{\mathcal{P}} \times \mathcal{C} \to \mathcal{L}$ 将提取的指标集提升到有界格 $(\mathcal{L}, \preceq, \vee, \wedge)$。并运算 $\vee$ 单调地组合佐证指标，交运算 $\wedge$ 则依据编码于 $c$ 中的严格偏序优先关系 $\prec_c \, \subseteq \mathcal{P} \times \mathcal{P}$ 解决冲突。若 $p_1 \prec_c p_2$，则 $\phi(p_1) \wedge \phi(p_2) = \phi(p_2)$，其中 $\phi: \mathcal{P} \to \mathcal{L}$ 为原始指标到格原子的标准嵌入映射。该格完全确定，不允许概率、模糊或贝叶斯算子。

- **判定。** $\Delta: \mathcal{L} \times \mathcal{C} \to \mathcal{F}$ 对聚合后的格元素执行基于阈值的分类，输出单工件结论 $f \in \mathcal{F}$。判定边界 $\theta_c = (\theta_{\text{高}}, \theta_{\text{低}}) \in \mathcal{L} \times \mathcal{L}$ 依赖于配置，但对给定 $c$ 固定不变，从而保证 $\forall e_1, e_2 \in \mathcal{E}, (e_1 = e_2) \implies \Pi(e_1, c) = \Pi(e_2, c)$，使流水线在严格数学意义上成为一个函数。

可选的**否定处理器** $\mathcal{N}$ 通过引入取自否定就绪子集 $\mathcal{P}_{\text{neg}}(c) \subseteq \mathcal{P}$ 的互补谓词 $\neg p$，将检测阶段扩展为 $\mathcal{D}'$。该扩展基于"实质缺失"原则运作：仅当证据记录包含期望出现 $p$ 的工件上下文时，$\neg p$ 才被实例化，从而防止空虚真值污染指标集。形式化表达为：

$$\mathcal{D}'(e, c) = \mathcal{D}(e, c) \cup \big\{ \neg p \mid p \in \mathcal{P}_{\text{neg}}(c) \;\wedge\; \text{上下文}(e, p) = \text{真} \big\}$$

### 3. 算法描述
执行流被划分为三个严格串行、无状态、无副作用的变换。

*阶段 I：检测。* 经命令行调用后，模块解析必选与可选参数，加载证据清单 $E = \{e_1, \dots, e_n\} \subset \mathcal{E}$，并绑定配置文档 $c \in \mathcal{C}$。检测引擎逐条迭代记录 $e_i$，并求值有序规则集 $R_c = \{r_1, \dots, r_k\}$。每条规则 $r_j$ 为基于 $\mathcal{E}$ 模式的一阶逻辑表达式。输出为指标集族 $\{I_1, \dots, I_n\}$，其中 $I_i = \{ p \in \mathcal{P} \mid \exists r \in R_c, r(e_i) \models p \}$。若通过 `--negation-handler` 标志启用否定处理器，引擎在实质缺失约束下额外求值对偶规则集 $R_c^{\neg}$，以填充否定指标。本阶段时间复杂度为 $O(|E| \cdot |R_c| \cdot L)$，其中 $L$ 为谓词求值的最大代价；空间复杂度为 $O(|E| \cdot |\mathcal{P}|)$。

*阶段 II：聚合。* 对每个指标集 $I_i$，聚合引擎计算格元素 $l_i = \bigvee_{p \in I_i} \phi(p)$。若存在冲突指标，引擎先应用优先关系 $\prec_c$ 计算成对交，再执行全局并。该调度保证聚合具有结合性与确定性，为每个 $I_i$ 生成唯一上确界 $l_i \in \mathcal{L}$。受优先关系消解的合并操作影响，单条记录复杂度为 $O(|I_i| \cdot \log |\mathcal{L}|)$。

*阶段 III：判定。* 判定引擎应用确定性阈值函数：

$$\tau(l_i, c) = \begin{cases} \text{确认} & \text{若 } l_i \succeq \theta_{\text{高}} \\ \text{可疑} & \text{若 } \theta_{\text{低}} \preceq l_i \prec \theta_{\text{高}} \\ \text{无害} & \text{若 } l_i \prec \theta_{\text{低}} \end{cases}$$

所得结论 $f_i = (a_i, \tau_i, \mu_i)$ 包含工件标识符 $a_i$、分类标签 $\tau_i$ 及确定性元数据包 $\mu_i$。元数据包编码规则命中向量 $\mathbf{h}_i \in \{0,1\}^{|R_c|}$、在 $\mathcal{L}$ 固定枚举下的格坐标 $\lambda(l_i) \in \mathbb{N}^d$，以及累积执行摘要 $d_i \in \{0,1\}^{256}$。

### 4. 输入/输出规约
*输入。* 本模块通过命令行接口（CLI）调用，接受以下参数：
- `--evidence-path`（必选）：指向符合 VIGÍA 归一化证据模式（VNES）之证据清单的文件系统路径或 URI。清单须以 UTF-8 编码并使用规范化换行符（LF），以防平台相关解析差异。
- `--config`（必选）：JSON 或 YAML 配置文件路径，内含规则集 $R_c$、格规约 $(\mathcal{L}, \preceq)$、嵌入映射 $\phi$、优先关系 $\prec_c$ 及阈值边界 $\theta$ 的定义。
- `--negation-handler`（可选）：布尔标志，启用时激活扩展检测空间 $\mathcal{D}'$。
- `--audit-anchor`（可选）：十六进制证明字符串，将本次执行与 **VIGÍA 审计日志器**中的不可变条目相关联。

*输出。* 模块输出单一结构化结论文档，默认为按键排序且采用定点十进制编码的规范 JSON，以消除序列化非确定性。文档模式包含：
- `execution_digest`：规范元组 $(c, E, \text{module\_version})$ 的 SHA-256 哈希值。
- `findings_array`：单工件对象的有序序列。每个对象包含字段 `artifact_id`（字符串）、`classification`（枚举：确认、可疑、无害）、`lattice_coordinate`（整数数组）、`indicator_hit_vector`（位串）及 `timestamp_utc`（字符串，取自审计子系统的单调时钟；绝对时间戳虽受环境约束，但分析载荷与墙钟时间严格无关）。
- `determinism_proof`：基于各 $f_i$ 的独立 SHA-256 哈希计算的 Merkle 根，用于跨执行、跨实验室的逐位一致性校验。

### 5. 确定性保证与合规性
本模块通过语言级、算法级与架构级约束的交汇，强制实现确定性执行：
- **纯函数语义。** 核心变换 $\mathcal{D}$、$\mathcal{A}$ 与 $\Delta$ 均实现为纯函数，不引用伪随机数生成器、硬件浮点单元或依赖并发线程调度时序。凡涉及分数表示的运算，一律采用定点有理数库完成，以规避 IEEE-754 跨平台差异。
- **逐位一致性。** 对任意固定输入元组 $(E, c)$ 及模块版本 $v$，在架构相同平台上重复执行时，序列化输出字节序列保持不变。形式化表达为 $\forall t_1, t_2, H(\Pi(E, c; t_1)) = H(\Pi(E, c; t_2))$，其中 $H$ 表示 SHA-256。**VIGÍA 同行审查网关**在跨实验室验证期间对该属性进行持续校验。
- **重执行幂等性。** 当输出结论文档通过 **VIGÍA 证据归一化器**重新作为证据摄取时，本模块将该文档视为新工件，生成元结论，以密码学方式证明先前执行哈希，而不改变原始分析结论。
- **标准合规。** 确定性架构直接支撑 *Daubert* 标准关于科学证据可采性的要求，提供可检验、可同行审查且误差界可计算（非确定性方差为零）的程序。其符合 **GB/T 29360-2012** 关于可复现取证提取的规定，并满足 **MLPS 2.0**（网络安全等级保护制度 2.0）第三级对审计可追溯性与确定性安全分析的控制要求。

### 6. 与相关 VIGÍA 模块的集成
`131c3f89` 模块架构上嵌入于一个有向无环数据流。上游方面，**VIGÍA 摄取引擎**负责 VNES 清单的语法验证，并为每个 $e \in \mathcal{E}$ 绑定密码学来源锚点；**VIGÍA 证据归一化器**将异构取证磁盘镜像、内存转储与日志流转码为规范 VNES 表示，确保适配器接收模式严格的输入。下游方面，**VIGÍA 报告生成器**消费 `findings_array` 以合成人类可读的案件叙述；**VIGÍA 密码学证明模块**将 `determinism_proof` 的 Merkle 根追加至保管链账本。**VIGÍA 审计日志器**拦截所有 CLI 调用，附加包含 `execution_digest` 的防篡改日志条目。在受监管环境中，**VIGÍA 同行审查网关**可在相同证据清单上重新执行本模块，以确认逐位一致性，从而闭合取证验证回路。

### 7. 结论
VIGÍA 规范取证流水线适配器（`131c3f89`）为数字取证分析建立了数学上严格、确定性的基础。通过