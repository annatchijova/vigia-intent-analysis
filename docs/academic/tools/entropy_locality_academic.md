<!--
VIGIA Academic Documentation
Module: 1dbdaea0
Batch ID: vigia-doc-0159-1dbdaea0
Generated: 2026-05-20T14:56:47.878870+00:00
-->

## ENGLISH

### Module: `vigia/tools/entropy_locality.py` — Entropy Locality Analyzer

### What Is This Module?
This module is a digital forensics instrument. It examines a file not as a single bag of bytes, but as a spatial map. Its purpose is to reveal *where* disorder hides inside a file, rather than reporting only an overall average. High entropy concentrated in a specific neighborhood is a strong indicator of encrypted payloads, steganographic insertion, or injected shellcode. By splitting the data into sequential chunks and measuring each zone independently through deterministic integer arithmetic, the tool produces an immutable spatial profile that an investigator can read, compare, and archive.

### Key Concepts

| Concept | Plain-Language Definition |
|---|---|
| **Global Entropy** | A single average of randomness across an entire file; easily manipulated by padding or mixed content. |
| **Spatial Entropy Distribution** | A coordinate map showing how randomness varies from one region to another. |
| **Entropy Locality** | The specific address (offset) where unusually high disorder appears. |
| **Chunk** | A fixed-size byte window treated as an independent specimen. |
| **Deterministic Integer Arithmetic** | Exact counting operations using whole-number frequencies and rational metrics; identical files always yield identical profiles, with no platform-dependent rounding. |
| **Steganography** | The practice of hiding a secret message inside an otherwise ordinary carrier file. |
| **Shellcode** | Machine-level instructions placed by an attacker to seize control of a process. |
| **Forensic Artifact** | Any object or data structure produced during an investigation that serves as evidence. |

### Module Components

| Component | Scientific Role |
|---|---|
| `EntropyProfile` | An immutable record—once created, it cannot be altered—storing entropy values for every spatial zone. |
| `EntropyLocalityAnalyzer` | The core detector. It answers the question *"Where is the entropy?"* rather than *"How much entropy exists in total?"* |
| `EntropyVisualizer` | A report generator that translates numerical results into ASCII bar charts for quick visual inspection. |
| `analyze(data)` | The primary measurement function. Accepts raw byte content and returns a complete `EntropyProfile`. |
| `visualize(profile)` | Renders cluster boundaries as ASCII graphics, allowing human analysts to spot peaks without plotting software. |

### Configuration Constants

| Constant | Purpose |
|---|---|
| `CHUNK_SIZE` | Width of each analysis window, measured in bytes. |
| `HIGH_ENTROPY_THRESHOLD` | Integer cutoff above which a chunk is classified as likely encrypted. |
| `STEGANOGRAPHY_THRESHOLD` | Integer cutoff suggesting the presence of hidden embedded data. |
| `LOCALITY_SUSPICIOUS` | Integer score indicating that a spatial pattern deviates from normal file structure. |

### Glossary of Technical Terms

- **Byte**: The smallest addressable unit of memory, consisting of 8 bits.
- **Entropy**: A measure of unpredictability derived from the frequency distribution of byte values; higher values indicate more randomness.
- **Offset**: The distance in bytes from the beginning of a file to a specific location.
- **Payload**: The malicious or secret data carried by an exploit or hidden channel.
- **Forensic Artifact**: Any documented output from a forensic process that can be cited as evidence.
- **Deterministic System**: A computational process in which the same input invariably produces the same output, free from stochastic variation or precision loss.

### 【Scientific Note】
This module occasionally references conceptual frameworks associated with **Peirce** (semiotic triads), **Eco** (coding theory), and **Grice** (pragmatic maxims). These terms are not mystical incantations. They function exactly like a calibrated sensor: Peirce's categories detect sign-to-object relationships, Eco's codes detect layered encoding schemes, and Grice's maxims detect **logical fractures** where expected communication structure is violated. A sensor does not "believe" in what it measures; it registers formal deviations. Likewise, these terminological borrowings are formal observational operators, not hermeneutic mysticism.

---

## ESPAÑOL

### Módulo: `vigia/tools/entropy_locality.py` — Analizador de Localidad de Entropía

