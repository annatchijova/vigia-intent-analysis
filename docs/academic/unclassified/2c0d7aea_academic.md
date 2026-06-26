<!--
VIGIA Academic Documentation
Module: 2c0d7aea
Batch ID: vigia-doc-0023-2c0d7aea
Generated: 2026-05-20T14:56:47.849557+00:00
-->

---

## ENGLISH

### What Is This Module?
The `run_vigia_full.py` module is the deterministic orchestration layer of the VIGÍA digital-forensics framework. It ingests a JSON case descriptor and sequentially performs evidential reasoning, bundle hashing, and integrity verification. All outputs are reproducible, audit-ready evidence bundles documenting chain-of-custody without probabilistic approximations. Scientists provide structured parameters; the module returns a tamper-evident evidence package suitable for chain-of-custody records. All computations rely on discrete logic and exact arithmetic.

### Key Concepts

| Concept | Definition | Technical Role |
|---|---|---|
| **Case Descriptor** | A structured JSON file defining the forensic parameters of an investigation. | The sole input; its exact contents determine the entire output deterministically. |
| **Evidential Reasoning** | The sequential application of logical inference rules to the case descriptor to produce findings. | Transforms raw case data into structured forensic conclusions. |
| **Bundle Hashing** | SHA-256 cryptographic fingerprinting of the assembled evidence bundle. | Provides a tamper-evident seal verifiable by any independent party. |
| **Integrity Verification** | Recomputation of hashes to confirm that no evidence has been altered since sealing. | Closes the chain-of-custody loop before report submission. |
| **Orchestration Layer** | The software component that coordinates the sequential execution of all pipeline stages. | Ensures stages execute in the correct order with validated inputs at each step. |
| **Deterministic System** | A process where identical inputs always yield identical outputs. | Guarantees reproducibility: any analyst running the same case descriptor receives the same result. |

> **【Scientific Note】**
> Peirce/Eco/Grice terminology is NOT mysticism. In VIGÍA, the orchestration layer embodies Peircean *Thirdness*: the rule-governed system that converts raw signals (case descriptor fields) through structured inference (Secondness) into a legally admissible conclusion (Thirdness). Grice's maxim of manner is operationalized as the requirement for sequential, unambiguous pipeline execution.

### Glossary
1. **Bundle Hash** — Cryptographic digest binding an evidence set to a specific state, enabling tamper detection.
2. **Case Descriptor** — Structured JSON input defining the forensic parameters of an investigation.
3. **Chain of Custody** — The documented, unbroken record of evidence handling from collection to court submission.
4. **Deterministic System** — A process where identical inputs always yield identical outputs.
5. **Digital Forensics** — The scientific recovery and investigation of material found in digital devices.
6. **Evidential Reasoning** — Logical inference applied to digital evidence to produce structured forensic conclusions.
7. **Integrity Verification** — The procedure confirming that data remains unaltered through hash recomputation.
8. **JSON** — JavaScript Object Notation; the structured text format used for the case descriptor.
9. **Orchestration Layer** — The software component coordinating the sequential execution of forensic pipeline stages.
10. **Tamper-Evident** — The property of a sealed evidence bundle whereby unauthorized modification is detectable through hash verification.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## ESPAÑOL

### ¿Qué es este módulo?
El módulo `run_vigia_full.py` es la capa de orquestación determinista del marco de informática forense digital VIGÍA. Ingiere un descriptor JSON de caso y ejecuta secuencialmente razonamiento probatorio, hash del paquete y verificación de integridad. Todos los resultados son paquetes de evidencia reproducibles y listos para auditoría que documentan la cadena de custodia sin aproximaciones probabilísticas. Los científicos proporcionan parámetros estructurados; el módulo devuelve un paquete de evidencia con indicación de manipulación adecuado para registros de cadena de custodia. Todos los cómputos se basan en lógica discreta y aritmética entera determinista.

### Conceptos clave

