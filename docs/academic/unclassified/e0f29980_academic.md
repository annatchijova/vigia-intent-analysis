<!--
VIGIA Academic Documentation
Module: e0f29980
Batch ID: vigia-doc-0092-e0f29980
Generated: 2026-05-20T14:56:47.864451+00:00
-->

---

## ENGLISH

### What Is This Module?
VIGIA (Visual Intentionality Audit) is a forensic analysis system designed for scientists and researchers who need to determine whether a digital image or scanned document is authentic or has been manipulated. Think of it as a laboratory instrument—like a spectrophotometer or an electron microscope—that accepts an image file instead of a physical sample. The module performs a battery of deterministic measurements using exclusively integer arithmetic to detect whether different regions of a picture originate from different sources. For example, it can reveal whether an official seal or handwritten signature was digitally pasted onto a background, because the statistical texture (local variance) of the pasted element will differ from its surroundings in a mathematically exact way. By combining computer vision, metadata archaeology, and semiotic logic, the system flags *intentionality dissonance*: the condition in which a document claims to be an official record but carries hidden structural contradictions.

### Key Concepts

| Term | Explanation |
|---|---|
| **Local Variance Analysis** | A deterministic counting method that measures how much pixel values change within fixed 32×32 windows. Pasted objects often show unnaturally uniform or mismatched variance compared to native document regions. |
| **Digital Perfection Detection** | The principle that forged elements frequently exhibit resolution, sharpness, or noise properties inconsistent with the rest of the image. Detected via integer-based texture metrics, not subjective visual inspection. |
| **CAIE Integration** | Cross-Artifact Intentionality Engine: the module that correlates image anomalies with other forensic signals (metadata, timestamps, document provenance). |
| **Intentionality Dissonance** | The condition in which a document's structural properties contradict its claimed authenticity. A sign whose form and context are irreconcilably mismatched. |
| **Metadata Archaeology** | Extraction and analysis of embedded EXIF and document metadata to reconstruct the creation and modification history of an image. |
| **Deterministic Integer Arithmetic** | All pixel measurements, variance calculations, and threshold comparisons use exact integer values. No floating-point approximations are introduced into the evidence record. |

### Core Operations

| Operation | Purpose |
|---|---|
| `analyze_image()` | Runs the full battery of integrity checks on an image file; returns a structured result with integer anomaly counts. |
| `compute_local_variance()` | Computes exact integer variance values across all 32×32 pixel windows in the image. |
| `detect_splice_boundary()` | Identifies pixel-level boundaries between regions of differing statistical texture, indicating composite construction. |
| `extract_metadata()` | Parses EXIF and embedded document metadata for provenance reconstruction. |

### Glossary
1. **CAIE (Cross-Artifact Intentionality Engine)** — The module correlating image anomalies with broader forensic signals.
2. **Deterministic Integer Arithmetic** — Computation using exact integer values; no approximations in the evidence pipeline.
3. **EXIF Metadata** — Embedded data within an image file recording camera settings, timestamps, and software information.
4. **Intentionality Dissonance** — The forensic condition in which a document's structure contradicts its claimed identity.
5. **Local Variance** — An integer-based measure of pixel-value change within a fixed spatial window.
6. **Metadata Archaeology** — Systematic extraction of provenance information from embedded document metadata.
7. **Pixel-Level Analysis** — Examination of individual or grouped pixel values to detect manipulation artifacts.
8. **Splice Boundary** — A detectable edge between image regions originating from different sources.
9. **Texture Metric** — A numerical descriptor of the statistical character of pixel patterns in a region.
10. **Visual Forensics** — The scientific discipline of authenticating or refuting the integrity of digital images and scanned documents.

> **【Scientific Note】**
> Peirce/Eco/Grice terminology is NOT mysticism. In VIGÍA, intentionality dissonance is a Peircean *secondness* event: the structural anomaly exists only in contrast to what a genuine document of this type should look like. Eco's interpretive principle identifies the forged element as a sign operating under a different code than its host document — a foreign semiotic system embedded in a native one. Grice's maxim of quality is violated when a document presents itself as authentic while carrying internal structural contradictions.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## ESPAÑOL

### ¿Qué es este módulo?
VIGIA (Auditoría de Intencionalidad Visual) es un sistema de análisis forense diseñado para científicos e investigadores que necesitan determinar si una imagen digital o documento escaneado es auténtico o ha sido manipulado. Piénselo como un instrumento de laboratorio —como un espectrofotómetro o un microscopio electrónico— que acepta un archivo de imagen en lugar de una muestra física. El módulo realiza una batería de mediciones deterministas usando exclusivamente aritmética entera para detectar si diferentes regiones de una imagen provienen de fuentes diferentes. Por ejemplo, puede revelar si un sello oficial o una firma manuscrita fue pegada digitalmente sobre un fondo, porque la textura estadística (varianza local) del elemento pegado diferirá de su entorno de forma matemáticamente exacta. Combinando visión por computadora, arqueología de metadatos y lógica semiótica, el sistema señala la *disonancia de intencionalidad*: la condición en que un documento afirma ser un registro oficial pero lleva contradicciones estructurales ocultas.

