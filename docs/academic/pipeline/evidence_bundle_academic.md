<!--
VIGIA Academic Documentation
Module: 3e34d629
Batch ID: vigia-doc-0110-3e34d629
Generated: 2026-05-20T14:56:47.868311+00:00
-->

---
doc_hash: 3e34d629
module: vigia/pipeline/evidence_bundle.py
languages: [ZH]
generated_by: moonshot-kimi-k2.6-batch-api
license: Apache-2.0
---

中文:
`vigia/pipeline/evidence_bundle.py` 是 VIGIA 数字取证框架中的管道支撑模块。它将数字物证、密码学哈希值与元数据聚合为统一的证据包。该模块通过生成确定性的只读容器，确保证据链的完整性。它在处理图中作为无状态转换运行，输出经校验的包对象，且不修改原始数据。模块专为可重现的自动化取证工作流设计。

Word count ZH: ~50 words.

Now glossary. 10 terms. Must be brief. Maybe bilingual? The prompt says "include a 10-term glossary". Since the text is in 4 languages, the glossary could be presented in English with maybe translations, or separate? To save words, maybe present terms in English with concise definitions, or provide 4-language glossary which might be too long. Usually, a glossary in a multilingual doc can be in the primary language or repeated. Given the tight word count, I should probably provide a single glossary table or list in English, or perhaps each term with 4-language definitions? That would explode word count.

Alternative: Provide the glossary terms in English only, as is common in multilingual technical summaries where English is the reference. Or provide terms and definitions in the 4 languages but extremely condensed. But 10 terms x ~10 words = 100 words. If I do 4 languages for glossary, it's 400 words, impossible.

I think the best approach is to provide a glossary section where each term is given in English, Spanish, Russian, and Chinese in a very compact format, perhaps:
- **Evidence bundle / Paquete de evidencias / Пакет доказательств / 证据包**: Aggregated forensic container. / Contenedor forense agregado. / Сводный криминалистический контейнер. / 聚合的取证容器。

But that's 4 definitions per term. 10 terms = 40 definitions. If each definition is ~5 words, that's 200 words. Plus the terms themselves. This might push over 500.

Let's calculate total so far:
EN: 55
ES: 55
RU: 50
ZH: 50
Subtotal: 210 words.

Remaining for glossary and scientific notes: ~280 words.

If I do a compact 4-language glossary with very short definitions:
Format:
1. **Evidence bundle** — EN: Forensic artifact container. ES: Contenedor de artefactos forenses. RU: Контейнер цифровых артефактов. ZH: 取证物证容器。
Each entry: ~15 words. 10 entries = 150 words. Plus intro line.

Scientific notes: A single cross-language note or a brief note in all 4? "Scientific note" could be one block. Example: "Scientific note: The module employs deterministic serialization to guarantee bitwise reproducibility across pipeline runs." Then translate? That adds words.

Maybe the "scientific notes" can be a single short line appended after each description or as one shared note. To minimize words, I can add a short scientific note within each description or as a separate block. Let's integrate a brief scientific note into the text or add one note in English and rely on the multilingual descriptions? The prompt says "include glossaries and scientific notes". It doesn't explicitly say scientific notes must be in 4 languages, but since everything is in 4 languages, probably yes. However, word limit is strict.

Alternative: Make descriptions slightly shorter to free up words.

Revised EN (45 words):
`vigia/pipeline/evidence_bundle.py` is a VIGIA forensic pipeline support module. It aggregates digital artifacts, cryptographic hashes, and metadata into a unified, deterministic evidence bundle. As a stateless graph transform, it emits a read-only, validated container without altering source data, ensuring chain-of-custody integrity for reproducible workflows.

ES (45):
`vigia/pipeline/evidence_bundle.py` es un módulo de soporte de la canalización forense VIGIA. Agrupa artefactos digitales, hashes criptográficos y metadatos en un paquete de evidencias determinista. Como transformación sin estado, emite un contenedor de solo lectura validado sin modificar los datos originales, garantizando la integridad de la cadena de custodia en flujos reproducibles.

RU (45):
`vigia/pipeline/evidence_bundle.py` — вспомогательный модуль конвейера цифровой криминалистики VIGIA. Объединяет цифровые артефакты, криптографические хеши и метаданные в детерминированный пакет доказательств. Как безсостоятельное преобразование графа, генерирует контейнер только для чтения без изменения исходных данных, обеспечивая сохранность цепочки хранения.

