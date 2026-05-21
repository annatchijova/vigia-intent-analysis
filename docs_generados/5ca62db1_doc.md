<!--
VIGIA Academic Documentation
Module: 5ca62db1
Batch ID: vigia-doc-0167-5ca62db1
Generated: 2026-05-20T14:56:47.880708+00:00
-->

The user wants a brief academic description of a VIGIA support module (`vigia/tools/nlp_constants.py`) in 4 languages (EN, ES, RU, 中文). Constraints:

- Under 500 words total (across all 4 languages? Or total? Usually "total" means combined word count for all languages should be <500. This is tight. Need to be very concise.)
- Include a 10-term glossary.
- Academic technical writer specializing in digital forensics.
- Audience: scientists who do not know Python.
- NEVER use floating-point math explanations for deterministic systems.
- Include glossaries and scientific notes.
- The content summary: lexical constants and base types for forensic NLP analysis. Extracted from adversarial_nlp_pericial_EN_ES.py. Diagnosis: these constants were UNDEFINED in the original file — the module used them at line 50.

Need to structure:
1. Description in EN
2. Description in ES
3. Description in RU
4. Description in 中文
5. Glossary (10 terms) — probably multilingual or one glossary with terms defined? The prompt says "Include a 10-term glossary." Since it's for scientists and 4 languages, likely a table or list with terms in all languages or a glossary section. But word count is strict (<500 total). A glossary of 10 terms with definitions will eat words. Need extreme brevity.

Let's calculate approximate word budget:

Total < 500 words.

If 4 language sections + glossary.

Maybe:
- EN: ~70 words
- ES: ~70 words
- RU: ~70 words
- 中文: ~70 words (Chinese characters count as words? Usually word count in Chinese is characters or just the text. But to be safe, keep each section very short.)
- Glossary: ~10 terms x ~8 words each = ~80 words.
Total ~360-430 words. That works.

Need to avoid Python jargon. Explain it as a "support module" defining "lexical constants and base types" for forensic NLP. Mention that it resolves undefined references discovered at line 50 of the source file. Frame as "deterministic lexical anchors" or "controlled vocabulary".

Since the audience doesn't know Python, don't mention line numbers or files as code, but as "source extraction" and "diagnostic correction". Use scientific tone.

Let's draft each section.

EN:
`vigia/tools/nlp_constants.py` is a forensic NLP support module that establishes a deterministic controlled vocabulary of lexical constants and base types. Extracted from the adversarial forensic NLP source, it resolves previously undefined symbolic references detected at line 50. By codifying immutable lexical anchors—such as tag sets, regular-expression signatures, and semantic category labels—the module ensures reproducible text analysis across examinations. It functions as a terminological substrate: non-computational scientists may regard it as a fixed glossary that standardizes input to downstream forensic linguistic pipelines, eliminating source-level indeterminacy without altering evidentiary semantics.

Word count EN: ~78 words. Good.

ES:
`vigia/tools/nlp_constants.py` es un módulo de soporte para NLP forense que establece un vocabulario controlado determinista de constantes léxicas y tipos base. Extraído del fuente de NLP pericial adversarial, resuelve referencias simbólicas previamente indefinidas detectadas en la línea 50. Al codificar anclas léxicas inmutables—conjuntos de etiquetas, firmas de expresiones regulares y etiquetas semánticas—garantiza análisis textuales reproducibles. Los científicos no informáticos pueden considerarlo un glosario fijo que estandariza la entrada de pipelines lingüísticos forenses, eliminando la indeterminación sin alterar la semántica probatoria.

Word count ES: ~75 words.

RU:
`vigia/tools/nlp_constants.py` — вспомогательный модуль судебной лингвистической экспертизы, задающий детерминированный контролируемый словарь лексических констант и базовых типов. Извлечён из исходного кода адверсарного судебного NLP; устраняет ранее неопределённые символьные ссылки, выявленные в строке 50. Кодифицируя неизменяемые лексические якоря — наборы меток, сигнатуры регулярных выражений и семантические категории — он обеспечивает воспроизводимый текстовый анализ. Не-программисты могут воспринимать модуль как фиксированный глоссарий, стандартизирующий входные данные для судебных лингвистических конвейеров.

Word count RU: ~72 words.

