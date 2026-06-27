<!--
VIGIA Academic Documentation
Module: 5fba2910
Batch ID: vigia-doc-0032-5fba2910
Generated: 2026-05-20T14:56:47.851472+00:00
-->

## ENGLISH

**Module:** `vigia/action/vigia_mitigation_planner.py`
**Layer:** Capa 4 — Action / Execution

### What Is This Module?
This module is the surgical execution layer of the VIGÍA Forensic Suite. Its sole purpose is to transform a validated, winning abductive hypothesis into a concrete, step-by-step system-level mitigation plan for Linux platforms. Imagine a robotic surgical suite: the module prepares every instrument trajectory (commands such as `kill`, `iptables`, `userdel`), but the scalpel never moves until the lead operator explicitly approves each action. No command contains empty placeholders; if a value is unknown, the module inserts a forensic acquisition directive so the operator must resolve the gap before proceeding. The system is strictly deterministic—every decision, hash, and platform check relies on exact integer arithmetic and bitwise operations, never on floating-point approximations.

### Key Concepts

| Concept | Role | Plain-Language Description |
|---------|------|---------------------------|
| **MitigationPlanner** | Generator | Reads a ForensicBundle and builds a surgical mitigation plan. It only produces operational steps when the bundle verdict is `REJECT`. |
| **MitigationPlan** | Container | Holds the complete ordered sequence of actions, target identifiers, and forensic justifications. |
| **MitigationAction** | Atomic Step | A single, reversible or irreversible system command (e.g., terminate process, block IP). Defaults to `approved=False`. |
| **PlaybookStep** | Metadata Wrapper | Wraps an action with pre-conditions, expected post-conditions, and rollback information. |
| **ContextValidationError** | Safety Gate | Raised when an input value (user, path, PID) fails security validation (e.g., contains forbidden shell characters). |
| **ApprovalRequired** | Enforcement Rule | Exception triggered if code attempts to execute any `MitigationAction` before the operator toggles `approved` to True. |
| **PlanIntegrityError (MP-INTEG-01)** | Tamper Detector | Raised when the HMAC-based plan signature does not match the serialized plan. HMAC computation uses deterministic integer bitwise arithmetic. |
| **verify_plan_signature()** | Audit Function | Verifies the HMAC signature of a serialized plan. Returns integer-like boolean states: unmodified (`True`) or altered (`False`). |
| **execute_action()** | Entry Point | The only approved gateway for running a `MitigationAction`. Enforces platform, approval, and integrity checks. |
| **_SHELL_CHARS** / **_BLOCKED_PREFIXES** | Sanitization Lists | Constant sets of forbidden characters and command prefixes that are rejected through exact string matching, never fuzzy logic. |

### Workflow MP-WFLOW-01: Correct Approval Chain

| Step | Actor | Deterministic Operation | Outcome |
|------|-------|------------------------|---------|
| 1 | **MitigationPlanner** | Generates plan from ForensicBundle using integer-based rule indices. | Plan object created with `approved=False` on every action. |
| 2 | **Operator** | Reviews forensic acquisition directives and fills missing values. | All command parameters become fully specified strings. |
| 3 | **System** | Computes `plan_hash` via bitwise HMAC over commands + targets (exact byte-to-integer mapping). | Integrity baseline established. |
| 4 | **Operator** | Explicitly sets `approved=True` on individual actions or the full plan. | Approval flag transitions from integer 0 to integer 1. |
| 5 | **execute_action()** | Checks `sys.platform == "linux"` (strict string equality), verifies HMAC, checks `approved==True`. | Execution proceeds or a critical halt occurs. |

### Deterministic Guarantees

This module avoids all floating-point arithmetic because forensic action must be reproducible and exact.
- **Platform check:** `sys.platform == "linux"` is a strict character-by-character string equality check, not a similarity score.
- **Integrity hash:** HMAC-SHA256 operates on fixed-width integer blocks; the comparison of the computed digest against the stored signature is an exact integer equality test over a 256-bit integer space.
- **Approval state:** Represented internally as a Boolean (integer domain {0, 1}), not a probability or confidence threshold.

### Glossary

