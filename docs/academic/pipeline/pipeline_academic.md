<!--
VIGIA Academic Documentation
Module: efe5a51e
Batch ID: vigia-doc-0111-efe5a51e
Generated: 2026-05-20T14:56:47.868566+00:00
-->

# Module Documentation: `vigia/pipeline/pipeline.py`

---

## ENGLISH

### What Is This Module?

The file `vigia/pipeline/pipeline.py` is the central control room of the VIGÍA Forensic Suite. Imagine a physical crime laboratory where evidence arrives from different instruments (DNA sequencers, spectrometers, cameras). This module acts as the laboratory chief that routes every item through five separate, sealed rooms. Each room performs one specific transformation: (0) data validation, (1) signal ingestion, (2) statistical inference, (3) risk governance, and (4) audit and sealing. Nothing moves backward; every hand-off is logged. The final product is a sealed forensic bundle—a digitally signed container that can be independently verified. The system uses deterministic integer arithmetic for hashes, counts, and verification codes, ensuring that two scientists running the same evidence obtain identical integrity tokens.

### Key Concepts

#### Table 1: The Five Compartmentalized Layers

| Layer | Name | Function | Deterministic Guarantees |
|---|---|---|---|
| 0 | Data Contracts (`models/ebs_v1.py`) | Validates shape and type of incoming evidence | Immutable schema; integer field counters |
| 1 | External Signals | Ingests output from forensic tools (SDA, CLI, GCI) | Normalized dictionaries; no interpretation yet |
| 2 | Inference Engine (`engine/`) | Multivariate analysis using KDE and Ledoit-Wolf shrinkage | Bootstrap B=500 (integer replication count); deterministic seeding |
| 3 | Governance (`governance/`) | Risk-bounded decision layer | Deterministic integer formula: r = (1−P)·(1+λD)·(1+γ(1−S)) computed on rational inputs |
| 4 | Audit & Action (`audit/` + `action/`) | Differential audit, optimization, and sealing | Cryptographic file hashes; deterministic transport verification |

#### Table 2: Public Interface (Simplified)

| Method / Function | Purpose | Scientist's View |
|---|---|---|
| `VigiaPipeline.run()` | Runs full pipeline, returns sealed bundle | "Press start; receive sealed case file." |
| `run_vigia()` | Simplified entry point for automated assistants | Remote trigger that preserves chain of custody |
| `main()` | Command-line interface | Type `vigia --signals evidence.json` in a terminal |
| `fit_evidence_graph()` | Calibrates evidence graph on baseline data | Training the instrument on known standards |
| `generate_narrative()` | Converts bundle to human-readable report | Automatic lab report generation |
| `verify_bundle_external()` | Independent verification via subprocess | Sending duplicate to a second lab for confirmation |
| `save_bundle()` / `load_and_verify()` | Persistence and retrieval with hash check | Storing evidence box and checking seal upon reopening |

#### Table 3: Semiotic Operators in the Pipeline

| Term | Role in Pipeline | Sensor Analogy |
|---|---|---|
| Firstness | Raw signal potential (uninterpreted voltage) | Thermistor resistance before conversion |
| Secondness | Hard collision between signal and threshold (fact/brute existence) | Comparator output: "temperature exceeded 37 °C" |
| Thirdness | Mediated interpretation via shared codes and protocols | Doctor reads "fever" because both parties use the same medical coding standard (Eco) and assume honest transmission (Grice) |

### Glossary