中文:
`vigia/tools/nlp_constants.py` 是数字取证自然语言处理的支撑模块，用于建立确定性的受控词汇表与基础语义类型。该模块提取自对抗性取证 NLP 源文件，修复了原第 50 行处未定义的符号引用。通过将标签集、正则表达式特征与语义类别标签编码为不可变的词汇锚点，它确保文本分析具备可重复性。非计算机背景科学家可将其视为固定术语表，为下游法医语言分析流程提供标准化输入，在不改变证据语义的前提下消除源级不确定性。

Word count 中文: ~120 characters, but in "words" maybe ~80 if counting each character/phrase. Actually Chinese word count is tricky, but the text is concise. Let's assume it's okay.

Now glossary. Need 10 terms. Must be scientific and relevant. Can present as a list. To save words, define briefly.

Terms:
1. Controlled vocabulary / Vocabulario controlado / Контролируемый словарь / 受控词汇表
2. Lexical anchor / Ancla léxica / Лексический якорь / 词汇锚点
3. Deterministic system / Sistema determinista / Детерминированная система / 确定性系统
4. Forensic NLP / NLP forense / Судебный NLP / 取证自然语言处理
5. Symbolic reference / Referencia simbólica / Символьная ссылка / 符号引用
6. Source-level indeterminacy / Indeterminación a nivel fuente / Неопределённость на уровне исходного кода / 源级不确定性
7. Regular-expression signature / Firma de expresión regular / Сигнатура регулярного выражения / 正则表达式特征
8. Semantic category label / Etiqueta de categoría semántica / Семантическая метка категории / 语义类别标签
9. Reproducible analysis / Análisis reproducible / Воспроизводимый анализ / 可重复分析
10. Evidentiary semantics / Semántica probatoria / Доказательственная семантика / 证据语义

Definitions need to be very short.

Example:
- **Controlled vocabulary**: A closed, authoritative set of terms that constrains analysis inputs to prevent ambiguity.
- **Lexical anchor**: An immutable token or pattern used to fix semantic meaning within a corpus.
- **Deterministic system**: A process where identical inputs always yield identical outputs, excluding probabilistic variation.
- **Forensic NLP**: The application of natural language processing to evidentiary text under chain-of-custody constraints.
- **Symbolic reference**: A named identifier pointing to a data object; undefined references cause system failure.
- **Source-level indeterminacy**: Uncertainty arising from missing or unresolved declarations in analytical code.
- **Regular-expression signature**: A formal pattern describing invariant textual structures for automated recognition.
- **Semantic category label**: A classification tag assigning conceptual domain membership to a token or phrase.
- **Reproducible analysis**: An examination protocol yielding consistent results when repeated under the same conditions.
- **Evidentiary semantics**: The stable meaning content of a text item as presented in legal proceedings.

Let's count words for glossary:
Each definition is about 15-20 words. 10 terms = ~170 words. That might push total over 500.

Need to cut down drastically.

Let's make definitions ~8-10 words.

1. **Controlled vocabulary**: Closed set of authorized terms that prevents analytical ambiguity. (10)
2. **Lexical anchor**: Immutable token fixing semantic meaning within a corpus. (9)
3. **Deterministic system**: Process where identical inputs always produce identical outputs. (9)
4. **Forensic NLP**: Application of language analysis to evidentiary text under legal custody. (11)
5. **Symbolic reference**: Named identifier pointing to a data object in code. (9)
6. **Source-level indeterminacy**: Uncertainty from missing declarations in analytical source code. (9)
7. **Regular-expression signature**: Formal pattern describing invariant textual structures. (8)
8. **Semantic category label**: Classification tag assigning conceptual domain to a phrase. (9)
9. **Reproducible analysis**: Protocol yielding consistent results under repeated identical conditions. (9)
10. **Evidentiary semantics**: Stable meaning content of a text item in legal proceedings. (10)

Total glossary words: ~94.

Now sum all sections:
EN: ~78
ES: ~75
RU: ~72
中文: ~85 (approx)
Glossary: ~94
Total: ~404 words. Well under 500. Good.

Need to ensure no floating-point math explanations. None used.

Need to include "scientific notes". Perhaps add a small [Scientific Note] after one of the sections, or within. But word count is tight. Maybe add a single scientific note in the EN section or as a separate small italic line? The user said "Include glossaries and scientific notes." Plural notes? Could be tricky with word count. Maybe one note appended to EN or ES.

