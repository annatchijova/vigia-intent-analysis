<!--
VIGIA Academic Documentation
Module: 2042863e
Batch ID: vigia-doc-0125-2042863e
Generated: 2026-05-20T14:56:47.871425+00:00
-->

# Module Documentation: `vigia/security/sandbox.py`

## ENGLISH

**Module Path:** `vigia/security/sandbox.py`

### What Is This Module?

The VIGÍA sandbox is a deterministic containment substrate for external program execution within digital forensic workflows. It replaces earlier routines that invoked arbitrary system commands without resource budgets, path restrictions, or recursion limits. The module establishes a bounded execution perimeter: every child process receives explicit, kernel-enforced integer ceilings for memory consumption, processor time, output volume, and filesystem traversal depth. By eliminating unbounded behavior, the sandbox ensures that evidence processing remains reproducible, measurable, and tamper-resistant.

### Key Concepts

| Concept | Operational Definition | Deterministic Guarantee |
|---|---|---|
| **Sandbox Boundary** | A logical-kinetic perimeter that isolates a child process from the host operating environment. | Enforced through POSIX `setrlimit` using integer resource descriptors. |
| **Path Confinement** | Restricts filesystem traversal to an explicitly authorized directory prefix; upward or lateral escapes are denied. | Absolute path string comparison; no heuristic resolution. |
| **Depth Limiting** | A vertical cap on directory recursion, expressed as a non-negative integer. | Governed by the constant `VIGIA_GREP_DEPTH`. |
| **Pattern Sanitization** | A deterministic lexical filter that neutralizes symbols which could be reinterpreted by a command interpreter. | Whitelist-based character validation; redundant to the argument-vector dispatch. |
| **Subprocess Wrapper** | An asynchronous execution harness that invokes a binary via an argument list and applies policy hooks before entry. | `preexec()` configures kernel limits before the target image is loaded. |
| **Integer Arithmetic Enforcement** | All resource quotas (bytes, seconds, byte counts) are defined and checked as whole numbers. | No floating-point representation is used; thresholds are exact. |

### Functional Procedures

- **`sandboxed_execute`** — Asynchronous process launcher. Prior to binary entry, the routine invokes `preexec()` to translate sandbox policy into kernel resource limits (`setrlimit`). Memory, CPU-time, and output-size quotas are specified as integer quantities, guaranteeing deterministic enforcement without rounding error.

- **`safe_grep`** — A bounded replacement for legacy unrestricted text search. The routine is confined to a predefined directory root and prohibited from exceeding `VIGIA_GREP_DEPTH` levels of recursion. It returns forensic artifacts (files and matching lines) only from the authorized subtree.

- **`_sanitize_grep_pattern`** — A defense-in-depth lexical scrubber. Although the module dispatches commands through an argument vector (which inherently prevents shell injection), this filter performs deterministic character-level validation on search strings to document intent and reject metacharacters.

- **`preexec()`** — A privileged child-side setup function executed immediately before the target program begins. It materializes the sandbox policy into the process control block by setting hard integer limits on addressable memory and CPU seconds.

- **`VIGIA_GREP_DEPTH`** — A compile-time integer constant specifying the maximum directory descent permitted during evidence search operations.

### Glossary

| Term | Definition |
|---|---|
| **POSIX `setrlimit`** | A kernel system-call interface that constrains per-process consumable resources (e.g., address-space bytes, CPU seconds) by accepting integer limit structures. |
| **P0 Vulnerability** | A critical-severity security flaw. Here, the unrestricted spawning of subprocesses without resource or path constraints. |
| **Subprocess** | An operating-system child process created by a parent to perform an isolated task. |
| **Shell Metacharacter** | A non-literal symbol (e.g., pipe, semicolon, expansion operator) that a command interpreter treats as a control instruction rather than data. |
| **Argument Vector (`exec` list)** | A null-terminated array of string arguments passed directly to the program loader, bypassing shell parsing entirely. |
| **Forensic Artifact** | Any digital object—file, log, or memory excerpt—that holds potential evidentiary value in an investigation. |
| **Deterministic Integer Arithmetic** | The use of fixed-width whole numbers for all calculations and policy thresholds, excluding floating-point approximations and ensuring bitwise reproducibility. |

### 【Scientific Note】— Semiotic Terminology as Analytical Instrumentation

