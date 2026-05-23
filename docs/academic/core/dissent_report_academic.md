<!--
VIGIA Academic Documentation
Module: 5fbbcb8f
Batch ID: vigia-doc-0047-5fbbcb8f
Generated: 2026-05-20T14:56:47.854612+00:00
-->

---
doc_hash: 5fbbcb8f
module: vigia/core/dissent_report.py
languages: [EN, ES, RU, ZH]
generated_by: moonshot-kimi-k2.6-batch-api
license: Apache-2.0
---

ENGLISH:
- Title: DISSENT REPORT MODULE — `vigia/core/dissent_report.py`
- What Is This Module?
  - It's a deterministic classifier aggregator for forensic detection. It collects "opinions" from multiple detection modules (sensors) and identifies when a minority disagrees with the majority. In advanced persistent threat (APT) analysis, a single behavioral module reporting MALICIOUS while nine others report BENIGN is a critical signal, not an error. The module treats consensus as a hypothesis to be tested, not a command.
- Key Concepts Table:
  - ModuleVerdict: The atomic classification produced by one detection engine (MALICIOUS, SUSPICIOUS, BENIGN, ABSTAIN).
  - ModuleOpinion: A verdict bound to its confidence score, expressed as exact rational numbers (Fraction), never approximate decimals.
  - DissentSignal: A minority opinion that survives noise filtering. It is preserved explicitly to prevent evasion via majority agreement.
  - DissentReport: The deterministic output document aggregating all opinions, the majority view, and all dissent signals.
  - Deterministic Scoring: All mathematics performed with Python's fractions.Fraction, ensuring identical inputs always yield identical reports across hardware and time.
  - Integer Display: Human-readable percentages are generated via integer truncation (int()), never rounding, eliminating reproducibility variance.
- Functions/Methods Table:
  - generate_dissent_report(): Orchestrates the creation of the report. Accepts thresholds as Fraction objects to maintain exact arithmetic.
  - display_confidence_pct(): Converts an exact confidence fraction to an integer percentage by truncation.
  - display_majority_pct(): Truncated integer percentage of the majority bloc.
  - display_consensus_pct(): Truncated integer percentage representing overall consensus.
- Constants Table:
  - MALICIOUS: Confirmed threat indicator.
  - SUSPICIOUS: Anomalous but inconclusive.
  - BENIGN: No threat detected.
  - ABSTAIN: Module declined to vote (e.g., insufficient data).
- Glossary:
  - APT (Advanced Persistent Threat): A stealthy, continuous computer hacking process.
  - Determinism: Property of a system where the same input always produces the same output, with no randomness or hardware-dependent variation.
  - Fraction (Python fractions.Fraction): A rational number type representing values exactly as numerator/denominator pairs (e.g., 1/3), avoiding binary floating-point errors.
  - Integer Truncation: Discarding the fractional part of a number without rounding (e.g., 33.99 becomes 33).
  - Consensus Evasion: An attack strategy designed to make a malicious artifact appear benign by exploiting the tendency of majority-voting systems to suppress minority alarms.
  - Sensor Analogy: Treating each software module as an independent physical instrument measuring the same event with different technologies.
- Scientific Note:
  - The terminology of Peirce (abduction), Eco (semiotic threshold), and Grice (cooperative principle / implicature) is sometimes dismissed as metaphysical. In this module, these concepts are operationalized as engineering constraints. Think of a laboratory instrument array: Peircean abduction is hypothesis generation from anomalous sensor readings; Eco's semiotic threshold is the noise floor below which a signal is treated as instrument error; Gricean maxims are communication protocols ensuring each sensor reports the maximal relevant information without redundancy. A dissenting module is not being "difficult" — it is a spectrometer reporting a peak that the other cameras cannot see. Silencing it is methodological failure, not statistical correction.

