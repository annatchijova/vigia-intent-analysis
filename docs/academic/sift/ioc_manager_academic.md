<!--
VIGIA Academic Documentation
Module: c0b86e2d
Batch ID: vigia-doc-0134-c0b86e2d
Generated: 2026-05-20T14:56:47.873415+00:00
-->

# Module Documentation: `vigia/sift/ioc_manager.py`

## ENGLISH

### What Is This Module?

This module, `vigia/sift/ioc_manager.py`, is the **Indicators of Compromise (IOC) Engine**. It operates like a high-precision reference library for digital investigations. When forensic scientists extract artifacts—such as file fingerprints (hashes), suspicious file names, Windows registry keys, network addresses (IPs or domains), or known attacker techniques—from a computer system, this engine compares each extracted item against a structured database of previously confirmed threat signatures. If an exact match is found, the engine records a structured result linking the evidence to a specific threat actor or malware family. The entire process is deterministic: identical inputs always yield identical outputs because the engine relies on exact symbolic and integer-based logic, never on probabilistic guessing or inexact decimal approximations.

**Key Concepts**

| Concept | Description | Role in Forensic Workflow |
|---|---|---|
| `IOCRecord` | A single known threat signature stored as a structured reference entry. | Ground-truth pattern for exact comparison. |
| `IOCMatchResult` | The documented correspondence between a recovered artifact and an `IOCRecord`. | Verified output datum confirming a threat link. |
| `IOCManager` | The core controller that hosts the database and executes the matching protocol. | Deterministic engine managing all correlations. |
| `match_against_findings` | The batch procedure that cross-checks a list of forensic discoveries against the database. | Bulk correlation using exact equality rules. |
| `enrich_signal` | The procedure that appends IOC-derived context to an alert message (`SignalOutput`). | Annotation step adding threat intelligence metadata. |
| `to_signal` | The converter that formats a raw match into a standardized alert signal. | Normalization function for downstream reporting. |
| `Fraction` / `str` Storage | Numeric evidence is encoded as exact integer ratios (e.g., 1/4) or literal text strings. | Eliminates rounding errors; ensures reproducibility. |
| `TOOL_NAME` | A constant label identifying the software component that performed the analysis. | Provenance metadata. |
| `ARTIFACT_RELIABILITY` | A constant defining the trust tier assigned to artifacts processed by this module. | Evidence quality grading parameter. |

**Supported IOC Types**

| Type | Description | Example |
|---|---|---|
| Hash | Cryptographic checksum of file contents | `e3b0c44298fc1c149afbf4c8996fb924...` |
| Filename | Name or path of a file of interest | `ransomware.exe` |
| Registry Key | Windows configuration entry indicating persistence | `HKCU\Software\Microsoft\Windows\CurrentVersion\Run` |
| IP Address | Host address linked to malicious infrastructure | `198.51.100.33` |
| Domain | Internet domain used for command-and-control | `phishing.example.net` |
| MITRE Technique | Standardized identifier for adversary behavior | `T1055` (Process Injection) |

**Glossary**

- **Indicator of Compromise (IOC)**: A forensic artifact suggesting that a system has been breached or exposed to malware.
- **Forensic Artifact / Finding**: Any object or trace recovered from a digital medium during an investigation.
- **Deterministic System**: A system in which every state and output is uniquely determined by prior states and inputs, with no randomness.
- **Exact Rational Number (Fraction)**: A number expressed as a ratio of two integers (numerator and denominator), preserving infinite precision without rounding.
- **Signal Enrichment**: The addition of contextual information to an alert to clarify its significance.
- **Hash Function**: A deterministic algorithm that maps data of arbitrary size to a fixed-size bit string.
- **MITRE ATT&CK Technique**: A globally accessible knowledge base of adversary tactics and techniques based on real-world observations.

**Scientific Note**

