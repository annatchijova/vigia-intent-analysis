<!--
VIGIA Academic Documentation
Module: 7b5f476a
Batch ID: vigia-doc-0034-7b5f476a
Generated: 2026-05-20T14:56:47.851872+00:00
-->

---

## ENGLISH

### What Is This Module?
The **Collapse Decision Layer (CDL)**, version 2 aggressive, is the terminal quality-control gate in the VIGÍA digital-forensics pipeline. Its sole purpose is to prevent composite evidence from being accepted when the underlying data sources have lost **sensor independence**—the guarantee that each source observes an event through an isolated channel. If two or more forensic artifacts share a hidden dependency (for example, one log file was generated from another), they can no longer corroborate each other. The CDL detects this condition and returns an **INCONCLUSIVE** verdict. The entire logic runs on **deterministic integer arithmetic**: every state, every comparison, and every decision uses exact whole-number flags, eliminating rounding errors and ensuring bit-level reproducibility across laboratories.

### Key Concepts

| Component | Plain-Language Description | Scientific Role |
|---|---|---|
| **CollapseVerdict** | The final classification label assigned to an evidence set: COHERENT, FRAGMENTED, or INCONCLUSIVE. | Communicates the structural integrity status of the composite evidence. |
| **Sensor Independence** | The guarantee that each evidence source observed the target event through an isolated, unshared channel. | Prevents circular corroboration, where two artifacts are actually one source masquerading as two. |
| **Dependency Graph** | A directed graph encoding known causal relationships between evidence sources. | Used to detect hidden shared origins that would invalidate cross-source confirmation. |
| **Collapse Threshold** | An integer count of the minimum number of independent sources required for a COHERENT verdict. | Enforces the evidential floor below which no verdict can be issued. |
| **Aggressive Mode (v2)** | A stricter detection setting that flags partial dependencies in addition to total ones. | Reduces false COHERENT verdicts by widening the collapse detection criteria. |
| **Deterministic Integer Arithmetic** | All threshold comparisons and state transitions use exact integer values. | Guarantees identical decisions across platforms and runs. |

### Core Operations

| Operation | Purpose |
|---|---|
| `evaluate()` | Accepts a set of evidence signals and their dependency metadata, then applies collapse detection logic to return a `CollapseVerdict`. |
| `check_independence()` | Inspects the dependency graph to determine whether the provided sources are genuinely independent. |
| `apply_aggressive_mode()` | Extends the collapse check to cover partial structural overlaps in addition to full shared origins. |

### Glossary
1. **Coherent Verdict** — A conclusion that the composite evidence is structurally sound and cross-corroborating.
2. **Collapse** — The condition in which evidence sources share a hidden dependency, invalidating their mutual corroboration.
3. **Dependency Graph** — A mathematical structure encoding causal relationships between evidence sources.
4. **Deterministic Integer Arithmetic** — Computation using only exact integer comparisons and counts; no approximations.
5. **Fragmented Verdict** — A conclusion that evidence sources are structurally inconsistent, suggesting partial manipulation.
6. **INCONCLUSIVE** — The CDL verdict issued when sensor independence cannot be established.
7. **Sensor Independence** — The property ensuring each evidence source operated through a distinct, unshared observation channel.
8. **Collapse Threshold** — The minimum integer count of genuinely independent sources required for a positive verdict.
9. **Aggressive Mode** — Detection configuration that flags partial as well as total dependencies.
10. **Cross-Corroboration** — The forensic principle that independent sources confirming the same event strengthen the conclusion.

> **【Scientific Note】**
> Peirce/Eco/Grice terminology is NOT mysticism. In VIGÍA, sensor independence is a Peircean requirement: two *indices* can only constitute independent evidence if they result from causally unrelated observation channels. Eco's interpretive principle warns against reading two signs as independent when they share a common code. Grice's maxim of quantity is violated when an analyst presents two derived sources as if they were two primary sources.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## ESPAÑOL

### ¿Qué es este módulo?
La **Capa de Decisión de Colapso (CDL)**, versión 2 agresiva, es la puerta de control de calidad terminal en la cadena de procesamiento forense digital de VIGÍA. Su único propósito es impedir que se acepte evidencia compuesta cuando las fuentes de datos subyacentes han perdido la **independencia de sensor**—la garantía de que cada fuente observa un evento a través de un canal aislado. Si dos o más artefactos forenses comparten una dependencia oculta (por ejemplo, un archivo de registro fue generado a partir de otro), ya no pueden corroborarse mutuamente. La CDL detecta esta condición y devuelve un veredicto **INCONCLUSO**. Toda la lógica funciona con **aritmética entera determinista**: cada estado, cada comparación y cada decisión utiliza indicadores de números enteros exactos.

### Conceptos clave

