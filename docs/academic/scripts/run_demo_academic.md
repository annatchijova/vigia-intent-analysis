<!--
VIGIA Academic Documentation
Module: d4e678b5
Batch ID: vigia-doc-0022-d4e678b5
Generated: 2026-05-20T14:56:47.849380+00:00
-->

---

# ENGLISH

## What Is This Module?

`scripts/run_demo.py` is the master entry point for the VIGÍA forensic demonstration. Think of it as the **“start button”** for an automated laboratory workflow. It reads a digital case file written in JSON format, transforms raw forensic artefacts into structured signals, evaluates evidence strength through deterministic statistical engines, checks logical consistency via a multi-agent review board, and finally seals the results with a cryptographic integrity chain. No manual Python coding is required from the analyst; the script orchestrates the entire analytical sequence.

The module exposes two control points:

| Function | Role |
|---|---|
| `run_case()` | Executes the full analytical pipeline for a single forensic case file. |
| `main()` | Activates the script when started; locates the case file and triggers `run_case()`. |

## Key Concepts

**Table 1. Workflow Stages**

| Stage | Plain-Language Description | Deterministic Integer Component |
|---|---|---|
| Case Loading | Reads the JSON case file (e.g., `case_001_temporal.json`). | File paths handled as exact byte strings. |
| CaseAdapter | Converts raw forensic artefacts into `SignalOutput` objects. | Integer-indexed artefact arrays. |
| LikelihoodEngine | Scores how strongly each signal supports a hypothesis. | Uses kernel density counts; final scores mapped to rational thresholds via integer arithmetic. |
| GraphStabilityEngine | Validates that the evidence network is robust. | Bootstrap B=500: exactly 500 resampling iterations, counted as integers. |
| RiskBoundedDecisionLayer | Applies decision rules with strict error limits. | Risk budgets expressed as integer counts of allowable misclassifications. |
| AbductionTrace | Records the inference path (Firstness / Secondness / Thirdness). | Trace indices stored as fixed-width integers. |
| ForensicBundle | Collects all outputs into one evidentiary package. | Bundle manifest uses integer sequence numbers. |
| BundleBuilder.seal() | Creates a SHA-256 Merkle chain to prevent tampering. | SHA-256 operates on 512-bit integer blocks; hash chain links are deterministic integers. |
| C3 Multi-Agent Validation | `NarrativeAuditor` checks for logical breaks or prompt injections before closure. | Validation flags are discrete integer states (pass / fail / uncertain). |

**Table 2. Configuration Constants**

| Constant | Purpose |
|---|---|
| `_SCRIPT_DIR` | Absolute path to the script location, ensuring files are found reliably. |
| `_CASE_SEARCH_DIRS` | Ordered list of directories to search for case files. |
| `_VERIFIER_CANDIDATES` | Pool of auditing agents available for the C3 validation step. |
| `_DEFAULT_CASES` | Fallback case filenames if the user supplies none. |
| `_BANNER` | Text header displayed when the demo starts. |

## Glossary

| Term | Definition |
|---|---|
| **Forensic artefact** | Any digital remnant left by user activity (log entry, file timestamp, registry key). |
| **SignalOutput** | A standardized numerical representation of an artefact’s features, ready for statistical analysis. |
| **KDE** | Kernel Density Estimation; here used as a counting-based smoothing method to compare observed frequencies against expected baselines. |
| **Bootstrap B=500** | A robustness check repeating the graph analysis exactly 500 times on resampled subsets. |
| **Merkle chain** | A hierarchical cryptographic checksum where each layer depends on the previous, producing a single top-level integrity value. |
| **Prompt injection** | An adversarial attempt to hide malicious activity inside a narrative or query. |
| **AbductionTrace** | The logical footprint of an inference: Firstness (raw sensation), Secondness (observed reaction), Thirdness (interpreted law or rule). |
| **NarrativeAuditor** | An automated reviewer that verifies story coherence before the case is sealed. |

## 【Scientific Note】

