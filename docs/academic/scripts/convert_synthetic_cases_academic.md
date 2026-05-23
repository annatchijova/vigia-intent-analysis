---
doc_hash: e74f0754
module: unknown
languages: [EN, ES, RU, ZH]
generated_by: moonshot-kimi-k2.6-batch-api
license: Apache-2.0
---

## ENGLISH

**Module Designation:** VIGÍA Forensic Migration Module `convert_synthetic_cases.py` (Cryptographic Hash: `e74f0754`)

**1. Module Purpose and Forensic Context**

The module `convert_synthetic_cases.py` constitutes a deterministic interoperability layer within the VIGÍA integrated digital-forensics architecture. Its primary operational mandate is to execute a lossless, bitwise-reproducible migration of synthetic forensic datasets originally instantiated under the deprecated VIGIA-SYN v1 schema into the canonical Evidentiary Batch Standard (EBS) v1 format. These synthetic cases were generated during the April production cycle via an antecedent release of the VIGÍA framework and serve as controlled evidentiary proxies for algorithmic validation, adversarial robustness testing, and calibration of the Analytical Correlation (AC) analytical pipeline. Because the legacy VIGIA-SYN v1 schema employs obsolete field ontologies, non-canonical temporal encodings, and forensic-score normalization routines that diverge semantically from contemporary AC pipeline expectations, direct ingestion of these legacy artifacts into current workflows is architecturally precluded. This module resolves the impedance mismatch by applying a mathematically specified transformation that preserves the probative integrity of the underlying synthetic artifacts while harmonizing metadata topology and recalibrating forensic scores to conform strictly to EBS v1 semantics. The conversion process is engineered to satisfy chain-of-custody requirements for synthetic evidentiary proxies, ensuring that every migrated record maintains an immutable, cryptographically verifiable link to its generative provenance and that no stochastic perturbation is introduced during transit.

Synthetic datasets occupy a privileged epistemic position in forensic science: they provide ground-truth labels for controlled experiments where naturalistic case data is unavailable or legally restricted. Consequently, any transformation applied to such data must not alter the latent forensic signal. The present module treats synthetic cases as forensic evidence *simpliciter*, applying the same rigor in integrity preservation that would be expected for naturalistic digital exhibits. This approach ensures that downstream AC pipeline inferences—whether concerned with correlation clustering, anomaly detection, or evidential weighting—operate upon a semantically stable and historically traceable data substrate.

**2. Mathematical Foundations**

Let the legacy input space be denoted by the set $\mathcal{S}$ comprising all syntactically valid VIGIA-SYN v1 records, and let the canonical output space be denoted by the set $\mathcal{E}$ comprising all valid EBS v1 entities. The conversion module implements a deterministic mapping function:

$$\Phi: \mathcal{S} \to \mathcal{E}, \quad \mathbf{e} = \Phi(\mathbf{s})$$

where $\mathbf{s} \in \mathcal{S}$ represents an individual input record and $\mathbf{e} \in \mathcal{E}$ its canonical counterpart. The function $\Phi$ is analytically decomposed into three sequential sub-mappings: structural canonicalization $\Phi_{\text{struct}}$, forensic score recalibration $\Phi_{\text{score}}$, and metadata provenance augmentation $\Phi_{\text{prov}}$, such that:

$$\Phi(\mathbf{s}) = (\Phi_{\text{prov}} \circ \Phi_{\text{score}} \circ \Phi_{\text{struct}})(\mathbf{s})$$

Structural canonicalization $\Phi_{\text{struct}}$ resolves schema incompatibilities through an injective mapping of legacy fields onto the EBS v1 relational model. Injectivity guarantees that no evidentiary field is lost, aliased, or merged ambiguously; every atomic datum in $\mathbf{s}$ has a unique image in $\mathbf{e}$ or is explicitly mapped to a null sentinel with documented semantics.

Forensic score recalibration is defined as a deterministic vector-valued affine transformation:

$$\Phi_{\text{score}}: \mathbb{R}^n \to \mathbb{R}^m, \quad \mathbf{v}_{\text{new}} = \mathbf{A}\mathbf{v}_{\text{old}} + \mathbf{b}$$

where $\mathbf{v}_{\text{old}} \in \mathbb{R}^n$ is the legacy forensic score vector, $\mathbf{A} \in \mathbb{Q}^{m \times n}$ is a rational-valued transformation matrix derived from inter-schema metrological equivalence constants, and $\mathbf{b} \in \mathbb{Q}^m$ is a deterministic bias vector encoding zero-point calibration offsets between the VIGIA-SYN v1 and EBS v1 scoring ontologies. The restriction of $\mathbf{A}$ and $\mathbf{b}$ to the rational number field $\mathbb{Q}$ guarantees that all intermediate computations remain closed under exact arithmetic, precluding the nondeterminism endemic to IEEE 754 floating-point round-off across divergent CPU architectures.

Provenance augmentation $\Phi_{\text{prov}}$ appends an immutable audit digest computed as:

$$\text{audit}(\mathbf{e}) = \text{SHA-256}\bigl(\mathbf{s} \,\|\, \text{module\_hash} \,\|\, \text{timestamp\_canonical} \,\|\, \text{schema\_version}\bigr)$$

where $\|$ denotes concatenation and the module hash is the fixed value `e74f0754`. The bitwise reproducibility condition requires that for any $\mathbf{s} \in \mathcal{S}$, the canonical serialized byte sequence $B(\Phi(\mathbf{s}))$ and its associated checksum $H(B(\Phi(\mathbf{s})))$ remain invariant across executions on homologous runtime environments.

**3. Algorithm Description**

The operational logic of `convert_synthetic_cases.py` proceeds through five strictly sequential phases, each designed to enforce deterministic constraints and evidentiary preservation mandates.

*Phase I: Ingestion and Schema Validation.* The module ingests raw VIGIA-SYN v1 artifacts, typically serialized as constrained JSON or Apache Avro streams. A deterministic recursive-descent parser validates structural conformance against the legacy schema ontology, verifying the presence and type correctness of mandatory fields: `case_id` (string, URI-safe), `generation_timestamp` (string, ISO 8601 variant), `synthetic_source_hash` (hexadecimal, 256-bit), `forensic_vector_legacy` (ordered array of numeric scalars), `metadata_bundle` (key-value dictionary with controlled vocabulary), and `confidence_interval_legacy` (closed interval tuple). Records failing validation are shunted to a quarantine log with deterministic error codes; no stochastic sampling, probabilistic filtering, or heuristic repair is applied.

*Phase II: Temporal Canonicalization.* Legacy timestamps, which may adhere to looser ISO 8601 representations or localized string formats, are parsed into monotonic UNIX epoch integers with nanosecond precision, then re-serialized into strict RFC 3339 format with explicit UTC offsets. This step eliminates locale-dependent ambiguity and ensures temporal sortability and causal ordering within the AC pipeline’s inference engines.

*Phase III: Deterministic Score Recalibration.* The forensic score vector undergoes affine transformation via the precomputed rational matrix $\mathbf{A}$ and bias vector $\mathbf{b}$. The implementation utilizes Python’s `fractions.Fraction` type during intermediate computation to circumvent floating-point rounding variance, casting to a fixed-width decimal representation (quantized to $10^{-9}$) only at final serialization. This phase explicitly excludes Monte Carlo simulation, bootstrap resampling, entropy-dependent noise injection, or any algorithmic branch dependent on system clock jitter, thereby guaranteeing that $\Phi_{\text{score}}(\mathbf{s}_1) = \Phi_{\text{score}}(\mathbf{s}_2)$ whenever $\mathbf{s}_1 = \mathbf{s}_2$.

