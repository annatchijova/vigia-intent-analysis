<!--
VIGIA Academic Documentation
Module: f02065bf
Batch ID: vigia-doc-0173-f02065bf
Generated: 2026-05-20T14:56:47.882087+00:00
-->

---

## ENGLISH

### What Is This Module?
The **Temporal Drift Detector** (`vigia/tools/temporal_drift.py`) is a deterministic forensic engine that examines sequences of timestamps extracted from digital artifacts. Its purpose is to reveal evidence tampering by identifying logically impossible chronologies—for example, a file modified before it was created, or an email sent in the future. The module treats time as a discrete, ordered set of integer values. All comparisons use deterministic integer arithmetic on whole seconds, ensuring exact reproducibility without fractional approximation.

### Key Concepts

**Core Classes**

| Class | Role | Plain-Language Description |
|-------|------|----------------------------|
| `TemporalEvent` | Data container | Represents one timestamped occurrence (e.g., file creation). Stores time as integer seconds since epoch. |
| `TemporalAnalysis` | Result object | Holds the outcome of a sequence check: consistent, anomalous, or impossible. |
| `TemporalDriftDetector` | Engine | Orchestrates the comparison of events using deterministic integer thresholds. |
| `TimestampExtractor` | Utility | Retrieves raw timestamp integers from artifact headers (PDF, email, etc.). |

**Analysis Functions**

| Function | Input | Output | Purpose |
|----------|-------|--------|---------|
| `analyze()` | List of `TemporalEvent` | `TemporalAnalysis` | Sequentially validates integer timestamps against logical order. |
| `extract_from_pdf()` | PDF artifact bytes | Integer timestamp | Reads creation/modification dates from PDF metadata as whole seconds. |
| `extract_from_email()` | Email header string | Integer timestamp | Parses sent/received dates from headers into integer epoch time. |

**Deterministic Thresholds (Constants)**

| Constant | Type | Forensic Meaning |
|----------|------|------------------|
| `MAX_CREATION_TO_SEND` | Integer (seconds) | Maximum plausible delay between file creation and transmission. |
| `MAX_MODIFY_TO_SEND` | Integer (seconds) | Maximum plausible delay between last modification and sending. |
| `MAX_FUTURE_TOLERANCE` | Integer (seconds) | Small integer buffer allowed versus system clock to account for benign skew; values beyond this indicate tampering. |
| `MIN_TIMEZONE_GAP_HOURS` | Integer (hours) | Minimum offset difference deemed suspicious when artifacts cross time zones without logical justification. |

### Glossary

- **Epoch time**: A universal integer count of seconds elapsed since a fixed reference date (1970-01-01 00:00:00 UTC), used to avoid time zone and calendar parsing ambiguity.
- **Deterministic integer arithmetic**: Mathematical operations on whole numbers that always yield the exact same result, with no approximation. Critical for reproducible forensic conclusions.
- **Temporal inconsistency**: A logical contradiction in timestamps (e.g., modification preceding creation) that cannot occur under normal system behavior and therefore indicates artifact manipulation.
- **Artifact**: Any digital object carrying potential evidence (files, emails, log entries).
- **Timestamp extraction**: The process of reading a raw temporal value from an artifact's metadata without interpreting or altering it.

### 【Scientific Note】
This module’s architecture employs semiotic concepts—Peirce’s theory of signs, Eco’s cultural codes, and Grice’s conversational maxims. These terms are **not** mysticism or literary criticism. They function as a formal **sensor model**: just as a physical sensor converts a stimulus (light, pressure) into a structured electrical signal, this detector converts raw timestamp traces (Peircean signs) into interpretable states via deterministic rules (Eco’s codes) and logical expectations (Grice’s maxims). A temporal inconsistency is simply a signal that violates the expected code, triggering an alert. The terminology describes an information-processing layer, not an esoteric belief system.

---

## ESPAÑOL

