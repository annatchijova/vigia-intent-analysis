<!--
VIGIA Academic Documentation
Module: 48ab3a10
Batch ID: vigia-doc-0038-48ab3a10
Generated: 2026-05-20T14:56:47.852728+00:00
-->

ENGLISH:
- Title: Audit and Action — VIGÍA Forensic Suite EBS v1
- Module Path: vigia/core/audit_action.py (with references to vigia/audit/evidence_graph_diff.py and vigia/action/safe_action_executor.py as component origins)
- What Is This Module?: This module is the "memory and safety switchboard" of the VIGÍA forensic system. It performs four tasks: (1) it compares two decision states to find exactly what changed (like diffing two lab notebooks), (2) it calculates the smallest corrective step needed to flip a rejection into an approval, (3) it checks every proposed step against a formal rulebook written in JSON, and (4) it executes approved steps inside a tamper-evident shell that can undo actions if necessary. No floating-point approximations are used; all state comparisons and cost calculations rely on deterministic integer arithmetic and discrete symbolic logic.
- Key Concepts Table:
  | Component | Role | Deterministic Guarantee |
  | EvidenceGraphDiff | Decomposes decision changes into causal deltas | Symbolic graph comparison over discrete nodes |
  | InterventionOptimizer | Finds minimal-cost intervention via greedy search | Integer-cost minimization; no fractional drift |
  | FormalPolicyEngine | Validates against JSON policy rules | Discrete state machine: ALLOW/DENY/REQUIRE_APPROVAL |
  | SafeActionExecutor | Runs actions with traceability and rollback | Immutable append-only history; reversible integer tokens |
  | forensic_timeout | Hard time boundary on execution | Interrupt driven by integer cycle counter |

- Functions Table:
  | Function | Purpose | Return Type |
  | diff_decisions() | Compares two DecisionTrace objects and graphs | Dictionary with boolean flags and delta lists |
  | recommend() | Suggests minimal intervention to reach ACCEPT | Intervention record with integer cost |
  | check() / check_action_record() | Validates action against policy | Categorical result string |
  | execute_recommendation() | Fetches recommendation and executes if policy allows | ActionReceipt or rollback token |
  | rollback(n) | Reverses last n actions | Previous state snapshot or None |
  | get_action_history() | Exports history for ForensicBundle | Ordered list of ActionRecords |
  | audit_log() | Generates SIFT-compatible log | Structured text stream |

- Glossary:
  - **DecisionTrace**: An immutable, timestamped record of every input, rule triggered, and intermediate conclusion that led to a system decision.
  - **Causal Delta**: A discrete unit of change that links an altered input directly to a changed output node in the evidence graph.
  - **Intervention**: A deliberately applied corrective operation intended to modify system state; analogous to a calibrated adjustment in an experimental apparatus.
  - **ForensicBundle**: A tamper-evident container of evidence, logs, and metadata ready for external review.
  - **SIFT**: Standard Interface for Forensic Traceability; the log format consumed by downstream audit tools.
  - **Rollback Token**: An integer-indexed handle that identifies a saved checkpoint, enabling deterministic reversal.
  - **Policy State**: One of three discrete categories: ALLOW, DENY, REQUIRE_APPROVAL.
  - **Greedy Search**: A deterministic algorithm that selects the next step based on the locally optimal integer cost until the goal is reached.

- Scientific Note:
  > 【Scientific Note】
  > References to semiotic frameworks—such as Peirce’s abduction, Eco’s interpretative codes, and Grice’s conversational maxims—appear in forensic literature because they describe *deterministic information-flow protocols*. They are not mysticism. Think of a temperature sensor: it converts continuous heat into discrete voltage states according to a fixed lookup table (Peirce’s “index”), assigns meaning via a manufacturer’s codebook (Eco’s “code”), and expects the receiver to interpret the reading cooperatively without hidden assumptions (Grice’s “cooperative principle”). VIGÍA treats decision traces exactly this way: evidence is indexed, decoded by formal policy, and communicated with full explicitness. There are no hidden implicatures—Invariant I4 guarantees that every effect is explicit and traceable.

- 

