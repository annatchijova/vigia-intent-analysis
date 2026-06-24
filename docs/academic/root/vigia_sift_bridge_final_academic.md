## ENGLISH

**Module Designation:** `vigia/vigia_sift_bridge_final.py`  
**System:** VIGÍA Intentionality Analysis Framework  
**Author:** Anna Tchijova  
**License:** Apache 2.0  

### What Is This Module?

The module `vigia/vigia_sift_bridge_final.py` constitutes the **Intentionality Analysis Bridge for the SIFT Workstation**. It is not a conventional evidence-parser; rather, it functions as a deterministic control membrane that mediates between raw digital-forensic output from a SANS Investigative Forensic Toolkit (SIFT) environment and the higher-order cognitive-inference layers of the VIGÍA architecture. Where classical forensic tools answer the question *“What happened?”*—for example, which file was deleted, when a registry key was modified, or where a process injected code—this module reframes the evidentiary stream to ask *“Why did the actor choose this particular sequence of actions?”* In other words, the module operationalizes the transition from **event reconstruction** to **intentionality attribution**.

Scientists without programming experience may conceptualize this module as a rigid, mathematically bounded filtering station. Imagine a high-throughput sensor array that examines every piece of evidence arriving from a crime-scene laboratory. Before any piece is allowed into the analytical chamber where psychologists and semioticians work, it must pass through a gate that checks physical dimensions, total mass, and chemical composition. The bridge performs an analogous function for digital artifacts: it verifies that every text fragment, file preview, and pattern string falls within strictly defined integer limits. If an artifact exceeds any limit, the module does not silently truncate it; instead, it emits a specialized signal—`_IntegrityViolation`—that routes the offending item to an isolated quarantine zone (`_PURGATORY_DIR`) for later inspection.

### Theoretical Foundations

The module rests on a four-pillar epistemological foundation: **Peirce**, **Carnegie**, **Grice**, and **Eco**.

1. **Charles Sanders Peirce (Semiotics).** Peirce’s triadic theory of the sign—comprising the *representamen* (the form the sign takes), the *object* (that which the sign refers to), and the *interpretant* (the sense made of the sign)—provides the ontological scaffold for the bridge. Every digital artifact ingested from SIFT is treated not as raw data but as a *sign* standing in relation to an intentional state. The module classifies artifacts according to their semiotic modality (icon, index, or symbol) before they enter the inference pipeline.

2. **The Carnegie Tradition (Structured Knowledge Taxonomy).** Drawing from the Carnegie institutional model of organized, accessible knowledge classification, the module imposes a strict taxonomic order on evidence objects. Just as Carnegie libraries standardized cataloguing to make knowledge retrievable, this module standardizes evidentiary boundaries so that downstream classifiers operate on a predictable, finite universe of discourse.

3. **H.P. Grice (Pragmatics and Implicature).** Grice’s Cooperative Principle and the associated maxims of quantity, quality, relation, and manner are repurposed here as forensic heuristics. A system log that is unexpectedly terse, irrelevant, or ambiguous is read as generating a *conversational implicature*: the actor may be deliberately obfuscating intent. The bridge flags such pragmatic anomalies for the VIGÍA implicature layer.

4. **Umberto Eco (Codes and Interpretative Labyrinths).** Eco’s theory of encodification warns that any single sign can trigger multiple, equally valid interpretative paths. The bridge acknowledges this labyrinthine complexity but contains it through deterministic constraint. By fixing upper bounds on every input dimension, the module ensures that the combinatorial explosion of interpretations remains computationally tractable and scientifically reproducible.

### Mathematical Foundations

Let the constraint vector $\mathbf{c} \in \mathbb{N}^5$ encode the module’s hard boundaries:

| Symbol | Constant | Semiotic Meaning |
|--------|----------|------------------|
| $c_1$ | `MAX_TEXT_LENGTH` | Maximum permissible length of any single text artifact |
| $c_2$ | `MAX_TEXTS_IN_LIST` | Maximum cardinality of the artifact list |
| $c_3$ | `MAX_TOTAL_BYTES` | Aggregate byte budget for the entire ingestion window |
| $c_4$ | `MAX_PATTERN_LENGTH` | Upper bound on regex or pattern descriptors |
| $c_5$ | `MAX_FILE_PREVIEW` | Largest allowable preview window for file headers |

Define the input evidence stream as a finite sequence $E = (e_1, e_2, \dots, e_n)$, where each $e_i \in \Sigma^*$ over a finite alphabet $\Sigma$ of allowed code points defined by `_ALLOWED_PATTERN`. The feasibility predicate $\Phi(E)$ is a conjunction of exact integer inequalities:

$$
\Phi(E) \; \equiv \; \bigwedge_{i=1}^{n} \Big( |e_i|_{\text{char}} \leq c_1 \Big) \; \land \; \Big( n \leq c_2 \Big) \; \land \; \Big( \sum_{i=1}^{n} |e_i|_{\text{byte}} \leq c_3 \Big) \; \land \; \Big( |\text{pat}(e_i)| \leq c_4 \Big) \; \land \; \Big( |\text{preview}(e_i)| \leq c_5 \Big).
$$

If $\neg \Phi(E)$ evaluates to true, the module instantiates the exception class `_IntegrityViolation`. All arithmetic evaluating $\Phi$ is performed with deterministic integer operations; no floating-point representations, probabilistic thresholds, or statistical approximations are employed.

