<!--
VIGIA Academic Documentation
Module: e7859153
Batch ID: vigia-doc-0028-e7859153
Generated: 2026-05-20T14:56:47.850642+00:00
-->

# Module Documentation: `vigia/abduction/hypothesis_lineage.py`

## ENGLISH

### What Is This Module?
This module serves as the **family tree of hypotheses** during VIGÍA's abductive reasoning cycle. In digital forensics, a SANS analyst must see more than a final verdict; the analyst needs a **map of alternatives**—a clear view of what additional evidence, if discovered or absent, would pivot the conclusion in another direction. This module records every hypothesis under consideration, tracks the discriminating signals that could alter the outcome, and produces an immutable **lineage report** that satisfies Daubert-standard traceability. To guarantee reproducibility, the module represents all costs as exact integer ratios and derives an audit hash deterministically from the complete reasoning trace.

### Key Concepts

**Table 1. Core Components**
| Component | Role | Forensic Analogy |
|-----------|------|------------------|
| `HypothesisNode` | Immutable container for one investigative hypothesis | A sealed evidence bag bearing an unalterable label |
| `PivotSignal` | Evidence whose presence or absence would flip the verdict | A latent fingerprint that reclassifies a breach from external to insider |
| `LineageReport` | Final, exportable output of the abductive cycle | The expert-witness workbook submitted for Daubert review |
| `HypothesisLineageTracker` | Registry of the full reasoning cycle | The chain-of-custody log, but for logical inference |

**Table 2. Integrity Model**
| Property | Representation | Scientific Benefit |
|----------|----------------|--------------------|
| Costs | Exact rational numbers (integer numerator / integer denominator) | Eliminates rounding drift; repeated calculations are bit-for-bit identical on any platform |
| `audit_hash` | Deterministic integer digest computed from the entire trace | Guarantees that the same evidence sequence always yields the same integrity signature |

**Table 3. Lifecycle Operations**
| Function | Purpose | Traceability Role |
|----------|---------|-------------------|
| `record()` | Enters a new hypothesis into the lineage tree | Appends an immutable, timestamped node to the reasoning journal |
| `finalize(winner_id)` | Closes the cycle and generates the `LineageReport` | Locks the journal and declares the winning hypothesis for independent audit |

### Glossary
- **Abductive cycle**: The inferential process of selecting the best explanation from a set of observed evidence.
- **Deterministic integer arithmetic**: Computation using exact ratios of whole numbers, ensuring identical outputs across repeated runs without any rounding approximation.
- **Frozen dataclass**: An immutable data structure; once instantiated, its fields cannot be altered, preventing post-hoc tampering.
- **Hypothesis lineage**: The documented ancestry, branching, and death of all explanations considered during an investigation.
- **Pivot signal**: A piece of evidence that acts as a binary switch; its state determines which hypothesis prevails.
- **Daubert traceability**: The legal requirement that forensic methodologies be testable, documented, and accompanied by known error rates.

### 【Scientific Note】
Terminology drawn from Peirce, Eco, and Grice is occasionally dismissed as metaphysical. It is not. Within this module, those concepts operate as **deterministic signal-processing constraints**. Peirce's abduction is the hypothesis-generation filter; Eco's coherence criteria serve as cross-sensor validation rules; Grice's maxims function as noise-reduction protocols. They are formal boundary conditions, not mysticism—precisely as a thermometer does not "believe" in temperature but registers it through calibrated physical expansion.

---

## ESPAÑOL

### ¿Qué es este módulo?
Este módulo es el **árbol genealógico de hipótesis** durante el ciclo abductivo de VIGÍA. En forense digital, el analista SANS debe ver más que el veredicto final; necesita un **mapa de alternativas**: una visión clara de qué evidencia adicional, de encontrarse o faltar, cambiaría la conclusión y hacia dónde. El módulo registra cada hipótesis considerada, rastrea las señales discriminantes que podrían modificar el resultado y produce un **informe de linaje** inmutable que cumple con la trazabilidad exigida por el estándar Daubert. Para garantizar la reproducibilidad, representa todos los costos como razones exactas de enteros y calcula un hash de auditoría de manera determinista a partir de la traza completa de razonamiento.

### Conceptos clave

**Tabla 1. Componentes principales**
| Componente | Función | Analogía forense |
|------------|---------|------------------|
| `HypothesisNode` | Contenedor inmutable para una hipótesis investigativa | Bolsa de evidencia sellada con etiqueta inalterable |
| `PivotSignal` | Evidencia cuya presencia o ausencia cambiaría el veredicto | Huella dactilar latente que reclasifica una intrusión de externa a interna |
| `LineageReport` | Producto final exportable del ciclo abductivo | Cuaderno de trabajo del perito presentado para revisión Daubert |
| `HypothesisLineageTracker` | Registro del ciclo de razonamiento completo | Registro de cadena de custodia, pero aplicado a la inferencia lógica |

