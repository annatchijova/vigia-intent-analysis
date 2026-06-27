<!--
VIGIA Academic Documentation
Module: 987f4f2e
Batch ID: vigia-doc-0062-987f4f2e
Generated: 2026-05-20T14:56:47.857823+00:00
-->

# Module Documentation: `vigia/core/llm_backend.py`

## ENGLISH

### What Is This Module?
`vigia/core/llm_backend.py` (engine reference: `llm_backend_v2.py`) is the **Unified LLM Backend with Capability-Based Graceful Degradation**. It acts as a deterministic dispatch layer for digital forensic analysis. Instead of sending every task to a monolithic neural model, the module classifies both the task and the backend into discrete, integer-ordered capability levels. If a backend lacks the required integer rank, the system does not fail; it steps down to a lower, deterministic processing tier. This guarantees that evidence processing remains reproducible and never depends on stochastic floating-point guesses.

### Key Concepts

| Concept | Integer Rank / Type | Description |
|---|---|---|
| **FIRSTNESS_ONLY** | 1 | Pure description of forensic artifacts. No interpretation. |
| **ANOMALY_DETECTION** | 2 | Description plus deterministic anomaly flags (logical breaks). |
| **CAUSAL_REASONING** | 3 | Above plus abductive inference via symbolic engine. |
| **FULL_SEMIOTIC** | 4 | Full chain including causal and semiotic closure. |
| **BackendCapability** | Integer enum | Strictly increasing ladder. Rank *N* permits tasks ≤ *N*. |
| **Graceful Degradation** | Integer comparison | If a backend lacks rank *R*, the task is rerouted using exact integer threshold checks (`capability_level >= task_level`). |
| **Deterministic Fallback** | Integer arithmetic | Symbolic or rule-based rescue that never uses floating-point probabilistic sampling. |
| **Devil's Advocate (Gorgias)** | Deterministic refutation | Mandatory contradiction stage run by a symbolic logic engine, never by an LLM. |

### Functional API Overview

| Function | Required Capability | Role | Fallback Mechanism |
|---|---|---|---|
| `analyze_firstness()` | ≥ 1 (any backend) | Generates raw, uninterpreted description of evidence. | None required. |
| `analyze_secondness()` | ≥ 2 | Detects anomalies and **logical breaks** using deterministic tools; may wrap findings in LLM narration if available. | Deterministic integer-threshold anomaly detector. |
| `analyze_thirdness()` | ≥ 3 | Performs abduction: selects best causal explanation. | Symbolic engine with integer-rule unification if backend lacks `CAUSAL_REASONING`. |
| `generate_devil_advocate()` | N/A (always Gorgias) | Produces formal refutation of the current hypothesis. | **Never** an LLM; always deterministic logical attack. |

### Deterministic Integer Arithmetic
All capability comparisons use exact integer ordering (1 < 2 < 3 < 4). There are no floating-point confidence thresholds, no probabilistic routing scores, and no continuous activation functions. A backend either possesses an integer rank or it does not. Fallback decisions are computed by discrete state transitions in a finite-state machine, ensuring bitwise-reproducible behavior across executions.

### 【Scientific Note】
The terminology of Peirce (Firstness, Secondness, Thirdness), Eco, and Grice used herein is not mysticism or literary flourish. It functions exactly like the processing pipeline of a scientific sensor: **Firstness** corresponds to raw, uninterpreted voltage (description); **Secondness** corresponds to a threshold breach or deviation flag (anomaly detection); **Thirdness** corresponds to the calibrated diagnostic model that explains why the deviation occurred (abductive inference). The "Devil's Advocate" is a redundant sensor run under opposite assumptions to check for systematic bias. These are deterministic, discrete operational stages—integer states in a finite-state machine—not esoteric philosophy.

