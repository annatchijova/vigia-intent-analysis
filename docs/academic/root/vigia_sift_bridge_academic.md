<!--
VIGIA Academic Documentation
Module: ff8f60eb
Batch ID: vigia-doc-0189-ff8f60eb
Generated: 2026-05-20T14:56:47.885419+00:00
-->

ENGLISH:
- What Is This Module?: VIGÍA is an intentionality analysis bridge for the SIFT digital forensics workstation. It does not reconstruct files; it reconstructs purpose. It treats digital evidence as a semiotic system (signs, symbols, and communication acts) and applies abductive reasoning (Peirce), cooperative principle analysis (Grice), and overinterpretation detection (Eco) to determine why an action was performed, not merely what occurred. It also includes protective guardrails (LLMShield, integrity checks) to prevent automated analysis from being manipulated by injected instructions. All safety boundaries are enforced via exact integer arithmetic—there are no statistical approximations or floating-point thresholds.
- Key Concepts Table:
  - Intentionality Analysis: Inferring the purpose (WHY) behind a digital trace.
  - SIFT Workstation: A standardized digital forensics environment.
  - Abductive Reasoning (Peirce): Inference to the best explanation; hypothesis generation from signs.
  - Cooperative Principle (Grice): Expectation that communication is rational and cooperative; violations indicate deception or manipulation (Dale Carnegie patterns).
  - Overinterpretation / Red Herring (Eco): Distinguishing meaningful evidence from deliberately planted noise.
  - Deterministic Integer Guards: Exact byte/text/pattern limits (MAX_TEXT_LENGTH, etc.) preventing resource exhaustion without floating-point calculation.
  - Integrity Violation: A detected logical fracture in evidence reading (not a physical crack).
  - Prompt Injection: Malicious text designed to hijack an automated analysis engine.
  - Honey Tokens & Purgatory: Deceptive bait files and quarantine directories for suspicious artifacts.

- Glossary:
  - Semiotics: Study of signs and symbols.
  - Abduction: Logical inference generating explanatory hypotheses.
  - Facade: A simplified interface shielding complexity.
  - Deterministic Integer Arithmetic: Exact whole-number computation with no rounding errors or probability.
  - Prompt Injection: Adversarial input crafted to alter system behavior.
  - Evidence Artifact: A digital object of forensic interest (取证工件).
  - Logical Fracture: A violation in the expected coherence of data (逻辑断裂).

- Scientific Note:
【Scientific Note】
Terms such as “abductive reasoning,” “cooperative maxims,” and “overinterpretation” are not metaphysical or mystical concepts. They constitute the operational vocabulary of a semiotic sensor. Just as a thermocouple translates temperature into voltage and a spectrometer translates light into wavelength, VIGÍA translates patterns of human communication into detectable logical signals. Peirce’s categories are calibration axes; Eco’s red-herring detection is a noise-filtering algorithm; Grice’s maxims are threshold criteria for cooperative signal integrity. When the module reports a “violation,” it is reporting a sensor reading—an exact integer deviation from an expected deterministic state—not a supernatural judgment.

ESPAÑOL:
- ¿Qué es este módulo?
- Conceptos clave: Análisis de intencionalidad, Razonamiento abductivo (Peirce), Principio cooperativo (Grice), Sobreinterpretación / Pista falsa (Eco), Patrones de influencia (Carnegie), Guardias enteros deterministas, Violación de integridad, Inyección de prompt, Tokens señuelo y Purgatorio.
- Glosario.
- Nota científica: analogía del sensor. Los términos no son misticismo. "Razonamiento abductivo", "máximas cooperativas", "sobreinterpretación" son vocabulario operacional de un sensor semiótico. Como un termopar traduce temperatura en voltaje, VIGÍA traduce patrones de comunicación humana en señales lógicas detectables. Las categorías de Peirce son ejes de calibración; la detección de pistas falsas de Eco es un algoritmo de filtrado de ruido; las máximas de Grice son criterios de umbral para la integridad de la señal cooperativa. Cuando el módulo reporta una "violación", reporta una lectura de sensor—una desviación entera exacta de un estado determinista esperado—no un juicio sobrenatural.

