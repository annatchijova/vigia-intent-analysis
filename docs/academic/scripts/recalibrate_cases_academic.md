<!--
VIGIA Academic Documentation
Module: 13bb704b
Batch ID: vigia-doc-0006-13bb704b
Generated: 2026-05-20T14:56:47.846269+00:00
-->

---
doc_hash: 13bb704b
module: unknown
languages: [EN, ES, RU, ZH]
generated_by: moonshot-kimi-k2.6-batch-api
license: Apache-2.0
---

ENGLISH:
"The `recalibrate_cases.py` module synchronizes stored expected verdicts within case JSON files against the current EBS v1 scorer logic, including all applied patches. It restricts modifications to cases outside the `KNOWN_LIMITATIONS` registry; items with documented limitations are logged for review but preserved unchanged. This ensures the reference dataset remains aligned with deterministic system behavior without altering acknowledged boundary conditions."

Word count EN: ~50 words.

ESPAÑOL:
"El módulo `recalibrate_cases.py` actualiza los veredictos esperados almacenados en los archivos JSON de casos para reflejar la lógica actual del evaluador EBS v1 y todos sus parches. Solo modifica casos ausentes en el registro `KNOWN_LIMITATIONS`; los casos con limitaciones documentadas se registran para revisión pero se preservan intactos. Así se mantiene el conjunto de referencia sincronizado con el comportamiento determinista del sistema."

Word count ES: ~52 words.

РУССКИЙ:
"Модуль `recalibrate_cases.py` синхронизирует ожидаемые вердикты в JSON-файлах кейсов с текущей логикой скорера EBS v1 и всеми установленными патчами. Изменения применяются только к кейсам, отсутствующим в реестре `KNOWN_LIMITATIONS`; кейсы с задокументированными ограничениями фиксируются в журнале, но остаются неизменными. Это обеспечивает соответствие эталонного набора детерминированному поведению системы."

Word count RU: ~45 words.

中文:
"`recalibrate_cases.py` 模块将案例 JSON 文件中的预期判决与当前 EBS v1 评分器逻辑（含全部补丁）进行同步。仅对不在 `KNOWN_LIMITATIONS` 登记册中的案例进行修改；已记录限制的案例会被记录备查但保持原状。此举确保参考数据集与系统确定性行为保持一致，同时不触碰已知的边界条件。"

Word count ZH: ~30 words.

Total body: ~177 words. Good.

Now glossary. Need 10 terms. Let's pick terms from the domain:
1. Expected verdict
2. Case JSON
3. Scorer (EBS v1)
4. Patch
5. Known limitations registry
6. Deterministic system
7. Reference dataset
8. Boundary conditions
9. Recalibration
10. Log / Audit trail

I will present as a table with 4 columns to save words.

Row format: Term | ESPAÑOL | РУССКИЙ | 中文

Wait, the prompt says "Include a 10-term glossary." Since the main text is in 4 languages, the glossary should probably define terms in all 4 languages or be multilingual. A table is best.

Let's draft each term concisely.

1. Expected verdict
EN: The ground-truth outcome predicted for a case.
ES: Resultado de verdad de referencia previsto para un caso.
RU: Эталонный ожидаемый результат для кейса.
ZH: 针对案例预设的基准真值结果。

2. Case JSON
EN: Structured text file storing a single case’s parameters.
ES: Archivo de texto estructurado que almacena los parámetros de un caso.
RU: Структурированный текстовый файл с параметрами кейса.
ZH: 存储单个案例参数的结构化文本文件。

3. EBS v1 Scorer
EN: Deterministic evaluation engine for rendering verdicts.
ES: Motor de evaluación determinista que emite veredictos.
RU: Детерминированный вычислительный модуль для формирования вердиктов.
ZH: 用于生成判决的确定性评估引擎。

4. Patch
EN: A targeted update to system logic without full replacement.
ES: Actualización puntual de la lógica del sistema.
RU: Целевое обновление логики системы.
ZH: 针对系统逻辑的局部更新。

