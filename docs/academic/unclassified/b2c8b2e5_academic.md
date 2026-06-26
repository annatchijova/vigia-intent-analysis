<!--
VIGIA Academic Documentation
Module: b2c8b2e5
Batch ID: vigia-doc-0093-b2c8b2e5
Generated: 2026-05-20T14:56:47.864631+00:00
-->

## ENGLISH

### What Is This Module?
VIGIA (Visual Intentionality Audit) is a deterministic forensic engine for verifying image and document authenticity. It treats every image as a structured grid of integer pixel values. The module compares visual elements—seals, signatures, backgrounds—against expected deterministic patterns. When a forgery introduces a collage, pasted seal, or resolution mismatch, the engine registers a **structural incongruence**. It applies deterministic algorithms—integer-based local variance analysis over fixed 32×32 windows and discrete cosine transform (DCT) coefficient inspection—to yield repeatable, reproducible findings. Two classes orchestrate the analysis: `ForensicImageAnalyzer` (main pipeline) and `CLIPVisualAuditor` (zero-shot semantic classification).

### Key Concepts

| Term | Plain-Language Definition | Scientific Role |
|---|---|---|
| Intentionality Dissonance | A conflict between an image's claimed origin (e.g., official scan) and its structural production evidence. | Primary detection target; indicates probable fabrication. |
| Digital Perfection Anomaly | An unnatural uniformity or unexpected variance in a region that should share a single acquisition history. | Detected via deterministic 32×32 integer-window variance. |
| Compression Artifact Profile | The deterministic fingerprint left by lossy compression on 8×8 pixel blocks. | Reveals splicing from sources with different compression histories. |
| CAIE Integration | Automatic injection of detected forgeries as **logic fractures** into the Cross-Artifact Incongruence Engine. | Guarantees traceability in multi-tool investigative workflows. |
| Silent Metadata Analysis | Non-destructive extraction and deterministic parsing of EXIF/XMP tags. | Surfaces software tampering indicators and editing history. |
| Zero-Shot Classification | Semantic categorization without prior training on labeled forgeries. | Provides categorical context using discrete class mappings. |
| Deterministic Integer Arithmetic | Operations on whole numbers that return identical outputs for identical inputs, free from rounding error. | Foundation of all measurable forensic operations in this module. |
| Expected PNG Keys (`_EXPECTED_PNG_KEYS`) | A deterministic checklist of mandatory metadata tags used to validate PNG provenance. | Serves as a baseline for detecting missing or manipulated structural metadata. |

### Glossary

| Term | Definition |
|---|---|
| **Local Variance (32×32 Window)** | A measure of pixel dispersion computed by summing integer squared deviations across fixed blocks of 32 by 32 pixels. |
| **DCT Coefficient** | An integer value (post-quantization) from the Discrete Cosine Transform of an 8×8 block; boundary inconsistencies indicate splicing. |
| **EXIF/XMP** | Embedded metadata dictionaries recording camera settings, software, and edit history; parsed as structured text. |
| **Forensic Fracture (Logic Fracture)** | A formal record of a detected anomaly representing a break in the expected provenance chain. |
| **Singleton** | A design pattern ensuring one auditor instance exists system-wide, maintaining consistent investigative state. |
| **ForensicImageAnalyzer** | Main class that orchestrates pixel-level analysis, metadata parsing, and CAIE fracture export. |
| **CLIPVisualAuditor** | Class providing zero-shot semantic classification via discrete categorical mappings. |

> **【Scientific Note】**
> This module employs terminology from Charles Sanders Peirce, Umberto Eco, and H.P. Grice—scholars who formalized how signs convey meaning. References to *intentionality*, *dissonance*, or *codes* denote technical observables, not metaphysical forces. Consider Peirce's triad (sign–object–interpretant) as a transduction protocol: the image file is the sign, the physical document it purports to be is the object, and the deterministic integer output is the interpretant. Eco's codes function like communication-protocol layers; Grice's Cooperative Principle operates as a sensor baseline—violations register as discrete anomalies, precisely as a barometer flags pressure deviations. The "magic" is rigorous integer arithmetic, not mysticism.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## ESPAÑOL

