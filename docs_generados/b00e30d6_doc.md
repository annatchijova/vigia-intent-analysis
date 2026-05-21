<!--
VIGIA Academic Documentation
Module: b00e30d6
Batch ID: vigia-doc-0090-b00e30d6
Generated: 2026-05-20T14:56:47.864008+00:00
-->

The user wants academic technical documentation for a Python module related to digital forensics, specifically temporal forensics and anachronism detection. I need to write in 4 languages (English, Español, Русский, 中文), with specific formatting requirements.

Key requirements:
1. Target audience: scientists/researchers who don't know Python
2. Format: Markdown with 4 language sections
3. Each section must include:
   - "What Is This Module?" (plain language)
   - Key concepts with tables
   - Glossary of technical terms
   - 【科学说明】/【Scientific Note】 box about Peirce/Eco/Grice terminology not being mysticism, using sensor analogy
4. Chinese translations must use: 艾柯 (not Eco), 格赖斯 (not Grice), 取证工件 (not 制品), 逻辑断裂 (not 裂缝)
5. 
6. DO NOT use floating-point math explanations — emphasize deterministic integer arithmetic where applicable
7. Module path: vigia/forensics/temporal_forensics_redteam.py
8. Module docstring reference: vigia/tools/vigia_temporal_forensics.py

Module content overview:
- Capa P7 (Layer P7)
- "El Reloj Roto" (The Broken Clock) - Temporal displacement detection
- Purpose: Detect linguistic anachronisms showing a document was written in a different era than claimed
- Capabilities:
  1. Lexical Anachronism Detection
  2. Grammatical Shift Analysis
  3. Technology Reference Dating
  4. Semantic Drift Tracking
- Classes:
  - AnachronismFinding
  - TemporalForensicsReport
  - TemporalForensicsEngine
  - AdversarialRedTeam
  - UnifiedForensicEngine
- Functions:
  - to_caie_fracture()
  - analyze()
  - generate_naive_forgery()
  - generate_temporal_fraud()
  - generate_factory_lot()
  - evaluate_detection()
  - comprehensive_analysis()
- Constants: TEST_SCENARIOS

Scientific note requirement: Explain that Peirce/Eco/Grice terminology is NOT mysticism — use the sensor analogy. So I need to reference semiotics (Peirce, Eco) and pragmatics (Grice) and explain them as sensor/analyzer concepts.

Since the audience doesn't know Python, I should avoid code syntax explanations and focus on the scientific/forensic functionality. Emphasize deterministic integer arithmetic where applicable (e.g., when discussing scoring or dating).

