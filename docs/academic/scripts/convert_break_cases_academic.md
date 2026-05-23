---
doc_hash: 28c684d0
module: scripts/convert_break_cases.py
languages: [EN, ES, RU]
generated_by: moonshot-kimi-k2.6-batch-api
license: Apache-2.0
---

## ENGLISH

**Module Designation and Functional Scope**

The `scripts/convert_break_cases.py` module constitutes a deterministic extract-transform-load (ETL) pipeline within the VIGÍA forensic architecture, specifically engineered to execute the canonical migration of legacy VIGIA_BREAK datasets into the Entity Breakdown Schema version 1 (EBS v1). Break cases, in the VIGÍA operational lexicon, represent controlled forensic experiments designed to isolate, stress-test, and quantitatively evaluate discrete capabilities of the forensic analysis engine. These capabilities span a broad operational spectrum, including but not limited to temporal coherence verification, entity resolution under adversarial noise, cryptographic hash validation, and chain-of-custody integrity assurance. The module functions as the authoritative semantic bridge between obsolete data representations—often characterized by ad-hoc identifiers, inconsistent hierarchical encodings, and deprecated capability taxonomies—and the standardized forensic ontology required by downstream analytic components. By enforcing a rule-based, non-stochastic transformation regime, the module ensures that every migrated record retains full evidentiary provenance while conforming to the strict structural and semantic constraints of the canonical schema.

**Mathematical Foundations and Formal Semantics**

Let the legacy input domain be denoted as the set $\mathcal{D}_{\text{legacy}}$, comprising tuples $\langle id_{\text{old}}, \mathbf{m}_{\text{meta}}, \mathbf{c}_{\text{cap}}, \mathbf{h}_{\text{struct}} \rangle$, where $id_{\text{old}}$ represents obsolete identifiers drawn from the legacy namespace $\mathcal{I}_{\text{legacy}}$, $\mathbf{m}_{\text{meta}}$ the metadata envelope encoding ingestion provenance and source-system lineage, $\mathbf{c}_{\text{cap}}$ the capability descriptor vector enumerating the specific forensic faculties under evaluation, and $\mathbf{h}_{\text{struct}}$ the legacy hierarchical encoding representing evidential containment or provenance relationships. The canonical output domain is $\mathcal{D}_{\text{ebs}}$, with tuples $\langle id_{\text{new}}, \mathbf{m}_{\text{ebs}}, \mathbf{s}_{\text{score}}, \mathbf{g}_{\text{graph}} \rangle$ conforming strictly to the EBS v1 schema specification.

The module implements a total deterministic transformation function:

$$\mathcal{T}: \mathcal{D}_{\text{legacy}} \rightarrow \mathcal{D}_{\text{ebs}}$$

such that for any input instance $x \in \mathcal{D}_{\text{legacy}}$, the output $y = \mathcal{T}(x)$ is unique and invariant across executions. This determinism is formally expressed as:

$$\forall x \in \mathcal{D}_{\text{legacy}}, \forall t_1, t_2 \in \mathbb{R}^+, \quad \mathcal{T}_{t_1}(x) = \mathcal{T}_{t_2}(x)$$

where $t_1$ and $t_2$ denote distinct execution timestamps. Identifier canonicalization is modeled as an injective mapping:

$$f_{\text{id}}: \mathcal{I}_{\text{legacy}} \hookrightarrow \mathcal{I}_{\text{ebs}}$$

where $\mathcal{I}_{\text{ebs}}$ is the canonical identifier space. The injectivity constraint ensures that no two distinct legacy identifiers collide within the canonical namespace, preserving evidential distinctiveness and preventing the aliasing of disparate forensic entities. Furthermore, $f_{\text{id}}$ is defined as a pure function with no dependence on external state or pseudo-random generators.

Capability scoring is defined by the bounded rational function:

$$s: \mathcal{C} \rightarrow [0, 1] \cap \mathbb{Q}$$

where $\mathcal{C}$ denotes the finite set of forensic capabilities under evaluation, and $s(c_i)$ yields a rational capability score quantized to the unit interval. Hierarchical enforcement is governed by a partial order $\preceq$ over the entity set $\mathcal{E}$, requiring that the output graph $\mathbf{g}_{\text{graph}}$ satisfy:

$$\forall e_i, e_j \in \mathcal{E}, \quad e_i \preceq e_j \iff \text{depth}(e_i) \leq \text{depth}(e_j) \land \text{ancestor}(e_i, e_j)$$

This partial order guarantees acyclicity and semantic coherence in the provenance graph.

