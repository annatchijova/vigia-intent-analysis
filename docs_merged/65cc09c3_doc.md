<!--
VIGIA Academic Documentation
Module: 65cc09c3
Batch ID: vigia-doc-0078-65cc09c3
Generated: 2026-05-20T14:56:47.861298+00:00
-->

ENGLISH:
- Title: Module Documentation: `vigia/core/signal_quality_gate.py`
- What Is This Module?: It's a quality control layer for a digital forensics system called VIGÍA. Before the system declares something "guilty" (ACCEPT), this gate checks if the evidence signals are strong enough. It applies semiotics and culinary metaphors but operates deterministically.
- Key Concepts Table: Maybe two tables? One for constants/config, one for classes/functions, one for checks. Let's combine into a clear table.
  - Signal Quality Gate: A filter that blocks weak evidence from triggering final verdicts.
  - Firstness / Thirdness (Peirce): Raw sensation vs. interpreted habit/law. Weak signals are Firstness; verdict is Thirdness.
  - z-score: A standardized measure of signal strength. Here, threshold Z_STRONG = 2.0 means "at least two standard deviations above baseline".
  - Noise Inflation: False confidence from many weak signals.
  - Independence: Signals must come from diverse forensic tools.
- Table for Constants:
  | Constant | Role | Deterministic Rule |
  | MIN_TOOLS_REQUIRED | Minimum number of distinct forensic tools | Integer count ≥ 2 |
  | MIN_STRONG_SIGNALS | Minimum high-confidence findings | Integer count ≥ 1 |
  | Z_STRONG | Threshold for a "strong" signal | Exact boundary; no approximation |
  | MIN_Z_VARIANCE | Required spread between scores | Prevents cloned/duplicated inputs |
  | MAX_SAME_TOOL_RATIO | Ceiling for single-tool dominance | Integer ratio limit |
- Table for Checks:
  | Check | Description | Scientific Rationale |
  | 1. Tool Diversity | ≥ 2 distinct tools | Avoids single-point methodology failure |
  | 2. Strong Signal Presence | ≥ 1 signal with z ≥ 2.0 | One excellent ingredient outweighs many mediocre ones |
  | 3. Independence | Not all from same tool | Correlation does not imply independent verification |
  | 4. Score Variability | z-scores not identical | Detects copy-paste or systematic duplication |
  | 5. Noise Inflation | Few strong vs. many weak | Prevents "wisdom of crowds" fallacy on noisy data |
- Glossary:
  - ACCEPT verdict: Final decision that a target is culpable/guilty.
  - Digital Forensics: Scientific recovery and investigation of material found in digital devices.
  - Deterministic Integer Arithmetic: Calculations using whole numbers with no rounding ambiguity; the gate logic uses exact counts and thresholds.
  - Firstness (Peirce): Category of raw feeling or immediate quality; unanalyzed signal.
  - Thirdness (Peirce): Category of law, habit, or mediated conclusion; the final verdict.
  - Noise Inflation: Artificial increase in confidence caused by aggregating many low-quality measurements.
  - z-score: Standardized score indicating how many standard deviations a signal is from the mean; used here as a deterministic strength classifier.
  - QualityGateResult: Output container holding PASS/FAIL status and explanatory notes.
  - SignalQualityGate: The controller class that executes all five checks.
- Scientific Note:
  【Scientific Note】
  The module uses terminology borrowed from Charles Sanders Peirce (Firstness, Thirdness), Umberto Eco, and H. P. Grice. This is NOT mysticism. In sensor engineering, a single raw voltage reading (Firstness) does not constitute a validated detection event (Thirdness). A sensor array must contain at least one transducer with a signal-to-noise ratio above a calibrated threshold before the system asserts a positive alarm. The semiotic labels are merely epistemological shorthand for verification stages that every instrumentation physicist already uses: raw acquisition → noise filtering → validated measurement.
- License line.

