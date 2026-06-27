<!--
VIGIA Academic Documentation
Module: 1e1dcf92
Batch ID: vigia-doc-0002-1e1dcf92
Generated: 2026-05-20T14:56:47.845378+00:00
-->

# Module Documentation: `cases/demo_case.py`

## ENGLISH

### What Is This Module?

This file, `cases/demo_case.py`, is the automated demonstrator for the VIGÍA Forensic Suite. Think of it as a laboratory robot that accepts a case file (a structured JSON document such as `case_001_temporal.json`) and executes a pre-defined analytical pipeline. It requires no knowledge of Python to operate; it is invoked from the system command line. The script produces two primary outputs: (1) a tamper-evident evidence bundle (`bundle_<case_id>.json`) that can be verified deterministically via integer checksum logic, and (2) a forensic report (`report_<case_id>.json`) compliant with ENFSI standards and containing an `AbductionTrace`. The module can process a single case or, with `--all-cases`, scan entire directories for batch execution. An optional connection to a local language model via Ollama (e.g., `llama3.2`) can be enabled for auxiliary textual analysis, though all core integrity checks rely strictly on deterministic integer arithmetic.

### Key Concepts

| Term | Role | Analogy |
|---|---|---|
| `run_single_case()` | Executes the complete forensic pipeline for one input case. | Pressing "Start" on an automated laboratory sequencer. |
| `main()` | Parses command-line instructions and routes execution to single-case or batch mode. | A reception desk that directs each sample to the correct analysis room. |
| `case_001_temporal.json` | Structured input file containing temporal artifacts and case metadata. | A patient intake form annotated with a detailed timeline. |
| `bundle_<case_id>.json` | Cryptographically verifiable output container adhering to EBS v1. | A sealed evidence bag bearing a tamper-evident integer seal. |
| `report_<case_id>.json` | ENFSI-compliant report embedding `AbductionTrace` records. | A peer-reviewed instrument print-out appended to a case file. |
| `_VIGIA_PROD_CANDIDATES` | Candidate filesystem paths searched by the suite to locate production modules. | A library card catalog used to find the correct equipment manual. |
| `_CASE_SEARCH_DIRS` | Directories recursively scanned when the `--all-cases` flag is issued. | A warehouse map used to retrieve all pending samples in one batch. |
| `_BANNER` | ASCII constant displaying version, attribution, and legal notices. | The letterhead on official laboratory stationery. |
| `verify_ebs_v1__3_.py` | External verification script using exact integer checksums; no floating-point arithmetic is involved. | A precision balance that confirms mass without rounding errors. |
| `AbductionTrace` | Deterministic, integer-ranked log of hypotheses generated via Peircean abduction. | A sensor's output log showing every measurement step in whole-number units. |
| **Deterministic Integer Arithmetic** | The use of whole-number operations (checksums, counters, exact string comparisons) to guarantee bitwise-identical results across all hardware platforms. | Counting discrete atoms rather than estimating continuous fluid volume. |

### Glossary

| Term | Definition |
|---|---|
| **Case File** | A JSON-formatted dataset containing digital artifacts, timestamps, and investigative metadata for one incident. |
| **Command-Line Flag** | A text switch (e.g., `--input`, `--output`) provided when the program is launched to alter its behavior. |
| **EBS v1 (Evidence Bundle Standard, version 1)** | A signed, structured container format designed to preserve evidence integrity from collection to court. |
| **ENFSI** | European Network of Forensic Science Institutes; compliance denotes adherence to transnational scientific quality benchmarks. |
| **Forensic Suite** | An integrated collection of software tools purpose-built for the scientific examination of digital evidence. |
| **Pipeline** | A rigid, sequential processing architecture in which the output of each stage becomes the input of the next, with no manual intervention. |
| **Deterministic Integer Arithmetic** | Mathematical operations restricted to integers (e.g., cryptographic hashes, exact counters) that produce identical results on every repetition and on every computing platform, excluding the rounding uncertainty inherent to floating-point representations. |
| **Ollama** | An optional, locally hosted inference engine for large language models; here it serves as an auxiliary natural-language sensor, not as a deterministic verifier. |
| **Temporal Artifacts** | Time-stamped digital traces—such as event logs, registry entries, or file MAC times—used to reconstruct the chronology of user or system activity. |
| **AbductionTrace** | A structured, machine-readable record of abductive (hypothesis-generating) inference steps, formally grounded in Peircean logic and ranked by integer confidence metrics. |

