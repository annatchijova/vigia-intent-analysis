<!--
VIGIA Academic Documentation
Module: c61c815b
Batch ID: vigia-doc-0155-c61c815b
Generated: 2026-05-20T14:56:47.877943+00:00
-->

The user wants a brief academic description in 4 languages (EN, ES, RU, 中文) for a VIGIA support module: `vigia/tools/document_integrity.py`. Total under 500 words. Include a 10-term glossary. Content summary mentions it's based on Case 041 (El Documento Frankenstein) and vision analysis requirements. Tools include `audit_document_integrity` for PDF/DOCX multi-layer.

Constraints:
- Academic technical writer specializing in digital forensics.
- Audience: scientists who do not know Python.
- 4 languages: ENGLISH, ESPAÑOL, РУССКИЙ, 中文.
- Include glossaries and scientific notes.
- NEVER use floating-point math explanations for deterministic systems.
- Under 500 words total. This is tight for 4 languages + glossary. Must be very concise.

Plan:
- Write a single cohesive description that is presented in 4 languages. Since total words must be under 500, each language gets maybe 2-3 sentences. Then a glossary of 10 terms.

Let's draft content:

EN:
Module `vigia/tools/document_integrity.py` provides deterministic forensic utilities for compound document examination. It performs multi-layer structural audits on PDF and DOCX containers to detect content grafting, metadata discontinuities, and object-stream tampering, as required by Case 041 ("El Documento Frankenstein") and the architecture's vision-analysis pipeline. The primary instrument, `audit_document_integrity`, returns reproducible, bitwise-verifiable integrity reports without reliance on probabilistic approximations.

ES:
El módulo `vigia/tools/document_integrity.py` ofrece utilidades forenses deterministas para el examen de documentos compuestos. Realiza auditorías estructurales multicapa en contenedores PDF y DOCX para detectar injertos de contenido, discontinuidades en metadatos y alteraciones en flujos de objetos, según lo requerido por el Caso 041 («El Documento Frankenstein») y la arquitectura de análisis visual. La herramienta principal, `audit_document_integrity`, genera informes de integridad reproducibles y verificables a nivel de bits sin recurrir a aproximaciones probabilísticas.

RU:
Модуль `vigia/tools/document_integrity.py` предоставляет детерминированные судебные утилиты для исследования составных документов. Он выполняет многоуровневые структурные аудиты контейнеров PDF и DOCX с целью выявления прививки контента, разрывов в метаданных и подделок потоков объектов, как требуется в Деле 041 («Документ Франкенштейн») и архитектуре визуального анализа. Основной инструмент `audit_document_integrity` возвращает воспроизводимые, верифицируемые побитово отчёты об целостности без использования вероятностных приближений.

中文:
`vigia/tools/document_integrity.py` 模块为复合文档检验提供确定性取证工具。该模块对 PDF 与 DOCX 容器执行多层结构审计，以检测内容嫁接、元数据不连续及对象流篡改，满足第041号案例（《科学怪人文档》）与视觉分析架构之需求。核心工具 `audit_document_integrity` 生成可复现、可逐位验证的完整性报告，不依赖概率近似。

Now glossary (10 terms). Must be concise. Maybe 2 lines per term? But total words must be under 500. Let's count words so far.

EN: ~48 words
ES: ~52 words
RU: ~52 words
ZH: ~48 words
Total ~200 words. Glossary must be under 300 words.

Glossary terms:
1. Compound Document / Documento compuesto / Составной документ / 复合文档
2. Content Grafting / Injerto de contenido / Прививка контента / 内容嫁接
3. Metadata Discontinuity / Discontinuidad de metadatos / Разрыв метаданных / 元数据不连续
4. Object Stream / Flujo de objetos / Поток объектов / 对象流
5. Deterministic Audit / Auditoría determinista / Детерминированный аудит / 确定性审计
6. Bitwise Verification / Verificación a nivel de bits / Побитовая верификация / 逐位验证
7. Multi-layer Analysis / Análisis multicapa / Многоуровневый анализ / 多层分析
8. Structural Tampering / Alteración estructural / Структурная подделка / 结构篡改
9. Vision-Analysis Pipeline / Canalización de análisis visual / Конвейер визуального анализа / 视觉分析管道
10. Integrity Report / Informe de integridad / Отчёт о целостности / 完整性报告

