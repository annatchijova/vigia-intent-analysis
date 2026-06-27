<!--
VIGIA Academic Documentation
Module: 7b4e076e
Batch ID: vigia-doc-0100-7b4e076e
Generated: 2026-05-20T14:56:47.866285+00:00
-->

# Module Documentation: `vigia/inference/check_determinism.py`

---

## ENGLISH

### What Is This Module?

`vigia/inference/check_determinism.py` is a forensic verification script that tests whether the analytical tools in the VIGÍA pipeline produce identical outputs on every execution. It runs each designated tool multiple times on the same evidence, computes a SHA-256 cryptographic fingerprint of each output report, and confirms that all fingerprints are identical. Think of it as a calibration check for a laboratory instrument: before trusting a spectrometer's reading in court, a scientist verifies that the instrument produces the same measurement when exposed to the same standard twice. This script performs the equivalent check for digital forensic tools.

VIGÍA borrows terminology from semiotics—Charles Sanders Peirce, Umberto Eco, and H.P. Grice—to describe information structures. These terms are formal abstractions, not mysticism. Consider the sensor analogy: in engineering, we call a physical sensor a "witness" to an event even though it lacks consciousness; it simply records data. Likewise, Peirce's sign, Eco's code, and Grice's maxims are analytical lenses for classifying how digital evidence carries meaning. They provide a rigorous logical framework; they do not invoke supernatural agency. When this module checks for determinism, it is ensuring that the "sensor" (the analytical tool) records the same "testimony" (the report) every time under identical conditions.

### Key Concepts

**Operational Outputs and Configuration**

| Label | Plain-Language Definition | Scientific Role |
|---|---|---|
| Exit code 0 | The script finishes and reports that all repeated analyses produced identical fingerprints. | Signals that the tool is deterministic and forensically admissible. |
| Non-zero exit | The script finishes and reports that at least one fingerprint differed across runs. | Signals non-determinism; the pipeline requires inspection before legal use. |
| VOLATILE_KEYS | Metadata fields that legitimately change between runs, such as timestamps or temporary paths. | Stripped from reports before hashing so they do not trigger false mismatches. |
| STABLE_TOOLS | Analytical methods engineered to produce bit-for-bit identical results on every execution. | The baseline tools whose determinism is being verified. |
| BRIDGE_TOOLS | Intermediate components that convert data between formats without altering meaning. | Must be deterministic; otherwise they introduce logical discontinuities in evidence handling. |
| _BRIDGE_CANDIDATES | New or modified intermediate tools currently under evaluation for stability. | Audited before promotion to full BRIDGE_TOOLS status to prevent non-determinism. |

**Determinism and Measurement**

| Concept | Plain-Language Definition | Scientific Role |
|---|---|---|
| Determinism | The property that a fixed input and fixed procedure always yield the same output. | The fundamental requirement for reproducible forensic science. |
| SHA-256 | A cryptographic hash function relying exclusively on deterministic integer arithmetic to produce a fixed-length fingerprint. | Provides an exact, computationally cheap method to detect even single-bit changes in output. |
| Evidence File | The digital object under investigation (disk image, log, packet capture, etc.). | The constant experimental input. |
| Forensic Admissibility | The standard that analytical methods must be repeatable and verifiable by independent parties. | The legal-scientific objective of the verification. |

### Glossary

- **Determinism**: A system state in which output is entirely predicted by input and algorithm, free of random variation.
- **SHA-256 Hash**: A deterministic integer fingerprint of a data object. Any alteration, however minor, produces a completely different hash value.
- **Non-determinism**: Behavior causing identical inputs to yield different outputs across runs, typically from hidden state, concurrency, or non-integer approximations (the latter excluded here by design).
- **Chain of Custody**: The documented, unbroken lineage of evidence handling. Non-determinism constitutes a logical breach in this chain.
- **Integer Arithmetic**: Exact mathematical operations on whole numbers, without the rounding errors inherent to floating-point representation. SHA-256 is built entirely upon bitwise integer operations.
- **Volatile Key**: A metadata attribute that changes between experimental trials and must be neutralized to avoid false conclusions.
- **Bridge Candidate**: A provisional processing component undergoing stability trials before full operational acceptance.

### 【Scientific Note】

In forensic science, reproducibility is not a procedural nicety—it is an epistemological requirement. A finding that cannot be reproduced is not a finding; it is a rumor. The VIGÍA pipeline uses SHA-256 integer hashing as its reproducibility witness precisely because integer operations are immune to the non-deterministic rounding that can affect probabilistic methods. When this module reports exit code 0, it is asserting, under deterministic guarantee, that the analytical instrument is scientifically valid. When it reports a non-zero exit, it is triggering an epistemic alarm: something in the pipeline is introducing hidden state or approximation that violates the chain of custody. Treat a non-zero exit as a laboratory instrument that has failed calibration—do not use it to testify in court until the failure source is identified and corrected.

