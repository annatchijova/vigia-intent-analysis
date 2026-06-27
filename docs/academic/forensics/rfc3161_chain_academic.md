<!--
VIGIA Academic Documentation
Module: c639dd43
Batch ID: vigia-doc-0088-c639dd43
Generated: 2026-05-20T14:56:47.863538+00:00
-->

# Module Documentation: `vigia/forensics/rfc3161_chain.py`

---

## ENGLISH

### What Is This Module?

This module, `vigia/forensics/rfc3161_chain.py`, is the digital equivalent of a notarized laboratory logbook. It creates tamper-evident timestamps for digital evidence (artifacts) by requesting cryptographic proof from an independent Time Stamp Authority (TSA). While an internal HMAC seal tells you "this file has not changed since our system touched it," the RFC 3161 seal tells you "an independent third party witnessed the fingerprint of this file at this exact time." For legal and scientific standards such as Daubert, this distinction is critical: it is the difference between a researcher certifying their own data and an external auditor certifying it. The module computes deterministic integer-based fingerprints (SHA-256 and SHA-512) and stores the results in immutable, frozen records that cannot be altered after creation.

### Key Concepts

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
| Daubert Standard | US legal standard for admissible scientific evidence | Peer-review and reproducibility criteria for court |

### Glossary

- **Hash (SHA-256/512)**: A deterministic fixed-length integer fingerprint produced by bitwise logical operations on binary data. No floating-point calculations are used; the process is entirely discrete integer arithmetic.
- **TSA (Time Stamp Authority)**: An independent trusted third party that issues cryptographically signed timestamps.
- **Custody Record**: An immutable entry documenting who handled a piece of evidence and when.
- **HMAC**: A local cryptographic checksum proving that data has not changed since it was last processed by the local system.
- **RFC 3161 Token**: A signed data structure proving that a specific digital hash existed at a specific point in time.
- **Deterministic Integer Arithmetic**: Mathematical operations on whole numbers (bits) that always produce the exact same result under the same conditions, with no rounding errors or approximations.

### 【Scientific Note】

The forensic vocabulary employed in this module occasionally borrows from semiotics—specifically the frameworks of **Peirce**, **Eco**, and **Grice**—to describe how digital evidence "signifies" integrity. This is not mysticism.

Think of a **sign** (in the Peircean sense) as a **sensor reading**: a thermometer does not "mean" temperature by magic; it produces an indexical sign via a deterministic physical process. Eco's codes are analogous to **calibration protocols** that map raw sensor outputs to interpretable units. Grice's maxims function like **quality-control criteria** for data transmission—ensuring that what the sender (the evidence producer) conveys is as informative, truthful, and relevant as a well-calibrated instrument would report.

Therefore, when we speak of an RFC 3161 token as an "indexical sign" of existence at a given moment, we are simply stating that the TSA acts as an independent measurement device—like a certified clock whose readout is frozen into an immutable integer record. There is no interpretive ambiguity in the arithmetic; the hash is a deterministic integer, the signature is a deterministic integer relation, and the timestamp is a discrete label.

---

## ESPAÑOL

### ¿Qué es este módulo?

Este módulo, `vigia/forensics/rfc3161_chain.py`, es el equivalente digital de un cuaderno de laboratorio notariado. Genera sellos de tiempo resistentes a la manipulación para evidencia digital (artefactos de evidencia) solicitando prueba criptográfica a una Autoridad de Sellado de Tiempo (TSA) independiente. Mientras que un sello HMAC interno indica "este archivo no ha cambiado desde que nuestro sistema lo procesó", el sello RFC 3161 indica "un tercero independiente presenció la huella de este archivo en este momento exacto". Para estándares legales y científicos como Daubert, esta distinción es crítica: es la diferencia entre un investigador que certifica sus propios datos y un auditor externo que lo hace. El módulo calcula huellas dactilares deterministas basadas en aritmética entera (SHA-256 y SHA-512) y almacena los resultados en registros inmutables, congelados, que no pueden alterarse tras su creación.

### Conceptos Clave