**Tabla 2. Modelo de integridad**
| Propiedad | Representación | Beneficio científico |
|-----------|----------------|----------------------|
| Costos | Números racionales exactos (numerador entero / denominador entero) | Elimina la deriva por redondeo; los cálculos repetidos son idénticos bit a bit en cualquier plataforma |
| `audit_hash` | Resumen determinista entero calculado sobre toda la traza | Garantiza que la misma secuencia de evidencia produzca siempre la misma firma de integridad |

**Tabla 3. Operaciones del ciclo de vida**
| Función | Propósito | Rol de trazabilidad |
|---------|-----------|---------------------|
| `record()` | Ingresa una nueva hipótesis al árbol de linaje | Añade un nodo inmutable con marca temporal al diario de razonamiento |
| `finalize(winner_id)` | Cierra el ciclo y genera el `LineageReport` | Bloquea el diario y declara la hipótesis ganadora para auditoría independiente |

### Glosario
- **Ciclo abductivo**: Proceso inferencial de seleccionar la mejor explicación a partir de un conjunto de evidencia observada.
- **Aritmética determinista de enteros**: Cálculo con razones exactas de números enteros, asegurando resultados idénticos en cada ejecución sin aproximación por redondeo.
- **Dataclass congelada (frozen)**: Estructura de datos inmutable; una vez creada, sus campos no pueden alterarse, evitando la manipulación a posteriori.
- **Linaje de hipótesis**: Ascendencia, ramificación y descarte documentados de todas las explicaciones consideradas durante una investigación.
- **Señal pivote (PivotSignal)**: Pieza de evidencia que actúa como interruptor binario; su estado determina qué hipótesis prevalece.
- **Trazabilidad Daubert**: Requisito legal de que las metodologías forenses sean comprobables, documentadas y acompañadas de tasas de error conocidas.

### 【Nota Científica】
La terminología de Peirce, Eco y Grice se descarta a veces como metafísica. No lo es. Dentro de este módulo, esos conceptos operan como **restricciones deterministas de procesamiento de señales**. La abducción de Peirce es el filtro de generación de hipótesis; los criterios de coherencia de Eco sirven como reglas de validación entre sensores; los máximos de Grice funcionan como protocolos de reducción de ruido. Son condiciones de contorno formales, no misticismo: exactamente como un termómetro no "cree" en la temperatura, sino que la registra mediante expansión física calibrada.

---

## РУССКИЙ

### Что это за модуль?
Этот модуль представляет собой **генеалогическое древо гипотез** в ходе абдуктивного цикла VIGÍA. В цифровой криминалистике аналитик SANS должен видеть не только окончательный вердикт, но и **карту альтернатив** — чёткое представление о том, какие дополнительные доказательства, будучи обнаруженными или отсутствующими, изменили бы заключение и в каком направлении. Модуль регистрирует каждую рассмотренную гипотезу, отслеживает различающие сигналы, способные изменить результат, и формирует неизменяемый **отчёт о происхождении (lineage)**, отвечающий требованиям прослеживаемости по стандарту Daubert. Для гарантии воспроизводимости все стоимости представлены в виде точных отношений целых чисел, а аудит-хеш вычисляется детерминированно из полной трассы рассуждений.

### Ключевые понятия

**Таблица 1. Основные классы**
| Класс | Роль | Судебная аналогия |
|-------|------|-------------------|
| `HypothesisNode` | Неизменяемый контейнер для одной следственной гипотезы | Запечатанный пакет с доказательством и неизменяемой этикеткой |
| `PivotSignal` | Сигнал, наличие или отсутствие которого меняет вердикт | Латентный отпечаток, переквалифицирующий кражу во внутренний доступ |
| `LineageReport` | Итоговый результат абдуктивного цикла | Рабочая тетрадь эксперта, представляемая в суде по стандарту Daubert |
| `HypothesisLineageTracker` | Реестр полного абдуктивного цикла | Журнал учёта цепочки сохранности для рассуждений |

**Таблица 2. Модель стоимости и целостности**
| Свойство | Тип данных | Почему это важно |
|----------|------------|------------------|
| Стоимость (cost) | `Fraction` (точная рациональная дробь) | Устраняет ошибки округления; 1/3 + 1/3 + 1/3 точно равно 1, а не 0,999... |
| audit_hash | Детерминированное целочисленное значение | Воспроизводит один и тот же хеш из одной и той же полной трассы на любой платформе |

**Таблица 3. Операции жизненного цикла**
| Функция | Назначение | Роль прослеживаемости |
|---------|------------|----------------------|
| `record()` | Вносит новую гипотезу в дерево происхождения | Добавляет неизменяемый узел с временной меткой в журнал рассуждений |
| `finalize(winner_id)` | Завершает цикл и генерирует `LineageReport` | Блокирует журнал и объявляет победившую гипотезу для независимого аудита |

