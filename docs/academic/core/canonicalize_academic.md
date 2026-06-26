## ENGLISH

`vigia/core/canonicalize.py` constitutes the sole authoritative implementation of the VIGÍA Canonical Schema v1, serving as the deterministic serialization gateway through which all evidentiary data structures must pass prior to cryptographic commitment. Within the VIGÍA forensic architecture, this module occupies a critical position in the chain of custody: it transforms semantically equivalent yet representationally divergent Python objects into a single, unambiguous byte sequence. By collapsing representational variance—whether arising from dictionary insertion order, integer encoding width, Unicode normalization form, or host platform endianness—the module ensures that the input to the SHA-256 hash function is bitwise identical across every subsystem, time of execution, and hardware architecture. Only independent verifier implementations, which are required to re-create the schema from first principles to avoid circular trust assumptions, are exempt from direct importation of this routine.

**Mathematical Foundations**

Let $\mathcal{D}$ denote the domain of admissible data structures accepted by Canonical Schema v1. This domain comprises finite compositions of the base types $\{\texttt{dict}, \texttt{list}, \texttt{tuple}, \texttt{str}, \texttt{int}, \texttt{float}, \texttt{bool}, \texttt{NoneType}, \texttt{bytes}\}$, subject to acyclicity constraints. The canonicalization function is defined as a total computable mapping:

$$\mathcal{C}_{v1} : \mathcal{D} \to \mathbb{B}^*$$

where $\mathbb{B}^* = \bigcup_{n \geq 0} \{0,1\}^{8n}$ represents the set of all finite-length byte strings. Let $\sim$ denote the relation of semantic equivalence over $\mathcal{D}$, such that $d_1 \sim d_2$ if and only if the two structures encode identical logical information under the schema's interpretation rules (e.g., two dictionaries containing identical key-value associations irrespective of insertion order). Canonical Schema v1 is designed to satisfy the invariant:

$$\forall d_1, d_2 \in \mathcal{D}, \quad d_1 \sim d_2 \iff \mathcal{C}_{v1}(d_1) = \mathcal{C}_{v1}(d_2)$$

This property establishes that $\mathcal{C}_{v1}$ is injective modulo semantic equivalence. Consequently, the composition of canonicalization with the SHA-256 hash function $H_{\text{SHA-256}} : \mathbb{B}^* \to \{0,1\}^{256}$ yields a digest $h$ that is a pure function of the evidentiary semantics:

$$h(d) = H_{\text{SHA-256}}(\mathcal{C}_{v1}(d))$$

Because $H_{\text{SHA-256}}$ is itself collision-resistant and $\mathcal{C}_{v1}$ is deterministic, the digest $h$ inherits a strict deterministic guarantee: any alteration in the semantic content of $d$, or any failure to reproduce $\mathcal{C}_{v1}(d)$ exactly, will produce a detectable change in $h$.

**Algorithm Description**

The algorithm implemented in `vigia/core/canonicalize.py` proceeds through four strict phases, each designed to eliminate a specific class of representational non-determinism.

*Phase I: Admissibility and Acyclicity Validation.* The input object $x \in \mathcal{D}$ is traversed to verify that every node belongs to the permitted type universe and that the object graph contains no cycles. If a cycle is detected or a non-admissible type (e.g., a custom Python class instance) is encountered, the routine raises a `CanonicalizationTypeError`, halting the forensic pipeline to prevent undefined serialization behavior.

*Phase II: Recursive Normalization.* The module performs a depth-first, left-to-right traversal of the object graph. During this traversal, each node is transformed according to type-specific rules:

- **Associative arrays (`dict`):** Keys are restricted to instances of `str`. The key set $K = \{k_1, k_2, \dots, k_m\}$ is sorted by strict lexicographic order of the UTF-8 byte encoding of each key. The resulting ordered sequence of pairs $(k_{(1)}, v_{(1)}), \dots, (k_{(m)}, v_{(m)})$ is then serialized recursively. This step explicitly nullifies any dependency on dictionary insertion order or hash randomization.
- **Unicode strings (`str`):** Every string is normalized according to Unicode Normalization Form C (NFC), as specified in ISO/IEC 10646 and Unicode Standard Annex #15. The normalized string is then encoded into UTF-8. This eliminates equivalence variance arising from composed versus decomposed character sequences.
- **Integers (`int`):** Arbitrary-precision integers are encoded using a minimal-length big-endian two's complement representation, prefixed by a type tag and length header. This representation is independent of the host machine's word size or signed-integer convention.
- **Floating-point numbers (`float`):** Values are represented as IEEE 754 binary64 (double-precision) big-endian byte sequences. Schema v1 enforces two additional constraints: negative zero ($-0.0$) is normalized to positive zero ($+0.0$), and non-finite values (`NaN`, `Inf`, `-Inf`) are rejected via `CanonicalizationValueError`. These restrictions are necessary because `NaN` lacks equality reflexivity in IEEE 754 and because sign-of-zero behavior varies across platforms.
- **Sequences (`list`, `tuple`):** Both types are encoded identically as length-prefixed sequences of their recursively canonicalized elements, ensuring that the forensic output does not distinguish between mutable and immutable sequence containers at the serialization layer.
- **Booleans and null:** Encoded as single-byte type-tagged constants.
- **Byte strings (`bytes`):** Passed through directly with a length prefix, as they are already raw binary artifacts.