| Concepto | Descripción | Equivalente científico |
|---|---|---|
| RFC 3161 | Estándar de Internet para el sellado de tiempo de confianza | Reloj de laboratorio acreditado bajo ISO 17025 con trazabilidad completa |
| TSA (Time Stamp Authority) | Servidor independiente que vincula criptográficamente un hash a una hora universal | Laboratorio de calibración externo que certifica el momento de la medición |
| `CustodyRecord` | Estructura de datos inmutable («frozen») que almacena los metadatos del sello | Tabla de piedra grabada en un archivo de laboratorio (no puede alterarse tras su creación) |
| `RFC3161Timestamper` | Motor que gestiona la comunicación con las TSAs y construye el sello de evidencia | Brazo robótico que aplica sellos inviolables y registra cada acción |
| `seal_artifact()` | Solicita sellos de tiempo de las TSAs en orden de prioridad; si todas fallan, usa un respaldo local documentado que declara explícitamente no ser testigo independiente | Aplicar un sello notarial; si el notario no está disponible, usar un memo interno claramente etiquetado como "no presenciado" |
| `export_chain()` | Exporta toda la cadena de custodia para adjuntarla al paquete del informe final | Compilar todos los recibos notariados en un apéndice maestro |
| `verify_chain_integrity()` | Comprueba el HMAC local de cada registro para detectar manipulaciones; **no** verifica la firma criptográfica de la TSA | Diagnóstico interno para detectar rupturas lógicas en el registro del instrumento |
| SHA-256 / SHA-512 | Funciones hash criptográficas basadas en operaciones bit a bit deterministas de aritmética entera | Huella dactilar analítica (aritmética entera determinista, sin operaciones de punto flotante) |
| HMAC | Suma de comprobación de integridad local que prueba que los datos no han cambiado desde que el sistema los procesó por última vez | Autocomprobación de la balanza interna del laboratorio |
| `NOT_INDEPENDENT_WITNESS` | Declaración explícita en el token de respaldo local para evitar representarlo erróneamente como testimonio de terceros | Una nota de laboratorio que declara honestamente "esta medición no fue observada por un auditor externo" |
| Estándar Daubert | Criterio legal estadounidense para evidencia científica admisible | Criterios de revisión por pares y reproducibilidad para el tribunal |

### Glosario

- **Hash (SHA-256/512)**: Huella dactilar digital de longitud fija generada por operaciones lógicas bit a bit sobre datos binarios. No se utilizan cálculos de coma flotante; el proceso es aritmética entera discreta puramente determinista.
- **TSA (Time Stamp Authority)**: Tercero de confianza independiente que emite sellos de tiempo firmados criptográficamente.
- **Registro de custodia (CustodyRecord)**: Entrada inmutable que documenta quién manipuló una pieza de evidencia y cuándo.
- **HMAC**: Suma de comprobación criptográfica local que demuestra que los datos no han cambiado desde que el sistema los procesó por última vez.
- **Token RFC 3161**: Estructura de datos firmada que prueba que un hash digital específico existía en un momento determinado.
- **Aritmética entera determinista**: Operaciones matemáticas sobre números enteros (bits) que siempre producen exactamente el mismo resultado bajo las mismas condiciones, sin errores de redondeo ni aproximaciones.

### 【Nota Científica】

El vocabulario forense empleado en este módulo toma prestado ocasionalmente de la semiótica —en concreto, los marcos de **Peirce**, **Eco** y **Grice**— para describir cómo la evidencia digital "significa" integridad. Esto no es misticismo.

Piense en un **signo** (en sentido peirceano) como una **lectura de sensor**: un termómetro no "significa" temperatura por arte de magia; produce un signo indexical mediante un proceso físico determinista. Los códigos de Eco son análogos a **protocolos de calibración** que mapean las salidas crudas del sensor a unidades interpretables. Los máximas de Grice funcionan como **criterios de control de calidad** para la transmisión de datos —garantizando que lo que el emisor (el productor de evidencia) comunica sea tan informativo, veraz y relevante como lo reportaría un instrumento bien calibrado.

Por tanto, cuando denominamos al token RFC 3161 un "signo indexical" de existencia en un instante dado, simplemente afirmamos que la TSA actúa como un dispositivo de medición independiente —como un reloj certificado cuya lectura se congela en un registro entero inmutable. No hay ambigüedad interpretativa en la aritmética; el hash es un entero determinista, la firma es una relación de enteros determinista, y la marca temporal es una etiqueta discreta.

---

## РУССКИЙ

### Что представляет собой этот модуль?

Данный модуль, `vigia/forensics/rfc3161_chain.py`, представляет собой цифровой аналог нотариально заверенного лабораторного журнала. Он создаёт невозможные к подделке временны́е метки для цифровых доказательств (улик) путём запроса криптографического доказательства у независимого центра штампования времени (TSA). В то время как внутренняя печать HMAC говорит: «этот файл не изменялся с момента последней обработки нашей системой», печать RFC 3161 заявляет: «независимая третья сторона засвидетельствовала отпечаток этого файла в точно указанный момент». Для правовых и научных стандартов, таких как Доберт (Daubert), это различие принципиально: оно аналогично разнице между исследователем, заверяющим собственные данные, и внешним аудитором, делающим то же самое. Модуль вычисляет детерминированные целочисленные отпечатки (SHA-256 и SHA-512) и сохраняет результаты в неизменяемых «замороженных» записях, которые невозможно изменить после создания.

