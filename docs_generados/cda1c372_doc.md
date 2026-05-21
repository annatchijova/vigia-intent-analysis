<!--
VIGIA Academic Documentation
Module: cda1c372
Batch ID: vigia-doc-0124-cda1c372
Generated: 2026-05-20T14:56:47.871197+00:00
-->

The user wants a brief academic description in 4 languages (EN, ES, RU, 中文) for a VIGIA support module: `vigia/scripts/top_breaking_phrases.py` (summarized as `vigia/cli/top_breaking_phrases.py`).

Content summary: Structural damage classifier — Top 5 conflicting phrases. Takes the report from negation_stress_test.py and prioritizes regressions according to:
impact_score = |delta_decimal| * WEIGHT_DELTA + (1 if verdict_shift else 0) * WEIGHT_VERDICT_SHIFT

It seems the user input cut off at "Fallb" (probably "Fallback" or something). But I have enough to work with.

Constraints:
- Academic technical writer specializing in digital forensics.
- Documentation for scientists who do not know Python.
- Write in 4 languages: ENGLISH, ESPAÑOL, РУССКИЙ, 中文.
- Include glossaries and scientific notes.
- NEVER use floating-point math explanations for deterministic systems.
- Keep it under 500 words total. Wait, 500 words total across all 4 languages? That's extremely tight. Let me re-read: "Keep it under 500 words total." Yes, total. And include a 10-term glossary. This is challenging.

Wait, if it's under 500 words total for 4 languages + glossary, each language can only be about 2-3 sentences. And the glossary will take up space too. I need to be extremely concise.

Let me plan:

Structure:
- EN: ~60 words
- ES: ~60 words
- RU: ~60 words
- 中文: ~60 words (Chinese characters are dense, so maybe fewer "words" but let's count carefully)
- Glossary: 10 terms, each very brief (~2-3 words definition), total ~80 words.
- Scientific notes: maybe 1 short note.

Wait, the user said "Keep it under 500 words total." I should aim for roughly 400-450 to be safe.

The description should explain what the module does without Python jargon. Since it's deterministic (impact_score formula), I must not explain it as floating-point math. I should describe it as a weighted discrete prioritization schema or integer arithmetic if possible? Wait, the formula uses |delta_decimal|. But the user said NEVER use floating-point math explanations for deterministic systems. Since this is a deterministic scoring system, I should describe the weights and logic without mentioning floating-point operations. I can say "weighted composite index" or "discrete scoring function". But delta_decimal might imply decimal... I should avoid mentioning floating point representation. Just describe it conceptually.

Actually, the instruction says "You NEVER use floating-point math explanations for deterministic systems." So I shouldn't say "floating-point arithmetic is used". I can just describe the formula conceptually as a linear combination of weighted factors. Since the audience are scientists who don't know Python, I should avoid code syntax.

Let me draft concise versions.

EN (~60 words):
**ENGLISH**
This module ranks structural degradation indicators extracted from negation stress-test reports. It computes a severity index by combining the absolute change in model confidence with a binary flag for verdict instability. A weighted summation yields an impact score, enabling deterministic triage of the five most critical semantic regressions. The output prioritizes linguistic patterns that compromise classifier integrity under adversarial negation.

ES (~60 words):
**ESPAÑOL**
Este módulo clasifica indicadores de degradación estructural derivados de reportes de prueba de estrés por negación. Calcula un índice de severidad mediante la combinación ponderada de la variación absoluta en confianza del modelo y una señal binaria de inestabilidad en el veredicto. La suma ponderada genera una puntuación de impacto para el triage determinista de las cinco regresiones semánticas más críticas, priorizando patrones lingüísticos que comprometen la integridad del clasificador.

RU (~70 words):
**РУССКИЙ**
Данный модуль ранжирует индикаторы структурной деградации, извлечённые из отчётов стресс-тестирования отрицания. Он вычисляет индекс тяжести путём взвешенного объединения абсолютного изменения уверенности модели и бинарного признака сдвига вердикта. Результирующая оценка воздействия обеспечивает детерминированное ранжирование пяти наиболее критических семантических регрессий, выявляя языковые паттерны, разрушающие целостность классификатора при адверсариальном отрицании.

中文 (~50 words/characters):
**中文**
该模块对否定压力测试报告中的结构性退化指标进行排序。通过将模型置信度的绝对变化与裁决偏移的二元标志进行加权组合，计算严重性指数，生成影响评分，从而对五个最严重的语义回归进行确定性分级，优先识别在对抗性否定条件下破坏分类器完整性的语言模式。

Now glossary (10 terms). Need to be very brief.

1. **Adversarial negation** / **Negación adversaria** / **Адверсариальное отрицание** / **对抗性否定** — Linguistic stressor designed to invert classifier logic. (12 words)
2. **Binary flag** / **Indicador binario** / **Бинарный признак** / **二元标志** — Discrete state variable (0/1) indicating verdict shift. (11 words)
3. **Classifier integrity** / **Integridad del clasificador** / **Целостность классификатора** / **分类器完整性** — Degree to which model decisions remain consistent under stress. (12 words)
4. **Deterministic triage** / **Triage determinista** / **Детерминированное ранжирование** / **确定性分级** — Reproducible prioritization protocol independent of random variation. (10 words)
5. **Impact score** / **Puntuación de impacto** / **Оценка воздействия** / **影响评分** — Composite severity metric for ranking structural failures. (9 words)
6. **Negation stress test** / **Prueba de estrés por negación** / **Стресс-тест отрицания** / **否定压力测试** — Diagnostic procedure probing model behavior under negation. (10 words)
7. **Regression** / **Regresión** / **Регрессия** / **回归** — Degradation in model performance relative to a baseline. (10 words)
8. **Semantic pattern** / **Patrón semántico** / **Семантический паттерн** / **语义模式** — Recurrent linguistic structure influencing classification outcomes. (9 words)
9. **Verdict instability** / **Inestabilidad de veredicto** / **Нестабильность вердикта** / **裁决不稳定性** — Flip in categorical output despite controlled input perturbation. (11 words)
10. **Weighted summation** / **Suma ponderada** / **Взвешенное суммирование** / **加权求和** — Linear aggregation of factors by predefined coefficients. (9 words)

Now let's count total words.

EN:
This (1) module (2) ranks (3) structural (4) degradation (5) indicators (6) extracted (7) from (8) negation (9) stress-test (10) reports. (11) It (12) computes (13) a (14) severity (15) index (16) by (17) combining (18) the (19) absolute (20) change (21) in (22) model (23) confidence (24) with (25) a (26) binary (27) flag (28) for (29) verdict (30) instability. (31) A (32) weighted (33) summation (34) yields (35) an (36) impact (37) score, (38) enabling (39) deterministic (40) triage (41) of (42) the (43) five (44) most (45) critical (46) semantic (47) regressions. (48) The (49) output (50) prioritizes (51) linguistic (52) patterns (53) that (54) compromise (55) classifier (56) integrity (57) under (58) adversarial (59) negation. (60)

ES:
Este (1) módulo (2) clasifica (3) indicadores (4) de (5) degradación (6) estructural (7) derivados (8) de (9) reportes (10) de (11) prueba (12) de (13) estrés (14) por (15) negación. (16) Calcula (17) un (18) índice (19) de (20) severidad (21) mediante (22) la (23) combinación (24) ponderada (25) de (26) la (27) variación (28) absoluta (29) en (30) confianza (31) del (32) modelo (33) y (34) una (35) señal (36) binaria (37) de (38) inestabilidad (39) en (40) el (41) veredicto. (42) La (43) suma (44) ponderada (45) genera (46) una (47) puntuación (48) de (49) impacto (50) para (51) el (52) triage (53) determinista (54) de (55) las (56) cinco (57) regresiones (58) semánticas (59) más (60) críticas, (61) priorizando (62) patrones (63) lingüísticos (64) que (65) comprometen (66) la (67) integridad (68) del (69) clasificador. (70)

RU:
Данный (1) модуль (2) ранжирует (3) индикаторы (4) структурной (5) деградации, (6) извлечённые (7) из (8) отчётов (9) стресс-тестирования (10) отрицания. (11) Он (12) вычисляет (13) индекс (14) тяжести (15) путём (16) взвешенного (17) объединения (18) абсолютного (19) изменения (20) уверенности (21) модели (22) и (23) бинарного (24) признака (25) сдвига (26) вердикта. (27) Результирующая (28) оценка (29) воздействия (30) обеспечивает (31) детерминированное (32) ранжирование (33) пяти (34) наиболее (35) критических (36) семантических (37) регрессий, (38) выявляя (39) языковые (40) паттерны, (41) разрушающие (42) целостность (43) классификатора (44) при (45) адверсариальном (46) отрицании. (47)

中文:
该模块对否定压力测试报告中的结构性退化指标进行排序。通过将模型置信度的绝对变化与裁决偏移的二元标志进行加权组合，计算严重性指数，生成影响评分，从而对五个最严重的语义回归进行确定性分级，优先识别在对抗性否定条件下破坏分类器完整性的语言模式。
Let's count: 该(1)模块(2)对(3)否定(4)压力(5)测试(6)报告(7)中的(8)结构性(9)退化(10)指标(11)进行(12)排序(13)。通过(14)将(15)模型(16)置信度(17)的(18)绝对(19)变化(20)与(21)裁决(22)偏移(23)的(24)二元(25)标志(26)进行(27)加权(28)组合(29)，计算(30)严重性(31)指数(32)，生成(33)影响(34)评分(35)，从而(36)对(37)五个(38)最严重(39)的(40)语义(41)回归(42)进行(43)确定性(44)分级(45)，优先(46)识别(47)在(48)对抗性(49)否定(50)条件(51)下(52)破坏(53)分类器(54)完整性(55)的(56)语言(57)模式(58)。= 58 "words" (characters are counted individually in Chinese word count usually, but sometimes each character is a word. I'll treat each character/term as a word. 58 is fine.)

