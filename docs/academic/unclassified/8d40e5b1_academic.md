<!--
VIGIA Academic Documentation
Module: 8d40e5b1
Batch ID: vigia-doc-0182-8d40e5b1
Generated: 2026-05-20T14:56:47.883887+00:00
-->

---

## ENGLISH

### What Is This Module?
`path_guard.py` is a support module for VIGÍA forensic artifact analyzers. It sanitizes file-system paths to prevent directory traversal outside a designated `base_dir`. Per Kimi Phase 3.2, it rejects symbolic links, device files, named pipes, and any resolved path lying outside the base directory. Core invariants require that every path is fully resolved prior to comparison and that only regular files are admitted; all special file types are blocked. This ensures deterministic, contamination-free evidence handling.

### Key Concepts

| Concept | Description | Scientific Relevance |
|---|---|---|
| **Path Sanitization** | Validation and cleaning of file paths to enforce security boundaries. | Prevents path traversal attacks that could redirect evidence reads to attacker-controlled locations. |
| **Base Directory (`base_dir`)** | The authorized root folder bounding all valid forensic analyzer operations and path resolutions. | Defines the physical boundary of the evidence domain; paths outside it are rejected unconditionally. |
| **Symbolic Link Rejection** | Refusal to follow symbolic links during path resolution. | Prevents redirection attacks where a symlink points outside the base directory. |
| **Regular File Requirement** | Only standard data-carrying files are admitted; device files, pipes, and sockets are blocked. | Eliminates interaction with kernel interfaces or inter-process channels that could contaminate evidence. |
| **Invariant** | A logical condition guaranteed to remain true throughout module execution. | Ensures consistent, reproducible behavior: the same path always yields the same admission decision. |
| **Deterministic System** | A process yielding identical, reproducible outcomes from the same inputs without non-deterministic side effects. | Guarantees that evidence handling produces no stochastic variance across platforms. |

### Core Operations

| Operation | Purpose |
|---|---|
| `sanitize()` | Accepts a raw path and returns the fully resolved, validated path, or raises an exception if the path is inadmissible. |
| `check_symlink()` | Explicitly tests whether any component of the path is a symbolic link. |
| `check_file_type()` | Verifies that the target is a regular file, rejecting device files, pipes, and sockets. |
| `check_bounds()` | Confirms the fully resolved path is contained within `base_dir`. |

### Glossary
1. **Base Directory** — The authorized root folder bounding all valid analyzer operations and path resolutions.
2. **Device File** — A special file representing a hardware or virtual device; excluded to avoid direct system interaction.
3. **Deterministic System** — A process yielding identical, reproducible outcomes from the same inputs.
4. **Invariant** — A logical condition guaranteed true throughout module execution, ensuring consistent behavior.
5. **Named Pipe** — An inter-process communication endpoint; rejected to eliminate injection or data-stream contamination risks.
6. **Path Sanitization** — Validation and cleaning of file paths to enforce security boundaries.
7. **Path Traversal** — An escape technique using relative path sequences (e.g., `..`) to access files outside a restricted directory.
8. **Regular File** — A standard data-carrying file; the only type permitted for evidence ingestion.
9. **Symbolic Link** — A file-system object referencing another path; blocked to prevent redirection outside the base directory.
10. **Forensic Artifact Analyzer** — A VIGÍA component examining digital traces under controlled, sanitized path constraints.

> **【Scientific Note】**
> Peirce/Eco/Grice terminology is NOT mysticism. In VIGÍA, path sanitization is a prerequisite for valid Peircean indexicality: an index (a forensic artifact) can only serve as evidence if its causal connection to the event is unbroken. A path that has been redirected through a symbolic link or escaped the base directory no longer indexes the original evidence; it indexes an attacker-controlled substitute. The invariant that every path must be fully resolved before comparison operationalizes Eco's requirement that the interpretive code remain stable and unmanipulated.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## ESPAÑOL

### ¿Qué es este módulo?
`path_guard.py` es un módulo de soporte para los analizadores de artefactos forenses VIGÍA. Sanitiza rutas del sistema de archivos para prevenir la salida del directorio `base_dir` designado. Según Kimi Fase 3.2, rechaza enlaces simbólicos, archivos de dispositivo, tuberías con nombre y cualquier ruta resuelta fuera del directorio base. Los invariantes del núcleo requieren que toda ruta se resuelva completamente antes de la comparación y que solo se admitan archivos regulares; todos los tipos de archivos especiales quedan bloqueados. Esto garantiza un manejo de evidencia determinista y libre de contaminación.

### Conceptos clave

