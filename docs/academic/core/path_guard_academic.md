<!--
VIGIA Academic Documentation
Module: 608005f0
Batch ID: vigia-doc-0068-608005f0
Generated: 2026-05-20T14:56:47.859121+00:00
-->

---

## ENGLISH

### What Is This Module?
`vigia/core/path_guard.py` is a deterministic access-control engine for digital forensics. It functions as a security checkpoint for files before they are opened or read. Rather than trusting a file path at face value, the module verifies that the filesystem object has not been substituted or altered between the moment it is inspected and the moment it is used. All verification relies on exact integer comparisons of kernel-reported metadata—inode numbers, byte sizes, and modification timestamps. Because filesystem states are discrete and countable, the module uses deterministic integer arithmetic exclusively; floating-point representations are neither necessary nor appropriate.

### Key Concepts

| Concept | Plain-Language Explanation | Scientific Relevance |
|---|---|---|
| **TOCTOU Hardening** | Closing the time window between "checking" a file and "using" it so an attacker cannot swap the file in between. | Prevents evidence tampering during acquisition. |
| **Symlink Detection (`lstat`)** | Inspecting a path’s own metadata without following shortcuts (symbolic links). | Ensures the examiner analyzes the true target, not a redirected decoy. |
| **Descriptor-Based Verification (`fstat`)** | Querying an already-open file handle for metadata, independent of the path string. | Eliminates race conditions because the handle points to a specific, immutable inode. |
| **Regular-File Check (`S_ISREG`)** | Confirming the object is a plain file—not a device, pipe, or socket—before reading. | Protects forensic workstations from unexpected system streams. |
| **Shared Lock (`flock`)** | Placing a non-exclusive lock on the file while reading so concurrent writers must wait. | Guarantees atomic integrity of integer metadata snapshots during acquisition. |
| **Deterministic Integer Metadata** | `inode`, `size`, and `mtime` are whole numbers reported by the kernel; equality is exact. | Floating-point math is excluded because filesystem identity is a countable, discrete state. |

### Glossary

- **PathValidationResult** — A structured record indicating whether a path passed all security checks.
- **PathGuard** — The primary controller class that orchestrates validation, opening, and reading.
- **SecurityException** — An alarm raised when a security rule is violated (e.g., symlink detected or TOCTOU mismatch).
- **validate()** — The initial checkpoint. Returns a result after checking for symlinks and regular-file status using integer metadata obtained via `lstat()`.
- **verify_no_toctou()** — The second checkpoint. Re-compares the `inode`, `size`, and `mtime` integers obtained *after* opening against those recorded *before* opening. Any mismatch signals an attack.
- **safe_open()** — A guarded open operation that chains validation, descriptor acquisition, and post-open TOCTOU verification using deterministic integer arithmetic.
- **safe_read()** — A guarded read operation that performs `safe_open()`, applies a shared `flock`, reads content, and confirms metadata integrity remained intact throughout.
- **lstat()** — A system call that inspects a path directly without traversing symbolic links.
- **fstat()** — A system call that inspects an already-open file descriptor, bypassing the path layer entirely.
- **inode** — An integer index that uniquely identifies a file object inside a filesystem.
- **mtime** — Modification time, recorded as an integer timestamp.
- **flock** — A kernel-managed advisory lock placed on a file descriptor.

### 【Scientific Note】
The terminology of Charles Sanders Peirce (semiotic signs), Umberto Eco (code and interpretation), and H. P. Grice (cooperative principles) appears in forensic literature as an analytical vocabulary, not as mysticism. Consider a digital sensor: a device transforms a physical state into an integer reading. In this module, the filesystem state is transformed into a triplet of exact integers — `inode`, `size`, and `mtime`. Peirce’s indexical sign is the kernel metadata that points directly to a file object by causal trace, not by resemblance. Eco’s code is the deterministic protocol that maps those integers to a security verdict. Grice’s cooperative maxims enforce the expectation that a file path behaves consistently between inspection and use; when it does not, the cooperative contract is broken — a forensic signal of adversarial substitution.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## ESPAÑOL

### ¿Qué es este módulo?

