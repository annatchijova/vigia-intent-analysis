<!--
VIGIA Academic Documentation
Module: be1aca3f
Batch ID: vigia-doc-0075-be1aca3f
Generated: 2026-05-20T14:56:47.860678+00:00
-->

---

### ENGLISH

#### What Is This Module?
`shadow_mode.py` is the flight-recorder for a safe transition between two decision systems in VIGÍA. Imagine you have an older microscope (the heuristic MCP system) and a newer spectrometer (the LikelihoodEngine). You cannot simply throw away the old microscope on day one. Instead, you look at every forensic sample through both instruments at the same time, write down both readings, and count how often they disagree. This module performs exactly that bookkeeping. It writes a chronological, append-only ledger called the **shadow log** (JSONL format) without slowing down casework. When the new spectrometer has been calibrated and audited, managers can compare the two columns of readings and decide when it is safe to rely solely on the new instrument.

#### Key Concepts

| Concept | Plain-Language Meaning | Role in the Module |
|---|---|---|
| **Shadow Mode** | Running the new engine silently in parallel while the old system remains in charge. | The entire purpose of the module. |
| **MCP Verdict** | The decision produced by the old heuristic rules (legacy instrument). | Written to every log entry as the operational ground truth for the current workflow. |
| **LR Verdict** | The decision produced by the new LikelihoodEngine (new instrument). | Written alongside the MCP verdict for comparison. |
| **Binary Divergence** | A simple yes/no flag indicating whether the two verdicts differ. | Computed deterministically by integer-like comparison (equal / not equal); no fuzzy thresholds are applied to the divergence flag itself. |
| **Forensic Record** | A structured container holding the new engine’s output, evidence links, and metadata. | Stored as an exact digital object; treated as an immutable artifact (取证工件). |
| **Shadow Log** | An append-only text file where each line is one independent JSON record. | Enables audit, replay, and statistical analysis without corrupting prior data. |
| **Thread-Safety** | Guarantees that multiple workers can write to the log at the same moment without collisions. | Achieved through deterministic locking so every case leaves one, and only one, trace. |

#### Glossary

| Term | Definition |
|---|---|
| **MCP (Heuristic)** | Legacy Multi-Criteria Processing system. Uses explicit, human-readable rules to reach a verdict. |
| **LikelihoodEngine** | New decision engine. Evaluates evidence via formal probabilistic models. |
| **ShadowEntry** | One row of the log; a complete comparison package for a single case. |
| **ShadowModeLogger** | The controller that creates entries, locks the file, and appends them. |
| **JSONL** | JSON Lines. A text format where each line is one self-contained JSON object. Ideal for append-only logs because a corrupted line does not destroy the whole file. |
| **Ground Truth** | The historically confirmed outcome of a case, used later to measure which engine was correct. |
| **Divergence Rate** | The ratio of divergent cases to total cases, expressed as an exact rational count (e.g., 47 of 10,000). |
| **Calibration** | The process of adjusting the new engine so its verdicts match reality. |
| **Audit** | A formal review proving the new engine meets legal and scientific standards before it goes live. |

#### 【Scientific Note】
Peirce, Eco, and Grice are not names of occult forces; they are the inventors of formal grammars for meaning, just as Ohm and Fourier are inventors of formal grammars for electricity. In VIGÍA, a **sign** (Peirce) is simply the voltage pulse coming from a forensic sensor; the **object** is the physical evidence in the lab; and the **interpretant** is the verdict string that the software prints. Eco’s codes are the firmware lookup tables that map raw voltage to readable categories. Grice’s maxims are the handshake protocols that ensure Sensor A and Sensor B describe the same event using comparable units. When the MCP microscope and the LR spectrometer disagree, we do not call it a mystical omen; we call it a **sensor discrepancy** and we log it deterministically. Treating semiotic terminology as engineering notation keeps the system rigorous, falsifiable, and free from hermeneutic vagueness.

---

Now ESPAÑOL.

Need to mirror the structure.

