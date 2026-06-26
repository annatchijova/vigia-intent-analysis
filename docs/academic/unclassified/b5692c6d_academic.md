<!--
VIGIA Academic Documentation
Module: b5692c6d
Batch ID: vigia-doc-0107-b5692c6d
Generated: 2026-05-20T14:56:47.867815+00:00
-->

---

## ENGLISH

### What Is This Module?
This module implements an **Adversarial Silence Detector** for the VIGÍA forensic framework. In digital investigations, every user action—a *primary action*—normally leaves behind secondary traces such as log entries, temporary files, or metadata structures. When these expected traces are systematically missing, the absence is not merely "nothing"; it is a deliberate pattern of deletion. This detector registers claimed or inferred actions, tracks whether their expected secondary artifacts are present or confirmed absent, and computes forensic scores using **exact integer arithmetic** (exact rational numbers). The central insight is that an attacker who knows which artifacts are difficult to erase—for example, Windows Prefetch files or `$MFT` records—and selectively removes them reveals advanced knowledge of forensic methodologies. The detector captures this sophistication indicator by analyzing the pattern of silence.

### Key Concepts

| Concept | Description | Scientific Relevance |
|---|---|---|
| **Primary Action** | An event asserted or inferred to have occurred (e.g., program execution, file deletion). | The hypothesized cause in a causal chain. |
| **Secondary Artifact** (`ExpectedArtifact`) | A trace or file that should remain if the primary action occurred (e.g., a Prefetch file). | The expected effect; its absence contradicts the hypothesis. |
| **Adversarial Silence** | The systematic absence of expected secondary artifacts. | Indicates deliberate anti-forensic activity rather than natural data decay. |
| **Deterministic Scoring** (`Fraction`) | Exact rational numbers computed from integer numerators and denominators. | Eliminates rounding errors; guarantees reproducible results across all platforms. |
| **Frozen Record** (`frozen dataclass`) | An immutable, hashable record. | Ensures audit integrity: once recorded, evidence cannot be altered in memory. |
| **Audit Hash** | A deterministic fingerprint of the analysis state. | Verifies that the investigative process itself has not been tampered with. |

| Operation | Plain-Language Description |
|---|---|
| **Register Primary Action** | Log a hypothesized main event into the detector. |
| **Register Present Artifact** | Confirm that a predicted secondary trace was found on the system. |
| **Register Confirmed Absent** | Record that a predicted trace is definitively missing. |
| **Analyze** | Compute exact forensic scores and detect patterns of adversarial silence. |

### Glossary

1. **Adversarial Silence** — A forensic pattern in which an attacker selectively removes traces to thwart investigation.
2. **Artifact (Forensic)** — Any digital object—file, log, metadata entry—that serves as evidence of an action.
3. **Deterministic Integer Arithmetic** — Calculations performed with exact fractions (ratios of integers), avoiding all approximations.
4. **Frozen Record** — An immutable data structure that cannot be modified after creation, preserving chain-of-custody in software.
5. **Primary Action** — The main event under investigation from which secondary effects are predicted.
6. **Secondary Artifact** — A byproduct trace expected to exist given a specific primary action.
7. **Sensor Analogy** — The conceptual model treating expected artifacts as sensors; a missing signal is a null measurement, not an absence of data.
8. **Anti-forensic Activity** — Deliberate steps taken by an attacker to erase or obscure digital evidence.
9. **Prefetch File** — A Windows artifact recording program execution; difficult to erase without specialized knowledge.
10. **Sophistication Indicator** — A metric measuring the attacker's knowledge of forensic methodologies, derived from the pattern of selective erasure.

### 【Scientific Note】
This module employs concepts from semiotics (C. S. Peirce, Umberto Eco) and linguistic pragmatics (H. P. Grice). In semiotics, a sign need not be a visible object; the *absence* of an expected index is itself a sign. In pragmatics, Grice's cooperative maxims assume truthful and informative communication—systematic violation implies deliberate intent. None of this is mysticism. Think of the detector as a sensor array: each expected artifact is a sensor channel. A missing sensor reading is not noise; it is data.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## ESPAÑOL

