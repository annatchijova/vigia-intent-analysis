<!--
VIGIA Academic Documentation
Module: ab0b295d
Batch ID: vigia-doc-0054-ab0b295d
Generated: 2026-05-20T14:56:47.856061+00:00
-->

# Module Documentation: `vigia/core/forensic_adapter.py`

---

## ENGLISH

### What Is This Module?
`vigia/core/forensic_adapter.py` acts as a central translation hub. It converts raw digital forensic signals (`SignalOutput`) into structured objects compatible with the CAIE (Context-Aware Information Extraction) framework and the `AbductiveReasonerV2` engine. Think of it as a laboratory sample preparator: it takes unprocessed traces from disks, memory, or network traffic and labels, stratifies, and catalogs them into evidence layers with deterministic integer-based weights. No probabilistic approximations are used; every classification relies on exact integer arithmetic.

### Key Concepts

#### Core Classes
| Class | Scientific Role |
|---|---|
| `ForensicContext` | Investigative frame container; holds deterministic parameters so every artifact is interpreted under identical constraints. |
| `ForensicAdapter` | Central translator. Routes raw `SignalOutput` into CAIE artifacts and abductive records using exact integer maps. |
| `SignalOutput` | Raw digital trace before processing (e.g., memory dump fragment, registry hive, packet capture). |
| `CAIEArtifact` | Structured output object for the CAIE pipeline. Fields are typed and weighted by integer constants. |
| `EvidenceLayer` | A stratum of the evidence pyramid (disk, memory, network). Each layer carries an integer epistemic weight. |
| `OntologicalLevel` | Declares the category of an artifact (file, process, user) via discrete ontology maps. |
| `ArtifactRecord` | Immutable ledger entry that binds a raw signal to its interpreted, timestamped fact. |
| `CausalLink` | Deterministic relation between two records, encoded with integer relation codes and exact timestamps. |

#### Adapter Functions
| Function | Operation |
|---|---|
| `signal_to_caie_artifact()` | Translates one `SignalOutput` into a `CAIEArtifact` by querying `_LAYER_MAP` and `_EVIDENCE_MAP`. |
| `signal_to_abductive_record()` | Produces an abductive hypothesis from a signal; ranks candidates using integer scores only. |
| `signal_to_causal_link()` | Derives a causal edge between two artifacts. Relies on exact integer IDs and deterministic ordering. |
| `build_context()` | Instantiates `ForensicContext` from configuration constants, establishing deterministic registries. |

#### Configuration Constants
| Constant | Purpose |
|---|---|
| `_LAYER_MAP` | Internal lookup table mapping raw signal origins to discrete integer layer identifiers. |
| `_EVIDENCE_MAP` | Internal lookup table mapping evidence types to deterministic integer categories. |
| `_ONTOLOGY_MAP` | Internal lookup table mapping signals to ontological classes using exact integer keys. |
| `LAYER_EPISTEMIC_WEIGHT` | Integer constant specifying the evidential strength of a layer (e.g., `DISK_MFT = 5`). |
| `MEMORY` | Integer token for volatile memory evidence. |
| `NETWORK` | Integer token for network-traffic evidence. |
| `REGISTRY` | Integer token for operating-system registry evidence. |
| `DISK_MFT` | Integer token for Master File Table evidence. |
| `TECHNIQUE` | Integer token classifying adversary techniques. |
| `TACTIC` | Integer token classifying adversary tactics. |

### Glossary
| Term | Definition |
|---|---|
| **Abduction (Peircean)** | Inference to the best explanation; given an anomalous signal, the system generates the most plausible hypothesis using deterministic rules. |
| **CAIE** | Context-Aware Information Extraction; the framework that interprets artifacts within their investigative context. |
| **Epistemic Weight** | An integer score representing the reliability or importance of an evidence layer. |
| **Forensic Artifact** | A preserved and labeled unit of digital evidence (取证工件). |
| **SignalOutput** | The unprocessed digital trace before interpretation. |
| **Deterministic Integer Arithmetic** | Calculations using whole numbers only, ensuring reproducible results without rounding errors. |
| **Logical Gap (逻辑断裂)** | The inferential space between a raw signal and its interpreted hypothesis; bridged by abductive reasoning via integer-weighted rules. |

### 【Scientific Note】
【Scientific Note】The terminology of Peirce, Eco, and Grice is sometimes mistaken for metaphysical speculation. It is not. These terms are operational labels for deterministic information processes, analogous to a physical sensor. When a thermometer registers a temperature, no one assumes mysticism; likewise, when this module performs "abduction," it executes a deterministic hypothesis-selection routine over integer-weighted evidence layers. "Relevance" (Grice) and "interpretation" (Eco) are here implemented as exact lookup and mapping operations. The sensor analogy should dispel any notion of occult mechanisms: the adapter reads a signal, applies a deterministic transform, and writes a structured record. Nothing more, nothing less.

