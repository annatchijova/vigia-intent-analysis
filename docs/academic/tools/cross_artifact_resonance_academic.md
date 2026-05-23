<!--
VIGIA Academic Documentation
Module: 2f6f63bf
Batch ID: vigia-doc-0154-2f6f63bf
Generated: 2026-05-20T14:56:47.877733+00:00
-->

---
doc_hash: 2f6f63bf
module: vigia/tools/cross_artifact_resonance.py
languages: [EN, ES, RU, ZH]
generated_by: moonshot-kimi-k2.6-batch-api
license: Apache-2.0
---

ENGLISH:
- Title: Cross-Artifact Resonance Analyzer (`vigia/tools/cross_artifact_resonance.py`)
- What Is This Module? This is a forensic analysis module that treats digital evidence (emails, PDFs) as "witness statements." It extracts claims (who, what, when) from each piece of evidence and checks if they tell the same story. If one email claims an event happened in Q4 2024 but the attached PDF references Q1 2025, the module flags a semantic inconsistency. It uses deterministic integer arithmetic to compare timestamps and categorical codes, avoiding probabilistic floating-point approximations.
- Key Concepts table:
  - Cross-Artifact Resonance: The degree to which separate pieces of digital evidence agree on facts, topics, and timelines.
  - ArtifactClaim: A structured assertion extracted from a document (e.g., "Date = 2024-10-15", "Topic = Budget").
  - SemanticConflict: A contradiction between two claims (temporal mismatch, actor mismatch, topic mismatch).
  - ResonanceAnalysis: The final report summarizing coherence and conflicts across all submitted artifacts.
  - TOPIC_TAXONOMY: A controlled dictionary mapping terms to integer category codes for deterministic comparison.
  - ATTACHMENT_VERBS: A lexical index of action words used to link an email to its attachments semantically.
- Glossary:
  - Semantic coherence: Logical consistency in meaning across multiple documents.
  - Deterministic integer arithmetic: Calculations using whole numbers (e.g., Unix epochs, taxonomy IDs) that produce identical results on every run, unlike floating-point estimates.
  - Forensic artifact: Any digital object subjected to investigation (email, PDF, log file).
  - Temporal mismatch: A conflict where two sources disagree about when an event occurred.
- Scientific Note: The terminology of Peirce (signs and interpretants), Eco (codes and overcoding), and Grice (conversational maxims) is sometimes perceived as esoteric. In this module, they function exactly like calibrated sensors in a laboratory: Peirce's semiotics provides the syntax for decoding signs (who sent what), Eco's cultural codes provide the taxonomy (what category an event belongs to), and Grice's maxims provide the logic for expecting truthfulness and relevance (why a mismatch is suspicious). When multiple "sensors" (artifacts) report conflicting measurements of the same reality, we do not invoke mysticism; we record a sensor discrepancy and investigate further. The module uses these formal models as deterministic filters, not magical intuition.

ESPAÑOL:
- Title: Analizador de Resonancia Cruzada entre Artefactos
- What Is This Module? -> "¿Qué es este módulo?"
- Similar content.
- Key concepts with Spanish terms:
  - Resonancia entre artefactos: Grado de concordancia...
  - Reclamación de artefacto (ArtifactClaim): Aserción estructurada...
  - Conflicto semántico: Contradicción entre dos afirmaciones...
  - Análisis de resonancia: Informe final...
  - TAXONOMÍA DE TEMAS (TOPIC_TAXONOMY): Diccionario controlado...
  - VERBOS DE ADJUNTO (ATTACHMENT_VERBS): Índice léxico...
- Glossary:
  - Coherencia semántica
  - Aritmética entera determinista
  - Artefacto forense
  - Discrepancia temporal
- Scientific Note: Nota Científica. Same sensor analogy. Peirce, Eco, Grice. In Spanish, Peirce is Peirce, Eco is Eco, Grice is Grice.

РУССКИЙ:
- Title: Анализатор межартефактного резонанса
- What Is This Module? -> "Что это за модуль?"
- Key concepts:
  - Межартефактный резонанс: Степень согласованности...
  - Утверждение артефакта (ArtifactClaim): Структурированное утверждение...
  - Семантический конфликт: Противоречие между утверждениями...
  - Анализ резонанса: Итоговый отчёт...
  - ТАКСОНОМИЯ ТЕМ (TOPIC_TAXONOMY): Контролируемый словарь...
  - ГЛАГОЛЫ ВЛОЖЕНИЙ (ATTACHMENT_VERBS): Лексический индекс...
