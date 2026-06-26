<!--
VIGIA Academic Documentation
Module: 8c5d9283
Batch ID: vigia-doc-0001-8c5d9283
Generated: 2026-05-20T14:56:47.845109+00:00
-->

## ENGLISH

### What Is This Module?
The Cross-Artifact Incongruence Engine (CAIE) is a deterministic forensic inference instrument. It operates like a correlation laboratory for digital evidence: multiple forensic tools act as independent sensors, each emitting an **Artifact** (a measurement). CAIE registers each artifact's origin, calibrates its trustworthiness through an **EvidenceProfile**, and searches for **Fractures**—logical contradictions between artifacts that should agree. The engine then fuses all valid artifacts into a final verdict using exact integer arithmetic, guaranteeing that two scientists running the same data on different computers receive bitwise-identical results.

### Key Concepts

**Table 1. Core Entities**

| Term | Scientific Meaning | Role in Investigation |
|---|---|---|
| **EvidenceProfile** | A calibrated descriptor that encodes an evidence type's resistance to fabrication (*spoofability*) and its structural priority (*weight*). | Pre-calibrates sensor reliability before data ingestion. |
| **Artifact** | A single forensic measurement produced by a VIGIA tool, packaged with its source identity, raw score, and profile. | The atomic observation, analogous to a single sensor reading. |
| **Fracture** | A logical discrepancy between two artifacts expected to be consistent (e.g., logs report a remote login while RAM contains no corresponding process object). | Indicates anti-forensic tampering, tool error, or undocumented system behavior. |
| **CrossArtifactIncongruenceEngine (CAIE)** | The central controller that ingests artifacts, detects fractures via Golden Forensic Rules, and fuses findings into a verdict. | Correlates multi-instrument readings into a unified laboratory report. |
| **Golden Forensic Rules** | Immutable integrity constraints that define how distinct evidence types must relate across a valid system state. | Function as conservation laws: a violation proves at least one measurement is inauthentic. |

**Table 2. Deterministic Scoring Parameters (Integer Arithmetic)**

| Parameter | Domain | Scientific Definition |
|---|---|---|
| `raw_score` | Integer (0–1000) | Initial suspicion level from the source tool, expressed in thousandths to avoid fractions. |
| `spoofability` | Integer (0–1000) | Ease of forging this evidence type (0 = structurally impossible; 1000 = trivially spoofed). |
| `weight` | Positive integer | Structural importance assigned by the investigator or policy. |
| `base_trust` | Integer (0–1000) | Calibration constant for the source tool's historical accuracy. |
| `adjusted_score` | Computed integer | Exact rational product: `raw_score × (1000 − spoofability) × weight × base_trust`, followed by fixed scaling. Identical on every CPU architecture. |

### Glossary

| Term | Definition |
|---|---|
| **Determinism** | The property that a computation yields the exact same bit pattern on every execution and every hardware platform, given identical inputs. Enforced here by eliminating floating-point operations and using scaled integer rational arithmetic. |
| **Spoofability** | The empirical likelihood (expressed as integer per mille) that an attacker can fabricate an evidence type without detectable residue. |
| **Volatile Memory Artifact** | Evidence extracted from live RAM. Intrinsically low spoofability because fabrication requires active kernel compromise. |
| **Noisy-OR Fusion (Deterministic)** | A probabilistic evidence-fusion model implemented via integer logarithms or precomputed rational tables, combining independent artifact scores without floating-point uncertainty. |
| **Anti-Forensics** | Deliberate adversarial actions to alter, conceal, or falsify digital evidence. |
| **Golden Forensic Rules** | Axiomatic cross-artifact consistency requirements. A violation denotes an invalid system state or tampered data. |