---

## ESPAÑOL

### ¿Qué es este módulo?
`vigia/core/forensic_adapter.py` funciona como un centro de traducción central. Convierte señales forenses digitales brutas (`SignalOutput`) en objetos estructurados compatibles con el marco CAIE y el motor `AbductiveReasonerV2`. Es similar a un preparador de muestras de laboratorio: toma rastros sin procesar de discos, memoria o tráfico de red y los etiqueta, estratifica y cataloga en capas de evidencia con pesos deterministas basados en enteros. No se emplea ninguna aproximación probabilística; cada clasificación se basa en aritmética exacta de enteros.

### Conceptos Clave

#### Clases Principales
| Clase | Función Científica |
|---|---|
| `ForensicContext` | Marco de investigación; contiene parámetros deterministas para interpretar artefactos en condiciones idénticas. |
| `ForensicAdapter` | Traductor central. Enruta `SignalOutput` bruto hacia artefactos CAIE y registros abductivos mediante mapas enteros exactos. |
| `SignalOutput` | Trazo digital en bruto antes del procesamiento (p. ej., fragmento de volcado de memoria, colmena de registro). |
| `CAIEArtifact` | Objeto estructurado para el pipeline CAIE. Campos tipados y ponderados por constantes enteras. |
| `EvidenceLayer` | Estrato de la pirámide de evidencia (disco, memoria, red). Cada capa porta un peso epistémico entero. |
| `OntologicalLevel` | Declara la categoría de un artefacto mediante mapas ontológicos discretos. |
| `ArtifactRecord` | Entrada inmutable del libro mayor que vincula una señal bruta con su hecho interpretado. |
| `CausalLink` | Relación determinista entre dos registros, codificada con códigos de relación enteros. |

#### Funciones del Adaptador
| Función | Operación |
|---|---|
| `signal_to_caie_artifact()` | Traduce un `SignalOutput` en `CAIEArtifact` consultando `_LAYER_MAP` y `_EVIDENCE_MAP`. |
| `signal_to_abductive_record()` | Produce una hipótesis abductiva a partir de una señal; ordena candidatos usando solo puntuaciones enteras. |
| `signal_to_causal_link()` | Deriva un arco causal entre dos artefactos. Depende de IDs enteros exactos y ordenamiento determinista. |
| `build_context()` | Instancia `ForensicContext` a partir de constantes de configuración, estableciendo registros deterministas. |

#### Constantes de Configuración
| Constante | Propósito |
|---|---|
| `_LAYER_MAP` | Tabla de búsqueda interna que mapea orígenes de señal a identificadores enteros de capa. |
| `_EVIDENCE_MAP` | Tabla de búsqueda que mapea tipos de evidencia a categorías enteras deterministas. |
| `_ONTOLOGY_MAP` | Tabla de búsqueda que mapea señales a clases ontológicas mediante claves enteras exactas. |
| `LAYER_EPISTEMIC_WEIGHT` | Constante entera que especifica la fuerza evidencial de una capa. |
| `MEMORY`, `NETWORK`, `REGISTRY`, `DISK_MFT`, `TECHNIQUE`, `TACTIC` | Tokens enteros para memoria volátil, red, registro, tabla MFT, técnicas y tácticas del adversario. |

### Glosario
| Término | Definición |
|---|---|
| **Abducción (Peirce)** | Inferencia a la mejor explicación; generación determinista de hipótesis ante una señal anómala. |
| **CAIE** | Extracción de Información Consciente del Contexto. |
| **Peso epistémico** | Puntuación entera que representa la fiabilidad de una capa de evidencia. |
| **Artefacto forense** | Unidad de evidencia digital preservada y etiquetada. |
| **SignalOutput** | Trazo digital sin procesar. |
| **Aritmética determinista de enteros** | Cálculos con números enteros, resultados reproducibles sin errores de redondeo. |

### 【Nota Científica】
【Nota Científica】La terminología de Peirce, Eco y Grice a veces se confunde con especulación metafísica. No lo es. Son etiquetas operacionales para procesos deterministas de información, análogos a un sensor físico. Cuando un termómetro registra temperatura, nadie asume misticismo; del mismo modo, cuando este módulo realiza "abducción", ejecuta una rutina determinista de selección de hipótesis sobre capas de evidencia ponderadas con enteros. La "relevancia" (Grice) y la "interpretación" (Eco) se implementan aquí como operaciones exactas de búsqueda y mapeo. La analogía del sensor debe disipar cualquier noción de mecanismos ocultos: el adaptador lee una señal, aplica una transformación determinista y escribe un registro estructurado. Nada más, nada menos.