*Phase III: Structured Serialization.* The normalized graph is flattened into a byte stream using a self-describing, type-tagged protocol. Each element is prefixed with a one-byte type tag, followed by a fixed-width big-endian length field (where applicable), followed by the payload bytes. The concatenation of these records produces the final canonical byte string $b = \mathcal{C}_{v1}(x)$.

**Input and Output Specifications**

- **Input:** A Python object $x$ drawn from the admissible domain $\mathcal{D}$.
- **Output:** An immutable `bytes` object $b \in \mathbb{B}^*$, representing the canonical serialization of $x$.
- **Time Complexity:** $O(n)$, where $n$ is the total number of atomic and compound nodes in the object graph.
- **Space Complexity:** $O(n)$ for the output byte string, plus $O(h)$ auxiliary stack space, where $h$ is the maximum depth of the object graph.
- **Exceptional Behavior:** 
  - `CanonicalizationTypeError`: Raised when $x$ contains a type outside the admissible universe or when a cyclic reference is detected.
  - `CanonicalizationValueError`: Raised upon encountering non-finite floating-point values or dictionary keys that are not strings.

**Deterministic Guarantees**

The module provides the following formal deterministic guarantees, which collectively establish the forensic reliability of the VIGÍA pipeline:

1. **Cross-Architectural Bitwise Reproducibility:** For any $x \in \mathcal{D}$, the output $\mathcal{C}_{v1}(x)$ is bitwise identical regardless of host CPU endianness (little-endian x86_64, big-endian ARM, bi-endian RISC-V), operating system, or Python interpreter patch version (within the supported 3.10+ series). This is achieved by mandating big-endian wire format and explicit type-length encodings.
2. **Temporal Independence:** The function $\mathcal{C}_{v1}$ is a pure function of its input. No timestamp, random salt, process identifier, or environmental variable (including `PYTHONHASHSEED`) influences the output.
3. **Semantic Idempotence:** Given two Python objects $x_1, x_2$ that are semantically equivalent under Schema v1 rules—for example, $\texttt{dict}(\texttt{a}=1, \texttt{b}=2)$ and $\texttt{dict}(\texttt{b}=2, \texttt{a}=1)$—the module guarantees $\mathcal{C}_{v1}(x_1) = \mathcal{C}_{v1}(x_2)$.
4. **Stability Under Admissible Mutation:** If a subsystem receives $b$ and later reparses it into a Python object $x'$, re-applying $\mathcal{C}_{v1}$ to $x'$ is guaranteed to produce $b$ provided the parser is schema-compliant. This round-trip invariant is essential for long-term archival verification in `vigia/storage/archive.py`.

**Relations to Other VIGÍA Modules**

`vigia/core/canonicalize.py` functions as a mandatory dependency for several downstream modules:

- **`vigia/core/ingest.py`:** The ingestion subsystem invokes $\mathcal{C}_{v1}$ immediately after evidentiary deserialization to ensure that all subsequent operations operate on stabilized byte representations.
- **`vigia/core/hash.py`:** Computes the cryptographic digest $h = H_{\text{SHA-256}}(b)$. This module never hashes raw objects directly; it exclusively consumes the output of the canonicalization routine.
- **`vigia/chain/merkle.py`:** Constructs Merkle trees over batches of evidentiary records. Each leaf node in the tree corresponds to a digest produced from a canonicalized object, thereby ensuring that the aggregate root hash reflects a deterministic ordering of semantically stable inputs.
- **`vigia/verify/independent.py`:** Independent verifiers are deliberately prohibited from importing `canonicalize.py`. Instead, they must implement an equivalent Schema v1 serializer from specification. This architectural separation prevents a single implementation bug from propagating undetected across the entire verification ecosystem.
- **`vigia/audit/logger.py`:** Forensic audit logs record the digest $h$ and, under high-assurance configurations, the byte-length $|b|$ of the canonical form, creating a non-repudiable trace of the exact input to the hash function.

**Standards Compliance**

The design of Canonical Schema v1 directly supports compliance with multiple national and international forensic and information-security standards:

- **Daubert Standard / FRE 702:** By enforcing a published, versioned protocol with a zero stochastic error rate over admissible inputs, the module satisfies the criteria of testability, known error rates, and general acceptance required for expert testimony in United States federal courts.
- **GB/T 29360-2012** (*Electronic Data Forensics*): The deterministic stabilization of hash inputs aligns with Chinese national standards for preserving the originality and integrity of electronic evidence throughout collection and analysis.
- **MLPS 2.0** (*Multi-Level Protection Scheme, Level 3 and Above*): The module's elimination of non-determinism in integrity verification supports the mandatory audit and data-protection requirements for classified information systems.
- **ISO/IEC 27037:2012** (*Guidelines for identification, collection, acquisition and preservation of digital evidence*): Canonicalization ensures that the "originality" principle is upheld in the digital domain by preventing format-level drift from being misinterpreted as evidentiary alteration.

