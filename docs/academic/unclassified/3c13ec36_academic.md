<!--
VIGIA Academic Documentation
Module: 3c13ec36
Batch ID: vigia-doc-0087-3c13ec36
Generated: 2026-05-20T14:56:47.863321+00:00
-->

## ENGLISH

### What Is This Module?
This module provides cryptographic timestamping and receipt generation for the VIGÍA forensic framework. It proves, in a legally verifiable manner, that a given evidence bundle existed at a specific point in time. Think of it as a notarial office for digital evidence: just as a notary seals a document with a date stamp that cannot be backdated, this module contacts an external Time-Stamping Authority (TSA) and obtains a cryptographically signed receipt. Where hardware security is required, it interfaces with a Hardware Security Module (HSM) via the PKCS#11 standard, ensuring that private keys never leave the secure hardware. All internal identifiers and counters use exact integer arithmetic.

### Key Concepts

| Component | Role | Analogy |
|---|---|---|
| **ReceiptProof** | Cryptographic artifact proving that a `bundle_hash` existed at a given timestamp. | A sealed envelope with a notarized postmark. |
| **TimestampClient** | Requests a timestamp token from an external TSA over a standard protocol. | A clerk sending a document to a certified notary. |
| **HSMConnector** | Interfaces with hardware security tokens via the PKCS#11 standard. | A key turning in a certified safe that records each opening. |
| **bundle_hash** | A SHA-256 integer digest of the evidence bundle. Serves as the immutable identifier. | The unique fingerprint of a sealed evidence bag. |
| **TSA (Time-Stamping Authority)** | A trusted third-party service that produces a signed timestamp token. | An official clock synchronized to a national time standard. |
| **PKCS#11** | A platform-independent standard API for cryptographic hardware tokens. | The standardized socket interface for connecting to a secure vault. |
| **Timestamp Token** | A cryptographically signed assertion that a specific hash existed at a specific moment. | A court-admissible certificate of existence. |

### Glossary

| Term | Definition |
|---|---|
| **SHA-256** | A deterministic hash function producing a 256-bit (32-byte) integer digest. Identical inputs always produce the identical digest; any change to the input produces a completely different digest. |
| **PKCS#11** | Public-Key Cryptography Standards #11. An interface specification for cryptographic tokens that allows software to use hardware keys without ever exposing the key material. |
| **HSM (Hardware Security Module)** | A physical device that generates, stores, and uses cryptographic keys in a tamper-resistant enclosure. |
| **Chain of Custody** | The chronological documentation proving that evidence has remained unaltered from collection to presentation. |
| **Bundle Hash** | A single integer digest representing the complete evidence bundle. Used as the input to the timestamping process. |
| **Timestamp Token** | The signed response from a TSA, binding a hash value to a point in time in a legally auditable format. |
| **Deterministic Integer Arithmetic** | All internal counters, sequence numbers, and identifiers in this module are whole numbers, ensuring reproducibility and auditability across platforms. |

> **【Scientific Note】**
> The vocabulary of *sign*, *interpretant*, and *chain of provenance* used in VIGÍA documentation derives from the formal semiotic traditions of Charles Sanders Peirce, Umberto Eco, and H. P. Grice. These are not mystical terms. A cryptographic timestamp is a perfect engineering instantiation of Peircean sign theory: the `bundle_hash` (the sign) points to the evidence bundle (the object), and the TSA's signed token (the interpretant) fixes the meaning at a specific point in time. Eco's codes define how that token is parsed and verified; Grice's cooperative maxims describe the communication protocol between client and TSA. Treat these frameworks as calibration standards—formal protocols that eliminate ambiguity, exactly as a calibrated atomic clock eliminates ambiguity about time.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## ESPAÑOL