### Algorithm Description

Although the module exposes no public functions, its internal control flow follows a five-stage deterministic protocol:

1. **Contextualization.** The module resolves environment references: `_EVIDENCE_ENV` (operational mode), `_HONEY_TOKEN_DIR` (decoy artifact repository), `_PURGATORY_DIR` (isolation zone for violations), and `_SYSTEM_PROMPT_PATH_DEFAULT` (baseline analytic template). These four parameters establish the topological frame within which validation occurs.

2. **Lexical Verification.** Each candidate artifact identifier is matched against `_ALLOWED_PATTERN` using exact character-codepoint comparison (integer equality on Unicode scalar values). This step prevents injection of malformed or adversarially constructed paths.

3. **Dimensional Bounding.** The module computes $|e_i|_{\text{char}}$, $|e_i|_{\text{byte}}$, and derived pattern lengths. These quantities are compared against $\mathbf{c}$ using integer subtraction and sign-bit evaluation. Because the operations are integer-only, they are associative, commutative, and exhibit zero rounding error.

4. **Exception Routing.** When a boundary violation is detected, the module raises `_IntegrityViolation`. As a specialized subclass of `ValueError`, this exception is distinguishable from generic value errors elsewhere in the VIGÍA ecosystem. The distinction enables automated routing: integrity violations are shunted to `vigia_purgatory_handler.py`, whereas generic errors trigger broader system alarms.

5. **Bridge Emission.** Artifacts satisfying $\Phi(E)$ are packaged into a deterministic bridge container $\mathcal{B}$ and forwarded to downstream modules, notably `vigia_intentionality_graph.py` and `vigia_semiotic_encoder.py`.

### Input and Output Specifications

**Inputs:**
- **Primary:** A finite ordered list of digital evidence artifacts $E$, where each element is drawn from the alphabet permitted by `_ALLOWED_PATTERN`.
- **Environmental:** A tuple $\eta = (\eta_{\text{env}}, \eta_{\text{honey}}, \eta_{\text{purgatory}}, \eta_{\text{prompt}})$ mapping to `_EVIDENCE_ENV`, `_HONEY_TOKEN_DIR`, `_PURGATORY_DIR`, and `_SYSTEM_PROMPT_PATH_DEFAULT`.
- **Auxiliary:** Honey-token references used for counter-deception validation.

**Outputs:**
- **Success:** A validated bridge structure $\mathcal{B}$ containing bounded artifacts and routing metadata.
- **Failure:** An exception token $\xi$ of type `_IntegrityViolation`, carrying integer diagnostic codes indicating which conjunct of $\Phi(E)$ was violated.

The time complexity of the validation pass is $O(n)$ linear in the number of artifacts; auxiliary space complexity is $O(1)$ because the bounds vector $\mathbf{c}$ is constant-sized.

### Deterministic Guarantees

The module provides the following formal guarantees:

- **Integer-Only Arithmetic:** All comparisons and aggregations use exact integer mathematics. There are no floating-point operations, no logarithmic transforms, and no probabilistic sampling. Consequently, the result is immune to IEEE-754 rounding anomalies and hardware-dependent floating-point pathologies.
- **Idempotence:** Under identical environmental tuples $\eta$, repeated application to the same evidence stream yields identical outputs: $f(E, \eta) = f(f(E, \eta))$.
- **Reproducibility:** The deterministic pipeline satisfies the *Daubert* standard’s requirement for known and non-mysterious error rates. An independent examiner can replicate the exact boundary decisions on any compatible platform.
- **Complexity Attack Resistance:** By enforcing $c_2$ and $c_3$, the module bounds worst-case memory and processing consumption, mitigating Algorithmic Complexity Attacks (ACAs) that might otherwise exploit unbounded ingestion windows.
- **Auditability:** Every rejection produces a discrete, classifiable exception, satisfying traceability requirements under MLPS 2.0 and GB/T forensic audit standards.

> 【Scientific Note】
> The invocation of Peirce, Eco, and Grice is not an appeal to mysticism or literary criticism. In the VIGÍA framework, these thinkers function as **formal sensor models**. Peirce provides the lens that detects *what kind of sign* a digital trace represents; Grice supplies the filter that detects *pragmatic inconsistencies* suggestive of deliberate intent; Eco contributes the codebook that constrains how interpretations may proliferate without descending into arbitrary speculation. A scientist may regard them exactly as one regards the mathematical model inside a spectrometer: not as metaphysical doctrines, but as calibrated theoretical instruments that map observable inputs to structured outputs.

### Glossary

| Term | Definition |
|------|------------|
| **SIFT Workstation** | SANS Investigative Forensic Toolkit; a Linux-based environment for disk and memory forensics. |
| **Intentionality** | The directedness of an actor’s will toward an object or outcome, inferred here from digital traces rather than from direct testimony. |
| **`_IntegrityViolation`** | A specialized exception class denoting a read-integrity or boundary violation, distinguishable from generic value errors to enable precise routing. |
| **Honey Token** | A deliberately placed decoy artifact designed to detect unauthorized access or tampering. |
| **Purgatory Directory** | A quarantine filesystem zone where rejected or suspect artifacts are isolated pending human review. |
| **Deterministic Integer Arithmetic** | Calculation using whole numbers only, with no rounding, approximation, or platform-dependent floating-point behavior. |
| **Feasibility Predicate $\Phi(E)$** | The logical conjunction of integer inequalities that an evidence stream must satisfy to be accepted. |