**Conclusion**

`vigia/core/canonicalize.py` is not merely a serialization utility but the formal foundation of evidentiary integrity within VIGÍA. By mathematically guaranteeing that semantically identical data structures converge to a single, reproducible byte string prior to hashing, the module closes a critical vulnerability in the forensic chain of custody: the possibility that benign representational variance could be mistaken for evidence tampering or that hash non-reproducibility could undermine legal admissibility.

## ESPAÑOL

`vigia/core/canonicalize.py` constituye la única fuente autorizada de la función de canonicalización en el sistema VIGÍA, implementando el Esquema Canónico v1 como protocolo determinista de serialización obligatorio para toda estructura de datos probatoria antes de su compromiso criptográfico. En la arquitectura forense de VIGÍA, este módulo ocupa una posición crítica en la cadena de custodia: transforma objetos de Python semánticamente equivalentes pero representacionalmente divergentes en una secuencia de bytes única e inequívoca. Al eliminar la varianza representacional —ya sea originada en el orden de inserción de diccionarios, la anchura de codificación de enteros, la forma de normalización Unicode o el endianness de la plataforma anfitriona—, el módulo garantiza que la entrada a la función de hash SHA-256 sea idéntica bit a bit en todos los subsistemas, instantes de ejecución y arquitecturas de hardware. Únicamente las implementaciones de verificadores independientes, que deben reconstruir el esquema desde los primeros principios para evitar supuestos circulares de confianza, quedan exceptuadas de importar directamente esta rutina.

**Fundamentos Matemáticos**

Sea $\mathcal{D}$ el dominio de estructuras de datos admisibles aceptadas por el Esquema Canónico v1. Este dominio comprende composiciones finitas de los tipos base $\{\texttt{dict}, \texttt{list}, \texttt{tuple}, \texttt{str}, \texttt{int}, \texttt{float}, \texttt{bool}, \texttt{NoneType}, \texttt{bytes}\}$, sujetas a restricciones de aciclicidad. La función de canonicalización se define como una aplicación computable total:

$$\mathcal{C}_{v1} : \mathcal{D} \to \mathbb{B}^*$$

donde $\mathbb{B}^* = \bigcup_{n \geq 0} \{0,1\}^{8n}$ representa el conjunto de todas las cadenas de bytes de longitud finita. Sea $\sim$ la relación de equivalencia semántica sobre $\mathcal{D}$, tal que $d_1 \sim d_2$ si y solo si ambas estructuras codifican información lógica idéntica bajo las reglas de interpretación del esquema (por ejemplo, dos diccionarios que contienen asociaciones clave-valor idénticas independientemente del orden de inserción). El Esquema Canónico v1 satisface el invariante:

$$\forall d_1, d_2 \in \mathcal{D}, \quad d_1 \sim d_2 \iff \mathcal{C}_{v1}(d_1) = \mathcal{C}_{v1}(d_2)$$

Esta propiedad establece que $\mathcal{C}_{v1}$ es inyectiva módulo equivalencia semántica. En consecuencia, la composición de la canonicalización con la función de hash SHA-256 $H_{\text{SHA-256}} : \mathbb{B}^* \to \{0,1\}^{256}$ produce un digesto $h$ que es función pura de la semántica probatoria:

$$h(d) = H_{\text{SHA-256}}(\mathcal{C}_{v1}(d))$$

Dado que $H_{\text{SHA-256}}$ es resistente a colisiones y $\mathcal{C}_{v1}$ es determinista, el digesto $h$ hereda una garantía determinista estricta: cualquier alteración en el contenido semántico de $d$, o cualquier incapacidad para reproducir $\mathcal{C}_{v1}(d)$ exactamente, producirá un cambio detectable en $h$.

**Descripción del Algoritmo**

El algoritmo implementado en `vigia/core/canonicalize.py` se ejecuta en cuatro fases estrictas, cada una diseñada para eliminar una clase específica de no determinismo representacional.

*Fase I: Validación de Admisibilidad y Aciclicidad.* El objeto de entrada $x \in \mathcal{D}$ se recorre para verificar que cada nodo pertenezca al universo de tipos permitidos y que el grafo de objetos no contenga ciclos. Si se detecta un ciclo o un tipo no admisible (por ejemplo, una instancia de clase personalizada de Python), la rutina eleva una excepción `CanonicalizationTypeError`, deteniendo la cadena forense para prevenir comportamientos de serialización indefinidos.

*Fase II: Normalización Recursiva.* El módulo ejecuta un recorrido en profundidad primero, de izquierda a derecha, sobre el grafo de objetos. Durante este recorrido, cada nodo se transforma según reglas específicas de tipo:

- **Arreglos asociativos (`dict`):** Las claves se restringen a instancias de `str`. El conjunto de claves $K = \{k_1, k_2, \dots, k_m\}$ se ordena por orden lexicográfico estricto de la codificación UTF-8 de cada clave. La secuencia resultante de pares ordenados $(k_{(1)}, v_{(1)}), \dots, (k_{(m)}, v_{(m)})$ se serializa recursivamente. Este paso anula explícitamente cualquier dependencia del orden de inserción o de la aleatorización de hash.
- **Cadenas Unicode (`str`):** Toda cadena se normaliza según la Forma de Normalización Canónica de Composición C (NFC), conforme a la norma ISO/IEC 10646 y al Anexo UAX #15 del estándar Unicode. La cadena normalizada se codifica posteriormente en UTF-8. Esto elimina la varianza de equivalencia originada en secuencias de caracteres compuestos versus descompuestos.
- **Enteros (`int`):** Los enteros de precisión arbitraria se codifican mediante una representación big-endian en complemento a dos de longitud mínima, precedida por una etiqueta de tipo y un encabezado de longitud. Esta representación es independiente del tamaño de palabra de la máquina anfitriona o de la convención de enteros con signo.
- **Números de punto flotante (`float`):** Los valores se representan como secuencias de bytes big-endian IEEE 754 binary64 (doble precisión). El Esquema v1 impone dos restricciones adicionales: el cero negativo ($-0.0$) se normaliza a cero positivo ($+0.0$), y los valores no finitos (`NaN`, `Inf`, `-Inf`) se rechazan mediante `CanonicalizationValueError`. Estas restricciones son necesarias porque `NaN` carece de reflexividad de igualdad en IEEE 754 y el comportamiento del signo del cero varía entre plataformas.
- **Secuencias (`list`, `tuple`):** Ambos tipos se codifican idénticamente como secuencias prefijadas por longitud de sus elementos canonicalizados recursivamente, asegurando que la salida forense no distinga entre contenedores de secuencia mutables e inmutables en la capa de serialización.
- **Booleanos y nulo:** Se codifican como constantes de un solo byte etiquetadas por tipo.
- **Cadenas de bytes (`bytes`):** Se transmiten directamente con un prefijo de longitud, dado que ya constituyen artefactos binarios brutos.

*Fase III: Serialización Estructurada.* El grafo normalizado se aplana en un flujo de bytes mediante un protocolo autodescriptivo con etiquetas de tipo. Cada elemento se prefija con una etiqueta de tipo de un byte, seguida de un campo de longitud big-endian de ancho fijo (cuando corresponde), seguido de los bytes de carga útil. La concatenación de estos registros produce la cadena de bytes canónica final $b = \mathcal{C}_{v1}(x)$.

**Especificaciones de Entrada y Salida**

- **Entrada:** Un objeto de Python $x$ extraído del dominio admisible $\mathcal{D}$.
- **Salida:** Un objeto inmutable `bytes` $b \in \mathbb{B}^*$, que representa la serialización canónica de $x$.
- **Complejidad Temporal:** $O(n)$, donde $n$ es el número total de nodos atómicos y compuestos en el grafo de objetos.
- **Complejidad Espacial:** $O(n)$ para la cadena de bytes de salida, más $O(h)$ de espacio auxiliar en la pila de recursión, donde $h$ es la profundidad máxima del grafo.
- **Comportamiento Excepcional:** 
  - `CanonicalizationTypeError`: Elevada cuando $x$ contiene un tipo fuera del universo admisible o cuando se detecta una referencia cíclica.
  - `CanonicalizationValueError`: Elevada al encontrar valores de punto flotante no finitos o claves de diccionario que no sean cadenas.

**Garantías Deterministas**

El módulo te proporciona a vos, como operador forense, las siguientes garantías deterministas formales, sobre las cuales vos debés basar la confiabilidad de toda la cadena forense de VIGÍA:

1. **Reproducibilidad Bit a Bit Interarquitectural.** Al auditar la salida del sistema, vos verificás que para cualquier $x \in \mathcal{D}$, la expresión $\mathcal{C}_{v1}(x)$ resulta idéntica bit a bit independientemente del endianness de la CPU anfitriona (x86_64 little-endian, ARM big-endian, RISC-V bi-endian), del sistema operativo o de la versión parche del intérprete Python (dentro de la serie soportada 3.10+). Esto se logra mediante el mandato de formato big-endian y codificaciones explícitas de tipo-longitud.
2. **Independencia Temporal.** Vos observás que la función $\mathcal{C}_{v1}$ es una función pura de su entrada. Ninguna marca temporal, sal aleatoria, identificador de proceso o variable de entorno (incluyendo `PYTHONHASHSEED`) influye en la salida.
3. **Idempotencia Semántica.** Cuando vos comparás dos objetos de Python $x_1, x_2$ que son semánticamente equivalentes bajo las reglas del Esquema v1 —por ejemplo, $\texttt{dict}(\texttt{a}=1, \texttt{b}=2)$ y $\texttt{dict}(\texttt{b}=2, \texttt{a}=1)$—, comprobás que el módulo garantiza $\mathcal{C}_{v1}(x_1) = \mathcal{C}_{v1}(x_2)$.
4. **Estabilidad ante Mutación Admisible.** Si vos recibís $b$ y lo reanalizás en un objeto $x'$, obtenés la garantía de que reaplicar $\mathcal{C}_{v1}$ a $x'$ reproduce exactamente $b$ siempre que el analizador sea conforme al esquema. Este invariante de ida y vuelta es esencial para la verificación archivística a largo plazo en `vigia/storage/archive.py`.

