<!--
VIGIA Academic Documentation
Module: 44542c22
Batch ID: vigia-doc-0158-44542c22
Generated: 2026-05-20T14:56:47.878644+00:00
-->

## ENGLISH

### What Is This Module?
The Entropy Kernel is the digital turbidity sensor of the VIGÍA Forensic Suite. It quantifies disorder in streams of digital evidence. Instead of manually counting symbols and computing logarithms one by one, this module provides a unified, reproducible engine that works identically on laptops, servers, and graphics processors. Scientists may treat it as a laboratory instrument: feed it a frequency distribution, and it returns a deterministic measurement of randomness.

### Key Concepts
| Concept | Plain-Language Definition | Scientific Role |
|---|---|---|
| Shannon Entropy | A score of unpredictability. Zero means complete order; higher values mean greater disorder. | Detects encryption or compression in suspicious files. |
| Normalized Entropy | The Shannon score linearly rescaled to a 0–1 interval for the specific sample size. | Enables fair comparison between small and large evidence samples. |
| Entropy Rate | A measure of whether each symbol in a sequence depends on the one before it. | Reveals scripted automation, such as botnet beaconing patterns. |
| Batch Processing | Simultaneous measurement of many data series using parallel processor cores or GPU units. | High-throughput screening during large-scale incident response. |
| Deterministic Invariant | A cross-hardware guarantee that identical inputs always produce identical integer histograms and, after scaling, identical rounded results. | Guarantees judicial reproducibility; two labs must not diverge because of different CPUs. |
| Backend | The internal computational engine: GPU (CuPy), vectorized CPU (NumPy), or standard library (pure Python). | Automatically chosen for maximum speed while respecting the deterministic invariant. |
| Drop-in Replacement | A substitute procedure that fits into an existing analytical pipeline without rewriting protocols. | Allows legacy systems to be upgraded transparently. |

### Procedures
| Procedure | Function | Forensic Application |
|---|---|---|
| `entropy_shannon` | Calculates raw disorder from an occurrence table. | Measuring randomness in malware configuration blocks. |
| `entropy_normalized` | Rescales raw disorder to the [0, 1] range. | Comparing entropy across email attachments of different sizes. |
| `entropy_rate` | Quantifies temporal dependence between consecutive symbols. | Identifying C2 scripts that emit correlated rather than random pairs. |
| `entropy_batch` | Analyzes multiple time series in a single deterministic pass. | Mass screening of memory-dump segments. |
| `patch_gci_entropy_score` | Substitutes the legacy static-entropy routine in GCI Engine. | Transparent upgrade of existing VIGÍA integration tests. |
| `patch_gci_entropy_rate` | Substitutes the legacy entropy-rate routine in GCI Engine. | Same as above, for temporal-dependence calculations. |
| `patch_gci_log_n` | Computes the base-2 logarithm of sample size, rounded for hash stability. | Ensuring evidence indexes produce identical hashes on any hardware. |
| `patch_integration_bridge_log_lr` | Computes the natural logarithm of a likelihood ratio with deterministic fallback. | Preserving deterministic chains in probabilistic forensic weighing. |
| `get_backend_info` | Reports the active engine (CPU/GPU/Python) for audit logs. | Regulatory documentation of the analytical environment. |
| `self_test` | Cross-validates all backends against each other before deployment. | Mandatory pre-shift verification in accredited laboratories. |

### Configuration Constants
| Constant | Purpose |
|---|---|
| `_INTEGRATION_GUIDE` | Internal mapping between kernel outputs and legacy suite formats. |
| `_BACKEND` | Identifier of the active calculation engine (`pure`, `numpy`, or `cupy`). |
| `_CUPY_DEVICE` | Identifier of the active graphics processor when GPU mode is selected. |

> **Note on Determinism:** All procedures begin by counting symbol occurrences as **exact integers**. Scaling and transformation are applied afterward through deterministic algebraic operations with fixed, reproducible precision. No step relies on hardware-specific approximations.

