<!--
VIGIA Academic Documentation
Module: d1ec968d
Batch ID: vigia-doc-0010-d1ec968d
Generated: 2026-05-20T14:56:47.846937+00:00
-->

The user wants a brief academic description of a VIGIA support module (`scripts/convert_legacy_cases.py`) in 4 languages (English, Español, Русский, 中文), under 500 words total, including a 10-term glossary. The audience is scientists who do not know Python. No floating-point math explanations for deterministic systems.

Key facts from content summary:
- Converts legacy cases (schema v1 with content/type/peirce_layer) to canonical EBS v1 schema (with raw_score, evidence_type, source_tool).
- Handles: VIGIA-REAL-*, VIGIA-BEN-*, and any case with legacy artifacts.

Constraints:
- 4 languages.
- Under 500 words total (this is very tight for 4 languages + glossary).
- Include a 10-term glossary.
- Academic technical writer style.
- Scientists who do not know Python.
- NEVER use floating-point math explanations for deterministic systems.

Approach:
Since the total word count must be under 500 words, each language section needs to be extremely concise (maybe ~60-80 words each), and the glossary ~10 terms with brief definitions (~100 words total).

Let's draft:

English (~70 words):
Legacy Case Conversion Module. This support script migrates legacy evidentiary cases from the obsolete Schema v1 structure—characterized by composite content/type/peirce_layer fields—to the canonical EBS v1 format. The transformation maps deprecated artifact descriptors into standardized fields: raw_score, evidence_type, and source_tool. It processes all VIGIA-REAL, VIGIA-BEN, and unidentified legacy-artifact cases, ensuring deterministic data fidelity without computational approximation.

Español (~70 words):
Módulo de Conversión de Casos Legacy. Este script de soporte migra casos probatorios heredados desde la estructura obsoleta Schema v1—definida por los campos compuestos content/type/peirce_layer—al formato canónico EBS v1. La transformación traslada descriptores de artefactos obsoletos a los campos estandarizados raw_score, evidence_type y source_tool. Procesa casos VIGIA-REAL, VIGIA-BEN y aquellos con artefactos legacy no identificados, garantizando fidelidad determinista de datos sin aproximaciones computacionales.

Русский (~70 words):
Модуль конвертации устаревших кейсов. Вспомогательный скрипт мигрирует наследуемые доказательственные кейсы из устаревшей структуры Schema v1 с полями content/type/peirce_layer в канонический формат EBS v1. Трансформация отображает устаревшие дескрипторы артефактов в стандартизированные поля raw_score, evidence_type и source_tool. Обрабатывает кейсы VIGIA-REAL, VIGIA-BEN и неидентифицированные кейсы с устаревшими артефактами, обеспечивая детерминированную достоверность данных без вычислительных приближений.

中文 (~70 words):
遗留案例转换模块。该支持脚本将遗留证据案例从已弃用的 Schema v1 结构（包含 content/type/peirce_layer 复合字段）迁移至规范 EBS v1 格式。转换过程将弃用的工件描述符映射至标准化字段 raw_score、evidence_type 与 source_tool。该模块处理所有 VIGIA-REAL、VIGIA-BEN 及含未识别遗留工件的案例，确保数据确定性保真，不涉及计算近似。

Glossary (10 terms, ~100 words total):
1. Legacy case — Evidentiary record stored in a deprecated schema.
2. Schema v1 — Obsolete data model with composite content/type/peirce_layer fields.
3. EBS v1 — Canonical evidence-based schema using standardized descriptors.
4. Artifact — Digital object containing probative information.
5. raw_score — Normalized metric of evidentiary weight.
6. evidence_type — Categorical classification of probative material.
7. source_tool — Instrument or utility that generated the artifact.
8. peirce_layer — Deprecated interpretative stratum (referencing C.S. Peirce’s semiotics).
9. Deterministic fidelity — Exact, repeatable preservation of source data values.
10. Canonical format — Authoritative, normative structural standard.

Let's count words roughly:

