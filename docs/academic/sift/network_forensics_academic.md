<!--
VIGIA Academic Documentation
Module: b9ce7db8
Batch ID: vigia-doc-0137-b9ce7db8
Generated: 2026-05-20T14:56:47.874055+00:00
-->

### ENGLISH

**What Is This Module?**
`vigia/sift/network_forensics.py` is the signal-processing core of a network forensics suite. It treats network traffic not merely as raw data, but as sequences of discrete signs. The module ingests flows—chronologically ordered records of communication between two endpoints—and subjects them to deterministic, integer-based analysis. Its purpose is to reveal hidden regularities (beaconing), sudden data hemorrhages (exfiltration), and structured burst patterns that traditional volume-only thresholds miss. Because every internal ratio is represented as an exact rational number (Fraction), the results are reproducible across hardware and execution order, satisfying the evidentiary standards of scientific and legal review.

**Key Concepts**

Table 1: Core Classes
| Class | Scientific Role |
|-------|-----------------|
| `NetworkFlow` | A container for a single bidirectional communication sequence, analogous to a physical sample in an experiment. |
| `NetworkAnalysisResult` | The structured output (a forensic artifact) containing diagnoses, confidence metrics, and temporal markers. |
| `NetworkForensicsEngine` | The deterministic processor that applies semiotic and statistical tests to the flow sample. |

Table 2: Key Functions
| Function | Scientific Role |
|----------|-----------------|
| `to_signal()` | Converts raw packet timings and sizes into a discrete symbolic sequence (the "sensor reading"). |
| `analyze()` | Executes the full analytical pipeline: jitter-resilient beacon detection, burst-aware exfiltration detection, and rational-metric synthesis. |

Table 3: Security Hardening (Tanda Seguridad P0)
| Fix | Mechanism | Scientific Rationale |
|-----|-----------|----------------------|
| Anti-Jitter Beaconing | Entropy analysis of intervals + Mann-Kendall trend test + adaptive CV threshold | Interval entropy does not scale linearly with injected jitter; a monotonic trend remains detectable via non-parametric statistics. |
| Exfiltration Detection | Burst-pattern analysis alongside aggregate volume | Total volume can be deceptive; burst autocorrelation reveals systematic data removal. |
| Fraction Purity | All ratios stored as `Fraction` (exact rational arithmetic) | Eliminates round-off non-determinism; guarantees bitwise-identical results on every replay. |

Table 4: Configuration
| Constant | Purpose |
|----------|---------|
| `TOOL_NAME` | Identifies the provenance of the forensic artifact in multi-tool chains. |

**Glossary**
- **Beaconing**: Rhythmic, low-entropy communication typically indicating command-and-control (C2) channel health checks.
- **Burst Pattern**: A transient elevation in packet rate or size, distinct from baseline noise, often signaling automated exfiltration.
- **Coefficient of Variation (CV)**: The ratio of standard deviation to mean, expressed here as an exact fraction to compare relative dispersion across samples of differing sizes.
- **Deterministic Integer Arithmetic**: Calculation performed exclusively with exact rational numbers (pairs of integers: numerator and denominator), guaranteeing bit-identical reproduction on every execution.
- **Exfiltration**: Unauthorized transmission of data from a protected network to an external destination.
- **Flow**: A unidirectional or bidirectional sequence of packets sharing source, destination, and protocol attributes within a time window.
- **Fraction (Rational Number)**: A number represented as p/q where p and q are integers; operations are closed under addition, multiplication, and division (q≠0), yielding no rounding error.
- **Jitter**: Intentional or noise-induced variance in packet inter-arrival times, often used by attackers to mask periodicity.
- **Mann-Kendall Test**: A non-parametric statistical test for monotonic trends in time-ordered data; robust to outliers and distributional assumptions.
- **Network Forensics**: The scientific examination of network events to reconstruct incidents and establish evidentiary chains.
- **Semiotic Signal**: In this context, the transformation of network events into interpretable signs governed by syntax (Peirce), coding (Eco), and cooperative maxims (Grice).