Let's integrate a brief scientific note in EN and RU or just one. Actually I can add a [Nota científica / Научное примечание / 科学注] as a one-liner in each language? That would multiply words. Better to have one scientific note in English or as a separate short line that is translated? The prompt doesn't specify notes must be in all languages, but since everything else is in 4 languages, maybe the note can be embedded in each language section. However, the sections themselves are already concise.

Alternative: make the descriptions slightly shorter and add a note line.

Let's trim EN to ~65 words.

EN:
`vigia/tools/nlp_constants.py` is a forensic NLP support module that establishes a deterministic controlled vocabulary of lexical constants and base types. Extracted from the adversarial forensic source, it resolves previously undefined symbolic references detected at line 50. By codifying immutable lexical anchors—tag sets, regular-expression signatures, and semantic category labels—it ensures reproducible text analysis. Non-computational scientists may regard it as a fixed glossary that standardizes input to downstream forensic linguistic pipelines, eliminating source-level indeterminacy without altering evidentiary semantics.

Word count: ~69.

ES:
`vigia/tools/nlp_constants.py` es un módulo de soporte para NLP forense que establece un vocabulario controlado determinista de constantes léxicas y tipos base. Extraído del fuente pericial adversarial, resuelve referencias simbólicas previamente indefinidas detectadas en la línea 50. Al codificar anclas léxicas inmutables—conjuntos de etiquetas, firmas de expresiones regulares y etiquetas semánticas—garantiza análisis textuales reproducibles. El módulo actúa como glosario fijo que estandariza la entrada de pipelines lingüísticos forenses, eliminando la indeterminación en origen sin alterar la semántica probatoria.

Word count: ~72.

RU:
`vigia/tools/nlp_constants.py` — вспомогательный модуль судебной лингвистической экспертизы, задающий детерминированный контролируемый словарь лексических констант и базовых типов. Извлечён из исходного кода адверсарной судебной системы; устраняет ранее неопределённые символьные ссылки, выявленные в строке 50. Кодифицируя неизменяемые лексические якоря — наборы меток, сигнатуры регулярных выражений, семантические категории — он обеспечивает воспроизводимый текстовый анализ. Модуль выполняет роль фиксированного глоссария, стандартизируя входные данные для судебных лингвистических конвейеров.

Word count: ~71.

中文:
`vigia/tools/nlp_constants.py` 是数字取证 NLP 支撑模块，用于建立确定性的受控词汇表与基础语义类型。该模块提取自对抗性取证源文件，修复了原第 50 行未定义的符号引用。通过将标签集、正则表达式特征与语义类别编码为不可变词汇锚点，确保文本分析可重复。非计算机背景科学家可将其视为固定术语表，为下游法医语言流程提供标准化输入，在不改变证据语义的前提下消除源级不确定性。

Word count: ~95 Chinese characters, which is about 70-80 "words" if counting each character as a word. Usually Chinese word count is by characters. Let's assume okay.

Now scientific notes. I can add a short bracketed note after each text? E.g.

EN: [Scientific note: This correction removes lexical entropy from the forensic pipeline by binding all tokens to a priori definitions.]

That's 16 words. If I add to each language, it's too much. Maybe add one note total, in English only? The prompt says "Include glossaries and scientific notes." It doesn't explicitly say notes must be in all 4 languages, but it's safer to include them in each. However, word count <500 total is very strict.

Wait, "Keep it under 500 words total." This likely counts everything: all 4 languages + glossary. Chinese characters might be counted differently by the user. But to be safe, let's aim for ~450 English-equivalent words.

I could add a very short scientific note in each language, 5-6 words each.

EN: *Scientific note: Removes lexical entropy via a priori definitions.* (9 words)
ES: *Nota científica: Elimina entropía léxica mediante definiciones a priori.* (9 words)
RU: *Научное примечание: устраняет лексическую энтропию через априорные определения.* (8 words)
中文: *科学注：通过先验定义消除词汇熵。* (9 characters, ~9 words)

That's manageable.

Let's recount with notes:

EN: 69 + 9 = 78
ES: 72 + 9 = 81
RU: 71 + 8 = 79
中文: ~95 characters + ~9 = ~104 char
Glossary: ~94

