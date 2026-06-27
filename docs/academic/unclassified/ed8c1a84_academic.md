<!--
VIGIA Academic Documentation
Module: ed8c1a84
Batch ID: vigia-doc-0192-ed8c1a84
Generated: 2026-05-20T14:56:47.886081+00:00
-->

## ENGLISH

`vigia_scorer.py` is a deterministic forensic scoring engine within the VIGÍA suite. It evaluates digital artifacts against structured intentionality criteria to produce reproducible integer severity rankings. Developed for the SANS FIND EVIL Hackathon 2026 and proposed for integration into the SANS SIFT Workstation, it is released under Apache 2.0. The module supports threat-hunting triage without probabilistic heuristics, ensuring identical inputs always yield identical outputs—an essential property for courtroom admissibility and peer review.

**Scientific Note.** Deterministic integer-based scoring eliminates stochastic variability, satisfying evidentiary reliability standards (e.g., Daubert) and ensuring platform-independent reproducibility.

## ESPAÑOL

`vigia_scorer.py` es un motor forense de puntuación determinista del conjunto VIGÍA. Evalúa artefactos digitales mediante criterios estructurados de intencionalidad para generar clasificaciones enteras reproducibles de severidad. Desarrollado para el SANS FIND EVIL Hackathon 2026 y propuesto para integrarse en la estación de trabajo SANS SIFT, se distribuye bajo licencia Apache 2.0. El módulo facilita el triaje de caza de amenazas sin heurísticas probabilísticas, garantizando que entradas idénticas produzcan salidas idénticas: propiedad esencial para la admisibilidad judicial y la revisión por pares.

**Nota científica.** La puntuación determinista basada en enteros elimina la variabilidad estocástica, satisfaciendo estándares de fiabilidad probatoria (p. ej., Daubert) y garantizando reproducibilidad independiente de la plataforma.

## РУССКИЙ

`vigia_scorer.py` — детерминированный форензический оценочный модуль комплекса VIGÍA. Он анализирует цифровые артефакты по структурированным критериям интенциональности и формирует воспроизводимые целочисленные ранги серьёзности. Разработан для хакатона SANS FIND EVIL 2026 и предложен для интеграции в рабочую станцию SANS SIFT; распространяется под лицензией Apache 2.0. Модуль обеспечивает триаж при охоте на угрозы без вероятностных эвристик, гарантируя, что одинаковые входные данные всегда дают одинаковый результат — ключевое свойство для судебного допуска и рецензирования.

**Научное примечание.** Детерминированное оценивание на основе целых чисел устраняет стохастическую изменчивость, удовлетворяя стандартам надёжности доказательств (напр., Daubert) и обеспечивая платформенно-независимую воспроизводимость.

## 中文

`vigia_scorer.py` 是 VIGÍA 套件中的确定性取证评分引擎。它依据结构化意图标准评估数字工件，生成可复现的整数严重等级。该模块为 2026 年 SANS FIND EVIL 黑客松开发，拟集成至 SANS SIFT 工作站，采用 Apache 2.0 许可。其无需概率启发即可支持威胁狩猎分流，确保相同输入始终产生相同输出——此乃法庭可采性与同行评审所需的核心属性。

**科学注.** 基于整数的确定性评分消除了随机变异，满足证据可靠性标准（如道伯特），并确保跨平台的可复现性。

## Glossary / Glosario / Глоссарий / 词汇表

1. **Digital artifact / Artefacto digital / Цифровой артефакт / 数字工件** — Discrete data object from storage media. / Objeto de datos discreto recuperado de almacenamiento. / Дискретный объект данных, извлечённый из носителя. / 从存储介质中恢复的离散数据对象。

2. **Deterministic system / Sistema determinista / Детерминированная система / 确定性系统** — Process yielding identical outputs from identical inputs. / Proceso que produce salidas idénticas de entradas idénticas. / Система, дающая одинаковый результат при одинаковых входных данных. / 相同输入始终产生相同输出的过程。

3. **Intentionality analysis / Análisis de intencionalidad / Анализ интенциональности / 意图分析** — Assessment of purposeful malicious indicators. / Evaluación de indicadores maliciosos deliberados. / Оценка признаков преднамеренных вредоносных действий. / 对蓄意恶意指标的评估。

4. **Threat-hunting triage / Triaje de caza de amenazas / Триаж охоты на угрозы / 威胁狩猎分流** — Prioritization of suspicious findings. / Priorización de hallazgos sospechosos. / Приоритизация подозрительных находок. / 对可疑发现的优先级排序。

5. **Forensic scoring / Puntuación forense / Форензическая оценка / 取证评分** — Standardized severity assignment to evidence. / Asignación estandarizada de severidad a la evidencia. / Стандартизированное присвоение степени серьёзности доказательствам. / 对证据进行标准化严重程度赋值。

6. **Severity ranking / Clasificación de severidad / Ранг серьёзности / 严重等级** — Ordinal ordering by investigative priority. / Ordenación ordinal por prioridad investigativa. / Порядковое ранжирование по приоритету расследования. / 按调查优先级排序的序数排名。

7. **Peer review / Revisión por pares / Рецензирование / 同行评审** — Independent scientific verification. / Verificación científica independiente. / Независимая научная проверка. / 独立科学验证。

8. **Courtroom admissibility / Admisibilidad judicial / Судебное допущение / 法庭可采性** — Legal qualification for judicial proceedings. / Calificación legal para procedimientos judiciales. / Правовое соответствие для судебных разбирательств. / 用于司法程序的法律资格认定。

9. **Structured criteria / Criterios estructurados / Структурированные критерии / 结构化标准** — Explicit, uniformly applied rules. / Reglas explícitas aplicadas uniformemente. / Явные, единообразно применяемые правила. / 明确且统一适用的规则。

10. **Bit-exact congruence / Congruencia bit-exacta / Битово-точное соответствие / 比特级一致性** — Perfect output identity across repeated runs. / Identidad perfecta de salida entre ejecuciones repetidas. / Точное побитовое совпадение результатов при повторных запусках. / 多次运行间输出的完美一致性。

---

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