- Glossary:
  - Семантическая когерентность
  - Детерминистская целочисленная арифметика
  - Цифровой артефакт (криминалистический)
  - Временное несоответствие
- Scientific Note: Научное примечание. Sensor analogy. Peirce (Пирс), Eco (Эко), Grice (Грайс).

中文:
- Title: 跨取证工件共振分析器
- What Is This Module? -> "本模块是什么？"
- Key concepts:
  - 跨取证工件共振 (Cross-Artifact Resonance): 多份数字证据在事实、主题与时间线上的一致程度。
  - 取证工件断言 (ArtifactClaim): 从文档中提取的结构化陈述。
  - 语义冲突 (SemanticConflict): 两个断言之间的矛盾。
  - 共振分析结果 (ResonanceAnalysis): 最终报告。
  - 主题分类体系 (TOPIC_TAXONOMY): 受控词典，将术语映射为整数类别码。
  - 附件动词索引 (ATTACHMENT_VERBS): 用于语义关联邮件与附件的动词词表。
- Glossary:
  - 语义连贯性
  - 确定性整数运算
  - 取证工件 (forensic artifact) - user explicitly said use 取证工件 (not 制品)
- Scientific Note: 【科学说明】. Need to mention 皮尔斯 (Peirce), 艾柯 (Eco - specified), 格赖斯 (Grice - specified). Sensor analogy: 传感器/探测器. Terminology is formal models. Not mysticism (神秘主义). Use deterministic filters.


Also need to ensure I don't use floating-point explanations. Emphasize deterministic integer arithmetic. The module compares timestamps as integers (Unix epoch), topic IDs as integers, etc. No probability scores from floats. This is important.



---

### ENGLISH

**Module:** `vigia/tools/cross_artifact_resonance.py`  
**Full Name:** Cross-Artifact Resonance Analyzer

#### What Is This Module?
This module performs multi-source forensic verification. In scientific terms, it treats each digital document (such as an email or a PDF) as an independent sensor recording a claim about reality. The module extracts structured assertions—who acted, what occurred, and when—from each document. It then cross-references these assertions using deterministic integer arithmetic (for example, exact Unix timestamps and fixed-category taxonomy codes) to detect contradictions. An attacker may forge a single document perfectly, but sustaining logical consistency across multiple independent documents is statistically and computationally difficult. This module automates that consistency check without using floating-point approximations.

#### Key Concepts

| Concept | Role in the Module | Scientific Analogy |
|---|---|---|
| **Cross-Artifact Resonance** | Measures whether separate pieces of evidence tell the same story. | Cross-validation between multiple instruments measuring the same variable. |
| **ArtifactClaim** | A structured assertion extracted from one document (e.g., date, sender, topic). | A single sensor reading with metadata. |
| **SemanticConflict** | A contradiction detected between two or more claims (temporal, topical, or actor mismatch). | A sensor outlier or instrument disagreement. |
| **ResonanceAnalysis** | The final deterministic report listing all resonances and conflicts. | A consolidated lab report from multiple instruments. |
| **TOPIC_TAXONOMY** | A controlled vocabulary that maps every possible topic to a unique integer code. | A reference calibration table with discrete indices. |
| **ATTACHMENT_VERBS** | A lexical index of action words linking an email to its attachments. | A protocol dictionary defining valid coupling terms. |

#### Glossary

| Term | Definition |
|---|---|
| **Semantic coherence** | The property of multiple documents agreeing in meaning, timeframe, and subject matter. |
| **Deterministic integer arithmetic** | Mathematical operations performed exclusively with whole numbers, ensuring that identical inputs always produce identical outputs, free of rounding errors. |
| **Forensic artifact** | Any digital object subjected to investigation (e.g., email, PDF, log file). |
| **Temporal mismatch** | A conflict in which two sources assert incompatible dates or times for the same event. |

#### 【Scientific Note】
The framework employs terminology derived from **Peirce** (semiotics: the logic of signs), **Eco** (cultural coding and overcoding), and **Grice** (conversational maxims: expectations of truthfulness, relevance, and clarity). These terms are not mystical constructs; they function as formal, deterministic models of communication. Think of them as laboratory instruments: Peirce provides the grammar for decoding signs (who sent what), Eco provides the categorical taxonomy (what domain an event belongs to), and Grice provides the logical axioms that make deception detectable (why an irrelevant or contradictory statement is anomalous). When two forensic artifacts produce incompatible readings, the module records a **sensor discrepancy**—not a supernatural intuition—and flags it for investigator review. All comparisons are performed via deterministic integer arithmetic, not probabilistic scoring.

---

### ESPAÑOL

