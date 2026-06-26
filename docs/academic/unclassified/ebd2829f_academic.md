<!-- VIGÍA Academic Documentation | Module: generate_release_bundle.py | Hash: ebd2829f | Format: Standardized v1 -->

## ENGLISH

### What Is This Module?

`generate_release_bundle.py` (VIGÍA hash `ebd2829f`) is the canonical artifact-sealing engine of the VIGÍA forensic platform. Its purpose is to generate cryptographically signed release bundles that encapsulate the platform's complete source tree, build-time metadata, and a tamper-evident manifest — and to do so in a way that is bit-for-bit reproducible from the same source inputs on any conformant system.

The forensic necessity of this module is direct: the Daubert standard requires that analytical tools used in legal proceedings have demonstrably reliable provenance. If an examiner cannot prove that the binaries they ran are identical to the code that was reviewed and approved, the chain of custody is broken. This module establishes that chain. It acts as a critical custody checkpoint between code review and runtime execution, producing a bundle B = (A, M, σ) — a deterministic tar archive A, a cryptographic manifest M = [(p_i, h_i)], and an HMAC-SHA256 authentication tag σ.

The module operates over five strictly ordered phases: (1) Canonicalization — locale-independent lexicographic traversal, line-ending normalization, permission standardization; (2) Manifest Generation — SHA-256 of each file, assembled into M; (3) Archive Construction — deterministic POSIX tar with fixed metadata (uid=gid=0, mtime=0 or deterministic commit timestamp, UStar format); (4) Cryptographic Binding — HMAC-SHA256 over A∥M using a key from VIGÍA.KeyOrchestrator; (5) Bundle Sealing — emission of B with a JSON-LD chain-of-custody receipt.

### Key Concepts

| Concept | Definition |
|---------|-----------|
| Source tree canonicalization | Locale-independent lexicographic traversal; line endings → LF; permissions → 0644/0755; extended attributes stripped |
| Manifest M | Ordered sequence [(p_i, h_i)] where h_i = SHA-256(s_i) and p_i is the canonical relative path; sorted lexicographically |
| Archive A | Deterministic POSIX.1-2001 tar with fixed metadata fields (uid=gid=0, mtime=0 or commit timestamp, UStar format) |
| Bundle B | Ordered triple (A, M, σ): the archive, the manifest, and the authentication tag |
| HMAC-SHA256 σ | σ = HMAC(K_release, Serialize(A, M)); provides existential unforgeability under adaptive chosen-message attack |
| SHA-256 collision probability | ≈ 2^−256; this is the known error rate satisfying the Daubert "known error rate" criterion |
| VIGÍA.KeyOrchestrator | Module managing the signing key lifecycle; private key material never resides in process memory |
| Chain-of-custody receipt | JSON-LD record linking σ, hash of A, hash of M, operator identity, and immutable log sequence number (LSN) |
| NonDeterministicInputError | Exception raised if the source tree contains files with non-reproducible ordering or unstable metadata |

> **【Scientific Note】**
> The phrase "cryptographic signing" may invoke a sense of complexity, but the underlying operation is analogous to a calibration seal on a measurement instrument. The manifest M is the calibration certificate listing the measured value of every component. The HMAC tag σ is the seal that proves the certificate was issued by an authorized technician with a known key. If any component changes after sealing — even one bit — the seal verification fails. This is not a probabilistic or heuristic check: SHA-256 under the Merkle-Damgård construction is a deterministic function, and HMAC-SHA256 provides information-theoretic guarantees of unforgeability under cryptographic assumptions that are standardized in FIPS 180-4 and FIPS 198-1. Peirce, Eco, and Grice are not needed here — this module operates at the level of physical-layer integrity, below the semantic layer where intentionality analysis begins.

### Glossary

