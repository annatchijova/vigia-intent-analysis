<!--
VIGIA Academic Documentation
Module: 14ba142e
Batch ID: vigia-doc-0187-14ba142e
Generated: 2026-05-20T14:56:47.885048+00:00
-->

English:
The `vigia_namespace_shim.py` module is a namespace adaptation layer for the VIGÍA forensic suite. Because the repository stores all Python source files in a single flat directory rather than a hierarchical package tree, internal statements such as `from vigia.core.X import Y` cannot resolve. This shim programmatically maps each flat module into the expected dotted namespace at runtime, enabling the codebase to behave as though it were organized in subpackages. It is transparent to the analyst and requires no manual path changes. Scientific note: this is a deterministic registration process; module identities are preserved exactly.

Español:
El módulo `vigia_namespace_shim.py` actúa como capa de adaptación de espacio de nombres para la suite forense VIGÍA. Dado que el repositorio es plano—todos los archivos `.py` residen en un único directorio—, las importaciones del tipo `from vigia.core.X import Y` fallan. Este shim registra determinísticamente cada módulo plano en el namespace jerárquico esperado durante la ejecución, preservando la identidad exacta de cada componente sin intervención del analista.

Русский:
Модуль `vigia_namespace_shim.py` представляет собой адаптационный слой пространства имён для судебно-аналитического комплекса VIGÍA. Поскольку все файлы `.py` находятся в одном плоском каталоге, а не в древовидной структуре пакетов, конструкции вида `from vigia.core.X import Y` не разрешаются. Данный shim детерминированно регистрирует каждый плоский модуль в ожидаемой иерархической схеме имён во время выполнения, сохраняя точную идентичность модулей.

中文:
`vigia_namespace_shim.py` 模块是 VIGÍA 数字取证套件的命名空间适配层。由于代码库采用扁平结构（所有 `.py` 文件位于同一目录），形如 `from vigia.core.X import Y` 的层级导入语句无法解析。该 shim 在运行时以确定性方式将各扁平模块注册至预期的点分命名空间，使代码行为等同于按子包组织，且完全无需分析人员手动调整路径。

Now glossary. 10 terms. Must be included. Under 500 words total. Let's count.

EN: ~50 words.
ES: ~45 words.
RU: ~45 words.
ZH: ~45 words.
Total description: ~185 words.
Remaining for glossary: ~315 words. 10 terms => ~30 words per term.

Let's refine to be safe. Let's aim for very short.

English (revision, tighter):
`vigia_namespace_shim.py` is a namespace adaptation layer for the VIGÍA forensic suite. The repository stores all source files in a single flat directory, so hierarchical import statements such as `from vigia.core.X import Y` fail. At runtime, this shim deterministically registers every flat module into the expected dotted namespace, preserving exact module identities without analyst intervention. (43 words)

Español:
`vigia_namespace_shim.py` es una capa de adaptación de espacio de nombres para la suite forense VIGÍA. Al ser el repositorio plano, las importaciones jerárquicas como `from vigia.core.X import Y` fallan. Este shim registra determinísticamente cada módulo plano en el namespace esperado durante la ejecución, preservando la identidad exacta de los componentes sin intervención del analista. (41 words)

Русский:
`vigia_namespace_shim.py` — адаптационный слой пространства имён комплекса VIGÍA. Все исходные файлы расположены в одном плоском каталоге, поэтому иерархические импорты вида `from vigia.core.X import Y` не разрешаются. Shim детерминированно регистрирует каждый плоский модуль в требуемую иерархию имён во время выполнения, сохраняя точную идентичность модулей. (39 words)

中文:
`vigia_namespace_shim.py` 是 VIGÍA 取证套件的命名空间适配层。仓库为扁平结构，所有 `.py` 文件位于同一目录，导致层级导入语句 `from vigia.core.X import Y` 无法解析。该 shim 在运行时以确定性方式将各扁平模块注册至预期的点分命名空间，精确保持模块身份，无需分析人员干预。 (45 words)

Total description ~168 words.
Remaining ~330 words for glossary. 10 terms. ~33 words each. Good.