Total: ~436. Still under 500. Good.

Wait, the user said "You NEVER use floating-point math explanations for deterministic systems." I didn't. Good.

Also "You include glossaries and scientific notes." I'm doing that.

Need to make sure I don't use Python jargon like "module" in a way that assumes knowledge. I used "module" and "source" and "line 50". For scientists who don't know Python, "line 50" might be too code-specific. But the prompt explicitly mentions line 50 and diagnosis. I can say "detected at position line 50" or "at the 50th line of the source". Maybe keep it but frame as diagnostic location. It's okay.

Actually, the user said "Module: vigia/tools/nlp_constants.py" and the content summary. It's okay to refer to the file path as the module identifier.

Let's refine the glossary format. Since it's 4 languages, a table might be best but plain text is okay. I can present each term in 4 languages with a single definition in English? No, the audience is scientists who read all 4 languages? The prompt asks to write in 4 languages, so probably the glossary should have translations. But to save words, I can list the term in 4 languages and then one definition.

Example:

1. **Controlled vocabulary / Vocabulario controlado / Контролируемый словарь / 受控词汇表** — Closed set of authorized terms preventing analytical ambiguity.

This is concise.

Let's do that.

1. **Controlled vocabulary / Vocabulario controlado / Контролируемый словарь / 受控词汇表** — Closed set of authorized terms preventing analytical ambiguity. (11)
2. **Lexical anchor / Ancla léxica / Лексический якорь / 词汇锚点** — Immutable token fixing semantic meaning within a corpus. (9)
3. **Deterministic system / Sistema determinista / Детерминированная система / 确定性系统** — Process where identical inputs always produce identical outputs. (9)
4. **Forensic NLP / NLP forense / Судебный NLP / 取证自然语言处理** — Language analysis applied to evidentiary text under legal custody. (10)
5. **Symbolic reference / Referencia simbólica / Символьная ссылка / 符号引用** — Named identifier pointing to a data object in source code. (10)
6. **Source-level indeterminacy / Indeterminación en origen / Неопределённость уровня исходного кода / 源级不确定性** — Uncertainty arising from missing declarations in analytical code. (10)
7. **Regular-expression signature / Firma de expresión regular / Сигнатура регулярного выражения / 正则表达式特征** — Formal pattern describing invariant textual structures. (8)
8. **Semantic category label / Etiqueta de categoría semántica / Семантическая метка категории / 语义类别标签** — Classification tag assigning conceptual domain to a phrase. (9)
9. **Reproducible analysis / Análisis reproducible / Воспроизводимый анализ / 可重复分析** — Protocol yielding consistent results under repeated identical conditions. (9)
10. **Evidentiary semantics / Semántica probatoria / Доказательственная семантика / 证据语义** — Stable meaning content of a text item in legal proceedings. (10)

Total glossary words: ~95.

Now let's assemble and do a final word count check.

EN section:
`vigia/tools/nlp_constants.py` is a forensic NLP support module that establishes a deterministic controlled vocabulary of lexical constants and base types. Extracted from the adversarial forensic source, it resolves previously undefined symbolic references detected at line 50. By codifying immutable lexical anchors—tag sets, regular-expression signatures, and semantic category labels—it ensures reproducible text analysis. Non-computational scientists may regard it as a fixed glossary that standardizes input to downstream forensic linguistic pipelines, eliminating source-level indeterminacy without altering evidentiary semantics.
*Scientific note: Removes lexical entropy via a priori definitions.*

Count:
is(1) a(2) forensic(3) NLP(4) support(5) module(6) that(7) establishes(8) a(9) deterministic(10) controlled(11) vocabulary(12) of(13) lexical(14) constants(15) and(16) base(17) types.(18) Extracted(19) from(20) the(21) adversarial(22) forensic(23) source,(24) it(25) resolves(26) previously(27) undefined(28) symbolic(29) references(30) detected(31) at(32) line(33) 50.(34) By(35) codifying(36) immutable(37) lexical(38) anchors—tag(39) sets,(40) regular-expression(41) signatures,(42) and(43) semantic(44) category(45) labels—it(46) ensures(47) reproducible(48) text(49) analysis.(50) Non-computational(51) scientists(52) may(53) regard(54) it(55) as(56) a(57) fixed(58) glossary(59) that(60) standardizes(61) input(62) to(63) downstream(64) forensic(65) linguistic(66) pipelines,(67) eliminating(68) source-level(69) indeterminacy(70) without(71) altering(72) evidentiary(73) semantics.(74)
Scientific(75) note:(76) Removes(77) lexical(78) entropy(79) via(80) a(81) priori(82) definitions.(83)
= 83 words.