Let's draft concise definitions bilingual-ish? Actually the prompt says "Include glossaries". Since the whole text is 4 languages, perhaps the glossary should have terms in all 4 languages too. Or maybe one glossary section with terms in English and translations? To save words, I can present each term as: EN / ES / RU / ZH — definition. Or maybe just EN term with 4-language definition? That might be confusing. Better to list terms in 4 columns? But it's text.

Alternative: provide glossary in English only? The prompt says "You always write in 4 languages". So glossary should probably follow suit. I can make a compact table-like format.

Let's estimate word count for glossary:

1. **Compound Document / Documento compuesto / Составной документ / 复合文档** — A file format encapsulating multiple data streams (e.g., PDF, DOCX). / Formato que encapsula múltiples flujos de datos. / Формат, инкапсулирующий несколько потоков данных. / 封装多个数据流的文件格式。
(~30 words)

If I do 10 terms like this, it's too long. I need to be very brief. Maybe just define once in English and give equivalents? But the instruction is strong about 4 languages. Perhaps I can do a glossary where each entry is: Term (EN / ES / RU / ZH): Definition. But definition itself in 4 languages would be huge.

Maybe the glossary is a separate section where each term is presented in 4 languages but with minimal definitions. Let's try:

**Glossary / Glosario / Глоссарий / 术语表**

1. **Compound document** — Documento compuesto — Составной документ — 复合文档: File format embedding multiple data streams. / Formato que incrusta múltiples flujos. / Формат со встроенными потоками. / 嵌入多数据流的文件格式。
(~25 words per entry x 10 = 250 words. Total ~450. Good.)

But wait, the user said "Include a 10-term glossary." It doesn't explicitly say each definition must be 4 languages, but since I always write in 4 languages, I should attempt to make the glossary accessible. However, with a 500-word total limit, full 4-language definitions for 10 terms is nearly impossible. The body text already uses ~200 words. 10 terms with 4-language definitions would exceed 500.

I need to be extremely concise. Let's calculate carefully.

Body text draft:

EN (46 words):
Module `vigia/tools/document_integrity.py` provides deterministic forensic utilities for compound-document examination. It performs multi-layer structural audits on PDF and DOCX containers to detect content grafting, metadata discontinuities, and object-stream tampering, as required by Case 041 ("El Documento Frankenstein") and the vision-analysis pipeline. The primary instrument, `audit_document_integrity`, returns reproducible, bitwise-verifiable integrity reports without probabilistic approximations.

ES (48 words):
El módulo `vigia/tools/document_integrity.py` ofrece utilidades forenses deterministas para el examen de documentos compuestos. Realiza auditorías estructurales multicapa en contenedores PDF y DOCX para detectar injertos de contenido, discontinuidades en metadatos y alteraciones en flujos de objetos, según el Caso 041 («El Documento Frankenstein») y el pipeline de análisis visual. La herramienta `audit_document_integrity` genera informes reproducibles y verificables a nivel de bits sin aproximaciones probabilísticas.

RU (49 words):
Модуль `vigia/tools/document_integrity.py` реализует детерминированные судебные утилиты для исследования составных документов. Выполняет многоуровневые структурные аудиты контейнеров PDF и DOCX с целью выявления прививки контента, разрывов метаданных и подделок потоков объектов, как требуется в Деле 041 («Документ Франкенштейн») и конвейере визуального анализа. Инструмент `audit_document_integrity` формирует воспроизводимые, побитово верифицируемые отчёты без вероятностных приближений.

ZH (47 words):
`vigia/tools/document_integrity.py` 模块为复合文档检验提供确定性取证工具。其对 PDF 与 DOCX 容器执行多层结构审计，以侦测内容嫁接、元数据不连续及对象流篡改，满足第041号案例（《弗兰肯斯坦文档》）与视觉分析管道之需求。核心工具 `audit_document_integrity` 生成可复现、可逐位验证的完整性报告，不依赖概率近似。

Total body: ~190 words. Leaves ~310 words for glossary.

