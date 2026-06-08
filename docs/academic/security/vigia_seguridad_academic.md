<!--
VIGIA Academic Documentation
Module: 61a43ef6
Batch ID: vigia-doc-0127-61a43ef6
Generated: 2026-05-20T14:56:47.871873+00:00
-->

中文:
`vigia/security/vigia_seguridad.py` 模块（内部代号“Cocinero”）是 VIGÍA 取证架构的确定性安全内核。它集中四项防御原语：(1) ASCII 净化，对不可信输入强制执行 7 位字符边界以消除不可打印控制序列；(2) 路径沙箱，将文件系统遍历限制在枚举的允许目录内；(3) 提示注入防护，通过词汇归一化在发送至语言模型接口前中和对抗性子串；(4) 子进程白名单，仅允许执行经密码学验证的二进制文件。科学注释：所有验证逻辑基于精确集合成员关系与离散语法规则，确保运行时无随机性的可复现行为。访问控制决策不涉及浮点估算。

Now check word counts roughly:
EN: ~95 words.
ES: ~105 words.
RU: ~95 words.
中文: ~95 words.
Total so far: ~390.
Glossary must fit in ~110 words.

Let's draft a compact 10-term glossary.

Terms:
1. ASCII Sanitization / Saneamiento ASCII / ASCII-санитизация / ASCII 净化
2. Path Sandboxing / Aislamiento de rutas / Изоляция путей / 路径沙箱
3. Prompt Injection / Inyección de prompt / Инъекция промптов / 提示注入
4. Subprocess Whitelist / Lista blanca de subprocesos / Белый список подпроцессов / 子进程白名单
5. Deterministic System / Sistema determinista / Детерминированная система / 确定性系统
6. Security Primitive / Primitiva de seguridad / Защитный примитив / 安全原语
7. Lexical Normalization / Normalización léxica / Лексическая нормализация / 词汇归一化
8. Allow-list Directory / Directorio de lista blanca / Каталог белого списка / 白名单目录
9. Cryptographic Verification / Verificación criptográfica / Криптографическая верификация / 密码学验证
10. Reproducible Behavior / Comportamiento reproducible / Воспроизводимое поведение / 可复现行为

Need to present definitions compactly. Maybe a table or a tight list. Since it's text, I can do:

**Glossary**
- **ASCII Sanitization** (ES: Saneamiento ASCII; RU: ASCII-санитизация; 中文: ASCII 净化): Strict removal or rejection of non-conforming characters outside a defined 7-bit printable set.
... etc.

But word count is tight. Let's calculate.

Better to group by term with 4 langs in one line each? That would be too long.

Alternative: A single block per term, very short.

Example:
1. **ASCII Sanitization / Saneamiento ASCII / ASCII-санитизация / ASCII 净化** — Rejection of non-7-bit characters from untrusted data.
2. **Path Sandboxing / Aislamiento de rutas / Изоляция путей / 路径沙箱** — Restriction of file operations to an enumerated directory set.
3. **Prompt Injection Shield / Blindaje contra inyección de prompts / Экранирование инъекций промптов / 提示注入防护** — Lexical neutralization of adversarial substrings prior to LLM dispatch.
4. **Subprocess Whitelist / Lista blanca de subprocesos / Белый список подпроцессов / 子进程白名单** — Execution permit limited to cryptographically verified binaries.
5. **Deterministic Kernel / Núcleo determinista / Детерминированное ядро / 确定性内核** — A logic subsystem whose output is entirely predictable from its inputs.
6. **Security Primitive / Primitiva de seguridad / Защитный примитив / 安全原语** — An atomic, indivisible security control mechanism.
7. **Lexical Normalization / Normalización léxica / Лексическая нормализация / 词汇归一化** — Transformation of symbolic input into a canonical discrete form.
8. **Exact-set Membership / Membresía exacta a conjuntos / Точное членство в множестве / 精确集合成员** — Evaluation based on discrete categorical presence, not probabilistic scoring.
9. **Non-printable Control Sequence / Secuencia de control no imprimible / Непечатаемая управляющая последовательность / 不可打印控制序列** — Byte patterns used for device signaling rather than data representation.
10. **Runtime Stochasticity / Estocasticidad en tiempo de ejecución / Стохастичность времени выполнения / 运行时随机性** — Non-deterministic variation arising from probabilistic algorithms or floating-point uncertainty.

