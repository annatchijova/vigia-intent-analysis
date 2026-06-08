## ENGLISH

**Module Identifier:** `vigia/security/security.py`  
**Forensic Batch ID:** vigia-doc-0126-741696a1  
**Artifact UID:** 741696a1  

### What Is This Module?

The `vigia/security/security.py` module constitutes the defensive perimeter and evidentiary trust-maintenance subsystem of the VIGÍA forensic architecture. In physical terms, it operates as the digital equivalent of a forensic laboratory’s access-control desk, evidence-sealing protocol, and visitor-trust ledger. The module enforces five primary policies: (1) deterministic trust decay, ensuring that stale credentials or aged evidence lose authority through exact integer geometric reduction rather than subjective human review; (2) security auditing, producing immutable, cryptographically bound evidentiary artifacts (取证工件) suitable for courtroom presentation; (3) large language model (LLM) shielding, sanitizing inputs and outputs against adversarial manipulation via deterministic finite-state classification; (4) adaptive rate limiting, regulating request throughput with discrete token-bucket arithmetic to prevent resource exhaustion; and (5) cryptographic chain verification, guaranteeing that every audit record links to its predecessor such that any tampering produces a detectable logical fracture (逻辑断裂). All operations are engineered exclusively over the ring of integers ℤ, eliminating the non-reproducibility associated with IEEE 754 floating-point approximations and thereby satisfying the strictest reproducibility mandates of forensic science.

### Mathematical Foundations

The module rests on three exact mathematical pillars.

**1. Discrete Geometric Decay of Trust.**  
Let the trust score at epoch *t* be denoted by the integer *S*<sub>*t*</sub> ∈ [0, *S*<sub>max</sub>]. The system defines a rational decay factor *q* = *N* / *D*, where *N*, *D* ∈ ℤ<sup>+</sup>, *N* < *D*, and both are configurable integer constants (alongside module-wide constants *P* and *T*). The update rule for *k* elapsed discrete intervals is:

*S*<sub>*t*+*k*</sub> = ⌊ *S*<sub>*t*</sub> · (*N*/*D*)<sup>*k*</sup> ⌋,

computed iteratively via floor division to guarantee that every intermediate value remains an integer:

*S*<sub>*i*+1</sub> = ⌊ (*S*<sub>*i*</sub> · *N*) / *D* ⌋.

Because floor division is a total function on integers, the result is bit-exact across all CPU architectures.

**2. Integer Token-Bucket Rate Limiting.**  
Each client *c* maintains a state vector (*C*, *τ*<sub>last</sub>, *σ*), where *C* ∈ ℤ is the current token count, *τ*<sub>last</sub> ∈ ℤ is the last refill timestamp measured in integer seconds, and *σ* ∈ ℤ is the burst ceiling. The refill rate *ρ* ∈ ℤ<sup>+</sup> specifies tokens accrued per base time quantum *T*. Upon a request arriving at integer time *τ*<sub>now</sub>, the controller computes:

Δ*τ* = ⌊ (*τ*<sub>now</sub> − *τ*<sub>last</sub>) / *T* ⌋,  
*C*′ = min(*σ*, *C* + *ρ* · Δ*τ*).

If the request cost *κ* satisfies *C*′ ≥ *κ*, the operation proceeds and the state updates to (*C*′ − *κ*, *τ*<sub>now</sub>, *σ*); otherwise, a `RateLimitExceeded` exception is raised. All variables are integers; no floating-point timing is used.

**3. Cryptographic Hash Chaining for Audit Immutability.**  
Let *H* : {0,1}<sup>*</sup> → {0,1}<sup>*λ*</sup> be a collision-resistant hash function with *λ* ≥ 256. Each evidentiary record *R*<sub>*i*</sub> contains a payload digest *d*<sub>*i*</sub> and a monotonic sequence number *n*<sub>*i*</sub> ∈ ℤ<sup>+</sup>. The chain linkage is defined as:

*h*<sub>*i*</sub> = *H*(*h*<sub>*i*−1</sub> ‖ *n*<sub>*i*</sub> ‖ *d*<sub>*i*</sub>),

where ‖ denotes concatenation and *h*<sub>0</sub> is a public initialization vector. This structure forms a Merkle-Damgård-like tape; altering any *R*<sub>*i*</sub> or *h*<sub>*i*−1</sub> invalidates all subsequent digests.

### Algorithmic Description

**`TrustExponentialDecay`**  
A stateful computational object encapsulating the geometric decay model. Its principal method, `apply_decay(current_score: int, elapsed_intervals: int) -> int`, performs exactly *k* = `elapsed_intervals` iterations of the floor-multiplication update. Because *k* is bounded by the maximum epoch count (a configurable constant), the operation is O(1) amortized time. The class precomputes the rational pair (*N*, *D*) and enforces *S*<sub>max</sub> ≤ *P* to guarantee that all products fit within the platform’s integer word without overflow or modular wrap-around ambiguity.

**`SecurityAudit`**  
The evidentiary logging engine. Methods `log_block(...)`, `log_info(...)`, and `log_tool_error(...)` each emit a structured record containing: (a) the monotonic sequence number *n* incremented by exactly one; (b) the integer Unix timestamp *τ*; (c) an event-type classifier; (d) the SHA-3 digest of the payload; and (e) the predecessor hash *h*<sub>*i*−1</sub>. The records are serialized into a canonical byte order (big-endian) before hashing to ensure cross-platform determinism.

**`LLMShield`**  
A semantic sanitation layer protecting LLM subsystems from prompt injection, data exfiltration, and adversarial token manipulation. The method `scan(input_text)` decomposes the input into an integer token-ID sequence and evaluates it against a battery of deterministic finite-state automata (DFA) that encode lexical and syntactic threat signatures. The auxiliary `decorator` is a higher-order procedure that wraps arbitrary operations, enforcing `scan` pre-execution and `SecurityAudit` post-execution without modifying the wrapped routine’s source.

**`_RateLimitEntry` and `_AdaptiveRateLimiter`**  
Internal state machines tracking per-client token counts. `_RateLimitEntry` stores the integer triad (*C*, *τ*<sub>last</sub>, *σ*). `_AdaptiveRateLimiter` aggregates multiple entries and exposes `rate_limit(client_id: str, cost: int) -> bool`, which executes the integer refill-and-deduct algorithm described above. The adaptive moniker refers to the ability to reconfigure *ρ* and *σ* per client at administrative epochs, not to any non-deterministic or stochastic process.

**`enforce_worm`**  
Implements Write Once Read Many (WORM) constraints on storage backends. The procedure issues atomic append directives, returning an integer storage offset *o*<sub>*i*</sub> and a cryptographic commitment *c*<sub>*i*</sub> = *H*(*R*<sub>*i*</sub> ‖ *o*<sub>*i*</sub>). Once committed, no VIGÍA subsystem may mutate the record, satisfying physical and logical immutability.

**`verify_chain`**  
Accepts an ordered sequence of audit records and recomputes the hash linkage. For each index *i* > 0, it calculates *h*<sub>*i*</sub>′ = *H*(*h*<sub>*i*−1</sub> ‖ canonical(*R*<sub>*i*</sub>)) and asserts equality with the stored *h*<sub>*i*</sub>. It returns a boolean integrity flag and, upon failure, the exact index of the first logical fracture.

**`scan`**  
A periodic integrity verification routine invoked by the VIGÍA scheduler. It audits the current state of all rate-limit buckets, trust scores, and pending LLMShield quarantines, emitting a consolidated deterministic report.

### Input/Output Specifications

| Procedure | Input Domain | Output Domain | Preconditions | Postconditions |
|---|---|---|---|---|
| `apply_decay` | *S* ∈ ℤ, 0 ≤ *S* ≤ *S*<sub>max</sub>; *k* ∈ ℤ<sup>+</sup> | *S*′ ∈ ℤ, 0 ≤ *S*′ ≤ *S* | *N*, *D*, *S*<sub>max</sub> configured | *S*′ = ⌊*S*·(*N*/*D*)<sup>*k*</sup>⌋ via exact integer steps |
| `rate_limit` | `client_id` ∈ Σ<sup>*</sup>; *κ* ∈ ℤ<sup>+</sup> | boolean or `RateLimitExceeded` | *σ*, *ρ*, *T* configured | If True, state decremented by *κ*; else exception |
| `log_block` / `log_info` / `log_tool_error` | Event payload ∈ byte sequence *B*<sup>*</sup> | Record ID *n* ∈ ℤ<sup>+</sup> | Audit context initialized | *n*<sub>*i*+1</sub> = *n*<sub>*i*</sub> + 1; chain extended |
| `verify_chain` | Ordered list of records ℛ | (*integrity*: bool, *fracture_idx*: ℤ) | ℛ non-empty | True iff ∀*i*, *h*<sub>*i*</sub>′ = *h*<sub>*i*</sub> |
| `enforce_worm` | Canonical record *R* ∈ *B*<sup>*</sup> | (*offset*: ℤ, *commitment*: *B*<sup>*λ*</sup>) | Storage backend writable | Record appended and sealed |
| `scan` | LLM input text ∈ UTF-8 | (*clean*: bool, *threat_vector*: ℤ<sup>*</sup>) | `LLMShield` vocabulary loaded | Deterministic classification |