Now glossary. Let's aim for ~250 words total for glossary.

Format: For each term, one line with 4 language labels and a single cohesive definition split? No, that's messy.

Better: Use a compact format where each entry is:

**Compound document / Documento compuesto / Составной документ / 复合文档** — Encapsulates heterogeneous data streams. / Encapsula flujos heterogéneos. / Инкапсулирует гетерогенные потоки. / 封装异构数据流。

Count: ~15 words per entry. 10 entries = 150 words. Total ~340. Perfect.

Let's draft 10 entries with very short definitions.

Terms:
1. Compound Document / Documento compuesto / Составной документ / 复合文档
2. Content Grafting / Injerto de contenido / Прививка контента / 内容嫁接
3. Metadata Discontinuity / Discontinuidad de metadatos / Разрыв метаданных / 元数据不连续
4. Object Stream / Flujo de objetos / Поток объектов / 对象流
5. Deterministic Audit / Auditoría determinista / Детерминированный аудит / 确定性审计
6. Bitwise Verification / Verificación bit a bit / Побитовая верификация / 逐位验证
7. Multi-layer Analysis / Análisis multicapa / Многоуровневый анализ / 多层分析
8. Structural Tampering / Alteración estructural / Структурное вмешательство / 结构篡改
9. Vision-Analysis Pipeline / Pipeline de análisis visual / Конвейер визуального анализа / 视觉分析管道
10. Integrity Report / Informe de integridad / Отчёт о целостности / 完整性报告

Definitions must be concise.

1. Encapsulates multiple internal data streams. / Encapsula múltiples flujos internos. / Инкапсулирует несколько внутренних потоков. / 封装多个内部数据流。
Words: ~12.

2. Insertion of foreign material into an authentic document. / Inserción de material foráneo en un documento auténtico. / Вставка чужеродного материала в подлинный документ. / 向真实文档插入外来材料。
~14 words.

3. Temporal or logical inconsistency in embedded metadata. / Inconsistencia temporal o lógica en metadatos incrustados. / Временное или логическое несоответствие во встроенных метаданных. / 嵌入元数据中的时间或逻辑不一致。
~14 words.

4. Binary container holding document objects. / Contenedor binario que almacena objetos del documento. / Бинарный контейнер, хранящий объекты документа. / 存储文档对象的二进制容器。
~12 words.

5. Examination protocol yielding identical results under identical inputs. / Protocolo de examen que produce resultados idénticos ante entradas idénticas. / Протокол исследования, дающий идентичные результаты при идентичных входных данных. / 在相同输入下产生相同结果的检验协议。
~16 words.

6. Exact per-bit comparison for data integrity. / Comparación exacta bit por bit para integridad. / Точное побитовое сравнение для проверки целостности. / 逐位精确比对以验证数据完整性。
~11 words.

7. Sequential inspection of file layers from container to content. / Inspección secuencial de capas desde contenedor hasta contenido. / Последовательная проверка слоёв файла от контейнера к содержимому. / 从容器到内容的文件层级顺序检查。
~13 words.

8. Unauthorized modification of internal file architecture. / Modificación no autorizada de la arquitectura interna. / Несанкционированное изменение внутренней архитектуры файла. / 对文件内部架构的未授权更改。
~11 words.

9. Automated workflow linking visual feature extraction with forensic logic. / Flujo automatizado que vincula extracción de rasgos visuales y lógica forense. / Автоматизированный рабочий процесс, связывающий извлечение визуальных признаков с судебной логикой. / 将视觉特征提取与取证逻辑相连的自动化工作流。
~16 words.

10. Formal record of structural and logical integrity findings. / Registro formal de hallazgos de integridad estructural y lógica. / Формальная запись выявленных структурных и логических нарушений целостности. / 结构与逻辑完整性发现的正式记录。
~13 words.

Let's calculate total words for glossary entries:

Entry 1: EN 4 + ES 4 + RU 4 + ZH 4 = 16? Actually Chinese words are counted differently but let's count tokens roughly. Let's just count English/Spanish/Russian words. Chinese characters count as words usually but let's be safe.

Actually, total word count limit of 500 is likely counting English/Spanish/Russian words and Chinese characters. This is ambiguous. To be safe, I should make it even shorter. But the definitions above seem quite short. Let's sum body text word counts more precisely.

