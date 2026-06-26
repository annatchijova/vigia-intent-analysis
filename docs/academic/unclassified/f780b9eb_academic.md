<!--
VIGIA Academic Documentation
Module: f780b9eb
Batch ID: vigia-doc-0160-f780b9eb
Generated: 2026-05-20T14:56:47.879095+00:00
-->

---

## ENGLISH

### What Is This Module?

This module is the **secure evidence locker** for the VIGÍA system.  
Imagine a high-security laboratory notebook that automatically records every observation, every suspect communication profile, and every chain-of-custody event in a tamper-resistant SQLite database. Scientists do not need to know the technical implementation; they only need to understand that this component guarantees that data retrieved today will be **bit-for-bit identical** to data stored yesterday.

The manager enforces strict admission rules: if a measurement fails integrity checks—for example, a coherence score crosses a safety threshold—the entry is **rejected**. All arithmetic inside the decision boundary is **deterministic integer arithmetic**; the system uses exact integer comparisons (e.g., scaled integer thresholds) rather than approximate real-number operations. There are no probabilistic roundings.

Design motto: **SANS FIND EVIL**.

### Key Concepts

| Concept | Plain-Language Definition | Scientific Relevance |
|---|---|---|
| **Singleton Pattern** | Only one database manager exists per running process. | Prevents conflicting writes and guarantees a single source of forensic truth. |
| **WAL Mode** | Write-Ahead Logging: changes are appended to a separate journal before touching the main file. | Ensures atomic transactions; if power is lost, recovery is deterministic. |
| **ACP Profile** | Adversarial Communication Profile: a structured record of linguistic behavior. | Stores Peircean sign-classification vectors and Gricean maxim-violation counts as integer tuples. |
| **MCP (Coherence Metric)** | An integer-scaled consistency score. | Updates are rejected via exact integer arithmetic when the scaled threshold is breached (e.g., `10 × MCP_int > 25`), signaling probable spoofing. |
| **Sliding Window** | SQLite triggers retain only the 20 most recent documents per emitter. | Bounds storage deterministically; old records are purged by integer count, not heuristic. |
| **Anti-Traversal / Anti-Symlink** | Path sanitization blocks `..` sequences and symbolic link tricks. | Prevents redirection of the database file to an attacker-controlled path. |
| **Daubert Audit Trail** | Immutable log satisfying legal admissibility standards for expert testimony. | Every write carries an integer timestamp and attribution, producing court-ready provenance. |
| **File Permissions (0o640)** | Owner and group may read/write; all others are denied. | Enforces least-privilege at the operating-system level using exact octal integer masks. |

### Core Operations

| Operation | Purpose |
|---|---|
| `store_observation()` | Validates and writes a forensic observation to the database with exact integer timestamp. |
| `store_acp_profile()` | Persists an Adversarial Communication Profile after coherence-metric gate check. |
| `retrieve()` | Returns stored records with integrity verification; rejects corrupted entries. |
| `audit_trail()` | Returns the full immutable log of all database operations for Daubert compliance. |

### Glossary
1. **ACP Profile** — Adversarial Communication Profile: a structured linguistic behavior record used to detect deception patterns.
2. **Audit Trail** — The immutable, time-stamped log of all write operations in the database, required for legal admissibility.
3. **Coherence Metric (MCP)** — An integer-scaled score measuring the internal consistency of a communication profile.
4. **Daubert Compliance** — The property of meeting legal standards for scientific evidence admissibility in court.
5. **Deterministic Integer Arithmetic** — Computation using exact integer comparisons and scaled thresholds; no approximations.
6. **File Permission Mask** — An octal integer specifying which system users may read or write a file.
7. **Singleton Pattern** — An architectural guarantee that exactly one instance of the database manager exists per process.
8. **Sliding Window** — A database trigger that maintains only the N most recent records per emitter, enforced by exact integer count.
9. **WAL Mode** — Write-Ahead Logging: a database journaling mode ensuring atomic, recoverable transactions.
10. **Anti-Traversal** — Path validation that rejects any path component containing `..` or symbolic link redirections.