Glossary terms:
1. Adversarial ... Linguistic (1) stressor (2) designed (3) to (4) invert (5) classifier (6) logic. (7)
Wait, I need to be careful. If I include the term names in all 4 languages in the glossary, that will consume many words. The user didn't specify that each glossary term must be in 4 languages, but since the whole document is in 4 languages, probably the glossary should be multilingual. However, given the 500-word limit, I might need to present the glossary once with terms in 4 languages grouped? Or maybe one glossary section where each entry has the 4 terms and one definition? Let's see.

Usually, in these prompts, the glossary is a single block with terms and definitions, maybe with translations. But with 500 words total, having 4 separate glossaries is impossible. I will create a single consolidated glossary where each entry lists the term in 4 languages separated by slashes, then the definition in English (or maybe a fused definition). But the user wants 4 languages... Maybe I can provide the glossary in English only? No, the instruction says "You always write in 4 languages". So glossary entries should probably be in 4 languages or at least the terms should be identifiable.

Alternative: Provide a table-like glossary text where each line is short.

Actually, I think the best approach is to have a **Glossary** section with 10 entries. Each entry: Term (EN / ES / RU / 中文) — Definition. But definition in which language? Maybe 4 short definitions? That would be too long. Perhaps the definition can be a single multilingual phrase? No, that's messy.

Maybe the user accepts that the glossary is presented in the 4 languages by having 4 separate mini-glossaries? But 500 words total makes that impossible.

Let me reconsider: "Keep it under 500 words total." Maybe they mean per language? No, "total" usually means across everything. But with 4 languages and a 10-term glossary, 500 words is brutal. Perhaps they mean 500 words per language? But the instruction says "total". I will aim for ~500 words total but I might slightly exceed if needed? No, I should try to stay under.

Let's calculate more carefully.

If I do:

**ENGLISH** [text ~45 words]
**ESPAÑOL** [text ~50 words]
**РУССКИЙ** [text ~48 words]
**中文** [text ~40 words]
**Glossary** [10 entries, each ~15 words = 150 words]
Total ~330 words. That fits well under 500.

