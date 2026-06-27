<!--
VIGIA Academic Documentation
Module: 815ea136
Batch ID: vigia-doc-0086-815ea136
Generated: 2026-05-20T14:56:47.863089+00:00
-->

# Module Documentation: `vigia/forensics/pdf_dual_parser.py`

---

## ENGLISH

### What Is This Module?

A detection engine that compares two independent PDF readers (parsers) — `fitz` (PyMuPDF) and `pypdf` — against the same document. The principle is that certain exploits (such as CVE-2023-21608) appear harmless to one parser but malicious to another. When the parsers disagree on the document's structure or content, this divergence is treated as an active evasion signal rather than random noise. It is analogous to asking two independent witnesses the same question: if their accounts contradict each other in a systematic way, the discrepancy is evidence of deliberate tampering, not a clerical error.

### Key Concepts

| Concept | Description | Scientific Relevance |
|---|---|---|
| Dual-Parser Consensus (`CONSENSUS`) | Both parsers report identical structural findings. | Indicates a document with no detectable structural anomalies. |
| Parser Disagreement (`PARSER_DISAGREEMENT`) | Parsers report different structures or content elements (e.g., one sees JavaScript, the other does not). | Active signal of potential evasion; the document is engineered to deceive one parser. |
| Critical Divergence (`PARSER_DIVERGENCE_CRITICAL`) | Disagreement involves executable or dangerous objects (scripts, launch actions). | High-confidence indicator of deliberate exploitation. |
| Structural Hash | A deterministic integer fingerprint derived from the parsed structure of the document, used for cross-parser comparison. | Enables exact, reproducible comparison without floating-point ambiguity. |
| Evasion Likelihood | A rational number (`Fraction`) quantifying the probability of evasion based on divergence severity. | Deterministic arithmetic; no floating-point rounding in final verdicts. |
| Entropy Display | Exact textual representation of Shannon entropy, rendered without floating-point decimals. | Preserves forensic traceability by avoiding inexact approximations. |

### Module Components

| Component | Role | Deterministic Guarantee |
|---|---|---|
| `ParserVerdict` | Enumeration of possible single-parser conclusions (CLEAN, SUSPICIOUS, MALICIOUS, PARSE_ERROR). | Categorical labels derived from integer thresholds. |
| `AgreementStatus` | Enumeration describing the relationship between the two parsers (CONSENSUS, PARSER_DISAGREEMENT, PARSER_DIVERGENCE_CRITICAL). | Discrete state machine with no continuous variables. |
| `ParserResult` | Data container storing the findings of one parser, including its `structural_hash()`. | `structural_hash()` returns an exact integer. |
| `DualParserAnalysis` | Aggregate object holding both `ParserResult`s and the final `evasion_likelihood`. | `evasion_likelihood` is strictly a `Fraction`. |
| `analyze_pdf_dual()` | Orchestrates parallel parsing and computes divergence. | All branching decisions use integer or Fraction comparisons. |
| `structural_hash()` | Computes a deterministic integer fingerprint from parsed structure. | Pure integer arithmetic; identical inputs yield identical hashes. |
| `display_entropy()` | Returns entropy as an exact string. | Avoids floating-point string formatting entirely. |
| `display_evasion_pct()` | Returns evasion likelihood as a truncated integer percentage. | Uses `int()` truncation on exact Fractions, never on floats. |

### Glossary

- **Parser**: A software component that reads and interprets the internal structure of a PDF file.
- **CVE-2023-21608**: A documented vulnerability in PDF processing where malicious payloads are invisible to certain parsers.
- **Structural Hash**: A deterministic integer digest representing the hierarchical structure detected by a parser.
- **Fraction**: A rational number expressed as a ratio of two integers (numerator/denominator), ensuring exact arithmetic.
- **Deterministic Integer Arithmetic**: Mathematical operations on whole numbers or exact fractions that produce identical results on every execution, free from rounding errors.
- **Evasion**: An attack technique where malware is designed to bypass security checks by exploiting differences in how software interprets data.

### 【Scientific Note】

