<!--
VIGIA Academic Documentation
Module: c639dd43
Batch ID: vigia-doc-0088-c639dd43
Generated: 2026-05-20T14:56:47.863538+00:00
-->

---
doc_hash: c639dd43
module: vigia/forensics/rfc3161_chain.py
languages: [EN, ES, RU, ZH]
generated_by: moonshot-kimi-k2.6-batch-api
license: Apache-2.0
---

ENGLISH:
- What Is This Module? Plain language for scientists. Explain it's a digital evidence custody module. It creates tamper-evident timestamps using an independent authority (TSA). Think of it like having a notary public stamp on your lab notebook, but for digital files. Uses SHA-256 and SHA-512 (deterministic integer-based hashing, no floating point). Creates immutable records.
- Key Concepts table:
  | Concept | Description | Scientific Equivalent |
  |---|---|---|
  | RFC 3161 | Internet standard for trusted timestamping | ISO 17025-accredited lab clock with audit trail |
  | TSA (Time Stamp Authority) | Independent server that cryptographically binds a hash to a time | External calibration lab verifying measurement time |
  | TimeStampReq (TSQ) | Standard request format sent to TSA | Signed requisition form |
  | TimeStampResp (TSR) | Signed reply from TSA proving time of existence | Notarized certificate of receipt |
  | CustodyRecord | Immutable frozen dataclass storing seal info | Permanent lab notebook entry |
  | HMAC | Local integrity check | Internal lab balance self-test |
  | SHA-256 / SHA-512 | Cryptographic hash functions using deterministic integer bitwise operations | Analytical fingerprint (deterministic, no floating-point arithmetic) |
  | NOT_INDEPENDENT_WITNESS | Fallback local token explicitly marked as non-independent | Internal memo acknowledging no external notary |
  | Daubert Standard | US legal standard for admissible scientific evidence | Peer-review and reproducibility criteria for court |
  | Frozen dataclass | Immutable data structure | Engraved stone tablet (cannot be altered) |

- Glossary:
  - **Hash (SHA-256/512)**: A deterministic fixed-length integer fingerprint produced by bitwise logical operations on binary data. No floating-point calculations are used; the process is entirely discrete integer arithmetic.
  - **TSA (Time Stamp Authority)**: An independent trusted third party that issues cryptographically signed timestamps.
  - **Custody Record**: An immutable entry documenting who handled a piece of evidence and when.
  - **HMAC**: A local cryptographic checksum proving that data has not changed since it was last processed by the local system.
  - **RFC 3161 Token**: A signed data structure proving that a specific digital hash existed at a specific point in time.
  - **Deterministic Integer Arithmetic**: Mathematical operations on whole numbers (bits) that always produce the exact same result under the same conditions, with no rounding errors or approximations.

- Scientific Note (ENGLISH):
  【Scientific Note】
  The forensic vocabulary employed in this module occasionally borrows from semiotics—specifically the frameworks of **Peirce**, **Eco**, and **Grice**—to describe how digital evidence "signifies" integrity. This is not mysticism.  
  Think of a **sign** (in the Peircean sense) as a **sensor reading**: a thermometer does not "mean" temperature by magic; it produces an indexical sign via a deterministic physical process. Eco’s codes are analogous to **calibration protocols** that map raw sensor outputs to interpretable units. Grice’s maxims function like **quality-control criteria** for data transmission—ensuring that what the sender (the evidence producer) conveys is as informative, truthful, and relevant as a well-calibrated instrument would report.  
  Therefore, when we speak of an RFC 3161 token as an "indexical sign" of existence at a given moment, we are simply stating that the TSA acts as an independent measurement device—like a certified clock whose readout is frozen into an immutable integer record. There is no interpretive ambiguity in the arithmetic; the hash is a deterministic integer, the signature is a deterministic integer relation, and the timestamp is a discrete label.