РУССКИЙ:
- Что это за модуль?
- Ключевые понятия: Анализ интенциональности, Абдуктивное рассуждение (Пирс), Кооперативный принцип (Грайс), Переинтерпретация / ложный след (Эко), Паттерны влияния (Карнеги), Детерминистские целочисленные ограничители, Нарушение целостности, Инъекция промпта, Медовые токены и Чистилище.
- Глоссарий.
- Научное примечание: Термины не мистика. Это операционный словарь семиотического датчика. Как термопара переводит температуру в напряжение, VIGÍA переводит паттерны человеческой коммуникации в обнаружимые логические сигналы. Категории Пирса — оси калибровки; обнаружение ложных следов Эко — алгоритм шумоподавления; максимы Грайса — пороговые критерии целостности кооперативного сигнала. «Нарушение» — это показание датчика, точное целочисленное отклонение от ожидаемого детерминистского состояния, а не сверхъестественное суждение.

中文:
- 这是什么模块？
- 关键概念：意向性分析、溯因推理（皮尔斯）、合作原则（格赖斯）、过度诠释/红鲱鱼（艾柯）、影响模式（卡内基）、确定性整数防护、完整性违规、提示注入、蜜罐令牌与隔离区(Purgatory)。
- 术语表：必须使用 取证工件 (not 制品), 逻辑断裂 (not 裂缝).
- 科学说明框：
【科学说明】
“溯因推理”“合作准则”“过度诠释”等术语并非玄学或神秘主义概念。它们是一套符号学传感器的操作词汇。正如热电偶将温度转换为电压、光谱仪将光线转换为波长，VIGÍA 将人类沟通模式转换为可检测的逻辑信号。皮尔斯的范畴是校准轴；艾柯的红鲱鱼检测是一种降噪算法；格赖斯的准则是合作信号完整性的阈值标准。当模块报告“违规”时，它是在报告传感器读数——一个相对于预期确定性状态的精确整数偏差，而非超自然判断。

Now, let's think about the tables. They should be concise but informative.

For the Key Concepts table in English:
| Concept | Description | Forensic Role |
|---|---|---|
| Intentionality Analysis | Inference of purpose (WHY) rather than mere event reconstruction (WHAT). | Reconstructs motive from digital traces. |
| Abductive Reasoning (Peirce) | Hypothesis generation from observed signs. | Generates best-explanation hypotheses for anomalies. |
| Cooperative Principle (Grice) | Assumption that communication is rational and cooperative. | Detects deception when maxims are violated. |
| Overinterpretation / Red Herring (Eco) | Distinguishing meaningful signals from planted noise. | Filters intentional distraction artifacts. |
| Influence Patterns (Carnegie) | Recognized structures of persuasion and manipulation. | Maps psychological pressure in evidence. |
| Deterministic Integer Guards | Exact whole-number limits on text length, byte count, pattern size. | Prevents resource exhaustion without floating-point error. |
| Integrity Violation (_IntegrityViolation) | Specialized exception for read-integrity logical fractures. | Signals evidence corruption or tampering. |
| LLMShield | Protective facade scanning for prompt injection. | Prevents adversarial hijacking of analysis. |
| Honey Tokens & Purgatory | Bait files and quarantine directories. | Traps intruders and isolates suspicious artifacts. |

Constants table:
| Constant | Deterministic Integer Function |
|---|---|
| MAX_TEXT_LENGTH | Hard upper bound on any single input string. |
| MAX_TEXTS_IN_LIST | Hard count limit for batch processing. |
| MAX_TOTAL_BYTES | Aggregate byte ceiling for memory safety. |
| MAX_PATTERN_LENGTH | Exact limit for regex or signature size. |
| MAX_FILE_PREVIEW | Integer byte window for file header inspection. |
| _CRITICAL_STDLIB_FUNCS | Whitelist/Blacklist of deterministic system calls. |
| _ALLOWED_PATTERN | Constrained template for valid input structure. |
| _EVIDENCE_ENV | Controlled environment variable namespace. |
| _HONEY_TOKEN_DIR | Integer-indexed bait file repository. |
| _PURGATORY_DIR | Quarantine path for unverified artifacts. |

