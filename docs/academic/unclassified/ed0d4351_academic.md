<!--
VIGIA Academic Documentation
Module: ed0d4351
Batch ID: vigia-doc-0153-ed0d4351
Generated: 2026-05-20T14:56:47.877494+00:00
-->

## ENGLISH

### What Is This Module?
The Cross-Artifact Incongruence Engine (CAIE) is a deterministic forensic inference system. It ingests disparate digital evidence—such as memory snapshots, event logs, and network records—and evaluates them on a single rigorously calibrated scale. The module treats each evidence item as a semiotic sensor: some sensors are trivially spoofed (e.g., an IP address), whereas others require deep system compromise (e.g., a kernel object). CAIE assigns higher inferential weight to structurally irrefutable evidence, detects contradictions between independent sources, and fuses the findings into a reproducible verdict using exact integer arithmetic.

### Key Concepts

**Table 1. Core Entities**

| Concept | Scientific Meaning | Role in the Analysis Pipeline |
|---|---|---|
| `EvidenceProfile` | A calibration record defining the fabrication cost (spoofability) and investigative priority of an evidence class. | Normalizes heterogeneous measurements onto a unified, deterministic scale. |
| `Artifact` | A single forensic measurement produced by a VIGIA tool (e.g., a memory handle or log entry). | Serves as the raw input datum for validation and weighting. |
| `Fracture` | A logical discrepancy between two artifacts that ought to describe the same state but do not agree. | Indicates potential tampering, collection error, or adversary deception. |
| `CrossArtifactIncongruenceEngine` | The central controller that ingests artifacts, identifies fractures, and issues a fused verdict. | Orchestrates the deterministic inference workflow. |

**Table 2. Deterministic Weighting Formula**

| Symbol | Scientific Interpretation | Deterministic Implementation |
|---|---|---|
| raw_score | Initial suspicion metric reported by the source tool. | Stored as a scaled integer; no inexact representation. |
| spoofability | Estimated ease of fabrication (0 = irrefutable, 1 = trivially faked). | Expressed as an exact rational; all multiplication uses integer numerator/denominator logic. |
| weight | Investigative importance assigned by the examiner or policy. | Strictly integer to preserve commutativity across platforms. |
| base_trust | Confidence in the collection instrument itself. | Integer scaling factor. |
| adjusted_score | Final weighted value: raw_score × (1 − spoofability) × weight × base_trust. | Computed via integer arithmetic (fixed-point or rational) to guarantee bit-identical output on every architecture. |

**Table 3. Classification Constants**

| Constant | Function |
|---|---|
| `_BENIGNITY_KEYWORDS` | Lexicon of contextual markers that reduce suspicion (e.g., legitimate system updates). |
| `_GOLDEN_RULE_TYPES` | Catalog of expert heuristics defining impossible or highly improbable cross-artifact combinations. |
| `_STRUCTURAL_MALICE_TYPES` | Taxonomy of evidence that is difficult to forge because it requires kernel- or hardware-level manipulation. |
| `_VERDICT_RANK` | Ordered threat levels, from informational to critical. |

### Glossary

| Term | Definition |
|---|---|
| Artifact | A discrete, tool-extracted unit of forensic information. |
| Fracture | A cross-artifact discrepancy indicating logical or temporal inconsistency. |
| Spoofability | The adversarial cost required to fabricate a given evidence type without leaving higher-integrity traces. |
| Deterministic Integer Arithmetic | Mathematical operations on whole numbers or exact rationals, ensuring identical results on any hardware. |
| Noisy-OR Fusion | A deterministic adaptation of probabilistic evidence combination, wherein concordant artifacts increase confidence via additive integer accumulation and fractures impose subtractive bounds. |
| Golden Forensic Rules | Domain-expert constraints that flag physically or logically impossible evidence pairings. |

> **【Scientific Note】**
> Terms such as *artifact*, *fracture*, and *incongruence* are drawn from the semiotic traditions of Charles Sanders Peirce, Umberto Eco, and H. Paul Grice. They are **not** mystical or metaphysical constructs. Within CAIE, they operate exactly like sensor calibration in experimental physics: a forensic *artifact* is analogous to a sensor reading; a *fracture* is a mismatch between two sensors observing the same phenomenon; and *incongruence* is the quantified deviation that triggers a recalibration alert. Semiotics, in this context, is merely the controlled vocabulary of signal interpretation.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## ESPAÑOL

