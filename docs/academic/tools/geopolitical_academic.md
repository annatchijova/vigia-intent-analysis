<!--
VIGIA Academic Documentation
Module: 1c834989
Batch ID: vigia-doc-0162-1c834989
Generated: 2026-05-20T14:56:47.879519+00:00
-->

## ENGLISH

### What Is This Module?
`vigia/tools/geopolitical.py` implements the **Fifth Pillar of VIGÍA: the Geopolitical Intent Engine**. It is not a conventional malware scanner. Rather, it is a strategic-consistency analyzer designed for scientists who need to evaluate cyber-attack attribution beyond raw technical artifacts.

When an incident occurs, investigators collect **technical signs**—code watermarks, language preferences, network nodes. These signs can be deliberately planted. This module treats each sign as a hypothesis and tests it against four non-technical dimensions: (1) documented state **doctrine**; (2) **geopolitical opportunity** at the exact moment of the incident; (3) the **cost of infrastructure exposure**; and (4) **linguistic authenticity**. If the technical attribution contradicts any of these dimensions, the engine registers a **logical rupture** and adjusts the composite score downward using deterministic integer arithmetic.

All calculations rely on integer weights, integer penalties, and integer baselines. No rounding errors or probabilistic noise are introduced.

### Key Concepts

| Component | Scientific Role | Operational Purpose |
|-----------|----------------|---------------------|
| **GeopoliticalIntentEngine** | Central evaluation orchestrator | Coerces all rule outputs into a single, reproducible risk tier. |
| **Cui Bono Analysis** (`rule_cui_bono`) | Interest-alignment validator | Verifies whether the attributed actor stands to gain strategically from the incident. |
| **Doctrine Consistency** (`rule_doctrine_consistency`) | Historical-pattern validator | Compares claimed attribution against documented strategic behavior of the state or group. |
| **Temporal Opportunity** (`rule_temporal_opportunity`) | Chronological-alignment validator | Checks if the incident timing coincides with elections, treaties, or kinetic conflicts relevant to the actor. |
| **Infrastructure Seizure Risk** (`rule_infrastructure_seizure_risk`) | Asset-exposure validator | Assesses whether the operation unnecessarily burns high-value command-and-control assets. |
| **Linguistic False-Flag Detection** (`rule_linguistic_false_flag_detection`) | Signal-authenticity validator | Detects planted language markers by testing for statistical inconsistencies in natural usage. |
| **Strategic Intent Inference** (`infer_strategic_intent`) | Synthesis layer | Aggregates individual rule scores into a final integer assessment. |
| **APT_PROFILES** | Reference knowledge base | Structured historical records of actor capabilities, preferred targets, and known doctrine. |
| **GEOPOLITICAL_EVENTS** | Temporal knowledge base | Annotated timeline of geopolitical windows (elections, sanctions, military maneuvers). |
| **RULE_WEIGHTS** | Integer coefficients | Deterministic multipliers assigned to each validation rule to preserve exact arithmetic. |
| **RULE_DEPENDENCIES** | Logical prerequisite map | Defines conditional relationships among rules (e.g., failure of doctrine check modifies temporal weight). |
| **SIGMOID_SCALE / SIGMOID_SHIFT** | Threshold-scaling parameters | Integer-ratio constants that map cumulative scores to discrete risk bands without fractional mathematics. |
| **PENALTY_SCALE** | Integer decrement multiplier | Uniform scaling factor applied to logical-rupture penalties to maintain integral precision. |
| **BASELINE_MEAN / BASELINE_MAD** | Historical reference constants | Median-centered statistics (in integer form) used to flag anomalous deviations from historical norms. |

### Glossary

- **Attribution** — The formal assignment of responsibility for a cyber incident to a specific state or non-state actor.
- **False Flag** — A covert operation engineered to appear as though it was perpetrated by another party.
- **Doctrine** — The recorded strategic principles—public or classified—that consistently guide an actor's decisions.
- **Technical Sign** — A forensic artifact (e.g., compiler watermark, code comment, file path) treated as a pointer toward a specific actor.
- **Interpretant** — In this framework, the structured knowledge base (APT_PROFILES + GEOPOLITICAL_EVENTS) that decodes a technical sign into a real-world inference.
- **Disinformation Cost** — The cumulative political, economic, and operational loss an actor suffers if its deception is revealed.
- **Logical Rupture** — A deterministic inconsistency between expected patterns (from doctrine and history) and observed incident characteristics; a primary indicator of fabrication.
- **Baseline Mean / MAD** — The central tendency and median absolute deviation of historical attribution scores, stored as integers to enable exact deviation detection.

