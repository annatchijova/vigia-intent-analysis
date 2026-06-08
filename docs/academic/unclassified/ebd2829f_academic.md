## ENGLISH

**Module Identifier:** `generate_release_bundle.py` (VIGÍA Hash: `ebd2829f`)

**1. Module Purpose and Forensic Context**

The module `generate_release_bundle.py` constitutes the canonical artifact-sealing engine of the VIGÍA forensic platform. Its primary forensic function is to generate cryptographically signed release bundles that encapsulate the totality of the platform's source code, build-time metadata, and a tamper-evident cryptographic manifest. Within the broader VIGÍA ecosystem, this module establishes the root-of-trust for all deployable software artifacts, ensuring that the binaries executed in controlled or field environments are bitwise identical to the source baseline subjected to peer review and SANS DFIR audit protocols.

The forensic necessity of this module arises from the *Daubert* standard's mandate that analytical tools used in legal proceedings must have demonstrably reliable provenance. By producing deterministic, reproducible, and authenticated bundles, `generate_release_bundle.py` satisfies the *Daubert* criteria of testability, known error rates, and general acceptance within the digital forensics community. The module operates prior to deployment, functioning as a critical chain-of-custody checkpoint that preserves software integrity from the conclusion of code review through to runtime execution.

**2. Mathematical Foundations**

The cryptographic rigor of the module rests on two primitives: the SHA-256 hash function and the HMAC-SHA256 message authentication code, both standardized under FIPS 180-4 and FIPS 198-1 respectively.

Let the source tree be represented as an ordered set of file canonicalizations \( \mathcal{F} = \{s_1, s_2, \ldots, s_n\} \), where each \( s_i \) is the pre-image of file \( f_i \) after deterministic normalization (line-ending canonicalization, permission standardization, and locale-independent lexicographic ordering of directory entries).

The SHA-256 compression function is denoted as:
\[
h: \{0,1\}^* \to \{0,1\}^{256}
\]
implemented via the Merkle-Damgård construction with Davies-Meyer compression, producing a 256-bit digest immune to pre-image and second pre-image attacks under standard cryptographic assumptions.

The manifest \( \mathcal{M} \) is defined as an ordered sequence of tuples:
\[
\mathcal{M} = \left[ (p_i, h_i) \right]_{i=1}^{n}, \quad h_i = \text{SHA-256}(s_i)
\]
where \( p_i \) is the canonical relative path of \( s_i \), and the sequence is ordered lexicographically by \( p_i \).

