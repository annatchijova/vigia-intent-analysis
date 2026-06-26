<!--
VIGIA Academic Documentation
Module: 61a43ef6
Batch ID: vigia-doc-0127-61a43ef6
Generated: 2026-05-20T14:56:47.871873+00:00
-->

## ENGLISH

### What Is This Module?

`vigia/security/vigia_seguridad.py` (internal codename "Cocinero") is the deterministic security kernel of the VIGÍA forensic architecture. It centralizes four defensive primitives: (1) ASCII sanitization, enforcing a strict 7-bit character boundary on untrusted inputs to eliminate non-printable control sequences; (2) path sandboxing, restricting filesystem traversal to an enumerated allow-list of directories; (3) prompt injection shielding, neutralizing adversarial substrings through lexical normalization before dispatch to language-model interfaces; and (4) subprocess whitelisting, permitting execution only of cryptographically verified binaries.

All validation logic is based on exact set-membership tests and discrete grammar rules. Access-control decisions require no probabilistic scoring, no statistical approximation, and no floating-point arithmetic. This architecture ensures that the security kernel behaves identically in every invocation given identical inputs—a mandatory property for forensic tooling subject to the Daubert standard.

### Key Concepts

| Concept | Definition | Technical Role |
|---|---|---|
| **ASCII sanitization** | Enforcement of a 7-bit printable character boundary | Eliminates control-sequence injection from untrusted data |
| **Path sandboxing** | Restriction of filesystem operations to an enumerated allow-list | Prevents directory traversal and evidence contamination |
| **Prompt injection shield** | Lexical neutralization of adversarial substrings | Protects LLM interfaces from manipulation before analysis |
| **Subprocess whitelist** | Execution permit for cryptographically verified binaries only | Eliminates supply-chain attack surface |
| **Exact-set membership** | Categorical presence test with no probabilistic scoring | Deterministic, reproducible access-control decision |
| **Lexical normalization** | Canonical transformation of symbolic input into a discrete grammar form | Makes adversarial substrings structurally inert |

> **【Scientific Note】**
> Peirce's Firstness is the raw untrusted input byte stream; Secondness is the module's categorical comparison against the allow-list or the ASCII boundary (the Boolean reaction that rejects or passes); Thirdness is the repeatable security rule applied uniformly to every invocation. Eco's encyclopedia principle defines which byte patterns count as "adversarial"—the module's allow-lists encode the shared semantic boundary between safe and unsafe input. Grice's maxim of Quality ensures the module reports exactly one outcome per input: pass or reject, with no hedged probability. Exact integer arithmetic means every security decision is fully reproducible and independently auditable.

### Glossary

1. **ASCII sanitization** — Enforcement of a strict 7-bit printable character boundary on untrusted input streams.
2. **Path sandboxing** — Restriction of all filesystem traversal operations to a pre-enumerated, cryptographically anchored allow-list.
3. **Prompt injection shielding** — Lexical neutralization of adversarial substrings in user-supplied text before it reaches language-model interfaces.
4. **Subprocess whitelisting** — A security control permitting execution only of binaries whose SHA-256 digest matches a pre-approved catalog.
5. **Exact-set membership** — A categorical presence test: the input is either in the allow-set or it is not, with no probabilistic intermediate.
6. **Lexical normalization** — Canonical transformation of symbolic input into a discrete grammar form that renders adversarial patterns structurally inert.
7. **Security primitive** — An atomic, indivisible security-control mechanism forming the lowest-level building block of a defense-in-depth architecture.
8. **Allow-list directory** — A directory explicitly enumerated in the security configuration as a permissible target for filesystem operations.
9. **Cryptographic verification** — Confirmation that a binary's SHA-256 digest matches a pre-approved entry, guaranteeing supply-chain integrity.
10. **Deterministic kernel** — A subsystem whose outputs are entirely determined by discrete inputs, with no stochastic variation across invocations.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## ESPAÑOL

### ¿Qué es este módulo?