> **【Scientific Note】**
> Peirce/Eco/Grice terminology is NOT mysticism. In VIGÍA, an ACP Profile stores Peircean sign-classification vectors: the classification of communicative acts as icons, indices, or symbols, each encoded as an integer tuple. Eco's interpretive principle is operationalized in the MCP coherence metric: a profile that shifts codes abruptly is flagged as semiotic inconsistency. Grice's maxim-violation counts are stored as exact integer fields, providing a deterministic measure of communicative deception.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## ESPAÑOL

### ¿Qué es este módulo?

Este módulo es el **almacén seguro de evidencia** del sistema VIGÍA.  
Imagine un cuaderno de laboratorio de alta seguridad que registra automáticamente cada observación, cada perfil de comunicación sospechoso y cada evento de cadena de custodia en una base de datos SQLite resistente a la manipulación. Los científicos no necesitan conocer la implementación técnica; solo necesitan entender que este componente garantiza que los datos recuperados hoy serán **bit a bit idénticos** a los datos almacenados ayer.

El gestor impone reglas de admisión estrictas: si una medición falla las verificaciones de integridad—por ejemplo, una puntuación de coherencia cruza un umbral de seguridad—la entrada es **rechazada**. Toda la aritmética dentro del límite de decisión es **aritmética entera determinista**; el sistema utiliza comparaciones enteras exactas en lugar de operaciones de números reales aproximadas. No hay redondeos probabilísticos.

Lema de diseño: **SANS FIND EVIL**.

### Conceptos clave

| Concepto | Definición | Relevancia Científica |
|---|---|---|
| **Patrón Singleton** | Solo existe un gestor de base de datos por proceso en ejecución. | Previene escrituras conflictivas y garantiza una única fuente de verdad forense. |
| **Modo WAL** | Registro por anticipación (Write-Ahead Logging): los cambios se anexan a un diario separado antes de tocar el archivo principal. | Garantiza transacciones atómicas; si se pierde energía, la recuperación es determinista. |
| **Perfil ACP** | Perfil de Comunicación Adversarial: registro estructurado de comportamiento lingüístico. | Almacena vectores de clasificación de signos peirceanos y conteos de violaciones de máximas de Grice como tuplas enteras. |
| **MCP (Métrica de Coherencia)** | Puntuación de consistencia escalada por enteros. | Las actualizaciones se rechazan mediante aritmética entera exacta cuando se supera el umbral escalado. |
| **Ventana Deslizante** | Los desencadenadores SQLite retienen solo los 20 documentos más recientes por emisor. | Limita el almacenamiento de forma determinista; los registros antiguos se purgan por conteo entero. |
| **Anti-Traversal / Anti-Symlink** | La sanitización de rutas bloquea secuencias `..` y trucos de enlaces simbólicos. | Previene la redirección del archivo de base de datos a una ruta controlada por el atacante. |
| **Rastro de Auditoría Daubert** | Registro inmutable que satisface los estándares de admisibilidad legal para testimonio experto. | Cada escritura lleva una marca de tiempo entera y atribución, produciendo procedencia lista para tribunal. |

### Glosario
1. **Perfil ACP** — Perfil de Comunicación Adversarial: registro estructurado de comportamiento lingüístico para detectar patrones de engaño.
2. **Rastro de Auditoría** — Registro inmutable con marca de tiempo de todas las operaciones de escritura en la base de datos, requerido para admisibilidad legal.
3. **Métrica de Coherencia (MCP)** — Puntuación escalada por enteros que mide la consistencia interna de un perfil de comunicación.
4. **Conformidad Daubert** — Propiedad de cumplir los estándares legales de admisibilidad de evidencia científica en tribunales.
5. **Aritmética Entera Determinista** — Cómputo usando comparaciones enteras exactas y umbrales escalados; sin aproximaciones.
6. **Máscara de Permisos de Archivo** — Entero octal que especifica qué usuarios del sistema pueden leer o escribir un archivo.
7. **Patrón Singleton** — Garantía arquitectónica de que existe exactamente una instancia del gestor de base de datos por proceso.
8. **Ventana Deslizante** — Desencadenador de base de datos que mantiene solo los N registros más recientes por emisor, impuesto por conteo entero exacto.
9. **Modo WAL** — Registro por Anticipación: modo de journaling de base de datos que garantiza transacciones atómicas y recuperables.
10. **Anti-Traversal** — Validación de rutas que rechaza cualquier componente de ruta que contenga `..` o redirecciones de enlace simbólico.

