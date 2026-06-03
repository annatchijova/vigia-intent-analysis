## ENGLISH

**Module Designation and Functional Purpose**
The Python module `vigia/sift/mft_timeline_analyzer.py` operates as a legacy backward-compatibility interface—conceptually, a forensic software shim—within the VIGÍA digital forensics framework, specifically under the SIFT (Systematic Investigation of Forensic Traces) subsystem. Historically, this component housed the authoritative implementation for Master File Table (MFT) timeline reconstruction from NTFS-formatted evidence media. Following architectural refactoring, its active analytical logic has been migrated to the canonical class `vigia.sift.disk_forensics.MFTTimelineAnalyzer`. The current instantiation of `vigia/sift/mft_timeline_analyzer.py` performs no native forensic computation; rather, it functions as a transparent proxy, deterministically routing all function invocations, class instantiations, and keyword arguments to the canonical successor. Its retention in the source tree ensures longitudinal reproducibility of legacy analytical workflows, chain-of-custody integrity for historical audits, and a deterministic migration pathway for forensic practitioners.

**Mathematical and Theoretical Foundations**
The reconstruction of timelines from the NTFS MFT is grounded in discrete mathematics and temporal logic. The MFT is modeled as a finite ordered set $M = \{r_1, r_2, \ldots, r_n\}$, where each record $r_i$ corresponds to a metadata entry of fixed length (typically 1024 bytes, though extensible). Each record encapsulates an attribute set $A(r_i) = \{a_{i,1}, a_{i,2}, \ldots, a_{i,m}\}$, wherein attributes of type $0x10$ (STANDARD_INFORMATION) and $0x30$ (FILE_NAME) contain the temporally significant fields.

Define the timestamp extraction operator $\Gamma$ over an attribute $a \in A(r_i)$ such that:
$$\Gamma(a) = (c, m, a, e) \in \mathbb{T}^4$$
where $\mathbb{T} \subset \mathbb{N}_{64}$ denotes the space of valid Windows FILETIME values, quantified in 100-nanosecond intervals elapsed since the epoch 1601-01-01T00:00:00Z. For each record, the complete temporal signature is the union of signatures from all resident $FILE_NAME attributes:
$$\mathcal{T}(r_i) = \bigcup_{a \in A(r_i), \text{type}(a) \in \{0x10, 0x30\}} \Gamma(a)$$

The timeline synthesis function $\Lambda$ imposes a strict weak ordering $\prec_\tau$ on $M$ across a selected temporal dimension $\tau \in \{t_c, t_m, t_a, t_e\}$:
$$\Lambda(M, \tau) = \text{sort}(M, \prec_\tau)$$
This operation exhibits time complexity $\mathcal{O}(|M| \log |M|)$ and space complexity $\mathcal{O}(|M|)$ under the comparison sort model.

Temporal integrity is enforced via the monotonicity predicate $\Phi$:
$$\Phi(r_i) = \begin{cases} 1 & \text{if } t_c(r_i) \leq t_m(r_i) \leq t_e(r_i) \\ 0 & \text{otherwise} \end{cases}$$
Violations of $\Phi$ suggest anti-forensic timestamp manipulation (time-stomping), system clock desynchronization, or malware-induced temporal anomalies. The anomaly quantification metric $\alpha$ assigns a deviation score:
$$\alpha(r_i) = \frac{|t_m - t_c| + |t_e - t_m|}{\mu_{\Delta t} + \epsilon}$$
where $\mu_{\Delta t}$ is the mean inter-event interval across the volume and $\epsilon$ is a smoothing constant to prevent division by zero.

Furthermore, the module’s proxy behavior can be formalized as an identity morphism $id_{\mathcal{F}}$ in the category of forensic transformations $\mathcal{F}$. For any forensic function $f \in \mathcal{F}$ implemented canonically as $f_{canon}$, the legacy module satisfies:
$$f_{legacy}(I) = (id_{\mathcal{F}} \circ f_{canon} \circ \rho)(I)$$
where $\rho$ is the parameter-space isomorphism mapping legacy schemas to canonical schemas.

**Algorithmic Architecture**
The operational workflow comprises four deterministic phases:

*Phase I: Input Validation and Schema Binding.* The legacy entry point receives an input tuple $I = \langle P, O, \Theta, \mathcal{K} \rangle$, where $P$ denotes the source path, $O$ the partition offset, $\Theta$ the timezone identifier, and $\mathcal{K}$ the configuration dictionary. The module validates $I$ against the legacy schema $\Sigma_{legacy}$ using predicate $V(I)$, ensuring type correctness and boundary constraints.

*Phase II: Parameter Transduction.* A bijective mapping function $\rho: \Sigma_{legacy} \to \Sigma_{canonical}$ transforms legacy arguments into the canonical API surface of `vigia.sift.disk_forensics.MFTTimelineAnalyzer`. This mapping preserves semantic equivalence: $\forall x \in \Sigma_{legacy}, \exists! y \in \Sigma_{canonical}: \rho(x) = y \land \text{sem}(x) = \text{sem}(y)$.

*Phase III: Canonical Delegation.* The module dispatches the transduced request to the canonical implementation. Formally, the shim layer computes:
$$R = f_{canon}(\rho(I))$$
where $f_{canon}$ represents the consolidated timeline reconstruction routine. The shim itself is stateless; its internal state transition is the identity: $\Delta S_{shim} = S_{post} - S_{pre} = 0$.

*Phase IV: Provenance Logging and Result Proxying.* Each invocation generates an immutable audit record $\mathcal{A} = \langle v, t_{exec}, f_{src}, f_{dst}, h(I), R \rangle$, where $v \sim \text{UUIDv4}$, $t_{exec}$ is the execution timestamp in UTC, $f_{src}$ and $f_{dst}$ are the legacy and canonical fully-qualified names, and $h(I)$ is the SHA-256 digest of the serialized input. The audit record is appended to the centralized logger `vigia.core.audit.AuditLogger`. The result $R$ is returned to the caller without mutation.