Reference to Peirce's triadic sign (representamen–object–interpretant), Eco's overcoding, or Grice's conversational maxims is sometimes mistaken for metaphysical speculation. These constructs are not mysticism; they are deterministic analytical models, functionally analogous to sensor calibration matrices. Just as a photodetector translates incident photons into quantized voltage readings, semiotic terminology translates communication patterns into structured, measurable variables. A *sign* is a data packet; an *interpretant* is the state change in the receiving system; a *code* is a lookup table. Within VIGÍA, a command string is the sign, its kernel-mediated execution is the object, and the resulting **forensic artifacts** are the interpretants. The **logical fracture** between intended and actual execution is measured and bounded through deterministic integer constraints, not approximated.

---

## ESPAÑOL

**Ruta del módulo:** `vigia/security/sandbox.py`

### ¿Qué es este módulo?

El sandbox VIGÍA es un sustrato de contención determinístico para la ejecución de programas externos dentro de flujos de trabajo forenses digitales. Reemplaza rutinas anteriores que invocaban comandos del sistema sin presupuestos de recursos, restricciones de ruta ni límites de recursión. El módulo establece un perímetro de ejecución acotado: cada proceso hijo recibe techos enteros explícitos, aplicados por el núcleo, para el consumo de memoria, tiempo de procesador, volumen de salida y profundidad de recorrido del sistema de archivos. Al eliminar los comportamientos no acotados, el sandbox garantiza que el procesamiento de evidencias sea reproducible, medible y resistente a manipulaciones.

### Conceptos Clave

| Concepto | Definición Operacional | Garantía Determinista |
|---|---|---|
| **Frontera del Sandbox** | Perímetro lógico-cinético que aísla un proceso hijo del entorno operativo del anfitrión. | Aplicada mediante POSIX `setrlimit` con descriptores de recursos enteros. |
| **Confinamiento de Rutas** | Restringe el recorrido del sistema de archivos a un prefijo de directorio autorizado explícitamente; se niegan los escapes hacia arriba o laterales. | Comparación de cadenas de rutas absolutas; sin resolución heurística. |
| **Limitación de Profundidad** | Tope vertical en la recursión de directorios, expresada como un entero no negativo. | Regida por la constante `VIGIA_GREP_DEPTH`. |
| **Sanitización de Patrones** | Filtro léxico determinista que neutraliza símbolos susceptibles de ser reinterpretados por un intérprete de comandos. | Validación de caracteres basada en lista blanca; redundante respecto al despacho por vector de argumentos. |
| **Envoltorio de Subproceso** | Arnés de ejecución asíncrona que invoca un binario mediante una lista de argumentos y aplica ganchos de política antes de la entrada. | `preexec()` configura los límites del núcleo antes de que se cargue la imagen objetivo. |
| **Aplicación de Aritmética Entera** | Todas las cuotas de recursos (bytes, segundos, recuentos de bytes) se definen y verifican como números enteros. | No se utiliza representación de punto flotante; los umbrales son exactos. |

### Procedimientos Funcionales

- **`sandboxed_execute`** — Lanzador de procesos asíncrono. Antes de la entrada del binario, la rutina invoca `preexec()` para traducir la política del sandbox a límites de recursos del núcleo (`setrlimit`). Las cuotas de memoria, tiempo de CPU y tamaño de salida se especifican como cantidades enteras, garantizando una aplicación determinista sin error de redondeo.

- **`safe_grep`** — Reemplazo acotado para la búsqueda de texto heredada sin restricciones. La rutina está confinada a una raíz de directorio predefinida y se le prohíbe exceder `VIGIA_GREP_DEPTH` niveles de recursión. Devuelve artefactos forenses (archivos y líneas coincidentes) únicamente del subárbol autorizado.

- **`_sanitize_grep_pattern`** — Limpiador léxico de defensa en profundidad. Aunque el módulo despacha comandos a través de un vector de argumentos (lo que inherentemente previene la inyección de shell), este filtro realiza una validación determinista a nivel de caracteres en las cadenas de búsqueda para documentar la intención y rechazar metacaracteres.

- **`preexec()`** — Función de configuración privilegiada ejecutada en el lado del hijo inmediatamente antes de que comience el programa objetivo. Materializa la política del sandbox en el bloque de control del proceso estableciendo límites enteros estrictos sobre la memoria direccionable y los segundos de CPU.