The terminology of Peirce (semiotics), Eco (codes and interpretative frames), and Grice (cooperative maxims) is employed here as a formal sensor-network model, not as mysticism. Think of `fitz` and `pypdf` as two physical sensors observing the same stimulus. When Sensor A reports "JavaScript present" and Sensor B reports "no executable content," this is not a supernatural event; it is a measurable disagreement in the sign-interpretation layer. Peirce's triadic sign relation gives us the grammar for why the same byte-stream can generate two different interpretants. Eco's theory of codes explains why each parser activates a different decoding frame. Grice's maxims of cooperation provide the logical structure for why a deliberate violation (saying one thing to one parser and another to the rest) constitutes a trace of adversarial intent. This is semiotics as instrumentation logic.

---

## ESPAÑOL

### ¿Qué es este módulo?

Un motor de detección que compara dos lectores (analizadores) independientes de PDF — `fitz` (PyMuPDF) y `pypdf` — sobre el mismo documento. El principio es que ciertos exploits (como CVE-2023-21608) parecen inofensivos para un analizador pero maliciosos para otro. Cuando los analizadores discrepan sobre la estructura o el contenido del documento, esa divergencia se trata como una señal activa de evasión y no como ruido aleatorio. Es análogo a preguntar a dos testigos independientes la misma cuestión: si sus relatos se contradicen de forma sistemática, la discrepancia es evidencia de manipulación deliberada, no de un error administrativo.

### Conceptos Clave

| Concepto | Descripción | Relevancia Científica |
|---|---|---|
| Consenso Dual (`CONSENSUS`) | Ambos analizadores reportan hallazgos estructurales idénticos. | Indica un documento sin anomalías estructurales detectables. |
| Desacuerdo de Analizadores (`PARSER_DISAGREEMENT`) | Los analizadores reportan estructuras o elementos de contenido diferentes (p. ej., uno ve JavaScript y el otro no). | Señal activa de evasión potencial; el documento está diseñado para engañar a un analizador. |
| Divergencia Crítica (`PARSER_DIVERGENCE_CRITICAL`) | El desacuerdo involucra objetos ejecutables o peligrosos (scripts, acciones de lanzamiento). | Indicador de alta confianza de explotación deliberada. |
| Hash Estructural | Una huella digital entera y determinista derivada de la estructura analizada del documento, usada para comparación entre analizadores. | Permite comparaciones exactas y reproducibles sin ambigüedad de punto flotante. |
| Probabilidad de Evasión | Un número racional (`Fraction`) que cuantifica la probabilidad de evasión según la severidad de la divergencia. | Aritmética determinista; sin redondeo de punto flotante en los veredictos finales. |
| Visualización de Entropía | Representación textual exacta de la entropía de Shannon, renderizada sin decimales de punto flotante. | Preserva la trazabilidad forense evitando aproximaciones inexactas. |

### Componentes del Módulo

| Componente | Rol | Garantía Determinista |
|---|---|---|
| `ParserVerdict` | Enumeración de posibles conclusiones de un analizador individual (CLEAN, SUSPICIOUS, MALICIOUS, PARSE_ERROR). | Etiquetas categóricas derivadas de umbrales enteros. |
| `AgreementStatus` | Enumeración que describe la relación entre los dos analizadores (CONSENSUS, PARSER_DISAGREEMENT, PARSER_DIVERGENCE_CRITICAL). | Máquina de estados discreta sin variables continuas. |
| `ParserResult` | Contenedor de datos que almacena los hallazgos de un analizador, incluyendo su `structural_hash()`. | `structural_hash()` devuelve un entero exacto. |
| `DualParserAnalysis` | Objeto agregado que contiene ambos `ParserResult`s y la `evasion_likelihood` final. | `evasion_likelihood` es estrictamente una `Fraction`. |
| `analyze_pdf_dual()` | Orquesta el análisis paralelo y computa la divergencia. | Todas las decisiones de ramificación usan comparaciones enteras o de fracciones. |
| `structural_hash()` | Calcula una huella digital entera y determinista a partir de la estructura analizada. | Aritmética pura de enteros; entradas idénticas producen hashes idénticos. |
| `display_entropy()` | Devuelve la entropía como una cadena exacta. | Evita completamente el formateo de cadenas con punto flotante. |
| `display_evasion_pct()` | Devuelve la probabilidad de evasión como un porcentaje entero truncado. | Usa truncamiento `int()` sobre fracciones exactas, nunca sobre flotantes. |

