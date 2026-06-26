<!--
VIGIA Academic Documentation
Module: c477932e
Batch ID: vigia-doc-0141-c477932e
Generated: 2026-05-20T14:56:47.874857+00:00
-->

---

## ENGLISH

### What Is This Module?
`vigia/sift/shellbag_analyzer.py` is a deterministic forensic processor for Windows shellbag artifacts. Shellbags are residual registry records stored inside the user's `NTUSER.DAT` hive. Even if a folder is later deleted, these traces persist and document which directories the user opened in Windows Explorer. The module ingests the raw hive—via the RegRipper engine or the `regipy` library—and emits structured, auditable evidence. Its primary investigative function is to reveal access to sensitive paths that a subject may subsequently deny. To guarantee exact reproducibility, every numeric value in the evidence dictionary is represented as a rational constant (`Fraction`) or an exact string; floating-point approximations are strictly excluded.

### Key Concepts

**Table 1 — Core Components**
| Component | Function | Scientific Analogy |
|---|---|---|
| `ShellbagRecord` | One immutable entry representing a single folder visit. | A numbered page in a bound laboratory notebook. |
| `ShellbagAnalysisResult` | A deterministic, aggregated container for all records recovered from one hive. | A sealed case file containing every slide from one specimen. |
| `ShellbagAnalyzer` | The extraction engine that reads `NTUSER.DAT` and produces records. | A microscope coupled to a digital stage recorder. |
| `to_signal()` | Transforms a raw shellbag entry into a normalized forensic signal. | Calibrating a sensor so that voltage maps exactly to temperature. |
| `analyze_hive()` | The entry point that opens the hive and orchestrates the parsing workflow. | Automated sample mounting and raster scanning. |

**Table 2 — Constants & Configuration**
| Constant | Purpose | Deterministic Property |
|---|---|---|
| `TOOL_NAME` | Canonical identifier for the parser in chain-of-custody logs. | Fixed alphanumeric string; zero ambiguity. |
| `ARTIFACT_RELIABILITY` | A qualitative confidence level assigned to shellbag provenance. | Encoded as an integer tier; no fractional drift between runs. |
| `SENSITIVE_FOLDER_PATTERNS` | Curated path signatures (e.g., cryptographic wallets, obfuscation utilities) that trigger investigative flags. | Exact string matching against deterministic integer indices. |

### Glossary
1. **Shellbag** — A Windows Explorer UI persistence structure stored in the Registry. It remembers folder view settings and, forensically critical, proves that navigation occurred.
2. **NTUSER.DAT** — The user-specific Windows Registry hive that contains profile settings and activity artifacts.
3. **Hive** — The binary file format Windows uses to store Registry trees.
4. **Deterministic Integer Arithmetic** — The exclusive use of exact whole-number or rational-number representations (via the `Fraction` type and string serialization) so that every repeated analysis yields bit-identical results.
5. **Forensic Signal** — A normalized, interpreted evidence unit derived from a raw artifact, suitable for correlation with signals from other modules.
6. **Registry Key / Value** — Hierarchical data containers inside a hive; shellbags reside at predictable paths such as `Software\Microsoft\Windows\Shell\BagMRU`.
7. **Logical Fracture** — A deterministic inconsistency between a subject's statement and the fact established by a forensic artifact; this module reveals such fractures via shellbag records.
8. **Sensitive Folder Pattern** — A predefined string pattern used to identify access to high-risk directories (e.g., cryptocurrency wallets, anti-forensic tools).

### 【Scientific Note】
Peircean semiotics, Eco's theory of signs, and Gricean implicature are not metaphysical speculation. In digital forensics they operate exactly like the interpretive firmware of a calibrated scientific instrument. The raw magnetic orientation on a platter is the **object** (Peirce); the shellbag parser that translates magnetic states into a folder path is the **sign**; the examiner's conclusion that a user accessed a sensitive directory is the **interpretant**. Eco's thresholds tell us when a cluster of registry bytes ceases to be noise and becomes a meaningful forensic artifact. Grice's maxims ensure that when the module reports a path, it does so with the cooperative clarity of a certified sensor readout—no more, no less. Rejecting this framework as "mysticism" is equivalent to discarding a spectrometer's calibration curve because one dislikes the unit printed on the axis.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## ESPAÑOL

