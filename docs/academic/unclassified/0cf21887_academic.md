<!--
VIGIA Academic Documentation
Module: 0cf21887
Batch ID: vigia-doc-0120-0cf21887
Generated: 2026-05-20T14:56:47.870468+00:00
-->

---

## ENGLISH

### What Is This Module?
This module is the central intake and normalization engine for the VIGÍA forensic analysis framework. Its sole purpose is to gather digital forensic cases from heterogeneous origins—narrative Markdown files, structured JSON dumps from AI agents, and legacy JSON repositories—and convert them into a single, strictly validated canonical format.

Think of it as a universal translator and quality-control gate: whatever language or shape the raw evidence arrives in, this engine ensures it leaves as a standardized, machine-readable case record with deterministic identifiers. It operates entirely on **deterministic integer arithmetic** for indexing and validation counters; no probabilistic floating-point thresholds are used to decide whether a record is accepted.

### Key Concepts

| Concept | Plain-Language Definition | Role in the Pipeline |
|---|---|---|
| Canonical Format (VIGÍA v1.0) | A fixed, universal template that every case must fit into, like a standard laboratory form. | Guarantees that downstream analytical tools can read every case without ambiguity. |
| Canonical ID | A deterministic integer-based identifier assigned to each case. | Ensures exact, reproducible referencing across the entire dataset. |
| Markdown Narrative | Human-readable text files describing synthetic forensic scenarios. | Source material written by analysts; the parser extracts structured data from prose. |
| Structured JSON | Machine-generated files (e.g., from Kimi Agent) with pre-labeled fields. | Directly mapped into the canonical format after validation. |
| Legacy JSON | Pre-existing case files stored in `data/cases/`. | Ingested and re-validated to maintain uniformity with new records. |
| Forensic Artifact | A discrete piece of digital evidence (log entry, file hash, memory dump excerpt). | The atomic unit of evidence within a case. |
| Peirce Layer | A classification of signs (Firstness, Secondness, Thirdness) describing how an artifact carries meaning. | Provides a semiotic scaffold for anomaly detection. |
| Devil's Advocate | A pre-computed counter-argument template challenging the expected verdict. | Stress-tests the case against cognitive bias. |
| Abstention Risk | A deterministic flag indicating whether the case lacks sufficient evidence for a verdict. | Prevents over-conclusion. |
| Index File (`_index.json`) | A master lookup table listing every consolidated case by its canonical ID. | Enables O(1) retrieval without scanning the entire archive. |

### Glossary

1. **Canonical Format** — The authoritative, single version of a case record. All fields are mandatory and typed.
2. **Deterministic Integer Arithmetic** — Calculations performed with whole numbers where the same input always yields exactly the same output, free from rounding errors.
3. **Forensic Artifact** — Any digital object or trace relevant to an investigation (e.g., network packet, registry key).
4. **Legacy Data** — Previously collected information that may use older schema versions.
5. **Markdown** — A lightweight markup language for formatting plain text.
6. **Normalization** — The process of converting diverse inputs into a common, standard structure.
7. **Semiotics** — The study of signs and symbols; here, used to model how forensic evidence signifies malicious activity.
8. **Synthetic Case** — A fictional but realistic scenario generated for training or testing.
9. **VERDICT_RE / SIGNALS_RE** — Deterministic regular-expression patterns used to extract specific fields from raw text without numerical approximation.
10. **Peirce Triad** — The three logical layers (Firstness, Secondness, Thirdness) through which every forensic sign is analyzed.

> **【Scientific Note】**
> The terminology of Peirce (Firstness, Secondness, Thirdness), Umberto Eco, and Grice is sometimes mistaken for metaphysical speculation. In VIGÍA, these terms function as **sensor ontologies**—conceptual calibrations analogous to how a spectrometer assigns peaks to wavelengths. Firstness is the raw signal; Secondness is its structural deviation from a known baseline; Thirdness is the repeatable behavioral law that explains why the deviation exists.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## ESPAÑOL

### ¿Qué es este módulo?
Este módulo es el motor central de ingesta y normalización del marco de análisis forense VIGÍA. Su único propósito es recopilar casos forenses digitales de orígenes heterogéneos—archivos Markdown narrativos, volcados JSON estructurados de agentes de IA y repositorios JSON heredados—y convertirlos en un único formato canónico estrictamente validado.

Puede concebirse como un traductor universal y puerta de control de calidad: independientemente del lenguaje o forma en que lleguen los datos en bruto, este motor garantiza que salgan como un registro de caso estandarizado y legible por máquina con identificadores deterministas. Opera enteramente con **aritmética entera determinista** para indexación y contadores de validación; no se utilizan umbrales probabilísticos para decidir si un registro se acepta.

### Conceptos clave

