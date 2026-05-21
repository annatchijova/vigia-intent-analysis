<!--
VIGIA Academic Documentation
Module: 2ddb875b
Batch ID: vigia-doc-0118-2ddb875b
Generated: 2026-05-20T14:56:47.870093+00:00
-->

**ENGLISH**  
The `ci_gate.py` module implements a deterministic acceptance gate for the VIGIA forensic pipeline. It conducts an exact comparison between candidate build artifacts and a certified reference baseline. The gate rejects any commit that degrades analytical accuracy or permits Mutual Information (MI) drift to exceed the rigid rational threshold of 1/100. Designed as a zero-tolerance SANS deliverable, it enforces non-negotiable regression boundaries to ensure evidentiary reproducibility across releases.

**ESPAÑOL**  
El módulo `ci_gate.py` constituye una compuerta determinista de aceptación para el pipeline forense VIGIA. Realiza una comparación exacta entre los artefactos de compilación candidatos y una línea base certificada. Rechaza cualquier *commit* que degrade la precisión analítica o permita una deriva de Información Mutua (MI) superior al umbral racional estricto de 1/100. Como entregable SANS de tolerancia cero, impone límites de regresión innegociables para garantizar la reproducibilidad probatoria entre versiones.

**РУССКИЙ**  
Модуль `ci_gate.py` реализует детерминированный приёмочный шлюз для судебного конвейера VIGIA. Выполняется точное сравнение артефактов кандидата с сертифицированной базовой линией. Шлюз отклоняет любую версию, снижающую аналитическую точность или допускающую дрейф взаимной информации (MI) сверх жёсткой рациональной границы 1/100. Как результат SANS с нулевой терпимостью, модуль устанавливает безусловные регрессионные пороги, обеспечивая доказательственную воспроизводимость.

**中文**  
`ci_gate.py` 模块为 VIGIA 取证流水线实施确定性准入闸门。该模块对候选构建产物与经认证的参考基线进行精确比对。若分析精度退化，或互信息（MI）漂移超出严格的有理分数阈值 1/100，则拒绝提交。作为 SANS 零容差交付物，该模块强制执行不可协商的回归边界，以确保证据级跨版本可复现性。

**Scientific Note**  
The drift limit is codified as the exact rational constant 1/100 and assessed by deterministic symbolic comparison, excluding any numerical approximation.

**Glossary**

- **Baseline / Línea base / Базовая линия / 基线**: Certified reference output for deterministic comparison.
- **CI Gate / Compuerta CI / CI-шлюз / CI 闸门**: Automated checkpoint that accepts or rejects software changes.
- **Deterministic / Determinista / Детерминированный / 确定性**: Producing identical outcomes under identical conditions.
- **MI Drift / Deriva MI / Дрейф ВИ / 互信息漂移**: Deviation in Mutual Information between releases.
- **Non-negotiable / Innegociable / Безусловный / 不可协商**: Absolute threshold admitting no exceptions.
- **Pipeline / Canalización / Конвейер / 流水线**: End-to-end analytical processing sequence.
- **Rational threshold / Umbral racional / Рациональная граница / 有理分数阈值**: Exact fractional limit expressed as a ratio of integers.
- **Regression / Regresión / Регресс / 回归**: Performance degradation relative to a prior version.
- **SANS Deliverable / Entregable SANS / Результат SANS / SANS 交付物**: Artifact meeting SANS Institute forensic standards.
- **Zero tolerance / Tolerancia cero / Нулевая терпимость / 零容差**: Policy rejecting any measurable deviation.
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
