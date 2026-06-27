<!--
VIGIA Academic Documentation
Module: 7ed37665
Batch ID: vigia-doc-0077-7ed37665
Generated: 2026-05-20T14:56:47.861093+00:00
-->

# Module Documentation: `vigia/core/signal_mapper.py`

## ENGLISH

### What Is This Module?
The file `vigia/core/signal_mapper.py` is the causal-validation gate of the VIGIA digital-forensics pipeline. Its purpose is to take raw detection reports produced by multiple external instruments and convert them into validated **SignalOutput** objects.

Think of it as a laboratory quality-control step: before any measurement is recorded in the final log, it must pass a consistency check called the **Causal Closure Score (CCS)**. The CCS measures whether the set of incoming pieces of evidence forms a self-contained causal story (no missing links, no logical ruptures). If the score meets or exceeds the exact rational threshold of one-half (`≥ 1/2`), the signal is accepted; if the score is lower, the module forcibly returns an **ABSTAIN** verdict, which means "insufficient causal grounding—do not trust."

Because the module is designed for reproducible science, every numeric quantity inside the evidence dictionary is stored as an exact rational number (`Fraction` type) or as its string representation. No floating-point approximations are used anywhere, guaranteeing bit-identical results on every hardware platform.

### Key Concepts

| Concept | Plain-Language Definition | Role in the Deterministic System |
|---|---|---|
| **Causal Closure Score (CCS)** | A rational metric (0 to 1) indicating how completely a set of signals closes its own causal chain. A value of 1 means perfect closure—no external gaps or logical ruptures remain. | Computed with integer-ratio arithmetic; compared against `CCS_THRESHOLD = Fraction(1, 2)`. |
| **CCS Gate** | The decision boundary that acts like a low-pass filter for forensic data. It attenuates high-noise, inconsistent, or synthetically injected signals. | If `ccs < 1/2`, the output is forced to `ABSTAIN`; otherwise the signal is mapped normally. |
| **ABSTAIN State** | A deliberate null decision ("refuse to answer") rather than a true/false classification. | `CCS_ABSTAIN_Z` and `CCS_ABSTAIN_CONF` supply the integer status code and confidence string. |
| **SignalOutput** | A validated forensic artifact that bundles the final decision, raw evidence pointers, and provenance metadata. | Produced by `from_ccs()` and tracked historically via `get_history()`. |
| **Raw Signal** | An unvalidated detection record arriving from an external tool. | Input format is a list of dictionaries; every numeric value must be a `Fraction` or `str`. |
| **Anti-Deepfake Gate** | A security firewall that prevents synthetically generated media from introducing false causal dependencies. | Low causal closure is the tell-tale signature of deepfake manipulation; the gate rejects it automatically. |
| **Deterministic Integer Arithmetic** | Exact computation using integer numerators and denominators, eliminating platform-dependent rounding. | The module never uses floating-point (`float`) types; all values are exact rationals or strings. |

### Glossary

- **Causal Closure**: The epistemic property of an evidence set that requires every effect to be accounted for by an internal cause, leaving no unbridged logical rupture.
- **Signal Mapper**: The translation interface that homogenizes heterogeneous tool outputs into standardized, auditable forensic artifacts.
- **Low-Pass Filter (analogical)**: A conceptual filter borrowed from electronics; here it denotes the suppression of rapidly varying, unsupported causal claims while allowing well-grounded, slowly varying signals to pass.
- **ABSTAIN**: A censored non-decision used to protect downstream analyses from propagating uncertain or contaminated data.
- **Deepfake**: A synthetic media artifact produced by deep-learning generative models; treated by the system as causally inconsistent with authentic capture devices.
- **Fraction / Rational Arithmetic**: A number representation based on integer pairs (numerator, denominator), ensuring that operations such as threshold comparison (`≥ 1/2`) are exact and reproducible.

### 【Scientific Note】