5. Known Limitations
EN: Catalog of documented boundary conditions exempt from change.
ES: Catálogo de condiciones límite documentadas exentas de cambio.
RU: Реестр задокументированных граничных условий, исключённых из изменений.
ZH: 免于修改的已记录边界条件目录。

6. Deterministic System
EN: System where identical inputs always produce identical outputs.
ES: Sistema en el que entradas idénticas producen siempre salidas idénticas.
RU: Система, в которой одинаковые входные данные всегда дают одинаковый результат.
ZH: 相同输入始终产生相同输出的系统。

7. Reference Dataset
EN: Collection of validated cases used as a behavioral baseline.
ES: Conjunto de casos validados usados como línea base de comportamiento.
RU: Набор валидированных кейсов, используемый в качестве поведенческого базиса.
ZH: 用作行为基线的已验证案例集合。

8. Recalibration
EN: Process of aligning expected values with current system logic.
ES: Proceso de alineación de valores esperados con la lógica actual del sistema.
RU: Процесс приведения ожидаемых значений в соответствие с текущей логикой системы.
ZH: 将预期值与当前系统逻辑对齐的过程。

9. Boundary Conditions
EN: Operational limits where standard behavior is defined or constrained.
ES: Límites operativos donde el comportamiento estándar se define o restringe.
RU: Операционные пределы, в рамках которых стандартное поведение определено или ограничено.
ZH: 标准行为被定义或受限的运行边界。

10. Audit Log
EN: Immutable record of reported but unchanged limited cases.
ES: Registro inmutable de casos limitados reportados pero no modificados.
RU: Неизменяемая запись о зафиксированных, но не изменённых ограниченных кейсах.
ZH: 对已报告但未修改的限制案例的不可变记录。

Now let's count glossary words roughly. Each entry ~12 words x 4 languages = ~48 words per entry? No, that's too much. Wait, I need to count carefully.

Actually, I can make the glossary terms very concise. Let's rewrite to be tighter and maybe have a header row.

Table:
| Term (English) | Español | Русский | 中文 |
|---|---|---|---|
| Expected verdict | Veredicto de referencia previsto. | Ожидаемый вердикт. | 预期判决。 |
| Case JSON | Archivo JSON de caso: parámetros estructurados. | JSON-файл кейса: структурированные параметры. | 案例 JSON：结构化参数文件。 |
| EBS v1 scorer | Evaluador determinista de veredictos. | Детерминированный модуль оценки. | 确定性判决评估引擎。 |
| Patch | Corrección puntual de lógica. | Целевое исправление логики. | 逻辑补丁。 |
| Known limitations | Registro de condiciones límite documentadas. | Реестр задокументированных ограничений. | 已知限制登记册。 |
| Deterministic system | Salida idéntica para entrada idéntica. | Одинаковый выход при одинаковом входе. | 相同输入产生相同输出。 |
| Reference dataset | Conjunto base validado. | Валидированный эталонный набор. | 经验证的基准数据集。 |
| Recalibration | Alineación de valores esperados. | Приведение ожидаемых значений в соответствие. | 重新对齐预期值。 |
| Boundary conditions | Límites operativos del sistema. | Граничные условия работы системы. | 系统运行边界条件。 |
| Audit log | Registro inmutable de revisión. | Неизменяемый журнал фиксации. | 不可变审查日志。 |

This is very concise, maybe ~60-80 words total.

Let's verify the total word count.