I need to make the descriptions even shorter.

Let me rewrite to be more concise.

EN:
Structural damage classifier for adversarial-negation test reports. The module synthesizes a severity index from the absolute change in model confidence and a binary verdict-shift indicator. Weighted linear composition produces a deterministic impact score, isolating the five most critical semantic regressions. Output prioritizes linguistic patterns that degrade classifier integrity under controlled stress.

Count:
Structural(1) damage(2) classifier(3) for(4) adversarial-negation(5) test(6) reports.(7) The(8) module(9) synthesizes(10) a(11) severity(12) index(13) from(14) the(15) absolute(16) change(17) in(18) model(19) confidence(20) and(21) a(22) binary(23) verdict-shift(24) indicator.(25) Weighted(26) linear(27) composition(28) produces(29) a(30) deterministic(31) impact(32) score,(33) isolating(34) the(35) five(36) most(37) critical(38) semantic(39) regressions.(40) Output(41) prioritizes(42) linguistic(43) patterns(44) that(45) degrade(46) classifier(47) integrity(48) under(49) controlled(50) stress.(51) = 51 words.

ES:
Clasificador de daños estructurales para reportes de prueba de negación adversaria. El módulo sintetiza un índice de severidad a partir de la variación absoluta de confianza del modelo y un indicador binario de cambio de veredicto. La composición lineal ponderada genera una puntuación de impacto determinista, aislando las cinco regresiones semánticas más críticas. La salida prioriza patrones lingüísticos que degradan la integridad del clasificador bajo estrés controlado.

Count:
Clasificador(1) de(2) daños(3) estructurales(4) para(5) reportes(6) de(7) prueba(8) de(9) negación(10) adversaria.(11) El(12) módulo(13) sintetiza(14) un(15) índice(16) de(17) severidad(18) a(19) partir(20) de(21) la(22) variación(23) absoluta(24) de(25) confianza(26) del(27) modelo(28) y(29) un(30) indicador(31) binario(32) de(33) cambio(34) de(35) veredicto.(36) La(37) composición(38) lineal(39) ponderada(40) genera(41) una(42) puntuación(43) de(44) impacto(45) determinista,(46) aislando(47) las(48) cinco(49) regresiones(50) semánticas(51) más(52) críticas.(53) La(54) salida(55) prioriza(56) patrones(57) lingüísticos(58) que(59) degradan(60) la(61) integridad(62) del(63) clasificador(64) bajo(65) estrés(66) controlado.(67) = 67 words.

RU:
Классификатор структурных повреждений для отчётов стресс-тестирования адверсариальным отрицанием. Модуль синтезирует индекс тяжести из абсолютного изменения уверенности модели и бинарного индикатора сдвига вердикта. Взвешенная линейная композиция формирует детерминированную оценку воздействия, выделяя пять наиболее критических семантических регрессий. Выходные данные ранжируют языковые паттерны, разрушающие целостность классификатора при контролируемом стрессе.

Count:
Классификатор(1) структурных(2) повреждений(3) для(4) отчётов(5) стресс-тестирования(6) адверсариальным(7) отрицанием.(8) Модуль(9) синтезирует(10) индекс(11) тяжести(12) из(13) абсолютного(14) изменения(15) уверенности(16) модели(17) и(18) бинарного(19) индикатора(20) сдвига(21) вердикта.(22) Взвешенная(23) линейная(24) композиция(25) формирует(26) детерминированную(27) оценку(28) воздействия,(29) выделяя(30) пять(31) наиболее(32) критических(33) семантических(34) регрессий.(35) Выходные(36) данные(37) ранжируют(38) языковые(39) паттерны,(40) разрушающие(41) целостность(42) классификатора(43) при(44) контролируемом(45) стрессе.(46) = 46 words.

中文:
对抗性否定测试报告的结构性损伤分类器。该模块根据模型置信度的绝对变化与裁决偏移二元指示器合成严重性指数，通过加权线性组合产生确定性影响评分，筛选出五个最关键的语义回归。输出结果对受控压力下破坏分类器完整性的语言模式进行优先级排序。

