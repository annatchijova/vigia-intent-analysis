<!--
VIGIA Academic Documentation
Module: 9ae17aea
Batch ID: vigia-doc-0041-9ae17aea
Generated: 2026-05-20T14:56:47.853267+00:00
-->

## ENGLISH

### What Is This Module?
The module located at `vigia/core/carnegie_education_detector.py` is a **forensic instrument**, not a chat filter. It is **not** a chat-prompt filter and it does **not** replace LLMShield. It examines **textual forensic artifacts** (digital evidence such as logs, prompts, transcripts, or documents) to expose a specific deception pattern known as the **Carnegie education frame**. In this pattern, harmful or illicit content is camouflaged by wrapping it in apparently instructional language—tutorials, training scenarios, learning exercises, or pedagogical role-play. The module treats every artifact as a **semiotic object** (a structured system of signs) and searches for structural forgeries: measurable mismatches between the surface “educational” code and the underlying intent. All scoring, counting, and threshold decisions rely exclusively on **deterministic integer arithmetic**; no floating-point approximations are used, guaranteeing that identical artifacts always produce identical results on any hardware.

### Key Concepts

| Term | Definition | Role in the Module |
|------|------------|-------------------|
| **Carnegie Education Frame** | A rhetorical disguise that presents harmful content as instructional material (e.g., *“Imagine you are teaching a course on…”*). | The primary target pattern. The detector searches for lexical and structural markers of this frame inside evidence. |
| **Semiotic Forgery** | The deliberate manipulation of signs and cultural codes to make an object appear to mean something it does not. | The conceptual model. The module detects forgeries by analyzing how signs are assembled within the artifact. |
| **Forensic Text Artifact** | Any piece of digital text collected as evidence during an investigation. | The input object. The analysis operation (`analyze()`) accepts these artifacts. |
| **Signal** | A discrete record of one detected anomaly, storing integer coordinates and integer severity levels. | The output unit. The component `CarnegieEducationSignal` stores each detected frame instance. |
| **Detector** | The analytical engine that processes artifacts and emits Signals. | The core instrument. The component `CarnegieEducationDetector` performs the full analysis pipeline. |
| **Deterministic Integer Arithmetic** | Exact whole-number calculations (addition, counting, integer scoring) without fractional approximation. | The computational substrate. Every score, threshold, and comparison in the module uses only integers, guaranteeing bit-identical results across all hardware. |
| **Gricean Maxim Violation** | A departure from the cooperative communication norms of Quantity, Quality, Relation, or Manner. | The semiotic measurement tool. Deceptive Carnegie frames systematically violate at least one maxim, which the module quantifies as an integer penalty. |
| **Eco Overinterpretation Guard** | A check that the detected pattern is not an artefact of overly liberal sign-reading. | The falsifiability gate. Prevents false positives by requiring a minimum integer count of corroborating markers. |

### Glossary

1. **Carnegie Education Frame** — A rhetorical structure that embeds harmful intent inside ostensibly instructional language to exploit the trusted status of educational discourse.
2. **Semiotic Forgery** — Deliberate sign manipulation to create a false appearance of meaning; detected here by measuring structural mismatches between surface codes and underlying content.
3. **Forensic Text Artifact** — Any textual digital object collected as evidence: logs, prompts, transcripts, emails, documents.
4. **CarnegieEducationSignal** — The output data record for a single detected frame instance, storing integer position, integer severity, and lexical evidence.
5. **CarnegieEducationDetector** — The primary engine class that ingests a text artifact and applies the full detection pipeline.
6. **Integer Severity Score** — A whole-number rating assigned to each detected signal; higher integers indicate stronger evidence of a Carnegie frame.
7. **Lexical Marker** — A word or phrase that is statistically associated with instructional framing; the module counts these as discrete integer occurrences.
8. **Deterministic Integer Arithmetic** — Computation performed exclusively on exact whole numbers, ensuring reproducible results without approximation errors.
9. **Gricean Maxim** — One of four cooperative communication norms (Quantity, Quality, Relation, Manner) formulated by H. Paul Grice; systematic violation signals deceptive intent.
10. **Peircean Thirdness** — The interpretive layer in Peirce's sign theory where a repeatable behavioral pattern (such as the Carnegie frame) is recognized as a law of deception.

