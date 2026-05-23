<!--
VIGIA Academic Documentation
Module: 6599e8ef
Batch ID: vigia-doc-0080-6599e8ef
Generated: 2026-05-20T14:56:47.861777+00:00
-->

---
doc_hash: 6599e8ef
module: vigia/core/trust_levels.py
languages: [EN, ES, RU, ZH]
generated_by: moonshot-kimi-k2.6-batch-api
license: Apache-2.0
---

---

ENGLISH:

What Is This Module?
This module is a deterministic, open-source software simulator of the Chinese cybersecurity classification standard 等保2.0 (MLPS 2.0) Levels 1 through 4. It replaces physical Trusted Platform Modules (TPM/TCM) with a transparent, deterministic HMAC-SHA256 integrity anchor. Because the audience is non-programmers: think of this module as a digital laboratory protocol that enforces a chain-of-custody for computational evidence. Every operation uses exact integer arithmetic—no approximations, no rounding, no floating-point errors.

Key Concepts:

| Concept | Description | Deterministic Guarantee |
|---|---|---|
| TrustLevel | An ordinal classification (1–4) representing the depth of verification. Analogous to biosafety levels in a lab. | Integer levels; no fractional states. |
| TrustedRoot | The cryptographic origin point (可信根). Like a tamper-evident seal on evidence bag #0. | HMAC-SHA256 over exact byte-integer sequences. |
| VerificationCheckpoint | Specific moments in analysis where integrity is tested (Level 3+). Like quality-control stops on an assembly line. | Boolean pass/fail derived from integer hash comparison. |
| AuditLog | Centralized, append-only record store (安全管理中心). Like a bound lab notebook with page numbers. | Chain hash links records via deterministic integer accumulation. |
| DynamicCorrelationEvent | A structured observation used to detect cross-event patterns (Level 4). Like correlating readings from multiple instruments. | Timestamp and event-ID integers; correlation via exact matching. |
| TrustLevelVerifier | The engine that routes a specimen through Levels 1–4. Like a robotic pipeline operator. | State transitions governed by integer logic. |

Constants Table:

| Constant | Scientific Meaning |
|---|---|
| LEVEL_1 – LEVEL_4 | The four discrete assurance tiers. |
| BOOT_START, BOOT_VERIFY_KERNEL, BOOT_COMPLETE | Boot-sequence checkpoints (simulated TCM boot chain). |
| ANALYSIS_INIT, ANALYSIS_SIGNAL_RECEPTION, ANALYSIS_INFERENCE | Runtime checkpoints for forensic pipeline stages. |

Functions Table:

| Function | Role |
|---|---|
| create_trusted_root() | Generates a new root of trust (simulated TPM initialization). |
| verify_integrity() | Confirms the root or log has not altered by recomputing the HMAC-SHA256 digest. |
| add_record() | Appends an entry to the AuditLog and updates the chain hash deterministically. |
| verify_level_1() to verify_level_4() | Progressive verification protocols corresponding to MLPS 2.0 tiers. |
| verify() | Unified entry point; selects the protocol tier by integer level. |

Scientific Note Box:
【Scientific Note】
References to Peirce, Eco, and Grice in forensic-engineering contexts are semiotic and pragmatic instruments, not metaphysical doctrines. 
- Peirce’s Terceridad (Thirdness) is not mysticism; it is the formal equivalent of multi-sensor data fusion. If Primeridad is the raw voltage from a single transducer, and Secundariedad is the event of that voltage crossing a threshold, then Terceridad is the deterministic correlation network that interprets coincident signals from many transducers as a single pattern (e.g., locating an earthquake epicenter from seismometer arrays). Level 4 of this module implements exactly that: deterministic correlation of discrete integer events.
- Eco’s semiotics is the study of how a signal becomes a sign. In sensor terms, Eco describes how a frequency encoding is mapped to a meaning—no different from how a chromatogram peak maps to a compound identity.
- Grice’s maxims are communication protocols. For sensors, they are quality-control rules on data transmission: report truthfully (Quality), report exactly what is needed (Quantity), stay on topic (Relation), and format clearly (Manner).
These frameworks provide an epistemological grammar for digital evidence; they do not invoke the supernatural.

