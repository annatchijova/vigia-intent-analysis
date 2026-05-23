---
doc_hash: 845ea393
module: vigia/sandbox.py
languages: [EN, ES, RU]
generated_by: moonshot-kimi-k2.6-batch-api
license: Apache-2.0
---

## ENGLISH

### 1. Module Purpose and Architectural Positioning
`vigia/sandbox.py` constitutes a deterministic, self-contained execution substrate within the VIGÍA digital-forensic framework. Its primary function is to instantiate, constrain, and monitor external operating-system processes—such as pattern-matching engines, file-carving utilities, and metadata extractors—under strictly quantified and immutable resource ceilings. The module was architected to replace the orphaned dependency `vigia.security.sandbox`, achieving full functional parity while eliminating third-party supply-chain risk by relying exclusively on the Python 3 standard library (`asyncio`, `subprocess`, `resource`). Within the VIGÍA pipeline topology, this module occupies the critical boundary between the high-level orchestration plane (`vigia.pipeline.orchestrator`) and unmanaged third-party binaries, serving as a compulsory mediation gateway that forecloses unbounded resource consumption, filesystem escape, and runaway computation during evidence processing.

### 2. Mathematical Foundations and Resource Model
Let the resource-bound vector be formally defined as $\mathbf{r} = (r_{\text{as}}, r_{\text{cpu}}, r_{\text{fsize}}, r_{\text{nproc}}) \in \mathbb{Z}_{\geq 0}^4$, where:
- $r_{\text{as}}$ denotes the maximum virtual address-space size in bytes, mapped to POSIX `RLIMIT_AS`;
- $r_{\text{cpu}}$ denotes the aggregate CPU-time limit in seconds, mapped to `RLIMIT_CPU`;
- $r_{\text{fsize}}$ denotes the maximum output file size in bytes, mapped to `RLIMIT_FSIZE`;
- $r_{\text{nproc}}$ denotes the maximum number of child processes, mapped to `RLIMIT_NPROC`.

The enforcement mechanism is modeled as a kernel-level hard-constraint function:
$$\Phi: \mathbb{Z}_{\geq 0}^4 \to \mathcal{P}, \quad \Phi(\mathbf{r}) = p_{\text{constrained}}$$
where $\mathcal{P}$ represents the space of feasible process configurations. Under POSIX.1-2008, the `setrlimit` system call establishes immutable ceilings such that for any resource-acquisition attempt $a_i$ by the sandboxed child process in dimension $i$:
$$\text{if } a_i > r_i \text{ then the kernel delivers signal } \sigma_i \text{ to } p_{\text{constrained}}$$
with $\sigma_{\text{as}} = \text{SIGKILL}$ (memory exhaustion), $\sigma_{\text{cpu}} = \text{SIGXCPU}$ (CPU exhaustion), and $\sigma_{\text{fsize}} = \text{SIGXFSZ}$ (file-size exhaustion). The module guarantees that all components of $\mathbf{r}$ are exact non-negative integers, satisfying:
$$\forall i \in \{1,2,3,4\}, \quad r_i \in \mathbb{N}_0, \quad \nexists \epsilon \in \mathbb{R}\setminus\mathbb{Q} : r_i = \lfloor r_i \rfloor + \epsilon$$
This deliberate exclusion of floating-point representation in the enforcement logic eliminates rounding-induced non-determinism and guarantees bitwise-identical limit semantics across repeated invocations.

Process isolation is formalized through strict address-space separation. Given a host forensic process $P_h$ and a sandboxed child $P_c$, the module ensures:
$$\text{Addr}(P_c) \cap \text{Addr}(P_h) = \emptyset \quad \text{except for kernel-mediated IPC channels}$$
where $\text{Addr}(\cdot)$ denotes the set of mapped virtual-memory pages. This separation is guaranteed by the operating-system kernel's copy-on-write (`COW`) semantics during the `fork()`–`exec()` sequence, as mediated by Python's `subprocess` module.

### 3. Algorithmic Description
The module exposes two principal operational modalities: (a) generic sandboxed subprocess execution, and (b) resource-bound asynchronous pattern search.

**Algorithm 1: Sandboxed Subprocess Execution**
*Input:* Absolute executable path $e \in \Sigma^*$, ordered argument vector $\mathbf{a} = [a_1, \dots, a_n] \in \Sigma^*$, resource vector $\mathbf{r} \in \mathbb{Z}_{\geq 0}^4$, optional wall-clock supervisor limit $t_{\text{wall}} \in \mathbb{Z}^+$.
*Output:* Execution tuple $\eta = (c, s_{\text{out}}, s_{\text{err}}, \mathbf{r}_{\text{actual}}, v)$.