> **【Scientific Note】Semiotics Is a Sensor, Not Mysticism**
> VIGÍA occasionally references terminology associated with Charles Sanders Peirce, Umberto Eco, and H. P. Grice. These are not metaphysical doctrines. Think of them as **pattern-detection frameworks**—formal lenses, analogous to a spectrometer or a pressure transducer. Peirce's abduction is a logical hypothesis generator; Eco's codes are classification taxonomies for signs; Grice's maxims are rules for detecting cooperative versus deceptive communication. In forensic practice, they serve as deterministic algorithms for spotting anomalies in digital evidence. A sensor does not "believe" in temperature; it registers it. Likewise, these semiotic models do not interpret meaning mystically; they measure structural properties of forensic artifacts and flag logical fractures in communication streams.

### Glossary
| Term | Definition |
|---|---|
| **Entropy** | A mathematical measure of uncertainty or information density within a discrete set of values. |
| **Vectorized Operation** | A computation applied to an entire array simultaneously rather than element by element. |
| **Backend** | The software engine (CuPy, NumPy, or Python standard library) that executes array operations. |
| **Determinism** | The property that a specific input always yields the exact same output, regardless of hardware or execution timing. |
| **Frequency Table** | A tally of how many times each distinct symbol appears; derived from exact integer arithmetic. |
| **Drop-in Replacement** | A component that substitutes an older one without requiring changes to the surrounding workflow. |
| **GPU** | A massively parallel co-processor used to accelerate array calculations. |
| **Forensic Artifact** | Any digital object submitted as evidence in an investigation. |
| **Time Series** | A chronologically ordered sequence of observations, such as network packets or keystrokes. |
| **Likelihood Ratio** | A statistical factor comparing the probability of evidence under two competing hypotheses. |

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## ESPAÑOL

### ¿Qué es este módulo?
El Kernel de Entropía es el sensor de turbidez digital de la Suite Forense VIGÍA. Cuantifica el desorden en flujos de evidencia digital. En lugar de contar símbolos y calcular logaritmos manualmente, este módulo ofrece un motor unificado y reproducible que opera de manera idéntica en computadoras portátiles, servidores y procesadores gráficos. Los científicos pueden tratarlo como un instrumento de laboratorio: se le proporciona una distribución de frecuencias y devuelve una medida determinista de la aleatoriedad.

### Conceptos Clave
| Concepto | Definición en lenguaje sencillo | Rol científico |
|---|---|---|
| Entropía de Shannon | Puntuación de impredecibilidad. Cero significa orden completo; valores más altos significan mayor desorden. | Detecta cifrado o compresión en archivos sospechosos. |
| Entropía Normalizada | El puntaje de Shannon reescalado linealmente a un intervalo 0–1 para el tamaño específico de muestra. | Permite comparación justa entre muestras de evidencia pequeñas y grandes. |
| Tasa de Entropía | Medida de si cada símbolo en una secuencia depende del anterior. | Revela automatización programada, como patrones de señalización de botnets. |
| Procesamiento por Lotes | Medición simultánea de muchas series de datos usando núcleos de procesador paralelos o unidades GPU. | Cribado de alto rendimiento durante respuesta a incidentes a gran escala. |
| Invariante Determinista | Garantía entre hardware de que entradas idénticas siempre producen histogramas enteros idénticos y resultados redondeados idénticos después del escalado. | Garantiza reproducibilidad judicial; dos laboratorios no deben divergir por diferentes CPUs. |
| Backend | Motor de cálculo interno: GPU (CuPy), CPU vectorizada (NumPy) o biblioteca estándar (Python puro). | Elegido automáticamente para máxima velocidad respetando el invariante determinista. |
| Reemplazo Directo | Procedimiento sustituto que encaja en un pipeline analítico existente sin reescribir protocolos. | Permite actualizar sistemas heredados de forma transparente. |

