<!--
VIGIA Academic Documentation
Module: 5a035ab4
Batch ID: vigia-doc-0143-5a035ab4
Generated: 2026-05-20T14:56:47.875267+00:00
-->

---

# ENGLISH

## What Is This Module?
This module is the chronological assembly line of the VIGIA forensic system. It collects observations from five distinct evidence domains—Network traffic, Disk storage, Memory (RAM), System Registry, and Log files—and merges them into one continuous, contradiction-free timeline. Think of it as a laboratory instrument that synchronizes clocks from five separate experiments so that causality can be determined with certainty. Every numeric value inside the evidence dictionary is stored as an exact rational number (integer numerator/denominator or its string representation); approximate decimal arithmetic is never used.

## Key Concepts

| Name | Role | Scientific Meaning |
|---|---|---|
| `TOOL_NAME` | Identifier | Name tag for the engine in audit reports. |
| `ARTIFACT_RELIABILITY` | Weight matrix | Confidence score assigned to each source type; a higher weight indicates a more trustworthy sensor. |
| `TEMPORAL_CORRELATION_WINDOW` | Tolerance threshold | Maximum allowable time gap between events before they are flagged as mismatched; expressed as an exact integer rational value. |

| Class | Purpose | Deterministic Guarantee |
|---|---|---|
| `TimelineEvent` | Atomic unit of time | Timestamp stored as a rational integer pair (`Fraction` / `str`); no rounding occurs. |
| `TimelineAnalysisResult` | Anomaly container | All temporal deltas are computed via exact integer-based arithmetic. |
| `UnifiedTimelineEngine` | Integration controller | Builds the unified timeline using deterministic integer arithmetic exclusively. |

| Function | Input | Output | Role |
|---|---|---|---|
| `to_signal()` | Raw forensic artifact | Normalized `TimelineEvent` | Translates heterogeneous source data into a common temporal language. |
| `build_timeline()` | Set of `TimelineEvent` objects | `TimelineAnalysisResult` | Correlates cross-source events and flags temporal paradoxes. |

## Glossary
- **Artifact**: Any digital object carrying evidentiary value (e.g., a file, network packet, or registry key).
- **Cross-source inconsistency**: A temporal paradox where two reliable sources disagree on when an action occurred.
- **Deterministic integer arithmetic**: Exact calculation using whole numbers and rational fractions (e.g., 1/2 represented as numerator/denominator), never approximate decimals.
- **Temporal correlation window**: The maximum acceptable clock skew between two events before the system registers a contradiction.
- **Signal**: A normalized observation that is ready for insertion into the timeline.

## 【Scientific Note】Peirce, Eco, and Grice in Digital Forensics
The terminology of semiotics—Charles Sanders Peirce’s sign-object-interpretant triad, Umberto Eco’s coding theory, and H. Paul Grice’s conversational maxims—is sometimes mistaken for philosophical mysticism. It is not. In this framework, forensic artifacts function as **semiotic sensors**.

- **Peirce’s triad**: A forensic artifact (sign) points to a past system state (object); the investigator’s inference (interpretant) reconstructs that state. This is identical to a thermometer reading (sign) representing temperature (object) interpreted by a scientist (interpretant).
- **Eco’s codes**: The encoding rules that govern how a log file formats time are no different from the calibration protocol of a spectrometer. They are deterministic conventions, not esoteric signs.
- **Grice’s maxims**: The assumption that a log timestamp is truthful and relevant is the same as assuming a voltmeter is properly grounded. Violations (temporal inconsistencies) are **sensor malfunctions or calibration drift**, not mystical paradoxes.

Treating these concepts as signal-processing parameters allows the engine to detect logical fractures in evidence through rigorous, deterministic arithmetic.

---

# ESPAÑOL

## ¿Qué es este módulo?
Es la línea de montaje cronológica del sistema forense VIGIA. Recoge observaciones de cinco dominios de evidencia distintos—tráfico de Red, almacenamiento en Disco, Memoria RAM, Registro del sistema y archivos de Logs—y los fusiona en una única línea temporal continua y libre de contradicciones. Considérelo como un instrumento de laboratorio que sincroniza relojes de cinco experimentos separados para que la causalidad pueda determinarse con certeza. Todo valor numérico en el diccionario de evidencia se almacena como un número racional exacto (numerador/denominador enteros o su representación textual); nunca se utiliza aritmética decimal aproximada.

## Conceptos Clave

| Nombre | Función | Significado Científico |
|---|---|---|
| `TOOL_NAME` | Identificador | Etiqueta del motor en informes de auditoría. |
| `ARTIFACT_RELIABILITY` | Matriz de pesos | Puntaje de confianza por tipo de fuente; mayor peso = sensor más fiable. |
| `TEMPORAL_CORRELATION_WINDOW` | Umbral de tolerancia | Brecha temporal máxima permitida antes de considerar dos eventos como incompatibles; expresado como racional entero exacto. |

