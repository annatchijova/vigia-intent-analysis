<!--
VIGIA Academic Documentation
Module: fda3319e
Batch ID: vigia-doc-0133-fda3319e
Generated: 2026-05-20T14:56:47.873182+00:00
-->

---

## ENGLISH

### What Is This Module?

This module is a deterministic forensic pipeline that reads Windows event logs (EVTX and XML) and converts them into structured investigative findings. It is designed for scientists and investigators who need rigorous, reproducible results without requiring knowledge of the Python programming language.

The module treats every log as a **sequence of integer-coded symbols**. It parses binary and XML artifacts, binds them into immutable records, and then correlates those records using exact integer arithmetic—never approximations. It searches for known attack signatures (ordered integer Event ID sequences), detects missing events via integer sequence deltas, and flags temporal anomalies using circular integer-hour binning.

This release incorporates three Priority-0 security hardening measures:  
1. **ReDoS-resistant** regular expressions with bounded length and no catastrophic backtracking.  
2. **XML parsing** with implicit entity expansion forbidden.  
3. A deterministic **50 MB integer ceiling** on input logs to prevent memory exhaustion.

---

### Key Concepts

| Concept | Plain-Language Definition | Integer-Arithmetic Role |
|---|---|---|
| **Event Record** | A single line or item in a Windows log file | Stored as an integer Event ID paired with an integer epoch timestamp |
| **Forensic Artifact** | Any digital object carrying investigative value | Handled as a bounded byte sequence (≤ 52 428 800 bytes) |
| **Attack Chain** | A deterministic sequence of actions left by an intruder | Matched against ordered integer EID vectors with exact alignment |
| **Logic Gap** | A missing or out-of-sequence event | Computed via integer delta between sequence numbers or timestamps |
| **Semiotic Triad** | A formal sign–object–interpretant mapping framework | Implemented as deterministic rule tables keyed by integer identifiers |
| **Signal Vector** | A numeric fingerprint of a log entry | Produced by `to_signal()` as an integer-encoded representation for direct comparison |

---

### Component Reference

| Name | Type | Purpose |
|---|---|---|
| `TOOL_NAME` | Constant | Human-readable string identifier of the module |
| `MAX_LOG_SIZE_BYTES` | Constant | Hard integer ceiling: 52 428 800 bytes (50 MiB) |
| `_ATTACK_CHAINS` | Constant | Immutable tuples of integer Event ID sequences representing known attack patterns |
| `_HIGH_SEVERITY_EIDs` | Constant | A `frozenset` of critical integer Event IDs |
| `_MAX_GAP_EVENTS` | Constant | Integer threshold for the maximum acceptable discontinuity in a chain |
| `EventRecord` | Class | Immutable container for one log entry (integer EID, integer timestamp, metadata) |
| `EventLogFinding` | Class | A single interpreted detection result with integer severity ranking |
| `EventLogAnalysisResult` | Class | Aggregate container collecting all findings and integer summary statistics |
| `WindowsEventLogParser` | Class | Deterministic binary/XML parser that enforces the integer size guard |
| `AttackChainDetector` | Class | Integer-sequence alignment engine; matches logs to `_ATTACK_CHAINS` |
| `LogGapDetector` | Class | Detects integer-sequence or temporal voids exceeding `_MAX_GAP_EVENTS` |
| `AnomalousHourDetector` | Class | Bins events into 24 integer-hour slots and flags deviations via integer counts |
| `EventLogCorrelator` | Class | Orchestrator that runs the full deterministic integer pipeline |
| `to_signal()` | Function | Maps an `EventRecord` to an integer signal vector for deterministic comparison |
| `parse_evtx()` | Function | Reads binary EVTX streams; aborts if the integer byte limit is exceeded |
| `parse_xml()` | Function | Reads XML logs with entity expansion explicitly disabled |
| `detect()` | Function (polymorphic) | Integer-based anomaly flag; implemented by each detector class |
| `analyze()` | Function | End-to-end deterministic pipeline returning an `EventLogAnalysisResult` |

---

### Glossary