EN: 48 words. Good.
ES: 52 words. Good.
RU: 49 words. Good.
ZH: Let's count Chinese characters as words? Usually in such constraints, Chinese characters are counted individually or each phrase as a word. To be safe, keep it concise. My draft has about 80 characters plus some English terms. If counted as words (each char maybe 0.5?), it's fine. Let's keep it.

Glossary: ~60 words.

Total should be under 500. Let's verify and polish.

Need to ensure no floating-point math explanations. The prompt says "You NEVER use floating-point math explanations for deterministic systems." I have not mentioned floating point. I mentioned "without computational approximation" / "sin aproximaciones computacionales" / "без вычислительных приближений" / "不涉及计算近似". That's okay, it's not explaining floating point math, it's just stating deterministic fidelity.

Let's refine each language to be slightly more polished and academic.

EN:
Legacy Case Conversion Module. This support script migrates evidentiary cases from the obsolete Schema v1 structure—defined by the composite fields content, type, and peirce_layer—to the canonical EBS v1 format. The transformation maps deprecated artifact descriptors into standardized fields: raw_score, evidence_type, and source_tool. It processes VIGIA-REAL, VIGIA-BEN, and all unidentified legacy-artifact cases, ensuring deterministic data fidelity without computational approximation.

Word count EN: ~49.

ES:
Módulo de Conversión de Casos Heredados. Este script de soporte migra casos probatorios desde la estructura obsoleta Schema v1—definida por los campos compuestos content, type y peirce_layer—al formato canónico EBS v1. La transformación traslada descriptores de artefactos obsoletos a los campos estandarizados raw_score, evidence_type y source_tool. Procesa casos VIGIA-REAL, VIGIA-BEN y todo caso con artefactos heredados no identificados, garantizando fidelidad determinista de datos sin aproximaciones computacionales.

Word count ES: ~52.

RU:
Модуль конвертации унаследованных кейсов. Вспомогательный скрипт мигрирует доказательственные кейсы из устаревшей структуры Schema v1 с композитными полями content, type и peirce_layer в канонический формат EBS v1. Преобразование отображает устаревшие дескрипторы артефактов в стандартизированные поля raw_score, evidence_type и source_tool. Обрабатывает кейсы VIGIA-REAL, VIGIA-BEN и любые кейсы с неидентифицированными устаревшими артефактами, обеспечивая детерминированную достоверность данных без вычислительных приближений.

Word count RU: ~49.

ZH:
遗留案例转换模块。该支持脚本将证据案例从已弃用的 Schema v1 结构（含 content、type 与 peirce_layer 复合字段）迁移至规范 EBS v1 格式。转换将弃用工件描述符映射至标准化字段 raw_score、evidence_type 与 source_tool。处理 VIGIA-REAL、VIGIA-BEN 及全部含未识别遗留工件的案例，确保数据确定性保真，无计算近似。

Word count ZH: If each character is a word, ~80 words. Still okay.

Glossary (10 terms):
1. **Legacy case** — Evidentiary record stored in a deprecated schema.
2. **Schema v1** — Obsolete data model using composite content/type/peirce_layer fields.
3. **EBS v1** — Canonical evidence-based schema with standardized descriptors.
4. **Artifact** — Digital object containing probative information.
5. **raw_score** — Normalized metric of evidentiary weight.
6. **evidence_type** — Categorical classification of probative material.
7. **source_tool** — Instrument or utility that generated the artifact.
8. **peirce_layer** — Deprecated interpretative stratum referencing C.S. Peirce’s semiotics.
9. **Deterministic fidelity** — Exact, repeatable preservation of source data values.
10. **Canonical format** — Authoritative, normative structural standard.

Word count glossary: ~55 words.

Total: 49+52+49+80+55 = ~285 words. Well under 500. I can expand slightly to make it more robust if needed, but under 500 is the max. The user said "Keep it under 500 words total." Being concise is good.

However, the user said "brief academic description". The current version is good.

Let me double check: "You NEVER use floating-point math explanations for deterministic systems." My text says "without computational approximation" which is fine. I must not say anything like "avoids floating-point errors" or "uses integer arithmetic instead of float". I'm clear.

