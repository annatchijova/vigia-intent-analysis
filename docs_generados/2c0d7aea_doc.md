<!--
VIGIA Academic Documentation
Module: 2c0d7aea
Batch ID: vigia-doc-0023-2c0d7aea
Generated: 2026-05-20T14:56:47.849557+00:00
-->

The user wants a brief academic description in 4 languages (English, Español, Русский, 中文) for a VIGIA support module called `scripts/run_vigia_full.py`. The content summary is: "Runner completo: razonamiento + bundle hash + verificación." Usage: `python3 run_vigia_full.py <caso.json>`.

Constraints:
- Academic technical writer specializing in digital forensics
- Audience: scientists who do not know Python
- Write in 4 languages: ENGLISH, ESPAÑOL, РУССКИЙ, 中文
- Include glossaries and scientific notes
- NEVER use floating-point math explanations for deterministic systems
- Keep it under 500 words total
- Include a 10-term glossary

Important: The total word count across all 4 languages + glossary must be under 500 words. That's very tight. I need to be extremely concise.

Structure:
- EN: ~80 words
- ES: ~80 words
- RU: ~80 words
- 中文: ~80 words (Chinese characters count as words? Usually yes in such contexts, but to be safe keep it compact)
- Glossary: 10 terms, ~60 words total

Wait, 500 words total for everything. Let's calculate:
- 4 sections × ~80 words = 320 words
- Glossary: 10 terms × ~5-6 words each = 50-60 words
- Scientific notes: maybe 20 words
Total ~400 words. Good.

Need to avoid Python jargon. Explain it as a forensic workflow tool. Don't mention floating point.

Key concepts to convey:
- It's a support module in the VIGIA framework
- Accepts a JSON case file
- Performs three deterministic stages: reasoning/inference, bundle hash computation, verification
- Outputs are reproducible and auditable
- Designed for forensic scientists

Let's draft EN:
"The `run_vigia_full.py` module constitutes the deterministic orchestration layer of the VIGIA forensic framework. Executed via a JSON case descriptor, it sequentially performs evidential reasoning, cryptographic bundle hashing, and integrity verification. The pipeline ensures fully reproducible, audit-ready results without probabilistic approximations. Scientists supply structured case parameters; the module returns tamper-evident bundles suitable for chain-of-custody documentation. All operations rely on discrete logic and exact arithmetic, eliminating non-deterministic variability inherent in floating-point computation."

Word count EN: ~58 words. Good.

ES:
"El módulo `run_vigia_full.py` es la capa de orquestación determinista del marco forense VIGIA. Ejecutado mediante un descriptor JSON de caso, realiza secuencialmente razonamiento probatorio, hash criptográfico del bundle y verificación de integridad. El flujo garantiza resultados reproducibles y auditables sin aproximaciones probabilísticas. Los científicos aportan parámetros estructurados; el módulo devuelve bundles con evidencia de manipulación para la cadena de custodia. Todas las operaciones emplean lógica discreta y aritmética exacta."

Word count ES: ~55 words.

RU:
"Модуль `run_vigia_full.py` представляет собой детерминированный оркестрационный слой цифровой криминалистической платформы VIGIA. Получая JSON-дескриптор случая, он последовательно выполняет доказательное рассуждение, криптографическое хеширование пакета и проверку целостности. Конвейер обеспечивает полностью воспроизводимые результаты, пригодные для аудита, без вероятностных приближений. Операции базируются на дискретной логике и точной арифметике."

Word count RU: ~48 words.

中文:
"`run_vigia_full.py` 模块是 VIGIA 取证框架的确定性编排层。通过 JSON 案件描述文件启动，依次执行证据推理、加密捆绑哈希与完整性校验。该流程确保结果完全可复现且适于审计，不含概率近似。科学家提供结构化参数，模块返回具备防篡改特性的证据包，以支持保管链记录。所有运算基于离散逻辑与精确算术。"

Word count ZH: ~78 characters/words. Good.

