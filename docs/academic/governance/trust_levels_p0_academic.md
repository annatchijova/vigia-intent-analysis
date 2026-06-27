<!--
VIGIA Academic Documentation
Module: 854c5cef
Batch ID: vigia-doc-0095-854c5cef
Generated: 2026-05-20T14:56:47.865096+00:00
-->

# Module Documentation: `vigia/governance/trust_levels_p0.py`

## ENGLISH

### What Is This Module?

`vigia/governance/trust_levels_p0.py` is a deterministic, open-source software simulation of Chinese multi-level trusted-computing governance (等保2.0 Levels 1–4). It replaces physical Trusted Platform Modules (TPM/TCM) with a software anchor based on HMAC-SHA256 integer digests. Designed for digital-forensic reproducibility, every integrity check relies on exact integer equality of hash values—never on approximate or floating-point comparisons.

All integrity comparisons rely on exact integer equality of 256-bit HMAC-SHA256 digests. There are no floating-point operations, approximations, or probabilistic roundings anywhere in the verification pipeline.

### Key Concepts

#### Governance Classes

| Class | Forensic Purpose | 等保2.0 Analogue |
|---|---|---|
| `TrustLevel` | Enumerates the four mandatory integer protection grades. | Levels 1–4 |
| `TrustedRoot` | Software-simulated root of trust holding a 256-bit integer HMAC secret. | 可信根 (TCM emulator) |
| `VerificationCheckpoint` | Named execution stage where runtime integrity is tested deterministically. | 动态可信验证 (Level 3) |
| `VerificationRecord` | Immutable entry documenting that a checkpoint was reached and passed. | Audit entry / forensic artifact |
| `AuditLog` | Append-only chain of records linked by iterated integer hash. | 安全管理中心 (Level 2) |
| `DynamicCorrelationEvent` | Integer-coded event token used in cross-temporal rule evaluation. | 动态关联感知 (Level 4) |
| `VerificationResult` | Structured pass/fail verdict carrying integer hash evidence. | Forensic outcome |
| `TrustLevelVerifier` | Central engine routing control to the appropriate level routine. | Governance orchestrator |

#### Core Functions

| Function | Role | Deterministic Guarantee |
|---|---|---|
| `create_trusted_root()` | Instantiates a new `TrustedRoot` with a fresh HMAC key. | Integer secret generated without floating-point entropy. |
| `verify_integrity()` | Compares current HMAC digest against stored integer baseline. | Exact integer equality; no approximation. |
| `add_record()` | Appends a `VerificationRecord` and re-computes chain hash. | Iterated integer hash function. |
| `verify_level_1()` | Basic boot-time checks and alarm generation. | Binary pass/fail on integer hashes. |
| `verify_level_2()` | Level 1 plus centralized audit-log consistency check. | Chain-hash integer equality. |
| `verify_level_3()` | Level 2 plus dynamic checkpoint verification during execution. | Named-stage integer token validation. |
| `verify_level_4()` | Level 3 plus dynamic correlation (Thirdness). | Multi-event integer rule mediation. |
| `verify()` | Unified dispatcher selecting the routine by integer level ID. | Branching on integer constants. |
| `to_dict()` | Serializes the current deterministic integer state into a reproducible dictionary. | Exact integer values preserved as strings/integers. |

#### Level Constants & Checkpoint Stages

| Constant | Type | Description |
|---|---|---|
| `LEVEL_1` … `LEVEL_4` | Integer | Discrete trust grades. |
| `BOOT_START` | String token | Initial boot stage marker. |
| `BOOT_VERIFY_KERNEL` | String token | Kernel validation stage. |
| `BOOT_COMPLETE` | String token | Boot completion marker. |
| `ANALYSIS_INIT` | String token | Forensic analysis initialization. |
| `ANALYSIS_SIGNAL_RECEPTION` | String token | Signal ingestion stage. |
| `ANALYSIS_INFERENCE` | String token | Inference/correlation stage. |

### Glossary