Let's count words for these definitions:
1: 9 words
2: 9
3: 10
4: 9
5: 11
6: 8
7: 9
8: 11
9: 11
10: 11
Total def words: ~98
Plus term headers? The terms themselves are words too. Maybe ~150 words.

Combined with ~390 words above = 540. Too much.

Need to cut down the descriptions further. Target total under 500. Let's tighten each language to ~70 words.

EN revision:
The `vigia/security/vigia_seguridad.py` module, codenamed "Cocinero", is the deterministic security kernel of the VIGÍA forensic architecture. It unifies four defensive primitives: (1) ASCII sanitization, enforcing a strict 7-bit boundary on untrusted inputs; (2) path sandboxing, restricting filesystem traversal to an enumerated allow-list directory; (3) prompt injection shielding, neutralizing adversarial substrings via lexical normalization before LLM dispatch; and (4) subprocess whitelisting, permitting only cryptographically verified binaries. Scientific note: validation relies on exact-set membership and discrete grammar rules, ensuring reproducible, stochastic-free behavior without floating-point logic in access-control decisions.

Word count EN: 82 words.

ES revision:
El módulo `vigia/security/vigia_seguridad.py`, clave interna «Cocinero», es el núcleo de seguridad determinista de la arquitectura forense VIGÍA. Unifica cuatro primitivas defensivas: (1) saneamiento ASCII, imponiendo un límite estricto de 7 bits a entradas no confiables; (2) aislamiento de rutas, restringiendo la navegación a un directorio de lista blanca enumerado; (3) blindaje contra inyección de prompts, neutralizando subcadenas adversarias mediante normalización léxica antes del envío al LLM; y (4) lista blanca de subprocesos, permitiendo solo binarios verificados criptográficamente. Nota científica: la validación se basa en membresía exacta a conjuntos y reglas gramaticales discretas, asegurando comportamiento reproducible sin estocasticidad ni lógica de coma flotante en el control de acceso.

Word count ES: ~95.

RU revision:
Модуль `vigia/security/vigia_seguridad.py`, кодовое имя «Cocinero», — детерминированное ядро безопасности судебно-аналитической архитектуры VIGÍA. Он объединяет четыре защитных примитива: (1) ASCII-санитизацию со строгим 7-битным ограничением недоверенных входных данных; (2) изоляцию путей, ограничивающую обход файловой системы перечисленным каталогом белого списка; (3) экранирование инъекций промптов, нейтрализующее состязательные подстроки лексической нормализацией перед передачей в LLM; и (4) белый список подпроцессов, разрешающий исполнение только криптографически верифицированных бинарников. Научное примечание: проверка опирается на точное членство в множествах и дискретные грамматические правила, гарантируя воспроизводимое поведение без стохастичности и без операций с плавающей точкой при принятии решений по контролю доступа.

Word count RU: ~95.

中文 revision:
`vigia/security/vigia_seguridad.py` 模块（代号“Cocinero”）是 VIGÍA 取证架构的确定性安全内核。它统一四项防御原语：(1) ASCII 净化，对不可信输入强制执行 7 位边界；(2) 路径沙箱，将文件系统遍历限制在枚举的白名单目录；(3) 提示注入防护，通过词汇归一化在发送至 LLM 前中和对抗性子串；(4) 子进程白名单，仅允许执行经密码学验证的二进制文件。科学注释：验证依赖精确集合成员关系与离散语法规则，确保可复现且无随机性的行为，访问控制不涉及浮点逻辑。

Word count ZH: ~90.

Total for 4 langs: 82+95+95+90 = 362 words.
Remaining for glossary: ~138 words. That's tight but possible with very short definitions.

Let's compress glossary to ~12 words per definition average.