### Conceptos clave

| Término | Explicación |
|---|---|
| **Análisis de Varianza Local** | Método de conteo determinista que mide cuánto cambian los valores de píxeles dentro de ventanas fijas de 32×32. Los objetos pegados frecuentemente muestran varianza anormalmente uniforme o desajustada comparada con regiones nativas del documento. |
| **Detección de Perfección Digital** | Principio de que los elementos falsificados frecuentemente exhiben propiedades de resolución, nitidez o ruido inconsistentes con el resto de la imagen. Detectado mediante métricas de textura basadas en enteros. |
| **Integración CAIE** | Motor de Intencionalidad entre Artefactos: correlaciona anomalías de imagen con otras señales forenses (metadatos, marcas de tiempo, procedencia del documento). |
| **Disonancia de Intencionalidad** | Condición en que las propiedades estructurales de un documento contradicen su autenticidad reclamada. |
| **Arqueología de Metadatos** | Extracción y análisis de metadatos EXIF y de documentos incrustados para reconstruir el historial de creación y modificación de una imagen. |
| **Aritmética Entera Determinista** | Todas las mediciones de píxeles, cálculos de varianza y comparaciones de umbral usan valores enteros exactos. |

### Glosario
1. **CAIE (Motor de Intencionalidad entre Artefactos)** — El módulo que correlaciona anomalías de imagen con señales forenses más amplias.
2. **Aritmética Entera Determinista** — Cómputo usando valores enteros exactos; sin aproximaciones en la cadena de evidencia.
3. **Metadatos EXIF** — Datos incrustados en un archivo de imagen que registran configuraciones de cámara, marcas de tiempo e información de software.
4. **Disonancia de Intencionalidad** — Condición forense en que la estructura de un documento contradice su identidad reclamada.
5. **Varianza Local** — Medida basada en enteros del cambio de valores de píxeles dentro de una ventana espacial fija.
6. **Arqueología de Metadatos** — Extracción sistemática de información de procedencia de metadatos de documentos incrustados.
7. **Análisis a Nivel de Píxel** — Examen de valores de píxeles individuales o agrupados para detectar artefactos de manipulación.
8. **Frontera de Empalme** — Borde detectable entre regiones de imagen procedentes de diferentes fuentes.
9. **Métrica de Textura** — Descriptor numérico del carácter estadístico de los patrones de píxeles en una región.
10. **Forense Visual** — Disciplina científica de autenticación o refutación de la integridad de imágenes digitales y documentos escaneados.

> **【Nota Científica】**
> La terminología de Peirce/Eco/Grice no es misticismo. En VIGÍA, la disonancia de intencionalidad es un evento de *segundidad* peirceana: la anomalía estructural existe solo en contraste con lo que debería verse un documento genuino de este tipo. El principio interpretativo de Eco identifica el elemento falsificado como un signo que opera bajo un código diferente al de su documento huésped. La máxima de calidad de Grice se viola cuando un documento se presenta como auténtico mientras porta contradicciones estructurales internas.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## РУССКИЙ

### Что это за модуль?
VIGIA (Аудит визуальной интенциональности) — криминалистическая система анализа, предназначенная для учёных и исследователей, которым необходимо определить, является ли цифровое изображение или отсканированный документ подлинным или подделанным. Представьте его как лабораторный прибор — подобный спектрофотометру или электронному микроскопу — принимающий файл изображения вместо физического образца. Модуль выполняет серию детерминированных измерений, используя исключительно целочисленную арифметику, для обнаружения различных источников происхождения регионов изображения. Например, он может выявить, было ли официальное лицо или рукописная подпись цифровым образом наклеена на фон, поскольку статистическая текстура (локальная дисперсия) наклеенного элемента будет математически точно отличаться от окружения. Сочетая компьютерное зрение, «археологию» метаданных и семиотическую логику, система выявляет *диссонанс интенциональности*: состояние, при котором документ заявляет о себе как об официальном, но несёт скрытые структурные противоречия.

### Ключевые концепции

| Термин | Объяснение |
|---|---|
| **Анализ локальной дисперсии** | Детерминированный метод подсчёта, измеряющий изменение значений пикселей в фиксированных окнах 32×32. Вставленные объекты часто показывают неестественно однородную или несоответствующую дисперсию по сравнению с исходными областями документа. |
| **Обнаружение цифрового совершенства** | Принцип, согласно которому поддельные элементы часто имеют свойства разрешения, резкости или шума, несовместимые с остальной частью изображения. Обнаруживается через целочисленные метрики текстуры. |
| **Интеграция CAIE** | Движок межартефактной интенциональности: коррелирует аномалии изображения с другими криминалистическими сигналами (метаданные, временны́е метки, провенанс документа). |
| **Диссонанс интенциональности** | Состояние, при котором структурные свойства документа противоречат его заявленной подлинности. |
| **«Археология» метаданных** | Извлечение и анализ встроенных метаданных EXIF и документа для реконструкции истории создания и модификации изображения. |
| **Детерминированная целочисленная арифметика** | Все измерения пикселей, вычисления дисперсии и сравнения порогов используют точные целочисленные значения. |