Glossary terms:
1. Namespace (Espacio de nombres / Пространство имён / 命名空间)
2. Shim
3. Flat directory structure (Estructura de directorio plana / Плоская структура каталогов / 扁平目录结构)
4. Import statement (Sentencia de importación / Инструкция импорта / 导入语句)
5. Deterministic registration (Registro determinístico / Детерминированная регистрация / 确定性注册)
6. Runtime (Tiempo de ejecución / Время выполнения / 运行时)
7. Module identity (Identidad de módulo / Идентичность модуля / 模块身份)
8. Dotted namespace (Namespace punteado / Точечное пространство имён / 点分命名空间)
9. Source file (Archivo fuente / Исходный файл / 源文件)
10. Analyst intervention (Intervención del analista / Вмешательство аналитика / 分析人员干预)

I need to keep definitions very short.

Glossary draft:

1. **Namespace** — A symbolic container that holds logical names for objects to avoid collisions. / Contenedor simbólico de nombres lógicos para evitar colisiones. / Символический контейнер логических имён, предотвращающий конфликты. / 避免名称冲突的逻辑名称符号容器。

2. **Shim** — A thin compatibility layer that translates calls between interfaces. / Capa delgada de compatibilidad que traduce llamadas entre interfaces. / Тонкий совместимый слой, транслирующий вызовы между интерфейсами. / 在不同接口之间转换调用的薄型兼容层。

3. **Flat directory** — A single-folder layout with no subdirectories. / Disposición en una sola carpeta sin subdirectorios. / Размещение всех файлов в одном каталоге без подкаталогов. / 无子目录的单层文件夹布局。

4. **Import statement** — A directive that makes external code available to the current module. / Directiva que hace disponible código externo al módulo actual. / Директива, подключающая внешний код к текущему модулю. / 将外部代码引入当前模块的指令。

5. **Deterministic registration** — A repeatable mapping process that yields identical results for identical inputs. / Proceso de mapeo repetible que produce el mismo resultado ante mismas entradas. / Повторяемый процесс сопоставления, дающий одинаковый результат при одинаковых входных данных. / 对相同输入始终产生相同映射结果的可重复过程。

6. **Runtime** — The execution phase of a program after loading. / Fase de ejecución de un programa tras su carga. / Этап выполнения программы после её загрузки. / 程序加载后的执行阶段。

7. **Module identity** — The canonical name and attributes that uniquely define a code unit. / Nombre canónico y atributos que definen unívocamente una unidad de código. / Каноническое имя и атрибуты, однозначно определяющие единицу кода. / 唯一标识代码单元的规范名称及属性。

8. **Dotted namespace** — A hierarchical naming scheme using periods as delimiters (e.g., `vigia.core`). / Esquema jerárquico de nombres separados por puntos (p. ej., `vigia.core`). / Иерархическая схема имён с точками в качестве разделителей (например, `vigia.core`). / 使用句点分隔符的层级命名方案（如 `vigia.core`）。

9. **Source file** — A human-readable text file containing program instructions. / Archivo de texto legible que contiene instrucciones del programa. / Текстовый файл с инструкциями программы, читаемый человеком. / 包含程序指令的人类可读文本文件。

10. **Analyst intervention** — Manual action required from a forensic examiner. / Acción manual requerida por el examinador forense. / Ручное действие, требуемое от судебного эксперта. / 取证检验人员所需执行的手动操作。

Now let's count words carefully.

EN description: 
vigia_namespace_shim.py is a namespace adaptation layer for the VIGÍA forensic suite. The repository stores all source files in a single flat directory, so hierarchical import statements such as from vigia.core.X import Y fail. At runtime, this shim deterministically registers every flat module into the expected dotted namespace, preserving exact module identities without analyst intervention.
Let's count:
1 vigia_namespace_shim.py 2 is 3 a 4 namespace 5 adaptation 6 layer 7 for 8 the 9 VIGÍA 10 forensic 11 suite. 12 The 13 repository 14 stores 15 all 16 source 17 files 18 in 19 a 20 single 21 flat 22 directory, 23 so 24 hierarchical 25 import 26 statements 27 such 28 as 29 from 30 vigia.core.X 31 import 32 Y 33 fail. 34 At 35 runtime, 36 this 37 shim 38 deterministically 39 registers 40 every 41 flat 42 module 43 into 44 the 45 expected 46 dotted 47 namespace, 48 preserving 49 exact 50 module 51 identities 52 without 53 analyst 54 intervention. => 54 words.