Need to ensure I don't use floating-point. Emphasize "exact", "whole-number", "deterministic integer arithmetic".

For the glossary in Chinese:
- 取证工件: 数字调查中的具体对象，如文件、日志条目或数据包。（不使用“制品”）
- 逻辑断裂: 数据预期连贯性中的确定性偏差或违规，即完整性违规。（不使用“裂缝”）
- 确定性整数运算: 仅使用整数的精确计算，无舍入误差或概率近似。
- 蜜罐令牌: 作为诱饵植入的取证工件，用于检测未授权访问。
- 隔离区 (Purgatory): 用于存放未经核实的可疑取证工件的暂存目录。
- 提示注入: 旨在操纵自动分析引擎的对抗性输入文本。
- 外立面模式 (Facade): 为复杂子系统提供简化统一接口的结构模式。
- 溯因推理: 从观察到的符号生成最佳解释假设的逻辑过程。
- 合作准则: 格赖斯提出的理性沟通预期标准。
- 红鲱鱼: 艾柯所指的、故意植入以误导调查的无关联噪声或诱饵。

Need to be careful: The user said "逻辑断裂 (not 裂缝)". The module has "_IntegrityViolation" which is for integrity violations / logical fractures. So I should use 逻辑断裂 in the glossary for integrity violation / logical fracture.

Also for Chinese: 艾柯 (Eco), 格赖斯 (Grice). Good.

License line at the end: ""

Let's make sure the Russian uses appropriate transliterations:
- Пирс (Peirce)
- Грайс (Grice)
- Эко (Eco)
- Карнеги (Carnegie)

The Spanish:
- Peirce, Grice, Eco, Carnegie are standard.
- "Lógica abductiva" or "Razonamiento abductivo".
- "Principio cooperativo".
- "Sobreinterpretación / Pista falsa".
- "Patrones de influencia".
- "Guardias enteros deterministas".
- "Violación de integridad".
- "Inyección de prompt" or "Inyección de indicaciones".
- "Tokens señuelo" or "Tokens miel".
- "Purgatorio".

The scientific note in Spanish: 【Nota Científica】
In Russian: 【Научное Примечание】
In Chinese: 【科学说明】
In English: 【Scientific Note】

Let's draft the full text carefully.

One concern: The module docstring mentions MIT License, but the user explicitly requires the line: "" I will use that exact line as required.

Also, the user says "Do NOT use floating-point math explanations — emphasize deterministic integer arithmetic where applicable". So when describing constants, I must say they are exact integer limits, not approximate or calculated via division/floats.

Let's write the content.

ENGLISH SECTION:

## ENGLISH

### What Is This Module?

`vigia/vigia_sift_bridge.py`—codenamed **VIGÍA**—is an intentionality-analysis bridge for the SIFT digital-forensics workstation. Unlike conventional tools that answer *what* happened to a file system, VIGÍA answers *why* an actor performed a given action. It treats every digital trace as a communicative sign and applies semiotic reasoning to reconstruct purpose from evidence artifacts.

The module integrates four theoretical frameworks into a deterministic analytical engine:
- **Charles S. Peirce** (abductive reasoning): hypothesis generation from signs.
- **Dale Carnegie** (influence patterns): detection of persuasion and manipulation structures.
- **H. Paul Grice** (cooperative principle): identification of deception via maxim violations.
- **Umberto Eco** (overinterpretation): separation of genuine signals from planted red herrings.

All safety boundaries—text length, byte totals, pattern sizes, list capacities—are enforced through **deterministic integer arithmetic**. The module never relies on statistical approximations, floating-point rounding, or probabilistic thresholds. A limit is an exact whole number; a violation is an exact integer deviation.