ESPAÑOL:
- Title: MÓDULO DE REPORTE DE DISENSO — `vigia/core/dissent_report.py`
- Similar structure.
- Key terms:
  - ModuleVerdict -> VeredictoDelMódulo
  - ModuleOpinion -> OpiniónDelMódulo
  - DissentSignal -> SeñalDeDisenso
  - DissentReport -> ReporteDeDisenso
  - Deterministic Scoring -> Puntuación Determinista
  - Integer Display -> Visualización Entera
  - generate_dissent_report() -> genera el reporte
  - display_confidence_pct() -> porcentaje de confianza entero truncado
  - display_majority_pct() -> porcentaje de mayoría truncado
  - display_consensus_pct() -> porcentaje de consenso truncado
  - Constants: MALICIOUS -> MALICIOSO, SUSPICIOUS -> SOSPECHOSO, BENIGN -> BENIGNO, ABSTAIN -> ABSTENCIÓN
- Glossary:
  - APT -> Amenaza Persistentemente Avanzada
  - Determinismo
  - Fraction -> Fracción (Python fractions.Fraction)
  - Truncamiento Entero
  - Evasión por Consenso
  - Analogía del Sensor
- Scientific Note:
  - La terminología de Peirce (abducción), Eco (umbral semiótico) y Grice (principio cooperativo / implicatura) a veces se descarta como metafísica. En este módulo, estos conceptos se operacionalizan como restricciones de ingeniería. Piense en un conjunto de instrumentos de laboratorio: la abducción peirceana es la generación de hipótesis a partir de lecturas anómalas de sensores; el umbral semiótico de Eco es el piso de ruido por debajo del cual una señal se trata como error instrumental; los máximas griceanos son protocolos de comunicación que aseguran que cada sensor reporte la información máximamente relevante sin redundancia. Un módulo disidente no está siendo "difícil" — es un espectrómetro reportando un pico que las otras cámaras no pueden ver. Silenciarlo es un fallo metodológico, no una corrección estadística.

РУССКИЙ:
- Title: МОДУЛЬ ОТЧЁТА О ДИССЕНСУСЕ — `vigia/core/dissent_report.py`
- What Is This Module? -> Что это за модуль?
- Key concepts:
  - ModuleVerdict -> ВердиктМодуля
  - ModuleOpinion -> МнениеМодуля
  - DissentSignal -> СигналДиссенсуса
  - DissentReport -> ОтчётОДиссенсусе
  - Deterministic Scoring -> Детерминированное оценивание
  - Integer Display -> Целочисленное отображение
  - Functions...
  - Constants: MALICIOUS -> ВРЕДОНОСНЫЙ, SUSPICIOUS -> ПОДОЗРИТЕЛЬНЫЙ, BENIGN -> БЕЗОПАСНЫЙ, ABSTAIN -> ВОЗДЕРЖАЛСЯ
- Glossary:
  - APT -> Продвинутая постоянная угроза
  - Determinism -> Детерминизм
  - Fraction -> Дробь (Python fractions.Fraction)
  - Integer Truncation -> Усечение до целого
  - Consensus Evasion -> Уклонение через консенсус
  - Sensor Analogy -> Аналогия с датчиком
- Scientific Note:
  - Терминология Пирса (абдукция), Эко (семиотический порог) и Грайса (кооперативный принцип / импликатура) иногда отвергается как метафизическая. В этом модуле эти концепции операционализированы как инженерные ограничения. Представьте лабораторную систему приборов: пирсовская абдукция — это генерация гипотез на основе аномальных показаний датчиков; семиотический порог Эко — это уровень шума, ниже которого сигнал считается приборной погрешностью; грайсовы максимы — это коммуникационные протоколы, гарантирующие, что каждый датчик сообщает максимально релевантную информацию без избыточности. Диссидентский модуль не «сложный» — это спектрометр, регистрирующий пик, который другие камеры не видят. Заглушать его — методологическая ошибка, а не статистическая коррекция.

中文:
- Title: 异议报告模块 — `vigia/core/dissent_report.py`
- What Is This Module? -> 本模块是什么？
- Must use: 艾柯 (Eco), 格赖斯 (Grice), 取证工件 (artifact), 逻辑断裂 (not 裂缝)
- Key concepts:
  - ModuleVerdict -> 模块裁决
  - ModuleOpinion -> 模块意见
  - DissentSignal -> 异议信号
  - DissentReport -> 异议报告
  - Deterministic Scoring -> 确定性评分
  - Integer Display -> 整数显示
  - Functions...
  - Constants: MALICIOUS -> 恶意, SUSPICIOUS -> 可疑, BENIGN -> 良性, ABSTAIN -> 弃权
