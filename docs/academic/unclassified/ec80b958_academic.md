<!-- VIGÍA Academic Documentation | Module: generate_report.py | Hash: ec80b958 | Format: Standardized v1 -->

## ENGLISH

### What Is This Module?

`generate_report.py` (VIGÍA hash `ec80b958`) is the deterministic Amicus Curiae reporting engine — the terminal node of the VIGÍA processing pipeline. Its function is to serialize the complete state of forensic investigations into structured, court-ready reports that are bit-for-bit reproducible from the same input state on any conformant system.

The module sits downstream of evidence ingestion (`evidence_acquisition.py`), cryptographic verification (`hash_verification.py`), and provenance tracking (`chain_of_custody.py`). It receives the evidentiary state E_i = (A_i, M_i, P_i) — acquired artifacts, derived metadata, and provenance ledger — and applies a total serialization function S_canon = φ_enc ∘ φ_q ∘ φ_ord. This composition enforces three deterministic properties: (1) φ_ord imposes a total lexicographic order on all keys and collections, eliminating hash-table iteration variance; (2) φ_q maps all numeric metrics to fixed-precision decimal D_15 with 15 significant digits, so platform-specific IEEE 754 deviations do not propagate; (3) φ_enc produces canonical UTF-8 JSON without BOM, with Unix LF line endings and no insignificant whitespace.

The output is a single minified JSON file conforming to the VIGÍA Amicus Curiae schema version 2.1, with four top-level keys: `case_manifest`, `evidentiary_digest`, `provenance_chain`, and `integrity_proof`. The SHA-256 of the output byte sequence is appended as the integrity proof. The result is a report that any independent examiner can reproduce byte-for-byte from the same case database.

### Key Concepts

| Concept | Definition |
|---------|-----------|
| Serialization function S_canon | Composition φ_enc ∘ φ_q ∘ φ_ord; provably injective on valid evidentiary states |
| φ_ord (ordering) | Lexicographic total order on all keys and collections by UTF-8 code point; eliminates hash-table nondeterminism |
| φ_q (quantization) | Maps all floating-point metrics to D_15 (15 significant decimal digits); prevents IEEE 754 platform variance |
| φ_enc (encoding) | Canonical UTF-8 JSON without BOM; Unix LF line endings; no insignificant whitespace; RFC 8259 conformant |
| Amicus Curiae schema v2.1 | Four top-level keys: case_manifest, evidentiary_digest, provenance_chain, integrity_proof |
| Bitwise reproducibility | For any fixed state E, output is invariant across executions on any conformant platform; H(output | E) = 0 |
| Topological normalization | Phase II: dependency DAG of artifacts sorted topologically under lexicographic artifact ID order |
| Integrity proof | SHA-256 of the full output byte sequence, appended as the integrity_proof field |
| generated_at_utc | Derived from the investigation closing timestamp in chain_of_custody.py — not from wall-clock time of report generation |

> **【Scientific Note】**
> This module is best understood as a notary function. A notary does not analyze documents — it faithfully records their content in a format that is legally recognized and independently verifiable. Similarly, `generate_report.py` does not interpret evidence; it serializes the terminal state of an investigation into a canonical form that any court system or independent auditor can verify byte-for-byte. The three-stage composition (order → quantize → encode) is not mysticism — it is the same process used in any measurement system that must be traceable across laboratories: define a canonical unit (UTF-8 + lexicographic order), define a measurement precision (D_15), define a recording format (RFC 8259 JSON). Peirce, Eco, and Grice operate upstream of this module; by the time data reaches `generate_report.py`, the intentionality analysis is complete and only faithful recording remains.

### Glossary