1. **Static Validation:** Verify that every component of $\mathbf{r}$ is a non-negative integer and that $e$ resolves to an absolute path within a read-only evidence mount managed by `vigia.storage.evidence`. Reject symbolic links that escape the evidence root.
2. **Pre-execution Hook Construction:** Define a callable $h_{\text{rlimit}}$ that executes in the child address space post-fork and pre-exec. This callable invokes `resource.setrlimit` for each dimension of $\mathbf{r}$, setting both the soft limit (`rlim_cur`) and hard limit (`rlim_max`) to the identical integer value $r_i$. By equating soft and hard limits, the module prevents any privilege-escalation attempt via `setrlimit` from within the child.
3. **Asynchronous Dispatch:** The parent coroutine invokes `asyncio.create_subprocess_exec(e, *a, preexec_fn=h_{\text{rlimit}}, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)`. This yields a `Process` object $p$ whose lifecycle is managed by the host event loop.
4. **Concurrent Monitoring:** A primary coroutine awaits process termination via `await p.wait()`. A secondary watchdog coroutine asserts that wall-clock elapsed time $\Delta t_{\text{wall}}$ does not exceed $t_{\text{wall}}$. The wall-clock limit is orthogonal to CPU time and specifically mitigates I/O-blocking denial-of-service attacks that would not consume CPU budget.
5. **Termination and Accounting:** Upon process termination, capture:
   - Return code $c \in \mathbb{Z}$;
   - Standard output byte stream $s_{\text{out}} \in \mathcal{B}^*$;
   - Standard error byte stream $s_{\text{err}} \in \mathcal{B}^*$;
   - Actual peak resource usage $\mathbf{r}_{\text{actual}}$ via `resource.getrusage(RUSAGE_CHILDREN)` where the host kernel exposes this datum.
6. **Deterministic Status Mapping:** Map $c$ to a forensic status enumeration:
   - $c = 0$: Success;
   - $c = 137$ ($128 + 9$): `SIGKILL`, typically induced by `RLIMIT_AS` violation;
   - $c = 24$ ($128 + 24$): `SIGXCPU`, induced by `RLIMIT_CPU` violation;
   - $c = 25$ ($128 + 25$): `SIGXFSZ`, induced by `RLIMIT_FSIZE` violation;
   - $c \in \mathcal{E}$: Unhandled sandbox violation or internal error.

**Algorithm 2: Asynchronous Resource-Bound Pattern Search (Sandboxed Grep)**
*Input:* Regular-expression pattern $\rho \in \Sigma^*$, evidence file handle $f \in \mathcal{F}$, resource vector $\mathbf{r}$.
*Output:* Match set $M = \{ (o_j, l_j, m_j) \}_{j=1}^k$, where $o_j$ is byte offset, $l_j$ is line number, and $m_j$ is the matched substring.

1. Construct a sandboxed invocation of an external pattern-matching engine (e.g., GNU `grep`, `ripgrep`) via Algorithm 1, passing $\rho$ and $f$ through the argument vector.
2. Stream the evidence file into the subprocess `stdin` rather than loading $f$ into the host Python interpreter. This preserves the memory bound $r_{\text{as}}$ exclusively for the child process and prevents host-level memory pressure.
3. Asynchronously consume `stdout` line-by-line. For each line $\lambda$, test pattern membership $\lambda \in \mathcal{L}(\rho)$ within the child; only decoded offsets and match strings cross the sandbox boundary.
4. If the kernel delivers $\sigma_{\text{cpu}}$ or $\sigma_{\text{as}}$ during execution, the host raises `SandboxResourceExhausted`, carrying an immutable snapshot of $\mathbf{r}_{\text{actual}}$ for audit insertion into `vigia.audit.logger`.

*Complexity Analysis:* The pattern-matching phase exhibits complexity $O(|f| \cdot |\rho|)$ in the worst case, dominated by the external matching engine. The sandboxing overhead is $O(1)$ with respect to evidence size; monitoring coroutines consume $O(1)$ memory and $O(\Delta t_{\text{wall}})$ temporal resources.

### 4. Interface and Input/Output Specifications
*Inputs:*
- `executable`: `str`, absolute filesystem path $e$. Must reside within an evidence-root directory with `noexec` or `ro` mount flags removed only for whitelisted binaries.
- `args`: `Sequence[str]`, ordered argument vector $\mathbf{a}$.
- `resource_limits`: `dict[str, int]`, strict mapping from limit canonical names to exact integer values. Mandatory keys: `"max_address_space_bytes"`, `"max_cpu_time_seconds"`. Optional keys: `"max_file_size_bytes"`, `"max_processes"`, `"max_stack_bytes"`.
- `wall_timeout_seconds`: `int`, supervisor wall-clock limit $t_{\text{wall}}$.

*Outputs:*
- `SandboxResult`: An immutable dataclass comprising:
  - `returncode: int` ($c$)
  - `stdout: bytes` ($s_{\text{out}}$)
  - `stderr: bytes` ($s_{\text{err}}$)
  - `peak_memory_bytes: int` ($r_{\text{actual, mem}}$)
  - `cpu_time_seconds: int` ($r_{\text{actual, cpu}}$)
  - `violation: Optional[SandboxViolationType]` (enum value or `None`)

