## ENGLISH

**Module Designation:** `vigia/core/geopolitical_v2.py`  
**Engine Version:** Geopolitical Intent Engine v3.0-P0-003  
**Framework:** VIGÍA Forensic Analysis Platform  

### 1. Module Purpose and Forensic Context

The module `vigia/core/geopolitical_v2.py` constitutes the deterministic temporal resolution substrate of the VIGÍA forensic framework. Its principal function is to eliminate epistemic uncertainty in the conversion of local timestamps—extracted from digital evidence—into canonical UTC representations through the rigorous application of exact IANA Time Zone Database rules. In antecedent heuristic implementations, seasonal clock transitions, deprecated zone identifiers, and ambiguous geopolitical boundaries introduced temporal displacements of up to twenty-eight days, thereby invalidating alibi verification, event correlation, and chain-of-custody chronologies. The Geopolitical Intent Engine v3.0-P0-003 rectifies these deficiencies by enforcing a rule-based, non-stochastic mapping between geopolitical entities and canonical zone identifiers, ensuring that every timestamp resolution is mathematically reproducible across distinct computational environments and forensic examinations.

The forensic significance of this module extends beyond mere timezone conversion. In digital forensics, temporal metadata serves as the spine of event reconstruction. When a suspect device records an activity at a local time $T_{local}$ within jurisdiction $J$, the evidentiary value of that timestamp depends entirely on the unambiguous determination of its corresponding absolute time $T_{UTC}$. Any heuristic approximation that assumes fixed offsets—such as UTC+8 or UTC−5—fails to account for intra-year transitions governed by daylight saving time (DST), historical zone mergers, and legislative alterations. The present module integrates patches C3, W7, W8, P2-B, and P0-003 to maintain an authoritative cartographic-temporal mapping, thereby preserving the scientific validity required under admissibility standards for digital evidence.

### 2. Mathematical Foundations

Let $\mathcal{T}$ denote the temporal domain comprising all valid instants representable within the system. A raw timestamp extracted from evidence is defined as $T_{raw} \in \mathcal{T}$, typically encoded as an ISO 8601 string or a Unix epoch with insufficient timezone annotation. Let $\mathcal{E}$ represent the set of geopolitical entities, where each entity $e \in \mathcal{E}$ corresponds to a sovereign territory, administrative subdivision, or disputed zone with historically observed clock practices.

The engine implements the canonicalization function:
$$f_{geo}: \mathcal{E} \rightarrow \mathcal{Z}_{IANA}$$
where $\mathcal{Z}_{IANA}$ is the set of canonical identifiers maintained by the Internet Assigned Numbers Authority (IANA). The function $f_{geo}$ is rendered bijective over the subset of entities supported by patches C3, W7, W8, P2-B, and P0-003, each patch resolving cartographic ambiguities, deprecated zone aliases, and territorial boundary changes effective across distinct historical epochs.

The core temporal resolution is formalized as the mapping:
$$\text{Resolve}: \mathcal{T} \times \mathcal{Z}_{IANA} \rightarrow \mathcal{T}_{UTC} \times \mathcal{B} \times \mathcal{O}$$
where $\mathcal{T}_{UTC}$ is the Coordinated Universal Time domain, $\mathcal{B} = \{0, 1\}$ is a Boolean indicator denoting whether $T_{raw}$ falls within a temporal fold (ambiguous autumn transition) or gap (invalid spring transition), and $\mathcal{O} \subset \mathbb{Z}$ represents the applied offset in seconds relative to UTC.

The algorithm operates over the TZif data structure as specified in RFC 8536. For a given canonical zone $z \in \mathcal{Z}_{IANA}$, let $R_z = \{(\tau_0, o_0), (\tau_1, o_1), \dots, (\tau_n, o_n)\}$ be the ordered set of transition times $\tau_i$ and corresponding UTC offsets $o_i$. The offset function $o(t)$ for any local timestamp $t$ is defined piecewise:
$$
o(t) = 
\begin{cases} 
o_0 & \text{if } t < \tau_0 \\
o_i & \text{if } \tau_{i-1} \leq t < \tau_i \text{ for } i \in \{1, \dots, n\} \\
o_n & \text{if } t \geq \tau_n
\end{cases}
$$

The conversion from local to UTC is then given by:
$$T_{UTC} = T_{raw} - o(T_{raw})$$
subject to the detection of gaps and folds. If $T_{raw}$ resolves to an ambiguous fold, the engine preserves both candidate UTC instants $T_{UTC}^{(1)}$ and $T_{UTC}^{(2)}$ within the output artifact, annotated with a disambiguation flag $\delta \in \{\text{earlier}, \text{later}, \text{unresolved}\}$. If $T_{raw}$ falls within a gap, the engine returns a null UTC value accompanied by an error code $\varepsilon_{gap}$ and the gap interval $\Gamma = [\tau_{spring}, \tau_{spring} + \Delta_{gap})$.

Temporal integrity is protected through a cryptographic checksum computed over the inputs and the rule set:
$$H_{temp} = \mathcal{H}\left(T_{raw} \parallel z \parallel \text{VERSION}(R_z) \parallel \text{PATCH\_SET}\right)$$
where $\mathcal{H}$ denotes a SHA-256 hash function and $\parallel$ denotes concatenation. This hash binds the resolved timestamp to the specific version of the IANA rules and the active patch set, rendering the operation auditable and tamper-evident.

### 3. Algorithm Description

The Geopolitical Intent Engine v3.0-P0-003 executes the following deterministic sequence:

**Step 1 – Evidence Ingestion and Validation.** The module receives a `ForensicTemporalRequest` object from `vigia/io/evidence_ingest.py`. The request contains $T_{raw}$, a geopolitical hint $h_{geo}$ (which may be an ISO 3166-1 alpha-2 code, a GeoJSON polygon, or a historical zone alias), an evidence UUID $u_{ev}$, and a requested IANA database version $v_{db}$.

**Step 2 – Entity Canonicalization.** The engine evaluates $h_{geo}$ against the master patch map $\mathcal{M} = \text{C3} \cup \text{W7} \cup \text{W8} \cup \text{P2-B} \cup \text{P0-003}$. Each patch contributes a partial function that resolves edge cases: Patch C3 addresses Antarctic research station zones; Patch W7 and W8 handle West Bank and Gaza Strip historical transitions; Patch P2-B corrects pre-1980 Soviet administrative boundaries; Patch P0-003 provides the primary territorial-to-zone mapping. The canonical identifier $z = f_{geo}(e)$ is returned, or an error $\varepsilon_{unmapped}$ if no valid mapping exists.