### Deterministic Guarantees

1. **Bit-Exact Reproducibility:** All arithmetic operations are confined to ℤ. Division is exclusively floor division of integers. Consequently, every algorithm yields bitwise identical outputs across x86_64, ARM64, and RISC-V architectures, satisfying forensic reproducibility criteria.
2. **Temporal Monotonicity:** The module asserts that every observed integer timestamp *τ*<sub>*i*+1</sub> ≥ *τ*<sub>*i*</sub>. A violation raises a logical fracture exception, preventing time-replay attacks.
3. **Audit Non-Repudiation:** Each evidentiary artifact binds the monotonic sequence number *n*<sub>*i*</sub>, the payload digest, and the predecessor hash *h*<sub>*i*−1</sub>. This triad forms a self-authenticating object that cannot be repudiated without breaking the hash function.
4. **Rate-Limit Monotonicity:** For any client, the cumulative admitted request count over interval [0, *t*] is bounded above by *σ* + *ρ*·⌈*t*/*T*⌉ and is non-decreasing. Rejection decisions are Markovian: they depend only on the current integer state vector, not on execution history.
5. **Idempotent Decay:** `apply_decay`(*S*, 0) = *S* for all valid *S*. Reapplying decay over zero elapsed intervals does not alter the trust score.

### Standards Compliance

- **Daubert Standard (U.S. Federal Rules of Evidence 702):** The module’s published integer algorithms, deterministic update rules, and use of standard hash primitives provide a known and empirically measurable error rate (effectively zero for arithmetic, bounded by collision probability for hashing). This satisfies the “reproducibility” and “general acceptance” prongs required for expert testimony.
- **GB/T 29360-2012** (*Electronic Data Forensics—Common Programs*): `enforce_worm` and `verify_chain` implement the standard’s mandates for original evidence write-protection and chain-of-custody verification.
- **MLPS 2.0 / GB/T 22239-2019** (*Information Security Technology—Baseline for Classified Protection of Cybersecurity*): The access-control granularity of `_AdaptiveRateLimiter`, the audit trail density of `SecurityAudit`, and the intrusion-prevention semantics of `LLMShield` collectively satisfy the security computing environment and security management center requirements for Level 3 (Supervised Protection) and Level 4 (Mandatory Protection) deployments.

### Key Concepts

| Concept | Description | Formal Representation |
|---|---|---|
| Discrete Trust Decay | Exact integer reduction of trust scores over epochs | *S*<sub>*t*+*k*</sub> = ⌊*S*<sub>*t*</sub>·(*N*/*D*)<sup>*k*</sup>⌋ |
| Adaptive Rate Limit | Token-bucket regulation using integer time quanta | *C*′ = min(*σ*, *C* + *ρ*·Δ*τ*) − *κ* |
| WORM Enforcement | Append-only immutability for evidentiary storage | ∀*i*: *R*<sub>*i*</sub> immutable after offset *o*<sub>*i*</sub> committed |
| Hash Chain | Cryptographic linkage of sequential records | *h*<sub>*i*</sub> = *H*(*h*<sub>*i*−1</sub> ‖ *n*<sub>*i*</sub> ‖ *d*<sub>*i*</sub>) |
| Logical Fracture | Detected breach in cryptographic, temporal, or semantic continuity | ∃*i* : *h*<sub>*i*</sub>′ ≠ *h*<sub>*i*</sub> |

### Glossary

- **Evidentiary Artifact (取证工件):** A structured, self-contained data object produced by `SecurityAudit`, bearing cryptographic provenance and admissible for forensic reconstruction.
- **Logical Fracture (逻辑断裂):** Any detectable discontinuity in a hash chain, timestamp sequence, or semantic filter state; indicative of tampering, clock manipulation, or adversarial injection.
- **Floor Division:** The mathematical operation ⌊*a*/*b*⌋ for *a*, *b* ∈ ℤ, *b* ≠ 0, yielding a unique integer quotient without fractional residue.
- **WORM:** Write Once Read Many; a storage policy ensuring that once an evidentiary record is committed, no subsequent operation may alter or delete it.
- **Rational Decay Factor:** An exact fraction *N*/*D* represented by two coprime integers, used in place of floating-point exponentials to preserve determinism.
- **Token Bucket:** An integer counter that accrues discrete tokens at rate *ρ* per quantum *T*, capped by ceiling *σ*, and depleted by request costs *κ*.

### 【Scientific Note】

VIGÍA occasionally employs terminology derived from semiotics and the philosophy of language—specifically Charles Sanders Peirce’s theory of signs, Umberto Eco’s coding theory, and H. Paul Grice’s conversational maxims. For empirical scientists, these terms should be understood strictly as formal signal-processing analogues, not as metaphysical speculation. Peirce’s triadic relation (representamen-object-interpretant) models how a forensic sensor maps raw physical signals into classified symbolic categories; it is a measurement epistemology, not mysticism. Eco’s coding theory describes the protocol framing that constrains the space of valid interpretations, functionally identical to how a communication standard defines permissible packet structures. Grice’s maxims (quantity, quality, relation, manner) operate as deterministic noise-reduction filters, rejecting inputs that violate expected informativeness or clarity thresholds. When `LLMShield` performs semantic validation, it applies these principles as computable classification rules over integer token sequences. The module treats natural language as a measurable signal space; its “interpretations” are total functions over discrete alphabets, entirely consistent with physicalist and operational epistemology.

### Related VIGÍA Modules

This module consumes normalized evidentiary tokens from `vigia/core/ingest.py`, which performs schema validation and integer normalization on incoming data streams. Cryptographic primitives for `verify_chain` are supplied by `vigia/chain/integrity.py`, providing platform-optimized hashing routines restricted to bitwise integer operations. Persistent serialization of audit records is delegated to `vigia/audit/logger.py`, while physical WORM storage constraints are enforced at the media layer by `vigia/storage/worm.py`. The `LLMShield` class coordinates adversarial test-vector generation with `vigia/ml/shield.py`. Together, these modules constitute the VIGÍA trust boundary and evidentiary lifecycle.

**SPDX-License-Identifier: GPL-3.0-or-later**

---

## ESPAÑOL

**Identificación del módulo:** `vigia/security/security.py`  
**ID de lote forense:** vigia-doc-0126-741696a1  
**UID del artefacto:** 741696a1  

### ¿Qué es este módulo?

Este módulo constituye el perímetro defensivo y el subsistema de mantenimiento de confianza probatoria de la arquitectura forense VIGÍA. Si vos imaginás un laboratorio forense físico, este módulo cumple la función del escritorio de control de accesos, del protocolo de sellado de bolsas de evidencia y del registro de confianza de visitantes, pero automatizado mediante matemática exacta y reproducible. El módulo aplica cinco políticas centrales: (1) decaimiento determinístico de la confianza, de modo que credenciales obsoletas o evidencia envejecida pierdan autoridad a través de una reducción geométrica entera exacta; (2) auditoría de seguridad, que produce artefactos forenses (取证工件) inmutables y criptográficamente vinculados, aptos para su presentación en procedimientos judiciales; (3) blindaje de modelos de lenguaje grandes (LLM), que sanitiza entradas y salidas contra manipulaciones adversarias mediante clasificación determinista por autómatas de estado finito; (4) limitación adaptativa de tasa, que regula el flujo de solicitudes mediante aritmética discreta de cubeta de tokens para prevenir el agotamiento de recursos; y (5) verificación de cadena criptográfica, que garantiza que cada registro de auditoría se vincule con su predecesor de tal modo que cualquier alteración genere una fractura lógica (逻辑断裂) detectable. Todas las operaciones se ejecutan exclusivamente sobre el anillo de los enteros ℤ, eliminando la no reproducibilidad propia de las aproximaciones de punto flotante IEEE 754 y satisfaciendo así los mandatos de reproducibilidad más estrictos de la ciencia forense.

