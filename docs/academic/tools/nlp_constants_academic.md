<!--
VIGIA Academic Documentation
Module: 5ca62db1
Batch ID: vigia-doc-0167-5ca62db1
Generated: 2026-05-20T14:56:47.880708+00:00
-->

## ENGLISH

`vigia/tools/nlp_constants.py` is a forensic NLP support module that establishes a deterministic controlled vocabulary of lexical constants and base types. Extracted from the adversarial forensic source, it resolves previously undefined symbolic references detected at line 50. By codifying immutable lexical anchors—tag sets, regular-expression signatures, and semantic category labels—it ensures reproducible text analysis. Non-computational scientists may regard it as a fixed glossary that standardizes input to downstream forensic linguistic pipelines, eliminating source-level indeterminacy without altering evidentiary semantics.

*Scientific note: Removes lexical entropy via a priori definitions.*

---

## ESPAÑOL

`vigia/tools/nlp_constants.py` es un módulo de soporte para NLP forense que establece un vocabulario controlado determinista de constantes léxicas y tipos base. Extraído del fuente pericial adversarial, resuelve referencias simbólicas previamente indefinidas detectadas en la línea 50. Al codificar anclas léxicas inmutables—conjuntos de etiquetas, firmas de expresiones regulares y etiquetas semánticas—garantiza análisis textuales reproducibles. El módulo actúa como glosario fijo que estandariza la entrada de pipelines lingüísticos forenses, eliminando la indeterminación en origen sin alterar la semántica probatoria.

*Nota científica: Elimina entropía léxica mediante definiciones a priori.*

---

## РУССКИЙ

`vigia/tools/nlp_constants.py` — вспомогательный модуль судебной лингвистической экспертизы, задающий детерминированный контролируемый словарь лексических констант и базовых типов. Извлечён из исходного кода адверсарной судебной системы; устраняет ранее неопределённые символьные ссылки, выявленные в строке 50. Кодифицируя неизменяемые лексические якоря — наборы меток, сигнатуры регулярных выражений, семантические категории — он обеспечивает воспроизводимый текстовый анализ. Модуль выполняет роль фиксированного глоссария, стандартизируя входные данные для судебных лингвистических конвейеров.

*Научное примечание: устраняет лексическую энтропию через априорные определения.*

---

## 中文

`vigia/tools/nlp_constants.py` 是数字取证 NLP 支撑模块，用于建立确定性的受控词汇表与基础语义类型。该模块提取自对抗性取证源文件，修复了原第 50 行未定义的符号引用。通过将标签集、正则表达式特征与语义类别编码为不可变词汇锚点，确保文本分析可重复。非计算机背景科学家可将其视为固定术语表，为下游法医语言流程提供标准化输入，在不改变证据语义的前提下消除源级不确定性。

*科学注：通过先验定义消除词汇熵。*

---

## Glossary / Glosario / Глоссарий / 词汇表

1. **Controlled vocabulary / Vocabulario controlado / Контролируемый словарь / 受控词汇表** — Closed set of authorized terms preventing analytical ambiguity.
2. **Lexical anchor / Ancla léxica / Лексический якорь / 词汇锚点** — Immutable token fixing semantic meaning within a corpus.
3. **Deterministic system / Sistema determinista / Детерминированная система / 确定性系统** — Process where identical inputs always produce identical outputs.
4. **Forensic NLP / NLP forense / Судебный NLP / 取证自然语言处理** — Language analysis applied to evidentiary text under legal custody.
5. **Symbolic reference / Referencia simbólica / Символьная ссылка / 符号引用** — Named identifier pointing to a data object in source code.
6. **Source-level indeterminacy / Indeterminación en origen / Неопределённость уровня исходного кода / 源级不确定性** — Uncertainty arising from missing declarations in analytical code.
7. **Regular-expression signature / Firma de expresión regular / Сигнатура регулярного выражения / 正则表达式特征** — Formal pattern describing invariant textual structures.
8. **Semantic category label / Etiqueta de categoría semántica / Семантическая метка категории / 语义类别标签** — Classification tag assigning conceptual domain to a phrase.
9. **Reproducible analysis / Análisis reproducible / Воспроизводимый анализ / 可重复分析** — Protocol yielding consistent results under repeated identical conditions.
10. **Evidentiary semantics / Semántica probatoria / Доказательственная семантика / 证据语义** — Stable meaning content of a text item in legal proceedings.

---

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