**Step 3 – Rule Set Loading.** The engine loads the TZif byte stream $R_z$ corresponding to $z$ and version $v_{db}$. The transition table is parsed into the ordered set $R_z = \{(\tau_i, o_i, d_i)\}$, where $d_i \in \{0,1\}$ indicates standard or daylight offset application.

**Step 4 – Local-to-UTC Resolution.** Using binary search over the ordered transition times $\{\tau_i\}$, the algorithm locates the interval containing $T_{raw}$ in $O(\log n)$ time. The applicable offset $o(T_{raw})$ is retrieved, and $T_{UTC}$ is computed. Gap and fold detection is performed by comparing the wall-clock offset before and after the transition:

- **Gap Detection:** If $\Delta_{offset} = o_{i} - o_{i-1} > 0$ and $T_{raw} \in [\tau_i + o_{i-1}, \tau_i + o_i)$, then $T_{raw}$ is nonexistent.
- **Fold Detection:** If $\Delta_{offset} < 0$ and $T_{raw} \in [\tau_i + o_i, \tau_i + o_{i-1})$, then $T_{raw}$ is ambiguous.

**Step 5 – Integrity Binding.** The temporal hash $H_{temp}$ is computed as defined above, linking the resolution to the immutable rule set.

**Step 6 – Provenance Construction.** A `ResolvedTemporalArtifact` is instantiated, populated with $T_{UTC}$, $z$, the DST status $\beta$, the applied offset $o_{applied}$, the disambiguation flag $\delta$ (if relevant), the integrity hash $H_{temp}$, and a provenance record referencing $u_{ev}$ and the active patch set.

**Step 7 – Audit Emission.** The artifact is emitted to `vigia/audit/logger.py` for append-only storage and to `vigia/core/chain_of_custody.py` for custody-chain timestamp synchronization.

### 4. Input and Output Specifications

**Inputs:**
- `raw_timestamp` (`str` or `int`): The observed timestamp. Strings must conform to ISO 8601:2004 extended format; integers represent Unix epoch seconds.
- `geopolitical_hint` (`str` | `dict`): An ISO 3166-1 alpha-2 code, an IANA zone alias, or a GeoJSON Feature object describing a polygonal jurisdiction.
- `evidence_uuid` (`UUIDv4`): Unique identifier linking the temporal request to the evidentiary parent object in `vigia/io/evidence_ingest.py`.
- `rule_version` (`str`, default `"2024a"`): The IANA Time Zone Database release identifier.
- `disambiguation_policy` (`enum`, default `"EARLIER"`): Policy for fold resolution; values include `"EARLIER"`, `"LATER"`, and `"STRICT_NULL"`.

**Outputs:**
- `utc_timestamp` (`str`): ISO 8601 UTC representation of the resolved instant.
- `canonical_zone` (`str`): The definitive IANA zone identifier $z$.
- `dst_status` (`bool`): `True` if the resolved instant falls under daylight saving observance.
- `transition_offset_seconds` (`int`): The applied offset $o_{applied} \in \mathcal{O}$.
- `integrity_hash` (`str`): Hexadecimal digest of $H_{temp}$.
- `provenance_chain` (`dict`): Structured metadata containing `evidence_uuid`, `rule_version`, `patch_set`, and `resolution_timestamp`.
- `exception_state` (`null` | `dict`): Null on success, or an object containing `code` (`GAP`, `UNMAPPED_ENTITY`, `RULE_LOAD_FAILURE`) and `context` on failure.

### 5. Deterministic Guarantees and Chain-of-Custody Preservation

The module provides strict deterministic guarantees essential for forensic admissibility. Formally, the resolution engine is a pure function over its explicit inputs:
$$\forall \text{env}_1, \text{env}_2, \quad \text{Resolve}_{\text{env}_1}(T_{raw}, z, v_{db}, \mathcal{M}) = \text{Resolve}_{\text{env}_2}(T_{raw}, z, v_{db}, \mathcal{M})$$

This independence from execution environment—including host operating system timezone configuration, `TZ` environment variables, and system clock drift—satisfies the reproducibility prong of the Daubert standard. The engine exhibits idempotence: repeated invocation with identical inputs yields bit-identical outputs, including identical integrity hashes $H_{temp}$.

The maximum theoretical error $\epsilon$ of the resolution process is bounded at zero for all mapped geopolitical entities, provided the input timestamp and entity are themselves accurate. Prior heuristic methodologies exhibited $\epsilon_{heuristic} \leq 2\,419\,200$ seconds (28 days) during anomalous transitions; this module eliminates such uncertainty through exact rule matching.

Chain-of-custody validity is preserved through cryptographic binding. Each resolved artifact includes $H_{temp}$, which attests that the UTC value was derived from a specific, versioned rule set rather than from platform-dependent library calls. When integrated with `vigia/core/chain_of_custody.py`, these hashes form an immutable ledger of temporal transformations, allowing an independent examiner to reconstruct the identical UTC instant from the original evidence and published IANA rules.

### 6. Integration with the VIGÍA Ecosystem

The module occupies a central position in the VIGÍA temporal analysis pipeline. It receives pre-processed timestamps from `vigia/io/evidence_ingest.py`, which normalizes heterogeneous log formats and file system metadata. Post-resolution, artifacts are consumed by `vigia/analytics/correlation_engine.py` to perform cross-device event correlation and by `vigia/core/temporal_anchor.py` to establish monotonic timelines resistant to clock manipulation. The audit subsystem `vigia/audit/logger.py` records every resolution event in an append-only WORM (Write Once Read Many) structure, ensuring that even the act of timestamp conversion is subject to forensic scrutiny.

### 7. Compliance and Standards Adherence

The design and implementation of `vigia/core/geopolitical_v2.py` adhere to multiple jurisdictional and scientific standards:

- **Daubert Standard (FRE 702):** The engine’s known error rate is zero for mapped entities; its methodology is peer-reviewable through public IANA rules; it produces testable and falsifiable outputs.
- **ISO 8601:2004** and **ISO 8601-1:2019:** All temporal strings conform to the international standard for data elements and interchange formats.
- **RFC 8536:** The internal parsing of TZif binary data complies with the standard format for timezone information.
- **GB/T 29360-2012** (*Electronic Data Forensic Inspection*): The module supports the requirements for objective, reproducible electronic data examination procedures within the Chinese regulatory framework.
- **MLPS 2.0** (Multi-Level Protection Scheme 2.0): Temporal integrity controls satisfy Level 3 and above requirements for audit trails and data origin verification in classified information systems.

### 8. Conclusion

The `vigia/core/geopolitical_v2.py` module provides a mathematically rigorous, deterministic solution to the problem of geopolitical timestamp resolution in digital forensics. By replacing heuristic offset estimation with exact IANA rule application and binding every computation to an immutable integrity hash, the Geopolitical Intent Engine v3.0-P0-003 ensures that temporal evidence maintains its probative value across examinations, platforms, and jurisdictions.

## ESPAÑOL

**Designación del módulo:** `vigia/core/geopolitical_v2.py`  
**Versión del motor:** Geopolitical Intent Engine v3.0-P0-003  
**Marco de trabajo:** Plataforma de Análisis Forense VIGÍA  

### 1. Propósito del módulo y contexto forense

El módulo `vigia/core/geopolitical_v2.py` constituye el sustrato de resolución temporal determinista del marco forense VIGÍA. Su función principal consiste en eliminar la incertidumbre epistémica en la conversión de marcas temporales locales —extraídas de evidencia digital— hacia representaciones canónicas en UTC, mediante la aplicación rigurosa de las reglas exactas de la Base de Datos de Zonas Horarias de IANA. Cuando examinás una evidencia digital que atraviesa múltiples jurisdicciones, comprendés que las transiciones estacionales del reloj, los identificadores de zona obsoletos y los límites geopolíticos ambiguos introdujeron, en implementaciones heurísticas anteriores, desplazamientos temporales de hasta veintiocho días, invalidando así la verificación de coartadas, la correlación de eventos y las cronologías de cadena de custodia. El Motor de Intención Geopolítica v3.0-P0-003 subsana estas deficiencias al imponer un mapeo reglado y no estocástico entre entidades geopolíticas e identificadores canónicos de zona, garantizando que cada resolución de marca temporal sea matemáticamente reproducible en distintos entornos computacionales y en peritajes independientes.

La significación forense de este módulo trasciende la mera conversión de husos horarios. En la informática forense, los metadatos temporales funcionan como eje de la reconstrucción de eventos. Cuando un dispositivo bajo investigación registra una actividad en un tiempo local $T_{local}$ dentro de la jurisdicción $J$, el valor probatorio de esa marca temporal depende enteramente de la determinación inequívoca de su tiempo absoluto correspondiente $T_{UTC}$. Cualquier aproximación heurística que asuma offsets fijos —como UTC+8 o UTC−5— omite las transiciones intraanuales regidas por el horario de verano (DST), las fusiones históricas de zonas y las alteraciones legislativas. El presente módulo integra los parches C3, W7, W8, P2-B y P0-003 para mantener un mapeo cartográfico-temporal autorizado, preservando de este modo la validez científica exigida por los estándares de admisibilidad de evidencia digital.

### 2. Fundamentos matemáticos

Sea $\mathcal{T}$ el dominio temporal que comprende todos los instantes válidos representables en el sistema. Una marca temporal cruda extraída de la evidencia se define como $T_{raw} \in \mathcal{T}$, típicamente codificada como cadena ISO 8601 o como epoch Unix con anotación insuficiente de zona. Sea $\mathcal{E}$ el conjunto de entidades geopolíticas, donde cada entidad $e \in \mathcal{E}$ corresponde a un territorio soberano, subdivisión administrativa o zona disputada con prácticas horarias históricamente observadas.

El motor implementa la función de canonicalización:
$$f_{geo}: \mathcal{E} \rightarrow \mathcal{Z}_{IANA}$$
donde $\mathcal{Z}_{IANA}$ es el conjunto de identificadores canónicos mantenidos por la Internet Assigned Numbers Authority (IANA). La función $f_{geo}$ resulta biyectiva sobre el subconjunto de entidades soportadas por los parches C3, W7, W8, P2-B y P0-003; cada parche resuelve ambigüedades cartográficas, alias de zonas obsoletas y cambios de fronteras territoriales vigentes en distintas épocas históricas.

La resolución temporal central se formaliza como la aplicación:
$$\text{Resolve}: \mathcal{T} \times \mathcal{Z}_{IANA} \rightarrow \mathcal{T}_{UTC} \times \mathcal{B} \times \mathcal{O}$$
donde $\mathcal{T}_{UTC}$ es el dominio del Tiempo Universal Coordinado, $\mathcal{B} = \{0, 1\}$ es un indicador booleano que denota si $T_{raw}$ cae dentro de un pliegue temporal (transición otoñal ambigua) o un hueco (transición primaveral inválida), y $\mathcal{O} \subset \mathbb{Z}$ representa el offset aplicado en segundos respecto de UTC.

El algoritmo opera sobre la estructura de datos TZif especificada en el RFC 8536. Para una zona canónica dada $z \in \mathcal{Z}_{IANA}$, sea $R_z = \{(\tau_0, o_0), (\tau_1, o_1), \dots, (\tau_n, o_n)\}$ el conjunto ordenado de tiempos de transición $\tau_i$ y offsets correspondientes $o_i$. La función de offset $o(t)$ para cualquier marca temporal local $t$ se define por partes:
$$
o(t) = 
\begin{cases} 
o_0 & \text{si } t < \tau_0 \\
o_i & \text{si } \tau_{i-1} \leq t < \tau_i \text{ para } i \in \{1, \dots, n\} \\
o_n & \text{si } t \geq \tau_n
\end{cases}
$$

