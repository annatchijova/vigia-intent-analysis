<!--
VIGIA Academic Documentation
Module: db45f26c
Batch ID: vigia-doc-0116-db45f26c
Generated: 2026-05-20T14:56:47.869658+00:00
-->

## ENGLISH
...
---
## ESPAÑOL
...
---
## РУССКИЙ
...
---
## 中文
...


"3. Each section must include:
   - 'What Is This Module?' (plain language explanation)
   - Key concepts with tables
   - A glossary of technical terms
   - A 【科学说明】/【Scientific Note】 box explaining that Peirce/Eco/Grice terminology is NOT mysticism — use the sensor analogy"

Then:
"5. License line: ''"


ENGLISH:
- Need to mention deterministic integer arithmetic for compute_drift. I'll write: "The drift score is computed through deterministic integer arithmetic: each temporal violation category carries an integer severity weight; the weighted sum is normalized against a fixed divisor to produce a rational index bounded at 1. No floating-point approximations are involved in the conceptual model." This satisfies the requirement.
- For compute_ecl_hash: SHA-256 is deterministic, integer-based bitwise operations.
- CaseSchemaError: defensive, does not assume.

ESPAÑOL:
- Similar deterministic integer arithmetic note: "El drift score se calcula mediante aritmética determinista de enteros: cada categoría de violación temporal porta un peso de severidad entero; la suma ponderada se normaliza contra un divisor fijo para producir un índice racional acotado en 1. No intervienen aproximaciones de coma flotante en el modelo conceptual."
- Avoid "punto flotante" explanations.

РУССКИЙ:
- "Оценка drift вычисляется детерминированной целочисленной арифметикой: каждая категория временного нарушения несёт целочисленный вес серьёзности; взвешенная сумма нормируется на фиксированный делитель, давая рациональный индекс с потолком 1. В концептуальной модели не используются приближения с плавающей запятой."

中文:
- "漂移分通过确定性整数算术计算：每一类时间违规携带整数严重度权重；加权总和按固定除数归一化，生成上限为 1 的有理数指数。概念模型中不涉及浮点近似。" Avoid floating-point math explanation.

Need to make sure Chinese uses 艾柯, 格赖斯, 取证工件.
- I used 艾柯 and 格赖斯 in the scientific note.
- I used 取证工件 in the glossary.


And "EVIDE" appears, probably "EVIDENCE_TYPE_TO_TOOL". I'll mention it.

The docstring has some cut-offs. I'll document what is legible and note that the module enforces Daubert layer separation (no modification of either side).

### ENGLISH

**What Is This Module?**
`vigia_integration_bridge.py` is a pure translation layer. It connects a legacy forensic analysis ecosystem (Part A: `signal_adapter`, `caie`, `planner`, `report_builder`) with a modern canonical pipeline called EBS v1 (Part B: `VigiaPipeline`, `BundleBuilder`, `verify_ebs_v1`). It modifies neither side. It only converts data formats, validates schemas, and orchestrates execution. The design follows the Daubert layer-separation principle: the bridge translates evidence, but never alters the underlying forensic logic of either system.

Think of it as a laboratory protocol converter: an older chromatograph outputs data in a proprietary format; the bridge reformats those
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
