<!--
VIGIA Academic Documentation
Module: 6599e8ef
Batch ID: vigia-doc-0080-6599e8ef
Generated: 2026-05-20T14:56:47.861777+00:00
-->

# Module Documentation: `vigia/core/trust_levels.py`

---

## ENGLISH

### What Is This Module?

This module, located at `vigia/core/trust_levels.py`, is a deterministic, open-source software simulator of the Chinese cybersecurity standard *等保2.0* (Multi-Level Protection Scheme 2.0, MLPS 2.0) Levels 1 through 4. It substitutes physical Trusted Platform Modules (TPM/TCM) with a transparent, deterministic HMAC-SHA256 integrity anchor. For researchers who do not program: imagine a digital laboratory protocol that enforces an unbroken chain-of-custody for computational evidence. Every operation relies on exact integer arithmetic—there are no approximations, no rounding operations, and no floating-point uncertainties.

### Key Concepts

| Concept | Description | Deterministic Guarantee |
|---|---|---|
| **TrustLevel** | An ordinal classification (1–4) representing the depth of verification. Analogous to biosafety laboratory levels. | Discrete integer levels only; no fractional or transitional states exist. |
| **TrustedRoot** | The cryptographic origin point (*可信根*). Comparable to a tamper-evident seal on an evidence bag. | HMAC-SHA256 computed over exact byte-integer sequences; any alteration yields a different integer fingerprint. |
| **VerificationCheckpoint** | Specific execution moments where integrity is tested (Level 3+). Like quality-control stops on a production line. | Pass/fail outcome derived from exact integer hash comparison. |
| **AuditLog** | A centralized, append-only record store (*安全管理中心*). Comparable to a permanently bound laboratory notebook with numbered pages. | Records are linked via deterministic integer chain hashes; any tampering breaks the chain. |
| **DynamicCorrelationEvent** | A structured observation used to detect cross-event patterns (Level 4). Like correlating readings from multiple instruments. | Timestamp and event-ID integers; correlation via exact matching. |
| **TrustLevelVerifier** | The engine that routes a specimen through Levels 1–4. Like a robotic pipeline operator. | State transitions governed by integer logic. |

### Constants

| Constant | Scientific Meaning |
|---|---|
| LEVEL_1 – LEVEL_4 | The four discrete assurance tiers. |
| BOOT_START, BOOT_VERIFY_KERNEL, BOOT_COMPLETE | Boot-sequence checkpoints (simulated TCM boot chain). |
| ANALYSIS_INIT, ANALYSIS_SIGNAL_RECEPTION, ANALYSIS_INFERENCE | Runtime checkpoints for forensic pipeline stages. |

### Functions

| Function | Role |
|---|---|
| create_trusted_root() | Generates a new root of trust (simulated TPM initialization). |
| verify_integrity() | Confirms the root or log has not been altered by recomputing the HMAC-SHA256 digest. |
| add_record() | Appends an entry to the AuditLog and updates the chain hash deterministically. |
| verify_level_1() to verify_level_4() | Progressive verification protocols corresponding to MLPS 2.0 tiers. |
| verify() | Unified entry point; selects the protocol tier by integer level. |

### 【Scientific Note】

References to Peirce, Eco, and Grice in forensic-engineering contexts are semiotic and pragmatic instruments, not metaphysical doctrines.

- Peirce's Thirdness is not mysticism; it is the formal equivalent of multi-sensor data fusion. If Firstness is the raw voltage from a single transducer, and Secondness is the event of that voltage crossing a threshold, then Thirdness is the deterministic correlation network that interprets coincident signals from many transducers as a single pattern (e.g., locating an earthquake epicenter from seismometer arrays). Level 4 of this module implements exactly that: deterministic correlation of discrete integer events.
- Eco's semiotics is the study of how a signal becomes a sign. In sensor terms, Eco describes how a frequency encoding is mapped to a meaning—no different from how a chromatogram peak maps to a compound identity.
- Grice's maxims are communication protocols. For sensors, they are quality-control rules on data transmission: report truthfully (Quality), report exactly what is needed (Quantity), stay on topic (Relation), and format clearly (Manner).

These frameworks provide an epistemological grammar for digital evidence; they do not invoke the supernatural.

