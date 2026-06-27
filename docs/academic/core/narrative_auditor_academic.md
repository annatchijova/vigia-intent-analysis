<!--
VIGIA Academic Documentation
Module: 4d89a448
Batch ID: vigia-doc-0064-4d89a448
Generated: 2026-05-20T14:56:47.858273+00:00
-->

# Module Documentation: `vigia/core/narrative_auditor.py`

> **System Path:** `vigia/core/narrative_auditor.py`
> **Docstring Reference:** `vigia/security/narrative_auditor.py`
> **Title:** Narrative Injection Auditor — C3 Multi-Agent Validation

---

## ENGLISH

### What Is This Module?
This module serves as an **independent verification layer** within a multi-agent forensic pipeline. Its sole purpose is to inspect a machine-generated narrative—a sequential text stream produced by an AI agent—for evidence of tampering, content injection, or logical fracture before that narrative is permanently sealed as a forensic artifact.

The module does not generate, paraphrase, or modify content. It validates. It enforces the **C3 protocol**: one agent generates the narrative (Claude), a second agent audits it (the NarrativeAuditor), and a human operator serves as the final witness. By separating these processes, the system ensures that an attacker capable of compromising the narrative generator cannot simultaneously compromise the auditor.

All judgments inside the auditor rely on **deterministic integer arithmetic**: threat counts, severity tiers, and pass/fail thresholds are computed using exact whole-number operations, never floating-point approximations. This guarantees bit-identical results across every execution.

### Key Concepts

| Concept | Description | Scientific Role |
|---|---|---|
| **C3 Multi-Agent Validation** | A three-stage pipeline: Generator → Validator → Witness. | Eliminates single-point failure through strict process separation. |
| **Narrative Injection** | The unauthorized insertion of misleading, adversarial, or harmful content into an AI-generated text stream. | Threat vector detected via semantic and syntactic invariants. |
| **Deterministic Integer Arithmetic** | All scoring, tallying, and threshold evaluations use exact integer operations without rounding. | Ensures reproducible, bit-identical audit verdicts across runs. |
| **OWASP LLM 2025 Taxonomy** | A standardized catalog of vulnerabilities specific to large language models. | Reference pattern library for recognized attack signatures. |
| **Qwen P0 Invariants** | Deterministic protocol rules (from the Qwen P0 standard) that must remain unviolated during audit. | Fixed logical constraints enforced through integer-state checks. |
| **Separation of Processes** | The auditor executes in a logically isolated space from the generator. | Prevents a single attacker from controlling both roles at once. |
| **Logical Fracture** | A precise break in the chain of reasoning within the narrative. | Indicates potential manipulation or inconsistent argumentation. |

| Module Component | Plain-Language Function |
|---|---|
| **NarrativeAuditor** | The independent inspector that reads the narrative line-by-line and applies detection rules. |
| **ThreatDetected** | A structured record indicating which line carries a problem and its integer severity class. |
| **NarrativeAuditResult** | The final certificate stating whether the narrative is clean, contains warnings, or is contaminated. |
| **audit_narrative_before_seal()** | The procedural checkpoint invoked immediately before the narrative is finalized as evidence. |
| **audit()** | The core review operation that applies the pattern taxonomy to every line of text. |
| **to_dict()** | Converts the audit certificate into a standardized, archivable data record. |

### Glossary
- **C3 Protocol**: A tripartite validation architecture (Creator, Checker, Witness) used in high-assurance forensic systems.
- **Narrative**: In this context, a sequential list of text statements produced by an AI system during an investigation.
- **Sealing**: The irreversible act of finalizing a forensic artifact so it becomes court-admissible evidence.
- **Threat Pattern**: A recognizable signature of attack, defined by the OWASP LLM 2025 taxonomy, Gemini "Lethal" cases, or Carnegie patterns.
- **Deterministic Integer Arithmetic**: Mathematical operations using whole numbers only, ensuring every audit produces the exact same integer-based result given the same input.
- **Injection**: The unauthorized insertion of content into a data stream.
- **Forensic Artifact**: A digital object preserved with integrity guarantees for investigative or legal purposes.
- **Logical Fracture**: A deterministic rupture in the inferential structure of the narrative, flagged when integer-state checks reveal broken premises.

### 【Scientific Note】