### Related VIGÍA Modules

- **`vigia_intentionality_graph.py`**: Constructs directed acyclic graphs representing inferred chains of actor purpose from validated bridge output.
- **`vigia_semiotic_encoder.py`**: Maps file-system events into Peircean sign-classes (icon, index, symbol).
- **`vigia_grice_pragmatic_filter.py`**: Applies Gricean maxims to system logs and network captures to detect implicatures of deception.
- **`vigia_evidence_ingest.py`**: Performs raw ingestion and hashing prior to boundary validation.
- **`vigia_purgatory_handler.py`**: Receives `_IntegrityViolation` instances and manages forensic chain-of-custody for quarantined objects.

### Standards Compliance

- **Daubert Standard (United States Federal Evidence):** The deterministic, testable, and peer-reviewable nature of the boundary logic supports admissibility under Daubert criteria for scientific evidence.
- **GB/T 29360-2012 & GB/T 31500-2015:** Chinese national standards for electronic data forensic inspection; the module’s audit trails and integer-exact validation align with evidentiary integrity requirements.
- **MLPS 2.0 (Multi-Level Protection Scheme 2.0):** The module’s isolation of suspicious artifacts, deterministic processing, and explicit exception taxonomy satisfy Level-3 audit and access-control stipulations.

## ESPAÑOL

**Designación del módulo:** `vigia/vigia_sift_bridge_final.py`  
**Sistema:** VIGÍA — Marco de Análisis de Intencionalidad  
**Autora:** Anna Tchijova  
**Licencia:** Apache 2.0  

### ¿Qué es este módulo?

El módulo `vigia/vigia_sift_bridge_final.py` constituye el **Puente de Análisis de Intencionalidad para la SIFT Workstation**. No se trata de un analizador de evidencia convencional, sino de una **membrana de control determinística** que media entre los datos brutos provenientes de un entorno SANS Investigative Forensic Toolkit (SIFT) y las capas superiores de inferencia cognitiva de la arquitectura VIGÍA. Cuando vos utilizás herramientas forenses clásicas, la pregunta central es *“¿Qué ocurrió?”*: qué archivo se eliminó, cuándo se modificó una clave de registro o dónde inyectó código un proceso. Este módulo, en cambio, reformula el flujo evidenciero para preguntar *“¿Por qué el actor eligió esta secuencia particular de acciones?”*. Es decir, el módulo operacionaliza la transición entre **reconstrucción de eventos** y **atribución de intencionalidad**.

Si vos no tenés experiencia en programación, podés imaginar este componente como una **estación de filtrado rígidamente delimitada por matemáticas enteras**. Pensá en un conjunto de sensores de alto rendimiento que examinan cada pieza de evidencia que llega desde la escena del incidente. Antes de que cualquier elemento ingrese a la cámara analítica donde operan psicólogos y semióticos, debe atravesar una verja que controla sus dimensiones físicas, su masa total y su composición. El puente cumple una función análoga para los artefactos digitales: verifica que cada fragmento de texto, cada previsualización de archivo y cada patrón de búsqueda se encuentren dentro de límites enteros estrictamente definidos. Si un artefacto excede alguno de esos límites, el módulo no lo trunca en silencio; por el contrario, emite una señal especializada —`_IntegrityViolation`— que deriva el elemento infractor hacia una zona de cuarentena aislada (`_PURGATORY_DIR`) para su posterior análisis.

### Fundamentos teóricos

El módulo se apoya en cuatro pilares epistemológicos: **Peirce**, **Carnegie**, **Grice** y **Eco**.

1. **Charles Sanders Peirce (Semiótica).** La teoría tríádica del signo de Peirce —compuesta por el *representamen* (la forma que adopta el signo), el *objeto* (aquello a lo que el signo alude) y el *interpretante* (el sentido que se construye)— proporciona el andamiaje ontológico del puente. Cada artefacto digital que se ingiere desde SIFT se trata no como dato bruto, sino como un *signo* que se vincula con un estado intencional. El módulo clasifica los artefactos según su modalidad semiótica (ícono, índice o símbolo) antes de que ingresen al pipeline de inferencia.

2. **La tradición Carnegie (Taxonomía del conocimiento estructurado).** Inspirado en el modelo institucional Carnegie de organización y accesibilidad del saber, el módulo impone un orden taxonómico estricto sobre los objetos de evidencia. Así como las bibliotecas Carnegie estandarizaron su catalogación para hacer retornable el conocimiento, este módulo estandariza los límites evidenciarios de modo que los clasificadores posteriores operen sobre un universo de discurso finito y predecible.

3. **H.P. Grice (Pragmática e implicatura).** El Principio Cooperativo de Grice y sus máximas de cantidad, calidad, relación y modo se reutilizan aquí como heurísticas forenses. Un registro de sistema que resulta inesperadamente escueto, irrelevante o ambiguo se lee como generador de una *implicatura conversacional*: el actor puede estar obfuscando deliberadamente su intención. El puente marca tales anomalías pragmáticas para la capa de implicaturas de VIGÍA.