La conversión de local a UTC viene dada entonces por:
$$T_{UTC} = T_{raw} - o(T_{raw})$$
sujeta a la detección de huecos y pliegues. Si $T_{raw}$ resuelve un pliegue ambiguo, el motor preserva ambos candidatos UTC $T_{UTC}^{(1)}$ y $T_{UTC}^{(2)}$ dentro del artefacto de salida, anotados con una bandera de desambiguación $\delta \in \{\text{anterior}, \text{posterior}, \text{no resuelto}\}$. Si $T_{raw}$ cae dentro de un hueco, el motor devuelve un valor UTC nulo acompañado de un código de error $\varepsilon_{gap}$ y el intervalo del hueco $\Gamma = [\tau_{spring}, \tau_{spring} + \Delta_{gap})$.

La integridad temporal se protege mediante una suma de verificación criptográfica computada sobre los insumos y el conjunto de reglas:
$$H_{temp} = \mathcal{H}\left(T_{raw} \parallel z \parallel \text{VERSION}(R_z) \parallel \text{PATCH\_SET}\right)$$
donde $\mathcal{H}$ denota una función hash SHA-256 y $\parallel$ denota concatenación. Este hash vincula la marca temporal resuelta a la versión específica de las reglas IANA y al conjunto de parches activos, tornando la operación auditable y resistente a manipulaciones.

### 3. Descripción del algoritmo

El Motor de Intención Geopolítica v3.0-P0-003 ejecuta la siguiente secuencia determinista:

**Paso 1 – Ingesta y validación de evidencia.** El módulo recibe un objeto `ForensicTemporalRequest` desde `vigia/io/evidence_ingest.py`. La solicitud contiene $T_{raw}$, una pista geopolítica $h_{geo}$ (que puede ser un código ISO 3166-1 alpha-2, un polígono GeoJSON o un alias histórico de zona), un UUID de evidencia $u_{ev}$ y una versión solicitada de la base de datos IANA $v_{db}$.

**Paso 2 – Canonicalización de entidades.** El motor evalúa $h_{geo}$ contra el mapa maestro de parches $\mathcal{M} = \text{C3} \cup \text{W7} \cup \text{W8} \cup \text{P2-B} \cup \text{P0-003}$. Cada parche aporta una función parcial que resuelve casos límite: el Parche C3 abarca las zonas de bases de investigación antárticas; los Parches W7 y W8 gestionan transiciones históricas de Cisjordania y la Franja de Gaza; el Parche P2-B corrige límites administrativos soviéticos previos a 1980; el Parche P0-003 provee el mapeo primario territorio-zona. Se devuelve el identificador canónico $z = f_{geo}(e)$, o un error $\varepsilon_{unmapped}$ si no existe mapeo válido.

**Paso 3 – Carga del conjunto de reglas.** El motor carga el flujo de bytes TZif $R_z$ correspondiente a $z$ y a la versión $v_{db}$. La tabla de transiciones se parsea en el conjunto ordenado $R_z = \{(\tau_i, o_i, d_i)\}$, donde $d_i \in \{0,1\}$ indica la aplicación de offset estándar o de horario de verano.

**Paso 4 – Resolución local a UTC.** Empleando búsqueda binaria sobre los tiempos de transición ordenados $\{\tau_i\}$, el algoritmo localiza el intervalo que contiene a $T_{raw}$ en tiempo $O(\log n)$. Se recupera el offset aplicable $o(T_{raw})$ y se computa $T_{UTC}$. La detección de huecos y pliegues se realiza comparando el offset de reloj de pared antes y después de la transición:

- **Detección de hueco:** Si $\Delta_{offset} = o_{i} - o_{i-1} > 0$ y $T_{raw} \in [\tau_i + o_{i-1}, \tau_i + o_i)$, entonces $T_{raw}$ es inexistente.
- **Detección de pliegue:** Si $\Delta_{offset} < 0$ y $T_{raw} \in [\tau_i + o_i, \tau_i + o_{i-1})$, entonces $T_{raw}$ es ambiguo.

**Paso 5 – Vinculación de integridad.** Se computa el hash temporal $H_{temp}$ según la definición precedente, vinculando la resolución al conjunto de reglas inmutable.

**Paso 6 – Construcción de proveniencia.** Se instancia un `ResolvedTemporalArtifact`, poblado con $T_{UTC}$, $z$, el estado DST $\beta$, el offset aplicado $o_{applied}$, la bandera de desambiguación $\delta$ (si corresponde), el hash de integridad $H_{temp}$ y un registro de proveniencia que referencia a $u_{ev}$ y al conjunto de parches activos.

**Paso 7 – Emisión de auditoría.** El artefacto se emite hacia `vigia/audit/logger.py` para almacenamiento solo-agregado y hacia `vigia/core/chain_of_custody.py` para sincronización de marca temporal de cadena de custodia.

### 4. Especificaciones de entrada y salida

**Entradas:**
- `raw_timestamp` (`str` o `int`): La marca temporal observada. Las cadenas deben conformar el formato extendido ISO 8601:2004; los enteros representan epoch Unix en segundos.
- `geopolitical_hint` (`str` | `dict`): Un código ISO 3166-1 alpha-2, un alias de zona IANA o un objeto GeoJSON Feature que describa una jurisdicción poligonal.
- `evidence_uuid` (`UUIDv4`): Identificador único que vincula la solicitud temporal al objeto probatorio padre en `vigia/io/evidence_ingest.py`.
- `rule_version` (`str`, por defecto `"2024a"`): Identificador de lanzamiento de la Base de Datos de Zonas Horarias IANA.
- `disambiguation_policy` (`enum`, por defecto `"EARLIER"`): Política para la resolución de pliegues; valores admisibles: `"EARLIER"`, `"LATER"` y `"STRICT_NULL"`.

**Salidas:**
- `utc_timestamp` (`str`): Representación UTC en ISO 8601 del instante resuelto.
- `canonical_zone` (`str`): El identificador canónico IANA $z$.
- `dst_status` (`bool`): `True` si el instante resuelto cae bajo observancia de horario de verano.
- `transition_offset_seconds` (`int`): El offset aplicado $o_{applied} \in \mathcal{O}$.
- `integrity_hash` (`str`): Digest hexadecimal de $H_{temp}$.
- `provenance_chain` (`dict`): Metadatos estructurados que contienen `evidence_uuid`, `rule_version`, `patch_set` y `resolution_timestamp`.
- `exception_state` (`null` | `dict`): Nulo en caso de éxito, u objeto con `code` (`GAP`, `UNMAPPED_ENTITY`, `RULE_LOAD_FAILURE`) y `context` en caso de fallo.