| Concepto | Definición | Rol técnico |
|---|---|---|
| Formato Canónico (VIGÍA v1.0) | Plantilla fija y universal que todo caso debe adoptar, como un formulario de laboratorio estándar. | Garantiza que las herramientas analíticas posteriores puedan leer cada caso sin ambigüedad. |
| ID Canónico | Identificador de base entera determinista asignado a cada caso. | Asegura referencias exactas y reproducibles en todo el conjunto de datos. |
| Narrativa Markdown | Archivos de texto legibles por humanos que describen escenarios forenses sintéticos. | Material fuente escrito por analistas; el analizador extrae datos estructurados de la prosa. |
| JSON Estructurado | Archivos generados por máquina (p. ej., del Agente Kimi) con campos preetiquetados. | Mapeado directamente al formato canónico tras validación. |
| JSON Heredado | Archivos de casos preexistentes almacenados en `data/cases/`. | Ingeridos y revalidados para mantener uniformidad con nuevos registros. |
| Artefacto Forense | Pieza discreta de evidencia digital (entrada de registro, hash de archivo, fragmento de volcado de memoria). | Unidad atómica de evidencia dentro de un caso. |
| Capa Peirce | Clasificación de signos (Primeridad, Segundidad, Terceridad) que describe cómo un artefacto porta significado. | Proporciona andamiaje semiótico para la detección de anomalías. |
| Abogado del Diablo | Plantilla de contraargumento precomputada que desafía el veredicto esperado. | Pone a prueba el caso contra el sesgo cognitivo. |
| Riesgo de Abstención | Indicador determinista que señala si el caso carece de evidencia suficiente para un veredicto. | Previene la sobreconclusion. |

> **【Nota Científica】**
> La terminología de Peirce (Primeridad, Segundidad, Terceridad), Umberto Eco y Grice no es misticismo. En VIGÍA, estos términos funcionan como **ontologías de sensores**—calibraciones conceptuales análogas a cómo un espectrómetro asigna picos a longitudes de onda. La Primeridad es la señal en bruto; la Segundidad es su desviación estructural respecto a un referente conocido; la Terceridad es la ley conductual repetible que explica por qué existe la desviación.

### Glosario
1. **Formato Canónico** — Versión autoritativa y única de un registro de caso. Todos los campos son obligatorios y tipados.
2. **Aritmética Entera Determinista** — Cálculos con números enteros donde la misma entrada siempre produce exactamente la misma salida.
3. **Artefacto Forense** — Cualquier objeto o rastro digital relevante para una investigación.
4. **Datos Heredados** — Información recopilada previamente que puede utilizar versiones de esquema más antiguas.
5. **Markdown** — Lenguaje de marcado ligero para formatear texto plano.
6. **Normalización** — Proceso de convertir entradas diversas en una estructura común estándar.
7. **Semiótica** — Estudio de signos y símbolos; aquí modela cómo la evidencia forense significa actividad maliciosa.
8. **Caso Sintético** — Escenario ficticio pero realista generado para entrenamiento o pruebas.
9. **Abstención** — Veredicto que indica evidencia insuficiente para una conclusión; respuesta válida, no un fallo.
10. **Tríada de Peirce** — Las tres capas lógicas (Primeridad, Segundidad, Terceridad) a través de las cuales se analiza todo signo forense.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## РУССКИЙ

### Что это за модуль?
Данный модуль представляет собой центральный механизм приёма и нормализации данных в рамках криминалистического анализа VIGÍA. Его единственная задача — собирать цифровые криминалистические дела из разнородных источников: нарративных файлов Markdown, структурированных JSON-дампов от агентов ИИ и устаревших JSON-репозиториев — и преобразовывать их в единый строго валидированный канонический формат.

Модуль можно рассматривать как универсальный переводчик и ворота контроля качества: в каком бы виде ни поступали необработанные данные, движок гарантирует их выход в виде стандартизированной, машиночитаемой записи дела с детерминированными идентификаторами. Модуль работает исключительно на **детерминированной целочисленной арифметике** для индексирования и счётчиков валидации.

### Ключевые концепции

| Концепция | Определение | Техническая роль |
|---|---|---|
| Канонический формат (VIGÍA v1.0) | Фиксированный универсальный шаблон, которому должно соответствовать каждое дело. | Гарантирует однозначное чтение каждого дела нижестоящими инструментами. |
| Канонический ID | Детерминированный целочисленный идентификатор, присваиваемый каждому делу. | Обеспечивает точные воспроизводимые ссылки по всему набору данных. |
| Нарратив Markdown | Удобочитаемые текстовые файлы, описывающие синтетические криминалистические сценарии. | Исходный материал аналитиков; парсер извлекает структурированные данные из текста. |
| Структурированный JSON | Машинно-сгенерированные файлы с предварительно размеченными полями. | Напрямую отображается в канонический формат после валидации. |
| Устаревший JSON | Ранее существовавшие файлы дел в `data/cases/`. | Ингестируется и повторно валидируется для единообразия с новыми записями. |
| Криминалистический артефакт | Дискретный фрагмент цифровых доказательств (запись журнала, хеш файла, фрагмент дампа памяти). | Атомарная единица доказательства внутри дела. |
| Слой Пирса | Классификация знаков (Первичность, Вторичность, Третичность), описывающая, как артефакт несёт смысл. | Предоставляет семиотический каркас для обнаружения аномалий. |
| Риск воздержания | Детерминированный флаг, указывающий на недостаточность доказательств для вынесения вердикта. | Предотвращает поспешные выводы. |

