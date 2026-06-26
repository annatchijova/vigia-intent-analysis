<!--
VIGIA Academic Documentation
Module: aa4e03f6
Batch ID: vigia-doc-0052-aa4e03f6
Generated: 2026-05-20T14:56:47.855668+00:00
-->

---

## ENGLISH

### What Is This Module?
`vigia/core/explainable_governance.py` is a **deterministic forensic reasoning engine**. Its purpose is to convert raw digital findings—called forensic artifacts—into structured, human-readable governance reports. The module operates entirely through discrete logic. Every conclusion is produced via **deterministic integer arithmetic**: identical inputs always yield identical outputs, with no approximation, rounding, or fractional drift. It employs formal semiotic frameworks (Peirce, Eco, Grice) as classification layers. These are not philosophical opinions; they function like calibrated sensors that translate evidence traces into categorical integer states.

### Key Concepts

| Component | Scientific Role | Deterministic Behavior |
|-----------|----------------|------------------------|
| `ExplanationEngine` | Core processing unit that ingests normalized forensic artifacts and assigns categorical states. | Uses only integer-encoded rule sets; output is reproducible. |
| `generate_explanation()` | Procedure that maps a set of artifacts to a validated reason code. | Relies on integer ranking of evidence weight; no fractional weights. |
| `to_html()` | Rendering layer that converts discrete output structures into a visual markup format. | Transforms integer states into text without altering evidentiary content. |
| `dominance_key()` | Resolution function for competing hypotheses. | Applies ordinal integer comparison to establish priority. |
| `TEMPLATES` | Predefined structural schemata ensuring report consistency across analyses. | Static integer-indexed layouts. |
| `REASON_CODES` | Enumerated integer identifiers for every conclusion type. | Fixed integer map; one-to-one correspondence between state and label. |
| `CONTRADICTION_TYPES` | Discrete categories for logical conflicts detected between artifacts. | Encoded as integer enumerations; logical fractures are classified as distinct integer states. |

### Glossary

| Term | Definition |
|------|------------|
| **Forensic Artifact** | A discrete, measurable digital object extracted from a source system and normalized for analysis. |
| **Deterministic Integer Arithmetic** | A calculation paradigm using only whole numbers (integers) where identical inputs invariably produce identical outputs, eliminating stochastic drift. |
| **Semiotic Layer** | A formal analytical filter that treats data traces as signs with structured meaning, analogous to a physical sensor calibrated to a specific wavelength. | Applied after artifact extraction to classify evidence by intentionality type using discrete categorical states. |
| **Reason Code** | An integer identifier uniquely encoding one conclusion type emitted by the module. | Eliminates ambiguous natural language in audit reports; every verdict maps to a unique integer. |
| **Contradiction Type** | A discrete category for logical conflicts detected between two or more artifacts. | Encoded as enumeration integers; logical fractures are classified as distinct states enabling structured resolution. |

> **【Scientific Note】**
> The frameworks of Charles Sanders Peirce, Umberto Eco, and H. Paul Grice are not philosophical decoration — they are calibrated sensor ontologies for measuring evidentiary intentionality. In this module, Peirce's Firstness corresponds to the raw artifact feature vector; Secondness is the differential comparison that detects whether an artifact deviates from baseline expectations; Thirdness is the governance report — the repeatable, law-like pattern that explains why the deviation is forensically significant. Eco's encyclopedia is operationalized as the TEMPLATES dictionary: the shared cultural codebook mapping integer reason codes to human-readable conclusions. Grice's maxims enforce quality and relevance constraints: the module will not emit a reason code unless the supporting artifact count meets an integer-threshold quorum. Every step uses deterministic integer arithmetic, ensuring that identical artifacts always produce identical governance verdicts on any hardware — a requirement of Daubert admissibility.

### Glossary

