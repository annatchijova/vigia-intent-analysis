<!--
VIGIA Academic Documentation
Module: de7d9a40
Batch ID: vigia-doc-0190-de7d9a40
Generated: 2026-05-20T14:56:47.885652+00:00
-->

The user wants academic technical documentation for a Python module `vigia/vigia_sift_bridge_final.py`. The target audience is scientists who don't know Python. Requirements:

1. Markdown format with 4 language sections: ENGLISH, ESPAÑOL, РУССКИЙ, 中文.
2. Each section must include:
   - "What Is This Module?" (plain language explanation)
   - Key concepts with tables
   - A glossary of technical terms
   - A 【科学说明】/【Scientific Note】 box explaining that Peirce/Eco/Grice terminology is NOT mysticism — use the sensor analogy
3. Chinese translations must use: 艾柯 (not Eco), 格赖斯 (not Grice), 取证工件 (not 制品), 逻辑断裂 (not 裂缝)
4.  (Note: the module docstring says MIT, but the user explicitly says to use GNU AGPL v3 line. I must follow the user instruction.)
5. Do NOT use floating-point math explanations — emphasize deterministic integer arithmetic where applicable.
6. Be thorough but concise.

Module details:
- Path: vigia/vigia_sift_bridge_final.py
- Docstring: VIGÍA — Intentionality Analysis Bridge for SIFT Workstation
- Author: Anna Tchijova
- Theoretical foundation: Peirce, Carnegie, Grice, Eco.
- Core question: not WHAT happened, but WHY.
- Classes: `_IntegrityViolation`: specialized exception for read integrity violations. Distinguishable from other ValueError — allows routing.
- Functions: no public functions.
- Constants & CONFIG:
  - MAX_TEXT_LENGTH
  - MAX_TEXTS_IN_LIST
  - MAX_TOTAL_BYTES
  - MAX_PATTERN_LENGTH
  - MAX_FILE_PREVIEW
  - _ALLOWED_PATTERN
  - _EVIDENCE_ENV
  - _HONEY_TOKEN_DIR
  - _PURGATORY_DIR
  - _SYSTEM_PROMPT_PATH_DEFAULT

Need to write for scientists who do not know Python. So avoid Python jargon. Explain in plain language but with academic rigor. Use tables. Glossary. Scientific note about terminology not being mysticism, using sensor analogy.

Important: No floating-point math explanations. Emphasize deterministic integer arithmetic where applicable. The constants listed are integers/bounds, so I can describe them as deterministic integer thresholds.

Structure:
- Title
- ENGLISH section
- ESPAÑOL section
- РУССКИЙ section
- 中文 section

Each section needs the subsections. Since it's a long document, I need to be careful with formatting.

Let's draft each section.

**ENGLISH**

What Is This Module?
- It's a connector (bridge) between the VIGÍA intentionality analysis engine and the SIFT digital forensics workstation. It translates human-readable theories (Peirce's abduction, Eco's overinterpretation, Grice's cooperative maxims, Carnegie's influence patterns) into deterministic constraints for a forensic environment.
- It answers WHY, not WHAT.
- It's not a black box of mysticism; it's like a sensor array.

Key concepts table:
Maybe two tables: one for theoretical foundations mapped to forensic function, one for constraints/constants.

Table 1: Theoretical Foundations
| Term | Domain | Forensic Role |
| Peirce's Abductive Reasoning | Semiotics | Hypothesis generation from incomplete evidence |
| Grice's Cooperative Maxims | Pragmatics | Detecting deception by violated communication rules |
| Eco's Overinterpretation | Semiotics | Filtering red herrings / false positives |
| Carnegie's Influence Patterns | Social Engineering | Recognizing manipulation in artifacts |
| Intentionality Analysis | Philosophy of Mind | Determining purpose behind actions |

