<!--
VIGIA Academic Documentation
Module: adc5d097
Batch ID: vigia-doc-0103-adc5d097
Generated: 2026-05-20T14:56:47.866961+00:00
-->

# ENGLISH

## What Is This Module?

`recommendation_engine_v3.1.py` is the forensic recommendation engine **VIGÍA**. It serves as a deterministic conduit between an upstream risk-assessment layer (`RiskBoundedDecisionLayer`) and an immutable forensic ledger (`recommendation_ledger`). 

Think of it as a laboratory protocol automaton: it ingests a test result (`audit_id` paired with `policy_id`), appends a precise UTC timestamp, and computes a collision-free fingerprint using **SHA-256 over integer-delimited byte sequences**—never floating-point values. Before writing any record, it verifies that the safety gate (`podSelector`) is not accidentally set to "open all." Finally, no action reaches the execution stage until a human operator supplies a cryptographic proof of consent via an **HMAC signature** (Rule X).

*Version note (C2):* This v3.1 release does **not** contain a webhook handler or the `_NoRedirect` class; those artifacts belong to a different version lineage.

### Key Concepts

| Concept | Description | Scientific Relevance |
|---|---|---|
| **Deterministic ID** (v3.1 B/2) | `SHA256(audit_id + '\|' + policy_id + '\|' + timestamp_utc)` | Eliminates `PRIMARY KEY` collisions. Identical evidence + policy + time always yields the same 256-bit digest, satisfying the *Daubert* reproducibility standard. |
| **Field Separator** (`_SEPARATOR`) | The pipe symbol `\|` concatenating tokens before hashing | Guarantees unambiguous parsing of discrete alphanumeric strings into a single byte vector. |
| **podSelector Validation** (v3.1-3) | Empty `{}` selectors are rejected prior to `INSERT` | Prevents accidental namespace-wide isolation; acts as a **logical break** in the workflow. |
| **Rule X — HMAC Hold** | `operator_hmac_signature` remains `NULL` until a human operator signs | Enforces algorithmic-human dual control: software proposes, human disposes. |
| **Risk-Bounded Verdict** | Output from `RiskBoundedDecisionLayer` | The trigger event that causes the engine to instantiate a recommendation. |
| **Forensic Bundle Spec** | Output of `get_recommendation_spec()` | A structured **forensic artifact** containing complete metadata for chain-of-custody packaging. |
| **Resource Release** | `close()` method | Terminates connections and releases handles deterministically. |

### Glossary

- **Audit ID** — A unique pointer to a specific digital-evidence event.
- **Policy ID** — The governance rule identifier activated by the event.
- **Timestamp (UTC)** — A discrete temporal coordinate in Coordinated Universal Time, ensuring global uniqueness without timezone ambiguity.
- **SHA-256** — A cryptographic hash function operating entirely via deterministic integer arithmetic (bitwise logic and modular 32-bit addition over finite fields). It accepts discrete bytes and emits a fixed 256-bit integer digest; no floating-point approximations exist in its pipeline.
- **PRIMARY KEY** — A database integrity constraint ensuring every persisted record is uniquely addressable.
- **podSelector** — A label filter (Kubernetes-style) designating which computational pods a policy governs. An empty selector would match everything.
- **HMAC** — Hash-based Message Authentication Code. A deterministic signature proving both message integrity and operator identity.
- **Daubert Standard** — A legal benchmark requiring expert methods to be testable, reproducible, and peer-reviewable.
- **Logical Break** — A deliberate workflow interruption that stops propagation when pre-conditions violate safety boundaries.
- **Forensic Artifact** — Any structured data object (here, the recommendation specification) intended for inclusion in a forensic evidence bundle.

### 【Scientific Note】

> Terms drawn from semiotics—**Charles Sanders Peirce** (sign, index, symbol), **Umberto Eco** (code, overcoding), and **H. P. Grice** (implicature, cooperative maxims)—are occasionally dismissed as mysticism. They are not. Within this engine they behave exactly like a **sensor transduction model**:
> 
> - **Peirce's index** is the causal trace left on a detector (the `audit_id`).  
> - **Eco's code** is the calibration table that maps raw sensor voltage to a physical unit (the `policy_id`).  
> - **Grice's maxims** are the noise-filtering rules that treat an empty `podSelector` as a violation of cooperative clarity and reject it.  
> 
> The resulting inference chain is deterministic, measurable, and falsifiable—no different from reading a thermometer or a mass spectrometer.

--- ESPAÑOL SECTION ---

# ESPAÑOL

## ¿Qué es este módulo?

`recommendation_engine_v3.1.py` es el **motor de recomendaciones forenses VIGÍA**. Actúa como un conducto determinista entre una capa superior de evaluación de riesgos (`RiskBoundedDecisionLayer`) y un libro mayor forense inmutable (`recommendation_ledger`).

