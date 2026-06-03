## ENGLISH

**1. Module Purpose and Forensic Context**

The `run_stress_tests.py` module, identified by the cryptographic hash `5f1c653e`, functions as the deterministic overload orchestration layer within the VIGÍA forensic platform. Its fundamental purpose is to execute reproducible, boundary-value stress protocols against a designated system under test (SUT) in order to validate computational stability, enforce resource-bound integrity, and verify deterministic response behavior under sustained peak operational load. Unlike conventional stress-testing frameworks that rely on pseudo-random input generation and non-deterministic operating-system scheduling, this module is architected specifically to satisfy forensic admissibility criteria and evidentiary chain-of-custody requirements. Every input sequence is pre-computed and immutable; every state transition is captured in a cryptographically bound log; and every output artifact is linked to its precise execution context through a tamper-evident hash chain. Consequently, the module establishes an auditable, scientifically rigorous demonstration of whether the SUT preserves its safety invariants when subjected to extremal computational demand, producing evidence suitable for both engineering validation and judicial scrutiny.

**2. Mathematical Foundations**

The module models the SUT as a discrete-time dynamical system governed by a state vector $\mathbf{s}(t) \in \mathbb{R}^k$ and subjected to an externally imposed load vector $\mathbf{u}(t) \in \mathcal{U} \subset \mathbb{R}^m$. A stress test case $\mathcal{T}_i$ is formalized as a finite, strictly ordered sequence of load vectors:

$$\mathcal{T}_i = \{\mathbf{u}_i(t_0), \mathbf{u}_i(t_1), \dots, \mathbf{u}_i(t_f)\},$$

where $t_j = t_0 + j\Delta t$ for a fixed sampling interval $\Delta t > 0$. Boundary-value analysis (BVA) mandates that each $\mathbf{u}_i(t_j)$ be selected from the topological boundary $\partial \mathcal{U}$ of the admissible input domain, thereby ensuring that the examination targets worst-case, edge-condition, and saturation scenarios rather than nominal operational modes.

The system response is expressed by the deterministic transition function $\mathcal{F}$:

$$\mathbf{r}_i(t) = \mathcal{F}(\mathbf{s}(t), \mathbf{u}_i(t)),$$

where $\mathbf{r}_i(t) \in \mathbb{R}^n$ denotes the observed response vector. The module enforces a safety envelope $\mathcal{S}_{\text{safe}} \subset \mathbb{R}^n$ defined by a vector-valued invariant function $g: \mathbb{R}^n \to \mathbb{R}^p$ such that:

$$\mathcal{S}_{\text{safe}} = \{\mathbf{r} \in \mathbb{R}^n \mid g(\mathbf{r}) \preceq \mathbf{0}\}.$$

A test case $\mathcal{T}_i$ is adjudicated forensically valid if and only if the response trajectory remains within the safe envelope for the entire test interval:

$$\forall t \in [t_0, t_f], \quad g(\mathbf{r}_i(t)) \preceq \mathbf{0}.$$

Determinism is formalized as an equivalence relation over execution traces. Let $\epsilon_1$ and $\epsilon_2$ denote two independent executions of the module against identical initial states $\mathbf{s}(t_0)$ and identical test matrices $\mathcal{M} = \{\mathcal{T}_1, \dots, \mathcal{T}_N\}$. The module guarantees bitwise reproducibility of the complete response tensor $\mathcal{R} = [\mathbf{r}_i(t_j)]_{N \times (f+1)}$:

$$\mathcal{R}^{(\epsilon_1)} \equiv \mathcal{R}^{(\epsilon_2)} \iff H_{\text{SHA-256}}(\text{serialize}(\mathcal{R}^{(\epsilon_1)})) = H_{\text{SHA-256}}(\text{serialize}(\mathcal{R}^{(\epsilon_2)})),$$

where $H_{\text{SHA-256}}$ denotes the cryptographically secure hash function and $\text{serialize}$ represents the canonical byte-order serialization routine. This equivalence excludes entropy-driven divergence and constitutes the mathematical core of the module’s forensic guarantee.

**3. Algorithm Description**

The algorithm executes through six strictly sequential phases, each designed to eliminate non-deterministic variance:

*Phase 1: Environmental Lockdown.* The module invokes `vigia.scheduler.deterministic_runner` to bind execution threads to specific CPU cores via affinity masks, neutralize address-space layout randomization (ASLR) effects within the test harness, and standardize memory allocator behavior. All operating-system entropy sources that could influence thread scheduling, file descriptor allocation, or timing jitter are explicitly bypassed. The pseudo-random number generator (PRNG) subsystem is de-initialized and sealed; no stochastic sampling or Monte Carlo iteration is employed at any stage.

