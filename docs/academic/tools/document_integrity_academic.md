<!--
VIGIA Academic Documentation
Module: c61c815b
Batch ID: vigia-doc-0155-c61c815b
Generated: 2026-05-20T14:56:47.877943+00:00
-->

## ENGLISH

### What Is This Module?

`vigia/tools/document_integrity.py` provides deterministic forensic utilities for compound-document examination. It performs multi-layer structural audits on PDF and DOCX containers to detect content grafting, metadata discontinuities, and object-stream tampering—as required by Case 041 ("El Documento Frankenstein") and the VIGÍA vision-analysis pipeline. The core instrument, `audit_document_integrity`, returns reproducible, bitwise-verifiable integrity reports without probabilistic approximations. Every field in the output record is typed as an exact integer or a UTF-8 string; no floating-point values enter the report.

The module integrates directly with the `ForensicBundle` output layer, sealing each integrity report with a SHA-256 anchor before it enters the chain of custody. Structural anomalies—such as author-field timestamps that predate file-creation events, or internal cross-references pointing to non-existent objects—are flagged as logical fractures with exact integer severity scores.

### Key Concepts

| Concept | Definition | Technical Role |
|---|---|---|
| **Compound document** | A file format encapsulating multiple heterogeneous data streams | PDF and DOCX are the primary targets |
| **Content grafting** | Insertion of foreign material into an authentic document structure | Principal forgery pattern in Case 041 |
| **Metadata discontinuity** | Temporal or logical inconsistency within embedded document metadata | Reveals post-hoc document manipulation |
| **Object stream** | A binary sequence storing structured document objects | The tampered layer in PDF-based forgeries |
| **Logical fracture** | A deterministic inconsistency between two verifiable document fields | Triggers an integer severity flag in the report |
| **Bitwise verification** | Exact per-bit comparison between expected and observed byte sequences | Guarantees reproducible, platform-independent findings |
| **Vision-analysis pipeline** | An automated workflow linking visual feature extraction to forensic logic | Downstream consumer of this module's output |

> **【Scientific Note】**
> Peirce's Firstness in this module is the raw byte sequence of the PDF or DOCX container. Secondness is the module's comparison of observed field values against expected structural constraints—the reaction that produces a logical fracture flag. Thirdness is the repeatable audit rule applied uniformly to every document of the same type. Eco's encyclopedia principle governs which structural patterns count as "authentic": the module's rule tables encode the shared semantic definition of a well-formed document. Grice's maxim of Quantity ensures the report contains exactly the findings that exist—no interpolated severity scores, no hedged probabilities. Exact integer arithmetic means every severity score is independently computable from the same inputs.

### Glossary

1. **Compound document** — A file format encapsulating multiple internal data streams within a single binary container.
2. **Content grafting** — Insertion of foreign material into an authentic document, producing structural inconsistencies detectable by layer-level audit.
3. **Metadata discontinuity** — A temporal or logical inconsistency within embedded document metadata, indicating post-hoc manipulation.
4. **Object stream** — A binary sequence that stores structured document objects inside a PDF or similar compound-format container.
5. **Logical fracture** — A deterministic inconsistency between two or more verifiable fields in a document record, flagged as a forensic finding.
6. **Bitwise verification** — Exact per-bit comparison ensuring that observed byte sequences match expected structural patterns without approximation.
7. **Multi-layer analysis** — Sequential inspection of a file from container headers through embedded streams to content payloads.
8. **Structural tampering** — Unauthorized modification of a document's internal architecture, typically to conceal grafted content.
9. **Vision-analysis pipeline** — The automated workflow that links visual feature extraction from document images to forensic logic and reporting.
10. **Integrity report** — A formal, SHA-256-anchored record of all structural and logical findings produced by the audit instrument.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## ESPAÑOL

### ¿Qué es este módulo?