> **【Scientific Note】Peirce, Eco, Grice: Semiotics as Sensor Fusion**
> The semiotic vocabulary of CAIE is occasionally mistaken for literary mysticism. It is rigorous analytical philosophy applied to engineering. **Charles Sanders Peirce** defined the logic of signs: a sign is anything that stands for something else—just as a voltage reading stands for temperature. **Umberto Eco** formalized the codes that map raw signals to meaning, precisely as a calibration curve maps ADC counts to physical units. **H. P. Grice** articulated the cooperative maxims that make communication possible—analogous to the data-link protocols that allow sensors to transmit parseable measurements. A **Fracture** is therefore nothing more than a sign-system malfunction: the smoke detector asserts "fire" while the thermal detector asserts "ambient." CAIE treats these frameworks as deterministic engineering constraints, ensuring forensic interpretation remains a reproducible physical science.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## ESPAÑOL

### ¿Qué es este módulo?
El Motor de Incongruencia Trans-Artefacto (CAIE, por sus siglas en inglés) es un instrumento forense de inferencia determinista. Funciona como un laboratorio de correlación para evidencia digital: múltiples herramientas forenses actúan como sensores independientes que emiten un **Artefacto** (una medición). CAIE registra el origen de cada artefacto, calibra su confiabilidad mediante un **Perfil de Evidencia**, y busca **Fracturas**—contradicciones lógicas entre artefactos que deberían concordar. El motor fusiona todos los artefactos válidos en un veredicto final usando aritmética entera exacta, garantizando que dos científicos que analicen los mismos datos en computadoras distintas obtengan resultados idénticos bit a bit.

### Conceptos Clave

**Tabla 1. Entidades Fundamentales**

| Término | Significado Científico | Rol en la Investigación |
|---|---|---|
| **Perfil de Evidencia** (*EvidenceProfile*) | Descriptor calibrado que codifica la resistencia al montaje (*falsificabilidad*) de un tipo de evidencia y su prioridad estructural (*peso*). | Pre-calibra la confiabilidad del sensor antes de la ingestión de datos. |
| **Artefacto** (*Artifact*) | Medición forense individual producida por una herramienta VIGIA, empaquetada con su identidad de origen, puntuación bruta y perfil. | Observación atómica, análoga a una única lectura de sensor. |
| **Fractura** (*Fracture*) | Discrepancia lógica entre dos artefactos que se espera sean consistentes (p. ej., los registros indican un inicio de sesión remoto mientras la RAM no contiene el proceso correspondiente). | Indica manipulación anti-forense, error de herramienta o comportamiento del sistema no documentado. |
| **Motor CAIE** (*CrossArtifactIncongruenceEngine*) | Controlador central que ingiere artefactos, detecta fracturas mediante las Reglas Doradas Forenses y fusiona los hallazgos en un veredicto. | Correlaciona lecturas multi-instrumento en un informe de laboratorio unificado. |
| **Reglas Doradas Forenses** | Restricciones inmutables de integridad que definen cómo deben relacionarse distintos tipos de evidencia en un estado válido del sistema. | Funcionan como leyes de conservación: una violación demuestra que al menos una medición es inauténtica. |

**Tabla 2. Parámetros del Modelo de Puntuación Determinista (Aritmética Entera)**

| Parámetro | Dominio | Definición Científica |
|---|---|---|
| `raw_score` | Entero (0–1000) | Nivel inicial de sospecha reportado por la herramienta origen, expresado en milésimas para evitar fracciones. |
| `spoofability` | Entero (0–1000) | Facilidad de falsificar este tipo de evidencia (0 = estructuralmente imposible; 1000 = trivialmente suplantable). |
| `weight` | Entero positivo | Importancia estructural asignada por el investigador o la política institucional. |
| `base_trust` | Entero (0–1000) | Constante de calibración para la precisión histórica de la herramienta origen. |
| `adjusted_score` | Entero calculado | Producto racional exacto: `raw_score × (1000 − spoofability) × weight × base_trust`, con escalamiento fijo. Idéntico en toda arquitectura de CPU. |

### Glosario