### Fundamentos matemáticos

El módulo se apoya en tres pilares matemáticos exactos.

**1. Decaimiento geométrico discreto de la confianza.**  
Sea la puntuación de confianza en la época *t* denotada por el entero *S*<sub>*t*</sub> ∈ [0, *S*<sub>máx</sub>]. El sistema define un factor de decaimiento racional *q* = *N* / *D*, donde *N*, *D* ∈ ℤ<sup>+</sup>, *N* < *D*, y ambos son constantes enteras configurables (al igual que las constantes globales del módulo *P* y *T*). La regla de actualización para *k* intervalos discretos transcurridos es:

*S*<sub>*t*+*k*</sub> = ⌊ *S*<sub>*t*</sub> · (*N*/*D*)<sup>*k*</sup> ⌋,

la cual se computa iterativamente mediante división entera por piso para garantizar que cada valor intermedio permanezca como entero:

*S*<sub>*i*+1</sub> = ⌊ (*S*<sub>*i*</sub> · *N*) / *D* ⌋.

Como la división por piso es una función total sobre los enteros, el resultado es idéntico bit a bit en todas las arquitecturas de CPU.

**2. Limitación de tasa por cubeta de tokens con aritmética entera.**  
Cada cliente *c* mantiene un vector de estado (*C*, *τ*<sub>últ</sub>, *σ*), donde *C* ∈ ℤ es el conteo actual de tokens, *τ*<sub>últ</sub> ∈ ℤ es la última marca temporal de recarga medida en segundos enteros, y *σ* ∈ ℤ es el techo de ráfaga. La tasa de recarga *ρ* ∈ ℤ<sup>+</sup> especifica los tokens acumulados por cada quantum de tiempo base *T*. Cuando una solicitud arriba en el tiempo entero *τ*<sub>ahora</sub>, el controlador computa:

Δ*τ* = ⌊ (*τ*<sub>ahora</sub> − *τ*<sub>últ</sub>) / *T* ⌋,  
*C*′ = mín(*σ*, *C* + *ρ* · Δ*τ*).

Si el costo de la solicitud *κ* satisface *C*′ ≥ *κ*, la operación prosigue y el estado se actualiza a (*C*′ − *κ*, *τ*<sub>ahora</sub>, *σ*); de lo contrario, se eleva la excepción `RateLimitExceeded`. Todas las variables son enteras; no se utiliza temporización de punto flotante.

**3. Encadenamiento criptográfico para inmutabilidad de auditoría.**  
Sea *H* : {0,1}<sup>*</sup> → {0,1}<sup>*λ*</sup> una función hash resistente a colisiones con *λ* ≥ 256. Cada registro probatorio *R*<sub>*i*</sub> contiene un resumen del payload *d*<sub>*i*</sub> y un número de secuencia monótono *n*<sub>*i*</sub> ∈ ℤ<sup>+</sup>. El vínculo de cadena se define como:

*h*<sub>*i*</sub> = *H*(*h*<sub>*i*−1</sub> ‖ *n*<sub>*i*</sub> ‖ *d*<sub>*i*</sub>),

donde ‖ denota concatenación y *h*<sub>0</sub> es un vector de inicialización público. Esta estructura forma una cinta tipo Merkle-Damgård; alterar cualquier *R*<sub>*i*</sub> o *h*<sub>*i*−1</sub> invalida todos los resúmenes posteriores.

### Descripción algorítmica

**`TrustExponentialDecay`**  
Un objeto computacional con estado que encapsula el modelo de decaimiento geométrico. Su método principal, `apply_decay(current_score: int, elapsed_intervals: int) -> int`, ejecuta exactamente *k* = `elapsed_intervals` iteraciones de la actualización por multiplicación con piso. Como *k* está acotado por el conteo máximo de épocas (una constante configurable), la operación tiene tiempo O(1) amortizado. La clase precomputa el par racional (*N*, *D*) y exige *S*<sub>máx</sub> ≤ *P* para garantizar que todos los productos quepan dentro de la palabra entera de la plataforma sin ambigüedades de desbordamiento.

**`SecurityAudit`**  
El motor de registro probatorio. Los métodos `log_block(...)`, `log_info(...)` y `log_tool_error(...)` emiten cada uno un registro estructurado que contiene: (a) el número de secuencia monótono *n* incrementado exactamente en uno; (b) la marca temporal Unix entera *τ*; (c) un clasificador de tipo de evento; (d) el resumen SHA-3 del payload; y (e) el hash predecesor *h*<sub>*i*−1</sub>. Los registros se serializan en un orden de bytes canónico (big-endian) antes de hashear para asegurar determinismo entre plataformas.

**`LLMShield`**  
Una capa de saneamiento semántico que protege los subsistemas LLM contra inyección de prompts, exfiltración de datos y manipulación adversaria de tokens. El método `scan(input_text)` descompone la entrada en una secuencia de identificadores de tokens enteros y la evalúa contra una batería de autómatas de estado finito deterministas (DFA) que codifican firmas de amenaza léxicas y sintácticas. El auxiliar `decorator` es un procedimiento de orden superior que envuelve operaciones arbitrarias, aplicando `scan` pre-ejecución y `SecurityAudit` post-ejecución sin modificar el código fuente de la rutina envuelta.

**`_RateLimitEntry` y `_AdaptiveRateLimiter`**  
Máquinas de estado internas que rastrean conteos de tokens por cliente. `_RateLimitEntry` almacena la tríada entera (*C*, *τ*<sub>últ</sub>, *σ*). `_AdaptiveRateLimiter` agrega múltiples entradas y expone `rate_limit(client_id: str, cost: int) -> bool`, que ejecuta el algoritmo entero de recarga y deducción descrito precedentemente. El calificativo “adaptativo” se refiere a la capacidad de reconfigurar *ρ* y *σ* por cliente en épocas administrativas, no a ningún proceso estocástico o no determinista.

**`enforce_worm`**  
Implementa restricciones WORM (*Write Once Read Many*) sobre los backends de almacenamiento. El procedimiento emite directivas atómicas de agregado, retornando un desplazamiento entero de almacenamiento *o*<sub>*i*</sub> y un compromiso criptográfico *c*<sub>*i*</sub> = *H*(*R*<sub>*i*</sub> ‖ *o*<sub>*i*</sub>). Una vez confirmado, ningún subsistema VIGÍA puede mutar el registro, satisfaciendo la inmutabilidad física y lógica.

**`verify_chain`**  
Acepta una secuencia ordenada de registros de auditoría y recomputa el vínculo hash. Para cada índice *i* > 0, calcula *h*<sub>*i*</sub>′ = *H*(*h*<sub>*i*−1</sub> ‖ canónico(*R*<sub>*i*</sub>)) y afirma la igualdad con el *h*<sub>*i*</sub> almacenado. Retorna un indicador booleano de integridad y, ante un fallo, el índice exacto de la primera fractura lógica.

**`scan`**  
Una rutina periódica de verificación de integridad invocada por el planificador VIGÍA. Audita el estado actual de todas las cubetas de límite de tasa, puntuaciones de confianza y cuarentenas pendientes de `LLMShield`, emitiendo un informe determinista consolidado.

### Especificaciones de entrada y salida

| Procedimiento | Dominio de entrada | Dominio de salida | Precondiciones | Postcondiciones |
|---|---|---|---|---|
| `apply_decay` | *S* ∈ ℤ, 0 ≤ *S* ≤ *S*<sub>máx</sub>; *k* ∈ ℤ<sup>+</sup> | *S*′ ∈ ℤ, 0 ≤ *S*′ ≤ *S* | *N*, *D*, *S*<sub>máx</sub> configurados | *S*′ = ⌊*S*·(*N*/*D*)<sup>*k*</sup>⌋ vía pasos enteros exactos |
| `rate_limit` | `client_id` ∈ Σ<sup>*</sup>; *κ* ∈ ℤ<sup>+</sup> | booleano o `RateLimitExceeded` | *σ*, *ρ*, *T* configurados | Si True, estado decrementado en *κ*; sino excepción |
| `log_block` / `log_info` / `log_tool_error` | Payload del evento ∈ secuencia de bytes *B*<sup>*</sup> | ID de registro *n* ∈ ℤ<sup>+</sup> | Contexto de auditoría inicializado | *n*<sub>*i*+1</sub> = *n*<sub>*i*</sub> + 1; cadena extendida |
| `verify_chain` | Lista ordenada de registros ℛ | (*integridad*: bool, *índice_fractura*: ℤ) | ℛ no vacía | True sii ∀*i*, *h*<sub>*i*</sub>′ = *h*<sub>*i*</sub> |
| `enforce_worm` | Registro canónico *R* ∈ *B*<sup>*</sup> | (*desplazamiento*: ℤ, *compromiso*: *B*<sup>*λ*</sup>) | Backend de almacenamiento escribible | Registro agregado y sellado |
| `scan` | Texto de entrada LLM ∈ UTF-8 | (*limpio*: bool, *vector_amenaza*: ℤ<sup>*</sup>) | Vocabulario de `LLMShield` cargado | Clasificación determinista |