*Phase 2: Test Matrix Ingestion.* The boundary-value test matrix $\mathcal{M}$ is loaded from the `vigia.validation.boundary_engine` submodule. Prior to execution, a cryptographic checksum $C_{\mathcal{M}} = H_{\text{SHA-256}}(\mathcal{M})$ is computed and irrevocably recorded in the audit preamble of the evidentiary log.

*Phase 3: Sequential Load Application.* For each test case $\mathcal{T}_i \in \mathcal{M}$, the module applies the load sequence monotonically from a defined baseline $\mathbf{u}_{\min}$ to a specified peak $\mathbf{u}_{\max}$. At each discrete time step $t_j$, the module samples a response vector $\mathbf{r}_i(t_j)$ comprising CPU utilization $\rho_{\text{CPU}}$, resident set size $M_{\text{RSS}}$, block I/O throughput $\Phi_{\text{IO}}$, and inter-process communication latency $\delta_{\text{LAT}}$. Sampling is performed via deterministic kernel probes with a fixed clock source to eliminate timer variance.

*Phase 4: Invariant Verification.* The module evaluates the invariant function $g(\mathbf{r}_i(t_j))$ component-wise. Should any scalar component exceed its corresponding safety threshold, a forensic event $E_i$ is instantiated. The event record contains the violating state snapshot $\mathbf{r}_i(t_j)$, the precipitating load vector $\mathbf{u}_i(t_j)$, the monotonic sequence index, and a high-resolution timestamp relative to $t_0$. Execution proceeds through the entire matrix; early termination is prohibited to prevent masking of compound failure modes.

*Phase 5: Cryptographic Logging.* All response vectors $\mathbf{r}_i(t_j)$ and forensic events $E_i$ are appended to an immutable evidence log $\mathcal{L}$ managed by `vigia.core.audit_logger`. The log is structured as a cryptographic hash chain:

$$H_k = H_{\text{SHA-256}}(H_{k-1} \parallel \mathcal{L}_k),$$

with the genesis hash $H_0$ initialized to the module identifier `5f1c653e`. This construction renders any retrospective modification of $\mathcal{L}$ computationally infeasible and immediately detectable through hash root mismatch.

*Phase 6: Report Compilation and Serialization.* The module invokes `vigia.report.compiler` to aggregate the response tensor, invariant adjudications, and forensic events. By default, a human-readable forensic narrative is emitted to standard output (stdout), presenting boundary values, peak responses, and pass/fail determinations in tabular form. If the operator specifies the `--json` flag, the module serializes output according to the VIGÍA Evidence Schema v2.1, producing a machine-parseable JSON object that includes the hash chain root $H_K$, the test matrix checksum $C_{\mathcal{M}}$, the canonical serialized response tensor, and a bitwise-reproducible report digest $D_{\text{report}}$.

**4. Input/Output Specifications**

*Inputs:* The module exposes a command-line interface (CLI) defined as `python run_stress_tests.py [--json] [--config PATH] [--output-dir DIR]`. The optional `--config` argument specifies a YAML or JSON configuration file declaring the admissible input domain $\mathcal{U}$, the sampling interval $\Delta t$, the peak hold duration $\tau$, and the threshold parameters for $g(\mathbf{r})$. Environmental baseline parameters—such as CPU affinity masks and memory control groups—may be injected through `vigia.scheduler.deterministic_runner`.

*Outputs:* Standard output (stdout) delivers a human-readable narrative suitable for expert review. When `--json` is present, the output conforms to a strict schema containing: (i) `metadata` with module hash, execution timestamp, and checksums; (ii) `test_matrix` enumerating boundary values; (iii) `results` as time-series arrays of $\mathbf{r}_i(t_j)$; and (iv) `forensic_events` detailing any invariant violations. As a side effect, immutable log segments are committed to `vigia.storage.evidence_vault` under write-once-read-many (WORM) semantics.

**5. Deterministic Guarantees and Traceability**

The module enforces four principal deterministic guarantees essential to forensic validity:

1. **Entropy Exclusion:** No PRNG, hardware random number generator, environmental noise sampler, or stochastic algorithm is invoked during the execution window. All input sequences are statically defined within $\mathcal{M}$.
2. **Bitwise Reproducibility:** Under identical initial conditions and SUT configurations, the serialized output byte streams of any two executions are bit-identical, as proven by the hash equivalence theorem stated in Section 2.
3. **Idempotence:** Re-execution of the module against an unmodified SUT yields bitwise-identical adjudications and response tensors, enabling longitudinal audit cycles without test-harness drift.
4. **Cryptographic Traceability:** Every logged datum is cryptographically bound to the module hash `5f1c653e` and the final hash chain root $H_K$, permitting independent auditors to verify evidentiary provenance using only the canonical VIGÍA toolchain.

**6. Integration with the VIGÍA Ecosystem**