ESPAÑOL:
- Terms: Peirce, Eco, Grice. Custodia, TSA.
- What is this module? Explain as above.
- Key concepts table:
  | Concepto | Descripción | Equivalente científico |
  |---|---|---|
  | RFC 3161 | Estándar de Internet para sellado de tiempo de confianza | Reloj de laboratorio acreditado ISO 17025 con trazabilidad |
  | TSA (Time Stamp Authority) | Servidor independiente que vincula criptográficamente un hash con una hora | Laboratorio de calibración externo que certifica el momento de la medición |
  | TimeStampReq (TSQ) | Formato estándar de solicitud enviado a la TSA | Formulario de requisición firmado |
  | TimeStampResp (TSR) | Respuesta firmada de la TSA que prueba la existencia temporal | Certificado de recepción notariado |
  | CustodyRecord | Clase de datos inmutable que almacena información del sello | Entrada permanente en el cuaderno de laboratorio |
  | HMAC | Verificación de integridad local | Autocomprobación de la balanza interna del laboratorio |
  | SHA-256 / SHA-512 | Funciones hash criptográficas basadas en operaciones bit a bit deterministas de aritmética entera | Huella dactilar analítica (determinista, sin aritmética de coma flotante) |
  | NOT_INDEPENDENT_WITNESS | Token de reserva local marcado explícitamente como no independiente | Memo interno que reconoce la ausencia de notario externo |
  | Estándar Daubert | Criterio legal estadounidense para evidencia científica admisible | Criterios de revisión por pares y reproducibilidad para el tribunal |
  | Frozen dataclass | Estructura de datos inmutable | Tabla de piedra grabada (no puede alterarse) |

- Glossary:
  - **Hash (SHA-256/512)**: Huella dactilar digital de longitud fija generada por operaciones lógicas bit a bit sobre datos binarios. No se utilizan cálculos de coma flotante; el proceso es aritmética entera discreta puramente determinista.
  - **TSA (Time Stamp Authority)**: Tercero de confianza independiente que emite sellos de tiempo firmados criptográficamente.
  - **Registro de custodia (CustodyRecord)**: Entrada inmutable que documenta quién manipuló una pieza de evidencia y cuándo.
  - **HMAC**: Suma de comprobación criptográfica local que demuestra que los datos no han cambiado desde que el sistema los procesó por última vez.
  - **Token RFC 3161**: Estructura de datos firmada que prueba que un hash digital específico existía en un momento determinado.
  - **Aritmética entera determinista**: Operaciones matemáticas sobre números enteros (bits) que siempre producen exactamente el mismo resultado bajo las mismas condiciones, sin errores de redondeo ni aproximaciones.

- Scientific Note (ESPAÑOL):
  【Nota Científica】
  El vocabulario forense empleado en este módulo toma prestado ocasionalmente de la semiótica —en concreto, los marcos de **Peirce**, **Eco** y **Grice**— para describir cómo la evidencia digital "significa" integridad. Esto no es misticismo.  
  Piense en un **signo** (en sentido peirceano) como una **lectura de sensor**: un termómetro no "significa" temperatura por arte de magia; produce un signo indexical mediante un proceso físico determinista. Los códigos de Eco son análogos a **protocolos de calibración** que mapean las salidas crudas del sensor a unidades interpretables. Los máximas de Grice funcionan como **criterios de control de calidad** para la transmisión de datos —garantizando que lo que el emisor (el productor de evidencia) comunica sea tan informativo, veraz y relevante como lo reportaría un instrumento bien calibrado.  
  Por tanto, cuando denominamos al token RFC 3161 un "signo indexical" de existencia en un instante dado, simplemente afirmamos que la TSA actúa como un dispositivo de medición independiente —como un reloj certificado cuya lectura se congela en un registro entero inmutable. No hay ambigüedad interpretativa en la aritmética; el hash es un entero determinista, la firma es una relación de enteros determinista, y la marca temporal es una etiqueta discreta.