### Garantías determinísticas

1. **Reproducibilidad bit a bit:** Todas las operaciones aritméticas se confinan a ℤ. La división es exclusivamente división entera por piso. En consecuencia, cada algoritmo produce salidas idénticas bit a bit en arquitecturas x86_64, ARM64 y RISC-V, satisfaciendo los criterios de reproducibilidad forense.
2. **Monotonicidad temporal:** El módulo exige que cada marca temporal entera observada *τ*<sub>*i*+1</sub> ≥ *τ*<sub>*i*</sub>. Una violación eleva una excepción de fractura lógica, impidiendo ataques de repetición temporal.
3. **No repudio de auditoría:** Cada artefacto probatorio vincula el número de secuencia monótono *n*<sub>*i*</sub>, el resumen del payload y el hash predecesor *h*<sub>*i*−1</sub>. Esta tríada conforma un objeto autoautenticable que no puede ser repudiado sin romper la función hash.
4. **Monotonicidad del límite de tasa:** Para cualquier cliente, el conteo acumulado de solicitudes admitidas en el intervalo [0, *t*] está acotado superiormente por *σ* + *ρ*·⌈*t*/*T*⌉ y es no decreciente. Las decisiones de rechazo son markovianas: dependen únicamente del vector de estado entero actual, no del historial de ejecución.
5. **Decaimiento idempotente:** `apply_decay`(*S*, 0) = *S* para todo *S* válido. Reaplicar el decaimiento sobre cero intervalos transcurridos no altera la puntuación de confianza.

### Cumplimiento normativo

- **Estándar Daubert (Reglas Federales de Evidencia 702 de EE.UU.):** Los algoritmos enteros publicados, las reglas de actualización deterministas y el uso de primitivas hash estándar proveen una tasa de error conocida y empíricamente medible (efectivamente cero para la aritmética, acotada por la probabilidad de colisión para el hash). Esto satisface los requisitos de “reproducibilidad” y “aceptación general” exigidos para el testimonio de peritos.
- **GB/T 29360-2012** (*Programas comunes de la informática forense*): `enforce_worm` y `verify_chain` implementan los mandatos de la norma para protección contra escritura de la evidencia original y verificación de la cadena de custodia.
- **MLPS 2.0 / GB/T 22239-2019** (*Tecnología de seguridad de la información—Línea base para la protección clasificada de la ciberseguridad*): La granularidad del control de acceso de `_AdaptiveRateLimiter`, la densidad de la pista de auditoría de `SecurityAudit` y la semántica de prevención de intrusiones de `LLMShield` satisfacen conjuntamente los requisitos del entorno de cómputo seguro y del centro de gestión de seguridad para despliegues de Nivel 3 (Protección Supervisada) y Nivel 4 (Protección Obligatoria).

### Conceptos clave

| Concepto | Descripción | Representación formal |
|---|---|---|
| Decaimiento de confianza discreto | Reducción entera exacta de puntuaciones de confianza a través de épocas | *S*<sub>*t*+*k*</sub> = ⌊*S*<sub>*t*</sub>·(*N*/*D*)<sup>*k*</sup>⌋ |
| Límite de tasa adaptativo | Regulación por cubeta de tokens utilizando quanta de tiempo enteros | *C*′ = mín(*σ*, *C* + *ρ*·Δ*τ*) − *κ* |
| Aplicación WORM | Inmutabilidad de solo agregado para almacenamiento probatorio | ∀*i*: *R*<sub>*i*</sub> inmutable luego de confirmado el desplazamiento *o*<sub>*i*</sub> |
| Cadena hash | Vínculo criptográfico de registros secuenciales | *h*<sub>*i*</sub> = *H*(*h*<sub>*i*−1</sub> ‖ *n*<sub>*i*</sub> ‖ *d*<sub>*i*</sub>) |
| Fractura lógica | Brecha detectable en continuidad criptográfica, temporal o semántica | ∃*i* : *h*<sub>*i*</sub>′ ≠ *h*<sub>*i*</sub> |

### Glosario

- **Artefacto forense / Artefacto probatorio (取证工件):** Un objeto de datos estructurado y auto contenido producido por `SecurityAudit`, provisto de proveniencia criptográfica y admisible para reconstrucción forense.
- **Fractura lógica (逻辑断裂):** Cualquier discontinuidad detectable en una cadena hash, una secuencia de marcas temporales o un estado de filtro semántico; indicativa de alteración, manipulación de reloj o inyección adversaria.
- **División por piso:** La operación matemática ⌊*a*/*b*⌋ para *a*, *b* ∈ ℤ, *b* ≠ 0, que produce un cociente entero único sin residuo fraccionario.
- **WORM:** *Write Once Read Many*; una política de almacenamiento que asegura que, una vez confirmado un registro probatorio, ninguna operación posterior puede alterarlo o eliminarlo.
- **Factor de decaimiento racional:** Una fracción exacta *N*/*D* representada por dos enteros coprimos, utilizada en lugar de exponenciales de punto flotante para preservar el determinismo.
- **Cubeta de tokens:** Un contador entero que acumula tokens discretos a tasa *ρ* por quantum *T*, con techo *σ*, y se depleta por costos de solicitud *κ*.

### 【Nota Científica】

VIGÍA emplea ocasionalmente terminología derivada de la semiótica y la filosofía del lenguaje—específicamente la teoría de los signos de Charles Sanders Peirce, la teoría de los códigos de Umberto Eco y los máximas conversacionales de H. Paul Grice. Para vos, como científico empírico, estos términos deben comprenderse estrictamente como análogos formales del procesamiento de señales, no como especulación metafísica. La tríada peirceana (representamen-objeto-interpretante) modela cómo un sensor forense mapea señales físicas brutas hacia categorías simbólicas clasificadas; es una epistemología de la medición, no misticismo. La teoría de códigos de Eco describe el enmarcado de protocolo que restringe el espacio de interpretaciones válidas, funcionalmente idéntico a cómo un estándar de comunicación define estructuras de paquetes permisibles. Los máximas de Grice (cantidad, calidad, relación, modalidad) operan como filtros deterministas de reducción de ruido, rechazando entradas que violan los umbrales esperados de informatividad o claridad. Cuando `LLMShield` realiza validación semántica, aplica estos principios como reglas de clasificación computables sobre secuencias de tokens enteros. El módulo trata el lenguaje natural como un espacio de señales medibles; sus “interpretaciones” son funciones totales sobre alfabetos discretos, enteramente consistentes con la epistemología fisicalista y operacional.

### Módulos VIGÍA relacionados

Este módulo consume tokens probatorios normalizados provenientes de `vigia/core/ingest.py`, que ejecuta validación de esquema y normalización entera sobre los flujos de datos entrantes. Las primitivas criptográficas para `verify_chain` son suministradas por `vigia/chain/integrity.py`, que provee rutinas de hash optimizadas por plataforma restringidas a operaciones bit a bit enteras. La serialización persistente de registros de auditoría se delega a `vigia/audit/logger.py`, mientras que las restricciones físicas de almacenamiento WORM se aplican en la capa de medios mediante `vigia/storage/worm.py`. La clase `LLMShield` coordina la generación de vectores de prueba adversaria con `vigia/ml/shield.py`. En conjunto, estos módulos constituyen el perímetro de confianza y el ciclo de vida probatorio de VIGÍA.