| Concepto | Descripción | Relevancia Científica |
|---|---|---|
| **Sanitización de Rutas** | Validación y limpieza de rutas de archivos para imponer límites de seguridad. | Previene ataques de recorrido de rutas que podrían redirigir lecturas de evidencia a ubicaciones controladas por atacantes. |
| **Directorio Base (`base_dir`)** | Carpeta raíz autorizada que delimita todas las operaciones válidas del analizador forense. | Define el límite físico del dominio de evidencia; las rutas fuera de él se rechazan incondicionalmente. |
| **Rechazo de Enlace Simbólico** | Rechazo de seguir enlaces simbólicos durante la resolución de rutas. | Previene ataques de redirección donde un enlace simbólico apunta fuera del directorio base. |
| **Requisito de Archivo Regular** | Solo se admiten archivos de datos estándar; archivos de dispositivo, tuberías y sockets quedan bloqueados. | Elimina la interacción con interfaces del kernel que podrían contaminar la evidencia. |
| **Invariante** | Condición lógica que se garantiza verdadera durante toda la ejecución del módulo. | Garantiza comportamiento consistente y reproducible: la misma ruta siempre da la misma decisión de admisión. |
| **Sistema Determinista** | Proceso que produce resultados idénticos y reproducibles a partir de las mismas entradas. | Garantiza que el manejo de evidencia no produzca varianza estocástica entre plataformas. |

### Glosario
1. **Directorio Base** — Carpeta raíz autorizada que delimita todas las operaciones válidas del analizador y resoluciones de rutas.
2. **Archivo de Dispositivo** — Archivo especial que representa un dispositivo de hardware o virtual; excluido para evitar interacción directa con el sistema.
3. **Sistema Determinista** — Proceso que produce resultados idénticos y reproducibles a partir de las mismas entradas.
4. **Invariante** — Condición lógica que se garantiza verdadera durante la ejecución del módulo, asegurando comportamiento consistente.
5. **Tubería con Nombre** — Punto de comunicación entre procesos; rechazado para eliminar riesgos de inyección o contaminación de flujos de datos.
6. **Sanitización de Rutas** — Validación y limpieza de rutas de archivos para imponer límites de seguridad.
7. **Recorrido de Rutas** — Técnica de escape usando secuencias de rutas relativas (p. ej., `..`) para acceder a archivos fuera de un directorio restringido.
8. **Archivo Regular** — Archivo estándar portador de datos; el único tipo permitido para la ingesta de evidencia.
9. **Enlace Simbólico** — Objeto del sistema de archivos que referencia otra ruta; bloqueado para prevenir redirección fuera del directorio base.
10. **Analizador de Artefactos Forenses** — Componente VIGÍA que examina rastros digitales bajo restricciones de ruta controladas y sanitizadas.

> **【Nota Científica】**
> La terminología de Peirce/Eco/Grice no es misticismo. En VIGÍA, la sanitización de rutas es un requisito previo para la indexicalidad peirceana válida: un índice (un artefacto forense) solo puede servir como evidencia si su conexión causal con el evento es ininterrumpida. Una ruta redirigida a través de un enlace simbólico ya no indexa la evidencia original; indexa un sustituto controlado por el atacante. El invariante de que toda ruta debe resolverse completamente antes de la comparación operacionaliza el requisito de Eco de que el código interpretativo permanezca estable y no manipulado.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## РУССКИЙ

### Что это за модуль?
`path_guard.py` — вспомогательный модуль для криминалистических анализаторов артефактов VIGÍA. Он санитирует пути файловой системы для предотвращения выхода за пределы назначенного `base_dir`. В соответствии с фазой 3.2 Kimi, отклоняются символические ссылки, файлы устройств, именованные каналы и любые разрешённые пути за пределами базового каталога. Инварианты ядра требуют полного разрешения пути перед сравнением и допуска только обычных файлов; все специальные типы файлов блокируются. Это обеспечивает детерминированную, свободную от загрязнения обработку доказательств.

### Ключевые концепции

| Концепция | Описание | Научная значимость |
|---|---|---|
| **Санитизация путей** | Валидация и очистка путей к файлам для обеспечения границ безопасности. | Предотвращает атаки обхода каталогов, которые могли бы перенаправить чтение доказательств в контролируемые злоумышленником места. |
| **Базовый каталог (`base_dir`)** | Авторизованная корневая папка, ограничивающая все валидные операции криминалистического анализатора. | Определяет физическую границу доменa доказательств; пути вне него отклоняются безусловно. |
| **Отклонение символических ссылок** | Отказ следовать символическим ссылкам при разрешении путей. | Предотвращает атаки перенаправления, при которых символическая ссылка указывает за пределы базового каталога. |
| **Требование обычного файла** | Допускаются только стандартные файлы-носители данных; файлы устройств, каналы и сокеты блокируются. | Исключает взаимодействие с интерфейсами ядра или межпроцессными каналами, которые могли бы загрязнить доказательства. |
| **Инвариант** | Логическое условие, гарантированно истинное на протяжении всего выполнения модуля. | Обеспечивает последовательное, воспроизводимое поведение: один и тот же путь всегда даёт одно и то же решение о допуске. |
| **Детерминированная система** | Процесс, дающий идентичные воспроизводимые результаты из тех же входных данных. | Гарантирует отсутствие стохастической дисперсии при обработке доказательств на разных платформах. |