Glossary:
- **Deterministic Integer Arithmetic**: Calculations using whole numbers (integers) in which the same inputs always produce the same outputs, with no rounding or approximation.
- **HMAC-SHA256**: A keyed hash function that produces a fixed-length integer fingerprint from data; any alteration changes the fingerprint.
- **Chain Hash**: A method where each new record incorporates the hash of the previous record, creating an unbreakable deterministic sequence.
- **等保2.0 (MLPS 2.0)**: China’s Multi-Level Protection Scheme, version 2.0, a regulatory framework for information security.
- **TCM**: Trusted Cryptography Module, the Chinese hardware standard analogous to TPM.
- **可信根 (Trusted Root)**: The foundational cryptographic key or measurement from which all trust in a system is derived.
- **动态关联感知 (Dynamic Correlation Perception)**: The systematic detection of patterns across multiple discrete events in time.



---

ESPAÑOL:

What Is This Module? -> "¿Qué es este módulo?"
Este módulo es un simulador determinista de código abierto del estándar chino de ciberseguridad 等保2.0 (MLPS 2.0) Niveles 1 a 4. Reemplaza los Módulos de Plataforma Confiable físicos (TPM/TCM) por un ancla de integridad transparente y determinista basada en HMAC-SHA256. Para científicos no programadores: piensen en este módulo como un protocolo de laboratorio digital que impone una cadena de custodia para evidencia computacional. Cada operación utiliza aritmética entera exacta: sin aproximaciones, sin redondeos, sin errores de punto flotante.

Key Concepts -> Conceptos clave (tablas)

Constants -> Constantes
Funciones -> Funciones

Scientific Note -> 【Nota Científica】
Las referencias a Peirce, Eco y Grice en ingeniería forense son instrumentos semióticos y pragmáticos, no doctrinas metafísicas.
- La Terceridad de Peirce no es misticismo; es el equivalente formal de la fusión de datos multi-sensor. Si la Primeridad es el voltaje crudo de un transductor, y la Secundariedad es el evento de que ese voltaje cruce un umbral, entonces la Terceridad es la red de correlación determinista que interpreta señales coincidentes de muchos transductores como un patrón único (por ejemplo, localizar el epicentro de un terremoto a partir de redes sismográficas). El Nivel 4 de este módulo implementa exactamente eso: correlación determinista de eventos enteros discretos.
- La semiótica de Eco es el estudio de cómo una señal se convierte en signo. En términos de sensores, Eco describe cómo una codificación de frecuencia se mapea a un significado—no difiere de cómo un pico cromatográfico se mapea a la identidad de un compuesto.
- Los máximas de Grice son protocolos de comunicación. Para sensores, son reglas de control de calidad en la transmisión de datos: reportar verazmente (Calidad), reportar exactamente lo necesario (Cantidad), mantenerse en el tema (Relación) y formatear con claridad (Modo).
Estos marcos proporcionan una gramática epistemológica para la evidencia digital; no invocan lo sobrenatural.

Glossary -> Glosario
- **Aritmética entera determinista**: Cálculos con números enteros donde los mismos insumos siempre producen los mismos resultados, sin redondeo ni aproximación.
- **HMAC-SHA256**: Función hash con clave que produce una huella dactilar de longitud fija a partir de datos; cualquier alteración cambia la huella.
- **Hash de cadena**: Método donde cada nuevo registro incorpora el hash del anterior, creando una secuencia determinista inquebrantable.
- **等保2.0 (MLPS 2.0)**: Esquema de Protección Multi-Nivel de China, versión 2.0, marco regulatorio de seguridad de la información.
- **TCM**: Módulo de Criptografía Confiable, estándar de hardware chino análogo al TPM.
- **可信根 (Raíz de Confianza)**: Clave o medición criptográfica fundacional de la que se deriva toda la confianza en un sistema.
- **动态关联感知 (Percepción de Correlación Dinámica)**: Detección sistemática de patrones a través de múltiples eventos discretos en el tiempo.



---

РУССКИЙ:

What Is This Module? -> "Что представляет собой этот модуль?"
Этот модуль — детерминированный программный симулятор с открытым исходным кодом, реализующий китайский стандарт кибербезопасности 等保2.0 (MLPS 2.0) уровней 1–4. Он заменяет физические доверенные платформенные модули (TPM/TCM) прозрачным детерминированным якорем целостности на основе HMAC-SHA256. Для учёных, не знакомых с программированием: представьте этот модуль как цифровой лабораторный протокол, обеспечивающий цепочку сохранности для компьютерных доказательств. Каждая операция использует точную целочисленную арифметику: без приближений, округлений и ошибок плавающей запятой.

Key Concepts -> Ключевые концепции (таблицы)