`vigia/tools/document_integrity.py` provee utilidades forenses deterministas para el examen de documentos compuestos. Realiza auditorías estructurales multicapa en contenedores PDF y DOCX para detectar injertos de contenido, discontinuidades en metadatos y alteraciones en flujos de objetos, tal como requieren el Caso 041 ("El Documento Frankenstein") y el pipeline de análisis visual de VIGÍA. La herramienta principal, `audit_document_integrity`, devuelve informes de integridad reproducibles y verificables a nivel de bit sin aproximaciones probabilísticas. Cada campo del registro de salida se tipifica como un entero exacto o una cadena UTF-8; ningún valor de punto flotante ingresa al informe.

El módulo se integra directamente con la capa de salida `ForensicBundle`, sellando cada informe de integridad con un ancla SHA-256 antes de que ingrese a la cadena de custodia. Las anomalías estructurales —como marcas de tiempo en campos de autor que son anteriores a la creación del archivo, o referencias internas cruzadas que apuntan a objetos inexistentes— se marcan como fracturas lógicas con puntuaciones de severidad expresadas como enteros exactos.

### Conceptos Clave

| Concepto | Definición | Rol Técnico |
|---|---|---|
| **Documento compuesto** | Formato de archivo que encapsula múltiples flujos de datos heterogéneos | PDF y DOCX son los objetivos principales |
| **Injerto de contenido** | Inserción de material ajeno en una estructura documental auténtica | Patrón principal de falsificación en el Caso 041 |
| **Discontinuidad en metadatos** | Inconsistencia temporal o lógica dentro de los metadatos embebidos | Revela manipulación documental posterior a la creación |
| **Flujo de objetos** | Secuencia binaria que almacena objetos documentales estructurados | La capa alterada en las falsificaciones basadas en PDF |
| **Fractura lógica** | Inconsistencia determinista entre dos campos documentales verificables | Activa un indicador entero de severidad en el informe |
| **Verificación bit a bit** | Comparación exacta por bit entre secuencias de bytes esperadas y observadas | Garantiza hallazgos reproducibles e independientes de la plataforma |
| **Pipeline de análisis visual** | Flujo de trabajo automatizado que vincula la extracción visual con la lógica forense | Consumidor posterior de la salida de este módulo |

> **【Nota Científica】**
> La Primereidad de Peirce en este módulo es la secuencia bruta de bytes del contenedor PDF o DOCX. La Segundidad es la comparación del módulo entre los valores de campo observados y las restricciones estructurales esperadas —la reacción que produce el indicador de fractura lógica. La Terceridad es la regla de auditoría repetible aplicada uniformemente a cada documento del mismo tipo. El principio de enciclopedia de Eco rige qué patrones estructurales se consideran "auténticos": las tablas de reglas del módulo codifican la definición semántica compartida de un documento bien formado. La máxima de Cantidad de Grice garantiza que el informe contiene exactamente los hallazgos que existen: sin puntuaciones de severidad interpoladas ni probabilidades ambiguas. La aritmética entera exacta significa que cada puntuación de severidad es independientemente calculable a partir de las mismas entradas.

### Glosario

1. **Documento compuesto** — Formato de archivo que encapsula múltiples flujos de datos internos dentro de un único contenedor binario.
2. **Injerto de contenido** — Inserción de material ajeno en un documento auténtico, produciendo inconsistencias estructurales detectables mediante auditoría por capas.
3. **Discontinuidad en metadatos** — Inconsistencia temporal o lógica dentro de los metadatos embebidos del documento, indicativa de manipulación posterior.
4. **Flujo de objetos** — Secuencia binaria que almacena objetos documentales estructurados dentro de un contenedor PDF u otro formato compuesto.
5. **Fractura lógica** — Inconsistencia determinista entre dos o más campos verificables en un registro documental, marcada como hallazgo forense.
6. **Verificación bit a bit** — Comparación exacta por bit que garantiza que las secuencias de bytes observadas coincidan con los patrones estructurales esperados sin aproximación.
7. **Análisis multicapa** — Inspección secuencial de un archivo desde los encabezados del contenedor hasta los flujos embebidos y las cargas de contenido.
8. **Alteración estructural** — Modificación no autorizada de la arquitectura interna de un documento, típicamente para ocultar contenido injertado.
9. **Pipeline de análisis visual** — El flujo de trabajo automatizado que vincula la extracción de características visuales de imágenes documentales con la lógica y los informes forenses.
10. **Informe de integridad** — Registro formal, anclado con SHA-256, de todos los hallazgos estructurales y lógicos producidos por el instrumento de auditoría.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## РУССКИЙ