| Término | Definición |
|---|---|
| **Determinismo** | Propiedad por la cual un cálculo produce exactamente el mismo patrón de bits en cada ejecución y en cada plataforma de hardware, dados insumos idénticos. Aquí se impone eliminando operaciones de coma flotante y usando aritmética racional de enteros escalados. |
| **Falsificabilidad / Spoofability** | Probabilidad empírica (expresada como entero por mil) de que un atacante fabrique un tipo de evidencia sin dejar residuos detectables. |
| **Artefacto de Memoria Volátil** | Evidencia extraída de la RAM viva. Intrínsecamente de baja falsificabilidad porque su montaje requiere compromiso activo del núcleo del sistema. |
| **Fusión Noisy-OR (Determinista)** | Modelo probabilístico de fusión de evidencia implementado mediante logaritmos enteros o tablas racionales precomputadas, combinando puntuaciones independientes sin incertidumbre de coma flotante. |
| **Anti-Forense** | Acciones adversariales deliberadas para alterar, ocultar o falsificar evidencia digital. |
| **Reglas Doradas Forenses** | Requisitos axiomáticos de consistencia entre artefactos. Una violación denota un estado de sistema inválido o datos manipulados. |

> **【Nota Científica】Peirce, Eco, Grice: La semiótica como fusión de sensores**
> El vocabulario semiótico de CAIE es ocasionalmente confundido con misticismo literario. Es filosofía analítica rigurosa aplicada a la ingeniería. **Charles Sanders Peirce** definió la lógica de los signos: un signo es todo aquello que representa otra cosa—exactamente como un voltaje representa temperatura. **Umberto Eco** formalizó los códigos que mapean señales brutas a significado, precisamente como una curva de calibración mapea cuentas de ADC a unidades físicas. **H. P. Grice** articuló los máximas cooperativas que hacen posible la comunicación—análogos a los protocolos de enlace de datos que permiten a los sensores transmitir mediciones analizables. Una **Fractura** no es, por tanto, más que un fallo del sistema de signos: el detector de humo afirma "fuego" mientras el detector térmico afirma "ambiente". CAIE trata estos marcos teóricos como restricciones de ingeniería deterministas, asegurando que la interpretación forense permanezca como ciencia física reproducible.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## РУССКИЙ

### Что представляет собой этот модуль?
Межартефактный Движок Несоответствий (CAIE) — это детерминистский судебно-экспертный инструмент для логического вывода. Он работает как корреляционная лаборатория для цифровых доказательств: множественные судебные инструменты выступают в роли независимых датчиков, каждый из которых генерирует **Артефакт** (измерение). CAIE регистрирует происхождение каждого артефакта, калибрует его достоверность посредством **Профиля Доказательства** и обнаруживает **Разломы** — логические противоречия между артефактами, которые должны согласовываться. Затем движок объединяет все валидные артефакты в итоговое заключение с помощью точной целочисленной арифметики, гарантируя, что два эксперта, обработав одни и те же данные на разных компьютерах, получат идентичные результаты побитово.

### Ключевые понятия

**Таблица 1. Основные сущности**

| Термин | Научное значение | Роль в расследовании |
|---|---|---|
| **Профиль Доказательства** (*EvidenceProfile*) | Калиброванный дескриптор, кодирующий сопротивляемость типа доказательства подделке (*спуфабельность*) и его структурный приоритет (*вес*). | Предварительная калибровка надёжности датчика до поступления данных. |
| **Артефакт** (*Artifact*) | Отдельное судебное измерение, произведённое инструментом VIGIA, включающее идентификатор источника, сырой балл и профиль. | Атомарное наблюдение, аналогичное единичному показанию датчика. |
| **Разлом** (*Fracture*) | Логическое несоответствие между двумя артефактами, которые по условиям должны быть согласованы (например, журналы фиксируют удалённый вход, а ОЗУ не содержит соответствующего процесса). | Сигнал антифорензичной подделки, ошибки инструмента или недокументированного поведения системы. |
| **Движок CAIE** (*CrossArtifactIncongruenceEngine*) | Центральный контроллер, поглощающий артефакты, выявляющий разломы по Золотым Судебным Правилам и объединяющий находки в вердикт. | Коррелирует многоприборные измерения в единый лабораторный отчёт. |
| **Золотые Судебные Правила** | Неизменные ограничения целостности, определяющие, как различные типы доказательств должны взаимосвязоваться в валидном состоянии системы. | Функционируют как законы сохранения: нарушение доказывает, что хотя бы одно измерение неаутентично. |