`vigia/core/path_guard.py` es un motor de control de acceso determinista para la informática forense. Funciona como un puesto de control de seguridad para los archivos antes de que sean abiertos o leídos. En lugar de confiar en una ruta de archivo a su valor nominal, el módulo verifica que el objeto del sistema de archivos no haya sido sustituido o alterado entre el momento en que se inspecciona y el momento en que se utiliza. Toda la verificación se basa en comparaciones enteras exactas de metadatos reportados por el kernel — números de inodo, tamaños en bytes y marcas temporales de modificación. Dado que los estados del sistema de archivos son discretos y contables, el módulo utiliza exclusivamente aritmética entera determinista; las representaciones de punto flotante no son necesarias ni apropiadas.

### Conceptos clave

| Concepto | Explicación | Relevancia científica |
|---|---|---|
| **Endurecimiento TOCTOU** | Cierre de la ventana temporal entre "verificar" un archivo y "usarlo" para que un atacante no pueda intercambiarlo. | Previene la manipulación de evidencia durante la adquisición. |
| **Detección de enlaces simbólicos (`lstat`)** | Inspección de los metadatos propios de una ruta sin seguir atajos (enlaces simbólicos). | Garantiza que el examinador analice el objetivo real, no un señuelo redirigido. |
| **Verificación basada en descriptor (`fstat`)** | Consulta de metadatos sobre un manejador de archivo ya abierto, independiente de la cadena de ruta. | Elimina condiciones de carrera porque el manejador apunta a un inodo específico e inmutable. |
| **Verificación de archivo regular (`S_ISREG`)** | Confirmación de que el objeto es un archivo plano —no un dispositivo, tubería o socket— antes de leer. | Protege las estaciones de trabajo forenses de flujos de sistema inesperados. |
| **Bloqueo compartido (`flock`)** | Colocación de un bloqueo no exclusivo en el archivo durante la lectura para que los escritores concurrentes esperen. | Garantiza la integridad atómica de las instantáneas de metadatos enteros durante la adquisición. |
| **Metadatos enteros deterministas** | `inode`, `size` y `mtime` son números enteros reportados por el kernel; la igualdad es exacta. | La aritmética de punto flotante se excluye porque la identidad del sistema de archivos es un estado discreto y contable. |

> **【Nota Científica】**
> La terminología de Charles Sanders Peirce, Umberto Eco y H. P. Grice aparece en la literatura forense como vocabulario analítico, no como misticismo. Considere un sensor digital: un dispositivo transforma un estado físico en una lectura entera. En este módulo, el estado del sistema de archivos se transforma en una tripleta de enteros exactos — `inode`, `size` y `mtime`. El signo indexical de Peirce es simplemente el metadato del kernel que apunta directamente a un objeto de archivo por traza causal. El código de Eco es el protocolo determinista que mapea esos enteros a un veredicto de seguridad. Las máximas cooperativas de Grice imponen la expectativa de que una ruta de archivo se comporte de forma consistente entre la inspección y el uso; cuando no lo hace, el contrato cooperativo está roto — una señal forense de sustitución adversarial.

### Glosario

1. **PathValidationResult** — Registro estructurado que indica si una ruta pasó todas las verificaciones de seguridad.
2. **PathGuard** — La clase controladora principal que orquesta la validación, apertura y lectura.
3. **SecurityException** — Alarma lanzada cuando se viola una regla de seguridad (por ejemplo, enlace simbólico detectado o discrepancia TOCTOU).
4. **validate()** — El primer punto de control. Devuelve un resultado tras verificar enlaces simbólicos y estado de archivo regular usando metadatos enteros obtenidos mediante `lstat()`.
5. **verify_no_toctou()** — El segundo punto de control. Compara los enteros `inode`, `size` y `mtime` obtenidos *después* de abrir con los registrados *antes* de abrir.
6. **safe_open()** — Operación de apertura protegida que encadena validación, adquisición de descriptor y verificación TOCTOU post-apertura.
7. **safe_read()** — Operación de lectura protegida que ejecuta `safe_open()`, aplica un `flock` compartido, lee el contenido y confirma la integridad de los metadatos.
8. **lstat()** — Llamada al sistema que inspecciona una ruta directamente sin atravesar enlaces simbólicos.
9. **fstat()** — Llamada al sistema que inspecciona un descriptor de archivo ya abierto, sin pasar por la capa de ruta.
10. **inode** — Índice entero que identifica de forma única un objeto de archivo dentro de un sistema de archivos.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## РУССКИЙ

