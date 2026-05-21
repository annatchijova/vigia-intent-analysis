<!--
VIGIA Academic Documentation
Module: 74d4c0cc
Batch ID: vigia-doc-0144-74d4c0cc
Generated: 2026-05-20T14:56:47.875502+00:00
-->

The user wants technical documentation for a Python module (`vigia/sift/usb_device_tracker.py`) written for scientists who don't know Python. It must be in Markdown with 4 languages: ENGLISH, ESPAÑOL, РУССКИЙ, 中文.

Requirements:
1. Target audience: scientists/researchers who do NOT know Python.
2. Format: Markdown with 4 language sections.
3. Each section must include:
   - "What Is This Module?" (plain language)
   - Key concepts with tables
   - A glossary of technical terms
   - A 【科学说明】/【Scientific Note】 box explaining Peirce/Eco/Grice terminology is NOT mysticism — use the sensor analogy.
4. Chinese translations must use: 艾柯 (not Eco), 格赖斯 (not Grice), 取证工件 (not 制品), 逻辑断裂 (not 裂缝).
5. 
6. Do NOT use floating-point math explanations — emphasize deterministic integer arithmetic where applicable.

Module details:
- Path: vigia/sift/usb_device_tracker.py
- Docstring: "Rastrea dispositivos USB conectados al sistema. Detecta exfiltración física de datos, dispositivos no autorizados, y correlación con actividad de red (exfiltración híbrida)."
- FIX P0: Todo valor numérico en evidence dict usa Fraction/str. NUNCA float. (All numeric values in evidence dict use Fraction/str. NEVER float.)
- Classes:
  - USBDeviceRecord
  - USBAnalysisResult
  - USBDeviceTracker: Analiza registros USB desde Registry o logs de sistema.
- Functions:
  - to_signal()
  - analyze_registry_hive()
  - correlate_with_network(): Detecta exfiltración híbrida: datos copiados a USB + subidos a nube. Si hay actividad USB y actividad de red a dominios [sentence cuts off, but implies suspicious domains]
- Constants & Config:
  - TOOL_NAME
  - ARTIFACT_RELIABILITY
  - SUSPICIOUS_VID_PID

Additional constraints:
- Academic technical writer style.
- Never use floating-point math explanations for deterministic systems. Emphasize deterministic integer arithmetic. The evidence dict uses Fraction/str, never float. This is crucial.
- The scientific note must explain Peirce/Eco/Grice terminology is not mysticism using a sensor analogy. Peirce (semiotics), Eco (interpretation), Grice (cooperative principle / implicature). Need to frame these as formal models of evidence interpretation, analogous to how a sensor transduces physical signals into data. They are epistemological frameworks, not mysticism.