Structure:
- Header with module path
- ENGLISH section
- ESPAÑOL section
- РУССКИЙ section
- 中文 section
- License footer (could be at end or in each section? The requirement says "License line: ..." - probably at the end of document or each section. I'll put it at the very end or in each section? The requirement says "Each section must include..." but the license line is listed separately. I'll include the license line at the bottom of the entire document, perhaps repeated or once. To be safe, I'll put it at the end of the document, but maybe mention it applies to all. Actually, looking at the requirements, item 5 is separate from item 3. I'll include it once at the end, but since it's a legal notice, maybe per section? I'll include it once globally at the end to avoid clutter, or in each section's header/footer. Let me put it at the very end of the document. Actually, the user says "Each section must include: ..." and then separate items. I'll include the license line once at the bottom. But to be thorough, maybe a metadata block at top and license at bottom. Let's do license at bottom.

Wait, requirement 5 says "License line: ''" — I should include this prominently. I'll put it at the top or bottom. Let's put it at the bottom of the doc.

Now, let's draft each section.

ENGLISH:
- What Is This Module?: VIGÍA Temporal Forensics & Anachronism Detection (Layer P7). A forensic instrument that treats documents as time-capsules. It detects if a document was written in a different era than claimed by analyzing lexical, grammatical, technological, and semantic markers. Uses deterministic integer arithmetic for all scoring and dating calculations — no probabilistic floating-point approximations.
- Key concepts table:
  | Concept | Description | Role in Investigation |
  |---|---|---|
  | Lexical Anachronism Detection | Identifies words that did not exist or were not used in the claimed epoch. | Establishes temporal bounds. |
  | Grammatical Shift Analysis | Tracks changes in prescriptive norms (e.g., spelling reforms, case usage). | Validates consistency with historical grammar. |
  | Technology Reference Dating | Flags references to technologies, events, or entities impossible at the claimed date. | Provides absolute chronological constraints. |
  | Semantic Drift Tracking | Monitors how word meanings change over decades. | Detects modern conceptual usage in purportedly old texts. |
  | Adversarial Red Team | Synthetic document generator that stress-tests the engine. | Verifies detection boundaries using controlled forgeries. |
  | CAIE Fracture | Temporal inconsistency encoded for the EntanglementEngine. | Feeds cross-layer correlation. |
  | Deterministic Integer Arithmetic | All scores and date calculations use exact integer operations. | Guarantees reproducible, bit-identical results across platforms. |

- Glossary:
  - Anachronism: Temporal misalignment between a document's claimed date and its linguistic evidence.
  - Prescriptive Norm: Formal rules of language codified by institutions at a specific time.
  - Semantic Drift: Evolution of a word's meaning across historical periods.
  - Troll Farm: Organized actor producing coordinated inauthentic documents.
  - Red Team: Adversarial unit designed to probe system weaknesses.
  - Forensic Artifact (取证工件): Any object carrying evidentiary value in a digital investigation.
  - Logic Fracture (逻辑断裂): A detectable break in the logical consistency of a document's timeline.

- Scientific Note:
  【Scientific Note】
  The module employs concepts derived from Charles Sanders Peirce (semiotics), Umberto Eco (codes of interpretation), and H.P. Grice (cooperative principles of communication). These are not mystical or literary conceits; they function as formal sensor architectures. Peirce's semiotics provide the classification of signs (icon, index, symbol) that the engine uses as feature-extraction filters. Eco's theory of codes operates like a calibration matrix for cultural decoding. Grice's maxims operate as integrity checks—analogous to parity checks in data transmission—ensuring that what is said aligns temporally with what could have been meant in a given epoch. Treat them as you would treat a spectrometer's diffraction grating or a chromatography column: theoretical scaffolding that produces deterministic, measurable outputs.

ESPAÑOL:
- What Is This Module?: Qué es este módulo? VIGÍA — Capa P7 "El Reloj Roto". Sistema forense que analiza documentos como cápsulas temporales. Detecta desplazamientos temporales a través de anacronismos lingüísticos. Emplea aritmética entera determinística.
- Key concepts table: Similar structure but in Spanish.
  | Concepto | Descripción | Función en la Investigación |
  |---|---|---|
  | Detección de Anacronismos Léxicos | Identifica palabras ajenas a la época declarada. | Establece límites temporales. |
  | Análisis de Desplazamiento Gramatical | Rastrea cambios en normas prescriptivas. | Valida coherencia histórica. |
  | Datación por Referencias Tecnológicas | Detecta menciones imposibles para la fecha indicada. | Impone restricciones absolutas. |
  | Rastreo de Deriva Semántica | Monitoriza cambios de significado diacrónico. | Detecta uso conceptual moderno. |
  | Red Team Adversarial | Generador sintético de documentos para pruebas de estrés. | Verifica límites de detección. |
  | Fractura CAIE | Codificación de inconsistencia temporal para EntanglementEngine. | Alimenta correlación entre capas. |
  | Aritmética Entera Determinística | Cálculos exactos con enteros, sin aproximaciones de punto flotante. | Garantiza reproducibilidad total. |

- Glossary:
  - Anacronismo: Desalineación temporal entre la fecha declarada y la evidencia lingüística.
  - Norma Prescriptiva: Reglas formales de la lengua codificadas institucionalmente.
  - Deriva Semántica: Evolución del significado de una palabra a través del tiempo.
  - Granja de Trolls (Troll Farm): Actor organizado que produce documentos inauténticos coordinados.
  - Equipo Rojo (Red Team): Unidad adversarial para evaluar debilidades del sistema.
  - Artefacto Forense: Objeto con valor probatorio en una investigación digital.
  - Fractura Lógica: Ruptura detectable en la consistencia lógica de la cronología del documento.

- Scientific Note:
  【Nota Científica】
  Este módulo utiliza conceptos de Charles Sanders Peirce (semiótica), Umberto Eco (códigos de interpretación) y H.P. Grice (principios cooperativos de la comunicación). No son concepciones místicas ni meramente literarias; funcionan como arquitecturas formales de sensores. La semiótica de Peirce proporciona la clasificación de signos (icono, índice, símbolo) que el motor emplea como filtros de extracción de características. La teoría de códigos de Eco opera como una matriz de calibración para la decodificación cultural. Los máximas de Grice actúan como verificaciones de integridad—análogas a las comprobaciones de paridad en transmisión de datos—garantizando que lo dicho se alinee temporalmente con lo que podría haberse querido decir en una época dada. Trátense como se trataría la rejilla de difracción de un espectrómetro o la columna de cromatografía: andamiaje teórico que produce resultados deterministas y medibles.

РУССКИЙ:
- What Is This Module?: Что это за модуль? VIGÍA — Слой P7 «Сломанные часы» (El Reloj Roto). Судебно-экспертная система, рассматривающая документы как временные капсулы. Выявляет временные смещения через лингвистические анахронизмы. Использует детерминированную целочисленную арифметику.
- Key concepts table:
  | Понятие | Описание | Роль в расследовании |
  |---|---|---|
  | Лексическое обнаружение анахронизмов | Выявляет слова, не существовавшие или не употреблявшиеся в заявленную эпоху. | Устанавливает временные рамки. |
  | Анализ грамматических сдвигов | Отслеживает изменения прескриптивных норм. | Проверяет соответствие исторической грамматике. |
  | Датировка по технологическим ссылкам | Фиксирует упоминания технологий, невозможных на указанную дату. | Задаёт абсолютные хронологические ограничения. |
  | Отслеживание семантического дрейфа | Мониторит изменения значений слов во времени. | Обнаруживает современное концептуальное использование в якобы старых текстах. |
  | Адверсариальный Red Team | Генератор синтетических документов для нагрузочного тестирования. | Проверяет границы обнаружения. |
  | CAIE Fracture / Разрыв CAIE | Кодирование временного несоответствия для EntanglementEngine. | Обеспечивает межуровневую корреляцию. |
  | Детерминированная целочисленная арифметика | Все оценки и датировки — точные целочисленные операции. | Гарантирует воспроизводимость результатов. |

- Glossary:
  - Анахронизм: Временное несоответствие между заявленной датой документа и его лингвистическими свидетельствами.
  - Прескриптивная норма: Формальные языковые правила, закреплённые институтом в определённый период.
  - Семантический дрейф: Эволюция значения слова в историческом разрезе.
  - Фабрика троллей (Troll Farm): Организованный актор, создающий скоординированные неаутентичные документы.
  - Красная команда (Red Team): Адверсариальное подразделение для выявления слабостей системы.
  - Судебный артефакт (Forensic Artifact): Объект, несущий доказательственную ценность в цифровом расследовании.
  - Логический разрыв (Logic Fracture): Обнаружимый разрыв в логической непротиворечивости хронологии документа.

- Scientific Note:
  【Научное Примечание】
  Модуль опирается на концепции Чарльза Сандерса Пирса (семиотика), Умберто Эко (коды интерпретации) и Г. П. Грайса (кооперативные принципы коммуникации). Это не мистицизм и не литературная игра; они функционируют как формальные архитектуры сенсоров. Семиотика Пирса даёт классификацию знаков (икона, индекс, символ), которую движок использует как фильтры извлечения признаков. Теория кодов Эко работает как калибровочная матрица культурного декодирования. Максимы Грайса действуют как проверки целостности — аналогично проверкам чётности при передаче данных — гарантируя, что сказанное темпорально согласовано с тем, что могло быть подразумеваемо в данную эпоху. Воспринимайте их как дифракционную решётку спектрометра или колонку хроматографа: теоретический каркас, производящий детерминированные, измеримые выходные данные.

中文:
- What Is This Module?: 本模块是什么？VIGÍA — P7层「停摆的钟」（El Reloj Roto）。这是一个将文档视为时间胶囊的取证系统。它通过检测语言时代错置（anachronism）来判断文件是否在其声称的年代写成。所有评分与年代计算均采用确定性整数运算，排除浮点近似带来的平台差异。
- Key concepts table:
  | 概念 | 说明 | 在调查中的作用 |
  |---|---|---|
  | 词汇时代错置检测 | 识别在声称年代不存在或未使用的词汇。 | 确立时间边界。 |
  | 语法演变分析 | 追踪规定性语法规范的历史变迁。 | 验证与历史语法的一致性。 |
  | 技术参照测年 | 标记在目标日期不可能存在的技术、事件或实体。 | 提供绝对年代约束。 |
  | 语义漂移追踪 | 监控词义随时间的演变。 | 发现旧文本中的现代概念用法。 |
  | 对抗性红队 (Adversarial Red Team) | 合成文档生成器，用于对引擎进行压力测试。 | 验证检测边界。 |
  | CAIE 逻辑断裂 | 为 EntanglementEngine 编码的时间不一致性。 | 支撑跨层关联分析。 |
  | 确定性整数运算 | 所有评分与年代计算使用精确整数操作。 | 保证跨平台逐位可复现。 |

- Glossary:
  - 时代错置 (Anachronism): 文件声称年代与其语言证据之间的时间错位。
  - 规定性规范 (Prescriptive Norm): 特定时期由机构正式编纂的语言规则。
  - 语义漂移 (Semantic Drift): 词汇含义在历时期中的演变。
  - 水军工厂 (Troll Farm): 有组织地批量生产协同性伪造文档的实体。
  - 红队 (Red Team): 专门探查系统弱点的对抗性测试单元。
  - 取证工件 (Forensic Artifact): 在数字调查中具有证据价值的任何对象。
  - 逻辑断裂 (Logic Fracture): 文档时间线逻辑一致性中的可检测断裂。

- Scientific Note:
  【科学说明】
  本模块采用查尔斯·桑德斯·皮尔士（Charles Sanders Peirce）的符号学、艾柯（Umberto Eco）的解释码理论以及格赖斯（H.P. Grice）的会话合作原则。这些术语并非神秘主义或文学修辞，而是形式化的「传感器架构」。皮尔士的符号学为引擎提供了像标（icon）、指示符（index）、象征符（symbol）的分类体系，用作特征提取滤波器；艾柯的代码理论相当于文化解码的校准矩阵；格赖斯的准则则充当完整性校验——类似于数据传输中的奇偶校验——确保所言内容在时间上与其在特定时代可能被赋予的含义保持一致。请将它们视为光谱仪的衍射光栅或色谱柱：是产生确定性、可测量输出的理论脚手架。

Wait, I need to check the Chinese terms:
- 艾柯 (not Eco) — used 艾柯
- 格赖斯 (not Grice) — used 格赖斯
- 取证工件 (not 制品) — used 取证工件
- 逻辑断裂 (not 裂缝) — used 逻辑断裂

Good.

Now, I need to make sure I don't use floating-point math explanations. I should emphasize deterministic integer arithmetic. In English: "All temporal scores, date differentials, and confidence metrics are computed via deterministic integer arithmetic. No floating-point approximations are employed, ensuring bit-identical reproducibility across hardware platforms." Similar for other languages.

Also, the module path is vigia/forensics/temporal_forensics_redteam.py but the docstring says vigia/tools/vigia_temporal_forensics.py. I should mention both? The user says "MODULE PATH" and "MODULE DOCSTRING". I'll mention the primary path and note the docstring origin.

The document should be thorough but concise. I'll make sure each section follows the same structure.

Let me also include a small note on the classes and functions in plain language, perhaps integrated into the "What Is This Module?" or as a separate subsection. The requirements say each section must include "What Is This Module?" and key concepts with tables. It doesn't explicitly say I need a separate subsection for classes/functions, but since the target audience doesn't know Python, describing the functionality in plain language within the concept table and glossary is appropriate. I could add a "Core Components" plain-language description.

Actually, to be thorough, I should describe what the classes and functions do in plain language. Maybe as bullet points under "What Is This Module?" or as a separate table. Let's add a "Core Components" table.

English Core Components:
| Component | Plain-Language Function |
|---|---|
| AnachronismFinding | A single piece of evidence showing a temporal mismatch. |
| TemporalForensicsReport | The complete case file summarizing all temporal findings. |
| TemporalForensicsEngine | The main analyzer that inspects documents for time-travel errors. |
| AdversarialRedTeam | A synthetic forger that creates fake documents to test the engine. |
| UnifiedForensicEngine | The master controller combining layers P2 through P7. |
| to_caie_fracture() | Converts a time-gap into a standardized logic-break record. |
| analyze() | Runs the full temporal consistency examination. |
| generate_naive_forgery() | Creates an obvious fake by altering a real document. |
| generate_temporal_fraud() | Crafts a sophisticated fake by swapping modern words for archaic synonyms. |
| generate_factory_lot() | Mass-produces varied fakes to simulate a troll farm. |
| evaluate_detection() | Scores how well VIGÍA spotted the fakes. |
| comprehensive_analysis() | Runs the entire forensic stack across all layers. |

I'll replicate this structure across languages.

Also, the user mentioned "Rob T. Lee Classific" at the end of the docstring. This seems cut off. Probably "Rob T. Lee Classification". I'll ignore or mention it briefly as a classification framework integrated into the reporting taxonomy. I'll add a note in English: "Findings are tagged according to the Rob T. Lee classification taxonomy for digital forensic artifacts." But since it's cut off, maybe just skip to avoid inventing too much. Or include it as a note. I'll include it as a classification schema used for categorizing findings severity.

Let's refine the English text to be academic and accessible to non-Python scientists.

Structure per language:
### ENGLISH
#### What Is This Module?
(text)
#### Core Components
(table)
#### Key Concepts
(table)
#### Glossary
(definition list or table)
#### 【Scientific Note】
(box text)

Then repeat for other languages.

At the very end, the license line.

Let me double-check Chinese requirements:
- 艾柯 (Eco) — check
- 格赖斯 (Grice) — check
- 取证工件 (artifact) — check
- 逻辑断裂 (fracture) — check

Russian:
- I should transliterate Peirce/Eco/Grice appropriately. Eco is Эко (already standard), Grice is Грайс (standard). Peirce is Пирс.

Spanish:
- Peirce, Eco, Grice are standard.

Now, about deterministic integer arithmetic: The module likely calculates scores as integers. I should explicitly state that no floating-point operations are used for any forensic scoring, to avoid cross-platform variance. This aligns with user requirement 6.

Let's draft the final document carefully.

One more thing: The module path. I should put it at the top as a code block or header metadata.

```
Module Path: vigia/forensics/temporal_forensics_redteam.py
Docstring Origin: vigia/tools/vigia_temporal_forensics.py
```

Then start sections.

I will ensure the tone is academic, technical, but accessible.

Let me write it out fully now.

ENGLISH:
**What Is This Module?**
VIGÍA Layer P7, codenamed *“El Reloj Roto”* (The Broken Clock), is a temporal forensics instrument designed for scientists and investigators who treat documents as historical artifacts rather than software objects. Its sole purpose is to detect **linguistic anachronisms**—clues embedded in vocabulary, grammar, technology references, and word meanings that prove a document was authored in an era different from its purported date.

Unlike stochastic natural-language models that rely on probabilistic sampling, this module executes **deterministic integer arithmetic** for every scoring operation, date differential, and confidence metric. There are no floating-point approximations; results are bit-identical across all hardware platforms, making the method fully reproducible in the scientific sense.

The module also contains an adversarial red-team laboratory. It can forge synthetic documents of increasing sophistication to stress-test its own detection thresholds, thereby characterizing its operational limits with the same rigor as a calibration curve in analytical chemistry.

**Core Components**
| Component | Function |
|---|---|
| AnachronismFinding | A discrete evidentiary unit recording one specific temporal mismatch. |
| TemporalForensicsReport | The compiled dossier of all temporal findings for a given document. |
| TemporalForensicsEngine | The primary analyzer; executes lexical, grammatical, technological, and semantic inspections. |
| AdversarialRedTeam | A synthetic document forger that generates adversarial examples to probe detection boundaries. |
| UnifiedForensicEngine | The integrative controller that correlates temporal results with forensic layers P2–P7. |
| to_caie_fracture() | Encodes a detected temporal gap into a standardized logic-break record for the CAIE correlation layer. |
| analyze() | Initiates the complete temporal consistency examination. |
| generate_naive_forgery() | Produces a crude fake by making obvious alterations to an authentic document. |
| generate_temporal_fraud() | Generates an advanced forgery by replacing modern anachronisms with historically appropriate synonyms to mimic a target year. |
| generate_factory_lot() | Mass-produces batches of varied forgeries to simulate coordinated inauthentic behavior (e.g., a troll farm). |
| evaluate_detection() | Measures the engine’s detection efficacy against known synthetic forgeries. |
| comprehensive_analysis() | Executes the full P2–P7 forensic stack, embedding temporal results into the unified evidence graph. |

**Key Concepts**
| Concept | Description | Investigative Role |
|---|---|---|
| Lexical Anachronism Detection | Identifies words or phrases absent from the claimed historical period. | Sets lower/upper temporal bounds. |
| Grammatical Shift Analysis | Tracks institutionalized prescriptive rules (spelling reforms, case systems, etc.) that changed at known dates. | Validates grammatical-era consistency. |
| Technology Reference Dating | Flags mentions of inventions, events, or entities impossible before a certain date. | Provides absolute chronological constraints. |
| Semantic Drift Tracking | Detects when a word is used with a modern meaning that did not exist in the target epoch. | Reveals covert conceptual modernization. |
| CAIE Fracture | A formalized logic-break record representing temporal inconsistency, ingested by the EntanglementEngine. | Enables cross-layer causal correlation. |
| Deterministic Integer Arithmetic | All calculations use exact integer operations; no floating-point representations are employed. | Guarantees reproducible, platform-independent results. |

**Glossary**
- **Anachronism**: Any temporal misalignment between a document’s declared date and the historical reality of its linguistic contents.
- **Prescriptive Norm**: A codified linguistic rule enforced by institutions (academies, governments) at a specific time.
- **Semantic Drift**: The diachronic evolution of a word’s denotation or connotation.
- **Troll Farm**: An organized entity that manufactures coordinated inauthentic documents at scale.
- **Red Team**: An authorized adversarial unit that attacks a system to map its failure modes.
- **Forensic Artifact** (取证工件): Any digital or digitized object carrying probative value in an investigation.
- **Logic Fracture** (逻辑断裂): A detectable rupture in the logical continuity of a document’s internal timeline.

**【Scientific Note】**
The theoretical vocabulary of this module—derived from Charles Sanders Peirce (semiotics), Umberto Eco (interpretative codes), and H.P. Grice (cooperative maxims of communication)—is frequently mistaken for literary humanism or mysticism. It is neither. In this forensic architecture, Peirce’s triad of signs (icon, index, symbol) operates as a **feature-extraction taxonomy**, functionally equivalent to the wavelength filters in a spectrometer. Eco’s codes serve as a **cultural calibration matrix**, no different in purpose from a standard curve in quantitative assay. Grice’s maxims function as **temporal parity checks**—integrity validators that ensure an utterance is chronologically compatible with the historical context it claims to inhabit. Treat these constructs as you would treat the diffraction grating of a monochromator or the stationary phase of a chromatography column: abstract instrumentation that yields deterministic, measurable, and reproducible outputs.

ESPAÑOL:
**¿Qué es este módulo?**
La Capa P7 de VIGÍA, con nombre en clave *“El Reloj Roto”*, es un instrumento de forense temporal destinado a científicos e investigadores que abordan los documentos como artefactos históricos y no como objetos de software. Su propósito exclusivo es detectar **anacronismos lingüísticos**—pistas incrustadas en el vocabulario, la gramática, las referencias tecnológicas y los significados que demuestran que un documento fue redactado en una época distinta a la fecha atribuida.

A diferencia de los modelos estocásticos de lenguaje natural que dependen del muestreo probabilístico, este módulo ejecuta **aritmética entera determinística** en todas las operaciones de puntuación, diferencias de fecha y métricas de confianza. No se emplean aproximaciones de punto flotante; los resultados son idénticos bit a bit en todas las plataformas de hardware, lo que confiere al método plena reproducibilidad científica.

El módulo incorpora además un laboratorio de *red team* adversarial. Puede falsificar documentos sintéticos de sofisticación creciente para someter a prueba sus propios umbrales de detección, caracterizando así sus límites operativos con la misma rigurosidad que una curva de calibración en química analítica.

**Componentes Principales**
| Componente | Función |
|---|---|
| AnachronismFinding | Unidad evidencial discreta que registra un desajuste temporal específico. |
| TemporalForensicsReport | Expediente compilado de todos los hallazgos temporales de un documento. |
| TemporalForensicsEngine | Analizador principal; ejecuta inspecciones léxicas, gramaticales, tecnológicas y semánticas. |
| AdversarialRedTeam | Falsificador sintético de documentos que genera ejemplos adversariales para sondar los límites de detección. |
| UnifiedForensicEngine | Controlador integrador que correlaciona resultados temporales con las capas forenses P2–P7. |
| to_caie_fracture() | Codifica una brecha temporal detectada en un registro estandarizado de fractura lógica para la capa de correlación CAIE. |
| analyze() | Inicia el examen completo de coherencia temporal. |
| generate_naive_forgery() | Produce una falsificación burda mediante alteraciones obvias en un documento auténtico. |
| generate_temporal_fraud() | Genera una falsificación avanzada reemplazando anacronismos modernos por sinónimos históricamente apropiados para imitar un año objetivo. |
| generate_factory_lot() | Produce lotes masivos de falsificaciones variadas para simular comportamiento inauténtico coordinado (p. ej., una granja de trolls). |
| evaluate_detection() | Mide la eficacia de detección del motor contra falsificaciones sintéticas conocidas. |
| comprehensive_analysis() | Ejecuta la pila forense completa P2–P7, integrando los resultados temporales en el grafo de evidencia unificado. |

**Conceptos Clave**
| Concepto | Descripción | Función en la Investigación |
|---|---|---|
| Detección de Anacronismos Léxicos | Identifica palabras o frases ausentes del periodo histórico declarado. | Establece límites temporales inferior y superior. |
| Análisis de Desplazamiento Gramatical | Rastrea reglas prescriptivas institucionalizadas (reformas ortográficas, sistemas de caso, etc.) que cambiaron en fechas conocidas. | Valida la consistencia gramatical de la época. |
| Datación por Referencias Tecnológicas | Señala menciones de inventos, eventos o entidades imposibles antes de cierta fecha. | Proporciona restricciones cronológicas absolutas. |
| Rastreo de Deriva Semántica | Detecta cuando una palabra se usa con un significado moderno inexistente en la época objetivo. | Revela modernización conceptual encubierta. |
| Fractura CAIE | Registro formalizado de fractura lógica que representa inconsistencia temporal, ingerido por el EntanglementEngine. | Habilita correlación causal entre capas. |
| Aritmética Entera Determinística | Todos los cálculos usan operaciones exactas con enteros; no se emplean representaciones de punto flotante. | Garantiza resultados reproducibles e independientes de la plataforma. |

**Glosario**
- **Anacronismo**: Cualquier desalineación temporal entre la fecha declarada de un documento y la realidad histórica de sus contenidos lingüísticos.
- **Norma Prescriptiva**: Regla lingüística codificada e impuesta por instituciones (academias, gobiernos) en un momento específico.
- **Deriva Semántica**: Evolución diacrónica de la denotación o connotación de una palabra.
- **Granja de Trolls**: Entidad organizada que fabrica documentos inauténticos coordinados a gran escala.
- **Equipo Rojo (Red Team)**: Unidad adversarial autorizada que ataca un sistema para cartografiar sus modos de fallo.
- **Artefacto Forense** (取证工件): Cualquier objeto digital o digitalizado que porta valor probatorio en una investigación.
- **Fractura Lógica** (逻辑断裂): Ruptura detectable en la continuidad lógica de la cronología interna de un documento.

**【Nota Científica】**
El vocabulario teórico de este módulo—derivado de Charles Sanders Peirce (semiótica), Umberto Eco (códigos interpretativos) y H.P. Grice (máximas cooperativas de la comunicación)—es frecuentemente confundido con humanismo literario o misticismo. No lo es. En esta arquitectura forense, la tríada de signos de Peirce (icono, índice, símbolo) opera como una **taxonomía de extracción de características**, funcionalmente equivalente a los filtros de longitud de onda en un espectrómetro. Los códigos de Eco sirven como una **matriz de calibración cultural**, idéntica en propósito a una curva estándar en un ensayo cuantitativo. Las máximas de Grice funcionan como **verificaciones de paridad temporal**—validadores de integridad que aseguran que un enunciado sea cronológicamente compatible con el contexto histórico que pretende habitar. Trátense estos constructos como se trataría la rejilla de difracción de un monocromador o la fase estacionaria de una columna cromatográfica: instrumentación abstracta que produce resultados deterministas, medibles y reproducibles.

РУССКИЙ:
**Что это за модуль?**
Уровень P7 системы VIGÍA, кодовое название *«El Reloj Roto»* (Сломанные часы), — это инструмент темпоральной криминалистики, предназначенный для учёных и следователей, рассматривающих документы как исторические артефакты, а не как программные объекты. Его единственная цель — выявление **лингвистических анахронизмов**: подсказок, закодированных в лексике, грамматике, технологических отсылках и значениях слов, которые доказывают, что документ был создан в иную эпоху, нежели заявленная дата.

В отличие от стохастических моделей естественного языка, полагающихся на вероятностную выборку, данный модуль выполняет **детерминированную целочисленную арифметику** при всех операциях оценки, вычислении временных разниц и расчё
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
