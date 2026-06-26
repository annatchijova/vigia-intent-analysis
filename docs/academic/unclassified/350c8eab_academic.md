<!--
VIGIA Academic Documentation
Module: 350c8eab
Batch ID: vigia-doc-0131-350c8eab
Generated: 2026-05-20T14:56:47.872778+00:00
-->

---

## ENGLISH

### What Is This Module?
This module is a digital forensics instrument. It treats web browser artifacts—history logs, download records, cookies, and cache files—as empirical evidence in a scientific investigation. Its purpose is to reconstruct user actions, detect the download of attack tools, identify navigation to command-and-control (C2) domains, and correlate these findings with network activity logs. The module operates as a deterministic system: every quantitative value is stored as an exact rational number (`Fraction`) or as its string representation, never as an imprecise approximation. This guarantees that repeated analyses of identical data produce bit-for-bit identical results.

### Key Concepts

| Name | Type | Scientific Role |
|---|---|---|
| `BrowserDownloadRecord` | Data Template | A single file-download event: timestamp, origin URL, local path, cryptographic hash. Analogous to a specimen label in a physical laboratory. |
| `BrowserHistoryRecord` | Data Template | A single URL-visit event: timestamp, page title, navigation type. Analogous to a chronological entry in a field notebook. |
| `BrowserAnalysisResult` | Data Container | The final aggregated report. Holds correlated events, reliability metrics (as exact fractions), and interpretive conclusions. |
| `BrowserForensicsEngine` | Analytical Instrument | The main apparatus. Accepts a browser user profile (Chrome, Edge, or Firefox) and executes a systematic examination. |

| Name | Type | Scientific Role |
|---|---|---|
| `to_signal()` | Conversion Procedure | Normalizes a raw browser entry into a standardized evidence signal. Like converting an analog sensor voltage into a calibrated digital reading. |
| `analyze_profile()` | Pipeline Procedure | Runs the full analytical workflow on a browser profile directory. Outputs a `BrowserAnalysisResult`. |

| Name | Type | Scientific Role |
|---|---|---|
| `TOOL_NAME` | Identifier String | Name tag for the engine instance, ensuring traceability in multi-instrument workflows. |
| `ARTIFACT_RELIABILITY` | Reliability Matrix | Coded reference table indicating the level of trust assigned to each source category. |
| `MALICIOUS_DOMAINS` | Reference Set | Deterministic lookup table of known hostile hostnames. |
| `SUSPICIOUS_EXTENSIONS` | Reference Set | Deterministic lookup table of file extensions commonly associated with attack tools. |

### Deterministic Arithmetic
All numerical values placed into the evidence dictionary use exact rational arithmetic (`Fraction` objects or their string equivalents). Timestamps, ratios, and reliability scores are therefore represented as pairs of integers (numerator/denominator). This approach eliminates irreproducibility and is scientifically equivalent to retaining all measurements in exact rational form until final reporting.

### Glossary
1. **Browser Profile** — A directory containing all user-specific data for a given browser installation.
2. **Command-and-Control (C2) Domain** — A server hostname used by malware to receive instructions and exfiltrate data.
3. **Cryptographic Hash** — A deterministic fixed-length fingerprint of a file's content, used to verify integrity.
4. **Deterministic System** — A process where identical inputs always produce identical outputs.
5. **Download Record** — A logged event capturing the retrieval of a file from the internet.
6. **Evidence Signal** — A normalized numerical representation of a raw artifact for quantitative analysis.
7. **Forensic Artifact** — Any digital object that carries evidential value in an investigation.
8. **History Log** — A browser's chronological record of visited URLs.
9. **Reliability Matrix** — A table assigning confidence levels to different artifact source types.
10. **Suspicious Extension** — A file extension associated with executable attack tools (e.g., `.exe`, `.ps1`).

> **【Scientific Note】**
> Peirce/Eco/Grice terminology is NOT mysticism. In VIGÍA, a browser history entry is a Peircean *index*: a causal trace left by an action. Eco's interpretive frame distinguishes between a legitimate download and a tool-staging event. Grice's maxim of relevance is violated when a download record appears that has no plausible legitimate explanation given the surrounding context.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## ESPAÑOL

### ¿Qué es este módulo?
Este módulo es un instrumento de informática forense. Trata los artefactos de navegadores web—registros de historial, registros de descargas, cookies y archivos de caché—como evidencia empírica en una investigación científica. Su propósito es reconstruir acciones de usuarios, detectar la descarga de herramientas de ataque, identificar la navegación hacia dominios de mando y control (C2) y correlacionar estos hallazgos con registros de actividad de red. El módulo opera como un sistema determinista: todo valor cuantitativo se almacena como número racional exacto o su representación de cadena, nunca como aproximación imprecisa. Esto garantiza resultados bit a bit idénticos en análisis repetidos de datos idénticos.

