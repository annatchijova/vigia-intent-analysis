<!--
VIGIA Academic Documentation
Module: b12aabdd
Batch ID: vigia-doc-0079-b12aabdd
Generated: 2026-05-20T14:56:47.861503+00:00
-->

# VIGÍA Trust Fusion Engine (P2) — Academic Technical Documentation

## Module: `vigia/core/trust_fusion.py`

---

## ENGLISH

### What Is This Module?

The VIGÍA Trust Fusion Engine (Pipeline Layer P2) is a deterministic decision-support system that synthesizes the credibility of digital evidence from four forensic dimensions: temporal consistency, provenance lineage, neighborhood correlation, and Bayesian belief revision. It processes discrete, integer-scaled trust metrics to ensure that every trust score is reproducible across executions. Rather than treating evidence assessment as subjective intuition, the module applies exact arithmetic rules—addition, exact multiplication, and integer ratio calculations—to fuse multiple indicators into a single, auditable confidence value. It is designed for scientists who require transparent, step-by-verifiable-step reasoning about why a given digital artifact is trusted or distrusted.

### Key Concepts

| Concept | Description | Deterministic Function |
|---|---|---|
| Temporal Artifact | A timestamped forensic unit carrying lifecycle metadata and severity weights | Supplies discrete integer timestamps to sequence events without clock ambiguity |
| Provenance Trust | A score reflecting the integrity of an artifact's chain of custody and origin | Computed by summing exact integer weights along the provenance graph |
| Neighborhood Context | The local cluster of artifacts directly linked to a target artifact | Enables deterministic neighbor counting and exact mean trust aggregation |
| Bayesian Trust Update | A structured revision of belief when new correlated evidence is observed | Updates trust states using integer-scaled likelihood ratios and exact marginalization |
| Trust Fusion Engine | The Layer P2 orchestrator that unifies temporal, provenance, and neighborhood data | Executes deterministic integer arithmetic pipelines to yield reproducible scores |
| Reliability Ceiling | A hard upper bound applied to prevent trust inflation | Enforced as an exact rational or integer threshold |

### Component Reference

*TemporalArtifact* — Represents one piece of digital evidence bound to a discrete time index. It encapsulates creation and modification timestamps, severity weights, and integrity flags. This object allows the engine to detect **逻辑断裂** (logical breaks) in event sequences by comparing integer timestamps against deterministic ordering rules.

*NeighborhoodContext* — Defines the relational topology around a target artifact. It stores identifiers of neighboring artifacts and their individual trust states. Through exact integer summation and division, it calculates aggregate neighborhood properties—such as mean trust, contamination counts, and suspicious ratios—without any statistical sampling.

*BayesianTrustUpdate* — Encodes the evidentiary weight of a new observation. It translates raw signals into integer-scaled likelihood values and combines them with existing trust states via exact arithmetic to produce a revised posterior score. The marginal evidence total is computed deterministically across all competing hypotheses.

*TrustFusionEngine* — The central processor of Layer P2. It ingests artifacts, retrieves their neighborhoods, applies Bayesian revisions, and fuses provenance and temporal factors into an effective trust score. All operations follow deterministic integer arithmetic to guarantee bitwise reproducibility.

*create_artifact_from_caie_result()* — Converts output from an external CAIE analysis into a standardized Temporal Artifact with integer-encoded fields.

*effective_provenance_trust()* — Derives a custody-chain confidence score by traversing provenance links and aggregating exact integer weights.

*compute_temporal_trust_factor()* — Maps the maximum weighted severity observed in an artifact's history to a temporal integrity coefficient. The mapping follows a deterministic decay law; in the hardened implementation, this is realized through exact rational arithmetic or precomputed integer lookup tables, avoiding floating-point approximations.

*compute_effective_trust()* — Fuses the provenance trust score with the temporal integrity factor through exact multiplication to generate a composite trust metric.

*apply_reliability_ceiling()* — Imposes a deterministic upper bound on the composite score to prevent over-confidence.

