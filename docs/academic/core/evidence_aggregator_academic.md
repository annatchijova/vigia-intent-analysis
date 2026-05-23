<!--
VIGIA Academic Documentation
Module: 3c7b4268
Batch ID: vigia-doc-0050-3c7b4268
Generated: 2026-05-20T14:56:47.855244+00:00
-->

---
doc_hash: 3c7b4268
module: vigia/core/evidence_aggregator.py
languages: [EN, ES, RU, ZH]
generated_by: moonshot-kimi-k2.6-batch-api
license: Apache-2.0
---

ENGLISH:
- Title: MODULE DOCUMENTATION: `vigia/core/evidence_aggregator.py`
- What Is This Module?: Plain language. It's a deterministic calculator that combines multiple independent indicators of suspicious activity into a single bounded score. No randomness, no rounding errors.
- Key Concepts Table: Maybe 2 tables. One for inputs (MI_base, synergy, sequence, ALPHA), one for operations (complement-product, Fraction arithmetic, MAX_CAP).
- Glossary: FSV, MI (Mutual Information or Mass Indicator?), Synergy, Sequence, ALPHA, Complement-Product, Deterministic Integer Arithmetic, Peirce, Eco, Grice. Need to define them simply.
- Scientific Note: 【Scientific Note】Peirce/Eco/Grice terminology... Think of it like a sensor array: a thermometer, a motion detector, and a chemical strip each detect different aspects of the same event. Semiotics is the theory of how signs (like sensor readings) convey meaning. Not mysticism.

Wait, the module docstring mentions "señales semióticas" and the user specifically asks for Peirce/Eco/Grice terminology explanation. So I should mention these as semiotic frameworks.

ESPANOL:
- ¿Qué es este módulo?
- Conceptos clave
- Glosario
- 【Nota Científica】

RUSSIAN:
- Что это за модуль?
- Ключевые понятия
- Глоссарий
- 【Научное Примечание】

CHINESE:
- 这是什么模块？
- 核心概念
- 术语表
- 【科学说明】
Terms: 皮尔斯 (Peirce), 艾柯 (Eco), 格赖斯 (Grice). 取证工件. 逻辑断裂.

Let me think about the formula and how to explain it without floating point.
The formula is: MI_final = 1 - (1 - MI_base) * (1 - synergy*ALPHA) * (1 - sequence*ALPHA)
This is bounded probabilistic composition using the complement product. Each term (1 - x) represents the "uncertainty" or "remaining doubt". Multiplying them gives combined remaining doubt. 1 minus that gives combined confidence.
ALPHA is Fraction(1,2) by default, so it's exact rational arithmetic. No floating point.

The user says "do NOT use floating-point math explanations — emphasize deterministic integer arithmetic where applicable".
So I should explicitly state that all calculations use exact rational numbers (fractions) represented as integer pairs (numerator/denominator), avoiding IEEE-754 float approximations.

Tables:
Let's create a table for the components:

| Symbol | Name | Role | Source |
| MI_base | Base Mass Indicator | Initial evidence score from detection layer | Forensic Signal Vector |
| synergy | Synergy modifier | Extra evidence from simultaneous correlated signals | Synergy Engine |
| sequence | Sequence modifier | Extra evidence from temporal ordering | Sequence Analyzer |
| ALPHA | Coupling coefficient | Dampening factor preventing overcounting | Constant (Fraction(1/2)) |

And a table for the mathematical properties:

| Property | Description | Scientific Rationale |
| Deterministic rational arithmetic | All values stored as exact integer ratios (e.g., 1/2) | Eliminates rounding drift across audits |
| Complement-product composition | Uncertainties multiply; confidence is the complement | Ensures independent evidence does not exceed 100% |
| Non-amplifying | Synergy and sequence modify residual uncertainty, not base directly | Prevents runaway positive feedback |