### ¿Qué es este módulo?
Este módulo proporciona marcas de tiempo criptográficas y generación de recibos para el marco forense VIGÍA. Demuestra, de forma legalmente verificable, que un paquete de evidencia determinado existía en un momento específico. Piénselo como una notaría para evidencia digital: al igual que un notario sella un documento con una fecha que no puede retroactarse, este módulo contacta una Autoridad de Sellado de Tiempo (TSA) externa y obtiene un recibo firmado criptográficamente. Cuando se requiere seguridad de hardware, se comunica con un Módulo de Seguridad de Hardware (HSM) a través del estándar PKCS#11, garantizando que las claves privadas nunca abandonen el hardware seguro. Todos los identificadores y contadores internos usan aritmética entera exacta.

### Conceptos Clave

| Componente | Rol | Analogía |
|---|---|---|
| **ReceiptProof** | Artefacto criptográfico que prueba que un `bundle_hash` existía en una marca de tiempo dada. | Un sobre sellado con sello notarial. |
| **TimestampClient** | Solicita un token de marca de tiempo de una TSA externa mediante un protocolo estándar. | Un empleado que envía un documento a un notario certificado. |
| **HSMConnector** | Se comunica con tokens de seguridad de hardware a través del estándar PKCS#11. | Una llave que gira en una caja fuerte certificada que registra cada apertura. |
| **bundle_hash** | Un resumen entero SHA-256 del paquete de evidencia. Sirve como identificador inmutable. | La huella dactilar única de una bolsa de evidencia sellada. |
| **TSA (Autoridad de Sellado de Tiempo)** | Servicio de terceros de confianza que produce un token de marca de tiempo firmado. | Un reloj oficial sincronizado con el estándar de tiempo nacional. |
| **PKCS#11** | API estándar independiente de plataforma para tokens de hardware criptográfico. | La interfaz de enchufe estandarizada para conectarse a una bóveda segura. |
| **Token de Marca de Tiempo** | Afirmación firmada criptográficamente de que un hash específico existía en un momento específico. | Un certificado de existencia admisible en tribunal. |

### Glosario

| Término | Definición |
|---|---|
| **SHA-256** | Función de hash determinista que produce un resumen entero de 256 bits (32 bytes). Entradas idénticas siempre producen el mismo resumen; cualquier cambio en la entrada produce un resumen completamente diferente. |
| **PKCS#11** | Public-Key Cryptography Standards #11. Especificación de interfaz para tokens criptográficos que permite al software usar claves de hardware sin exponer nunca el material clave. |
| **HSM (Módulo de Seguridad de Hardware)** | Dispositivo físico que genera, almacena y usa claves criptográficas en un recinto resistente a manipulaciones. |
| **Cadena de Custodia** | Documentación cronológica que prueba que la evidencia ha permanecido sin alterar desde la recolección hasta la presentación. |
| **Hash del Paquete** | Un único resumen entero que representa el paquete completo de evidencia. Usado como entrada al proceso de sellado de tiempo. |
| **Token de Marca de Tiempo** | La respuesta firmada de una TSA, vinculando un valor hash a un punto en el tiempo en formato legalmente auditable. |
| **Aritmética Entera Determinista** | Todos los contadores internos, números de secuencia e identificadores de este módulo son números enteros, garantizando reproducibilidad y auditabilidad entre plataformas. |

> **【Nota Científica】**
> El vocabulario de *signo*, *interpretante* y *cadena de procedencia* utilizado en la documentación de VIGÍA proviene de las tradiciones semióticas formales de Charles Sanders Peirce, Umberto Eco y H. P. Grice. No son términos místicos. Una marca de tiempo criptográfica es una instanciación perfecta en ingeniería de la teoría semiótica de Peirce: el `bundle_hash` (el signo) apunta al paquete de evidencia (el objeto), y el token firmado de la TSA (el interpretante) fija el significado en un punto específico en el tiempo. Los códigos de Eco definen cómo se analiza y verifica ese token; las máximas cooperativas de Grice describen el protocolo de comunicación entre cliente y TSA. Trate estos marcos como estándares de calibración—protocolos formales que eliminan la ambigüedad, exactamente como un reloj atómico calibrado elimina la ambigüedad sobre el tiempo.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## РУССКИЙ

