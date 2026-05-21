<!--
VIGIA Academic Documentation
Module: 3c13ec36
Batch ID: vigia-doc-0087-3c13ec36
Generated: 2026-05-20T14:56:47.863321+00:00
-->

The user wants academic technical documentation for a Python module `vigia/forensics/pki_tools.py`. The target audience is scientists/researchers who do NOT know Python. Requirements:

1. Markdown format with 4 language sections: ENGLISH, ESPAÑOL, РУССКИЙ, 中文.
2. Each section must include:
   - "What Is This Module?" (plain language explanation)
   - Key concepts with tables
   - A glossary of technical terms
   - A 【科学说明】/【Scientific Note】 box explaining that Peirce/Eco/Grice terminology is NOT mysticism — use the sensor analogy
3. Chinese translations must use: 艾柯 (not Eco), 格赖斯 (not Grice), 取证工件 (not 制品), 逻辑断裂 (not 裂缝).
4. 
5. Do NOT use floating-point math explanations — emphasize deterministic integer arithmetic where applicable.
6. The module is about PKI Tools for forensic suite. Components: TimestampClient, HSMConnector, ReceiptProof. Standards: RFC 3161, PKCS#11, ETSI EN 319 102, eIDAS. Zero-trust architecture. Classes and functions described in the prompt.

Important constraints:
- Never use floating-point math explanations for deterministic systems.
- The scientific note must clarify Peirce/Eco/Grice terminology is not mysticism, using sensor analogy.
- Must be thorough but concise.
- Since the audience doesn't know Python, avoid Python-specific jargon or explain it in plain terms. But since it's documentation for a module, we can describe the functionality without assuming they can code.

Let's structure each language section similarly.

First, let's outline the content:

**Header/Module Info:**
- Path: `vigia/forensics/pki_tools.py`
- License line at the end.

**For each language:**

1. **What Is This Module?**
   - Plain language: This module is part of the VIGIA Forensic Suite. It provides tools to cryptographically prove that a digital evidence bundle existed at a specific time (timestamping) and to digitally sign it using hardware security modules (HSM). It ensures the integrity and non-repudiation of forensic artifacts. It acts like a laboratory sealing machine and notary for digital data.

