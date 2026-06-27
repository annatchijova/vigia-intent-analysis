<!--
VIGIA Academic Documentation
Module: b32a18e2
Batch ID: vigia-doc-0074-b32a18e2
Generated: 2026-05-20T14:56:47.860448+00:00
-->

# Module Documentation: `vigia/core/semiotic_detector_v2.py`

## ENGLISH

### What Is This Module?
The `vigia/core/semiotic_detector_v2.py` module implements the Semiotic Detector v2.2, a deterministic forensic analysis engine for textual artifacts. It treats digital evidence as a signal stream that can be inspected through formal sign-relations. The detector executes a fixed pipeline: regular expression matching, fuzzy n-gram comparison, synergy detection, sequence validation, and Forensic Signal Vector (FSV) synthesis. It incorporates five critical hardening fixes from the VIGÍA Collective, including strict rational scoring, real TTL memory management, and structured collision logging.

### Key Concepts

| Concept | Role in Analysis |
|---|---|
| `PatternMatch` | Atomic detection unit storing pattern ID, position, and raw integer score. |
| `SynergyEvent` | Composite alert triggered when co-occurring patterns satisfy an interaction rule. |
| `SequenceEvent` | Higher-order alert requiring patterns to appear in a specific temporal order. |
| `SessionPatternMemory` | Context buffer with real TTL eviction and hard capacity caps; prevents unbounded growth. |
| `SemioticDetectorV2` | Controller class orchestrating the five-phase deterministic pipeline. |
| `analyze_artifact()` | Canonical public interface; accepts a forensic artifact and a `negation_enabled` flag. |

### Architecture Overview

| Phase | Method / Component | Description |
|---|---|---|
| 1. Regex Scan | Internal regex engine | Exact signature matching with integer timeout guards. |
| 2. Fuzzy Scan | Fuzzy config (5 patterns, 25 variants) | Approximate matching via n-grams and rational similarity thresholds (`NUM/DEN`). |
| 3. Synergy Analysis | `SynergyEvent` | Cross-reference matches against `SYNERGY_RULES` to detect combined threats. |
| 4. Sequence Check | `check_sequences()` | Validates ordered chains against `WINDOW_SIZE` and `TEMPORAL_SPAN`. |
| 5. FSV Synthesis | `analyze()` / `weight()` / `add()` | Aggregates integer sub-scores into a granular vector using `Fraction`. |

### Deterministic Integer Arithmetic
All scoring operations inside `SemioticDetectorV2` use Python's `fractions.Fraction`, representing every value as an exact ratio of two integers (numerator and denominator). There are no floating-point variables in the scoring path. This integer-only discipline guarantees that every forensic conclusion is bitwise identical across repeated executions and different hardware platforms.

### Constants & Configuration

| Constant | Function | Type |
|---|---|---|
| `NGRAM_SIZE` | Fuzzy token length | Positive integer |
| `SIMILARITY_THRESHOLD_NUM` | Threshold numerator | Integer |
| `SIMILARITY_THRESHOLD_DEN` | Threshold denominator | Non-zero integer |
| `WINDOW_SIZE` | Co-occurrence range | Positive integer |
| `TEMPORAL_SPAN` | Sequence validity limit | Positive integer |
| `TOP_K_MATCHES` | Match retention limit | Positive integer |
| `REGEX_TIMEOUT_SECONDS` | Execution safety bound | Positive integer |
| `MAX_TEXT_SIZE_BYTES` | Input size ceiling | Positive integer |
| `SYNERGY_RULES` | Interaction law table | Integer-structured mapping |
| `NEGATION_STRONG` | Negation polarity flag | Integer (0 or 1) |

### Glossary
- **Artifact**: A discrete object of digital evidence submitted for inspection (取证工件).
- **Deterministic Pipeline**: An analytical workflow where output is strictly entailed by input and configuration, excluding stochastic steps.
- **ECO_SEMIOTIC_COLLISION**: A structured field (`critical_patterns`) logging semiotic collisions per Eco (艾柯)—cases where pattern meanings structurally interfere.
- **Forensic Signal Vector (FSV)**: The final output structure decomposing the total score into rational components.
- **Fraction**: Python class for exact rational arithmetic; internally stores two integers.
- **Fuzzy Config**: The loaded `fuzzy_config.json` containing 5 base patterns and 25 variants.
- **Negation Handler**: A logical layer toggled by `negation_enabled` that inverts or suppresses scores when negation keywords are present.
- **TTL**: Time-to-live eviction policy coupled with a maximum count cap in `SessionPatternMemory`.