1. **ASCII Sanitization** — Enforced rejection of non-7-bit characters from untrusted streams. (11 words)
2. **Path Sandboxing** — Confinement of filesystem traversal to an enumerated allow-list. (10)
3. **Prompt Injection Shield** — Lexical neutralization of adversarial substrings prior to LLM ingestion. (10)
4. **Subprocess Whitelist** — Execution restricted to cryptographically verified binary images. (9)
5. **Deterministic Kernel** — Subsystem whose outputs are fully predictable from discrete inputs. (10)
6. **Security Primitive** — Atomic, indivisible mechanism enforcing a single security policy. (9)
7. **Lexical Normalization** — Canonical transformation of symbolic input into a discrete grammar. (10)
8. **Exact-set Membership** — Categorical presence test excluding probabilistic or scored evaluation. (9)
9. **Control Sequence** — Non-printable byte pattern for device signaling, not data representation. (10)
10. **Reproducible Behavior** — Identical output under identical input conditions across all runs. (10)

Total def words: ~98.
Plus the term words: maybe 20.
Total glossary ~120 words.

362 + 120 = 482. Under 500. Great.

But wait, the user asked for 4 languages in the glossary too? "Include a 10-term glossary." Since the whole document is 4 languages, it's implied the glossary should be multilingual. However, with word count under 500, it's almost impossible to define each term in 4 languages. I think providing the terms in 4 languages with a single definition (in English, or maybe a compact multilingual label) is acceptable given the constraint. Or I can provide the term in 4 languages and definition in English, as the terms themselves fulfill the multilingual requirement. Let me make sure the terms are clearly marked in 4 languages.

Example:
1. **ASCII Sanitization / Saneamiento ASCII / ASCII-санитизация / ASCII 净化** — Enforced rejection of non-7-bit characters.

The slash-separated terms count as words but that's fine.

Let's calculate with this format:

1. **ASCII Sanitization / Saneamiento ASCII / ASCII-санитизация / ASCII 净化** — Enforced rejection of non-7-bit characters. (12 words)
2. **Path Sandboxing / Aislamiento de rutas / Изоляция путей / 路径沙箱** — Confinement of filesystem traversal to an enumerated allow-list. (10)
3. **Prompt Injection Shield / Blindaje de inyección / Экранирование инъекций / 注入防护** — Lexical neutralization of adversarial substrings before LLM dispatch. (10)
Wait "Blindaje de inyección" is ambiguous. Better "Blindaje contra inyección de prompts" but that's long. Let's abbreviate: "Blindaje anti-inyección". But the prompt mentions "limpiar_para_llm". It's okay.

Actually, to save words, use short forms:
1. **ASCII Sanitization / Saneamiento ASCII / ASCII-санитизация / ASCII 净化** — Rejection of non-7-bit characters.
2. **Path Sandboxing / Aislamiento de rutas / Изоляция путей / 路径沙箱** — Filesystem traversal limited to an enumerated allow-list.
3. **Prompt Injection Shield / Blindaje anti-inyección / Экранирование инъекций / 注入防护盾** — Lexical neutralization of adversarial substrings pre-LLM.
4. **Subprocess Whitelist / Lista blanca de subprocesos / Белый список подпроцессов / 子进程白名单** — Execution restricted to cryptographically verified binaries.
5. **Deterministic Kernel / Núcleo determinista / Детерминированное ядро / 确定性内核** — Output fully predicted by discrete inputs without stochasticity.
6. **Security Primitive / Primitiva de seguridad / Защитный примитив / 安全原语** — Atomic mechanism enforcing one security policy.
7. **Lexical Normalization / Normalización léxica / Лексическая нормализация / 词汇归一化** — Canonical transformation into a discrete grammar form.
8. **Exact-set Membership / Pertenencia exacta / Точное членство / 精确集合成员** — Categorical presence test, not probabilistic scoring.
9. **Control Sequence / Secuencia de control / Управляющая последовательность / 控制序列** — Non-printable byte pattern for device signaling.
10. **Reproducible Behavior / Comportamiento reproducible / Воспроизводимое поведение / 可复现行为** — Identical output for identical input across runs.

Count:
1: term(9) + def(6) = 15
2: term(8) + def(8) = 16
3: term(7) + def(8) = 15
4: term(8) + def(8) = 16
5: term(7) + def(8) = 15
6: term(7) + def(7) = 14
7: term(7) + def(8) = 15
8: term(6) + def(8) = 14
9: term(7) + def(6) = 13
10: term(7) + def(8) = 15
Total glossary words: ~148.