### Глоссарий
1. **Базовый каталог** — Авторизованная корневая папка, ограничивающая все валидные операции анализатора и разрешения путей.
2. **Файл устройства** — Специальный файл, представляющий аппаратное или виртуальное устройство; исключён во избежание прямого взаимодействия с системой.
3. **Детерминированная система** — Процесс, дающий идентичные воспроизводимые результаты из тех же входных данных.
4. **Инвариант** — Логическое условие, гарантированно истинное на протяжении выполнения модуля, обеспечивающее последовательное поведение.
5. **Именованный канал** — Конечная точка межпроцессной коммуникации; отклоняется для устранения рисков внедрения или загрязнения потоков данных.
6. **Санитизация путей** — Валидация и очистка путей к файлам для обеспечения границ безопасности.
7. **Обход каталогов** — Техника выхода за пределы с использованием последовательностей относительных путей (напр., `..`) для доступа к файлам вне ограниченной директории.
8. **Обычный файл** — Стандартный файл-носитель данных; единственный тип, допустимый для ингестирования доказательств.
9. **Символическая ссылка** — Объект файловой системы, ссылающийся на другой путь; блокируется для предотвращения перенаправления за пределы базового каталога.
10. **Криминалистический анализатор артефактов** — Компонент VIGÍA, изучающий цифровые следы в контролируемых, санитизированных ограничениях путей.

> **【Научное примечание】**
> Терминология Пирса, Эко и Грайса — не мистика. В VIGÍA санитизация путей является предпосылкой для действительной пирсовской индексальности: индекс (криминалистический артефакт) может служить доказательством только при непрерывной причинно-следственной связи с событием. Путь, перенаправленный через символическую ссылку, больше не индексирует исходные доказательства; он индексирует подставной объект, контролируемый злоумышленником. Инвариант полного разрешения пути перед сравнением операционализирует требование Эко о стабильности и неманипулируемости интерпретационного кода.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## 中文

### 这是什么模块？
`path_guard.py` 是 VIGÍA 取证工件分析器的支持模块。它对文件系统路径进行净化，防止目录遍历至指定的 `base_dir` 之外。依据 Kimi 阶段 3.2，模块拒绝符号链接、设备文件、命名管道以及解析后位于基础目录外的任何路径。核心不变量要求所有路径在比较前必须完全解析，且仅允许常规文件；所有特殊文件类型均被阻断。从而确保证据处理的确定性与无染性。

### 关键概念

| 概念 | 描述 | 科学相关性 |
|---|---|---|
| **路径净化** | 验证并清理文件路径以强制执行安全边界。 | 防止路径遍历攻击将证据读取重定向到攻击者控制的位置。 |
| **基础目录（`base_dir`）** | 限定所有有效取证分析器操作和路径解析的授权根文件夹。 | 定义证据域的物理边界；其外的路径被无条件拒绝。 |
| **符号链接拒绝** | 在路径解析期间拒绝跟随符号链接。 | 防止符号链接指向基础目录之外的重定向攻击。 |
| **常规文件要求** | 仅允许标准数据文件；设备文件、管道和套接字被阻止。 | 消除与可能污染证据的内核接口或进程间通道的交互。 |
| **不变量** | 在整个模块执行过程中保证为真的逻辑条件。 | 确保一致、可复现的行为：相同路径始终产生相同的准入决定。 |
| **确定性系统** | 从相同输入产生相同可复现结果而无非确定性副作用的过程。 | 保证证据处理在各平台上不产生随机方差。 |

### 词汇表
1. **基础目录** — 限定所有有效分析器操作和路径解析的授权根文件夹。
2. **设备文件** — 代表硬件或虚拟设备的特殊文件；排除以避免直接系统交互。
3. **确定性系统** — 从相同输入产生相同可复现结果的过程。
4. **不变量** — 在模块执行过程中保证为真的逻辑条件，确保一致行为。
5. **命名管道** — 进程间通信端点；拒绝以消除注入或数据流污染风险。
6. **路径净化** — 验证并清理文件路径以强制执行安全边界。
7. **路径遍历** — 使用相对路径序列（如 `..`）访问受限目录外文件的逃逸技术。
8. **常规文件** — 标准数据文件；唯一允许用于证据采集的文件类型。
9. **符号链接** — 引用另一路径的文件系统对象；被阻止以防止重定向至基础目录外。
10. **取证工件分析器** — 在受控、净化路径约束下检查数字痕迹的 VIGÍA 组件。

> **【科学说明】**
> 皮尔斯、艾柯和格赖斯的术语并非神秘主义。在 VIGÍA 中，路径净化是有效皮尔斯索引性的先决条件：索引（取证工件）只有在其与事件的因果联系未被中断时才能作为证据。通过符号链接重定向的路径不再索引原始证据；它索引的是攻击者控制的替代物。路径在比较前必须完全解析的不变量，操作化了艾柯对解释代码保持稳定且不受操纵的要求。

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