ES section:
`vigia/tools/nlp_constants.py` es un módulo de soporte para NLP forense que establece un vocabulario controlado determinista de constantes léxicas y tipos base. Extraído del fuente pericial adversarial, resuelve referencias simbólicas previamente indefinidas detectadas en la línea 50. Al codificar anclas léxicas inmutables—conjuntos de etiquetas, firmas de expresiones regulares y etiquetas semánticas—garantiza análisis textuales reproducibles. El módulo actúa como glosario fijo que estandariza la entrada de pipelines lingüísticos forenses, eliminando la indeterminación en origen sin alterar la semántica probatoria.
*Nota científica: Elimina entropía léxica mediante definiciones a priori.*

Count:
es(1) un(2) módulo(3) de(4) soporte(5) para(6) NLP(7) forense(8) que(9) establece(10) un(11) vocabulario(12) controlado(13) determinista(14) de(15) constantes(16) léxicas(17) y(18) tipos(19) base.(20) Extraído(21) del(22) fuente(23) pericial(24) adversarial,(25) resuelve(26) referencias(27) simbólicas(28) previamente(29) indefinidas(30) detectadas(31) en(32) la(33) línea(34) 50.(35) Al(36) codificar(37) anclas(38) léxicas(39) inmutables—conjuntos(40) de(41) etiquetas,(42) firmas(43) de(44) expresiones(45) regulares(46) y(47) etiquetas(48) semánticas—garantiza(49) análisis(50) textuales(51) reproducibles.(52) El(53) módulo(54) actúa(55) como(56) glosario(57) fijo(58) que(59) estandariza(60) la(61) entrada(62) de(63) pipelines(64) lingüísticos(65) forenses,(66) eliminando(67) la(68) indeterminación(69) en(70) origen(71) sin(72) alterar(73) la(74) semántica(75) probatoria.(76)
Nota(77) científica:(78) Elimina(79) entropía(80) léxica(81) mediante(82) definiciones(83) a(84) priori.(85)
= 85 words.

RU section:
`vigia/tools/nlp_constants.py` — вспомогательный модуль судебной лингвистической экспертизы, задающий детерминированный контролируемый словарь лексических констант и базовых типов. Извлечён из исходного кода адверсарной судебной системы; устраняет ранее неопределённые символьные ссылки, выявленные в строке 50. Кодифицируя неизменяемые лексические якоря — наборы меток, сигнатуры регулярных выражений, семантические категории — он обеспечивает воспроизводимый текстовый анализ. Модуль выполняет роль фиксированного глоссария, стандартизируя входные данные для судебных лингвистических конвейеров.
*Научное примечание: устраняет лексическую энтропию через априорные определения.*

Count:
вспомогательный(1) модуль(2) судебной(3) лингвистической(4) экспертизы,(5) задающий(6) детерминированный(7) контролируемый(8) словарь(9) лексических(10) констант(11) и(12) базовых(13) типов.(14) Извлечён(15) из(16) исходного(17) кода(18) адверсарной(19) судебной(20) системы;(21) устраняет(22) ранее(23) неопределённые(24) символьные(25) ссылки,(26) выявленные(27) в(28) строке(29) 50.(30) Кодифицируя(31) неизменяемые(32) лексические(33) якоря(34) —(35) наборы(36) меток,(37) сигнатуры(38) регулярных(39) выражений,(40) семантические(41) категории(42) —(43) он(44) обеспечивает(45) воспроизводимый(46) текстовый(47) анализ.(48) Модуль(49) выполняет(50) роль(51) фиксированного(52) глоссария,(53) стандартизируя(54) входные(55) данные(56) для(57) судебных(58) лингвистических(59) конвейеров.(60)
Научное(61) примечание:(62) устраняет(63) лексическую(64) энтропию(65) через(66) априорные(67) определения.(68)
= 68 words.

