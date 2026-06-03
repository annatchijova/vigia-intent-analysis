<!--
VIGIA Academic Documentation
Module: e7859153
Batch ID: vigia-doc-0028-e7859153
Generated: 2026-05-20T14:56:47.850642+00:00
-->

### ENGLISH
**What Is This Module?**
This module is the "family tree" of hypotheses during VIGÍA's abductive cycle. In digital forensics, an analyst must see not only the final verdict but also the landscape of alternatives: what evidence, if found or missing, would pivot the conclusion elsewhere. This module records every considered hypothesis, tracks the signals that could change the outcome, and produces an immutable lineage report suitable for Daubert-standard traceability. It ensures reproducibility by using exact fractional costs and deterministic hashing over the entire trace.

**Key Concepts**
Table 1: Core Classes
| Class | Role | Forensic Analogy |
|-------|------|------------------|
| HypothesisNode | Frozen container for a single investigative hypothesis | A sealed evidence bag with an unalterable label |
| PivotSignal | A signal whose presence/absence would flip the verdict | A latent fingerprint that would reclassify a burglary as insider access |
| LineageReport | Final output of the abductive cycle | The expert witness workbook submitted under Daubert |
| HypothesisLineageTracker | Registry of the full abductive cycle | The chain-of-custody log for reasoning |

Table 2: Cost & Integrity Model
| Property | Data Type | Why It Matters |
|----------|-----------|----------------|
| Cost | `Fraction` (exact rational) | Eliminates rounding errors; 1/3 + 1/3 + 1/3 equals exactly 1, never 0.999... |
| audit_hash | Deterministic integer digest | Reproduces the same hash from the same complete trace on any platform |

**Glossary**
- **Abductive cycle**: The reasoning process of inferring the best explanation from observed evidence.
- **Frozen dataclass**: An immutable data structure; once created, it cannot be modified, preventing tampering.
- **Daubert traceability**: The legal standard requiring that forensic methods be testable, peer-reviewed, and accompanied by known error rates.
- **Deterministic integer arithmetic**: Calculations performed with exact whole-number ratios, yielding identical results every time without floating-point approximation.
- **Hypothesis lineage**: The documented ancestry and branching of all considered explanations.
- **Pivot signal**: A discriminating piece of evidence whose state (present/absent) alters the optimal hypothesis.

**【Scientific Note】**
The terminology of Peirce, Eco, and Grice is sometimes mistaken for metaphysical speculation. It is not. In this module, these concepts function as deterministic signal-processing constraints. Peirce’s abduction is the hypothesis-generation filter; Eco’s coherence criteria act like cross-sensor validation; Grice’s maxims operate as noise-reduction protocols. They are formal rules, not mysticism—exactly as a thermometer does not "believe" in temperature but measures it through calibrated expansion.

### ESPAÑOL
**What Is This Module?** -> **¿Qué es este módulo?**
Este módulo es el "árbol genealógico" de las hipótesis durante el ciclo abductivo de VIGÍA. En forense digital, el analista debe ver no solo el veredicto final, sino también el "mapa de alternativas": qué evidencia adicional, si se encontrara o faltara, cambiaría el veredicto y hacia dónde. El módulo registra cada hipótesis considerada, rastrea las señales que podrían cambiar el resultado y produce un informe de linaje inmutable, apto para la trazabilidad estándar Daubert. Garantiza la reproducibilidad mediante costos fraccionarios exactos y un hash de auditoría determinista sobre la traza completa.

**Key Concepts** -> **Conceptos clave**
Tabla 1: Clases principales
| Clase | Función | Analogía forense |
|-------|---------|------------------|
| HypothesisNode | Contenedor inmutable para una hipótesis investigativa | Una bolsa de evidencia sellada con etiqueta inalterable |
| PivotSignal | Señal cuya presencia o ausencia cambiaría el veredicto | Una huella dactilar latente que reclasificaría un allanamiento como acceso interno |
| LineageReport | Producto final del ciclo abductivo | El cuaderno de trabajo del perito presentado bajo Daubert |
| HypothesisLineageTracker | Registro del ciclo abductivo completo | El registro de cadena de custodia del razonamiento |