The underlying canonical algorithm performs: (1) raw byte acquisition via `vigia.io.raw_disk_reader`; (2) NTFS boot sector parsing to locate the $MFT cluster; (3) fixup verification using the 2-byte signature array stored in the record header; (4) attribute parsing distinguishing resident versus non-resident data runs; (5) FILETIME decoding and timezone normalization to UTC; and (6) super-timeline correlation with USN Journal entries when available.

**Input and Output Specifications**
*Input Domain:*
- `source_path` ($P$): File system path to a forensic image (Expert Witness Format/E01, raw DD, AFF4) or an extracted `$MFT` binary stream.
- `partition_offset` ($O$): Non-negative integer byte offset ($O \in \mathbb{Z}_{\geq 0}$) to the NTFS boot sector. Default $O = 0$ for standalone MFT extractions.
- `timezone` ($\Theta$): IANA Olson database string (e.g., "America/Buenos_Aires") for localization.
- `configuration` ($\mathcal{K}$): A key-value dictionary controlling parsing granularity, anomaly threshold $\theta_\alpha$, and boolean flags for cross-artifact correlation.

*Output Codomain:*
- `timeline` ($\mathcal{L}$): A totally ordered sequence of forensic events $\mathcal{L} = [l_1, l_2, \ldots, l_n]$ such that $l_j \prec l_{j+1}$ by the selected temporal key. Each element $l_j$ is an 8-tuple:
  $$l_j = \langle \text{record\_idx}, \text{full\_path}, t_c^{SI}, t_m^{SI}, t_a^{SI}, t_e^{SI}, t_c^{FN}, \alpha_j \rangle$$
- `audit_provenance` ($\mathcal{A}^*$): A JSON-L structured log conforming to W3C PROV-O ontology extensions used within VIGÍA.
- `metadata` ($\mathcal{M}$): Execution statistics including wall-clock duration $\Delta t_{wall}$, CPU cycles $N_{cycles}$, record cardinality $|M|$, parsing error count $|\mathcal{E}|$, and entropy $H(\mathcal{T})$ of the timestamp distribution.

**Deterministic Guarantees and Forensic Rigor**
The module adheres to stringent deterministic guarantees necessary for courtroom admissibility under the Daubert standard and international digital forensics protocols:
1. **Idempotency of Interface Redirection:** For any input $I$ drawn from the valid input domain $\mathcal{I}$, the routing function is stable: $\rho(I) = \rho'(I)$ across repeated evaluations. Consequently, $f_{legacy}(I) = f_{legacy}^k(I)$ for all $k \in \mathbb{N}^+$.
2. **Bitwise Canonical Fidelity:** The proxy guarantees $R_{legacy} \equiv R_{canonical}$ at the byte level. No post-processing, annotation, or filtering is applied within the shim.
3. **Complete Provenance Immutability:** The set of all audit tuples $\mathcal{A}^*$ generated during the module lifecycle constitutes a complete, tamper-evident provenance graph. Any omission or mutation of $\mathcal{A}^*$ is detectable via the Merkle tree maintained by `vigia.core.audit.AuditLogger`.
4. **Cross-Platform Reproducibility:** Given identical input bytes, identical partition geometry, and equivalent configuration $\mathcal{K}$, the output timeline $\mathcal{L}$ is invariant across execution environments, satisfying the repeatability and reproducibility requirements of GB/T 29360-2012.

**Related VIGÍA Modules and System Topology**
- `vigia.sift.disk_forensics.MFTTimelineAnalyzer`: The canonical implementation to which all operations are delegated.
- `vigia.sift.mft_parser.MFTRecordDecoder`: Responsible for low-level deserialization of MFT record structures, fixup array application, and attribute resident/non-resident classification.
- `vigia.io.raw_disk_reader.BlockDeviceReader`: Provides forensically sound, read-only, byte-addressable access to evidence media.
- `vigia.core.audit.AuditLogger`: Centralized subsystem for tamper-evident logging and chain-of-custody maintenance.
- `vigia.correlator.super_timeline.SuperTimelineBuilder`: Aggregates MFT-derived events with Windows Registry, EVTX, Prefetch, and MACB timestamps to construct a unified super-timeline.

**Standards and Compliance Matrix**
- **Daubert Standard (USA):** The deterministic output, documented error rates (quantified as $|\mathcal{E}|/|M|$), and reproducible methodology satisfy the criteria for admissibility of scientific evidence in federal courts.
- **GB/T 29360-2012 (China):** Compliant with electronic data forensic examination standards, specifically regarding evidence integrity and process documentation.
- **GB/T 31500-2015 (China):** Satisfies information security audit data specification requirements for forensic tool validation.
- **MLPS 2.0 Level 3 (China):** Aligns with Multi-Level Protection Scheme 2.0 audit and traceability mandates, ensuring non-repudiable logging of all forensic transformations on information systems classified at security protection level 3 or above.

## ESPAÑOL

**Designación del módulo y propósito funcional**
El módulo Python `vigia/sift/mft_timeline_analyzer.py` opera como una interfaz de compatibilidad retrospectiva —formalmente, una *shim* forense— dentro del marco de forense digital VIGÍA, específicamente en el subsistema SIFT (*Systematic Investigation of Forensic Traces*). Históricamente, este componente albergaba la implementación autoritativa para la reconstrucción de líneas temporales a partir de la Tabla Maestra de Archivos (MFT) de volúmenes NTFS. Tras una refactorización arquitectónica, la lógica analítica activa migró a la clase canónica `vigia.sift.disk_forensics.MFTTimelineAnalyzer`. La instancia actual del módulo `vigia/sift/mft_timeline_analyzer.py` no realiza cómputo forense nativo; cuando lo utilizás, observás que funciona exclusivamente como un proxy transparente que deriva todas las invocaciones de funciones, instanciaciones de clases y argumentos nombrados hacia la implementación canónica. Su permanencia en el árbol de fuentes garantiza la reproducibilidad longitudinal de *workflows* heredados, la integridad de la cadena de custodia para auditorías históricas y una vía de migración determinista que debés considerar al estandarizar tus protocolos forenses.