Now glossary (10 terms). Need to keep it short. Maybe 2-3 words per definition.
Terms:
1. Bundle hash / Hash del bundle / Хеш пакета / 捆绑哈希
2. Case descriptor / Descriptor de caso / Дескриптор случая / 案件描述符
3. Chain of custody / Cadena de custodia / Цепочка сохранности / 保管链
4. Deterministic system / Sistema determinista / Детерминированная система / 确定性系统
5. Digital forensics / Informática forense / Цифровая криминалистика / 数字取证
6. Evidential reasoning / Razonamiento probatorio / Доказательное рассуждение / 证据推理
7. Integrity verification / Verificación de integridad / Проверка целостности / 完整性校验
8. JSON / JSON / JSON / JSON
9. Orchestration layer / Capa de orquestación / Оркестрационный слой / 编排层
10. Tamper-evident / Con evidencia de manipulación / С индикацией вмешательства / 防篡改

But I need to present the glossary maybe once, with 4 languages for each term? Or separate glossaries? The user said "Include glossaries" (plural) but given the 500-word limit, a single consolidated glossary with multilingual terms is best. Or four mini-glossaries? The prompt says "You include glossaries and scientific notes." Since the word count is tight, I will do one glossary table/list where each term is shown in all 4 languages, or define each term in English only but list translations? No, the user wants the text in 4 languages. I think a glossary per language would be too long. Better: a multilingual glossary where each entry has the term in 4 languages and a brief definition in English (or maybe 4 definitions?). But that quadruples length.

Alternative: provide the glossary in English only but note the translations? That might violate the spirit. However, with 500 words total, it's impossible to have 4 full glossaries. The main descriptions are already in 4 languages. A single glossary in English with cross-referenced terms should be acceptable, or I can make a compact table.

Actually, the user said "You always write in 4 languages". So the glossary should probably be accessible in all 4. But I can do a combined format where each entry is one line with terms in all 4 languages and a one-sentence definition shared? No, definitions should be language-specific.

Maybe the best approach: after the four descriptions, add a "Multilingual Glossary" where each entry is:
- **EN** Term / **ES** Término / **RU** Термин / **中文** 术语
- Brief definition (maybe EN only to save words, but that breaks the rule). Or I can write the definition in a way that is very short.

Wait, if I write 10 terms, each with a 5-word definition in each language, that's 200 words just for definitions. Plus 40 words for terms. Total 240. With 320 for descriptions = 560. Over limit.

I need to be extremely economical. Maybe the "glossary" can be a list of 10 terms with their 4-language equivalents and a single shared symbolic/technical definition? Or I can integrate the glossary into the text? No.

Another idea: The user might accept a glossary where each term is presented in all four languages in one line, with a concise single-language definition (e.g., English) because the main text already explains everything in 4 languages. But the instruction says "You always write in 4 languages". However, a glossary is part of the text. This is challenging.

Let's reconsider the word count. "Keep it under 500 words total." If I make each description ~50 words:
- EN: 50
- ES: 50
- RU: 50
- ZH: 50
Total: 200 words.
Then glossary: 10 terms. If each term has ~10 words of definition across 4 languages... that's 400 words. No.

Maybe Chinese characters and Russian words count differently in the user's expectation? Usually word count is word count. But maybe the limit is lenient. Still, I should try to respect it.

Let's draft very short descriptions (~40 words each):

EN (40):
"The `run_vigia_full.py` module is the deterministic execution engine of the VIGIA digital-forensics framework. It ingests a JSON case descriptor and sequentially performs evidential reasoning, bundle hashing, and integrity verification. Outputs are reproducible, audit-ready bundles documenting chain-of-custody without probabilistic approximations."

ES (41):
"El módulo `run_vigia_full.py` es el motor de ejecución determinista del marco forense VIGIA. Ingiere un descriptor JSON de caso y ejecuta secuencialmente razonamiento probatorio, hash de bundle y verificación de integridad. Los resultados son reproducibles, auditables y documentan la cadena de custodia sin aproximaciones probabilísticas."

RU (41):
"Модуль `run_vigia_full.py` — детерминированный исполнительный модуль цифровой криминалистической платформы VIGIA. Получая JSON-дескриптор случая, он последовательно выполняет доказательное рассуждение, хеширование пакета и проверку целостности. Результаты воспроизводимы, пригодны для аудита и фиксируют цепочку сохранности."