| Componente | Descripción | Rol científico |
|---|---|---|
| **CollapseVerdict** | Etiqueta de clasificación final asignada a un conjunto de evidencia: COHERENTE, FRAGMENTADA o INCONCLUSA. | Comunica el estado de integridad estructural de la evidencia compuesta. |
| **Independencia de Sensor** | Garantía de que cada fuente de evidencia observó el evento objetivo a través de un canal aislado e independiente. | Previene la corroboración circular, donde dos artefactos son en realidad una sola fuente. |
| **Grafo de Dependencias** | Grafo dirigido que codifica las relaciones causales conocidas entre fuentes de evidencia. | Detecta orígenes compartidos ocultos que invalidarían la confirmación entre fuentes. |
| **Umbral de Colapso** | Recuento entero del número mínimo de fuentes independientes requeridas para un veredicto COHERENTE. | Impone el suelo probatorio por debajo del cual no puede emitirse ningún veredicto. |
| **Modo Agresivo (v2)** | Configuración de detección más estricta que marca dependencias parciales además de totales. | Reduce los falsos veredictos COHERENTES ampliando los criterios de detección de colapso. |

### Glosario
1. **Veredicto Coherente** — Conclusión de que la evidencia compuesta es estructuralmente sólida y se corrobora mutuamente.
2. **Colapso** — Condición en que las fuentes de evidencia comparten una dependencia oculta, invalidando su corroboración mutua.
3. **Grafo de Dependencias** — Estructura matemática que codifica relaciones causales entre fuentes de evidencia.
4. **Aritmética Entera Determinista** — Cómputo usando solo comparaciones y recuentos enteros exactos; sin aproximaciones.
5. **Veredicto Fragmentado** — Conclusión de que las fuentes de evidencia son estructuralmente inconsistentes, sugiriendo manipulación parcial.
6. **INCONCLUSO** — Veredicto CDL emitido cuando no puede establecerse la independencia de sensor.
7. **Independencia de Sensor** — Propiedad que garantiza que cada fuente de evidencia operó a través de un canal de observación distinto e independiente.
8. **Umbral de Colapso** — Recuento entero mínimo de fuentes genuinamente independientes requeridas para un veredicto positivo.
9. **Modo Agresivo** — Configuración de detección que marca dependencias parciales y totales.
10. **Corroboración Cruzada** — Principio forense de que fuentes independientes que confirman el mismo evento fortalecen la conclusión.

> **【Nota Científica】**
> La terminología de Peirce/Eco/Grice no es misticismo. En VIGÍA, la independencia de sensor es un requisito peirceano: dos *índices* solo pueden constituir evidencia independiente si resultan de canales de observación causalmente no relacionados. El principio interpretativo de Eco advierte contra leer dos signos como independientes cuando comparten un código común. La máxima de cantidad de Grice se viola cuando un analista presenta dos fuentes derivadas como si fueran dos fuentes primarias.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## РУССКИЙ

### Что это за модуль?
**Слой решения о коллапсе (CDL)**, версия 2 aggressive — конечный контрольный шлюз в конвейере цифровой криминалистики VIGÍA. Его единственная задача — не допустить принятия составных доказательств, когда источники данных утратили **независимость датчиков**: гарантию того, что каждый источник наблюдал событие через изолированный канал. Если два или более криминалистических артефакта разделяют скрытую зависимость (например, один журнальный файл был сгенерирован из другого), они больше не могут подтверждать друг друга. CDL обнаруживает это условие и возвращает вердикт **INCONCLUSIVE**. Вся логика работает на **детерминированной целочисленной арифметике**: каждое состояние, каждое сравнение и каждое решение использует точные целочисленные флаги.

### Ключевые концепции

| Компонент | Описание | Научная роль |
|---|---|---|
| **CollapseVerdict** | Итоговая классификационная метка, присваиваемая набору доказательств: COHERENT, FRAGMENTED или INCONCLUSIVE. | Сообщает о структурной целостности составных доказательств. |
| **Независимость датчиков** | Гарантия того, что каждый источник доказательств наблюдал целевое событие через изолированный, несовместимый канал. | Предотвращает круговую корроборацию, когда два артефакта фактически являются одним источником. |
| **Граф зависимостей** | Направленный граф, кодирующий известные причинно-следственные связи между источниками доказательств. | Используется для обнаружения скрытых общих истоков, которые аннулировали бы межисточниковое подтверждение. |
| **Порог коллапса** | Целочисленное количество минимально необходимых независимых источников для вердикта COHERENT. | Устанавливает доказательный минимум, ниже которого не может быть вынесен вердикт. |
| **Агрессивный режим (v2)** | Более строгая настройка обнаружения, маркирующая частичные зависимости наряду с полными. | Снижает количество ложных вердиктов COHERENT. |