### ¿Qué es este módulo?
Este módulo es un instrumento de forense digital. Examina un archivo no como un simple conjunto de bytes, sino como un mapa espacial. Su propósito es revelar *dónde* se oculta el desorden dentro de un archivo, en lugar de reportar únicamente un promedio global. Una entropía alta concentrada en una vecindad específica es un indicio sólido de cargas útiles cifradas, inserción esteganográfica o código de inyección (shellcode). Al dividir los datos en ventanas secuenciales y medir cada zona de forma independiente mediante aritmética entera determinista, la herramienta genera un perfil espacial inmutable que el investigador puede leer, comparar y archivar.

### Conceptos clave

| Concepto | Definición en lenguaje sencillo |
|---|---|
| **Entropía global** | Un promedio único de aleatoriedad en todo el archivo; fácilmente manipulado mediante relleno o contenido mixto. |
| **Distribución espacial de entropía** | Un mapa de coordenadas que muestra cómo varía la aleatoriedad de una región a otra. |
| **Localidad de entropía** | La dirección específica (desplazamiento) donde aparece un desorden inusualmente alto. |
| **Ventana (Chunk)** | Una ventana de bytes de tamaño fijo tratada como una muestra independiente. |
| **Aritmética entera determinista** | Operaciones de conteo exactas utilizando frecuencias de números enteros y métricas racionales; archivos idénticos siempre producen perfiles idénticos, sin redondeo dependiente de la plataforma. |
| **Esteganografía** | La práctica de ocultar un mensaje secreto dentro de un archivo portador aparentemente ordinario. |
| **Código de shell (shellcode)** | Instrucciones a nivel máquina colocadas por un atacante para tomar el control de un proceso. |
| **Artefacto forense** | Cualquier objeto o estructura de datos producido durante una investigación que sirve como evidencia. |

### Componentes del módulo

| Componente | Rol científico |
|---|---|
| `EntropyProfile` | Registro inmutable—una vez creado, no puede alterarse—que almacena los valores de entropía de cada zona espacial. |
| `EntropyLocalityAnalyzer` | El detector central. Responde a la pregunta *«¿Dónde está la entropía?»* en lugar de *«¿Cuánta entropía hay en total?»*. |
| `EntropyVisualizer` | Generador de informes que traduce resultados numéricos a gráficos de barras ASCII para inspección visual rápida. |
| `analyze(data)` | Función de medición principal. Acepta contenido en bytes crudos y devuelve un `EntropyProfile` completo. |
| `visualize(profile)` | Dibuja los límites de los conglomerados como gráficos ASCII, permitiendo a los analistas identificar picos sin software de trazado. |

### Constantes de configuración

| Constante | Propósito |
|---|---|
| `CHUNK_SIZE` | Anchura de cada ventana de análisis, medida en bytes. |
| `HIGH_ENTROPY_THRESHOLD` | Umbral entero por encima del cual una ventana se clasifica como probablemente cifrada. |
| `STEGANOGRAPHY_THRESHOLD` | Umbral entero que sugiere la presencia de datos ocultos incrustados. |
| `LOCALITY_SUSPICIOUS` | Puntuación entera que indica que un patrón espacial se desvía de la estructura normal del archivo. |

### Glosario de términos técnicos

- **Byte**: La unidad de memoria direccionable más pequeña, consistente en 8 bits.
- **Entropía**: Medida de imprevisibilidad derivada de la distribución de frecuencias de valores de byte; valores más altos indican mayor aleatoriedad.
- **Desplazamiento (Offset)**: La distancia en bytes desde el inicio de un archivo hasta una ubicación específica.
- **Carga útil (Payload)**: Los datos maliciosos o secretos transportados por un exploit o canal oculto.
- **Artefacto forense**: Cualquier salida documentada de un proceso forense que puede citarse como evidencia.
- **Sistema determinista**: Proceso computacional en el que la misma entrada produce invariablemente la misma salida, libre de variación estocástica o pérdida de precisión.

### 【Nota Científica】
Este módulo hace referencia ocasional a marcos conceptuales asociados con **Peirce** (tríadas semióticas), **Eco** (teoría de los códigos) y **Grice** (máximas pragmáticas). Estos términos no son invocaciones místicas. Funcionan exactamente como un sensor calibrado: las categorías de Peirce detectan relaciones signo-objeto, los códigos de Eco detectan esquemas de codificación en capas, y las máximas de Grice detectan **rupturas lógicas** donde la estructura comunicativa esperada es violada. Un sensor no «cree» en lo que mide; registra desviaciones formales. Así, estos préstamos terminológicos son operadores observacionales formales, no misticismo hermenéutico.

---

## РУССКИЙ

### Модуль: `vigia/tools/entropy_locality.py` — Анализатор пространственной энтропии