---

## РУССКИЙ

### Что это за модуль?
`vigia/core/forensic_adapter.py` служит центральным узлом трансляции. Он преобразует сырые цифровые криминалистические сигналы (`SignalOutput`) в структурированные объекты, совместимые с фреймворком CAIE и движком `AbductiveReasonerV2`. Это аналог лабораторного препаратора образцов: берутся необработанные следы с дисков, памяти или сетевого трафика, которые затем маркируются, стратифицируются и каталогизируются по слоям доказательств с детерминированными целочисленными весами. Вероятностные приближения не используются; каждая классификация опирается на точную целочисленную арифметику.

### Ключевые Понятия

#### Основные Классы
| Класс | Научная роль |
|---|---|
| `ForensicContext` | Среда расследования; содержит детерминированные параметры для интерпретации артефактов в идентичных условиях. |
| `ForensicAdapter` | Центральный транслятор. Направляет сырые `SignalOutput` в артефакты CAIE и абдуктивные записи с помощью точных целочисленных карт. |
| `SignalOutput` | Сырой цифровой след до обработки (например, фрагмент дампа памяти, ветвь реестра). |
| `CAIEArtifact` | Структурированный выходной объект для конвейера CAIE. Поля типизированы и взвешены целочисленными константами. |
| `EvidenceLayer` | Слой пирамиды доказательств (диск, память, сеть). Каждый слой несёт целочисленный эпистемический вес. |
| `OntologicalLevel` | Заявляет категорию артефакта (файл, процесс, пользователь) через дискретные онтологические карты. |
| `ArtifactRecord` | Неизменяемая запись реестра, связывающая сырой сигнал с интерпретированным фактом. |
| `CausalLink` | Детерминированная связь между двумя записями, кодируемая целочисленными кодами отношений. |

#### Функции Адаптера
| Функция | Операция |
|---|---|
| `signal_to_caie_artifact()` | Преобразует `SignalOutput` в `CAIEArtifact` по запросу к `_LAYER_MAP` и `_EVIDENCE_MAP`. |
| `signal_to_abductive_record()` | Формирует абдуктивную гипотезу из сигнала; ранжирует кандидатов исключительно по целочисленным оценкам. |
| `signal_to_causal_link()` | Выводит причинное ребро между двумя артефактами. Опирается на точные целочисленные идентификаторы. |
| `build_context()` | Создаёт экземпляр `ForensicContext` из конфигурационных констант, устанавливая детерминированные реестры. |

#### Константы Конфигурации
| Константа | Назначение |
|---|---|
| `_LAYER_MAP` | Внутренняя таблица отображения источников сигнала на дискретные целочисленные идентификаторы слоёв. |
| `_EVIDENCE_MAP` | Таблица отображения типов доказательств на детерминированные целочисленные категории. |
| `_ONTOLOGY_MAP` | Таблица отображения сигналов на онтологические классы по точным целочисленным ключам. |
| `LAYER_EPISTEMIC_WEIGHT` | Целочисленная константа, задающая доказательную силу слоя. |
| `MEMORY`, `NETWORK`, `REGISTRY`, `DISK_MFT`, `TECHNIQUE`, `TACTIC` | Целочисленные токены для оперативной памяти, сети, реестра, MFT, техник и тактик противника. |

### Глоссарий
| Термин | Определение |
|---|---|
| **Абдукция (Пирс)** | Вывод к наилучшему объяснению; детерминированная генерация гипотез при аномальном сигнале. |
| **CAIE** | Контекстно-зависимое извлечение информации. |
| **Эпистемический вес** | Целочисленный показатель надёжности слоя доказательств. |
| **Криминалистический артефакт** | Сохранённая и маркированная единица цифрового доказательства. |
| **SignalOutput** | Необработанный цифровой след. |
| **Детерминированная целочисленная арифметика** | Вычисления только с целыми числами без ошибок округления. |

### 【Научное Примечание】
【Научное Примечание】Терминология Пирса, Эко и Грайса иногда ошибочно принимается за метафизическую спекуляцию. Это не так. Эти термины — операционные метки для детерминированных информационных процессов, аналогичных физическому датчику. Когда термометр регистрирует температуру, никто не видит в этом мистицизм; точно так же, когда данный модуль выполняет «абдукцию», он запускает детерминированную процедуру выбора гипотезы на основе слоёв доказательств с целочисленными весами. «Релевантность» (Грайс) и «интерпретация» (Эко) здесь реализованы как точные операции поиска и отображения. Аналогия с датчиком должна развеять любые представления об оккультных механизмах: адаптер считывает сигнал, применяет детерминированное преобразование и записывает структурированную запись. Не больше и не меньше.

---

