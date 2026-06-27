<!--
VIGIA Academic Documentation
Module: 02a8adb4
Batch ID: vigia-doc-0056-02a8adb4
Generated: 2026-05-20T14:56:47.856511+00:00
-->

## ENGLISH

### What Is This Module?
`vigia/core/forensic_technical_detector.py` v2.3.5 is the deterministic rule engine of a digital-forensics platform. Its purpose is to inspect digital artifacts—file paths, system logs, memory strings, registry entries—for structural and lexical indicators of compromise. The module does not guess; it applies immutable rule tables, exact integer-score thresholds, and lexical boundary checks to reach a verdict. Version 2.3.5 refines this rigor with a hybrid balancer that prevents concentrated evidence from being undervalued, a hard input-anomaly cap that blocks denial-of-service exhaustion before pattern matching begins, and an expanded Spanish lexicon for shadow-copy detection.

### Key Concepts

| Concept | Description | Deterministic Mechanism |
|---|---|---|
| **Forensic Artifact** | Digital specimen (log, path, registry key) submitted for inspection. | Immutable input; identical on every analysis. |
| **Detector Engine** | Central component (`ForensicTechnicalDetector`) that loads rules and executes tests. | Static rule tables loaded once; reproducible output. |
| **Analysis Function** (`analyze`) | The entry point that runs sanitation, pattern matching, scoring, and verdict. | Fixed sequence of integer comparisons and lookups. |
| **Score Thresholds** (`BASE_Z`, `MAX_Z`) | Discrete levels representing evidentiary weight. | Compared by exact integer inequality; no rounding. |
| **Synergy Caps** (`SYNERGY_STEP`, `MAX_SYNERGY`) | Incremental reward when independent categories co-occur. | Integer addition with a hard ceiling; no drift. |
| **Anomaly Limit** (`INPUT_ANOMALIES_LIMIT`) | Maximum irregular tokens accepted before regex evaluation. | Hard stop at a whole-number count. |
| **Hybrid Balancer** (M4) | Adjusts effective category count so concentrated evidence in one category is not weaker than scattered evidence across many. | Uses integer division (`//`) and whole-number `max()`. |
| **Shadow-Copy Lexicon** | Localized keywords detecting volume-snapshot abuse. | Deterministic dictionary membership test. |
| **Word Boundaries** | Lexical delimiters preventing partial-string false positives. | Exact positional matching; no probabilistic guess. |

### Glossary

- **Artifact (Forensic Artifact)**: Any digital object extracted from a host or network and submitted for inspection.
- **Deterministic Integer Arithmetic**: Mathematical operations on whole numbers that produce identical outputs for identical inputs, without rounding or approximation.
- **Logic Break**: A structural inconsistency between an artifact's expected behavior and its observed form, suggesting tampering.
- **Shadow Copy**: A volume-snapshot mechanism that attackers may abuse to conceal data; detected via localized keyword matching.
- **Synergy**: The cumulative evidentiary weight generated when multiple independent indicator categories co-occur.
- **Word Boundary**: A lexical delimiter that constrains pattern matching to complete tokens, eliminating partial-word false positives.
- **Hybrid Balancer (M4)**: The v2.3.5 algorithm that computes an effective category count using whole-number division and comparison, ensuring a single strong category is scored fairly against several weak ones.
- **Anomaly Cap**: The integer limit placed on irregular input tokens before they enter the regex evaluation stage.

### 【Scientific Note】
> 【Scientific Note】
> This module occasionally references terminology associated with Charles Sanders Peirce, Umberto Eco, and H. P. Grice—semioticians who created formal models of how signs, codes, and communication generate meaning. These names are **not** mystical invocations. Treat the detector as a sensor: Peirce supplied the optical geometry (how a sign refracts into an interpretant), Eco provided the calibration standard (which codes map to which threats), and Grice installed the noise filter (what deviation from expected cooperation reveals a covert signal). The schematic is grounded in formal logic; every verdict is produced by deterministic integer arithmetic, not intuition.

---

## ESPAÑOL

