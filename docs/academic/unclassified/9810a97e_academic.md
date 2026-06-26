<!--
VIGIA Academic Documentation
Module: 9810a97e
Batch ID: vigia-doc-0005-9810a97e
Generated: 2026-05-20T14:56:47.845994+00:00
-->

## ENGLISH

### What Is This Module?
This file is the **Independent EBS v1 Verifier**, a standalone audit tool belonging to the VIGIA Forensic Suite. In non-programming terms, it is an external inspector that reads a digital evidence package and checks whether every seal, label, and measurement inside follows the EBS version 1 standard. Crucially, it does not trust the software that originally created the package. It carries its own copy of every rule and threshold, and it runs using only the basic tools that come pre-installed with Python. This means any independent scientist or court-appointed expert can run it on any computer with Python 3.6 or newer without installing anything else.

### Module Components

| Name | Role |
|---|---|
| `verify_bundle()` | Performs the complete audit of one evidence bundle. |
| `main()` | Provides a direct command-line interface for immediate use. |
| `VerificationResult` | A structured log that stores every pass, warning, and failure detected during an audit. |
| `add()` | Records a single finding into the result log. |
| `critical_failures()` | Extracts only those findings that render the bundle scientifically or legally invalid. |
| `to_dict()` | Converts the result log into a plain structured data map. |
| `to_json()` | Converts the result log into a standardized JSON text string for exchange. |
| `_EBS_VERSION` | The exact version of the EBS standard enforced by this script. |
| `_EBS_SUPPORTED_VERSIONS` | All standard versions recognized as valid. |
| `_VERIFIER_VERSION` | The internal revision number of the verifier itself. |
| `TOL` | The integer tolerance limit for boundary checks; deviations are measured against this exact whole number. |

### Key Concepts

| Concept | Plain-Language Explanation |
|---|---|
| **Total Independence** | The verifier never imports code from the main VIGIA system. All constants are duplicated here intentionally so the audit cannot be influenced by the production environment. |
| **Deterministic Integer Arithmetic** | Every numerical comparison uses exact operations on whole numbers. There are no fractional approximations, ensuring identical results on every machine. |
| **Local Constants** | Rules and thresholds are hard-copied into this file. If the original production code changes, this verifier still applies the known standard. |
| **Critical Failure** | A defect severe enough to break the chain of custody or corrupt scientific reproducibility. |
| **JSON Export** | A universal text format that lets other systems read the verdict without understanding Python. |

### Glossary

- **EBS (Evidence Bundle Standard)**: The protocol that defines how digital forensic artifacts must be packaged, labeled, and linked to metadata.
- **Stdlib (Standard Library)**: The built-in set of tools included with Python. Because only these tools are used, no extra software installation is required.
- **Verifier**: An independent checker that audits evidence without relying on the original author's code.
- **Bundle**: A structured container holding one or more digital evidence files plus their descriptive metadata.
- **Deterministic**: A process that yields exactly the same output whenever the same input and conditions are repeated.
- **Tolerance (TOL)**: An integer boundary value. A measurement must exceed this precise whole number before it is flagged as an anomaly.

### 【Scientific Note】
Terms borrowed from semiotics—such as **Peirce's** categories, **Eco's** (艾柯) codes, and **Grice's** (格赖斯) maxims—are used throughout the VIGIA suite as analytical sensors, not as metaphysical or mystical doctrines. Think of them as laboratory instruments: just as a spectrometer assigns precise wavelengths to chemical signals, these terminological frames assign precise coordinates to communication structures within evidence bundles. When the verifier reports a "breach of the cooperative principle," it is functionally identical to a sensor registering an out-of-range voltage. The purpose is to detect **logical fractures** (逻辑断裂) in the chain of proof. The notation is operationalized forensic mathematics, not mysticism.

---

## ESPAÑOL