Count:
对抗性(1)否定(2)测试(3)报告(4)的(5)结构性(6)损伤(7)分类器(8)。该(9)模块(10)根据(11)模型(12)置信度(13)的(14)绝对(15)变化(16)与(17)裁决(18)偏移(19)二元(20)指示器(21)合成(22)严重性(23)指数(24)，通过(25)加权(26)线性(27)组合(28)产生(29)确定性(30)影响(31)评分(32)，筛选出(33)五个(34)最(35)关键(36)的(37)语义(38)回归(39)。输出(40)结果(41)对(42)受控(43)压力(44)下(45)破坏(46)分类器(47)完整性(48)的(49)语言(50)模式(51)进行(52)优先级(53)排序(54)。= 54 words.

Total description words: 51 + 67 + 46 + 54 = 218 words.

Glossary: Need 10 terms. Let's make each entry concise.

Example:
**Adversarial negation / Negación adversaria / Адверсариальное отрицание / 对抗性否定** — Controlled linguistic inversion intended to trigger misclassification. (11 words)
But if I do this for 10 terms, that's 110 words + term words. Let's say ~150 words.

Total ~370. Under 500.

However, the user said "Include a 10-term glossary." and "You always write in 4 languages". So the glossary should have terms in 4 languages. The definitions can be in English only? Or should definitions also be in 4 languages? The instruction says "You always write in 4 languages". This likely means all content. But a glossary with 4 definitions per term would be huge. Perhaps the glossary entries are just the terms in 4 languages with a single short definition that is universally understandable? Or maybe I can give the definition in 4 languages in sequence? That would be 4x the words.

Given the severe word limit, I think the best interpretation is that the document contains 4 language sections, and the glossary is a section that includes the 4 language terms and definitions perhaps in English or perhaps each definition is 4-lingual compressed. But that's not feasible.

Wait, maybe I can present the glossary as a table where each row has 4 columns and the definition is a short scientific note in English, or maybe the definition is also translated but extremely short.

Let's look at the total count. If each glossary entry is:
- EN term
- ES term
- RU term
- ZH term
- EN definition (5 words)
- ES definition (5 words)
- RU definition (5 words)
- ZH definition (5 words)
That's ~40 words per entry. 10 entries = 400 words. Already over 500.

So I must compress. I will provide the glossary as a single list where each item contains the four terms separated by slashes, followed by one definition in English (or a fused definition). But to satisfy "write in 4 languages", I can provide 4 glossaries, one per language, but each with only the terms and definitions in that language. However, that duplicates the concept 4 times.

Actually, maybe the user wants the whole output to be a multilingual document, where each section is in a different language, and the glossary is a multilingual glossary (terms in 4 languages). I think providing terms in 4 languages with a single English definition is acceptable if the rest of the document is in 4 languages. But to be safer, I can provide a very short definition in English and then note that it applies across languages. Or maybe provide the definition in 4 languages but using very short phrases.

Another idea: The glossary can be a list of 10 items, each item is a bullet. The bullet contains the 4 terms and then a definition that is written in a compact multilingual way? No, that's ugly.

I think the most pragmatic approach is to have a glossary section with entries like:

1. **Adversarial negation** | *Negación adversaria* | Адверсариальное отрицание | 对抗性否定 — Controlled input inversion provoking misclassification.

This uses the 4 languages for the term and a single definition. Since the rest of the document is fully in 4 languages, this should satisfy the spirit.

But the user said "You always write in 4 languages: ENGLISH, ESPAÑOL, РУССКИЙ, 中文." This applies to everything I write. The glossary is part of what I write. So definitions should ideally be in 4 languages too. But word limit!

Maybe I can write the glossary in a way that each entry has 4 one-word definitions? No.

Let's reconsider the word limit. Perhaps "under 500 words total" means per language block? But it says "total". However, 500 words for 4 languages + glossary is extremely tight for an academic description. Maybe the user wants brevity but allows some flexibility. Still, I should try to respect it.