### ¿Qué es este módulo?
`vigia/core/forensic_technical_detector.py` v2.3.5 es el motor de reglas determinista de una plataforma de informática forense. Su propósito es inspeccionar artefactos digitales—rutas de archivo, registros del sistema, cadenas de memoria, entradas de registro—en busca de indicadores estructurales y léxicos de compromiso. El módulo no conjetura; aplica tablas de reglas inmutables, umbrales exactos de puntuación en aritmética entera y verificaciones de delimitación léxica para emitir un veredicto. La versión 2.3.5 refina este rigor con un balanceador híbrido que evita la subvaloración de evidencia concentrada, un tope duro de anomalías de entrada que bloquea el agotamiento por DoS antes de que comience la coincidencia de patrones, y un léxico español ampliado para la detección de shadow copy.

### Conceptos Clave

| Concepto | Descripción | Mecanismo Determinista |
|---|---|---|
| **Artefacto Forense** | Espécimen digital (log, ruta, clave de registro) sometido a inspección. | Entrada inmutable; idéntica en cada análisis. |
| **Motor Detector** | Componente central (`ForensicTechnicalDetector`) que carga reglas y ejecuta pruebas. | Tablas de reglas estáticas cargadas una sola vez; salida reproducible. |
| **Función de Análisis** (`analyze`) | Punto de entrada que ejecuta sanitización, coincidencia de patrones, puntuación y veredicto. | Secuencia fija de comparaciones enteras y búsquedas. |
| **Umbrales de Puntuación** (`BASE_Z`, `MAX_Z`) | Niveles discretos que representan el peso evidencial. | Comparados por desigualdad entera exacta; sin redondeo. |
| **Topes de Sinergia** (`SYNERGY_STEP`, `MAX_SYNERGY`) | Recompensa incremental cuando categorías independientes coocurren. | Suma entera con techo rígido; sin deriva. |
| **Límite de Anomalías** (`INPUT_ANOMALIES_LIMIT`) | Máximo de tokens irregulares aceptados antes de la evaluación por expresiones regulares. | Parada rígida en un conteo de números enteros. |
| **Balanceador Híbrido** (M4) | Ajusta el conteo efectivo de categorías para que la evidencia concentrada no valga menos que la dispersa. | Usa división entera (`//`) y `max()` sobre números enteros. |
| **Léxico de Shadow Copy** | Palabras clave localizadas que detectan abuso de instantáneas de volumen. | Prueba de pertenencia a diccionario determinista. |
| **Fronteras de Palabra** | Delimitadores léxicos que previenen falsos positivos por coincidencias parciales. | Coincidencia posicional exacta; sin estimación probabilística. |

### Glosario

- **Artefacto (Artefacto Forense)**: Objeto digital extraído de un host o red y sometido a inspección.
- **Aritmética Entera Determinista**: Operaciones matemáticas sobre números enteros que producen idénticos resultados para idénticas entradas, sin redondeo ni aproximación.
- **Quiebra Lógica**: Inconsistencia estructural entre el comportamiento esperado de un artefacto y su forma observada, sugiriendo manipulación.
- **Shadow Copy**: Mecanismo de instantánea de volumen que los atacantes pueden abusar para ocultar datos; detectado mediante coincidencia de palabras clave localizadas.
- **Sinería**: Peso evidencial acumulado generado cuando múltiples categorías independientes de indicadores coinciden.
- **Frontera de Palabra**: Delimitador léxico que restringe la coincidencia de patrones a tokens completos, eliminando falsos positivos por palabras parciales.
- **Balanceador Híbrido (M4)**: Algoritmo de la v2.3.5 que calcula un conteo efectivo de categorías mediante división entera y comparación, garantizando que una única categoría fuerte se puntúe equitativamente frente a varias débiles.
- **Tope de Anomalías**: Límite entero impuesto a tokens de entrada irregulares antes de que ingresen a la etapa de evaluación por expresiones regulares.

### 【Nota Científica】
> 【Nota Científica】
> Este módulo emplea terminología asociada a Charles Sanders Peirce, Umberto Eco y H. P. Grice—semiotistas que crearon modelos formales de cómo los signos, los códigos y la comunicación generan significado. Estos nombres **no** son invocaciones místicas. Considere el detector como un sensor: Peirce aportó la geometría óptica (cómo un signo se refracta en un interpretante), Eco proporcionó el estándar de calibración (qué códigos se mapean a qué amenazas) y Grice instaló el filtro de ruido (qué desviación de la cooperación esperada revela una señal encubierta). El esquema está fundado en lógica formal; cada veredicto se produce por aritmética entera determinista, no por intuición.

