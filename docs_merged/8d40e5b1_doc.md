<!--
VIGIA Academic Documentation
Module: 8d40e5b1
Batch ID: vigia-doc-0182-8d40e5b1
Generated: 2026-05-20T14:56:47.883887+00:00
-->

中文:
`path_guard.py` 是 VIGIA 取证分析工具的辅助模块。它对文件系统路径进行净化，阻止访问指定的 `base_dir` 之外的区域。根据 Kimi 阶段 3.2，该模块拒绝符号链接、设备文件、命名管道以及解析后超出基础目录的路径。不变量：所有路径在比较前必须完全解析，且仅接受常规文件；特殊文件类型均被阻断。确保证据处理确定且无染。


Terms to include:
1. Path sanitization
2. Symbolic link (symlink)
3. Device file
4. Named pipe
5. Base directory (base_dir)
6. Path traversal
7. Regular file
8. Invariant
9. Artifact analyzer
10. Deterministic system

If I make a compact table-like glossary, maybe just term + 1-line definition. Let's count words.

Draft glossary:
1. **Path sanitization** – Validation and cleaning of file paths to enforce security policies.
2. **Symbolic link** – A file-system pointer to another path; rejected to prevent redirection attacks.
3. **Device file** – A special file representing a hardware device; blocked to avoid system interaction.
4. **Named pipe** – An inter-process communication channel; excluded to stop data injection.
5. **Base directory** – The authorized root folder bounding all valid analyzer operations.
6. **Path traversal** – An attack escaping a restricted directory via relative path manipulations.
7. **Regular file** – Ordinary data-carrying file; the only type permitted for evidence ingestion.
8. **Invariant** – A condition held true throughout execution, ensuring consistent behavior.
9. **Artifact analyzer** – A forensic component examining digital traces within controlled paths.
10. **Deterministic system** – A process producing identical, reproducible outcomes from the same inputs.

Let's count words roughly:

EN text: 56 words.
ES text: 58 words.
RU text: 59 words.
ZH text: 56 words.
Glossary: approx 80 words.
Total: ~309 words. Well under 500. Great.


Let's refine the texts slightly to make them more academic and polished.

EN:

ES:
`path_guard.py` es un módulo de soporte VIGIA para analizadores de artefactos forenses. Sanitiza rutas del sistema de archivos para evitar la salida del directorio `base_dir` designado. Según Kimi Fase 3.2, rechaza enlaces simbólicos, archivos de dispositivo, tuberías con nombre y rutas resueltas fuera del directorio base. Los invariantes exigen que toda ruta se resuelva antes de compararse y que solo se admitan archivos regulares, bloqueando tipos especiales. Garantiza un manejo determinista de evidencias sin contaminación.

RU:
`path_guard.py` — вспомогательный модуль VIGIA для судебных анализаторов артефактов. Он санитирует пути файловой системы, предотвращая выход за пределы назначенного `base_dir`. В соответствии с фазой 3.2 Kimi, отклоняются символические ссылки, файлы устройств, именованные каналы и разрешённые пути за пределами базового каталога. Инварианты требуют полного разрешения пути перед сравнением и допуска только обычных файлов; специальные типы блокируются. Обеспечивает детерминированную обработку доказательств без загрязнения.

ZH:
`path_guard.py` 是 VIGIA 取证工件分析器的支持模块。它对文件系统路径进行净化，防止目录遍历至指定的 `base_dir` 之外。依据 Kimi 阶段 3.2，模块拒绝符号链接、设备文件、命名管道以及解析后位于基础目录外的任何路径。核心不变量要求所有路径在比较前必须完全解析，且仅允许常规文件；所有特殊文件类型均被阻断。从而确保证据处理的确定性与无染性。


Alternative: make the glossary entries have the term in 4 languages, but very short. For example:

1. **Path sanitization** / Sanitización de rutas / Санитизация путей / 路径净化 — Process of validating and cleaning file paths to enforce security boundaries.

But that adds many words. Let's count: each entry would be ~15 words extra for translations. 10 entries = 150 extra words. That might push us near 500 but still maybe okay.

Let's calculate precisely.

EN paragraph: 56 words.
ES paragraph: 58 words.
RU paragraph: 59 words.
ZH paragraph: 56 words.
Subtotal: 229 words.

Remaining for glossary: ~270 words. That's plenty! Actually 500 is not that tight if I'm concise. Let's do a proper multilingual glossary. It will look professional.