**【Scientific Note】**
The module occasionally employs concepts drawn from semiotics—Peirce's theory of signs, Eco's cultural/technical codes, and Grice's conversational maxims. This is not mysticism or literary criticism deployed in a technical vacuum. Think of these terms as the *metadata schema* of a very specialized sensor. When a thermometer converts molecular kinetic energy into a temperature reading, it relies on a physical model. When `network_forensics.py` converts packet timings into a "beaconing index," it relies on a semiotic model: Peirce provides the syntax (icon, index, symbol), Eco provides the codebook (what a given pattern means inside a specific protocol culture), and Grice provides the pragmatic filter (why a pattern that violates expected cooperation is suspicious). The terminology is formal epistemology, not mysticism; it is the interpretive layer that makes the raw signal intelligible to an investigator.

---

### ESPAÑOL

**¿Qué es este módulo?**
`vigia/sift/network_forensics.py` constituye el núcleo de procesamiento de señales de una suite forense de red. Trata el tráfico de red no como mero ruido digital, sino como secuencias de signos discretos. El módulo ingiere flujos—registros ordenados cronológicamente de comunicación entre dos extremos—y los somete a análisis determinista basado en enteros. Su propósito es revelar regularidades ocultas (beaconing), hemorragias súbitas de datos (exfiltración) y patrones de ráfaga estructurados que los umbrales tradicionales de volumen pasan por alto. Dado que toda razón interna se representa como número racional exacto (`Fraction`), los resultados son reproducibles en cualquier hardware y orden de ejecución, satisfaciendo los estándares probatorios de la revisión científica y legal.

**Conceptos Clave**

Tabla 1: Clases principales
| Clase | Rol Científico |
|-------|----------------|
| `NetworkFlow` | Contenedor de una secuencia de comunicación bidireccional; análogo a una muestra física en un experimento. |
| `NetworkAnalysisResult` | Salida estructurada (artefacto forense) que contiene diagnósticos, métricas de confianza y marcadores temporales. |
| `NetworkForensicsEngine` | Procesador determinista que aplica pruebas semióticas y estadísticas a la muestra de flujo. |

Tabla 2: Funciones principales
| Función | Rol Científico |
|---------|----------------|
| `to_signal()` | Convierte tiempos y tamaños de paquetes brutos en una secuencia simbólica discreta (la "lectura del sensor"). |
| `analyze()` | Ejecuta el pipeline analítico completo: detección de beaconing resistente a jitter, detección de exfiltración consciente de ráfagas y síntesis de métricas racionales. |

Tabla 3: Endurecimiento de seguridad (Tanda Seguridad P0)
| Corrección | Mecanismo | Fundamento Científico |
|------------|-----------|----------------------|
| Anti-Jitter (Beaconing) | Análisis de entropía de intervalos + prueba de tendencia de Mann-Kendall + umbral adaptativo de CV | La entropía de intervalos no escala linealmente con el jitter inyectado; la tendencia monotónica sigue siendo detectable mediante estadística no paramétrica. |
| Detección de Exfiltración | Análisis de patrones de ráfaga además del volumen agregado | El volumen total puede ser engañoso; la autocorrelación de ráfagas revela extracción sistemática de datos. |
| Pureza de Fracciones | Todas las razones se almacenan como `Fraction` (aritmética racional exacta) | Elimina el no-determinismo por redondeo; garantiza resultados idénticos bit a bit en cada repetición. |

Tabla 4: Configuración
| Constante | Propósito |
|-----------|-----------|
| `TOOL_NAME` | Identifica la procedencia del artefacto forense en cadenas multi-herramienta. |