### Key Concepts

| Concept | Description | Role in Forensic Analysis |
|---|---|---|
| **Intentionality Analysis** | Inference of motive and purpose (*why*) rather than mere event reconstruction (*what*). | Reconstructs actor purpose from digital traces. |
| **Abductive Reasoning (Peirce)** | Logical inference that generates the best explanatory hypothesis from observed signs. | Produces testable hypotheses for anomalous evidence patterns. |
| **Cooperative Principle (Grice)** | The expectation that rational communication follows quantity, quality, relevance, and manner maxims. | Detects deception when communication violates these deterministic rules. |
| **Influence Patterns (Carnegie)** | Recognized psychological structures of persuasion, manipulation, and social engineering. | Maps coercion or deception embedded in digital communications. |
| **Overinterpretation / Red Herring (Eco)** | Distinguishing meaningful evidence from deliberately planted noise or distraction. | Filters artifactual noise designed to mislead investigators. |
| **Deterministic Integer Guards** | Exact whole-number limits (`MAX_TEXT_LENGTH`, `MAX_TOTAL_BYTES`, etc.) on all inputs. | Guarantees reproducible resource consumption with no floating-point error. |
| **Integrity Violation** | A specialized exception indicating a logical fracture in evidence reading (not a physical crack). | Signals tampering, corruption, or unauthorized modification of evidence. |
| **LLMShield** | A protective facade that scans incoming text for adversarial prompt-injection attempts. | Prevents automated analysis engines from being hijacked by malicious instructions. |
| **Honey Tokens & Purgatory** | Bait files (`_HONEY_TOKEN_DIR`) and quarantine directories (`_PURGATORY_DIR`). | Traps unauthorized access and isolates unverified evidence artifacts. |

| Constant / Config | Deterministic Integer Function |
|---|---|
| `MAX_TEXT_LENGTH` | Exact character ceiling for any single input string. |
| `MAX_TEXTS_IN_LIST` | Hard count limit for items processed in a single batch. |
| `MAX_TOTAL_BYTES` | Aggregate byte ceiling ensuring bounded memory usage. |
| `MAX_PATTERN_LENGTH` | Exact limit on regex or signature length. |
| `MAX_FILE_PREVIEW` | Integer byte window for deterministic file-header inspection. |
| `_CRITICAL_STDLIB_FUNCS` | Controlled enumeration of system functions accessible during analysis. |
| `_ALLOWED_PATTERN` | Rigid template defining valid input structure. |
| `_EVIDENCE_ENV` | Restricted namespace for environment variables handling evidence. |
| `_HONEY_TOKEN_DIR` | Deterministic path to bait-file repository. |
| `_PURGATORY_DIR` | Quarantine path for isolating suspicious or unverified artifacts. |

### Glossary

| Term | Definition |
|---|---|
| **Semiotics** | The scientific study of signs, symbols, and their interpretation within communicative systems. |
| **Abduction** | A logical process that infers the most plausible explanation from a finite set of observations. |
| **Deterministic Integer Arithmetic** | Computation using exact whole numbers only, eliminating rounding errors, probabilistic noise, and floating-point drift. |
| **Evidence Artifact** | Any digital object—file, log entry, packet, or fragment—subject to forensic examination. |
| **Logical Fracture** | A deterministic deviation from expected data coherence; the condition signaled by an integrity violation. |
| **Prompt Injection** | An adversarial input technique whereby malicious text alters the behavior of an automated language-model analysis. |
| **Facade** | A design construct providing a simplified, unified interface to a more complex subsystem. |
| **Honey Token** | A deliberately planted decoy artifact used to detect unauthorized access or data exfiltration. |
| **Purgatory** | A quarantine directory where unverified or suspicious artifacts are held pending deterministic review. |

### 【Scientific Note】