*Preconditions:*
- $e$ is executable by the VIGÍA service UID and GID.
- $\forall v \in \mathbf{r},\; v \geq 0 \land v \in \mathbb{Z}$.
- The host kernel implements POSIX.1-2008 `setrlimit` semantics.

*Postconditions:*
- If `violation is None`, then $c = 0$ and $\mathbf{r}_{\text{actual}} \leq \mathbf{r}$ component-wise.
- If `violation is not None`, the child process received the corresponding POSIX fatal signal and no host resources outside the pre-allocated pipes were accessed.

### 5. Deterministic Guarantees and Security Invariants
The module provides strict determinism in resource accounting and enforcement:
- **Integer-Only Enforcement Path:** All limit calculations, comparisons, and audit-log serializations operate exclusively on $\mathbb{Z}$. The complete absence of floating-point instructions in the enforcement path guarantees that limit thresholds are represented without approximation error, satisfying:
  $$\forall r_i \in \mathbf{r},\; \text{encode}(r_i) = \text{decode}(\text{encode}(r_i))$$
  where $\text{encode}$ maps the integer to its runtime representation.
- **Reproducible Termination Semantics:** For identical inputs $(e, \mathbf{a}, \mathbf{r}, t_{\text{wall}})$ executing on the same kernel version and hardware architecture, the termination modality—natural exit, `SIGKILL`, `SIGXCPU`, or `SIGXFSZ`—is deterministic. This satisfies the *reliability* and *known error rate* prongs of the Daubert standard by minimizing execution-control variance.
- **Sealed Resource Vectors:** Once a process is dispatched, $\mathbf{r}$ is sealed and stored in an append-only audit record. Runtime mutation of limits by the parent is prohibited, preventing privilege-escalation windows.
- **Filesystem Confinement:** Integration with `vigia.storage.evidence` ensures that the child process inherits a file-descriptor table restricted to read-only evidence mounts and temporary scratch directories, enforcing:
  $$\forall \text{fd} \in \text{FD}(P_c),\; \text{path}(\text{fd}) \in \mathcal{M}_{\text{evidence}} \cup \mathcal{M}_{\text{tmp}}$$

### 6. Integration with Related VIGÍA Modules
- **`vigia.security.sandbox`:** Direct functional replacement. The present module replicates the critical API surface of the orphaned dependency while removing external package risk.
- **`vigia.pipeline.orchestrator`:** The orchestrator consumes `vigia.sandbox.py` as its exclusive process-spawning backend. It passes evidence handles and tool configurations and receives `SandboxResult` objects to determine pipeline stage success.
- **`vigia.analyzer.pattern`:** Delegates line-oriented pattern matching to Algorithm 2. The analyzer post-processes the match set $M$ without directly executing foreign code.
- **`vigia.storage.evidence`:** Manages mount namespaces and read-only bindings. Evidence files are never opened for writing within the sandbox.
- **`vigia.audit.logger`:** Receives structured, timestamped, append-only JSON-LD records for every sandbox invocation. Each record contains the quadruple $(\text{batch\_id}, \mathbf{r}, c, \mathbf{r}_{\text{actual}})$.

### 7. Standards Compliance and Forensic Admissibility
- **Daubert Standard (U.S. Federal Rules of Evidence 702):** The module's deterministic integer-enforcement model, quantifiable resource accounting, and reproducible execution semantics provide a theoretically zero error rate for resource-bound enforcement. These characteristics satisfy the Daubert criteria of testability, peer review (via open POSIX standards), known error rate, and general acceptance.
- **GB/T 29360-2012** (*General Methods for Electronic Data Forensic Inspection*): The module's process isolation, immutable audit logging, and resource-constrained execution align with Chinese national standards for tool validation, inspection-process integrity, and prevention of evidence contamination.
- **MLPS 2.0** (*Multi-Level Protection Scheme 2.0*, Level 3): By enforcing memory and CPU hard limits and isolating third-party tools, the module contributes to the Level 3 requirements for intrusion prevention, malicious code execution containment, and resource-control within forensic analysis systems.

## ESPAÑOL

### 1. Propósito del módulo y posicionamiento arquitectónico
`vigia/sandbox.py` constituye un sustrato de ejecución determinista y autónomo dentro del marco de trabajo forense digital VIGÍA. Su función principal consiste en instanciar, restringir y monitorear procesos externos del sistema operativo —tales como motores de búsqueda de patrones, utilidades de extracción de archivos y analizadores de metadatos— bajo techos de recursos estrictamente cuantificados e inmutables. El módulo fue arquitectado para reemplazar la dependencia huérfana `vigia.security.sandbox`, logrando paridad funcional completa mientras elimina el riesgo de la cadena de suministro de terceros al basarse exclusivamente en la biblioteca estándar de Python 3 (`asyncio`, `subprocess`, `resource`). Dentro de la topología de canalizaciones de VIGÍA, este módulo ocupa el límite crítico entre el plano de orquestación de alto nivel (`vigia.pipeline.orchestrator`) y los binarios no gestionados de terceros, actuando como una puerta de enlace de mediación obligatoria que impide el consumo desmedido de recursos, la fuga del sistema de archivos y la computación descontrolada durante el procesamiento de la evidencia.