### 【Scientific Note】
The terminology of Peirce, Eco, and Grice is employed here as formal epistemological infrastructure, not mysticism. Consider a standard laboratory sensor: the **sign** is the raw voltage reading; the **object** is the underlying physical quantity (e.g., chemical concentration); the **interpretant** is the calibration curve built from prior controlled experiments. **Thirdness** is nothing more than the signal-processing layer that translates voltage into concentration by mediating between raw data and historical calibration. Likewise, in this module, a linguistic marker is a voltage, state doctrine is the calibration standard, and Gricean maxims are noise-filtering rules. Umberto Eco's codes define the encoding standard. The entire pipeline is a deterministic measurement apparatus; all internal arithmetic is performed with integers to ensure that every repetition of the same input yields exactly the same output.

---

## ESPAÑOL

### ¿Qué es este módulo?
`vigia/tools/geopolitical.py` implementa el **Quinto Pilar de VIGÍA: el Motor de Intención Geopolítica**. No es un escáner de malware convencional, sino un analizador de coherencia estratégica destinado a científicos que deben evaluar la atribución de ciberataques más allá de los artefactos técnicos brutos.

Cuando ocurre un incidente, los investigadores recogen **signos técnicos**: marcas de compilador, preferencias idiomáticas, nodos de red. Estos signos pueden ser plantados deliberadamente. Este módulo trata cada signo como una hipótesis y la contrasta con cuatro dimensiones no técnicas: (1) la **doctrina** estatal documentada; (2) la **oportunidad geopolítica** en el momento exacto del incidente; (3) el **costo de exposición de infraestructura**; y (4) la **autenticidad lingüística**. Si la atribución técnica contradice alguna de estas dimensiones, el motor registra una **ruptura lógica** y ajusta la puntuación compuesta mediante aritmética entera determinista.

Todos los cálculos se apoyan en pesos enteros, penalizaciones enteras y referencias basales enteras. No se introduce ruido por redondeo ni incertidumbre de punto flotante.

### Conceptos clave

| Componente | Función científica | Propósito operativo |
|------------|--------------------|---------------------|
| **GeopoliticalIntentEngine** | Orquestador de evaluación central | Fuerza todas las salidas de las reglas en un único nivel de riesgo reproducible. |
| **Análisis de Cui Bono** (`rule_cui_bono`) | Validador de alineación de intereses | Verifica si el actor atribuido obtiene una ganancia estratégica del incidente. |
| **Consistencia Doctrinal** (`rule_doctrine_consistency`) | Validador de patrón histórico | Compara la atribución reclamada contra el comportamiento estratégico documentado del Estado o grupo. |
| **Oportunidad Temporal** (`rule_temporal_opportunity`) | Validador de alineación cronológica | Comprueba si la cronología del incidente coincide con elecciones, tratados o conflictos relevantes para el actor. |
| **Riesgo de Exposición de Infraestructura** (`rule_infrastructure_seizure_risk`) | Validador de exposición de activos | Evalúa si la operación quema innecesariamente activos de comando y control de alto valor. |
| **Detección Lingüística de Bandera Falsa** (`rule_linguistic_false_flag_detection`) | Validador de autenticidad de señal | Detecta marcadores idiomáticos plantados mediante pruebas de inconsistencias estadísticas en el uso natural. |
| **Inferencia de Intención Estratégica** (`infer_strategic_intent`) | Capa de síntesis | Agrega las puntuaciones individuales en una evaluación final entera. |
| **APT_PROFILES** | Base de conocimiento de referencia | Registros históricos estructurados de capacidades, objetivos preferidos y doctrina conocida de actores. |
| **GEOPOLITICAL_EVENTS** | Base de conocimiento temporal | Cronología anotada de ventanas geopolíticas (elecciones, sanciones, maniobras militares). |
| **RULE_WEIGHTS** | Coeficientes enteros | Multiplicadores deterministas asignados a cada regla de validación para preservar la aritmética exacta. |
| **RULE_DEPENDENCIES** | Mapa de prerrequisitos lógicos | Define relaciones condicionales entre reglas (p. ej., el fallo de la verificación doctrinal modifica el peso temporal). |
| **SIGMOID_SCALE / SIGMOID_SHIFT** | Parámetros de escalamiento de umbral | Constantes de relación entera que asignan puntuaciones acumuladas a bandas discretas de riesgo sin matemáticas fraccionarias. |
| **PENALTY_SCALE** | Multiplicador entero de decremento | Factor de escala uniforme aplicado a las penalizaciones por ruptura lógica para mantener la precisión integral. |
| **BASELINE_MEAN / BASELINE_MAD** | Constantes de referencia histórica | Estadísticas centradas en la mediana (en forma entera) usadas para señalar desviaciones anómalas respecto a normas históricas. |