| Term | Definition |
|------|-----------|
| generate_report.py | Deterministic module that serializes the complete forensic case state into a reproducible Amicus Curiae JSON report |
| Amicus Curiae | "Friend of the court" — a structured evidentiary submission for judicial review |
| S_canon | Total serialization function; composition of ordering, quantization, and encoding maps |
| case_manifest | Top-level schema key: array of case objects with case_id, title, examiner, opened_at, closed_at |
| evidentiary_digest | Top-level schema key: array of artifact records with artifact_id, source_hash, extracted_path, classification |
| provenance_chain | Top-level schema key: array of custody events with event_id, timestamp_utc, actor, action |
| integrity_proof | Top-level schema key: object with algorithm ("SHA-256"), digest, generated_at_utc |
| fixed-precision domain D_15 | Set of decimal values with 15 significant digits; eliminates IEEE 754 platform-specific rounding variance |
| topological sort | Phase II algorithm resolving artifact dependency order; ensures isomorphic graphs produce identical linearizations |

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## ESPAÑOL

### ¿Qué es este módulo?

`generate_report.py` (hash VIGÍA `ec80b958`) es el motor determinista de generación de informes Amicus Curiae — el nodo terminal del pipeline de procesamiento de VIGÍA. Su función es serializar el estado completo de las investigaciones forenses en informes estructurados, listos para la corte, que son bit a bit reproducibles desde el mismo estado de entrada en cualquier sistema conforme.

El módulo se ubica aguas abajo de la ingesta de pruebas (`evidence_acquisition.py`), la verificación criptográfica (`hash_verification.py`) y el rastreo de procedencia (`chain_of_custody.py`). Recibe el estado probatorio E_i = (A_i, M_i, P_i) — artefactos adquiridos, metadatos derivados y libro de procedencia — y aplica una función total de serialización S_canon = φ_enc ∘ φ_q ∘ φ_ord. Esta composición impone tres propiedades deterministas: (1) φ_ord impone un orden lexicográfico total sobre todas las claves y colecciones, eliminando la varianza de iteración de tablas hash; (2) φ_q mapea todas las métricas numéricas al dominio decimal de precisión fija D_15 con 15 dígitos significativos, para que las desviaciones específicas de la plataforma de IEEE 754 no se propaguen; (3) φ_enc produce JSON UTF-8 canónico sin BOM, con finales de línea Unix LF y sin espacios en blanco insignificantes.

La salida es un único archivo JSON minificado conforme al esquema Amicus Curiae de VIGÍA versión 2.1, con cuatro claves de primer nivel: `case_manifest`, `evidentiary_digest`, `provenance_chain` e `integrity_proof`. El SHA-256 de la secuencia de bytes de salida se adjunta como prueba de integridad. El resultado es un informe que cualquier perito independiente puede reproducir byte a byte desde la misma base de datos de casos.

### Conceptos clave

| Concepto | Definición |
|---------|-----------|
| Función de serialización S_canon | Composición φ_enc ∘ φ_q ∘ φ_ord; demostratoriamente inyectiva sobre estados probatorios válidos |
| φ_ord (ordenamiento) | Orden total lexicográfico sobre todas las claves y colecciones por punto de código UTF-8; elimina no-determinismo de tablas hash |
| φ_q (cuantización) | Mapea todas las métricas de punto flotante a D_15 (15 dígitos decimales significativos); previene varianza de IEEE 754 por plataforma |
| φ_enc (codificación) | JSON UTF-8 canónico sin BOM; finales de línea Unix LF; sin espacios en blanco insignificantes; conforme a RFC 8259 |
| Esquema Amicus Curiae v2.1 | Cuatro claves de primer nivel: case_manifest, evidentiary_digest, provenance_chain, integrity_proof |
| Reproducibilidad bit a bit | Para cualquier estado fijo E, la salida es invariante entre ejecuciones en cualquier plataforma conforme; H(salida | E) = 0 |
| Normalización topológica | Fase II: DAG de dependencias de artefactos ordenado topológicamente bajo orden lexicográfico de identificadores de artefactos |
| Prueba de integridad | SHA-256 de la secuencia de bytes de salida completa, adjuntado como campo integrity_proof |
| generated_at_utc | Derivado del timestamp de cierre de la investigación en chain_of_custody.py — no del tiempo de pared de la generación del informe |