- **Deterministic integer arithmetic**: Mathematical operations on whole numbers (hash digests treated as large integers) where identical inputs always produce identical outputs. No rounding, truncation, or floating-point error exists.
- **HMAC-SHA256**: A keyed cryptographic hash algorithm producing a 256-bit integer digest. In this module it replaces a physical TPM/TCM as the software integrity anchor.
- **MLPS 2.0 (等保2.0)**: Chinese Multi-Level Protection Scheme, version 2.0, defining four mandatory security grades for information systems.
- **TCM (Trusted Cryptography Module)**: Chinese national standard for hardware root of trust. This module emulates its behavior in software.
- **Chain hash**: A deterministic sequence where each new integer digest incorporates the previous digest, creating a tamper-evident log.
- **Logical fracture (逻辑断裂)**: A deterministic indicator that the integrity chain has been broken; an exact integer mismatch between expected and observed hash values.
- **Forensic artifact (取证工件)**: Any digital object produced by deterministic integer operations and admissible as reproducible evidence.
- **Thirdness (Peirce)**: The categorical level of mediating rules or habits. In this module, Level 4 implements Thirdness as deterministic dynamic correlation—not mysticism, but a formal rule system analogous to multi-sensor data fusion.
- **Dynamic trusted verification (动态可信验证)**: Level 3 runtime checkpoint mechanism.
- **Dynamic correlation perception (动态关联感知)**: Level 4 mechanism evaluating event sequences via deterministic mediating rules.

### 【Scientific Note】

Terms drawn from C. S. Peirce (Firstness, Secondness, Thirdness), Umberto Eco (unlimited semiosis, encyclopedic semantics), and H. P. Grice (cooperative maxims, implicature) are sometimes dismissed as literary mysticism. They are not. In this deterministic forensic architecture, they operate exactly like calibrated scientific instruments: Peirce's Thirdness is formally equivalent to a sensor-fusion algorithm that mediates among multiple integer-verified event streams to reject noise; Eco's semiotic layering corresponds to the stacked encoding and decoding of protocol headers into integer tokens; and Grice's maxims function as deterministic relevance filters for log entries. Just as a thermometer does not "believe" in temperature, these semiotic concepts do not invoke the paranormal—they are rule-based descriptors for how deterministic integer structures produce interpretable meaning.

---

## ESPAÑOL

### ¿Qué es este módulo?

`vigia/governance/trust_levels_p0.py` es una simulación de software determinista y de código abierto del sistema chino de gobernanza informática multinivel confiable (等保2.0 Niveles 1–4). Sustituye los Módulos de Plataforma Confiable físicos (TPM/TCM) con un ancla de software basada en resúmenes enteros HMAC-SHA256. Diseñado para la reproducibilidad en la informática forense digital, cada verificación de integridad se basa en la igualdad exacta de enteros de los valores hash, nunca en comparaciones aproximadas o de punto flotante.

Todas las comparaciones de integridad se basan en la igualdad exacta de enteros de 256 bits de los resúmenes HMAC-SHA256. No existen operaciones de punto flotante, aproximaciones ni redondeos probabilísticos en ninguna parte de la tubería de verificación.

### Conceptos clave

#### Clases de gobernanza

| Clase | Propósito forense | Equivalente 等保2.0 |
|---|---|---|
| `TrustLevel` | Enumera los cuatro grados de protección enteros obligatorios. | Niveles 1–4 |
| `TrustedRoot` | Raíz de confianza simulada por software que contiene un secreto HMAC entero de 256 bits. | 可信根 (emulador TCM) |
| `VerificationCheckpoint` | Etapa de ejecución nombrada donde la integridad en tiempo de ejecución se verifica de forma determinista. | 动态可信验证 (Nivel 3) |
| `VerificationRecord` | Entrada inmutable que documenta que se alcanzó y superó un punto de control. | Entrada de auditoría / artefacto forense |
| `AuditLog` | Cadena de registros de solo adición vinculados por hash entero iterado. | 安全管理中心 (Nivel 2) |
| `DynamicCorrelationEvent` | Token de evento codificado en entero utilizado en evaluación de reglas cruzadas temporales. | 动态关联感知 (Nivel 4) |
| `VerificationResult` | Veredicto estructurado de aprobación/fallo con evidencia hash entera. | Resultado forense |
| `TrustLevelVerifier` | Motor central que enruta el control a la rutina de nivel apropiada. | Orquestador de gobernanza |

#### Funciones principales