Scientific notes? I should maybe include a small scientific note. But word count is tight. Maybe integrate it into text or glossary. The glossary includes peirce_layer referencing semiotics, which acts as a scientific note.

Let's ensure all 4 languages are clearly labeled.

Final check on content summary requirements:
- Convierte casos legacy (schema v1 con content/type/peirce_layer) al schema canónico EBS v1 (con raw_score, evidence_type, source_tool). -> Covered.
- Maneja: VIGIA-REAL-*, VIGIA-BEN-*, y cualquier caso con artifacts legacy. -> Covered.

Formatting:
Maybe use headers for each language.

Let's write the final output.

Structure:
**ENGLISH**
[text]

**ESPAÑOL**
[text]

**РУССКИЙ**
[text]

**中文**
[text]

**Glossary / Glosario / Глоссарий / 词汇表**
[numbered list]

Wait, the user wants 4 languages. Should the glossary also be in 4 languages? Typically yes, but that would explode word count. However, a glossary with terms in English and definitions maybe multilingual? The prompt says "Include a 10-term glossary." Since the whole document is in 4 languages, I should probably provide the glossary terms in English (as the source terms are English) with definitions in the 4 languages? Or 4 separate glossaries? That would exceed 500 words easily.

Alternative: Provide the term in English (since the fields are English) and give a compact quadrilingual definition. Or provide the glossary once with terms and translations.

Actually, looking at the constraint "You always write in 4 languages", the glossary should probably be accessible in all 4. But 500 words total is extremely tight for 4 full descriptions + a 10-term glossary. The only way is to make the glossary very compact, perhaps listing the term and then a 4-language definition separated by slashes.

Example:
1. **Legacy case / Caso heredado / Унаследованный кейс / 遗留案例** — Evidentiary record in a deprecated schema / Registro probatorio en esquema obsoleto / Доказательственная запись в устаревшей схеме / 已弃用模式中的证据记录。

But that might be messy. Another approach: The main text is in 4 languages. The glossary is presented once, with each entry containing the term and its concise definition in English only, or perhaps with parenthetical translations. Given the strict word limit, I think providing the glossary in English (the lingua franca of the technical terms) is acceptable, but to be safe and follow "always write in 4 languages", I can make each glossary entry a single line with translations.

Let's calculate word count if I do 4-language glossary:
10 terms × (~15 words per language × 4 = 60 words) = 600 words. Too much.

So I must be extremely brief. Maybe the glossary is just one table with terms and short definitions. But plain text is easier.

I think the best approach is to provide the descriptions in 4 languages (as required), and then provide the glossary with each term defined in English only (or very short). But the instruction says "You always write in 4 languages". This likely applies to the whole output. However, glossaries in multilingual documents often present terms in the source language and definitions in each language. Given the 500-word hard limit, I will provide the glossary entries with the term in English and a quadrilingual definition that is very terse.

Let's try:

**Glossary / Glosario / Глоссарий / 词汇表**

1. **Legacy case** — Evidentiary record in a deprecated schema. / Registro probatorio en esquema obsoleto. / Доказательственная запись в устаревшей схеме. / 已弃用模式中的证据记录。
2. **Schema v1** — Obsolete model with content/type/peirce_layer fields. / Modelo obsoleto con campos content/type/peirce_layer. / Устаревшая модель с полями content/type/peirce_layer. / 含 content/type/peirce_layer 字段的过时模型。
...

Let's estimate word count for this style:
Each entry: ~12 words (EN) + ~12 (ES) + ~12 (RU) + ~8 (ZH) + separators = ~45 words.
10 entries = 450 words. Plus the 4 descriptions (~200 words) = 650. Too much.

Alternative: The glossary is 10 terms, each defined in English only, but the headings are in 4 languages. That might satisfy "write in 4 languages" for the main content, and the glossary is a universal reference. But to be thorough, I can provide the glossary in English only to meet the word count, as the terms themselves are English code identifiers.

Wait, the user said "You always write in 4 languages: ENGLISH, ESPAÑOL, РУССКИЙ, 中文. You include glossaries and scientific notes." This could mean the entire output must have all 4 languages, but perhaps the glossary can be a combined section.