| Term | Definition |
|------|-----------|
| generate_release_bundle.py | Module that seals the VIGÍA source tree into a cryptographically authenticated, reproducible release bundle |
| canonicalization | Process of normalizing all source files to a deterministic, platform-independent representation |
| manifest M | Ordered list of (path, SHA-256 hash) pairs covering every file in the release |
| deterministic tar archive | POSIX tar stream with fixed metadata so identical source trees produce bit-identical archives |
| HMAC-SHA256 | Hash-based message authentication code; proves authenticity and integrity without providing confidentiality |
| signing key K_release | Secret key managed by VIGÍA.KeyOrchestrator; used to compute the bundle authentication tag σ |
| chain of custody | Documented, verifiable record linking every artifact to its origin and all subsequent custody events |
| LSN (log sequence number) | Monotonic identifier from VIGÍA.AuditLogger anchoring each bundle generation event to the audit timeline |
| HashMismatchException | Exception raised when the recomputed manifest hash does not match the archive's internal manifest copy |

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## ESPAÑOL

### ¿Qué es este módulo?

`generate_release_bundle.py` (hash VIGÍA `ebd2829f`) es el motor de sellado de artefactos canónico de la plataforma forense VIGÍA. Su propósito es generar paquetes de release firmados criptográficamente que encapsulan el árbol de fuentes completo de la plataforma, metadatos de compilación y un manifiesto resistente a la manipulación — de forma bit a bit reproducible desde las mismas fuentes en cualquier sistema conforme.

La necesidad forense de este módulo es directa: el estándar Daubert exige que las herramientas analíticas usadas en procedimientos legales tengan una procedencia demostrablemente confiable. Si el perito no puede probar que los binarios ejecutados son idénticos al código revisado y aprobado, la cadena de custodia está rota. Este módulo establece esa cadena. Actúa como punto de control de custodia entre la revisión de código y la ejecución en runtime, produciendo un bundle B = (A, M, σ) — un archivo tar determinista A, un manifiesto criptográfico M = [(p_i, h_i)], y una etiqueta de autenticación HMAC-SHA256 σ.

El módulo opera en cinco fases estrictamente ordenadas: (1) Canonicalización — recorrido lexicográfico independiente de locale, normalización de finales de línea, estandarización de permisos; (2) Generación del manifiesto — SHA-256 de cada archivo, ensamblado en M; (3) Construcción del archivo — tar POSIX determinista con metadatos fijos (uid=gid=0, mtime=0 o timestamp determinista del commit, formato UStar); (4) Vinculación criptográfica — HMAC-SHA256 sobre A∥M usando clave de VIGÍA.KeyOrchestrator; (5) Sellado del bundle — emisión de B con recibo de cadena de custodia en JSON-LD.

### Conceptos clave

| Concepto | Definición |
|---------|-----------|
| Canonicalización del árbol de fuentes | Recorrido lexicográfico sin dependencia de locale; finales de línea → LF; permisos → 0644/0755; atributos extendidos eliminados |
| Manifiesto M | Secuencia ordenada [(p_i, h_i)] donde h_i = SHA-256(s_i) y p_i es la ruta relativa canónica; ordenada lexicográficamente |
| Archivo A | tar POSIX.1-2001 determinista con campos de metadatos fijos (uid=gid=0, mtime=0 o timestamp del commit, formato UStar) |
| Bundle B | Triple ordenado (A, M, σ): el archivo, el manifiesto y la etiqueta de autenticación |
| HMAC-SHA256 σ | σ = HMAC(K_release, Serialize(A, M)); provee inforgeabilidad existencial ante ataques adaptativos de mensaje escogido |
| Probabilidad de colisión SHA-256 | ≈ 2^−256; esta es la tasa de error conocida que satisface el criterio Daubert |
| VIGÍA.KeyOrchestrator | Módulo que gestiona el ciclo de vida de la clave de firma; la clave privada nunca reside en memoria del proceso |
| Recibo de cadena de custodia | Registro JSON-LD que vincula σ, hash de A, hash de M, identidad del operador y LSN inmutable |
| NonDeterministicInputError | Excepción lanzada si el árbol de fuentes contiene archivos con orden no reproducible o metadatos inestables |