| Función | Rol | Garantía determinista |
|---|---|---|
| `create_trusted_root()` | Instancia una nueva `TrustedRoot` con una clave HMAC nueva. | Secreto entero generado sin entropía de punto flotante. |
| `verify_integrity()` | Compara el resumen HMAC actual con la línea base entera almacenada. | Igualdad entera exacta; sin aproximación. |
| `add_record()` | Añade un `VerificationRecord` y recalcula el hash de cadena. | Función hash entera iterada. |
| `verify_level_1()` | Verificaciones básicas en tiempo de arranque y generación de alarmas. | Aprobación/fallo binario sobre hashes enteros. |
| `verify_level_2()` | Nivel 1 más comprobación de consistencia de registro de auditoría centralizado. | Igualdad entera de hash de cadena. |
| `verify_level_3()` | Nivel 2 más verificación dinámica de puntos de control durante la ejecución. | Validación de token entero de etapa nombrada. |
| `verify_level_4()` | Nivel 3 más correlación dinámica (Terceridad). | Mediación de reglas enteras multi-evento. |
| `verify()` | Despachador unificado que selecciona la rutina por ID de nivel entero. | Ramificación sobre constantes enteras. |
| `to_dict()` | Serializa el estado entero determinista actual en un diccionario reproducible. | Valores enteros exactos preservados como cadenas/enteros. |

#### Constantes de nivel y etapas de ejecución

| Constante | Tipo | Descripción |
|---|---|---|
| `LEVEL_1` … `LEVEL_4` | Entero | Grados de confianza discretos. |
| `BOOT_START` | Token de cadena | Marcador de etapa de arranque inicial. |
| `BOOT_VERIFY_KERNEL` | Token de cadena | Etapa de validación del núcleo. |
| `BOOT_COMPLETE` | Token de cadena | Marcador de finalización del arranque. |
| `ANALYSIS_INIT` | Token de cadena | Inicialización del análisis forense. |
| `ANALYSIS_SIGNAL_RECEPTION` | Token de cadena | Etapa de ingestión de señales. |
| `ANALYSIS_INFERENCE` | Token de cadena | Etapa de inferencia/correlación. |

### Glosario

- **Aritmética entera determinista**: Operaciones matemáticas sobre números enteros (resúmenes hash tratados como enteros grandes) donde entradas idénticas siempre producen salidas idénticas. No existe redondeo ni error de punto flotante.
- **HMAC-SHA256**: Algoritmo criptográfico de hash con clave que produce un resumen entero de 256 bits. En este módulo reemplaza al TPM/TCM físico como ancla de integridad por software.
- **MLPS 2.0 (等保2.0)**: Esquema de Protección Multinivel de China, versión 2.0.
- **TCM (Módulo de Criptografía Confiable)**: Estándar nacional chino de raíz de confianza en hardware; este módulo emula su comportamiento en software.
- **Hash de cadena**: Secuencia determinista donde cada nuevo resumen entero incorpora el anterior, creando un registro inmutable.
- **Fractura lógica (逻辑断裂)**: Indicador determinista de que la cadena de integridad se ha roto; una discrepancia exacta entre valores hash enteros esperados y observados.
- **Artefacto forense (取证工件)**: Objeto digital producido por operaciones deterministas sobre enteros y admisible como evidencia reproducible.
- **Terceridad (Peirce)**: Nivel categórico de reglas mediadoras. En este módulo, el Nivel 4 implementa la Terceridad como correlación dinámica determinista: no es misticismo, sino un sistema formal análogo a la fusión de datos multisensorial.
- **Verificación confiable dinámica (动态可信验证)**: Mecanismo de puntos de control en tiempo de ejecución del Nivel 3.
- **Percepción de correlación dinámica (动态关联感知)**: Mecanismo del Nivel 4 que evalúa secuencias de eventos mediante reglas mediadoras deterministas.

### 【Nota Científica】

Los términos tomados de C. S. Peirce (Primeridad, Segundidad, Terceridad), Umberto Eco (semiosis ilimitada, semántica enciclopédica) y H. P. Grice (máximas conversacionales, implicatura) a veces se descartan como misticismo literario. No lo son. En esta arquitectura forense determinista operan exactamente como instrumentos científicos calibrados: la Terceridad de Peirce es formalmente equivalente a un algoritmo de fusión de sensores que media entre múltiples flujos de eventos verificados por enteros para rechazar ruido; el estrato semiótico de Eco corresponde a la codificación y decodificación apilada de cabeceras de protocolo en tokens enteros; y las máximas de Grice funcionan como filtros deterministas de relevancia para entradas de registro. Así como un termómetro no «cree» en la temperatura, estos conceptos semióticos no invocan lo paranormal: son descriptores basados en reglas de cómo estructuras deterministas de enteros producen significado interpretable.

