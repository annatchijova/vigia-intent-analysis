<!--
VIGIA Academic Documentation
Module: e782beeb
Batch ID: vigia-doc-0142-e782beeb
Generated: 2026-05-20T14:56:47.875056+00:00
-->

---

## ENGLISH

### What Is This Module?

The **SIFT Orchestrator V4** is the central coordination engine of the VIGÍA forensic collective. It functions as a deterministic pipeline manager that directs fourteen or more specialized analytical engines—collectively called SIFT engines—to examine digital evidence. The orchestrator does not perform analysis itself; rather, it enforces strict operational rules: every file path is validated before any disk access occurs (TOCTOU protection), and each engine operates inside an isolated failure domain so that a malfunction in one component cannot collapse the entire investigation. All state transitions rely on exact integer arithmetic and boolean validation flags; no approximations are used anywhere in the evidence-handling logic.

### Evidence Sources

| Source | Description |
|---|---|
| Prefetch Directory | A folder containing `.pf` files that log program execution times and paths. |
| USB Registry Hive | A binary registry database file recording USB device attachment and configuration history. |

### Key Concepts

| Concept | Description | Scientific Role |
|---|---|---|
| **SIFT Engine** | A specialized analytical module (e.g., Metabolic, Resonance, Temporal) responsible for one category of forensic analysis. | The atomic unit of analytical capability in the collective. |
| **Isolated Failure Domain** | An architectural boundary preventing a fault in one engine from propagating to others. | Ensures that a partial failure yields a partial result rather than total investigation collapse. |
| **TOCTOU Protection** | Time-Of-Check to Time-Of-Use validation: file paths are re-verified at the moment of access, not merely at scheduling time. | Prevents path substitution attacks during multi-step investigations. |
| **Deterministic Pipeline** | A sequenced set of analytical steps where each step's output is entirely determined by its input and the current validated state. | Guarantees reproducibility: the same evidence set always produces the same analytical path. |
| **Boolean Validation Flag** | An exact two-value (true/false) indicator used to gate every state transition. | Eliminates ambiguous intermediate states from the evidence-handling logic. |

### Core Operations

| Operation | Purpose |
|---|---|
| `orchestrate()` | Accepts an evidence manifest, validates all paths, dispatches engines in order, and aggregates results into a unified report. |
| `validate_paths()` | Performs TOCTOU-safe validation on every evidence file path before dispatching any engine. |
| `dispatch()` | Sends a validated evidence item to the appropriate SIFT engine and records the result. |
| `aggregate()` | Combines individual engine results into a single, integrity-verified forensic bundle. |

### Glossary
1. **Dispatch** — The act of sending a validated evidence item to a specific analytical engine for processing.
2. **Deterministic Pipeline** — An analytical sequence where identical inputs always produce identical outputs and processing paths.
3. **Evidence Manifest** — A structured list of evidence file paths and their associated metadata, validated before processing begins.
4. **Failure Domain** — An architectural boundary limiting the scope of damage from a component malfunction.
5. **Forensic Bundle** — The sealed, integrity-verified output container aggregating all engine results.
6. **Isolated Engine** — An analytical component encapsulated so its failure does not affect sibling components.
7. **Orchestrator** — The central coordination component that manages engine sequencing, path validation, and result aggregation.
8. **Prefetch File** — A Windows artifact recording program execution events; input source for temporal analysis engines.
9. **SIFT Engine** — A specialized VIGÍA analytical module responsible for one forensic domain.
10. **TOCTOU Protection** — Time-Of-Check to Time-Of-Use: re-validating file paths at the moment of access to prevent substitution attacks.

> **【Scientific Note】**
> Peirce/Eco/Grice terminology is NOT mysticism. In VIGÍA, the SIFT Orchestrator operates at the level of Peircean *Thirdness*: it is the rule-governed system that transforms raw signals (Firstness) and structural anomalies (Secondness) into a coherent investigative conclusion. Eco's principle of code consistency requires that all engines apply the same interpretive rules to the same evidence. Grice's maxim of manner demands that the analytical process be orderly and unambiguous — the orchestrator enforces this at the architectural level.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## ESPAÑOL

### ¿Qué es este módulo?

El **Orquestador SIFT V4** es el motor de coordinación central del colectivo forense VIGÍA. Funciona como un gestor de canalización determinista que dirige catorce o más motores analíticos especializados—denominados colectivamente motores SIFT—para examinar evidencia digital. El orquestador no realiza análisis por sí mismo; en cambio, impone reglas operacionales estrictas: cada ruta de archivo se valida antes de cualquier acceso al disco (protección TOCTOU), y cada motor opera dentro de un dominio de fallo aislado para que un mal funcionamiento en un componente no pueda colapsar toda la investigación. Todas las transiciones de estado dependen de aritmética entera exacta e indicadores booleanos de validación; no se usan aproximaciones en ningún lugar de la lógica de manejo de evidencia.

### Fuentes de evidencia

| Fuente | Descripción |
|---|---|
| Directorio Prefetch | Carpeta que contiene archivos `.pf` que registran tiempos y rutas de ejecución de programas. |
| Registro USB | Archivo de base de datos de registro binario que registra el historial de conexión y configuración de dispositivos USB. |