**Relación con Otros Módulos de VIGÍA**

`vigia/core/canonicalize.py` funciona como una dependencia obligatoria para varios módulos posteriores, con los cuales vos debés integrarlo de manera estricta:

- **`vigia/core/ingest.py`:** El subsistema de ingesta invoca $\mathcal{C}_{v1}$ inmediatamente después de la deserialización probatoria para asegurar que todas las operaciones subsiguientes actúen sobre representaciones de bytes estabilizadas.
- **`vigia/core/hash.py`:** Calcula el digesto criptográfico $h = H_{\text{SHA-256}}(b)$. Este módulo nunca aplica hash a objetos crudos directamente; consume exclusivamente la salida de la rutina de canonicalización, lo cual vos debés respetar en todo desarrollo derivado.
- **`vigia/chain/merkle.py`:** Construye árboles de Merkle sobre lotes de registros probatorios. Cada nodo hoja del árbol corresponde a un digesto producido a partir de un objeto canonicalizado, garantizando así que el hash raíz agregado refleje un ordenamiento determinista de entradas semánticamente estables.
- **`vigia/verify/independent.py`:** Los verificadores independientes están deliberadamente prohibidos de importar `canonicalize.py`. En cambio, deben implementar un serializador equivalente al Esquema v1 a partir de la especificación. Esta separación arquitectónica previene que un error de implementación único se propague de manera indetectable a través de todo el ecosistema de verificación.
- **`vigia/audit/logger.py`:** Los registros de auditoría forense documentan el digesto $h$ y, bajo configuraciones de alta garantía, la longitud en bytes $|b|$ de la forma canónica, creando una traza no repudiable de la entrada exacta a la función de hash.

**Cumplimiento de Normas**

En tu desempeño forense, vos debés considerar que el diseño del Esquema Canónico v1 respalda directamente el cumplimiento de múltiples normativas nacionales e internacionales:

- **Estándar Daubert / FRE 702:** Para satisfacer este estándar, vos contás con un protocolo publicado y versionado con una tasa de error estocástico de cero sobre entradas admisibles, lo cual satisface los criterios de testabilidad, tasas de error conocidas y aceptación general requeridos para el testimonio de expertos en tribunales federales de los Estados Unidos.
- **GB/T 29360-2012** (*Informática forense de datos electrónicos*): Vos notarás que la estabilización determinista de las entradas de hash se alinea con las normas nacionales chinas para preservar la originalidad e integridad de la evidencia electrónica durante la recolección y el análisis.
- **MLPS 2.0** (*Esquema de Protección Multinivel, Nivel 3 y superior*): Respecto al MLPS 2.0, vos tenés la certeza de que la eliminación del no determinismo en la verificación de integridad respalda los requisitos obligatorios de auditoría y protección de datos para sistemas de información clasificados.
- **ISO/IEC 27037:2012** (*Directrices para la identificación, recolección, adquisición y preservación de evidencia digital*): La canonicalización asegura que el principio de originalidad se mantenga en el dominio digital, impidiendo que una deriva a nivel de formato sea interpretada erróneamente como una alteración probatoria.

**Conclusión**

`vigia/core/canonicalize.py` no es meramente una utilidad de serialización, sino el fundamento formal de la integridad probatoria dentro de VIGÍA. Al garantizar matemáticamente que estructuras de datos semánticamente idénticas convergen en una única cadena de bytes reproducible antes del hash, el módulo cierra una vulnerabilidad crítica en la cadena de custodia forense: la posibilidad de que una varianza representacional benigna sea confundida con un sabotaje de la evidencia o de que una no reproducibilidad del hash socave la admisibilidad legal.

## РУССКИЙ

`vigia/core/canonicalize.py` представляет собой единственный авторитетный источник реализации канонической функции системы VIGÍA, воплощая Каноническую схему v1 в качестве обязательного детерминированного протокола сериализации, применяемого ко всем структурам данных доказательственного характера до их криптографического закрепления. В архитектуре судебной экспертизы VIGÍA данный модуль занимает критически важное положение в цепочке сохранности: он преобразует семантически эквивалентные, но представленные различным образом объекты языка Python в единственную однозначную последовательность байтов. Устраняя представленческую вариативность—будь то порядок вставки в словари, ширина кодирования целых чисел, форма нормализации Unicode или порядок байтов хост-платформы,—модуль гарантирует, что входные данные для хеш-функции SHA-256 являются побитово идентичными во всех подсистемах, моментах выполнения и аппаратных архитектурах. Исключение составляют лишь независимые верификаторы, которым предписано воспроизводить схему из первых принципов во избежание циркулярных предположений о доверии; им прямой импорт данной процедуры запрещён.

**Математические основания**

Пусть $\mathcal{D}$ обозначает домен допустимых структур данных, принимаемых Канонической схемой v1. Этот домен включает конечные композиции базовых типов $\{\texttt{dict}, \texttt{list}, \texttt{tuple}, \texttt{str}, \texttt{int}, \texttt{float}, \texttt{bool}, \texttt{NoneType}, \texttt{bytes}\}$ при условии ацикличности графа объектов. Функция канонизации определяется как всюду определённое вычислимое отображение:

$$\mathcal{C}_{v1} : \mathcal{D} \to \mathbb{B}^*$$

где $\mathbb{B}^* = \bigcup_{n \geq 0} \{0,1\}^{8n}$ представляет собой множество всех байтовых строк конечной длины. Введём отношение семантической эквивалентности $\sim$ на $\mathcal{D}$ таким образом, что $d_1 \sim d_2$ тогда и только тогда, когда обе структуры кодируют тождественную логическую информацию в рамках правил интерпретации схемы (например, два словаря с одинаковыми ассоциациями «ключ—значение», независимо от порядка вставки). Каноническая схема v1 удовлетворяет инварианту:

$$\forall d_1, d_2 \in \mathcal{D}, \quad d_1 \sim d_2 \iff \mathcal{C}_{v1}(d_1) = \mathcal{C}_{v1}(d_2)$$

Указанное свойство устанавливает, что $\mathcal{C}_{v1}$ инъективна с точностью до семантической эквивалентности. Следовательно, композиция канонизации и хеш-функции SHA-256 $H_{\text{SHA-256}} : \mathbb{B}^* \to \{0,1\}^{256}$ порождает дайджест $h$, являющийся чистой функцией от семантики доказательственных данных:

$$h(d) = H_{\text{SHA-256}}(\mathcal{C}_{v1}(d))$$

Поскольку $H_{\text{SHA-256}}$ устойчива к коллизиям, а $\mathcal{C}_{v1}$ детерминирована, дайджест $h$ наследует строгую детерминированную гарантию: любое изменение семантического содержания $d$ или невозможность точного воспроизведения $\mathcal{C}_{v1}(d)$ приведёт к обнаружимому изменению $h$.

**Описание алгоритма**

Алгоритм, реализованный в `vigia/core/canonicalize.py`, выполняется в чётырёх строгих фазах, каждая из которых предназначена для устранения конкретного класса представленческого недетерминизма.

*Фаза I: Проверка допустимости и ацикличности.* Входной объект $x \in \mathcal{D}$ обходится с целью верификации принадлежности каждого узла разрешённому универсуму типов, а также проверки отсутствия циклов в графе объектов. При обнаружении цикла или недопустимого типа (например, экземпляра пользовательского класса Python) генерируется исключение `CanonicalizationTypeError`, и работа судебного конвейера прерывается для предотвращения неопределённого поведения при сериализации.

*Фаза II: Рекурсивная нормализация.* Модуль осуществляет обход графа объектов в глубину, слева направо. В ходе этого обхода каждый узел трансформируется в соответствии со специфическими правилами для данного типа:

- **Ассоциативные массивы (`dict`):** Ключи ограничиваются экземплярами `str`. Множество ключей $K = \{k_1, k_2, \dots, k_m\}$ упорядочивается по строгой лексикографической сортировке байтового представления каждого ключа в кодировке UTF-8. Полученная упорядоченная последовательность пар $(k_{(1)}, v_{(1)}), \dots, (k_{(m)}, v_{(m)})$ рекурсивно сериализуется. Данный шаг явным образом устраняет зависимость от порядка вставки элементов или рандомизации хеш-таблиц.
- **Строки Unicode (`str`):** Каждая строка нормализуется в соответствии с Канонической формой нормализации композиции C (NFC) согласно ISO/IEC 10646 и приложению UAX #15 стандарта Unicode. Нормализованная строка затем кодируется в UTF-8. Это устраняет вариативность эквивалентности, возникающую из-за различий между предварительно составными и разложенными последовательностями символов.
- **Целые числа (`int`):** Целые числа произвольной точности кодируются с использованием минимальной дополнительной двоичной записи (дополнение до двух) с прямым порядком байтов (big-endian), снабжённые префиксом типа и заголовком длины. Такое представление не зависит от разрядности хост-процессора или соглашений о знаковых целых.
- **Числа с плавающей запятой (`float`):** Значения представляются как последовательности байтов IEEE 754 binary64 (двойная точность) с прямым порядком байтов. Схема v1 накладывает два дополнительных ограничения: отрицательный ноль ($-0.0$) нормализуется к положительному нулю ($+0.0$), а не-конечные значения (`NaN`, `Inf`, `-Inf`) отвергаются посредством возбуждения `CanonicalizationValueError`. Эти ограничения необходимы, поскольку `NaN` не обладает рефлексивностью равенства в IEEE 754, а поведение знака нуля различается на различных платформах.
- **Последовательности (`list`, `tuple`):** Оба типа идентично кодируются как последовательности с префиксом длины, состоящие из рекурсивно канонизированных элементов, что гарантирует невозможность различения изменяемых и неизменяемых контейнеров на уровне сериализации.
- **Логические значения и пустое значение:** Кодируются как однобайтовые константы с меткой типа.
- **Байтовые строки (`bytes`):** Передаются непосредственно с префиксом длины, поскольку уже являются необработанными двоичными артефактами.