### 2. Fundamentos matemáticos y modelo de recursos
Definíase formalmente el vector de restricción de recursos como $\mathbf{r} = (r_{\text{as}}, r_{\text{cpu}}, r_{\text{fsize}}, r_{\text{nproc}}) \in \mathbb{Z}_{\geq 0}^4$, donde:
- $r_{\text{as}}$ denota el tamaño máximo del espacio de direcciones virtuales en bytes, mapeado a `RLIMIT_AS` de POSIX;
- $r_{\text{cpu}}$ denota el límite agregado de tiempo de CPU en segundos, mapeado a `RLIMIT_CPU`;
- $r_{\text{fsize}}$ denota el tamaño máximo de archivo de salida en bytes, mapeado a `RLIMIT_FSIZE`;
- $r_{\text{nproc}}$ denota la cantidad máxima de procesos hijos, mapeado a `RLIMIT_NPROC`.

El mecanismo de control se modela como una función de restricción rígida a nivel de kernel:
$$\Phi: \mathbb{Z}_{\geq 0}^4 \to \mathcal{P}, \quad \Phi(\mathbf{r}) = p_{\text{restringido}}$$
donde $\mathcal{P}$ representa el espacio de configuraciones de proceso factibles. En el marco de POSIX.1-2008, la llamada al sistema `setrlimit` establece techos inmutables tales que, para cualquier intento de adquisición de recurso $a_i$ por parte del proceso hijo aislado en la dimensión $i$:
$$\text{si } a_i > r_i \text{, el kernel envía la señal } \sigma_i \text{ a } p_{\text{restringido}}$$
siendo $\sigma_{\text{as}} = \text{SIGKILL}$ (agotamiento de memoria), $\sigma_{\text{cpu}} = \text{SIGXCPU}$ (agotamiento de CPU) y $\sigma_{\text{fsize}} = \text{SIGXFSZ}$ (agotamiento de tamaño de archivo). El módulo garantiza que todos los componentes de $\mathbf{r}$ sean enteros no negativos exactos, satisfaciendo:
$$\forall i \in \{1,2,3,4\}, \quad r_i \in \mathbb{N}_0, \quad \nexists \epsilon \in \mathbb{R}\setminus\mathbb{Q} : r_i = \lfloor r_i \rfloor + \epsilon$$
Esta exclusión deliberada de la representación de punto flotante en la lógica de control elimina el no determinismo inducido por redondeo y garantiza semánticas de límite idénticas bit a bit en invocaciones repetidas.

El aislamiento de procesos se formaliza mediante una separación estricta de espacios de direcciones. Dado un proceso forense huésped $P_h$ y un hijo aislado $P_c$, el módulo asegura que:
$$\text{Dir}(P_c) \cap \text{Dir}(P_h) = \emptyset \quad \text{salvo por canales de IPC mediados por el kernel}$$
donde $\text{Dir}(\cdot)$ denota el conjunto de páginas de memoria virtual mapeadas. Esta separación está garantizada por la semántica de copia en escritura (`copy-on-write`, COW) del kernel del sistema operativo durante la secuencia `fork()`–`exec()`, mediada por el módulo `subprocess` de Python.

### 3. Descripción algorítmica
El módulo expone dos modalidades operativas principales: (a) ejecución genérica de subprocesos aislados, y (b) búsqueda de patrones asíncrona con restricción de recursos.

**Algoritmo 1: Ejecución de subprocesos en entorno aislado**
*Entrada:* Ruta ejecutable absoluta $e \in \Sigma^*$, vector de argumentos ordenado $\mathbf{a} = [a_1, \dots, a_n] \in \Sigma^*$, vector de recursos $\mathbf{r} \in \mathbb{Z}_{\geq 0}^4$, límite supervisor opcional de tiempo de reloj $t_{\text{wall}} \in \mathbb{Z}^+$.
*Salida:* Tupla de ejecución $\eta = (c, s_{\text{out}}, s_{\text{err}}, \mathbf{r}_{\text{real}}, v)$.