### 【Scientific Note】

The terminology of Peirce, Eco, and Grice is sometimes mistaken for metaphysical speculation. In this module, these terms function exactly like sensor metadata. Charles Sanders Peirce's *abduction* is not mysticism; it is the formal logic of hypothesis selection under uncertainty—mathematically analogous to how a spectrometer selects the most probable molecular signature from raw intensity data. Umberto Eco's semiotic limits operate like calibration bounds on an instrument: they define the range within which a sign (data pattern) can be said to represent an object (system state). H. Paul Grice's conversational maxims act as noise-reduction filters, eliminating interpretive hypotheses that violate cooperative consistency. The `AbductionTrace` is therefore a deterministic register of integer-ranked hypotheses, comparable to a digital sensor's output log—nothing more, nothing less.

---

## ESPAÑOL

### ¿Qué es este módulo?

Este archivo, `cases/demo_case.py`, es el demostrador automatizado de la VIGÍA Forensic Suite. Piense en él como un robot de laboratorio que acepta un archivo de caso (un documento JSON estructurado, como `case_001_temporal.json`) y ejecuta una tubería analítica predefinida. No se requiere conocimiento de Python para su uso; se invoca desde la línea de comandos del sistema. El script produce dos salidas principales: (1) un paquete de evidencia a prueba de manipulaciones (`bundle_<case_id>.json`) que puede verificarse de manera determinista mediante lógica de suma de comprobación entera, y (2) un informe forense (`report_<case_id>.json`) conforme a los estándares ENFSI y que contiene un `AbductionTrace`. El módulo puede procesar un caso único o, con `--all-cases`, escanear directorios completos para ejecución por lotes. Una conexión opcional a un modelo de lenguaje local mediante Ollama (p. ej., `llama3.2`) puede habilitarse para análisis textual auxiliar, aunque todas las comprobaciones de integridad central se basan estrictamente en aritmética entera determinista.

### Conceptos Clave

| Término | Función | Analogía |
|---|---|---|
| `run_single_case()` | Ejecuta la tubería forense completa para un caso de entrada. | Pulsar "Inicio" en un secuenciador de laboratorio automatizado. |
| `main()` | Analiza las instrucciones de la línea de comandos y dirige la ejecución al modo unitario o por lotes. | Una recepción que dirige cada muestra a la sala de análisis correcta. |
| `case_001_temporal.json` | Archivo de entrada estructurado que contiene artefactos temporales y metadatos del caso. | Una ficha de admisión de paciente anotada con una cronología detallada. |
| `bundle_<case_id>.json` | Contenedor de salida verificable criptográficamente conforme al EBS v1. | Una bolsa de evidencia sellada con un sello entero a prueba de manipulaciones. |
| `report_<case_id>.json` | Informe compatible con ENFSI que incorpora registros `AbductionTrace`. | Un informe revisado por pares generado por el instrumento, anexado al expediente. |
| `_VIGIA_PROD_CANDIDATES` | Rutas candidatas del sistema de archivos donde la suite busca módulos de producción. | Un catálogo de tarjetas de biblioteca para encontrar el manual del equipo adecuado. |
| `_CASE_SEARCH_DIRS` | Directorios escaneados recursivamente cuando se emite la bandera `--all-cases`. | Un mapa de almacén utilizado para recuperar todas las muestras pendientes en un lote. |
| `_BANNER` | Constante ASCII que muestra la versión, atribución y avisos legales. | El membrete del papel membretado oficial del laboratorio. |
| `verify_ebs_v1__3_.py` | Script de verificación externo que utiliza sumas de comprobación enteras exactas; no interviene aritmética de coma flotante. | Una balanza de precisión que confirma la masa sin errores de redondeo. |
| `AbductionTrace` | Registro determinista, clasificado por enteros, de hipótesis generadas mediante abducción peirceana. | El registro de salida de un sensor que muestra cada paso de medición en unidades de números enteros. |
| **Aritmética entera determinista** | Uso de operaciones con números enteros (sumas de comprobación, contadores, comparaciones exactas de cadenas) para garantizar resultados idénticos bit a bit en todas las plataformas de hardware. | Contar átomos discretos en lugar de estimar el volumen de un fluido continuo. |