> The terminology of Peirce, Eco, and Grice (Firstness / Secondness / Thirdness, narrative frameworks, implicatures) is sometimes mistaken for metaphysical speculation. In this module, these terms function exactly like a sensor array reading from multiple instruments. **Firstness** is the raw JSON case file before any interpretation—the pure phenomenon. **Secondness** is the CaseAdapter's conversion: each artefact is differentially compared against a known schema and typed as a `SignalOutput`, a binary reaction that detects structural anomalies. **Thirdness** is the LikelihoodEngine's scoring rule: a repeatable law applied uniformly across all signals to produce the same integer-bounded result on identical inputs. Eco's encyclopedia principle guarantees that each pipeline stage receives a uniquely defined object type. Grice's Quantity maxim is operationalized by `BundleBuilder.seal()`: the SHA-256 Merkle chain reports exactly the evidence it contains—no more, no less—making overstatement or understatement architecturally impossible.

---

## ESPAÑOL

## ¿Qué es este módulo?

`scripts/run_demo.py` es el punto de entrada maestro para la demostración forense de VIGÍA. Funciona como el **"botón de inicio"** de un flujo de trabajo de laboratorio automatizado. Lee un archivo de caso digital en formato JSON, transforma artefactos forenses crudos en señales estructuradas, evalúa la solidez de las evidencias mediante motores estadísticos deterministas, verifica la consistencia lógica a través de un comité de revisión multiagente y finalmente sella los resultados con una cadena de integridad criptográfica. El analista no requiere programación manual en Python; el script orquesta la secuencia analítica completa.

El módulo expone dos puntos de control:

| Función | Rol |
|---|---|
| `run_case()` | Ejecuta el flujo de análisis completo para un único archivo de caso forense. |
| `main()` | Activa el script al iniciarse; localiza el archivo de caso y lanza `run_case()`. |

## Conceptos clave

**Tabla 1. Etapas del flujo de trabajo**

| Etapa | Descripción en lenguaje llano | Componente entero determinista |
|---|---|---|
| Carga de caso | Lee el archivo JSON del caso (p. ej., `case_001_temporal.json`). | Rutas manejadas como cadenas de bytes exactas. |
| CaseAdapter | Convierte artefactos forenses crudos en objetos `SignalOutput`. | Matrices de artefactos indexadas por enteros. |
| LikelihoodEngine | Puntúa cuán fuertemente cada señal respalda una hipótesis. | Conteos de densidad de kernel; puntajes finales mapeados a umbrales racionales mediante aritmética entera. |
| GraphStabilityEngine | Valida la robustez de la red de evidencias. | Bootstrap B=500: exactamente 500 iteraciones de remuestreo contadas como enteros. |
| RiskBoundedDecisionLayer | Aplica reglas de decisión con límites de error estrictos. | Presupuestos de riesgo expresados como conteos enteros de errores de clasificación permitidos. |
| AbductionTrace | Registra el camino de inferencia (Primereidad / Segundidad / Terceridad). | Índices de traza almacenados como enteros de ancho fijo. |
| ForensicBundle | Recopila todas las salidas en un paquete evidenciario único. | El manifiesto del paquete usa números de secuencia enteros. |
| BundleBuilder.seal() | Crea una cadena Merkle SHA-256 para prevenir manipulaciones. | SHA-256 opera sobre bloques enteros de 512 bits; los eslabones de la cadena de hash son enteros deterministas. |
| Validación Multiagente C3 | `NarrativeAuditor` verifica rupturas lógicas o inyecciones de prompt antes del cierre. | Las banderas de validación son estados enteros discretos (aprobado / fallido / incierto). |

**Tabla 2. Constantes de configuración**

| Constante | Propósito |
|---|---|
| `_SCRIPT_DIR` | Ruta absoluta a la ubicación del script, asegurando que los archivos se encuentren de manera confiable. |
| `_CASE_SEARCH_DIRS` | Lista ordenada de directorios en los que buscar archivos de caso. |
| `_VERIFIER_CANDIDATES` | Pool de agentes de auditoría disponibles para el paso de validación C3. |
| `_DEFAULT_CASES` | Nombres de archivo de caso predeterminados si el usuario no proporciona ninguno. |
| `_BANNER` | Encabezado de texto que se muestra cuando comienza la demostración. |

## Glosario