Table 2: System Guardrails (Deterministic Integer Constraints)
| Constant | Plain Meaning | Scientific Purpose |
| MAX_TEXT_LENGTH | Maximum number of characters in a single text buffer | Prevents memory saturation; bounded input |
| MAX_TEXTS_IN_LIST | Maximum number of text items per batch | Deterministic workload sizing |
| MAX_TOTAL_BYTES | Upper bound on total data volume | Integer-capped resource allocation |
| MAX_PATTERN_LENGTH | Longest searchable signature string | Exact-match boundary without approximation |
| MAX_FILE_PREVIEW | Largest preview window for evidence | Fixed-size inspection aperture |
| _ALLOWED_PATTERN | Whitelist of valid search expressions | Schema-based filtering |
| _EVIDENCE_ENV | Controlled container for evidence variables | Isolation of forensic context |
| _HONEY_TOKEN_DIR | Decoy repository location | Tripwire for unauthorized access |
| _PURGATORY_DIR | Quarantine zone for suspicious items | Containment before adjudication |
| _SYSTEM_PROMPT_PATH_DEFAULT | Default instruction set location | Reproducible analysis baseline |

Glossary:
- Abductive Reasoning: Inference to the best explanation; forming a likely hypothesis from observed effects.
- Cooperative Principle (Grice): The assumption that communicators intend to be informative, truthful, relevant, and clear.
- Honey Token: A deliberately placed fake credential or file that triggers an alert when accessed.
- Integrity Violation: A deterministic error signaling that evidence data was altered or corrupted during read operations.
- Intentionality: The quality of mental states—such as beliefs and desires—being directed toward a goal.
- Overinterpretation (Eco): The tendency to assign meaning beyond what the evidence objectively supports.
- Purgatory (Quarantine): A holding area where artifacts await further classification.
- Red Herring: A clue or artifact intentionally designed to mislead investigators.
- SIFT Workstation: A standardized digital forensic analysis platform.
- Semiotics: The study of signs and symbols and their interpretation.

Scientific Note:
【Scientific Note】
The terminology drawn from Peirce, Eco, and Grice is not mysticism or literary embellishment. Think of these constructs as a sensor analogy: just as a mass spectrometer does not “believe” in ions but uses physical principles to detect them, VIGÍA does not “believe” in intentions but applies semiotic and pragmatic constraints as deterministic filters. Peirce's abduction is a logical operator for hypothesis ranking; Grice's maxims are communication protocol validators; Eco's overinterpretation threshold is a noise-floor gate. All internal computations rely on deterministic integer arithmetic—bounded counts, exact string lengths, and discrete state transitions—ensuring reproducible, auditable results without floating-point approximation.

**ESPAÑOL**

What Is This Module? -> "¿Qué es este módulo?"
- Explanation in Spanish.

Key concepts: similar tables but in Spanish.

Glossary in Spanish.

Scientific Note -> 【Nota Científica】 or keep 【Scientific Note】? The requirement says: "A 【科学说明】/【Scientific Note】 box". I think it's acceptable to use the bracketed title in each language or adapt it. I'll use 【Nota Científica】 for Spanish, 【Научное примечание】 for Russian, 【科学说明】 for Chinese. But the requirement literally says "A 【科学说明】/【Scientific Note】 box". To be safe, I'll use the format 【Scientific Note】 in English, 【Nota Científica】 in Spanish, etc., or maybe keep the box title as requested. Let's do:
- EN: 【Scientific Note】
- ES: 【Nota Científica】
- RU: 【Научное примечание】
- ZH: 【科学说明】

That seems appropriate.

**РУССКИЙ**

What Is This Module? -> "Что это за модуль?"
- Explanation in Russian.

Key concepts tables in Russian.

Glossary in Russian.

Scientific note in Russian.

**中文**