1. **Forensic Artifact** — A discrete, measurable digital object extracted from a source system and normalized for analysis.
2. **Deterministic Integer Arithmetic** — A calculation paradigm using only whole numbers where identical inputs invariably produce identical outputs.
3. **Semiotic Layer** — A formal analytical filter that treats data traces as signs with structured meaning.
4. **Reason Code** — An integer identifier uniquely encoding one type of conclusion emitted by the module.
5. **Contradiction Type** — A discrete category for logical conflicts detected between artifacts.
6. **ExplanationEngine** — The central processing class that ingests artifacts and assigns categorical states.
7. **Logical Fracture** — A detected inconsistency between artifacts; encoded as a distinct integer state for structured resolution.
8. **Dominance Key** — An ordinal integer priority resolution function for competing hypotheses.
9. **Reproducibility** — The property ensuring identical artifacts always produce identical verdicts.
10. **Daubert Standard** — The legal criterion requiring scientific methods to be testable with known error rates.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## ESPAÑOL

### ¿Qué es este módulo?

`vigia/core/explainable_governance.py` es un **motor de razonamiento forense determinista**. Su propósito es convertir hallazgos digitales brutos —llamados artefactos forenses— en informes de gobernanza estructurados y legibles por humanos. El módulo opera enteramente mediante lógica discreta. Cada conclusión se produce a través de **aritmética entera determinista**: entradas idénticas siempre producen salidas idénticas, sin aproximación, redondeo ni deriva fraccionaria. Emplea marcos semióticos formales (Peirce, Eco, Grice) como capas de clasificación. No son opiniones filosóficas; funcionan como sensores calibrados que traducen trazas de evidencia en estados enteros categóricos.

### Conceptos clave

| Componente | Rol científico | Comportamiento determinista |
|-----------|----------------|----------------------------|
| `ExplanationEngine` | Unidad de procesamiento central que ingiere artefactos forenses normalizados y asigna estados categóricos. | Usa solo conjuntos de reglas codificadas como enteros; la salida es reproducible. |
| `generate_explanation()` | Procedimiento que mapea un conjunto de artefactos a un código de razón validado. | Se apoya en ranking entero de peso de evidencia; sin pesos fraccionarios. |
| `to_html()` | Capa de renderizado que convierte estructuras de salida discretas en formato visual. | Transforma estados enteros en texto sin alterar contenido probatorio. |
| `dominance_key()` | Función de resolución para hipótesis en competencia. | Aplica comparación ordinal entera para establecer prioridad. |
| `TEMPLATES` | Esquemas estructurales predefinidos que garantizan consistencia del informe. | Diseños indexados por enteros estáticos. |
| `REASON_CODES` | Identificadores enteros enumerados para cada tipo de conclusión. | Mapa entero fijo; correspondencia uno a uno entre estado y etiqueta. |
| `CONTRADICTION_TYPES` | Categorías discretas para conflictos lógicos detectados entre artefactos. | Codificados como enumeraciones enteras; las fracturas lógicas se clasifican como estados enteros distintos. |

> **【Nota Científica】**
> Los marcos de Charles Sanders Peirce, Umberto Eco y H. Paul Grice no son decoración filosófica — son ontologías de sensor calibradas para medir la intencionalidad probatoria. En este módulo, la Primereidad de Peirce corresponde al vector de características brutas del artefacto; la Segundidad es la comparación diferencial que detecta si un artefacto se desvía de las expectativas de referencia; la Terceridad es el informe de gobernanza — el patrón repetible y similar a una ley que explica por qué la desviación es forensemente significativa. La enciclopedia de Eco se operacionaliza como el diccionario TEMPLATES: el libro de códigos culturales compartido que mapea códigos de razón enteros a conclusiones legibles. Las máximas de Grice imponen restricciones de calidad y relevancia. Cada paso usa aritmética entera determinista, garantizando reproducibilidad bajo el estándar Daubert.

### Glosario