Piénselo como un autómata de protocolo de laboratorio: ingiere un resultado de prueba (`audit_id` junto con `policy_id`), le anexa una marca temporal UTC exacta y calcula una huella digital libre de colisiones mediante **SHA-256 sobre secuencias de bytes delimitadas por enteros**—nunca valores de punto flotante. Antes de escribir registro alguno, verifica que la compuerta de seguridad (`podSelector`) no esté accidentalmente en modo "abrir todo". Finalmente, ninguna acción alcanza la etapa de ejecución hasta que un operador humano aporte una prueba criptográfica de consentimiento mediante una **firma HMAC** (Regla X).

*Nota de versión (C2):* Esta versión 3.1 **no** contiene manejador de *webhook* ni la clase `_NoRedirect`; esos artefactos pertenecen a un linaje de versión distinto.

### Conceptos Clave

| Concepto | Descripción | Relevancia Científica |
|---|---|---|
| **ID determinista** (v3.1 B/2) | `SHA256(audit_id + '\|' + policy_id + '\|' + timestamp_utc)` | Elimina colisiones de `PRIMARY KEY`. La misma evidencia + política + tiempo siempre produce el mismo resumen de 256 bits, satisfaciendo
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## РУССКИЙ

### Что это за модуль?

`recommendation_engine_v3.1.py` — **форензический движок рекомендаций VIGÍA**. Он служит детерминированным каналом между вышестоящим слоем оценки рисков (`RiskBoundedDecisionLayer`) и неизменяемым форензическим реестром (`recommendation_ledger`).

Представьте его как автомат лабораторного протокола: он принимает результат проверки (`audit_id` в паре с `policy_id`), добавляет точную временну́ю метку UTC и вычисляет бесколлизионный отпечаток с помощью **SHA-256 над целочисленно-разделёнными байтовыми последовательностями** — никогда не с помощью значений с плавающей запятой. Перед записью любой записи он проверяет, что шлюз безопасности (`podSelector`) не установлен случайно в режим «открыть всё». Наконец, ни одно действие не достигает этапа выполнения, пока оператор-человек не предоставит криптографическое доказательство согласия через **подпись HMAC** (Правило X).

*Примечание версии (C2):* В выпуске v3.1 **отсутствует** обработчик webhook и класс `_NoRedirect`; эти артефакты относятся к другой версионной линии.

Ключевая гарантия детерминизма: одна и та же комбинация `audit_id + policy_id + timestamp_utc` всегда порождает один и тот же 256-битный дайджест, что соответствует требованию воспроизводимости стандарта Добера. Разделитель-пайп `_SEPARATOR` гарантирует однозначный разбор дискретных буквенно-цифровых строк в единый байтовый вектор перед хэшированием.

### Ключевые концепции
| Концепция | Описание | Научная значимость |
|---|---|---|
| Детерминированный ID (v3.1 B/2) | `SHA256(audit_id + '\|' + policy_id + '\|' + timestamp_utc)` | Устраняет коллизии PRIMARY KEY; удовлетворяет требованию воспроизводимости стандарта Добера |
| Разделитель полей (`_SEPARATOR`) | Символ пайпа, объединяющий токены перед хэшированием | Гарантирует однозначный разбор строк в единый байтовый вектор |
| Валидация podSelector (v3.1-3) | Пустые селекторы `{}` отклоняются до операции INSERT | Предотвращает случайную изоляцию всего пространства имён; действует как логический разрыв в рабочем процессе |
| Правило X — удержание HMAC | `operator_hmac_signature` остаётся NULL до подписи оператором | Обеспечивает двойной контроль алгоритм-человек: программа предлагает, человек решает |
| Ограниченный риском вердикт | Выход из `RiskBoundedDecisionLayer` | Триггерное событие, инициирующее создание рекомендации |
| Спецификация форензического пакета | Выход `get_recommendation_spec()` | Структурированный форензический артефакт с полными метаданными для упаковки цепочки хранения улик |
| Освобождение ресурсов | Метод `close()` | Детерминированное завершение соединений и освобождение дескрипторов |

> **【Научное примечание】**
> Терминология Пирса, Эко и Грайса — это не мистика, а формальная аналитическая механика. Как спектрометр преобразует фотонные взаимодействия в дискретные целочисленные отсчёты, этот модуль преобразует сигналы улик в детерминированные целочисленные оценки. Целочисленная арифметика гарантирует воспроизводимость в суде без округлений и аппроксимаций. Любое нарушение логики в цепочке артефактов фиксируется как целочисленный флаг, а не интуитивное суждение.

