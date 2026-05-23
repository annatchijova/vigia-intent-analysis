<!--
VIGIA Academic Documentation
Module: 7a688cdd
Batch ID: vigia-doc-0168-7a688cdd
Generated: 2026-05-20T14:56:47.880966+00:00
-->

---
doc_hash: 7a688cdd
module: vigia/tools/pattern_detector.py
languages: [EN, ES, RU, ZH]
generated_by: moonshot-kimi-k2.6-batch-api
license: Apache-2.0
---

ENGLISH:
- What Is This Module?: A deterministic forensic engine that scans textual artifacts for adversarial semiotic patterns. It uses regular expressions and abductive logic (rule-based inference) rather than machine learning or statistics. It operates on integer arithmetic for reproducibility. Part of VIGÍA pipeline.
- Key Concepts Table:
  - Semiotic Friction | A mismatch between intended meaning and encoded signal, indicative of adversarial manipulation.
  - Abductive Logic | Rule-based inference that generates the best explanation from observed patterns (Peircean framework).
  - Textual Artifact | Any file or string subjected to forensic examination (logs, configs, scripts).
  - Deterministic Integer Scoring | Risk scores calculated via exact integer arithmetic, ensuring identical inputs always yield identical outputs.
  - Regex Pattern | Precise symbolic search rules that match known adversarial markers without probabilistic guesswork.
  - RiskB Adjustment | Calibrated modifier applied to the baseline risk budget based on detected frictions.
- Glossary:
  - Adversarial Semiotics | The study of hidden or deceptive signs in digital artifacts.
  - PatternMatch | Data structure storing a detected instance: location, category, and integer severity.
  - SemioticPatternDetector | Core engine class.
  - Corpus | The 110+ case library used to validate detection rules.
  - SANS_FIND_EVIL_2026 | Forensic standard schema governing classification.
  - VIGÍA Pipeline | Integrated forensic analysis workflow.
- Scientific Note: Explain that terms from Peirce (abduction), Eco (semiotic theory), and Grice (cooperative principles / implicature) are formal analytical constructs, not mysticism. Use sensor analogy: just as a spectrometer identifies a compound by its unique absorption lines (deterministic signature matching), this detector identifies adversarial intent by unique "signatures" in text. The terminology describes the sensor's logic, not magical thinking.

ESPAÑOL:
- What Is This Module? -> "¿Qué es este módulo?"
- Similar content in Spanish.
- Key terms: Fricción semiótica, Lógica abdutiva, Artefacto textual, Puntuación determinista entera, Patrón regex, Ajuste RiskB.
- Glossary: Semiótica adversarial, PatternMatch, SemioticPatternDetector, Corpus, SANS_FIND_EVIL_2026, Pipeline VIGÍA.
- Scientific Note -> 【Nota Científica】
- Peirce/Eco/Grice terminology explanation.

РУССКИЙ:
- What Is This Module? -> "Что представляет собой этот модуль?"
- Key terms: Семиотическое трение, Абдуктивная логика, Текстуальный артефакт, Детерминированное целочисленное скорингование, Регулярное выражение, Корректировка RiskB.
- Note: Пирс/Эко/Грайс terminology.
- Sensor analogy: спектрометр.

中文:
- What Is This Module? -> "本模块是什么？"
- Key terms: 符号对抗模式 (adversarial semiotic patterns), 逻辑断裂 (semiotic friction / logical fracture), 溯因逻辑 (abductive logic), 取证工件 (textual artifact), 确定性整数评分 (deterministic integer scoring), 正则规则 (regex pattern), RiskB 校正 (RiskB adjustment).
- Glossary: 对抗符号学, 模式匹配 (PatternMatch), 符号模式检测器 (SemioticPatternDetector), 案例库 (Corpus), 标准模式, VIGÍA 流水线.
- Scientific Note -> 【科学说明】
- Sensor analogy: 传感器/光谱仪.