`vigia/security/vigia_seguridad.py` (nombre interno "Cocinero") es el núcleo de seguridad determinista de la arquitectura forense VIGÍA. Centraliza cuatro primitivas defensivas: (1) saneamiento ASCII, imponiendo un límite estricto de 7 bits a las entradas no confiables para eliminar secuencias de control no imprimibles; (2) aislamiento de rutas, restringiendo la navegación del sistema de archivos a una lista blanca enumerada de directorios; (3) blindaje contra inyección de prompts, neutralizando subcadenas adversarias mediante normalización léxica antes del envío a interfaces de modelos de lenguaje; y (4) lista blanca de subprocesos, permitiendo la ejecución únicamente de binarios verificados criptográficamente.

Toda la lógica de validación se basa en pruebas exactas de pertenencia a conjuntos y reglas gramaticales discretas. Las decisiones de control de acceso no requieren puntuación probabilística, ni aproximación estadística, ni aritmética de punto flotante. Esta arquitectura garantiza que el núcleo de seguridad se comporte de manera idéntica en cada invocación para entradas idénticas, propiedad mandatoria para herramientas forenses sujetas al estándar Daubert.

### Conceptos Clave

| Concepto | Definición | Rol Técnico |
|---|---|---|
| **Saneamiento ASCII** | Aplicación de un límite de caracteres imprimibles de 7 bits | Elimina la inyección de secuencias de control en datos no confiables |
| **Aislamiento de rutas** | Restricción de operaciones del sistema de archivos a una lista blanca enumerada | Previene el traversal de directorios y la contaminación de evidencia |
| **Blindaje anti-inyección** | Neutralización léxica de subcadenas adversarias | Protege las interfaces LLM de manipulación antes del análisis |
| **Lista blanca de subprocesos** | Permiso de ejecución solo para binarios verificados criptográficamente | Elimina la superficie de ataque de la cadena de suministro |
| **Pertenencia exacta a conjuntos** | Prueba categórica de presencia sin puntuación probabilística | Decisión de control de acceso determinista y reproducible |
| **Normalización léxica** | Transformación canónica de entrada simbólica a forma gramatical discreta | Hace que las subcadenas adversarias sean estructuralmente inertes |

> **【Nota Científica】**
> La Primereidad de Peirce es el flujo bruto de bytes de entrada no confiable; la Segundidad es la comparación categórica del módulo contra la lista blanca o el límite ASCII (la reacción booleana que rechaza o permite); la Terceridad es la regla de seguridad repetible aplicada uniformemente a cada invocación. El principio de enciclopedia de Eco define qué patrones de bytes cuentan como "adversarios": las listas blancas del módulo codifican el límite semántico compartido entre entradas seguras e inseguras. La máxima de Calidad de Grice garantiza que el módulo informe exactamente un resultado por entrada: permitir o rechazar, sin probabilidad ambigua. La aritmética entera exacta significa que cada decisión de seguridad es completamente reproducible e independientemente auditable.

### Glosario

1. **Saneamiento ASCII** — Aplicación de un límite estricto de caracteres imprimibles de 7 bits a flujos de entrada no confiables.
2. **Aislamiento de rutas** — Restricción de todas las operaciones de navegación del sistema de archivos a una lista blanca preestablecida y anclada criptográficamente.
3. **Blindaje contra inyección de prompts** — Neutralización léxica de subcadenas adversarias en texto proporcionado por usuarios antes de que alcance interfaces de modelos de lenguaje.
4. **Lista blanca de subprocesos** — Control de seguridad que permite la ejecución solo de binarios cuyo resumen SHA-256 coincida con un catálogo preaprobado.
5. **Pertenencia exacta a conjuntos** — Prueba categórica de presencia: la entrada está o no está en el conjunto permitido, sin intermedios probabilísticos.
6. **Normalización léxica** — Transformación canónica de entrada simbólica a una forma gramatical discreta que vuelve los patrones adversarios estructuralmente inertes.
7. **Primitiva de seguridad** — Mecanismo de control de seguridad atómico e indivisible que forma el bloque básico de una arquitectura de defensa en profundidad.
8. **Directorio de lista blanca** — Directorio explícitamente enumerado en la configuración de seguridad como destino permisible para operaciones del sistema de archivos.
9. **Verificación criptográfica** — Confirmación de que el resumen SHA-256 de un binario coincide con una entrada preaprobada, garantizando la integridad de la cadena de suministro.
10. **Núcleo determinista** — Subsistema cuyas salidas están completamente determinadas por entradas discretas, sin variación estocástica entre invocaciones.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## РУССКИЙ