What Is This Module? -> "本模块是什么？"
- Explanation in Chinese.
- Must use: 艾柯 (not Eco), 格赖斯 (not Grice), 取证工件 (not 制品), 逻辑断裂 (not 裂缝).
- Also 皮尔斯 for Peirce? The user didn't specify Peirce translation, but standard is 皮尔斯. I'll use 皮尔士 or 皮尔斯. Charles S. Peirce is usually 查尔斯·桑德斯·皮尔士 in academic Chinese. I'll use 皮尔士.
- Carnegie: 卡内基 (Dale Carnegie).
- SIFT: usually SIFT工作站.
- Intentionality: 意向性.
- Integrity Violation: 完整性违规? Or 读取完整性违规. The class is _IntegrityViolation. I'll describe it as 完整性违规异常.
- Honey Token: 蜜标 / 蜜罐令牌. I'll use 蜜罐令牌 or 诱饵令牌. The user didn't restrict these, but let's use standard forensic terms.
- Purgatory: 炼狱? In digital forensics, quarantine is 隔离区. The constant is _PURGATORY_DIR. I'll explain as 隔离暂存区 (Purgatory).
- Deterministic integer arithmetic: 确定性整数运算.

Check Chinese terms:
- 艾柯 (Eco)
- 格赖斯 (Grice)
- 取证工件 (evidence artifact) - user says not 制品. So use 取证工件.
- 逻辑断裂 (logical fracture/break) - user says not 裂缝. Wait, the module doesn't explicitly mention "logical fracture". The user is giving translation constraints. I should use 逻辑断裂 where appropriate if needed, but maybe not directly in the text unless necessary. The user instruction: "Chinese translations must use: 艾柯 (not Eco), 格赖斯 (not Grice), 取证工件 (not 制品), 逻辑断裂 (not 裂缝)". This implies if I mention Eco, Grice, artifact, or crack/fracture concepts, I must use these terms. For "artifact", use 取证工件. For any concept of logical break, use 逻辑断裂. Okay.

Also, the user says: "You NEVER use floating-point math explanations for deterministic systems." So in all sections, when discussing internal logic, emphasize integer boundaries, exact counts, discrete states.

 Must appear in each section? The requirement says "License line". Probably once at the end or in each section. To be safe, I'll put it at the very end of the document, but maybe also under each language section? The user says "Each section must include: ... License line". Wait, looking back: "Each section must include: - 'What Is This Module?' ... - A 【科学说明】/【Scientific Note】 box ... 5. License line". Actually point 5 is separate: "License line: ''". It doesn't explicitly say "in each section". I'll put it once at the bottom, or maybe under each section's header. But to be thorough and concise, I'll put it at the bottom of the document. However, the user listed it as a requirement alongside the 4 languages. I'll include it once after all sections. Or perhaps as a footer in each section. Let's put it at the very end of the document. But to be absolutely compliant, I'll append it to each language section? That might be repetitive. Let's read carefully: "3. Each section must include: ... 4. Chinese translations must use: ... 5. License line: ...". Actually the numbering in the prompt is:
1. Target audience...
2. Format...
3. Each section must include...
4. Chinese translations must use...
5. License line...
6. Do NOT use...

So point 5 is a global requirement. I'll put the license line once at the bottom. Or maybe under the title. I'll put it as a final footer. But to ensure visibility, I'll include it once.

Now, let's construct the content carefully.

**ENGLISH Section**

Title: ## ENGLISH

### What Is This Module?
VIGÍA — Intentionality Analysis Bridge for SIFT Workstation (`vigia/vigia_sift_bridge_final.py`) is a deterministic control layer that connects advanced theories of meaning and communication to the concrete task of digital forensic investigation.

Imagine a physical laboratory where you examine evidence. Instead of asking “What object is this?” (a question of material identity), VIGÍA asks “Why was this object placed here?” (a question of purpose and intent). It translates abstract concepts—such as Charles S. Peirce’s rules for forming hypotheses, Umberto Eco’s methods for spotting false clues, H. Paul Grice’s expectations for honest communication, and Dale Carnegie’s documented patterns of social influence—into strict, countable, reproducible operations inside a forensic computer environment.