*Phase IV: Metadata Standardization and Header Injection.* The module constructs an EBS v1 header envelope, injecting canonical identifiers: `ebs_case_uuid` is generated deterministically via UUID version 5 over the SHA-1 hash of the concatenated `case_id` and a fixed VIGÍA namespace identifier, ensuring that identical inputs always yield identical canonical identifiers. The `normalized_metadata` field is populated by mapping deprecated VIGIA-SYN ontology terms to their EBS v1 controlled-vocabulary equivalents through a static, versioned thesaurus (hash-locked at build time). The `conversion_audit_trail` field records the module hash `e74f0754`, the source schema version, and the deterministic conversion timestamp.

*Phase V: Integrity Sealing and Emission.* The completed EBS v1 entity is serialized to a byte stream using canonical JSON encoding (lexicographically sorted keys, no insignificant whitespace, UTF-8 without BOM). A SHA-256 checksum is computed over the exact serialized payload and appended as `integrity_checksum`. The output is atomically written to the downstream storage interface, and a provenance receipt containing the audit digest is emitted to the VIGÍA Provenance Ledger for chain-of-custody anchoring.

**4. Input/Output Specifications**

*Input Specification:* A VIGIA-SYN v1 record is defined as the ordered tuple:

$$\mathbf{s} = \langle \text{case\_id}, \; t_{\text{gen}}, \; h_{\text{src}}, \; \mathbf{v}_{\text{legacy}}, \; \mathbf{m}_{\text{bundle}}, \; \mathbf{c}_{\text{legacy}} \rangle$$

where $t_{\text{gen}}$ denotes the generation timestamp string, $h_{\text{src}} \in \{0,1\}^{256}$ the synthetic source hash, $\mathbf{v}_{\text{legacy}} \in \mathbb{R}^n$ the legacy forensic score vector of dimensionality $n$, $\mathbf{m}_{\text{bundle}}$ an extensible metadata dictionary constrained by the VIGIA-SYN v1 ontology, and $\mathbf{c}_{\text{legacy}} = [l, u] \subset \mathbb{R}$ the legacy confidence interval bounds.

*Output Specification:* An EBS v1 entity is defined as the ordered tuple:

$$\mathbf{e} = \langle \text{ebs\_case\_uuid}, \; t_{\text{canon}}, \; d_{\text{prov}}, \; \mathbf{v}_{\text{new}}, \; \mathbf{m}_{\text{norm}}, \; h_{\text{integ}}, \; \tau_{\text{audit}} \rangle$$

where $\text{ebs\_case\_uuid}$ is the deterministic canonical identifier, $t_{\text{canon}}$ the RFC 3339 canonical timestamp, $d_{\text{prov}}$ the provenance digest derived from the input hash and module identity, $\mathbf{v}_{\text{new}} \in \mathbb{R}^m$ the recalibrated score vector of dimensionality $m$, $\mathbf{m}_{\text{norm}}$ the normalized metadata dictionary conforming to the EBS v1 controlled vocabulary, $h_{\text{integ}}$ the SHA-256 integrity checksum of the serialized output, and $\tau_{\text{audit}}$ the conversion audit trail string.

**5. Deterministic Guarantees**

The module provides formal deterministic guarantees essential for forensic admissibility and scientific reproducibility under adversarial scrutiny.

- **Bitwise Reproducibility (Theorem 1):** For any input record $\mathbf{s} \in \mathcal{S}$, and for any two executions $\mathcal{X}_1, \mathcal{X}_2$ of the module on runtime environments with identical dependency versions, interpreter implementations (CPython ≥3.10), and architecture endianness, the output byte sequences satisfy $B(\Phi(\mathbf{s}))_{\mathcal{X}_1} = B(\Phi(\mathbf{s}))_{\mathcal{X}_2}$.

- **Idempotency under Canonical Re-conversion (Corollary 1):** If an EBS v1 output $\mathbf{e}$ is reverse-mapped to a pseudo-legacy form and re-converted under identical schema mapping versions, the resultant entity $\mathbf{e}'$ satisfies $H(\mathbf{e}) = H(\mathbf{e}')$ provided the reverse mapping preserves information content.

- **Absence of Stochastic Processes:** The algorithm contains no invocations of pseudo-random number generators, no dependence on operating-system entropy sources (`os.urandom`, `/dev/urandom`, Windows CryptoAPI), and no thread-scheduling or timing-based jitter. All control-flow branching decisions are predicate-based exclusively on input data values and static configuration hashes.

- **Rational Arithmetic Contract:** All score recalibration operations are conducted within the rational number field $\mathbb{Q}$ until final quantization, ensuring that arithmetic non-determinism is confined to a single, controlled serialization step with an explicit rounding mode (round-half-even, `decimal.ROUND_HALF_EVEN`).

**6. Related VIGÍA Modules**

The module interfaces with the following components of the VIGÍA forensic ecosystem:
- **VIGIA-SYN Generator (Module hash `a3b2c1d0`):** The upstream synthetic case generator responsible for the April batch instantiation under the legacy schema.
- **AC Analytical Pipeline (Module hash `c8d9e0f1`):** The downstream consumer requiring EBS v1 canonical inputs for correlation analysis, threat-model calibration, and evidential weighting.
- **EBS Validation Engine (Module hash `b4c5d6e7`):** A post-conversion verification module that checks schema conformance, checksum validity, and referential integrity before admission to persistent storage.
- **VIGÍA Provenance Ledger (Module hash `d2e3f4a5`):** The distributed cryptographic audit log receiving conversion receipts to establish an immutable, temporally ordered chain of custody.

**7. Standards Compliance**

The design, implementation, and operational deployment of `convert_synthetic_cases.py` adhere to the following regulatory and scientific frameworks:
- **Daubert Standard (United States):** The deterministic transformation methodology is empirically testable, subject to peer review, characterized by known error rates (the conversion failure rate is zero under schema-valid inputs), and governed by standards of forensic software reliability and maintainability.
- **GB/T 29360-2012 (*Specification for Electronic Data Forensics*) and GB/T 31500-2015 (*Information Technology—Data Vault—Data Archiving and Long-term Preservation*):** Compliance with Chinese national standards regarding data integrity verification, chain-of-custody documentation, non-repudiation of processing steps, and long-term format stability for digital evidence.
- **MLPS 2.0 (Multi-Level Protection Scheme, PRC):** The module operates within the classified data protection regime, ensuring that synthetic data migration preserves security classification tags, does not induce unauthorized declassification, and prevents cross-contamination between differentially classified security domains during format translation.

## ESPAÑOL

**Designación del módulo:** Módulo de Migración Forense VIGÍA `convert_synthetic_cases.py` (Hash criptográfico: `e74f0754`)

**1. Propósito del módulo y contexto forense**

El módulo `convert_synthetic_cases.py` constituye una capa de interoperabilidad determinística dentro de la arquitectura integrada de ciberinvestigación forense VIGÍA. Su mandato operativo principal consiste en ejecutar una migración sin pérdidas y reproducible bit a bit de conjuntos de datos forenses sintéticos originalmente instanciados bajo el esquema deprecado VIGIA-SYN v1 hacia el formato canónico Evidentiary Batch Standard (EBS) v1. Estos casos sintéticos fueron generados durante el ciclo productivo de abril mediante un lanzamiento anterior del framework VIGÍA y funcionan como proxies probatorios controlados para la validación algorítmica, el análisis de robustez adversarial y la calibración del pipeline analítico de Correlación Analítica (AC). Dado que el esquema legacy VIGIA-SYN v1 emplea ontologías de campo obsoletas, codificaciones temporales no canónicas y rutinas de normalización de puntuaciones forenses que divergen semánticamente de las expectativas actuales del pipeline AC, la ingesta directa de estos artefactos legacy en los flujos de trabajo actuales se encuentra arquitectónicamente vedada. Este módulo resuelve el desajuste de impedancia aplicando una transformación especificada matemáticamente que preserva la integridad probatoria de los artefactos sintéticos subyacentes, a la vez que armoniza la topología de los metadatos y recalibra las puntuaciones forenses para que se ajusten estrictamente a la semántica de EBS v1. El proceso de conversión está diseñado para satisfacer los requisitos de cadena de custodia propios de los proxies probatorios sintéticos, garantizando que cada registro migrado mantenga un vínculo inmutable, verificable criptográficamente, con su procedencia generativa y que no se introduzca perturbación estocástica alguna durante el tránsito.