### Что это за модуль?
Этот модуль обеспечивает криптографическое отметку времени и генерацию квитанций для судебно-экспертного комплекса VIGÍA. Он доказывает юридически проверяемым способом, что данный пакет доказательств существовал в конкретный момент времени. Думайте о нём как о нотариальной конторе для цифровых доказательств: подобно тому как нотариус заверяет документ датированной печатью, которую нельзя задним числом изменить, этот модуль обращается к внешнему Центру Временны́х Меток (TSA) и получает криптографически подписанную квитанцию. Когда требуется аппаратная защита, модуль взаимодействует с Аппаратным Модулем Безопасности (HSM) через стандарт PKCS#11, гарантируя, что закрытые ключи никогда не покидают защищённое оборудование. Все внутренние идентификаторы и счётчики используют точную целочисленную арифметику.

### Ключевые концепции

| Компонент | Роль | Аналогия |
|---|---|---|
| **ReceiptProof** | Криптографический артефакт, доказывающий, что `bundle_hash` существовал в заданный момент времени. | Запечатанный конверт с нотариально заверенным штемпелем. |
| **TimestampClient** | Запрашивает токен временно́й метки у внешнего TSA по стандартному протоколу. | Клерк, отправляющий документ к сертифицированному нотариусу. |
| **HSMConnector** | Взаимодействует с аппаратными криптографическими токенами через стандарт PKCS#11. | Ключ, поворачивающийся в сертифицированном сейфе, фиксирующем каждое открытие. |
| **bundle_hash** | SHA-256 целочисленный дайджест пакета доказательств. Служит неизменяемым идентификатором. | Уникальный отпечаток запечатанного мешка с уликами. |
| **TSA (Центр Временны́х Меток)** | Доверенный сторонний сервис, выдающий подписанный токен временно́й метки. | Официальные часы, синхронизированные с государственным стандартом времени. |
| **PKCS#11** | Платформонезависимый стандартный API для аппаратных криптографических токенов. | Стандартизированный разъём для подключения к защищённому хранилищу. |
| **Токен Временно́й Метки** | Криптографически подписанное утверждение, что конкретный хэш существовал в конкретный момент. | Юридически значимый сертификат существования. |

### Глоссарий

| Термин | Определение |
|---|---|
| **SHA-256** | Детерминированная хэш-функция, производящая 256-битный (32-байтный) целочисленный дайджест. Идентичные входные данные всегда производят идентичный дайджест; любое изменение входа порождает совершенно иной дайджест. |
| **PKCS#11** | Public-Key Cryptography Standards #11. Спецификация интерфейса для криптографических токенов, позволяющая программному обеспечению использовать аппаратные ключи без раскрытия ключевого материала. |
| **HSM (Аппаратный Модуль Безопасности)** | Физическое устройство, генерирующее, хранящее и использующее криптографические ключи в устойчивом к вскрытию корпусе. |
| **Цепочка Хранения** | Хронологическая документация, доказывающая, что доказательства оставались неизменёнными от сбора до представления. |
| **Хэш Пакета** | Единый целочисленный дайджест, представляющий полный пакет доказательств. Используется как входные данные для процесса временно́й метки. |
| **Токен Временно́й Метки** | Подписанный ответ TSA, связывающий хэш-значение с точкой во времени в юридически аудируемом формате. |
| **Детерминированная Целочисленная Арифметика** | Все внутренние счётчики, порядковые номера и идентификаторы данного модуля являются целыми числами, обеспечивая воспроизводимость и аудируемость на всех платформах. |