**Glosario**
- **Beaconing**: Comunicación rítmica de baja entropía que típicamente indica controles de salud de un canal de comando y control (C2).
- **Coeficiente de Variación (CV)**: Razón entre desviación estándar y media, expresada aquí como fracción exacta para comparar dispersión relativa entre muestras de distinto tamaño.
- **Determinismo Aritmético Entero**: Cálculo exclusivamente con números racionales exactos (pares de enteros: numerador y denominador), garantizando reproducción idéntica bit a bit en cada ejecución.
- **Exfiltración**: Transmisión no autorizada de datos desde una red protegida hacia un destino externo.
- **Flujo (Flow)**: Secuencia unidireccional o bidireccional de paquetes que comparten origen, destino y atributos de protocolo dentro de una ventana temporal.
- **Fracción (Número Racional)**: Número representado como p/q donde p y q son enteros; las operaciones son cerradas bajo adición, multiplicación y división (q≠0), sin error de redondeo.
- **Jitter**: Variación intencional o por ruido en los tiempos de inter-llegada de paquetes, frecuentemente usada por atacantes para enmascarar periodicidad.
- **Patrón de Ráfaga (Burst)**: Elevación transitoria en la tasa o tamaño de paquetes, distinta del ruido basal, que a menudo señala exfiltración automatizada.
- **Prueba de Mann-Kendall**: Prueba estadística no paramétrica para tendencias monotónicas en datos ordenados temporalmente; robusta ante valores atípicos.
- **Forense de Red**: Examen científico de eventos de red para reconstruir incidentes y establecer cadenas probatorias.
- **Señal Semiótica**: En este contexto, la transformación de eventos de red en signos interpretables gobernados por sintaxis (Peirce), códigos (Eco) y máximas cooperativas (Grice).

**【Nota Científica】**
Este módulo emplea ocasionalmente conceptos de la semiótica: la teoría de los signos de Peirce, los códigos técnicos/culturales de Eco y las máximas conversacionales de Grice. Esto no es misticismo ni crítica literaria aplicada en un vacío técnico. Piense en estos términos como el *esquema de metadatos* de un sensor muy especializado. Cuando un termómetro convierte la energía cinética molecular en una lectura de temperatura, se apoya en un modelo físico. Cuando `network_forensics.py` convierte tiempos de paquete en un "índice de beaconing", se apoya en un modelo semiótico: Peirce proporciona la sintaxis (icono, índice, símbolo), Eco el código (qué significa un patrón dado dentro de una cultura de protocolo específica) y Grice el filtro pragmático (por qué un patrón que viola la cooperación esperada resulta sospechoso). La terminología es epistemología formal, no misticismo; es la capa interpretativa que hace inteligible la señal bruta para el investigador.

---

### РУССКИЙ

**Что это за модуль?**
`vigia/sift/network_forensics.py` — это ядро обработки сигналов комплекса сетевой криминалистики. Он рассматривает сетевой трафик не как сырой цифровой шум, а как последовательности дискретных знаков. Модуль принимает потоки — хронологически упорядоченные записи коммуникации между двумя конечными точками — и подвергает их детерминированному целочисленному анализу. Его цель — выявить скрытые регулярности (маяки/beaconing), внезапные утечки данных (эксфильтрация) и структурированные пакетные всплески, которые традиционные объёмные пороги упускают. Поскольку все внутренние отношения представлены точными рациональными числами (`Fraction`), результаты воспроизводимы на любом оборудовании и при любом порядке выполнения, что удовлетворяет стандартам доказательственной экспертизы в науке и праве.

**Ключевые понятия**

Таблица 1: Основные классы
| Класс | Научная роль |
|-------|--------------|
| `NetworkFlow` | Контейнер для одной двунаправленной коммуникационной последовательности; аналог физического образца в эксперименте. |
| `NetworkAnalysisResult` | Структурированный результат (криминалистический артефакт), содержащий диагнозы, метрики достоверности и временные маркеры. |
| `NetworkForensicsEngine` | Детерминированный процессор, применяющий семиотические и статистические тесты к образцу потока. |

Таблица 2: Ключевые функции
| Функция | Научная роль |
|---------|--------------|
| `to_signal()` | Преобразует исходные временные метки и размеры пакетов в дискретную символьную последовательность («показания датчика»). |
| `analyze()` | Выполняет полный аналитический конвейер: обнаружение маяков, устойчивое к джиттеру; обнаружение эксфильтрации с учётом пакетных всплесков; синтез рациональных метрик. |