### Conceptos clave

| Nombre | Tipo | Rol científico |
|---|---|---|
| `BrowserDownloadRecord` | Plantilla de datos | Evento único de descarga de archivo: marca de tiempo, URL de origen, ruta local, hash criptográfico. Análogo a una etiqueta de muestra en laboratorio físico. |
| `BrowserHistoryRecord` | Plantilla de datos | Evento único de visita a URL: marca de tiempo, título de página, tipo de navegación. Análogo a entrada cronológica en cuaderno de campo. |
| `BrowserAnalysisResult` | Contenedor de datos | Informe agregado final. Contiene eventos correlacionados, métricas de fiabilidad (como fracciones exactas) y conclusiones interpretativas. |
| `BrowserForensicsEngine` | Instrumento analítico | Aparato principal. Acepta un perfil de usuario de navegador (Chrome, Edge o Firefox) y ejecuta el examen sistemático. |
| `to_signal()` | Procedimiento de conversión | Normaliza una entrada de navegador en bruto como señal de evidencia estandarizada. Como convertir un voltaje de sensor analógico en lectura digital calibrada. |
| `analyze_profile()` | Procedimiento de canalización | Ejecuta el flujo de trabajo analítico completo sobre un directorio de perfil de navegador. |

### Aritmética Determinista
Todos los valores numéricos colocados en el diccionario de evidencia utilizan aritmética racional exacta. Las marcas de tiempo, ratios y puntuaciones de fiabilidad se representan como pares de enteros (numerador/denominador). Este enfoque elimina la irreproducibilidad y es científicamente equivalente a conservar todas las mediciones en forma racional exacta hasta el informe final.

### Glosario
1. **Perfil de Navegador** — Directorio que contiene todos los datos específicos del usuario para una instalación de navegador dada.
2. **Dominio C2 (Mando y Control)** — Nombre de host de servidor utilizado por malware para recibir instrucciones y exfiltrar datos.
3. **Hash Criptográfico** — Huella digital determinista de longitud fija del contenido de un archivo.
4. **Sistema Determinista** — Proceso donde entradas idénticas siempre producen salidas idénticas.
5. **Registro de Descarga** — Evento registrado que captura la recuperación de un archivo desde internet.
6. **Señal de Evidencia** — Representación numérica normalizada de un artefacto en bruto para análisis cuantitativo.
7. **Artefacto Forense** — Cualquier objeto digital con valor probatorio en una investigación.
8. **Registro de Historial** — Registro cronológico de URLs visitadas por un navegador.
9. **Matriz de Fiabilidad** — Tabla que asigna niveles de confianza a diferentes tipos de fuentes de artefactos.
10. **Extensión Sospechosa** — Extensión de archivo asociada con herramientas de ataque ejecutables (p. ej., `.exe`, `.ps1`).

> **【Nota Científica】**
> La terminología de Peirce/Eco/Grice no es misticismo. En VIGÍA, una entrada de historial de navegador es un *índice* peirceano: un rastro causal dejado por una acción. El marco interpretativo de Eco distingue entre una descarga legítima y un evento de preparación de herramientas. La máxima de relevancia de Grice se viola cuando aparece un registro de descarga sin explicación legítima plausible en el contexto circundante.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## РУССКИЙ

### Что это за модуль?
Данный модуль является инструментом цифровой криминалистики. Он рассматривает артефакты веб-браузеров — журналы истории, записи о загрузках, файлы cookie и кэш — как эмпирические доказательства в научном расследовании. Его цель: реконструировать действия пользователей, обнаружить загрузку инструментов атаки, идентифицировать обращения к командно-контрольным (C2) доменам и сопоставить эти данные с журналами сетевой активности. Модуль работает как детерминированная система: каждое количественное значение хранится как точное рациональное число или его строковое представление — никогда в виде неточного приближения. Это гарантирует побитовую идентичность результатов при повторных анализах одинаковых данных.

### Ключевые концепции

| Название | Тип | Научная роль |
|---|---|---|
| `BrowserDownloadRecord` | Шаблон данных | Единственное событие загрузки файла: метка времени, исходный URL, локальный путь, криптографический хеш. Аналог этикетки образца в физической лаборатории. |
| `BrowserHistoryRecord` | Шаблон данных | Единственное событие посещения URL: метка времени, заголовок страницы, тип навигации. Аналог хронологической записи в полевом дневнике. |
| `BrowserAnalysisResult` | Контейнер данных | Итоговый агрегированный отчёт. Содержит сопоставленные события, метрики надёжности и интерпретационные выводы. |
| `BrowserForensicsEngine` | Аналитический инструмент | Главный аппарат. Принимает профиль пользователя браузера (Chrome, Edge или Firefox) и выполняет систематическое исследование. |
| `to_signal()` | Процедура преобразования | Нормализует необработанную запись браузера в стандартизированный сигнал доказательств. |
| `analyze_profile()` | Процедура конвейера | Запускает полный аналитический рабочий процесс для директории профиля браузера. |