### ¿Qué es este módulo?
VIGIA (Auditoría de Intencionalidad Visual) es un motor forense determinista para verificar la autenticidad de imágenes y documentos digitalizados. Trata cada imagen como una cuadrícula estructurada de valores de píxeles enteros. El módulo compara elementos visuales—sellos, firmas, fondos—contra patrones deterministas esperados. Cuando un falsificador introduce un collage, un sello pegado o una discrepancia de resolución, el motor registra una **incongruencia estructural**. Aplica algoritmos deterministas—análisis de varianza local basado en enteros sobre ventanas fijas de 32×32 e inspección de coeficientes de transformada discreta de coseno (DCT)—para producir hallazgos repetibles y reproducibles. Dos clases orquestan el análisis: `ForensicImageAnalyzer` (tubería principal) y `CLIPVisualAuditor` (clasificación semántica sin entrenamiento previo).

### Conceptos Clave

| Término | Definición en lenguaje sencillo | Rol científico |
|---|---|---|
| Discrepancia intencional | Conflicto entre el origen que reclama una imagen (p. ej., escaneo oficial) y la evidencia estructural de su producción. | Objetivo principal de detección; indica fabricación probable. |
| Anomalía de perfección digital | Uniformidad antinatural o varianza inesperada en una región que debería tener una única historia de adquisición. | Detectada mediante varianza determinista en ventanas enteras de 32×32. |
| Perfil de artefactos de compresión | Huella determinista que deja la compresión con pérdida en bloques de 8×8 píxeles. | Revela empalmes de fuentes con historiales de compresión distintos. |
| Integración CAIE | Inyección automática de falsificaciones detectadas como **fracturas lógicas** en el Motor de Incongruencia Cruzada entre Artefactos. | Garantiza trazabilidad en flujos de trabajo multi-herramienta. |
| Análisis silencioso de metadatos | Extracción no destructiva y análisis determinista de etiquetas EXIF/XMP. | Expone indicadores de manipulación por software e historial de edición. |
| Clasificación sin entrenamiento previo | Categorización semántica sin entrenamiento previo sobre falsificaciones etiquetadas. | Provee contexto categórico mediante mapeos discretos de clases. |
| Aritmética entera determinista | Operaciones sobre números enteros que devuelven idénticos resultados ante idénticas entradas, sin error de redondeo. | Fundamento de todas las operaciones forenses mensurables de este módulo. |
| Claves PNG esperadas (`_EXPECTED_PNG_KEYS`) | Lista de verificación determinista de etiquetas de metadatos obligatorias para validar la procedencia PNG. | Sirve como línea base para detectar metadatos estructurales faltantes o manipulados. |

### Glosario

| Término | Definición |
|---|---|
| **Varianza local (ventana 32×32)** | Medida de dispersión de píxeles calculada sumando desviaciones cuadradas enteras en bloques fijos de 32×32 píxeles. |
| **Coeficiente DCT** | Valor entero (post-cuantización) proveniente de la Transformada Discreta de Coseno de un bloque 8×8; inconsistencias en los límites indican empalme. |
| **EXIF/XMP** | Diccionarios de metadatos incrustados que registran ajustes de cámara, software e historial de edición; analizados como texto estructurado. |
| **Fractura forense (fractura lógica)** | Registro formal de una anomalía detectada que representa una ruptura en la cadena de procedencia esperada. |
| **Singleton** | Patrón que garantiza una única instancia del auditor en el sistema, manteniendo estado consistente en la investigación. |
| **ForensicImageAnalyzer** | Clase principal que orquesta el análisis a nivel de píxel, el análisis de metadatos y la exportación de fracturas CAIE. |
| **CLIPVisualAuditor** | Clase que provee clasificación semántica sin entrenamiento previo mediante mapeos discretos de clases. |

> **【Nota Científica】**
> Este módulo utiliza terminología de Charles Sanders Peirce, Umberto Eco y H.P. Grice—estudiosos que formalizaron cómo los signos transmiten significado. Las referencias a *intencionalidad*, *discrepancia* o *códigos* denotan observables técnicos, no fuerzas metafísicas. Considere la tríada de Peirce (signo–objeto–interpretante) como un protocolo de transducción: el archivo de imagen es el signo, el documento físico que pretende ser es el objeto, y la salida determinista en enteros es el interpretante. Los códigos de Eco funcionan como capas de protocolo de comunicación; el Principio de Cooperación de Grice opera como una línea base de sensor—las violaciones se registran como anomalías discretas, exactamente como un barómetro señala desviaciones de presión. La "magia" es una aritmética entera rigurosa, no misticismo.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## РУССКИЙ