### Glosario

- **Analizador (Parser)**: Componente de software que lee e interpreta la estructura interna de un archivo PDF.
- **CVE-2023-21608**: Vulnerabilidad documentada en el procesamiento de PDF donde cargas maliciosas son invisibles para ciertos analizadores.
- **Hash Estructural**: Resumen entero determinista que representa la estructura jerárquica detectada por un analizador.
- **Fraction (Fracción)**: Número racional expresado como cociente de dos enteros (numerador/denominador), garantizando aritmética exacta.
- **Aritmética Entera Determinista**: Operaciones matemáticas sobre números enteros o fracciones exactas que producen resultados idénticos en cada ejecución, libres de errores de redondeo.
- **Evasión**: Técnica de ataque donde el malware está diseñado para eludir controles de seguridad explotando diferencias en cómo el software interpreta los datos.

### 【Nota Científica】

La terminología de Peirce (semiótica), Eco (códigos y marcos interpretativos) y Grice (máximas de cooperación) se emplea aquí como un modelo formal de red de sensores, no como misticismo. Piense en `fitz` y `pypdf` como dos sensores físicos observando el mismo estímulo. Cuando el Sensor A reporta "JavaScript presente" y el Sensor B reporta "sin contenido ejecutable", esto no es un evento sobrenatural; es un desacuerdo medible en la capa de interpretación de signos. La relación triádica del signo de Peirce nos da la gramática para entender por qué el mismo flujo de bytes puede generar dos interpretantes distintos. La teoría de los códigos de Eco explica por qué cada analizador activa un marco de decodificación diferente. Las máximas de cooperación de Grice proporcionan la estructura lógica para entender por qué una violación deliberada (decir una cosa a un analizador y otra al resto) constituye un rastro de intención adversarial. Esto es semiótica como lógica de instrumentación.

---

## РУССКИЙ

### Что это за модуль?

Детекционный движок, сравнивающий два независимых PDF-анализатора (парсера) — `fitz` (PyMuPDF) и `pypdf` — применительно к одному и тому же документу. Принцип заключается в том, что определённые эксплойты (такие как CVE-2023-21608) выглядят безобидными для одного парсера, но вредоносными для другого. Когда парсеры расходятся во мнениях относительно структуры или содержимого документа, это расхождение трактуется как активный сигнал уклонения, а не как случайный шум. Это аналогично опросу двух независимых свидетелей одним и тем же вопросом: если их показания систематически противоречат друг другу, расхождение является доказательством преднамеренной подделки, а не канцелярской ошибки.

### Ключевые концепции

| Концепция | Описание | Научная значимость |
|---|---|---|
| Двойной консенсус (`CONSENSUS`) | Оба парсера сообщают об идентичных структурных находках. | Указывает на документ без обнаружимых структурных аномалий. |
| Расхождение парсеров (`PARSER_DISAGREEMENT`) | Парсеры сообщают о различных структурах или элементах содержимого (например, один видит JavaScript, другой — нет). | Активный сигнал потенциального уклонения; документ сконструирован так, чтобы обмануть один из парсеров. |
| Критическое расхождение (`PARSER_DIVERGENCE_CRITICAL`) | Расхождение касается исполняемых или опасных объектов (скрипты, действия запуска). | Индикатор преднамеренной эксплуатации с высокой степенью достоверности. |
| Структурный хеш | Детерминированное целочисленное отпечаток, производное от разобранной структуры документа, используемое для межпарсерного сравнения. | Обеспечивает точное, воспроизводимое сравнение без двусмысленности плавающей точки. |
| Вероятность уклонения | Рациональное число (`Fraction`), количественно оценивающее вероятность уклонения на основе тяжести расхождения. | Детерминированная арифметика; в итоговых вердиктах отсутствует округление чисел с плавающей точкой. |
| Отображение энтропии | Точное текстовое представление энтропии Шеннона, выводимое без десятичных знаков плавающей точки. | Сохраняет судебную прослеживаемость, избегая неточных аппроксимаций. |

### Компоненты модуля