**Módulo:** `vigia/tools/cross_artifact_resonance.py`  
**Nombre completo:** Analizador de Resonancia Cruzada entre Artefactos

#### ¿Qué es este módulo?
Este módulo realiza verificación forense multi-fuente. En términos científicos, trata cada documento digital (como un correo electrónico o un PDF) como un sensor independiente que registra una afirmación sobre la realidad. El módulo extrae aserciones estructuradas—quién actuó, qué ocurrió y cuándo—de cada documento. Luego contrasta estas aserciones mediante aritmética entera determinista (por ejemplo, marcas de tiempo Unix exactas y códigos de taxonomía de categoría fija) para detectar contradicciones. Un atacante puede falsificar un solo documento a la perfección, pero mantener la coherencia lógica entre múltiples documentos independientes es difícil estadística y computacionalmente. Este módulo automatiza esa verificación de coherencia sin utilizar aproximaciones de punto flotante.

#### Conceptos clave

| Concepto | Rol en el módulo | Analogía científica |
|---|---|---|
| **Resonancia entre artefactos** | Mide si piezas separadas de evidencia cuentan la misma historia. | Validación cruzada entre instrumentos que miden la misma variable. |
| **Reclamación de artefacto (ArtifactClaim)** | Aserción estructurada extraída de un documento (fecha, remitente, tema). | Una lectura de sensor individual con metadatos. |
| **Conflicto semántico (SemanticConflict)** | Contradicción detectada entre dos o más reclamaciones (temporal, temática o de actor). | Un valor atípico o desacuerdo entre instrumentos. |
| **Análisis de resonancia (ResonanceAnalysis)** | Informe determinista final que lista todas las resonancias y conflictos. | Informe de laboratorio consolidado de múltiples instrumentos. |
| **TAXONOMÍA DE TEMAS (TOPIC_TAXONOMY)** | Vocabulario controlado que asigna a cada tema un código entero único. | Tabla de calibración de referencia con índices discretos. |
| **VERBOS DE ADJUNTO (ATTACHMENT_VERBS)** | Índice léxico de verbos de acción que vinculan semánticamente un correo con sus adjuntos. | Diccionario de protocolo que define términos de acoplamiento válidos. |

#### Glosario

| Término | Definición |
|---|---|
| **Coherencia semántica** | Propiedad por la cual múltiples documentos concuerdan en significado, marco temporal y materia. |
| **Aritmética entera determinista** | Operaciones matemáticas realizadas exclusivamente con números enteros, garantizando que entradas idénticas produzcan salidas idénticas, libres de errores de redondeo. |
| **Artefacto forense** | Cualquier objeto digital sometido a investigación (correo, PDF, registro de registro). |
| **Discrepancia temporal** | Conflicto en el que dos fuentes afirman fechas u horas incompatibles para el mismo evento. |

#### 【Nota Científica】
El marco emplea terminología derivada de **Peirce** (semiótica: la lógica de los signos), **Eco** (codificación cultural y sobrecodificación) y **Grice** (máximas conversacionales: expectativas de veracidad, relevancia y claridad). Estos términos no son constructos místicos; funcionan como modelos formales y deterministas de la comunicación. Piense en ellos como instrumentos de laboratorio: Peirce proporciona la gramática para decodificar signos (quién envió qué), Eco proporciona la taxonomía categórica (a qué dominio pertenece un evento) y Grice proporciona los axiomas lógicos que hacen detectable el engaño (por qué una declaración irrelevante o contradictoria es anómala). Cuando dos artefactos forenses producen lecturas incompatibles, el módulo registra una **discrepancia entre sensores**—no una intuición sobrenatural—y la señala para revisión del investigador. Todas las comparaciones se realizan mediante aritmética entera determinista, no puntuación probabilística.

---

### РУССКИЙ

**Модуль:** `vigia/tools/cross_artifact_resonance.py`  
**Полное название:** Анализатор межартефактного резонанса

#### Что это за модуль?
Этот модуль выполняет многоисточниковую судебно-экспертную верификацию. В научных терминах он трактует каждый цифровой документ (например, электронное письмо или PDF) как независимый датчик, регистрирующий утверждение о реальности. Модуль извлекает структурированные утверждения—кто действовал, что произошло и когда—из каждого документа. Затем он перекрёстно сверяет эти утверждения с помощью детерминистской целочисленной арифметики (например, точные временные метки Unix и фиксированные коды категорий таксономии) для выявления противоречий. Злоумышленник может идеально подделать один документ, но поддерживать логическую согласованность между несколькими независимыми документами статистически и вычислительно сложно. Данный модуль автоматизирует эту проверку согласованности без использования приближений с плавающей запятой.