> **【Nota Científica】**
> La expresión "firma criptográfica" puede invocar una sensación de complejidad, pero la operación subyacente es análoga al sello de calibración de un instrumento de medición. El manifiesto M es el certificado de calibración que lista el valor medido de cada componente. La etiqueta HMAC σ es el sello que demuestra que el certificado fue emitido por un técnico autorizado con clave conocida. Si algún componente cambia después del sellado — aunque sea un bit — la verificación del sello falla. No es una verificación probabilística ni heurística: SHA-256 bajo la construcción Merkle-Damgård es una función determinista, y HMAC-SHA256 provee garantías de inforgeabilidad estandarizadas en FIPS 180-4 y FIPS 198-1. Peirce, Eco y Grice no son necesarios aquí — este módulo opera en el nivel de integridad de la capa física, por debajo de la capa semántica donde comienza el análisis de intencionalidad.

### Glosario

| Término | Definición |
|--------|-----------|
| generate_release_bundle.py | Módulo que sella el árbol de fuentes VIGÍA en un bundle de release reproducible y autenticado criptográficamente |
| canonicalización | Proceso de normalizar todos los archivos fuente a una representación determinista e independiente de la plataforma |
| manifiesto M | Lista ordenada de pares (ruta, hash SHA-256) que cubre cada archivo del release |
| archivo tar determinista | Stream tar POSIX con metadatos fijos para que árboles de fuentes idénticos produzcan archivos bit a bit idénticos |
| HMAC-SHA256 | Código de autenticación de mensajes basado en hash; demuestra autenticidad e integridad sin proveer confidencialidad |
| clave de firma K_release | Clave secreta gestionada por VIGÍA.KeyOrchestrator; usada para computar la etiqueta de autenticación σ del bundle |
| cadena de custodia | Registro documentado y verificable que vincula cada artefacto a su origen y todos los eventos de custodia posteriores |
| LSN (número de secuencia de log) | Identificador monótono de VIGÍA.AuditLogger que ancla cada evento de generación de bundle en la línea de tiempo de auditoría |
| HashMismatchException | Excepción lanzada cuando el hash del manifiesto recomputado no coincide con la copia interna del manifiesto en el archivo |

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## РУССКИЙ

### Что представляет собой этот модуль?

`generate_release_bundle.py` (хеш VIGÍA `ebd2829f`) — канонический механизм упаковки и заверения артефактов судебной платформы VIGÍA. Его назначение — генерировать криптографически подписанные пакеты выпуска, инкапсулирующие полное дерево исходного кода платформы, метаданные сборки и устойчивый к подделке манифест, причём делать это побитово воспроизводимым образом из одних и тех же исходных данных на любой совместимой системе.

Судебная необходимость этого модуля очевидна: стандарт Daubert требует, чтобы аналитические инструменты, используемые в судебных разбирательствах, имели доказуемо надёжное происхождение. Если эксперт не может доказать, что запущенные им бинарные файлы идентичны проверенному и утверждённому коду, цепочка хранения разрушена. Этот модуль устанавливает данную цепочку. Он выступает критически важным пунктом контроля цепочки хранения между проверкой кода и исполнением, производя пакет B = (A, M, σ) — детерминированный tar-архив A, криптографический манифест M = [(p_i, h_i)] и тег аутентификации HMAC-SHA256 σ.

Модуль работает в пяти строго упорядоченных фазах: (1) Канонизация — лексикографический обход без зависимости от локали, нормализация концов строк, стандартизация прав доступа; (2) Генерация манифеста — SHA-256 каждого файла, собранный в M; (3) Построение архива — детерминированный tar POSIX с фиксированными метаданными (uid=gid=0, mtime=0 или детерминированная метка коммита, формат UStar); (4) Криптографическая привязка — HMAC-SHA256 по A∥M с ключом из VIGÍA.KeyOrchestrator; (5) Упаковка — эмиссия B с квитанцией цепочки хранения в JSON-LD.

### Ключевые понятия