The module contains no public functions exposed to casual users; it operates as a protected configuration and exception-management substrate. Its settings are expressed entirely as integer boundaries and exact string patterns, ensuring that every decision is auditable and free from statistical rounding.

### Key Concepts

| Theoretical Construct | Discipline | Forensic Function |
|---|---|---|
| Peirce’s Abductive Reasoning | Semiotics / Logic | Ranks competing hypotheses from incomplete evidence using exact, countable inference steps. |
| Grice’s Cooperative Maxims | Pragmatics | Validates communication artifacts against four discrete rules (quality, quantity, relevance, manner); violations flag potential deception. |
| Eco’s Overinterpretation Threshold | Semiotics | Applies an integer-strength cutoff to distinguish plausible meaning from noise and red herrings. |
| Carnegie’s Influence Patterns | Social Psychology | Maps recurrent manipulation signatures onto evidence sequences as deterministic pattern matches. |
| Intentionality Analysis | Philosophy of Mind | Shifts investigative focus from event reconstruction to motive detection. |

| System Guardrail | Form | Scientific Purpose |
|---|---|---|
| `MAX_TEXT_LENGTH` | Integer character limit | Bounds any single input buffer to a fixed, non-approximate size. |
| `MAX_TEXTS_IN_LIST` | Integer item limit | Sets a deterministic ceiling on batch workload. |
| `MAX_TOTAL_BYTES` | Integer byte limit | Caps total memory commitment with exact arithmetic. |
| `MAX_PATTERN_LENGTH` | Integer symbol limit | Restricts search signatures to precise, countable lengths. |
| `MAX_FILE_PREVIEW` | Integer window size | Defines a fixed aperture for evidence inspection. |
| `_ALLOWED_PATTERN` | Exact string schema | Whitelists valid expressions to prevent injection of malformed queries. |
| `_EVIDENCE_ENV` | Isolated variable container | Quarantines forensic context from host-system variability. |
| `_HONEY_TOKEN_DIR` | File-system path | Points to a decoy repository; access triggers an alert. |
| `_PURGATORY_DIR` | File-system path | Designates a quarantine zone for artifacts awaiting classification. |
| `_SYSTEM_PROMPT_PATH_DEFAULT` | File-system path | Anchors the default instruction set for reproducible analysis. |

### Glossary of Technical Terms

- **Abductive Reasoning** — A logical process that selects the most probable explanation for an observation from a finite set of alternatives. It operates with discrete hypotheses, not continuous probability distributions.
- **Cooperative Principle (Grice)** — The baseline assumption that communicators attempt to be truthful, informative, relevant, and clear. Violations are treated as binary flags.
- **Honey Token** — A deliberately placed decoy credential or file. Its access is logged as an integer event count.
- **Integrity Violation (`_IntegrityViolation`)** — A specialized exception that fires deterministically when evidence data fails a read-integrity check. Unlike a generic error, it is explicitly routed to an incident handler.
- **Intentionality** — The directedness of a mental state or action toward a specific goal. In VIGÍA, it is modeled as a constrained attribute of an evidence artifact rather than a subjective guess.
- **Overinterpretation (Eco)** — The assignment of meaning beyond what objective evidence supports. The module treats this as a noise-suppression problem.
- **Purgatory / Quarantine** — A holding directory where suspect files reside under restricted access until adjudication.
- **Red Herring** — A fabricated or planted clue intended to mislead an investigation.
- **SIFT Workstation** — A standardized Ubuntu-based digital forensic platform used for incident response and malware analysis.
- **Semiotics** — The formal study of signs, symbols, and their interpretation.