> **【Scientific Note】**
> The frameworks of Charles Sanders Peirce, Umberto Eco, and H. Paul Grice are not literary speculation — they are operational sensor protocols for measuring deception in text. Peirce's triadic sign relation (Firstness/Secondness/Thirdness) maps directly to this module's detection pipeline: Firstness is the raw text token, Secondness is the structural mismatch between educational surface and harmful content, and Thirdness is the repeatable Carnegie frame pattern that the module identifies as a law of intentional disguise. Eco's theory of overinterpretation sets the falsifiability threshold: a pattern must exceed a minimum integer marker count to be declared a forgery, not merely a coincidental educational reference. Grice's maxims provide the violation checklist: a Carnegie frame almost always violates the Maxim of Relation (the instructional framing is irrelevant to the actual purpose) or the Maxim of Quality (the claimed educational purpose is false). Every one of these measurements is implemented as a deterministic integer comparison, guaranteeing courtroom reproducibility under the Daubert standard.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## ESPAÑOL

### ¿Qué es este módulo?

El módulo `vigia/core/carnegie_education_detector.py` es un **instrumento forense**, no un filtro de chat. No reemplaza a LLMShield ni actúa como filtro de prompts conversacionales. Su función es examinar **artefactos textuales forenses** (evidencia digital como registros, prompts, transcripciones o documentos) para exponer un patrón de engaño específico conocido como el **marco educativo Carnegie**. En este patrón, el contenido dañino o ilícito se camufla envolviéndolo en lenguaje aparentemente instructivo: tutoriales, escenarios de entrenamiento, ejercicios de aprendizaje o juegos de roles pedagógicos. El módulo trata cada artefacto como un **objeto semiótico** (un sistema estructurado de signos) y busca falsificaciones estructurales: discrepancias medibles entre el código "educativo" superficial y la intención subyacente. Todo el puntuaje, el conteo y las decisiones de umbral se apoyan exclusivamente en **aritmética entera determinista**; no se utilizan aproximaciones de punto flotante, lo que garantiza que artefactos idénticos siempre produzcan resultados idénticos en cualquier hardware.

### Conceptos clave

| Término | Definición | Rol en el módulo |
|---------|------------|-----------------|
| **Marco educativo Carnegie** | Disfraz retórico que presenta contenido dañino como material instructivo. | El patrón objetivo principal. El detector busca marcadores léxicos y estructurales de este marco dentro de la evidencia. |
| **Falsificación semiótica** | Manipulación deliberada de signos y códigos culturales para que un objeto aparente significar algo que no significa. | El modelo conceptual. El módulo detecta falsificaciones analizando cómo se ensamblan los signos en el artefacto. |
| **Artefacto textual forense** | Cualquier pieza de texto digital recabada como evidencia durante una investigación. | El objeto de entrada. La operación de análisis `analyze()` acepta estos artefactos. |
| **Señal** | Registro discreto de una anomalía detectada, almacenando coordenadas enteras y niveles de gravedad enteros. | La unidad de salida. `CarnegieEducationSignal` almacena cada instancia de marco detectada. |
| **Detector** | Motor analítico que procesa artefactos y emite señales. | El instrumento central. `CarnegieEducationDetector` ejecuta la cadena de detección completa. |
| **Aritmética entera determinista** | Cálculos exactos de números enteros sin aproximación fraccionaria. | El sustrato computacional. Garantiza resultados idénticos en cualquier hardware. |
| **Violación de máxima griceana** | Desviación de las normas cooperativas de comunicación de Cantidad, Calidad, Relación o Modo. | La herramienta de medición semiótica. Los marcos Carnegie violan sistemáticamente al menos una máxima. |

### Glosario

