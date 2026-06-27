<!--
VIGIA Academic Documentation
Module: f14e91cc
Batch ID: vigia-doc-0036-f14e91cc
Generated: 2026-05-20T14:56:47.852299+00:00
-->

# Module Documentation: `vigia/core/abductive_intent_engine.py` — HITO 2.1

## ENGLISH

**What Is This Module?**

This module is the abductive inference engine of the VIGÍA system. It functions like a digital forensic microscope that takes a chain of raw evidence artifacts (files, logs, timestamps) and reasons backward to propose the most probable attacker habit or intent. Instead of guessing, it compares competing explanatory hypotheses using a deterministic scoring rule based on Ockham's Razor: the explanation requiring the fewest unobserved assumptions wins. All calculations use integer arithmetic, ensuring that the same evidence always produces the same conclusion.

**Key Concepts**

| Concept | Role in Forensic Analysis | Scientific Parallel |
|---|---|---|
| Artifact | A raw piece of digital evidence (e.g., a log entry, hash, file fragment). In Peircean terms, an instance of *Firstness*—pure data before interpretation. | A voltage reading from a sensor before calibration |
| AbductiveHypothesis | A candidate explanation of *Thirdness*—a proposed law or habit that would generate the observed artifacts. | A theoretical model predicting how a physical process produces sensor readings |
| Ockham Cost | An integer count of unobserved assumptions a hypothesis requires. Lower is better. | The number of free parameters added to a model beyond the measured data |
| Coverage | An integer percentage (0–100) of observed artifacts explained by the hypothesis. | The ratio of data points accounted for by the model, expressed as a whole number |
| AbductiveResult | The final output: one winning hypothesis plus ranked alternatives (runners-up), ordered strictly by Ockham cost then coverage. | A ranked list of candidate models from a fitting procedure |
| infer_habit() | The core procedure: loads candidate templates, scores each against the evidence chain, and returns the deterministic best fit. | The automated measurement protocol that selects the best model |

**Glossary**

| Term | Definition |
|---|---|
| Abduction | The logical operation of inferring the best explanation from observed effects (Peirce). |
| Firstness (Primeridad) | The mode of being of a raw, uninterpreted datum. |
| Secondness (Segundidad) | The mode of being of brute factual connection or correlation between data points. |
| Thirdness (Terceridad) | The mode of being of law, habit, or general rule that explains patterns. |
| Ockham's Razor | The principle that, among competing explanations, the one with the fewest unnecessary assumptions is preferable. |
| Daubert Guarantee | A set of auditability requirements ensuring forensic methods are testable, explicit, and reproducible. |
| Deterministic | A system where identical inputs always yield identical outputs; no randomness or floating-point approximation is used. |
| Integer Arithmetic | Mathematical operations using whole numbers only, avoiding fractional or decimal representations. |

**Scientific Note**

【Scientific Note】
Terminology borrowed from Peirce, Eco, or Grice is **not** mysticism or literary criticism. In this engine, these terms function exactly like the components of a sensor array. **Firstness** is the raw voltage off the detector; **Secondness** is the correlation between two detectors firing; **Thirdness** is the calibrated physical law that predicts both. Treating abductive inference as a sensor pipeline makes the process auditable, deterministic, and entirely free of esoteric interpretation.

---

## ESPAÑOL

**¿Qué es este módulo?**

Este módulo es el motor de inferencia abductiva del sistema VIGÍA. Funciona como un microscopio forense digital que recibe una cadena de artefactos de evidencia brutos (archivos, registros, marcas de tiempo) y razona hacia atrás para proponer el hábito o la intención del atacante más probable. En lugar de conjeturar, compara hipótesis explicativas competidoras mediante una regla de puntuación determinista basada en la Navaja de Ockham: gana la explicación que requiere menos supuestos no observados. Todos los cálculos usan aritmética entera, garantizando que la misma evidencia siempre produce la misma conclusión.

**Tabla de conceptos clave**