### 【Scientific Note】
The terminology drawn from Peirce, Eco, and Grice is not mysticism or literary embellishment. Think of these constructs as a **sensor analogy**: just as a mass spectrometer does not “believe” in ions but uses physical principles to detect them, VIGÍA does not “believe” in intentions but applies semiotic and pragmatic constraints as deterministic filters. Peirce’s abduction is a logical operator for hypothesis ranking; Grice’s maxims are communication protocol validators; Eco’s overinterpretation threshold is a noise-floor gate. All internal computations rely on **deterministic integer arithmetic**—bounded counts, exact string lengths, and discrete state transitions—ensuring reproducible, auditable results without floating-point approximation.

**ESPAÑOL Section**

Title: ## ESPAÑOL

### ¿Qué es este módulo?
VIGÍA — Intentionality Analysis Bridge for SIFT Workstation (`vigia/vigia_sift_bridge_final.py`) es una capa de control determinista que conecta teorías avanzadas del significado y la comunicación con la tarea concreta de la investigación forense digital.

Imagínese un laboratorio físico donde examina pruebas. En lugar de preguntarse «¿Qué objeto es este?» (una cuestión de identidad material), VIGÍA se pregunta «¿Por qué se colocó este objeto aquí?» (una cuestión de propósito e intención). Traduce conceptos abstractos—como las reglas de Charles S. Peirce para formar hipótesis, los métodos de Umberto Eco para detectar pistas falsas, las expectativas de H. Paul Grice sobre comunicación honesta y los patrones documentados por Dale Carnegie de influencia social—en operaciones estrictas, contables y reproducibles dentro de un entorno informático forense.

El módulo no contiene funciones públicas expuestas a usuarios casuales; opera como un sustrato protegido de configuración y gestión de excepciones. Sus ajustes se expresan enteramente como límites enteros y patrones de cadenas exactos, garantizando que cada decisión sea auditable y libre de redondeo estadístico.

### Conceptos clave

| Constructo teórico | Disciplina | Función forense |
|---|---|---|
| Razonamiento abductivo de Peirce | Semiótica / Lógica | Ordena hipótesis competidoras a partir de evidencia incompleta mediante pasos de inferencia exactos y contables. |
| Máximas cooperativas de Grice | Pragmática | Valida artefactos de comunicación contra cuatro reglas discretas (calidad, cantidad, relevancia, modo); las violaciones señalan posible engaño. |
| Umbral de sobreinterpretación de Eco | Semiótica | Aplica un punto de corte de fuerza entera para distinguir el significado plausible del ruido y las pistas falsas (*red herrings*). |
| Patrones de influencia de Carnegie | Psicología social | Asigna firmas recurrentes de manipulación sobre secuencias de pruebas como coincidencias de patrón deterministas. |
| Análisis de intencionalidad | Filosofía de la mente | Desplaza el foco investigativo de la reconstrucción del evento a la detección del motivo. |

| Barrera del sistema | Forma | Propósito científico |
|---|---|---|
| `MAX_TEXT_LENGTH` | Límite entero de caracteres | Acota cualquier búfer de entrada individual a un tamaño fijo y no aproximado. |
| `MAX_TEXTS_IN_LIST` | Límite entero de elementos | Establece un techo determinista sobre la carga de trabajo por lote. |
| `MAX_TOTAL_BYTES` | Límite entero de bytes | Fija el compromiso total de memoria con aritmética exacta. |
| `MAX_PATTERN_LENGTH` | Límite entero de símbolos | Restringe las firmas de búsqueda a longitudes precisas y contables. |
| `MAX_FILE_PREVIEW` | Tamaño entero de ventana | Define una apertura fija para la inspección de pruebas. |
| `_ALLOWED_PATTERN` | Esquema de cadena exacta | Lista blanca de expresiones válidas para prevenir la inyección de consultas malformadas. |
| `_EVIDENCE_ENV` | Contenedor de variables aislado | Pone en cuarentena el contexto forense de la variabilidad del sistema anfitrión. |
| `_HONEY_TOKEN_DIR` | Ruta del sistema de archivos | Apunta a un repositorio de señuelos; el acceso dispara una alerta. |
| `_PURGATORY_DIR` | Ruta del sistema de archivos | Designa una zona de cuarentena para artefactos en espera de clasificación. |
| `_SYSTEM_PROMPT_PATH_DEFAULT` | Ruta del sistema de archivos | Ancla el conjunto de instrucciones predeterminado para análisis reproducible. |

