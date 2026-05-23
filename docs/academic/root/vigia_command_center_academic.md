<!--
VIGIA Academic Documentation
Module: 7d593d40
Batch ID: vigia-doc-0185-7d593d40
Generated: 2026-05-20T14:56:47.884598+00:00
-->

---
doc_hash: 7d593d40
module: vigia/vigia_command_center.py
languages: [EN, ES, RU, ZH]
generated_by: moonshot-kimi-k2.6-batch-api
license: Apache-2.0
---

ENGLISH:
- Title: VIGÍA Forensic Suite — Command Center (`vigia/vigia_command_center.py`)
- What Is This Module?: Explain it's a real-time terminal dashboard (Textual User Interface) for digital forensic analysts. It watches a stream of evidence records (JSON Lines) and displays the "health" of an automated reasoning process. It shows which hypotheses are currently winning, how chaotic the network evidence is (entropy), hardware status, anomalies, chain of custody integrity, and decision tallies. Think of it as the control panel of a scientific instrument.
- Key Concepts Table:
  | Concept | Description |
  |---|---|
  | Real-time JSONL Ingestion | Reads evidence logs incrementally (deterministic byte offsets) without reloading entire files. |
  | Hypothesis Winner | The most probable investigative hypothesis selected by the VIGÍA engine, annotated with coverage (scope) and cost (resource penalty). |
  | Entropy History | A bar chart showing normalized disorder in network traffic over discrete time windows. Uses deterministic integer arithmetic from `entropy_kernel`. |
  | GPU Telemetry | Optional hardware monitoring (load, VRAM, temperature) for accelerator cards, when NVIDIA libraries are present. |
  | Chain of Custody Metrics | Cryptographic integrity checks proving evidence artifacts have not been altered since collection. |
  | Decision Tally | Count of ACCEPT/REJECT/ABSTAIN verdicts issued by the analytical engine. |
  | TUI Layout | Terminal-based visual panel arrangement; advanced grid if `textual` is installed, fallback to `rich`. |