### Ключевые концепции

| Понятие | Описание | Научный эквивалент |
|---|---|---|
| RFC 3161 | Стандарт Интернета для доверенного штампования времени | Аккредитованные ISO 17025 лабораторные часы с аудитом |
| TSA (Time Stamp Authority) | Независимый сервер, криптографически связывающий хеш со временем | Внешняя калибровочная лаборатория, подтверждающая момент измерения |
| `CustodyRecord` | Неизменяемый класс данных, хранящий сведения о печати | Постоянная запись в лабораторном журнале |
| `RFC3161Timestamper` | Движок, управляющий коммуникацией с TSA и строящий печать доказательства | Роботизированная рука, применяющая защитные печати и регистрирующая каждое действие |
| `seal_artifact()` | Запрашивает метки времени у TSA в порядке приоритета; при неудаче всех использует документированный локальный резервный вариант, явно объявляющий себя не независимым свидетелем | Применение нотариальной печати; при отсутствии нотариуса — внутренняя памятка, чётко помеченная как «незасвидетельствованная» |
| `export_chain()` | Экспортирует всю цепочку хранения для приложения к итоговому пакету отчёта | Составление всех нотариально заверенных расписок в главное приложение |
| `verify_chain_integrity()` | Проверяет локальный HMAC каждой записи для обнаружения подделки; **не** проверяет криптографическую подпись TSA | Внутренняя диагностика для обнаружения логических разрывов в журнале прибора |
| SHA-256 / SHA-512 | Криптографические хеш-функции, основанные на детерминированных побитовых операциях целочисленной арифметики | Аналитический отпечаток (детерминированный, без арифметики с плавающей точкой) |
| HMAC | Локальная проверка целостности | Внутренний самоконтроль лабораторных весов |
| `NOT_INDEPENDENT_WITNESS` | Локальный резервный токен, явно помеченный как не независимый | Внутренняя служебная запись, признающая отсутствие внешнего нотариуса |
| Стандарт Доберта (Daubert) | Правовой стандарт США для допустимости научных доказательств | Критерии рецензирования и воспроизводимости для суда |

### Глоссарий

- **Хеш (SHA-256/512)**: Детерминированный целочисленный отпечаток фиксированной длины, производимый побитовыми логическими операциями над двоичными данными. Вычисления с плавающей точкой не используются; процесс представляет собой чистую дискретную целочисленную арифметику.
- **TSA (Time Stamp Authority)**: Независимая доверенная третья сторона, выдающая криптографически подписанные метки времени.
- **CustodyRecord (Регистр хранения)**: Неизменяемая запись, документирующая, кто и когда обращался с уликой.
- **HMAC**: Локальная криптографическая контрольная сумма, подтверждающая, что данные не изменились с момента их последней обработки локальной системой.
- **Токен RFC 3161**: Подписанная структура данных, доказывающая, что конкретный цифровой хеш существовал в определённый момент времени.
- **Детерминированная целочисленная арифметика**: Математические операции над целыми числами (битами), которые всегда дают точно такой же результат при тех же условиях, без ошибок округления или приближений.

### 【Научное примечание】

Следовательская терминология, используемая в данном модуле, время от времени заимствует из семиотики — в частности, из концепций **Пирса**, **Эко** и **Грайса** — чтобы описать, как цифровое доказательство «означает» целостность. Это не мистицизм.

Воспринимайте **знак** (в пирсовском смысле) как **показание датчика**: термометр не «означает» температуру по магии; он производит индексальный знак посредством детерминированного физического процесса. Коды Эко аналогичны **протоколам калибровки**, которые отображают сырые выходные сигналы датчика на интерпретируемые единицы. Максимы Грайса функционируют как **критерии контроля качества** передачи данных — гарантируя, что то, что передатчик (производитель доказательства) сообщает, столь же информативно, достоверно и релевантно, как показания хорошо откалиброванного прибора.

Следовательно, когда мы называем токен RFC 3161 «индексальным знаком» существования в данный момент, мы лишь констатируем, что TSA действует как независимое измерительное устройство — как сертифицированные часы, показания которых зафиксированы в неизменяемом целочисленном регистре. В арифметике нет интерпретационной неоднозначности; хеш — это детерминированное целое число, подпись — детерминированное целочисленное отношение, а метка времени — дискретная метка.