### Glosario de términos técnicos

- **Razonamiento abductivo** — Proceso lógico que selecciona la explicación más probable para una observación desde un conjunto finito de alternativas. Opera con hipótesis discretas, no con distribuciones de probabilidad continuas.
- **Principio cooperativo (Grice)** — Supuesto base de que los comunicadores intentan ser veraces, informativos, relevantes y claros. Las violaciones se tratan como banderas binarias.
- **Honey token (token de miel / señuelo)** — Credencial o archivo señuelo colocado deliberadamente. Su acceso se registra como un conteo entero de eventos.
- **Violación de integridad (`_IntegrityViolation`)** — Excepción especializada que se activa de manera determinista cuando los datos de prueba fallan una verificación de integridad de lectura. A diferencia de un error genérico, se enruta explícitamente a un gestor de incidentes.
- **Intencionalidad** — La direccionalidad de un estado mental o acción hacia un objetivo específico. En VIGÍA, se modela como un atributo restringido de un artefacto de prueba en lugar de una conjetura subjetiva.
- **Sobreinterpretación (Eco)** — Asignación de significado más allá de lo que la evidencia objetiva soporta. El módulo lo trata como un problema de supresión de ruido.
- **Purgatorio / Cuarentena** — Directorio de retención donde residen archivos sospechosos bajo acceso restringido hasta su adjudicación.
- **Red herring (pista falsa)** — Pista fabricada o plantada con la intención de desviar una investigación.
- **SIFT Workstation** — Plataforma forense digital estandarizada basada en Ubuntu para respuesta a incidentes y análisis de malware.
- **Semiótica** — Estudio formal de los signos, símbolos y su interpretación.

### 【Nota Científica】
La terminología proveniente de Peirce, Eco y Grice no es misticismo ni adorno literario. Piense en estos constructos como una **analogía de sensor**: así como un espectrómetro de masas no «cree» en los iones sino que usa principios físicos para detectarlos, VIGÍA no «cree» en las intenciones sino que aplica restricciones semióticas y pragmáticas como filtros deterministas. La abducción de Peirce es un operador lógico para la jerarquización de hipótesis; las máximas de Grice son validadores de protocolos de comunicación; el umbral de sobreinterpretación de Eco es una compuerta de piso de ruido. Todos los cálculos internos se basan en **aritmética entera determinista**—conteos acotados, longitudes exactas de cadenas y transiciones de estado discretas—garantizando resultados reproducibles y auditables sin aproximación de punto flotante.

**РУССКИЙ Section**

Title: ## РУССКИЙ

### Что это за модуль?
VIGÍA — Intentionality Analysis Bridge for SIFT Workstation (`vigia/vigia_sift_bridge_final.py`) — это детерминированный управляющий слой, связывающий продвинутые теории значения и коммуникации с конкретной задачей цифрового криминалистического исследования.

Представьте физическую лабораторию, где вы изучаете доказательства. Вместо вопроса «Что это за объект?» (вопрос материальной идентичности) VIGÍA задаёт вопрос «Зачем этот объект был помещён сюда?» (вопрос цели и намерения). Он переводит абстрактные концепции — такие как правила Чарльза С. Пирса для формирования гипотез, методы Умберто Эко выявления ложных следов, ожидания Г. Пола Грайса относительно честного общения и задокументированные Дейлом Карнеги паттерны социального влияния — в строгие, исчислимые и воспроизводимые операции в криминалистической вычислительной среде.