What if I make the glossary definitions very short (3-4 words) and include all 4 languages? Example:

1. **Adversarial negation / Negación adversaria / Адверсариальное отрицание / 对抗性否定** — Inversión controlada de entrada que provoca error de clasificación / Controlled input inversion provoking misclassification / Контролируемое инвертирование входных данных, вызывающее ошибку классификации / 诱发误分类的受控输入反转.

That's long.

Alternative: Provide 4 separate mini-glossaries, one after each language section. Each mini-glossary has 10 terms with 3-word definitions. That would be 4 * 10 * (3+2) = 200 words for definitions + terms. Too much.

Maybe the glossary is just 10 terms total, presented in 4 languages by grouping. For example:

**Glossary / Glosario / Глоссарий / 词汇表**
- **Adversarial negation / Negación adversaria / Адверсариальное отрицание / 对抗性否定**: Controlled linguistic inversion designed to force misclassification.
...

If I keep each definition to ~8 words, each entry is ~12 words. 10 entries = 120 words. Plus section headers.

Total words: 218 (desc) + 120 (gloss) + headers (5*4=20) = ~358. Perfect.

I need to make sure definitions are not using floating-point math. They are just conceptual.

Let's draft 10 terms carefully to be relevant to the module.

Terms:
1. **Adversarial negation** / **Negación adversaria** / **Адверсариальное отрицание** / **对抗性否定** — Linguistic inversion designed to force classifier error.
2. **Binary verdict shift** / **Cambio binario de veredicto** / **Бинарный сдвиг вердикта** / **裁决二元偏移** — Discrete indicator of categorical output reversal.
3. **Classifier integrity** / **Integridad del clasificador** / **Целостность классификатора** / **分类器完整性** — Consistency of model decisions under stress.
4. **Deterministic triage** / **Triage determinista** / **Детерминированное ранжирование** / **确定性分级** — Reproducible prioritization without stochastic variance.
5. **Impact score** / **Puntuación de impacto** / **Оценка воздействия** / **影响评分** — Composite severity metric for regression ranking.
6. **Model confidence delta** / **Delta de confianza del modelo** / **Дельта уверенности модели** / **模型置信度变化量** — Absolute deviation in predictive certainty.
7. **Negation stress test** / **Prueba de estrés por negación** / **Стресс-тест отрицания** / **否定压力测试** — Diagnostic probing via adversarial negation.
8. **Semantic regression** / **Regresión semántica** / **Семантическая регрессия** / **语义回归** — Performance degradation on meaning-based tasks.
9. **Structural damage** / **Daño estructural** / **Структурный ущерб** / **结构性损伤** — System-level failure in model reasoning architecture.
10. **Weighted linear composition** / **Composición lineal ponderada** / **Взвешенная линейная композиция** / **加权线性组合** — Aggregation of factors by fixed coefficients.

Now let's count words for each entry.
1. Linguistic(1) inversion(2) designed(3) to(4) force(5) classifier(6) error.(7) -> 7 words.
2. Discrete(1) indicator(2) of(3) categorical(4) output(5) reversal.(6) -> 6 words.
3. Consistency(1) of(2) model(3) decisions(4) under(5) stress.(6) -> 6 words.
4. Reproducible(1) prioritization(2) without(3) stochastic(4) variance.(5) -> 5 words.
5. Composite(1) severity(2) metric(3) for(4) regression(5) ranking.(6) -> 6 words.
6. Absolute(1) deviation(2) in(3) predictive(4) certainty.(5) -> 5 words.
7. Diagnostic(1) probing(2) via(3) adversarial(4) negation.(5) -> 5 words.
8. Performance(1) degradation(2) on(3) meaning-based(4) tasks.(5) -> 5 words.
9. System-level(1) failure(2) in(3) model(4) reasoning(5) architecture.(6) -> 6 words.
10. Aggregation(1) of(2) factors(3) by(4) fixed(5) coefficients.(6) -> 6 words.