---

## РУССКИЙ

### Что это за модуль?
`vigia/core/forensic_technical_detector.py` v2.3.5 — это детерминированный правиловый движок платформы цифровой криминалистики. Его назначение — проверка цифровых артефактов (путей файлов, системных журналов, строк памяти, записей реестра) на структурные и лексические признаки компрометации. Модуль не строит догадок; он применяет неизменяемые таблицы правил, точные пороги оценки на основе целочисленной арифметики и проверки лексических границ для вынесения вердикта. Версия 2.3.5 усиливает эту строгость гибридным балансиром, предотвращающим недооценку сосредоточенных доказательств, жёстким потолком аномалий входных данных, блокирующим DoS-истощение до начала сопоставления шаблонов, а также расширенным испаноязычным лексиконом для обнаружения теневых копий.

### Ключевые Понятия

| Понятие | Описание | Детерминированный Механизм |
|---|---|---|
| **Цифровой Артефакт** | Образец (журнал, путь, ключ реестра), представленный для проверки. | Неизменяемые входные данные; идентичны при каждом анализе. |
| **Детекторный Движок** | Центральный компонент (`ForensicTechnicalDetector`), загружающий правила и выполняющий тесты. | Статические таблицы правил загружаются один раз; воспроизводимый вывод. |
| **Функция Анализа** (`analyze`) | Точка входа: выполняет санацию, сопоставление шаблонов, оценку и вынесение вердикта. | Фиксированная последовательность целочисленных сравнений и поиска. |
| **Пороги Оценки** (`BASE_Z`, `MAX_Z`) | Дискретные уровни, представляющие доказательный вес. | Сравниваются точным целочисленным неравенством; без округления. |
| **Ограничения Синергии** (`SYNERGY_STEP`, `MAX_SYNERGY`) | Инкрементальное вознаграждение при совместном появлении независимых категорий. | Целочисленное сложение с жёстким потолком; без дрейфа. |
| **Лимит Аномалий** (`INPUT_ANOMALIES_LIMIT`) | Максимальное число нерегулярных токенов до оценки регулярными выражениями. | Жёсткая остановка на целочисленном счётчике. |
| **Гибридный Балансир** (M4) | Корректирует эффективное число категорий, чтобы концентрированная доказательная база не оценивалась слабее рассредоточенной. | Использует целочисленное деление (`//`) и `max()` над целыми числами. |
| **Лексикон Теневых Копий** | Локализованные ключевые слова для обнаружения злоупотребления снимками тома. | Детерминированная проверка принадлежности к словарю. |
| **Границы Слова** | Лексические разделители, предотвращающие ложные срабатывания на частях строк. | Точное позиционное совпадение; без вероятностных предположений. |

### Глоссарий

- **Артефакт (Цифровой артефакт)**: Объект, извлечённый из хоста или сети и представленный для исследования.
- **Детерминистическая целочисленная арифметика**: Математические операции над целыми числами, дающие одинаковый результат при одинаковых входных данных, без округления или приближения.
- **Логический разрыв**: Структурное несоответствие между ожидаемым поведением артефакта и его наблюдаемой формой, указывающее на подделку.
- **Теневая копия (Shadow Copy)**: Механизм снимков тома, который злоумышленники могут использовать для сокрытия данных; обнаруживается поиском по локализованным ключевым словам.
- **Синергия**: Совокупный вес доказательств, возникающий при совместном появлении нескольких независимых категорий индикаторов.
- **Граница слова**: Лексический разделитель, ограничивающий сопоставление шаблонов целыми токенами и устраняющий ложные срабатывания на частях слов.
- **Гибридный балансир (M4)**: Алгоритм v2.3.5, вычисляющий эффективное число категорий с помощью целочисленного деления и сравнения, чтобы одна сильная категория оценивалась корректно по сравнению с несколькими слабыми.
- **Потолок аномалий**: Целочисленное ограничение на количество нерегулярных входных токенов до этапа оценки регулярными выражениями.