---

## 中文

### 本模块是什么？

本模块 `vigia/forensics/rfc3161_chain.py` 相当于一本经过公证的数字化实验室日志。它通过向独立的时间戳机构（TSA）申请加密证明，为数字取证工件生成防篡改的时间戳。内部HMAC封印的含义是"自本系统处理该文件以来，它未被改动"；而RFC 3161封印的含义则是"在确切的时间点，有独立第三方见证了该文件的指纹"。对于Daubert等法律与科学标准而言，这一区别至关重要：它类似于研究者自证其数据，与由外部审计员进行认证之间的差别。本模块采用基于确定性整数运算的指纹算法（SHA-256与SHA-512），并将结果存入创建后不可更改的冻结记录中。

### 核心概念

| 概念 | 说明 | 科学等效物 |
|---|---|---|
| RFC 3161 | 互联网可信时间戳标准 | 经ISO 17025认证的实验室时钟及审计追踪 |
| TSA (Time Stamp Authority) | 通过加密方式将哈希值与时间点绑定的独立服务器 | 外部校准实验室，验证测量发生的时间 |
| `CustodyRecord` | 不可变的冻结数据类，存储封印信息 | 实验室永久日志条目 |
| `RFC3161Timestamper` | 管理与TSA通信并构建证据封印的引擎 | 自动化管线操作员 |
| `seal_artifact()` | 按优先顺序向TSA请求时间戳；若全部失败，则使用明确声明非独立见证的本地回退方案 | 应用公证封印；若公证人缺席，则使用标注为"未见证"的内部备忘录 |
| `export_chain()` | 导出完整的保管链以附入最终报告包 | 将所有公证收据汇编至主附录 |
| `verify_chain_integrity()` | 逐条校验本地HMAC以确认记录未被篡改，从而识别证据链中的任何逻辑断裂；注意：不验证TSA签名 | 运行内部诊断以发现仪器日志中的逻辑断裂 |
| SHA-256 / SHA-512 | 基于确定性整数位运算的加密哈希函数 | 分析指纹（确定性，无浮点运算） |
| HMAC | 本地完整性校验 | 实验室内部天平的自检程序 |
| `NOT_INDEPENDENT_WITNESS` | 本地回退令牌中的明确声明，防止被误认为第三方证词 | 诚实声明"此测量未经外部审计员观察"的实验室备注 |
| Daubert标准 | 美国科学证据可采性的法律标准 | 用于法庭的同行评审与可重复性标准 |

### 术语表

- **哈希值 (SHA-256/512)**: 通过对二进制数据进行按位逻辑运算而生成的、长度固定的确定性整数指纹。不使用浮点运算；整个过程纯粹是离散整数算术。
- **TSA (时间戳机构)**: 独立可信的第三方，负责签发加密签名的时间戳。
- **保管记录 (CustodyRecord)**: 不可变的日志条目，记录谁、在何时接触过取证工件。
- **HMAC**: 本地加密校验和，用于证明自本地系统上次处理以来，数据未被改动。
- **RFC 3161令牌**: 一种已签名的数据结构，证明某个特定数字哈希在某一确切时间点已经存在。
- **确定性整数算术**: 对整数（比特）进行的数学运算，在相同条件下总是产生完全相同的结果，不存在舍入误差或近似值。

### 【科学说明】

本模块所使用的取证词汇偶尔借鉴自符号学——尤其是**皮尔斯**、**艾柯**与**格赖斯**的理论框架——以描述数字证据如何"意指"完整性。这并非神秘主义。

请将**符号**（皮尔斯意义上的）视为一种**传感器读数**：温度计并非凭借魔法来"意指"温度；它通过确定性物理过程产生一个指示性符号。艾柯的"代码"类似于**校准协议**，将传感器的原始输出映射为可解释的单位。格赖斯的"准则"则相当于数据传输的**质控标准**——确保证据发送者（取证工件的生成方）所传达的信息如同一台经过良好校准的仪器所报告的那样，具有充分的信息量、真实性与相关性。

因此，当我们将RFC 3161令牌称为某一时刻存在性的"指示性符号"时，我们仅仅是在陈述：TSA充当了一台独立的测量装置——如同一台经过认证的时钟，其读数被冻结成一条不可变的整数记录。算术层面不存在解释上的歧义；哈希是确定性整数，签名是确定性的整数关系，而时间戳则是一个离散标签。

---

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