### ¿Qué es este módulo?
`vigia/sift/shellbag_analyzer.py` es un procesador forense determinista para artefactos shellbag de Windows. Los shellbags son registros residuales del Registro almacenados en la hive `NTUSER.DAT` de cada usuario. Incluso si una carpeta se elimina posteriormente, estas trazas persisten y documentan qué directorios abrió el usuario en el Explorador de Windows. El módulo consume la hive en bruto —mediante el motor RegRipper o la biblioteca `regipy`— y produce evidencia estructurada y auditable. Su función investigativa principal consiste en revelar accesos a rutas sensibles que el sujeto pueda negar después. Para garantizar la reproducibilidad exacta, cada valor numérico en el diccionario de evidencias se representa como una constante racional (`Fraction`) o una cadena exacta; las aproximaciones de punto flotante están estrictamente excluidas.

### Conceptos clave

**Tabla 1 — Componentes principales**
| Componente | Función | Analogía científica |
|---|---|---|
| `ShellbagRecord` | Una entrada inmutable que representa una única visita a una carpeta. | Una página numerada en un cuaderno de laboratorio encuadernado. |
| `ShellbagAnalysisResult` | Contenedor determinista y agregado de todos los registros recuperados de una hive. | Un expediente sellado que contiene todas las diapositivas de un espécimen. |
| `ShellbagAnalyzer` | Motor de extracción que lee `NTUSER.DAT` y produce registros. | Un microscopio acoplado a un grabador digital de etapa. |
| `to_signal()` | Transforma una entrada shellbag cruda en una señal forense normalizada. | Calibrar un sensor para que el voltaje se mapee exactamente a temperatura. |
| `analyze_hive()` | Punto de entrada que abre la hive y orquesta el flujo de trabajo de parseo. | Montaje automatizado de muestra y escaneado rasster. |

**Tabla 2 — Constantes y configuración**
| Constante | Propósito | Propiedad determinista |
|---|---|---|
| `TOOL_NAME` | Identificador canónico del analizador en los registros de cadena de custodia. | Cadena alfanumérica fija; ambigüedad cero. |
| `ARTIFACT_RELIABILITY` | Nivel de confianza cualitativo asignado a la procedencia shellbag. | Codificado como nivel entero; sin deriva fraccional entre ejecuciones. |
| `SENSITIVE_FOLDER_PATTERNS` | Firmas de rutas curadas (p. ej., carteras criptográficas, utilidades de ofuscación) que activan banderas de investigación. | Coincidencia exacta de cadenas contra índices enteros deterministas. |

### Glosario
1. **Shellbag** — Estructura de persistencia de la interfaz del Explorador de Windows almacenada en el Registro. Recuerda la configuración de vista de carpetas y, crucialmente para la forense, prueba que ocurrió la navegación.
2. **NTUSER.DAT** — La hive del Registro de Windows específica del usuario que contiene configuraciones de perfil y artefactos de actividad.
3. **Hive** — El formato de archivo binario que Windows usa para almacenar árboles del Registro.
4. **Aritmética entera determinista** — El uso exclusivo de representaciones de números enteros o racionales exactos (mediante el tipo `Fraction` y serialización en cadena de texto) para que cada análisis repetido produzca resultados bit a bit idénticos.
5. **Señal forense** — Unidad de evidencia normalizada e interpretada derivada de un artefacto crudo, adecuada para correlación con señales de otros módulos.
6. **Clave/Valor del Registro** — Contenedores de datos jerárquicos dentro de una hive; los shellbags residen en rutas predecibles como `Software\Microsoft\Windows\Shell\BagMRU`.
7. **Fractura lógica** — Inconsistencia determinista entre la declaración de un sujeto y el hecho establecido por un artefacto forense; este módulo revela tales fracturas mediante registros shellbag.
8. **Patrón de carpeta sensible** — Patrón de cadena predefinido para identificar el acceso a directorios de alto riesgo (p. ej., carteras de criptomonedas, herramientas anti-forenses).

### 【Nota Científica】
La semiótica peirceana, la teoría de los signos de Eco y la implicatura griceana no son especulación metafísica. En la forense digital operan exactamente como el firmware interpretativo de un instrumento científico calibrado. La orientación magnética bruta en un plato es el **objeto** (Peirce); el analizador shellbag que traduce estados magnéticos en una ruta de carpeta es el **signo**; la conclusión del examinador de que un usuario accedió a un directorio sensible es el **interpretante**. Los umbrales de Eco nos dicen cuándo un clúster de bytes del registro deja de ser ruido y se convierte en un artefacto forense significativo. Las máximas de Grice aseguran que cuando el módulo reporta una ruta, lo hace con la claridad cooperativa de una lectura de sensor certificada — ni más ni menos. Rechazar este marco como "misticismo" equivale a descartar la curva de calibración de un espectrómetro porque no agrada la unidad impresa en el eje.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## РУССКИЙ