### Glossary

- **Deterministic Integer Arithmetic**: Calculations using whole numbers (integers) in which the same inputs always produce the same outputs, with no rounding or approximation.
- **HMAC-SHA256**: A keyed hash function that produces a fixed-length integer fingerprint from data; any alteration changes the fingerprint.
- **Chain Hash**: A method where each new record incorporates the hash of the previous record, creating an unbreakable deterministic sequence.
- **等保2.0 (MLPS 2.0)**: China's Multi-Level Protection Scheme, version 2.0, a regulatory framework for information security.
- **TCM**: Trusted Cryptography Module, the Chinese hardware standard analogous to TPM.
- **可信根 (Trusted Root)**: The foundational cryptographic key or measurement from which all trust in a system is derived.
- **动态关联感知 (Dynamic Correlation Perception)**: The systematic detection of patterns across multiple discrete events in time.

---

## ESPAÑOL

### ¿Qué es este módulo?

Este módulo es un simulador determinista de código abierto del estándar chino de ciberseguridad 等保2.0 (MLPS 2.0) Niveles 1 a 4. Reemplaza los Módulos de Plataforma Confiable físicos (TPM/TCM) por un ancla de integridad transparente y determinista basada en HMAC-SHA256. Para científicos no programadores: piensen en este módulo como un protocolo de laboratorio digital que impone una cadena de custodia para evidencia computacional. Cada operación utiliza aritmética entera exacta: sin aproximaciones, sin redondeos, sin errores de punto flotante.

### Conceptos Clave

| Concepto | Descripción | Garantía Determinista |
|---|---|---|
| **TrustLevel** | Clasificación ordinal (1–4) que representa la profundidad de verificación. Análogo a los niveles de bioseguridad de un laboratorio. | Niveles enteros discretos únicamente; no existen estados fraccionarios o transicionales. |
| **TrustedRoot** | Punto de origen criptográfico (*可信根*). Comparable a un sello inviolable en una bolsa de evidencias. | HMAC-SHA256 calculado sobre secuencias de bytes enteros exactos; cualquier alteración produce una huella diferente. |
| **VerificationCheckpoint** | Momentos específicos de ejecución donde se prueba la integridad (Nivel 3+). Como paradas de control de calidad en una línea de producción. | Resultado de pase/fallo derivado de comparación exacta de hashes enteros. |
| **AuditLog** | Almacén centralizado de registros de solo adición (*安全管理中心*). Comparable a un cuaderno de laboratorio permanentemente encuadernado con páginas numeradas. | Los registros se vinculan mediante hashes de cadena deterministas; cualquier manipulación rompe la cadena. |
| **DynamicCorrelationEvent** | Observación estructurada usada para detectar patrones entre eventos (Nivel 4). Como correlacionar lecturas de múltiples instrumentos. | Enteros de marca temporal e ID de evento; correlación mediante coincidencia exacta. |
| **TrustLevelVerifier** | Motor que enruta una muestra a través de los Niveles 1–4. Como un operador robótico de línea. | Transiciones de estado gobernadas por lógica entera. |

### Constantes

| Constante | Significado Científico |
|---|---|
| LEVEL_1 – LEVEL_4 | Los cuatro niveles discretos de garantía. |
| BOOT_START, BOOT_VERIFY_KERNEL, BOOT_COMPLETE | Puntos de control de secuencia de arranque (cadena TCM simulada). |
| ANALYSIS_INIT, ANALYSIS_SIGNAL_RECEPTION, ANALYSIS_INFERENCE | Puntos de control en tiempo de ejecución para etapas del pipeline forense. |

### Funciones

| Función | Rol |
|---|---|
| create_trusted_root() | Genera una nueva raíz de confianza (inicialización TPM simulada). |
| verify_integrity() | Confirma que la raíz o el log no ha sido alterado recalculando el resumen HMAC-SHA256. |
| add_record() | Añade una entrada al AuditLog y actualiza el hash de cadena de forma determinista. |
| verify_level_1() a verify_level_4() | Protocolos de verificación progresiva correspondientes a los niveles MLPS 2.0. |
| verify() | Punto de entrada unificado; selecciona el nivel de protocolo por nivel entero. |