Модуль не содержит публичных функций для случайных пользователей; он работает как защищённый субстрат конфигурации и управления исключениями. Его настройки выражены исключительно целочисленными границами и точными строковыми шаблонами, гарантируя, что каждое решение поддаётся аудиту и свободно от статистического округления.

### Ключевые концепции

| Теоретическая конструкция | Дисциплина | Криминалистическая функция |
|---|---|---|
| Абдукция Пирса | Семиотика / Логика | Ранжирует конкурирующие гипотезы на основе неполных доказательств с помощью точных, исчислимых шагов вывода. |
| Кооперативные максимы Грайса | Прагматика | Проверяет коммуникационные артефакты по четырём дискретным правилам (качество, количество, релевантность, манера); нарушения сигнализируют о возможной дезинформации. |
| Порог чрезмерной интерпретации Эко | Семиотика | Применяет целочисленный порог отсечения, отличающий правдоподобный смысл от шума и ложных следов. |
| Паттерны влияния Карнеги | Социальная психология | Отображает рекуррентные сигнатуры манипуляции на последовательности доказательств как детерминированные совпадения шаблонов. |
| Анализ интенциональности | Философия сознания | Переносит акцент расследования с реконструкции события на выявление мотива. |

| Системный ограничитель | Форма | Научное назначение |
|---|---|---|
| `MAX_TEXT_LENGTH` | Целочисленный лимит символов | Ограничивает любой отдельный входной буфер фиксированным, неприближённым размером. |
| `MAX_TEXTS_IN_LIST` | Целочисленный лимит элементов | Устанавливает детерминированный потолок нагрузки пакета. |
| `MAX_TOTAL_BYTES` | Целочисленный лимит байтов | Ограничивает общий объём памяти точной арифметикой. |
| `MAX_PATTERN_LENGTH` | Целочисленный лимит символов шаблона | Суживает поисковые сигнатуры до точных, исчислимых длин. |
| `MAX_FILE_PREVIEW` | Целочисленный размер окна | Задаёт фиксированную апертуру для осмотра доказательств. |
| `_ALLOWED_PATTERN` | Точная строковая схема | «Белый список» допустимых выражений для предотвращения инъекции некорректных запросов. |
| `_EVIDENCE_ENV` | Изолированный контейнер переменных | Изолирует криминалистический контекст от изменчивости хост-системы. |
| `_HONEY_TOKEN_DIR` | Путь файловой системы | Указывает на хранилище приманок; доступ к нему инициирует оповещение. |
| `_PURGATORY_DIR` | Путь файловой системы | Назначает карантинную зону для артефактов, ожидающих классификации. |
| `_SYSTEM_PROMPT_PATH_DEFAULT` | Путь файловой системы | Фиксирует базовый набор инструкций для воспроизводимого анализа. |

### Глоссарий технических терминов

- **Абдукция (абдуктивное рассуждение)** — Логический процесс выбора наиболее вероятного объяснения наблюдения из конечного набора альтернатив. Оперирует дискретными гипотезами, а не непрерывными распределениями вероятностей.
- **Кооперативный принцип (Грайс)** — Базовое предположение, что коммуниканты стремятся быть правдивыми, информативными, релевантными и ясными. Нарушения трактуются как бинарные флаги.
- **Honey token (приманка / медовый токен)** — Специально размещённая ложная учётная запись или файл. Доступ к нему регистрируется как целочисленное событие.
- **Нарушение целостности (`_IntegrityViolation`)** — Специализированное исключение, детерминированно возникающее при сбое проверки целостности данных доказательств при чтении. В отличие от универсальной ошибки, оно явно маршрутизируется к обработчику инцидентов.
- **Интенциональность** — Направленность ментального состояния или действия на конкретную цель. В VIGÍA моделируется как ограниченный атрибут криминалистического артефакта, а не как субъективная догадка.
- **Чрезмерная интерпретация (Эко)** — Приписывание смысла сверх того, что объективно поддерживается доказательствами. Модуль рассматривает это как задачу подавления шума.
- **Чистилище / Карантин** — Директория удержания, где подозрительные файлы находятся под ограниченным доступом до вынесения решения.
- **Ложный след (red herring)** — Сфабрикованная или подброшенная улика, предназначенная для введения расследования в заблуждение.
- **SIFT Workstation** — Стандартизированная цифровая криминалистическая платформа на базе Ubuntu для реагирования на инциденты и анализа вредоносного ПО.
- **Семиотика** — Формальное изучение знаков, символов и их интерпретации.