> **【Nota Científica】**
> Este módulo se entiende mejor como una función notarial. Un notario no analiza documentos — los registra fielmente en un formato legalmente reconocido e independientemente verificable. De manera análoga, `generate_report.py` no interpreta evidencia; serializa el estado terminal de una investigación en una forma canónica que cualquier sistema judicial o auditor independiente puede verificar byte a byte. La composición de tres etapas (ordenar → cuantizar → codificar) no es algo misterioso — es el mismo proceso usado en cualquier sistema de medición que debe ser trazable entre laboratorios: definir una unidad canónica (UTF-8 + orden lexicográfico), definir una precisión de medición (D_15), definir un formato de registro (JSON RFC 8259). Peirce, Eco y Grice operan aguas arriba de este módulo; cuando los datos llegan a `generate_report.py`, el análisis de intencionalidad está completo y solo resta el registro fiel.

### Glosario

| Término | Definición |
|--------|-----------|
| generate_report.py | Módulo determinista que serializa el estado completo del caso forense en un informe JSON Amicus Curiae reproducible |
| Amicus Curiae | "Amigo de la corte" — una presentación probatoria estructurada para revisión judicial |
| S_canon | Función total de serialización; composición de mapeos de ordenamiento, cuantización y codificación |
| case_manifest | Clave de esquema de primer nivel: arreglo de objetos de caso con case_id, title, examiner, opened_at, closed_at |
| evidentiary_digest | Clave de esquema de primer nivel: arreglo de registros de artefactos con artifact_id, source_hash, extracted_path, classification |
| provenance_chain | Clave de esquema de primer nivel: arreglo de eventos de custodia con event_id, timestamp_utc, actor, action |
| integrity_proof | Clave de esquema de primer nivel: objeto con algorithm ("SHA-256"), digest, generated_at_utc |
| dominio de precisión fija D_15 | Conjunto de valores decimales con 15 dígitos significativos; elimina varianza de redondeo específica de plataforma de IEEE 754 |
| ordenamiento topológico | Algoritmo de Fase II que resuelve el orden de dependencias de artefactos; garantiza que grafos isomorfos producen linealizaciones idénticas |

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## РУССКИЙ

### Что представляет собой этот модуль?

`generate_report.py` (хеш VIGÍA `ec80b958`) — детерминированный механизм формирования заключений *amicus curiae* — терминальный узел конвейера обработки VIGÍA. Его назначение — сериализовать полное состояние судебно-экспертных расследований в структурированные, готовые для суда отчёты, которые являются побитово воспроизводимыми из одного и того же входного состояния на любой совместимой системе.

Модуль расположен ниже по потоку относительно изъятия доказательств (`evidence_acquisition.py`), криптографической верификации (`hash_verification.py`) и учёта происхождения (`chain_of_custody.py`). Он принимает доказательственное состояние E_i = (A_i, M_i, P_i) — изъятые артефакты, производные метаданные и реестр происхождения — и применяет тотальную функцию сериализации S_canon = φ_enc ∘ φ_q ∘ φ_ord. Данная композиция обеспечивает три детерминистских свойства: (1) φ_ord навязывает полный лексикографический порядок всем ключам и коллекциям, устраняя вариативность итерации хеш-таблиц; (2) φ_q отображает все числовые метрики на область фиксированной точности D_15 с 15 значащими цифрами; (3) φ_enc производит канонический UTF-8 JSON без BOM, с концами строк Unix LF и без незначимых пробелов.

Выходными данными является единственный минифицированный JSON-файл, соответствующий схеме *amicus curiae* VIGÍA версии 2.1, с четырьмя ключами верхнего уровня: `case_manifest`, `evidentiary_digest`, `provenance_chain` и `integrity_proof`. SHA-256 выходной байтовой последовательности прикрепляется как доказательство целостности. Результат — отчёт, который любой независимый эксперт может воспроизвести байт в байт из той же базы данных дел.

### Ключевые понятия