> **Semiotics is Sensor Calibration, Not Mysticism**
>
> The module's documentation borrows terminology from Charles Sanders **Peirce** (abductive inference), Umberto **Eco** (sign systems), and H. Paul **Grice** (cooperative maxims). In an interdisciplinary forensics environment, these terms are sometimes mistaken for metaphysical speculation. They are not.
>
> **Sensor Analogy**: Treat each raw signal as a voltage reading from an uncalibrated probe.
> - **Peirce's abduction** is the formation of the best explanatory hypothesis for that voltage (e.g., "this peak indicates compound X").
> - **Eco's semiotics** is the codebook that maps the raw voltage into a symbolic label (e.g., 3.3 V → "positive").
> - **Grice's maxims** are the quality-control rules that discard readings violating relevance or truthfulness (e.g., a negative-resistance value from a miswired sensor).
>
> The CCS gate performs exactly the same operation as a **validity mask on a sensor array**: it filters out readings that fail coherence checks. Causal closure is therefore the forensic equivalent of verifying that all sensors in an array agree within calibration tolerance before accepting the measurement vector. There is no mysticism—only deterministic quality control.

---

## ESPAÑOL

### ¿Qué es este módulo?
El archivo `vigia/core/signal_mapper.py` es la compuerta de validación causal del pipeline forense VIGIA. Su función consiste en tomar los informes de detección brutos generados por múltiples instrumentos externos y convertirlos en objetos **SignalOutput** validados.

Piénselo como un paso de control de calidad de laboratorio: antes de que cualquier medición se registre en el log final, debe superar una prueba de coherencia denominada **Causal Closure Score (CCS)**. El CCS mide si el conjunto de evidencias entrantes forma una narrativa causal autocontenida (sin eslabones faltantes ni rupturas lógicas). Si la puntuación alcanza o supera el umbral racional exacto de un medio (`≥ 1/2`), la señal se acepta; si es inferior, el módulo devuelve forzosamente un veredicto de **ABSTAIN** ("abstenerse"), lo cual significa: "fundamentación causal insuficiente—no confiar".

Dado que el módulo está diseñado para ciencia reproducible, toda cantidad numérica dentro del diccionario de evidencia se almacena como un número racional exacto (tipo `Fraction`) o como su representación en cadena de texto. No se emplean aproximaciones en ninguna parte, lo que garantiza resultados idénticos bit a bit en cualquier plataforma de hardware.

### Conceptos Clave

| Concepto | Definición en lenguaje sencillo | Rol en el sistema determinista |
|---|---|---|
| **Causal Closure Score (CCS)** | Métrica racional (de 0 a 1) que indica qué tan completamente un conjunto de señales cierra su propia cadena causal. Un valor de 1 significa cierre perfecto: no quedan vacíos externos ni rupturas lógicas. | Se computa con aritmética de razones enteras; se compara contra `CCS_THRESHOLD = Fraction(1, 2)`. |
| **CCS Gate** | Frontera de decisión que actúa como filtro pasabajos conceptual para datos forenses. Atenúa señales ruidosas, inconsistentes o inyectadas sintéticamente. | Si `ccs < 1/2`, la salida se fuerza a `ABSTAIN`; de lo contrario, la señal se mapea normalmente. |
| **Estado ABSTAIN** | Decisión nula deliberada ("me niego a responder") en lugar de una clasificación verdadero/falso. | `CCS_ABSTAIN_Z` y `CCS_ABSTAIN_CONF` proporcionan el código de estado entero y la cadena de confianza. |
| **SignalOutput** | Artefacto forense validado que agrupa la decisión final, punteros a la evidencia bruta y metadatos de procedencia. | Producido por `from_ccs()` y rastreado históricamente mediante `get_history()`. |
| **Señal Bruta (Raw Signal)** | Registro de detección no validado proveniente de una herramienta externa. | El formato de entrada es una lista de diccionarios; todo valor numérico debe ser `Fraction` o `str`. |
| **Anti-Deepfake Gate** | Cortafuegos de seguridad que impide que medios generados sintéticamente introduzcan dependencias causales falsas. | El bajo cierre causal es la huella distintiva de la manipulación deepfake; la compuerta la rechaza automáticamente. |
| **Aritmética Entera Determinista** | Computación exacta mediante numeradores y denominadores enteros, eliminando el redondeo dependiente de la plataforma. | El módulo nunca usa tipos de punto flotante (`float`); todos los valores son racionales exactos o cadenas. |

### Glosario

