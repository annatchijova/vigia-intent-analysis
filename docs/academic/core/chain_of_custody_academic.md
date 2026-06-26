<!--
VIGIA Academic Documentation
Module: cc27fff8
Batch ID: vigia-doc-0043-cc27fff8
Generated: 2026-05-20T14:56:47.853722+00:00
-->

---

## ENGLISH

### What Is This Module?

`vigia/core/chain_of_custody.py` is the laboratory notebook of the VIGÍA digital-forensics platform. It chronicles every manipulation of a digital evidence artifact—who accessed it, when, and what changed—by generating cryptographic fingerprints (SHA-256 hashes) and universal timestamps. Imagine a permanently bound logbook in which each new page is physically linked to the previous one; removing or altering a page breaks the seal and exposes the tampering.

### Key Concepts

| Concept | Plain-Language Definition | Scientific Function |
|---|---|---|
| **Chain of Custody** | A chronological ledger of every action taken on a piece of digital evidence. | Guarantees integrity and provenance for legal and scientific review. |
| **Custody Record** | One entry in the ledger: actor + timestamp + action + fingerprint. | Provides an atomic, indivisible unit of accountability. |
| **SHA-256 Hash** | A 256-bit deterministic integer fingerprint computed from file contents via exact arithmetic on bits and bytes. | Detects alteration; any microscopic change yields a completely different integer identifier. |
| **Timestamp** | A standardized UTC temporal marker. | Establishes strict temporal order and prevents back-dating. |
| **Actor** | The human operator or automated system performing the action. | Attributes responsibility and enables end-to-end audit tracing. |
| **Immutability** | The property that historical records cannot be changed retroactively. | Ensures that past observations remain scientifically valid and legally defensible. |
| **Evidence Bundle** | A compiled export of the chain for court or peer review. | Facilitates reproducibility and cross-institutional verification. |
| **Deterministic Integer Arithmetic** | Operations on discrete whole numbers (bits and bytes) without approximation. | Eliminates platform-dependent variance; identical inputs always yield identical hash integers on any system. |

### Glossary

- **Deterministic Integer Arithmetic**: Mathematical operations performed on exact whole numbers. SHA-256 processes data as discrete integers, so every identical file always produces the same hash value on every computer, with no rounding or approximation errors.
- **Hash (SHA-256)**: A one-way function that maps data of arbitrary size to a fixed 256-bit integer. It acts as a unique specimen barcode.
- **Actor**: The entity (person or service account) responsible for an action. Equivalent to a dated signature in a paper lab notebook.
- **Immutability**: Once a record is written, it cannot be silently modified. Any tampering creates a detectable logical discontinuity.
- **Timestamp**: A temporal coordinate, expressed in UTC, marking when an event occurred.
- **Evidence Bundle**: A standardized package containing the evidence together with its complete chain-of-custody log.

【Scientific Note】
Terminology inspired by semiotics—Charles Sanders Peirce, Umberto Eco, and H.P. Grice—is sometimes mistaken for metaphysical speculation. It is not. In digital forensics, these concepts function exactly like sensor calibration theory. Peirce’s *interpretant* is the measurable output produced when a sign (the evidence artifact) interacts with an observer (the forensic system). Eco’s *encyclopedia* corresponds to the contextual calibration matrix that allows different laboratories to agree on what a pattern means. Grice’s *cooperative maxims* are the communication protocol ensuring that the custodial record is not noise but meaningful signal. Treating the chain of custody as a semiotic sensor rig turns mysticism into metrology.

---

## ESPAÑOL

### ¿Qué es este módulo?

`vigia/core/chain_of_custody.py` es el cuaderno de laboratorio de la plataforma forense VIGÍA. Rastrea cada manipulación de un artefacto de evidencia digital—quién lo tocó, cuándo y qué cambió—mediante huellas criptográficas (hash SHA-256) y marcas temporales universales. Imaginese un registro encuadernado de forma permanente donde cada página nueva está unida a la anterior; arrancar o alterar una página rompe el sello y delata la intrusión.

### Conceptos clave

| Concepto | Definición en lenguaje sencillo | Función científica |
|---|---|---|
| **Cadena de custodia** | Registro cronológico de cada acción sobre una evidencia digital. | Garantiza integridad y procedencia para revisión legal y científica. |
| **Registro de custodia** | Una línea del registro: actor + marca temporal + acción + huella. | Unidad atómica e indivisible de responsabilidad. |
| **Hash SHA-256** | Huella digital entera determinista de 256 bits calculada mediante aritmética exacta sobre bits y bytes. | Detecta alteración; cualquier cambio mínimo genera un identificador entero completamente distinto. |
| **Marca temporal** | Marcador de tiempo estandarizado en UTC. | Establece orden temporal estricto e impide fechados retroactivos. |
| **Actor** | Operador humano o sistema automatizado que ejecuta la acción. | Atribuye responsabilidad y permite trazabilidad completa. |
| **Inmutabilidad** | Propiedad de que los registros históricos no pueden cambiarse retroactivamente. | Asegura que observaciones pasadas sigan siendo válidas científica y legalmente. |
| **Paquete de evidencia** | Exportación compilada de la cadena para tribunal o revisión por pares. | Facilita reproducibilidad y verificación interinstitucional. |
| **Aritmética entera determinista** | Operaciones sobre números enteros discretos (bits y bytes) sin aproximación. | Elimina varianza entre plataformas; entradas idénticas siempre producen el mismo hash en cualquier sistema. |

### Glosario