**Fundamentos matemáticos y teóricos**
La reconstrucción de líneas temporales desde el MFT de NTFS se fundamenta en matemática discreta y lógica temporal. Modelizamos el MFT como un conjunto finito ordenado $M = \{r_1, r_2, \ldots, r_n\}$, donde cada registro $r_i$ corresponde a una entrada de metadatos de longitud fija (típicamente 1024 bytes, aunque extensible). Cada registro encapsula un conjunto de atributos $A(r_i) = \{a_{i,1}, a_{i,2}, \ldots, a_{i,m}\}$, donde los atributos de tipo $0x10$ (STANDARD_INFORMATION) y $0x30$ (FILE_NAME) contienen los campos temporalmente significativos.

Definimos el operador de extracción de marcas temporales $\Gamma$ sobre un atributo $a \in A(r_i)$ tal que:
$$\Gamma(a) = (c, m, a, e) \in \mathbb{T}^4$$
donde $\mathbb{T} \subset \mathbb{N}_{64}$ denota el espacio de valores FILETIME válidos de Windows, cuantificados en intervalos de 100 nanosegundos desde el *epoch* 1601-01-01T00:00:00Z. Para cada registro, la firma temporal completa es la unión de las firmas de todos los atributos residentes $FILE_NAME:
$$\mathcal{T}(r_i) = \bigcup_{a \in A(r_i), \text{tipo}(a) \in \{0x10, 0x30\}} \Gamma(a)$$

La función de síntesis de línea temporal $\Lambda$ impone un orden estricto débil $\prec_\tau$ sobre $M$ a lo largo de una dimensión temporal seleccionada $\tau \in \{t_c, t_m, t_a, t_e\}$:
$$\Lambda(M, \tau) = \text{ordenar}(M, \prec_\tau)$$
Esta operación exhibe complejidad temporal $\mathcal{O}(|M| \log |M|)$ y complejidad espacial $\mathcal{O}(|M|)$ bajo el modelo de ordenamiento por comparación.

La integridad temporal se aplica mediante el predicado de monotonicidad $\Phi$:
$$\Phi(r_i) = \begin{cases} 1 & \text{si } t_c(r_i) \leq t_m(r_i) \leq t_e(r_i) \\ 0 & \text{en otro caso} \end{cases}$$
Las violaciones de $\Phi$ sugieren manipulación anti-forense de marcas temporales (*time-stomping*), desincronización del reloj del sistema o anomalías temporales inducidas por *malware*. La métrica de cuantificación de anomalías $\alpha$ que obtenés del análisis asigna una puntuación de desviación:
$$\alpha(r_i) = \frac{|t_m - t_c| + |t_e - t_m|}{\mu_{\Delta t} + \epsilon}$$
donde $\mu_{\Delta t}$ es el intervalo medio inter-evento en el volumen y $\epsilon$ es una constante de suavizado para evitar la división por cero.

Además, el comportamiento *proxy* del módulo podés formalizarlo como un morfismo identidad $id_{\mathcal{F}}$ en la categoría de transformaciones forenses $\mathcal{F}$. Para cualquier función forense $f \in \mathcal{F}$ implementada canónicamente como $f_{canon}$, el módulo heredado satisface:
$$f_{legacy}(I) = (id_{\mathcal{F}} \circ f_{canon} \circ \rho)(I)$$
donde $\rho$ es el isomorfismo del espacio de parámetros que mapea esquemas heredados a esquemas canónicos.

**Arquitectura algorítmica**
El flujo de trabajo operativo comprende cuatro fases deterministas:

*Fase I: Validación de entrada y vinculación de esquema.* El punto de entrada heredado recibe una tupla de entrada $I = \langle P, O, \Theta, \mathcal{K} \rangle$, donde $P$ denota la ruta fuente, $O$ el desplazamiento de partición, $\Theta$ el identificador de zona horaria y $\mathcal{K}$ el diccionario de configuración. El módulo valida $I$ contra el esquema heredado $\Sigma_{legacy}$ mediante el predicado $V(I)$, asegurando corrección de tipos y restricciones de límite.

*Fase II: Transducción de parámetros.* Una función de mapeo biyectiva $\rho: \Sigma_{legacy} \to \Sigma_{canonical}$ transforma los argumentos heredados en la superficie de API canónica de `vigia.sift.disk_forensics.MFTTimelineAnalyzer`. Este mapeo preserva la equivalencia semántica: $\forall x \in \Sigma_{legacy}, \exists! y \in \Sigma_{canonical}: \rho(x) = y \land \text{sem}(x) = \text{sem}(y)$.

*Fase III: Delegación canónica.* El módulo despacha la solicitud transducida a la implementación canónica. Formalmente, la capa *shim* computa:
$$R = f_{canon}(\rho(I))$$
donde $f_{canon}$ representa la rutina consolidada de reconstrucción de línea temporal. El *shim* en sí es *stateless*; si analizás su transición de estado interno, verificás que es la identidad: $\Delta S_{shim} = S_{post} - S_{pre} = 0$.

*Fase IV: Registro de proveniencia y *proxy* de resultados.* Cada invocación genera un registro de auditoría inmutable $\mathcal{A} = \langle v, t_{exec}, f_{src}, f_{dst}, h(I), R \rangle$, donde $v \sim \text{UUIDv4}$, $t_{exec}$ es la marca temporal de ejecución en UTC, $f_{src}$ y $f_{dst}$ son los nombres completamente calificados heredado y canónico, respectivamente, y $h(I)$ es el resumen SHA-256 de la entrada serializada. El registro de auditoría se anexa al registrador centralizado `vigia.core.audit.AuditLogger`. El resultado $R$ se devuelve al invocador sin mutación.

