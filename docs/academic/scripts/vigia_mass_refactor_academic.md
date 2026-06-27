<!--
VIGIA Academic Documentation
Module: 637ecdc6
Batch ID: vigia-doc-0024-637ecdc6
Generated: 2026-05-20T14:56:47.849810+00:00
-->

# Module Documentation: `scripts/vigia_mass_refactor.py`

## ENGLISH

### What Is This Module?

This module is an industrial-grade batch refacturing engine for the VIGÍA Forensic Suite. Imagine a robotic laboratory technician that reads hundreds of experimental protocol files, detects mislabeled reagents (namespace collisions), removes duplicated safety seals from the wrong containers, repairs broken supply chains (import paths), and ensures that every numerical measurement produces the exact same result on every repetition. It performs these edits automatically but with rigorous safeguards: it can rehearse every move without touching anything (`--dry-run`), backs up every original specimen, fingerprints each file with SHA-256, verifies that modified protocols are grammatically valid before finalizing them, and keeps a cryptographically signed laboratory notebook (audit log).

### Key Concepts

| Concept | Plain-Language Description | Role in Forensic Science |
|---|---|---|
| **Atomic Operation (P0–P2)** | An indivisible, all-or-nothing transformation. If any step fails, the entire operation is aborted, leaving the original file untouched. | Guarantees that evidence containers are never left in a partially altered state. |
| **P0-A Namespace Migration** | Renames mislabeled hypothesis identifiers to resolve tag collisions (e.g., `H_EX_001` duplicates). | Prevents two distinct evidence chains from being mistaken for one another. |
| **P0-B Seal Purge** | Removes unauthorized calls to `ForensicBundle.seal()` from every file except the designated vault (`ebs_v1.py`). | Ensures that cryptographic sealing of forensic bundles happens only at the legally defined boundary. |
| **P0-C Import Correction** | Redirects outdated supply references (`ebs.py`) to the current standard (`ebs_v1`). | Repairs broken logical pathways so that analysis scripts load the correct validation rules. |
| **P1 Determinism Injection** | Replaces uncontrolled precision arithmetic with deterministic, fixed-precision quantization rules, favoring integer-normalized representations where applicable. | Makes entropy calculations bitwise reproducible across independent audits; no floating-point variability. |
| **P2 Legacy Migration Plan** | Generates structured transition blueprints for paired legacy/`_v2` file systems. | Allows researchers to phase out obsolete formats without losing traceability. |
| **Dry Run** | A full rehearsal of all planned changes with zero disk writes. | Lets scientists preview the experiment before altering evidence. |
| **Atomic Write** | Writes new content to a temporary location, then swaps it into place only after syntax validation succeeds; original files are preserved as `.bak`. | Eliminates the risk of corruption during power loss or interruption. |
| **SHA-256 Fingerprint** | A deterministic 256-bit integer hash computed from the exact byte sequence of a file. | Provides a mathematically unique specimen identifier for chain-of-custody records. |
| **AST Validation** | A grammatical check that verifies modified source code follows Python syntax rules before it is accepted. | Equivalent to confirming that a rewritten protocol contains no ambiguous commands. |
| **Audit Log** | An append-only, cryptographically signed ledger recording who changed what, when, and the original file fingerprint. | Satisfies legal and scientific requirements for reproducibility and non-repudiation. |

### Glossary

| Term | Definition |
|---|---|
| **Namespace** | A logical container that keeps names (identifiers) unique so that two different hypotheses do not accidentally share the same label. |
| **Hypothesis ID** | A unique alphanumeric tag assigned to a forensic hypothesis; analogous to a barcode on an evidence bag. |
| **Forensic Bundle** | A digital package containing evidence files and metadata; treated as a single sealed specimen. |
| **Seal / Sealing** | The act of cryptographically locking a bundle so that any later tampering is detectable. |
| **Import** | A directive that tells the system where to retrieve external rules or data structures; analogous to citing a specific laboratory manual. |
| **Legacy Pair** | A matching set of an old-format file and its modernized `_v2` successor. |
| **Entropy Accumulator** | A computational component that gathers randomness or uncertainty metrics from data; in this context, it must behave identically on every run. |
| **Deterministic** | Producing exactly the same output from the same input, with no variation caused by timing, hardware, or hidden randomness. |
| **SHA-256** | A cryptographic hash function that maps data to a fixed-length integer digest; used here as a digital fingerprint. |
| **AST (Abstract Syntax Tree)** | A hierarchical diagram of code grammar, used to verify that text files are valid instructions before execution. |
| **Non-repudiation** | The property that a logged action cannot later be denied by the actor who performed it. |

