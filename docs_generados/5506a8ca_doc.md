<!--
VIGIA Academic Documentation
Module: 5506a8ca
Batch ID: vigia-doc-0099-5506a8ca
Generated: 2026-05-20T14:56:47.866047+00:00
-->

The user wants documentation for a Python module `vigia/inference/case_pattern_library.py` (docstring says `vigia/engine/case_pattern_library.py`, but the path given is `vigia/inference/case_pattern_library.py`). I need to generate academic technical documentation in Markdown format with 4 language sections: ENGLISH, ESPAÑOL, РУССКИЙ, 中文.

Target audience: scientists and researchers who do NOT know Python. So I must avoid Python jargon, explain everything in plain language, but maintain scientific rigor.

Requirements:
1. 4 language sections.
2. Each section must include:
   - "What Is This Module?" (plain language explanation)
   - Key concepts with tables
   - A glossary of technical terms
   - A 【科学说明】/【Scientific Note】 box explaining that Peirce/Eco/Grice terminology is NOT mysticism — use the sensor analogy
3. Chinese translations must use: 艾柯 (not Eco), 格赖斯 (not Grice), 取证工件 (not 制品), 逻辑断裂 (not 裂缝).
4. 
5. Do NOT use floating-point math explanations — emphasize deterministic integer arithmetic where applicable. Never use floating-point math explanations for deterministic systems.
6. Module path: vigia/inference/case_pattern_library.py
7. Module docstring: vigia/engine/case_pattern_library.py (I should probably mention this discrepancy or just use the path given? The user says MODULE PATH: vigia/inference/case_pattern_library.py and MODULE DOCSTRING: vigia/engine/case_pattern_library.py. I'll note the canonical path and the docstring origin.)
8. Content based on the provided description:
   - Biblioteca de patrones de casos forenses conocidos. Permite detectar campañas de ataque comparando contra patrones históricos.
   - FIX P0: Validación de denominador > 0 en TODAS las operaciones de Fraction.
   - FIX P0: Todo valor numérico en evidence dict usa Fraction/str. NUNCA float.
   - Classes: CasePattern, PatternMatchResult, CasePatternResult, CasePatternLibrary.
   - Built-in patterns: APT29 (Cozy Bear): spear-phishing + PowerShell + credent (seems truncated, probably credential theft).
   - Functions: to_signal(), match(): Matchea señales actuales contra patrones de la biblioteca.
   - Constants & Config: TOOL_NAME, ARTIFACT_RELIABILITY.

I need to be thorough but concise. Since the audience doesn't know Python, I should explain the module as a scientific instrument or methodology.

Structure for each language section:
- Heading with language name.
- Subheading: What Is This Module?
- Subheading: Key Concepts (with tables)
- Subheading: Glossary
- Subheading: Scientific Note (in the respective language, using the required terminology)

Let's draft the content.

**Core ideas to convey:**
- This is a forensic pattern library. It stores known attack campaign signatures.
- It compares current evidence (signals) against historical patterns.
- Uses exact integer arithmetic (Python's `fractions.Fraction`) to avoid any non-deterministic rounding errors. All numeric evidence is stored as exact ratios (numerator/denominator) or strings. No floats.
- Denominator validation ensures no division by zero.
- The classes represent: a pattern (CasePattern), the result of matching a pattern to evidence (PatternMatchResult), the aggregated result for a case (CasePatternResult), and the library container (CasePatternLibrary).
- `to_signal()` converts raw observations into a structured signal.
- `match()` performs the comparison.
- `TOOL_NAME` identifies the software component.
- `ARTIFACT_RELIABILITY` scores the trustworthiness of forensic artifacts (exact integer values).

**Scientific Note requirement:**
Explain that Peirce/Eco/Grice terminology is NOT mysticism — use the sensor analogy.
- Peirce (abduction/semeiotics), Eco (code/interpretation), Grice (cooperative principle/implicature).
- The analogy: a sensor does not "mystically" know temperature; it registers voltage. Similarly, these terms are formal operators for inference, not mystical concepts. They are interpretative frameworks, like calibration curves for sensors.
- In Chinese: 皮尔斯 (Peirce), 艾柯 (Eco), 格赖斯 (Grice).

Let's draft the English section first.

**ENGLISH**

*What Is This Module?*
This module functions as a digital forensic reference archive. It catalogs historically validated attack campaigns—such as the APT29 intrusion set—and provides a deterministic mechanism to compare newly collected evidence against these catalogs. Think of it as a spectroscopic library: just as a chemist identifies an unknown compound by matching its emission lines against a database of known spectra, this module identifies malicious campaigns by matching sequences of forensic artifacts against stored patterns. Every numerical operation is performed using exact integer ratios (fractions), eliminating measurement noise introduced by approximate decimal representations.

*Key Concepts*

| Term | Role | Analogy |
|---|---|---|
| `CasePattern` | A formal template describing a single known attack campaign. | A reference spectrum of a known chemical element. |
| `PatternMatchResult` | The outcome of comparing one pattern against current evidence. | A correlation score between a sample and a reference spectrum. |
| `CasePatternResult` | The consolidated findings after evaluating all relevant patterns. | A final laboratory report summarizing all comparisons. |
| `CasePatternLibrary` | The curated collection of all stored patterns. | The master spectral database in an analytical laboratory. |
| `to_signal()` | Converts raw forensic observations into a structured, comparable format. | Transducing a physical voltage into a calibrated digital reading. |
| `match()` | Executes the comparison between current signals and archived patterns. | Running a cross-correlation analysis between sample and library. |
| `TOOL_NAME` | Canonical identifier for this software component. | The model number of an analytical instrument. |
| `ARTIFACT_RELIABILITY` | Exact integer score indicating the trustworthiness of a given forensic artifact. | The certified purity grade of a reagent. |
| `Fraction` | Exact rational number (numerator ÷ denominator) using only integer arithmetic. | A precise mass-to-charge ratio, never an approximation. |

*Glossary*
- **APT29 (Cozy Bear)**: A documented cyber-espionage campaign characterized by spear-phishing emails, PowerShell execution, and credential harvesting.
- **Deterministic Integer Arithmetic**: Mathematical operations using whole numbers and exact ratios that always produce the same result, with no rounding or approximation.
- **Evidence Dictionary (`evidence dict`)**: A structured record containing all numerical and categorical data from a forensic examination.
- **Forensic Artifact**: Any digital object—such as a log entry, file hash, or registry key—that serves as evidence in an investigation. (中文: 取证工件)
- **Pattern Matching**: The systematic process of aligning observed data with predefined templates to identify known phenomena.
- **Signal**: In this context, a normalized representation of raw forensic data prepared for analysis.
- **Spear-Phishing**: A targeted fraudulent communication designed to compromise a specific individual or organization.
- **Validation of Denominator**: A safety check ensuring that no mathematical operation attempts division by zero.

*【Scientific Note】*
The inferential terminology associated with Peirce, Eco, and Grice—abduction, code, interpretive frames, cooperative maxims, and implicature—is sometimes dismissed as metaphysical or literary. This is a category error. These concepts operate as formal epistemic operators, analogous to the calibration logic of a physical sensor. A thermocouple does not "intuit" temperature through mysticism; it generates a voltage that an engineer interprets through a known transfer function. Likewise, Peircean abduction is the formal operator for hypothesis generation; Eco's codes govern how signs map to meaning under fixed rules; Grice's maxims define boundary conditions for valid inference in communicative exchange. When this module performs pattern matching, it is executing a deterministic semiotic operation—comparing an observed sign (the forensic signal) against a stored interpretive rule (the pattern). There is no ambiguity: the process is as replicable as a spectrometer reading.

---

**ESPAÑOL**

*¿Qué es este módulo?*
Este módulo funciona como un archivo de referencia forense digital. Cataloga campañas de ataque históricamente validadas—como el conjunto de intrusión APT29—y proporciona un mecanismo determinista para comparar evidencia recién recolectada contra estos catálogos. Piense en ello como una biblioteca espectroscópica: así como un químico identifica un compuesto desconocido comparando sus líneas de emisión contra una base de datos de espectros conocidos, este módulo identifica campañas maliciosas comparando secuencias de artefactos forenses contra patrones almacenados. Cada operación numérica se realiza mediante razones enteras exactas (fracciones), eliminando el ruido de medición introducido por las representaciones decimales aproximadas.

*Conceptos Clave*

| Término | Función | Analogía |
|---|---|---|
| `CasePattern` | Plantilla formal que describe una campaña de ataque conocida. | Un espectro de referencia de un elemento químico conocido. |
| `PatternMatchResult` | Resultado de comparar un patrón contra la evidencia actual. | Un coeficiente de correlación entre una muestra y un espectro de referencia. |
| `CasePatternResult` | Hallazgos consolidados tras evaluar todos los patrones relevantes. | Un informe de laboratorio final que resume todas las comparaciones. |
| `CasePatternLibrary` | Colección curada de todos los patrones almacenados. | La base de datos maestra espectral de un laboratorio analítico. |
| `to_signal()` | Convierte observaciones forenses brutas en un formato estructurado y comparable. | La transducción de un voltaje físico en una lectura digital calibrada. |
| `match()` | Ejecuta la comparación entre señales actuales y patrones archivados. | El análisis de correlación cruzada entre muestra y biblioteca. |
| `TOOL_NAME` | Identificador canónico de este componente software. | El número de modelo de un instrumento analítico. |
| `ARTIFACT_RELIABILITY` | Puntuación entera exacta que indica la confiabilidad de un artefacto forense. | El grado de pureza certificada de un reactivo. |
| `Fraction` | Número racional exacto (numerador ÷ denominador) usando solo aritmética entera. | Una relación masa/carga precisa, nunca una aproximación. |

*Glosario*
- **APT29 (Cozy Bear)**: Campaña documentada de ciberespionaje caracterizada por correos de spear-phishing, ejecución de PowerShell y recolección de credenciales.
- **Aritmética Entera Determinista**: Operaciones matemáticas con números enteros y razones exactas que siempre producen el mismo resultado, sin redondeo ni aproximación.
- **Diccionario de Evidencia (`evidence dict`)**: Registro estructurado que contiene todos los datos numéricos y categóricos de un examen forense.
- **Artefacto Forense**: Cualquier objeto digital—como una entrada de registro, un hash de archivo o una clave del registro—que sirve como evidencia en una investigación.
- **Emparejamiento de Patrones**: Proceso sistemático de alinear datos observados con plantillas predefinidas para identificar fenómenos conocidos.
- **Señal**: En este contexto, una representación normalizada de datos forenses brutos preparada para análisis.
- **Spear-Phishing**: Comunicación fraudulenta dirigida diseñada para comprometer a un individuo u organización específicos.
- **Validación del Denominador**: Verificación de seguridad que asegura que ninguna operación matemática intente dividir por cero.

*【Nota Científica】*
La terminología inferencial asociada a Peirce, Eco y Grice—abducción, código, marcos interpretativos, máximas cooperativas e implicatura—es a veces descartada como metafísica o literaria. Este es un error de categoría. Estos conceptos operan como operadores epistémicos formales, análogos a la lógica de calibración de un sensor físico. Un termopar no "intuye" la temperatura mediante misticismo; genera un voltaje que un ingeniero interpreta mediante una función de transferencia conocida. De igual modo, la abducción peirceana es el operador formal para la generación de hipótesis; los códigos de Eco gobiernan cómo los signos se mapean al significado bajo reglas fijas; las máximas de Grice definen condiciones de contorno para la inferencia válida en el intercambio comunicativo. Cuando este módulo realiza el emparejamiento de patrones, está ejecutando una operación semiótica determinista—comparando un signo observado (la señal forense) contra una regla interpretativa almacenada (el patrón). No hay ambigüedad: el proceso es tan replicable como la lectura de un espectrómetro.

---

**РУССКИЙ**

*Что это за модуль?*
Этот модуль функционирует как цифровой судебно-экспертный справочный архив. В нём каталогизированы исторически подтверждённые кампании атак — например, APT29 — и предусмотрен детерминистский механизм сравнения вновь собранных доказательств с этими каталогами. Воспринимайте его как спектроскопическую библиотеку: химик определяет неизвестное соединение, сопоставляя его линии излучения с базой данных известных спектров; аналогично этот модуль идентифицирует вредоносные кампании, сопоставляя последовательности судебных артефактов с хранимыми шаблонами. Каждая числовая операция выполняется с использованием точных целочисленных отношений (дробей), устраняя шум измерений, вносимый приближёнными десятичными представлениями.

*Ключевые понятия*

| Термин | Роль | Аналогия |
|---|---|---|
| `CasePattern` | Формальный шаблон, описывающий одну известную кампанию атаки. | Опорный спектр известного химического элемента. |
| `PatternMatchResult` | Результат сравнения одного шаблона с текущими доказательствами. | Корреляционный коэффициент между образцом и опорным спектром. |
| `CasePatternResult` | Сводные результаты после оценки всех релевантных шаблонов. | Итоговый лабораторный отчёт, обобщающий все сравнения. |
| `CasePatternLibrary` | Курируемая коллекция всех хранимых шаблонов. | Главная спектральная база данных аналитической лаборатории. |
| `to_signal()` | Преобразует необработанные судебные наблюдения в структурированный формат. | Преобразование физического напряжения в калиброванное цифровое показание. |
| `match()` | Выполняет сравнение между текущими сигналами и архивными шаблонами. | Кросс-корреляционный анализ между образцом и библиотекой. |
| `TOOL_NAME` | Канонический идентификатор данного программного компонента. | Модельный номер аналитического прибора. |
| `ARTIFACT_RELIABILITY` | Точное целочисленное значение, указывающее на достоверность судебного артефакта. | Сертифицированная степень чистоты реактива. |
| `Fraction` | Точное рациональное число (числитель ÷ знаменатель) с использованием только целочисленной арифметики. | Точное отношение массы к заряду, а не приближение. |

*Глоссарий*
- **APT29 (Cozy Bear)**: Документированная кампания кибершпионажа, характеризующаяся целевым фишингом (spear-phishing), выполнением PowerShell и хищением учётных данных.
- **Детерминистская целочисленная арифметика**: Математические операции с целыми числами и точными отношениями, всегда дающие один и тот же результат без округления или приближения.
- **Словарь доказательств (`evidence dict`)**: Структурированная запись, содержащая все числовые и категориальные данные судебной экспертизы.
- **Судебный артефакт**: Любой цифровой объект — запись журнала, хэш файла или ключ реестра — служащий доказательством в расследовании.
- **Сопоставление шаблонов**: Систематический процесс выравнивания наблюдаемых данных с предопределёнными шаблонами для идентификации известных явлений.
- **Сигнал**: В данном контексте — нормализованное представление необработанных судебных данных, подготовленное для анализа.
- **Целевой фишинг (Spear-Phishing)**: Нацеленное мошенническое сообщение, предназначенное для компрометации конкретного лица или организации.
- **Валидация знаменателя**: Проверка безопасности, гарантирующая отсутствие попыток деления на ноль.

*【Научное Примечание】*
Инференциальная терминология, связанная с Пирсом, Эко и Грайсом — абдукция, код, интерпретативные рамки, кооперативные максимы и импликатура — иногда отвергается как метафизическая или литературная. Это категориальная ошибка. Эти понятия функционируют как формальные эпистемические операторы, аналогичные логике калибровки физического датчика. Термопара не «интуитивно» ощущает температуру посредством мистицизма; она генерирует напряжение, которое инженер интерпретирует через известную передаточную функцию. Аналогично, пирсова абдукция — это формальный оператор генерации гипотез; коды Эко управляют тем, как знаки отображаются в значение по фиксированным правилам; максимы Грайса определяют граничные условия для корректной инференции в коммуникативном обмене. Когда этот модуль выполняет сопоставление шаблонов, он осуществляет детерминистскую семиотическую операцию — сравнивая наблюдаемый знак (судебный сигнал) с хранимой интерпретативной правилом (шаблоном). Нет никакой двусмысленности: процесс столь же воспроизводим, как показание спектрометра.

---

**中文**

*这是什么模块？*
本模块是一个数字取证参考档案库。它对历史上已验证的攻击活动（例如 APT29 入侵集合）进行编目，并提供一种确定性机制，将新收集的证据与这些编目进行比对。可将其理解为光谱库：正如化学家通过将未知化合物的发射谱线与已知光谱数据库进行匹配来识别该化合物，本模块通过将取证工件序列与存储的模式进行匹配来识别恶意活动。所有数值运算均使用精确整数比（分数）完成，从而消除了近似小数表示所引入的测量噪声。

*核心概念*

| 术语 | 作用 | 类比 |
|---|---|---|
| `CasePattern` | 描述单一已知攻击活动的形式化模板。 | 某种已知化学元素的参考光谱。 |
| `PatternMatchResult` | 将某一模式与当前证据进行比对后的结果。 | 样品与参考光谱之间的相关系数。 |
| `CasePatternResult` | 评估所有相关模式后的综合发现。 | 总结所有比对结果的最终实验室报告。 |
| `CasePatternLibrary` | 所有已存储模式的策展集合。 | 分析实验室的主光谱数据库。 |
| `to_signal()` | 将原始取证观测转换为结构化、可比较的格式。 | 将物理电压转换为经过校准的数字读数。 |
| `match()` | 执行当前信号与归档模式之间的比对。 | 在样品与库之间运行互相关分析。 |
| `TOOL_NAME` | 该软件组件的规范标识符。 | 分析仪器的型号。 |
| `ARTIFACT_RELIABILITY` | 指示特定取证工件可信度的精确整数值。 | 试剂的认证纯度等级。 |
| `Fraction` | 仅使用整数算术的精确有理数（分子 ÷ 分母）。 | 精确的质荷比，绝非近似值。 |

*术语表*
- **APT29 (Cozy Bear)**：一种已记录在案的网络间谍活动，其特征包括鱼叉式网络钓鱼、PowerShell 执行和凭据窃取。
- **确定性整数算术**：使用整数和精确比例进行的数学运算，始终产生相同结果，不存在四舍五入或近似。
- **证据字典（`evidence dict`）**：包含取证检查中所有数值数据和类别数据的结构化记录。
- **取证工件**：任何可作为调查证据的数字对象，如日志条目、文件哈希值或注册表项。
- **模式匹配**：将观测数据与预定义模板进行对齐以识别已知现象的系统化过程。
- **信号**：在本语境中指为分析而准备的原始取证数据的规范化表示。
- **鱼叉式网络钓鱼**：旨在入侵特定个人或组织的定向欺诈性通信。
- **分母验证**：一项安全检查，确保没有任何数学运算尝试除以零。

*【科学说明】*
与皮尔斯、艾柯和格赖斯相关的推理术语——溯因、符码、解释框架、合作准则与含义——有时被斥为玄学或文学概念。这是一种范畴错误。这些概念作为形式化的认识论运算符发挥作用，类似于物理传感器的校准逻辑。热电偶并非通过神秘主义“直觉”温度；它产生电压，工程师通过已知的传递函数对其进行解释。同样，皮尔斯的溯因是假设生成的形式运算符；艾柯的符码规定了符号如何在固定规则下映射到意义；格赖斯的准则定义了交际交换中有效推理的边界条件。当本模块执行模式匹配时，它正在执行一种确定性的符号学操作——将观测到的符号（取证信号）与存储的解释规则（模式）进行比较。其中不存在模糊性：该过程如同光谱仪读数一样可复现。

---

Now, I need to make sure I include the license line exactly as requested in each section or at least once? The user said "License line: ''" I'll put it at the bottom of the document, perhaps under each section or as a global footer. To be safe and thorough, I'll include it at the end of each language section or as a final line in the markdown. Let's put it as a footer at the very bottom of the document, but since it's a 4-language doc, maybe place it after all sections. However, to be safe and ensure it's present, I'll include it as a final line in each section or a dedicated section. The prompt says "Include" — I'll put it at the bottom of the Markdown file once. But to be absolutely compliant with "each section must include", the license isn't explicitly listed in the bullet points of what each section must include, but the prompt says "License line: ..." as a global requirement. I'll add it as a document footer. Actually, to be safest, I'll append it to each language section. But that might be redundant. Let's do a single footer at the end. Wait, requirement 5 is a global requirement. I'll add it at the bottom. But the user said "Generate the complete academic document now." I'll make it a single markdown file with the 4 sections and the license line at the bottom. Or I can put it under a header "License / Licencia / Лицензия / 许可证". That seems professional.

Let's check Chinese translation requirements again:
- 艾柯 (not Eco) -> used.
- 格赖斯 (not Grice) -> used.
- 取证工件 (not 制品) -> used.
- 逻辑断裂 (not 裂缝) -> I didn't use "逻辑断裂". Good, I don't need to use it unless relevant. Wait, the user says "Chinese translations must use: ... 逻辑断裂 (not 裂缝)". This implies if I translate "crack/fracture/logical gap" I should use 逻辑断裂. I didn't use any word for crack/fracture, so I'm fine. But let me double-check if any term I used might imply it. "裂缝" means crack. I didn't use it. So okay.

Also, the user said: "FIX P0: Validación de denominador > 0 en TODAS las operaciones de Fraction. FIX P0: Todo valor numérico en evidence dict usa Fraction/str. NUNCA float." I need to make sure the documentation mentions these constraints clearly under deterministic integer arithmetic.

Let's review the module path and docstring discrepancy. I should mention it.
"The canonical module path is `vigia/inference/case_pattern_library.py`. Its internal docstring references the historical path `vigia/engine/case_pattern_library.py`." I'll add a note about this.

Let's refine the tables to be more precise about the classes/functions.

For the English table:
| Concept | Scientific Description | Practical Analogy |
|---|---|---|
| CasePattern | A formalized profile of a known adversary campaign, defining required and optional forensic indicators. | A reference fingerprint card in a criminal database. |
| PatternMatchResult | The quantitative and qualitative output of comparing live evidence against a single CasePattern. | The similarity score generated by a mass spectrometer comparing an unknown sample to a library compound. |
| CasePatternResult | An aggregated forensic conclusion that synthesizes all individual PatternMatchResult objects for a given investigation. | A peer-reviewed lab report integrating multiple instrument readings into a single finding. |
| CasePatternLibrary | The persistent repository containing all validated CasePattern definitions, including built-in profiles such as APT29. | A certified reference material (CRM) library used for calibration and identification. |
| to_signal() | A transduction function that converts raw, heterogeneous forensic observations into a normalized evidentiary signal. | The analog-to-digital converter (ADC) in a sensor that standardizes voltage into discrete integer values. |
| match() | The deterministic algorithm that evaluates congruence between an incoming signal and archived patterns using exact rational arithmetic. | A chi-squared test or cross-correlation function executed with integer precision. |
| TOOL_NAME | A constant string identifying the software component's provenance and version lineage. | The serial number engraved on a laboratory analytical balance. |
| ARTIFACT_RELIABILITY | An exact integer scalar denoting the epistemic weight or trust level assigned to a specific forensic artifact. | The certified concentration tolerance of a standard solution (e.g., 99.999 %). |
| Fraction (Rational) | A numeric type representing exact ratios of two integers, with mandatory denominator validation (denominator > 0). | A calibrated mass ratio measured on a gravimetric balance, never a floating-point estimate. |

This looks good. I should ensure I don't use "float" or "floating-point" except to say it's excluded. The prompt says "Do NOT use floating-point math explanations — emphasize deterministic integer arithmetic where applicable". I will mention that floats are explicitly prohibited.

Let's refine the scientific note to explicitly mention Peirce, Eco, Grice in all languages and the sensor analogy.

English note:
"Peirce's abduction, Eco's codes, and Grice's maxims... sensor analogy..."

Español note:
"La abducción de Peirce, los códigos de Eco y las máximas de Grice..."

Русский note:
"Абдукция Пирса, коды Эко и максимы Грайса..."

中文 note:
"皮尔斯的溯因、艾柯的符码与格赖斯的准则..."

I need to ensure the document is "thorough but concise". I'll keep descriptions tight.

Let's assemble the final Markdown.

Structure:
```markdown
# Case Pattern Library — Academic Technical Documentation
**Canonical Path:** `vigia/inference/case_pattern_library.py`  
**Internal Docstring Origin:** `vigia/engine/case_pattern_library.py`

---

## ENGLISH

### What Is This Module?
...

### Key Concepts
| ... | ... | ... |

### Glossary
...

### 【Scientific Note】
...

---

## ESPAÑOL
...

---

## РУССКИЙ
...

---

## 中文
...

---


```

Wait, the user said "Each section must include ... A 【科学说明】/【Scientific Note】 box". I should ensure the scientific note is formatted distinctly, perhaps as a blockquote or a bordered section. In Markdown, a blockquote with bold header works.

Also, the user specified "中文 translations must use: 艾柯 (not Eco), 格赖斯 (not Grice), 取证工件 (not 制品), 逻辑断裂 (not 裂缝)". I need to ensure 取证工件 is used in the Chinese glossary. I used it. Good.

One more check: "Do NOT use floating-point math explanations for deterministic systems." and "emphasize deterministic integer arithmetic where applicable". I should make sure I don't explain fractions as "floating point alternatives" but rather as exact integer ratios. The wording "never a floating-point estimate" is acceptable as a negative prohibition, not an explanation of floating-point math. But to be ultra-safe, I should just say "exact integer ratio, never an approximate decimal". I'll avoid the phrase "floating-point" entirely if possible, except maybe to say "no floating-point arithmetic is used". The prompt says "Do NOT use floating-point math explanations". So I won't explain how floats work. I'll just say we use exact integer fractions.

Let's double-check the denominator validation. The prompt mentions "FIX P0: Validación de denominador > 0 en TODAS las operaciones de Fraction." I need to include this in the documentation. I'll add it to the table and glossary.

Let's refine the content one more time.

**ENGLISH**

*What Is This Module?*
This module is a deterministic forensic knowledge base. It catalogs historically confirmed attack campaigns—notably APT29 (Cozy Bear)—and compares newly acquired evidence against these archived profiles. The system operates exclusively with exact integer arithmetic: every numeric value in an evidence record is stored as a precise ratio of two integers (a Fraction) or as a string. No approximate decimal representations are permitted. A mandatory validation rule ensures that every mathematical denominator is strictly greater than zero, preventing undefined operations.

*Key Concepts*

| Concept | Scientific Description | Practical Analogy |
|---|---|---|
| `CasePattern` | Formalized profile of a known attack campaign, specifying required and optional forensic indicators. | A reference fingerprint card in a criminal database. |
| `PatternMatchResult` | Quantitative and qualitative output from comparing live evidence against one `CasePattern`. | A similarity score from a mass spectrometer matching an unknown to a library compound. |
| `CasePatternResult` | Aggregated forensic conclusion synthesizing all individual `PatternMatchResult` objects for an investigation. | A peer-reviewed lab report integrating multiple instrument readings. |
| `CasePatternLibrary` | Persistent repository of all validated `CasePattern` definitions, including built-in profiles. | A certified reference material (CRM) library for calibration and identification. |
| `to_signal()` | Transduction function converting raw, heterogeneous forensic observations into a normalized signal. | An analog-to-digital converter that standardizes physical readings into discrete integer values. |
| `match()` | Deterministic algorithm evaluating congruence between an incoming signal and archived patterns. | A cross-correlation function executed with exact integer precision. |
| `TOOL_NAME` | Constant string identifying the software component’s provenance. | The serial number on an analytical balance. |
| `ARTIFACT_RELIABILITY` | Exact integer scalar denoting the epistemic weight of a forensic artifact. | The certified purity grade of a analytical reagent. |
| `Fraction` | Exact rational number (numerator ÷ denominator) using pure integer arithmetic; denominator > 0 enforced. | A precise mass-to-charge ratio determined by gravimetric analysis. |

*Glossary*
- **APT29 (Cozy Bear)**: Documented cyber-espionage campaign characterized by spear-phishing, PowerShell execution, and credential theft.
- **Case Pattern**: A structured template representing a known modus operandi in digital forensics.
- **Deterministic Integer Arithmetic**: Mathematical operations using whole numbers and exact ratios that yield identical results on every execution, free from rounding or approximation.
- **Evidence Dictionary**: Structured record holding all numerical and categorical findings from a forensic examination; numeric entries are Fractions or strings only.
- **Forensic Artifact**: Any digital object—log entry, file hash, registry key—serving as evidentiary material. (中文: 取证工件)
- **Match**: The systematic alignment of an observed signal against a stored pattern to detect known phenomena.
- **Signal**: Normalized, structured representation of raw forensic data, ready for deterministic comparison.
- **Spear-Phishing**: Targeted deceptive communication aimed at compromising a specific individual or organization.
- **Denominator Validation**: Safety rule guaranteeing that every Fraction operation has a denominator strictly greater than zero.

*【Scientific Note】*
The inferential terminology of **Peirce**, **Eco**, and **Grice**—encompassing abduction, code, interpretive frames, cooperative maxims, and implicature—is sometimes mistaken for literary mysticism. This is a category error. These are formal epistemic operators, functionally equivalent to the calibration logic of a physical sensor. A thermocouple does not intuit temperature through magic; it produces a voltage that an engineer maps to degrees via a known transfer function. Likewise, Peircean abduction is the formal operator for hypothesis generation; Eco’s codes define deterministic mappings from sign to meaning; Grice’s maxims establish boundary conditions for valid inference in communicative systems. When this module performs pattern matching, it executes a deterministic semiotic operation: an observed forensic sign is compared against a stored interpretive rule (the pattern). The process is as replicable and unambiguous as a spectrometer reading.

---

**ESPAÑOL**

*¿Qué es este módulo?*
Este módulo es una base de conocimiento forense determinista. Cataloga campañas de ataque confirmadas históricamente—notablemente APT29 (Cozy Bear)—y compara evidencia recién adquirida contra estos perfiles archivados. El sistema opera exclusivamente con aritmética entera exacta: cada valor numérico en un registro de evidencia se almacena como una proporción precisa de dos enteros (una fracción) o como una cadena de texto. No se permiten representaciones decimales aproximadas. Una regla de validación obligatoria garantiza que todo denominador matemático sea estrictamente mayor que cero, evitando operaciones indefinidas.

*Conceptos Clave*

| Concepto | Descripción Científica | Analogía Práctica |
|---|---|---|
| `CasePattern` | Perfil formalizado de una campaña de ataque conocida, espec
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
