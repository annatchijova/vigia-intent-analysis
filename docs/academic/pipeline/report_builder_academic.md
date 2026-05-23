<!--
VIGIA Academic Documentation
Module: 10a8df9f
Batch ID: vigia-doc-0112-10a8df9f
Generated: 2026-05-20T14:56:47.868787+00:00
-->

---
doc_hash: 10a8df9f
module: unknown
languages: [ES, RU, ZH]
generated_by: moonshot-kimi-k2.6-batch-api
license: Apache-2.0
---

ESPAÑOL:
El módulo `report_builder` funciona como un componente de síntesis forense dentro de la tubería de procesamiento VIGIA. Agrega artefactos procesados—valores hash, entradas de cronología y metadatos extraídos—en un informe probatorio unificado. Opera de manera determinista para transformar resultados analíticos en una narrativa estructurada apta para revisión por pares y examen legal, preservando la cadena de custodia.

РУССКИЙ:
Модуль `report_builder` выступает в роли компонента судебного синтеза в конвейере обработки VIGIA. Он агрегирует обработанные артефакты—хеш-значения, временные метки и извлечённые метаданные—в единый доказательственный отчёт. Детерминированно преобразуя сырые аналитические данные в структурированное повествование, модуль обеспечивает сохранность документации цепочки хранения для экспертной и юридической проверки.

中文:
`report_builder` 模块是 VIGIA 处理流水线中的法医综合组件。它以确定性方式聚合已处理工件——包括哈希值、时间线条目与提取的元数据——生成统一证据报告。该模块将原始分析输出转化为结构化叙述，供同行评审与法律审查使用，并确保监管链文档完整无缺。