- Glossary:
  - APT -> 高级持续性威胁
  - Determinism -> 确定性
  - Fraction -> 分数 (Python fractions.Fraction)
  - Integer Truncation -> 整数截断
  - Consensus Evasion -> 共识规避
  - Sensor Analogy -> 传感器类比
- Scientific Note:



- 格赖斯 (not Grice) — same
- 取证工件 (not 制品) — use 取证工件 for artifacts
- 逻辑断裂 (not 裂缝) — use 逻辑断裂



Chinese scientific note draft:
【科学说明】
皮尔斯（Peirce）的溯因推理、艾柯的符号学阈值，以及格赖斯的合作原则与含义理论，有时被误认为神秘主义或玄学话语。在本模块中，这些概念被严格操作化为工程约束。请使用传感器类比：将每个检测模块视为实验室中独立的物理仪器——皮尔斯式的溯因是从异常传感器读数中生成最佳假设；艾柯的符号学阈值即为噪声基底，低于该基底的信号被归类为仪器误差而非现象；格赖斯的量准则与关系准则则构成仪器间通信协议，确保每台传感器报告最大相关数据而不冗余。当单一模块发出异议信号时，它并非“不合作”，而是一台光谱仪探测到了其他成像设备无法感知的峰值。在取证科学中，以“多数共识”压制此类信号不是统计修正，而是方法论上的逻辑断裂。







---

# Module Documentation: `vigia/core/dissent_report.py`

## ENGLISH

### What Is This Module?
...

### Key Concepts
| Term | Description |
|------|-------------|
| ...

### Functions & Output Methods
| Function / Method | Purpose |
|-------------------|---------|
| ...

### Constants
| Constant | Meaning |
|----------|---------|
| ...

### Glossary
...

> 【Scientific Note】 ...

---

## ESPAÑOL

### ¿Qué es este módulo?
...

### Conceptos clave
...

### Funciones y métodos de salida
...

### Constantes
...

### Glosario
...

> 【Nota Científica】 ...

---

## РУССКИЙ

### Что представляет собой этот модуль?
...

### Ключевые концепции
...

### Функции и методы вывода
...

### Константы
...

### Глоссарий
...

> 【Научное примечание】 ...

---

## 中文

### 本模块是什么？
...

### 核心概念
...

### 函数与输出方法
...

### 常量
...

### 术语表
...

> 【科学说明】 ...

---



---


For example, bad: "Unlike floating-point numbers, which are approximate..." Good: "All scoring uses Python's fractions.Fraction class, representing values as exact integer ratios (e.g., 1/100) to guarantee bitwise reproducibility." This avoids explaining floating point and focuses on deterministic integer arithmetic.



ENGLISH:

What Is This Module?
This module is a deterministic aggregator for multi-sensor forensic detection. In the VIGÍA system, multiple detection modules (specialized software sensors) analyze the same digital object and render independent classifications. This module collects those classifications, calculates exact consensus and dissent metrics using integer-ratio arithmetic, and produces a structured report. Its core scientific purpose is to prevent "majority suppression" — a tactic used by advanced persistent threats (APTs) to evade detection by forcing a false consensus of BENIGN. When one behavioral module reports MALICIOUS against nine others reporting BENIGN, this module escalates the minority opinion as a dissent signal requiring analyst review. All calculations are reproducible: identical inputs always produce identical reports, with no hardware-dependent variation.

Key Concepts table:
| Concept | Description |
|---|---|
| `ModuleVerdict` | The atomic label assigned by a single detection engine. One of four possible states: MALICIOUS, SUSPICIOUS, BENIGN, or ABSTAIN. |
| `ModuleOpinion` | A verdict bound to an exact confidence score, stored as a rational number (numerator/denominator integer pair) rather than a decimal approximation. |
| `DissentSignal` | A minority opinion that exceeds the noise threshold and must not be silenced. It represents a statistically significant deviation from the majority view. |
| `DissentReport` | The deterministic output document that records every voting module, every abstention, the majority bloc, and all dissent signals. |
| Deterministic Scoring | The use of Python's `fractions.Fraction` for all arithmetic. Every confidence value is an exact ratio of two integers, ensuring cross-platform reproducibility. |
| Integer Display | Conversion of exact fractional confidence to human-readable percentages via integer truncation (`int()`), never rounding. This guarantees that display logic does not introduce variance. |
| Noise Threshold | A minimum confidence level, defined as a `Fraction`, below which an opinion is treated as instrument noise rather than evidence. |
| Critical Dissent Threshold | A `Fraction`-based boundary that determines when a minority opinion is strong enough to be declared a dissent signal. |
| Voting vs. Abstention | A strict logical boundary separates modules that render a verdict from modules that abstain. Abstentions are recorded but excluded from consensus calculations. |

