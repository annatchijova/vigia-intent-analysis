<!--
VIGIA Academic Documentation
Module: 6c431d0b
Batch ID: vigia-doc-0138-6c431d0b
Generated: 2026-05-20T14:56:47.874302+00:00
-->

---

## ENGLISH

### What Is This Module?
`vigia/sift/prefetch_analyzer.py` is a deterministic digital-forensic engine that examines Windows Prefetch files (extension `.pf`). Every time a program launches, Windows creates or updates one of these files. The module reads them to reconstruct when a program ran, how many times it ran, and which auxiliary files were loaded. It also detects deliberate gaps—such as the selective deletion of individual prefetch files—which are strong indicators of anti-forensic tampering. All quantitative findings are stored as exact rational numbers (`Fraction` objects or their string forms), ensuring that repeated analyses produce identical integer results with no approximation errors.

### Key Concepts

| Concept | Description | Scientific Purpose |
|---|---|---|
| **Prefetch File (.pf)** | A Windows system trace that records program execution, launch timestamp, and dependencies. | Serves as a passive, OS-generated sensor of software activity. |
| **PrefetchRecord** | A structured data row representing a single parsed prefetch trace. | Standardizes raw file contents into a human-readable evidence unit. |
| **PrefetchAnalysisResult** | The final report object containing correlated findings, reliability metrics, and anomaly flags. | Provides a deterministic, auditable summary of all parsed traces for chain-of-custody logging. |
| **Run Count** | An exact integer stored in the prefetch file indicating how many times the program launched. | Enables exact integer comparison against behavioral baselines without approximation. |
| **Selective Deletion Flag** | A boolean signal raised when expected prefetch files are absent while surrounding files are present. | Detects anti-forensic file removal via deterministic gap analysis over the integer-indexed file list. |
| **Exact Rational Arithmetic** | All intermediate scores stored as `Fraction` objects. | Guarantees bit-identical results across platforms and execution environments. |
| **Artifact Reliability** | A calibrated integer-tier confidence level assigned to prefetch evidence. | Weights evidence contribution in downstream scoring without floating-point approximation. |

### Glossary

1. **Prefetch File** — A Windows system artifact (`.pf` extension) that records program execution metadata, created automatically by the OS prefetch service.
2. **Run Count** — An exact integer embedded in a prefetch file indicating the total number of program launches recorded by the OS.
3. **Selective Deletion** — The deliberate removal of specific prefetch files to conceal program execution history, detectable via gap analysis.
4. **Deterministic Integer Arithmetic** — Mathematical operations exclusively on whole numbers or rational fractions, yielding identical results on every platform without rounding drift.
5. **Forensic Artifact** — Any digital object carrying potential evidence; here specifically prefetch files recovered from a Windows volume.
6. **PrefetchRecord** — An immutable, structured record produced by the parser for each valid prefetch file encountered.
7. **Anomaly Flag** — A boolean integer signal (0 or 1) raised by a detector rule when an expected property is violated.
8. **Artifact Reliability** — An integer-tier confidence weight indicating how trustworthy the prefetch evidence class is as a source of truth.
9. **Chain of Custody** — The unbroken, timestamped record of all actions taken on evidence from collection through analysis.
10. **Gap Analysis** — The deterministic detection of missing entries within a complete integer-indexed sequence of expected artifacts.

> **【Scientific Note】**
> Peirce's Firstness in this module is the raw prefetch file—a byte sequence without interpretation. Secondness is the comparison of the parsed run count and timestamps against the expected behavioral baseline: the binary reaction that signals an anomaly or confirms normality. Thirdness is the selective-deletion detection rule: a repeatable law uniformly applied to the integer-indexed file list, producing the same boolean flag on the same input in every execution. Eco's encyclopedia principle ensures that "run count" and "selective deletion" have single, unambiguous definitions across all VIGÍA modules. Grice's maxim of Quality guarantees the module reports exactly what it finds: exact integer counts and boolean flags, with no probabilistic embellishment.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## ESPAÑOL