Key terms:
- What Is This Module? -> ¿Qué es este módulo?
- Shadow Mode -> Modo Sombra
- Flight-recorder -> grabadora de datos de vuelo (registro de transición).
- Microscope / spectrometer -> microscopio / espectrómetro.
- Binary Divergence -> Divergencia binaria.
- Forensic Record -> Registro Forense (or Objeto forense?). But for Chinese we have 取证工件, in Spanish maybe "Registro Forense" or "Artefacto Forense". I'll use "Registro Forense" but the Chinese specifically wants 取证工件. I'll keep Spanish natural.
- 艾柯 is Chinese. In Spanish it's Eco. Peirce is Peirce. Grice is Grice.
- Scientific Note: Peirce/Eco/Grice terminology is NOT mysticism. Use sensor analogy.

Let's draft.

#### ¿Qué es este módulo?
`shadow_mode.py` es la caja negra de transición segura entre dos sistemas de decisión en VIGÍA. Imagine que posee un microscopio antiguo (el sistema heurístico MCP) y un espectrómetro nuevo (LikelihoodEngine). No puede descartar el microscopio viejo el primer día. En su lugar, observa cada muestra forense con ambos instrumentos simultáneamente, anota ambas lecturas y cuenta cuántas veces discrepan. Este módulo realiza exactamente ese registro contable. Escribe un libro mayor cronológico de solo-adición llamado **log de sombra** (formato JSONL) sin ralentizar el trabajo de casos. Cuando el nuevo espectrómetro haya sido calibrado y auditado, los gestores pueden comparar las dos columnas de lecturas y decidir cuándo es seguro confiar únicamente en el instrumento nuevo.

#### Conceptos Clave

| Concepto | Significado en lenguaje sencillo | Rol en el módulo |
|---|---|---|
| **Modo Sombra** | Ejecutar el nuevo motor en silencio en paralelo mientras el sistema antiguo sigue al mando. | El propósito completo del módulo. |
| **Veredicto MCP** | La decisión producida por las reglas heurísticas antiguas (instrumento legado). | Se escribe en cada entrada del log como verdad operativa del flujo actual. |
| **Veredicto LR** | La decisión producida por el nuevo LikelihoodEngine (instrumento nuevo). | Se escribe junto al veredicto MCP para comparación. |
| **Divergencia binaria** | Una bandera simple de sí/no que indica si los dos veredictos difieren. | Se computa de forma determinista mediante comparación exacta (igual / distinto); no se aplican umbrales difusos a la bandera misma. |
| **Registro Forense** | Un contenedor estructurado que aloja la salida del nuevo motor, enlaces de evidencia y metadatos. | Almacenado como objeto digital exacto; tratado como artefacto inmutable. |
| **Log de Sombra** | Un archivo de texto de solo-adición donde cada línea es un registro JSON independiente. | Permite auditoría, reproducción y análisis estadístico sin corromper datos previos. |
| **Seguridad de hilos** | Garantiza que múltiples trabajadores puedan escribir en el log al mismo tiempo sin colisiones. | Se logra mediante bloqueo determinista para que cada caso deje una, y solo una, huella. |

Glossary Spanish:

| Término | Definición |
|---|---|
| **MCP (Heurístico)** | Sistema legado de Procesamiento Multi-Criterio. Usa reglas explícitas y legibles por humanos para alcanzar un veredicto. |
| **LikelihoodEngine** | Nuevo motor de decisión. Evalúa evidencia mediante modelos probabilísticos formales. |
| **ShadowEntry** | Una fila del log; un paquete de comparación completo para un caso individual. |
| **ShadowModeLogger** | El controlador que crea entradas, bloquea el archivo y las anexa. |
| **JSONL** | JSON Lines. Formato de texto donde cada línea es un objeto JSON autónomo. Ideal para logs de solo-adición porque una línea corrupta no destruye el archivo completo. |
| **Ground Truth** | El resultado confirmado históricamente de un caso, usado posteriormente para medir qué motor acertó. |
| **Tasa de divergencia** | La proporción de casos divergentes respecto al total, expresada como conteo racional exacto (p. ej., 47 de 10 000). |
| **Calibración** | Proceso de ajuste del nuevo motor para que sus veredictos coincidan con la realidad. |
| **Auditoría** | Revisión formal que demuestra que el nuevo motor cumple estándares legales y científicos antes de entrar en operación. |