| Concepto | Definición | Rol técnico |
|---|---|---|
| **Descriptor de Caso** | Archivo JSON estructurado que define los parámetros forenses de una investigación. | La única entrada; su contenido exacto determina toda la salida de forma determinista. |
| **Razonamiento Probatorio** | Aplicación secuencial de reglas de inferencia lógica al descriptor de caso para producir hallazgos. | Transforma datos de caso en bruto en conclusiones forenses estructuradas. |
| **Hash del Paquete** | Huella digital criptográfica SHA-256 del paquete de evidencia ensamblado. | Proporciona un sello con indicación de manipulación verificable por cualquier parte independiente. |
| **Verificación de Integridad** | Recomputación de hashes para confirmar que ninguna evidencia ha sido alterada desde el sellado. | Cierra el ciclo de cadena de custodia antes del envío del informe. |
| **Capa de Orquestación** | Componente software que coordina la ejecución secuencial de todas las etapas de la canalización. | Garantiza que las etapas se ejecuten en el orden correcto con entradas validadas en cada paso. |
| **Sistema Determinista** | Proceso donde entradas idénticas siempre producen salidas idénticas. | Garantiza reproducibilidad: cualquier analista que ejecute el mismo descriptor de caso recibe el mismo resultado. |

> **【Nota Científica】**
> La terminología de Peirce/Eco/Grice no es misticismo. En VIGÍA, la capa de orquestación encarna la *Terceridad* peirceana: el sistema gobernado por reglas que convierte señales en bruto a través de inferencia estructurada en una conclusión legalmente admisible. La máxima de modo de Grice se operacionaliza como el requisito de ejecución secuencial e inequívoca de la canalización.

### Glosario
1. **Hash del Paquete** — Resumen criptográfico que vincula un conjunto de evidencia a un estado específico, permitiendo la detección de manipulación.
2. **Descriptor de Caso** — Entrada JSON estructurada que define los parámetros forenses de una investigación.
3. **Cadena de Custodia** — Registro documentado e ininterrumpido del manejo de evidencia desde la recolección hasta la presentación judicial.
4. **Sistema Determinista** — Proceso donde entradas idénticas siempre producen salidas idénticas.
5. **Informática Forense Digital** — Recuperación e investigación científica de material encontrado en dispositivos digitales.
6. **Razonamiento Probatorio** — Inferencia lógica aplicada a evidencia digital para producir conclusiones forenses estructuradas.
7. **Verificación de Integridad** — Procedimiento que confirma que los datos permanecen inalterados mediante recomputación de hashes.
8. **JSON** — JavaScript Object Notation; formato de texto estructurado utilizado para el descriptor de caso.
9. **Capa de Orquestación** — Componente software que coordina la ejecución secuencial de las etapas de la canalización forense.
10. **Con Indicación de Manipulación** — Propiedad de un paquete de evidencia sellado por la que cualquier modificación no autorizada es detectable mediante verificación de hash.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## РУССКИЙ

### Что это за модуль?
Модуль `run_vigia_full.py` является детерминированным оркестрационным слоем цифровой криминалистической платформы VIGÍA. Получая JSON-дескриптор случая, он последовательно выполняет доказательное рассуждение, хеширование пакета и проверку целостности. Все результаты представляют собой воспроизводимые, пригодные для аудита пакеты доказательств, документирующие цепочку хранения без вероятностных приближений. Учёные предоставляют структурированные параметры; модуль возвращает пакет доказательств с индикацией вмешательства, пригодный для записей цепочки хранения. Все вычисления опираются на дискретную логику и точную целочисленную арифметику.

### Ключевые концепции

| Концепция | Определение | Техническая роль |
|---|---|---|
| **Дескриптор случая** | Структурированный JSON-файл, определяющий криминалистические параметры расследования. | Единственный входной параметр; его точное содержание детерминировано определяет весь вывод. |
| **Доказательное рассуждение** | Последовательное применение правил логического вывода к дескриптору случая для получения выводов. | Преобразует необработанные данные случая в структурированные криминалистические заключения. |
| **Хеширование пакета** | SHA-256 криптографическая дактилоскопия собранного пакета доказательств. | Обеспечивает печать с индикацией вмешательства, верифицируемую любой независимой стороной. |
| **Проверка целостности** | Повторное вычисление хешей для подтверждения неизменности доказательств с момента опечатывания. | Замыкает цикл цепочки хранения перед представлением отчёта. |
| **Оркестрационный слой** | Программный компонент, координирующий последовательное выполнение всех стадий конвейера. | Гарантирует выполнение стадий в правильном порядке с верифицированными входными данными на каждом шаге. |
| **Детерминированная система** | Процесс, при котором одинаковые входные данные всегда дают одинаковые выходные. | Гарантирует воспроизводимость: любой аналитик, запускающий тот же дескриптор случая, получает тот же результат. |