ESPAÑOL:
- Similar structure. Translate carefully.
- "What Is This Module?" -> "¿Qué es este módulo?"
- Key concepts: Same tables, Spanish.
- Glossary: 
  - Veredicto ACCEPT: Decisión final de culpabilidad.
  - Arqueología digital / Informática forense: Investigación científica de dispositivos digitales.
  - Aritmética entera determinista: Cálculos con números enteros sin ambigüedad de redondeo.
  - Firstness (Peirce): Categoría de sentimiento crudo; señal inmediata no analizada.
  - Thirdness (Peirce): Categoría de ley, hábito o conclusión mediada; veredicto final.
  - Inflación por ruido: Aumento artificial de confianza por agregación de medidas débiles.
  - z-score: Puntuación estandarizada; aquí clasificador determinista de fuerza.
  - QualityGateResult: Contenedor de salida con estado APROBADO/RECHAZADO.
  - SignalQualityGate: Clase controladora que ejecuta las cinco pruebas.
- Scientific Note: 
  【Nota Científica】
  El módulo usa términos de Charles Sanders Peirce (Firstness, Thirdness), Umberto Eco y H. P. Grice. NO es misticismo. En ingeniería de sensores, una sola lectura de voltaje crudo (Firstness) no constituye un evento de detección validado (Thirdness). Una matriz de sensores debe contener al menos un transductor con relación señal/ruido por encima de un umbral calibrado antes de que el sistema aserte una alarma positiva. Las etiquetas semióticas son solo abreviaturas epistemológicas de etapas de verificación que todo físico de instrumentación ya utiliza: adquisición cruda → filtrado de ruido → medición validada.
- License.

РУССКИЙ:
- "What Is This Module?" -> "Что это за модуль?"
- Key concepts tables.
- Glossary:
  - Вердикт ACCEPT: Окончательное решение о виновности.
  - Цифровая криминалистика: Научное восстановление и исследование данных с цифровых устройств.
  - Детерминированная целочисленная арифметика: Вычисления с целыми числами без неоднозначности округления.
  - Firstness (Пирс): Категория непосредственного качества, «сырой» сигнал.
  - Thirdness (Пирс): Категория закона, привычки, посредничества; итоговый вердикт.
  - Инфляция шума: Искусственное повышение уверенности при агрегировании множества слабых измерений.
  - z-score: Стандартизированная оценка; здесь используется как детерминированный классификатор силы сигнала.
  - QualityGateResult: Контейнер результата со статусом ПРОЙДЕН/НЕ ПРОЙДЕН.
  - SignalQualityGate: Контролирующий класс, выполняющий все пять проверок.
- Scientific Note:
  【Научное Примечание】
  Модуль использует терминологию Чарльза Сандерса Пирса (Firstness, Thirdness), Умберто Эко и Г. П. Грайса. Это НЕ мистицизм. В сенсорной инженерии одиночное сырое показание напряжения (Firstness) не составляет подтверждённого события обнаружения (Thirdness). Сенсорная матрица должна содержать хотя бы один преобразователь с отношением сигнал/шум выше калиброванного порога, прежде чем система выдаст положительную тревогу. Семиотические метки — лишь эпистемологические сокращения для стадий верификации, которые и без того использует каждый инженер-физик: сырой сбор → фильтрация шума → валидированное измерение.
- License.

中文:
- What Is This Module? -> "本模块是什么？"
- Key concepts tables.
- Glossary:
  - ACCEPT 裁决: 最终认定目标有罪的判定。
  - 数字取证: 对数字设备中物质进行科学恢复与调查。
  - 确定性整数运算: 使用整数进行无舍入歧义的计算。
  - 初性 (Firstness, 皮尔斯): 原始感知或直接性质的范畴；未经分析的信号。
  - 三性 (Thirdness, 皮尔斯): 法则、习惯或中介推断的范畴；最终裁决。
  - 噪声膨胀: 通过聚合大量低质量测量而人为提升置信度。
  - z-score: 标准化分数；此处用作信号强度的确定性分类器。
  - QualityGateResult: 保存通过/未通过状态及说明性备注的输出容器。
  - SignalQualityGate: 执行全部五项检查的控制器类。