### Что представляет собой этот модуль?
`vigia/sift/shellbag_analyzer.py` — детерминированный криминалистический процессор для артефактов shellbag Windows. Shellbag'и — это остаточные записи реестра, хранимые в hive `NTUSER.DAT` пользователя. Даже если папка впоследствии удаляется, эти следы сохраняются и документируют, какие каталоги пользователь открывал в Проводнике Windows. Модуль принимает исходную hive — через движок RegRipper или библиотеку `regipy` — и эмитирует структурированные, поддающиеся аудиту доказательства. Его основная следственная функция — выявить доступ к чувствительным путям, которые субъект может впоследствии отрицать. Для гарантии точной воспроизводимости каждое числовое значение в словаре доказательств представлено как рациональная константа (`Fraction`) или точная строка; приближения с плавающей точкой строго исключены.

### Ключевые понятия

**Таблица 1 — Основные компоненты**
| Компонент | Функция | Научная аналогия |
|---|---|---|
| `ShellbagRecord` | Одна неизменяемая запись, представляющая единственное посещение папки. | Пронумерованная страница в переплетённом лабораторном журнале. |
| `ShellbagAnalysisResult` | Детерминированный агрегированный контейнер для всех записей, извлечённых из одной hive. | Запечатанное дело, содержащее все препараты одного образца. |
| `ShellbagAnalyzer` | Движок извлечения, считывающий `NTUSER.DAT` и производящий записи. | Микроскоп, сопряжённый с цифровым предметным регистратором. |
| `to_signal()` | Преобразует необработанную запись shellbag в нормализованный криминалистический сигнал. | Калибровка датчика для точного отображения напряжения в температуру. |
| `analyze_hive()` | Точка входа, открывающая hive и оркестрирующая рабочий процесс разбора. | Автоматизированная установка образца и растровое сканирование. |

**Таблица 2 — Константы и конфигурация**
| Константа | Назначение | Детерминированное свойство |
|---|---|---|
| `TOOL_NAME` | Канонический идентификатор анализатора в журналах цепочки сохранения. | Фиксированная алфавитно-цифровая строка; нулевая неоднозначность. |
| `ARTIFACT_RELIABILITY` | Качественный уровень достоверности, присвоенный происхождению shellbag. | Кодируется как целочисленный уровень; без дробного дрейфа между запусками. |
| `SENSITIVE_FOLDER_PATTERNS` | Кураторские сигнатуры путей (напр., криптовалютные кошельки, утилиты обфускации), активирующие следственные флаги. | Точное сопоставление строк с детерминированными целочисленными индексами. |

### Глоссарий
1. **Shellbag** — Структура постоянства интерфейса Проводника Windows, хранимая в реестре. Запоминает настройки отображения папок и, что критически важно для криминалистики, доказывает факт навигации.
2. **NTUSER.DAT** — Специфическая для пользователя hive реестра Windows, содержащая настройки профиля и артефакты активности.
3. **Hive** — Двоичный формат файла, используемый Windows для хранения деревьев реестра.
4. **Детерминированная целочисленная арифметика** — Исключительное использование точных целочисленных или рациональных представлений (через тип `Fraction` и строковую сериализацию), чтобы каждый повторный анализ давал побитово идентичные результаты.
5. **Криминалистический сигнал** — Нормализованная, интерпретированная доказательственная единица, производная от необработанного артефакта, пригодная для корреляции с сигналами других модулей.
6. **Ключ/Значение реестра** — Иерархические контейнеры данных внутри hive; shellbag'и находятся по предсказуемым путям типа `Software\Microsoft\Windows\Shell\BagMRU`.
7. **Логический разрыв** — Детерминированная непоследовательность между заявлением субъекта и фактом, установленным криминалистическим артефактом; данный модуль выявляет такие разрывы через shellbag-записи.
8. **Паттерн чувствительной папки** — Предопределённый строковый паттерн для идентификации доступа к высокорисковым каталогам (напр., криптовалютные кошельки, антикриминалистические инструменты).

### 【Научное примечание】
Семиотика Пирса, теория знаков Эко и импликатура Грайса — не метафизические спекуляции. В цифровой криминалистике они действуют точно так же, как интерпретативная прошивка откалиброванного научного прибора. Исходная магнитная ориентация на диске — это **объект** (Пирс); shellbag-анализатор, переводящий магнитные состояния в путь к папке, — это **знак**; вывод эксперта о том, что пользователь получил доступ к чувствительному каталогу, — это **интерпретант**. Пороги Эко указывают нам, когда кластер байт реестра перестаёт быть шумом и становится значимым криминалистическим артефактом. Максимы Грайса гарантируют, что когда модуль сообщает путь, он делает это с кооперативной ясностью показания сертифицированного датчика — ни больше ни меньше. Отвергать эту рамку как «мистицизм» равносильно отказу от калибровочной кривой спектрометра лишь потому, что не нравится единица, напечатанная на оси.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## 中文