ZH (41):
"`run_vigia_full.py` 模块是 VIGIA 取证框架的确定性执行引擎。其读取 JSON 案件描述符，依次执行证据推理、捆绑哈希与完整性校验。输出结果可复现、可审计，并记录保管链，不包含概率近似。"

Total descriptions: ~163 words.

Now glossary. I'll create a compact multilingual glossary. Each entry: Term (EN | ES | RU | ZH): Definition. But I'll write the definition in English only to save words? Or perhaps a very short definition in each language using a table format would be too heavy.

Wait, I can do this: For each term, provide a 1-line definition that is multilingual? No, that's not readable.

Alternative: Provide 4 separate glossaries, each with 5 terms? That covers 20 terms, but we only need 10 terms total. No, we need a 10-term glossary.

Maybe I can present it like:

**Glossary / Glosario / Глоссарий / 术语表**

1. **Bundle hash** · Hash de bundle · Хеш пакета · 捆绑哈希 — *EN* Cryptographic digest of an evidence bundle. *ES* Resumen criptográfico de un paquete probatorio. *RU* Криптографический дайджест пакета доказательств. *中文* 证据包的加密摘要。

That's ~20 words per term × 10 = 200 words. Total ~363 words. Under 500! Perfect.

Let's refine to ensure total under 500.

Descriptions total ~163 words.
Glossary 10 terms with 4 short definitions each. Let's aim for ~25 words per term total (including term names).
25 × 10 = 250.
163 + 250 = 413. Well under 500.

Let's draft the glossary carefully:

Terms:
1. **Bundle hash** / Hash de bundle / Хеш пакета / 捆绑哈希 — Cryptographic digest binding an evidence set. / Resumen criptográfico que vincula un conjunto probatorio. / Криптографический дайджест, связывающий набор доказательств. / 绑定证据集的加密摘要。
Words: ~20.

2. **Case descriptor** / Descriptor de caso / Дескриптор случая / 案件描述符 — Structured JSON input defining forensic parameters. / Entrada JSON estructurada que define parámetros forenses. / Структурированный JSON-вход, определяющий криминалистические параметры. / 定义取证参数的结构化 JSON 输入。
Words: ~24.

3. **Chain of custody** / Cadena de custodia / Цепочка сохранности / 保管链 — Audit trail tracking evidence handling. / Trazabilidad auditorable del manejo probatorio. / Аудиторский след отслеживания обращения с доказательствами. / 追踪证据处理的审计轨迹。
Words: ~20.

4. **Deterministic system** / Sistema determinista / Детерминированная система / 确定性系统 — Process where identical inputs always yield identical outputs. / Proceso donde entradas idénticas producen salidas idénticas. / Процесс, при котором идентичные входы всегда дают идентичные выходы. / 相同输入始终产生相同输出的流程。
Words: ~24.

5. **Digital forensics** / Informática forense / Цифровая криминалистика / 数字取证 — Scientific recovery and investigation of material in digital devices. / Recuperación e investigación científica de material en dispositivos digitales. / Научное восстановление и исследование материала с цифровых устройств. / 对数字设备中材料进行科学恢复与调查。
Words: ~24.

6. **Evidential reasoning** / Razonamiento probatorio / Доказательное рассуждение / 证据推理 — Logical inference applied to digital evidence. / Inferencia lógica aplicada a pruebas digitales. / Логический вывод, применяемый к цифровым доказательствам. / 应用于数字证据的逻辑推理。
Words: ~18.

7. **Integrity verification** / Verificación de integridad / Проверка целостности / 完整性校验 — Procedure confirming data remain unaltered. / Procedimiento que confirma que los datos no han sido alterados. / Процедура подтверждения неизменности данных. / 确认数据未被更改的程序。
Words: ~18.

8. **JSON** / JSON / JSON / JSON — Lightweight text format for structured case parameters. / Formato de texto ligero para parámetros estructurados de caso. / Лёгкий текстовый формат для структурированных параметров случая. / 用于结构化案件参数的轻量级文本格式。
Words: ~20.

