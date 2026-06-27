<!--
VIGIA Academic Documentation
Module: e4d00825
Batch ID: vigia-doc-0049-e4d00825
Generated: 2026-05-20T14:56:47.855039+00:00
-->

# Module Documentation: `vigia/core/entanglement.py`

**Layer:** Capa P6 — Advanced Adversary Detection ("La Cacería de Lotes")

## ENGLISH

**What Is This Module?**

This module is the Layer P6 detection engine of the VIGÍA forensic platform. It treats document collections as physical evidence batches. Rather than reading for semantic content, it measures *linguistic entanglement*—the invisible threads that bind supposedly unrelated documents to a single forgery factory. It operates like a forensic mass spectrometer: it does not interpret human intent directly; it counts exact structural overlaps using deterministic integer arithmetic to decide whether documents share a common origin.

**Key Concepts**

| Concept | Forensic Function | Deterministic Basis |
|---|---|---|
| N-Gram Fingerprint | Countable token-sequence identifier extracted from text | Integer cardinality of exact set overlaps |
| Jaccard Similarity | Exact structural overlap between two artifacts | Rational ratio of two integers (intersection count / union count); no rounding |
| Physical Key Signature | Recurrent orthographic error trace | Integer count of identical error strings across the batch |
| Forced Variety Profile | Synthetic lexical-diversity mask | Integer frequency dispersion of vocabulary usage |
| Entanglement Report | Structured record linking each forensic artifact to shared-origin hypotheses | Aggregated integer vectors |
| CAIE Fracture | Injected anomaly descriptor for the Cross-Artifact Incongruence Engine | Boolean trigger + integer severity offset |
| Batch Analysis | Simultaneous comparison of every document in a lot | Matrix operations on integer fingerprint tallies |

**Operational Components**

| Component | Role |
|---|---|
| EntanglementEngine | Central processor that detects forgery factories via batch-wise deterministic pipelines. |
| EntanglementCAIEIntegration | Bridge translating engine outputs into CAIE-compatible logic fractures. |
| analyze_batch() | Executes complete deterministic comparison of a document lot. |
| query_cross_linked() | Reconstructs forgery networks from relational database records. |
| to_caie_fractures() | Converts findings into injectable fractures for downstream incongruence analysis. |

**Glossary**

- **Entanglement** — Non-random correlation between documents indicating a shared generative source.
- **Factory Signature** — A deterministic pattern recurrent across a batch, statistically incompatible with independent authorship.
- **Deterministic Integer Arithmetic** — Exact counting operations (addition, subtraction, comparison of whole numbers) that yield reproducible results without rounding error.
- **Cross-Linked Query** — A relational search that reconstructs entire forgery networks from database records.
- **CAIE** — Cross-Artifact Incongruence Engine; subsystem mapping contradictions across evidence types.
- **Peircean Semiotics** — Formal study of signs and interpretants, applied here as rigorous detection rules rather than literary theory.
- **Eco/Grice Filters** — Interpretive and cooperative-principle frameworks recast as algorithmic boundary conditions.

**Scientific Note**

> 【Scientific Note】
> References to Peirce, Eco, and Grice within this system are not appeals to mysticism or literary criticism. They function exactly like calibrated sensors in a physical instrument. Peirce's semiotics provides the detection lattice (what counts as a sign of forgery). Umberto Eco's interpretive models act as noise filters against over-reading. Paul Grice's cooperative maxima define the expected baseline; deviation from that baseline is measured as a discrete integer offset, not a subjective impression. When the engine reports "entanglement," it is reporting a sensor-detected structural anomaly, not a metaphysical connection.

---

## ESPAÑOL

**¿Qué es este módulo?**

Este módulo es el motor de detección de la Capa P6 de la plataforma forense VIGÍA. Trata las colecciones documentales como lotes de evidencia física. En lugar de leer para extraer significado, mide el *entrelazamiento lingüístico*: los hilos invisibles que unen documentos supuestamente independientes a una misma fábrica de falsificación. Opera como un espectrómetro de masas forense: no interpreta la intención humana directamente; cuenta superposiciones estructurales exactas mediante aritmética entera determinista para determinar si los documentos comparten un origen común.

**Conceptos Clave**

| Concepto | Función Forense | Base Determinista |
|---|---|---|
| Huella N-Gram | Identificador de secuencias contables extraído del texto | Cardinalidad entera de superposiciones exactas |
| Similitud Jaccard | Superposición estructural exacta entre dos artefactos | Razón racional de dos enteros (intersección / unión); sin redondeo |
| Firma de Teclado Físico | Rastro de errores ortográficos recurrentes | Conteo entero de cadenas de error idénticas en el lote |
| Perfil de Variedad Forzada | Máscara sintética de diversidad léxica | Dispersión de frecuencias enteras del vocabulario |
| Reporte de Entrelazamiento | Registro estructurado que vincula artefactos forenses a hipótesis de origen compartido | Vectores enteros agregados |
| Fractura CAIE | Descriptor de anomalía inyectado en el Motor de Incongruencia Cruzada de Artefactos | Bandera booleana + desplazamiento entero de severidad |
| Análisis de Lote | Comparación simultánea de todos los documentos de un lote | Operaciones matriciales sobre conteos enteros de huellas |