### Glossary
- **BackendCapability**: An integer enumeration that assigns each backend a strictly increasing rank. A backend at rank *N* can execute all tasks of rank ≤ *N*.
- **Graceful Degradation**: The system's ability to step down to a lower integer capability when a higher one is unavailable, preserving the chain of custody.
- **Deterministic Fallback**: A non-probabilistic rescue mechanism using exact integer arithmetic and symbolic rules instead of neural generation.
- **Firstness**: The stage of pure description without interpretation (Peircean category).
- **Secondness**: The stage of anomaly detection, marking the brute fact of a **logical break**.
- **Thirdness**: The stage of abductive reasoning, forming hypotheses via symbolic causal laws.
- **Devil's Advocate (Gorgias Mode)**: A mandatory refutation stage executed by a deterministic logic engine to stress-test conclusions.
- **Abduction**: Inference to the best explanation, performed here by integer-symbolic engines.
- **Forensic Artifact**: Any digital object under investigation; referred to in Chinese as 取证工件.
- **Logical Break**: A deterministic flag indicating a contradiction or discontinuity in evidence; referred to in Chinese as 逻辑断裂.

---

## ESPAÑOL

### ¿Qué es este módulo?
`vigia/core/llm_backend.py` (motor: `llm_backend_v2.py`) es el **Backend Unificado de LLM con Degradación Elegante por Capacidades**. Funciona como una capa de despacho determinista para el análisis forense digital. En lugar de enviar cada tarea a un modelo neuronal monolítico, el módulo clasifica la tarea y el backend en niveles discretos y ordenados por enteros. Si un backend carece del rango requerido, el sistema no falla; desciende a un nivel determinista inferior. Esto garantiza que el procesamiento de pruebas sea reproducible y nunca dependa de conjeturas estocásticas de punto flotante.

### Conceptos Clave

| Concepto | Rango Entero / Tipo | Descripción |
|---|---|---|
| **FIRSTNESS_ONLY** | 1 | Descripción pura de artefactos forenses. Sin interpretación. |
| **ANOMALY_DETECTION** | 2 | Descripción más banderas deterministas de anomalías (rupturas lógicas). |
| **CAUSAL_REASONING** | 3 | Lo anterior más inferencia abdutiva vía motor simbólico. |
| **FULL_SEMIOTIC** | 4 | Cadena completa con cierre causal y semiótico. |
| **BackendCapability** | Enum entero | Escalera estrictamente creciente. Rango *N* permite tareas ≤ *N*. |
| **Degradación Elegante** | Comparación entera | Si un backend no tiene rango *R*, la tarea se reenruta mediante comprobaciones exactas de umbral entero. |
| **Fallback Determinista** | Aritmética entera | Rescate basado en reglas simbólicas que nunca usa muestreo probabilístico de punto flotante. |
| **Devil's Advocate (Gorgias)** | Refutación determinista | Etapa obligatoria de contradicción ejecutada por motor de lógica simbólica, nunca por LLM. |

### Vista General de la API Funcional

| Función | Capacidad Requerida | Rol | Mecanismo de Rescate |
|---|---|---|---|
| `analyze_firstness()` | ≥ 1 (cualquier backend) | Genera descripción cruda e interpretada de la evidencia. | No requiere rescate. |
| `analyze_secondness()` | ≥ 2 | Detecta anomalías y **rupturas lógicas** con herramientas deterministas; puede narrar hallazgos con LLM si está disponible. | Detector de anomalías por umbral entero determinista. |
| `analyze_thirdness()` | ≥ 3 | Realiza abducción: selecciona la mejor explicación causal. | Motor simbólico con unificación de reglas enteras si el backend carece de `CAUSAL_REASONING`. |
| `generate_devil_advocate()` | N/A (siempre Gorgias) | Produce refutación formal de la hipótesis actual. | **Nunca** un LLM; siempre ataque lógico determinista. |

### Aritmética Entera Determinista
Todas las comparaciones de capacidad usan ordenamiento exacto de enteros (1 < 2 < 3 < 4). No existen umbrales de confianza de punto flotante, ni puntajes de enrutamiento probabilísticos, ni funciones de activación continuas. Un backend posee un rango entero o no lo posee. Las decisiones de rescate se computan mediante transiciones discretas de estado en una máquina de estados finita, asegurando comportamiento reproducible bit a bit.