### Procedimientos
| Procedimiento | Función | Aplicación forense |
|---|---|---|
| `entropy_shannon` | Calcula el desorden bruto desde una tabla de ocurrencias. | Medir aleatoriedad en bloques de configuración de malware. |
| `entropy_normalized` | Reescala el desorden bruto al rango [0, 1]. | Comparar entropía en archivos adjuntos de correo de diferentes tamaños. |
| `entropy_rate` | Cuantifica la dependencia temporal entre símbolos consecutivos. | Identificar scripts C2 que emiten pares correlacionados en vez de aleatorios. |
| `entropy_batch` | Analiza múltiples series temporales en un solo paso determinista. | Cribado masivo de segmentos de volcado de memoria. |
| `patch_gci_entropy_score` | Sustituye la rutina de entropía estática heredada en GCI Engine. | Actualización transparente de pruebas de integración VIGÍA existentes. |
| `patch_gci_entropy_rate` | Sustituye la rutina de tasa de entropía heredada en GCI Engine. | Igual que anterior, para cálculos de dependencia temporal. |
| `patch_gci_log_n` | Calcula el logaritmo base 2 del tamaño de muestra, redondeado para estabilidad del hash. | Asegura que los índices de evidencia produzcan hashes idénticos en cualquier hardware. |
| `patch_integration_bridge_log_lr` | Calcula el logaritmo natural de una razón de verosimilitud con respaldo determinista. | Preservar cadenas deterministas en ponderación forense probabilística. |
| `get_backend_info` | Reporta el motor activo (CPU/GPU/Python) para registros de auditoría. | Documentación regulatoria del entorno analítico. |
| `self_test` | Valida cruzadamente todos los backends entre sí antes del despliegue. | Verificación obligatoria pre-turno en laboratorios acreditados. |

### Constantes de Configuración
| Constante | Propósito |
|---|---|
| `_INTEGRATION_GUIDE` | Mapeo interno entre salidas del kernel y formatos de suite heredada. |
| `_BACKEND` | Identificador del motor de cálculo activo (`pure`, `numpy` o `cupy`). |
| `_CUPY_DEVICE` | Identificador del procesador gráfico activo cuando el modo GPU está seleccionado. |

> **Nota sobre Determinismo:** Todos los procedimientos comienzan tabulando ocurrencias de símbolos como **conteos enteros exactos**. El escalado y la transformación subsiguientes aplican reglas algebraicas deterministas con precisión fija y reproducible. Ningún paso depende de aproximaciones específicas del hardware.

> **【Nota Científica】La Semiótica es un Sensor, No Misticismo**
> VIGÍA ocasionalmente utiliza terminología asociada a Charles Sanders Peirce, Umberto Eco y H. P. Grice. Estas no son doctrinas metafísicas. Considérenlas **marcos de detección de patrones** formales—lentes análogos a un espectrómetro o un transductor de presión. La abducción de Peirce es un generador lógico de hipótesis; los códigos de Eco son taxonomías de clasificación de signos; los máximas de Grice son reglas para distinguir comunicación cooperativa de comunicación engañosa. En la práctica forense funcionan como algoritmos deterministas para detectar anomalías estructurales. Un sensor no "cree" en la temperatura; la registra. Asimismo, estos modelos semióticos no interpretan el sentido místicamente; miden propiedades de artefactos forenses y señalan fracturas lógicas en flujos de comunicación.

### Glosario
| Término | Definición |
|---|---|
| **Entropía** | Medida matemática de incertidumbre o densidad de información dentro de un conjunto discreto de valores. |
| **Operación Vectorizada** | Cálculo aplicado a un arreglo completo simultáneamente en lugar de elemento por elemento. |
| **Backend** | Motor de software (CuPy, NumPy o biblioteca estándar de Python) que ejecuta operaciones de arreglo. |
| **Determinismo** | Propiedad por la cual una entrada específica siempre produce la misma salida exacta, independientemente del hardware o el tiempo de ejecución. |
| **Tabla de Frecuencias** | Recuento de cuántas veces aparece cada símbolo distinto; derivado de aritmética entera exacta. |
| **Reemplazo Directo** | Componente que sustituye a uno más antiguo sin requerir cambios en el flujo de trabajo circundante. |
| **GPU** | Coprocesador masivamente paralelo utilizado para acelerar cálculos de arreglos. |
| **Artefacto Forense** | Cualquier objeto digital presentado como evidencia en una investigación. |
| **Serie Temporal** | Secuencia cronológicamente ordenada de observaciones, como paquetes de red o pulsaciones de teclas. |
| **Razón de Verosimilitud** | Factor estadístico que compara la probabilidad de evidencia bajo dos hipótesis competidoras. |

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## РУССКИЙ