ESPAÑOL:
- Título: Auditoría y Acción — VIGÍA Forensic Suite EBS v1
- ¿Qué es este módulo?: Es el "cuadro de memoria e interruptores de seguridad" del sistema forense VIGÍA. Realiza cuatro tareas: compara dos estados de decisión para encontrar exactamente qué cambió (como comparar dos cuadernos de laboratorio), calcula el paso correctivo más pequeño para convertir un rechazo en aprobación, verifica cada paso propuesto contra un reglamento formal en JSON, y ejecuta los pasos aprobados dentro de un caparazón a prueba de manipulaciones que puede deshacer acciones si es necesario. No se utilizan aproximaciones de coma flotante; toda comparación de estados y cálculo de costos se basa en aritmética entera determinista y lógica simbólica discreta.
- Conceptos clave:
  | Componente | Función | Garantía determinista |
  | EvidenceGraphDiff | Descompone cambios de decisión en deltas causales | Comparación simbólica de grafos sobre nodos discretos |
  | InterventionOptimizer | Busca intervención mínima mediante búsqueda greedy | Minimización de costos enteros; sin deriva fraccionaria |
  | FormalPolicyEngine | Valida contra reglas JSON | Máquina de estados discreta: ALLOW/DENY/REQUIRE_APPROVAL |
  | SafeActionExecutor | Ejecuta acciones con trazabilidad y rollback | Historial inmutable de solo anexión; tokens enteros reversibles |
  | forensic_timeout | Límite de tiempo estricto en ejecución | Interrupción por contador de ciclos entero |

- Functions:
  | Función | Propósito | Tipo de retorno |
  | diff_decisions() | Compara dos DecisionTrace y grafos | Diccionario con banderas booleanas y listas de deltas |
  | recommend() | Sugiere intervención mínima para alcanzar ACCEPT | Registro de intervención con costo entero |
  | check() / check_action_record() | Valida acción contra política | Cadena categórica de resultado |
  | execute_recommendation() | Obtiene recomendación y ejecuta si la política lo permite | ActionReceipt o token de rollback |
  | rollback(n) | Revierte las últimas n acciones | Instantánea de estado anterior o None |
  | get_action_history() | Exporta historial para ForensicBundle | Lista ordenada de ActionRecords |
  | audit_log() | Genera registro compatible SIFT | Flujo de texto estructurado |

- Glosario:
  - **DecisionTrace**: Registro inmutable y sellado de cada entrada, regla activada y conclusión intermedia que condujo a una decisión del sistema.
  - **Delta Causal**: Unidad discreta de cambio que vincula una entrada alterada directamente con un nodo de salida modificado en el grafo de evidencia.
  - **Intervención**: Operación correctiva aplicada deliberadamente para modificar el estado del sistema; análoga a un ajuste calibrado en un aparato experimental.
  - **ForensicBundle**: Contenedor a prueba de manipulaciones de evidencia, registros y metadatos listo para revisión externa.
  - **SIFT**: Standard Interface for Forensic Traceability; formato de registro consumido por herramientas de auditoría posteriores.
  - **Token de Rollback**: Manejador indexado por enteros que identifica un punto de control guardado, permitiendo la reversión determinista.
  - **Estado de Política**: Una de tres categorías discretas: ALLOW, DENY, REQUIRE_APPROVAL.
  - **Búsqueda Greedy**: Algoritmo determinista que selecciona el siguiente paso basado en el costo entero localmente óptimo hasta alcanzar la meta.

- Nota científica:
  > 【Scientific Note】 / 【Nota Científica】
  > Las referencias a marcos semióticos—como la abducción de Peirce, los códigos interpretativos de Eco y los máximas conversacionales de Grice—aparecen en la literatura forense porque describen *protocolos deterministas de flujo de información*. No son misticismo. Piense en un sensor de temperatura: convierte el calor continuo en estados de voltaje discretos según una tabla de consulta fija (el “índice” de Peirce), asigna significado mediante un manual del fabricante (el “código” de Eco) y espera que el receptor interprete la lectura de manera cooperativa sin suposiciones ocultas (el “principio cooperativo” de Grice). VIGÍA trata las trazas de decisión exactamente así: la evidencia se indexa, se decodifica mediante política formal y se comunica con total explicitud. No hay implicaturas ocultas—el Invariante I4 garantiza que cada efecto sea explícito y trazable.

- Licencia: 