For English:
| Concept | Plain-Language Definition | Role in Forensic Analysis |
|---|---|---|
| Semiotic Friction | A detectable mismatch between what a text appears to say and what it actually encodes. | Flags potential adversarial tampering or deception. |
| Abductive Logic | Inference to the best explanation using hard-coded rules derived from known cases. | Bridges raw pattern matches to actionable hypotheses. |
| Textual Artifact | Any string or file undergoing forensic inspection (logs, configs, code). | The input material being analyzed. |
| Deterministic Integer Scoring | Risk values computed with exact whole-number arithmetic; no rounding, no probabilities. | Guarantees reproducible results across repeated analyses. |
| Regex Pattern | Symbolic search template that matches exact character sequences. | Performs the ground-truth detection without statistical guessing. |
| RiskB Adjustment | A calibrated integer modifier fed back into the risk budget engine. | Fine-tunes overall threat assessment based on textual evidence. |

For Spanish:
| Concepto | Definición en lenguaje sencillo | Papel en el análisis forense |
|---|---|---|
| Fricción semiótica | Discordancia detectable entre lo que un texto parece decir y lo que realmente codifica. | Señala posibles manipulaciones o engaños adversariales. |
| Lógica abdutiva | Inferencia a la mejor explicación mediante reglas derivadas de casos conocidos. | Conecta coincidencias de patrones con hipótesis accionables. |
| Artefacto textual | Cualquier cadena o archivo sometido a inspección forense. | Material de entrada del análisis. |
| Puntuación determinista de enteros | Valores de riesgo calculados con aritmética exacta de números enteros; sin redondeo ni probabilidades. | Garantiza resultados reproducibles en cada análisis. |
| Patrón regex | Plantilla de búsqueda simbólica que coincide con secuencias exactas de caracteres. | Realiza la detección fundamental sin conjeturas estadísticas. |
| Ajuste RiskB | Modificador entero calibrado que se reinyecta en el motor de presupuesto de riesgo. | Ajusta la evaluación global de amenazas según la evidencia textual. |

For Russian:
| Концепция | Определение простым языком | Роль в криминалистическом анализе |
|---|---|---|
| Семиотическое трение | Обнаружимое несоответствие между тем, что текст кажется сообщает, и тем, что он фактически кодирует. | Выявляет потенциальное противоборствующее вмешательство или обман. |
| Абдуктивная логика | Вывод наилучшего объяснения с помощью жёстко заданных правил, выведенных из известных случаев. | Связывает обнаруженные паттерны с действенными гипотезами. |
| Текстуальный артефакт | Любая строка или файл, подвергаемые криминалистической проверке. | Входной материал для анализа. |
| Детерминированное целочисленное скорингование | Значения риска, вычисляемые точной целочисленной арифметикой; без округления и вероятностей. | Гарантирует воспроизводимые результаты при повторных анализах. |
| Шаблон регулярного выражения | Символьная поисковая маска, находящая точные последовательности символов. | Выполняет достоверное обнаружение без статистических догадок. |
| Корректировка RiskB | Калиброванное целочисленное поправочное значение, передаваемое в движок риск-бюджета. | Уточняет общую оценку угрозы на основании текстовых доказательств. |

For Chinese:
| 概念 | 通俗定义 | 取证分析中的作用 |
|---|---|---|
| 对抗符号模式 | 文本意图表达与其编码信号之间的不一致模式。 | 标记潜在的对抗性篡改或欺骗行为。 |
| 逻辑断裂 | 文本表面含义与实际编码信息之间的可检测失配。 | 指示可能的对抗性操纵。 |
| 溯因逻辑 | 从已知案例中提取规则，推导出最佳解释的规则化推理。 | 将原始模式匹配转化为可操作的假设。 |
| 取证工件 | 接受取证检查的任何字符串或文件（日志、配置、脚本）。 | 被分析的输入材料。 |
| 确定性整数评分 | 使用精确整数运算计算的风险值；无舍入、无概率。 | 确保重复分析结果完全一致。 |
| 正则规则 | 匹配精确字符序列的符号化搜索模板。 | 在不依赖统计猜测的前提下完成基础检测。 |
| RiskB 校正 | 反馈至风险预算引擎的校准整数修正值。 | 根据文本证据微调整体威胁评估。 |



