<!--
VIGIA Academic Documentation
Module: 06e4330c
Batch ID: vigia-doc-0045-06e4330c
Generated: 2026-05-20T14:56:47.854193+00:00
-->

ENGLISH:
- Title: Module Documentation: vigia/core/config_sentinel.py
- What Is This Module? Explain it as a forensic instrument that seals the configuration of a digital observation system (VIGÍA). Like a tamper-evident seal on a sample container. It takes a snapshot of system settings at the start, checks between analysis phases, and finalizes. Uses SHA-256 (deterministic integer arithmetic on bit strings) — no floating point. Produces an audit trail.
- Key Concepts table:
  - Immutable Sealing / Sellado Inmutable / Непрерывное запечатывание / 不可变封存
  - Tamper Detection / Detección de manipulación / Обнаружение подделки / 篡改检测
  - Runtime Integrity / Integridad en ejecución / Целостность времени выполнения / 运行时完整性
  - Audit Trail / Trail de auditoría / Аудиторский след / 审计追踪
  - Deterministic Hash / Hash determinista / Детерминированный хеш / 确定性哈希
- Classes/Components table (explain in scientific terms, not Python code):
  - SystemIntegrityLevel: Categorical state of the whole system (FULL, DEGRADED, COMPROMISED, UNKNOWN).
  - ModuleSnapshot: A frozen record of which analytical modules were active at a specific moment.
  - DegradationEvent: A logged incident where a capability was lost or altered.
  - ConfigAuditTrail: The complete, append-only record of all snapshots and events.
  - ConfigurationTamperedException: An alert triggered when the configuration changes illegally during analysis.
  - ConfigAuditMonitor: The central instrument that executes snapshot, checkpoint, and sealing operations.
- Functions explained as procedures:
  - initialize(): Baseline measurement. Must precede all analysis.
  - checkpoint(): Interim verification. Compares current state to baseline using deterministic integer hash.
  - finalize(): Terminal sealing. Closes the audit trail and prepares the bundle.
  - to_report_dict(): Data export for the sealed forensic bundle.
- Glossary: terms like SHA-256 (deterministic cryptographic hash using integer bit operations), Environment Variable, Runtime, Audit Trail, Immutable Seal, SANS Analyst, etc.

ESPAÑOL:
- Similar, using Spanish from the docstring as basis. "¿Qué es este módulo?" "Guardián de configuración con sellado inmutable".
- Use terms: sellado, módulos críticos, degradación silenciosa, trail de auditoría.

РУССКИЙ:
- "Что такое этот модуль?" "Страж конфигурации с неизменным запечатыванием".
- Terms: Непрерывное / неизменное запечатывание (immutable sealing), контрольная точка, след аудита, детерминированный хеш.

中文:
- "这是什么模块？" "VIGÍA 配置守卫与不可变封存模块".
- Must use: 艾柯 (Eco), 格赖斯 (Grice), 取证工件 (not 制品), 逻辑断裂 (not 裂缝).
- Note: The module itself doesn't use these terms, but the scientific note must mention them in the context of VIGÍA's theoretical framework.

Scientific Note content (sensor analogy):
- Explain that in the VIGÍA framework, references to Peirce (semiotics), Eco (code/interpretation), and Grice (cooperative principle/maxims) are not metaphysical or mystical concepts.
- They function exactly like calibrated sensors in an instrument array.
- Peirce's signs = sensor readings mapping stimuli to interpretable data.
- Eco's codes = calibration tables that translate raw integers into forensic categories.
- Grice's maxims = quality control protocols ensuring the sensor data is truthful, relevant, and sufficiently detailed.
- Without this configuration sentinel (the sensor grounding), those higher-level abstractions would lack deterministic integrity.
- Therefore, this module provides the deterministic integer arithmetic foundation (SHA-256 bit operations, integer state flags) that makes the "semiotic" layer scientifically rigorous, not mystical.

Need to make sure no floating-point explanations. Emphasize deterministic integer arithmetic:
- SHA-256 operates on 32-bit integer words, modular addition, bitwise operations.
- State flags are integers.
- Comparisons are exact integer equality.
- No probability, no rounding, no floating-point uncertainty.

Tables should be clean Markdown.

