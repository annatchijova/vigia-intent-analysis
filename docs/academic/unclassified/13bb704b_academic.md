<!--
VIGIA Academic Documentation
Module: 13bb704b
Batch ID: vigia-doc-0006-13bb704b
Generated: 2026-05-20T14:56:47.846269+00:00
-->

## ENGLISH

### What Is This Module?
The `recalibrate_cases.py` module synchronizes the `expected_verdict` field in case JSON files with the current deterministic logic of the EBS v1 scorer, inclusive of all applied patches. It restricts write operations to cases absent from the `KNOWN_LIMITATIONS` registry; documented limitation cases are logged for audit but preserved unchanged. This maintains reference dataset integrity while respecting established boundary conditions.

*Scientific note: Because the EBS v1 scorer is deterministic, any mismatch between stored and rendered verdicts indicates a logic revision rather than stochastic variance.*

### Key Concepts
| Term (English) | Español | Русский | 中文 |
|---|---|---|---|
| Expected verdict | Veredicto de referencia previsto. | Ожидаемый вердикт. | 预期判决。 |
| Case JSON | Archivo estructurado de parámetros del caso. | Структурированный файл параметров кейса. | 案例结构化参数文件。 |
| EBS v1 scorer | Evaluador determinista de veredictos. | Детерминированный модуль оценки. | 确定性判决评估引擎。 |
| Patch | Actualización puntual de la lógica del sistema. | Целевое обновление логики системы. | 系统逻辑局部更新。 |
| Known limitations | Registro de condiciones límite documentadas. | Реестр задокументированных ограничений. | 已记录限制登记册。 |
| Deterministic system | Sistema cuya salida es idéntica para entrada idéntica. | Система с идентичным выходом при идентичном входе. | 相同输入产生相同输出的系统。 |
| Reference dataset | Conjunto de casos validados como línea base. | Валидированный эталонный набор данных. | 经验证的基准数据集。 |
| Recalibration | Alineación de valores esperados con la lógica actual. | Приведение ожидаемых значений к текущей логике. | 将预期值与当前逻辑对齐。 |
| Boundary conditions | Límites operativos definidos o restringidos. | Определённые или ограниченные операционные пределы. | 被定义或受限的运行边界。 |
| Audit log | Registro inmutable de eventos de revisión. | Неизменяемый журнал событий проверки. | 不可变的审查事件记录。 |

> **【Scientific Note】**
> Peirce/Eco/Grice terminology is NOT mysticism. These are formal sensors of meaning: Peircean abduction generates hypotheses from observed anomalies exactly as a spectrometer generates spectral lines from incident light. Eco's codes map signs to interpretations deterministically. Grice's maxims define baseline communication norms whose violation registers as a measurable signal anomaly.

### Glossary
1. **Expected verdict** — The ground-truth outcome predicted for a case before running the scorer.
2. **Case JSON** — Structured text file storing a single case's parameters and expected results.
3. **EBS v1 Scorer** — Deterministic evaluation engine for rendering forensic verdicts.
4. **Patch** — A targeted update to system logic without full replacement.
5. **Known Limitations** — Catalog of documented boundary conditions exempt from automatic change.
6. **Deterministic System** — System where identical inputs always produce identical outputs.
7. **Reference Dataset** — Collection of validated cases used as a behavioral baseline.
8. **Recalibration** — Process of aligning expected values with current system logic.
9. **Boundary Conditions** — Operational limits where standard behavior is defined or constrained.
10. **Audit Log** — Immutable record of reported but unchanged limited cases.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## ESPAÑOL

### ¿Qué es este módulo?
El módulo `recalibrate_cases.py` sincroniza el campo `expected_verdict` en los archivos JSON de casos con la lógica determinista actual del evaluador EBS v1, incluidos todos los parches aplicados. Restringe las operaciones de escritura a casos ausentes del registro `KNOWN_LIMITATIONS`; los casos con limitaciones documentadas se registran para auditoría pero se preservan sin cambios. Así se mantiene la integridad del conjunto de referencia respetando las condiciones límite establecidas.

*Nota científica: dado que el evaluador EBS v1 es determinista, cualquier discrepancia entre el veredicto almacenado y el emitido indica una revisión lógica y no una variación estocástica.*