### Глоссарий
1. **Вердикт COHERENT** — Заключение о структурной состоятельности составных доказательств и их взаимной корроборации.
2. **Коллапс** — Состояние, при котором источники доказательств разделяют скрытую зависимость, аннулируя взаимную корроборацию.
3. **Граф зависимостей** — Математическая структура, кодирующая причинно-следственные связи между источниками доказательств.
4. **Детерминированная целочисленная арифметика** — Вычисления с использованием только точных целочисленных сравнений и подсчётов.
5. **Вердикт FRAGMENTED** — Заключение о структурной несогласованности источников доказательств, указывающее на частичную манипуляцию.
6. **INCONCLUSIVE** — Вердикт CDL, выносимый когда независимость датчиков не может быть установлена.
7. **Независимость датчиков** — Свойство, обеспечивающее работу каждого источника доказательств через отдельный, несовместимый канал наблюдения.
8. **Порог коллапса** — Минимальное целочисленное количество по-настоящему независимых источников для положительного вердикта.
9. **Агрессивный режим** — Конфигурация обнаружения, маркирующая как частичные, так и полные зависимости.
10. **Перекрёстная корроборация** — Криминалистический принцип, по которому независимые источники, подтверждающие одно и то же событие, укрепляют вывод.

> **【Научное примечание】**
> Терминология Пирса, Эко и Грайса — не мистика. В VIGÍA независимость датчиков является пирсовским требованием: два *индекса* могут составлять независимые доказательства только если они возникли из причинно несвязанных каналов наблюдения. Интерпретационный принцип Эко предостерегает от прочтения двух знаков как независимых при наличии общего кода. Максима количества Грайса нарушается, когда аналитик представляет два производных источника как два первичных.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## 中文

### 这是什么模块？
**折叠决策层（CDL）**第 2 版（激进模式）是 VIGÍA 数字取证流水线中的终端质量控制门。其唯一目的是在底层数据源失去**传感器独立性**——每个源通过隔离通道观测事件的保证——时，阻止接受复合证据。若两个或多个取证工件共享隐藏依赖关系（例如，一个日志文件从另一个生成），它们便无法相互印证。CDL 检测此条件并返回 **INCONCLUSIVE**（不确定）裁决。所有逻辑均运行在**确定性整数运算**上：每个状态、每次比较和每个决策均使用精确整数标志，消除舍入误差，确保跨实验室的位级可复现性。

### 关键概念

| 组件 | 通俗描述 | 科学作用 |
|---|---|---|
| **CollapseVerdict** | 分配给证据集的最终分类标签：COHERENT、FRAGMENTED 或 INCONCLUSIVE。 | 传达复合证据的结构完整性状态。 |
| **传感器独立性** | 保证每个证据源通过隔离的独立通道观测目标事件。 | 防止循环印证：两个工件实际上是伪装成两个的单一来源。 |
| **依赖图** | 编码证据源之间已知因果关系的有向图。 | 用于检测使跨源确认无效的隐藏共同起源。 |
| **折叠阈值** | COHERENT 裁决所需最少独立源数量的整数计数。 | 强制执行最低证据底线，低于此底线不能发出任何裁决。 |
| **激进模式（v2）** | 除全部依赖外还标记部分依赖的更严格检测设置。 | 通过扩大折叠检测标准减少虚假 COHERENT 裁决。 |
| **确定性整数运算** | 所有阈值比较和状态转换使用精确整数值。 | 保证跨平台和跨次运行的相同决策。 |

### 词汇表
1. **COHERENT 裁决** — 结论认定复合证据结构合理且相互印证。
2. **折叠** — 证据源共享隐藏依赖关系、使相互印证失效的条件。
3. **依赖图** — 编码证据源之间因果关系的数学结构。
4. **确定性整数运算** — 仅使用精确整数比较和计数的计算；无近似值。
5. **FRAGMENTED 裁决** — 结论认定证据源结构不一致，暗示存在部分篡改。
6. **INCONCLUSIVE** — 无法建立传感器独立性时 CDL 发出的裁决。
7. **传感器独立性** — 确保每个证据源通过不同独立观测通道运作的属性。
8. **折叠阈值** — COHERENT 裁决所需真正独立源的最低整数计数。
9. **激进模式** — 同时标记部分和完全依赖关系的检测配置。
10. **交叉印证** — 独立源确认同一事件可强化结论的取证原则。

> **【科学说明】**
> 皮尔斯、艾柯和格赖斯的术语并非神秘主义。在 VIGÍA 中，传感器独立性是皮尔斯意义上的要求：两个*索引*只有在来自因果无关的观测通道时，才能构成独立证据。艾柯的解释原则警告不要将共享共同代码的两个符号视为独立的。当分析员将两个派生来源呈现为两个主要来源时，格赖斯的数量准则即遭到违反。

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