## 中文

### 这是什么模块？
`vigia/core/forensic_adapter.py` 是一个中央翻译与适配枢纽。它将原始的数字取证信号（`SignalOutput`）转换为与 CAIE（上下文感知信息提取）框架以及 `AbductiveReasonerV2` 引擎兼容的结构化对象。可将其比作实验室中的样本制备仪：从磁盘、内存或网络流量中采集未经处理的痕迹，随后对其进行标记、分层和编目，归入具有确定性整数权重的证据层。系统不使用概率近似；每一次分类均依赖精确的整数运算。

### 核心概念

#### 主要类
| 类 | 科学角色 |
|---|---|
| `ForensicContext` | 调查环境容器；保存确定性参数，使所有取证工件在相同约束下被解释。 |
| `ForensicAdapter` | 中央转换器。通过精确整数映射将原始 `SignalOutput` 路由至 CAIE 取证工件与溯因记录。 |
| `SignalOutput` | 处理前的原始数字痕迹（如内存转储片段、注册表配置单元、数据包捕获）。 |
| `CAIEArtifact` | 面向 CAIE 管道的结构化输出对象；字段经类型化并以整数常量加权。 |
| `EvidenceLayer` | 证据金字塔的一个层级（磁盘、内存、网络）。每一层携带整数认识论权重。 |
| `OntologicalLevel` | 通过离散本体映射声明取证工件的类别（文件、进程、用户账户）。 |
| `ArtifactRecord` | 不可变台账条目，将原始信号与其经解释、带时间戳的事实绑定。 |
| `CausalLink` | 两条记录之间的确定性关系，以整数关系码与精确时间戳编码。 |

#### 适配器函数
| 函数 | 操作 |
|---|---|
| `signal_to_caie_artifact()` | 查询 `_LAYER_MAP` 与 `_EVIDENCE_MAP`，将一个 `SignalOutput` 转换为 `CAIEArtifact`。 |
| `signal_to_abductive_record()` | 从信号生成溯因假设；仅使用整数分值对候选假设进行排序。 |
| `signal_to_causal_link()` | 推导两个取证工件之间的因果边；依赖精确整数 ID 与确定性排序。 |
| `build_context()` | 依据配置常量实例化 `ForensicContext`，建立确定性注册表。 |

#### 配置常量
| 常量 | 用途 |
|---|---|
| `_LAYER_MAP` | 内部查找表，将信号来源映射至离散的整数层标识符。 |
| `_EVIDENCE_MAP` | 将证据类型映射至确定性整数类别的查找表。 |
| `_ONTOLOGY_MAP` | 使用精确整数键将信号映射至本体类别的查找表。 |
| `LAYER_EPISTEMIC_WEIGHT` | 指定某证据层证据强度的整数常量。 |
| `MEMORY` | 易失性内存证据的整数令牌。 |
| `NETWORK` | 网络流量证据的整数令牌。 |
| `REGISTRY` | 操作系统注册表证据的整数令牌。 |
| `DISK_MFT` | 主文件表（MFT）证据的整数令牌。 |
| `TECHNIQUE` | 对手技术分类的整数令牌。 |
| `TACTIC` | 对手战术分类的整数令牌。 |

### 术语表
| 术语 | 定义 |
|---|---|
| **溯因（皮尔斯）** | 最佳解释推理；系统在检测到异常信号时，依据确定性规则生成最可能的假设。 |
| **CAIE** | 上下文感知信息提取（Context-Aware Information Extraction）。 |
| **认识论权重 (Epistemic Weight)** | 表示证据层可靠性或重要性的整数值。 |
| **取证工件** | 经过保存与标记的数字证据单元。 |
| **原始信号 (SignalOutput)** | 解释前的未处理数字痕迹。 |
| **确定性整数运算** | 仅使用整数的计算，确保结果可复现，杜绝舍入误差。 |
| **逻辑断裂** | 信号与假设之间的逻辑缺口；溯因推理通过确定性规则填补此断裂。 |

### 【科学说明】
【科学说明】皮尔斯、艾柯与格赖斯的术语有时被误认为玄学思辨。事实并非如此。这些术语是对确定性信息过程的操作性标记，其性质类似于物理传感器。当温度计记录温度时，无人将其视为神秘主义；同理，当本模块执行"溯因"时，它是在整数加权证据层上执行一种确定性的假设选择例程。格赖斯的"相关性"与艾柯的"诠释"在此处被实现为精确的查找与映射操作。所谓"逻辑断裂"不过是信号输入与结构化输出之间有待映射的区间，由确定性整数运算填补。传感器类比足以消除任何关于隐秘机制的错觉：适配器读取信号，施加确定性变换，写入结构化记录。仅此而已，不多不少。

---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