### Что это за модуль?

`vigia/security/vigia_seguridad.py` (кодовое имя «Cocinero») — это детерминированное ядро безопасности судебно-аналитической архитектуры VIGÍA. Оно централизует четыре защитных примитива: (1) ASCII-санитизацию со строгим 7-битным ограничением недоверенных входных данных для устранения непечатаемых управляющих последовательностей; (2) изоляцию путей, ограничивающую обход файловой системы перечисленным каталогом белого списка; (3) экранирование инъекций промптов, нейтрализующее состязательные подстроки лексической нормализацией перед передачей в интерфейсы языковых моделей; и (4) белый список подпроцессов, разрешающий исполнение только криптографически верифицированных бинарных файлов.

Вся логика проверки основана на точных проверках членства в множествах и дискретных грамматических правилах. Решения по контролю доступа не требуют вероятностного оценивания, статистических приближений или арифметики с плавающей запятой. Эта архитектура гарантирует, что ядро безопасности ведёт себя идентично при каждом вызове с идентичными входными данными — обязательное свойство для криминалистических инструментов, подпадающих под стандарт Добера.

### Ключевые концепции

| Концепция | Определение | Техническая роль |
|---|---|---|
| **ASCII-санитизация** | Принудительное установление 7-битного ограничения для печатаемых символов | Устраняет инъекцию управляющих последовательностей из недоверенных данных |
| **Изоляция путей** | Ограничение операций файловой системы перечисленным белым списком | Предотвращает обход каталогов и загрязнение доказательств |
| **Экранирование инъекций промптов** | Лексическая нейтрализация состязательных подстрок | Защищает интерфейсы LLM от манипуляций до начала анализа |
| **Белый список подпроцессов** | Разрешение на выполнение только криптографически верифицированных бинарников | Устраняет поверхность атаки цепочки поставок |
| **Точное членство в множестве** | Категориальная проверка присутствия без вероятностного оценивания | Детерминированное, воспроизводимое решение по контролю доступа |
| **Лексическая нормализация** | Каноническое преобразование символьного входа в дискретную грамматическую форму | Делает состязательные подстроки структурно инертными |

> **【Научное примечание】**
> Первичность Пирса — это необработанный поток недоверенных входных байтов; Вторичность — это категориальное сравнение модуля с белым списком или ASCII-границей (булева реакция, отклоняющая или пропускающая); Третичность — это повторяемое правило безопасности, единообразно применяемое к каждому вызову. Принцип энциклопедии Эко определяет, какие байтовые паттерны считаются «состязательными»: белые списки модуля кодируют разделяемую семантическую границу между безопасным и небезопасным входом. Максима Качества Грайса гарантирует, что модуль сообщает ровно один результат для каждого входа: пропустить или отклонить, без неоднозначной вероятности. Детерминированная целочисленная арифметика означает, что каждое решение по безопасности полностью воспроизводимо и независимо проверяемо.

### Глоссарий

1. **ASCII-санитизация** — Принудительное применение строгого ограничения на 7-битные печатаемые символы к недоверенным входным потокам.
2. **Изоляция путей** — Ограничение всех операций обхода файловой системы предварительно перечисленным, криптографически привязанным белым списком.
3. **Экранирование инъекций промптов** — Лексическая нейтрализация состязательных подстрок в пользовательском тексте до его поступления к интерфейсам языковых моделей.
4. **Белый список подпроцессов** — Средство контроля безопасности, разрешающее выполнение только тех бинарников, чей дайджест SHA-256 соответствует предварительно одобренному каталогу.
5. **Точное членство в множестве** — Категориальная проверка присутствия: входные данные либо содержатся в разрешённом множестве, либо нет, без вероятностных промежуточных состояний.
6. **Лексическая нормализация** — Каноническое преобразование символьного входа в дискретную грамматическую форму, делающую состязательные паттерны структурно инертными.
7. **Защитный примитив** — Атомарный, неделимый механизм контроля безопасности, формирующий базовый блок архитектуры глубокой защиты.
8. **Каталог белого списка** — Каталог, явно перечисленный в конфигурации безопасности как допустимая цель для операций файловой системы.
9. **Криптографическая верификация** — Подтверждение того, что дайджест SHA-256 бинарника соответствует предварительно одобренной записи, гарантируя целостность цепочки поставок.
10. **Детерминированное ядро** — Подсистема, выходные данные которой полностью определяются дискретными входными данными, без стохастической вариации между вызовами.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## 中文