### Глоссарий
- **Абдуктивный цикл**: Процесс рассуждения, при котором из наблюдаемых доказательств выводится наилучшее объяснение.
- **Frozen dataclass (замороженный класс данных)**: Неизменяемая структура данных; после создания её нельзя изменить, что предотвращает фальсификацию.
- **Прослеживаемость Daubert**: Правовой стандарт, требующий, чтобы криминалистические методы были проверяемыми, рецензируемыми и сопровождались известными частотами ошибок.
- **Детерминированная целочисленная арифметика**: Вычисления с точными отношениями целых чисел, дающие одинаковый результат каждый раз без приближений с плавающей точкой.
- **Происхождение гипотезы (lineage)**: Документированное родословие и ветвление всех рассмотренных объяснений.
- **Поворотный сигнал (PivotSignal)**: Различающее доказательство, состояние которого (наличие/отсутствие) изменяет оптимальную гипотезу.

### 【Научное Примечание】
Терминология Пирса, Эко и Грайса иногда ошибочно принимается за метафизическую спекуляцию. Это не так. В данном модуле эти понятия работают как детерминированные ограничения обработки сигналов. Абдукция Пирса — это фильтр генерации гипотез; критерии когерентности Эко действуют как межсенсорная валидация; максимы Грайса функционируют как протоколы подавления шума. Это формальные правила, а не мистика — точно так же, как термометр не «верит» в температуру, а измеряет её посредством калиброванного расширения.

---

## 中文

### 本模块是什么？
本模块是 VIGÍA 溯因推理周期中的假设"家谱树"。在数字取证中，分析人员不仅要看到最终裁决，还要看到"替代方案图"：哪些额外证据的发现或缺失会改变裁决、以及朝哪个方向改变。该模块记录每一个被考虑的假设，追踪可能改变结果的信号与**取证工件**，并生成一份不可篡改的谱系报告，以满足道伯特标准（Daubert）的可追溯性要求。它帮助分析人员识别**逻辑断裂**——即哪些证据的缺失会逆转当前结论。模块通过精确分数成本和基于完整轨迹的确定性哈希值来确保结果的可复现性。

### 核心概念

**表 1：核心类**
| 类 | 作用 | 取证类比 |
|----|------|----------|
| `HypothesisNode` | 单个调查假设的不可变容器 | 贴有不可更改标签的密封证据袋 |
| `PivotSignal` | 其存在或缺失会改变裁决的信号 | 能将入室盗窃重新归类为内部人员访问的潜在指纹 |
| `LineageReport` | 溯因推理周期的最终输出 | 按道伯特标准提交的专家工作手册 |
| `HypothesisLineageTracker` | 完整溯因推理周期的登记簿 | 推理过程的保管链日志 |

**表 2：成本与完整性模型**
| 属性 | 数据类型 | 重要性 |
|------|----------|--------|
| 成本 (cost) | `Fraction`（精确有理数） | 消除舍入误差；1/3 + 1/3 + 1/3 精确等于 1，而非 0.999… |
| audit_hash | 确定性整数摘要 | 在任何平台上，相同的完整轨迹都能复现出相同的哈希值 |

**表 3：生命周期操作**
| 函数 | 用途 | 可追溯性角色 |
|------|------|------------|
| `record()` | 将新假设录入谱系树 | 向推理日志追加不可变的带时间戳节点 |
| `finalize(winner_id)` | 关闭周期并生成 `LineageReport` | 锁定日志并声明胜出假设以供独立审计 |

### 术语表
- **溯因推理周期 (Abductive cycle)**：从观测证据推断最佳解释的推理过程。
- **冻结数据类 (Frozen dataclass)**：不可变的数据结构；一旦创建便无法修改，防止篡改。
- **道伯特可追溯性 (Daubert traceability)**：法律标准，要求取证方法具有可检验性、经过同行评审，并附有已知的错误率。
- **确定性整数运算 (Deterministic integer arithmetic)**：使用整数的精确比值进行计算，每次产生完全相同的结果，不存在浮点近似。
- **假设谱系 (Hypothesis lineage)**：所有被考虑解释的已记录起源与分支。
- **枢轴信号 (PivotSignal)**：一种具有判别性的取证工件，其状态（存在/缺失）会改变最优假设。
- **逻辑断裂 (Logical fracture)**：假设谱系中的一种语义不连续，指某项证据的缺失或矛盾导致当前最优假设无法成立的状态。

### 【科学说明】
皮尔士、艾柯与格赖斯的术语有时被误认为玄学思辨。事实并非如此。在本模块中，这些概念起到确定性信号处理约束的作用：皮尔士的溯因推理是假设生成过滤器；艾柯的连贯性标准相当于跨传感器验证；格赖斯的准则则充当降噪协议。它们是形式化规则，而非神秘主义——正如温度计并不"相信"温度，而是通过校准膨胀来测量它一样。

---

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
