<!--
VIGIA Academic Documentation
Module: 74d4c0cc
Batch ID: vigia-doc-0144-74d4c0cc
Generated: 2026-05-20T14:56:47.875502+00:00
-->

---

### ENGLISH

#### What Is This Module?
`vigia/sift/usb_device_tracker.py` is a forensic analysis engine that reconstructs the history of USB device connections on a computer. It operates like a laboratory logbook reviewer: it reads the system’s Registry (the master index of hardware events) or system log files, extracts records of every removable device that was plugged in, and flags suspicious patterns. Specifically, it detects physical data exfiltration—unauthorized copying of information onto a USB stick—and “hybrid exfiltration,” where data is simultaneously copied to a USB device and uploaded to a remote server (cloud). To preserve scientific rigor, every numeric value in the evidence output is stored as an exact rational number or string, never as an imprecise floating-point value.

#### Key Concepts

| Component | Function | Scientific Analogy |
|---|---|---|
| `USBDeviceRecord` | Stores identifiers and timestamps for one USB device | A specimen card in a biological collection |
| `USBAnalysisResult` | Aggregates all findings, reliability scores, and alerts | A consolidated pathology report |
| `USBDeviceTracker` | Coordinates reading the Registry/logs and launches analysis | The principal investigator directing the study |
| `to_signal()` | Transforms a raw log entry into a discrete, typed event | A sensor converting an analog voltage into a digital reading |
| `analyze_registry_hive()` | Parses the Windows Registry binary file for USB history | Extracting layered core samples from permafrost |
| `correlate_with_network()` | Matches USB activity timeframes with outbound network flows | Cross-referencing a sample checkout log with security camera footage |
| `TOOL_NAME` | Canonical name of the forensic instrument | Catalog number of the analytical device |
| `ARTIFACT_RELIABILITY` | Qualitative confidence grade assigned to the data source | Uncertainty coefficient on a calibration standard |
| `SUSPICIOUS_VID_PID` | Blacklist of Vendor/Product ID pairs known to be high-risk | List of prohibited chemical precursors |

**Deterministic Evidence Arithmetic**

| Rule | Implementation | Rationale |
|---|---|---|
| P0 — Exact Quantities | All numeric evidence uses `Fraction` or `str` | Guarantees bitwise reproducibility across analyses |
| No Floating-Point | Float types are prohibited in evidence dictionaries | Floating-point arithmetic introduces non-deterministic rounding; forensic science requires exactitude |

#### Glossary

- **Registry Hive**: A binary database in Windows operating systems that records hardware configurations, software settings, and—critically for this module—a history of attached USB devices.
- **VID / PID**: Vendor ID and Product ID. Hexadecimal codes that uniquely identify the manufacturer and model of a USB device, comparable to a CAS registry number for a chemical compound.
- **Exfiltration**: The unauthorized removal of data from a secured environment.
- **Hybrid Exfiltration**: A dual-channel leak in which data is transferred to a local removable medium (USB) and also transmitted over a network within a correlated time window.
- **Evidence Dictionary**: A structured key-value repository holding the results of a forensic examination.
- **Deterministic Integer Arithmetic**: Mathematical operations using exact integers or rational fractions that yield identical outputs on every execution, ensuring reproducible measurements.
- **Signal**: In the context of `to_signal()`, a discrete, interpretable event extracted from noisy raw logs, analogous to a filtered digital sensor reading.
- **Floating-Point**: A computer number representation that approximates real values; explicitly excluded from this module to prevent rounding artifacts.