### Что это за модуль?
Ядро энтропии — это цифровой турбидиметрический датчик судебного комплекса VIGÍA. Оно количественно оценивает беспорядок в потоках цифровых доказательств. Вместо ручного подсчёта символов и вычисления логарифмов по одному данный модуль предоставляет унифицированный воспроизводимый движок, работающий одинаково на ноутбуках, серверах и графических процессорах. Учёные могут воспринимать его как лабораторный прибор: подаёте таблицу частот — получаете детерминированную оценку случайности.

### Ключевые понятия
| Понятие | Определение простым языком | Научная роль |
|---|---|---|
| Энтропия Шеннона | Оценка непредсказуемости. Ноль означает полный порядок; большие значения означают большую хаотичность. | Обнаруживает шифрование или сжатие в подозрительных файлах. |
| Нормализованная энтропия | Оценка Шеннона, линейно перемасштабированная до интервала 0–1 для конкретного размера выборки. | Позволяет справедливо сравнивать малые и большие образцы доказательств. |
| Скорость энтропии | Мера того, зависит ли каждый символ в последовательности от предыдущего. | Выявляет автоматизацию по скрипту, например паттерны сигналов ботнетов. |
| Пакетная обработка | Одновременное измерение многих серий данных с использованием параллельных ядер процессора или GPU. | Высокопроизводительный скрининг при масштабном реагировании на инциденты. |
| Инвариант детерминизма | Межаппаратная гарантия того, что идентичные входные данные всегда дают идентичные целочисленные гистограммы и одинаковые результаты. | Гарантирует судебную воспроизводимость; два лаборатории не должны расходиться из-за разных ЦПУ. |
| Бэкенд | Внутренний вычислительный движок: GPU (CuPy), векторизованный ЦПУ (NumPy) или стандартная библиотека (чистый Python). | Выбирается автоматически для максимальной скорости с соблюдением инварианта детерминизма. |
| Прямая замена | Замещающая процедура, встраиваемая в существующий аналитический конвейер без переписывания протоколов. | Позволяет прозрачно обновлять устаревшие системы. |

### Процедуры
| Процедура | Функция | Судебное применение |
|---|---|---|
| `entropy_shannon` | Вычисляет сырую хаотичность по таблице вхождений. | Измерение случайности в блоках конфигурации вредоносного ПО. |
| `entropy_normalized` | Перемасштабирует сырую хаотичность до [0, 1]. | Сравнение энтропии в почтовых вложениях разных размеров. |
| `entropy_rate` | Количественно оценивает временную зависимость между соседними символами. | Выявление скриптов C2, испускающих коррелированные, а не случайные пары. |
| `entropy_batch` | Анализирует несколько временны́х рядов за один детерминированный проход. | Массовый скрининг сегментов дампа памяти. |
| `patch_gci_entropy_score` | Заменяет унаследованную процедуру статической энтропии в GCI Engine. | Прозрачное обновление существующих интеграционных тестов VIGÍA. |
| `patch_gci_entropy_rate` | Заменяет унаследованную процедуру скорости энтропии в GCI Engine. | Аналогично выше, для расчётов временно́й зависимости. |
| `patch_gci_log_n` | Вычисляет логарифм по основанию 2 от размера выборки, округлённый для стабильности хеша. | Обеспечение идентичных хешей индексов доказательств на любом оборудовании. |
| `patch_integration_bridge_log_lr` | Вычисляет натуральный логарифм отношения правдоподобия с детерминированным откатом. | Сохранение детерминированных цепочек при вероятностном судебном взвешивании. |
| `get_backend_info` | Сообщает активный движок (CPU/GPU/Python) для журналов аудита. | Нормативная документация аналитической среды. |
| `self_test` | Перекрёстно проверяет все бэкенды друг против друга перед развёртыванием. | Обязательная доверочная проверка в аккредитованных лабораториях. |