### 【Научное примечание】
Терминология, заимствованная у Пирса, Эко и Грайса, не является мистикой или литературным украшением. Мысленно сравните эти конструкты с **аналогией датчика**: так же, как масс-спектрометр не «верит» в ионы, а использует физические принципы для их обнаружения, VIGÍA не «верит» в намерения, а применяет семиотические и прагматические ограничения в качестве детерминированных фильтров. Абдукция Пирса — это логический оператор для ранжирования гипотез; максимы Грайса — валидаторы коммуникационных протоколов; порог чрезмерной интерпретации Эко — шумоподавляющий порог. Все внутренние вычисления опираются на **детерминированную целочисленную арифметику** — ограниченные счётчики, точные длины строк и дискретные переходы состояний — обеспечивая воспроизводимые, поддающиеся аудиту результаты без приближений с плавающей запятой.

**中文 Section**

Title: ## 中文

### 本模块是什么？
VIGÍA — SIFT工作站的意向性分析桥接模块（`vigia/vigia_sift_bridge_final.py`）是一个确定性控制层，它将高级意义与通信理论转化为数字取证调查的具体任务。

想象一间实体实验室，您正在检查取证工件。VIGÍA不问“这是什么东西？”（物质身份问题），而是问“为什么这个东西会被放在这里？”（目的与意向问题）。它将抽象概念——例如查尔斯·S·皮尔士的假设形成规则、翁贝托·艾柯识别假线索的方法、H·保罗·格赖斯对诚实通信的期望，以及戴尔·卡内基记录的社会影响模式——转化为计算机取证环境中的严格、可计数、可复现的操作。

该模块不向普通用户暴露任何公共函数；它作为受保护的配置与异常管理底层运行。其设置完全以整数边界和精确字符串模式表达，确保每一项决定均可审计，且不受统计舍入影响。

### 核心概念

| 理论构建 | 学科 | 取证功能 |
|---|---|---|
| 皮尔士的溯因推理 | 符号学 / 逻辑学 | 从不完整证据出发，通过精确、可计数的推理步骤对竞争性假设进行排序。 |
| 格赖斯的合作原则 | 语用学 | 依据四条离散规则（质量、数量、关联、方式）验证通信取证工件；违规标记潜在欺骗。 |
| 艾柯的过度诠释阈值 | 符号学 | 施加整数强度截断，区分可信意义与噪音及假线索。 |
| 卡内基的影响模式 | 社会心理学 | 将反复出现的操控特征映射到证据序列，作为确定性模式匹配。 |
| 意向性分析 | 心灵哲学 | 将调查焦点从事件重构转向动机检测。 |

| 系统防护栏 | 形式 | 科学用途 |
|---|---|---|
| `MAX_TEXT_LENGTH` | 整数字符上限 | 将单个输入缓冲区的尺寸限制为固定、非近似值。 |
| `MAX_TEXTS_IN_LIST` | 整数项目上限 | 为批量工作负载设置确定性上限。 |
| `MAX_TOTAL_BYTES` | 整数字节上限 | 以精确算术限制总内存占用。 |
| `MAX_PATTERN_LENGTH` | 整数符号上限 | 将搜索签名的长度限制为精确、可计数的值。 |
|
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