- Scientific Note:
  【科学说明】
  本模块使用查尔斯·桑德斯·皮尔斯（初性/三性）、艾柯与格赖斯的术语。这并非神秘主义。在传感器工程中，单一原始电压读数（初性）并不构成经过验证的探测事件（三性）。传感器阵列必须至少包含一个信噪比高于校准阈值的换能器，系统才能断言正向告警。这些符号学术语只是认识论层面的简写，代表每位仪器物理学家都在使用的验证阶段：原始采集 → 噪声过滤 → 经确认的测量。
- License.


For 取证工件: I can say the module evaluates digital 取证工件 (forensic artifacts). Or in the "What is this module" section: it inspects 取证工件 before verdict.

Okay.

Now, formatting: Markdown. Use headers.


Let's write it.

Plan:

# Module Documentation: `vigia/core/signal_quality_gate.py`

---

## ENGLISH

### What Is This Module?

...

### Key Concepts

Table 1: Configuration Constants (Deterministic Rules)
| Constant | Scientific Role | Rule (Integer Arithmetic) |
|---|---|---|
| `MIN_TOOLS_REQUIRED` | Minimum forensic methodologies | Exact count ≥ 2 |
| `MIN_STRONG_SIGNALS` | High-confidence findings required | Exact count ≥ 1 |
| `Z_STRONG` | Strength threshold | Exact integer boundary; signals must meet or exceed this deterministic classifier |
| `MIN_Z_VARIANCE` | Cloning/duplication detector | Exact non-zero spread required |
| `MAX_SAME_TOOL_RATIO` | Single-source dominance limit | Exact maximum ratio enforced via integer counts |

Table 2: The Five Quality Checks
| Check | Purpose | Failure Mode Prevented |
|---|---|---|
| 1. Tool Diversity | Verify ≥ 2 distinct tools | Methodological monoculture |
| 2. Strong Signal Presence | Require ≥ 1 signal with z ≥ 2.0 | "Bad soup" fallacy (many weak ingredients) |
| 3. Independence | Reject single-tool unanimity | Correlated noise mistaken for consensus |
| 4. Score Variability | Ensure z-scores differ | Duplicated or cloned forensic artifacts |
| 5. Noise Inflation | Flag many weak vs. few strong | Confidence inflation from low-quality data |

Table 3: Core Components
| Component | Type | Function |
|---|---|---|
| `QualityGateResult` | Data structure | Stores PASS/FAIL status and human-readable rationale |
| `SignalQualityGate` | Controller | Orchestrates the five checks |
| `evaluate()` | Method | Executes the full quality protocol |
| `detect_noise_inflation()` | Method | Identifies and corrects false confidence from noisy signals |

### Glossary

- **ACCEPT verdict**: The final determination that a target is culpable.
- **Deterministic Integer Arithmetic**: Computation using whole-number counts and exact thresholds, eliminating rounding ambiguity.
- **Digital Forensics**: The scientific recovery and investigation of material found in digital devices.
- **Firstness (Peirce)**: The category of raw, unanalyzed feeling or immediate quality; a weak signal before interpretation.
- **Noise Inflation**: An artificial increase in confidence caused by aggregating numerous low-quality measurements.
- **QualityGateResult**: The output container holding gate status and explanatory annotations.
- **SignalQualityGate**: The evaluator class that tests evidence before a verdict is issued.
- **Thirdness (Peirce)**: The category of law, habit, or mediated conclusion; the final interpretive verdict.
- **z-score**: A standardized strength classifier indicating how many standard deviations a signal lies from baseline; used here with an exact integer threshold.

### 【Scientific Note】

The module uses terminology borrowed from Charles Sanders Peirce (Firstness, Thirdness), Umberto Eco, and H. P. Grice. This is **NOT mysticism**. In sensor engineering, a single raw voltage reading (Firstness) does not constitute a validated detection event (Thirdness). A sensor array must contain at least one transducer with a signal-to-noise ratio above a calibrated threshold before the system asserts a positive alarm. The semiotic labels are merely epistemological shorthand for verification stages that every instrumentation physicist already uses: raw acquisition → noise filtering → validated measurement.

---

## ESPAÑOL

### ¿Qué es este módulo?