ES description:
vigia_namespace_shim.py es una capa de adaptación de espacio de nombres para la suite forense VIGÍA. Al ser el repositorio plano, las importaciones jerárquicas como from vigia.core.X import Y fallan. Este shim registra determinísticamente cada módulo plano en el namespace esperado durante la ejecución, preservando la identidad exacta de los componentes sin intervención del analista.
Count: 1 vigia_namespace_shim.py 2 es 3 una 4 capa 5 de 6 adaptación 7 de 8 espacio 9 de 10 nombres 11 para 12 la 13 suite 14 forense 15 VIGÍA. 16 Al 17 ser 18 el 19 repositorio 20 plano, 21 las 22 importaciones 23 jerárquicas 24 como 25 from 26 vigia.core.X 27 import 28 Y 29 fallan. 30 Este 31 shim 32 registra 33 determinísticamente 34 cada 35 módulo 36 plano 37 en 38 el 39 namespace 40 esperado 41 durante 42 la 43 ejecución, 44 preservando 45 la 46 identidad 47 exacta 48 de 49 los 50 componentes 51 sin 52 intervención 53 del 54 analista. => 54 words.

RU description:
vigia_namespace_shim.py — адаптационный слой пространства имён комплекса VIGÍA. Все исходные файлы расположены в одном плоском каталоге, поэтому иерархические импорты вида from vigia.core.X import Y не разрешаются. Shim детерминированно регистрирует каждый плоский модуль в требуемую иерархию имён во время выполнения, сохраняя точную идентичность модулей.
Count: 1 vigia_namespace_shim.py 2 — 3 адаптационный 4 слой 5 пространства 6 имён 7 комплекса 8 VIGÍA. 9 Все 10 исходные 11 файлы 12 расположены 13 в 14 одном 15 плоском 16 каталоге, 17 поэтому 18 иерархические 19 импорты 20 вида 21 from 22 vigia.core.X 23 import 24 Y 25 не 26 разрешаются. 27 Shim 28 детерминированно 29 регистрирует 30 каждый 31 плоский 32 модуль 33 в 34 требуемую 35 иерархию 36 имён 37 во 38 время 39 выполнения, 40 сохраняя 41 точную 42 идентичность 43 модулей. => 43 words.

ZH description:
vigia_namespace_shim.py 是 VIGÍA 取证套件的命名空间适配层。仓库为扁平结构，所有 .py 文件位于同一目录，导致层级导入语句 from vigia.core.X import Y 无法解析。该 shim 在运行时以确定性方式将各扁平模块注册至预期的点分命名空间，精确保持模块身份，无需分析人员干预。
Count: 1 vigia_namespace_shim.py 2 是 3 VIGÍA 4 取证 5 套件 6 的 7 命名 8 空间 9 适配 10 层。 11 仓库 12 为 13 扁平 14 结构， 15 所有 16 .py 17 文件 18 位于 19 同一 20 目录， 21 导致 22 层级 23 导入 24 语句 25 from 26 vigia.core.X 27 import 28 Y 29 无法 30 解析。 31 该 32 shim 33 在 34 运行时 35 以 36 确定性 37 方式 38 将 39 各 40 扁平 41 模块 42 注册 43 至 44 预期 45 的 46 点分 47 命名 48 空间， 49 精确 50 保持 51 模块 52 身份， 53 无需 54 分析 55 人员 56 干预。 => 56 words.

Total description words: 54+54+43+56 = 207 words.

Glossary words:
1. Namespace — A symbolic container that holds logical names for objects to avoid collisions. (12 words) / Contenedor simbólico de nombres lógicos para evitar colisiones. (10) / Символический контейнер логических имён, предотвращающий конфликты. (6) / 避免名称冲突的逻辑名称符号容器。 (Words in Chinese are characters, but let's count them as words for estimation? Actually word count for Chinese is characters, but total "words" in mixed text is tricky. The user likely means English word count or general token count. I'll keep it short.)

Maybe the glossary can be a single block with each term in 4 languages on one line? That's still heavy.

Let's reconsider. The user says "Include a 10-term glossary." It doesn't explicitly say the glossary must be in 4 languages, but since I always write in 4 languages, I should include all 4. However, with 500 words total, it's almost impossible to have 10 terms defined in 4 languages unless each definition is 3-4 words. That's not feasible.

Alternative interpretation: The description is in 4 languages (as separate paragraphs), and the glossary is a separate section perhaps with terms in English and equivalents? Or maybe the user wants the glossary to be multilingual too but I can be extremely concise.