EN text: 46 words.
ES text: 51 words.
RU text: 44 words.
ZH text: let's count. `recalibrate_cases.py` (1) 模块将案例 JSON 文件中的预期判决与当前 EBS v1 评分器逻辑（含全部补丁）进行同步。仅对不在 `KNOWN_LIMITATIONS` 登记册中的案例进行修改；已记录限制的案例会被记录备查但保持原状。此举确保参考数据集与系统确定性行为保持一致，同时不触碰已知的边界条件。
Count: 1+模块(1)+将(1)+案例(1)+JSON(1)+文件(1)+中的(1)+预期(1)+判决(1)+与(1)+当前(1)+EBS(1)+v1(1)+评分器(1)+逻辑(1)+含(1)+全部(1)+补丁(1)+进行(1)+同步(1)。仅(1)+对(1)+不在(1)+KNOWN_LIMITATIONS(1)+登记册(1)+中的(1)+案例(1)+进行(1)+修改(1)；已(1)+记录(1)+限制(1)+的(1)+案例(1)+会(1)+被(1)+记录(1)+备查(1)+但(1)+保持(1)+原状(1)。此举(1)+确保(1)+参考(1)+数据集(1)+与(1)+系统(1)+确定性(1)+行为(1)+保持(1)+一致(1)，同时(1)+不(1)+触碰(1)+已知(1)+的(1)+边界(1)+条件(1)。 = ~56 words/tokens? In Chinese word count usually characters are counted or spaces? The user said under 500 words. For mixed text, Chinese characters often count as words. Even if so, it's around 60. Total ~200 words. Glossary maybe ~80 words. Total ~280. Well under 500.

Wait, I need to make sure I don't use floating-point math explanations. I didn't.

Let's check for any Python jargon. The user said scientists who do not know Python. I used "module", "JSON files", `KNOWN_LIMITATIONS`. These are domain terms but not Python-specific syntax explanations. I should avoid terms like "dictionary", "list", "script". I used "module" which is fine. I used "JSON files" which is a data format, not Python-specific. I think it's okay.

Let's refine the EN text to ensure academic tone.
"The `recalibrate_cases.py` module synchronizes the `expected_verdict` field in case JSON files with the current deterministic logic of the EBS v1 scorer, inclusive of all applied patches. It restricts write operations to cases absent from the `KNOWN_LIMITATIONS` registry; documented limitation cases are logged for audit but preserved unchanged. This maintains reference dataset integrity while respecting established boundary conditions."

46 words. Good.

ES:
"El módulo `recalibrate_cases.py` sincroniza el campo `expected_verdict` en los archivos JSON de casos con la lógica determinista actual del evaluador EBS v1, incluidos todos los parches aplicados. Restringe las operaciones de escritura a casos ausentes del registro `KNOWN_LIMITATIONS`; los casos con limitaciones documentadas se registran para auditoría pero se preservan sin cambios. Así se mantiene la integridad del conjunto de referencia respetando las condiciones límite establecidas."

53 words.

RU:
"Модуль `recalibrate_cases.py` синхронизирует поле `expected_verdict` в JSON-файлах кейсов с текущей детерминированной логикой скорера EBS v1 с учётом всех применённых патчей. Запись изменений ограничена кейсами, отсутствующими в реестре `KNOWN_LIMITATIONS`; кейсы с задокументированными ограничениями фиксируются в журнале аудита, но сохраняются неизменными. Это поддерживает целостность эталонного набора с соблюдением установленных граничных условий."

52 words.

ZH:
"`recalibrate_cases.py` 模块将案例 JSON 文件中的 `expected_verdict` 字段与当前 EBS v1 评分器的确定性逻辑（含全部已应用补丁）进行同步。写操作仅针对不在 `KNOWN_LIMITATIONS` 登记册中的案例；已记录限制的案例记入审计日志但原样保留。由此在尊重已确立边界条件的同时维护参考数据集的完整性。"

Let's count Chinese characters/words:
recalibrate_cases.py(1) 模块(2)将(3)案例(4)JSON(5)文件(6)中的(7)expected_verdict(8)字段(9)与(10)当前(11)EBS(12)v1(13)评分器(14)的(15)确定性(16)逻辑(17)含(18)全部(19)已应用(20)补丁(21)进行(22)同步(23)。写操作(24)仅(25)针对(26)不在(27)KNOWN_LIMITATIONS(28)登记册(29)中的(30)案例(31)；已记录(32)限制(33)的(34)案例(35)记入(36)审计(37)日志(38)但(39)原样(40)保留(41)。由此(42)在(43)尊重(44)已确立(45)边界条件(46)的(47)同时(48)维护(49)参考(50)数据集(51)的(52)完整性(53)。
53 units. Good.

