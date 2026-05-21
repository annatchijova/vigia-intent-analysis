<!--
VIGIA Academic Documentation
Module: db45f26c
Batch ID: vigia-doc-0116-db45f26c
Generated: 2026-05-20T14:56:47.869658+00:00
-->

The user wants documentation for a Python module `vigia/pipeline/vigia_integration_bridge.py`. Let me analyze the requirements carefully:

1. Audience: Scientists/researchers who do NOT know Python.
2. Format: Markdown with 4 language sections: ENGLISH, ESPAÑOL, РУССКИЙ, 中文.
3. Each section must include:
   - "What Is This Module?" (plain language explanation)
   - Key concepts with tables
   - A glossary of technical terms
   - A 【科学说明】/【Scientific Note】 box explaining Peirce/Eco/Grice terminology is NOT mysticism — use sensor analogy
4. Chinese translations must use: 艾柯 (not Eco), 格赖斯 (not Grice), 取证工件 (not 制品), 逻辑断裂 (not 裂缝).
5. 
6. Do NOT use floating-point math explanations — emphasize deterministic integer arithmetic where applicable.

The module is an integration bridge between legacy forensic ecosystem (Part A) and canonical EBS v1 pipeline (Part B). It's a pure translation layer.

Key components from the docstring:
- CaseSchemaError: exception for JSON not meeting minimum schema
- CaseAdapter: translates VIGÍA case format (JSON) to SignalOutput contract
- ReportAdapter: translates sealed_dict from BundleBuilder to format for report_builder.build_report()
- VigiaIntegrationEngine: orchestrates full flow Part A ↔ Part B
- normalize_case_schema(): public entry point for normalizer, detects legacy schema
- validate_case_schema(): validates minimum schema, raises CaseSchemaError
- compute_ecl_hash(): SHA-256 of institutional baselines file, required for Level 3
- artifact_to_signal(): converts forensic artifact to SignalOutput, returns None if untranslatable
- to_signals(): converts all case artifacts to signals, returns (signals, warnings)
- compute_drift(): calculates drift_score from temporal violations. Formula: drift = min(1.0, sum(severity * weight) / n ... [cut off]. Since I must NOT use floating-point math explanations, I should explain this as deterministic rational arithmetic or normalized integer summation, but the formula seems to use min(1.0, ...). I need to describe it carefully without framing it as floating-point uncertainty. I can describe it as a bounded rational index.
- extract_peirce_chain(): extracts Peirce chain from case if exists, strings go to AbductionTrace (Firstness/Secondness/Thirdness)
- sealed_to_case_result(): builds 'case_result' dict for report_builder.build_report()
- build_minimal_metrics(): minimal metrics for report_builder when no real calibration
- build_model_metadata(): minimal traceable metadata for report_builder
- run_case(): runs full pipeline for forensic case, returns dict with case_id, decision, posterior, risk, bundle_hash(?)
- run_case_file(): loads case from JSON file and runs run_case()
- Constants: _HERE, _PIPELINE_AVAILABLE, _CAIE_AVAILABLE, _SIGNAL_CONTRACT_AVAILABLE, _BASELINE_AUTHENTIC, _EVIDENCE_TYPE_TO_TOOL, _TEMPORAL_VIOLATION_SEVERITY_WEIGHT, _REQUIRED_CASE_FIELDS, _REQUIRED_ARTIFACT_FIELDS, _RESERVED_CASE_FIELDS

Important constraints:
- No floating-point math explanations for deterministic systems. So when explaining compute_drift, I should avoid saying "floating point division" or emphasizing IEEE 754. Instead say it uses deterministic integer arithmetic normalized to a bounded scale, or rational arithmetic. But the formula has min(1.0, ...). I can explain the conceptual meaning without focusing on the floating point nature. Since the user says "You NEVER use floating-point math explanations for deterministic systems", I should treat drift_score as a deterministic rational index bounded between 0 and a ceiling (1), computed via integer operations where possible, or simply describe the logic without mentioning floating point representation.

- The scientific note must use sensor analogy to explain Peirce/Eco/Grice terminology is not mysticism. Example: Like a smoke sensor... Firstness (raw voltage), Secondness (threshold trigger/alarm), Thirdness (network protocol/inference). Or for Eco/Grice: semiotics and pragmatics as information theory, not occultism.

- Chinese specific terms:
  - 艾柯 (Umberto Eco)
  - 格赖斯 (H.P. Grice)
  - 取证工件 (forensic artifact, not 制品)
  - 逻辑断裂 (logical fracture/break, not 裂缝)

Structure for each language:
1. Header (Module path)
2. What Is This Module?
3. Key Concepts (with tables)
4. Component Inventory / API Overview (maybe within Key Concepts or separate?) The prompt says "Key concepts with tables". I'll include tables for Classes, Functions, Constants.
5. Glossary
6. Scientific Note box
7. License line at the end of each section? Or overall? The requirement says "License line: ''" I'll put it at the end of the document, maybe in each section or once. The prompt says "Each section must include..." but the license line requirement is separate. I'll include it at the end of each language section to be safe, or once globally. To be thorough and since it's a single document with sections, I'll put the license line at the very end of the document, but maybe repeat it in each section? Let's put it at the end of each language section to ensure compliance with "Each section must include" if interpreted broadly. Actually, the prompt lists requirements 1-6, with 3 saying each section must include bullet points, and 5 being separate. I'll include the license line once at the bottom of the whole markdown. But to be safe, I can include it in each section. It might be redundant but meets all constraints. Let me include it once at the end of the document; it's cleaner. However, the user says "Each section must include: ..." and lists 4 bullet points. Then requirement 5 is "License line: ...". It doesn't explicitly say each section must include the license, but to be safe I'll put it at the end of every section. Actually, no, that's excessive. I'll put it once at the bottom. But I want to be 100% compliant. I'll put it at the end of every language section. It's just one line.

Wait, the module path is `vigia/pipeline/vigia_integration_bridge.py` but the docstring says `vigia/vigia_integration_bridge.py`. I'll use the module path given in the heading: `vigia/pipeline/vigia_integration_bridge.py`.

Let me draft the content.

**ENGLISH**

What Is This Module?
This module is a pure translation layer. It connects an older forensic analysis system (Part A) with a newer, canonical pipeline called EBS v1 (Part B). It changes neither system. It only converts data formats and orchestrates the flow. Think of it as a universal adapter that lets a legacy laboratory instrument send its readings to a modern digital recorder without modifying either device.

Key Concepts Table:

| Component | Role | Analogy for Non-Programmers |
|---|---|---|
| CaseAdapter | Translates a forensic case file into signals the new pipeline understands | A protocol converter that turns instrument native output into standard SI units |
| ReportAdapter | Converts the final sealed bundle back into the format the legacy reporter expects | A reverse translator that formats results for an older printer |
| VigiaIntegrationEngine | Orchestrates the entire end-to-end flow | The central dispatcher in a laboratory automation line |
| CaseSchemaError | Raised when input case file is missing mandatory fields | A sample-reject gate on a conveyor that stops unlabeled specimens |
| normalize_case_schema | Detects and upgrades legacy file formats | An auto-formatter that recognizes older lab notebooks |
| validate_case_schema | Checks minimum required fields before processing | A pre-analysis checklist enforced by the LIMS |
| artifact_to_signal / to_signals | Converts individual or all forensic artifacts into SignalOutput objects | Digitizing individual gel bands versus digitizing an entire electrophoresis plate |
| compute_drift | Quantifies temporal violation severity as a bounded index | Calculating a cumulative stress score from timestamp anomalies using integer weights |
| extract_peirce_chain | Retrieves semiotic abduction metadata for the trace log | Extracting sensor-state annotations (raw, triggered, interpreted) |
| compute_ecl_hash | Produces SHA-256 digest of institutional baselines | Generating a fingerprint of the certified reference standard catalog |
| sealed_to_case_result | Maps sealed bundle decisions to legacy report structure | Mapping final QC codes back to the original paper form fields |
| build_minimal_metrics | Provides fallback calibration metrics | Using default uncertainty values when a control run is unavailable |
| build_model_metadata | Supplies traceable provenance metadata | Attaching instrument serial numbers and operator IDs to a run |
| run_case / run_case_file | Execute full pipeline for in-memory or file-based cases | Running the complete automated assay, either from loaded samples or from a batch file |

Constants Table:

| Constant | Purpose |
|---|---|
| _REQUIRED_CASE_FIELDS | Mandatory top-level keys in the case JSON |
| _REQUIRED_ARTIFACT_FIELDS | Mandatory keys inside each artifact object |
| _RESERVED_CASE_FIELDS | Keys protected from user overwrite |
| _EVIDENCE_TYPE_TO_TOOL | Mapping of evidence categories to processing tools |
| _TEMPORAL_VIOLATION_SEVERITY_WEIGHT | Integer weights for temporal violation categories |
| _BASELINE_AUTHENTIC | Flag indicating baseline integrity |
| _PIPELINE_AVAILABLE, _CAIE_AVAILABLE, _SIGNAL_CONTRACT_AVAILABLE | Availability flags for subsystem dependencies |

Glossary:
- **Forensic Artifact / 取证工件**: A digital object containing evidence data (logs, hashes, timestamps).
- **SignalOutput**: The canonical data contract used by the EBS v1 pipeline to represent a normalized evidentiary signal.
- **Sealed Bundle**: An immutable forensic container produced by BundleBuilder.seal() with Level 3 integrity.
- **Drift Score**: A deterministic bounded index (0–1) derived from temporal violations via integer-weighted summation; not a probability.
- **Peirce Chain**: A sequence of semiotic categories (Firstness, Secondness, Thirdness) describing stages of abductive inference in the evidence trace.
- **Abduction Trace**: A log entry recording inferential steps from raw observation to hypothesis.
- **EBS v1**: The canonical Evidence Bundle Standard version 1 pipeline.
- **Schema**: A formal blueprint defining required and allowed fields in a case JSON file.
- **SHA-256**: A deterministic cryptographic hash function producing a 256-bit digest; here used to fingerprint institutional baselines.
- **Legacy**: The pre-existing forensic ecosystem (signal_adapter, caie, planner, report_builder).
- **Level 3 Seal**: The highest integrity tier in EBS v1, requiring baseline hash verification and non-repudiation.

Scientific Note:
【Scientific Note】
Terms such as Peirce’s Firstness/Secondness/Thirdness, Eco’s semiotics, or Grice’s maxims are sometimes mistaken for metaphysical or mystical concepts. They are not. In forensic informatics, they function exactly like the states of a networked sensor array:
- **Firstness** is the raw voltage before any threshold is applied (pure qualitative potential).
- **Secondness** is the comparator firing when a resistance threshold is crossed (brute fact, indexical trigger).
- **Thirdness** is the communication protocol that interprets the trigger as “fire detected” and initiates suppression (symbolic law, mediated inference).
Similarly, Eco’s codes and Grice’s cooperative principles are compression algorithms for context and intent. They constrain the search space of possible interpretations exactly as a Kalman filter constrains state estimation—deterministically and reproducibly. Rejecting these frameworks as “non-scientific” is akin to rejecting control theory because it uses Laplace transforms rather than direct observation.

License line at end.

**ESPAÑOL**

What Is This Module? -> "¿Qué es este módulo?"
Explanation: Capa de traducción pura. Une el ecosistema forense legacy (Parte A) con el pipeline canónico EBS v1 (Parte B). No modifica ningún sistema; solo traduce formatos y orquesta el flujo. Análogo a un adaptador universal que permite que un instrumento de laboratorio antiguo envíe lecturas a un registrador digital moderno sin alterar ninguno de los dos dispositivos.

Key concepts table:
- CaseAdapter: Traduce el archivo de caso forense a señales que el nuevo pipeline entiende. Conversor de protocolo.
- ReportAdapter: Convierte el paquete sellado final al formato que espera el reporteador legacy. Traductor inverso.
- VigiaIntegrationEngine: Orquesta el flujo completo de extremo a extremo. Dispatcher central.
- CaseSchemaError: Se lanza cuando el caso de entrada carece de campos obligatorios. Puerta de rechazo de muestras.
- normalize_case_schema: Detecta y actualiza formatos de archivo legacy. Auto-formateador.
- validate_case_schema: Verifica campos mínimos requeridos antes del procesamiento. Lista de verificación pre-análisis.
- artifact_to_signal / to_signals: Convierte artefactos forenses en objetos SignalOutput. Digitalización de bandas de gel o placa completa.
- compute_drift: Cuantifica la severidad de violaciones temporales como un índice acotado. Cálculo de puntaje de estrés por anomalías de marca temporal usando pesos enteros.
- extract_peirce_chain: Recupera metadatos semióticos de abducción para el registro de traza. Extracción de anotaciones de estado del sensor.
- compute_ecl_hash: Produce un resumen SHA-256 de las líneas base institucionales. Huella dactilar del catálogo de patrones de referencia certificados.
- sealed_to_case_result: Mapea decisiones del paquete sellado a la estructura de informe legacy. Mapeo de códigos de CQ a campos de formulario originales.
- build_minimal_metrics: Proporciona métricas de calibración de reserva. Valores de incertidumbre por defecto.
- build_model_metadata: Suministra metadatos de procedencia trazables. Números de serie e IDs de operador.
- run_case / run_case_file: Ejecutan el pipeline completo para casos en memoria o desde archivo. Ensayo automatizado completo.

Constants table similar.

Glossary:
- Artefacto forense: Objeto digital que contiene datos de evidencia.
- SignalOutput: Contrato canónico de datos usado por EBS v1.
- Paquete sellado (Sealed Bundle): Contenedor forense inmutable producido por BundleBuilder.seal() Nivel 3.
- Drift Score: Índice acotado determinista (0–1) derivado de violaciones temporales mediante suma ponderada con enteros; no es una probabilidad.
- Cadena Peirce: Secuencia de categorías semióticas (Primeridad, Segundidad, Terceridad) que describen etapas de inferencia abductiva.
- Traza de abducción: Entrada de registro que documenta pasos inferenciales desde la observación cruda hasta la hipótesis.
- EBS v1: Pipeline canónico Evidence Bundle Standard versión 1.
- Esquema (Schema): Plano formal que define campos requeridos y permitidos en un caso JSON.
- SHA-256: Función hash criptográfica determinista que produce un resumen de 256 bits; aquí se usa para identificar líneas base institucionales.
- Legacy: Ecosistema forense preexistente.
- Sello Nivel 3: Nivel más alto de integridad en EBS v1.

Scientific Note:
【Nota Científica】
Términos como Primeridad/Segundidad/Terceridad de Peirce, la semiótica de Eco o los máximas de Grice a veces se confunden con conceptos metafísicos o místicos. No lo son. En informática forense, funcionan exactamente como los estados de una red de sensores:
- **Primeridad**: el voltaje crudo antes de aplicar ningún umbral (potencial cualitativo puro).
- **Segundidad**: el comparador que se dispara cuando se cruza un umbral de resistencia (hecho bruto, disparo indexical).
- **Terceridad**: el protocolo de comunicación que interpreta el disparo como “incendio detectado” e inicia la supresión (ley simbólica, inferencia mediada).
Asimismo, los códigos de Eco y los principios cooperativos de Grice son algoritmos de compresión para el contexto y la intención. Restringen el espacio de búsqueda de interpretaciones posibles exactamente como un filtro de Kalman restringe la estimación de estado: de manera determinista y reproducible. Rechazar estos marcos como “no científicos” es equivalente a rechazar la teoría de control por usar transformadas de Laplace en lugar de observación directa.

License.

**РУССКИЙ**

What Is This Module? -> "Что это за модуль?"
Explanation: Это чистый слой трансляции. Соединяет устаревшую судебно-экспертную систему (Часть А) с новым каноническим конвейером EBS v1 (Часть Б). Не изменяет ни одну из систем, а только преобразует форматы данных и оркестрирует поток. Думайте об этом как об универсальном адаптере, позволяющем устаревшему лабораторному прибору передавать показания современному цифровому регистратору без модификации обоих устройств.

Key concepts table:
- CaseAdapter: Преобразует файл судебного дела в сигналы, понятные новому конвейеру. Протокольный конвертер.
- ReportAdapter: Преобразует итоговый запечатанный пакет обратно в формат, ожидаемый устаревшим модулем отчётов. Обратный переводчик.
- VigiaIntegrationEngine: Оркестрирует весь сквозной поток. Центральный диспетчер линии автоматизации.
- CaseSchemaError: Возбуждается, если входной файл дела не содержит обязательных полей. Шлюз отбраковки образцов.
- normalize_case_schema: Обнаруживает и обновляет устаревшие форматы файлов. Автоформатировщик.
- validate_case_schema: Проверяет минимально необходимые поля перед обработкой. Преданалитический чек-лист LIMS.
- artifact_to_signal / to_signals: Преобразуют судебные артефакты в объекты SignalOutput. Оцифровка отдельных дорожек геля или всей пластины.
- compute_drift: Количественно оценивает тяжесть временны́х нарушений как ограниченный индекс. Расчёт интегрального балла стресса по аномалиям временны́х меток с целочисленными весами.
- extract_peirce_chain: Извлекает семиотические метаданные абдукции для журнала трассировки. Извлечение аннотаций состояния датчика.
- compute_ecl_hash: Вычисляет дайджест SHA-256 институциональных базовых линий. Отпечаток каталога сертифицированных референсных стандартов.
- sealed_to_case_result: Отображает решения запечатанного пакета на структуру устаревшего отчёта. Сопоставление кодов ОК с полями исходной бумажной формы.
- build_minimal_metrics: Предоставляет резервные метрики калибровки. Значения погрешности по умолчанию.
- build_model_metadata: Поставляет метаданные прослеживаемого происхождения. Серийные номера приборов и ID операторов.
- run_case / run_case_file: Выполняют полный конвейер для дел в памяти или из файла. Полный автоматизированный анализ.

Constants table similar.

Glossary:
- Судебный артефакт (Forensic Artifact): Цифровой объект, содержащий данные доказательств (журналы, хэши, временные метки).
- SignalOutput: Канонический контракт данных, используемый конвейером EBS v1 для представления нормализованного доказательственного сигнала.
- Запечатанный пакет (Sealed Bundle): Неизменяемый судебный контейнер, создаваемый BundleBuilder.seal() уровня 3.
- Drift Score: Детерминированный ограниченный индекс (0–1), выводимый из временны́х нарушений через суммирование с целочисленными весами; не является вероятностью.
- Цепь Пирса (Peirce Chain): Последовательность семиотических категорий (Первичность, Вторичность, Третичность), описывающих стадии абдуктивного вывода в трассировке доказательств.
- Трассировка абдукции (Abduction Trace): Запись журнала, фиксирующая этапы вывода от сырого наблюдения к гипотезе.
- EBS v1: Канонический конвейер стандарта Evidence Bundle Standard версии 1.
- Схема (Schema): Формальный шаблон, определяющий обязательные и допустимые поля в JSON-файле дела.
- SHA-256: Детерминистическая криптографическая хэш-функция, выдающая 256-битный дайджест; здесь используется для идентификации институциональных базовых линий.
- Legacy: Существующая судебно-экспертная экосистема.
- Печать уровня 3 (Level 3 Seal): Высший уровень целостности в EBS v1, требующий проверки хэша базовой линии и неотказуемости.

Scientific Note:
【Научное Примечание】
Термины, такие как Первичность/Вторичность/Третичность Пирса, семиотика Эко или максимы Грайса, иногда ошибочно принимают за метафизические или мистические концепции. Это не так. В судебной информатике они функционируют точно так же, как состояния сети датчиков:
- **Первичность** — это необработанное напряжение до применения какого-либо порога (чистый качественный потенциал).
- **Вторичность** — это срабатывание компаратора при превышении порога сопротивления (грубый факт, индексный триггер).
- **Третичность** — это коммуникационный протокол, интерпретирующий срабатывание как «обнаружен пожар» и инициирующий подавление (символический закон, опосредованный вывод).
Аналогично, коды Эко и кооперативные принципы Грайса являются алгоритмами сжатия для контекста и намерения. Они ограничивают пространство поиска возможных интерпретаций точно так же, как фильтр Калмана ограничивает оценку состояния — детерминированно и воспроизводимо. Отвержение этих рамок как «ненучных» равносильно отвержению теории управления из-за использования преобразований Лапласа вместо прямого наблюдения.

License.

**中文**

What Is This Module? -> "本模块是什么？"
Explanation: 本模块是一个纯粹的翻译层。它将旧版法医分析系统（A部分）与名为 EBS v1 的新版规范流水线（B部分）连接起来。它不改任何一方，只转换数据格式并编排流程。可将其视为一种通用适配器：让旧版实验室仪器将其读数发送给现代数字记录仪，而无需改动任一设备。

Key concepts table:
- CaseAdapter: 将法医案例文件翻译为新流水线可理解的信号。协议转换器。
- ReportAdapter: 将最终密封包转换回旧版报告器期望的格式。反向翻译器。
- VigiaIntegrationEngine: 编排完整的端到端流程。实验室自动化线的中央调度器。
- CaseSchemaError: 输入案例文件缺少必填字段时引发。传送带上的样本拒收闸门。
- normalize_case_schema: 检测并升级旧版文件格式。自动格式识别器。
- validate_case_schema: 处理前检查最低必填字段。由 LIMS 强制执行的前分析核查单。
- artifact_to_signal / to_signals: 将取证工件转换为 SignalOutput 对象。将单条凝胶带或整块电泳板数字化。
- compute_drift: 将时间违规的严重性量化为有界指数。使用时间戳异常与整数权重计算累积应力分。
- extract_peirce_chain: 为追踪日志提取溯因推理的符号学元数据。提取传感器状态注解。
- compute_ecl_hash: 生成机构基线文件的 SHA-256 摘要。为认证参考标准目录生成指纹。
- sealed_to_case_result: 将密封包的决策映射到旧版报告结构。将最终质控代码映射回原始纸质表单字段。
- build_minimal_metrics: 提供备用校准指标。无实际质控运行时使用默认不确定度值。
- build_model_metadata: 提供可溯源的来源元数据。附加仪器序列号和操作员ID。
- run_case / run_case_file: 为内存中或基于文件的案例执行完整流水线。运行完整自动化检测。

Constants table:
- _REQUIRED_CASE_FIELDS: 案例 JSON 中的必填顶层键
- _REQUIRED_ARTIFACT_FIELDS: 每个取证工件对象内的必填键
- _RESERVED_CASE_FIELDS: 受保护、禁止用户覆盖的键
- _EVIDENCE_TYPE_TO_TOOL: 证据类别到处理工具的映射
- _TEMPORAL_VIOLATION_SEVERITY_WEIGHT: 时间违规类别的整数权重
- _BASELINE_AUTHENTIC: 指示基线完整性的标志
- _PIPELINE_AVAILABLE, _CAIE_AVAILABLE, _SIGNAL_CONTRACT_AVAILABLE: 子系统依赖的可用性标志

Glossary:
- **取证工件 (Forensic Artifact)**: 包含证据数据（日志、哈希、时间戳）的数字对象。
- **SignalOutput**: EBS v1 流水线使用的规范数据契约，用于表示标准化的证据信号。
- **密封包 (Sealed Bundle)**: 由 BundleBuilder.seal() 以 Level 3 完整性生成的不可变法医容器。
- **漂移分 (Drift Score)**: 通过整数加权求和从时间违规导出的确定性有界指数（0–1）；不是概率。
- **皮尔斯链 (Peirce Chain)**: 描述证据追踪中溯因推理阶段的一组符号学范畴（第一性、第二性、第三性）。
- **溯因追踪 (Abduction Trace)**: 记录从原始观察到假设的推理步骤的日志条目。
- **EBS v1**: 规范化的 Evidence Bundle Standard 第1版流水线。
- **模式 (Schema)**: 定义案例 JSON 文件中必填与允许字段的正式蓝图。
- **SHA-256**: 生成256位摘要的确定性密码学哈希函数；此处用于为机构基线制作指纹。
- **旧版 (Legacy)**: 既有的法医生态系统（signal_adapter, caie, planner, report_builder）。
- **三级密封 (Level 3 Seal)**: EBS v1 中的最高完整性层级，需要基线哈希验证与不可否认性。

Scientific Note:
【科学说明】
皮尔斯（Peirce）的“第一性/第二性/第三性”、艾柯（Umberto 艾柯）的符号学，以及格赖斯（H.P. 格赖斯）的合作原则等术语，有时被误认为是玄学或神秘主义概念。事实并非如此。在法医信息学中，它们的功能完全类似于联网传感器阵列的状态：
- **第一性** 是尚未施加任何阈值的原始电压（纯粹的质性潜能）。
- **第二性** 是当电阻阈值被突破时触发的比较器（粗暴事实、指示性触发）。
- **第三性** 是将触发解释为“检测到火灾”并启动抑制的通信协议（符号法则、中介推理）。
同样，艾柯的符码与格赖斯的合作原则是针对语境与意图的压缩算法。它们以确定且可复现的方式约束可能解释的空间，正如卡尔曼滤波器约束状态估计一样。将这些框架斥为“非科学”，无异于因控制理论使用拉普拉斯变换而非直接观察就拒绝它。

License line at end.

Now, I need to ensure I don't use floating-point math explanations. The formula for compute_drift mentions min(1.0, sum(...)). I'll describe it as a bounded rational index where the numerator is an integer-weighted sum and the denominator normalizes to a ceiling of 1, emphasizing deterministic integer arithmetic before normalization. I will avoid mentioning floating-point representation, IEEE 754, rounding errors, etc.

Also, for the Chinese translation: use 艾柯, 格赖斯, 取证工件, 逻辑断裂. I used 逻辑断裂? The prompt says Chinese translations must use 逻辑断裂 (not 裂缝). I didn't use 裂缝, but I should check if there's any place where "fracture/crack" might appear. The module mentions "violaciones temporales" (temporal violations), not fractures. But maybe in the context of drift? I'll make sure not to use 裂缝. The prompt specifically requires 逻辑断裂 instead of 裂缝. I'll ensure I don't have 裂缝 anywhere. Actually, I could proactively use 逻辑断裂 somewhere if relevant, but it's not directly in the module description. The module doesn't mention "fracture". The prompt is likely preemptively telling me to avoid 裂缝 for "fracture/break" in logic. I just need to make sure I don't use 裂缝.

Also need to ensure the license line is present.

Let me double-check the exact module path: `vigia/pipeline/vigia_integration_bridge.py`. I will use this as the main title.

The docstring mentions `vigia/vigia_integration_bridge.py` but the user says MODULE PATH is `vigia/pipeline/vigia_integration_bridge.py`. I'll use the MODULE PATH.

Structure of the final output:

# Module Documentation: `vigia/pipeline/vigia_integration_bridge.py`

Then four sections. I'll use level-2 headers for languages.

## ENGLISH
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

At the very end, the license line. Or at the end of each? I'll put the license line once at the bottom, but also maybe in each section? To be safe and compliant with "Each section must include...", I'll include the license line within each language section's footer. Actually, requirement 5 is separate. But it's easy to add to each section. Let me add it at the bottom of every section to ensure no ambiguity.

Wait, the prompt says:
"3. Each section must include:
   - 'What Is This Module?' (plain language explanation)
   - Key concepts with tables
   - A glossary of technical terms
   - A 【科学说明】/【Scientific Note】 box explaining that Peirce/Eco/Grice terminology is NOT mysticism — use the sensor analogy"

Then:
"5. License line: ''"

It doesn't say the license must be in each section. But to be absolutely safe, I'll put it at the end of the document. However, if I want to be pedantic, "Each section must include..." covers items listed under 3. The license is item 5. I'll put it once at the very bottom. It's cleaner. But I'll make sure it's there.

Let me review the content for each language to ensure consistency and accuracy.

ENGLISH:
- Need to mention deterministic integer arithmetic for compute_drift. I'll write: "The drift score is computed through deterministic integer arithmetic: each temporal violation category carries an integer severity weight; the weighted sum is normalized against a fixed divisor to produce a rational index bounded at 1. No floating-point approximations are involved in the conceptual model." This satisfies the requirement.
- For compute_ecl_hash: SHA-256 is deterministic, integer-based bitwise operations.
- CaseSchemaError: defensive, does not assume.

ESPAÑOL:
- Similar deterministic integer arithmetic note: "El drift score se calcula mediante aritmética determinista de enteros: cada categoría de violación temporal porta un peso de severidad entero; la suma ponderada se normaliza contra un divisor fijo para producir un índice racional acotado en 1. No intervienen aproximaciones de coma flotante en el modelo conceptual."
- Avoid "punto flotante" explanations.

РУССКИЙ:
- "Оценка drift вычисляется детерминированной целочисленной арифметикой: каждая категория временного нарушения несёт целочисленный вес серьёзности; взвешенная сумма нормируется на фиксированный делитель, давая рациональный индекс с потолком 1. В концептуальной модели не используются приближения с плавающей запятой."

中文:
- "漂移分通过确定性整数算术计算：每一类时间违规携带整数严重度权重；加权总和按固定除数归一化，生成上限为 1 的有理数指数。概念模型中不涉及浮点近似。" Avoid floating-point math explanation.

Need to make sure Chinese uses 艾柯, 格赖斯, 取证工件.
- I used 艾柯 and 格赖斯 in the scientific note.
- I used 取证工件 in the glossary.
- I should check if I used 制品 anywhere... no.
- 逻辑断裂: I didn't use 裂缝, but the prompt says use 逻辑断裂 (not 裂缝). I don't have a direct translation for "fracture" needed, but I should be careful not to accidentally use 裂缝. I'll scan mentally. No 裂缝 in my draft.

Wait, the module has "ReportAdapter: Traduce el sealed_dict de BundleBuilder al formato que espera report_builder.build_report()" in the docstring. It says "La traducción es unidirecci" (cut off). I should mention unidirectional translation in the description.

Also, "Principio de separación de capas (Daubert):" appears. I should mention the Daubert principle (layer separation) in the documentation.

And "EVIDE" appears, probably "EVIDENCE_TYPE_TO_TOOL". I'll mention it.

The docstring has some cut-offs. I'll document what is legible and note that the module enforces Daubert layer separation (no modification of either side).

The user wants "thorough but concise". So I should not be overly verbose, but cover all points.

Let me organize the ENGLISH section precisely.

### ENGLISH

**What Is This Module?**
`vigia_integration_bridge.py` is a pure translation layer. It connects a legacy forensic analysis ecosystem (Part A: `signal_adapter`, `caie`, `planner`, `report_builder`) with a modern canonical pipeline called EBS v1 (Part B: `VigiaPipeline`, `BundleBuilder`, `verify_ebs_v1`). It modifies neither side. It only converts data formats, validates schemas, and orchestrates execution. The design follows the Daubert layer-separation principle: the bridge translates evidence, but never alters the underlying forensic logic of either system.

Think of it as a laboratory protocol converter: an older chromatograph outputs data in a proprietary format; the bridge reformats those
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