**Таблица 2. Параметры детерминистической модели оценки (целочисленная арифметика)**

| Параметр | Домен | Научное определение |
|---|---|---|
| `raw_score` | Целое (0–1000) | Начальный уровень подозрительности от исходного инструмента, выраженный в промилле для исключения дробей. |
| `spoofability` | Целое (0–1000) | Лёгкость подделки данного типа доказательства (0 = структурно невозможно; 1000 = тривиально поддельно). |
| `weight` | Положительное целое | Структурная значимость, назначенная исследователем или политикой. |
| `base_trust` | Целое (0–1000) | Калибровочная константа исторической точности исходного инструмента. |
| `adjusted_score` | Вычисляемое целое | Точное рациональное произведение: `raw_score × (1000 − spoofability) × weight × base_trust` с последующим фиксированным масштабированием. Идентично на любой архитектуре ЦПУ. |

### Глоссарий

| Термин | Определение |
|---|---|
| **Детерминизм** | Свойство вычисления, при котором оно порождает абсолютно идентичный битовый паттерн при каждом запуске и на любой аппаратной платформе при одинаковых входных данных. Здесь обеспечивается отказом от операций с плавающей точкой и использованием масштабированной целочисленной рациональной арифметики. |
| **Спуфабельность / Подделываемость** | Эмпирическая вероятность (выраженная целым числом в промилле) того, что злоумышленник сможет сфабриковать тип доказательства без обнаружимых следов. |
| **Артефакт Оперативной Памяти** | Доказательство, извлечённое из ОЗУ. Имеет принципиально низкую спуфабельность, поскольку подделка требует активного компрометации ядра системы. |
| **Детерминистское слияние Noisy-OR** | Вероятностная модель объединения доказательств, реализованная через целочисленные логарифмы или предвычисленные рациональные таблицы, исключающая неопределённость операций с плавающей точкой. |
| **Антифорензика** | Преднамеренные действия противника по изменению, сокрытию или фальсификации цифровых доказательств. |
| **Золотые Судебные Правила** | Аксиоматические требования межартефактной согласованности. Нарушение означает невалидное состояние системы или подмену данных. |

> **【Научное примечание】Пирс, Эко, Грайс: семиотика как слияние сенсоров**
> Семиотическая терминология CAIE иногда ошибочно принимается за литературный мистицизм. Это строгая аналитическая философия, применённая к инженерии. **Чарлз Сандерс Пирс** заложил логику знаков: знак — это всё, что замещает другой объект — точно так же, как напряжение замещает температуру. **Умберто Эко** формализовал коды, отображающие сырые сигналы в значение, в точности как калибровочная кривая отображает отсчёты АЦП в физические единицы. **Г. П. Грайс** сформулировал кооперативные максимы, делающие коммуникацию возможной — аналогично протоколам канального уровня, позволяющим датчикам передавать измерения, пригодные для разбора. **Разлом** есть не что иное, как отказ знаковой системы: дымовой датчик утверждает «пожар», тогда как тепловой датчик утверждает «норма». CAIE рассматривает эти теоретические рамки как детерминистские инженерные ограничения, гарантируя, что судебная интерпретация остаётся воспроизводимой физической наукой.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## 中文

### 这是什么模块？
跨取证工件不协调引擎（CAIE）是一套确定性数字取证推理系统。它如同数字证据的关联实验室：多个取证工具充当独立传感器，各自产生一个**取证工件**（即测量值）。CAIE 记录每个工件的来源，通过**证据轮廓**校准其可信度，并搜寻**逻辑断裂**——即本应一致的工件之间出现的逻辑矛盾。随后，引擎利用精确的整数运算将所有有效工件融合为最终裁决，确保两名科学家在不同计算机上运行同一数据时，获得逐位完全相同的结果。