**Algorithmic Description**

The transformation pipeline executes through seven strictly ordered phases, each producing an intermediate artifact auditable by the VIGÍA chain-of-custody subsystem:

1. **Ingestion and Structural Validation.** The parser ingests the VIGIA_BREAK payload from the legacy ingestion layer, verifying structural integrity against the legacy schema constraints and character encoding norms (UTF-8). Malformed records, schema violations, or encoding anomalies are rejected and logged to the forensic audit stream with verbatim excerpts and failure classification codes.

2. **Cryptographic Fingerprinting.** Prior to any mutation of the input tuple, a SHA-256 digest $\delta(x)$ is computed for each $x \in \mathcal{D}_{\text{legacy}}$, establishing an immutable cryptographic reference to the pre-transformation state. This digest anchors the chain-of-custody continuity and enables bitwise integrity verification at any future point.

3. **Identifier Canonicalization.** The function $f_{\text{id}}$ maps each $id_{\text{old}}$ to a standardized UUIDv5 identifier within the EBS v1 namespace. The UUID is deterministically derived from the VIGÍA forensic namespace UUID combined with the salted legacy identifier, ensuring global uniqueness and reproducibility.

4. **Entity Resolution and Deduplication.** A transitive closure is computed over relational links embedded within $\mathbf{h}_{\text{struct}}$. Duplicate entity references are collapsed using a deterministic merge strategy that prioritizes the maximal timestamp $t_{\text{max}}$, the most complete metadata envelope, and lexicographic tie-breaking on the canonical identifier. This phase eliminates redundant subgraphs while preserving all evidentiary attributes.

5. **Capability Score Assignment.** For each capability $c_i \in \mathbf{c}_{\text{cap}}$, the module applies $s(c_i)$ based on predefined deterministic rule tables indexed by legacy capability codes. Scores are quantized to rational numbers with denominator $10^4$ to prevent floating-point indeterminacy in heterogeneous computing environments.

6. **Hierarchical Graph Construction.** The partial order $\preceq$ is materialized as a directed acyclic graph (DAG) $\mathbf{g}_{\text{graph}}$, where directed edges represent forensic provenance, evidential containment, or derived-from relationships. The DAG undergoes topological sorting to ensure that parent entities always precede child entities in the serialized output, thereby preserving semantic dependency order.

7. **Schema-Locked Serialization and Post-Transformation Attestation.** The resulting canonical tuple is serialized into EBS v1 JSON Lines or Apache Parquet format with strict schema enforcement (ISO 8601 timestamps, decimal128 for scores, UTF-8 strings). A post-transformation digest $\delta(\mathcal{T}(x))$ is computed, and both $\delta(x)$ and $\delta(\mathcal{T}(x))$ are emitted to the audit subsystem with the rule manifest version $v_r$.

**Input and Output Specifications**

*Input Artifacts:*
- **Primary Payload:** VIGIA_BREAK JSON, JSONL, or legacy XML files, mandatorily encoded in UTF-8 without byte-order mark variability.
- **Metadata Envelope:** A JSON object containing ingestion timestamps $t_{\text{ingest}}$, source system provenance URI, original case identifiers, and cryptographic checksums of the source media.
- **Rule Manifest:** A deterministic mapping table (JSON/YAML) specifying the exact interpretations of $f_{\text{id}}$, the scoring function $s$, and the partial order $\preceq$ for all known legacy variant sub-schemas.
- **Configuration Parameters:** Namespace UUID $U_{\text{ns}}$, cryptographic salt $\sigma$, output path $\omega$, and an optional lineage anchor identifier.

*Output Artifacts:*
- **Canonical Dataset:** EBS v1-compliant records in JSON Lines or Apache Parquet format, featuring strict atomic typing (ISO 8601:2019 timestamps, IEEE 754 decimal128 for capability scores, normalized Unicode strings).
- **Forensic Audit Log:** A structured, append-only log capturing $\delta(x)$, $\delta(\mathcal{T}(x))$, transformation timestamps $t_{\text{transform}}$, rule manifest version $v_r$, and the identity of the processing node.
- **Exception Report:** A machine-readable JSON manifest enumerating rejected records, including hexadecimal failure codes, verbatim malformed excerpts, and diagnostic context sufficient for peer review.

**Deterministic Guarantees and Reproducibility**

The module provides formal deterministic guarantees critical to forensic admissibility under evidentiary standards:

- **Execution Invariance:** The transformation $\mathcal{T}$ contains no stochastic operations, no dependence on system clocks for logical decisions, and no unordered iterations. All sorting, merging, and scoring decisions are governed by total order predicates derived strictly from immutable input attributes.
- **Idempotence under Canonical Form:** For any already-canonicalized record $y \in \mathcal{D}_{\text{ebs}}$ re-ingested under compatible rule manifest and salt parameters, the module guarantees that $\mathcal{T}(y) = y$, modulo non-semantic metadata timestamps.
- **Cross-Platform Reproducibility:** Quantized rational scores, UTF-8 normalized identifiers, and explicit endianness conventions eliminate platform-dependent behavior. Conforming implementations yield bit-identical outputs for identical inputs, satisfying the Daubert criterion of testability.
- **Audit Completeness and Non-Repudiation:** Every input tuple generates exactly one output tuple or one exception record; silent record dropping is architecturally impossible. The dual-digest mechanism $\langle \delta(x), \delta(\mathcal{T}(x)) \rangle$ provides non-repudiable attestation of the transformation scope.

**Integration with the VIGÍA Ecosystem**

The module interfaces directly with the following forensic subsystems:
- `engine/break_evaluator.py`: Consumes the EBS v1 output to execute capability isolation tests, compute engine performance metrics, and generate regression baselines.
- `schema/validators/ebs_v1.py`: Performs post-serialization syntactic and semantic validation, ensuring strict compliance with the canonical ontology and type system.
- `audit/chain_of_custody.py`: Receives cryptographic digests $\delta(x)$ and $\delta(\mathcal{T}(x))$ to maintain an unbroken, timestamped evidentiary chain from ingestion through transformation.
- `pipeline/ingest_legacy.py`: Supplies pre-validated legacy payloads, manages filesystem and object-store abstraction, and provides schema-version detection heuristics.
- `reports/forensic_manifest.py`: Aggregates batch-level transformation metadata—including input cardinality, exception rates, and rule versions—into court-admissible forensic manifests suitable for expert testimony.

**Compliance with Forensic and Security Standards**

The deterministic, peer-reviewable design of `scripts/convert_break_cases.py` satisfies admissibility requirements under the **Daubert Standard**, specifically addressing the factors of falsifiability, known or potential error rates, and general acceptance within the relevant scientific community. By ensuring that the transformation logic is entirely rule-based and reproducible, the module supports expert testimony regarding the integrity of migrated forensic data. With respect to Chinese national standards, the module aligns with **GB/T 29360-2012** (General Rules for Electronic Data Forensic Examination) and **GB/T 29362-2012** (Procedures for Electronic Data Recovery and Extraction) through its rigorous preservation of data integrity, provenance metadata, and transformation transparency. Furthermore, the processing pipeline adheres to **MLPS 2.0** (Multi-Level Protection Scheme 2.0, 网络安全等级保护 2.0) requirements for data processing security by maintaining cryptographic traceability, role-based access control over audit logs, and immutable retention policies throughout the transformation lifecycle.

## ESPAÑOL

**Designación del Módulo y Alcance Funcional**

Al incorporar el módulo `scripts/convert_break_cases.py` al flujo de trabajo forense, contás con una canalización ETL determinista dentro de la arquitectura VIGÍA, específicamente diseñada para ejecutar la migración canónica de conjuntos de datos heredados VIGIA_BREAK hacia el esquema Entity Breakdown Schema versión 1 (EBS v1). Los casos break, en el léxico operativo de VIGÍA, representan experimentos forenses controlados destinados a aislar, someter a prueba de estrés y evaluar cuantitativamente capacidades discretas del motor de análisis forense. Estas capacidades abarcan un espectro operativo amplio que incluye, entre otras, la verificación de coherencia temporal, la resolución de entidades bajo ruido adversarial, la validación de hashes criptográficos y el aseguramiento de la integridad de la cadena de custodia. Este módulo funciona como el puente semántico autorizado entre representaciones de datos obsoletas —frecuentemente caracterizadas por identificadores ad-hoc, codificaciones jerárquicas inconsistentes y taxonomías de capacidades deprecadas— y la ontología forense estandarizada que requieren los componentes analíticos downstream. Al imponer un régimen de transformación basado en reglas y no estocástico, el módulo garantiza que cada registro migrado conserve la proveniencia evidenciaría completa al tiempo que se ajusta a las estrictas restricciones estructurales y semánticas del esquema canónico.

**Fundamentos Matemáticos y Semántica Formal**