### ¿Qué es este módulo?
El **Detector de Deriva Temporal** (`vigia/tools/temporal_drift.py`) es un motor forense determinista que examina secuencias de marcas temporales extraídas de artefactos digitales. Su objetivo es revelar la manipulación de evidencia identificando cronologías lógicamente imposibles—por ejemplo, un archivo modificado antes de ser creado, o un correo enviado en el futuro. El módulo trata el tiempo como un conjunto discreto y ordenado de valores enteros. Todas las comparaciones utilizan aritmética entera determinista sobre segundos completos, garantizando reproducibilidad exacta sin aproximación fraccionaria.

### Conceptos clave

**Clases principales**

| Clase | Rol | Descripción |
|-------|-----|-------------|
| `TemporalEvent` | Contenedor de datos | Representa una ocurrencia con marca temporal. Almacena el tiempo como enteros de segundos desde la época. |
| `TemporalAnalysis` | Objeto de resultado | Contiene el resultado de la verificación: consistente, anómalo o imposible. |
| `TemporalDriftDetector` | Motor | Orquesta la comparación de eventos usando umbrales enteros deterministas. |
| `TimestampExtractor` | Utilidad | Recupera valores enteros de marcas temporales de encabezados (PDF, correo, etc.). |

**Funciones de análisis**

| Función | Entrada | Salida | Propósito |
|---------|---------|--------|-----------|
| `analyze()` | Lista de `TemporalEvent` | `TemporalAnalysis` | Valida secuencialmente marcas temporales enteras contra el orden lógico. |
| `extract_from_pdf()` | Bytes del artefacto PDF | Marca temporal entera | Lee fechas de creación/modificación de metadatos PDF en segundos enteros. |
| `extract_from_email()` | Cadena de encabezado de correo | Marca temporal entera | Analiza fechas de envío/recepción de encabezados a tiempo época entero. |

**Umbrales deterministas (Constantes)**

| Constante | Tipo | Significado forense |
|-----------|------|---------------------|
| `MAX_CREATION_TO_SEND` | Entero (segundos) | Retraso máximo plausible entre creación y transmisión. |
| `MAX_MODIFY_TO_SEND` | Entero (segundos) | Retraso máximo plausible entre última modificación y envío. |
| `MAX_FUTURE_TOLERANCE` | Entero (segundos) | Pequeño margen entero permitido respecto al reloj del sistema para tolerar desfase benigno; los valores que lo superen indican manipulación. |
| `MIN_TIMEZONE_GAP_HOURS` | Entero (horas) | Diferencia de compensación mínima considerada sospechosa cuando artefactos cruzan zonas horarias sin justificación lógica. |

### Glosario

- **Tiempo época**: Conteo entero universal de segundos transcurridos desde una fecha de referencia fija (1970-01-01 00:00:00 UTC), que evita ambigüedades de zona horaria y calendario.
- **Aritmética entera determinista**: Operaciones matemáticas sobre números enteros que siempre producen el mismo resultado exacto, sin aproximación. Fundamental para conclusiones forenses reproducibles.
- **Inconsistencia temporal**: Contradicción lógica en marcas temporales (p. ej., modificación que precede a la creación) que no puede ocurrir bajo comportamiento normal del sistema e indica manipulación del artefacto.
- **Artefacto**: Cualquier objeto digital que lleva evidencia potencial (archivos, correos, entradas de registro).
- **Extracción de marca temporal**: Proceso de leer un valor temporal crudo desde los metadatos de un artefacto sin interpretarlo ni alterarlo.

### 【Nota Científica】
La arquitectura de este módulo emplea conceptos semióticos—la teoría del signo de Peirce, los códigos culturales de Eco y las máximas conversacionales de Grice. Estos términos **no** son misticismo ni crítica literaria. Funcionan como un **modelo de sensor** formal: al igual que un sensor físico convierte un estímulo (luz, presión) en una señal eléctrica estructurada, este detector convierte trazas de marcas temporales crudas (signos peirceanos) en estados interpretables mediante reglas deterministas (códigos de Eco) y expectativas lógicas (máximas de Grice). Una inconsistencia temporal es simplemente una señal que viola el código esperado, activando una alerta. La terminología describe una capa de procesamiento de información, no un sistema de creencias esotérico.