1. **Validación estática:** Verificá que cada componente de $\mathbf{r}$ sea un entero no negativo y que $e$ se resuelva como una ruta absoluta dentro de un punto de montaje de evidencia de solo lectura gestionado por `vigia.storage.evidence`. Rechazá los enlaces simbólicos que escapen de la raíz de evidencia.
2. **Construcción del gancho pre-ejecución:** Definí un invocable $h_{\text{rlimit}}$ que se ejecuta en el espacio de direcciones del hijo post-`fork` y pre-`exec`. Este invocable llama a `resource.setrlimit` para cada dimensión de $\mathbf{r}$, estableciendo tanto el límite blando (`rlim_cur`) como el límite duro (`rlim_max`) en el valor entero idéntico $r_i$. Al igualar los límites blandos y duros, el módulo previene cualquier intento de escalada de privilegios mediante `setrlimit` desde el interior del hijo.
3. **Despacho asíncrono:** La corrutina padre invoca `asyncio.create_subprocess_exec(e, *a, preexec_fn=h_{\text{rlimit}}, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)`. Esto produce un objeto `Process` $p$ cuyo ciclo de vida es gestionado por el bucle de eventos del huésped.
4. **Monitoreo concurrente:** Una corrutina primaria espera la terminación del proceso mediante `await p.wait()`. Una corrutina secundaria de tipo *watchdog* asegura que el tiempo transcurrido de reloj $\Delta t_{\text{wall}}$ no supere $t_{\text{wall}}$. El límite de reloj es ortogonal al tiempo de CPU y mitiga específicamente ataques de denegación de servicio por bloqueo de E/S que no consumirían presupuesto de CPU.
5. **Terminación y contabilidad:** Al finalizar el proceso, capturá:
   - Código de retorno $c \in \mathbb{Z}$;
   - Flujo de bytes de salida estándar $s_{\text{out}} \in \mathcal{B}^*$;
   - Flujo de bytes de error estándar $s_{\text{err}} \in \mathcal{B}^*$;
   - Uso pico real de recursos $\mathbf{r}_{\text{real}}$ mediante `resource.getrusage(RUSAGE_CHILDREN)` cuando el kernel del huésped expone este dato.
6. **Mapeo determinista de estados:** Mapeá $c$ a una enumeración de estado forense:
   - $c = 0$: Éxito;
   - $c = 137$ ($128 + 9$): `SIGKILL`, típicamente inducido por violación de `RLIMIT_AS`;
   - $c = 24$ ($128 + 24$): `SIGXCPU`, inducido por violación de `RLIMIT_CPU`;
   - $c = 25$ ($128 + 25$): `SIGXFSZ`, inducido por violación de `RLIMIT_FSIZE`;
   - $c \in \mathcal{E}$: Violación no controlada del entorno aislado o error interno.

**Algoritmo 2: Búsqueda de patrones asíncrona con restricción de recursos (Grep aislado)**
*Entrada:* Patrón de expresión regular $\rho \in \Sigma^*$, manejador de archivo de evidencia $f \in \mathcal{F}$, vector de recursos $\mathbf{r}$.
*Salida:* Conjunto de coincidencias $M = \{ (o_j, l_j, m_j) \}_{j=1}^k$, donde $o_j$ es el desplazamiento en bytes, $l_j$ el número de línea y $m_j$ la subcadena coincidente.

1. Construí una invocación aislada de un motor de búsqueda de patrones externo (p. ej., GNU `grep`, `ripgrep`) mediante el Algoritmo 1, pasando $\rho$ y $f$ a través del vector de argumentos.
2. Transmití el archivo de evidencia al `stdin` del subproceso en lugar de cargar $f$ en el intérprete Python del huésped. Esto preserva el límite de memoria $r_{\text{as}}$ exclusivamente para el proceso hijo y evita la presión de memoria a nivel del huésped.
3. Consumí asíncronamente la `stdout` línea por línea. Para cada línea $\lambda$, probá la pertenencia al patrón $\lambda \in \mathcal{L}(\rho)$ dentro del hijo; solo los desplazamientos decodificados y las cadenas coincidentes cruzan la frontera del entorno aislado.
4. Si el kernel entrega $\sigma_{\text{cpu}}$ o $\sigma_{\text{as}}$ durante la ejecución, el huésped genera la excepción `SandboxResourceExhausted`, portando una instantánea inmutable de $\mathbf{r}_{\text{real}}$ para su inserción en la auditoría de `vigia.audit.logger`.

*Análisis de complejidad:* La fase de búsqueda de patrones exhibe una complejidad $O(|f| \cdot |\rho|)$ en el peor caso, dominada por el motor externo. La sobrecarga del entorno aislado es $O(1)$ respecto del tamaño de la evidencia; las corrutinas de monitoreo consumen $O(1)$ de memoria y $O(\Delta t_{\text{wall}})$ de recursos temporales.