> 【Scientific Note】
> This module occasionally employs terminology derived from the semiotic frameworks of **Charles Sanders Peirce**, **Umberto Eco**, and **H. Paul Grice**—for example, when discussing how identifiers acquire meaning through context, how imports establish "relevance" between modules, or how a namespace collision represents a breakdown in shared convention. This is **not** mysticism or literary criticism. It is best understood as a **sensor-calibration protocol**: just as a spectrometer must be told which wavelengths correspond to which substances, a forensic software system must be told which symbols correspond to which evidence chains. Peirce's triadic model, Eco's codes, and Grice's cooperative principles are formal descriptions of how signs (IDs, imports, seals) map to real-world referents (evidence bundles, audit events). When a collision occurs, the sensor misreads the sample; the refactor acts as recalibration.

---

## ESPAÑOL

### ¿Qué es este módulo?

Este módulo es un motor de refactorización masiva a escala industrial para la Suite Forense VIGÍA. Piense en él como un técnico de laboratorio robótico que lee cientos de archivos de protocolo experimental, detecta reactivos mal etiquetados (colisiones de espacio de nombres), elimina sellos de seguridad duplicados de los contenedores equivocados, repara cadenas de suministro rotas (rutas de importación) y garantiza que cada medición numérica produzca exactamente el mismo resultado en cada repetición. Realiza estas ediciones automáticamente pero con salvaguardas rigurosas: puede ensayar cada movimiento sin tocar nada (`--dry-run`), respalda cada espécimen original, toma la huella digital de cada archivo con SHA-256, verifica que los protocolos modificados sean gramaticalmente válidos antes de finalizarlos y mantiene un cuaderno de laboratorio firmado criptográficamente (registro de auditoría).

### Conceptos Clave

| Concepto | Descripción en lenguaje sencillo | Papel en la ciencia forense |
|---|---|---|
| **Operación atómica (P0–P2)** | Una transformación indivisible de tipo «todo o nada». Si falla algún paso, se aborta toda la operación, dejando el archivo original intacto. | Garantiza que los contenedores de evidencia nunca queden en un estado parcialmente alterado. |
| **P0-A Migración de namespace** | Renombra identificadores de hipótesis mal etiquetados para resolver colisiones (p. ej., duplicados de `H_EX_001`). | Evita que dos cadenas de evidencia distintas se confundan entre sí. |
| **P0-B Purgado de sellos** | Elimina llamadas no autorizadas a `ForensicBundle.seal()` de todos los archivos excepto la bóveda designada (`ebs_v1.py`). | Asegura que el sellado criptográfico de paquetes forenses ocurra solo en el límite legalmente definido. |
| **P0-C Corrección de imports** | Redirige referencias de suministro obsoletas (`ebs.py`) al estándar actual (`ebs_v1`). | Repara las vías lógicas rotas para que los scripts de análisis carguen las reglas de validación correctas. |
| **P1 Inyección de determinismo** | Reemplaza la aritmética de precisión no controlada por reglas de cuantificación deterministas de precisión fija, dando prioridad a representaciones normalizadas enteras cuando sea aplicable. | Hace que los cálculos de entropía sean reproducibles bit a bit en auditorías independientes; elimina la variación numérica dependiente de la ejecución. |
| **P2 Plan de migración legacy** | Genera planos estructurados de transición para sistemas de archivos emparejados legacy/`_v2`. | Permite a los investigadores eliminar formatos obsoletos sin perder trazabilidad. |
| **Dry run** | Un ensayo completo de todos los cambios planificados sin escrituras en disco. | Permite a los científicos previsualizar el experimento antes de alterar la evidencia. |
| **Escritura atómica** | Escribe el contenido nuevo en una ubicación temporal y lo intercambia solo después de que la validación sintáctica tenga éxito; los archivos originales se conservan como `.bak`. | Elimina el riesgo de corrupción durante un corte de energía o interrupción. |
| **Huella SHA-256** | Un hash entero determinista de 256 bits calculado a partir de la secuencia exacta de bytes de un archivo. | Proporciona un identificador matemáticamente único del espécimen para los registros de cadena de custodia. |
| **Validación AST** | Una verificación gramatical que comprueba que el código fuente modificado siga las reglas sintácticas antes de ser aceptado. | Equivalente a confirmar que un protocolo reescrito no contiene comandos ambiguos. |
| **Registro de auditoría** | Un libro de contabilidad de solo-apéndice, firmado criptográficamente, que registra quién cambió qué, cuándo y la huella digital del archivo original. | Satisface requisitos legales y científicos de reproducibilidad y no repudio. |