### ¿Qué es este módulo?
Este módulo implementa un **Detector de Silencio Adversarial** para el marco forense VIGÍA. En las investigaciones digitales, toda acción de usuario—una *acción primaria*—normalmente deja rastros secundarios tales como entradas de registro, archivos temporales o estructuras de metadatos. Cuando estos rastros esperados faltan sistemáticamente, la ausencia no es simplemente "nada"; es un patrón deliberado de eliminación. Este detector registra acciones reclamadas o inferidas, rastrea si sus artefactos secundarios esperados están presentes o confirmados como ausentes, y calcula puntuaciones forenses usando **aritmética entera exacta** (números racionales exactos). La percepción central es que un atacante que sabe qué artefactos son difíciles de borrar—como los archivos Prefetch de Windows o los registros `$MFT`—y los elimina selectivamente, revela conocimiento avanzado de metodologías forenses. El detector captura este indicador de sofisticación analizando el patrón del silencio.

### Conceptos clave

| Concepto | Descripción | Relevancia Científica |
|---|---|---|
| **Acción Primaria** | Evento asertado o inferido como ocurrido (p. ej., ejecución de programa, eliminación de archivo). | La causa hipotética en una cadena causal. |
| **Artefacto Secundario** (`ExpectedArtifact`) | Rastro o archivo que debería permanecer si ocurrió la acción primaria (p. ej., un archivo Prefetch). | El efecto esperado; su ausencia contradice la hipótesis. |
| **Silencio Adversarial** | La ausencia sistemática de artefactos secundarios esperados. | Indica actividad antiforense deliberada en lugar de decaimiento natural de datos. |
| **Puntuación Determinista** (`Fraction`) | Números racionales exactos calculados a partir de numeradores y denominadores enteros. | Elimina errores de redondeo; garantiza resultados reproducibles en todas las plataformas. |
| **Registro Congelado** (`frozen dataclass`) | Registro inmutable y hashable. | Garantiza la integridad de auditoría: una vez registrada, la evidencia no puede alterarse en memoria. |
| **Hash de Auditoría** | Huella digital determinista del estado del análisis. | Verifica que el propio proceso investigativo no haya sido manipulado. |

### Glosario
1. **Silencio Adversarial** — Patrón forense en el que un atacante elimina selectivamente rastros para obstaculizar la investigación.
2. **Artefacto Forense** — Cualquier objeto digital—archivo, registro, entrada de metadatos—que sirve como evidencia de una acción.
3. **Aritmética Entera Determinista** — Cálculos realizados con fracciones exactas (cocientes de enteros), evitando todas las aproximaciones.
4. **Registro Congelado** — Estructura de datos inmutable que no puede modificarse tras su creación, preservando la cadena de custodia en el software.
5. **Acción Primaria** — El evento principal bajo investigación del que se predicen los efectos secundarios.
6. **Artefacto Secundario** — Rastro subproducto que se espera exista dado una acción primaria específica.
7. **Analogía de Sensor** — Modelo conceptual que trata los artefactos esperados como sensores; una señal faltante es una medición nula, no una ausencia de datos.
8. **Actividad Antiforense** — Pasos deliberados tomados por un atacante para borrar u obscurecer evidencia digital.
9. **Archivo Prefetch** — Artefacto de Windows que registra la ejecución de programas; difícil de borrar sin conocimiento especializado.
10. **Indicador de Sofisticación** — Métrica que mide el conocimiento del atacante sobre metodologías forenses, derivada del patrón de borrado selectivo.