9. **Orchestration layer** / Capa de orquestación / Оркестрационный слой / 编排层 — Software component coordinating sequential forensic tasks. / Componente software que coordina tareas forenses secuenciales. / Программный компонент, координирующий последовательные криминалистические задачи. / 协调顺序取证任务的软件组件。
Words: ~20.

10. **Tamper-evident** / Con evidencia de manipulación / С индикацией вмешательства / 防篡改 — Property revealing unauthorized modification. / Propiedad que revela modificación no autorizada. / Свойство, выявляющее несанкционированное изменение. / 揭示未经授权修改的特性。
Words: ~16.

Now let's count more precisely.

EN descriptions:
"The `run_vigia_full.py` module is the deterministic execution engine of the VIGIA digital-forensics framework. It ingests a JSON case descriptor and sequentially performs evidential reasoning, bundle hashing, and integrity verification. Outputs are reproducible, audit-ready bundles documenting chain-of-custody without probabilistic approximations."
Count: 42 words.

ES:
"El módulo `run_vigia_full.py` es el motor de ejecución determinista del marco forense VIGIA. Ingiere un descriptor JSON de caso y ejecuta secuencialmente razonamiento probatorio, hash de bundle y verificación de integridad. Los resultados son reproducibles, auditables y documentan la cadena de custodia sin aproximaciones probabilísticas."
Count: 41 words.

RU:
"Модуль `run_vigia_full.py` — детерминированный исполнительный модуль цифровой криминалистической платформы VIGIA. Получая JSON-дескриптор случая, он последовательно выполняет доказательное рассуждение, хеширование пакета и проверку целостности. Результаты воспроизводимы, пригодны для аудита и фиксируют цепочку сохранности."
Count: 33 words. Wait, "платформы VIGIA" = 2, "Получая"=1, etc. Let's count carefully:
Модуль(1) run_vigia_full.py(2) —(3) детерминированный(4) исполнительный(5) модуль(6) цифровой(7) криминалистической(8) платформы(9) VIGIA.(10) Получая(11) JSON-дескриптор(12) случая,(13) он(14) последовательно(15) выполняет(16) доказательное(17) рассуждение,(18) хеширование(19) пакета(20) и(21) проверку(22) целостности.(23) Результаты(24) воспроизводимы,(25) пригодны(26) для(27) аудита(28) и(29) фиксируют(30) цепочку(31) сохранности.(32)
32 words.

ZH:
"`run_vigia_full.py`(1) 模块(2) 是(3) VIGIA(4) 取证(5) 框架(6) 的(7) 确定性(8) 执行(9) 引擎。(10) 其(11) 读取(12) JSON(13) 案件(14) 描述符，(15) 依次(16) 执行(17) 证据(18) 推理、(19) 捆绑(20) 哈希(21) 与(22) 完整性(23) 校验。(24) 输出(25) 结果(26) 可复现、(27) 可审计，(28) 并(29) 记录(30) 保管链，(31) 不(32) 包含(33) 概率(34) 近似。(35)
35 words.

Total description words: 42+41+32+35 = 150.

Now glossary. I'll count each entry carefully.

1. **Bundle hash** / Hash de bundle / Хеш пакета / 捆绑哈希 — EN: Cryptographic(1) digest(2) binding(3) an(4) evidence(5) set.(6) ES: Resumen(1) criptográfico(2) que(3) vincula(4) un(5) conjunto(6) probatorio.(7) RU: Криптографический(1) дайджест,(2) связывающий(3) набор(4) доказательств.(5) ZH: 绑定(1) 证据(2) 集(3) 的(4) 加密(5) 摘要。(6)
Total for entry 1: 6+7+5+6 = 24 words.

2. **Case descriptor** / Descriptor de caso / Дескриптор случая / 案件描述符 — EN: Structured(1) JSON(2) input(3) defining(4) forensic(5) parameters.(6) ES: Entrada(1) JSON(2) estructurada(3) que(4) define(5) parámetros(6) forenses.(7) RU: Структурированный(1) JSON-вход,(2) определяющий(3) криминалистические(4) параметры.(5) ZH: 定义(1) 取证(2) 参数(3) 的(4) 结构化(5) JSON(6) 输入。(7)
Total: 6+7+5+7 = 25.