#### Ключевые концепции

| Концепция | Роль в модуле | Научная аналогия |
|---|---|---|
| **Межартефактный резонанс** | Измеряет, рассказывают ли отдельные части доказательств одну и ту же историю. | Перекрёстная проверка между несколькими приборами, измеряющими одну переменную. |
| **Утверждение артефакта (ArtifactClaim)** | Структурированное утверждение, извлечённое из документа (дата, отправитель, тема). | Отдельное показание датчика с метаданными. |
| **Семантический конфликт (SemanticConflict)** | Выявленное противоречие между двумя или более утверждениями (временное, тематическое или по субъекту). | Аномальное значение или расхождение приборов. |
| **Анализ резонанса (ResonanceAnalysis)** | Итоговый детерминистский отчёт, содержащий все резонансы и конфликты. | Сводный лабораторный отчёт по нескольким приборам. |
| **ТАКСОНОМИЯ ТЕМ (TOPIC_TAXONOMY)** | Контролируемый словарь, сопоставляющий каждую возможную тему с уникальным целочисленным кодом. | Эталонная калибровочная таблица с дискретными индексами. |
| **ГЛАГОЛЫ ВЛОЖЕНИЙ (ATTACHMENT_VERBS)** | Лексический индекс глаголов действия, семантически связывающих письмо с вложениями. | Протокольный словарь допустимых терминов сопряжения. |

#### Глоссарий

| Термин | Определение |
|---|---|
| **Семантическая когерентность** | Свойство множества документов согласовываться по смыслу, временным рамкам и предмету. |
| **Детерминистская целочисленная арифметика** | Математические операции, выполняемые исключительно с целыми числами, гарантирующие, что идентичные входные данные всегда дают идентичный результат, без ошибок округления. |
| **Цифровой артефакт (криминалистический)** | Любой цифровой объект, подвергаемый исследованию (письмо, PDF, журнал). |
| **Временное несоответствие** | Конфликт, при котором два источника утверждают несовместимые даты или время одного и того же события. |

#### 【Научное примечание】
В основе фреймворка лежит терминология, восходящая к **Пирсу** (семиотика: логика знаков), **Эко** (культурная кодировка и overcoding) и **Грайсу** (конверсациональные максимы: ожидания правдивости, релевантности и ясности). Эти термины не являются мистическими конструктами; они функционируют как формальные детерминистские модели коммуникации. Воспринимайте их как лабораторные приборы: Пирс задаёт грамматику декодирования знаков (кто отправил что), Эко предоставляет категориальную таксономию (к какой области относится событие), а Грайс формулирует логические аксиомы, делающие обман обнаружимым (почему нерелевантное или противоречивое утверждение аномально). Когда два цифровых артефакта дают несовместимые показания, модуль регистрирует **расхождение датчиков**—а не сверхъестественную интуицию—и помечает его для проверки исследователем. Все сравнения выполняются с помощью детерминистской целочисленной арифметики, а не вероятностного оценивания.

---

### 中文

**模块路径：** `vigia/tools/cross_artifact_resonance.py`  
**全称：** 跨取证工件共振分析器

#### 本模块是什么？
本模块执行多源取证验证。用科学语言来说，它将每一份数字文档（如电子邮件或 PDF）视为独立记录现实陈述的传感器。模块从每份文档中提取结构化断言——谁实施了行为、发生了什么、何时发生——然后使用确定性整数运算（例如精确的 Unix 时间戳和固定类别分类码）对这些断言进行交叉比对，以发现矛盾。攻击者可以完美地伪造单份文档，但在多份独立文档之间维持逻辑一致性在统计学和计算上都是困难的。本模块自动化地完成这一一致性检验，且不使用浮点近似。

#### 关键概念

| 概念 | 模块中的角色 | 科学类比 |
|---|---|---|
| **跨取证工件共振** | 衡量多份证据是否讲述同一事实。 | 多台仪器测量同一变量时的交叉验证。 |
| **取证工件断言 (ArtifactClaim)** | 从单份文档提取的结构化陈述（日期、发件人、主题）。 | 带元数据的单次传感器读数。 |
| **语义冲突 (SemanticConflict)** | 在两个或多个断言之间检测到的矛盾（时序、主题或行为者错配）。 | 传感器异常值或仪器间分歧。 |
| **共振分析结果 (ResonanceAnalysis)** | 列出所有共振与冲突的确定性最终报告。 | 多台仪器出具的合并实验报告。 |
| **主题分类体系 (TOPIC_TAXONOMY)** | 受控词表，将每个可能的主题映射为唯一整数编码。 | 带有离散索引的参考校准表。 |
| **附件动词索引 (ATTACHMENT_VERBS)** | 动作词汇表，用于在语义上将邮件与其附件关联。 | 定义有效耦合术语的协议词典。 |

