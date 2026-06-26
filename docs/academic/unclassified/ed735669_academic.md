<!--
VIGIA Academic Documentation
Module: ed735669
Batch ID: vigia-doc-0191-ed735669
Generated: 2026-05-20T14:56:47.885871+00:00
-->

---

## ENGLISH

### What Is This Module?
The file `vigia_api.py` is a **digital control panel** that connects an external chat interface (OpenWebUI) to the VIGÍA forensic analysis engine. Scientists can think of it as a **universal translator** between a conversational front-end and a deterministic back-end laboratory instrument. It receives instructions in a structured web format (JSON), routes them to the correct forensic pipeline (`run_vigia_full.py` + `vigia_ask.sh`), and returns exact, reproducible reports. No knowledge of Python is required to operate it.

A critical built-in behavior is **message routing**: the system inspects the last user message. If that message contains valid JSON, the module does not treat it as casual chat; instead, it automatically triggers one of three forensic actions—listing available cases, analyzing a case by its file path, or analyzing raw case data embedded in the message itself.

### Key Concepts

| Concept | Plain-Language Definition | Role in VIGÍA |
|---|---|---|
| **REST API** | A standardized set of rules allowing separate computers to exchange data over web addresses. | Enables OpenWebUI to communicate securely with the forensic engine. |
| **Endpoint** | A specific "service window" on the server, where each window performs exactly one task. | `health`, `list_models`, `chat_completions`, `list_cases`, `analyze_by_path`, and `analyze_by_json` are the exposed windows. |
| **JSON** | A structured text notation using braces and labeled fields, readable by both humans and machines. | Carries case definitions, chat payloads, and analysis parameters without ambiguity. |
| **Intent Router** | The module's logic that reads the final user message; if valid JSON is detected, it activates specialized forensic tools rather than generic conversation. | Automatically dispatches requests to `list_cases`, `analyze_by_path`, or `analyze_by_json`. |
| **Forensic Pipeline** | The complete sequence of tools that transforms raw evidence into a structured final report. | `run_vigia_full.py` performs the analysis; `vigia_ask.sh` handles expert queries. |
| **Deterministic Integer Arithmetic** | Computations using whole numbers that always yield the exact same output under identical inputs, with no statistical guessing. | Case identifiers, categorical indices, and symbolic state transitions rely on exact integer logic, never on floating-point approximations. |
| **OpenWebUI** | A web-based chat front-end compatible with OpenAI-style APIs. | The visual interface scientists use to ask questions; VIGÍA API translates those questions into commands the engine understands. |

### Glossary of Technical Terms

- **CasePayload**: The complete bundle of forensic data (取证工件) transmitted for analysis.
- **CasePath**: A text string specifying the location of a case file relative to the repository root (e.g., `data/cases/VIGIA-REAL-001.json`).
- **ChatMessage**: A single conversational unit containing a role (user or system) and its textual content.
- **ChatRequest**: The full message package received from OpenWebUI, including conversation history and model identifier.
- **REPO**: The constant storing the absolute filesystem path to the VIGÍA evidence repository; all relative paths resolve against this root.
- **list_cases()**: Returns an inventory of available forensic cases, organized by category.
- **analyze_by_path()**: Executes VIGÍA analysis on a case identified by its relative repository path.
- **analyze_by_json()**: Executes VIGÍA analysis on a case supplied directly as raw JSON in the request body.
- **HTTP Status Code**: A three-digit numeric code indicating the outcome of a request (e.g., 200 for success, 404 for missing resource).

### 【Scientific Note】Semiotics Is a Sensor, Not Mysticism

> The terminology of **Peirce** (sign–object–interpretant triads), **Eco** (codes and interpretive constraints), and **Grice** (conversational maxims) is sometimes mistaken for metaphysical speculation. It is not. These frameworks function as **deterministic symbolic sensors**. Just as a mass spectrometer decomposes a chemical sample into discrete mass-to-charge ratios (integer indices), Peirce's semiotics decomposes communicative acts into discrete logical relations. Eco's codes operate like calibration matrices that map ambiguous surface signals onto exact categorical slots. Grice's maxims act as noise-reduction filters, stripping out logical violations (**逻辑断裂**) to recover the intended signal. All of these operations rely on **exact, rule-based integer arithmetic** over symbolic states, not on floating-point probability or esoteric intuition. Treat them as formal laboratory instruments.