### 4. Especificaciones de interfaz y entrada/salida
*Entradas:*
- `executable`: `str`, ruta absoluta del sistema de archivos $e$. Debe residir dentro de un directorio raíz de evidencia con banderas de montaje `noexec` o `ro` removidas únicamente para binarios en lista blanca.
- `args`: `Sequence[str]`, vector de argumentos ordenado $\mathbf{a}$.
- `resource_limits`: `dict[str, int]`, mapeo estricto desde nombres canónicos de límite hasta valores enteros exactos. Claves obligatorias: `"max_address_space_bytes"`, `"max_cpu_time_seconds"`. Claves opcionales: `"max_file_size_bytes"`, `"max_processes"`, `"max_stack_bytes"`.
- `wall_timeout_seconds`: `int`, límite supervisor de tiempo de reloj $t_{\text{wall}}$.

*Salidas:*
- `SandboxResult`: Una clase de datos inmutable que comprende:
  - `returncode: int` ($c$)
  - `stdout: bytes` ($s_{\text{out}}$)
  - `stderr: bytes` ($s_{\text{err}}$)
  - `peak_memory_bytes: int` ($r_{\text{real, mem}}$)
  - `cpu_time_seconds: int` ($r_{\text{real, cpu}}$)
  - `violation: Optional[SandboxViolationType]` (valor de enumeración o `None`)

*Precondiciones:*
- $e$ es ejecutable por el UID y GID del servicio VIGÍA.
- $\forall v \in \mathbf{r},\; v \geq 0 \land v \in \mathbb{Z}$.
- El kernel del huésped implementa las semánticas de `setrlimit` de POSIX.1-2008.

*Postcondiciones:*
- Si `violation is None`, entonces $c = 0$ y $\mathbf{r}_{\text{real}} \leq \mathbf{r}$ componente a componente.
- Si `violation is not None`, el proceso hijo recibió la señal fatal POSIX correspondiente y ningún recurso del huésped fuera de las tuberías preasignadas fue accedido.

### 5. Garantías deterministas e invariantes de seguridad
El módulo provee determinismo estricto en la contabilidad y el control de recursos:
- **Camino de control exclusivamente entero:** Todos los cálculos de límites, las comparaciones y las serializaciones de registro de auditoría operan exclusivamente sobre $\mathbb{Z}$. La ausencia completa de instrucciones de punto flotante en el camino de control garantiza que los umbrales de límite se representen sin error de aproximación, satisfaciendo:
  $$\forall r_i \in \mathbf{r},\; \text{codificar}(r_i) = \text{decodificar}(\text{codificar}(r_i))$$
  donde $\text{codificar}$ mapea el entero a su representación en tiempo de ejecución.
- **Semánticas de terminación reproducibles:** Para entradas idénticas $(e, \mathbf{a}, \mathbf{r}, t_{\text{wall}})$ ejecutadas sobre la misma versión de kernel y arquitectura de hardware, la modalidad de terminación —salida natural, `SIGKILL`, `SIGXCPU` o `SIGXFSZ`— es determinista. Esto satisface los requisitos de *confiabilidad* y *tasa de error conocida* del estándar Daubert al minimizar la varianza en el control de ejecución.
- **Vectores de recursos sellados:** Una vez despachado un proceso, $\mathbf{r}$ se sella y almacena en un registro de auditoría de solo apéndice. La mutación de límites en tiempo de ejecución por parte del padre está prohibida, previniendo ventanas de escalada de privilegios.
- **Confinamiento del sistema de archivos:** La integración con `vigia.storage.evidence` asegura que el proceso hijo hereda una tabla de descriptores de archivo restringida a montajes de evidencia de solo lectura y directorios temporales de trabajo, forzando:
  $$\forall \text{fd} \in \text{FD}(P_c),\; \text{ruta}(\text{fd}) \in \mathcal{M}_{\text{evidencia}} \cup \mathcal{M}_{\text{tmp}}$$

### 6. Integración con módulos VIGÍA relacionados
- **`vigia.security.sandbox`:** Reemplazo funcional directo. El presente módulo replica la superficie crítica de la API de la dependencia huérfana eliminando el riesgo de paquetes externos.
- **`vigia.pipeline.orchestrator`:** El orquestador consume `vigia.sandbox.py` como su backend exclusivo de generación de procesos. Pasa manejadores de evidencia y configuraciones de herramientas, y recibe objetos `SandboxResult` para determinar el éxito de la etapa de la canalización.
- **`vigia.analyzer.pattern`:** Delega la búsqueda de patrones orientada a líneas al Algoritmo 2. El analizador post-procesa el conjunto de coincidencias $M$ sin ejecutar código ajeno directamente.
- **`vigia.storage.evidence`:** Gestiona espacios de nombres de montaje y vínculos de solo lectura. Los archivos de evidencia nunca se abren para escritura dentro del entorno aislado.
- **`vigia.audit.logger`:** Recibe registros estructurados, con marca temporal y de solo apéndice, en formato JSON-LD para cada invocación del entorno aislado. Cada registro contiene la cuádrupla $(\text{id\_lote}, \mathbf{r}, c, \mathbf{r}_{\text{real}})$.

