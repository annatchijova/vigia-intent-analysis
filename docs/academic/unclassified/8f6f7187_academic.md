<!--
VIGIA Academic Documentation
Module: 8f6f7187
Batch ID: vigia-doc-0030-8f6f7187
Generated: 2026-05-20T14:56:47.851087+00:00
-->

---

## ENGLISH

### What Is This Module?

This module is the **Virtual Layer of Inverse Probabilistic Abduction** inside the VIGÍA Forensic Suite. Its scientific purpose is strictly methodological: once an investigation has produced a winning hypothesis **H\***, the module systematically asks, *"What would have to change in the evidence for a discarded alternative hypothesis to become more plausible than H\*?"* This is a controlled stress-test of the winning explanation — analogous to a structural engineer applying counter-loads to a bridge to locate hidden weaknesses before signing off on the design.

The module operates entirely on **deterministic integer arithmetic**: every threshold, every score, and every comparison uses exact integer or rational values. No stochastic sampling, no probabilistic thresholds, and no approximations are permitted. This ensures that any analyst, on any machine, running the same evidence set will arrive at the exact same stress-test result.

### Key Concepts

| Concept | Plain-Language Description | Scientific Role |
|---|---|---|
| **Inverse Abduction** | The process of asking what evidence would need to change to overturn the winning hypothesis. | Implements Eco's principle that no sign is self-evidently univocal — alternative readings must be systematically tested. |
| **Abduction Stress Score** | An exact integer metric quantifying how much the evidence would have to shift to make an alternative hypothesis competitive. | Provides a deterministic measure of the winning hypothesis's robustness. |
| **Hypothesis Inversion** | Constructing the logical negation of H\* and evaluating it against the same evidence set. | Prevents confirmation bias by forcing consideration of the opposite conclusion. |
| **Threshold Sensitivity** | Analysis of how small a change in evidence weight causes a verdict reversal. | Identifies which pieces of evidence are load-bearing and which are redundant. |
| **Deterministic Integer Arithmetic** | All scoring uses exact integer or rational values. | Guarantees reproducibility across platforms and audit sessions. |

### Core Operations

| Operation | Purpose |
|---|---|
| `invert()` | Accepts the winning hypothesis and evidence set, constructs the logical inverse, and returns an inversion record. |
| `stress_test()` | Runs the full inverse abduction protocol and computes the abduction stress score. |
| `identify_load_bearing()` | Returns the subset of evidence items whose removal would reverse the verdict. |

### Glossary
1. **Abductive Stress Score** — An exact integer quantifying the evidential distance between the winning hypothesis and the nearest alternative.
2. **Confirmation Bias** — The cognitive tendency to seek evidence supporting an already-held conclusion, which this module counteracts.
3. **Deterministic Integer Arithmetic** — Computation using only exact integer and rational values; no approximations.
4. **Hypothesis Inversion** — The logical negation of the winning hypothesis, constructed to test its fragility.
5. **Inverse Abduction** — Systematic inquiry into what evidence changes would overturn the accepted conclusion.
6. **Load-Bearing Evidence** — An artifact whose removal or reweighting alone would cause a verdict reversal.
7. **Threshold Sensitivity** — The minimum change in evidence weight that triggers a verdict change.
8. **Winning Hypothesis (H\*)** — The hypothesis selected by the primary abductive engine as the best explanation of the evidence.
9. **Verdict Reversal** — The condition in which a sufficient change in evidence causes the CDL to switch from one verdict to another.
10. **Robustness** — The property of a conclusion that resists overturning under adversarial evidence perturbations.

> **【Scientific Note】**
> Peirce/Eco/Grice terminology is NOT mysticism. Inverse abduction is a direct application of Eco's warning against unlimited semiosis: the fact that a sign *can* be interpreted one way does not mean it cannot be interpreted another. The stress-test operationalizes this warning as a deterministic algorithm. Grice's maxim of quality demands that analysts not assert conclusions they could not defend under adversarial questioning — this module enforces that standard computationally.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## ESPAÑOL

### ¿Qué es este módulo?

Este módulo es la **Capa Virtual de Abducción Probabilística Inversa** dentro de la Suite Forense VIGÍA. Su propósito científico es estrictamente metodológico: una vez que una investigación ha producido una hipótesis ganadora **H\***, el módulo pregunta sistemáticamente: *"¿Qué tendría que cambiar en la evidencia para que una hipótesis alternativa descartada fuera más plausible que H\*?"* Esta es una prueba de estrés controlada de la explicación ganadora — análoga a un ingeniero estructural que aplica cargas contrarias a un puente para localizar debilidades ocultas antes de firmar el diseño.

El módulo opera enteramente con **aritmética entera determinista**: cada umbral, cada puntuación y cada comparación utiliza valores enteros o racionales exactos. No se permiten muestreos estocásticos, umbrales probabilísticos ni aproximaciones.

### Conceptos clave