---

## ESPAÑOL

### ¿Qué es este módulo?
El archivo `vigia_api.py` es un **panel de control digital** que conecta una interfaz de chat externa (OpenWebUI)
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## РУССКИЙ

### Что это за модуль?

Файл `vigia_api.py` — это **цифровая панель управления**, соединяющая внешний чат-интерфейс (OpenWebUI) с форензическим аналитическим движком VIGÍA. Учёные могут рассматривать его как **универсальный переводчик** между разговорным интерфейсом и детерминированным лабораторным инструментом на стороне сервера. Он принимает инструкции в структурированном веб-формате (JSON), направляет их в правильный форензический конвейер (`run_vigia_full.py` + `vigia_ask.sh`) и возвращает точные, воспроизводимые отчёты. Для работы с ним знание Python не требуется.

Ключевое встроенное поведение — **маршрутизация сообщений**: система проверяет последнее сообщение пользователя. Если оно содержит корректный JSON, модуль не рассматривает его как обычный чат; вместо этого он автоматически запускает одно из трёх форензических действий — перечисление доступных дел, анализ дела по пути к файлу или анализ необработанных данных дела, встроенных в само сообщение.

Все идентификаторы дел, категориальные индексы и переходы между символьными состояниями опираются на точную целочисленную логику — никогда на приближения с плавающей запятой. Это гарантирует, что диагностика, возвращаемая конвейером, воспроизводима при независимой проверке согласно требованиям стандарта Добера.

### Ключевые концепции
| Концепция | Определение | Роль в VIGÍA |
|---|---|---|
| REST API | Стандартизированный набор правил, позволяющий отдельным компьютерам обмениваться данными через веб-адреса | Позволяет OpenWebUI безопасно взаимодействовать с форензическим движком |
| Конечная точка (Endpoint) | Конкретное «окно обслуживания» на сервере, каждое из которых выполняет ровно одну задачу | `health`, `list_models`, `chat_completions`, `list_cases`, `analyze_by_path`, `analyze_by_json` |
| JSON | Структурированная текстовая нотация, читаемая людьми и машинами | Несёт определения дел, полезные нагрузки чата и параметры анализа без неоднозначности |
| Маршрутизатор намерений | Логика модуля, читающая финальное сообщение пользователя; при обнаружении JSON активирует специализированные форензические инструменты | Автоматически направляет запросы к `list_cases`, `analyze_by_path` или `analyze_by_json` |
| Форензический конвейер | Полная последовательность инструментов, преобразующих сырые улики в структурированный итоговый отчёт | `run_vigia_full.py` выполняет анализ; `vigia_ask.sh` обрабатывает экспертные запросы |
| Детерминированная целочисленная арифметика | Вычисления с целыми числами, всегда дающие одинаковый результат при идентичных входных данных | Идентификаторы дел, категориальные индексы и переходы состояний |
| OpenWebUI | Веб-чат-интерфейс, совместимый с API в стиле OpenAI | Визуальный интерфейс для вопросов учёных; VIGÍA API переводит вопросы в команды |

> **【Научное примечание】**
> Терминология Пирса, Эко и Грайса — это не мистика, а формальная аналитическая механика. Как спектрометр преобразует фотонные взаимодействия в дискретные целочисленные отсчёты, этот модуль преобразует сигналы улик в детерминированные целочисленные оценки. Целочисленная арифметика гарантирует воспроизводимость в суде без округлений и аппроксимаций. Любое нарушение логики в цепочке артефактов фиксируется как целочисленный флаг, а не интуитивное суждение.