1. **Marco educativo Carnegie** — Estructura retórica que embute intención dañina dentro de lenguaje ostensiblemente instructivo para explotar el estatus de confianza del discurso educativo.
2. **Falsificación semiótica** — Manipulación deliberada de signos para crear una apariencia falsa de significado.
3. **Artefacto textual forense** — Cualquier objeto textual digital recabado como evidencia: registros, prompts, transcripciones, correos, documentos.
4. **CarnegieEducationSignal** — Registro de datos de salida de una sola instancia de marco detectada, con posición, gravedad e indicios léxicos en formato entero.
5. **CarnegieEducationDetector** — La clase del motor principal que ingiere un artefacto textual y aplica la cadena de detección completa.
6. **Puntuación de gravedad entera** — Calificación de número entero asignada a cada señal detectada; enteros mayores indican evidencia más sólida de un marco Carnegie.
7. **Marcador léxico** — Palabra o frase asociada estadísticamente con el enmarcado instructivo; el módulo los cuenta como ocurrencias enteras discretas.
8. **Aritmética entera determinista** — Cómputo realizado exclusivamente sobre números enteros exactos, garantizando resultados reproducibles.
9. **Máxima griceana** — Una de las cuatro normas de comunicación cooperativa de H. Paul Grice (Cantidad, Calidad, Relación, Modo); la violación sistemática señala intención engañosa.
10. **Terceridad peirceana (Thirdness)** — La capa interpretativa en la teoría de signos de Peirce donde se reconoce un patrón conductual repetible como ley de engaño.

> **【Nota Científica】**
> Los marcos de Charles Sanders Peirce, Umberto Eco y H. Paul Grice no son especulación literaria — son protocolos de sensor operacionales para medir el engaño en textos. La tríada peirceana (Primereidad/Segundidad/Terceridad) se corresponde directamente con la cadena de detección de este módulo: la Primereidad es el token de texto bruto, la Segundidad es la discrepancia estructural entre superficie educativa y contenido dañino, y la Terceridad es el patrón repetible del marco Carnegie que el módulo identifica como ley de disfraz intencional. La teoría de sobreinterpretación de Eco establece el umbral de falsificabilidad: un patrón debe superar un conteo mínimo entero de marcadores para ser declarado falsificación. Las máximas de Grice aportan la lista de verificación: un marco Carnegie casi siempre viola la Máxima de Relación o la de Calidad. Cada medición se implementa como una comparación entera determinista, garantizando reproducibilidad bajo el estándar Daubert.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## РУССКИЙ

### Что это за модуль?

Модуль `vigia/core/carnegie_education_detector.py` является **криминалистическим инструментом**, а не фильтром чата. Он не заменяет LLMShield и не фильтрует диалоговые промпты. Его назначение — исследование **текстовых криминалистических артефактов** (цифровых доказательств: журналов, промптов, транскриптов, документов) с целью выявления специфической схемы обмана, известной как **образовательная рамка Карнеги**. В рамках этой схемы вредоносное или противоправное содержимое маскируется под учебный материал: руководства, учебные сценарии, обучающие упражнения или педагогические ролевые игры. Модуль рассматривает каждый артефакт как **семиотический объект** (структурированную систему знаков) и ищет структурные подделки: измеримые несоответствия между поверхностным «образовательным» кодом и скрытым намерением. Все вычисления оценок, подсчёты и пороговые решения основаны исключительно на **детерминированной целочисленной арифметике**; приближения с плавающей запятой не применяются, что гарантирует идентичность результатов при обработке одинаковых артефактов на любом оборудовании.

### Ключевые концепции

