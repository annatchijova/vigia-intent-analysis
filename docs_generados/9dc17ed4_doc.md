<!--
VIGIA Academic Documentation
Module: 9dc17ed4
Batch ID: vigia-doc-0161-9dc17ed4
Generated: 2026-05-20T14:56:47.879272+00:00
-->

The user wants an academic description in 4 languages (EN, ES, RU, 中文) for a VIGIA support module: `vigia/tools/generate_calibration.py`.

Key constraints:
1. Under 500 words total (across all 4 languages? Or total? Usually "total" means sum of all languages. Need to be very concise).
2. Include a 10-term glossary.
3. Never use floating-point math explanations for deterministic systems. (So avoid explaining things via float precision, rounding errors, etc. Use deterministic language).
4. Audience: scientists who do not know Python.
5. Academic technical writer specializing in digital forensics.
6. Content summary: Converts `vigia_60_cases_dataset.json` (artifacts with text) to format needed by `fit_calibration.py`: `[{"ground_truth": "AUTHENTIC"|"FABRICATED", "z_scores": {"SDA": f, ...}}]`. Uses SemioticDetectorV2 to derive z_scores from real text. Sin random (no randomness — deterministic).

Structure:
- EN description (brief)
- ES description (brief)
- RU description (brief)
- 中文 description (brief)
- Glossary (10 terms)

Need to keep total under 500 words. This is tight. Let's estimate:
- EN: ~60 words
- ES: ~60 words
- RU: ~60 words
- 中文: ~60 words (Chinese characters count as words? Usually yes in such counts, but to be safe, keep concise)
- Glossary: 10 terms, ~3-4 words each plus definition ~15 words = ~180 words.
Total maybe around 400-450.

Tone: Academic, formal, deterministic. No mention of Python specifics like dictionaries, lists, etc. Explain it as a data transformation module.

Key concepts to convey:
- Input: Dataset of textual artifacts (60 cases).
- Output: Structured calibration vectors (ground truth labels + derived z-scores per semiotic dimension).
- Method: SemioticDetectorV2 performs deterministic statistical derivation from text.
- Purpose: Prepares data for calibration fitting (mapping detector outputs to probabilistic/confidence space without stochastic elements).
- No randomness: fully reproducible pipeline.

Let's draft each section carefully.

EN (approx 60 words):
"The `generate_calibration` module transforms a labeled corpus of textual artifacts into calibrated feature vectors for statistical fitting. It ingests 60 case records containing raw text and ground-truth authenticity labels. Using SemioticDetectorV2, it deterministically derives standardized z-scores across semiotic dimensions such as SDA. The output schema pairs each artifact’s true class—AUTHENTIC or FABRICATED—with its derived metric profile. The process is entirely non-stochastic, ensuring full reproducibility of the calibration pipeline."

Word count EN: ~56. Good.

ES (approx 60 words):
"El módulo `generate_calibration` transforma un corpus etiquetado de artefactos textuales en vectores de características para ajuste estadístico. Procesa 60 registros con texto crudo y etiquetas de autenticidad verdaderas. Mediante SemioticDetectorV2, deriva determinísticamente puntuaciones z estandarizadas en dimensiones semióticas (p. ej., SDA). El esquema de salida vincula cada clase verdadera—AUTHENTIC o FABRICATED—con su perfil métrico. El proceso es completamente no estocástico, garantizando la reproducibilidad total del pipeline de calibración."

Word count ES: ~56. Good.

RU (approx 60 words):
"Модуль `generate_calibration` преобразует размеченный корпус текстовых артефактов в калибровочные векторы признаков для статистического подгонки. Обрабатывает 60 записей с исходным текстом и эталонными метками подлинности. С помощью SemioticDetectorV2 детерминированно выводит стандартизированные z-баллы по семиотическим измерениям (например, SDA). Выходная схема сопоставляет каждому истинному классу — AUTHENTIC или FABRICATED — производный метрический профиль. Процесс полностью недетерминированный? No, NON-stochastic = недетерминированный? Wait. Non-stochastic = нестохастический = deterministic. In Russian: 'полностью детерминированный' or 'нестохастический'. Let's use 'полностью детерминированный' to emphasize no randomness. 