...

### Conceptos Clave

Table 1: Constantes de Configuración (Reglas Deterministas)
| Constante | Rol Científico | Regla (Aritmética Entera) |
|---|---|---|
| `MIN_TOOLS_REQUIRED` | Metodologías forenses mínimas | Conteo exacto ≥ 2 |
| `MIN_STRONG_SIGNALS` | Hallazgos de alta confianza requeridos | Conteo exacto ≥ 1 |
| `Z_STRONG` | Umbral de fuerza | Frontera entera exacta; clasificador determinista |
| `MIN_Z_VARIANCE` | Detector de clonación/duplicación | Dispersión exacta distinta de cero |
| `MAX_SAME_TOOL_RATIO` | Límite de dominancia de una sola fuente | Razón máxima exacta mediante conteos enteros |

Table 2: Las Cinco Pruebas de Calidad
| Prueba | Propósito | Fallo Prevenido |
|---|---|---|
| 1. Diversidad de Herramientas | Verificar ≥ 2 herramientas distintas | Monocultivo metodológico |
| 2. Presencia de Señal Fuerte | Exigir ≥ 1 señal con z ≥ 2,0 | Falacia de la "sopa mala" (muchos ingredientes débiles) |
| 3. Independencia | Rechazar unanimidad de una sola herramienta | Ruido correlacionado confundido con consenso |
| 4. Variabilidad de Puntuaciones | Garantizar que los z-scores difieran | Artefactos forenses duplicados o clonados |
| 5. Inflación por Ruido | Marcar muchas débiles vs. pocas fuertes | Inflación de confianza por datos de baja calidad |

Table 3: Componentes Principales
| Componente | Tipo | Función |
|---|---|---|
| `QualityGateResult` | Estructura de datos | Almacena estado APROBADO/RECHAZADO y justificación legible |
| `SignalQualityGate` | Controlador | Orquesta las cinco pruebas |
| `evaluate()` | Método | Ejecuta el protocolo completo de calidad |
| `detect_noise_inflation()` | Método | Identifica y corrige falsa confianza por señales ruidosas |

### Glosario

- **Veredicto ACCEPT**: Determinación final de que un objetivo es culpable.
- **Aritmética Entera Determinista**: Cálculo mediante conteos de números enteros y umbrales exactos, eliminando la ambigüedad del redondeo.
- **Informática Forense / Arqueología Digital**: Recuperación e investigación científica de material hallado en dispositivos digitales.
- **Firstness (Peirce)**: Categoría de sentimiento crudo o calidad inmediata; una señal débil antes de la interpretación.
- **Inflación por Ruido**: Aumento artificial de la confianza causado por agregar numerosas mediciones de baja calidad.
- **QualityGateResult**: Contenedor de salida que guarda el estado de la puerta y anotaciones explicativas.
- **SignalQualityGate**: Clase evaluadora que prueba la evidencia antes de emitir un veredicto.
- **Thirdness (Peirce)**: Categoría de ley, hábito o conclusión mediada; el veredicto interpretativo final.
- **z-score**: Clasificador estandarizado de fuerza que indica cuántas desviaciones estándar se sitúa una señal respecto a la línea base; aquí se emplea con un umbral entero exacto.

### 【Nota Científica】

El módulo usa términos de Charles Sanders Peirce (Firstness, Thirdness), Umberto Eco y H. P. Grice. **NO es misticismo**. En ingeniería de sensores, una sola lectura de voltaje crudo (Firstness) no constituye un evento de detección validado (Thirdness). Una matriz de sensores debe contener al menos un transductor con relación señal/ruido por encima de un umbral calibrado antes de que el sistema asiente una alarma positiva. Las etiquetas semióticas son solo abreviaturas epistemológicas de etapas de verificación que todo físico de instrumentación ya utiliza: adquisición cruda → filtrado de ruido → medición validada.

---

## РУССКИЙ

### Что это за модуль?

...

### Ключевые Концепции