Tabla 2: Modelo de costo e integridad
| Propiedad | Tipo de dato | Por qué importa |
|-----------|--------------|-----------------|
| Costo | `Fraction` (racional exacto) | Elimina errores de redondeo; 1/3 + 1/3 + 1/3 es exactamente 1, nunca 0,999... |
| audit_hash | Resumen determinista entero | Reproduce el mismo hash a partir de la misma traza completa en cualquier plataforma |

**Glossary** -> **Glosario**
- **Ciclo abductivo**: Proceso de razonamiento para inferir la mejor explicación a partir de evidencia observada.
- **Dataclass congelada (frozen)**: Estructura de datos inmutable; una vez creada, no puede modificarse, evitando manipulación.
- **Trazabilidad Daubert**: Estándar legal que exige que los métodos forenses sean comprobables, revisados por pares y acompañados de tasas de error conocidas.
- **Aritmética determinista de enteros**: Cálculos realizados con razones exactas de números enteros, produciendo resultados idénticos sin aproximación de punto flotante.
- **Linaje de hipótesis**: La ascendencia documentada y la ramificación de todas las explicaciones consideradas.
- **Señal pivote (PivotSignal)**: Pieza de evidencia discriminante cuyo estado (presente/ausente) altera la hipótesis óptima.

**【Scientific Note】** -> **【Nota Científica】**
La terminología de Peirce, Eco y Grice a veces se confunde con especulación metafísica. No lo es. En este módulo, estos conceptos funcionan como restricciones deterministas de procesamiento de señales. La abducción de Peirce es el filtro de generación de hipótesis; los criterios de coherencia de Eco actúan como validación entre sensores; los máximos de Grice operan como protocolos de reducción de ruido. Son reglas formales, no misticismo: exactamente como un termómetro no "cree" en la temperatura, sino que la mide mediante expansión calibrada.

### РУССКИЙ
**What Is This Module?** -> **Что это за модуль?**
Этот модуль — «генеалогическое древо» гипотез в ходе абдуктивного цикла VIGÍA. В цифровой криминалистике аналитик должен видеть не только окончательный вердикт, но и «карту альтернатив»: какие дополнительные доказательства, будучи обнаруженными или отсутствующими, изменили бы вердикт и в каком направлении. Модуль регистрирует каждую рассмотренную гипотезу, отслеживает сигналы, способные изменить результат, и формирует неизменяемый отчёт о происхождении (lineage), соответствующий требованиям прослеживаемости по стандарту Daubert. Воспроизводимость обеспечивается за счёт точных дробных стоимостей и детерминированного хеширования всей трасы.

**Key Concepts** -> **Ключевые понятия**
Таблица 1: Основные классы
| Класс | Роль | Судебная аналогия |
|-------|------|-------------------|
| HypothesisNode | Неизменяемый контейнер для одной следственной гипотезы | Запечатанный пакет с доказательством и неизменяемой этикеткой |
| PivotSignal | Сигнал, наличие или отсутствие которого меняет вердикт | Латентный отпечаток, переквалифицирующий кражу во внутренний доступ |
| LineageReport | Итоговый результат абдуктивного цикла | Рабочая тетрадь эксперта, представляемая в суде по стандарту Daubert |
| HypothesisLineageTracker | Реестр полного абдуктивного цикла | Журнал учёта цепочки сохранности для рассуждений |

Таблица 2: Модель стоимости и целостности
| Свойство | Тип данных | Почему это важно |
|----------|------------|------------------|
| Стоимость (cost) | `Fraction` (точная рациональная дробь) | Устраняет ошибки округления; 1/3 + 1/3 + 1/3 точно равно 1, а не 0,999... |
| audit_hash | Детерминированное целочисленное значение | Воспроизводит один и тот же хеш из одной и той же полной трассы на любой платформе |

**Glossary** -> **Глоссарий**
- **Абдуктивный цикл**: Процесс рассуждения, при котором из наблюдаемых доказательств выводится наилучшее объяснение.
- **Frozen dataclass (замороженный класс данных)**: Неизменяемая структура данных; после создания её нельзя изменить, что предотвращает фальсификацию.
- **Прослеживаемость Daubert**: Правовой стандарт, требующий, чтобы криминалистические методы были проверяемыми, рецензируемыми и сопровождались известными частотами ошибок.
- **Детерминированная целочисленная арифметика**: Вычисления с точными отношениями целых чисел, дающие одинаковый результат каждый раз без приближений с плавающей точкой.
- **Происхождение гипотезы (lineage)**: Документированное родословие и ветвление всех рассмотренных объяснений.
- **Поворотный сигнал (PivotSignal)**: Различающее доказательство, состояние которого (наличие/отсутствие) изменяет оптимальную гипотезу.