- **`VIGIA_GREP_DEPTH`** — Constante entera de tiempo de compilación que especifica la profundidad máxima de descenso de directorios permitida durante las operaciones de búsqueda de evidencias.

### Glosario

| Término | Definición |
|---|---|
| **POSIX `setrlimit`** | Interfaz de llamada al sistema del núcleo que restringe los recursos consumibles por proceso (p. ej., bytes de espacio de direcciones, segundos de CPU) aceptando estructuras de límites enteros. |
| **Vulnerabilidad P0** | Falla de seguridad de severidad crítica. Aquí, la creación irrestringida de subprocesos sin restricciones de recursos o rutas. |
| **Subproceso** | Proceso hijo del sistema operativo creado por un padre para realizar una tarea aislada. |
| **Metacaracter de Shell** | Símbolo no literal (p. ej., tubería, punto y coma, operador de expansión) que el intérprete de comandos trata como instrucción de control en lugar de dato. |
| **Vector de Argumentos (lista `exec`)** | Arreglo de cadenas de argumentos terminado en nulo pasado directamente al cargador del programa, evitando completamente el análisis del shell. |
| **Artefacto Forense** | Cualquier objeto digital—archivo, registro o extracto de memoria—que posea valor probatorio potencial en una investigación. |
| **Aritmética Determinista de Enteros** | Uso de números enteros de ancho fijo para todos los cálculos y umbrales de política, excluyendo aproximaciones de punto flotante y asegurando reproducibilidad a nivel de bits. |

### 【Nota Científica】— La terminología semiótica como instrumento analítico

La referencia al signo triádico de Peirce (representamen–objeto–interpretante), al sobrecodaje de Eco o a las máximas conversacionales de Grice a veces se confunde con especulación metafísica. Estos constructos no son misticismo; son modelos analíticos deterministas, funcionalmente análogos a las matrices de calibración de sensores. Así como un fotodetector traduce fotones incidentes en lecturas de voltaje cuantizadas, la terminología semiótica traduce patrones de comunicación en variables estructuradas y medibles. Un *signo* es un paquete de datos; un *interpretante* es el cambio de estado en el sistema receptor; un *código* es una tabla de búsqueda. Dentro de VIGÍA, la cadena de comando es el signo, su ejecución mediada por el núcleo es el objeto, y los **artefactos forenses** resultantes son los interpretantes. La **fractura lógica** entre la ejecución pretendida y la real se mide y acota mediante restricciones enteras deterministas, no aproximadas.

---

## РУССКИЙ

**Путь к модулю:** `vigia/security/sandbox.py`

### Что представляет собой этот модуль?

Песочница VIGÍA — это детерминированная среда изоляции для выполнения внешних программ в рамках цифровых судебных рабочих процессов. Она заменяет прежние процедуры, которые вызывали произвольные системные команды без ограничений ресурсов, путей или глубины рекурсии. Модуль устанавливает ограниченный периметр выполнения: каждый дочерний процесс получает явные, принудительно задаваемые ядром целочисленные потолки потребления памяти, процессорного времени, объёма вывода и глубины обхода файловой системы. Устраняя неограниченное поведение, песочница гарантирует воспроизводимость, измеримость и устойчивость к компрометации при обработке доказательств.

### Ключевые концепции

| Концепция | Операционное определение | Детерминированная гарантия |
|---|---|---|
| **Граница песочницы** | Логико-кинетический периметр, изолирующий дочерний процесс от операционной среды хоста. | Реализовано через POSIX `setrlimit` с целочисленными дескрипторами ресурсов. |
| **Ограничение путей** | Сужает обход файловой системы до явно авторизованного префикса каталога; «побеги» вверх или в сторону запрещены. | Сравнение строк абсолютных путей; без эвристического разрешения. |
| **Ограничение глубины** | Вертикальный потолок рекурсии по каталогам, выраженный неотрицательным целым числом. | Управляется константой `VIGIA_GREP_DEPTH`. |
| **Санитизация шаблона** | Детерминированный лексический фильтр, нейтрализующий символы, которые могут быть переинтерпретированы командным интерпретатором. | Проверка символов по белому списку; избыточна при передаче вектора аргументов. |
| **Обертка подпроцесса** | Асинхронная среда выполнения, вызывающая бинарный файл через список аргументов и применяющая политические хуки перед входом. | `preexec()` настраивает лимиты ядра до загрузки целевого образа. |
| **Целочисленное ограничение** | Все квоты ресурсов (байты, секунды, счётчики байтов) определяются и проверяются как целые числа. | Не используется представление с плавающей запятой; пороги точны. |