### 【Научное примечание】
> 【Научное примечание】
> В модуле встречается терминология, связанная с Чарльзом Сандерсом Пирсом, Умберто Эко и Г. П. Грайсом — семиотиками, создавшими формальные модели того, как знаки, коды и коммуникация порождают значение. Эти имена **не** являются мистическими инвокациями. Воспринимайте детектор как сенсор: Пирс спроектировал оптическую геометрию (как знак преломляется в интерпретант), Эко разработал калибровочный стандарт (какие коды соответствуют каким угрозам), а Грайс установил шумовой фильтр (какое отклонение от ожидаемого сотрудничества обнаруживает скрытый сигнал). Схема основана на формальной логике; каждый вердикт выдаётся детерминистической целочисленной арифметикой, а не интуицией.

---

## 中文

### 这是什么模块？
`vigia/core/forensic_technical_detector.py` v2.3.5 是数字取证平台的确定性规则引擎。其目的在于检查数字取证工件——如文件路径、系统日志、内存字符串和注册表项——以发现结构和词法层面的入侵指标。该模块不进行概率推测；它应用不可变规则表、基于确定性整数运算的精确评分阈值，以及词法边界检查来得出裁决。v2.3.5 版本通过以下改进进一步强化了严谨性：混合平衡器防止集中证据被低估；输入异常硬上限在模式匹配开始前阻断拒绝服务耗尽；并扩展了用于卷影副本检测的西班牙语词典。

### 核心概念

| 概念 | 描述 | 确定性机制 |
|---|---|---|
| **取证工件** | 送检的数字样本（日志、路径、注册表键）。 | 不可变输入；每次分析均相同。 |
| **检测引擎** | 核心组件（`ForensicTechnicalDetector`），负责加载规则并执行测试。 | 规则表静态加载一次；输出可复现。 |
| **分析函数** (`analyze`) | 依次执行净化、模式匹配、评分和裁决的入口点。 | 固定的整数比较与查找操作序列。 |
| **评分阈值** (`BASE_Z`, `MAX_Z`) | 代表证据权重的离散层级。 | 以精确整数不等式比较；无舍入。 |
| **协同上限** (`SYNERGY_STEP`, `MAX_SYNERGY`) | 独立类别同时触发时的增量奖励。 | 带硬上限的整数加法；无漂移。 |
| **异常上限** (`INPUT_ANOMALIES_LIMIT`) | 正则评估前可接受的最大不规则词元数。 | 以整数计数为硬停止点。 |
| **混合平衡器** (M4) | 调整有效类别数，使单一强类别不弱于多个弱类别的散布证据。 | 使用整数除法（`//`）与整数 `max()`。 |
| **卷影副本词典** | 检测卷快照滥用的本地化关键词。 | 确定性字典成员检测。 |
| **词边界** | 防止部分字符串误报的词法分隔符。 | 精确位置匹配；无概率推断。 |

### 术语表

- **取证工件**：从主机或网络中提取并送检的任何数字对象。
- **确定性整数运算**：对整数进行的数学操作，在相同输入下产生相同输出，无舍入或近似。
- **逻辑断裂**：工件预期行为与其观测形态之间的结构性不一致，暗示遭到篡改。
- **卷影副本 (Shadow Copy)**：攻击者可能滥用的卷快照机制；通过本地化关键词匹配进行检测。
- **协同度**：多个独立指标类别同时触发时产生的累积证据权重。
- **词边界**：将模式匹配限制为完整词元的词法分隔符，消除部分字符串导致的误报。
- **混合平衡器 (M4)**：v2.3.5 引入的算法，利用整数除法与比较计算有效类别数，确保单个强类别相对于多个弱类别得到公平评分。
- **异常上限**：在正则表达式评估阶段之前，对不规则输入词元设置的整数数量限制。

### 【科学说明】
> 【科学说明】
> 本模块偶尔引用与查尔斯·桑德斯·皮尔斯、艾柯和格赖斯相关的术语——这三位符号学家建立了关于符号、代码与传播如何产生意义的形式模型。这些姓名**并非**神秘主义咒语。请将本检测器视为一种传感器：皮尔斯设计了光学几何结构（符号如何折射为解释项），艾柯制定了校准标准（哪些代码映射至哪些威胁），格赖斯则安装了噪声滤波器（预期合作之外的何种偏差会揭示隐蔽信号）。其电路图以形式逻辑为基础；每一项裁决均由确定性整数运算得出，而非直觉。

---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
