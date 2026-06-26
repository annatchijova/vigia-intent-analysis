<!--
VIGIA Academic Documentation
Module: 69cb51de
Batch ID: vigia-doc-0083-69cb51de
Generated: 2026-05-20T14:56:47.862439+00:00
-->

---

## ENGLISH

### What Is This Module?
`vigia_scorer.py` is a deterministic forensic scoring submodule of the VIGÍA suite. It evaluates digital artifact intentionality through strict rule-based logic, yielding reproducible metrics for incident response. Developed for the SANS FIND EVIL Hackathon 2026, it is a candidate for integration into the SANS SIFT Workstation. All scoring uses exact integer arithmetic; no probabilistic thresholds are applied. Licensed under the Apache License, Version 2.0.

### Key Concepts

| Concept | Definition | Technical Role |
|---|---|---|
| **Forensic Intentionality** | The property of a digital artifact indicating deliberate, purposeful action rather than accidental occurrence. | The primary subject of scoring; distinguishes attacker artifacts from benign noise. |
| **Deterministic Scoring** | A scoring system where identical inputs always produce identical scores through exact integer computation. | Eliminates stochastic variance; ensures reproducibility across audits. |
| **Rule-Based Evaluation** | Logical decision procedures governed by explicit, verifiable conditions rather than learned statistical weights. | Each score increment is traceable to a specific, documented rule. |
| **Incident Response Metric** | A quantitative indicator used by analysts to prioritize investigation resources. | Produced by the scorer to guide triage of multiple concurrent alerts. |
| **SIFT Workstation** | The SANS-recognized forensic Linux distribution; the target deployment environment. | Provides the operational context for artifact analysis in live investigations. |

> **【Scientific Note】**
> Peirce/Eco/Grice terminology is NOT mysticism. In VIGÍA, forensic intentionality scoring is a direct application of Peircean *Thirdness*: the module identifies the repeatable behavioral law—the signature of deliberate choice—that distinguishes malicious artifacts from coincidental ones. Grice's maxim of quality demands that each score increment be grounded in verifiable evidence, not assumption.

### Glossary
1. **Deterministic Scoring** — A scoring system producing identical results for identical inputs through exact integer computation.
2. **Digital Artifact** — Any file, log entry, or system trace with investigative value.
3. **Forensic Intentionality** — The inferred property of deliberate, purposeful action encoded in a digital artifact.
4. **Hackathon Prototype** — A functional system developed within a competitive coding event; this module was built for SANS FIND EVIL 2026.
5. **Incident Response** — The structured process of detecting, analyzing, and containing security incidents.
6. **Reproducible Metric** — A quantitative result that any analyst with the same input data will independently compute to be identical.
7. **Rule-Based Logic** — Decision procedures governed by explicit, human-readable conditions rather than statistical models.
8. **SANS FIND EVIL** — The 2026 forensic hackathon event for which this module was developed.
9. **SIFT Workstation** — The SANS-recognized Linux distribution for digital forensic investigations.
10. **VIGÍA Suite** — The integrated platform for forensic intentionality analysis of which this scorer is a component.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## ESPAÑOL

### ¿Qué es este módulo?
`vigia_scorer.py` es un submódulo forense de puntuación determinista del conjunto VIGÍA. Evalúa la intencionalidad de artefactos digitales mediante lógica estricta basada en reglas, produciendo métricas reproducibles para respuesta a incidentes. Desarrollado para el SANS FIND EVIL Hackathon 2026, es candidato a integrarse en SANS SIFT Workstation. Toda la puntuación usa aritmética entera exacta; no se aplican umbrales probabilísticos. Apache License, Version 2.0.

### Conceptos clave