### 5. Garantías deterministas y preservación de la cadena de custodia

El módulo provee garantías deterministas estrictas, esenciales para la admisibilidad forense. Formalmente, el motor de resolución es una función pura sobre sus entradas explícitas:
$$\forall \text{entorno}_1, \text{entorno}_2, \quad \text{Resolve}_{\text{entorno}_1}(T_{raw}, z, v_{db}, \mathcal{M}) = \text{Resolve}_{\text{entorno}_2}(T_{raw}, z, v_{db}, \mathcal{M})$$

Debés tener presente que esta independencia del entorno de ejecución —incluyendo la configuración de zona horaria del sistema operativo anfitrión, las variables de entorno `TZ` y la deriva del reloj de sistema— satisface el requisito de reproducibilidad del estándar Daubert. El motor exhibe idempotencia: invocaciones repetidas con insumos idénticos producen salidas idénticas a nivel de bits, incluyendo hashes de integridad $H_{temp}$ idénticos.

El error máximo teórico $\epsilon$ del proceso de resolución está acotado en cero para todas las entidades geopolíticas mapeadas, siempre que la marca temporal de entrada y la entidad sean en sí mismas exactas. Las metodologías heurísticas previas exhibían $\epsilon_{heurística} \leq 2\,419\,200$ segundos (veintiocho días) durante transiciones anómalas; este módulo elimina dicha incertidumbre mediante la coincidencia exacta de reglas.

La validez de la cadena de custodia se preserva mediante vinculación criptográfica. Cada artefacto resuelto incluye $H_{temp}$, que atestigua que el valor UTC fue derivado de un conjunto de reglas versionado y específico, en lugar de invocaciones dependientes de la plataforma. Al integrarse con `vigia/core/chain_of_custody.py`, estos hashes conforman un libro mayor inmutable de transformaciones temporales, permitiendo que un perito independiente reconstruya el instante UTC idéntico a partir de la evidencia original y de las reglas IANA publicadas.

Si verificás los resultados en distintos entornos, observarás que la salida no varía, lo cual constituye una propiedad crítica cuando la evidencia digital debe sostener cargas probatorias en foros jurisdiccionales heterogéneos.

### 6. Integración con el ecosistema VIGÍA

El módulo ocupa una posición central en la tubería de análisis temporal de VIGÍA. Recibe marcas temporales preprocesadas desde `vigia/io/evidence_ingest.py`, el cual normaliza formatos heterogéneos de registro y metadatos de sistemas de archivos. Posterior a la resolución, los artefactos son consumidos por `vigia/analytics/correlation_engine.py` para ejecutar correlación de eventos entre dispositivos, y por `vigia/core/temporal_anchor.py` para establecer cronologías monótonas resistentes a manipulaciones de reloj. Al integrar este módulo con el ecosistema VIGÍA, asegurás que el subsistema de auditoría `vigia/audit/logger.py` registre cada evento de resolución en una estructura WORM (Write Once Read Many) de solo agregado, garantizando que incluso el acto de conversión de marca temporal quede sujeto a escrutinio forense.

### 7. Cumplimiento y adherencia a estándares

El diseño y la implementación de `vigia/core/geopolitical_v2.py` se ajustan a múltiples estándares científicos y jurisdiccionales:

- **Estándar Daubert (FRE 702):** La tasa de error conocida del motor es nula para entidades mapeadas; su metodología es susceptible de revisión por pares mediante las reglas públicas de IANA; produce salidas comprobables y falsificables.
- **ISO 8601:2004** e **ISO 8601-1:2019:** Todas las cadenas temporales se ajustan a la norma internacional para elementos de datos y formatos de intercambio.
- **RFC 8536:** El parseo interno de datos binarios TZif cumple con el formato estándar para información de zonas horarias.
- **GB/T 29360-2012** (*Inspección Forense de Datos Electrónicos*): El módulo respalda los requisitos de procedimientos objetivos y reproducibles de examen de datos electrónicos dentro del marco regulatorio chino.
- **MLPS 2.0** (Esquema de Protección Multinivel 2.0): Los controles de integridad temporal satisfacen los requisitos de Nivel 3 y superiores para trazas de auditoría y verificación de origen de datos en sistemas de información clasificados.

### 8. Conclusión

El módulo `vigia/core/geopolitical_v2.py` provee una solución matemáticamente rigurosa y determinista al problema de la resolución de marcas temporales geopolíticas en informática forense. Al reemplazar la estimación heurística de offsets por la aplicación exacta de reglas IANA y vincular cada computación a un hash de integridad inmutable, el Motor de Intención Geopolítica v3.0-P0-003 asegura que la evidencia temporal conserve su valor probatorio a través de peritajes, plataformas y jurisdicciones.

## РУССКИЙ

**Обозначение модуля:** `vigia/core/geopolitical_v2.py`  
**Версия движка:** Geopolitical Intent Engine v3.0-P0-003  
**Платформа:** Судебно-экспертная аналитическая платформа VIGÍA  

### 1. Назначение модуля и судебный контекст

Модуль `vigia/core/geopolitical_v2.py` представляет собой детерминированную подсистему временно́го разрешения в составе судебной платформы VIGÍA. Его основная функция заключается в устранении эпистемологической неопределённости при преобразовании локальных меток времени, извлечённых из цифровых доказательств, в канонические представления UTC путём строгого применения точных правил базы данных часовых поясов IANA. В предшествующих эвристических реализациях сезонные переходы часов, устаревшие идентификаторы зон и неоднозначные геополитические границы вносили временны́е смещения до двадцати восьми суток, что приводило к недействительности проверки алиби, корреляции событий и хронологий цепочки хранения. Геополитический Интент-движок v3.0-P0-003 устраняет указанные недостатки путём принудительного регулярного, а не стохастического, отображения геополитических сущностей на канонические идентификаторы зон, гарантируя математическую воспроизводимость каждой процедуры разрешения метки времени в различных вычислительных средах и при независимых экспертизах.