> **Semiotics as Sensor Architecture**
>
> The terminology of Peirce, Eco, and Grice refers to formal semiotic frameworks—not mysticism. Charles Sanders Peirce's theory of signs, Umberto Eco's codes of interpretation, and H. Paul Grice's conversational maxims operate like optical sensors tuned to specific wavelengths: they are categorical detection filters. Just as a spectrometer identifies a chemical by its exact emission lines, these frameworks identify semantic anomalies by their exact logical signatures. When the auditor flags a "violation of the cooperative principle" or an "unintended interpretant," it is performing a deterministic, integer-based state classification—not invoking supernatural forces. The auditor is a semiotic sensor; the narrative is its specimen.

---

## ESPAÑOL

### ¿Qué es este módulo?
Este módulo funciona como una **capa de verificación independiente** dentro de una canalización forense multiagente. Su único propósito es inspeccionar una narrativa generada por máquina—un flujo secuencial de texto producido por un agente de IA—en busca de evidencia de alteración, inyección de contenido o **fractura lógica** antes de que dicha narrativa se selle permanentemente como artefacto forense.

El módulo no genera, parafrasea ni modifica contenido. Valida. Aplica el **protocolo C3**: un agente genera la narrativa (Claude), un segundo agente la audita (NarrativeAuditor) y un operador humano actúa como testigo final. Al separar estos procesos, el sistema asegura que un atacante capaz de comprometer el generador no pueda comprometer simultáneamente al auditor.

Todos los juicios internos del auditor se basan en **aritmética entera determinista**: los recuentos de amenazas, los niveles de severidad y los umbrales de aprobación/rechazo se computan con operaciones exactas de números enteros, nunca con aproximaciones de coma flotante. Esto garantiza resultados bit-a-bit idénticos en cada ejecución.

### Conceptos Clave

| Concepto | Descripción | Rol científico |
|---|---|---|
| **Validación multiagente C3** | Canalización de tres etapas: Generador → Validador → Testigo. | Elimina el fallo de punto único mediante separación estricta de procesos. |
| **Inyección narrativa** | Inserción no autorizada de contenido engañoso, adversarial o dañino en un flujo de texto generado por IA. | Vector de amenaza detectado por invariantes semánticas y sintácticas. |
| **Aritmética entera determinista** | Todas las puntuaciones, recuentos y umbrales usan operaciones exactas con números enteros, sin redondeo. | Garantiza resultados de auditoría reproducibles y bit-a-bit idénticos. |
| **Taxonomía OWASP LLM 2025** | Clasificación estandarizada de vulnerabilidades en modelos de lenguaje grandes. | Referencia de coincidencia de patrones para firmas de ataque conocidas. |
| **Invariantes Qwen P0** | Reglas de protocolo deterministas (estándar Qwen P0) que nunca deben violarse. | Restricciones lógicas fijas aplicadas mediante verificaciones de estado enteras. |
| **Separación de procesos** | El auditor se ejecuta en un espacio lógico aislado del generador. | Impide que un atacante comprometa ambos roles simultáneamente. |
| **Fractura Lógica** | Ruptura precisa en la cadena de razonamiento de la narrativa. | Indica posible manipulación o argumentación inconsistente. |

| Componente | Función en lenguaje sencillo |
|---|---|
| **NarrativeAuditor** | El inspector independiente que lee la narrativa línea por línea y aplica reglas de detección. |
| **ThreatDetected** | Un registro que indica qué línea contiene un problema y su nivel de severidad entero. |
| **NarrativeAuditResult** | El certificado final que indica si la narrativa está limpia, contiene advertencias o está contaminada. |
| **audit_narrative_before_seal()** | El punto de control procesal que se invoca justo antes de finalizar la evidencia. |
| **audit()** | La operación central de revisión que aplica patrones de detección al texto. |
| **to_dict()** | Convierte el certificado de auditoría en un registro de datos estandarizado para archivar. |

### Glosario
- **Protocolo C3**: Arquitectura de validación tripartita (Creador, Verificador, Testigo) usada en sistemas forenses de alta confianza.
- **Narrativa**: En este contexto, una lista secuencial de declaraciones de texto producidas por un sistema de IA durante una investigación.
- **Sellado**: El acto irreversible de finalizar un artefacto forense para que se convierta en evidencia admisible en tribunal.
- **Patrón de amenaza**: Una firma reconocible de ataque, definida por la taxonomía OWASP LLM 2025, los casos "Lethal" de Gemini o los patrones Carnegie.
- **Aritmética entera determinista**: Operaciones matemáticas usando solo números enteros, asegurando que cada auditoría produce exactamente el mismo resultado ante la misma entrada.
- **Inyección**: La inserción no autorizada de contenido en un flujo de datos.
- **Artefacto forense**: Objeto digital preservado con garantías de integridad para fines investigativos o legales.

