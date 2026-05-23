<!--
VIGIA Academic Documentation
Module: adf95e94
Batch ID: vigia-doc-0067-adf95e94
Generated: 2026-05-20T14:56:47.858908+00:00
-->

---
doc_hash: adf95e94
module: unknown
languages: [EN, ES, RU, ZH]
generated_by: moonshot-kimi-k2.6-batch-api
license: Apache-2.0
---

ENGLISH:
- What Is This Module?: Explain it's a deterministic scoring engine within VIGÍA that corrects a dangerous bias: the tendency to prefer "benign incompetence" just because it looks simpler. Uses Peircean semiotics (Secondness) and adversarial thinking. Inspired by SolarWinds. Uses exact rational arithmetic (fractions.Fraction) and integer display to avoid cross-platform irreproducibility.
- Key Concepts Table: 
  - Ockham’s Razor (Adversarial Twist): Normally prefer simpler explanation; here, simplicity is suspect if malice signals exist.
  - Peircean Secondness: The brute fact of resistance; a signal that something external (malice) is acting upon the system.
  - Deterministic Integer Arithmetic: Using Python's fractions.Fraction and truncated integer conversion to guarantee identical results on all hardware.
  - Immutable Configuration: _PENALTY_TABLE as frozenset prevents runtime tampering.
  - SolarWinds Paradigm: Signed artifact + ignored anomalies = artificially clean benign explanation.
- Classes/Functions Table:
  - MaliceSignalStrength: Ordinal enum (NONE→CRITICAL). No continuous/floating values.
  - OckhamPenaltyResult: Immutable record of penalty calculation.
  - aggregate_malice_signal_strength(): Pools discrete malice weights (Fractions) into an aggregate.
  - compute_adversarial_penalty(): Applies penalty to overly simple benign hypotheses.
  - display_confidence(): Converts exact rational confidence to integer percent via truncation (int()), never banker's rounding.
- Glossary:
  - Adversarial Penalty: A cost increment added to the benign hypothesis to compensate for attacker-contrived simplicity.
  - Fractions.Fraction: Python's exact rational number type; think of it as storing numerator and denominator as integers separately, avoiding decimal rounding.
  - Frozenset: An immutable set; once created, its contents cannot be altered, ensuring forensic integrity.
  - Ordinal Scale: A ranked category system (e.g., NONE < WEAK < ... < CRITICAL) without assuming equal intervals between ranks.
  - Peircean Secondness: In C.S. Peirce's phenomenology, the mode of being of that which is such as it is, with respect to a second but regardless of any third; here, the irreducible fact of an anomalous signal pushing back against interpretation.
  - Truncation: Discarding the decimal remainder rather than rounding; mathematically identical to floor for positive numbers, ensuring deterministic output.
- Scientific Note box: Peirce/Eco/Grice terminology is NOT mysticism. Think of a sensor: Peirce's Secondness is simply the voltage spike when a physical probe encounters resistance. It is a raw datum before theory. Eco's codes and Grice's maxims are calibration protocols for interpreting that voltage. We use them as formal heuristics, not metaphysical entities.

ESPAÑOL:
- What Is This Module? -> ¿Qué es este módulo?
- Similar content. Use "afección benigna" or "incompetencia benigna". "Segundo peirceano". "Rasero de Ockham". "Determinismo aritmético entero".
- Specific terms: "fracciones.Fraction", "frozenset".
- Glossary: "Penalización adversarial", "Fractions.Fraction" (número racional exacto), "Frozenset" (conjunto inmutable), "Escala ordinal", "Segundez peirceana", "Truncamiento".
- Scientific Note: Same sensor analogy.

РУССКИЙ:
- What Is This Module? -> Что это за модуль?
- Terms: Принцип Оккама (адверсариальный поворот), Пирсовская Secondness (Вторичность), Детерминированная целочисленная арифметика, Неизменяемая конфигурация, Парадигма SolarWinds.
- Classes: MaliceSignalStrength (ординальная шкала силы сигналов зловредности), OckhamPenaltyResult (неизменяемый результат), aggregate... (агрегация), compute... (вычисление штрафа), display_confidence() (целочисленный процент).
- Glossary: Адверсариальный штраф, Fractions.Fraction (точные рациональные числа), Frozenset (неизменяемое множество), Порядковая шкала, Пирсовская вторая категория (Secondness), Усечение (truncation).
- Scientific Note: Аналогия с датчиком. Терминология Пирса/Эко/Грайса — не мистицизм.