> **【Научное примечание】**
> Терминология Пирса, Эко и Грайса — не мистика. В VIGÍA оркестрационный слой воплощает пирсовскую *Третичность*: систему, управляемую правилами, которая преобразует необработанные сигналы через структурированный вывод в юридически допустимое заключение. Максима манеры Грайса операционализируется как требование последовательного и однозначного выполнения конвейера.

### Глоссарий
1. **Хеш пакета** — Криптографический дайджест, связывающий набор доказательств с конкретным состоянием, обеспечивая обнаружение вмешательства.
2. **Дескриптор случая** — Структурированный JSON-вход, определяющий криминалистические параметры расследования.
3. **Цепочка хранения** — Задокументированная, непрерывная запись об обращении с доказательствами от сбора до судебного представления.
4. **Детерминированная система** — Процесс, при котором одинаковые входные данные всегда дают одинаковые выходные.
5. **Цифровая криминалистика** — Научное восстановление и исследование материала с цифровых устройств.
6. **Доказательное рассуждение** — Логический вывод, применяемый к цифровым доказательствам для получения структурированных криминалистических заключений.
7. **Проверка целостности** — Процедура подтверждения неизменности данных через повторное вычисление хешей.
8. **JSON** — JavaScript Object Notation; структурированный текстовый формат для дескриптора случая.
9. **Оркестрационный слой** — Программный компонент, координирующий последовательное выполнение стадий криминалистического конвейера.
10. **С индикацией вмешательства** — Свойство запечатанного пакета доказательств, при котором любое несанкционированное изменение обнаруживается через верификацию хеша.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## 中文

### 这是什么模块？
`run_vigia_full.py` 模块是 VIGÍA 数字取证框架的确定性编排层。它读取 JSON 案件描述符，依次执行证据推理、捆绑哈希与完整性校验。所有输出均为可复现、可审计的证据包，记录保管链而不含概率近似。科学家提供结构化参数，模块返回具备防篡改特性的证据包以支持保管链记录。所有运算基于离散逻辑与精确整数运算。

### 关键概念

| 概念 | 定义 | 技术作用 |
|---|---|---|
| **案件描述符** | 定义调查取证参数的结构化 JSON 文件。 | 唯一输入；其精确内容以确定性方式决定全部输出。 |
| **证据推理** | 对案件描述符依次应用逻辑推理规则以产生发现。 | 将原始案件数据转化为结构化取证结论。 |
| **捆绑哈希** | 对组装好的证据包进行 SHA-256 加密指纹处理。 | 提供可由任何独立方验证的防篡改印章。 |
| **完整性校验** | 重新计算哈希以确认自密封以来证据未被更改。 | 在提交报告前完成保管链闭环。 |
| **编排层** | 协调所有流水线阶段按序执行的软件组件。 | 确保各阶段以正确顺序执行，并在每步验证输入。 |
| **确定性系统** | 相同输入始终产生相同输出的过程。 | 保证可复现性：任何分析员运行相同案件描述符均获得相同结果。 |

> **【科学说明】**
> 皮尔斯、艾柯和格赖斯的术语并非神秘主义。在 VIGÍA 中，编排层体现了皮尔斯的*第三性*：将原始信号（案件描述符字段）通过结构化推理（第二性）转化为法律可采结论（第三性）的规则驱动系统。格赖斯的方式准则被操作化为对按序、明确的流水线执行的要求。

### 词汇表
1. **捆绑哈希** — 将证据集绑定到特定状态以实现篡改检测的加密摘要。
2. **案件描述符** — 定义调查取证参数的结构化 JSON 输入。
3. **保管链** — 从收集到法庭提交的证据处理过程的书面、连续记录。
4. **确定性系统** — 相同输入始终产生相同输出的过程。
5. **数字取证** — 对数字设备中材料进行科学恢复与调查。
6. **证据推理** — 应用于数字证据以产生结构化取证结论的逻辑推理。
7. **完整性校验** — 通过哈希重算确认数据未被更改的程序。
8. **JSON** — JavaScript 对象表示法；案件描述符所用的结构化文本格式。
9. **编排层** — 协调取证流水线各阶段按序执行的软件组件。
10. **防篡改** — 密封证据包的属性，使任何未经授权的修改可通过哈希验证被检测到。

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