### 【Nota Científica】
La terminología de Peirce, Eco y Grice se refiere a marcos semióticos formales, no a misticismo. La teoría de los signos de Charles Sanders Peirce, los códigos de interpretación de Umberto Eco y los máximas conversacionales de H. Paul Grice funcionan como sensores ópticos sintonizados a longitudes de onda específicas: son filtros de detección categóricos. Así como un espectrómetro identifica un químico por sus líneas de emisión exactas, estos marcos identifican anomalías semánticas por sus firmas lógicas exactas. Cuando el auditor señala una "violación del principio cooperativo" o un "interpretante no intencionado", está realizando una clasificación de estado determinista basada en enteros, no invocando fuerzas sobrenaturales. El auditor es un sensor semiótico; la narrativa es su espécimen.

---

## РУССКИЙ

### Что представляет собой этот модуль?
Этот модуль действует как независимая стадия верификации в многоагентной судебной конвейерной системе. Он проверяет сгенерированный нарратив (последовательный текстовый выход ИИ-генератора) на признаки манипуляции, инъекции или логической непротиворечивости до того, как нарратив будет окончательно запечатан в качестве судебного артефакта. Он не создаёт контент; он только инспектирует. Реализуется протокол C3: один агент генерирует (Claude), второй агент аудитирует (NarrativeAuditor), а человек выступает свидетелем. Такое разделение обязанностей гарантирует, что единая точка компрометации не сможет одновременно скомпрометировать и генерацию, и валидацию.

### Ключевые концепции

| Концепция | Описание | Научная роль |
|---|---|---|
| **Многоагентная валидация C3** | Трёхстадийный конвейер: Генератор → Валидатор → Свидетель. | Устранение единой точки отказа посредством разделения процессов. |
| **Нарративная инъекция** | Вредоносная вставка вводящего в заблуждение или опасного контента в поток текста, сгенерированного ИИ. | Вектор угрозы, обнаруживаемый семантическими и синтаксическими инвариантами. |
| **Детерминированная целочисленная арифметика** | Все оценки, пороги и классификации выполняются точными операциями с целыми числами без округления. | Гарантирует воспроизводимые, битово-идентичные результаты аудита при повторных запусках. |
| **Таксономия OWASP LLM 2025** | Стандартизированная классификация уязвимостей больших языковых моделей. | Эталон сопоставления с известными сигнатурами атак. |
| **Инварианты Qwen P0** | Детерминированные правила протокола (стандарт Qwen P0), которые никогда не должны нарушаться. | Фиксированные логические ограничения, применяемые через проверки целочисленных состояний. |
| **Разделение процессов** | Аудитор выполняется в изолированном логическом пространстве, отдельном от генератора. | Препятствует одновременному компрометированию обеих ролей злоумышленником. |

| Компонент | Функция на доступном языке |
|---|---|
| **NarrativeAuditor** | Независимый инспектор, читающий нарратив построчно. |
| **ThreatDetected** | Запись, указывающая, какая строка содержит проблему и какого рода. |
| **NarrativeAuditResult** | Итоговый сертификат, подтверждающий, что нарратив чист или скомпрометирован. |
| **audit_narrative_before_seal()** | Процедурная контрольная точка, вызываемая непосредственно перед финализацией доказательства. |
| **audit()** | Основная операция проверки, применяющая шаблоны обнаружения к тексту. |
| **to_dict()** | Преобразует аудиторский сертификат в стандартизированную запись данных для архивирования. |

### Глоссарий
- **Протокол C3**: Трёхчастная архитектура валидации (Создатель, Проверяющий, Свидетель), применяемая в высоконадёжных судебных системах.
- **Нарратив**: В данном контексте — последовательный список текстовых утверждений, произведённых ИИ-системой в ходе расследования.
- **Запечатывание**: Безвозвратное завершение формирования судебного артефакта для признания его допустимым доказательством в суде.
- **Шаблон угрозы**: Узнаваемая сигнатура атаки, определённая таксономией OWASP LLM 2025, кейсами Gemini «Lethal» или паттернами Carnegie.
- **Детерминированная целочисленная арифметика**: Математические операции исключительно с целыми числами, обеспечивающие получение абсолютно идентичного результата при каждом аудите при одном и том же входе.
- **Инъекция**: Несанкционированная вставка контента в поток данных.
- **Судебный артефакт**: Цифровой объект, сохранённый с гарантиями целостности для следственных или юридических целей.