---

## РУССКИЙ

### Что представляет собой этот модуль?

`vigia/governance/trust_levels_p0.py` — это детерминированная программная симуляция китайской многоуровневой системы управления доверенными вычислениями (等保2.0, Уровни 1–4) с открытым исходным кодом. Она заменяет физические модули доверенной платформы (TPM/TCM) программным якорем на основе целочисленных дайджестов HMAC-SHA256. Разработанная для воспроизводимости в цифровой криминалистике, каждая проверка целостности опирается на точное целочисленное равенство хеш-значений — никогда на приближённые или операции с плавающей точкой.

Все сравнения целостности опираются на точное целочисленное равенство 256-битных дайджестов HMAC-SHA256. В конвейере верификации отсутствуют операции с плавающей точкой, приближения и вероятностные округления.

### Ключевые концепции

#### Классы управления

| Класс | Судебно-экспертное назначение | Аналог 等保2.0 |
|---|---|---|
| `TrustLevel` | Перечисляет четыре обязательных целочисленных уровня защиты. | Уровни 1–4 |
| `TrustedRoot` | Программно-симулированный корень доверия, хранящий 256-битный целочисленный секрет HMAC. | 可信根 (эмулятор TCM) |
| `VerificationCheckpoint` | Именованный этап выполнения, на котором целостность в реальном времени проверяется детерминированно. | 动态可信验证 (Уровень 3) |
| `VerificationRecord` | Неизменяемая запись, фиксирующая достижение и прохождение контрольной точки. | Запись аудита / артефакт для экспертизы |
| `AuditLog` | Цепочка записей только для добавления, связанных итерированным целочисленным хешем. | 安全管理中心 (Уровень 2) |
| `DynamicCorrelationEvent` | Целочисленно-кодированный токен события для оценки правил с перекрёстными временными метками. | 动态关联感知 (Уровень 4) |
| `VerificationResult` | Структурированный вердикт «пройдено/не пройдено» с доказательством целочисленного хеша. | Судебный результат |
| `TrustLevelVerifier` | Центральный движок, маршрутизирующий управление к соответствующей процедуре уровня. | Оркестратор управления |

#### Основные функции

| Функция | Роль | Детерминированная гарантия |
|---|---|---|
| `create_trusted_root()` | Создаёт новый `TrustedRoot` со свежим ключом HMAC. | Целочисленный секрет генерируется без энтропии с плавающей точкой. |
| `verify_integrity()` | Сравнивает текущий дайджест HMAC с сохранённой целочисленной базовой линией. | Точное целочисленное равенство; без приближения. |
| `add_record()` | Добавляет `VerificationRecord` и пересчитывает цепочечный хеш. | Итерированная целочисленная хеш-функция. |
| `verify_level_1()` | Базовые проверки при загрузке и генерация тревог. | Бинарное прохождение/отказ на целочисленных хешах. |
| `verify_level_2()` | Уровень 1 плюс проверка согласованности централизованного журнала аудита. | Целочисленное равенство цепочечного хеша. |
| `verify_level_3()` | Уровень 2 плюс динамическая верификация контрольных точек во время выполнения. | Валидация целочисленного токена именованного этапа. |
| `verify_level_4()` | Уровень 3 плюс динамическая корреляция (Третичность). | Посредничество целочисленных правил при множественных событиях. |
| `verify()` | Единый диспетчер, выбирающий процедуру по целочисленному идентификатору уровня. | Ветвление по целочисленным константам. |
| `to_dict()` | Сериализует текущее детерминированное целочисленное состояние в воспроизводимый словарь. | Точные целочисленные значения сохраняются в виде строк или целых чисел. |

#### Константы уровней и этапы выполнения

| Константа | Тип | Описание |
|---|---|---|
| `LEVEL_1` … `LEVEL_4` | Целое число | Дискретные уровни доверия. |
| `BOOT_START` | Строковый токен | Маркер начального этапа загрузки. |
| `BOOT_VERIFY_KERNEL` | Строковый токен | Этап валидации ядра. |
| `BOOT_COMPLETE` | Строковый токен | Маркер завершения загрузки. |
| `ANALYSIS_INIT` | Строковый токен | Инициализация судебного анализа. |
| `ANALYSIS_SIGNAL_RECEPTION` | Строковый токен | Этап приёма сигналов. |
| `ANALYSIS_INFERENCE` | Строковый токен | Этап вывода/корреляции. |