> **【Научное примечание】**
> Словарь *знак*, *интерпретант* и *цепочка происхождения*, используемый в документации VIGÍA, происходит из формальных семиотических традиций Чарльза Сандерса Пирса, Умберто Эко и Г. П. Грайса. Это не мистические термины. Криптографическая временна́я метка — это совершенное инженерное воплощение теории знаков Пирса: `bundle_hash` (знак) указывает на пакет доказательств (объект), а подписанный токен TSA (интерпретант) фиксирует значение в конкретной точке времени. Коды Эко определяют, как этот токен анализируется и верифицируется; кооперативные максимы Грайса описывают протокол коммуникации между клиентом и TSA. Относитесь к этим рамкам как к калибровочным стандартам — формальным протоколам, устраняющим неопределённость, подобно тому как калиброванные атомные часы устраняют неопределённость времени.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## 中文

### 这是什么模块？
本模块为 VIGÍA 取证框架提供密码学时间戳和收据生成功能。它以法律上可验证的方式证明，特定证据包在某一时刻确实存在。请将其想象为数字证据的公证处：正如公证人以无法倒签的日期印章封存文件，本模块联系外部时间戳机构（TSA）并获得经密码学签名的收据。当需要硬件安全保障时，它通过 PKCS#11 标准与硬件安全模块（HSM）交互，确保私钥永远不会离开安全硬件。所有内部标识符和计数器均使用精确的整数运算。

### 核心概念

| 组件 | 角色 | 类比 |
|---|---|---|
| **ReceiptProof** | 证明特定 `bundle_hash` 在给定时间戳存在的密码学取证工件。 | 带有公证邮戳的密封信封。 |
| **TimestampClient** | 通过标准协议向外部 TSA 请求时间戳令牌。 | 将文件发送给认证公证人的书记员。 |
| **HSMConnector** | 通过 PKCS#11 标准与硬件安全令牌交互。 | 在记录每次开启的认证保险箱中转动的钥匙。 |
| **bundle_hash** | 证据包的 SHA-256 整数摘要。用作不可变标识符。 | 密封证据袋的唯一指纹。 |
| **TSA（时间戳机构）** | 生成签名时间戳令牌的可信第三方服务。 | 与国家时间标准同步的官方时钟。 |
| **PKCS#11** | 用于密码学硬件令牌的平台无关标准 API。 | 连接安全保险库的标准化接口插座。 |
| **时间戳令牌** | 经密码学签名的断言，证明特定哈希在特定时刻存在。 | 可被法庭采纳的存在证明证书。 |

### 词汇表

| 术语 | 定义 |
|---|---|
| **SHA-256** | 产生 256 位（32 字节）整数摘要的确定性哈希函数。相同输入始终产生相同摘要；输入的任何变化都会产生完全不同的摘要。 |
| **PKCS#11** | 公钥密码学标准第 11 号。密码学令牌的接口规范，允许软件使用硬件密钥而无需暴露密钥材料。 |
| **HSM（硬件安全模块）** | 在防篡改外壳中生成、存储和使用密码学密钥的物理设备。 |
| **监管链** | 证明证据从采集到呈堂过程中保持原封不动的时间顺序记录。 |
| **证据包哈希** | 代表完整证据包的单一整数摘要。用作时间戳流程的输入。 |
| **时间戳令牌** | TSA 的签名响应，以法律可审计格式将哈希值与某一时间点绑定。 |
| **确定性整数运算** | 本模块中所有内部计数器、序列号和标识符均为整数，确保跨平台的可复现性和可审计性。 |

> **【科学说明】**
> VIGÍA 文档中使用的"符号"、"解释项"和"溯源链"等词汇，源自查尔斯·桑德斯·皮尔士、**艾柯**（Umberto Eco）和**格赖斯**（H. P. Grice）的形式化符号学传统。这些并非神秘术语。密码学时间戳是皮尔士符号理论的完美工程实例：`bundle_hash`（符号）指向证据包（对象），而 TSA 的签名令牌（解释项）在特定时间点固定了意义。艾柯的编码定义了如何解析和验证该令牌；格赖斯的合作准则描述了客户端与 TSA 之间的通信协议。请将这些框架视为校准标准——消除歧义的形式化协议，正如校准原子钟消除时间歧义一样。

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