**SPDX-License-Identifier: GPL-3.0-or-later**

---

## РУССКИЙ

**Идентификатор модуля:** `vigia/security/security.py`  
**Идентификатор партии:** vigia-doc-0126-741696a1  
**UID артефакта:** 741696a1  

### Что представляет собой данный модуль?

Настоящий модуль является оборонительным периметром и подсистемой поддержания доверия к доказательственной базе в составе судебно-экспертной архитектуры VIGÍA. Если провести аналогию с физической судебно-экспертной лабораторией, данный модуль выполняет функции стола контроля доступа, протокола опечатывания пакетов с вещественными доказательствами и журнала учёта доверия к посетителям, однако автоматизированным путём с применением точной и воспроизводимой математики. Модуль реализует пять основных политик: (1) детерминированное экспоненциальное затухание доверия, обеспечивающее утрату полномочий устаревшими учётными данными или состарившимися доказательствами посредством точного целочисленного геометрического убывания; (2) аудит безопасности, порождающий неизменяемые и криптографически связанные артефакты цифровой экспертизы (取证工件), пригодные для представления в судебном заседании; (3) защитный экран для больших языковых моделей (LLM), осуществляющий детерминистскую санитарную обработку входных и выходных данных против состязательных манипуляций; (4) адаптивное ограничение скорости (рейт-лимитинг), регулирующее пропускную способность запросов дискретной арифметикой маркерного ведра для предотвращения исчерпания ресурсов; и (5) верификацию криптографической цепочки, гарантирующую, что каждая запись аудита связана со своей предшественницей таким образом, что любое вмешательство порождает обнаружимый логический разрыв (逻辑断裂). Все операции выполняются исключительно в кольце целых чисел ℤ, что устраняет невоспроизводимость, присущую аппроксимациям с плавающей точкой по стандарту IEEE 754, и тем самым удовлетворяет наиболее строгим требованиям воспроизводимости, предъявляемым к судебной экспертизе.

### Математические основания

Модуль опирается на три точных математических столпа.

**1. Дискретное геометрическое затухание доверия.**  
Пусть показатель доверия в эпоху *t* обозначается целым числом *S*<sub>*t*</sub> ∈ [0, *S*<sub>max</sub>]. Система определяет рациональный коэффициент затухания *q* = *N* / *D*, где *N*, *D* ∈ ℤ<sup>+</sup>, *N* < *D*, и оба являются настраиваемыми целочисленными константами (наряду с глобальными константами модуля *P* и *T*). Правило обновления за *k* прошедших дискретных интервалов имеет вид:

*S*<sub>*t*+*k*</sub> = ⌊ *S*<sub>*t*</sub> · (*N*/*D*)<sup>*k*</sup> ⌋,

причём вычисление производится итеративно с помощью деления нацело с округлением вниз, гарантируя, что каждое промежуточное значение остаётся целым:

*S*<sub>*i*+1</sub> = ⌊ (*S*<sub>*i*</sub> · *N*) / *D* ⌋.

Поскольку деление нацело с округлением вниз является тотальной функцией на множестве целых чисел, результат побитово идентичен на всех архитектурах центральных процессоров.

**2. Целочисленное рейт-лимитирование методом маркерного ведра.**  
Каждый клиент *c* поддерживает вектор состояния (*C*, *τ*<sub>last</sub>, *σ*), где *C* ∈ ℤ — текущее количество маркеров, *τ*<sub>last</sub> ∈ ℤ — метка времени последнего пополнения в целых секундах, а *σ* ∈ ℤ — потолок всплеска. Интенсивность пополнения *ρ* ∈ ℤ<sup>+</sup> задаёт количество маркеров, начисляемых за базовый квант времени *T*. При поступлении запроса в целочисленный момент *τ*<sub>now</sub> контроллер вычисляет:

Δ*τ* = ⌊ (*τ*<sub>now</sub> − *τ*<sub>last</sub>) / *T* ⌋,  
*C*′ = min(*σ*, *C* + *ρ* · Δ*τ*).

Если стоимость запроса *κ* удовлетворяет условию *C*′ ≥ *κ*, операция выполняется, а состояние обновляется до (*C*′ − *κ*, *τ*<sub>now</sub>, *σ*); в противном случае возбуждается исключение `RateLimitExceeded`. Все переменные являются целыми числами; временны́е измерения с плавающей точкой не используются.

**3. Криптографическое связывание в цепочку для обеспечения неизменности аудита.**  
Пусть *H* : {0,1}<sup>*</sup> → {0,1}<sup>*λ*</sup> — функция хеширования, устойчивая к коллизиям, при *λ* ≥ 256. Каждая экспертная запись *R*<sub>*i*</sub> содержит дайджест полезной нагрузки *d*<sub>*i*</sub> и монотонный порядковый номер *n*<sub>*i*</sub> ∈ ℤ<sup>+</sup>. Связь в цепочке определяется как:

*h*<sub>*i*</sub> = *H*(*h*<sub>*i*−1</sub> ‖ *n*<sub>*i*</sub> ‖ *d*<sub>*i*</sub>),

где ‖ обозначает конкатенацию, а *h*<sub>0</sub> — публичный вектор инициализации. Данная структура образует ленту типа Меркла—Дамгарда; изменение любой *R*<sub>*i*</sub> или *h*<sub>*i*−1</sub> делает недействительными все последующие дайджесты.

### Алгоритмическое описание

**`TrustExponentialDecay`**  
Сохраняющий состояние вычислительный объект, инкапсулирующий модель геометрического затухания. Его основной метод `apply_decay(current_score: int, elapsed_intervals: int) -> int` выполняет ровно *k* = `elapsed_intervals` итераций обновления с помощью умножения с округлением вниз. Поскольку *k* ограничен максимальным количеством эпох (настраиваемая константа), операция выполняется за амортизированное время O(1). Класс предвычисляет рациональную пару (*N*, *D*) и требует *S*<sub>max</sub> ≤ *P*, чтобы гарантировать отсутствие переполнения или неоднозначности циклического перехода.

**`SecurityAudit`**  
Двигатель судебно-экспертного протоколирования. Методы `log_block(...)`, `log_info(...)` и `log_tool_error(...)` каждый излучают структурированную запись, содержащую: (a) монотонный порядковый номер *n*, увеличенный точно на единицу; (b) целочисленную метку времени Unix *τ*; (c) классификатор типа события; (d) дайджест SHA-3 полезной нагрузки; и (e) хеш предшественника *h*<sub>*i*−1</sub>. Записи сериализуются в канонический порядок байтов (big-endian) перед хешированием для обеспечения межплатформенного детерминизма.

**`LLMShield`**  
Семантический санитарный слой, защищающий подсистемы LLM от инъекций промптов, эксфильтрации данных и состязательной манипуляции токенами. Метод `scan(input_text)` разлагает входные данные на последовательность целочисленных идентификаторов токенов и оценивает её на батарее детерминированных конечных автоматов (ДКА), кодирующих лексические и синтаксические сигнатуры угроз. Вспомогательный метод `decorator` представляет собой процедуру высшего порядка, оборачивающую произвольные операции и принудительно применяющую `scan` перед выполнением и `SecurityAudit` после выполнения без модификации исходного кода обёрнутой подпрограммы.

**`_RateLimitEntry` и `_AdaptiveRateLimiter`**  
Внутренние конечные автоматы, отслеживающие счётчики маркеров для каждого клиента. `_RateLimitEntry` хранит целочисленную триаду (*C*, *τ*<sub>last</sub>, *σ*). `_AdaptiveRateLimiter` агрегирует множество записей и предоставляет метод `rate_limit(client_id: str, cost: int) -> bool`, реализующий описанный выше целочисленный алгоритм пополнения и вычитания. Эпитет «адаптивный» относится к возможности переконфигурирования *ρ* и *σ* для каждого клиента в административные эпохи, а не к какому-либо недетерминированному или стохастическому процессу.

**`enforce_worm`**  
Реализует ограничения WORM (*Write Once Read Many*) на уровне хранилищ. Процедура выдаёт атомарные директивы добавления, возвращая целочисленное смещение хранения *o*<sub>*i*</sub> и криптографическое обязательство *c*<sub>*i*</sub> = *H*(*R*<sub>*i*</sub> ‖ *o*<sub>*i*</sub>). После фиксации ни одна подсистема VIGÍA не может мутировать запись, что обеспечивает физическую и логическую неизменность.

**`verify_chain`**  
Принимает упорядоченную последовательность аудиторских записей и пересчитывает хеш-связь. Для каждого индекса *i* > 0 вычисляется *h*<sub>*i*</sub>′ = *H*(*h*<sub>*i*−1</sub> ‖ канонический(*R*<sub>*i*</sub>)), после чего проверяется равенство сохранённому *h*<sub>*i*</sub>. Возвращается булев флаг целостности и, при сбое, точный индекс первого логического разрыва.

**`scan`**  
Периодическая процедура проверки целостности, вызываемая планировщиком VIGÍA. Она проверяет текущее состояние всех маркерных вёдер рейт-лимитинга, показателей доверия и ожидающих карантинов `LLMShield`, излучая консолидированный детерминированный отчёт.

### Спецификации входных и выходных данных

| Процедура | Входной домен | Выходной домен | Предусловия | Постусловия |
|---|---|---|---|---|
| `apply_decay` | *S* ∈ ℤ, 0 ≤ *S* ≤ *S*<sub>max</sub>; *k* ∈ ℤ<sup>+</sup> | *S*′ ∈ ℤ, 0 ≤ *S*′ ≤ *S* | *N*, *D*, *S*<sub>max</sub> сконфигурированы | *S*′ = ⌊*S*·(*N*/*D*)<sup>*k*</sup>⌋ точно через целочисленные шаги |
| `rate_limit` | `client_id` ∈ Σ<sup>*</sup>; *κ* ∈ ℤ<sup>+</sup> | булево или `RateLimitExceeded` | *σ*, *ρ*, *T* сконфигурированы | При True состояние уменьшено на *κ*; иначе исключение |
| `log_block` / `log_info` / `log_tool_error` | Полезная нагрузка события ∈ последовательность байтов *B*<sup>*</sup> | ID записи *n* ∈ ℤ<sup>+</sup> | Контекст аудита инициализирован | *n*<sub>*i*+1</sub> = *n*<sub>*i*</sub> + 1; цепочка расширена |
| `verify_chain` | Упорядоченный список записей ℛ | (*целостность*: bool, *индекс_разрыва*: ℤ) | ℛ непуст | True тогда и только тогда, когда ∀*i*, *h*<sub>*i*</sub>′ = *h*<sub>*i*</sub> |
| `enforce_worm` | Каноническая запись *R* ∈ *B*<sup>*</sup> | (*смещение*: ℤ, *обязательство*: *B*<sup>*λ*</sup>) | Хранилище доступно для записи | Запись добавлена и запечатана |
| `scan` | Входной текст LLM ∈ UTF-8 | (*чистота*: bool, *вектор_угрозы*: ℤ<sup>*</sup>) | Словарь `LLMShield` загружен | Детерминистская классификация |