**【Scientific Note】** -> **【Научное Примечание】**
Терминология Пирса, Эко и Грайса иногда ошибочно принимается за метафизическую спекуляцию. Это не так. В данном модуле эти понятия работают как детерминированные ограничения обработки сигналов. Абдукция Пирса — это фильтр генерации гипотез; критерии когерентности Эко действуют как межсенсорная валидация; максимы Грайса функционируют как протоколы подавления шума. Это формальные правила, а не мистика — точно так же, как термометр не «верит» в температуру, а измеряет её посредством калиброванного расширения.

### 中文
**What Is This Module?** -> **本模块是什么？**
本模块是 VIGÍA 溯因推理周期中的假设“家谱树”。在数字取证中，分析人员不仅要看到最终裁决，还要看到“替代方案图”：哪些额外证据的发现或缺失会改变裁决、以及朝哪个方向改变。该模块记录每一个被考虑的假设，追踪可能改变结果的信号，并生成一份不可篡改的谱系报告，以满足道伯特标准（Daubert）的可追溯性要求。它通过精确分数成本和基于完整轨迹的确定性哈希值来确保结果的可复现性。

**Key Concepts** -> **核心概念**
表 1：核心类
| 类 | 作用 | 取证类比 |
|----|------|----------|
| HypothesisNode | 单个调查假设的不可变容器 | 贴有不可更改标签的密封证据袋 |
| PivotSignal | 其存在或缺失会改变裁决的信号 | 能将入室盗窃重新归类为内部人员访问的潜在指纹 |
| LineageReport | 溯因推理周期的最终输出 | 按道伯特标准提交的专家工作手册 |
| HypothesisLineageTracker | 完整溯因推理周期的登记簿 | 推理过程的保管链日志 |

表 2：成本与完整性模型
| 属性 | 数据类型 | 重要性 |
|------|----------|--------|
| 成本 (cost) | `Fraction`（精确有理数） | 消除舍入误差；1/3 + 1/3 + 1/3 精确等于 1，而非 0.999… |
| audit_hash | 确定性整数摘要 | 在任何平台上，相同的完整轨迹都能复现出相同的哈希值 |

**Glossary** -> **术语表**
- **溯因推理周期 (Abductive cycle)**：从观测证据推断最佳解释推理过程。
- **冻结数据类 (Frozen dataclass)**：不可变的数据结构；一旦创建便无法修改，防止篡改。
- **道伯特可追溯性 (Daubert traceability)**：法律标准，要求取证方法具有可检验性、经过同行评审，并附有已知的错误率。
- **确定性整数运算 (Deterministic integer arithmetic)**：使用整数的精确比值进行计算，每次产生完全相同的结果，不存在浮点近似。
- **假设谱系 (Hypothesis lineage)**：所有被考虑解释的已记录起源与分支。
- **枢轴信号 (PivotSignal)**：一种具有判别性的取证工件，其状态（存在/缺失）会改变最优假设。

**【科学说明】**
皮尔士、艾柯与格赖斯的术语有时被误认为玄学思辨。事实并非如此。在本模块中，这些概念起到确定性信号处理约束的作用：皮尔士的溯因推理是假设生成过滤器；艾柯的连贯性标准相当于跨传感器验证；格赖斯的准则则充当降噪协议。它们是形式化规则，而非神秘主义——正如温度计并不“相信”温度，而是通过校准膨胀来测量它一样。

I also need to ensure I mention the functions `record()` and `finalize()` in the key concepts or explanation. And mention deterministic integer arithmetic instead of floating-point.

Also need to include the License line exactly: ""

I should check the Chinese terms again:
- 艾柯 (not Eco) -> used
- 格赖斯 (not Grice) -> used
- 取证工件 (not 制品) -> used in PivotSignal description (我将入室盗窃...潜在指纹 作为类比，但“取证工件”这个词需要在术语表或正文中出现。让我确保使用它。我可以在术语表或正文中用“取证工件”来描述证据。目前PivotSignal行里用了“潜在指纹”，但也许我应该在某个地方明确使用“取证工件”。让我修改PivotSignal的描述或增加一处。实际上，在中文里“取证工件”应该用来翻译artifact。我可以在术语表或某个地方提到“取证工件”作为证据的同义词。或者把PivotSignal那一行的描述改成包含“取证工件”。)