### 【Nota Científica】
La terminología de Peirce (Primeridad, Segundidad, Terceridad), Eco y Grice utilizada aquí no es misticismo ni adorno literario. Funciona exactamente como la cadena de procesamiento de un sensor científico: la **Primeridad** corresponde al voltaje crudo e interpretado (descripción); la **Segundidad** corresponde al incumplimiento de umbral o bandera de desviación (detección de anomalías); la **Terceridad** corresponde al modelo diagnóstico calibrado que explica por qué ocurrió la desviación (inferencia abdutiva). El "Abogado del Diablo" es un sensor redundante ejecutado bajo supuestos opuestos para verificar sesgos sistemáticos. Son etapas operativas discretas y deterministas—estados enteros en una máquina de estados finita—, no filosofía esotérica.

### Glosario
- **BackendCapability**: Enumeración de enteros que asigna a cada backend un rango estrictamente creciente. Un backend en rango *N* puede ejecutar todas las tareas de rango ≤ *N*.
- **Degradación Elegante**: Capacidad del sistema para descender a una capacidad entera inferior cuando la superior no está disponible, preservando la cadena de custodia.
- **Fallback Determinista**: Mecanismo de rescate no probabilístico que usa aritmética entera exacta y reglas simbólicas en lugar de generación neuronal.
- **Primeridad (Firstness)**: Etapa de descripción pura sin interpretación (categoría peirceana).
- **Segundidad (Secondness)**: Etapa de detección de anomalías, marcando el hecho bruto de una **ruptura lógica**.
- **Terceridad (Thirdness)**: Etapa de razonamiento abdutivo, formando hipótesis mediante leyes causales simbólicas.
- **Devil's Advocate (Modo Gorgias)**: Etapa obligatoria de refutación ejecutada por un motor de lógica determinista para someter a prueba las conclusiones.
- **Abducción**: Inferencia a la mejor explicación, realizada aquí por motores simbólico-enteros.
- **Artefacto Forense**: Cualquier objeto digital bajo investigación; en chino se denomina 取证工件.
- **Ruptura Lógica**: Bandera determinista que indica una contradicción o discontinuidad en la evidencia; en chino se denomina 逻辑断裂.

---

## РУССКИЙ

### Что представляет собой этот модуль?
`vigia/core/llm_backend.py` (движок: `llm_backend_v2.py`) — это **Унифицированный бэкенд LLM с graceful degradation на основе целочисленных уровней возможностей**. Он выступает в роли детерминированного диспетчерского слоя для цифровой криминалистики. Вместо того чтобы направлять каждую задачу в монолитную нейронную модуль, модуль классифицирует задачу и бэкенд по дискретным, упорядоченным целыми числами уровням. Если у бэкенда отсутствует требуемый ранг, система не падает, а переходит на более низкий детерминированный уровень обработки. Это гарантирует воспроизводимость обработки доказательств и исключает зависимость от стохастических догадок с плавающей точкой.

### Ключевые концепции

| Концепция | Целочисленный ранг / Тип | Описание |
|---|---|---|
| **FIRSTNESS_ONLY** | 1 | Чистое описание криминалистических артефактов. Без интерпретации. |
| **ANOMALY_DETECTION** | 2 | Описание плюс детерминированные флаги аномалий (логические разрывы). |
| **CAUSAL_REASONING** | 3 | Вышеперечисленное плюс абдуктивный вывод через символьный движок. |
| **FULL_SEMIOTIC** | 4 | Полная цепочка с причинно-следственным и семиотическим замыканием. |
| **BackendCapability** | Целочисленное перечисление | Строго возрастающая лестница. Ранг *N* разрешает задачи ≤ *N*. |
| **Плавная деградация** | Целочисленное сравнение | При отсутствии ранга *R* задача перенаправляется через точные пороговые проверки целых чисел. |
| **Детерминированный fallback** | Целочисленная арифметика | Правиловое спасение, никогда не использующее вероятностную выборку с плавающей точкой. |
| **Devil's Advocate (Горгий)** | Детерминированное опровержение | Обязательная стадия противоречия, выполняемая символьным логическим движком, а не LLM. |

### Обзор функционального API