### 【Scientific Note】

> The references to Peirce, Eco (艾柯), and Grice (格赖斯) in this codebase are formal epistemological instruments, not mysticism. Think of them as the calibration vocabulary of a sensor: Peirce's triad defines the states a sign-detector must distinguish (sign, object, interpretant); Eco's semiotic threshold is realized as an exact rational cutoff (`SIMILARITY_THRESHOLD_NUM/DEN`); Grice's conversational maxims become logical constraints on valid sequences. They provide a structured language for deterministic decision boundaries, analogous to wavelength specifications in a spectrometer.

---

## ESPAÑOL

### ¿Qué es este módulo?
El módulo `vigia/core/semiotic_detector_v2.py` implementa el Detector Semiótico v2.2, un motor de análisis forense determinista para artefactos textuales. Trata la evidencia digital como una corriente de señales inspeccionable mediante relaciones de signos formales. El detector ejecuta un pipeline fijo: coincidencia regex, comparación fuzzy de n-gramas, detección de sinergia, validación de secuencias y síntesis del Vector de Señal Forense (FSV). Incorpora cinco correcciones críticas del Colectivo VIGÍA, incluyendo puntuación racional estricta, gestión TTL real y registro estructurado de colisiones.

### Conceptos Clave

| Concepto | Rol en el Análisis |
|---|---|
| `PatternMatch` | Unidad atómica de detección que almacena ID de patrón, posición y puntaje entero crudo. |
| `SynergyEvent` | Alerta compuesta disparada cuando patrones coexistentes satisfacen una regla de interacción. |
| `SequenceEvent` | Alerta de orden superior que exige que los patrones aparezcan en un orden temporal específico. |
| `SessionPatternMemory` | Búfer de contexto con evacuación TTL real y límites duros de capacidad; evita crecimiento ilimitado. |
| `SemioticDetectorV2` | Clase controladora que orquesta el pipeline determinista de cinco fases. |
| `analyze_artifact()` | Interfaz pública canónica; acepta un artefacto forense y una bandera `negation_enabled`. |

### Arquitectura / Pipeline

| Fase | Método / Componente | Descripción |
|---|---|---|
| 1. Escaneo Regex | Motor regex interno | Coincidencia exacta de firmas con guardas de tiempo de ejecución enteros. |
| 2. Escaneo Fuzzy | Config fuzzy (5 patrones, 25 variantes) | Coincidencia aproximada mediante n-gramas y umbrales de similitud racionales (`NUM/DEN`). |
| 3. Análisis de Sinergia | `SynergyEvent` | Referencia cruzada de coincidencias contra `SYNERGY_RULES` para detectar amenazas combinadas. |
| 4. Verificación de Secuencia | `check_sequences()` | Valida cadenas ordenadas contra `WINDOW_SIZE` y `TEMPORAL_SPAN`. |
| 5. Síntesis FSV | `analyze()` / `weight()` / `add()` | Agrega sub-puntajes enteros en un vector granular usando `Fraction`. |

### Aritmética Determinista
Todas las operaciones de puntuación dentro de `SemioticDetectorV2` utilizan `fractions.Fraction` de Python, representando cada valor como una razón exacta de dos enteros (numerador y denominador). No existen variables de punto flotante en la ruta de puntuación. Esta disciplina de solo-enteros garantiza que cada conclusión forense sea idéntica bit a bit entre ejecuciones repetidas y diferentes plataformas de hardware.

### Tabla de Constantes

| Constante | Función | Tipo |
|---|---|---|
| `NGRAM_SIZE` | Longitud del token fuzzy | Entero positivo |
| `SIMILARITY_THRESHOLD_NUM` | Numerador del umbral | Entero |
| `SIMILARITY_THRESHOLD_DEN` | Denominador del umbral | Entero no cero |
| `WINDOW_SIZE` | Rango de co-ocurrencia | Entero positivo |
| `TEMPORAL_SPAN` | Límite de validez de secuencia | Entero positivo |
| `TOP_K_MATCHES` | Límite de retención de coincidencias | Entero positivo |
| `REGEX_TIMEOUT_SECONDS` | Cota de seguridad de ejecución | Entero positivo |
| `MAX_TEXT_SIZE_BYTES` | Tope de tamaño de entrada | Entero positivo |
| `SYNERGY_RULES` | Tabla de leyes de interacción | Mapeo estructurado con enteros |
| `NEGATION_STRONG` | Bandera de polaridad de negación | Entero (0 o 1) |