> **【Scientific Note】**
> The module occasionally employs terminology inspired by semiotics—**Peirce** (theory of signs), **Eco** (interpretative frames), and **Grice** (cooperative maxims and implicature). These are not mystical or metaphysical concepts. They are formal epistemological models that describe how raw data becomes meaningful evidence, functionally identical to the way a physical sensor transduces energy into a structured digital reading. A “sign” is the voltage pulse; the “object” is the physical state being measured; the “interpretant” is the calibrated value you record. When a system violates Gricean maxims—say, by communicating in an unnecessarily obscure or contradictory manner—it generates an “implicature,” much like a sensor returning an out-of-range value flags instrument tampering or an anomalous physical condition. **Eco**’s emphasis on encyclopedic context mirrors the need to calibrate a sensor against known reference standards. Thus, these terms denote rigorous analytical categories, not mysticism.

---

### ESPAÑOL

#### ¿Qué es este módulo?
`vigia/sift/usb_device_tracker.py` es un motor de análisis forense que reconstruye el historial de conexiones de dispositivos USB en una computadora. Funciona como un revisor de bitácoras de laboratorio: lee el Registro del sistema (el índice maestro de eventos de hardware) o los archivos de registro, extrae constancias de cada dispositivo removible conectado y marca patrones sospechosos. Específicamente, detecta exfiltración física de datos—copias no autorizadas a una memoria USB—y «exfiltración híbrida», donde los datos se copian simultáneamente a un USB y se suben a un servidor remoto (nube). Para preservar el rigor científico, todo valor numérico en la evidencia se almacena como un número racional exacto o cadena de texto, nunca como un valor de punto flotante impreciso.

#### Conceptos Clave

| Componente | Función | Analogía Científica |
|---|---|---|
| `USBDeviceRecord` | Almacena identificadores y marcas temporales de un dispositivo USB | Una ficha de especimen en una colección biológica |
| `USBAnalysisResult` | Agrega hallazgos, puntuaciones de confiabilidad y alertas | Un informe de patología consolidado |
| `USBDeviceTracker` | Coordina la lectura del Registro/logs y lanza el análisis | El investigador principal dirigiendo el estudio |
| `to_signal()` | Transforma una entrada cruda del registro en un evento discreto y tipado | Un sensor que convierte voltaje analógico en lectura digital |
| `analyze_registry_hive()` | Analiza el archivo binario del Registro de Windows en busca de historial USB | Extraer muestras estratificadas de permafrost |
| `correlate_with_network()` | Cruza los intervalos de actividad USB con flujos de red salientes | Cotejar un registro de préstamo de muestras con grabaciones de cámaras |
| `TOOL_NAME` | Nombre canónico del instrumento forense | Número de catálogo del dispositivo analítico |
| `ARTIFACT_RELIABILITY` | Grado cualitativo de confianza asignado a la fuente de datos | Coeficiente de incertidumbre de un patrón de calibración |
| `SUSPICIOUS_VID_PID` | Lista negra de pares Vendor/Product ID de alto riesgo | Lista de precursores químicos prohibidos |

**Aritmética Determinista de la Evidencia**

| Regla | Implementación | Justificación |
|---|---|---|
| P0 — Cantidades exactas | Toda evidencia numérica usa `Fraction` o `str` | Garantiza reproducibilidad bit a bit entre análisis |
| Sin punto flotante | Los tipos flotante están prohibidos en diccionarios de evidencia | La aritmética de punto flotante introduce errores de redondeo no deterministas; la ciencia forense exige exactitud |

#### Glosario

- **Hive del Registro (Registry Hive)**: Base de datos binaria en sistemas Windows que registra configuraciones de hardware, ajustes de software y, lo más importante para este módulo, el historial de dispositivos USB conectados.
- **VID / PID**: *Vendor ID* e *Product ID*. Códigos hexadecimales que identifican de manera única al fabricante y modelo de un dispositivo USB, comparables a un número de registro CAS para un compuesto químico.
- **Exfiltración**: Extracción no autorizada de datos desde un entorno seguro.
- **Exfiltración Híbrida**: Fuga de doble canal en la que los datos se transfieren a un medio removible local (USB) y también se transmiten por red dentro de una ventana temporal correlacionada.
- **Diccionario de Evidencia**: Repositorio estructurado de pares clave-valor que contiene los resultados de un examen forense.
- **Aritmética Entera Determinista**: Operaciones matemáticas con enteros exactos o fracciones racionales que producen el mismo resultado en cada ejecución, asegurando mediciones reproducibles.
- **Señal**: En el contexto de `to_signal()`, un evento discreto e interpretable extraído de registros crudos ruidosos, análogo a una lectura digital filtrada de un sensor.
- **Punto Flotante**: Representación numérica computacional que aproxima valores reales; excluida explícitamente de este módulo para prevenir artefactos de redondeo.