### 【Научное примечание】
Терминология Пирса, Эко и Грайса отсылает к формальным семиотическим рамкам, а не к мистицизму. Теория знаков Чарльза Сандерса Пирса, коды интерпретации Умберто Эко и разговорные максимы Герберта Пола Грайса работают как оптические датчики, настроенные на определённые длины волн: это категориальные фильтры обнаружения. Подобно тому как спектрометр идентифицирует химическое вещество по его точным линиям излучения, эти рамки выявляют семантические аномалии по их точным логическим сигнатурам. Когда аудитор отмечает «нарушение кооперативного принципа» или «непреднамеренный интерпретант», он выполняет детерминированную классификацию состояния на основе целых чисел, а не вызывает сверхъестественные силы. Аудитор — это семиотический датчик; нарратив — его образец.

---

## 中文

### 本模块是什么？
本模块是多智能体取证流程中的独立验证环节。它对生成的叙事（由AI生成器产出的顺序文本流）进行检查，在将其永久封存为取证工件之前，发现操纵、注入或逻辑不一致的迹象。它不生成内容，只执行审查。它实现了C3协议：一个智能体生成（Claude），第二个智能体审计（NarrativeAuditor），人类作为见证人。这种职责分离确保单一受损点无法同时破坏生成与验证。

### 核心概念

| 概念 | 说明 | 科学作用 |
|---|---|---|
| **C3多智能体验证** | 三阶段流程：生成器 → 验证器 → 见证人。 | 通过流程隔离消除单点故障。 |
| **叙事注入** | 在AI生成的文本流中恶意插入误导性或有害内容。 | 通过语义与句法不变量检测的威胁向量。 |
| **确定性整数运算** | 所有评分、阈值判定与分类均使用精确的整数操作，无舍入或近似。 | 保证每次执行在相同输入下产生比特级一致的审计结果。 |
| **OWASP LLM 2025分类法** | 大语言模型漏洞的标准化分类体系。 | 针对已知攻击特征的模式匹配基准。 |
| **Qwen P0不变量** | 源自Qwen P0标准的确定性协议规则，审计中绝不可违背。 | 通过整数状态检查强制执行的固定逻辑约束。 |
| **流程隔离** | 审计器在独立于生成器的逻辑空间中运行。 | 阻止攻击者同时破坏两个角色。 |

| 组件 | 通俗功能说明 |
|---|---|
| **NarrativeAuditor** | 独立检查器，逐行审阅叙事内容。 |
| **ThreatDetected** | 记录指出哪一行存在问题及其类型。 |
| **NarrativeAuditResult** | 最终证书，声明叙事是洁净还是已被污染。 |
| **audit_narrative_before_seal()** | 在证据最终定稿之前立即调用的程序检查点。 |
| **audit()** | 核心审查操作，将检测模式应用于文本。 |
| **to_dict()** | 将审计证书转换为标准化的数据记录以归档。 |

### 术语表
- **C3协议**：高可信取证系统中使用的三方验证架构（创建者、检查者、见证人）。
- **叙事**：此处指调查过程中AI系统产生的一系列顺序文本陈述。
- **封存**：将取证工件最终定稿的不可逆行为，使其成为可在法庭采纳的证据。
- **威胁模式**：可识别的攻击特征，由OWASP LLM 2025分类法、Gemini"Lethal"案例或Carnegie模式定义。
- **确定性整数运算**：仅使用整数的数学运算，确保同一输入下每次审计产生完全相同的结果。
- **注入**：向数据流中未经授权插入内容。
- **取证工件**：以完整性保证保存的数字对象，用于调查或法律目的。
- **逻辑断裂**：叙事推理结构中的确定性断裂，当整数状态检查发现前提破损时触发标记。

### 【科学说明】
皮尔斯、艾柯与格赖斯的术语指向形式符号学框架，而非神秘主义。查尔斯·桑德斯·皮尔斯的符号学理论、翁贝托·艾柯的诠释代码以及赫伯特·保罗·格赖斯的会话准则，其运作方式类似于调谐至特定波长的光学传感器：它们是范畴化检测滤波器。正如光谱仪通过精确的发射谱线识别化学物质，这些框架通过精确的逻辑特征识别语义异常。当审计器标记"合作原则违例"或"非意图阐释项"时，它执行的是基于整数的确定性状态分类，而非召唤超自然力量。审计器是一枚符号学传感器；叙事即其待检样本。

---

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