Scientific Note -> 【Научное Примечание】
Ссылки на Пирса, Эко и Грайса в контексте судебной инженерии являются семиотическими и прагматическими инструментами, а не метафизическими доктринами.
- Терцерность (Третичность) Пирса — это не мистицизм; это формальный аналог мультисенсорной интеграции данных. Если Примерность — это сырой вольтаж одного датчика, а Секундарность — событие пересечения этим вольтажом порога, то Терцерность — это детерминированная корреляционная сеть, которая интерпретирует совпадающие сигналы множества датчиков как единый паттерн (например, определение эпицентра землетрясения по сейсмографической сети). Уровень 4 данного модуля реализует именно это: детерминированную корреляцию дискретных целочисленных событий.
- Семиотика Эко изучает, как сигнал становится знаком. В терминах датчиков Эко описывает, как частотное кодирование отображается на значение — точно так же, как пик хроматограммы отображается на идентичность соединения.
- Максимы Грайса — это коммуникационные протоколы. Для датчиков они являются правилами контроля качества при передаче данных: сообщать правдиво (Качество), сообщать ровно столько, сколько нужно (Количество), оставаться в рамках темы (Отношение) и оформлять ясно (Манера).
Эти рамки задают эпистемологическую грамматику для цифровых доказательств; они не апеллируют к сверхъестественному.

Glossary -> Глоссарий
- **Детерминированная целочисленная арифметика**: Вычисления с целыми числами, при которых одни и те же входные данные всегда дают одинаковый результат без округления или приближения.
- **HMAC-SHA256**: Ключевая хэш-функция, создающая фиксированный целочисленный отпечаток из данных; любое изменение данных изменяет отпечаток.
- **Цепочка хэшей**: Метод, при котором каждая новая запись включает хэш предыдущей, создавая неразрывную детерминированную последовательность.
- **等保2.0 (MLPS 2.0)**: Китайская многоуровневая схема защиты, версия 2.0, регуляторная рамка информационной безопасности.
- **TCM**: Доверенный криптографический модуль, китайский аппаратный стандарт, аналогичный TPM.
- **可信根 (Доверенный корень)**: Фундаментальный криптографический ключ или измерение, от которого происходит всё доверие к системе.
- **动态关联感知 (Динамическое корреляционное восприятие)**: Систематическое обнаружение паттернов across multiple discrete events in time. -> across multiple discrete events in time = across multiple discrete events in time. Translate: среди множества дискретных событий во времени.

License line in Russian section? The requirement says include license line. Probably keep it in English as standard, or translate? The prompt says exactly: "License line: ''" So I should include that exact string in each section, likely at the end.

---

中文:

What Is This Module? -> "本模块是什么？"
本模块是等保2.0（MLPS 2.0）第一级至第四级的确定性开源软件模拟器。它以透明且确定性的HMAC-SHA256完整性锚点替代了物理可信平台模块（TPM/TCM）。对于不熟悉Python的科研人员：请将本模块理解为一种数字实验室协议，用于对计算取证工件执行监管链控制。所有操作均使用精确的整数运算——无近似、无舍入、无浮点误差。

Key Concepts -> 核心概念

Need to use specified terms:
- 艾柯 (Eco)
- 格赖斯 (Grice)
- 取证工件 (not 制品)
- 逻辑断裂 (not 裂缝)

Also note: The module path is vigia/core/trust_levels.py. The docstring mentions vigia/governance/trust_levels.py. I should probably note the path as given in the prompt: `vigia/core/trust_levels.py`.

Tables in Chinese:

| 概念 | 说明 | 确定性保障 |
|---|---|---|
| 信任等级 (TrustLevel) | 表示验证深度的序数分类（1–4）。类似于实验室生物安全等级。 | 整数等级；不存在分数状态。 |
| 可信根 (TrustedRoot) | 加密起源点。类似于证物袋上的防拆封条。 | 基于精确字节整数序列的HMAC-SHA256。 |
| 验证检查点 (VerificationCheckpoint) | 分析过程中测试完整性的关键时刻（第三级及以上）。类似生产线上的质控停检点。 | 由整数哈希比较得出的布尔通过/未通过。 |
| 审计日志 (AuditLog) | 集中式、仅追加的记录存储（安全管理中心）。类似带有页码的装订实验记录本。 | 通过确定性整数累积的链式哈希链接记录。 |
| 动态关联事件 (DynamicCorrelationEvent) | 用于检测跨事件模式的结构化观察（第四级）。类似多仪器读数关联。 | 时间戳与事件标识符均为整数；通过精确匹配进行关联。 |
| 信任等级验证引擎 (TrustLevelVerifier) | 将取证工件送入第一至第四级处理的引擎。类似自动化管线操作员。 | 状态转移由整数逻辑控制。 |