- 艾柯 (Umberto Eco)
- 格赖斯 (H.P. Grice)
- 取证工件 (forensic artifact, instead of 制品)
- 逻辑断裂 (logical fracture/break, instead of 裂缝)

Also, the license line must be exactly: ""

---

# Module Documentation: `vigia/core/config_sentinel.py`

## ENGLISH

### What Is This Module?
[Explanation]

### Key Concepts
| Concept | Description |
|---|---|
| ... | ... |

### Component Reference
| Component | Scientific Function |
|---|---|
| SystemIntegrityLevel | ... |
| ... | ... |

### Operational Procedures
| Procedure | Purpose |
|---|---|
| initialize() | ... |
| checkpoint() | ... |
| finalize() | ... |
| to_report_dict() | ... |

### Glossary
- **SHA-256**: ...
- **Environment Variable**: ...
- etc.

> 【Scientific Note】Peirce/Eco/Grice...

---

## ESPAÑOL

### ¿Qué es este módulo?
...

### Conceptos clave
...

### Referencia de componentes
...

### Procedimientos operativos
...

### Glosario
...

> 【Nota Científica】...

---

## РУССКИЙ

### Что такое этот модуль?
...

### Ключевые концепции
...

### Описание компонентов
...

### Операционные процедуры
...

### Глоссарий
...

> 【Научное Примечание】...

---

## 中文

### 这是什么模块？
...

### 核心概念
...

### 组件说明
...

### 操作流程
...

### 术语表
...

> 【科学说明】...

---

---

Now, let me flesh out the content carefully.

ENGLISH details:
- What Is This Module?: It is a forensic tamper-evidence instrument for the VIGÍA system's configuration. Think of it as a digital equivalent of a sealed sample bag with a signed chain-of-custody card. Before any analysis begins, it photographs the system settings. Between each phase of the analytical pipeline, it checks whether the photograph still matches reality. If an environment variable changes, a module is silently disabled, or a setting is altered, the instrument logs a degradation event or raises an alarm. The final output is an immutable audit trail bound to a SHA-256 fingerprint, which a SANS-certified analyst can later inspect to confirm exactly which modules were active and whether the system state remained intact. All operations rely on deterministic integer arithmetic—bitwise logical operations and modular addition on 32-bit words—eliminating any uncertainty introduced by floating-point approximations.

ESPAÑOL details:
- Guardian de configuración con sellado inmutable. Similar explanation. "Equivalente digital de una bolsa de muestras sellada con cadena de custodia firmada." "Aritmética entera determinista."

РУССКИЙ details:
- Страж конфигурации с неизменным запечатыванием. "Цифровой эквивалент запечатанного пакета для образцов с подписанной картой учёта цепочки хранения." "Детерминированная целочисленная арифметика."

中文 details:
- VIGÍA 配置守卫与不可变封存模块。 "数字取证中的防篡改证据仪器，相当于贴有监管链签字卡的密封样本袋。" "确定性整数运算".

Key concepts table (English example):
| Concept | Scientific Description |
|---|---|
| Immutable Sealing | A one-way, append-only binding process. Once a snapshot is recorded, it cannot be altered without invalidating the SHA-256 fingerprint. |
| Tamper Detection | Deterministic comparison between the initial integer hash baseline and the current system state. Any deviation produces an exception or degradation event. |
| Silent Degradation | Loss of analytical capability caused by environment variables or disabled modules that does not trigger an immediate user-visible error. |
| Runtime Integrity | The property that configuration remains unchanged during the entire analysis window, verified by integer-equality checkpoints. |
| Deterministic Hash (SHA-256) | A reproducible fingerprint computed exclusively through fixed-width integer bitwise operations and modular addition; no timestamps or floating-point values are used, so identical inputs always yield identical outputs. |

Component Reference table (English):
| Component | Scientific Role |
|---|---|
| `SystemIntegrityLevel` | Categorical integrity classifier. States: FULL (all systems nominal), DEGRADED (capability reduced but traceable), COMPROMISED (evidence trustworthiness at risk), UNKNOWN (state cannot be ascertained). |
| `ModuleSnapshot` | A cryogenic freeze-frame of active analytical modules at a specific instant. Represented as integer state vectors and string identifiers. |
| `DegradationEvent` | A structured forensic log entry describing what changed, when (in pipeline sequence, not wall-clock time), and how the integrity level was affected. |
| `ConfigAuditTrail` | The complete, append-only ledger of snapshots and events. Functions as the primary 取证工件 for external review. |
| `ConfigurationTamperedException` | An integrity alarm triggered when a checkpoint detects an unauthorized configuration delta. Halts analysis to prevent corrupted evidence processing. |
| `ConfigAuditMonitor` | The master instrument that executes baseline capture, phase-to-phase verification, and final seal. Operates using secret-key-authenticated integer hashes. |