El algoritmo canónico subyacente ejecuta: (1) adquisición de bytes crudos mediante `vigia.io.raw_disk_reader`; (2) análisis del sector de arranque NTFS para localizar el clúster $MFT$; (3) verificación de *fixup* utilizando el arreglo de firmas de 2 bytes almacenado en el encabezado del registro; (4) análisis de atributos distinguiendo *runs* de datos residentes y no residentes; (5) decodificación de FILETIME y normalización de zona horaria a UTC; y (6) correlación de *super-timeline* con entradas del Diario USN cuando estén disponibles.

**Especificaciones de entrada y salida**
*Dominio de entrada:*
- `source_path` ($P$): Ruta del sistema de archivos a una imagen forense (formato Expert Witness/E01, DD cruda, AFF4) o a un flujo binario `$MFT` extraído.
- `partition_offset` ($O$): Entero no negativo ($O \in \mathbb{Z}_{\geq 0}$) que indica el desplazamiento en bytes hacia el sector de arranque NTFS. Por defecto $O = 0$ para extracciones independientes del MFT.
- `timezone` ($\Theta$): Cadena de la base de datos IANA Olson (p. ej., "America/Buenos_Aires") para localización.
- `configuration` ($\mathcal{K}$): Diccionario clave-valor que controla la granularidad del análisis, el umbral de anomalía $\theta_\alpha$ y banderas booleanas para la correlación entre artefactos.

*Codominio de salida:*
- `timeline` ($\mathcal{L}$): Una secuencia totalmente ordenada de eventos forenses $\mathcal{L} = [l_1, l_2, \ldots, l_n]$ tal que $l_j \prec l_{j+1}$ según la clave temporal seleccionada. Cada elemento $l_j$ es una 8-tupla:
  $$l_j = \langle \text{record\_idx}, \text{ruta\_completa}, t_c^{SI}, t_m^{SI}, t_a^{SI}, t_e^{SI}, t_c^{FN}, \alpha_j \rangle$$
- `audit_provenance` ($\mathcal{A}^*$): Un registro estructurado en JSON-L conforme a las extensiones de ontología W3C PROV-O utilizadas en VIGÍA.
- `metadata` ($\mathcal{M}$): Estadísticas de ejecución que incluyen duración de reloj de pared $\Delta t_{wall}$, ciclos de CPU $N_{cycles}$, cardinalidad de registros $|M|$, cantidad de errores de análisis $|\mathcal{E}|$ y entropía $H(\mathcal{T})$ de la distribución de marcas temporales.

**Garantías deterministas y rigor forense**
El módulo se adhiere a garantías deterministas estrictas, necesarias para la admisibilidad en sede judicial bajo el estándar Daubert y los protocolos internacionales de forense digital:
1. **Idempotencia de la redirección de interfaz:** Para cualquier entrada $I$ extraída del dominio de entrada válido $\mathcal{I}$, la función de enrutamiento es estable: $\rho(I) = \rho'(I)$ a través de evaluaciones repetidas. En consecuencia, $f_{legacy}(I) = f_{legacy}^k(I)$ para todo $k \in \mathbb{N}^+$.
2. **Fidelidad canónica a nivel de bit:** El *proxy* garantiza $R_{legacy} \equiv R_{canonical}$ a nivel de byte. No se aplica post-procesamiento, anotación ni filtrado dentro de la capa *shim*.
3. **Inmutabilidad completa de la proveniencia:** El conjunto de todas las tuplas de auditoría $\mathcal{A}^*$ generadas durante el ciclo de vida del módulo constituye un grafo de proveniencia completo y resistente a manipulaciones. Si analizás cualquier omisión o mutación de $\mathcal{A}^*$, detectás la anomalía mediante el árbol de Merkle mantenido por `vigia.core.audit.AuditLogger`.
4. **Reproducibilidad multiplataforma:** Dados bytes de entrada idénticos, geometría de partición idéntica y configuración equivalente $\mathcal{K}$, la línea temporal de salida $\mathcal{L}$ es invariante entre entornos de ejecución, satisfaciendo los requisitos de repetibilidad y reproducibilidad de la norma GB/T 29360-2012.

**Módulos VIGÍA relacionados y topología del sistema**
- `vigia.sift.disk_forensics.MFTTimelineAnalyzer`: La implementación canónica hacia la cual se delegan todas las operaciones.
- `vigia.sift.mft_parser.MFTRecordDecoder`: Responsable de la deserialización de bajo nivel de las estructuras de registro MFT, aplicación de arreglos de *fixup* y clasificación de atributos residentes/no residentes.
- `vigia.io.raw_disk_reader.BlockDeviceReader`: Provee acceso forense sano, de solo lectura y direccionable por bytes a los medios de evidencia.
- `vigia.core.audit.AuditLogger`: Subsistema centralizado para registro resistente a manipulaciones y mantenimiento de la cadena de custodia.
- `vigia.correlator.super_timeline.SuperTimelineBuilder`: Agrega eventos derivados del MFT con el Registro de Windows, EVTX, Prefetch y marcas temporales MACB para construir una *super-timeline* unificada.

**Matriz de estándares y cumplimiento**
- **Estándar Daubert (EE.UU.):** El output determinista, las tasas de error documentadas (cuantificadas como $|\mathcal{E}|/|M|$) y la metodología reproducible satisfacen los criterios de admisibilidad de evidencia científica en tribunales federales.
- **GB/T 29360-2012 (China):** Cumple con los estándares de examen forense de datos electrónicos, específicamente respecto a la integridad de la evidencia y la documentación del proceso.
- **GB/T 31500-2015 (China):** Satisface los requisitos de especificación de datos de auditoría de seguridad de la información para la validación de herramientas forenses.
- **MLPS 2.0 Nivel 3 (China):** Se alinea con los mandatos de auditoría y trazabilidad del Esquema de Protección Multinivel 2.0, asegurando el registro no repudiable de todas las transformaciones forenses en sistemas de información clasificados en nivel de protección de seguridad 3 o superior.