Таблица 3: Усиление безопасности (Tanda Seguridad P0)
| Исправление | Механизм | Научное обоснование |
|-------------|----------|---------------------|
| Анти-джиттер (Beaconing) | Анализ энтропии интервалов + трендовый тест Манна-Кендалла + адаптивный порог CV | Энтропия интервалов не растёт линейно с внедряемым джиттером; монотонный тренд остаётся обнаружимым непараметрической статистикой. |
| Обнаружение эксфильтрации | Анализ паттернов всплесков наряду с суммарным объёмом | Общий объём может быть обманчив; автокорреляция всплесков выявляет систематическое изъятие данных. |
| Чистота Fraction | Все отношения хранятся как `Fraction` (точная рациональная арифметика) | Устраняет недетерминизм округления; гарантирует побитово идентичные результаты при каждом повторе. |

Таблица 4: Конфигурация
| Константа | Назначение |
|-----------|------------|
| `TOOL_NAME` | Идентифицирует происхождение криминалистического артефакта в многоинструментальных цепочках. |

**Глоссарий**
- **Beaconing (маячение)**: Ритмичная коммуникация с низкой энтропией, обычно указывающая на проверку работоспособности канала управления (C2).
- **Всплесковый паттерн (Burst)**: Кратковременное повышение интенсивности или размера пакетов, отличное от базового шума, часто сигнализирующее об автоматизированной эксфильтрации.
- **Джиттер**: Преднамеренный или шумовой разброс межпакетных интервалов, часто используемый злоумышленниками для маскировки периодичности.
- **Детерминированная целочисленная арифметика**: Вычисления исключительно с точными рациональными числами (числитель/знаменатель — целые), гарантирующие побитово идентичное воспроизведение при каждом запуске.
- **Коэффициент вариации (CV)**: Отношение стандартного отклонения к среднему, выраженное здесь точной дробью для сравнения относительного разброса в выборках разного объёма.
- **Эксфильтрация**: Несанкционированная передача данных из защищённой сети во внешний пункт назначения.
- **Поток (Flow)**: Одно- или двунаправленная последовательность пакетов с общими атрибутами источника, назначения и протокола внутри временного окна.
- **Fraction (рациональное число)**: Число в виде p/q, где p и q — целые; операции замкнуты относительно сложения, умножения и деления (q≠0), без ошибок округления.
- **Семиотический сигнал**: В данном контексте — преобразование сетевых событий в интерпретируемые знаки, регулируемые синтаксисом (Пирс), кодом (Эко) и кооперативными максимами (Грайс).
- **Тест Манна-Кендалла**: Непараметрический статистический тест на монотонные тренды во временных рядах; устойчив к выбросам и не требует предположений о распределении.
- **Сетевая криминалистика**: Научное исследование сетевых событий для реконструкции инцидентов и установления доказательственных цепочек.

**【Научное примечание】**
Модуль время от времени оперирует понятиями семиотики — теорией знаков Пирса, техническими/культурными кодами Эко и разговорными максимами Грайса. Это не мистицизм и не литературная критика, применённая в техническом вакууме. Воспринимайте эти термины как *схему метаданных* очень специализированного датчика. Когда термометр преобразует молекулярную кинетическую энергию в показание температуры, он опирается на физическую модель. Когда `network_forensics.py` преобразует межпакетные интервалы в «индекс маячения», он опирается на семиотическую модель: Пирс задаёт синтаксис (икона, индекс, символ), Эко — кодировку (что означает данный паттерн внутри конкретной протокольной культуры), а Грайс — прагматический фильтр (почему паттерн, нарушающий ожидаемое сотрудничество, вызывает подозрение). Терминология — это формальная эпистемология, а не мистицизм; это интерпретативный слой, который делает сырой сигнал понятным для исследователя.

---

### 中文

**本模块是什么？**
`vigia/sift/network_forensics.py` 是一个网络取证套件的信号处理核心。它将网络流量不仅视为原始数字噪声，更视为离散符号的序列。该模块摄取"流"（flow）——即两个端点间按时间顺序排列的通信记录——并对其进行基于整数的确定性分析。其目的在于揭示隐藏的规律（信标通信/beaconing）、突发性的数据外泄（exfiltration/数据渗出）以及传统仅按总量阈值所忽略的结构化突发模式。由于所有内部比率均以精确有理数（Fraction，分数）表示，结果在任何硬件与执行顺序下均可复现，满足科学与法律审查的证据标准。