English Glossary:
- **Adversarial Semiotics**: The discipline of analyzing deceptive or concealed signs within digital objects.
- **PatternMatch**: A structured record of a detection event, containing position, category label, and integer severity.
- **SemioticPatternDetector**: The primary engine class that orchestrates regex scanning and abductive reasoning.
- **Corpus**: A validated collection of 110+ synthetic and real-world forensic cases used to derive and test detection rules.
- **SANS_FIND_EVIL_2026**: The governing forensic schema (v1.0) that standardizes classification and reporting formats.
- **VIGÍA Pipeline**: The integrated forensic workflow into which this module feeds its RiskB adjustments.
- **Deterministic Integer Arithmetic**: Mathematical operations using whole numbers only, producing exact, unambiguous outputs with no floating-point approximation.

Spanish Glossary:
- **Semiótica adversarial**: Disciplina que analiza signos engañosos u ocultos dentro de objetos digitales.
- **PatternMatch**: Registro estructurado de un evento de detección; contiene posición, etiqueta de categoría y severidad entera.
- **SemioticPatternDetector**: Clase motor principal que orquesta el escaneo regex y el razonamiento abdutivo.
- **Corpus**: Colección validada de más de 110 casos forenses (sintéticos y reales) para derivar y probar reglas.
- **SANS_FIND_EVIL_2026**: Esquema forense rector (v1.0) que estandariza clasificación y formatos de informe.
- **Pipeline VIGÍA**: Flujo de trabajo forense integrado que recibe los ajustes RiskB de este módulo.
- **Aritmética determinista de enteros**: Operaciones matemáticas con números enteros únicamente, que producen salidas exactas y sin aproximaciones de coma flotante.

Russian Glossary:
- **Адверсарная семиотика**: Дисциплина анализа дезинформирующих или скрытых знаков в цифровых объектах.
- **PatternMatch**: Структурированная запись события обнаружения, содержащая позицию, метку категории и целочисленную степень серьёзности.
- **SemioticPatternDetector**: Основной класс-движок, координирующий сканирование регулярными выражениями и абдуктивное рассуждение.
- **Корпус**: Проверенная совокупность 110+ синтетических и реальных криминалистических случаев для вывода и тестирования правил.
- **SANS_FIND_EVIL_2026**: Управляющая криминалистическая схема (v1.0), стандартизирующая классификацию и форматы отчётности.
- **Конвейер VIGÍA**: Интегрированный криминалистический рабочий процесс, получающий корректировки RiskB от данного модуля.
- **Детерминированная целочисленная арифметика**: Математические операции исключительно с целыми числами, дающие точные однозначные результаты без приближений с плавающей точкой.

Chinese Glossary:
- **对抗符号学**: 分析数字对象中欺骗性或隐藏符号的学科。
- **模式匹配 (PatternMatch)**: 存储检测事件的结构化记录，包含位置、类别标签与整数严重度。
- **符号模式检测器 (SemioticPatternDetector)**: 主引擎类，负责协调正则扫描与溯因推理。
- **案例库 (Corpus)**: 由 110 余个合成与真实取证案例组成的验证集合，用于推导与测试检测规则。
- **SANS_FIND_EVIL_2026**: 管理分类与报告格式的取证标准模式（v1.0）。
- **VIGÍA 流水线**: 接收本模块 RiskB 校正的集成取证工作流。
- **确定性整数运算**: 仅使用整数的数学运算，产生精确、无歧义的输出，不存在浮点近似。

Scientific Note content (to be translated):

Core message: Terminology from Charles Sanders Peirce (abductive inference), Umberto Eco (semiotic theory), and H. Paul Grice (cooperative maxims / implicature) are formal, rigorously defined analytical frameworks. They are not mysticism, esotericism, or anthropomorphism. 

Sensor analogy: Consider a mass spectrometer or an infrared spectrometer. It identifies a chemical compound not by "guessing" but by comparing observed absorption lines against a deterministic library of known signatures. When we say the spectrometer "infers" the presence of a compound, we do not mean it is thinking; we mean it executes a formal mapping from signal to category. Similarly, this module uses Peircean abduction as its logical architecture, Eco's sign theory to define what constitutes a meaningful mismatch, and Gricean maxims to encode expectations of normal communication. These are the "optics" and "calibration curves" of the detector. They describe how the sensor processes data, not a belief in supernatural forces.