- **Cierre Causal**: Propiedad epistémica de un conjunto de evidencias que exige que cada efecto se explique por una causa interna, sin dejar rupturas lógicas sin puentear.
- **Mapeador de Señales**: Interfaz de traducción que homogeneiza salidas heterogéneas de herramientas en artefactos forenses estandarizados y auditables.
- **Filtro Pasabajos (analógico)**: Filtro conceptual tomado de la electrónica; aquí denota la supresión de afirmaciones causales rápidamente variables y sin sustento, permitiendo el paso de señales bien fundamentadas.
- **ABSTAIN (Abstenerse)**: Decisión censurada de no-decisión utilizada para proteger los análisis posteriores de propagar datos inciertos o contaminados.
- **Deepfake**: Artefacto de medio sintético producido por modelos generativos de aprendizaje profundo; el sistema lo trata como causalmente inconsistente con dispositivos de captura auténticos.
- **Fracción / Aritmética Racional**: Representación numérica basada en pares de enteros (numerador, denominador), que asegura que operaciones como la comparación de umbrales (`≥ 1/2`) sean exactas y reproducibles.

### 【Nota Científica】

> **La semiótica es calibración de sensores, no misticismo**
>
> La documentación del módulo toma prestada terminología de Charles Sanders **Peirce** (inferencia abductiva), Umberto **Eco** (sistemas de signos) y H. Paul **Grice** (máximas cooperativas). En un entorno forense interdisciplinario, estos términos a veces se confunden con especulación metafísica. No lo son.
>
> **Analogía del sensor**: Considere cada señal bruta como una lectura de voltaje de una sonda sin calibrar.
> - La **abducción de Peirce** es la formación de la hipótesis explicativa más plausible para ese voltaje (p. ej., "este pico indica el compuesto X").
> - La **semiótica de Eco** es el código que mapea el voltaje bruto hacia una etiqueta simbólica (p. ej., 3,3 V → "positivo").
> - Las **máximas de Grice** son las reglas de control de calidad que descartan lecturas que violan relevancia o veracidad (p. ej., un valor de resistencia negativa proveniente de un sensor mal cableado).
>
> La compuerta CCS realiza exactamente la misma operación que una **máscara de validez sobre un arreglo de sensores**: filtra las lecturas que fallan las verificaciones de coherencia. El cierre causal es, por tanto, el equivalente forense de verificar que todos los sensores de un arreglo concuerden dentro de la tolerancia de calibración antes de aceptar el vector de medición. No hay misticismo, solo control de calidad determinista.

---

## РУССКИЙ

### Что представляет собой этот модуль?
Файл `vigia/core/signal_mapper.py` — это вентиль проверки причинной замкнутости в цифровой судебной системе VIGIA. Его назначение — принимать сырые отчёты детекторов от нескольких внешних инструментов и преобразовывать их в валидированные объекты **SignalOutput**.

Воспринимайте его как лабораторный этап контроля качества: прежде чем любое измерение будет зафиксировано в финальном журнале, оно должно пройти проверку согласованности под названием **Causal Closure Score (CCS)**. CCS измеряет, образует ли множество поступающих доказательств самодостаточную причинную цепочку (без пропущенных звеньев и логических разрывов). Если показатель достигает или превышает точный рациональный порог одна вторая (`≥ 1/2`), сигнал принимается; если ниже — модуль принудительно возвращает вердикт **ABSTAIN** («воздержаться»), что означает «недостаточное причинное обоснование — не доверять».

Поскольку модуль предназначен для воспроизводимой науки, каждое числовое значение в словаре доказательств хранится как точная рациональная дробь (тип `Fraction`) или в виде её строкового представления. Нигде не используются приближённые вычисления, что гарантирует побитово идентичные результаты на любой аппаратной платформе.

### Ключевые понятия