## РУССКИЙ

**Обозначение модуля и функциональное назначение**
Модуль `vigia/sift/mft_timeline_analyzer.py` функционирует в качестве устаревшего интерфейса обратной совместимости — формально, криминалистической программной прослойки (*shim*) — в рамках цифровой криминалистической платформы VIGÍA, конкретно в подсистеме SIFT (*Systematic Investigation of Forensic Traces*). Исторически данный компонент содержал авторитетную реализацию логики реконструкции временной шкалы на основании данных Главной файловой таблицы (MFT) носителей с файловой системой NTFS. В результате архитектурного рефакторинга активная аналитическая логика была перенесена в канонический класс `vigia.sift.disk_forensics.MFTTimelineAnalyzer`. Текущая версия модуля `vigia/sift/mft_timeline_analyzer.py` не осуществляет собственных криминалистических вычислений; он действует исключительно как прозрачный прокси, детерминированно перенаправляя все вызовы функций, инстанцирования классов и именованные аргументы к канонической реализации. Сохранение модуля в дереве исходных кодов обеспечивает долгосрочную воспроизводимость устаревших аналитических сценариев, сохранение целостности цепочки хранения для исторических аудитов и детерминированный путь миграции для экспертов-исследователей.

**Математические и теоретические основания**
Реконструкция временной шкалы на основании MFT файловой системы NTFS базируется на дискретной математике и темпоральной логике. MFT моделируется как конечное упорядоченное множество $M = \{r_1, r_2, \ldots, r_n\}$, где каждая запись $r_i$ соответствует метаданным фиксированной длины (как правило, 1024 байта, хотя возможно расширение). Каждая запись инкапсулирует набор атрибутов $A(r_i) = \{a_{i,1}, a_{i,2}, \ldots, a_{i,m}\}$, причем атрибуты типа $0x10$ (STANDARD_INFORMATION) и $0x30$ (FILE_NAME) содержат темпорально значимые поля.

Определим оператор извлечения временных меток $\Gamma$ над атрибутом $a \in A(r_i)$ таким образом, что:
$$\Gamma(a) = (c, m, a, e) \in \mathbb{T}^4$$
где $\mathbb{T} \subset \mathbb{N}_{64}$ обозначает пространство допустимых значений Windows FILETIME, квантованных в интервалах по 100 наносекунд, истекших с эпохи 1601-01-01T00:00:00Z. Для каждой записи полная темпоральная сигнатура представляет собой объединение сигнатур всех резидентных атрибутов $FILE_NAME:
$$\mathcal{T}(r_i) = \bigcup_{a \in A(r_i), \text{тип}(a) \in \{0x10, 0x30\}} \Gamma(a)$$

Функция синтеза временной шкалы $\Lambda$ накладывает строгое слабое упорядочение $\prec_\tau$ на множество $M$ по выбранной темпоральной размерности $\tau \in \{t_c, t_m, t_a, t_e\}$:
$$\Lambda(M, \tau) = \text{сортировка}(M, \prec_\tau)$$
Данная операция демонстрирует вычислительную сложность $\mathcal{O}(|M| \log |M|)$ и пространственную сложность $\mathcal{O}(|M|)$ в модели сортировки на основе сравнений.

Темпоральная целостность обеспечивается посредством предиката монотонности $\Phi$:
$$\Phi(r_i) = \begin{cases} 1 & \text{если } t_c(r_i) \leq t_m(r_i) \leq t_e(r_i) \\ 0 & \text{в ином случае} \end{cases}$$
Нарушения предиката $\Phi$ свидетельствуют о возможной анти-криминалистической манипуляции временными метками (*time-stomping*), десинхронизации системных часов или темпоральных аномалиях, индуцированных вредоносным программным обеспечением. Метрика количественной оценки аномалий $\alpha$ присваивает оценку отклонения:
$$\alpha(r_i) = \frac{|t_m - t_c| + |t_e - t_m|}{\mu_{\Delta t} + \epsilon}$$
где $\mu_{\Delta t}$ — средний межсобытийный интервал в пределах тома, а $\epsilon$ — сглаживающая константа, предотвращающая деление на ноль.

Кроме того, прокси-поведение модуля может быть формализовано как тождественный морфизм $id_{\mathcal{F}}$ в категории криминалистических преобразований $\mathcal{F}$. Для любой криминалистической функции $f \in \mathcal{F}$, реализованной канонически как $f_{canon}$, устаревший модуль удовлетворяет соотношению:
$$f_{legacy}(I) = (id_{\mathcal{F}} \circ f_{canon} \circ \rho)(I)$$
где $\rho$ — изоморфизм пространства параметров, отображающий устаревшие схемы на канонические.

**Алгоритмическая архитектура**
Операционный рабочий процесс включает четыре детерминированные фазы:

*Фаза I: Валидация входных данных и привязка схемы.* Точка входа устаревшего интерфейса принимает входной кортеж $I = \langle P, O, \Theta, \mathcal{K} \rangle$, где $P$ обозначает путь к источнику, $O$ — смещение раздела, $\Theta$ — идентификатор часового пояса, а $\mathcal{K}$ — словарь конфигурации. Модуль выполняет валидацию $I$ относительно устаревшей схемы $\Sigma_{legacy}$ с использованием предиката $V(I)$, обеспечивая корректность типов и соблюдение граничных ограничений.

*Фаза II: Трансдукция параметров.* Биективная функция отображения $\rho: \Sigma_{legacy} \to \Sigma_{canonical}$ преобразует устаревшие аргументы в канонический программный интерфейс класса `vigia.sift.disk_forensics.MFTTimelineAnalyzer`. Данное отображение сохраняет семантическую эквивалентность: $\forall x \in \Sigma_{legacy}, \exists! y \in \Sigma_{canonical}: \rho(x) = y \land \text{sem}(x) = \text{sem}(y)$.