> **【Научное примечание】**
> Терминология Пирса (Первичность, Вторичность, Третичность), Умберто Эко и Грайса — не мистика. В VIGÍA эти термины функционируют как **онтологии сенсоров** — концептуальные калибровки, аналогичные тому, как спектрометр соотносит пики с длинами волн. Первичность — это необработанный сигнал; Вторичность — его структурное отклонение от известного базового уровня; Третичность — повторяющийся поведенческий закон, объясняющий природу отклонения.

### Глоссарий
1. **Канонический формат** — Авторитетная единственная версия записи дела. Все поля обязательны и типизированы.
2. **Детерминированная целочисленная арифметика** — Вычисления с целыми числами, при которых одинаковые входные данные всегда дают точно такой же результат.
3. **Криминалистический артефакт** — Любой цифровой объект или след, имеющий значение для расследования.
4. **Устаревшие данные** — Ранее собранная информация, использующая более старые версии схем.
5. **Markdown** — Облегчённый язык разметки для форматирования текста.
6. **Нормализация** — Процесс преобразования разнородных входных данных в единую стандартную структуру.
7. **Семиотика** — Наука о знаках и символах; здесь моделирует, как криминалистические доказательства указывают на вредоносную активность.
8. **Синтетическое дело** — Вымышленный, но реалистичный сценарий для обучения или тестирования.
9. **Воздержание** — Вердикт, означающий недостаточность доказательств; допустимый ответ, а не сбой.
10. **Триада Пирса** — Три логических слоя (Первичность, Вторичность, Третичность) для анализа каждого криминалистического знака.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## 中文

### 这是什么模块？
本模块是 VIGÍA 取证分析框架的中央采集与规范化引擎。其唯一目标是从异构来源收集数字取证案例——包括叙事性 Markdown 文件、来自 AI 智能体的结构化 JSON 转储以及遗留 JSON 仓库——并将其转换为单一、严格验证的规范格式。

可将其视为通用翻译器与质量控制门：无论原始证据以何种语言或形态到来，该引擎均确保其以标准化、机器可读的案例记录形式输出，并附有确定性标识符。它完全依赖**精确整数运算**进行索引和验证计数；不使用概率阈值决定记录是否被接受。

### 关键概念

| 概念 | 定义 | 技术作用 |
|---|---|---|
| 规范格式（VIGÍA v1.0） | 每个案例必须符合的固定通用模板，如标准实验室表格。 | 保证下游分析工具能无歧义地读取每个案例。 |
| 规范 ID | 分配给每个案例的确定性整数标识符。 | 确保整个数据集中引用的精确性和可复现性。 |
| Markdown 叙述 | 描述合成取证场景的人类可读文本文件。 | 分析人员编写的原始材料；解析器从散文中提取结构化数据。 |
| 结构化 JSON | 带有预标记字段的机器生成文件（如来自 Kimi Agent）。 | 验证后直接映射到规范格式。 |
| 遗留 JSON | 存储于 `data/cases/` 的既有案例文件。 | 采集后重新验证以保持与新记录的一致性。 |
| 取证工件 | 离散的数字证据片段（日志条目、文件哈希、内存转储摘录）。 | 案例内证据的原子单元。 |
| 皮尔斯层 | 符号分类（第一性、第二性、第三性），描述工件如何携带意义。 | 为异常检测提供符号学脚手架。 |
| 魔鬼代言人 | 质疑预期裁决的预计算反驳模板。 | 对案例进行认知偏差压力测试。 |
| 弃权风险 | 确定性标志，指示案例是否缺乏足够证据作出裁决。 | 防止过度结论。 |

> **【科学说明】**
> 皮尔斯（第一性、第二性、第三性）、艾柯和格赖斯的术语并非神秘主义。在 VIGÍA 中，这些术语充当**传感器本体论**——类似于光谱仪将峰值分配到波长的概念校准。第一性是原始信号；第二性是其相对于已知基线的结构偏差；第三性是解释偏差存在原因的可重复行为规律。

### 词汇表
1. **规范格式** — 案例记录的权威唯一版本。所有字段均为必填且有类型约束。
2. **精确整数运算** — 使用整数进行计算，相同输入始终产生完全相同的输出。
3. **取证工件** — 与调查相关的任何数字对象或痕迹。
4. **遗留数据** — 可能使用旧版模式的既有信息。
5. **Markdown** — 用于格式化纯文本的轻量级标记语言。
6. **规范化** — 将多样化输入转换为通用标准结构的过程。
7. **符号学** — 符号与象征的研究；此处用于建模取证证据如何指示恶意活动。
8. **合成案例** — 为训练或测试生成的虚构但逼真的场景。
9. **弃权** — 表示证据不足以得出结论的裁决；有效答案，而非失败。
10. **皮尔斯三元组** — 分析每个取证符号的三个逻辑层（第一性、第二性、第三性）。

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