*contamination_ratio()* — Returns the exact integer ratio of neighbors flagged as contaminated to the total neighbor count.

*suspicious_ratio()* — Returns the exact integer ratio of neighbors flagged as suspicious to the total neighbor count.

*trust_delta()* — Computes the exact arithmetic difference between the current trust state and the prior trust state.

*was_degraded()* — A predicate that evaluates whether a logical break or negative trust delta indicates degradation.

### Glossary

- **Provenance**: The documented chain of custody and origin for a digital artifact.
- **Temporal Integrity**: The property of an artifact having a chronologically consistent, unbroken timeline.
- **Logical Break (逻辑断裂)**: A deterministic discontinuity detected in an artifact's temporal or causal sequence.
- **Neighborhood**: The set of artifacts directly correlated with a target artifact.
- **Likelihood**: An integer-scaled weight representing the conditional probability of evidence given a hypothesis.
- **Evidence Marginal**: The total weight of evidence aggregated across all possible hypotheses.
- **Contamination**: The presence of artifacts from untrusted or compromised sources within a neighborhood.
- **Degradation**: A measurable, deterministic reduction in an artifact's trust state.
- **Reliability Ceiling**: A maximum allowable trust score enforced by the system.
- **Trust Delta**: The signed integer difference between successive trust states.

### 【Scientific Note】

The terminology associated with Charles Sanders Peirce, Umberto Eco, and H. P. Grice is sometimes mischaracterized as esoteric or mystical. In the VIGÍA framework, these names denote rigorous epistemological instruments—analogous to laboratory sensors. Peirce's abduction operates like a smoke detector: it maps anomalous traces (signs) onto the most plausible explanatory hypothesis. Eco's semiotics functions like a spectrometer: it decodes ambiguous signs by referencing a structured encyclopedia of prior correlations, not by invoking magic. Grice's cooperative maxims operate like a parity-check protocol on a data channel: they provide calibration rules that allow the engine to infer meaningful correlations from artifact interactions rather than noise. These frameworks supply deterministic rules of interpretation; they do not require belief, intuition, or supernatural agency.

---

## ESPAÑOL

### ¿Qué es este módulo?

El Motor de Fusión de Confianza VIGÍA (Capa P2 del Pipeline) es un sistema determinista de apoyo a la decisión que sintetiza la credibilidad de la evidencia digital a partir de cuatro dimensiones forenses: consistencia temporal, linaje de procedencia, correlación de vecindario y revisión bayesiana de creencias. Procesa métricas de confianza escaladas en enteros para garantizar que cada puntaje sea reproducible. En lugar de tratar la evaluación de evidencias como intuición subjetiva, el módulo aplica reglas aritméticas exactas—suma, multiplicación exacta y cálculos de razones enteras—para fusionar múltiples indicadores en un valor de confianza único y auditables.

### Conceptos Clave

| Concepto | Descripción | Función Determinista |
|---|---|---|
| Artefacto Temporal | Unidad forense con marca temporal y metadatos de ciclo de vida | Provee marcas temporales enteras para secuenciar eventos sin ambigüedad |
| Confianza de Procedencia | Puntaje que refleja la integridad de la cadena de custodia y origen | Calculado sumando pesos enteros exactos a lo largo del grafo de procedencia |
| Contexto de Vecindario | Agrupación local de artefactos vinculados directamente a un objetivo | Permite conteo determinista de vecinos y agregación exacta de confianza media |
| Actualización Bayesiana de Confianza | Revisión estructurada de la creencia ante nueva evidencia correlacionada | Actualiza estados usando razones de verosimilitud escaladas en enteros y marginalización exacta |
| Motor de Fusión de Confianza | Orquestador de Capa P2 que unifica datos temporales, de procedencia y vecindario | Ejecuta tuberías aritméticas enteras deterministas para producir puntajes reproducibles |
| Techo de Fiabilidad | Límite superior estricto para prevenir la inflación de confianza | Aplicado como umbral racional o entero exacto |