### Глоссарий

- **Детерминированная целочисленная арифметика**: Математические операции над целыми числами (хеш-дайджесты, представленные как большие целые), при которых одинаковые входные данные всегда дают одинаковый результат. Никаких округлений или ошибок плавающей точки.
- **HMAC-SHA256**: Ключевой криптографический хеш-алгоритм, выдающий 256-битный целочисленный дайджест. В данном модуле используется как программная замена физическому TPM/TCM.
- **MLPS 2.0 (等保2.0)**: Китайская многоуровневая система защиты информации, версия 2.0.
- **TCM (доверенный криптографический модуль)**: Национальный стандарт Китая аппаратного корня доверия; данный модуль эмулирует его поведение программно.
- **Цепочечный хеш**: Детерминированная последовательность, в которой каждый новый целочисленный дайджест включает предыдущий, образуя неизменяемый журнал.
- **Логический разрыв (逻辑断裂)**: Детерминированный индикатор нарушения цепочки целостности; точное несовпадение ожидаемого и наблюдаемого целочисленных хеш-значений.
- **Цифровой артефакт для экспертизы (取证工件)**: Любой цифровой объект, созданный детерминированными целочисленными операциями и пригодный для использования в качестве воспроизводимого доказательства.
- **Третичность (Пирс)**: Категория посредничающих правил. В данном модуле Уровень 4 реализует Третичность как детерминированную динамическую корреляцию — не мистицизм, а формальная система правил, аналогичная мультисенсорной интеграции данных.
- **Динамическая доверенная верификация (动态可信验证)**: Механизм контрольных точек времени выполнения Уровня 3.
- **Динамическое корреляционное восприятие (动态关联感知)**: Механизм Уровня 4 для оценки последовательностей событий по детерминированным посредничающим правилам.

### 【Научное примечание】

Термины из работ Ч. С. Пирса (первичность, вторичность, третичность), Умберто Эко (неограниченная семиозис, энциклопедическая семантика) и Г. П. Грайса (кооперативные максимы, импликатура) иногда отвергаются как литературный мистицизм. Это не так. В данной детерминированной судебно-экспертной архитектуре они функционируют точно так же, как калиброванные научные приборы: третичность Пирса формально эквивалентна алгоритму слияния данных сенсоров, который опосредует между множественными потоками событий, верифицированными целыми числами, чтобы отсеять шум; семиотическое расслоение Эко соответствует послойному кодированию и декодированию заголовков протоколов в целочисленные токены; а максимы Грайса работают как детерминированные фильтры релевантности для записей журнала. Как термометр не «верит» в температуру, эти семиотические концепции не призывают паранормальное — это правил-ориентированные дескрипторы того, как детерминированные целочисленные структуры порождают интерпретируемый смысл.

---

## 中文

### 本模块是什么？

`vigia/governance/trust_levels_p0.py` 是一个确定性的开源软件模块，用于模拟中国多级可信计算治理体系（等保2.0 第一级至第四级）。它以 HMAC-SHA256 整数摘要作为完整性锚点，取代物理可信密码模块（TCM/TPM）。所有验证均基于整数哈希的精确相等性，而非浮点近似。

所有完整性比较均依赖 256 位 HMAC-SHA256 摘要的精确整数相等性。验证流水线中不存在任何浮点运算、近似计算或概率舍入。

### 核心概念

#### 治理类

| 类 | 取证功能 | 等保2.0 对应项 |
|---|---|---|
| `TrustLevel` | 枚举四个强制整数保护等级。 | 第一级至第四级 |
| `TrustedRoot` | 持有 256 位整数 HMAC 密钥的软件模拟可信根。 | 可信根（TCM 仿真器） |
| `VerificationCheckpoint` | 运行时完整性被确定性检测的命名执行阶段。 | 动态可信验证（第三级） |
| `VerificationRecord` | 记录已到达并通过检查点的不可变条目。 | 审计条目 / 取证工件 |
| `AuditLog` | 通过迭代整数哈希链接的仅追加记录链。 | 安全管理中心（第二级） |
| `DynamicCorrelationEvent` | 用于跨时域规则评估的整数编码事件令牌。 | 动态关联感知（第四级） |
| `VerificationResult` | 携带整数哈希证据的结构化通过/失败裁决。 | 取证结果 |
| `TrustLevelVerifier` | 将控制路由至相应等级例程的中央引擎。 | 治理编排器 |