### Glosario

- **Atribución** — Asignación formal de la responsabilidad de un ciberataque a un actor estatal o no estatal específico.
- **Bandera Falsa** — Operación encubierta diseñada para parecer perpetrada por otra parte.
- **Doctrina** — Principios estratégicos registrados—públicos o clasificados—que guían consistentemente las decisiones de un actor.
- **Signo Técnico** — Artefacto forense (p. ej., marca de compilador, comentario de código, ruta de archivo) tratado como indicador de un actor específico.
- **Interpretante** — En este marco, la base de conocimiento estructurada (APT_PROFILES + GEOPOLITICAL_EVENTS) que descifra un signo técnico en una inferencia del mundo real.
- **Costo de Desinformación** — Pérdida política, económica y operativa acumulada que sufre un actor si se revela su engaño.
- **Ruptura Lógica** — Inconsistencia determinista entre los patrones esperados (de la doctrina y la historia) y las características observadas del incidente; indicador primario de fabricación.
- **Media Basal / DAM (MAD)** — Tendencia central y desviación absoluta mediana de puntuaciones históricas de atribución, almacenadas como enteros para permitir la detección exacta de desviaciones.

### 【Nota Científica】
La terminología de Peirce, Eco y Grice se emplea aquí como infraestructura epistemológica formal, no como misticismo. Considere un sensor de laboratorio estándar: el **signo** es la lectura de voltaje crudo; el **objeto** es la cantidad física subyacente (p. ej., concentración química); el **interpretante** es la curva de calibración construida a partir de experimentos controlados previos. La **terceridad** no es más que la capa de procesamiento de señales que traduce voltaje en concentración al mediar entre los datos brutos y la calibración histórica. De manera similar, en este módulo un marcador lingüístico es un voltaje, la doctrina estatal es el estándar de calibración y las máximas de Grice son reglas de filtrado de ruido. Los códigos de Eco definen el estándar de codificación. Todo el proceso es un aparato de medición determinista; toda la aritmética interna se realiza con números enteros para garantizar que cada repetición de la misma entrada produzca exactamente la misma salida.

---

## РУССКИЙ

### Что это за модуль?
`vigia/tools/geopolitical.py` реализует **Пятый столп VIGÍA: Движок геополитического намерения**. Это не стандартный сканер вредоносных программ, а анализатор стратегической согласованности, предназначенный для учёных, которым необходимо оценить атрибуцию киберинцидента за пределами сырых технических артефактов.

При наступлении инцидента следователи собирают **технические знаки**: метки компилятора, языковые предпочтения, сетевые узлы. Эти знаки могут быть преднамеренно подброшены. Данный модуль рассматривает каждый знак как гипотезу и проверяет её по четырём нетехническим измерениям: (1) документированная государственная **доктрина**; (2) **геополитическая возможность** в точный момент инцидента; (3) **стоимость экспозиции инфраструктуры**; и (4) **лингвистическая подлинность**. Если техническая атрибуция противоречит любому из этих измерений, движок регистрирует **логический разрыв** и скорректирует композитную оценку вниз с помощью детерминированной целочисленной арифметики.

Все вычисления опираются на целочисленные веса, целочисленные штрафы и целочисленные базовые константы. Шум округления и вероятностные погрешности отсутствуют.

### Ключевые концепции