| Понятие | Определение |
|---------|------------|
| Функция сериализации S_canon | Композиция φ_enc ∘ φ_q ∘ φ_ord; доказуемо инъективна на допустимых доказательственных состояниях |
| φ_ord (упорядочение) | Полный лексикографический порядок всех ключей и коллекций по кодовым точкам UTF-8; устраняет недетерминизм хеш-таблиц |
| φ_q (квантование) | Отображает все показатели с плавающей точкой на D_15 (15 значащих десятичных цифр); предотвращает платформенную вариативность IEEE 754 |
| φ_enc (кодирование) | Канонический UTF-8 JSON без BOM; концы строк Unix LF; без незначимых пробелов; соответствие RFC 8259 |
| Схема Amicus Curiae v2.1 | Четыре ключа верхнего уровня: case_manifest, evidentiary_digest, provenance_chain, integrity_proof |
| Побитовая воспроизводимость | Для любого фиксированного состояния E выходные данные инвариантны между выполнениями на любой совместимой платформе; H(выход | E) = 0 |
| Топологическая нормализация | Фаза II: DAG зависимостей артефактов, топологически отсортированный под лексикографическим порядком идентификаторов артефактов |
| Доказательство целостности | SHA-256 полной выходной байтовой последовательности, прикреплённый как поле integrity_proof |
| generated_at_utc | Производится от временнóй метки закрытия расследования в chain_of_custody.py — не от астрономического времени генерации отчёта |

> **【Научное примечание】**
> Этот модуль лучше всего понимать как нотариальную функцию. Нотариус не анализирует документы — он достоверно фиксирует их содержание в юридически признанном и независимо верифицируемом формате. Аналогично, `generate_report.py` не интерпретирует доказательства; он сериализует конечное состояние расследования в каноническую форму, которую любая судебная система или независимый аудитор может проверить байт в байт. Трёхэтапная композиция (упорядочить → квантовать → закодировать) — не мистика: это тот же процесс, который применяется в любой измерительной системе, трассируемой между лабораториями: определить каноническую единицу (UTF-8 + лексикографический порядок), определить точность измерения (D_15), определить формат записи (RFC 8259 JSON). Пирс, Эко и Грайс работают выше по потоку относительно этого модуля; к моменту поступления данных в `generate_report.py` анализ интенциональности завершён и остаётся лишь достоверная запись.

### Глоссарий

| Термин | Определение |
|--------|------------|
| generate_report.py | Детерминистский модуль, сериализующий полное состояние форензического дела в воспроизводимый JSON-отчёт Amicus Curiae |
| Amicus Curiae | «Друг суда» — структурированное доказательственное представление для судебного рецензирования |
| S_canon | Тотальная функция сериализации; композиция отображений упорядочения, квантования и кодирования |
| case_manifest | Ключ схемы верхнего уровня: массив объектов дела с case_id, title, examiner, opened_at, closed_at |
| evidentiary_digest | Ключ схемы верхнего уровня: массив записей артефактов с artifact_id, source_hash, extracted_path, classification |
| provenance_chain | Ключ схемы верхнего уровня: массив событий цепочки хранения с event_id, timestamp_utc, actor, action |
| integrity_proof | Ключ схемы верхнего уровня: объект с algorithm («SHA-256»), digest, generated_at_utc |
| область фиксированной точности D_15 | Множество десятичных значений с 15 значащими цифрами; устраняет платформенно-специфическую вариативность округления IEEE 754 |
| топологическая сортировка | Алгоритм Фазы II, разрешающий порядок зависимостей артефактов; гарантирует, что изоморфные графы дают идентичные линеаризации |

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## 中文

### 本模块是什么？

`generate_report.py`（VIGÍA 哈希值 `ec80b958`）是确定性 Amicus Curiae 报告引擎——VIGÍA 处理流水线的终端节点。其职能是将取证调查的完整状态序列化为结构化、可供法庭使用的报告，这些报告在任何兼容系统上均可从相同输入状态逐位复现。