### ¿Qué es este módulo?
El Motor de Incongruencia entre Artefactos Cruzados (CAIE, por sus siglas en inglés) es un sistema de inferencia forense determinista. Ingesta evidencia digital heterogénea—como volcados de memoria, registros de eventos y trazas de red—y la evalúa en una escala única y rigurosamente calibrada. El módulo trata cada elemento de evidencia como un sensor semiótico: algunos sensores son fácilmente suplantables (por ejemplo, una dirección IP), mientras que otros exigen la compromiso profundo del sistema (por ejemplo, un objeto del kernel). CAIE asigna mayor peso inferencial a la evidencia estructuralmente irrefutable, detecta contradicciones entre fuentes independientes y fusiona los hallazgos en un veredicto reproducible mediante aritmética entera exacta.

### Conceptos Clave

**Tabla 1. Entidades Fundamentales**

| Concepto | Significado científico | Rol en la tubería de análisis |
|---|---|---|
| `EvidenceProfile` | Registro de calibración que define el costo de fabricación (suplantabilidad) y la prioridad investigativa de una clase de evidencia. | Normaliza mediciones heterogéneas en una escala determinista unificada. |
| `Artifact` | Una medición forense individual producida por una herramienta VIGIA (p. ej., un handle de memoria o una entrada de registro). | Funciona como dato bruto para la validación y ponderación. |
| `Fracture` | Una ruptura lógica entre dos artefactos que deberían describir el mismo estado pero no concuerdan. | Indica posible manipulación, error de recolección o engaño adversarial. |
| `CrossArtifactIncongruenceEngine` | Controlador central que ingiere artefactos, identifica fracturas y emite un veredicto fusionado. | Orquesta el flujo de trabajo de inferencia determinista. |

**Tabla 2. Fórmula de ponderación determinista**

| Símbolo | Interpretación científica | Implementación determinista |
|---|---|---|
| raw_score | Métrica de sospecha inicial reportada por la herramienta origen. | Almacenado como entero escalado; sin representación inexacta. |
| spoofability | Facilidad estimada de fabricación (0 = irrefutable, 1 = trivialmente falsificable). | Expresada como racional exacto; toda multiplicación usa lógica de numerador/denominador enteros. |
| weight | Importancia investigativa asignada por el examinador o la política. | Estrictamente entero para preservar la conmutatividad entre plataformas. |
| base_trust | Confianza en el instrumento de recolección. | Factor de escala entero. |
| adjusted_score | Valor ponderado final: raw_score × (1 − spoofability) × weight × base_trust. | Calculado mediante aritmética entera (punto fijo o racional) para garantizar salidas idénticas bit a bit en toda arquitectura. |

**Tabla 3. Constantes de clasificación**

| Constante | Función |
|---|---|
| `_BENIGNITY_KEYWORDS` | Léxico de marcadores contextuales que reducen la sospecha (p. ej., actualizaciones legítimas del sistema). |
| `_GOLDEN_RULE_TYPES` | Catálogo de heurísticas expertas que definen combinaciones artefacto-cruzado imposibles o altamente improbables. |
| `_STRUCTURAL_MALICE_TYPES` | Taxonomía de evidencia difícil de falsificar porque requiere manipulación a nivel de kernel o hardware. |
| `_VERDICT_RANK` | Niveles de amenaza ordenados, de informativo a crítico. |

### Glosario

| Término | Definición |
|---|---|
| Artefacto | Unidad discreta de información forense extraída por una herramienta. |
| Fractura | Discrepancia entre artefactos que indica inconsistencia lógica o temporal. |
| Suplantabilidad | Costo adversarial requerido para fabricar un tipo de evidencia sin dejar rastros de mayor integridad. |
| Aritmética entera determinista | Operaciones matemáticas sobre números enteros o racionales exactos, asegurando resultados idénticos en cualquier hardware. |
| Fusión Noisy-OR | Adaptación determinista de la combinación probabilística de evidencias, donde artefactos concordantes incrementan la confianza mediante acumulación entera aditiva y las fracturas imponen límites sustractivos. |
| Reglas Doradas Forenses | Restricciones de dominio experto que señalan emparejamientos de evidencia física o lógicamente imposibles. |

> **【Nota Científica】**
> Términos como *artefacto*, *fractura* e *incongruencia* provienen de las tradiciones semióticas de Charles Sanders Peirce, Umberto Eco y H. Paul Grice. **No** son construcciones místicas ni metafísicas. Dentro de CAIE, operan exactamente como la calibración de sensores en física experimental: un *artefacto* forense es análogo a la lectura de un sensor; una *fractura* es la falta de coincidencia entre dos sensores que observan el mismo fenómeno; y la *incongruencia* es la desviación cuantificada que dispara una alerta de recalibración. La semiótica, en este contexto, es simplemente el vocabulario controlado de la interpretación de señales.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## РУССКИЙ