### Glosario
- **Artefacto**: Objeto discreto de evidencia digital sometido a inspección (取证工件).
- **Pipeline Determinista**: Flujo de trabajo analítico donde la salida está estrictamente implicada por la entrada y la configuración, excluyendo pasos estocásticos.
- **ECO_SEMIOTIC_COLLISION**: Campo estructurado (`critical_patterns`) que registra colisiones semióticas según Eco (艾柯)—casos donde los significados de los patrones interfieren estructuralmente.
- **Vector de Señal Forense (FSV)**: Estructura de salida final que descompone el puntaje total en componentes racionales.
- **Fraction**: Clase de Python para aritmética racional exacta; almacena internamente dos enteros.
- **Config Fuzzy**: El `fuzzy_config.json` cargado que contiene 5 patrones base y 25 variantes.
- **Manejador de Negación**: Capa lógica activada por `negation_enabled` que invierte o suprime puntajes cuando se detectan palabras clave de negación.
- **TTL**: Política de evacuación por tiempo de vida acoplada a un límite máximo de cantidad en `SessionPatternMemory`.

### 【Nota Científica】

> Las referencias a Peirce, Eco (艾柯) y Grice (格赖斯) en este código son instrumentos epistemológicos formales, no misticismo. Piense en ellos como el vocabulario de calibración de un sensor: la tríada de Peirce define los estados que un detector de signos debe distinguir (signo, objeto, interpretante); el umbral semiótico de Eco se realiza como un corte racional exacto (`SIMILARITY_THRESHOLD_NUM/_DEN`); las máximas conversacionales de Grice se convierten en restricciones lógicas sobre secuencias válidas. Proporcionan un lenguaje estructurado para límites de decisión deterministas, análogo a las especificaciones de longitud de onda en un espectrómetro.

---

## РУССКИЙ

### Что представляет собой этот модуль?
Модуль `vigia/core/semiotic_detector_v2.py` реализует Семиотический Детектор v2.2 — детерминистский судебно-экспертный аналитический движок для текстовых артефактов. Он рассматривает цифровые доказательства как поток сигналов, поддающийся инспекции через формальные отношения знаков. Детектор выполняет фиксированный конвейер: сопоставление регулярных выражений, нечёткое сравнение n-грамм, обнаружение синергии, проверку последовательностей и синтез Судебного Сигнального Вектора (FSV). Он включает пять критических исправлений коллектива VIGÍA, включая строгую рациональную оценку, реальное управление памятью TTL и структурированное журналирование коллизий.

### Ключевые Концепции

| Концепция | Роль в Анализе |
|---|---|
| `PatternMatch` | Атомарная единица обнаружения, хранящая ID шаблона, позицию и сырые целочисленные баллы. |
| `SynergyEvent` | Составное оповещение, запускаемое при совместном появлении шаблонов, удовлетворяющих правилу взаимодействия. |
| `SequenceEvent` | Оповещение высшего порядка, требующее, чтобы шаблоны следовали в определённом временном порядке. |
| `SessionPatternMemory` | Контекстный буфер с реальным TTL-удалением и жёсткими ограничениями ёмкости; предотвращает неограниченный рост. |
| `SemioticDetectorV2` | Контроллирующий класс, оркестрирующий детерминированный конвейер из пяти фаз. |
| `analyze_artifact()` | Канонический публичный интерфейс; принимает судебный артефакт и флаг `negation_enabled`. |

### Архитектура / Конвейер

| Фаза | Метод / Компонент | Описание |
|---|---|---|
| 1. Regex-сканирование | Внутренний движок regex | Точное сопоставление сигнатур с целочисленными защитами таймаута. |
| 2. Fuzzy-сканирование | Fuzzy-конфигурация (5 паттернов, 25 вариантов) | Приближённое сопоставление через n-граммы и рациональные пороги сходства (`NUM/DEN`). |
| 3. Анализ синергии | `SynergyEvent` | Перекрёстная проверка совпадений с `SYNERGY_RULES` для обнаружения комбинированных угроз. |
| 4. Проверка последовательностей | `check_sequences()` | Валидирует упорядоченные цепочки в соответствии с `WINDOW_SIZE` и `TEMPORAL_SPAN`. |
| 5. Синтез FSV | `analyze()` / `weight()` / `add()` | Агрегирует целочисленные под-оценки в детализированный вектор с помощью `Fraction`. |

