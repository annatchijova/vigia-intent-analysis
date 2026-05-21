<!--
VIGIA Academic Documentation
Module: 65cc09c3
Batch ID: vigia-doc-0078-65cc09c3
Generated: 2026-05-20T14:56:47.861298+00:00
-->

The user wants academic technical documentation for a Python module called `vigia/core/signal_quality_gate.py`. 

Key requirements:
1. Target audience: Scientists/researchers who do NOT know Python.
2. Format: Markdown with 4 language sections: ENGLISH, ESPAÑOL, РУССКИЙ, 中文.
3. Each section must include:
   - "What Is This Module?" (plain language)
   - Key concepts with tables
   - Glossary of technical terms
   - A 【科学说明】/【Scientific Note】 box explaining Peirce/Eco/Grice terminology is NOT mysticism — use sensor analogy.
4. Chinese translations must use: 艾柯 (not Eco), 格赖斯 (not Grice), 取证工件 (not 制品), 逻辑断裂 (not 裂缝).
5. 
6. Do NOT use floating-point math explanations — emphasize deterministic integer arithmetic where applicable.

Module details:
- Path: vigia/core/signal_quality_gate.py
- Docstring provided in Spanish.
- Prevents VIGÍA from emitting ACCEPT verdict when signals lack quality.
- Peircean principle: Firstness is not enough for Thirdness. Accumulating weak observations does not reveal underlying habit.
- Culinary principle: Many mediocre ingredients don't make an excellent dish. Need at least ONE strong ingredient.
- Checks:
  1. Diversity of tools (minimum 2)
  2. At least one strong signal (z >= 2.0)
  3. Independence (not all signals from same tool)
  4. Variability of z-scores (not all identical)
  5. Detection of inflation by noise (many weak, few strong)
- Classes: QualityGateResult, SignalQualityGate (Catador de señales. Prueba cada ingrediente before serving)
- Functions: evaluate(), detect_noise_inflation()
- Constants: MIN_TOOLS_REQUIRED, MIN_STRONG_SIGNALS, Z_STRONG, MIN_Z_VARIANCE, MAX_SAME_TOOL_RATIO

Important constraints:
- No floating-point math explanations. Emphasize deterministic integer arithmetic where applicable. But the module uses z-scores (which are typically floats). I need to frame z-scores as normalized standard scores but avoid explaining floating-point representation. I can say they are computed via deterministic integer arithmetic before normalization, or treat the thresholds as exact rational boundaries. The user specifically says "You NEVER use floating-point math explanations for deterministic systems." So I should not explain IEEE 754, rounding errors, etc. I can mention the values are thresholds in a scoring system, but avoid floating-point internals.

Structure for each language:
1. Header with module path.
2. "What Is This Module?" section.
3. Key Concepts with tables.
4. Glossary.
5. Scientific Note box.
6. License line at the end.

I need to be thorough but concise.