### Что представляет собой этот модуль?
Межартефактный движок несоответствия (CAIE) — это детерминированная судебно-экспертная система вывода. Он принимает разнородную цифровую улику — снимки памяти, журналы событий, сетевые записи — и оценивает их по единой строго откалиброванной шкале. Модуль рассматривает каждый элемент улики как семиотический датчик: одни датчики легко подделать (например, IP-адрес), тогда как другие требуют глубокого компрометации системы (например, объект ядра). CAIE назначает больший инференциальный вес структурно неопровержимым уликам, выявляет противоречия между независимыми источниками и объединяет результаты в воспроизводимый вердикт с помощью точной целочисленной арифметики.

### Ключевые понятия

**Таблица 1. Основные сущности**

| Понятие | Научное значение | Роль в конвейере анализа |
|---|---|---|
| `EvidenceProfile` | Калибровочная запись, определяющая стоимость подделки (spoofability) и следственный приоритет класса улики. | Нормализует гетерогенные измерения на единую детерминированную шкалу. |
| `Artifact` | Отдельное судебное измерение, произведённое инструментом VIGIA (например, дескриптор памяти или запись журнала). | Служит исходным данным для валидации и взвешивания. |
| `Fracture` | Логический разрыв между двумя артефактами, которые должны описывать одно состояние, но не согласуются. | Сигнализирует о возможном вмешательстве, ошибке сбора или противоборстве злоумышленника. |
| `CrossArtifactIncongruenceEngine` | Центральный контроллер, поглощающий артефакты, выявляющий разрывы и выдающий интегральный вердикт. | Оркестрирует детерминированный инференциальный процесс. |

**Таблица 2. Детерминированная формула взвешивания**

| Символ | Научная интерпретация | Детерминированная реализация |
|---|---|---|
| raw_score | Исходная метрика подозрительности, сообщённая исходным инструментом. | Хранится как масштабированное целое; без приближённого представления. |
| spoofability | Оценочная лёгкость подделки (0 = неопровержимо, 1 = тривиально фальсифицируется). | Выражена точным рациональным числом; все умножения выполняются над целыми числителем/знаменателем. |
| weight | Следственная значимость, назначенная экспертом или политикой. | Строго целое число для сохранения коммутативности на всех платформах. |
| base_trust | Доверие к самому инструменту сбора. | Целочисленный масштабирующий коэффициент. |
| adjusted_score | Итоговое взвешенное значение: raw_score × (1 − spoofability) × weight × base_trust. | Вычисляется целочисленной арифметикой (фиксированной точки или рациональной), гарантируя побитово идентичный результат на любой архитектуре. |

**Таблица 3. Константы классификации**

| Константа | Функция |
|---|---|
| `_BENIGNITY_KEYWORDS` | Лексикон контекстных маркеров, снижающих подозрительность (например, легитимные обновления системы). |
| `_GOLDEN_RULE_TYPES` | Каталог эвристик экспертов, определяющих невозможные или крайне маловероятные межартефактные сочетания. |
| `_STRUCTURAL_MALICE_TYPES` | Таксономия улик, трудных для подделки, так как они требуют манипуляций на уровне ядра или оборудования. |
| `_VERDICT_RANK` | Упорядоченные уровни угрозы, от информационного до критического. |

### Глоссарий

| Термин | Определение |
|---|---|
| Артефакт | Дискретная единица судебной информации, извлечённая инструментом. |
| Разрыв (Fracture) | Межартефактное несоответствие, указывающее на логическую или временную несогласованность. |
| Спуфабилити (Spoofability) | Затраты злоумышленника на подделку данного типа улики без оставления следов высокой целостности. |
| Детерминированная целочисленная арифметика | Математические операции над целыми числами или точными рационалями, обеспечивающие идентичные результаты на любом оборудовании. |
| Noisy-OR слияние | Детерминированная адаптация вероятностной модели комбинирования улик: согласующиеся артефакты наращивают уверенность аддитивным целочисленным накоплением, а разрывы вводят субтрактивные ограничения. |
| Золотые судебные правила | Экспертные ограничения предметной области, маркирующие физически или логически невозможные пары улик. |