Debés considerar el dominio de entrada heredado como el conjunto $\mathcal{D}_{\text{legacy}}$, compuesto por tuplas $\langle id_{\text{old}}, \mathbf{m}_{\text{meta}}, \mathbf{c}_{\text{cap}}, \mathbf{h}_{\text{struct}} \rangle$, donde $id_{\text{old}}$ representa identificadores obsoletos extraídos del espacio de nombres heredado $\mathcal{I}_{\text{legacy}}$, $\mathbf{m}_{\text{meta}}$ el sobre de metadatos que codifica la proveniencia de ingesta y el linaje del sistema fuente, $\mathbf{c}_{\text{cap}}$ el vector descriptor de capacidades que enumera las facultades forenses específicas bajo evaluación, y $\mathbf{h}_{\text{struct}}$ la codificación jerárquica heredada que representa relaciones de contención o proveniencia evidenciaría. El dominio de salida canónico es $\mathcal{D}_{\text{ebs}}$, con tuplas $\langle id_{\text{new}}, \mathbf{m}_{\text{ebs}}, \mathbf{s}_{\text{score}}, \mathbf{g}_{\text{graph}} \rangle$ conformes de manera estricta a la especificación del esquema EBS v1.

El módulo implementa una función de transformación determinista total:

$$\mathcal{T}: \mathcal{D}_{\text{legacy}} \rightarrow \mathcal{D}_{\text{ebs}}$$

de modo que para cualquier instancia de entrada $x \in \mathcal{D}_{\text{legacy}}$, la salida $y = \mathcal{T}(x)$ resulta única e invariante entre ejecuciones. Formalmente, esta determinación se expresa como:

$$\forall x \in \mathcal{D}_{\text{legacy}}, \forall t_1, t_2 \in \mathbb{R}^+, \quad \mathcal{T}_{t_1}(x) = \mathcal{T}_{t_2}(x)$$

donde $t_1$ y $t_2$ denotan marcas temporales de ejecución distintas. La canonicalización de identificadores se modela como una aplicación inyectiva:

$$f_{\text{id}}: \mathcal{I}_{\text{legacy}} \hookrightarrow \mathcal{I}_{\text{ebs}}$$

donde $\mathcal{I}_{\text{ebs}}$ es el espacio de identificadores canónicos. La restricción de inyectividad te asegura que dos identificadores heredados distintos no colisionen dentro del espacio de nombres canónico, preservando la distintividad evidenciaría y evitando el aliasing de entidades forenses dispares. Asimismo, $f_{\text{id}}$ se define como una función pura sin dependencia de estado externo ni de generadores seudoaleatorios.

La puntuación de capacidades se define mediante la función racional acotada:

$$s: \mathcal{C} \rightarrow [0, 1] \cap \mathbb{Q}$$

donde $\mathcal{C}$ denota el conjunto finito de capacidades forenses bajo evaluación, y $s(c_i)$ arroja una puntuación racional cuantizada al intervalo unitario. El cumplimiento jerárquico se rige por un orden parcial $\preceq$ sobre el conjunto de entidades $\mathcal{E}$, exigiendo que el grafo de salida $\mathbf{g}_{\text{graph}}$ satisfaga:

$$\forall e_i, e_j \in \mathcal{E}, \quad e_i \preceq e_j \iff \text{profundidad}(e_i) \leq \text{profundidad}(e_j) \land \text{ancestro}(e_i, e_j)$$

Este orden parcial garantiza la aciclicidad y la coherencia semántica en el grafo de proveniencia.

**Descripción Algorítmica**

La canalización de transformación se ejecuta a través de siete fases estrictamente ordenadas, cada una de las cuales produce un artefacto intermedio auditado por el subsistema de cadena de custodia de VIGÍA:

1. **Ingesta y Validación Estructural.** El analizador ingiere la carga útil VIGIA_BREAK proveniente de la capa de ingesta heredada, verificando la integridad estructural contra las restricciones del esquema heredado y las normas de codificación de caracteres (UTF-8). Los registros malformados, las violaciones de esquema o las anomalías de codificación se rechazan y se registran en el flujo de auditoría forense con extractos textuales y códigos de clasificación de fallas.

2. **Huella Digital Criptográfica.** Previo a cualquier mutación de la tupla de entrada, se computa un resumen SHA-256 $\delta(x)$ para cada $x \in \mathcal{D}_{\text{legacy}}$, estableciendo una referencia criptográfica inmutable al estado pre-transformación. Este resumen ancla la continuidad de la cadena de custodia y habilita la verificación de integridad bit a bit en cualquier punto futuro.