### 【Nota Científica】

Las referencias a Peirce, Eco y Grice en ingeniería forense son instrumentos semióticos y pragmáticos, no doctrinas metafísicas.

- La Terceridad de Peirce no es misticismo; es el equivalente formal de la fusión de datos multi-sensor. Si la Primeridad es el voltaje crudo de un transductor, y la Secundariedad es el evento de que ese voltaje cruce un umbral, entonces la Terceridad es la red de correlación determinista que interpreta señales coincidentes de muchos transductores como un patrón único (por ejemplo, localizar el epicentro de un terremoto a partir de redes sismográficas). El Nivel 4 de este módulo implementa exactamente eso: correlación determinista de eventos enteros discretos.
- La semiótica de Eco es el estudio de cómo una señal se convierte en signo. En términos de sensores, Eco describe cómo una codificación de frecuencia se mapea a un significado—no difiere de cómo un pico cromatográfico se mapea a la identidad de un compuesto.
- Los máximas de Grice son protocolos de comunicación. Para sensores, son reglas de control de calidad en la transmisión de datos: reportar verazmente (Calidad), reportar exactamente lo necesario (Cantidad), mantenerse en el tema (Relación) y formatear con claridad (Modo).

Estos marcos proporcionan una gramática epistemológica para la evidencia digital; no invocan lo sobrenatural.

### Glosario

- **Aritmética entera determinista**: Cálculos con números enteros donde los mismos insumos siempre producen los mismos resultados, sin redondeo ni aproximación.
- **HMAC-SHA256**: Función hash con clave que produce una huella dactilar de longitud fija a partir de datos; cualquier alteración cambia la huella.
- **Hash de cadena**: Método donde cada nuevo registro incorpora el hash del anterior, creando una secuencia determinista inquebrantable.
- **等保2.0 (MLPS 2.0)**: Esquema de Protección Multi-Nivel de China, versión 2.0, marco regulatorio de seguridad de la información.
- **TCM**: Módulo de Criptografía Confiable, estándar de hardware chino análogo al TPM.
- **可信根 (Raíz de Confianza)**: Clave o medición criptográfica fundacional de la que se deriva toda la confianza en un sistema.
- **动态关联感知 (Percepción de Correlación Dinámica)**: Detección sistemática de patrones a través de múltiples eventos discretos en el tiempo.

---

## РУССКИЙ

### Что представляет собой этот модуль?

Этот модуль — детерминированный программный симулятор с открытым исходным кодом, реализующий китайский стандарт кибербезопасности 等保2.0 (MLPS 2.0) уровней 1–4. Он заменяет физические доверенные платформенные модули (TPM/TCM) прозрачным детерминированным якорем целостности на основе HMAC-SHA256. Для учёных, не знакомых с программированием: представьте этот модуль как цифровой лабораторный протокол, обеспечивающий цепочку сохранности для компьютерных доказательств. Каждая операция использует точную целочисленную арифметику: без приближений, округлений и ошибок плавающей запятой.

### Ключевые концепции

| Концепция | Описание | Детерминированная гарантия |
|---|---|---|
| **TrustLevel** | Порядковая классификация (1–4), представляющая глубину верификации. Аналог уровней биологической безопасности в лаборатории. | Только дискретные целочисленные уровни; дробных или переходных состояний не существует. |
| **TrustedRoot** | Криптографическая точка происхождения (*可信根*). Сравнима с защищённой от вскрытия пломбой на пакете с уликами. | HMAC-SHA256, вычисленный над точными байт-целочисленными последовательностями; любое изменение даёт другой отпечаток. |
| **VerificationCheckpoint** | Конкретные моменты выполнения, где проверяется целостность (Уровень 3+). Как остановки контроля качества на производственной линии. | Результат прохождения/непрохождения, производный из точного сравнения целочисленных хэшей. |
| **AuditLog** | Централизованное хранилище записей только для добавления (*安全管理中心*). Сравнимо с постоянно переплётным лабораторным журналом с номерами страниц. | Записи связаны через детерминированные цепочечные хэши; любая подделка разрывает цепочку. |
| **DynamicCorrelationEvent** | Структурированное наблюдение для обнаружения паттернов между событиями (Уровень 4). Как корреляция показаний нескольких приборов. | Целые числа меток времени и идентификаторов событий; корреляция через точное сопоставление. |
| **TrustLevelVerifier** | Движок, маршрутизирующий образец через Уровни 1–4. Как роботизированный оператор конвейера. | Переходы состояний управляются целочисленной логикой. |

