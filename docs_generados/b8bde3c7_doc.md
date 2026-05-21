<!--
VIGIA Academic Documentation
Module: b8bde3c7
Batch ID: vigia-doc-0065-b8bde3c7
Generated: 2026-05-20T14:56:47.858475+00:00
-->

**ENGLISH**  
`negation_handler.py` is a deterministic lexical filter in the VIGÍA forensic pipeline. It scans a defined proximity window around pattern matches to detect negation lexemes, then applies a fixed attenuation factor to lower match confidence. Version 1.0 uses minimalist, predictable logic without machine learning or stochastic processes, ensuring fully reproducible evidence processing.

**ESPAÑOL**  
`negation_handler.py` es un filtro léxico determinista en la tubería forense VIGÍA. Examina una ventana de proximidad definida alrededor de coincidencias para detectar lexemas de negación, aplicando un factor fijo de atenuación que reduce la confianza del *match*. La versión 1.0 emplea lógica minimalista y predecible sin aprendizaje automático ni procesos estocásticos, garantizando un procesamiento de evidencias completamente reproducible.

**РУССКИЙ**  
`negation_handler.py` — детерминистский лексический фильтр в судебном конвейере VIGÍA. Он сканирует заданное окно близости вокруг совпадений по шаблону, выявляя лексемы отрицания, и применяет фиксированный коэффициент ослабления достоверности. Версия 1.0 использует минималистичную предсказуемую логику без машинного обучения и стохастических процессов, обеспечивая полностью воспроизводимую обработку доказательств.

**中文**  
`negation_handler.py` 是 VIGÍA 取证流程中的确定性词汇过滤器。它在限定邻近窗口内扫描模式匹配周边的否定词素，并施加固定衰减因子以降低匹配可信度。1.0 版采用极简、可预测的逻辑，不依赖机器学习或随机过程，确保证据处理的完全可复现性。

*Author / Autor / Автор / 作者:* Colectivo VIGÍA (DeepSeek ideation, ChatGPT critique, Kimi consolidation).

**Scientific Note**  
Deterministic lexical adjacency analysis guarantees identical outputs for identical inputs across independent forensic replications, satisfying admissibility criteria for scientific reliability.

---

**Glossary / Glosario / Глоссарий / 术语表**

1. **Attenuation factor** — Fixed multiplier reducing confidence. / *Factor de atenuación* / *Коэффициент ослабления* / 衰减因子
2. **Deterministic system** — Process fully defined by inputs, without randomness. / *Sistema determinista* / *Детерминистская система* / 确定性系统
3. **Forensic pipeline** — Modular architecture for digital evidence processing. / *Tubería forense* / *Судебный конвейер* / 取证流程
4. **Lexeme** — Minimal unit of lexical meaning. / *Lexema* / *Лексема* / 词素
5. **Machine learning** — Data-driven statistical training paradigm. / *Aprendizaje automático* / *Машинное обучение* / 机器学习
6. **Match confidence** — Quantified reliability of a detected pattern. / *Confianza del match* / *Достоверность совпадения* / 匹配可信度
7. **Negation lexeme** — Token expressing logical negation. / *Lexema de negación* / *Лексема отрицания* / 否定词素
8. **Proximity window** — Bounded textual scope around an anchor match. / *Ventana de proximidad* / *Окно близости* / 邻近窗口
9. **Reproducibility** — Ability to duplicate identical results. / *Reproducibilidad* / *Воспроизводимость* / 可复现性
10. **Stochastic process** — System with inherent random variability. / *Proceso estocástico* / *Стохастический процесс* / 随机过程
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