中文:
- Must use: 艾柯 (not Eco), 格赖斯 (not Grice), 取证工件 (not 制品), 逻辑断裂 (not 裂缝).
- What Is This Module? -> 本模块是什么？
- Terms: 奥卡姆剃刀（对抗性修正）, 皮尔斯第二性（Peircean Secondness）, 确定性整数运算, 不可变配置, SolarWinds范式.
- Classes: 恶意信号强度（MaliceSignalStrength）- 序数等级, 奥卡姆惩罚结果（OckhamPenaltyResult）- 不可变记录, 聚合恶意信号强度, 计算对抗性惩罚, 显示置信度（截断整数）.
- Glossary: 对抗性惩罚, 精确有理数类型（fractions.Fraction）, 不可变集合（frozenset）, 序数量表, 皮尔斯第二性, 截断法.
- Scientific Note: 【科学说明】皮尔斯/艾柯/格赖斯术语并非神秘主义。请将其想象为一种传感器：皮尔斯的“第二性”本质上是物理探针遇到阻力时产生的电压尖峰，是理论介入之前的原始数据；艾柯的符码与格赖斯的准则则是解读该电压的校准协议。在VIGÍA中，它们被用作形式化启发式规则，而非形而上学实体。
- 取证工件 is used instead of 制品. For example: "取证工件" for forensic artifacts. The module mentions SolarWinds DLL signed. I should use 取证工件 there.
- 逻辑断裂: use for logical fracture/break? The module doesn't explicitly mention fracture, but I can incorporate it if needed or just ensure I don't use 裂缝. Wait, the user specifically said "逻辑断裂 (not 裂缝)". I should probably use 逻辑断裂 somewhere appropriate, perhaps in the context of the "clean explanation" creating a logical break. Or perhaps in the glossary or concept table. Let's use it: "过于简洁的解释造成逻辑断裂".
- License: "" (keep in English or translate? User said license line specifically. Probably keep as is, but can add translation. I'll keep exact line.)

General structure:
I'll make a markdown document with clear headings for each language.

Double check: no floating-point math explanations. Emphasize deterministic integer arithmetic.
- fractions.Fraction is exact rational arithmetic based on integers.
- display uses int() truncation.
- No round().
- _PENALTY_TABLE immutable frozenset.

I need to be thorough but concise.

Let's draft the ENGLISH section as template:

---
## ENGLISH

### What Is This Module?
This module is a deterministic correction engine inside the VIGÍA forensic framework. Its purpose is to stop an investigative trap: a sophisticated attacker deliberately stages an incident so that the simplest explanation appears to be innocent human error. The module detects when a "too-clean" benign story is artificially cheap and punishes that hypothesis, steering the investigator toward a conclusion of malice.

The logic is inspired by the SolarWinds breach, where a legitimately signed dynamic-link library (DLL) plus five ignored anomalies produced an explanation that looked elegantly simple—yet was wrong. The module treats such suspicious simplicity as evidence in its own right (a phenomenon aligned with C. S. Peirce’s category of Secondness). All calculations use exact integer-based rational arithmetic (`fractions.Fraction`) to guarantee that two different computers always reach the identical score.

### Key Concepts

| Concept | Plain-Language Definition | Role in the Module |
|---|---|---|
| Adversarial Ockham’s Razor | The principle that, under attack, the simplest explanation may be a deliberately planted decoy rather than the truth. | Governs when to distrust low-complexity benign hypotheses. |
| Peircean Secondness | The raw, uninterpreted fact of resistance or anomaly—like a sensor spike—that signals an external force (malice) is present. | Provides the philosophical grounding for treating ignored anomalies as active signals, not passive noise. |
| Deterministic Integer Arithmetic | Mathematical operations performed with exact fractions (pairs of integers) and truncated integer conversion, never with floating-point decimals. | Ensures bitwise-reproducible scores across CPU architectures. |
| Immutable Configuration | A lookup table (`_PENALTY_TABLE`) locked as a `frozenset`, meaning its contents cannot be altered at runtime. | Protects forensic integrity by preventing in-memory tampering with penalty values. |
| SolarWinds Paradigm | A signed forensic artifact coupled with multiple dismissed anomalies that together create an artificially "clean" benign narrative. | Serves as the motivating case study for the penalty logic. |

### Module Components

| Component | Type | Function |
|---|---|---|
| `NONE`, `WEAK`, `MODERATE`, `STRONG`, `CRITICAL` | Constants | Ordinal levels of malice signal strength. Discrete ranks without floating-point gradation. |
| `MaliceSignalStrength` | Class | Encapsulates the ordinal scale of malice. Guarantees all signal strengths remain integer-typed ordinals. |
| `OckhamPenaltyResult` | Class | An immutable data record that stores the outcome of a penalty calculation. Once created, it cannot be modified. |
| `aggregate_malice_signal_strength()` | Function | Collects malice indicators from the active evidence pool. Each indicator carries an exact rational weight (`Fraction` between 0 and 1). The function merges them into a unified ordinal assessment. |
| `compute_adversarial_penalty()` | Function | Measures how suspiciously simple the benign hypothesis is and adds a deterministic penalty cost to it. |
| `display_confidence()` | Function | Converts an exact internal confidence score into a whole-number percentage (e.g., 73 %) using truncation (`int()`), avoiding floating-point display and banker's rounding. |

### Glossary

| Term | Definition |
|---|---|
| **Adversarial Penalty** | A deterministic cost increment deliberately added to a benign hypothesis to compensate for simplicity that an attacker may have engineered. |
| **`fractions.Fraction`** | A Python data type representing an exact ratio of two integers (numerator and denominator). It operates like symbolic fraction arithmetic taught in basic algebra, producing no rounding errors. |
| **`frozenset`** | An immutable collection. Because its contents are fixed at creation, it functions as a read-only seal, preventing accidental or malicious runtime changes to penalty parameters. |
| **Ordinal Scale** | A ranking system (e.g., NONE → CRITICAL) where order matters but the numerical distance between ranks is not assumed to be equal. There are no decimals between ranks. |
| **Peircean Secondness** | In the semiotics of Charles Sanders Peirce, the mode of being of brute fact or resistance. In digital forensics, it is the irreducible datum of an anomaly that refuses to be explained away by the simplest story. |
| **Truncation** | The removal of any fractional remainder (e.g., turning 73.9 into 73). For positive scores this is identical to the mathematical floor function and yields deterministic, architecture-independent output. |

### 【Scientific Note】
> **Peirce, Eco, and Grice Are Not Mysticism**
>
> The terminology borrowed from C. S. Peirce, Umberto **Eco**, and H. P. **Grice** is employed here as formal semiotic engineering, not metaphysical speculation. Think of a physical sensor: **Peircean Secondness** is nothing more than the voltage spike when a probe encounters unexpected resistance—a raw measurement before any theory is applied. **Eco’s** codes and **Grice’s** conversational maxims act as calibration protocols: they tell us how to interpret that voltage spike in context. VIGÍA uses these frameworks as deterministic heuristics—rules that map observed取证工件 (forensic artifacts) to logical states. They are mathematical instruments, not occult forces.


---

Wait, in the English scientific note, I should not use Chinese term 取证工件. That was a slip in my draft thought. I'll keep English clean. Also, the user said Chinese must use 艾柯, 格赖斯, 取证工件, 逻辑断裂. I should ensure those are in the Chinese section. The note in English can mention Eco and Grice normally.

Now ESPAÑOL:

---
## ESPAÑOL

### ¿Qué es este módulo?
Es un motor de corrección determinista dentro del marco forense VIGÍA. Su objetivo es evitar una trampa investigativa: un atacante sofisticado diseña deliberadamente un incidente para que la explicación más simple parezca un error humano benigno. El módulo detecta cuando una narrativa benigna está artificialmente "demasiado limpia" y penaliza esa hipótesis, orientando al investigador hacia la conclusión de malicia.

La lógica se inspira en el caso SolarWinds, donde una biblioteca de enlace dinámico (DLL) legítimamente firmada, sumada a cinco anomalías ignoradas, generó una explicación elegante pero falsa. El módulo trata esa simplicidad sospechosa como evidencia por sí misma (un fenómeno alineado con la Segundez peirceana). Todos los cálculos usan aritmética racional exacta basada en enteros (`fractions.Fraction`), garantizando que dos computadoras distintas produzcan idéntica puntuación.

### Conceptos Clave

| Concepto | Definición en lenguaje sencillo | Rol en el módulo |
|---|---|---|
| Navaja de Ockham adversarial | El principio de que, bajo ataque, la explicación más simple puede ser un señuelo plantado deliberadamente en lugar de la verdad. | Gobierna cuándo desconfiar de hipótesis benignas de baja complejidad. |
| Segundez peirceana | El hecho bruto de resistencia o anomalía—como el pico de un sensor—que señala la presencia de una fuerza externa (malicia). | Fundamento para tratar las anomalías ignoradas como señales activas, no ruido pasivo. |
| Aritmética determinista de enteros | Operaciones matemáticas con fracciones exactas (pares de enteros) y conversión entera truncada, nunca con decimales de punto flotante. | Asegura puntuaciones bit-a-bit reproducibles en distintas arquitecturas de CPU. |
| Configuración inmutable | Una tabla de búsqueda (`_PENALTY_TABLE`) bloqueada como `frozenset`, cuyo contenido no puede alterarse en tiempo de ejecución. | Protege la integridad forense al evitar la manipulación en memoria de los valores de penalización. |
| Paradigma SolarWinds | Un artefacto forense firmado acompañado de múltiples anomalías descartadas que, en conjunto, crean una narrativa benigna artificialmente "limpia". | Caso de estudio motivador de la lógica de penalización. |

### Componentes del Módulo

| Componente | Tipo | Función |
|---|---|---|
| `NONE`, `WEAK`, `MODERATE`, `STRONG`, `CRITICAL` | Constantes | Niveles ordinales de fuerza de señal de malicia. Rangos discretos sin gradación de punto flotante. |
| `MaliceSignalStrength` | Clase | Encapsula la escala ordinal de malicia. Garantiza que todas las fuerzas de señal permanezcan como ordinales de tipo entero. |
| `OckhamPenaltyResult` | Clase | Registro de datos inmutable que almacena el resultado de un cálculo de penalización. Una vez creado, no puede modificarse. |
| `aggregate_malice_signal_strength()` | Función | Recolecta indicadores de malicia del pool de evidencia activo. Cada indicador porta un peso racional exacto (`Fraction` entre 0 y 1). La función los fusiona en una evaluación ordinal unificada. |
| `compute_adversarial_penalty()` | Función | Mide qué tan sospechosamente simple es la hipótesis benigna y le añade un costo de penalización determinista. |
| `display_confidence()` | Función | Convierte una puntuación interna de confianza exacta en un porcentaje de número entero (p. ej., 73 %) usando truncamiento (`int()`), evitando la exhibición en punto flotante y el redondeo del banquero. |

### Glosario

| Término | Definición |
|---|---|
| **Penalización adversarial** | Incremento de costo determinista añadido deliberadamente a una hipótesis benigna para compensar una simplicidad que el atacante pudo haber diseñado. |
| **`fractions.Fraction`** | Tipo de dato de Python que representa una razón exacta de dos enteros (numerador y denominador). Opera como la aritmética de fracciones simbólicas de álgebra básica, sin errores de redondeo. |
| **`frozenset`** | Colección inmutable. Dado que su contenido se fija en la creación, funciona como un sello de solo lectura que evita cambios accidentales o maliciosos en tiempo de ejecución de los parámetros de penalización. |
| **Escala ordinal** | Sistema de jerarquización (p. ej., NONE → CRITICAL) donde el orden importa pero no se asume que la distancia numérica entre rangos sea igual. No hay decimales entre rangos. |
| **Segundez peirceana** | En la semiótica de Charles Sanders Peirce, el modo de ser del hecho bruto o la resistencia. En informática forense, es el dato irreductible de una anomalía que se niega a ser disuelta por la narrativa más simple. |
| **Truncamiento** | Eliminación de cualquier resto fraccionario (p. ej., convertir 73,9 en 73). Para puntuaciones positivas es idéntico a la función piso matemática y produce salida determinista e independiente de la arquitectura. |

### 【Scientific Note】 / 【Nota Científica】
> **Peirce, Eco y Grice no son misticismo**
>
> La terminología tomada de C. S. Peirce, Umberto Eco y H. P. Grice se emplea aquí como ingeniería semiótica formal, no como especulación metafísica. Piense en un sensor físico: la **Segundez peirceana** no es más que el pico de voltaje cuando una sonda encuentra resistencia inesperada: una medición cruda antes de aplicar cualquier teoría. Los códigos de **Eco** y los máximas conversacionales de **Grice** actúan como protocolos de calibración: nos indican cómo interpretar ese pico en contexto. VIGÍA utiliza estos marcos como heurísticas deterministas—reglas que mapean artefactos forenses observados a estados lógicos. Son instrumentos matemáticos, no fuerzas ocultas.


---

РУССКИЙ:

---
## РУССКИЙ

### Что это за модуль?
Это детерминированный корректирующий движок внутри судебно-экспертного комплекса VIGÍA. Его цель — предотвратить следственную ловушку: искушённый противник целенаправленно конструирует инцидент так, чтобы простейшее объяснение выглядело как доброкачественная человеческая ошибка. Модуль обнаруживает, когда «слишком чистая» благонамеренная гипотеза искусственно занижает сложность, и штрафует её, направляя исследователя к выводу о злонамеренности.

Логика вдохновлена инцидентом SolarWinds, когда легитимно подписанная динамическая библиотека (DLL) в сочетании с пятью проигнорированными аномалиями породила изящно простое, но ложное объяснение. Модуль рассматривает такую подозрительную простоту как самодостаточное доказательство (феномен, соответствующий пирсовской категории Вторичности — Secondness). Все вычисления выполняются точной рациональной арифметикой на целых числах (`fractions.Fraction`), гарантируя идентичность итоговой оценки на любых компьютерах.

### Ключевые концепции

| Концепция | Определение простым языком | Роль в модуле |
|---|---|---|
| Адверсариальная бритва Оккама | Принцип, согласно которому в условиях атаки простейшее объяснение может быть преднамеренно подброшенной приманкой, а не истиной. | Определяет, когда следует подвергать сомнению упрощённые благонамеренные гипотезы. |
| Пирсовская Вторичность (Secondness) | Грубый факт сопротивления или аномалии — как всплеск показаний датчика — сигнализирующий о присутствии внешней силы (злонамеренности). | Обосновывает рассмотрение проигнорированных аномалий как активных сигналов, а не пассивного шума. |
| Детерминированная целочисленная арифметика | Математические операции с точными дробями (парами целых чисел) и усечённым целочисленным преобразованием, никогда — с плавающей запятой. | Обеспечивает битово-воспроизводимые оценки на любых архитектурах ЦПУ. |
| Неизменяемая конфигурация | Справочная таблица (`_PENALTY_TABLE`), зафиксированная как `frozenset`: её содержимое невозможно изменить во время выполнения. | Защищает судебную целостность, предотвращая подмену в памяти штрафных параметров. |
| Парадигма SolarWinds | Подписанный судебный артефакт в совокупности с множеством отброшенных аномалий, порождающих искусственно «чистую» благонамеренную картину. | Служит мотивирующим кейсом для логики начисления штрафа. |

### Компоненты модуля

| Компонент | Тип | Функция |
|---|---|---|
| `NONE`, `WEAK`, `MODERATE`, `STRONG`, `CRITICAL` | Константы | Порядковые уровни силы сигнала злонамеренности. Дискретные ранги без плавающей градации. |
| `MaliceSignalStrength` | Класс | Инкапсулирует порядковую шкалу злонамеренности. Гарантирует, что все силы сигналов остаются целочисленными порядковыми величинами. |
| `OckhamPenaltyResult` | Класс | Неизменяемая запись данных, хранящая результат расчёта штрафа. После создания изменению не подлежит. |
| `aggregate_malice_signal_strength()` | Функция | Собирает индикаторы злонамеренности из активного пула доказательств. Каждый индикатор несёт точный рациональный вес (`Fraction` от 0 до 1). Функция объединяет их в единую порядковую оценку. |
| `compute_adversarial_penalty()` | Функция | Измеряет, насколько подозрительно проста благонамеренная гипотеза, и добавляет к ней детерминированный штраф. |
| `display_confidence()` | Функция | Преобразует точное внутреннее значение уверенности в целочисленный процент (например, 73 %) посредством усечения (`int()`), избегая отображения чисел с плавающей запятой и банковского округления. |

### Глоссарий

| Термин | Определение |
|---|---|
| **Адверсариальный штраф** | Детерминированное приращение стоимости, целенаправленно добавляемое к благонамеренной гипотезе для компенсации простоты, которую противник мог спроектировать. |
| **`fractions.Fraction`** | Тип данных Python, представляющий точное отношение двух целых чисел (числителя и знаменателя). Работает как символьное дробное исчисление из школьной алгебры, не порождая ошибок округления. |
| **`frozenset`** | Неизменяемое множество. Поскольку его содержимое фиксируется при создании, оно действует как печать только для чтения, предотвращая случайные или злонамеренные изменения штрафных параметров во время работы. |
| **Порядковая шкала** | Система ранжирования (например, NONE → CRITICAL), в которой важен порядок, но числовое расстояние между рангами не предполагается равным. Между рангами нет десятичных дробей. |
| **Пирсовская Вторичность (Secondness)** | В семиотике Чарльза Сандерса Пирса — модус бытия грубого факта или сопротивления. В цифровой криминалистике это ирредуцируемый датум аномалии, который отказывается быть развеянным простейшим рассказом. |
| **Усечение (truncation)** | Отбрасывание любой дробной части (например, превращение 73,9 в 73). Для положительных оценок это тождественно функции пола и даёт детерминированный вывод, не зависящий от архитектуры. |

### 【Scientific Note】 / 【Научное примечание】
> **Терминология Пирса, Эко и Грайса — не мистицизм**
>
> Заимствованная из семиотики Ч. С. Пирса, Умберто **Эко** и Г. П. **Грайса** терминология используется здесь как формальная инженерная дисциплина, а не метафизическая спекуляция. Представьте физический датчик: **пирсовская Вторичность** — не что иное, как скачок напряжения при встрече зонда с неожиданным сопротивлением: сырые измерения до наложения теории. Коды **Эко** и разговорные максимы **Грайса** выступают протоколами калибровки: они сообщают, как интерпретировать этот скачок в контексте. VIGÍA применяет эти рамки как детерминированные эвристики — правила, отображающие наблюдаемые судебные артефакты на логические состояния. Это математические инструменты, а не оккультные силы.


---

中文:

Must include:
- 艾柯 (Umberto Eco)
- 格赖斯 (H.P. Grice)
- 取证工件 (forensic artifact, not 制品)
- 逻辑断裂 (logical break/fracture, not 裂缝)
- 【科学说明】box

Also: "display_confidence" uses int() truncated, not round.

Chinese phrasing:
- VIGÍA: keep as is.
- Ockham's Razor: 奥卡姆剃刀.
- Adversarial: 对抗性.
- Peircean Secondness: 皮尔斯第二性 (or 皮尔斯所言的“第二性”).
- Immutable: 不可变的.
- Frozenset: 不可变集合.
- Fraction: 精确分数 / 有理数类型. Use 精确有理数.
- Truncation: 截断.
- SolarWinds: SolarWinds事件.
- DLL: 动态链接库 (DLL).
- Ordinal: 序数的 / 序数量表.
- Malice: 恶意.
- Benign: 良性 / 善意的. 良性 hypothesis: 良性假设.
- Sensor analogy: 传感器.

Use 逻辑断裂 in a natural place. For example, in the "Adversarial Ockham's Razor" concept: "过度简化的良性叙事会造成逻辑断裂" or "攻击者设计的简单解释与真实证据之间存在逻辑断裂". Let's put it in the Key Concepts table or in the explanation.

Let's draft:

---
## 中文

### 本模块是什么？
本模块是 VIGÍA 取证框架内部的一个确定性校正引擎，旨在阻止一种调查陷阱：老练的对手会刻意设计一起事件，使得最简单的解释看起来像是无害的人为失误。该模块负责识别那些“过于干净”的良性故事是否被人为压低了成本，并对该假设施加惩罚，从而将调查人员导向“恶意”结论。

其逻辑灵感源自 SolarWinds 事件：一份经过合法签名的动态链接库（DLL）加上五处被忽略的异常，共同产生了一个看似优雅简洁、实则错误的解释。模块将这种可疑的简洁性本身视为证据（一种与 C. S. 皮尔斯“第二性”范畴相一致的现象）。所有计算均采用基于整数的精确有理数运算（`fractions.Fraction`），以确保不同计算机总能输出完全一致的评分。

### 核心概念

| 概念 | 通俗定义 | 在本模块中的作用 |
|---|---|---|
| 对抗性奥卡姆剃刀 | 在遭受攻击的环境下，最简单的解释可能是对手刻意 planted 的诱饵，而非真相。 | 决定何时应对过度简化的良性假设保持怀疑。 |
| 皮尔斯第二性 | 阻力或异常的原始事实——如同传感器上的电压尖峰——标志着外部力量（恶意）的存在。 | 为“将被忽略的异常视为主动信号而非被动噪声”提供理论基础。 |
| 确定性整数运算 | 使用精确分数（一对整数）及截断式整数转换完成数学运算，绝不使用浮点小数。 | 确保评分在不同 CPU 架构上实现按位可复现。 |
| 不可变配置 | 以 `frozenset` 锁定的查找表（`_PENALTY_TABLE`），其内容在运行期间无法更改。 | 防止惩罚参数在内存中被篡改，保障取证完整性。
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