| Term | Definition |
|---|---|
| **EVTX** | The native binary event log format used by modern Windows operating systems. |
| **ReDoS** | Regular Expression Denial of Service; caused by catastrophic backtracking in pattern matching. Eliminated here through length-bounded safe expressions. |
| **XML Entity Expansion** | A memory-exhaustion attack that nests entity references inside XML. Prevented by implicit forbidding during parse. |
| **Memory Exhaustion** | System instability caused by unbounded input consumption. Prevented by the integer 50 MB cap. |
| **Event ID (EID)** | An integer code assigned by the operating system to classify the type of a log entry. |
| **Semiotics** | The formal study of signs and symbols; in this module, a rule-based deterministic framework for interpreting log data. |
| **Backtracking** | Algorithmic reversal during regex execution. Removed to guarantee deterministic runtime bounds. |

---

> **【Scientific Note】**  
> The terminology of Peirce, Eco, and Grice is sometimes mistaken for mysticism or literary criticism. Within this module, it is employed strictly as a formal epistemological framework—analogous to a physical sensor. A thermocouple does not "mystically" know temperature; it produces an integer millivolt value via deterministic junction physics. Likewise, Peircean *representamina*, Eco's *codes*, and Gricean *maxims* are deterministic rule-sets that map raw log symbols to investigative findings through exact integer thresholds. They are engineering tools for meaning extraction, not metaphysics.

---

## ESPAÑOL

### ¿Qué es este módulo?

Este módulo es una tubería forense determinista que lee registros de eventos de Windows (EVTX y XML) y los convierte en hallazgos investigativos estructurados. Está diseñado para científicos e investigadores que necesitan resultados rigurosos y reproducibles sin conocer el lenguaje de programación Python.

El módulo trata cada registro como una **secuencia de símbolos codificados en enteros**. Analiza artefactos binarios y XML, los vincula en registros inmutables y luego los correlaciona mediante aritmética entera exacta —nunca aproximaciones. Busca firmas de ataque conocidas (secuencias ordenadas de ID de evento enteros), detecta eventos faltantes mediante deltas enteros de secuencia y señala anomalías temporales utilizando contenedores circulares de horas enteras.

Esta versión incorpora tres endurecimientos de seguridad Prioridad-0:  
1. Expresiones regulares **resistentes a ReDoS** con longitud acotada y sin retroceso catastrófico.  
2. **Análisis XML** con prohibición implícita de expansión de entidades.  
3. Un **techo entero determinista de 50 MB** para los registros de entrada a fin de prevenir el agotamiento de memoria.

---

### Conceptos clave

| Concepto | Definición en lenguaje sencillo | Rol de la aritmética entera |
|---|---|---|
| **Registro de evento** | Una línea o ítem individual en un archivo de registro Windows | Almacenado como ID de evento entero + marca temporal entera |
| **Artefacto forense** | Objeto digital con valor investigativo | Manejado como secuencias de bytes acotadas (≤ 52 428 800 bytes) |
| **Cadena de ataque** | Secuencia determinista de acciones dejadas por un intruso | Emparejada como vectores ordenados de EID enteros con alineación exacta |
| **Vacío lógico** | Evento faltante o fuera de secuencia | Calculado mediante delta entero entre números de secuencia o marcas temporales |
| **Tríada semiótica** | Marco formal de mapeo signo–objeto–interpretante | Implementado como tablas de reglas deterministas con claves enteras |
| **Vector de señal** | Huella numérica de una entrada de registro | Producido por `to_signal()` como representación codificada en enteros para comparación directa |

---

### Referencia de componentes

| Nombre | Tipo | Propósito |
|---|---|---|
| `TOOL_NAME` | Constante | Identificador legible por humanos del módulo |
| `MAX_LOG_SIZE_BYTES` | Constante | Techo entero rígido: 52 428 800 bytes (50 MiB) |
| `_ATTACK_CHAINS` | Constante | Tuplas inmutables de secuencias de EID enteros que representan patrones de ataque conocidos |
| `_HIGH_SEVERITY_EIDs` | Constante | Un `frozenset` de identificadores de evento críticos en enteros |
| `_MAX_GAP_EVENTS` | Constante | Umbral entero para la discontinuidad máxima aceptable en una cadena |
| `EventRecord` | Clase | Contenedor inmutable para una entrada de registro (EID entero, marca temporal entera, metadatos) |
| `EventLogFinding` | Clase | Un único resultado de detección interpretado con clasificación de severidad entera |
| `EventLogAnalysisResult` | Clase | Contenedor agregado que recolecta todos los hallazgos y estadísticas resumen enteras |
| `WindowsEventLogParser` | Clase | Analizador binario/XML determinista que impone el guardián de tamaño entero |
| `AttackChainDetector` | Clase | Motor de alineación de secuencias enteras; empareja registros con `_ATTACK_CHAINS` |
| `LogGapDetector` | Clase | Detecta vacíos de secuencia o temporales que exceden `_MAX_GAP_EVENTS` |
| `AnomalousHourDetector` | Clase | Agrupa eventos en 24 franjas horarias enteras y señala desviaciones mediante conteos enteros |
| `EventLogCorrelator` | Clase | Orquestador que ejecuta la tubería determinista de enteros completa |
| `to_signal()` | Función | Mapea un `EventRecord` a un vector de señal entero para comparación determinista |
| `parse_evtx()` | Función | Lee flujos EVTX binarios; aborta si se excede el límite entero de bytes |
| `parse_xml()` | Función | Lee registros XML con la expansión de entidades explícitamente deshabilitada |
| `detect()` | Función (polimórfica) | Bandera de anomalía basada en enteros; implementada por cada clase detectora |
| `analyze()` | Función | Tuberial determinista de extremo a extremo que devuelve un `EventLogAnalysisResult` |