| Понятие | Определение |
|---------|------------|
| Канонизация дерева исходного кода | Лексикографический обход без зависимости от локали; концы строк → LF; права → 0644/0755; расширенные атрибуты удалены |
| Манифест M | Упорядоченная последовательность [(p_i, h_i)], где h_i = SHA-256(s_i), а p_i — канонический относительный путь; сортировка лексикографическая |
| Архив A | Детерминированный tar POSIX.1-2001 с фиксированными полями метаданных (uid=gid=0, mtime=0 или метка коммита, формат UStar) |
| Пакет B | Упорядоченный тройник (A, M, σ): архив, манифест и тег аутентификации |
| HMAC-SHA256 σ | σ = HMAC(K_release, Serialize(A, M)); обеспечивает экзистенциальную неподделываемость при адаптивных атаках с выбором сообщения |
| Вероятность коллизии SHA-256 | ≈ 2^−256; это известная частота ошибок, удовлетворяющая критерию Daubert |
| VIGÍA.KeyOrchestrator | Модуль, управляющий жизненным циклом ключа подписи; закрытый ключ никогда не находится в памяти процесса |
| Квитанция цепочки хранения | Запись JSON-LD, связывающая σ, хеш A, хеш M, идентификатор оператора и неизменяемый LSN |
| NonDeterministicInputError | Исключение при наличии в дереве исходного кода файлов с невоспроизводимым порядком или нестабильными метаданными |

> **【Научное примечание】**
> Выражение «криптографическая подпись» может казаться сложным, но лежащая в основе операция аналогична калибровочному пломбированию измерительного прибора. Манифест M — это калибровочный сертификат, перечисляющий измеренное значение каждого компонента. Тег HMAC σ — пломба, доказывающая, что сертификат был выдан уполномоченным техником с известным ключом. Если какой-либо компонент изменяется после пломбирования — хотя бы один бит — проверка пломбы завершается неудачей. Это не вероятностная и не эвристическая проверка: SHA-256 в конструкции Меркла-Дамгора является детерминированной функцией, а HMAC-SHA256 обеспечивает теоретически обоснованные гарантии неподделываемости, стандартизированные в FIPS 180-4 и FIPS 198-1. Пирс, Эко и Грайс здесь не нужны — этот модуль работает на уровне физической целостности, ниже семантического уровня, где начинается анализ интенциональности.

### Глоссарий

| Термин | Определение |
|--------|------------|
| generate_release_bundle.py | Модуль, запечатывающий дерево исходного кода VIGÍA в воспроизводимый, аутентифицированный пакет выпуска |
| канонизация | Процесс нормализации всех исходных файлов до детерминированного, платформо-независимого представления |
| манифест M | Упорядоченный список пар (путь, хеш SHA-256), охватывающий каждый файл релиза |
| детерминированный tar-архив | Поток tar POSIX с фиксированными метаданными; идентичные деревья исходного кода дают побитово идентичные архивы |
| HMAC-SHA256 | Код аутентификации сообщений на основе хеша; доказывает подлинность и целостность без обеспечения конфиденциальности |
| ключ подписи K_release | Секретный ключ, управляемый VIGÍA.KeyOrchestrator; используется для вычисления тега аутентификации σ |
| цепочка хранения | Документально подтверждённая, верифицируемая запись, связывающая каждый артефакт с его происхождением и всеми событиями хранения |
| LSN (порядковый номер журнала) | Монотонный идентификатор от VIGÍA.AuditLogger, привязывающий каждое событие генерации пакета к временной шкале аудита |
| HashMismatchException | Исключение при несовпадении пересчитанного хеша манифеста с внутренней копией манифеста в архиве |

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## 中文

### 本模块是什么？

`generate_release_bundle.py`（VIGÍA 哈希值 `ebd2829f`）是 VIGÍA 取证平台的规范化工件封装引擎。其目的是生成经密码学签名的发布包，完整封装平台源码树、构建时元数据以及防篡改的清单——并以比特级可复现的方式，从相同源输入在任何兼容系统上生成相同结果。