> 【Scientific Note】
> In interdisciplinary literature, the semiotic frameworks of **Charles Sanders Peirce** (abductive inference), **Umberto Eco** (sign theory), and **H. Paul Grice** (implicature and cooperative communication) are occasionally dismissed as metaphysical. In forensic engineering, they are rigorous analytical tools. Consider an IOC match: it is not a mystical portent but a **sensor measurement**. Just as a thermocouple produces a voltage that deterministically maps to temperature through physical law, an `IOCRecord` maps a recovered artifact to a threat class through exact logical rules. The "sign" is simply a structured correlation between a physical state and a symbolic representation. This module operationalizes that principle by enforcing **deterministic integer arithmetic** and exact symbolic matching. There is no ambiguity, no rounding, and no interpretive divination—only reproducible, mechanistic inference.


## ESPAÑOL

### ¿Qué es este módulo?

Este módulo, `vigia/sift/ioc_manager.py`, es el **Motor de Indicadores de Compromiso (IOC)**. Funciona como una biblioteca de referencia de alta precisión para investigaciones digitales. Cuando los científicos forenses extraen artefactos—como huellas dactilares de archivos (hashes), nombres de archivo sospechosos, claves del registro de Windows, direcciones de red (IPs o dominios) o técnicas conocidas de atacantes—de un sistema informático, este motor compara cada elemento extraído contra una base de datos estructurada de firmas de amenazas confirmadas previamente. Si se encuentra una coincidencia exacta, el motor registra un resultado estructurado que vincula la evidencia con un actor de amenazas o familia de malware específicos. Todo el proceso es determinista: entradas idénticas siempre producen salidas idénticas porque el motor se basa en lógica simbólica y enteros exactos, nunca en suposiciones probabilísticas o aproximaciones decimales inexactas.

**Conceptos clave**

| Concepto | Descripción | Rol en el flujo de trabajo forense |
|---|---|---|
| `IOCRecord` | Una firma de amenaza conocida almacenada como entrada de referencia estructurada. | Patrón de verdad de referencia para comparación exacta. |
| `IOCMatchResult` | La correspondencia documentada entre un artefacto recuperado y un `IOCRecord`. | Dato de salida verificado que confirma un vínculo de amenaza. |
| `IOCManager` | El controlador central que aloja la base de datos y ejecuta el protocolo de coincidencia. | Motor determinista que gestiona todas las correlaciones. |
| `match_against_findings` | El procedimiento por lotes que contrasta una lista de hallazgos forenses contra la base de datos. | Correlación masiva mediante reglas de igualdad exacta. |
| `enrich_signal` | El procedimiento que añade contexto derivado de IOCs a un mensaje de alerta (`SignalOutput`). | Paso de anotación que agrega metadatos de inteligencia de amenazas. |
| `to_signal` | El convertidor que formatea una coincidencia bruta en una señal de alerta estandarizada. | Función de normalización para informes posteriores. |
| Almacenamiento `Fraction` / `str` | La evidencia numérica se codifica como razones exactas de enteros (p. ej., 1/4) o cadenas de texto literales. | Elimina errores de redondeo; garantiza reproducibilidad. |
| `TOOL_NAME` | Una etiqueta constante que identifica el componente de software que realizó el análisis. | Metadatos de procedencia. |
| `ARTIFACT_RELIABILITY` | Una constante que define el nivel de confianza asignado a los artefactos procesados por este módulo. | Parámetro de clasificación de calidad de la evidencia. |

**Tipos de IOC soportados**

| Tipo | Descripción | Ejemplo |
|---|---|---|
| Hash | Suma de verificación criptográfica del contenido del archivo | `e3b0c44298fc1c149afbf4c8996fb924...` |
| Nombre de archivo | Nombre o ruta de un archivo de interés | `ransomware.exe` |
| Clave de registro | Entrada de configuración de Windows que indica persistencia | `HKCU\Software\Microsoft\Windows\CurrentVersion\Run` |
| Dirección IP | Dirección de host vinculada a infraestructura maliciosa | `198.51.100.33` |
| Dominio | Dominio de Internet utilizado para mando y control | `phishing.example.net` |
| Técnica MITRE | Identificador estandarizado del comportamiento del adversario | `T1055` (Process Injection) |