| Concepto | Descripción | Rol científico |
|---|---|---|
| **Abducción Inversa** | Proceso de preguntar qué evidencia necesitaría cambiar para anular la hipótesis ganadora. | Implementa el principio de Eco de que ningún signo es unívoco por sí mismo. |
| **Puntuación de Estrés Abductivo** | Métrica entera exacta que cuantifica cuánto tendría que cambiar la evidencia para hacer competitiva una hipótesis alternativa. | Proporciona una medida determinista de la robustez de la hipótesis ganadora. |
| **Inversión de Hipótesis** | Construcción de la negación lógica de H\* y su evaluación frente al mismo conjunto de evidencia. | Previene el sesgo de confirmación al forzar la consideración de la conclusión opuesta. |
| **Sensibilidad de Umbral** | Análisis de qué tan pequeño debe ser el cambio en el peso de la evidencia para causar una inversión del veredicto. | Identifica qué piezas de evidencia son sustentadoras y cuáles son redundantes. |
| **Aritmética Entera Determinista** | Toda la puntuación usa valores enteros o racionales exactos. | Garantiza reproducibilidad entre plataformas y sesiones de auditoría. |

### Glosario
1. **Puntuación de Estrés Abductivo** — Entero exacto que cuantifica la distancia probatoria entre la hipótesis ganadora y la alternativa más cercana.
2. **Sesgo de Confirmación** — Tendencia cognitiva a buscar evidencia que apoye una conclusión ya sostenida; este módulo la contrarresta.
3. **Aritmética Entera Determinista** — Cómputo usando solo valores enteros y racionales exactos; sin aproximaciones.
4. **Inversión de Hipótesis** — Negación lógica de la hipótesis ganadora, construida para probar su fragilidad.
5. **Abducción Inversa** — Investigación sistemática sobre qué cambios en la evidencia anularían la conclusión aceptada.
6. **Evidencia Sustentadora** — Artefacto cuya eliminación o reponderación sola causaría una inversión del veredicto.
7. **Sensibilidad de Umbral** — El cambio mínimo en el peso de la evidencia que desencadena un cambio de veredicto.
8. **Hipótesis Ganadora (H\*)** — La hipótesis seleccionada por el motor abductivo primario como la mejor explicación de la evidencia.
9. **Inversión de Veredicto** — Condición en que un cambio suficiente en la evidencia hace que la CDL cambie de un veredicto a otro.
10. **Robustez** — Propiedad de una conclusión que resiste ser anulada bajo perturbaciones adversariales de la evidencia.

> **【Nota Científica】**
> La terminología de Peirce/Eco/Grice no es misticismo. La abducción inversa es una aplicación directa de la advertencia de Eco contra la semiosis ilimitada: el hecho de que un signo *pueda* interpretarse de una manera no significa que no pueda interpretarse de otra. La prueba de estrés operacionaliza esta advertencia como un algoritmo determinista. La máxima de calidad de Grice exige que los analistas no afirmen conclusiones que no podrían defender bajo interrogatorio adversarial — este módulo impone ese estándar computacionalmente.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## РУССКИЙ

### Что это за модуль?

Данный модуль представляет собой **Виртуальный слой инверсной вероятностной абдукции** в составе Криминалистического комплекса VIGÍA. Его научная задача строго методологическая: после того как расследование выдало победившую гипотезу **H\***, модуль систематически задаёт вопрос: *«Что должно было бы измениться в доказательствах, чтобы отброшенная альтернативная гипотеза стала более правдоподобной, чем H\*?»* Это контролируемый стресс-тест победившего объяснения — аналог того, как инженер-строитель прикладывает противонагрузки к мосту, чтобы найти скрытые слабости перед подписанием проекта.

Модуль работает исключительно на **детерминированной целочисленной арифметике**: каждый порог, каждая оценка и каждое сравнение использует точные целочисленные или рациональные значения. Стохастическая выборка, вероятностные пороги и приближения не допускаются.

### Ключевые концепции

| Концепция | Описание | Научная роль |
|---|---|---|
| **Инверсная абдукция** | Процесс выяснения того, что именно в доказательствах должно измениться для опровержения победившей гипотезы. | Реализует принцип Эко о том, что ни один знак не является однозначным сам по себе. |
| **Абдуктивный стресс-балл** | Точная целочисленная метрика, количественно оценивающая, насколько должны измениться доказательства для конкурентоспособности альтернативной гипотезы. | Предоставляет детерминированную меру устойчивости победившей гипотезы. |
| **Инверсия гипотезы** | Построение логического отрицания H\* и его оценка на том же наборе доказательств. | Предотвращает предвзятость подтверждения, принуждая рассматривать противоположный вывод. |
| **Чувствительность к порогу** | Анализ того, насколько мало изменение веса доказательств необходимо для переворачивания вердикта. | Выявляет, какие доказательства несут нагрузку, а какие избыточны. |
| **Детерминированная целочисленная арифметика** | Вся оценка использует точные целочисленные или рациональные значения. | Гарантирует воспроизводимость на разных платформах и в сессиях аудита. |