Terms such as “abductive reasoning,” “cooperative maxims,” and “overinterpretation” are not metaphysical or mystical concepts. They constitute the operational vocabulary of a semiotic sensor. Just as a thermocouple translates temperature into voltage and a spectrometer translates light into wavelength, VIGÍA translates patterns of human communication into detectable logical signals. Peirce’s categories are calibration axes; Eco’s red-herring detection is a noise-filtering algorithm; Grice’s maxims are threshold criteria for cooperative signal integrity. When the module reports a “violation,” it is reporting a sensor reading—an exact integer deviation from an expected deterministic state—not a supernatural judgment.

---

ESPAÑOL SECTION:

## ESPAÑOL

### ¿Qué es este módulo?

`vigia/vigia_sift_bridge.py`, denominado **VIGÍA**, es un puente de análisis de intencionalidad para la estación de trabajo forense digital SIFT. A diferencia de las herramientas convencionales que responden *qué* ocurrió en un sistema de archivos, VIGÍA responde *por qué* un actor ejecutó una acción determinada. Trata cada rastro digital como un signo comunicativo y aplica razonamiento semiótico para reconstruir el propósito a partir de artefactos de evidencia.

El módulo integra cuatro marcos teóricos en un motor analítico determinista:
- **Charles S. Peirce** (razonamiento abductivo): generación de hipótesis a partir de signos.
- **Dale Carnegie** (patrones de influencia): detección de estructuras de persuasión y manipulación.
- **H. Paul Grice** (principio cooperativo): identificación de engaño mediante violaciones de máximas.
- **Umberto Eco** (sobreinterpretación): separación de señales genuinas de pistas falsas plantadas.

Todos los límites de seguridad—longitud de texto, total de bytes, tamaño de patrones, capacidad de listas—se imponen mediante **aritmética entera determinista**. El módulo nunca recurre a aproximaciones estadísticas, redondeos de coma flotante ni umbrales probabilísticos. Un límite es un número entero exacto; una violación es una desviación entera exacta.

### Conceptos clave

| Concepto | Descripción | Rol en el análisis forense |
|---|---|---|
| **Análisis de intencionalidad** | Inferencia del motivo y propósito (*por qué*) más allá de la reconstrucción de eventos (*qué*). | Reconstruye la intención del actor a partir de rastros digitales. |
| **Razonamiento abductivo (Peirce)** | Inferencia lógica que genera la hipótesis explicativa más robusta a partir de signos observados. | Produce hipótesis contrastables para patrones anómalos de evidencia. |
| **Principio cooperativo (Grice)** | Expectativa de que la comunicación racional sigue máximas de cantidad, calidad, relevancia y modo. | Detecta engaño cuando la comunicación viola estas reglas deterministas. |
| **Patrones de influencia (Carnegie)** | Estructuras psicológicas reconocidas de persuasión, manipulación e ingeniería social. | Mapea coerción o engaño incrustado en comunicaciones digitales. |
| **Sobreinterpretación / Pista falsa (Eco)** | Distinguir evidencia significativa de ruido o distracciones plantadas deliberadamente. | Filtra ruido artifactual diseñado para desorientar a los investigadores. |
| **Guardias enteros deterministas** | Límites exactos de números enteros (`MAX_TEXT_LENGTH`, `MAX_TOTAL_BYTES`, etc.) en todas las entradas. | Garantiza consumo de recursos reproducible sin error de coma flotante. |
| **Violación de integridad** | Excepción especializada que indica una fractura lógica en la lectura de evidencia (no una griega física). | Señala manipulación, corrupción o modificación no autorizada de la evidencia. |
| **LLMShield** | Fachada protectora que escanea textos entrantes en busca de inyecciones de prompt adversariales. | Previene el secuestro del motor de análisis automatizado por instrucciones maliciosas. |
| **Tokens señuelo y Purgatorio** | Archivos cebo (`_HONEY_TOKEN_DIR`) y directorios de cuarentena (`_PURGATORY_DIR`). | Atrapan accesos no autorizados y aíslan artefactos de evidencia no verificados. |