| Компонент | Роль | Детерминированная гарантия |
|---|---|---|
| `ParserVerdict` | Перечисление возможных заключений отдельного парсера (CLEAN, SUSPICIOUS, MALICIOUS, PARSE_ERROR). | Категориальные метки, производные от целочисленных порогов. |
| `AgreementStatus` | Перечисление, описывающее отношение между двумя парсерами (CONSENSUS, PARSER_DISAGREEMENT, PARSER_DIVERGENCE_CRITICAL). | Дискретная конечная машина без непрерывных переменных. |
| `ParserResult` | Контейнер данных, хранящий находки одного парсера, включая его `structural_hash()`. | `structural_hash()` возвращает точное целое число. |
| `DualParserAnalysis` | Агрегированный объект, содержащий оба `ParserResult` и итоговую `evasion_likelihood`. | `evasion_likelihood` строго является `Fraction`. |
| `analyze_pdf_dual()` | Оркестрирует параллельный разбор и вычисляет расхождение. | Все решающие ветвления используют целочисленные или дробные сравнения. |
| `structural_hash()` | Вычисляет детерминированное целочисленное отпечаток из разобранной структуры. | Чистая целочисленная арифметика; идентичные входы дают идентичные хеши. |
| `display_entropy()` | Возвращает энтропию в виде точной строки. | Полностью исключает форматирование строк с плавающей точкой. |
| `display_evasion_pct()` | Возвращает вероятность уклонения в виде усечённого целочисленного процента. | Использует усечение `int()` над точными дробями, никогда над числами с плавающей точкой. |

### Глоссарий

- **Парсер (Parser)**: Программный компонент, читающий и интерпретирующий внутреннюю структуру PDF-файла.
- **CVE-2023-21608**: Документированная уязвимость в обработке PDF, при которой вредоносные объекты невидимы для определённых парсеров.
- **Структурный хеш**: Детерминированное целочисленное дайджест, представляющее иерархическую структуру, обнаруженную парсером.
- **Fraction (Дробь)**: Рациональное число, выраженное как отношение двух целых чисел (числитель/знаменатель), гарантирующее точную арифметику.
- **Детерминированная целочисленная арифметика**: Математические операции над целыми числами или точными дробями, дающие идентичные результаты при каждом выполнении, свободные от ошибок округления.
- **Уклонение (Evasion)**: Техника атаки, при которой вредоносное ПО разработано для обхода проверок безопасности, эксплуатируя различия в интерпретации данных программным обеспечением.

### 【Научное примечание】

Терминология Пирса (семиотика), Эко (коды и интерпретативные рамки) и Грайса (кооперативные максимы) используется здесь как формальная модель сенсорной сети, а не как мистицизм. Воспринимайте `fitz` и `pypdf` как два физических датчика, наблюдающих один и тот же стимул. Когда датчик А сообщает «присутствует JavaScript», а датчик Б сообщает «исполняемого содержимого нет», это не сверхъестественное явление; это измеримое расхождение на уровне интерпретации знаков. Триадическое отношение знака Пирса даёт нам грамматику для понимания того, почему один и тот же поток байтов может породить два разных интерпретанта. Теория кодов Эко объясняет, почему каждый парсер активирует различную декодирующую рамку. Максимы сотрудничества Грайса предоставляют логическую структуру для понимания того, почему преднамеренное нарушение (говоря одно одному парсеру и другое — остальным) составляет след враждебного намерения. Это семиотика как логика приборостроения.

---

## 中文

### 本模块是什么？

这是一个检测引擎，通过让两个独立的PDF阅读器（解析器）——`fitz`（PyMuPDF）和`pypdf`——读取同一份文档，来发现潜在的规避攻击。其原理是：某些漏洞利用程序（如CVE-2023-21608）在一个解析器看来是无害的，但在另一个解析器看来却是恶意的。当两个解析器对文档的结构或内容得出不同结论时，这种分歧不是随机噪声，而是一个主动的规避信号。这种分歧被视为一种逻辑断裂，而非随机误差。这类似于向两位独立的证人询问同一个问题：如果他们的证词在系统性层面上相互矛盾，这种差异就是蓄意篡改的证据，而不是笔误。

### 核心概念