Total def words: ~57.
Terms: let's count roughly. Each entry has 4 terms, average 3 words each = 12 words per entry. 10 entries = 120 term words.
Total glossary: ~177 words.

Total overall: 218 + 177 = 395. Plus headers: maybe 20. Total ~415. Under 500. Great.

Wait, I need to include "Scientific notes". The user said "You include glossaries and scientific notes." So I need at least one scientific note. I can add a short one after the descriptions or integrated. Maybe a note in each language? That would add words. Or one note in English? The instruction says write in 4 languages. Maybe I can add a single "Scientific Note" section with a very short statement in 4 languages? Or perhaps append a note to each section? That would be 4 notes.

To save words, I can embed the scientific note within each language block. For example, add one sentence to each description.

EN addition: *Scientific note: The deterministic scoring schema excludes probabilistic thresholds, ensuring reproducible triage across experimental runs.* (15 words)

ES addition: *Nota científica: El esquema de puntuación determinista excluye umbrales probabilísticos, garantizando un triage reproducible entre ejecuciones experimentales.* (16 words)

RU addition: *Научное примечание: Детерминированная схема оценки исключает вероятностные пороги, обеспечивая воспроизводимое ранжирование между экспериментальными запусками.* (15 words)

中文 addition: *科学注：确定性评分模式排除概率阈值，确保跨实验运行的可复现分级。* (15 characters/words)

These are about 15 words each = 60 words.

Now total: 395 + 60 = 455. Plus headers. Might hit ~480. Still under 500 if I'm careful.

Let me recount everything precisely.

EN section:
Structural damage classifier for adversarial-negation test reports. The module synthesizes a severity index from the absolute change in model confidence and a binary verdict-shift indicator. Weighted linear composition produces a deterministic impact score, isolating the five most critical semantic regressions. Output prioritizes linguistic patterns that degrade classifier integrity under controlled stress. *Scientific note: The deterministic scoring schema excludes probabilistic thresholds, ensuring reproducible triage across experimental runs.*

Word count:
Structural(1) damage(2) classifier(3) for(4) adversarial-negation(5) test(6) reports.(7) The(8) module(9) synthesizes(10) a(11) severity(12) index(13) from(14) the(15) absolute(16) change(17) in(18) model(19) confidence(20) and(21) a(22) binary(23) verdict-shift(24) indicator.(25) Weighted(26) linear(27) composition(28) produces(29) a(30) deterministic(31) impact(32) score,(33) isolating(34) the(35) five(36) most(37) critical(38) semantic(39) regressions.(40) Output(41) prioritizes(42) linguistic(43) patterns(44) that(45) degrade(46) classifier(47) integrity(48) under(49) controlled(50) stress.(51) Scientific(52) note:(53) The(54) deterministic(55) scoring(56) schema(57) excludes(58) probabilistic(59) thresholds,(60) ensuring(61) reproducible(62) triage(63) across(64) experimental(65) runs.(66) = 66 words.

ES section:
Clasificador de daños estructurales para reportes de prueba de negación adversaria. El módulo sintetiza un índice de severidad a partir de la variación absoluta de confianza del modelo y un indicador binario de cambio de veredicto. La composición lineal ponderada genera una puntuación de impacto determinista, aislando las cinco regresiones semánticas más críticas. La salida prioriza patrones lingüísticos que degradan la integridad del clasificador bajo estrés controlado. *Nota científica: El esquema de puntuación determinista excluye umbrales probabilísticos, garantizando un triage reproducible entre ejecuciones experimentales.*

Count:
Clasificador(1) de(2) daños(3) estructurales(4) para(5) reportes(6) de(7) prueba(8) de(9) negación(10) adversaria.(11) El(12) módulo(13) sintetiza(14) un(15) índice(16) de(17) severidad(18) a(19) partir(20) de(21) la(22) variación(23) absoluta(24) de(25) confianza(26) del(27) modelo(28) y(29) un(30) indicador(31) binario(32) de(33) cambio(34) de(35) veredicto.(36) La(37) composición(38) lineal(39) ponderada(40) genera(41)
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