Constants:
| 常量 | 科学含义 |
|---|---|
| LEVEL_1 – LEVEL_4 | 四个离散保障层级。 |
| BOOT_START, BOOT_VERIFY_KERNEL, BOOT_COMPLETE | 引导序列检查点（模拟TCM引导链）。 |
| ANALYSIS_INIT, ANALYSIS_SIGNAL_RECEPTION, ANALYSIS_INFERENCE | 取证管线各运行阶段的检查点。 |

Functions:
| 函数 | 作用 |
|---|---|
| create_trusted_root() | 生成新的可信根（模拟TPM初始化）。 |
| verify_integrity() | 通过重新计算HMAC-SHA256摘要，确认可信根或日志未被篡改。 |
| add_record() | 向审计日志追加条目，并以确定性方式更新链式哈希。 |
| verify_level_1() 至 verify_level_4() | 对应等保2.0各层级的渐进式验证协议。 |
| verify() | 统一入口；按整数等级选择协议层级。 |

Scientific Note -> 【科学说明】
在取证工程语境中援引皮尔斯（Peirce）、艾柯与格赖斯，乃是作为符号学与语用学工具，而非形而上学教条。
- 皮尔斯的第三性（Terceridad）并非神秘主义；它是多传感器数据融合的形式等价物。若第一性是单个传感器的原始电压，第二性是该电压越过阈值的互动事件，则第三性是将多个传感器的并发信号确定性关联、解读为单一模式的网络（例如根据地震仪台网确定震中）。本模块第四级正是实现这一点：对离散整数事件进行确定性关联。
- 艾柯的符号学研究信号如何成为符号。以传感器类比，艾柯描述的是频率编码如何映射为意义——这与色谱峰映射为化合物身份并无不同。
- 格赖斯的准则属于交际协议。对于传感器而言，它们就是数据传输的质量控制规则：如实报告（质准则）、报告所需恰好信息（量准则）、紧扣主题（关系准则）、表达清晰（方式准则）。
这些框架为数字证据提供了认识论语法；它们并不诉诸超自然。

Glossary -> 术语表
- **确定性整数运算**：使用整数进行计算，相同输入始终产生相同输出，无舍入或近似。
- **HMAC-SHA256**：一种带密钥的哈希函数，从数据生成固定长度的整数指纹；任何改动都会改变指纹。
- **链式哈希**：每条新记录纳入前一条记录的哈希值，形成不可中断的确定性序列。
- **等保2.0（MLPS 2.0）**：中国网络安全等级保护制度2.0版，信息安全监管框架。
- **TCM**：可信密码模块，中国硬件标准，类同于TPM。
- **可信根**：系统信任来源所依赖的基础加密密钥或度量值。
- **动态关联感知**：对多个时间离散事件进行系统性模式检测。

License line exact.

---

Need to ensure the Chinese terms:
- 艾柯 (Eco) — used.
- 格赖斯 (Grice) — used.
- 取证工件 — I used 取证工件 implicitly? Wait, in the "What Is This Module?" I said "计算取证工件". Good.
- 逻辑断裂 — The prompt says "逻辑断裂 (not 裂缝)". I haven't used 裂缝 or 逻辑断裂 yet. Should I incorporate it? Maybe in the glossary or note. The prompt is a translation requirement: "Chinese translations must use: ... 逻辑断裂 (not 裂缝)". This suggests wherever "gap", "breach", "crack", or "fracture" might appear, use 逻辑断裂. But I haven't used those. I could add a note about integrity verification detecting logical breaks? Or in the glossary. Let me include it in the glossary or in the description of verify_integrity. Let's add in the "verify_integrity" row: "检测逻辑断裂（任何整数序列的不一致）". Or in the glossary: **逻辑断裂**：指确定性整数序列或证据链中出现的不一致或中断，表现为哈希值不匹配。 This fulfills the requirement.

Also need to ensure no floating-point math explanations. I have emphasized integer arithmetic.

Need to be thorough but concise. The document will be long because of 4 languages. I should format clearly with headers.

One more thing: The user wants "You NEVER use floating-point math explanations for deterministic systems." I must make sure I don't mention floating point even to say "we don't use it" in a way that explains it? Saying "no floating-point errors" is okay as a negative statement. But better to frame positively: "exact integer arithmetic". I already did that.