Now translate into 4 languages.

English:
> 【Scientific Note】
> The terminology of Peirce (abductive inference), Eco (semiotic theory), and Grice (cooperative principles) is frequently misunderstood as philosophical mysticism. It is not. These are formal, mathematically operationalized frameworks—analogous to the calibration logic inside a spectrometer. A spectrometer does not “guess” a chemical; it matches observed absorption lines against a deterministic library of integer-indexed signatures. When this module “abduces” a pattern, it performs the same deterministic mapping: observed textual sign → known adversarial signature. Peirce provides the inference architecture, Eco defines the sign-mismatch library, and Grice supplies the baseline communication protocol against which deviation is measured. They are the instrument’s optics and firmware, not incantations.

Spanish:
> 【Nota Científica】
> La terminología de Peirce (inferencia abdutiva), Eco (teoría semiótica) y Grice (principios cooperativos) suele confundirse con misticismo filosófico. No lo es. Son marcos formales y matemáticamente operacionalizados, análogos a la lógica de calibración interna de un espectrómetro. Un espectrómetro no “adivina” un compuesto químico; compara líneas de absorción observadas contra una biblioteca determinista de firmas indexadas por enteros. Cuando este módulo “abduce” un patrón, realiza el mismo mapeo determinista: signo textual observado → firma adversarial conocida. Peirce aporta la arquitectura de inferencia, Eco define la biblioteca de desajustes de signos y Grice suministra el protocolo de comunicación base contra el cual se mide la desviación. Son la óptica y el firmware del instrumento, no conjuros.

Russian:
> 【Научное примечание】
> Терминология Пирса (абдуктивный вывод), Эко (семиотическая теория) и Грайса (кооперативные принципы) нередко ошибочно воспринимается как философский мистицизм. Это не так. Это формальные, математически операционализированные рамки, аналогичные логике калибровки внутри спектрометра. Спектрометр не «угадывает» химическое соединение; он сопоставляет наблюдаемые линии поглощения с детерминированной библиотекой сигнатур, индексированных целыми числами. Когда данный модуль «абдуцирует» паттерн, он выполняет то же детерминированное отображение: наблюдаемый текстовый знак → известная адверсарная сигнатура. Пирс задаёт архитектуру вывода, Эко определяет библиотеку несоответствий знаков, а Грайс предоставляет базовый коммуникационный протокол, относительно которого измеряется отклонение. Это оптика и прошивка прибора, а не заклинания.

Chinese:
> 【科学说明】
> 皮尔士（溯因推理）、艾柯（符号学理论）与格赖斯（合作原则）等术语常被误解为哲学神秘主义。事实并非如此。它们均为形式化、可数学操作的框架，类似于光谱仪内部的校准逻辑。光谱仪并非在“猜测”某种化学物质；而是将观测到的吸收谱线与一个以整数索引的确定性特征库进行比对。当本模块对某一模式进行“溯因”时，它执行的同样是确定性映射：观测到的文本符号 → 已知的对抗性特征。皮尔士提供了推理架构，艾柯定义了符号失配库，格赖斯则提供了用以衡量偏差的基准通信协议。它们是仪器的“光学系统”与“固件”，而非咒语。




In Chinese "What Is This Module?":
本模块是一个确定性取证引擎，用于扫描**取证工件**（文本形式的日志、配置、脚本等）中的对抗性符号模式。它不依赖机器学习或统计学方法，仅通过正则规则与溯因逻辑（基于规则的推理）进行检测。所有风险评分均采用**确定性整数运算**，确保完全可复现。该模块是 VIGÍA 流水线的一个组件，依据 SANS_FIND_EVIL_2026 标准（v1.0）运行，其规则库源自 110 余个合成与真实取证案例。