- **Zero-Trust Architecture (Capas Estancas)**: A design where no layer trusts data from another; each compartment re-validates inputs as if they came from an adversary.
- **ForensicBundle**: A sealed, tamper-evident container holding evidence, inference results, and audit logs.
- **Bootstrap Stability Selection (B = 500)**: A resampling procedure repeated exactly 500 times (an integer count) to measure how consistently variables associate with one another.
- **KDE (Kernel Density Estimation)**: A non-parametric method to estimate the probability distribution of a dataset without assuming a specific equation.
- **Ledoit-Wolf Shrinkage**: A covariance estimation technique that improves numerical stability when many variables are measured simultaneously.
- **Deterministic Integer Arithmetic**: Calculations performed with whole numbers and exact fractions (hashes, counts, replication indices) rather than approximations, ensuring reproducible verification tokens.
- **EvidenceGraph**: A network model linking pieces of evidence; its edges are validated by bootstrap replication.
- **Risk-Bounded Layer**: Governance module that computes an upper bound on decision risk using deterministic rational formulas.
- **SIFT**: An independent verifier that consumes the bundle as an external auditor would.
- **Peircean Categories**: Firstness (possibility/quality), Secondness (fact/relation), Thirdness (law/mediation). Used here as formal epistemological layers, not metaphysical speculation.

### 【Scientific Note】

The terminology of Peirce, Eco, and Grice is frequently mistaken for literary mysticism or philosophical speculation. It is not. These terms describe formal layers of information transmission, perfectly analogous to a physical sensor array. Consider a laboratory thermometer: **Firstness** is the raw voltage across the thermistor—a quality without interpretation. **Secondness** is the brute fact that the voltage crossed a comparator threshold; something *happened*. **Thirdness** is the entire mediating framework: the calibration curve (a shared **code**, in Eco's sense) and the expectation that the device reports truthfully and relevantly (Grice's cooperative maxims). When VIGÍA's documentation speaks of "Secondness + Thirdness," it is referring to the transition from raw signal detection to validated, communicable forensic knowledge. The module treats these as deterministic processing strata, not as esoteric concepts.

---

## ESPAÑOL

### ¿Qué es este módulo?

El archivo `vigia/pipeline/pipeline.py` es la sala de control central de la Forensic Suite VIGÍA. Imagínese un laboratorio forense físico donde la evidencia llega desde distintos instrumentos (secuenciadores de ADN, espectrómetros, cámaras). Este módulo actúa como el jefe de laboratorio que encamina cada elemento por cinco salas selladas e independientes. Cada sala realiza una transformación específica: (0) validación de datos, (1) ingestión de señales, (2) inferencia estadística, (3) gobernanza del riesgo y (4) auditoría y sellado. Nada fluye hacia atrás; cada transferencia queda registrada. El producto final es un paquete forense sellado —un contenedor firmado digitalmente que puede verificarse de manera independiente. El sistema emplea aritmética determinista de enteros para hashes, conteos y códigos de verificación, garantizando que dos científicos que procesen la misma evidencia obtengan tokens de integridad idénticos.

### Conceptos clave

#### Tabla 1: Las Cinco Capas Estancas

| Capa | Nombre | Función | Garantías deterministas |
|---|---|---|---|
| 0 | Contratos de datos (`models/ebs_v1.py`) | Valida la forma y tipo de la evidencia entrante | Esquema inmutable; contadores enteros de campos |
| 1 | Señales externas | Ingesta la salida de herramientas forenses (SDA, CLI, GCI) | Diccionarios normalizados; sin interpretación aún |
| 2 | Motor de inferencia (`engine/`) | Análisis multivariante con KDE y contracción Ledoit-Wolf | Bootstrap B=500 (conteo entero de replicaciones); semilla determinista |
| 3 | Gobernanza (`governance/`) | Capa de decisión de riesgo acotado | Fórmula entera determinista: r = (1−P)·(1+λD)·(1+γ(1−S)) sobre entradas racionales |
| 4 | Auditoría y Acción (`audit/` + `action/`) | Auditoría diferencial, optimización y sellado | Hashes criptográficos de archivos; verificación determinista de transporte |

#### Tabla 2: Interfaz pública (simplificada)