### Функциональные процедуры

- **`sandboxed_execute`** — Асинхронный запуск процесса. Перед входом в бинарный файл процедура вызывает `preexec()`, чтобы транслировать политику песочницы в ограничения ресурсов ядра (`setrlimit`). Квоты памяти, процессорного времени и объёма вывода задаются целыми величинами, что гарантирует детерминированное принуждение без ошибок округления.

- **`safe_grep`** — Ограниченная замена унаследованному неограниченному текстовому поиску. Процедура ограничена предопределённым корневым каталогом и не может превышать `VIGIA_GREP_DEPTH` уровней рекурсии. Возвращает следственные артефакты (файлы и совпадающие строки) только из авторизованного поддерева.

- **`_sanitize_grep_pattern`** — Лексический скруббер глубокой защиты. Хотя модуль диспетчеризует команды через вектор аргументов (что само по себе предотвращает внедрение командной оболочки), данный фильтр выполняет детерминированную посимвольную валидацию поисковых строк для документирования намерения и отсечения метасимволов.

- **`preexec()`** — Привилегированная функция настройки со стороны дочернего процесса, выполняемая непосредственно перед запуском целевой программы. Она материализует политику песочницы в блок управления процессом, устанавливая жёсткие целочисленные лимиты на адресуемую память и процессорные секунды.

- **`VIGIA_GREP_DEPTH`** — Константа времени компиляции, целое число, определяющее максимально допустимую глубину спуска по каталогам при операциях поиска доказательств.

### Глоссарий

| Термин | Определение |
|---|---|
| **POSIX `setrlimit`** | Интерфейс системного вызова ядра, ограничивающий ресурсы, потребляемые процессом (например, байты адресного пространства, секунды CPU), путём приёма структур целочисленных лимитов. |
| **Уязвимость P0** | Уязвимость критической степени серьёзности. В данном контексте — неограниченное порождение подпроцессов без ограничений ресурсов или путей. |
| **Подпроцесс** | Дочерний процесс операционной системы, создаваемый родительским для выполнения изолированной задачи. |
| **Метасимвол оболочки** | Нелитеральный символ (например, канал, точка с запятой, оператор подстановки), который интерпретатор команд воспринимает как управляющую инструкцию, а не данные. |
| **Вектор аргументов (список `exec`)** | Массив строк аргументов, завершающийся нулём, передаваемый непосредственно загрузчику программы, полностью минуя парсинг оболочки. |
| **Следственный артефакт** | Любой цифровой объект — файл, журнал или фрагмент памяти — имеющий потенциальное доказательственное значение в расследовании. |
| **Детерминированная целочисленная арифметика** | Использование целых чисел фиксированной ширины для всех вычислений и политических порогов, исключающее приближённые вычисления с плавающей запятой и обеспечивающее битовую воспроизводимость. |

### 【Научное примечание】— Семиотическая терминология как аналитический инструмент

Обращение к триадическому знаку Пирса (репрезентамен–объект–интерпретант), к сверхкодированию Эко или к разговорным максимам Грайса иногда ошибочно принимается за метафизическую спекуляцию. Эти конструкты не являются мистицизмом; они представляют собой детерминированные аналитические модели, функционально аналогичные матрицам калибровки датчиков. Как фотодетектор переводит падающие фотоны в квантованные показания напряжения, так и семиотическая терминология переводит паттерны коммуникации в структурированные, измеримые переменные. *Знак* — это пакет данных; *интерпретант* — это изменение состояния в принимающей системе; *код* — это таблица соответствий. Внутри VIGÍA командная строка является знаком, её посредством ядра исполнение — объектом, а полученные **следственные артефакты** — интерпретантами. **Логический разрыв** между предполагаемым и фактическим исполнением измеряется и ограничивается детерминированными целочисленными констрейнтами, а не аппроксимируется.

---

## 中文

**模块路径：** `vigia/security/sandbox.py`

### 本模块是什么？