| Функция | Требуемая возможность | Роль | Механизм возврата |
|---|---|---|---|
| `analyze_firstness()` | ≥ 1 (любой бэкенд) | Генерирует сырое, неинтерпретированное описание доказательства. | Возврат не требуется. |
| `analyze_secondness()` | ≥ 2 | Обнаруживает аномалии и **логические разрывы** с помощью детерминированных инструментов; при наличии может обернуть находки в LLM-наррацию. | Детерминированный детектор аномалий с целочисленным порогом. |
| `analyze_thirdness()` | ≥ 3 | Выполняет абдукцию: выбирает наилучшее причинное объяснение. | Символьный движок с целочисленным унифицированием правил, если бэкенд не поддерживает `CAUSAL_REASONING`. |
| `generate_devil_advocate()` | N/A (всегда Горгий) | Производит формальное опровержение текущей гипотезы. | **Никогда** LLM; всегда детерминированная логическая атака. |

### Детерминированная целочисленная арифметика
Все сравнения возможностей используют точное целочисленное упорядочивание (1 < 2 < 3 < 4). Отсутствуют пороги уверенности с плавающей точкой, вероятностные баллы маршрутизации и непрерывные функции активации. Бэкенд либо обладает целочисленным рангом, либо нет. Решения о возврате вычисляются дискретными переходами состояний в конечном автомате, обеспечивая побитово воспроизводимое поведение.

### 【Научное Примечание】
Терминология Пирса (Первичность, Вторичность, Третичность), Эко и Грайса, используемая здесь, не является мистицизмом или литературным украшением. Она функционирует точно так же, как конвейер обработки научного датчика: **Первичность** соответствует сырому, неинтерпретированному напряжению (описание); **Вторичность** — нарушению порога или флагу отклонения (обнаружение аномалий); **Третичность** — калиброванной диагностической модели, объясняющей, почему произошло отклонение (абдуктивный вывод). «Адвокат дьявола» — это резервный датчик, запущенный при противоположных допущениях для проверки систематического смещения. Это детерминированные дискретные операционные этапы — целочисленные состояния конечного автомата — а не эзотерическая философия.

### Глоссарий
- **BackendCapability**: Целочисленное перечисление, присваивающее каждому бэкенду строго возрастающий ранг. Бэкенд с рангом *N* может выполнять все задачи ранга ≤ *N*.
- **Плавная деградация (Graceful Degradation)**: Способность системы спускаться на более низкий целочисленный уровень, когда высший недоступен, сохраняя цепочку сохранности.
- **Детерминированный fallback**: Невероятностный спасательный механизм, использующий точную целочисленную арифметику и символьные правила вместо нейрогенерации.
- **Первичность (Firstness)**: Этап чистого описания без интерпретации (пирсовская категория).
- **Вторичность (Secondness)**: Этап обнаружения аномалий, фиксирующий факт **логического разрыва**.
- **Третичность (Thirdness)**: Этап абдуктивного рассуждения, формирующий гипотезы через символьные причинные законы.
- **Devil's Advocate (режим Горгия)**: Обязательная стадия опровержения, выполняемая детерминированным логическим движком для стресс-тестирования выводов.
- **Абдукция**: Вывод наилучшего объяснения, выполняемый здесь целочисленно-символьными движками.
- **Криминалистический артефакт**: Любой цифровой объект под следствием; на китайском обозначается как 取证工件.
- **Логический разрыв**: Детерминированный флаг, указывающий на противоречие или разрыв в доказательствах; на китайском обозначается как 逻辑断裂.

---

## 中文

### 这是什么模块？
`vigia/core/llm_backend.py`（引擎引用：`llm_backend_v2.py`）是**基于能力等级的统一大语言模型（LLM）后端优雅降级系统**。它是数字取证中的确定性调度层。该模块不会将所有任务都发送给单一的神经网络模型，而是将任务与后端按严格递增的整数能力等级进行分类。若某个后端不具备所需等级，系统不会崩溃，而是降级至较低的确定性处理层级。这保证了证据处理的可复现性，且绝不依赖浮点数的随机猜测。

### 核心概念

