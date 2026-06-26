<!--
VIGIA Academic Documentation
Module: cda1c372
Batch ID: vigia-doc-0124-cda1c372
Generated: 2026-05-20T14:56:47.871197+00:00
-->

---

## ENGLISH

### What Is This Module?
This module is a structural damage classifier for adversarial-negation stress-test reports. It synthesizes a severity index from the absolute change in model confidence and a binary verdict-shift indicator. Weighted linear composition produces a deterministic impact score, isolating the five most critical semantic regressions. Output prioritizes linguistic patterns that degrade classifier integrity under controlled adversarial stress. All scoring uses exact integer and rational arithmetic; no probabilistic thresholds are applied.

### Key Concepts

| Concept | Definition | Technical Role |
|---|---|---|
| **Adversarial Negation** | A controlled linguistic inversion designed to force classifier misclassification. | The stress stimulus; applied to probe the fragility of existing verdicts. |
| **Severity Index** | An exact composite score synthesized from confidence delta and verdict-shift indicator. | Ranks regressions from most to least damaging; top five are reported. |
| **Model Confidence Delta** | The absolute change in a classifier's certainty score between the nominal and negated inputs. | Quantifies the magnitude of destabilization caused by adversarial input. |
| **Binary Verdict Shift** | A two-value (0 or 1) indicator of whether the classifier's output category changed. | Captures categorical reversal as an exact integer flag. |
| **Semantic Regression** | A performance degradation on meaning-based classification tasks under adversarial conditions. | The primary output of the stress test; the module ranks and reports the top five. |
| **Deterministic Triage** | Reproducible prioritization of regressions without stochastic variance. | Guarantees that identical stress-test inputs always yield the same ranked list of regressions. |