| Concepto | Papel en el análisis forense | Paralelo científico |
|---|---|---|
| Artifact (Artefacto) | Pieza bruta de evidencia digital (p. ej., entrada de registro, hash, fragmento de archivo). En términos peirceanos, instancia de *Primeridad*: dato puro previo a la interpretación. | Lectura de voltaje de un sensor antes de la calibración |
| AbductiveHypothesis | Explicación candidata de *Terceridad*: ley o hábito propuesto que generaría los artefactos observados. | Modelo teórico que predice cómo un proceso físico produce lecturas de sensor |
| Costo Ockham | Conteo entero de supuestos no observados que requiere una hipótesis. Menor es mejor. | Número de parámetros libres añadidos a un modelo más allá de los datos medidos |
| Cobertura | Porcentaje entero (0–100) de artefactos observados explicados por la hipótesis. | Proporción de puntos de datos explicados por el modelo, expresada como número entero |
| AbductiveResult | Salida final: hipótesis ganadora más alternativas ordenadas, estrictamente por costo Ockham y luego cobertura. | Lista ordenada de modelos candidatos de un procedimiento de ajuste |
| infer_habit() | Procedimiento central: carga plantillas candidatas, puntúa cada una contra la cadena de evidencia y devuelve el mejor ajuste determinista. | Protocolo de medición automatizado que selecciona el mejor modelo |

**Glosario**

| Término | Definición |
|---|---|
| Abducción | Operación lógica de inferir la mejor explicación a partir de efectos observados (Peirce). |
| Primeridad (Firstness) | Modo de ser de un dato bruto, no interpretado. |
| Segundidad (Secondness) | Modo de ser de la conexión factual o correlación entre puntos de datos. |
| Terceridad (Thirdness) | Modo de ser de la ley, el hábito o la regla general que explica patrones. |
| Navaja de Ockham | Principio según el cual, entre explicaciones competidoras, se prefiere la que tiene menos supuestos innecesarios. |
| Garantía Daubert | Requisitos de auditabilidad que aseguran que los métodos forenses sean comprobables, explícitos y reproducibles. |
| Determinista | Sistema en el que entradas idénticas siempre producen salidas idénticas; no se usa aleatoriedad ni aproximación de coma flotante. |
| Aritmética entera | Operaciones matemáticas usando solo números enteros, evitando representaciones fraccionarias o decimales. |

**Nota científica**

【Scientific Note】
La terminología tomada de Peirce, Eco o Grice **no** es misticismo ni crítica literaria. En este motor, estos términos funcionan exactamente como los componentes de un arreglo de sensores. La **Primeridad** es el voltaje crudo del detector; la **Segundidad** es la correlación entre dos sensores que se activan; la **Terceridad** es la ley física calibrada que predice ambos. Tratar la inferencia abductiva como una tubería de sensores hace el proceso auditable, determinista y completamente libre de interpretación esotérica.

---

## РУССКИЙ

**Что это за модуль?**

Этот модуль — абдуктивный инференс-движок системы VIGÍA. Он работает как цифровой судебный микроскоп: получает цепочку необработанных артефактов доказательств (файлы, журналы, временные метки) и рассуждает в обратном направлении, предлагая наиболее вероятную привычку или намерение злоумышленника. Вместо догадок он сравнивает конкурирующие объяснительные гипотезы с помощью детерминированного правила оценки, основанного на Бритве Оккама: побеждает объяснение, требующее наименьшего числа ненаблюдаемых допущений. Все вычисления выполняются целочисленной арифметикой, гарантируя, что одни и те же доказательства всегда дают один и тот же вывод.

**Таблица ключевых понятий**

| Понятие | Роль в судебном анализе | Научный параллель |
|---|---|---|
| Artifact (Артефакт) | Необработанный фрагмент цифрового доказательства (например, запись журнала, хеш, фрагмент файла). В терминах Пирса — экземпляр *Первичности*: чистые данные до интерпретации. | Показание напряжения с датчика до калибровки |
| AbductiveHypothesis | Кандидат-объяснение *Третичности*: предполагаемый закон или привычка, которые могли породить наблюдаемые артефакты. | Теоретическая модель, предсказывающая, как физический процесс генерирует показания датчика |
| Стоимость по Оккаму | Целочисленный подсчёт ненаблюдаемых допущений, требуемых гипотезой. Чем меньше, тем лучше. | Количество свободных параметров модели, добавленных помимо измеренных данных |
| Покрытие | Целочисленный процент (0–100) наблюдаемых артефактов, объясняемых гипотезой. | Доля учтённых точек данных, выраженная целым числом |
| AbductiveResult | Итоговый результат: победившая гипотеза плюс упорядоченные альтернативы (по стоимости Оккама, затем покрытию). | Ранжированный список кандидат-моделей по результатам процедуры подгонки |
| infer_habit() | Основная процедура: загружает шаблоны-кандидаты, оценивает каждый по цепочке доказательств и возвращает детерминированное наилучшее соответствие. | Автоматизированный протокол измерения, выбирающий лучшую модель |

**Глоссарий**

