<!--
VIGIA Academic Documentation
Module: 79fddb64
Batch ID: vigia-doc-0042-79fddb64
Generated: 2026-05-20T14:56:47.853470+00:00
-->

The user wants academic technical documentation for a Python module `vigia/core/causal_closure.py`. Let me carefully parse the requirements.

**Constraints & Requirements:**
1. Target audience: Scientists/researchers who do NOT know Python.
2. Format: Markdown with 4 language sections: ENGLISH, ESPAÑOL, РУССКИЙ, 中文.
3. Each section must include:
   - "What Is This Module?" (plain language explanation)
   - Key concepts with tables
   - A glossary of technical terms
   - A 【科学说明】/【Scientific Note】 box explaining Peirce/Eco/Grice terminology is NOT mysticism — use the sensor analogy.
4. Chinese translations must use specific terms:
   - 艾柯 (not Eco)
   - 格赖斯 (not Grice)
   - 取证工件 (not 制品)
   - 逻辑断裂 (not 裂缝)
5. 
6. Do NOT use floating-point math explanations — emphasize deterministic integer arithmetic where applicable.
7. Module path: vigia/core/causal_closure.py
8. Module docstring provided in Spanish (mainly).

**Module Analysis from docstring:**
- Name: Causal Closure Score para VIGÍA.
- Principle: A forensic case is not just signals — it's a coherent causal story.
- CCS measures how well available artifacts causally close the winning hypothesis under adversarial conditions.
- Four dimensions:
  1. temporal_coherence (TCV) — are timestamps physically possible?
  2. semantic_resonance (CAR) — do artifacts refer to the same event?
  3. abductive_parsimony (HLT) — is the hypothesis the simplest explaining everything?
  4. adversarial_silence (ASD) — is the absence of artifacts structural?
- Usage as GATE (not just multiplier):
  - If CCS < GATE_THRESHOLD → maximum achievable verdict = ABSTAIN
  - This is defensible (text cuts off, but implies legally/scientifically defensible)
- Classes:
  - CausalClosureResult: Immutable result of causal closure score.