1. **Artefacto forense** — Un objeto digital discreto y medible extraído de un sistema fuente y normalizado para análisis.
2. **Aritmética entera determinista** — Paradigma de cálculo que usa solo números enteros donde entradas idénticas producen invariablemente salidas idénticas.
3. **Capa semiótica** — Filtro analítico formal que trata las trazas de datos como signos con significado estructurado.
4. **Código de razón** — Identificador entero que codifica de forma única un tipo de conclusión emitido por el módulo.
5. **Tipo de contradicción** — Categoría discreta para conflictos lógicos detectados entre artefactos.
6. **Motor de explicación** — La clase de procesamiento central que ingiere artefactos y asigna estados categóricos.
7. **Fractura lógica** — Inconsistencia detectada entre artefactos; codificada como estado entero distinto para resolución estructurada.
8. **Clave de dominancia** — Función de resolución de prioridad entera ordinal para hipótesis en competencia.
9. **Reproducibilidad** — Propiedad que garantiza que artefactos idénticos siempre produzcan veredictos idénticos.
10. **Estándar Daubert** — Criterio legal que exige que los métodos científicos sean comprobables y tengan tasas de error conocidas.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## РУССКИЙ

### Что это за модуль?

`vigia/core/explainable_governance.py` является **детерминированным движком криминалистического рассуждения**. Его назначение — преобразование необработанных цифровых находок — именуемых криминалистическими артефактами — в структурированные, удобочитаемые отчёты о соответствии. Модуль работает исключительно посредством дискретной логики. Каждый вывод производится с помощью **детерминированной целочисленной арифметики**: идентичные входные данные всегда дают идентичные результаты без приближений, округлений или дробного дрейфа. В качестве классификационных слоёв используются формальные семиотические концепции (Пирс, Эко, Грайс). Это не философские мнения; они функционируют как откалиброванные датчики, переводящие следы доказательств в категориальные целочисленные состояния.

### Ключевые концепции

| Компонент | Научная роль | Детерминированное поведение |
|----------|--------------|----------------------------|
| `ExplanationEngine` | Центральный блок обработки, принимающий нормализованные криминалистические артефакты. | Использует только целочисленные наборы правил; вывод воспроизводим. |
| `generate_explanation()` | Процедура, отображающая набор артефактов на валидированный код причины. | Опирается на целочисленное ранжирование весов доказательств. |
| `to_html()` | Слой рендеринга, преобразующий дискретные выходные структуры в визуальный формат. | Преобразует целочисленные состояния в текст без изменения доказательств. |
| `dominance_key()` | Функция разрешения конкурирующих гипотез. | Применяет ординальное целочисленное сравнение для установления приоритета. |
| `TEMPLATES` | Предопределённые структурные схемы, обеспечивающие последовательность отчётов. | Статические целочисленно-индексированные макеты. |
| `REASON_CODES` | Перечислимые целочисленные идентификаторы для каждого типа вывода. | Фиксированная целочисленная карта; однозначное соответствие состояния и метки. |
| `CONTRADICTION_TYPES` | Дискретные категории для логических конфликтов между артефактами. | Кодируются как целочисленные перечисления; логические разрывы — отдельные целочисленные состояния. |

> **【Научное примечание】**
> Концепции Пирса, Эко и Грайса — не философское украшение, а откалиброванные сенсорные онтологии для измерения доказательственной интенциональности. Первичность Пирса соответствует вектору необработанных признаков артефакта; Вторичность — дифференциальному сравнению, выявляющему отклонение; Третичность — отчёту о соответствии. Энциклопедия Эко операционализирована как словарь TEMPLATES. Максимы Грайса вводят пороговые ограничения качества и релевантности. Каждый шаг использует детерминированную целочисленную арифметику, гарантируя воспроизводимость согласно стандарту Daubert.

### Глоссарий