The module is not operable as an isolated component; it relies upon a formally defined ecosystem of peer modules:

- `vigia.validation.boundary_engine`: Generates and verifies the mathematical correctness of boundary-value pairs prior to ingestion.
- `vigia.scheduler.deterministic_runner`: Enforces deterministic process scheduling, CPU affinity, and isolation from asynchronous system interrupts.
- `vigia.core.audit_logger`: Provides tamper-evident, append-only logging primitives with temporal ordering guarantees.
- `vigia.crypto.hash_chain`: Implements the Merkle-Damgård-style cryptographic chaining of evidence records.
- `vigia.report.compiler`: Transforms raw response tensors into human-readable or machine-parseable forensic reports.
- `vigia.storage.evidence_vault`: Persists evidence logs with cryptographic integrity checks and WORM storage semantics.

**7. Standards Compliance**

The design and operation of `run_stress_tests.py` directly align with internationally recognized forensic and quality standards:

- **Daubert Standard (FRE 702):** The module’s deterministic protocol, empirically testable error rate (determined solely by the SUT, not the harness), known and controllable methodology, and general acceptance of boundary-value analysis in software reliability engineering satisfy the Daubert factors governing the admissibility of scientific expert testimony.
- **GB/T 29360-2012 (Electronic Data Forensic Examination Procedures):** The module’s hash-chained logging, immutable storage, and documented chain-of-custody mechanisms satisfy Chinese national requirements for the preservation of original electronic evidence and forensic examination documentation.
- **GB/T 25000.51-2016 (Systems and Software Quality Requirements and Evaluation — SQuaRE):** The module directly validates the SUT’s performance efficiency and reliability characteristics under specified stress conditions, conforming to product-quality evaluation criteria for ready-to-use software.
- **MLPS 2.0 (Multi-Level Protection Scheme 2.0):** The module satisfies Level 3 operational assurance requirements by providing secure audit trails, deterministic test coverage, and tamper-evident evidence storage within the security computing environment.

**8. Conclusion**

`run_stress_tests.py` (hash `5f1c653e`) constitutes a formally rigorous, forensically sound instrument for deterministic stress validation within the VIGÍA architecture. By mathematically grounding its operation in boundary-value theory, excluding all sources of computational stochasticity, and integrating deeply with tamper-evident logging and storage infrastructure, the module produces evidence that is simultaneously suitable for high-assurance systems engineering and for presentation in judicial proceedings requiring demonstrable scientific validity.

## ESPAÑOL

**1. Propósito del módulo y contexto forense**

El módulo `run_stress_tests.py`, identificado mediante el hash criptográfico `5f1c653e`, funciona como la capa de orquestación de sobrecarga determinista dentro de la plataforma forense VIGÍA. Su propósito fundamental consiste en ejecutar protocolos de estrés de valores límite, reproducibles y auditables, contra un sistema bajo prueba (SUT) para validar su estabilidad computacional, hacer cumplir la integridad de los recursos acotados y verificar el comportamiento determinista de respuesta bajo carga operativa máxima sostenida. A diferencia de los marcos de prueba de estrés convencionales que dependen de generación de entrada pseudoaleatoria y planificación no determinista por parte del sistema operativo, este módulo está arquitectado específicamente para satisfacer criterios de admisibilidad forense y requisitos de cadena de custodia de evidencias. Cada secuencia de entrada se encuentra precomputada e inmutable; cada transición de estado se captura en un registro criptográficamente vinculado; y cada artefacto de salida se enlaza con su contexto de ejecución preciso mediante una cadena de hash inviolable. En consecuencia, el módulo establece una demostración científicamente rigurosa y auditable de si el SUT preserva sus invariantes de seguridad cuando se lo somete a demanda computacional extrema, produciendo evidencia apta tanto para validación de ingeniería como para escrutinio judicial.

**2. Fundamentos matemáticos**

El módulo modela el SUT como un sistema dinámico de tiempo discreto gobernado por un vector de estado $\mathbf{s}(t) \in \mathbb{R}^k$ y sometido a un vector de carga externa $\mathbf{u}(t) \in \mathcal{U} \subset \mathbb{R}^m$. Un caso de prueba de estrés $\mathcal{T}_i$ se formaliza como una secuencia finita y estrictamente ordenada de vectores de carga:

$$\mathcal{T}_i = \{\mathbf{u}_i(t_0), \mathbf{u}_i(t_1), \dots, \mathbf{u}_i(t_f)\},$$

donde $t_j = t_0 + j\Delta t$ para un intervalo de muestreo fijo $\Delta t > 0$. El análisis de valores límite (BVA) exige que cada $\mathbf{u}_i(t_j)$ se seleccione desde la frontera topológica $\partial \mathcal{U}$ del dominio de entrada admisible, asegurando así que el examen apunte a escenarios de peor caso, condiciones de borde y saturación, en lugar de modos operativos nominales.