| Término | Definición |
|---|---|
| **Artefacto forense** | Cualquier resto digital dejado por la actividad del usuario (entrada de registro, marca temporal de archivo, clave de registro). |
| **SignalOutput** | Representación numérica estandarizada de las características de un artefacto, lista para análisis estadístico. |
| **KDE** | Estimación de Densidad de Kernel; usada aquí como método de suavizado basado en conteo para comparar frecuencias observadas con líneas base esperadas. |
| **Bootstrap B=500** | Verificación de robustez que repite el análisis del grafo exactamente 500 veces sobre subconjuntos remuestreados. |
| **Cadena Merkle** | Suma de verificación criptográfica jerárquica donde cada capa depende de la anterior, produciendo un único valor de integridad de nivel superior. |
| **Inyección de prompt** | Intento adversarial de ocultar actividad maliciosa dentro de una narrativa o consulta. |
| **AbductionTrace** | La huella lógica de una inferencia: Primereidad (sensación bruta), Segundidad (reacción observada), Terceridad (ley o regla interpretada). |
| **NarrativeAuditor** | Revisor automatizado que verifica la coherencia narrativa antes de sellar el caso. |

## 【Nota Científica】

> La terminología de Peirce, Eco y Grice (Primereidad / Segundidad / Terceridad, marcos narrativos, implicaturas) es a veces confundida con especulación metafísica. En este módulo, estos términos funcionan exactamente como una matriz de sensores que toma lecturas de múltiples instrumentos. **La Primereidad** es el archivo JSON del caso antes de cualquier interpretación — el fenómeno puro. **La Segundidad** es la conversión del CaseAdapter: cada artefacto se compara diferencialmente contra un esquema conocido y se tipifica como `SignalOutput`, una reacción binaria que detecta anomalías estructurales. **La Terceridad** es la regla de puntuación del LikelihoodEngine: una ley repetible aplicada uniformemente sobre todas las señales para producir el mismo resultado acotado por enteros en entradas idénticas. El principio de enciclopedia de Eco garantiza que cada etapa del flujo recibe un tipo de objeto definido de manera única. La máxima de Cantidad de Grice es operacionalizada por `BundleBuilder.seal()`: la cadena Merkle SHA-256 reporta exactamente la evidencia que contiene, ni más ni menos.

---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## РУССКИЙ

## Что представляет собой этот модуль?

`scripts/run_demo.py` является главной точкой входа для криминалистической демонстрации VIGÍA. Его можно уподобить **«кнопке запуска»** автоматизированного лабораторного рабочего процесса. Скрипт считывает цифровой файл дела в формате JSON, преобразует необработанные криминалистические артефакты в структурированные сигналы, оценивает силу доказательств с помощью детерминированных статистических движков, проверяет логическую согласованность через многоагентную экспертную комиссию и, наконец, запечатывает результаты криптографической цепочкой целостности. От аналитика не требуется ручного программирования на Python; скрипт оркестрирует полную аналитическую последовательность.

Модуль предоставляет две точки управления:

| Функция | Роль |
|---|---|
| `run_case()` | Выполняет полный аналитический конвейер для единственного криминалистического файла дела. |
| `main()` | Активирует скрипт при запуске; находит файл дела и инициирует `run_case()`. |

## Ключевые концепции

**Таблица 1. Этапы рабочего процесса**

| Этап | Описание простым языком | Детерминированный целочисленный компонент |
|---|---|---|
| Загрузка дела | Считывает JSON-файл дела (напр., `case_001_temporal.json`). | Пути обрабатываются как точные байтовые строки. |
| CaseAdapter | Преобразует необработанные криминалистические артефакты в объекты `SignalOutput`. | Целочисленно-индексированные массивы артефактов. |
| LikelihoodEngine | Оценивает, насколько сильно каждый сигнал поддерживает гипотезу. | Счётчики плотности ядра; итоговые оценки отображаются на рациональные пороги через целочисленную арифметику. |
| GraphStabilityEngine | Проверяет устойчивость доказательственной сети. | Bootstrap B=500: ровно 500 итераций ресамплинга, считаемых как целые числа. |
| RiskBoundedDecisionLayer | Применяет правила принятия решений со строгими пределами ошибок. | Бюджеты риска выражены как целочисленные счётчики допустимых неверных классификаций. |
| AbductionTrace | Записывает путь вывода (Первичность / Вторичность / Третичность). | Индексы трассы хранятся как целые числа фиксированной ширины. |
| ForensicBundle | Собирает все выходные данные в единый доказательственный пакет. | Манифест пакета использует целочисленные порядковые номера. |
| BundleBuilder.seal() | Создаёт цепочку Меркла SHA-256 для предотвращения фальсификации. | SHA-256 работает с 512-битными целочисленными блоками; связи хеш-цепочки — детерминированные целые числа. |
| Многоагентная валидация C3 | `NarrativeAuditor` проверяет логические разрывы или инъекции промпта перед завершением. | Флаги валидации — дискретные целочисленные состояния (пройдено / не пройдено / неопределённо). |