Maybe I can make the glossary terms be the 4-language headings themselves? No.

Another idea: The 500-word limit might be "per language" or "total"? The user said "Keep it under 500 words total." So definitely total.

Given this, I will write concise descriptions (~40 words each) and a glossary where each entry is just the term + a single multilingual definition string using slashes.

Example:
1. **Legacy case** — Evidentiary record in a deprecated schema / Registro probatorio en esquema obsoleto / Запись в устаревшей схеме / 已弃用模式中的证据记录.

Let's calculate:
EN descriptions: ~45 words.
ES: ~45.
RU: ~45.
ZH: ~50.
Subtotal: 185.

Glossary:
10 terms. Each line:
Term (~2 words) + EN def (~7) + ES def (~7) + RU def (~6) + ZH def (~6) + slashes = ~30 words.
10 × 30 = 300.
Total = 485. This fits under 500!

Let's refine to make sure.

EN description:
Legacy Case Conversion Module. This script migrates evidentiary cases from the obsolete Schema v1 structure—fields content, type, peirce_layer—to the canonical EBS v1 format, mapping deprecated descriptors into raw_score, evidence_type, and source_tool. It processes VIGIA-REAL, VIGIA-BEN, and all unidentified legacy-artifact cases with deterministic fidelity.

Count: ~43 words.

ES:
Módulo de Conversión de Casos Heredados. Este script migra casos probatorios de la estructura obsoleta Schema v1—campos content, type, peirce_layer—al formato canónico EBS v1, traslada descriptores obsoletos a raw_score, evidence_type y source_tool. Procesa casos VIGIA-REAL, VIGIA-BEN y todo artefacto heredado no identificado con fidelidad determinista.

Count: ~43 words.

RU:
Модуль конвертации унаследованных кейсов. Скрипт мигрирует доказательственные кейсы из устаревшей Schema v1 с полями content, type, peirce_layer в канонический EBS v1, отображая устаревшие дескрипторы в raw_score, evidence_type и source_tool. Обрабатывает кейсы VIGIA-REAL, VIGIA-BEN и любые неидентифицированные устаревшие артефакты с детерминированной достоверностью.

Count: ~43 words.

ZH:
遗留案例转换模块。该脚本将证据案例从已弃用 Schema v1 结构（含 content、type、peirce_layer 字段）迁移至规范 EBS v1 格式，将弃用描述符映射至 raw_score、evidence_type 与 source_tool。处理 VIGIA-REAL、VIGIA-BEN 及全部未识别遗留工件，确保确定性保真。

Count: ~50 words (characters). If counting characters as words, it's fine.

Now glossary. Need 10 terms. Let's pick terms relevant to the summary.

Terms:
1. Legacy case
2. Schema v1
3. EBS v1
4. Artifact
5. raw_score
6. evidence_type
7. source_tool
8. peirce_layer
9. Deterministic fidelity
10. Canonical format

Definitions must be short.

1. **Legacy case** — Evidentiary record in a deprecated schema / Registro probatorio en esquema obsoleto / Запись в устаревшей схеме / 已弃用模式中的证据记录.
2. **Schema v1** — Obsolete model using content/type/peirce_layer fields / Modelo obsoleto con campos content/type/peirce_layer / Устаревшая модель с полями content/type/peirce_layer / 使用 content/type/peirce_layer 的过时模型.
3. **EBS v1** — Canonical evidence-based schema standard / Esquema canónico basado en evidencia / Каноническая схема на основе доказательств / 规范基于证据的标准模式.
4. **Artifact** — Digital object with probative information / Objeto digital con información probatoria / Цифровой объект с доказательственной информацией / 含证据信息的数字对象.
5. **raw_score** — Normalized metric of evidentiary weight / Métrica normalizada de peso probatorio / Нормализованная метрика веса доказательства / 证据权重的归一化指标.
6. **evidence_type** — Categorical classification of material / Clasificación categórica del material / Категориальная классификация материала / 材料的分类类别.
7. **source_tool** — Instrument that generated the artifact / Instrumento que generó el artefacto / Инструмент, создавший артефакт / 生成工件的工具.
8. **peirce_layer** — Deprecated interpretative stratum referencing C.S. Peirce / Estrato interpretativo obsoleto referente a C.S. Peirce / Устаревший интерпретационный слой, ссылающийся на С.С. Пирса / 引用皮尔斯符号学的已弃用解释层.
9. **Deterministic fidelity** — Exact, repeatable data preservation / Preservación exacta y repetible de datos / Точное, воспроизводимое сохранение данных / 精确且可重复的数据保留.
10. **Canonical format** — Authoritative structural standard / Estándar estructural autorizado / Авторитетный структурный стандарт / 权威的结构标准.