---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## РУССКИЙ

### Что представляет собой этот модуль?
**Детектор временно́го дрейфа** (`vigia/tools/temporal_drift.py`) — детерминированный криминалистический движок, анализирующий последовательности временны́х меток, извлечённых из цифровых артефактов. Его назначение — выявлять фальсификацию доказательств путём идентификации логически невозможных хронологий: например, файл, изменённый до создания, или электронное письмо, отправленное в будущем. Модуль трактует время как дискретное, упорядоченное множество целочисленных значений. Все сравнения используют детерминированную целочисленную арифметику на целых секундах, обеспечивая точную воспроизводимость без дробного приближения.

### Ключевые концепции

**Основные классы**

| Класс | Роль | Описание |
|-------|------|----------|
| `TemporalEvent` | Контейнер данных | Представляет одно временно́е событие (напр., создание файла). Время хранится как целые секунды от эпохи. |
| `TemporalAnalysis` | Объект результата | Содержит итог проверки последовательности: согласованный, аномальный или невозможный. |
| `TemporalDriftDetector` | Движок | Оркестрирует сравнение событий с применением детерминированных целочисленных порогов. |
| `TimestampExtractor` | Утилита | Извлекает целочисленные временны́е метки из заголовков артефактов (PDF, почта и пр.). |

**Функции анализа**

| Функция | Вход | Выход | Назначение |
|---------|------|-------|------------|
| `analyze()` | Список `TemporalEvent` | `TemporalAnalysis` | Последовательно валидирует целочисленные временны́е метки против логического порядка. |
| `extract_from_pdf()` | Байты PDF-артефакта | Целочисленная временна́я метка | Считывает даты создания/изменения из метаданных PDF как целые секунды. |
| `extract_from_email()` | Строка заголовка почты | Целочисленная временна́я метка | Разбирает даты отправки/получения из заголовков в целочисленное время эпохи. |

**Детерминированные пороги (Константы)**

| Константа | Тип | Криминалистический смысл |
|-----------|-----|--------------------------|
| `MAX_CREATION_TO_SEND` | Целое (секунды) | Максимальная правдоподобная задержка между созданием файла и передачей. |
| `MAX_MODIFY_TO_SEND` | Целое (секунды) | Максимальная правдоподобная задержка между последним изменением и отправкой. |
| `MAX_FUTURE_TOLERANCE` | Целое (секунды) | Малый целочисленный допуск относительно системных часов для учёта безвредного дрейфа; значения сверх него указывают на фальсификацию. |
| `MIN_TIMEZONE_GAP_HOURS` | Целое (часы) | Минимальное различие смещения, считаемое подозрительным, когда артефакты пересекают часовые пояса без логического обоснования. |

### Глоссарий

- **Время эпохи**: Универсальный целочисленный счётчик секунд, прошедших с фиксированной даты отсчёта (1970-01-01 00:00:00 UTC), позволяющий избежать неоднозначностей часовых поясов и календарей.
- **Детерминированная целочисленная арифметика**: Математические операции над целыми числами, всегда дающие одинаковый точный результат без приближения. Критична для воспроизводимых криминалистических выводов.
- **Временна́я непоследовательность**: Логическое противоречие в временны́х метках (напр., изменение, предшествующее созданию), которое не может возникнуть при нормальном поведении системы и свидетельствует о манипуляции с артефактом.
- **Артефакт**: Любой цифровой объект, несущий потенциальные доказательства (файлы, письма, записи журнала).
- **Извлечение временно́й метки**: Процесс считывания необработанного временно́го значения из метаданных артефакта без его интерпретации или изменения.