Functions & Output Methods table:
| Function / Method | Purpose |
|---|---|
| `generate_dissent_report()` | Orchestrates report generation. Accepts thresholds as `Fraction` objects to preserve exact arithmetic through every stage of aggregation. |
| `display_confidence_pct()` | Converts an exact confidence `Fraction` to an integer percentage by truncating the fractional part. Deterministic and reproducible. |
| `display_majority_pct()` | Returns the truncated integer percentage representing the share of the majority voting bloc. |
| `display_consensus_pct()` | Returns the truncated integer percentage representing the overall agreement level among all participating modules. |

Constants table:
| Constant | Scientific Meaning |
|---|---|
| `MALICIOUS` | Confirmed threat indicator. The object exhibits known or strongly inferred hostile behavior. |
| `SUSPICIOUS` | Anomalous characteristics detected, but insufficient evidence for a confirmed malicious verdict. |
| `BENIGN` | No threat indicators detected. Object appears safe under current analytical rules. |
| `ABSTAIN` | The module declined to render a verdict, typically due to insufficient data or out-of-scope analysis. |

Glossary:
- **Advanced Persistent Threat (APT):** A prolonged and targeted cyberattack in which an intruder establishes a long-term presence in a network to exfiltrate data or disrupt operations.
- **Determinism:** The property of a computational system whereby the same input always yields the same output, with no temporal or hardware-dependent variation.
- **Fraction (`fractions.Fraction`):** A Python numeric type representing rational numbers exactly as pairs of integers (numerator, denominator). All arithmetic is integer-based.
- **Integer Truncation:** The discarding of a fractional remainder without rounding (e.g., 99.9 % becomes 99 %). This operation is deterministic.
- **Consensus Evasion:** An adversarial technique designed to force a majority of detection modules to agree on a false BENIGN classification, thereby suppressing true minority alarms.
- **Sensor Analogy:** The conceptual model treating each software detection module as an independent physical instrument measuring the same target with different physical principles.

Scientific Note:
> 【Scientific Note】
> The terminology of Charles Sanders Peirce (abductive inference), Umberto Eco (semiotic threshold), and H. Paul Grice (cooperative principle / conversational implicature) is occasionally dismissed as metaphysical. Within this module, these frameworks are operationalized as rigorous engineering constraints. Use the sensor analogy: Peircean abduction is the generation of a best-fit hypothesis when a single instrument produces an anomalous reading; Eco's semiotic threshold is the noise floor below which a signal is classified as instrument error rather than a phenomenon; Gricean maxims function as inter-instrument communication protocols, ensuring each sensor conveys the maximally relevant information without redundancy. A dissenting module is not being uncooperative — it is a spectrometer reporting a spectral peak that optical cameras cannot resolve. In forensic science, suppressing such a signal in the name of consensus is a methodological failure, not a statistical correction.

ESPAÑOL:

¿Qué es este módulo?
Este módulo es un agregador determinista para la detección forense multi-sensor. En el sistema VIGÍA, múltiples módulos de detección (sensores software especializados) analizan el mismo objeto digital y emiten clasificaciones independientes. Este módulo recoge esas clasificaciones, calcula métricas exactas de consenso y disenso mediante aritmética de razones enteras, y produce un informe estructurado. Su propósito científico central es prevenir la "supresión mayoritaria" — una táctica empleada por amenazas persistentes avanzadas (APT) para evadir la detección forzando un falso consenso de BENIGNO. Cuando un módulo conductual reporta MALICIOSO frente a nueve que reportan BENIGNO, este módulo escala la opinión minoritaria como una señal de disenso que requiere revisión del analista. Todos los cálculos son reproducibles: entradas idénticas siempre producen informes idénticos, sin variación dependiente del hardware.