| Constante / Configuración | Función de entero determinista |
|---|---|
| `MAX_TEXT_LENGTH` | Techo exacto de caracteres para cualquier cadena de entrada individual. |
| `MAX_TEXTS_IN_LIST` | Límite rígido de conteo para elementos procesados en un lote único. |
| `MAX_TOTAL_BYTES` | Techo agregado de bytes que asegura un uso de memoria acotado. |
| `MAX_PATTERN_LENGTH` | Límite exacto para la longitud de expresiones regulares o firmas. |
| `MAX_FILE_PREVIEW` | Ventana de bytes entera para inspección determinista de cabeceras de archivo. |
| `_CRITICAL_STDLIB_FUNCS` | Enumeración controlada de funciones del sistema accesibles durante el análisis. |
| `_ALLOWED_PATTERN` | Plantilla rígida que define la estructura válida de entrada. |
| `_EVIDENCE_ENV` | Espacio de nombres restringido para variables de entorno que gestionan evidencia. |
| `_HONEY_TOKEN_DIR` | Ruta determinista al repositorio de archivos-cebo. |
| `_PURGATORY_DIR` | Ruta de cuarentena para aislar artefactos sospechosos o no verificados. |

### Glosario

| Término | Definición |
|---|---|
| **Semiótica** | Estudio científico de los signos, símbolos y su interpretación dentro de sistemas comunicativos. |
| **Abducción** | Proceso lógico que infiere la explicación más plausible a partir de un conjunto finito de observaciones. |
| **Aritmética entera determinista** | Computación que utiliza únicamente números enteros exactos, eliminando errores de redondeo, ruido probabilístico y deriva de coma flotante. |
| **Artefacto de evidencia** | Cualquier objeto digital—archivo, registro, paquete o fragmento—sujeto a examen forense. |
| **Fractura lógica** | Desviación determinista de la coherencia de datos esperada; la condición señalada por una violación de integridad. |
| **Inyección de prompt** | Técnica de entrada adversarial mediante la cual un texto malicioso altera el comportamiento de un análisis automatizado basado en modelo de lenguaje. |
| **Fachada** | Constructo de diseño que proporciona una interfaz simplificada y unificada a un subsistema más complejo. |
| **Token señuelo** | Artefacto señuelo plantado deliberadamente para detectar accesos no autorizados o exfiltración de datos. |
| **Purgatorio** | Directorio de cuarentena donde se retienen artefactos no verificados o sospechosos a la espera de revisión determinista. |

### 【Nota Científica】

Términos como “razonamiento abductivo”, “máximas cooperativas” y “sobreinterpretación” no son conceptos metafísicos o místicos. Constituyen el vocabulario operacional de un sensor semiótico. Así como un termopar traduce la temperatura en voltaje y un espectrómetro traduce la luz en longitud de onda, VIGÍA traduce patrones de comunicación humana en señales lógicas detectables. Las categorías de Peirce son ejes de calibración; la detección de pistas falsas de Eco es un algoritmo de filtrado de ruido; las máximas de Grice son criterios de umbral para la integridad de la señal cooperativa. Cuando el módulo reporta una “violación”, está reportando una lectura de sensor—una desviación entera exacta de un estado determinista esperado—no un juicio sobrenatural.

---

РУССКИЙ SECTION:

## РУССКИЙ

### Что это за модуль?

`vigia/vigia_sift_bridge.py` под кодовым названием **VIGÍA** — это мост анализа интенциональности для цифровой криминалистической станции SIFT. В отличие от традиционных инструментов, отвечающих на вопрос *что* произошло с файловой системой, VIGÍA отвечает на вопрос *почему* действующее лицо совершило то или иное действие. Каждый цифровой след рассматривается как коммуникативный знак; применяется семиотическое рассуждение для реконструкции цели по криминалистическим артефактам.

Модуль интегрирует четыре теоретические рамки в детерминистский аналитический движок:
- **Чарлз С. Пирс** (абдуктивное рассуждение): генерация гипотез по знакам.
- **Дейл Карнеги** (паттерны влияния): обнаружение структур убеждения и манипуляции.
- **Х. Пол Грайс** (кооперативный принцип): выявление обмана через нарушение максим.
- **Умберто Эко** (переинтерпретация): отделение подлинных сигналов от подброшенных ложных следов.