So I need to make sure these specific terms appear in the Chinese text.
- 艾柯: used in Scientific Note.
- 格赖斯: used in Scientific Note.
- 取证工件: need to use somewhere. Perhaps in the glossary or in the PivotSignal description. Let's add it to the description of PivotSignal: "一种具有判别性的取证工件（PivotSignal），其存在或缺失会改变最优假设。" Or in the table. Let me adjust the table: "其存在或缺失会改变裁决的取证工件" -> but PivotSignal is a signal, not exactly an artifact... but the user specifically wants 取证工件 used. Perhaps in the general text or glossary. I'll add a sentence in the "What Is This Module?" or glossary. Actually, the module deals with evidence. I can say in the plain language explanation: "...追踪可能改变结果的取证工件与信号..." Let's do that. Or in the glossary entry for PivotSignal: "一种关键取证工件". That satisfies the requirement.

- 逻辑断裂 (not 裂缝): need to use somewhere. Where? The docstring mentions "逻辑断裂"? Not explicitly. But maybe I can mention it in the scientific note or explanation as "逻辑断裂" when describing what the module prevents, or in the context of abduction. Actually, abduction often deals with filling logical gaps. I can say in the Chinese section: "该模块帮助识别逻辑断裂，即哪些证据缺失会导致假设不成立。" That would naturally use the term.

Chinese revisions:
- In "What Is This Module?": 该模块记录每一个被考虑的假设，追踪可能改变结果的信号与**取证工件**，并生成一份不可篡改的谱系报告... 它帮助分析人员识别**逻辑断裂**——即哪些证据的缺失会逆转当前结论。
- In Scientific Note: 皮尔士、**艾柯**与**格赖斯**的术语... (already there)

Good.

Now, check for floating-point math: I must NOT use floating-point math explanations. Emphasize deterministic integer arithmetic. I have `Fraction` and deterministic hash. I should make sure I don't say "floating point" anywhere. I currently say "no floating-point approximation" in Chinese glossary (浮点近似). The requirement says "Do NOT use floating-point math explanations". Saying "no floating point approximation" is okay, it's not explaining floating-point math, it's explaining why we avoid it. But to be safe, maybe phrase it as "exact rational arithmetic using integer numerators and denominators" and avoid mentioning floating point entirely. Let me revise to remove explicit mention of floating point in all languages, or keep it minimal as "without floating-point rounding". The requirement is "Do NOT use floating-point math explanations for deterministic systems." So I shouldn't explain how floating point works. I can just say "exact integer ratio arithmetic" or "deterministic integer arithmetic". I'll adjust.

English: "Calculations performed with exact whole-number ratios, yielding identical results every time." (No mention of float.)
Spanish: "Cálculos realizados con razones exactas de números enteros, produciendo resultados idénticos en cada ejecución." (No float.)
Russian: "Вычисления с точными отношениями целых чисел, дающие одинаковый результат при каждом запуске." (No float.)
Chinese: "使用整数的精确比值进行计算，每次产生完全相同的结果。" (No float.)

I can mention that `Fraction` avoids rounding errors without explaining floating point.

Also need to include `record()` and `finalize()` in the document. I'll add a small table or mention them in Key Concepts.

Let's add a Table 3: Lifecycle Operations
English:
| Function | Purpose | Daubert Relevance |
|----------|---------|-------------------|
| `record()` | Enters a new hypothesis into the tree | Creates an immutable timestamped entry in the reasoning log |
| `finalize(winner_id)` | Closes the cycle and emits the `LineageReport` | Locks the record and identifies the winning hypothesis for court review |

I'll include this in all languages.

Also, ensure the license line is present exactly. Usually placed at the end.

Now, structure:
I'll have top-level headings for each language, or perhaps just the four sections. The user said "Markdown with 4 language sections". So:

# Module Documentation: `vigia/abduction/hypothesis_lineage.py`

## ENGLISH
...

## ESPAÑOL
...

## РУССКИЙ
...

## 中文
...

Then at the very end, the license line.