Let's draft glossary entries with EN term first, then ES, RU, ZH in parentheses, then a concise definition in English (or maybe 4 short definitions?). To keep consistent with the persona, maybe the definition should also be in 4 languages? But that's 4x the words. The prompt says "You always write in 4 languages" for the documentation. A glossary is part of the documentation. However, a glossary is typically a list of terms with definitions. If I define each in 4 languages, it will exceed 500 words easily. Let's test:

Entry 1:
- EN: Path sanitization: validation of file paths to enforce security policies.
- ES: Sanitización de rutas: validación de rutas para imponer políticas de seguridad.
- RU: Санитизация путей: проверка путей для обеспечения политик безопасности.
- ZH: 路径净化：验证文件路径以执行安全策略。
That's ~30 words per entry. 10 entries = 300 words. Plus 230 = 530. Slightly over.

But I can compress further. Maybe present as a table or list where each entry is a single sentence with slashes. Or maybe just the term in 4 languages and the definition in English only. The prompt doesn't explicitly say "glossary in 4 languages", just "include a 10-term glossary". Since the main description is in 4 languages, the glossary could be a supplemental EN-only list to save space, but that breaks the persona. However, the persona says "You always write in 4 languages". So the glossary should ideally be in 4 languages too.

Alternative: Provide 4 separate mini-glossaries, one per language, but that repeats definitions and uses too many words.

Better approach: Use a compact format where each line contains the term in 4 languages separated by slashes, followed by a single definition in English (or maybe a multilingual definition). But English-only definition is okay for scientists; they read English. However, to respect the persona, perhaps I can give a definition that is universally understandable or include short translations.

Let's try this format:

**Glossary / Glosario / Глоссарий / 词汇表**

1. **Path sanitization** — *Sanitización de rutas / Санитизация путей / 路径净化*: Validation and cleaning of file paths to enforce security boundaries.
2. **Symbolic link** — *Enlace simbólico / Символическая ссылка / 符号链接*: A file-system pointer to another path; rejected to prevent redirection attacks.
...

This way each entry is about 20 words. 10 entries = 200 words. 229 + 200 = 429. Under 500. Perfect.

Let's write them carefully.

Terms:
1. Path sanitization
2. Symbolic link
3. Device file
4. Named pipe
5. Base directory
6. Path traversal
7. Regular file
8. Invariant
9. Artifact analyzer
10. Deterministic system

Let's draft each entry with word counts.

1. **Path sanitization** — *Sanitización de rutas / Санитизация путей / 路径净化*: Validation and cleaning of file paths to enforce security boundaries and prevent unauthorized access. (18 words)
2. **Symbolic link** — *Enlace simbólico / Символическая ссылка / 符号链接*: A file-system object that references another path; blocked to prevent redirection outside the base directory. (19 words)
3. **Device file** — *Archivo de dispositivo / Файл устройства / 设备文件*: A special file representing a hardware or virtual device; excluded to avoid direct system interaction. (18 words)
4. **Named pipe** — *Tubería con nombre / Именованный канал / 命名管道*: An inter-process communication endpoint; rejected to eliminate injection or data-stream contamination risks. (15 words)
5. **Base directory** — *Directorio base / Базовый каталог / 基础目录*: The authorized root folder that bounds all valid forensic analyzer operations and path resolutions. (16 words)
6. **Path traversal** — *Recorrido de rutas / Обход каталогов / 路径遍历*: An escape technique using relative path sequences to access files outside a restricted directory. (17 words)
7. **Regular file** — *Archivo regular / Обычный файл / 常规文件*: A standard file containing data; the only file type permitted for evidence ingestion by the analyzer. (17 words)
8. **Invariant** — *Invariante / Инвариант / 不变量*: A logical condition guaranteed to remain true throughout module execution, ensuring consistent behavior. (15 words)
9. **Artifact analyzer** — *Analizador de artefactos / Анализатор артефактов / 工件分析器*: A forensic component that examines digital traces under controlled, sanitized path constraints. (15 words)
10. **Deterministic system** — *Sistema determinista / Детерминированная система / 确定性系统*: A process that yields identical, reproducible outcomes from the same inputs without non-deterministic side effects. (16 words)

Total glossary words: ~166 words.
Text words: ~229.
Total: ~395 words. Under 500. Great.