---

## ESPAÑOL

### ¿Qué es este módulo?

`vigia/inference/check_determinism.py` es un script de verificación forense que comprueba si las herramientas analíticas de la tubería VIGÍA producen resultados idénticos en cada ejecución. Ejecuta cada herramienta designada varias veces sobre la misma evidencia, calcula una huella criptográfica SHA-256 de cada informe de salida y confirma que todas las huellas son idénticas. Piense en él como una verificación de calibración para un instrumento de laboratorio: antes de confiar en la lectura de un espectrómetro en un tribunal, un científico verifica que el instrumento produce la misma medición cuando se expone al mismo estándar dos veces. Este script realiza la verificación equivalente para herramientas de forense digital.

### Conceptos clave

**Salidas y configuración operativas**

| Etiqueta | Definición en lenguaje sencillo | Rol científico |
|---|---|---|
| Código de salida 0 | El script termina e informa que todos los análisis repetidos produjeron huellas digitales idénticas. | Señala que la herramienta es determinista y forensemente admisible. |
| Salida distinta de cero | El script termina e informa que al menos una huella difirió entre ejecuciones. | Señala no determinismo; la tubería requiere inspección antes de su uso legal. |
| VOLATILE_KEYS | Campos de metadatos que cambian legítimamente entre ejecuciones, como marcas de tiempo o rutas temporales. | Se eliminan de los informes antes del hash para evitar falsas discrepancias. |
| STABLE_TOOLS | Métodos analíticos diseñados para producir resultados idénticos bit a bit en cada ejecución. | Herramientas base cuyo determinismo se verifica. |
| BRIDGE_TOOLS | Componentes intermedios que convierten datos entre formatos sin alterar el significado. | Deben ser deterministas; de lo contrario, introducen discontinuidades lógicas en el manejo de evidencia. |
| _BRIDGE_CANDIDATES | Herramientas intermedias nuevas o modificadas actualmente en evaluación de estabilidad. | Auditadas antes de su promoción a estado BRIDGE_TOOLS para prevenir no determinismo. |

**Determinismo y medición**

| Concepto | Definición en lenguaje sencillo | Rol científico |
|---|---|---|
| Determinismo | La propiedad por la cual una entrada y un procedimiento fijos siempre producen la misma salida. | Requisito fundamental para la ciencia forense reproducible. |
| SHA-256 | Función hash criptográfica que se basa exclusivamente en aritmética entera determinista para producir una huella de longitud fija. | Método exacto y computacionalmente económico para detectar cambios de un solo bit en la salida. |
| Archivo de evidencia | Objeto digital bajo investigación (imagen de disco, registro, captura de paquetes, etc.). | Entrada experimental constante. |
| Admisibilidad forense | Estándar que exige que los métodos analíticos sean repetibles y verificables por partes independientes. | Objetivo científico-jurídico de la verificación. |

### Glosario

- **Determinismo**: Estado del sistema en el que la salida está enteramente determinada por la entrada y el algoritmo, libre de variación aleatoria.
- **Hash SHA-256**: Huella digital determinista de un objeto de datos. Cualquier alteración, por mínima que sea, produce un valor hash completamente diferente.
- **No determinismo**: Comportamiento que hace que entradas idénticas produzcan salidas diferentes entre ejecuciones, típicamente por estado oculto, concurrencia o aproximaciones no enteras (estas últimas excluidas aquí por diseño).
- **Cadena de custodia**: Linaje documentado e ininterrumpido del manejo de evidencia. El no determinismo constituye una ruptura lógica en esta cadena.
- **Aritmética entera**: Operaciones matemáticas exactas sobre números enteros, sin los errores de redondeo inherentes a la representación de punto flotante. SHA-256 se construye enteramente sobre operaciones enteras bit a bit.
- **Clave volátil**: Atributo de metadatos que cambia entre ensayos experimentales y debe neutralizarse para evitar conclusiones falsas.
- **Candidato a puente**: Componente de procesamiento provisional que atraviesa pruebas de estabilidad antes de su aceptación operativa completa.

### 【Nota Científica】