**Glosario**

- **Indicador de Compromiso (IOC)**: Artefacto forense que sugiere que un sistema ha sido vulnerado o expuesto a malware.
- **Hallazgo / Artefacto Forense**: Cualquier objeto o rastro recuperado de un medio digital durante una investigación.
- **Sistema Determinista**: Sistema en el que cada estado y salida está determinado de manera única por estados y entradas previas, sin aleatoriedad.
- **Número Racional Exacto (Fraction)**: Número expresado como razón de dos enteros (numerador y denominador), preservando precisión infinita sin redondeo.
- **Enriquecimiento de Señal**: Adición de información contextual a una alerta para clarificar su significado.
- **Función Hash**: Algoritmo determinista que asigna datos de tamaño arbitrario a una cadena de bits de tamaño fijo.
- **Técnica MITRE ATT&CK**: Base de conocimiento global de tácticas y técnicas de adversarios basada en observaciones del mundo real.

**Nota Científica**

> 【Nota Científica】
> En la literatura interdisciplinaria, los marcos semióticos de **Charles Sanders Peirce** (inferencia abductiva), **Umberto Eco** (teoría del signo) y **H. Paul Grice** (implicatura y comunicación cooperativa) se descartan ocasionalmente como metafísicos. En ingeniería forense son herramientas analíticas rigurosas. Considere una coincidencia de IOC: no es un presagio místico, sino una **medición de sensor**. Así como un termopar produce un voltaje que se asigna de manera determinista a la temperatura mediante leyes físicas, un `IOCRecord` asigna un artefacto recuperado a una clase de amenaza mediante reglas lógicas exactas. El "signo" es simplemente una correlación estructurada entre un estado físico y una representación simbólica. Este módulo operacionaliza ese principio imponiendo **aritmética entera determinista** y coincidencia simbólica exacta. No hay ambigüedad, redondeo ni adivinación interpretativa—solo inferencia mecanicista reproducible.


## РУССКИЙ

### Что представляет собой этот модуль?

Этот модуль, `vigia/sift/ioc_manager.py`, — это **движок индикаторов компрометации (IOC)**. Он функционирует как высокоточная справочная библиотека для цифровых расследований. Когда судебные эксперты извлекают артефакты — такие как отпечатки файлов (хеши), подозрительные имена файлов, ключи реестра Windows, сетевые адреса (IP или домены) или известные техники злоумышленников — из компьютерной системы, этот движок сравнивает каждый извлечённый элемент со структурированной базой данных ранее подтверждённых сигнатур угроз. При обнаружении точного совпадения движок регистрирует структурированный результат, связывающий доказательство с конкретным субъектом угрозы или семейством вредоносного ПО. Весь процесс детерминирован: одинаковые входные данные всегда дают одинаковый результат, поскольку движок опирается на точную символьную и целочисленную логику, а не на вероятностные догадки или неточные десятичные приближения.

**Таблица ключевых понятий**

| Понятие | Описание | Роль в судебном процессе |
|---|---|---|
| `IOCRecord` | Одна известная сигнатура угрозы, хранящаяся как структурированная справочная запись. | Эталонный образец для точного сравнения. |
| `IOCMatchResult` | Документированное соответствие между извлечённым артефактом и `IOCRecord`. | Верифицированный выходной данный, подтверждающий связь с угрозой. |
| `IOCManager` | Центральный контроллер, содержащий базу данных и выполняющий протокол сопоставления. | Детерминированный движок, управляющий всеми корреляциями. |
| `match_against_findings` | Пакетная процедура перекрёстной проверки списка судебных находок по базе данных. | Массовая корреляция по правилам точного равенства. |
| `enrich_signal` | Процедура добавления контекста из IOC к сообщению оповещения (`SignalOutput`). | Этап аннотирования метаданными Threat Intelligence. |
| `to_signal` | Преобразователь, форматирующий сырое совпадение в стандартизированный сигнал тревоги. | Функция нормализации для последующей отчётности. |
| Хранение `Fraction` / `str` | Числовые доказательства кодируются как точные отношения целых чисел (например, 1/4) или литеральные текстовые строки. | Устраняет ошибки округления; гарантирует воспроизводимость. |
| `TOOL_NAME` | Постоянная метка, идентифицирующая программный компонент, выполнивший анализ. | Метаданные происхождения. |
| `ARTIFACT_RELIABILITY` | Константа, определяющая уровень доверия, присваиваемый артефактам, обрабатываемым этим модулем. | Параметр оценки качества доказательств. |

