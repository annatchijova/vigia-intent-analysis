<!--
VIGIA Academic Documentation
Module: 2640bfa6
Batch ID: vigia-doc-0085-2640bfa6
Generated: 2026-05-20T14:56:47.862861+00:00
-->

---

## ENGLISH

### What Is This Module?
The **VIGÍA Forensic PDF Reporter** is a deterministic document-assembly system. It transforms a structured expert verdict—called a `ForensicVerdict`—into a court-admissible PDF report. Think of it as a scientific instrument that takes raw analytical conclusions and encodes them into a standardized legal document. The system guarantees reproducibility by relying exclusively on **deterministic integer arithmetic** for all checksums, timestamps, counters, and threshold comparisons. No floating-point approximations are used at any stage, ensuring that two identical inputs always yield bit-identical outputs.

The module contains three principal components:
1. **PeirceDaubertStyles** — A typographic-formatting engine that applies court-approved visual standards (fonts, margins, heading hierarchies) analogous to a journal's LaTeX template.
2. **VigiaForensicReporter** — The core assembly engine. It ingests a `ForensicVerdict`, maps its contents across four technical layers, and renders them into a structured PDF.
3. **Convenience Functions (`generate_forensic_pdf`, `generate_report`)** — One-button interfaces that initiate the full pipeline, returning the exact file path of the generated document.

### Key Concepts

| Term | Plain-Language Definition | Role in the Module |
|---|---|---|
| **ForensicVerdict** | A structured data object containing the final expert opinion, findings, and custody metadata. | Serves as the sole input to the reporter. |
| **Peirce Semiotics** | A triadic framework: *Firstness* (raw possibility), *Secondness* (actual fact), *Thirdness* (governing law/rule). | Structures reasoning within each of the four technical analysis layers. |
| **Daubert Standard** | Legal criteria for admitting expert scientific evidence; demands testability, known error rates, and peer review. | Ensures the report's methodology section meets admissibility requirements. |
| **Digital Chain of Custody** | An auditable trail linking every digital artifact to its origin via cryptographic hash and database records. | Enforced through SHA-256 integer fingerprints and SQLite relational links. |
| **Deterministic Integer Arithmetic** | Exact mathematical operations on whole numbers, free from rounding or representation error. | Guarantees that hashes, timestamps, layer metrics, and counts are fully reproducible. |
| **σ Deviation (Sigma)** | A quantized measure of variation from a baseline, expressed as an exact integer ratio to avoid rounding ambiguity. | Evaluated in the four technical layers to flag anomalies without floating-point drift. |
| **Logic Break** | A deterministic indicator of discontinuity within an integer-verified process, signaling a breach or anomaly. | Triggers detailed logging when a layer's integer metrics exceed exact thresholds. |
| **SHA-256** | A cryptographic hash algorithm yielding a 256-bit integer fingerprint. | Provides integrity verification for every forensic artifact. |
| **SQLite Link** | A persistent reference pointer stored in a relational database file. | Creates a queryable, tamper-evident custody record. |

### Glossary

- **Artifact** — Any digital object collected as evidence (e.g., a memory image, log file, or network packet capture).
- **Firstness** — The mode of being of a quality or possibility; in forensic terms, the latent potential for an anomaly before it is triggered.
- **Secondness** — The mode of being of an actual fact or event; the moment an anomaly is detected.
- **Thirdness** — The mode of being of a law or habit; the deterministic rule that connects a detected event to its legal or technical interpretation.
- **Grado Pericial** — Expert grade; the formal evidentiary standard required of a forensic report in legal proceedings.
- **Deterministic System** — A system in which identical initial conditions always produce identical outputs, excluding all probabilistic approximation.

### 【Scientific Note】
The terminology of Peirce, Eco, and Grice is sometimes mistaken for metaphysical speculation. In this module, these terms function exactly like a **multi-layered sensor array**. **Firstness** is analogous to raw sensor voltage—unprocessed potential. **Secondness** is the triggered threshold alarm—an actual event. **Thirdness** is the calibrated inference engine that maps the alarm to a known failure mode. Umberto Eco's code theory and Grice's cooperative maxims serve as communication-protocol specifications, ensuring that the report's signs (text, tables, hashes) unambiguously transmit the expert's findings to the court, just as a deterministic bus protocol transmits sensor data to a controller without floating-point drift.

---