> **【Nota Científica】**
> La terminología de Peirce/Eco/Grice no es misticismo. En VIGÍA, un Perfil ACP almacena vectores de clasificación de signos peirceanos: la clasificación de actos comunicativos como iconos, índices o símbolos, cada uno codificado como una tupla entera. El principio interpretativo de Eco se operacionaliza en la métrica de coherencia MCP. Los conteos de violaciones de máximas de Grice se almacenan como campos enteros exactos, proporcionando una medida determinista del engaño comunicativo.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## РУССКИЙ

### Что это за модуль?

Данный модуль является **безопасным хранилищем доказательств** системы VIGÍA.  
Представьте высокозащищённый лабораторный журнал, автоматически записывающий каждое наблюдение, каждый профиль подозрительной коммуникации и каждое событие цепочки хранения в защищённую от вмешательства базу данных SQLite. Учёным не нужно знать техническую реализацию; им достаточно понимать, что данный компонент гарантирует: данные, извлечённые сегодня, будут **побитово идентичны** данным, сохранённым вчера.

Менеджер применяет строгие правила допуска: если измерение не проходит проверки целостности — например, оценка когерентности превышает порог безопасности — запись **отклоняется**. Вся арифметика внутри границы принятия решений — это **детерминированная целочисленная арифметика**; система использует точные целочисленные сравнения, а не приближённые операции с вещественными числами.

Девиз проектирования: **SANS FIND EVIL**.

### Ключевые концепции

| Концепция | Определение | Научная значимость |
|---|---|---|
| **Шаблон Singleton** | Только один менеджер базы данных существует на один работающий процесс. | Предотвращает конфликтующие записи и гарантирует единственный источник криминалистической истины. |
| **Режим WAL** | Журналирование с опережающей записью: изменения добавляются в отдельный журнал до изменения основного файла. | Обеспечивает атомарные транзакции; восстановление детерминировано. |
| **Профиль ACP** | Профиль состязательной коммуникации: структурированная запись лингвистического поведения. | Хранит пирсовские векторы классификации знаков и целочисленные счётчики нарушений максим Грайса. |
| **MCP (Метрика когерентности)** | Оценка согласованности, масштабированная по целым числам. | Обновления отклоняются через точную целочисленную арифметику при превышении масштабированного порога. |
| **Скользящее окно** | Триггеры SQLite сохраняют только 20 последних документов на эмиттер. | Детерминированно ограничивает хранение; старые записи удаляются по целочисленному счётчику. |
| **Защита от обхода** | Санитизация путей блокирует последовательности `..` и трюки с символическими ссылками. | Предотвращает перенаправление файла базы данных на путь, контролируемый злоумышленником. |
| **Аудиторский след Добера** | Неизменяемый журнал, удовлетворяющий юридическим стандартам допустимости для экспертных показаний. | Каждая запись несёт целочисленную метку времени и атрибуцию. |

### Глоссарий
1. **Профиль ACP** — Профиль состязательной коммуникации: структурированная запись лингвистического поведения для обнаружения паттернов обмана.
2. **Аудиторский след** — Неизменяемый, хронологический журнал всех операций записи в базе данных, необходимый для юридической допустимости.
3. **Метрика когерентности (MCP)** — Целочисленно масштабированная оценка, измеряющая внутреннюю согласованность коммуникационного профиля.
4. **Соответствие Доберу** — Свойство соответствия юридическим стандартам допустимости научных доказательств в суде.
5. **Детерминированная целочисленная арифметика** — Вычисления с точными целочисленными сравнениями и масштабированными порогами; без приближений.
6. **Маска прав доступа к файлу** — Восьмеричное целое число, определяющее, какие пользователи системы могут читать или писать файл.
7. **Шаблон Singleton** — Архитектурная гарантия существования ровно одного экземпляра менеджера базы данных на процесс.
8. **Скользящее окно** — Триггер базы данных, поддерживающий только N последних записей на эмиттер, обеспечиваемый точным целочисленным счётчиком.
9. **Режим WAL** — Журналирование с опережающей записью: режим базы данных, обеспечивающий атомарные восстанавливаемые транзакции.
10. **Защита от обхода** — Валидация путей, отклоняющая любой компонент пути, содержащий `..` или перенаправления символических ссылок.