*Фаза III: Структурированная сериализация.* Нормализованный граф уплощается в байтовый поток посредством самоописывающего протокола с типовыми метками. Каждый элемент предваряется однобайтовой меткой типа, за которой следует поле длины фиксированной ширины в формате big-endian (применимо), а затем байты полезной нагрузки. Конкатенация данных записей формирует итоговую каноническую байтовую строку $b = \mathcal{C}_{v1}(x)$.

**Спецификации входных и выходных данных**

- **Вход:** Объект языка Python $x$, принадлежащий допустимому домену $\mathcal{D}$.
- **Выход:** Неизменяемый объект `bytes` $b \in \mathbb{B}^*$, представляющий каноническую сериализацию $x$.
- **Временная сложность:** $O(n)$, где $n$ — общее количество атомарных и составных узлов в графе объектов.
- **Пространственная сложность:** $O(n)$ для выходной байтовой строки плюс $O(h)$ вспомогательного стекового пространства, где $h$ — максимальная глубина графа объектов.
- **Исключительные ситуации:** 
  - `CanonicalizationTypeError`: возбуждается при обнаружении в $x$ типа вне допустимого универсума или при выявлении циклической ссылки.
  - `CanonicalizationValueError`: возбуждается при встрече не-конечных значений с плавающей запятой или при наличии в словаре ключей, не являющихся строками.

**Детерминированные гарантии**

Модуль обеспечивает следующие формальные детерминированные гарантии, которые совместно определяют судебную надёжность конвейера VIGÍA:

1. **Межархитектурная побитовая воспроизводимость.** Для любого $x \in \mathcal{D}$ выход $\mathcal{C}_{v1}(x)$ побитово идентичен независимо от порядка байтов центрального процессора (little-endian x86_64, big-endian ARM, bi-endian RISC-V), операционной системы или версии интерпретатора Python в пределах поддерживаемой ветви 3.10+. Достигается это посредством мандатного использования сетевого порядка байтов (big-endian) и явных кодировок тип—длина.
2. **Временная независимость.** Функция $\mathcal{C}_{v1}$ является чистой функцией своего аргумента. На выход не влияют временные метки, случайные соли, идентификаторы процессов или переменные окружения (включая `PYTHONHASHSEED`).
3. **Семантическая идемпотентность.** Для двух объектов Python $x_1, x_2$, семантически эквивалентных по правилам схемы v1—например, $\texttt{dict}(\texttt{a}=1, \texttt{b}=2)$ и $\texttt{dict}(\texttt{b}=2, \texttt{a}=1)$,—модуль гарантирует выполнение равенства $\mathcal{C}_{v1}(x_1) = \mathcal{C}_{v1}(x_2)$.
4. **Устойчивость к допустимой мутации.** Если подсистема получает $b$ и впоследствии реанализирует его в объект $x'$, повторное применение $\mathcal{C}_{v1}$ к $x'$ гарантированно воспроизводит $b$ при условии схемной совместимости анализатора. Данный инвариант прямого и обратного преобразования является критическим для долгосрочной архивной верификации в модуле `vigia/storage/archive.py`.

**Связь с прочими модулями VIGÍA**

`vigia/core/canonicalize.py` функционирует в качестве обязательной зависимости для ряда последующих модулей:

- **`vigia/core/ingest.py`:** Подсистема инжестирования вызывает $\mathcal{C}_{v1}$ непосредственно после десериализации доказательственных данных, гарантируя, что все последующие операции выполняются над стабилизированными байтовыми представлениями.
- **`vigia/core/hash.py`:** Вычисляет криптографический дайджест $h = H_{\text{SHA-256}}(b)$. Данный модуль никогда не применяет хеширование к необработанным объектам; он исключительно потребляет выходные данные канонической процедуры.
- **`vigia/chain/merkle.py`:** Конструирует деревья Меркля над пакетами доказательственных записей. Каждый листовой узел дерева соответствует дайджесту, полученному из канонизированного объекта, благодаря чему агрегированный корневой хеш отражает детерминированное упорядочение семантически стабильных входов.
- **`vigia/verify/independent.py`:** Независимым верификаторам прямой импорт `canonicalize.py` категорически запрещён. Вместо этого они обязаны реализовать эквивалентный сериализатор Схемы v1 на основании спецификации. Такое архитектурное разделение предотвращает распространение единичной ошибки реализации по всей верификационной экосистеме.
- **`vigia/audit/logger.py`:** Журналы судебного аудита фиксируют дайджест $h$ и, в режимах высокой гарантии, байтовую длину $|b|$ канонической формы, создавая неотказуемую трассу точного входа хеш-функции.

**Соответствие стандартам**

Проектирование Канонической схемы v1 непосредственно обеспечивает соблюдение ряда национальных и международных стандартов в области судебной экспертизы и информационной безопасности:

- **Стандарт Daubert / Правило 702 ФРС:** Публикуемый версионированный протокол с нулевой стохастической частотой ошибок на допустимых входах удовлетворяет критериям тестируемости, известных частот ошибок и общей признанности, обязательным для экспертных показаний в федеральных судах США.
- **GB/T 29360-2012** (*Криминалистическая экспертиза электронных данных*): Детерминированная стабилизация входных данных хеш-функции соответствует китайским национальным стандартам сохранения оригинальности и целостности электронных доказательств.
- **MLPS 2.0** (*Многоуровневая схема защиты, уровень 3 и выше*): Устранение недетерминизма в проверке целостности поддерживает обязательные требования к аудиту и защите данных для классифицированных информационных систем.
- **ISO/IEC 27037:2012**: Канонизация обеспечивает соблюдение принципа оригинальности в цифровой среде, предотвращая ошибочную интерпретацию представленческого дрейфа как фальсификации доказательств.

**Заключение**

`vigia/core/canonicalize.py` является не просто утилитой сериализации, но формальным фундаментом доказательственной целостности VIGÍA. Гарантируя математически, что семантически идентичные структуры данных сходятся к единственной воспроизводимой байтовой строке перед хешированием, модуль закрывает критическую уязвимость в судебной цепочке хранения: возможность того, что безвредная представленческая вариативность будет ошибочно принята за фальсификацию доказательств.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## 中文

`vigia/core/canonicalize.py` 是 VIGÍA 取证架构中规范化模式 v1 的唯一权威实现，充当确定性序列化网关，所有证据数据结构在提交密码学承诺之前必须经过此网关处理。在 VIGÍA 取证架构中，该模块在证据链中占据关键地位：它将语义等价但表示形式不同的 Python 对象转换为单一、无歧义的字节序列。通过消除表示差异——无论是字典插入顺序、整数编码宽度、Unicode 规范化形式还是宿主平台字节序——该模块确保 SHA-256 哈希函数的输入在所有子系统、执行时刻和硬件架构上逐位相同。只有独立验证器实现（需从第一原理重新构建模式以避免循环信任假设）可豁免直接导入此例程。

### Key Concepts（关键概念）

| 概念 | 定义 | 技术作用 |
|---|---|---|
| **规范化模式 v1** | 所有取证工件序列化必须遵循的版本化协议 | 作为哈希函数的确定性入口，消除表示歧义 |
| **精确整数运算** | 仅使用整数（位和字节）的计算范式，无近似 | 保证跨平台逐位可重现，消除舍入误差 |
| **语义等价性** | 两个结构在模式解释规则下编码相同逻辑信息 | 确保等价结构产生相同哈希值 |
| **Unicode NFC 规范化** | 将字符串统一为组合形式（ISO/IEC 10646 标准） | 消除由组合与分解字符序列引起的等价差异 |
| **字典键词典排序** | 按 UTF-8 字节编码的严格词典顺序对键排序 | 消除字典插入顺序和哈希随机化的依赖 |
| **类型标记序列化** | 每个元素附带单字节类型标记的自描述协议 | 产生明确、可独立解析的规范字节流 |
| **循环引用检测** | 对象图遍历时验证不存在环 | 防止序列化进入无限循环或未定义状态 |

### 【科学说明】

> **【科学说明】**
> 皮尔斯（Peirce）、艾柯（Eco）和格赖斯（Grice）的术语并非神秘主义——它们是形式传感器本体论。规范化模块是 VIGÍA 中的基础计量仪器：正如光谱仪将物理刺激转换为精确的波长整数，该模块将任意 Python 对象转换为单一规范字节序列。皮尔斯的"符号"在此就是输入对象；规范化函数是"解释项"——将符号映射为可验证字节字符串的确定性规则。艾柯的"百科全书"对应模式 v1 规范，所有实现必须遵循的共享校准标准。格赖斯的合作准则要求序列化是明确的（量的准则）、可重现的（质的准则）且无冗余的（方式准则）。该模块将这些抽象框架操作化为精确整数运算，确保法庭可重现性。

### 词汇表

1. **规范化函数（Canonicalization Function）** — 将语义等价的不同对象映射到相同字节字符串的确定性映射。
2. **精确整数运算（Exact Integer Arithmetic）** — 仅对精确整数执行的计算，不含近似或舍入误差。
3. **字节序（Endianness）** — 多字节数值中字节的排列顺序；该模块强制使用大端序以实现跨架构兼容。
4. **语义等价（Semantic Equivalence）** — 两个数据结构在规范化规则下编码相同逻辑内容的属性。
5. **循环引用（Cyclic Reference）** — 对象图中导致无限遍历的环；该模块检测并拒绝此类结构。
6. **规范字节字符串（Canonical Byte String）** — 应用规范化函数后，等价对象的唯一确定性字节序列。
7. **哈希链（Hash Chain）** — 将规范化字节序列传递给 SHA-256 以生成取证完整性摘要的组合操作。
8. **幂等性（Idempotence）** — 对已规范化数据重新应用函数产生相同输出的属性。
9. **道伯特标准（Daubert Standard）** — 美国联邦法庭要求科学方法具有可测试性和已知错误率的准则；该模块通过零随机性满足此标准。
10. **独立验证器（Independent Verifier）** — 必须从规范说明独立重新实现规范化的外部验证组件，以防止循环信任假设。

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

- **Стандарт Daubert / Правило 702 ФРС:** Внедрение опубликованного версионированного протокола с нулевой стохастической частотой ошибок на допустимых входах удовлетворяет критериям тестируемости, известных частот ошибок и общего приз