Draft RU:
"Модуль `generate_calibration` преобразует размеченный корпус текстовых артефактов в калибровочные векторы для статистической подгонки. Обрабатывает 60 записей, содержащих исходный текст и эталонные метки аутентичности. Через SemioticDetectorV2 детерминированно вычисляет стандартизированные z-оценки по семиотическим измерениям (например, SDA). Выходная схема сопоставляет каждый истинный класс — AUTHENTIC или FABRICATED — с производным метрическим профилем. Процесс полностью детерминирован, обеспечивая полную воспроизводимость калибровочного конвейера."

Word count RU: ~54. Good.

中文 (approx 60 words):
"`generate_calibration` 模块将带标签的文本工件语料库转换为用于统计拟合的校准特征向量。该模块处理包含原始文本及真实性真值标签的60条记录，通过 SemioticDetectorV2 以确定性方式从文本中导出半计维度（如 SDA）的标准化 z 分数。输出格式将每个工件的真实类别（AUTHENTIC 或 FABRICATED）与其度量轮廓配对。整个过程不含随机成分，确保校准流程的完全可复现性。"

Word count 中文: ~ characters, but word count in Chinese is typically counted by characters or "words". Let's assume it's fine. It's concise.

Now glossary. Need 10 terms. Must be relevant and academic. Terms:
1. Artefacto textual / Textual artifact / Текстовый артефакт / 文本工件
2. Etiqueta de verdad de fondo / Ground-truth label / Эталонная метка / 真值标签
3. Puntuación z / z-score / z-оценка / z 分数
4. Dimensión semiótica / Semiotic dimension / Семиотическое измерение / 半计维度 (or 符号学维度). Better use 符号学维度.
5. Calibración / Calibration / Калибровка / 校准
6. Vector de características / Feature vector / Вектор признаков / 特征向量
7. Detector semiótico / Semiotic detector / Семиотический детектор / 符号学检测器
8. Pipeline de procesamiento / Processing pipeline / Конвейер обработки / 处理流程
9. Determinismo / Determinism / Детерминизм / 确定性
10. Perfil métrico / Metric profile / Метрический профиль / 度量轮廓

Wait, the user said "Include a 10-term glossary." Probably one glossary with terms in all 4 languages? Or separate? Usually a single glossary with terms defined once, maybe with translations. But the user writes "Include a 10-term glossary." Since the whole document is quadrilingual, perhaps list each term with its 4 equivalents and one definition. But that could be long. Alternatively, provide the glossary in one language? No, the prompt says "You always write in 4 languages". So the glossary should probably be presented in 4 languages too, or as a unified table. However, word count is very tight (<500 words total).

Let's calculate current word count roughly:
EN: 56
ES: 56
RU: 54
ZH: ~50 (if counting Chinese characters as roughly 1 word each, it's about 100 characters, let's say 60 words).
Total so far: ~220 words.
Remaining for glossary: ~280 words. For 10 terms, that's 28 words per term. That's doable if each entry is brief.

Format for glossary:
Maybe 4 short glossaries? No, too repetitive. Better: One glossary section with each term defined in 4 languages? That would quadruple length.

Alternative: Provide the glossary as a table where each row is a term, and columns are minimal definitions? Still heavy.

Actually, the user might accept a glossary where each term is given in 4 languages with a single concise definition that is itself translated or implied. But the instruction "You always write in 4 languages" suggests every content block should be available in 4 languages. However, a glossary is typically a list of terms and definitions. I can do:

**Glossary / Glosario / Глоссарий / 术语表**

Then for each term, present the 4 names and one definition in 4 languages? That's 4 definitions per term. 10 terms * 4 definitions * ~5 words = 200 words. Plus terms = 40. Total ~240. Plus previous 220 = 460. Under 500! Perfect. Let's try to make each definition extremely concise (~6-8 words per language).