Actually, looking at the prompt: "You always write in 4 languages: ENGLISH, ESPAÑOL, РУССКИЙ, 中文. You include glossaries and scientific notes."

So the whole document should be in 4 languages. But a glossary is typically a list of terms. I can provide a compact glossary where each entry is:
**Term (EN) / Término (ES) / Термин (RU) / 术语 (ZH)**: Definition in 4 languages? That quadruples size.

Maybe I can provide 4 mini-glossaries, one per language, but that's also large.

Given the 500-word total limit, the most practical approach is to provide the description in 4 short paragraphs, then a glossary where each entry gives the term in all 4 languages and a single-sentence definition that is itself multilingual? No, that would be messy.

Better: Provide the description in 4 languages (as required). Then for the glossary, list 10 terms, each with a 4-language definition separated by slashes. This is common in multilingual docs. For example:
- **Namespace / Espacio de nombres / Пространство имён / 命名空间**: Logical container for names / Contenedor lógico de nombres / Логический контейнер имён / 逻辑名称容器。

But that still multiplies. Let's think about word count. If I use slashes and keep each entry to about 20 words total across all languages, 10 entries = 200 words. Plus 200 words for descriptions = 400. That fits.

Let's try to compress the glossary entries to roughly 20-25 words per entry across all 4 languages.

Glossary structure per entry:
**EN term / ES term / RU term / ZH term** — EN def. / ES def. / RU def. / ZH def.

Let's draft:

1. **Namespace / Espacio de nombres / Пространство имён / 命名空间** — Symbolic container for logical names to prevent collisions. / Contenedor simbólico de nombres lógicos para prevenir colisiones. / Символический контейнер логических имён, предотвращающий коллизии. / 防止命名冲突的逻辑名称符号容器。

Count: ~23 words.

2. **Shim** — Compatibility layer translating interfaces. / Capa de compatibilidad que traduce interfaces. / Совместимый слой, транслирующий интерфейсы. / 转换接口的兼容层。
Count: ~15 words.

3. **Flat directory / Directorio plano / Плоский каталог / 扁平目录** — Single-folder layout without subdirectories. / Diseño en una sola carpeta sin subdirectorios. / Размещение в одном каталоге без подкаталогов. / 无子目录的单层文件夹结构。
Count: ~19 words.

4. **Import statement / Sentencia de importación / Инструкция импорта / 导入语句** — Directive that introduces external code into a module. / Directiva que introduce código externo en un módulo. / Директива подключения внешнего кода к модулю. / 将外部代码引入模块的指令。
Count: ~19 words.

5. **Deterministic registration / Registro determinístico / Детерминированная регистрация / 确定性注册** — Reproducible mapping yielding identical results for identical inputs. / Mapeo reproducible que produce idénticos resultados ante iguales entradas. / Воспроизводимое сопоставление, дающее одинаковый результат. / 对相同输入始终产生一致结果的可重复映射。
Count: ~20 words.

6. **Runtime / Tiempo de ejecución / Время выполнения / 运行时** — Program execution phase after loading. / Fase de ejecución del programa tras la carga. / Этап выполнения программы после загрузки. / 程序加载后的执行阶段。
Count: ~16 words.

7. **Module identity / Identidad del módulo / Идентичность модуля / 模块身份** — Canonical name and attributes uniquely defining a code unit. / Nombre canónico y atributos que definen unívocamente una unidad de código. / Каноническое имя и атрибуты, однозначно определяющие единицу кода. / 唯一标识代码单元的规范名称与属性。
Count: ~20 words.

8. **Dotted namespace / Namespace punteado / Точечное пространство имён / 点分命名空间** — Hierarchical naming scheme using periods as delimiters. / Esquema jerárquico de nombres con puntos como delimitadores. / Иерархическая схема имён с точками-разделителями. / 以句点为分隔符的层级命名方案。
Count: ~19 words.

9. **Source file / Archivo fuente / Исходный файл / 源文件** — Human-readable text file containing program instructions. / Archivo de texto legible que contiene instrucciones del programa. / Текстовый файл с инструкциями программы, читаемый человеком. / 包含程序指令的人类可读文本文件。
Count: ~18 words.

10. **Analyst intervention / Intervención del analista / Вмешательство аналитика / 分析人员干预** — Manual action required from a forensic examiner. / Acción manual requerida por el examinador forense. / Ручное действие, требуемое от судебного эксперта. / 取证检验人员必须执行的手动操作。
Count: ~18 words.