- Sanitización de paths para analizadores de artefactos forenses. (covered)
- Kimi Fase 3.2: rechazar symlinks, device files, pipes, paths fuera de base_dir. (covered)
- Invariantes: Siempre resolver path antes de comparar; Verificar que es archivo regular (no device... (covered)

Everything covered.

Now formatting. I will present the four language blocks, then the glossary.


EN:
Count: is(1) a(2) VIGIA(3) support(4) module(5) for(6) forensic(7) artifact(8) analyzers.(9) It(10) sanitizes(11) file-system(12) paths(13) to(14) prevent(15) directory(16) traversal(17) outside(18) a(19) designated(20) `base_dir`.(21) Per(22) Kimi(23) Phase(24) 3.2,(25) it(26) rejects(27) symbolic(28) links,(29) device(30) files,(31) named(32) pipes,(33) and(34) any(35) resolved(36) path(37) lying(38) outside(39) the(40) base(41) directory.(42) Core(43) invariants(44) require(45) that(46) every(47) path(48) is(49) fully(50) resolved(51) prior(52) to(53) comparison(54) and(55) that(56) only(57) regular(58) files(59) are(60) admitted;(61) all(62) special(63) file(64) types(65) are(66) blocked.(67) This(68) ensures(69) deterministic,(70) contamination-free(71) evidence(72) handling.(73)
73 words.

ES:
`path_guard.py` es un módulo de soporte VIGIA para analizadores de artefactos forenses. Sanitiza rutas del sistema de archivos para evitar la salida del directorio `base_dir` designado. Según Kimi Fase 3.2, rechaza enlaces simbólicos, archivos de dispositivo, tuberías con nombre y rutas resueltas fuera del directorio base. Los invariantes exigen que toda ruta se resuelva antes de compararse y que solo se admitan archivos regulares, bloqueando tipos especiales. Garantiza un manejo determinista de evidencias sin contaminación.
Count: `path_guard.py`(1) es(2) un(3) módulo(4) de(5) soporte(6) VIGIA(7) para(8) analizadores(9) de(10) artefactos(11) forenses.(12) Sanitiza(13) rutas(14) del(15) sistema(16) de(17) archivos(18) para(19) evitar(20) la(21) salida(22) del(23) directorio(24) `base_dir`(25) designado.(26) Según(27) Kimi(28) Fase(29) 3.2,(30) rechaza(31) enlaces(32) simbólicos,(33) archivos(34) de(35) dispositivo,(36) tuberías(37) con(38) nombre(39) y(40) rutas(41) resueltas(42) fuera(43) del(44) directorio(45) base.(46) Los(47) invariantes(48) exigen(49) que(50) toda(51) ruta(52) se(53) resuelva(54) antes(55) de(56) compararse(57) y(58) que(59) solo(60) se(61) admitan(62) archivos(63) regulares,(64) bloqueando(65) tipos(66) especiales.(67) Garantiza(68) un(69) manejo(70) determinista(71) de(72) evidencias(73) sin(74) contaminación.(75)
75 words.

RU:
`path_guard.py` — вспомогательный модуль VIGIA для судебных анализаторов артефактов. Он санитирует пути файловой системы, предотвращая выход за пределы назначенного `base_dir`. В соответствии с фазой 3.2 Kimi, отклоняются символические ссылки, файлы устройств, именованные каналы и разрешённые пути за пределами базового каталога. Инварианты требуют полного разрешения пути перед сравнением и допуска только обычных файлов; специальные типы блокируются. Обеспечивает детерминированную обработку доказательств без загрязнения.
Count: `path_guard.py`(1) —(2) вспомогательный(3) модуль(4) VIGIA(5) для(6) судебных(7) анализаторов(8) артефактов.(9) Он(10) санитирует(11) пути(12) файловой(13) системы,(14) предотвращая(15) выход(16) за(17) пределы(18) назначенного(19) `base_dir`.(20) В(21) соответствии(22) с(23) фазой(24) 3.2(25) Kimi,(26) отклоняются(27) символические(28) ссылки,(29) файлы(30) устройств,(31) именованные(32) каналы(33) и(34) разрешённые(35) пути(36) за(37) пределами(38) базового(39) каталога.(40) Инварианты(41) требуют(42) полного(43) разрешения(44) пути(45) перед(46) сравнением(47) и(48) допуска(49) только(50) обычных(51) файлов;(52) специальные(53) типы(54) блокируются.(55) Обеспечивает(56) детерминированную(57) обработку(58) доказательств(59) без(60) загрязнения.(61)
61 words.

ZH:
`path_guard.py` 是 VIGIA 取证工件分析器的支持模块。它对文件系统路径进行净化，防止目录遍历至指定的 `base_dir` 之外。依据 Kimi 阶段 3.2，模块拒绝符号链接、设备文件、命名管道以及解析后位于基础目录外的任何路径。核心不变量要求所有路径在比较前必须完全解析，且仅允许常规文件；所有特殊文件类型均被阻断。从而确保证据处理的确定性与无染性。
Count: `path_guard.py`(1) 是(2) VIGIA(3) 取证(4) 工件(5) 分析器(6) 的(7) 支持(8) 模块。(9) 它(10) 对(11) 文件(12) 系统(13) 路径(14) 进行(15) 净化，(16) 防止(17) 目录(18) 遍历(19) 至(20) 指定(21) 的(22) `base_dir`(23) 之外。(24) 依据(25) Kimi(26) 阶段(27) 3.2，(28) 模块(29) 拒绝(30) 符号(31) 链接、(32) 设备(33) 文件、(34) 命名(35) 管道(36) 以及(37) 解析(38) 后(39) 位于(40) 基础(41) 目录(42) 外(43) 的(44) 任何(45) 路径。(46) 核心(47) 不变量(48) 要求(49) 所有(50) 路径(51) 在(52) 比较(53) 前(54) 必须(55) 完全(56) 解析，(57) 且(58) 仅(59) 允许(60) 常规(61) 文件；(62) 所有(63) 特殊(64) 文件(65) 类型(66) 均(67) 被(68) 阻断。(69) 从而(70) 确保(71) 证据(72) 处理(73) 的(74) 确定性(75) 与(76) 无染性。(77)
77 words.

Subtotal: 73+75+61+77 = 286 words.

Now glossary with the format above.

Let's recount glossary entries with that exact phrasing.

1. **Path sanitization** — *Sanitización de rutas / Санитизация путей / 路径净化*: Validation and cleaning of file paths to enforce security boundaries and prevent unauthorized access.
Words: Path(1) sanitization(2) —(3) Sanitización(4) de(5) rutas(6) /(7) Санитизация(8) путей(9) /(10) 路径净化(11): Validation(12) and(13) cleaning(14) of(15) file(16) paths(17) to(18) enforce(19) security(20) boundaries(21) and(22) prevent(23) unauthorized(24) access.(25) => 25 words.

2. **Symbolic link** — *Enlace simbólico / Символическая ссылка / 符号链接*: A file-system object that references another path; blocked to prevent redirection outside the base directory.
Words: Symbolic(1) link(2) —(3) Enlace(4) simbólico(5) /(6) Символическая(7) ссылка(8) /(9) 符号链接(10): A(11) file-system(12) object(13) that(14) references(15) another(16) path;(17) blocked(18) to(19) prevent(20) redirection(21) outside(22) the(23) base(24) directory.(25) => 25 words.

3. **Device file** — *Archivo de dispositivo / Файл устройства / 设备文件*: A special file representing a hardware or virtual device; excluded to avoid direct system interaction.
Words: Device(1) file(2) —(3) Archivo(4) de(5) dispositivo(6) /(7) Файл(8) устройства(9) /(10) 设备文件(11): A(12) special(13) file(14) representing(15) a(16) hardware(17) or(18) virtual(19) device;(20) excluded(21) to(22) avoid(23) direct(24) system(25) interaction.(26) => 26 words.

4. **Named pipe** — *Tubería con nombre / Именованный канал / 命名管道*: An inter-process communication endpoint; rejected to eliminate injection or data-stream contamination risks.
Words: Named(1) pipe(2) —(3) Tubería(4) con(5) nombre(6) /(7) Именованный(8) канал(9) /(10) 命名管道(11): An(12) inter-process(13) communication(14) endpoint;(15) rejected(16) to(17) eliminate(18) injection(19) or(20) data-stream(21) contamination(22) risks.(23) => 23 words.

5. **Base directory** — *Directorio base / Базовый каталог / 基础目录*: The authorized root folder that bounds all valid forensic analyzer operations and path resolutions.
Words: Base(1) directory(2) —(3) Directorio(4) base(5) /(6) Базовый(7) каталог(8) /(9) 基础目录(10): The(11) authorized(12) root(13) folder(14) that(15) bounds(16) all(17) valid(18) forensic(19) analyzer(20) operations(21) and(22) path(23) resolutions.(24) => 24 words.

6. **Path traversal** — *Recorrido de rutas / Обход каталогов / 路径遍历*: An escape technique using relative path sequences to access files outside a restricted directory.
Words: Path(1) traversal(2) —(3) Recorrido(4) de(5) rutas(6) /(7) Обход(8) каталогов(9) /(10) 路径遍历(11): An(12) escape(13) technique(14) using(15) relative(16) path(17) sequences(18) to(19) access(20) files(21) outside(22) a(23) restricted(24) directory.(25) => 25 words.

7. **Regular file** — *Archivo regular / Обычный файл / 常规文件*: A standard file containing data; the only file type permitted for evidence ingestion by the analyzer.
Words: Regular(1) file(2) —(3) Archivo(4) regular(5) /(6) Обычный(7) файл(8) /(9) 常规文件(10): A(11) standard(12) file(13) containing(14) data;(15) the(16) only(17) file(18) type(19) permitted(20) for(21) evidence(22) ingestion(23) by(24) the(25) analyzer.(26) => 26 words.

8. **Invariant** — *Invariante / Инвариант / 不变量*: A logical condition guaranteed to remain true throughout module execution, ensuring consistent behavior.
Words: Invariant(1) —(2) Invariante(3) /(4) Инвариант(5) /(6) 不变量(7): A(8) logical(9) condition(10) guaranteed(11) to(12) remain(13) true(14) throughout(15) module(16) execution,(17) ensuring(18) consistent(19) behavior.(20) => 20 words.

9. **Artifact analyzer** — *Analizador de artefactos / Анализатор артефактов / 工件分析器*: A forensic component that examines digital traces under controlled, sanitized path constraints.
Words: Artifact(1) analyzer(2) —(3) Analizador(4) de(5) artefactos(6) /(7) Анализатор(8) артефактов(9) /(10) 工件分析器(11): A(12) forensic(13) component(14) that(15) examines(16) digital(17) traces(18) under(19) controlled,(20) sanitized(21) path(22) constraints.(23) => 23 words.

10. **Deterministic system** — *Sistema determinista / Детерминированная система / 确定性系统*: A process that yields identical, reproducible outcomes from the same inputs without non-deterministic side effects.
Words: Deterministic(1) system(2) —(3) Sistema(4) determinista(5) /(6) Детерминированная(7) система(8) /(9) 确定性系统(10): A(11) process(12) that(13) yields(14) identical,(15) reproducible(16) outcomes(17) from(18) the(19) same(20) inputs(21) without(22) non-deterministic(23) side(24) effects.(25) => 25 words.

Glossary total: 25+25+26+23+24+25+26+20+23+25 = 242 words.
Grand total: 286 + 242 = 528 words. Oops, slightly over 500.


Let's tighten the main texts.

EN (target ~60 -> 50):
Count: `path_guard.py`(1) is(2) a(3) VIGIA(4) support(5) module(6) for(7) forensic(8) artifact(9) analyzers.(10) It(11) sanitizes(12) file-system(13) paths(14) to(15) prevent(16) traversal(17) outside(18) a(19) designated(20) `base_dir`.(21) Per(22) Kimi(23) Phase(24) 3.2,(25) it(26) rejects(27) symbolic(28) links,(29) device(30) files,(31) named(32) pipes,(33) and(34) any(35) resolved(36) path(37) outside(38) the(39) base(40) directory.(41) Core(42) invariants:(43) every(44) path(45) is(46) fully(47) resolved(48) before(49) comparison,(50) and(51) only(52) regular(53) files(54) are(55) admitted;(56) special(57) file(58) types(59) are(60) blocked.(61) This(62) ensures(63) deterministic,(64) contamination-free(65) evidence(66) handling.(67)
67 words. Slightly less than before? Actually before was 73. Good.

ES (trim):
`path_guard.py` es un módulo de soporte VIGIA para analizadores forenses. Sanitiza rutas para evitar salidas del `base_dir` designado. Según Kimi Fase 3.2, rechaza enlaces simbólicos, archivos de dispositivo, tuberías con nombre y rutas resueltas fuera del directorio base. Invariantes: toda ruta se resuelve antes de compararse y solo se admiten archivos regulares; los tipos especiales se bloquean. Garantiza manejo determinista de evidencias sin contaminación.
Count: `path_guard.py`(1) es(2) un(3) módulo(4) de(5) soporte(6) VIGIA(7) para(8) analizadores(9) forenses.(10) Sanitiza(11) rutas(12) para(13) evitar(14) salidas(15) del(16) `base_dir`(17) designado.(18) Según(19) Kimi(20) Fase(21) 3.2,(22) rechaza(23) enlaces(24) simbólicos,(25) archivos(26) de(27) dispositivo,(28) tuberías(29) con(30) nombre(31) y(32) rutas(33) resueltas(34) fuera(35) del(36) directorio(37) base.(38) Invariantes:(39) toda(40) ruta(41) se(42) resuelve(43) antes(44) de(45) compararse(46) y(47) solo(48) se(49) admiten(50) archivos(51) regulares;(52) los(53) tipos(54) especiales(55) se(56) bloquean.(57) Garantiza(58) manejo(59) determinista(60) de(61) evidencias(62)
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