### ¿Qué es este módulo?
`vigia/sift/prefetch_analyzer.py` es un motor forense digital determinista que examina archivos Prefetch de Windows (extensión `.pf`). Cada vez que se lanza un programa, Windows crea o actualiza uno de estos archivos. El módulo los lee para reconstruir cuándo se ejecutó un programa, cuántas veces se ejecutó y qué archivos auxiliares se cargaron. También detecta huecos deliberados —como la eliminación selectiva de archivos prefetch individuales— que son fuertes indicadores de manipulación anti-forense. Todos los hallazgos cuantitativos se almacenan como números racionales exactos (objetos `Fraction` o sus formas en cadena de texto), garantizando que análisis repetidos produzcan resultados enteros idénticos sin errores de aproximación.

### Conceptos clave

| Concepto | Descripción | Propósito científico |
|---|---|---|
| **Archivo Prefetch (.pf)** | Traza del sistema Windows que registra la ejecución de un programa, la marca temporal de lanzamiento y las dependencias. | Actúa como sensor pasivo generado por el SO de la actividad del software. |
| **PrefetchRecord** | Fila de datos estructurada que representa una única traza prefetch parseada. | Estandariza el contenido crudo del archivo en una unidad de evidencia legible. |
| **PrefetchAnalysisResult** | Objeto de informe final que contiene hallazgos correlacionados, métricas de fiabilidad y banderas de anomalía. | Proporciona un resumen determinista y auditable de todas las trazas parseadas. |
| **Conteo de ejecuciones** | Entero exacto almacenado en el archivo prefetch que indica cuántas veces se lanzó el programa. | Permite comparación entera exacta contra líneas base de comportamiento. |
| **Bandera de eliminación selectiva** | Señal booleana que se activa cuando se esperan archivos prefetch pero están ausentes mientras los archivos circundantes están presentes. | Detecta la eliminación anti-forense de archivos mediante análisis determinista de huecos. |
| **Aritmética racional exacta** | Todas las puntuaciones intermedias almacenadas como objetos `Fraction`. | Garantiza resultados bit a bit idénticos en todas las plataformas. |
| **Fiabilidad del artefacto** | Nivel de confianza entero calibrado asignado a la evidencia prefetch. | Pondera la contribución de evidencia en la puntuación downstream sin aproximación de punto flotante. |

### Glosario

1. **Archivo Prefetch** — Artefacto del sistema Windows (extensión `.pf`) que registra metadatos de ejecución de programas, creado automáticamente por el servicio prefetch del SO.
2. **Conteo de ejecuciones** — Entero exacto embebido en un archivo prefetch que indica el número total de lanzamientos de programa registrados por el SO.
3. **Eliminación selectiva** — Remoción deliberada de archivos prefetch específicos para ocultar el historial de ejecución de programas, detectable mediante análisis de huecos.
4. **Aritmética entera determinista** — Operaciones matemáticas exclusivamente sobre números enteros o fracciones racionales, que producen resultados idénticos en toda plataforma sin deriva por redondeo.
5. **Artefacto forense** — Cualquier objeto digital con evidencia potencial; aquí específicamente archivos prefetch recuperados de un volumen Windows.
6. **PrefetchRecord** — Registro inmutable y estructurado producido por el analizador para cada archivo prefetch válido encontrado.
7. **Bandera de anomalía** — Señal booleana entera (0 o 1) activada por una regla del detector cuando se viola una propiedad esperada.
8. **Fiabilidad del artefacto** — Peso de confianza de nivel entero que indica cuán confiable es la clase de evidencia prefetch como fuente de verdad.
9. **Cadena de custodia** — Registro ininterrumpido y con marca temporal de todas las acciones realizadas sobre la evidencia desde su recolección hasta el análisis.
10. **Análisis de huecos** — Detección determinista de entradas faltantes dentro de una secuencia indexada por enteros de artefactos esperados.

> **【Nota Científica】**
> La Primereidad de Peirce en este módulo es el archivo prefetch crudo — una secuencia de bytes sin interpretación. La Segundidad es la comparación del conteo de ejecuciones parseado y las marcas temporales contra la línea base de comportamiento esperada: la reacción binaria que señala una anomalía o confirma la normalidad. La Terceridad es la regla de detección de eliminación selectiva: una ley repetible aplicada uniformemente a la lista de archivos indexada por enteros, produciendo la misma bandera booleana en la misma entrada en cada ejecución. El principio de enciclopedia de Eco garantiza que "conteo de ejecuciones" y "eliminación selectiva" tienen definiciones únicas e inequívocas en todos los módulos de VIGÍA. La máxima de Calidad de Grice garantiza que el módulo reporte exactamente lo que encuentra: conteos enteros exactos y banderas booleanas, sin embellecimiento probabilístico.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## РУССКИЙ