I need to make sure the tone is academic and for non-Pythonists. So avoid code syntax except when naming the classes/functions as labels. Explain `Fraction` as "exact rational type" rather than Python class. Explain `frozen dataclass` as immutable data structure.

Let's refine each section for consistency.

### ENGLISH details:
- Title maybe not needed inside section, but I can just have the headings.
- "What Is This Module?" section: Keep it plain language. Mention it's like a lab notebook for hypotheses.
- Key Concepts tables:
  - Table 1: Core Components (Classes)
  - Table 2: Integrity Model (Properties)
  - Table 3: Lifecycle Functions
- Glossary: 6-8 terms.
- Scientific Note: sensor analogy.

### ESPAÑOL details:
- Make sure to mirror structure.
- "Árbol genealógico" is already in docstring, good to use.

### РУССКИЙ details:
- "генеалогическое древо" is good.
- Use "Пирс" for Peirce, "Эко" for Eco, "Грайс" for Grice.

### 中文 details:
- "家谱树" or "谱系树".
- Ensure terms: 艾柯, 格赖斯, 取证工件, 逻辑断裂.
- Use "道伯特" for Daubert (standard transliteration).
- Use "冻结数据类" for frozen dataclass.

Let's carefully write out the content to ensure no hallucination of internal implementation (like specific hash algorithms). Just say "deterministic audit hash derived from the complete trace".

One more thing: The user said "Be thorough but concise." So I should not be overly verbose, but cover all requirements.

Let's write the final output.

I'll place the license line once at the bottom, as it is universal. Or should it be in each section? The requirement says "License line: ''" It doesn't explicitly say per section, but since it says "Each section must include..." and then separately lists the license line, I think putting it once at the end is fine. However, to be safe and compliant, I'll put it at the end of the document, maybe under a universal heading. Actually, looking at the requirements: "5. License line: ''" It's a global requirement. I'll include it at the very bottom.

Let's draft the full text now.

---

# Module Documentation: `vigia/abduction/hypothesis_lineage.py`

## ENGLISH

### What Is This Module?
This module serves as the **family tree of hypotheses** during VIGÍA’s abductive reasoning cycle. In digital forensics, a SANS analyst must see more than a final verdict; the analyst needs a **map of alternatives**—a clear view of what additional evidence, if discovered or absent, would pivot the conclusion in another direction. This module records every hypothesis under consideration, tracks the discriminating signals that could alter the outcome, and produces an immutable **lineage report** that satisfies Daubert-standard traceability. To guarantee reproducibility, the module represents all costs as exact integer ratios and derives an audit hash deterministically from the complete reasoning trace.

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
Terminology drawn from Peirce, Eco, and Grice is occasionally dismissed as metaphysical. It is not. Within this module, those concepts operate as **deterministic signal-processing constraints**. Peirce’s abduction is the hypothesis-generation filter; Eco’s coherence criteria serve as cross-sensor validation rules; Grice’s maxims function as noise-reduction protocols. They are formal boundary conditions, not mysticism—precisely as a thermometer does not “believe” in temperature but registers it through calibrated physical expansion.

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
La terminología de Peirce, Eco y Grice se descarta a veces como metafísica. No lo es. Dentro de este módulo, esos conceptos operan como **restricciones deterministas de procesamiento de señales**. La abducción de Peirce es el filtro de generación de hipótesis; los criterios de coherencia de Eco sirven como reglas de validación entre sensores; los máximos de Grice funcionan como protocolos de reducción de ruido. Son condiciones de contorno formales, no misticismo: exactamente como un termómetro no “cree” en la temperatura, sino que la registra mediante expansión física calibrada.

---

## РУССКИЙ

### Что это за модуль?
Этот модуль представляет собой **генеалогическое древо гипотез** в ходе абдуктивного цикла VIGÍA. В цифровой криминалистике аналитик SANS должен видеть не только окончательный вердикт, но и **карту альтернатив** — чёткое представление о том, какие дополнительные доказательства, будучи обнаруженными или отсутствующими, изменили бы заключение и в каком направлении. Модуль регистрирует каждую рассмотренную гипотезу, отслеживает различающие сигналы, способные изменить результат, и формирует неизменяемый **отчёт о происхождении (lineage)**, отвечающий требованиям прослеживаемости по стандарту Daubert. Для гарантии воспроизводимости все стоимости представлены в виде точных отношений целых чисел, а аудит-хеш вычисляется детерминированно
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