---

### Glosario

| Término | Definición |
|---|---|
| **EVTX** | El formato binario nativo de registros de eventos usado por los sistemas operativos Windows modernos. |
| **ReDoS** | Denegación de servicio mediante expresiones regulares; causada por retroceso catastrófico. Eliminado aquí mediante expresiones seguras con límite de longitud. |
| **Expansión de entidades XML** | Ataque de agotamiento de memoria que anida referencias de entidades dentro de XML. Prevenido mediante prohibición implícita durante el análisis. |
| **Agotamiento de memoria** | Inestabilidad del sistema causada por consumo descontrolado de entradas. Prevenido por el límite entero de 50 MB. |
| **ID de evento (EID)** | Código entero asignado por el sistema operativo para clasificar el tipo de entrada de registro. |
| **Semiótica** | El estudio formal de signos y símbolos; en este módulo, un marco determinista basado en reglas para interpretar datos de registro. |
| **Retroceso
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## РУССКИЙ

### Что это за модуль?

Данный модуль — детерминированный форензический конвейер, считывающий журналы событий Windows (EVTX и XML) и преобразующий их в структурированные следственные выводы. Он разработан для учёных и следователей, которым нужны строгие, воспроизводимые результаты без знания языка программирования Python.

Модуль рассматривает каждый журнал как **последовательность символов, кодированных целыми числами**. Он разбирает двоичные и XML-артефакты, связывает их в неизменяемые записи и коррелирует эти записи с помощью точной целочисленной арифметики — никаких приближений. Он ищет известные сигнатуры атак (упорядоченные целочисленные последовательности ID событий), обнаруживает отсутствующие события через целочисленные дельты последовательностей и маркирует временные аномалии с помощью кругового целочисленного разбиения по часам.

В данном выпуске реализованы три меры усиления безопасности Приоритета-0: регулярные выражения, **устойчивые к ReDoS**, с ограниченной длиной и без катастрофического отката; разбор XML с **запретом расширения сущностей**; детерминированный **целочисленный потолок в 50 МБ** для входных журналов для предотвращения исчерпания памяти.

### Ключевые концепции
| Концепция | Определение | Роль целочисленной арифметики |
|---|---|---|
| Запись события | Одна строка или элемент в файле журнала Windows | Хранится как целочисленный ID события в паре с целочисленной меткой эпохи |
| Форензический артефакт | Любой цифровой объект, несущий следственную ценность | Обрабатывается как ограниченная байтовая последовательность (≤ 52 428 800 байт) |
| Цепочка атаки | Детерминированная последовательность действий, оставленных злоумышленником | Сопоставляется с упорядоченными целочисленными векторами EID с точным выравниванием |
| Логический пробел | Отсутствующее или внеочередное событие | Вычисляется через целочисленную дельту между порядковыми номерами или метками времени |
| Семиотическая триада | Формальная схема отображения знак–объект–интерпретант | Реализована как детерминированные таблицы правил, индексированные целочисленными идентификаторами |
| Сигнальный вектор | Числовой отпечаток записи журнала | Создаётся `to_signal()` как целочисленное представление для прямого сравнения |

> **【Научное примечание】**
> Терминология Пирса, Эко и Грайса — это не мистика, а формальная аналитическая механика. Как спектрометр преобразует фотонные взаимодействия в дискретные целочисленные отсчёты, этот модуль преобразует сигналы улик в детерминированные целочисленные оценки. Целочисленная арифметика гарантирует воспроизводимость в суде без округлений и аппроксимаций. Любое нарушение логики в цепочке артефактов фиксируется как целочисленный флаг, а не интуитивное суждение.