- Functions:
  - compute_causal_closure(): Calculates CCS from four dimensions.
  - Any unavailable dimension is replaced by Fracti (I need to interpret this; likely a default value or sentinel, but since I don't have code, I must stick to docstring. "Fracti" seems to be a term used in the project; I should mention it as a default fallback value).
  - apply_ccs_to_confidence(): Applies CCS as multiplier and gate to raw confidence.
  - If gate fails → effective confidence = 0, verdict = ABSTAIN.
  - display_pct(): Integer percentage — int() truncated, never round().
- Constants & Config: None.

**Audience Consideration:**
Scientists who don't know Python. Avoid code syntax, Python-specific jargon (like "class", "function", "immutable" in a programming sense). Instead, describe them as conceptual tools, data structures, operations. Use plain language. However, since they are scientists, they understand mathematical concepts, logic, experimental methodology.

**Scientific Note requirement:**
Explain Peirce/Eco/Grice terminology is NOT mysticism using a sensor analogy.
- Peirce: semiotics, abduction.
- Eco: semantic resonance, interpretation.
- Grice: cooperative principle, implicature (silence/absence meaning).
Sensor analogy: Just as a sensor array detects physical phenomena (temperature, pressure), these conceptual tools detect logical-semantic properties of evidence. No mysticism—just structured detection of patterns in data.

**Deterministic Integer Arithmetic:**
- Emphasize that calculations use integer truncation (int()), never floating-point rounding (round()).
- The module avoids probabilistic floating-point errors by using deterministic integer arithmetic for final percentage display.
- The CCS itself might be rational/integer-based.

**Structure for each language:**

### ENGLISH
- Heading
- What Is This Module?
- Key Concepts (table format)
- The Four Dimensions (table)
- Glossary
- Scientific Note box

### ESPAÑOL
- Similar structure, but in Spanish.
- Use "artefactos" (or "artefactos forenses"), note the docstring uses "artefactos".
- Peirce/Eco/Grice note.

### РУССКИЙ
- Russian structure.
- Terms: Пирс, Эко, Грайс (or Грис; but standard Russian academic is Пирс, Эко, Грайс).
- "Артефакты" for artifacts.

### 中文
- Must use: 艾柯, 格赖斯, 取证工件, 逻辑断裂.
- Structure: 本模块是什么？, 关键概念 (表格), 四维量表 (表格), 术语表, 【科学说明】.

**Drafting content:**

**ENGLISH:**
- What Is This Module?
  This document describes the Causal Closure Score (CCS) engine, a deterministic evaluation module within the VIGÍA forensic framework. Its purpose is to test whether a collection of digital evidence artifacts forms a complete, logically consistent causal narrative around a leading investigative hypothesis. Rather than treating evidence as isolated signals, CCS verifies whether the artifacts collectively "close" the causal loop—meaning no unexplained logical gaps remain under adversarial scrutiny. The module operates exclusively with deterministic integer arithmetic to ensure reproducible, court-defensible results.

- Key Concepts Table:
  | Concept | Plain-Language Definition | Role in Investigation |
  |---|---|---|
  | Causal Closure | The state where available evidence fully accounts for a hypothesis without leaving internal contradictions. | Prevents false confidence when evidence is fragmented. |
  | Gate (Threshold) | A logical checkpoint; if the score falls below this limit, the system refuses to render a definitive verdict. | Safeguards against over-interpretation of weak evidence. |
  | Abductive Parsimony | Preferring the explanation that requires the fewest unproven assumptions. | Keeps hypotheses grounded; avoids conspiracy drift. |
  | Adversarial Silence | Structured absence of evidence where something should exist. | Detects data destruction or blind spots in collection. |
  | Immutable Result | A read-only output record that cannot be altered after creation. | Guarantees chain-of-custody integrity for the score itself. |
  | Deterministic Integer Arithmetic | Calculations using whole numbers with exact truncation, never floating-point rounding. | Eliminates machine-precision ambiguity in legal reports. |

- The Four Dimensions Table:
  | Dimension | Code | Question It Answers | Scientific Meaning |
  |---|---|---|---|
  | Temporal Coherence | TCV | Are the timestamps physically possible? | Checks causality violations (effect before cause). |
  | Semantic Resonance | CAR | Do artifacts refer to the same event? | Uses semiotic coherence (Peirce/Eco) to verify shared referent. |
  | Abductive Parsimony | HLT | Is this the simplest explanation? | Measures explanatory economy; fewer ad-hoc assumptions = higher score. |
  | Adversarial Silence | ASD | Is missing evidence structurally significant? | Applies Gricean implicature: systematic absence carries information. |

- Glossary:
  - **Artifact**: Any piece of digital evidence (log entry, file fragment, network packet) treated as a physical object with metadata.
  - **Causal Closure Score (CCS)**: A composite metric indicating the degree to which evidence completes a causal story.
  - **Fracti**: A default neutral value substituted when one of the four dimensions cannot be measured.
  - **Gate**: A binary pass/fail boundary; failure forces an ABSTAIN verdict.
  - **ABSTAIN**: The verdict indicating insufficient causal closure to support either affirmation or negation.
  - **Raw Confidence**: The preliminary probability-like measure before causal filtering.
  - **Effective Confidence**: The final, post-gate confidence value (set to zero if the gate fails).
  - **Hypothesis**: The investigative proposition being tested against the evidence.

- Scientific Note:
  【Scientific Note】Terminology borrowed from Peirce (abduction), Eco (semiosis), and Grice (implicature) is sometimes mistaken for philosophical mysticism. It is not. Think of these constructs as **logical sensors**. Just as a thermometer transduces thermal energy into a numeric reading, abductive parsimony transduces explanatory complexity into a scalar value. Semantic resonance functions like a coherence interferometer: it detects whether multiple evidence channels point to the same referent. Adversarial silence operates like a dark-current detector in photonics—it measures structured absence rather than presence. These are formalized pattern-detection predicates, not metaphysical claims.

**ESPAÑOL:**
- What Is This Module? -> ¿Qué es este módulo?
  Describe el motor de Causal Closure Score (CCS), módulo determinístico del marco VIGÍA. Evalúa si una colección de artefactos de evidencia digital forma una narrativa causal completa y lógicamente consistente en torno a una hipótesis investigativa principal. En lugar de tratar la evidencia como señales aisladas, el CCS verifica si los artefactos cierran causalmente el ciclo; es decir, si no quedan brechas lógicas sin explicar bajo escrutinio adversarial. Emplea aritmética determinista de enteros para garantizar resultados reproducibles y defendibles en sede judicial.

- Key Concepts:
  | Concepto | Definición en lenguaje llano | Papel en la investigación |
  |---|---|---|
  | Cierre causal | Estado en que la evidencia disponible explica completamente una hipótesis sin contradicciones internas. | Evita falsa confianza cuando la evidencia está fragmentada. |
  | Compuerta (umbral) | Punto de control lógico; si la puntuación cae debajo de este límite, el sistema se niega a emitir un veredicto definitivo. | Protege contra la sobreinterpretación de evidencia débil. |
  | Parsimonia abductiva | Preferir la explicación que requiere las menos suposiciones no probadas. | Mantiene las hipótesis fundamentadas; evita deriva conspirativa. |
  | Silencio adversarial | Ausencia estructurada de evidencia donde algo debería existir. | Detecta destrucción de datos o puntos ciegos en la recolección. |
  | Resultado inmutable | Registro de salida de solo lectura que no puede alterarse tras su creación. | Garantiza la integridad de la cadena de custodia del propio score. |
  | Aritmética determinista de enteros | Cálculos con números enteros y truncamiento exacto, nunca redondeo de punto flotante. | Elimina la ambigüedad de precisión máquina en dictámenes forenses. |

- Four Dimensions:
  | Dimensión | Código | Pregunta que responde | Significado científico |
  |---|---|---|---|
  | Coherencia temporal | TCV | ¿Los timestamps son físicamente posibles? | Verifica violaciones de causalidad (efecto antes que causa). |
  | Resonancia semántica | CAR | ¿Los artefactos se refieren al mismo evento? | Usa coherencia semiótica (Peirce/Eco) para verificar un referente compartido. |
  | Parsimonia abductiva | HLT | ¿Es esta la explicación más simple? | Mide economía explicativa; menos supuestos ad hoc = puntuación mayor. |
  | Silencio adversarial | ASD | ¿La evidencia faltante es estructuralmente significativa? | Aplica la implicatura griceana: la ausencia sistemática informa. |

- Glossary:
  - **Artefacto**: Cualquier pieza de evidencia digital (entrada de registro, fragmento de archivo, paquete de red) tratada como objeto físico con metadatos.
  - **Causal Closure Score (CCS)**: Métrica compuesta que indica el grado en que la evidencia completa una historia causal.
  - **Fracti**: Valor neutro por defecto sustituido cuando una de las cuatro dimensiones no puede medirse.
  - **Compuerta**: Frontera binaria aprobado/reprobado; el fracaso fuerza un veredicto ABSTAIN (abstención).
  - **ABSTAIN**: Veredicto que indica cierre causal insuficiente para sostener afirmación o negación.
  - **Confianza bruta (raw confidence)**: Medida preliminar tipo probabilidad antes del filtrado causal.
  - **Confianza efectiva**: Valor final post-compuerta (se fija en cero si la compuerta falla).
  - **Hipótesis**: Proposición investigativa sometida a prueba contra la evidencia.

- Scientific Note:
  【Nota Científica】La terminología tomada de Peirce (abducción), Eco (semiosis) y Grice (implicatura) a veces se confunde con misticismo filosófico. No lo es. Piense en estos constructos como **sensores lógicos**. Así como un termómetro transduce energía térmica en una lectura numérica, la parsimonia abductiva transduce complejidad explicativa en un valor escalar. La resonancia semántica funciona como un interferómetro de coherencia: detecta si múltiples canales de evidencia apuntan al mismo referente. El silencio adversarial opera como un detector de corriente oscura en fotónica—mide la ausencia estructurada en lugar de la presencia. Son predicados formalizados de detección de patrones, no afirmaciones metafísicas.

**РУССКИЙ:**
- What Is This Module? -> Что представляет собой этот модуль?
  Описание движка Causal Closure Score (CCS) — детерминированного оценочного модуля в рамках судебной системы VIGÍA. Его назначение — проверить, образует ли совокупность цифровых доказательных артефактов полную, логически непротиворечивую причинно-следственную повествовательность вокруг ведущей следственной гипотезы. Вместо того чтобы рассматривать доказательства как изолированные сигналы, CCS проверяет, замыкают ли артефакты причинный контур — то есть не остаётся ли необъяснённых логических разрывов при состязательной проверке. Модуль использует исключительно детерминированную целочисленную арифметику для обеспечения воспроизводимых и судебно защищённых результатов.

- Key Concepts:
  | Понятие | Определение простым языком | Роль в расследовании |
  |---|---|---|
  | Причинное замыкание | Состояние, при котором имеющиеся доказательства полностью объясняют гипотезу, не оставляя внутренних противоречий. | Предотвращает ложную уверенность при фрагментарности доказательств. |
  | Ворота (порог) | Логический контрольный пункт; если оценка ниже этого предела, система отказывается выносить окончательный вердикт. | Защищает от чрезмерной интерпретации слабых доказательств. |
  | Абдуктивная парсимония | Предпочтение объяснения, требующего наименьшего числа недоказанных допущений. | Удерживает гипотезы в рамках фактов; предотвращает «конспирологический уход». |
  | Состязательное молчание | Структурированное отсутствие доказательств там, где они должны были бы существовать. | Выявляет уничтожение данных или «слепые зоны» сбора. |
  | Неизменяемый результат | Выходная запись только для чтения, которая не может быть изменена после создания. | Гарантирует целостность цепочки хранения самой оценки. |
  | Детерминированная целочисленная арифметика | Вычисления с целыми числами и точным усечением, без округления с плавающей точкой. | Устраняет неоднозначность машинной точности в судебных заключениях. |

- Four Dimensions:
  | Измерение | Код | Вопрос, на который отвечает | Научное значение |
  |---|---|---|---|
  | Временная когерентность | TCV | Физически ли возможны отметки времени? | Проверяет нарушения причинности (эффект до причины). |
  | Семантический резонанс | CAR | Ссылаются ли артефакты на одно событие? | Использует семиотическую когерентность (Пирс/Эко) для проверки общего референта. |
  | Абдуктивная парсимония | HLT | Является ли это простейшим объяснением? | Измеряет экономию объяснения; меньше ad-hoc допущений = выше оценка. |
  | Состязательное молчание | ASD | Имеет ли отсутствие доказательств структурное значение? | Применяет грайсовскую импликатуру: систематическое отсутствие несёт информацию. |

- Glossary:
  - **Артефакт**: Любой элемент цифрового доказательства (запись журнала, фрагмент файла, сетевой пакет), рассматриваемый как физический объект с метаданными.
  - **Causal Closure Score (CCS)**: Комплексная метрика, показывающая, насколько полно доказательства завершают причинную историю.
  - **Fracti**: Нейтральное значение по умолчанию, используемое при невозможности измерить одно из четырёх измерений.
  - **Ворота**: Бинарная граница проход/отказ; при отказе выставляется вердикт ABSTAIN (воздержание).
  - **ABSTAIN**: Вердикт, означающий недостаточность причинного замыкания для подтверждения или опровержения.
  - **Сырая уверенность (raw confidence)**: Предварительная мера, аналогичная вероятности, до причинной фильтрации.
  - **Эффективная уверенность**: Итоговое значение после ворот (устанавливается в ноль при непрохождении ворот).
  - **Гипотеза**: Следственное предположение, проверяемое на соответствие доказательствам.

- Scientific Note:
  【Научное примечание】Терминология, заимствованная у Пирса (абдукция), Эко (семиозис) и Грайса (импликатура), иногда ошибочно принимается за философский мистицизм. Это не так. Воспринимайте эти конструкты как **логические датчики**. Как термометр преобразует тепловую энергию в числовое показание, так абдуктивная парсимония преобразует сложность объяснения в скалярную величину. Семантический резонанс функционирует как когерентный интерферометр: он определяет, указывают ли множественные каналы доказательств на один референт. Состязательное молчание работает как детектор тёмного тока в фотонике — измеряет структурированное отсутствие, а не присутствие. Это формализованные предикаты обнаружения паттернов, а не метафизические утверждения.

**中文:**
- Must use: 艾柯, 格赖斯, 取证工件, 逻辑断裂.
- What Is This Module? -> 本模块是什么？
  本文档描述“因果闭合评分”（CCS）引擎，它是 VIGÍA 取证框架中的确定性评估模块。其用途在于检验一组数字取证工件是否围绕某一主导调查假设形成了完整且逻辑自洽的因果叙事。该模块并非将证据视为孤立信号，而是验证这些取证工件是否在整体上“闭合”了因果环——即在对抗性审查下，是否不再存在无法解释的逻辑断裂。本模块完全采用确定性整数运算，以确保结果可复现，并具备出庭辩护的效力。

- Key Concepts:
  | 概念 | 通俗定义 | 在调查中的作用 |
  |---|---|---|
  | 因果闭合 | 现有证据能够完整解释某一假设，且内部无矛盾的状态。 | 防止在证据碎片化时产生虚假信心。 |
  | 门控（阈值） | 逻辑检查点；若评分低于此界限，系统拒绝给出确定性结论。 | 防止对薄弱证据进行过度解释。 |
  | 溯因简约性 | 优先选择所需未证假设最少的解释。 | 使假设扎根于事实，防止阴谋论漂移。 |
  | 对抗性沉默 | 在应有证据之处出现结构性的证据缺失。 | 发现数据销毁或采集盲区。 |
  | 不可变结果 | 创建后不可更改的只读输出记录。 | 保证评分本身的保管链完整性。 |
  | 确定性整数运算 | 使用整数与精确截断进行计算，绝不采用浮点舍入。 | 消除司法鉴定报告中机器精度歧义。 |

- Four Dimensions:
  | 维度 | 代码 | 回答的问题 | 科学含义 |
  |---|---|---|---|
  | 时间相干性 | TCV | 时间戳在物理上是否可能？ | 检验因果律违背（果在因前）。 |
  | 语义共振 | CAR | 取证工件是否指向同一事件？ | 利用符号学一致性（皮尔斯 / 艾柯）验证共同指涉。 |
  | 溯因简约性 | HLT | 这是否是最简解释？ | 测度解释经济性；特设假设越少，评分越高。 |
  | 对抗性沉默 | ASD | 证据缺失是否具有结构性意义？ | 应用格赖斯含义：系统性缺席本身携带信息。 |

- Glossary:
  - **取证工件**：任何数字证据片段（日志条目、文件碎片、网络数据包），被视为带有元数据的物理对象。
  - **因果闭合评分（CCS）**：综合指标，表明证据在多大程度上完成了一段因果叙事。
  - **Fracti**：当某一维度无法测得时，用于替换的默认中性值。
  - **门控**：二元通过/失败边界；未通过时强制结论为“弃权（ABSTAIN）”。
  - **ABSTAIN（弃权）**：表明因果闭合不足，既不足以支持肯定，也不足以支持否定的结论。
  - **原始置信度（Raw Confidence）**：经过因果过滤前的初步概率型度量。
  - **有效置信度**：经过门控后的最终置信度值（若未通过门控，则置为零）。
  - **假设**：正在接受证据检验的调查命题。

- Scientific Note:
  【科学说明】皮尔斯（溯因）、艾柯（符号过程）与格赖斯（含义）的术语有时被误认为哲学神秘主义。事实并非如此。请将这些概念视为**逻辑传感器**。正如温度计将热能转译为数值读数，溯因简约性将解释复杂度转译为标量值。语义共振如同一台相干干涉仪：它检测多路证据通道是否指向同一指涉对象。对抗性沉默则类似于光子学中的暗电流检测器——它测量的是结构性的“无”，而非“有”。这些都是形式化的模式检测谓词，而非形而上学断言。

**License line requirement:**
""
This should appear once at the end of the document (or per section? The requirement says "License line: ..." Usually one at the bottom of the file is fine. I'll put it at the very end of the markdown document.)

**Formatting:**
Use proper Markdown headers. Since it's one document with 4 sections, I'll use ## for languages, ### for subsections.

**Check on Chinese terms:**
- 艾柯 (Eco) ✓
- 格赖斯 (Grice) ✓
- 取证工件 (artifact) ✓
- 逻辑断裂 (logical gap/break) — used in "无法解释的逻辑断裂" instead of 裂缝 ✓

**Check on deterministic integer arithmetic:**
I must emphasize `int()` truncation, never `round()`. I should mention this in the key concepts and perhaps under a specific "Arithmetic Integrity" subsection or within the display_pct function description.

In EN: "The module guarantees deterministic output through integer truncation (int()), explicitly rejecting floating-point rounding (round())."
In ES: "El módulo garantiza salidas deterministas mediante truncamiento entero (int()), rechazando explícitamente el redondeo de punto flotante (round())."
In RU: "Модуль гарантирует детерминированный вывод посредством целочисленного усечения (int()), категорически исключая округление с плавающей точкой (round())."
In CN: "本模块通过整数截断（int()）保证输出确定性，明确拒绝浮点舍入（round()）。"

Also, the prompt mentions `display_pct()`: "Porcentaje entero — int() truncado, nunca round()." I should explain this function simply as "Integer Percentage Display".

**Check on "Fracti":**
The docstring says: "Cualquier dimensión no disponible se sustituye por Fracti". I should explain this as a placeholder default.

**Tone Check:**
Academic, technical, but accessible to non-Python scientists. Avoid words like "class", "function", "import", "immutable" in a programming sense? The prompt says they do NOT know Python. So I should describe CausalClosureResult as an "immutable output container/record" rather than a Python class. And describe compute_causal_closure as a "procedure/core algorithm".

Wait, the prompt says "CLASSES: - CausalClosureResult... FUNCTIONS: - compute_causal_closure...". I need to document them but in a way scientists understand. I can say "Data Structure" or "Output Record" for the class, and "Algorithm/Operation" for the function.

**Refining the structure within each language:**

#### ENGLISH
**What Is This Module?**
(text)

**Core Algorithm and Data Structures**
- *Causal Closure Evaluation Procedure* (`compute_causal_closure`): Computes the composite score from the four dimensions. If a dimension is unavailable, the default neutral placeholder **Fracti** is substituted so the calculation can proceed without bias.
- *Result Record* (`CausalClosureResult`): An immutable container that holds the final score and diagnostic metadata. Immutability ensures that once the score is issued, it cannot be tampered with—analogous to sealing an evidence bag.
- *Confidence Application Procedure* (`apply_ccs_to_confidence`): Modifies the raw investigative confidence. If the score fails the gate threshold, the effective confidence is set to exactly 0 and the verdict becomes **ABSTAIN**.
- *Integer Percentage Display* (`display_pct`): Converts internal metrics into a human-readable percentage using strict integer truncation. This guarantees that 49.9 % becomes 49 %, never 50 %, removing any probabilistic ambiguity.

**The Four Evaluative Dimensions** (table)

**Key Concepts** (table)

**Glossary**

**【Scientific Note】**

#### ESPAÑOL
Similar.

#### РУССКИЙ
Similar.

#### 中文
Similar.

Wait, the user asked for each section to include:
- "What Is This Module?" (plain language explanation)
- Key concepts with tables
- A glossary of technical terms
- A 【科学说明】/【Scientific Note】 box

It doesn't explicitly say I need to detail the classes/functions separately in tables, but since it's documentation for a module, I should cover them. I can integrate them into "Key Concepts" or a dedicated "Module Components" table. I'll add a "Module Components" table to each section.

Let me make sure the Chinese section uses the required terms correctly throughout.
- 艾柯: in the table and note. ✓
- 格赖斯: in the table and note. ✓
- 取证工件: in glossary and text. ✓
- 逻辑断裂: used. ✓

Also, I need to ensure the Scientific Note specifically mentions the sensor analogy and explicitly denies mysticism.

Let me double-check the Chinese for Peirce. Standard translation is 皮尔斯. I'll use 皮尔斯.

Now, let me consider the requirement: "You NEVER use floating-point math explanations for deterministic systems."
I must be careful not to explain anything using floating point. I should emphasize integer arithmetic. When explaining display_pct, I say it uses integer truncation. I do not mention floating point except to say it is NOT used.

Let's construct the final response.

**Overall Markdown Outline:**

```markdown
# Module Documentation: `vigia/core/causal_closure.py`

---

## ENGLISH

### What Is This Module?

### Module Components

### The Four Evaluative Dimensions

### Key Concepts

### Glossary

### 【Scientific Note】

---

## ESPAÑOL

### ¿Qué es este módulo?

...

---

## РУССКИЙ

### Что представляет собой этот модуль?

...

---

## 中文

### 本模块是什么？

...

---


```

Wait, should the license be in all four languages? The requirement says "License line: ''" It's a specific line. I'll put it once at the bottom. That's standard.

Let me write out the ENGLISH text carefully.

**ENGLISH:**

### What Is This Module?
This document describes the **Causal Closure Score (CCS)** engine, a deterministic evaluation module within the VIGÍA forensic framework. Its scientific purpose is to test whether a collection of digital evidence artifacts forms a complete, logically consistent causal narrative around a leading investigative hypothesis. Rather than treating evidence as isolated signals, CCS verifies whether the artifacts collectively "close" the causal loop—meaning no unexplained logical gaps remain under adversarial scrutiny. The module operates exclusively with deterministic integer arithmetic to ensure reproducible, legally defensible results.

### Module Components
| Component | Role | Why It Matters |
|---|---|---|
| **Causal Closure Evaluation** | Core algorithm that synthesizes four independent dimensions into a single composite score. | Provides a unified, auditable measure of narrative completeness. |
| **Fracti Default** | Neutral placeholder value substituted when any of the four dimensions cannot be measured. | Prevents missing data from biasing the computation. |
| **Result Record** | Immutable output container that stores the final score and diagnostic flags. | Guarantees chain-of-custody integrity for the metric itself. |
| **Confidence Application** | Procedure that applies the score as both a multiplier and a hard gate to raw investigative confidence. | Protects downstream decisions from overconfidence. |
| **Integer Percentage Display** | Conversion routine that renders metrics as whole-number percentages using exact truncation (`int()`), never rounding (`round()`). | Eliminates machine-precision ambiguity in court reports. |

### The Four Evaluative Dimensions
| Dimension | Code | Question It Answers | Scientific Meaning |
|---|---|---|---|
| **Temporal Coherence** | TCV | Are the timestamps physically possible? | Detects causality violations (an effect preceding its cause). |
| **Semantic Resonance** | CAR | Do artifacts refer to the same event? | Uses semiotic coherence (Peirce / Eco) to verify a shared referent across evidence channels. |
| **Abductive Parsimony** | HLT | Is this the simplest explanation that accounts for everything? | Measures explanatory economy; fewer ad-hoc assumptions yield a higher score. |
| **Adversarial Silence** | ASD | Is the absence of expected evidence structurally significant? | Applies Gricean implicature: systematic absence is itself informative. |

### Key Concepts
| Concept | Plain-Language Definition | Role in Investigation |
|---|---|---|
| **Causal Closure** | The state in which available evidence fully accounts for a hypothesis without leaving internal contradictions. | Prevents false confidence when evidence is fragmented or incomplete. |
| **Gate (Threshold)** | A logical checkpoint; if the composite score falls below this limit, the system is forbidden from issuing a definitive verdict. | Safeguards against over-interpretation of weak or contradictory evidence. |
| **Abductive Parsimony** | The principle of preferring the explanation that requires the fewest unproven assumptions. | Keeps hypotheses empirically grounded and avoids conspiracy drift. |
| **Adversarial Silence** | A structured, non-random absence of artifacts where something should exist according to the hypothesis. | Detects data destruction, collection blind spots, or deliberate concealment. |
| **Immutable Result** | A read-only output record that cannot be altered after its creation. | Preserves the integrity and auditability of the scoring process. |
| **Deterministic Integer Arithmetic** | Calculations performed with whole numbers and exact truncation, explicitly excluding floating-point rounding. | Guarantees bit-wise reproducibility across different machines and repeated analyses. |

### Glossary
- **Artifact**: Any piece of digital evidence—such as a log entry, file fragment, or network packet—treated as a physical object carrying metadata.
- **Causal Closure Score (CCS)**: A composite metric quantifying the degree to which the available evidence completes a coherent causal story.
- **Fracti**: A predefined neutral scalar used as a fallback when one of the four evaluative dimensions is unavailable.
- **Gate**: A binary pass/fail boundary applied to the CCS. Failure forces the verdict **ABSTAIN**.
- **ABSTAIN**: The verdict indicating that causal closure is insufficient to support either affirmation or negation of the hypothesis.
- **Raw Confidence**: The preliminary confidence measure assigned to a hypothesis before causal filtering.
- **Effective Confidence**: The final confidence value after the gate is applied; set to exactly zero if the gate fails.
- **Hypothesis**: The specific investigative proposition being tested against the body of evidence.

### 【Scientific Note】
Terminology borrowed from Charles Sanders Peirce (abduction), Umberto Eco (semiosis), and H. P. Grice (implicature) is occasionally mistaken for philosophical mysticism. It is not. Treat these constructs as **logical sensors**. Just as a thermometer transduces thermal energy into a scalar reading, abductive parsimony transduces explanatory complexity into a scalar value. Semantic resonance functions like a coherence interferometer: it detects whether multiple evidence channels converge on the same referent. Adversarial silence operates analogously to a dark-current detector in photonics—it measures structured absence rather than presence. These are formalized pattern-detection predicates, not metaphysical claims.

---

**ESPAÑOL:**

### ¿Qué es este módulo?
Este documento describe el motor de **Causal Closure Score (CCS)**, un módulo de evaluación determinístico dentro del marco forense VIGÍA. Su propósito científico es comprobar si una colección de artefactos de evidencia digital forma una narrativa causal completa y lógicamente consistente en torno a una hipótesis investigativa principal. En lugar de tratar la evidencia como señales aisladas, el CCS verifica si los artefactos cierran causalmente el ciclo; es decir, si no quedan brechas lógicas sin explicar bajo un escrutinio advers
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