### Константы

| Константа | Научное значение |
|---|---|
| LEVEL_1 – LEVEL_4 | Четыре дискретных уровня гарантии. |
| BOOT_START, BOOT_VERIFY_KERNEL, BOOT_COMPLETE | Контрольные точки последовательности загрузки (симулированная TCM цепочка загрузки). |
| ANALYSIS_INIT, ANALYSIS_SIGNAL_RECEPTION, ANALYSIS_INFERENCE | Контрольные точки времени выполнения для этапов судебного конвейера. |

### Функции

| Функция | Роль |
|---|---|
| create_trusted_root() | Генерирует новый корень доверия (симулированная инициализация TPM). |
| verify_integrity() | Подтверждает, что корень или журнал не изменены, пересчитывая дайджест HMAC-SHA256. |
| add_record() | Добавляет запись в AuditLog и детерминированно обновляет цепочечный хэш. |
| verify_level_1() – verify_level_4() | Прогрессивные протоколы верификации, соответствующие уровням MLPS 2.0. |
| verify() | Единая точка входа; выбирает уровень протокола по целочисленному уровню. |

### 【Научное Примечание】

Ссылки на Пирса, Эко и Грайса в контексте судебной инженерии являются семиотическими и прагматическими инструментами, а не метафизическими доктринами.

- Третичность (Thirdness) Пирса — это не мистицизм; это формальный аналог мультисенсорной интеграции данных. Если Первичность — это сырой вольтаж одного датчика, а Вторичность — событие пересечения этим вольтажом порога, то Третичность — это детерминированная корреляционная сеть, которая интерпретирует совпадающие сигналы множества датчиков как единый паттерн (например, определение эпицентра землетрясения по сейсмографической сети). Уровень 4 данного модуля реализует именно это: детерминированную корреляцию дискретных целочисленных событий.
- Семиотика Эко изучает, как сигнал становится знаком. В терминах датчиков Эко описывает, как частотное кодирование отображается на значение — точно так же, как пик хроматограммы отображается на идентичность соединения.
- Максимы Грайса — это коммуникационные протоколы. Для датчиков они являются правилами контроля качества при передаче данных: сообщать правдиво (Качество), сообщать ровно столько, сколько нужно (Количество), оставаться в рамках темы (Отношение) и оформлять ясно (Манера).

Эти рамки задают эпистемологическую грамматику для цифровых доказательств; они не апеллируют к сверхъестественному.

### Глоссарий

- **Детерминированная целочисленная арифметика**: Вычисления с целыми числами, при которых одни и те же входные данные всегда дают одинаковый результат без округления или приближения.
- **HMAC-SHA256**: Ключевая хэш-функция, создающая фиксированный целочисленный отпечаток из данных; любое изменение данных изменяет отпечаток.
- **Цепочка хэшей**: Метод, при котором каждая новая запись включает хэш предыдущей, создавая неразрывную детерминированную последовательность.
- **等保2.0 (MLPS 2.0)**: Китайская многоуровневая схема защиты, версия 2.0, регуляторная рамка информационной безопасности.
- **TCM**: Доверенный криптографический модуль, китайский аппаратный стандарт, аналогичный TPM.
- **可信根 (Доверенный корень)**: Фундаментальный криптографический ключ или измерение, от которого происходит всё доверие к системе.
- **动态关联感知 (Динамическое корреляционное восприятие)**: Систематическое обнаружение паттернов среди множества дискретных событий во времени.

---

## 中文

### 本模块是什么？

本模块是等保2.0（MLPS 2.0）第一级至第四级的确定性开源软件模拟器。它以透明且确定性的HMAC-SHA256完整性锚点替代了物理可信平台模块（TPM/TCM）。对于不熟悉Python的科研人员：请将本模块理解为一种数字实验室协议，用于对计算取证工件执行监管链控制。所有操作均使用精确的整数运算——无近似、无舍入、无浮点误差。