### Conceptos clave

| Concepto | Descripción | Rol científico |
|---|---|---|
| **Motor SIFT** | Módulo analítico especializado responsable de una categoría de análisis forense. | Unidad atómica de capacidad analítica en el colectivo. |
| **Dominio de Fallo Aislado** | Límite arquitectónico que impide que un fallo en un motor se propague a otros. | Garantiza que un fallo parcial produzca un resultado parcial en lugar de colapso total de la investigación. |
| **Protección TOCTOU** | Validación de Tiempo-De-Verificación a Tiempo-De-Uso: las rutas de archivo se re-verifican en el momento del acceso. | Previene ataques de sustitución de rutas durante investigaciones en múltiples pasos. |
| **Canalización Determinista** | Conjunto secuenciado de pasos analíticos donde la salida de cada paso está completamente determinada por su entrada. | Garantiza reproducibilidad: el mismo conjunto de evidencia siempre produce el mismo camino analítico. |
| **Indicador Booleano de Validación** | Indicador exacto de dos valores (verdadero/falso) usado para controlar cada transición de estado. | Elimina estados intermedios ambiguos de la lógica de manejo de evidencia. |

### Glosario
1. **Despacho** — Acto de enviar un elemento de evidencia validado a un motor analítico específico para su procesamiento.
2. **Canalización Determinista** — Secuencia analítica donde entradas idénticas siempre producen salidas idénticas y caminos de procesamiento idénticos.
3. **Manifiesto de Evidencia** — Lista estructurada de rutas de archivos de evidencia y sus metadatos asociados, validados antes de comenzar el procesamiento.
4. **Dominio de Fallo** — Límite arquitectónico que limita el alcance del daño de un mal funcionamiento de un componente.
5. **Paquete Forense** — Contenedor sellado y verificado de integridad que agrega todos los resultados de los motores.
6. **Motor Aislado** — Componente analítico encapsulado para que su fallo no afecte a los componentes hermanos.
7. **Orquestador** — Componente de coordinación central que gestiona la secuenciación de motores, validación de rutas y agregación de resultados.
8. **Archivo Prefetch** — Artefacto de Windows que registra eventos de ejecución de programas; fuente de entrada para motores de análisis temporal.
9. **Motor SIFT** — Módulo analítico especializado de VIGÍA responsable de un dominio forense.
10. **Protección TOCTOU** — Tiempo-De-Verificación a Tiempo-De-Uso: re-validación de rutas en el momento del acceso para prevenir ataques de sustitución.

> **【Nota Científica】**
> La terminología de Peirce/Eco/Grice no es misticismo. En VIGÍA, el Orquestador SIFT opera al nivel de la *Terceridad* peirceana: es el sistema gobernado por reglas que transforma señales en bruto (Primeridad) y anomalías estructurales (Segundidad) en una conclusión investigativa coherente. El principio de consistencia de código de Eco requiere que todos los motores apliquen las mismas reglas interpretativas a la misma evidencia. La máxima de modo de Grice exige que el proceso analítico sea ordenado e inequívoco.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## РУССКИЙ

### Что это за модуль?

**Оркестратор SIFT V4** является центральным координационным движком криминалистического коллектива VIGÍA. Он функционирует как детерминированный менеджер конвейера, направляющий четырнадцать или более специализированных аналитических движков — именуемых коллективно движками SIFT — для изучения цифровых доказательств. Оркестратор сам не проводит анализ; вместо этого он применяет строгие операционные правила: каждый путь к файлу проверяется до любого доступа к диску (защита TOCTOU), и каждый движок работает внутри изолированного домена сбоев, так что неисправность одного компонента не может обрушить всё расследование. Все переходы состояний опираются на точную целочисленную арифметику и логические флаги валидации.

### Источники доказательств

| Источник | Описание |
|---|---|
| Директория Prefetch | Папка, содержащая файлы `.pf`, регистрирующие время и пути выполнения программ. |
| Куст реестра USB | Двоичный файл базы данных реестра, фиксирующий историю подключения и конфигурации USB-устройств. |

### Ключевые концепции

| Концепция | Описание | Научная роль |
|---|---|---|
| **Движок SIFT** | Специализированный аналитический модуль, отвечающий за одну категорию криминалистического анализа. | Атомарная единица аналитических возможностей коллектива. |
| **Изолированный домен сбоев** | Архитектурная граница, препятствующая распространению сбоя одного движка на другие. | Обеспечивает частичный результат при частичном сбое, а не полный коллапс расследования. |
| **Защита TOCTOU** | Валидация от момента проверки до момента использования: пути к файлам повторно верифицируются в момент доступа. | Предотвращает атаки подстановки путей в ходе многоэтапных расследований. |
| **Детерминированный конвейер** | Последовательный набор аналитических шагов, где выход каждого шага полностью определяется входом. | Гарантирует воспроизводимость: одинаковый набор доказательств всегда порождает одинаковый аналитический путь. |
| **Логический флаг валидации** | Точный двузначный (истина/ложь) индикатор, используемый для управления каждым переходом состояния. | Исключает неоднозначные промежуточные состояния из логики обработки доказательств. |