#### 核心函数

| 函数 | 作用 | 确定性保证 |
|---|---|---|
| `create_trusted_root()` | 实例化具有新 HMAC 密钥的 `TrustedRoot`。 | 整数密钥生成，无浮点熵源。 |
| `verify_integrity()` | 将当前 HMAC 摘要与存储的整数基线进行比较。 | 精确整数相等，无近似。 |
| `add_record()` | 追加 `VerificationRecord` 并重新计算链式哈希。 | 迭代整数哈希函数。 |
| `verify_level_1()` | 基本启动时检查与告警生成。 | 基于整数哈希的二元通过/失败。 |
| `verify_level_2()` | 第一级功能加集中式审计日志一致性检查。 | 链式哈希整数相等。 |
| `verify_level_3()` | 第二级功能加执行中动态检查点验证。 | 命名阶段整数令牌验证。 |
| `verify_level_4()` | 第三级功能加动态关联（第三性）。 | 多事件整数规则中介。 |
| `verify()` | 通过整数等级 ID 选择例程的统一调度器。 | 基于整数常数的分支。 |
| `to_dict()` | 将当前确定性整数状态序列化为可复现的字典。 | 精确整数值以字符串或整数形式保留。 |

#### 常量与执行阶段

| 常量 | 类型 | 说明 |
|---|---|---|
| `LEVEL_1` … `LEVEL_4` | 整数 | 离散的信任等级。 |
| `BOOT_START` | 字符串标记 | 初始启动阶段标记。 |
| `BOOT_VERIFY_KERNEL` | 字符串标记 | 内核验证阶段。 |
| `BOOT_COMPLETE` | 字符串标记 | 启动完成标记。 |
| `ANALYSIS_INIT` | 字符串标记 | 取证分析初始化。 |
| `ANALYSIS_SIGNAL_RECEPTION` | 字符串标记 | 信号接收阶段。 |
| `ANALYSIS_INFERENCE` | 字符串标记 | 推断/关联阶段。 |

### 术语表

- **确定性整数运算**：对整数（哈希摘要视为大整数）进行的数学操作，相同输入永远产生相同输出，不存在舍入、截断或浮点误差。
- **HMAC-SHA256**：一种带密钥的加密哈希算法，输出 256 位整数摘要。本模块以其作为软件完整性锚点，代替物理 TPM/TCM。
- **等保2.0（MLPS 2.0）**：中国网络安全等级保护制度 2.0 版，定义信息系统四个强制安全等级。
- **可信密码模块（TCM）**：中国硬件可信根国家标准；本模块以软件模拟其行为。
- **链式哈希**：确定性序列，每个新的整数摘要都包含前一个摘要，形成不可篡改的日志。
- **逻辑断裂**：完整性链条被破坏的确定性指标；预期整数哈希值与实际观测值之间的精确不匹配。
- **取证工件**：由确定性整数操作生成的任何数字对象，可作为可复现证据采信。
- **第三性（皮尔斯）**：中介规则或习惯的范畴。本模块第四级实现第三性，即确定性动态关联——并非神秘主义，而是类似于多传感器数据融合的形式化规则系统。
- **动态可信验证（第三级）**：运行时检查点机制。
- **动态关联感知（第四级）**：通过确定性中介规则评估事件序列的机制。

### 【科学说明】

源自皮尔斯（C. S. Peirce，第一性、第二性、第三性）、艾柯（Umberto Eco，无限符号过程、百科全书式语义学）与格赖斯（H. P. Grice，合作原则、会话含义）的术语有时被误认为是文学神秘主义。事实并非如此。在该确定性取证架构中，它们的作用完全等同于经校准的科学仪器：皮尔斯的"第三性"在形式上等同于一种传感器融合算法，它在多条经整数验证的事件流之间进行中介，以排除噪声；艾柯的符号学分层对应于协议首部向整数令牌的堆叠式编码与解码；格赖斯准则则充当日志条目的确定性相关性过滤器。正如温度计并不"相信"温度，这些符号学概念也不召唤超自然现象——它们是基于规则的描述符，说明确定性的整数结构如何生成可解释的意义。

---

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