Total narrative: ~204 words.

Now glossary. Let's make it tight.

| Term (EN) | Español | Русский | 中文 |
|---|---|---|---|
| Expected verdict | Veredicto de referencia previsto. | Ожидаемый вердикт. | 预期判决。 |
| Case JSON | Archivo estructurado de parámetros del caso. | Структурированный файл параметров кейса. | 案例结构化参数文件。 |
| EBS v1 scorer | Evaluador determinista de veredictos. | Детерминированный модуль оценки. | 确定性判决评估引擎。 |
| Patch | Actualización puntual de la lógica del sistema. | Целевое обновление логики системы. | 系统逻辑局部更新。 |
| Known limitations | Registro de condiciones límite documentadas. | Реестр задокументированных ограничений. | 已记录限制登记册。 |
| Deterministic system | Sistema cuya salida es idéntica para entrada idéntica. | Система с идентичным выходом при идентичном входе. | 相同输入产生相同输出的系统。 |
| Reference dataset | Conjunto de casos validados como línea base. | Валидированный эталонный набор данных. | 经验证的基准数据集。 |
| Recalibration | Alineación de valores esperados con la lógica actual. | Приведение ожидаемых значений к текущей логике. | 将预期值与当前逻辑对齐。 |
| Boundary conditions | Límites operativos definidos o restringidos. | Определённые или ограниченные операционные пределы. | 被定义或受限的运行边界。 |
| Audit log | Registro inmutable de eventos de revisión. | Неизменяемый журнал событий проверки. | 不可变的审查事件记录。 |

Let's roughly count glossary words.
Row 1: 4 + 4 + 3 + 3 = 14
Row 2: 3 + 5 + 4 + 4 = 16
Row 3: 4 + 4 + 4 + 4 = 16
Row 4: 2 + 6 + 4 + 4 = 16
Row 5: 3 + 5 + 3 + 3 = 14
Row 6: 3 + 7 + 6 + 5 = 21
Row 7: 3 + 6 + 4 + 4 = 17
Row 8: 3 + 6 + 5 + 5 = 19
Row 9: 3 + 4 + 4 + 4 = 15
Row 10: 3 + 5 + 4 + 4 = 16
Total ~164 words.
Grand total ~368 words. Under 500. Perfect.

One thing: The user said "You NEVER use floating-point math explanations for deterministic systems." I didn't mention floating point. I mentioned "deterministic logic" and "deterministic system". This is fine.

Also need scientific notes? The persona says "You include glossaries and scientific notes." Maybe I should add a brief scientific note? But word count is tight. I can include a short note in each language or one consolidated note? The user said "brief academic description... Include a 10-term glossary." Given the strict word limit, a "Scientific Note" could be a single sentence italicized or something. But the prompt didn't explicitly ask for scientific notes this time, it's part of the persona. However, I should try to include at least one brief note if possible, or maybe the glossary counts? No, glossary is separate. Let me see if I can add a small "Nota científica / Научное примечание / Scientific note / 科学注" section without blowing word count.

Maybe integrate it into the text? Like "Scientific note: This process assumes the scorer behaves as a deterministic finite-state function; therefore, divergence between stored and rendered verdicts indicates a schema or logic update rather than computational indeterminacy."

That might be too many words. But I can add a very short note:
"[Scientific note: The scorer is modeled as a deterministic state function; divergence implies schema drift, not stochastic variance.]"