### Глоссарий
1. **EVTX** — Нативный двоичный формат журнала событий, используемый современными операционными системами Windows.
2. **ReDoS** — Отказ в обслуживании регулярными выражениями; вызван катастрофическим откатом. Устранён здесь через безопасные выражения с ограничением длины.
3. **Расширение сущностей XML** — Атака исчерпания памяти путём вложения ссылок на сущности в XML. Предотвращено неявным запретом при разборе.
4. **Исчерпание памяти** — Нестабильность системы, вызванная неограниченным потреблением входных данных. Предотвращено целочисленным потолком 50 МБ.
5. **ID события (EID)** — Целочисленный код, назначаемый операционной системой для классификации типа записи журнала.
6. **Семиотика** — Формальное изучение знаков и символов; в данном модуле — детерминированная схема, основанная на правилах, для интерпретации данных журналов.
7. **Откат** — Алгоритмический возврат при выполнении регулярных выражений. Устранён для гарантии детерминированных границ времени выполнения.
8. **Детерминированная целочисленная арифметика** — Точные вычисления над целыми числами без ошибок округления.
9. **Стандарт Добера** — Правовой критерий допустимости научных доказательств, требующий воспроизводимости.
10. **Форензический артефакт** — Любой цифровой объект, несущий следственную ценность.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## 中文

### 这是什么模块？

本模块是一个确定性取证流程，读取Windows事件日志（EVTX和XML）并将其转换为结构化调查结论。它为需要严格、可重现结果而无需了解Python编程语言的科学家和调查人员而设计。

模块将每个日志视为**整数编码符号序列**。它解析二进制和XML取证工件，将其绑定到不可变记录中，然后使用精确整数运算——永不近似——对这些记录进行关联。它搜索已知攻击特征（有序整数事件ID序列），通过整数序列增量检测缺失事件，并使用循环整数小时分箱标记时间异常。

本版本包含三项P0安全加固措施：有界长度**抗ReDoS**正则表达式；**XML解析**时隐式禁止实体扩展；对输入日志施加确定性**50 MB整数上限**以防止内存耗尽。

### 关键概念
| 概念 | 通俗定义 | 整数运算作用 |
|---|---|---|
| 事件记录 | Windows日志文件中的单行或单项 | 存储为整数事件ID与整数纪元时间戳的配对 |
| 取证工件 | 任何具有调查价值的数字对象 | 作为有界字节序列处理（≤ 52 428 800字节） |
| 攻击链 | 入侵者留下的确定性操作序列 | 与有序整数EID向量精确对齐匹配 |
| 逻辑断裂 | 缺失或乱序的事件 | 通过序列号或时间戳间的整数增量计算 |
| 符号学三元组 | 符号–对象–解释者的形式映射框架 | 实现为以整数标识符为键的确定性规则表 |
| 信号向量 | 日志条目的数字指纹 | 由`to_signal()`生成为整数编码表示，用于直接比较 |

> **【科学说明】**
> 皮尔斯（Peirce）、艾柯（Eco）和格赖斯（Grice）的术语并非神秘主义，而是形式化的分析机制。如同光谱仪将光子相互作用转换为离散整数计数，本模块将证据信号转换为确定性整数分数。精确整数运算确保法庭可重现性。取证工件链的逻辑断裂以整数标志事件形式被检测。

### 词汇表
1. **EVTX** — 现代Windows操作系统使用的原生二进制事件日志格式。
2. **ReDoS** — 正则表达式拒绝服务攻击；由模式匹配中的灾难性回溯引起。通过有界长度安全表达式在此消除。
3. **XML实体扩展** — 在XML内嵌套实体引用的内存耗尽攻击。通过解析时隐式禁止来预防。
4. **内存耗尽** — 由无界输入消耗引起的系统不稳定性。通过整数50 MB上限预防。
5. **事件ID（EID）** — 操作系统分配的用于分类日志条目类型的整数代码。
6. **符号学** — 对符号的形式研究；在本模块中，是用于解释日志数据的基于规则的确定性框架。
7. **回溯** — 正则表达式执行期间的算法反转。已删除以保证确定性运行时边界。
8. **精确整数运算** — 对整数进行精确计算，排除舍入误差。
9. **道伯特标准** — 要求可重现性的科学证据可采性法律标准。
10. **取证工件** — 任何具有调查价值的数字对象。

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