> **【Nota Científica】**
> El módulo emplea ocasionalmente terminología inspirada en la semiótica—**Peirce** (teoría de los signos), **Eco** (marcos interpretativos) y **Grice** (máximas cooperativas e implicaturas). Estos no son conceptos místicos o metafísicos. Son modelos epistemológicos formales que describen cómo los datos brutos se convierten en evidencia significativa, funcionalmente idénticos a la forma en que un sensor físico transduce energía en una lectura digital estructurada. Un «signo» es el pulso de voltaje; el «objeto» es el estado físico que se mide; el «interpretante» es el valor calibrado que se registra. Cuando un sistema viola las máximas de Grice—por ejemplo, comunicándose de manera innecesariamente oscura o contradictoria—genera una «implicatura», de forma similar a como un sensor que devuelve un valor fuera de rango señala manipulación del instrumento o una condición física anómala. El énfasis de **Eco** en el contexto enciclopédico se asemeja a la necesidad de calibrar un sensor contra estándares de referencia conocidos. Por tanto, estos términos denotan categorías analíticas rigurosas, no misticismo.

---

### РУССКИЙ

#### Что представляет собой этот модуль?
`vigia/sift/usb_device_tracker.py` — это судебно-экспертный аналитический модуль, восстанавливающий историю подключений USB-устройств к компьютеру. Он работает как рецензент лабораторных журналов: считывает системный Реестр (главный индекс аппаратных событий) или системные журналы, извлекает записи о каждом подключённом съёмном устройстве и выявляет подозрительные закономерности. В частности, он обнаруживает физическую эксфильтрацию данных — несанкционированное копирование информации на USB-накопитель — а также «гибридную эксфильтрацию», при которой данные одновременно копируются на USB и загружаются на удалённый сервер (облако). В целях научной строгости все числовые значения в выходных данных сохраняются в виде точных рациональных чисел или строк, но никак не в виде приближённых чисел с плавающей запятой.

#### Ключевые понятия

| Компонент | Функция | Научная аналогия |
|---|---|---|
| `USBDeviceRecord` | Хранит идентификаторы и временные метки одного USB-устройства | Спецификационная карточка образца в биологической коллекции |
| `USBAnalysisResult` | Агрегирует все находки, оценки надёжности и оповещения | Сводный патологоанатомический отчёт |
| `USBDeviceTracker` | Координирует чтение Реестра/журналов и запускает анализ | Руководитель исследования, управляющий делом |
| `to_signal()` | Преобразует необработанную запись журнала в дискретное типизированное событие | Датчик, превращающий аналоговое напряжение в цифровое показание |
| `analyze_registry_hive()` | Разбирает двоичный файл Реестра Windows на предмет истории USB | Извлечение слоистых кернов из вечной мерзлоты |
| `correlate_with_network()` | Сопоставляет интервалы USB-активности с исходящими сетевыми потоками | Сверка журнала выдачи образцов с записями камер наблюдения |
| `TOOL_NAME` | Каноническое название судебного инструмента | Каталожный номер аналитического прибора |
| `ARTIFACT_RELIABILITY` | Качественная оценка доверия к источнику данных | Коэффициент неопределённости калибровочного эталона |
| `SUSPICIOUS_VID_PID` | Чёрный список пар Vendor/Product ID с повышенным риском | Перечень запрещённых химических прекурсоров |