4. **Umberto Eco (Códigos y laberintos interpretativos).** La teoría de la codificación de Eco advierte que un mismo signo puede desencadenar múltiples sendas interpretativas igualmente válidas. El puente reconoce esta complejidad laberíntica, pero la contiene mediante restricciones determinísticas. Al fijar cotas superiores en cada dimensión de entrada, el módulo garantiza que la explosión combinatoria de interpretaciones permanezca computacionalmente tratable y científicamente reproducible.

### Fundamentos matemáticos

Sea el vector de restricciones $\mathbf{c} \in \mathbb{N}^5$ que codifica los límites rígidos del módulo:

| Símbolo | Constante | Significado semiótico |
|---------|-----------|----------------------|
| $c_1$ | `MAX_TEXT_LENGTH` | Longitud máxima permisible de un artefacto textual individual |
| $c_2$ | `MAX_TEXTS_IN_LIST` | Cardinalidad máxima de la lista de artefactos |
| $c_3$ | `MAX_TOTAL_BYTES` | Presupuesto agregado en bytes para toda la ventana de ingestión |
| $c_4$ | `MAX_PATTERN_LENGTH` | Cota superior de descriptores de patrón o expresiones regulares |
| $c_5$ | `MAX_FILE_PREVIEW` | Ventana de previsualización más grande permitida para cabeceras de archivo |

Definimos el flujo de evidencia de entrada como una secuencia finita $E = (e_1, e_2, \dots, e_n)$, donde cada $e_i \in \Sigma^*$ sobre un alfabeto finito $\Sigma$ de puntos de código permitidos definidos por `_ALLOWED_PATTERN`. El predicado de factibilidad $\Phi(E)$ es una conjunción de desigualdades enteras exactas:

$$
\Phi(E) \; \equiv \; \bigwedge_{i=1}^{n} \Big( |e_i|_{\text{car}} \leq c_1 \Big) \; \land \; \Big( n \leq c_2 \Big) \; \land \; \Big( \sum_{i=1}^{n} |e_i|_{\text{byte}} \leq c_3 \Big) \; \land \; \Big( |\text{pat}(e_i)| \leq c_4 \Big) \; \land \; \Big( |\text{prev}(e_i)| \leq c_5 \Big).
$$

Si $\neg \Phi(E)$ resulta verdadero, el módulo instancia la clase de excepción `_IntegrityViolation`. Toda la aritmética que evalúa $\Phi$ se ejecuta con operaciones enteras determinísticas; no se emplean representaciones de punto flotante, umbrales probabilísticos ni aproximaciones estadísticas.

### Descripción del algoritmo

Aunque el módulo no expone funciones públicas, su flujo de control interno obedece a un protocolo determinístico de cinco etapas:

1. **Contextualización.** El módulo resuelve las referencias ambientales: `_EVIDENCE_ENV` (modo operacional), `_HONEY_TOKEN_DIR` (repositorio de artefactos señuelo), `_PURGATORY_DIR` (zona de aislamiento para violaciones) y `_SYSTEM_PROMPT_PATH_DEFAULT` (plantilla analítica basal). Estos cuatro parámetros establecen el marco topológico dentro del cual se realiza la validación.

2. **Verificación léxica.** Cada identificador candidato de artefacto se contrasta con `_ALLOWED_PATTERN` mediante comparación exacta de puntos de código de caracteres (igualdad entera sobre valores escalares Unicode). Este paso previene la inyección de rutas malformadas o construidas adversariamente.

3. **Acotación dimensional.** El módulo computa $|e_i|_{\text{car}}$, $|e_i|_{\text{byte}}$ y las longitudes derivadas de patrones. Estas cantidades se comparan contra $\mathbf{c}$ mediante resta entera y evaluación del bit de signo. Dado que las operaciones son exclusivamente enteras, resultan asociativas, conmutativas y exhiben **error de redondeo nulo**.

4. **Enrutamiento de excepciones.** Cuando se detecta una violación de límite, el módulo eleva `_IntegrityViolation`. Al tratarse de una subclase especializada de `ValueError`, esta excepción es distinguible de los errores de valor genéricos que ocurren en otros sectores del ecosistema VIGÍA. Dicha distinción posibilita el enrutamiento automatizado: las violaciones de integridad se desvían hacia `vigia_purgatory_handler.py`, mientras que los errores genéricos activan alarmas sistémicas más amplias.

5. **Emisión del puente.** Los artefactos que satisfacen $\Phi(E)$ se empaquetan en un contenedor determinístico del puente $\mathcal{B}$ y se reenvían a los módulos posteriores, en particular a `vigia_intentionality_graph.py` y `vigia_semiotic_encoder.py`.

### Especificaciones de entrada y salida

**Entradas:**
- **Primaria:** Una lista ordenada y finita de artefactos de evidencia digital $E$, donde cada elemento se extrae del alfabeto permitido por `_ALLOWED_PATTERN`.
- **Ambiental:** Una tupla $\eta = (\eta_{\text{env}}, \eta_{\text{honey}}, \eta_{\text{purgatory}}, \eta_{\text{prompt}})$ que se mapea a `_EVIDENCE_ENV`, `_HONEY_TOKEN_DIR`, `_PURGATORY_DIR` y `_SYSTEM_PROMPT_PATH_DEFAULT`.
- **Auxiliar:** Referencias a *honey tokens* utilizadas para la validación contra-decepción.