ZH (45):
`vigia/pipeline/evidence_bundle.py` 是 VIGIA 取证管道的支撑模块。它将数字物证、密码学哈希与元数据聚合为确定性证据包。作为无状态图转换，它输出只读经验证的容器，不改动源数据，从而保障可重现工作流中的证据链完整性。

Subtotal: 180 words.

Now glossary. Let's aim for ~150 words.
Format: a list where each line contains the term in 4 languages separated by slashes, then a brief definition in English (or 4 brief phrases). But the prompt requires writing in 4 languages. The glossary should probably be accessible to all four audiences.

Maybe:
**Glossary / Glosario / Глоссарий / 术语表**

1. **Evidence bundle / Paquete de evidencias / Пакет доказательств / 证据包** — Deterministic forensic container. / Contenedor forense determinista. / Детерминированный криминалистический контейнер. / 确定性取证容器。

If each entry is ~12 words, 10 entries = 120 words. Plus header ~5 words. Total ~305. That's good.

Let's craft 10 terms relevant:
1. Evidence bundle (the concept)
2. Chain of custody / Cadena de custodia / Цепочка хранения / 保管链
3. Cryptographic hash / Hash criptográfico / Криптографический хеш / 密码学哈希
4. Metadata / Metadatos / Метаданные / 元数据
5. Stateless transform / Transformación sin estado / Бессостоятельное преобразование / 无状态转换
6. Artifact (digital) / Artefacto digital / Цифровой артефакт / 数字物证
7. Deterministic container / Contenedor determinista / Детерминированный контейнер / 确定性容器
8. Pipeline (processing graph) / Canalización / Конвейер обработки / 处理管道
9. Downstream analysis / Análisis descendente / Последующий анализ / 下游分析
10. Bitwise reproducibility / Reproducibilidad bit a bit / Побитовая воспроизводимость / 按位可重现性

Now count words per entry carefully.

Entry 1: Evidence bundle / Paquete de evidencias / Пакет доказательств / 证据包 — A unified forensic container. / Contenedor forense unificado. / Единый криминалистический контейнер. / 统一的取证容器。 (Words: 14)
Entry 2: Chain of custody / Cadena de custodia / Цепочка хранения / 保管链 — Documented evidence integrity. / Integridad documentada de evidencias. / Документированная сохранность доказательств. / 证据完整性的记录追踪。 (Words: 13)
Entry 3: Cryptographic hash / Hash criptográfico / Криптографический хеш / 密码学哈希 — Fixed-length data fingerprint. / Huella digital de longitud fija. / Короткий идентификатор данных. / 定长数据指纹。 (Words: 12)
Entry 4: Metadata / Metadatos / Метаданные / 元数据 — Contextual data descriptors. / Descriptores contextuales de datos. / Контекстные описатели данных. / 数据的上下文描述符。 (Words: 11)
Entry 5: Stateless transform / Transformación sin estado / Бессостоятельное преобразование / 无状态转换 — Input-dependent, memoryless operation. / Operación sin memoria dependiente de entrada. / Операция без памяти, зависящая от входа. / 仅依赖输入的无记忆操作。 (Words: 13)
Entry 6: Digital artifact / Artefacto digital / Цифровой артефакт / 数字物证 — Extracted source data element. / Elemento de datos fuente extraído. / Извлечённый элемент исходных данных. / 提取的源数据单元。 (Words: 12)
Entry 7: Deterministic container / Contenedor determinista / Детерминированный контейнер / 确定性容器 — Predictable, repeatable output structure. / Estructura de salida repetible y predecible. / Предсказуемая повторяемая структура выходных данных. / 可预测且可重复的输出结构。 (Words: 14)
Entry 8: Processing pipeline / Canalización de procesamiento / Конвейер обработки / 处理管道 — Ordered forensic workflow graph. / Grafo de flujo de trabajo ordenado. / Упорядоченный граф криминалистического процесса. / 有序的取证工作流图。 (Words: 12)
Entry 9: Downstream analysis / Análisis descendente / Последующий анализ / 下游分析 — Subsequent evidentiary examination. / Examinación probatoria posterior. / Последующее исследование доказательств. / 后续的证据审查。 (Words: 11)
Entry 10: Bitwise reproducibility / Reproducibilidad bit a bit / Побитовая воспроизводимость / 按位可重现性 — Identical binary output across runs. / Salida binaria idéntica entre ejecuciones. / Идентичный двоичный результат при повторных запусках. / 多次运行产生完全相同的二进制输出。 (Words: 14)