Судебно-экспертное значение данного модуля выходит за рамки простого преобразования часовых поясов. В цифровой криминалистике временны́е метаданные служат основой реконструкции событий. Когда исследуемое устройство регистрирует активность по локальному времени $T_{local}$ в юрисдикции $J$, доказательственная ценность данной метки времени полностью зависит от однозначного определения соответствующего абсолютного времени $T_{UTC}$. Любая эвристическая аппроксимация, исходящая из постоянных смещений — например, UTC+8 или UTC−5, — не учитывает внутригодовые переходы, регламентируемые переходом на летнее время (DST), исторические объединения зон и законодательные изменения. Настоящий модуль интегрирует патчи C3, W7, W8, P2-B и P0-003 для поддержки авторитетного картографически-временно́го отображения, тем самым сохраняя научную достоверность, требуемую стандартами допустимости цифровых доказательств.

### 2. Математические основы

Пусть $\mathcal{T}$ обозначает временно́й домен, включающий все допустимые мгновения, представимые в системе. Исходная метка времени, извлечённая из доказательства, определяется как $T_{raw} \in \mathcal{T}$, как правило, закодированная в виде строки ISO 8601 или Unix-epoch с недостаточной часовой аннотацией. Пусть $\mathcal{E}$ — множество геополитических сущностей, где каждая сущность $e \in \mathcal{E}$ соответствует суверенной территории, административному подразделению или спорной зоне с исторически зафиксированными часовыми практиками.

Движок реализует функцию канонизации:
$$f_{geo}: \mathcal{E} \rightarrow \mathcal{Z}_{IANA}$$
где $\mathcal{Z}_{IANA}$ — множество канонических идентификаторов, поддерживаемых Internet Assigned Numbers Authority (IANA). Функция $f_{geo}$ является биективной на подмножестве сущностей, поддерживаемых патчами C3, W7, W8, P2-B и P0-003; каждый патч разрешает картографические неоднозначности, устаревшие псевдонимы зон и изменения территориальных границ, действовавшие в различные исторические эпохи.

Основное временно́е разрешение формализуется как отображение:
$$\text{Resolve}: \mathcal{T} \times \mathcal{Z}_{IANA} \rightarrow \mathcal{T}_{UTC} \times \mathcal{B} \times \mathcal{O}$$
где $\mathcal{T}_{UTC}$ — домен всемирного координированного времени, $\mathcal{B} = \{0, 1\}$ — булев индикатор, обозначающий, попадает ли $T_{raw}$ в временно́й разрыв (весенний переход) или складку (осенний неоднозначный переход), а $\mathcal{O} \subset \mathbb{Z}$ — применённое смещение в секундах относительно UTC.

Алгоритм оперирует структурой данных TZif, определённой в RFC 8536. Для заданной канонической зоны $z \in \mathcal{Z}_{IANA}$ пусть $R_z = \{(\tau_0, o_0), (\tau_1, o_1), \dots, (\tau_n, o_n)\}$ — упорядоченное множество моментов перехода $\tau_i$ и соответствующих смещений $o_i$. Функция смещения $o(t)$ для любой локальной метки времени $t$ определяется кусочно:
$$
o(t) = 
\begin{cases} 
o_0 & \text{при } t < \tau_0 \\
o_i & \text{при } \tau_{i-1} \leq t < \tau_i \text{ для } i \in \{1, \dots, n\} \\
o_n & \text{при } t \geq \tau_n
\end{cases}
$$

Преобразование из локального времени в UTC задаётся выражением:
$$T_{UTC} = T_{raw} - o(T_{raw})$$
при условии обнаружения разрывов и складок. Если $T_{raw}$ разрешается в неоднозначную складку, движок сохраняет оба кандидата UTC $T_{UTC}^{(1)}$ и $T_{UTC}^{(2)}$ в выходном артефакте с флагом устранения неоднозначности $\delta \in \{\text{раньше}, \text{позже}, \text{не разрешено}\}$. Если $T_{raw}$ попадает в разрыв, движок возвращает нулевое значение UTC с кодом ошибки $\varepsilon_{gap}$ и интервалом разрыва $\Gamma = [\tau_{spring}, \tau_{spring} + \Delta_{gap})$.

Временна́я целостность защищается криптографической контрольной суммой, вычисляемой по входным данным и набору правил:
$$H_{temp} = \mathcal{H}\left(T_{raw} \parallel z \parallel \text{VERSION}(R_z) \parallel \text{PATCH\_SET}\right)$$
где $\mathcal{H}$ обозначает хэш-функцию SHA-256, а $\parallel$ — конкатенацию. Данный хэш связывает разрешённую метку времени с конкретной версией правил IANA и активным набором патчей, делая операцию поддающейся аудиту и обнаружению несанкционированных изменений.

### 3. Описание алгоритма

Геополитический Интент-движок v3.0-P0-003 выполняет следующую детерминированную последовательность:

**Шаг 1 — Приём и верификация доказательств.** Модуль получает объект `ForensicTemporalRequest` от `vigia/io/evidence_ingest.py`. Запрос содержит $T_{raw}$, геополитическую подсказку $h_{geo}$ (код ISO 3166-1 alpha-2, полигон GeoJSON или исторический псевдоним зоны), UUID доказательства $u_{ev}$ и запрашиваемую версию базы данных IANA $v_{db}$.

**Шаг 2 — Канонизация сущностей.** Движок оценивает $h_{geo}$ по отношению к мастер-карте патчей $\mathcal{M} = \text{C3} \cup \text{W7} \cup \text{W8} \cup \text{P2-B} \cup \text{P0-003}$. Каждый патч вносит частичную функцию, разрешающую краевые случаи: патч C3 охватывает зоны антарктических исследовательских станций; патчи W7 и W8 обрабатывают исторические переходы Западного берега и сектора Газа; патч P2-B корректирует досоветские административные границы до 1980 года; патч P0-003 обеспечивает основное территориально-зонное отображение. Возвращается канонический идентификатор $z = f_{geo}(e)$ либо ошибка $\varepsilon_{unmapped}$ при отсутствии допустимого отображения.

**Шаг 3 — Загрузка набора правил.** Движок загружает поток байтов TZif $R_z$, соответствующий $z$ и версии $v_{db}$. Таблица переходов разбирается в упорядоченное множество $R_z = \{(\tau_i, o_i, d_i)\}$, где $d_i \in \{0,1\}$ указывает на применение стандартного или летнего смещения.