### 本模块是什么？
`vigia/sift/shellbag_analyzer.py` 是一个针对 Windows shellbag 取证工件的确定性取证处理器。Shellbags 是存储在用户 `NTUSER.DAT` 注册表蜂巢（hive）中的残留注册表记录。即使文件夹随后被删除，这些痕迹依然保留并记录了用户在 Windows 资源管理器中打开了哪些目录。模块通过 RegRipper 引擎或 `regipy` 库摄入原始蜂巢，并发出结构化的可审计证据。其主要调查功能是揭示受调查对象可能随后否认的敏感路径访问行为。为保证精确可重现性，证据字典中的每个数值均表示为有理数常量（`Fraction`）或精确字符串；严格排除浮点近似。

### 核心概念

**表 1 — 核心组件**
| 组件 | 功能 | 科学类比 |
|---|---|---|
| `ShellbagRecord` | 表示单次文件夹访问的一个不可变条目。 | 装订实验室笔记本中的一页编号页面。 |
| `ShellbagAnalysisResult` | 从一个蜂巢中恢复的所有记录的确定性聚合容器。 | 包含一份标本所有切片的密封案例档案。 |
| `ShellbagAnalyzer` | 读取 `NTUSER.DAT` 并产生记录的提取引擎。 | 与数字载台记录仪耦合的显微镜。 |
| `to_signal()` | 将原始 shellbag 条目转换为规范化的取证信号。 | 校准传感器使电压精确映射至温度。 |
| `analyze_hive()` | 打开蜂巢并编排解析工作流的入口点。 | 自动化样本安装和光栅扫描。 |

**表 2 — 常量与配置**
| 常量 | 用途 | 确定性属性 |
|---|---|---|
| `TOOL_NAME` | 监管链日志中解析器的规范标识符。 | 固定字母数字字符串；零歧义。 |
| `ARTIFACT_RELIABILITY` | 分配给 shellbag 来源的定性置信水平。 | 编码为整数层级；运行间无分数漂移。 |
| `SENSITIVE_FOLDER_PATTERNS` | 触发调查标志的精选路径特征（如密码钱包、混淆工具）。 | 针对确定性整数索引的精确字符串匹配。 |

### 术语表
1. **Shellbag** — 存储在注册表中的 Windows 资源管理器 UI 持久性结构。它记住文件夹视图设置，并且对取证至关重要——证明发生了导航行为。
2. **NTUSER.DAT** — 包含用户配置文件设置和活动取证工件的用户特定 Windows 注册表蜂巢。
3. **蜂巢（Hive）** — Windows 用于存储注册表树的二进制文件格式。
4. **确定性整数算术** — 专门使用精确整数或有理数表示（通过 `Fraction` 类型和字符串序列化），使每次重复分析产生位相同结果。
5. **取证信号** — 从原始取证工件派生的规范化、已解释证据单元，适合与其他模块的信号进行关联。
6. **注册表键/值** — 蜂巢内的层次数据容器；shellbags 位于可预测的路径，如 `Software\Microsoft\Windows\Shell\BagMRU`。
7. **逻辑断裂** — 受调查对象陈述与取证工件确立的事实之间的确定性不一致；本模块通过 shellbag 记录揭示此类断裂。
8. **敏感文件夹模式** — 用于识别访问高风险目录（如加密货币钱包、反取证工具）的预定义字符串模式。

### 【科学说明】
皮尔斯语义学、艾柯的符号理论和格赖斯的含义推导不是形而上学推测。在数字取证中，它们的功能与经校准科学仪器的解释固件完全相同。盘片上的原始磁性定向是**对象**（皮尔斯）；将磁性状态翻译为文件夹路径的 shellbag 解析器是**符号**；检查员关于用户访问敏感目录的结论是**解释项**。艾柯的阈值告诉我们，注册表字节的某个集群何时不再是噪声，而成为有意义的取证工件。格赖斯的准则确保模块报告路径时，以经认证传感器读数的合作清晰度进行报告——不多也不少。将这一框架斥为"神秘主义"，相当于因不喜欢轴上印的单位就丢弃质谱仪的校准曲线。

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