### 【Nota Científica】
Este módulo emplea conceptos de la semiótica (C. S. Peirce, Umberto Eco) y la pragmática lingüística (H. P. Grice). En semiótica, un signo no necesita ser un objeto visible; la *ausencia* de un índice esperado es en sí misma un signo. En pragmática, las máximas cooperativas de Grice asumen comunicación veraz e informativa—la violación sistemática implica intención deliberada. Nada de esto es misticismo. Piense en el detector como una red de sensores: cada artefacto esperado es un canal de sensor. Una lectura de sensor faltante no es ruido; es un dato.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## РУССКИЙ

### Что это за модуль?
Данный модуль реализует **Детектор состязательного молчания** для криминалистической платформы VIGÍA. В цифровых расследованиях каждое действие пользователя — *первичное действие* — обычно оставляет вторичные следы: записи журнала, временные файлы или структуры метаданных. Когда эти ожидаемые следы систематически отсутствуют, отсутствие — не просто «ничто»; это намеренная схема удаления. Данный детектор регистрирует заявленные или выведенные действия, отслеживает, присутствуют ли ожидаемые вторичные артефакты или их отсутствие подтверждено, и вычисляет криминалистические оценки с использованием **точной целочисленной арифметики** (точных рациональных чисел). Ключевой вывод: злоумышленник, знающий, какие артефакты трудно стереть — например, файлы Windows Prefetch или записи `$MFT` — и избирательно удаляющий их, раскрывает передовые знания криминалистических методологий.

### Ключевые концепции

| Концепция | Описание | Научная значимость |
|---|---|---|
| **Первичное действие** | Событие, заявленное или выведенное как произошедшее (напр., выполнение программы, удаление файла). | Предполагаемая причина в причинно-следственной цепи. |
| **Вторичный артефакт** (`ExpectedArtifact`) | След или файл, который должен остаться если первичное действие произошло (напр., файл Prefetch). | Ожидаемый эффект; его отсутствие противоречит гипотезе. |
| **Состязательное молчание** | Систематическое отсутствие ожидаемых вторичных артефактов. | Указывает на намеренную антикриминалистическую деятельность, а не на естественный распад данных. |
| **Детерминированная оценка** (`Fraction`) | Точные рациональные числа, вычисленные из целочисленных числителей и знаменателей. | Исключает ошибки округления; гарантирует воспроизводимые результаты на всех платформах. |
| **Замороженная запись** (`frozen dataclass`) | Неизменяемая, хешируемая запись. | Обеспечивает целостность аудита: однажды записанные доказательства не могут быть изменены в памяти. |
| **Хеш аудита** | Детерминированный отпечаток состояния анализа. | Подтверждает, что сам следственный процесс не был подделан. |

### Глоссарий
1. **Состязательное молчание** — Криминалистический паттерн, при котором злоумышленник избирательно удаляет следы для срыва расследования.
2. **Криминалистический артефакт** — Любой цифровой объект — файл, журнал, запись метаданных — служащий доказательством действия.
3. **Детерминированная целочисленная арифметика** — Вычисления с точными дробями (отношениями целых чисел), исключающие все приближения.
4. **Замороженная запись** — Неизменяемая структура данных, которая не может быть изменена после создания, сохраняя цепочку хранения в программном обеспечении.
5. **Первичное действие** — Основное расследуемое событие, из которого предсказываются вторичные эффекты.
6. **Вторичный артефакт** — Побочный след, ожидаемый при конкретном первичном действии.
7. **Аналогия датчика** — Концептуальная модель, рассматривающая ожидаемые артефакты как датчики; отсутствующий сигнал — нулевое измерение, а не отсутствие данных.
8. **Антикриминалистическая деятельность** — Намеренные шаги злоумышленника по удалению или сокрытию цифровых доказательств.
9. **Файл Prefetch** — Артефакт Windows, фиксирующий выполнение программ; трудно стереть без специальных знаний.
10. **Индикатор изощрённости** — Метрика знания злоумышленника о криминалистических методологиях, выводимая из паттерна избирательного стирания.