Conceptos clave:
| Concepto | Descripción |
|---|---|
| `ModuleVerdict` | La etiqueta atómica asignada por un único motor de detección. Uno de cuatro estados posibles: MALICIOUS, SUSPICIOUS, BENIGN o ABSTAIN. |
| `ModuleOpinion` | Un veredicto vinculado a una puntuación de confianza exacta, almacenada como número racional (par de enteros numerador/denominador) en lugar de aproximación decimal. |
| `DissentSignal` | Una opinión minoritaria que supera el umbral de ruido y no debe ser silenciada. Representa una desviación estadísticamente significativa respecto a la mayoría. |
| `DissentReport` | El documento de salida determinista que registra cada módulo votante, cada abstención, el bloque mayoritario y todas las señales de disenso. |
| Puntuación Determinista | El uso de `fractions.Fraction` de Python para toda la aritmética. Cada valor de confianza es una razón exacta de dos enteros, garantizando la reproducibilidad entre plataformas. |
| Visualización Entera | Conversión de la confianza fraccionaria exacta a porcentajes legibles mediante truncamiento entero (`int()`), nunca redondeo. Esto asegura que la lógica de visualización no introduzca varianza. |
| Umbral de Ruido | Nivel mínimo de confianza, definido como `Fraction`, por debajo del cual una opinión se trata como ruido instrumental en lugar de evidencia. |
| Umbral Crítico de Disenso | Límite basado en `Fraction` que determina cuándo una opinión minoritaria es lo suficientemente fuerte para declararse señal de disenso. |
| Votación vs. Abstención | Una frontera lógica estricta separa a los módulos que emiten un veredicto de los que se abstienen. Las abstenciones se registran pero se excluyen del cálculo de consenso. |

Funciones y métodos de salida:
| Función / Método | Propósito |
|---|---|
| `generate_dissent_report()` | Orquesta la generación del informe. Acepta umbrales como objetos `Fraction` para preservar la aritmética exacta en cada etapa de agregación. |
| `display_confidence_pct()` | Convierte una `Fraction` de confianza exacta a un porcentaje entero truncando la parte fraccionaria. Determinista y reproducible. |
| `display_majority_pct()` | Devuelve el porcentaje entero truncado que representa la proporción del bloque mayoritario. |
| `display_consensus_pct()` | Devuelve el porcentaje entero truncado que representa el nivel general de acuerdo entre todos los módulos participantes. |

Constantes:
| Constante | Significado Científico |
|---|---|
| `MALICIOUS` | Indicador de amenaza confirmada. El objeto exhibe comportamiento hostil conocido o fuertemente inferido. |
| `SUSPICIOUS` | Características anómalas detectadas, pero evidencia insuficiente para un veredicto malicioso confirmado. |
| `BENIGN` | No se detectan indicadores de amenaza. El objeto parece seguro bajo las reglas analíticas actuales. |
| `ABSTAIN` | El módulo declinó emitir un veredicto, típicamente por datos insuficientes o análisis fuera de alcance. |

Glosario:
- **Amenaza Persistentemente Avanzada (APT):** Un ciberataque prolongado y dirigido en el que un intruso establece una presencia a largo plazo en una red para exfiltrar datos o perturbar operaciones.
- **Determinismo:** Propiedad de un sistema computacional por la cual la misma entrada siempre produce la misma salida, sin variación temporal o dependiente del hardware.
- **Fracción (`fractions.Fraction`):** Un tipo numérico de Python que representa números racionales exactamente como pares de enteros (numerador, denominador). Toda la aritmética es de base entera.
- **Truncamiento Entero:** El descarte del resto fraccionario sin redondeo (p. ej., 99.9 % se convierte en 99 %). Esta operación es determinista.
- **Evasión por Consenso:** Una técnica adversarial diseñada para forzar a una mayoría de módulos de detección a acordar una falsa clasificación BENIGN, suprimiendo así alarmas minoritarias verdaderas.
- **Analogía del Sensor:** El modelo conceptual que trata cada módulo de detección software como un instrumento físico independiente que mide el mismo objetivo con diferentes principios físicos.