3. **Canonicalización de Identificadores.** La función $f_{\text{id}}$ mapea cada $id_{\text{old}}$ hacia un identificador UUIDv5 estandarizado dentro del espacio de nombres EBS v1. El UUID se deriva de forma determinista a partir del UUID del espacio de nombres forense VIGÍA combinado con el identificador heredado salado, asegurando unicidad global y reproducibilidad.

4. **Resolución de Entidades y Deduplicación.** Se computa la clausura transitiva sobre los enlaces relacionales embebidos dentro de $\mathbf{h}_{\text{struct}}$. Las referencias de entidad duplicadas se colapsan mediante una estrategia de fusión determinista que prioriza la marca temporal máxima $t_{\text{max}}$, el sobre de metadatos más completo y el desempate lexicográfico sobre el identificador canónico. Esta fase elimina subgrafos redundantes preservando todos los atributos evidenciaríos.

5. **Asignación de Puntuaciones de Capacidad.** Para cada capacidad $c_i \in \mathbf{c}_{\text{cap}}$, el módulo aplica $s(c_i)$ basado en tablas de reglas deterministas predefinidas, indexadas por códigos de capacidad heredados. Las puntuaciones se cuantizan a números racionales con denominador $10^4$ para prevenir la indeterminación de punto flotante en entornos computacionales heterogéneos.

6. **Construcción del Grafo Jerárquico.** El orden parcial $\preceq$ se materializa como un grafo dirigido acíclico (DAG) $\mathbf{g}_{\text{graph}}$, donde las aristas dirigidas representan proveniencia forense, contención evidenciaría o relaciones derivadas. El DAG se somete a ordenamiento topológico para asegurar que las entidades padre siempre precedan a las entidades hijas en la salida serializada, preservando así el orden de dependencia semántica.

7. **Serialización Bloqueada por Esquema y Atestación Post-Transformación.** La tupla canónica resultante se serializa en formato JSON Lines o Apache Parquet EBS v1 con cumplimiento estricto del esquema (marcas temporales ISO 8601, decimal128 para puntuaciones, cadenas UTF-8). Se computa un resumen post-transformación $\delta(\mathcal{T}(x))$, y ambos resúmenes $\delta(x)$ y $\delta(\mathcal{T}(x))$ se emiten hacia el subsistema de auditoría junto con la versión del manifiesto de reglas $v_r$.

**Especificaciones de Entrada y Salida**

*Artefactos de Entrada:*
- **Carga útil primaria:** archivos VIGIA_BREAK JSON, JSONL o XML heredado, codificados obligatoriamente en UTF-8 sin variabilidad en la marca de orden de bytes.
- **Sobre de metadatos:** un objeto JSON que debés estructurar de modo que incluya marcas temporales de ingesta $t_{\text{ingest}}$, URI de proveniencia del sistema fuente, identificadores de caso originales y checksums criptográficos del medio fuente.
- **Manifiesto de reglas:** una tabla de mapeo determinista (JSON/YAML) que especifica las interpretaciones exactas de $f_{\text{id}}$, la función de puntuación $s$ y el orden parcial $\preceq$ para todos los subesquemas variantes heredados conocidos.
- **Parámetros de configuración:** UUID de espacio de nombres $U_{\text{ns}}$, valor de sal criptográfica $\sigma$, ruta de salida $\omega$ y un identificador ancla de linaje opcional.

*Artefactos de Salida:*
- **Conjunto de datos canónico:** registros conformes a EBS v1 en formato JSON Lines o Apache Parquet, con tipado atómico estricto (marcas temporales ISO 8601:2019, IEEE 754 decimal128 para puntuaciones de capacidad, cadenas Unicode normalizadas).
- **Registro de auditoría forense:** un log estructurado de solo adición que captura $\delta(x)$, $\delta(\mathcal{T}(x))$, marcas temporales de transformación $t_{\text{transform}}$, versión del manifiesto de reglas $v_r$ y la identidad del nodo de procesamiento.
- **Reporte de excepciones:** un manifiesto JSON legible por máquina que enumera los registros rechazados, incluyendo códigos de falla hexadecimales, extractos textuales de registros malformados y contexto diagnóstico suficiente para revisión por pares.

**Garantías Deterministas y Reproducibilidad**

El módulo provee garantías deterministas formales críticas para la admisibilidad forense bajo estándares evidenciaríos:

- **Invarianza de ejecución:** $\mathcal{T}$ no contiene operaciones estocásticas, no depende de relojes del sistema para decisiones lógicas ni realiza iteraciones desordenadas. Todas las decisiones de ordenamiento, fusión y puntuación se rigen por predicados de orden total derivados estrictamente de atributos de entrada inmutables.
- **Idempotencia bajo forma canónica:** para cualquier registro ya canonicalizado $y \in \mathcal{D}_{\text{ebs}}$ re-ingestado bajo parámetros de manifiesto de reglas y sal compatibles, el módulo garantiza que $\mathcal{T}(y) = y$, con la salvedad de las marcas temporales de metadatos no semánticos.
- **Reproducibilidad multiplataforma:** las puntuaciones racionales cuantizadas, los identificadores normalizados en UTF-8 y las convenciones explícitas de endianness eliminan el comportamiento dependiente de plataforma. Las implementaciones conformes producen salidas idénticas bit a bit para entradas idénticas, satisfaciendo el criterio de testabilidad del estándar Daubert.
- **Completitud de auditoría y no repudio:** cada tupla de entrada genera exactamente una tupla de salida o un registro de excepción; la omisión silenciosa de registros resulta arquitectónicamente imposible. El mecanismo de doble resumen $\langle \delta(x), \delta(\mathcal{T}(x)) \rangle$ provee una atestación no repudiable del alcance de la transformación.

**Integración con el Ecosistema VIGÍA**

El módulo interactúa directamente con los siguientes subsistemas forenses:
- `engine/break_evaluator.py`: consume la salida EBS v1 para ejecutar pruebas de aislamiento de capacidades, computar métricas de rendimiento del motor y generar líneas base de regresión.
- `schema/validators/ebs_v1.py`: realiza validación sintáctica y semántica post-serialización, asegurando el cumplimiento estricto con la ontología y el sistema de tipos canónicos.
- `audit/chain_of_custody.py`: recibe los resúmenes criptográficos $\delta(x)$ y $\delta(\mathcal{T}(x))$ para mantener una cadena evidenciaría ininterrumpida y marcada temporalmente desde la ingesta hasta la transformación.
- `pipeline/ingest_legacy.py`: suministra cargas útiles heredadas pre-validadas, gestiona la abstracción del sistema de archivos y del almacenamiento de objetos, y provee heurísticas de detección de versión de esquema.
- `reports/forensic_manifest.py`: agrega metadatos de transformación a nivel de lote —incluyendo cardinalidad de entrada, tasas de excepción y versiones de reglas— en manifiestos forenses admisibles en procedimientos judiciales y aptos para testimonio de peritos.

**Cumplimiento de Normas Forenses y de Seguridad**

El diseño determinista y susceptible de revisión por pares de `scripts/convert_break_cases.py` satisface los requisitos de admisibilidad bajo el **Estándar Daubert**, abordando específicamente los factores de falsabilidad, tasas de error conocidas o potenciales y aceptación general dentro de la comunidad científica relevante. Al asegurar que la lógica de transformación sea enteramente basada en reglas y reproducible, el módulo sustenta el testimonio de peritos respecto a la integridad de los datos forenses migrados. Con respecto a las normas nacionales de la República Popular China, el módulo se alinea con **GB/T 29360-2012** (Reglas Generales de Examinación Forense de Datos Electrónicos) y **GB/T 29362-2012** (Procedimientos de Recuperación y Extracción de Datos Electrónicos) mediante su manejo riguroso de la integridad de datos, la preservación de metadatos de proveniencia y la transparencia de la transformación. Asimismo, la canalización de procesamiento se adhiere a los requisitos de **MLPS 2.0** (Esquema de Protección Multi-Nivel 2.0, 网络安全等级保护 2.0) para la seguridad en el procesamiento de datos, al mantener trazabilidad criptográfica, control de acceso basado en roles sobre los registros de auditoría y políticas de retención inmutables a lo largo de todo el ciclo de vida de la transformación.

## РУССКИЙ

**Обозначение модуля и функциональный охват**

Модуль `scripts/convert_break_cases.py` представляет собой детерминированный конвейер ETL в составе судебно-экспертной архитектуры VIGÍA, специально разработанный для выполнения канонической миграции унаследованных наборов данных VIGIA_BREAK в схему Entity Breakdown Schema версии 1 (EBS v1). Кейсы break в оперативной терминологии VIGÍA представляют контролируемые судебно-экспертные эксперименты, предназначенные для изоляции, нагрузочного тестирования и количественной оценки дискретных возможностей судебно-экспертного аналитического движка. Указанные возможности охватывают широкий оперативный спектр, включая, помимо прочего, проверку временной когерентности, разрешение сущностей в условиях адверсариального шума, валидацию криптографических хэшей и гарантирование целостности цепочки сохранения. Данный модуль функционирует в качестве авторитетного семантического моста между устаревшими представлениями данных — зачастую характеризующимися ad-hoc идентификаторами, неконсистентными иерархическими кодировками и депрецированными таксономиями возможностей — и стандартизированной судебно-экспертной онтологией, необходимой для нисходящих аналитических компонентов. Благодаря принуждению к режиму преобразования, основанному исключительно на правилах и не содержащему стохастических компонентов, модуль гарантирует, что каждая мигрированная запись сохраняет полную доказательственную происходящую при одновременном соответствии строгим структурным и семантическим ограничениям канонической схемы.