Total glossary words:
Header: Glossary / Glosario / Глоссарий / 术语表 (4)
Entries: 14+13+12+11+13+12+14+12+11+14 = 126
Total glossary ~130 words.

Now scientific notes. The prompt says "include glossaries and scientific notes". I can add a very brief scientific note at the end, maybe as a single sentence in 4 languages or one note with 4 translations. To save words, I can prepend a "Scientific note:" line to the glossary or add a small note block.

Maybe:
**Scientific note / Nota científica / Научное примечание / 科学备注**
Deterministic serialization excludes non-reproducible timestamps from the bundle manifest to ensure bitwise reproducibility across pipeline executions. / La serialización determinista excluye marcas temporales no reproducibles del manifiesto para garantizar la reproducibilidad bit a bit. / Детерминированная сериализация исключает невоспроизводимые временные метки из манифеста, обеспечивая побитовую воспроизводимость. / 确定性序列化从清单中排除不可复现的时间戳，以保障按位可重现性。

Word count for note: ~28 words (English) + ~30 (ES) + ~30 (RU) + ~25 (ZH) = ~113 words. That's too much.

Maybe integrate the scientific note into the description paragraphs. For example, add a sentence to each description:
EN: ... Scientific note: deterministic serialization excludes volatile timestamps to guarantee bitwise reproducibility.
ES: ... Nota científica: la serialización determinista excluye marcas temporales volátiles para garantizar reproducibilidad bit a bit.
RU: ... Научное примечание: детерминированная сериализация исключает изменчивые временные метки, обеспечивая побитовую воспроизводимость.
ZH: ... 科学备注：确定性序列化排除易变时间戳，以保障按位可重现性。

Each sentence is ~10-12 words. Adds ~44 words total.

Let's recalculate totals with integrated notes:

EN revised:
`vigia/pipeline/evidence_bundle.py` is a VIGIA forensic pipeline support module. It aggregates digital artifacts, cryptographic hashes, and metadata into a unified, deterministic evidence bundle. As a stateless graph transform, it emits a read-only, validated container without altering source data, ensuring chain-of-custody integrity. Scientific note: deterministic serialization excludes volatile timestamps to guarantee bitwise reproducibility.

Words EN: 51.

ES revised:
`vigia/pipeline/evidence_bundle.py` es un módulo de soporte de la canalización forense VIGIA. Agrupa artefactos digitales, hashes criptográficos y metadatos en un paquete de evidencias determinista. Como transformación sin estado, emite un contenedor de solo lectura validado sin modificar los datos originales, garantizando la integridad de la cadena de custodia. Nota científica: la serialización determinista excluye marcas temporales volátiles para garantizar la reproducibilidad bit a bit.

Words ES: 56.

RU revised:
`vigia/pipeline/evidence_bundle.py` — вспомогательный модуль конвейера цифровой криминалистики VIGIA. Объединяет цифровые артефакты, криптографические хеши и метаданные в детерминированный пакет доказательств. Как безсостоятельное преобразование графа, генерирует контейнер только для чтения без изменения исходных данных, обеспечивая сохранность цепочки хранения. Научное примечание: детерминированная сериализация исключает изменчивые временные метки, гарантируя побитовую воспроизводимость.

Words RU: 54.

ZH revised:
`vigia/pipeline/evidence_bundle.py` 是 VIGIA 取证管道的支撑模块。它将数字物证、密码学哈希与元数据聚合为确定性证据包。作为无状态图转换，它输出只读经验证的容器，不改动源数据，从而保障证据链完整性。科学备注：确定性序列化排除易变时间戳，以保障按位可重现性。

Words ZH: 49.

Total descriptions: 51+56+54+49 = 210 words.

Glossary: ~130 words.
Grand total: ~340 words. Well under 500.

Wait, does "бессостоятельное преобразование" make sense in Russian? The standard term for stateless is "безсостоятельное" or "не сохраняющее состояние". "Безсостоятельное" is a bit unusual; better "не имеющее состояния" or "безсостоянительное". Actually in IT Russian, "stateless" is often "не сохраняющий состояние" or "безсостояние". "Безсостоятельное" means insolvent/bankrupt. I must avoid that. Correction: "преобразование без сохранения состояния". Let's adjust.