Word count check:
EN: 48 words
ES: 49 words
RU: 39 words (Russian words count differently, but let's assume word count by tokens/characters? Usually word count is language-agnostic count of words separated by spaces. Russian text is typically shorter in word count but denser. Let's check: Модуль(1) `report_builder`(2) выступает(3) в(4) роли(5) компонента(6) судебного(7) синтеза(8) в(9) конвейере(10) обработки(11) VIGIA.(12) Он(13) агрегирует(14) обработанные(15) артефакты—хеш-значения,(16) временные(17) метки(18) и(19) извлечённые(20) метаданные—в(21) единый(22) доказательственный(23) отчёт.(24) Детерминированно(25) преобразуя(26) сырые(27) аналитические(28) данные(29) в(30) структурированное(31) повествование,(32) модуль(33) обеспечивает(34) сохранность(35) документации(36) цепочки(37) хранения(38) для(39) экспертной(40) и(41) юридической(42) проверки.(43) = 43 words. Good.

ZH: Let's count: `report_builder`(1) 模块(2) 是(3) VIGIA(4) 处理(5) 流水线(6) 中的(7) 法医(8) 综合(9) 组件(10)。它(11) 以(12) 确定性(13) 方式(14) 聚合(15) 已处理(16) 工件(17)——包括(18) 哈希值(19)、时间线(20) 条目(21) 与(22) 提取(23) 的(24) 元数据(25)——生成(26) 统一(27) 证据(28) 报告(29)。该(30) 模块(31) 将(32) 原始(33) 分析(34) 输出(35) 转化(36) 为(37) 结构化(38) 叙述(39)，供(40) 同行(41) 评审(42) 与(43) 法律(44) 审查(45) 使用(46)，并(47) 确保(48) 监管链(49) 文档(50) 完整(51) 无缺(52)。(53) = 53 words.

Total so far: ~48+49+43+53 = 193 words. Very good. Leaves ~300 words for glossary.

Glossary needs 10 terms. Let's select terms relevant to digital forensics and the description:
1. Artifact (Artefacto / Артефакт / 工件)
2. Chain of custody (Cadena de custodia / Цепочка хранения / 监管链)
3. Deterministic system (Sistema determinista / Детерминированная система / 确定性系统)
4. Evidentiary report (Informe probatorio / Доказательственный отчёт / 证据报告)
5. Hash value (Valor hash / Хеш-значение / 哈希值)
6. Metadata (Metadatos / Метаданные / 元数据)
7. Pipeline (Tubería/Canalización / Конвейер обработки / 流水线)
8. Structured narrative (Narrativa estructurada / Структурированное повествование / 结构化叙述)
9. Timeline entries (Entradas de cronología / Временные метки / 时间线条目)
10. Peer review (Revisión por pares / Экспертная проверка / 同行评审)

Need to format glossary concisely. Since total word count must be under 500, each glossary entry should be around 10-15 words.

Let's draft entries:

1. **Artifact / Artefacto / Артефакт / 工件** — A digital object of investigative interest recovered from storage media. / Objeto digital de interés investigativo recuperado de medios de almacenamiento. / Цифровой объект, представляющий следственный интерес, извлечённый из носителей. / 从存储介质中恢复、具有调查价值的数字对象。

Wait, formatting glossary in 4 languages simultaneously or one term with 4 translations? The prompt says "Include a 10-term glossary." Since the whole document is in 4 languages, the glossary should probably provide each term in all 4 languages. But to save words, I can list the term in 4 languages and then a brief definition, maybe split by language? No, that would multiply words. Better: present the glossary as a table or list where each entry gives the term in 4 languages and one definition? But definitions should be in the target language ideally. However, with a 500-word limit, defining each term 4 times is impossible.

Alternative: The user might accept a glossary section where terms are presented in English, with equivalents noted, but the user asked for 4 languages throughout. Let's look at the instruction: "You always write in 4 languages: ENGLISH, ESPAÑOL, РУССКИЙ, 中文. You include glossaries and scientific notes." This suggests the whole output should contain these 4 languages. The glossary could have entries grouped by language. But that would be 40 entries (10 terms x 4 languages). Too long.

Better approach: Create a compact glossary where each line contains the term in 4 languages separated by slashes, followed by a brief definition in English (or perhaps 4 short definitions?). But to be fair to the 4-language requirement, maybe I can do a multilingual glossary where each entry is:
- Term EN / ES / RU / ZH: Definition EN. Definition ES. Definition RU. Definition ZH. (Too long).

Let's reconsider word count. The limit is 500 words. If I have 4 descriptive paragraphs (approx 200 words total) and 10 glossary entries, each entry must average 30 words across all 4 languages. That's about 7-8 words per language definition. That's feasible if I make them extremely concise, telegraphic style (acceptable in glossary format).

Example:
**Artifact / Artefacto / Артефакт / 工件** — Digital object recovered for examination. / Objeto digital recuperado para examen. / Цифровой объект, извлечённый для экспертизы. / 用于检验的恢复数字对象。

Let's count words for this entry:
EN def: 5 words
ES def: 5 words
RU def: 5 words
ZH def: 6 words (用于检验的恢复数字对象 = 7 characters but as words: 用于(1) 检验(2) 的(3) 恢复(4) 数字(5) 对象(6)). Actually in Chinese word counting, it's characters or space-separated tokens? Usually Chinese text word count is by characters or by natural segmentation. But to be safe, I'll keep it very short.

Let's try to draft 10 entries with ultra-short definitions.

Terms:
1. Artifact / Artefacto / Артефакт / 工件
2. Chain of Custody / Cadena de Custodia / Цепочка Хранения / 监管链
3. Deterministic Output / Salida Determinista / Детерминированный Вывод / 确定性输出
4. Evidentiary Report / Informe Probatorio / Доказательственный Отчёт / 证据报告
5. Hash Value / Valor Hash / Хеш-Значение / 哈希值
6. Metadata / Metadatos / Метаданные / 元数据
7. Processing Pipeline / Canalización de Procesamiento / Конвейер Обработки / 处理流水线
8. Structured Narrative / Narrativa Estructurada / Структурированное Повествование / 结构化叙述
9. Timeline Entry / Entrada de Cronología / Временная Метка / 时间线索引
10. Peer Review / Revisión por Pares / Экспертная Проверка / 同行评审

Definitions (keeping to ~5 words each language):

1. **Artifact / Artefacto / Артефакт / 工件**
   - EN: Recovered digital item for analysis.
   - ES: Elemento digital recuperado para análisis.
   - RU: Извлечённый цифровой объект анализа.
   - ZH: 用于分析的数字检材。

2. **Chain of Custody / Cadena de Custodia / Цепочка Хранения / 监管链**
   - EN: Documented evidence transfer history.
   - ES: Historial documentado de transferencia probatoria.
   - RU: Документированная история передачи доказательств.
   - ZH: 证据移交的 documented 历史。(Wait, don't mix languages). Use: 证据流转记录。 (4 words: 证据(1) 流转(2) 记录(3)) -> 证据流转记录 (3 words? If counting characters as words, it's 6 characters. But usually each character is a word in Chinese word count? No, in Chinese, word count can be ambiguous. I'll just keep it concise).

3. **Deterministic Output / Salida Determinista / Детерминированный Результат / 确定性输出**
   - EN: Reproducible result from fixed inputs.
   - ES: Resultado reproducible ante entradas fijas.
   - RU: Воспроизводимый результат при фиксированных входных данных.
   - ZH: 固定输入下的可复现结果。

4. **Evidentiary Report / Informe Probatorio / Доказательственный Отчёт / 证据报告**
   - EN: Formal findings for legal review.
   - ES: Hallazgos formales para revisión legal.
   - RU: Формализованные выводы для юридической проверки.
   - ZH: 供法律审查的正式发现。

5. **Hash Value / Valor Hash / Хеш-Значение / 哈希值**
   - EN: Fixed-length data fingerprint.
   - ES: Huella dactilar de datos de longitud fija.
   - RU: Контрольная сумма фиксированной длины.
   - ZH: 定长数据指纹。

6. **Metadata / Metadatos / Метаданные / 元数据**
   - EN: Contextual data describing files.
   - ES: Datos contextuales que describen archivos.
   - RU: Контекстуальные данные, описывающие файлы.
   - ZH: 描述文件的上下文数据。

7. **Processing Pipeline / Canalización de Procesamiento / Конвейер Обработки / 处理流水线**
   - EN: Sequential forensic analysis stages.
   - ES: Etapas secuenciales de análisis forense.
   - RU: Последовательные этапы судебного анализа.
   - ZH: 按序执行的分析阶段。

8. **Structured Narrative / Narrativa Estructurada / Структурированное Повествование / 结构化叙述**
   - EN: Organized factual presentation.
   - ES: Presentación factual organizada.
   - RU: Организованное изложение фактов.
   - ZH: 有组织的事实陈述。

9. **Timeline Entry / Entrada de Cronología / Временная Метка / 时间线条目**
   - EN: Timestamped event record.
   - ES: Registro de eventos con marca temporal.
   - RU: Запись события с временной меткой.
   - ZH: 带时间戳的事件记录。

10. **Peer Review / Revisión por Pares / Экспертная Проверка / 同行评审**
    - EN: Independent expert verification.
    - ES: Verificación independiente por expertos.
    - RU: Независимая экспертная верификация.
    - ZH: 独立专家核查。

Now let's estimate total word count.

Descriptions:
EN: 48 words.
ES: 49 words.
RU: 43 words.
ZH: 53 words.
Subtotal: 193 words.

Glossary entries:
Each entry has: Term line (~5-8 words across 4 languages) + 4 definitions (~5 words each) = ~28 words per entry.
10 entries = ~280 words.
Total = 473 words. This is under 500. Good.

Need to ensure I don't use floating-point math explanations. The glossary includes "Deterministic Output" but I won't mention floats.

Scientific note: I should add a brief scientific note. But word count is tight. Maybe incorporate it into the description? The prompt says "You include glossaries and scientific notes." It might mean as part of my general style, but given the strict 500-word limit, a full separate scientific note might be hard. I can add a small "Scientific Note" sentence in each language block or one note after the descriptions. Let's see if I can fit a brief note.

Maybe add after the descriptions, before glossary:
**Scientific Note / Nota Científica / Научное Примечание / 科学注释** — This module performs deterministic aggregation; output depends solely on input artifacts and pipeline state, with no stochastic sampling or floating-point approximations involved. / Este módulo realiza agregación determinista; la salida depende únicamente de los artefactos de entrada y del estado del canal, sin muestreo estocástico ni aproximaciones de punto flotante. / Данный модуль выполняет детерминированную агрегацию; вывод зависит исключительно от входных артефактов и состояния конвейера без стохастической выборки или аппроксимаций с плавающей точкой. / 该模块执行确定性聚合；输出仅取决于输入工件与流水线状态，不涉及随机采样或浮点近似。

Wait, the user said "You NEVER use floating-point math explanations for deterministic systems." So I should NOT mention floating-point approximations even to say they are absent? The instruction says "You NEVER use floating-point math explanations for deterministic systems." This could mean: do not explain deterministic systems using floating-point math concepts, or do not mention floating-point math at all when describing deterministic systems. To be safe, I should not mention floating-point at all. I can just say "deterministic aggregation; output is fully reproducible from input artifacts and pipeline state." No mention of floating-point.

Revised Scientific Note:
**Scientific Note / Nota Científica / Научное Примечание / 科学注释** — The module guarantees reproducible aggregation: identical inputs and pipeline states yield identical reports, excluding stochastic variability. / El módulo garantiza agregación reproducible: entradas y estados idénticos del canal producen informes idénticos, excluyendo variabilidad estocástica. / Модуль обеспечивает воспроизводимую агрегацию: идентичные входные данные и состояния конвейера дают идентичные отчёты без стохастической вариативности. / 该模块保证可复现聚合：相同输入与流水线状态产生相同报告，不存在随机变异。

Word count for note: EN(15), ES(16), RU(13), ZH(15). Total ~59 words.
193 + 59 = 252.
Glossary ~280. Total ~532. Slightly over.

Need to trim. Let's make glossary definitions slightly shorter, maybe 4 words each on average. Or remove the scientific note and integrate the reproducibility concept into the main text (which I already did: "Operating deterministically"). The descriptions already mention deterministic operation. That serves as the scientific note implicitly? The prompt says "You include glossaries and scientific notes." It might be safer to have a one-line scientific note shared across languages? But the 4-language requirement suggests everything should be in 4 languages.

Alternative: skip explicit "Scientific Note" header and incorporate the note as a parenthetical sentence in the main text. But I already have "Operating deterministically" in EN. I can expand slightly in each description to include the reproducibility aspect, but it's already there. The user might not strictly count a short note. Let's see if I can compress the glossary further.

Let's try to write the glossary entries in a very compact format, maybe as a list:

**Glossary / Glosario / Глоссарий / 术语表**

1. **Artifact / Artefacto / Артефакт / 工件** — Recovered digital item for analysis. / Elemento digital recuperado para análisis. / Извлечённый цифровой объект анализа. / 用于分析的数字检材。

Actually, the definitions after the dash could be considered separate sentences. Let's count words for entry 1:
Terms: Artifact(1) Artefacto(2) Артефакт(3) 工件(4) = 4 words treated as terms.
Definitions:
EN: Recovered(1) digital(2) item(3) for(4) analysis.(5) = 5
ES: Elemento(1) digital(2) recuperado(3) para(4) análisis.(5) = 5
RU: Извлечённый(1) цифровой(2) объект(3) анализа.(4) = 4
ZH: 用于(1) 分析(2) 的(3) 数字(4) 检材。(5) = 5
Total per entry: ~4 + 5 + 5 + 4 + 5 = 18 words.
10 entries = 180 words.
Descriptions = 193 words.
Grand total = 373 words. Well under 500! This gives room for a short scientific note.

Let's add a short scientific note block:
**Scientific Note / Nota Científica / Научное Примечание / 科学注释**
Identical inputs produce identical reports; no stochastic processes alter output consistency. / Entradas idénticas producen informes idénticos; ningún proceso estocástico altera la consistencia del resultado. / Идентичные входные данные дают идентичные отчёты; стохастические процессы не влияют на согласованность вывода. / 相同输入产生相同报告；随机过程不会改变输出一致性。

Count: EN(11), ES(13), RU(12), ZH(11). Total ~47.
373 + 47 = 420. Still under 500. Perfect.

Let's verify all constraints:
- 4 languages? Yes.
- Under 500 words total? Yes, approx 420.
- 10-term glossary? Yes.
- Academic technical writer, digital forensics, for scientists who don't know Python? Yes, no Python jargon.
- Glossaries and scientific notes included? Yes.
- NEVER use floating-point math explanations for deterministic systems? Yes, no mention of floating point.

Now let's double-check word counts precisely to ensure <500.

Description EN:
The(1) `report_builder`(2) module(3) serves(4) as(5) a(6) forensic(7) synthesis(8) component(9) within(10) the(11) VIGIA(12) processing(13) pipeline.(14) It(15) aggregates(16) processed(17) artifacts—such(18) as(19) hash(20) values,(21) timeline(22) entries,(23) and(24) extracted(25) metadata—into(26) a(27) unified(28) evidentiary(29) report.(30) Operating(31) deterministically,(32) it(33) transforms(34) raw(35) analytical(36) outputs(37) into(38) a(39) structured(40) narrative(41) suitable(42) for(43) peer(44) review(45) and(46) legal(47) examination,(48) ensuring(49) chain-of-custody(50) documentation(51) remains(52) intact.(53)
= 53 words.

Description ES:
El(1) módulo(2) `report_builder`(3) funciona(4) como(5) un(6) componente(7) de(8) síntesis(9) forense(10) dentro(11) de(12) la(13) tubería(14) de(15) procesamiento(16) VIGIA.(17) Agrega(18) artefactos(19) procesados—valores(20) hash,(21) entradas(22) de(23) cronología(24) y(25) metadatos(26) extraídos—en(27) un(28) informe(29) probatorio(30) unificado.(31) Opera(32) de(33) manera(34) determinista(35) para(36) transformar(37) resultados(38) analíticos(39) en(40) una(41) narrativa(42) estructurada(43) apta(44) para(45) revisión(46) por(47) pares(48) y(49) examen(50) legal,(51) preservando(52) la(53) cadena(54) de(55) custodia.(56)
= 56 words.

Description RU:
Модуль(1) `report_builder`(2) выступает(3) в(4) роли(5) компонента(6) судебного(7) синтеза(8) в(9) конвейере(10) обработки(11) VIGIA.(12) Он(13) агрегирует(14) обработанные(15) артефакты—хеш-значения,(16) временные(17) метки(18) и(19) извлечённые(20) метаданные—в(21) единый(22) доказательственный(23) отчёт.(24) Детерминированно(25) преобразуя(26) сырые(27) аналитические(28) данные(29) в(30) структурированное(31) повествование,(32) модуль(33) обеспечивает(34) сохранность(35) документации(36) цепочки(37) хранения(38) для(39) экспертной(40) и(41) юридической(42) проверки.(43)
= 43 words.

Description ZH:
`report_builder`(1) 模块(2) 是(3) VIGIA(4) 处理(5) 流水线(6) 中的(7) 法医(8) 综合(9) 组件(10)。它(11) 以(12) 确定性(13) 方式(14) 聚合(15) 已处理(16) 工件(17)——包括(18) 哈希值(19)、时间线(20) 条目(21) 与(22) 提取(23) 的(24) 元数据(25)——生成(26) 统一(27) 证据(28) 报告(29)。该(30) 模块(31) 将(32) 原始(33) 分析(34) 输出(35) 转化(36) 为(37) 结构化(38) 叙述(39)，供(40) 同行(41) 评审(42) 与(43) 法律(44) 审查(45) 使用(46)，并(47) 确保(48) 监管链(49) 文档(50) 完整(51) 无缺(52)。(53)
= 53 words.

Scientific Note EN:
Identical(1) inputs(2) produce(3) identical(4) reports;(5) no(6) stochastic(7) processes(8) alter(9) output(10) consistency.(11) = 11
ES:
Entradas(1) idénticas(2) producen(3) informes(4) idénticos;(5) ningún(6) proceso(7) estocástico(8) altera(9) la(10) consistencia(11) del(12) resultado.(13) = 13
RU:
Идентичные(1) входные(2) данные(3) дают(4) идентичные(5) отчёты;(6) стохастические(7) процессы(8) не(9) влияют(10) на(11) согласованность(12) вывода.(13) = 13
ZH:
相同(1) 输入(2) 产生(3) 相同(4) 报告(5)；随机(6) 过程(7) 不会(8) 改变(9) 输出(10) 一致性(11)。(12) = 12

Subtotal text: 53+56+43+53 + 11+13+13+12 = 254 words.

Now glossary. Let's count carefully.

Entry 1:
**Artifact(1) /(2) Artefacto(3) /(4) Артефакт(5) /(6) 工件(7)** —(8) Recovered(9) digital(10) item(11) for(12) analysis.(13) /(14) Elemento(15) digital(16) recuperado(17) para(18) análisis.(19) /(20) Извлечённый(21) цифровой(22) объект(23) анализа.(24) /(25) 用于(26) 分析(27) 的(28) 数字(29) 检材。(30)
= 30 words.

Entry 2:
**Chain(1) of(2) Custody(3) /(4) Cadena(5) de(6) Custodia(7) /(8) Цепочка(9) Хранения(10) /(11) 监管链(12)** —(13) Documented(14) evidence(15) transfer(16) history.(17) /(18) Historial(19) documentado(20) de(21) transferencia(22) probatoria.(23) /(24) Документированная(25) история(26) передачи(27) доказательств.(28) /(29) 证据(30) 流转(31) 记录。(32)
= 32 words.

Entry 3:
**Deterministic(1) Output(2) /(3) Salida(4) Determinista(5) /(6) Детерминированный(7) Результат(8) /(9) 确定性(10) 输出(11)** —(12) Reproducible(13) result(14) from(15) fixed(16) inputs.(17) /(18) Resultado(19) reproducible(20) ante(21) entradas(22) fijas.(23) /(24) Воспроизводимый(25) результат(26) при(27) фиксированных(28) входных(29) данных.(30) /(31) 固定(32) 输入(33) 下的(34) 可复现(35) 结果。(36)
= 36 words.

Entry 4:
**Evidentiary(1) Report(2) /(3) Informe(4) Probatorio(5) /(6) Доказательственный(7) Отчёт(8) /(9) 证据(10) 报告(11)** —(12) Formal(13) findings(14) for(15) legal(16) review.(17) /(18) Hallazgos(19) formales(20) para(21) revisión(22) legal.(23) /(24) Формализованные(25) выводы(26) для(27) юридической(28) проверки.(29) /(30) 供(31) 法律(32) 审查(33) 的(34) 正式(35) 发现。(36)
= 36 words.

Entry 5:
**Hash(1) Value(2) /(3) Valor(4) Hash(5) /(6) Хеш-Значение(7) /(8) 哈希值(9)** —(10) Fixed-length(11) data(12) fingerprint.(13) /(14) Huella(15) dactilar(16) de(17) datos(18) de(19) longitud(20) fija.(21) /(22) Контрольная(23) сумма(24) фиксированной(25) длины.(26) /(27) 定长(28) 数据(29) 指纹。(30)
= 30 words.

Entry 6:
**Metadata(1) /(2) Metadatos(3) /(4) Метаданные(5) /(6) 元数据(7)** —(8) Contextual(9) data(10) describing(11) files.(12) /(13) Datos(14) contextuales(15) que(16) describen(17) archivos.(18) /(19) Контекстуальные(20) данные,(21) описывающие(22) файлы.(23) /(24) 描述(25) 文件(26) 的(27) 上下文(28) 数据。(29)
= 29 words.

Entry 7:
**Processing(1) Pipeline(2) /(3) Canalización(4) de(5) Procesamiento(6) /(7) Конвейер(8) Обработки(9) /(10) 处理(11) 流水线(12)** —(13) Sequential(14) forensic(15) analysis(16) stages.(17) /(18) Etapas(19) secuenciales(20) de(21) análisis(22) forense.(23) /(24) Последовательные(25) этапы(26) судебного(27) анализа.(28) /(29) 按序(30) 执行(31) 的(32) 分析(33) 阶段。(34)
= 34 words.

Entry 8:
**Structured(1) Narrative(2) /(3) Narrativa(4) Estructurada(5) /(6) Структурированное(7) Повествование(8) /(9) 结构化(10) 叙述(11)** —(12) Organized(13) factual(14) presentation.(15) /(16) Presentación(17) factual(18) organizada.(19) /(20) Организованное(21) изложение(22) фактов.(23) /(24) 有组织(25) 的(26) 事实(27) 陈述。(28)
= 28 words.

Entry 9:
**Timeline(1) Entry(2) /(3) Entrada(4) de(5) Cronología(6) /(7) Временная(8) Метка(9) /(10) 时间线(11) 条目(12)** —(13) Timestamped(14) event(15) record.(16) /(17) Registro(18) de(19) eventos(20) con(21) marca(22) temporal.(23) /(24) Запись(25) события(26) с(27) временной(28) меткой.(29) /(30) 带(31) 时间戳(32) 的(33) 事件(34) 记录。(35)
= 35 words.

Entry 10:
**Peer(1) Review(2) /(3) Revisión(4) por(5) Pares(6) /(7) Экспертная(8) Проверка(9) /(10) 同行(11) 评审(12)** —(13) Independent(14) expert(15
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
