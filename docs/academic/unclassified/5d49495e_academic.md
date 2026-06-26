<!--
VIGIA Academic Documentation
Module: 5d49495e
Batch ID: vigia-doc-0039-5d49495e
Generated: 2026-05-20T14:56:47.852948+00:00
-->

---

## ENGLISH

### What Is This Module?
Imagine a laboratory notebook that must never be altered after an experiment. This module acts as an **independent laboratory archivist**. It takes a collection of digital evidence—called a **Forensic Bundle**—and applies a mathematical seal using SHA-256, a deterministic integer-based fingerprinting method. Because this archivist works outside the room where the experiment happens (the inference engine), even a compromised machine cannot secretly rewrite its own notebook. The module also fingerprints the experiment's machinery (the engine source code and dependency manifests) to ensure the tools themselves were not swapped.

### Key Concepts

| Concept | Description |
|---|---|
| External Cryptographic Attestation | An independent sealing process that runs outside the inference engine to prevent self-certification of compromised evidence. |
| SHA-256 Chain Hashing | A deterministic protocol where each digest is computed via exact integer operations on byte sequences, with each output feeding into the next link. |
| Forensic Bundle | A structured evidence container (inference graph, trace logs, policy rules) treated as an immutable artifact. |
| Graph Self-Exclusion | The graph hash is computed only over the graph's data fields, deliberately excluding the hash field to prevent circular logic. |
| Engine Attestation | A fingerprint of the inference engine's own source code and dependency files, ensuring runtime integrity. |
| Exclusion Patterns | Filtering rules that ignore cache directories and temporary files when fingerprinting engine code. |
| Deterministic Integer Arithmetic | All computations use exact whole-number operations on bytes; no approximations are permitted. |

### Core Operations

| Operation | Purpose |
|---|---|
| Seal | Computes the full chain of SHA-256 hashes over the bundle contents and returns a complete JSON attestation record. |
| Save | Writes the sealed bundle to persistent storage and returns a transport verification hash. |
| Quick Verify | Recomputes the integer hash chain internally for rapid integrity checks without invoking the external verifier. |
| Engine Attestation | Generates a source-code hash covering the engine implementation and dependency manifests to detect runtime substitution. |

### Glossary
1. **Attestation** — The formal act of binding a cryptographic hash to a dataset to guarantee its state at a specific moment.
2. **Chain Hashing** — A method of linking sequential digests so that any alteration invalidates the entire lineage.
3. **Decoupling** — The deliberate separation of the builder process from the inference runtime to eliminate insider tampering.
4. **Deterministic Integer Arithmetic** — Computation using exact whole-number operations; only integer-based arithmetic is used in the hashing protocol.
5. **Forensic Bundle** — A digitally signed collection of inference artifacts.
6. **Runtime** — The operational environment of the inference engine during processing.
7. **Verification** — The process of recomputing integer hashes to confirm that no bits have changed.
8. **Graph Self-Exclusion** — Technique of omitting a hash field from its own hash computation to avoid circular dependency.
9. **SHA-256** — A deterministic algorithm producing an exact 256-bit integer fingerprint of any byte sequence.
10. **Dependency Manifest** — A file listing the exact versions of all software libraries used by the engine, included in attestation.

> **【Scientific Note】**
> References to semiotic frameworks—such as **Peirce**'s theory of signs, **Eco**'s notion of interpretative codes, or **Grice**'s cooperative maxims—are sometimes mistaken for metaphysical speculation. In digital forensics, they serve as precise epistemological models. Think of a forensic bundle as a sensor array: Peirce's *sign* is the raw hash value, Eco's interpretive code is the expected hash of an unmodified bundle, and Grice's maxim of quality is violated when the computed hash fails to match — a lie encoded in bytes.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## ESPAÑOL

### ¿Qué es este módulo?
Imagine un cuaderno de laboratorio que nunca debe alterarse tras un experimento. Este módulo actúa como un **archivista de laboratorio independiente**. Toma una colección de evidencia digital —denominada **Paquete Forense** (Forensic Bundle)— y le aplica un sello matemático mediante SHA-256, un método de huella digital basado en aritmética entera determinista. Dado que este archivista trabaja fuera de la sala donde ocurre el experimento (el motor de inferencia), incluso una máquina comprometida no puede reescribir secretamente su propio cuaderno. El módulo también genera la huella digital de la maquinaria del experimento (el código fuente del motor y los manifiestos de dependencias) para garantizar que las herramientas mismas no hayan sido intercambiadas.

### Conceptos clave