Los conjuntos de datos sintéticos ocupan una posición epistémica privilegiada en la ciencia forense: proporcionan etiquetas de verdad fundamentada (*ground truth*) para experimentos controlados en los que los datos casuísticos naturalistas no se encuentran disponibles o se hallan restringidos legalmente. Por consiguiente, cualquier transformación aplicada a dichos datos no debe alterar la señal forense latente. El presente módulo trata los casos sintéticos como evidencia forense *simpliciter*, aplicando la misma rigurosidad en la preservación de la integridad que se esperaría para exhibiciones digitales naturalistas. Este enfoque asegura que las inferencias posteriores del pipeline AC —ya se trate de agrupamiento por correlación, detección de anomalías o ponderación evidenciaría— operen sobre un sustrato de datos semánticamente estable e históricamente rastreable.

**2. Fundamentos matemáticos**

Denominemos $\mathcal{S}$ al espacio de entrada legacy conformado por todos los registros sintácticamente válidos del esquema VIGIA-SYN v1, y $\mathcal{E}$ al espacio de salida canónico conformado por todas las entidades válidas del formato EBS v1. El módulo de conversión implementa una función de mapeo determinista:

$$\Phi: \mathcal{S} \to \mathcal{E}, \quad \mathbf{e} = \Phi(\mathbf{s})$$

donde $\mathbf{s} \in \mathcal{S}$ representa un registro de entrada individual y $\mathbf{e} \in \mathcal{E}$ su contraparte canónica. La función $\Phi$ se descompone analíticamente en tres submapeos secuenciales: la canonicalización estructural $\Phi_{\text{struct}}$, la recalibración de puntuaciones forenses $\Phi_{\text{score}}$ y el aumento de proveniencia de metadatos $\Phi_{\text{prov}}$, de modo que:

$$\Phi(\mathbf{s}) = (\Phi_{\text{prov}} \circ \Phi_{\text{score}} \circ \Phi_{\text{struct}})(\mathbf{s})$$

La canonicalización estructural $\Phi_{\text{struct}}$ resuelve las incompatibilidades de esquema a través de un mapeo inyectivo de los campos legacy hacia el modelo relacional EBS v1. La inyectividad garantiza que ningún campo probatorio se pierda, se alíase o se fusione de manera ambigua; todo dato atómico en $\mathbf{s}$ posee una imagen única en $\mathbf{e}$ o se mapea explícitamente a un valor nulo con semántica documentada.

La recalibración de puntuaciones forenses se define como una transformación afín vectorial determinista:

$$\Phi_{\text{score}}: \mathbb{R}^n \to \mathbb{R}^m, \quad \mathbf{v}_{\text{new}} = \mathbf{A}\mathbf{v}_{\text{old}} + \mathbf{b}$$

donde $\mathbf{v}_{\text{old}} \in \mathbb{R}^n$ es el vector de puntuaciones forenses legacy, $\mathbf{A} \in \mathbb{Q}^{m \times n}$ es una matriz de transformación de valores racionales derivada de constantes de equivalencia metrológica interesquemas, y $\mathbf{b} \in \mathbb{Q}^m$ es un vector de sesgo determinista que codifica los offsets de calibración de punto cero entre las ontologías de puntuación de VIGIA-SYN v1 y EBS v1. La restricción de $\mathbf{A}$ y $\mathbf{b}$ al cuerpo numérico racional $\mathbb{Q}$ garantiza que todos los cálculos intermedios permanezcan cerrados bajo aritmética exacta, evitando el indeterminismo propio del redondeo en punto flotante IEEE 754 entre arquitecturas de CPU divergentes.

El aumento de proveniencia $\Phi_{\text{prov}}$ adjunta un resumen de auditoría inmutable computado como:

$$\text{audit}(\mathbf{e}) = \text{SHA-256}\bigl(\mathbf{s} \,\|\, \text{module\_hash} \,\|\, \text{timestamp\_canonical} \,\|\, \text{schema\_version}\bigr)$$

donde $\|$ denota concatenación y el hash del módulo es el valor fijo `e74f0754`. La condición de reproducibilidad bit a bit exige que, para cualquier $\mathbf{s} \in \mathcal{S}$, la secuencia canónica de bytes serializada $B(\Phi(\mathbf{s}))$ y su checksum asociado $H(B(\Phi(\mathbf{s})))$ permanezcan invariantes entre ejecuciones sobre entornos de ejecución homólogos.

**3. Descripción del algoritmo**

La lógica operativa de `convert_synthetic_cases.py` se desarrolla en cinco fases estrictamente secuenciales, cada una diseñada para hacer cumplir las restricciones deterministas y los mandatos de preservación probatoria.

*Fase I: Ingesta y validación de esquema.* El módulo ingiere artefactos crudos VIGIA-SYN v1, típicamente serializados como flujos JSON restringidos o Apache Avro. Un analizador sintáctico determinista de descenso recursivo valida la conformidad estructural contra la ontología del esquema legacy, verificando la presencia y la corrección tipológica de los campos obligatorios: `case_id` (cadena, URI-safe), `generation_timestamp` (cadena, variante ISO 8601), `synthetic_source_hash` (hexadecimal, 256 bits), `forensic_vector_legacy` (arreglo ordenado de escalares numéricos), `metadata_bundle` (diccionario clave-valor con vocabulario controlado) y `confidence_interval_legacy` (tupla de intervalo cerrado). Los registros que fallan la validación se desvían hacia un registro de cuarentena con códigos de error deterministas; no se aplica muestreo estocástico, filtrado probabilístico ni reparación heurística.

*Fase II: Canonicalización temporal.* Las marcas temporales legacy, que pueden adherirse a representaciones ISO 8601 más permisivas o a formatos de cadena localizados, se analizan sintácticamente en enteros de época UNIX monótonos con precisión de nanosegundos y luego se reserializan en formato estricto RFC 3339 con desplazamientos UTC explícitos. Este paso elimina la ambigüedad dependiente de la localización y asegura la ordenabilidad temporal y el ordenamiento causal dentro de los motores de inferencia del pipeline AC.

*Fase III: Recalibración determinista de puntuaciones.* El vector de puntuaciones forenses se somete a transformación afín mediante la matriz racional precomputada $\mathbf{A}$ y el vector de sesgo $\mathbf{b}$. La implementación utiliza el tipo `fractions.Fraction` de Python durante la computación intermedia para eludir la varianza de redondeo en punto flotante, realizando la conversión a una representación decimal de ancho fijo (cuantizada a $10^{-9}$) únicamente en la serialización final. Esta fase excluye explícitamente la simulación de Monte Carlo, el remuestreo bootstrap, la inyección de ruido dependiente de entropía o cualquier rama algorítmica que dependa de la fluctuación del reloj del sistema, garantizando así que $\Phi_{\text{score}}(\mathbf{s}_1) = \Phi_{\text{score}}(\mathbf{s}_2)$ siempre que $\mathbf{s}_1 = \mathbf{s}_2$.