La respuesta del sistema se expresa mediante la función de transición determinista $\mathcal{F}$:

$$\mathbf{r}_i(t) = \mathcal{F}(\mathbf{s}(t), \mathbf{u}_i(t)),$$

donde $\mathbf{r}_i(t) \in \mathbb{R}^n$ denota el vector de respuesta observado. El módulo impone un sobre de seguridad $\mathcal{S}_{\text{safe}} \subset \mathbb{R}^n$ definido por una función invariante vectorial $g: \mathbb{R}^n \to \mathbb{R}^p$ tal que:

$$\mathcal{S}_{\text{safe}} = \{\mathbf{r} \in \mathbb{R}^n \mid g(\mathbf{r}) \preceq \mathbf{0}\}.$$

Un caso de prueba $\mathcal{T}_i$ se adjudica forensemente válido si y solo si la trayectoria de respuesta permanece dentro del sobre seguro durante todo el intervalo de prueba:

$$\forall t \in [t_0, t_f], \quad g(\mathbf{r}_i(t)) \preceq \mathbf{0}.$$

El determinismo se formaliza como una relación de equivalencia sobre trazas de ejecución. Sean $\epsilon_1$ y $\epsilon_2$ dos ejecuciones independientes del módulo contra estados iniciales idénticos $\mathbf{s}(t_0)$ y matrices de prueba idénticas $\mathcal{M} = \{\mathcal{T}_1, \dots, \mathcal{T}_N\}$. El módulo garantiza la reproducibilidad bit a bit del tensor de respuesta completo $\mathcal{R} = [\mathbf{r}_i(t_j)]_{N \times (f+1)}$:

$$\mathcal{R}^{(\epsilon_1)} \equiv \mathcal{R}^{(\epsilon_2)} \iff H_{\text{SHA-256}}(\text{serializar}(\mathcal{R}^{(\epsilon_1)})) = H_{\text{SHA-256}}(\text{serializar}(\mathcal{R}^{(\epsilon_2)})),$$

donde $H_{\text{SHA-256}}$ denota la función hash criptográficamente segura y $\text{serializar}$ representa la rutina canónica de serialización en orden de bytes. Esta equivalencia excluye la divergencia impulsada por entropía y constituye el núcleo matemático de la garantía forense del módulo.

**3. Descripción del algoritmo**

El algoritmo se ejecuta en seis fases estrictamente secuenciales, cada una diseñada para eliminar la varianza no determinista:

*Fase 1: Bloqueo ambiental.* El módulo invoca a `vigia.scheduler.deterministic_runner` para vincular los hilos de ejecución a núcleos específicos de CPU mediante máscaras de afinidad, neutralizar los efectos de la aleatorización del diseño del espacio de direcciones (ASLR) dentro del *harness* de prueba y estandarizar el comportamiento del asignador de memoria. Todas las fuentes de entropía del sistema operativo que podrían influir en la planificación de hilos, la asignación de descriptores de archivos o la fluctuación de tiempos se evaden explícitamente. El subsistema de generador de números pseudoaleatorios (PRNG) se desinicializa y sella; no se emplea muestreo estocástico ni iteración de Monte Carlo en ninguna etapa.

*Fase 2: Ingesta de la matriz de prueba.* La matriz de prueba de valores límite $\mathcal{M}$ se carga desde el submódulo `vigia.validation.boundary_engine`. Antes de la ejecución, se computa una suma de verificación criptográfica $C_{\mathcal{M}} = H_{\text{SHA-256}}(\mathcal{M})$ y se registra de manera irrevocable en el preámbulo de auditoría del registro de evidencias.

*Fase 3: Aplicación secuencial de carga.* Para cada caso de prueba $\mathcal{T}_i \in \mathcal{M}$, el módulo aplica la secuencia de carga de forma monótona desde una línea base definida $\mathbf{u}_{\min}$ hasta un pico especificado $\mathbf{u}_{\max}$. En cada paso de tiempo discreto $t_j$, el módulo muestrea un vector de respuesta $\mathbf{r}_i(t_j)$ que comprende la utilización de CPU $\rho_{\text{CPU}}$, el tamaño del conjunto residente $M_{\text{RSS}}$, el throughput de E/S por bloques $\Phi_{\text{IO}}$ y la latencia de comunicación entre procesos $\delta_{\text{LAT}}$. El muestreo se realiza mediante sondas deterministas del *kernel* con una fuente de reloj fija para eliminar la varianza del temporizador.