### Glosario

| Término | Definición |
|---|---|
| **Namespace (espacio de nombres)** | Un contenedor lógico que mantiene los nombres (identificadores) únicos para que dos hipótesis distintas no compartan accidentalmente la misma etiqueta. |
| **Hypothesis ID** | Una etiqueta alfanumérica única asignada a una hipótesis forense; análoga a un código de barras en una bolsa de evidencia. |
| **Forensic Bundle** | Un paquete digital que contiene archivos de evidencia y metadatos; tratado como un espécimen sellado único. |
| **Seal / Sealing (sellado)** | El acto de bloquear criptográficamente un paquete para que cualquier manipulación posterior sea detectable. |
| **Import** | Una directiva que indica al sistema dónde recuperar reglas o estructuras de datos externas; análogo a citar un manual de laboratorio específico. |
| **Legacy Pair (par legacy)** | Un conjunto emparejado de un archivo en formato antiguo y su sucesor modernizado `_v2`. |
| **Entropy Accumulator (acumulador de entropía)** | Un componente computacional que recoge métricas de aleatoriedad o incertidumbre a partir de datos; en este contexto, debe comportarse de forma idéntica en cada ejecución. |
| **Deterministic (determinista)** | Producir exactamente la misma salida a partir de la misma entrada, sin variación causada por tiempo, hardware o aleatoriedad oculta. |
| **SHA-256** | Una función hash criptográfica que asigna datos a un digest entero de longitud fija; utilizada aquí como huella digital. |
| **AST (Árbol de Sintaxis Abstracta)** | Un diagrama jerárquico de la gramática del código, utilizado para verificar que los archivos de texto sean instrucciones válidas antes de la ejecución. |
| **Non-repudiation (no repudio)** | La propiedad por la cual una acción registrada no puede ser negada posteriormente por el actor que la realizó. |

> 【Nota Científica】
> Este módulo emplea ocasionalmente terminología derivada de los marcos semióticos de **Charles Sanders Peirce**, **Umberto Eco** y **H. Paul Grice**—por ejemplo, al discutir cómo los identificadores adquieren significado mediante el contexto, cómo los imports establecen «relevancia» entre módulos, o cómo una colisión de espacio de nombres representa una ruptura en la convención compartida. Esto **no** es misticismo ni crítica literaria. Se comprende mejor como un **protocolo de calibración de sensores**: así como a un espectrómetro se le debe indicar qué longitudes de onda corresponden a qué sustancias, a un sistema forense informático se le debe indicar qué símbolos corresponden a qué cadenas de evidencia. El modelo triádico de Peirce, los códigos de Eco y los principios cooperativos de Grice son descripciones formales de cómo los signos (IDs, imports, sellos) se mapean a referentes del mundo real (paquetes de evidencia, eventos de auditoría). Cuando ocurre una colisión, el sensor lee mal la muestra; el refactor actúa como una recalibración.