**Salidas:**
- **Éxito:** Una estructura de puente validada $\mathcal{B}$ que contiene artefactos acotados y metadatos de enrutamiento.
- **Fracaso:** Un token de excepción $\xi$ del tipo `_IntegrityViolation`, que porta códigos diagnósticos enteros indicando cuál conjunto de $\Phi(E)$ fue violado.

La complejidad temporal del paso de validación es $O(n)$, lineal en la cantidad de artefactos; la complejidad espacial auxiliar es $O(1)$ porque el vector de cotas $\mathbf{c}$ es de tamaño constante.

### Garantías determinísticas

El módulo proporciona las siguientes garantías formales:

- **Aritmética exclusivamente entera:** Todas las comparaciones y agregaciones utilizan matemáticas enteras exactas. No existen operaciones de punto flotante, transformaciones logarítmicas ni muestreo probabilístico. En consecuencia, el resultado es inmune a las anomalías de redondeo IEEE-754 y a las patologías dependientes del hardware.
- **Idempotencia:** Bajo tuplas ambientales $\eta$ idénticas, la aplicación repetida al mismo flujo de evidencia produce salidas idénticas: $f(E, \eta) = f(f(E, \eta))$.
- **Reproducibilidad:** El pipeline determinístico satisface el requisito del *estándar Daubert* de tasas de error conocidas y no misteriosas. Un examinador independiente puede replicar las decisiones de límite exactas en cualquier plataforma compatible.
- **Resistencia a ataques de complejidad:** Al hacer cumplir $c_2$ y $c_3$, el módulo acota el peor caso de consumo de memoria y procesamiento, mitigando los ataques de complejidad algorítmica (ACA) que de otro modo podrían explotar ventanas de ingestión ilimitadas.
- **Auditabilidad:** Cada rechazo produce una excepción discreta y clasificable, satisfaciendo los requisitos de trazabilidad bajo MLPS 2.0 y las normas forenses GB/T.

> 【Nota Científica】
> La invocación de Peirce, Eco y Grice no constituye un llamado al misticismo ni a la crítica literaria. Dentro del marco VIGÍA, estos pensadores funcionan como **modelos formales de sensor**. Peirce proporciona la lente que detecta *qué clase de signo* representa un rastro digital; Grice provee el filtro que detecta *inconsistencias pragmáticas* sugestivas de una intención deliberada; Eco aporta el libro de códigos que restringe cómo las interpretaciones pueden proliferar sin caer en la especulación arbitraria. Vos podés concebirlos exactamente como se concibe el modelo matemático interno de un espectrómetro: no como doctrinas metafísicas, sino como instrumentos teóricos calibrados que mapean entradas observables a salidas estructuradas.

### Glosario

| Término | Definición |
|---------|------------|
| **SIFT Workstation** | SANS Investigative Forensic Toolkit; entorno basado en Linux para forense de disco y memoria. |
| **Intencionalidad** | La direccionalidad de la voluntad de un actor hacia un objeto o resultado, inferida aquí a partir de rastros digitales en lugar de testimonio directo. |
| **`_IntegrityViolation`** | Clase de excepción especializada que denota una violación de integridad de lectura o de límite, distinguible de errores de valor genéricos para permitir un enrutamiento preciso. |
| **Honey Token** | Artefacto señuelo colocado deliberadamente para detectar accesos no autorizados o manipulaciones. |
| **Purgatory Directory** | Zona de cuarentena en el sistema de archivos donde se aíslan los artefactos rechazados o sospechosos a la espera de revisión humana. |
| **Aritmética entera determinística** | Cálculo que utiliza únicamente números enteros, sin redondeo, aproximación ni comportamiento dependiente de la plataforma en punto flotante. |
| **Predicado de factibilidad $\Phi(E)$** | Conjunción lógica de desigualdades enteras que un flujo de evidencia debe satisfacer para ser aceptado. |

### Módulos VIGÍA relacionados

- **`vigia_intentionality_graph.py`**: Construye grafos acíclicos dirigidos que representan cadenas inferidas de propósito del actor a partir de la salida validada del puente.
- **`vigia_semiotic_encoder.py`**: Mapea eventos del sistema de archivos a clases de signos peirceanos (ícono, índice, símbolo).
- **`vigia_grice_pragmatic_filter.py`**: Aplica las máximas griceanas a registros del sistema y capturas de red para detectar implicaturas de engaño.
- **`vigia_evidence_ingest.py`**: Realiza la ingestión cruda y el hasheo previo a la validación de límites.
- **`vigia_purgatory_handler.py`**: Recibe instancias de `_IntegrityViolation` y gestiona la cadena de custodia forense de los objetos cuarentenados.

### Cumplimiento normativo

- **Estándar Daubert (Evidencia Federal de los Estados Unidos):** La naturaleza determinística, comprobable y revisable por pares de la lógica de límites respalda su admisibilidad bajo los criterios Daubert para evidencia científica.
- **GB/T 29360-2012 y GB/T 31500-2015:** Normas nacionales chinas para inspección forense de datos electrónicos; las pistas de auditoría y la validación exacta en enteros del módulo se alinean con los requisitos de integridad evidenciera.
- **MLPS 2.0 (Multi-Level Protection Scheme 2.0):** El aislamiento de artefactos sospechosos, el procesamiento determinístico y la taxonomía explícita de excepciones satisfacen las estipulaciones de auditoría y control de acceso de Nivel 3.

## РУССКИЙ