Total overall: 362 + 148 = 510. Slightly over.

Need to cut 10+ words.

Trim descriptions:
1. Rejection of non-7-bit characters. (5) -> saves 1
2. Traversal limited to an enumerated allow-list. (7) -> saves 1
3. Neutralization of adversarial substrings pre-LLM. (6) -> saves 2
4. Execution restricted to verified binaries only. (6) -> saves 2
5. Output predicted by discrete inputs alone. (6) -> saves 2
6. Atomic mechanism for one security policy. (6) -> saves 1
7. Canonical transformation to discrete grammar. (5) -> saves 3
8. Categorical presence, not probabilistic score. (5) -> saves 3
9. Non-printable bytes for device signaling. (5) -> saves 1
10. Identical output for identical input always. (6) -> saves 2

Total saved ~17 words. New glossary ~131 words. Total ~493. Good.

Let's verify term counts again with exact word counts.

EN text:
"The `vigia/security/vigia_seguridad.py` module, codenamed "Cocinero", is the deterministic security kernel of the VIGÍA forensic architecture. It unifies four defensive primitives: (1) ASCII sanitization, enforcing a strict 7-bit boundary on untrusted inputs; (2) path sandboxing, restricting filesystem traversal to an enumerated allow-list directory; (3) prompt injection shielding, neutralizing adversarial substrings via lexical normalization before LLM dispatch; and (4) subprocess whitelisting, permitting only cryptographically verified binaries. Scientific note: validation relies on exact-set membership and discrete grammar rules, ensuring reproducible, stochastic-free behavior without floating-point logic in access-control decisions."

Let's count:
The(1) vigia/security/vigia_seguridad.py(1) module,(1) codenamed(1) "Cocinero",(1) is(1) the(1) deterministic(1) security(1) kernel(1) of(1) the(1) VIGÍA(1) forensic(1) architecture.(1) It(1) unifies(1) four(1) defensive(1) primitives:(1) (1)(1) ASCII(1) sanitization,(1) enforcing(1) a(1) strict(1) 7-bit(1) boundary(1) on(1) untrusted(1) inputs;(1) (2)(1) path(1) sandboxing,(1) restricting(1) filesystem(1) traversal(1) to(1) an(1) enumerated(1) allow-list(1) directory;(1) (3)(1) prompt(1) injection(1) shielding,(1) neutralizing(1) adversarial(1) substrings(1) via(1) lexical(1) normalization(1) before(1) LLM(1) dispatch;(1) and(1) (4)(1) subprocess(1) whitelisting,(1) permitting(1) only(1) cryptographically(1) verified(1) binaries.(1) Scientific(1) note:(1) validation(1) relies(1) on(1) exact-set(1) membership(1) and(1) discrete(1) grammar(1) rules,(1) ensuring(1) reproducible,(1) stochastic-free(1) behavior(1) without(1) floating-point(1) logic(1) in(1) access-control(1) decisions.(1)

That's exactly 82 words. Good.

ES text:
"El módulo `vigia/security/vigia_seguridad.py`, clave interna «Cocinero», es el núcleo de seguridad determinista de la arquitectura forense VIGÍA. Unifica cuatro primitivas defensivas: (1) saneamiento ASCII, imponiendo un límite estricto de 7 bits a entradas no confiables; (2) aislamiento de rutas, restringiendo la navegación a un directorio de lista blanca enumerado; (3) blindaje contra inyección de prompts, neutralizando subcadenas adversarias mediante normalización léxica antes del envío al LLM; y (4) lista blanca de subprocesos, permitiendo solo binarios verificados criptográficamente. Nota científica: la validación se basa en membresía exacta a conjuntos y reglas gramaticales discretas, asegurando comportamiento reproducible sin estocasticidad ni lógica de coma flotante en el control de acceso."