*Fase 4: Verificación de invariantes.* El módulo evalúa la función invariante $g(\mathbf{r}_i(t_j))$ componente por componente. Si algún componente escalar excede el umbral de seguridad correspondiente, se instancia un evento forense $E_i$. El registro del evento contiene la instantánea del estado violador $\mathbf{r}_i(t_j)$, el vector de carga precipitante $\mathbf{u}_i(t_j)$, el índice de secuencia monótono y una marca de tiempo de alta resolución relativa a $t_0$. La ejecución procede a través de toda la matriz; se prohíbe la terminación anticipada para evitar enmascarar modos de falla compuestos.

*Fase 5: Registro criptográfico.* Todos los vectores de respuesta $\mathbf{r}_i(t_j)$ y los eventos forenses $E_i$ se agregan a un registro de evidencias inmutable $\mathcal{L}$ gestionado por `vigia.core.audit_logger`. El registro se estructura como una cadena de hash criptográfico:

$$H_k = H_{\text{SHA-256}}(H_{k-1} \parallel \mathcal{L}_k),$$

con el hash de génesis $H_0$ inicializado al identificador del módulo `5f1c653e`. Esta construcción hace que cualquier modificación retrospectiva de $\mathcal{L}$ sea computacionalmente inviable e inmediatamente detectable mediante la discrepancia de la raíz de hash.

*Fase 6: Compilación y serialización del informe.* El módulo invoca a `vigia.report.compiler` para agregar el tensor de respuesta, las adjudicaciones de invariantes y los eventos forenses. De manera predeterminada, se emite una narrativa forense legible por humanos en la salida estándar (stdout), presentando valores límite, respuestas pico y determinaciones de aprobación/rechazo en forma tabular. Si especificás el flag `--json`, el módulo serializa la salida de acuerdo con el Esquema de Evidencias VIGÍA v2.1, produciendo un objeto JSON analizable por máquina que incluye la raíz de la cadena de hash $H_K$, la suma de verificación de la matriz de prueba $C_{\mathcal{M}}$, el tensor de respuesta serializado canónicamente y un digesto de informe reproducible bit a bit $D_{\text{report}}$.

**4. Especificaciones de entrada y salida**

*Entradas:* El módulo expone una interfaz de línea de comandos (CLI) definida como `python run_stress_tests.py [--json] [--config RUTA] [--output-dir DIRECTORIO]`. El argumento opcional `--config` especifica un archivo de configuración en YAML o JSON que declara el dominio de entrada admisible $\mathcal{U}$, el intervalo de muestreo $\Delta t$, la duración de sostenimiento del pico $\tau$ y los parámetros de umbral para $g(\mathbf{r})$. Los parámetros de línea base ambiental —tales como máscaras de afinidad de CPU y grupos de control de memoria— podés inyectar a través de `vigia.scheduler.deterministic_runner`.

*Salidas:* La salida estándar (stdout) entrega una narrativa legible por humanos apta para revisión experta. Cuando está presente `--json`, la salida se ajusta a un esquema estricto que contiene: (i) `metadata` con el hash del módulo, la marca de tiempo de ejecución y las sumas de verificación; (ii) `test_matrix` enumerando los valores límite; (iii) `results` como arreglos de series temporales de $\mathbf{r}_i(t_j)$; y (iv) `forensic_events` detallando cualquier violación de invariantes. Como efecto colateral, los segmentos de registro inmutables se comprometen en `vigia.storage.evidence_vault` bajo semántica de escritura-única-lectura-múltiple (WORM).

**5. Garantías deterministas y trazabilidad**

El módulo impone cuatro garantías deterministas principales esenciales para la validez forense:

1. **Exclusión de entropía:** No se invoca ningún PRNG, generador de números aleatorios por hardware, muestreador de ruido ambiental ni algoritmo estocástico durante la ventana de ejecución. Todas las secuencias de entrada se definen estáticamente dentro de $\mathcal{M}$.
2. **Reproducibilidad bit a bit:** Bajo condiciones iniciales idénticas y configuraciones de SUT idénticas, los flujos de bytes serializados de salida de dos ejecuciones cualesquiera son idénticos bit a bit, como lo demuestra el teorema de equivalencia de hash enunciado en la Sección 2.
3. **Idempotencia:** La reejecución del módulo contra un SUT no modificado produce adjudicaciones y tensores de respuesta idénticos bit a bit, permitiendo ciclos de auditoría longitudinal sin deriva del *harness* de prueba.
4. **Trazabilidad criptográfica:** Cada dato registrado se vincula criptográficamente al hash del módulo `5f1c653e` y a la raíz final de la cadena de hash $H_K$, permitiendo que auditores independientes verifiquen la procedencia de la evidencia utilizando únicamente la cadena de herramientas canónica de VIGÍA.

**6. Integración con el ecosistema VIGÍA**

El módulo no es operable como componente aislado; depende de un ecosistema de módulos pares formalmente definido:

- `vigia.validation.boundary_engine`: Genera y verifica la corrección matemática de los pares de valores límite antes de la ingesta.
- `vigia.scheduler.deterministic_runner`: Impone planificación determinista de procesos, afinidad de CPU y aislamiento de interrupciones del sistema asincrónicas.
- `vigia.core.audit_logger`: Provee primitivas de registro de solo agregado e inviolable con garantías de orden temporal.
- `vigia.crypto.hash_chain`: Implementa el encadenamiento criptográfico de registros de evidencias al estilo Merkle-Damgård.
- `vigia.report.compiler`: Transforma los tensores de respuesta crudos en informes forenses legibles por humanos o analizables por máquinas.
- `vigia.storage.evidence_vault`: Persiste los registros de evidencias con verificaciones de integridad criptográfica y semántica de almacenamiento WORM.

**7. Conformidad con estándares**

El diseño y la operación de `run_stress_tests.py` se alinean directamente con estándares forenses y de calidad reconocidos internacionalmente:

- **Estándar Daubert (FRE 702):** El protocolo determinista del módulo, su tasa de error empíricamente comprobable (determinada exclusivamente por el SUT, no por el *harness*), su metodología conocida y controlable, y la aceptación general del análisis de valores límite en la ingeniería de confiabilidad de software satisfacen los factores Daubert que rigen la admisibilidad del testimonio pericial científico.
- **GB/T 29360-2012 (Procedimientos de Examen Forense de Datos Electrónicos):** Los registros encadenados por hash, el almacenamiento inmutable y los mecanismos documentados de cadena de custodia del módulo satisfacen los requisitos nacionales chinos para la preservación de evidencia electrónica original y la documentación de exámenes forenses.
- **GB/T 25000.51-2016 (Requisitos y Evaluación de Calidad de Sistemas y Software — SQuaRE):** El módulo valida directamente las características de eficiencia de rendimiento y confiabilidad del SUT bajo condiciones de estrés especificadas, conformando a los criterios de evaluación de calidad de producto para software listo para usar.
- **MLPS 2.0 (Esquema de Protección Multinivel 2.0):** El módulo satisface los requisitos de garantía operativa de Nivel 3 al proporcionar auditorías seguras, cobertura de prueba determinista y almacenamiento de evidencias inviolable dentro del entorno de computación seguro.

**8. Conclusión**

`run_stress_tests.py` (hash `5f1c653e`) constituye un instrumento formalmente riguroso y forensemente sólido para la validación determinista de estrés dentro de la arquitectura VIGÍA. Al fundamentar matemáticamente su operación en la teoría de valores límite, excluir todas las fuentes de estocasticidad computacional e integrarse profundamente con infraestructura de registro y almacenamiento inviolable, el módulo produce evidencia que resulta simultáneamente apta para la ingeniería de sistemas de alta garantía y para la presentación en procedimientos judiciales que exigen validez científica demostrable.

## РУССКИЙ

**1. Назначение модуля и судебный контекст**

Модуль `run_stress_tests.py`, идентифицируемый криптографическим хешем `5f1c653e`, функционирует в качестве слоя оркестрации детерминированных протоколов перегрузки в составе судебно-экспертной платформы VIGÍA. Его основное предназначение заключается в выполнении воспроизводимых протоколов стресс-тестирования на основе граничных значений по отношению к тестируемой системе (ТС) с целью проверки вычислительной стабильности, обеспечения целостности ресурсных ограничений и верификации детерминированного поведения откликов при длительной пиковой операционной нагрузке. В отличие от традиционных средств стресс-тестирования, полагающихся на псевдослучайную генерацию входных данных и недетерминированное планирование операционной системой, данный модуль спроектирован с учётом критериев судебной допустимости и требований к сохранению цепочки хранения доказательств. Каждая входная последовательность является предварительно вычисленной и неизменяемой; каждый переход состояния фиксируется в криптографически связанном журнале; каждый выходной артефакт привязывается к точному контексту исполнения посредством нарушаемой хеш-цепочки. Следовательно, модуль формирует поддающуюся аудиту и научно строгую демонстрацию того, сохраняет ли ТС свои инварианты безопасности при воздействии экстремальной вычислительной нагрузки, производя доказательства, пригодные как для инженерной валидации, так и для судебного рассмотрения.

**2. Математические основания**

Модель ТС в рамках модуля представлена как дискретная динамическая система, управляемая вектором состояния $\mathbf{s}(t) \in \mathbb{R}^k$ и подвергаемая воздействию внешнего вектора нагрузки $\mathbf{u}(t) \in \mathcal{U} \subset \mathbb{R}^m$. Стресс-тестовый случай $\mathcal{T}_i$ формализуется как конечная строго упорядоченная последовательность векторов нагрузки:

$$\mathcal{T}_i = \{\mathbf{u}_i(t_0), \mathbf{u}_i(t_1), \dots, \mathbf{u}_i(t_f)\},$$