| Concepto | Descripción |
|---|---|
| Attestation Criptográfica Externa | Proceso de sellado independiente ejecutado fuera del motor de inferencia para prevenir la auto-certificación de evidencia comprometida. |
| SHA-256 Chain Hashing | Protocolo determinista donde cada resumen se calcula mediante operaciones enteras exactas sobre secuencias de bytes, con cada salida alimentando el siguiente eslabón. |
| Paquete Forense | Contenedor de evidencia estructurado (grafo de inferencia, trazas de registro, reglas de política) tratado como artefacto inmutable. |
| Auto-exclusión del Grafo | El hash del grafo se calcula solo sobre los campos de datos del grafo, excluyendo deliberadamente el campo hash para prevenir lógica circular. |
| Attestation del Motor | Huella digital del código fuente del motor de inferencia y sus archivos de dependencias, garantizando la integridad en tiempo de ejecución. |
| Aritmética Entera Determinista | Todos los cómputos utilizan operaciones exactas de números enteros sobre bytes; no se permiten aproximaciones. |

### Glosario
1. **Attestation** — Acto formal de vincular un hash criptográfico a un conjunto de datos para garantizar su estado en un momento específico.
2. **Chain Hashing** — Método de encadenamiento de resúmenes secuenciales donde cualquier alteración invalida todo el linaje.
3. **Desacoplamiento** — Separación deliberada del proceso constructor del tiempo de ejecución de inferencia para eliminar la manipulación interna.
4. **Aritmética Entera Determinista** — Cómputo usando operaciones exactas de números enteros; solo se usa aritmética de base entera en el protocolo de hash.
5. **Paquete Forense** — Colección firmada digitalmente de artefactos de inferencia.
6. **Tiempo de Ejecución** — Entorno operacional del motor de inferencia durante el procesamiento.
7. **Verificación** — Proceso de recomputar hashes enteros para confirmar que no ha cambiado ningún bit.
8. **Auto-exclusión del Grafo** — Técnica de omitir el campo hash del propio cómputo hash para evitar dependencia circular.
9. **SHA-256** — Algoritmo determinista que produce una huella digital entera exacta de 256 bits de cualquier secuencia de bytes.
10. **Manifiesto de Dependencias** — Archivo que lista las versiones exactas de todas las bibliotecas de software utilizadas por el motor, incluido en la attestation.

> **【Nota Científica】**
> Las referencias a marcos semióticos —como la teoría de signos de **Peirce**, la noción de códigos interpretativos de **Eco** o las máximas cooperativas de **Grice**— a veces se confunden con especulación metafísica. En la informática forense, sirven como modelos epistemológicos precisos. Piense en un paquete forense como una red de sensores: el *signo* de Peirce es el valor hash en bruto, el código interpretativo de Eco es el hash esperado de un paquete no modificado, y la máxima de calidad de Grice se viola cuando el hash calculado no coincide — una mentira codificada en bytes.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## РУССКИЙ

### Что это за модуль?
Представьте лабораторный журнал, который нельзя изменить после завершения эксперимента. Данный модуль выступает в роли **независимого лабораторного архивариуса**. Он принимает коллекцию цифровых доказательств — так называемый **Криминалистический пакет** (Forensic Bundle) — и накладывает математическую печать с помощью SHA-256, детерминированного метода цифрового отпечатка на основе целочисленной арифметики. Поскольку этот архивариус работает вне комнаты, где происходит эксперимент (движок вывода), даже скомпрометированная машина не может тайно переписать свой собственный журнал. Модуль также создаёт отпечаток оборудования эксперимента (исходный код движка и манифесты зависимостей), чтобы убедиться, что инструменты не были подменены.

### Ключевые концепции

| Концепция | Описание |
|---|---|
| Внешняя криптографическая аттестация | Независимый процесс опечатывания, выполняемый вне движка вывода, для предотвращения самосертификации скомпрометированных доказательств. |
| SHA-256 цепочечное хеширование | Детерминированный протокол, в котором каждый дайджест вычисляется через точные целочисленные операции над байтовыми последовательностями, с передачей каждого выхода в следующее звено. |
| Криминалистический пакет | Структурированный контейнер доказательств (граф вывода, журналы трассировки, правила политики), рассматриваемый как неизменяемый артефакт. |
| Само-исключение графа | Хеш графа вычисляется только по полям данных графа, намеренно исключая поле хеша для предотвращения циклической логики. |
| Аттестация движка | Отпечаток исходного кода движка вывода и файлов зависимостей, обеспечивающий целостность во время выполнения. |
| Детерминированная целочисленная арифметика | Все вычисления используют точные целочисленные операции над байтами; приближения не допускаются. |