### Что это за модуль?

`vigia/core/path_guard.py` — детерминированный движок контроля доступа для цифровой криминалистики. Он функционирует как контрольно-пропускной пункт безопасности для файлов перед их открытием или чтением. Вместо того чтобы доверять пути к файлу по номинальной стоимости, модуль проверяет, что объект файловой системы не был подменён или изменён в промежутке между моментом его проверки и моментом использования. Вся верификация основана на точных целочисленных сравнениях метаданных, сообщаемых ядром, — номеров инодов, размеров в байтах и временны́х меток изменения. Поскольку состояния файловой системы дискретны и перечислимы, модуль использует исключительно детерминированную целочисленную арифметику; представления с плавающей запятой здесь ни необходимы, ни уместны.

### Ключевые концепции

| Концепция | Объяснение | Научная значимость |
|---|---|---|
| **Защита от TOCTOU** | Закрытие временно́го окна между «проверкой» файла и его «использованием», чтобы злоумышленник не мог подменить файл. | Предотвращает фальсификацию доказательств при сборе. |
| **Обнаружение символических ссылок (`lstat`)** | Инспекция собственных метаданных пути без следования ярлыкам (символическим ссылкам). | Гарантирует, что эксперт анализирует истинный объект, а не подставной. |
| **Верификация по дескриптору (`fstat`)** | Запрос метаданных у уже открытого дескриптора файла, независимо от строки пути. | Устраняет состояния гонки, поскольку дескриптор указывает на конкретный неизменяемый инод. |
| **Проверка обычного файла (`S_ISREG`)** | Подтверждение того, что объект является обычным файлом — не устройством, каналом или сокетом. | Защищает криминалистические рабочие станции от неожиданных системных потоков. |
| **Общая блокировка (`flock`)** | Установка неисключительной блокировки файла при чтении, чтобы параллельные операции записи ожидали. | Гарантирует атомарную целостность целочисленных снимков метаданных при сборе. |
| **Детерминированные целочисленные метаданные** | `inode`, `size` и `mtime` — целые числа, сообщаемые ядром; равенство точное. | Арифметика с плавающей запятой исключена, поскольку идентичность файловой системы является дискретным, перечислимым состоянием. |

> **【Научное примечание】**
> Терминология Чарльза Сандерса Пирса, Умберто Эко и Г. П. Грайса в криминалистической литературе выступает как аналитический словарь, а не мистицизм. Рассмотрим цифровой датчик: устройство преобразует физическое состояние в целочисленное значение. В данном модуле состояние файловой системы преобразуется в тройку точных целых чисел — `inode`, `size` и `mtime`. Индексальный знак Пирса — это просто метаданные ядра, указывающие на файловый объект по причинно-следственной трассе. Код Эко — детерминированный протокол, отображающий эти целые числа на вердикт безопасности. Кооперативные максимы Грайса устанавливают ожидание, что путь к файлу будет вести себя последовательно между инспекцией и использованием; когда этого не происходит, кооперативный контракт нарушен — это криминалистический сигнал об adversarial-подмене.

### Глоссарий

1. **PathValidationResult** — Структурированная запись, указывающая, прошёл ли путь все проверки безопасности.
2. **PathGuard** — Основной класс-контроллер, оркестрирующий валидацию, открытие и чтение.
3. **SecurityException** — Исключение, возбуждаемое при нарушении правила безопасности (например, обнаружение символической ссылки или несоответствие TOCTOU).
4. **validate()** — Первая контрольная точка. Возвращает результат после проверки символических ссылок и статуса обычного файла через `lstat()`.
5. **verify_no_toctou()** — Вторая контрольная точка. Сравнивает целые числа `inode`, `size` и `mtime`, полученные *после* открытия, с записанными *до* открытия.
6. **safe_open()** — Охраняемая операция открытия, объединяющая валидацию, получение дескриптора и post-open TOCTOU верификацию.
7. **safe_read()** — Охраняемая операция чтения, выполняющая `safe_open()`, применяющая общую блокировку `flock`, читающая содержимое и подтверждающая целостность метаданных.
8. **lstat()** — Системный вызов, инспектирующий путь напрямую без следования символическим ссылкам.
9. **fstat()** — Системный вызов, инспектирующий уже открытый дескриптор файла в обход слоя пути.
10. **inode** — Целочисленный индекс, уникально идентифицирующий файловый объект внутри файловой системы.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## 中文