Operational Procedures table (English):
| Procedure | When to Use | Scientific Outcome |
|---|---|---|
| `initialize()` | Before any data enters the pipeline. | Captures the baseline snapshot and computes the initial deterministic config hash. |
| `checkpoint()` | Between every analytical phase. | Performs integer-equality verification against baseline. Returns a list of degradation events; raises `ConfigurationTamperedException` if integrity is breached. |
| `finalize()` | After the last evidence item is processed. | Appends the terminal snapshot, closes the audit trail, and prepares the sealed bundle. |
| `to_report_dict()` | During report generation. | Exports the trail into a standardized dictionary format suitable for inclusion in the sealed forensic package. |

Glossary (English):
- **SHA-256**: A cryptographic hash function that processes data through 64 rounds of deterministic integer operations on 32-bit words. It produces a fixed 256-bit fingerprint; any single-bit change in input yields a completely different output.
- **Environment Variable**: External system parameter that can alter program behavior without modifying source files. A common vector for silent degradation.
- **Runtime**: The period during which the analysis is actively executing. Changes to configuration during this window are prohibited and detectable by this module.
- **Audit Trail**: A chronologically ordered, tamper-evident record of events. In this module, it is bound to a hash chain to guarantee non-repudiation.
- **Deterministic Integer Arithmetic**: Mathematical operations on whole numbers (bitwise AND, OR, XOR, shifts, modular addition) that always produce the same result for the same inputs, with no rounding error or probabilistic noise.
- **SANS Analyst**: A digital forensics professional certified by the SANS Institute, trained to verify integrity seals and audit trails.
- **Logic Fracture / 逻辑断裂**: A discontinuity in the inferential chain of evidence processing. Prevented by maintaining unbroken integer hash continuity across checkpoints.

For the Scientific Note, I need to make sure it's consistent across languages.

English version:
> 【Scientific Note】Within the broader VIGÍA framework, terminology derived from Charles Sanders Peirce (semiotics), Umberto Eco (codes of interpretation), and H. P. Grice (cooperative maxims) is sometimes misread as metaphysical or mystical. It is not. These concepts operate as a **sensor analogy** for deterministic measurement:
> - **Peircean semiotics** functions like a transduction layer: raw physical states (signs) are mapped into structured integer identifiers (interpretants) that the machine can process.
> - **Eco’s codes** act as calibration tables: they translate raw bit patterns into forensic categories using deterministic rules, exactly as a spectrometer translates wavelength integers into chemical element IDs.
> - **Grice’s maxims** serve as quality-control protocols for the sensor array: they ensure that emitted data is truthful (Quality), relevant (Relation), and sufficiently detailed (Quantity).
> This module (`config_sentinel`) is the physical instrument layer that grounds those abstractions. By sealing configuration with SHA-256 deterministic integer arithmetic—never floating-point approximations—it supplies the exact, reproducible sensor readings upon which any higher-order semiotic interpretation must rest. Without this grounding, semiotic analysis would suffer from **逻辑断裂** (logical discontinuity) between evidence and inference.

ESPAÑOL version of note:
> 【Nota Científica】En el marco general de VIGÍA, la terminología derivada de Charles Sanders Peirce (semiótica), Umberto Eco (códigos de interpretación) y H. P. Grice (máximas cooperativas) a veces se lee erróneamente como metafísica o mística. No lo es. Estos conceptos funcionan como una **analogía de sensor** para la medición determinista:
> - La **semiótica peirceana** actúa como una capa de transducción: los estados físicos brutos (signos) se mapean a identificadores enteros estructurados (interpretantes) que la máquina puede procesar.
> - Los **códigos de Eco** funcionan como tablas de calibración: traducen patrones de bits brutos en categorías forenses mediante reglas deterministas, exactamente como un espectrómetro traduce longitudes de onda enteras en identificadores de elementos químicos.
> - Las **máximas de Grice** sirven como protocolos de control de calidad para la matriz de sensores: garantizan que los datos emitidos sean veraces (Calidad), pertinentes (Relación) y suficientemente detallados (Cantidad).
> Este módulo (`config_sentinel`) es la capa de instrumentación física que ancla esas abstracciones. Al sellar la configuración mediante aritmética entera determinista SHA-256 —nunca aproximaciones de punto flotante— proporciona las lecturas de sensor exactas y reproducibles sobre las que debe apoyarse cualquier interpretación semiótica de orden superior. Sin esta anclaje, el análisis semiótico sufriría una **ruptura lógica** entre la evidencia y la inferencia.