### Что представляет собой этот модуль?
Этот модуль — инструмент цифровой криминалистики. Он исследует файл не как простой набор байтов, а как пространственную карту. Его цель — выявить, *где* именно в файле скрывается беспорядок, а не сообщить лишь общее среднее значение. Высокая энтропия, сконцентрированная в конкретной области, является надёжным признаком зашифрованной полезной нагрузки, стеганографической вставки или инжектированного шеллкода. Разделяя данные на последовательные блоки и измеряя каждую зону независимо с помощью детерминированной целочисленной арифметики, инструмент создаёт неизменяемый пространственный профиль, который следователь может прочитать, сравнить и заархивировать.

### Ключевые понятия

| Понятие | Определение простым языком |
|---|---|
| **Глобальная энтропия** | Единое среднее значение случайности по всему файлу; легко манипулируется за счёт заполнения или смешанного содержимого. |
| **Пространственное распределение энтропии** | Координатная карта, показывающая, как изменяется случайность от одного региона к другому. |
| **Локальность энтропии** | Конкретный адрес (смещение), где появляется необычно высокий беспорядок. |
| **Блок (Chunk)** | Окно байтов фиксированного размера, рассматриваемое как независимый образец. |
| **Детерминированная целочисленная арифметика** | Точные операции подсчёта с использованием частот целых чисел и рациональных метрик; идентичные файлы всегда дают идентичные профили без зависимого от платформы округления. |
| **Стеганография** | Практика сокрытия секретного сообщения внутри иначе обычного файла-носителя. |
| **Шеллкод** | Машинные инструкции, размещённые злоумышленником для захвата управления процессом. |
| **Следственный артефакт** | Любой объект или структура данных, полученные в ходе расследования и служащие доказательством. |

### Компоненты модуля

| Компонент | Научная роль |
|---|---|
| `EntropyProfile` | Неизменяемая запись — после создания не подлежит изменению — хранящая значения энтропии для каждой пространственной зоны. |
| `EntropyLocalityAnalyzer` | Основной детектор. Отвечает на вопрос *«Где находится энтропия?»*, а не *«Какова общая энтропия?»*. |
| `EntropyVisualizer` | Генератор отчётов, преобразующий числовые результаты в ASCII-диаграммы для быстрой визуальной проверки. |
| `analyze(data)` | Основная функция измерения. Принимает необработанное байтовое содержимое и возвращает полный `EntropyProfile`. |
| `visualize(profile)` | Отображает границы кластеров в виде ASCII-графики, позволяя аналитикам выявлять пики без программ построения графиков. |

### Конфигурационные константы

| Константа | Назначение |
|---|---|
| `CHUNK_SIZE` | Размер каждого окна анализа в байтах. |
| `HIGH_ENTROPY_THRESHOLD` | Целочисленный порог, выше которого блок классифицируется как вероятно зашифрованный. |
| `STEGANOGRAPHY_THRESHOLD` | Целочисленный порог, указывающий на наличие скрытых встроенных данных. |
| `LOCALITY_SUSPICIOUS` | Целочисленная оценка, свидетельствующая о том, что пространственный паттерн отклоняется от нормальной структуры файла. |

### Глоссарий технических терминов

- **Байт**: Наименьшая адресуемая единица памяти, состоящая из 8 бит.
- **Энтропия**: Мера непредсказуемости, выводимая из распределения частот значений байтов; более высокие значения указывают на большую случайность.
- **Смещение (Offset)**: Расстояние в байтах от начала файла до конкретного местоположения.
- **Полезная нагрузка (Payload)**: Вредоносные или секретные данные, переносимые эксплойтом или скрытым каналом.
- **Следственный артефакт**: Любой документированный результат судебного процесса, который может быть использован в качестве доказательства.
- **Детерминированная система**: Вычислительный процесс, в котором один и тот же вход неизменно приводит к одному и тому же выходу, свободному от стохастических вариаций или потери точности.

### 【Научное примечание】
В модуле иногда используются концепции, связанные с **Пирсом** (семиотические триады), **Эко** (теория кодов) и **Грайсом** (прагматические максимы). Эти термины не являются мистическими формулами. Они работают точно так же, как калиброванный датчик: категории Пирса выявляют отношения знак–объект, коды Эко обнаруживают многоуровневые схемы кодирования, а максимы Грайса фиксируют **логические разрывы**, где нарушается ожидаемая коммуникативная структура. Датчик не «верит» в то, что измеряет; он регистрирует формальные отклонения. Таким образом, эти заимствованные термины — это формальные наблюдательные операторы, а не герменевтический мистицизм.