Table 1: Конфигурационные Константы (Детерминированные Правила)
| Константа | Научная Роль | Правило (Целочисленная Арифметика) |
|---|---|---|
| `MIN_TOOLS_REQUIRED` | Минимум методологий экспертизы | Точное число ≥ 2 |
| `MIN_STRONG_SIGNALS` | Требуемые высокодостоверные находки | Точное число ≥ 1 |
| `Z_STRONG` | Порог силы сигнала | Точная целочисленная граница; детерминированный классификатор |
| `MIN_Z_VARIANCE` | Детектор клонирования/дублирования | Требуется точная ненулевая вариативность |
| `MAX_SAME_TOOL_RATIO` | Потолок доминирования одного источника | Точное максимальное соотношение через целочисленные счётчики |

Table 2: Пять Проверок Качества
| Проверка | Назначение | Предотвращаемый Сбой |
|---|---|---|
| 1. Разнообразие Инструментов | Проверить ≥ 2 различных инструмента | Методологическая монокультура |
| 2. Наличие Сильного Сигнала | Требовать ≥ 1 сигнал с z ≥ 2,0 | Парадокс «плохого супа» (много слабых ингредиентов) |
| 3. Независимость | Отвергать единогласие одного инструмента | Коррелированный шум, принятый за консенсус |
| 4. Вариативность Оценок | Обеспечить различие z-scores | Дублированные или клонированные артефакты |
| 5. Инфляция Шума | Маркировать много слабых vs. мало сильных | Накопление уверенности на основе низкокачественных данных |

Table 3: Основные Компоненты
| Компонент | Тип | Функция |
|---|---|---|
| `QualityGateResult` | Структура данных | Хранит статус ПРОЙДЕН/НЕ ПРОЙДЕН и пояснения |
| `SignalQualityGate` | Контроллер | Оркестрирует пять проверок |
| `evaluate()` | Метод | Выполняет полный протокол контроля качества |
| `detect_noise_inflation()` | Метод | Выявляет и корректирует ложную уверенность от зашумлённых сигналов |

### Глоссарий

- **Вердикт ACCEPT**: Окончательное решение о виновности объекта.
- **Детерминированная Целочисленная Арифметика**: Вычисления с использованием целых счётчиков и точных порогов, исключающие неоднозначность округления.
- **Цифровая Криминалистика**: Научное восстановление и исследование материалов, обнаруженных на цифровых устройствах.
- **Firstness (Пирс)**: Категория непосредственного, неанализированного качества; «сырой» сигнал до интерпретации.
- **Инфляция Шума**: Искусственное повышение уверенности, вызванное агрегированием множества низкокачественных измерений.
- **QualityGateResult**: Контейнер результата, содержащий статус ворот и пояснительные аннотации.
- **SignalQualityGate**: Оценочный класс, проверяющий доказательства перед вынесением вердикта.
- **Thirdness (Пирс)**: Категория закона, привычки или опосредованного вывода; итоговый интерпретативный вердикт.
- **z-score**: Стандартизированный классификатор силы сигнала, показывающий отклонение от базового уровня в единицах стандартного отклонения; здесь применяется с точным целочисленным порогом.

### 【Научное Примечание】

Модуль использует терминологию Чарльза Сандерса Пирса (Firstness, Thirdness), Умберто Эко и Г. П. Грайса. Это **НЕ мистицизм**. В сенсорной инженерии одиночное сырое показание напряжения (Firstness) не составляет подтверждённого события обнаружения (Thirdness). Сенсорная матрица должна содержать хотя бы один преобразователь с отношением сигнал/шум выше калиброванного порога, прежде чем система выдаст положительную тревогу. Семиотические метки — лишь эпистемологические сокращения для стадий верификации, которые и без того использует каждый инженер-физик: сырой сбор данных → фильтрация шума → валидированное измерение.

---

## 中文

### 本模块是什么？

...

### 核心概念

