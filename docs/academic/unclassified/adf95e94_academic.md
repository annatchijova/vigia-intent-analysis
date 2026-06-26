<!--
VIGIA Academic Documentation
Module: adf95e94
Batch ID: vigia-doc-0067-adf95e94
Generated: 2026-05-20T14:56:47.858908+00:00
-->

## ENGLISH

### What Is This Module?
This module is a deterministic correction engine inside the VIGÍA forensic framework. Its purpose is to stop an investigative trap: a sophisticated attacker deliberately stages an incident so that the simplest explanation appears to be innocent human error. The module detects when a "too-clean" benign story is artificially cheap and punishes that hypothesis, steering the investigator toward a conclusion of malice.

The logic is inspired by the SolarWinds breach, where a legitimately signed dynamic-link library (DLL) plus five ignored anomalies produced an explanation that looked elegantly simple—yet was wrong. The module treats such suspicious simplicity as evidence in its own right (a phenomenon aligned with C. S. Peirce's category of Secondness). All calculations use exact integer-based rational arithmetic (`fractions.Fraction`) to guarantee that two different computers always reach the identical score.

### Key Concepts

| Concept | Plain-Language Definition | Role in the Module |
|---|---|---|
| Adversarial Ockham's Razor | The principle that, under attack, the simplest explanation may be a deliberately planted decoy rather than the truth. | Governs when to distrust low-complexity benign hypotheses. |
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
| `display_confidence()` | Function | Converts an exact internal confidence score into a whole-number percentage (e.g., 73%) using truncation (`int()`), avoiding floating-point display and banker's rounding. |

### Glossary

| Term | Definition |
|---|---|
| **Adversarial Penalty** | A deterministic cost increment deliberately added to a benign hypothesis to compensate for simplicity that an attacker may have engineered. |
| **`fractions.Fraction`** | A Python data type representing an exact ratio of two integers (numerator and denominator). It operates like symbolic fraction arithmetic taught in basic algebra, producing no rounding errors. |
| **`frozenset`** | An immutable collection. Because its contents are fixed at creation, it functions as a read-only seal, preventing accidental or malicious runtime changes to penalty parameters. |
| **Ordinal Scale** | A ranking system (e.g., NONE → CRITICAL) where order matters but the numerical distance between ranks is not assumed to be equal. There are no decimals between ranks. |
| **Peircean Secondness** | In the semiotics of Charles Sanders Peirce, the mode of being of brute fact or resistance. In digital forensics, it is the irreducible datum of an anomaly that refuses to be explained away by the simplest story. |
| **Truncation** | The removal of any fractional remainder (e.g., turning 73.9 into 73). For positive scores this is identical to the mathematical floor function and yields deterministic, architecture-independent output. |

> **【Scientific Note】**
> The terminology borrowed from C. S. Peirce, Umberto **Eco**, and H. P. **Grice** is employed here as formal semiotic engineering, not metaphysical speculation. Think of a physical sensor: **Peircean Secondness** is nothing more than the voltage spike when a probe encounters unexpected resistance—a raw measurement before any theory is applied. **Eco's** codes and **Grice's** conversational maxims act as calibration protocols: they tell us how to interpret that voltage spike in context. VIGÍA uses these frameworks as deterministic heuristics—rules that map observed forensic artifacts to logical states. They are mathematical instruments, not occult forces.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

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
| `display_confidence()` | Función | Convierte una puntuación interna de confianza exacta en un porcentaje de número entero (p. ej., 73%) usando truncamiento (`int()`), evitando la exhibición en punto flotante y el redondeo del banquero. |

### Glosario

| Término | Definición |
|---|---|
| **Penalización adversarial** | Incremento de costo determinista añadido deliberadamente a una hipótesis benigna para compensar una simplicidad que el atacante pudo haber diseñado. |
| **`fractions.Fraction`** | Tipo de dato que representa una razón exacta de dos enteros (numerador y denominador). Opera como la aritmética de fracciones simbólicas de álgebra básica, sin errores de redondeo. |
| **`frozenset`** | Colección inmutable. Dado que su contenido se fija en la creación, funciona como un sello de solo lectura que evita cambios accidentales o maliciosos en tiempo de ejecución de los parámetros de penalización. |
| **Escala ordinal** | Sistema de jerarquización (p. ej., NONE → CRITICAL) donde el orden importa pero no se asume que la distancia numérica entre rangos sea igual. No hay decimales entre rangos. |
| **Segundez peirceana** | En la semiótica de Charles Sanders Peirce, el modo de ser del hecho bruto o la resistencia. En informática forense, es el dato irreductible de una anomalía que se niega a ser disuelta por la narrativa más simple. |
| **Truncamiento** | Eliminación de cualquier resto fraccionario (p. ej., convertir 73,9 en 73). Para puntuaciones positivas es idéntico a la función piso matemática y produce salida determinista e independiente de la arquitectura. |

> **【Nota Científica】**
> La terminología tomada de C. S. Peirce, Umberto Eco y H. P. Grice se emplea aquí como ingeniería semiótica formal, no como especulación metafísica. Piense en un sensor físico: la **Segundez peirceana** no es más que el pico de voltaje cuando una sonda encuentra resistencia inesperada: una medición cruda antes de aplicar cualquier teoría. Los códigos de **Eco** y las máximas conversacionales de **Grice** actúan como protocolos de calibración: nos indican cómo interpretar ese pico en contexto. VIGÍA utiliza estos marcos como heurísticas deterministas—reglas que mapean artefactos forenses observados a estados lógicos. Son instrumentos matemáticos, no fuerzas ocultas.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

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
| `display_confidence()` | Функция | Преобразует точное внутреннее значение уверенности в целочисленный процент (например, 73%) посредством усечения (`int()`), избегая отображения чисел с плавающей запятой и банковского округления. |

### Глоссарий

| Термин | Определение |
|---|---|
| **Адверсариальный штраф** | Детерминированное приращение стоимости, целенаправленно добавляемое к благонамеренной гипотезе для компенсации простоты, которую противник мог спроектировать. |
| **`fractions.Fraction`** | Тип данных, представляющий точное отношение двух целых чисел (числителя и знаменателя). Работает как символьное дробное исчисление из школьной алгебры, не порождая ошибок округления. |
| **`frozenset`** | Неизменяемое множество. Поскольку его содержимое фиксируется при создании, оно действует как печать только для чтения, предотвращая случайные или злонамеренные изменения штрафных параметров во время работы. |
| **Порядковая шкала** | Система ранжирования (например, NONE → CRITICAL), в которой важен порядок, но числовое расстояние между рангами не предполагается равным. Между рангами нет десятичных дробей. |
| **Пирсовская Вторичность (Secondness)** | В семиотике Чарльза Сандерса Пирса — модус бытия грубого факта или сопротивления. В цифровой криминалистике это ирредуцируемый датум аномалии, который отказывается быть развеянным простейшим рассказом. |
| **Усечение (truncation)** | Отбрасывание любой дробной части (например, превращение 73,9 в 73). Для положительных оценок это тождественно функции пола и даёт детерминированный вывод, не зависящий от архитектуры. |

> **【Научное примечание】**
> Заимствованная из семиотики Ч. С. Пирса, Умберто **Эко** и Г. П. **Грайса** терминология используется здесь как формальная инженерная дисциплина, а не метафизическая спекуляция. Представьте физический датчик: **пирсовская Вторичность** — не что иное, как скачок напряжения при встрече зонда с неожиданным сопротивлением: сырые измерения до наложения теории. Коды **Эко** и разговорные максимы **Грайса** выступают протоколами калибровки: они сообщают, как интерпретировать этот скачок в контексте. VIGÍA применяет эти рамки как детерминированные эвристики — правила, отображающие наблюдаемые судебные артефакты на логические состояния. Это математические инструменты, а не оккультные силы.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## 中文

### 本模块是什么？
本模块是 VIGÍA 取证框架内部的一个确定性校正引擎，旨在阻止一种调查陷阱：老练的对手会刻意设计一起事件，使得最简单的解释看起来像是无害的人为失误。该模块负责识别那些"过于干净"的良性故事是否被人为压低了成本，并对该假设施加惩罚，从而将调查人员导向"恶意"结论。

其逻辑灵感源自 SolarWinds 事件：一份经过合法签名的动态链接库（DLL）加上五处被忽略的异常，共同产生了一个看似优雅简洁、实则错误的解释。模块将这种可疑的简洁性本身视为证据（一种与 C. S. 皮尔斯"第二性"范畴相一致的现象）。所有计算均采用基于整数的精确有理数运算（`fractions.Fraction`），以确保不同计算机总能输出完全一致的评分。

### 核心概念

| 概念 | 通俗定义 | 在本模块中的作用 |
|---|---|---|
| 对抗性奥卡姆剃刀 | 在遭受攻击的环境下，最简单的解释可能是对手刻意植入的诱饵，而非真相。 | 决定何时应对过度简化的良性假设保持怀疑。 |
| 皮尔斯第二性 | 阻力或异常的原始事实——如同传感器上的电压尖峰——标志着外部力量（恶意）的存在。 | 为"将被忽略的异常视为主动信号而非被动噪声"提供理论基础。 |
| 确定性整数运算 | 使用精确分数（一对整数）及截断式整数转换完成数学运算，绝不使用浮点小数。 | 确保评分在不同 CPU 架构上实现按位可复现。 |
| 不可变配置 | 以 `frozenset` 锁定的查找表（`_PENALTY_TABLE`），其内容在运行期间无法更改。 | 防止惩罚参数在内存中被篡改，保障取证完整性。 |
| SolarWinds 范式 | 经合法签名的取证工件叠加多项被忽视的异常，共同制造出一个人为的"干净"良性叙事。 | 作为惩罚逻辑的动机性案例研究。 |

### 模块组件

| 组件 | 类型 | 功能 |
|---|---|---|
| `NONE`, `WEAK`, `MODERATE`, `STRONG`, `CRITICAL` | 常量 | 恶意信号强度的序数等级。无浮点渐变的离散等级。 |
| `MaliceSignalStrength` | 类 | 封装恶意信号的序数量表。保证所有信号强度保持整数类型的序数。 |
| `OckhamPenaltyResult` | 类 | 存储惩罚计算结果的不可变数据记录。一经创建，不可修改。 |
| `aggregate_malice_signal_strength()` | 函数 | 从活跃证据池中收集恶意指标。每个指标携带精确有理数权重（0 到 1 之间的 `Fraction`）。该函数将它们合并为统一的序数评估。 |
| `compute_adversarial_penalty()` | 函数 | 衡量良性假设的可疑简洁程度，并向其添加确定性惩罚成本。 |
| `display_confidence()` | 函数 | 使用截断方式（`int()`）将精确内部置信度评分转换为整数百分比（如 73%），避免浮点显示和银行家舍入。 |

### 词汇表

| 术语 | 定义 |
|---|---|
| **对抗性惩罚** | 刻意添加到良性假设中的确定性成本增量，用于补偿对手可能人为设计的简洁性。 |
| **`fractions.Fraction`** | 表示两个整数（分子和分母）的精确比值的数据类型。其工作方式如同基础代数中教授的符号分数运算，不产生舍入误差。 |
| **`frozenset`** | 不可变集合。由于其内容在创建时固定，它充当只读封印，防止运行时对惩罚参数进行意外或恶意更改。 |
| **序数量表** | 一种排序系统（如 NONE → CRITICAL），其中顺序重要，但各等级之间的数值距离不假设为相等。等级之间没有小数。 |
| **皮尔斯第二性** | 在查尔斯·桑德斯·皮尔斯的符号学中，即原始事实或阻力的存在方式。在数字取证中，它是异常的不可化约数据，拒绝被最简单的叙事解释消解。 |
| **截断法** | 去除任何分数余数（如将 73.9 转为 73）。对于正数评分，这等同于数学取整函数，产生与体系结构无关的确定性输出。 |

> **【科学说明】**
> 皮尔斯（C. S. Peirce）、**艾柯**（Umberto Eco）与**格赖斯**（H. P. Grice）的术语在本模块中作为形式化符号学工程使用，而非形而上学思辨。请设想一个物理传感器：**皮尔斯第二性**不过是探针遇到意外阻力时产生的电压尖峰——这是理论介入之前的原始测量值。**艾柯**的编码与**格赖斯**的会话准则充当校准协议：它们告诉我们如何在具体情境中解读该电压尖峰。VIGÍA 将这些框架用作确定性启发式规则——将观测到的取证工件映射到逻辑状态的规则。它们是数学工具，而非神秘力量。

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
