<!--
VIGIA Academic Documentation
Module: f44d4660
Batch ID: vigia-doc-0135-f44d4660
Generated: 2026-05-20T14:56:47.873637+00:00
-->

## ENGLISH

### What Is This Module?

`vigia/sift/memory_forensics.py` is a digital forensic analysis instrument designed to operate on memory dump images (snapshots of a computer's RAM). It functions analogously to an automated laboratory analyzer: a memory dump is inserted, its integrity is cryptographically verified, and the instrument extracts structured artifacts—running processes, suspicious injected code segments, and network connection residues. These artifacts are parsed into integer-based records and passed through deterministic anomaly detectors. The output is a formal analysis report (`MemoryAnalysisResult`) suitable for evidentiary review. No knowledge of the Python language is required to interpret its operation; it is treated here as a dedicated scientific appliance.

All memory addresses are treated as exact integers. All timestamps are Unix epoch integers. All SHA-256 hashes are fixed-length deterministic fingerprints. No floating-point approximations are used for thresholds; all comparisons use exact integer arithmetic or exact string equality.

### Key Concepts and Components

**Table 1 — Core Data Artifacts**

| Record Type | Description | Deterministic Data Types |
|---|---|---|
| `ProcessRecord` | A structured card describing a running program, including its integer Process ID (PID), parent PID, executable path, and creation epoch. | PIDs and timestamps as exact integers. |
| `MalfindRecord` | A structured card describing a suspicious virtual memory region flagged by the Volatility 3 `malfind` plugin. | Start/end offsets as integers; protection flags as bitmasks. |
| `NetworkRecord` | A structured card describing a network socket or connection recovered from RAM. | Ports and IP octets handled as integer tuples; states as categorical strings. |
| `MemoryAnomalyFinding` | A positive deviation flag produced when a detector rule is triggered. | Severity encoded as integer levels (e.g., 1–5). No floating-point scores. |
| `MemoryAnalysisResult` | The final aggregated report. | Aggregated integer counts and exact SHA-256 hash strings. |

**Table 2 — Analysis Engines**

| Component | Function |
|---|---|
| `Volatility3Interface` | Secure gateway to the external Volatility 3 engine. Executes commands as isolated argument lists (never shell-mode), sanitizes paths with `shlex.quote`, restricts file access to an allowlist (`ALLOWED_BASE_PATHS`), enforces a parametric timeout, and verifies the dump's SHA-256 hash before analysis. |
| `VolatilityParsers` | Converts raw text output from Volatility into typed records using deterministic integer extraction. |
| `ProcessTreeAnomalyDetector` | Evaluates process lineage. Uses exact integer PID matching to detect parent-child violations (e.g., a system process spawned by an abnormal parent). |
| `MalfindAnomalyDetector` | Evaluates memory injection patterns. Flags executable pages lacking file backing. |
| `NetworkAnomalyDetector` | Evaluates network artifacts. Flags anomalous connection states or unexpected port integers. |
| `MemoryForensicsEngine` | Master orchestrator. Sequentially executes acquisition → parsing → detection → report compilation. |

**Table 3 — Utility and Acquisition Functions**

| Function | Purpose |
|---|---|
| `get_process_list`, `get_malfind`, `get_netscan`, `get_cmdline` | Acquisition probes that invoke `Volatility3Interface` to retrieve specific artifact categories. |
| `parse_pslist`, `parse_malfind`, `parse_netscan` | Parsing engines that map raw strings to structured records. |
| `resolve_parent_names` | Reconstructs the process tree by integer PID linkage. |
| `name_lower`, `path_lower` | Normalization filters using deterministic character-code conversion. |
| `to_signal` | Converts a record into a discrete anomaly signal via integer-threshold logic. |
| `version` | Reports the instrument version identifier. |
| `detect` (three instances) | The rule-evaluation kernel for each detector; returns a boolean integer flag (0/1). |
| `analyze` | The main assay pipeline; returns a `MemoryAnalysisResult`. |

### Security Controls (P0 Fixes)

| Control | Mechanism | Scientific Rationale |
|---|---|---|
| Command Injection Prevention | `subprocess.run` receives a list of arguments. `shell=True` is strictly prohibited. | Prevents malicious command concatenation, ensuring only the intended deterministic instruction sequence executes. |
| Path Traversal Prevention | `dump_path` is resolved against `ALLOWED_BASE_PATHS`. | Guarantees the analyzer accesses only authorized memory dump repositories. |
| Parametric Timeout | Volatility 3 execution timeout is configurable and wrapped in exception handling. | Prevents indefinite resource occupation; ensures the assay completes within a deterministic wall-clock bound. |
| Integrity Verification | SHA-256 hash of the dump is computed and verified prior to analysis. | Ensures the specimen has not been altered since collection, preserving chain-of-custody validity. |

### Glossary

1. **Memory Dump** — A bit-for-bit copy of volatile RAM, analogous to a frozen tissue sample.
2. **PID (Process Identifier)** — An integer label assigned by the operating system to a running program.
3. **Volatility 3** — An open-source forensic framework for extracting digital artifacts from memory dumps.
4. **Argument List** — A sequence of isolated command tokens, preventing unintended command interpretation.
5. **Allowlist** — A predefined set of permitted file system paths; any request outside this set is rejected.
6. **SHA-256** — A cryptographic hash function producing a 256-bit deterministic fingerprint of a file.
7. **Memory Injection** — The unauthorized placement of executable code into another process's address space.
8. **Anomaly Detector** — A rule-based evaluator that flags deviations from expected system behavior using deterministic logic.
9. **Bitmask** — An integer used to represent multiple Boolean flags simultaneously via binary encoding.
10. **Forensic Artifact** — Any object or data fragment recovered from a digital scene that possesses potential evidentiary value.

> **【Scientific Note】**
> This module employs concepts derived from the semiotic traditions of **Charles Sanders Peirce**, **Umberto Eco**, and **H. P. Grice** (e.g., abductive inference, sign classification, maxim violations). These are formal, deterministic frameworks for pattern recognition, not mystical or divinatory practices. Think of the anomaly detectors as laboratory sensors: a spectrometer does not "intuit" the mass of an ion; it measures deflection along a calibrated magnetic field and outputs a discrete integer mass-to-charge ratio. Likewise, when this module detects a "violation of a Gricean maxim" in process behavior—such as an unexpected parent-child relationship—it is recording a deterministic deviation from an expected communication protocol, exactly as a thermometer records a deviation from a baseline temperature. The use of **abduction** here is strictly logical: given an anomalous memory pattern (the index), the system selects the most plausible explanation from a finite rule set (the encyclopedia), producing a deterministic diagnostic signal. No esoteric reasoning is involved.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## ESPAÑOL

### ¿Qué es este módulo?

`vigia/sift/memory_forensics.py` es un instrumento de análisis forense digital diseñado para operar sobre imágenes de volcado de memoria (capturas de la RAM del equipo). Funciona como un analizador automatizado de laboratorio: se introduce el volcado, se verifica su integridad criptográfica y el instrumento extrae artefactos estructurados —procesos en ejecución, segmentos de código sospechosos inyectados y residuos de conexiones de red—. Estos artefactos se parsean en registros basados en enteros y se someten a detectores de anomalías deterministas. El resultado es un informe formal (`MemoryAnalysisResult`) apto para revisión probatoria.

Todas las direcciones de memoria se tratan como enteros exactos. Todas las marcas temporales son enteros de época Unix. Todos los hashes SHA-256 son huellas digitales deterministas de longitud fija. No se emplean aproximaciones de punto flotante para los umbrales; todas las comparaciones usan aritmética entera exacta o igualdad de cadenas exacta.

### Conceptos clave y componentes

**Tabla 1 — Artefactos de datos principales**

| Tipo de Registro | Descripción | Tipos de datos deterministas |
|---|---|---|
| `ProcessRecord` | Tarjeta estructurada que describe un programa en ejecución: PID entero, PID padre, ruta ejecutable y época de creación. | PID y marcas de tiempo como enteros exactos. |
| `MalfindRecord` | Tarjeta estructurada que describe una región de memoria virtual sospechosa detectada por el plugin `malfind` de Volatility 3. | Desplazamientos inicial/final como enteros; permisos como máscaras de bits enteras. |
| `NetworkRecord` | Tarjeta estructurada que describe un socket o conexión de red recuperada de la RAM. | Puertos y octetos IP como tuplas de enteros; estados como cadenas categóricas. |
| `MemoryAnomalyFinding` | Bandera de desviación positiva producida cuando se dispara una regla del detector. | Severidad codificada como niveles enteros (p. ej., 1–5). Sin puntuaciones de punto flotante. |
| `MemoryAnalysisResult` | Informe final agregado. | Conteos enteros agregados y cadenas hash SHA-256 exactas. |

**Tabla 2 — Motores de análisis**

| Componente | Función |
|---|---|
| `Volatility3Interface` | Puerta de enlace segura al motor Volatility 3 externo. Ejecuta comandos como listas de argumentos aisladas (nunca modo shell), sanitiza rutas con `shlex.quote`, restringe el acceso a una lista de permisos (`ALLOWED_BASE_PATHS`), impone un tiempo de espera paramétrico y verifica el hash SHA-256 del volcado antes del análisis. |
| `VolatilityParsers` | Convierte la salida de texto crudo de Volatility en registros tipados mediante extracción determinista de enteros. |
| `ProcessTreeAnomalyDetector` | Evalúa el linaje de procesos. Utiliza coincidencia exacta de PID enteros para detectar violaciones padre-hijo. |
| `MalfindAnomalyDetector` | Evalúa patrones de inyección de memoria. Marca páginas ejecutables sin respaldo de archivo. |
| `NetworkAnomalyDetector` | Evalúa artefactos de red. Marca estados de conexión anómalos o puertos enteros inesperados. |
| `MemoryForensicsEngine` | Orquestador maestro. Ejecuta secuencialmente adquisición → parseo → detección → compilación de informes. |

### Controles de seguridad (Correcciones P0)

| Control | Mecanismo | Fundamento científico |
|---|---|---|
| Prevención de inyección de comandos | `subprocess.run` recibe una lista de argumentos. `shell=True` está estrictamente prohibido. | Evita la concatenación maliciosa de comandos. |
| Prevención de recorrido de rutas | `dump_path` se resuelve contra `ALLOWED_BASE_PATHS`. | Garantiza que el analizador acceda solo a repositorios de volcados autorizados. |
| Tiempo de espera paramétrico | El tiempo de espera de ejecución de Volatility 3 es configurable. | Previene la ocupación indefinida de recursos. |
| Verificación de integridad | El hash SHA-256 del volcado se computa y verifica antes del análisis. | Preserva la validez de la cadena de custodia. |

### Glosario

1. **Volcado de memoria** — Copia bit a bit de la RAM volátil, análoga a una muestra de tejido congelada.
2. **PID (Identificador de Proceso)** — Etiqueta entera asignada por el sistema operativo a un programa en ejecución.
3. **Volatility 3** — Marco forense de código abierto para extraer artefactos digitales de volcados de memoria.
4. **Lista de argumentos** — Secuencia de tokens de comando aislados que impide la interpretación no deseada de comandos.
5. **Lista de permisos (Allowlist)** — Conjunto predefinido de rutas permitidas; cualquier solicitud fuera de este conjunto es rechazada.
6. **SHA-256** — Función hash criptográfica que produce una huella digital determinista de 256 bits.
7. **Inyección de memoria** — Colocación no autorizada de código ejecutable en el espacio de direcciones de otro proceso.
8. **Detector de anomalías** — Evaluador basado en reglas que marca desviaciones del comportamiento esperado usando lógica determinista.
9. **Máscara de bits** — Entero utilizado para representar múltiples banderas booleanas mediante codificación binaria.
10. **Artefacto forense** — Cualquier objeto o fragmento de datos recuperado de una escena digital con valor probatorio potencial.

> **【Nota Científica】**
> Este módulo emplea conceptos derivados de las tradiciones semióticas de **Charles Sanders Peirce**, **Umberto Eco** y **H. P. Grice** (p. ej., inferencia abductiva, clasificación de signos, violación de máximas). Se trata de marcos formales y deterministas para el reconocimiento de patrones, no de prácticas místicas. Piense en los detectores de anomalías como sensores de laboratorio: un espectrómetro no "intuye" la masa de un ion; mide la desviación a lo largo de un campo magnético calibrado y produce una relación masa-carga entera discreta. Del mismo modo, cuando este módulo detecta una "violación de una máxima griceana" en el comportamiento de un proceso —como una relación padre-hijo inesperada— está registrando una desviación determinista de un protocolo de comunicación esperado. El uso de la **abducción** es estrictamente lógico: dado un patrón de memoria anómalo (el índice), el sistema selecciona la explicación más plausible desde un conjunto finito de reglas (la enciclopedia), produciendo una señal diagnóstica determinista.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## РУССКИЙ

### Что представляет собой этот модуль?

`vigia/sift/memory_forensics.py` — цифровой судебно-экспертный анализатор, предназначенный для работы с дампами памяти (снимками оперативной памяти компьютера). Он действует как автоматизированный лабораторный прибор: в него загружается дамп, проверяется его криптографическая целостность, после чего прибор извлекает структурированные цифровые артефакты — запущенные процессы, подозрительные внедрённые сегменты кода и остаточные данные сетевых соединений. Артефакты преобразуются в записи на основе целых чисел и проходят через детерминированные детекторы аномалий. Результатом служит формальный отчёт (`MemoryAnalysisResult`), пригодный для доказательственного анализа.

Все адреса памяти трактуются как точные целые числа. Все временны́е метки — целочисленные эпохи Unix. Все хэши SHA-256 — детерминированные отпечатки фиксированной длины. Приближения с плавающей точкой для порогов не используются; все сравнения применяют точную целочисленную арифметику.

### Ключевые понятия и компоненты

**Таблица 1 — Основные цифровые артефакты**

| Тип записи | Описание | Детерминированные типы данных |
|---|---|---|
| `ProcessRecord` | Структурированная карта, описывающая запущенную программу: целочисленный PID, родительский PID, путь к исполняемому файлу и время создания. | PID и временны́е метки — точные целые числа. |
| `MalfindRecord` | Структурированная карта, описывающая подозрительный регион виртуальной памяти, выявленный плагином `malfind` Volatility 3. | Начальное/конечное смещение — целые числа; права доступа — битовые маски. |
| `NetworkRecord` | Структурированная карта, описывающая сетевой сокет или соединение, восстановленное из RAM. | Порты и октеты IP — кортежи целых чисел; состояния — категориальные строки. |
| `MemoryAnomalyFinding` | Флаг положительного отклонения, генерируемый при срабатывании правила детектора. | Серьёзность кодируется целыми уровнями (например, 1–5). |
| `MemoryAnalysisResult` | Итоговый агрегированный отчёт. | Агрегированные целочисленные счётчики и точные строки хэша SHA-256. |

**Таблица 2 — Аналитические движки**

| Компонент | Функция |
|---|---|
| `Volatility3Interface` | Защищённый шлюз к внешнему движку Volatility 3. Выполняет команды в виде изолированных списков аргументов (никогда в режиме shell), санитирует пути с помощью `shlex.quote`, ограничивает доступ к каталогам из белого списка (`ALLOWED_BASE_PATHS`), устанавливает параметрический тайм-аут и проверяет хэш SHA-256 дампа перед анализом. |
| `VolatilityParsers` | Преобразует сырой текстовый вывод Volatility в типизированные записи с извлечением целых чисел по детерминированным правилам. |
| `ProcessTreeAnomalyDetector` | Анализирует родословную процессов. Использует точное сопоставление целочисленных PID для выявления нарушений в отношениях родитель-потомок. |
| `MalfindAnomalyDetector` | Анализирует паттерны внедрения в память. Помечает исполняемые страницы без файлового резервирования. |
| `NetworkAnomalyDetector` | Анализирует сетевые артефакты. Помечает аномальные состояния соединений или неожиданные целочисленные номера портов. |
| `MemoryForensicsEngine` | Главный оркестратор. Последовательно выполняет этапы: захват → разбор → обнаружение → формирование отчёта. |

### Средства управления безопасностью (Исправления P0)

| Средство управления | Механизм | Научное обоснование |
|---|---|---|
| Предотвращение инъекции команд | `subprocess.run` получает список аргументов. `shell=True` строго запрещён. | Предотвращает вредоносную конкатенацию команд. |
| Предотвращение обхода путей | `dump_path` разрешается против `ALLOWED_BASE_PATHS`. | Гарантирует, что анализатор обращается только к авторизованным репозиториям дампов. |
| Параметрический тайм-аут | Время выполнения Volatility 3 настраивается и оборачивается в обработчик исключений. | Предотвращает неопределённое потребление ресурсов. |
| Верификация целостности | Хэш SHA-256 дампа вычисляется и проверяется до анализа. | Сохраняет достоверность цепочки сохранения. |

### Глоссарий

1. **Дамп памяти** — Побитовая копия оперативной памяти, аналогичная замороженному образцу ткани.
2. **PID (Идентификатор процесса)** — Целочисленная метка, присвоенная операционной системой запущенной программе.
3. **Volatility 3** — Открытый криминалистический фреймворк для извлечения цифровых артефактов из дампов памяти.
4. **Список аргументов** — Последовательность изолированных токенов команды, предотвращающая нежелательную интерпретацию команд.
5. **Белый список (Allowlist)** — Предопределённый набор разрешённых путей файловой системы; любой запрос вне этого набора отклоняется.
6. **SHA-256** — Криптографическая хэш-функция, производящая детерминированный отпечаток длиной 256 бит.
7. **Внедрение в память** — Несанкционированное размещение исполняемого кода в адресном пространстве другого процесса.
8. **Детектор аномалий** — Основанный на правилах оценщик, помечающий отклонения от ожидаемого поведения системы с использованием детерминированной логики.
9. **Битовая маска** — Целое число, используемое для представления нескольких булевых флагов посредством двоичного кодирования.
10. **Цифровой артефакт** — Любой объект или фрагмент данных, восстановленный из цифровой сцены, обладающий потенциальной доказательственной ценностью.

> **【Научное примечание】**
> Модуль задействует концепции семиотических традиций **Чарльза Сандерса Пирса**, **Умберто Эко** и **Г. П. Грайса** (напр., абдуктивный вывод, классификация знаков, нарушение максим). Это формальные, детерминированные рамки для распознавания паттернов, не мистические практики. Воспринимайте детекторы аномалий как лабораторные датчики: спектрометр не «интуирует» массу иона — он измеряет отклонение вдоль калиброванного магнитного поля и выдаёт дискретное целочисленное отношение масса/заряд. Аналогично, когда модуль обнаруживает «нарушение грайсовской максимы» в поведении процесса — например, неожиданное отношение родитель-потомок — он фиксирует детерминированное отклонение от ожидаемого протокола коммуникации. Использование **абдукции** здесь строго логично: по аномальному паттерну памяти (индексу) система выбирает наиболее правдоподобное объяснение из конечного набора правил (энциклопедии), производя детерминированный диагностический сигнал.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## 中文

### 本模块是什么？

`vigia/sift/memory_forensics.py` 是一个数字取证分析仪器，专为操作内存转储镜像（计算机 RAM 快照）而设计。它的功能类似于自动化实验室分析仪：插入内存转储，对其进行密码学完整性验证，然后仪器提取结构化取证工件——运行中的进程、可疑注入代码段和网络连接残留。这些取证工件被解析为基于整数的记录，并通过确定性异常检测器处理。输出是适合证据审查的正式分析报告（`MemoryAnalysisResult`）。

所有内存地址均视为精确整数。所有时间戳均为 Unix 纪元整数。所有 SHA-256 哈希均为固定长度确定性指纹。阈值不使用浮点近似；所有比较使用精确整数算术或精确字符串相等性。

### 核心概念与组件

**表 1 — 核心数据取证工件**

| 记录类型 | 描述 | 确定性数据类型 |
|---|---|---|
| `ProcessRecord` | 描述运行中程序的结构化记录：整数进程 ID (PID)、父 PID、可执行路径和创建纪元。 | PID 和时间戳为精确整数。 |
| `MalfindRecord` | 描述 Volatility 3 `malfind` 插件标记的可疑虚拟内存区域的结构化记录。 | 起始/结束偏移量为整数；保护标志为位掩码。 |
| `NetworkRecord` | 描述从 RAM 中恢复的网络套接字或连接的结构化记录。 | 端口和 IP 八位字节作为整数元组处理；状态为分类字符串。 |
| `MemoryAnomalyFinding` | 当检测器规则触发时产生的正偏差标志。 | 严重程度编码为整数级别（如 1-5）。无浮点评分。 |
| `MemoryAnalysisResult` | 最终汇总报告。 | 汇总整数计数和精确 SHA-256 哈希字符串。 |

**表 2 — 分析引擎**

| 组件 | 功能 |
|---|---|
| `Volatility3Interface` | 外部 Volatility 3 引擎的安全网关。以隔离参数列表（绝不使用 shell 模式）执行命令，用 `shlex.quote` 消毒路径，限制文件访问至允许列表（`ALLOWED_BASE_PATHS`），强制参数化超时，并在分析前验证转储的 SHA-256 哈希。 |
| `VolatilityParsers` | 使用确定性整数提取将 Volatility 的原始文本输出转换为类型化记录。 |
| `ProcessTreeAnomalyDetector` | 评估进程血统。使用精确整数 PID 匹配检测父子关系违规（如系统进程由异常父进程生成）。 |
| `MalfindAnomalyDetector` | 评估内存注入模式。标记缺乏文件备份的可执行页面。 |
| `NetworkAnomalyDetector` | 评估网络取证工件。标记异常连接状态或意外整数端口号。 |
| `MemoryForensicsEngine` | 主编排器。顺序执行：采集 → 解析 → 检测 → 报告编译。 |

### 安全控制（P0 修复）

| 控制 | 机制 | 科学依据 |
|---|---|---|
| 命令注入防护 | `subprocess.run` 接收参数列表。严格禁止 `shell=True`。 | 防止恶意命令拼接，确保仪器只执行预期的确定性指令序列。 |
| 路径遍历防护 | `dump_path` 对照 `ALLOWED_BASE_PATHS` 进行解析。 | 确保分析仪只访问授权的内存转储存储库。 |
| 参数化超时 | Volatility 3 执行超时可配置，并包含异常处理。 | 防止无限期资源占用；确保分析在确定性挂钟限制内完成。 |
| 完整性验证 | 分析前计算并验证转储的 SHA-256 哈希。 | 确保样本自采集以来未被修改，保持监管链有效性。 |

### 术语表

1. **内存转储** — 易失性 RAM 的逐位副本，类似于冷冻组织样本。
2. **PID（进程标识符）** — 操作系统分配给运行程序的整数标签。
3. **Volatility 3** — 用于从内存转储中提取数字取证工件的开源取证框架。
4. **参数列表** — 隔离命令令牌的序列，防止意外的命令解释。
5. **允许列表** — 预定义的允许文件系统路径集；此集合外的任何请求均被拒绝。
6. **SHA-256** — 产生文件 256 位确定性指纹的密码哈希函数。
7. **内存注入** — 将可执行代码未经授权放置到另一进程地址空间的行为。
8. **异常检测器** — 使用确定性逻辑标记偏离预期系统行为的基于规则的评估器。
9. **位掩码** — 通过二进制编码同时表示多个布尔标志的整数。
10. **取证工件** — 从数字场景中恢复的任何具有潜在证据价值的对象或数据片段。

> **【科学说明】**
> 本模块采用源自**查尔斯·桑德斯·皮尔士**、**艾柯**和**格赖斯**语义传统的概念（如溯因推断、符号分类、准则违反）。这些是用于模式识别的正式、确定性框架，而非神秘或占卜实践。将异常检测器视为实验室传感器：质谱仪不"直觉感知"离子质量——它测量沿校准磁场的偏转并输出离散整数质荷比。同样，当本模块检测到进程行为中的"格赖斯准则违反"——如意外的父子关系——时，它记录的是偏离预期通信协议的确定性偏差，就像温度计记录偏离基线温度一样。此处**溯因推断**的使用严格合乎逻辑：给定异常内存模式（索引），系统从有限规则集（百科全书）中选择最合理的解释，产生确定性诊断信号。不涉及任何神秘推理。

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