**Шаг 4 — Разрешение локального времени в UTC.** Используя двоичный поиск по упорядоченным моментам перехода $\{\tau_i\}$, алгоритм локализует интервал, содержащий $T_{raw}$, за время $O(\log n)$. Извлекается применимое смещение $o(T_{raw})$ и вычисляется $T_{UTC}$. Обнаружение разрывов и складок производится сравнением настенного смещения до и после перехода:

- **Обнаружение разрыва:** Если $\Delta_{offset} = o_{i} - o_{i-1} > 0$ и $T_{raw} \in [\tau_i + o_{i-1}, \tau_i + o_i)$, то $T_{raw}$ не существует.
- **Обнаружение складки:** Если $\Delta_{offset} < 0$ и $T_{raw} \in [\tau_i + o_i, \tau_i + o_{i-1})$, то $T_{raw}$ неоднозначна.

**Шаг 5 — Фиксация целостности.** Вычисляется временно́й хэш $H_{temp}$ в соответствии с приведённым выше определением, связывая разрешение с неизменяемым набором правил.

**Шаг 6 — Построение происхождения.** Инстанцируется объект `ResolvedTemporalArtifact`, заполняемый значениями $T_{UTC}$, $z$, статусом DST $\beta$, применённым смещением $o_{applied}$, флагом устранения неоднозначности $\delta$ (при необходимости), хэшем целостности $H_{temp}$ и записью происхождения, ссылающейся на $u_{ev}$ и активный набор патчей.

**Шаг 7 — Передача в аудит.** Артефакт передаётся в `vigia/audit/logger.py` для хранения с режимом только-дозапись (WORM) и в `vigia/core/chain_of_custody.py` для синхронизации метки времени цепочки хранения.

### 4. Спецификации входных и выходных данных

**Входные данные:**
- `raw_timestamp` (`str` или `int`): Наблюдаемая метка времени. Строки должны соответствовать расширенному формату ISO 8601:2004; целые числа представляют Unix-epoch в секундах.
- `geopolitical_hint` (`str` | `dict`): Код ISO 3166-1 alpha-2, псевдоним зоны IANA или объект GeoJSON Feature, описывающий полигональную юрисдикцию.
- `evidence_uuid` (`UUIDv4`): Уникальный идентификатор, связывающий временной запрос с родительским объектом доказательства в `vigia/io/evidence_ingest.py`.
- `rule_version` (`str`, по умолчанию `"2024a"`): Идентификатор выпуска базы данных часовых поясов IANA.
- `disambiguation_policy` (`enum`, по умолчанию `"EARLIER"`): Политика разрешения складок; допустимые значения: `"EARLIER"`, `"LATER"` и `"STRICT_NULL"`.

**Выходные данные:**
- `utc_timestamp` (`str`): Представление разрешённого мгновения в UTC по ISO 8601.
- `canonical_zone` (`str`): Дефинитивный идентификатор зоны IANA $z$.
- `dst_status` (`bool`): `True`, если разрешённый момент попадает на период действия летнего времени.
- `transition_offset_seconds` (`int`): Применённое смещение $o_{applied} \in \mathcal{O}$.
- `integrity_hash` (`str`): Шестнадцатеричный дайджест $H_{temp}$.
- `provenance_chain` (`dict`): Структурированные метаданные, содержащие `evidence_uuid`, `rule_version`, `patch_set` и `resolution_timestamp`.
- `exception_state` (`null` | `dict`): Null при успехе либо объект с полями `code` (`GAP`, `UNMAPPED_ENTITY`, `RULE_LOAD_FAILURE`) и `context` при сбое.

### 5. Детерминированные гарантии и сохранение цепочки хранения

Модуль обеспечивает строгие детерминированные гарантии, необходимые для судебной допустимости. Формально движок разрешения является чистой функцией от своих явных входных данных:
$$\forall \text{среда}_1, \text{среда}_2, \quad \text{Resolve}_{\text{среда}_1}(T_{raw}, z, v_{db}, \mathcal{M}) = \text{Resolve}_{\text{среда}_2}(T_{raw}, z, v_{db}, \mathcal{M})$$

Эта независимость от среды выполнения — включая конфигурацию часового пояса хостовой операционной системы, переменные среды `TZ` и дрейф системных часов — удовлетворяет требованию воспроизводимости стандарта Daubert. Движок демонстрирует идемпотентность: повторный вызов с идентичными входными данными порождает побитово идентичные выходные данные, включая идентичные хэши целостности $H_{temp}$.

Максимальная теоретическая погрешность $\epsilon$ процесса разрешения ограничена нулём для всех отображённых геополитических сущностей при условии, что входная метка времени и сущность сами по себе точны. Предшествующие эвристические методологии демонстрировали $\epsilon_{эвристика} \leq 2\,419\,200$ секунд (двадцать восемь суток) в периоды аномальных переходов; настоящий модуль устраняет указанную неопределённость посредством точного сопоставления с правилами.

Действительность цепочки хранения сохраняется за счёт криптографической привязки. Каждый разрешённый артефакт включает $H_{temp}$, удостоверяющий, что значение UTC получено из конкретного версионированного набора правил, а не из зависящих от платформы библиотечных вызовов. При интеграции с `vigia/core/chain_of_custody.py` указанные хэши образуют неизменяемый реестр временны́х преобразований, позволяющий независимому эксперту воспроизвести идентичный UTC-инстант из исходного доказательства и опубликованных правил IANA.

### 6. Интеграция с экосистемой VIGÍA

Модуль занимает центральное положение в конвейере временно́го анализа VIGÍA. Он получает предварительно обработанные метки времени от `vigia/io/evidence_ingest.py`, нормализующего гетерогенные форматы журналов. После разрешения артефакты потребляются `vigia/analytics/correlation_engine.py` для корреляции событий и `vigia/core/temporal_anchor.py` для установления монотонных хронологий.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## 中文

**模块标识：** `vigia/core/geopolitical_v2.py`
**引擎版本：** 地缘政治意图引擎 v3.0-P0-003
**框架：** VIGÍA 取证分析平台

### 1. 模块目的与取证背景