---

## РУССКИЙ

### Что это за модуль?

Этот модуль — это масштабируемый автоматический двигатель рефакторинга для судебно-экспертного комплекса VIGÍA. Возьмите его как роботизированного лаборанта, который читает сотни файлов экспериментальных протоколов, обнаруживает неправильно промаркированные реагенты (столкновения имён), удаляет дублированные защитные пломбы с неподходящих контейнеров, устраняет разрывы в цепочках поставок (пути импорта) и гарантирует, что каждое числовое измерение даёт абсолютно одинаковый результат при каждом повторении. Он выполняет правки автоматически, но с жёсткими гарантиями: может отрепетировать каждое действие, не касаясь файлов (`--dry-run`), создаёт резервные копии каждого оригинального образца, снимает по SHA-256 «отпечатки» каждого файла, проверяет грамматическую корректность изменённых протоколов перед финализацией и ведёт криптографически подписанную лабораторную книгу (журнал аудита).

### Ключевые концепции

| Концепция | Описание простым языком | Роль в судебной экспертизе |
|---|---|---|
| **Атомарная операция (P0–P2)** | Неделимое преобразование типа «всё или ничего». Если какой-либо шаг неудачен, вся операция прерывается, а исходный файл остаётся нетронутым. | Гарантирует, что контейнеры с доказательствами никогда не останутся в частично изменённом состоянии. |
| **P0-A Миграция пространства имён** | Переименовывает неправильно присвоенные идентификаторы гипотез для устранения коллизий меток (например, дубликатов `H_EX_001`). | Предотвращает случайное отождествление двух разных цепочек доказательств. |
| **P0-B Удаление пломб** | Удаляет несанкционированные вызовы `ForensicBundle.seal()` из всех файлов, кроме назначенного хранилища (`ebs_v1.py`). | Обеспечивает криптографическое опечатывание судебных пакетов только в пределах юридически определённой границы. |
| **P0-C Исправление импортов** | Перенаправляет устаревшие ссылки (`ebs.py`) на действующий стандарт (`ebs_v1`). | Устраняет логические разрывы, чтобы аналитические сценарии загружали корректные правила валидации. |
| **P1 Внедрение детерминизма** | Заменяет неуправляемую точную арифметику детерминистскими правилами квантования фиксированной точности, отдавая предпочтение целочисленным нормализованным представлениям, где это применимо. | Делает расчёты энтропии побитово воспроизводимыми при независимых аудитах; устраняет исполнительно-зависимую числовую вариативность. |
| **P2 План миграции legacy** | Генерирует структурированные планы перехода для парных файловых систем legacy/`_v2`. | Позволяет исследователям поэтапно выводить из эксплуатации устаревшие форматы без потери прослеживаемости. |
| **Холостой прогон (dry run)** | Полная репетиция всех запланированных изменений с нулевой записью на диск. | Позволяет учёным предварительно просмотреть эксперимент перед изменением доказательств. |
| **Атомарная запись** | Новое содержимое записывается во временное место и переносится на место только после успешной синтаксической валидации; оригиналы сохраняются как `.bak`. | Устраняет риск повреждения при отключении питания или прерывании. |
| **Отпечаток SHA-256** | Детерминистский 256-битный целочисленный хеш, вычисленный из точной байтовой последовательности файла. | Служит математически уникальным идентификатором образца для записей о цепочке хранения. |
| **AST-валидация** | Грамматическая проверка, подтверждающая, что изменённый исходный код следует правилам синтаксиса, прежде чем он будет принят. | Аналогично подтверждению того, что переписанный протокол не содержит двусмысленных команд. |
| **Журнал аудита** | Дополняемый только, криптографически подписанный реестр, фиксирующий кто, что и когда изменил, а также отпечаток исходного файла. | Удовлетворяет юридические и научные требования воспроизводимости и неотказуемости. |

### Глоссарий

