<!--
VIGIA Academic Documentation
Module: adc5d097
Batch ID: vigia-doc-0103-adc5d097
Generated: 2026-05-20T14:56:47.866961+00:00
-->

The user wants academic technical documentation for a Python module in 4 languages (English, Spanish, Russian, Chinese). Key requirements:

1. Target audience: scientists/researchers who do NOT know Python.
2. Format: Markdown with 4 language sections.
3. Each section must include:
   - "What Is This Module?" (plain language explanation)
   - Key concepts with tables
   - A glossary of technical terms
   - A Scientific Note box explaining Peirce/Eco/Grice terminology is NOT mysticism — use sensor analogy.
4. Chinese translations must use specific terms:
   - 艾柯 (not Eco)
   - 格赖斯 (not Grice)
   - 取证工件 (not 制品)
   - 逻辑断裂 (not 裂缝)
5. 
6. Do NOT use floating-point math explanations — emphasize deterministic integer arithmetic where applicable (the module uses SHA256, not floating point, so emphasize deterministic hashing).

Module details:
- Path: vigia/inference/recommendation_engine_v3.1.py
- Docstring: recommendation_engine_v3.1.py, "Motor de recomendaciones forenses VIGÍA."
- Changes v3.1 vs v3.0:
  - B/2: Deterministic ID = SHA256(audit_id + '|' + policy_id + '|' + timestamp_utc). Resolves PRIMARY KEY collision when same event happens twice for same policy. Timestamp guarantees temporal uniqueness. Same evidence + policy + timestamp = same ID (reproducible, Daubert).
  - 3: Validation of podSelector before INSERT in recommendation_ledger. Empty podSelector {} isolates entire namespace — rejected before persisting payload.
  - Rule X: operator_hmac_signature = NULL until explicit human authorization.