где $t_j = t_0 + j\Delta t$ при фиксированном интервале дискретизации $\Delta t > 0$. Граничный анализ значений (ГАЗ) требует, чтобы каждый вектор $\mathbf{u}_i(t_j)$ выбирался из топологической границы $\partial \mathcal{U}$ допустимой области входных данных, обеспечивая тем самым исследование наихудших случаев, краевых условий и сценариев насыщения, а не номинальных режимов функционирования.

Отклик системы выражается детерминированной функцией перехода $\mathcal{F}$:

$$\mathbf{r}_i(t) = \mathcal{F}(\mathbf{s}(t), \mathbf{u}_i(t)),$$

где $\mathbf{r}_i(t) \in \mathbb{R}^n$ обозначает наблюдаемый вектор отклика. Модуль обеспечивает соблюдение области безопасности $\mathcal{S}_{\text{safe}} \subset \mathbb{R}^n$, определяемой вектор-значной функцией инвариантов $g: \mathbb{R}^n \to \mathbb{R}^p$ таким образом, что:

$$\mathcal{S}_{\text{safe}} = \{\mathbf{r} \in \mathbb{R}^n \mid g(\mathbf{r}) \preceq \mathbf{0}\}.$$

Тестовый случай $\mathcal{T}_i$ признаётся судебно значимым тогда и только тогда, когда траектория отклика остаётся внутри безопасной области на протяжении всего тестового интервала:

$$\forall t \in [t_0, t_f], \quad g(\mathbf{r}_i(t)) \preceq \mathbf{0}.$$

Детерминизм формализуется как отношение эквивалентности над трассами исполнения. Пусть $\epsilon_1$ и $\epsilon_2$ обозначают два независимых исполнения модуля при идентичных начальных состояниях $\mathbf{s}(t_0)$ и идентичных тестовых матрицах $\mathcal{M} = \{\mathcal{T}_1, \dots, \mathcal{T}_N\}$. Модуль гарантирует побитовую воспроизводимость полного тензора откликов $\mathcal{R} = [\mathbf{r}_i(t_j)]_{N \times (f+1)}$:

$$\mathcal{R}^{(\epsilon_1)} \equiv \mathcal{R}^{(\epsilon_2)} \iff H_{\text{SHA-256}}(\text{сериализовать}(\mathcal{R}^{(\epsilon_1)})) = H_{\text{SHA-256}}(\text{сериализовать}(\mathcal{R}^{(\epsilon_2)})),$$

где $H_{\text{SHA-256}}$ — криптографически стойкая хеш-функция, а $\text{сериализовать}$ представляет собой каноническую процедуру байтовой сериализации. Данная эквивалентность исключает расхождение, обусловленное энтропией, и составляет математическое ядро судебной гарантии модуля.

**3. Описание алгоритма**

Алгоритм реализуется в шесть строго последовательных фаз, каждая из которых предназначена для устранения недетерминированной вариативности:

*Фаза 1: Блокировка среды исполнения.* Модуль вызывает `vigia.scheduler.deterministic_runner` для привязки потоков исполнения к конкретным ядрам ЦП посредством масок аффинности, нейтрализации эффектов рандомизации размещения адресного пространства (ASLR) внутри тестового каркаса и стандартизации поведения распределителя памяти. Все источники энтропии операционной системы, способные повлиять на планирование потоков, выделение дескрипторов файлов или джиттер временных меток, явным образом обходятся. Подсистема псевдослучайного генератора чисел (ПСГЧ) деинициализируется и запечатывается; на каком-либо этапе не применяется стохастическое сэмплирование или итерация по методу Монте-Карло.

*Фаза 2: Загрузка тестовой матрицы.* Граничная тестовая матрица $\mathcal{M}$ загружается из подмодуля `vigia.validation.boundary_engine`. Перед началом исполнения вычисляется и безвозвратно регистрируется в аудиторском предисловии журнала доказательств криптографическая контрольная сумма $C_{\mathcal{M}} = H_{\text{SHA-256}}(\mathcal{M})$.

*Фаза 3: Последовательное приложение нагрузки.* Для каждого тестового случая $\mathcal{T}_i \in \mathcal{M}$ модуль монотонно приложеняет последовательность нагрузки от определённого базового уровня $\mathbf{u}_{\min}$ до заданного пика $\mathbf{u}_{\max}$. На каждом дискретном временном шаге $t_j$ модуль производит выборку вектора отклика $\mathbf{r}_i(t_j)$, включающего загрузку ЦП $\rho_{\text{CPU}}$, резидентный размер памяти $M_{\text{RSS}}$, пропускную способность блочного ввода-вывода $\Phi_{\text{IO}}$ и задержку межпроцессного взаимодействия $\delta_{\text{LAT}}$. Выборка осуществляется детерминированными зондами ядра с фиксированным источником тактовых импульсов с целью исключения вариативности таймера.