But this is EN only. The user wants 4 languages. Maybe skip the explicit note section to respect the word limit, as the user specifically asked for "brief academic description" and "Keep it under 500 words total." The persona says "You include glossaries and scientific notes" but under a strict constraint, I might need to balance. I think I'll add a very brief single scientific note in English only after the EN paragraph, or perhaps a multilingual sentence? No, that would clutter.

Actually, I can make the "Scientific note" part of the EN paragraph? No.

Let's reconsider. The user wants total under 500 words. If I add 4 scientific notes (one per language), that's extra ~40-60 words. Still under 500. Let's try.

EN Scientific note: *Scientific note: Because the EBS v1 scorer is deterministic, any mismatch between stored and rendered verdicts indicates a logic revision rather than stochastic variance.*
(~20 words)

ES Nota científica: *Nota científica: dado que el evaluador EBS v1 es determinista, cualquier discrepancia entre el veredicto almacenado y el emitido indica una revisión lógica y no una variación estocástica.*
(~24 words)

RU Научное примечание: *Научное примечание: поскольку скорер EBS v1 детерминирован, любое несоответствие между сохранённым и вычисленным вердиктом свидетельствует о логической ревизии, а не о стохастическом разбросе.*
(~23 words)

ZH 科学注释: *科学注释：由于 EBS v1 评分器具有确定性，存储判决与生成判决之间的任何差异均表明逻辑修订，而非随机方差。*
(~20 words)

Total added: ~87 words. New total ~290 + 87 = ~377. Still under 500. But wait, I must ensure I don't use floating-point math explanations. I used "deterministic" and said mismatch indicates logic revision not stochastic variance. This avoids floating point. Good.

However, does the user want the scientific note to be separate? The persona says "You include glossaries and scientific notes." I'll include them as a short parenthetical or italicized sentence after each paragraph. It adds value for scientists.

Let me recount total words with this addition.

EN para: 46 words.
EN note: 20 words.
Total EN: 66.

ES para: 53 words.
ES note: 24 words.
Total ES: 77.

RU para: 52 words.
RU note: 23 words.
Total RU: 75.

ZH para: 53 words.
ZH note: 20 words.
Total ZH: 73.

Narrative total: 291 words.
Glossary: ~164 words.
Grand total: ~455 words. Under 500. Perfect.

Let's double-check that no floating-point explanation is used. The note mentions deterministic and stochastic variance. No mention of floats. Good.

Let's verify the EN text doesn't sound too Pythonic. "Module", "field", "JSON files", "registry", "logged for audit". These are accessible to scientists.

One final check on Russian: "скорера" is transliteration, fine. "JSON-файлах" fine.
Spanish: "evaluador" for scorer. Good. "condiciones límite" for boundary conditions. Good.
Chinese: "评分器" for scorer. Good. "登记册" for registry. Good.

The user wrote the summary in Spanish ("Actualiza expected_verdict..."). They might be Spanish speaker, but all 4 languages are required.

Let's ensure the glossary headers don't count too much, but they will. Still okay.

I should present cleanly.

Layout:
**ENGLISH** [text] *Scientific note: ...*

**ESPAÑOL** [text] *Nota científica: ...*

**РУССКИЙ** [text] *Научное примечание: ...*

**中文** [text] *科学注释：...*

**Glossary / Glosario / Глоссарий / 词汇表**
[Table]

I need to make sure the word count is strictly under 500. Let's do a precise count.

EN:
The(1) `recalibrate_cases.py`(2) module(3) synchronizes(4) the(5) `expected_verdict`(6) field(7) in(8) case(9) JSON(10) files(11) with(12) the(13) current(14) deterministic(15) logic(16) of(17) the(18) EBS(19) v1(20) scorer,(21) inclusive(22) of(23) all(24) applied(25) patches.(26) It(27) restricts(28) write(29) operations(30) to(31) cases(32) absent(33) from(34) the(35) `KNOWN_LIMITATIONS`(36) registry;(37) documented(38) limitation(39) cases(40) are(41) logged(42) for(43) audit(44) but(45) preserved(46) unchanged.(47) This(48) maintains(49) reference(50) dataset(51) integrity(52) while(53) respecting(54) established(55) boundary(56) conditions.(57)
Scientific(1) note:(2) Because(3) the(4) EBS(5) v1(6) scorer(7) is(8) deterministic,(9) any(10) mismatch(11) between(12) stored(13) and(14) rendered(15) verdicts(16) indicates(17) a(18) logic(19) revision(20) rather(21) than(22) stochastic(23) variance.(24)
EN total: 57+24 = 81.