### Что это за модуль?

`vigia/tools/document_integrity.py` предоставляет детерминированные криминалистические утилиты для исследования составных документов. Модуль выполняет многоуровневые структурные аудиты контейнеров PDF и DOCX с целью выявления прививки контента, разрывов метаданных и фальсификации потоков объектов — как требуется в Деле 041 («Документ Франкенштейн») и конвейере визуального анализа VIGÍA. Основной инструмент, `audit_document_integrity`, возвращает воспроизводимые, побитово верифицируемые отчёты о целостности без вероятностных приближений. Каждое поле выходной записи типизировано как точное целое число или строка UTF-8; никакие значения с плавающей запятой не попадают в отчёт.

Модуль интегрируется непосредственно со слоем вывода `ForensicBundle`, запечатывая каждый отчёт о целостности якорем SHA-256 до его включения в цепочку хранения. Структурные аномалии — такие как временны́е метки в полях авторства, предшествующие дате создания файла, или внутренние перекрёстные ссылки на несуществующие объекты — фиксируются как логические разрывы с точными целочисленными оценками серьёзности.

### Ключевые концепции

| Концепция | Определение | Техническая роль |
|---|---|---|
| **Составной документ** | Формат файла, инкапсулирующий несколько гетерогенных потоков данных | PDF и DOCX — основные объекты анализа |
| **Прививка контента** | Вставка чужеродного материала в структуру подлинного документа | Главный паттерн подделки в Деле 041 |
| **Разрыв метаданных** | Временнáя или логическая несогласованность во встроенных метаданных | Выявляет постфактумную манипуляцию с документом |
| **Поток объектов** | Бинарная последовательность, хранящая структурированные объекты документа | Изменённый слой в PDF-подделках |
| **Логический разрыв** | Детерминированная несогласованность между двумя верифицируемыми полями | Активирует целочисленный индикатор серьёзности в отчёте |
| **Побитовая верификация** | Точное посимвольное сравнение ожидаемых и наблюдаемых байтовых последовательностей | Гарантирует воспроизводимые платформо-независимые выводы |
| **Конвейер визуального анализа** | Автоматизированный процесс, связывающий извлечение визуальных признаков с криминалистической логикой | Потребитель нисходящего потока данного модуля |

> **【Научное примечание】**
> Первичность Пирса в данном модуле — это необработанная байтовая последовательность контейнера PDF или DOCX. Вторичность — это сравнение модулем наблюдаемых значений полей с ожидаемыми структурными ограничениями: реакция, производящая флаг логического разрыва. Третичность — это повторяемое правило аудита, единообразно применяемое к каждому документу одного и того же типа. Принцип энциклопедии Эко определяет, какие структурные паттерны считаются «подлинными»: таблицы правил модуля кодируют разделяемое семантическое определение корректно сформированного документа. Максима Количества Грайса гарантирует, что отчёт содержит ровно те находки, которые существуют: без интерполированных оценок серьёзности и без неоднозначных вероятностей. Детерминированная целочисленная арифметика означает, что каждая оценка серьёзности независимо исчислима из тех же входных данных.

### Глоссарий

1. **Составной документ** — Формат файла, инкапсулирующий несколько внутренних потоков данных в едином бинарном контейнере.
2. **Прививка контента** — Вставка чужеродного материала в подлинный документ, порождающая структурные несоответствия, обнаруживаемые послойным аудитом.
3. **Разрыв метаданных** — Временнáя или логическая несогласованность во встроенных метаданных документа, свидетельствующая о постфактумной манипуляции.
4. **Поток объектов** — Бинарная последовательность, хранящая структурированные объекты документа внутри контейнера PDF или аналогичного составного формата.
5. **Логический разрыв** — Детерминированная несогласованность между двумя или более верифицируемыми полями записи документа, фиксируемая как криминалистическая находка.
6. **Побитовая верификация** — Точное посимвольное сравнение, обеспечивающее соответствие наблюдаемых байтовых последовательностей ожидаемым структурным паттернам без приближений.
7. **Многоуровневый анализ** — Последовательная инспекция файла от заголовков контейнера через встроенные потоки до полезной нагрузки содержимого.
8. **Структурное вмешательство** — Несанкционированное изменение внутренней архитектуры документа, как правило, с целью сокрытия привитого контента.
9. **Конвейер визуального анализа** — Автоматизированный процесс, связывающий извлечение визуальных признаков из изображений документов с криминалистической логикой и формированием отчётов.
10. **Отчёт о целостности** — Формальная, запечатанная якорем SHA-256, запись всех структурных и логических находок, произведённых инструментом аудита.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## 中文