### Conceptos clave
| Término (EN) | Español | Русский | 中文 |
|---|---|---|---|
| Expected verdict | Veredicto de referencia previsto. | Ожидаемый вердикт. | 预期判决。 |
| Case JSON | Archivo estructurado de parámetros del caso. | Структурированный файл параметров кейса. | 案例结构化参数文件。 |
| EBS v1 scorer | Evaluador determinista de veredictos. | Детерминированный модуль оценки. | 确定性判决评估引擎。 |
| Patch | Actualización puntual de la lógica del sistema. | Целевое обновление логики системы. | 系统逻辑局部更新。 |
| Known limitations | Registro de condiciones límite documentadas. | Реестр задокументированных ограничений. | 已记录限制登记册。 |
| Deterministic system | Sistema cuya salida es idéntica para entrada idéntica. | Система с идентичным выходом при идентичном входе. | 相同输入产生相同输出的系统。 |
| Reference dataset | Conjunto de casos validados como línea base. | Валидированный эталонный набор данных. | 经验证的基准数据集。 |
| Recalibration | Alineación de valores esperados con la lógica actual. | Приведение ожидаемых значений к текущей логике. | 将预期值与当前逻辑对齐。 |
| Boundary conditions | Límites operativos definidos o restringidos. | Определённые или ограниченные операционные пределы. | 被定义或受限的运行边界。 |
| Audit log | Registro inmutable de eventos de revisión. | Неизменяемый журнал событий проверки. | 不可变的审查事件记录。 |

> **【Nota Científica】**
> La terminología de Peirce, Eco y Grice NO es misticismo. Son sensores formales de significado: la abducción peirceana genera hipótesis a partir de anomalías observadas, exactamente como un espectrómetro genera líneas espectrales a partir de luz incidente. Los códigos de Eco mapean signos a interpretaciones de forma determinista. Las máximas de Grice definen normas de comunicación de referencia cuya violación se registra como una anomalía de señal medible.

### Glosario
1. **Veredicto esperado** — El resultado de verdad de referencia previsto para un caso antes de ejecutar el evaluador.
2. **JSON de caso** — Archivo de texto estructurado que almacena los parámetros de un caso.
3. **Evaluador EBS v1** — Motor de evaluación determinista para emitir veredictos forenses.
4. **Parche** — Actualización puntual de la lógica del sistema sin reemplazo completo.
5. **Limitaciones conocidas** — Catálogo de condiciones límite documentadas exentas de cambio automático.
6. **Sistema determinista** — Sistema en el que entradas idénticas producen siempre salidas idénticas.
7. **Conjunto de referencia** — Colección de casos validados usados como línea base de comportamiento.
8. **Recalibración** — Proceso de alineación de valores esperados con la lógica actual del sistema.
9. **Condiciones límite** — Límites operativos donde el comportamiento estándar se define o restringe.
10. **Registro de auditoría** — Registro inmutable de casos limitados reportados pero no modificados.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## РУССКИЙ

### Что это за модуль?
Модуль `recalibrate_cases.py` синхронизирует поле `expected_verdict` в JSON-файлах кейсов с текущей детерминированной логикой скорера EBS v1 с учётом всех применённых патчей. Запись изменений ограничена кейсами, отсутствующими в реестре `KNOWN_LIMITATIONS`; кейсы с задокументированными ограничениями фиксируются в журнале аудита, но сохраняются неизменными. Это поддерживает целостность эталонного набора с соблюдением установленных граничных условий.

*Научное примечание: поскольку скорер EBS v1 детерминирован, любое несоответствие между сохранённым и вычисленным вердиктом свидетельствует о логической ревизии, а не о стохастическом разбросе.*

### Ключевые понятия
| Термин (EN) | Español | Русский | 中文 |
|---|---|---|---|
| Expected verdict | Veredicto de referencia previsto. | Ожидаемый вердикт. | 预期判决。 |
| Case JSON | Archivo estructurado de parámetros del caso. | Структурированный файл параметров кейса. | 案例结构化参数文件。 |
| EBS v1 scorer | Evaluador determinista de veredictos. | Детерминированный модуль оценки. | 确定性判决评估引擎。 |
| Patch | Actualización puntual de la lógica del sistema. | Целевое обновление логики системы. | 系统逻辑局部更新。 |
| Known limitations | Registro de condiciones límite documentadas. | Реестр задокументированных ограничений. | 已记录限制登记册。 |
| Deterministic system | Sistema cuya salida es idéntica para entrada idéntica. | Система с идентичным выходом при идентичном входе. | 相同输入产生相同输出的系统。 |
| Reference dataset | Conjunto de casos validados como línea base. | Валидированный эталонный набор данных. | 经验证的基准数据集。 |
| Recalibration | Alineación de valores esperados con la lógica actual. | Приведение ожидаемых значений к текущей логике. | 将预期值与当前逻辑对齐。 |
| Boundary conditions | Límites operativos definidos o restringidos. | Определённые или ограниченные операционные пределы. | 被定义或受限的运行边界。 |
| Audit log | Registro inmutable de eventos de revisión. | Неизменяемый журнал событий проверки. | 不可变的审查事件记录。 |