中文 section:
`vigia/tools/nlp_constants.py` 是数字取证 NLP 支撑模块，用于建立确定性的受控词汇表与基础语义类型。该模块提取自对抗性取证源文件，修复了原第 50 行未定义的符号引用。通过将标签集、正则表达式特征与语义类别编码为不可变词汇锚点，确保文本分析可重复。非计算机背景科学家可将其视为固定术语表，为下游法医语言流程提供标准化输入，在不改变证据语义的前提下消除源级不确定性。
*科学注：通过先验定义消除词汇熵。*

Chinese word count: If counting characters as words: 是(1) 数字(2) 取证(3) NLP(4) 支撑(5) 模块(6)，(7) 用于(8) 建立(9) 确定性(10) 的(11) 受控(12) 词汇表(13) 与(14) 基础(15) 语义(16) 类型(17)。(18) 该(19) 模块(20) 提取(21) 自(22) 对抗性(23) 取证(24) 源文件(25)，(26) 修复(27) 了(28) 原(29) 第(30) 50(31) 行(32) 未定义(33) 的(34) 符号(35) 引用(36)。(37) 通过(38) 将(39) 标签集(40)、(41) 正则表达式(42) 特征(43) 与(44) 语义(45) 类别(46) 编码(47) 为(48) 不可变(49) 词汇(50) 锚点(51)，(52) 确保(53) 文本(54) 分析(55) 可重复(56)。(57) 非(58) 计算机(59) 背景(60) 科学家(61) 可(62) 将(63) 其(64) 视为(65) 固定(66) 术语表(67)，(68) 为(69) 下游(70) 法医(71) 语言(72) 流程(73) 提供(74) 标准化(75) 输入(76)，(77) 在(78) 不(79) 改变(80) 证据(81) 语义(82) 的(83) 前提(84) 下(85) 消除(86) 源级(87) 不确定性(88)。(89)
科学注(90)：通过(91) 先验(92) 定义(93) 消除(94) 词汇熵(95)。(96)
~96 "words" (characters/punctuation units).

Glossary: Let's count.

1. Controlled vocabulary / Vocabulario controlado / Контролируемый словарь / 受控词汇表 — Closed set of authorized terms preventing analytical ambiguity. (14)
2. Lexical anchor / Ancla léxica / Лексический якорь / 词汇锚点 — Immutable token fixing semantic meaning within a corpus. (12)
3. Deterministic system / Sistema determinista / Детерминированная система / 确定性系统 — Process where identical inputs always produce identical outputs. (12)
4. Forensic NLP / NLP forense / Судебный NLP / 取证自然语言处理 — Language analysis applied to evidentiary text under legal custody. (13)
5. Symbolic reference / Referencia simbólica / Символьная ссылка / 符号引用 — Named identifier pointing to a data object in source code. (14)
6. Source-level indeterminacy / Indeterminación en origen / Неопределённость уровня исходного кода / 源级不确定性 — Uncertainty arising from missing declarations in analytical code. (13)
7. Regular-expression signature / Firma de expresión regular / Сигнатура регулярного выражения / 正则表达式特征 — Formal pattern describing invariant textual structures. (10)
8. Semantic category label / Etiqueta de categoría semántica / Семантическая метка категории / 语义类别标签 — Classification tag assigning conceptual domain to a phrase. (12)
9. Reproducible analysis / Análisis reproducible / Воспроизводимый анализ / 可重复分析 — Protocol yielding consistent results under repeated identical conditions. (12)
10. Evidentiary semantics / Semántica probatoria / Доказательственная семантика / 证据语义 — Stable meaning content of a text item in legal proceedings. (12)

Total glossary: ~124 words.

Now sum:
EN: 83
ES: 85
RU: 68
中文: 96
Glossary: 124
Total: ~456 words.

Under 500. Perfect.

One concern: The user said "You NEVER use floating-point math explanations for deterministic systems." I haven't. Also, the system prompt says I write for scientists who do not know Python. I used "line 50", "module", "source code" (in RU). For scientists, "line 50" might be okay as a diagnostic coordinate, but maybe rephrase to avoid code-centric jargon? However, the prompt explicitly says "the module las usaba en línea 50". It's part of the diagnosis. I think it's acceptable to mention "line 50" as the diagnostic locus.