| Concepto | Definición | Rol técnico |
|---|---|---|
| **Intencionalidad Forense** | Propiedad de un artefacto digital que indica acción deliberada y con propósito en lugar de ocurrencia accidental. | Tema principal de la puntuación; distingue artefactos de atacante del ruido benigno. |
| **Puntuación Determinista** | Sistema de puntuación donde entradas idénticas siempre producen puntuaciones idénticas mediante cómputo entero exacto. | Elimina varianza estocástica; garantiza reproducibilidad entre auditorías. |
| **Evaluación Basada en Reglas** | Procedimientos de decisión lógica gobernados por condiciones explícitas y verificables en lugar de pesos estadísticos aprendidos. | Cada incremento de puntuación es rastreable a una regla específica y documentada. |
| **Métrica de Respuesta a Incidentes** | Indicador cuantitativo utilizado por analistas para priorizar recursos de investigación. | Producida por el evaluador para guiar el triaje de múltiples alertas concurrentes. |
| **SIFT Workstation** | Distribución Linux forense reconocida por SANS; el entorno de despliegue objetivo. | Proporciona el contexto operacional para el análisis de artefactos en investigaciones en vivo. |

> **【Nota Científica】**
> La terminología de Peirce/Eco/Grice no es misticismo. En VIGÍA, la puntuación de intencionalidad forense es una aplicación directa de la *Terceridad* peirceana: el módulo identifica la ley conductual repetible que distingue artefactos maliciosos de los coincidentales. La máxima de calidad de Grice exige que cada incremento de puntuación esté fundamentado en evidencia verificable.

### Glosario
1. **Puntuación Determinista** — Sistema de puntuación que produce resultados idénticos para entradas idénticas mediante cómputo entero exacto.
2. **Artefacto Digital** — Cualquier archivo, entrada de registro o traza del sistema con valor investigativo.
3. **Intencionalidad Forense** — Propiedad inferida de acción deliberada y con propósito codificada en un artefacto digital.
4. **Prototipo Hackathon** — Sistema funcional desarrollado en un evento competitivo de programación; este módulo se construyó para SANS FIND EVIL 2026.
5. **Respuesta a Incidentes** — Proceso estructurado de detección, análisis y contención de incidentes de seguridad.
6. **Métrica Reproducible** — Resultado cuantitativo que cualquier analista con los mismos datos de entrada calculará de forma independiente como idéntico.
7. **Lógica Basada en Reglas** — Procedimientos de decisión gobernados por condiciones explícitas y legibles por humanos en lugar de modelos estadísticos.
8. **SANS FIND EVIL** — El evento hackathon forense 2026 para el que se desarrolló este módulo.
9. **SIFT Workstation** — Distribución Linux reconocida por SANS para investigaciones forenses digitales.
10. **Conjunto VIGÍA** — La plataforma integrada de análisis de intencionalidad forense de la que este evaluador es componente.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## РУССКИЙ

### Что это за модуль?
`vigia_scorer.py` — детерминированный криминалистический подмодуль оценивания набора VIGÍA. Он оценивает интенциональность цифровых артефактов посредством строгой правило-основанной логики, формируя воспроизводимые метрики реагирования на инциденты. Разработан для хакатона SANS FIND EVIL 2026, кандидат на интеграцию в SANS SIFT Workstation. Всё оценивание использует точную целочисленную арифметику; вероятностные пороги не применяются. Apache License, Version 2.0.

### Ключевые концепции

| Концепция | Определение | Техническая роль |
|---|---|---|
| **Криминалистическая интенциональность** | Свойство цифрового артефакта, указывающее на намеренное, целенаправленное действие, а не случайное возникновение. | Основной предмет оценивания; отличает артефакты злоумышленника от доброкачественного шума. |
| **Детерминированное оценивание** | Система оценивания, при которой одинаковые входные данные всегда дают одинаковые оценки через точное целочисленное вычисление. | Исключает стохастическую дисперсию; обеспечивает воспроизводимость между аудитами. |
| **Оценка на основе правил** | Процедуры логического решения, управляемые явными, верифицируемыми условиями. | Каждый прирост оценки отслеживается к конкретному задокументированному правилу. |
| **Метрика реагирования на инциденты** | Количественный индикатор, используемый аналитиками для приоритизации следственных ресурсов. | Производится оценщиком для руководства триажем нескольких одновременных предупреждений. |
| **SIFT Workstation** | Признанный SANS криминалистический Linux-дистрибутив; целевая среда развёртывания. | Обеспечивает операционный контекст для анализа артефактов в живых расследованиях. |

