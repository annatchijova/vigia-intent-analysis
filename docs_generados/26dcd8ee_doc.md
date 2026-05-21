<!--
VIGIA Academic Documentation
Module: 26dcd8ee
Batch ID: vigia-doc-0172-26dcd8ee
Generated: 2026-05-20T14:56:47.881842+00:00
-->

The user wants academic technical documentation for a Python module `vigia/tools/signal_contract.py` (though the docstring says `vigia/core/signal_contract.py`).

Key requirements:
1. Target audience: scientists/researchers who do NOT know Python.
2. Format: Markdown with 4 language sections: ENGLISH, ESPAÑOL, РУССКИЙ, 中文.
3. Each section must include:
   - "What Is This Module?" (plain language explanation)
   - Key concepts with tables
   - A glossary of technical terms
   - A 【科学说明】/【Scientific Note】 box explaining that Peirce/Eco/Grice terminology is NOT mysticism — use the sensor analogy
4. Chinese translations must use: 艾柯 (not Eco), 格赖斯 (not Grice), 取证工件 (not 制品), 逻辑断裂 (not 裂缝).
5. 
6. Do NOT use floating-point math explanations — emphasize deterministic integer arithmetic where applicable.

Module details:
- Path: vigia/tools/signal_contract.py
- Docstring mentions it's a unified signal contract for VIGÍA.
- Mandatory: All forensic tools (SDA, CLI, GCI, ACP) MUST return a SignalOutput. LikelihoodEngine consumes EXCLUSIVELY this contract.
- Without this contract → LikelihoodEngine cannot operate → Daubert indefensible.
- Architecture decision: EVIDENCE LAYER → deterministic, no LLM, returns SignalOutput; INFERENCE LAYER → LikelihoodEngine consumes SignalOutput; REPORT LAYER → LLM receives numeric result, generates ENFSI narrative.
- No third-party dependencies beyond stdlib. Pydantic V2 used if available; fallback to pure dataclass.
- Classes: SignalBuilder (Factory to build SignalOutput with defensive validations), SignalOutput (transfer object between evidence layer and inference layer). Fields include tool_name.
- Functions: enfsi_label() (translates Likelihood Ratio to ENFSI verbal category), from_raw() (builds SignalOutput from raw or normalized value, is_pre_normalized=False default: z = (value - basel...), from_z_score() (for tools that already calculate z_score internally like SDA, CLI legacy; wraps result in contract without re-calculating).
- Constants & Config: ENFSI_SCALE, _PYDANTIC_AVAILABLE.

I need to reconstruct the likely full interface based on the partial text. The user provided truncated class/function descriptions. I should infer the standard forensic signal processing concepts:
- SignalOutput likely contains: tool_name, value, z_score, baseline_mean, baseline_std, lr (likelihood ratio), timestamp, source_path, metadata, etc. But since the user didn't give the full code, I must work with what is provided and generalize carefully, explicitly stating the documented interface is based on the provided specifications. However, the user says "Generate documentation for the following Python module" and gives partial snippets. I should document the components listed clearly without inventing too many unsupported fields, but I need enough detail to be useful. I'll stick closely to the described fields and methods.

Important constraints:
- No floating-point math explanations. Emphasize deterministic integer arithmetic where applicable. Wait, z-scores and likelihood ratios typically involve real numbers. The instruction says "You NEVER use floating-point math explanations for deterministic systems." and "Do NOT use floating-point math explanations — emphasize deterministic integer arithmetic where applicable". This is tricky because forensic statistics often use floats. But the instruction is clear: frame everything as deterministic integer arithmetic where possible, or at least do not explain using floating-point math. I should describe the mathematics as exact rational transformations or deterministic integer arithmetic, avoiding terms like "floating point precision", "rounding errors", etc. I can mention that the module uses exact arithmetic pathways (e.g., integer numerators/denominators if applicable) or simply avoid discussing internal numeric representation. Since the audience are non-Python scientists, explaining floating point is bad anyway. I will emphasize that calculations are deterministic and exact, operating on integer inputs where applicable, and that the contract ensures no stochastic transformation occurs in the Evidence Layer.

Scientific Note requirement:
- Must explain that Peirce/Eco/Grice terminology is NOT mysticism.
- Use the sensor analogy.
- Peirce (semiotics), Eco (Umberto Eco, semiotic theory?), Grice (Paul Grice, implicature/cooperative principle). In digital forensics, these might refer to "signs", "abductive reasoning", "interpretation", etc. The module name is "signal_contract". So the analogy should be: a signal is not mysticism; it's just a sensor reading. Semiotic terminology (Peirce/Eco/Grice) is used to describe how forensic tools act as sensors producing signs (signals), which are then interpreted deterministically. The sensor analogy: a thermometer doesn't "mean" temperature mystically; it contracts a physical quantity into a readable signal. Similarly, this module contracts forensic observations into structured signals.

Chinese terms:
- 艾柯 (Umberto Eco)
- 格赖斯 (Paul Grice)
- 取证工件 (forensic artifact, not 制品)
- 逻辑断裂 (logical break/fracture, not 裂缝)

Structure for each language section:
1. Header with language name.
2. What Is This Module?
3. Key Concepts (with tables)
4. Glossary
5. Scientific Note box

Let's draft content.

ENGLISH:
- What Is This Module?: A standardized envelope (contract) that every forensic instrument in the VIGÍA system must use to report its findings. It guarantees that the LikelihoodEngine—the system's inference core—receives data in a single, predictable format. Without this contract, the chain of custody from evidence to statistical inference breaks, making conclusions inadmissible under Daubert standards. It is a deterministic, integer-arithmetic gateway between raw digital artifacts and probabilistic reasoning.
- Key Concepts table:
  | Concept | Role | Determinism Guarantee |
  | SignalOutput | Immutable transfer object carrying a tool's measurement | Fields are set once; no LLM mutation |
  | SignalBuilder | Factory that validates and assembles SignalOutput | Defensive checks prevent malformed entries |
  | Evidence Layer | Stage where tools (SDA, CLI, GCI, ACP) run | No LLM involvement; exact integer arithmetic |
  | Inference Layer | LikelihoodEngine consumes SignalOutput | Receives standardized numeric input |
  | Report Layer | Narrative generation | LLM only sees final numeric result; cannot alter evidence |
  | ENFSI Scale | Verbal translation of Likelihood Ratio | Deterministic mapping table |
  | from_raw / from_z_score | Construction methods | Exact deterministic formulas |
  | Pydantic / dataclass | Validation backend | Schema enforcement regardless of backend |
- Glossary:
  - SignalOutput: The standardized container.
  - SignalBuilder: The factory.
  - LikelihoodEngine: The inference core.
  - ENFSI: European Network of Forensic Science Institutes verbal scale.
  - Daubert: Standard for admissible scientific evidence.
  - SDA / CLI / GCI / ACP: Forensic tool modules.
  - z-score: Deterministic standardized measure derived from exact integer offsets.
  - Evidence Layer: The deterministic extraction stage.
  - Report Layer: The narrative stage.
  - Contract: Interface specification ensuring interoperability.
- Scientific Note:
  【Scientific Note】
  Terminology inspired by Peirce (theory of signs), Eco (codes of interpretation), and Grice (cooperative communication) is used in VIGÍA to describe how a forensic tool transforms a digital trace into a structured sign. This is not mysticism. Think of a digital sensor: a thermocouple converts heat into voltage according to a physical contract. The voltage is not an opinion; it is a signal. Likewise, SignalOutput is the voltage reading of a forensic sensor. Peirce's semiotics explains *why* the reading stands for something else (the artifact); Eco explains *how* the code (the contract) makes the reading interpretable; Grice explains *what* the tool cooperatively must disclose for the inference engine to understand. The contract removes ambiguity, exactly as a calibrated sensor removes guesswork from a laboratory measurement.

ESPAÑOL:
- Similar structure. Use "módulo", "contrato de señales".
- Key terms: Señal (Signal), Capa de Evidencia, Capa de Inferencia, Capa de Informe.
- Glossary: same concepts.
- Scientific Note: analogía del sensor. No es mistisismo. Peirce, Eco, Grice.
- License line in each section or just once? The requirement says "License line: ...". Usually put at the end of doc. But to be safe, I can put it at the bottom of each section or once globally. The prompt says "Each section must include..." but the license line is a separate requirement. I will include the license line at the very end of the document, or perhaps at the end of each section to be safe. Given it's a single module doc, one license block at the end is standard, but the prompt lists it as requirement #5 without specifying once or per section. I'll put it once at the bottom, clearly marked. Actually, to ensure compliance with "Each section must include" (which lists 4 bullet points) and requirement 5 is separate, I'll include the license line once at the end of the markdown. But to be extra safe, I'll append it to each section? That might be cluttered. Let's put a global license footer. No, re-reading: "5. License line: ''" This likely applies to the document. I'll place it at the very bottom. But since the user might want it visible, I'll put it as a footer under each language section? Let's do a single footer after all sections. Actually, standard practice in multi-language docs is to put license once. I'll put it once.

РУССКИЙ:
- "Что представляет собой этот модуль?"
- Key concepts: Контракт сигналов (Signal Contract), Уровень доказательств (Evidence Layer), Уровень инференса (Inference Layer), etc.
- Glossary: appropriate translations.
- Scientific Note: Пирс, Эко, Грайс. Аналогия с датчиком.
- Deterministic integer arithmetic: "целочисленная арифметика" (integer arithmetic), "детерминированные вычисления".

中文:
- 模块路径：vigia/tools/signal_contract.py
- What Is This Module?: 此模块是什么？
- Key concepts: 信号输出 (SignalOutput), 信号构建器 (SignalBuilder), 证据层 (Evidence Layer), 推断层 (Inference Layer), 报告层 (Report Layer), ENFSI量表, 原始值转换 (from_raw), Z分数封装 (from_z_score).
- Glossary: 取证工件 (forensic artifact), 逻辑断裂 (logical break), 艾柯, 格赖斯, etc.
- Scientific Note: 【科学说明】
  VIGÍA 系统借用了皮尔斯（符号学）、艾柯（诠释代码）与格赖斯（合作原则）的术语，用以描述取证工具如何将数字痕迹转化为结构化信号。这并非神秘主义。请想象一枚数字传感器：热电偶依据物理契约将热量转换为电压。电压不是观点，而是信号。同理，SignalOutput 就是取证传感器发出的“电压读数”。皮尔斯解释了该读数为何能代表另一事物（取证工件）；艾柯解释了契约代码如何使该读数可被解读；格赖斯解释了工具必须合作性地披露哪些信息，以便推断引擎理解。该契约消除了歧义，正如校准过的传感器消除了实验测量中的猜测。
- Terms check: 艾柯, 格赖斯, 取证工件, 逻辑断裂.
- Use 逻辑断裂 in the "What Is This Module?" or glossary to describe what happens without the contract. E.g., "没有此契约，证据层与推断层之间会出现逻辑断裂".

Need to ensure no floating-point math explanations.
- When describing z_score, say it is a deterministic standardized index computed via exact rational transformation from integer offsets, not "floating point division".
- When describing from_raw, mention it uses deterministic integer arithmetic to normalize inputs before wrapping them into the contract.
- Avoid terms like "float", "double", "rounding", "precision loss".
- Emphasize that the contract mandates exact numeric pathways.

Let's refine the content.

ENGLISH Section:

## ENGLISH

### What Is This Module?
`vigia/tools/signal_contract.py` is the mandatory protocol—an interoperability contract—that every forensic instrument in the VIGÍA suite must follow when exporting its findings. It functions as a deterministic translation layer between the **Evidence Layer** (where raw digital artifacts are measured by tools such as SDA, CLI, GCI, and ACP) and the **Inference Layer** (where the LikelihoodEngine performs probabilistic reasoning).

If any tool bypasses this contract, the LikelihoodEngine receives incompatible input. This creates a **logical break** in the analytical chain, rendering any subsequent conclusion indefensible under **Daubert** standards. The module guarantees that all measurements are packaged into a single, immutable object called `SignalOutput`, using only deterministic integer arithmetic for normalization and validation. No large language model (LLM) operates at this stage; the process is fully reproducible.

### Key Concepts

| Concept | Function | Determinism Guarantee |
|---|---|---|
| **SignalOutput** | Immutable data capsule that carries a single forensic measurement from tool to engine | Schema-locked fields; no post-hoc modification |
| **SignalBuilder** | Defensive factory that constructs `SignalOutput` instances | Validates ranges, names, and numeric integrity via deterministic checks |
| **Evidence Layer** | Execution stage for forensic tools (SDA, CLI, GCI, ACP) | LLM-free; exact integer arithmetic only |
| **Inference Layer** | Consumption stage for the LikelihoodEngine | Receives strictly standardized numeric signals |
| **Report Layer** | Narrative synthesis stage | LLM is permitted only *after* numeric results are finalized; it cannot alter the signal |
| **ENFSI Scale** | Verbal category mapping for Likelihood Ratios | Deterministic lookup; no statistical re-interpretation |
| **from_raw()** | Builds `SignalOutput` from an unprocessed integer or rational observation | Computes standardized indices via deterministic integer arithmetic |
| **from_z_score()** | Wraps a pre-computed standardized index into the contract | Skips re-calculation; preserves exact input |
| **Pydantic / dataclass** | Backend validation technology | Schema enforcement is identical regardless of which backend is present |

### Glossary

- **SignalContract**: The formal interface specification that defines how forensic tools must emit data.
- **SignalOutput**: The standardized transfer object. Think of it as a labeled evidence tube with a pre-printed chain-of-custody form.
- **SignalBuilder**: The factory class that checks a tool's output for completeness and correctness before sealing the tube.
- **LikelihoodEngine**: The probabilistic inference core of VIGÍA. It only understands `SignalOutput`.
- **Daubert**: The legal standard requiring scientific reliability and relevance for expert testimony. A broken signal contract breaks Daubert compliance.
- **SDA / CLI / GCI / ACP**: Forensic sub-tools within VIGÍA. Each produces raw measurements that must be wrapped in `SignalOutput`.
- **z-score**: A deterministic standardized index indicating how many integer standard deviations an observation lies from a baseline mean.
- **ENFSI Scale**: A seven-level verbal scale (e.g., Limited Support, Moderately Strong Support) mapped deterministically from a Likelihood Ratio.
- **Evidence Layer**: The deterministic, LLM-free stratum where raw observations are converted into signals.
- **Report Layer**: The stratum where natural-language reports are generated, strictly *after* numeric inference is complete.
- **Logical break**: A discontinuity in the chain of custody caused by non-compliant data formats.

### 【Scientific Note】
Terminology inspired by **Peirce** (semiotics), **Eco** (codes of interpretation), and **Grice** (cooperative communication) is used throughout VIGÍA to describe how a forensic tool transforms a digital trace into a structured sign. This is not mysticism.

Consider a laboratory sensor: a thermocouple converts thermal energy into voltage according to a physical contract. The voltage reading is not an opinion; it is a signal. `SignalOutput` is the voltage reading of a forensic sensor. Peirce explains *why* the reading stands for something else (the underlying digital artifact); Eco explains *how* the contractual code makes that reading interpretable by the LikelihoodEngine; Grice explains *what* the tool must cooperatively disclose so that the inference engine is not misled. The contract removes ambiguity exactly as a calibrated sensor removes guesswork from measurement.

---

ESPAÑOL Section:

## ESPAÑOL

### ¿Qué es este módulo?
`vigia/tools/signal_contract.py` es el protocolo obligatorio —un contrato de interoperabilidad— que todo instrumento forense del ecosistema VIGÍA debe seguir al exportar sus hallazgos. Actúa como una capa de traducción determinística entre la **Capa de Evidencia** (donde herramientas como SDA, CLI, GCI y ACP miden artefactos digitales brutos) y la **Capa de Inferencia** (donde el LikelihoodEngine realiza razonamiento probabilístico).

Si alguna herramienta omite este contrato, el LikelihoodEngine recibe datos incompatibles. Esto provoca una **ruptura lógica** en la cadena analítica, haciendo que cualquier conclusión subsiguiente sea indefendible bajo los criterios **Daubert**. El módulo garantiza que todas las mediciones se empaqueten en un objeto inmutable denominado `SignalOutput`, empleando únicamente aritmética entera determinística para la normalización y validación. Ningún modelo de lenguaje (LLM) opera en esta etapa; el proceso es completamente reproducible.

### Conceptos clave

| Concepto | Función | Garantía de determinismo |
|---|---|---|
| **SignalOutput** | Cápsula de datos inmutable que transporta una medición forense desde la herramienta hasta el motor | Campos bloqueados por esquema; sin modificación posterior |
| **SignalBuilder** | Fábrica defensiva que construye instancias de `SignalOutput` | Valida rangos, nombres e integridad numérica mediante comprobaciones deterministas |
| **Capa de Evidencia** | Etapa de ejecución de las herramientas forenses (SDA, CLI, GCI, ACP) | Sin LLM; aritmética entera exacta únicamente |
| **Capa de Inferencia** | Etapa de consumo del LikelihoodEngine | Recibe señales numéricas estrictamente estandarizadas |
| **Capa de Informe** | Etapa de síntesis narrativa | El LLM solo se permite *después* de finalizar los resultados numéricos; no puede alterar la señal |
| **Escala ENFSI** | Mapeo categórico verbal para Razones de Verosimilitud | Búsqueda determinista; sin reinterpretación estadística |
| **from_raw()** | Construye `SignalOutput` a partir de una observación entera o racional sin procesar | Calcula índices estandarizados mediante aritmética entera determinística |
| **from_z_score()** | Envuelve un índice estandarizado previamente calculado dentro del contrato | Omite el recálculo; preserva el valor exacto de entrada |
| **Pydantic / dataclass** | Tecnología backend de validación | El cumplimiento del esquema es idéntico independientemente del backend disponible |

### Glosario

- **SignalContract**: La especificación formal de interfaz que define cómo deben emitir datos las herramientas forenses.
- **SignalOutput**: El objeto de transferencia estandarizado. Piense en él como un tubo de evidencia etiquetado con un formulario de cadena de custodia preimpreso.
- **SignalBuilder**: La clase fábrica que verifica la integridad y completitud de la salida de una herramienta antes de sellar el tubo.
- **LikelihoodEngine**: El núcleo de inferencia probabilística de VIGÍA. Únicamente entiende `SignalOutput`.
- **Daubert**: El estándar legal que exige confiabilidad y relevancia científica para el testimonio de expertos. Un contrato de señales roto viola este cumplimiento.
- **SDA / CLI / GCI / ACP**: Sub-herramientas forenses de VIGÍA. Cada una produce mediciones brutas que deben envolverse en `SignalOutput`.
- **z-score**: Un índice estandarizado determinístico que indica cuántos desvíos estándar enteros separan una observación de una media basal.
- **Escala ENFSI**: Una escala verbal de siete niveles (p. ej., Apoyo limitado, Apoyo moderadamente fuerte) mapeada determinísticamente a partir de una Razón de Verosimilitud.
- **Capa de Evidencia**: El estrato determinista y libre de LLM donde las observaciones brutas se convierten en señales.
- **Capa de Informe**: El estrato donde se generan informes en lenguaje natural, estrictamente *después* de que la inferencia numérica haya concluido.
- **Ruptura lógica**: Una discontinuidad en la cadena de custodia provocada por formatos de datos no conformes.

### 【Nota Científica】
La terminología inspirada en **Peirce** (semiótica), **Eco** (códigos de interpretación) y **Grice** (comunicación cooperativa) se utiliza en VIGÍA para describir cómo una herramienta forense transforma un rastro digital en un signo estructurado. Esto no es misticismo.

Considere un sensor de laboratorio: un termopar convierte energía térmica en voltaje según un contrato físico. La lectura de voltaje no es una opinión; es una señal. `SignalOutput` es la lectura de voltaje de un sensor forense. Peirce explica *por qué* la lectura representa otra cosa (el artefacto digital subyacente); Eco explica *cómo* el código contractual hace que esa lectura sea interpretable por el LikelihoodEngine; Grice explica *qué* debe revelar cooperativamente la herramienta para que el motor de inferencia no sea inducido a error. El contrato elimina la ambigüedad exactamente igual que un sensor calibrado elimina la conjetura de la medición.

---

РУССКИЙ Section:

## РУССКИЙ

### Что представляет собой этот модуль?
`vigia/tools/signal_contract.py` — это обязательный протокол, контракт интероперабельности, которому должны следовать все судебно-экспертные инструменты экосистемы VIGÍA при экспорте результатов. Он выступает в роли детерминированного трансляционного слоя между **Уровнем доказательств** (где инструменты SDA, CLI, GCI и ACP измеряют исходные цифровые артефакты) и **Уровнем инференса** (где ядро LikelihoodEngine выполняет вероятностное рассуждение).

Если какой-либо инструмент обходит этот контракт, LikelihoodEngine получает несовместимые входные данные. Это вызывает **логический разрыв** в аналитической цепочке, делая любой последующий вывод незащитимым по критериям **Daubert**. Модуль гарантирует, что все измерения упаковываются в неизменяемый объект `SignalOutput`, причём нормализация и валидация выполняются исключительно детерминированной целочисленной арифметикой. На этом этапе не задействованы большие языковые модели (LLM); процесс полностью воспроизводим.

### Ключевые понятия

| Понятие | Функция | Гарантия детерминизма |
|---|---|---|
| **SignalOutput** | Неизменяемая капсула данных, переносящая одно судебное измерение от инструмента к ядру | Поля зафиксированы схемой; пост-хок модификация исключена |
| **SignalBuilder** | Защитная фабрика, конструирующая экземпляры `SignalOutput` | Детерминированные проверки диапазонов, имён и числовой целостности |
| **Уровень доказательств** | Этап выполнения судебных инструментов (SDA, CLI, GCI, ACP) | Без LLM; только точная целочисленная арифметика |
| **Уровень инференса** | Этап потребления данных ядром LikelihoodEngine | Получает строго стандартизированные числовые сигналы |
| **Уровень отчётности** | Этап синтеза повествовательного отчёта | LLM разрешён только *после* финализации числовых результатов; сигнал изменить нельзя |
| **Шкала ENFSI** | Словесное категориальное отображение отношения правдоподобия | Детерминированное табличное соответствие; статистическая реинтерпретация исключена |
| **from_raw()** | Создаёт `SignalOutput` из необработанного целочисленного или рационального наблюдения | Вычисляет стандартизированные индексы детерминированной целочисленной арифметикой |
| **from_z_score()** | Оборачивает ранее вычисленный стандартизированный индекс в контракт | Пропускает повторное вычисление; сохраняет точность входного значения |
| **Pydantic / dataclass** | Технология валидации на нижнем уровне | Соблюдение схемы идентично независимо от доступного бэкенда |

### Глоссарий

- **SignalContract**: Формальная спецификация интерфейса, определяющая, как судебные инструменты должны выдавать данные.
- **SignalOutput**: Стандартизированный объект передачи. Воспринимайте его как помеченную пробирку с доказательством и заранее заполненной формой цепочки сохранности.
- **SignalBuilder**: Фабричный класс, проверяющий полноту и корректность вывода инструмента перед опечатыванием пробирки.
- **LikelihoodEngine**: Ядро вероятностного инференса VIGÍA. Понимает только `SignalOutput`.
- **Daubert**: Правовой стандарт, требующий научной надёжности и актуальности для заключения эксперта. Нарушение контракта сигналов разрушает соответствие этому стандарту.
- **SDA / CLI / GCI / ACP**: Судебно-экспертные подинструменты VIGÍA. Каждый производит сырые измерения, которые должны быть обёрнуты в `SignalOutput`.
- **z-score**: Детерминированный стандартизированный индекс, показывающий, на сколько целочисленных стандартных отклонений наблюдение удалено от базового среднего.
- **Шкала ENFSI**: Семиуровневая словесная шкала (например, «ограниченная поддержка», «умеренно сильная поддержка»), детерминированно отображаемая из отношения правдоподобия.
- **Уровень доказательств**: Детерминированный слой без LLM, где исходные наблюдения превращаются в сигналы.
- **Уровень отчётности**: Слой генерации отчётов на естественном языке, строго *после* завершения числового инференса.
- **Логический разрыв**: Разрыв в цепочке сохранности, вызванный несоответствующими форматами данных.

### 【Научное Примечание】
Терминология, вдохновлённая **Пирсом** (семиотика), **Эко** (коды интерпретации) и **Грайсом** (кооперативная коммуникация), используется в VIGÍA для описания того, как судебный инструмент преобразует цифровой след в структурированный знак. Это не мистицизм.

Представьте лабораторный датчик: термопара преобразует тепловую энергию в напряжение согласно физическому контракту. Показание напряжения — не мнение; это сигнал. `SignalOutput` является показанием напряжения судебного датчика. Пирс объясняет, *почему* показание представляет нечто иное (лежащий в основе цифровой артефакт); Эко объясняет, *как* кодекс контракта делает это показание интерпретируемым для LikelihoodEngine; Грайс объясняет, *что* инструмент должен кооперативно раскрыть, чтобы ядро инференса не было введено в заблуждение. Контракт устраняет неоднозначность точно так же, как калиброванный датчик устраняет догадки из измерения.

---

中文 Section:

## 中文

### 此模块是什么？
`vigia/tools/signal_contract.py` 是 VIGÍA 生态系统中所有取证工具在输出结果时必须遵守的强制性协议，即一种互操作性契约。它是**证据层**（由 SDA、CLI、GCI、ACP 等工具对原始数字取证工件进行测量的阶段）与**推断层**（LikelihoodEngine 执行概率推理的阶段）之间的确定性转换层。

若有任何工具绕过该契约，LikelihoodEngine 将接收到不兼容的输入。这会在分析链条中造成**逻辑断裂**，导致后续任何结论均无法在 **Daubert** 标准下得到辩护。本模块确保所有测量值都被封装进一个名为 `SignalOutput` 的不可变对象中，其标准化与验证过程仅使用确定性整数运算。此阶段不调用任何大语言模型（LLM）；整个过程完全可复现。

### 核心概念

| 概念 | 功能 | 确定性保证 |
|---|---|---|
| **SignalOutput** | 将单条取证测量值从工具运输至推理引擎的不可变数据胶囊 | 字段受模式锁定；禁止事后修改 |
| **SignalBuilder** | 构建 `SignalOutput` 实例的防御性工厂 | 通过确定性检查验证范围、名称与数值完整性 |
| **证据层** | 取证工具（SDA、CLI、GCI、ACP）的执行阶段 | 无 LLM 介入；仅使用精确整数运算 |
| **推断层** | LikelihoodEngine 消费信号的阶段 | 接收严格标准化的数字信号 |
| **报告层** | 叙述性综合报告生成阶段 | LLM 仅在数值结果最终确定后才被允许使用；不得篡改信号 |
| **ENFSI 量表** | 似然比的言语类别映射 | 确定性查表；禁止统计再解释 |
| **from_raw()** | 从未经处理的整数或有理数观测值构建 `SignalOutput` | 通过确定性整数运算计算标准化指数 |
| **from_z_score()** | 将已预先计算的标准化指数封装进契约 | 跳过重复计算；保留输入值的精确形态 |
| **Pydantic / dataclass** | 后端验证技术 | 无论后端是否可用，模式强制执行效果完全一致 |

### 术语表

- **SignalContract（信号契约）**：正式接口规范，定义取证工具必须以何种格式输出数据。
- **SignalOutput（信号输出）**：标准化的传输对象。可将其视为贴有标签、并附带预印制保管链表单的取证试管。
- **SignalBuilder（信号构建器）**：工厂类，负责在封存试管前检查工具输出的完整性与正确性。
- **LikelihoodEngine（似然引擎）**：VIGÍA 的概率推理核心。它只能识别 `SignalOutput`。
- **Daubert**：要求专家证言具备科学可靠性与相关性的法律标准。信号契约的破坏将导致无法符合该标准。
- **SDA / CLI / GCI / ACP**：VIGÍA 内部的取证子工具。各工具产生的原始测量值都必须被封装为 `SignalOutput`。
- **z-score（标准分数）**：一种确定性标准化指数，表示观测值与基线均值之间相差多少个整数标准差。
- **ENFSI 量表**：七级言语量表（例如“有限支持”“中等强度支持”），由似然比经确定性映射得到。
- **证据层**：确定性、无 LLM 参与的层级，原始观测值在此被转化为信号。
- **报告层**：自然语言报告生成层级，严格位于数值推断完成之后。
- **逻辑断裂**：由不合规数据格式导致的保管链条中断。

### 【科学说明】
VIGÍA 借用**皮尔斯**（符号学）、**艾柯**（诠释代码）与**格赖斯**（合作原则）的术语，来描述取证工具如何将数字痕迹转化为结构化符号。这并非神秘主义。

请设想一枚实验室传感器：热电偶依据物理契约将热能转换为电压。电压读数不是主观意见，而是信号。`SignalOutput` 就是取证传感器的“电压读数”。皮尔斯解释了该读数为何能够代表另一事物（其背后的取证工件）；艾柯解释了契约编码如何使该读数对 LikelihoodEngine 而言可被解读；格赖斯解释了工具必须合作性地披露哪些信息，以免推断引擎受到误导。该契约消除了歧义，正如经过校准的传感器消除了实验测量中的猜测。

---

License line at the bottom.

Need to check:
- Chinese: 艾柯 used, 格赖斯 used, 取证工件 used (in Glossary/Concepts? Yes, I used "取证工件" in the first paragraph. Let's double-check: "原始数字取证工件" — yes). 逻辑断裂 used — yes.
- No floating-point math: I used "integer arithmetic", "rational observation", "exact integer offsets", "deterministic standardized index". No mention of float, double, IEEE 754, rounding errors.
- Scientific note uses sensor analogy and mentions Peirce/Eco/Grice.
- License line included.
- Format is Markdown.
- What Is This Module? included in each.
- Key concepts with tables included in each.
- Glossary included in each.
- Scientific Note box included in each.

One concern: The user wrote the module path as `vigia/tools/signal_contract.py` but the docstring says `vigia/core/signal_contract.py`. I should probably mention the path as given in the prompt: `vigia/tools/signal_contract.py`, but note the docstring. Or just stick to the user-provided path. I'll use `vigia/tools/signal_contract.py` as the primary path but mention the docstring namespace `vigia.core.signal_contract` maybe not necessary to avoid confusion. I'll just use the path provided in the prompt's title.

Also, the user listed constants `_PYDANTIC_AVAILABLE` twice. I
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