**Componentes Operativos**

| Componente | Rol |
|---|---|
| EntanglementEngine | Procesador central que detecta fábricas de falsificación mediante tuberías deterministas por lotes. |
| EntanglementCAIEIntegration | Puente que traduce los resultados del motor a fracturas lógicas compatibles con CAIE. |
| analyze_batch() | Ejecuta la comparación determinista completa de un lote documental. |
| query_cross_linked() | Reconstruye redes de falsificación desde registros relacionales de base de datos. |
| to_caie_fractures() | Convierte hallazgos en fracturas inyectables para análisis de incongruencia posterior. |

**Glosario**

- **Entrelazamiento** — Correlación no aleatoria entre documentos que indica una fuente generativa compartida.
- **Firma de Fábrica** — Patrón determinista recurrente en un lote, estadísticamente incompatible con autoría independiente.
- **Aritmética Entera Determinista** — Operaciones exactas de conteo (suma, resta, comparación de números enteros) que producen resultados reproducibles sin error de redondeo.
- **Consulta Cruzada Vinculada** — Búsqueda relacional que reconstruye redes completas de falsificación a partir de registros de base de datos.
- **CAIE** — Motor de Incongruencia Cruzada de Artefactos; subsistema que mapea contradicciones entre tipos de evidencia.
- **Semiótica Peirceana** — Estudio formal de signos e interpretantes, aplicado aquí como reglas rigurosas de detección, no como teoría literaria.
- **Filtros Eco/Grice** — Marcos interpretativos y de principios cooperativos recodificados como condiciones de contorno algorítmicas.

**Nota Científica**

> 【Nota Científica】
> Las referencias a Peirce, Eco y Grice en este sistema no son apelaciones al misticismo ni a la crítica literaria. Funcionan exactamente como sensores calibrados en un instrumento físico. La semiótica de Peirce provee la retícula de detección (qué cuenta como signo de falsificación). Los modelos interpretativos de Eco actúan como filtros de ruido contra la sobre-interpretación. Las máximas cooperativas de Grice definen la línea base esperada; la desviación respecto a esa línea se mide como un desplazamiento entero discreto, no como una impresión subjetiva. Cuando el motor reporta "entrelazamiento", está reportando una anomalía estructural detectada por sensor, no una conexión metafísica.

---

## РУССКИЙ

**Что это за модуль?**

Это детекционный движок уровня P6 форензической платформы VIGÍA. Он обрабатывает собрания документов как партии физических доказательств. Вместо чтения для извлечения смысла он измеряет *лингвистическую запутанность* — невидимые нити, связывающие якобы независимые документы с одной фабрикой подделок. Он работает как форензический масс-спектрометр: не интерпретирует человеческое намерение напрямую; подсчитывает точные структурные совпадения с помощью детерминированной целочисленной арифметики, чтобы определить, имеют ли документы общее происхождение.

**Ключевые Концепции**

| Концепция | Форензическая Функция | Детерминированная Основа |
|---|---|---|
| N-граммный отпечаток | Извлекаемый идентификатор счётных последовательностей из текста | Целочисленная мощность точных пересечений множеств |
| Сходство Жаккара | Точное структурное совпадение между двумя артефактами | Рациональное отношение двух целых чисел (пересечение / объединение); без округления |
| Сигнатура физической клавиатуры | Поведенческий след повторяющихся орфографических ошибок | Целочисленный подсчёт идентичных строк ошибок в партии |
| Профиль принудительного разнообразия | Синтетическая маска лексического разнообразия | Целочисленное рассеяние частот использования словаря |
| Отчёт о запутанности | Структурированная запись, связывающая артефакты с гипотезами общего происхождения | Агрегированные целочисленные векторы |
| CAIE-разрыв | Дескриптор обнаруженной аномалии для движка межартефактной несоответствия | Булев триггер + целочисленное смещение серьёзности |
| Пакетный анализ | Одновременное сравнение всех документов в партии | Матричные операции над целочисленными подсчётами отпечатков |

**Компоненты**

| Компонент | Роль |
|---|---|
| EntanglementEngine | Центральный процессор, обнаруживающий фабрики подделок посредством пакетных детерминированных конвейеров. |
| EntanglementCAIEIntegration | Мост, транслирующий выходные данные движка в CAIE-совместимые логические разрывы. |
| analyze_batch() | Выполняет полное детерминированное сравнение документной партии. |
| query_cross_linked() | Реконструирует сети подделок по реляционным записям базы данных. |
| to_caie_fractures() | Преобразует находки в инжектируемые разрывы для последующего анализа несоответствий. |