1. **Криминалистический артефакт** — Дискретный, измеримый цифровой объект, извлечённый из исходной системы и нормализованный для анализа.
2. **Детерминированная целочисленная арифметика** — Парадигма вычислений, использующая только целые числа, при которой идентичные входные данные неизменно производят идентичные результаты.
3. **Семиотический слой** — Формальный аналитический фильтр, рассматривающий следы данных как знаки со структурированным смыслом.
4. **Код причины** — Целочисленный идентификатор, однозначно кодирующий один тип вывода модуля.
5. **Тип противоречия** — Дискретная категория для логических конфликтов между артефактами.
6. **Движок объяснений** — Центральный класс обработки, принимающий артефакты и присваивающий категориальные состояния.
7. **Логический разрыв** — Обнаруженная несогласованность между артефактами; кодируется как отдельное целочисленное состояние.
8. **Ключ доминирования** — Функция ординального целочисленного разрешения приоритетов для конкурирующих гипотез.
9. **Воспроизводимость** — Свойство, гарантирующее, что идентичные артефакты всегда производят идентичные вердикты.
10. **Стандарт Daubert** — Правовой критерий, требующий проверяемости научных методов с известными частотами ошибок.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## 中文

### 这是什么模块？

`vigia/core/explainable_governance.py` 是一个**确定性取证推理引擎**。其目的是将原始数字发现——称为取证工件——转换为结构化的、人类可读的治理报告。该模块完全通过离散逻辑运作。每个结论均通过**确定性整数运算**产生：相同的输入始终产生相同的输出，无近似、舍入或分数漂移。它采用形式符号框架（皮尔斯、艾柯、格赖斯）作为分类层，功能如经过校准的传感器，将证据轨迹转换为整数类别状态。

### 关键概念

| 组件 | 科学作用 | 确定性行为 |
|------|---------|-----------|
| `ExplanationEngine` | 核心处理单元，接受规范化取证工件并分配类别状态。 | 仅使用整数编码的规则集；输出可重现。 |
| `generate_explanation()` | 将工件集合映射到经验证的原因码的程序。 | 依赖整数证据权重排名；无分数权重。 |
| `to_html()` | 将离散输出结构转换为可视标记格式的渲染层。 | 将整数状态转换为文本而不改变证据内容。 |
| `dominance_key()` | 竞争假设的解析函数。 | 应用序数整数比较以建立优先级。 |
| `TEMPLATES` | 确保分析报告一致性的预定义结构模式。 | 静态整数索引布局。 |
| `REASON_CODES` | 每种结论类型的枚举整数标识符。 | 固定整数映射；状态与标签一一对应。 |
| `CONTRADICTION_TYPES` | 工件间检测到的逻辑冲突的离散类别。 | 编码为整数枚举；逻辑断裂被分类为不同的整数状态。 |

> **【科学说明】**
> 皮尔斯（Peirce）、艾柯（Eco）和格赖斯（Grice）的框架并非哲学装饰——它们是测量证据意图性的经过校准的传感器本体论。在该模块中，皮尔斯的初性对应工件的原始特征向量；二性是检测工件是否偏离基线期望的差异比较；三性是治理报告——解释偏差为何具有取证意义的可重复、类似规律的模式。艾柯的百科全书被操作化为 TEMPLATES 字典。格赖斯的准则强制执行质量和相关性约束：除非支撑工件计数达到整数阈值法定人数，否则模块不会发出原因码。每个步骤使用确定性整数运算，确保道伯特标准下的法庭可重现性。

### 词汇表

1. **取证工件** — 从源系统提取并规范化以供分析的离散、可测量数字对象。
2. **确定性整数运算** — 仅使用整数的计算范式，相同输入必然产生相同输出。
3. **语义层** — 将数据轨迹视为具有结构化含义的符号的正式分析过滤器。
4. **原因码（Reason Code）** — 唯一编码模块发出的一种结论类型的整数标识符。
5. **矛盾类型** — 工件间检测到的逻辑冲突的离散类别。
6. **解释引擎** — 接受工件并分配类别状态的核心处理类。
7. **逻辑断裂（Logical Fracture）** — 工件间检测到的不一致；编码为不同整数状态以实现结构化解决。
8. **优势键（Dominance Key）** — 竞争假设的序数整数优先级解析函数。
9. **可重现性** — 确保相同工件始终产生相同裁决的属性。
10. **道伯特标准（Daubert Standard）** — 要求科学方法可测试且具有已知错误率的法律标准。

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---