EN text:
Module(1) `vigia/tools/document_integrity.py`(2) provides(3) deterministic(4) forensic(5) utilities(6) for(7) compound-document(8) examination.(9) It(10) performs(11) multi-layer(12) structural(13) audits(14) on(15) PDF(16) and(17) DOCX(18) containers(19) to(20) detect(21) content(22) grafting,(23) metadata(24) discontinuities,(25) and(26) object-stream(27) tampering,(28) as(29) required(30) by(31) Case(32) 041(33) ("El(34) Documento(35) Frankenstein")(36) and(37) the(38) vision-analysis(39) pipeline.(40) The(41) primary(42) instrument,(43) `audit_document_integrity`,(44) returns(45) reproducible,(46) bitwise-verifiable(47) integrity(48) reports(49) without(50) probabilistic(51) approximations.(52) -> 52 words.

ES text:
El(1) módulo(2) `vigia/tools/document_integrity.py`(3) ofrece(4) utilidades(5) forenses(6) deterministas(7) para(8) el(9) examen(10) de(11) documentos(12) compuestos.(13) Realiza(14) auditorías(15) estructurales(16) multicapa(17) en(18) contenedores(19) PDF(20) y(21) DOCX(22) para(23) detectar(24) injertos(25) de(26) contenido,(27) discontinuidades(28) en(29) metadatos(30) y(31) alteraciones(32) en(33) flujos(34) de(35) objetos,(36) según(37) el(38) Caso(39) 041(40) («El(41) Documento(42) Frankenstein»)(43) y(44) el(45) pipeline(46) de(47) análisis(48) visual.(49) La(50) herramienta(51) `audit_document_integrity`(52) genera(53) informes(54) reproducibles(55) y(56) verificables(57) a(58) nivel(59) de(60) bits(61) sin(62) aproximaciones(63) probabilísticas.(64) -> 64 words.

RU text:
Модуль(1) `vigia/tools/document_integrity.py`(2) реализует(3) детерминированные(4) судебные(5) утилиты(6) для(7) исследования(8) составных(9) документов.(10) Выполняет(11) многоуровневые(12) структурные(13) аудиты(14) контейнеров(15) PDF(16) и(17) DOCX(18) с(19) целью(20) выявления(21) прививки(22) контента,(23) разрывов(24) метаданных(25) и(26) подделок(27) потоков(28) объектов,(29) как(30) требуется(31) в(32) Деле(33) 041(34) («Документ(35) Франкенштейн»)(36) и(37) конвейере(38) визуального(39) анализа.(40) Инструмент(41) `audit_document_integrity`(42) формирует(43) воспроизводимые,(44) побитово(45) верифицируемые(46) отчёты(47) без(48) вероятностных(49) приближений.(50) -> 50 words.

ZH text:
`vigia/tools/document_integrity.py`(1) 模块(2) 为(3) 复合文档(4) 检验(5) 提供(6) 确定性(7) 取证(8) 工具(9)。(10) 其(11) 对(12) PDF(13) 与(14) DOCX(15) 容器(16) 执行(17) 多层(18) 结构(19) 审计(20)，(21) 以(22) 侦测(23) 内容(24) 嫁接(25)、(26) 元数据(27) 不连续(28) 及(29) 对象流(30) 篡改(31)，(32) 满足(33) 第(34) 041(35) 号(36) 案例(37)（《(38) 弗兰肯斯坦(39) 文档(40)》）(41) 与(42) 视觉(43) 分析(44) 管道(45) 之(46) 需求(47)。(48) 核心(49) 工具(50) `audit_document_integrity`(51) 生成(52) 可复现(53)、(54) 可逐位验证(55) 的(56) 完整性(57) 报告(58)，(59) 不(60) 依赖(61) 概率(62) 近似(63)。(64) -> ~64 words (counting Chinese characters/punctuation as units).

Total body: ~230 words.

Glossary budget: ~270 words.

Now glossary entries with word counts.