*Фаза III: Каноническое делегирование.* Модуль направляет трансдуцированный запрос к канонической реализации. Формально прослойка вычисляет:
$$R = f_{canon}(\rho(I))$$
где $f_{canon}$ представляет собой консолидированную процедуру реконструкции временной шкалы. Прослойка (*shim*) сама по себе не имеет состояния; её внутренний переход состояния является тождественным: $\Delta S_{shim} = S_{post} - S_{pre} = 0$.

*Фаза IV: Протоколирование происхождения и проксирование результата.* Каждый вызов порождает неизменяемую аудиторскую запись $\mathcal{A} = \langle v, t_{exec}, f_{src}, f_{dst}, h(I), R \rangle$, где $v \sim \text{UUIDv4}$, $t_{exec}$ — временная метка выполнения в формате UTC, $f_{src}$ и $f_{dst}$ — полностью определенные имена устаревшего и канонического модулей соответственно, а $h(I)$ — дайджест SHA-256 сериализованных входных данных. Аудиторская запись добавляется в централизованный регистратор `vigia.core.audit.AuditLogger`. Результат $R$ возвращается вызывающей стороне без модификации.

Канонический алгоритм, лежащий в основе данного прокси, выполняет: (1) получение необработанных байтов посредством `vigia.io.raw_disk_reader`; (2) разбор загрузочного сектора NTFS для локализации кластера $MFT; (3) верификацию корректирующего массива (*fixup*) с использованием 2-байтового массива сигнатур, хранящегося в заголовке записи; (4) разбор атрибутов с различением резидентных и нерезидентных последовательностей данных; (5) декодирование FILETIME и нормализацию часового пояса к UTC; (6) корреляцию супер-временной шкалы с записями журнала USN при их наличии.

**Спецификации входных и выходных данных**
*Входной домен:*
- `source_path` ($P$): Путь файловой системы к криминалистическому образу (форматы Expert Witness/E01, RAW/DD, AFF4) или извлеченному двоичному потоку `$MFT`.
- `partition_offset` ($O$): Неотрицательное целочисленное смещение в байтах ($O \in \mathbb{Z}_{\geq 0}$) к загрузочному сектору NTFS. Значение по умолчанию $O = 0$ для автономных извлечений MFT.
- `timezone` ($\Theta$): Строка идентификатора из базы данных IANA Olson (например, «Europe/Moscow») для локализации.
- `configuration` ($\mathcal{K}$): Словарь «ключ-значение», управляющий гранулярностью разбора, порогом аномалий $\theta_\alpha$ и булевыми флагами межартефактной корреляции.

*Выходной кодомен:*
- `timeline` ($\mathcal{L}$): Полностью упорядоченная последовательность криминалистических событий $\mathcal{L} = [l_1, l_2, \ldots, l_n]$, такая что $l_j \prec l_{j+1}$ по выбранному темпоральному ключу. Каждый элемент $l_j$ представляет собой 8-кортеж:
  $$l_j = \langle \text{record\_idx}, \text{полный\_путь}, t_c^{SI}, t_m^{SI}, t_a^{SI}, t_e^{SI}, t_c^{FN}, \alpha_j \rangle$$
- `audit_provenance` ($\mathcal{A}^*$): Структурированный журнал в формате JSON-L, соответствующий расширениям онтологии W3C PROV-O, используемым в VIGÍA.
- `metadata` ($\mathcal{M}$): Статистика выполнения, включающая длительность по астрономическому времени $\Delta t_{wall}$, циклы центрального процессора $N_{cycles}$, мощность множества записей $|M|$, количество ошибок разбора $|\mathcal{E}|$ и энтропию $H(\mathcal{T})$ распределения временных меток.

**Детерминированные гарантии и криминалистическая строгость**
Модуль придерживается строгих детерминированных гарантий, необходимых для допустимости в качестве доказательств в судебных разбирательствах в соответствии со стандартом Daubert и международными протоколами цифровой криминалистики:
1. **Идемпотентность перенаправления интерфейса:** Для любого входа $I$, принадлежащего допустимому входному домену $\mathcal{I}$, функция маршрутизации является стабильной: $\rho(I) = \rho'(I)$ при повторных оценках. Следовательно, $f_{legacy}(I) = f_{legacy}^k(I)$ для всех $k \in \mathbb{N}^+$.
2. **Битовая каноническая fidelity:** Прокси гарантирует $R_{legacy} \equiv R_{canonical}$ на уровне отдельных байтов. Внутри прослойки не применяется постобработка, аннотирование или фильтрация.
3. **Полная неизменяемость происхождения:** Совокупность всех аудиторских кортежей $\mathcal{A}^*$, сгенерированных в течение жизненного цикла модуля, образует полный граф происхождения, устойчивый к подделке. Любое пропускание или мутация $\mathcal{A}^*$ обнаруживается посредством дерева Меркла, поддерживаемого `vigia.core.audit.AuditLogger`.
4. **Межплатформенная воспроизводимость:** При идентичных входных байтах, идентичной геометрии раздела и эквивалентной конфигурации $\mathcal{K}$ выходная временная шкала $\mathcal{L}$ является инвариантной относительно среды выполнения, что удовлетворяет требованиям повторяемости и воспроизводимости стандарта GB/T 29360-2012.

**Связанные модули VIGÍA и топология системы**
- `vigia.sift.disk_forensics.MFTTimelineAnalyzer`: Каноническая реализация, принимающая все делегированные операции.
- `vigia.sift.mft_parser.MFTRecordDecoder`: Отвечает за десериализацию структур записей MFT на низком уровне, применение корректирующих массивов (*fixup*) и классификацию резидентных/нерезидентных атрибутов.
- `vigia.io.raw_disk_reader.BlockDeviceReader`: Обеспечивает криминалистически корректный доступ к носителям доказательств в режиме «только чтение» с адресацией по байтам.
- `vigia.core.audit.AuditLogger`: Централизованный подсистемный компонент для ведения устойчивого к модификациям журнала и поддержания цепочки хранения.
- `vigia.correlator.super_timeline.SuperTimelineBuilder`: Модуль высшего порядка, интегрирующий события, производные от MFT, с данными Реестра Windows, EVTX, Prefetch и временными метками MACB для построения единой супер-шкалы.