### Детерминистские гарантии

1. **Побитовая воспроизводимость:** Все арифметические операции ограничены множеством ℤ. Деление исключительно целочисленное с округлением вниз. Следовательно, каждый алгоритм выдаёт побитово идентичные результаты на архитектурах x86_64, ARM64 и RISC-V, удовлетворяя критериям судебной воспроизводимости.
2. **Временна́я монотонность:** Модуль требует, чтобы каждая наблюдаемая целочисленная метка времени *τ*<sub>*i*+1</sub> ≥ *τ*<sub>*i*</sub>. Нарушение возбуждает исключение логического разрыва, предотвращая темпоральные атаки повтора.
3. **Невозможность отречения от аудита:** Каждый артефакт экспертизы связывает монотонный порядковый номер *n*<sub>*i*</sub>, дайджест полезной нагрузки и хеш предшественника *h*<sub>*i*−1</sub>. Эта триада образует самоаутентифицируемый объект, который невозможно опровергнуть без нарушения свойств хеш-функции.
4. **Монотонность рейт-лимитинга:** Для любого клиента совокупное количество допущенных запросов на интервале [0, *t*] ограничено сверху величиной *σ* + *ρ*·⌈*t*/*T*⌉ и является неубывающим. Решения об отказе марковски: они зависят только от текущего целочисленного вектора состояния, а не от истории исполнения.
5. **Идемпотентность затухания:** `apply_decay`(*S*, 0) = *S* для всех допустимых *S*. Повторное применение затухания при нуле прошедших интервалов не изменяет показатель доверия.

### Соответствие стандартам

- **Стандарт Доберта (Федеральные правила доказывания 702 США):** Опубликованные целочисленные алгоритмы модуля, детерминистские правила обновления и использование стандартных хеш-примитивов обеспечивают известную и эмпирически измеримую частоту ошибок (фактически нулевую для арифметики, ограниченную вероятностью коллизии для хеширования). Это удовлетворяет требованиям «воспроизводимости» и «общего признания», предъявляемым к заключению эксперта.
- **GB/T 29360-2012** (*Общие программы компьютерной экспертизы*): Процедуры `enforce_worm` и `verify_chain` реализуют требования стандарта к защите исходных доказательств от записи и к верификации цепочки хранения.
- **MLPS 2.0 / GB/T 22239-2019** (*Технология безопасности информации—Базовый уровень классифицированной защиты кибербезопасности*): Гранулярность контроля доступа `_AdaptiveRateLimiter`, плотность аудиторского следа `SecurityAudit` и семантика предотвращения вторжений `LLMShield` совместно удовлетворяют требованиям к среде безопасных вычислений и центру управления безопасностью для развёртываний уровня 3 (Контролируемая защита) и уровня 4 (Обязательная защита).

### Ключевые понятия

| Понятие | Описание | Формальное представление |
|---|---|---|
| Дискретное затухание доверия | Точное целочисленное уменьшение показателей доверия по эпохам | *S*<sub>*t*+*k*</sub> = ⌊*S*<sub>*t*</sub>·(*N*/*D*)<sup>*k*</sup>⌋ |
| Адаптивное рейт-лимитирование | Регулирование маркерным ведром с использованием целочисленных квантов времени | *C*′ = min(*σ*, *C* + *ρ*·Δ*τ*) − *κ* |
| Применение WORM | Дополнительная неизменность хранилища экспертных данных | ∀*i*: *R*<sub>*i*</sub> неизменна после фиксации смещения *o*<sub>*i*</sub> |
| Хеш-цепочка | Криптографическая связь последовательных записей | *h*<sub>*i*</sub> = *H*(*h*<sub>*i*−1</sub> ‖ *n*<sub>*i*</sub> ‖ *d*<sub>*i*</sub>) |
| Логический разрыв | Обнаруженное нарушение криптографической, темпоральной или семантической непрерывности | ∃*i* : *h*<sub>*i*</sub>′ ≠ *h*<sub>*i*</sub> |

### Глоссарий

- **Артефакт цифровой экспертизы (取证工件):** Структурированный самодостаточный объект данных, порождённый `SecurityAudit`, наделённый криптографическим происхождением и пригодный для судебной реконструкции.
- **Логический разрыв (逻辑断裂):** Любая обнаруженная разрывность в хеш-цепочке, последовательности меток времени или состоянии семантического фильтра; свидетельствует о фальсификации, манипуляции часами или состязательной инъекции.
- **Деление с округлением вниз:** Математическая операция ⌊*a*/*b*⌋ для *a*, *b* ∈ ℤ, *b* ≠ 0, дающая единственное целое частное без дробного остатка.
- **WORM:** *Write Once Read Many*; политика хранения, гарантирующая, что после фиксации экспертной записи ни одна последующая операция не может её изменить или удалить.
- **Рациональный коэффициент затухания:** Точная дробь *N*/*D*, представленная двумя взаимно простыми целыми числами, используемая вместо показательных функций с плавающей точкой для сохранения детерминизма.
- **Маркерное ведро:** Целочисленный счётчик, накапливающий дискретные маркеры со скоростью *ρ* за квант *T* с потолком *σ* и расходуемый по стоимости запроса *κ*.

### 【Научное примечание】