### Glosario

| Término | Definición |
|---|---|
| **Archivo de caso** | Conjunto de datos en formato JSON que contiene artefactos digitales, marcas temporales y metadatos de investigación de un incidente. |
| **Bandera de línea de comandos** | Interruptor de texto (p. ej., `--input`, `--output`) proporcionado al lanzar el programa para modificar su comportamiento. |
| **EBS v1 (Evidence Bundle Standard, versión 1)** | Formato de contenedor estructurado y firmado diseñado para preservar la integridad de la evidencia desde la recolección hasta el tribunal. |
| **ENFSI** | Red Europea de Institutos de Ciencias Forenses; el cumplimiento denota adherencia a parámetros científicos de calidad transnacionales. |
| **Suite forense** | Colección integrada de herramientas de software diseñadas para el examen científico de evidencia digital. |
| **Tubería / Pipeline** | Arquitectura de procesamiento secuencial y rígida en la que la salida de cada etapa se convierte en la entrada de la siguiente, sin intervención manual. |
| **Aritmética entera determinista** | Operaciones matemáticas restringidas a enteros que producen resultados idénticos en cada repetición y en cada plataforma de cómputo. |
| **Ollama** | Motor de inferencia local opcional para modelos de lenguaje grande; aquí actúa como sensor auxiliar de análisis de lenguaje natural, no como verificador determinista. |
| **Artefactos temporales** | Rastros digitales con marca temporal utilizados para reconstruir la cronología de la actividad del usuario o del sistema. |
| **AbductionTrace** | Registro estructurado y legible por máquina de los pasos de inferencia abductiva, formalmente basado en la lógica peirceana y clasificado por métricas de confianza enteras. |

### 【Nota Científica】

La terminología de Peirce, Eco y Grice a veces se confunde con especulación metafísica. En este módulo, estos términos funcionan exactamente como metadatos de sensor. La *abducción* de Charles Sanders Peirce no es misticismo; es la lógica formal de selección de hipótesis bajo incertidumbre—análoga matemáticamente a cómo un espectrómetro selecciona la firma molecular más probable a partir de datos brutos de intensidad. Los límites semióticos de Umberto Eco operan como límites de calibración de un instrumento: definen el rango dentro del cual un signo (patrón de datos) puede decirse que representa un objeto (estado del sistema). Los máximas conversacionales de H. Paul Grice actúan como filtros de reducción de ruido, eliminando hipótesis interpretativas que violan la consistencia cooperativa. El `AbductionTrace` es, por tanto, un registro determinista de hipótesis clasificadas por números enteros, comparable al log de salida de un sensor digital—ni más, ni menos.

---

## РУССКИЙ

### Что это за модуль?

Этот файл, `cases/demo_case.py`, — автоматический демонстратор для судебно-экспертного комплекса VIGÍA. Представьте его как лабораторного робота, принимающего файл дела (структурированный JSON-документ, например `case_001_temporal.json`) и выполняющего предопределённый аналитический конвейер. Для работы с ним не требуется знание Python; он запускается из командной строки системы. Скрипт производит два основных вывода: (1) пакет доказательств с защитой от несанкционированного доступа (`bundle_<case_id>.json`), который можно верифицировать детерминировано посредством целочисленной логики контрольных сумм, и (2) судебный отчёт (`report_<case_id>.json`) в соответствии со стандартами ENFSI, содержащий записи `AbductionTrace`. Модуль может обрабатывать одно дело или, с флагом `--all-cases`, сканировать целые директории для пакетного выполнения.

### Ключевые понятия