*Фаза 4: Проверка инвариантов.* Модуль поэлементно вычисляет функцию инвариантов $g(\mathbf{r}_i(t_j))$. При превышении каким-либо скалярным компонентом соответствующего порога безопасности формируется судебное событие $E_i$. Запись события содержит снимок нарушающего состояния $\mathbf{r}_i(t_j)$, спровоцировавший вектор нагрузки $\mathbf{u}_i(t_j)$, монотонный индекс последовательности и высокоразрешенную временную метку относительно $t_0$. Исполнение продолжается по всей матрице; досрочное прерывание запрещено во избежание маскировки составных режимов отказа.

*Фаза 5: Криптографическое журналирование.* Все векторы откликов $\mathbf{r}_i(t_j)$ и судебные события $E_i$ добавляются в неизменяемый журнал доказательств $\mathcal{L}$, управляемый модулем `vigia.core.audit_logger`. Журнал структурирован в виде криптографической хеш-цепочки:

$$H_k = H_{\text{SHA-256}}(H_{k-1} \parallel \mathcal{L}_k),$$

причём начальный хеш $H_0$ инициализируется идентификатором модуля `5f1c653e`. Данная конструкция делает любую ретроспективную модификацию $\mathcal{L}$ вычислительно неосуществимой и немедленно обнаружимой посредством несоответствия корневого хеша.

*Фаза 6: Компиляция и сериализация отчёта.* Модуль вызывает `vigia.report.compiler` для агрегирования тензора откликов, результатов проверки инвариантов и судебных событий. По умолчанию в стандартный вывод (stdout) направляется удобочитаемая судебная экспертная сводка, представляющая граничные значения, пиковые отклики и заключения о соответствии/несоответствии в табличной форме. При указании флага `--json` модуль сериализует выходные данные в соответствии со Схемой Доказательств VIGÍA v2.1, формируя машинно-анализируемый JSON-объект, включающий корневой хеш цепочки $H_K$, контрольную сумму тестовой матрицы $C_{\mathcal{M}}$, канонически сериализованный тензор откликов и побитово воспроизводимый дайджест отчёта $D_{\text{report}}$.

**4. Спецификации входных и выходных данных**

*Входные данные:* Модуль предоставляет интерфейс командной строки (CLI), определяемый как `python run_stress_tests.py [--json] [--config ПУТЬ] [--output-dir КАТАЛОГ]`. Необязательный аргумент `--config` задаёт файл конфигурации в формате YAML или JSON, декларирующий допустимую область входных данных $\mathcal{U}$, интервал дискретизации $\Delta t$, длительность удержания пиковой нагрузки $\tau$ и параметры порогов для функции $g(\mathbf{r})$. Базовые параметры среды исполнения — такие как маски аффинности ЦП и группы управления памятью — могут подаваться через `vigia.scheduler.deterministic_runner`.

*Выходные данные:* Стандартный вывод (stdout) обеспечивает подачу удобочитаемой экспертной сводки. При наличии флага `--json` выходные данные строго соответствуют схеме, содержащей: (i) раздел `metadata` с хешем модуля, временной меткой исполнения и контрольными суммами; (ii) раздел `test_matrix` с перечислением граничных значений; (iii) раздел `results` в виде временных рядов массивов $\mathbf{r}_i(t_j)$; и (iv) раздел `forensic_events` с детализацией любых нарушений инвариантов. В качестве побочного эффекта неизменяемые сегменты журнала фиксируются в `vigia.storage.evidence_vault` с семантикой однократной записи и многократного чтения (WORM).

**5. Детерминированные гарантии и прослеживаемость**

Модуль обеспечивает четыре основные детерминированные гарантии, необходимые для судебной значимости:

1. **Исключение энтропии:** В течение окна исполнения не вызываются ПСГЧ, аппаратные генераторы случайных чисел, сэмплеры окружающего шума и стохастические алгоритмы. Все входные последовательности статически определены внутри $\mathcal{M}$.
2. **Побитовая воспроизводимость:** При идентичных начальных условиях и конфигурациях ТС сериализованные выходные байтовые потоки любых двух исполнений побитово идентичны, что доказано теоремой эквивалентности хешей, изложенной в разделе 2.
3. **Идемпотентность:** Повторное исполнение модуля по отношению к немодифицированной ТС даёт побитово идентичные результаты проверки и тензоры откликов, позволяя проводить продольные аудиторские циклы без дрейфа тестового каркаса.
4. **Криптографическая прослеживаемость:** Каждая зарегистрированная порция данных криптографически привязана к хешу модуля `5f1c653e` и конечному корневому хешу цепочки $H_K$, что позволяет независимым аудиторам верифицировать происхождение доказательств, используя