РУССКИЙ version:
> 【Научное Примечание】В рамках общей системы VIGÍA терминология, происходящая от Чарльза Сандерса Пирса (семиотика), Умберто Эко (коды интерпретации) и Х. П. Грайса (кооперативные максимы), иногда ошибочно воспринимается как метафизическая или мистическая. Это не так. Эти концепции работают как **аналогия датчика** для детерминированного измерения:
> - **Пирсовская семиотика** действует как слой трансдукции: необработанные физические состояния (знаки) отображаются в структурированные целочисленные идентификаторы (интерпретанты), которые машина может обрабатывать.
> - **Коды Эко** служат калибровочными таблицами: они переводят сырые битовые паттерны в судебно-медицинские категории с помощью детерминированных правил, точно так же, как спектрометр переводит целочисленные длины волн в идентификаторы химических элементов.
> - **Максимы Грайса** выступают в роли протоколов контроля качества для массива датчиков: они гарантируют, что выдаваемые данные являются достоверными (Качество), релевантными (Отношение) и достаточно детализированными (Количество).
> Этот модуль (`config_sentinel`) — это физический инструментальный слой, который обосновывает эти абстракции. Запечатывая конфигурацию с помощью детерминированной целочисленной арифметики SHA-256 — никогда приближений с плавающей запятой — он предоставляет точные, воспроизводимые показания датчиков, на которых должна основываться любая семиотическая интерпретация высшего порядка. Без этого обоснования семиотический анализ страдал бы от **логического разрыва** между доказательством и выводом.

中文 version:
> 【科学说明】在 VIGÍA 系统的整体框架中，源自查尔斯·桑德斯·皮尔士（符号学）、**艾柯**（解释代码）与 **格赖斯**（合作原则/会话准则）的术语有时被误读为形而上学或神秘主义概念。事实并非如此。这些概念是作为**传感器类比**而运作的确定性测量工具：
> - **皮尔士符号学**相当于传感器的转换层：将原始物理状态（符号）映射为机器可处理的结构化整数标识符（解释项）。
> - **艾柯的代码**相当于校准表：以确定性规则将原始比特模式转译为取证类别，其原理与光谱仪将整数波长转译为化学元素标识完全一致。
> - **格赖斯的准则**相当于传感器阵列的质量控制协议：确保输出数据真实（质准则）、相关（关系准则）且足够详尽（量准则）。
> 本模块（`config_sentinel`）正是将这些抽象理论加以落地的物理仪器层。它通过 SHA-256 确定性整数运算——绝不使用浮点近似——对配置进行封存，从而为任何高阶符号学解释提供精确、可复现的传感器读数。若缺乏此确定性基础，符号学分析将在证据与推理之间产生**逻辑断裂**，导致取证工件失效。

Also, the user said "Do NOT use floating-point math explanations — emphasize deterministic integer arithmetic where applicable". So in the hash explanation, emphasize integer bitwise operations.

- 取证工件 (forensic artifact) - used in glossary and/or component table.
- 逻辑断裂 (logical break/fracture) - used in scientific note.

Now let me draft the full document carefully.

One more thing: The module path is `vigia/core/config_sentinel.py`. I should mention this as the module identifier but not focus on it as code.

Also, for the functions, the user listed them with Python syntax (to_report_dict(), initialize(), etc.). Since the audience doesn't know Python, I should present them as procedures or actions, but keep the names as labels for traceability. I can write them as `initialize()` but explain them as steps.

Structure check:
- ENGLISH
  - What Is This Module?
  - Key Concepts (table)
  - Component Reference (table)
  - Operational Procedures (table)
  - Glossary
  - Scientific Note
- ESPAÑOL
  - Same structure