| Clase | Propósito | Garantía Determinista |
|---|---|---|
| `TimelineEvent` | Unidad atómica de tiempo | Marca temporal almacenada como par de enteros (`Fraction` / `str`); sin redondeo. |
| `TimelineAnalysisResult` | Contenedor de anomalías | Todas las diferencias computadas mediante aritmética exacta. |
| `UnifiedTimelineEngine` | Controlador de integración | Construye la línea temporal usando únicamente aritmética entera determinista. |

| Función | Entrada | Salida | Rol |
|---|---|---|---|
| `to_signal()` | Artefacto forense en bruto | `TimelineEvent` normalizado | Traduce datos heterogéneos a un lenguaje temporal común. |
| `build_timeline()` | Conjunto de objetos `TimelineEvent` | `TimelineAnalysisResult` | Correlaciona eventos cross-source y señala paradojas temporales. |

## Glosario
- **Artefacto**: Cualquier objeto digital con valor probatorio (archivo, paquete, clave de registro, etc.).
- **Inconsistencia cross-source**: Paradoja temporal donde dos sensores fiables discrepan sobre cuándo ocurrió una acción.
- **Aritmética entera determinista**: Cálculo exacto con números enteros y fracciones racionales (p. ej., 1/2 como numerador/denominador), nunca decimales aproximados.
- **Ventana de correlación temporal**: Máxima desviación de reloj aceptable entre dos eventos antes de que el sistema marque una contradicción.
- **Señal**: En este contexto, una observación normalizada lista para inserción en la línea temporal.

## 【Nota Científica】Peirce, Eco y Grice en Informática Forense
La terminología de la semiótica—el triada signo-objeto-interpretante de Charles Sanders Peirce, la teoría de los códigos de Umberto Eco y las máximas conversacionales de H. Paul Grice—a veces se confunde con misticismo filosófico. No lo es. En este marco, los artefactos forenses funcionan como **sensores semióticos**.

- **Tríada de Peirce**: Un artefacto forense (signo) apunta a un estado pasado del sistema (objeto); la inferencia del investigador (interpretante) reconstruye ese estado. Es idéntico a la lectura de un termómetro (signo) que representa temperatura (objeto) e interpretada por un científico (interpretante).
- **Códigos de Eco**: Las reglas de codificación que gobiernan cómo un archivo de log formatea el tiempo no difieren del protocolo de calibración de un espectrómetro. Son convenciones deterministas, no signos esotéricos.
- **Máximas de Grice**: La suposición de que una marca temporal es veraz y relevante equivale a asumir que un voltímetro está correctamente conectado a tierra. Las violaciones (inconsistencias temporales) son **fallos de sensor o deriva de calibración**, no paradojas místicas.

Tratar estos conceptos como parámetros de procesamiento de señales permite al motor detectar fracturas lógicas en la evidencia mediante aritmética rigurosa y determinista.

---

# РУССКИЙ

## Что представляет собой этот модуль?
Это хронологическая сборочная линия судебно-экспертной системы VIGIA. Модуль собирает наблюдения из пяти различных областей доказательств — сетевого трафика (Red), дисковых накопителей (Disco), оперативной памяти (Memoria), системного реестра (Registro) и журналов (Logs) — и объединяет их в единую непрерывную временну́ю шкалу, свободную от противоречий. Воспринимайте его как лабораторный прибор, синхронизирующий часы пяти отдельных экспериментов, чтобы причинно-следственные связи можно было установить с достоверностью. Каждое числовое значение в словаре доказательств хранится в виде точного рационального числа (числитель/знаменатель целые или их строковое представление); приближённая десятичная арифметика никогда не применяется.

## Ключевые концепции

| Имя | Роль | Научное значение |
|---|---|---|
| `TOOL_NAME` | Идентификатор | Имя механизма в аудиторских отчётах. |
| `ARTIFACT_RELIABILITY` | Весовая матрица | Оценка достоверности по типу источника; больший вес = более надёжный датчик. |
| `TEMPORAL_CORRELATION_WINDOW` | Порог допуска | Максимально допустимый временной разрыв между событиями, прежде чем они будут признаны несовпадающими; выражен точным целым рациональным числом. |

| Класс | Назначение | Детерминистская гарантия |
|---|---|---|
| `TimelineEvent` | Атомарная единица времени | Отметка времени хранится как пара целых чисел (`Fraction` / `str`); округление отсутствует. |
| `TimelineAnalysisResult` | Контейнер аномалий | Все дельты вычисляются точной целочисленной арифметикой. |
| `UnifiedTimelineEngine` | Контроллер интеграции | Построение шкалы только с помощью детерминистской целочисленной арифметики. |