本模块位于证据获取（`evidence_acquisition.py`）、密码学验证（`hash_verification.py`）和来源追溯（`chain_of_custody.py`）的下游。它接收证据状态 E_i = (A_i, M_i, P_i)——已获取的取证工件、衍生元数据和溯源账本——并应用全映射序列化函数 S_canon = φ_enc ∘ φ_q ∘ φ_ord。该组合强制执行三项确定性属性：（1）φ_ord 按 UTF-8 码点对所有键和集合施加全词典序，消除哈希表迭代不确定性；（2）φ_q 将所有数值指标映射至 15 位有效数字的固定精度十进制域 D_15，防止平台特定的 IEEE 754 偏差传播；（3）φ_enc 生成规范 UTF-8 JSON（无 BOM、Unix LF 行尾、无多余空白）。

输出为单个最小化 JSON 文件，符合 VIGÍA Amicus Curiae 模式 2.1 版，包含四个顶层键：`case_manifest`、`evidentiary_digest`、`provenance_chain` 和 `integrity_proof`。输出字节序列的 SHA-256 作为完整性证明附加。结果是任何独立检验员都能从相同案件数据库逐字节复现的报告。

### 关键概念

| 概念 | 定义 |
|------|------|
| 序列化函数 S_canon | 组合 φ_enc ∘ φ_q ∘ φ_ord；在有效证据状态上可证明为单射 |
| φ_ord（排序） | 按 UTF-8 码点对所有键和集合施加全词典序；消除哈希表非确定性 |
| φ_q（量化） | 将所有浮点指标映射至 D_15（15 位有效十进制数字）；防止 IEEE 754 平台差异 |
| φ_enc（编码） | 规范 UTF-8 JSON，无 BOM；Unix LF 行尾；无多余空白；符合 RFC 8259 |
| Amicus Curiae 模式 v2.1 | 四个顶层键：case_manifest、evidentiary_digest、provenance_chain、integrity_proof |
| 按位可复现性 | 对于任意固定状态 E，输出在任何兼容平台上跨执行保持不变；H(输出 | E) = 0 |
| 拓扑规范化 | 阶段 II：取证工件依赖有向无环图在取证工件 ID 词典序下拓扑排序 |
| 完整性证明 | 完整输出字节序列的 SHA-256，附加为 integrity_proof 字段 |
| generated_at_utc | 来源于 chain_of_custody.py 中记录的调查关闭时间戳——而非报告生成时的系统时钟 |

> **【科学说明】**
> 理解本模块的最佳方式是将其视为公证职能。公证人不分析文件——而是以法律认可的、可独立验证的格式忠实记录其内容。类似地，`generate_report.py` 不解读证据；它将调查的终态序列化为任何司法系统或独立审计员都能逐字节验证的规范形式。三阶段组合（排序 → 量化 → 编码）并非神秘之举——这与任何必须跨实验室可追溯的测量系统所采用的流程完全相同：定义规范单位（UTF-8 + 词典序）、定义测量精度（D_15）、定义记录格式（RFC 8259 JSON）。皮尔斯、艾柯和格赖斯在本模块上游运作；当数据到达 `generate_report.py` 时，意图性分析已经完成，剩下的只是忠实记录。

### 术语表

| 术语 | 定义 |
|------|------|
| generate_report.py | 将完整取证案件状态序列化为可复现 Amicus Curiae JSON 报告的确定性模块 |
| Amicus Curiae | "法庭之友"——用于司法审查的结构化证据报告 |
| S_canon | 全映射序列化函数；排序、量化和编码映射的组合 |
| case_manifest | 顶层模式键：包含 case_id、title、examiner、opened_at、closed_at 的案件对象数组 |
| evidentiary_digest | 顶层模式键：包含 artifact_id、source_hash、extracted_path、classification 的取证工件记录数组 |
| provenance_chain | 顶层模式键：包含 event_id、timestamp_utc、actor、action 的保管事件数组 |
| integrity_proof | 顶层模式键：包含 algorithm（"SHA-256"）、digest、generated_at_utc 的对象 |
| 固定精度域 D_15 | 具有 15 位有效数字的十进制值集合；消除 IEEE 754 平台特定舍入差异 |
| 拓扑排序 | 阶段 II 算法，解析取证工件依赖顺序；确保同构图产生一致的线性化 |

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