Wait, "words total" under 500. If I write 4 definitions per term, that's 40 definitions. At ~6 words each = 240 words. Plus terms ~40. Plus the descriptions ~220. Total ~500. It's tight but possible if I'm very terse.

Let's try to design 10 terms and their definitions. Definitions should be single sentence fragments, very dense.

Terms:
1. Textual Artifact / Artefacto textual / Текстовый артефакт / 文本工件
2. Ground Truth / Verdad de fondo / Эталонная метка / 真值标签
3. z-score / puntuación z / z-оценка / z 分数
4. Semiotic Dimension / Dimensión semiótica / Семиотическое измерение / 符号学维度
5. Calibration / Calibración / Калибровка / 校准
6. Feature Vector / Vector de características / Вектор признаков / 特征向量
7. Deterministic Derivation / Derivación determinista / Детерминированное выведение / 确定性推导
8. Authenticity Label / Etiqueta de autenticidad / Метка аутентичности / 真实性标签
9. Metric Profile / Perfil métrico / Метрический профиль / 度量轮廓
10. Processing Pipeline / Pipeline de procesamiento / Конвейер обработки / 处理流程

Now definitions. Must be very short.

1. EN: Raw language sample under forensic examination.
   ES: Muestra lingüística cruda bajo examen forense.
   RU: Языковой образец, подлежащий судебно-лингвистической экспертизе.
   ZH: 接受取证检验的原始语言样本。

   Word counts: EN 7, ES 7, RU 6, ZH 9. Total ~29.

2. EN: Empirically verified class assignment.
   ES: Clasificación verificada empíricamente.
   RU: Эмпирически подтверждённое классовое назначение.
   ZH: 经实验验证的类别指定。

   Total ~25.

3. EN: Standardized deviation from a reference mean.
   ES: Desviación estandarizada respecto a una media.
   RU: Стандартизированное отклонение от эталонного среднего.
   ZH: 相对于参考均值的标准化偏差。

   Total ~26.

4. EN: Measurable axis of sign-based analysis.
   ES: Eje medible del análisis basado en signos.
   RU: Измеримая ось знакового анализа.
   ZH: 基于符号分析的可测量轴。

   Total ~24.

5. EN: Mapping detector outputs to probabilistic space.
   ES: Mapeo de salidas del detector a espacio probabilístico.
   RU: Отображение выходов детектора в вероятностное пространство.
   ZH: 将检测器输出映射至概率空间。

   Total ~28.

6. EN: Ordered set of quantitative descriptors.
   ES: Conjunto ordenado de descriptores cuantitativos.
   RU: Упорядоченный набор количественных дескрипторов.
   ZH: 定量描述符的有序集合。

   Total ~24.

7. EN: Reproducible computation without stochastic steps.
   ES: Cálculo reproducible sin pasos estocásticos.
   RU: Воспроизводимое вычисление без стохастических шагов.
   ZH: 不含随机步骤的可复现计算。

   Total ~26.

8. EN: Binary indicator of genuine or manipulated origin.
   ES: Indicador binario de origen genuino o manipulado.
   RU: Бинарный индикатор подлинного или сфабрикованного происхождения.
   ZH: 标识真实或篡改来源的二元指示符。

   Total ~29.

9. EN: Aggregate of dimension-specific scores.
   ES: Agregado de puntuaciones específicas por dimensión.
   RU: Совокупность баллов по конкретным измерениям.
   ZH: 各维度专用分数的聚合体。

   Total ~24.

10. EN: Sequential data-transformation stages.
    ES: Etapas secuenciales de transformación de datos.
    RU: Последовательные этапы преобразования данных.
    ZH: 数据转换的连续阶段。

    Total ~24.

Now let's sum up everything precisely.