### Детерминированная Целочисленная Арифметика
Все операции оценки внутри `SemioticDetectorV2` используют `fractions.Fraction` Python, представляя каждое значение как точную дробь из двух целых чисел (числитель и знаменатель). В пути оценки нет переменных с плавающей точкой. Эта дисциплина только-целых чисел гарантирует, что каждый криминалистический вывод является побитово идентичным при повторных выполнениях на разных аппаратных платформах.

### Константы и Конфигурация

| Константа | Функция | Тип |
|---|---|---|
| `NGRAM_SIZE` | Длина токена fuzzy | Положительное целое |
| `SIMILARITY_THRESHOLD_NUM` | Числитель порога | Целое |
| `SIMILARITY_THRESHOLD_DEN` | Знаменатель порога | Ненулевое целое |
| `WINDOW_SIZE` | Диапазон совместного появления | Положительное целое |
| `TEMPORAL_SPAN` | Предел валидности последовательности | Положительное целое |
| `TOP_K_MATCHES` | Предел удержания совпадений | Положительное целое |
| `REGEX_TIMEOUT_SECONDS` | Граница безопасности выполнения | Положительное целое |
| `MAX_TEXT_SIZE_BYTES` | Потолок размера входа | Положительное целое |
| `SYNERGY_RULES` | Таблица законов взаимодействия | Целочисленное отображение |
| `NEGATION_STRONG` | Флаг полярности отрицания | Целое (0 или 1) |

### Глоссарий
- **Артефакт**: Дискретный объект цифровых доказательств, представленный для инспекции (取证工件).
- **Детерминированный конвейер**: Аналитический рабочий процесс, где выход строго определяется входом и конфигурацией, исключая стохастические шаги.
- **ECO_SEMIOTIC_COLLISION**: Структурированное поле (`critical_patterns`), регистрирующее семиотические коллизии по Эко (艾柯) — случаи, когда значения паттернов структурно интерферируют.
- **Судебный Сигнальный Вектор (FSV)**: Финальная выходная структура, разложившая общий балл на рациональные компоненты.
- **Fraction**: Класс Python для точной рациональной арифметики; внутренне хранит два целых числа.
- **Fuzzy-конфигурация**: Загруженный `fuzzy_config.json`, содержащий 5 базовых паттернов и 25 вариантов.
- **Обработчик отрицания**: Логический слой, включаемый `negation_enabled`, который инвертирует или подавляет баллы при обнаружении ключевых слов отрицания.
- **TTL**: Политика удаления по времени жизни, связанная с ограничением максимального количества в `SessionPatternMemory`.

### 【Научное Примечание】

> Ссылки на Пирса, Эко (艾柯) и Грайса (格赖斯) в этом коде являются формальными эпистемологическими инструментами, а не мистицизмом. Думайте о них как о калибровочном словаре датчика: триада Пирса определяет состояния, которые детектор знаков должен различать (знак, объект, интерпретант); семиотический порог Эко реализован как точная рациональная отсечка (`SIMILARITY_THRESHOLD_NUM/DEN`); разговорные максимы Грайса становятся логическими ограничениями на допустимые последовательности. Они обеспечивают структурированный язык для детерминированных границ принятия решений, аналогичный спецификациям длин волн в спектрометре.

---

## 中文

### 本模块是什么？
`vigia/core/semiotic_detector_v2.py` 模块实现了符号学探测器 v2.2，这是一个针对文本取证工件的确定性法医分析引擎。它将数字证据视为可通过形式符号关系进行检查的信号流。探测器执行固定的处理管线：正则表达式匹配、模糊 n-gram 比较、协同检测、序列验证以及取证信号向量（FSV）综合。它融入了 VIGÍA 集体的五项关键加固修复，包括严格有理数评分、真实 TTL 内存管理和结构化碰撞日志记录。

### 核心概念