### 【Научное примечание】
Архитектура этого модуля задействует семиотические концепции — теорию знака Пирса, культурные коды Эко и конверсациональные максимы Грайса. Эти термины **не** являются мистицизмом или литературной критикой. Они функционируют как формальная **модель датчика**: подобно тому как физический датчик преобразует стимул (свет, давление) в структурированный электрический сигнал, этот детектор преобразует необработанные следы временны́х меток (пирсовские знаки) в интерпретируемые состояния посредством детерминированных правил (коды Эко) и логических ожиданий (максимы Грайса). Временна́я непоследовательность — это просто сигнал, нарушающий ожидаемый код и вызывающий оповещение. Терминология описывает уровень обработки информации, а не эзотерическую систему убеждений.

---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## 中文

### 本模块是什么？
**时间漂移检测器**（`vigia/tools/temporal_drift.py`）是一个确定性取证引擎，检查从数字取证工件中提取的时间戳序列。其目的是通过识别逻辑上不可能的时间顺序来揭露证据篡改——例如，文件在创建之前被修改，或电子邮件被发送至未来时间。模块将时间视为整数值的离散有序集合。所有比较均使用基于整秒的确定性整数算术，确保精确可重现性，不涉及任何分数近似。

### 核心概念

**核心类**

| 类 | 作用 | 通俗描述 |
|----|------|----------|
| `TemporalEvent` | 数据容器 | 表示一个带时间戳的事件（如文件创建）。时间以纪元整数秒存储。 |
| `TemporalAnalysis` | 结果对象 | 保存序列检查结果：一致、异常或不可能。 |
| `TemporalDriftDetector` | 引擎 | 使用确定性整数阈值编排事件比较。 |
| `TimestampExtractor` | 工具 | 从取证工件头部（PDF、电子邮件等）获取原始整数时间戳。 |

**分析函数**

| 函数 | 输入 | 输出 | 用途 |
|------|------|------|------|
| `analyze()` | `TemporalEvent` 列表 | `TemporalAnalysis` | 按逻辑顺序顺序验证整数时间戳。 |
| `extract_from_pdf()` | PDF 取证工件字节 | 整数时间戳 | 以整数秒从 PDF 元数据读取创建/修改日期。 |
| `extract_from_email()` | 电子邮件头部字符串 | 整数时间戳 | 将头部发送/接收日期解析为整数纪元时间。 |

**确定性阈值（常量）**

| 常量 | 类型 | 取证含义 |
|------|------|----------|
| `MAX_CREATION_TO_SEND` | 整数（秒） | 文件创建到传输之间的最大合理延迟。 |
| `MAX_MODIFY_TO_SEND` | 整数（秒） | 最后修改到发送之间的最大合理延迟。 |
| `MAX_FUTURE_TOLERANCE` | 整数（秒） | 相对系统时钟允许的小整数缓冲，用于容纳良性偏斜；超过此值表明篡改。 |
| `MIN_TIMEZONE_GAP_HOURS` | 整数（小时） | 当取证工件跨越时区而无逻辑依据时，被视为可疑的最小偏移差值。 |

### 术语表

- **纪元时间**：自固定参考日期（1970-01-01 00:00:00 UTC）起经过秒数的通用整数计数，用于避免时区和日历解析歧义。
- **确定性整数算术**：对整数执行的数学运算，始终产生完全相同的结果，不涉及任何近似。对于可重现的取证结论至关重要。
- **时间不一致性**：时间戳中的逻辑矛盾（如修改先于创建），在正常系统行为下不可能发生，因此表明取证工件被篡改。
- **取证工件**：携带潜在证据的任何数字对象（文件、电子邮件、日志条目）。
- **时间戳提取**：从取证工件的元数据中读取原始时间值的过程，不对其进行解释或更改。

### 【科学说明】
本模块架构采用语义概念——皮尔斯的符号理论、艾柯的文化代码和格赖斯的会话准则。这些术语**不是**神秘主义或文学批评，而是作为正式的**传感器模型**发挥作用：就像物理传感器将刺激（光、压力）转换为结构化电信号一样，该检测器通过确定性规则（艾柯的代码）和逻辑期望（格赖斯的准则）将原始时间戳痕迹（皮尔斯的符号）转换为可解释的状态。时间不一致性就是一个违反预期代码的信号，触发警报。这些术语描述的是信息处理层，而非神秘信仰体系。

---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