### 7. Alineación normativa y admisibilidad forense
- **Estándar Daubert (Reglas Federales de Evidencia 702 de EE. UU.):** El modelo de control entero determinista, la contabilidad cuantificable de recursos y las semánticas de ejecución reproducibles proveen una tasa de error teóricamente nula para el control de límites. Estas características satisfacen los criterios Daubert de comprobabilidad, revisión por pares (mediante estándares POSIX abiertos), tasa de error conocida y aceptación general.
- **GB/T 29360-2012** (*Métodos Generales para la Inspección Forense de Datos Electrónicos*): El aislamiento de procesos, el registro de auditoría inmutable y la ejecución con restricción de recursos se alinean con las normas nacionales chinas para la validación de herramientas, la integridad del proceso de inspección y la prevención de la contaminación de la evidencia.
- **MLPS 2.0** (*Esquema de Protección Multinivel 2.0*, Nivel 3): Al imponer límites rígidos de memoria y CPU y aislar herramientas de terceros, el módulo contribuye a los requisitos de Nivel 3 para la prevención de intrusiones, la contención de ejecución de código malicioso y el control de recursos dentro de sistemas de análisis forense.

## РУССКИЙ

### 1. Назначение модуля и архитектурное положение
Модуль `vigia/sandbox.py` представляет собой детерминированную автономную среду исполнения в рамках цифровой криминалистической платформы VIGÍA. Его основная функция заключается в инстанцировании, ограничении и мониторинге внешних процессов операционной системы — таких как механизмы поиска по шаблону, утилиты извлечения файлов и анализаторы метаданных — под строго количественно определёнными и неизменными потолками ресурсов. Данный модуль спроектирован в качестве функциональной замены утраченной зависимости `vigia.security.sandbox`, обеспечивая полный паритет возможностей при одновременном устранении рисков цепочки поставок сторонних компонентов благодаря использованию исключительно стандартной библиотеки Python 3 (`asyncio`, `subprocess`, `resource`). В топологии конвейера VIGÍA настоящий модуль занимает критическую границу между высокоуровневым плоскостью оркестрации (`vigia.pipeline.orchestrator`) и неуправляемыми сторонними исполняемыми модулями, выступая в роли обязательного медиационного шлюза, исключающего неконтролируемое потребление ресурсов, побег из файловой системы и неограниченные вычисления в ходе обработки доказательств.

### 2. Математические основы и модель ресурсов
Вектор ограничений ресурсов формально определяется как $\mathbf{r} = (r_{\text{as}}, r_{\text{cpu}}, r_{\text{fsize}}, r_{\text{nproc}}) \in \mathbb{Z}_{\geq 0}^4$, где:
- $r_{\text{as}}$ обозначает максимальный размер виртуального адресного пространства в байтах, отображаемый на POSIX `RLIMIT_AS`;
- $r_{\text{cpu}}$ обозначает совокупное ограничение процессорного времени в секундах, отображаемое на `RLIMIT_CPU`;
- $r_{\text{fsize}}$ обозначает максимальный размер выходного файла в байтах, отображаемый на `RLIMIT_FSIZE`;
- $r_{\text{nproc}}$ обозначает максимальное количество дочерних процессов, отображаемое на `RLIMIT_NPROC`.

Механизм принудительного ограничения моделируется как функция жёстких ограничений уровня ядра:
$$\Phi: \mathbb{Z}_{\geq 0}^4 \to \mathcal{P}, \quad \Phi(\mathbf{r}) = p_{\text{ограниченный}}$$
где $\mathcal{P}$ представляет пространство допустимых конфигураций процесса. В соответствии с POSIX.1-2008, системный вызов `setrlimit` устанавливает неизменные потолки, такие что для любой попытки захвата ресурса $a_i$ изолированным дочерним процессом по измерению $i$:
$$\text{если } a_i > r_i \text{, то ядро направляет сигнал } \sigma_i \text{ процессу } p_{\text{ограниченный}}$$
причём $\sigma_{\text{as}} = \text{SIGKILL}$ (исчерпание памяти), $\sigma_{\text{cpu}} = \text{SIGXCPU}$ (исчерпание процессорного времени) и $\sigma_{\text{fsize}} = \text{SIGXFSZ}$ (исчерпание размера файла). Модуль гарантирует, что все компоненты вектора $\mathbf{r}$ являются точными неотрицательными целыми числами, удовлетворяя условию:
$$\forall i \in \{1,2,3,4\}, \quad r_i \in \mathbb{N}_0, \quad \nexists \epsilon \in \mathbb{R}\setminus\mathbb{Q} : r_i = \lfloor r_i \rfloor + \epsilon$$
Данное целенаправленное исключение представления с плавающей запятой из логики принуждения устраняет вызванный округлением недетерминизм и гарантирует побитово идентичную семантику ограничений при повторных вызовах.