РУССКИЙ:
- Need to use Russian terms. Peirce = Пирс, Eco = Эко, Grice = Грайс. But the user didn't specify Russian transliteration restrictions, only Chinese. However, standard Russian academic transliteration: Пирс, Умберто Эко, Грайс. I'll use those.
- What is this module? etc.
- Key concepts:
  | Понятие | Описание | Научный эквивалент |
  |---|---|---|
  | RFC 3161 | Стандарт Интернета для доверенного штампования времени | Аккредитованные ISO 17025 лабораторные часы с аудитом |
  | TSA (Time Stamp Authority) | Независимый сервер, криптографически связывающий хеш со временем | Внешняя калибровочная лаборатория, подтверждающая момент измерения |
  | TimeStampReq (TSQ) | Стандартный формат запроса, отправляемый в TSA | Подписанная форма-заявка |
  | TimeStampResp (TSR) | Подписанный ответ TSA, доказывающий момент существования | Нотариально заверенное свидетельство о приёме |
  | CustodyRecord | Неизменяемый класс данных, хранящий сведения о печати | Постоянная запись в лабораторном журнале |
  | HMAC | Локальная проверка целостности | Внутренний самоконтроль лабораторных весов |
  | SHA-256 / SHA-512 | Криптографические хеш-функции, основанные на детерминированных побитовых операциях целочисленной арифметики | Аналитический отпечаток (детерминированный, без арифметики с плавающей точкой) |
  | NOT_INDEPENDENT_WITNESS | Локальный резервный токен, явно помеченный как независимый | Внутренняя служебная запись, признающая отсутствие внешнего нотариуса |
  | Стандарт Доберта (Daubert) | Правовой стандарт США для допустимости научных доказательств | Критерии рецензирования и воспроизводимости для суда |
  | Frozen dataclass | Неизменяемая структура данных | Выгравированная каменная табличка (невозможно изменить) |

- Glossary:
  - **Хеш (SHA-256/512)**: Детерминированный целочисленный отпечаток фиксированной длины, производимый побитовыми логическими операциями над двоичными данными. Вычисления с плавающей точкой не используются; процесс представляет собой чистую дискретную целочисленную арифметику.
  - **TSA (Time Stamp Authority)**: Независимая доверенная третья сторона, выдающая криптографически подписанные метки времени.
  - **CustodyRecord (Регистр хранения)**: Неизменяемая запись, документирующая, кто и когда обращался с уликой.
  - **HMAC**: Локальная криптографическая контрольная сумма, подтверждающая, что данные не изменились с момента их последней обработки локальной системой.
  - **Токен RFC 3161**: Подписанная структура данных, доказывающая, что конкретный цифровой хеш существовал в определённый момент времени.
  - **Детерминированная целочисленная арифметика**: Математические операции над целыми числами (битами), которые всегда дают точно такой же результат при тех же условиях, без ошибок округления или приближений.

- Scientific Note (РУССКИЙ):
  【Научное примечание】
  Следовательская терминология, используемая в данном модуле, время от времени заимствует из семиотики — в частности, из концепций **Пирса**, **Эко** и **Грайса** — чтобы описать, как цифровое доказательство «означает» целостность. Это не мистицизм.  
  Воспринимайте **знак** (в пирсовском смысле) как **показание датчика**: термометр не «означает» температуру по магии; он производит индексальный знак посредством детерминированного физического процесса. Коды Эко аналогичны **протоколам калибровки**, которые отображают сырые выходные сигналы датчика на интерпретируемые единицы. Максимы Грайса функционируют как **критерии контроля качества** передачи данных — гарантируя, что то, что передатчик (производитель доказательства) сообщает, столь же информативно, достоверно и релевантно, как показания хорошо откалиброванного прибора.  
  Следовательно, когда мы называем токен RFC 3161 «индексальным знаком» существования в данный момент, мы лишь констатируем, что TSA действует как независимое измерительное устройство — как сертифицированные часы, показания которых зафиксированы в неизменяемом целочисленном регистре. В арифметике нет интерпретационной неоднозначности; хеш — это детерминированное целое число, подпись — детерминированное целочисленное отношение, а метка времени — дискретная метка.