**Детерминированная арифметика доказательств**

| Правило | Реализация | Обоснование |
|---|---|---|
| P0 — Точные величины | Все числовые доказательства используют `Fraction` или `str` | Гарантирует побитовую воспроизводимость при повторных анализах |
| Запрет чисел с плавающей запятой | Типы float запрещены в словарях доказательств | Арифметика с плавающей запятой вносит недетерминированные погрешности округления; судебная экспертиза требует точности |

#### Глоссарий

- **Улей Реестра (Registry Hive)**: Двоичная база данных в операционных системах Windows, регистрирующая конфигурации оборудования, параметры программного обеспечения и, что критически важно для данного модуля, историю подключённых USB-устройств.
- **VID / PID**: Идентификаторы производителя (*Vendor ID*) и изделия (*Product ID*). Шестнадцатеричные коды, однозначно идентифицирующие изготовителя и модель USB-устройства, сопоставимые с регистрационным номером CAS химического соединения.
- **Эксфильтрация**: Несанкционированное изъятие данных из защищённой среды.
- **Гибридная эксфильтрация**: Двухканальная утечка, при которой данные переносятся на локальный съёмный носитель (USB) и одновременно передаются по сети в коррелированном временном окне.
- **Словарь доказательств (Evidence Dictionary)**: Структурированное хранилище пар «ключ—значение», содержащее результаты судебно-экспертного исследования.
- **Детерминированная целочисленная арифметика**: Математические операции с точными целыми числами или рациональными дробями, дающие одинаковый результат при каждом выполнении и обеспечивающие воспроизводимость измерений.
- **Сигнал**: В контексте `to_signal()` — дискретное интерпретируемое событие, извлечённое из зашумлённых необработанных журналов, аналогично отфильтрованному цифровому показанию датчика.
- **Число с плавающей запятой (Floating-Point)**: Компьютерное представление чисел, приближающее действительные значения; явно исключено из данного модуля для предотвращения артефактов округления.

> **【Научное Примечание】**
> В модуле время от времени используется терминология, навеянная семиотикой — **Пирс** (теория знаков), **Эко** (интерпретативные рамки) и **Грайс** (кооперативные максимы и импликатуры). Это не мистические или метафизические концепции. Это формальные эпистемологические модели, описывающие, как сырые данные превращаются в осмысленные доказательства; функционально они тождественны тому, как физический датчик преобразует энергию в структурированную цифровую запись. «Знак» — это импульс напряжения; «объект» — измеряемое физическое состояние; «интерпретант» — откалиброванное значение, заносимое в протокол. Когда система нарушает максимы Грайса — например, сообщая неоправданно запутанным или противоречивым образом — возникает «импликатура», подобно тому как показание датчика, выходящее за пределы диапазона, сигнализирует о вмешательстве в прибор или об аномальном физическом состоянии. Акцент **Эко** на энциклопедическом контексте отражает необходимость калибровки датчика по известным эталонам. Таким образом, эти термины обозначают строгие аналитические категории, а не мистицизм.

---

### 中文

#### 什么是本模块？
`vigia/sift/usb_device_tracker.py` 是一个法庭科学分析引擎，用于重构计算机上 USB 设备的连接历史。它的作用类似于实验室日志审查员：读取系统的注册表（硬件事件的索引主档）或系统日志文件，提取每一个曾连接的可移动设备记录，并标记可疑模式。具体而言，它能检测物理数据渗出（exfiltration）——即将信息非法复制到 U 盘——以及“混合渗出”，即数据在拷贝至 USB 设备的同时又被上传至远程服务器（云端）。为保持科学严谨性，证据输出中的所有数值均以精确有理数或字符串形式存储，绝不使用不精确的浮点数。

#### 核心概念