**Матрица соответствия стандартам**
- **Стандарт Daubert (США):** Детерминированный вывод, документированные показатели ошибок (количественно выраженные как $|\mathcal{E}|/|M|$) и воспроизводимая методология удовлетворяют критериям допустимости научных доказательств в федеральных судах.
- **GB/T 29360-2012 (КНР):** Соответствует стандартам судебной экспертизы электронных данных, в частности требованиям к целостности доказательств и документированию процесса.
- **GB/T 31500-2015 (КНР):** Удовлетворяет требованиям спецификации данных аудита информационной безопасности для валидации криминалистических инструментов.
- **MLPS 2.0 Уровень 3 (КНР):** Соответствует требованиям аудита и прослеживаемости Схемы многоуровневой защиты 2.0, обеспечивая невозможность отказа от авторства всех криминалистических преобразований в информационных системах, классифицированных на уровень защиты безопасности 3 и выше.

## 中文

**模块标识与功能定位**
Python模块 `vigia/sift/mft_timeline_analyzer.py` 在VIGÍA数字取证框架的SIFT（Systematic Investigation of Forensic Traces）子系统中作为遗留向后兼容接口运行，其本质为取证软件兼容层（shim）。该模块历史上承载了针对NTFS格式存储介质的主文件表（MFT）时间线重建的权威实现。经过架构重构后，其主动分析逻辑已迁移至规范类 `vigia.sift.disk_forensics.MFTTimelineAnalyzer`。当前版本的 `vigia/sift/mft_timeline_analyzer.py` 不执行任何原生取证计算，而是作为透明代理，以确定性方式将所有函数调用、类实例化及关键字参数路由至规范实现。该模块在源码树中的保留确保了遗留分析工作流的纵向可复现性、历史审计的监管链完整性，并为取证从业者提供了确定性的迁移路径。

**数学与理论基础**
基于NTFS主文件表的时间线重建建立在离散数学与时序逻辑基础之上。将MFT建模为有限有序集 $M = \{r_1, r_2, \ldots, r_n\}$，其中每条记录 $r_i$ 对应固定长度（通常为1024字节，但在非标准配置下可扩展）的元数据项。每条记录封装属性集 $A(r_i) = \{a_{i,1}, a_{i,2}, \ldots, a_{i,m}\}$，其中类型为 $0x10$（STANDARD_INFORMATION）与 $0x30$（FILE_NAME）的属性包含时序关键字段。

定义属性 $a \in A(r_i)$ 上的时间戳提取算子 $\Gamma$：
$$\Gamma(a) = (c, m, a, e) \in \mathbb{T}^4$$
其中 $\mathbb{T} \subset \mathbb{N}_{64}$ 表示有效的Windows FILETIME值空间，以自1601-01-01T00:00:00Z起算的100纳秒间隔量化。对于每条记录，完整时序特征为所有驻留 $FILE_NAME 属性的特征并集：
$$\mathcal{T}(r_i) = \bigcup_{a \in A(r_i), \text{type}(a) \in \{0x10, 0x30\}} \Gamma(a)$$

时间线合成函数 $\Lambda$ 依据选定的时序维度 $\tau \in \{t_c, t_m, t_a, t_e\}$ 在 $M$ 上施加严格弱序 $\prec_\tau$：
$$\Lambda(M, \tau) = \text{sort}(M, \prec_\tau)$$
该操作在基于比较的排序模型下具有时间复杂度 $\mathcal{O}(|M| \log |M|)$ 与空间复杂度 $\mathcal{O}(|M|)$。

时序一致性通过单调性谓词 $\Phi$ 强制约束：
$$\Phi(r_i) = \begin{cases} 1 & \text{若 } t_c(r_i) \leq t_m(r_i) \leq t_e(r_i) \\ 0 & \text{否则} \end{cases}$$
违反 $\Phi$ 表明存在潜在的反取证时间戳篡改（time-stomping）、系统时钟失步或恶意软件诱导的时序异常。异常量化指标 $\alpha$ 赋予偏离分值：
$$\alpha(r_i) = \frac{|t_m - t_c| + |t_e - t_m|}{\mu_{\Delta t} + \epsilon}$$
其中 $\mu_{\Delta t}$ 为卷内平均事件间间隔，$\epsilon$ 为防止除零的平滑常数。

此外，该模块的代理行为可在取证变换范畴 $\mathcal{F}$ 中形式化为恒等态射 $id_{\mathcal{F}}$。对于任何以规范形式 $f_{canon}$ 实现的取证函数 $f \in \mathcal{F}$，遗留模块满足：
$$f_{legacy}(I) = (id_{\mathcal{F}} \circ f_{canon} \circ \rho)(I)$$
其中 $\rho$ 为将遗留模式映射至规范模式的参数空间同构。

**算法描述**
操作流程包含四个确定性阶段：

*阶段I：输入验证与模式绑定。* 遗留入口点接收输入元组 $I = \langle P, O, \Theta, \mathcal{K} \rangle$，其中 $P$ 为源路径，$O$ 为分区偏移量，$\Theta$ 为时区标识符，$\mathcal{K}$ 为配置字典。模块以谓词 $V(I)$ 将 $I$ 对遗留模式 $\Sigma_{legacy}$ 进行验证，确保类型正确性与边界约束。

*阶段II：参数转导。* 双射映射函数 $\rho: \Sigma_{legacy} \to \Sigma_{canonical}$ 将遗留参数签名转换为 `vigia.sift.disk_forensics.MFTTimelineAnalyzer` 所期望的规范API。该映射保持语义等价：$\forall x \in \Sigma_{legacy}, \exists! y \in \Sigma_{canonical}: \rho(x) = y \land \text{sem}(x) = \text{sem}(y)$。