| Компонент | Научная роль | Операционное назначение |
|-----------|--------------|-------------------------|
| **GeopoliticalIntentEngine** | Центральный оркестратор оценки | Приводит все выходные данные правил к единому воспроизводимому уровню риска. |
| **Анализ Cui Bono** (`rule_cui_bono`) | Валидатор соответствия интересов | Проверяет, извлекает ли атрибутированный актёр стратегическую выгоду из инцидента. |
| **Доктринальная согласованность** (`rule_doctrine_consistency`) | Валидатор исторического паттерна | Сопоставляет заявленную атрибуцию с документированным стратегическим поведением государства или группы. |
| **Временно́е окно возможности** (`rule_temporal_opportunity`) | Валидатор хронологического соответствия | Проверяет, совпадает ли момент инцидента с выборами, договорами или кинетическими конфликтами, актуальными для актёра. |
| **Риск компрометации инфраструктуры** (`rule_infrastructure_seizure_risk`) | Валидатор экспозиции активов | Оценивает, не сжигает ли операция без необходимости высокоценные активы управления и контроля. |
| **Лингвистическое обнаружение ложного флага** (`rule_linguistic_false_flag_detection`) | Валидатор подлинности сигнала | Выявляет подброшенные языковые маркеры путём проверки статистических несоответствий в естественном употреблении. |
| **Инференция стратегического намерения** (`infer_strategic_intent`) | Синтезирующий слой | Агрегирует индивидуальные оценки правил в итоговую целочисленную оценку. |
| **APT_PROFILES** | База знаний-эталон | Структурированные исторические записи о возможностях актёров, предпочтительных целях и известной доктрине. |
| **GEOPOLITICAL_EVENTS** | Временна́я база знаний | Аннотированная хронология геополитических окон (выборы, санкции, военные манёвры). |
| **RULE_WEIGHTS** | Целочисленные коэффициенты | Детерминированные множители, назначенные каждому правилу валидации для сохранения точной арифметики. |
| **RULE_DEPENDENCIES** | Карта логических предпосылок | Определяет условные отношения между правилами (например, при провале проверки доктрины изменяется временной вес). |
| **SIGMOID_SCALE / SIGMOID_SHIFT** | Параметры масштабирования порогов | Константы целочисленного отношения, отображающие совокупные оценки на дискретные диапазоны риска без дробной математики. |
| **PENALTY_SCALE** | Целочисленный множитель декремента | Единый масштабирующий фактор, применяемый к штрафам за логический разрыв для поддержания интегральной точности. |
| **BASELINE_MEAN / BASELINE_MAD** | Исторические референтные константы | Медианно-центрированные статистики (в целочисленной форме), используемые для выявления аномальных отклонений от исторических норм. |

### Глоссарий

- **Атрибуция** — Формальное приписывание ответственности за киберинцидент конкретному государственному или негосударственному актёру.
- **Ложный флаг** — Тайная операция, рассчитанная на то, чтобы казаться совершённой другой стороной.
- **Доктрина** — Зафиксированные стратегические принципы—открытые или секретные—последовательно определяющие решения актёра.
- **Технический знак** — Криминалистический артефакт (например, метка компилятора, комментарий в коде, путь к файлу), рассматриваемый как указатель на конкретного актёра.
- **Интерпретант** — В данном фреймворке: структурированная база знаний (APT_PROFILES + GEOPOLITICAL_EVENTS), декодирующая технический знак в вывод о реальном мире.
- **Цена дезинформации** — Совокупные политические, экономические и операционные потери актёра в случае разоблачения его обмана.
- **Логический разрыв** — Детерминированное несоответствие между ожидаемыми паттернами (из доктрины и истории) и наблюдаемыми характеристиками инцидента; первичный индикатор фабрикации.
- **Базовое среднее / MAD** — Центральная тенденция и медианное абсолютное отклонение исторических оценок атрибуции, хранимые как целые числа для точного обнаружения отклонений.