- C2 note: This module does NOT have webhook handler nor _NoRedirect — finding applies to a version.
- Classes: RecommendationEngine (Forensic recommendation engine). Connects RiskBoundedDecisionLayer with recommendation_ledger. Every action requires... (sentence incomplete in prompt).
- Functions:
  - generate_recommendation(): Generates recommendation for a given verdict. ID calculated deterministically: SHA256(audit_id | policy_id ... (incomplete). Mention deterministic integer arithmetic via SHA256 (cryptographic hash over integer/byte inputs).
  - list_pending_recommendations(): Returns all recommendations pending human authorization.
  - authorize_and_execute(): Rule X: human authorization with HMAC signature. If hmac_key is None, uses env var VIGIA_HMAC_KEY. Returns Tr... (incomplete, likely True).
  - get_recommendation_spec(): Complete metadata of a recommendation to include in forensic bundle.
  - close(): (no description)
- Constants & Config: _SEPARATOR (likely the pipe '|' separator).

Structure:
The output should be a single Markdown document with 4 sections: ENGLISH, ESPAÑOL, РУССКИЙ, 中文. Each section has the required subsections.

Need to incorporate:
- Plain language for non-Python scientists.
- Key concepts tables.
- Glossary.
- Scientific Note about Peirce/Eco/Grice terminology not being mysticism, using sensor analogy. The prompt says "Peirce/Eco/Grice terminology is NOT mysticism — use the sensor analogy". This is a bit unusual for a forensic recommendation engine module, but the user explicitly requests it. I need to relate semiotics (Peirce, Eco, Grice) to forensic science via sensor analogy: just as a sensor transduces physical signals into data, forensic signs (indices, symbols) are transduced into evidence; the terminology describes deterministic inference chains, not mystical interpretation. In Chinese: 皮尔斯 (Peirce), 艾柯 (Eco), 格赖斯 (Grice).
- Chinese specific translations.
- License line in each section or at least once? The user says "License line: ...". Probably include in each section's footer or once at the end. I'll include in each section to be safe, or at the very end. Given "Each section must include", the license could be part of each section. But it's a single line. I'll place it at the bottom of each section or a global footer. Let's put it at the bottom of the document once, but since the prompt says "Each section must include..." for specific items, and the license line is a separate requirement, I'll add it at the end of each language section to be safe.
- No floating-point math. Emphasize deterministic integer arithmetic: SHA256 operates on discrete byte sequences; the hash output is an integer-like fixed-length digest; no rounding errors, fully reproducible.

Need to be thorough but concise.

Let's draft each section.

--- ENGLISH ---

Title: Technical Documentation — `vigia/inference/recommendation_engine_v3.1.py`

What Is This Module?
A forensic recommendation engine named VIGÍA. It acts as a deterministic bridge between a risk-assessment layer (RiskBoundedDecisionLayer) and a permanent forensic ledger (recommendation_ledger). Non-technical analogy: it is like a laboratory protocol robot that reads a test result (audit_id + policy_id), stamps it with an exact time, computes an irreproducible-but-deterministic fingerprint (SHA-256), and only appends the record to the lab notebook after checking that the safety cage (podSelector) is not left wide open. No human action is executed without explicit cryptographic approval (HMAC signature).

Key Concepts Table:
| Concept | Description | Scientific Relevance |
|---|---|---|
| Deterministic ID (v3.1 B/2) | SHA256(audit_id + '\|' + policy_id + '\|' + timestamp_utc) | Eliminates PRIMARY KEY collisions; guarantees that identical inputs always yield the identical identifier, satisfying Daubert reproducibility standards. |
| Separator (`_SEPARATOR`) | The pipe character `\|` used to delimit fields before hashing | Ensures unambiguous concatenation of discrete alphanumeric tokens into a single byte sequence. |
| podSelector Validation (v3.1-3) | Rejects empty `{}` selectors before database INSERT | Prevents accidental namespace-wide isolation; acts as a logical circuit breaker. |
| Rule X — HMAC Hold | `operator_hmac_signature` remains NULL until a human operator provides an HMAC signature | Enforces a two-person rule: algorithm proposes, human disposes. Cryptographic proof of authorization. |
| RiskBoundedDecisionLayer | Upstream risk-analysis component | Supplies the verdict that triggers recommendation generation. |
| recommendation_ledger | Immutable persistence layer | Stores finalized forensic recommendations for chain-of-custody. |

Glossary:
- **Audit ID**: A unique reference to a specific forensic event or evidence packet.
- **Policy ID**: The identifier of the governance rule that was triggered by the event.
- **Timestamp (UTC)**: Coordinated Universal Time stamp, ensuring global temporal uniqueness without timezone ambiguity.
- **SHA-256**: A cryptographic hash function producing a 256-bit digest from discrete input bytes; operates entirely on integer arithmetic over finite fields, with no floating-point approximations.
- **PRIMARY KEY**: A database constraint guaranteeing that each record is uniquely addressable.
- **podSelector**: A Kubernetes-style label filter defining which computational pods a policy targets.
- **HMAC (Hash-based Message Authentication Code)**: A deterministic signature computed from a secret key and a message, proving both data integrity and operator identity.
- **Daubert Standard**: A legal evidentiary criterion requiring that expert methodology be testable, reproducible, and subject to peer review.
- **Deterministic**: A process that, given the same initial conditions, always produces exactly the same result—essential for reproducible science.
- **Namespace Isolation**: A security boundary that segregates computational resources; an empty selector would inadvertently isolate an entire namespace.

Scientific Note:
> 【Scientific Note】
> Terms borrowed from semiotics—Charles Sanders Peirce (sign, index, symbol), Umberto Eco (code, overcoding), and H. P. Grice (implicature, cooperative principle)—are sometimes mistaken for metaphysical speculation. They are not. In this module, they function exactly like a sensor transduction model: Peirce’s “index” is the causal trace left on a sensor (the audit_id); Eco’s “code” is the calibration table that maps raw voltage to a physical unit (the policy_id); Grice’s “maxims” are the noise-filtering rules that discard empty podSelectors as violations of cooperative clarity. The inference chain is deterministic, measurable, and falsifiable—just like any other instrument reading.



--- ESPAÑOL ---

Title: Documentación Técnica — `vigia/inference/recommendation_engine_v3.1.py`

¿Qué es este módulo?
El motor de recomendaciones forenses VIGÍA. Funciona como un puente determinista entre una capa de evaluación de riesgos (RiskBoundedDecisionLayer) y un libro mayor forense permanente (recommendation_ledger). Análogo no técnico: es como un robot de protocolo de laboratorio que lee un resultado de prueba (audit_id + policy_id), lo estampa con una hora exacta, calcula una huella dactilar determinista (SHA-256) y solo añade el registro al cuaderno de laboratorio después de verificar que la jaula de seguridad (podSelector) no quedó completamente abierta. Ninguna acción humana se ejecuta sin aprobación criptográfica explícita (firma HMAC).

Tabla de Conceptos Clave:
| Concepto | Descripción | Relevancia Científica |
|---|---|---|
| ID determinista (v3.1 B/2) | SHA256(audit_id + '\|' + policy_id + '\|' + timestamp_utc) | Elimina colisiones de PRIMARY KEY; garantiza que entradas idénticas produzcan siempre el mismo identificador, cumpliendo el estándar de reproducibilidad Daubert. |
| Separador (`_SEPARATOR`) | Carácter de barra vertical `\|` para delimitar campos antes del hash | Asegura la concatenación inequívoca de tokens alfanuméricos discretos en una secuencia de bytes única. |
| Validación de podSelector (v3.1-3) | Rechaza selectores vacíos `{}` antes del INSERT en la base de datos | Previene el aislamiento accidental de todo un namespace; actúa como un disyuntor lógico. |
| Regla X — Retención HMAC | `operator_hmac_signature` permanece NULL hasta que un operador humano proporcione una firma HMAC | Refuerza la regla de las dos personas: el algoritmo propone, el humano dispone. Prueba criptográfica de autorización. |
| RiskBoundedDecisionLayer | Componente ascendente de análisis de riesgo | Suministra el veredicto que dispara la generación de la recomendación. |
| recommendation_ledger | Capa de persistencia inmutable | Almacena las recomendaciones forenses finalizadas para la cadena de custodia. |

Glosario:
- **Audit ID**: Referencia única a un evento forense específico o paquete de evidencia.
- **Policy ID**: Identificador de la regla de gobernanza activada por el evento.
- **Timestamp (UTC)**: Marca temporal en Tiempo Universal Coordinado, asegurando unicidad temporal global sin ambigüedad de zona horaria.
- **SHA-256**: Función hash criptográfica que produce un resumen de 256 bits a partir de bytes de entrada discretos; opera enteramente con aritmética entera sobre campos finitos, sin aproximaciones de punto flotante.
- **PRIMARY KEY**: Restricción de base de datos que garantiza que cada registro sea direccionable de forma única.
- **podSelector**: Filtro de etiquetas estilo Kubernetes que define qué pods computacionales apunta una política.
- **HMAC (Código de Autenticación de Mensajes basado en Hash)**: Firma determinista calculada a partir de una clave secreta y un mensaje, probando tanto la integridad de los datos como la identidad del operador.
- **Estándar Daubert**: Criterio legal de evidencia que exige que la metodología experta sea comprobable, reproducible y sujeta a revisión por pares.
- **Determinista**: Proceso que, dadas las mismas condiciones iniciales, siempre produce exactamente el mismo resultado—esencial para la ciencia reproducible.
- **Aislamiento de Namespace**: Frontera de seguridad que segrega recursos computacionales; un selector vacío aislaría inadvertidamente un namespace completo.

Nota Científica:
> 【Scientific Note】
> Los términos tomados de la semiótica—Charles Sanders Peirce (signo, índice, símbolo), Umberto Eco (código, sobrecodificación) y H. P. Grice (implicatura, principio cooperativo)—a veces se confunden con especulación metafísica. No lo son. En este módulo funcionan exactamente como un modelo de transducción de sensores: el “índice” de Peirce es la huella causal dejada en un sensor (el audit_id); el “código” de Eco es la tabla de calibración que mapea voltaje crudo a una unidad física (el policy_id); los “máximas” de Grice son las reglas de filtrado de ruido que descartan podSelectors vacíos como violaciones de claridad cooperativa. La cadena de inferencia es determinista, medible y falsable—exactamente como cualquier otra lectura instrumental.

License line.

--- РУССКИЙ ---

Title: Техническая документация — `vigia/inference/recommendation_engine_v3.1.py`

Что представляет собой этот модуль?
Судебно-экспертная рекомендательная система VIGÍA. Она выступает в роли детерминированного моста между уровнем оценки рисков (RiskBoundedDecisionLayer) и постоянным судебным реестром (recommendation_ledger). Нетехническая аналогия: это как лабораторный протокольный робот, который считывает результат теста (audit_id + policy_id), ставит на нём точную метку времени, вычисляет детерминированный «отпечаток» (SHA-256) и только после проверки, что защитная клетка (podSelector) не оставлена полностью открытой, вносит запись в лабораторный журнал. Никакие действия оператора не выполняются без явного криптографического одобрения (подписи HMAC).

Таблица ключевых понятий:
| Понятие | Описание | Научная значимость |
|---|---|---|
| Детерминированный ID (v3.1 B/2) | SHA256(audit_id + '\|' + policy_id + '\|' + timestamp_utc) | Устраняет коллизии PRIMARY KEY; гарантирует, что идентичные входные данные всегда дают один и тот же идентификатор, удовлетворяя стандартам воспроизводимости Daubert. |
| Разделитель (`_SEPARATOR`) | Символ вертикальной черты `\|` для разграничения полей перед хешированием | Обеспечивает однозначную конкатенацию дискретных буквенно-цифровых токенов в единую байтовую последовательность. |
| Валидация podSelector (v3.1-3) | Отклонение пустых `{}` селекторов перед INSERT в базу данных | Предотвращает случайную изоляцию всего пространства имён; действует как логический прерыватель цепи. |
| Правило X — блокировка HMAC | `operator_hmac_signature` остаётся NULL до тех пор, пока оператор не предоставит подпись HMAC | Усиливает правило двух лиц: алгоритм предлагает, человек распоряжается. Криптографическое доказательство авторизации. |
| RiskBoundedDecisionLayer | Восходящий компонент анализа рисков | Поставляет вердикт, инициирующий генерацию рекомендации. |
| recommendation_ledger | Неизменяемый уровень хранения | Сохраняет завершённые судебные рекомендации для обеспечения цепочки сохранности. |

Глоссарий:
- **Audit ID**: Уникальная ссылка на конкретное судебное событие или пакет доказательств.
- **Policy ID**: Идентификатор правила управления, активированного событием.
- **Timestamp (UTC)**: Метка времени по Всемирному координированному времени, обеспечивающая глобальную временную уникальность без неоднозначности часовых поясов.
- **SHA-256**: Криптографическая хеш-функция, вырабатывающая 256-битный дайджест из дискретных входных байтов; работает полностью на целочисленной арифметике над конечными полями без приближений с плавающей точкой.
- **PRIMARY KEY**: Ограничение базы данных, гарантирующее уникальную адресуемость каждой записи.
- **podSelector**: Фильтр меток в стиле Kubernetes, определяющий, какие вычислительные поды являются целью политики.
- **HMAC (код аутентификации сообщений на основе хеша)**: Детерминированная подпись, вычисляемая из секретного ключа и сообщения, подтверждающая как целостность данных, так и личность оператора.
- **Стандарт Daubert**: Правовой критерий допустимости, требующий, чтобы экспертная методология была проверяемой, воспроизводимой и подверженной рецензированию.
- **Детерминированный**: Процесс, который при одинаковых начальных условиях всегда даёт точно такой же результат — необходимое условие для воспроизводимой науки.
- **Изоляция пространства имён (namespace)**: Граница безопасности, разделяющая вычислительные ресурсы; пустой селектор непреднамеренно изолировал бы всё пространство имён.

Научное примечание:
> 【Scientific Note】
> Термины, заимствованные из семиотики,— Чарльз Сандерс Пирс (знак, индекс, символ), Умберто Эко (код, надкодирование) и Г. П. Грайс (импликатура, кооперативный принцип),— иногда ошибочно принимают за метафизическую спекуляцию. Это не так. В данном модуле они работают точно так же, как модель трансдукции датчика: «индекс» Пирса — это причинный след, оставленный на датчике (audit_id); «код» Эко — это таблица калибровки, отображающая сырые вольты в физическую единицу (policy_id); «максимы» Грайса — это правила фильтрации шума, отбрасывающие пустые podSelector’ы как нарушения кооперативной ясности. Цепочка вывода детерминирована, измерима и фальсифицируема — в точности как любое другое показание прибора.

License line.

--- 中文 ---

Title: 技术文档 — `vigia/inference/recommendation_engine_v3.1.py`

What Is This Module? (in Chinese, but the heading should be "这是什么模块？" maybe? The prompt says each section must include "What Is This Module?" but in Chinese context, I can translate the heading or keep it as requested. The prompt says: "What Is This Module?" (plain language explanation). So the heading can be translated. Let's use "这是什么模块？" or "模块概述". I'll use the translated heading but keep the spirit.

这是什么模块？
名为 VIGÍA 的取证推荐引擎。它在风险评估层（RiskBoundedDecisionLayer）与永久性取证台账（recommendation_ledger）之间充当确定性桥梁。非技术比喻：它如同一台实验室协议机器人，读取检测结果（audit_id + policy_id），加盖精确时间戳，计算一个确定性指纹（SHA-256），并在确认安全笼（podSelector）未被完全敞开之后，才将记录追加至实验笔记本。任何人工操作未经显式加密授权（HMAC 签名）均不会执行。

关键概念表：
| 概念 | 说明 | 科学意义 |
|---|---|---|
| 确定性 ID (v3.1 B/2) | SHA256(audit_id + '\|' + policy_id + '\|' + timestamp_utc) | 消除主键（PRIMARY KEY）冲突；保证相同输入始终产生相同标识符，满足 Daubert 可复现标准。 |
| 分隔符 (`_SEPARATOR`) | 竖线字符 `\|`，用于在哈希前界定字段 | 确保将离散字母数字令牌无歧义地串联为单一字节序列。 |
| podSelector 校验 (v3.1-3) | 在数据库 INSERT 前拒绝空 `{}` 选择器 | 防止意外隔离整个命名空间；充当逻辑断路器。 |
| 规则 X — HMAC 挂起 | `operator_hmac_signature` 在人工操作员提供 HMAC 签名前保持为 NULL | 强化双人规则：算法提议，人类裁决。授权的加密证明。 |
| RiskBoundedDecisionLayer | 上游风险分析组件 | 提供触发推荐生成的裁决。 |
| recommendation_ledger | 不可变持久层 | 存储最终取证推荐，以维护监管链。 |

术语表：
- **审计标识符 (audit_id)**：指向特定取证事件或证据包的唯一引用。
- **策略标识符 (policy_id)**：被事件触发的治理规则的标识符。
- **时间戳 (UTC)**：协调世界时标记，确保全球时间唯一性，无时区歧义。
- **SHA-256**：一种加密哈希函数，从离散输入字节生成 256 位摘要；完全基于有限域上的整数运算，无任何浮点近似。
- **主键 (PRIMARY KEY)**：数据库约束，保证每条记录可被唯一寻址。
- **podSelector**：类 Kubernetes 标签过滤器，定义策略所针对的计算 Pod。
- **HMAC（基于哈希的消息认证码）**：由密钥与消息计算得出的确定性签名，既证明数据完整性，也证明操作者身份。
- **Daubert 标准**：法律证据标准，要求专家方法可被检验、可复现并经受同行评审。
- **确定性**：给定相同初始条件，始终产生完全相同结果的过程——可复现科学的核心要求。
- **命名空间隔离**：划分计算资源的安全边界；空选择器将无意中隔离整个命名空间。

科学说明：
> 【科学说明】
> 从符号学借用的术语——查尔斯·桑德斯·皮尔斯（Charles Sanders Peirce，记号、指号、象征）、翁贝托·艾柯（Umberto Eco，符码、超编码）以及赫伯特·保罗·格赖斯（H. P. Grice，隐涵、合作原则）——有时被误认为形而上学思辨。事实并非如此。在本模块中，它们的功能与传感器换能模型完全类似：皮尔斯的“指号”是传感器上留下的因果痕迹（即 audit_id）；艾柯的“符码”是将原始电压映射为物理量单位的校准表（即 policy_id）；格赖斯的“准则”则是滤除空 podSelector 这类违反合作明晰性之噪声的滤波规则。推理链是确定性的、可测量的、可证伪的——与任何其他仪器读数别无二致。



--- Review constraints ---
- Must NOT use floating-point math explanations. I used "целочисленной арифметике над конечными полями", "integer arithmetic over finite fields", "整数运算", etc. Good.
- Chinese terms: 艾柯 (used), 格赖斯 (used), 取证工件 (not used, but module doesn't explicitly mention artifacts; however the prompt says "Chinese translations must use: 取证工件 (not 制品)". I should check if I need to incorporate 取证工件 somewhere. The module has "get_recommendation_spec(): Metadata completa de una recomendación para incluir en el bundle forense." Forensic bundle. Maybe in Chinese I can refer to the metadata spec as a 取证工件. Let me add it: in the glossary or key concepts, mention that the output of get_recommendation_spec() is a 取证工件. Or in the description. I'll add a row in the table or mention in glossary.
  - Add in glossary: **取证工件 (Forensic Artifact)**：由 get_recommendation_spec() 生成的完整元数据对象，用于纳入取证证据包。 This satisfies the requirement.
- 逻辑断裂 (not 裂缝): The module mentions "empty podSelector isolates namespace — rejected before persisting". This is a logical break/circuit breaker. In Chinese I should use 逻辑断裂. Let's add or modify: "充当逻辑断裂" instead of "逻辑断路器". Or in the glossary. The prompt says "逻辑断裂 (not 裂缝)". So I'll use 逻辑断裂 in the table: "防止意外隔离整个命名空间；充当逻辑断裂。"
- Peirce/Eco/Grice note must use sensor analogy. I used sensor transduction model. Good.
- License line included.
- Module path and docstring referenced.
- Classes and functions described in plain language integrated into the explanation and tables.
- C2 note included? The prompt mentions "C2 (Claude 2026-05-02): Este módulo NO tiene webhook handler ni _NoRedirect — el hallazgo aplica a una versión". I should mention this in the document as a version note. I'll add a "Version Note" or incorporate into the "What Is This Module?" or a separate note. Let's add a small note in each section: "Nota de versión (C2): Esta versión 3.1 no incluye manejador de webhook ni la clase _NoRedirect; dichos hallazgos corresponden a otra versión del sistema." And similarly in other languages.

Let's refine each section for thoroughness but conciseness.

Also, the function `close()` has no description. I'll mention it briefly as "releases resources" or similar.

In English, "deterministic integer arithmetic" should be emphasized for SHA-256. SHA-256 uses bitwise operations and modular addition on 32-bit integers. I can mention that explicitly.

Let's double-check Chinese specific terms:
- 艾柯: used.
- 格赖斯: used.
- 取证工件: will add.
- 逻辑断裂: will use.

Structure per language:
1. Heading (Language name)
2. ### What Is This Module? / ¿Qué es este módulo? / Что представляет собой этот модуль? / 这是什么模块？
3. ### Key Concepts / Conceptos Clave / Ключевые понятия / 关键概念
   - Table
4. ### Glossary / Glosario / Глоссарий / 术语表
5. ### Scientific Note / Nota Científica / Научное примечание / 【科学说明】
6. Version Note / Nota de Versión / Примечание к версии / 版本说明
7. License line.

Make sure the scientific note box starts with 【科学说明】 in Chinese and 【Scientific Note】 in others.

Let's write it out.

In the English Key Concepts table, I should mention `generate_recommendation`, `authorize_and_execute`, etc. But the prompt asks for "Key concepts with tables", not necessarily function signatures. The concepts already cover them. But maybe a table row for "Rule X" and "HMAC" is enough. I'll add a row for Forensic Bundle / Spec.

English Glossary: Add "Forensic Bundle" and "Recommendation Spec".

Let's ensure all functions are covered in plain language in the "What Is This Module?" text:
- generate_recommendation(): explained as computing deterministic ID.
- list_pending_recommendations(): explained as returning pending ones.
- authorize_and_execute(): explained as human auth with HMAC.
- get_recommendation_spec(): explained as metadata for bundle.
- close(): releasing resources.

In Chinese, for 取证工件:
| 取证工件规范 (get_recommendation_spec) | 为取证证据包生成的完整元数据结构 | 确保证据包内的监管链完整性。 |
Or in glossary: **取证工件**：由 get_recommendation_spec() 产出的结构化元数据对象，用于封装进取证证据包。

Let's also incorporate "逻辑断裂" for the empty podSelector rejection. In Chinese table: "防止意外隔离整个命名空间；形成一道逻辑断裂。"

Let's check Russian: "логический разрыв" or "логический прерыватель"? The user asked for Chinese specific term 逻辑断裂. In Russian I can use "логический разрыв" or "прерыватель цепи". Not mandated. I'll use "логический предохранитель" or "логический разрыв". I'll keep "логический прерыватель цепи" as it's more natural, but the prompt only mandates Chinese terms.

Now, let's draft carefully.

--- ENGLISH SECTION ---

# ENGLISH

## What Is This Module?

`recommendation_engine_v3.1.py` is the forensic recommendation engine **VIGÍA**. It serves as a deterministic conduit between an upstream risk-assessment layer (`RiskBoundedDecisionLayer`) and an immutable forensic ledger (`recommendation_ledger`). 

Think of it as a laboratory protocol automaton: it ingests a test result (`audit_id` paired with `policy_id`), appends a precise UTC timestamp, and computes a collision-free fingerprint using **SHA-256 over integer-delimited byte sequences**—never floating-point values. Before writing any record, it verifies that the safety gate (`podSelector`) is not accidentally set to “open all.” Finally, no action reaches the execution stage until a human operator supplies a cryptographic proof of consent via an **HMAC signature** (Rule X).

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
> - **Peirce’s index** is the causal trace left on a detector (the `audit_id`).  
> - **Eco’s code** is the calibration table that maps raw sensor voltage to a physical unit (the `policy_id`).  
> - **Grice’s maxims** are the noise-filtering rules that treat an empty `podSelector` as a violation of cooperative clarity and reject it.  
> 
> The resulting inference chain is deterministic, measurable, and falsifiable—no different from reading a thermometer or a mass spectrometer.



--- ESPAÑOL SECTION ---

# ESPAÑOL

## ¿Qué es este módulo?

`recommendation_engine_v3.1.py` es el **motor de recomendaciones forenses VIGÍA**. Actúa como un conducto determinista entre una capa superior de evaluación de riesgos (`RiskBoundedDecisionLayer`) y un libro mayor forense inmutable (`recommendation_ledger`).

Piénselo como un autómata de protocolo de laboratorio: ingiere un resultado de prueba (`audit_id` junto con `policy_id`), le anexa una marca temporal UTC exacta y calcula una huella digital libre de colisiones mediante **SHA-256 sobre secuencias de bytes delimitadas por enteros**—nunca valores de punto flotante. Antes de escribir registro alguno, verifica que la compuerta de seguridad (`podSelector`) no esté accidentalmente en modo “abrir todo”. Finalmente, ninguna acción alcanza la etapa de ejecución hasta que un operador humano aporte una prueba criptográfica de consentimiento mediante una **firma HMAC** (Regla X).

*Nota de versión (C2):* Esta versión 3.1 **no** contiene manejador de *webhook* ni la clase `_NoRedirect`; esos artefactos pertenecen a un linaje de versión distinto.

### Conceptos Clave

| Concepto | Descripción | Relevancia Científica |
|---|---|---|
| **ID determinista** (v3.1 B/2) | `SHA256(audit_id + '\|' + policy_id + '\|' + timestamp_utc)` | Elimina colisiones de `PRIMARY KEY`. La misma evidencia + política + tiempo siempre produce el mismo resumen de 256 bits, satisfaciendo
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