**Таблица 2. Конфигурационные константы**

| Константа | Назначение |
|---|---|
| `_SCRIPT_DIR` | Абсолютный путь к расположению скрипта, обеспечивающий надёжное обнаружение файлов. |
| `_CASE_SEARCH_DIRS` | Упорядоченный список каталогов для поиска файлов дел. |
| `_VERIFIER_CANDIDATES` | Пул агентов аудита, доступных для шага валидации C3. |
| `_DEFAULT_CASES` | Резервные имена файлов дел, если пользователь не указал свои. |
| `_BANNER` | Текстовый заголовок, отображаемый при запуске демонстрации. |

## Глоссарий

| Термин | Определение |
|---|---|
| **Криминалистический артефакт** | Любой цифровой след, оставленный активностью пользователя (запись журнала, временна́я метка файла, ключ реестра). |
| **SignalOutput** | Стандартизированное числовое представление признаков артефакта, готовое для статистического анализа. |
| **KDE** | Оценка плотности ядра; используется здесь как метод сглаживания на основе счётчиков для сравнения наблюдаемых частот с ожидаемыми базовыми линиями. |
| **Bootstrap B=500** | Проверка устойчивости, повторяющая анализ графа ровно 500 раз на ресамплированных подмножествах. |
| **Цепочка Меркла** | Иерархическая криптографическая контрольная сумма, где каждый уровень зависит от предыдущего, производя единственное значение целостности верхнего уровня. |
| **Инъекция промпта** | Состязательная попытка скрыть вредоносную активность внутри нарратива или запроса. |
| **AbductionTrace** | Логический след вывода: Первичность (грубое ощущение), Вторичность (наблюдаемая реакция), Третичность (интерпретированный закон или правило). |
| **NarrativeAuditor** | Автоматизированный рецензент, верифицирующий нарративную согласованность перед запечатыванием дела. |

## 【Научное примечание】

> Терминология Пирса, Эко и Грайса (Первичность / Вторичность / Третичность, нарративные рамки, импликатуры) иногда ошибочно принимается за метафизические спекуляции. В данном модуле эти термины функционируют точно как массив датчиков, снимающих показания с нескольких инструментов. **Первичность** — это JSON-файл дела до какой-либо интерпретации — чистое явление. **Вторичность** — это преобразование CaseAdapter: каждый артефакт дифференциально сравнивается с известной схемой и типизируется как `SignalOutput`, бинарная реакция, обнаруживающая структурные аномалии. **Третичность** — это правило оценки LikelihoodEngine: повторяемый закон, единообразно применяемый ко всем сигналам для производства одного и того же целочисленно-ограниченного результата на идентичных входных данных. Принцип энциклопедии Эко гарантирует, что каждый этап конвейера получает уникально определённый тип объекта. Максима Количества Грайса операционализируется `BundleBuilder.seal()`: цепочка Меркла SHA-256 сообщает ровно те доказательства, которые содержит — ни больше ни меньше.

---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## 中文

## 本模块是什么？

`scripts/run_demo.py` 是 VIGÍA 取证演示的主入口点。可将其理解为自动化实验室工作流程的**"启动按钮"**。它读取 JSON 格式的数字案例文件，将原始取证工件转换为结构化信号，通过确定性统计引擎评估证据强度，经多智能体审查委员会检验逻辑一致性，最终以密码学完整性链封存结果。分析员无需手动编写 Python 代码；脚本编排完整的分析序列。

