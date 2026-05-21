<!--
VIGIA Academic Documentation
Module: bc9b406c
Batch ID: vigia-doc-0021-bc9b406c
Generated: 2026-05-20T14:56:47.849214+00:00
-->

**ENGLISH**  
**Case Execution Controller** (`scripts/run_case.py`). A deterministic support module within the VIGIA forensic framework. It initializes a single investigative case, enforces sequential processing of evidence objects, and records execution metadata. Designed for reproducible forensic pipelines. *Scientific note:* Discrete logic and integer indexing guarantee bitwise reproducibility across independent executions.

**ESPAÑOL**  
**Controlador de Ejecución de Caso** (`scripts/run_case.py`). Módulo de soporte determinista del marco forense VIGIA. Inicializa un caso de investigación, impone el procesamiento secuencial de objetos de evidencia y registra metadatos de ejecución. Diseñado para flujos de trabajo forenses reproducibles.

**РУССКИЙ**  
**Контроллер выполнения дела** (`scripts/run_case.py`). Детерминированный вспомогательный модуль цифровой судебной системы VIGIA. Инициирует одно расследование, обеспечивает последовательную обработку объектов доказательств и фиксирует метаданные выполнения. Предназначен для воспроизводимых судебных потоков обработки.

**中文**  
**案件执行控制器**（`scripts/run_case.py`）。VIGIA数字取证框架中的确定性支持模块，用于初始化单一调查案件、顺序处理证据对象并记录执行元数据，确保取证流程可复现。

---

**Glossary / Glosario / Глоссарий / 词汇表**

1. **Algorithmic uncertainty** — Output variability caused by non-deterministic computational steps; variabilidad de salida por pasos computacionales no deterministas; неопределённость, вызванная недетерминированными вычислениями; 非确定性计算导致的输出变异.
2. **Case initialization** — Structured provisioning of parameters and resources for one investigation; aprovisionamiento estructurado para una investigación; структурированное выделение ресурсов расследования; 为单一调查结构化配置参数与资源.
3. **Deterministic system** — A process where identical inputs invariably produce identical outputs; proceso donde entradas idénticas producen salidas idénticas; система, при одинаковых входных данных дающая одинаковый результат; 相同输入始终产生相同输出的过程.
4. **Evidence object** — A discrete digital artifact subjected to forensic analysis; artefacto digital discreto sometido a análisis forense; дискретный цифровой артефакт, подлежащий экспертизе; 接受取证分析的离散数字工件.
5. **Execution metadata** — Runtime records documenting sequence, timestamp, and module state; registros de secuencia, marca temporal y estado; метаданные выполнения, фиксирующие последовательность и состояние; 记录序列、时间戳与模块状态的运行数据.
6. **Forensic framework** — An integrated software environment for digital evidence examination; entorno software integrado para examen de evidencia digital; интегрированная программная среда для цифровых расследований; 用于数字证据检验的集成软件环境.
7. **Investigative case** — A bounded unit of inquiry within a digital forensic workflow; unidad delimitada de investigación forense digital; ограниченная единица судебно-цифрового исследования; 数字取证工作流中的限定调查单元.
8. **Reproducible pipeline** — An analytical workflow yielding consistent results across repeated runs; flujo analítico con resultados consistentes en repeticiones; воспроизводимый аналитический конвейер с повторяемыми результатами; 重复运行产生一致结果的分析序列.
9. **Sequential processing** — Ordered, non-concurrent handling of data items; manejo ordenado y no concurrente de datos; последовательная, непараллельная обработка данных; 有序且非并发的数据处理方式.
10. **Support module** — An ancillary software component facilitating core system tasks; componente auxiliar que facilita tareas principales; вспомогательный компонент, обеспечивающий работу основной системы; 协助核心系统任务的辅助组件.
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