*Fase IV: Estandarización de metadatos e inyección de encabezado.* El módulo construye un sobre de encabezado EBS v1, inyectando identificadores canónicos: el campo `ebs_case_uuid` se genera de manera determinista mediante UUID versión 5 sobre el hash SHA-1 de la concatenación del `case_id` y un identificador de namespace VIGÍA fijo, asegurando que entradas idénticas siempre produzcan identificadores canónicos idénticos. El campo `normalized_metadata` se completa mapeando términos ontológicos deprecados de VIGIA-SYN a sus equivalentes de vocabulario controlado de EBS v1 a través de un tesauro estático, bloqueado por hash en tiempo de compilación. El campo `conversion_audit_trail` registra el hash del módulo `e74f0754`, la versión del esquema fuente y la marca temporal determinista de conversión.

*Fase V: Sellado de integridad y emisión.* La entidad EBS v1 completada se serializa a un flujo de bytes utilizando codificación JSON canónica (claves ordenadas lexicográficamente, sin espacios en blanco insignificantes, UTF-8 sin BOM). Se computa un checksum SHA-256 sobre la carga útil serializada exacta y se adjunta como `integrity_checksum`. La salida se escribe de forma atómica a la interfaz de almacenamiento downstream, y un recibo de proveniencia que contiene el resumen de auditoría se emite hacia el Registro de Procedencia VIGÍA para el anclaje de la cadena de custodia.

**4. Especificaciones de entrada/salida**

*Especificación de entrada:* Un registro VIGIA-SYN v1 se define como la tupla ordenada:

$$\mathbf{s} = \langle \text{case\_id}, \; t_{\text{gen}}, \; h_{\text{src}}, \; \mathbf{v}_{\text{legacy}}, \; \mathbf{m}_{\text{bundle}}, \; \mathbf{c}_{\text{legacy}} \rangle$$

donde $t_{\text{gen}}$ denota la cadena de marca temporal de generación, $h_{\text{src}} \in \{0,1\}^{256}$ el hash de fuente sintética, $\mathbf{v}_{\text{legacy}} \in \mathbb{R}^n$ el vector de puntuaciones forenses legacy de dimensionalidad $n$, $\mathbf{m}_{\text{bundle}}$ un diccionario de metadatos extensible restringido por la ontología VIGIA-SYN v1, y $\mathbf{c}_{\text{legacy}} = [l, u] \subset \mathbb{R}$ los límites del intervalo de confianza legacy.

*Especificación de salida:* Una entidad EBS v1 se define como la tupla ordenada:

$$\mathbf{e} = \langle \text{ebs\_case\_uuid}, \; t_{\text{canon}}, \; d_{\text{prov}}, \; \mathbf{v}_{\text{new}}, \; \mathbf{m}_{\text{norm}}, \; h_{\text{integ}}, \; \tau_{\text{audit}} \rangle$$

donde $\text{ebs\_case\_uuid}$ es el identificador canónico determinista, $t_{\text{canon}}$ la marca temporal canónica en RFC 3339, $d_{\text{prov}}$ el resumen de proveniencia derivado del hash de entrada y la identidad del módulo, $\mathbf{v}_{\text{new}} \in \mathbb{R}^m$ el vector de puntuaciones recalibrado de dimensionalidad $m$, $\mathbf{m}_{\text{norm}}$ el diccionario de metadatos normalizado conforme al vocabulario controlado EBS v1, $h_{\text{integ}}$ el checksum de integridad SHA-256 de la salida serializada, y $\tau_{\text{audit}}$ la cadena de rastro de auditoría de la conversión.

**5. Garantías deterministas**

El módulo provee garantías deterministas formales esenciales para la admisibilidad forense y la reproducibilidad científica bajo escrutinio adversarial.

- **Reproducibilidad bit a bit (Teorema 1):** Para cualquier registro de entrada $\mathbf{s} \in \mathcal{S}$, y para cualesquiera dos ejecuciones $\mathcal{X}_1, \mathcal{X}_2$ del módulo sobre entornos de ejecución con versiones idénticas de dependencias, implementaciones de intérprete (CPython ≥3.10) y endianness de arquitectura, las secuencias de bytes de salida satisfacen $B(\Phi(\mathbf{s}))_{\mathcal{X}_1} = B(\Phi(\mathbf{s}))_{\mathcal{X}_2}$.

- **Idempotencia bajo re-conversión canónica (Corolario 1):** Si una salida EBS v1 $\mathbf{e}$ se mapea inversamente a una forma pseudo-legacy y se re-convierte bajo versiones idénticas de mapeo de esquema, la entidad resultante $\mathbf{e}'$ satisface $H(\mathbf{e}) = H(\mathbf{e}')$ siempre que el mapeo inverso preserve el contenido informativo.

- **Ausencia de procesos estocásticos:** El algoritmo no contiene invocaciones a generadores de números pseudoaleatorios, no depende de fuentes de entropía del sistema operativo (`os.urandom`, `/dev/urandom`, Windows CryptoAPI) y no presenta fluctuaciones basadas en planificación de hilos ni en temporización. Todas las decisiones de bifurcación de flujo de control se basan exclusivamente en predicados sobre valores de datos de entrada y hashes de configuración estática.

- **Contrato de aritmética racional:** Todas las operaciones de recalibración de puntuaciones se ejecutan dentro del cuerpo numérico racional $\mathbb{Q}$ hasta la cuantización final, asegurando que el indeterminismo aritmético quede confinado a un único paso de serialización controlado con modo de redondeo explícito (mitad par, `decimal.ROUND_HALF_EVEN`).

**6. Módulos VIGÍA relacionados**

El módulo se interconecta con los siguientes componentes del ecosistema forense VIGÍA:
- **VIGIA-SYN Generator (Hash de módulo `a3b2c1d0`):** El generador de casos sintéticos upstream responsable de la instanciación del lote de abril bajo el esquema legacy.
- **AC Analytical Pipeline (Hash de módulo `c8d9e0f1`):** El consumidor downstream que requiere entradas canónicas EBS v1 para análisis de correlación, calibración de modelos de amenazas y ponderación evidenciaría.
- **EBS Validation Engine (Hash de módulo `b4c5d6e7`):** Un módulo de verificación post-conversión que controla la conformidad de esquema, la validez del checksum y la integridad referencial antes de la admisión al almacenamiento persistente.
- **VIGÍA Provenance Ledger (Hash de módulo `d2e3f4a5`):** El registro de auditoría criptográfico distribuido que recibe los recibos de conversión para establecer una cadena de custodia inmutable y ordenada temporalmente.

**7. Alineación normativa**

El diseño, la implementación y el despliegue operativo de `convert_synthetic_cases.py` se ajustan a los siguientes marcos regulatorios y científicos:
- **Estándar Daubert (Estados Unidos):** La metodología de transformación determinista es empíricamente comprobable, sujeta a revisión por pares, caracterizada por tasas de error conocidas (la tasa de fallo de conversión es cero bajo entradas válidas de esquema) y regida por estándares de confiabilidad y mantenibilidad del software forense.
- **GB/T 29360-2012 (*Especificación para la investigación forense de datos electrónicos*) y GB/T 31500-2015 (*Tecnología de la información—Bóveda de datos—Archivo y preservación a largo plazo*):** Alineación con las normas nacionales chinas respecto a la verificación de integridad de datos, la documentación de cadena de custodia, la no repudiación de los pasos de procesamiento y la estabilidad de formato a largo plazo para evidencia digital.
- **MLPS 2.0 (Esquema de Protección Multinivel, RPC):** El módulo opera dentro del régimen de protección de datos clasificados, asegurando que la migración de datos sintéticos preserve las etiquetas de clasificación de seguridad, no induzca declasificación no autorizada y prevenga la contaminación cruzada entre dominios de seguridad diferencialmente clasificados durante la traducción de formatos.