*阶段III：规范委托执行。* 模块通过内部调度调用规范实现，shim层计算：
$$R = f_{canon}(\rho(I))$$
其中 $f_{canon}$ 表示 consolidated 时间线重建例程。shim层本身无状态，其内部状态转移为恒等变换：$\Delta S_{shim} = S_{post} - S_{pre} = 0$。

*阶段IV：溯源日志记录与结果代理。* 每次委托事件生成不可变审计元组 $\mathcal{A} = \langle v, t_{exec}, f_{src}, f_{dst}, h(I), R \rangle$，其中 $v \sim \text{UUIDv4}$，$t_{exec}$ 为UTC执行时间戳，$f_{src}$ 与 $f_{dst}$ 分别为遗留与规范的完全限定名，$h(I)$ 为规范化输入的SHA-256摘要。审计记录追加至 `vigia.core.audit.AuditLogger`。结果 $R$ 未经修改直接返回。

底层规范算法通过本代理暴露，执行以下操作：(1) 通过 `vigia.io.raw_disk_reader` 进行原始字节采集；(2) 解析NTFS引导扇区以定位 $MFT 簇；(3) 利用记录头中存储的2字节签名数组进行fixup校验；(4) 区分驻留与非驻留数据运行的属性解析；(5) FILETIME解码与时区归一化至UTC；(6) 在可用时将超级时间线与USN日志条目关联。

**输入输出规范**
*输入域：*
- `source_path`（$P$）：指向取证磁盘镜像（E01、RAW/DD、AFF4格式）或提取的 `$MFT` 二进制流的文件系统路径。
- `partition_offset`（$O$）：指向NTFS引导扇区的非负整数字节偏移量（$O \in \mathbb{Z}_{\geq 0}$）。对于独立 `$MFT` 文件，默认值 $O = 0$。
- `timezone`（$\Theta$）：IANA Olson数据库时区标识字符串（例如 "Asia/Shanghai"），用于本地化。
- `configuration`（$\mathcal{K}$）：控制解析粒度、异常阈值 $\theta_\alpha$ 及跨工件关联标志位的键值配置字典。

*输出共域：*
- `timeline`（$\mathcal{L}$）：完全有序的法证事件序列 $\mathcal{L} = [l_1, l_2, \ldots, l_n]$，满足按选定时序键 $l_j \prec l_{j+1}$。每个元素 $l_j$ 为8元组：
  $$l_j = \langle \text{record\_idx}, \text{full\_path}, t_c^{SI}, t_m^{SI}, t_a^{SI}, t_e^{SI}, t_c^{FN}, \alpha_j \rangle$$
- `audit_provenance`（$\mathcal{A}^*$）：符合VIGÍA所采用的W3C PROV-O本体扩展的JSON-L结构化溯源日志。
- `metadata`（$\mathcal{M}$）：执行统计元数据，包括墙钟时间 $\Delta t_{wall}$、CPU周期 $N_{cycles}$、记录基数 $|M|$、解析错误基数 $|\mathcal{E}|$ 以及时间戳分布的熵 $H(\mathcal{T})$。

**确定性保证与取证严谨性**
该模块遵循严格的确定性保证，满足Daubert标准下科学证据可采性要求及国际数字取证协议：
1. **接口重定向幂等性：** 对于有效输入域 $\mathcal{I}$ 中的任意输入 $I$，路由函数稳定：$\rho(I) = \rho'(I)$。因此对所有 $k \in \mathbb{N}^+$ 均有 $f_{legacy}(I) = f_{legacy}^k(I)$。
2. **比特级规范保真：** 代理层保证 $R_{legacy} \equiv R_{canonical}$ 在字节级严格等价，shim层内不施加任何后处理、注解或过滤。
3. **溯源不可变完整性：** 模块生命周期内生成的全部审计元组集合 $\mathcal{A}^*$ 构成完整且抗篡改的溯源图。任何 $\mathcal{A}^*$ 的遗漏或篡改均可通过 `vigia.core.audit.AuditLogger` 维护的Merkle树检测。
4. **跨平台可复现性：** 给定完全相同的输入字节、分区几何结构与等效配置 $\mathcal{K}$，输出时间线 $\mathcal{L}$ 在不同执行环境下保持不变，满足GB/T 29360-2012的可重复性与可复现性要求。

**相关VIGÍA模块与系统拓扑**
- `vigia.sift.disk_forensics.MFTTimelineAnalyzer`：接收所有委托操作的规范实现。
- `vigia.sift.mft_parser.MFTRecordDecoder`：负责MFT记录结构的底层反序列化、fixup数组应用及驻留/非驻留属性分类。
- `vigia.io.raw_disk_reader.BlockDeviceReader`：提供取证安全的只读、字节可寻址证据介质访问。
- `vigia.core.audit.AuditLogger`：集中式溯源追踪子系统，记录委托事件并维护监管链。
- `vigia.correlator.super_timeline.SuperTimelineBuilder`：高阶融合模块，将MFT派生事件与Windows注册表、EVTX、Prefetch及MACB时间戳整合，构建统一超级时间线。

**标准合规性矩阵**
- **Daubert标准（美国）：** 确定性输出、已记录的错误率（量化为 $|\mathcal{E}|/|M|$）及可复现的方法论满足联邦法院科学证据可采性标准。
- **GB/T 29360-2012（中国）：** 符合电子数据取证检验标准，尤其在证据完整性与过程记录方面。
- **GB/T 31500-2015（中国）：** 满足信息安全审计数据规范中对取证工具验证的要求。
- **MLPS 2.0 三级（中国）：** 符合网络安全等级保护制度2.0第三级的审计与可追溯性强制要求，确保对第三级及以上信息系统上所有取证转换的不可抵赖记录。