EN description:
"The generate_calibration module transforms a labeled corpus of textual artifacts into calibrated feature vectors for statistical fitting. It ingests 60 case records containing raw text and ground-truth authenticity labels. Using SemioticDetectorV2, it deterministically derives standardized z-scores across semiotic dimensions such as SDA. The output schema pairs each artifact’s true class—AUTHENTIC or FABRICATED—with its derived metric profile. The process is entirely non-stochastic, ensuring full reproducibility of the calibration pipeline."
Count: The(1) generate_calibration(2) module(3) transforms(4) a(5) labeled(6) corpus(7) of(8) textual(9) artifacts(10) into(11) calibrated(12) feature(13) vectors(14) for(15) statistical(16) fitting.(17) It(18) ingests(19) 60(20) case(21) records(22) containing(23) raw(24) text(25) and(26) ground-truth(27) authenticity(28) labels.(29) Using(30) SemioticDetectorV2,(31) it(32) deterministically(33) derives(34) standardized(35) z-scores(36) across(37) semiotic(38) dimensions(39) such(40) as(41) SDA.(42) The(43) output(44) schema(45) pairs(46) each(47) artifact’s(48) true(49) class—AUTHENTIC(50) or(51) FABRICATED—with(52) its(53) derived(54) metric(55) profile.(56) The(57) process(58) is(59) entirely(60) non-stochastic,(61) ensuring(62) full(63) reproducibility(64) of(65) the(66) calibration(67) pipeline.(68)
68 words.

ES description:
"El módulo generate_calibration transforma un corpus etiquetado de artefactos textuales en vectores de características para ajuste estadístico. Procesa 60 registros con texto crudo y etiquetas de autenticidad verdaderas. Mediante SemioticDetectorV2, deriva determinísticamente puntuaciones z estandarizadas en dimensiones semióticas (p. ej., SDA). El esquema de salida vincula cada clase verdadera—AUTHENTIC o FABRICATED—con su perfil métrico. El proceso es completamente no estocástico, garantizando la reproducibilidad total del pipeline de calibración."
Count: El(1) módulo(2) generate_calibration(3) transforma(4) un(5) corpus(6) etiquetado(7) de(8) artefactos(9) textuales(10) en(11) vectores(12) de(13) características(14) para(15) ajuste(16) estadístico.(17) Procesa(18) 60(19) registros(20) con(21) texto(22) crudo(23) y(24) etiquetas(25) de(26) autenticidad(27) verdaderas.(28) Mediante(29) SemioticDetectorV2,(30) deriva(31) determinísticamente(32) puntuaciones(33) z(34) estandarizadas(35) en(36) dimensiones(37) semióticas(38) (p.(39) ej.,(40) SDA).(41) El(42) esquema(43) de(44) salida(45) vincula(46) cada(47) clase(48) verdadera—AUTHENTIC(49) o(50) FABRICATED—con(51) su(52) perfil(53) métrico.(54) El(55) proceso(56) es(57) completamente(58) no(59) estocástico,(60) garantizando(61) la(62) reproducibilidad(63) total(64) del(65) pipeline(66) de(67) calibración.(68)
68 words.

RU description:
"Модуль generate_calibration преобразует размеченный корпус текстовых артефактов в калибровочные векторы для статистической подгонки. Обрабатывает 60 записей, содержащих исходный текст и эталонные метки аутентичности. Через SemioticDetectorV2 детерминированно вычисляет стандартизированные z-оценки по семиотическим измерениям (например, SDA). Выходная схема сопоставляет каждый истинный класс — AUTHENTIC или FABRICATED — с производным метрическим профилем. Процесс полностью детерминирован, обеспечивая полную воспроизводимость калибровочного конвейера."
Count: Модуль(1) generate_calibration(2) преобразует(3) размеченный(4) корпус(5) текстовых(6) артефактов(7) в(8) калибровочные(9) векторы(10) для(11) статистической(12) подгонки.(13) Обрабатывает(14) 60(15) записей,(16) содержащих(17) исходный(18) текст(19) и(20) эталонные(21) метки(22) аутентичности.(23) Через(24) SemioticDetectorV2(25) детерминированно(26) вычисляет(27) стандартизированные(28) z-оценки(29) по(30) семиотическим(31) измерениям(32) (например,(33) SDA).(34) Выходная(35) схема(36) сопоставляет(37) каждый(38) истинный(39) класс(40) —(41) AUTHENTIC(42) или(43) FABRICATED(44) —(45) с(46) производным(47) метрическим(48) профилем.(49) Процесс(50) полностью(51) детерминирован,(52) обеспечивая(53) полную(54) воспроизводимость(55) калибровочного(56) конвейера.(57)
57 words.