Now total word estimate:
Descriptions: ~207 words.
Glossary: let's sum roughly.
Entry 1: 23
Entry 2: 15
Entry 3: 19
Entry 4: 19
Entry 5: 20
Entry 6: 16
Entry 7: 20
Entry 8: 19
Entry 9: 18
Entry 10: 18
Total glossary: ~187 words.
Grand total: ~394 words. This is safely under 500.

I should format cleanly. Use bold headers for languages? The user said "4 languages". Usually I label each paragraph.

Let's do:

**ENGLISH**
[text]

**ESPAÑOL**
[text]

**РУССКИЙ**
[text]

**中文**
[text]

**Glossary / Glosario / Глоссарий / 词汇表**

Then list.

Actually, "Scientific note" could be a separate single line shared across languages? No, that violates the 4-language rule. I can append a short note in each language.

Let's adjust descriptions to include a brief scientific note phrase.

EN: ... preserving exact module identities without analyst intervention. *Scientific note:* The mapping is deterministic and stateless.
(10 more words)

ES: ... sin intervención del analista. *Nota científica:* El mapeo es determinístico y sin estado.
(9 words)

RU: ... модулей. *Научное примечание:* Сопоставление детерминировано и не имеет состояния.
(7 words)

ZH: ... 干预。*科学注：* 该映射是确定性的且无状态。
(8 words)

This adds ~34 words. Total becomes ~428. Still under 500. Good.

Let's refine the texts to be polished.

EN:
**ENGLISH**
`vigia_namespace_shim.py` is a namespace adaptation layer for the VIGÍA forensic suite. The repository stores all source files in a single flat directory, so hierarchical import statements such as `from vigia.core.X import Y` fail. At runtime, this shim deterministically registers every flat module into the expected dotted namespace, preserving exact module identities without analyst intervention. *Scientific note:* The mapping is deterministic and stateless.

ES:
**ESPAÑOL**
`vigia_namespace_shim.py` es una capa de adaptación de espacio de nombres para la suite forense VIGÍA. Al ser el repositorio plano, las importaciones jerárquicas como `from vigia.core.X import Y` fallan. Este shim registra determinísticamente cada módulo plano en el namespace esperado durante la ejecución, preservando la identidad exacta de los componentes sin intervención del analista. *Nota científica:* El mapeo es determinístico y sin estado.

RU:
**РУССКИЙ**
`vigia_namespace_shim.py` — адаптационный слой пространства имён комплекса VIGÍA. Все исходные файлы расположены в одном плоском каталоге, поэтому иерархические импорты вида `from vigia.core.X import Y` не разрешаются. Shim детерминированно регистрирует каждый плоский модуль в требуемую иерархию имён во время выполнения, сохраняя точную идентичность модулей. *Научное примечание:* Сопоставление детерминировано и не имеет состояния.

ZH:
**中文**
`vigia_namespace_shim.py` 是 VIGÍA 取证套件的命名空间适配层。仓库为扁平结构，所有 `.py` 文件位于同一目录，导致层级导入语句 `from vigia.core.X import Y` 无法解析。该 shim 在运行时以确定性方式将各扁平模块注册至预期的点分命名空间，精确保持模块身份，无需分析人员干预。*科学注释：* 该映射是确定性的且无状态。

Now glossary.

**Glossary / Glosario / Глоссарий / 词汇表**

1. **Namespace / Espacio de nombres / Пространство имён / 命名空间** — Symbolic container for logical names to prevent collisions. / Contenedor simbólico de nombres lógicos para prevenir colisiones. / Символический контейнер логических имён, предотвращающий коллизии. / 防止命名冲突的逻辑名称符号容器。

2. **Shim** — Compatibility layer translating interfaces. / Capa de compatibilidad que traduce interfaces. / Совместимый слой, транслирующий интерфейсы. / 转换接口的兼容层。

3. **Flat directory / Directorio plano / Плоский каталог / 扁平目录** — Single-folder layout without subdirectories. / Diseño de carpeta única sin subdirectorios. / Размещение файлов в одном каталоге без подкаталогов. / 无子目录的单层文件夹结构。

4. **Import statement / Sentencia de importación / Инструкция импорта / 导入语句** — Directive that introduces external code into a module. / Directiva que introduce código externo en un módulo. / Директива подключения внешнего кода к модулю. / 将外部代码引入模块的指令。