RU revised:
`vigia/pipeline/evidence_bundle.py` — вспомогательный модуль конвейера цифровой криминалистики VIGIA. Объединяет цифровые артефакты, криптографические хеши и метаданные в детерминированный пакет доказательств. Как преобразование без сохранения состояния, генерирует контейнер только для чтения без изменения исходных данных, обеспечивая сохранность цепочки хранения. Научное примечание: детерминированная сериализация исключает изменчивые временные метки, гарантируя побитовую воспроизводимость.

Words: 54.

ES: "Canalización" is okay but "pipeline" in software is often "tublería" or "pipeline". "Canalización de procesamiento" is fine. "flujo de trabajo" could work too. I'll keep canalización forense / de procesamiento.

Now check word count for glossary again. I need to make sure the total is under 500. Let's tally precisely.

EN text: "vigia/pipeline/evidence_bundle.py is a VIGIA forensic pipeline support module. It aggregates digital artifacts, cryptographic hashes, and metadata into a unified, deterministic evidence bundle. As a stateless graph transform, it emits a read-only, validated container without altering source data, ensuring chain-of-custody integrity. Scientific note: deterministic serialization excludes volatile timestamps to guarantee bitwise reproducibility."
Count:
1-vigia/pipeline/evidence_bundle.py 2-is 3-a 4-VIGIA 5-forensic 6-pipeline 7-support 8-module. 9-It 10-aggregates 11-digital 12-artifacts, 13-cryptographic 14-hashes, 15-and 16-metadata 17-into 18-a 19-unified, 20-deterministic 21-evidence 22-bundle. 23-As 24-a 25-stateless 26-graph 27-transform, 28-it 29-emits 30-a 31-read-only, 32-validated 33-container 34-without 35-altering 36-source 37-data, 38-ensuring 39-chain-of-custody 40-integrity. 41-Scientific 42-note: 43-deterministic 44-serialization 45-excludes 46-volatile 47-timestamps 48-to 49-guarantee 50-bitwise 51-reproducibility.
51 words.

ES text: "vigia/pipeline/evidence_bundle.py es un módulo de soporte de la canalización forense VIGIA. Agrupa artefactos digitales, hashes criptográficos y metadatos en un paquete de evidencias determinista. Como transformación sin estado, emite un contenedor de solo lectura validado sin modificar los datos originales, garantizando la integridad de la cadena de custodia. Nota científica: la serialización determinista excluye marcas temporales volátiles para garantizar la reproducibilidad bit a bit."
Count:
1-vigia/pipeline/evidence_bundle.py 2-es 3-un 4-módulo 5-de 6-soporte 7-de 8-la 9-canalización 10-forense 11-VIGIA. 12-Agrupa 13-artefactos 14-digitales, 15-hashes 16-criptográficos 17-y 18-metadatos 19-en 20-un 21-paquete 22-de 23-evidencias 24-determinista. 25-Como 26-transformación 27-sin 28-estado, 29-emite 30-un 31-contenedor 32-de 33-solo 34-lectura 35-validado 36-sin 37-modificar 38-los 39-datos 40-originales, 41-garantizando 42-la 43-integridad 44-de 45-la 46-cadena 47-de 48-custodia. 49-Nota 50-científica: 51-la 52-serialización 53-determinista 54-excluye 55-marcas 56-temporales 57-volátiles 58-para 59-garantizar 60-la 61-reproducibilidad 62-bit 63-a 64-bit.
64 words.