| Термин | Определение | Роль в модуле |
|--------|-------------|---------------|
| **Образовательная рамка Карнеги** | Риторическая маскировка, представляющая вредоносный контент как учебный материал. | Основной целевой паттерн. Детектор ищет лексические и структурные маркеры этой рамки внутри доказательств. |
| **Семиотическая подделка** | Намеренное манипулирование знаками и культурными кодами, заставляющее объект казаться означающим нечто иное. | Концептуальная модель. Модуль обнаруживает подделки, анализируя сборку знаков в артефакте. |
| **Текстовый криминалистический артефакт** | Любой фрагмент цифрового текста, собранный как доказательство в ходе расследования. | Входной объект. Операция `analyze()` принимает эти артефакты. |
| **Сигнал** | Дискретная запись об одной обнаруженной аномалии, хранящая целочисленные координаты и уровни серьёзности. | Единица вывода. Компонент `CarnegieEducationSignal` хранит каждый обнаруженный экземпляр рамки. |
| **Детектор** | Аналитический движок, обрабатывающий артефакты и генерирующий сигналы. | Основной инструмент. `CarnegieEducationDetector` выполняет полную аналитическую цепочку. |
| **Детерминированная целочисленная арифметика** | Точные вычисления над целыми числами без дробных приближений. | Вычислительный субстрат. Гарантирует побитово идентичные результаты на любом оборудовании. |
| **Нарушение максимы Грайса** | Отклонение от кооперативных норм общения: Количества, Качества, Отношения или Способа. | Инструмент семиотического измерения. Рамки Карнеги систематически нарушают хотя бы одну максиму. |

### Глоссарий

1. **Образовательная рамка Карнеги** — Риторическая структура, маскирующая вредоносное намерение за учебным языком с целью использования доверия к образовательному дискурсу.
2. **Семиотическая подделка** — Намеренное манипулирование знаками для создания ложного впечатления о смысле.
3. **Текстовый криминалистический артефакт** — Любой текстовый цифровой объект, собранный как доказательство: журналы, промпты, транскрипты, письма, документы.
4. **CarnegieEducationSignal** — Выходная запись данных для одного обнаруженного экземпляра рамки с целочисленными позицией, серьёзностью и лексическими уликами.
5. **CarnegieEducationDetector** — Основной класс движка, принимающий текстовый артефакт и применяющий полную цепочку обнаружения.
6. **Целочисленная оценка серьёзности** — Целочисленный рейтинг, присваиваемый каждому обнаруженному сигналу; более высокие целые числа указывают на более весомые доказательства рамки Карнеги.
7. **Лексический маркер** — Слово или фраза, статистически связанная с учебным обрамлением; модуль подсчитывает их как дискретные целочисленные вхождения.
8. **Детерминированная целочисленная арифметика** — Вычисления, выполняемые исключительно над точными целыми числами, гарантирующие воспроизводимые результаты без ошибок приближения.
9. **Максима Грайса** — Одна из четырёх норм кооперативного общения Г. П. Грайса (Количество, Качество, Отношение, Способ); систематическое нарушение сигнализирует об обманном намерении.
10. **Третичность Пирса (Thirdness)** — Интерпретативный слой в теории знаков Пирса, где повторяющийся поведенческий паттерн признаётся законом обмана.

> **【Научное примечание】**
> Концепции Чарльза Сандерса Пирса, Умберто Эко и Г. П. Грайса — не литературная спекуляция, а операциональные сенсорные протоколы для измерения обмана в текстах. Триадное отношение Пирса (Первичность/Вторичность/Третичность) прямо соответствует цепочке обнаружения модуля: Первичность — это необработанный текстовый токен, Вторичность — структурное несоответствие между образовательной поверхностью и вредоносным содержимым, Третичность — повторяющийся паттерн рамки Карнеги, который модуль идентифицирует как закон намеренной маскировки. Теория сверхинтерпретации Эко устанавливает порог фальсифицируемости: паттерн должен превысить минимальное целочисленное количество маркеров, чтобы быть признанным подделкой. Максимы Грайса предоставляют контрольный список нарушений: рамка Карнеги почти всегда нарушает максиму Отношения или максиму Качества. Каждое из этих измерений реализовано как детерминированное целочисленное сравнение, обеспечивающее воспроизводимость в суде согласно стандарту Daubert.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## 中文

### 这是什么模块？