Изоляция процессов формализуется посредством строгого разделения адресных пространств. Заданы хост-процесс криминалистического исследования $P_h$ и изолированный дочерний процесс $P_c$. Модуль обеспечивает:
$$\text{Addr}(P_c) \cap \text{Addr}(P_h) = \emptyset \quad \text{за исключением каналов IPC, управляемых ядром}$$
где $\text{Addr}(\cdot)$ обозначает множество отображённых страниц виртуальной памяти. Указанное разделение гарантируется семантикой копирования при записи (`copy-on-write`, COW) ядра операционной системы в ходе последовательности `fork()`–`exec()`, осуществляемой через модуль `subprocess` языка Python.

### 3. Алгоритмическое описание
Модуль предоставляет две основные операционные модальности: (a) универсальное изолированное исполнение подпроцессов и (b) асинхронный поиск по шаблону с ограничением ресурсов.

**Алгоритм 1: Изолированное исполнение подпроцесса**
*Вход:* Абсолютный путь к исполняемому файлу $e \in \Sigma^*$, упорядоченный вектор аргументов $\mathbf{a} = [a_1, \dots, a_n] \in \Sigma^*$, вектор ресурсов $\mathbf{r} \in \mathbb{Z}_{\geq 0}^4$, необязательное предельное время наблюдения по астрономическому времени $t_{\text{wall}} \in \mathbb{Z}^+$.
*Выход:* Кортеж исполнения $\eta = (c, s_{\text{out}}, s_{\text{err}}, \mathbf{r}_{\text{факт}}, v)$.

1. **Статическая валидация:** Проверяется, что каждый компонент $\mathbf{r}$ является неотрицательным целым числом, а $e$ разрешается в абсолютный путь внутри точки монтирования доказательств, доступной только для чтения и управляемой модулем `vigia.storage.evidence`. Символические ссылки, выходящие за пределы корня доказательств, отклоняются.
2. **Конструирование предвыполнительного обработчика:** Определяется вызываемый объект $h_{\text{rlimit}}$, исполняемый в адресном пространстве потомка после `fork` и до `exec`. Данный объект вызывает `resource.setrlimit` для каждого измерения $\mathbf{r}$, устанавливая как мягкое ограничение (`rlim_cur`), так и жёсткое ограничение (`rlim_max`) в одно и то же целочисленное значение $r_i$. Уравнивая мягкие и жёсткие ограничения, модуль предотвращает любые попытки эскалации привилегий посредством `setrlimit` изнутри дочернего процесса.
3. **Асинхронный запуск:** Родительская сопрограмма вызывает `asyncio.create_subprocess_exec(e, *a, preexec_fn=h_{\text{rlimit}}, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)`. В результате создаётся объект `Process` $p$, жизненный цикл которого управляется циклом событий хоста.
4. **Параллельный мониторинг:** Основная сопрограмма ожидает завершения процесса посредством `await p.wait()`. Вспомогательная сопрограмма-сторожевой таймер гарантирует, что астрономическое время выполнения $\Delta t_{\text{wall}}$ не превышает $t_{\text{wall}}$. Ограничение по астрономическому времени ортогонально процессорному времени и специфически нейтрализует атаки типа отказа в обслуживании посредством блокировки ввода-вывода, которые не расходуют процессорный бюджет.
5. **Завершение и учёт ресурсов:** По окончании процесса фиксируются:
   - Код возврата $c \in \mathbb{Z}$;
   - Поток стандартного вывода $s_{\text{out}} \in \mathcal{B}^*$;
   - Поток стандартных ошибок $s_{\text{err}} \in \mathcal{B}^*$;
   - Фактический пиковый расход ресурсов $\mathbf{r}_{\text{факт}}$ посредством `resource.getrusage(RUSAGE_CHILDREN)` при условии, что хостовое ядро предоставляет данный параметр.
6. **Детерминированное отображение статусов:** Код $c$ отображается на перечисление криминалистического статуса:
   - $c = 0$: Успешное завершение;
   - $c = 137$ ($128 + 9$): `SIGKILL`, как правило, вызванный нарушением `RLIMIT_AS`;
   - $c = 24$ ($128 + 24$): `SIGXCPU`, вызванный нарушением `RLIMIT_CPU`;
   - $c = 25$ ($128 + 25$): `SIGXFSZ`, вызванный нарушением `RLIMIT_FSIZE`;
   - $c \in \mathcal{E}$: Необработанное нарушение песочницы или внутренняя ошибка.

**Алгоритм 2: Асинхронный поиск по шаблону с ограничением ресурсов (изолированный grep)**
*Вход:* Шаблон регулярного выражения $\rho \in \Sigma^*$, дескриптор файла доказательств $f \in \mathcal{F}$, вектор ресурсов $\mathbf{r}$.
*Выход:* Множество совпадений $M = \{ (o_j, l_j, m_j) \}_{j=1}^k$, где $o_j$ — смещение в байтах, $l_j$ — номер строки, $m_j$ — совпавшая подстрока.

1. Конструируется изолированный вызов