**Типы поддерживаемых IOC**

| Тип | Описание | Пример |
|---|---|---|
| Хеш | Криптографическая контрольная сумма содержимого файла | `e3b0c44298fc1c149afbf4c8996fb924...` |
| Имя файла | Имя или путь файла, представляющего интерес | `ransomware.exe` |
| Ключ реестра | Запись конфигурации Windows, указывающая на персистентность | `HKCU\Software\Microsoft\Windows\CurrentVersion\Run` |
| IP-адрес | Адрес хоста, связанный с вредоносной инфраструктурой | `198.51.100.33` |
| Домен | Интернет-домен, используемый для управления и контроля | `phishing.example.net` |
| Техника MITRE | Стандартизированный идентификатор поведения злоумышленника | `T1055` (Process Injection) |

**Глоссарий**

- **Индикатор компрометации (IOC)**: Судебный артефакт, указывающий на то, что система была скомпрометирована или подверглась воздействию вредоносного ПО.
- **Судебная находка / Артефакт**: Любой объект или след, извлечённый из цифрового носителя в ходе расследования.
- **Детерминированная система**: Система, в которой каждое состояние и выход однозначно определяются предыдущими состояниями и входами, без случайности.
- **Точное рациональное число (Fraction)**: Число, выраженное как отношение двух целых чисел (числителя и знаменателя), сохраняющее бесконечную точность без округления.
- **Обогащение сигнала**: Добавление контекстной информации к оповещению для прояснения его значимости.
- **Хеш-функция**: Детерминированный алгоритм, отображающий данные произвольного размера в битовую строку фиксированного размера.
- **Техника MITRE ATT&CK**: Глобально доступная база знаний о тактиках и техниках противника, основанная на реальных наблюдениях.

**Научное примечание**

> 【Научное примечание】
> В междисциплинарной литературе семиотические концепции **Чарльза Сандерса Пирса** (абдуктивное умозаключение), **Умберто Эко** (теория знака) и **Герберта Пола Грайса** (импликатура и кооперативная коммуникация) иногда отвергаются как метафизические. В судебной инженерии они являются строгими аналитическими инструментами. Рассмотрите совпадение IOC: это не мистическое предзнаменование, а **показание датчика**. Подобно тому как термопара генерирует напряжение, которое детерминированно соответствует температуре согласно физическим законам, `IOCRecord` соотносит извлечённый артефакт с классом угрозы посредством точных логических правил. «Знак» — это просто структурированная корреляция между физическим состоянием и символическим представлением. Данный модуль операционализирует этот принцип, применяя **детерминированную целочисленную арифметику** и точное символьное сопоставление. Нет неоднозначности, округления или интерпретативного пророчества — только воспроизводимый механистический вывод.


## 中文

### 本模块是什么？

本模块（`vigia/sift/ioc_manager.py`）是**失陷指标（IOC）引擎**。其功能类似于数字调查中的高精度参考库。当取证科学家从计算机系统中提取**取证工件**时——例如文件指纹（哈希值）、可疑文件名、Windows 注册表项、网络地址（IP 或域名）或已知的攻击者技术——该引擎会将每一个提取项与先前确认的威胁特征数据库进行比对。一旦发现精确匹配，引擎即生成结构化结果，将证据与特定的威胁行为体或恶意软件家族关联起来。整个过程是**确定性**的：相同的输入总是产生相同的输出，因为引擎完全依赖精确的符号逻辑与**确定性整数运算**，从不使用概率推测或不精确的小数近似。