Nota Científica:
> 【Nota Científica】
> La terminología de Charles Sanders Peirce (inferencia abdutiva), Umberto Eco (umbral semiótico) y H. Paul Grice (principio cooperativo / implicatura conversacional) ocasionalmente se descarta como metafísica. Dentro de este módulo, estos marcos se operacionalizan como restricciones de ingeniería rigurosas. Use la analogía del sensor: la abducción peirceana es la generación de una hipótesis de mejor ajuste cuando un instrumento produce una lectura anómala; el umbral semiótico de Eco es el piso de ruido bajo el cual una señal se clasifica como error instrumental en lugar de un fenómeno; las máximas griceanas funcionan como protocolos de comunicación entre instrumentos, asegurando que cada sensor transmita la información máximamente relevante sin redundancia. Un módulo disidente no está siendo poco cooperativo: es un espectrómetro que reporta un pico espectral que las cámaras ópticas no pueden resolver. En ciencias forenses, suprimir tal señal en nombre del consenso es un fallo metodológico, no una corrección estadística.

РУССКИЙ:

Что представляет собой этот модуль?
Этот модуль является детерминированным агрегатором для многосенсорной криминалистической детекции. В системе VIGÍA множество модулей детекции (специализированных программных датчиков) анализируют один и тот же цифровой объект и выдают независимые классификации. Данный модуль собирает эти классификации, вычисляет точные метрики консенсуса и диссенсуса с помощью арифметики целочисленных отношений и формирует структурированный отчёт. Его основная научная цель — предотвратить «подавление большинством» — тактику, используемую продвинутыми постоянными угрозами (APT) для уклонения от обнаружения путём принуждения к ложному консенсусу BENIGN. Когда один поведенческий модуль сообщает MALICIOUS против девяти, сообщающих BENIGN, этот модуль эскалирует мнение меньшинства как сигнал диссенсуса, требующий анализа аналитиком. Все вычисления воспроизводимы: идентичные входные данные всегда дают идентичные отчёты без аппаратно-зависимых вариаций.

Ключевые концепции:
| Концепция | Описание |
|---|---|
| `ModuleVerdict` | Атомарная метка, присвоенная одним движком детекции. Одно из четырёх возможных состояний: MALICIOUS, SUSPICIOUS, BENIGN или ABSTAIN. |
| `ModuleOpinion` | Вердикт, связанный с точным значением достоверности, хранимым как рациональное число (пара целых чисел числитель/знаменатель), а не десятичное приближение. |
| `DissentSignal` | Мнение меньшинства, превышающее порог шума и не подлежащее заглушению. Представляет статистически значимое отклонение от точки зрения большинства. |
| `DissentReport` | Детерминированный выходной документ, фиксирующий каждый голосующий модуль, каждую абстенцию, большинственный блок и все сигналы диссенсуса. |
| Детерминированное оценивание | Использование `fractions.Fraction` из Python для всех вычислений. Каждое значение достоверности — точное отношение двух целых чисел, обеспечивающее воспроизводимость на разных платформах. |
| Целочисленное отображение | Преобразование точной дробной достоверности в проценты для восприятия человеком путём усечения до целого (`int()`), а не округления. Это гарантирует, что логика отображения не вносит вариативности. |
| Порог шума | Минимальный уровень достоверности, заданный как `Fraction`, ниже которого мнение рассматривается как шум прибора, а не доказательство. |
| Критический порог диссенсуса | Граница на основе `Fraction`, определяющая, когда мнение меньшинства достаточно сильно, чтобы быть объявленным сигналом диссенсуса. |
| Голосование vs. Абстенция | Строгая логическая граница разделяет модули, выносящие вердикт, и модули, воздерживающиеся от голоса. Абстенции регистрируются, но исключаются из расчёта консенсуса. |

Функции и методы вывода:
| Функция / Метод | Назначение |
|---|---|
| `generate_dissent_report()` | Организует генерацию отчёта. Принимает пороги в виде объектов `Fraction`, чтобы сохранить точную арифметику на каждом этапе агрегации. |
| `display_confidence_pct()` | Преобразует точную дробь достоверности в целое процентное значение путём усечения дробной части. Детерминированная и воспроизводимая операция. |
| `display_majority_pct()` | Возвращает усечённое целое процентное значение, представляющее долю большинственного голосующего блока. |
| `display_consensus_pct()` | Возвращает усечённое целое процентное значение, представляющее общ
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