Entry 1:
**Compound document / Documento compuesto / Составной документ / 复合文档** — Encapsulates multiple internal data streams. / Encapsula múltiples flujos internos. / Инкапсулирует несколько внутренних потоков. / 封装多个内部数据流。
EN def: 5 words. ES: 5. RU: 4. ZH: 6. Plus labels ~8. Total ~28.

Entry 2:
**Content grafting / Injerto de contenido / Прививка контента / 内容嫁接** — Insertion of foreign material into an authentic document. / Inserción de material foráneo en un documento auténtico. / Вставка чужеродного материала в подлинный документ. / 向真实文档插入外来材料。
EN: 8. ES: 9. RU: 5. ZH: 8. Labels ~8. Total ~38.

Entry 3:
**Metadata discontinuity / Discontinuidad de metadatos / Разрыв метаданных / 元数据不连续** — Temporal or logical inconsistency in embedded metadata. / Inconsistencia temporal o lógica en metadatos incrustados. / Временное или логическое несоответствие встроенных метаданных. / 嵌入元数据中的时间或逻辑不一致。
EN: 7. ES: 8. RU: 4. ZH: 9. Labels ~8. Total ~36.

Entry 4:
**Object stream / Flujo de objetos / Поток объектов / 对象流** — Binary container holding document objects. / Contenedor binario que almacena objetos del documento. / Бинарный контейнер, хранящий объекты документа. / 存储文档对象的二进制容器。
EN: 5. ES: 7. RU: 4. ZH: 8. Labels ~8. Total ~32.

Entry 5:
**Deterministic audit / Auditoría determinista / Детерминированный аудит / 确定性审计** — Protocol yielding identical results under identical inputs. / Protocolo que produce resultados idénticos ante entradas iguales. / Протокол, дающий идентичные результаты при одинаковых данных. / 相同输入下产生相同结果的协议。
EN: 7. ES: 8. RU: 5. ZH: 9. Labels ~8. Total ~37.

Entry 6:
**Bitwise verification / Verificación bit a bit / Побитовая верификация / 逐位验证** — Exact per-bit comparison for data integrity. / Comparación exacta bit por bit para integridad. / Точное побитовое сравнение для проверки целостности. / 逐位精确比对以验证完整性。
EN: 7. ES: 8. RU: 4. ZH: 8. Labels ~8. Total ~35.

Entry 7:
**Multi-layer analysis / Análisis multicapa / Многоуровневый анализ / 多层分析** — Sequential inspection from container to content. / Inspección secuencial desde contenedor hasta contenido. / Последовательная проверка слоёв от контейнера к содержимому. / 从容器到内容的层级顺序检查。
EN: 6. ES: 6. RU: 5. ZH: 9. Labels ~8. Total ~34.

Entry 8:
**Structural tampering / Alteración estructural / Структурное вмешательство / 结构篡改** — Unauthorized modification of internal file architecture. / Modificación no autorizada de la arquitectura interna. / Несанкционированное изменение внутренней архитектуры. / 对内部文件架构的未授权更改。
EN: 6. ES: 6. RU: 3. ZH: 8. Labels ~8. Total ~31.

Entry 9:
**Vision-analysis pipeline / Pipeline de análisis visual / Конвейер визуального анализа / 视觉分析管道** — Automated workflow linking visual extraction to forensic logic. / Flujo automatizado que vincula extracción visual con lógica forense. / Автоматизированный процесс, связывающий визуальное извлечение с судебной логикой. / 将视觉提取与取证逻辑相连的自动化工作流。
EN: 8. ES: 9. RU: 4. ZH: 12. Labels ~8. Total ~41.

Entry 10:
**Integrity report / Informe de integridad / Отчёт о целостности / 完整性报告** — Formal record of structural and logical findings. / Registro formal de hallazgos estructurales y lógicos. / Формальная запись структурных и логических выявлений. / 结构与逻辑发现的正式记录。
EN: 7. ES: 7. RU: 4. ZH: 9. Labels ~8. Total ~35.

Now sum glossary totals:
28+38+36+32+37+35+34+31+41+35 = 347 words.

Body + Glossary = 230 + 347 = 577. Too much.

Need to cut. Target under 500. So I need to reduce by ~80+ words.

