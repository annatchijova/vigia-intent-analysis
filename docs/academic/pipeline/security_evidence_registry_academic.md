<!--
VIGIA Academic Documentation
Module: 6ba25d19
Batch ID: vigia-doc-0115-6ba25d19
Generated: 2026-05-20T14:56:47.869427+00:00
-->

# Module Documentation: `vigia/pipeline/security_evidence_registry.py`

## ENGLISH

### What Is This Module?

This module is a deterministic chain-of-custody recorder for digital evidence. It functions like a bound laboratory notebook: pages cannot be torn out or inserted without detection. Each evidentiary item (an **EvidenceEntry**) is mathematically sealed into an **EvidenceLedger** using cryptographic hashing. The result is a chronological, append-only sequence in which every state depends on all previous states through exact integer arithmetic. If any historical record is altered, the linkage breaks and the tampering is revealed by the `verify()` audit.

### Key Concepts

**Table 1. Core Components and Functions**

| Component / Function | Scientific Role | Deterministic Guarantee |
|---|---|---|
| `EvidenceEntry` | Atomic unit of custody | Immutable once sealed; fields stored as exact byte sequences |
| `EvidenceLedger` | Temporal container and ordering engine | Append-only structure; prior entries cannot be modified in place |
| `append()` | State transition operator | Computes hash linkage to predecessor using deterministic integer operations |
| `verify()` | Integrity audit procedure | Recomputes the full chain of integer digests from genesis to tip; detects any logical discontinuity |
| `root_hash()` | Current-state fingerprint | A single deterministic digest representing the entire ledger history |
| `export_json()` | Structured serialization | Lossless text encoding of all integer and string fields |
| `sign()` | Optional authenticity placeholder | Cryptographic binding to actor identity |

**Table 2. Mathematical Properties**

| Property | Description |
|---|---|
| Deterministic Integer Hashing | All cryptographic digests are produced by exact integer arithmetic (bitwise logic, modular addition) over finite fields. No floating-point operations or approximations are involved. |
| Append-Only Enforcement | The ledger prohibits silent deletion or retroactive insertion; any such attack corrupts the hash chain. |
| Complete Verifiability | The `verify()` function recomputes every expected value and confirms a zero-discontinuity chain. |

### Glossary

- **Cryptographic hash** — A deterministic function that maps data of arbitrary size to a fixed-length integer digest. It acts like a molecular fingerprint: an infinitesimal change in input yields a completely different output integer.
- **Chain of custody** — The documented trail of evidence possession, transfer, and analysis. In this module, custody is enforced mathematically rather than merely procedurally.
- **Ledger** — An append-only record book. In digital forensics, this guarantees that the historical record grows monotonically without silent erasures.
- **Integrity verification** — The process of recomputing expected hash values and comparing them to stored values. A mismatch indicates tampering or corruption.
- **Deterministic integer arithmetic** — Mathematical operations on whole numbers (bits and bytes) performed without rounding, truncation, or floating-point error. Identical inputs always yield identical outputs.

### 【Scientific Note】

> The terminology of Peirce, Eco, and Grice is sometimes mistaken for metaphysical speculation. It is not. These frameworks function exactly like physical sensors: Peirce's semiotics translates sign-relations into measurable triads (sign–object–interpretant); Eco's theory of sign production provides the protocol for detecting fabricated or anomalous evidence artifacts; and Grice's maxims operationalize the expectations of cooperative information exchange. Just as a spectrometer converts light into an electrical spectrum without invoking mysticism, these models convert evidentiary communication into formal, testable categories. They are epistemological instruments, not occult doctrines.

---

## ESPAÑOL

### ¿Qué es este módulo?

Este módulo es un registro determinista de la cadena de custodia para evidencia digital. Funciona como un cuaderno de laboratorio encuadernado: no se pueden arrancar o insertar páginas sin que se detecte. Cada elemento probatorio (un **`EvidenceEntry`**) se sella matemáticamente en un **`EvidenceLedger`** mediante hash criptográfico. El resultado es una secuencia cronológica de solo-adición en la que cada estado depende de todos los anteriores mediante aritmética entera exacta. Si se altera cualquier registro histórico, el vínculo se rompe y la auditoría `verify()` revela la manipulación.

### Conceptos clave

**Tabla 1. Componentes y funciones principales**

| Componente / Función | Rol científico | Garantía determinista |
|---|---|---|
| `EvidenceEntry` | Unidad atómica de custodia | Inmutable una vez sellado; campos almacenados como secuencias exactas de bytes |
| `EvidenceLedger` | Contenedor temporal y motor de ordenación | Estructura de solo-adición; las entradas previas no pueden modificarse in situ |
| `append()` | Operador de transición de estado | Calcula el vínculo de hash con el predecesor mediante operaciones enteras deterministas |
| `verify()` | Procedimiento de auditoría de integridad | Recalcula la cadena completa de resúmenes enteros desde el génesis hasta el último bloque; detecta cualquier discontinuidad lógica |
| `root_hash()` | Huella dactilar del estado actual | Un único digesto determinista que representa toda la historia del libro mayor |
| `export_json()` | Serialización estructurada | Codificación textual sin pérdida de todos los campos enteros y de texto |
| `sign()` | Marcador opcional de autenticidad | Vínculo criptográfico con la identidad del actor |