### 这是什么模块？

`vigia/core/path_guard.py` 是数字取证领域的确定性访问控制引擎。它在文件被打开或读取之前充当安全检查站。该模块不是简单地信任文件路径的表面值，而是验证文件系统对象在检查时刻与使用时刻之间没有被替换或更改。所有验证均依赖内核报告的元数据的精确整数比较——inode 编号、字节大小和修改时间戳。由于文件系统状态是离散且可计数的，该模块专门使用确定性整数运算；浮点表示既不必要也不适合。

### 关键概念

| 概念 | 通俗解释 | 科学相关性 |
|---|---|---|
| **TOCTOU 防护** | 关闭"检查"文件与"使用"文件之间的时间窗口，防止攻击者在其间替换文件。 | 防止在证据采集过程中对证据进行篡改。 |
| **符号链接检测（`lstat`）** | 在不跟随快捷方式（符号链接）的情况下检查路径自身的元数据。 | 确保检查人员分析真实目标，而非重定向的诱饵。 |
| **基于描述符的验证（`fstat`）** | 独立于路径字符串，查询已打开文件句柄的元数据。 | 消除竞态条件，因为句柄指向特定的不可变 inode。 |
| **普通文件检查（`S_ISREG`）** | 在读取之前确认对象是普通文件——而非设备、管道或套接字。 | 保护取证工作站免受意外系统流的影响。 |
| **共享锁（`flock`）** | 在读取文件时放置非独占锁，使并发写入者必须等待。 | 在采集过程中保证整数元数据快照的原子完整性。 |
| **确定性整数元数据** | `inode`、`size` 和 `mtime` 是内核报告的整数；相等性是精确的。 | 排除浮点运算，因为文件系统身份是可计数的离散状态。 |

> **【科学说明】**
> 皮尔斯（Peirce）、艾柯（Eco）和格赖斯（Grice）的术语在取证文献中作为分析词汇出现，而非神秘主义。考虑一个数字传感器：一个设备将物理状态转换为整数读数。在该模块中，文件系统状态被转换为精确整数的三元组——`inode`、`size` 和 `mtime`。皮尔斯的索引符号就是通过因果轨迹直接指向文件对象的内核元数据。艾柯的"代码"是将这些整数映射到安全裁决的确定性协议。格赖斯的合作准则强制要求文件路径在检查和使用之间表现一致；当它不一致时，合作契约被打破——这是对抗性替换的取证信号。

### 词汇表

1. **PathValidationResult** — 指示路径是否通过所有安全检查的结构化记录。
2. **PathGuard** — 编排验证、打开和读取的主控制器类。
3. **SecurityException** — 当违反安全规则（如检测到符号链接或 TOCTOU 不匹配）时引发的警报。
4. **validate()** — 初始检查点。使用通过 `lstat()` 获取的整数元数据检查符号链接和普通文件状态后返回结果。
5. **verify_no_toctou()** — 第二检查点。将打开后获取的 `inode`、`size` 和 `mtime` 整数与打开前记录的进行比较；任何不匹配都表示攻击。
6. **safe_open()** — 链接验证、描述符获取和打开后 TOCTOU 验证的受保护打开操作。
7. **safe_read()** — 执行 `safe_open()`、应用共享 `flock`、读取内容并确认元数据完整性的受保护读取操作。
8. **lstat()** — 直接检查路径而不遍历符号链接的系统调用。
9. **fstat()** — 完全绕过路径层检查已打开文件描述符的系统调用。
10. **inode** — 文件系统内唯一标识文件对象的整数索引。

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---