ES:
El(1) módulo(2) `recalibrate_cases.py`(3) sincroniza(4) el(5) campo(6) `expected_verdict`(7) en(8) los(9) archivos(10) JSON(11) de(12) casos(13) con(14) la(15) lógica(16) determinista(17) actual(18) del(19) evaluador(20) EBS(21) v1,(22) incluidos(23) todos(24) los(25) parches(26) aplicados.(27) Restringe(28) las(29) operaciones(30) de(31) escritura(32) a(33) casos(34) ausentes(35) del(36) registro(37) `KNOWN_LIMITATIONS`;(38) los(39) casos(40) con(41) limitaciones(42) documentadas(43) se(44) registran(45) para(46) auditoría(47) pero(48) se(49) preservan(50) sin(51) cambios.(52) Así(53) se(54) mantiene(55) la(56) integridad(57) del(58) conjunto(59) de(60) referencia(61) respetando(62) las(63) condiciones(64) límite(65) establecidas.(66)
Nota(1) científica:(2) dado(3) que(4) el(5) evaluador(6) EBS(7) v1(8) es(9) determinista,(10) cualquier(11) discrepancia(12) entre(13) el(14) veredicto(15) almacenado(16) y(17) el(18) emitido(19) indica(20) una(21) revisión(22) lógica(23) y(24) no(25) una(26) variación(27) estocástica.(28)
ES total: 66+28 = 94.

RU:
Модуль(1) `recalibrate_cases.py`(2) синхронизирует(3) поле(4) `expected_verdict`(5) в(6) JSON-файлах(7) кейсов(8) с(9) текущей(10) детерминированной(11) логикой(12) скорера(13) EBS(14) v1(15) с(16) учётом(17) всех(18) применённых(19) патчей.(20) Запись(21) изменений(22) ограничена(23) кейсами,(24) отсутствующими(25) в(26) реестре(27) `KNOWN_LIMITATIONS`;(28) кейсы(29) с(30) задокументированными(31) ограничениями(32) фиксируются(33) в(34) журнале(35) аудита,(36) но(37) сохраняются(38) неизменными.(39) Это(40) поддерживает(41) целостность(42) эталонного(43) набора(44) с(45) соблюдением(46) установленных(47) граничных(48) условий.(49)
Научное(1) примечание:(2) поскольку(3) скорер(4) EBS(5) v1(6) детерминирован,(7) любое(8) несоответствие(9) между(10) сохранённым(11) и(12) вычисленным(13) вердиктом(14) свидетельствует(15) о(16) логической(17) ревизии,(18) а(19) не(20) о(21) стохастическом(22) разбросе.(23)
RU total: 49+23 = 72.

ZH:
`recalibrate_cases.py`(1) 模块(2)将(3)案例(4) JSON(5)文件(6)中的(7) `expected_verdict`(8)字段(9)与(10)当前(11) EBS(12) v1(13)评分器(14)的(15)确定性(16)逻辑(17)（含(18)全部(19)已应用(20)补丁(21)）进行(22)同步(23)。写操作(24)仅(25)针对(26)不在(27) `KNOWN_LIMITATIONS`(28)登记册(29)中的(30)案例(31)；已记录(32)限制(33)的(34)案例(35)记入(36)审计(37)日志(38)但(39)原样(40)保留(41)。由此(42)在(43)尊重(44)已确立(45)边界条件(46)的(47)同时(48)维护(49)参考(50)数据集(51)的(52)完整性(53)。
科学注释(1)：由于(2) EBS(3) v1(4)评分器(5)具有(6)确定性(7)，存储(8)判决(9)与(10)生成(11)判决(12)之间(13)的(14)任何(15)差异(16)均(17)表明(18)逻辑(19)修订(20)，而非(21)随机(22)方差(23)。
ZH total: 53+23 = 76.