### 【Научное примечание】
Данный модуль использует концепции семиотики (Ч. С. Пирс, Умберто Эко) и лингвистической прагматики (Г. П. Грайс). В семиотике знак не обязан быть видимым объектом; *отсутствие* ожидаемого индекса само по себе является знаком. В прагматике кооперативные максимы Грайса предполагают правдивое и информативное общение — систематическое нарушение подразумевает намеренный умысел. Ничего мистического здесь нет. Представьте детектор как массив датчиков: каждый ожидаемый артефакт — это канал датчика. Отсутствующее показание датчика — не шум; это данные.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## 中文

### 这是什么模块？
本模块为 VIGÍA 取证框架实现了一个**对抗性沉默检测器**。在数字调查中，每个用户行为——*主要行为*——通常会留下日志条目、临时文件或元数据结构等次要痕迹。当这些预期痕迹系统性地缺失时，这种缺失不仅仅是"什么都没有"；它是一种蓄意删除的模式。该检测器记录声称或推断发生的行为，追踪其预期次要取证工件是否存在或被确认缺失，并使用**精确整数运算**（精确有理数）计算取证评分。核心洞察是：一个知道哪些工件难以擦除——例如 Windows Prefetch 文件或 `$MFT` 记录——并选择性删除它们的攻击者，揭示了对取证方法论的高级知识。检测器通过分析沉默模式来捕获这一复杂程度指标。

### 关键概念

| 概念 | 描述 | 科学相关性 |
|---|---|---|
| **主要行为** | 被断言或推断为发生的事件（如程序执行、文件删除）。 | 因果链中的假设原因。 |
| **次要取证工件**（`ExpectedArtifact`） | 若主要行为发生则应存在的痕迹或文件（如 Prefetch 文件）。 | 预期效果；其缺失与假说相矛盾。 |
| **对抗性沉默** | 预期次要取证工件的系统性缺失。 | 表明是蓄意的反取证活动，而非自然数据衰减。 |
| **确定性评分**（`Fraction`） | 由整数分子和分母计算的精确有理数。 | 消除舍入误差；保证所有平台上的可复现结果。 |
| **冻结记录**（`frozen dataclass`） | 不可变的、可哈希的记录。 | 确保审计完整性：一旦记录，证据在内存中无法更改。 |
| **审计哈希** | 分析状态的确定性指纹。 | 验证调查过程本身未被篡改。 |

### 词汇表
1. **对抗性沉默** — 攻击者选择性删除痕迹以阻挠调查的取证模式。
2. **取证工件** — 作为行为证据的任何数字对象——文件、日志、元数据条目。
3. **精确整数运算** — 使用精确分数（整数比值）进行计算，避免所有近似。
4. **冻结记录** — 创建后无法修改的不可变数据结构，在软件中保护监管链。
5. **主要行为** — 调查中的主要事件，从中预测次要效果。
6. **次要取证工件** — 给定特定主要行为后预期存在的副产品痕迹。
7. **传感器类比** — 将预期取证工件视为传感器的概念模型；缺失信号是零测量，而非数据缺失。
8. **反取证活动** — 攻击者为擦除或模糊数字证据采取的蓄意步骤。
9. **Prefetch 文件** — 记录程序执行的 Windows 工件；没有专业知识难以擦除。
10. **复杂程度指标** — 从选择性擦除模式得出的衡量攻击者对取证方法论了解程度的指标。

### 【科学说明】
本模块采用符号学（查尔斯·桑德斯·皮尔斯、翁贝托·艾柯）和语言语用学（H·P·格赖斯）的概念。在符号学中，符号不必是可见对象；预期索引的*缺失*本身就是一个符号。在语用学中，格赖斯的合作准则假设真实且信息丰富的交流——系统性违反暗示蓄意意图。这一切都不是神秘主义。将检测器视为传感器阵列：每个预期取证工件都是一个传感器通道。缺失的传感器读数不是噪声；它是数据。

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