### Что это за модуль?
VIGIA (Визуальный аудит интенциональности) — это детерминированный судебно-экспертный движок для проверки подлинности изображений и отсканированных документов. Каждое изображение рассматривается как структурированная сетка целочисленных значений пикселей. Модуль сравнивает визуальные элементы — печати, подписи, фон — с ожидаемыми детерминированными шаблонами. Когда подделка вносит коллаж, наклеенную печать или несоответствие разрешения, движок регистрирует **структурное несоответствие**. Применяются детерминированные алгоритмы — целочисленный анализ локальной дисперсии в фиксированных окнах 32×32 и проверка коэффициентов дискретного косинусного преобразования (ДКП) — для получения воспроизводимых результатов. Анализ организован двумя классами: `ForensicImageAnalyzer` (основной конвейер) и `CLIPVisualAuditor` (семантическая классификация).

### Ключевые концепции

| Термин | Определение простым языком | Научная роль |
|---|---|---|
| Диссонанс интенциональности | Конфликт между заявленным происхождением изображения (например, официальное сканирование) и структурными признаками его создания. | Основная цель обнаружения; указывает на вероятную фальсификацию. |
| Аномалия цифрового совершенства | Неприродная однородность или неожиданная дисперсия в области, которая должна иметь единую историю получения. | Обнаруживается детерминированным целочисленным анализом в окнах 32×32. |
| Профиль артефактов сжатия | Детерминированный отпечаток, оставляемый сжатием с потерями на блоках 8×8 пикселей. | Выявляет склейку из источников с разной историей сжатия. |
| Интеграция с CAIE | Автоматическая инъекция обнаруженных подделок как **логических разрывов** в CrossArtifactIncongruenceEngine. | Гарантирует прослеживаемость в многоинструментальных рабочих процессах. |
| Бесшумный анализ метаданных | Неразрушающее извлечение и детерминированный разбор тегов EXIF/XMP. | Выявляет индикаторы программной подделки и историю редактирования. |
| Классификация без обучения | Семантическая категоризация без предварительного обучения на размеченных подделках. | Обеспечивает категориальный контекст посредством дискретных отображений классов. |
| Детерминированная целочисленная арифметика | Операции над целыми числами, дающие идентичные результаты при идентичных входных данных, без ошибок округления. | Основа всех измеримых судебно-экспертных операций данного модуля. |
| Ожидаемые ключи PNG (`_EXPECTED_PNG_KEYS`) | Детерминированный контрольный список обязательных тегов метаданных для валидации происхождения PNG. | Служит базовой линией для обнаружения отсутствующих или манипулированных структурных метаданных. |

### Глоссарий

| Термин | Определение |
|---|---|
| **Локальная дисперсия (окно 32×32)** | Мера рассеяния пикселей, вычисляемая суммированием квадратов целочисленных отклонений по фиксированным блокам 32×32. |
| **Коэффициент ДКП** | Целочисленное значение (после квантования) из дискретного косинусного преобразования блока 8×8; несоответствия на границах блоков указывают на склейку. |
| **EXIF/XMP** | Встроенные словари метаданных, фиксирующие параметры камеры, программное обеспечение и историю редактирования; разбираются как структурированный текст. |
| **Судебная фрактура (логический разрыв)** | Формальная запись обнаруженной аномалии, представляющая разрыв в ожидаемой цепи происхождения. |
| **Singleton** | Шаблон, гарантирующий существование единственного экземпляра аудитора в системе и поддерживающий согласованное состояние расследования. |
| **ForensicImageAnalyzer** | Основной класс, оркестрирующий анализ на уровне пикселей, разбор метаданных и экспорт фрактур CAIE. |
| **CLIPVisualAuditor** | Класс, предоставляющий семантическую классификацию без обучения посредством дискретных отображений классов. |

> **【Научное примечание】**
> Модуль заимствует терминологию Чарльза Сандерса Пирса, Умберто Эко и Г. П. Грайса — учёных, формализовавших передачу значения знаками. Упоминания *интенциональности*, *диссонанса* или *кодов* обозначают технические наблюдаемые величины, а не метафизические силы. Триада Пирса (знак–объект–интерпретант) — это протокол преобразования: файл изображения — знак, физический документ, которым он претендует быть, — объект, а детерминированный целочисленный выход — интерпретант. Коды Эко действуют как уровни коммуникационного протокола; Принцип кооперации Грайса работает как базовая калибровка датчика — нарушения регистрируются как дискретные аномалии, точно так же, как барометр фиксирует отклонения давления. «Магия» — строгая целочисленная арифметика, а не мистицизм.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## 中文