| Термин | Роль | Аналогия |
|---|---|---|
| `run_single_case()` | Выполняет полный криминалистический конвейер для одного входного дела. | Как нажатие кнопки «Старт» на автоматическом лабораторном секвенаторе. |
| `main()` | Точка входа, считывающая инструкции командной строки. | Как приёмная, направляющая образцы в нужную лабораторию. |
| `case_001_temporal.json` | Входной файл со структурированными данными дела и временны́ми артефактами. | Как карта пациента с временно́й шкалой. |
| `bundle_<case_id>.json` | Выходной артефакт, соответствующий стандарту EBS v1. | Как запечатанный пакет с вещдоком и индикатором вскрытия. |
| `report_<case_id>.json` | Отчёт, соответствующий стандартам ENFSI, с записями `AbductionTrace`. | Как рецензируемый лабораторный отчёт, сгенерированный прибором. |
| `_VIGIA_PROD_CANDIDATES` | Список путей, где suite ищет производственные модули. | Как библиотечный каталог для поиска руководств по оборудованию. |
| `_CASE_SEARCH_DIRS` | Каталоги, сканируемые при запросе `--all-cases`. | Как карта склада для пакетной выборки всех ожидающих образцов. |
| `verify_ebs_v1__3_.py` | Внешний детерминированный верификатор на основе целочисленных контрольных сумм, а не плавающей точки. | Как прецизионные весы, проверяющие массу без ошибок округления. |
| `AbductionTrace` | Структурированный журнал умозаключений по пирсовской абдукции. | Как журнал аудита гипотез, полученных с данных сенсоров. |
| `_BANNER` | Константа с текстом ASCII, отображающая версию и авторство. | Как бланк официальной лабораторной бумаги. |

### Глоссарий

| Термин | Определение |
|---|---|
| **Криминалистический пакет / Forensic Suite** | Интегрированный набор программных инструментов для экспертизы цифровых доказательств. |
| **Конвейер / Pipeline** | Фиксированная последовательность этапов обработки, где выход одного этапа подаётся на вход следующего. |
| **EBS v1** | Структурированный подписанный контейнер для обеспечения целостности доказательств. |
| **ENFSI** | Европейская сеть криминалистических научных институтов; соответствие стандартам подразумевает соблюдение научных норм качества. |
| **AbductionTrace** | Машиночитаемая запись абдуктивных умозаключений, полученных при анализе артефактов. |
| **Детерминированная целочисленная арифметика** | Вычисления с целыми числами, дающие точно воспроизводимые результаты, в отличие от операций с плавающей точкой, вносящих погрешность округления. |
| **Ollama** | Дополнительный локальный движок вывода для больших языковых моделей, используемый здесь как вспомогательный текстовый сенсор. |
| **Временны́е артефакты** | Цифровые следы с временны́ми метками для реконструкции последовательности событий. |
| **Аргумент командной строки** | Текстовая инструкция, передаваемая программе при запуске. |

### 【Научное Примечание】

Терминология Пирса, Эко и Грайса иногда ошибочно принимается за метафизическую спекуляцию. В данном модуле эти термины работают точно так же, как метаданные сенсора. Абдукция Чарльза Сандерса Пирса — это не мистицизм; это формальная логика выбора гипотезы в условиях неопределённости — математически аналогичная тому, как спектрометр выбирает наиболее вероятную молекулярную сигнатуру из сырых данных об интенсивности. Семиотические границы Умберто Эко действуют как калибровочные пределы прибора: они определяют диапазон, внутри которого знак (шаблон данных) может считаться представляющим объект (состояние системы). Конверсациональные максимы Г. Пола Грайса работают как фильтры подавления шума, устраняя интерпретативные гипотезы, нарушающие кооперативную согласованность. Таким образом, `AbductionTrace` представляет собой детерминированный регистр гипотез, ранжированных целыми числами, сопоставимый с журналом выходных данных цифрового сенсора — ни больше, ни меньше.

---

## 中文

### 本模块是什么？

本文件（`cases/demo_case.py`）是 VIGÍA 取证套件的自动化演示脚本。可将其想象为一个实验室机器人：接受案件文件（结构化 JSON 文档，如 `case_001_temporal.json`），并执行预定义的分析流程。无需 Python 知识，从系统命令行调用即可。该脚本产生两项主要输出：(1) 可通过确定性整数校验和逻辑进行验证的防篡改证据包（`bundle_<case_id>.json`），以及 (2) 符合 ENFSI 标准、内含 `AbductionTrace` 的取证报告（`report_<case_id>.json`）。本模块可处理单个案件，也可使用 `--all-cases` 标志扫描整个目录进行批量执行。