### Глоссарий
1. **Диспетчеризация** — Акт отправки верифицированного элемента доказательства конкретному аналитическому движку для обработки.
2. **Детерминированный конвейер** — Аналитическая последовательность, при которой идентичные входные данные всегда порождают идентичные выходные данные и пути обработки.
3. **Манифест доказательств** — Структурированный список путей к файлам доказательств и их метаданных, верифицированных до начала обработки.
4. **Домен сбоев** — Архитектурная граница, ограничивающая ущерб от неисправности компонента.
5. **Криминалистический пакет** — Запечатанный, верифицированный по целостности выходной контейнер, агрегирующий все результаты движков.
6. **Изолированный движок** — Аналитический компонент, инкапсулированный так, чтобы его сбой не затрагивал соседние компоненты.
7. **Оркестратор** — Центральный координационный компонент, управляющий последовательностью движков, валидацией путей и агрегацией результатов.
8. **Файл Prefetch** — Артефакт Windows, фиксирующий события выполнения программ; источник входных данных для движков временного анализа.
9. **Движок SIFT** — Специализированный аналитический модуль VIGÍA, отвечающий за один криминалистический домен.
10. **Защита TOCTOU** — Повторная верификация путей к файлам в момент доступа для предотвращения атак подстановки.

> **【Научное примечание】**
> Терминология Пирса, Эко и Грайса — не мистика. В VIGÍA Оркестратор SIFT работает на уровне пирсовской *Третичности*: это система, управляемая правилами, которая преобразует необработанные сигналы (Первичность) и структурные аномалии (Вторичность) в связный следственный вывод. Принцип согласованности кода Эко требует, чтобы все движки применяли одинаковые интерпретационные правила к одинаковым доказательствам. Максима манеры Грайса требует, чтобы аналитический процесс был упорядоченным и однозначным.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## 中文

### 这是什么模块？

**SIFT 编排器 V4** 是 VIGÍA 取证集合的中央协调引擎。它作为确定性流水线管理器，指挥十四个或更多专业分析引擎——统称为 SIFT 引擎——检查数字证据。编排器本身不进行分析；相反，它强制执行严格的操作规则：在任何磁盘访问发生之前验证每个文件路径（TOCTOU 保护），每个引擎在隔离的故障域内运行，使一个组件的故障不会导致整个调查崩溃。所有状态转换依赖精确整数运算和布尔验证标志；证据处理逻辑中不使用任何近似值。

### 证据来源

| 来源 | 描述 |
|---|---|
| Prefetch 目录 | 包含记录程序执行时间和路径的 `.pf` 文件的文件夹。 |
| USB 注册表配置文件 | 记录 USB 设备连接和配置历史的二进制注册表数据库文件。 |

### 关键概念

| 概念 | 描述 | 科学作用 |
|---|---|---|
| **SIFT 引擎** | 负责一类取证分析的专业分析模块。 | 集合中分析能力的原子单元。 |
| **隔离故障域** | 防止一个引擎的故障传播到其他引擎的架构边界。 | 确保部分故障产生部分结果，而非调查全面崩溃。 |
| **TOCTOU 保护** | 检查时到使用时验证：文件路径在访问时重新验证，而非仅在调度时验证。 | 在多步骤调查期间防止路径替换攻击。 |
| **确定性流水线** | 一系列分析步骤，每一步的输出完全由其输入和当前验证状态决定。 | 保证可复现性：相同证据集始终产生相同分析路径。 |
| **布尔验证标志** | 用于控制每个状态转换的精确双值（真/假）指示器。 | 从证据处理逻辑中消除模糊的中间状态。 |

### 词汇表
1. **调度** — 将验证的证据项发送到特定分析引擎进行处理的行为。
2. **确定性流水线** — 相同输入始终产生相同输出和处理路径的分析序列。
3. **证据清单** — 处理开始前经过验证的证据文件路径及其关联元数据的结构化列表。
4. **故障域** — 限制组件故障损害范围的架构边界。
5. **取证捆绑包** — 聚合所有引擎结果的密封完整性验证输出容器。
6. **隔离引擎** — 封装使其故障不影响相邻组件的分析组件。
7. **编排器** — 管理引擎排序、路径验证和结果聚合的中央协调组件。
8. **Prefetch 文件** — 记录程序执行事件的 Windows 工件；时序分析引擎的输入来源。
9. **SIFT 引擎** — 负责一个取证领域的 VIGÍA 专业分析模块。
10. **TOCTOU 保护** — 在访问时重新验证文件路径以防止替换攻击。

> **【科学说明】**
> 皮尔斯、艾柯和格赖斯的术语并非神秘主义。在 VIGÍA 中，SIFT 编排器在皮尔斯*第三性*层面运作：它是将原始信号（第一性）和结构异常（第二性）转化为连贯调查结论的规则驱动系统。艾柯的代码一致性原则要求所有引擎对相同证据应用相同的解释规则。格赖斯的方式准则要求分析过程有序且明确——编排器在架构层面强制执行这一点。

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