| Método / Función | Propósito | Vista del científico |
|---|---|---|
| `VigiaPipeline.run()` | Ejecuta el pipeline completo, devuelve paquete sellado | "Presione inicio; reciba expediente sellado." |
| `run_vigia()` | Punto de entrada simplificado para asistentes automáticos | Disparador remoto que preserva la cadena de custodia |
| `main()` | Interfaz de línea de comandos | Escriba `vigia --signals evidence.json` en una terminal |
| `fit_evidence_graph()` | Calibra el grafo de evidencia sobre datos de referencia | Entrenar el instrumento con estándares conocidos |
| `generate_narrative()` | Convierte el paquete en informe legible | Generación automática de informe de laboratorio |
| `verify_bundle_external()` | Verificación independiente mediante subproceso | Enviar duplicado a segundo laboratorio para confirmación |
| `save_bundle()` / `load_and_verify()` | Persistencia y recuperación con verificación de hash | Almacenar caja de evidencia y comprobar el sello al reabrir |

#### Tabla 3: Operadores semióticos en el pipeline

| Término | Rol en el pipeline | Analogía con sensor |
|---|---|---|
| Primeridad | Potencial de señal bruta (voltaje sin interpretar) | Resistencia del termistor antes de la conversión |
| Segundidad | Colisión dura entre señal y umbral (hecho/existencia bruta) | Salida del comparador: "temperatura superó 37 °C" |
| Terceridad | Interpretación mediada a través de códigos y protocolos compartidos | El médico lee "fiebre" porque ambas partes usan el mismo estándar de codificación médica (Eco) y asumen transmisión honesta (Grice) |

### Glosario

- **Arquitectura de Cero Confianza (Capas Estancas)**: Diseño en el que ninguna capa confía en los datos de otra; cada compartimento re-valida las entradas como si provinieran de un adversario.
- **Paquete Forense (ForensicBundle)**: Contenedor sellado y con evidencia de manipulación que aloja la evidencia, resultados de inferencia y bitácoras de auditoría.
- **Selección de Estabilidad Bootstrap (B = 500)**: Procedimiento de remuestreo repetido exactamente 500 veces (un conteo entero) para medir la consistencia de las asociaciones entre variables.
- **KDE (Estimación de Densidad por Núcleos)**: Método no paramétrico para estimar la distribución de probabilidad de un conjunto de datos sin asumir una ecuación específica.
- **Encogimiento Ledoit-Wolf**: Técnica de estimación de covarianza que mejora la estabilidad numérica cuando se miden muchas variables simultáneamente.
- **Aritmética Entera Determinista**: Cálculos realizados con números enteros y fracciones exactas (hashes, conteos, índices de replicación) en lugar de aproximaciones, asegurando tokens de verificación reproducibles.
- **Grafo de Evidencia (EvidenceGraph)**: Modelo de red que vincula piezas de evidencia; sus aristas se validan mediante replicación bootstrap.
- **Capa de Riesgo Acotado**: Módulo de gobernanza que computa una cota superior del riesgo de decisión mediante fórmulas racionales deterministas.
- **SIFT**: Verificador independiente que consume el paquete como lo haría un auditor externo.
- **Categorías Peirceanianas**: Primeridad (posibilidad/cualidad), Segundidad (hecho/relación), Terceridad (ley/mediación). Usadas aquí como capas epistemológicas formales, no como especulación metafísica.

### 【Nota Científica】

La terminología de Peirce, Eco y Grice es frecuentemente confundida con mística literaria o especulación filosófica. No lo es. Estos términos describen capas formales de transmisión de información, perfectamente análogas a un conjunto de sensores físicos. Considere un termómetro de laboratorio: la **Primeridad** es el voltaje crudo en el termistor —una cualidad sin interpretación. La **Segundidad** es el hecho bruto de que el voltaje cruzó un umbral del comparador; *algo ocurrió*. La **Terceridad** es el marco mediador completo: la curva de calibración (un **código** compartido, en el sentido de Eco) y la expectativa de que el dispositivo reporte con veracidad y relevancia (los máximas cooperativas de Grice). Cuando la documentación de VIGÍA habla de "Segundidad + Terceridad", se refiere a la transición desde la detección de señal bruta hasta el conocimiento forense validado y comunicable. El módulo trata estos estratos como capas de procesamiento deterministas, no como conceptos esotéricos.