Narrative sum: 81+94+72+76 = 323 words.

Glossary count. I need to be careful. Let's assign each cell a word count.

Row 1: Expected(1) verdict(2) | Veredicto(1) de(2) referencia(3) previsto.(4) | Ожидаемый(1) вердикт.(2) | 预期判决。(1)
-> 2+4+2+1 = 9

Row 2: Case(1) JSON(2) | Archivo(1) estructurado(2) de(3) parámetros(4) del(5) caso.(6) | Структурированный(1) файл(2) параметров(3) кейса.(4) | 案例结构化参数文件。(1)
-> 2+6+4+1 = 13

Row 3: EBS(1) v1(2) scorer(3) | Evaluador(1) determinista(2) de(3) veredictos.(4) | Детерминированный(1) модуль(2) оценки.(3) | 确定性判决评估引擎。(1)
-> 3+4+3+1 = 11

Row 4: Patch(1) | Actualización(1) puntual(2) de(3) la(4) lógica(5) del(6) sistema.(7) | Целевое(1) обновление(2) логики(3) системы.(4) | 系统逻辑局部更新。(1)
-> 1+7+4+1 = 13

Row 5: Known(1) limitations(2) | Registro(1) de(2) condiciones(3) límite(4) documentadas.(5) | Реестр(1) задокументированных(2) ограничений.(3) | 已记录限制登记册。(1)
-> 2+5+3+1 = 11

Row 6: Deterministic(1) system(2) | Sistema(1) cuya(2) salida(3) es(4) idéntica(5) para(6) entrada(7) idéntica.(8) | Система(1) с(2) идентичным(3) выходом(4) при(5) идентичном(6) входе.(7) | 相同输入产生相同输出的系统。(1)
-> 2+8+7+1 = 18

Row 7: Reference(1) dataset(2) | Conjunto(1) de(2) casos(3) validados(4) como(5) línea(6) base.(7) | Валидированный(1) эталонный(2) набор(3) данных.(4) | 经验证的基准数据集。(1)
-> 2+7+4+1 = 14

Row 8: Recalibration(1) | Alineación(1) de(2) valores(3) esperados(4) con(5) la(6) lógica(7) actual.(8) | Приведение(1) ожидаемых(2) значений(3) к(4) текущей(5) логике.(6) | 将预期值与当前逻辑对齐。(1)
-> 1+8+6+1 = 16

Row 9: Boundary(1) conditions(2) | Límites(1) operativos(2) definidos(3) o(4) restringidos.(5) | Определённые(1) или(2) ограниченные(3) операционные(4) пределы.(5) | 被定义或受限的运行边界。(1)
-> 2+5+5+1 = 13

Row 10: Audit(1) log(2) | Registro(1) inmutable(2) de(3) eventos(4) de(5) revisión.(6) | Неизменяемый(1) журнал(2) событий(3) проверки.(4) | 不可变的审查事件记录。(1)
-> 2+6+4+1 = 13

Glossary sum: 9+13+11+13+11+18+14+16+13+13 = 131 words.

Grand total: 323 + 131 = 454 words. Under 500. Great.

Wait, the headers for the table also have words: "Term (EN)", "Español", "Русский", "中文". That's 4 words. And maybe section headers. Let's count them too.
"Glossary / Glosario / Глоссарий / 词汇表" -> 4 words.
Plus table header row: Term(1) (EN)(2) Español(1) Русский(1) 中文(1) = 6 words.
Total extra: 10.
464 words. Still under 500.

I should also include the section headers like "ENGLISH", "ESPAÑOL",
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