Key concepts table for Chinese:
Maybe:
| 概念 | 通俗定义 | 取证分析中的角色 |
|---|---|---|
| 逻辑断裂 | 文本表面含义与实际编码信息之间的可检测失配，常暗示对抗性篡改。 | 标记潜在的欺骗或操纵行为。 |
| 对抗符号模式 | 攻击者嵌入文本中的隐蔽欺骗性符号结构。 | 成为检测器识别的目标特征。 |
| 溯因逻辑 | 从已知案例提取规则，通过最佳解释进行推理的确定性机制。 | 将原始匹配结果转化为可操作的取证假设。 |
| 取证工件 | 接受 forensic 检查的任何字符串或文件。 | 被分析的输入对象。 |
| 确定性整数评分 | 仅使用整数运算得到的精确风险值；无概率、无舍入。 | 保证多次分析输出完全一致。 |
| 正则规则 | 精确匹配字符序列的符号化搜索模板。 | 在零统计猜测的前提下执行底层检测。 |
| RiskB 校正 | 反馈至风险预算引擎的校准整数修正值。 | 根据文本证据调整整体威胁评估。 |

Glossary:
- **对抗符号学**: 研究数字对象中欺骗性或隐藏符号的学科。
- **模式匹配 (PatternMatch)**: 存储检测事件的结构化记录，包含位置、类别标签与整数严重度。
- **符号模式检测器 (SemioticPatternDetector)**: 主引擎类，负责协调正则扫描与溯因推理。
- **案例库 (Corpus)**: 由 110 余个合成与真实取证案例组成的验证集合，用于推导与测试规则。
- **SANS_FIND_EVIL_2026**: 管理分类与报告格式的取证标准方案（v1.0）。
- **VIGÍA 流水线**: 接收本模块 RiskB 校正的集成取证工作流。
- **确定性整数运算**: 仅使用整数的数学运算，产生精确且无歧义的结果，不存在浮点近似。

Scientific Note Chinese:
> 【科学说明】
> 皮尔士（Charles Sanders Peirce，溯因推理）、艾柯（符号学理论）与格赖斯（合作原则）等术语常被误解为哲学神秘主义。事实并非如此。它们均为形式化、可数学操作的框架，类似于光谱仪内部的校准逻辑。光谱仪并非在“猜测”某种化学物质；而是将观测到的吸收谱线与一个以整数索引的确定性特征库进行比对。当本模块对某一模式进行“溯因”时，它执行的同样是确定性映射：观测到的文本符号 → 已知的对抗性特征。皮尔士提供了推理架构，艾柯定义了符号失配库，格赖斯则提供了用以衡量偏差的基准通信协议。它们是仪器的“光学系统”与“固件”，而非咒语。


Also need to make sure I don't use floating-point explanations. I explicitly mention deterministic integer arithmetic and no floating-point.







For each language:
## ENGLISH
### What Is This Module?
...
### Key Concepts
Table...
### Glossary
...
### 【Scientific Note】
...
---

Then repeat for other languages.


1. Target audience: scientists/researchers who do NOT know Python -> Yes, plain language, no "instantiate the class" but rather "the engine" or "the detector component".
2. Format: Markdown with 4 language sections -> Yes.
3. Each section includes:
   - "What Is This Module?" -> Yes.
   - Key concepts with tables -> Yes.
   - Glossary -> Yes.
   - 【科学说明】/【Scientific Note】 box -> Yes.
   - 艾柯: in note.
   - 格赖斯: in note.
   - 逻辑断裂: in table.
5. License line at the end.
6. NO floating-point math explanations. Emphasize deterministic integer arithmetic. -> Yes.



English:
- The module exposes two data structures and four operations. `PatternMatch` is the detection record. `SemioticPatternDetector` is the core engine. `analyze_text` examines a raw string. `analyze_artifact` performs full scoring on a file-like object. `detect_semiotic_frictions` is the high-level entry point for the VIGÍA pipeline, returning RiskB adjustments. `get_stats` reports corpus coverage metrics.



**ENGLISH — What Is This Module?**
`vigia/tools/pattern_detector.py` is a deterministic forensic engine designed to examine textual artifacts—such as system logs, configuration files, and scripts—for hidden adversarial patterns. It does not employ machine learning, statistical modeling, or any probabilistic reasoning. Instead, it relies on exact symbolic search rules (regular expressions) and abductive logic: a rule-based inference method that selects the best available explanation for an observed textual anomaly.