| Термин | Определение |
|---|---|
| Абдукция | Логическая операция выведения наилучшего объяснения из наблюдаемых следствий (Пирс). |
| Первичность (Firstness/Primeridad) | Модус бытия необработанного, неинтерпретированного датчика. |
| Вторичность (Secondness/Segundidad) | Модус бытия фактической связи или корреляции между точками данных. |
| Третичность (Thirdness/Terceridad) | Модус бытия закона, привычки или общего правила, объясняющего закономерности. |
| Бритва Оккама | Принцип, согласно которому среди конкурирующих объяснений предпочтительнее то, что содержит меньше ненужных допущений. |
| Гарантия Доберта | Набор требований к аудируемости, гарантирующих, что судебные методы проверяемы, явны и воспроизводимы. |
| Детерминированный | Система, в которой идентичные входы всегда дают идентичные выходы; не используется случайность или плавающая точка. |
| Целочисленная арифметика | Математические операции только с целыми числами, без дробных или десятичных представлений. |

**Научное примечание**

【Scientific Note】
Терминология, заимствованная у Пирса, Эко или Грайса, **не** является мистицизмом или литературной критикой. В этом движке эти термины работают точно так же, как компоненты сенсорной матрицы. **Первичность** — это необработанное напряжение с детектора; **Вторичность** — корреляция между срабатываниями двух детекторов; **Третичность** — откалиброванный физический закон, предсказывающий оба. Рассмотрение абдуктивного вывода как сенсорного конвейера делает процесс аудируемым, детерминированным и полностью свободным от эзотерической интерпретации.

---

## 中文

**这是什么模块？**

本模块是 VIGÍA 系统的溯因推理引擎。它如同一台数字取证显微镜，接收原始证据取证工件（日志条目、哈希值、文件碎片等）构成的链条，并反向推理，以提出最可能的攻击者习惯或意图。该引擎并非凭空猜测，而是依据奥卡姆剃刀原则，通过确定性评分规则对相互竞争的解释性假设进行比较：所需未观测假设最少的解释胜出。所有计算均采用整数运算，确保证据相同则结论必然相同。

**关键概念表**

| 概念 | 在取证分析中的角色 | 科学类比 |
|---|---|---|
| Artifact（取证工件） | 原始数字证据片段（如日志条目、哈希、文件碎片）。在皮尔斯术语中，属于*第一性*的实例：尚未被解释的纯数据。 | 校准前的传感器原始电压读数 |
| AbductiveHypothesis（溯因假设） | 对*第三性*的候选解释：一个被提出的规律或习惯，能够产生已观测的取证工件。 | 预测物理过程如何产生传感器读数的理论模型 |
| 奥卡姆成本（Ockham Cost） | 某一假设所需未观测假设的整数计数。越低越好。 | 模型中超出实测数据的自由参数个数 |
| 覆盖率（Coverage） | 假设所能解释的已观测取证工件的整数百分比（0–100）。 | 模型所解释的数据点比例，以整数表示 |
| AbductiveResult（溯因结果） | 最终输出：一个获胜假设，以及按奥卡姆成本和覆盖率严格排序的备选假设。 | 拟合程序得到的候选模型排序列表 |
| infer_habit() | 核心流程：加载候选模板，依据证据链为每个模板评分，并返回确定性的最优匹配。 | 自动测量协议，用于选定最佳模型 |

**术语表**

| 术语 | 定义 |
|---|---|
| 溯因（Abduction） | 从观测结果推断最佳解释的逻辑操作（皮尔斯）。 |
| 第一性（Primeridad/Firstness） | 原始、未被解释的数据之存在方式。 |
| 第二性（Segundidad/Secondness） | 数据点之间的事实关联或相关性的存在方式。 |
| 第三性（Terceridad/Thirdness） | 解释模式的规律、习惯或一般规则之存在方式。 |
| 奥卡姆剃刀 | 在相互竞争的解释中，所需不必要假设最少的解释更可取。 |
| 道伯特保证（Daubert Guarantee） | 一组可审计性要求，确保取证方法可检验、明确且可复现。 |
| 确定性（Deterministic） | 相同输入始终产生相同输出的系统；不使用随机性或浮点近似。 |
| 整数运算 | 仅使用整数的数学运算，避免分数或小数表示。 |

**科学说明**

【科学说明】
从皮尔斯、艾柯或格赖斯借用的术语**并非**神秘主义或文学批评。在本引擎中，这些术语的功能完全等同于传感器阵列的组成部分。**第一性**是检测器输出的原始电压；**第二性**是两个检测器触发之间的关联；**第三性**是预测前两者的经校准物理定律。将溯因推理视为传感器管道，使整个过程具备可审计性、确定性，并且完全不包含玄奥解释。

---

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