**Математические основания и формальная семантика**

Унаследованный домен входных данных обозначим как множество $\mathcal{D}_{\text{legacy}}$, состоящее из кортежей $\langle id_{\text{old}}, \mathbf{m}_{\text{meta}}, \mathbf{c}_{\text{cap}}, \mathbf{h}_{\text{struct}} \rangle$, где $id_{\text{old}}$ представляет устаревшие идентификаторы, извлечённые из унаследованного пространства имён $\mathcal{I}_{\text{legacy}}$, $\mathbf{m}_{\text{meta}}$ — метаданный конверт, кодирующий происхождение поглощения и линейку исходной системы, $\mathbf{c}_{\text{cap}}$ — вектор-дескриптор возможностей, перечисляющий конкретные судебно-экспертные факультеты, подлежащие оценке, а $\mathbf{h}_{\text{struct}}$ — унаследованную иерархическую кодировку, представляющую отношения доказательственного включения или происхождения. Канонический домен выходных данных есть $\mathcal{D}_{\text{ebs}}$, с кортежами $\langle id_{\text{new}}, \mathbf{m}_{\text{ebs}}, \mathbf{s}_{\text{score}}, \mathbf{g}_{\text{graph}} \rangle$, соответствующими в строгом порядке спецификации схемы EBS v1.

Модуль реализует тотальную детерминированную функцию преобразования:

$$\mathcal{T}: \mathcal{D}_{\text{legacy}} \rightarrow \mathcal{D}_{\text{ebs}}$$

такую, что для любого входного экземпляра $x \in \mathcal{D}_{\text{legacy}}$ выход $y = \mathcal{T}(x)$ является единственным и инвариантным относительно исполнений. Формально данный детерминизм выражается как:

$$\forall x \in \mathcal{D}_{\text{legacy}}, \forall t_1, t_2 \in \mathbb{R}^+, \quad \mathcal{T}_{t_1}(x) = \mathcal{T}_{t_2}(x)$$

где $t_1$ и $t_2$ обозначают различные временны́е метки исполнения. Канонизация идентификаторов моделируется как инъективное отображение:

$$f_{\text{id}}: \mathcal{I}_{\text{legacy}} \hookrightarrow \mathcal{I}_{\text{ebs}}$$

где $\mathcal{I}_{\text{ebs}}$ — каноническое пространство идентификаторов. Ограничение инъективности гарантирует отсутствие коллизий двух различных унаследованных идентификаторов в каноническом пространстве имён, сохраняя доказательственную различимость и предотвращая алиасинг разрозненных судебно-экспертных сущностей. Кроме того, $f_{\text{id}}$ определяется как чистая функция без зависимости от внешнего состояния или псевдослучайных генераторов.

Назначение баллов возможностей определяется ограниченной рациональной функцией:

$$s: \mathcal{C} \rightarrow [0, 1] \cap \mathbb{Q}$$

где $\mathcal{C}$ обозначает конечное множество оцениваемых судебно-экспертных возможностей, а $s(c_i)$ даёт рациональный балл, квантованный к единичному интервалу. Иерархическое принуждение регулируется частичным порядком $\preceq$ над множеством сущностей $\mathcal{E}$, требуя, чтобы выходной граф $\mathbf{g}_{\text{graph}}$ удовлетворял:

$$\forall e_i, e_j \in \mathcal{E}, \quad e_i \preceq e_j \iff \text{depth}(e_i) \leq \text{depth}(e_j) \land \text{ancestor}(e_i, e_j)$$

Данный частичный порядок гарантирует ацикличность и семантическую когерентность в графе происхождения.

**Алгоритмическое описание**

Конвейер преобразования выполняется в семь строго упорядоченных фаз, каждая из которых производит промежуточный артефакт, подлежащий аудиту судебно-экспертной подсистемой цепочки сохранения VIGÍA:

1. **Поглощение и структурная валидация.** Парсер принимает полезную нагрузку VIGIA_BREAK из унаследованного слоя поглощения, верифицируя структурную целостность в соответствии с ограничениями унаследованной схемы и нормами кодировки символов (UTF-8). Некорректные записи, нарушения схемы или аномалии кодировки отклоняются и фиксируются в потоке судебно-экспертного аудита с дословными выдержками и кодами классификации отказов.

2. **Криптографическое фингерпринтирование.** До какой-либо мутации входного кортежа вычисляется дайджест SHA-256 $\delta(x)$ для каждого $x \in \mathcal{D}_{\text{legacy}}$, устанавливая неизменную криптографическую ссылку на предтрансформационное состояние. Данный дайджест закрепляет непрерывность цепочки сохранения и обеспечивает побитовую верификацию целостности в любой будущий момент.

3. **Канонизация идентификаторов.** Функция $f_{\text{id}}$ отображает каждый $id_{\text{old}}$ в стандартизированный идентификатор UUIDv5 внутри пространства имён EBS v1. UUID производится детерминированно из UUID судебно-экспертного пространства имён VIGÍA в комбинации с солёным унаследованным идентификатором, обеспечивая глобальную уникальность и воспроизводимость.

4. **Разрешение сущностей и дедупликация.** Вычисляется транзитивное замыкание над реляционными связями, встроенными в $\mathbf{h}_{\text{struct}}$. Дублирующиеся ссылочные записи свёртываются посредством детерминированной стратегии слияния, приоритизирующей максимальную временну́ю метку $t_{\text{max}}$, наиболее полный метаданный конверт и лексикографический тай-брейк на каноническом идентификаторе. Данная фаза устраняет избыточные подграфы при сохранении всех доказательственных атрибутов.

5. **Назначение баллов возможностей.** Для каждой возможности $c_i \in \mathbf{c}_{\text{cap}}$ модуль применяет $s(c_i)$ на основе предопределённых детерминированных таблиц правил, индексированных унаследованными кодами возможностей. Баллы квантуются до рациональных чисел со знаменателем $10^4$ для предотвращения неопределённости с плавающей точкой в гетерогенных вычислительных средах.

6. **Построение иерархического графа.** Частичный порядок $\preceq$ материализуется в виде ориентированного ациклического графа (DAG) $\mathbf{g}_{\text{graph}}$, где ориентированные рёбра представляют судебно-экспертное происхождение, доказательственное включение или отношения derived-from. DAG подвергается топологической сортировке, гарантирующей, что родительские сущности всегда предшествуют дочерним в сериализованном выводе, тем самым сохраняя порядок семантической зависимости.

7. **Сериализация с фиксацией схемы и аттестация после преобразования.** Результирующий канонический кортеж сериализуется в формат JSON Lines или Apache Parquet EBS v1 со строгим принуждением схемы (временны́е метки ISO 8601, decimal128 для баллов, строки UTF-8). Вычисляется посттрансформационный дайджест $\delta(\mathcal{T}(x))$, и оба дайджеста $\delta(x)$ и $\delta(\mathcal{T}(x))$ передаются в аудиторскую подсистему вместе с версией правилового манифеста $v_r$.

**Спецификации входных и выходных данных**

*Входные артефакты:*
- **Основная полезная нагрузка:** файлы VIGIA_BREAK JSON, JSONL или унаследованный XML, мандаторно закодированные в UTF-8 без вариативности метки порядка байтов.
- **Метаданный конверт:** объект JSON, содержащий временны́е метки поглощения $t_{\text{ingest}}$, URI происхождения исходной системы, оригинальные идентификаторы кейсов и криптографические контрольные суммы исходного носителя.
- **Правиловой манифест:** детерминированная таблица отображений (JSON/YAML), специфицирующая точные интерпретации $f_{\text{id}}$, функции балльной оценки $s$ и частичного порядка $\preceq$ для всех известных вариантных унаследованных подсхем.
- **Конфигурационные параметры:** UUID пространства имён $U_{\text{ns}}$, значение криптографической соли $\sigma$, путь вывода $\omega$ и опциональный идентификатор якоря линейки.

*Выходные артефакты:*
- **Канонический набор данных:** записи, соответствующие EBS v1, в формате JSON Lines или Apache Parquet со строгой атомарной типизацией (временны́е метки ISO 8601:2019, IEEE 754 decimal128 для баллов возможностей, нормализованные строки Unicode).
- **Судебно-экспертный журнал аудита:** структурированный журнал с добавлением только в конец, фиксирующий $\delta(x)$, $\delta(\mathcal{T}(x))$, временны́е метки преобразования $t_{\text{transform}}$, версию прав