### Referencia de Componentes

*TemporalArtifact* — Representa una pieza de evidencia digital ligada a un índice temporal discreto. Encapsula marcas de creación y modificación, pesos de severidad y banderas de integridad. Permite al motor detectar **逻辑断裂** (rupturas lógicas) en secuencias de eventos comparando marcas temporales enteras contra reglas deterministas de ordenamiento.

*NeighborhoodContext* — Define la topología relacional alrededor de un artefacto objetivo. Almacena identificadores de artefactos vecinos y sus estados de confianza individuales. Mediante suma y división exacta de enteros, calcula propiedades agregadas—como confianza media, conteos de contaminación y ratios de sospecha—sin muestreo estadístico.

*BayesianTrustUpdate* — Codifica el peso probatorio de una nueva observación. Traduce señales brutas en valores de verosimilitud escalados en enteros y los combina con estados de confianza existentes mediante aritmética exacta para producir un puntaje posterior revisado.

*TrustFusionEngine* — El procesador central de la Capa P2. Ingiere artefactos, recupera sus vecindarios, aplica revisiones bayesianas y fusiona factores de procedencia y temporales en un puntaje efectivo de confianza. Todas las operaciones siguen aritmética entera determinista.

*create_artifact_from_caie_result()* — Convierte la salida de un análisis externo CAIE en un Artefacto Temporal estandarizado con campos codificados en enteros.

*effective_provenance_trust()* — Deriva un puntaje de confianza de cadena de custodia recorriendo enlaces de procedencia y agregando pesos enteros exactos.

*compute_temporal_trust_factor()* — Mapea la severidad ponderada máxima observada en la historia de un artefacto a un coeficiente de integridad temporal. El mapeo sigue una ley de decaimiento determinista; en la implementación endurecida, se realiza mediante aritmética racional exacta o tablas de búsqueda enteras precomputadas, evitando aproximaciones de punto flotante.

*compute_effective_trust()* — Fusiona el puntaje de confianza de procedencia con el factor de integridad temporal mediante multiplicación exacta.

*apply_reliability_ceiling()* — Impone un límite superior determinista sobre el puntaje compuesto.

*contamination_ratio()* — Devuelve la razón entera exacta de vecinos marcados como contaminados respecto al total.

*suspicious_ratio()* — Devuelve la razón entera exacta de vecinos marcados como sospechosos respecto al total.

*trust_delta()* — Calcula la diferencia aritmética exacta entre el estado de confianza actual y el anterior.

*was_degraded()* — Predicado que evalúa si una ruptura lógica o un delta de confianza negativo indica degradación.

### Glosario

- **Procedencia**: Cadena documentada de custodia y origen de un artefacto digital.
- **Integridad Temporal**: Propiedad de un artefacto de tener una línea de tiempo cronológicamente consistente e ininterrumpida.
- **Ruptura Lógica (逻辑断裂)**: Discontinuidad determinista detectada en la secuencia temporal o causal de un artefacto.
- **Vecindario**: Conjunto de artefactos directamente correlacionados con un artefacto objetivo.
- **Verosimilitud**: Peso escalado en enteros que representa la probabilidad condicional de la evidencia dada una hipótesis.
- **Marginal de Evidencia**: Peso total de la evidencia agregado a través de todas las hipótesis posibles.
- **Contaminación**: Presencia de artefactos de fuentes no confiables o comprometidas dentro de un vecindario.
- **Degradación**: Reducción determinista y medible en el estado de confianza de un artefacto.
- **Techo de Fiabilidad**: Puntaje máximo de confianza permitido por el sistema.
- **Delta de Confianza**: Diferencia entera con signo entre estados de confianza sucesivos.

### 【Scientific Note】