РУССКИЙ:
- Название: Аудит и Действие — VIGÍA Forensic Suite EBS v1
- Что это за модуль?: Это «плата памяти и защитных выключателей» судебно-медицинской системы VIGÍA. Выполняет четыре задачи: сравнивает два состояния решений, чтобы найти точно, что изменилось (как сравнение двух лабораторных журналов), вычисляет наименьший корректирующий шаг для превращения отказа в одобрение, проверяет каждый предложенный шаг по формальному своду правил в JSON и выполняет одобренные шаги в защищённой от подделки оболочке, способной откатить действия при необходимости. Не используются приближения с плавающей запятой; все сравнения состояний и расчёты стоимости основаны на детерминированной целочисленной арифметике и дискретной символической логике.
- Ключевые концепции:
  | Компонент | Роль | Детерминированная гарантия |
  | EvidenceGraphDiff | Разлагает изменения решений на причинные дельты | Символьное сравнение графов по дискретным узлам |
  | InterventionOptimizer | Поиск минимального вмешательства жадным алгоритмом | Минимизация целочисленной стоимости; без дробного дрейфа |
  | FormalPolicyEngine | Проверка по правилам JSON | Дискретный автомат: ALLOW/DENY/REQUIRE_APPROVAL |
  | SafeActionExecutor | Выполнение действий с трассируемостью и откатом | Неизменяемый дополняемый журнал; обратимые целочисленные токены |
  | forensic_timeout | Жёсткое ограничение времени выполнения | Прерывание по целочисленному счётчику циклов |

- Функции:
  | Функция | Назначение | Тип возвращаемого значения |
  | diff_decisions() | Сравнивает два DecisionTrace и графы | Словарь с булевыми флагами и списками дельт |
  | recommend() | Предлагает минимальное вмешательство для достижения ACCEPT | Запись вмешательства с целочисленной стоимостью |
  | check() / check_action_record() | Проверяет действие по политике | Категориальная результирующая строка |
  | execute_recommendation() | Получает рекомендацию и выполняет, если политика разрешает | ActionReceipt или токен отката |
  | rollback(n) | Отменяет последние n действий | Снимок предыдущего состояния или None |
  | get_action_history() | Экспортирует историю для ForensicBundle | Упорядоченный список ActionRecords |
  | audit_log() | Генерирует журнал, совместимый с SIFT | Структурированный текстовый поток |

- Глоссарий:
  - **DecisionTrace**: Неизменяемая записи с отметкой времени каждого входа, сработавшего правила и промежуточного заключения, приведшего к решению системы.
  - **Причинная дельта (Causal Delta)**: Дискретная единица изменения, связывающая изменённый вход непосредственно с изменённым выходным узлом в графе доказательств.
  - **Вмешательство (Intervention)**: Целенаправленная корректирующая операция, предназначенная для изменения состояния системы; аналог откалиброванной регулировки в экспериментальной установке.
  - **ForensicBundle**: Контейнер с защитой от подделки, содержащий доказательства, журналы и метаданные, готовый к внешней экспертизе.
  - **SIFT**: Standard Interface for Forensic Traceability; формат журнала, используемый последующими инструментами аудита.
  - **Токен отката (Rollback Token)**: Индексированный целым числом дескриптор, идентифицирующий сохранённую контрольную точку и обеспечивающий детерминированный откат.
  - **Состояние политики**: Одна из трёх дискретных категорий: ALLOW, DENY, REQUIRE_APPROVAL.
  - **Жадный поиск (Greedy Search)**: Детерминированный алгоритм, выбирающий следующий шаг на основе локально оптимальной целочисленной стоимости до достижения цели.

- Научное примечание:
  > 【Scientific Note】 / 【Научное примечание】
  > Ссылки на семиотические рамки — такие как абдукция Пирса, интерпретативные коды Эко и разговорные максимы Грайса — встречаются в судебной литературе, потому что они описывают *детерминированные протоколы потока информации*. Это не мистицизм. Представьте температурный датчик: он преобразует непрерывное тепло в дискретные состояния напряжения по фиксированной таблице соответствия («индекс» Пирса), присваивает значение через справочник производителя («код» Эко) и ожидает, что получатель интерпретирует показание кооперативно, без скрытых предположений («кооперативный принцип» Грайса). VIGÍA обращается с трассами решений точно так же: доказательства индексируются, декодируются формальной политикой и передаются с полной явностью. Скрытых импликатур не существует — инвариант I4 гарантирует, что каждый эффект явный и прослеживаемый.

- Лицензия: 