---

## 中文

### 模块：`vigia/tools/entropy_locality.py` — 熵空间局部分析器

### 本模块是什么？
本模块是一件数字取证工具。它检查文件时，不是将其视为一袋杂乱的字节，而是视为一张空间地图。其目的在于揭示文件内部*何处*藏匿着无序，而非仅报告一个总平均值。特定邻域内的高熵是加密载荷、隐写术嵌入或注入式 shellcode 的强指示信号。该工具将数据切分为连续的块，并通过**确定性整数运算**独立测量每个区域，从而生成不可变更的空间剖面，供调查人员阅读、比对与存档。

### 核心概念

| 概念 | 通俗定义 |
|---|---|
| **全局熵** | 对整个文件随机程度的单一平均值；易于通过填充或混合内容被操纵。 |
| **熵空间分布** | 一张坐标图，显示随机性如何从一个区域变化到另一个区域。 |
| **熵局部性** | 出现异常高无序状态的具体地址（偏移量）。 |
| **数据块 (Chunk)** | 一个固定大小的字节窗口，被视为独立的样本。 |
| **确定性整数运算** | 使用整数频率与有理度量的精确计数操作；相同文件永远产生相同的剖面，不存在因平台而异的舍入误差。 |
| **隐写术** | 将秘密信息隐藏在看似普通的载体文件中的技术。 |
| **植入代码 (Shellcode)** | 攻击者放置的机器级指令，用于夺取进程控制权。 |
| **取证工件** | 调查过程中产生的、可作为证据使用的任何对象或数据结构。 |

### 模块组件

| 组件 | 科学作用 |
|---|---|
| `EntropyProfile`（熵剖面） | 不可变记录——一经创建便不可更改——存储每个空间区域的熵值。 |
| `EntropyLocalityAnalyzer`（熵局部性分析器） | 核心探测器。回答*"熵在哪里？"*，而非*"总共有多少熵？"* |
| `EntropyVisualizer`（熵可视化器） | 报告生成器，将数值结果转换为 ASCII 条形图，以便快速目视检查。 |
| `analyze(data)`（分析函数） | 主要测量函数。接收原始字节内容，返回完整的 `EntropyProfile`。 |
| `visualize(profile)`（可视化函数） | 将聚类边界渲染为 ASCII 图形，使分析人员无需绘图软件即可发现峰值。 |

### 配置常量

| 常量 | 用途 |
|---|---|
| `CHUNK_SIZE`（块大小） | 每个分析窗口的宽度，以字节为单位。 |
| `HIGH_ENTROPY_THRESHOLD`（高熵阈值） | 整数阈值，超过此值的数据块被归类为疑似加密内容。 |
| `STEGANOGRAPHY_THRESHOLD`（隐写阈值） | 整数阈值，暗示存在隐藏的嵌入数据。 |
| `LOCALITY_SUSPICIOUS`（局部可疑度） | 整数评分，表示某种空间模式偏离了正常文件结构。 |

### 术语表

- **字节（Byte）**：内存中最小的可寻址单元，由 8 位组成。
- **熵（Entropy）**：从字节值频率分布中导出的不可预测性度量；较高的值表示较强的随机性。
- **偏移量（Offset）**：从文件开头到特定位置的字节距离。
- **载荷（Payload）**：由漏洞利用程序或隐蔽信道携带的恶意或秘密数据。
- **取证工件（Forensic Artifact）**：取证过程中产生的任何可作为证据引用的有文档记录的输出。
- **确定性系统（Deterministic System）**：相同输入必然产生相同输出的计算过程，不存在随机变化或精度损失。
- **逻辑断裂**：预期通信结构遭到违反时出现的确定性不连续性，是模块通过熵空间分析所能检测到的客观现象。

### 【科学说明】
本模块偶尔借用**皮尔斯**（Peirce）符号学三元组、**艾柯**（Eco）编码理论以及**格赖斯**（Grice）语用学准则的概念框架。这些术语并非神秘主义咒语。它们的功能与校准后的传感器完全一致：皮尔斯的范畴用于检测符号与对象之间的形式关系；艾柯的编码用于识别分层编码结构；格赖斯的准则用于侦测**逻辑断裂**——即预期通信结构遭到违反的位置。传感器不会"相信"它所测量的对象，它只记录形式偏差。因此，这些术语借用的本质是形式化观测算子，而非诠释学的神秘主义。

---

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