**关键概念**

| 概念 | 说明 | 取证工作流中的角色 |
|---|---|---|
| `IOCRecord` | 以结构化参考条目存储的单一已知威胁特征。 | 用于精确比对的基准真值模式。 |
| `IOCMatchResult` | 已恢复的取证工件与 `IOCRecord` 之间已记录的对应关系。 | 确认威胁关联的已验证输出数据。 |
| `IOCManager` | 承载数据库并执行匹配协议的核心控制器。 | 管理所有关联关系的确定性引擎。 |
| `match_against_findings` | 将一批取证发现结果与数据库进行交叉核验的批量程序。 | 基于精确相等规则的大规模关联。 |
| `enrich_signal` | 向警报消息（`SignalOutput`）追加 IOC 衍生上下文的程序。 | 添加威胁情报元数据的标注步骤。 |
| `to_signal` | 将原始匹配结果格式化为标准化警报信号的转换器。 | 用于下游报告的规范化功能。 |
| `Fraction` / `str` 存储 | 数值证据采用精确的整数比（如 1/4）或字面文本字符串进行编码。 | 消除舍入误差，确保结果可复现。 |
| `TOOL_NAME` | 标识执行分析之软件组件的常量标签。 | 溯源元数据。 |
| `ARTIFACT_RELIABILITY` | 定义本模块处理之取证工件可信度等级的常量。 | 证据质量分级参数。 |

**支持的 IOC 类型**

| 类型 | 说明 | 示例 |
|---|---|---|
| 哈希值 | 文件内容的加密学校验和 | `e3b0c44298fc1c149afbf4c8996fb924...` |
| 文件名 | 可疑文件的名称或路径 | `ransomware.exe` |
| 注册表项 | 指示持久化机制的 Windows 配置条目 | `HKCU\Software\Microsoft\Windows\CurrentVersion\Run` |
| IP 地址 | 与恶意基础设施关联的主机地址 | `198.51.100.33` |
| 域名 | 用于命令与控制的互联网域名 | `phishing.example.net` |
| MITRE 技术 | 攻击者行为的标准化标识符 | `T1055`（进程注入） |

**术语表**

- **失陷指标（IOC）**：表明系统已遭入侵或暴露于恶意软件的取证工件。
- **取证发现 / 取证工件**：调查期间从数字介质中恢复的任何对象或痕迹。
- **确定性系统**：每一状态和输出均由先前状态与输入唯一确定、不含随机性的系统。
- **精确有理数（Fraction）**：以两个整数之比（分子与分母）表示的数值，可在不产生舍入误差的前提下保持无限精度。
- **信号富化**：向警报添加上下文信息以阐明其含义的过程。
- **哈希函数**：将任意大小的数据映射为固定长度位串的确定性算法。
- **MITRE ATT&CK 技术**：基于真实观测的攻击者战术与技术全球知识库。
- **逻辑断裂**：由概率推断或浮点近似计算引入的推理链中断，确定性整数运算可系统性地消除此类断裂。

**科学说明**

> 【科学说明】
> 在跨学科文献中，**皮尔斯**（Charles Sanders Peirce）的溯因推理、**艾柯**（Umberto Eco）的符号理论以及**格赖斯**（H. Paul Grice）的会话含义与合作原则，有时被视为形而上学而遭到忽视。然而在取证工程领域，它们是严格的分析工具。以 IOC 匹配为例：这并非神秘预兆，而是一次**传感器读数**。正如热电偶依据物理定律将电压值确定性地映射至温度，`IOCRecord` 同样通过精确逻辑规则将已恢复的取证工件映射至威胁类别。所谓"符号"，不过是物理状态与符号表示之间有结构的关联。本模块通过强制执行**确定性整数运算**与精确符号匹配来实现这一原则，从根本上消除**逻辑断裂**的风险。系统中没有歧义、没有舍入误差、没有解释性臆断——只有可复现的机械式推断。

---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