### Глоссарий
1. **Аттестация** — Формальный акт привязки криптографического хеша к набору данных для гарантии его состояния в определённый момент.
2. **Цепочечное хеширование** — Метод связывания последовательных дайджестов, при котором любое изменение делает недействительным всё «семейство».
3. **Развязка** — Намеренное разделение процесса сборки и среды выполнения вывода для исключения инсайдерской манипуляции.
4. **Детерминированная целочисленная арифметика** — Вычисления с использованием точных целочисленных операций; в протоколе хеширования применяется только целочисленная арифметика.
5. **Криминалистический пакет** — Цифрово подписанная коллекция артефактов вывода.
6. **Среда выполнения** — Операционная среда движка вывода в процессе работы.
7. **Верификация** — Процесс повторного вычисления целочисленных хешей для подтверждения неизменности битов.
8. **Само-исключение графа** — Техника исключения поля хеша из собственного вычисления хеша во избежание циклической зависимости.
9. **SHA-256** — Детерминированный алгоритм, производящий точный 256-битный целочисленный отпечаток любой байтовой последовательности.
10. **Манифест зависимостей** — Файл со списком точных версий всех программных библиотек, используемых движком, включаемый в аттестацию.

> **【Научное примечание】**
> Ссылки на семиотические рамки — теорию знаков **Пирса**, концепцию интерпретационных кодов **Эко** или кооперативные максимы **Грайса** — иногда принимают за метафизическую спекуляцию. В цифровой криминалистике они служат точными эпистемологическими моделями. Представьте криминалистический пакет как массив датчиков: *знак* Пирса — это необработанное хеш-значение, интерпретационный код Эко — ожидаемый хеш неизменённого пакета, а максима качества Грайса нарушается, когда вычисленный хеш не совпадает — ложь, закодированная в байтах.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## 中文

### 这是什么模块？
想象一本实验结束后永远不能被篡改的实验室记录本。本模块充当**独立实验室档案员**。它接收一批数字证据——称为**取证捆绑包**（Forensic Bundle）——并使用 SHA-256 施加数学印章，SHA-256 是一种基于确定性整数运算的指纹方法。由于此档案员在实验发生的房间之外工作（推理引擎之外），即使是被攻陷的机器也无法秘密改写自己的记录本。该模块还对实验机制（引擎源代码和依赖项清单）生成指纹，以确保工具本身未被替换。

### 关键概念

| 概念 | 描述 |
|---|---|
| 外部加密认证 | 在推理引擎外部运行的独立封印过程，防止对被篡改证据的自我认证。 |
| SHA-256 链式哈希 | 确定性协议，每个摘要通过对字节序列的精确整数运算计算得出，每个输出均输入下一个链节。 |
| 取证捆绑包 | 结构化证据容器（推理图、追踪日志、策略规则），作为不可变工件处理。 |
| 图自排除 | 图哈希仅在图的数据字段上计算，故意排除哈希字段以防止循环逻辑。 |
| 引擎认证 | 推理引擎自身源代码和依赖文件的指纹，确保运行时完整性。 |
| 确定性整数运算 | 所有计算均对字节使用精确整数运算；不允许任何近似值。 |

### 词汇表
1. **认证** — 将加密哈希绑定到数据集以保证其在特定时刻状态的正式行为。
2. **链式哈希** — 链接连续摘要的方法，任何更改都会使整个谱系失效。
3. **解耦** — 有意将构建过程与推理运行时分离，以消除内部人员篡改。
4. **精确整数运算** — 使用精确整数运算进行计算；哈希协议中仅使用基于整数的运算。
5. **取证捆绑包** — 推理工件的数字签名集合。
6. **运行时** — 推理引擎在处理过程中的操作环境。
7. **验证** — 重新计算整数哈希以确认没有位发生变化的过程。
8. **图自排除** — 从自身哈希计算中排除哈希字段以避免循环依赖的技术。
9. **SHA-256** — 产生任意字节序列精确 256 位整数指纹的确定性算法。
10. **依赖项清单** — 列出引擎使用的所有软件库精确版本的文件，包含在认证中。

> **【科学说明】**
> 对符号学框架的引用——如**皮尔斯**的符号理论、**艾柯**的解释代码概念或**格赖斯**的合作准则——有时被误认为形而上学推测。在数字取证中，它们充当精确的认识论模型。将取证捆绑包视为传感器阵列：皮尔斯的*符号*是原始哈希值，艾柯的解释代码是未修改捆绑包的预期哈希，而当计算的哈希不匹配时，格赖斯的质量准则即遭到违反——一个用字节编码的谎言。

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