### Детерминированная арифметика
Все числовые значения в словаре доказательств используют точную рациональную арифметику. Метки времени, соотношения и оценки надёжности представлены парами целых чисел (числитель/знаменатель). Этот подход исключает невоспроизводимость и научно эквивалентен сохранению всех измерений в точной рациональной форме до финального отчёта.

### Глоссарий
1. **Профиль браузера** — Директория, содержащая все пользовательские данные для данной установки браузера.
2. **Домен C2 (командование и управление)** — Имя хоста сервера, используемого вредоносным ПО для получения инструкций и кражи данных.
3. **Криптографический хеш** — Детерминированный отпечаток фиксированной длины от содержимого файла.
4. **Детерминированная система** — Процесс, при котором одинаковые входные данные всегда дают одинаковые выходные.
5. **Запись о загрузке** — Зарегистрированное событие получения файла из интернета.
6. **Сигнал доказательств** — Нормализованное числовое представление необработанного артефакта для количественного анализа.
7. **Криминалистический артефакт** — Любой цифровой объект, обладающий доказательной ценностью в расследовании.
8. **Журнал истории** — Хронологическая запись браузером посещённых URL.
9. **Матрица надёжности** — Таблица, назначающая уровни доверия различным типам источников артефактов.
10. **Подозрительное расширение** — Расширение файла, связанное с исполняемыми инструментами атаки.

> **【Научное примечание】**
> Терминология Пирса, Эко и Грайса — не мистика. В VIGÍA запись истории браузера является пирсовым *индексом*: причинным следом, оставленным действием. Интерпретационная рамка Эко различает легитимную загрузку и событие подготовки инструментов атаки. Максима релевантности Грайса нарушается, когда запись о загрузке не имеет правдоподобного законного объяснения в окружающем контексте.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## 中文

### 这是什么模块？
本模块是一个数字取证工具。它将网络浏览器工件——历史记录日志、下载记录、Cookie 和缓存文件——视为科学调查中的实证证据。其目的是重建用户行为、检测攻击工具的下载、识别对命令与控制（C2）域名的访问，并将这些发现与网络活动日志相关联。该模块作为确定性系统运行：每个量化值均以精确有理数或其字符串形式存储，从不使用不精确的近似值。这保证了对相同数据的重复分析产生逐位相同的结果。

### 关键概念

| 名称 | 类型 | 科学作用 |
|---|---|---|
| `BrowserDownloadRecord` | 数据模板 | 单次文件下载事件：时间戳、源 URL、本地路径、加密哈希。类似于物理实验室中的样本标签。 |
| `BrowserHistoryRecord` | 数据模板 | 单次 URL 访问事件：时间戳、页面标题、导航类型。类似于野外笔记本中的时序条目。 |
| `BrowserAnalysisResult` | 数据容器 | 最终聚合报告。包含关联事件、可靠性指标（以精确分数表示）及解释性结论。 |
| `BrowserForensicsEngine` | 分析仪器 | 主装置。接受浏览器用户配置文件（Chrome、Edge 或 Firefox）并执行系统检查。 |
| `to_signal()` | 转换程序 | 将原始浏览器条目规范化为标准化证据信号。如将模拟传感器电压转换为校准的数字读数。 |
| `analyze_profile()` | 流水线程序 | 对浏览器配置文件目录运行完整分析工作流，输出 `BrowserAnalysisResult`。 |

### 词汇表
1. **浏览器配置文件** — 包含特定浏览器安装所有用户特定数据的目录。
2. **C2 域名（命令与控制）** — 恶意软件用于接收指令和窃取数据的服务器主机名。
3. **加密哈希** — 文件内容的确定性固定长度指纹，用于验证完整性。
4. **确定性系统** — 相同输入始终产生相同输出的过程。
5. **下载记录** — 捕获从互联网检索文件的记录事件。
6. **证据信号** — 原始取证工件的规范化数值表示，用于定量分析。
7. **取证工件** — 调查中具有证据价值的任何数字对象。
8. **历史日志** — 浏览器访问过的 URL 的时序记录。
9. **可靠性矩阵** — 为不同工件来源类型分配置信度的表格。
10. **可疑扩展名** — 与可执行攻击工具相关的文件扩展名（如 `.exe`、`.ps1`）。

> **【科学说明】**
> 皮尔斯、艾柯和格赖斯的术语并非神秘主义。在 VIGÍA 中，浏览器历史条目是皮尔斯意义上的*索引*：行动留下的因果痕迹。艾柯的解释框架区分合法下载与工具预置事件。当下载记录在周围上下文中没有合理合法解释时，格赖斯的相关性准则即遭到违反。

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