> **【Научное примечание】**
> Термины «артефакт», «разрыв» и «несоответствие» происходят из семиотических традиций Чарльза Сандерса Пирса, Умберто Эко и Х. Пола Грайса. Это **не** мистические или метафизические конструкты. В рамках CAIE они функционируют точно так же, как калибровка датчиков в экспериментальной физике: судебный *артефакт* аналогичен показанию датчика; *разрыв* — это рассогласование двух датчиков, наблюдающих одно явление; а *несоответствие* — количественное отклонение, инициирующее сигнал перекалибровки. Семиотика в данном контексте является лишь контролируемым словарём интерпретации сигналов.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## 中文

### 这是什么模块？
跨取证工件不一致引擎（CAIE）是一个确定性的数字取证推理系统。它摄取各类数字证据——如内存快照、事件日志与网络记录——并在单一、严格校准的尺度上进行评估。本模块将每一项证据视为一个符号学传感器：某些传感器极易被欺骗（例如IP地址），而另一些则需要深度系统入侵才能伪造（例如内核对象）。CAIE对结构性无可辩驳的证据赋予更高的推理权重，检测独立来源之间的矛盾，并运用精确的整数运算将结果融合为可复现的裁决。

### 关键概念

**表 1. 核心实体**

| 概念 | 科学含义 | 在分析流程中的作用 |
|---|---|---|
| `EvidenceProfile` | 记录某一类证据的伪造成本（可欺骗性）与调查优先级的校准表。 | 将异构测量归一化到统一的确定性尺度。 |
| `Artifact` | 由VIGIA工具产生的单一取证测量值（如内存句柄或日志条目）。 | 作为待验证与加权的原始输入数据。 |
| `Fracture` | 两个本应描述同一状态却不一致的取证工件之间的逻辑断裂。 | 表明可能存在篡改、采集错误或对抗性欺骗。 |
| `CrossArtifactIncongruenceEngine` | 摄取取证工件、识别逻辑断裂并输出融合裁决的中央控制器。 | 编排确定性推理工作流。 |

**表 2. 确定性加权公式**

| 符号 | 科学解释 | 确定性实现方式 |
|---|---|---|
| raw_score | 来源工具报告的初始可疑度指标。 | 以缩放整数存储；不存在近似表示。 |
| spoofability | 估计的伪造难度（0 = 无可辩驳；1 = 极易伪造）。 | 以精确有理数表示；所有乘法使用整数分子/分母逻辑。 |
| weight | 由检查员或策略分配的调查重要性。 | 严格为整数，以在各平台间保持交换律。 |
| base_trust | 对采集工具本身的信任度。 | 整数比例因子。 |
| adjusted_score | 最终加权值：raw_score × (1 − spoofability) × weight × base_trust。 | 通过整数运算（定点或有理数）计算，保证在任何架构上输出逐位相同。 |

**表 3. 分类常量**

| 常量 | 功能 |
|---|---|
| `_BENIGNITY_KEYWORDS` | 降低可疑度的上下文标记词典（如合法的系统更新）。 |
| `_GOLDEN_RULE_TYPES` | 定义不可能或极不可能的跨取证工件组合的专家启发规则目录。 |
| `_STRUCTURAL_MALICE_TYPES` | 难以伪造的证据分类，因为伪造需要内核级或硬件级操作。 |
| `_VERDICT_RANK` | 按从信息性到关键性排列的有序威胁级别。 |

### 词汇表

| 术语 | 定义 |
|---|---|
| 取证工件 | 由工具提取的离散取证信息单元。 |
| 逻辑断裂 | 表明逻辑或时间不一致的跨取证工件差异。 |
| 可欺骗性（Spoofability） | 在不留下更高完整性痕迹的情况下伪造给定证据类型所需的对抗性成本。 |
| 确定性整数运算 | 对整数或精确有理数进行数学运算，确保在任何硬件上结果相同。 |
| Noisy-OR 融合 | 概率证据组合的确定性改编：一致性取证工件通过加法整数累积增加置信度，而逻辑断裂施加减法上界。 |
| 黄金取证规则 | 标记物理上或逻辑上不可能的证据配对的领域专家约束。 |

> **【科学说明】**
> "取证工件"、"逻辑断裂"和"不协调"等术语源自查尔斯·桑德斯·皮尔士、**艾柯**（Umberto Eco）和**格赖斯**（H. Paul Grice）的符号学传统。这些**不是**神秘或形而上学的构念。在 CAIE 中，它们的工作方式与实验物理中的传感器校准完全一样：取证*工件*类似于传感器读数；*逻辑断裂*是两个观察同一现象的传感器之间的不匹配；*不协调*是触发重新校准警报的量化偏差。符号学在此语境下仅是信号解读的受控词汇表。

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