### Глоссарий
1. **Audit ID** — Уникальный указатель на конкретное событие цифровых улик.
2. **Policy ID** — Идентификатор правила управления, активированного событием.
3. **Временна́я метка (UTC)** — Дискретная временна́я координата в UTC, обеспечивающая глобальную уникальность без неоднозначности часовых поясов.
4. **SHA-256** — Криптографическая хэш-функция, работающая исключительно через детерминированную целочисленную арифметику.
5. **PRIMARY KEY** — Ограничение целостности базы данных, обеспечивающее уникальную адресуемость каждой записи.
6. **podSelector** — Фильтр меток, обозначающий, какими вычислительными подами управляет политика.
7. **HMAC** — Код аутентификации сообщений на основе хэша; детерминированная подпись.
8. **Стандарт Добера** — Правовой критерий, требующий проверяемости и воспроизводимости экспертных методов.
9. **Логический разрыв** — Намеренное прерывание рабочего процесса при нарушении предусловий безопасности.
10. **Форензический артефакт** — Любой структурированный объект данных, предназначенный для включения в форензический пакет улик.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## 中文

### 这是什么模块？

`recommendation_engine_v3.1.py`是VIGÍA**取证推荐引擎**。它作为上游风险评估层（`RiskBoundedDecisionLayer`）与不可变取证账本（`recommendation_ledger`）之间的确定性通道。

将其视为实验室协议自动机：它摄取测试结果（`audit_id`与`policy_id`配对），附加精确的UTC时间戳，并使用**SHA-256对整数分隔字节序列**计算无碰撞指纹——永不使用浮点值。在写入任何记录之前，它验证安全门（`podSelector`）未被意外设置为"全部开放"。最后，在人类操作员通过**HMAC签名**（规则X）提供密码学同意证明之前，任何操作都不会进入执行阶段。

*版本说明（C2）：* v3.1版本**不**包含webhook处理器或`_NoRedirect`类；这些取证工件属于不同的版本谱系。

关键确定性保证：相同的`audit_id + policy_id + timestamp_utc`组合始终产生相同的256位摘要，符合道伯特标准的可重现性要求。分隔符`_SEPARATOR`（管道符）保证在哈希之前将离散字母数字字符串明确解析为单一字节向量。

### 关键概念
| 概念 | 描述 | 科学相关性 |
|---|---|---|
| 确定性ID（v3.1 B/2） | `SHA256(audit_id + '\|' + policy_id + '\|' + timestamp_utc)` | 消除PRIMARY KEY碰撞；满足道伯特标准的可重现性要求 |
| 字段分隔符（`_SEPARATOR`） | 哈希前连接令牌的管道符 | 保证离散字母数字字符串到单一字节向量的明确解析 |
| podSelector验证（v3.1-3） | INSERT前拒绝空`{}`选择器 | 防止意外的命名空间范围隔离；作为工作流中的逻辑断裂 |
| 规则X——HMAC保持 | `operator_hmac_signature`保持NULL直到人工签名 | 强制算法-人工双重控制：软件提议，人工决定 |
| 风险限定裁决 | `RiskBoundedDecisionLayer`的输出 | 导致引擎实例化推荐的触发事件 |
| 取证包规范 | `get_recommendation_spec()`的输出 | 包含监管链打包完整元数据的结构化取证工件 |
| 资源释放 | `close()`方法 | 确定性终止连接并释放句柄 |

> **【科学说明】**
> 皮尔斯（Peirce）、艾柯（Eco）和格赖斯（Grice）的术语并非神秘主义，而是形式化的分析机制。如同光谱仪将光子相互作用转换为离散整数计数，本模块将证据信号转换为确定性整数分数。精确整数运算确保法庭可重现性。取证工件链的逻辑断裂以整数标志事件形式被检测。

### 词汇表
1. **Audit ID** — 指向特定数字证据事件的唯一指针。
2. **Policy ID** — 事件激活的治理规则标识符。
3. **时间戳（UTC）** — 协调世界时中的离散时间坐标，确保全球唯一性。
4. **SHA-256** — 完全通过确定性整数运算操作的密码学哈希函数，产生固定256位整数摘要。
5. **PRIMARY KEY** — 确保每条持久化记录唯一可寻址的数据库完整性约束。
6. **podSelector** — 标签过滤器，指定策略管辖哪些计算Pod；空选择器将匹配所有内容。
7. **HMAC** — 基于哈希的消息认证码；证明消息完整性和操作者身份的确定性签名。
8. **道伯特标准** — 要求专家方法可测试、可重现和可同行评审的法律基准。
9. **逻辑断裂** — 当前提条件违反安全边界时停止传播的刻意工作流中断。
10. **取证工件** — 任何旨在纳入取证证据包的结构化数据对象。

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