### Что представляет собой этот модуль?
`vigia/sift/prefetch_analyzer.py` — детерминированный цифровой криминалистический движок, исследующий файлы Prefetch Windows (расширение `.pf`). Каждый раз при запуске программы Windows создаёт или обновляет один из таких файлов. Модуль считывает их для восстановления информации о том, когда запускалась программа, сколько раз она запускалась и какие вспомогательные файлы загружались. Модуль также обнаруживает намеренные пробелы — например, избирательное удаление отдельных prefetch-файлов, — являющиеся весомым индикатором антикриминалистической фальсификации. Все количественные выводы хранятся как точные рациональные числа (объекты `Fraction` или их строковые формы), гарантируя, что повторные анализы дают идентичные целочисленные результаты без ошибок аппроксимации.

### Ключевые понятия

| Понятие | Описание | Научное назначение |
|---|---|---|
| **Файл Prefetch (.pf)** | Системный след Windows, фиксирующий исполнение программы, временну́ю метку запуска и зависимости. | Выступает пассивным сенсором активности программного обеспечения, генерируемым ОС. |
| **PrefetchRecord** | Структурированная строка данных, представляющая единственный разобранный prefetch-след. | Стандартизирует содержимое исходного файла в читаемую доказательственную единицу. |
| **PrefetchAnalysisResult** | Итоговый объект отчёта, содержащий коррелированные выводы, метрики надёжности и флаги аномалий. | Предоставляет детерминированное, поддающееся аудиту резюме всех разобранных следов. |
| **Счётчик запусков** | Точное целое число, хранимое в prefetch-файле и указывающее, сколько раз запускалась программа. | Позволяет точное целочисленное сравнение с поведенческими базами без аппроксимации. |
| **Флаг избирательного удаления** | Булев сигнал, активируемый, когда ожидаемые prefetch-файлы отсутствуют при наличии соседних. | Обнаруживает антикриминалистическое удаление файлов через детерминированный анализ пробелов. |
| **Точная рациональная арифметика** | Все промежуточные оценки хранятся как объекты `Fraction`. | Гарантирует побитово идентичные результаты на всех платформах. |
| **Надёжность артефакта** | Откалиброванный целочисленный уровень достоверности, назначаемый prefetch-доказательствам. | Взвешивает вклад доказательств в downstream-оценку без аппроксимации с плавающей точкой. |

### Глоссарий

1. **Файл Prefetch** — Системный артефакт Windows (расширение `.pf`), автоматически создаваемый сервисом prefetch и содержащий метаданные исполнения программ.
2. **Счётчик запусков** — Точное целое число, встроенное в prefetch-файл и обозначающее суммарное количество зафиксированных ОС запусков программы.
3. **Избирательное удаление** — Намеренное удаление конкретных prefetch-файлов для сокрытия истории исполнения программ, выявляемое через анализ пробелов.
4. **Детерминированная целочисленная арифметика** — Математические операции исключительно над целыми числами или рациональными дробями, дающие идентичные результаты на всех платформах без дрейфа округления.
5. **Криминалистический артефакт** — Любой цифровой объект, несущий потенциальные доказательства; здесь конкретно prefetch-файлы, извлечённые из тома Windows.
6. **PrefetchRecord** — Неизменяемая, структурированная запись, создаваемая анализатором для каждого найденного действительного prefetch-файла.
7. **Флаг аномалии** — Булев целочисленный сигнал (0 или 1), активируемый правилом детектора при нарушении ожидаемого свойства.
8. **Надёжность артефакта** — Целочисленный весовой уровень достоверности, указывающий, насколько достоверен класс prefetch-доказательств в качестве источника истины.
9. **Цепочка сохранения** — Непрерывный, отмеченный временем журнал всех действий, предпринятых в отношении доказательств от сбора до анализа.
10. **Анализ пробелов** — Детерминированное обнаружение отсутствующих записей в полной целочисленно-индексированной последовательности ожидаемых артефактов.