### 核心概念

| 术语 | 作用 | 类比 |
|---|---|---|
| `run_single_case()` | 为单个案件执行完整的取证流程。 | 如同按下自动化实验测序仪的"启动"键。 |
| `main()` | 程序入口，读取命令行指令并选择单件或批量模式。 | 如同实验室前台，将样本分发到正确的分析室。 |
| `case_001_temporal.json` | 包含结构化案件数据与时间取证工件的输入文件。 | 如同带有时间线的患者登记表。 |
| `bundle_<case_id>.json` | 符合 EBS v1 标准的输出取证工件。 | 如同带有防拆标签的密封证物袋。 |
| `report_<case_id>.json` | 符合 ENFSI 标准的报告，内含 `AbductionTrace`。 | 如同由仪器生成的、经过同行评审的实验报告。 |
| `_VIGIA_PROD_CANDIDATES` | 套件搜索生产模块的路径列表。 | 如同查找设备手册的图书馆卡片目录。 |
| `_CASE_SEARCH_DIRS` | 当请求 `--all-cases` 时扫描的目录。 | 如同批量调取所有待检样本的仓库地图。 |
| `verify_ebs_v1__3_.py` | 外部确定性验证器，使用整数校验和而非浮点运算。 | 如同精确称重而不产生舍入误差的天平。 |
| `AbductionTrace` | 遵循皮尔斯溯因推理的结构化推理步骤日志。 | 如同由传感器数据生成假设的审计追踪。 |
| `_BANNER` | 显示版本与作者信息的 ASCII 文本常量。 | 如同实验室正式信笺上的抬头。 |

### 术语表

| 术语 | 定义 |
|---|---|
| **取证套件 (Forensic Suite)** | 用于数字证据检验的集成软件工具集。 |
| **流程管道 (Pipeline)** | 固定的处理阶段序列，前一阶段的输出直接作为下一阶段的输入。 |
| **EBS v1 (证据包标准第1版)** | 结构化的签名容器格式，确保证据完整性。 |
| **ENFSI** | 欧洲法庭科学研究所网络；合规意味着符合科学质量标准。 |
| **溯因痕迹 (AbductionTrace)** | 机器可读的、从取证工件分析中得出的溯因推理（假设形成）记录。 |
| **确定性整数运算** | 使用整数进行计算，产生完全可复现的结果，避免浮点运算带来的舍入不确定性。 |
| **Ollama** | 可选的本地大语言模型推理引擎，在此作为辅助文本分析传感器使用。 |
| **时间取证工件** | 带有时间戳的数字痕迹，用于重建事件序列。 |
| **命令行参数** | 启动程序时传入的文本指令（例如 `--input`）。 |
| **逻辑断裂** | 在符号系统中，数据模式与其所表征的系统状态之间出现的解释性断裂；溯因推理的作用即在于通过确定性整数排序的假设来弥合此类断裂。 |

### 【科学说明】

皮尔斯、艾柯与格赖斯的术语有时被误认为玄学思辨。在本模块中，这些术语的功能与传感器元数据完全等同。查尔斯·桑德斯·皮尔斯的"溯因"（abduction）并非神秘主义，而是在不确定性下进行假设选择的形式逻辑——在数学上类似于光谱仪如何从原始强度数据中选中最可能的分子特征。翁贝托·艾柯的符号学界限如同仪器的校准阈值：它们界定了"符号"（数据模式）在何种范围内可以被视为代表"对象"（系统状态）。H·保罗·格赖斯的会话准则则充当降噪滤波器，剔除那些违反合作一致性的解释假设。因此，`AbductionTrace` 是一个以确定性整数排序的假设寄存器，相当于数字传感器的输出日志——仅此而已，既非更多，也非更少。当数据模式与系统状态之间出现**逻辑断裂**时，该寄存器通过严格的整数运算填补断裂，生成可复现的推理链，而非依赖任何浮点近似。

---

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