中文:
- Must use: 艾柯 (Eco), 格赖斯 (Grice), 取证工件 (artifact), 逻辑断裂 (logical break/gap? The user said "逻辑断裂 (not 裂缝)". I need to make sure I use 逻辑断裂 somewhere appropriate, perhaps in the context of NOT_INDEPENDENT_WITNESS or chain integrity? Or perhaps in the scientific note? Actually, the user specifically listed these Chinese translation requirements. I should incorporate 取证工件 for artifact/evidence item, and 逻辑断裂 instead of 裂缝 for any mention of crack/fracture/gap. Since the module is about chain integrity, "crack in the chain" could be translated as 逻辑断裂. Let's ensure to use it.
- What is this module?
- Key concepts:
  | 概念 | 说明 | 科学等效物 |
  |---|---|---|
  | RFC 3161 | 互联网可信时间戳标准 | 经ISO 17025认证的实验室时钟及审计追踪 |
  | TSA (Time Stamp Authority) | 通过加密方式将哈希值与时间点绑定的独立服务器 | 外部校准实验室，验证测量发生的时间 |
  | TimeStampReq (TSQ) | 发送至TSA的标准请求格式 | 已签名的申请单 |
  | TimeStampResp (TSR) | TSA返回的签名应答，证明某时刻的存在性 | 经公证的收据证明 |
  | CustodyRecord | 不可变的冻结数据类，存储封印信息 | 实验室永久日志条目 |
  | HMAC | 本地完整性校验 | 实验室内部天平的自检程序 |
  | SHA-256 / SHA-512 | 基于确定性整数位运算的加密哈希函数 | 分析指纹（确定性，无浮点运算） |
  | NOT_INDEPENDENT_WITNESS | 本地回退令牌，明确声明非独立见证 | 内部备忘录，承认无外部公证人 |
  | Daubert标准 | 美国科学证据可采性的法律标准 | 用于法庭的同行评审与可重复性标准 |
  | 冻结数据类 (Frozen dataclass) | 不可变的数据结构 | 刻有文字的石板（无法篡改） |

  Note: Use 取证工件 for "artifact" in explanations.
- Glossary:
  - **哈希值 (SHA-256/512)**: 通过对二进制数据进行按位逻辑运算而生成的、长度固定的确定性整数指纹。不使用浮点运算；整个过程纯粹是离散整数算术。
  - **TSA (时间戳机构)**: 独立可信的第三方，负责签发加密签名的时间戳。
  - **保管记录 (CustodyRecord)**: 不可变的日志条目，记录谁、在何时接触过取证工件。
  - **HMAC**: 本地加密校验和，用于证明自本地系统上次处理以来，数据未被改动。
  - **RFC 3161令牌**: 一种已签名的数据结构，证明某个特定数字哈希在某一确切时间点已经存在。
  - **确定性整数算术**: 对整数（比特）进行的数学运算，在相同条件下总是产生完全相同的结果，不存在舍入误差或近似值。

- Scientific Note (中文):
  【科学说明】
  本模块所使用的取证词汇偶尔借鉴自符号学——尤其是**皮尔斯**、**艾柯**与**格赖斯**的理论框架——以描述数字证据如何“意指”完整性。这并非神秘主义。  
  请将**符号**（皮尔斯意义上的）视为一种**传感器读数**：温度计并非凭借魔法来“意指”温度；它通过确定性物理过程产生一个指示性符号。艾柯的“代码”类似于**校准协议**，将传感器的原始输出映射为可解释的单位。格赖斯的“准则”则相当于数据传输的**质控标准**——确保证据发送者（取证工件的生成方）所传达的信息如同一台经过良好校准的仪器所报告的那样，具有充分的信息量、真实性与相关性。  
  因此，当我们将RFC 3161令牌称为某一时刻存在性的“指示性符号”时，我们仅仅是在陈述：TSA充当了一台独立的测量装置——如同一台经过认证的时钟，其读数被冻结成一条不可变的整数记录。算术层面不存在解释上的歧义；哈希是确定性整数，签名是确定性的整数关系，而时间戳则是一个离散标签。

Now, I need to ensure I incorporate 逻辑断裂 somewhere. The user specifically said: "逻辑断裂 (not 裂缝)". This likely refers to avoiding "裂缝" for "crack/breach" in chain of custody context. I can use it in the Chinese section when discussing chain integrity or the fallback local token. For example, in the description of verify_chain_integrity: "此函数检测保管链中的逻辑断裂" or in the NOT_INDEPENDENT_WITNESS row: "防止在证据链中引入逻辑断裂". Let me add that.

Also, the user said "Do NOT use floating-point math explanations — emphasize deterministic integer arithmetic where applicable." I need to make sure I explicitly mention in the hash explanation that SHA-256/512 uses deterministic integer arithmetic (bitwise operations on 32-bit or 64-bit words), no floating point.

The module path is `vigia/forensics/rfc3161_chain.py`. I should include this.

The document should be Markdown.

Let's construct the final output. I'll separate sections clearly.

I should also make sure to mention the Kimi fix in plain language: the local fallback does not pretend to be an independent witness. It explicitly declares NOT_INDEPENDENT_WITNESS. This is important.

Let's refine the "What Is This Module?" sections.

ENGLISH:
This module, `vigia/forensics/rfc3161_chain.py`, is the digital equivalent of a notarized laboratory logbook. It creates tamper-evident timestamps for digital evidence (artifacts) by requesting cryptographic proof from an independent Time Stamp Authority (TSA). While an internal HMAC seal tells you "this file has not changed since our system touched it," the RFC 3161 seal tells you "an independent third party witnessed the fingerprint of this file at this exact time." For legal and scientific standards such as Daubert, this distinction is critical: it is the difference between a researcher certifying their own data and an external auditor certifying it. The module computes deterministic integer-based fingerprints (SHA-256 and SHA-512) and stores the results in immutable, frozen records that cannot be altered after creation.

ESPAÑOL:
Este módulo, `vigia/forensics/rfc3161_chain.py`, es el equivalente digital de un cuaderno de laboratorio notariado. Genera sellos de tiempo resistentes a la manipulación para evidencia digital (artefactos de evidencia) solicitando prueba criptográfica a una Autoridad de Sellado de Tiempo (TSA) independiente. Mientras que un sello HMAC interno indica "este archivo no ha cambiado desde que nuestro sistema lo procesó", el sello RFC 3161 indica "un tercero independiente presenció la huella de este archivo en este momento exacto". Para estándares legales y científicos como Daubert, esta distinción es crítica: es la diferencia entre un investigador que certifica sus propios datos y un auditor externo que lo hace. El módulo calcula huellas dactilares deterministas basadas en aritmética entera (SHA-256 y SHA-512) y almacena los resultados en registros inmutables, congelados, que no pueden alterarse tras su creación.

РУССКИЙ:
Данный модуль, `vigia/forensics/rfc3161_chain.py`, представляет собой цифровой аналог нотариально заверенного лабораторного журнала. Он создаёт невозможные к подделке временны́е метки для цифровых доказательств (улик) путём запроса криптографического доказательства у независимого центра штампования времени (TSA). В то время как внутренняя печать HMAC говорит: «этот файл не изменялся с момента последней обработки нашей системой», печать RFC 3161 заявляет: «независимая третья сторона засвидетельствовала отпечаток этого файла в точно указанный момент». Для правовых и научных стандартов, таких как Доберт (Daubert), это различие принципиально: оно аналогично разнице между исследователем, заверяющим собственные данные, и внешним аудитором, делающим то же самое. Модуль вычисляет детерминированные целочисленные отпечатки (SHA-256 и SHA-512) и сохраняет результаты в неизменяемых «замороженных» записях, которые невозможно изменить после создания.

中文:
本模块 `vigia/forensics/rfc3161_chain.py` 相当于一本经过公证的数字化实验室日志。它通过向独立的时间戳机构（TSA）申请加密证明，为数字取证工件生成防篡改的时间戳。内部HMAC封印的含义是“自本系统处理该文件以来，它未被改动”；而RFC 3161封印的含义则是“在确切的时间点，有独立第三方见证了该文件的指纹”。对于Daubert等法律与科学标准而言，这一区别至关重要：它类似于研究者自证其数据，与由外部审计员进行认证之间的差别。本模块采用基于确定性整数运算的指纹算法（SHA-256与SHA-512），并将结果存入创建后不可更改的冻结记录中。

Now, key concepts tables. I should make sure they are formatted nicely.

I need to include the License line exactly: ""

I will place it at the very end of the document, once.

Let's double-check the Chinese terms:
- 艾柯 (Eco) ✓
- 格赖斯 (Grice) ✓
- 取证工件 (artifact) ✓
- 逻辑断裂 (not 裂缝) — I will use this in the context of chain integrity or fallback. Let me add a specific note or sentence in the Chinese section. For example, in the description of `verify_chain_integrity`: "该函数逐条校验本地HMAC，以发现任何逻辑断裂；请注意，它并不验证TSA签名。" Or in the table for `NOT_INDEPENDENT_WITNESS`: "本地显式声明的回退令牌，防止在证据链中伪装独立见证，避免产生逻辑断裂。" That works.

Let's ensure the scientific note in Chinese uses 【科学说明】. The user wrote: "A 【科学说明】/【Scientific Note】 box". So in the English section it can be 【Scientific Note】, Spanish 【Nota Científica】, Russian 【Научное примечание】, Chinese 【科学说明】.

Let's write the full text.

One more thing: The user said "You NEVER use floating-point math explanations for deterministic systems." So when describing SHA, I must explicitly say it uses integer arithmetic, no floating point. I have done that.

Also, the module computes both SHA-256 and SHA-512. I should mention that in the flow.

Let's verify all requirements:
1. Target audience: scientists who do NOT know Python. Yes, plain language, no Python code blocks or syntax explanations. I will not show code.
2. Format: Markdown with 4 language sections. Yes.
3. Each section includes:
   - "What Is This Module?" (plain language). Yes.
   - Key concepts with tables. Yes.
   - Glossary. Yes.
   - Scientific Note box. Yes.
4. Chinese translations: 艾柯, 格赖斯, 取证工件, 逻辑断裂. Yes.
5. License line. Yes.
6. No floating-point math explanations. Yes.

I will not include the module docstring verbatim; I will paraphrase it for the audience.

Structure:
# Module Documentation: `vigia/forensics/rfc3161_chain.py`

## ENGLISH
...
## ESPAÑOL
...
## РУССКИЙ
...
## 中文
...

Then license.

Let me draft carefully.

One potential issue: The user said "A 【科学说明】/【Scientific Note】 box explaining that Peirce/Eco/Grice terminology is NOT mysticism — use the sensor analogy". So all four sections need to contain this box. I have drafted them.

Let me check the Chinese section for 逻辑断裂 again. I will integrate it into the `verify_chain_integrity` description in the table or text. Let's add it to the table for `verify_chain_integrity`:
| `verify_chain_integrity` | 校验整条保管链的本地HMAC，侦测是否存在逻辑断裂；不校验TSA签名 | — |

Actually, the module functions are `seal_artifact`, `export_chain`, `verify_chain_integrity`. I should mention these in the key concepts or in the text.

Key concepts tables should probably include the main classes/functions too, or at least the concepts. Let me add rows for the functions.

ENGLISH Table update:
| Concept | Description | Scientific Equivalent |
|---|---|---|
| `seal_artifact()` | Seals an artifact by requesting timestamps from TSAs in priority order; falls back to a local signer if all external TSAs fail | Applying a witnessed tamper-evident seal to a sample tube |
| `export_chain()` | Exports the complete custody chain for inclusion in a final report bundle | Generating a PDF appendix of all calibration certificates |
| `verify_chain_integrity()` | Verifies the local HMAC of each record to detect tampering; does **not** verify the TSA signature | Running an internal diagnostic to detect logical breaks in the instrument log |

Wait, the user said for Chinese: 逻辑断裂 (not 裂缝). So in English, I can use "logical break" but in Chinese I must use 逻辑断裂. In the English table, "logical breaks" is okay as a translation aid, but the Chinese table must have 逻辑断裂. I'll ensure the Chinese row for verify_chain_integrity uses 逻辑断裂.

Chinese table row:
| `verify_chain_integrity` | 逐条校验本地HMAC以确认记录未被篡改，从而识别证据链中的任何逻辑断裂；注意：不验证TSA签名 | 运行内部诊断以发现仪器日志中的逻辑断裂 |

Yes.

Let's finalize the tables.

ENGLISH Table:
| Concept | Description | Scientific Equivalent |
|---|---|---|
| RFC 3161 | Internet standard for trusted timestamping | ISO 17025-accredited laboratory clock with full audit trail |
| TSA (Time Stamp Authority) | Independent server that cryptographically binds a hash to a universal time | External calibration laboratory certifying the moment of measurement |
| `CustodyRecord` | Immutable frozen data structure that stores seal metadata | Engraved stone tablet in a lab archive (cannot be altered after creation) |
| `RFC3161Timestamper` | Engine that manages communication with TSAs and builds the evidence seal | Robotic arm that applies tamper-evident seals and logs each action |
| `seal_artifact()` | Requests timestamps from TSAs in priority order; if all fail, uses a documented local fallback that explicitly states it is **not** an independent witness | Applying a notary seal; if the notary is absent, using an internal memo clearly labeled "unwitnessed" |
| `export_chain()` | Exports the entire custody chain for attachment to a final report bundle | Compiling all notarized receipts into a master appendix |
| `verify_chain_integrity()` | Checks the local HMAC of every record to detect tampering; does **not** verify the TSA's cryptographic signature | Internal diagnostic to detect logical breaks in the instrument log |
| SHA-256 / SHA-512 | Cryptographic hash functions using deterministic integer bitwise operations on binary data | Analytical fingerprint (deterministic integer arithmetic, no floating-point operations) |
| HMAC | Local integrity checksum proving the data has not changed since last processed by the local system | Internal balance self-test |
| `NOT_INDEPENDENT_WITNESS` | Explicit declaration in the local fallback token to prevent misrepresentation as third-party testimony | A lab note honestly stating "this measurement was not observed by an external auditor" |

ESPAÑOL Table:
| Concepto | Descripción | Equivalente científico |
|---|---|---|
| RFC 3161 | Estándar de Internet para el sellado de tiempo de confianza | Reloj de laboratorio acreditado bajo ISO 17025 con trazabilidad completa |
| TSA (Time Stamp Authority) | Servidor independiente que vincula criptográficamente un hash a una hora universal | Laboratorio de calibración externo que certifica el momento de la medición |
| `CustodyRecord` | Estructura de datos inmutable («frozen») que almacena los metadatos del sello | Tabla de piedra grabada en un archivo de laboratorio (no puede alterarse tras su creación) |
| `RFC3161Timestamper` | Motor que gestiona la comunicación con las TSAs y construye el sello de evidencia | Brazo robótico que aplica sellos inviolables y registra cada acción |
| `seal_artifact()` | Solicita sellos de tiempo
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