### 核心概念

| 概念 | 说明 | 确定性保障 |
|---|---|---|
| 信任等级 (TrustLevel) | 表示验证深度的序数分类（1–4）。类似于实验室生物安全等级。 | 整数等级；不存在分数状态。 |
| 可信根 (TrustedRoot) | 加密起源点。类似于证物袋上的防拆封条。 | 基于精确字节整数序列的HMAC-SHA256。 |
| 验证检查点 (VerificationCheckpoint) | 分析过程中测试完整性的关键时刻（第三级及以上）。类似生产线上的质控停检点。 | 由整数哈希比较得出的布尔通过/未通过。 |
| 审计日志 (AuditLog) | 集中式、仅追加的记录存储（安全管理中心）。类似带有页码的装订实验记录本。 | 通过确定性整数累积的链式哈希链接记录。 |
| 动态关联事件 (DynamicCorrelationEvent) | 用于检测跨事件模式的结构化观察（第四级）。类似多仪器读数关联。 | 时间戳与事件标识符均为整数；通过精确匹配进行关联。 |
| 信任等级验证引擎 (TrustLevelVerifier) | 将取证工件送入第一至第四级处理的引擎。类似自动化管线操作员。 | 状态转移由整数逻辑控制。 |

### 常量

| 常量 | 科学含义 |
|---|---|
| LEVEL_1 – LEVEL_4 | 四个离散保障层级。 |
| BOOT_START, BOOT_VERIFY_KERNEL, BOOT_COMPLETE | 引导序列检查点（模拟TCM引导链）。 |
| ANALYSIS_INIT, ANALYSIS_SIGNAL_RECEPTION, ANALYSIS_INFERENCE | 取证管线各运行阶段的检查点。 |

### 函数

| 函数 | 作用 |
|---|---|
| create_trusted_root() | 生成新的可信根（模拟TPM初始化）。 |
| verify_integrity() | 通过重新计算HMAC-SHA256摘要，确认可信根或日志未被篡改。 |
| add_record() | 向审计日志追加条目，并以确定性方式更新链式哈希。 |
| verify_level_1() 至 verify_level_4() | 对应等保2.0各层级的渐进式验证协议。 |
| verify() | 统一入口；按整数等级选择协议层级。 |

### 【科学说明】

在取证工程语境中援引皮尔斯（Peirce）、艾柯与格赖斯，乃是作为符号学与语用学工具，而非形而上学教条。

- 皮尔斯的第三性（Thirdness）并非神秘主义；它是多传感器数据融合的形式等价物。若第一性是单个传感器的原始电压，第二性是该电压越过阈值的互动事件，则第三性是将多个传感器的并发信号确定性关联、解读为单一模式的网络（例如根据地震仪台网确定震中）。本模块第四级正是实现这一点：对离散整数事件进行确定性关联。
- 艾柯的符号学研究信号如何成为符号。以传感器类比，艾柯描述的是频率编码如何映射为意义——这与色谱峰映射为化合物身份并无不同。
- 格赖斯的准则属于交际协议。对于传感器而言，它们就是数据传输的质量控制规则：如实报告（质准则）、报告所需恰好信息（量准则）、紧扣主题（关系准则）、表达清晰（方式准则）。

这些框架为数字证据提供了认识论语法；它们并不诉诸超自然。

### 术语表

- **确定性整数运算**：使用整数进行计算，相同输入始终产生相同输出，无舍入或近似。
- **HMAC-SHA256**：一种带密钥的哈希函数，从数据生成固定长度的整数指纹；任何改动都会改变指纹。
- **链式哈希**：每条新记录纳入前一条记录的哈希值，形成不可中断的确定性序列。
- **等保2.0（MLPS 2.0）**：中国网络安全等级保护制度2.0版，信息安全监管框架。
- **TCM**：可信密码模块，中国硬件标准，类同于TPM。
- **可信根**：系统信任来源所依赖的基础加密密钥或度量值。
- **动态关联感知**：对多个时间离散事件进行系统性模式检测。
- **逻辑断裂**：确定性整数序列或证据链中出现的不一致或中断，表现为哈希值不匹配。

---

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