| Термин | Определение |
|---|---|
| **Пространство имён (namespace)** | Логический контейнер, обеспечивающий уникальность имён (идентификаторов), чтобы две разные гипотезы случайно не получили одну и ту же метку. |
| **Hypothesis ID** | Уникальный буквенно-цифровой тег, присвоенный судебной гипотезе; аналогичен штрих-коду на пакете с доказательствами. |
| **Forensic Bundle** | Цифровой пакет, содержащий файлы доказательств и метаданные; рассматривается как единый опечатанный образец. |
| **Seal / Sealing (опечатывание)** | Акт криптографической блокировки пакета, делающий любое последующее вмешательство обнаружимым. |
| **Import (импорт)** | Директива, указывающая системе, где извлечь внешние правила или структуры данных; аналогична ссылке на конкретное лабораторное руководство. |
| **Legacy Pair** | Сопоставленная пара файла устаревшего формата и его современного преемника `_v2`. |
| **Entropy Accumulator (аккумулятор энтропии)** | Вычислительный компонент, собирающий метрики случайности или неопределённости из данных; в данном контексте должен вести себя идентично при каждом запуске. |
| **Deterministic (детерминистский)** | Выдача абсолютно одинакового результата при одинаковом входе без вариаций, вызванных временем, оборудованием или скрытой случайностью. |
| **SHA-256** | Криптографическая хеш-функция, отображающая данные на целочисленный дайджест фиксированной длины; здесь используется как цифровой отпечаток. |
| **AST (Абстрактное синтаксическое дерево)** | Иерархическая диаграмма грамматики кода, используемая для проверки того, что текстовые файлы являются допустимыми инструкциями перед выполнением. |
| **Non-repudiation (неотказуемость)** | Свойство, при котором зарегистрированное действие не может быть впоследствии отрицано субъектом, его совершившим. |

> 【Научное Примечание】
> Этот модуль иногда использует терминологию, заимствованную из семиотических рамок **Чарльза Сандерса Пирса**, **Умберто Эко** и **Г. Пола Грайса** — например, при обсуждении того, как идентификаторы приобретают значение через контекст, как импорты устанавливают «релевантность» между модулями, или как коллизия пространств имён представляет собой нарушение общей конвенции. Это **не** мистицизм и не литературная критика. Лучше всего понимать это как **протокол калибровки датчиков**: подобно тому как спектрометру необходимо указать, какие длины волн соответствуют каким веществам, судебно-программной системе необходимо указать, какие символы соответствуют каким цепочкам доказательств. Триадическая модель Пирса, коды Эко и кооперативные принципы Грайса — это формальные описания того, как знаки (идентификаторы, импорты, пломбы) отображаются на реальные референты (пакеты доказательств, события аудита). Когда происходит коллизия, датчик неправильно считывает образец; рефакторинг действует как перекалибровка.

---

## 中文

### 本模块是什么？

本模块是 VIGÍA 取证套件的工业级批量重构引擎。请将其想象为一名机器人实验室技术员：读取数百个实验协议文件，检测错误标注的试剂（命名空间冲突），从错误容器中移除重复的安全封签，修复断裂的供应链（导入路径），并确保每次数值测量在每次重复时产生完全相同的结果。它自动执行这些编辑，但具有严格的保障措施：可以在不触碰任何内容的情况下演练每一步（`--dry-run`），备份每个原始样本，用 SHA-256 为每个文件取指纹，在最终确认之前验证修改后的协议在语法上是否有效，并保存一份经密码学签名的实验室记录本（审计日志）。

### 核心概念