Count:
El(1) módulo(1) `vigia/security/vigia_seguridad.py`,(1) clave(1) interna(1) «Cocinero»,(1) es(1) el(1) núcleo(1) de(1) seguridad(1) determinista(1) de(1) la(1) arquitectura(1) forense(1) VIGÍA.(1) Unifica(1) cuatro(1) primitivas(1) defensivas:(1) (1)(1) saneamiento(1) ASCII,(1) imponiendo(1) un(1) límite(1) estricto(1) de(1) 7(1) bits(1) a(1) entradas(1) no(1) confiables;(1) (2)(1) aislamiento(1) de(1) rutas,(1) restringiendo(1) la(1) navegación(1) a(1) un(1) directorio(1) de(1) lista(1) blanca(1) enumerado;(1) (3)(1) blindaje(1) contra(1) inyección(1) de(1) prompts,(1) neutralizando(1) subcadenas(1) adversarias(1) mediante(1) normalización(1) léxica(1) antes(1) del(1) envío(1) al(1) LLM;(1) y(1) (4)(1) lista(1) blanca(1) de(1) subprocesos,(1) permitiendo(1) solo(1) binarios(1) verificados(1) criptográficamente.(1) Nota(1) científica:(1) la(1) validación(1) se(1) basa(1) en(1) membresía(1) exacta(1) a(1) conjuntos(1) y(1) reglas(1) gramaticales(1) discretas,(1) asegurando(1) comportamiento(1) reproducible(1) sin(1) estocasticidad(1) ni(1) lógica(1) de(1) coma(1) flotante(1) en(1) el(1) control(1) de(1) acceso.(1)

Count: Let's tally roughly. Looks like ~95 words. Okay.

RU text:
"Модуль `vigia/security/vigia_seguridad.py`, кодовое имя «Cocinero», — детерминированное ядро безопасности судебно-аналитической архитектуры VIGÍA. Он объединяет четыре защитных примитива: (1) ASCII-санитизацию со строгим 7-битным ограничением недоверенных входных данных; (2) изоляцию путей, ограничивающую обход файловой системы перечисленным каталогом белого списка; (3) экранирование инъекций промптов, нейтрализующее состязательные подстроки лексической нормализацией перед передачей в LLM; и (4) белый список подпроцессов, разрешающий исполнение только криптографически верифицированных бинарников. Научное примечание: проверка опирается на точное членство в множествах и дискретные грамматические правила, гарантируя воспроизводимое поведение без стохастичности и без операций с плавающей точкой при принятии решений по контролю доступа."

Count roughly: ~95 words. Okay.

ZH text:
"`vigia/security/vigia_seguridad.py` 模块（代号“Cocinero”）是 VIGÍA 取证架构的确定性安全内核。它统一四项防御原语：(1) ASCII 净化，对不可信输入强制执行 7 位边界；(2) 路径沙箱，将文件系统遍历限制在枚举的白名单目录；(3) 提示注入防护，通过词汇归一化在发送至 LLM 前中和对抗性子串；(4) 子进程白名单，仅允许执行经密码学验证的二进制文件。科学注释：验证依赖精确集合成员关系与离散语法规则，确保可复现且无随机性的行为，访问控制不涉及浮点逻辑。"

Count: ~90 words.

Now glossary with trimmed defs:

1. **ASCII Sanitization / Saneamiento ASCII / ASCII-санитизация / ASCII 净化** — Rejection of non-7-bit characters.
2. **Path Sandboxing / Aislamiento de rutas / Изоляция путей / 路径沙箱** — Traversal limited to an enumerated allow-list.
3. **Prompt Injection Shield / Blindaje anti-inyección / Экранирование инъекций / 注入防护盾** — Neutralization of adversarial substrings pre-LLM.
4. **Subprocess Whitelist / Lista blanca de subprocesos / Белый список подпроцессов / 子进程白名单** — Execution restricted to verified binaries only.
5. **Deterministic Kernel / Núcleo determinista / Детерминированное ядро / 确定性内核** — Output predicted by discrete inputs alone.
6. **Security Primitive / Primitiva de seguridad / Защитный примитив / 安全原语** — Atomic mechanism for one security policy.
7. **Lexical Normalization / Normalización léxica / Лексическая нормализация / 词汇归一化** — Canonical transformation to discrete grammar.
8. **Exact-set Membership / Pertenencia exacta / Точное членство / 精确集合成员** — Categorical presence, not probabilistic score.
9. **Control Sequence / Secuencia de control / Управляющая последовательность / 控制序列** — Non-printable bytes for device signaling.
10. **Reproducible Behavior / Comportamiento reproducible / Воспроизводимое поведение / 可复现行为** — Identical output for identical input always.