| 概念 | 整数等级 / 类型 | 说明 |
|---|---|---|
| **FIRSTNESS_ONLY** | 1 | 对取证工件的纯描述，无任何解释。 |
| **ANOMALY_DETECTION** | 2 | 描述加上确定性异常标志（逻辑断裂）。 |
| **CAUSAL_REASONING** | 3 | 在上述基础上，通过符号引擎进行溯因推理。 |
| **FULL_SEMIOTIC** | 4 | 包含因果与符号闭合的完整处理链。 |
| **BackendCapability** | 整数枚举 | 严格递增的阶梯。等级为 *N* 的后端可执行所有等级 ≤ *N* 的任务。 |
| **优雅降级** | 整数比较 | 若后端缺少等级 *R*，系统通过精确的整数阈值检查重新路由任务。 |
| **确定性回退** | 整数运算 | 基于符号规则的救援机制，绝不使用浮点概率采样。 |
| **魔鬼辩护人（高尔吉亚模式）** | 确定性反驳 | 由符号逻辑引擎强制执行的矛盾检验阶段，**绝不**使用LLM。 |

### 功能接口概览

| 函数 | 所需能力等级 | 作用 | 回退机制 |
|---|---|---|---|
| `analyze_firstness()` | ≥ 1（任意后端） | 生成对证据的原始、未解释描述。 | 无需回退。 |
| `analyze_secondness()` | ≥ 2 | 使用确定性工具检测异常与**逻辑断裂**；若可用，可用LLM对发现进行叙述包装。 | 确定性整数阈值异常检测器。 |
| `analyze_thirdness()` | ≥ 3 | 执行溯因：选择最佳因果解释。 | 若后端缺少`CAUSAL_REASONING`，则调用基于整数规则合一的符号引擎。 |
| `generate_devil_advocate()` | 不适用（始终为高尔吉亚） | 对当前假设产生形式化反驳。 | **绝不**使用LLM；始终为确定性逻辑攻击。 |

### 确定性整数运算
所有能力比较均采用精确的整数序关系（1 < 2 < 3 < 4）。不存在浮点置信度阈值、不存在概率路由分数、也不存在连续激活函数。后端要么具备某个整数等级，要么不具备。回退决策由有限状态机中的离散状态转移计算得出，确保跨执行的按位可复现行为。

### 【科学说明】
本模块所使用的皮尔斯（第一性、第二性、第三性）、艾柯与格赖斯术语并非神秘主义或文学修饰。其功能原理与科学传感器的处理流水线完全一致：**第一性**对应原始、未解释的电压信号（描述）；**第二性**对应阈值越界或偏差标志（异常检测）；**第三性**对应经过标定的诊断模型，用于解释偏差为何发生（溯因推理）。"魔鬼辩护人"则是在相反假设下运行的冗余传感器，用于检验系统性偏差。这些是确定性的、离散的操作阶段——即有限状态机中的整数状态——而非玄学。

### 术语表
- **BackendCapability（后端能力）**：为每个后端分配严格递增等级的整数枚举。等级为 *N* 的后端可执行所有等级 ≤ *N* 的任务。
- **Graceful Degradation（优雅降级）**：当较高能力不可用时，系统降级至较低整数能力的能力，以保全证据链。
- **Deterministic Fallback（确定性回退）**：一种非概率的救援机制，使用精确的整数运算与符号规则，而非神经生成。
- **第一性（Firstness）**：纯描述而无解释的阶段（皮尔斯范畴）。
- **第二性（Secondness）**：异常检测阶段，标记**逻辑断裂**的客观事实。
- **第三性（Thirdness）**：溯因推理阶段，通过符号因果律形成假说。
- **魔鬼辩护人（高尔吉亚模式）**：由确定性逻辑引擎执行的强制反驳阶段，用于对结论进行压力测试。
- **溯因（Abduction）**：推断最佳解释，此处由整数-符号引擎执行。
- **取证工件（Forensic Artifact）**：任何受调查的数字对象。
- **逻辑断裂（Logical Break）**：指示证据中存在矛盾或不连续性的确定性标志。

---

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