| 组件 | 功能 | 科学类比 |
|---|---|---|
| `USBDeviceRecord` | 存储单个 USB 设备的标识符与时间戳 | 生物标本库中的标本卡片 |
| `USBAnalysisResult` | 汇总所有发现、可靠性评分与告警 | 整合后的病理学报告 |
| `USBDeviceTracker` | 协调注册表/日志的读取并启动分析 | 主导研究的首席调查员 |
| `to_signal()` | 将原始日志条目转化为离散、类型化的事件 | 将模拟电压转换为数字读数的传感器 |
| `analyze_registry_hive()` | 解析 Windows 注册表二进制文件以提取 USB 历史 | 从多年冻土中提取分层岩芯 |
| `correlate_with_network()` | 将 USB 活动时段与出站网络流量进行交叉比对 | 将样本借出记录与监控录像进行核对 |
| `TOOL_NAME` | 取证工具的规范名称 | 分析仪器的目录编号 |
| `ARTIFACT_RELIABILITY` | 赋予数据源的质量置信等级 | 校准标准物的不确定度系数 |
| `SUSPICIOUS_VID_PID` | 已知高风险的厂商/产品 ID 对黑名单 | 禁止使用的化学前体清单 |

**确定性证据算术**

| 规则 | 实现方式 | 科学依据 |
|---|---|---|
| P0 — 精确量值 | 所有数值证据使用 `Fraction` 或 `str` | 保证多次分析之间的按位可复现性 |
| 禁用浮点 | 证据字典中禁止使用浮点类型 | 浮点运算会引入非确定性的舍入误差；法庭科学要求绝对精确 |

#### 术语表

- **注册表配置单元（Registry Hive）**：Windows 操作系统中的二进制数据库，记录硬件配置、软件设置，以及对本模块至关重要的已连接 USB 设备历史。
- **VID / PID**：厂商 ID（Vendor ID）与产品 ID（Product ID）。用于唯一标识 USB 设备制造商与型号的十六进制代码，类似于化学物质的 CAS 登记号。
- **数据渗出（Exfiltration）**：从受保护环境中未经授权移出数据的行为。
- **混合渗出（Hybrid Exfiltration）**：一种双通道泄漏，数据既被传输至本地可移动介质（USB），又在相关时间窗口内通过网络外传。
- **证据字典（Evidence Dictionary）**：以键值对形式存储法医检验结果的结构化仓库。在本模块中，其数值条目严格遵循 P0 规则。
- **确定性整数运算**：使用精确整数或有理分数进行的数学运算，每次执行均产生完全相同的结果，从而确保测量可复现。
- **信号（Signal）**：在 `to_signal()` 的语境下，指从嘈杂原始日志中提取的、可被解释的离散事件，类似于经滤波后的数字传感器读数。
- **浮点数（Floating-Point）**：一种近似表示实数的计算机数值格式；本模块明确排除浮点数，以防止舍入伪影。

> **【科学说明】**
> 本模块偶尔使用源自符号学的术语——**皮尔斯**（Peirce，符号理论）、**艾柯**（Umberto Eco，诠释框架）与**格赖斯**（H.P. Grice，合作原则及含义/implicature）。这些既非神秘主义，亦非形而上学玄思，而是形式化的认识论模型，用于描述原始数据如何转化为有意义的证据；其功能与物理传感器将能量转导为结构化数字读数的过程完全等同。“符号”即电压脉冲；“对象”即被测物理状态；“解释项”即你记录下的经校准数值。当系统违反格赖斯合作原则——例如以不必要地隐晦或自相矛盾的方式“交流”时——便产生一种“含义/隐涵”（implicature），这正如同传感器返回越界读数时，会提示仪器遭受篡改或存在异常物理条件。**艾柯**所强调的百科全书式语境，则类似于必须将传感器与已知参考标准进行校准。因此，这些术语代表的是严格的分析范畴，而非神秘主义。

---

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