### 这是什么模块？

`vigia/tools/document_integrity.py` 模块为复合文档检验提供确定性取证工具。该模块对 PDF 与 DOCX 容器执行多层结构审计，以检测内容嫁接、元数据不连续及对象流篡改，满足第 041 号案例（《弗兰肯斯坦文档》）与 VIGÍA 视觉分析管道之需求。核心工具 `audit_document_integrity` 生成可复现、可逐位验证的完整性报告，不依赖概率近似。输出记录的每个字段均类型化为精确整数或 UTF-8 字符串；浮点值不进入报告。

该模块直接与 `ForensicBundle` 输出层集成，在每份完整性报告进入证据链之前以 SHA-256 锚对其进行密封。结构异常——例如作者字段时间戳早于文件创建时间，或内部交叉引用指向不存在的对象——将以精确整数严重性评分标记为逻辑断裂。

### 核心概念

| 概念 | 定义 | 技术作用 |
|---|---|---|
| **复合文档** | 封装多个异构数据流的文件格式 | PDF 与 DOCX 是主要分析对象 |
| **内容嫁接** | 将外来材料插入真实文档结构 | 第 041 号案例的主要伪造模式 |
| **元数据不连续** | 嵌入文档元数据中的时间或逻辑不一致 | 揭示文档创建后的篡改行为 |
| **对象流** | 存储结构化文档对象的二进制序列 | 基于 PDF 的伪造中被篡改的层级 |
| **逻辑断裂** | 两个可验证文档字段之间的确定性不一致 | 在报告中触发整数严重性标志 |
| **逐位验证** | 预期与观察到的字节序列之间的精确逐位比较 | 保证可重现、独立于平台的发现 |
| **视觉分析管道** | 将视觉特征提取与取证逻辑连接的自动化工作流 | 本模块输出的下游消费者 |

> **【科学说明】**
> 皮尔斯的初性在本模块中是 PDF 或 DOCX 容器的原始字节序列。二性是模块将观察到的字段值与预期结构约束进行比较——产生逻辑断裂标志的反应。三性是对同类型每份文档统一应用的可重复审计规则。艾柯的百科全书原则决定哪些结构模式算作"真实"：模块的规则表编码了格式良好文档的共享语义定义。格赖斯的量的准则确保报告恰好包含存在的发现——无插值严重性评分，无模糊概率。精确整数运算意味着每个严重性评分均可从相同输入独立计算得出。

### 术语表

1. **复合文档** — 在单一二进制容器内封装多个内部数据流的文件格式。
2. **内容嫁接** — 将外来材料插入真实文档，产生通过层级审计可检测到的结构不一致。
3. **元数据不连续** — 文档嵌入元数据中的时间或逻辑不一致，表明存在事后篡改。
4. **对象流** — 在 PDF 或类似复合格式容器内存储结构化文档对象的二进制序列。
5. **逻辑断裂** — 文档记录中两个或多个可验证字段之间的确定性不一致，标记为取证发现。
6. **逐位验证** — 精确的逐位比较，确保观察到的字节序列与预期结构模式无近似地匹配。
7. **多层分析** — 从容器头部经嵌入流到内容载荷对文件进行的顺序检查。
8. **结构篡改** — 对文档内部架构的未授权修改，通常用于隐藏嫁接的内容。
9. **视觉分析管道** — 将文档图像的视觉特征提取与取证逻辑和报告相连接的自动化工作流。
10. **完整性报告** — 由审计工具生成的、以 SHA-256 锚定的所有结构与逻辑发现的正式记录。

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