模块 `vigia/core/geopolitical_v2.py` 构成 VIGÍA 取证框架的确定性时间解析基底。其主要功能是通过严格应用精确 IANA 时区数据库规则，消除从数字证据中提取的本地时间戳转换为规范 UTC 表示时的认识论不确定性。在先前的启发式实现中，季节性时钟转换、废弃的区域标识符和模糊的地缘政治边界在异常转换期间引入了长达二十八天的时间位移，从而使不在场证明验证、事件关联和证据保管链年表失效。地缘政治意图引擎 v3.0-P0-003 通过强制执行地缘政治实体与规范区域标识符之间基于规则的非随机映射来纠正这些缺陷，确保每次时间戳解析在不同计算环境和取证检查中都具有数学可重现性。

### 2. 数学基础

设 $\mathcal{T}$ 表示系统内可表示的所有有效时刻的时间域。从证据中提取的原始时间戳定义为 $T_{raw} \in \mathcal{T}$，通常编码为 ISO 8601 字符串或时区注释不足的 Unix 纪元整数。

引擎实现规范化函数：
$$f_{geo}: \mathcal{E} \rightarrow \mathcal{Z}_{IANA}$$

核心时间解析形式化为映射：
$$\text{Resolve}: \mathcal{T} \times \mathcal{Z}_{IANA} \rightarrow \mathcal{T}_{UTC} \times \mathcal{B} \times \mathcal{O}$$

其中 $\mathcal{T}_{UTC}$ 是 UTC 时域，$\mathcal{B} = \{0,1\}$ 是指示 $T_{raw}$ 是否落入时间折叠（模糊秋季过渡）或时间间隙（无效春季过渡）的布尔指示符，$\mathcal{O} \subset \mathbb{Z}$ 是相对于 UTC 的应用偏移量（以整数秒表示）。

时间完整性通过对输入和规则集计算的密码学校验和进行保护：
$$H_{temp} = \mathcal{H}(T_{raw} \parallel z \parallel \text{VERSION}(R_z) \parallel \text{PATCH\_SET})$$

### 3. 关键概念

| 概念 | 定义 | 取证作用 |
|---|---|---|
| **IANA 时区数据库** | Internet 号码分配机构维护的权威时区标识符集合 | 规范时区解析的事实标准 |
| **时间折叠（Fold）** | 秋季回拨时同一本地时间出现两次的模糊区间 | 检测并标记具有两个候选 UTC 值的模糊时间戳 |
| **时间间隙（Gap）** | 春季拨快时不存在的本地时间区间 | 返回空值并附带错误代码以阻止无效时间戳 |
| **完整性哈希 $H_{temp}$** | 将解析结果绑定到特定 IANA 规则版本的 SHA-256 摘要 | 防篡改证明；使每次时间转换可审计 |
| **确定性整数运算** | 以整数秒执行的精确 UTC 偏移计算 | 消除舍入误差；跨平台保证逐位可重现 |
| **补丁集（Patch Set）** | 解决边缘案例的规则扩展（C3、W7、W8、P2-B、P0-003） | 维护历史准确性；覆盖废弃区域别名和争议领土 |

### 4. 确定性保证与证据保管链

模块提供严格的确定性保证，对取证可采性至关重要。形式上，解析引擎是其显式输入的纯函数：

$$\forall \text{env}_1, \text{env}_2, \quad \text{Resolve}_{\text{env}_1}(T_{raw}, z, v_{db}, \mathcal{M}) = \text{Resolve}_{\text{env}_2}(T_{raw}, z, v_{db}, \mathcal{M})$$

最大理论误差 $\epsilon$ 对所有已映射地缘政治实体的解析过程界定为零，前提是输入时间戳和实体本身准确。先前的启发式方法在异常过渡期间表现出 $\epsilon_{heuristic} \leq 2\,419\,200$ 秒（28 天）的误差；本模块通过精确规则匹配消除了这种不确定性。

### 5. 标准合规

- **道伯特标准（FRE 702）：** 引擎对已映射实体的已知错误率为零；其方法通过公开 IANA 规则可进行同行审查；输出可测试且可证伪。
- **ISO 8601:2004 和 ISO 8601-1:2019：** 所有时间字符串符合数据元素和交换格式国际标准。
- **RFC 8536：** TZif 二进制数据的内部解析符合时区信息标准格式。
- **GB/T 29360-2012**（电子数据取证检查）：支持在中国监管框架内进行客观、可重现电子数据检查程序的要求。

### 【科学说明】

> **【科学说明】**
> 皮尔斯（Peirce）、艾柯（Eco）和格赖斯（Grice）的框架在该模块中作为精确传感器协议运作。皮尔斯的初性是原始时间戳标记 $T_{raw}$——尚无时区上下文的纯现象；二性是差异比较：$T_{raw}$ 是否落在折叠或间隙区间内？三性是规律：IANA 规则集提供将本地时间映射到 UTC 的确定性解释项。艾柯的百科全书是 IANA 时区数据库本身——编码历史时钟实践的共享文化知识体。格赖斯的相关性准则通过拒绝不在已映射地缘政治实体范围内的时间戳来执行：只有有意义的时间输入才能进入证据链。所有计算使用精确整数运算（以整数秒为单位的偏移量），确保道伯特标准下的法庭可重现性。

### 词汇表

1. **时间折叠（Temporal Fold）** — 秋季时钟回拨时本地时间出现两次的模糊区间；引擎保留两个候选 UTC 值并附加消歧标志。
2. **时间间隙（Temporal Gap）** — 春季时钟拨快时不存在的本地时间区间；引擎返回错误代码而非无效时间戳。
3. **IANA 时区数据库** — 时区标识符和历史时区转换规则的权威来源。
4. **规范区域标识符** — IANA 分配的标准时区名称（如 "Asia/Shanghai"），消除历史别名歧义。
5. **完整性哈希 $H_{temp}$** — 将 UTC 解析绑定到特定 IANA 规则版本的 SHA-256 摘要，使操作可审计。
6. **UTC（协调世界时）** — 用于同步时间戳的全球参考时间标准，消除时区歧义。
7. **地缘政治实体** — 具有历史可观察时钟实践的主权领土、行政区划或争议区域。
8. **补丁集** — 解决边缘案例的规则扩展（C3 处理南极研究站区域；W7/W8 处理历史过渡；P0-003 提供主要领土映射）。
9. **确定性整数运算** — 以精确整数秒执行的 UTC 偏移计算，跨架构保证可重现。
10. **道伯特标准（Daubert Standard）** — 要求取证方法可测试且具有已知错误率的美国联邦法律标准；该模块通过零误差满足此标准。

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---