### Глоссарий
1. **CAIE (Движок межартефактной интенциональности)** — Модуль, коррелирующий аномалии изображения с более широкими криминалистическими сигналами.
2. **Детерминированная целочисленная арифметика** — Вычисления с точными целочисленными значениями; без приближений в доказательственной цепочке.
3. **Метаданные EXIF** — Встроенные данные в файле изображения, фиксирующие настройки камеры, временны́е метки и информацию о программном обеспечении.
4. **Диссонанс интенциональности** — Криминалистическое состояние, при котором структура документа противоречит его заявленной идентичности.
5. **Локальная дисперсия** — Целочисленная мера изменения значений пикселей в фиксированном пространственном окне.
6. **«Археология» метаданных** — Систематическое извлечение информации о провенансе из встроенных метаданных документа.
7. **Анализ на уровне пикселей** — Исследование отдельных или сгруппированных значений пикселей для обнаружения артефактов манипуляции.
8. **Граница склейки** — Обнаруживаемая граница между областями изображения из разных источников.
9. **Метрика текстуры** — Числовой дескриптор статистического характера паттернов пикселей в регионе.
10. **Визуальная криминалистика** — Научная дисциплина аутентификации или опровержения целостности цифровых изображений и отсканированных документов.

> **【Научное примечание】**
> Терминология Пирса, Эко и Грайса — не мистика. В VIGÍA диссонанс интенциональности является событием пирсовской *Вторичности*: структурная аномалия существует только в контрасте с тем, как должен выглядеть подлинный документ данного типа. Интерпретационный принцип Эко идентифицирует поддельный элемент как знак, действующий по иному коду, нежели документ-носитель. Максима качества Грайса нарушается, когда документ представляет себя подлинным, неся внутренние структурные противоречия.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## 中文

### 这是什么模块？
VIGIA（视觉意图审计）是一个取证分析系统，专为需要判断数字图像或扫描文档是否真实或被篡改的科学家和研究人员设计。可将其视为实验室仪器——如分光光度计或电子显微镜——接受图像文件而非物理样本。该模块使用完全基于整数的确定性算术执行一系列测量，以检测图像不同区域是否来自不同来源。例如，它能揭示官方印章或手写签名是否被数字粘贴到背景上，因为粘贴元素的统计纹理（局部方差）将以数学上精确的方式与周围环境不同。通过结合计算机视觉、元数据考古学和符号学逻辑，该系统标记*意图失谐*：文件声称为官方记录但带有隐藏结构矛盾的状态。

### 关键概念

| 术语 | 说明 |
|---|---|
| **局部方差分析** | 在固定 32×32 窗口内测量像素值变化程度的确定性计数方法。粘贴对象与文档原生区域相比通常显示出不自然的均匀或不匹配方差。 |
| **数字完美检测** | 伪造元素通常表现出与图像其余部分不一致的分辨率、清晰度或噪声属性的原则。通过基于整数的纹理指标检测，而非主观视觉检查。 |
| **CAIE 集成** | 跨工件意图引擎：将图像异常与其他取证信号（元数据、时间戳、文档来源）关联起来的模块。 |
| **意图失谐** | 文档结构属性与其声称真实性相矛盾的状态。 |
| **元数据考古学** | 提取和分析嵌入的 EXIF 和文档元数据，以重建图像的创建和修改历史。 |
| **确定性整数运算** | 所有像素测量、方差计算和阈值比较均使用精确整数值。 |

### 词汇表
1. **CAIE（跨工件意图引擎）** — 将图像异常与更广泛取证信号相关联的模块。
2. **确定性整数运算** — 使用精确整数值的计算；证据流水线中无近似值。
3. **EXIF 元数据** — 图像文件中记录相机设置、时间戳和软件信息的嵌入数据。
4. **意图失谐** — 文档结构与其声称身份相矛盾的取证状态。
5. **局部方差** — 在固定空间窗口内基于整数的像素值变化度量。
6. **元数据考古学** — 从嵌入文档元数据系统提取来源信息的方法。
7. **像素级分析** — 检查单个或分组像素值以检测篡改工件。
8. **拼接边界** — 来自不同来源的图像区域之间可检测到的边缘。
9. **纹理指标** — 区域内像素模式统计特征的数值描述符。
10. **视觉取证** — 对数字图像和扫描文档完整性进行认证或反驳的科学学科。

> **【科学说明】**
> 皮尔斯、艾柯和格赖斯的术语并非神秘主义。在 VIGÍA 中，意图失谐是皮尔斯意义上的*第二性*事件：结构异常仅在与同类真实文档的外观对比中存在。艾柯的解释原则将伪造元素识别为在与宿主文档不同的代码下运作的符号——嵌入在本地符号系统中的外来符号系统。当文档在呈现为真实的同时携带内部结构矛盾时，格赖斯的质量准则即遭到违反。

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