2. **Key Concepts with Tables**
   - Table 1: Components/Classes (ReceiptProof, TimestampClient, HSMConnector, PKIRecord)
   - Table 2: Standards Implemented (RFC 3161, PKCS#11, ETSI EN 319 102, eIDAS)
   - Table 3: Workflow / Functions (stamp_and_sign, stamp, stamp_multiple, connect, sign, disconnect, etc.)
   - Table 4: Security Principles (Zero-Trust, Private key never leaves HSM, External TSA, Deterministic integer arithmetic for hashes)

   Need to emphasize deterministic integer arithmetic: SHA-256 operates on integer representations, no floating point. All cryptographic operations are deterministic integer arithmetic.

3. **Glossary of Technical Terms**
   - Bundle hash: SHA-256 fingerprint of evidence.
   - TSA (Time Stamping Authority): Trusted third party that issues timestamps.
   - HSM (Hardware Security Module): Physical device safeguarding private keys.
   - PKCS#11: Standard API for cryptographic tokens.
   - RFC 3161: Protocol for timestamps.
   - ReceiptProof: Sealed artifact proving timestamp.
   - PKIRecord: Complete PKI registry.
   - Zero-Trust: Architecture assuming no implicit trust.
   - Deterministic integer arithmetic: Operations on exact whole numbers without rounding errors (relevant to hashing and signatures).

4. **【Scientific Note】/【Nota Científica】/【Научное примечание】/【科学说明】**
   - Must mention Peirce, Eco (艾柯), Grice (格赖斯).
   - Explain that their terminology (sign, semiotics, implicature) is not mysticism.
   - Sensor analogy: Just as a sensor transduces physical phenomena into measurable signals, semiotics provides a formal framework to analyze how signs convey meaning. In forensics, a digital signature is a sign (Peirce) that communicates intent non-repudiably;艾柯's codes describe how protocols like RFC 3161 encode trust;格赖斯's maxims explain why protocols must be cooperative and unambiguous to be valid evidence. This is a formal analytical lens, not occultism.

5. **License line**

Now, let's draft each section carefully.

**ENGLISH:**

What Is This Module?
- The `pki_tools.py` module is the digital notary and seal laboratory of the VIGIA Forensic Suite. It allows investigators to prove that a collection of digital evidence (a "bundle") existed in an exact state at an exact moment in time, and to bind that proof to a legally recognized digital signature. It does this without ever exposing private keys, using hardware security devices and external trusted time authorities. Think of it as an evidence-locking vault that also receives an official date stamp from a government clock and a signature from a tamper-proof pen.

Key Concepts:
Table 1: Core Components
| Component | Role | Analogy |
|---|---|---|
| ReceiptProof | Cryptographic artifact proving a bundle_hash existed at a given time | A sealed envelope with a postmark |
| TimestampClient | Requests timestamps from an external TSA | A clerk sending a document to a notary |
| HSMConnector | Interfaces with hardware tokens via PKCS#11 | A key turning in a safe that never leaves the vault |
| PKIRecord | Full registry: timestamp(s) + HSM signature + metadata | The complete notarized file folder |

Table 2: Standards & Compliance
| Standard | Function | Forensic Relevance |
|---|---|---|
| RFC 3161 | Time-Stamp Protocol (TSP) | Provides auditable, independent time attestation |
| PKCS#11 | Cryptographic Token Interface | Ensures private keys remain inside hardware |
| ETSI EN 319 102 | PAdES baseline profiles | European framework for advanced signatures |
| eIDAS | Qualified Electronic Signatures | Legal equivalence to handwritten signatures in the EU |

Table 3: Primary Operations
| Operation | Input | Output | Deterministic Guarantee |
|---|---|---|---|
| stamp() | SHA-256 bundle hash (64 hex chars) | RFC 3161 token | Exact integer hash, no approximation |
| stamp_multiple() | Same hash, multiple TSAs | List of independent proofs | Redundant jurisdictional evidence |
| sign() | bundle_hash + HSM key label | HSMSignature object | Private key never exported; integer arithmetic only |
| stamp_and_sign() | bundle_hash, HSM config | PKIRecord | End-to-end sealed record |
| connect() / disconnect() | Slot number, PIN | Session handle | Hardware-bound session |

Table 4: Zero-Trust Security Principles
| Principle | Implementation |
|---|---|
| Key Custody | Private key remains in HSM/token at all times |
| Temporal Trust | Timestamp produced by independent external TSA |
| Verification Chain | ReceiptProof includes full verification chain |
| Arithmetic Integrity | All hashes and signatures use deterministic integer arithmetic; no floating-point operations |

Glossary:
- **Bundle hash**: A 64-character hexadecimal string representing the SHA-256 fingerprint of a digital evidence bundle. It is computed using deterministic integer arithmetic over the exact byte content.
- **Deterministic integer arithmetic**: Mathematical operations performed on whole numbers without rounding, approximation, or floating-point error. Cryptographic hashing and signing rely entirely on this to ensure identical inputs always produce identical outputs.
- **HSM (Hardware Security Module)**: A physical computing device that safeguards and manages digital keys.
- **PKCS#11**: A standard programming interface allowing applications to use cryptographic hardware without knowing its internals.
- **ReceiptProof**: A sealed forensic artifact that demonstrates a specific hash existed at a specific time.
- **RFC 3161**: The Internet standard protocol for requesting and verifying timestamps from a Time Stamping Authority.
- **TSA (Time Stamping Authority)**: A trusted third party that issues cryptographically secure timestamps.
- **Zero-Trust architecture**: A security model that assumes no user or system is trustworthy by default and requires continuous verification.

【Scientific Note】
The VIGIA suite occasionally employs concepts derived from Charles Sanders Peirce (semiotics), Umberto Eco, and H.P. Grice. These are not mystical or esoteric doctrines. They constitute a formal analytical framework—analogous to how a physicist uses sensor theory. Peirce’s theory of signs provides a grammar for how a digital signature functions as a signifier bound to an identity. Eco’s codes describe how protocols like RFC 3161 encode trust relationships through conventional rules, just as a sensor encodes physical phenomena into digital signals. Grice’s cooperative principles explain why communication protocols must be maximally truthful, relevant, and unambiguous to be admissible as evidence. Semiotics here is a methodological sensor: it transduces social and logical relationships into inspectable, testable structures. There is nothing supernatural about it; it is a rigorous epistemological tool.



**ESPAÑOL:**

¿Qué es este módulo?
- El módulo `pki_tools.py` es el laboratorio de sellado digital y notaría forense de la Suite VIGIA. Permite a los investigadores demostrar que un conjunto de pruebas digitales (un "bundle") existió en un estado exacto en un momento exacto, vinculando esa prueba a una firma digital reconocida legalmente. Lo hace sin exponer nunca las claves privadas, utilizando dispositivos de seguridad de hardware y autoridades de tiempo externas de confianza. Piense en ello como una cámara acorazada para evidencias que también recibe un sello de fecha oficial de un reloj gubernamental y una firma de un bolígrafo a prueba de manipulaciones.

Conceptos Clave:
Tabla 1: Componentes Principales
| Componente | Función | Analogía |
|---|---|---|
| ReceiptProof | Artefacto criptográfico que prueba que un bundle_hash existió en un momento dado | Sobre sellado con matasellos |
| TimestampClient | Solicita timestamps a una TSA externa | Escribano que envía un documento a notaría |
| HSMConnector | Interfaz con tokens hardware mediante PKCS#11 | Llave que gira en una caja fuerte sin salir de ella |
| PKIRecord | Registro completo: timestamp(s) + firma HSM + metadatos | Expediente notarial completo |

Tabla 2: Normas y Cumplimiento
| Norma | Función | Relevancia Forense |
|---|---|---|
| RFC 3161 | Protocolo de sellado de tiempo (TSP) | Atestación temporal independiente y auditable |
| PKCS#11 | Interfaz de token criptográfico | Garantiza que la clave privada permanezca en el hardware |
| ETSI EN 319 102 | Perfiles baseline PAdES | Marco europeo para firmas avanzadas |
| eIDAS | Firmas electrónicas cualificadas | Equivalencia legal con firma manuscrita en la UE |

Tabla 3: Operaciones Primarias
| Operación | Entrada | Salida | Garantía Determinista |
|---|---|---|---|
| stamp() | Hash SHA-256 del bundle (64 hex) | Token RFC 3161 | Hash entero exacto, sin aproximación |
| stamp_multiple() | Mismo hash, múltiples TSAs | Lista de pruebas independientes | Evidencia jurisdiccional redundante |
| sign() | bundle_hash + etiqueta de clave HSM | Objeto HSMSignature | Clave privada nunca exportada; solo aritmética entera |
| stamp_and_sign() | bundle_hash, config HSM | PKIRecord | Registro sellado de extremo a extremo |
| connect() / disconnect() | Número de slot, PIN | Manejador de sesión | Sesión vinculada al hardware |

Tabla 4: Principios de Seguridad Zero-Trust
| Principio | Implementación |
|---|---|
| Custodia de Claves | La clave privada permanece siempre en el HSM/token |
| Confianza Temporal | El timestamp es producido por una TSA externa independiente |
| Cadena de Verificación | ReceiptProof incluye la cadena completa de verificación |
| Integridad Aritmética | Todos los hashes y firmas usan aritmética entera determinista; sin operaciones de punto flotante |

Glosario:
- **Aritmética entera determinista**: Operaciones matemáticas sobre números enteros sin redondeo, aproximación ni error de punto flotante. El hashing y la firma criptográfica dependen enteramente de esto para garantizar que entradas idénticas produzcan salidas idénticas.
- **Bundle hash**: Cadena hexadecimal de 64 caracteres que representa la huella SHA-256 de un conjunto de evidencia digital. Se calcula mediante aritmética entera determinista sobre el contenido exacto de bytes.
- **HSM (Hardware Security Module)**: Dispositivo físico que protege y gestiona claves digitales.
- **PKCS#11**: Interfaz estándar que permite a las aplicaciones utilizar hardware criptográfico sin conocer sus detalles internos.
- **ReceiptProof**: Artefacto forense sellado que demuestra que un hash específico existió en un momento específico.
- **RFC 3161**: El estándar de Internet para solicitar y verificar timestamps ante una Autoridad de Sellado de Tiempo.
- **TSA (Time Stamping Authority)**: Tercero de confianza que emite timestamps criptográficamente seguros.
- **Arquitectura Zero-Trust**: Modelo de seguridad que no otorga confianza implícita a ningún usuario o sistema y exige verificación continua.

【Nota Científica】
La suite VIGIA emplea ocasionalmente conceptos derivados de Charles Sanders Peirce (semiótica), Umberto Eco y H.P. Grice. Estas no son doctrinas místicas ni esotéricas. Constituyen un marco analítico formal, análogo a cómo un físico utiliza la teoría de sensores. La teoría de los signos de Peirce proporciona una gramática para entender cómo una firma digital funciona como significante vinculado a una identidad. Los códigos de Eco describen cómo protocolos como RFC 3161 codifican relaciones de confianza mediante reglas convencionales, así como un sensor codifica fenómenos físicos en señales digitales. Los principios cooperativos de Grice explican por qué los protocolos de comunicación deben ser maximamente veraces, relevantes y inequívocos para ser admisibles como evidencia. La semiótica aquí es un sensor metodológico: transduce relaciones sociales y lógicas en estructuras inspeccionables y comprobables. No hay nada sobrenatural en ello; es una herramienta epistemológica rigurosa.

Licenciado bajo GNU AGPL v3. Copyright © 2026 Anna Tchijova.

**РУССКИЙ:**

Что это за модуль?
- Модуль `pki_tools.py` — это цифровая нотариальная контора и лаборатория пломбирования судебно-медицинского комплекса VIGIA. Он позволяет исследователям доказать, что набор цифровых доказательств («связка») существовал в точном состоянии в точный момент времени, и привязать это доказательство к юридически значимой цифровой подписи. Это достигается без раскрытия закрытых ключей, с использованием аппаратных средств безопасности и внешних доверенных центров сертификации времени. Представьте это как сейф для улик, который также получает официальную датировку от государственных часов и подпись от невскрываемой ручки.

Ключевые концепции:
Таблица 1: Основные компоненты
| Компонент | Роль | Аналогия |
|---|---|---|
| ReceiptProof | Криптографический артефакт, доказывающий существование bundle_hash в заданный момент | Запечатанный конверт с почтовым штемпелем |
| TimestampClient | Запрашивает метки времени у внешнего TSA | Клерк, отправляющий документ нотариусу |
| HSMConnector | Интерфейс с аппаратными токенами через PKCS#11 | Ключ, поворачивающийся в сейфе, но не покидающий его |
| PKIRecord | Полный реестр: метка(и) времени + подпись HSM + метаданные | Полная нотариальная папка |

Таблица 2: Стандарты и соответствие
| Стандарт | Функция | Судебная значимость |
|---|---|---|
| RFC 3161 | Протокол меток времени (TSP) | Независимая, поддающаяся аудиту временная аттестация |
| PKCS#11 | Интерфейс криптографического токена | Гарантирует, что закрытый ключ остаётся внутри устройства |
| ETSI EN 319 102 | Базовые профили PAdES | Европейская основа для усовершенствованных подписей |
| eIDAS | Квалифицированные электронные подписи | Правовое равенство рукописной подписи в ЕС |

Таблица 3: Основные операции
| Операция | Входные данные | Выходные данные | Детерминистская гарантия |
|---|---|---|---|
| stamp() | SHA-256 хеш связки (64 шестнадцатеричных символа) | Токен RFC 3161 | Точное целочисленное хеширование, без аппроксимации |
| stamp_multiple() | Тот же хеш, несколько TSA | Список независимых доказательств | Избыточная юрисдикционная доказательственная база |
| sign() | bundle_hash + метка ключа HSM | Объект HSMSignature | Закрытый ключ никогда не экспортируется; только целочисленная арифметика |
| stamp_and_sign() | bundle_hash, конфигурация HSM | PKIRecord | Сквозной запечатанный реестр |
| connect() / disconnect() | Номер слота, PIN | Дескриптор сессии | Сессия, привязанная к оборудованию |

Таблица 4: Принципы безопасности Zero-Trust
| Принцип | Реализация |
|---|---|
| Хранение ключей | Закрытый ключ находится в HSM/токене постоянно |
| Временное доверие | Метка времени выдаётся независимым внешним TSA |
| Цепочка проверки | ReceiptProof включает полную цепочку верификации |
| Арифметическая целостность | Все хеши и подписи используют детерминистскую целочисленную арифметику; без операций с плавающей точкой |

Глоссарий:
- **Bundle hash**: 64-символьная шестнадцатеричная строка, представляющая отпечаток SHA-256 цифрового набора доказательств. Вычисляется с помощью детерминистской целочисленной арифметики по точному содержимому байтов.
- **Детерминистская целочисленная арифметика**: Математические операции над целыми числами без округления, аппроксимации или ошибок плавающей точки. Криптографическое хеширование и подписание полностью полагаются на неё, чтобы одинаковые входные данные всегда давали одинаковый результат.
- **HSM (Hardware Security Module)**: Физическое устройство для защиты и управления цифровыми ключами.
- **PKCS#11**: Стандартный программный интерфейс, позволяющий приложениям использовать криптографическое оборудование, не зная его внутреннего устройства.
- **ReceiptProof**: Запечатанный судебный артефакт, демонстрирующий, что конкретный хеш существовал в конкретный момент времени.
- **RFC 3161**: Интернет-стандарт протокола запроса и проверки меток времени у Центра Серверации Времени (TSA).
- **TSA (Time Stamping Authority)**: Доверенная третья сторона, выдающая криптографически защищённые метки времени.
- **Архитектура Zero-Trust**: Модель безопасности, предполагающая отсутствие неявного доверия к любому пользователю или системе и требующая непрерывной верификации.

【Научное примечание】
В комплексе VIGIA время от времени используются концепции, восходящие к Чарльзу Сандерсу Пирсу (семиотика), Умберто Эко и Х.П. Грайсу. Это не мистические или эзотерические учения. Они составляют формальный аналитический каркас — аналогично тому, как физик использует теорию сенсоров. Теория знаков Пирса даёт грамматику для понимания того, как цифровая подпись функционирует как означающее, связанное с идентичностью. Коды Эко описывают, как протоколы вроде RFC 3161 кодируют доверительные отношения посредством условных правил, точно так же, как сенсор кодирует физические явления в цифровые сигналы. Кооперативные принципы Грайса объясняют, почему коммуникационные протоколы должны быть максимально правдивыми, релевантными и однозначными, чтобы быть допустимыми в качестве доказательств. Семиотика здесь выступает методологическим сенсором: она трансдуцирует социальные и логические отношения в инспектируемые, проверяемые структуры. В этом нет ничего сверхъестественного; это строгий эпистемологический инструмент.

Лицензия: GNU AGPL v3. Copyright © 2026 Anna Tchijova.

**中文:**

这是什么模块？
- `pki_tools.py` 模块是 VIGIA 取证套件的数字公证与封装实验室。它使调查人员能够证明一组数字证据（“取证工件包”）在某一精确时刻以精确状态存在，并将该证明与具有法律效力的数字签名绑定。它在整个过程中不暴露私钥，利用硬件安全设备和外部可信时间机构完成。可将其视为一个证据保险库，同时从政府时钟获得官方日期戳，并使用一支防篡改的笔签名。

关键概念：
表1：核心组件
| 组件 | 作用 | 类比 |
|---|---|---|
| ReceiptProof | 加密证明，证明某 bundle_hash 在特定时间点存在 | 盖有邮戳的密封信封 |
| TimestampClient | 向外部 TSA 请求时间戳 | 将文件送交公证处的文员 |
| HSMConnector | 通过 PKCS#11 与硬件令牌交互 | 在保险箱内转动、永不离开的钥匙 |
| PKIRecord | 完整登记：时间戳 + HSM 签名 + 元数据 | 完整的公证卷宗 |

表2：实施标准与合规性
| 标准 | 功能 | 取证相关性 |
|---|---|---|
| RFC 3161 | 时间戳协议（TSP） | 提供可审计的独立时间认证 |
| PKCS#11 | 加密令牌接口 | 确保私钥始终留存于硬件内部 |
| ETSI EN 319 102 | PAdES 基线配置文件 | 欧洲高级签名框架 |
| eIDAS | 合格电子签名 | 在欧盟具有与手写签名同等法律效力 |

表3：主要操作
| 操作 | 输入 | 输出 | 确定性保证 |
|---|---|---|---|
| stamp() | 取证工件包的 SHA-256 哈希（64 位十六进制字符） | RFC 3161 令牌 | 精确整数哈希，无近似 |
| stamp_multiple() | 同一哈希，多个 TSA | 多份独立证明 | 跨司法管辖区的冗余证据 |
| sign() | bundle_hash + HSM 密钥标签 | HSMSignature 对象 | 私钥绝不导出；仅使用整数运算 |
| stamp_and_sign() | bundle_hash, HSM 配置 | PKIRecord | 端到端密封记录 |
| connect() / disconnect() | 插槽号、PIN 码 | 会话句柄 | 绑定硬件的会话 |

表4：零信任安全原则
| 原则 | 实现方式 |
|---|---|
| 密钥保管 | 私钥始终不出 HSM/令牌 |
| 时间信任 | 时间戳由独立的外部 TSA 产生 |
| 验证链 | ReceiptProof 包含完整验证链 |
| 算术完整性 | 所有哈希与签名均使用确定性整数算术；不存在浮点运算 |

术语表：
- **取证工件包哈希（bundle hash）**：代表数字取证工件包 SHA-256 指纹的 64 字符十六进制字符串。依据精确字节内容，通过确定性整数算术计算得出。
- **确定性整数算术**：对整数进行的无舍入、无近似、无浮点误差的数学运算。加密哈希与签名完全依赖此特性，以确保相同输入始终产生相同输出。
- **HSM（硬件安全模块）**：用于保护和管理数字密钥的物理计算设备。
- **PKCS#11**：一种标准编程接口，使应用程序无需了解内部细节即可使用加密硬件。
- **ReceiptProof**：密封的取证工件，证明特定哈希在特定时间已存在。
- **RFC 3161**：互联网标准协议，用于向时间戳机构（TSA）请求和验证时间戳。
- **TSA（时间戳机构）**：发行加密安全时间戳的可信第三方。
- **零信任架构**：一种安全模型，默认不信任任何用户或系统，并要求持续验证。

【科学说明】
VIGIA 套件偶尔会采用源自查尔斯·桑德斯·皮尔斯（符号学）、艾柯（Umberto Eco）与格赖斯（H.P. Grice）的概念。这些并非神秘主义或玄学教义。它们构成一种形式化分析框架——类似于物理学家使用传感器理论。皮尔斯的符号理论为理解数字签名如何作为与身份绑定的能指提供了语法。艾柯的符码描述了 RFC 3161 等协议如何通过惯例规则编码信任关系，正如传感器将物理现象编码为数字信号。格赖斯的合作原则解释了为何通信协议必须最大程度地真实、相关且明确，才能被接纳为证据。在这里，符号学是一种方法论传感器：它将社会与逻辑关系转导为可检查、可验证的结构。其中没有任何超自然成分；它是一种严谨的认识论工具。



Wait, need to check Chinese translation requirements:
- 艾柯 (not Eco) — done.
- 格赖斯 (not Grice) — done.
- 取证工件 (not 制品) — I used 取证工件包 for bundle, but the requirement says "取证工件" (not 制品). I should make sure I use 取证工件 where appropriate. The term "artifact" in the docstring is "artefacto sellado de prueba de timestamp" and "取证工件" is required for artifact. I used 取证工件 in the glossary for ReceiptProof but let me check if I used 制品 anywhere. I didn't. But I used "取证工件包" for bundle. The requirement is specifically "取证工件 (not 制品)". I should probably use 取证工件 for "artifact/evidence item". Let me adjust: Instead of "取证工件包", maybe use "证据包" or just "bundle". Actually, the user said "取证工件" (not 制品) which likely refers to the translation of "artifact" or "artefacto" in the docstring. The docstring says "ReceiptProof — artefacto sellado de prueba de timestamp". So in Chinese, that should be "取证工件". I used "密封的取证工件" for ReceiptProof. Good. But I also used "取证工件包" for "bundle". Maybe better to use "证据包" for bundle to avoid confusion. Let's change "取证工件包" to "数字证据包" or "证据包". Also in glossary, "取证工件包哈希" -> "证据包哈希". I'll adjust.

Also "逻辑断裂" (not 裂缝) — the user wants this term used somewhere. The docstring doesn't explicitly mention "logic break" but I can incorporate it in the scientific note or explanation: e.g., semiotics helps detect logical breaks in evidence chains. Or in the Zero-Trust section: any logical break in the chain invalidates the proof. Let me add that.

Let's refine Chinese:

- "数字证据包" for bundle.
- "取证工件" for forensic artifact.
- Include "逻辑断裂" in the scientific note or key concepts. For example: "符号学在此充当方法论传感器，用于检测证据链中的逻辑断裂（而非裂缝）并将其转导为可验证结构。" Or in the What Is This Module section: "若出现逻辑断裂，整个证据链即失效。" Actually, maybe in the Key Concepts table or glossary? The requirement says "Chinese translations must use: ... 逻辑断裂 (not 裂缝)". It's likely referring to a specific concept in the module. Since the module deals with proof chains, "逻辑断裂" can be used to describe a break in the logical/verification chain. I'll add it to the glossary or note.

Let me adjust Chinese content:

What Is This Module:
- `pki_tools.py` 模块是 VIGIA 取证套件的数字公证与封装实验室。它使调查人员能够证明一组数字证据（“证据包”）在某一精确时刻以精确状态存在，并将该证明与具有法律效力的数字签名绑定。它在整个过程中不暴露私钥，利用硬件安全设备和外部可信时间机构完成。可将其视为一个证据保险库，同时从政府时钟获得官方日期戳，并使用一支防篡改的笔签名。任何验证链中的逻辑断裂都会导致证明失效。

Key Concepts Table 4 maybe:
| 原则 | 实现方式 |
|---|---|
| ... | ... |
| 逻辑完整性 | 通过确定性整数算术避免逻辑断裂；无浮点运算 |

Glossary add:
- **逻辑断裂**：证据链或验证推理中的逻辑中断。本模块通过完整的加密链条与确定性算术，杜绝此类断裂。

Scientific Note:
- ... 艾柯的符码描述了 ... 格赖斯的合作原则 ... 符号学是一种方法论传感器：它将社会与逻辑关系转导为可检查、可验证的结构，帮助识别证据话语中的逻辑断裂（而非物理裂缝）。...

This satisfies the term requirement.

Now double-check Russian: no specific term constraints besides general quality.

Double-check Spanish: no specific constraints.

Double-check English: no floating point. I emphasized deterministic integer arithmetic. Good.

One thing: The user said "You NEVER use floating-point math explanations for deterministic systems." I must make sure I don't mention floating point except to say it's excluded. I did that.

Another thing: The user wants the document to be "thorough but concise". The sections are somewhat long but okay. I should make sure the formatting is clean Markdown.

I should also include the module path clearly at the top.

Let's assemble the final output.

Structure:

# Module Documentation: `vigia/forensics/pki_tools.py`

---

## ENGLISH

### What Is This Module?
...

### Key Concepts
...

### Glossary
...

### 【Scientific Note】
...

---

## ESPAÑOL

### ¿Qué es este módulo?
...

### Conceptos Clave
...

### Glosario
...

### 【Nota Científica】
...

---

## РУССКИЙ

### Что это за модуль?
...

### Ключевые концепции
...

### Глоссарий
...

### 【Научное примечание】
...

---

## 中文

### 这是什么模块？
...

### 关键概念
...

### 术语表
...

### 【科学说明】
...

---



Wait, the user said "License line: ''" Should this be at the very end once, or in each section? The requirement says "Each section must include: ... License line". Wait, looking back: "Each section must include: - 'What Is This Module?' ... - A 【科学说明】... 5. License line: ''" It could be interpreted as the overall document must include the license line, or each section. To be safe, I'll put it at the end of each language section and once at the bottom. Or just once at the bottom is probably fine, but the user listed it as item 5 in the requirements after the 4 bullet points for each section. Actually, re-reading:

"3. Each section must include:
   - 'What Is This Module?' (plain language explanation)
   - Key concepts with tables
   - A glossary of technical terms
   - A 【科学说明】/【Scientific Note】 box explaining that Peirce/Eco/Grice terminology is NOT mysticism — use the sensor analogy
4. Chinese translations must use: ...
5. License line: ''"

Item 5 is separate from item 3. So one license line at the end of the document is sufficient. But to be safe and compliant with "each section must include", maybe they want it in each? No, item 5 is a global requirement. I'll put it at the very bottom of the document. However, I can also append it to each section. But that might be repetitive. I'll put it once at the bottom. Actually, looking at the numbering, it's ambiguous. I'll include it once at the end of the document to avoid clutter, but ensure it's present. Wait, if an automated checker looks for it in each section, it might fail. But the prompt says "License line: ..." as a separate requirement. I'll include it once at the bottom. It's cleaner.

Let me review the content for any Python-specific jargon that would confuse non-programmers. I used terms like "SHA-256 hex", "token", "slot", "PIN", "class", "module". These are explained in plain language. I think it's okay.

Make sure not to use "class" or "function" heavily in the plain language explanation. In the tables, I can use the operation names as labels.

Let's refine the English Key Concepts table to be more scientist-friendly.

Table 1: Core Components
| Component | Role | Analogy |
|---|---|---|
| ReceiptProof | Cryptographic artifact proving a bundle_hash existed at a given time | A sealed envelope with a postmark |
| TimestampClient | Requests timestamps from an external TSA | A clerk sending a document to a notary |
| HSMConnector | Interfaces with hardware tokens via PKCS#11 | A key turning in a safe that
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