### Константы конфигурации
| Константа | Назначение |
|---|---|
| `_INTEGRATION_GUIDE` | Внутреннее отображение между выходами ядра и форматами унаследованного комплекса. |
| `_BACKEND` | Идентификатор активного вычислительного движка (`pure`, `numpy` или `cupy`). |
| `_CUPY_DEVICE` | Идентификатор активного графического процессора в режиме GPU. |

> **Примечание о детерминизме:** Все процедуры начинаются с табуляции вхождений символов как **точных целочисленных счётчиков**. Последующее масштабирование и преобразование применяют детерминированные алгебраические правила с фиксированной воспроизводимой точностью. Ни один шаг не зависит от аппаратно-специфичных аппроксимаций.

> **【Научное примечание】Семиотика — это датчик, а не мистицизм**
> VIGÍA иногда использует терминологию, связанную с Чарльзом Сандерсом Пирсом, Умберто Эко и Г. П. Грайсом. Это не метафизические учения. Воспринимайте их как формальные **схемы обнаружения паттернов** — аналогично спектрометру или датчику давления. Абдукция Пирса — логический генератор гипотез; коды Эко — таксономии классификации знаков; максимы Грайса — правила выявления кооперативной коммуникации в отличие от обманчивой. На практике судебной экспертизы они служат детерминированными алгоритмами обнаружения структурных аномалий. Датчик не «верит» в температуру; он её регистрирует. Точно так же эти семиотические модели не истолковывают смысл мистически; они измеряют свойства цифровых артефактов и выявляют логические разрывы в потоках коммуникации.

### Глоссарий
| Термин | Определение |
|---|---|
| **Энтропия** | Математическая мера неопределённости или плотности информации в дискретном наборе значений. |
| **Векторизованная операция** | Вычисление, применяемое ко всему массиву одновременно, а не поэлементно. |
| **Бэкенд** | Программный движок (CuPy, NumPy или стандартная библиотека Python), выполняющий операции с массивами. |
| **Детерминизм** | Свойство, при котором конкретный вход всегда даёт точно такой же результат, независимо от оборудования или времени выполнения. |
| **Таблица частот** | Подсчёт количества вхождений каждого отдельного символа; производный от точной целочисленной арифметики. |
| **Прямая замена** | Компонент, заменяющий старый без изменений окружающего рабочего процесса. |
| **GPU** | Массивно-параллельный сопроцессор для ускорения операций с массивами. |
| **Цифровой артефакт** | Любой цифровой объект, представленный в качестве доказательства в расследовании. |
| **Временной ряд** | Хронологически упорядоченная последовательность наблюдений, например сетевые пакеты или нажатия клавиш. |
| **Отношение правдоподобия** | Статистический показатель сравнения вероятности доказательств при двух конкурирующих гипотезах. |

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## 中文

### 这是什么模块？
熵核（Entropy Kernel）是 VIGÍA 取证套件中的数字浊度传感器。它对数字证据流中的无序性进行定量测量。科学家无需手动逐个计数符号并计算对数，而可将该模块视为一台实验室仪器：输入频率分布表，即可获得确定性的随机度读数。该模块在笔记本电脑、服务器及图形处理器上均能产生完全一致的结果。

### 核心概念
| 概念 | 通俗定义 | 科学作用 |
|---|---|---|
| 香农熵 | 不可预测性评分。零代表完全有序；值越高代表越无序。 | 检测可疑文件中的加密或压缩。 |
| 归一化熵 | 针对特定样本大小将香农评分线性重标度至 0–1 区间。 | 允许对大小不同的证据样本进行公平比较。 |
| 熵率 | 衡量序列中每个符号是否依赖于前一个符号。 | 揭示脚本化自动化，例如僵尸网络信标模式。 |
| 批量处理 | 使用并行处理器核心或 GPU 单元同时测量多条数据序列。 | 大规模事件响应期间的高通量筛查。 |
| 确定性不变量 | 跨硬件保证，确保相同输入始终产生相同整数直方图，缩放后结果也相同。 | 保证司法可复现性；两个实验室不得因 CPU 不同而产生分歧。 |
| 后端 | 内部计算引擎：GPU (CuPy)、向量化 CPU (NumPy) 或标准库（纯 Python）。 | 在遵守确定性不变量的同时自动选择以获得最大速度。 |
| 直接替换 | 不改动现有分析流程即可嵌入其中的替代程序。 | 允许透明地升级旧版系统。 |