La terminología asociada a Charles Sanders Peirce, Umberto Eco y H. P. Grice a veces se tacha de esotérica o mística. En el marco VIGÍA, estos nombres designan instrumentos epistemológicos rigurosos—análogos a sensores de laboratorio. La abducción de Peirce opera como un detector de humo: mapea trazas anómalas (signos) sobre la hipótesis explicativa más plausible. La semiótica de Eco funciona como un espectrómetro: decodifica signos ambiguos consultando una enciclopedia estructurada de correlaciones previas, sin invocar magia. Los máximas cooperativas de Grice operan como un protocolo de verificación de paridad en un canal de datos: proporcionan reglas de calibración que permiten al motor inferir correlaciones significativas a partir de interacciones entre artefactos, en lugar de ruido. Estos marcos aportan reglas deterministas de interpretación; no requieren fe, intuición ni agentes sobrenaturales.

---

## РУССКИЙ

### Что представляет собой этот модуль?

Модуль слияния доверия VIGÍA (уровень P2 конвейера) — это детерминированная система поддержки принятия решений, синтезирующая достоверность цифровых доказательств по четырём судебным измерениям: временная согласованность, происхождение (провенанс), корреляция окружения и байесовское обновление убеждений. Он обрабатывает дискретные целочисленные метрики доверия, гарантируя воспроизводимость каждого показателя. Вместо субъективной интуиции модуль применяет точные арифметические правила — сложение, точное умножение и вычисление целочисленных отношений — для объединения множества индикаторов в единое поддающееся аудиту значение доверия.

### Ключевые концепции

| Концепция | Описание | Детерминированная роль |
|---|---|---|
| Временной артефакт | Форензическая единица с меткой времени и метаданными жизненного цикла | Поставляет дискретные целочисленные метки времени для упорядочивания событий |
| Доверие происхождения | Показатель, отражающий целостность цепочки хранения и происхождения | Вычисляется суммированием точных целочисленных весов по графу провенанса |
| Контекст окружения | Локальный кластер артефактов, непосредственно связанных с целевым | Обеспечивает детерминированный подсчёт соседей и точное усреднение доверия |
| Байесовское обновление доверия | Структурированная корректировка убеждения при появлении новых коррелированных доказательств | Обновляет состояния с помощью целочисленных отношений правдоподобия и точной маргинализации |
| Механизм слияния доверия | Оркестратор уровня P2, объединяющий временные, провенансные и окружные данные | Выполняет конвейеры детерминированной целочисленной арифметики |
| Потолок надёжности | Жёсткая верхняя граница, предотвращающая завышение доверия | Применяется как точный целочисленный или рациональный порог |

### Описание компонентов

*TemporalArtifact* — Представляет один цифровой доказательный объект, привязанный к дискретному временному индексу. Инкапсулирует метки создания и модификации, веса серьёзности и флаги целостности. Позволяет движку обнаруживать **逻辑断裂** (логические разрывы) в последовательностях событий путём сравнения целочисленных меток времени по детерминированным правилам упорядочивания.

*NeighborhoodContext* — Определяет реляционную топологию вокруг целевого артефакта. Хранит идентификаторы соседних артефактов и их индивидуальные состояния доверия. Посредством точного целочисленного суммирования и деления вычисляет агрегированные свойства окружения — среднее доверие, количество загрязнённых и коэффициенты подозрительности — без статистической выборки.

*BayesianTrustUpdate* — Кодирует доказательный вес нового наблюдения. Преобразует сырые сигналы в целочисленные значения правдоподобия и комбинирует их с существующими состояниями доверия через точную арифметику для получения скорректированного апостериорного показателя.

*TrustFusionEngine* — Центральный процессор уровня P2. Поглощает артефакты, извлекает их окружения, применяет байесовские корректировки и объединяет факторы провенанса и временны́е в эффективный показатель доверия. Все операции следуют детерминированной целочисленной арифметике.

*create_artifact_from_caie_result()* — Преобразует выходные данные внешнего анализа CAIE в стандартизированный Временной Артефакт с целочисленными полями.

*effective_provenance_trust()* — Выводит показатель доверия цепочки хранения, обходя ссылки провенанса и агрегируя точные целочисленные веса.