RU text: "vigia/pipeline/evidence_bundle.py — вспомогательный модуль конвейера цифровой криминалистики VIGIA. Объединяет цифровые артефакты, криптографические хеши и метаданные в детерминированный пакет доказательств. Как преобразование без сохранения состояния, генерирует контейнер только для чтения без изменения исходных данных, обеспечивая сохранность цепочки хранения. Научное примечание: детерминированная сериализация исключает изменчивые временные метки, гарантируя побитовую воспроизводимость."
Count:
1-vigia/pipeline/evidence_bundle.py 2-— 3-вспомогательный 4-модуль 5-конвейера 6-цифровой 7-криминалистики 8-VIGIA. 9-Объединяет 10-цифровые 11-артефакты, 12-криптографические 13-хеши 14-и 15-метаданные 16-в 17-детерминированный 18-пакет 19-доказательств. 20-Как 21-преобразование 22-без 23-сохранения 24-состояния, 25-генерирует 26-контейнер 27-только 28-для 29-чтения 30-без 31-изменения 32-исходных 33-данных, 34-обеспечивая 35-сохранность 36-цепочки 37-хранения. 38-Научное 39-примечание: 40-детерминированная 41-сериализация 42-исключает 43-изменчивые 44-временные 45-метки, 46-гарантируя 47-побитовую 48-воспроизводимость.
48 words.

ZH text: "vigia/pipeline/evidence_bundle.py 是 VIGIA 取证管道的支撑模块。它将数字物证、密码学哈希与元数据聚合为确定性证据包。作为无状态图转换，它输出只读经验证的容器，不改动源数据，从而保障证据链完整性。科学备注：确定性序列化排除易变时间戳，以保障按位可重现性。"
Count Chinese characters/words. In Chinese, each character or short phrase counts? Usually word count in Chinese is characters. But the prompt says "under 500 words". Chinese text is compact. Let's count characters as words? Or count terms. Let's just assume it's fine. It's short anyway.

Glossary count.
Header: "Glossary / Glosario / Глоссарий / 术语表" = 4 words? Actually slashes may be separators. Let's count as words or not? Usually punctuation isn't counted, but to be safe, let's count conservative.

Entries:
1. Evidence bundle / Paquete de evidencias / Пакет доказательств / 证据包 — A unified forensic container. / Contenedor forense unificado. / Единый криминалистический контейнер. / 统一的取证容器。
Words:
Evidence(1) bundle(2) Paquete(3) de(4) evidencias(5) Пакет(6) доказательств(7) 证据包(8?) A(9) unified(10) forensic(11) container.(12) Contenedor(13) forense(14) unificado.(15) Единый(16) криминалистический(17) контейнер.(18) 统一的取证容器。(19)
~19 words.

2. Chain of custody / Cadena de custodia / Цепочка хранения / 保管链 — Documented evidence integrity. / Integridad documentada de evidencias. / Документированная сохранность доказательств. / 证据完整性的记录追踪。
Words:
Chain(1) of(2) custody(3) Cadena(4) de(5) custodia(6) Цепочка(7) хранения(8) 保管链(9) Documented(10) evidence(11) integrity.(12) Integridad(13) documentada(14) de(15) evidencias.(16) Документированная(17) сохранность(18) доказательств.(19) 证据完整性的记录追踪。(20)
~20 words.

3. Cryptographic hash / Hash criptográfico / Криптографический хеш / 密码学哈希 — Fixed-length data fingerprint. / Huella digital de longitud fija. / Короткий идентификатор данных. / 定长数据指纹。
Words:
Cryptographic(1) hash(2) Hash(3) criptográfico(4) Криптографический(5) хеш(6) 密码学哈希(7) Fixed-length(8) data(9) fingerprint.(10) Huella(11) digital(12) de(13) longitud(14) fija.(15) Короткий(16) идентификатор(17) данных.(18) 定长数据指纹。(19)
~19 words.

4. Metadata / Metadatos / Метаданные / 元数据 — Contextual data descriptors. / Descriptores contextuales de datos. / Контекстные описатели данных. / 数据的上下文描述符。
Words:
Metadata(1) Metadatos(2) Метаданные(3) 元数据(4) Contextual(5) data(6) descriptors.(7) Descriptores(8) contextuales(9) de(10) datos.(11) Контекстные(12) описатели(13) данных.(14) 数据的上下文描述符。(15)
~15 words.

5. Stateless transform / Transformación sin estado / Преобразование без сохранения состояния / 无状态转换 — Input-dependent, memoryless operation. / Operación sin memoria dependiente de entrada. / Операция без памяти, зависящая от входа. / 仅依赖输入的无记忆操作。
Words:
Stateless(1) transform(2) Transformación(3) sin(4) estado(5) Преобразование(6) без(7) сохранения(8) состояния(9) 无状态转换(10) Input-dependent,(11) memoryless(12) operation.(13) Operación(14) sin(15) memoria(16) dependiente(17) de(18) entrada.(19) Операция(20) без(21) памяти,(22) зависящая(23) от(24) входа.(25) 仅依赖输入的无记忆操作。(26)
~26 words.