## РУССКИЙ

**Обозначение модуля:** Модуль судебно-экспертной миграции VIGÍA `convert_synthetic_cases.py` (Криптографический хеш: `e74f0754`)

**1. Назначение модуля и судебно-экспертный контекст**

Настоящий модуль `convert_synthetic_cases.py` представляет собой детерминированный межуровневый компонент в составе интегрированной архитектуры цифровой криминалистики VIGÍA. Его основная функциональная задача заключается в выполнении воспроизводимой побитово без потерь миграции синтетических судебно-экспертных наборов данных, первоначально инстанцированных в рамках устаревшей схемы VIGIA-SYN v1, в канонический формат Evidentiary Batch Standard (EBS) v1. Указанные синтетические кейсы были сгенерированы в апрельском производственном цикле посредством предшествующего релиза фреймворка VIGÍA и используются в качестве контролируемых доказательственных суррогатов для алгоритмической валидации, тестирования адверсариальной устойчивости и калибровки аналитического конвейера корреляционного анализа (AC). Поскольку устаревшая схема VIGIA-SYN v1 использует депрецированные онтологии полей, неканонические форматы временны́х меток и процедуры нормализации криминалистических оценок, семантически расходящиеся с современными требованиями конвейера AC, прямая инжестия унаследованных артефактов в актуальные рабочие потоки архитектурно исключена. Описываемый модуль устраняет импедансное несоответствие путём применения математически специфицированного преобразования, сохраняющего доказательственную целостность лежащих в основе синтетических артефактов, одновременно гармонизируя топологию метаданных и перекалибровывая экспертные оценки с целью строгого соответствия семантике формата EBS v1. Процесс конверсии спроектирован с учётом требований к цепочке хранения (chain-of-custody) в отношении синтетических доказательственных прокси, обеспечивая для каждой мигрированной записи сохранение неизменяемой, криптографически верифицируемой связи с порождающей провенансной информацией и гарантируя отсутствие стохастических возмущений в ходе транзита.

Синтетические наборы данных занимают привилегированную эпистемическую позицию в криминалистике: они предоставляют размеченные эталонные данные (*ground truth*) для контролируемых экспериментов в условиях, когда натуралистические казуистические данные недоступны или юридически ограничены. Следовательно, любое преобразование, применяемое к указанным данным, не должно изменять латентный криминалистический сигнал. Настоящий модуль рассматривает синтетические кейсы как цифровые доказательства *simpliciter*, применяя к их обработке такой же уровень строгости в части сохранения целостности, какой ожидается в отношении натуралистических цифровых объектов. Данный подход гарантирует, что последующие инференции конвейера AC — будь то корреляционная кластеризация, обнаружение аномалий или взвешивание доказательственной значимости — выполняются над семантически стабильным и исторически прослеживаемым данным субстратом.

**2. Математические основания**

Пусть пространство унаследованных входных данных обозначено множеством $\mathcal{S}$, включающим все синтаксически корректные записи схемы VIGIA-SYN v1, а пространство канонических выходных данных — множеством $\mathcal{E}$, включающим все допустимые сущности формата EBS v1. Модуль конверсии реализует детерминированную функцию отображения:

$$\Phi: \mathcal{S} \to \mathcal{E}, \quad \mathbf{e} = \Phi(\mathbf{s})$$

где $\mathbf{s} \in \mathcal{S}$ представляет отдельную входную запись, а $\mathbf{e} \in \mathcal{E}$ — её канонический двойник. Функция $\Phi$ аналитически декомпозирована на три последовательных подотображения: структурную каноникализацию $\Phi_{\text{struct}}$, перекалибровку криминалистической оценки $\Phi_{\text{score}}$ и дополнение провенансных метаданных $\Phi_{\text{prov}}$, так что:

$$\Phi(\mathbf{s}) = (\Phi_{\text{prov}} \circ \Phi_{\text{score}} \circ \Phi_{\text{struct}})(\mathbf{s})$$

Структурная каноникализация $\Phi_{\text{struct}}$ устраняет несовместимости схем посредством инъективного отображения унаследованных полей на реляционную модель EBS v1. Инъективность гарантирует, что ни одно экспертное поле не будет утрачено, псевдонимизировано или неоднозначно слито; каждый атомарный элемент данных в $\mathbf{s}$ обладает уникальным образом в $\mathbf{e}$ либо явно отображается на нулевой сентинел с документированной семантикой.

Перекалибровка криминалистической оценки определяется как детерминированное аффинное векторное преобразование:

$$\Phi_{\text{score}}: \mathbb{R}^n \to \mathbb{R}^m, \quad \mathbf{v}_{\text{new}} = \mathbf{A}\mathbf{v}_{\text{old}} + \mathbf{b}$$

где $\mathbf{v}_{\text{old}} \in \mathbb{R}^n$ — унаследованный вектор криминалистических оценок, $\mathbf{A} \in \mathbb{Q}^{m \times n}$ — рациональная матрица преобразования, выведенная из межсхемных метрологических констант эквивалентности, а $\mathbf{b} \in \mathbb{Q}^m$ — детерминированный вектор смещения, кодирующий нулевые калибровочные отступы между онтологиями оценивания VIGIA-SYN v1 и EBS v1. Ограничение матрицы $\mathbf{A}$ и вектора $\mathbf{b}$ полем рациональных чисел $\mathbb{Q}$ гарантирует замкнутость всех промежуточных вычислений относительно точной арифметики, предотвращая недетерминизм, присущий округлению чисел с плавающей точкой IEEE 754 на разнородных архитектурах ЦПУ.

Дополнение провенанса $\Phi_{\text{prov}}$ присоединяет неизменяемый аудиторский дайджест, вычисляемый по формуле:

$$\text{audit}(\mathbf{e}) = \text{SHA-256}\bigl(\mathbf{s} \,\|\, \text{module\_hash} \,\|\, \text{timestamp\_canonical} \,\|\, \text{schema\_version}\bigr)$$

где $\|$ обозначает конкатенацию, а хеш модуля является фиксированным значением `e74f0754`. Условие побитовой воспроизводимости требует, чтобы для любого $\mathbf{s} \in \mathcal{S}$ каноническая сериализованная байтовая последовательность $B(\Phi(\mathbf{s}))$ и ассоциированная с ней контрольная сумма $H(B(\Phi(\mathbf{s})))$ оставались инвариантными при межзапусковом выполнении в гомологичных средах исполнения.

**3. Описание алгоритма**

Операционная логика `convert_synthetic_cases.py` реализуется в виде пяти строго последовательных фаз, каждая из которых предназначена для обеспечения детерминистских ограничений и требований сохранения доказательственной целостности.

*Фаза I: Инжестия и валидация схемы.* Модуль принимает необработанные артефакты VIGIA-SYN v1, как правило сериализованные в виде ограниченных потоков JSON или Apache Avro. Детерминированный рекурсивно-спусковой парсер выполняет валидацию структурной согласованности с онтологией унаследованной схемы, проверяя наличие и корректность типов обязательных полей: `case_id` (строка, URI-safe), `generation_timestamp` (строка, вариант ISO 8601), `synthetic_source_hash` (шестнадцатеричное представление, 256 бит), `forensic_vector_legacy` (упорядоченный массив числовых скаляров), `metadata_bundle` (словарь «ключ—значение» с контролируемым словарём) и `confidence_interval_legacy` (кортеж замкнутого интервала). Записи, не прошедшие валидацию, направляются в карантинный журнал с детерминированными кодами ошибок; стохастическая выборка, вероятностная фильтрация или эвристическое восстановление не применяются.