Table 1: 配置常数（确定性规则）
| 常数 | 科学作用 | 规则（整数运算） |
|---|---|---|
| `MIN_TOOLS_REQUIRED` | 取证工具方法的最小数量 | 精确计数 ≥ 2 |
| `MIN_STRONG_SIGNALS` | 所需的高置信度发现 | 精确计数 ≥ 1 |
| `Z_STRONG` | 信号强度阈值 | 精确整数边界；确定性分类器 |
| `MIN_Z_VARIANCE` | 克隆/复制检测器 | 要求精确的非零离散度 |
| `MAX_SAME_TOOL_RATIO` | 单一来源 dominance 上限 | 通过整数计数强制执行精确最大比例 |

Table 2: 五项质量检查
| 检查 | 目的 | 防止的失效模式 |
|---|---|---|
| 1. 工具多样性 | 验证 ≥ 2 种不同工具 | 方法论单一化 |
| 2. 强信号存在 | 要求 ≥ 1 个 z ≥ 2.0 的信号 | “劣汤”谬误（许多弱成分） |
| 3. 独立性 | 拒绝单一工具的一致性 | 将相关噪声误认为共识 |
| 4. 分数变异性 | 确保 z 分数互不相同 | 取证工件被复制或克隆 |
| 5. 噪声膨胀 | 标记多弱少强 | 低质量数据导致的置信度膨胀 |

Table 3: 核心组件
| 组件 | 类型 | 功能 |
|---|---|---|
| `QualityGateResult` | 数据结构 | 保存通过/未通过状态及人类可读的理由 |
| `SignalQualityGate` | 控制器 | 编排五项检查 |
| `evaluate()` | 方法 | 执行完整质量协议 |
| `detect_noise_inflation()` | 方法 | 识别并修正噪声信号产生的虚假置信度 |

### 术语表

- **ACCEPT 裁决**：最终认定目标有罪的判定。
- **确定性整数运算**：使用整数计数和精确阈值进行计算，消除舍入歧义。
- **数字取证**：对数字设备中发现的内容进行科学恢复与调查。
- **初性（Firstness，皮尔斯）**：未经分析的原始感知或直接性质的范畴；解释之前的弱信号。
- **噪声膨胀**：通过聚合大量低质量测量而人为提升置信度的现象。
- **QualityGateResult**：保存门控状态及说明性注释的输出容器。
- **SignalQualityGate**：在发出裁决前对证据进行测试的评估器类。
- **三性（Thirdness，皮尔斯）**：法则、习惯或中介推断的范畴；最终的解释性裁决。
- **z-score**：标准化强度分类器，表示信号偏离基线多少个标准差；此处以精确整数阈值使用。

### 【科学说明】

本模块使用查尔斯·桑德斯·皮尔斯（初性/三性）、艾柯与格赖斯的术语。这**并非神秘主义**。在传感器工程中，单一原始电压读数（初性）并不构成经过验证的探测事件（三性）。传感器阵列必须至少包含一个信噪比高于校准阈值的换能器，系统才能断言正向告警。这些符号学术语只是认识论层面的简写，代表每位仪器物理学家都在使用的验证阶段：原始采集 → 噪声过滤 → 经确认的测量。若所有信号源自同一工具，则形成**逻辑断裂**，无法建立有效的证据链；而重复的取证工件亦无法增强证明力。

---


Let's refine the ENGLISH table for Z_STRONG to say "Exact integer threshold; deterministic classifier" rather than "Exact integer boundary". Since z-scores can be 2.0, it's a threshold. I'll say "Exact deterministic threshold; signals must meet or exceed the integer boundary of 2". That emphasizes integer arithmetic.

Similarly for other languages.

Now, the scientific note: Need to mention Peirce/Eco/Grice. I have Peirce in all, Eco/Grice in EN, but need Eco and Grice explicitly in all languages.

EN: "Charles Sanders Peirce (Firstness, Thirdness), Umberto Eco, and H. P. Grice." Good.
ES: "Charles Sanders Peirce (Firstness, Thirdness), Umberto Eco y H. P. Grice." Good.
RU: "Чарльза Сандерса Пирса (Firstness, Thirdness), Умберто Эко и Г. П. Грайса." Good.
ZH: "查尔斯·桑德斯·皮尔斯（初性/三性）、艾柯与格赖斯". Good.

Sensor analogy: raw voltage reading (Firstness) → validated detection (Thirdness). Good.

---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