The module contains the following components:
- **PatternMatch**: A structured detection ticket that records where a pattern was found, what category it belongs to, and its integer severity level.
- **SemioticPatternDetector**: The central engine that scans input material, compares it against a validated library of 110+ forensic cases, and assigns risk scores using deterministic integer arithmetic only.
- **analyze_text**: An operation that inspects a raw character sequence for semiotic frictions.
- **analyze_artifact**: A comprehensive examination that produces a full integer-based score profile, a list of all PatternMatch records, and a dominant category label.
- **detect_semiotic_frictions**: The high-level gateway for the VIGÍA pipeline. It translates textual evidence into calibrated RiskB adjustments—integer modifiers that feed directly into the risk budget engine.
- **get_stats**: A reporting function that returns coverage metrics of the internal case library.

All scoring operations use whole-number mathematics. Given the same input, the module will always produce the same output, with no rounding errors or floating-point uncertainty.

This is good. Similar content for other languages.

Spanish:
`vigia/tools/pattern_detector.py` es un motor forense determinista diseñado para examinar artefactos textuales—como registros del sistema, archivos de configuración y scripts—en busca de patrones adversariales ocultos. No emplea aprendizaje automático, modelado estadístico ni razonamiento probabilístico. En su lugar, se basa en reglas de búsqueda simbólica exactas (expresiones regulares) y lógica abdutiva: un método de inferencia basado en reglas que selecciona la mejor explicación disponible para una anomalía textual observada.

El módulo contiene los siguientes componentes:
- **PatternMatch**: Un registro estructurado de detección que anota dónde se encontró un patrón, a qué categoría pertenece y su nivel de severidad entero.
- **SemioticPatternDetector**: El motor central que escanea el material de entrada, lo compara contra una biblioteca validada de más de 110 casos forenses y asigna puntuaciones de riesgo usando únicamente aritmética determinista de enteros.
- **analyze_text**: Operación que inspecciona una secuencia de caracteres en bruto en busca de fricciones semióticas.
- **analyze_artifact**: Examen comprehensivo que produce un perfil de puntuación completo basado en enteros, una lista de todos los registros PatternMatch y una etiqueta de categoría dominante.
- **detect_semiotic_frictions**: La puerta de entrada de alto nivel para el pipeline VIGÍA. Traduce la evidencia textual en ajustes RiskB calibrados—modificadores enteros que se inyectan directamente en el motor de presupuesto de riesgo.
- **get_stats**: Función de reporte que devuelve métricas de cobertura de la biblioteca interna de casos.

Todas las operaciones de puntuación usan matemáticas de números enteros. Dado el mismo insumo, el módulo siempre producirá el mismo resultado, sin errores de redondeo ni incertidumbre de coma flotante.

Russian:
`vigia/tools/pattern_detector.py` — это детерминированный криминалистический движок, предназначенный для исследования текстуальных артефактов—таких как системные журналы, файлы конфигурации и скрипты—на предмет скрытых адверсарных паттернов. Он не использует машинное обучение, статистическое моделирование или вероятностные рассуждения. Вместо этого он полагается на точные символьные правила поиска (регулярные выражения) и абдуктивную логику: метод rule-based вывода, который выбирает наилучшее доступное объяснение для наблюдаемой текстовой аномалии.

Модуль содержит следующие компоненты:
- **PatternMatch**: Структурированная запись обнаружения, фиксирующая местоположение паттерна, его категорию и целочисленный уровень серьёзности.
- **SemioticPatternDetector**: Центральный движок, который сканирует входной материал, сравнивает его с проверенной библиотекой более чем из 110 криминалистических случаев и назначает оценки риска исключительно с помощью детерминированной целочисленной арифметики.
- **analyze_text**: Операция, проверяющая необработанную последовательность символов на наличие семиотического трения.
- **analyze_artifact**: Комплексное исследование, формирующее полный профиль оценки на основе целых чисел, список всех записей PatternMatch и метку доминирующей категории.
- **detect_semiotic_frictions**: Высокоуровневый шлюз для конвейера VIGÍA. Преобразует
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