*Фаза II: Каноникализация временны́х меток.* Унаследованные временны́е метки, которые могут соответствовать более мягким вариантам представления ISO 8601 или локализованным строковым форматам, разбираются в монотонные целочисленные значения эпохи UNIX с точностью до наносекунд, после чего ресериализуются в строгий формат RFC 3339 с явным указанием UTC-смещения. Данный этап устраняет локальную двусмысленность и обеспечивает сортировку по времени и причинно-следственное упорядочение в механизмах логического вывода конвейера AC.

*Фаза III: Детерминированная перекалибровка оценок.* Вектор криминалистических оценок подвергается аффинному преобразованию с использованием предвычисленной рациональной матрицы $\mathbf{A}$ и вектора смещения $\mathbf{b}$. Реализация использует тип `fractions.Fraction` языка Python на промежуточных этапах вычислений для устранения вариативности округления чисел с плавающей точкой; приведение к десятичному представлению фиксированной ширины (квантование до $10^{-9}$) осуществляется исключительно на финальной стадии сериализации. На данной фазе явно исключаются моделирование методом Монте-Карло, бутстреп-ресэмплинг, инъекция шума, зависящего от энтропии, а также любые алгоритмические ветвления, зависящие от джиттера системных часов, что гарантирует $\Phi_{\text{score}}(\mathbf{s}_1) = \Phi_{\text{score}}(\mathbf{s}_2)$ при $\mathbf{s}_1 = \mathbf{s}_2$.

*Фаза IV: Стандартизация метаданных и инжекция заголовка.* Модуль конструирует заголовочную обёртку EBS v1, внедряя канонические идентификаторы: поле `ebs_case_uuid` генерируется детерминированно посредством UUID версии 5 на основе хеша SHA-1 от конкатенации `case_id` и фиксированного идентификатора пространства имён VIGÍA, гарантируя, что идентичные входные данные всегда порождают идентичные канонические идентификаторы. Поле `normalized_metadata` заполняется путём отображения депрецированных онтологических терминов VIGIA-SYN на их эквиваленты из контролируемого словаря EBS v1 посредством статического тезауруса, хеширование которого фиксируется на этапе сборки. Поле `conversion_audit_trail` регистрирует хеш модуля `e74f0754`, версию исходной схемы и детерминированную временну́ю метку конверсии.

*Фаза V: Уплотнение целостности и эмиссия.* Сформированная сущность EBS v1 сериализуется в байтовый поток с использованием канонической кодировки JSON (лексикографически упорядоченные ключи, отсутствие незначащих пробелов, UTF-8 без BOM). Контрольная сумма SHA-256 вычисляется над точной сериализованной полезной нагрузкой и присоединяется в качестве значения поля `integrity_checksum`. Выходные данные атомарно записываются в downstream-интерфейс хранения, а квитанция о провенансе, содержащая аудиторский дайджест, передаётся в Реестр Провенанса VIGÍA для якорения цепочки хранения.

**4. Спецификации входных и выходных данных**

*Спецификация входных данных:* Запись VIGIA-SYN v1 определяется как упорядоченный кортеж:

$$\mathbf{s} = \langle \text{case\_id}, \; t_{\text{gen}}, \; h_{\text{src}}, \; \mathbf{v}_{\text{legacy}}, \; \mathbf{m}_{\text{bundle}}, \; \mathbf{c}_{\text{legacy}} \rangle$$

где $t_{\text{gen}}$ обозначает строку временнóй метки генерации, $h_{\text{src}} \in \{0,1\}^{256}$ — хеш синтетического источника, $\mathbf{v}_{\text{legacy}} \in \mathbb{R}^n$ — унаследованный вектор криминалистических оценок размерности $n$, $\mathbf{m}_{\text{bundle}}$ — расширяемый словарь метаданных, ограниченный онтологией VIGIA-SYN v1, а $\mathbf{c}_{\text{legacy}} = [l, u] \subset \mathbb{R}$ — границы унаследованного доверительного интервала.

*Спецификация выходных данных:* Сущность EBS v1 определяется как упорядоченный кортеж:

$$\mathbf{e} = \langle \text{ebs\_case\_uuid}, \; t_{\text{canon}}, \; d_{\text{prov}}, \; \mathbf{v}_{\text{new}}, \; \mathbf{m}_{\text{norm}}, \; h_{\text{integ}}, \; \tau_{\text{audit}} \rangle$$

где $\text{ebs\_case\_uuid}$ — детерминированный канонический идентификатор, $t_{\text{canon}}$ — каноническая временна́я метка в формате RFC 3339, $d_{\text{prov}}$ — дайджест провенанса, производный от входного хеша и идентичности модуля, $\mathbf{v}_{\text{new}} \in \mathbb{R}^m$ — перекалиброванный вектор оценок размерности $m$, $\mathbf{m}_{\text{norm}}$ — нормализованный словарь метаданных, соответствующий контролируемому словарю EBS v1, $h_{\text{integ}}$ — контрольная сумма целостности SHA-256 сериализованного выхода, а $\tau_{\text{audit}}$ — строка аудиторского следа конверсии.

**5. Детерминистские гарантии**

Модуль обеспечивает формальные детерминистские гарантии, необходимые для судебной допустимости и научной воспроизводимости при состязательном рассмотрении.

- **Побитовая воспроизводимость (Теорема 1):** Для любой входной записи $\mathbf{s} \in \mathcal{S}$ и для любых двух выполнений $\mathcal{X}_1, \mathcal{X}_2$ модуля в средах исполнения с идентичными версиями зависимостей, реализациями интерпретатора (CPython ≥3.10) и порядком байтов архитектуры выходные байтовые последовательности удовлетворяют условию $B(\Phi(\mathbf{s}))_{\mathcal{X}_1} = B(\Phi(\mathbf{s}))_{\mathcal{X}_2}$.

- **Идемпотентность при канонической повторной конверсии (Следствие 1):** Если выходная сущность EBS v1 $\mathbf{e}$ подвергается обратному отображению в псевдо-унаследованную форму и повторной конверсии при идентичных версиях схемного отображения, результирующая сущность $\mathbf{e}'$ удовлетворяет $H(\mathbf{e}) = H(\mathbf{e}')$ при условии, что обратное отображение сохраняет информационное содержание.

- **Отсутствие стохастических процессов:** Алгоритм не содержит вызовов генераторов псевдослучайных чисел, не зависит от источников энтропии операционной системы (`os.urandom`, `/dev/urandom`, Windows CryptoAPI) и не включает джиттер планирования потоков или временны́х меток. Все решения о ветвлении управляющего потока основываются исключительно на предикатах над значениями входных данных и статических хешах конфигурации.

- **Контракт рациональной арифметики:** Все операции перекалибровки оценок выполняются в поле рациональных чисел $\mathbb{Q}$ до финального квантования, гарантируя, что арифметический недетерминизм ограничен единственным контролируемым шагом сериализации с явным режимом округления (округление до ближайшего чётного, `decimal.ROUND_HALF_EVEN`).

**6. Связанные модули VIGÍA**