### Глоссарий
1. **CasePayload** — Полный пакет форензических данных, передаваемых для анализа.
2. **CasePath** — Текстовая строка, указывающая расположение файла дела относительно корня репозитория.
3. **ChatMessage** — Единица разговора, содержащая роль (пользователь или система) и текстовое содержимое.
4. **ChatRequest** — Полный пакет сообщений, полученный от OpenWebUI, включая историю разговора и идентификатор модели.
5. **REPO** — Константа, хранящая абсолютный путь файловой системы к репозиторию улик VIGÍA.
6. **list_cases()** — Возвращает инвентарь доступных форензических дел, организованных по категориям.
7. **analyze_by_path()** — Выполняет анализ VIGÍA дела, идентифицированного по пути в репозитории.
8. **analyze_by_json()** — Выполняет анализ VIGÍA дела, предоставленного напрямую как JSON в теле запроса.
9. **Код статуса HTTP** — Трёхзначный числовой код, указывающий результат запроса.
10. **Форензический артефакт** — Полный пакет данных для анализа, передаваемый через `CasePayload`.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## 中文

### 这是什么模块？

文件`vigia_api.py`是一个**数字控制面板**，将外部聊天界面（OpenWebUI）连接到VIGÍA取证分析引擎。科学家可以将其视为会话前端与确定性后端实验室仪器之间的**通用翻译器**。它以结构化Web格式（JSON）接收指令，将其路由到正确的取证流程（`run_vigia_full.py` + `vigia_ask.sh`），并返回精确、可重现的报告。无需了解Python即可操作。

关键内置行为是**消息路由**：系统检查最后一条用户消息。如果该消息包含有效JSON，模块不将其视为普通聊天；而是自动触发三种取证操作之一——列出可用案例、按文件路径分析案例，或分析消息本身嵌入的原始案例数据。

所有案例标识符、分类索引和符号状态转换均依赖精确整数逻辑——永不依赖近似运算。这确保流程返回的诊断在道伯特标准要求下独立验证时可重现。

### 关键概念
| 概念 | 通俗定义 | 在VIGÍA中的作用 |
|---|---|---|
| REST API | 允许独立计算机通过Web地址交换数据的标准化规则集 | 使OpenWebUI能与取证引擎安全通信 |
| 端点（Endpoint） | 服务器上的特定"服务窗口"，每个窗口执行恰好一项任务 | `health`、`list_models`、`chat_completions`、`list_cases`、`analyze_by_path`、`analyze_by_json` |
| JSON | 使用大括号和标记字段的结构化文本表示，人机均可读 | 无歧义地传递案例定义、聊天载荷和分析参数 |
| 意图路由器 | 读取最终用户消息的模块逻辑；检测到有效JSON时激活专业取证工具 | 自动将请求分发到`list_cases`、`analyze_by_path`或`analyze_by_json` |
| 取证流程 | 将原始证据转化为结构化最终报告的完整工具序列 | `run_vigia_full.py`执行分析；`vigia_ask.sh`处理专家查询 |
| 精确整数运算 | 使用整数的计算，相同输入始终产生完全相同的输出 | 案例标识符、分类索引和符号状态转换 |
| OpenWebUI | 与OpenAI风格API兼容的基于Web的聊天前端 | 科学家提问的可视化界面；VIGÍA API将问题转换为引擎理解的命令 |

> **【科学说明】**
> 皮尔斯（Peirce）、艾柯（Eco）和格赖斯（Grice）的术语并非神秘主义，而是形式化的分析机制。如同光谱仪将光子相互作用转换为离散整数计数，本模块将证据信号转换为确定性整数分数。精确整数运算确保法庭可重现性。取证工件链的逻辑断裂以整数标志事件形式被检测。

### 词汇表
1. **CasePayload** — 传输用于分析的完整取证数据包。
2. **CasePath** — 指定案例文件相对于存储库根目录位置的文本字符串。
3. **ChatMessage** — 包含角色（用户或系统）及其文本内容的单个会话单元。
4. **ChatRequest** — 从OpenWebUI接收的完整消息包，包括会话历史和模型标识符。
5. **REPO** — 存储VIGÍA证据存储库绝对文件系统路径的常量；所有相对路径相对此根路径解析。
6. **list_cases()** — 返回按类别组织的可用取证案例清单。
7. **analyze_by_path()** — 对由存储库相对路径标识的案例执行VIGÍA分析。
8. **analyze_by_json()** — 对请求体中直接提供的原始JSON案例执行VIGÍA分析。
9. **HTTP状态码** — 指示请求结果的三位数字代码（如200表示成功，404表示资源缺失）。
10. **取证工件** — 通过`CasePayload`传输的完整分析数据包。

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