中文:
- 标题: 审计与行动 — VIGÍA 法医套件 EBS v1
- 模块路径: vigia/core/audit_action.py（组件源自 vigia/audit/evidence_graph_diff.py 与 vigia/action/safe_action_executor.py）
- 这是什么模块？: 本模块是 VIGÍA 取证系统的“记忆与安全总闸”。它执行四项任务：（1）比对两个决策状态，精确定位变更内容（如同比对两本实验记录本）；（2）计算将“拒绝”翻转为“接受”所需的最小修正步骤；（3）依据以 JSON 编写的正式规则手册核查每一个拟议步骤；（4）在防篡改外壳内执行已批准的步骤，并在必要时撤销行动。系统不使用浮点近似；所有状态比对与代价计算均基于确定性整数运算与离散符号逻辑。
- 核心概念:
  | 组件 | 作用 | 确定性保证 |
  | EvidenceGraphDiff | 将决策变更分解为因果增量 | 基于离散节点的符号图比对 |
  | InterventionOptimizer | 以贪心搜索寻找最小代价干预 | 整数代价最小化；无分数漂移 |
  | FormalPolicyEngine | 依据 JSON 策略规则验证 | 离散状态机：ALLOW/DENY/REQUIRE_APPROVAL |
  | SafeActionExecutor | 带可追溯性与回滚的执行器 | 仅追加的不可变历史；可逆整数令牌 |
  | forensic_timeout | 对执行施加硬时限 | 由整数周期计数器驱动中断 |

- 函数:
  | 函数 | 用途 | 返回类型 |
  | diff_decisions() | 比对两个 DecisionTrace 及可选图结构 | 含布尔标志与增量列表的字典 |
  | recommend() | 推荐将决策变为 ACCEPT 的最小干预 | 带整数代价的干预记录 |
  | check() / check_action_record() | 依据正式策略校验行动 | 分类结果字符串 |
  | execute_recommendation() | 获取优化器推荐并在策略通过后执行 | ActionReceipt 或回滚令牌 |
  | rollback(n) | 回退最近 n 条行动 | 先前状态快照或 None |
  | get_action_history() | 导出历史供 ForensicBundle 使用 | 有序的 ActionRecord 列表 |
  | audit_log() | 生成符合 SIFT 标准的审计日志 | 结构化文本流 |

- 术语表:
  - **DecisionTrace（决策痕迹）**: 导致系统决策的每一项输入、触发规则及中间结论的不可变带时戳记录。
  - **Causal Delta（因果增量）**: 将变更的输入直接关联到证据图中被变更输出节点的离散变化单位。
  - **Intervention（干预）**: 为修改系统状态而刻意施加的校正操作；类似于实验装置上的校准调节。
  - **ForensicBundle（取证包）**: 防篡改的证据、日志与元数据容器，可供外部审查。
  - **SIFT**: 取证可追溯性标准接口（Standard Interface for Forensic Traceability）；下游审计工具所使用的日志格式。
  - **Rollback Token（回滚令牌）**: 以整数索引的句柄，标识已保存的检查点，从而实现确定性回退。
  - **Policy State（策略状态）**: 三类离散类别之一：ALLOW、DENY、REQUIRE_APPROVAL。
  - **Greedy Search（贪心搜索）**: 一种确定性算法，基于局部最优整数代价逐步选择下一步，直至达到目标。

- 科学说明:
  > 【科学说明】
  > 在取证文献中引用符号学框架——如皮尔士（Peirce）的溯因推理、艾柯的阐释代码、格赖斯的会话准则——是因为它们描述的是*确定性的信息流协议*，而非神秘主义。请以温度传感器为例：它将连续的热能依据固定查表转换为离散的电压状态（皮尔士的“指示符”），通过制造商代码本赋予其意义（艾柯的“代码”），并期望接收方以合作方式解读读数、不作隐藏假设（格赖斯的“合作原则”）。VIGÍA 正是如此对待决策痕迹：证据被索引，由正式策略解码，并以完全显式的方式传递。不存在隐含意涵——不变式 I4 保证每一个效应都是显式且可追溯的。

- 许可证: 

Need to check Chinese terms:
- 艾柯 (Eco) — used.
- 格赖斯 (Grice) — used.
  - In Chinese "What Is This Module?": ... 所有输出均以**取证工件**形式留存 ...


So update Chinese:
- In EvidenceGraphDiff row: "将决策变更分解为因果增量，并识别状态间的**逻辑断裂**"
- Or in Glossary: **逻辑断裂**: 两个决策状态之间的不一致路径，表现为证据图中离散节点的符号差异。


Also include the Isolation Rule and Invariant I4.

The document should be Markdown.

I will structure it with clear headers for each language. To avoid repetition of the module path in every language header, I'll put it under each language's title.

ENGLISH:
- Under "Architecture & Isolation": Layer 4 — Audit and Action. Isolation Rule: reads from models/, engine/, governance/. No downward writes. No LLM calls. Invariant I4: No implicit effects.