- РУССКИЙ
  - Same structure
- 中文
  - Same structure

Then License.

ENGLISH:
This module is the **Immutable Configuration Guardian** for the VIGÍA digital forensics platform. Its purpose is to guarantee that the analytical environment does not change while evidence is being processed. Imagine a sealed laboratory glovebox: before an experiment begins, a technician photographs every dial setting. During the experiment, no one may turn a dial without triggering an alarm. At the end, the photograph and the alarm log are locked inside a tamper-evident envelope.

In computational terms, the module performs three critical tasks:
1. **Baseline Freezing** — It records an exact integer fingerprint of every critical module and environment variable before analysis starts.
2. **Phase Verification** — Between each stage of the evidence-processing pipeline, it performs deterministic integer-comparison checkpoints. If a module has been disabled or an environment variable has shifted, it logs a degradation event or raises a tamper alarm.
3. **Final Sealing** — It appends a terminal snapshot to the audit trail and computes a SHA-256 integrity seal using only deterministic integer arithmetic on 32-bit words. The resulting bundle can be inspected by a SANS-certified analyst to verify which modules were active and whether any silent degradation occurred.

Because the configuration hash excludes timestamps and relies exclusively on exact integer operations—not floating-point approximations—the seal is fully reproducible. Two identical system configurations will always produce the same hash, enabling rigorous peer verification.

ESPAÑOL:
Este módulo es el **Guardián de Configuración con Sellado Inmutable** de la plataforma de informática forense VIGÍA. Su propósito es garantizar que el entorno analítico no cambie mientras se procesa la evidencia. Imagínese una cámara de guantes sellada de laboratorio: antes de comenzar un experimento, un técnico fotografía cada dial. Durante el experimento, nadie puede girar un dial sin activar una alarma. Al final, la fotografía y el registro de alarmas se guardan en un sobre inviolable.

En términos computacionales, el módulo realiza tres tareas críticas:
1. **Congelamiento de línea base** — Registra una huella digital entera exacta de cada módulo crítico y variable de entorno antes de que comience el análisis.
2. **Verificación por fases** — Entre cada etapa del pipeline de procesamiento de evidencia, ejecuta puntos de control mediante comparación determinista de enteros. Si un módulo se ha desactivado o una variable de entorno ha cambiado, registra un evento de degradación o lanza una alarma de manipulación.
3. **Sellado final** — Añade una instantánea terminal al trail de auditoría y calcula un sello de integridad SHA-256 utilizando únicamente aritmética entera determinista sobre palabras de 32 bits. El bundle resultante puede ser inspeccionado por un analista certificado SANS para verificar qué módulos estuvieron activos y si ocurrió alguna degradación silenciosa.

Dado que el hash de configuración excluye marcas de tiempo y se basa exclusivamente en operaciones enteras exactas —no en aproximaciones de punto flotante—, el sello es totalmente reproducible. Dos configuraciones idénticas del sistema siempre producirán el mismo hash, permitiendo una verificación rigurosa por pares.

РУССКИЙ:
Этот модуль — **Страж конфигурации с неизменным запечатыванием** для цифровой судебно-медицинской платформы VIGÍA. Его назначение — гарантировать неизменность аналитической среды в процессе обработки доказательств. Представьте герметичную лабораторную перчаточную камеру: прежде чем начать эксперимент, лаборант фотографирует положение каждого регулятора. Во время эксперимента никто не может повернуть регулятор, не включив сигнализацию. В конце фотография и журнал тревог помещаются в защитный пакет, нарушение целостности которого очевидно.

В вычислительном отношении модуль выполняет три критически важные задачи:
1. **Заморозка базовой линии** — Записывает точное целочисленное отпечаток каждого критического модуля и переменной среды до начала анализа.
2. **Поверка по фазам** — Между каждым этапом конвейера обработки доказательств выполняет контрольные точки на основе детерминированного сравнения целых чисел. Если модуль был отключён или переменная среды изменилась, регистрирует событие деградации или выдаёт тревогу о подделке.
3. **Окончательное запечатывание** — Дополняет аудиторский след терминальным снимком и вычисляет печать целостности SHA-256, используя исключительно детерминированную целочисленную арифметику над 32-битными словами. Полученный пакет может быть проверен сертифицированным аналитиком SANS, чтобы подтвердить, какие модули были активны и не произошла ли скрытая деградация.