Structure for each language section:
- Heading in that language.
- Subsection: What Is This Module?
- Subsection: Key Concepts (with tables)
- Subsection: Glossary
- Subsection: Scientific Note (in Chinese: 【科学说明】, but user says each section must include a 【科学说明】/【Scientific Note】 box. So in each language section, use the appropriate label, maybe keeping the Chinese markers for Chinese and translated for others? The prompt says: A 【科学说明】/【Scientific Note】 box. Probably in each language section, use the localized version but maybe the Chinese section uses 【科学说明】 and others use 【Scientific Note】 or similar. I'll do:
  - ENGLISH: > **【Scientific Note】**
  - ESPAÑOL: > **【Nota Científica】**
  - РУССКИЙ: > **【Научное Примечание】**
  - 中文: > **【科学说明】**
  But the prompt explicitly says "A 【科学说明】/【Scientific Note】 box". I'll interpret as: in English, label it 【Scientific Note】, in Chinese label it 【科学说明】, and others analogously. Or perhaps literally include both? No, that would be messy. I'll use the localized bracketed title.

Wait, the prompt says: "A 【科学说明】/【Scientific Note】 box explaining that Peirce/Eco/Grice terminology is NOT mysticism — use the sensor analogy". This might mean the box should be titled with both? Or just that type of box. I will use a blockquote or callout box with the title in the respective language. For Chinese, I'll use 【科学说明】. For English, I'll use **Scientific Note**. But to be safe and match the prompt's slash notation, maybe I should use the combined title? That seems weird in a non-Chinese section. I'll use:
- EN: > **Scientific Note**
- ES: > **Nota Científica**
- RU: > **Научное примечание**
- ZH: > **【科学说明】**

Let's think about the content.

**What Is This Module?**
It's a digital forensics tool that tracks USB device connections on a system. It reads Windows Registry or system logs to find evidence of USB devices. It detects physical data exfiltration, unauthorized devices, and correlates USB activity with network activity to find hybrid exfiltration (USB + cloud). It ensures all numeric evidence uses exact rational numbers (Fraction) or string representations, avoiding floating-point imprecision.

**Key Concepts Tables:**

We need tables for:
- Classes: USBDeviceRecord, USBAnalysisResult, USBDeviceTracker.
- Functions: to_signal, analyze_registry_hive, correlate_with_network.
- Constants: TOOL_NAME, ARTIFACT_RELIABILITY, SUSPICIOUS_VID_PID.
- Deterministic Arithmetic Rule (P0): Fraction/str, never float.

Maybe one table for "Core Components", one for "Evidence Handling Rules", one for "Threat Patterns".

Table 1: Core Components
| Component | Role | Analogy for Non-Programmers |
|---|---|---|
| USBDeviceRecord | Stores properties of a single USB device (VID, PID, timestamps) | A lab notebook entry for one specimen |
| USBAnalysisResult | Aggregates findings and flags anomalies | A pathology report summarizing test results |
| USBDeviceTracker | Orchestrates parsing of Registry/logs and runs analysis | The senior investigator managing the case file |
| to_signal() | Converts raw log entries into interpretable event tokens | A signal processor filtering noise from sensor data |
| analyze_registry_hive() | Reads the Windows Registry hive containing USB history | Extracting strata from a geological core sample |
| correlate_with_network() | Cross-references USB timestamps with outbound network flows | Checking if a lab sample left the facility while data was also transmitted |

Table 2: Evidence Integrity & Deterministic Arithmetic
| Rule | Requirement | Scientific Rationale |
|---|---|---|
| P0 — Exact Numeric Storage | All quantities stored as `Fraction` (rational) or `str` | Eliminates rounding errors inherent in floating-point representation; guarantees reproducible measurements |
| No Float Policy | Floating-point types forbidden in evidence dictionaries | Floats are non-deterministic approximations; forensic conclusions require exact, repeatable values |

Table 3: Configuration Constants
| Constant | Purpose |
|---|---|
| TOOL_NAME | Identifier string for the forensic module |
| ARTIFACT_RELIABILITY | Confidence分级 /分级 indicator assigned to the USB data source |
| SUSPICIOUS_VID_PID | Catalog of known-suspicious Vendor/Product IDs used for triage |

**Glossary:**
Need technical terms explained for scientists who don't know Python.

Terms:
- Registry Hive: A binary database in Windows storing hardware and software configuration, including USB connection history.
- VID/PID: Vendor ID and Product ID. Unique hexadecimal identifiers for USB device manufacturers and models.
- Exfiltration: Unauthorized transfer of data out of a secure environment.
- Hybrid Exfiltration: A two-stage leak where data is copied to a local removable device (USB) AND transmitted over a network (cloud) to maximize bypass probability.
- Deterministic Integer Arithmetic: Calculations using exact whole numbers or rational fractions (Fraction) that produce identical results on every repetition, without rounding errors.
- Evidence Dictionary: A structured data container holding forensic findings in key-value pairs.
- Timestamp Correlation: The process of aligning events from different logs by their time markers to establish causal or sequential relationships.
- Signal (in `to_signal`): A discrete, typed event extracted from raw log noise, ready for semiotic interpretation (Peircean sign).
- Float / Floating-Point: A computer number format that approximates real values with inherent imprecision; explicitly excluded from this module.

**Scientific Note:**
Must explain Peirce/Eco/Grice terminology is not mysticism, using sensor analogy.

Content idea:
Semiotics (Peirce), interpretative frames (Eco), and conversational implicature / cooperative maxims (Grice) are formal epistemological models. They describe how an observer moves from raw sensory data to meaningful conclusions.
- Peirce: sign (representamen), object, interpretant. Like a sensor: voltage (sign) corresponds to temperature (object) and triggers a reading (interpretant).
- Eco: interpretation depends on context/encyclopedia. Like calibrating a sensor against known references.
- Grice: cooperative principle implies that communicative (or system) behavior follows rational maxims. Violations generate "implicatures" (anomalies). Like detecting a sensor reading that violates expected patterns, signaling instrument error or physical tampering.
So, terminology like "sign", "interpretant", or "implicature" is not metaphysical mysticism; it is a rigorous taxonomy for evidence interpretation, exactly analogous to how a transducer converts physical energy into structured data.

Need to ensure Chinese terms: 艾柯 (Eco), 格赖斯 (Grice), 取证工件 (artifact... but here in glossary maybe), 逻辑断裂 (logical break/fracture?). Wait, the user said "Chinese translations must use: 艾柯 (not Eco), 格赖斯 (not Grice), 取证工件 (not 制品), 逻辑断裂 (not 裂缝)". So in the Chinese section, I must ensure these specific terms are used. Let's map them:

- 艾柯 = Umberto Eco.
- 格赖斯 = H.P. Grice.
- 取证工件 = forensic artifact (instead of 制品 or 工件 alone? Actually 取证工件 is specified instead of 制品).
- 逻辑断裂 = logical fracture/break (instead of 裂缝).

Where to use them:
In the Chinese glossary, for "Artifact" use 取证工件.
In the scientific note, mention 艾柯 and 格赖斯.
For "logical break/gap" maybe in correlation or analysis context use 逻辑断裂 instead of 裂缝.

**License line:**
Must include exactly: ""
This can go at the very bottom of the document, or per section? The prompt says "License line". Usually one at the end is fine. I'll put it at the bottom.

**No floating-point math explanations:**
When discussing timestamps or counts, emphasize that the module stores them as exact integers or Fractions. Do not explain floating-point internals (mantissa, exponent, etc.) as a reason. Just state that deterministic integer or rational arithmetic is used, and floats are excluded to ensure reproducibility.

**Writing style:**
Academic, technical, but accessible to non-Python scientists. Avoid Python-specific jargon (like "class", "method") without explanation, or explain it in scientific terms. Actually, the prompt asks for documentation for a Python module, so we can mention the names but must explain them plainly.

Let's draft each section.

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

Wait, I need to check the Chinese requirements again:
- 艾柯 (not Eco) -> I used 艾柯.
- 格赖斯 (not Grice) -> I used 格赖斯.
- 取证工件 (not 制品) -> I haven't used this term yet in the Chinese section. I should make sure to use it instead of 制品/工件 where appropriate. The glossary has "证据字典", but "artifact" is usually a forensic artifact. The constant is ARTIFACT_RELIABILITY. In the table I translated ARTIFACT_RELIABILITY as 数据源的质量置信等级, but maybe I should mention 取证工件 somewhere. Let's integrate "取证工件" into the glossary or the key concepts. The constant `ARTIFACT_RELIABILITY` refers to the reliability of the artifact. In Chinese digital forensics, "artifact" is often translated as "取证工件" or "证据工件". I should use 取证工件 in the glossary for "Artifact" or in the description of ARTIFACT_RELIABILITY.

Let's adjust the Chinese section:
In the Key Concepts table for ARTIFACT_RELIABILITY: "赋予取证工件数据源的质量置信等级" or just change the glossary entry for Artifact.

Add to Chinese Glossary:
- **取证工件**：指在数字取证过程中产生的、可作为证据使用的数据对象或记录片段。本模块中，注册表项与日志条目均属取证工件。

And maybe in the English/Spanish/Russian, mention "Artifact" explicitly.

Also, for 逻辑断裂 (not 裂缝): I need to use this somewhere. Maybe in the explanation of correlation or anomaly detection? The user said "逻辑断裂 (not 裂缝)". This means if I describe a logical gap/break/fracture
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