> **【Научное примечание】**
> Первичность Пирса в данном модуле — необработанный prefetch-файл: байтовая последовательность без интерпретации. Вторичность — сравнение разобранного счётчика запусков и временны́х меток с ожидаемой поведенческой базой: бинарная реакция, сигнализирующая об аномалии или подтверждающая норму. Третичность — правило обнаружения избирательного удаления: повторяемый закон, единообразно применяемый к целочисленно-индексированному списку файлов и производящий одинаковый булев флаг на одних и тех же входных данных при каждом исполнении. Принцип энциклопедии Эко гарантирует, что «счётчик запусков» и «избирательное удаление» имеют единственные, недвусмысленные определения во всех модулях VIGÍA. Максима Качества Грайса гарантирует, что модуль сообщает ровно то, что обнаружил: точные целочисленные счётчики и булевы флаги, без вероятностных украшений.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## 中文

### 本模块是什么？
`vigia/sift/prefetch_analyzer.py` 是一个确定性数字取证引擎，用于检查 Windows 预取文件（扩展名 `.pf`）。每次程序启动时，Windows 都会创建或更新其中一个文件。模块读取这些文件以重建程序运行的时间、运行次数以及加载了哪些辅助文件。模块还检测故意制造的空白——例如选择性删除单个预取文件——这是强有力的反取证篡改指标。所有定量结果均以精确有理数（`Fraction` 对象或其字符串形式）存储，确保重复分析产生完全相同的整数结果，无任何近似误差。

### 核心概念

| 概念 | 描述 | 科学用途 |
|---|---|---|
| **预取文件 (.pf)** | 记录程序执行、启动时间戳和依赖项的 Windows 系统痕迹。 | 作为操作系统生成的软件活动被动传感器。 |
| **PrefetchRecord** | 表示单个已解析预取痕迹的结构化数据行。 | 将原始文件内容标准化为人类可读的证据单元。 |
| **PrefetchAnalysisResult** | 包含相关发现、可靠性指标和异常标志的最终报告对象。 | 为监管链日志提供所有已解析痕迹的确定性可审计摘要。 |
| **运行计数** | 存储在预取文件中的精确整数，表示程序启动的次数。 | 无近似地与行为基线进行精确整数比较。 |
| **选择性删除标志** | 当相邻文件存在但预期预取文件缺失时引发的布尔信号。 | 通过对整数索引文件列表进行确定性空白分析来检测反取证文件删除。 |
| **精确有理数算术** | 所有中间分数存储为 `Fraction` 对象。 | 保证跨平台位相同结果。 |
| **取证工件可靠性** | 分配给预取证据的经校准整数层级置信水平。 | 在下游评分中无浮点近似地加权证据贡献。 |

### 术语表

1. **预取文件** — Windows 系统取证工件（`.pf` 扩展名），由操作系统预取服务自动创建，记录程序执行元数据。
2. **运行计数** — 嵌入预取文件中的精确整数，表示操作系统记录的程序启动总次数。
3. **选择性删除** — 故意删除特定预取文件以隐藏程序执行历史，可通过空白分析检测。
4. **确定性整数算术** — 仅对整数或有理分数执行的数学运算，在所有平台上产生相同结果，无舍入漂移。
5. **取证工件** — 携带潜在证据的任何数字对象；此处特指从 Windows 卷恢复的预取文件。
6. **PrefetchRecord** — 解析器为每个遇到的有效预取文件生成的不可变结构化记录。
7. **异常标志** — 检测器规则在违反预期属性时引发的布尔整数信号（0 或 1）。
8. **取证工件可靠性** — 整数层级置信权重，表示预取证据类别作为真值来源的可信度。
9. **监管链** — 从采集到分析对证据采取的所有行动的不间断带时间戳记录。
10. **空白分析** — 在预期取证工件的完整整数索引序列中确定性检测缺失条目。

> **【科学说明】**
> 皮尔斯的初性在本模块中是原始预取文件——一个未加解释的字节序列。二性是已解析运行计数和时间戳与预期行为基线的比较：信号异常或确认正常的二元反应。三性是选择性删除检测规则：一种可重复的规律，均匀应用于整数索引的文件列表，在每次执行的相同输入上产生相同的布尔标志。艾柯的百科全书原则确保"运行计数"和"选择性删除"在所有 VIGÍA 模块中各有唯一明确的定义。格赖斯的质的准则保证模块精确报告其所发现的内容：精确整数计数和布尔标志，无概率修饰。

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