En la ciencia forense, la reproducibilidad no es una formalidad procedimental—es un requisito epistemológico. Un hallazgo que no puede reproducirse no es un hallazgo; es un rumor. La tubería VIGÍA utiliza el hash entero SHA-256 como testigo de reproducibilidad precisamente porque las operaciones enteras son inmunes al redondeo no determinista que puede afectar a los métodos probabilísticos. Cuando este módulo informa un código de salida 0, afirma, bajo garantía determinista, que el instrumento analítico es científicamente válido. Cuando informa una salida distinta de cero, activa una alarma epistémica: algo en la tubería está introduciendo estado oculto o aproximación que viola la cadena de custodia. Trate una salida distinta de cero como un instrumento de laboratorio que ha fallado en la calibración—no lo use para testificar en un tribunal hasta que se identifique y corrija la fuente del fallo.

---

## РУССКИЙ

### Что это за модуль?

`vigia/inference/check_determinism.py` — это скрипт форензик-верификации, проверяющий, производят ли аналитические инструменты конвейера VIGÍA идентичные результаты при каждом запуске. Он запускает каждый назначенный инструмент несколько раз на одних и тех же доказательствах, вычисляет криптографический отпечаток SHA-256 каждого выходного отчёта и подтверждает, что все отпечатки идентичны. Представьте это как калибровочную проверку лабораторного инструмента: прежде чем доверять показаниям спектрометра в суде, учёный проверяет, что инструмент даёт одинаковые показания при воздействии одного и того же стандарта дважды. Данный скрипт выполняет аналогичную проверку для инструментов цифровой криминалистики.

### Ключевые понятия

**Операционные выходные данные и конфигурация**

| Метка | Определение простым языком | Научная роль |
|---|---|---|
| Код выхода 0 | Скрипт завершается и сообщает, что все повторные анализы дали идентичные отпечатки. | Сигнализирует о детерминированности инструмента и его форензик-допустимости. |
| Ненулевой выход | Скрипт завершается и сообщает, что хотя бы один отпечаток отличался между запусками. | Сигнализирует о недетерминированности; конвейер требует проверки перед юридическим использованием. |
| VOLATILE_KEYS | Поля метаданных, законно меняющиеся между запусками (временные метки, временные пути). | Удаляются из отчётов перед хешированием, чтобы не провоцировать ложные несоответствия. |
| STABLE_TOOLS | Аналитические методы, спроектированные для получения побитово идентичных результатов при каждом выполнении. | Базовые инструменты, чья детерминированность проверяется. |
| BRIDGE_TOOLS | Промежуточные компоненты, преобразующие данные между форматами без изменения смысла. | Должны быть детерминированными; иначе они вводят логические разрывы в обращение с доказательствами. |
| _BRIDGE_CANDIDATES | Новые или изменённые промежуточные инструменты, находящиеся на оценке стабильности. | Проходят аудит перед продвижением в статус BRIDGE_TOOLS для предотвращения недетерминированности. |

**Детерминизм и измерение**

| Понятие | Определение простым языком | Научная роль |
|---|---|---|
| Детерминизм | Свойство системы, при котором фиксированные входные данные и процедура всегда дают одинаковый результат. | Фундаментальное требование воспроизводимой криминалистики. |
| SHA-256 | Криптографическая хеш-функция, основанная исключительно на детерминированной целочисленной арифметике для получения отпечатка фиксированной длины. | Точный и экономичный метод обнаружения даже однобитовых изменений в выходных данных. |
| Файл доказательств | Цифровой объект под следствием (образ диска, журнал, перехват пакетов и т. д.). | Постоянный экспериментальный ввод. |
| Форензик-допустимость | Стандарт, требующий повторяемости и верифицируемости аналитических методов независимыми сторонами. | Правовой и научный объект верификации. |

### Глоссарий

- **Детерминизм**: Состояние системы, при котором вывод полностью определяется входными данными и алгоритмом, без случайной изменчивости.
- **Хеш SHA-256**: Детерминированный целочисленный отпечаток объекта данных. Любое изменение, сколь угодно малое, даёт совершенно другое хеш-значение.
- **Недетерминированность**: Поведение, при котором идентичные входные данные дают различные результаты при повторных запусках — как правило, из-за скрытого состояния, параллелизма или нецелочисленных приближений (последнее исключено здесь по замыслу).
- **Цепочка хранения**: Документированная, непрерывная история обращения с доказательствами. Недетерминированность представляет собой логический разрыв в этой цепочке.
- **Целочисленная арифметика**: Точные математические операции над целыми числами, без ошибок округления, присущих представлению с плавающей запятой. SHA-256 полностью построен на побитовых целочисленных операциях.
- **Волатильный ключ**: Атрибут метаданных, меняющийся между экспериментальными испытаниями и требующий нейтрализации для предотвращения ложных выводов.
- **Кандидат в мостовые инструменты**: Временный компонент обработки, проходящий испытания стабильности перед полным операционным принятием.

### 【Научное Примечание】