| Понятие | Определение простым языком | Роль в детерминированной системе |
|---|---|---|
| **Causal Closure Score (CCS)** | Рациональная метрика (от 0 до 1), показывающая, насколько полно множество сигналов замыкает собственную причинную цепь. Значение 1 означает идеальную замкнутость: внешних пробелов и логических разрывов не остаётся. | Вычисляется целочисленным дробным арифметическим действием; сравнивается с `CCS_THRESHOLD = Fraction(1, 2)`. |
| **CCS Gate** | Решающая граница, действующая как фильтр нижних частот для судебных данных. Ослабляет зашумлённые, противоречивые или синтетически внедрённые сигналы. | При `ccs < 1/2` выход принудительно устанавливается в `ABSTAIN`; иначе сигнал проходит обычное отображение. |
| **Состояние ABSTAIN** | Осознанное нулевое решение («отказываюсь отвечать») вместо классификации истина/ложь. | `CCS_ABSTAIN_Z` и `CCS_ABSTAIN_CONF` задают целочисленный код состояния и строку достоверности. |
| **SignalOutput** | Валидированный судебный артефакт, объединяющий итоговое решение, указатели на сырые доказательства и метаданные происхождения. | Формируется функцией `from_ccs()`; история отслеживается через `get_history()`. |
| **Сырой сигнал (Raw Signal)** | Невалидированная запись обнаружения, поступающая от внешнего инструмента. | Входной формат — список словарей; каждое числовое значение должно быть `Fraction` или `str`. |
| **Anti-Deepfake Gate** | Защитный барьер, предотвращающий внедрение синтетически сгенерированных медиа с ложными причинными зависимостями. | Низкая причинная замкнутость — характерный признак манипуляции deepfake; вентиль отбрасывает такой сигнал автоматически. |
| **Детерминированная целочисленная арифметика** | Точное вычисление с использованием целых числителей и знаменателей, исключающее зависимое от платформы округление. | Модуль никогда не использует типы с плавающей точкой (`float`); все значения — точные дроби или строки. |

### Глоссарий

- **Причинная замкнутость (Causal Closure)**: Эпистемологическое свойство набора доказательств, требующее, чтобы каждый эффект был объяснён внутренней причиной без незамкнутых логических разрывов.
- **Маппер сигналов (Signal Mapper)**: Трансляционный интерфейс, который приводит разнородные выходы инструментов к стандартизированным, поддающимся аудиту судебным артефактам.
- **Фильтр нижних частот (концептуальный)**: Концепция, заимствованная из электроники; здесь она обозначает подавление быстро меняющихся, неподтверждённых причинных утверждений и пропускание хорошо обоснованных сигналов.
- **ABSTAIN (Воздержаться)**: Цензурируемое отсутствие решения, защищающее последующие анализы от распространения сомнительных или заражённых данных.
- **Deepfake**: Синтетический медиа-артефакт, созданный генеративными моделями глубокого обучения; система рассматривает его как причинно несогласованный с реальными устройствами захвата.
- **Fraction / Рациональная арифметика**: Представление чисел в виде пар целых (числитель, знаменатель), гарантирующее точность операций вроде сравнения порога (`≥ 1/2`) и воспроизводимость результатов.

### 【Научное примечание】

> **Семиотика — это калибровка датчиков, а не мистицизм**
>
> Документация модуля заимствует терминологию Чарльза Сандерса **Пирса** (абдуктивный вывод), Умберто **Эко** (системы знаков) и Герберта Пола **Грайса** (кооперативные максимы). В междисциплинарной судебной среде эти термины иногда ошибочно принимают за метафизическую спекуляцию. Это не так.
>
> **Аналогия с датчиком**: Воспринимайте каждый сырой сигнал как напряжение на некалиброванном зонде.
> - **Абдукция Пирса** — это формирование наилучшей объяснительной гипотезы для этого напряжения (например, «этот пик указывает на соединение X»).
> - **Семиотика Эко** — это кодовая книга, отображающая сырое напряжение на символическую метку (например, 3,3 В → «положительно»).
> - **Максимы Грайса** — это правила контроля качества, отбрасывающие показания, нарушающие релевантность или истинность (например, отрицательное сопротивление от неправильно подключённого датчика).
>
> Вентиль CCS выполняет в точности ту же операцию, что и **маска валидности на массиве датчиков**: он отфильтровывает показания, не прошедшие проверку когерентности. Таким образом, причинная замкнутость — это судебный эквивалент проверки того, что все датчики в массиве согласуются в пределах допуска калибровки, прежде чем принять вектор измерений. Никакого мистицизма — только детерминированный контроль качества.

---

## 中文

### 本模块是什么？
文件 `vigia/core/signal_mapper.py` 是 VIGIA 数字取证流水线中的因果闭合校验门。其功能是将多台外部仪器生成的原始检测报告转换为经过验证的 **SignalOutput**（信号输出）对象。

您可以把它理解为实验室中的质量控制环节：在任何测量结果被记入最终日志之前，它必须先通过一项名为 **Causal Closure Score（CCS，因果闭合分数）** 的一致性检验。CCS 衡量的是输入证据集合是否构成了一个自我完备的因果叙事（没有缺失环节，也没有逻辑断裂）。如果该分数达到或超过精确的有理数阈值二分之一（`≥ 1/2`），信号即被接受；若低于该阈值，模块将强制返回 **ABSTAIN**（弃权）裁决，其含义是"因果根基不足——不可信"。