## ESPAÑOL

### ¿Qué es este módulo?
El **Reportero Forense PDF VIGÍA** es un sistema determinista de ensamblaje de documentos. Transforma un veredicto experto estructurado—denominado `ForensicVerdict`—en un informe pericial PDF admisible en juicio. Considérelo como un instrumento científico que toma conclusiones analíticas brutas y las codifica en un documento legal estandarizado. El sistema garantiza la reproducibilidad al basarse exclusivamente en **aritmética entera determinista** para todas las sumas de verificación, marcas temporales, conteos y comparaciones de umbrales. No se utilizan aproximaciones de coma flotante en ninguna etapa, asegurando que dos entradas idénticas siempre produzcan salidas idénticas bit a bit.

El módulo contiene tres componentes principales:
1. **PeirceDaubertStyles** — Motor de formato tipográfico que aplica estándares visuales aprobados para tribunales (fuentes, márgenes, jerarquías de títulos), análogo a una plantilla LaTeX de revista científica.
2. **VigiaForensicReporter** — Motor de ensamblaje central. Ingiere un `ForensicVerdict`, asigna sus contenidos a cuatro capas técnicas y los renderiza en un PDF estructurado.
3. **Funciones de conveniencia (`generate_forensic_pdf`, `generate_report`)** — Interfaces de un solo botón que inician la canalización completa, devolviendo la ruta exacta del archivo generado.

### Conceptos clave

| Término | Definición en lenguaje sencillo | Rol en el módulo |
|---|---|---|
| **ForensicVerdict** | Objeto de datos estructurado que contiene la opinión pericial final, los hallazgos y los metadatos de custodia. | Fuente de entrada única del generador. |
| **Semiótica de Peirce** | Marco triádico: *Primedad* (posibilidad bruta), *Segundidad* (hecho real), *Terceridad* (ley/regla gobernante). | Estructura el razonamiento dentro de cada una de las cuatro capas de análisis técnico. |
| **Estándar Daubert** | Criterios legales para admitir evidencia científica experta; exige comprobabilidad, tasas de error conocidas y revisión por pares. | Garantiza que la sección de metodología del informe cumpla los requisitos de admisibilidad. |
| **Cadena de Custodia Digital** | Rastro auditable que vincula cada artefacto digital con su origen mediante hash criptográfico y registros de base de datos. | Aplicada mediante huellas dactilares enteras SHA-256 y enlaces relacionales SQLite. |
| **Aritmética Entera Determinística** | Operaciones matemáticas exactas sobre números enteros, libres de redondeo o error de representación. | Asegura que los hashes, marcas temporales, métricas de capa y conteos sean plenamente reproducibles. |
| **Desviación σ (Sigma)** | Medida cuantizada de variación respecto a una línea base, expresada como razón entera exacta para evitar ambigüedad de redondeo. | Evaluada en las cuatro capas técnicas para señalar anomalías sin deriva de coma flotante. |
| **Ruptura Lógica** | Indicador determinista de discontinuidad dentro de un proceso verificado por enteros, señalando una brecha o anomalía. | Activa registro detallado cuando las métricas enteras de una capa exceden umbrales exactos. |
| **SHA-256** | Algoritmo hash criptográfico que produce una huella digital de 256 bits como número entero. | Provee verificación de integridad para cada artefacto forense. |
| **Enlace SQLite** | Puntero de referencia persistente almacenado en un archivo de base de datos relacional. | Crea un registro de custodia consultable y resistente a alteraciones. |

### Glosario

- **Artefacto** — Cualquier objeto digital recopilado como evidencia (p. ej., imagen de memoria, archivo de registro o captura de paquetes de red).
- **Primedad** — Modo de ser de una cualidad o posibilidad; en términos forenses, el potencial latente de una anomalía antes de que se active.
- **Segundidad** — Modo de ser de un hecho o evento actual; el momento en que se detecta una anomalía.
- **Terceridad** — Modo de ser de una ley o hábito; la regla determinista que conecta un evento detectado con su interpretación legal o técnica.
- **Grado Pericial** — Nivel experto; el estándar probatorio formal exigido a un informe forense en procedimientos legales.
- **Sistema Determinista** — Sistema en el que condiciones iniciales idénticas siempre producen salidas idénticas, excluyendo toda aproximación probabilística.