- **Aritmética entera determinista**: Operaciones matemáticas sobre números enteros exactos. Como SHA-256 procesa datos como enteros puros, todo archivo idéntico siempre produce el mismo valor de hash en cualquier computadora, sin errores de redondeo ni aproximación.
- **Hash (SHA-256)**: Función unidireccional que asigna a datos de tamaño arbitrario un entero fijo de 256 bits. Actúa como un código de barras único para el espécimen.
- **Actor**: Entidad (persona o cuenta de servicio) responsable de una acción. Equivalente a una firma fechada en un cuaderno de papel.
- **Inmutabilidad**: Una vez escrito un registro, no puede modificarse en silencio. Cualquier manipulación crea una discontinuidad lógica detectable.
- **Marca temporal**: Coordenada temporal, generalmente en UTC, que marca cuándo ocurrió un evento.
- **Paquete de evidencia**: Paquete estandarizado que contiene la evidencia y su registro completo de cadena de custodia.

【Nota Científica】
La terminología inspirada en la semiótica—Charles Sanders Peirce, Umberto Eco y H.P. Grice—es a veces confundida con especulación metafísica. No lo es. En forense digital, estos conceptos funcionan exactamente como la teoría de calibración de sensores. El *interpretante* de Peirce es la salida medible cuando un signo (el artefacto de evidencia) interactúa con un observador (el sistema forense). La *enciclopedia* de Eco corresponde a la matriz de calibración contextual que permite que distintos laboratorios acuerden qué significa un patrón. Los *máximas cooperativas* de Grice son el protocolo de comunicación que garantiza que el registro de custodia no sea ruido, sino señal significativa. Tratar la cadena de custodia como un aparato semiótico-sensorial convierte el misticismo en metrología.

---

## РУССКИЙ

### Что представляет собой этот модуль?

`vigia/core/chain_of_custody.py` — это лабораторный журнал платформы
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

## 中文

### 这是什么模块？

`vigia/core/chain_of_custody.py` 是 VIGÍA 数字取证平台的实验室记录本。它通过生成密码学指纹（SHA-256 哈希值）和通用时间戳，追踪对数字证据工件的每次操作——谁访问了它、何时访问以及发生了什么变化。可以将其想象为一本永久装订的记录本，其中每个新页面都与上一页物理相连；撕掉或更改任何一页都会破坏封印并暴露篡改行为。

### 关键概念

| 概念 | 通俗定义 | 科学功能 |
|---|---|---|
| **证据保管链** | 对数字证据进行的每项操作的按时间顺序排列的账本。 | 为法律和科学审查保证完整性和溯源性。 |
| **保管记录** | 账本中的一个条目：行为者 + 时间戳 + 操作 + 指纹。 | 提供不可分割的原子责任单元。 |
| **SHA-256 哈希** | 通过对位和字节进行精确整数运算从文件内容计算得出的256位确定性整数指纹。 | 检测篡改；任何微小变化都会产生完全不同的整数标识符。 |
| **时间戳** | 标准化的 UTC 时间标记。 | 建立严格的时间顺序并防止回溯修改。 |
| **行为者（Actor）** | 执行操作的人类操作员或自动化系统。 | 归因责任并支持端到端审计追踪。 |
| **不可变性** | 历史记录无法被追溯更改的属性。 | 确保过去的观察在科学和法律上继续有效。 |
| **证据包** | 用于法庭或同行评审的链条编译导出。 | 促进可重现性和跨机构验证。 |
| **确定性整数运算** | 对离散整数（位和字节）的运算，无近似。 | 消除平台依赖的差异；相同输入在任何系统上始终产生相同的哈希整数。 |

### 词汇表

1. **确定性整数运算** — 对精确整数进行的数学运算。SHA-256 将数据处理为离散整数，因此每个相同文件在任何计算机上始终产生相同的哈希值，无舍入或近似误差。
2. **哈希（SHA-256）** — 将任意大小的数据映射到固定256位整数的单向函数；充当独特的样品条形码。
3. **行为者（Actor）** — 负责某项操作的实体（人员或服务账户）；相当于纸质实验室记录本中的签名日期。
4. **不可变性（Immutability）** — 记录一旦写入就无法静默修改；任何篡改都会产生可检测的逻辑断裂。
5. **时间戳（Timestamp）** — 以 UTC 表示的时间坐标，标记事件发生的时间。
6. **证据包（Evidence Bundle）** — 包含证据及其完整保管链日志的标准化包。
7. **逻辑断裂（Logical Fracture）** — 保管链中的可检测不一致，表明证据受到了篡改。
8. **SHA-256 摘要** — 文件内容的256位密码学指纹；任何字节级别的更改都会产生完全不同的摘要。
9. **追加式日志** — 只能添加新条目而无法修改或删除现有条目的审计记录结构。
10. **审计追踪** — 记录对证据工件进行的所有操作的完整时间顺序记录，满足道伯特标准要求。

> **【科学说明】**
> 受符号学启发的术语——查尔斯·桑德斯·皮尔斯（Peirce）、艾柯（Eco）和格赖斯（Grice）——有时被误认为是形而上学推测。事实并非如此。在数字取证中，这些概念的作用完全等同于传感器校准理论。皮尔斯的"解释项"（interpretant）是当符号（证据工件）与观察者（取证系统）交互时产生的可测量输出。艾柯的"百科全书"对应于允许不同实验室就模式含义达成一致的上下文校准矩阵。格赖斯的"合作准则"是确保保管记录不是噪声而是有意义信号的通信协议。将保管链视为符号传感器阵列，将神秘主义转变为计量学。

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---