| Функция | Вход | Выход | Роль |
|---|---|---|---|
| `to_signal()` | Сырые судебные артефакты | Нормализованный `TimelineEvent` | Преобразует гетерогенные данные в общий временной язык. |
| `build_timeline()` | Набор объектов `TimelineEvent` | `TimelineAnalysisResult` | Коррелирует события из разных источников и маркирует временные парадоксы. |

## Глоссарий
- **Артефакт**: Любой цифровой объект, обладающий доказательственной ценностью (файл, пакет, ключ реестра и т.
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

## 中文

### 这是什么模块？

本模块是 VIGÍA 取证系统的**时间轴组装流水线**。它从五个独立证据领域——网络（Red）流量、磁盘（Disco）存储、内存（Memoria）、系统注册表（Registro）和日志（Logs）文件——收集观察数据，并将其合并为一条连续且无矛盾的统一时间轴。可将其理解为一台实验室仪器：它同步五个独立实验的时钟，以确定性方式确立因果关系。

证据字典中的每个数值均以精确有理数（整数分子/分母或其字符串表示）存储，永不使用近似十进制算术。这一设计保证了时间比较和异常检测的绝对可重现性：对于相同输入，无论在何种硬件平台上运行，模块均产生逐位一致的输出。

皮尔斯（Peirce）的符号三元组、艾柯（Eco）的代码理论和格赖斯（Grice）的会话准则在此框架中被用作形式化信号处理参数。取证工件充当符号传感器：时间戳是符号（sign），过去的系统状态是对象（object），调查员的推断是解释项（interpretant）。时间不一致性即为传感器故障或校准漂移——逻辑断裂——而非神秘现象。

### 关键概念

| 概念 | 定义 | 技术作用 |
|---|---|---|
| **`TimelineEvent`** | 时间轴的原子单位 | 时间戳以有理整数对（`Fraction`/`str`）存储，不发生舍入 |
| **`TimelineAnalysisResult`** | 异常容器 | 所有时间差值通过精确整数运算计算得出 |
| **`UnifiedTimelineEngine`** | 集成控制器 | 完全使用确定性整数运算构建统一时间轴 |
| **`ARTIFACT_RELIABILITY`** | 权重矩阵 | 为每种证据源类型分配的置信度分数；权重越高表示传感器越可信 |
| **`TEMPORAL_CORRELATION_WINDOW`** | 容差阈值 | 事件间允许的最大时间间隙，超过此值则标记为不匹配；以精确整数有理数表示 |
| **`to_signal()`** | 转换器函数 | 将异构来源数据转换为统一时间语言的规范化 `TimelineEvent` |
| **`build_timeline()`** | 主分析函数 | 关联跨源事件并标记时间逻辑断裂 |

> **【科学说明】**
> 皮尔斯（Peirce）、艾柯（Eco）和格赖斯（Grice）的术语并非神秘主义，而是形式化的分析机制。如同光谱仪将光子相互作用转换为离散整数计数，本模块将证据信号转换为确定性整数分数。精确整数运算确保法庭可重现性，不依赖浮点近似。取证工件链的逻辑断裂以整数标志事件的形式被检测，而非直觉判断。艾柯的代码是日志文件格式化时间的编码规则，与光谱仪的校准协议并无本质差异：两者均是确定性约定，而非神秘符号。

### 词汇表

1. **取证工件** — 承载证据价值的任何数字对象（文件、网络数据包、注册表键等）。
2. **跨源不一致性** — 两个可靠证据源对某动作发生时间存在分歧的时间悖论；即逻辑断裂。
3. **确定性整数运算** — 使用整数和精确有理分数进行的计算（如以分子/分母表示 1/2），永不使用近似小数。
4. **时间相关窗口** — 两个事件之间可接受的最大时钟偏差，超过此值系统注册矛盾。
5. **信号（Signal）** — 已规范化、可插入时间轴的观察数据。
6. **分数运算（Fraction arithmetic）** — 使用 Python `Fraction` 类型或字符串表示进行的精确有理数运算，确保时间比较不丢失精度。
7. **法证可重现性** — 对于相同输入，在任意硬件平台上产生相同时间轴结果的属性。
8. **SHA-256 哈希链** — 将每次分析事件密码学绑定至先前事件的不可篡改日志链。
9. **初性（Firstness）** — 皮尔斯三元组中纯现象描述阶段：不加解释地描述原始时间戳。
10. **二性（Secondness）** — 皮尔斯三元组中结构对比阶段：时间戳相对于基线的偏差分析。
11. **三性（Thirdness）** — 皮尔斯三元组中规律推断阶段：从时间异常推断攻击者行为模式。

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