### 【Научное примечание】
Терминология Пирса, Эко и Грайса применяется здесь как формальная эпистемологическая инфраструктура, а не мистика. Рассмотрим стандартный лабораторный датчик: **знак** — это необработанное показание напряжения; **объект** — лежащая в основе физическая величина (например, концентрация химического вещества); **интерпретант** — калибровочная кривая, построенная на основе предыдущих контролируемых экспериментов. **Третичность** — это не что иное, как уровень обработки сигнала, переводящий напряжение в концентрацию путём медиации между необработанными данными и исторической калибровкой. Аналогично, в данном модуле лингвистический маркер — это напряжение, государственная доктрина — стандарт калибровки, а максимы Грайса — правила фильтрации шума. Коды Умберто Эко определяют стандарт кодирования. Весь конвейер представляет собой детерминированный измерительный прибор; вся внутренняя арифметика выполняется с целыми числами, гарантируя, что каждое повторение одних и тех же входных данных даёт в точности одинаковый результат.

---

## 中文

### 本模块是什么？
`vigia/tools/geopolitical.py` 实现了 **VIGÍA 第五支柱：地缘政治意图引擎**。它并非传统的恶意软件扫描器，而是一种战略一致性分析器，专为需要超越原始技术取证工件来评估网络攻击归因的科学家而设计。

当事件发生时，调查人员会收集**技术记号**——编译器水印、语言偏好、网络节点。这些记号可能被刻意植入。本模块将每个记号视为一项假设，并从四个非技术维度对其进行检验：（1）已记录的国家**教义**；（2）事件发生的精确时刻所呈现的**地缘政治机遇**；（3）**基础设施暴露成本**；以及（4）**语言学真实性**。若技术归因与上述任一维度相矛盾，引擎将记录一处**逻辑断裂**，并通过确定性整数运算下调综合评分。

所有计算均依赖整数权重、整数惩罚值和整数基线。不引入任何舍入误差或概率噪声。

### 核心概念

| 概念 | 作用 | 科学意义 |
|---|---|---|
| 地缘政治意图引擎 (GeopoliticalIntentEngine) | 核心评估协调器 | 整合所有逻辑规则为统一评分 |
| 利益归属分析 (Cui Bono) | 利益一致性校验 | 若归因行为体无利可图，则为假旗嫌疑 |
| 教义一致性 | 历史行为模式校验 | 国家遵循已记录的战略教义；偏离暗示欺骗 |
| 时间窗口机遇 | 时机对齐校验 | 事件时机与地缘政治窗口（选举、条约、冲突） |
| 基础设施暴露风险 | 资产暴露校验 | 真实行为体不会无意义地烧毁高价值基础设施 |
| 语言学假旗检测 | 信号真实性校验 | 自然语言留下统计痕迹；植入标记呈现逻辑断裂 |
| 第三性（皮尔斯） | 中介层 | 通过历史模型连接原始技术记号与真实世界对象 |
| 确定性整数评分 | 量化方法 | 所有权值与阈值均使用整数运算，消除舍入歧义 |

### 术语表

- **归因 (Attribution)**: 将事件责任正式指派给特定行为体。
- **假旗行动 (False Flag)**: 旨在嫁祸于他方的隐蔽行动。
- **教义 (Doctrine)**: 公开或机密记录的指导国家行为的战略原则。
- **技术记号 (Technical Sign)**: 指向特定行为体的取证工件（如编译器水印、代码片段）。
- **解释项 (Interpretant)**: 本系统中指结构化知识库（历史模式 + 教义表），用于解码记号。
- **虚假信息成本 (Disinformation Cost)**: 若欺骗被揭露，行为体需承担的政治、经济与行动代价。
- **逻辑断裂 (Logical Rupture)**: 预期模式与观测模式之间的不一致，指示伪造。
- **基线均值 / MAD (Baseline Mean / MAD)**: 历史评分数据的集中趋势与绝对中位差，用于整数偏移量偏差检测。

### 【科学说明】
本模块使用的皮尔斯符号学、艾柯编码理论与格赖斯会话准则并非神秘主义。请以实验室传感器为类比：**记号**即电压读数；**对象**即待测化学浓度；**解释项**即由先前受控实验得出的校准曲线。**第三性**即利用历史数据将原始电压转换为物理量的信号处理层。同理，语言学标记是信号，国家教义是校准标准，格赖斯准则是滤波规则。该框架将这些视为确定性逻辑约束，而非形而上实体。所有计算均以整数运算执行，以确保结果可完全复现。

---

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