> **【Scientific Note】**
> Peirce/Eco/Grice terminology is NOT mysticism. In VIGÍA, adversarial negation is a direct probe of Peircean *Thirdness*: it tests whether the interpretive law (the classifier's decision rule) remains stable under adversarial semantic perturbation. Eco's principle of code robustness demands that an interpretive system not be destabilized by surface-level linguistic inversions. Grice's maxim of quality is violated when a classifier shifts its verdict based on negation alone, without a corresponding change in the underlying evidential facts.

### Glossary
1. **Adversarial Negation** — A linguistic inversion designed to force classifier error through semantic destabilization.
2. **Binary Verdict Shift** — An exact two-value (0 or 1) indicator of categorical output reversal.
3. **Classifier Integrity** — The consistency of a model's decisions under controlled adversarial stress.
4. **Deterministic Triage** — Reproducible prioritization without stochastic variance; identical inputs yield identical ranked outputs.
5. **Impact Score** — A composite severity metric combining confidence delta and verdict shift for regression ranking.
6. **Model Confidence Delta** — The absolute deviation in predictive certainty between nominal and adversarially negated inputs.
7. **Negation Stress Test** — The diagnostic procedure applying adversarial negation to probe classifier fragility.
8. **Semantic Regression** — Performance degradation on meaning-based classification tasks under adversarial conditions.
9. **Severity Index** — The exact composite score ranking structural damage from adversarial-negation events.
10. **Weighted Linear Composition** — Aggregation of component scores using fixed integer-ratio coefficients, producing an exact rational result.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## ESPAÑOL

### ¿Qué es este módulo?
Este módulo es un clasificador de daños estructurales para reportes de prueba de estrés por negación adversaria. Sintetiza un índice de severidad a partir de la variación absoluta de confianza del modelo y un indicador binario de cambio de veredicto. La composición lineal ponderada genera una puntuación de impacto determinista, aislando las cinco regresiones semánticas más críticas. La salida prioriza patrones lingüísticos que degradan la integridad del clasificador bajo estrés adversario controlado. Toda la puntuación usa aritmética entera y racional exacta; no se aplican umbrales probabilísticos.

### Conceptos clave

| Concepto | Definición | Rol técnico |
|---|---|---|
| **Negación Adversaria** | Inversión lingüística controlada diseñada para forzar errores de clasificación. | El estímulo de estrés; aplicado para sondear la fragilidad de los veredictos existentes. |
| **Índice de Severidad** | Puntuación compuesta exacta sintetizada a partir del delta de confianza y el indicador de cambio de veredicto. | Clasifica las regresiones de más a menos dañinas; se reportan las cinco principales. |
| **Delta de Confianza del Modelo** | Cambio absoluto en la certeza del clasificador entre las entradas nominal y negada. | Cuantifica la magnitud de desestabilización causada por la entrada adversaria. |
| **Cambio Binario de Veredicto** | Indicador de dos valores (0 o 1) de si la categoría de salida del clasificador cambió. | Captura la inversión categórica como un indicador entero exacto. |
| **Regresión Semántica** | Degradación del rendimiento en tareas de clasificación basadas en significado bajo condiciones adversarias. | La salida primaria de la prueba de estrés; el módulo clasifica y reporta las cinco principales. |
| **Triaje Determinista** | Priorización reproducible de regresiones sin varianza estocástica. | Garantiza que entradas de prueba de estrés idénticas siempre producen la misma lista clasificada. |

> **【Nota Científica】**
> La terminología de Peirce/Eco/Grice no es misticismo. En VIGÍA, la negación adversaria es una sonda directa de la *Terceridad* peirceana: prueba si la ley interpretativa (la regla de decisión del clasificador) permanece estable bajo perturbación semántica adversaria. El principio de robustez de código de Eco exige que un sistema interpretativo no sea desestabilizado por inversiones lingüísticas superficiales. La máxima de calidad de Grice se viola cuando un clasificador cambia su veredicto basándose únicamente en la negación, sin un cambio correspondiente en los hechos probatorios subyacentes.

### Glosario
1. **Negación Adversaria** — Inversión lingüística diseñada para forzar errores del clasificador mediante desestabilización semántica.
2. **Cambio Binario de Veredicto** — Indicador exacto de dos valores (0 o 1) de inversión categórica de la salida.
3. **Integridad del Clasificador** — Consistencia de las decisiones de un modelo bajo estrés adversario controlado.
4. **Triaje Determinista** — Priorización reproducible sin varianza estocástica; entradas idénticas producen salidas clasificadas idénticas.
5. **Puntuación de Impacto** — Métrica de severidad compuesta que combina delta de confianza y cambio de veredicto para clasificación de regresiones.
6. **Delta de Confianza del Modelo** — La desviación absoluta en la certeza predictiva entre entradas nominales y adversariamente negadas.
7. **Prueba de Estrés por Negación** — El procedimiento diagnóstico que aplica negación adversaria para sondear la fragilidad del clasificador.
8. **Regresión Semántica** — Degradación del rendimiento en tareas de clasificación basadas en significado bajo condiciones adversarias.
9. **Índice de Severidad** — La puntuación compuesta exacta que clasifica el daño estructural de los eventos de negación adversaria.
10. **Composición Lineal Ponderada** — Agregación de puntuaciones componentes usando coeficientes de razón entera fijos, produciendo un resultado racional exacto.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## РУССКИЙ

### Что это за модуль?
Данный модуль является классификатором структурных повреждений для отчётов стресс-тестирования адверсариальным отрицанием. Он синтезирует индекс тяжести из абсолютного изменения уверенности модели и бинарного индикатора сдвига вердикта. Взвешенная линейная композиция формирует детерминированную оценку воздействия, выделяя пять наиболее критических семантических регрессий. Выходные данные ранжируют языковые паттерны, разрушающие целостность классификатора при контролируемом адверсариальном стрессе. Всё оценивание использует точную целочисленную и рациональную арифметику; вероятностные пороги не применяются.

### Ключевые концепции

| Концепция | Определение | Техническая роль |
|---|---|---|
| **Адверсариальное отрицание** | Контролируемая лингвистическая инверсия, предназначенная для принудительной ошибки классификации. | Стрессовый стимул; применяется для зондирования хрупкости существующих вердиктов. |
| **Индекс тяжести** | Точная составная оценка, синтезированная из дельты уверенности и индикатора сдвига вердикта. | Ранжирует регрессии от наиболее до наименее разрушительных; сообщаются пять наиболее важных. |
| **Дельта уверенности модели** | Абсолютное изменение степени уверенности классификатора между номинальными и отрицательными входными данными. | Количественно оценивает масштаб дестабилизации, вызванной адверсариальным вводом. |
| **Бинарный сдвиг вердикта** | Двузначный (0 или 1) индикатор изменения выходной категории классификатора. | Фиксирует категориальную инверсию как точный целочисленный флаг. |
| **Семантическая регрессия** | Снижение производительности на задачах классификации, основанных на значении, в адверсариальных условиях. | Основной результат стресс-теста; модуль ранжирует и сообщает пять наиболее важных. |
| **Детерминированный триаж** | Воспроизводимая приоритизация регрессий без стохастической дисперсии. | Гарантирует, что идентичные входные данные стресс-теста всегда дают одинаковый ранжированный список регрессий. |

> **【Научное примечание】**
> Терминология Пирса, Эко и Грайса — не мистика. В VIGÍA адверсариальное отрицание является прямым зондированием пирсовской *Третичности*: оно проверяет, остаётся ли интерпретационный закон (правило решения классификатора) стабильным при адверсариальном семантическом возмущении. Принцип кодовой устойчивости Эко требует, чтобы интерпретационная система не дестабилизировалась поверхностными лингвистическими инверсиями. Максима качества Грайса нарушается, когда классификатор меняет вердикт только на основании отрицания, без соответствующего изменения базовых доказательных фактов.

### Глоссарий
1. **Адверсариальное отрицание** — Лингвистическая инверсия, предназначенная для принудительной ошибки классификатора через семантическую дестабилизацию.
2. **Бинарный сдвиг вердикта** — Точный двузначный (0 или 1) индикатор категориальной инверсии выхода.
3. **Целостность классификатора** — Согласованность решений модели при контролируемом адверсариальном стрессе.
4. **Детерминированный триаж** — Воспроизводимая приоритизация без стохастической дисперсии; идентичные входные данные дают идентичные ранжированные выходные.
5. **Оценка воздействия** — Составная метрика тяжести, сочетающая дельту уверенности и сдвиг вердикта для ранжирования регрессий.
6. **Дельта уверенности модели** — Абсолютное отклонение прогностической уверенности между номинальными и адверсариально отрицаемыми входными данными.
7. **Стресс-тест отрицания** — Диагностическая процедура, применяющая адверсариальное отрицание для зондирования хрупкости классификатора.
8. **Семантическая регрессия** — Снижение производительности на задачах классификации, основанных на значении, в адверсариальных условиях.
9. **Индекс тяжести** — Точная составная оценка, ранжирующая структурный ущерб от событий адверсариального отрицания.
10. **Взвешенная линейная композиция** — Агрегация компонентных оценок с использованием фиксированных коэффициентов целочисленного отношения, дающая точный рациональный результат.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## 中文

### 这是什么模块？
本模块是对抗性否定压力测试报告的结构性损伤分类器。它通过将模型置信度的绝对变化与裁决偏移的二元标志进行加权线性组合，合成严重性指数，产生确定性影响评分，从而对五个最严重的语义回归进行确定性分级，优先识别在对抗性否定条件下破坏分类器完整性的语言模式。所有评分使用精确整数与有理数运算；不应用概率阈值。

### 关键概念

| 概念 | 定义 | 技术作用 |
|---|---|---|
| **对抗性否定** | 旨在强制分类器误分类的受控语言反转。 | 压力刺激；用于探测现有裁决的脆弱性。 |
| **严重性指数** | 由置信度变化量和裁决偏移指标合成的精确综合评分。 | 将回归从最有害到最无害排序；报告前五名。 |
| **模型置信度变化量** | 分类器在名义输入和否定输入之间确定性得分的绝对变化。 | 量化对抗性输入造成的去稳定化程度。 |
| **裁决二元偏移** | 分类器输出类别是否发生变化的双值（0 或 1）指示器。 | 将分类反转捕获为精确整数标志。 |
| **语义回归** | 在对抗性条件下基于意义的分类任务中的性能退化。 | 压力测试的主要输出；模块对前五名进行排名和报告。 |
| **确定性分级** | 无随机方差的可复现回归优先级排序。 | 保证相同的压力测试输入始终产生相同的排名回归列表。 |

> **【科学说明】**
> 皮尔斯、艾柯和格赖斯的术语并非神秘主义。在 VIGÍA 中，对抗性否定是对皮尔斯*第三性*的直接探测：它测试解释规律（分类器的决策规则）在对抗性语义扰动下是否保持稳定。艾柯的代码稳健性原则要求解释系统不被表面的语言反转所动摇。当分类器仅基于否定改变其裁决——而底层证据事实没有相应变化——时，格赖斯的质量准则即遭到违反。

### 词汇表
1. **对抗性否定** — 旨在通过语义去稳定化强制分类器出错的语言反转。
2. **裁决二元偏移** — 输出分类反转的精确双值（0 或 1）指示器。
3. **分类器完整性** — 模型在受控对抗性压力下决策的一致性。
4. **确定性分级** — 无随机方差的可复现优先级排序；相同输入产生相同排名输出。
5. **影响评分** — 结合置信度变化量和裁决偏移的综合严重性指标，用于回归排名。
6. **模型置信度变化量** — 名义输入与对抗性否定输入之间预测确定性的绝对偏差。
7. **否定压力测试** — 应用对抗性否定以探测分类器脆弱性的诊断程序。
8. **语义回归** — 在对抗性条件下基于意义的分类任务中的性能退化。
9. **严重性指数** — 对对抗性否定事件的结构性损伤进行排名的精确综合评分。
10. **加权线性组合** — 使用固定整数比系数聚合组件评分，产生精确有理数结果。

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