Options:
- Shorten body text further.
- Reduce glossary definitions to single-language (English) with slash-separated translations? But violates "always write in 4 languages".
- Reduce glossary to 5 terms? User asked for 10-term glossary.
- Make definitions extremely telegraphic, like 3-4 words each.

Let's try telegraphic definitions. Since the audience are scientists, short definitions are okay if precise.

Entry 1: File format embedding heterogeneous streams. / Formato que incrusta flujos heterogéneos. / Формат со встроенными потоками. / 封装异构数据流的格式。
EN: 5. ES: 5. RU: 3. ZH: 8. Labels ~8. Total ~21.

Entry 2: Foreign material inserted into a document. / Material foráneo insertado en un documento. / Чужеродный материал, вставленный в документ. / 插入文档的外来材料。
EN: 6. ES: 6. RU: 4. ZH: 8. Labels ~8. Total ~24.

Entry 3: Inconsistency within embedded metadata. / Inconsistencia dentro de metadatos incrustados. / Несоответствие во встроенных метаданных. / 嵌入元数据内部的不一致。
EN: 4. ES: 5. RU: 3. ZH: 9. Labels ~8. Total ~21.

Entry 4: Binary sequence storing document objects. / Secuencia binaria que almacena objetos. / Бинарная последовательность хранения объектов. / 存储文档对象的二进制序列。
EN: 5. ES: 5. RU: 3. ZH: 9. Labels ~8. Total ~22.

Entry 5: Identical output for identical input. / Salida idéntica para entrada idéntica. / Идентичный вывод при идентичном вводе. / 相同输入产生相同输出。
EN: 5. ES: 5. RU: 3. ZH: 8. Labels ~8. Total ~21.

Entry 6: Per-bit exact comparison. / Comparación exacta bit por bit. / Точное побитовое сравнение. / 逐位精确比较。
EN: 4. ES: 5. RU: 3. ZH: 6. Labels ~8. Total ~18.

Entry 7: Layer-by-layer file inspection. / Inspección de archivo capa por capa. / Проверка файла слой за слоем. / 逐层文件检查。
EN: 4. ES: 6. RU: 4. ZH: 6. Labels ~8. Total ~22.

Entry 8: Unauthorized internal architecture change. / Cambio no autorizado de arquitectura interna. / Несанкционированное изменение внутренней архитектуры. / 对内部架构的未授权更改。
EN: 5. ES: 6. RU: 3. ZH: 8. Labels ~8. Total ~22.

Entry 9: Visual-to-forensic automated workflow. / Flujo automatizado visual a forense. / Автоматизированный рабочий процесс визуальной судебной экспертизы. / 视觉到取证的自动化工作流。
Wait, Russian is long. Let's shorten: Автоматизированный визуально-судебный процесс. (3 words) / 视觉取证自动流程 (5 characters). Let's use:
Automated visual-to-forensic workflow. / Flujo automatizado visual a forense. / Автоматизированный визуально-судебный процесс. / 视觉取证自动工作流。
EN: 4. ES: 5. RU: 3. ZH: 6. Labels ~8. Total ~20.

Entry 10: Record of integrity findings. / Registro de hallazgos de integridad. / Запись выявлений целостности. / 完整性发现记录。
EN: 4. ES: 5. RU: 3. ZH: 6. Labels ~8. Total ~18.

Now sum telegraphic glossary:
21+24+21+22+21+18+22+22+20+18 = 209 words.

Body ~230. Total ~439. Under 500. Perfect.

But I need to check if the glossary is too telegraphic to be useful for scientists. They are okay. Let's ensure they are accurate.

Entry 1: Compound document. Definition: File format embedding heterogeneous streams. That's okay.
Entry 2: Content grafting. Foreign material inserted into a document. Good.
Entry 3: Metadata discontinuity. Inconsistency within embedded metadata. Good.
Entry 4: Object stream. Binary sequence storing document objects. Good.
Entry 5: Deterministic audit. Identical output for identical input. Good.
Entry 6: Bitwise verification. Per-bit exact comparison. Good.
Entry 7: Multi-layer analysis. Layer-by-layer file inspection. Good.
Entry 8: Structural tampering. Unauthorized internal architecture change. Good.
Entry 9: Vision-analysis pipeline. Automated visual-to-forensic workflow. Hmm. "Visual-to-forensic" is a bit odd. Maybe "Workflow linking visual extraction to forensic logic." That's longer. Let's see if we can shorten.
EN: Workflow linking visual features to forensic logic. (7 words)
ES: Flujo que vincula rasgos visuales a lógica forense. (8 words)
RU: Процесс, связывающий визуальные признаки с судебной логикой. (5 words)
ZH: 将视觉特征与取证逻辑关联的工作流。(9 chars)
Total with labels ~8+7+8+5+9 = 37. That's a jump. Let's keep it shorter.