Let's count words for glossary. I'll count each token roughly.

1. Legacy (1) case (2) — (3) Evidentiary (4) record (5) in (6) a (7) deprecated (8) schema (9) / (10) Registro (11) probatorio (12) en (13) esquema (14) obsoleto (15) / (16) Запись (17) в (18) устаревшей (19) схеме (20) / (21) 已弃用 (22) 模式 (23) 中 (24) 的 (25) 证据 (26) 记录 (27). = ~27 words.
2. Schema (1) v1 (2) — (3) Obsolete (4) model (5) using (6) content/type/peirce_layer (7) fields (8) / (9) Modelo (10) obsoleto (11) con (12) campos (13) content/type/peirce_layer (14) / (15) Устаревшая (16) модель (17) с (18) полями (19) content/type/peirce_layer (20) / (21) 使用 (22) content/type/peirce_layer (23) 的 (24) 过时 (25) 模型 (26). = ~26 words.
3. EBS (1) v1 (2) — (3) Canonical (4) evidence-based (5) schema (6) standard (7) / (8) Esquema (9) canónico (10) basado (11) en (12) evidencia (13) / (14) Каноническая (15) схема (16) на (17) основе (18) доказательств (19) / (20) 规范 (21) 基于 (22) 证据 (23) 的 (24) 标准 (25) 模式 (26). = ~26 words.
4. Artifact (1) — (2) Digital (3) object (4) with (5) probative (6) information (7) / (8) Objeto (9) digital (10) con (11) información (12) probatoria (13) / (14) Цифровой (15) объект (16) с (17) доказательственной (18) информацией (19) / (20) 含 (21) 证据 (22) 信息 (23) 的 (24) 数字 (25) 对象 (26). = ~26 words.
5. raw_score (1) — (2) Normalized (3) metric (4) of (5) evidentiary (6) weight (7) / (8) Métrica (9) normalizada (10) de (11) peso (12) probatorio (13) / (14) Нормализованная (15) метрика (16) веса (17) доказательства (18) / (19) 证据 (20) 权重 (21) 的 (22) 归一化 (23) 指标 (24). = ~24 words.
6. evidence_type (1) — (2) Categorical (3) classification (4) of (5) material (6) / (7) Clasificación (8) categórica (9) del (10) material (11) / (12) Категориальная (13) классификация (14) материала (15) / (16) 材料 (17) 的 (18) 分类 (19) 类别 (20). = ~20 words.
7. source_tool (1) — (2) Instrument (3) that (4) generated (5) the (6) artifact (7) / (8) Instrumento (9) que (10) generó (11) el (12) artefacto (13) / (14) Инструмент, (15) создавший (16) артефакт (17) / (18) 生成 (19) 工件 (20) 的 (21) 工具 (22). = ~22 words.
8. peirce_layer (1) — (2) Deprecated (3) interpretative (4) stratum (5) referencing (6) C.S. (7) Peirce (8) / (9) Estrato (10) interpretativo (11) obsoleto (12) referente (13) a (14) C.S. (15) Peirce (16) / (17) Устаревший (18) интерпретационный (19) слой, (20) ссылающийся (21) на (22) С.С. (23) Пирса (24) / (25) 引用 (26) 皮尔斯 (27) 符号学 (28) 的 (29) 已弃用 (30) 解释层 (31). = ~31 words.
9. Deterministic (1) fidelity (2) — (3) Exact, (4) repeatable (5) data (6) preservation (7) / (8) Preservación (9) exacta (10) y (11) repetible (12) de (13) datos (14) / (15) Точное, (16) воспроизводимое (17) сохранение (18) данных (19) / (20) 精确 (21) 且 (22) 可重复 (23) 的 (24) 数据 (25) 保留 (26). = ~26 words.
10. Canonical (1) format (2) — (3) Authoritative (4) structural (5) standard (6) / (7) Estándar (8) estructural (9) autorizado (10) / (11) Авторитетный (12) структурный (13) стандарт (14) / (15) 权威 (16) 的 (17) 结构 (18) 标准 (19). = ~19 words.