3. **Chain of custody** / Cadena de custodia / Цепочка сохранности / 保管链 — EN: Audit(1) trail(2) tracking(3) evidence(4) handling.(5) ES: Trazabilidad(1) auditorable(2) del(3) manejo(4) probatorio.(5) RU: Аудиторский(1) след(2) отслеживания(3) обращения(4) с(5) доказательствами.(6) ZH: 追踪(1) 证据(2) 处理(3) 的(4) 审计(5) 轨迹。(6)
Total: 5+5+6+6 = 22.

4. **Deterministic system** / Sistema determinista / Детерминированная система / 确定性系统 — EN: Process(1) where(2) identical(3) inputs(4) always(5) yield(6) identical(7) outputs.(8) ES: Proceso(1) donde(2) entradas(3) idénticas(4) producen(5) salidas(6) idénticas.(7) RU: Процесс,(1) при(2) котором(3) идентичные(4) входы(5) всегда(6) дают(7) идентичные(8) выходы.(9) ZH: 相同(1) 输入(2) 始终(3) 产生(4) 相同(5) 输出(6) 的(7) 流程。(8)
Total: 8+7+9+8 = 32.

5. **Digital forensics** / Informática forense / Цифровая криминалистика / 数字取证 — EN: Scientific(1) recovery(2) and(3) investigation(4) of(5) material(6) in(7) digital(8) devices.(9) ES: Recuperación(1) e(2) investigación(3) científica(4) de(5) material(6) en(7) dispositivos(8) digitales.(9) RU: Научное(1) восстановление(2) и(3) исследование(4) материала(5) с(6) цифровых(7) устройств.(8) ZH: 对(1) 数字(2) 设备(3) 中(4) 材料(5) 进行(6) 科学(7) 恢复(8) 与(9) 调查。(10)
Total: 9+9+8+10 = 36.

6. **Evidential reasoning** / Razonamiento probatorio / Доказательное рассуждение / 证据推理 — EN: Logical(1) inference(2) applied(3) to(4) digital(5) evidence.(6) ES: Inferencia(1) lógica(2) aplicada(3) a(4) pruebas(5) digitales.(6) RU: Логический(1) вывод,(2) применяемый(3) к(4) цифровым(5) доказательствам.(6) ZH: 应用于(1) 数字(2) 证据(3) 的(4) 逻辑(5) 推理。(6)
Total: 6+6+6+6 = 24.

7. **Integrity verification** / Verificación de integridad / Проверка целостности / 完整性校验 — EN: Procedure(1) confirming(2) data(3) remain(4) unaltered.(5) ES: Procedimiento(1) que(2) confirma(3) que(4) los(5) datos(6) no(7) han(8) sido(9) alterados.(10) RU: Процедура(1) подтверждения(2) неизменности(3) данных.(4) ZH: 确认(1) 数据(2) 未被(3) 更改(4) 的(5) 程序。(6)
Total: 5+10+4+6 = 25.

8. **JSON** / JSON / JSON / JSON — EN: Lightweight(1) text(2) format(3) for(4) structured(5) case(6) parameters.(7) ES: Formato(1) de(2) texto(3) ligero(4) para(5) parámetros(6) estructurados(7) de(8) caso.(9) RU: Лёгкий(1) текстовый(2) формат(3) для(4) структурированных(5) параметров(6) случая.(7) ZH: 用于(1) 结构化(2) 案件(3) 参数(4) 的(5) 轻量级(6) 文本(7) 格式。(8)
Total: 7+9+7+8 = 31.

9. **Orchestration layer** / Capa de orquestación / Оркестрационный слой / 编排层 — EN: Software(1) component(2) coordinating(3) sequential(4) forensic(5) tasks.(6) ES: Componente(1) software(2) que(3) coordina(4) tareas(5) forenses(6) secuenciales.(7) RU: Программный(1) компонент,(2) координирующий(3) последовательные(4) криминалистические(5) задачи.(6) ZH: 协调(1) 顺序(2) 取证(3) 任务(4) 的(5) 软件(6) 组件。(7)
Total: 6+7+6+7 = 26.