6. Digital artifact / Artefacto digital / Цифровой артефакт / 数字物证 — Extracted source data element. / Elemento de datos fuente extraído. / Извлечённый элемент исходных данных. / 提取的源数据单元。
Words:
Digital(1) artifact(2) Artefacto(3) digital(4) Цифровой(5) артефакт(6) 数字物证(7) Extracted(8) source(9) data(10) element.(11) Elemento(12) de(13) datos(14) fuente(15) extraído.(16) Извлечённый(17) элемент(18) исходных(19) данных.(20) 提取的源数据单元。(21)
~21 words.

7. Deterministic container / Contenedor determinista / Детерминированный контейнер / 确定性容器 — Predictable, repeatable output structure. / Estructura de salida repetible y predecible. / Предсказуемая повторяемая структура выходных данных. / 可预测且可重复的输出结构。
Words:
Deterministic(1) container(2) Contenedor(3) determinista(4) Детерминированный(5) контейнер(6) 确定性容器(7) Predictable,(8) repeatable(9) output(10) structure.(11) Estructura(12) de(13) salida(14) repetible(15) y(16) predecible.(17) Предсказуемая(18) повторяемая(19) структура(20) выходных(21) данных.(22) 可预测且可重复的输出结构。(23)
~23 words.

8. Processing pipeline / Canalización de procesamiento / Конвейер обработки / 处理管道 — Ordered forensic workflow graph. / Grafo de flujo de trabajo ordenado. / Упорядоченный граф криминалистического процесса. / 有序的取证工作流图。
Words:
Processing(1) pipeline(2) Canalización(3) de(4) procesamiento(5) Конвейер(6) обработки(7) 处理管道(8) Ordered(9) forensic(10) workflow(11) graph.(12) Grafo(13) de(14) flujo(15) de(16) trabajo(17) ordenado.(18) Упорядоченный(19) граф(20) криминалистического(21) процесса.(22) 有序的取证工作流图。(23)
~23 words.

9. Downstream analysis / Análisis descendente / Последующий анализ / 下游分析 — Subsequent evidentiary examination. / Examinación probatoria posterior. / Последующее исследование доказательств. / 后续的证据审查。
Words:
Downstream(1) analysis(2) Análisis(3) descendente(4) Последующий(5) анализ(6) 下游分析(7) Subsequent(8) evidentiary(9) examination.(10) Examinación(11) probatoria(12) posterior.(13) Последующее(14) исследование(15) доказательств.(16) 后续的证据审查。(17)
~17 words.

10. Bitwise reproducibility / Reproducibilidad bit a bit / Побитовая воспроизводимость / 按位可重现性 — Identical binary output across runs. / Salida binaria idéntica entre ejecuciones. / Идентичный двоичный результат при повторных запусках. / 多次运行产生完全相同的二进制输出。
Words:
Bitwise(1) reproducibility(2) Reproducibilidad(3) bit(4) a(5) bit(6) Побитовая(7) воспроизводимость(8) 按位可重现性(9) Identical(10) binary(11) output(12) across(13) runs.(14) Salida(15) binaria(16) idéntica(17) entre(18) ejecuciones.(19) Идентичный(20) двоичный(21) результат(22) при(23) повторных(24) запусках.(25) 多次运行产生完全相同的二进制输出。(26)
~26 words.

Total glossary words: 19+20+19+15+26+21+23+23+17+26 = 209 words. Plus header 4 = 213.

Total text: 210 + 213 = 423 words. Under 500. Good.

But I need to make sure I don't use floating-point math explanations. None present.

One concern: The user asked "Generate a brief academic description (4 languages: EN, ES, RU, 中文) for this VIGIA support module. Keep it under 500 words total. Include a 10-term glossary."

I have 4 language descriptions and a 10-term glossary. I included scientific notes within the text. I should verify if the flow is good.

Let's double-check the Chinese scientific note: "确定性序列化排除易变时间戳，以保障按位可重现性。" Good.

Check Russian: "детерминированная сериализация исключает изменчивые временные метки, гарантируя побитовую воспроизводимость." Good.

One issue: In the EN text, I say "stateless graph transform". Is "graph transform" too technical for scientists who don't
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