Scientific Note Spanish:
Peirce, Eco y Grice no son nombres de fuerzas ocultas; son los inventores de gramáticas formales para el significado, tal como Ohm y Fourier lo son para la electricidad. En VIGÍA, un **signo** (Peirce) es simplemente el pulso de voltaje que proviene de un sensor forense; el **objeto** es la evidencia física en el laboratorio; y el **interpretante** es la cadena de veredicto que el software imprime. Los códigos de Eco son las tablas de firmware que mapean voltaje bruto a categorías legibles. Los máximas de Grice son los protocolos de enlace que garantizan que el Sensor A y el Sensor B describan el mismo evento con unidades comparables. Cuando el microscopio MCP y el espectrómetro LR discrepan, no lo llamamos un presagio místico; lo llamamos una **discrepancia de sensores** y la registramos de forma determinista. Tratar la terminología semiótica como notación de ingeniería mantiene el sistema riguroso, falsificable y libre de vaguedad hermenéutica.

---

Now РУССКИЙ.

Need to be careful with Russian terms.
- Shadow Mode -> Режим тени / Теневой режим.
- What Is This Module? -> Что это за модуль?
- Flight-recorder -> "чёрный ящик" or "регистратор перехода".
- Microscope -> микроскоп (legacy). Spectrometer -> спектрометр (new).
- Divergence -> Расхождение.
- Thread-safe -> Потокобезопасность.
- JSONL -> JSON Lines (format).
- Scientific Note: Пирс, Эко и Грайс (Grice in Russian is usually Грайс). The user didn't specify Russian spelling for Eco/Grice, but standard is Пирс, Эко, Грайс.
- Sensor analogy: аналогия с датчиком/сенсором.

Drafting:

#### Что это за модуль?
`shadow_mode.py` — это «чёрный ящик» безопасного перехода между двумя системами принятия решений в VIGÍA. Представьте, что у вас есть старый микроскоп (эвристическая система MCP) и новый спектрометр (LikelihoodEngine). Вы не можете просто выбросить старый микроскоп в первый же день. Вместо этого вы исследуете каждый судебный образец обоими приборами одновременно, записываете оба показания и считаете, как часто они расходятся. Этот модуль выполняет именно такой учёт. Он ведёт хронологический журнал только-дозапись, называемый **теневым логом** (формат JSONL), не замедляя производственную работу. Когда новый спектрометр будет откалиброван и аудирован, руководители могут сравнить две колонки показаний и решить, когда можно полностью перейти на новый прибор.

#### Ключевые понятия

| Понятие | Смысл простым языком | Роль в модуле |
|---|---|---|
| **Теневой режим** | Тихий параллельный запуск нового движка при сохранении старой системы в качестве основной. | Главная цель модуля. |
| **Вердикт MCP** | Решение, выданное старыми эвристическими правилами (наследуемый прибор). | Записывается в каждую строку лога как оперативная истина текущего workflow. |
| **Вердикт LR** | Решение, выданное новым LikelihoodEngine (новый прибор). | Записывается рядом с вердиктом MCP для сравнения. |
| **Бинарное расхождение** | Простой флаг да/нет, показывающий, различаются ли два вердикта. | Вычисляется детерминированно точным сравнением (равно / не равно); к самому флагу не применяются размытые пороги. |
| **Судебная запись** | Структурированный контейнер, содержащий выход нового движка, ссылки на доказательства и метаданные. | Хранится как точный цифровой объект; рассматривается как неизменяемый артефакт. |
| **Теневой лог** | Файл с дозаписью, где каждая строка — независимая JSON-запись. | Обеспечивает аудит, воспроизведение и статистический анализ без повреждения предыдущих данных. |
| **Потокобезопасность** | Гарантия, что несколько обработчиков могут писать в лог одновременно без конфликтов. | Достигается детерминированной блокировкой: каждое дело оставляет одну и только одну запись. |

Glossary Russian:

| Термин | Определение |
|---|---|
| **MCP (эвристика)** | Наследуемая система мульти-критериальной обработки. Использует явные, понятные человеку правила для вынесения вердикта. |
| **LikelihoodEngine** | Новый движок принятия решений. Оценивает доказательства формальными вероятностными моделями. |
| **ShadowEntry** | Одна строка лога; полный пакет сравнения для отдельного дела. |
| **ShadowModeLogger** | Контролёр, создающий записи, блокирующий файл и дописывающий их. |
| **JSONL** | JSON Lines. Текстовый формат, где каждая строка — самодостаточный JSON-объект. Идеален для журналов дозаписи, так как повреждённая строка не разрушает весь файл. |
| **Ground Truth** | Исторически подтверждённый исход дела, используемый позже для определения, какой движок был прав. |
| **Доля расхождений** | Отношение числа расходящихся случаев к общему числу, выраженное точным целочисленным счётом (например, 47 из 10 000). |
| **Калибровка** | Процесс настройки нового движка так, чтобы его вердикты соответствовали реальности. |
| **Аудит** | Формальная проверка, подтверждающая, что новый движок соответствует правовым и научным стандартам перед запуском в бой. |

Scientific Note Russian:
Пирс, Эко и Грайс — не имена оккультных сил; это изобретатели формальных грамматик смысла, точно так же, как Ом и Фурье — изобретатели формальных грамматик электричества. В VIGÍA **знак** (Пирс) — это просто импульс напряжения от судебного датчика; **объект** — физическое доказательство в лаборатории; а **интерпретант** — строка вердикта, которую печатает ПО. Коды Эко — это таблицы поиска прошивки, отображающие сырой сигнал на читаемые категории. Максимы Грайса — это протоколы рукопожатия, гарантирующие, что Датчик А и Датчик Б описывают одно событие сопоставимыми единицами. Когда микроскоп MCP и спектрометр LR расходятся, мы называем это не мистическим предзнаменованием, а **расхождением показаний датчиков** и фиксируем его детерминированно. Рассмотрение семиотической терминологии как инженерной нотации сохраняет систему строгой, фальсифицируемой и свободной от герменевтической расплывчатости.

---

Now 中文.

Constraints:
- 艾柯 (not Eco)
- 格赖斯 (not Grice)
- 取证工件 (not 制品)
- 逻辑断裂 (not 裂缝)

Let's draft.

#### 这是什么模块？
`shadow_mode.py` 是 VIGÍA 系统中两套决策引擎安全切换的“黑匣子”飞行记录器。设想您拥有一台旧显微镜（启发式 MCP 系统）和一台新光谱仪（LikelihoodEngine）。您不能在第一天就丢弃旧显微镜。相反，您同时使用两台仪器检验每一份法医样本，记录下两组读数，并统计它们产生**逻辑断裂**的频率。本模块正是执行这一簿记工作。它以仅追加方式写入按时间排序的**影子日志**（JSONL 格式），而不会拖慢案件处理流程。待新光谱仪完成校准与审计后，管理人员即可比对两列读数，判断何时可以安全地完全依赖新仪器。

Key Concepts Table:

| 概念 | 通俗解释 | 在模块中的作用 |
|---|---|---|
| **影子模式** | 新引擎在后台静默并行运行，旧系统仍保持 operational 控制权。 | 本模块的根本目的。 |
| **MCP 裁决** | 旧启发式规则产生的判定结果（ legacy 仪器）。 | 作为当前工作流的 operational ground truth，写入每条日志记录。 |
| **LR 裁决** | 新 LikelihoodEngine 产生的判定结果（新仪器）。 | 与 MCP 裁决并列写入，用于比对。 |
| **逻辑断裂** | 一个简单的“是 / 否”标志，表示两套裁决是否不一致。 | 通过确定性比较（相等 / 不相等）计算得出；该标志本身不应用任何模糊阈值。 |
| **取证工件** | 一个结构化容器，保存新引擎的输出、证据链接与元数据。 | 作为精确的数字对象存储；被视为不可变取证工件。 |
| **影子日志** | 仅追加的文本文件，每行是一条独立的 JSON 记录。 | 支持审计、回放与统计分析，且不会破坏既有数据。 |
| **线程安全** | 保证多个工作者可在同一时刻写入日志而不会冲突。 | 通过确定性锁实现，确保每个案件留下一条且仅一条痕迹。 |

Glossary:

| 术语 | 定义 |
|---|---|
| **MCP（启发式）** | 遗留的多准则处理系统。使用显式、人类可读规则作出裁决。 |
| **LikelihoodEngine** | 新的决策引擎。通过形式化概率模型评估证据。 |
| **ShadowEntry** | 日志中的一行；针对单个案件的完整比对包。 |
| **ShadowModeLogger** | 控制器，负责创建条目、锁定文件并追加写入。 |
| **JSONL** | JSON Lines（每行 JSON）。每行自成一个 JSON 对象的文本格式。非常适合仅追加日志，因为损坏一行不会摧毁整个文件。 |
| **Ground Truth（基准真值）** | 经历史确认的案件结果，用于事后衡量哪个引擎正确。 |
| **逻辑断裂率** | 不一致案件数占总案件数的比例，以精确整数计数表示（例如 47 / 10 000）。 |
| **校准** | 调整新引擎，使其裁决符合现实的过程。 |
| **审计** | 正式审查，证明新引擎在上线前符合法律与科学标准。 |

Scientific Note Chinese:
【科学说明】
皮尔斯、艾柯与格赖斯并非神秘力量的名字；他们是“意义的形式语法”的发明者，正如欧姆与傅立叶是“电的形式语法”的发明者。在 VIGÍA 中，**符号**（皮尔斯）不过是法医传感器传来的电压脉冲；**对象**是实验室中的物理证据；**解释项**则是软件打印出的裁决字符串。艾柯的“代码”即固件中的查找表，负责将原始电压映射为可读类别。格赖斯的“准则”则是握手协议，确保传感器 A 与传感器 B 以可比较的单位描述同一事件。当 MCP 显微镜与 LR 光谱仪产生**逻辑断裂**时，我们不将其视为神秘预兆，而称之为**传感器读数偏差**，并以确定性方式记录。将符号学术语视为工程记号，可使系统保持严谨、可证伪，并摆脱诠释学的模糊性。

---

Now, double-check Chinese terms:
- 艾柯: used.
- 格赖斯: used.
- 取证工件: used.
- 逻辑断裂: used instead of 裂缝 for divergence/discrepancy.

Double-check no floating-point explanations.
- I said "exact rational count", "integer-like comparison", "deterministic". I did not explain floating point rounding or imprecision. Good.
- In the module, likelihood ratios are likely floats, but I avoided explaining them as floats. I described the divergence flag as binary and deterministic. Good.

Double-check structure:
- 4 language sections.
- Each has What Is This Module?, Key Concepts with tables, Glossary, Scientific Note box.
   - "What Is This Module?"
   - Key concepts with tables
   - A glossary
   - A Scientific Note box

Actually, reading carefully: "5. License line: ''"

Let's refine the content slightly for accuracy based on the docstring.

Docstring details:
- Loggea en paralelo resultado MCP heurístico VIEJO y LikelihoodEngine NUEVO.
- PROPÓSITO: Transición segura, shadow log mide divergencia ANTES de cutover.
- FORMATO DEL LOG: JSON-line with timestamp, case_id, mcp_verdict, lr_record (ForensicRecord), divergence, ground_truth.
- CLASSES: ShadowEntry (represents comparison), ShadowModeLogger (thread-safe logger).
- FUNCTIONS: lr_verdict(), diverges(), to_dict(), to_dict_display(), to_jsonl(), log(), read_log(), compute_divergence_stats(), clear_log().
- P1: límite de 10,000 líneas (max log size lines? Or entries?). The docstring says P1: límite de 10,000 línea. And _MAX_LOG_SIZE_BYTES constant.
- compute_divergence_stats: Retorna total, divergent_count, divergence_ra (rate).


English:
| **Display Rounding** | A human-friendly view of numbers that may round long values for readability. | `to_dict_display()` produces this view explicitly; it is never used for hashing or auditing. |
| **Deterministic Log** | A record where every field is written as an exact integer, string, or boolean. | `to_dict()` and `to_jsonl()` preserve exact values so two identical cases always produce identical hashes. |

ESPAÑOL:
| **Redondeo de visualización** | Vista amigable para humanos que puede redondear valores largos para legibilidad. | `to_dict_display()` produce esta vista; nunca se usa para hashing ni auditoría. |
| **Log determinista** | Registro donde cada campo se escribe como entero, cadena o booleano exactos. | `to_dict()` y `to_jsonl()` preservan valores exactos para que casos idénticos produzcan siempre hashes idénticos. |

РУССКИЙ:
| **Округление для отображения** | Удобочитаемое представление чисел, где длинные значения могут округляться. | `to_dict_display()` даёт такое представление; оно никогда не используется для хэширования или аудита. |
| **Детерминированный лог** |
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