### 这是什么模块？
VIGIA（视觉意向性审计）是一个确定性取证引擎，用于验证图像与扫描文档的真实性。它将每幅图像视为由整数像素值构成的结构化网格。该模块将视觉元素（印章、签名、背景纹理）与预期的确定性模式进行比对。当伪造行为引入拼贴、粘贴印章或分辨率不匹配时，引擎将记录**结构性不协调**。该模块应用确定性算法——基于整数的 32×32 窗口局部方差分析，以及离散余弦变换（DCT）系数检查——以生成可重复、可复现的发现。分析由两个类组织：`ForensicImageAnalyzer`（主流水线）和 `CLIPVisualAuditor`（零样本语义分类）。

### 核心概念

| 术语 | 通俗定义 | 科学作用 |
|---|---|---|
| 意向性失调 | 图像所声称的来源（如官方扫描件）与其结构生成证据之间的冲突。 | 核心检测目标；表明可能存在伪造。 |
| 数字完美异常 | 在同一采集历史应统一的区域内出现的不自然均匀性或意外方差。 | 通过 32×32 整数窗口的确定性方差运算检测。 |
| 压缩伪影特征 | 有损压缩在 8×8 像素块上留下的确定性指纹。 | 揭示来自不同压缩历史来源的拼接。 |
| CAIE 集成 | 将检测到的伪造自动作为**逻辑断裂**注入跨取证工件不协调引擎。 | 确保多工具调查工作流中的可追溯性。 |
| 静默元数据分析 | 对 EXIF/XMP 标签进行非破坏性提取与确定性解析。 | 暴露软件篡改指标与编辑历史。 |
| 零样本分类 | 无需在已标注伪造样本上预先训练即可进行语义归类。 | 利用离散类别映射提供语义上下文。 |
| 确定性整数运算 | 对整数进行操作，在相同输入下始终产生相同输出，无舍入误差。 | 本模块所有可测量取证操作的基础。 |
| 预期 PNG 键（`_EXPECTED_PNG_KEYS`） | 用于验证 PNG 来源的必需元数据标签的确定性检查列表。 | 作为检测缺失或被篡改结构性元数据的基线。 |

### 词汇表

| 术语 | 定义 |
|---|---|
| **局部方差（32×32 窗口）** | 在固定的 32×32 像素块上，通过对整数偏差平方求和来计算像素离散程度的度量。 |
| **DCT 系数** | 对 8×8 块进行离散余弦变换后得到的（量化后）整数值；块边界处的不一致性表明存在拼接。 |
| **EXIF/XMP** | 记录相机参数、软件信息及编辑历史的嵌入式元数据字典；作为结构化文本进行解析。 |
| **取证断裂（逻辑断裂）** | 对检测到的异常进行正式记录，代表预期溯源链中的断裂。 |
| **单例（Singleton）** | 一种设计模式，确保系统中仅存在一个审计器实例，从而保持调查状态的一致性。 |
| **取证图像分析器（ForensicImageAnalyzer）** | 主类，统筹像素级分析、元数据解析和 CAIE 逻辑断裂导出。 |
| **CLIP 视觉审计器（CLIPVisualAuditor）** | 通过离散类别映射提供零样本语义分类的类。 |

> **【科学说明】**
> 本模块采用了查尔斯·桑德斯·皮尔士、**艾柯**（Umberto Eco）与**格赖斯**（H.P. Grice）的术语——这些学者将符号如何承载意义进行了形式化。文中提及的"意向性""失调""代码"均为技术可观测指标，而非形而上学力量。请将皮尔士的三元组（符号–对象–解释项）视为一种传感转导协议：图像文件是符号，其声称代表的物理文件是对象，而确定性整数输出即为解释项。艾柯的"代码"相当于通信协议层；格赖斯的"合作原则"则类似于传感器的基线校准——违反该原则即被登记为离散异常，正如气压计标记气压偏离一样。这里的"魔力"来自严格的整数运算，而非神秘主义。

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