- Component Overview Table (since they don't know Python, explain functions as "panels" or "capabilities"):
  | Capability | Purpose |
  |---|---|
  | State Manager (`VigiAState`) | Holds the current snapshot of all measurements, tallies, and ingestion pointers. |
  | Header Renderer | Displays system title and session identifiers. |
  | GPU Panel | Renders accelerator diagnostics. |
  | Hypotheses Table | Lists winning hypothesis IDs with coverage and cost. |
  | Entropy Chart | Draws historical entropy as vertical bars. |
  | Decisions Panel | Shows ACCEPT / REJECT / ABSTAIN counters. |
  | Anomalies Panel | Lists recent anomalies graded by severity. |
  | Statistics Footer | Summarizes chain-of-custody integrity and ingestion statistics. |
  | Layout Builder | Assembles panels into a coherent dashboard grid. |
  | Event Generator | Produces synthetic demo events for validation. |
  | Dashboard Runner | Main observation loop refreshing the display at fixed intervals. |
  | JSONL Ingestor | Reads new lines from evidence logs using deterministic integer byte offsets. |
  | Directory Scanner | Polls paths and triggers incremental ingestion. |

- Glossary:
  - **JSON Lines (.jsonl)**: A text format where each line is one self-contained evidence record. Safer for streaming than standard JSON because corruption on one line does not invalidate the whole file.
  - **Entropy (in forensics)**: A measure of unpredictability in a data stream. High entropy suggests encrypted, compressed, or obfuscated content; low entropy suggests plaintext or redundancy. The module uses normalized integer-based calculations.
  - **Chain of Custody**: The documented trail that establishes the integrity of evidence. Any gap or alteration is a *logical break*.
  - **Hypothesis ID**: A unique identifier assigned to a candidate explanation during forensic inference.
  - **ACCEPT/REJECT/ABSTAIN**: The three epistemic verdicts the engine can issue. ACCEPT = sufficient evidence; REJECT = falsified; ABSTAIN = insufficient information.
  - **VRAM**: Video Random Access Memory; dedicated storage on a GPU accelerator.
  - **TUI**: Text-based User Interface. Operates entirely within the terminal, requiring no graphical desktop environment.
  - **Deterministic Integer Arithmetic**: Calculations performed with whole numbers and fixed-point scaling rather than fractional approximations, guaranteeing repeatable results across runs.

- Scientific Note:
  【Scientific Note】
  This module employs terminology inspired by Charles Sanders Peirce (abductive reasoning), Umberto Eco (semiotic limits of interpretation), and H. P. Grice (cooperative maxims). These are not mystical or literary decorations. They function exactly like calibrated sensors in a laboratory instrument: Peirce’s abduction supplies the *inference trigger* (hypothesis generation), Eco’s constraints set the *measurement range* (what the system refuses to over-interpret), and Grice’s maxims act as *noise filters* on communication channels between subsystems. A physicist does not dismiss a photomultiplier tube because its manual cites quantum theory; likewise, these philosophical sensors are operationalized as strict boundary conditions on the automated reasoning process.

ESPAÑOL:
- Similar structure.
- Terms: Módulo Centro de Comando. Panel de instrumentos en terminal. Ingesta en tiempo real. Hipótesis ganadoras. Historial de entropía. Telemetría de GPU. Métricas de cadena de custodia. Contador de decisiones.
- Glossary: Líneas JSON (.jsonl), Entropía, Cadena de custodia, ID de hipótesis, ACEPTAR/RECHAZAR/ABSTENERSE, VRAM, TUI, Aritmética determinista de enteros.
- Scientific Note: 【Nota Científica】 - Explain Peirce/Eco/Grice no son misticismo. Analogía del sensor. Peirce = disparador de inferencia (abducción), Eco = rango de medición (límites semióticos), Grice = filtros de ruido (máximas cooperativas).
- License line same.

РУССКИЙ:
- Title: VIGÍA Forensic Suite — Центр управления.
- What Is This Module?: Панель управления в терминале для цифровой криминалистики. Аналог приборной панели научного оборудования.
- Key concepts: Инкрементальное чтение JSONL, Победившие гипотезы, История энтропии, Мониторинг GPU, Метрики цепочки сохранности, Счётчик решений ПРИНЯТЬ/ОТКЛОНИТЬ/ВОЗДЕРЖАТЬСЯ.
- Glossary: JSON Lines (.jsonl), Энтропия (в криминалистике), Цепочка сохранности (цепочка хранения), Идентификатор гипотезы, ПРИНЯТЬ/ОТКЛОНИТЬ/ВОЗДЕРЖАТЬСЯ, Видеопамять (VRAM), Текстовый интерфейс (TUI), Детерминированная целочисленная арифметика.
- Scientific Note: 【Научное примечание】 - Пирс/Эко/Грайс не мистика. Аналогия датчика. Пирс = триггер вывода (абдукция), Эко = диапазон измерения (семиотические ограничения), Грайс = шумовые фильтры (кооперативные максимы).
- License line.

中文:
- Must use specific terms: 艾柯 (Eco), 格赖斯 (Grice), 取证工件 (artifacts), 逻辑断裂 (breaks/gaps).
- Title: VIGÍA 取证套件 — 指挥中心 (`vigia/vigia_command_center.py`)
- What Is This Module?: 这是一个实时终端仪表板（TUI），用于数字取证分析。它将取证引擎的自动推理过程可视化，类似于科学仪器的控制面板。
- Key Concepts: 实时 JSONL 摄取, 胜出假设, 熵历史柱状图, GPU 遥测, 保管链指标, 决策计数器.
- Table with descriptions. Use 取证工件 where appropriate (e.g., in chain of custody or anomalies? Actually "artifacts" might refer to evidence artifacts = 取证工件). Use 逻辑断裂 for chain of custody gaps.
- Glossary:
  - JSON Lines (.jsonl): 每行一条独立证据记录的文本格式。
  - 熵（取证领域）: 数据流的不可预测性度量。使用确定性整数运算归一化。
  - 保管链（Chain of Custody）: 证明取证工件自采集后未被篡改的文档化追踪路径；任何缺口称为逻辑断裂。
  - 假设编号（Hypothesis ID）: 取证推理过程中候选解释的唯一标识符。
  - 接受/拒绝/弃权（ACCEPT/REJECT/ABSTAIN）: 分析引擎可发出的三种认识论裁决。
  - 显存（VRAM）: GPU 加速器上的专用存储器。
  - 文本用户界面（TUI）: 完全在终端内运行的可视化界面。
  - 确定性整数运算: 使用整数和定点缩放进行的计算，避免分数近似，确保每次运行结果可重复。
- Scientific Note: 【科学说明】 - 术语受皮尔斯、艾柯、格赖斯启发，不是神秘主义。类比传感器：皮尔斯的溯因推理是推理触发器，艾柯的符号学约束是量程边界（防止过度解释），格赖斯的合作准则是子系统通信的噪声滤波器。
- License line.

Important: No floating-point math explanations. Emphasize deterministic integer arithmetic. So when discussing entropy, mention it's normalized via integer arithmetic or fixed-point, not floating point. When discussing offsets, mention byte offsets are integers.

Let's draft carefully.

ENGLISH draft:
## ENGLISH

### What Is This Module?
`vigia/vigia_command_center.py` is the **Command Center** of the VIGÍA Forensic Suite. It is a real-time terminal dashboard—analogous to the control panel of a chromatograph or particle detector—that displays the internal state of an automated forensic inference engine. Instead of test tubes or spectra, the scientist observes digital evidence artifacts: winning hypotheses, network entropy, hardware health, chain-of-custody integrity, and epistemic decisions (ACCEPT, REJECT, ABSTAIN). The module consumes `.jsonl` (JSON Lines) evidence logs incrementally, using deterministic integer byte offsets, and renders the information into human-readable panels inside the terminal.

### Key Concepts and Components

| Concept / Component | Scientific Description |
|---|---|
| **Real-Time JSONL Ingestion** | Evidence logs are read line-by-line from a deterministic integer byte offset. Only new records are parsed; the system never re-reads previously processed data, ensuring deterministic throughput. |
| **VigiAState** | The central registry holding current measurements, decision tallies, ingestion pointers, and anomaly queues. It functions as the instrument’s “black box” memory. |
| **Winning Hypotheses** | Candidate explanations (hypothesis IDs) ranked by the inference engine, shown with coverage (scope of affected artifacts) and cost (computational or evidentiary penalty). |
| **Entropy Bar Chart** | A historical histogram of normalized network disorder. Values are derived from deterministic integer arithmetic via the `entropy_kernel`, not floating-point approximation. |
| **GPU Telemetry Panel** | Optional display of accelerator load, VRAM utilization, and temperature. Requires NVIDIA management libraries; if absent, the panel degrades gracefully. |
| **Anomalies Panel** | A time-ordered list of detected deviations, each graded by severity. These flag potential logical breaks in evidence integrity or unexpected behavioral signatures. |
| **Chain of Custody Footer** | Integrity metrics confirming that evidence artifacts remain unaltered since acquisition. Any tamper event is reported as a logical break. |
| **Decision Tally** | Integer counters for ACCEPT (confirmed), REJECT (falsified), and ABSTAIN (insufficient data) verdicts issued by the reasoning engine. |
| **Layout Engine** | Uses `rich` by default; upgrades to an advanced grid via `textual` if available. This is purely a display concern and does not alter underlying deterministic logic. |

### Glossary

| Term | Definition |
|---|---|
| **.jsonl (JSON Lines)** | A streaming text format where each line is an independent evidence record. Corruption is spatially isolated to a single line. |
| **Entropy (forensic)** | A normalized measure of unpredictability in data traffic. High values indicate encryption or obfuscation; low values indicate redundancy. Computed with integer-based deterministic methods. |
| **Chain of Custody** | The documented, unbroken trail that authenticates evidence from collection to analysis. A gap constitutes a *logical break*. |
| **Hypothesis ID** | A unique alphanumeric label for a candidate investigative explanation generated by the abductive engine. |
| **ACCEPT / REJECT / ABSTAIN** | The three possible epistemic verdicts. ACCEPT = sufficient supporting evidence; REJECT = contradictory evidence; ABSTAIN = withheld judgment due to missing data. |
| **VRAM** | Video RAM; dedicated high-speed memory on a GPU accelerator card. |
| **TUI** | Text-based User Interface. Operates inside a terminal emulator without requiring a windowing system. |
| **Deterministic Integer Arithmetic** | Mathematical operations restricted to whole numbers and fixed-point scaling. Eliminates cross-platform rounding drift and guarantees reproducible results. |

### 【Scientific Note】
This module incorporates conceptual frameworks derived from Charles Sanders Peirce (abductive reasoning), Umberto Eco (semiotic over-interpretation limits), and H. P. Grice (cooperative communication maxims). These names are not invoked as mysticism or humanistic ornament. They function precisely like the labeled sensors on a mass spectrometer: **Peirce** provides the *inference trigger*—the abductive mechanism that generates hypotheses from surprising observations; **Eco** defines the *measurement range*—the semiotic boundary beyond which the system refuses to hallucinate meaning; and **Grice** acts as a *noise filter*—a set of cooperative constraints that suppress irrelevant chatter between subsystems. A chemist does not reject a spectrometer because its optics rely on quantum mechanical models; likewise, these philosophical components are operationalized as strict, testable boundary conditions on automated reasoning.



---

ESPAÑOL draft:
## ESPAÑOL

### ¿Qué es este módulo?
`vigia/vigia_command_center.py` es el **Centro de Comando** de la Suite Forense VIGÍA. Es un tablero de instrumentos en tiempo real dentro de la terminal—análogo al panel de control de un cromatógrafo o detector de partículas—que muestra el estado interno de un motor de inferencia forense automatizado. En lugar de tubos de ensayo o espectros, el científico observa artefactos de evidencia digital: hipótesis ganadoras, entropía de red, salud del hardware, integridad de la cadena de custodia y decisiones epistémicas (ACCEPT, REJECT, ABSTAIN). El módulo consume registros de evidencia en formato `.jsonl` de forma incremental, utilizando desplazamientos deterministas en bytes enteros, y presenta la información en paneles legibles dentro del terminal.

### Conceptos y Componentes Clave

| Concepto / Componente | Descripción Científica |
|---|---|
| **Ingesta en tiempo real de JSONL** | Los registros se leen línea a línea desde un offset de bytes entero determinista. Solo se analizan registros nuevos; el sistema nunca relee datos procesados, garantizando un rendimiento determinista. |
| **VigiAState** | Registro central que almacena mediciones actuales, conteos de decisiones, punteros de ingestión y colas de anomalías. Funciona como la memoria de la “caja negra” del instrumento. |
| **Hipótesis Ganadoras** | Explicaciones candidatas (hypothesis_id) clasificadas por el motor de inferencia, mostradas con cobertura (alcance de artefactos afectados) y costo (penalización computacional o probatoria). |
| **Gráfico de Barras de Entropía** | Histograma histórico del desorden de red normalizado. Los valores se derivan de aritmética determinista de enteros mediante el `entropy_kernel`, no de aproximaciones de punto flotante. |
| **Panel de Telemetría GPU** | Visualización opcional de carga del acelerador, uso de VRAM y temperatura. Requiere librerías de gestión NVIDIA; si faltan, el panel se desactiva gracefulmente. |
| **Panel de Anomalías** | Lista ordenada por tiempo de desviaciones detectadas, cada una calificada por severidad. Señalan posibles rupturas lógicas en la integridad de la evidencia o firmas conductuales inesperadas. |
| **Pie de Métricas de Cadena de Custodia** | Métricas de integridad que confirman que los artefactos de evidencia no han sido alterados desde su adquisición. Cualquier evento de manipulación se reporta como una ruptura lógica. |
| **Contador de Decisiones** | Contadores enteros para ACCEPT (confirmado), REJECT (falsificado) y ABSTAIN (datos insuficientes) emitidos por el motor de razonamiento. |
| **Motor de Layout** | Utiliza `rich` por defecto; mejora a una cuadrícula avanzada mediante `textual` si está disponible. Es puramente una cuestión de visualización y no altera la lógica determinista subyacente. |

### Glosario

| Término | Definición |
|---|---|
| **.jsonl (JSON Lines)** | Formato de texto en streaming donde cada línea es un registro de evidencia independiente. La corrupción queda aislada espacialmente en una sola línea. |
| **Entropía (forense)** | Medida normalizada de impredecibilidad en el tráfico de datos. Valores altos indican cifrado u ofuscación; valores bajos, redundancia. Se calcula con métodos deterministas basados en enteros. |
| **Cadena de Custodia** | La documentación continua e ininterrumpida que autentica la evidencia desde su recolección hasta el análisis. Un vacío constituye una *ruptura lógica*. |
| **Hypothesis ID** | Etiqueta alfanumérica única para una explicación investigativa candidata generada por el motor abdutivo. |
| **ACCEPT / REJECT / ABSTAIN** | Los tres veredictos epistémicos posibles. ACCEPT = evidencia de respaldo suficiente; REJECT = evidencia contradictoria; ABSTAIN = juicio retenido por falta de datos. |
| **VRAM** | RAM de video; memoria de alta velocidad dedicada en una tarjeta aceleradora GPU. |
| **TUI** | Interfaz de Usuario basada en Texto. Opera dentro de un emulador de terminal sin requerir un sistema de ventanas. |
| **Aritmética Determinista de Enteros** | Operaciones matemáticas restringidas a números enteros y escalado de punto fijo. Eliminan la deriva de redondeo entre plataformas y garantizan resultados reproducibles. |

### 【Nota Científica】
Este módulo incorpora marcos conceptuales derivados de Charles Sanders Peirce (razonamiento abdutivo), Umberto Eco (límites de la sobre-interpretación semiótica) y H. P. Grice (máximas de comunicación cooperativa). Estos nombres no se invocan como misticismo ni ornamento humanístico. Funcionan exactamente como los sensores etiquetados en un espectrómetro de masas: **Peirce** provee el *disparador de inferencia*—el mecanismo abdutivo que genera hipótesis a partir de observaciones sorprendentes; **Eco** define el *rango de medición*—el límite semiótico más allá del cual el sistema se niega a alucinar significado; y **Grice** actúa como un *filtro de ruido*—un conjunto de restricciones cooperativas que suprimen la charla irrelevante entre subsistemas. Un químico no rechaza un espectrómetro porque sus ópticas se basen en modelos mecánicos cuánticos; asimismo, estos componentes filosóficos están operacionalizados como condiciones de frontera estrictas y comprobables sobre el razonamiento automatizado.



---

РУССКИЙ draft:
## РУССКИЙ

### Что представляет собой этот модуль?
`vigia/vigia_command_center.py` — это **Центр управления** судебно-экспертного комплекса VIGÍA. Это терминальная панель приборов, работающая в реальном времени—аналогичная панели управления хроматографа или детектора частиц—которая отображает внутреннее состояние автоматизированного судебно-экспертного механизма логического вывода. Вместо пробирок или спектров исследователь наблюдает цифровые артефакты доказательств: победившие гипотезы, энтропию сети, состояние оборудования, целостность цепочки хранения и эпистемические решения (ACCEPT, REJECT, ABSTAIN). Модуль инкрементально потребляет журналы доказательств в формате `.jsonl`, используя детерминированные целочисленные смещения в байтах, и выводит информацию в читаемые панели внутри терминала.

### Ключевые концепции и компоненты

| Концепция / Компонент | Научное описание |
|---|---|
| **Инкрементальное чтение JSONL** | Журналы доказательств читаются построчно начиная с детерминированного целочисленного байтового смещения. Анализируются только новые записи; система никогда не перечитывает ранее обработанные данные, обеспечивая детерминированную пропускную способность. |
| **VigiAState** | Центральный реестр, хранящий текущие измерения, счётчики решений, указатели чтения и очереди аномалий. Функционирует как «чёрный ящик» памяти прибора. |
| **Победившие гипотезы** | Кандидатные объяснения (hypothesis_id), ранжированные механизмом вывода, с указанием покрытия (охват затронутых артефактов) и стоимости (вычислительная или доказательственная цена). |
| **Диаграмма энтропии** | Историческая гистограмма нормализованного сетевого беспорядка. Значения получены из детерминированной целочисленной арифметики через `entropy_kernel`, а не из приближений с плавающей запятой. |
| **Панель телеметрии GPU** | Опциональное отображение загрузки ускорителя, использования VRAM и температуры. Требует библиотек управления NVIDIA; при их отсутствии панель корректно деградирует. |
| **Панель аномалий** | Упорядоченный по времени список обнаруженных отклонений, каждое с градацией по тяжести. Сигнализируют о потенциальных логических разрывах в целостности доказательств или неожиданных поведенческих сигнатурах. |
| **Нижняя строка цепочки хранения** | Метрики целостности, подтверждающие, что артефакты доказательств не изменялись с момента получения. Любое вмешательство регистрируется как логический разрыв. |
| **Счётчик решений** | Целочисленные счётчики для ACCEPT (подтверждено), REJECT (опровергнуто) и ABSTAIN (недостаточно данных), вынесенные механизмом рассуждений. |
| **Механизм раскладки** | По умолчанию использует `rich`; при наличии `textual` переключается на улучшенную сетку. Это исключительно вопрос отображения и не влияет на базовую детерминированную логику. |

### Глоссарий

| Термин | Определение |
|---|---|
| **.jsonl (JSON Lines)** | Потоковый текстовый формат, где каждая строка — независимая запись доказательства. Повреждение пространственно изолировано в одной строке. |
| **Энтропия (в криминалистике)** | Нормализованная мера непредсказуемости в потоке данных. Высокие значения указывают на шифрование или обфускацию; низкие — на избыточность. Вычисляется детерминированными целочисленными методами. |
| **Цепочка хранения (Chain of Custody)** | Документированный непрерывный след, подтверждающий подлинность доказательства от сбора до анализа. Пробел представляет собой *логический разрыв*. |
| **Hypothesis ID** | Уникальный буквенно-цифровой идентификатор кандидатного следственного объяснения, сгенерированного абдуктивным механизмом. |
| **ACCEPT / REJECT / ABSTAIN** | Три возможных эпистемических вердикта. ACCEPT = достаточно подтверждающих данных; REJECT = противоречивые данные; ABSTAIN = воздержание от суждения из-за отсутствия данных. |
| **VRAM** | Видеопамять; высокоскоростная память на плате GPU-ускорителя. |
| **TUI** | Текстовый пользовательский интерфейс. Работает внутри эмулятора терминала без оконной системы. |
| **Детерминированная целочисленная арифметика** | Математические операции, ограниченные целыми числами и масштабированием с фиксированной точкой. Устраняют межплатформенное округление и гарантируют воспроизводимые результаты. |

### 【Научное примечание】
Этот модуль включает концептуальные рамки, основанные на Чарльзе Сандерсе Пирсе (абдуктивное рассуждение), Умберто Эко (пределы семиотической переинтерпретации) и Г. П. Грайсе (максимы кооперативного общения). Эти имена привлекаются не как мистицизм или гуманитарное украшение. Они функционируют точно так же, как калиброванные датчики на масс-спектрометре: **Пирс** обеспечивает *триггер вывода*—абдуктивный механизм генерации гипотез из неожиданных наблюдений; **Эко** определяет *диапазон измерения*—семиотическую границу, за которой система отказывается галлюцинировать смысл; а **Грайс** выступает *шумовым фильтром*—набором кооперативных ограничений, подавляющих нерелевантный обмен между подсистемами. Химик не отказывается от спектрометра потому, что его оптика опирается на квантовомеханические модели; аналогично, эти философские компоненты операционализированы как строгие, проверяемые граничные условия автоматизированного рассуждения.



---

中文 draft:
## 中文

### 这是什么模块？
`vigia/vigia_command_center.py` 是 **VIGÍA 取证套件** 的指挥中心。它是一个实时终端仪表板（TUI）——类似于色谱仪或粒子探测器的控制面板——用于展示自动取证推理引擎的内部状态。科学家观察的不是试管或光谱，而是数字取证工件：胜出假设、网络熵、硬件健康状态、保管链完整性以及认识论裁决（接受 / 拒绝 / 弃权）。该模块以增量方式摄取 `.jsonl`（JSON Lines）格式的证据日志，使用确定性的整数字节偏移量进行读取，仅解析新增记录，并将信息渲染为终端内可读的面板。

### 核心概念与组件

| 概念 / 组件 | 科学说明 |
|---|---|
| **实时 JSONL 摄取** | 从确定性的整数字节偏移量开始逐行读取证据日志。仅解析新记录，系统不会重复读取已处理数据，从而确保确定性的吞吐量。 |
| **VigiAState（状态管理器）** | 保存当前测量值、决策计数、摄取指针与异常队列的中心注册表。功能类似于仪器的“黑匣子”存储器。 |
| **胜出假设** | 由推理引擎排序的候选解释（假设编号），附带覆盖率（受影响取证工件的范围）与代价（计算或证据惩罚）。 |
| **熵历史柱状图** | 展示归一化网络无序程度的历史直方图。数值由 `entropy_kernel` 通过确定性整数运算得出，而非浮点近似。 |
| **GPU 遥测面板** | 可选展示加速器负载、显存（VRAM）占用与温度。需要 NVIDIA 管理库；若缺失，面板将优雅降级。 |
| **异常面板** | 按时间排序的检测偏差列表，每条均标有严重等级。用于标记证据完整性中可能的逻辑断裂或异常行为特征。 |
| **保管链页脚指标** | 完整性指标，用于确认取证工件自采集以来未被篡改。任何篡改事件均报告为逻辑断裂。 |
| **决策计数器** | 对接受（确认）、拒绝（证伪）、弃权（信息不足）三种裁决
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