---

## РУССКИЙ

### Что представляет собой этот модуль?

Файл `vigia/pipeline/pipeline.py` — это центральный пункт управления судебно-медицинского комплекса VIGÍA. Представьте себе физическую криминалистическую лабораторию, куда улики поступают из различных приборов (секвенаторы ДНК, спектрометры, камеры). Этот модуль действует как заведующий лабораторией, направляющий каждый предмет через пять изолированных, герметичных помещений. Каждое помещение выполняет одно конкретное преобразование: (0) валидация данных, (1) приём сигналов, (2) статистический вывод, (3) управление рисками и (4) аудит и опечатывание. Ничто не движется вспять; каждая передача регистрируется. Конечный продукт — опечатанный судебный пакет (ForensicBundle): цифровой контейнер с подписью, пригодный для независимой проверки. Система использует детерминированную целочисленную арифметику для хешей, подсчётов и проверочных кодов, гарантируя, что два учёных, обработавших одни и те же улики, получат идентичные токены целостности.

### Ключевые понятия

#### Таблица 1: Пять герметичных уровней

| Уровень | Название | Функция | Детерминированные гарантии |
|---|---|---|---|
| 0 | Контракты данных (`models/ebs_v1.py`) | Валидирует структуру и тип поступающих улик | Неизменяемая схема; целочисленные счётчики полей |
| 1 | Внешние сигналы | Принимает вывод криминалистических инструментов (SDA, CLI, GCI) | Нормализованные словари; интерпретация пока отсутствует |
| 2 | Движок вывода (`engine/`) | Многомерный анализ с KDE и сжатием Ледуа-Вольфа | Бутстреп B=500 (целое число повторений); детерминированное начальное значение |
| 3 | Управление (`governance/`) | Уровень принятия решений с ограниченным риском | Детерминированная целочисленная формула: r = (1−P)·(1+λD)·(1+γ(1−S)) на рациональных входах |
| 4 | Аудит и действие (`audit/` + `action/`) | Дифференциальный аудит, оптимизация и опечатывание | Криптографические хеши файлов; детерминированная проверка транспорта |

#### Таблица 2: Публичный интерфейс (упрощённо)

| Метод / Функция | Назначение | Взгляд учёного |
|---|---|---|
| `VigiaPipeline.run()` | Запускает весь конвейер, возвращает опечатанный пакет | «Нажмите запуск; получите запечатанное дело.» |
| `run_vigia()` | Упрощённая точка входа для автоматизированных ассистентов | Удалённый триггер, сохраняющий цепочку хранения |
| `main()` | Интерфейс командной строки | Введите `vigia --signals evidence.json` в терминале |
| `fit_evidence_graph()` | Калибрует граф улик на базовых данных | Обучение инструмента на известных стандартах |
| `generate_narrative()` | Конвертирует пакет в читаемый отчёт | Автоматическое формирование лабораторного отчёта |
| `verify_bundle_external()` | Независимая проверка через дочерний процесс | Отправка дубликата в другую лабораторию для подтверждения |
| `save_bundle()` / `load_and_verify()` | Хранение и извлечение с проверкой хеша | Хранить ящик с уликами и проверять печать при повторном открытии |

#### Таблица 3: Семиотические операторы в конвейере

| Термин | Роль в конвейере | Аналогия с датчиком |
|---|---|---|
| Первичность | Потенциал сырого сигнала (ненинтерпретированное напряжение) | Сопротивление термистора до преобразования |
| Вторичность | Жёсткое столкновение сигнала и порога (факт/брутальное существование) | Выход компаратора: «температура превысила 37 °C» |
| Третичность | Опосредованная интерпретация через общие коды и протоколы | Врач читает «лихорадку», потому что обе стороны используют один и тот же медицинский стандарт кодирования (Эко) и предполагают честную передачу (Грайс) |

### Глоссарий