ESPAÑOL:
- Arquitectura y aislamiento: Capa 4 — Auditoría y Acción. Regla de aislamiento: lee de models/, engine/, governance/. No escribe hacia abajo. No llama a LLM. Invariante I4: no existen efectos implícitos.

РУССКИЙ:
- Архитектура и изоляция: Уровень 4 — Аудит и Действие. Правило изоляции: читает из models/, engine/, governance/. Не пишет вниз. Не вызывает LLM. Инвариант I4: не существует неявных эффектов.

中文:
- 架构与隔离规则: 第4层 — 审计与行动。隔离规则：读取 models/、engine/、governance/；不向下层写入；不调用 LLM。不变式 I4：不存在隐式效应。


- 艾柯: used in scientific note.
- 格赖斯: used in scientific note.


The user wrote:
- EvidenceGraphDiff — descompone cambio de decisión en deltas causales. Responde a la pregunta: "¿Qué cambió entre e..."
- InterventionOptimizer — búsqueda greedy de mínima intervención. OBJETIVO: Dado un estado que produjo REJECT o ABSTAIN, en...
- FormalPolicyEngine — validación contra reglas JSON (ALLOW/DENY/REQUIRE_APPROVAL). INVARIANTE I4: no existen efectos implícitos. Toda acción...
- SafeActionExecutor — ejecutor con trazabilidad + rollback + auditoría. PRINCIPIO: "Ninguna acción pu..."

Functions:
- forensic_timeout(): Decorador que impone un timeout a cualquier método del SafeActionExecutor. Si la ejecución supera `seconds`, lanza conc...
- decorator(): (empty)
- diff_decisions(): Calcula diferencias entre dos DecisionTrace y opcionalmente dos grafos. Returns: {"decision_changed": bool...}
- check(): Valida una acción propuesta contra la política formal. Returns: {"result": "ALLOW" | "DENY" | "REQUIRE_APP...
- check_action_record(): Valida un ActionRecord completo.
- execute_recommendation(): Obtiene recomendación del optimizer y la ejecuta si pasa la política. Decorado con @forensic_timeout(30) — H23: Si la e...
- rollback(): Revierte las últimas n acciones del historial. Retorna el estado anterior si hay rollback disponible, None si no.
- get_action_history(): Retorna historial de acciones para incluir en ForensicBundle.
- audit_log(): Log de auditoría completo para SIFT.
- wrapper(): (internal)

CONSTANTS & CONFIG: _ROOT_AUD... (incomplete) I can mention that configuration constants are defined at module root but are implementation details.


Let's structure each language section similarly:

### ENGLISH
#### Module Path
`vigia/core/audit_action.py` (incorporating `vigia/audit/evidence_graph_diff.py` and `vigia/action/safe_action_executor.py`)

#### What Is This Module?
...

#### Architecture & Design Principle
Layer 4 — Audit and Action.
Isolation Rule: ...
Invariant I4: ...

#### Key Components
Table...

#### Function Reference
Table...

#### Glossary
...

#### 【Scientific Note】
...

#### License
...

Repeat for other languages.

Now, writing the content carefully.


For the Chinese scientific note, I must use the exact required terms. The note should be in the 【科学说明】 box.


Let's draft the English scientific note carefully:
> 【Scientific Note】
> Forensic science occasionally borrows terms from semiotics—Peirce’s abduction, Eco’s interpretative codes, and Grice’s cooperative maxims—because these frameworks are *deterministic protocols for information flow*, not mystical doctrines. Consider a digital thermometer: a continuous temperature field is mapped to discrete voltage bands via a fixed manufacturer lookup table (Peirce’s *index*); the device manual tells the operator how to read those bands (Eco’s *code*); and the operator assumes the reading is presented honestly, without hidden tricks (Grice’s *cooperative principle*). VIGÍA applies the same rigor to decision traces: evidence is indexed, decoded through formal policy, and transmitted with total explicitness. There are no implicatures, no hidden states, and no vague probabilities—Invariant I4 ensures every causal effect is explicit, traceable, and reversible.

This is good.

Now Chinese scientific note:
> 【科学说明】
> 取证科学有时会借用符号学术语——皮尔士（Peirce）的溯因、艾柯的阐释代码、格赖斯的合作准则——因为它们是*确定性的信息流协议*，而非神秘主义学说。请以数字温度计为喻：连续的温度场经由固定的制造商查表被映射到离散的电压档位（皮尔士的“指示符”）；设备手册告诉操作员如何读取这些档位（艾柯的“代码”）；而操作员假定读数被诚实呈现，不含隐藏 tricks（格赖
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