| 概念 | 通俗描述 | 在取证科学中的作用 |
|---|---|---|
| **原子操作（P0–P2）** | 不可分割的"全有或全无"转换。如果任何步骤失败，整个操作将中止，原始文件保持不变。 | 确保证据容器永远不会处于部分更改的状态。 |
| **P0-A 命名空间迁移** | 重命名错误标注的假设标识符以解决标签冲突（例如 `H_EX_001` 重复）。 | 防止两条不同的证据链被混淆。 |
| **P0-B 封签清除** | 从除指定存储库（`ebs_v1.py`）之外的所有文件中移除对 `ForensicBundle.seal()` 的未经授权调用。 | 确保取证包的密码学封签只在法律定义的边界处发生。 |
| **P0-C 导入纠正** | 将过时的供应引用（`ebs.py`）重定向到当前标准（`ebs_v1`）。 | 修复断裂的逻辑断裂，使分析脚本加载正确的验证规则。 |
| **P1 确定性注入** | 将不受控的精确运算替换为确定性的固定精度量化规则，在适用的情况下优先使用整数归一化表示。 | 使熵计算在独立审计中按位可复现；消除执行相关的数值变动。 |
| **P2 旧版迁移计划** | 为配对的旧版/`_v2` 文件系统生成结构化的过渡蓝图。 | 允许研究人员逐步淘汰过时格式，而不会失去可追溯性。 |
| **试运行（Dry Run）** | 对所有计划变更进行完整演练，零磁盘写入。 | 让科学家在更改证据前预览实验结果。 |
| **原子写入** | 将新内容写入临时位置，仅在语法验证成功后才将其交换到位；原始文件保留为 `.bak`。 | 消除断电或中断期间损坏的风险。 |
| **SHA-256 指纹** | 从文件的精确字节序列计算出的确定性 256 位整数哈希值。 | 为保管链记录提供数学上唯一的样本标识符。 |
| **AST 验证** | 在修改后的源代码被接受之前，验证其是否遵循 Python 语法规则的语法检查。 | 等同于确认重写的协议不包含任何含糊的命令。 |
| **审计日志** | 一个仅追加的、经密码学签名的账本，记录谁在何时更改了什么以及原始文件的指纹。 | 满足可复现性和不可否认性的法律和科学要求。 |

### 术语表

| 术语 | 定义 |
|---|---|
| **命名空间（Namespace）** | 保持名称（标识符）唯一性的逻辑容器，以防止两个不同的假设意外共享同一标签。 |
| **假设 ID（Hypothesis ID）** | 分配给取证假设的唯一字母数字标签；类似于证物袋上的条形码。 |
| **取证工件（Forensic Bundle）** | 包含证据文件和元数据的数字包；被视为单一的密封样本。 |
| **封签（Seal / Sealing）** | 对包进行密码学锁定的行为，使任何后续篡改可被检测到。 |
| **导入（Import）** | 告知系统从哪里检索外部规则或数据结构的指令；类似于引用特定的实验室手册。 |
| **旧版配对（Legacy Pair）** | 旧格式文件与其现代化 `_v2` 继任者的匹配集合。 |
| **熵累加器（Entropy Accumulator）** | 从数据中收集随机性或不确定性指标的计算组件；在此语境中，它必须在每次运行时表现完全相同。 |
| **确定性（Deterministic）** | 从相同输入产生完全相同的输出，不存在由时序、硬件或隐藏随机性引起的变化。 |
| **SHA-256** | 将数据映射为固定长度整数摘要的密码学哈希函数；此处用作数字指纹。 |
| **AST（抽象语法树）** | 代码语法的层级图，用于在执行前验证文本文件是有效的指令。 |
| **不可否认性（Non-repudiation）** | 已记录的操作事后不能被执行该操作的主体否认的属性。 |

> 【科学说明】
> 本模块偶尔使用源自**查尔斯·桑德斯·皮尔斯**、**艾柯**与**格赖斯**符号学框架的术语——例如，讨论标识符如何通过上下文获得意义、导入如何在模块之间建立"相关性"，或命名空间冲突如何代表共同约定的逻辑断裂。这**不是**神秘主义或文学批评。最好将其理解为**传感器校准协议**：正如必须告知光谱仪哪些波长对应哪些物质，也必须告知取证软件系统哪些符号对应哪些证据链。皮尔斯的三元模型、艾柯的编码与格赖斯的合作原则，是对符号（ID、导入、封签）如何映射到现实世界指涉物（证据包、审计事件）的形式化描述。当发生冲突时，传感器误读了样本；重构充当了重新校准。

---

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