| 概念 | 描述 | 科学意义 |
|---|---|---|
| 双重解析器共识 (`CONSENSUS`) | 两个解析器报告完全相同的结构发现。 | 表明文档不存在可检测的结构异常。 |
| 解析器分歧 (`PARSER_DISAGREEMENT`) | 解析器报告了不同的结构或内容元素（例如，一个发现JavaScript，另一个未发现）。 | 潜在规避的主动信号；文档被设计用于欺骗某一个解析器。 |
| 关键性分歧 (`PARSER_DIVERGENCE_CRITICAL`) | 分歧涉及可执行或危险对象（脚本、启动动作）。 | 高置信度的蓄意利用指标。 |
| 结构哈希 | 从解析出的文档结构导出的确定性整数指纹，用于跨解析器比较。 | 实现精确、可复现的比较，避免浮点歧义。 |
| 规避可能性 | 基于分歧严重程度以有理数（`Fraction`）量化的规避概率。 | 确定性算术；最终裁决中不存在浮点舍入。 |
| 熵显示 | 香农熵的精确文本表示，渲染时不使用浮点小数。 | 通过避免不精确近似来保留取证可追溯性。 |

### 模块组件

| 组件 | 作用 | 确定性保证 |
|---|---|---|
| `ParserVerdict` | 单一解析器可能结论的枚举（CLEAN, SUSPICIOUS, MALICIOUS, PARSE_ERROR）。 | 由整数阈值导出的类别标签。 |
| `AgreementStatus` | 描述两个解析器之间关系的枚举（CONSENSUS, PARSER_DISAGREEMENT, PARSER_DIVERGENCE_CRITICAL）。 | 不含连续变量的离散状态机。 |
| `ParserResult` | 存储单个解析器发现结果的数据容器，包含其 `structural_hash()`。 | `structural_hash()` 返回精确整数。 |
| `DualParserAnalysis` | 聚合对象，包含两个 `ParserResult` 及最终的 `evasion_likelihood`。 | `evasion_likelihood` 严格为 `Fraction`（分数）。 |
| `analyze_pdf_dual()` | 协调并行解析并计算分歧。 | 所有分支决策使用整数或分数比较。 |
| `structural_hash()` | 从解析出的结构计算确定性整数指纹。 | 纯整数运算；相同输入产生相同哈希。 |
| `display_entropy()` | 以精确字符串形式返回熵值。 | 完全避免浮点字符串格式化。 |
| `display_evasion_pct()` | 以截断整数百分比形式返回规避可能性。 | 对精确分数使用 `int()` 截断，不对浮点数使用。 |

### 术语表

- **解析器 (Parser)**：读取并解释PDF文件内部结构的软件组件。
- **CVE-2023-21608**：PDF处理中已记录的漏洞，恶意载荷对某些解析器不可见。
- **结构哈希**：由解析器检测到的层次结构所表示的确定性整数摘要。
- **Fraction（分数）**：以两个整数之比（分子/分母）表示的有理数，确保精确算术。
- **确定性整数运算**：对整数或精确分数进行的数学运算，每次执行产生相同结果，无舍入误差。
- **规避 (Evasion)**：恶意软件利用软件在数据解释上的差异来绕过安全检查的攻击技术。
- **取证工件 (Artifact)**：在数字取证过程中被提取、分析和记录的结构化数据对象。
- **逻辑断裂**：两个解析器对同一文档产生不同解释项时出现的可检测的结构不一致。

### 【科学说明】

此处使用的皮尔斯（符号学）、艾柯（编码与解释框架）和格赖斯（合作原则）术语，是一种形式化的传感器网络模型，而非神秘主义。请将 `fitz` 和 `pypdf` 想象为观测同一刺激的物理传感器。当传感器A报告"存在JavaScript"，而传感器B报告"无可执行内容"时，这不是超自然事件，而是符号解释层上可测量的分歧。皮尔斯的符号三元关系为我们提供了语法，说明为何相同的字节流可以产生两种不同的解释项。艾柯的编码理论解释了为何每个解析器会激活不同的解码框架。格赖斯的合作准则提供了逻辑结构，说明为何一种蓄意违反（对一个解析器说一套，对其余的说另一套）构成了对抗意图的痕迹。这是作为仪器逻辑的符号学。

---

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