ZH description:
"`generate_calibration` 模块将带标签的文本工件语料库转换为用于统计拟合的校准特征向量。该模块处理包含原始文本及真实性真值标签的60条记录，通过 SemioticDetectorV2 以确定性方式从文本中导出符号学维度（如 SDA）的标准化 z 分数。输出格式将每个工件的真实类别（AUTHENTIC 或 FABRICATED）与其度量轮廓配对。整个过程不含随机成分，确保校准流程的完全可复现性。"
Count: generate_calibration(1) 模块(2) 将(3) 带标签的(4) 文本工件(5) 语料库(6) 转换(7) 为(8) 用于(9) 统计拟合(10) 的(11) 校准特征向量。(12) 该模块(13) 处理(14) 包含(15) 原始文本(16) 及(17) 真实性(18) 真值标签的(19) 60(20) 条记录，(21) 通过(22) SemioticDetectorV2(23) 以(24) 确定性方式(25) 从(26) 文本中(27) 导出(28) 符号学维度（如(29) SDA）的(30) 标准化(31) z(32) 分数。(33) 输出格式(34) 将(35) 每个(36) 工件的(37) 真实类别（AUTHENTIC(38) 或(39) FABRICATED）(40) 与(41) 其(42) 度量轮廓(43) 配对。(44) 整个(45) 过程(46) 不含(47) 随机成分，(48) 确保(49) 校准流程(50) 的(51) 完全(52) 可复现性。(53)
53 words.

Total descriptions: 68+68+57+53 = 246 words.

Now glossary. Need to be very compact. Maybe a list format with slashes? But user wants academic. Let's do a compact table-like list but count words.