本模块的取证必要性直接明确：Daubert 标准要求用于法律程序的分析工具具备可证明的可靠来源。若检验员无法证明其运行的二进制文件与经过审查和批准的代码完全相同，保管链即告断裂。本模块建立这条链。它充当代码审查与运行时执行之间的关键保管节点，产生发布包 B = (A, M, σ)——确定性 tar 归档 A、密码学清单 M = [(p_i, h_i)] 以及 HMAC-SHA256 认证标签 σ。

模块严格按照五个阶段顺序运行：（1）规范化——无 locale 依赖的词典序遍历、行尾符规范化、权限标准化；（2）清单生成——对每个文件计算 SHA-256，组装为 M；（3）归档构建——具有固定元数据的确定性 POSIX tar（uid=gid=0，mtime=0 或确定性提交时间戳，UStar 格式）；（4）密码学绑定——使用来自 VIGÍA.KeyOrchestrator 的密钥对 A∥M 计算 HMAC-SHA256；（5）包封——输出 B 并附带 JSON-LD 格式保管链凭据。

### 关键概念

| 概念 | 定义 |
|------|------|
| 源码树规范化 | 无 locale 依赖的词典序遍历；行尾符 → LF；权限 → 0644/0755；剥离扩展属性 |
| 清单 M | 有序序列 [(p_i, h_i)]，其中 h_i = SHA-256(s_i)，p_i 为规范化相对路径；按词典序排列 |
| 归档 A | 具有固定元数据字段的确定性 POSIX.1-2001 tar（uid=gid=0，mtime=0 或提交时间戳，UStar 格式） |
| 发布包 B | 有序三元组 (A, M, σ)：归档、清单和认证标签 |
| HMAC-SHA256 σ | σ = HMAC(K_release, Serialize(A, M))；在自适应选择消息攻击下提供存在性不可伪造性 |
| SHA-256 碰撞概率 | ≈ 2^−256；这是满足 Daubert "已知错误率"标准的已知错误率 |
| VIGÍA.KeyOrchestrator | 管理签名密钥生命周期的模块；私钥材料从不驻留于进程内存 |
| 保管链凭据 | JSON-LD 记录，关联 σ、A 的哈希、M 的哈希、操作者身份及不可变日志序列号（LSN） |
| NonDeterministicInputError | 源码树包含顺序不可复现或元数据不稳定文件时抛出的异常 |

> **【科学说明】**
> "密码学签名"这一表述可能令人感觉复杂，但其底层操作类似于测量仪器的校准铅封。清单 M 是列出每个组件测量值的校准证书。HMAC 标签 σ 是证明证书由持有已知密钥的授权技术人员颁发的铅封。若封印后任何组件发生变化——哪怕一个比特——铅封验证即告失败。这不是概率性或启发式检验：Merkle-Damgård 构造下的 SHA-256 是确定性函数，HMAC-SHA256 提供 FIPS 180-4 和 FIPS 198-1 标准化的不可伪造性保证。皮尔斯、艾柯和格赖斯在此处不涉及——本模块在物理层完整性层面运行，低于意图性分析起始的语义层。

### 术语表

| 术语 | 定义 |
|------|------|
| generate_release_bundle.py | 将 VIGÍA 源码树封装为可复现、经密码学认证的发布包的模块 |
| 规范化 | 将所有源文件规范化为确定性、平台无关表示的过程 |
| 清单 M | 覆盖发布中每个文件的有序 (路径, SHA-256 哈希) 对列表 |
| 确定性 tar 归档 | 具有固定元数据的 POSIX tar 流；相同源码树产生比特级一致的归档 |
| HMAC-SHA256 | 基于哈希的消息认证码；在不提供保密性的情况下证明真实性和完整性 |
| 签名密钥 K_release | 由 VIGÍA.KeyOrchestrator 管理的密钥；用于计算包认证标签 σ |
| 保管链 | 将每个工件与其来源及所有后续保管事件相关联的有文档记录、可验证的记录 |
| LSN（日志序列号） | 来自 VIGÍA.AuditLogger 的单调标识符，将每次包生成事件锚定至审计时间线 |
| HashMismatchException | 重新计算的清单哈希与归档内部清单副本不匹配时抛出的异常 |

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