Let's count glossary words precisely.

1. ASCII(1) Sanitization(1) /(1) Saneamiento(1) ASCII(1) /(1) ASCII-санитизация(1) /(1) ASCII(1) 净化(1) —(1) Rejection(1) of(1) non-7-bit(1) characters.(1) = 14
2. Path(1) Sandboxing(1) /(1) Aislamiento(1) de(1) rutas(1) /(1) Изоляция(1) путей(1) /(1) 路径沙箱(1) —(1) Traversal(1) limited(1) to(1) an(1) enumerated(1) allow-list.(1) = 15
3. Prompt(1) Injection(1) Shield(1) /(1) Blindaje(1) anti-inyección(1) /(1) Экранирование(1) инъекций(1) /(1) 注入防护盾(1) —(1) Neutralization(1) of(1) adversarial(1) substrings(1) pre-LLM.(1) = 15
4. Subprocess(1) Whitelist(1) /(1) Lista(1) blanca(1) de(1) subprocesos(1) /(1) Белый(1) список(1) подпроцессов(1) /(1) 子进程白名单(1) —(1) Execution(1) restricted(1) to(1) verified(1) binaries(1) only.(1) = 16
5. Deterministic(1) Kernel(1) /(1) Núcleo(1) determinista(1) /(1) Детерминированное(1) ядро(1) /(1) 确定性内核(1) —(1) Output(1) predicted(1) by(1) discrete(1) inputs(1) alone.(1) = 14
6. Security(1) Primitive(1) /(1) Primitiva(1) de(1) seguridad(1) /(1) Защитный(1) примитив(1) /(1) 安全原语(1) —(1) Atomic(1) mechanism(1) for(1) one(1) security(1) policy.(1) = 14
7. Lexical(1) Normalization(1) /(1) Normalización(1) léxica(1) /(1) Лексическая(1) нормализация(1) /(1) 词汇归一化(1) —(1) Canonical(1) transformation(1) to(1) discrete(1) grammar.(1) = 13
8. Exact-set(1) Membership(1) /(1) Pertenencia(1) exacta(1) /(1) Точное(1) членство(1) /(1) 精确集合成员(1) —(1) Categorical(1) presence,(1) not(1) probabilistic(1) score.(1) = 13
9. Control(1) Sequence(1) /(1) Secuencia(1) de(1) control(1) /(1) Управляющая(1) последовательность(1) /(1) 控制序列(1) —(1) Non-printable(1) bytes(1) for(1) device(1) signaling.(1) = 13
10. Reproducible(1) Behavior(1) /(1) Comportamiento(1) reproducible(1) /(1) Воспроизводимое(1) поведение(1) /(1) 可复现行为(1) —(1) Identical(1) output(1) for(1) identical(1) input(1) always.(1) = 14

Total glossary words: 14+15+15+16+14+14+13+13+13+14 = 141.

Total overall: 82+95+95+90+141 = 503. Crap, 3 words over.

Need to trim 4+ words to be safe.

Cut from EN:
"The `vigia/security/vigia_seguridad.py` module, codenamed "Cocinero", is the deterministic security kernel of the VIGÍA forensic architecture. It unifies four defensive primitives: (1) ASCII sanitization, enforcing a strict 7-bit boundary on untrusted inputs; (2) path sandboxing, restricting filesystem traversal to an enumerated allow-list directory; (3) prompt injection shielding, neutralizing adversarial substrings via lexical normalization before LLM dispatch; and (4) subprocess whitelisting, permitting only cryptographically verified binaries. Scientific note: validation relies on exact-set membership and discrete grammar rules, ensuring reproducible, stochastic-free behavior without floating-point logic in access-control decisions."

Can cut "the" before VIGÍA? No. Cut "strict"? Cut "via lexical normalization" -> "by lexical normalization"? Same count. Cut "cryptographically" -> "verified binaries"? But that's important. Cut "only"? Not really.

Let's rewrite EN slightly shorter:
"The
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