### 这是什么模块？

`vigia/security/vigia_seguridad.py` 模块（内部代号"Cocinero"）是 VIGÍA 取证架构的确定性安全内核。它集中四项防御原语：(1) ASCII 净化，对不可信输入强制执行 7 位字符边界以消除不可打印控制序列；(2) 路径沙箱，将文件系统遍历限制在枚举的允许目录内；(3) 提示注入防护，通过词汇归一化在发送至语言模型接口前中和对抗性子串；(4) 子进程白名单，仅允许执行经密码学验证的二进制文件。

所有验证逻辑基于精确集合成员关系与离散语法规则。访问控制决策不需要概率评分、统计近似或浮点运算。该架构确保安全内核在相同输入下的每次调用行为完全一致——这是受道伯特标准约束的取证工具所必须具备的属性。

### 核心概念

| 概念 | 定义 | 技术作用 |
|---|---|---|
| **ASCII 净化** | 对可打印字符实施 7 位边界限制 | 消除来自不可信数据的控制序列注入 |
| **路径沙箱** | 将文件系统操作限制在枚举的白名单内 | 防止目录遍历和证据污染 |
| **注入防护盾** | 对抗性子串的词汇中和处理 | 在分析前保护 LLM 接口免受操纵 |
| **子进程白名单** | 仅允许执行经密码学验证的二进制文件 | 消除供应链攻击面 |
| **精确集合成员** | 无概率评分的类别存在性检验 | 确定性、可重现的访问控制决策 |
| **词汇归一化** | 将符号输入规范化转换为离散语法形式 | 使对抗性子串在结构上失效 |

> **【科学说明】**
> 皮尔斯的初性是原始的不可信输入字节流；二性是模块对白名单或 ASCII 边界的类别比较（拒绝或通过的布尔反应）；三性是统一应用于每次调用的可重复安全规则。艾柯的百科全书原则定义哪些字节模式算作"对抗性"——模块的白名单编码了安全输入与不安全输入之间共享的语义边界。格赖斯的质量准则确保模块对每个输入恰好报告一个结果：通过或拒绝，无模糊概率。精确整数运算意味着每个安全决策完全可重现，可被独立审计。

### 术语表

1. **ASCII 净化** — 对不可信输入流强制执行严格的 7 位可打印字符边界限制。
2. **路径沙箱** — 将所有文件系统遍历操作限制在预先枚举的、以密码学方式锚定的白名单内。
3. **提示注入防护** — 在用户提供的文本到达语言模型接口前，对其中的对抗性子串进行词汇中和处理。
4. **子进程白名单** — 一种安全控制机制，仅允许执行 SHA-256 摘要与预审批目录匹配的二进制文件。
5. **精确集合成员** — 类别存在性检验：输入要么在允许集中，要么不在，没有概率性中间状态。
6. **词汇归一化** — 将符号输入规范化转换为离散语法形式，使对抗性模式在结构上失效。
7. **安全原语** — 构成纵深防御架构最底层构建块的原子性、不可分割的安全控制机制。
8. **白名单目录** — 在安全配置中明确枚举为文件系统操作许可目标的目录。
9. **密码学验证** — 确认二进制文件的 SHA-256 摘要与预审批条目匹配，保证供应链完整性。
10. **确定性内核** — 输出完全由离散输入决定、调用间无随机变化的子系统。

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