由于本模块面向可复现科学设计，证据字典中的所有数值量均以精确有理数（`Fraction` 类型）或其字符串形式存储。任何位置均不使用近似值，从而确保在任何硬件平台上都能获得比特级一致的结果。

### 关键概念

| 概念 | 通俗定义 | 在确定性系统中的作用 |
|---|---|---|
| **因果闭合分数（CCS）** | 0 到 1 之间的有理数度量，指示一组信号在多大程度上闭合了自身的因果链。值为 1 表示完美闭合：不存在外部空白或逻辑断裂。 | 通过整数比值运算计算；与 `CCS_THRESHOLD = Fraction(1, 2)` 进行比较。 |
| **CCS 门（CCS Gate）** | 对取证数据起到类似低通滤波器作用的决策边界。它会削弱高噪声、不一致或被注入的合成信号。 | 若 `ccs < 1/2`，输出被强制置为 `ABSTAIN`；否则信号正常通过。 |
| **ABSTAIN 状态** | 一种刻意的空决策（"拒绝回答"），而非真/假分类。 | `CCS_ABSTAIN_Z` 与 `CCS_ABSTAIN_CONF` 提供整数状态码与置信度字符串。 |
| **SignalOutput（信号输出）** | 经过验证的取证工件，打包了最终裁决、原始证据指针及溯源元数据。 | 由 `from_ccs()` 生成，并通过 `get_history()` 进行历史追踪。 |
| **原始信号（Raw Signal）** | 来自外部工具的未经验证的检测记录。 | 输入格式为字典列表；所有数值必须是 `Fraction` 或 `str`。 |
| **反深度伪造门（Anti-Deepfake Gate）** | 防止合成生成媒体引入虚假因果依赖的安全防火墙。 | 低因果闭合是深度伪造操纵的显著特征；该门自动予以拒绝。 |
| **确定性整数运算** | 使用整数分子与分母进行的精确计算，消除了依赖平台的舍入误差。 | 模块绝不使用浮点（`float`）类型；所有值均为精确有理数或字符串。 |

### 术语表

- **因果闭合（Causal Closure）**：一组证据的认识论属性，要求每个效应都能由内部原因解释，不留未弥合的逻辑断裂。
- **信号映射器（Signal Mapper）**：将异构工具输出转换为标准化、可审计的取证工件的翻译接口。
- **低通滤波器（概念借用）**：借自电子学的概念隐喻；此处指抑制快速变化、缺乏支撑的因果断言，同时允许基础牢固、变化缓慢的信号通过。
- **ABSTAIN（弃权）**：一种经过审查的不决策，用于保护下游分析免受传播不确定或被污染的数据。
- **深度伪造（Deepfake）**：由深度学习生成模型制作的合成媒体工件；系统将其视为与真实采集设备在因果上不一致的对象。
- **分数 / 有理数运算（Fraction / Rational Arithmetic）**：基于整数对（分子、分母）的数值表示，确保诸如阈值比较（`≥ 1/2`）等操作精确且可复现。

### 【科学说明】

> **符号学是传感器校准，而非神秘主义**
>
> 本模块文档借用了查尔斯·桑德斯·**皮尔斯**（溯因推理）、翁贝托·**艾柯**（符号系统）以及 H·保罗·**格赖斯**（合作准则）的术语。在跨学科取证环境中，这些术语有时被误认为是形而上学思辨。事实并非如此。
>
> **传感器类比**：将每条原始信号视为来自未校准探头的电压读数。
> - **皮尔斯的溯因**就是为该电压形成最佳解释假说（例如："这个峰值指示化合物 X"）。
> - **艾柯的符号学**是将原始电压映射为符号标签的代码本（例如：3.3 V → "正"）。
> - **格赖斯的准则**是丢弃违反相关性或真实性读数的质量控制规则（例如：来自接线错误传感器的负阻值）。
>
> CCS 门执行的正是**传感器阵列上有效性掩码**的同等操作：过滤掉未通过一致性检查的读数。因此，因果闭合是取证领域中"在接受测量向量之前验证阵列中所有传感器均在校准容差内一致"的等价物。没有神秘主义——只有确定性质量控制。

---

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