**Наименование модуля:** `vigia/vigia_sift_bridge_final.py`  
**Система:** VIGÍA — Инфраструктура анализа интенциональности  
**Автор:** Anna Tchijova  
**Лицензия:** Apache 2.0  

### Что представляет собой данный модуль?

Модуль `vigia/vigia_sift_bridge_final.py` представляет собой **Мост анализа интенциональности для рабочей станции SIFT**. Это не традиционный парсер цифровых доказательств, а детерминированная контрольная мембрана, осуществляющая посредничество между сырым выходным потоком цифровой криминалистики, генерируемым средой SANS Investigative Forensic Toolkit (SIFT), и высокоуровневыми слоями когнитивной инференции архитектуры VIGÍA. Если классические криминалистические инструменты отвечают на вопрос *«Что произошло?»* — какой файл удалён, когда модифицирован ключ реестра, куда внедрён код процесса, — то данный модуль переформулирует поток доказательств таким образом, чтобы центральным стал вопрос *«Почему субъект выбрал именно эту последовательность действий?»*. Иными словами, модуль операционализирует переход от **реконструкции события** к **атрибуции интенциональности**.

Исследователям, не знакомым с программированием, целесообразно представлять данный модуль как жёстко математически ограниченную фильтрационную станцию. Вообразите высокопроизводительную решётку датчиков, исследующую каждый объект доказательственной базы, поступающий с места инцидента. Прежде чем какой-либо элемент будет допущен в аналитическую камеру, где трудятся специалисты по семиотике и когнитивистике, он проходит через ворота, проверяющие физические размеры, общую массу и химический состав. Мост выполняет аналогичную функцию в отношении цифровых артефактов: верифицирует, чтобы каждый текстовый фрагмент, каждый предпросмотр файла и каждый строковый паттерн укладывались в строго определённые целочисленные пределы. Если артефакт превышает хотя бы один лимит, модуль не осуществляет тихого усечения; напротив, генерируется специализированный сигнал — `_IntegrityViolation`, — который направляет проблемный объект в изолированную зону карантина (`_PURGATORY_DIR`) для последующего анализа.

### Теоретические основы

Модуль опирается на четыре эпистемологических столпа: **Пирс**, **Карнеги**, **Грайс** и **Эко**.

1. **Чарлс Сандерс Пирс (Семиотика).** Триадическая теория знака Пирса — включающая *репрезентамен* (форму знака), *объект* (то, на что знак указывает) и *интерпретант* (осмысление знака) — задаёт онтологический каркас моста. Каждый цифровой артефакт, поступающий из SIFT, рассматривается не как сырой массив данных, а как *знак*, находящийся в отношении к интенциональному состоянию субъекта. Модуль классифицирует артефакты по их семиотической модальности (икона, индекс, символ) ещё до их попадания в инференциальный конвейер.

2. **Традиция Карнеги (Структурированная таксономия знаний).** Опираясь на институциональную модель Карнеги организации и доступности знания, модуль накладывает строгий таксономический порядок на объекты доказательственной базы. Подобно тому как библиотеки Карнеги стандартизировали каталогизацию для обеспечения поиска, данный модуль стандартизирует границы доказательственных объектов, чтобы нисходящие классификаторы оперировали предсказуемой, конечной областью дискурса.

3. **Г. П. Грайс (Прагматика и импликатура).** Кооперативный принцип Грайса и связанные с ним максимы количества, качества, отношения и манеры перепрофилированы здесь в криминалистические эвристики. Системный журнал, который неожиданно лаконичен, иррелевантен или двусмысленен, интерпретируется как порождающий *конверсационную импликатуру*: субъект может преднамеренно маскировать свою интенцию. Мост маркирует подобные прагматические аномалии для слоя импликатур VIGÍA.

4. **Умберто Эко (Коды и интерпретативные лабиринты).** Теория кодификации Эко предупреждает, что один и тот же знак может запускать множество равноправных интерпретативных траекторий. Мост признаёт эту лабиринтную сложность, но сдерживает её детерминированными ограничениями. Фиксируя верхние границы каждого входного измерения, модуль гарантирует, что комбинаторный взрыв интерпретаций остаётся вычислительно управляемым и научно воспроизводимым.

### Математические основы

Пусть вектор ограничений $\mathbf{c} \in \mathbb{N}^5$ кодирует жёсткие границы модуля:

| Символ | Константа | Семиотическое значение |
|--------|-----------|------------------------|
| $c_1$ | `MAX_TEXT_LENGTH` | Максимально допустимая длина отдельного текстового артефакта |
| $c_2$ | `MAX_TEXTS_IN_LIST` | Максимальная мощность списка артефактов |
| $c_3$ | `MAX_TOTAL_BYTES` | Совокупный байтовый бюджет всего окна поглощения |
| $c_4$ | `MAX_PATTERN_LENGTH` | Верхняя граница длины паттернов и регулярных выражений |
| $c_5$ | `MAX_FILE_PREVIEW` | Наибольший допустимый объём окна предпросмотра заголовков файлов |

Определим входной поток доказательств как конечную последовательность $E = (e_1, e_2, \dots, e_n)$, где каждый $e_i \in \Sigma^*$ над конечным алфавитом $\Sigma$ разрешённых скалярных кодовых точек Unicode, задаваемых `_ALLOWED_PATTERN`. Предикат допустимости $\Phi(E)$ представляет собой конъюнкцию точных целочисленных неравенств:

$$
\Phi(E) \; \equiv \; \bigwedge_{i=1}^{n} \Big( |e_i|_{\text{симв}} \leq c_1 \Big) \; \land \; \Big( n \leq c_2 \Big) \; \land \; \Big( \sum_{i=1}^{n} |e_i|_{\text{байт}} \leq c_3 \Big) \; \land \; \Big( |\text{pat}(e_i)| \leq c_4 \Big) \; \land \; \Big( |\text{pre}(e_i)| \leq c_5 \Big).
$$

Если $\neg \Phi(E)$ истинно, модуль инстанциирует класс исключения `_IntegrityViolation`. Вся арифметика, вычисляющая $\Phi$, выполняется с применением детерминированных целочисленных операций; не используются числа с плавающей запятой, вероятностные пороги или статистические аппроксимации.

### Описание алгоритма

Несмотря на отсутствие публичных функций, внутренний поток управления модуля следует пятиэтапному детерминированному протоколу:

1. **Контекстуализация.** Модуль разрешает ссылки окружения: `_EVIDENCE_ENV` (операционный режим), `_HONEY_TOKEN_DIR` (хранилище артефактов-приманок), `_PURGATORY_DIR` (зона изоляции нарушений) и `_SYSTEM_PROMPT_PATH_DEFAULT` (базовый аналитический шаблон). Эти четыре параметра задают топологическую рамку, внутри которой осуществляется валидация.

2. **Лексическая верификация.** Каждый идентификатор кандидата сопоставляется с `_ALLOWED_PATTERN` посредством точного сравнения кодовых точек символов (целочисленное равенство скалярных значений Unicode). Данный шаг предотвращает инъекцию malformed или адверсарно сконструированных путей.

3. **Размерное ограничение.** Модуль вычисляет $|e_i|_{\text{симв}}$, $|e_i|_{\text{байт}}$ и производные длины паттернов. Эти величины сравниваются с $\mathbf{c}$ при помощи целочисленного вычитания и оценки знакового бита. Поскольку операции исключительно целочисленные, они ассоциативны, коммутативны и демонстрируют **нулевую ошибку округления**.

4. **Маршрутизация исключений.** При обнаружении нарушения границы модуль возбуждает `_IntegrityViolation`. Будучи специализированным подклассом `ValueError`, данное исключение отличимо от общих ошибок значений в экосистеме VIGÍA. Это различие обеспечивает автоматическую маршрутизацию: нарушения целостности перенаправляются в `vigia_purgatory_handler.py`, тогда как общие ошибки активируют более широкие системные тревоги.

5. **Эмиссия моста.** Артефакты, удовлетворяющие $\Phi(E)$, упаковываются в детерминированный мостовой контейнер $\mathcal{B}$ и передаются нисходящим модулям, в частности `vigia_intentionality_graph.py` и `vigia_semiotic_encoder.py`.

### Спецификации входных и выходных данных

**Входные данные:**
- **Первичные:** Конечный упорядоченный список цифровых артефактов $E$, каждый элемент которого извлечён из алфавита, разрешённого `_ALLOWED_PATTERN`.
- **Контекстные:** Кортеж $\eta = (\eta_{\text{env}}, \eta_{\text{honey}}, \eta_{\text{purgatory}}, \eta_{\text{prompt}})$, отображаемый на `_EVIDENCE_ENV`, `_HONEY_TOKEN_DIR`, `_PURGATORY_DIR` и `_SYSTEM_PROMPT_PATH_DEFAULT`.
- **Вспомогательные:** Ссылки на honey-токены, применяемые для контрдекептивной валидации.

**Выходные данные:**
- **Успех:** Валидированная мостовая структура $\mathcal{B}$, содержащая ограниченные артефакты и метаданные маршрутизации.
- **Отказ:** Токен исключения $\xi$ типа `_IntegrityViolation`, несущий целочисленные диагностические коды, указывающие, какая конъюнкта $\Phi(E)$ была нарушена.

Временная сложность прохода валидации составляет $O(n)$, линейную относительно числа артефактов; вспомогательная пространственная сложность — $O(1)$, поскольку вектор ограничений $\mathbf{c}$ имеет фиксированный размер.

### Детерминистические гарантии

Модуль обеспечивает следующие формальные гарантии:

- **Исключительно целочисленная арифметика:** Все сравнения и агрегации используют точную целочисленную математику. Отсутствуют операции с плавающей запятой, логарифмические преобразования и вероятностная выборка. Следовательно, результат иммунен к аномалиям округления IEEE-754 и аппаратно-зависимым патологиям чисел с плавающей запятой.
- **Идемпотентность:** При идентичных контекстных кортежах $\eta$ повторное применение к одному и тому же потоку доказательств даёт идентичные выходы: $f(E, \eta) = f(f(E, \eta))$.
- **Воспроизводимость:** Детерминированный конвейер удовлетворяет требованию стандарта *Daubert* об известных и немистических частотах ошибок. Независимый эксперт может воспроизвести точные граничные решения на любой совместимой платформе.
- **Устойчивость к атакам на сложность:** Благодаря принудительному соблюдению $c_2$ и $c_3$ модуль ограничивает худший случай потребления памяти и вычислительных ресурсов, смягчая атаки на алгоритмическую сложность (ACA), которые иначе могли бы эксплуатировать неограниченные окна поглощения.
- **Аудируемость:** Каждый отказ порождает дискретное классифицируемое исключение, удовлетворяя требованиям прослеживаемости в рамках MLPS 2.0 и криминалистических стандартов GB/T.