### Глоссарий
1. **Абдуктивный стресс-балл** — Точное целое число, количественно оценивающее доказательное расстояние между победившей гипотезой и ближайшей альтернативой.
2. **Предвзятость подтверждения** — Когнитивная тенденция искать доказательства в поддержку уже принятого вывода; данный модуль противодействует ей.
3. **Детерминированная целочисленная арифметика** — Вычисления с использованием только точных целочисленных и рациональных значений.
4. **Инверсия гипотезы** — Логическое отрицание победившей гипотезы, построенное для проверки её хрупкости.
5. **Инверсная абдукция** — Систематическое исследование того, какие изменения в доказательствах опровергнут принятый вывод.
6. **Нагрузочное доказательство** — Артефакт, удаление или перевзвешивание которого одного приведёт к перевороту вердикта.
7. **Чувствительность к порогу** — Минимальное изменение веса доказательства, вызывающее смену вердикта.
8. **Победившая гипотеза (H\*)** — Гипотеза, выбранная первичным абдуктивным движком как наилучшее объяснение доказательств.
9. **Переворот вердикта** — Состояние, при котором достаточное изменение в доказательствах вызывает смену вердикта CDL.
10. **Устойчивость** — Свойство вывода, позволяющее ему противостоять опровержению при состязательных пертурбациях доказательств.

> **【Научное примечание】**
> Терминология Пирса, Эко и Грайса — не мистика. Инверсная абдукция является прямым применением предупреждения Эко против безграничного семиозиса: то, что знак *может* быть интерпретирован одним образом, не означает, что он не может быть интерпретирован иначе. Стресс-тест операционализирует это предупреждение как детерминированный алгоритм. Максима качества Грайса требует, чтобы аналитики не утверждали выводы, которые они не смогли бы отстоять при состязательном допросе.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## 中文

### 这是什么模块？

本模块是 VIGÍA 取证套件中的**逆向溯因概率虚拟层**。其科学目的严格属于方法论层面：一旦调查产生了获胜假说 **H\***，该模块就系统性地提问：*"证据中什么需要改变，才能使被否定的备选假说比 H\* 更合理？"* 这是对获胜解释的受控压力测试——类似于结构工程师在签署设计前对桥梁施加反向荷载以定位隐藏弱点。

该模块完全基于**确定性整数运算**运行：每个阈值、每个评分和每次比较均使用精确整数或有理数值。不允许随机采样、概率阈值或任何近似值。

### 关键概念

| 概念 | 通俗描述 | 科学作用 |
|---|---|---|
| **逆向溯因** | 询问证据中什么需要改变才能推翻获胜假说的过程。 | 实现艾柯的原则：没有任何符号本身就是单义的——必须系统地检验替代读法。 |
| **溯因压力评分** | 精确整数指标，量化证据需要移动多少才能使备选假说具有竞争力。 | 为获胜假说的稳健性提供确定性度量。 |
| **假说反转** | 构造 H\* 的逻辑否定并对同一证据集进行评估。 | 通过强制考虑相反结论来防止确认偏误。 |
| **阈值敏感性** | 分析证据权重变化多小会导致裁决逆转。 | 识别哪些证据是承重的，哪些是冗余的。 |
| **确定性整数运算** | 所有评分使用精确整数或有理数值。 | 保证跨平台和审计会话的可复现性。 |

### 词汇表
1. **溯因压力评分** — 量化获胜假说与最近备选假说之间证据距离的精确整数。
2. **确认偏误** — 倾向于寻求支持已持结论的证据的认知倾向；本模块对其进行反制。
3. **确定性整数运算** — 仅使用精确整数和有理数值的计算；无近似值。
4. **假说反转** — 获胜假说的逻辑否定，用于检验其脆弱性。
5. **逆向溯因** — 系统探究证据中什么变化会推翻已接受结论的调查。
6. **承重证据** — 单独删除或重新加权就会导致裁决逆转的工件。
7. **阈值敏感性** — 触发裁决变化的最小证据权重变化量。
8. **获胜假说（H\*）** — 主溯因引擎选定为证据最佳解释的假说。
9. **裁决逆转** — 证据充分变化导致 CDL 从一个裁决切换到另一个裁决的条件。
10. **稳健性** — 结论在对抗性证据扰动下抵御被推翻的属性。

> **【科学说明】**
> 皮尔斯、艾柯和格赖斯的术语并非神秘主义。逆向溯因是对艾柯关于无限符号义警告的直接应用：一个符号*可以*以某种方式解释，这一事实并不意味着它不能以另一种方式解释。压力测试将这一警告操作化为确定性算法。格赖斯的质量准则要求分析员不要断言他们在对抗性质询下无法捍卫的结论——本模块以计算方式强制执行该标准。

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