### ¿Qué es este módulo?
Este archivo es el **Verificador Independiente EBS v1**, una herramienta de auditoría autónoma del conjunto forense VIGIA. En lenguaje sencillo, es un inspector externo que lee un paquete de evidencia digital y verifica si cada sello, etiqueta y medida cumple el estándar EBS versión 1. Lo esencial es que no confía en el software que creó originalmente el paquete. Transporta su propia copia de cada regla y umbral, y funciona únicamente con las herramientas básicas incluidas en Python. Esto significa que cualquier científico independiente o perito designado por un tribunal puede ejecutarlo en cualquier computadora con Python 3.6 o superior sin instalar nada adicional.

### Componentes del módulo

| Nombre | Función |
|---|---|
| `verify_bundle()` | Realiza la auditoría completa de un paquete de evidencia. |
| `main()` | Ofrece una interfaz de línea de comandos para uso inmediato. |
| `VerificationResult` | Un registro estructurado que almacena cada acierto, advertencia y fallo detectado. |
| `add()` | Anota un hallazgo individual en el registro de resultados. |
| `critical_failures()` | Extrae únicamente los hallazgos que invalidan científica o legalmente el paquete. |
| `to_dict()` | Convierte el registro en un mapa de datos estructurado en texto plano. |
| `to_json()` | Convierte el registro en una cadena de texto JSON estandarizada para intercambio. |
| `_EBS_VERSION` | La versión exacta del estándar EBS que aplica este script. |
| `_EBS_SUPPORTED_VERSIONS` | Todas las versiones del estándar reconocidas como válidas. |
| `_VERIFIER_VERSION` | El número de revisión interno del propio verificador. |
| `TOL` | El límite entero de tolerancia para comprobaciones de frontera; las desviaciones se miden contra este número exacto. |

### Conceptos clave

| Concepto | Explicación sencilla |
|---|---|
| **Independencia total** | El verificador nunca importa código del sistema VIGIA principal. Todas las constantes se duplican aquí intencionalmente para que la auditoría no pueda ser influenciada por el entorno de producción. |
| **Aritmética entera determinista** | Toda comparación numérica usa operaciones exactas sobre números enteros. No hay aproximaciones fraccionarias, garantizando resultados idénticos en cualquier máquina. |
| **Constantes locales** | Las reglas y umbrales se copian directamente en este archivo. Si el código de producción original cambia, este verificador aplica igualmente el estándar conocido. |
| **Fallo crítico** | Un defecto grave suficiente para romper la cadena de custodia o corromper la reproducibilidad científica. |
| **Exportación JSON** | Un formato de texto universal que permite a otros sistemas leer el veredicto sin conocer Python. |

### Glosario

- **EBS (Estándar de Paquete de Evidencia)**: Protocolo que define cómo deben empaquetarse, etiquetarse y vincularse a metadatos los artefactos forenses digitales.
- **Stdlib (Biblioteca estándar)**: Conjunto de herramientas incorporado en Python. Al usar solo estas herramientas, no se requiere instalación de software adicional.
- **Verificador**: Auditor independiente que examina la evidencia sin depender del código del autor original.
- **Paquete (Bundle)**: Contenedor estructurado que aloja uno o más archivos de evidencia digital junto con sus metadatos descriptivos.
- **Determinista**: Proceso que produce exactamente el mismo resultado cada vez que se repiten la misma entrada y condiciones.
- **Tolerancia (TOL)**: Un valor límite entero. Una medida debe superar este número exacto antes de ser marcada como anomalía.

### 【Nota Científica】
Los términos tomados de la semiótica—como las categorías de **Peirce**, los códigos de **Eco** (艾柯) y las máximas de **Grice** (格赖斯)—se emplean en la suite VIGIA como sensores analíticos, no como doctrinas metafísicas o místicas. Piense en ellos como instrumentos de laboratorio: así como un espectrómetro asigna longitudes de onda precisas a señales químicas, estos marcos terminológicos asignan coordenadas precisas a las estructuras de comunicación dentro de los paquetes de evidencia. Cuando el verificador reporta un "incumplimiento del principio cooperativo", es funcionalmente idéntico a un sensor que registra un voltaje fuera de rango. El objetivo es detectar **rupturas lógicas** (逻辑断裂) en la cadena de pruebas. La notación es matemática forense operacionalizada, no misticismo.