模块提供两个控制点：

| 函数 | 作用 |
|---|---|
| `run_case()` | 对单个取证案例文件执行完整分析流水线。 |
| `main()` | 脚本启动时激活；定位案例文件并触发 `run_case()`。 |

## 核心概念

**表 1. 工作流程阶段**

| 阶段 | 通俗描述 | 确定性整数组件 |
|---|---|---|
| 案例加载 | 读取 JSON 案例文件（如 `case_001_temporal.json`）。 | 路径作为精确字节字符串处理。 |
| CaseAdapter | 将原始取证工件转换为 `SignalOutput` 对象。 | 整数索引的取证工件数组。 |
| LikelihoodEngine | 评分每个信号对假设的支持强度。 | 使用核密度计数；最终评分通过整数算术映射至有理阈值。 |
| GraphStabilityEngine | 验证证据网络的鲁棒性。 | Bootstrap B=500：恰好 500 次重采样迭代，计为整数。 |
| RiskBoundedDecisionLayer | 以严格误差限制应用决策规则。 | 风险预算表示为允许错误分类的整数计数。 |
| AbductionTrace | 记录推断路径（初性/二性/三性）。 | 轨迹索引存储为固定宽度整数。 |
| ForensicBundle | 将所有输出收集到一个证据包中。 | 包清单使用整数序列号。 |
| BundleBuilder.seal() | 创建 SHA-256 默克尔链以防篡改。 | SHA-256 在 512 位整数块上操作；哈希链链接为确定性整数。 |
| C3 多智能体验证 | `NarrativeAuditor` 在结束前检查逻辑断裂或提示词注入。 | 验证标志为离散整数状态（通过/失败/不确定）。 |

**表 2. 配置常量**

| 常量 | 用途 |
|---|---|
| `_SCRIPT_DIR` | 脚本位置的绝对路径，确保文件可靠找到。 |
| `_CASE_SEARCH_DIRS` | 搜索案例文件的有序目录列表。 |
| `_VERIFIER_CANDIDATES` | C3 验证步骤可用的审计智能体池。 |
| `_DEFAULT_CASES` | 用户未提供时的回退案例文件名。 |
| `_BANNER` | 演示启动时显示的文本标题。 |

## 术语表

| 术语 | 定义 |
|---|---|
| **取证工件** | 用户活动留下的任何数字遗迹（日志条目、文件时间戳、注册表键）。 |
| **SignalOutput** | 取证工件特征的标准化数值表示，可直接用于统计分析。 |
| **KDE** | 核密度估计；此处用作基于计数的平滑方法，将观察频率与预期基线对比。 |
| **Bootstrap B=500** | 鲁棒性检验，在重采样子集上恰好重复图分析 500 次。 |
| **默克尔链** | 层次密码校验和，每层依赖前一层，产生单个顶层完整性值。 |
| **提示词注入** | 将恶意活动隐藏于叙述或查询中的对抗性尝试。 |
| **AbductionTrace** | 推断的逻辑印记：初性（原始感知）、二性（观察到的反应）、三性（解释的规律或规则）。 |
| **NarrativeAuditor** | 在案例封存前验证叙述一致性的自动化审查员。 |

## 【科学说明】

> 皮尔斯、艾柯和格赖斯的术语（初性/二性/三性、叙述框架、含义推导）有时被误认为是形而上学推测。在本模块中，这些术语的功能与从多个仪器读取数据的传感器阵列完全相同。**初性**是 JSON 案例文件在任何解释之前的状态——纯粹的现象。**二性**是 CaseAdapter 的转换：每个取证工件与已知模式进行差异比较并类型化为 `SignalOutput`，这是一种检测结构异常的二元反应。**三性**是 LikelihoodEngine 的评分规则：一种可重复的规律，均匀应用于所有信号，对相同输入产生相同的整数有界结果。艾柯的百科全书原则保证流水线每个阶段接收唯一定义的对象类型。格赖斯的量的准则通过 `BundleBuilder.seal()` 被操作化：SHA-256 默克尔链精确报告其包含的证据，不多也不少，使夸大或遗漏在架构上不可能发生。

---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