> **【Научное примечание】**
> Терминология Пирса, Эко и Грайса — НЕ мистицизм. Это формальные сенсоры смысла: абдукция Пирса генерирует гипотезы из наблюдаемых аномалий точно так же, как спектрометр генерирует спектральные линии из падающего света. Коды Эко детерминированно отображают знаки в интерпретации. Максимы Грайса задают базовые нормы коммуникации, нарушение которых регистрируется как измеримая аномалия сигнала.

### Глоссарий
1. **Ожидаемый вердикт** — Эталонный результат, предсказанный для кейса до запуска скорера.
2. **JSON-файл кейса** — Структурированный текстовый файл с параметрами кейса.
3. **Скорер EBS v1** — Детерминированный вычислительный модуль для формирования вердиктов.
4. **Патч** — Целевое обновление логики системы без полной замены.
5. **Известные ограничения** — Реестр задокументированных граничных условий, исключённых из изменений.
6. **Детерминированная система** — Система, в которой одинаковые входные данные всегда дают одинаковый результат.
7. **Эталонный набор** — Набор валидированных кейсов, используемый в качестве поведенческого базиса.
8. **Рекалибровка** — Процесс приведения ожидаемых значений в соответствие с текущей логикой системы.
9. **Граничные условия** — Операционные пределы, в рамках которых стандартное поведение определено или ограничено.
10. **Журнал аудита** — Неизменяемая запись о зафиксированных, но не изменённых ограниченных кейсах.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## 中文

### 这是什么模块？
`recalibrate_cases.py` 模块将案例 JSON 文件中的 `expected_verdict` 字段与当前 EBS v1 评分器的确定性逻辑（含全部已应用补丁）进行同步。写操作仅针对不在 `KNOWN_LIMITATIONS` 登记册中的案例；已记录限制的案例记入审计日志但原样保留。由此在尊重已确立边界条件的同时维护参考数据集的完整性。

*科学注释：由于 EBS v1 评分器具有确定性，存储判决与生成判决之间的任何差异均表明逻辑修订，而非随机方差。*

### 核心概念
| 术语 (EN) | Español | Русский | 中文 |
|---|---|---|---|
| Expected verdict | Veredicto de referencia previsto. | Ожидаемый вердикт. | 预期判决。 |
| Case JSON | Archivo estructurado de parámetros del caso. | Структурированный файл параметров кейса. | 案例结构化参数文件。 |
| EBS v1 scorer | Evaluador determinista de veredictos. | Детерминированный модуль оценки. | 确定性判决评估引擎。 |
| Patch | Actualización puntual de la lógica del sistema. | Целевое обновление логики системы. | 系统逻辑局部更新。 |
| Known limitations | Registro de condiciones límite documentadas. | Реестр задокументированных ограничений. | 已记录限制登记册。 |
| Deterministic system | Sistema cuya salida es idéntica para entrada idéntica. | Система с идентичным выходом при идентичном входе. | 相同输入产生相同输出的系统。 |
| Reference dataset | Conjunto de casos validados como línea base. | Валидированный эталонный набор данных. | 经验证的基准数据集。 |
| Recalibration | Alineación de valores esperados con la lógica actual. | Приведение ожидаемых значений к текущей логике. | 将预期值与当前逻辑对齐。 |
| Boundary conditions | Límites operativos definidos o restringidos. | Определённые или ограниченные операционные пределы. | 被定义或受限的运行边界。 |
| Audit log | Registro inmutable de eventos de revisión. | Неизменяемый журнал событий проверки. | 不可变的审查事件记录。 |

> **【科学说明】**
> 皮尔士/艾柯/格赖斯的术语并非神秘主义。它们是意义的形式传感器：皮尔士的溯因推理从观测到的异常中生成假设，正如光谱仪从入射光中生成谱线。艾柯的编码以确定性方式将符号映射到解释。格赖斯的准则定义了基准通信规范，其违反被记录为可测量的信号异常。

### 词汇表
1. **预期判决** — 在运行评分器之前为案例预设的基准真值结果。
2. **案例 JSON** — 存储单个案例参数的结构化文本文件。
3. **EBS v1 评分器** — 用于生成取证判决的确定性评估引擎。
4. **补丁** — 针对系统逻辑的局部更新，无需完整替换。
5. **已知限制** — 免于自动更改的已记录边界条件目录。
6. **确定性系统** — 相同输入始终产生相同输出的系统。
7. **参考数据集** — 用作行为基线的已验证案例集合。
8. **重新校准** — 将预期值与当前系统逻辑对齐的过程。
9. **边界条件** — 标准行为被定义或受限的运行边界。
10. **审计日志** — 对已报告但未修改的限制案例的不可变记录。

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