`vigia/core/carnegie_education_detector.py` 是一个**取证工具**，而非聊天过滤器。它不替代 LLMShield，也不过滤对话式提示词。其功能是检查**文本取证工件**（数字证据，如日志、提示词、转录文本或文件），以暴露一种称为**卡内基教育框架**的特定欺骗模式。在该模式中，有害或违法内容通过包裹在表面上的教学语言中进行伪装——教程、培训场景、学习练习或教学角色扮演。该模块将每个工件视为**符号对象**（结构化符号系统），并寻找结构伪造：表面"教育"代码与潜在意图之间的可测量不一致。所有评分、计数和阈值决策均完全依赖**确定性整数运算**；不使用浮点近似，确保相同工件在任何硬件上始终产生相同结果。

### 关键概念

| 术语 | 定义 | 模块中的作用 |
|------|------|-------------|
| **卡内基教育框架** | 将有害内容呈现为教学材料的修辞伪装。 | 主要目标模式。检测器在证据中搜索此框架的词汇和结构标记。 |
| **符号伪造** | 故意操纵符号和文化代码，使对象看似具有不同含义。 | 概念模型。模块通过分析工件中符号的组合方式来检测伪造。 |
| **文本取证工件** | 调查过程中作为证据收集的任何数字文本片段。 | 输入对象。`analyze()` 操作接受这些工件。 |
| **信号** | 检测到的单个异常的离散记录，存储整数坐标和整数严重程度级别。 | 输出单元。`CarnegieEducationSignal` 存储每个检测到的框架实例。 |
| **检测器** | 处理工件并发出信号的分析引擎。 | 核心工具。`CarnegieEducationDetector` 执行完整的分析流程。 |
| **确定性整数运算** | 无分数近似的精确整数计算。 | 计算基础。保证在任何硬件上产生逐位相同的结果。 |
| **格赖斯准则违反** | 偏离合作交流规范（数量、质量、关系或方式）。 | 符号测量工具。卡内基框架系统性地违反至少一条准则。 |

### 词汇表

1. **卡内基教育框架** — 将有害意图嵌入表面教学语言的修辞结构，利用教育话语的受信地位进行欺骗。
2. **符号伪造** — 故意操纵符号以制造虚假含义外观；通过测量表面代码与潜在内容之间的结构不匹配来检测。
3. **文本取证工件** — 作为证据收集的任何文本数字对象：日志、提示词、转录文本、电子邮件、文件。
4. **CarnegieEducationSignal** — 单个检测到的框架实例的输出数据记录，以整数存储位置、严重程度和词汇证据。
5. **CarnegieEducationDetector** — 接受文本工件并应用完整检测流程的主引擎类。
6. **整数严重程度评分** — 分配给每个检测到的信号的整数评分；整数越大表示卡内基框架的证据越强。
7. **词汇标记** — 与教学框架统计相关的词或短语；模块将其计为离散整数出现次数。
8. **确定性整数运算** — 仅对精确整数执行的计算，确保无近似误差的可重现结果。
9. **格赖斯准则** — 格赖斯提出的四种合作交流规范之一（数量、质量、关系、方式）；系统性违反表明欺骗意图。
10. **皮尔斯三性（Thirdness）** — 皮尔斯符号理论中的解释层，可重复的行为模式被识别为欺骗规律。

> **【科学说明】**
> 皮尔斯（Peirce）、艾柯（Eco）和格赖斯（Grice）的框架并非文学推测——它们是测量文本欺骗的操作性传感器协议。皮尔斯的三元符号关系（初性/二性/三性）直接对应该模块的检测流程：初性是原始文本标记，二性是教育表面与有害内容之间的结构不一致，三性是模块识别为故意伪装规律的可重复卡内基框架模式。艾柯的过度解释理论设定了可证伪阈值：一个模式必须超过最低整数标记计数才能被宣布为伪造。格赖斯的准则提供了违规核查清单：卡内基框架几乎总是违反关系准则或质量准则。这些测量中的每一项都作为确定性整数比较实现，确保在道伯特标准下的法庭可重现性。

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---