- **Архитектура «Нулевого доверия» (Capas Estancas)**: Конструкция, в которой ни один уровень не доверяет данным от другого; каждый отсек повторно проверяет входные данные, как если бы они поступили от противника.
- **Судебный пакет (ForensicBundle)**: Опечатанный контейнер с индикатором вскрытия, содержащий улики, результаты вывода и журналы аудита.
- **Отбор устойчивости бутстрепом (B = 500)**: Процедура повторного выборочного исследования, проведённая ровно 500 раз (целое число повторений), для измерения согласованности связей между переменными.
- **KDE (Оценка плотности ядра)**: Непараметрический метод оценки вероятностного распределения данных без предположения о конкретном уравнении.
- **Сжатие Ледуа-Вольфа**: Метод оценки ковариации, повышающий численную устойчивость при одновременном измерении множества переменных.
- **Детерминированная целочисленная арифметика**: Вычисления с целыми числами и точными дробями (хеши, счётчики, индексы репликации), а не приближениями, обеспечивающие воспроизводимые проверочные токены.
- **Граф улик (EvidenceGraph)**: Сетевая модель, связывающая фрагменты улик; её рёбра подтверждаются бутстреп-репликацией.
- **Уровень ограниченного риска**: Модуль управления, вычисляющий верхнюю границу риска решения с помощью детерминированных рациональных формул.
- **SIFT**: Независимый верификатор, потребляющий пакет так, как это сделал бы внешний аудитор.
- **Пирсовские категории**: Первичность (возможность/качество), Вторичность (факт/отношение), Третичность (закон/посредничество). Используются здесь как формальные эпистемологические уровни, а не метафизическая спекуляция.

### 【Научное примечание】

Терминология Пирса, Эко и Грайса часто ошибочно принимается за литературный мистицизм или философскую спекуляцию. Это не так. Эти термины описывают формальные уровни передачи информации, вполне аналогичные физическому массиву датчиков. Рассмотрим лабораторный термометр: **Первичность** — это необработанное напряжение на термисторе, качество без интерпретации. **Вторичность** — это неумолимый факт пересечения напряжением порога компаратора; *что-то произошло*. **Третичность** — вся посредническая структура: калибровочная кривая (общий **код**, в смысле Эко) и ожидание того, что прибор сообщает правдиво и по существу (кооперативные максимы Грайса). Когда в документации VIGÍA говорится о «Вторичность + Третичность», имеется в виду переход от обнаружения сырого сигнала к проверенным, коммуникабельным судебным знаниям. Модуль рассматривает эти уровни как детерминированные страты обработки, а не как эзотерические концепции.

---

## 中文

### 这是什么模块？

文件 `vigia/pipeline/pipeline.py` 是 VIGÍA 取证套件的中枢控制室。请想象一间实体物证实验室：DNA 测序仪、光谱仪、摄像机等仪器不断送来证据材料。本模块就像实验室主任，把每一份材料依次送入五间相互隔离的密封房间。每间房只负责一种转化：(0) 数据契约验证，(1) 信号摄取，(2) 统计推断，(3) 风险治理，(4) 审计与封存。数据绝不回流；每一次交接都被记录。最终产物是一个密封的**取证工件**（ForensicBundle）——一份经过数字签名的容器，可被独立核验。系统对哈希值、计数与验证码采用**确定性整数运算**，确保两位科学家处理同一份证据时，能够得到完全一致的完整性令牌。

### 关键概念

#### 表 1：五层隔离架构（零信任）

| 层级 | 名称 | 功能 | 确定性保障 |
|---|---|---|---|
| 0 | 数据契约 (`models/ebs_v1.py`) | 验证输入证据的格式与类型 | 不可变模式；整数字段计数 |
| 1 | 外部信号 | 摄取取证工具（SDA/CLI/GCI 等）的输出 | 规范化字典；尚未解释 |
| 2 | 推断引擎 (`engine/`) | 基于 KDE 与 Ledoit-Wolf 收缩的多变量分析 | 自助法 B=500（整数复制次数）；确定性种子 |
| 3 | 治理层 (`governance/`) | 风险有界决策 | 确定性整数公式 r = (1−P)·(1+λD)·(1+γ(1−S)) 在有理数输入上计算 |
| 4 | 审计与行动 (`audit/` + `action/`) | 差异审计、优化与封存 | 加密文件哈希；确定性传输核验 |