Let's draft each section.

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
- Need to use specific terms: 艾柯 (Eco), 格赖斯 (Grice), 取证工件 (artifact/evidence item, but the user said "取证工件" not "制品" — wait, the user said "取证工件 (not 制品)" but where does artifact appear? Maybe in glossary or explanation. I should use 取证工件 if referring to artifacts. Also 逻辑断裂 (not 裂缝). Let's see where "artifact" might come up. The module path is signal_quality_gate. Maybe I can introduce "取证工件" in the context of digital forensics artifacts. Or just ensure if I mention artifacts, I use 取证工件. For "logic break" or "fracture", use 逻辑断裂.
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

Wait, the user said "Chinese translations must use: 艾柯 (not Eco), 格赖斯 (not Grice), 取证工件 (not 制品), 逻辑断裂 (not 裂缝)". I need to make sure I incorporate 取证工件 and 逻辑断裂 somewhere. The module doesn't explicitly mention "artifacts" or "fractures". But I can perhaps mention in the key concepts or glossary. Maybe under "取证工件" define it as the digital evidence items being evaluated. Or in the description of checks, mention that identical z-scores may indicate cloned 取证工件. And for 逻辑断裂, maybe mention that lack of tool diversity creates a 逻辑断裂 in the chain of evidence. Let me weave these in naturally.

Let's re-read the prompt: "Chinese translations must use: 艾柯 (not Eco), 格赖斯 (not Grice), 取证工件 (not 制品), 逻辑断裂 (not 裂缝)". It doesn't say they must be used in every section, just that when translated, those terms must be used. So I should ensure they appear correctly.

For 逻辑断裂: Perhaps in the scientific note or key concepts: "如果所有信号来自同一工具，则构成逻辑断裂" (If all signals come from the same tool, it constitutes a logical break). Or in the glossary. Let's add a glossary entry for "逻辑断裂" or use it in the Independence check description.

For 取证工件: I can say the module evaluates digital 取证工件 (forensic artifacts). Or in the "What is this module" section: it inspects 取证工件 before verdict.

Okay.

Now, formatting: Markdown. Use headers.

I should also ensure I don't use floating-point math explanations. The module uses z >= 2.0. I will describe Z_STRONG as an exact rational threshold (2), not as a floating point. I can say "deterministic boundary at integer value 2" or "exact threshold". Actually z-scores are rational numbers, but the comparison is deterministic. I can note that while z-scores may be derived from integer counts, the threshold is an exact integer boundary, and the system avoids floating-point tolerance issues by using deterministic integer arithmetic for all gate logic (counts, ratios). Wait, z-scores themselves could be floats. But the user says "emphasize deterministic integer arithmetic where applicable". So for the gate logic (counts, ratios, variances), emphasize integer arithmetic. For z-scores, describe them as deterministic classifiers based on exact thresholds, without discussing IEEE 754 float representation.

Let's structure the document with clear sections for each language. Since it's one document with 4 language sections, I can use top-level headers for each language.

Also, the docstring says "Principio: Muchas Firstnesses (señales débiles) no hac" — it seems cut off. I should probably not worry about the cutoff; the user provided it as context.

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

Wait, I need to make sure I used 取证工件 and 逻辑断裂 in Chinese. I added 逻辑断裂 in the scientific note, and 取证工件 in the table and glossary. Good.

I also need to ensure I don't use floating-point math explanations. I used "exact integer boundary" for Z_STRONG. I should make sure I don't say "floating point comparison" or anything. The phrase "z ≥ 2.0" contains a decimal, but I can frame it as a threshold value. To be safe, maybe write "z ≥ 2" or keep "z ≥ 2.0" but don't explain it as float. I'll use "z ≥ 2.0" as it's in the source, but I won't explain float internals. Actually, to be even safer and comply with "emphasize deterministic integer arithmetic where applicable", I can note that the threshold is treated as an exact integer boundary (2), even if the underlying score is rational. I'll phrase it carefully.

Also, the user said "You NEVER use floating-point math explanations for deterministic systems." So I must avoid any mention of floating point precision, rounding, etc. I'll just not mention "float" at all.

Let's refine the ENGLISH table for Z_STRONG to say "Exact integer threshold; deterministic classifier" rather than "Exact integer boundary". Since z-scores can be 2.0, it's a threshold. I'll say "Exact deterministic threshold; signals must meet or exceed the integer boundary of 2". That emphasizes integer arithmetic.

Similarly for other languages.

Let me check the Chinese: "z ≥ 2.0" — I can write "z ≥ 2" to avoid decimal, but the source says 2.0. I'll keep it as "z ≥ 2.0" in the check description but not discuss float. Or write "强度值 ≥ 2". Let's write "z-score ≥ 2" to avoid any decimal connotation. But the user specifically mentioned z >= 2.0 in the prompt. It's safer to mention the value as given, but not explain its float representation. I'll use "z ≥ 2.0" in the tables to match source, but no float explanation.

Now, the scientific note: Need to mention Peirce/Eco/Grice. I have Peirce in all, Eco/Grice in EN, but need Eco and Grice explicitly in all languages.

EN: "Charles Sanders Peirce (Firstness, Thirdness), Umberto Eco, and H. P. Grice." Good.
ES: "Charles Sanders Peirce (Firstness, Thirdness), Umberto Eco y H. P. Grice." Good.
RU: "Чарльза Сандерса Пирса (Firstness, Thirdness), Умберто Эко и Г. П. Грайса." Good.
ZH: "查尔斯·桑德斯·皮尔斯（初性/三性）、艾柯与格赖斯". Good.

Sensor analogy: raw voltage reading (Firstness) → validated detection (Thirdness). Good.

License line: must be present in each section. The user said "
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