### 【Nota Científica】
La terminología de Peirce, Eco y Grice es a veces confundida con especulación metafísica. En este módulo, estos términos operan exactamente como una **matriz de sensores multicapa**. La **Primedad** es análoga al voltaje crudo del sensor—potencial no procesado. La **Segundidad** es la alarma de umbral activada—un evento real. La **Terceridad** es el motor de inferencia calibrado que asocia la alarma con un modo de fallo conocido. La teoría de códigos de Umberto Eco y las
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## РУССКИЙ

### Что это за модуль?
**Форензический PDF-репортёр VIGÍA** — это детерминированная система сборки документов. Он преобразует структурированный экспертный вердикт (`ForensicVerdict`) в PDF-отчёт, допустимый в суде. Представьте его как научный инструмент, который принимает сырые аналитические заключения и кодирует их в стандартизированный юридический документ. Система обеспечивает воспроизводимость, опираясь исключительно на **детерминированную целочисленную арифметику** при вычислении контрольных сумм, временных меток, счётчиков и сравнении порогов. Никаких приближений с плавающей запятой на каком-либо этапе не используется, что гарантирует: два идентичных входа всегда порождают побитово идентичный выход.

Модуль содержит три основных компонента: **PeirceDaubertStyles** — типографский движок, применяющий утверждённые судом визуальные стандарты; **VigiaForensicReporter** — центральный сборочный движок, принимающий `ForensicVerdict` и визуализирующий его в структурированный PDF; **функции-обёртки** (`generate_forensic_pdf`, `generate_report`) — однокнопочные интерфейсы, инициирующие полный конвейер и возвращающие точный путь к сгенерированному файлу.

Четыре технических слоя анализа — семиотика Пирса, стандарт Добера, цифровая цепочка хранения улик и детерминированная целочисленная арифметика — составляют аналитическую основу каждого формируемого отчёта, обеспечивая его полную воспроизводимость при последующей проверке.

### Ключевые концепции
| Концепция | Определение | Техническая роль |
|---|---|---|
| ForensicVerdict | Структурированный объект данных, содержащий итоговое экспертное мнение, выводы и метаданные хранения | Единственный источник входных данных репортёра |
| Семиотика Пирса | Триадическая схема: Первичность (потенциал), Вторичность (факт), Третичность (закон/правило) | Структурирует рассуждение в каждом из четырёх технических слоёв |
| Стандарт Добера | Правовые критерии допустимости экспертных научных доказательств | Обеспечивает соответствие методологии отчёта требованиям допустимости |
| Цифровая цепочка хранения улик | Проверяемый след, связывающий каждый форензический артефакт с его происхождением через криптографический хэш | Реализован через целочисленные отпечатки SHA-256 и реляционные связи SQLite |
| Детерминированная целочисленная арифметика | Точные математические операции над целыми числами без ошибок округления | Гарантирует полную воспроизводимость хэшей, меток времени и метрик слоёв |
| Отклонение σ (Сигма) | Квантованная мера отклонения от базовой линии, выраженная точным целочисленным отношением | Оценивается в четырёх технических слоях для обнаружения аномалий |
| Логический разрыв | Детерминированный индикатор разрыва внутри целочисленно верифицированного процесса | Инициирует детальное протоколирование при превышении порогов |
| SHA-256 | Криптографический алгоритм хэширования, дающий 256-битный целочисленный отпечаток | Обеспечивает проверку целостности каждого форензического артефакта |

> **【Научное примечание】**
> Терминология Пирса, Эко и Грайса — это не мистика, а формальная аналитическая механика. Как спектрометр преобразует фотонные взаимодействия в дискретные целочисленные отсчёты, этот модуль преобразует сигналы улик в детерминированные целочисленные оценки. Целочисленная арифметика гарантирует воспроизводимость в суде без округлений и аппроксимаций. Любое нарушение логики в цепочке артефактов фиксируется как целочисленный флаг, а не интуитивное суждение.