But to be safer for non-Python scientists, in EN I said "detected at line 50". In ES "detectadas en la línea 50". In RU "в строке 50". In 中文 "原第 50 行". That seems fine.

Let's check the tone: Academic, technical, digital forensics. Good.

Final check on glossary terms: Are there exactly 10? Yes.

Are there scientific notes? Yes, one per language section.

Are there glossaries? Yes.

Are all 4 languages present? Yes.

Is total under 500 words? Yes, ~456.

One final thing: In the Chinese section, I used "法医语言流程" for forensic linguistic pipelines. That's okay. Or "法医语言分析流程". The current text has "法医语言流程". It's fine.

Let's refine the Chinese text slightly for better flow:

`vigia/tools/nlp_constants.py` 是数字取证 NLP 支撑模块，用于建立确定性的受控词汇表与基础语义类型。该模块提取自对抗性取证源文件，修复了原第 50 行未定义的符号引用。通过将标签集、正则表达式特征与语义类别编码为不可变词汇锚点，确保文本分析可重复。非计算机背景科学家可将其视为固定术语表，为下游法医语言流程提供标准化输入，在不改变证据语义的前提下消除源级不确定性。
*科学注：通过先验定义消除词汇熵。*

Yes.

Now, formatting. I will present each language section with its note. Then the glossary.

Potential issue: The prompt says "You always write in 4 languages: ENGLISH, ESPAÑOL, РУССКИЙ, 中文." So I should label them clearly.

Let's write the final output.

Structure:

**ENGLISH**
[text]
*Scientific note: ...*

**ESPAÑOL**
[text]
*Nota científica: ...*

**РУССКИЙ**
[text]
*Научное примечание: ...*

**中文**
[text]
*科学注：...*

**Glossary / Glosario / Глоссарий / 词汇表**
1. ...
...

This adds 8 header words. Still under 500.

Headers:
ENGLISH (1)
ESPAÑOL (1)
РУССКИЙ (1)
中文 (1)
Glossary / Glosario / Глоссарий / 词汇表 (4) = 8 words.

Total ~464. Still safe.

Let's ensure no Python code blocks or backticks? The user used backticks for file path. I can use italics or plain text. Backticks are okay but might look code-ish. I'll use plain text without backticks to avoid Python associations, or just the path as a name. Actually, using the exact file path is fine as a proper noun identifier.

I will omit backticks to make it less code-like.

ENGLISH
vigia/tools/nlp_constants.py is a forensic NLP support module...

Actually, keep it as is but no code formatting.

One more check: "floating-point math explanations for deterministic systems" — I must not explain determinism via floating point. I don't. I mention deterministic as a property. That's fine.

Let's finalize.

Word count sanity check one more time:

ENGLISH
vigia/tools/nlp_constants.py is a forensic NLP support module that establishes a deterministic controlled vocabulary of lexical constants and base types. Extracted from the adversarial forensic source, it resolves previously undefined symbolic references detected at line 50. By codifying immutable lexical anchors—tag sets, regular-expression signatures, and semantic category labels—it ensures reproducible text analysis. Non-computational scientists may regard it as a fixed glossary that standardizes input to downstream forensic linguistic pipelines, eliminating source-level indeterminacy without altering evidentiary semantics.
Scientific note: Removes lexical entropy via a priori definitions.

Count:
vigia/tools/nlp_constants.py(1?) Usually hyphenated paths count as multiple words depending on counter. To be safe, I should consider "vigia/tools/nlp_constants.py" as ~3 words (separated by slashes). But word counters vary. Let's assume standard: punctuation/slashes separate words. So "vigia/tools/nlp_constants.py" = 3 words: vigia, tools, nlp_constants.py. Or maybe 1 if treated as a token. In most word processors, slashes are word separators. So add ~2 extra per section.

EN: +2 = 85
ES: +2 = 87
RU: +2 = 70 (no path in body? Actually I start with it). So +2 = 70.
中文: +2 = 98
Glossary: terms have slashes. Each term has 3 slashes, so 3 extra words per term = 30 extra.
Total extra ~36.

New total: 456 + 36 = 492. Still just under 500! Very close but okay.

If I want to be safer, I can remove the file path from the body and just refer to it
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