VIGÍA 沙箱是一个用于数字取证工作流中外程序执行的确定性隔离基板。它取代了早期在调用系统命令时没有任何资源预算、路径限制或递归限制的例程。该模块建立一个受控的执行边界：每个子进程都会收到由内核强制实施的、明确的整数上限，涵盖内存消耗、处理器时间、输出体积和文件系统遍历深度。通过消除无界行为，该沙箱确保证据处理保持可复现、可度量且抗篡改。

### 核心概念

| 概念 | 操作定义 | 确定性保证 |
|---|---|---|
| **沙箱边界** | 将子进程与主机操作环境隔离的逻辑-动能边界。 | 通过 POSIX `setrlimit` 以整数资源描述符强制实施。 |
| **路径限制** | 将文件系统遍历限制在明确授权的目录前缀内；禁止向上或横向逃逸。 | 绝对路径字符串比对；无启发式解析。 |
| **深度限制** | 对目录递归的垂直上限，以非负整数表示。 | 由常量 `VIGIA_GREP_DEPTH` 控制。 |
| **模式净化** | 确定性词法过滤器，中和可能被命令解释器重新解释的符号。 | 基于白名单的字符验证；相对于参数向量分发是冗余的。 |
| **子进程封装器** | 通过参数列表调用二进制文件并在入口前应用策略钩子的异步执行框架。 | `preexec()` 在加载目标镜像之前配置内核限制。 |
| **整数运算执行** | 所有资源配额（字节、秒、字节计数）均定义并以整数形式检查。 | 不使用浮点数表示；阈值是精确的。 |

### 功能程序

- **`sandboxed_execute`** — 异步进程启动器。在二进制入口之前，该例程调用 `preexec()` 将沙箱策略转换为内核资源限制（`setrlimit`）。内存、CPU 时间和输出大小配额以整数数量指定，保证无舍入误差的确定性执行。

- **`safe_grep`** — 对旧版无限制文本搜索的有界替换。该例程被限制在预定义的目录根目录内，禁止超过 `VIGIA_GREP_DEPTH` 级别的递归。仅从授权子树返回取证工件（文件和匹配行）。

- **`_sanitize_grep_pattern`** — 纵深防御词法清洗器。尽管模块通过参数向量分发命令（这本身可以防止 shell 注入），该过滤器仍对搜索字符串执行确定性字符级验证，以记录意图并拒绝元字符。

- **`preexec()`** — 在目标程序开始之前立即在子进程侧执行的特权设置函数。它通过设置可寻址内存和 CPU 秒的硬整数限制将沙箱策略实现为进程控制块。

- **`VIGIA_GREP_DEPTH`** — 编译时整数常量，指定证据搜索操作期间允许的最大目录下降深度。

### 术语表

| 术语 | 定义 |
|---|---|
| **POSIX `setrlimit`** | 内核系统调用接口，通过接受整数限制结构来约束每个进程的可消耗资源（例如地址空间字节、CPU 秒）。 |
| **P0 漏洞** | 关键严重级别的安全缺陷。此处指在没有资源或路径约束的情况下无限制地产生子进程。 |
| **子进程** | 由父进程创建以执行隔离任务的操作系统子进程。 |
| **Shell 元字符** | 命令解释器将其视为控制指令而非数据的非字面符号（例如管道、分号、扩展运算符）。 |
| **参数向量（exec 列表）** | 直接传递给程序加载器的以空值结尾的字符串参数数组，完全绕过 shell 解析。 |
| **取证工件** | 调查中具有潜在证据价值的任何数字对象——文件、日志或内存摘录。 |
| **确定性整数运算** | 对所有计算和策略阈值使用固定宽度整数，排除浮点近似并确保逐位可复现性。 |

### 【科学说明】— 符号学术语作为分析仪器

对皮尔斯三元符号（representamen–object–interpretant）、艾柯的过度编码或格赖斯会话准则的引用，有时被误认为形而上学推测。这些构念不是神秘主义；它们是确定性分析模型，在功能上类似于传感器校准矩阵。正如光电探测器将入射光子转换为量化的电压读数，符号学术语将通信模式转换为结构化的、可测量的变量。*符号*是数据包；*解释项*是接收系统中的状态变化；*编码*是查找表。在 VIGÍA 中，命令字符串是符号，其内核介导的执行是对象，由此产生的**取证工件**是解释项。预期执行与实际执行之间的**逻辑断裂**通过确定性整数约束来测量和界定，而非近似处理。

---

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