---

## РУССКИЙ

### Что это за модуль?
Этот файл — **Независимый верификатор EBS v1**, автономный инструмент аудита из судебно-экспертного комплекса VIGIA. Простым языком: это внешний инспектор, который читает цифровой пакет доказательств и проверяет, соответствует ли каждая пломба, метка и измерение стандарту EBS версии 1. Главное — он не доверяет программному обеспечению, изначально создавшему пакет. Он несёт собственную копию каждого правила и порога и работает только на базовых инструментах, входящих в состав Python. Это означает, что любой независимый учёный или судебный эксперт может запустить его на любом компьютере с Python 3.6 или новее без установки дополнительного ПО.

### Компоненты модуля

| Имя | Назначение |
|---|---|
| `verify_bundle()` | Выполняет полную проверку одного пакета доказательств. |
| `main()` | Предоставляет интерфейс командной строки для немедленного использования. |
| `VerificationResult` | Структурированный журнал, хранящий каждый успех, предупреждение и сбой, выявленные при аудите. |
| `add()` | Фиксирует отдельное наблюдение в журнале результатов. |
| `critical_failures()` | Извлекает только те наблюдения, которые делают пакет научно или юридически недействительным. |
| `to_dict()` | Преобразует журнал результатов в простую структурированную карту данных. |
| `to_json()` | Преобразует журнал результатов в стандартизированную текстовую строку JSON для обмена. |
| `_EBS_VERSION` | Точная версия стандарта EBS, применяемая данным скриптом. |
| `_EBS_SUPPORTED_VERSIONS` | Все версии стандарта, признанные допустимыми. |
| `_VERIFIER_VERSION` | Внутренний номер ревизии самого верификатора. |
| `TOL` | Целочисленный порог допуска для проверки границ; отклонения измеряются относительно этого точного целого числа. |

### Ключевые понятия

| Понятие | Объяснение простым языком |
|---|---|
| **Полная независимость** | Верификатор никогда не импортирует код основной системы VIGIA. Все константы намеренно продублированы здесь, чтобы аудит нельзя было подвергнуть влиянию производственной среды. |
| **Детерминированная целочисленная арифметика** | Все числовые сравнения выполняются точными операциями над целыми числами. Дробных приближений нет, что гарантирует идентичные результаты на любой машине. |
| **Локальные константы** | Правила и пороги жёстко скопированы в этот файл. Если оригинальный производственный код изменится, данный верификатор всё равно применит известный стандарт. |
| **Критический сбой** | Дефект, достаточно серьёзный для разрыва цепочки хранения или нарушения научной воспроизводимости. |
| **Экспорт в JSON** | Универсальный текстовый формат, позволяющий другим системам прочитать вердикт без знания Python. |

### Глоссарий

- **EBS (Стандарт пакета доказательств)**: Протокол, определяющий, как цифровые судебные артефакты должны упаковываться, маркироваться и связываться с метаданными.
- **Stdlib (Стандартная библиотека)**: Встроенный набор инструментов, поставляемый с Python. Поскольку используются только они, дополнительная установка ПО не требуется.
- **Верификатор**: Независимый аудитор, проверяющий доказательства без доверия к коду первоначального автора.
- **Пакет (Bundle)**: Структурированный контейнер, содержащий один или несколько файлов цифровых доказательств вместе с их описательными метаданными.
- **Детерминированный**: Процесс, который при повторении тех же входных данных и условий даёт точно такой же результат.
- **Допуск (TOL)**: Предельное целочисленное значение. Измерение должно превысить это точное целое число, прежде чем оно будет отмечено как аномалия.

### 【Научное примечание】
Термины, заимствованные из семиотики—такие как категории **Пирса**, коды **Эко** (艾柯) и максима **Грайса** (格赖斯)—используются в комплексе VIGIA как аналитические датчики, а не как метафизические или мистические доктрины. Воспринимайте их как лабораторные приборы: как спектрометр назначает точные длины волн химическим сигналам, эти терминологические рамки назначают точные координ
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