The HMAC-SHA256 construction is formalized as:
\[
\text{HMAC}(K, m) = H\Bigl( (K' \oplus \text{opad}) \,\|\, H\bigl( (K' \oplus \text{ipad}) \,\|\, m \bigr) \Bigr)
\]
where \( K \) is the secret signing key provisioned by VIGÍA.KeyOrchestrator, \( K' \) is the block-sized derivation of \( K \), \( H \) is SHA-256, \( \oplus \) denotes bitwise XOR, \( \| \) denotes concatenation, opad \( = \texttt{0x5c} \) repeated, and ipad \( = \texttt{0x36} \) repeated.

The deterministic archive \( \mathcal{A} \) is produced by canonical POSIX.1-2001 tar serialization of \( \mathcal{F} \) with fixed metadata fields (uid = gid = 0, mtime = 0 or deterministic commit timestamp, UStar format). The final bundle \( \mathcal{B} \) is the ordered structure:
\[
\mathcal{B} = (\mathcal{A}, \mathcal{M}, \sigma)
\]
where \( \sigma = \text{HMAC}(K_{\text{release}}, \text{Serialize}(\mathcal{A}, \mathcal{M})) \).

**3. Algorithm Description**

The execution of `generate_release_bundle.py` proceeds through five strictly ordered phases:

*Phase 1: Canonicalization.* The module traverses the source directory using a locale-independent lexicographic sort on path strings. All regular files are normalized: text files undergo line-ending conversion to UNIX LF (`\n`), file permissions are coerced to `0644` (regular) or `0755` (executable directories), and extended attributes are stripped unless explicitly whitelisted. Symlinks are dereferenced or recorded canonically per configuration policy.

*Phase 2: Manifest Generation.* For each canonicalized file \( s_i \), the module computes \( h_i = \text{SHA-256}(s_i) \). The resulting tuples \( (p_i, h_i) \) are assembled into \( \mathcal{M} \), serialized as a newline-delimited or JSON-structured manifest file, and itself hashed to produce \( h_{\mathcal{M}} \).

*Phase 3: Archive Construction.* The module streams the canonicalized tree into a POSIX tar archive with deterministic headers. Non-deterministic metadata (user names, stochastic timestamps, system-specific permissions) are overridden by fixed values. The tar stream is written to a temporary file and hashed to yield \( h_{\mathcal{A}} \).

*Phase 4: Cryptographic Binding.* Using the signing key handle retrieved from VIGÍA.KeyOrchestrator, the module computes the authentication tag \( \sigma \) over the bitwise concatenation of \( \mathcal{A} \) and \( \mathcal{M} \) (or their respective hashes, per policy). The signing operation occurs within a hardware-backed or HSM-bound context when available, preventing key exfiltration.

*Phase 5: Bundle Sealing and Emission.* The final artifact \( \mathcal{B} \) is emitted as a composite file or file set: the tar archive, the manifest, and the detached or appended signature. A JSON-LD chain-of-custody receipt is generated, linking \( \sigma \), \( h_{\mathcal{A}} \), \( h_{\mathcal{M}} \), the operator identity, and an immutable log sequence number (LSN) obtained from VIGÍA.AuditLogger.

**4. Input/Output Specifications**

*Inputs:*
- `SRC_DIR`: Absolute or relative path to the source tree root. Must be under version control (linked to VIGÍA.SourceAttestor).
- `KEY_HANDLE`: Cryptographic key reference managed by VIGÍA.KeyOrchestrator. May reference a symmetric HMAC key or an asymmetric private key.
- `BUILD_METADATA`: Dictionary containing `BUILD_ID`, `COMMIT_HASH`, `TIMESTAMP_POLICY` (epoch or deterministic), and `NORMALIZATION_RULES`.
- `POLICY_CONFIG`: Forensic policy flags governing symlink handling, extended attribute retention, and signature format (detached vs. inline).

*Outputs:*
- `vigia-release-{BUILD_ID}.tar`: Deterministic source archive \( \mathcal{A} \).
- `manifest.sha256`: Cryptographic manifest \( \mathcal{M} \) listing all \( (p_i, h_i) \).
- `bundle.sig` or inline signature: The authentication tag \( \sigma \).
- `custody-receipt.json`: Structured chain-of-custody record with LSN, timestamp, and operator binding.

*Error Conditions:*
- `NonDeterministicInputError`: Raised if the source tree contains files with non-reproducible ordering or unstable metadata that cannot be canonicalized.
- `KeyAccessViolation`: Raised if the key handle lacks signing authorization or the HSM communication channel fails.
- `HashMismatchException`: Raised if the computed manifest hash does not match the archive's internal manifest copy.

**5. Deterministic Guarantees**

The module provides three formal deterministic guarantees essential for forensic admissibility:

*Theorem 1 (Manifest Invariance).* Given a fixed input set \( \mathcal{F} \) and canonicalization policy \( C \), the manifest \( \mathcal{M} \) is invariant across executions on heterogeneous host systems. Formally:
\[
\forall \mathcal{F}, C: \; \mathcal{M}_1 = \mathcal{M}_2 \iff C(\mathcal{F})_1 = C(\mathcal{F})_2
\]
*Proof Sketch.* SHA-256 is a deterministic function. Lexicographic ordering is total and deterministic. Therefore, the ordered sequence of path-hash tuples is a pure function of \( C(\mathcal{F}) \).

*Theorem 2 (Archive Bitwise Identity).* Under the canonical tar policy (fixed uid/gid/mtime, deterministic ordering, UStar format), the archive stream \( \mathcal{A} \) is bitwise identical for any two executions with identical \( C(\mathcal{F}) \).

*Theorem 3 (Signature Unforgeability and Binding).* Under the random oracle model and the assumption that SHA-256 is collision-resistant, HMAC-SHA256 provides existential unforgeability against adaptive chosen-message attacks. Consequently, any alteration \( \mathcal{A}' \neq \mathcal{A} \) or \( \mathcal{M}' \neq \mathcal{M} \) results in verification failure with overwhelming probability.

**6. Chain-of-Custody and Standards Compliance**

The module is designed to satisfy multiple jurisdictional and institutional standards for digital evidence and secure software supply chains.

Under the *Daubert* standard, the module's outputs are testable (verifiable by VIGÍA.ManifestValidator), subject to known error rates (hash collision probability \( \approx 2^{-256} \)), and generally accepted via FIPS 180-4 and FIPS 198-1. This establishes the reliability of VIGÍA-derived evidence in U.S. federal proceedings.

Under *GB/T 29360-2012* (Electronic Data Forensics Standard of the People's Republic of China), the module fulfills the requirement for integrity verification of forensic tools prior to examination. The manifest \( \mathcal{M} \) serves as the mandatory checksum baseline for tool validation.

Under *MLPS 2.0* (Multi-Level Protection Scheme 2.0), Level 3 and above mandates cryptographic protection for critical system updates and deployment packages. The HMAC-SHA256 binding and HSM-backed key storage via VIGÍA.KeyOrchestrator satisfy the cryptographic control requirements for secure update transmission and storage.

SANS DFIR audit protocols are supported by the deterministic nature of \( \mathcal{B} \), enabling auditors to recompute hashes and validate \( \sigma \) independently.

**7. Related VIGÍA Modules**

- **VIGÍA.KeyOrchestrator:** Manages the lifecycle of \( K_{\text{release}} \), including HSM provisioning, key rotation, and access control. The signing operation in `generate_release_bundle.py` is delegated to this module's API to ensure private key material never resides in process memory.
- **VIGÍA.AuditLogger:** Provides an append-only, tamper-evident log. Every bundle generation event is recorded with an LSN, operator identity, and \( h_{\sigma} \), creating an auditable timeline.
- **VIGÍA.ManifestValidator:** The verification counterpart. It recomputes \( \mathcal{M} \) and verifies \( \sigma \) against the published public key or shared secret, used in CI/CD pipelines and field audits.
- **VIGÍA.DeployGuard:** Runtime enforcement agent that ingests \( \mathcal{B} \) and refuses deployment if \( \sigma \) is invalid or if \( \mathcal{M} \) contains unauthorized file modifications.
- **VIGÍA.SourceAttestor:** Links the bundle's `COMMIT_HASH` to the version control system, cryptographically attesting that the bundled source corresponds to a specific, reviewed commit.

**8. Security and Confidentiality Notice**

HMAC-SHA256 guarantees authenticity and integrity; it does not provide confidentiality. The release bundle \( \mathcal{B} \) must be protected in transit and at rest through complementary mechanisms—such as AES-256-GCM encryption or TLS 1.3 transport—governed by the organization's access control policy. The module itself does not perform encryption, in compliance with the principle of cryptographic separation of duties.

## ESPAÑOL

**Identificador del Módulo:** `generate_release_bundle.py` (Hash VIGÍA: `ebd2829f`)

**1. Propósito del Módulo y Contexto Forense**

El módulo `generate_release_bundle.py` constituye el motor de sellado de artefactos canónico de la plataforma forense VIGÍA. Su función forense principal consiste en generar paquetes de release firmados criptográficamente que encapsulan la totalidad del código fuente de la plataforma, los metadatos de compilación y un manifiesto criptográfico resistente a la manipulación. Dentro del ecosistema VIGÍA, este módulo establece la raíz de confianza para todos los artefactos de software desplegables, garantizando que los binarios ejecutados en entornos controlados o de campo sean idénticos bit a bit con respecto a la línea base de fuentes sometida a revisión por pares y a los protocolos de auditoría SANS DFIR.

Como operador forense, podés emplear este módulo para asegurar que tus herramientas de análisis cumplan con el mandato del estándar *Daubert*, que exige que las herramientas analíticas utilizadas en procedimientos legales posean una procedencia demostrablemente confiable. Al producir paquetes deterministas, reproducibles y autenticados, `generate_release_bundle.py` satisface los criterios de *Daubert* referidos a la testabilidad, las tasas de error conocidas y la aceptación general en la comunidad de informática forense. El módulo opera con anterioridad al despliegue y funciona como un punto de control crítico de la cadena de custodia que preserva la integridad del software desde la conclusión de la revisión de código hasta la ejecución en tiempo de ejecución.

**2. Fundamentos Matemáticos**

Para comprender el rigor criptográfico del módulo, debés considerar dos primitivas fundamentales: la función hash SHA-256 y el código de autenticación de mensajes HMAC-SHA256, estandarizadas respectivamente en FIPS 180-4 y FIPS 198-1.

Sea el árbol de fuentes representado como un conjunto ordenado de canonicalizaciones de archivos \( \mathcal{F} = \{s_1, s_2, \ldots, s_n\} \), donde cada \( s_i \) es la pre-imagen del archivo \( f_i \) luego de una normalización determinista (canonicalización de finales de línea, estandarización de permisos y ordenamiento lexicográfico independiente de la localización de las entradas de directorio).

La función de compresión SHA-256 se denota como:
\[
h: \{0,1\}^* \to \{0,1\}^{256}
\]
implementada mediante la construcción de Merkle-Damgård con compresión Davies-Meyer, produciendo un digest de 256 bits inmune a ataques de pre-imagen y segunda pre-imagen bajo supuestos criptográficos estándar.

El manifiesto \( \mathcal{M} \) se define como una secuencia ordenada de tuplas:
\[
\mathcal{M} = \left[ (p_i, h_i) \right]_{i=1}^{n}, \quad h_i = \text{SHA-256}(s_i)
\]
donde \( p_i \) es la ruta relativa canónica de \( s_i \), y la secuencia se ordena lexicográficamente por \( p_i \).

La construcción HMAC-SHA256 se formaliza como:
\[
\text{HMAC}(K, m) = H\Bigl( (K' \oplus \text{opad}) \,\|\, H\bigl( (K' \oplus \text{ipad}) \,\|\, m \bigr) \Bigr)
\]
donde \( K \) es la clave secreta de firma aprovisionada por VIGÍA.KeyOrchestrator, \( K' \) es la derivación de \( K \) a tamaño de bloque, \( H \) es SHA-256, \( \oplus \) denota el XOR bit a bit, \( \| \) denota la concatenación, opad \( = \texttt{0x5c} \) repetido, e ipad \( = \texttt{0x36} \) repetido.

El archivo determinista \( \mathcal{A} \) se produce mediante la serialización canónica tar conforme a POSIX.1-2001 de \( \mathcal{F} \) con campos de metadatos fijos (uid = gid = 0, mtime = 0 o timestamp de commit determinista, formato UStar). El paquete final \( \mathcal{B} \) es la estructura ordenada:
\[
\mathcal{B} = (\mathcal{A}, \mathcal{M}, \sigma)
\]
donde \( \sigma = \text{HMAC}(K_{\text{release}}, \text{Serialize}(\mathcal{A}, \mathcal{M})) \).

**3. Descripción del Algoritmo**

La ejecución de `generate_release_bundle.py` avanza mediante cinco fases estrictamente ordenadas:

*Fase 1: Canonicalización.* El módulo recorre el directorio de fuentes utilizando un ordenamiento lexicográfico independiente de la localización sobre las cadenas de ruta. Todos los archivos regulares se normalizan: los archivos de texto se someten a conversión de finales de línea a LF de UNIX (`\n`), los permisos de archivo se coercionan a `0644` (regulares) o `0755` (directorios ejecutables), y los atributos extendidos se eliminan salvo que estén explícitamente incluidos en una lista blanca. Los enlaces simbólicos se desreferencian o registran canónicamente según la política de configuración. Vos no necesitás intervenir manualmente en esta fase, pero podés auditar el log de canonicalización.

*Fase 2: Generación del Manifiesto.* Para cada archivo canonicalizado \( s_i \), el módulo computa \( h_i = \text{SHA-256}(s_i) \). Las tuplas resultantes \( (p_i, h_i) \) se ensamblan en \( \mathcal{M} \), serializadas como un archivo de manifiesto delimitado por saltos de línea o estructurado en JSON, y el propio manifiesto se hashea para producir \( h_{\mathcal{M}} \).

*Fase 3: Construcción del Archivo.* El módulo emite el árbol canonicalizado hacia un archivo tar POSIX con encabezados deterministas. Los metadatos no deterministas (nombres de usuario, timestamps estocásticos, permisos específicos del sistema) se sobrescriben con valores fijos. El flujo tar se escribe en un archivo temporal y se hashea para obtener \( h_{\mathcal{A}} \).

*Fase 4: Vinculación Criptográfica.* Utilizando el handle de clave de firma obtenido de VIGÍA.KeyOrchestrator, el módulo computa la etiqueta de autenticación \( \sigma \) sobre la concatenación bit a bit de \( \mathcal{A} \) y \( \mathcal{M} \) (o sus respectivos hashes, según la política). La operación de firma se ejecuta dentro de un contexto respaldado por hardware o vinculado a HSM cuando está disponible, evitando la exfiltración de la clave.

*Fase 5: Sellado y Emisión del Paquete.* El artefacto final \( \mathcal{B} \) se emite como un archivo compuesto o un conjunto de archivos: el archivo tar, el manifiesto y la firma adjunta o separada. Se genera un recibo de cadena de custodia en JSON-LD que vincula \( \sigma \), \( h_{\mathcal{A}} \), \( h_{\mathcal{M}} \), la identidad del operador y un número de secuencia de registro (LSN) inmutable obtenido de VIGÍA.AuditLogger.

**4. Especificaciones de Entrada y Salida**

A continuación, detallamos las entradas que debés proporcionar y las salidas que obtenés al ejecutar el módulo:

*Entradas:*
- `SRC_DIR`: Ruta absoluta o relativa a la raíz del árbol de fuentes. Debés asegurarte de que esté bajo control de versiones (vinculado a VIGÍA.SourceAttestor).
- `KEY_HANDLE`: Referencia criptográfica de clave gestionada por VIGÍA.KeyOrchestrator. Podés referirte a una clave simétrica HMAC o a una clave privada asimétrica.
- `BUILD_METADATA`: Diccionario que contiene `BUILD_ID`, `COMMIT_HASH`, `TIMESTAMP_POLICY` (época o determinista) y `NORMALIZATION_RULES`.
- `POLICY_CONFIG`: Banderas de política forense que gobiernan el manejo de enlaces simbólicos, la retención de atributos extendidos y el formato de firma (separada vs. inline).

*Salidas:*
- `vigia-release-{BUILD_ID}.tar`: Archivo de fuentes determinista \( \mathcal{A} \).
- `manifest.sha256`: Manifiesto criptográfico \( \mathcal{M} \) que lista todos los \( (p_i, h_i) \).
- `bundle.sig` o firma inline: La etiqueta de autenticación \( \sigma \).
- `custody-receipt.json`: Registro estructurado de cadena de custodia con LSN, timestamp y vinculación del operador.

*Condiciones de Error:*
- `NonDeterministicInputError`: Se dispara si el árbol de fuentes contiene archivos con ordenamiento no reproducible o metadatos inestables que no pueden canonicalizarse.
- `KeyAccessViolation`: Se dispara si el handle de clave carece de autorización para firmar o si el canal de comunicación con el HSM falla.
- `HashMismatchException`: Se dispara si el hash del manifiesto computado no coincide con la copia interna del manifiesto en el archivo.

**5. Garantías Deterministas**

El módulo te ofrece tres garantías deterministas formales esenciales para la admisibilidad forense:

*Teorema 1 (Invarianza del Manifiesto).* Dado un conjunto de entrada fijo \( \mathcal{F} \) y una política de canonicalización \( C \), el manifiesto \( \mathcal{M} \) es invariante entre ejecuciones en sistemas heterogéneos. Formalmente:
\[
\forall \mathcal{F}, C: \; \mathcal{M}_1 = \mathcal{M}_2 \iff C(\mathcal{F})_1 = C(\mathcal{F})_2
\]
*Esbozo de Demostración.* SHA-256 es una función determinista. El ordenamiento lexicográfico es total y determinista. Por lo tanto, la secuencia ordenada de tuplas ruta-hash es una función pura de \( C(\mathcal{F}) \). Si ejecutás dos veces el proceso con los mismos insumos, observás idénticos resultados.

*Teorema 2 (Identidad Bit a Bit del Archivo).* Bajo la política tar canónica (uid/gid/mtime fijos, ordenamiento determinista, formato UStar), el flujo de archivo \( \mathcal{A} \) es idéntico bit a bit para cualesquiera dos ejecuciones con idéntico \( C(\mathcal{F}) \).

*Teorema 3 (Vinculación e Inforgeabilidad de la Firma).* Bajo el modelo de oráculo aleatorio y el supuesto de que SHA-256 es resistente a colisiones, HMAC-SHA256 provee inforgeabilidad existencial ante ataques adaptativos de mensaje escogido. En consecuencia, cualquier alteración \( \mathcal{A}' \neq \mathcal{A} \) o \( \mathcal{M}' \neq \mathcal{M} \) resulta en un fallo de verificación con probabilidad abrumadora.

**6. Cadena de Custodia y Cumplimiento Normativo**

Como profesional de la informática forense, debés asegurarte de que tus herramientas cumplan con los estándares internacionales. El módulo está diseñado para satisfacer múltiples estándares jurisdiccionales e institucionales para evidencia digital y cadenas de suministro de software seguras.

Bajo el estándar *Daubert*, las salidas del módulo son testables (verificables mediante VIGÍA.ManifestValidator), sujetas a tasas de error conocidas (probabilidad de colisión de hash \( \approx 2^{-256} \)), y generalmente aceptadas mediante FIPS 180-4 y FIPS 198-1. Esto establece la confiabilidad de la evidencia derivada de VIGÍA en procedimientos federales de los Estados Unidos.

Bajo la norma *GB/T 29360-2012* (Estándar de Informática Forense de Datos Electrónicos de la República Popular China), el módulo cumple con el requisito de verificación de integridad de herramientas forenses previo al examen. El manifiesto \( \mathcal{M} \) sirve como la línea base obligatoria de checksum para la validación de herramientas.

Bajo el *MLPS 2.0* (Esquema de Protección Multi-Nivel 2.0), los Niveles 3 y superiores exigen protección criptográfica para actualizaciones críticas del sistema y paquetes de despliegue. El vínculo HMAC-SHA256 y el almacenamiento de claves respaldado por HSM a través de VIGÍA.KeyOrchestrator satisfacen los requisitos de controles criptográficos para la transmisión y almacenamiento seguros de actualizaciones.

Los protocolos de auditoría SANS DFIR se sustentan en la naturaleza determinista de \( \mathcal{B} \), permitiendo que los auditores recomputen los hashes y validen \( \sigma \) de manera independiente.

**7. Módulos VIGÍA Relacionados**

Contás con los siguientes módulos relacionados para complementar el flujo forense:

- **VIGÍA.KeyOrchestrator:** Gestiona el ciclo de vida de \( K_{\text{release}} \), incluyendo el aprovisionamiento en HSM, la rotación de claves y el control de acceso. La operación de firma en `generate_release_bundle.py` se delega a la API de este módulo para garantizar que el material de clave privada nunca resida en la memoria del proceso.
- **VIGÍA.AuditLogger:** Provee un registro de solo adición, resistente a la manipulación. Cada evento de generación de paquete se registra con un LSN, la identidad del operador y \( h_{\sigma} \), creando una línea de tiempo auditable.
- **VIGÍA.ManifestValidator:** La contraparte de verificación. Recomputa \( \mathcal{M} \) y verifica \( \sigma \) contra la clave pública publicada o el secreto compartido, utilizado en pipelines de CI/CD y auditorías de campo. Podés ejecutarlo independientemente para validar cualquier paquete.
- **VIGÍA.DeployGuard:** Agente de cumplimiento en tiempo de ejecución que ingiere \( \mathcal{B} \) y se niega a desplegarlo si \( \sigma \) es inválida o si \( \mathcal{M} \) contiene modificaciones no autorizadas en archivos.
- **VIGÍA.SourceAttestor:** Vincula el `COMMIT_HASH` del paquete al sistema de control de versiones, atestando criptográficamente que el código fuente empaquetado corresponde a un commit específico y revisado.

**8. Aviso de Seguridad y Confidencialidad**

Tenés presente que HMAC-SHA256 garantiza autenticidad e integridad; no provee confidencialidad. El paquete de release \( \mathcal{B} \) debe protegerse en tránsito y en reposo mediante mecanismos complementarios —tales como cifrado AES-256-GCM o transporte TLS 1.3— gobernados por la política de control de acceso de la organización. El módulo en sí no realiza cifrado, en cumplimiento con el principio de separación de funciones criptográficas.

## РУССКИЙ

**Идентификатор модуля:** `generate_release_bundle.py` (Хэш VIGÍA: `ebd2829f`)

**1. Назначение модуля и судебный контекст**

Модуль `generate_release_bundle.py` представляет собой канонический механизм упаковки и заверения артефактов судебной платформы VIGÍA. Его основная судебная функция заключается в формировании криптографически подписанных пакетов выпуска, инкапсулирующих полный исходный код платформы, метаданные сборки и криптографически стойкий манифест, устойчивый к несанкционированному изменению. В рамках экосистемы VIGÍA данный модуль устанавливает корень доверия для всех развёртываемых программных артефактов, гарантируя, что исполняемые в контролируемых или полевых условиях бинарные файлы являются побитово идентичными базовому уровню исходного кода, прошедшему экспертную оценку и аудит по протоколам SANS DFIR.

Потребность в данном модуле обусловлена требованиями стандарта *Daubert*, предписывающего, чтобы аналитические инструменты, используемые в судебных разбирательствах, обладали доказуемо надёжной происхождением. Производя детерминированные, воспроизводимые и аутентифицированные пакеты, `generate_release_bundle.py` удовлетворяет критериям *Daubert*, касающимся тестируемости, известных частот ошибок и общего признания в сообществе цифровой судебной экспертизы. Модуль функционирует на этапе, предшествующем развёртыванию, выступая критически важным пунктом контроля цепочки хранения, обеспечивающим сохранение целостности программного обеспечения с момента завершения проверки кода до момента его исполнения.

**2. Математические основания**

Криптографическая строгость модуля базируется на двух примитивах: хэш-функции SHA-256 и коде аутентификации сообщений HMAC-SHA256, стандартизированных соответственно в FIPS 180-4 и FIPS 198-1.

Пусть дерево исходного кода представлено в виде упорядоченного множества канонизированных файлов \( \mathcal{F} = \{s_1, s_2, \ldots, s_n\} \), где каждый \( s_i \) является прообразом файла \( f_i \) после детерминированной нормализации (канонизация окончаний строк, стандартизация прав доступа и лексикографическое упорядочение элементов каталога, не зависящее от локали).

Функция сжатия SHA-256 обозначается как:
\[
h: \{0,1\}^* \to \{0,1\}^{256}
\]
реализуемая посредством конструкции Меркла — Дамгора со сжатием по Дэвису — Мейеру, формирующая 256-битный дайджест, устойчивый к атакам на прообраз и второй прообраз в рамках стандартных криптографических предположений.

Манифест \( \mathcal{M} \) определяется как упорядоченная последовательность кортежей:
\[
\mathcal{M} = \left[ (p_i, h_i) \right]_{i=1}^{n}, \quad h_i = \text{SHA-256}(s_i)
\]
где \( p_i \) — канонический относительный путь \( s_i \), а последовательность упорядочена лексикографически по \( p_i \).

Конструкция HMAC-SHA256 формализуется следующим образом:
\[
\text{HMAC}(K, m) = H\Bigl( (K' \oplus \text{opad}) \,\|\, H\bigl( (K' \oplus \text{ipad}) \,\|\, m \bigr) \Bigr)
\]
где \( K \) — секретный ключ подписи, предоставляемый модулем VIGÍA.KeyOrchestrator, \( K' \) — производная от \( K \) размером с блок, \( H \) — SHA-256, \( \oplus \) обозначает побитовое исключающее ИЛИ, \( \| \) — конкатенацию, opad \( = \texttt{0x5c} \), повторяемый необходимое число раз, и ipad \( = \texttt{0x36} \), повторяемый аналогичным образом.

Детерминированный архив \( \mathcal{A} \) формируется путём канонической сериализации дерева \( \mathcal{F} \) в формат tar согласно POSIX.1-2001 с фиксированными полями метаданных (uid = gid = 0, mtime = 0 или детерминированная метка коммита, формат UStar). Итоговый пакет \( \mathcal{B} \) представляет собой упорядоченную структуру:
\[
\mathcal{B} = (\mathcal{A}, \mathcal{M}, \sigma)
\]
где \( \sigma = \text{HMAC}(K_{\text{release}}, \text{Serialize}(\mathcal{A}, \mathcal{M})) \).

**3. Описание алгоритма**

Выполнение модуля `generate_release_bundle.py` осуществляется в пять строго упорядоченных фаз:

*Фаза 1: Канонизация.* Модуль осуществляет обход исходного каталога с применением лексикографической сортировки строк путей, не зависящей от локали. Все обычные файлы подвергаются нормализации: текстовые файлы преобразуются к окончаниям строк UNIX LF (`\n`), права доступа к файлам приводятся к значениям `0644` (обычные файлы) или `0755` (исполняемые каталоги), расширенные атрибуты удаляются, если они не включены в белый список. Символические ссылки разыменовываются или регистрируются каноническим образом в соответствии с политикой конфигурации.

*Фаза 2: Генерация манифеста.* Для каждого канонизированного файла \( s_i \) модуль вычисляет \( h_i = \text{SHA-256}(s_i) \). Полученные кортежи \( (p_i, h_i) \) собираются в \( \mathcal{M} \), сериализуются в файл манифеста с разделителем в виде новой строки или в структурированном формате JSON, после чего сам манифест хэшируется для получения \( h_{\mathcal{M}} \).

*Фаза 3: Построение архива.* Модуль формирует поток канонизированного дерева в архив tar стандарта POSIX с детерминированными заголовками. Недетерминированные метаданные (имена пользователей, стохастические временные метки, системно-специфичные права) замещаются фиксированными значениями. Поток tar записывается во временный файл и хэшируется с целью получения \( h_{\mathcal{A}} \).

*Фаза 4: Криптографическая привязка.* Используя дескриптор ключа подписи, полученный от VIGÍA.KeyOrchestrator, модуль вычисляет тег аутентификации \( \sigma \) над побитовой конкатенацией \( \mathcal{A} \) и \( \mathcal{M} \) (или их соответствующих хэшей — в зависимости от политики). Операция подписи выполняется в аппаратно защищённом контексте или внутри модуля HSM при его наличии, что исключает эксфильтрацию ключа.

*Фаза 5: Упаковка и выдача пакета.* Итоговый артефакт \( \mathcal{B} \) выдаётся в виде составного файла или набора файлов: архива tar, манифеста и отсоединённой либо встроенной подписи. Формируется квитанция цепочки хранения в формате JSON-LD, связывающая \( \sigma \), \( h_{\mathcal{A}} \), \( h_{\mathcal{M}} \), идентификатор оператора и неизменяемый порядковый номер журнала (LSN), полученный от VIGÍA.AuditLogger.

**4. Спецификации входных и выходных данных**

*Входные данные:*
- `SRC_DIR`: Абсолютный или относительный путь к корню дерева исходного кода. Должен находиться под контролем версий (связан с VIGÍA.SourceAttestor).
- `KEY_HANDLE`: Ссылка на криптографический ключ, управляемый VIGÍA.KeyOrchestrator. Может указывать на симметричный ключ HMAC или на асимметричный закрытый ключ.
- `BUILD_METADATA`: Словарь, содержащий `BUILD_ID`, `COMMIT_HASH`, `TIMESTAMP_POLICY` (эпоха или детерминированная метка), а также `NORMALIZATION_RULES`.
- `POLICY_CONFIG`: Флаги судебной политики, регламентирующие обработку символических ссылок, сохранение расширенных атрибутов и формат подписи (отсоединённая или встроенная).

*Выходные данные:*
- `vigia-release-{BUILD_ID}.tar`: Детерминированный архив исходного кода \( \mathcal{A} \).
- `manifest.sha256`: Криптографический манифест \( \mathcal{M} \), содержащий перечисление всех \( (p_i, h_i) \).
- `bundle.sig` или встроенная подпись: Тег аутентификации \( \sigma \).
- `custody-receipt.json`: Структурированная запись цепочки хранения с LSN, временной меткой и привязкой к оператору.

*Условия возникновения ошибок:*
- `NonDeterministicInputError`: Инициируется, если дерево исходного кода содержит файлы с невоспроизводимым порядком или нестабильными метаданными, поддающимися канонизации.
- `KeyAccessViolation`: Инициируется, если дескриптор ключа не обладает полномочиями на подпись либо нарушено соединение с HSM.
- `HashMismatchException`: Инициируется, если вычисленный хэш манифеста не совпадает с внутренней копией манифеста в архиве.

**5. Детерминистские гарантии**

Модуль обеспечивает три формальные детерминистские гарантии, являющиеся необходимыми для судебного допустимости результатов:

*Теорема 1 (Инвариантность манифеста).* При фиксированном входном множестве \( \mathcal{F} \) и политике канонизации \( C \) манифест \( \mathcal{M} \) инвариантен относительно выполнения на разнородных хост-системах. Формально:
\[
\forall \mathcal{F}, C: \; \mathcal{M}_1 = \mathcal{M}_2 \iff C(\mathcal{F})_1 = C(\mathcal{F})_2
\]
*Схема доказательства.* SHA-256 является детерминированной функцией. Лексикографическое упорядочение является полным и детерминированным. Следовательно, упорядоченная последовательность кортежей «путь — хэш» представляет собой чистую функцию от \( C(\mathcal{F}) \).

*Теорема 2 (Побитовая идентичность архива).* При соблюдении политики канонического tar (фиксированные uid/gid/mtime, детерминированное упорядочение, формат UStar) поток архива \( \mathcal{A} \) является побитово идентичным для любых двух выполнений при идентичном \( C(\mathcal{F}) \).

*Теорема 3 (Привязка подписи и неподделываемость).* В модели случайного оракула при предположении о столкновительной стойкости SHA-256 конструкция HMAC-SHA256 обеспечивает экзистенциальную неподделываемость при адаптивных атаках с выбором сообщения. Следовательно, любое изменение \( \mathcal{A}' \neq \mathcal{A} \) или \( \mathcal{M}' \neq \mathcal{M} \) приводит к отказу верификации с подавляющей вероятностью.

**6. Цепочка хранения и соответствие стандартам**

Модуль спроектирован с учётом требований многочисленных юрисдикционных и институциональных стандартов, регламентирующих обращение с цифровыми доказательствами и обеспечение безопасности цепочек поставок программного обеспечения.

В соответствии со стандартом *Daubert* выходные данные модуля являются тестируемыми (верифицируемыми посредством VIGÍA.ManifestValidator), подчиняются известным частотам ошибок (вероятность хэш-коллизии \( \approx 2^{-256} \)) и общепризнаны на основании FIPS 180-4 и FIPS 198-1. Это устанавливает надёжность доказательств, полученных с применением VIGÍA, в федеральных судебных разбирательствах США.

В соответствии со стандартом *GB/T 29360-2012* (стандарт компьютерной судебной экспертизы электронных данных Китайской Народной Республики) модуль удовлетворяет требованию обязательной проверки целостности судебных инструментов перед экспертизой. Манифест \( \mathcal{M} \) выступает в роли обязательной базовой линии контрольной суммы для валидации инструментария.

В соответствии с требованиями *MLPS 2.0* (многоуровневой системы защиты, уровни 3 и выше) предписывается криптографическая защита критических обновлений системы и пакетов развёртывания. Криптографическая привязка HMAC-SHA256 и хранение ключей в HSM посредством VIGÍA.KeyOrchestrator удовлетворяют требованиям криптографических контролей, обеспечивающих безопасную передачу и хранение обновлений.

Протоколы аудита SANS DFIR поддерживаются детерминистской природой \( \mathcal{B} \), позволяющей аудиторам самостоятельно пересчитывать хэши и верифицировать \( \sigma \).

**7. Связанные модули VIGÍA**

- **VIGÍA.KeyOrchestrator:** Управляет жизненным циклом ключа \( K_{\text{release}} \), включая развёртывание в HSM, ротацию ключей и управление доступом. Операция подписи в модуле `generate_release_bundle.py` делегируется API данного модуля, что гарантирует отсутствие закрытого ключа в оперативной памяти процесса.
- **VIGÍA.AuditLogger:** Обеспечивает журнал с возможностью только добавления записей, устойчивый к несанкционированному изменению. Каждое событие формирования пакета регистрируется с указанием LSN, идентификатора оператора и \( h_{\sigma} \), формируя поддающуюся аудиту временную шкалу.
- **VIGÍA.ManifestValidator:** Компонент верификации, выполняющий пересчёт \( \mathcal{M} \) и проверку \( \sigma \) относительно опубликованного открытого ключа или общего секрета. Используется в конвейерах CI/CD и при полевых аудитах.
- **VIGÍA.DeployGuard:** Агент принудительного контроля в режиме исполнения, который принимает \( \mathcal{B} \) и блокирует развёртывание при недействительности \( \sigma \) либо при наличии в \( \mathcal{M} \) несанкционированных изменений файлов.
- **VIGÍA.SourceAttestor:** Устанавливает связь между хэшем коммита (`COMMIT_HASH`) пакета и системой управления версиями, криптографически засвидетельствуя, что упакованный исходный код соответствует конкретному прошедшему проверку коммиту.

**8. Примечание по безопасности и конфиденциальности**

Конструкция HMAC-SHA256 гарантирует аутентичность и целостность, однако не обеспечивает конфиденциальность. Пакет выпуска \( \mathcal{B} \) должен защищаться при передаче и в состоянии покоя дополнительными механизмами — например, шифрованием AES-256-GCM или транспортом TLS 1.3, — регулируемыми корпоративной политикой управления доступом. Сам модуль не выполняет шифрования, что соответствует принципу разделения криптографических функций.

## 中文

**模块标识符：** `generate_release_bundle.py`（VIGÍA 哈希：`ebd2829f`）

**1. 模块目的与取证语境**

`generate_release_bundle.py` 模块是 VIGÍA 取证平台的规范化工件封装引擎。其核心的取证功能在于生成经密码学签名的发布包（release bundle），该发布包完整封装平台源代码、构建时元数据以及具备防篡改能力的密码学清单（manifest）。在 VIGÍA 生态系统内，本模块为所有可部署软件工件建立信任根（root-of-trust），确保受控环境或现场环境中执行的二进制文件与经同行评审及 SANS DFIR 审计协议审查的源代码基线保持逐位一致。

本模块的取证必要性源于 *Daubert* 标准的要求：用于法律程序的分析工具必须具备可证明的可靠来源。通过生成确定性、可复现且已认证的发布包，`generate_release_bundle.py` 满足了 *Daubert* 标准关于可测试性、已知错误率及数字取证领域普遍接受性的要求。该模块运行于部署前阶段，作为监管链（chain-of-custody）的关键控制节点，自代码审查结束起直至运行时刻，持续保全软件完整性。

**2. 数学基础**

本模块的密码学严谨性建立在两种基础原语之上：SHA-256 哈希函数与 HMAC-SHA256 消息认证码，二者分别由 FIPS 180-4 与 FIPS 198-1 标准化。

设源码树表示为经规范化处理的文件的ordered set \( \mathcal{F} = \{s_1, s_2, \ldots, s_n\} \)，其中每个 \( s_i \) 均为文件 \( f_i \) 经确定性规范化（行尾符规范化、权限标准化、目录项与区域设置无关的词典序排序）后的原像。

SHA-256 压缩函数记为：
\[
h: \{0,1\}^* \to \{0,1\}^{256}
\]
其实现采用 Merkle-Damgård 结构及 Davies-Meyer 压缩方式，在标准密码学假设下可生成抗原像攻击与第二原像攻击的 256 位摘要。

清单 \( \mathcal{M} \) 定义为有序元组序列：
\[
\mathcal{M} = \left[ (p_i, h_i) \right]_{i=1}^{n}, \quad h_i = \text{SHA-256}(s_i)
\]
其中 \( p_i \) 为 \( s_i \) 的规范化相对路径，序列按 \( p_i \) 词典序排列。

HMAC-SHA256 构造形式化表述为：
\[
\text{HMAC}(K, m) = H\Bigl( (K' \oplus \text{opad}) \,\|\, H\bigl( (K' \oplus \text{ipad}) \,\|\, m \bigr) \Bigr)
\]
式中，\( K \) 为由 VIGÍA.KeyOrchestrator 提供的签名密钥；\( K' \) 为经填充至分组长度后的密钥派生值；\( H \) 为 SHA-256；\( \oplus \) 表示按位异或；\( \| \) 表示串联；opad 为重复填充的 `0x5c`；ipad 为重复填充的 `0x36`。

确定性归档 \( \mathcal{A} \) 采用符合 POSIX.1-2001 的 tar 格式对 \( \mathcal{F} \) 进行规范化序列化，元数据字段固定（uid = gid = 0，mtime = 0 或确定性提交时间戳，UStar 格式）。最终发布包 \( \mathcal{B} \) 为有序结构：
\[
\mathcal{B} = (\mathcal{A}, \mathcal{M}, \sigma)
\]
其中 \( \sigma = \text{HMAC}(K_{\text{release}}, \text{Serialize}(\mathcal{A}, \mathcal{M})) \)。

**3. 算法描述**

`generate_release_bundle.py` 的执行严格按以下五个阶段展开：

*阶段一：规范化（Canonicalization）。* 模块以与区域设置无关的词典序遍历源码目录路径字符串。所有常规文件均接受规范化处理：文本文件行尾统一转换为 UNIX LF（`\n`）；文件权限强制为 `0644`（普通文件）或 `0755`（可执行目录）；扩展属性除非显式列入白名单否则一律剥离；符号链接根据配置策略进行解引用或规范化记录。

*阶段二：清单生成。* 对每个规范化文件 \( s_i \)，模块计算 \( h_i = \text{SHA-256}(s_i) \)。所得元组 \( (p_i, h_i) \) 被组装为 \( \mathcal{M} \)，并以换行分隔或 JSON 结构形式序列化为清单文件，随后对清单本身进行哈希运算得到 \( h_{\mathcal{M}} \)。

*阶段三：归档构建。* 模块将规范化后的源码树流式写入具有确定性头部的 POSIX tar 归档。非确定性元数据（用户名、随机时间戳、系统相关权限）被固定值覆盖。tar 流写入临时文件并进行哈希运算，得到 \( h_{\mathcal{A}} \)。

*阶段四：密码学绑定。* 模块利用从 VIGÍA.KeyOrchestrator 获取的签名密钥句柄，针对 \( \mathcal{A} \) 与 \( \mathcal{M} \) 的按位串联（或根据策略采用其各自哈希值）计算认证标签 \( \sigma \)。签名操作在硬件支持或 HSM 边界内完成，以防密钥外泄。

*阶段五：包封与输出。* 最终工件 \( \mathcal{B} \) 以组合文件或文件集形式输出：tar 归档、清单文件、以及分离式或内联式签名。同时生成 JSON-LD 格式的监管链接收凭据，关联 \( \sigma \)、\( h_{\mathcal{A}} \)、\( h_{\mathcal{M}} \)、操作者身份及由 VIGÍA.AuditLogger 提供的不可变日志序列号（LSN）。

**4. 输入输出规范**

*输入：*
- `SRC_DIR`：源码树根目录的绝对或相对路径，须处于版本控制之下（并与 VIGÍA.SourceAttestor 关联）。
- `KEY_HANDLE`：由 VIGÍA.KeyOrchestrator 管理的密码学密钥引用，可指向对称 HMAC 密钥或非对称私钥。
- `BUILD_METADATA`：包含 `BUILD_ID`、`COMMIT_HASH`、`TIMESTAMP_POLICY`（纪元时间或确定性时间戳）及 `NORMALIZATION_RULES` 的字典。
- `POLICY_CONFIG`：取证策略标志，管控符号链接处理、扩展属性保留及签名格式（分离式/内联式）。

*输出：*
- `vigia-release-{BUILD_ID}.tar`：确定性源码归档 \( \mathcal{A} \)。
- `manifest.sha256`：密码学清单 \( \mathcal{M} \)，列出全部 \( (p_i, h_i) \)。
- `bundle.sig` 或内联签名：认证标签 \( \sigma \)。
- `custody-receipt.json`：结构化监管链记录，含 LSN、时间戳及操作者绑定信息。

*错误条件：*
- `NonDeterministicInputError`：源码树包含