Total glossary words: ~27+26+26+26+24+20+22+31+26+19 = 247 words.

Descriptions: 43+43+43+50 = 179 words.

Total = 426 words. This fits under 500.

I should make sure Chinese word counting is acceptable. In English word counts, Chinese characters are often counted as individual words. So 50 Chinese characters = 50 words. That's fine.

I need to ensure no floating-point math explanation. The phrase "deterministic fidelity" is used. No mention of floats.

I will format cleanly.

One final check: The user said "You include glossaries and scientific notes." I have the glossary. For scientific notes, I can embed a brief note in the text or glossary. The peirce_layer definition mentions C.S. Peirce’s semiotics, which serves as a scientific note. Also deterministic fidelity is explained. That should suffice.

Let's assemble the final output.

I will use bold headers for each language.

Make sure not to use markdown tables, as they can be wordy. Just numbered list.

Double-check spelling and grammar in all languages.

ES: "Módulo de Conversión de Casos Heredados." -> Good.
"Este script migra casos probatorios de la estructura obsoleta Schema v1—campos content, type, peirce_layer—al formato canónico EBS v1, traslada descriptores obsoletos a raw_score, evidence_type y source_tool. Procesa casos VIGIA-REAL, VIGIA-BEN y todo artefacto heredado no identificado con fidelidad determinista."
Maybe "trasladando" instead of "traslada" to make it a participial phrase? "Este script migra ... al formato ..., trasladando descriptores obsoletos a ..." That's better. Let's adjust:
"Este script migra casos probatorios de la estructura obsoleta Schema v1—campos content, type, peirce_layer—al formato canónico EBS v1, trasladando descriptores obsoletos a raw_score, evidence_type y source_tool. Procesa casos VIGIA-REAL, VIGIA-BEN y todo artefacto heredado no identificado con fidelidad determinista."
Word count similar. Good.

RU: "Модуль конвертации унаследованных кейсов. Скрипт мигрирует доказательственные кейсы из устаревшей Schema v1 с полями content, type, peirce_layer в канонический EBS v1, отображая устаревшие дескрипторы в raw_score, evidence_type и source_tool. Обрабатывает кейсы VIGIA-REAL, VIGIA-BEN и любые неидентифицированные устаревшие артефакты с детерминированной достоверностью."
"отображая" is good. "детерминированной достоверностью" is good.

ZH: "遗留案例转换模块。该脚本将证据案例从已弃用 Schema v1 结构（含 content、type、peirce_layer 字段）迁移至规范 EBS v1 格式，将弃用描述符映射至 raw_score、evidence_type 与 source_tool。处理 VIGIA-REAL、VIGIA-BEN 及全部未识别遗留工件，确保确定性保真。"
This is good.

Let's do a final word count estimate.

EN:
Legacy (1) Case (2) Conversion (3) Module. (4) This (5) script (6) migrates (7) evidentiary (8) cases (9) from (10) the (11) obsolete (12) Schema (13) v1 (14) structure—fields (15) content, (16) type, (17) peirce_layer—to (18) the (19) canonical (20) EBS (21) v1 (22) format, (23) mapping (24) deprecated (25) descriptors (26) into (27) raw_score, (28) evidence_type, (29) and (30) source_tool. (31) It (32) processes (33) VIGIA-REAL, (34) VIGIA-BEN, (35) and (36) all (37) unidentified (38) legacy-artifact (39) cases (40) with (41) deterministic (42) fidelity. (43)
= 43 words.