#### 表 2：公共接口（简化）

| 方法 / 函数 | 用途 | 科学家视角 |
|---|---|---|
| `VigiaPipeline.run()` | 运行完整流水线，返回密封取证工件 | "按下启动；接收密封案卷。" |
| `run_vigia()` | 供自动化助手使用的简化入口 | 远程触发，同时保全监管链 |
| `main()` | 命令行界面 | 在终端输入 `vigia --signals evidence.json` |
| `fit_evidence_graph()` | 在基线数据集上校准证据图 | 使用已知标准"训练仪器" |
| `generate_narrative()` | 将取证工件转换为人可读报告 | 自动生成实验报告 |
| `verify_bundle_external()` | 通过子进程进行独立验证 | 将副本送往第二实验室复核 |
| `save_bundle()` / `load_and_verify()` | 带哈希检查的持久化与检索 | 存放证物箱并在重新开启时检查封条 |

#### 表 3：流水线中的符号学算子

| 术语 | 在流水线中的角色 | 传感器类比 |
|---|---|---|
| 第一性 | 原始信号潜能（未解释电压） | 热敏电阻在转换前的电阻值 |
| 第二性 | 信号与阈值的硬性碰撞（事实/蛮在） | 比较器输出："温度超过 37 °C" |
| 第三性 | 通过共享代码与协议的中介解释 | 医生能读出"发烧"，因为双方使用同一医学编码标准（艾柯）并假定诚实传输（格赖斯） |

### 术语表

- **零信任架构（隔离层）**：任何层级都不信任其他层级的数据；每个隔间都像面对对手一样重新验证输入。
- **取证工件（ForensicBundle）**：密封的防篡改容器，内含证据、推断结果与审计日志。
- **自助法稳定性选择（B = 500）**：精确重复 500 次（整数次数）的重采样程序，用于度量变量间关联的稳健性。
- **KDE（核密度估计）**：不预设特定方程式的非参数概率分布估计方法。
- **Ledoit-Wolf 收缩**：在同时测量多变量时提升数值稳定性的协方差估计技术。
- **确定性整数运算**：使用整数与精确分数（哈希、计数、复制索引）而非近似值的计算，确保核验令牌可复现。
- **证据图（EvidenceGraph）**：连接各证据片段的网络模型；其边经自助复制验证。
- **风险有界层**：治理模块，利用确定性有理公式计算决策风险上界。
- **SIFT**：独立验证器，以外部审计员方式消费取证工件。
- **皮尔斯范畴**：第一性（可能/质性）、第二性（事实/关系）、第三性（法则/中介）。此处作为形式认识论层级使用，而非形而上学臆测。
- **逻辑断裂**：系统中需要中介解释的不连续点，第三性通过共享代码弥合之。

### 【科学说明】

皮尔斯、艾柯与格赖斯的术语常被误认为文学神秘主义或哲学玄思。事实并非如此。这些术语描述的是信息传输的形式层级，与物理传感器阵列完全类比。以实验室温度计为例：**第一性** 是热敏电阻两端的原始电压——一种尚未被解释的质性。**第二性** 是电压越过比较器阈值的蛮荒事实；*某件事发生了*。**第三性** 则是完整的中介框架：校准曲线（在艾柯意义上即共享的**代码**）以及设备会真实且相关地报告的预设（格赖斯的合作原则）。当 VIGÍA 文档提到"第二性 + 第三性"时，指的是从原始信号检测到经过验证、可传播的取证知识的跃迁。本模块将这些层级视为确定性的处理地层，而非玄学概念。

---

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
