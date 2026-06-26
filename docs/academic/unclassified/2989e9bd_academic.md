<!--
VIGIA Academic Documentation
Module: 2989e9bd
Batch ID: vigia-doc-0025-2989e9bd
Generated: 2026-05-20T14:56:47.850039+00:00
-->

---

# ENGLISH

## What Is This Module?
This file is a **forensic maintenance script** — a precise, automated repair tool for the VIGÍA digital forensics suite. Imagine a laboratory robotic arm that opens instrument cabinets, swaps mislabeled specimen tags, removes a compromised safety seal, and installs a corrected reference chart, all while logging every action with a tamper-evident checksum. This module performs exactly those operations on software files: it corrects four specific flaws discovered during a formal forensic audit, preserves backups, verifies file integrity via deterministic SHA-256 hashes, and can undo every change if an error occurs. No floating-point approximations are used; every decision is based on exact integer hash comparisons and deterministic string matching.

## Key Concepts

| Concept | Plain-Language Definition | Role in This Module |
|---|---|---|
| **Deterministic SHA-256 Verification** | A cryptographic fingerprint computed with exact integer arithmetic over every byte of a file. If a single bit changes, the fingerprint changes completely. | Before modifying anything, the script confirms that `ebs_v1.py` matches a pre-calculated, exact hash (`EBS_V1_EXPECTED_HASH`). |
| **Verifier Independence Invariant** | A scientific rule stating that the party who packages evidence must not be the same mechanism that later certifies its authenticity. | `patch_p0b()` removes the `ForensicBundle.seal()` method from all files except the original `ebs_v1.py`, preventing a conflict of interest in the evidence-handling chain. |
| **Tombstone (Daubert Marker)** | A permanent, read-only audit record left in place of removed code, noting why the removal occurred and under whose authority. | The `_SEAL_TOMBSTONE` constant injects a forensic marker so future reviewers can see that the seal was intentionally excised. |
| **Hypothesis ID Canonical Prefix** | A rigid naming convention for evidence labels (e.g., `H_XF_001`) that prevents two different artifacts from carrying the same identifier. | `patch_p0c()` renames a colliding label inside `abductive_intent_engine.py`, and `patch_p0d()` injects the master prefix table so the naming logic is consistent and deterministic. |
| **Rollback / Backup** | The automatic creation of a safety copy (`.valkyrie_bak`) before any change, with a one-click restore function. | `rollback_all_backups()` reverts every file to its pre-patch state using exact byte-for-byte restoration. |
| **PatchResult** | A structured record indicating whether a repair succeeded, failed, or was skipped. | Returned by every patch function so the `run()` coordinator can decide whether to continue or trigger automatic rollback. |
| **LIVE Mode** | The operational state in which changes are actually written to disk (as opposed to a simulation). | If any patch fails in LIVE mode, the script automatically invokes `rollback_all_backups()` to preserve evidence integrity. |

## Glossary

- **Forensic Artifact** — Any file, log, or data object that may be presented as evidence in an audit or legal proceeding.
- **Hash (SHA-256)** — A deterministic 256-bit integer digest that uniquely identifies a file's exact content. Two files with the same hash are bit-for-bit identical.
- **Invariant** — A condition that must remain true at all times for the system to be scientifically valid.
- **Tombstone** — A non-executable audit marker left after code deletion to document the time, reason, and authority for the removal.
- **Canonical Prefix Table** — An authoritative lookup table that defines the only permitted letter codes for hypothesis identifiers, eliminating ambiguity.
- **Rollback** — The deterministic reversal of all modifications by restoring original files from their exact backups.

## 【Scientific Note】
> **Why the terminology of Peirce, Eco, and Grice is not mysticism.**  
> In the VIGÍA suite, these names refer to **semiotic sensors** — conceptual instruments that detect how meaning is formed, transmitted, and interpreted within digital evidence. Think of them not as philosophical ghosts, but as calibrated laboratory sensors:
> - A **Peirce sensor** detects the triadic relationship between a sign, the object it represents, and the interpreting mind (the interpretant).
> - An **Eco sensor** measures the boundaries of a "code" — the set of rules that makes a signal intelligible within a given culture or protocol.
> - A **Grice sensor** monitors cooperative communication expectations: it flags when a message violates the maxims of quantity, quality, relation, or manner.
>
> Just as a gas chromatograph does not "believe" in chemicals but measures them deterministically, these semiotic sensors do not invoke the occult; they apply deterministic, rule-based filters to logical fractures in evidence streams. Their outputs are integer-coded states, not vague intuitions.

