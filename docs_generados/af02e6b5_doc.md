<!--
VIGIA Academic Documentation
Module: af02e6b5
Batch ID: vigia-doc-0152-af02e6b5
Generated: 2026-05-20T14:56:47.877252+00:00
-->

The user wants a brief academic description in 4 languages (EN, ES, RU, 中文) of a specific VIGIA support module: `vigia/tools/build_calibration_dataset.py`.

 Constraints:
 - Total under 500 words. This is tight across 4 languages. Must be very concise.
 - Include a 10-term glossary.
 - Target audience: scientists who do not know Python.
 - Style: academic technical writer specializing in digital forensics.
 - NEVER use floating-point math explanations for deterministic systems. (The user mentioned z_scores with "f" which implies float, but I should avoid explaining the deterministic system using floating-point math. I can mention z-scores as statistical measures without discussing IEEE 754 or floating-point precision issues).
 - Must include scientific notes.
 - 4 languages side-by-side or sequentially? Usually sequential is fine. Given the word count, I need to be extremely brief per language. Maybe ~80 words per language + glossary.

 Let's analyze the module:
 - Name: build_calibration_dataset.py
 - Purpose: Builds a calibration dataset for `fit_calibration.py`
 - Sources cases from REAL (FABRICATED) and BEN (AUTHENTIC). Wait, the prompt says "casos REAL (FABRICATED) y BEN (AUTHENTIC)". This seems contradictory/label-swapped or code-named. REAL maps to FABRICATED and BEN maps to AUTHENTIC? Or it's saying the categories are REAL (which are FABRICATED) and BEN (which are AUTHENTIC)? Looking at the output format: ground_truth is "AUTHENTIC" or "FABRICATED". So likely the module takes input cases labeled internally as REAL (meaning fabricated/fake) and BEN (meaning authentic/benign)? Wait, BEN likely stands for benign (authentic). REAL might be a misnomer or stands for "realistic synthetic"? Actually, in forensics, sometimes "Real" means manipulated (fabricated) and "Benign" means original. But the prompt explicitly says: "a partir de los casos REAL (FABRICATED) y BEN (AUTHENTIC)". So I should treat REAL as the label for FABRICATED cases and BEN as the label for AUTHENTIC cases. This is likely an internal naming convention (e.g., REAL = realistic tampering, BEN = benign). I must accurately reflect this mapping without confusing the reader. I'll describe it as an internal label mapping where the source categories REAL and BEN are mapped to forensic ground-truth labels FABRICATED and AUTHENTIC, respectively.

 Output format: JSON list of objects with ground_truth and z_scores dictionary (REG, NET, etc.).
 - z_scores are statistical standard scores. I should not explain them as floating-point. I can describe them as standardized statistical distances.

 Structure:
 1. EN description (~80 words)
 2. ES description (~80 words)
 3. RU description (~80 words)
 4. 中文 description (~80 words)
 5. Glossary (10 terms, bilingual or multilingual? The prompt says include a 10-term glossary. Since the doc is in 4 languages, the glossary could be presented with terms in English and definitions across languages, or terms in all languages. Usually, a glossary in such contexts lists the term and its translation/definition. Given word count, maybe a compact table or list. Let's do EN term + brief definition, or maybe just the terms and multilingual definitions? The prompt says "Include a 10-term glossary". I'll make a compact glossary where each entry has the term and a short note in English, or perhaps list the 4-language equivalents. But glossaries typically define terms. Given the constraint, I'll provide the term in English (since it's code) and brief definitions in the 4 languages? No, that would explode word count.

 Better approach:
 - Write a very tight single-paragraph description per language.
 - Then a glossary of 10 terms. To save words, I can present the glossary as: **Term** (EN / ES / RU / 中文): Definition (EN only or multilingual?). But the user wants the whole output under 500 words. Let's calculate:

 EN: ~60 words
 ES: ~60 words
 RU: ~60 words
 中文: ~60 words (Chinese characters count as words? Usually yes in word count estimates, but sometimes character count. I'll assume words for now, but Chinese is dense).
 Glossary: 10 terms × ~10 words each = ~100 words.
 Total ~340 words. Safe.

 Let's draft EN (max 60 words):
 "This support module constructs a calibration dataset for subsequent statistical fitting. It ingests forensic cases from two source classes—internally labeled REAL (mapped to ground-truth FABRICATED) and BEN (mapped to ground-truth AUTHENTIC)—and emits a structured JSON record per case. Each record contains the ground-truth label and a dictionary of standardized statistical scores (e.g., REG, NET) representing extracted features. The output serves as labeled input for vigia/tools/fit_calibration.py. Scientific note: The module performs deterministic label translation and feature aggregation without probabilistic scoring."

 Wait, "without probabilistic scoring" might be okay. But I should avoid floating-point math explanations. I won't mention float representation.

 ES:
 "Este módulo auxiliar construye un conjunto de datos de calibración para ajuste estadístico posterior. Procesa casos forenses de dos clases origen—REAL (etiqueta interna para FABRICATED) y BEN (etiqueta interna para AUTHENTIC)—y genera un registro JSON estructurado por caso. Cada registro contiene la etiqueta de verdad de campo y un diccionario de puntuaciones estadísticas estandarizadas (p. ej., REG, NET). El resultado alimenta a vigia/tools/fit_calibration.py. Nota científica: El módulo realiza una traducción determinista de etiquetas y agregación de características."

 RU:
 "Вспомогательный модуль формирует калибровочный набор данных для последующего статистического подбора. Обрабатывает криминалистические примеры двух исходных классов — REAL (внутренняя метка для FABRICATED) и BEN (внутренняя метка для AUTHENTIC) — и выдаёт структурированную JSON-запись для каждого примера. Каждая запись содержит эталонную метку и словарь стандартизированных статистических оценок (например, REG, NET). Выходные данные поступают в vigia/tools/fit_calibration.py. Научное примечание: модуль выполняет детерминированное преобразование меток и агрегацию признаков."

 中文:
 "该支持模块构建用于后续统计拟合的校准数据集。它处理来自两个源类别的取证案例——内部标记为 REAL（对应真实标签 FABRICATED）和 BEN（对应真实标签 AUTHENTIC）——并为每个案例生成结构化 JSON 记录。每条记录包含真实标签及标准化统计评分字典（如 REG、NET）。输出作为 vigia/tools/fit_calibration.py 的标注输入。科学说明：本模块执行确定性标签转换与特征聚合。"

 Word counts:
 EN: ~65 words.
 ES: ~60 words.
 RU: ~55 words.
 中文: ~55 words.
 Subtotal: ~235 words.

 Glossary: Need 10 terms. Let's choose terms relevant to the module and digital forensics.
 1. Calibration Dataset
 2. Ground Truth
 3. Z-Score (Standard Score) -> Wait, user output has z_scores. I should include it but avoid floating point explanation. Call it "Standardized Statistical Distance".
 4. Feature Vector (the dictionary of scores)
 5. Deterministic Label Translation
 6. Authentic (Benign)
 7. Fabricated (Tampered)
 8. JSON Record
 9. Source Class (REAL/BEN internal taxonomy)
 10. Statistical Fitting

 Let's refine glossary entries to be multilingual but compact. The user wants 4 languages everywhere. Does the glossary need to be in 4 languages too? The prompt says "You always write in 4 languages". So the glossary should probably present terms and definitions in 4 languages, or at least translate the terms. But 500 words is very tight.

 Alternative: Provide the glossary as a list where each entry gives the term in English, Spanish, Russian, Chinese, and then a single definition in English? No, that's not really 4-language. Better to integrate the glossary entries as short multilingual phrases.

 Actually, maybe I can format the glossary as:
 **Term** (EN) / (ES) / (RU) / (中文) — One-sentence definition that is itself multilingual? That's messy.

 Another approach: Since the descriptions are already in 4 languages, the glossary can be a compact table with 4 columns: EN, ES, RU, 中文. Each row is a term (not a full sentence). But a glossary usually defines. Given the extreme word limit, I will provide each glossary entry as: **EN term / ES term / RU term / 中文 term**: brief definition (in English only to save words? But that violates "always write in 4 languages"). I think the safest is to make the glossary terms themselves multilingual and the definition be a very short phrase repeated or distributed. But that's repetitive and word-heavy.

 Let's reconsider the 500-word limit. Maybe Chinese characters are counted as individual words by the user? If so, my 中文 description is ~70 words. Let's count more carefully.

 EN draft:
 "This support module constructs a calibration dataset for subsequent statistical fitting. It ingests forensic cases from two source classes—internally labeled REAL (mapped to ground-truth FABRICATED) and BEN (mapped to ground-truth AUTHENTIC)—and emits a structured JSON record per case. Each record contains the ground-truth label and a dictionary of standardized statistical scores (e.g., REG, NET) representing extracted features. The output serves as labeled input for vigia/tools/fit_calibration.py. Scientific note: The module performs deterministic label translation and feature aggregation without probabilistic scoring."
 Word count: Let's count.
 This(1) support(2) module(3) constructs(4) a(5) calibration(6) dataset(7) for(8) subsequent(9) statistical(10) fitting.(11) It(12) ingests(13) forensic(14) cases(15) from(16) two(17) source(18) classes—internally(19) labeled(20) REAL(21) (mapped(22) to(23) ground-truth(24) FABRICATED)(25) and(26) BEN(27) (mapped(28) to(29) ground-truth(30) AUTHENTIC)—and(31) emits(32) a(33) structured(34) JSON(35) record(36) per(37) case.(38) Each(39) record(40) contains(41) the(42) ground-truth(43) label(44) and(45) a(46) dictionary(47) of(48) standardized(49) statistical(50) scores(51) (e.g.,(52) REG,(53) NET)(54) representing(55) extracted(56) features.(57) The(58) output(59) serves(60) as(61) labeled(62) input(63) for(64) vigia/tools/fit_calibration.py.(65) Scientific(66) note:(67) The(68) module(69) performs(70) deterministic(71) label(72) translation(73) and(74) feature(75) aggregation(76) without(77) probabilistic(78) scoring.(79)
 ~79 words.

 ES draft:
 "Este módulo auxiliar construye un conjunto de datos de calibración para ajuste estadístico posterior. Procesa casos forenses de dos clases origen—REAL (etiqueta interna para FABRICATED) y BEN (etiqueta interna para AUTHENTIC)—y genera un registro JSON estructurado por caso. Cada registro contiene la etiqueta de verdad de campo y un diccionario de puntuaciones estadísticas estandarizadas (p. ej., REG, NET). El resultado alimenta a vigia/tools/fit_calibration.py. Nota científica: El módulo realiza una traducción determinista de etiquetas y agregación de características."
 Count:
 Este(1) módulo(2) auxiliar(3) construye(4) un(5) conjunto(6) de(7) datos(8) de(9) calibración(10) para(11) ajuste(12) estadístico(13) posterior.(14) Procesa(15) casos(16) forenses(17) de(18) dos(19) clases(20) origen—REAL(21) (etiqueta(22) interna(23) para(24) FABRICATED)(25) y(26) BEN(27) (etiqueta(28) interna(29) para(30) AUTHENTIC)—y(31) genera(32) un(33) registro(34) JSON(35) estructurado(36) por(37) caso.(38) Cada(39) registro(40) contiene(41) la(42) etiqueta(43) de(44) verdad(45) de(46) campo(47) y(48) un(49) diccionario(50) de(51) puntuaciones(52) estadísticas(53) estandarizadas(54) (p.(55) ej.,(56) REG,(57) NET).(58) El(59) resultado(60) alimenta(61) a(62) vigia/tools/fit_calibration.py.(63) Nota(64) científica:(65) El(66) módulo(67) realiza(68) una(69) traducción(70) determinista(71) de(72) etiquetas(73) y(74) agregación(75) de(76) características.(77)
 ~77 words.

 RU draft:
 "Вспомогательный модуль формирует калибровочный набор данных для последующего статистического подбора. Обрабатывает криминалистические примеры двух исходных классов — REAL (внутренняя метка для FABRICATED) и BEN (внутренняя метка для AUTHENTIC) — и выдаёт структурированную JSON-запись для каждого примера. Каждая запись содержит эталонную метку и словарь стандартизированных статистических оценок (например, REG, NET). Выходные данные поступают в vigia/tools/fit_calibration.py. Научное примечание: модуль выполняет детерминированное преобразование меток и агрегацию признаков."
 Count:
 Вспомогательный(1) модуль(2) формирует(3) калибровочный(4) набор(5) данных(6) для(7) последующего(8) статистического(9) подбора.(10) Обрабатывает(11) криминалистические(12) примеры(13) двух(14) исходных(15) классов(16) —(17) REAL(18) (внутренняя(19) метка(20) для(21) FABRICATED)(22) и(23) BEN(24) (внутренняя(25) метка(26) для(27) AUTHENTIC)(28) —(29) и(30) выдаёт(31) структурированную(32) JSON-запись(33) для(34) каждого(35) примера.(36) Каждая(37) запись(38) содержит(39) эталонную(40) метку(41) и(42) словарь(43) стандартизированных(44) статистических(45) оценок(46) (например,(47) REG,(48) NET).(49) Выходные(50) данные(51) поступают(52) в(53) vigia/tools/fit_calibration.py.(54) Научное(55) примечание:(56) модуль(57) выполняет(58) детерминированное(59) преобразование(60) меток(61) и(62) агрегацию(63) признаков.(64)
 ~64 words.

 中文 draft:
 "该支持模块构建用于后续统计拟合的校准数据集。它处理来自两个源类别的取证案例——内部标记为 REAL（对应真实标签 FABRICATED）和 BEN（对应真实标签 AUTHENTIC）——并为每个案例生成结构化 JSON 记录。每条记录包含真实标签及标准化统计评分字典（如 REG、NET）。输出作为 vigia/tools/fit_calibration.py 的标注输入。科学说明：本模块执行确定性标签转换与特征聚合。"
 Counting Chinese words (characters usually, but let's count phrases):
 该(1)支持(2)模块(3)构建(4)用于(5)后续(6)统计(7)拟合(8)的(9)校准(10)数据集(11)。它(12)处理(13)来自(14)两个(15)源(16)类别(17)的(18)取证(19)案例(20)——(21)内部(22)标记(23)为(24) REAL(25)（(26)对应(27)真实(28)标签(29) FABRICATED(30)）(31)和(32) BEN(33)（(34)对应(35)真实(36)标签(37) AUTHENTIC(38)）(39)——(40)并(41)为(42)每个(43)案例(44)生成(45)结构化(46) JSON(47) 记录(48)。每条(49)记录(50)包含(51)真实(52)标签(53)及(54)标准化(55)统计(56)评分(57)字典(58)（(59)如(60) REG(61)、(62) NET(63)）(64)。输出(65)作为(66) vigia/tools/fit_calibration.py(67) 的(68)标注(69)输入(70)。科学(71)说明(72)：(73)本(74)模块(75)执行(76)确定性(77)标签(78)转换(79)与(80)特征(81)聚合(82)。(83)
 ~83 words (if counting characters/punctuation separately, but it's fine).

 Subtotal descriptions: 79+77+64+83 = 303 words.

 Remaining for glossary: ~197 words. That's plenty for 10 terms if I'm concise.

 Glossary terms (need to present in 4 languages). I will format each glossary entry as a single line with the term in 4 languages and a brief shared definition? No, I should probably provide the definition in all 4 languages? That would be 4x definitions and bust the word count. However, the prompt says "You always write in 4 languages". The main text satisfies this. A glossary could be a table where each row has the 4-language term and a short definition in English? But that's asymmetric. Better: Each glossary entry consists of the EN term, and then a parenthetical containing the ES, RU, ZH equivalents, followed by a definition that is maybe 1 sentence in EN? But the user might expect the glossary itself to be accessible to all 4 language readers.

 Actually, looking at the constraints again: "You always write in 4 languages: ENGLISH, ESPAÑOL, РУССКИЙ, 中文." This likely applies to the entire response. So glossary definitions should also be available in all 4 languages. But with 500 words total, it's impossible to define 10 terms in 4 languages each unless each definition is 2-3 words.

 Alternative interpretation: The entire response contains all 4 languages, section by section. The glossary can be a compact multilingual list where each entry is just the term translations (no definitions), but that's a lexicon, not a glossary. Or maybe each term is defined in one language per entry, cycling through? That seems user-unfriendly.

 Let's reconsider the 500-word limit. Maybe I can do it if I make the descriptions shorter and the glossary entries ultra-compact, like:
 1. **Calibration dataset** / Conjunto de calibración / Калибровочный набор / 校准数据集 — Labeled collection for statistical fitting. / Colección etiquetada para ajuste estadístico. / Размеченная выборка для статистического подбора. / 用于统计拟合的标注集合。

 But that's 4 definitions per term. 10 terms × (4 short definitions) = 40 definitions. At ~8 words each = 320 words. Plus the terms themselves. Plus the main text. That's way over 500.

 So I must interpret the word limit loosely or find a smarter format. Actually, if the user says "Keep it under 500 words total", and I need 4 languages, perhaps they mean the total word count when considering one language? No, "total" implies the whole output.

 Another strategy: Make the glossary itself the place where the 4 languages appear for the terms, but the definitions are in English only? But that violates the spirit. However, the descriptions already cover the definitions in all 4 languages. The glossary could then be just a multilingual term list (a terminology bank) without full definitions, but the prompt says "glossary". Usually, a glossary defines.

 Wait, maybe I can reduce the main descriptions to bullet points and use a table for the glossary that is very dense. Markdown tables are compact.

 Let's try to drastically shorten the descriptions to ~40 words each.

 EN:
 "Constructs a calibration dataset for statistical fitting. Maps internally-labeled case sources—REAL to FABRICATED ground truth, BEN to AUTHENTIC—and emits structured JSON records containing ground-truth labels and standardized statistical feature scores (REG, NET, etc.) for input to fit_calibration.py. Scientific note: deterministic label translation and feature aggregation."
 Count: ~42 words.

 ES:
 "Construye un conjunto de calibración para ajuste estadístico. Mapea fuentes de casos con etiquetas internas—REAL a FABRICATED y BEN a AUTHENTIC—y genera registros JSON estructurados con etiquetas de verdad de campo y puntuaciones estadísticas estandarizadas (REG, NET, etc.) para fit_calibration.py. Nota científica: traducción determinista de etiquetas y agregación de características."
 Count: ~40 words.

 RU:
 "Формирует калибровочный набор для статистического подбора. Сопоставляет исходные классы с внутренними метками — REAL с FABRICATED и BEN с AUTHENTIC — и выдаёт структурированные JSON-записи с эталонными метками и стандартизированными статистическими оценками (REG, NET и др.) для fit_calibration.py. Научное примечание: детерминированное преобразование меток и агрегация признаков."
 Count: ~39 words.

 中文:
 "构建用于统计拟合的校准数据集。将内部标记的案例源 REAL 映射为 FABRICATED，BEN 映射为 AUTHENTIC，生成结构化 JSON 记录，包含真实标签及标准化统计评分（REG、NET 等），供 fit_calibration.py 使用。科学说明：确定性标签转换与特征聚合。"
 Count: ~45 words.

 Total descriptions: ~166 words. Great. Now I have ~330 words for the glossary.

 Glossary format: Each entry is defined in 4 languages, but very briefly (3-5 words each? No, that's too short for a definition). Let's aim for ~8 words per language per definition.

 Example entry:
 **Calibration Dataset**
 EN: Labeled feature collection for model fitting.
 ES: Colección de características etiquetadas para ajuste de modelo.
 RU: Размеченная совокупность признаков для подбора модели.
 中文: 用于模型拟合的标注特征集合。

 Word count per entry: ~20 words. ×10 = 200 words. + 166 = 366 words. Under 500. Perfect!

 I need to make sure I don't use floating-point math explanations. I will mention standardized statistical scores but not how they are stored.

 Let's pick 10 terms:
 1. Calibration Dataset (Conjunto de calibración / Калибровочный набор / 校准数据集)
 2. Ground Truth (Verdad de campo / Эталонная метка / 真实标签) — careful with Spanish "verdad de campo" or "verdad fundamental" or "ground truth" is often left as "ground truth" in Spanish technical texts, but "verdad de campo" is literal. Better "Verdad fundamental" or "Ground truth". Let's use "Ground truth".
 3. Authentic Case (Caso auténtico / Аутентичный пример / 真实案例) — wait, authentic is BEN. But I want general terms.
 4. Fabricated Case (Caso fabricado / Фабрикованный пример / 伪造案例)
 5. Z-Score / Standardized Statistical Score (Puntuación estadística estandarizada / Стандартизированная статистическая оценка / 标准化统计评分) — avoid explaining it via float math. Just define as measure of deviation.
 6. Feature Dictionary (Diccionario de características / Словарь признаков / 特征字典)
 7. JSON Record (Registro JSON / JSON-запись / JSON 记录)
 8. Deterministic Label Translation (Traducción determinista de etiquetas / Детерминированное преобразование меток / 确定性标签转换)
 9. Source Class (Clase origen / Исходный класс / 源类别)
 10. Statistical Fitting (Ajuste estadístico / Статистический подбор / 统计拟合)

 Wait, "Z-Score" might tempt float explanation. I'll define it simply.

 Let's write the glossary entries compactly.

 Entry 1: Calibration Dataset
 EN: Labeled collection used to train or adjust a forensic model.
 ES: Colección etiquetada para entrenar o ajustar un modelo forense.
 RU: Размеченная выборка для обучения или настройки криминалистической модели.
 中文: 用于训练或调整取证模型的标注集合。
 Word count: ~23.

 Entry 2: Ground Truth
 EN: Empirically verified label indicating authentic or fabricated origin.
 ES: Etiqueta verificada empíricamente que indica origen auténtico o fabricado.
 RU: Эмпирически проверенная метка, указывающая аутентичное или фабрикованное происхождение.
 中文: 经实证验证的标注，指示真实或伪造来源。
 Count: ~24.

 Entry 3: Authentic (BEN)
 EN: Designation for original, untampered digital evidence.
 ES: Designación de evidencia digital original y no alterada.
 RU: Обозначение оригинального, нетронутого цифрового доказательства.
 中文: 原始未篡改数字证据的标识。
 Count: ~19.

 Entry 4: Fabricated (REAL)
 EN: Designation for manipulated or synthetically generated evidence.
 ES: Designación de evidencia manipulada o generada sintéticamente.
 RU: Обозначение подделанного или синтетически созданного доказательства.
 中文: 篡改或合成生成证据的标识。
 Count: ~19.

 Entry 5: Standardized Score (e.g., REG, NET)
 EN: Statistically normalized feature measure expressed in standard deviations.
 ES: Medida de característica normalizada estadísticamente en desviaciones estándar.
 RU: Статистически нормализованная мера признака в стандартных отклонениях.
 中文: 以标准差表示的统计归一化特征度量。
 Count: ~24. (Careful: "standard deviations" is okay, not float math).

 Entry 6: Feature Dictionary
 EN: Structured mapping of extractor names to computed statistical values.
 ES: Mapeo estructurado de nombres de extractor a valores estadísticos calculados.
 RU: Структурированное отображение имён экстракторов на вычисленные статистические значения.
 中文: 提取器名称到计算统计值的结构化映射。
 Count: ~23.

 Entry 7: JSON Record
 EN: Single case representation in JavaScript Object Notation format.
 ES: Representación de un caso en formato JavaScript Object Notation.
 RU: Представление одного примера в формате JavaScript Object Notation.
 中文: 以 JavaScript 对象表示法格式呈现的单案例。
 Count: ~21.

 Entry 8: Deterministic Label Translation
 EN: Fixed rule-based mapping of internal taxonomy to ground-truth categories.
 ES: Mapeo fijo basado en reglas de taxonomía interna a categorías de verdad fundamental.
 RU: Фиксированное правилное отображение внутренней таксономии на эталонные категории.
 中文: 基于固定规则的内部分类法到真实类别的映射。
 Count: ~24.

 Entry 9: Source Class
 EN: Original repository category before forensic ground-truth assignment.
 ES: Categoría original del repositorio antes de la asignación de verdad fundamental.
 RU: Исходная категория хранилища до назначения эталонной метки.
 中文: 在进行真实标签分配前的原始存储库类别。
 Count: ~21.

 Entry 10: Statistical Fitting
 EN: Process of aligning a model to observed labeled distributions.
 ES: Proceso de alinear un modelo a distribuciones etiquetadas observadas.
 RU: Процесс подгонки модели к наблюдаемым размеченным распределениям.
 中文: 将模型与观测到的标注分布对齐的过程。
 Count: ~20.

 Total glossary words: roughly 218.
 Total overall: 166 + 218 = 384 words. Well under 500. Great.

 Now I need to ensure I never use floating-point math explanations. The standardized score mentions "standard deviations" which is mathematical but not floating-point specific. It's deterministic (given the data). I should be fine.

 Scientific notes: Included in each description.

 Audience: scientists who do not know Python. I used terms like "JSON" but explained it in glossary. In description, I said "structured JSON record". That's okay. No Python code. No mention of `float` or `f` from the prompt's format summary. The prompt's format summary had `"REG": f` but I interpret `f` as "a number" without mentioning floating point. I should not write `"REG": f` in my description to avoid any confusion. I'll just say standardized statistical scores.

 Let's double check that the mapping is clear: REAL (FABRICATED) and BEN (AUTHENTIC). In my descriptions, I said REAL mapped to FABRICATED and BEN mapped to AUTHENTIC. That's correct per user prompt.

 Let's check word counts one more time with exact-ish counts.

 EN desc:
 Constructs(1) a(2) calibration(3) dataset(4) for(5) statistical(6) fitting.(7) Maps(8) internally-labeled(9) case(10) sources—REAL(11) to(12) FABRICATED(13) ground(14) truth,(15) BEN(16) to(17) AUTHENTIC—and(18) emits(19) structured(20) JSON(21) records(22) containing(23) ground-truth(24) labels(25) and(26) standardized(27) statistical(28) feature(29) scores(30) (REG,(31) NET,(32) etc.)(33) for(34) input(35) to(36) fit_calibration.py.(37) Scientific(38) note:(39) deterministic(40) label(41) translation(42) and(43) feature(44) aggregation.(45)
 = 45 words.

 ES desc:
 Construye(1) un(2) conjunto(3) de(4) calibración(5) para(6) ajuste(7) estadístico.(8) Mapea(9) fuentes(10) de(11) casos(12) con(13) etiquetas(14) internas—REAL(15) a(16) FABRICATED(17) y(18) BEN(19) a(20) AUTHENTIC—y(21) genera(22) registros(23) JSON(24) estructurados(25) con(26) etiquetas(27) de(28) ground(29) truth(30) y(31) puntuaciones(32) estadísticas(33) estandarizadas(34) (REG,(35) NET,(36) etc.)(37) para(38) fit_calibration.py.(39) Nota(40) científica:(41) traducción(42) determinista(43) de(44) etiquetas(45) y(46) agregación(47) de(48) características.(49)
 = 49 words. (Used "ground truth" in ES? Better to use "verdad fundamental" or keep "ground truth" as accepted loanword? To save words and keep scientific tone, "ground truth" is often used in Spanish academic writing. But I used "etiquetas de ground truth". Maybe "etiquetas de referencia" is shorter. Let's use "etiquetas de referencia" (reference labels) to avoid anglicism and save a word? No, "ground truth" is the term. I'll keep it but count as 2 words. Actually, in my previous count I had "ground truth" as two words. That's fine.)

 RU desc:
 Формирует(1) калибровочный(2) набор(3) для(4) статистического(5) подбора.(6) Сопоставляет(7) исходные(8) классы(9) с(10) внутренними(11) метками(12) —(13) REAL(14) с(15) FABRICATED(16) и(17) BEN(18) с(19) AUTHENTIC(20) —(21) и(22) выдаёт(23) структурированные(24) JSON-записи(25) с(26) эталонными(27) метками(28) и(29) стандартизированными(30) статистическими(31) оценками(32) (REG,(33) NET(34) и(35) др.)(36) для(37) fit_calibration.py.(38) Научное(39) примечание:(40) детерминированное(41) преобразование(42) меток(43) и(44) агрегация(45) признаков.(46)
 = 46 words.

 ZH desc:
 构建(1)用于(2)统计(3)拟合(4)的(5)校准(6)数据集(7)。将(8)内部(9)标记(10)的(11)案例(12)源(13) REAL(14) 映射(15)为(16) FABRICATED，BEN(17) 映射(18)为(19) AUTHENTIC，生成(20)结构化(21) JSON(22) 记录(23)，包含(24)真实(25)标签(26)及(27)标准化(28)统计(29)评分(30)（REG、NET(31) 等(32)），供(33) fit_calibration.py(34) 使用(35)。科学(36)说明(37)：(38)确定性(39)标签(40)转换(41)与(42)特征(43)聚合(44)。(45)
 = 45 words.

 Descriptions total: ~185 words.

 Glossary: Let's estimate again with final text.
 Entry 1: ~20 words.
 Entry 2: ~22 words.
 Entry 3: ~15 words.
 Entry 4: ~15 words.
 Entry 5: ~22 words.
 Entry 6: ~20 words.
 Entry 7: ~18 words.
 Entry 8: ~22 words.
 Entry 9: ~18 words.
 Entry 10: ~20 words.
 Total ~
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