> 【НАУЧНОЕ ПОЯСНЕНИЕ】
> Ссылки на Пирса, Эко и Грайса не являются апелляцией к мистицизму или литературоведению. В рамках VIGÍA эти мыслители функционируют как **формальные модели датчиков**. Пирс предоставляет линзу, детектирующую, *какого рода знак* представляет собой цифровой след; Грайс поставляет фильтр, выявляющий *прагматические несоответствия*, наводящие на мысль о преднамеренной интенции; Эко вносит кодовую книгу, ограничивающую возможное размножение интерпретаций без скатывания в произвольную спекуляцию. Исследователь вправе рассматривать их в точности так же, как математическую модель внутри спектрометра: не как метафизические доктрины, а как калиброванные теоретические инструменты, отображающие наблюдаемые входы на структурированные выходы.

### Глоссарий

| Термин | Определение |
|--------|-------------|
| **SIFT Workstation** | SANS Investigative Forensic Toolkit; среда на базе Linux для криминалистического исследования дисков и памяти. |
| **Интенциональность** | Направленность воли субъекта на объект или результат, выводимая здесь из цифровых следов, а не из прямого свидетельства. |
| **`_IntegrityViolation`** | Специализированный класс исключений, обозначающий нарушение целостности чтения или границы; отличим от общих ошибок значений для обеспечения точной маршрутизации. |
| **Honey Token** | Артефакт-приманка, преднамеренно размещаемый для обнаружения несанкционированного доступа или подделки. |
| **Purgatory Directory** | Карантинная зона файловой системы, куда помещаются отвергнутые или подозрительные артефакты в ожидании человеческой экспертизы. |
| **Детерминистическая целочисленная арифметика** | Вычисление с использованием исключительно целых чисел без округления, аппроксимации или платформенно-зависимого поведения чисел с плавающей запятой. |
| **Предикат допустимости $\Phi(E)$** | Логическая конъюнкция целочисленных неравенств, которым должен удовлетворять поток доказательств для допуска к обработке. |

### Связанные модули VIGÍA

- **`vigia_intentionality_graph.py`**: Строит ориентированные ациклические графы, представляющие инферируемые цепочки целей субъекта, на основе валидированного выхода моста.
- **`vigia_semiotic_encoder.py`**: Отображает события файловой системы на классы пирсовских знаков (икона, индекс, символ).
- **`vigia_grice_pragmatic_filter.py`**: Применяет грайсовы максимы к системным журналам и сетевым дампам для детекции импликатур обмана.
- **`vigia_evidence_ingest.py`**: Осуществляет сырой приём и хеширование до валидации границ.
- **`vigia_purgatory_handler.py`**: Принимает экземпляры `_IntegrityViolation` и управляет цепью сохранности карантинных объектов.

### Соответствие стандартам

- **Стандарт Daubert (Федеральные правила доказывания США):** Детерминированный, поддающийся проверке и рецензированию характер граничной логики поддерживает допустимость под стандартом Daubert в качестве научного доказательства.
- **GB/T 29360-2012 и GB/T 31500-2015:** Национальные стандарты Китая по судебной экспертизе электронных данных; журналы аудита и точная целочисленная валидация модуля согласуются с требованиями целостности доказательств.
- **MLPS 2.0 (Multi-Level Protection Scheme 2.0):** Изоляция подозрительных артефактов, детерминированная обработка и явная таксономия исключений удовлетворяют требованиям аудита и контроля доступа Уровня 3.

## 中文

**模块标识：** `vigia/vigia_sift_bridge_final.py`  
**系统：** VIGÍA 意图性分析框架  
**作者：** Anna Tchijova  
**许可证：** Apache 2.0  

### 本模块是什么？

`vigia/vigia_sift_bridge_final.py` 模块是 **SIFT 工作站的意图性分析桥接器**。它并非传统的证据解析器，而是作为确定性控制膜，在 SANS Investigative Forensic Toolkit（SIFT）环境输出的原始数字取证数据与 VIGÍA 架构的高阶认知推理层之间进行中介。传统的取证工具回答的问题是 *“发生了什么？”*——例如哪个文件被删除、注册表键何时被修改、进程在何处注入代码；而本模块将证据流重新框架化，使其核心问题变为 *“行为主体为何选择这一特定行为序列？”* 换言之，该模块将 **事件重构** 到 **意图归因** 的操作化过渡予以实现。

对于不具备编程经验的科研人员，可将本模块理解为一道由整数数学严格界定的过滤关卡。设想一组高通量传感器阵列，对来自事件现场的每一件取证工件进行审查。在任何一件工件进入符号学家与认知分析师所在分析舱之前，都必须先通过一道检验其物理尺寸、总质量与化学组成的关卡。该桥接器对数字工件执行类似功能：它验证每一个文本片段、文件预览与模式字符串是否处于严格定义的整数界限之内。若某工件超出任一界限，模块不会执行静默截断；相反，它会发出一种专用信号——`_IntegrityViolation`——并将违规工件路由至隔离检疫区（`_PURGATORY_DIR`）以待后续审查。

### 理论基础

本模块依托四大认识论支柱：**皮尔士**、**卡内基**、**格