### 核心概念

**表 1. 核心实体**

| 术语 | 科学含义 | 调查作用 |
|---|---|---|
| **证据轮廓** (*EvidenceProfile*) | 编码某类证据抗伪造能力（可伪造性）与结构优先级（权重）的校准描述符。 | 在数据摄入前预先校准传感器的可靠性。 |
| **取证工件** (*Artifact*) | 由 VIGIA 工具产生的单一取证测量值，含来源标识、原始评分和轮廓。 | 原子级观测值，类比于单次传感器读数。 |
| **逻辑断裂** (*Fracture*) | 两个本应一致的取证工件之间的逻辑矛盾（如日志报告了远程登录，而 RAM 中无对应进程对象）。 | 表明反取证篡改、工具错误或未记录的系统行为。 |
| **跨取证工件不协调引擎 (CAIE)** | 摄取取证工件、通过黄金取证规则检测逻辑断裂、并将结果融合为裁决的中央控制器。 | 将多仪器读数关联整合为统一的实验室报告。 |
| **黄金取证规则** | 定义有效系统状态下各类证据必须如何关联的不可变完整性约束。 | 充当守恒定律：违反即证明至少一项测量不可靠。 |

**表 2. 确定性评分参数（整数运算）**

| 参数 | 范围 | 科学定义 |
|---|---|---|
| `raw_score` | 整数（0–1000） | 来源工具报告的初始可疑度，以千分之一为单位以避免小数。 |
| `spoofability` | 整数（0–1000） | 伪造该类证据的难易程度（0 = 结构上不可能；1000 = 极易伪造）。 |
| `weight` | 正整数 | 由调查人员或策略分配的结构重要性。 |
| `base_trust` | 整数（0–1000） | 来源工具历史准确性的校准常数。 |
| `adjusted_score` | 计算所得整数 | 精确有理数乘积：`raw_score × (1000 − spoofability) × weight × base_trust`，再经固定比例缩放。在任意 CPU 架构上结果完全相同。 |

### 词汇表

| 术语 | 定义 |
|---|---|
| **确定性** | 在相同输入下，计算在每次执行及任何硬件平台上产生完全相同的位模式的属性。通过消除浮点运算、使用缩放整数有理运算来保证。 |
| **可伪造性** | 攻击者在不留可检测残留的情况下伪造某类证据的经验概率（以整数千分之一表示）。 |
| **易失性内存取证工件** | 从活跃 RAM 中提取的证据。由于伪造需要主动的内核级入侵，其可伪造性本质上很低。 |
| **确定性 Noisy-OR 融合** | 通过整数对数或预计算有理数表实现的概率证据融合模型，结合独立工件评分而不引入浮点不确定性。 |
| **反取证** | 对手为篡改、隐藏或伪造数字证据而采取的蓄意行动。 |
| **黄金取证规则** | 公理性跨工件一致性要求。违反即表示系统状态无效或数据已被篡改。 |

> **【科学说明】皮尔士、艾柯、格赖斯：符号学即传感器融合**
> CAIE 的符号学词汇偶尔被误认为文学神秘主义。这是严格的分析哲学在工程中的应用。**查尔斯·桑德斯·皮尔士**定义了符号逻辑：符号是任何代表其他事物的东西——正如电压读数代表温度。**艾柯**（Umberto Eco）形式化了将原始信号映射到意义的编码，正如校准曲线将 ADC 计数映射到物理单位。**格赖斯**（H. P. Grice）阐明了使通信成为可能的合作准则——类似于允许传感器传输可解析测量值的数据链路协议。因此，**逻辑断裂**不过是符号系统的故障：烟雾探测器断言"火灾"，而热传感器断言"正常"。CAIE 将这些框架视为确定性工程约束，确保取证解释保持可复现的物理科学属性。

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