| Term | Definition |
|------|------------|
| **Abductive Hypothesis** | The inference to the best explanation (Peircean abduction) selected by the analysis layer as the most probable cause of an observed incident. |
| **ForensicBundle** | A structured collection of 取证工件 (forensic artifacts), timestamps, and inferred logical fractures delivered by the upstream analysis layer. |
| **HMAC** | Hash-based Message Authentication Code; a deterministic integer fingerprint used here to detect unauthorized modification of a mitigation plan. |
| **Surgical Mitigation** | Precision containment or remediation that affects only targeted resources, minimizing collateral damage to the host system. |
| **Forensic Acquisition Directive** | An embedded instruction (not a blank placeholder) that tells the operator exactly what evidence must be collected to resolve an unknown parameter. |
| **Logical Fracture** | A discontinuity in expected system behavior (逻辑断裂) that serves as the evidentiary basis for the winning abductive hypothesis. |

### 【Scientific Note】Peirce, Eco, and Grice Are Not Mysticism: The Sensor Analogy

In scientific literature, the terminology borrowed from Charles Sanders Peirce (abduction), Umberto Eco (semiotics), and H. P. Grice (pragmatic maxims) is sometimes mistaken for philosophical mysticism. It is not. Consider a laboratory sensor array:

- **The Sign (Peirce):** A thermocouple outputs a raw voltage. The voltage is not "meaning"; it is a physical index.
- **The Interpretant (Eco):** A calibrated firmware layer maps that voltage to a temperature reading through coded conventions (艾柯's semiotic code). Without the code, the voltage remains noise.
- **The Cooperative Maxim (Grice):** The reporting module follows 格赖斯's maxims of quality and quantity—it states only what the sensor genuinely detected, neither more nor less.

VIGÍA's mitigation planner treats forensic artifacts exactly like calibrated sensor readings. An anomalous log entry (raw sign) is decoded by the semiotic layer (rules of evidence) into a logical fracture (interpretant), and the planner acts only when the operator explicitly confirms the reading (cooperative verification). The "mystical" vocabulary is merely a formal taxonomy for information flow—from physical signal to justified action—no different from signal processing in instrumentation.

---

## ESPAÑOL

**Módulo:** `vigia/action/vigia_mitigation_planner.py`
**Capa:** 4 — Acción / Ejecución

### ¿Qué es este módulo?
Este módulo es la capa de ejecución quirúrgica de la Suite Forense VIGÍA. Su único propósito es transformar una hipótesis abductiva validada y ganadora en un plan de mitigación concreto, paso a paso, a nivel de sistema para plataformas Linux. Imagínese un quirófano robótico: el módulo prepara cada trayectoria del instrumento (comandos como `kill`, `iptables`, `userdel`), pero el bisturí no se mueve hasta que el operador principal apruebe explícitamente cada acción. Ningún comando contiene marcadores de posición vacíos; si un valor es desconocido, el módulo inserta una directiva de obtención forense para que el operador resuelva la laguna antes de continuar. El sistema es estrictamente determinista: cada decisión, hash y verificación de plataforma se basa en aritmética entera exacta y operaciones a nivel de bits, nunca en aproximaciones de coma flotante.

### Conceptos Clave

| Concepto | Rol | Descripción en lenguaje sencillo |
|----------|-----|----------------------------------|
| **MitigationPlanner** | Generador | Lee un ForensicBundle y construye un plan de mitigación quirúrgica. Solo produce pasos operativos cuando el veredicto del bundle es `REJECT`. |
| **MitigationPlan** | Contenedor | Alberga la secuencia completa ordenada de acciones, identificadores de objetivo y justificaciones forenses. |
| **MitigationAction** | Paso Atómico | Un único comando de sistema reversible o irreversible (p. ej., terminar proceso, bloquear IP). Por defecto `approved=False`. |
| **PlaybookStep** | Envoltorio de Metadatos | Envuelve una acción con pre-condiciones, post-condiciones esperadas e información de reversión. |
| **ContextValidationError** | Puerta de Seguridad | Se lanza cuando un valor de entrada (usuario, ruta, PID) falla la validación de seguridad (p. ej., contiene caracteres de shell prohibidos). |
| **ApprovalRequired** | Regla de Aplicación | Excepción disparada si el código intenta ejecutar una `MitigationAction` antes de que el operador cambie `approved` a True. |
| **PlanIntegrityError (MP-INTEG-01)** | Detector de Manipulación | Se lanza cuando la firma HMAC del plan no coincide con el plan serializado. El cálculo HMAC utiliza aritmética entera determinista a nivel de bits. |
| **verify_plan_signature()** | Función de Auditoría | Verifica la firma HMAC de un plan serializado. Devuelve estados booleanos enteros: no modificado (`True`) o alterado (`False`). |
| **execute_action()** | Punto de Entrada | La única puerta de enlace aprobada para ejecutar una `MitigationAction`. Aplica verificaciones de plataforma, aprobación e integridad. |
| **_SHELL_CHARS** / **_BLOCKED_PREFIXES** | Listas de Saneamiento | Conjuntos constantes de caracteres prohibidos y prefijos de comando que se rechazan mediante coincidencia exacta de cadenas, nunca lógica difusa. |

### Flujo de Trabajo MP-WFLOW-01: Cadena de Aprobación Correcta

| Paso | Actor | Operación Determinista | Resultado |
|------|-------|------------------------|-----------|
| 1 | **MitigationPlanner** | Genera el plan desde el ForensicBundle usando índices de regla enteros. | Objeto Plan creado con `approved=False` en cada acción. |
| 2 | **Operador** | Revisa las directivas de obtención forense y completa los valores faltantes. | Todos los parámetros del comando se convierten en cadenas completamente especificadas. |
| 3 | **Sistema** | Calcula `plan_hash` mediante HMAC a nivel de bits sobre comandos + objetivos (mapeo exacto byte-entero). | Línea base de integridad establecida. |
| 4 | **Operador** | Establece explícitamente `approved=True` en acciones individuales o en el plan completo. | Bandera de aprobación pasa de entero 0 a entero 1. |
| 5 | **execute_action()** | Comprueba `sys.platform == "linux"` (igualdad estricta de caracteres), verifica HMAC, comprueba `approved==True`. | La ejecución procede o se produce una parada crítica. |

### Garantías Deterministas

Este módulo evita toda aritmética de coma flotante porque la acción forense debe ser reproducible y exacta.
- **Verificación de plataforma:** `sys.platform == "linux"` es una comprobación de igualdad de cadena carácter por carácter, no una puntuación de similitud.
- **Hash de integridad:** HMAC-SHA256 opera sobre bloques enteros de ancho fijo; la comparación del digest calculado contra la firma almacenada es una prueba de igualdad entera exacta en un espacio de enteros de 256 bits.
- **Estado de aprobación:** Representado internamente como un booleano (dominio entero {0, 1}), no como una probabilidad o umbral de confianza.

### Glosario

| Término | Definición |
|---------|------------|
| **Hipótesis Abductiva** | Inferencia a la mejor explicación (abducción peirceana) seleccionada por la capa de análisis como la causa más probable de un incidente observado. |
| **ForensicBundle** | Colección estructurada de artefactos forenses, marcas de tiempo y fracturas lógicas inferidas entregadas por la capa de análisis superior. |
| **HMAC** | Código de Autenticación de Mensajes basado en Hash; una huella dactilar entera determinista usada aquí para detectar modificación no autorizada de un plan de mitigación. |
| **Mitigación Quirúrgica** | Contención o remediación de precisión que afecta solo los recursos objetivo, minimizando el daño colateral al sistema anfitrión. |
| **Directiva de Obtención Forense** | Una instrucción incrustada (no un marcador vacío) que indica exactamente al operador qué evidencia debe recolectar para resolver un parámetro desconocido. |
| **Fractura Lógica** | Una discontinuidad en el comportamiento esperado del sistema (逻辑断裂) que sirve como base probatoria para la hipótesis abductiva ganadora. |

### 【Nota Científica】Peirce, Eco y Grice no son misticismo: la analogía del sensor

En literatura científica, la terminología tomada de Charles Sanders Peirce (abducción), Umberto Eco (semiótica) y H. P. Grice (máximas pragmáticas) a veces se confunde con misticismo filosófico. No lo es. Considérese una matriz de sensores de laboratorio:

- **El Signo (Peirce):** Un termopar emite un voltaje crudo. El voltaje no es "significado"; es un índice físico.
- **El Interpretante (Eco):** Un firmware calibrado mapea ese voltaje a una lectura de temperatura mediante convenciones codificadas (código semiótico de Eco). Sin el código, el voltaje permanece como ruido.
- **La Máxima Cooperativa (Grice):** El módulo de reporte sigue las máximas de Grice de calidad y cantidad: declara solo lo que el sensor detectó genuinamente, ni más ni menos.

El planificador de mitigación de VIGÍA trata los artefactos forenses exactamente como lecturas de sensores calibrados. Una entrada de registro anómala (signo crudo) es decodificada por la capa semiótica (reglas de evidencia) en una fractura lógica (interpretante), y el planificador actúa solo cuando el operador confirma explícitamente la lectura (verificación cooperativa). El vocabulario "místico" es meramente una taxonomía formal para el flujo de información—de señal física a acción justificada—no diferente del procesamiento de señales en instrumentación.

---

## РУССКИЙ

**Модуль:** `vigia/action/vigia_mitigation_planner.py`
**Уровень:** 4 — Действие / Исполнение

### Что представляет собой этот модуль?
Этот модуль является хирургическим исполнительным уровнем набора инструментов судебной экспертизы VIGÍA. Его единственная цель — преобразовать проверенную победившую абдуктивную гипотезу в конкретный пошаговый план реагирования на уровне системы для платформ Linux. Представьте себе роботизированную операционную: модуль готовит траекторию каждого инструмента (команды типа `kill`, `iptables`, `userdel`), но скальпель не движется, пока ведущий оператор явно не утвердит каждое действие. Ни одна команда не содержит пустых заполнителей; если значение неизвестно, модуль вставляет директиву судебного получения, чтобы оператор устранил пробел перед продолжением. Система строго детерминирована — каждое решение, хеш и проверка платформы основаны на точной целочисленной арифметике и побитовых операциях, а не на приближениях с плавающей запятой.

### Ключевые понятия

| Понятие | Роль | Описание простым языком |
|---------|------|-------------------------|
| **MitigationPlanner** | Генератор | Считывает ForensicBundle и строит план хирургического реагирования. Производит операционные шаги только при вердикте `REJECT`. |
| **MitigationPlan** | Контейнер | Содержит полную упорядоченную последовательность действий, идентификаторов целей и судебных обоснований. |
| **MitigationAction** | Атомарный шаг | Одна обратимая или необратимая системная команда (например, завершить процесс, заблокировать IP). По умолчанию `approved=False`. |
| **PlaybookStep** | Обертка метаданных | Оборачивает действие в предусловия, ожидаемые постусловия и информацию об откате. |
| **ContextValidationError** | Защитный шлюз | Возбуждается, когда входное значение (пользователь, путь, PID) не проходит проверку безопасности (например, содержит запрещенные символы оболочки). |
| **ApprovalRequired** | Правило принудительного применения | Исключение, возникающее при попытке выполнить `MitigationAction` до того, как оператор установит `approved` в True. |
| **PlanIntegrityError (MP-INTEG-01)** | Детектор подделки | Возбуждается, когда подпись HMAC плана не совпадает с сериализованным планом. Вычисление HMAC использует детерминированную целочисленную побитовую арифметику. |
| **verify_plan_signature()** | Функция аудита | Проверяет подпись HMAC сериализованного плана. Возвращает целочисленные логические состояния: не изменен (`True`) или изменен (`False`). |
| **execute_action()** | Точка входа | Единственный утвержденный шлюз для выполнения `MitigationAction`. Осуществляет проверки платформы, утверждения и целостности. |
| **_SHELL_CHARS** / **_BLOCKED_PREFIXES** | Списки очистки | Постоянные наборы запрещенных символов и префиксов команд, которые отклоняются посредством точного сопоставления строк, а не нечеткой логики. |

### Рабочий процесс MP-WFLOW-01: Правильная цепочка утверждения

| Шаг | Субъект | Детерминированная операция | Результат |
|-----|---------|----------------------------|-----------|
| 1 | **MitigationPlanner** | Генерирует план из ForensicBundle с использованием целочисленных индексов правил. | Объект Plan создан с `approved=False` для каждого действия. |
| 2 | **Оператор** | Проверяет директивы судебного получения и заполняет недостающие значения. | Все параметры команд становятся полностью определенными строками. |
| 3 | **Система** | Вычисляет `plan_hash` посредством побитового HMAC по командам + целям (точное отображение байт-целое). | Установлен базовый уровень целостности. |
| 4 | **Оператор** | Явно устанавливает `approved=True` для отдельных действий или всего плана. | Флаг утверждения переходит из целого 0 в целое 1. |
| 5 | **execute_action()** | Проверяет `sys.platform == "linux"` (строгое посимвольное равенство строк), верифицирует HMAC, проверяет `approved==True`. | Выполнение продолжается или происходит критическая остановка. |

### Гарантии детерминизма

Этот модуль исключает любую арифметику с плавающей запятой, поскольку судебное действие должно быть воспроизводимым и точным.
- **Проверка платформы:** `sys.platform == "linux"` — это строгая посимвольная проверка равенства строк, а не оценка сходства.
- **Хеш целостности:** HMAC-SHA256 работает с блоками фиксированной ширины в целочисленном представлении; сравнение вычисленного дайджеста с хранимой подписью является точным тестом целочисленного равенства в 256-битном целочисленном пространстве.
- **Состояние утверждения:** Представлено внутренне как булево значение (целочисленная область {0, 1}), а не как вероятность или порог доверия.

### Глоссарий

| Термин | Определение |
|--------|-------------|
| **Абдуктивная гипотеза** | Вывод к наилучшему объяснению (пирсовская абдукция), выбранный аналитическим уровнем как наиболее вероятная причина наблюдаемого инцидента. |
| **ForensicBundle** | Структурированный набор артефактов цифровой криминалистики, временных меток и выведенных логических разрывов, переданный вышестоящим аналитическим уровнем. |
| **HMAC** | Код аутентификации сообщений на основе хеша; детерминированный целочисленный отпечаток, используемый здесь для обнаружения несанкционированного изменения плана реагирования. |
| **Хирургическое реагирование** | Точечное сдерживание или устранение, затрагивающее только целевые ресурсы, минимизируя побочный ущерб хост-системе. |
| **Директива судебного получения** | Встроенная инструкция (не пустой заполнитель), точно указывающая оператору, какие доказательства необходимо собрать для разрешения неизвестного параметра. |
| **Логический разрыв** | Разрыв в ожидаемом поведении системы (逻辑断裂), служащий доказательственной основой для победившей абдуктивной гипотезы. |

### 【Научное примечание】Пирс, Эко и Грайс — не мистицизм: аналогия с датчиком

В научной литературе терминология, заимствованная у Чарльза Сандерса Пирса (абдукция), Умберто Эко (семиотика) и Г. П. Грайса (прагматические максимы), иногда ошибочно принимается за философский мистицизм. Это не так. Рассмотрим лабораторную матрицу датчиков:

- **Знак (Пирс):** Термопара выдает необработанное напряжение. Напряжение — это не «смысл»; это физический индекс.
- **Интерпретант (Эко):** Калиброванный прошивочный уровень отображает это напряжение на показание температуры посредством кодированных конвенций (семиотический код Эко). Без кода напряжение остается шумом.
- **Кооперативный максим (Грайс):** Модуль отчетности следует максимам Грайса качества и количества — он сообщает только то, что датчик действительно зафиксировал, ни больше ни меньше.

Планировщик реагирования VIGÍA обращается с судебными артефактами точно так же, как с откалиброванными показаниями датчиков. Аномальная запись журнала (необработанный знак) декодируется семиотическим уровнем (правила доказательств) в логический разрыв (интерпретант), и планировщик действует только тогда, когда оператор явно подтверждает показание (кооперативная верификация). «Мистический» словарь является лишь формальной таксономией потока информации — от физического сигнала к обоснованному действию — ничем не отличающейся от обработки сигналов в измерительной технике.

---

## 中文

**模块路径：** `vigia/action/vigia_mitigation_planner.py`
**层级：** 4 — 行动 / 执行

### 本模块是什么？
本模块是 VIGÍA 取证套件的外科式执行层。其唯一目的是将经过验证的胜出溯因假设转化为针对 Linux 平台的具体、分步系统级缓解计划。想象一个机器人手术室：模块准备好每一个器械的运动轨迹（如 `kill`、`iptables`、`userdel` 等命令），但手术刀直到主操作员明确批准每项操作后才会启动。任何命令均不含空白占位符；若某参数值未知，模块将插入取证采集指令，要求操作员在继续之前解决该缺口。系统严格遵循确定性原则——每一个决策、哈希值与平台检查均依赖精确整数运算与按位操作，绝不使用浮点近似。

### 核心概念

| 概念 | 角色 | 通俗描述 |
|------|------|----------|
| **MitigationPlanner** | 生成器 | 读取 ForensicBundle 并构建外科式缓解计划。仅当 bundle 裁决为 `REJECT` 时才生成操作步骤。 |
| **MitigationPlan** | 容器 | 保存完整有序的操作序列、目标标识符与取证依据。 |
| **MitigationAction** | 原子步骤 | 单条可逆或不可逆的系统命令（如终止进程、封锁 IP）。默认 `approved=False`。 |
| **PlaybookStep** | 元数据包装器 | 为操作附加前置条件、预期后置条件及回滚信息。 |
| **ContextValidationError** | 安全门控 | 当输入值（用户名、路径、PID）未通过安全验证（如含有禁用 shell 字符）时抛出。 |
| **ApprovalRequired** | 执行规则 | 若代码在操作员将 `approved` 设为 True 之前尝试执行 `MitigationAction`，则触发此异常。 |
| **PlanIntegrityError (MP-INTEG-01)** | 篡改检测器 | 当计划的 HMAC 签名与序列化计划不匹配时抛出。HMAC 计算采用确定性整数按位运算。 |
| **verify_plan_signature()** | 审计函数 | 验证序列化计划的 HMAC 签名。返回整数布尔状态：未修改（`True`）或已被篡改（`False`）。 |
| **execute_action()** | 入口点 | 执行 `MitigationAction` 的唯一授权通道。强制执行平台、批准与完整性检查。 |
| **_SHELL_CHARS** / **_BLOCKED_PREFIXES** | 净化列表 | 被拒绝字符与命令前缀的常量集，通过精确字符串匹配进行拒绝，不使用模糊逻辑。 |

### 工作流 MP-WFLOW-01：正确的批准链

| 步骤 | 主体 | 确定性操作 | 结果 |
|------|------|------------|------|
| 1 | **MitigationPlanner** | 使用整数规则索引从 ForensicBundle 生成计划。 | Plan 对象创建完毕，每项操作均设 `approved=False`。 |
| 2 | **操作员** | 审查取证采集指令并填写缺失值。 | 所有命令参数均变为完整字符串。 |
| 3 | **系统** | 通过对命令+目标的按位 HMAC（精确字节-整数映射）计算 `plan_hash`。 | 完整性基线建立。 |
| 4 | **操作员** | 对单项操作或整个计划显式设置 `approved=True`。 | 批准标志从整数 0 转变为整数 1。 |
| 5 | **execute_action()** | 检查 `sys.platform == "linux"`（严格字符串相等），验证 HMAC，检查 `approved==True`。 | 执行继续，或发生紧急停止。 |

### 确定性保证

本模块规避所有浮点运算，因为取证操作必须具有可复现性与精确性。
- **平台检查：** `sys.platform == "linux"` 是逐字符的严格字符串相等检查，而非相似度打分。
- **完整性哈希：** HMAC-SHA256 对固定宽度整数块进行运算；计算所得摘要与存储签名的比对是对 256 位整数空间进行的精确整数相等测试。
- **批准状态：** 内部以布尔值（整数域 {0, 1}）表示，而非概率或置信度阈值。

### 术语表

| 术语 | 定义 |
|------|------|
| **溯因假设** | 由分析层选定的"最佳解释推断"（皮尔士溯因法），作为所观察事件最可能原因的结论。 |
| **ForensicBundle** | 由上游分析层传递的取证工件、时间戳及推断逻辑断裂的结构化集合。 |
| **HMAC** | 基于哈希的消息认证码；此处用作确定性整数指纹，以检测对缓解计划的未授权修改。 |
| **外科式缓解** | 仅针对目标资源的精准遏制或修复，最大限度降低对宿主系统的附带损害。 |
| **取证采集指令** | 嵌入式指令（非空白占位符），精确告知操作员需收集哪些证据以解决未知参数。 |
| **逻辑断裂** | 系统预期行为中的不连续性（逻辑断裂），作为胜出溯因假设的证据基础。 |

### 【科学说明】皮尔士、艾柯与格赖斯并非神秘主义：传感器类比

在科学文献中，借自查尔斯·桑德斯·皮尔士（溯因法）、翁贝托·艾柯（符号学）与格赖斯（语用学准则）的术语有时被误认为哲学神秘主义。事实并非如此。请考虑一组实验室传感器阵列：

- **符号（皮尔士）：** 热电偶输出原始电压。电压并非"意义"，而是物理索引。
- **解释项（艾柯）：** 经过校准的固件层通过编码惯例（艾柯的符号学代码）将该电压映射为温度读数。没有代码，电压只是噪声。
- **合作准则（格赖斯）：** 报告模块遵循格赖斯的质量与数量准则——它只陈述传感器真实检测到的内容，不多也不少。

VIGÍA 的缓解规划器将取证工件视为经过校准的传感器读数。一条异常日志条目（原始符号）被符号学层（证据规则）解码为逻辑断裂（解释项），规划器仅在操作员明确确认读数（合作验证）后才采取行动。这套"神秘"词汇不过是信息流的形式化分类体系——从物理信号到正当行动——与仪器仪表中的信号处理并无本质区别。

---

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