---

# ESPAÑOL

## ¿Qué es este módulo?
Este archivo es un **script de mantenimiento forense** — una herramienta de reparación automatizada y precisa para la suite de forense digital VIGÍA. Imagínese un brazo robótico de laboratorio que abre gabinetes de instrumentos, corrige etiquetas de muestras mal escritas, retira un sello de seguridad comprometido e instala una tabla de referencia corregida, todo mientras
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## РУССКИЙ

### Что это за модуль?
Данный файл представляет собой **скрипт форензического обслуживания** — точный автоматизированный инструмент ремонта для комплекта цифровой криминалистики VIGÍA. Представьте лабораторный робот-манипулятор, который открывает шкафы с инструментами, меняет неправильно промаркированные ярлыки образцов, снимает скомпрометированные пломбы и устанавливает исправленные справочные таблицы — всё это с протоколированием каждого действия через защищённую от вмешательства контрольную сумму. Именно эти операции модуль выполняет над программными файлами: исправляет четыре конкретных дефекта, обнаруженных в ходе официальной судебно-криминалистической проверки, сохраняет резервные копии, проверяет целостность файлов с помощью детерминированных хэшей SHA-256 и может отменить каждое изменение при возникновении ошибки.

Каждое решение основано на точных целочисленных сравнениях хэшей и детерминированном сопоставлении строк. Никаких приближений с плавающей запятой не используется ни на одном этапе, что обеспечивает криминалистическую целостность всех операций по обслуживанию. Откат (`rollback`) осуществляется байт-в-байт: идентичные резервные копии гарантируют восстановление исходного состояния без каких-либо допущений.

Инвариант независимости верификатора — ключевая концепция этого модуля: сторона, упаковывающая доказательства, не должна совпадать с механизмом, впоследствии удостоверяющим их подлинность. Функция `patch_p0b()` закрепляет этот принцип, исключая метод `ForensicBundle.seal()` из всех файлов, кроме исходного `ebs_v1.py`.

### Ключевые концепции
| Концепция | Определение | Техническая роль |
|---|---|---|
| Детерминированная верификация SHA-256 | Криптографический отпечаток, вычисленный точной целочисленной арифметикой над каждым байтом файла | Подтверждает соответствие файла предварительно вычисленному хэшу перед любой модификацией |
| Инвариант независимости верификатора | Научное правило: упаковщик доказательств не должен быть их верификатором | Реализован функцией `patch_p0b()`, исключающей метод seal() из всех файлов, кроме исходного |
| Надгробие (маркер Добера) | Постоянная запись аудита только для чтения, оставленная вместо удалённого кода | Константа `_SEAL_TOMBSTONE` позволяет будущим ревизорам видеть, что удаление было намеренным |
| Канонический префикс ID гипотезы | Жёсткое соглашение об именовании меток доказательств | Предотвращает коллизии идентификаторов в `abductive_intent_engine.py` |
| Откат / Резервная копия | Автоматическое создание копии безопасности `.valkyrie_bak` перед любым изменением | `rollback_all_backups()` восстанавливает каждый файл побайтово |
| PatchResult | Структурированная запись о результате ремонта (успех, неудача, пропуск) | Позволяет координатору `run()` принять решение о продолжении или откате |
| Режим LIVE | Операционное состояние, при котором изменения фактически записываются на диск | При сбое в режиме LIVE автоматически вызывается откат для сохранения целостности улик |

> **【Научное примечание】**
> Терминология Пирса, Эко и Грайса — это не мистика, а формальная аналитическая механика. Как спектрометр преобразует фотонные взаимодействия в дискретные целочисленные отсчёты, этот модуль преобразует сигналы улик в детерминированные целочисленные оценки. Целочисленная арифметика гарантирует воспроизводимость в суде без округлений и аппроксимаций. Любое нарушение логики в цепочке артефактов фиксируется как целочисленный флаг, а не интуитивное суждение.

