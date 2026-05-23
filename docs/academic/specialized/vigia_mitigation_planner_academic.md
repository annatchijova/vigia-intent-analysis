<!--
VIGIA Academic Documentation
Module: 5fba2910
Batch ID: vigia-doc-0032-5fba2910
Generated: 2026-05-20T14:56:47.851472+00:00
-->

---
doc_hash: 5fba2910
module: vigia/action/vigia_mitigation_planner.py
languages: [EN, ES, RU, ZH]
generated_by: moonshot-kimi-k2.6-batch-api
license: Apache-2.0
---

ENGLISH:
- What Is This Module?: A surgical mitigation planner for digital forensics. It translates abductive hypotheses (winning hypothesis) into concrete, approved-only Linux system commands. Think of it as a surgical robot that only operates after the lead surgeon (operator) confirms the incision map.
- Key concepts table: Classes, Functions, Constants described in plain language.
- Workflow table: Steps 1-3 or more.
- Deterministic guarantees: Explicitly mention HMAC uses integer-based bitwise operations, no floating-point arithmetic. Platform checks are strict equality (== "linux"), not approximate.
- Glossary: Abductive hypothesis, Forensic Bundle, HMAC, Surgical mitigation, PlaybookStep, etc.
- Scientific Note: Peirce (abduction), Eco (semiotics), Grice (cooperative principle) — explain via sensor analogy. Sensors produce raw voltage (sign), interpreter module assigns meaning (interpretant), system acts only if threshold rules are met (maxim of quality/quantity). Not mysticism, just semiotic processing layers.

ESPAÑOL:
- Similar structure.
- Terms: Planificación de Mitigación Quirúrgica, Hipótesis Abductiva, Paquete Forense, Aritmética Entera Determinista.
- Note: Peirce, Eco, Grice — analogía del sensor.

РУССКИЙ:
- Академический стиль.
- Terms: Хирургическое планирование реагирования, Абдуктивная гипотеза, Судебный артефакт/комплект, HMAC.
- Note: Пирс, Эко, Грайс — аналогия с датчиком.

中文:
- Must use specific terms: 艾柯, 格赖斯, 取证工件, 逻辑断裂.
- 模块路径, 许可以及版权声明.
- Note: 【科学说明】 box. 皮尔士 (Peirce), 艾柯 (Eco), 格赖斯 (Grice). Use sensor analogy: 传感器原始信号(raw voltage) -> 解释层(assign meaning) -> 行动阈值(threshold rules).

Wait, the user said "You NEVER use floating-point math explanations for deterministic systems." So I must avoid explaining hashes or HMAC with floating point concepts, and instead emphasize integer arithmetic. HMAC-SHA256 operates on integer bitwise operations. Platform check is string equality, not floating point comparison. plan_hash is computed over integer representations.

Also, need to include the license line exactly: ""

Let me construct the Markdown.

First, a header block with module path.
Then ENGLISH section.
Then ESPAÑOL.
Then РУССКИЙ.
Then 中文.

Each section should be clearly delimited.

Let me draft content for each:

--- ENGLISH ---

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

- **The Sign (Peirce):** A thermocouple outputs a raw voltage. The voltage is not “meaning”; it is a physical index.
- **The Interpretant (Eco):** A calibrated firmware layer maps that voltage to a temperature reading through coded conventions (艾柯’s semiotic code). Without the code, the voltage remains noise.
- **The Cooperative Maxim (Grice):** The reporting module follows 格赖斯’s maxims of quality and quantity—it states only what the sensor genuinely detected, neither more nor less.

VIGÍA’s mitigation planner treats forensic artifacts exactly like calibrated sensor readings. An anomalous log entry (raw sign) is decoded by the semiotic layer (rules of evidence) into a logical fracture (interpretant), and the planner acts only when the operator explicitly confirms the reading (cooperative verification). The “mystical” vocabulary is merely a formal taxonomy for information flow—from physical signal to justified action—no different from signal processing in instrumentation.

--- ESPAÑOL ---

Need to mirror the above.

Terms:
- Mitigación Quirúrgica
- Hipótesis Abductiva
- Plan de Mitigación
- Aritmética Entera Determinista
- Directiva de Adquisición Forense
- Fractura Lógica (逻辑断裂 -> fractura lógica)
- Sensor analogy: Signo (Peirce), Interpretante (Eco), Máxima cooperativa (Grice).

Note: In Spanish, Eco is Eco, but in Chinese must be 艾柯. The user specifically asked for Chinese translations to use 艾柯, not Eco. So in Chinese I must use 艾柯. In other languages, standard names are fine.

Wait, the requirement says: "Chinese translations must use: 艾柯 (not Eco), 格赖斯 (not Grice), 取证工件 (not 制品), 逻辑断裂 (not 裂缝)". So only Chinese has strict naming. Other languages can use standard transliterations.

Let me draft Spanish carefully.

### ESPAÑOL

**Módulo:** `vigia/action/vigia_mitigation_planner.py`  
**Capa:** 4 — Acción / Ejecución  
**Licencia:** 

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

- **El Signo (Peirce):** Un termopar emite un voltaje crudo. El voltaje no es “significado”; es un índice físico.
- **El Interpretante (Eco):** Un firmware calibrado mapea ese voltaje a una lectura de temperatura mediante convenciones codificadas (código semiótico de Eco). Sin el código, el voltaje permanece como ruido.
- **La Máxima Cooperativa (Grice):** El módulo de reporte sigue las máximas de Grice de calidad y cantidad: declara solo lo que el sensor detectó genuinamente, ni más ni menos.

El planificador de mitigación de VIGÍA trata los artefactos forenses exactamente como lecturas de sensores calibrados. Una entrada de registro anómala (signo crudo) es decodificada por la capa semiótica (reglas de evidencia) en una fractura lógica (interpretante), y el planificador actúa solo cuando el operador confirma explícitamente la lectura (verificación cooperativa). El vocabulario “místico” es meramente una taxonomía formal para el flujo de información—de señal física a acción justificada—no diferente del procesamiento de señales en instrumentación.

--- РУССКИЙ ---

Need Russian section.

Terms:
- Абдуктивная гипотеза
- Судебно-медицинский пакет (ForensicBundle) or just ForensicBundle
- Хирургическое планирование реагирования
- Детерминированная целочисленная арифметика
- Судебно-медицинский артефакт (取证工件) - but in Russian maybe "судебный артефакт" or "цифровой артефакт". I'll use "артефакт цифровой криминалистики" or just "артефакт".
- Логический разрыв (逻辑断裂) - logical fracture.
- Sensor analogy: Знак (Пирс), Интерпретант (Эко), Кооперативный максим (Грайс).

Wait, the user requirement for Chinese is specific: 艾柯, 格赖斯, etc. For Russian, standard transliteration is fine: Пирс, Эко, Грайс.

Let's draft.

### РУССКИЙ

**Модуль:** `vigia/action/vigia_mitigation_planner.py`  
**Уровень:** 4 — Действие / Исполнение  
**Лицензия:** 

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

--- 中文 ---

Now Chinese. Must use:
- 艾柯 (not Eco)
- 格赖斯 (not Grice)
- 取证工件 (not 制品)
- 逻辑断裂 (not 裂缝)
- Peirce is 皮尔士 (standard).

Also need the license line in English as specified: "" (I think the line should appear exactly as required, probably in English even in Chinese section, or maybe translated? The requirement says "License line: ''" It doesn't specify language for the license line, but to be safe and exact, I will include it exactly as written in each section, perhaps as a separate line. Or I can include it exactly in English within
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