Поскольку хеш конфигурации исключает временные метки и опирается исключительно на точные целочисленные операции — а не на приближения с плавающей запятой — печать полностью воспроизводима. Две идентичные системные конфигурации всегда дадут один и тот же хеш, что позволяет проводить строгую независимую верификацию.

中文:
本模块是 VIGÍA 数字取证平台的**配置守卫与不可变封存模块**。其目的在于确保证据处理过程中分析环境不发生任何变动。请将其想象为实验室中的密封手套箱：实验开始前，技术人员对所有旋钮设定进行拍照记录；实验期间，任何人转动旋钮都会触发警报；实验结束后，照片与警报日志被锁入一次性防拆信封。

从计算角度而言，本模块执行三项核心任务：
1. **基线冻结** — 在分析开始前，记录所有关键模块与环境变量的精确整数指纹。
2. **阶段核验** — 在证据处理流水线的每个阶段之间，执行基于确定性整数比对的检查点。若有模块被静默禁用或环境变量发生偏移，则记录降级事件或触发篡改警报。
3. **最终封存** — 将终端快照追加至审计追踪，并仅使用针对 32 位字长的确定性整数运算计算 SHA-256 完整性封印。生成的密封包可供 SANS 认证分析师查验，以确认哪些模块处于活跃状态，以及是否发生了静默降级。

由于配置哈希排除了时间戳，且完全依赖精确整数运算——而非浮点近似——该封印具有完全可复现性。两个完全相同的系统配置将始终生成相同的哈希值，从而支持严格的同行复核。

Now tables.

ENGLISH Key Concepts:
| Concept | Scientific Description |
|---|---|
| Immutable Sealing | A one-way, append-only binding process. Once a snapshot is recorded, prior entries cannot be retroactively altered without invalidating the SHA-256 fingerprint. |
| Tamper Detection | Deterministic bitwise comparison between the initial integer hash baseline and the current system state. Any deviation produces an exception or degradation event. |
| Silent Degradation | Loss of analytical capability caused by environment variables or disabled modules that does not trigger an immediate user-visible error. |
| Runtime Integrity | The property that configuration remains invariant during the entire analysis window, verified by exact integer-equality checkpoints. |
| Deterministic Hash (SHA-256) | A reproducible fingerprint computed exclusively through fixed-width integer bitwise operations (AND, OR, XOR, shifts) and modular addition on 32-bit words. No timestamps or floating-point values participate, guaranteeing identical inputs always yield identical outputs. |

ESPAÑOL Key Concepts:
| Concepto | Descripción científica |
|---|---|
| Sellado inmutable | Proceso de vinculación unidireccional y de solo-adición. Una vez registrada una instantánea, las entradas anteriores no pueden alterarse retroactivamente sin invalidar la huella SHA-256. |
| Detección de manipulación | Comparación determinista bit a bit entre la línea base de hash entero inicial y el estado actual del sistema. Cualquier desviación genera una excepción o un evento de degradación. |
| Degradación silenciosa | Pérdida de capacidad analítica causada por variables de entorno o módulos desactivados que no generan un error inmediato visible para el usuario. |
| Integridad en ejecución | Propiedad por la cual la configuración permanece invariante durante toda la ventana de análisis, verificada por puntos de control de igualdad entera exacta. |
| Hash determinista (SHA-256) | Huella reproducible calculada exclusivamente mediante operaciones bit a bit de enteros de ancho fijo (AND, OR, XOR, desplazamientos) y suma modular sobre palabras de 32 bits. No intervienen marcas de tiempo ni valores de punto flotante, garantizando que entradas idénticas produzcan siempre salidas idénticas. |

РУССКИЙ Key Concepts:
| Концепция | Научное описание |
|---|---|
| Неизменное запечатывание | Однонаправленный процесс связывания с добавлением только в конец. После записи снимка предыдущие записи не могут быть ретроспективно изменены без аннулирования отпечатка SHA-256. |
| Обнаружение подделки | Детерминированное побитовое сравнение между исходной базовой линией целочисленного хеша и текущим состоянием системы. Любое отклонение порождает исключение или событие деградации. |
| Скрытая деградация | Потеря аналитической способности, вызванная переменными среды или отключёнными модулями, не приводящая к немедленной вид
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