| 概念 | 在分析中的作用 |
|---|---|
| `PatternMatch` | 原子检测单元，存储模式 ID、位置与原始整数分数。 |
| `SynergyEvent` | 当共现模式满足交互规则时触发的复合警报。 |
| `SequenceEvent` | 要求模式按特定时间顺序出现的高阶警报。 |
| `SessionPatternMemory` | 具有真实 TTL 驱逐和硬性容量上限的上下文缓冲区；防止无限增长。 |
| `SemioticDetectorV2` | 编排五阶段确定性管线的控制器类。 |
| `analyze_artifact()` | 规范公共接口；接受一个取证工件和一个 `negation_enabled` 标志。 |

### 架构概览

| 阶段 | 方法 / 组件 | 描述 |
|---|---|---|
| 1. 正则扫描 | 内部正则引擎 | 带整数超时保护的精确签名匹配。 |
| 2. 模糊扫描 | 模糊配置（5 个模式，25 个变体） | 通过 n-gram 和有理相似度阈值（`NUM/DEN`）进行近似匹配。 |
| 3. 协同分析 | `SynergyEvent` | 对照 `SYNERGY_RULES` 交叉引用匹配，以检测组合威胁。 |
| 4. 序列检查 | `check_sequences()` | 根据 `WINDOW_SIZE` 和 `TEMPORAL_SPAN` 验证有序链。 |
| 5. FSV 综合 | `analyze()` / `weight()` / `add()` | 使用 `Fraction` 将整数子分数聚合为细粒度向量。 |

### 确定性整数运算
`SemioticDetectorV2` 内的所有评分操作均使用 Python 的 `fractions.Fraction`，将每个值表示为两个整数（分子和分母）的精确比值。评分路径中不存在任何浮点变量。这种纯整数规范确保每个法医结论在重复执行和不同硬件平台上均为比特级一致。

### 常量与配置

| 常量 | 功能 | 类型 |
|---|---|---|
| `NGRAM_SIZE` | 模糊令牌长度 | 正整数 |
| `SIMILARITY_THRESHOLD_NUM` | 阈值分子 | 整数 |
| `SIMILARITY_THRESHOLD_DEN` | 阈值分母 | 非零整数 |
| `WINDOW_SIZE` | 共现范围 | 正整数 |
| `TEMPORAL_SPAN` | 序列有效期限制 | 正整数 |
| `TOP_K_MATCHES` | 匹配保留限制 | 正整数 |
| `REGEX_TIMEOUT_SECONDS` | 执行安全边界 | 正整数 |
| `MAX_TEXT_SIZE_BYTES` | 输入大小上限 | 正整数 |
| `SYNERGY_RULES` | 交互规则表 | 整数结构化映射 |
| `NEGATION_STRONG` | 否定极性标志 | 整数（0 或 1） |

### 术语表
- **取证工件**：提交检查的离散数字证据对象。
- **确定性管线**：输出严格由输入和配置决定的分析工作流，不包含随机步骤。
- **ECO_SEMIOTIC_COLLISION**：结构化字段（`critical_patterns`），按艾柯理论记录符号学碰撞——即模式含义在结构上相互干扰的情况。
- **取证信号向量（FSV）**：将总分分解为有理数分量的最终输出结构。
- **Fraction**：Python 的精确有理数运算类；内部存储两个整数。
- **模糊配置**：加载的 `fuzzy_config.json`，包含 5 个基本模式和 25 个变体。
- **否定处理器**：由 `negation_enabled` 切换的逻辑层，当检测到否定关键词时反转或抑制分数。
- **TTL**：与 `SessionPatternMemory` 中最大数量上限配对的生存时间驱逐策略。
- **逻辑断裂**：叙事或序列推理链中的确定性断裂，当整数序列检查未能满足有序约束时被标记。

### 【科学说明】

> 本代码库中对皮尔斯、艾柯与格赖斯的引用是形式认识论工具，而非神秘主义。将它们视为传感器的校准词汇：皮尔斯的三元组定义了符号探测器必须区分的状态（符号、对象、阐释项）；艾柯的符号学阈值被实现为精确有理数截止值（`SIMILARITY_THRESHOLD_NUM/DEN`）；格赖斯的会话准则成为有效序列的逻辑约束。它们为确定性决策边界提供了结构化语言，类似于光谱仪中的波长规范。

---

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