> **【Научное примечание】**
> Терминология Пирса, Эко и Грайса — не мистика. В VIGÍA профиль ACP хранит пирсовские векторы классификации знаков: классификацию коммуникативных актов как иконов, индексов или символов, каждый закодирован как целочисленный кортеж. Интерпретационный принцип Эко операционализируется в метрике когерентности MCP. Счётчики нарушений максим Грайса хранятся как точные целочисленные поля, обеспечивая детерминированную меру коммуникативного обмана.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## 中文

### 这是什么模块？

本模块是 VIGÍA 系统的**安全证据保险库**。  
想象一本高安全性实验室记录本，自动将每个观察、每个可疑通信配置文件和每个监管链事件记录到防篡改的 SQLite 数据库中。科学家不需要了解技术实现；他们只需要理解，这个组件保证今天检索的数据与昨天存储的数据**逐位相同**。

管理器强制执行严格的接受规则：如果测量未通过完整性检查——例如，一致性评分超过安全阈值——该条目将被**拒绝**。决策边界内的所有运算均为**确定性整数运算**；系统使用精确整数比较（如整数缩放阈值），而非近似实数运算。不存在概率舍入。

设计格言：**SANS FIND EVIL**。

### 关键概念

| 概念 | 通俗定义 | 科学相关性 |
|---|---|---|
| **单例模式** | 每个运行进程只存在一个数据库管理器。 | 防止冲突写入，保证单一取证事实来源。 |
| **WAL 模式** | 预写日志：更改在修改主文件之前追加到单独的日志。 | 确保原子事务；若断电，恢复是确定性的。 |
| **ACP 配置文件** | 对抗性通信配置文件：语言行为的结构化记录。 | 将皮尔斯符号分类向量和格赖斯准则违反计数存储为整数元组。 |
| **MCP（一致性指标）** | 整数缩放的一致性评分。 | 当缩放阈值被突破时（如 `10 × MCP_int > 25`），通过精确整数运算拒绝更新，信号表明可能存在欺骗。 |
| **滑动窗口** | SQLite 触发器每个发送者仅保留最近 20 个文档。 | 以确定性方式限制存储；旧记录按整数计数清除，而非启发式方法。 |
| **反路径遍历/反符号链接** | 路径清理阻止 `..` 序列和符号链接技巧。 | 防止数据库文件被重定向到攻击者控制的路径。 |
| **道伯特审计追踪** | 满足专家证词法律可采性标准的不可变日志。 | 每次写入都带有整数时间戳和归因，产生法庭就绪的来源记录。 |
| **文件权限（0o640）** | 所有者和组可读写；所有其他人被拒绝。 | 使用精确八进制整数掩码在操作系统级别强制执行最小权限。 |

### 词汇表
1. **ACP 配置文件** — 对抗性通信配置文件：用于检测欺骗模式的结构化语言行为记录。
2. **审计追踪** — 数据库中所有写入操作的不可变时间戳日志，法律可采性所需。
3. **一致性指标（MCP）** — 衡量通信配置文件内部一致性的整数缩放评分。
4. **道伯特合规性** — 满足法庭科学证据可采性法律标准的属性。
5. **确定性整数运算** — 使用精确整数比较和缩放阈值的计算；无近似值。
6. **文件权限掩码** — 指定哪些系统用户可以读取或写入文件的八进制整数。
7. **单例模式** — 每个进程恰好存在一个数据库管理器实例的架构保证。
8. **滑动窗口** — 维护每个发送者仅 N 条最新记录的数据库触发器，由精确整数计数强制执行。
9. **WAL 模式** — 预写日志：确保原子可恢复事务的数据库日志记录模式。
10. **反路径遍历** — 路径验证，拒绝任何包含 `..` 或符号链接重定向的路径组件。

> **【科学说明】**
> 皮尔斯、艾柯和格赖斯的术语并非神秘主义。在 VIGÍA 中，ACP 配置文件存储皮尔斯符号分类向量：将交际行为分类为图像符号、索引或象征符号，每种都编码为整数元组。艾柯的解释原则在 MCP 一致性指标中得到操作化：突然转换代码的配置文件被标记为符号学不一致。格赖斯的准则违反计数存储为精确整数字段，提供交际欺骗的确定性度量。

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