### Глоссарий
1. **Форензический артефакт** — Любой цифровой объект, собранный в качестве доказательства.
2. **Первичность** — Способ существования качества или возможности; в судебных терминах — скрытый потенциал аномалии до её активации.
3. **Вторичность** — Способ существования реального факта; момент обнаружения аномалии.
4. **Третичность** — Способ существования закона или привычки; детерминированное правило, связывающее обнаруженное событие с его интерпретацией.
5. **Стандарт Добера** — Правовой критерий допустимости научных доказательств, требующий проверяемости и воспроизводимости.
6. **Детерминированная система** — Система, в которой идентичные начальные условия всегда порождают идентичные выходные данные.
7. **Цепочка хранения улик** — Проверяемый след, связывающий каждый форензический артефакт с его происхождением.
8. **Логический разрыв** — Детерминированный индикатор разрыва в целочисленно верифицированном процессе.
9. **Воспроизводимость** — Согласованность результатов при независимом повторном анализе.
10. **SHA-256** — Криптографический алгоритм хэширования, дающий 256-битный целочисленный отпечаток целостности.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## 中文

### 这是什么模块？
**VIGÍA取证PDF报告器**是一个确定性文档组装系统。它将结构化的专家裁决（`ForensicVerdict`）转换为法庭可采纳的PDF报告。可以将其视为一种科学仪器，将原始分析结论编码为标准化法律文件。系统通过在所有校验和、时间戳、计数器和阈值比较中完全依赖**精确整数运算**来保证可重现性。任何阶段均不使用近似运算，确保两个相同的输入始终产生逐位相同的输出。

模块包含三个主要组件：**PeirceDaubertStyles**——应用法院认可视觉标准的排版引擎；**VigiaForensicReporter**——核心组装引擎，接收`ForensicVerdict`并将其内容映射到四个技术层后渲染为结构化PDF；**便捷函数**（`generate_forensic_pdf`、`generate_report`）——启动完整流程并返回生成文件精确路径的一键式接口。

四个技术分析层——皮尔斯符号学、道伯特标准、数字证据监管链和精确整数运算——构成每份生成报告的分析基础，确保其在后续审查中完全可重现。

### 关键概念
| 概念 | 定义 | 技术作用 |
|---|---|---|
| ForensicVerdict | 包含最终专家意见、调查结论和监管元数据的结构化数据对象 | 报告器的唯一输入源 |
| 皮尔斯符号学 | 三元框架：初性（原始可能性）、二性（实际事实）、三性（支配规律） | 构建四个技术分析层中的推理结构 |
| 道伯特标准 | 专家科学证据可采性的法律标准，要求可测试性、已知错误率和同行评审 | 确保报告方法论部分满足可采性要求 |
| 数字证据监管链 | 通过密码学哈希和数据库记录将每个数字取证工件与其来源关联的可审计轨迹 | 通过SHA-256整数指纹和SQLite关联链接强制执行 |
| 精确整数运算 | 对整数进行精确数学运算，不存在舍入或表示误差 | 保证哈希、时间戳、层指标和计数的完全可重现性 |
| σ偏差（Sigma） | 相对于基准线的量化变异度量，以精确整数比表示 | 在四个技术层中评估以标记异常 |
| 逻辑断裂 | 整数验证过程中不连续性的确定性指标，表示违规或异常 | 当某层整数指标超过精确阈值时触发详细记录 |
| SHA-256 | 产生256位整数指纹的密码学哈希算法 | 为每个取证工件提供完整性验证 |

> **【科学说明】**
> 皮尔斯（Peirce）、艾柯（Eco）和格赖斯（Grice）的术语并非神秘主义，而是形式化的分析机制。如同光谱仪将光子相互作用转换为离散整数计数，本模块将证据信号转换为确定性整数分数。精确整数运算确保法庭可重现性。取证工件链的逻辑断裂以整数标志事件形式被检测。

### 词汇表
1. **取证工件** — 作为证据收集的任何数字对象（如内存镜像、日志文件或网络数据包捕获）。
2. **初性** — 质量或可能性的存在方式；在取证意义上，异常被触发前的潜在可能。
3. **二性** — 实际事实或事件的存在方式；检测到异常的时刻。
4. **三性** — 规律或习惯的存在方式；将检测到的事件与其法律或技术解释相连的确定性规则。
5. **道伯特标准** — 专家科学证据可采性的法律标准，要求可测试性和可重现性。
6. **确定性系统** — 相同初始条件始终产生相同输出的系统。
7. **证据监管链** — 将每个取证工件与其来源关联的可审计轨迹。
8. **逻辑断裂** — 整数验证过程中的确定性不连续性指标。
9. **可重现性** — 在独立重复分析中获得一致结果的能力。
10. **SHA-256** — 产生256位整数完整性指纹的密码学哈希算法。

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