> **【Научное примечание】**
> Терминология Пирса, Эко и Грайса — не мистика. В VIGÍA оценивание криминалистической интенциональности является прямым применением пирсовской *Третичности*: модуль выявляет повторяющийся поведенческий закон — сигнатуру намеренного выбора — отличающий вредоносные артефакты от случайных. Максима качества Грайса требует, чтобы каждый прирост оценки был обоснован верифицируемыми доказательствами.

### Глоссарий
1. **Детерминированное оценивание** — Система оценивания, производящая идентичные результаты для идентичных входных данных через точное целочисленное вычисление.
2. **Цифровой артефакт** — Любой файл, запись журнала или системный след, обладающий следственной ценностью.
3. **Криминалистическая интенциональность** — Выводимое свойство намеренного, целенаправленного действия, закодированного в цифровом артефакте.
4. **Хакатонный прототип** — Функциональная система, разработанная на соревновательном мероприятии; данный модуль создан для SANS FIND EVIL 2026.
5. **Реагирование на инциденты** — Структурированный процесс обнаружения, анализа и сдерживания инцидентов безопасности.
6. **Воспроизводимая метрика** — Количественный результат, который любой аналитик с теми же входными данными независимо вычислит идентично.
7. **Правило-основанная логика** — Процедуры принятия решений, управляемые явными, удобочитаемыми условиями, а не статистическими моделями.
8. **SANS FIND EVIL** — Криминалистический хакатон 2026 года, для которого был разработан данный модуль.
9. **SIFT Workstation** — Признанный SANS Linux-дистрибутив для цифровых криминалистических расследований.
10. **Набор VIGÍA** — Интегрированная платформа криминалистического анализа интенциональности, компонентом которой является данный оценщик.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## 中文

### 这是什么模块？
`vigia_scorer.py` 是 VIGÍA 套件中的确定性取证评分子模块。它基于严格的规则逻辑评估数字工件的意图性，为事件响应生成可复现指标。为 2026 年 SANS FIND EVIL 黑客松开发，拟集成至 SANS SIFT 工作站。所有评分使用精确整数运算；不应用概率阈值。采用 Apache 2.0 许可证。

### 关键概念

| 概念 | 定义 | 技术作用 |
|---|---|---|
| **取证意图性** | 数字工件所具有的表明蓄意、有目的行动而非偶然发生的属性。 | 评分的主要对象；区分攻击者工件与良性噪声。 |
| **确定性评分** | 通过精确整数计算，相同输入始终产生相同评分的评分系统。 | 消除随机方差；确保跨审计的可复现性。 |
| **规则评估** | 由明确可验证条件而非统计权重驱动的逻辑决策过程。 | 每个评分增量均可追溯至特定已记录规则。 |
| **事件响应指标** | 分析员用于优先分配调查资源的量化指标。 | 由评分器产生，用于指导多个并发警报的分类。 |
| **SIFT 工作站** | SANS 认可的取证 Linux 发行版；目标部署环境。 | 为实时调查中的取证工件分析提供操作上下文。 |

> **【科学说明】**
> 皮尔斯、艾柯和格赖斯的术语并非神秘主义。在 VIGÍA 中，取证意图性评分是皮尔斯*第三性*的直接应用：该模块识别出将恶意工件与偶然工件区分开来的可重复行为规律——蓄意选择的特征。格赖斯的质量准则要求每个评分增量都基于可验证的证据，而非假设。

### 词汇表
1. **确定性评分** — 通过精确整数计算对相同输入产生相同结果的评分系统。
2. **数字工件** — 具有调查价值的任何文件、日志条目或系统痕迹。
3. **取证意图性** — 数字工件中编码的蓄意、有目的行动的推断属性。
4. **黑客松原型** — 在竞争性编程活动中开发的功能系统；本模块为 SANS FIND EVIL 2026 构建。
5. **事件响应** — 检测、分析和遏制安全事件的结构化流程。
6. **可复现指标** — 任何拥有相同输入数据的分析员都将独立计算得出相同结果的量化结果。
7. **规则逻辑** — 由明确人类可读条件而非统计模型驱动的决策过程。
8. **SANS FIND EVIL** — 本模块为之开发的 2026 年取证黑客松活动。
9. **SIFT 工作站** — SANS 认可的数字取证调查 Linux 发行版。
10. **VIGÍA 套件** — 本评分器所属的取证意图性分析集成平台。

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