Glossary terms for all languages:
- FSV (Forensic Signal Vector): A structured record of anomalies detected in a digital artifact.
- MI (Mass Indicator / Mutual Information? The docstring uses MI. I'll interpret as "Mass Indicator" or "Mutual Information Index". Since the audience is scientists, maybe "Mass Indicator" is safer, but given "semiotics" context, maybe it's "Meaning Index" or "Mass Indicator". I'll define it as Mass Indicator or simply MI as bounded evidence metric. Let's use "Mass Indicator" in EN, "Indicador de Masa" in ES, "Массовый Индикатор" in RU, "质量指标" in CN. Actually "Mutual Information" is a real info-theory term. But the formula looks like probabilistic OR/complement product. I'll define MI as "Metric of Incrimination / Mutual Information" but to keep it simple, let's call it "Mass Indicator" or just explain it as a bounded scalar from 0 to 1. Let's use "Mass Indicator (MI)".
- Evidence: Information that increases the certainty of a hypothesis.
- Synergy: Coincident signals that reinforce each other beyond individual capability.
- Sequence: Temporal ordering of events that adds structural meaning.
- Complement-product: Mathematical operation where (1-a)(1-b)... represents combined uncertainty.
- ALPHA: Rational coupling constant, default 1/2, preventing double-counting.
- Deterministic integer arithmetic: Computation using exact fractions (pairs of integers) rather than decimal approximations.
- MAX_CAP / MAX_MI: Upper bounds ensuring the score never exceeds logical certainty.

Scientific Note content:
The note must say that Peirce (Charles Sanders Peirce), Eco (Umberto Eco), and Grice (H.P. Grice) are semioticians/philosophers of language. Their terminology (sign, interpretant, implicature, etc.) is a formal analytical framework, not mysticism. Use sensor analogy: Just as a geophysicist uses seismometers, magnetometers, and gravimeters to infer subsurface structure without "magic", the VIGÍA system uses semiotic layers (detection, synergy, sequence) as distinct sensors. The "meaning" extracted is a measurement of structured deviation, not an occult property.

Chinese terms check:
- Peirce: 皮尔斯
- Eco: 艾柯
- Grice: 格赖斯
- forensic artifact: 取证工件
- logical fracture: 逻辑断裂 (though maybe not needed in this doc? The user said Chinese translations must use these. I should try to incorporate 取证工件 and 逻辑断裂 naturally. Since the module is evidence aggregator, "forensic artifact" can be mentioned as the input. "逻辑断裂" might fit in the glossary or as a concept related to sequence/synergy detection. Or maybe in the scientific note? Let's see. The user specifically listed these as requirements for Chinese translations. I should definitely use 取证工件 for forensic artifacts and 逻辑断裂 for logical fractures/cracks. I can mention that the Detection Layer scans 取证工件 for 逻辑断裂.)

License line: Must appear exactly as:  Probably at the end of each section or top/bottom. I'll put it at the bottom of each language section.

No floating point: I must avoid terms like "floating point" except to say we don't use it. Instead use "exact rational arithmetic", "integer ratios", "deterministic fraction arithmetic".

Let's draft ENGLISH first.

---
## ENGLISH

**MODULE PATH:** `vigia/core/evidence_aggregator.py`

### What Is This Module?
This module is a deterministic evidence calculator. It takes multiple independent indicators of suspicious behavior—detected inside digital artifacts—and fuses them into a single, legally auditable score called the Mass Indicator (MI). Instead of relying on approximations, it performs all calculations using exact rational numbers (integer fractions such as 1/2 or 3/4). This guarantees that every audit trail reproduces the exact same result on every run.

Think of it as a digital laboratory balance: it weighs different signals (base detection, simultaneous synergy, temporal sequence) and returns a total mass of evidence that is bounded, reproducible, and free of rounding error.

### Key Concepts

**Table 1. Input Components**
| Symbol | Plain-Language Name | What It Measures | Source Layer |
|---|---|---|---|
| `MI_base` | Base Evidence Score | Initial suspicion level from a single artifact | Detection Layer |
| `synergy` | Synergy Modifier | Extra certainty gained when multiple anomalies coincide | Synergy Engine |
| `sequence` | Sequence Modifier | Extra certainty gained from the temporal order of events | Sequence Analyzer |
| `ALPHA` | Coupling Coefficient | Dampening factor that prevents double-counting; exact value 1/2 | System Constant |

**Table 2. Operational Properties**
| Property | Description | Why It Matters for Science |
|---|---|---|
| Deterministic rational arithmetic | Every value is stored as an exact ratio of two integers (e.g., `Fraction(1, 2)`) | Eliminates rounding drift; audits are bit-for-bit reproducible |
| Complement-product composition | Formula: `MI_final = 1 − (1−MI_base)(1−synergy·ALPHA)(1−sequence·ALPHA)` | Treats each signal as an independent reduction of residual uncertainty |
| Non-amplifying design | Modifiers act on the *remaining doubt*, not on the base score directly | Prevents feedback loops that could artificially inflate certainty |
| Bounded output (`MAX_MI`) | Final score cannot exceed a hard logical ceiling | Maintains interpretability as a bounded probability-like index |

### Glossary

| Term | Definition |
|---|---|
| **Evidence** | Information that increases the certainty of a forensic hypothesis. |
| **Forensic Signal Vector (FSV)** | A structured record of anomalies found within a digital artifact. |
| **Mass Indicator (MI)** | A bounded scalar from 0 to 1 representing the cumulative weight of evidence. |
| **Synergy** | Coincident signals that collectively imply more than the sum of their individual implications. |
| **Sequence** | A temporally ordered pattern of events that adds structural meaning. |
| **Complement-product** | A mathematical operation where uncertainties multiply and the final certainty is their complement (1 minus product). |
| **ALPHA** | A rational coupling constant (exactly 1/2 by default) that scales secondary contributions to avoid overcounting. |
| **Deterministic integer arithmetic** | Computation using exact integer ratios rather than decimal or binary approximations. |
| **MAX_CAP / MAX_MI** | Hard upper limits enforcing that the aggregated score never exceeds total certainty. |

### 【Scientific Note】Semiotics Is a Sensor Array, Not Mysticism
This module references concepts from **Charles Sanders Peirce**, **Umberto Eco**, and **H. P. Grice**—founders of modern semiotics and pragmatics. Their terminology is not metaphysical. It is a formal framework for describing how "signs" (data points) convey meaning in context.

**Sensor analogy:** A geophysicist interpreting an earthquake does not rely on a single instrument. She compares readings from seismometers, magnetometers, and GPS stations. Each sensor measures a different physical property; together they constrain the model. Similarly, VIGÍA treats semiotic layers as distinct sensors:
- The **Detection Layer** is like a thermometer registering a temperature anomaly.
- The **Synergy Engine** is like a chemical strip detecting correlated compounds.
- The **Sequence Analyzer** is like a motion detector revealing temporal progression.

The "meaning" extracted by these layers is simply a measurement of structured deviation. When Peirce writes about the *interpretant* or Eco writes about *signification*, they are describing inference rules—mathematically analogous to sensor fusion. There is no mysticism; there is only multi-source signal integration under deterministic logic.

---

Now ESPAÑOL. Need to mirror structure.

Terms:
- Peirce, Eco, Grice (names stay).
- Evidence Aggregator = Agregador de Evidencias
- Forensic Signal Vector = Vector de Señal Forense
- Mass Indicator = Indicador de Masa (or Índice de Evidencia?). Let's use Indicador de Masa (MI).
- Complement-product = producto de complementos
- Deterministic integer arithmetic = aritmética entera determinista
- MAX_CAP / MAX_MI = límite máximo

Scientific Note: "La semiótica es una red de sensores, no un misticismo."
Names: Charles Sanders Peirce, Umberto Eco, H. P. Grice.

---

## ESPAÑOL

**RUTA DEL MÓDULO:** `vigia/core/evidence_aggregator.py`

### ¿Qué es este módulo?
Este módulo es una calculadora determinista de evidencia. Recibe múltiples indicadores independientes de comportamiento sospechoso—detectados dentro de artefactos digitales—y los fusiona en una puntuación única, auditable legalmente, denominada Indicador de Masa (MI). En lugar de recurrir a aproximaciones numéricas, realiza todos los cálculos con números racionales exactos (fracciones enteras como 1/2 o 3/4). Esto garantiza que cada auditoría reproduzca exactamente el mismo resultado en cada ejecución.

Piense en él como una balanza de laboratorio digital: pesa diferentes señales (detección base, sinergia simultánea, secuencia temporal) y devuelve una masa total de evidencia que está acotada, es reproducible y carece de error de redondeo.

### Conceptos Clave

**Tabla 1. Componentes de Entrada**
| Símbolo | Nombre en Lenguaje Sencillo | Qué Mide | Capa de Origen |
|---|---|---|---|
| `MI_base` | Puntuación Base de Evidencia | Nivel inicial de sospecha de un artefacto individual | Capa de Detección |
| `synergy` | Modificador de Sinergia | Certeza adicional cuando múltiples anomalías coinciden | Motor de Sinergia |
| `sequence` | Modificador de Secuencia | Certeza adicional derivada del orden temporal de los eventos | Analizador de Secuencia |
| `ALPHA` | Coeficiente de Acoplamiento | Factor de amortiguación que evita el doble conteo; valor exacto 1/2 | Constante del Sistema |

**Tabla 2. Propiedades Operativas**
| Propiedad | Descripción | Relevancia Científica |
|---|---|---|
| Aritmética racional determinista | Cada valor se almacena como una razón exacta de dos enteros (p. ej., `Fraction(1, 2)`) | Elimina la deriva por redondeo; las auditorías son reproducibles bit a bit |
| Composición por producto de complementos | Fórmula: `MI_final = 1 − (1−MI_base)(1−sinergia·ALPHA)(1−secuencia·ALPHA)` | Trata cada señal como una reducción independiente de la incertidumbre residual |
| Diseño no amplificador | Los modificadores actúan sobre la *duda remanente*, no sobre la puntuación base directamente | Evita bucles de retroalimentación que inflarían artificialmente la certeza |
| Salida acotada (`MAX_MI`) | La puntuación final no puede exceder un techo lógico estricto | Mantiene la interpretabilidad como un índice tipo probabilidad acotado |

### Glosario

| Término | Definición |
|---|---|
| **Evidencia** | Información que aumenta la certeza de una hipótesis forense. |
| **Vector de Señal Forense (FSV)** | Registro estructurado de anomalías encontradas dentro de un artefacto digital. |
| **Indicador de Masa (MI)** | Escalar acotado entre 0 y 1 que representa el peso acumulado de la evidencia. |
| **Sinergia** | Señales coincidentes que implican colectivamente más que la suma de sus implicaciones individuales. |
| **Secuencia** | Patrón ordenado temporalmente de eventos que añade significado estructural. |
| **Producto de complementos** | Operación matemática donde las incertidumbres se multiplican y la certeza final es su complemento (1 menos el producto). |
| **ALPHA** | Constante racional de acoplamiento (exactamente 1/2 por defecto) que escala las contribuciones secundarias para evitar el sobreconteo. |
| **Aritmética entera determinista** | Cálculo que utiliza razones exactas de enteros en lugar de aproximaciones decimales o binarias. |
| **MAX_CAP / MAX_MI** | Límites superiores estrictos que garantizan que la puntuación agregada nunca exceda la certeza total. |

### 【Nota Científica】La Semiótica Es una Red de Sensores, No un Misticismo
Este módulo hace referencia a conceptos de **Charles Sanders Peirce**, **Umberto Eco** y **H. P. Grice**—fundadores de la semiótica moderna y la pragmática. Su terminología no es metafísica. Es un marco formal para describir cómo los "signos" (puntos de datos) transmiten significado en contexto.

**Analogía del sensor:** Un geofísico que interpreta un terremoto no depende de un solo instrumento. Compara lecturas de sismógrafos, magnetómetros y estaciones GPS. Cada sensor mide una propiedad física distinta; en conjunto, restringen el modelo. De forma análoga, VIGÍA trata las capas semióticas como sensores distintos:
- La **Capa de Detección** es como un termómetro que registra una anomalía térmica.
- El **Motor de Sinergia** es como una tira química que detecta compuestos correlacionados.
- El **Analizador de Secuencia** es como un detector de movimiento que revela progresión temporal.

El "significado" extraído por estas capas es simplemente una medición de desviación estructurada. Cuando Peirce escribe sobre el *interpretante* o Eco sobre la *significación*, están describiendo reglas de inferencia—análogas matemáticamente a la fusión de sensores. No hay misticismo; solo hay integración de señales de múltiples fuentes bajo lógica determinista.

---

Now RUSSIAN.

Terms:
- Module path: ПУТЬ К МОДУЛЮ
- What Is This Module?: Что это за модуль?
- Deterministic evidence calculator: детерминированный калькулятор доказательственной массы
- Exact rational numbers: точные рациональные числа (дроби)
- Mass Indicator: Индикатор Массы (ИМ) or maybe Весовой Индикатор. Let's use Индекс Достоверности? No, let's stick to Индикатор Массы (IM) to match MI. Actually MI is "Mass Indicator" in English, so in Russian "Массовый Индикатор (МИ)" or "Показатель Массы". Let's use "Показатель Массы (МИ)" or "Индикатор Массы". Let's use Индикатор Массы (MI).
- FSV: Вектор Следственного Сигнала (ВСС) or Вектор Криминалистического Сигнала. Let's use "Вектор Криминалистического Сигнала (ВКС)" or keep FSV acronym but explain. Let's use Вектор Сигнала (ВС) or Вектор Судебного Сигнала. Let's use "Вектор Судебного Сигнала (FSV)".
- Synergy: Синергия
- Sequence: Последовательность
- Complement-product: произведение дополнений
- Deterministic integer arithmetic: детерминированная целочисленная арифметика

Scientific Note: 【Научное Примечание】Семиотика — это массив датчиков, а не мистика.
Names: Чарльз Сандерс Пирс, Умберто Эко, Х. П. Грайс.

Important: user said "РУССКИЙ" (all caps).

---

## РУССКИЙ

**ПУТЬ К МОДУЛЮ:** `vigia/core/evidence_aggregator.py`

### Что это за модуль?
Этот модуль — детерминированный калькулятор доказательственной массы. Он получает множество независимых индикаторов подозрительного поведения, обнаруженных внутри цифровых артефактов, и объединяет их в единую юридически аудируемую величину, называемую Индикатором Массы (MI). Вместо приближённых вычислений модуль использует точные рациональные числа (целочисленные дроби, такие как 1/2 или 3/4). Это гарантирует, что любая аудиторская проверка воспроизведёт абсолютно идентичный результат при каждом запуске.

Представьте его как цифровые лабораторные весы: он взвешивает различные сигналы (базовое обнаружение, одновременную синергию, временную последовательность) и возвращает суммарную массу доказательств, которая ограничена, воспроизводима и свободна от ошибок округления.

### Ключевые Понятия

**Таблица 1. Входные Компоненты**
| Обозначение | Название Простым Языком | Что Измеряет | Источник |
|---|---|---|---|
| `MI_base` | Базовый Балл Доказательности | Начальный уровень подозрительности отдельного артефакта | Слой Обнаружения |
| `synergy` | Синергетический Модификатор | Дополнительная уверенность при совпадении нескольких аномалий | Синергетический Движок |
| `sequence` | Последовательный Модификатор | Дополнительная уверенность, вытекающая из временного порядка событий | Анализатор Последовательности |
| `ALPHA` | Коэффициент Связи | Ослабляющий фактор, предотвращающий двойной учёт; точное значение 1/2 | Системная Константа |

**Таблица 2. Операционные Свойства**
| Свойство | Описание | Научное Значение |
|---|---|---|
| Детерминированная рациональная арифметика | Каждое значение хранится как точное отношение двух целых чисел (например, `Fraction(1, 2)`) | Устраняет дрейф округления; аудиты воспроизводимы побитово |
| Композиция произведением дополнений | Формула: `MI_final = 1 − (1−MI_base)(1−synergy·ALPHA)(1−sequence·ALPHA)` | Рассматривает каждый сигнал как независимое сокращение остаточной неопределённости |
| Неусиливающий дизайн | Модификаторы воздействуют на *оставшееся сомнение*, а не на базовый балл напрямую | Предотвращает петли положительной обратной связи, искусственно завышающие уверенность |
| Ограниченный выход (`MAX_MI`) | Итоговая оценка не может превысить жёсткий логический потолок | Сохраняет интерпретируемость как ограниченный вероятностный индекс |

### Глоссарий

| Термин | Определение |
|---|---|
| **Доказательство (Evidence)** | Информация, повышающая достоверность следственной гипотезы. |
| **Вектор Судебного Сигнала (FSV)** | Структурированная запись аномалий, обнаруженных внутри цифрового артефакта. |
| **Индикатор Массы (MI)** | Ограниченный скаляр от 0 до 1, представляющий суммарный вес доказательств. |
| **Синергия** | Совпадающие сигналы, которые совместно означают больше, чем сумма их отдельных значений. |
| **Последовательность** | Временно упорядоченный паттерн событий, придающий структурный смысл. |
| **Произведение дополнений** | Математическая операция, при которой неопределённости перемножаются, а итоговая достоверность является их дополнением (1 минус произведение). |
| **ALPHA** | Рациональная константа связи (строго 1/2 по умолчанию), масштабирующая вторичные вклады для предотвращения пересчёта. |
| **Детерминированная целочисленная арифметика** | Вычисления с использованием точных целочисленных отношений вместо десятичных или двоичных приближений. |
| **MAX_CAP / MAX_MI** | Жёсткие верхние пределы, гарантирующие, что агрегированная оценка никогда не превысит полной достоверности. |

### 【Научное Примечание】Семиотика — Это Массив Датчиков, а Не Мистика
Этот модуль ссылается на концепции **Чарльза Сандерса Пирса**, **Умберто Эко** и **Х. П. Грайса** — основателей современной семиотики и прагматики. Их терминология не является метафизической. Это формальная рамка для описания того, как «знаки» (точки данных) передают значение в контексте.

**Аналогия с датчиком:** Геофизик, интерпретирующий землетрясение, не полагается на один прибор. Он сравнивает показания сейсмографов, магнитометров и GPS-станций. Каждый датчик измеряет различное физическое свойство; в совокупности они сужают модель. Аналогично VIGÍA рассматривает семиотические слои как различные датчики:
- **Слой Обнаружения** — как термометр, регистрирующий температурную аномалию.
- **Синергетический Движок** — как химическая полоска, обнаруживающая коррелированные соединения.
- **Анализатор Последовательности** — как детектор движения, выявляющий временное развитие.

«Значение», извлекаемое этими слоями, — это просто измерение структурированного отклонения. Когда Пирс пишет об *интерпретанте* или Эко о *значении*, они описывают правила вывода — математически аналогичные слиянию данных датчиков. Никакого мистицизма; только интеграция сигналов из множества источников в рамках детерминистской логики.

---

Now CHINESE. This is critical because of the mandated terms.

Terms:
- Module path: 模块路径
- What Is This Module?: 这是什么模块？
- Deterministic evidence calculator: 确定性证据计算器 / 确定性证据聚合计算器
- Exact rational numbers: 精确有理数 (整数分数)
- Mass Indicator: 质量指标 (MI) — wait, "Mass Indicator" could be 质量指标 or 块度指标? In this context, maybe "质量指标" is okay, but "质量" can mean quality. Maybe "质量" as in physics mass? The English used "Mass Indicator" to mean weight of evidence. In Chinese, "证据质量指标" or simply "质量指标". Let's use "质量指标 (MI)" and clarify it means cumulative weight. Or "集总指标"? Let's use "质量指标 (MI)" and note it represents cumulative evidentiary weight.
- FSV: 取证信号向量 (FSV) — wait, the user said 取证工件 for forensic artifact. FSV is Forensic Signal Vector. So "取证信号向量 (FSV)" is fine. Or "法庭科学信号向量". Let's use "取证信号向量 (FSV)".
- Synergy: 协同 / 协同效应. Let's use 协同.
- Sequence: 时序 / 序列. Let's use 时序.
- Complement-product: 补数乘积 / 互补乘积合成. Let's use 互补乘积合成.
- ALPHA: 耦合系数 (exact value 1/2)
- Deterministic integer arithmetic: 确定性整数运算. Actually it's rational arithmetic (分数运算). The requirement says emphasize deterministic integer arithmetic where applicable. Since Fraction is integer pair, I can say "基于整数对的精确分数运算" or "确定性整数比率运算". Let's use "确定性整数比率运算（精确分数）".
- Evidence: 证据
- Forensic artifact: 取证工件 (must use this)
- Logical fracture: 逻辑断裂 (must use this)

I need to incorporate 取证工件 and 逻辑断裂.
In the "What Is This Module?" or Key Concepts, I can say the Detection Layer scans 取证工件 for anomalies including 逻辑断裂.
For example: "检测层扫描取证工件以发现异常（如逻辑断裂）..."

Scientific Note: 【科学说明】符号学不是神秘主义，而是传感器阵列。
Names: 查尔斯·桑德斯·皮尔斯 (Charles Sanders Peirce), 艾柯 (Umberto Eco), 格赖斯 (H.P. Grice). User said 艾柯 and 格赖斯.

Let's draft.

---

## 中文

**模块路径：** `vigia/core/evidence_aggregator.py`

### 这是什么模块？
本模块是一个**确定性证据聚合计算器**。它接收在数字**取证工件**中检测到的多个独立可疑行为指标（例如**逻辑断裂**、异常时序、协同特征），并将它们融合为一个单一的、可法律审计的评分，称为**质量指标（MI）**。模块不使用任何近似小数计算，而是完全基于**精确有理数**（整数分数，如 1/2、3/4）进行运算。这保证了每一次审计追踪在每次运行时都能复现完全相同的结果。

可以将其视为一台数字实验室天平：它称量不同的信号（基础检测、同时性协同、时序序列），并返回一个总证据质量。该质量有界、可复现，且不受舍入误差影响。

### 核心概念

**表 1. 输入组件**
| 符号 | 通俗名称 | 测量内容 | 来源层 |
|---|---|---|---|
| `MI_base` | 基础证据评分 | 来自单个取证工件的初始可疑程度 | 检测层 |
| `synergy` | 协同修正量 | 多个异常同时出现时获得的额外确定性 | 协同引擎 |
| `sequence` | 时序修正量 | 由事件的时间顺序所贡献的额外确定性 | 时序分析器 |
| `ALPHA` | 耦合系数 | 防止重复计算的衰减因子；精确值为 1/2 | 系统常量 |

**表 2. 运算属性**
| 属性 | 描述 | 科学意义 |
|---|---|---|
| 确定性整数比率运算 | 每个值均以两个整数的精确比率存储（例如 `Fraction(1, 2)`） | 消除舍入漂移；审计结果可逐位复现 |
| 互补乘积合成 | 公式：`MI_final = 1 − (1−MI_base)(1−synergy·ALPHA)(1−sequence·ALPHA)` | 将每个信号视为对残余不确定度的独立削减 |
| 非放大式设计 | 修正量作用于*剩余疑义*，而非直接放大基础分 | 防止正反馈循环人为抬升确定性 |
| 有界输出 (`MAX_MI`) | 最终评分不得超过严格的逻辑上限 | 保持其作为有界概率型指数的可解释性 |

### 术语表

| 术语 | 定义 |
|---|---|
| **证据** | 能够提高取证假设确定性程度的信息。 |
| **取证信号向量（FSV）** | 在数字取证工件中发现的异常的结构化记录。 |
| **质量指标（MI）** | 一个介于 0 与 1 之间的有界标量，代表证据的累积权重。 |
| **协同（Synergy）** | 多个同时出现的信号，其整体含义大于各信号单独含义之和。 |
| **时序（Sequence）** | 按时间排列的事件模式，可赋予结构性的意义。 |
| **互补乘积合成** | 一种数学运算：将各不确定度相
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