Glossary entries (I'll write them out and count):

**Glossary / Glosario / Глоссарий / 术语表**

1. **Textual artifact / Artefacto textual / Текстовый артефакт / 文本工件** — EN: Raw language sample under forensic examination. ES: Muestra lingüística cruda bajo examen forense. RU: Языковой образец, подлежащий судебно-лингвистической экспертизе. ZH: 接受取证检验的原始语言样本。
Count: Textual(1) artifact(2) /(3) Artefacto(4) textual(5) /(6) Текстовый(7) артефакт(8) /(9) 文本工件(10) —(11) EN:(12) Raw(13) language(14) sample(15) under(16) forensic(17) examination.(18) ES:(19) Muestra(20) lingüística(21) cruda(22) bajo(23) examen(24) forense.(25) RU:(26) Языковой(27) образец,(28) подлежащий(29) судебно-лингвистической(30) экспертизе.(31) ZH:(32) 接受取证检验的原始语言样本。(33) -> 33 words.

2. **Ground truth / Verdad de fondo / Эталонная метка / 真值标签** — EN: Empirically verified class assignment. ES: Clasificación verificada empíricamente. RU: Эмпирически подтверждённое классовое назначение. ZH: 经实验验证的类别指定。
Count: Ground(1) truth(2) /(3) Verdad(4) de(5) fondo(6) /(7) Эталонная(8) метка(9) /(10) 真值标签(11) —(12) EN:(13) Empirically(14) verified(15) class(16) assignment.(17) ES:(18) Clasificación(19) verificada(20) empíricamente.(21) RU:(22) Эмпирически(23) подтверждённое(24) классовое(25) назначение.(26) ZH:(27) 经实验验证的类别指定。(28) -> 28 words.

3. **z-score / puntuación z / z-оценка / z 分数** — EN: Standardized deviation from a reference mean. ES: Desviación estandarizada respecto a una media. RU: Стандартизированное отклонение от эталонного среднего. ZH: 相对于参考均值的标准化偏差。
Count: z-score(1) /(2) puntuación(3) z(4) /(5) z-оценка(6) /(7) z(8) 分数(9) —(10) EN:(11) Standardized(12) deviation(13) from(14) a(15) reference(16) mean.(17) ES:(18) Desviación(19) estandarizada(20) respecto(21) a(22) una(23) media.(24) RU:(25) Стандартизированное(26) отклонение(27) от(28) эталонного(29) среднего.(30) ZH:(31) 相对于参考均值的标准化偏差。(32) -> 32 words.

4. **Semiotic dimension / Dimensión semiótica / Семиотическое измерение / 符号学维度** — EN: Measurable axis of sign-based analysis. ES: Eje medible del análisis basado en signos. RU: Измеримая ось знакового анализа. ZH: 基于符号分析的可测量轴。
Count: Semiotic(1) dimension(2) /(3) Dimensión(4) semiótica(5) /(6) Семиотическое(7) измерение(8) /(9) 符号学维度(10) —(11) EN:(12) Measurable(13) axis(14) of(15) sign-based(16) analysis.(17) ES:(18) Eje(19) medible(20) del(21) análisis(22) basado(23) en(24) signos.(25) RU:(26) Измеримая(27) ось(28) знакового(29) анализа.(30) ZH:(31) 基于符号分析的可测量轴。(32) -> 32 words.

5. **Calibration / Calibración / Калибровка / 校准** — EN: Mapping detector outputs to probabilistic space. ES: Mapeo de salidas del detector a espacio probabilístico. RU: Отображение выходов детектора в вероятностное пространство. ZH: 将检测器输出映射至概率空间。
Count: Calibration(1) /(2) Calibración(3) /(4) Калибровка(5) /(6) 校准(7) —(8) EN:(9) Mapping(10) detector(11) outputs(12) to(13) probabilistic(14) space.(15) ES:(16) Mapeo(17) de(18) salidas(19) del(20) detector(21) a(22) espacio(23) probabilístico.(24) RU:(25) Отображение(26) выходов(27) детектора(28) в(29) вероятностное(30) пространство.(31) ZH:(32) 将检测器输出映射至概率空间。(33) -> 33 words.

6. **Feature vector / Vector de características / Вектор признаков / 特征向量** — EN: Ordered set of quantitative descriptors. ES: Conjunto ordenado de descriptores cuantitativos. RU: Упорядоченный набор количественных дескрипторов. ZH: 定量描述符的有序集合。
Count: Feature(1) vector(2) /(3) Vector(4) de(5) características(6) /(7) Вектор(8) признаков(9) /(10) 特征向量(11) —(12) EN:(13) Ordered(14) set(15) of(16) quantitative(17) descriptors.(18) ES:(19) Conjunto(20) ordenado(21) de(22) descriptores(23) cuantitativos.(24) RU:(25) Упорядоченный(26) набор(27) количественных(28) дескрипторов.(29) ZH:(30) 定量描述符的有序集合。(31) -> 31 words.

7. **Deterministic derivation / Derivación determinista / Детерминированное выведение / 确定性推导** — EN: Reproducible computation without stochastic steps. ES: Cálculo reproducible sin pasos estocásticos. RU: Воспроизводимое вычисление без стохастических шагов. ZH: 不含随机步骤的可复现计算。
Count: Deterministic(1) derivation(2) /(3) Derivación(4) determinista(5) /(6) Детерминированное(7) выведение(8) /(9) 确定性推导(10) —(11) EN:(12) Reproducible(13) computation(14) without(15) stochastic(16) steps.(17) ES:(18) Cálculo(19) reproducible(20) sin(21) pasos(22) estocásticos.(23) RU:(24) Воспроизводимое(25) вычисление(26) без(27) стохастических(28) шагов.(29) ZH:(30) 不含随机步骤的可复现计算。(31) -> 31 words.

8. **Authenticity label / Etiqueta de autenticidad / Метка аутентичности / 真实性标签** — EN: Binary indicator of genuine or manipulated origin. ES: Indicador binario de origen genuino o manipulado. RU: Бинарный индикатор подлинного или сфабрикованного происхождения. ZH: 标识真实或篡改来源的二元指示符。
Count: Authenticity(1) label(2) /(3) Etiqueta(4) de(5) autenticidad(6) /(7) Метка(8) аутентичности(9) /(10) 真实性标签(11) —(12) EN:(13) Binary(14) indicator(15) of(16) genuine(17) or(18) manipulated(19) origin.(20) ES:(21) Indicador(22) binario(23) de(24) origen(25) genuino(26) o(27) manipulado.(28) RU:(29) Бинарный(30) индикатор(31) подлинного(32) или(33) сфабрикованного(34) происхождения.(35) ZH:(36) 标识真实或篡改来源的二元指示符。(37) -> 37 words.

9. **Metric profile / Perfil métrico / Метрический профиль / 度量轮廓** — EN: Aggregate of dimension-specific scores. ES: Agregado de puntuaciones específicas por dimensión. RU: Совокупность баллов по конкретным измерениям. ZH: 各维度专用分数的聚合体。
Count: Metric(1) profile(2) /(3) Perfil(4) métrico(5) /(6) Метрический(7) профиль(8) /(9) 度量轮廓(10) —(11) EN:(12) Aggregate(13) of(14) dimension-specific(15) scores.(16) ES:(17) Agregado(18) de(19) puntuaciones(20) específicas(21) por(22) dimensión.(23) RU:(24) Совокупность(25) баллов(26) по(27) конкретным(28) измерениям.(29) ZH:(30) 各维度专用分数的聚合体。(31) -> 31 words.

10. **Processing pipeline / Pipeline de procesamiento / Конвейер обработки / 处理流程** — EN: Sequential data-transformation stages. ES: Etapas secuenciales de transformación de datos. RU: Последовательные этапы преобразования данных. ZH: 数据转换的连续阶段。
Count: Processing(1) pipeline(2) /(3) Pipeline(4) de(5) procesamiento(6) /(7) Конвейер(8) обработки(9) /(10) 处理流程(11) —(12) EN:(13) Sequential(14) data-transformation(15) stages.(16) ES:(17) Etapas(18) secuenciales(19) de(20) transformación(21) de(22) datos.(23) RU:(24) Последовательные(25) этапы(26) преобразования(27) данных.(28) ZH:(29) 数据转换的连续阶段。(30) -> 30 words.

Now let's sum glossary word counts:
33+28+32+32+33+31+31+37+31+30 = 318 words.

Total: 246 + 318 = 564 words. That's over 500.

I need to cut. I must get under 500. Let's reduce glossary definitions drastically. Maybe combine definitions into one per term but keep 4 languages? No, I need all 4 languages.

Alternative: Instead of giving full sentence definitions in 4 languages for each term, provide a single concise definition per term, but present the term in 4 languages. But the instruction says "You always write in 4 languages". Does a glossary entry with terms in 4 languages and definition in only one violate that? Probably yes. But maybe I can make the definition a very short phrase in 4 languages using a compact format.

Wait, maybe I can reduce the descriptions to bare minimum to save words.

Revised EN:
"The generate_calibration module converts a labeled textual corpus into feature vectors for statistical fitting. From 60 case records with raw text and ground-truth labels, SemioticDetectorV2 deterministically derives standardized z-scores across semiotic dimensions (e.g., SDA). Each output record maps a true class—AUTHENTIC or FABRICATED—to its metric profile. The workflow contains no stochastic steps, ensuring full reproducibility."
Count: The(1) generate_calibration(2) module(3) converts(4) a(5) labeled(6) textual(7) corpus(8) into(9) feature(10) vectors(11) for(12) statistical(13) fitting.(14) From(15) 60(16) case(17) records(18) with(19) raw(20) text(21) and(22) ground-truth(23) labels,(24) SemioticDetectorV2(25) deterministically(26) derives(27) standardized(28) z-scores(29) across(30) semiotic(31) dimensions(32) (e.g.,(33) SDA).(34) Each(35) output(36) record(37) maps(38) a(39) true(40) class—AUTHENTIC(41) or(42) FABRICATED—to(43) its(44) metric(45) profile.(46) The(47) workflow(48)
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