5. **Deterministic registration / Registro determinístico / Детерминированная регистрация / 确定性注册** — Reproducible mapping yielding identical results for identical inputs. / Mapeo reproducible que produce idénticos resultados ante iguales entradas. / Воспроизводимое сопоставление, дающее одинаковый результат. / 对相同输入始终产生一致结果的可重复映射。

6. **Runtime / Tiempo de ejecución / Время выполнения / 运行时** — Program execution phase after loading. / Fase de ejecución del programa tras su carga. / Этап выполнения программы после загрузки. / 程序加载后的执行阶段。

7. **Module identity / Identidad del módulo / Идентичность модуля / 模块身份** — Canonical name and attributes uniquely defining a code unit. / Nombre canónico y atributos que definen unívocamente una unidad de código. / Каноническое имя и атрибуты, однозначно определяющие единицу кода. / 唯一标识代码单元的规范名称与属性。

8. **Dotted namespace / Namespace punteado / Точечное пространство имён / 点分命名空间** — Hierarchical naming scheme using periods as delimiters. / Esquema jerárquico de nombres con puntos como delimitadores. / Иерархическая схема имён с точками-разделителями. / 以句点为分隔符的层级命名方案。

9. **Source file / Archivo fuente / Исходный файл / 源文件** — Human-readable text file containing program instructions. / Archivo de texto legible que contiene instrucciones del programa. / Текстовый файл с инструкциями программы, читаемый человеком. / 包含程序指令的人类可读文本文件。

10. **Analyst intervention / Intervención del analista / Вмешательство аналитика / 分析人员干预** — Manual action required from a forensic examiner. / Acción manual requerida por el examinador forense. / Ручное действие, требуемое от судебного эксперта. / 取证检验人员必须执行的手动操作。

Now let's do a precise word count to ensure under 500. I'll count every token separated by spaces.

EN para:
ENGLISH (1)
vigia_namespace_shim.py (2) is (3) a (4) namespace (5) adaptation (6) layer (7) for (8) the (9) VIGÍA (10) forensic (11) suite. (12) The (13) repository (14) stores (15) all (16) source (17) files (18) in (19) a (20) single (21) flat (22) directory, (23) so (24) hierarchical (25) import (26) statements (27) such (28) as (29) from (30) vigia.core.X (31) import (32) Y (33) fail. (34) At (35) runtime, (36) this (37) shim (38) deterministically (39) registers (40) every (41) flat (42) module (43) into (44) the (45) expected (46) dotted (47) namespace, (48) preserving (49) exact (50) module (51) identities (52) without (53) analyst (54) intervention. (55) Scientific (56) note: (57) The (58) mapping (59) is (60) deterministic (61) and (62) stateless. (63)
=> 63 words (including header? Usually headers count, but I'll be safe and include them or not; even if included, still okay).

ES para:
ESPAÑOL (1)
vigia_namespace_shim.py (2) es (3) una (4) capa (5) de (6) adaptación (7) de (8) espacio (9) de (10) nombres (11) para (12) la (13) suite (14) forense (15) VIGÍA. (16) Al (17) ser (18) el (19) repositorio (20) plano, (21) las (22) importaciones (23) jerárquicas (24) como (25) from (26) vigia.core.X (27) import (28) Y (29) fallan. (30) Este (31) shim (32) registra (33) determinísticamente (34) cada (35) módulo (36) plano (37) en (38) el (39) namespace (40) esperado (41) durante (42) la (43) ejecución, (44) preservando (45) la (46) identidad (47) exacta (48) de (49) los (50) componentes (51) sin (52) intervención (53) del (54) analista. (55) Nota (56) científica: (57) El (58) mapeo (59) es (60) determinístico (61) y (62) sin (63) estado. (64)
=> 64 words.

RU para:
РУССКИЙ (1)
vigia_namespace_shim.py (2) — (3) адаптационный (4) слой (5) пространства (6) имён (7) комплекса (8) VIGÍA. (9) Все (10) исходные (11) файлы (12) расположены (13) в (14) одном (15) плоском (16) каталоге, (17) поэтому (18) иерархические (19) импорты (20) вида (21) from (22) vigia.core.X (23) import (24) Y (25) не (26) разрешаются. (27) Shim (28) детерминированно (29) регистрирует (30) каждый (31) плоский (32) модуль (33) в (34) требуемую (35) иерархию (
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