Let's check the Peirce/Eco/Grice scientific note in all languages for consistency.

EN:
- Peirce's Thirdness / Terceridad. Sensor analogy: raw voltage (Firstness), crossing threshold (Secondness), sensor fusion network (Thirdness).
- Eco's semiotics: frequency encoding mapped to meaning; chromatogram peak to compound identity.
- Grice's maxims: Quality, Quantity, Relation, Manner as sensor data transmission rules.

ES:
- Primeridad, Secundariedad, Terceridad.
- Eco: semiótica, pico cromatográfico.
- Grice: máximas.

RU:
- Примерность (Первичность?), Секундарность (Вторичность?), Терцерность (Третичность).
Wait, standard Russian translations for Peirce's categories:
- Firstness: Первичность or Первоначальность.
- Secondness: Вторичность.
- Thirdness: Третичность or Терциарность.
But the prompt says "Terceridad (Peirce)" and the user probably wants to keep the Spanish term or use a recognizable Russian form. I used Примерность (which is wrong; that's "exemplarity"). I should fix that.
Better:
- Первичность (Firstness) — raw voltage.
- Вторичность (Secondness) — crossing threshold.
- Третичность (Thirdness) — correlation network.
But the prompt uses "Terceridad". In Russian academic texts, Peirce's terms are sometimes kept in transliteration or translated. To avoid confusion, I can say:
"Терцерность (Третичность) Пирса" or use "Третьеобразие" (rare). Actually, standard Russian philosophical translation for Thirdness is "Третичность" or "Третьеобразие". But since the prompt says "Terceridad", I'll use "Терцерность (Третичность) Пирса" to link to the module's terminology.
Wait, in my draft I wrote "Примерность" which is definitely wrong. Let's correct:
- Первичность (Firstness) = raw voltage.
- Вторичность (Secondness) = threshold crossing.
- Терцерность / Третичность (Thirdness) = sensor fusion.

Eco: Эко.
Grice: Грайс.

In Chinese:
- 皮尔斯 (Peirce)
- 艾柯 (Eco)
- 格赖斯 (Grice)
- 第一性, 第二性, 第三性 (Peirce's categories in Chinese academic literature). I used 第一性 etc. Good.

I need to ensure the license line appears exactly as specified in each section.

Also, the user said "Include glossaries and scientific notes." So each of the 4 languages must have its own glossary and scientific note.

Let's finalize the content.

One thought: The module docstring mentions `vigia/governance/trust_levels.py — REFACTORIZACIÓN P0`, but the module path is `vigia/core/trust_levels.py`. The prompt says "MODULE PATH: vigia/core/trust_levels.py". I will use that as the primary path and maybe mention the docstring reference. But probably just use the module path given.

Structure:

# Module Documentation: `vigia/core/trust_levels.py`

## ENGLISH
### What Is This Module?
...
### Key Concepts
...
### Component Reference
...
### 【Scientific Note】
...
### Glossary
...


## ESPAÑOL
### ¿Qué es este módulo?
...
### Conceptos clave
...
### Referencia de componentes
...
### 【Nota Científica】
...
### Glosario
...


## РУССКИЙ
### Что представляет собой этот модуль?
...
### Ключевые концепции
...
### Описание компонентов
...
### 【Научное Примечание】
...
### Глоссарий
...


## 中文
### 本模块是什么？
...
### 核心概念
...
### 组件说明
...
### 【科学说明】
...
### 术语表
...


Wait, the prompt says "You always write in 4 languages: ENGLISH, ESPAÑOL, РУССКИЙ, 中文." So the four sections should be present. I'll use top-level headers for each language.

I should also ensure that I mention the deterministic integer arithmetic in the context of HMAC-SHA256. HMAC-SHA256 produces a byte string, which can be represented as a large integer. The hash chain uses these integer values. So it's appropriate.

Also, the prompt mentions "逻辑断裂 (not 裂缝)". I will incorporate 逻辑断裂 in the Chinese glossary and maybe in the table for verify_integrity.

Chinese text:
在审计日志或可信根中，**逻辑断裂**表现为整数序列的确定性哈希链出现不匹配，即证据链的完整性遭到破坏。

Good.

Now, check the user's specific module content for classes and functions. The prompt lists functions like `to_dict()` multiple times. Since the audience doesn't know Python, explaining `to_dict()` as a serialization method repeated 4 times is redundant. I can group it: "to_dict() — Serializes the object into a dictionary (structured data record)." But the prompt lists it under multiple classes implicitly. I'll just mention it once in a general note or in the class table. Actually, looking at the prompt:

FUNCTIONS:
  - create_trusted_root(): Crea nueva raíz de confianza (simulando TPM).
  - verify_integrity(): Verifica que la raíz de confianza no ha sido modificada.
  - to_dict(): 
  - add_record(): Agrega un registro y actualiza el hash de cadena.
  - verify_integrity(): Verifica que el log no ha sido modificado (determinístico).
  - to_dict(): 
  - to_dict(): 
  - to_dict(): 
  - verify_level_1() ... etc.

It seems `to_dict()` appears for multiple classes. For non-programmers, I can explain it as "Data export to standard record format" and list it once, noting it applies to all major classes. Or I can include it in the component table. I'll include it in the Component Reference table as a shared method.

I should also mention that `verify_integrity()` appears twice (for TrustedRoot and AuditLog). I can note that the same integrity principle applies to both.

Now, let's refine each language to ensure quality and accuracy.

ENGLISH:
Make sure tone is academic, for scientists.
- "What Is This Module?" -> Plain language.
- Tables: Use markdown tables.
- Scientific note: boxed with 【Scientific Note】.
- Glossary: bullet terms.

ESPAÑOL:
- Use "módulo" not "module".
- "TrustedRoot" -> Raíz de Confianza.
- "AuditLog" -> Registro de Auditoría or Log de Auditoría Centralizado. The prompt uses "Log de auditoría centralizado (安全管理中心)". I'll use that.
- "Determinista" is correct.
- "Aritmética de enteros" or "aritmética entera". "Aritmética entera determinista".

РУССКИЙ:
- "Модуль" in software sense is acceptable, but for non-programmers maybe "компонент" or "блок". I'll use "модуль" but explain it's a software component.
- "TrustedRoot" -> Доверенный корень.
- "AuditLog" -> Централизованный журнал аудита.
- "VerificationCheckpoint" -> Контрольная точка верификации.
- "DynamicCorrelationEvent" -> Событие динамической корреляции.
- "TrustLevelVerifier" -> Проверяющий доверенных уровней? Better: Движок верификации уровней доверия.
- "Deterministic integer arithmetic" -> Детерминированная целочисленная арифметика.

中文:
- "Module" -> 模块.
- "TrustedRoot" -> 可信根.
- "AuditLog" -> 审计日志.
- "VerificationCheckpoint" -> 验证检查点.
- "DynamicCorrelationEvent" -> 动态关联事件.
- "TrustLevelVerifier" -> 信任等级验证引擎.
- "Deterministic integer arithmetic" -> 确定性整数运算.
- "Chain hash" -> 链式哈希.
- "取证工件" used.
- "逻辑断裂" used.

Let me write the final output carefully.

I need to be thorough but concise. The four-language structure will be lengthy. I should avoid excessive verbosity while covering all requirements.

Let's compose.

---

**ENGLISH**

**What Is This Module?**
This module, located at `vigia/core/trust_levels.py`, is a deterministic, open-source software simulator of the Chinese cybersecurity standard *等保2.0* (Multi-Level Protection Scheme 2.0, MLPS 2.0) Levels 1 through 4. It substitutes physical Trusted Platform Modules (TPM/TCM) with a transparent, deterministic HMAC-SHA256 integrity anchor. For researchers who do not program: imagine a digital laboratory protocol that enforces an unbroken chain-of-custody for computational evidence. Every operation relies on exact integer arithmetic—there are no approximations, no rounding operations, and no floating-point uncertainties.

**Key Concepts & Component Reference**

| Concept | Description | Deterministic Guarantee |
|---|---|---|
| **TrustLevel** | An ordinal classification (1–4) representing the depth of verification. Analogous to biosafety laboratory levels. | Discrete integer levels only; no fractional or transitional states exist. |
| **TrustedRoot** | The cryptographic origin point (*可信根*). Comparable to a tamper-evident seal on an evidence bag. | HMAC-SHA256 computed over exact byte-integer sequences; any alteration yields a different integer fingerprint. |
| **VerificationCheckpoint** | Specific execution moments where integrity is tested (Level 3+). Like quality-control stops on a production line. | Pass/fail outcome derived from exact integer hash comparison. |
| **AuditLog** | A centralized, append-only record store (*安全管理中心*). Comparable to a permanently bound laboratory notebook with numbered pages. | Records are
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