Модуль взаимодействует со следующими компонентами экосистемы судебно-экспертного анализа VIGÍA:
- **VIGIA-SYN Generator (Хеш модуля `a3b2c1d0`):** Выше расположенный генератор синтетических кейсов, ответственный за апрельскую инстанциацию пакета в рамках устаревшей схемы.
- **AC Analytical Pipeline (Хеш модуля `c8d9e0f1`):** Ниже расположенный потребитель, требующий канонических входных данных EBS v1 для корреляционного анализа, калибровки моделей угроз и взвешивания доказательственной значимости.
- **EBS Validation Engine (Хеш модуля `b4c5d6e7`):** Модуль пост-конверсионной верификации, выполняющий проверку схемной согласованности, валидности контрольных сумм и референциальной целостности перед допуском к постоянному хранению.
- **VIGÍA Provenance Ledger (Хеш модуля `d2e3f4a5`):** Распределённый криптографический аудиторский журнал, принимающий квитанции о конверсии для установления неизменяемой, временно́ упорядоченной цепочки хранения.

**7. Соответствие стандартам**

Проектирование, реализация и операционное развёртывание `convert_synthetic_cases.py` осуществляются в соответствии со следующими нормативными и научными рамками:
- **Стандарт Daubert (США):** Детерминированная методология преобразования является эмпирически проверяемой, подлежит рецензированию, характеризуется известными показателями ошибок (показатель отказа конверсии равен нулю при схемно-валидных входных данных) и регулируется стандартами надёжности и сопровождаемости судебного программного обеспечения.
- **GB/T 29360-2012 (*Спецификация судебно-медицинского исследования электронных данных*) и GB/T 31500-2015 (*Информационные технологии — Хранилище данных — Архивирование и долгосрочное сохранение*):** Соответствие национальным стандартам КНР в части верификации целостности данных, документирования цепочки хранения, невозможности отказа от ответственности за этапы обработки и долгосрочной стабильности форматов цифровых доказательств.
- **MLPS 2.0 (Многоуровневая система защиты, КНР):** Модуль функционирует в рамках режима защиты классифицированных данных, обеспечивая сохранение меток классификации безопасности при миграции синтетических данных, предотвращая несанкционированную деклассификацию и исключая перекрёстное загрязнение между дифференциально классифицированными доменами безопасности в ходе трансляции форматов.

## 中文

**模块标识：** VIGÍA 取证迁移模块 `convert_synthetic_cases.py`（密码学哈希：`e74f0754`）

**1. 模块目的与取证背景**

本模块 `convert_synthetic_cases.py` 是 VIGÍA 综合数字取证架构中的确定性互操作层，其核心职能是将最初以遗留架构 VIGIA-SYN v1 实例化的合成取证数据集，无损且按位可复现地迁移至规范性的证据批次标准（EBS）v1 格式。这些合成案例生成于四月份的生产周期，由 VIGÍA 框架的早期版本产出，作为受控的证据代理（evidentiary proxy），用于算法验证、对抗鲁棒性测试以及分析相关性（AC）分析流程的校准。由于遗留架构 VIGIA-SYN v1 采用已弃用的字段本体、非规范的时间编码以及语义上与当前 AC 分析流程预期不一致的取证评分归一化例程，此类遗留工件无法直接输入当代工作流。本模块通过施加数学上严格规定的转换，在保持底层合成工件证据完整性的同时，协调元数据拓扑结构，并将取证评分重新校准至严格符合 EBS v1 语义。该转换过程的设计满足合成证据代理的保管链（chain-of-custody）要求，确保每条迁移记录与其生成溯源之间保持不可篡改、可密码学验证的链接，且在迁移过程中不引入任何随机扰动。

合成数据集在取证科学中占据特殊的认识论地位：当自然案例数据不可用或受法律限制时，它们为受控实验提供了带标注的真值（ground truth）。因此，对此类数据施加的任何转换均不得改变其潜在的取证信号。本模块将合成案例视为取证证据本身（*simpliciter*），对其施加与自然数字检材同等严格的完整性保持要求。这一方法论确保下游 AC 流程的推理——无论是相关性聚类、异常检测还是证据权重计算——均运行于语义稳定、历史可追溯的数据基底之上。

**2. 数学基础**

设遗留输入空间为集合 $\mathcal{S}$，包含所有语法有效的 VIGIA-SYN v1 记录；规范输出空间为集合 $\mathcal{E}$，包含所有有效的 EBS v1 实体。本转换模块实现了一个确定性映射函数：

$$\Phi: \mathcal{S} \to \mathcal{E}, \quad \mathbf{e} = \Phi(\mathbf{s})$$

其中 $\mathbf{s} \in \mathcal{S}$ 表示单条输入记录，$\mathbf{e} \in \mathcal{E}$ 为其规范对应实体。函数 $\Phi$ 在解析上分解为三个顺序子映射：结构规范化 $\Phi_{\text{struct}}$、取证评分重校准 $\Phi_{\text{score}}$ 以及元数据溯源增强 $\Phi_{\text{prov}}$，满足：

$$\Phi(\mathbf{s}) = (\Phi_{\text{prov}} \circ \Phi_{\text{score}} \circ \Phi_{\text{struct}})(\mathbf{s})$$

结构规范化 $\Phi_{\text{struct}}$ 通过将遗留字段以单射方式映射至 EBS v1 关系模型来解决架构不兼容问题。单射性保证了无任何证据字段丢失、混淆或发生歧义合并；$\mathbf{s}$ 中的每个原子数据在 $\mathbf{e}$ 中均有唯一像，或被显式映射至具有文档化语义的空值标记。

取证评分重校准定义为确定性向量值仿射变换：

$$\Phi_{\text{score}}: \mathbb{R}^n \to \mathbb{R}^m, \quad \mathbf{v}_{\text{new}} = \mathbf{A}\mathbf{v}_{\text{old}} + \mathbf{b}$$

其中 $\mathbf{v}_{\text{old}} \in \mathbb{R}^n$ 为遗留取证评分向量，$\mathbf{A} \in \mathbb{Q}^{m \times n}$ 为基于跨架构计量等价常数导出的有理值变换矩阵，$\mathbf{b} \in \mathbb{Q}^m$ 为编码 VIGIA-SYN v1 与 EBS v1 评分本体之间零点校准偏移的确定性偏置向量。将 $\mathbf{A}$ 与 $\mathbf{b}$ 限制于有理数域 $\mathbb{Q}$，保证所有中间运算在精确算术下封闭，从而排除异构 CPU 架构上 IEEE 754 浮点舍入的非确定性。

溯源增强 $\Phi_{\text{prov}}$ 附加一个不可变的审计摘要，其计算方式为：

$$\text{audit}(\mathbf{e}) = \text{SHA-256}\bigl(\mathbf{s} \,\|\, \text{module\_hash} \,\|\, \text{timestamp\_canonical} \,\|\, \text{schema\_version}\bigr)$$

其中 $\|$ 表示拼接，模块哈希为固定值 `e74f0754`。按位可复现性条件要求：对于任意 $\mathbf{s} \in \mathcal{S}$，其规范序列化字节序列 $B(\Phi(\mathbf{s}))$ 及关联校验值 $H(B(\Phi(\mathbf{s})))$ 在同构运行环境下跨执行保持不变。

**3. 算法描述**

`convert_synthetic_cases.py` 的操作逻辑严格按照五个顺序阶段执行，每一阶段均旨在强制执行确定性约束与证据保持规范。

*阶段 I：摄取与架构验证。* 模块摄取原始 VIGIA-SYN v1 工件，通常以受限 JSON 或 Apache Avro 流序列化。确定性递归下降解析器依据遗留架构本体进行结构一致性验证，检查以下强制字段的存在性与类型正确性：`case_id`（字符串，URI 安全）、`generation_timestamp`（字符串，ISO 8601 变体）、`synthetic_source_hash`（十六进制，256 位）、`forensic_vector_legacy`（有序数值标量数组）、`metadata_bundle`（受控词表键值字典）以及 `confidence_interval_legacy`（闭区间元组）。未通过验证的记录被分流至隔离日志并赋予确定性错误码；不采用随机采样、概率过滤或启发式修复。