10. **Tamper-evident** / Con evidencia de manipulación / С индикацией вмешательства / 防篡改 — EN: Property(1) revealing(2) unauthorized(3) modification.(4) ES: Propiedad(1) que(2) revela(3) modificación(4) no(5) autorizada.(6) RU: Свойство,(1) выявляющее(2) несанкционированное(3) изменение.(4) ZH: 揭示(1) 未经(2) 授权(3) 修改(4) 的(5) 特性。(6)
Total: 4+6+4+6 = 20.

Now sum glossary words: 24+25+22+32+36+24+25+31+26+20 = 265.
Descriptions: 150.
Total: 415 words. Excellent, under 500.

I should also add a brief scientific note. Maybe integrate it into the descriptions? The user asked for scientific notes. I can add a one-line note in each language or a shared note. Given word count, I'll add a short "Scientific note" at the end in all 4 languages, very briefly. Or integrate into each description (already did: "without probabilistic approximations").

Actually, the descriptions already contain the scientific note about deterministic systems and no floating point. That should suffice.

Let's double-check the constraint: "You NEVER use floating-point math explanations for deterministic systems." I avoided floating-point math. I mentioned "without probabilistic approximations" and "deterministic". Good.

Let's verify no Python jargon is used that scientists wouldn't understand. I used "module", "execution engine", "JSON case descriptor", "bundle hashing". These are explained in the glossary. Good.

Formatting: Use headers for each language. Then a Glossary section. Keep it clean.

Let's finalize text.

One thing: In Spanish, "hash de bundle" or "hash del bundle"? The user wrote "bundle hash" in the summary. I'll use "hash de bundle". Or better "hash del paquete"? No, keep it close to the term. I'll use "hash de bundle" since it's in the glossary.

In Russian, "хеширование пакета" is fine.

In Chinese, "捆绑哈希" is a literal translation of bundle hash. Good.

Check the JSON term: In glossary, I didn't translate JSON. That's fine, it's a proper noun.

Now check word counts again with final text to be safe.

EN:
"The `run_vigia_full.py` module is the deterministic execution engine of the VIGIA digital-forensics framework. It ingests a JSON case descriptor and sequentially performs evidential reasoning, bundle hashing, and integrity verification. Outputs are reproducible, audit-ready bundles documenting chain-of-custody without probabilistic approximations."
1 The 2 run_vigia_full.py 3 module 4 is 5 the 6 deterministic 7 execution 8 engine 9 of 10 the 11 VIGIA 12 digital-forensics 13 framework. 14 It 15 ingests 16 a 17 JSON 18 case 19 descriptor 20 and 21 sequentially 22 performs 23 evidential 24 reasoning, 25 bundle 26 hashing, 27 and 28 integrity 29 verification. 30 Outputs 31 are 32 reproducible, 33 audit-ready 34 bundles 35 documenting 36 chain-of-custody 37 without 38 probabilistic 39 approximations.
39 words. Good.

ES:
"El módulo `run_vigia_full.py` es el motor de ejecución determinista del marco forense VIGIA. Ingiere un descriptor JSON de caso y ejecuta secuencialmente razonamiento probatorio, hash de bundle y verificación de integridad. Los resultados son reproducibles, auditables y documentan la cadena de custodia sin aproximaciones probabilísticas."
1 El 2 módulo 3 run_vigia_full.py 4 es 5 el 6 motor 7 de 8 ejecución 9 determinista 10 del 11 marco 12 forense 13 VIGIA. 14 Ingiere 15 un 16 descriptor 17 JSON 18 de 19 caso 20 y 21 ejecuta 22 secuencialmente 23 razonamiento 24 probatorio, 25 hash 26 de 27 bundle 28 y 29 verificación 30 de 31 integridad. 32 Los 33 resultados 34 son 35 reproducibles, 36 auditables 37 y 38 documentan 39 la 40 cadena 41 de 42 custodia 43 sin 44 aproximaciones 45 probabilísticas.
45 words.