В криминалистике воспроизводимость — не процедурная формальность, а эпистемологическое требование. Результат, который нельзя воспроизвести, — не результат; это слух. Конвейер VIGÍA использует целочисленное хеширование SHA-256 в качестве свидетеля воспроизводимости именно потому, что целочисленные операции невосприимчивы к недетерминированному округлению, которое может затронуть вероятностные методы. Когда данный модуль сообщает код выхода 0, он утверждает — с детерминированной гарантией — что аналитический инструмент научно достоверен. Когда он сообщает ненулевой выход, он активирует эпистемологическую тревогу: что-то в конвейере вводит скрытое состояние или приближение, нарушающее цепочку хранения. Рассматривайте ненулевой выход как лабораторный инструмент, провалившийся при калибровке — не используйте его для свидетельства в суде до тех пор, пока источник сбоя не будет определён и исправлен.

---

## 中文

### 这是什么模块？

`vigia/inference/check_determinism.py` 是一个取证验证脚本，用于测试 VIGÍA 流水线中的分析工具在每次执行时是否产生相同的输出。它对同一证据多次运行每个指定工具，计算每份输出报告的 SHA-256 加密指纹，并确认所有指纹完全一致。将其理解为实验室仪器的校准检查：在法庭上信任光谱仪的读数之前，科学家要验证仪器在两次接触同一标准品时能产生相同的测量结果。本脚本对数字取证工具执行等效检查。

### 核心概念

**操作输出与配置**

| 标签 | 通俗定义 | 科学作用 |
|---|---|---|
| 退出码 0 | 脚本结束并报告所有重复分析产生了相同的指纹。 | 表明工具具有确定性且可作为取证工件采信。 |
| 非零退出 | 脚本结束并报告至少有一个指纹在运行之间存在差异。 | 表明存在非确定性；流水线在法律使用前需要检查。 |
| VOLATILE_KEYS | 在运行之间合理变化的元数据字段，如时间戳或临时路径。 | 哈希前从报告中剥离，以避免触发误判差异。 |
| STABLE_TOOLS | 设计为在每次执行时产生逐位相同结果的分析方法。 | 正在验证确定性的基线工具。 |
| BRIDGE_TOOLS | 在不改变含义的情况下在格式之间转换数据的中间组件。 | 必须是确定性的；否则会在证据处理中引入逻辑断裂。 |
| _BRIDGE_CANDIDATES | 目前正在接受稳定性评估的新或修改的中间工具。 | 在晋升为 BRIDGE_TOOLS 状态之前进行审计，以防止非确定性。 |

**确定性与测量**

| 概念 | 通俗定义 | 科学作用 |
|---|---|---|
| 确定性 | 固定输入和固定程序始终产生相同输出的属性。 | 可复现取证科学的基本要求。 |
| SHA-256 | 完全依赖确定性整数运算产生固定长度指纹的加密哈希函数。 | 提供精确且计算成本低廉的方法，可检测输出中的单比特变化。 |
| 证据文件 | 被调查的数字对象（磁盘镜像、日志、数据包捕获等）。 | 恒定的实验输入。 |
| 取证可采信性 | 分析方法必须可重复且可由独立方验证的标准。 | 验证的法律-科学目标。 |

### 术语表

- **确定性**：系统状态，其中输出完全由输入和算法预测，不存在随机变化。
- **SHA-256 哈希**：数据对象的确定性整数指纹。任何改动，无论多么微小，都会产生完全不同的哈希值。
- **非确定性**：导致相同输入在不同运行中产生不同输出的行为——通常由隐藏状态、并发或非整数近似引起（后者在此处被设计排除）。
- **保管链**：证据处理的有据可查的不间断谱系。非确定性构成此链中的逻辑断裂。
- **整数运算**：对整数的精确数学操作，不存在浮点表示固有的舍入误差。SHA-256 完全建立在按位整数操作之上。
- **挥发键**：在实验试验之间变化且必须中和以避免错误结论的元数据属性。
- **桥接候选工具**：在完全运营接受之前正在接受稳定性测试的临时处理组件。

### 【科学说明】

在取证科学中，可复现性不是程序上的礼节——它是认识论要求。无法复现的发现不是发现；它是谣言。VIGÍA 流水线使用 SHA-256 整数哈希作为可复现性见证，正是因为整数操作不受可能影响概率方法的非确定性舍入的影响。当本模块报告退出码 0 时，它在确定性保证下断言分析仪器具有科学有效性。当它报告非零退出时，它触发认识论警报：流水线中的某些内容引入了违反保管链的隐藏状态或近似值。将非零退出视为校准失败的实验室仪器——在识别并纠正故障源之前，不要使用它在法庭上作证。

---

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