## 中文

### 这是什么模块？

本文件是**独立 EBS v1 验证器**，VIGÍA 取证套件中的独立审计工具。用非编程语言描述：它是一个外部检查员，读取数字证据包并验证其中每个封印、标签和测量值是否遵循 EBS 第 1 版标准。关键在于，它不信任最初创建该包的软件。它自带每条规则和阈值的副本，并且仅使用 Python 预装的基本工具运行。

这意味着任何独立科学家或法院指定专家均可在装有 Python 3.6 或更新版本的任何计算机上运行它，无需安装其他软件。所有数值比较均使用整数的精确操作——无分数近似，确保在任何机器上产生相同结果。本地常数（规则和阈值）被硬编码到此文件中：即使原始生产代码发生变化，本验证器仍然应用已知标准。

皮尔斯（Peirce）的类别、艾柯（Eco）的代码和格赖斯（Grice）的准则在 VIGÍA 套件中用作分析传感器，而非形而上学或神秘主义学说。当验证器报告"违反合作原则"时，功能上等同于传感器记录越限电压——目的是检测证据链中的**逻辑断裂**。

### 关键概念

| 概念 | 定义 | 技术作用 |
|---|---|---|
| **完全独立性** | 验证器从不从主 VIGÍA 系统导入代码 | 所有常数在此处有意复制，使审计不受生产环境影响 |
| **确定性整数运算** | 每次数值比较使用整数的精确操作 | 无分数近似，确保在任何机器上产生相同结果 |
| **本地常数** | 规则和阈值硬编码到此文件中 | 即使原始生产代码更改，此验证器仍应用已知标准 |
| **关键失败** | 足以破坏监管链或损害科学可重现性的严重缺陷 | 通过 `critical_failures()` 提取，可直接触发证据包无效 |
| **JSON 导出** | 通用文本格式，允许其他系统在不理解 Python 的情况下读取裁决 | `to_json()` 实现跨系统的标准化结果交换 |
| **容差（TOL）** | 用于边界检查的整数限制；偏差相对此精确整数测量 | 超过 TOL 才标记为异常；整数表示确保精确边界 |
| **EBS（证据包标准）** | 定义数字取证工件如何打包、标记和链接至元数据的协议 | 本验证器强制执行 EBS v1 规范的所有约束 |

> **【科学说明】**
> 皮尔斯（Peirce）、艾柯（Eco）和格赖斯（Grice）的术语并非神秘主义，而是形式化的分析机制。如同光谱仪将光子相互作用转换为离散整数计数，本模块将证据信号转换为确定性整数分数。精确整数运算确保法庭可重现性，不依赖浮点近似。取证工件链的逻辑断裂以整数标志事件的形式被检测，而非直觉判断。这些术语框架将精确坐标分配给证据包内通信结构——与光谱仪将精确波长分配给化学信号完全相同。

### 词汇表

1. **EBS（证据包标准）** — 定义数字取证工件如何打包、标记和链接至元数据的协议。
2. **标准库（Stdlib）** — Python 内置工具集；本验证器仅使用标准库，无需安装额外软件。
3. **验证器** — 不依赖原始作者代码审计证据的独立检查器；可重现性的保障。
4. **证据包（Bundle）** — 包含一个或多个数字证据文件及其描述性元数据的结构化容器。
5. **确定性整数运算** — 使用整数精确操作的过程，对相同输入和条件产生完全相同的结果。
6. **容差（TOL）** — 整数边界值；测量必须超过此精确整数才被标记为异常。
7. **取证工件** — 任何受证据审查的数字对象；本模块验证其封装标准的合规性。
8. **逻辑断裂** — 证据链中的不连续性；由验证器通过整数比较确定性地检测。
9. **SHA-256 哈希链** — 将证据包内容密码学绑定至监管链的不可篡改机制。
10. **法证可重现性** — 对于相同证据包，在任意 Python 3.6+ 环境中运行验证器产生相同审计结果的属性。

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