*compute_temporal_trust_factor()* — Отображает максимальный взвешенный уровень серьёзности из истории артефакта на коэффициент временной целостности. Отображение следует детерминированному закону затухания; в закалённой реализации это достигается точной рациональной арифметикой или предвычисленными целочисленными таблицами поиска, избегая приближений с плавающей запятой.

*compute_effective_trust()* — Объединяет показатель доверия провенанса с коэффициентом временной целостности посредством точного умножения.

*apply_reliability_ceiling()* — Накладывает детерминированную верхнюю границу на итоговый показатель.

*contamination_ratio()* — Возвращает точное целочисленное отношение соседей, помеченных как загрязнённые, к общему числу соседей.

*suspicious_ratio()* — Возвращает точное целочисленное отношение соседей, помеченных как подозрительные, к общему числу.

*trust_delta()* — Вычисляет точную арифметическую разность между текущим и предыдущим состоянием доверия.

*was_degraded()* — Предикат, оценивающий, указывает ли логический разрыв или отрицательная дельта доверия на деградацию.

### Глоссарий

- **Провенанс**: Документированная цепочка хранения и происхождения цифрового артефакта.
- **Временная целостность**: Свойство артефакта иметь хронологически согласованную, непрерывную временную шкалу.
- **Логический разрыв (逻辑断裂)**: Детерминированный разрыв, обнаруженный во временной или причинной последовательности артефакта.
- **Окружение**: Набор артефактов, непосредственно коррелированных с целевым артефактом.
- **Правдоподобие**: Целочисленный вес, представляющий условную вероятность доказательства при данной гипотезе.
- **Маргинал доказательств**: Совокупный вес доказательств по всем возможным гипотезам.
- **Загрязнение**: Присутствие в окружении артефактов из ненадёжных или скомпрометированных источников.
- **Деградация**: Измеримое детерминированное снижение состояния доверия артефакта.
- **Потолок надёжности**: Максимально допустимый показатель доверия, устанавливаемый системой.
- **Дельта доверия**: Знаковая целочисленная разность между последовательными состояниями доверия.

### 【Scientific Note】

Терминология, ассоциированная с Чарльзом Сандерсом Пирсом, Умберто Эко и Х. П. Грайсом, иногда ошибочно характеризуется как эзотерическая или мистическая. В рамках VIGÍA эти имена обозначают строгие эпистемологические инструменты — аналогичные лабораторным датчикам. Абдукция Пирса работает как дымовой извещатель: она отображает аномальные следы (знаки) на наиболее правдоподобную объяснительную гипотезу. Семиотика Эко функционирует как спектрометр: декодирует неоднозначные знаки, обращаясь к структурированной энциклопедии предшествующих корреляций, не прибегая к мистике. Максимы Грайса работают как протокол проверки чётности в канале передачи данных: они предоставляют правила калибровки, позволяющие движку выводить значимые корреляции из взаимодействий артефактов, а не из шума. Эти рамки задают детерминированные правила интерпретации; они не требуют веры, интуиции или сверхъестественных посредников.

---

## 中文

### 本模块是什么？

VIGÍA 信任融合引擎（管道层 P2）是一个确定性决策支持系统，从四个取证维度综合数字证据的可信度：时间一致性、来源溯源、邻域关联以及贝叶斯信念修正。它处理离散的整数缩放信任指标，确保每个信任分数在各次执行中均可复现。该模块不将证据评估视为主观直觉，而是应用精确的算术规则——加法、精确乘法和整数比率计算——将多个指标融合为单一可审计的置信值。

### 核心概念

| 概念 | 描述 | 确定性功能 |
|---|---|---|
| 时间取证工件 | 携带生命周期元数据和严重程度权重的带时间戳取证单元 | 提供离散整数时间戳以消除时钟歧义地排序事件 |
| 来源信任 | 反映证据监管链和来源完整性的分数 | 通过在来源图上累加精确整数权重计算 |
| 邻域上下文 | 与目标取证工件直接关联的本地工件集群 | 支持确定性邻居计数和精确平均信任聚合 |
| 贝叶斯信任更新 | 新关联证据到来时的结构化信念修正 | 使用整数缩放似然比和精确边际化更新信任状态 |
| 信任融合引擎 | 统一时间、来源和邻域数据的 P2 层编排器 | 执行确定性整数运算管道以产生可复现的分数 |
| 可靠性上限 | 防止信任膨胀的硬性上界 | 作为精确有理数或整数阈值强制执行 |