### Глоссарий
1. **Форензический артефакт** — Любой файл, журнал или объект данных, который может быть представлен в качестве доказательства.
2. **Хэш (SHA-256)** — Детерминированный 256-битный целочисленный дайджест, уникально идентифицирующий точное содержимое файла.
3. **Инвариант** — Условие, которое должно всегда оставаться истинным для научной валидности системы.
4. **Надгробие** — Неисполняемый маркер аудита, оставленный после удаления кода для документирования времени, причины и полномочия удаления.
5. **Каноническая таблица префиксов** — Авторитетная таблица поиска, определяющая единственно допустимые коды для идентификаторов гипотез.
6. **Откат** — Детерминированная отмена всех изменений путём восстановления исходных файлов из точных резервных копий.
7. **Детерминированная система** — Система, в которой одинаковые входные данные всегда порождают одинаковые выходные данные.
8. **Верификатор** — Независимый механизм, подтверждающий подлинность и целостность форензического артефакта.
9. **Стандарт Добера** — Правовой критерий допустимости научных доказательств, требующий воспроизводимости.
10. **Коллизия идентификатора** — Ситуация, когда два разных арtefакта несут один и тот же метаданный идентификатор; устраняется канонической таблицей префиксов.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## 中文

### 这是什么模块？
本文件是一个**取证维护脚本**——VIGÍA数字取证套件的精确自动化修复工具。想象一个实验室机械臂，它打开仪器柜、替换错误标记的样本标签、移除受损的安全封条、安装经过修正的参考图表，同时用防篡改校验和记录每一个操作。本模块对软件文件执行完全相同的操作：修正在正式取证审计中发现的四个特定缺陷，保存备份，通过确定性SHA-256哈希验证文件完整性，并可在出现错误时撤销所有更改。

所有决策均基于精确整数哈希比较和确定性字符串匹配，不使用任何近似运算。回滚操作按字节进行：完全相同的备份副本保证在无任何假设的情况下恢复原始状态，确保取证可重现性。

验证者独立性不变量是本模块的核心原则：打包证据的一方不得与后来认证其真实性的机制相同。`patch_p0b()`函数通过从除原始`ebs_v1.py`外的所有文件中移除`ForensicBundle.seal()`方法来落实这一原则。

### 关键概念
| 概念 | 定义 | 技术作用 |
|---|---|---|
| 确定性SHA-256验证 | 对文件每个字节用精确整数运算计算的密码学指纹 | 在任何修改前确认文件与预计算哈希相符 |
| 验证者独立性不变量 | 打包证据的一方不得是后来认证其真实性的机制 | 由`patch_p0b()`实现，从所有文件中移除seal()方法 |
| 墓碑（道伯特标记） | 代替已删除代码留下的永久只读审计记录 | `_SEAL_TOMBSTONE`常量使未来审查者可见删除是有意为之 |
| 假设ID规范前缀 | 证据标签的严格命名约定，防止不同取证工件带有相同标识符 | `patch_p0c()`重命名冲突标签，`patch_p0d()`注入主前缀表 |
| 回滚/备份 | 每次更改前自动创建`.valkyrie_bak`安全副本 | `rollback_all_backups()`按字节恢复每个文件 |
| PatchResult | 指示修复成功、失败或跳过的结构化记录 | 由每个修补函数返回以供协调器决策 |
| LIVE模式 | 更改实际写入磁盘的操作状态 | 任何修补失败时自动调用回滚以保护证据完整性 |

> **【科学说明】**
> 皮尔斯（Peirce）、艾柯（Eco）和格赖斯（Grice）的术语并非神秘主义，而是形式化的分析机制。如同光谱仪将光子相互作用转换为离散整数计数，本模块将证据信号转换为确定性整数分数。精确整数运算确保法庭可重现性。取证工件链的逻辑断裂以整数标志事件形式被检测。

### 词汇表
1. **取证工件** — 可在审计或法律程序中作为证据提交的任何文件、日志或数据对象。
2. **哈希（SHA-256）** — 唯一标识文件精确内容的确定性256位整数摘要。
3. **不变量** — 系统科学有效性所要求的、必须始终为真的条件。
4. **墓碑** — 代码删除后留下的不可执行审计标记，记录删除的时间、原因和授权。
5. **规范前缀表** — 定义假设标识符唯一允许字母代码的权威查找表，消除歧义。
6. **回滚** — 通过从精确备份恢复原始文件来确定性撤销所有修改。
7. **确定性系统** — 相同输入始终产生相同输出的系统。
8. **验证者** — 确认取证工件真实性和完整性的独立机制。
9. **道伯特标准** — 要求可重现性的科学证据可采性法律标准。
10. **标识符冲突** — 两个不同取证工件带有相同元数据标识符的情况；由规范前缀表消除。

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