**核心概念**

表1：核心类
| 类名 | 科学作用 |
|------|----------|
| `NetworkFlow` | 单个双向通信序列的容器；类似于实验中的物理样本。 |
| `NetworkAnalysisResult` | 结构化输出（取证工件），包含诊断结论、置信度指标与时间标记。 |
| `NetworkForensicsEngine` | 确定性处理器，对流量样本应用符号学与统计检验。 |

表2：关键函数
| 函数名 | 科学作用 |
|--------|----------|
| `to_signal()` | 将原始数据包时序与大小转换为离散符号序列（即"传感器读数"）。 |
| `analyze()` | 执行完整分析管线：抗抖动的信标检测、突发感知的数据外泄检测，以及有理数指标合成。 |

表3：安全加固（Tanda Seguridad P0）
| 修复项 | 机制 | 科学依据 |
|--------|------|----------|
| 抗抖动信标检测 | 间隔熵分析 + 曼-肯德尔趋势检验 + 自适应CV阈值 | 间隔熵不会随注入抖动线性上升；单调趋势仍可通过非参数统计检出。 |
| 数据外泄检测 | 在总体积之外增加突发模式分析 | 总体积可能具有欺骗性；突发自相关可揭示系统性的数据搬移。 |
| Fraction纯化 | 所有比率均以 `Fraction`（精确有理运算）存储 | 消除舍入导致的非确定性；保证每次重放结果在比特级别完全一致。 |

表4：配置常量
| 常量 | 用途 |
|------|------|
| `TOOL_NAME` | 在多工具链中标示取证工件的来源与谱系。 |

**术语表**
- **信标通信（Beaconing）**：低熵节律性通信，通常指示命令与控制（C2）信道的保活检测。
- **突发模式（Burst Pattern）**：数据包速率或大小的瞬时升高，区别于基线噪声，常暗示自动化数据外泄。
- **变异系数（CV）**：标准差与均值的比率，此处以精确分数表示，用于比较不同容量样本的相对离散程度。
- **确定性整数运算**：完全使用精确有理数（整数分子与分母构成的数对）进行计算，确保每次执行在比特级别完全一致。
- **数据外泄（Exfiltration）**：未经授权将数据从受保护网络传输至外部目的地。
- **流（Flow）**：在时间窗口内共享源地址、目的地址与协议属性的单向或双向数据包序列。
- **Fraction（分数/有理数）**：以 p/q 形式表示的数，其中 p 与 q 为整数；该运算系统在加、乘与精确除（q≠0）下封闭，不存在表示不确定性。
- **抖动（Jitter）**：数据包到达间隔时间的故意或噪声性变化，攻击者常借此掩盖周期性。
- **曼-肯德尔检验（Mann-Kendall Test）**：一种非参数统计检验，用于检测时序数据中的单调趋势；对异常值与分布假设具有鲁棒性。
- **网络取证**：对网络事件进行科学检验，以重建事件过程并建立证据链。
- **符号学信号（Semiotic Signal）**：在本语境中，指将网络事件转换为可解释符号的过程，其受句法（皮尔斯）、编码（艾柯）与合作原则（格赖斯）支配。
- **逻辑断裂**：在符号学模型中，指预期合作原则或协议规范被违反时出现的语义-语用层面的断裂，而非物理层面的裂缝。

**【科学说明】**
本模块偶尔会使用符号学概念——皮尔斯的符号理论、艾柯的技术/文化代码，以及格赖斯的会话准则。这并非在真空中套用神秘主义或文学批评。请将这些术语视为一种高度专业化传感器的*元数据模式*。当温度计将分子动能转换为温度读数时，它依赖的是物理模型；当 `network_forensics.py` 将数据包时序转换为"信标指数"时，它依赖的是符号学模型：皮尔斯提供句法（象似、标指、象征），艾柯提供代码本（某一特定协议文化中给定模式的意义），格赖斯提供语用过滤器（为何违反预期合作原则的模式是可疑的）。这套术语是形式认识论，而非神秘主义；它是使原始信号对调查人员变得可理解的解释层。

---

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