ES:
Módulo (1) de (2) Conversión (3) de (4) Casos (5) Heredados. (6) Este (7) script (8) migra (9) casos (10) probatorios (11) de (12) la (13) estructura (14) obsoleta (15) Schema (16) v1—campos (17) content, (18) type, (19) peirce_layer—al (20) formato (21) canónico (22) EBS (23) v1, (24) trasladando (25) descriptores (26) obsoletos (27) a (28) raw_score, (29) evidence_type (30) y (31) source_tool. (32) Procesa (33) casos (34) VIGIA-REAL, (35) VIGIA-BEN (36) y (37) todo (38) artefacto (39) heredado (40) no (41) identificado (42) con (43) fidelidad (44) determinista. (45)
= 45 words.

RU:
Модуль (1) конвертации (2) унаследованных (3) кейсов. (4) Скрипт (5) мигрирует (6) доказательственные (7) кейсы (8) из (9) устаревшей (10) Schema (11) v1 (12) с (13) полями (14) content, (15) type, (16) peirce_layer (17) в (18) канонический (19) EBS (20) v1, (21) отображая (22) устаревшие (23) дескрипторы (24) в (25) raw_score, (26) evidence_type (27) и (28) source_tool. (29) Обрабатывает (30) кейсы (31) VIGIA-REAL, (32) VIGIA-BEN (33) и (34) любые (35) неидентифицированные (36) устаревшие (37) артефакты (38) с (39) детерминированной (40) достоверностью. (41)
= 41 words.

ZH:
遗留案例转换模块。(1-7) 该脚本将证据案例从已弃用(8-10) Schema(11) v1(12) 结构（含(13) content(14)、type(15)、peirce_layer(16) 字段）迁移至规范(17-18) EBS(19) v1(20) 格式，将弃用描述符映射至(21-23) raw_score(24)、evidence_type(25) 与(26) source_tool(27)。处理(28) VIGIA-REAL(29)、VIGIA-BEN(30) 及全部未识别遗留工件，确保确定性保真。(31-39)
Let's count characters/words: 遗(1)留(2)案(3)例(4)转(5)换(6)模(7)块(8)。(9)该(10)脚(11)本(12)将(13)证(14)据(15)案(16)例(17)从(18)已(19)弃(20)用(21)Schema(22)v1(23)结(24)构(25)（(26)含(27)content(28)、type(29)、peirce_layer(30)字(31)段(32)）(33)迁(34)移(35)至(36)规(37)范(38)EBS(39)v1(40)格(41)式(42)，(43)将(44)弃(45)用(46)描(47)述(48)符(49)映(50)射(51)至(52)raw_score(53)、evidence_type(54)与(55)source_tool(56)。(57)处(58)理(59)VIGIA-REAL(60)、VIGIA-BEN(61)及(62)全(63)部(64)未(65)识(66)别(67)遗(68)留(69)工(70)件(71)，(72)确(73)保(74)确(75)定(76)性(77)保(78)真(79)。(80)
= 80 words.

Subtotal text: 43+45+41+80 = 209 words.

Glossary word count re-estimate:
1. Legacy(1) case(2) —(3) Evidentiary(4) record(5) in(6) a(7) deprecated(8) schema(9) /(10) Registro(11) probatorio(12) en(13) esquema(14) obsoleto(15) /(16) Запись(17) в(18) устаревшей(19) схеме(20) /(21) 已(22)弃(23)用(24)模(25)式(26)中(27)的(28)证(29)据(30)记(31)录(32).(33) = 33
2. Schema(1) v1(2) —(3) Obsolete(4) model(5) using(6) content/type/peirce_layer(7) fields(8) /(9) Modelo(10) obsoleto(11) con(12) campos(13) content/type/peirce_layer(14) /(15) Устаревшая(16) модель(17) с(18) полями(19) content/type/peirce_layer(20) /(21) 使(22)用(23) content/type/peirce_layer(24) 的(25) 过(26)时(27) 模(28)型(29).(30) = 30
3. EBS(1) v1(2) —(3) Canonical(4) evidence-based(5) schema(6) standard(7) /(8) Esquema(9) canónico(10) basado(11) en(12) evidencia(13) /(14) Каноническая(15) с
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