Все защитные границы — длина текста, суммарное число байтов, размер паттернов, вместимость списков — обеспечиваются **детерминистской целочисленной арифметикой**. Модуль никогда не использует статистические аппроксимации, округление с плавающей запятой или вероятностные пороги. Предел — это точное целое число; нарушение — это точное целочисленное отклонение.

### Ключевые понятия

| Понятие | Описание | Роль в криминалистическом анализе |
|---|---|---|
| **Анализ интенциональности** | Вывод мотива и цели (*почему*), а не просто реконструкция события (*что*). | Реконструирует намерение субъекта по цифровым следам. |
| **Абдуктивное рассуждение (Пирс)** | Логический вывод, генерирующий наилучшую объяснительную гипотезу из наблюдаемых знаков. | Порождает проверяемые гипотезы для аномальных паттернов улик. |
| **Кооперативный принцип (Грайс)** | Ожидание, что рациональное общение следует максимам количества, качества, релевантности и способа. | Обнаруживает обман при нарушении этих детерминистских правил. |
| **Паттерны влияния (Карнеги)** | Признанные психологические структуры убеждения, манипуляции и социальной инженерии. | Картографирует принуждение или обман, встроенный в цифровые коммуникации. |
| **Переинтерпретация / Ложный след (Эко)** | Различение значимой улики и намеренно подброшенного шума или отвлекающего манёвра. | Фильтрует артефактный шум, созданный для введения следователей в заблуждение. |
| **Детерминистские целочисленные ограничители** | Точные пределы целых чисел (`MAX_TEXT_LENGTH`, `MAX_TOTAL_BYTES` и др.) для всех входных данных. | Гарантируют воспроизводимое потребление ресурсов без ошибок плавающей запятой. |
| **Нарушение целостности** | Специализированное исключение, указывающее на логический разрыв при чтении улики (не физическую трещину). | Сигнализирует о подделке, повреждении или несанкционированном изменении улики. |
| **LLMShield** | Защитный фасад, сканирующий входящий текст на предмет состязательных инъекций промпта. | Предотвращает захват автоматизированного аналитического движка вредоносными инструкциями. |
| **Медовые токены и Чистилище** | Приманочные файлы (`_HONEY_TOKEN_DIR`) и карантинные каталоги (`_PURGATORY_DIR`). | Ловят несанкционированный доступ и изолируют неверифицированные криминалистические артефакты. |

| Константа / Конфигурация | Функция детерминистского целого |
|---|---|
| `MAX_TEXT_LENGTH` | Жёсткий потолок символов для любой отдельной входной строки. |
| `MAX_TEXTS_IN_LIST` | Жёсткий лимит количества элементов, обрабатываемых в одной пакетной задаче. |
| `MAX_TOTAL_BYTES` | Совокупный байтовый потолок, гарантирующий ограниченное использование памяти. |
| `MAX_PATTERN_LENGTH` | Точный предел длины регулярного выражения или сигнатуры. |
| `MAX_FILE_PREVIEW` | Целочисленное байтовое окно для детерминистской проверки заголовков файлов. |
| `_CRITICAL_STDLIB_FUNCS` | Контролируемый перечень системных функций, доступных во время анализа. |
| `_ALLOWED_PATTERN` | Жёсткий шаблон, определяющий допустимую структуру входных данных. |
| `_EVIDENCE_ENV` | Ограниченное пространство имён переменных среды, обрабатывающих улики. |
| `_HONEY_TOKEN_DIR` | Детерминистский путь к хранилищу приманочных файлов. |
| `_PURGATORY_DIR` | Карантинный путь для изоляции подозрительных или неверифицированных артефактов. |

### Глоссарий

| Термин | Определение |
|---|---|
| **Семиотика** | Научное изучение знаков, символов и их интерпретации в коммуникативных системах. |
| **Абдукция** | Логический проц
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