### 组件说明

*TemporalArtifact* — 表示绑定到离散时间索引的单个数字证据。封装创建和修改时间戳、严重程度权重和完整性标志。通过将整数时间戳与确定性排序规则进行比较，使引擎能够检测事件序列中的**逻辑断裂**。

*NeighborhoodContext* — 定义目标取证工件周围的关系拓扑。存储相邻取证工件的标识符及其各自的信任状态。通过精确整数求和与除法，计算聚合邻域属性——如平均信任、污染计数和可疑比率——无需统计采样。

*BayesianTrustUpdate* — 编码新观测的证据权重。将原始信号转换为整数缩放的似然值，并通过精确算术将其与现有信任状态组合，以产生修正后的后验分数。

*TrustFusionEngine* — P2 层中央处理器。摄取取证工件、检索其邻域、应用贝叶斯修正，并将来源和时间因素融合为有效信任分数。所有操作遵循确定性整数运算以保证逐位可复现性。

*create_artifact_from_caie_result()* — 将外部 CAIE 分析的输出转换为具有整数编码字段的标准化时间取证工件。

*effective_provenance_trust()* — 通过遍历来源链接并聚合精确整数权重，推导监管链置信度分数。

*compute_temporal_trust_factor()* — 将取证工件历史中观测到的最大加权严重程度映射到时间完整性系数。该映射遵循确定性衰减规律；在加固实现中，通过精确有理数运算或预计算整数查找表实现，避免浮点近似。

*compute_effective_trust()* — 通过精确乘法将来源信任分数与时间完整性因子融合，生成复合信任指标。

*apply_reliability_ceiling()* — 对复合分数施加确定性上界以防止过度置信。

*contamination_ratio()* — 返回被标记为污染的邻居与总邻居数的精确整数比率。

*suspicious_ratio()* — 返回被标记为可疑的邻居与总邻居数的精确整数比率。

*trust_delta()* — 计算当前信任状态与先前信任状态之间的精确算术差值。

*was_degraded()* — 评估逻辑断裂或负信任增量是否指示降级的谓词。

### 术语表

- **来源溯源**：数字取证工件的记录监管链和来源。
- **时间完整性**：取证工件具有时间顺序一致、不间断时间线的属性。
- **逻辑断裂**：在取证工件的时间或因果序列中检测到的确定性不连续性。
- **邻域**：与目标取证工件直接关联的取证工件集合。
- **似然**：表示给定假设下证据条件概率的整数缩放权重。
- **证据边际**：跨所有可能假设聚合的证据总权重。
- **污染**：邻域中存在来自不可信或已受损来源的取证工件。
- **降级**：取证工件信任状态的可测量确定性降低。
- **可靠性上限**：系统强制执行的最大允许信任分数。
- **信任增量**：连续信任状态之间的有符号整数差值。

### 【科学说明】

皮尔士、艾柯与格赖斯的术语有时被错误地定性为神秘主义。在 VIGÍA 框架中，这些名称指代严格的认识论工具——类似于实验室传感器。皮尔士的溯因推理像烟雾探测器一样工作：它将异常痕迹（符号）映射到最合理的解释假设上。艾柯的符号学功能像光谱仪：通过参照先前关联的结构化百科全书来解码模糊符号，而不是诉诸魔法。格赖斯的合作准则像数据信道上的奇偶校验协议一样运作：它们提供校准规则，使引擎能够从取证工件交互中推断有意义的关联，而非噪声。这些框架提供确定性的解释规则；它们不需要信仰、直觉或超自然力量。

---

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