*阶段 II：时间规范化。* 遗留时间戳可能遵循较宽松的 ISO 8601 表示或本地化字符串格式，本阶段将其解析为具有纳秒精度的单调递增 UNIX 纪元整数，随后以带显式 UTC 偏移量的严格 RFC 3339 格式重新序列化。该步骤消除了 locale 相关歧义，并确保在 AC 流程推理引擎中具备时序可排序性与因果序关系。

*阶段 III：确定性评分重校准。* 取证评分向量通过预计算的有理矩阵 $\mathbf{A}$ 与偏置向量 $\mathbf{b}$ 接受仿射变换。实现方案在中间计算阶段采用 Python 的 `fractions.Fraction` 类型以规避浮点舍入差异，仅在最终序列化时转换为固定位宽十进制表示（量化至 $10^{-9}$）。本阶段明确排除蒙特卡洛模拟、Bootstrap 重采样、依赖熵的噪声注入，以及任何依赖系统时钟抖动的算法分支，从而保证当 $\mathbf{s}_1 = \mathbf{s}_2$ 时，必有 $\Phi_{\text{score}}(\mathbf{s}_1) = \Phi_{\text{score}}(\mathbf{s}_2)$。

*阶段 IV：元数据标准化与头部注入。* 模块构建 EBS v1 头部封套，注入规范标识符：字段 `ebs_case_uuid` 通过对 `case_id` 与固定 VIGÍA 命名空间标识符的拼接结果进行 SHA-1 哈希后，以确定性方式按 UUID 版本 5 生成，确保相同输入始终产生相同规范标识。字段 `normalized_metadata` 通过静态版本化词表（构建时以哈希锁定）将弃用的 VIGIA-SYN 本体术语映射至 EBS v1 受控词表等价项。字段 `conversion_audit_trail` 记录模块哈希 `e74f0754`、源架构版本及确定性转换时间戳。

*阶段 V：完整性封印与输出。* 完成的 EBS v1 实体以规范 JSON 编码序列化为字节流（按键字典序排序、无冗余空白、UTF-8 无 BOM）。对精确序列化载荷计算 SHA-256 校验和，并以 `integrity_checksum` 字段附加。输出以原子方式写入下游存储接口，同时向 VIGÍA 溯源账本（Provenance Ledger）发送包含审计摘要的溯源回执，以锚定保管链。

**4. 输入/输出规范**

*输入规范：* VIGIA-SYN v1 记录定义为如下有序元组：

$$\mathbf{s} = \langle \text{case\_id}, \; t_{\text{gen}}, \; h_{\text{src}}, \; \mathbf{v}_{\text{legacy}}, \; \mathbf{m}_{\text{bundle}}, \; \mathbf{c}_{\text{legacy}} \rangle$$

其中 $t_{\text{gen}}$ 为生成时间戳字符串，$h_{\text{src}} \in \{0,1\}^{256}$ 为合成源哈希，$\mathbf{v}_{\text{legacy}} \in \mathbb{R}^n$ 为 $n$ 维遗留取证评分向量，$\mathbf{m}_{\text{bundle}}$ 为受 VIGIA-SYN v1 本体约束的可扩展元数据字典，$\mathbf{c}_{\text{legacy}} = [l, u] \subset \mathbb{R}$ 为遗留置信区间边界。

*输出规范：* EBS v1 实体定义为如下有序元组：

$$\mathbf{e} = \langle \text{ebs\_case\_uuid}, \; t_{\text{canon}}, \; d_{\text{prov}}, \; \mathbf{v}_{\text{new}}, \; \mathbf{m}_{\text{norm}}, \; h_{\text{integ}}, \; \tau_{\text{audit}} \rangle$$

其中 $\text{ebs\_case\_uuid}$ 为确定性规范标识符，$t_{\text{canon}}$ 为 RFC 3339 规范时间戳，$d_{\text{prov}}$ 为派生自输入哈希与模块身份的溯源摘要，$\mathbf{v}_{\text{new}} \in \mathbb{R}^m$ 为 $m$ 维重校准评分向量，$\mathbf{m}_{\text{norm}}$ 为符合 EBS v1 受控词表的规范化元数据字典，$h_{\text{integ}}$ 为序列化输出的 SHA-256 完整性校验和，$\tau_{\text{audit}}$ 为转换审计跟踪字符串。

**5. 确定性保证**

本模块提供对抗审查环境下取证可采性与科学复现性所必需的形式化确定性保证。

- **按位可复现性（定理 1）：** 对于任意输入记录 $\mathbf{s} \in \mathcal{S}$，以及模块在具有相同依赖版本、解释器实现（CPython ≥3.10）及架构字节序的同构运行环境下的任意两次执行 $\mathcal{X}_1, \mathcal{X}_2$，其输出字节序列满足 $B(\Phi(\mathbf{s}))_{\mathcal{X}_1} = B(\Phi(\mathbf{s}))_{\mathcal{X}_2}$。

- **规范再转换下的幂等性（推论 1）：** 若 EBS v1 输出 $\mathbf{e}$ 被逆映射为伪遗留形式并在相同架构映射版本下再次转换，则所得实体 $\mathbf{e}'$ 满足 $H(\mathbf{e}) = H(\mathbf{e}')$，前提是该逆映射保持信息内容。

- **无随机过程：** 算法不包含伪随机数生成器调用，不依赖操作系统熵源（`os.urandom`、`/dev/urandom`、Windows CryptoAPI），亦不存在基于线程调度或时序的抖动。所有控制流分支决策完全基于输入数据值与静态配置哈希的谓词判定。

- **有理数算术契约：** 所有评分重校准操作在最终量化前均在有理数域 $\mathbb{Q}$ 内执行，确保算术非确定性被限制在单一受控序列化步骤中，并采用显式舍入模式（银行家舍入，即 `decimal.ROUND_HALF_EVEN`）。

**6. 关联 VIGÍA 模块**

本模块与 VIGÍA 取证生态系统中的以下组件交互：
- **VIGIA-SYN 生成器（模块哈希 `a3b2c1d0`）：** 上游合成案例生成器，负责以遗留架构生成四月批次实例。
- **AC 分析管线（模块哈希 `c8d9e0f1`）：** 下游消费者，要求输入规范 EBS v1 格式以进行相关性分析、威胁模型校准及证据权重计算。
- **EBS 验证引擎（模块哈希 `b4c5d6e7`）：** 转换后验证模块，在准入持久存储前检查架构一致性、校验和有效性及引用完整性。
- **VIGÍA 溯源账本（模块哈希 `d2e3f4a5`）：** 分布式密码学审计日志，接收转换回执以建立不可篡改、时序有序的保管链。

**7. 标准合规性**

`convert_synthetic_cases.py` 的设计、实现及运行部署符合以下法规与科学框架：
- **Daubert 标准（美国）：** 该确定性转换方法具有可检验性，经受同行评审，具备已知误差率（在架构有效输入下转换失效率为零），并受取证软件可靠性与可维护性标准约束。
- **GB/T 29360-2012《电子数据法庭科学鉴定通用方法》及 GB/T 31500-2015《信息技术 数据存储 归档与长期保存》：** 符合中国国家标准关于电子数据取证中数据完整性验证、保管链文档化、处理步骤不可抵赖性及数字证据长期格式稳定性的要求。
- **网络安全等级保护制度 2.0（MLPS 2.0，中国）：** 本模块运行于分级数据保护制度内，确保合成数据迁移过程中保持安全分类标签，不引发非授权降级，并在格式转换期间防止不同安全等级域之间的交叉污染。