### 操作流程
| 操作名称 | 功能 | 取证应用 |
|---|---|---|
| `entropy_shannon` | 根据频数表计算原始无序度。 | 测量恶意软件配置块的随机性。 |
| `entropy_normalized` | 将原始无序度归一化至 [0,1]。 | 比较不同大小邮件附件的熵值。 |
| `entropy_rate` | 量化相邻符号的时间依赖性。 | 识别发出关联性而非随机性信号的 C2 脚本。 |
| `entropy_batch` | 一次确定性处理多组时间序列。 | 大规模事件响应中对内存转储段进行批量筛查。 |
| `patch_gci_entropy_score` | 替换 GCI 引擎中的旧版静态熵计算。 | 现有 VIGÍA 集成测试的无缝升级。 |
| `patch_gci_entropy_rate` | 替换 GCI 引擎中的旧版熵率计算。 | 同上，用于时间依赖性计算。 |
| `patch_gci_log_n` | 计算样本大小的以 2 为底的对数，四舍五入以确保哈希稳定性。 | 确保证据索引在任何硬件上产生相同哈希。 |
| `patch_integration_bridge_log_lr` | 计算似然比的自然对数，具有确定性回退。 | 在概率取证加权中维护确定性链。 |
| `get_backend_info` | 报告当前活动引擎（CPU/GPU/Python）以供审计日志使用。 | 分析环境的监管文档记录。 |
| `self_test` | 部署前对所有后端进行交叉验证。 | 认证实验室的强制性班前验证。 |

### 配置常量
| 常量 | 用途 |
|---|---|
| `_INTEGRATION_GUIDE` | 内核输出与旧版套件格式之间的内部映射。 |
| `_BACKEND` | 当前活动计算引擎的标识符（`pure`、`numpy` 或 `cupy`）。 |
| `_CUPY_DEVICE` | 选择 GPU 模式时当前活动图形处理器的标识符。 |

> **确定性说明：** 所有程序均从将符号出现次数计为**精确整数**开始。后续的缩放和变换通过具有固定、可复现精度的确定性代数运算来应用。没有任何步骤依赖于特定硬件的近似值。

> **【科学说明】符号学是传感器，不是神秘主义**
> VIGÍA 偶尔使用与查尔斯·桑德斯·皮尔士、艾柯（Umberto Eco）和格赖斯（H. P. Grice）相关的术语。这些不是形而上学教义。请将它们视为形式化的**模式检测框架**——类似于光谱仪或压力传感器。皮尔士的溯因推理是逻辑假设生成器；艾柯的符码是符号分类分类法；格赖斯的准则是区分合作性与欺骗性通信的规则。在取证实践中，它们用作检测数字证据中结构异常的确定性算法。传感器不"信仰"温度；它只是记录温度。同样，这些符号学模型不以神秘方式解释意义；它们测量取证工件的结构属性并标记通信流中的逻辑断裂。

### 术语表
| 术语 | 定义 |
|---|---|
| **熵** | 离散值集合内不确定性或信息密度的数学度量。 |
| **向量化操作** | 同时应用于整个数组而非逐元素应用的计算。 |
| **后端** | 执行数组操作的软件引擎（CuPy、NumPy 或 Python 标准库）。 |
| **确定性** | 特定输入始终产生完全相同输出的属性，与硬件或执行时序无关。 |
| **频率表** | 每个不同符号出现次数的计数；由精确整数运算得出。 |
| **直接替换** | 无需更改周围工作流即可替代旧组件的组件。 |
| **GPU** | 用于加速数组计算的大规模并行协处理器。 |
| **取证工件** | 在调查中作为证据提交的任何数字对象。 |
| **时间序列** | 按时间顺序排列的观测序列，如网络数据包或击键记录。 |
| **似然比** | 在两个竞争假设下比较证据概率的统计因子。 |

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