RU:
"Модуль `run_vigia_full.py` — детерминированный исполнительный модуль цифровой криминалистической платформы VIGIA. Получая JSON-дескриптор случая, он последовательно выполняет доказательное рассуждение, хеширование пакета и проверку целостности. Результаты воспроизводимы, пригодны для аудита и фиксируют цепочку сохранности."
1 Модуль 2 run_vigia_full.py 3 — 4 детерминированный 5 исполнительный 6 модуль 7 цифровой 8 криминалистической 9 платформы 10 VIGIA. 11 Получая 12 JSON-дескриптор 13 случая, 14 он 15 последовательно 16 выполняет 17 доказательное 18 рассуждение, 19 хеширование 20 пакета 21 и 22 проверку 23 целостности. 24 Результаты 25 воспроизводимы, 26 пригодны 27 для 28 аудита 29 и 30 фиксируют 31 цепочку 32 сохранности.
32 words.

ZH:
"`run_vigia_full.py` 模块是 VIGIA 取证框架的确定性执行引擎。其读取 JSON 案件描述符，依次执行证据推理、捆绑哈希与完整性校验。输出结果可复现、可审计，并记录保管链，不包含概率近似。"
1 run_vigia_full.py 2 模块 3 是 4 VIGIA 5 取证 6 框架 7 的 8 确定性 9 执行 10 引擎。 11 其 12 读取 13 JSON 14 案件 15 描述符， 16 依次 17 执行 18 证据 19 推理、 20 捆绑 21 哈希 22 与 23 完整性 24 校验。 25 输出 26 结果 27 可复现、 28 可审计， 29 并 30 记录 31 保管链， 32 不 33 包含 34 概率 35 近似。
35 words.

Total desc: 39+45+32+35 = 151.

Glossary re-count with exact formatting. I'll format as bullet points. Each bullet will have terms and defs.

1. **Bundle hash** / Hash de bundle / Хеш пакета / 捆绑哈希 — EN: Cryptographic digest binding an evidence set. ES: Resumen criptográfico que vincula un conjunto probatorio. RU: Криптографический дайджест, связывающий набор доказательств. ZH: 绑定证据集的加密摘要。
Words: 6+7+5+6 = 24.

2. **Case descriptor** / Descriptor de caso / Дескриптор случая / 案件描述符 — EN: Structured JSON input defining forensic parameters. ES: Entrada JSON estructurada que define parámetros forenses. RU: Структурированный JSON-вход, определяющий криминалистические параметры. ZH: 定义取证参数的结构化 JSON 输入。
Words: 6+7+5+7 = 25.

3. **Chain of custody** / Cadena de custodia / Цепочка сохранности / 保管链 — EN: Audit trail tracking evidence handling. ES: Trazabilidad auditorable del manejo probatorio. RU: Аудиторский след отслеживания обращения с доказательствами. ZH: 追踪证据处理的审计轨迹。
Words: 5+5+6+6 = 22.

4. **Deterministic system** / Sistema determinista / Детерминированная система / 确定性系统 — EN: Process where identical inputs always yield identical outputs. ES: Proceso donde entradas idénticas producen salidas idénticas. RU: Процесс, при котором идентичные входы всегда дают идентичные выходы. ZH: 相同输入始终产生相同输出的流程。
Words: 8+7+9+8 = 32.

5. **Digital forensics** / Informática forense / Цифровая криминалистика / 数字取证 — EN: Scientific recovery and investigation of material in digital devices. ES: Recuperación e investigación científica de material en dispositivos digitales. RU: Научное восстановление и исследование материала с цифровых устройств. ZH: 对数字设备中材料进行科学恢复与调查。
Words: 9+9+8+10 = 36.

6. **Evidential reasoning** / Razonamiento probatorio / Доказательное рассуждение / 证据推理 — EN: Logical inference applied to digital evidence. ES: Inferencia lógica aplicada a pruebas digitales. RU: Логический вывод, применяемый к цифровым доказательствам. ZH: 应用于数字证据的逻辑推理。
Words: 6+6+6+6 = 24.

7. **Integrity verification** / Verificación de integridad / Проверка целостности / 完整性
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