**Tabla 2. Propiedades matemáticas**

| Propiedad | Descripción |
|---|---|
| Hash criptográfico entero determinista | Todos los resúmenes se producen mediante aritmética entera exacta (lógica de bits, adición modular) sobre campos finitos. No intervienen operaciones de coma flotante ni aproximaciones. |
| Aplicación de solo-adición | El libro mayor prohíbe el borrado silencioso o la inserción retroactiva; cualquier ataque de este tipo corrompe la cadena de hashes. |
| Verificabilidad completa | La función `verify()` recalcula cada valor esperado y confirma una cadena sin discontinuidades. |

### Glosario

- **Hash criptográfico** — Función determinista que asigna datos de tamaño arbitrario a un resumen entero de longitud fija. Actúa como una huella molecular: un cambio mínimo en la entrada produce un entero de salida completamente diferente.
- **Cadena de custodia** — Rastro documentado de la posesión, transferencia y análisis de la evidencia. En este módulo, la custodia se aplica matemáticamente y no solo de forma procesal.
- **Libro mayor (ledger)** — Registro de solo-adición. En informática forense, garantiza que el registro histórico crece monotónicamente sin borrados silenciosos.
- **Verificación de integridad** — Proceso de recalcular los valores de hash esperados y compararlos con los valores almacenados. Una discrepancia indica manipulación o corrupción.
- **Aritmética entera determinista** — Operaciones matemáticas sobre números enteros (bits y bytes) realizadas sin redondeo, truncamiento ni error de coma flotante. Entradas idénticas siempre producen salidas idénticas.

### 【Nota Científica】

> La terminología de Peirce, Eco y Grice a veces se confunde con especulación metafísica. No lo es. Estos marcos funcionan exactamente como sensores físicos: la semiótica de Peirce traduce las relaciones de signos en tríadas mensurables (signo–objeto–interpretante); la teoría de la producción de signos de Eco proporciona el protocolo para detectar artefactos de evidencia fabricados o anómalos; y los máximas de Grice operacionalizan las expectativas del intercambio cooperativo de información. Así como un espectrómetro convierte la luz en un espectro eléctrico sin invocar misticismo, estos modelos convierten la comunicación probatoria en categorías formales y comprobables. Son instrumentos epistemológicos, no doctrinas ocultistas.

---

## РУССКИЙ

### Что представляет собой этот модуль?

Этот модуль представляет собой детерминированный регистратор цепочки сохранения цифровых доказательств. Он работает как сшитый лабораторный журнал: страницы нельзя вырвать или вставить без обнаружения. Каждый элемент доказательства (**`EvidenceEntry`**) математически запечатывается в реестре (**`EvidenceLedger`**) с помощью криптографического хеширования. В результате получается хронологическая, дополняемая только с конца последовательность, в которой каждое состояние зависит от всех предыдущих посредством точной целочисленной арифметики. Если какая-либо историческая запись будет изменена, связь разрывается, и аудит `verify()` выявит факт несанкционированного вмешательства.

### Ключевые понятия

**Таблица 1. Основные компоненты и функции**

| Компонент / Функция | Научная роль | Детерминированная гарантия |
|---|---|---|
| `EvidenceEntry` | Атомарная единица хранения | Неизменяема после запечатывания; поля хранятся как точные последовательности байтов |
| `EvidenceLedger` | Временный контейнер и механизм упорядочивания | Структура с добавлением только в конец; предыдущие записи нельзя изменить на месте |
| `append()` | Оператор перехода состояния | Вычисляет хеш-связь с предшественником при помощи детерминированных целочисленных операций |
| `verify()` | Процедура аудита целостности | Пересчитывает полную цепочку целочисленных дайджестов от начала до конца; обнаруживает любой логический разрыв |
| `root_hash()` | Отпечаток текущего состояния | Единый детерминированный дайджест, представляющий всю историю реестра |
| `export_json()` | Структурированная сериализация | Безубыточное текстовое кодирование всех целочисленных и строковых полей |
| `sign()` | Опциональный маркер подлинности | Криптографическая привязка к идентичности субъекта |

**Таблица 2. Математические свойства**

| Свойство | Описание |
|---|---|
| Детерминированное целочисленное хеширование | Все криптографические дайджесты получены точной целочисленной арифметикой (побитовая логика, модульное сложение) над конечными полями. Операций с плавающей запятой и приближений не используется. |
| Принудительное добавление в конец | Реестр запрещает скрытое удаление или ретроспективную вставку; любая такая атака разрушает хеш-цепочку. |
| Полная верифицируемость | Функция `verify()` пересчитывает каждое ожидаемое значение и подтверждает цепочку без разрывов. |

### Глоссарий