В архитектуре VIGÍA время от времени используется терминология, заимствованная из семиотики и философии языка—в частности, теория знаков Чарльза Сандерса Пирса, теория кодов Умберто Эко и разговорные максимы Герберта Пола Грайса. Для исследователей, работающих в эмпирических науках, эти термины должны пониматься строго как формальные аналоги обработки сигналов, а не как метафизическая спекуляция. Триада Пирса (представляющий—объект—интерпретант) моделирует то, как судебно-экспертный датчик отображает необработанные физические сигналы на классифицированные символические категории; это эпистемология измерения, а не мистицизм. Теория кодов Эко описывает протокольное обрамление, ограничивающее пространство допустимых интерпретаций, функционально тождественное тому, как стандарт связи определяет допустимые структуры пакетов. Максимы Грайса (количество, качество, отношение, манера) функционируют как детерминистские фильтры подавления шума, отвергая входные данные, нарушающие ожидаемые пороги информативности или ясности. Когда `LLMShield` выполняет семантическую валидацию, он применяет эти принципы как вычислимые правила классификации над последовательностями целочисленных токенов. Модуль трактует естественный язык как измеримое пространство сигналов; его «интерпретации» являются тотальными функциями над дискретными алфавитами, полностью согласованными с физикалистской и операционной эпистемологией.

### Связанные модули VIGÍA

Настоящий модуль потребляет нормализованные экспертные токены из `vigia/core/ingest.py`, выполняющего валидацию схемы и целочисленную нормализацию входных потоков данных. Криптографические примитивы для `verify_chain` предоставляются `vigia/chain/integrity.py`, обеспечивающим оптимизированные платформенно хеш-функции, ограниченные побитовыми целочисленными операциями. Персистентная сериализация аудиторских записей делегируется `vigia/audit/logger.py`, тогда как физические ограничения хранилища WORM применяются на уровне носителя модулем `vigia/storage/worm.py`. Класс `LLMShield` координирует генерацию состязательных тестовых векторов с `vigia/ml/shield.py`. Совместно указанные модули образуют периметр доверия и жизненный цикл экспертных данных VIGÍA.

**SPDX-License-Identifier: GPL-3.0-or-later**

---

## 中文

**模块标识：** `vigia/security/security.py`  
**取证批次编号：** vigia-doc-0126-741696a1  
**工件UID：** 741696a1  

### 这是什么模块？

本模块是VIGÍA取证架构的防御边界与证据信任维持子系统。若将其类比于实体法医实验室，则本模块相当于实验室的出入登记台、证物袋封装协议以及访客信任台账的数字化实现，但其运作完全依赖精确且可复现的数学方法。本模块执行五项核心策略：（1）确定性信任衰减，即通过精确的整数几何递减，使过期凭证或陈旧证据自动丧失效力；（2）安全审计，生成不可篡改且密码学绑定的取证工件（取证工件），可直接用于法庭举证；（3）大语言模型防护（LLMShield），利用确定性有限状态自动机对输入输出进行语义清洗，以抵御对抗性操纵；（4）自适应速率限制，采用离散整数令牌桶算术调控请求吞吐，防止资源耗尽；（5）密码学链式验证，确保每一条审计记录均与其前驱密码学绑定，任何篡改都将产生可检测的逻辑断裂（逻辑断裂）。所有运算严格限制在整数环ℤ内进行，彻底排除IEEE 754浮点近似带来的不可复现性，从而满足司法鉴定最严格的可复现性要求。

### 数学基础

本模块建立在三项精确数学支柱之上。

**1. 信任的离散几何衰减。**  
设第*t*个纪元（epoch）的信任评分为整数*S*<sub>*t*</sub> ∈ [0, *S*<sub>max</sub>]。系统定义有理衰减因子*q* = *N* / *D*，其中*N*, *D* ∈ ℤ<sup>+</sup>，*N* < *D*，二者均为可配置整数常数（与模块级常量*P*、*T*一同设定）。对于经过*k*个离散间隔后的更新规则为：

*S*<sub>*t*+*k*</sub> = ⌊ *S*<sub>*t*</sub> · (*N*/*D*)<sup>*k*</sup> ⌋，

该式通过向下取整除法迭代计算，以保证每一步中间值均为整数：

*S*<sub>*i*+1</sub> = ⌊ (*S*<sub>*i*</sub> · *N*) / *D* ⌋。

由于向下取整除法是整数集上的全函数，计算结果在所有CPU架构上比特级一致。

**2. 整数令牌桶速率限制。**  
每个客户端*c*维护一个状态向量(*C*, *τ*<sub>last</sub>, *σ*)，其中*C* ∈ ℤ为当前令牌数，*τ*<sub>last</sub> ∈ ℤ为最后一次充值的整数时间戳（秒），*σ* ∈ ℤ为突发上限。补充速率*ρ* ∈ ℤ<sup>+</sup>表示每基准时间量子*T*所累积的令牌数。当请求在整数时刻*τ*<sub>now</sub>到达时，控制器计算：

Δ*τ* = ⌊ (*τ*<sub>now</sub> − *τ*<sub>last</sub>) / *T* ⌋，  
*C*′ = min(*σ*, *C* + *ρ* · Δ*τ*)。

若请求成本*κ*满足*C*′ ≥ *κ*，则操作被允许，状态更新为(*C*′ − *κ*, *τ*<sub>now</sub>, *σ*)；否则抛出`RateLimitExceeded`异常。所有变量均为整数，不涉及浮点计时。

**3. 审计不可篡改性的密码学哈希链。**  
设*H* : {0,1}<sup>*</sup> → {0,1}<sup>*λ*</sup>为抗碰撞哈希函数，*λ* ≥ 256。每条取证记录*R*<sub>*i*</sub>包含载荷摘要*d*<sub>*i*</sub>与单调递增序号*n*<sub>*i*</sub> ∈ ℤ<sup>+</sup>。链式绑定定义为：

*h*<sub>*i*</sub> = *H*(*h*<sub>*i*−1</sub> ‖ *n*<sub>*i*</sub> ‖ *d*<sub>*i*</sub>)，

其中‖表示连接运算，*h*<sub>0</sub>为公开初始化向量。该结构形成类Merkle-Damgård磁带；篡改任意*R*<sub>*i*</sub>或*h*<sub>*i*−1</sub>将导致后续所有摘要失效。

### 算法描述

**`TrustExponentialDecay`**  
封装几何衰减模型的有状态计算对象。其主方法`apply_decay(current_score: int, elapsed_intervals: int) -> int`执行恰好*k* = `elapsed_intervals`次向下取整乘法迭代。由于*k*受最大纪元数（可配置常量）约束，该操作摊还时间复杂度为O(1)。类在初始化时预计算有理数对(*N*, *D*)，并强制*S*<sub>max</sub> ≤ *P*，以确保所有乘积在平台整数字长内完成，避免溢出或模回绕歧义。

**`SecurityAudit`**  
取证日志引擎。`log_block(...)`、`log_info(...)`与`log_tool_error(...)`各产生一条结构化记录，内容包括：（a）单调序号*n*严格递增1；（b）整数Unix时间戳*τ*；（c）事件类型分类符；（d）载荷的SHA-3摘要；（e）前驱哈希*h*<sub>*i*−1</sub>。记录在进行哈希运算前按大端字节序规范序列化，以保证跨平台确定性。

**`LLMShield`**  
保护LLM子系统的语义清洗层，防御提示注入、数据渗出及对抗性令牌操纵。`scan(input_text)`将输入分解为整数令牌ID序列，并通过一组确定性有限状态自动机（DFA）对其进行评估，这些DFA编码了词汇与句法层面的威胁特征。辅助方法`decorator`为一个高阶过程包装器，它在不修改被包装例程源码的前提下，对任意操作强制执行执行前`scan`与执行后`SecurityAudit`。

**`_RateLimitEntry`与`_AdaptiveRateLimiter`**  
追踪每客户端令牌计数的内部状态机。`_RateLimitEntry`存储整数三元组(*C*, *τ*<sub>last</sub>, *σ*)。`_AdaptiveRateLimiter`聚合多个条目，对外暴露`rate_limit(client_id: str, cost: int) -> bool`，执行上述整数充值与扣除算法。“自适应”一词指可在管理纪元针对各客户端重新配置*ρ*与*σ*，而非指任何非确定性或随机过程。

**`enforce_worm`**  
在存储后端实施一次写入多次读取（WORM）约束。该过程发出原子追加指令，返回整数存储偏移量*o*<sub>*i*</sub>与密码学承诺*c*<sub>*i*</sub> = *H*(*R*<sub>*i*</sub> ‖ *o*<sub>*i*</sub>)。一旦提交，任何VIGÍA子系统均不得修改该记录，从而实现物理与逻辑层面的不可变性。

**`verify_chain`**  
接受有序审计记录序列并重新计算哈希链接。对每个索引*i* > 0，计算*h*<sub>*i*</sub>′ = *H*(*h*<sub>*i*−1</sub> ‖ canonical(*R*<sub>*i*</sub>))，并断言其与存储值*h*<sub>*i*</sub>相等。返回完整性布尔标志；若校验失败，则返回首个逻辑断裂的精确索引。

**`scan`**  
由VIGÍA调度器调用的周期性完整性核查例程。审计当前所有速率限制令牌桶、信任评分及LLMShield待检隔离区的状态，输出合并的确定性报告。

### 输入/输出规范

| 过程 | 输入域 | 输出域 | 前置条件 | 后置条件 |
|---|---|---|---|---|
| `apply_decay` | *S* ∈ ℤ, 0 ≤ *S* ≤ *S*<sub>max</sub>；*k* ∈ ℤ<sup>+</sup> | *S*′ ∈ ℤ, 0 ≤ *S*′ ≤ *S* | *N*, *D*, *S*<sub>max</sub>已配置 | *S*′ = ⌊*S*·(*N*/*D*)<sup>*k*</sup>⌋，经精确整数步达成 |
| `rate_limit` | `client_id` ∈ Σ<sup>*</sup>；*κ* ∈ ℤ<sup>+</sup> | 布尔值或`RateLimitExceeded` | *σ*, *ρ*, *T*已配置 | 若为真，状态扣减*κ*；否则抛出异常 |
| `log_block`/`log_info`/`log_tool_error` | 事件载荷 ∈ 字节序列*B*<sup>*</sup> | 记录ID *n* ∈ ℤ<sup>+</sup> | 审计上下文已初始化 | *n*<sub>*i*+1</sub> = *n*<sub>*i*</sub> + 1；链式结构扩展 |
| `verify_chain` | 有序记录列表ℛ | (完整性: bool, 断裂索引: ℤ) | ℛ非空 | 当且仅当∀*i*, *h*<sub>*i*</sub>′ = *h*<sub>*i*</sub>时为真 |
| `enforce_worm` | 规范记录*R* ∈ *B*<sup>*</sup> | (偏移量: ℤ, 承诺值: *B*<sup>*λ*</sup>) | 存储后端可写 | 记录已追加并封存 |
| `scan` | LLM输入文本 ∈ UTF-8 | (清洁: bool, 威胁向量: ℤ<sup>*</sup>) | LLMShield词表已加载 | 确定性分类 |