Alternative Entry 9:
EN: Automated workflow for visual forensic analysis. (6)
ES: Flujo automatizado para análisis forense visual. (7)
RU: Автоматизированный процесс визуально-судебного анализа. (4)
ZH: 视觉取证分析的自动化工作流。(8)
Total labels ~8 + 6+7+4+8 = 33. Acceptable.

Let's adjust totals: remove 20, add 33. Glossary total = 209 - 20 + 33 = 222.

Total ~452. Still under 500.

Let's recalc body text to see if we can shave a few more words.

EN:
Module `vigia/tools/document_integrity.py` provides deterministic forensic utilities for compound-document examination. It performs multi-layer structural audits on PDF and DOCX containers to detect content grafting, metadata discontinuities, and object-stream tampering, as required by Case 041 ("El Documento Frankenstein") and the vision-analysis pipeline. The primary instrument, `audit_document_integrity`, returns reproducible, bitwise-verifiable integrity reports without probabilistic approximations.
52 words.

Can shorten:
Module `vigia/tools/document_integrity.py` delivers deterministic forensic utilities for compound-document examination. It conducts multi-layer structural audits of PDF and DOCX containers to detect content grafting, metadata discontinuities, and object-stream tampering per Case 041 ("El Documento Frankenstein") and the vision-analysis pipeline. Its core instrument, `audit_document_integrity`, produces reproducible, bitwise-verifiable integrity reports without probabilistic approximations.
49 words. ("delivers" vs "provides", "conducts" vs "performs", "per" vs "as required by", "core instrument" vs "primary instrument", "produces" vs "returns").

ES:
El módulo `vigia/tools/document_integrity.py` ofrece utilidades forenses deterministas para el examen de documentos compuestos. Realiza auditorías estructurales multicapa en contenedores PDF y DOCX para detectar injertos de contenido, discontinuidades en metadatos y alteraciones en flujos de objetos, según el Caso 041 («El Documento Frankenstein») y el pipeline de análisis visual. La herramienta `audit_document_integrity` genera informes reproducibles y verificables a nivel de bits sin aproximaciones probabilísticas.
64 words.

Shorten:
El módulo `vigia/tools/document_integrity.py` aporta utilidades forenses deterministas para examinar documentos compuestos. Ejecuta auditorías estructurales multicapa en contenedores PDF y DOCX para detectar injertos de contenido, discontinuidades en metadatos y alteraciones en flujos de objetos, conforme al Caso 041 («El Documento Frankenstein») y al pipeline de análisis visual. La herramienta `audit_document_integrity` genera informes reproducibles y verificables a nivel de bits sin aproximaciones probabilísticas.
61 words. ("aporta" vs "ofrece", "para examinar" vs "para el examen de", "Ejecuta" vs "Realiza", "conforme al" vs "según el").

RU:
Модуль `vigia/tools/document_integrity.py` реализует детерминированные судебные утилиты для исследования составных документов. Выполняет многоуровневые структурные аудиты контейнеров PDF и DOCX с целью выявления прививки контента, разрывов метаданных и подделок потоков объектов, как требуется в Деле 041 («Документ Франкенштейн») и конвейере визуального анализа. Инструмент `audit_document_integrity` формирует воспроизводимые, побитово верифицируемые отчёты без вероятностных приближений.
50 words.

Shorten:
Модуль `vigia/tools/document_integrity.py` реализует детерминированные утилиты для исследования составных документов. Выполняет многоуровневые структурные аудиты контейнеров PDF и DOCX для выявления прививки контента, разрывов метаданных и подделок потоков объектов, как требует Дело 041
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