- **Криптографический хеш** — Детерминированная функция, отображающая данные произвольного размера на дайджест фиксированной длины в виде целого числа. Действует как молекулярный отпечаток: бесконечно малое изменение входных данных даёт совершенно иное выходное целое.
- **Цепочка сохранения** — Документированный след владения, передачи и анализа доказательств. В данном модуле сохранение обеспечивается математически, а не только процедурно.
- **Реестр (ledger)** — Запись с добавлением только в конец. В цифровой криминалистике это гарантирует монотонный рост исторической записи без скрытых стираний.
- **Проверка целостности** — Процесс пересчёта ожидаемых хеш-значений и сравнения их с хранимыми значениями. Несоответствие указывает на подделку или повреждение.
- **Детерминированная целочисленная арифметика** — Математические операции над целыми числами (битами и байтами) без округления, усечения или ошибок плавающей запятой. Идентичные входные данные всегда дают идентичный результат.

### 【Научное Примечание】

> Терминология Пирса, Эко и Грайса иногда ошибочно принимается за метафизическую спекуляцию. Это не так. Эти фреймворки функционируют точно так же, как физические датчики: семиотика Пирса транслирует отношения знаков в измеримые триады (знак–объект–интерпретант); теория производства знаков Эко задаёт протокол обнаружения поддельных или аномальных артефактов доказательственной практики; а максимы Грайса операционализируют ожидания кооперативного обмена информацией. Как спектрометр преобразует свет в электрический спектр, не прибегая к мистицизму, эти модели превращают доказательственную коммуникацию в формальные, проверяемые категории. Это эпистемологические инструменты, а не оккультные доктрины.

---

## 中文

### 本模块是什么？

本模块是一个用于数字证据保管链的确定性登记系统。其功能相当于一本无法撕页或夹页的装订式实验室笔记本：每一页（即**取证条目 / EvidenceEntry**）都通过加密哈希值被数学性地锁定进**证据账本 / EvidenceLedger**，形成一个仅可追加的时序序列。序列中的每一个状态都通过精确的整数运算依赖于此前所有的状态。若任何历史记录遭到篡改，其数学链接即发生**逻辑断裂**，审计函数 `verify()` 将立即揭示该篡改行为。

### 核心概念

**表 1. 核心组件与函数**

| 组件 / 函数 | 科学角色 | 确定性保障 |
|---|---|---|
| `EvidenceEntry`（取证条目） | 原子级保管单元 | 封存后不可变；所有字段以精确字节序列存储 |
| `EvidenceLedger`（证据账本） | 时序容器与排序引擎 | 仅追加结构；历史条目不可就地修改 |
| `append()` | 状态转换算子 | 通过确定性整数运算计算与前驱区块的哈希链接 |
| `verify()` | 完整性审计程序 | 从创世区块至最新区块逐块重算整数摘要；检测任何逻辑断裂 |
| `root_hash()` | 当前状态指纹 | 代表整个账本历史的单一确定性摘要值 |
| `export_json()` | 结构化序列化 | 对所有整数与字符串字段进行无损文本编码 |
| `sign()` | 可选真实性标记 | 与行为主体身份进行加密绑定 |

**表 2. 数学特性**

| 特性 | 说明 |
|---|---|
| 确定性整数哈希 | 所有加密摘要均通过有限域上的精确整数运算（位运算、模加）生成，不使用浮点运算；相同输入永远产生相同输出。 |
| 仅追加强制执行 | 账本禁止静默删除或事后插入；任何此类攻击都会破坏哈希链。 |
| 完全可验证性 | `verify()` 函数重算每一个预期值，确认零断裂链。 |

### 术语表

- **加密哈希 (Cryptographic hash)** — 一种将任意数据映射为定长整数摘要的确定性函数。如同分子指纹：输入的微小变化将导致输出截然不同。
- **保管链 (Chain of custody)** — 证据持有与流转的文档化追踪路径。在本模块中，它通过数学而非仅依靠程序来强制执行。
- **账本 (Ledger)** — 仅追加的记录簿。在数字取证中，这意味着不可能发生静默删除或事后插入。
- **完整性验证 (Integrity verification)** — 重新计算预期哈希值并与存储值比对的过程。不匹配即表明篡改或数据损坏。
- **确定性整数运算 (Deterministic integer arithmetic)** — 对整数（比特与字节）进行的精确运算，不存在舍入、近似或浮点误差。保证完全可复现性。
- **逻辑断裂 (Logical discontinuity)** — 哈希链中因数据篡改而导致的前后链接失效。验证程序可通过整数重算精确识别此类断裂。

### 【科学说明】

> 皮尔斯、艾柯与格赖斯的术语有时被误认为玄学思辨。事实并非如此。这些理论框架的运作方式与物理传感器完全相同：皮尔斯的符号学将符号关系转译为可测量的三元组（符号-客体-解释项）；艾柯的符号生产理论为检测伪造或异常的取证工件提供了协议；而格赖斯的准则将合作性信息交换的预期予以可操作化。正如光谱仪将光转换为电信号频谱而无需诉诸神秘主义，这些模型将证据性交流转化为形式化、可检验的范畴。它们是认识论工具，而非神秘教义。

---

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