**Глоссарий**

- **Запутанность** — Неслучайная корреляция между документами, указывающая на общий генеративный источник.
- **Фабричная сигнатура** — Детерминированный повторяющийся паттерн в партии, статистически несовместимый с независимым авторством.
- **Детерминированная целочисленная арифметика** — Точные операции подсчёта (сложение, вычитание, сравнение целых чисел), дающие воспроизводимые результаты без ошибок округления.
- **Перекрёстный запрос** — Реляционный поиск, реконструирующий полные сети подделок по записям базы данных.
- **CAIE** — Движок межартефактной несоответствия; подсистема картирования противоречий между типами доказательств.
- **Пирсовская семиотика** — Формальное изучение знаков и интерпретантов, применённое здесь как строгие правила обнаружения, а не как литературная теория.
- **Фильтры Эко/Грайса** — Интерпретативные модели и кооперативные максимы, перекодированные как алгоритмические граничные условия.

**Научное Примечание**

> 【Научное примечание】
> Упоминания Пирса, Эко и Грайса в данной системе не являются апелляциями к мистицизму или литературной критике. Они функционируют точно так же, как откалиброванные датчики в физическом приборе. Семиотика Пирса задаёт решётку обнаружения (что считается признаком подделки). Интерпретативные модели Эко выступают в роли шумовых фильтров против переинтерпретации. Кооперативные максимы Грайса определяют ожидаемую базовую линию; отклонение от неё измеряется как дискретное целочисленное смещение, а не как субъективное впечатление. Когда движок сообщает о «запутанности», он регистрирует структурную аномалию, зафиксированную датчиком, а не метафизическую связь.

---

## 中文

**这是什么模块？**

本模块是 VIGÍA 取证平台第六层（P6）检测引擎。它将文档集合视为实物证据批次。该模块不通过阅读来提取语义，而是测量"语言纠缠"——将表面上无关的文档与同一伪造工厂绑定的隐形线索。其运作方式类似于取证质谱仪：不直接解读意图，而是通过确定性整数运算统计精确的结构重叠，以判断文档是否源自同一出处。

**关键概念**

| 概念 | 取证功能 | 确定性基础 |
|---|---|---|
| N元语法指纹 | 从文本中提取的可计数标记序列标识符 | 精确集合重叠的整数基数 |
| 杰卡德相似度 | 两个取证工件之间的精确结构重叠 | 两个整数的有理比率（交集计数/并集计数）；不舍入 |
| 物理键盘签名 | 由反复出现的拼写错误留下的行为痕迹 | 批次中相同错误字符串的整数计数 |
| 强制多样性画像 | 人工词汇多样性掩码 | 词汇使用的整数频率离散度 |
| 纠缠报告 | 将取证工件与共同来源假设关联的结构化取证记录 | 聚合整数向量 |
| CAIE 逻辑断裂 | 注入跨工件不一致引擎（CAIE）的逻辑断裂描述符 | 布尔触发器 + 整数严重性偏移 |
| 批次分析 | 对一批次内所有文档进行同步确定性比较 | 对整数指纹计数的矩阵运算 |

**运作组件**

| 组件 | 角色 |
|---|---|
| EntanglementEngine | 通过批量确定性流水线检测伪造工厂的中央处理器。 |
| EntanglementCAIEIntegration | 将引擎输出转换为 CAIE 兼容逻辑断裂的桥接模块。 |
| analyze_batch() | 执行文档批次的完整确定性比较。 |
| query_cross_linked() | 从关系数据库记录重建伪造网络。 |
| to_caie_fractures() | 将发现转换为可注入的断裂供下游不一致分析使用。 |

**术语表**

- **纠缠** — 文档之间的非随机相关性，表明其共享同一生成源。
- **工厂签名** — 批次内反复出现的确定性模式，与独立创作不兼容。
- **确定性整数运算** — 精确的计数操作（整数加减、比较），产生可复现结果且无舍入误差。
- **交叉关联查询** — 通过数据库记录重建伪造网络的关系型搜索。
- **CAIE** — 跨工件不一致引擎（Cross-Artifact Incongruence Engine）。
- **皮尔斯符号学** — 对符号与解释项的形式研究，在此作为检测规则应用，而非文学理论。
- **艾柯/格赖斯过滤器** — 溯因模型与会话准则被重新编码为算法边界条件。

**科学说明**

> 【科学说明】
> 本系统中提及的皮尔斯、艾柯与格赖斯术语并非神秘主义或文学批评的诉求。它们的功能完全类似于物理仪器中经过校准的传感器。皮尔斯的符号学提供了检测栅格（什么算作伪造的符号）。艾柯的阐释模型充当防止过度解读的噪声滤波器。格赖斯的合作准则定义了预期基线；偏离该基线的程度被量化为离散的整数偏移，而非主观印象。当引擎报告"纠缠"时，它报告的是传感器检测到的结构性异常，而非形而上的关联。

---

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