### 确定性保障

1. **比特级精确可复现性：** 所有算术运算均限制在整数集ℤ内。除法仅限于整数向下取整除法。因此，所有算法在x86_64、ARM64及RISC-V架构上均输出比特级一致的结果，满足取证可复现性标准。
2. **时间单调性：** 模块断言每个观测到的整数时间戳满足*τ*<sub>*i*+1</sub> ≥ *τ*<sub>*i*</sub>。若违反则抛出逻辑断裂异常，防止基于时间回放的攻击。
3. **审计不可否认性：** 每个取证工件绑定单调序号*n*<sub>*i*</sub>、载荷摘要与前驱哈希*h*<sub>*i*−1</sub>。该三元组构成自认证的证据对象，除非攻破哈希函数，否则不可抵赖。
4. **速率限制单调性：** 对任意客户端，在区间[0, *t*]内获准的请求累积数有上界*σ* + *ρ*·⌈*t*/*T*⌉，且非递减。拒绝决策具有马尔可夫性：仅依赖当前整数状态向量，与执行历史无关。
5. **衰减幂等性：** 对任意有效*S*，均有`apply_decay`(*S*, 0) = *S*。在零间隔上重复衰减不会改变信任评分。

### 标准合规性

- **Daubert标准（美国联邦证据规则702）：** 本模块所采用的公开整数算法、确定性更新规则及标准哈希原语，提供了已知且可经验测量的误差率（算术层面实际为零，哈希层面受碰撞概率约束）。这满足专家证词所要求的“可复现性”与“普遍接受性”要件。
- **GB/T 29360-2012《电子数据取证通用程序》：** `enforce_worm`与`verify_chain`实现了该标准对原始证据写保护及保管链核验的强制性要求。
- **MLPS 2.0 / GB/T 22239-2019《信息安全技术 网络安全等级保护基本要求》：** `_AdaptiveRateLimiter`的访问控制粒度、`SecurityAudit`的审计轨迹密度，以及`LLMShield`的入侵防御语义，共同满足第三级（监督保护级）与第四级（强制保护级）部署中安全计算环境与安全管理中心的合规要求。

### 关键概念

| 概念 | 说明 | 形式化表示 |
|---|---|---|
| 离散信任衰减 | 在整数纪元上对信任评分进行精确递减 | *S*<sub>*t*+*k*</sub> = ⌊*S*<sub>*t*</sub>·(*N*/*D*)<sup>*k*</sup>⌋ |
| 自适应速率限制 | 基于整数时间量子的令牌桶调控 | *C*′ = min(*σ*, *C* + *ρ*·Δ*τ*) − *κ* |
| WORM强制实施 | 证据存储的仅追加不可变性 | ∀*i*：记录*R*<sub>*i*</sub>在偏移*o*<sub>*i*</sub>提交后不可更改 |
| 哈希链 | 顺序记录之间的密码学链接 | *h*<sub>*i*</sub> = *H*(*h*<sub>*i*−1</sub> ‖ *n*<sub>*i*</sub> ‖ *d*<sub>*i*</sub>) |
| 逻辑断裂 | 密码学、时序或语义连续性中检测到的断裂 | ∃*i* : *h*<sub>*i*</sub>′ ≠ *h*<sub>*i*</sub> |

### 术语表

- **取证工件（取证工件）：** 由`SecurityAudit`生成的结构化自包含数据对象，带有密码学来源证明，可用于取证重建。
- **逻辑断裂（逻辑断裂）：** 在哈希链、时间戳序列或语义过滤器状态中检测到的任何不连续，暗示篡改、时钟操纵或对抗性注入。
- **向下取整除法：** 对整数*a*, *b*（*b* ≠ 0）的数学运算⌊*a*/*b*⌋，产生唯一整数商而无分数余数。
- **WORM：** 一次写入多次读取（Write Once Read Many）；一种存储策略，确保证据记录一旦提交，后续任何操作均不得更改或删除之。
- **有理衰减因子：** 以两个互素整数*N*/*D*表示的精确分数，替代浮点指数函数以保持确定性。
- **令牌桶：** 以速率*ρ*在每个时间量子*T*内累积离散令牌的整数计数器，上限为*σ*，并按请求成本*κ*扣减。

### 【科学说明】

VIGÍA在部分术语中借用了符号学与语言哲学的概念——具体而言，包括查尔斯·桑德斯·皮尔斯（Charles Sanders Peirce）的符号理论、翁贝托·艾柯（Umberto Eco）的编码理论以及赫伯特·保罗·格赖斯（H. Paul Grice）的会话准则。对于从事实证科学的研究者，这些术语应被严格理解为信号处理的形式类比，而非形而上学臆测。皮尔斯的三元关系（再现体—对象—解释项）建模了取证传感器如何将原始物理信号映射到分类符号范畴，这是一种测量认识论，而非神秘主义。艾柯的编码理论描述了限制有效解释空间的协议框架，其功能等同于通信标准对合法分组结构的定义。格赖斯的准则（量、质、关系、方式）则相当于确定性降噪滤波器，拒绝违反预期信息量或清晰度阈值的输入。当`LLMShield`执行语义验证时，它将上述原理作为可计算分类规则应用于整数令牌序列。本模块将自然语言视为可测信号空间；其“解释”是离散字母表上的全函数，完全与物理主义及操作主义认识论相容。

### 相关VIGÍA模块

本模块从`vigia/core/ingest.py`摄取经规范化的取证令牌，后者对输入数据流执行模式验证与整数规范化。`verify_chain`所需的密码学原语由`vigia/chain/integrity.py`提供，该模块提供平台优化的哈希例程，且仅限定位整数位运算。审计记录的持久化序列化委托给`vigia/audit/logger.py`，而物理层面的WORM存储约束则由`vigia/storage/worm.py`在介质层强制执行。`LLMShield`类与`vigia/ml/shield.py`协同生成对抗性测试向量。上述模块共同构成VIGÍA的信任边界与证据生命周期。

**SPDX-License-Identifier: GPL-3.0-or-later**