#### 术语表

| 术语 | 定义 |
|---|---|
| **语义连贯性** | 多份文档在含义、时间范围和主题内容上达成一致的特性。 |
| **确定性整数运算** | 仅使用整数进行的数学运算，确保相同输入始终产生相同输出，不存在舍入误差。 |
| **取证工件** | 任何接受调查的数字对象（邮件、PDF、日志文件）。 |
| **时序错配** | 两个来源对同一事件主张不兼容的日期或时间而产生的冲突。 |

#### 【科学说明】
本框架使用的术语源自**皮尔斯**（符号学：符号的逻辑）、**艾柯**（文化编码与超编码）与**格赖斯**（会话准则：对真实性、相关性与清晰性的期望）。这些术语并非神秘主义构造，而是形式化的、确定性的交际模型。请将它们理解为实验室仪器：皮尔斯提供了解码符号的语法（谁发送了什么），艾柯提供了范畴分类体系（事件属于哪个领域），格赖斯则提供了使欺骗可检测的逻辑公理（为何一项不相关或自相矛盾的陈述是异常的）。当两份取证工件产生不兼容的读数时，模块记录的是**传感器 discrepancy**——而非超自然直觉——并将其标记以供调查人员复核。所有比较均通过确定性整数运算完成，而非概率评分。这里的任何语义不一致都表现为**逻辑断裂**，是可重复检测的客观现象，而非文本解读上的神秘感应。


Also need to check: "逻辑断裂 (not 裂缝)". I used 逻辑断裂 in the note. I didn't use 裂缝. Good.



"格赖斯 (not Grice)". Used 格赖斯. Good.










- 跨取证工件共振分析器 - good.
- 本模块是什么？ - good.
- 独立记录现实陈述的传感器 - good.
- 结构化断言 - good.
- 确定性整数运算 - good.
- Unix 时间戳 - acceptable technical term.
- 固定类别分类码 - good.
- 时序错配 - good (instead of temporal mismatch with 裂缝).
- 逻辑断裂 - included.
- 非概率评分 - good.

"When two forensic artifacts produce incompatible readings, the module records a **sensor discrepancy**" -> "当两份取证工件产生不兼容的读数时，模块记录的是**传感器差异**——而非超自然直觉——并将其标记以供调查人员复核。"

Also check the English scientific note: "sensor discrepancy" is fine.





One final check: The user wants "A 【科学说明】/【Scientific Note】 box explaining that Peirce/Eco/Grice terminology is NOT mysticism — use the sensor analogy". The heading should be exactly that? Or should it be 【Scientific Note】 in English, etc.? The user wrote "A 【科学说明】/【Scientific Note】 box". I can use 【Scientific Note】 in EN, 【Nota Científica】 in ES, 【Научное примечание】 in RU, and 【科学说明】 in ZH. That satisfies the bilingual bracket style.




Revised Key Concepts table (EN):

| Concept | Role in the Module | Scientific Analogy |
|---|---|---|
| **Cross-Artifact Resonance** | Degree to which separate evidence units agree on facts, topics, and timelines. | Cross-validation between multiple instruments measuring the same variable. |
| **ArtifactClaim** | Structured assertion extracted from one document (e.g., date, sender, topic). | A single sensor reading with metadata. |
| **SemanticConflict** | Contradiction between two or more claims (temporal, topical, or actor mismatch). | A sensor outlier or instrument disagreement. |
| **ResonanceAnalysis** | Final deterministic report listing all resonances and conflicts. | Consolidated lab report from multiple instruments. |
| **CrossArtifactResonanceAnalyzer** | Core engine that executes the extraction and comparison workflow. | Automated control system coordinating an array of sensors. |
| **TOPIC_TAXONOMY** | Controlled vocabulary mapping every topic to a unique integer code. | Reference calibration table with discrete indices. |
| **ATTACHMENT_VERBS** | Lexical index of action words semantically linking an email to its attachments. | Protocol dictionary defining valid coupling terms. |

Similarly for other languages.


Add a small section "Analysis Protocol" or include in "What Is This Module?" I think the table and glossary are enough, but to be thorough, I can mention it in the plain language explanation.

"...The module accepts a collection of artifacts—each labeled by type, such as email or PDF—and executes a comparison protocol (`analyze`). It cross-references these assertions..."



Alright, let's write the final document.




---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
